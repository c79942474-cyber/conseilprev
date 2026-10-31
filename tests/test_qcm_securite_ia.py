# -*- coding: utf-8 -*-
"""LE QCM DE SÉCURITÉ DE L'IA — CE QUE LA BANQUE ET L'ÉCRAN DOIVENT TENIR.

CE QUI A ÉTÉ DEMANDÉ : dans le Hub Training de Sentinel, un hub de QCM en
sécurité de l'IA centré sur la banque, la finance et l'assurance, sur le
modèle du QCM fourni (scène, quatre options, indice, explication, motif de
chaque option fausse, gestes « en pratique », fiche des référentiels OWASP),
avec des médailles, une progression et quatre niveaux de difficulté.

CE QUE CES RÈGLES MESURENT, ET QUI NE SE DEVINE PAS À LA LECTURE :

  1. LA BONNE RÉPONSE NE SE TRAHIT PAS PAR SA LONGUEUR. Mesuré sur la première
     écriture de la banque : la bonne option était la PLUS LONGUE dans 49
     questions sur 50. Choisir la plus longue sans lire donnait 98 %. Après
     une première réécriture, elle était la plus COURTE dans 39 : le même
     défaut, retourné. La règle borne les deux stratégies, en français et en
     anglais.

  2. LES CODES D'UNE QUESTION SUIVENT LA TABLE DE CORRESPONDANCE. Mesuré :
     27 questions sur 50 surlignaient un triangle que la note de
     correspondance du cabinet dément (un ASI cité avec un code LLM ou T
     qu'elle ne lui relie pas).

  3. LE RANG SE LIT SUR LA MÉDAILLE LA PLUS BASSE, et l'écran — qui ne parle
     pas au serveur — calcule le même que le module, sur les 625 cas.

  4. RIEN NE REMONTE AU SERVEUR, et ce n'est pas qu'une phrase : la règle lit
     l'écran et n'y admet qu'un seul appel réseau, la lecture de la banque.

  5. AUCUN COMPTE N'EST ÉCRIT. Le nombre de questions est dérivé partout ; la
     règle refuse un compte écrit en chiffres ou en lettres dans les textes
     de l'écran.

  6. UN LIBELLÉ QUE L'INVENTAIRE NE RELÈVE PAS RESTE EN FRANÇAIS. « Or » ou
     « Expert », seuls, ne sont pas reconnus comme français par l'inventaire
     de traduction : ils seraient restés tels quels à l'écran anglais.

CE QUE CE FICHIER NE PEUT PAS MESURER, ET QUI LE MESURE :

  · L'ÉCRAN PEINT, LE CLAVIER, LA MÉDAILLE GAGNÉE, LA PROGRESSION GARDÉE, ET
    L'ÉCRAN ANGLAIS : `outils/recette_qcm_securite_ia.js` les éprouve dans un
    vrai navigateur, après une vraie connexion.
  · LA GARDE D'IMPORT : un module qui lève à l'import empêche la collecte de
    ce fichier — `tests/test_qcm_securite_ia_socle.py` l'éprouve sur une
    copie jetable.
"""
import io
import itertools
import json
import os
import re
import subprocess
import sys

import pytest

import qcm_securite_ia as M

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_RACINE, "outils"))
import i18n_sentinel as OUTIL  # noqa: E402
from sentinel_i18n import fusionner, normaliser  # noqa: E402


def _lire(nom):
    return io.open(os.path.join(_RACINE, nom), encoding="utf-8").read()


HTML = _lire("sentinel.html")
JS = _lire("sentinel.page.js")
APP = _lire("app.py")
REF = M.referentiel()

_CODES_ASI = set(e[0] for e in M.OWASP_ASI)
_CODES_LLM = set(e[0] for e in M.OWASP_LLM)
_CODES_T = set(e[0] for e in M.OWASP_AGENT)


def _bloc_qcm_js():
    i = JS.rfind("/*", 0, JS.index("QCM SÉCURITÉ DE L'IA — BANQUE, FINANCE, ASSURANCE"))
    j = JS.index("window.qcmSuite = qcmSuite;", i)
    return JS[i:j]


def _panneau():
    i = HTML.index('id="p-qcm-ia"')
    return HTML[i:HTML.index('<!-- MON ESPACE -->', i)]


