# -*- coding: utf-8 -*-
"""Les six listes qui se validaient sur un clic se MESURENT.

LA DEMANDE : six blocs du rail passaient au vert sur une simple déclaration
— « J'ai passé cette liste en revue » : l'audit IA Act, l'AIPD, la privacy
by design, la politique documentaire, la sensibilisation et l'analyse de
risque ReCyF (objectif 16). Chacun doit demander une réponse explicite par
question, et se mesurer comme les autres blocs.

CE QUI A ÉTÉ MESURÉ DANS UN NAVIGATEUR, AVANT D'ÉCRIRE UNE LIGNE
(recette_revues_mesurees.js, sur le code d'alors : 46 contrôles en échec
sur 49) :
  · aucune des six listes n'avait de valeur « non renseigné » : des cases
    décochées, « absent », « à planifier », une gravité et une
    vraisemblance de 1 — chaque défaut était aussi une réponse ;
  · la déclaration « passé en revue » validait chacun des six blocs sans
    qu'une seule question ait reçu de réponse ; et sans elle, aucune
    réponse ne les validait ;
  · « sans objet » n'existait nulle part : un contrôle qui ne s'applique
    pas comptait comme un contrôle manqué ;
  · l'AIPD PRÉSUMAIT le critère des données sensibles pour le traitement
    livré avec chaque compte, dont le registre répond « Non (hors art. 9) ».

LE CODE EST EXÉCUTÉ, PAS LU. Les règles de l'écran évaluent sous node les
VRAIES tranches de sentinel.page.js — l'audit, le RGPD, puis la queue qui
porte ReCyF, le rail et la mémoire — dans le harnais de
tests/test_memoire_ecrans.py : même faux DOM, même stockage qui survit au
rechargement. Les réponses passent par les vrais gestionnaires des champs,
et ce que l'écran affiche est relu dans le HTML qu'il écrit.
"""
import json
import os
import re
import sys

import pytest

_ICI = os.path.dirname(os.path.abspath(__file__))
_RACINE = os.path.dirname(_ICI)
sys.path.insert(0, _RACINE)
sys.path.insert(0, _ICI)

import conformite  # noqa: E402
import nis2_recyf  # noqa: E402
import parcours_normes as pn  # noqa: E402
import test_memoire_ecrans as _tm  # noqa: E402

PAGE = open(os.path.join(_RACINE, "sentinel.page.js"), encoding="utf-8").read()

#: LES SIX BLOCS, par référentiel, et l'écran de chacun.
SIX = {("ia_act", "audit"): "audit-ia-act",
       ("rgpd", "aipd"): "rgpd-aipd",
       ("rgpd", "pbd"): "rgpd-pbd",
       ("rgpd", "doc"): "rgpd-doc",
       ("rgpd", "sensibilisation"): "rgpd-sensibilisation",
       ("nis2", "recyf_analyse"): "recyf-analyse"}


# ══════════════════════════════════════════════════════════════════════════
#  LE HARNAIS : celui de la mémoire des écrans, avec deux tranches de plus
# ══════════════════════════════════════════════════════════════════════════

_BORNES = r"""
function _borne(debut, fin) {
  const i = src.indexOf(debut);
  if (i < 0) throw new Error('borne introuvable : ' + debut);
  const j = src.indexOf(fin, i);
  if (j < 0) throw new Error('borne introuvable : ' + fin);
  return src.slice(i, j);
}
/* L'AUDIT IA ACT, puis le RGPD — du registre aux quatre briques. Ils se
   chargent AVANT la queue, dans l'ordre de la page. */
const AUDIT_TRANCHE = _borne('/* ══ ONGLET 2 : AUDIT IA ACT ══ */', '/* ══ ONGLET 3 : ARTICLES ══ */');
const RGPD_TRANCHE = _borne('/* ══ Registre des traitements (RGPD art. 30) ══ */',
                            'window.confRender = function(){');
"""


def _socle():
    s = _tm._SOCLE
    a = "const TRANCHE = src.slice(d0);"
    b = "(0, eval)(TRANCHE);"
    # UN HARNAIS QUI NE SE GREFFE PLUS NE DOIT PAS TOURNER EN SILENCE : les
    # règles mesureraient la seule queue du fichier.
    assert s.count(a) == 1 and s.count(b) == 1, "le harnais de la mémoire a changé de forme"
    return (s.replace(a, a + _BORNES)
             .replace(b, "(0, eval)(AUDIT_TRANCHE + '\\n' + RGPD_TRANCHE + '\\n' + TRANCHE);"))


_SOCLE = _socle()


def _executer(scenario):
    ancien = _tm._SOCLE
    _tm._SOCLE = _SOCLE
    try:
        return _tm._executer(scenario)
    finally:
        _tm._SOCLE = ancien


