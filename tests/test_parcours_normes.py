# -*- coding: utf-8 -*-
"""LE RAIL DES ONZE RÉFÉRENTIELS — CE QUE LE VERT MESURE, ET RIEN D'AUTRE.

CE QUI A ÉTÉ DEMANDÉ : dans chaque module de « Votre Mise en Conformité »,
quand un bloc est rempli, l'afficher en vert et passer automatiquement au
suivant — « Suis-je concerné ? » puis « Mesures art. 21 §2 » pour NIS 2 —,
avec une infobulle à chaque fois et une flèche vers le bas, pour les onze
normes. DORA avait son rail ; `parcours_normes` le donne aux dix autres.

CE QUE CES RÈGLES GARDENT, ET QUI SE DÉFERAIT EN SILENCE :

  · un rail dont l'ordre n'est plus celui de la barre — la flèche vers le
    bas sauterait par-dessus des onglets ;
  · un formulaire vide qui validerait un bloc — mesuré sur le moteur NIS 2 :
    sans secteur, il répond déjà « hors champ » ;
  · « lu » qui passerait au vert — un écran sans champ n'a pas été rempli ;
  · une déclaration qui validerait d'un clic un bloc à remplir ;
  · une liste de manques écrite ici plutôt que tirée des modules — elle se
    séparerait du référentiel au premier millésime.
"""
import html
import io
import os
import re

import pytest

import cra
import dora_parcours
import iso27001
import iso42001
import nis2
import nis2_recyf
import nist_800_53
import nist_800_82
import nist_ai_rmf
import owasp_llm
import parcours_normes as pn

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _lire(nom):
    return io.open(os.path.join(_RACINE, nom), encoding="utf-8").read()


HTML = _lire("sentinel.html")
JS = _lire("sentinel.page.js")
APP = _lire("app.py")
CSS = "\n}\n".join(re.findall(r"<style[^>]*>(.*?)</style>", HTML, re.S))
NAV = HTML[HTML.index('class="sb-nav"'):]


def _onglets(norme):
    """Les onglets RÉELS d'un référentiel, dans l'ordre de la barre :
    (panneau, libellé écrit)."""
    out = []
    for m in re.finditer(r'<div class="sb-item"([^>]*\sdata-norme="%s"[^>]*)>(.*?)</div>'
                         % re.escape(norme), NAV, re.S):
        panneau = re.search(r"go\('([\w-]+)'", m.group(1)).group(1)
        texte = html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
        out.append((panneau, texte))
    return out


def _etats(av):
    return {l["cle"]: l["etat"] for l in av["blocs"]}


def _bloc(av, cle):
    return [l for l in av["blocs"] if l["cle"] == cle][0]


# ══ L'ORDRE, LES NOMS, LES ONGLETS ══════════════════════════════════════

@pytest.mark.parametrize("norme", sorted(pn.BLOCS))
def test_chaque_bloc_est_UN_ONGLET_de_la_barre_dans_le_MEME_ordre(norme):
    """LA FLÈCHE VERS LE BAS RELIE DEUX ONGLETS VOISINS. Un rail dont l'ordre
    divergerait de la barre la ferait sauter par-dessus des onglets — et un
    onglet sans bloc resterait sans pastille, comme s'il n'existait pas."""
    barre = [p for p, _t in _onglets(norme)]
    rail = [b["panneau"] for b in pn.BLOCS[norme]]
    assert barre == rail, ("%s — barre : %s\n  rail : %s" % (norme, barre, rail))


def test_DORA_aussi_a_sa_barre_dans_l_ordre_de_SON_rail():
    """DORA GARDE SON MOTEUR, qui place « Ce qu'un SMSI apporte déjà » en
    DEUXIÈME — avant l'analyse de risque, pour ne pas coter deux fois. La
    barre plaçait cet onglet en cinquième : la flèche aurait sauté trois
    onglets. L'onglet a été déplacé ; cette règle l'y tient."""
    barre = [p for p, _t in _onglets("dora")]
    assert barre == [b["panneau"] for b in dora_parcours.BLOCS], barre


@pytest.mark.parametrize("norme", sorted(pn.BLOCS))
def test_le_NOM_du_bloc_est_le_LIBELLE_de_l_onglet(norme):
    """L'infobulle et la barre ne désignent pas le même écran par deux noms."""
    libelles = [t for _p, t in _onglets(norme)]
    noms = [b["nom"] for b in pn.BLOCS[norme]]
    assert libelles == noms, "%s — onglets %s, blocs %s" % (norme, libelles, noms)


