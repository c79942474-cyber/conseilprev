# -*- coding: utf-8 -*-
"""Les deux derniers modules reçoivent le questionnaire qui leur manquait.

LE DÉFAUT MESURÉ, ET IL NE SE VOYAIT NULLE PART. Les moteurs
`nist_ai_rmf.evaluer` et `owasp_llm.evaluer` existent depuis leur écriture,
leurs routes aussi — et RIEN ne les appelait. Les cinq pages de ces deux
modules ne portaient pas un seul champ de saisie : ni <select>, ni <input>,
aucune persistance. Elles affichaient le référentiel, point.

LA CONSÉQUENCE, SUR UN AUTRE ÉCRAN. `confDeclarations()` lisait
`window.CONF_DECL[norme]` pour six normes. Ce global était lu à un seul
endroit et ÉCRIT NULLE PART. (Le taux lit aujourd'hui la collecte du rail,
et ce global n'existe plus.) Deux cartes du taux de conformité ne pouvaient
donc afficher qu'un tiret, quoi que fasse le visiteur — et pas parce qu'il
n'avait rien rempli : parce qu'il n'y avait rien à remplir.

RIEN NE TOMBAIT, et c'est ce qui rend ce défaut coûteux. Une déclaration
vide est un état LÉGITIME : le moteur rend « — » plutôt qu'un zéro, à
dessein. L'écran vide et l'écran jamais branché rendent exactement la même
chose. Ces règles séparent les deux.
"""
import io
import json
import os
import re

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _lire(nom):
    with io.open(os.path.join(_RACINE, nom), encoding="utf-8") as f:
        return f.read()


PAGEJS = _lire("sentinel.page.js")
SENTINEL = _lire("sentinel.html")

#  LES DEUX MODULES, ET CE QUE CHACUN DOIT DEMANDER. Le nombre n'est PAS
#  écrit ici : il est dérivé de la référence Python, seule source. Figer
#  « 19 » interdirait au NIST d'ajouter une catégorie sans faire tomber une
#  règle qui n'a rien à dire là-dessus.
MODULES = {
    "nist": {"panneau": "p-nist-profil", "repondre": "nistRepondre",
             "stock": "cp-sentinel-nist-profil-v1", "norme": "nist_ai_rmf",
             "route": "/api/nist-ai-rmf/evaluer", "envoi": "etats"},
    "owasp": {"panneau": "p-owasp-dix", "repondre": "owaspRepondre",
              "stock": "cp-sentinel-owasp-declares-v1", "norme": "owasp_llm",
              "route": "/api/owasp-llm/evaluer", "envoi": "declares"},
}


def _attendus():
    """(questions, états) que chaque module doit offrir, lus dans la référence."""
    import nist_ai_rmf
    import owasp_llm
    return {
        "nist": (len(nist_ai_rmf.CATEGORIES), sorted(nist_ai_rmf.ETATS)),
        "owasp": (len(owasp_llm.RISQUES), sorted(owasp_llm.ETATS)),
    }


# ══════════════════════════════════════════════════════════════════════════
#  1. LE QUESTIONNAIRE EXISTE, ET IL COUVRE TOUTE LA RÉFÉRENCE
# ══════════════════════════════════════════════════════════════════════════

def test_la_lecture_des_deux_references_n_est_pas_vide():
    """LE GARDE-FOU DE TOUT CE FICHIER. Une référence qui rendrait zéro
    élément ferait passer les règles suivantes pour des comparaisons de
    vides — c'est arrivé une fois dans ce dépôt, et la recette est restée
    verte."""
    a = _attendus()
    assert a["nist"][0] >= 15, a["nist"]
    assert a["owasp"][0] == 10, a["owasp"]
    for m in a:
        assert len(a[m][1]) >= 3, (m, a[m][1])


def test_chaque_module_offre_TOUS_les_etats_de_sa_reference():
    """UN ÉTAT MANQUANT DANS LA LISTE DÉROULANTE est une réponse que le
    visiteur ne peut pas donner — et le moteur, lui, l'accepte. L'écart ne
    se voit pas : la question s'affiche, elle est simplement incomplète."""
    a = _attendus()
    for m, cfg in MODULES.items():
        ordre = re.search(r"var %s_ORDRE = \[([^\]]*)\]"
                          % ("NIST" if m == "nist" else "OWASP"), PAGEJS)
        assert ordre, "l'ordre des états de %s a disparu" % m
        offerts = sorted(re.findall(r"'([a-z_]+)'", ordre.group(1)))
        assert offerts == a[m][1], (
            "%s offre %s ; sa référence connaît %s — un état absent de la "
            "liste est une réponse qu'on ne peut pas donner"
            % (m, offerts, a[m][1]))