#: Le traitement livré avec chaque compte, tel que le registre le sert.
TRAITEMENT = {"id": 1, "nom": "Gestion des ressources humaines",
              "finalites": "Gestion administrative du personnel (paie)",
              "base_legale": "Obligation légale", "categories_personnes": "Salariés",
              "categories_donnees": "Identité, paie",
              "donnees_sensibles": "Non (hors art. 9)",
              "duree_conservation": "Contrat + 5 ans",
              "mesures_securite": "Chiffrement, habilitations", "service": "RH"}


def _rail_ref():
    return json.dumps(pn.referentiel())


# ══════════════════════════════════════════════════════════════════════════
#  1. LE MOTEUR : une question sans réponse est nommée, jamais devinée
# ══════════════════════════════════════════════════════════════════════════

def test_les_SIX_blocs_se_remplissent_et_ne_se_declarent_plus():
    for (norme, cle), panneau in SIX.items():
        b = [x for x in pn.BLOCS[norme] if x["cle"] == cle][0]
        assert b["panneau"] == panneau, (norme, cle, b["panneau"])
        assert b["nature"] == "saisie", "%s/%s est encore « %s »" % (norme, cle, b["nature"])


def test_l_ancienne_declaration_ne_valide_AUCUN_des_six():
    """UNE MÉMOIRE DE NAVIGATEUR GARDE LES ANCIENNES MARQUES « passé en
    revue » : elles ne doivent plus rien valider — ni comme revue, ni
    déguisées en « lu »."""
    for (norme, cle), panneau in SIX.items():
        d = {"revus": [panneau], "lus": [panneau]}
        b = [l for l in pn.avancement(norme, d)["blocs"] if l["cle"] == cle][0]
        assert b["etat"] != "validee", "%s/%s passe au vert sur un clic" % (norme, cle)


def test_AUDIT_un_point_sans_reponse_est_NOMME():
    points = [{"cle": "a5_1", "titre": "Inventaire"}, {"cle": "a5_2", "titre": "Biométrie"},
              {"cle": "a5_3", "titre": "Émotions"}]
    m, _so, _ctx = pn._ia_act({"points": points,
                               "audit": {"a5_1": "todo", "a5_3": "none"}})
    # « À RÉALISER » EST UNE RÉPONSE ; « none », l'état d'un point jamais
    # touché dans l'ancien écran, n'en est pas une.
    assert [q["quoi"] for q in m["audit"]] == ["Biométrie", "Émotions"], m["audit"]
    m, _so, _ctx = pn._ia_act({"points": points, "audit": {
        "a5_1": "done", "a5_2": "partial", "a5_3": "na"}})
    assert m["audit"] == [], m["audit"]


def test_AUDIT_sans_la_liste_des_points_le_bloc_le_DIT():
    """UNE LISTE ABSENTE N'EST PAS UNE LISTE COMPLÈTE."""
    m, _so, _ctx = pn._ia_act({"audit": {"a5_1": "done"}})
    assert len(m["audit"]) == 1 and "pas été transmise" in m["audit"][0]["quoi"], m


def test_AIPD_un_critere_sans_reponse_n_est_pas_un_NON():
    crit = [{"nom": "C%d" % i, "reponse": False} for i in range(9)]
    crit[4]["reponse"] = None
    m = pn._manque_aipd([{"nom": "Paie", "aipd": {"criteres": crit, "evenements": []}}])
    assert [q["quoi"] for q in m] == ["« Paie » : C4"], m


def test_AIPD_les_cotations_ne_sont_demandees_qu_au_SEUIL():
    """LES ÉVÉNEMENTS NE SONT DEMANDÉS QU'À QUI DOIT UNE AIPD : les exiger de
    tous ferait coter des risques qu'aucune analyse n'a à apprécier."""
    assert pn.AIPD_SEUIL == 2
    evs = [{"nom": "Accès", "g": None, "v": None}, {"nom": "Modification", "g": 2, "v": 5},
           {"nom": "Disparition", "g": "3", "v": 3}]

    def _m(oui):
        crit = [{"nom": "C%d" % i, "reponse": i < oui} for i in range(9)]
        return [q["quoi"] for q in pn._manque_aipd(
            [{"nom": "Paie", "aipd": {"criteres": crit, "evenements": evs}}])]
    assert _m(1) == [], "des cotations sont exigées avant le seuil"
    # UNE VRAISEMBLANCE DE 5, UNE GRAVITÉ ÉCRITE EN TEXTE : pas des réponses.
    assert _m(2) == ["« Paie » : gravité et vraisemblance — Accès",
                     "« Paie » : gravité et vraisemblance — Modification",
                     "« Paie » : gravité et vraisemblance — Disparition"], _m(2)