def test_les_onze_referentiels_ont_un_rail():
    """DIX ICI, DORA DANS SON MODULE — ET PAS UN DE PLUS OU DE MOINS que ce
    que la barre marque comme référentiel."""
    marques = set(re.findall(r'<div class="sb-item"[^>]*\sdata-norme="([a-z0-9_]+)"', NAV))
    assert marques == set(pn.BLOCS) | {"dora"}, marques


# ══ LES ÉTATS ═══════════════════════════════════════════════════════════

def test_les_cinq_etats_communs_sont_CEUX_DE_DORA():
    """UN MÊME VERT NE PEUT PAS VOULOIR DIRE DEUX CHOSES D'UN TIROIR À
    L'AUTRE : clés, couleurs, puces et animation sont celles du rail DORA."""
    for cle, e in dora_parcours.ETATS.items():
        mien = pn.ETATS[cle]
        for champ in ("couleur", "puce", "anime"):
            assert mien[champ] == e[champ], (cle, champ, mien[champ], e[champ])
    assert set(pn.ETATS) == set(dora_parcours.ETATS) | {"lue"}


def test_LU_n_est_PAS_vert_ni_dans_le_moteur_ni_a_l_ecran():
    """UN ÉCRAN SANS CHAMP N'A PAS ÉTÉ REMPLI. Le vert dit « rempli » ; si
    « lu » le prenait, trois écrans d'explication feraient un parcours
    « aux trois quarts validé » sans une seule réponse."""
    assert pn.ETATS["lue"]["couleur"] != pn.ETATS["validee"]["couleur"]
    lue = re.search(r'\.sb-item\[data-rail="lue"\] \.rail-puce\{([^}]*)\}', CSS)
    valide = re.search(r'\.sb-item\[data-rail="validee"\] \.rail-puce\{([^}]*)\}', CSS)
    assert lue and valide
    assert "--green" not in lue.group(1), lue.group(1)
    assert "--green" in valide.group(1), valide.group(1)


def test_les_couleurs_du_rail_sont_celles_du_RAIL_DORA():
    """VALIDÉ, ATTENDU, VERROUILLÉ : les trois jetons que le rail DORA donne
    à ses blocs, relus dans ses propres règles."""
    def jeton(regle, prop):
        m = re.search(re.escape(regle) + r"\{[^}]*?" + prop + r":var\(--([a-z]+)\)", CSS)
        assert m, regle
        return m.group(1)
    assert jeton('.sb-item[data-rail="validee"] .rail-puce', "border-color") == \
        jeton(".dr-bloc.validee", "border-color")
    assert jeton('.sb-item[data-rail="courante"] .rail-puce', "border-color") == \
        jeton(".dr-bloc.courante", "border-color")
    assert jeton('.sb-item[data-rail="verrouillee"] .rail-puce', "border-color") == \
        jeton(".dr-bloc.verrouillee", "border-color")


# ══ CE QUE « REMPLI » VEUT DIRE ═════════════════════════════════════════

@pytest.mark.parametrize("norme", sorted(pn.BLOCS))
def test_une_declaration_VIDE_ne_valide_RIEN(norme):
    """LE DÉFAUT QUE LE MOTEUR NIS 2 TENDAIT : sans secteur, il répond déjà
    « hors champ ». Un rail qui lirait le verdict validerait la
    qualification — et fermerait le parcours — sans une seule réponse."""
    av = pn.avancement(norme, {})
    faits = [l["cle"] for l in av["blocs"] if l["etat"] in ("validee", "lue")]
    assert not faits, "%s : validé sans rien déclarer : %s" % (norme, faits)
    assert av["courante"] == pn.BLOCS[norme][0]["cle"]
    assert not av["fini"]


def test_AUCUNE_des_deux_annexes_est_une_REPONSE_et_ferme_le_parcours():
    """« AUCUN SECTEUR CHOISI » N'EST PAS « AUCUNE DES DEUX ANNEXES ». Le
    second prononce un hors champ : le parcours s'arrête, et c'est le bon
    résultat — dit comme tel, pas comme une réussite."""
    av = pn.avancement("nis2", {"secteur": pn.SECTEUR_HORS_ANNEXES})
    et = _etats(av)
    assert et["qualifier"] == "validee"
    assert set(et.values()) == {"validee", "sans_objet"}, et
    assert all(s["motif"] and "Hors du champ" in s["motif"] for s in av["sans_objet"])
    assert av["fini"] and "hors du champ" in av["conclusion"]
    assert "n'y en a pas" in av["conclusion"]


