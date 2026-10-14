# -*- coding: utf-8 -*-
"""prEN 18286 — le SMQ que l'article 17 impose au fournisseur d'un SIA à haut
risque. CE QUE CES RÈGLES MESURENT, ET POURQUOI CELLES-LÀ.

LA DEMANDE : « intégrer ce projet aussi dans la barre menu latéral sentinel
dans "votre conformité" avec analyse, questionnaire, conformité et processus ».

CE QUI A ÉTÉ MESURÉ AVANT D'ÉCRIRE UNE LIGNE, et qui a fait écrire ces règles
plutôt que d'autres :

  · DEUX VÉRITÉS SUR UN SEUL NOMBRE. Le module annonçait 83 % — plafond de la
    charge de preuve du §4.4.3.2.2 appliqué — et la carte du taux de
    conformité, qui recomposait les parts BRUTES, annonçait 100 %. Les deux
    nombres venaient du même écran. La règle de la section 5 interdit que
    l'écart revienne : le moteur rend des parts DÉJÀ plafonnées, et
    `conformite` les lit sans rejouer le verrou.
  · LES QUATRE ÉCRANS S'OUVRAIENT SUR « Chargement… » PAR TOUT CHEMIN AUTRE
    QUE LE MENU. `en18286Init()` ne vivait que dans le `onclick` de la barre ;
    or la carte de l'accueil mène par `?goto=en18286-processus` et le parcours
    guidé enchaîne ses étapes par `go()`. Relevé par l'inventaire navigateur,
    qui n'a trouvé AUCUN contenu sur ces quatre pages.
  · LE TEXTE EST LA PROPRIÉTÉ DU CEN. Mesuré contre l'empreinte du document :
    trois suites de huit mots étaient reprises du texte normatif. Après
    réécriture des trois formulations : zéro, et AUCUNE exemption déclarée.

CE QUE CE MODULE NE PEUT PAS DIRE, ET QUE LES RÈGLES LUI INTERDISENT DE
LAISSER CROIRE. Le projet est au stade de l'Enquête CEN : sa référence n'est
pas citée au Journal officiel de l'Union européenne. Le tenir entièrement
n'ouvre AUCUNE présomption de conformité à l'article 17. Et l'annexe ZA
déclare elle-même l'article 17(2) non couvert : cent pour cent ici ne veut
donc pas dire « article 17 tenu ».
"""
import hashlib
import io
import json
import os
import re
import sys
import unicodedata

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RACINE)

import conformite as c          # noqa: E402
import en18286 as EN            # noqa: E402
import parcours_normes as pn    # noqa: E402


def _lire(nom):
    return io.open(os.path.join(_RACINE, nom), encoding="utf-8").read()


HTML = _lire("sentinel.html")
PAGEJS = _lire("sentinel.page.js")
APPPY = _lire("app.py")

#: LES QUATRE ÉCRANS, DANS L'ORDRE DE LA BARRE. Les noms viennent de la
#: demande elle-même : analyse, questionnaire, conformité, processus.
PANNEAUX = ("en18286-processus", "en18286-questionnaire",
            "en18286-conformite", "en18286-analyse")


def _declaration(approche="harmonisee", pieces=True, reponse="tenu",
                 fournisseur=True, haut_risque=True, elements=True,
                 financiers=False):
    """Une déclaration complète, paramétrée par ce qu'on veut éprouver."""
    exigences = {}
    for e in EN.EXIGENCES_ESSENTIELLES:
        v = {"approche": approche}
        if pieces and approche in EN.APPROCHES_A_JUSTIFIER:
            for p in EN.PIECES_A_JUSTIFIER:
                v[p["cle"]] = True
        exigences[e["cle"]] = v
    return {
        "qualification": {"fournisseur": fournisseur,
                          "haut_risque": haut_risque,
                          "services_financiers": financiers},
        "strategie": {
            "elements": {e["cle"]: bool(elements)
                         for e in EN.ELEMENTS_STRATEGIE},
            "exigences": exigences},
        "reponses": ({p["num"]: reponse for p in EN.PARAGRAPHES}
                     if reponse else {}),
        "certifie": {},
    }


# ═══════════════════════════════════════════════════════════════════════════
#  0. LE GARDE-FOU DE LECTURE — une lecture cassée rendrait tout vert
# ═══════════════════════════════════════════════════════════════════════════

def test_le_releve_lit_bien_le_moteur_et_les_deux_fichiers_de_page():
    """CE DÉPÔT A DÉJÀ COMMIS CE DÉFAUT : une lecture qui ne trouve plus rien
    fait passer toutes les règles suivantes, parce qu'elles ne mesurent plus
    rien. Les planchers sont larges — ils attrapent la lecture cassée, pas une
    évolution du produit."""
    assert len(EN.PARAGRAPHES) >= 60, len(EN.PARAGRAPHES)
    assert len(EN.CHAPITRES) == 7, [ch["num"] for ch in EN.CHAPITRES]
    assert len(EN.ANNEXE_ZA) >= 15, len(EN.ANNEXE_ZA)
    assert len(EN.PARTS) == 5, [p["cle"] for p in EN.PARTS]
    assert len(HTML) > 100000 and len(PAGEJS) > 500000
    assert list(EN._FAUTES) == [], EN._FAUTES


def test_la_GARDE_du_moteur_NOMME_ce_qui_se_defait():
    """Le module se vérifie lui-même à l'import. Une table qui se défait doit
    donner un refus NOMMÉ, pas un calcul faux — et cette règle vérifie que la
    garde est encore branchée, pas seulement qu'elle est écrite."""
    assert isinstance(EN._FAUTES, (list, tuple)), type(EN._FAUTES)
    assert callable(EN._verifier)
    assert list(EN._verifier()) == [], EN._verifier()


# ═══════════════════════════════════════════════════════════════════════════
#  1. LE DROIT D'AUTEUR DU CEN — MESURÉ, PAS PROMIS
# ═══════════════════════════════════════════════════════════════════════════
#
# L'EMPREINTE DU DOCUMENT, ET CE QU'ELLE N'EST PAS. Le fichier ne porte AUCUN
# mot du texte normatif : il porte des empreintes SHA-256 tronquées (32 bits)
# de chaque suite de huit mots. Une empreinte ne se remonte pas — on ne peut
# rien LIRE du document avec ce fichier ; on peut seulement demander « cette
# suite de huit mots y est-elle ? ». C'est exactement ce que la règle demande.
# Produit une fois, par le script décrit dans le journal du lot, à partir de
# prEN_18286_F.docx.
EMPREINTES = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "_empreintes_en18286.json")

#: LA SEULE SUITE ADMISE, ET POURQUOI. « citée au Journal officiel de l'Union
#: européenne au titre du Règlement (UE) 2024/1689 » est la FORMULE LÉGALE de
#: la citation des normes harmonisées — règlement (UE) n° 1025/2012, article
#: 10. Elle figure dans l'annexe ZA de TOUTE norme harmonisée parce que c'est
#: la formule du droit de l'Union, pas une expression du CEN. La dire
#: autrement dirait autre chose : « publiée au Journal officiel » est faux
#: (la norme n'y est pas publiée, sa RÉFÉRENCE y est citée), et « reconnue
#: par la Commission » n'existe pas en droit. Le module la reprend donc, dans
#: UN seul champ, et la règle suivante vérifie que l'exemption ne couvre que
#: celui-là.
FORMULE_LEGALE = "journal officiel de l union europeenne"