def test_RECYF_chaque_OUI_engage_ce_que_le_referentiel_exige_avec_lui():
    tout_non = {"gouvernance": False, "couverture": False, "acceptation": False,
                "reexamen": False}
    assert pn._manque_analyse_recyf(tout_non) == []
    assert len(pn._manque_analyse_recyf({})) == 4
    a = dict(tout_non, gouvernance=True)
    assert ["16.1 — des moyens sont-ils alloués ?"] == [
        q["quoi"] for q in pn._manque_analyse_recyf(a)]
    a = dict(tout_non, couverture=True, entrees={"pssi": True, "si": False})
    manque = [q["quoi"] for q in pn._manque_analyse_recyf(a)]
    assert len(manque) == len(nis2_recyf.ANALYSE_ENTREES) - 2, manque
    a = dict(tout_non, acceptation=True, risques_residuels_acceptes=False)
    assert len(pn._manque_analyse_recyf(a)) == 1
    a = dict(tout_non, reexamen=True)
    assert ["16.4 — le dernier réexamen, en mois"] == [
        q["quoi"] for q in pn._manque_analyse_recyf(a)]


def test_RECYF_une_entree_NON_n_est_pas_une_entree_CITEE():
    """LE PIÈGE QUE LA CARTE OUVRAIT. Les entrées partent désormais en carte
    — {entrée : oui ou non}. Lue comme une liste, une carte rend ses CLÉS :
    chaque « non » aurait compté pour une entrée citée."""
    d = {"couverture": True, "entrees": {c: (i == 0) for i, (c, _n)
                                         in enumerate(nis2_recyf.ANALYSE_ENTREES)}}
    r = nis2_recyf.analyse_de_risque(d, "essentielle")
    couv = [e for e in r["exigences"] if e["cle"] == "couverture"][0]
    assert not couv["acquis"], couv
    assert couv["manque"] and all(n in couv["manque"][0] for _c, n
                                  in nis2_recyf.ANALYSE_ENTREES[1:]), couv["manque"]
    # UNE LISTE, la forme d'avant, se lit toujours.
    d["entrees"] = [c for c, _n in nis2_recyf.ANALYSE_ENTREES]
    r = nis2_recyf.analyse_de_risque(d, "essentielle")
    assert [e for e in r["exigences"] if e["cle"] == "couverture"][0]["acquis"]


def test_le_TAUX_IA_Act_lit_A_REALISER_et_ignore_le_NON_RENSEIGNE():
    t = conformite._de_ia_act({"audit": {"a": "todo", "b": "none", "c": "na",
                                         "d": "done", "e": "partial", "f": 3}}, {})
    assert t == {"a": "absent", "c": "sans_objet", "d": "tenu", "e": "partiel"}, t
    assert conformite._de_ia_act({"audit": {"b": "none"}}, {}) is None


# ══════════════════════════════════════════════════════════════════════════
#  2. L'AUDIT IA ACT — une liste par point, un décompte pour neuf lecteurs
# ══════════════════════════════════════════════════════════════════════════

def test_l_ecran_d_audit_pose_UNE_question_par_point():
    o = _executer("""
      auditInit();
      out.c = affiche('audit-sections');
      out.html = document.getElementById('audit-sections').innerHTML;
    """)
    listes = [c for c in o["c"] if c["balise"] == "select"]
    assert len(listes) == 34, len(listes)
    for c in listes:
        assert c["options"] == ["", "todo", "partial", "done", "na"], c
        assert c["valeur"] == "", "un point a une réponse sans qu'on l'ait donnée : %s" % c
    # LE CARRÉ NE SE CLIQUE PLUS : il faisait défiler trois états, dont un
    # qui voulait dire deux choses.
    assert "auditToggle" not in o["html"] and 'onclick="audit' not in o["html"]
    assert o["html"].count("— non renseigné —") == 34


def test_le_DECOMPTE_de_l_audit():
    o = _executer("""
      AUDIT_STATE.a5_1 = 'done'; AUDIT_STATE.a5_2 = 'partial';
      AUDIT_STATE.a5_3 = 'todo'; AUDIT_STATE.a5_4 = 'na';
      AUDIT_STATE.a6_1 = 'none'; AUDIT_STATE.a6_2 = 'conforme';
      out.c = auditComptes();
      Object.keys(AUDIT_STATE).forEach(function (k) { AUDIT_STATE[k] = 'na'; });
      AUDIT_SECTIONS.forEach(function (s) { s.items.forEach(function (it) { AUDIT_STATE[it.id] = 'na'; }); });
      out.tout_na = auditComptes();
    """)
    c = o["c"]
    assert (c["done"], c["partial"], c["todo"], c["na"]) == (1, 1, 1, 1), c
    # « none » et une valeur inconnue ne sont PAS des réponses.
    assert c["sans_reponse"] == 30 and c["total"] == 34, c
    # « SANS OBJET » SORT DU DÉNOMINATEUR ; un point sans réponse y reste.
    assert c["applicables"] == 33 and c["pct"] == round(1.5 / 33 * 100), c
    assert o["tout_na"]["pct"] is None, "un audit tout « sans objet » affiche un score"