def test_la_valeur_hors_annexes_de_l_ecran_est_CELLE_DU_MOTEUR():
    assert "value=\"%s\"" % pn.SECTEUR_HORS_ANNEXES in JS
    assert pn.SECTEUR_HORS_ANNEXES not in nis2.SECTEURS


def test_la_taille_manquante_est_NOMMEE_pas_comptee():
    secteur = [k for k, v in nis2.SECTEURS.items() if v["annexe"] == "I"][0]
    av = pn.avancement("nis2", {"secteur": secteur})
    manque = [m["quoi"] for m in _bloc(av, "qualifier")["manque"]]
    attendus = nis2.taille()["manquants"]
    assert manque == ["La taille : " + x for x in attendus], manque


def test_une_porte_DIRECTE_suffit_a_prononcer_la_qualification():
    """DEUX PORTES MÈNENT À « ESSENTIELLE » SANS SECTEUR NI TAILLE. Exiger la
    taille à qui a déclaré l'une d'elles laisserait le bloc bleu pour
    toujours."""
    porte = sorted(nis2.ESSENTIELLE_HORS_TAILLE)[0]
    av = pn.avancement("nis2", {porte: True})
    assert _etats(av)["qualifier"] == "validee"
    assert av["courante"] == "mesures"


def _nis2_qualifie():
    secteur = [k for k, v in nis2.SECTEURS.items() if v["annexe"] == "I"][0]
    return {"secteur": secteur, "effectif": 300, "ca_eur": 60e6}


def test_un_bloc_REMPLI_passe_au_vert_et_le_SUIVANT_devient_courant():
    """LE SCÉNARIO DE LA DEMANDE, PAS À PAS. Chaque bloc rempli passe au vert,
    et le bloc attendu avance d'un cran — jusqu'à la fin."""
    d = _nis2_qualifie()
    av = pn.avancement("nis2", d)
    assert (_etats(av)["qualifier"], av["courante"]) == ("validee", "mesures")
    d["mesures"] = {c: "partiel" for c, _n, _d in nis2.MESURES}
    assert pn.avancement("nis2", d)["courante"] == "gouvernance"
    d["gouvernance"] = {c: "conforme" for c in nis2.GOUVERNANCE_OBLIGATOIRE}
    assert pn.avancement("nis2", d)["courante"] == "signalement"
    d["lus"] = ["nis2-signalement"]
    assert pn.avancement("nis2", d)["courante"] == "recyf_objectifs"
    d["recyf"] = {"statut": "essentielle",
                  "etats": {str(o["numero"]): "engage"
                            for o in nis2_recyf.attendus("essentielle")["objectifs"]
                            if o["dans_le_champ"]}}
    assert pn.avancement("nis2", d)["courante"] == "recyf_analyse"
    d["revus"] = ["recyf-analyse"]
    assert pn.avancement("nis2", d)["courante"] == "chiffre"
    d["chiffre_affaires"] = 60e6
    av = pn.avancement("nis2", d)
    assert av["fini"] and av["courante"] is None and av["part"] == 100.0
    assert pn.QUI_JUGE["nis2"] in av["conclusion"]


def test_l_analyse_ReCyF_est_SANS_OBJET_pour_une_entite_importante():
    """L'objectif 16 est réservé aux entités essentielles : pour une
    importante, le bloc ne s'ouvre pas — il n'est pas « à zéro »."""
    d = dict(_nis2_qualifie(), recyf={"statut": "importante", "etats": {}})
    b = _bloc(pn.avancement("nis2", d), "recyf_analyse")
    assert b["etat"] == "sans_objet" and "essentielles" in b["motif"]


def test_le_SUIVANT_est_le_bloc_d_apres_MEME_verrouille():
    """LA LEÇON DE DORA : sur une déclaration vide, tout ce qui suit la
    qualification est verrouillé. Si le suivant sautait les blocs
    verrouillés, le passage automatique n'aurait aucune cible au moment où
    il sert le plus — juste après la qualification, qui les déverrouille."""
    av = pn.avancement("nis2", {})
    assert _etats(av)["mesures"] == "verrouillee"
    assert av["suivant"] == "mesures"


def test_le_VERROU_nomme_le_bloc_dont_il_depend():
    av = pn.avancement("cra", {})
    for cle in ("produits", "ecarts", "chiffre", "signalement"):
        b = _bloc(av, cle)
        assert b["etat"] == "verrouillee", (cle, b["etat"])
        assert "Qualifier mon rôle" in b["motif"]
    av = pn.avancement("cra", {"role": {"je_concois": True}})
    assert _etats(av)["role"] == "validee" and av["courante"] == "produits"


