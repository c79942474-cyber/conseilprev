"""UN PARC DE VINGT SYSTÈMES VOISINS SE DOCUMENTAIT VINGT FOIS.

CE QUE LE GUIDE AUTORISE, ET QUE SENTINEL NE PERMETTAIT PAS. Le guide
d'application de l'IA Act admet une documentation de gestion des risques et de
conformité COMMUNE à une famille de systèmes d'IA voisins — même technologie,
même finalité, même profil de risque. Le registre n'avait aucun moyen de dire
que deux systèmes appartiennent à la même famille : chacun se remplissait de
zéro, y compris quand le précédent disait déjà la même chose.

C'est le seul écart relevé le 28 août 2026 qui fait GAGNER du temps au client
au lieu de lui en demander. Pour un parc de vingt systèmes proches, la
différence est d'un ordre de grandeur.

CE QUE CES RÈGLES GARDENT. Que la colonne existe et traverse réellement
l'aller-retour SQL — c'est là qu'une colonne ajoutée se perd, en silence, parce
qu'un `?` manque quelque part ; que la reprise d'un dossier copie ce qui est
propre à la FAMILLE et jamais ce qui est propre au SYSTÈME — recopier un nom,
un responsable ou des preuves déjà constituées produirait un faux document ; et
que la liste des familles déjà employées existe, sans quoi « chatbots »,
« Chatbots » et « chat-bots » font trois familles et le regroupement ne
regroupe plus rien.
"""
import io
import json
import os
import re
import shutil
import sqlite3
import subprocess

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = io.open(os.path.join(ICI, 'app.py'), encoding='utf-8').read()
MOTEUR = io.open(os.path.join(ICI, 'sentinel.page.js'), encoding='utf-8').read()
NODE = shutil.which('node')


# ── LA COLONNE TRAVERSE VRAIMENT LE SQL ──────────────────────────────────

def _table_sqlite():
    """La table `systemes_ia` telle qu'`app.py` la crée, migrations comprises."""
    ddl = [m for m in re.findall(
        r"CREATE TABLE IF NOT EXISTS systemes_ia \([^)]*?\)", SOURCE, re.S)
        if 'AUTOINCREMENT' in m]
    assert ddl, "la création de table SQLite est introuvable dans app.py"
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.execute(ddl[0])
    for col, decl in re.findall(
            r"""registre_ajouter_colonne\(cur,\s*'systemes_ia',\s*'(\w+)',\s*"""
            r"""("[^"]*"|'[^']*')\s*\)""", SOURCE):
        conn.execute('ALTER TABLE systemes_ia ADD COLUMN %s %s' % (col, decl[1:-1]))
    return conn


def _sql(motif):
    m = re.search(motif, SOURCE, re.S)
    assert m, "instruction SQL introuvable dans app.py : %s" % motif[:60]
    return re.sub(r'\s+', ' ', m.group(0)).strip()


INSERT_SQLITE = _sql(r"INSERT INTO systemes_ia\s*\n\s*\(nom,[^)]*\)\s*\n\s*VALUES \(\?[^)]*\)")
UPDATE_SQLITE = _sql(r"UPDATE systemes_ia SET nom=\?.*?WHERE id=\? AND client_id=\?")


def test_la_colonne_famille_est_migree():
    c = _table_sqlite()
    colonnes = {r[1] for r in c.execute('PRAGMA table_info(systemes_ia)')}
    assert 'famille' in colonnes, (
        "la colonne `famille` n'est pas créée : la documentation commune à une "
        "famille de systèmes voisins n'a nulle part où se ranger")


def test_l_insertion_compte_autant_de_valeurs_que_de_colonnes():
    """LÀ OÙ UNE COLONNE AJOUTÉE SE PERD. Ajouter un nom de colonne sans
    ajouter son `?` — ou l'inverse — ne se voit pas à la lecture : la requête
    est longue, les deux listes sont loin l'une de l'autre, et l'erreur
    n'apparaît qu'à la première écriture réelle, en production."""
    colonnes = re.search(r'\((nom,[^)]*)\)', INSERT_SQLITE).group(1).split(',')
    valeurs = re.search(r'VALUES \(([^)]*)\)', INSERT_SQLITE).group(1).split(',')
    assert len(colonnes) == len(valeurs), (
        "l'INSERT du registre déclare %d colonnes pour %d valeurs : %s"
        % (len(colonnes), len(valeurs), ', '.join(c.strip() for c in colonnes)))
    assert 'famille' in [c.strip() for c in colonnes], (
        "`famille` n'est pas insérée : le champ sera saisi puis perdu")