def _fonction_js(nom):
    """Le source d'une fonction de l'écran, accolade comprise."""
    i = JS.index("function %s(" % nom)
    j, prof = JS.index("{", i), 0
    for k in range(j, len(JS)):
        prof += {"{": 1, "}": -1}.get(JS[k], 0)
        if prof == 0:
            return JS[i:k + 1]
    raise AssertionError("fonction %s non refermée" % nom)


def _node(script):
    r = subprocess.run(["node", "-e", script], capture_output=True, text=True,
                       timeout=60)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


# ══════════════════════════════════════════════════════════════════════════
#  LA BANQUE
# ══════════════════════════════════════════════════════════════════════════

def test_chaque_niveau_porte_les_SIX_domaines():
    """UN NIVEAU QUI NE POSE PAS UN DOMAINE rend, pour ce domaine, un profil à
    zéro que la personne lirait comme une faiblesse. Mesuré à l'écriture :
    les quatre niveaux portent chacun les six domaines."""
    for cle in M._CLES_NIVEAUX:
        vus = {q["domaine"] for q in M.QUESTIONS if q["niveau"] == cle}
        manquants = sorted(set(M._CLES_DOMAINES) - vus)
        assert not manquants, ("le niveau %s ne pose aucune question sur : %s"
                               % (cle, manquants))


def _rangs_de_longueur(questions, options_de):
    plus_longue = plus_courte = 0
    for q in questions:
        L = [len(o) for o in options_de(q)]
        bonne = L[q["a"]]
        plus_longue += bonne == max(L)
        plus_courte += bonne == min(L)
    return plus_longue, plus_courte


#: LE PLAFOND DES DEUX STRATÉGIES À L'AVEUGLE. Le hasard en donne un quart ;
#: 40 % laisse la place aux questions où la bonne réponse est naturellement
#: plus courte ou plus longue, et refuse ce qu'on a mesuré à l'écriture
#: (98 %, puis 78 %).
_PLAFOND_AVEUGLE = 0.40


def test_la_bonne_reponse_ne_se_TRAHIT_PAS_par_sa_longueur_en_francais():
    n = len(M.QUESTIONS)
    longue, courte = _rangs_de_longueur(M.QUESTIONS, lambda q: q["o"])
    assert longue <= _PLAFOND_AVEUGLE * n, (
        "« choisir la plus longue » réussit %d questions sur %d" % (longue, n))
    assert courte <= _PLAFOND_AVEUGLE * n, (
        "« choisir la plus courte » réussit %d questions sur %d" % (courte, n))


def test_la_bonne_reponse_ne_se_TRAHIT_PAS_par_sa_longueur_en_anglais():
    """LA MÊME MESURE SUR L'ÉCRAN ANGLAIS : une traduction qui condense la
    bonne réponse et développe les autres recrée le biais sans toucher au
    français."""
    dico, _f = fusionner()
    manquantes = []

    def anglais(q):
        out = []
        for o in q["o"]:
            v = dico["texte"].get(normaliser(o))
            if v is None:
                manquantes.append(o)
                v = o
            out.append(v)
        return out
    n = len(M.QUESTIONS)
    longue, courte = _rangs_de_longueur(M.QUESTIONS, anglais)
    assert not manquantes, "options sans anglais : %s" % manquantes[:3]
    assert longue <= _PLAFOND_AVEUGLE * n, (
        "en anglais, « la plus longue » réussit %d sur %d" % (longue, n))
    assert courte <= _PLAFOND_AVEUGLE * n, (
        "en anglais, « la plus courte » réussit %d sur %d" % (courte, n))


def test_les_codes_d_une_question_suivent_la_TABLE_DE_CORRESPONDANCE():
    """QUAND UN RISQUE AGENTIQUE EST CITÉ, ses compagnons LLM et T sont ceux
    que la table lui relie. La fiche de l'écran surligne les trois colonnes :
    un code que la table ne relie pas à l'ASI surligné dessinerait une
    correspondance que la note du cabinet dément."""
    fautes = []
    for q in M.QUESTIONS:
        asi = [c for c in q["codes"] if c in _CODES_ASI]
        if not asi:
            continue
        llm = set().union(*[M.OWASP_MAP[a]["llm"] for a in asi])
        t = set().union(*[M.OWASP_MAP[a]["t"] for a in asi])
        hors = [c for c in q["codes"]
                if (c in _CODES_LLM and c not in llm) or (c in _CODES_T and c not in t)]
        if hors:
            fautes.append((q["n"], asi, hors))
    assert not fautes, ("questions dont les codes contredisent la table : %s"
                        % fautes)