def test_revenir_a_NON_RENSEIGNE_retire_la_reponse():
    o = _executer("""
      auditInit();
      auditRepondre('a5_1', 'done');
      out.apres_oui = JSON.parse(localStorage.getItem('cpAuditState'));
      auditRepondre('a5_1', '');
      auditRepondre('a5_2', 'none');
      out.apres_vide = JSON.parse(localStorage.getItem('cpAuditState'));
      out.none = document.getElementById('audit-none-count').textContent;
    """)
    assert o["apres_oui"] == {"a5_1": "done"}, o["apres_oui"]
    assert o["apres_vide"] == {}, "« non renseigné » a laissé une réponse : %r" % o["apres_vide"]
    assert o["none"] == "34", o["none"]


def test_une_memoire_d_audit_abimee_ne_casse_pas_l_ecran():
    o = _executer("""
      localStorage.setItem('cpAuditState', '[1,2]');
      chargerPage();
      out.etat = AUDIT_STATE; out.c = auditComptes();
    """)
    assert o["etat"] == {} and o["c"]["sans_reponse"] == 34, o


#: CHAQUE LECTEUR DE L'AUDIT, par l'endroit qui le déclare.
LECTEURS = ["function auditUpdateScore()", "window.auditExportPDF = function()",
            "function simEtatAudit(numero){", "window.cpEvalSaveAudit = function()",
            "function cardsGetData(callback){", "function pricingGetData(callback){",
            "window.gcAuditPct = function()", "function bellComputeAuditPending()"]


def _corps(debut):
    i = PAGE.index(debut)
    j = PAGE.index("\n}", i)
    return PAGE[i:j]


def test_NEUF_lecteurs_UN_decompte():
    """LE DÉFAUT QUE CE FICHIER A DÉJÀ PAYÉ : le même audit donnait deux
    pourcentages selon l'écran, parce que chacun comptait à sa façon. Un
    « sans objet » exclu ici et compté là le rendrait. Tous passent par
    `auditComptes`, et rien d'autre ne lit l'état de l'audit."""
    for l in LECTEURS:
        assert "auditComptes(" in _corps(l), "%s recompte l'audit à sa façon" % l
    # LE LIEN CROISÉ DE LA FRIA ET LE TABLEAU DE BORD, écrits en ligne.
    for ancre in ("fria-cross-links", "data.auditTodo = "):
        i = PAGE.index(ancre)
        assert "auditComptes()" in PAGE[i - 1500:i + 200], ancre
    lectures = [m.start() for m in re.finditer(r"AUDIT_STATE\s*\[", PAGE)]
    permis = [PAGE.index("function auditReponse(id){"),
              PAGE.index("window.auditRepondre = function(id, v){")]
    for p in lectures:
        assert any(0 < p - d < 400 for d in permis), (
            "l'état de l'audit est lu hors du décompte : %r"
            % PAGE[p - 120:p + 40])


def test_le_simulateur_n_appelle_pas_TRAITE_un_article_tout_SANS_OBJET():
    o = _executer("""
      AUDIT_SECTIONS.forEach(function (s) { s.items.forEach(function (it) {
        if (/Art\\.\\s*11(?![0-9])/.test(it.art)) AUDIT_STATE[it.id] = 'na'; }); });
      var src = require('fs').readFileSync(process.argv[2], 'utf8');
      var i = src.indexOf('function simEtatAudit(numero){');
      (0, eval)(src.slice(i, src.indexOf('\\n}', i) + 2));
      out.onze = simEtatAudit(11);
    """)
    assert o["onze"]["statut"] == "none" and o["onze"]["sans_objet"] == 2, o["onze"]


# ══════════════════════════════════════════════════════════════════════════
#  3. L'AIPD — oui, non, ou pas encore répondu ; et la présomption
# ══════════════════════════════════════════════════════════════════════════

def test_AIPD_rien_n_est_repondu_par_defaut():
    o = _executer("""
      var t = %s;
      window.TRAIT_DATA = [t];
      out.s = aipdGet(1);
      out.c = controles(aipdCardHtml(t));
      out.verdict = aipdVerdict(t, aipdGet(1));
      out.risque = aipdRiskLevel(aipdGet(1));
    """ % json.dumps(TRAITEMENT))
    assert out_criteres(o["s"]) == [None] * 9, o["s"]
    assert all(e == {"g": None, "v": None} for e in o["s"]["events"].values()), o["s"]
    listes = [c for c in o["c"] if c["balise"] == "select"]
    assert len(listes) == 15 and all(c["valeur"] == "" for c in listes), listes
    assert o["verdict"][0] == "À compléter", o["verdict"]
    assert o["risque"] == 0, "un risque est coté sans cotation"


def out_criteres(s):
    return s["criteria"]