@pytest.mark.parametrize("norme,decl", [
    pytest.param("nis2", {}, id="nis2-vide"),
    pytest.param("nis2", _nis2_qualifie(), id="nis2-qualifie"),
    pytest.param("rgpd", {"revus": ["rgpd-pbd", "rgpd-doc"]}, id="rgpd-revus"),
    pytest.param("cra", {"role": {"je_distribue": True}}, id="cra-role"),
    pytest.param("iso27001", {"articles": {"4.1": "conforme"}}, id="iso27001-un"),
])
def test_UN_SEUL_bloc_bat(norme, decl):
    """Deux blocs qui clignotent ne désignent plus rien."""
    av = pn.avancement(norme, decl)
    assert sum(1 for l in av["blocs"] if l["etat"] == "courante") <= 1


# ══ LES DEUX DÉCLARATIONS : « LU » ET « PASSÉ EN REVUE » ════════════════

def test_un_LU_ne_valide_JAMAIS_un_bloc_a_remplir():
    """SANS CE FILTRE, UN CLIC VALIDERAIT CE QUE LE BLOC DEMANDE DE
    RENSEIGNER. Le « lu » posé sur l'écran des mesures est ignoré."""
    d = dict(_nis2_qualifie(), lus=["nis2", "nis2-signalement"],
             revus=["nis2", "nis2-gouvernance"])
    et = _etats(pn.avancement("nis2", d))
    assert et["mesures"] == "courante" and et["gouvernance"] == "attente"
    assert et["signalement"] == "lue"


def test_une_REVUE_se_DECLARE_et_ne_se_devine_pas():
    """« PAS COCHÉ » NE SE DISTINGUE PAS DE « PAS ENCORE REGARDÉ ». La liste
    ne passe au vert que sur la déclaration, et le bloc dit qu'il l'attend."""
    av = pn.avancement("rgpd", {})
    b = _bloc(av, "pbd")
    assert b["etat"] != "validee"
    assert any("passée en revue" in m["quoi"] for m in b["manque"])
    av = pn.avancement("rgpd", {"revus": ["rgpd-pbd"]})
    assert _etats(av)["pbd"] == "validee"


def test_un_ecran_A_LIRE_se_marque_LU_et_seulement_ainsi():
    av = pn.avancement("iso27001", {})
    assert _etats(av)["millesime"] == "attente"
    assert any("marquez-le lu" in m["quoi"] for m in _bloc(av, "millesime")["manque"])
    av = pn.avancement("iso27001", {"lus": ["iso27001-millesime"]})
    assert _etats(av)["millesime"] == "lue"


# ══ LES MANQUES VIENNENT DES MODULES ════════════════════════════════════

def test_les_manques_sont_COMPTES_PAR_LES_MODULES_pas_ici():
    """UNE LISTE ÉCRITE ICI SE SÉPARERAIT DU RÉFÉRENTIEL au premier
    millésime. Sur une déclaration vide, chaque bloc à remplir attend
    exactement ce que son module compte."""
    def n(norme, cle):
        return len(_bloc(pn.avancement(norme, {}), cle)["manque"])
    assert n("nis2", "mesures") == len(nis2.MESURES)
    assert n("nis2", "gouvernance") == len(nis2.GOUVERNANCE_OBLIGATOIRE)
    assert n("iso27001", "soa") == len(iso27001.declaration_applicabilite({})["non_decidees"])
    assert n("iso27001", "articles") == iso27001.maturite({})["non_renseigne"]
    assert n("iso42001", "soa") == len(iso42001.declaration_applicabilite({})["non_decidees"])
    assert n("iso42001", "articles") == iso42001.maturite({})["non_renseigne"]
    assert n("cra", "ecarts") == len(cra.ANNEXE_I_I) + len(cra.ANNEXE_I_II)
    assert n("nist_ai_rmf", "profil") == len(nist_ai_rmf.CATEGORIES)
    assert n("owasp_llm", "dix") == len(owasp_llm.RISQUES)
    assert n("nist_800_53", "socle") == len(nist_800_53.FAMILLES) + 1
    assert n("nist_800_82", "ot") == len(nist_800_82.AXES)


