"""LES MIGRATIONS DU REGISTRE IA — deux moteurs, une seule syntaxe possible.

LA FAUTE, ET CE QU'ELLE COÛTAIT. Les migrations de `systemes_ia`
s'écrivaient « ALTER TABLE ... ADD COLUMN IF NOT EXISTS », qui est de la
syntaxe PostgreSQL. SQLite ne la connaît pas et répond
« near "EXISTS": syntax error ».

CE N'ÉTAIT PAS UNE COLONNE PERDUE, C'ÉTAIT LES NEUF. Les migrations
s'enchaînaient sans garde : l'exception remontait dès la PREMIÈRE, et
`registre_init_db()` s'arrêtait là. Sous SQLite, `systemes_ia` n'avait donc
aucune des neuf colonnes — à commencer par `client_id`, dont dépend
l'isolation par client, et que `app.py` interroge à plus de quatre cents
endroits. Le repli SQLite du registre n'a jamais fonctionné, et le seul signe
visible était une ligne d'erreur au démarrage :

    ERROR REGISTRE_IA — erreur init DB : near "EXISTS": syntax error

CE QUE CES CONTRÔLES EXÉCUTENT. Pas une copie du schéma : le schéma
LUI-MÊME. Ils extraient de `app.py` la fonction de migration et la liste de
ses appels, puis les rejouent sur une base SQLite réelle. Une liste tenue à
part dériverait, et ces contrôles ne protégeraient plus que d'elle-même.
"""
import os
import re
import sqlite3
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

SOURCE = open(os.path.join(ICI, 'app.py'), encoding='utf-8').read()


def _fonction(nom):
    """Le code source d'une fonction de `app.py`, et RIEN QU'ELLE.

    La fin est la première ligne non vide revenue en colonne zéro. Un premier
    essai s'arrêtait au prochain `def`, ce qui embarquait le code de module
    posé entre les deux — la fonction extraite tirait alors des noms qu'elle
    n'emploie pas, et le contrôle échouait pour une raison sans rapport avec
    ce qu'il mesure."""
    lignes = SOURCE[SOURCE.index('def %s(' % nom):].split('\n')
    gardees = [lignes[0]]
    for l in lignes[1:]:
        if l.strip() and not l.startswith((' ', '\t')):
            break
        gardees.append(l)
    return '\n'.join(gardees)


def _migrer(moteur_pg=False):
    """La VRAIE fonction d'`app.py`, avec le moteur qu'on veut."""
    espace = {'REGISTRE_USE_PG': moteur_pg}
    exec(compile(_fonction('registre_ajouter_colonne'), 'app.py', 'exec'), espace)
    return espace['registre_ajouter_colonne']


def _colonnes_attendues():
    """Les migrations de `systemes_ia` telles qu'`app.py` les appelle.

    Le motif distingue les deux styles de guillemets : deux déclarations
    portent une valeur par défaut entre apostrophes — `"TEXT DEFAULT
    'production'"` —, et un motif qui ne verrait qu'un seul style les
    laisserait tomber. Sept migrations sur neuf, silencieusement.

    LA LISTE EST LUE DANS `app.py`, PAS RECOPIÉE ICI — mais son EFFECTIF est
    fixé plus bas. Ajouter une colonne fait donc tomber le contrôle, et c'est
    voulu : une migration s'ajoute en connaissance de cause, pas au fil de
    l'eau. La colonne `famille` a été ajoutée le 28 août 2026 pour la
    documentation commune à une famille de systèmes voisins."""
    trouvees = re.findall(
        r"""registre_ajouter_colonne\(cur,\s*'systemes_ia',\s*'(\w+)',\s*"""
        r"""("[^"]*"|'[^']*')\s*\)""", SOURCE)
    return [(col, decl[1:-1]) for col, decl in trouvees]


def _table_sqlite(conn):
    """La table `systemes_ia` de la branche SQLite d'`app.py` — celle qui
    porte AUTOINCREMENT, propre à ce moteur."""
    ddl = [m for m in re.findall(
        r"CREATE TABLE IF NOT EXISTS systemes_ia \([^)]*?\)", SOURCE, re.S)
        if 'AUTOINCREMENT' in m]
    assert ddl, "la création de table SQLite n'a pas été retrouvée dans app.py"
    conn.execute(ddl[0])
    return conn


def _colonnes(conn):
    return {r[1] for r in conn.execute('PRAGMA table_info(systemes_ia)')}


# ── 1. La faute elle-même ne doit plus pouvoir être écrite ────────────────

def test_aucune_migration_du_registre_n_emploie_la_syntaxe_postgresql():
    """LE CONTRÔLE QUI GARDE LA CORRECTION. `ADD COLUMN IF NOT EXISTS` ne doit
    plus apparaître sur `systemes_ia` : il n'est légitime que dans la branche
    PostgreSQL de la fonction de migration, jamais au fil des appels."""
    assert 'ALTER TABLE systemes_ia ADD COLUMN IF NOT EXISTS' not in SOURCE


def test_sqlite_refuse_bien_cette_syntaxe():
    """La raison d'être de tout ce qui précède, vérifiée et non supposée : si
    un jour SQLite l'acceptait, ces contrôles pourraient être retirés."""
    c = _table_sqlite(sqlite3.connect(':memory:'))
    with pytest.raises(sqlite3.OperationalError) as e:
        c.execute('ALTER TABLE systemes_ia ADD COLUMN IF NOT EXISTS essai TEXT')
    assert 'EXISTS' in str(e.value)