def test_AIPD_le_registre_ne_presume_que_sur_un_OUI():
    """MESURÉ : le traitement livré avec chaque compte répond « Non (hors
    art. 9) » aux données sensibles, et l'AIPD en présumait son critère 4."""
    o = _executer("""
      var non = %s, oui = JSON.parse(JSON.stringify(non));
      oui.id = 2; oui.donnees_sensibles = 'Oui — données de santé';
      window.TRAIT_DATA = [non, oui];
      out.filled = [ctFilled('Non (hors art. 9)'), ctFilled('non'), ctFilled('Oui — santé'),
                    ctFilled('Néant'), ctFilled('Nom et prénom')];
      out.non = controles(aipdCardHtml(non)).filter(function (c) { return c.id === 'aipd-c-1-3'; })[0];
      out.oui = controles(aipdCardHtml(oui)).filter(function (c) { return c.id === 'aipd-c-2-3'; })[0];
      out.decl = aipdDeclaration(oui).criteres[3];
    """ % json.dumps(TRAITEMENT))
    assert o["filled"] == [False, False, True, False, True], o["filled"]
    assert o["non"]["valeur"] == "" and "disabled" not in o["non"]["attrs"], o["non"]
    assert o["oui"]["valeur"] == "oui" and "disabled" in o["oui"]["attrs"], o["oui"]
    assert o["decl"]["reponse"] is True, o["decl"]


def test_AIPD_la_premiere_version_se_relit_avec_PRUDENCE():
    """UN FALSE ET UN 1 ÉTAIENT DES DÉFAUTS, pas des réponses : ils
    redeviennent « non renseigné ». Un oui reste un oui, une cotation de 2
    à 4 reste choisie."""
    o = _executer("""
      localStorage.setItem('sentinel_aipd_v1', JSON.stringify({ '1': {
        criteria: [true, false, false, false, false, false, false, false, false],
        events: { acces: { g: 1, v: 3 }, modif: { g: 4, v: 1 }, dispar: { g: 1, v: 1 } },
        mesures: 'Chiffrement' } }));
      chargerPage();
      out.s = aipdGet(1);
      out.v2 = JSON.parse(localStorage.getItem('sentinel_aipd_v2'));
      out.v1 = localStorage.getItem('sentinel_aipd_v1') !== null;
    """)
    s = o["s"]
    assert s["criteria"] == [True] + [None] * 8, s["criteria"]
    assert s["events"] == {"acces": {"g": None, "v": 3}, "modif": {"g": 4, "v": None},
                           "dispar": {"g": None, "v": None}}, s["events"]
    assert s["mesures"] == "Chiffrement"
    assert o["v2"] and o["v1"], "la migration n'a pas écrit la nouvelle clé, ou a effacé l'ancienne"


def test_AIPD_le_verdict_et_l_EVALUATION():
    o = _executer("""
      var t = %s; window.TRAIT_DATA = [t];
      aipdRepondreCrit(1, 0, 'oui');
      out.un_oui = aipdVerdict(t, aipdGet(1))[0];
      for (var i = 1; i < 9; i++) aipdRepondreCrit(1, i, 'non');
      out.un_seul = aipdVerdict(t, aipdGet(1))[0];
      aipdRepondreCrit(1, 1, 'oui');
      out.deux = aipdVerdict(t, aipdGet(1))[0];
      ['acces', 'modif', 'dispar'].forEach(function (e) { aipdSetEv(1, e, 'g', '2'); });
      aipdSetEv(1, 'acces', 'v', '3'); aipdSetEv(1, 'modif', 'v', '1');
      out.cinq = confAipdStats();
      aipdSetEv(1, 'dispar', 'v', '2');
      out.six = confAipdStats();
      aipdSetEv(1, 'dispar', 'v', '');
      out.retire = aipdGet(1).events.dispar;
      aipdRepondreCrit(1, 0, 'non'); aipdRepondreCrit(1, 1, 'non');
      out.aucun = aipdVerdict(t, aipdGet(1))[0];
    """ % json.dumps(TRAITEMENT))
    assert o["un_oui"] == "À compléter", o["un_oui"]
    assert o["un_seul"] == "À évaluer" and o["deux"] == "AIPD requise", o
    assert o["cinq"]["requises"] == 1 and o["cinq"]["traitees"] == 0, (
        "une AIPD cotée à moitié passe pour évaluée : %r" % o["cinq"])
    assert o["six"]["traitees"] == 1 and o["six"]["eleves"] == 1, o["six"]
    assert o["retire"] == {"g": 2, "v": None}, o["retire"]
    assert o["aucun"] == "Non requise a priori", o["aucun"]


# ══════════════════════════════════════════════════════════════════════════
#  4. PRIVACY BY DESIGN, DOCUMENTATION, SENSIBILISATION
# ══════════════════════════════════════════════════════════════════════════