@pytest.mark.parametrize("norme,cle,decl", [
    pytest.param("nist_ai_rmf", "profil",
                 {"etats": {c["cle"]: "tenu" for c in nist_ai_rmf.CATEGORIES}}, id="nist"),
    pytest.param("owasp_llm", "dix",
                 {"etats": {r["cle"]: "oui" for r in owasp_llm.RISQUES}}, id="owasp"),
    pytest.param("nist_800_53", "socle",
                 {"socle": "moderate",
                  "etats": {f[0]: "amorce" for f in nist_800_53.FAMILLES}}, id="n53"),
    pytest.param("nist_800_82", "ot",
                 {"etats": {a["cle"]: "absent" for a in nist_800_82.AXES}}, id="n82"),
    pytest.param("iso27001", "articles",
                 {"articles": {l["numero"]: "partiel"
                               for c in iso27001.maturite({})["chapitres"]
                               for l in c["lignes"]}}, id="i27-articles"),
    pytest.param("cra", "ecarts",
                 {"role": {"je_concois": True},
                  "ecarts": {c: "absent" for c, _t, _d in cra.ANNEXE_I_I + cra.ANNEXE_I_II}},
                 id="cra-ecarts"),
])
def test_REPONDRE_a_tout_valide_le_bloc_quelle_que_soit_la_reponse(norme, cle, decl):
    """LE VERT DIT « RENSEIGNÉ », PAS « BIEN RENSEIGNÉ ». Des réponses toutes
    défavorables valident le bloc autant que des réponses favorables : le
    rail mesure l'avancement du travail, le taux mesure son résultat."""
    assert _etats(pn.avancement(norme, decl))[cle] == "validee"


def test_le_role_CRA_se_lit_sur_la_DECLARATION_pas_sur_le_verdict():
    """MESURÉ SUR LE MOTEUR : SANS AUCUNE RÉPONSE, IL REND DÉJÀ UN RÔLE —
    « distributeur ». Un rail qui lirait le verdict validerait la
    qualification d'un écran vierge. Il lit donc la déclaration, et
    « je distribue » est la réponse qui fait de ce défaut un choix."""
    vide = cra.qualifier_role({})
    assert vide["ok"] and vide["role"]["nom"] == "Distributeur"
    assert cra.qualifier_role({"je_distribue": True})["role"] == vide["role"]
    assert _etats(pn.avancement("cra", {}))["role"] == "courante"
    assert _etats(pn.avancement("cra", {"role": {"je_distribue": True}}))["role"] == "validee"


def test_les_questions_de_role_du_rail_sont_CELLES_DE_L_ECRAN():
    """UNE CLÉ QUE L'ÉCRAN NE POSE PAS ne serait jamais cochée : le bloc
    resterait bleu pour qui n'a que cette réponse-là à donner."""
    corps = _bloc_js("var CRA_ROLE_Q = [")
    ecran = set(re.findall(r"\{k:'([a-z_]+)'", corps))
    assert set(pn.CRA_ROLE_CLES) <= ecran, (set(pn.CRA_ROLE_CLES) - ecran)
    assert ecran - set(pn.CRA_ROLE_CLES) == {"modification_affecte_ensemble"}


@pytest.mark.parametrize("cle", [c for c in pn.CRA_ROLE_CLES if c != "je_distribue"])
def test_chaque_geste_qui_FAIT_un_role_change_le_verdict(cle):
    """Les quatre autres questions sont des gestes qui changent le rôle : si
    l'une cessait d'être lue par le moteur, la cocher validerait le bloc
    sans rien qualifier."""
    assert cra.qualifier_role({cle: True})["role"] != cra.qualifier_role({})["role"]


def _risque_complet(**k):
    r = {"nom": "Rançongiciel", "vraisemblance": 3, "consequence": 4,
         "confidentialite": True, "proprietaire": "DSI"}
    r.update(k)
    return r


def test_l_appreciation_ISO27001_attend_SES_DEUX_DATES():
    """LES DATES NE SONT PAS DÉCORATIVES : sans elles, rien ne montre que les
    critères précèdent l'appréciation. Un registre complet sans dates n'est
    pas un bloc rempli."""
    d = {"criteres": {"seuil_acceptation": 6}, "risques": [_risque_complet()]}
    b = _bloc(pn.avancement("iso27001", d), "risques")
    assert b["etat"] != "validee"
    quoi = " ".join(m["quoi"] for m in b["manque"])
    assert "critères d'acceptation ont été établis" in quoi and "appréciation" in quoi
    d["criteres"].update(etabli_le="2026-01-10", apprecie_le="2026-02-01")
    assert _etats(pn.avancement("iso27001", d))["risques"] == "validee"


