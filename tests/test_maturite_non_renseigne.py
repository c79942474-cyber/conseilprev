# -*- coding: utf-8 -*-
"""L'audit de maturité cesse de répondre à la place de l'utilisateur.

LE DÉFAUT MESURÉ. Les seize réponses étaient PRÉ-REMPLIES depuis le profil
sectoriel de référence, avant que l'utilisateur ait touché à quoi que ce soit.
Relevé au navigateur, panneau ouvert et rien de cliqué :

    secteur telecom · score global 2,7 / 5 · 8 piliers notés

Et comme les trois boutons ne proposaient que Non (0), Partiel (0,5) et Oui
(1), un zéro par défaut était INDISCERNABLE d'un « Non » répondu. L'écran
rendait un diagnostic que personne n'avait posé.

Second défaut, mesuré aussi : AUCUNE clé de stockage ne concernait ce module.
Les seize réponses disparaissaient à chaque rechargement.

APRÈS, même parcours :

    avant toute réponse   score 0 · 0/16 répondues · 0 bouton allumé · [null, null]
    après seize réponses  score 2,5 · 16/16 · 16 boutons allumés
    après rechargement    score 2,5 · 16/16 · mêmes réponses — elles ont survécu
    clé de mémoire        cp-sentinel-maturite-v1

C'est le défaut que ce dépôt a déjà corrigé six fois — l'audit IA Act, l'AIPD,
la privacy by design, la politique documentaire, la sensibilisation et
l'analyse de risque ReCyF : « pas coché » s'y confondait avec « pas encore
regardé ». Même remède, et les mêmes règles pour le tenir.
"""
import io
import json
import os
import re
import shutil
import subprocess

import pytest

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE = shutil.which("node")


def _lire(nom):
    with io.open(os.path.join(RACINE, nom), encoding="utf-8") as f:
        return f.read()


ECRAN = _lire("sentinel.page.js")


def _bloc(depuis, jusqu_a):
    i = ECRAN.index(depuis)
    return ECRAN[i:ECRAN.index(jusqu_a, i)]


#: Le moteur réel du module, extrait du fichier servi : les questions, les
#: réponses, l'initialisation, le score d'un pilier, le score global et le
#: compteur de réponses. On exécute CE code, pas une reformulation.
def _moteur():
    morceaux = []
    for debut, fin in (
        ("var MAT_QUESTIONS = {", "\nwindow.MAT_QUESTIONS"),
        ("function matInitAnswers(sectorKey){", "\n/* Calcul du score d'un pilier"),
        ("window.matPillarScore = function", "\n/* Niveau de maturité textuel */"),
    ):
        morceaux.append(_bloc(debut, fin))
    return "\n".join(morceaux)