def test_PBD_sans_objet_sort_du_taux_NON_y_reste_le_VIDE_aussi():
    o = _executer("""
      out.vide = pbdCounts();
      var ids = pbdAllItems();
      ids.slice(0, 10).forEach(function (id) { pbdRepondre(id, 'oui'); });
      ids.slice(10, 14).forEach(function (id) { pbdRepondre(id, 'non'); });
      ids.slice(14, 17).forEach(function (id) { pbdRepondre(id, 'sans_objet'); });
      out.c = pbdCounts(); out.brique = confPbdPct();
      pbdRepondre(ids[0], ''); pbdRepondre(ids[1], 'peut-etre');
      out.retire = pbdState();
      document.getElementById('pbd-list').innerHTML = '';
      pbdRender(); out.ecran = affiche('pbd-list');
    """)
    assert o["vide"]["pct"] == 0 and o["vide"]["sans_reponse"] == 18, o["vide"]
    c = o["c"]
    assert (c["oui"], c["non"], c["sans_objet"], c["sans_reponse"]) == (10, 4, 3, 1), c
    # 10 OUI SUR 15 APPLICABLES — le contrôle sans réponse reste au
    # dénominateur : ne pas avoir répondu n'est pas être en règle.
    assert c["pct"] == round(10 / 15 * 100) == o["brique"], c
    assert "pbd-min-1" not in o["retire"] and "pbd-min-2" not in o["retire"], o["retire"]
    listes = [x for x in o["ecran"] if x["balise"] == "select"]
    assert len(listes) == 18 and listes[0]["options"] == ["", "oui", "non", "sans_objet"]


def test_PBD_la_premiere_version_ne_gardait_que_les_OUI():
    o = _executer("""
      localStorage.setItem('sentinel_pbd_v1', JSON.stringify(
        { 'pbd-min-1': true, 'pbd-min-2': false, 'pbd-fin-1': 'x' }));
      chargerPage();
      out.st = pbdState();
    """)
    assert o["st"] == {"pbd-min-1": "oui"}, o["st"]


def test_DOC_ABSENT_est_une_reponse_mais_plus_un_DEFAUT():
    o = _executer("""
      out.defaut = docRec('doc-politique');
      localStorage.setItem('sentinel_rgpddoc_v1', JSON.stringify({
        'doc-politique': { statut: 'absent', resp: 'DPO', revue: '01/02/2026' },
        'doc-pssi': { statut: 'en_place', resp: 'RSSI', revue: '' } }));
      chargerPage();
      out.politique = docRec('doc-politique'); out.pssi = docRec('doc-pssi');
      var ids = docAllIds();
      ids.forEach(function (id, i) { docSet(id, 'statut', i < 6 ? 'en_place' : i < 12 ? 'absent' : 'sans_objet'); });
      out.c = docCounts();
      docSet('doc-pssi', 'statut', 'inconnu');
      out.inconnu = docRec('doc-pssi').statut;
      out.stocke = JSON.parse(localStorage.getItem('sentinel_rgpddoc_v2'))['doc-pssi'].statut;
      /* UNE MÉMOIRE ABÎMÉE, écrite par une autre version ou à la main : la
         lecture écarte ce qu'aucune liste ne propose. */
      localStorage.setItem('sentinel_rgpddoc_v2', JSON.stringify(
        { 'doc-pssi': { statut: 'inconnu', resp: 3, revue: null } }));
      out.abime = docRec('doc-pssi');
    """)
    assert o["defaut"]["statut"] == "", o["defaut"]
    assert o["politique"] == {"statut": "", "resp": "DPO", "revue": "01/02/2026"}, o["politique"]
    assert o["pssi"]["statut"] == "en_place", o["pssi"]
    assert o["c"]["pct"] == 50 and o["c"]["applicables"] == 12, o["c"]
    assert o["inconnu"] == "" and o["stocke"] == "", (o["inconnu"], o["stocke"])
    assert o["abime"] == {"statut": "", "resp": "", "revue": ""}, o["abime"]


def test_SENS_A_PLANIFIER_est_une_reponse_mais_plus_un_DEFAUT():
    o = _executer("""
      out.defaut = sensRec('sens-all-1');
      localStorage.setItem('sentinel_sens_v1', JSON.stringify({
        'sens-all-1': { statut: 'a_planifier', date: '03/03/2026' },
        'sens-all-2': { statut: 'realise', date: '' } }));
      chargerPage();
      out.un = sensRec('sens-all-1'); out.deux = sensRec('sens-all-2');
      var ids = sensAllIds();
      ids.forEach(function (id, i) { sensSet(id, 'statut', i < 5 ? 'realise' : i < 9 ? 'a_planifier' : 'sans_objet'); });
      out.c = sensCounts();
      sensSet('sens-all-1', 'statut', 'fait');
      out.stocke = JSON.parse(localStorage.getItem('sentinel_sens_v2'))['sens-all-1'].statut;
      localStorage.setItem('sentinel_sens_v2', JSON.stringify(
        { 'sens-all-1': { statut: 'fait', date: 12 } }));
      out.abime = sensRec('sens-all-1');
    """)
    assert o["defaut"]["statut"] == "", o["defaut"]
    assert o["un"] == {"statut": "", "date": "03/03/2026"}, o["un"]
    assert o["deux"]["statut"] == "realise"
    assert o["c"]["pct"] == round(5 / 9 * 100) and o["c"]["sans_objet"] == 1, o["c"]
    assert o["stocke"] == "" and o["abime"] == {"statut": "", "date": ""}, (o["stocke"], o["abime"])


# ══════════════════════════════════════════════════════════════════════════
#  5. ReCyF, OBJECTIF 16 — oui, non, ou pas encore répondu
# ══════════════════════════════════════════════════════════════════════════