def test_chaque_question_est_un_CHAMP_et_pas_une_ligne_de_lecture():
    """CE QUI MANQUAIT LITTÉRALEMENT : zéro <select>, zéro <input>. La règle
    vérifie que la peinture fabrique bien un champ par élément de la
    référence, en passant par le même constructeur."""
    for m, cfg in MODULES.items():
        assert "_choix(R.etats," in PAGEJS, "le constructeur de champ a disparu"
        appel = re.search(
            r"_choix\(R\.etats, %s_ORDRE, [A-Z]+_DECL\[[^\]]+\],\s*'%s'"
            % ("NIST" if m == "nist" else "OWASP", cfg["repondre"]), PAGEJS)
        assert appel, (
            "le module %s ne construit plus de champ de réponse : sa page "
            "redevient une liste de lecture" % m)
    assert "<select class=\"q-sel\"" in PAGEJS, (
        "le champ n'est plus un <select> : un lecteur d'écran ne l'annonce "
        "plus comme un choix")


# ══════════════════════════════════════════════════════════════════════════
#  2. CE QUI EST RÉPONDU REMONTE — SINON LE QUESTIONNAIRE NE SERT À RIEN
# ══════════════════════════════════════════════════════════════════════════

def _code(src):
    """Le JavaScript sans ses commentaires : un nom cité dans l'historique
    d'un défaut n'est pas un nom que le code lit."""
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", "", src)


def test_le_taux_lit_ces_reponses_par_la_COLLECTE_DU_RAIL():
    """LE DÉFAUT CENTRAL, ET SA SUITE. `confDeclarations()` lisait
    `window.CONF_DECL[k]` ; rien ne l'écrivait, puis ces deux modules l'ont
    écrit — et quatre autres ne l'ont jamais fait. Le taux lit désormais la
    collecte du rail : ces deux questionnaires y partent tels quels, et plus
    aucun code ne lit l'ancien global."""
    code = _code(PAGEJS)
    assert "CONF_DECL" not in code, (
        "un global CONF_DECL est encore lu ou écrit : une seconde collecte "
        "pour les mêmes réponses, et le rail et le taux se contrediront")
    for cfg in MODULES.values():
        decl = "NIST_DECL" if cfg["norme"] == "nist_ai_rmf" else "OWASP_DECL"
        assert re.search(r"%s: function \(\) \{ return \{ etats: %s \}; \}"
                         % (cfg["norme"], decl), code), (
            "le rail ne collecte plus %s : ni lui ni le taux ne verront ces "
            "réponses" % cfg["norme"])
    assert "body: JSON.stringify({ecrans: ecrans})" in code, (
        "le taux n'envoie plus la collecte du rail")


def test_une_declaration_VIDE_reste_absente_et_ne_devient_pas_un_zero():
    """LA DOCTRINE DU MODULE, TENUE JUSQU'AU SERVEUR. Un questionnaire sans
    réponse doit rester ABSENT, pour que le taux rende « — ». Le traduire en
    déclaration vide le ferait passer pour mesuré à zéro, et un zéro se lit
    comme un constat."""
    import sys
    sys.path.insert(0, _RACINE)
    import conformite as c
    vides = {cfg["norme"]: {"etats": {}} for cfg in MODULES.values()}
    assert c.depuis_les_ecrans(vides) == {}, (
        "un questionnaire vide devient une déclaration")
    r = c.etat_des_lieux(c.depuis_les_ecrans(vides))
    for n in r["normes"]:
        if n["cle"] in vides:
            assert n["taux"] is None and not n["renseigne"], (
                "%s affiche %r sans une seule réponse" % (n["cle"], n["taux"]))