def test_la_citation_affichee_est_DERIVEE_et_nomme_son_code():
    """LA CITATION N'EST ÉCRITE QU'UNE FOIS — par le code, ou, à défaut de
    tout code OWASP, par une citation externe. Une question qui porterait
    les deux offrirait deux vérités."""
    for q, servie in zip(M.QUESTIONS, REF["questions"]):
        if q["codes"]:
            assert "ref" not in q, q["n"]
            assert servie["ref"] == M.citation(q["codes"][0]), q["n"]
            assert q["codes"][0] in servie["ref"], q["n"]
        else:
            assert servie["ref"] == q["ref"] and q["ref"].strip(), q["n"]


def test_la_banque_SERVIE_est_la_banque_ENTIERE_et_ses_totaux_sont_DERIVES():
    assert len(REF["questions"]) == len(M.QUESTIONS)
    assert [q["n"] for q in REF["questions"]] == list(range(1, len(M.QUESTIONS) + 1))
    assert sum(REF["par_niveau"].values()) == len(M.QUESTIONS)
    assert sum(REF["par_domaine"].values()) == len(M.QUESTIONS)
    for cle in M._CLES_NIVEAUX:
        assert REF["par_niveau"][cle] == sum(1 for q in M.QUESTIONS if q["niveau"] == cle)
    for q in REF["questions"]:
        assert 0 <= q["a"] < len(q["o"]) == REF["options_par_question"]
        assert len(q["faux"]) == len(q["o"]) - 1


# ══════════════════════════════════════════════════════════════════════════
#  LES MÉDAILLES ET LE RANG
# ══════════════════════════════════════════════════════════════════════════

def test_le_SANS_FAUTE_et_lui_seul_donne_la_medaille_la_plus_haute():
    haut = M.MEDAILLES[0][0]
    for n in set(REF["par_niveau"].values()):
        assert M.medaille(1.0)["cle"] == haut
        assert M.medaille((n - 1) / float(n))["cle"] != haut, (
            "une question manquée sur %d donne encore « %s »" % (n, haut))


def test_le_palier_le_plus_bas_demande_DEJA_la_majorite():
    """LE GUIDE L'ÉCRIT — « le palier le plus bas demande déjà la majorité
    des réponses » — et c'est ce qui sépare une médaille d'une médaille de
    participation."""
    assert M.MEDAILLES[-1][3] > 0.5
    assert M.medaille(0.5) is None


def _rang_attendu(meds):
    ordre = [m[0] for m in M.MEDAILLES]
    if any(meds.get(c) not in ordre for c in M._CLES_NIVEAUX):
        return None
    return max((meds[c] for c in M._CLES_NIVEAUX), key=ordre.index)


_ETATS = [None] + [m[0] for m in M.MEDAILLES]
_COMBINAISONS = list(itertools.product(_ETATS, repeat=len(M._CLES_NIVEAUX)))


def test_le_rang_se_lit_sur_la_medaille_la_plus_BASSE_jamais_sur_la_moyenne():
    for combo in _COMBINAISONS:
        meds = dict((c, m) for c, m in zip(M._CLES_NIVEAUX, combo) if m)
        r = M.rang(meds)
        attendu = _rang_attendu(meds)
        if attendu is None:
            assert r["ouvert"] is False, combo
        else:
            assert r["ouvert"] and r["medaille"] == attendu, (combo, r)


def test_l_ECRAN_calcule_le_meme_rang_que_le_module_sur_les_625_cas():
    """L'ÉCRAN NE PARLE PAS AU SERVEUR : il reproduit la règle du rang. Deux
    arithmétiques du même chiffre divergent au premier changement — la règle
    exécute celle de l'écran et la confronte au module, cas par cas."""
    src = _fonction_js("_qcmRang")
    ref = {"niveaux": REF["niveaux"], "medailles": REF["medailles"], "rangs": REF["rangs"]}
    cas = [dict((c, {"medaille": m}) for c, m in zip(M._CLES_NIVEAUX, combo) if m)
           for combo in _COMBINAISONS]
    sortie = _node("var QCM_REF=%s;%s;console.log(JSON.stringify(%s.map(function(n){"
                   "var r=_qcmRang({niveaux:n});return r.ouvert?r.medaille.cle:null;})));"
                   % (json.dumps(ref), src, json.dumps(cas)))
    for combo, ecran in zip(_COMBINAISONS, sortie):
        meds = dict((c, m) for c, m in zip(M._CLES_NIVEAUX, combo) if m)
        assert ecran == _rang_attendu(meds), (combo, ecran)