def test_une_ligne_de_risque_INCOMPLETE_est_nommee_avec_ce_qui_lui_manque():
    d = {"criteres": {"seuil_acceptation": 6, "etabli_le": "2026-01-10",
                      "apprecie_le": "2026-02-01"},
         "risques": [_risque_complet(), _risque_complet(nom="Fuite", proprietaire="")]}
    b = _bloc(pn.avancement("iso27001", d), "risques")
    assert [m["quoi"] for m in b["manque"]] == ["Risque « Fuite » : propriétaire"]


def test_une_mesure_decidee_SANS_justification_n_est_pas_renseignee():
    """La justification est exigée dans les deux sens : retenue ou écartée."""
    mesures = {n: {"decision": "retenue", "statut": "mise_en_oeuvre",
                   "justification": "risque R1"} for n in iso27001.MESURES}
    premiere = sorted(iso27001.MESURES)[0]
    mesures[premiere] = {"decision": "ecartee", "justification": ""}
    b = _bloc(pn.avancement("iso27001", {"mesures": mesures}), "soa")
    assert [m["quoi"] for m in b["manque"]] == [
        "%s %s — justification" % (premiere, iso27001.MESURES[premiere]["titre"])]


def test_un_produit_SANS_NOM_ne_remplit_pas_le_registre_CRA():
    """Le moteur refuse d'évaluer un produit sans nom : le rail ne peut pas
    le compter comme déclaré."""
    base = {"role": {"je_concois": True}}
    b = _bloc(pn.avancement("cra", dict(base, produits=[{"classe": "classe_i"}])), "produits")
    assert b["etat"] != "validee"
    b = _bloc(pn.avancement("cra", dict(base, produits=[{"nom": "Passerelle"}])), "produits")
    assert b["etat"] == "validee"


@pytest.mark.parametrize("valeur", [
    pytest.param(True, id="booleen"), pytest.param(-5, id="negatif"),
    pytest.param("12", id="texte"), pytest.param(None, id="vide")])
def test_le_chiffre_d_affaires_est_un_NOMBRE_ou_il_manque(valeur):
    """UNE CASE COCHÉE N'EST PAS UN CHIFFRE D'AFFAIRES. En Python, `True`
    vaut 1 : sans ce refus, un booléen égaré validerait le bloc."""
    b = _bloc(pn.avancement("nis2", dict(_nis2_qualifie(), chiffre_affaires=valeur)), "chiffre")
    assert b["manque"], valeur


def test_le_registre_RGPD_nomme_le_traitement_ET_ses_champs_vides():
    av = pn.avancement("rgpd", {"traitements": [
        {"nom": "Paie", "champs": {c: True for c, _n in pn.RGPD_CHAMPS_ART30}},
        {"nom": "Recrutement", "champs": {"finalites": True}}]})
    manque = [m["quoi"] for m in _bloc(av, "traitements")["manque"]]
    assert len(manque) == 1 and manque[0].startswith("« Recrutement »")
    assert "base légale" in manque[0] and "finalités" not in manque[0]


def test_la_conclusion_dit_QUI_JUGE_et_ne_se_felicite_pas():
    d = {"etats": {r["cle"]: "non" for r in owasp_llm.RISQUES},
         "lus": ["owasp-pont"]}
    av = pn.avancement("owasp_llm", d)
    assert av["fini"]
    assert pn.QUI_JUGE["owasp_llm"] in av["conclusion"]
    assert "conforme" not in av["conclusion"].lower().replace("conformité", "")


# ══ LA GARDE DU MODULE ══════════════════════════════════════════════════

def _fausser(monkeypatch, norme, i, **champs):
    blocs = [dict(b) for b in pn.BLOCS[norme]]
    blocs[i].update(champs)
    nouveaux = dict(pn.BLOCS, **{norme: tuple(blocs)})
    monkeypatch.setattr(pn, "BLOCS", nouveaux)
    monkeypatch.setattr(pn, "BLOCS_PAR_NORME",
                        {n: {b["cle"]: b for b in bs} for n, bs in nouveaux.items()})