def test_les_reponses_survivent_a_la_fermeture_de_l_onglet():
    """UN QUESTIONNAIRE QU'ON DOIT REMPLIR À CHAQUE VISITE n'est pas un
    questionnaire : dix-neuf catégories ne se renseignent pas d'une traite."""
    for m, cfg in MODULES.items():
        assert "'%s'" % cfg["stock"] in PAGEJS, (
            "%s ne conserve plus les réponses" % m)
    assert "_declLire" in PAGEJS and "_declEcrire" in PAGEJS
    #  ET ELLES SONT LUES DÈS LE CHARGEMENT, pas à l'ouverture de leur écran :
    #  le rail et le taux les lisent par la même collecte, et le visiteur qui
    #  a répondu hier ne doit pas retrouver ses cartes « non renseignées ».
    for decl, cle in (("NIST_DECL", "NIST_CLE_STOCK"),
                      ("OWASP_DECL", "OWASP_CLE_STOCK")):
        assert "var %s = _declLire(%s);" % (decl, cle) in PAGEJS, (
            "%s n'est plus relu au chargement" % decl)
        i = PAGEJS.index("var %s = _declLire(%s);" % (decl, cle))
        assert PAGEJS.index("var %s = " % cle) < i, (
            "la clé %s est lue avant d'être définie : la lecture rend {}"
            % cle)


# ══════════════════════════════════════════════════════════════════════════
#  3. LE PARCOURS GUIDÉ MÈNE DU QUESTIONNAIRE AU TAUX
# ══════════════════════════════════════════════════════════════════════════

def _parcours(pid):
    i = PAGEJS.index("id: '%s'," % pid)
    return PAGEJS[i:PAGEJS.index("\n    ]\n  },", i)]


def test_les_deux_parcours_finissent_sur_le_TAUX_de_conformite():
    """UN PARCOURS QUI S'ARRÊTE AU MODULE laisse le visiteur avec un profil
    et sans réponse à « et alors ? ». La dernière étape le renvoie là où sa
    déclaration change quelque chose."""
    for pid in ("nist_ai_rmf", "owasp_llm"):
        etapes = re.findall(r"\{id:'([a-z0-9-]+)',", _parcours(pid))
        assert len(etapes) >= 4, (pid, etapes)
        assert etapes[-1] == "conf-taux", (
            "le parcours %s finit sur « %s » : le visiteur repart avec un "
            "profil et sans savoir ce qu'il en fait" % (pid, etapes[-1]))


def test_le_parcours_NE_PROMET_PAS_un_questionnaire_qui_n_existe_pas():
    """CE QUI ÉTAIT ÉCRIT AVANT QUE LE CHAMP EXISTE. Le parcours NIST disait
    déjà « Renseignez d'abord les six catégories de GOVERN » — une consigne
    adressée à une page en lecture seule. Le texte promettait une action que
    l'écran ne rendait pas possible.

    La règle lie les deux : un parcours dont une étape demande de
    RENSEIGNER ou de DÉCLARER doit viser une page qui porte un champ."""
    #  LA RÈGLE NE JUGE QUE LES CINQ PAGES DE CES DEUX MODULES. Les parcours
    #  passent aussi par ISO 42001 ou l'IA Act, qui ont leurs propres
    #  questionnaires depuis longtemps : les inclure ferait tomber la règle
    #  sur des pages dont elle ne sait rien, c'est-à-dire pour une raison
    #  sans rapport avec ce qu'elle prétend mesurer.
    PAGES = {"nist-profil", "nist-cadre", "nist-genai", "owasp-dix", "owasp-pont"}
    avec_champ = {"nist-profil", "owasp-dix"}
    vu = 0
    for pid in ("nist_ai_rmf", "owasp_llm"):
        bloc = _parcours(pid)
        for etape, action in re.findall(
                r"\{id:'([a-z0-9-]+)',[^}]*?action:\"((?:[^\"\\]|\\.)*)\"", bloc):
            if etape not in PAGES:
                continue
            vu += 1
            if not re.search(r"[Rr]enseign|[Dd]\\u00e9clar|[Dd]éclar", action):
                continue
            assert etape in avec_champ, (
                "l'étape « %s » du parcours %s demande de renseigner, mais "
                "cette page ne porte aucun champ" % (etape, pid))
    assert vu >= 5, (
        "%d étape(s) des cinq pages relevées : la lecture des parcours a "
        "changé de forme et cette règle ne prouve plus rien" % vu)