def test_l_ECRAN_attribue_la_meme_medaille_que_le_module_a_chaque_score():
    src = _fonction_js("_qcmMedaille")
    cas = [(k, n) for n in sorted(set(REF["par_niveau"].values())) for k in range(n + 1)]
    sortie = _node("var QCM_REF=%s;%s;console.log(JSON.stringify(%s.map(function(c){"
                   "var m=_qcmMedaille(c[0]/c[1]);return m?m.cle:null;})));"
                   % (json.dumps({"medailles": REF["medailles"]}), src, json.dumps(cas)))
    for (k, n), ecran in zip(cas, sortie):
        m = M.medaille(k / float(n))
        assert ecran == (m["cle"] if m else None), (k, n, ecran)


# ══════════════════════════════════════════════════════════════════════════
#  RIEN NE REMONTE, RIEN N'EST ÉCRIT EN DUR
# ══════════════════════════════════════════════════════════════════════════

def test_l_ecran_n_envoie_RIEN_au_serveur():
    """LA RÉSERVE DE L'ÉCRAN LE PROMET : « rien de ce que vous répondez ne
    quitte votre navigateur ». Un seul appel réseau est admis — la lecture
    de la banque — et aucun moyen d'émettre."""
    bloc = _bloc_qcm_js()
    appels = re.findall(r"fetch\(\s*'([^']+)'", bloc)
    assert appels == ["/api/qcm-securite-ia/referentiel"], appels
    for interdit in ("method:", "sendBeacon", "XMLHttpRequest", "navigator.sendBeacon",
                     "new Image(", "WebSocket"):
        assert interdit not in bloc, "l'écran du QCM peut émettre : %s" % interdit
    #  ET LE SERVEUR N'A RIEN POUR RECEVOIR.
    routes = re.findall(r"@app\.route\('(/api/qcm[^']*)'", APP)
    assert routes == ["/api/qcm-securite-ia/referentiel"], routes
    decl = "@app.route('/api/qcm-securite-ia/referentiel', methods=['GET'])"
    assert decl in APP
    assert "@rate_limit(limit=120, window=60)" in APP[APP.index(decl):APP.index(decl) + 200]


_NOMBRES_EN_LETTRES = ("cinquante", "quarante-neuf", "treize", "douze", "onze")


def test_aucun_COMPTE_de_questions_n_est_ECRIT_dans_les_textes():
    """LE NOMBRE DE QUESTIONS EST DÉRIVÉ PARTOUT. Un « cinquante questions »
    écrit dans une phrase mentira le jour où une question sera ajoutée, et
    aucune règle d'inventaire ne le verra : la phrase restera traduite."""
    textes = {
        "le panneau": _panneau(),
        "l'entrée de barre": HTML[HTML.index("go('qcm-ia'") - 300:HTML.index("go('qcm-ia'") + 900],
        "le moteur d'écran": _bloc_qcm_js(),
        "le guide": JS[JS.index("  'qcm-ia': {\n    title:"):JS.index("  espace: {\n    title:")],
        "l'étape de parcours": JS[JS.index("{id:'qcm-ia'"):JS.index("{id:'training'", JS.index("{id:'qcm-ia'"))],
    }
    total = len(M.QUESTIONS)
    for ou, t in textes.items():
        bas = t.lower()
        for mot in _NOMBRES_EN_LETTRES:
            assert mot not in bas, "%s écrit un compte en lettres : « %s »" % (ou, mot)
        assert not re.search(r"\b%d\s+questions\b" % total, t), (
            "%s écrit le compte de la banque en chiffres" % ou)
    #  ET LES SEUILS DE MÉDAILLE NE SONT PAS RECOPIÉS DANS L'ÉCRAN.
    bloc = _bloc_qcm_js()
    for _c, _d, _q, seuil in M.MEDAILLES:
        for forme in ("%g" % seuil, "%d" % round(100 * seuil)):
            if forme in ("1", "100"):
                continue
            assert not re.search(r"(?<![\w.])%s(?![\w.])" % re.escape(forme), bloc), (
                "le seuil %s est recopié dans l'écran" % forme)