@pytest.mark.parametrize("defaut,faute", [
    pytest.param("apres", "vient APRÈS lui", id="prerequis-apres"),
    pytest.param("inconnu", "prérequis inconnu", id="prerequis-inconnu"),
    pytest.param("premier", "le parcours ne pourrait pas commencer", id="premier-bloque"),
    pytest.param("nature", "nature inconnue", id="nature"),
    pytest.param("champ", "piege manquant", id="champ-vide"),
])
def test_la_GARDE_nomme_le_parcours_qui_se_contredit(monkeypatch, defaut, faute):
    """ÉPROUVÉE SUR UN PARCOURS FAUSSÉ, un défaut à la fois : une garde qui
    rendrait toujours « rien à signaler » passerait sur le parcours sain."""
    if defaut == "apres":
        _fausser(monkeypatch, "cra", 1, prerequis=("chiffre",))
    elif defaut == "inconnu":
        _fausser(monkeypatch, "cra", 1, prerequis=("fantome",))
    elif defaut == "premier":
        _fausser(monkeypatch, "iso27001", 0, prerequis=("soa",))
    elif defaut == "nature":
        _fausser(monkeypatch, "owasp_llm", 1, nature="survol")
    else:
        _fausser(monkeypatch, "owasp_llm", 1, piege="")
    fautes = " | ".join(pn._verifier())
    assert faute in fautes, fautes


def test_la_GARDE_refuse_que_LU_prenne_le_vert(monkeypatch):
    monkeypatch.setattr(pn, "ETATS", dict(pn.ETATS, lue=dict(pn.ETATS["lue"],
                                                             couleur="vert")))
    assert any("« lu » ne peut pas porter le vert" in f for f in pn._verifier())


def test_la_GARDE_refuse_DEUX_etats_qui_battent(monkeypatch):
    monkeypatch.setattr(pn, "ANIMES", ("courante", "attente"))
    assert any("réservée au seul état" in f for f in pn._verifier())


def test_la_GARDE_refuse_un_ecran_dans_DEUX_parcours(monkeypatch):
    _fausser(monkeypatch, "owasp_llm", 1, panneau="nist-cadre")
    assert any("appartient à deux parcours" in f for f in pn._verifier())


def test_la_garde_LAISSE_passer_le_module_intact():
    assert pn._verifier() == []


# ══ LES ROUTES ══════════════════════════════════════════════════════════

def test_les_routes_rendent_le_referentiel_et_l_avancement():
    import app
    c = app.app.test_client()
    r = c.get("/api/parcours/referentiel")
    assert r.status_code == 200
    j = r.get_json()
    assert set(j["normes"]) == set(pn.BLOCS)
    assert j["rgpd_champs"] == [c for c, _n in pn.RGPD_CHAMPS_ART30]
    r = c.post("/api/parcours/nis2", json={"secteur": pn.SECTEUR_HORS_ANNEXES})
    assert r.status_code == 200 and r.get_json()["fini"]
    r = c.post("/api/parcours/fantome", json={})
    assert r.status_code == 404 and r.get_json()["motif"] == "norme_inconnue"


def test_la_route_du_rail_a_la_CADENCE_du_rail_DORA():
    """ELLE SE REDEMANDE À CHAQUE RÉPONSE : la cadence d'un calcul la ferait
    mourir au milieu d'un questionnaire de 93 lignes."""
    dora = re.search(r"@app\.route\('/api/dora/parcours'[^\n]*\n@rate_limit\(limit=(\d+)", APP)
    rail = re.search(r"@app\.route\('/api/parcours/<norme>'[^\n]*\n@rate_limit\(limit=(\d+)", APP)
    assert dora and rail and rail.group(1) == dora.group(1)


# ══ L'ÉCRAN ═════════════════════════════════════════════════════════════

def _bloc_js(debut):
    """Le texte d'une déclaration du script, de son début à la fermeture du
    PREMIER délimiteur qu'elle ouvre — accolade d'une fonction ou crochet
    d'un tableau. Apparier des accolades dans un tableau d'objets s'arrêtait
    au premier objet."""
    i = JS.index(debut)
    j = min(k for k in (JS.find("{", i), JS.find("[", i)) if k >= 0)
    ouvre = JS[j]
    ferme = {"{": "}", "[": "]"}[ouvre]
    n = 0
    while True:
        n += {ouvre: 1, ferme: -1}.get(JS[j], 0)
        if n == 0:
            return JS[i:j + 1]
        j += 1


def test_l_ecran_rassemble_les_DIX_referentiels_du_moteur():
    """UN RÉFÉRENTIEL SANS COLLECTEUR N'AURAIT JAMAIS DE RAIL, et rien ne le
    dirait : sa barre resterait simplement sans pastille."""
    corps = _bloc_js("var RAIL_DECL = {")
    cles = set(re.findall(r"^  ([a-z0-9_]+): function", corps, re.M))
    assert cles == set(pn.BLOCS), cles