# ── 2. Les dix colonnes arrivent vraiment, sur SQLite ─────────────────────

def test_les_colonnes_migrees_arrivent_vraiment_sur_sqlite():
    """C'est l'état que le démarrage n'atteignait jamais."""
    attendues = _colonnes_attendues()
    assert len(attendues) == 10, (
        "le nombre de migrations de systemes_ia a changé : %s. Si c'est\n"
        "délibéré, mettez ce compte à jour ; sinon, une migration a disparu."
        % [c for c, _ in attendues])
    assert 'famille' in [c for c, _ in attendues], (
        "la colonne `famille` n'est plus migrée : la documentation commune à\n"
        "une famille de systèmes voisins n'a plus où se ranger")
    c = _table_sqlite(sqlite3.connect(':memory:'))
    ajouter = _migrer(moteur_pg=False)
    cur = c.cursor()
    for col, decl in attendues:
        ajouter(cur, 'systemes_ia', col, decl)
    c.commit()
    manquantes = {col for col, _ in attendues} - _colonnes(c)
    assert not manquantes, sorted(manquantes)


def test_client_id_existe_car_tout_le_registre_en_depend():
    """Nommée à part parce que c'est elle qui portait le coût : `app.py`
    interroge `client_id` à plus de quatre cents endroits, et c'était la
    PREMIÈRE migration — donc celle qui faisait tomber les huit autres."""
    assert SOURCE.count('client_id') > 100
    c = _table_sqlite(sqlite3.connect(':memory:'))
    ajouter = _migrer(moteur_pg=False)
    ajouter(c.cursor(), 'systemes_ia', 'client_id', 'INTEGER')
    c.commit()
    assert 'client_id' in _colonnes(c)


def test_rejouer_les_migrations_ne_casse_rien():
    """Elles s'exécutent à CHAQUE démarrage : la deuxième fois, les colonnes
    sont déjà là. C'est tout l'objet du « si elle manque »."""
    attendues = _colonnes_attendues()
    c = _table_sqlite(sqlite3.connect(':memory:'))
    ajouter = _migrer(moteur_pg=False)
    for _ in range(3):
        cur = c.cursor()
        for col, decl in attendues:
            ajouter(cur, 'systemes_ia', col, decl)
        c.commit()
    assert {col for col, _ in attendues} <= _colonnes(c)


def test_les_valeurs_par_defaut_declarees_arrivent_dans_la_table():
    """Deux colonnes portent un défaut, et ce défaut EST le motif écrit dans
    `app.py` : `cycle_vie='production'` parce que les systèmes antérieurs au
    suivi étaient déjà déployés, `transparence_art50='a_evaluer'` parce que
    rien n'autorise à supposer une évaluation faite. Une colonne ajoutée sans
    son défaut inverserait l'hypothèse, en silence.

    LA DÉCLARATION EST LUE DANS `app.py`, PAS RECOPIÉE ICI. Première version :
    la chaîne était écrite dans ce contrôle, si bien que retirer le défaut du
    fichier ne le faisait pas tomber — il ne gardait que lui-même."""
    defauts = {col: re.search(r"DEFAULT\s+'([^']+)'", decl).group(1)
               for col, decl in _colonnes_attendues() if 'DEFAULT' in decl}
    assert defauts == {'cycle_vie': 'production',
                       'transparence_art50': 'a_evaluer'}, defauts
    c = _table_sqlite(sqlite3.connect(':memory:'))
    ajouter = _migrer(moteur_pg=False)
    cur = c.cursor()
    for col, decl in _colonnes_attendues():
        ajouter(cur, 'systemes_ia', col, decl)
    c.commit()
    c.execute("INSERT INTO systemes_ia (nom) VALUES ('essai')")
    ligne = c.execute('SELECT %s FROM systemes_ia'
                      % ', '.join(defauts)).fetchone()
    assert list(ligne) == [defauts[c] for c in defauts], ligne


# ── 3. Ce qui échoue vraiment doit continuer d'échouer ────────────────────

def test_une_vraie_erreur_de_migration_remonte_toujours():
    """POURQUOI PAS UN try/except AUTOUR DE CHAQUE ALTER — la solution la plus
    courte, et la mauvaise. Avaler l'exception ferait passer une VRAIE erreur
    de migration pour un « la colonne existait déjà », et le registre
    repartirait silencieusement incomplet. C'est exactement le mode de panne
    qu'on vient de payer : un défaut dont le seul signe était une ligne de
    journal que personne ne lit."""
    c = _table_sqlite(sqlite3.connect(':memory:'))
    ajouter = _migrer(moteur_pg=False)
    with pytest.raises(sqlite3.OperationalError):
        ajouter(c.cursor(), 'table_absente', 'peu_importe', 'TEXT')


def test_la_branche_postgresql_garde_sa_syntaxe():
    """Elle, elle est correcte : `IF NOT EXISTS` est du PostgreSQL valide, et
    le remplacer par une introspection ferait deux dialectes là où le moteur
    en offre un."""
    f = _fonction('registre_ajouter_colonne')
    pg = f[f.index('if REGISTRE_USE_PG'):f.index('PRAGMA')]
    assert 'ADD COLUMN IF NOT EXISTS' in pg
    assert 'PRAGMA' not in pg