def test_les_touches_du_clavier_suivent_le_nombre_d_OPTIONS():
    m = re.search(r"var QCM_TOUCHES = \[([^\]]*)\];", JS)
    touches = re.findall(r"'([A-Z])'", m.group(1))
    assert len(touches) == M.OPTIONS_PAR_QUESTION, touches


def test_QUATRE_niveaux_parce_que_les_textes_disent_quatre():
    """« QUATRE NIVEAUX » EST ÉCRIT dans le chapô, le guide et le moteur de
    rang. Le nombre de niveaux est structurel, et c'est cette règle qui lie
    le texte à la table."""
    assert len(M.NIVEAUX) == 4
    assert "Quatre niveaux" in _panneau()
    teintes = re.search(r"var QCM_TEINTES = \{([^}]*)\}", JS).group(1)
    assert set(re.findall(r"(\w+):\s*'#", teintes)) == set(M._CLES_NIVEAUX)


# ══════════════════════════════════════════════════════════════════════════
#  LA TRADUCTION
# ══════════════════════════════════════════════════════════════════════════

def test_chaque_LIBELLE_de_niveau_de_medaille_de_rang_et_de_domaine_est_RELEVE():
    """L'INVENTAIRE NE RELÈVE QUE CE QU'IL RECONNAÎT COMME FRANÇAIS — deux
    mots, et un accent ou un mot-outil. « Or », « Argent », « Expert » seuls
    ne le sont pas : ils seraient restés en français à l'écran anglais, et
    « Or » s'y lit comme une conjonction."""
    libelles = ([n[1] for n in M.NIVEAUX] + [m[1] for m in M.MEDAILLES]
                + [m[2] for m in M.MEDAILLES] + [r[1] for r in M.RANGS]
                + [d[1] for d in M.DOMAINES] + [M.SANS_MEDAILLE])
    muets = [x for x in libelles if not OUTIL.est_francais(x)]
    assert not muets, "libellés que l'inventaire ne relèvera jamais : %s" % muets


def test_tout_le_FRANCAIS_que_la_route_sert_est_TRADUIT():
    dico, _f = fusionner()
    manquants = []
    for s in OUTIL.chaines_d_une_charge(REF):
        #  LE MÊME FILTRE QUE L'INVENTAIRE : une clé JSON (« quoi_faire ») est
        #  un identifiant, pas du texte lu.
        if (OUTIL.est_francais(s) and not OUTIL.est_identifiant(s)
                and normaliser(s) not in dico["texte"]):
            manquants.append(s)
    assert not manquants, ("%d chaîne(s) servie(s) sans anglais, dont : %s"
                           % (len(manquants), manquants[:3]))


def test_tout_le_FRANCAIS_que_l_ecran_compose_est_TRADUIT():
    """LES LITTÉRAUX SONT LUS COMME L'INVENTAIRE LES LIT, balisage compris.
    La première version de cette règle sautait tout littéral contenant un
    « < » — c'est-à-dire la plupart des libellés de l'écran, écrits dans
    leur balise. La batterie de mutations l'a montré : un libellé de bouton
    changé sans traduction passait."""
    dico, _f = fusionner()
    manquants = []
    for lit in OUTIL.litteraux_js(_bloc_qcm_js()):
        if '<' in lit and '>' in lit and OUTIL._BALISE.search(lit):
            candidats = OUTIL.entrees_d_un_html(lit)
        else:
            candidats = [('texte', lit, None)]
        for regime, fr, _html in candidats:
            fr = OUTIL.aplanir(fr)
            if not OUTIL.est_francais(fr) or OUTIL.est_identifiant(fr):
                continue
            if normaliser(fr) not in dico.get(regime, {}):
                manquants.append((regime, fr))
    assert not manquants, "littéraux de l'écran sans anglais : %s" % manquants[:5]
    for c in ("nav.item.qcm-ia", "pg.qcm-ia.eb", "pg.qcm-ia.h1", "pg.qcm-ia.p",
              "pg.qcm-ia.attente"):
        assert "'%s':" % c in JS, "la clé « %s » n'a pas d'anglais" % c