def test_le_collecteur_RGPD_n_envoie_PAS_le_texte_du_registre():
    """LES FINALITÉS OU LES MESURES DE SÉCURITÉ n'ont rien à faire dans un
    calcul d'avancement : seul « rempli ou non » part, champ par champ."""
    corps = _bloc_js("  rgpd: function () {")
    assert "c[k] = !!String(t[k] || '').trim();" in corps
    assert "return { nom: t.nom, champs: c };" in corps


def test_la_pastille_du_bloc_attendu_est_la_FLECHE_VERS_LE_BAS():
    assert "puce.textContent = (b.etat === 'courante') ? '↓' : (e.puce || '');" in JS


def test_la_pastille_reste_HORS_de_la_tabulation_mais_DIT_son_etat():
    """Quarante arrêts de tabulation de plus ne diraient rien que le bandeau
    ne dise ; l'état passe dans le nom de l'onglet."""
    corps = _bloc_js("function railPeindreBarre(norme, p) {")
    assert "puce.setAttribute('tabindex', '-1');" in corps
    assert "puce.setAttribute('aria-label'," in corps
    assert "puce.setAttribute('data-bulle-avant-clic', '');" in corps


def test_UNE_rafale_de_reponses_fait_UN_appel():
    """LE LIMITEUR COUPE À 120 REQUÊTES PAR MINUTE, et les modules appellent
    déjà leur moteur à chaque champ."""
    corps = _bloc_js("function railDemander(norme, tout_de_suite) {")
    assert "clearTimeout(RAIL_ATTENTE[norme]);" in corps
    assert re.search(r"tout_de_suite \? 0 : (\d+)", corps)
    assert int(re.search(r"tout_de_suite \? 0 : (\d+)", corps).group(1)) >= 300


def test_le_rail_se_redemande_a_l_OUVERTURE_d_un_ecran_et_d_un_TIROIR():
    go = _bloc_js("function go(id, el, sec, pg) {")
    assert "window.railApresGo(id)" in go
    pli = _bloc_js("window.sbAppliquerPli = function(sec, replie){")
    assert "if (!replie && typeof window.railTiroirOuvert === 'function')" in pli


def test_DORA_peint_aussi_ses_onglets_de_la_barre():
    corps = _bloc_js("function doraRailPeindre() {")
    assert "window.railPeindreBarre('dora', p);" in corps


def test_la_barre_DORA_se_peint_SANS_recalculer_DORA():
    """MESURÉ AU DOIGT, PAR LA RECETTE DES INFOBULLES : redemander son
    avancement à DORA à l'ouverture du tiroir repeignait le rail de l'écran
    un instant après le chargement — et le repeint détruisait le bouton dont
    la bulle venait de s'ouvrir. DORA recalcule lui-même à chaque réponse ;
    la barre se peint depuis ce qu'il tient déjà."""
    corps = _bloc_js("function railCalculer(norme) {")
    dora = corps[corps.index("if (norme === 'dora') {"):]
    peint = dora.index("railPeindreBarre('dora', DORA_PARCOURS)")
    recalcule = dora.index("doraParcours()")
    assert peint < recalcule, "la barre DORA recalcule avant de peindre ce qu'elle a"
    assert "if (typeof DORA_PARCOURS !== 'undefined' && DORA_PARCOURS) railPeindreBarre" in dora


def test_la_bulle_passe_AU_DESSUS_des_onglets_voisins():
    """MESURÉ À L'ÉCRAN : le `transform` du survol enfermait la bulle dans son
    onglet, et les onglets suivants la recouvraient ligne à ligne."""
    m = re.search(r"\.sb-item\[data-rail\]:hover,\.sb-item\[data-rail\]:focus-within,\s*"
                  r"\.sb-item\[data-rail\]:has\(\.bulle-ouverte\)\{z-index:(\d+)\}", CSS)
    assert m and int(m.group(1)) > 0


def test_la_bulle_s_ouvre_DANS_la_largeur_de_la_barre():
    """La barre coupe ce qui déborde à droite : la bulle se cale sur l'onglet
    entier, de part et d'autre."""
    m = re.search(r"\.rail-puce\[data-tooltip\]::after\{([^}]*)\}", CSS)
    assert m and "left:12px" in m.group(1) and "right:8px" in m.group(1)
    assert not re.search(r"\.sb-item \.rail-puce\{[^}]*position:", CSS)