def test_la_famille_survit_a_l_aller_retour_en_base():
    """LA RÈGLE QUI COMPTE. Elle exécute l'INSERT et l'UPDATE d'`app.py` tels
    qu'ils sont écrits, contre la table qu'`app.py` crée. Un décalage de
    placeholder tombe ici plutôt qu'en production."""
    c = _table_sqlite()
    colonnes = [x.strip() for x in
                re.search(r'\((nom,[^)]*)\)', INSERT_SQLITE).group(1).split(',')]
    valeurs = ['Assistant RH' if col == 'nom' else
               'Assistants conversationnels internes' if col == 'famille' else
               0 if col in ('score_risque', 'client_id') else 'x'
               for col in colonnes]
    c.execute(INSERT_SQLITE, valeurs)
    ligne = c.execute('SELECT famille FROM systemes_ia').fetchone()
    assert ligne['famille'] == 'Assistants conversationnels internes', (
        "la famille n'est pas écrite en base : elle vaut %r" % ligne['famille'])

    # Et la mise à jour la modifie, au lieu de l'écraser à vide.
    n_places = UPDATE_SQLITE.count('?')
    # LA CLAUSE WHERE PORTE ELLE AUSSI DES `=?`. Les compter avec les colonnes
    # du SET donnait deux paramètres de trop et faisait échouer la règle sur
    # son propre comptage, pas sur le code mesuré.
    ordre = re.findall(r'(\w+)=\?', UPDATE_SQLITE.split(' WHERE ')[0])
    vals = []
    for col in ordre:
        vals.append('Modèles de scoring' if col == 'famille'
                    else 0 if col == 'score_risque' else 'y')
    vals += [1, 0]  # WHERE id, client_id
    assert len(vals) == n_places, (
        "l'UPDATE attend %d paramètres et %d colonnes sont nommées" % (n_places, len(vals)))
    c.execute(UPDATE_SQLITE, vals)
    ligne = c.execute('SELECT famille FROM systemes_ia').fetchone()
    assert ligne['famille'] == 'Modèles de scoring', (
        "la mise à jour ne modifie pas la famille : elle vaut %r" % ligne['famille'])


def test_la_famille_est_rendue_par_l_api():
    """Écrite en base et jamais renvoyée, elle serait invisible à l'écran —
    et le client la ressaisirait à chaque modification."""
    d = SOURCE.index('def registre_row_to_dict(row):')
    corps = SOURCE[d:SOURCE.index('\n@app.route', d)]
    assert "'famille'" in corps, (
        "`famille` n'est pas renvoyée par l'API : le champ sera vide à chaque "
        "réouverture de la fiche, et le regroupement se défera tout seul")


# ── LA REPRISE D'UN DOSSIER DE FAMILLE ───────────────────────────────────

_SONDE = r'''
var REG_DATA = %(donnees)s;
var champs = %(champs)s;
var lus = {}, roles = %(roles)s;
var document = {
  getElementById: function(id){
    if(id === 'rf-famille') return { value: %(saisie)s };
    if(id === 'rf-famille-msg') return { textContent:'', style:{} };
    if(champs.indexOf(id) === -1) return null;
    return { set value(v){ lus[id] = v; }, get value(){ return lus[id]; } };
  },
  querySelectorAll: function(){ return roles; }
};
var window = {};
%(code)s
window.regReprendreFamille();
console.log(JSON.stringify({champs: lus, roles: roles.filter(function(r){return r.checked;}).map(function(r){return r.value;})}));
'''