def test_un_element_qui_porte_data_i18n_n_est_JAMAIS_repeint():
    """LE DÉFAUT EST ARRIVÉ DEUX FOIS, et la seconde l'a révélé. Un élément
    qui porte `data-i18n` est EXCLU de la traduction par contenu, lui et tout
    ce qu'il contient, et la bascule de langue réécrit son `textContent`.
    L'écran du référentiel de compétences peignait sa proposition DANS un tel
    élément : à l'écran anglais elle restait en français, et le clic sur EN
    la remplaçait par « Loading the framework… ». Le QCM a d'abord reproduit
    le même geste. La règle relève les éléments `data-i18n` qui portent un
    identifiant et refuse que le JavaScript y écrive."""
    ids = set(re.findall(r'<[a-z0-9]+[^>]*\bid="([^"]+)"[^>]*\bdata-i18n(?:-bloc)?="', HTML))
    ids |= set(re.findall(r'<[a-z0-9]+[^>]*\bdata-i18n(?:-bloc)?="[^"]+"[^>]*\bid="([^"]+)"', HTML))
    peints = []
    for i in sorted(ids):
        e = re.escape(i)
        if re.search(r"getElementById\(\s*'%s'\s*\)[^;\n]*\.(innerHTML|textContent)\s*=" % e, JS):
            peints.append(i)
            continue
        for v in re.findall(r"var (\w+) = document\.getElementById\('%s'\)" % e, JS):
            if re.search(r"\b%s\.(innerHTML|textContent)\s*=" % re.escape(v), JS):
                peints.append(i)
                break
    assert not peints, "éléments data-i18n que le JavaScript repeint : %s" % peints
    #  ET LES DEUX CONTENEURS QUI L'ONT ÉTÉ GARDENT LEUR ATTENTE EN ENFANT.
    for conteneur in ("comp-sortie", "qcm-hub"):
        assert '<div id="%s"><div class="veille-loading" data-i18n=' % conteneur in HTML


# ══════════════════════════════════════════════════════════════════════════
#  L'ÉCRAN DANS SENTINEL
# ══════════════════════════════════════════════════════════════════════════

def test_la_barre_mene_a_l_ecran_et_l_AMORCE_est_dans_son_appel():
    items = re.findall(r'class="sb-item[^"]*"[^>]*onclick="([^"]+)"', HTML)
    notre = [o for o in items if "go('qcm-ia'" in o]
    assert len(notre) == 1, "l'écran a %d entrée(s) de barre" % len(notre)
    assert "qcmInit()" in notre[0], "l'onglet n'amorce rien : écran vide"
    i = HTML.index("go('qcm-ia'")
    assert 'data-grp="equipe-et-formation"' in HTML[i - 300:i]
    assert HTML.index("go('training'") < HTML.index("go('competences'") < i
    assert "window.qcmInit = qcmInit;" in JS


def test_l_ecran_a_sa_fiche_son_guide_et_une_etape_de_parcours():
    assert re.search(r"'qcm-ia':\s*\{section:'ÉQUIPE & FORMATION'", JS)
    assert "  'qcm-ia': {\n    title:" in JS
    i = JS.index("{id:'qcm-ia'")
    etape = JS[i:JS.index("{id:'training'", i)]
    assert "action:" in etape and "gain:" in etape and "tip:" in etape


def test_les_trois_scenes_existent_et_le_hub_s_ouvre_sur_ses_quatre_niveaux():
    p = _panneau()
    for scene in ("qcm-hub", "qcm-jeu", "qcm-bilan"):
        assert 'id="%s"' % scene in p, scene
    assert 'id="qcm-jeu" hidden' in p and 'id="qcm-bilan" hidden' in p
    hub = _fonction_js("qcmHub")
    assert "QCM_REF.niveaux.map" in hub and "QCM_REF.domaines.map" in hub
    assert "QCM_REF.medailles.map" in hub and "QCM_REF.reserves.map" in hub