def _mots(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return re.findall(r"[a-z0-9]+", s)


def _empreintes():
    assert os.path.isfile(EMPREINTES), "tests/_empreintes_en18286.json manque"
    return json.load(io.open(EMPREINTES, encoding="utf-8"))


def _champs_rediges():
    """Tout ce que le module écrit en PROSE. Les numéros et les titres de
    paragraphes n'y sont pas : ils sont cités comme un index, ce que le droit
    d'auteur n'interdit pas et qu'une norme harmonisée exige même pour être
    utilisable."""
    out = []
    for p in EN.PARAGRAPHES:
        for champ in ("demande", "piege"):
            if p.get(champ):
                out.append(("paragraphe:%s:%s" % (p["num"], champ), p[champ]))
    for ch in EN.CHAPITRES:
        out.append(("chapitre:%s:ce_qui_le_fait_tomber" % ch["num"],
                    ch["ce_qui_le_fait_tomber"]))
    for e in EN.ELEMENTS_STRATEGIE:
        out.append(("element:%s:nom" % e["cle"], e["nom"]))
        out.append(("element:%s:dit" % e["cle"], e["dit"]))
    for a in EN.APPROCHES:
        out.append(("approche:%s:dit" % a["cle"], a["dit"]))
        out.append(("approche:%s:charge" % a["cle"], a["charge"]))
    for pa in EN.PARTS:
        out.append(("part:%s:pourquoi" % pa["cle"], pa["pourquoi"]))
    for cle, v in EN.ETATS.items():
        out.append(("etat:%s:dit" % cle, v["dit"]))
    for pc in EN.PIECES_A_JUSTIFIER:
        out.append(("piece:%s:nom" % pc["cle"], pc.get("nom", "")))
        out.append(("piece:%s:dit" % pc["cle"], pc.get("dit", "")))
    for r in EN.RESERVES:
        out.append(("reserve:%s:dit" % r["cle"], r["dit"]))
        out.append(("reserve:%s:porte_sur" % r["cle"], r["porte_sur"]))
    out.append(("hors_champ:dit", EN.HORS_CHAMP["dit"]))
    for cle in ("licence", "presomption_dit"):
        if EN.SOURCE.get(cle):
            out.append(("source:%s" % cle, EN.SOURCE[cle]))
    return out


def test_l_empreinte_DÉCRIT_toujours_ce_document():
    """LE DÉFAUT QUE CETTE RÈGLE REND IMPOSSIBLE : une empreinte vidée ou
    régénérée depuis un autre fichier ferait passer la règle suivante sans
    rien mesurer. Douze témoins — douze suites de huit mots PRISES dans le
    document, à intervalle régulier — doivent s'y retrouver. Un témoin ne se
    remonte pas plus qu'une empreinte : c'est un haché de 32 bits."""
    e = _empreintes()
    emp, temoins = set(e["empreintes"]), e["temoins"]
    assert len(emp) > 15000, (
        "%d empreintes seulement : le fichier ne décrit plus le document "
        "entier" % len(emp))
    assert len(temoins) >= 10, len(temoins)
    perdus = [t for t in temoins if t not in emp]
    assert not perdus, (
        "%d témoin(s) ne sont plus dans l'empreinte : le fichier a été "
        "régénéré depuis autre chose que prEN_18286_F.docx" % len(perdus))


def test_AUCUNE_suite_de_huit_mots_du_module_n_est_dans_le_texte_de_la_norme():
    """LA MESURE, PAS L'INTENTION. Chaque suite de huit mots de la prose du
    module est cherchée dans l'empreinte du document. Huit mots n'est pas un
    seuil arbitraire : c'est la longueur à partir de laquelle une coïncidence
    cesse d'être une coïncidence et devient une reprise.

    MESURÉ AVANT LA CORRECTION : 3 suites partagées — deux autour de « système
    de management de la qualité », qui est le sujet même du document, et une
    sur la définition de l'approche « autre solution technique ». Après
    réécriture des trois : ZÉRO reprise, à la seule exemption déclarée
    ci-dessus — la formule légale de la citation au Journal officiel, que la
    réserve de présomption reprend parce que c'est une formule du droit de
    l'Union et non une expression du CEN."""
    emp = set(_empreintes()["empreintes"])
    reprises = []
    for nom, txt in _champs_rediges():
        m = _mots(txt)
        for i in range(len(m) - 7):
            suite = " ".join(m[i:i + 8])
            if FORMULE_LEGALE in suite:
                continue
            if hashlib.sha256(suite.encode()).hexdigest()[:8] in emp:
                reprises.append("%s : « %s »" % (nom, suite))
    assert not reprises, (
        "%d suite(s) de huit mots reprises du texte normatif :\n  %s"
        % (len(reprises), "\n  ".join(reprises[:10])))


def test_l_exemption_de_la_formule_legale_SERT_vraiment_et_ne_couvre_QU_ELLE():
    """UNE EXEMPTION QUI NE SERT PLUS EST UNE EXEMPTION QUI DORT, et une
    exemption qui dort s'élargit un jour sans que personne s'en aperçoive.
    Celle-ci doit couvrir au moins une suite, et dans UN seul champ : la
    réserve de présomption. Si demain elle couvrait un paragraphe du
    questionnaire, ce ne serait plus la formule légale qu'on reprend — ce
    serait le texte du CEN sous couvert d'elle."""
    emp = set(_empreintes()["empreintes"])
    couvertes = []
    for nom, txt in _champs_rediges():
        m = _mots(txt)
        for i in range(len(m) - 7):
            suite = " ".join(m[i:i + 8])
            if FORMULE_LEGALE not in suite:
                continue
            if hashlib.sha256(suite.encode()).hexdigest()[:8] in emp:
                couvertes.append(nom)
    assert couvertes, (
        "l'exemption de la formule légale ne couvre plus rien : retirez-la "
        "plutôt que de la laisser ouverte")
    assert set(couvertes) == {"reserve:presomption:dit"}, sorted(set(couvertes))


def test_la_prose_relevee_COUVRE_vraiment_le_module():
    """UNE RÈGLE DE NON-REPRISE QUI NE REGARDE RIEN PASSE TOUJOURS. Le relevé
    doit porter sur l'essentiel de ce que le module écrit : on le mesure en
    mots, et on vérifie qu'il atteint bien les champs de chaque table."""
    champs = _champs_rediges()
    mots = sum(len(_mots(t)) for _n, t in champs)
    assert mots > 2000, "%d mots de prose relevés seulement" % mots
    prefixes = {n.split(":")[0] for n, _t in champs}
    assert prefixes >= {"paragraphe", "chapitre", "element", "approche",
                        "part", "etat", "piece", "reserve", "source"}, prefixes


def test_la_licence_du_CEN_est_ECRITE_dans_la_source():
    """Le registre des sources du site porte la licence de chacune. Celle-ci
    est PROTÉGÉE : la dire « libre de réutilisation » comme les textes de
    l'Union serait faux, et c'est la faute que ce champ existe pour éviter."""
    assert "DROIT D'AUTEUR" in EN.SOURCE["licence"].upper()
    assert EN.SOURCE["presomption"] is False


# ═══════════════════════════════════════════════════════════════════════════
#  2. LA QUALIFICATION COMMANDE TOUT — ET LE SILENCE N'EST PAS UN « NON »
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("fournisseur,haut_risque,attendu", [
    pytest.param(None, None, None, id="rien-repondu"),
    pytest.param(True, None, None, id="fournisseur-sans-risque"),
    pytest.param(None, True, None, id="risque-sans-role"),
    pytest.param(False, True, False, id="pas-fournisseur"),
    pytest.param(True, False, False, id="pas-haut-risque"),
    pytest.param(True, True, True, id="dans-le-champ"),
])
def test_le_SILENCE_n_est_pas_un_NON_sur_la_qualification(fournisseur,
                                                          haut_risque,
                                                          attendu):
    """TROIS VALEURS, PAS DEUX. Ranger « pas encore répondu » du côté de
    « non » déclarerait le client HORS CHAMP sans qu'il l'ait dit — et
    l'écran lui annoncerait qu'il n'a rien à faire. `ok` vaut None tant que
    la question n'est pas tranchée, et le motif le nomme."""
    champ = EN.applicable({"qualification": {"fournisseur": fournisseur,
                                             "haut_risque": haut_risque}})
    assert champ["ok"] is attendu, champ
    if attendu is None:
        assert champ["motif"] == "non_qualifie", champ
    elif attendu is False:
        assert champ["motif"] == "hors_champ", champ


def test_HORS_CHAMP_il_n_y_a_PAS_de_taux_et_le_rail_dit_SANS_OBJET():
    """UN ZÉRO SE LIT COMME UN CONSTAT. Un déployeur qui vient de se déclarer
    tel a RÉPONDU : sa carte doit dire « sans objet » avec sa raison, pas
    « 0 % », et les quatre blocs du rail doivent sortir du chantier au lieu de
    rester bleus."""
    d = _declaration(fournisseur=False)
    taux, signaux = c.LECTEURS["en18286"](EN.evaluer(d), d)
    assert taux is None and "hors_champ" in signaux, (taux, signaux)

    av = pn.avancement("en18286", d)
    etats = {b["cle"]: b["etat"] for b in av["blocs"]}
    assert set(etats.values()) == {"sans_objet"}, etats
    assert len(etats) == 4, etats


def test_DANS_le_champ_les_quatre_blocs_redeviennent_du_travail():
    """LA RÈGLE MIROIR DE LA PRÉCÉDENTE. « Sans objet » partout serait aussi
    faux pour qui EST dans le champ : sans elle, un moteur qui déclarerait
    tout sans objet passerait la règle du dessus et viderait le module."""
    av = pn.avancement("en18286", _declaration(reponse=None, elements=False))
    etats = {b["cle"]: b["etat"] for b in av["blocs"]}
    assert "sans_objet" not in etats.values(), etats
    assert len(etats) == 4, etats


def test_la_qualification_SEULE_fait_deja_une_declaration():
    """QUI S'EST DÉCLARÉ HORS CHAMP A RÉPONDU, et sa carte doit le dire. Un
    écran que personne n'a touché, lui, reste absent — et le taux rend « — »,
    jamais zéro."""
    assert c.depuis_les_ecrans({"en18286": {}}) == {}
    vu = c.depuis_les_ecrans(
        {"en18286": {"qualification": {"fournisseur": False}}})
    assert "en18286" in vu, vu


# ═══════════════════════════════════════════════════════════════════════════
#  3. LE §4.4 — L'APPROCHE RETENUE COMMANDE LA CHARGE DE PREUVE
# ═══════════════════════════════════════════════════════════════════════════

def test_les_deux_approches_qui_OUVRENT_presomption_n_ont_rien_de_plus_a_porter():
    """UNE NORME HARMONISÉE CITÉE AU JOUE ET UNE SPÉCIFICATION COMMUNE ADOPTÉE
    PAR ACTE D'EXÉCUTION ouvrent présomption : il reste à documenter. Les deux
    autres n'en ouvrent aucune. Ce n'est pas un détail de rédaction — c'est ce
    qui décide des trois pièces du §4.4.3.2.2."""
    ouvrent = [a["cle"] for a in EN.APPROCHES if a["presomption"]]
    justifient = list(EN.APPROCHES_A_JUSTIFIER)
    assert sorted(ouvrent) == ["harmonisee", "specification"], ouvrent
    assert sorted(justifient) == ["autre_norme", "autre_solution"], justifient
    assert not (set(ouvrent) & set(justifient)), "une approche des deux côtés"
    for a in EN.APPROCHES:
        assert (a["preuve"] == "justifier") == (a["cle"] in justifient), a


@pytest.mark.parametrize("approche", sorted(EN.APPROCHES_A_JUSTIFIER))
@pytest.mark.parametrize("piece", [p["cle"] for p in EN.PIECES_A_JUSTIFIER])
def test_CHACUNE_des_trois_pieces_manquantes_SUFFIT_a_plafonner(approche,
                                                                piece):
    """LE VERROU NE SE NÉGOCIE PAS AU TIERS. Le §4.4.3.2.2 réclame les TROIS
    pièces ; il n'en demande pas deux et demie. Une seule qui manque laisse
    l'exigence « à prouver », et la part « stratégie » est plafonnée.

    CHAQUE PIÈCE EST ÉPROUVÉE SÉPARÉMENT, et c'est ce qui fait la valeur de
    cette règle : un moteur qui n'en regarderait que deux passerait une règle
    qui les donnerait toutes les trois à la fois."""
    d = _declaration(approche=approche)
    del d["strategie"]["exigences"]["risques"][piece]
    st = EN.strategie(d)
    assert st["a_prouver"] == ["risques"], st["a_prouver"]
    assert not st["complete"], st
    sc = EN.score(d)
    assert sc["taux"] < sc["brut"], sc
    assert sc["plafonne"] is True, sc


def test_le_plafond_de_la_charge_de_preuve_est_la_MOITIE_et_non_ZERO():
    """LA MOITIÉ, ET C'EST UNE DÉCISION. Le travail de documentation est réel ;
    c'est la DÉMONSTRATION qui manque. Zéro effacerait ce qui est fait, cent
    laisserait s'en prévaloir. MESURÉ de bout en bout : avec les cinq
    composantes déclarées, les soixante-cinq paragraphes tenus et les sept
    exigences sur « autre solution » sans preuve, le brut vaut 100 et le taux
    83 — la part « stratégie » (poids 3 sur 9) comptant pour moitié."""
    assert EN.PLAFOND_STRATEGIE_SANS_PREUVE == 0.5
    sc = EN.score(_declaration(approche="autre_solution", pieces=False))
    assert sc["brut"] == 100, sc
    assert sc["taux"] == 83, sc
    assert [v["cle"] for v in sc["verrous"]] == ["charge_de_preuve"], sc

    #  ET L'ARITHMÉTIQUE EST CELLE DES POIDS, pas un nombre écrit à la main :
    #  (6 + 3 × 0,5) / 9 = 0,8333…
    poids = {p["cle"]: p["poids"] for p in EN.PARTS}
    total = sum(poids.values())
    attendu = int(round(100.0 * (total - poids["strategie"]
                                 + poids["strategie"] * 0.5) / total))
    assert sc["taux"] == attendu, (sc["taux"], attendu)


def test_les_trois_pieces_FOURNIES_levent_le_plafond():
    """LA RÈGLE MIROIR : un verrou qu'aucune réponse ne lève n'est pas un
    verrou, c'est un mur. Les trois pièces produites, le taux remonte au
    brut — et la présomption, elle, ne remonte pas pour autant."""
    sc = EN.score(_declaration(approche="autre_solution", pieces=True))
    assert sc["taux"] == sc["brut"] == 100, sc
    assert sc["verrous"] == [], sc
    ev = EN.evaluer(_declaration(approche="autre_solution", pieces=True))
    assert ev["presomption"] is False, (
        "les trois pièces honorent la CHARGE DE PREUVE ; elles n'ouvrent "
        "aucune présomption de conformité — ce projet n'est pas cité au JOUE")


def test_une_composante_MANQUANTE_retient_le_bloc_processus():
    """LES CINQ COMPOSANTES DU §4.4.1 FONT PARTIE DE LA STRATÉGIE, et pas
    seulement les sept exigences. Une stratégie qui ne dit rien de la
    surveillance après commercialisation est incomplète même si ses sept
    approches sont honorées — et le rail doit retenir le bloc « Processus »
    au lieu de le passer au vert."""
    d = _declaration()
    d["strategie"]["elements"]["surveillance"] = False
    st = EN.strategie(d)
    assert st["composantes_manquantes"] == ["surveillance"], st
    assert not st["complete"], st
    manque, _p, _so = pn.EVALUATEURS["en18286"](d)
    quoi = " ".join(q["quoi"] if isinstance(q, dict) else str(q)
                    for q in manque["processus"])
    assert "surveillance" in quoi.lower(), quoi
    etats = {b["cle"]: b["etat"]
             for b in pn.avancement("en18286", d)["blocs"]}
    assert etats["processus"] != "validee", etats

    #  ET LA RÈGLE MIROIR, dans la même règle : les cinq déclarées, le bloc
    #  passe. Sans elle, un évaluateur qui retiendrait TOUJOURS le bloc
    #  passerait la moitié du dessus.
    etats = {b["cle"]: b["etat"]
             for b in pn.avancement("en18286", _declaration())["blocs"]}
    assert etats["processus"] == "validee", etats


def test_une_exigence_SANS_APPROCHE_n_est_pas_une_exigence_a_prouver():
    """DEUX ÉTATS QU'ON CONFONDRAIT VOLONTIERS, et qui ne s'adressent pas au
    même travail : « aucune approche retenue » demande une DÉCISION, « à
    prouver » demande des PIÈCES. Les mêler ferait écrire la mauvaise action
    au plan."""
    d = _declaration()
    d["strategie"]["exigences"]["risques"] = {}
    st = EN.strategie(d)
    assert st["sans_approche"] == ["risques"], st
    assert st["a_prouver"] == [], st
    manque, _p, _so = pn.EVALUATEURS["en18286"](d)
    quoi = " ".join(q["quoi"] if isinstance(q, dict) else str(q)
                    for q in manque["processus"])
    assert "aucune approche" in quoi.lower(), quoi


def test_une_exigence_SANS_OBJET_sort_du_denominateur():
    """SANS OBJET N'EST PAS ABSENT. Une exigence hors du système — le
    fournisseur qui n'entraîne aucun modèle sur des données, par exemple —
    sort du calcul ; la compter pour zéro punirait une déclaration juste."""
    d = _declaration()
    d["strategie"]["exigences"]["donnees"] = {"sans_objet": True}
    st = EN.strategie(d)
    assert st["sans_objet"] == ["donnees"], st
    assert st["portees"] == len(EN.EXIGENCES_ESSENTIELLES) - 1, st
    assert st["taux"] == 100, st["taux"]


# ═══════════════════════════════════════════════════════════════════════════
#  4. LE QUESTIONNAIRE — « PAS ENCORE RÉPONDU » N'EST NI « ABSENT » NI « SANS
#     OBJET »
# ═══════════════════════════════════════════════════════════════════════════

def test_un_paragraphe_SANS_REPONSE_compte_zero_et_le_dit():
    """L'INVERSE FERAIT MONTER LE TAUX À MESURE QU'ON RÉPOND MOINS. Un
    paragraphe sans réponse pèse zéro au numérateur ET au dénominateur, donc
    il tire le taux vers le bas ; et le module annonce SUR COMBIEN il porte,
    pour qu'un taux bas ne se lise pas comme un constat d'absence."""
    partiel = _declaration(reponse=None)
    moitie = [p["num"] for p in EN.PARAGRAPHES][:30]
    partiel["reponses"] = {n: "tenu" for n in moitie}
    ev = EN.evaluer(partiel)
    assert ev["renseignes"] == 30, ev["renseignes"]
    assert ev["paragraphes"] == len(EN.PARAGRAPHES), ev["paragraphes"]
    assert 0 < ev["score"]["brut"] < 100, ev["score"]


def test_un_paragraphe_SANS_OBJET_sort_du_calcul_et_ne_le_fait_pas_monter():
    """SANS OBJET SORT DU DÉNOMINATEUR — mais tout mettre sans objet ne doit
    pas rendre 100 % : une part dont aucun paragraphe ne porte doit rendre
    « — », pas « parfait »."""
    d = _declaration(reponse="sans_objet")
    ev = EN.evaluer(d)
    for cle, taux in ev["parts"].items():
        assert taux is None, (cle, taux)
    assert ev["score"]["taux"] is None or ev["score"]["taux"] == 0, ev["score"]


def test_les_quatre_etats_sont_les_quatre_etats_et_leurs_valeurs_sont_ordonnees():
    """UN ÉTAT DE PLUS OU DE MOINS CHANGE LE SENS DU TAUX SANS QUE PERSONNE
    L'AIT DÉCIDÉ. Et l'ordre des valeurs doit suivre l'ordre du sens :
    absent < partiel < tenu, « sans objet » hors échelle."""
    assert set(EN.ETATS) == {"tenu", "partiel", "absent", "sans_objet"}
    assert EN.ETATS["absent"]["valeur"] == 0.0
    assert EN.ETATS["partiel"]["valeur"] == 0.5
    assert EN.ETATS["tenu"]["valeur"] == 1.0
    assert EN.ETATS["sans_objet"]["valeur"] is None
    assert set(EN.ORDRE_ETATS) == set(EN.ETATS)


def test_le_POIDS_suit_la_charge_reglementaire_et_non_le_nombre_de_paragraphes():
    """LE CHAPITRE 4 PÈSE TROIS FOIS LE CHAPITRE 10 parce qu'il porte le §4.4,
    que ni ISO 9001 ni ISO/IEC 42001 ne donnent. Compter les paragraphes
    aurait fait l'inverse : le chapitre 9 en porte vingt-deux, le chapitre 5
    en porte trois. La règle MESURE que les deux ordres diffèrent, au lieu de
    recopier les poids."""
    par_chapitre = {}
    for p in EN.PARAGRAPHES:
        par_chapitre[p["chapitre"]] = par_chapitre.get(p["chapitre"], 0) + 1
    poids = {p["cle"]: p["poids"] for p in EN.PARTS}
    compte = {p["cle"]: sum(par_chapitre.get(ch, 0) for ch in p["chapitres"])
              for p in EN.PARTS}
    assert poids["strategie"] == 3 * poids["performance"], poids
    ordre_poids = sorted(poids, key=lambda k: (-poids[k], k))
    ordre_compte = sorted(compte, key=lambda k: (-compte[k], k))
    assert ordre_poids != ordre_compte, (
        "les poids suivent le nombre de paragraphes : le §4.4 ne pèse plus "
        "ce qu'il coûte\n  poids : %s\n  compte : %s" % (poids, compte))
    #  ET CHAQUE PARAGRAPHE EST DANS UNE PART, EXACTEMENT UNE.
    pris = [ch for p in EN.PARTS for ch in p["chapitres"]]
    assert sorted(pris) == sorted(set(pris)), pris
    assert set(pris) == {ch["num"] for ch in EN.CHAPITRES}, pris


# ═══════════════════════════════════════════════════════════════════════════
#  5. UNE SEULE VÉRITÉ SUR LE TAUX — le défaut mesuré, et ce qui l'interdit
# ═══════════════════════════════════════════════════════════════════════════

def test_le_moteur_et_la_carte_du_taux_rendent_LE_MEME_nombre():
    """LE DÉFAUT MESURÉ, ET IL ÉTAIT VISIBLE À L'ŒIL : l'écran du module
    affichait « 83 % de 100 % faits, plafonnés » et la carte du taux de
    conformité affichait 100 %. `conformite` recomposait les parts BRUTES et
    ne rejouait pas le verrou du §4.4.3.2.2.

    CE QUI L'INTERDIT MAINTENANT : le moteur rend `parts` DÉJÀ plafonnées et
    `parts_brutes` à côté ; `conformite` lit les premières et ne replafonne
    rien. Deux arithmétiques sur un même nombre n'en donneraient jamais le
    même — celle du moteur DEMI-COMPTE la part, celle de `conformite` RETIRE
    une part entière."""
    d = _declaration(approche="autre_solution", pieces=False)
    ev = EN.evaluer(d)
    etat = c.etat_des_lieux(c.depuis_les_ecrans({"en18286": d}),
                            plafond_actions=999)
    assert etat["ok"], etat
    carte = [n for n in etat["normes"] if n["cle"] == "en18286"][0]
    assert carte["renseigne"] and carte["taux"] is not None, carte
    assert carte["taux"] == ev["score"]["taux"] == 83, (
        "le module dit %r, la carte dit %r"
        % (ev["score"]["taux"], carte["taux"]))
    parts = {p["cle"]: p["taux"] for p in carte["composants"]}
    assert parts["strategie"] == ev["parts"]["strategie"] == 50, (
        parts, ev["parts"])
    #  ET LE BRUT DE LA CARTE EST CELUI DU MOTEUR : `conformite` compose
    #  depuis des parts DÉJÀ plafonnées, donc il ne replafonne pas.
    assert carte["brut"] == carte["taux"] == 83, carte
    assert ev["parts_brutes"]["strategie"] == 100, ev["parts_brutes"]


def test_le_verrou_de_la_charge_de_preuve_REMONTE_jusqu_a_la_carte():
    """UN PLAFOND QUI NE SE DIT PAS EST UN PLAFOND QU'ON DÉCOUVRE EN RÉUNION.
    Le signal part du moteur et arrive dans la carte, nommé."""
    d = _declaration(approche="autre_solution", pieces=False)
    _taux, signaux = c.LECTEURS["en18286"](EN.evaluer(d), d)
    assert "charge_de_preuve" in signaux, signaux
    #  LE SIGNAL VISE UNE RÉSERVE, PAS UN VERROU DE `conformite`, et c'est
    #  tout l'enjeu : l'arithmétique du plafond vit DANS le moteur, qui
    #  demi-compte la part. Un verrou `conformite` RETIRERAIT la part
    #  entière — deux arithmétiques, deux nombres.
    assert "en18286" not in c.VERROUS, (
        "en18286 a reçu un verrou de conformite : le plafond serait compté "
        "deux fois, et les deux comptes ne donnent pas le même nombre")
    assert "charge_de_preuve" in {r["cle"] for r in c.RESERVES["en18286"]}, (
        "le signal ne vise aucune réserve déclarée")


def test_sans_verrou_le_signal_NE_PART_PAS():
    """UN SIGNAL QUI PART TOUJOURS NE SIGNALE RIEN. Les trois pièces fournies,
    « charge_de_preuve » doit disparaître — sinon la règle du dessus ne
    mesurerait que la présence d'une chaîne."""
    d = _declaration(approche="harmonisee")
    _taux, signaux = c.LECTEURS["en18286"](EN.evaluer(d), d)
    assert "charge_de_preuve" not in signaux, signaux


# ═══════════════════════════════════════════════════════════════════════════
#  6. L'ANNEXE ZA — ET LA LIGNE LA PLUS IMPORTANTE EST CELLE QUI EST VIDE
# ═══════════════════════════════════════════════════════════════════════════

def test_l_article_17_2_est_declare_NON_COUVERT_et_ne_rend_AUCUN_taux():
    """LA LIGNE QU'ON SERAIT TENTÉ DE NE PAS AFFICHER. L'annexe ZA déclare
    elle-même l'article 17(2) — les fournisseurs soumis à la législation de
    l'Union sur les services financiers — couvert par AUCUN paragraphe. Un
    taux de 100 % sur une norme qui avoue sa lacune serait un mensonge par
    arrondi."""
    ev = EN.evaluer(_declaration())
    assert ev["score"]["taux"] == 100, ev["score"]
    nues = [l for l in ev["annexe_za"] if not l["couvert_par_la_norme"]]
    assert [l["article"] for l in nues] == list(EN.ZA_NON_COUVERTS), nues
    for l in nues:
        assert l["vises"] == [] and l["taux"] is None, l
    assert "za_non_couverts" in ev and ev["za_non_couverts"], ev.keys()
    assert {r["cle"] for r in ev["reserves"]} >= {"presomption",
                                                  "za_incomplete"}, ev["reserves"]


def test_CHAQUE_autre_ligne_de_la_ZA_resout_ses_paragraphes():
    """UNE RÉFÉRENCE QUI NE RÉSOUT RIEN AFFICHE UNE COLONNE VIDE SANS LE DIRE.
    MESURÉ : l'annexe écrit « 4.4 » là où la table porte 4.4.1 à 4.4.3.2.2, et
    « 5.3.1 » là où la table porte 5.3. La résolution doit donc marcher DANS
    LES DEUX SENS — du général au détaillé et l'inverse."""
    ev = EN.evaluer(_declaration())
    connus = {p["num"] for p in EN.PARAGRAPHES}
    muettes = []
    for l in ev["annexe_za"]:
        if not l["couvert_par_la_norme"]:
            continue
        if not l["vises"]:
            muettes.append(l["article"])
        inconnus = [n for n in l["vises"] if n not in connus]
        assert not inconnus, (l["article"], inconnus)
        assert l["taux"] == 100, (l["article"], l["taux"])
    assert not muettes, (
        "ligne(s) de l'annexe ZA dont aucun paragraphe ne se résout : %s"
        % muettes)


def test_la_resolution_marche_DANS_LES_DEUX_SENS():
    """LE CAS PRÉCIS QUI A FAIT ÉCRIRE `_resout`, et sans lequel deux lignes
    de l'annexe seraient restées vides : une référence PLUS COURTE que ce que
    la table porte (« 4.4 » → 4.4.1 …), et une référence PLUS LONGUE (« 5.3.1 »
    → 5.3)."""
    large = [p["num"] for p in EN._resout("4.4")]
    assert len(large) >= 4, large
    assert all(n.startswith("4.4") for n in large), large
    assert [p["num"] for p in EN._resout("5.3.1")] == ["5.3"], (
        [p["num"] for p in EN._resout("5.3.1")])
    assert EN._resout("99.9") == [], EN._resout("99.9")


def test_l_annexe_ZA_vise_l_article_17_et_PAS_un_autre():
    """LE MODULE SERT L'ARTICLE 17, et son annexe ZA doit le dire : si elle se
    mettait à viser l'article 9 ou l'article 15, ce ne serait plus le même
    document — ce sont d'autres projets de la famille qui les portent."""
    articles = [l["article"] for l in EN.ANNEXE_ZA]
    dix_sept = [a for a in articles if "17" in a]
    assert len(dix_sept) >= 14, articles
    assert any("11" in a for a in articles), articles
    assert any("72" in a for a in articles), articles


def test_les_services_financiers_LEVENT_la_reserve_de_l_article_17_2():
    """UNE RÉSERVE CONDITIONNELLE QUI NE SE DÉCLENCHE JAMAIS NE SERT À RIEN.
    Celle-ci ne part que si le client s'est déclaré soumis à la législation
    de l'Union sur les services financiers — et alors elle dit la seule chose
    utile : ses obligations de gouvernance interne valent exécution."""
    sans = EN.evaluer(_declaration(financiers=False))
    avec = EN.evaluer(_declaration(financiers=True))
    assert "article_17_2" not in {r["cle"] for r in sans["reserves"]}
    assert "article_17_2" in {r["cle"] for r in avec["reserves"]}


# ═══════════════════════════════════════════════════════════════════════════
#  7. LES PONTS ISO — CE QUI COMPTE EST LA LIGNE EN FACE DU VIDE
# ═══════════════════════════════════════════════════════════════════════════

def test_les_DEUX_chapitres_sans_equivalent_le_sont_VRAIMENT_dans_les_deux_tables():
    """LA PHRASE QUE CE MODULE EXISTE POUR CONTREDIRE : « nous sommes
    certifiés ISO 9001, donc l'article 17 est couvert ». Deux chapitres n'ont
    d'équivalent dans AUCUNE des deux tables de correspondance du document —
    et c'est exactement ce que le règlement ajoute. La règle ne recopie pas
    la liste : elle la RECALCULE depuis les deux ponts, et la confronte à
    `SANS_EQUIVALENT`."""
    nus = None
    for p in EN.PONTS:
        ici = {l["ici"] for l in p["lignes"] if not l["couvert"]}
        nus = ici if nus is None else (nus & ici)
    assert nus == set(EN.SANS_EQUIVALENT), (sorted(nus),
                                            sorted(EN.SANS_EQUIVALENT))
    assert len(nus) == 2, sorted(nus)
    assert any("4.4" in x for x in nus), sorted(nus)


def test_les_deux_ponts_ne_sont_PAS_vides_et_ne_sont_PAS_complets():
    """UN PONT TOUT PLEIN OU TOUT VIDE NE DIT RIEN. S'ils étaient complets,
    le certificat suffirait ; s'ils étaient vides, la structure harmonisée
    des articles 4 à 10 ne servirait à rien. MESURÉ : 11 lignes sur 13 pour
    ISO 9001, 9 sur 11 pour ISO/IEC 42001."""
    ev = EN.evaluer(_declaration())
    assert len(ev["ponts"]) == 2, ev["ponts"]
    for p in ev["ponts"]:
        assert 0 < p["correspondances"] < p["total"], p
        assert p["total"] == len(p["lignes"]), p


def test_la_FAMILLE_dit_lesquelles_le_site_traite_DEJA():
    """ACHETER « LA NORME DU SMQ » ET CROIRE AVOIR TRAITÉ L'ARTICLE 10, C'EST
    SE TROMPER DE DOCUMENT. La famille est affichée avec, pour chacune, si ce
    site la traite — et cette marque doit être VRAIE : elle est confrontée aux
    normes réellement branchées sur le taux de conformité."""
    dedans = {f["ref"] for f in EN.FAMILLE if f["dans_le_site"]}
    assert dedans, "aucune norme de la famille n'est marquée traitée"
    noms = {n["nom"] for n in c.NORMES}
    manquantes = [r for r in dedans if r not in noms]
    assert not manquantes, (
        "déclarée(s) traitée(s) par le site, mais absente(s) de la table des "
        "normes : %s" % manquantes)
    dehors = {f["ref"] for f in EN.FAMILLE if not f["dans_le_site"]}
    fautes = [r for r in dehors if r in noms]
    assert not fautes, (
        "déclarée(s) NON traitée(s), alors que le site les porte : %s" % fautes)


def test_les_TROIS_contradictions_du_document_sont_DITES_et_non_masquees():
    """LES DIRE VAUT MIEUX QUE LES DÉCOUVRIR EN RÉUNION. Chacune nomme
    l'endroit du document, ce qui s'y contredit, et le fait constaté."""
    assert len(EN.CONTRADICTIONS) == 3, EN.CONTRADICTIONS
    for x in EN.CONTRADICTIONS:
        assert x["ou"] and x["quoi"] and x["fait"], x
        assert len(x["fait"]) > 20, x


# ═══════════════════════════════════════════════════════════════════════════
#  8. LE PLAN — DÉRIVÉ, ET CE QUI PLAFONNE PASSE DEVANT
# ═══════════════════════════════════════════════════════════════════════════

def test_ce_qui_PLAFONNE_passe_devant_le_reste_du_plan():
    """TANT QUE LA CHARGE DE PREUVE N'EST PAS HONORÉE, LE RESTE BUTE SUR LE
    MÊME PLAFOND. Monter les paragraphes d'abord, c'est travailler sous un
    plafond qu'on n'a pas levé."""
    d = _declaration(approche="autre_solution", pieces=False, reponse="absent",
                     elements=False)
    plan = EN.plan(d, limite=12)
    assert plan, "aucune action sur une déclaration trouée de partout"
    tete = plan[0]
    assert "exigence" in tete["quoi"].lower(), tete
    assert tete["manque"], tete
    assert [e["rang"] for e in plan] == list(range(1, len(plan) + 1)), plan


def test_le_plan_se_TAIT_sur_un_module_complet():
    """UN PLAN QUI PROPOSE TOUJOURS QUELQUE CHOSE N'EST PAS UN PLAN. Tout tenu,
    toutes les pièces produites, il n'y a plus d'action — et la réserve de
    présomption, elle, reste."""
    plan = EN.plan(_declaration(), limite=12)
    assert plan == [], plan
    ev = EN.evaluer(_declaration())
    assert any(r["cle"] == "presomption" for r in ev["reserves"]), ev["reserves"]


def test_la_limite_du_plan_est_RESPECTEE():
    """UN PLAN DE SOIXANTE LIGNES NE SE LIT PAS. L'écran en demande douze ;
    la limite doit être tenue, et la demande d'une seule action doit rendre
    une seule action."""
    d = _declaration(approche="autre_solution", pieces=False, reponse="absent",
                     elements=False)
    assert len(EN.plan(d, limite=3)) == 3
    assert len(EN.plan(d, limite=1)) == 1
    assert len(EN.plan(d, limite=99)) > 3


# ═══════════════════════════════════════════════════════════════════════════
#  9. LES ROUTES — CE QUE L'ÉCRAN DEMANDE, LE SERVEUR LE SERT
# ═══════════════════════════════════════════════════════════════════════════

def _appeler(url, methode="GET", corps=None):
    import app as application
    a = application.app
    lien = a.url_map.bind("localhost")
    ep, args = lien.match(url, method=methode)
    with a.test_request_context(url, method=methode, json=corps):
        r = a.view_functions[ep](**args)
        r = r[0] if isinstance(r, tuple) else r
        return json.loads(r.get_data(as_text=True))


def test_la_route_du_referentiel_sert_les_SOIXANTE_CINQ_paragraphes():
    r = _appeler("/api/en18286/referentiel")
    assert r["ok"] is True, r
    ref = r["referentiel"]
    assert len(ref["paragraphes"]) == len(EN.PARAGRAPHES)
    assert len(ref["annexe_za"]) == len(EN.ANNEXE_ZA)
    assert ref["presomption"] is False
    for cle in ("chapitres", "parts", "approches", "elements_strategie",
                "exigences_essentielles", "pieces_a_justifier", "famille",
                "contradictions", "hors_champ", "reserve", "source"):
        assert ref.get(cle), cle
    #  AUCUN ÉNONCÉ NORMATIF NE SORT PAR CETTE ROUTE : ce qu'elle rend de
    #  la norme est une liste de numéros et de titres, et la prose est
    #  celle du cabinet — la section 1 le mesure contre l'empreinte.
    assert "DROIT D'AUTEUR" in ref["source"]["licence"].upper()


def test_la_route_d_evaluation_rend_le_taux_ET_le_plan():
    d = _declaration(approche="autre_solution", pieces=False)
    r = _appeler("/api/en18286/evaluer", "POST",
                 {"declaration": d, "limite": 4})
    assert r["ok"] is True, r
    assert r["score"]["taux"] == 83, r["score"]
    assert len(r["plan"]) == 4, r["plan"]
    assert r["parts"]["strategie"] == 50, r["parts"]


def test_la_route_d_evaluation_REFUSE_une_declaration_qui_n_en_est_pas_une():
    """UNE DEMANDE DE TRAVERS NE DOIT PAS RENDRE UN TAUX. Mesuré ailleurs dans
    ce dépôt : une enveloppe passée telle quelle au moteur levait une
    TypeError et faisait tomber les treize cartes."""
    r = _appeler("/api/en18286/evaluer", "POST", {"declaration": "oui"})
    assert r["ok"] is True, r
    assert r["applicable"]["ok"] is None, r["applicable"]


def test_les_deux_routes_sont_ECRITES_une_seule_fois():
    """Une route déclarée deux fois ne lève rien à l'import : la seconde
    écrase la première, et c'est le code mort qui répond."""
    for chemin in ("/api/en18286/referentiel", "/api/en18286/evaluer"):
        assert APPPY.count('"%s"' % chemin) + APPPY.count("'%s'" % chemin) == 1, chemin


# ═══════════════════════════════════════════════════════════════════════════
#  10. LES QUATRE ÉCRANS — LA BARRE, LE RAIL, ET LE CHEMIN QUI LES AMORCE
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("panneau", PANNEAUX)
def test_CHAQUE_panneau_demande_existe_dans_la_page(panneau):
    """LES QUATRE NOMS VIENNENT DE LA DEMANDE : analyse, questionnaire,
    conformité, processus."""
    assert 'id="p-%s"' % panneau in HTML, panneau
    assert 'id="%s-body"' % panneau.replace("en18286-", "en18286-") in HTML \
        or 'id="%s-body"' % panneau in HTML, panneau


@pytest.mark.parametrize("panneau", PANNEAUX)
def test_CHAQUE_panneau_a_son_entree_de_barre_sous_la_conformite(panneau):
    """« Votre Mise en Conformité Réglementaire » est la famille demandée : le
    tiroir doit y être, pas ailleurs."""
    m = re.search(r'onclick="go\(\'%s\'[^"]*"' % re.escape(panneau), HTML)
    assert m, "aucune entrée de barre ne mène à %s" % panneau
    assert 'data-norme="en18286"' in HTML
    titre = re.search(r'<div class="sb-section sb-pliable" data-grp="en18286"'
                      r' data-fam="([a-z]+)"', HTML)
    assert titre and titre.group(1) == "conformite", titre


def test_le_tiroir_porte_les_QUATRE_onglets_et_pas_un_de_plus():
    nav = HTML[HTML.index('data-grp="en18286"'):]
    nav = nav[:nav.index('<!-- ═══ NIS 2')] if '<!-- ═══ NIS 2' in nav else nav
    onglets = re.findall(r'onclick="go\(\'(en18286-[a-z]+)\'', nav)
    assert onglets == list(PANNEAUX), onglets


@pytest.mark.parametrize("panneau", PANNEAUX)
def test_un_lien_PROFOND_amorce_le_module_au_lieu_de_laisser_Chargement(panneau):
    """LE DÉFAUT MESURÉ PAR L'INVENTAIRE NAVIGATEUR : il n'a trouvé AUCUN
    contenu sur ces quatre pages. `;en18286Init()` ne vit que dans le
    `onclick` de la barre ; la carte de l'accueil mène par
    `?goto=en18286-processus` et le parcours guidé enchaîne par `go()`. Sans
    la ligne d'amorçage dans `go()`, les quatre écrans s'ouvraient sur un
    « Chargement… » qui ne finissait jamais."""
    assert "'%s'" % panneau in PAGEJS or '"%s"' % panneau in PAGEJS, panneau
    amorce = re.search(
        r"if \(id\.indexOf\('en18286'\) === 0 && typeof window\.en18286Init "
        r"=== 'function'\) _amorcer\(window\.en18286Init\);", PAGEJS)
    assert amorce, (
        "go() n'amorce pas le module : un lien profond ou un parcours guidé "
        "ouvrira « Chargement… » sans fin")


def test_les_quatre_panneaux_portent_la_couleur_du_referentiel():
    """LA COULEUR DIT « QUEL RÉFÉRENTIEL », et elle est celle du moteur — pas
    une teinte recopiée dans la feuille de style."""
    coul = c.COULEURS["en18286"].lstrip("#")
    rvb = " ".join(str(int(coul[i:i + 2], 16)) for i in (0, 2, 4))
    assert "{--ref:%s}" % rvb in HTML, (
        "les pages du module ne portent pas %s (%s)" % (c.COULEURS["en18286"],
                                                        rvb)) 
    assert '.sb-nav .sb-item[data-norme="en18286"]{--sb-ic:%s}' \
        % c.COULEURS["en18286"] in HTML


def test_le_rail_du_referentiel_porte_les_QUATRE_blocs_dans_l_ordre():
    """LE RAIL EST CE QUI DIT OÙ ALLER ENSUITE. Les quatre blocs sont ceux de
    la demande, et leurs noms sont ceux des onglets — une règle du dépôt
    l'exige déjà ; celle-ci mesure en plus que les deux blocs de LECTURE
    attendent les deux blocs de SAISIE."""
    blocs = pn.BLOCS["en18286"]
    assert [b["cle"] for b in blocs] == ["processus", "questionnaire",
                                         "conformite", "analyse"], blocs
    saisie = [b["cle"] for b in blocs if b["nature"] == "saisie"]
    lecture = [b["cle"] for b in blocs if b["nature"] == "lecture"]
    assert saisie == ["processus", "questionnaire"], saisie
    assert lecture == ["conformite", "analyse"], lecture
    for b in blocs:
        assert b["panneau"] in PANNEAUX, b


def test_le_module_est_la_TREIZIEME_norme_du_taux_et_non_une_carte_de_plus():
    """UN TIROIR DE PLUS SANS CARTE DE TAUX SERAIT UN MODULE QUI NE COMPTE
    NULLE PART. Le nombre n'est pas épinglé ici : ce qui se mesure est
    l'ACCORD entre la table des normes, l'ordre de la barre, les
    compositions, les lecteurs, les évaluateurs et les traducteurs."""
    assert "en18286" in c.NORMES_PAR_CLE
    assert "en18286" in c.ORDRE_BARRE
    for table in (c.COMPOSITIONS, c.LECTEURS, c.EVALUATEURS, c.TRADUCTEURS,
                  c.COULEURS, c.RESERVES, c.SANS_OBJET):
        assert "en18286" in table, table
    assert [p["cle"] for p in c.COMPOSITIONS["en18286"]] \
        == [p["cle"] for p in EN.PARTS], c.COMPOSITIONS["en18286"]
    assert c.NORMES_ANNONCEES == len(c.NORMES)


def test_la_DERNIERE_etape_du_parcours_s_amorce_aussi_par_go():
    """CE QUE LA RECETTE A TROUVÉ SUR LE PANNEAU LE PLUS VISITÉ DU SITE.
    `conf-taux` est la dernière étape de CINQ parcours guidés — dont celui de
    prEN 18286 — et la carte « taux de conformité » de l'accueil y mène par
    `?goto=`. Or `confInit()` ne vivait que dans le `onclick` de la barre :
    arrivé par `go()`, le panneau n'affichait que son chapô. Aucune carte,
    aucun taux, et rien pour le dire.

    MESURÉ DANS UN NAVIGATEUR, avant et après : 742 caractères et aucune
    occurrence de « prEN 18286 » sur la page ; puis la carte, et son taux."""
    amorce = re.search(
        r"if \(id\.indexOf\('conf-'\) === 0 && typeof window\.confInit "
        r"=== 'function'\) _amorcer\(window\.confInit\);", PAGEJS)
    assert amorce, (
        "go() n'amorce pas l'écran du taux : les cinq parcours qui s'y "
        "terminent y conduiront sur une page vide")
    #  ET LES TROIS PANNEAUX DU TIROIR SONT COUVERTS PAR CE SEUL PRÉFIXE :
    #  `conf-taux`, `conf-plan`, `conf-limites`. Un quatrième écran du tiroir
    #  qui ne commencerait pas par « conf- » retomberait dans le défaut.
    servis = set(re.findall(r'id="p-(conf-[a-z]+)"', HTML))
    assert servis >= {"conf-taux", "conf-plan", "conf-limites"}, servis
    etapes = set(re.findall(r"\{id:'(conf-[a-z]+)'", PAGEJS))
    assert etapes, "aucun parcours ne mène plus à l'écran du taux"
    assert all(e.startswith("conf-") for e in etapes), etapes


def test_aucun_ECRAN_du_taux_ne_fige_un_COMPTE_de_normes_devenu_faux():
    """LE DÉFAUT MESURÉ À L'ÉCRAN, ET IL AVAIT DEUX ANS D'AVANCE SUR LE
    PRODUIT : le surtitre disait « les treize normes » et, deux lignes plus
    bas, le titre disait « Onze taux » — le libellé du menu, lui, disait
    « Les neuf taux ». Trois comptes, trois chiffres, un seul vrai.

    CE QUE LA RÈGLE EXIGE : que le nombre écrit dans ces trois endroits soit
    celui que le moteur annonce, ou qu'il n'y soit pas écrit du tout. Elle
    cherche les mots des comptes, pas des chiffres — c'est en lettres qu'ils
    s'écrivent ici."""
    mots = {9: "neuf", 10: "dix", 11: "onze", 12: "douze", 13: "treize",
            14: "quatorze", 15: "quinze", 16: "seize"}
    juste = mots.get(c.NORMES_ANNONCEES)
    assert juste, ("%d normes annoncées : ajouter ce nombre à la table des "
                   "mots, puis réécrire l'écran du taux" % c.NORMES_ANNONCEES)
    i = HTML.index('id="p-conf-taux"')
    bloc = HTML[i:HTML.index("</div>", HTML.index('id="conf-body"', i))
                if 'id="conf-body"' in HTML[i:i + 6000] else i + 4000]
    perimes = sorted(m for n, m in mots.items()
                     if n != c.NORMES_ANNONCEES
                     and re.search(r"\b%s\b" % m, bloc, re.I))
    assert not perimes, (
        "l'écran du taux compte encore « %s » normes alors qu'il y en a %s : "
        "un compte se calcule ou ne s'écrit pas"
        % (", ".join(perimes), juste))
    #  ET LE LIBELLÉ DU MENU N'EN PORTE PLUS AUCUN : c'est lui qui a vieilli
    #  le plus longtemps sans que personne le relise.
    i = PAGEJS.index("var PAGE_META = {")
    meta = PAGEJS[i:PAGEJS.index("\n};", i)]
    ligne = re.search(r"'conf-taux':\s*\{[^}]*\}", meta).group(0)
    dedans = sorted(m for m in mots.values() if re.search(r"\b%s\b" % m, ligne, re.I))
    assert not dedans, (
        "le libellé de menu de l'écran du taux fige un compte (« %s ») : il a "
        "déjà menti pendant quatre normes" % ", ".join(dedans))


def test_la_declaration_de_l_ecran_est_RAMASSEE_une_seule_fois():
    """LE RAIL ET LE TAUX LISENT LA MÊME DÉCLARATION. Deux collectes
    finiraient par divergar : le collecteur du module est écrit une fois."""
    assert PAGEJS.count("en18286: function () { return EN18286_DECL; },") == 1
    assert PAGEJS.count("var EN18286_CLE_STOCK = 'cp-sentinel-en18286-v1';") == 1