def _reprise(donnees, saisie):
    if not NODE:
        pytest.skip('node absent : la reprise de dossier ne peut pas être exécutée')
    d = MOTEUR.index('function regFamillesConnues(){')
    code = MOTEUR[d:MOTEUR.index('\n};', MOTEUR.index('window.regReprendreFamille = function(){', d)) + 3]
    champs = [p[1] for p in re.findall(r"\['(\w+)', '([\w-]+)'\]", code)]
    prog = _SONDE % {
        'donnees': json.dumps(donnees), 'champs': json.dumps(champs),
        'saisie': json.dumps(saisie),
        'roles': json.dumps([{'value': r, 'checked': False}
                             for r in ('fournisseur', 'deployeur', 'importateur', 'distributeur')]),
        'code': code}
    r = subprocess.run([NODE, '-e', prog], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        pytest.fail("la reprise de dossier ne s'exécute pas :\n%s" % (r.stderr or '')[-1200:])
    return json.loads(r.stdout)


MODELE = {'id': 1, 'nom': 'Assistant RH', 'famille': 'Assistants internes',
          'finalite': 'Répondre aux questions des salariés', 'secteur': 'RH',
          'type_systeme': 'LLM conversationnel', 'donnees_utilisees': 'Base de connaissance interne',
          'classification': 'limite', 'justification': 'Art. 50 — interaction avec une IA',
          'service': 'rh', 'personnes_concernees': 'Salariés',
          'transparence_art50': 'deja_conforme', 'roles': ['deployeur'],
          'responsable': 'Marie Durand', 'preuves_conformite': 'Capture du bandeau, 12/06/2026',
          'date_maj': '2026-06-12T10:00:00'}


def test_la_reprise_copie_ce_qui_est_propre_a_la_famille():
    r = _reprise([MODELE], 'Assistants internes')
    for champ, attendu in (('rf-finalite', MODELE['finalite']),
                           ('rf-type', MODELE['type_systeme']),
                           ('rf-classif', MODELE['classification']),
                           ('rf-transp', MODELE['transparence_art50'])):
        assert r['champs'].get(champ) == attendu, (
            "la reprise ne copie pas %s : %r" % (champ, r['champs'].get(champ)))
    assert r['roles'] == ['deployeur'], (
        "les rôles ne sont pas repris : %s" % r['roles'])


def test_la_reprise_ne_copie_JAMAIS_ce_qui_est_propre_au_systeme():
    """RECOPIER UN NOM, UN RESPONSABLE OU DES PREUVES PRODUIRAIT UN FAUX. Les
    preuves surtout : « capture du bandeau, 12/06/2026 » désigne un document
    qui existe pour CE système-là. La reprendre sur un autre, c'est produire
    une conformité documentaire qui ne repose sur rien."""
    r = _reprise([MODELE], 'Assistants internes')
    for interdit in ('rf-nom', 'rf-resp', 'rf-preuves', 'rf-po', 'rf-score'):
        assert interdit not in r['champs'], (
            "la reprise a recopié %s : ce champ est propre à chaque système et "
            "sa reprise fabriquerait un document faux" % interdit)


def test_la_reprise_ignore_une_famille_inconnue():
    """Ne rien trouver n'est pas une erreur : c'est le premier système de sa
    famille. Rien ne doit être écrasé pour autant."""
    r = _reprise([MODELE], 'Une famille qui n’existe pas')
    assert not r['champs'], (
        "des champs ont été remplis alors qu'aucun système de cette famille "
        "n'existe : %s" % r['champs'])


def test_la_reprise_prend_le_systeme_le_plus_recemment_mis_a_jour():
    """Deux systèmes d'une même famille peuvent diverger. Le plus récent est
    celui dont la documentation a été revue en dernier."""
    ancien = dict(MODELE, id=2, nom='Ancien', finalite='Version dépassée',
                  date_maj='2026-01-01T00:00:00')
    r = _reprise([ancien, MODELE], 'Assistants internes')
    assert r['champs'].get('rf-finalite') == MODELE['finalite'], (
        "la reprise a pris le système le plus ancien de la famille")


def test_la_comparaison_de_famille_ignore_la_casse():
    """« Assistants internes » et « assistants internes » sont la même famille.
    Sans cela, le regroupement se défait sur une majuscule."""
    r = _reprise([MODELE], 'ASSISTANTS INTERNES')
    assert r['champs'].get('rf-finalite') == MODELE['finalite'], (
        "une différence de casse suffit à ne plus reconnaître la famille")


def test_la_liste_des_familles_deja_employees_existe():
    """Sans proposition, chacun réinvente son orthographe et le regroupement
    ne regroupe plus rien."""
    assert 'function regFamillesConnues(' in MOTEUR, (
        "la liste des familles déjà employées a disparu")
    # LA LISTE EXISTE-T-ELLE, OU EST-ELLE BRANCHÉE ? Deux propriétés, et une
    # première version ne vérifiait que la première : retirer le
    # `list="rf-familles-connues"` de la saisie laissait la balise <datalist>
    # dans le fichier, la règle passait, et le champ ne proposait plus rien.
    m = re.search(r'id="rf-famille"[^>]*', MOTEUR)
    assert m, "le champ de saisie de la famille a disparu"
    assert 'list="rf-familles-connues"' in m.group(0), (
        "le champ famille n'est plus relié à la liste des familles existantes : "
        "trois orthographes feront trois familles")
    assert '<datalist id="rf-familles-connues">' in MOTEUR, (
        "la liste proposée n'existe plus")


def test_la_famille_est_envoyee_au_serveur():
    d = MOTEUR.index('window.regSave = function(){')
    corps = MOTEUR[d:MOTEUR.index('\n  if(!payload.nom)', d)]
    assert 'famille:' in corps, (
        "la famille n'est pas envoyée à l'enregistrement : le champ sera "
        "saisi puis perdu au premier enregistrement")