def test_la_correction_dit_POURQUOI_chaque_option_fausse_l_est():
    """L'ORDRE DES MOTIFS EST CELUI DE L'ÉCRITURE, PAS CELUI DE L'ÉCRAN, qui
    mélange les options. La règle rejoue l'appariement de l'écran : les
    options fausses, dans l'ordre d'écriture, reçoivent `faux` dans l'ordre."""
    src = _fonction_js("_qcmCorriger")
    assert "if (k === q.a) return;" in src and "q.faux[j++]" in src
    for q in M.QUESTIONS:
        fausses = [o for k, o in enumerate(q["o"]) if k != q["a"]]
        assert len(fausses) == len(q["faux"]), q["n"]


# ══════════════════════════════════════════════════════════════════════════
#  LES CORRESPONDANCES OWASP, À L'ÉCRAN
# ══════════════════════════════════════════════════════════════════════════
#
#  LE DÉFAUT CONSTATÉ : la route servait `correspondance` et l'écran ne la
#  lisait nulle part — la table de la note du cabinet restait invisible dans
#  le QCM. Ces règles tiennent la vue du hub à la table du module.

def _relations_ecran():
    """Les relations que l'ÉCRAN calcule, pour chaque code, à partir de la
    banque servie — exécutées dans node, pas relues. Seules les deux clés
    que ces fonctions lisent sont passées : la banque entière dépasserait
    la longueur d'argument que Linux accepte."""
    src = "\n".join(_fonction_js(n) for n in
                    ("_qcmCorrIndex", "_qcmCorrAsi", "_qcmCorrRelations"))
    script = ("var QCM_REF = %s;\nvar QCM_CORR = {idx: null, ordre: null};\n"
              "var QCM_CORR_FW = {llm: 'llm', asi: 'asi', agent: 't'};\n%s\n"
              "var o = {}; Object.keys(_qcmCorrIndex()).forEach(function (c) {"
              " o[c] = _qcmCorrRelations(c); });\n"
              "process.stdout.write(JSON.stringify(o));"
              % (json.dumps({"referentiels": REF["referentiels"],
                             "correspondance": REF["correspondance"]}), src))
    return _node(script)


def _attendu(code):
    m = M.OWASP_MAP
    if code in m:
        return sorted(m[code]["llm"] + m[code]["t"]), []
    cle = "llm" if code in _CODES_LLM else "t"
    autre = "t" if cle == "llm" else "llm"
    asis = sorted(a for a in m if code in m[a][cle])
    ind = set()
    for a in asis:
        ind |= set(m[a][autre])
    return asis, sorted(ind)


def test_le_HUB_peint_la_correspondance_que_la_route_sert():
    hub = _fonction_js("qcmHub")
    assert "_qcmCorrBloc()" in hub and "_qcmCorrBrancher(h)" in hub, (
        "la vue des correspondances n'est plus dans le hub")
    bloc = _fonction_js("_qcmCorrBloc")
    assert "QCM_REF.correspondance" in bloc and "QCM_REF.referentiels" in bloc
    assert "correspondance" in REF and set(REF["correspondance"]) == set(M.OWASP_MAP)


def test_l_ECRAN_relie_chaque_code_comme_la_TABLE_du_module():
    """Pour CHACUN des codes : liens directs et indirects calculés par
    l'écran = ceux que la table OWASP_MAP implique. Un risque agentique
    relie ses risques LLM et ses menaces ; un risque LLM ou une menace
    passe par les risques agentiques qui le citent."""
    rel = _relations_ecran()
    assert set(rel) == _CODES_LLM | _CODES_ASI | _CODES_T
    faux = []
    for code, r in sorted(rel.items()):
        d, i = _attendu(code)
        if sorted(r["direct"]) != d or sorted(r["indirect"]) != i:
            faux.append((code, r, d, i))
    assert not faux, "l'écran ne suit pas la table : %s" % faux[:2]


def test_les_questions_d_un_code_sont_DERIVEES_de_la_banque():
    """La fiche liste les questions qui citent le code, filtrées sur leurs
    codes — jamais une liste écrite à part, qui mentirait à la première
    question ajoutée."""
    fiche = _fonction_js("_qcmCorrFiche")
    assert ("QCM_REF.questions.filter(function (q) { return q.codes.indexOf(code) >= 0; })"
            in fiche)


def test_la_correction_marque_les_codes_LIES_par_la_table():
    ow = _fonction_js("_qcmOwasp")
    assert "_qcmCorrRelations(c)" in ow and "LIÉ PAR LA CORRESPONDANCE" in ow
