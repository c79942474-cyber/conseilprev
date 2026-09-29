# -*- coding: utf-8 -*-
"""LA MESURE DE CE QUI RESTE EN FRANÇAIS — outils/sentinel_langue.js,
recette_sentinel_langue.js et i18n/sentinel/MESURE_AVANT.json.

CE QUI EXISTAIT, ET CE QUI MANQUAIT. Le corps de Sentinel se traduit par
contenu (sentinel.i18n.js) ; le dictionnaire est presque vide. Pour que le
lot de traduction sache ce qu'il doit battre, il fallait une MESURE : dans un
vrai navigateur, EN choisi, chaque page de PAGE_META visitée, tout ce qui est
visible relevé et classé français / anglais / neutre. La recette fait cela ;
ces règles gardent ce dont elle dépend et ce qu'elle a produit.

CE QUI A CHANGÉ DEPUIS. Les DONNÉES SAISIES (noms de systèmes, fournisseurs,
finalités, clients — déclarées translate="no") sont désormais relevées à part
et tenues hors du verdict ; les CADRES, eux, y entrent, parce qu'ils se
traduisent maintenant eux-mêmes. Ces deux partages sont gardés par
tests/test_sentinel_donnees_saisies.py ; ce qui suit garde le reste.

CES RÈGLES EXÉCUTENT LE CODE. L'heuristique de classement tourne sous node,
sur le VRAI outils/sentinel_langue.js, avec des phrases françaises, anglaises,
neutres et mixtes — et les cas qu'elle classe MAL sont écrits ici aussi, pour
qu'on sache ce que le score ignore. L'agrégation, le seuil et le code de
sortie sont éprouvés sur des relevés fabriqués, puis sur la VRAIE recette en
mode --relire (sans navigateur). Enfin, MESURE_AVANT.json — le point de
départ commité — doit couvrir les 118 pages de PAGE_META : une page oubliée
serait une page que personne ne mesure.
"""
import io
import json
import os
import re
import shutil
import subprocess
import unicodedata

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE = shutil.which("node")
MODULE = os.path.join(_RACINE, "outils", "sentinel_langue.js")
RECETTE = os.path.join(_RACINE, "recette_sentinel_langue.js")
MESURE_AVANT = os.path.join(_RACINE, "i18n", "sentinel", "MESURE_AVANT.json")


def _lire(nom):
    return io.open(os.path.join(_RACINE, nom), encoding="utf-8").read()


def _ids(cas):
    out = []
    for c in cas:
        s = unicodedata.normalize("NFKD", c[0]).encode("ascii", "ignore").decode()
        out.append(re.sub(r"-+", "-", re.sub(r"[^A-Za-z0-9]+", "-", s)).strip("-")[:40])
    return out


# ══════════════════════════════════════════════════════════════════════════
#  LE HARNAIS — le vrai module, sous node, un appel par règle
# ══════════════════════════════════════════════════════════════════════════

_HARNAIS = """
const M = require(process.argv[1]);
const prog = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = prog.map(([fn, args]) => { try { return M[fn].apply(null, args); } catch (e) { return { erreur: String(e) }; } });
process.stdout.write(JSON.stringify(out));
"""