def test_RECYF_oui_non_ou_RIEN():
    o = _executer("""
      out.defaut = JSON.parse(JSON.stringify(RECYF_ANALYSE));
      recyfRepondre('gouvernance', 'oui'); recyfRepondre('couverture', 'non');
      recyfRepondre('acceptation', 'oui'); recyfRepondre('acceptation', '');
      recyfRepondre('inconnue', 'oui');
      recyfEntree('pssi', 'oui'); recyfEntree('si', 'non'); recyfEntree('audits', 'oui');
      recyfEntree('audits', '');
      out.envoi = recyfDeclarationAnalyse();
      RECYF_REF = REFS.recyf.referentiel;
      out.ecran = controles(recyfRenduAnalyse(REFS.recyf_analyse));
    """)
    d = o["defaut"]
    assert all(d[k] is None for k in ("gouvernance", "moyens_alloues", "couverture",
                                       "acceptation", "reexamen")), d
    assert d["entrees"] == {}, d["entrees"]
    e = o["envoi"]
    assert e["gouvernance"] is True and e["couverture"] is False and e["acceptation"] is None, e
    assert e["entrees"] == {"pssi": True, "si": False}, e["entrees"]
    assert "inconnue" not in e
    listes = {c["id"]: c for c in o["ecran"] if c["balise"] == "select"}
    assert len(listes) == 12, sorted(listes)
    assert listes["recyf-a-gouvernance"]["valeur"] == "oui"
    assert listes["recyf-a-acceptation"]["valeur"] == ""
    assert listes["recyf-e-si"]["valeur"] == "non" and listes["recyf-e-audits"]["valeur"] == ""
    assert all(c["options"] == ["", "oui", "non"] for c in listes.values())


def test_RECYF_la_premiere_version_se_relit_avec_PRUDENCE():
    """LA V1 GARDAIT DES CASES : false y disait « pas coché », qui n'est pas
    « non ». Un oui reste un oui ; les entrées cochées deviennent des oui."""
    o = _executer("""
      localStorage.setItem('cp-sentinel-recyf-v1', JSON.stringify({
        statut: 'essentielle', etats: { '3': 'atteint' },
        analyse: { gouvernance: true, moyens_alloues: false, couverture: false,
                   entrees: ['pssi', 'audits', 7], reexamen: true,
                   dernier_reexamen_mois: 12 } }));
      chargerPage();
      out.a = RECYF_ANALYSE; out.etats = RECYF_ETATS;
      out.statut = document.getElementById('recyf-statut-sel').value;
    """)
    a = o["a"]
    assert a["gouvernance"] is True and a["reexamen"] is True, a
    assert a["moyens_alloues"] is None and a["couverture"] is None, a
    assert a["entrees"] == {"pssi": True, "audits": True}, a["entrees"]
    assert a["dernier_reexamen_mois"] == 12
    assert o["etats"] == {"3": "atteint"} and o["statut"] == "essentielle", o


# ══════════════════════════════════════════════════════════════════════════
#  6. LE RAIL LIT CE QUE LES ÉCRANS AFFICHENT — et plus aucune revue
# ══════════════════════════════════════════════════════════════════════════

def test_les_listes_partent_ENTIERES_et_le_texte_du_registre_JAMAIS():
    o = _executer("""
      RAIL_REF = %s;
      window.TRAIT_DATA = [%s];
      pbdRepondre('pbd-min-1', 'oui'); docSet('doc-pssi', 'statut', 'absent');
      sensSet('sens-it-2', 'statut', 'sans_objet'); aipdRepondreCrit(1, 2, 'non');
      out.d = RAIL_DECL.rgpd();
      out.ia = RAIL_DECL.ia_act();
      out.txt = JSON.stringify(out.d);
    """ % (_rail_ref(), json.dumps(TRAITEMENT)))
    d = o["d"]
    assert [len(d[k]) for k in ("pbd", "doc", "sensibilisation")] == [18, 14, 10], d
    assert {"cle": "pbd-min-1", "nom": "Seules les données strictement nécessaires sont collectées",
            "reponse": "oui"} in d["pbd"]
    assert {"cle": "doc-pssi", "nom": "Politique de sécurité des systèmes d'information",
            "reponse": "absent"} in d["doc"]
    assert [x for x in d["sensibilisation"] if x["cle"] == "sens-it-2"][0]["reponse"] == "sans_objet"
    assert sum(1 for x in d["pbd"] if x["reponse"] == "") == 17
    a = d["traitements"][0]["aipd"]
    assert len(a["criteres"]) == 9 and a["criteres"][2] == {
        "nom": "Surveillance systématique", "reponse": False}, a
    assert len(a["evenements"]) == 3
    for texte in ("Gestion administrative du personnel", "Chiffrement, habilitations",
                  "Contrat + 5 ans"):
        assert texte not in o["txt"], "le texte du registre part au calcul : %s" % texte
    assert len(o["ia"]["points"]) == 34 and o["ia"]["points"][0] == {
        "cle": "a5_1", "titre": "Inventaire des pratiques potentiellement interdites"}


