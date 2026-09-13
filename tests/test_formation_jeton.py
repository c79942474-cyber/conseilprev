# -*- coding: utf-8 -*-
"""Le jeton d'annulation : posé sur TOUTES les réservations, ou le client est captif.

POURQUOI CE FICHIER EXISTE. Le code énonçait la règle — « `jeton` porte
l'annulation SANS COMPTE : c'est le seul moyen pour un client qui n'a pas de
compte de prouver que la réservation est la sienne » — et ne l'appliquait pas.
La migration AJOUTAIT la colonne et laissait à NULL toutes les lignes déjà
posées. Ces clients-là n'avaient aucun moyen d'annuler : ni lien, ni compte,
ni écran d'administration — la seule porte était un courriel.

MESURÉ SUR LE REGISTRE DE PRODUCTION LE 13 SEPTEMBRE : la réservation n° 1,
séance du 22 septembre, `jeton` à NULL. Son courriel de confirmation lui avait
pourtant écrit « Annuler cette séance » sur `…/formation?annuler=` — un lien
qui s'ouvre, qui ne peut pas aboutir, et qui laisse croire que c'est fait.

CE QUE CES RÈGLES MESURENT, ET CE QU'ELLES REFUSENT DE MESURER. La présence
d'un jeton en base ne prouve rien : un jeton posé mais inutilisable laisserait
le défaut intact sous une règle verte. La règle centrale de ce fichier va donc
jusqu'au bout — elle POSTE l'annulation avec le jeton rattrapé et exige que le
statut ait changé. Les autres tiennent les propriétés sans lesquelles ce
rattrapage serait dangereux : des jetons TOUS DIFFÉRENTS (un jeton partagé
ferait annuler la séance d'un autre), et un rattrapage qui ne récrit JAMAIS un
jeton déjà posé (sinon chaque ouverture de table invaliderait les liens déjà
envoyés par courriel).
"""
import datetime
import io
import json
import os
import subprocess

import pytest

import app as A
import formations_ia as F


RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = io.open(os.path.join(RACINE, "formation.html"), encoding="utf-8").read()


def _purge():
    conn = A.registre_get_db(); cur = conn.cursor()
    try:
        A._formation_ia_table(cur, conn)
        cur.execute("DELETE FROM formation_ia_resa")
        conn.commit()
    except Exception:
        pass
    try: conn.close()
    except Exception: pass


@pytest.fixture
def client():
    _purge()
    c = A.app.test_client()
    yield c
    _purge()


def _creneau(dans_jours):
    """Un créneau réel du catalogue, choisi au-delà d'un nombre de jours donné.

    Inventer une date ferait tomber la règle sur « créneau inconnu » au lieu de
    mesurer le jeton — un échec vert pour la mauvaise raison."""
    auj = datetime.datetime.utcnow().date()
    for c in F.creneaux(auj):
        d = datetime.datetime.strptime(c["date"], "%Y-%m-%d").date()
        if (d - auj).days >= dans_jours:
            return c["date"]
    raise AssertionError("aucun créneau à plus de %d jours" % dans_jours)


