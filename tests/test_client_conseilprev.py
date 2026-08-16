"""Le compte interne CONSEILPREV : il doit VRAIMENT être créé.

CE QUE CES TESTS PROTÈGENT, ET LA FAUTE QU'ILS EMPÊCHENT.

L'accès par lien maître crée, au premier appel, un enregistrement dans la
table `clients` pour que CONSEILPREV porte un `client_id` numérique comme
n'importe quel client. Cette insertion ne renseignait pas
`mot_de_passe_hash`. Sur PostgreSQL la colonne est nullable et rien ne se
voyait ; sur SQLite elle est déclarée NOT NULL, donc l'insertion échouait à
tous les coups.

L'échec ne remontait nulle part : il était rattrapé, journalisé, et l'accès
retombait sur un identifiant dégradé `id=0`. Un compte fantôme, jamais créé,
sans qu'aucune page ne le dise — 170 erreurs dans un seul journal de recette
avant correction, aucune après.

DEUX MOTEURS, DEUX SCHÉMAS : c'est là que se logent ces défauts. Le test
n'affirme donc pas que le code « a l'air bon », il EXÉCUTE l'une contre
l'autre les deux instructions SQL que porte `app.py` — la création de table
SQLite et l'insertion SQLite — sur une base réelle en mémoire. Retirer à
nouveau la colonne de l'insertion fait tomber ce test.
"""
import os
import re
import sqlite3
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

SOURCE = open(os.path.join(ICI, 'app.py'), encoding='utf-8').read()


def _schema_clients_sqlite(conn):
    """Rejoue le schéma `clients` de la branche SQLite tel qu'app.py le
    construit : la création de table, PUIS les colonnes ajoutées une à une.
    Rien n'est recopié à la main — une copie tenue à part dériverait, et ce
    test ne protégerait plus que d'elle-même.

    Deux tables `clients` coexistent dans le fichier, une par moteur : on
    retient celle qui porte AUTOINCREMENT, propre à SQLite."""
    ddl = [m for m in re.findall(
        r"CREATE TABLE IF NOT EXISTS clients \((?:[^']|'(?!''))*?\)",
        SOURCE) if 'AUTOINCREMENT' in m]
    assert len(ddl) == 1, f"DDL SQLite de `clients` : {len(ddl)} trouvée(s), 1 attendue"
    conn.execute(ddl[0])

    bloc = re.search(r"for _col, _decl in \((.*?)\n        \):", SOURCE, re.S)
    assert bloc, "la liste des colonnes ajoutées à `clients` est introuvable"
    colonnes = re.findall(r"\('([a-z_]+)',\s*(?:'|\")(.*?)(?:'|\")\)", bloc.group(1))
    assert len(colonnes) >= 10, f"seulement {len(colonnes)} colonne(s) relevée(s)"
    for col, decl in colonnes:
        conn.execute(f'ALTER TABLE clients ADD COLUMN {col} {decl}')
    return conn


def _insert_conseilprev_sqlite():
    """L'insertion du compte interne, branche SQLite (placeholders `?`)."""
    m = re.search(
        r'"INSERT INTO clients \(nom_entreprise[^"]*"\s*\n\s*"VALUES \(\?[^"]*"',
        SOURCE)
    assert m, "insertion SQLite du compte CONSEILPREV introuvable dans app.py"
    return ''.join(re.findall(r'"([^"]*)"', m.group(0)))


def test_le_compte_interne_s_insere_reellement_dans_le_schema_sqlite():
    """LE TEST QUI COMPTE. On rejoue l'insertion contre le vrai schéma."""
    conn = _schema_clients_sqlite(sqlite3.connect(':memory:'))
    conn.execute(_insert_conseilprev_sqlite(),
                 ('CONSEILPREV', 'conseilprev@internal.system',
                  '2026-01-01T00:00:00', '2026-01-01T00:00:00'))
    conn.commit()
    r = conn.execute(
        'SELECT id, nom_entreprise, plan, actif FROM clients').fetchone()
    assert r is not None, "aucun compte créé : l'accès retomberait sur id=0"
    # Un identifiant EXPLOITABLE : `id=0` est justement la valeur dégradée que
    # ce compte existe pour éviter — un `client_id` faux mais silencieux.
    assert r[0] >= 1, f"identifiant inutilisable : {r[0]}"
    assert r[1] == 'CONSEILPREV'
    assert r[2] == 'entreprise', "le compte interne doit porter le plan complet"
    assert r[3] == 1


def test_le_schema_sqlite_exige_bien_le_mot_de_passe():
    """La contrainte qui faisait tomber l'insertion est TOUJOURS LÀ. Sans ce
    contrôle, le test précédent passerait aussi le jour où quelqu'un rendrait
    la colonne nullable — et ne prouverait plus rien."""
    conn = _schema_clients_sqlite(sqlite3.connect(':memory:'))
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO clients (nom_entreprise, email, date_creation) "
            "VALUES ('X','x@y.z','2026-01-01')")


def test_les_deux_moteurs_renseignent_la_meme_colonne():
    """La divergence PostgreSQL / SQLite est la CAUSE du défaut. Les deux
    insertions doivent nommer les mêmes colonnes, sinon le prochain écart
    repassera inaperçu sur le moteur permissif."""
    blocs = re.findall(r'INSERT INTO clients \(([^)]*)\)[^"]*"\s*\n\s*"VALUES',
                       SOURCE)
    conseil = [b for b in blocs if 'rgpd_consenti_date' in b and 'essai_fin' not in b]
    assert len(conseil) == 2, (
        f"attendu deux insertions du compte interne (PG et SQLite), trouvé {len(conseil)}")
    colonnes = [tuple(c.strip() for c in b.split(',')) for b in conseil]
    assert colonnes[0] == colonnes[1], (
        f"les deux moteurs divergent : {colonnes[0]} vs {colonnes[1]}")
    assert 'mot_de_passe_hash' in colonnes[0], (
        "la colonne qui faisait échouer l'insertion n'est plus renseignée")


def test_un_hache_vide_n_ouvre_aucune_porte():
    """LE COMPTE INTERNE NE DOIT PAS DEVENIR UNE ENTRÉE. On lui pose un haché
    vide : il faut donc qu'un haché vide ne valide jamais de mot de passe,
    sinon la correction ci-dessus ouvrirait un compte au plan « entreprise »."""
    from werkzeug.security import check_password_hash
    for essai in ('', ' ', 'motdepasse', 'conseilprev'):
        assert check_password_hash('', essai) is False, essai


def test_la_connexion_refuse_avant_meme_de_verifier():
    """Ceinture ET bretelles : la route de connexion écarte un haché absent ou
    vide AVANT d'appeler la vérification, sans dépendre de son comportement."""
    assert re.search(
        r"if not d\.get\('mot_de_passe_hash'\) or not check_password_hash",
        SOURCE), "le garde-fou de connexion sur haché vide a disparu"