def _node(*appels):
    """Joue `[nom de fonction, [arguments]]…` sur le module ; rend un
    résultat par appel."""
    if not NODE:
        pytest.skip("node absent : l'heuristique ne peut pas être exécutée")
    r = subprocess.run([NODE, "-e", _HARNAIS, MODULE],
                       input=json.dumps(list(appels), ensure_ascii=False),
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        pytest.fail("le module n'a pas tourné :\n%s" % (r.stderr or "")[-2000:])
    out = json.loads(r.stdout)
    for i, x in enumerate(out):
        assert not (isinstance(x, dict) and "erreur" in x), "l'appel %d a levé : %s" % (i, x["erreur"])
    return out


def _classer(texte):
    return _node(["classer", [texte]])[0]


# ══════════════════════════════════════════════════════════════════════════
#  1. L'HEURISTIQUE DE CLASSEMENT
# ══════════════════════════════════════════════════════════════════════════

CAS_FRANCAIS = [
    ("phrase à mots-outils", u"Modules certifiants — progression calculée à partir de vos scores réels de l'Audit de maturité IA par pilier."),
    ("un seul mot accentué", u"Coûts"),
    ("élision", u"l'audit de maturité"),
    ("élision seule", u"l'audit"),
    ("mot-outil « de »", u"Registre de traitements"),
    ("sans accent mais avec mots-outils", u"Qualification reglementaire deterministe, lectures possibles des textes"),
    ("terminaison -ique", u"Panorama juridique"),
    ("libellé d'interface", u"Toutes (15)"),
    ("bouton d'un mot", u"Voir"),
    ("mot-outil « en »", u"Il en reste"),
    ("nom propre au milieu d'une phrase française", u"Le cadre ISO 42001 structure l'ensemble."),
    ("anglicismes noyés dans du français", u"Le reporting et le monitoring de la plateforme"),
]
CAS_ANGLAIS = [
    ("phrase à mots-outils", u"Certifying modules — progress computed from your real AI maturity audit scores, pillar by pillar."),
    ("contraction", u"It's the audit of the year"),
    ("terminaison -ing", u"Steering"),
    ("terminaison -ly", u"Weekly"),
    ("libellé d'interface", u"View all"),
    ("mot-outil « on » seul", u"on"),
]
CAS_NEUTRES = [
    ("sans lettre", u"12 %"),
    ("vide", u""),
    ("nom propre seul", u"EU AI Act"),
    ("nom propre et nombre", u"ISO 42001"),
    ("deux noms propres", u"Sentinel AI"),
    ("mot sans signal", u"Budget"),
    ("mot partagé « a »", u"a"),
    ("égalité fr / en", u"le on"),
]


@pytest.mark.parametrize("nom,texte", CAS_FRANCAIS, ids=_ids(CAS_FRANCAIS))
def test_un_texte_francais_est_classe_fr(nom, texte):
    c = _classer(texte)
    assert c["langue"] == "fr", "%s → %s" % (texte, c)


@pytest.mark.parametrize("nom,texte", CAS_ANGLAIS, ids=_ids(CAS_ANGLAIS))
def test_un_texte_anglais_est_classe_en(nom, texte):
    c = _classer(texte)
    assert c["langue"] == "en", "%s → %s" % (texte, c)


@pytest.mark.parametrize("nom,texte", CAS_NEUTRES, ids=_ids(CAS_NEUTRES))
def test_un_texte_sans_signal_est_NEUTRE(nom, texte):
    """Ce que l'heuristique ne sait pas décider ne compte pour aucune langue :
    le mettre d'un côté fausserait le score dans ce sens."""
    c = _classer(texte)
    assert c["langue"] == "neutre", "%s → %s" % (texte, c)


def test_un_texte_mixte_se_decide_a_la_majorite_des_points():
    fr = _classer(u"Le reporting et le monitoring")   # 3 points fr, 2 points en
    en = _classer(u"The monitoring of la plateforme")  # 3 points en, 1 point fr
    assert (fr["langue"], fr["fr"], fr["en"]) == ("fr", 3, 2), fr
    assert (en["langue"], en["en"], en["fr"]) == ("en", 3, 1), en


def test_un_nom_propre_ne_se_retire_qu_ENTIER():
    """« DORADE » n'est pas « DORA » suivi de « DE » — qui est un mot-outil
    français et ferait basculer un poisson en français. Le nom propre ne se
    retire qu'entre deux non-lettres ; « ISOLÉ » et « CRAINTE » restent des
    mots entiers."""
    assert _classer(u"DORADE")["langue"] == "neutre"
    assert _classer(u"ISOLÉ")["langue"] == "fr"
    assert _classer(u"CRAINTE des sanctions")["langue"] == "fr"
    assert _classer(u"EU AI Act — NIS 2 — DORA — CRA — ReCyF")["langue"] == "neutre"


def test_les_mots_se_comptent_en_lettres_sans_les_noms_propres_et_l_elision_est_un_seul_mot():
    """« ISO » n'est un mot d'aucune langue : il ne pèse dans aucun score."""
    assert _node(["compterMots", [u"Toutes (15) — l'audit de maturité"]])[0] == 4
    assert _node(["compterMots", [u"12 % — 2024"]])[0] == 0
    assert _classer(u"Programme détaillé")["mots"] == 2
    assert _classer(u"Le cadre ISO 42001 structure l'ensemble.")["mots"] == 4
    assert _classer(u"EU AI Act")["mots"] == 0


CE_QU_ELLE_CLASSE_MAL = [
    # (texte, langue rendue, ce qu'il est vraiment) — écrit pour que le
    # lecteur du score sache ce qu'il ignore. Une amélioration de
    # l'heuristique doit déplacer ces cas, pas les casser en silence.
    (u"FORMATION 01", "neutre", "français : « FORMATION » est le mot français, l'anglais dirait TRAINING"),
    (u"Detailed programme", "neutre", "anglais : aucun mot-outil, aucune terminaison propre"),
    (u"Pilotage", "neutre", "français : « -age » est partagé (manage, storage)"),
    (u"Dashboard", "neutre", "anglais : aucun signal"),
]


@pytest.mark.parametrize("texte,rendu,verite", CE_QU_ELLE_CLASSE_MAL,
                         ids=[_ids([(t,)])[0] for t, _, _ in CE_QU_ELLE_CLASSE_MAL])
def test_ce_que_l_heuristique_classe_MAL_est_ecrit_et_connu(texte, rendu, verite):
    c = _classer(texte)
    assert c["langue"] == rendu, "%s → %s (attendu %s ; en vrai : %s)" % (texte, c, rendu, verite)


def test_les_listes_de_mots_outils_de_la_conception_sont_toutes_la():
    """Les mots-outils nommés par la conception : un retiré par mégarde et
    des phrases entières basculent en neutre."""
    src = _lire("outils/sentinel_langue.js")
    for m in ("le", "la", "les", "des", "une", "un", "et", "est", "pour", "dans", "avec", "sur",
              "par", "pas", "vous", "votre", "cette", "ce", "sont", "au", "aux", "du", u"être",
              "ou", "qui", "que", "ne", "se"):
        assert re.search(r"MOTS_FR = \[[^\]]*'%s'" % m, src, re.S), "mot-outil français absent : %s" % m
    for m in ("the", "and", "of", "to", "is", "for", "with", "on", "in", "are", "this", "that",
              "your", "be", "by", "as", "at", "from", "or", "which", "not", "it"):
        assert re.search(r"MOTS_EN = \[[^\]]*'%s'" % m, src, re.S), "mot-outil anglais absent : %s" % m


# ══════════════════════════════════════════════════════════════════════════
#  2. L'AGRÉGATION — des relevés au JSON de mesure
# ══════════════════════════════════════════════════════════════════════════

RELEVES = {
    "pages": {
        "espace": [
            {"t": u"Aucune activité récente.", "ou": "texte"},          # fr, 3 mots
            {"t": u"Aucune activité récente.", "ou": "texte"},          # la même, deux fois
            {"t": u"Your recent activity", "ou": "texte"},              # en, 3 mots
            {"t": u"12 %", "ou": "texte"},                              # neutre, 0 mot
            {"t": u"Budget", "ou": "texte"},                            # neutre, 1 mot
            {"t": u"Ouvrir le guide de cette page", "ou": "title"},     # fr, 6 mots
        ],
        "training": [
            {"t": u"Detailed programme", "ou": "texte"},                # neutre, 2 mots
        ],
        "pan-sia": [
            {"t": u"Panorama des cas", "ou": "texte"},                  # fr, 3 mots
            {"t": u"Le panorama complet des cas d'usage", "ou": "cadre:texte"},  # cadre, fr, 6 mots
            {"t": u"Loading the map", "ou": "cadre:texte"},             # cadre, en, 3 mots
        ],
    },
    "coquille": [
        {"t": u"Steering", "ou": "texte"},                              # en, 1 mot
        {"t": u"Se déconnecter de l'espace client", "ou": "title"},     # fr, 5 mots
    ],
}


def _agreger(seuil=None):
    opts = {"base": "http://x", "date": "2026-09-24T00:00:00Z", "dictionnaire": {"charge": True, "texte": 6, "bloc": 1}}
    if seuil is not None:
        opts["seuil"] = seuil
    return _node(["agreger", [RELEVES, opts]])[0]


def test_le_JSON_de_mesure_a_la_structure_attendue():
    m = _agreger()
    assert set(m) >= {"_quoi", "date", "base", "seuil", "dictionnaire", "global", "coquille", "pages", "cadres"}, sorted(m)
    assert m["global"]["pages"] == 3
    for p in m["pages"].values():
        assert set(p) >= {"mots_fr", "mots_en", "mots_neutres", "textes", "part_fr", "restes"}, sorted(p)
    assert m["seuil"] == 0.05, "le seuil par défaut est 5 %%, lu %s" % m["seuil"]


def test_chaque_occurrence_compte_dans_les_mots_et_une_seule_fois_dans_les_restes():
    p = _agreger()["pages"]["espace"]
    assert p["mots_fr"] == 3 + 3 + 6, p
    assert p["mots_en"] == 3, p
    assert p["mots_neutres"] == 1, p
    assert p["textes"] == 6, p
    assert [r["texte"] for r in p["restes"]] == [u"Ouvrir le guide de cette page", u"Aucune activité récente."], p["restes"]
    assert p["restes"][0]["ou"] == "title" and p["restes"][0]["mots"] == 6


def test_la_part_francaise_ne_compte_que_les_mots_DECIDES():
    m = _agreger()
    assert m["pages"]["espace"]["part_fr"] == 0.8, m["pages"]["espace"]          # 12 / (12 + 3)
    assert m["pages"]["training"]["part_fr"] is None, m["pages"]["training"]   # rien de décidé
    assert m["coquille"]["part_fr"] == 0.8333, m["coquille"]                    # 5 / 6
    # global : espace 12 fr + pan-sia 3 + 6 fr (cadre compris) + coquille 5 fr
    #          = 26 fr ; 3 + 3 + 1 = 7 en
    assert (m["global"]["mots_fr"], m["global"]["mots_en"]) == (26, 7), m["global"]
    assert m["global"]["part_fr"] == 0.7879, m["global"]


def test_les_cadres_sont_dits_A_PART_et_COMPTENT_dans_le_verdict():
    """CE QUI A CHANGÉ, ET POURQUOI. Un iframe restait hors du verdict tant
    que le dictionnaire ne l'atteignait pas. Depuis que ces documents
    chargent sentinel.i18n.js (data-sent-cadre), ils se traduisent par LA
    MÊME mécanique que Sentinel : les tenir dehors reviendrait à ne pas
    regarder un cinquième de ce qu'un lecteur voit. Ils restent comptés à
    part, EN PLUS, parce qu'une page qui régresse doit se nommer."""
    m = _agreger()
    p = m["pages"]["pan-sia"]
    assert (p["mots_fr"], p["mots_en"]) == (9, 3), p
    assert p["cadres"]["mots_fr"] == 6 and p["cadres"]["mots_en"] == 3, p["cadres"]
    assert m["cadres"]["pages"] == 1 and m["cadres"]["mots_fr"] == 6, m["cadres"]
    assert "cadres" not in m["pages"]["espace"]


def test_les_restes_sont_limites_a_quinze_et_tries_des_plus_longs_aux_plus_courts():
    lot = [{"t": u"phrase française numéro %d avec %s" % (i, " ".join([u"mot"] * i)), "ou": "texte"} for i in range(1, 25)]
    m = _node(["mesurerLot", [lot]])[0]
    assert len(m["restes"]) == 15, len(m["restes"])
    mots = [r["mots"] for r in m["restes"]]
    assert mots == sorted(mots, reverse=True), mots
    assert mots[0] == 4 + 24, mots[0]


def test_les_dix_pires_pages_viennent_par_part_puis_par_masse_et_les_indecises_en_dernier():
    m = _agreger()
    pires = _node(["pires", [m, 10]])[0]
    assert [p["page"] for p in pires] == ["espace", "pan-sia", "training"], pires
    m2 = json.loads(json.dumps(m))
    m2["pages"]["autre"] = dict(m["pages"]["pan-sia"], mots_fr=30, part_fr=1)
    assert [p["page"] for p in _node(["pires", [m2, 2]])[0]] == ["autre", "espace"]


# ══════════════════════════════════════════════════════════════════════════
#  3. LE SEUIL ET LE CODE DE SORTIE
# ══════════════════════════════════════════════════════════════════════════

def _mesure_a(part):
    return {"global": {"part_fr": part, "mots_fr": 1, "mots_en": 1, "mots_neutres": 0, "textes": 1, "pages": 1},
            "coquille": {"part_fr": None, "mots_fr": 0, "mots_en": 0, "mots_neutres": 0, "textes": 0, "restes": []},
            "pages": {}, "seuil": 0.05}


@pytest.mark.parametrize("part,seuil,code", [
    (0.936, 0.05, 1), (0.051, 0.05, 1), (0.05, 0.05, 0), (0.0, 0.0, 0), (0.01, 0.0, 1), (None, 0.05, 0),
], ids=["93-pct", "juste-au-dessus", "egal", "zero-zero", "au-dessus-de-zero", "rien-de-decide"])
def test_le_verdict_vaut_1_quand_la_part_DEPASSE_le_seuil(part, seuil, code):
    assert _node(["verdict", [_mesure_a(part), seuil]])[0] == code


def test_le_seuil_par_defaut_est_5_pour_cent():
    assert _node(["verdict", [_mesure_a(0.06)]])[0] == 1
    assert _node(["verdict", [_mesure_a(0.04)]])[0] == 0


def test_le_resume_dit_les_chiffres_globaux_et_les_dix_pires_pages():
    m = _agreger()
    r = _node(["resumer", [m]])[0]
    assert u"PART FRANÇAISE GLOBALE : 78.8 %" in r, r
    assert u"pan-sia" in r and u"espace" in r and u"training" in r, r
    assert u"cadres (iframes, COMPRIS dans le verdict)" in r, r
    assert u"code 1" in r, r


def _recette(*args):
    if not NODE:
        pytest.skip("node absent")
    return subprocess.run([NODE, RECETTE] + list(args), capture_output=True, text=True, timeout=60)


def test_la_recette_en_mode_relire_rend_le_code_du_verdict_sans_navigateur(tmp_path):
    """Le même chemin que la fin d'une vraie recette — résumé, verdict, code
    de sortie — joué sur un JSON déjà mesuré."""
    p = str(tmp_path / "m.json")
    io.open(p, "w", encoding="utf-8").write(json.dumps(_agreger()))
    r = _recette("--relire", p)
    assert r.returncode == 1, (r.returncode, r.stdout[-600:], r.stderr[-600:])
    assert u"PART FRANÇAISE GLOBALE : 78.8 %" in r.stdout, r.stdout
    r2 = _recette("--relire", p, "--seuil", "0.9")
    assert r2.returncode == 0, (r2.returncode, r2.stdout[-600:], r2.stderr[-600:])


@pytest.mark.parametrize("args", [["--seuil", "2"], ["--seuil", "abc"], ["--inconnue"]],
                         ids=["seuil-hors-bornes", "seuil-lettres", "option-inconnue"])
def test_une_option_mal_ecrite_est_une_erreur_de_recette_code_2(args, tmp_path):
    p = str(tmp_path / "m.json")
    io.open(p, "w", encoding="utf-8").write(json.dumps(_agreger()))
    r = _recette("--relire", p, *args)
    assert r.returncode == 2, (r.returncode, r.stderr[-300:])


# ══════════════════════════════════════════════════════════════════════════
#  4. LE POINT DE DÉPART COMMITÉ — MESURE_AVANT.json
# ══════════════════════════════════════════════════════════════════════════

def _pages_de_PAGE_META():
    src = _lire("sentinel.page.js")
    i = src.index("var PAGE_META = {")
    j = src.index("\n};", i)
    return re.findall(r"(?m)^\s*'?([A-Za-z0-9_-]+)'?\s*:\s*\{", src[i:j])


def test_PAGE_META_porte_bien_118_pages():
    assert len(_pages_de_PAGE_META()) == 118, len(_pages_de_PAGE_META())


def test_MESURE_AVANT_couvre_chaque_page_de_PAGE_META():
    """Une page absente de la mesure est une page que le lot de traduction
    n'aura pas à battre — donc qu'il pourra oublier."""
    assert os.path.isfile(MESURE_AVANT), "i18n/sentinel/MESURE_AVANT.json manque"
    m = json.load(io.open(MESURE_AVANT, encoding="utf-8"))
    attendues = set(_pages_de_PAGE_META())
    mesurees = set(m["pages"])
    assert attendues <= mesurees, "pages de PAGE_META absentes de la mesure : %s" % sorted(attendues - mesurees)
    assert m["global"]["pages"] == len(m["pages"]) == 118, m["global"]


def test_MESURE_AVANT_est_une_vraie_mesure_du_point_de_depart():
    """Dictionnaire reçu (sinon on mesure une panne, pas le produit), aucune
    page refusée par le limiteur, des mots partout, une part française qui
    dit bien « presque tout reste à faire »."""
    m = json.load(io.open(MESURE_AVANT, encoding="utf-8"))
    assert m["dictionnaire"]["charge"] is True, m["dictionnaire"]
    assert m.get("pages_429") == [], m.get("pages_429")
    vides = [k for k, p in m["pages"].items() if p["textes"] == 0]
    assert not vides, "pages sans aucun texte visible : %s" % vides
    assert m["global"]["part_fr"] > 0.5, m["global"]
    assert m["global"]["mots_fr"] > 10000, m["global"]
    assert m["coquille"]["textes"] > 50, m["coquille"]