def test_le_rail_n_envoie_PLUS_de_revue():
    """UNE ANCIENNE MARQUE « passé en revue » peut dormir dans ce navigateur :
    elle n'est plus envoyée."""
    o = _executer("""
      RAIL_REF = %s;
      window.TRAIT_DATA = [];
      localStorage.setItem('cp-sentinel-rail-v1', JSON.stringify(
        { rgpd: { lus: ['rgpd-carto'], revus: ['rgpd-pbd', 'rgpd-doc'] } }));
      var envois = [];
      global.fetch = function (u, opt) { envois.push({ u: String(u), corps: opt && opt.body });
                                         return new Promise(function () {}); };
      railCalculer('rgpd');
      out.envois = envois;
    """ % _rail_ref())
    corps = [json.loads(e["corps"]) for e in o["envois"] if e["u"] == "/api/parcours/rgpd"]
    assert len(corps) == 1, o["envois"]
    assert "revus" not in corps[0] and corps[0]["lus"] == ["rgpd-carto"], corps[0]


def test_le_pied_du_rail_ne_propose_PLUS_de_revue():
    assert "passé cette liste en revue" not in PAGE
    corps = _corps("function railPeindreEcran(norme) {")
    assert "var decl = (b.nature === 'lecture') ? 'lus' : null;" in corps


@pytest.mark.parametrize("vide", [False, True], ids=["tout-repondu", "une-question-vide"])
def test_de_l_ECRAN_au_MOTEUR_les_six_blocs_se_mesurent(vide):
    """LA CHAÎNE ENTIÈRE : les réponses données par les vrais gestionnaires,
    la déclaration que la page envoie, et le moteur du rail qui la lit. Tout
    répondu, les blocs passent au vert ; une seule question laissée vide, le
    bloc attend et la NOMME."""
    o = _executer("""
      RAIL_REF = %s;
      window.TRAIT_DATA = [%s];
      var VIDE = %s;
      auditInit();
      auditPoints().forEach(function (p, i) {
        if (!(VIDE && i === 5)) auditRepondre(p.cle, ['done', 'todo', 'na', 'partial'][i %% 4]); });
      pbdAllItems().forEach(function (id, i) {
        if (!(VIDE && i === 3)) pbdRepondre(id, i %% 3 ? 'oui' : 'sans_objet'); });
      docAllIds().forEach(function (id, i) {
        if (!(VIDE && i === 0)) docSet(id, 'statut', i %% 2 ? 'absent' : 'en_place'); });
      sensAllIds().forEach(function (id, i) {
        if (!(VIDE && i === 9)) sensSet(id, 'statut', 'realise'); });
      for (var c = 0; c < 9; c++) if (!(VIDE && c === 8)) aipdRepondreCrit(1, c, c < 2 ? 'oui' : 'non');
      ['acces', 'modif', 'dispar'].forEach(function (e) {
        aipdSetEv(1, e, 'g', '2'); aipdSetEv(1, e, 'v', '3'); });
      recyfRepondre('gouvernance', 'oui'); recyfRepondre('moyens_alloues', 'non');
      recyfRepondre('couverture', 'non'); recyfRepondre('acceptation', 'non');
      if (!VIDE) recyfRepondre('reexamen', 'non');
      out.d = declarationsDesEcrans();
    """ % (_rail_ref(), json.dumps(TRAITEMENT), "true" if vide else "false"))
    d = o["d"]
    ia = [l for l in pn.avancement("ia_act", d["ia_act"])["blocs"] if l["cle"] == "audit"][0]
    rg = {l["cle"]: l for l in pn.avancement("rgpd", d["rgpd"])["blocs"]}
    ana = pn._manque_analyse_recyf(d["nis2"]["recyf"]["analyse"])
    if not vide:
        assert ia["etat"] == "validee", ia
        for cle in ("aipd", "pbd", "doc", "sensibilisation"):
            assert rg[cle]["etat"] == "validee", (cle, rg[cle])
        assert ana == [], ana
        return
    assert ia["etat"] != "validee" and [m["quoi"] for m in ia["manque"]] == [
        "Classification selon l'Annexe III (8 domaines)"], ia["manque"]
    attendus = {"aipd": "« Gestion des ressources humaines » : Obstacle à un droit, "
                        "à un service ou à un contrat",
                "pbd": "Aucune réutilisation incompatible sans nouvelle base légale",
                "doc": "Registre des activités de traitement (art. 30)",
                "sensibilisation": "Gestion des habilitations et journalisation"}
    for cle, quoi in attendus.items():
        assert rg[cle]["etat"] != "validee", (cle, rg[cle])
        assert [m["quoi"] for m in rg[cle]["manque"]] == [quoi], (cle, rg[cle]["manque"])
    assert [q["quoi"] for q in ana] == ["16.4 — Réexamen au moins tous les trois ans"], ana