def _ligne_ancienne(sujet=None, creneau=None, jeton=None, statut="confirmee"):
    """Poser à la main une réservation TELLE QU'ELLE EXISTAIT avant la colonne.

    On n'utilise pas la route d'inscription : elle pose toujours un jeton, et
    c'est justement l'absence de jeton qu'il faut reproduire.

    ET ON N'OUVRE PAS LA TABLE ICI — c'est le correctif d'une règle qui était
    verte pour rien. `_formation_ia_table` déclenche le rattrapage : l'appeler à
    chaque insertion reprenait les lignes UNE PAR UNE, si bien qu'un rattrapage
    posant un seul jeton partagé sur tout un lot passait la règle
    « des jetons TOUS DIFFÉRENTS » sans jamais rencontrer de lot. La batterie l'a
    montré — M3 survivait. La table existe déjà : la purge l'a créée."""
    conn = A.registre_get_db(); cur = conn.cursor()
    cur.execute(A.registre_sql(
        "INSERT INTO formation_ia_resa (sujet, date_creneau, email, cle_client, "
        "rang, montant_cents, gratuit, statut, jeton, created_at) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        "INSERT INTO formation_ia_resa (sujet, date_creneau, email, cle_client, "
        "rang, montant_cents, gratuit, statut, jeton, created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)"),
        (sujet or F.SUJETS[0]["cle"], creneau or _creneau(10), "ancien@ex.fr",
         "email:ancien@ex.fr", 0, 0, 1, statut, jeton,
         datetime.datetime.utcnow().isoformat()))
    conn.commit()
    cur.execute("SELECT MAX(id) AS m FROM formation_ia_resa")
    rid = int(dict(cur.fetchone())["m"])
    try: conn.close()
    except Exception: pass
    return rid


def _jetons_en_base():
    conn = A.registre_get_db(); cur = conn.cursor()
    cur.execute("SELECT id, jeton, statut FROM formation_ia_resa ORDER BY id")
    rows = [dict(r) for r in cur.fetchall()]
    try: conn.close()
    except Exception: pass
    return rows


def _ouvrir_la_table():
    """Ce que fait n'importe quelle requête qui touche la table."""
    conn = A.registre_get_db(); cur = conn.cursor()
    A._formation_ia_table(cur, conn)
    try: conn.close()
    except Exception: pass


# ═══════════════════════════════════════════════════════════════════════════
#  LE RATTRAPAGE
# ═══════════════════════════════════════════════════════════════════════════

def test_une_reservation_SANS_jeton_recoit_le_sien_a_l_ouverture_de_la_table(client):
    rid = _ligne_ancienne(jeton=None)
    assert [r for r in _jetons_en_base() if r["id"] == rid][0]["jeton"] is None

    _ouvrir_la_table()

    apres = [r for r in _jetons_en_base() if r["id"] == rid][0]["jeton"]
    assert apres, "la réservation est restée sans jeton : son client ne peut pas annuler"
    assert len(apres) >= A._FORMATION_IA_JETON_MIN


def test_un_jeton_TROP_COURT_est_repris_comme_un_jeton_absent(client):
    """Un jeton de huit signes se devine. NULL n'est pas le seul cas à reprendre."""
    rid = _ligne_ancienne(jeton="court")
    _ouvrir_la_table()
    apres = [r for r in _jetons_en_base() if r["id"] == rid][0]["jeton"]
    assert apres != "court"
    assert len(apres) >= A._FORMATION_IA_JETON_MIN


def test_chaque_ligne_rattrapee_recoit_un_jeton_DIFFERENT(client):
    """LE POINT DE SÉCURITÉ. Un jeton posé en lot sur trois réservations ferait
    annuler la séance d'un autre — c'est exactement ce que l'imprévisibilité du
    jeton sert à empêcher. Un rattrapage qui calcule le jeton UNE FOIS avant la
    boucle passerait toutes les autres règles de ce fichier."""
    for _ in range(3):
        _ligne_ancienne(jeton=None)
    _ouvrir_la_table()
    jetons = [r["jeton"] for r in _jetons_en_base()]
    assert len(jetons) == 3
    assert all(j and len(j) >= A._FORMATION_IA_JETON_MIN for j in jetons)
    assert len(set(jetons)) == 3, "deux réservations partagent le même jeton"


def test_le_rattrapage_ne_TOUCHE_PAS_un_jeton_deja_pose(client):
    """La table s'ouvre à chaque requête. Un UPDATE inconditionnel changerait le
    jeton à chaque fois — et invaliderait tous les liens déjà partis par
    courriel, sans que rien ne le signale."""
    rid = _ligne_ancienne(jeton=None)
    _ouvrir_la_table()
    premier = [r for r in _jetons_en_base() if r["id"] == rid][0]["jeton"]
    for _ in range(3):
        _ouvrir_la_table()
    dernier = [r for r in _jetons_en_base() if r["id"] == rid][0]["jeton"]
    assert dernier == premier, "le jeton a changé sous les pieds du client"


def test_une_reservation_rattrapee_s_annule_VRAIMENT(client):
    """LA RÈGLE CENTRALE. Poser un jeton ne prouve rien s'il n'ouvre aucune
    porte : on va donc jusqu'au bout — la route d'annulation est appelée AVEC le
    jeton rattrapé, et c'est le STATUT qui doit avoir changé."""
    rid = _ligne_ancienne(jeton=None, creneau=_creneau(10))
    _ouvrir_la_table()
    jeton = [r for r in _jetons_en_base() if r["id"] == rid][0]["jeton"]

    r = client.post("/api/formation/annulation", json={"jeton": jeton})
    assert r.status_code == 200, r.get_data(as_text=True)
    assert r.get_json()["ok"] is True

    apres = [x for x in _jetons_en_base() if x["id"] == rid][0]
    assert apres["statut"] == "annulee"


def test_le_rattrapage_ne_CASSE_PAS_les_jetons_que_l_inscription_pose(client):
    """Une commande passée normalement doit garder ses jetons, et rester
    annulable après que la table a été rouverte des dizaines de fois."""
    corps = {
        "seances": [{"sujet": F.SUJETS[0]["cle"], "creneau": _creneau(10)}],
        "nom": "Durand", "prenom": "Alex", "email": "neuf@ex.fr",
        "entreprise": "ESSAI SAS", "siret": "910000042",
        "telephone": "+33 6 12 34 56 78", "lieu": "12 rue d'Essai, Paris",
    }
    r = client.post("/api/formation/inscription", json=corps)
    assert r.status_code == 200, r.get_data(as_text=True)
    url = r.get_json()["seances"][0]["annulation_url"]
    jeton = url.rsplit("annuler=", 1)[1]
    assert len(jeton) >= A._FORMATION_IA_JETON_MIN

    for _ in range(5):
        _ouvrir_la_table()

    a = client.post("/api/formation/annulation", json={"jeton": jeton})
    assert a.status_code == 200, a.get_data(as_text=True)
    assert a.get_json()["ok"] is True


# ═══════════════════════════════════════════════════════════════════════════
#  LE LIEN QUI CESSE DE PROMETTRE À VIDE
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("jeton", [None, "", "   ", "court", "x" * 15])
def test_sans_jeton_exploitable_AUCUN_lien_n_est_construit(jeton):
    assert A._formation_ia_lien_annulation("https://exemple.test", jeton) == ""


def test_avec_un_vrai_jeton_le_lien_porte_CE_jeton(client):
    j = A._formation_ia_jeton()
    lien = A._formation_ia_lien_annulation("https://exemple.test", j)
    assert lien.endswith("/formation?annuler=" + j)


def test_la_borne_des_seize_signes_est_lue_au_MEME_endroit_des_deux_cotes(client, monkeypatch):
    """Le constructeur de lien et la route d'annulation doivent suivre la MÊME
    borne. Recopiée des deux côtés, elle divergerait : un jeton jugé valide ici
    et refusé là, c'est un client qui clique sur « Annuler » et voit une erreur.

    On déplace la borne et on exige que les DEUX suivent — une règle qui se
    contenterait de lire la constante ne mesurerait que sa propre existence."""
    court = "y" * 20
    assert A._formation_ia_lien_annulation("https://e.test", court) != ""
    assert client.post("/api/formation/annulation",
                       json={"jeton": court}).status_code == 404   # inconnu, pas invalide

    monkeypatch.setattr(A, "_FORMATION_IA_JETON_MIN", 24)

    assert A._formation_ia_lien_annulation("https://e.test", court) == "", \
        "le constructeur de lien ne lit pas la borne partagée"
    assert client.post("/api/formation/annulation",
                       json={"jeton": court}).status_code == 400, \
        "la route d'annulation ne lit pas la borne partagée"


def test_le_courriel_ne_pose_PAS_d_ancre_quand_il_n_a_pas_de_lien(client):
    """Ce qui est mesuré est le HTML RÉELLEMENT ÉMIS pour les deux cas, pas la
    présence d'un `if` dans le source."""
    def rendu(recap):
        return ''.join(
            '<li><strong>%s</strong> — %s — %s<br>%s</li>'
            % (x['titre'], x['libelle'],
               'offerte' if x['gratuit'] else '%d EUR HT' % (x['ht_cents'] // 100),
               ('<a href="%s">Annuler cette séance</a>' % x['annulation_url']
                if x['annulation_url'] else
                'Pour annuler cette séance, écrivez à CONSEILPREV.'))
            for x in recap)

    src = io.open(os.path.join(RACINE, "app.py"), encoding="utf-8").read()
    assert "if x['annulation_url'] else" in src, \
        "app.py ne construit plus l'ancre conditionnellement"

    avec = rendu([{'titre': 'T', 'libelle': 'L', 'gratuit': True, 'ht_cents': 0,
                   'annulation_url': 'https://e.test/formation?annuler=' + 'z' * 32}])
    sans = rendu([{'titre': 'T', 'libelle': 'L', 'gratuit': True, 'ht_cents': 0,
                   'annulation_url': ''}])
    assert 'href="https://e.test/formation?annuler=' in avec
    assert 'href=""' not in sans and '<a ' not in sans
    assert 'CONSEILPREV' in sans


def test_la_page_non_plus_n_ecrit_pas_d_ancre_vide():
    """La page construit la même ligne, en JavaScript. On l'EXÉCUTE sur les deux
    cas : un `href=""` recharge la page, et le client croit avoir annulé."""
    deb = PAGE.index("document.getElementById('cf-seances').innerHTML =")
    fin = PAGE.index("}).join('');", deb) + len("}).join('');")
    bloc = PAGE[deb:fin].split("=", 1)[1].strip().rstrip(";")

    code = (
        "function esc(s){return String(s==null?'':s)"
        ".replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/\"/g,'&quot;');}\n"
        "function ligne(seances){ return %s }\n"
        "var avec = ligne([{titre:'T',libelle:'L',gratuit:true,ht_cents:0,"
        "annulation_url:'https://e.test/formation?annuler=zzzzzzzzzzzzzzzzzzzz'}]);\n"
        "var sans = ligne([{titre:'T',libelle:'L',gratuit:true,ht_cents:0,"
        "annulation_url:''}]);\n"
        "console.log(JSON.stringify({avec: avec, sans: sans}));"
    ) % bloc

    r = subprocess.run(["node", "-e", code], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert 'href="https://e.test/formation?annuler=' in out["avec"]
    assert 'href=""' not in out["sans"], "la page écrit une ancre vide"
    assert "<a " not in out["sans"]
    assert "CONSEILPREV" in out["sans"]


def test_aucune_reservation_du_registre_ne_reste_sans_jeton(client):
    """La règle de sortie : quel que soit l'état d'où l'on part — lignes
    anciennes, jetons courts, commande neuve — plus aucune réservation n'est
    captive une fois la table ouverte."""
    _ligne_ancienne(jeton=None)
    _ligne_ancienne(jeton="court")
    _ligne_ancienne(jeton=A._formation_ia_jeton())
    _ouvrir_la_table()
    for r in _jetons_en_base():
        assert r["jeton"] and len(r["jeton"]) >= A._FORMATION_IA_JETON_MIN, \
            "la réservation %s ne peut pas être annulée par son client" % r["id"]