def _node(corps):
    if not NODE:
        pytest.skip("node absent : le moteur de maturité ne peut pas être exécuté")
    prog = ["var window = {};", "var MAT_ANSWERS = {};", "window.MAT_ANSWERS = MAT_ANSWERS;",
            _moteur(), corps]
    r = subprocess.run([NODE, "-e", "\n".join(prog)],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        pytest.fail("le moteur ne s'exécute pas :\n%s" % (r.stderr or "")[-1500:])
    return json.loads(r.stdout.strip())


# ── 1. RIEN N'EST RÉPONDU TANT QUE RIEN N'EST RÉPONDU ────────────────────

def test_a_l_ouverture_aucune_question_n_a_de_reponse():
    """LE DÉFAUT D'ORIGINE, EXÉCUTÉ. Le module notait les huit piliers avant
    la première question."""
    r = _node("""
      matInitAnswers('telecom');
      console.log(JSON.stringify({
        reponses: MAT_ANSWERS.telecom,
        repondu: window.matRepondu('telecom'),
        global: window.matGlobalScore ? null : null
      }));""")
    for pilier, a in r["reponses"].items():
        assert a == [None, None], (pilier, a)
    assert r["repondu"]["repondues"] == 0, r["repondu"]
    assert r["repondu"]["total"] == 16, r["repondu"]
    assert r["repondu"]["complet"] is False


def test_un_pilier_sans_reponse_ne_vaut_aucun_score():
    r = _node("""
      matInitAnswers('telecom');
      console.log(JSON.stringify(window.matPillarScore('telecom','explicabilite')));""")
    assert r == 0, r


def test_le_profil_sectoriel_ne_prete_plus_ses_notes_a_l_utilisateur():
    """La référence du secteur reste affichée ailleurs ; elle n'est plus
    versée dans les réponses."""
    corps = _bloc("function matInitAnswers(sectorKey){", "\n/* CE QUI EST RÉPONDU")
    assert "MAT_SECTORS" not in corps, (
        "matInitAnswers lit encore le profil sectoriel : %s" % corps[:400])
    assert "[null, null]" in corps, corps[:400]


# ── 2. « NON » RÉPONDU N'EST PAS « PAS ENCORE RÉPONDU » ──────────────────

def test_un_non_repondu_compte_comme_une_reponse_et_vaut_zero():
    """Les deux états sont distincts, et c'est tout l'enjeu : `null` ne se
    compte pas, `0` se compte et vaut zéro."""
    r = _node("""
      matInitAnswers('telecom');
      MAT_ANSWERS.telecom.explicabilite[0] = 0;
      console.log(JSON.stringify({
        score: window.matPillarScore('telecom','explicabilite'),
        repondu: window.matRepondu('telecom')
      }));""")
    assert r["repondu"]["repondues"] == 1, r["repondu"]
    assert r["score"] == 0, r


def test_le_score_porte_sur_les_reponses_recues_et_pas_sur_les_cases_vides():
    """Un « Oui » sur une des deux questions d'un pilier donne 5/5 sur ce qui
    est répondu, pas 2,5/5 — compter une question sans réponse comme un
    « Non » donnerait un chiffre bas qui a l'air d'un diagnostic."""
    r = _node("""
      matInitAnswers('telecom');
      MAT_ANSWERS.telecom.explicabilite[0] = 1;
      console.log(JSON.stringify(window.matPillarScore('telecom','explicabilite')));""")
    assert r == 5.0, r


def test_un_parcours_commence_n_est_pas_un_parcours_complet():
    """« complet » doit dire LES SEIZE, jamais « au moins une ». Une seule
    réponse validerait sinon le module entier."""
    r = _node("""
      matInitAnswers('telecom');
      MAT_ANSWERS.telecom.explicabilite = [1, 1];
      MAT_ANSWERS.telecom.gouvernance[0] = 0.5;
      console.log(JSON.stringify(window.matRepondu('telecom')));""")
    assert r["repondues"] == 3, r
    assert r["total"] == 16, r
    assert r["complet"] is False, (
        "trois réponses sur seize suffisent à déclarer le module fini : %s" % r)


def test_les_seize_reponses_donnent_un_parcours_complet():
    r = _node("""
      matInitAnswers('telecom');
      Object.keys(MAT_ANSWERS.telecom).forEach(function(p){
        MAT_ANSWERS.telecom[p] = [1, 1];
      });
      console.log(JSON.stringify({
        repondu: window.matRepondu('telecom'),
        pilier: window.matPillarScore('telecom','explicabilite')
      }));""")
    assert r["repondu"]["complet"] is True, r["repondu"]
    assert r["repondu"]["repondues"] == 16, r["repondu"]
    assert r["pilier"] == 5.0, r


#: La valeur répondue, et le score sur 5 qu'elle vaut à elle seule.
TROIS_VALEURS = [(0, 0.0), (0.5, 2.5), (1, 5.0)]


@pytest.mark.parametrize("valeur,attendu", TROIS_VALEURS)
def test_les_trois_valeurs_admises_comptent_comme_une_reponse(valeur, attendu):
    """Les deux compteurs doivent reconnaître les trois valeurs : celui qui
    dit COMBIEN de questions ont une réponse, et celui qui en tire un score.
    La première version n'interrogeait que le premier — un « Partiel » retiré
    du calcul du score passait inaperçu."""
    r = _node("""
      matInitAnswers('telecom');
      MAT_ANSWERS.telecom.explicabilite[0] = %s;
      console.log(JSON.stringify({
        repondues: window.matRepondu('telecom').repondues,
        score: window.matPillarScore('telecom','explicabilite')
      }));""" % valeur)
    assert r["repondues"] == 1, r
    assert r["score"] == attendu, r


# ── 3. L'ÉCRAN N'ALLUME AUCUN BOUTON TANT QUE RIEN N'EST RÉPONDU ─────────

def test_aucun_bouton_n_est_allume_par_defaut():
    """Le défaut se voyait ici : la valeur courante valait 0, et « Non »
    paraissait choisi sur les seize questions."""
    m = re.search(r"var cur = \(window\.MAT_ANSWERS\[MAT_CUR\][^;]*;", ECRAN)
    assert m, "la valeur courante d'une question est introuvable"
    assert m.group(0).rstrip().endswith(": null;"), (
        "une question sans réponse retombe sur une valeur qui allume un "
        "bouton : %s" % m.group(0))


def test_l_ecran_dit_combien_de_questions_ont_une_reponse():
    """Un 4,2 / 5 obtenu sur deux questions ne se lit pas comme le même 4,2
    obtenu sur seize."""
    assert "matq-repondu" in ECRAN
    assert "questions répondue" in ECRAN or "question' + (r.total" in ECRAN
    assert "window.matRepondu(MAT_CUR)" in ECRAN, (
        "le compteur n'est pas peint au rendu : il resterait vide pour qui "
        "n'a encore rien répondu")


# ── 4. LES RÉPONSES SURVIVENT AU RECHARGEMENT ────────────────────────────

def test_le_module_a_une_memoire_declaree():
    m = re.search(r"maturite: \{ norme: 'maturite'.*?cle: '([\w-]+)'", ECRAN, re.S)
    assert m, "l'audit de maturité n'a aucune entrée de mémoire"
    assert m.group(1).startswith("cp-sentinel-"), m.group(1)


def test_la_memoire_garde_les_reponses_et_le_secteur_pas_les_scores():
    bloc = _bloc("maturite: { norme: 'maturite'", "  nis2: {")
    #  CE QUE LA MÉMOIRE LIT, ET PAS CE QU'ELLE RELIT. Chercher les deux mots
    #  dans tout le bloc laissait passer leur retrait de `lire` : « secteur »
    #  figure aussi dans la relecture, et la règle passait pour rien.
    ecrit = _bloc("lire: function () {\n      if (typeof window.MAT_ANSWERS",
                  "    relire: function (m) {")
    assert "reponses" in ecrit, (
        "la mémoire n'écrit pas les réponses : %s" % ecrit[:300])
    assert "matGetCur" in ecrit, (
        "la mémoire n'écrit pas le secteur choisi : qui change de secteur le "
        "retrouverait sur un autre au rechargement — %s" % ecrit[:300])
    for recalcule in ("matGlobalScore", "matPillarScore", "niveau", "radar"):
        assert recalcule not in bloc, (
            "« %s » est gardé alors qu'il se recalcule" % recalcule)


@pytest.mark.parametrize("valeur", ["'oui'", "2", "-1", "null", "{}"])
def test_une_reponse_illisible_est_ecartee_seule(valeur):
    """« Une valeur d'un autre type est écartée, jamais recopiée » : une
    réponse abîmée ne doit pas coûter les quinze autres."""
    bloc = _bloc("relire: function (m) {\n      if (typeof window.MAT_ANSWERS",
                 "    } },\n  nis2: {")
    prog = ("var window = { MAT_ANSWERS: {} };\n"
            "var relire = function (m) {\n" + bloc.split("relire: function (m) {", 1)[1]
            .rsplit("} },", 1)[0] + "};\n"
            "relire({reponses: {telecom: {explicabilite: [1, %s]}}});\n"
            "console.log(JSON.stringify(window.MAT_ANSWERS.telecom.explicabilite));" % valeur)
    if not NODE:
        pytest.skip("node absent")
    r = subprocess.run([NODE, "-e", prog], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-800:]
    assert json.loads(r.stdout.strip()) == [1, None], r.stdout
