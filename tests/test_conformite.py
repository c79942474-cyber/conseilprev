# -*- coding: utf-8 -*-
"""Le taux de conformité des onze normes, et le plan qui le fait monter.

LA DEMANDE : un taux entre 0 et 100 % par norme, tiré des analyses de risque
et des réponses aux questionnaires, puis un plan de mise en conformité et de
remédiation pour s'approcher de 100 %.

CE QUE CES RÈGLES GARDENT, ET POURQUOI CHACUNE EXISTE.

Un taux de conformité est l'objet le plus facile à truquer d'un outil de
conformité : personne ne recompte, et un chiffre flatteur ne se conteste pas
avant l'audit. Les règles ci-dessous visent donc, une par une, les façons
précises dont ce chiffre peut mentir :

  · en additionnant des natures qui ne s'additionnent pas (une obligation
    légale, une norme certifiable et un cadre volontaire) ;
  · en laissant une moyenne diluer la composante qui commande ;
  · en comptant les cases vides comme vertes ;
  · en oubliant qu'un défaut bloquant plafonne tout le reste ;
  · en annonçant des gains qui ne mènent pas où le plan le dit ;
  · en promettant 100 % là où aucun travail ne le permet.
"""
import io
import json
import os
import re
import sys

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RACINE)

import conformite as c  # noqa: E402
import cra as _cra  # noqa: E402
import iso27001 as _i27  # noqa: E402
import iso42001 as _i42  # noqa: E402
import nist_ai_rmf as _nist  # noqa: E402
import owasp_llm as _ow  # noqa: E402


def _lire(nom):
    with io.open(os.path.join(_RACINE, nom), encoding="utf-8") as f:
        return f.read()


PAGEJS = _lire("sentinel.page.js")
SENTINEL = _lire("sentinel.html")


# ── UN DOSSIER À MI-CHEMIN, qui sert de banc à la plupart des règles ──────
#
# IL EST CONSTRUIT DEPUIS LES RÉFÉRENTIELS EUX-MÊMES, jamais recopié : une
# déclaration écrite à la main ici vieillirait sans bruit le jour où une
# norme gagne une ligne, et les règles mesureraient alors un dossier qui
# n'existe plus.

def _dossier():
    return {
        "ia_act": dict([(p[0], "tenu") for p in c.AUDIT_IA_ACT[:12]]
                       + [(p[0], "partiel") for p in c.AUDIT_IA_ACT[12:18]]),
        # UN SECTEUR QUI EXISTE, ET C'EST LE POINT. Ce banc a longtemps
        # déclaré « finance », qu'aucune des deux annexes ne porte : le
        # moteur NIS 2 le jugeait HORS CHAMP, et le taux mesurait quand même
        # ses dix mesures — le défaut que « sans objet » corrige. Il fallait
        # un secteur réel pour que le banc éprouve encore NIS 2. Un
        # assureur n'est pas dans NIS 2 ; une banque l'est (annexe I).
        "nis2": {"nom": "Banque", "secteur": "banque", "effectif": 900,
                 "ca_eur": 400e6,
                 "mesures": {k: "conforme" for k in list("abcdef")},
                 "gouvernance": {"approbation": "conforme",
                                 "supervision": "partiel"}},
        "cra": {"nom": "Boîtier", "marche_ue": True, "role": "fabricant",
                "fonctions": ["reseau"],
                "ecarts": dict([(e[0], "conforme")
                                for e in _cra.ANNEXE_I_I[:7]]
                               + [(e[0], "conforme")
                                  for e in _cra.ANNEXE_I_II[:3]])},
        "iso42001": {"nom": "Assureur",
                     "articles": {n: "conforme" for ch in _i42.CHAPITRES
                                  for n, *_ in ch[2]},
                     # « conforme », ET C'EST LE POINT. Le dossier d'essai
                     # n'a longtemps porté AUCUNE mesure en œuvre : les deux
                     # côtés du calcul étaient faux de la même façon — les
                     # extracteurs d'écarts cherchaient « oui » — et donc
                     # d'accord entre eux. Un banc où rien n'est fait ne
                     # mesure pas ce qui se passe quand quelque chose l'est.
                     # RETENIR LARGEMENT, N'AVOIR APPLIQUÉ QU'UNE PARTIE :
                     # c'est l'état réel d'un dossier à mi-chemin, et c'est
                     # le seul qui laisse des mesures RETENUES-NON-APPLIQUÉES
                     # — donc des écarts sur lesquels les ponts entre
                     # référentiels peuvent mordre. Un banc où tout ce qui
                     # est retenu est appliqué n'éprouve jamais le rang 2.
                     # TROIS ÉTATS DANS LE MÊME DOSSIER, ET LES TROIS SONT
                     # NÉCESSAIRES : une mesure appliquée (pour que le taux
                     # ne soit pas nul), une retenue-non-appliquée (pour que
                     # les ponts aient un écart sur quoi mordre), et une
                     # retenue SANS justification (pour que la déclaration
                     # reste irrecevable et que le verrou existe). Un banc
                     # qui n'en porterait que deux laisserait une règle
                     # entière sans objet — et c'est la garde interne de
                     # cette règle-là qui l'a dit.
                     "mesures": dict(
                         [(m[0], {"decision": "retenue",
                                  "justification": "SoA",
                                  "mise_en_oeuvre": "conforme"})
                          for obj in _i42.ANNEXE_A for m in obj[3][:1]]
                         + [(m[0], {"decision": "retenue",
                                    "justification": "SoA"})
                            for obj in _i42.ANNEXE_A for m in obj[3][1:2]]
                         + [(m[0], {"decision": "retenue"})
                            for obj in _i42.ANNEXE_A for m in obj[3][2:]])},
        "iso27001": {"nom": "Assureur", "perimetre": "SI assurance",
                     "risques": [{"cle": "r%d" % i, "actif": "SI",
                                  "vraisemblance": 3, "consequence": 3,
                                  "proprietaire": "RSSI", "option": "reduire",
                                  "acceptation": "DG"} for i in range(5)],
                     "articles": {n: "conforme" for ch in _i27.CHAPITRES
                                  for n, *_ in ch[2]}},
        "rgpd": {"briques": {"registre": 80, "pbd": 45, "doc": 60,
                             "sensibilisation": 30}},
        "nist_ai_rmf": dict([(cat["cle"], "tenu") for cat in _nist.CATEGORIES
                             if cat["fonction"] == "GOVERN"]
                            + [(cat["cle"], "amorce")
                               for cat in _nist.CATEGORIES
                               if cat["fonction"] in ("MAP", "MEASURE")]),
        "owasp_llm": {"LLM01": "oui", "LLM02": "oui", "LLM06": "partiel",
                      "LLM09": "oui"},
        # UN ÉTABLISSEMENT DE CRÉDIT, DONC LE CADRE COMPLET : c'est le seul
        # régime qui porte les vingt-six articles du titre II, et donc le
        # seul où un article manquant se voit. DEUX CONTRATS, dont un qui
        # soutient une fonction critique avec une clause du paragraphe 3
        # absente : sans lui, la part « tiers » serait pleine et le verrou
        # du module de contrats ne serait jamais éprouvé.
        "dora": {
            "entite": "etablissement_credit",
            "identifiee_nis2": True,
            "etats": dict([(n, "prouve") for n in range(2, 16)]
                          + [(n, "amorce") for n in range(16, 22)]),
            "contrats": [
                {"fonction_critique": True,
                 "clauses": dict(
                     [("commune_%s" % l, "presente") for l in "abcdefghi"]
                     + [("critique_%s" % l, "presente") for l in "abcd"])},
                {"fonction_critique": False,
                 "clauses": {"commune_a": "presente",
                             "commune_b": "presente",
                             "commune_c": "partielle"}},
            ],
        },
    }


@pytest.fixture(scope="module")
def etat():
    r = c.etat_des_lieux(_dossier(), plafond_actions=999)
    assert r["ok"], r
    return r


def _norme(etat, cle):
    return [n for n in etat["normes"] if n["cle"] == cle][0]


# ══════════════════════════════════════════════════════════════════════════
#  1. NEUF TAUX, ET NEUF NATURES QUI NE S'ADDITIONNENT PAS
# ══════════════════════════════════════════════════════════════════════════

def test_les_normes_EVALUEES_sont_celles_QUE_LA_PAGE_MONTRE():
    """LE MODULE, LE TITRE ET LA GRILLE DOIVENT COMPTER PAREIL.

    TROIS SURFACES DISENT LE MÊME NOMBRE, et ce dépôt a déjà vu deux d'entre
    elles diverger : le titre annonçait sept normes quand la grille en
    montrait neuf. Un titre est codé en dur, une grille se complète carte
    par carte, et un module se déclare dans une table — rien ne les tient
    ensemble sauf cette règle.

    LE NOMBRE SE DÉCIDE À UN SEUL ENDROIT : `conformite.NORMES_ANNONCEES`.
    Les deux autres surfaces lui sont confrontées ici."""
    index = _lire("index.html")
    i = index.index('data-i18n="nr.lbl"')
    bloc = index[i:index.index("</section>", i)]
    cartes = len(re.findall(r'<div class="nc nc-(?:lie|ext)', bloc))
    assert len(c.NORMES) == c.NORMES_ANNONCEES, (
        "le module déclare %d normes et en annonce %d"
        % (len(c.NORMES), c.NORMES_ANNONCEES))
    assert cartes == c.NORMES_ANNONCEES, (
        "la page d'accueil montre %d normes, le module en annonce %d"
        % (cartes, c.NORMES_ANNONCEES))
    titre = re.search(r'data-i18n="nr\.ttl">(\d+) normes', bloc)
    assert titre, "le titre de la grille n'annonce plus un nombre de normes"
    assert int(titre.group(1)) == c.NORMES_ANNONCEES, (
        "le titre annonce %s normes, la grille en montre %d"
        % (titre.group(1), cartes))


def test_chaque_taux_dit_ce_que_CENT_POUR_CENT_NE_VEUT_PAS_DIRE():
    """LA PHRASE QUI EMPÊCHE DE LIRE UN TAUX COMME UNE ATTESTATION.

    « 80 % » sur l'ISO 42001 veut dire « prêt aux quatre cinquièmes pour un
    audit » ; « 80 % » sur le NIST AI RMF ne veut rien dire de tel, puisque ce
    cadre n'est pas certifiable — il n'y a aucun auditeur au bout. Neuf
    pourcentages alignés se lisent pourtant comme neuf fois la même chose. La
    seule chose qui l'empêche est cette phrase-là, et elle doit exister pour
    chacune des cinq natures.
    """
    for cle, nat in c.NATURES.items():
        assert nat.get("cent_ne_veut_pas_dire"), (
            "la nature %r ne dit pas ce que 100 %% NE veut pas dire" % cle)
        assert len(nat["cent_ne_veut_pas_dire"]) > 40, cle


def test_le_cadre_NON_CERTIFIABLE_refuse_le_mot_conformite(etat):
    """LE NIST AI RMF N'EST PAS CERTIFIABLE, et son propre module le déclare.
    Un taux présenté comme une « conformité » sur ce cadre serait une faute
    devant un client comme devant un assureur — et c'est précisément le genre
    de raccourci qu'un tableau de bord encourage."""
    n = _norme(etat, "nist_ai_rmf")
    assert n["nature"] == "cadre", n["nature"]
    assert "couverture" in (n["taux_dit"] or ""), n["taux_dit"]
    assert "certifiable" in n["cent_ne_veut_pas_dire"].lower()
    ev = _nist.evaluer(_dossier()["nist_ai_rmf"])
    assert ev["certifiable"] is False, (
        "le module NIST se dit certifiable : l'une des deux sources ment")


def test_DORA_a_un_taux_ET_dit_ce_que_ce_taux_NE_COUVRE_PAS(etat):
    """LA RÈGLE RETOURNÉE, ET C'EST UN GAIN DE MESURE.

    Elle disait « DORA n'a pas de taux, et ce n'est pas zéro » — vrai tant
    qu'aucun module ne l'évaluait. Les quatre moteurs `dora*.py` l'évaluent ;
    la règle mesure donc l'inverse, et surtout ce qui n'a PAS changé avec le
    branchement : un taux affiché est lu comme s'il couvrait tout le
    règlement, et il n'en couvre que deux chapitres. La réserve permanente
    `hors_taux` est ce qui l'empêche, et elle doit voyager AVEC le nombre.
    """
    d = _norme(etat, "dora")
    assert d["nature"] == "obligation", d["nature"]
    assert d["renseigne"] is True
    assert isinstance(d["taux"], int) and 0 < d["taux"] < 100, d["taux"]
    assert {x["cle"] for x in d["composants"]} == {"cadre", "tiers"}
    assert d["panneau"] == "dora-qualifier", (
        "un taux qui ne mène pas à l'écran où on le corrige est un reproche")
    portees = {r["cle"] for r in d["reserves"]}
    assert "hors_taux" in portees, (
        "le taux DORA s'affiche sans dire qu'il ne couvre ni la chaîne de "
        "notification, ni les tests, ni le registre d'informations : %s"
        % sorted(portees))


def test_DORA_sans_regime_ne_peut_PAS_mesurer_son_cadre():
    """LE RÉGIME COMMANDE, ET SON ABSENCE SE DIT PLUTÔT QUE DE SE COMBLER.

    Un prestataire tiers de services TIC est dans le champ du règlement sans
    avoir de régime — les chapitres II à IV ne lui sont pas opposables. Lui
    rendre un taux de cadre reviendrait à lui prêter les devoirs de son
    client. La part reste donc vide, et la réserve NOMME la raison."""
    r = c.etat_des_lieux({"dora": {"entite": "prestataire_tic",
                                   "identifiee_nis2": True}})
    d = _norme(r, "dora")
    cadre = [x for x in d["composants"] if x["cle"] == "cadre"][0]
    assert cadre["taux"] is None, (
        "un prestataire tiers reçoit un taux de cadre : %r" % cadre["taux"])
    assert "regime_absent" in {x["cle"] for x in d["reserves"]}, (
        "la part « cadre » est vide sans que rien ne dise pourquoi")


def test_une_norme_JAMAIS_renseignee_ne_rend_pas_zero():
    """UN TAUX DE 0 % SE LIT COMME UN CONSTAT ACCABLANT ; « — » se lit comme
    « nous n'avons pas regardé ». La différence décide de la réunion."""
    r = c.etat_des_lieux({})
    for n in r["normes"]:
        assert n["taux"] is None, (
            "%s rend %r sans qu'aucune déclaration n'ait été faite"
            % (n["cle"], n["taux"]))
        assert n["renseigne"] is False


def test_tout_taux_reste_entre_zero_et_cent(etat):
    for n in etat["normes"]:
        if n["taux"] is None:
            continue
        assert 0 <= n["taux"] <= 100, (n["cle"], n["taux"])
        assert 0 <= n["plafond"] <= 100, (n["cle"], n["plafond"])


# ══════════════════════════════════════════════════════════════════════════
#  2. LE VERROU PLAFONNE — ET LA RÉSERVE NE PLAFONNE PAS
# ══════════════════════════════════════════════════════════════════════════

def test_un_verrou_PLAFONNE_le_taux_sans_effacer_le_travail(etat):
    """« UN ORGANISME À 90 % DE MATURITÉ AVEC UNE DÉCLARATION IRRECEVABLE
    N'EST PAS PRESQUE PRÊT, IL EST ARRÊTÉ » — c'est le module ISO 42001 de ce
    dépôt qui l'écrit. Le taux doit donc être le plus petit du brut et du
    plafond : ni le brut seul, qui fait croire la porte ouverte, ni zéro, qui
    jetterait le travail fait.
    """
    n = _norme(etat, "iso42001")
    assert n["verrous"], "le dossier de banc n'a plus de verrou ISO 42001 : " \
                         "cette règle ne mesure plus rien"
    assert n["plafond"] < 100
    assert n["taux"] == min(n["brut"], n["plafond"]), (
        "taux %r ≠ min(brut %r, plafond %r)"
        % (n["taux"], n["brut"], n["plafond"]))
    assert n["taux"] > 0, (
        "le verrou a effacé le travail au lieu de le plafonner")


def test_le_plafond_est_la_part_NON_bloquee_et_se_recalcule(etat):
    """LE PLAFOND N'EST PAS UN NOMBRE CHOISI : c'est la somme des poids que le
    verrou ne bloque pas. Écrit à la main, il se désynchroniserait du jour où
    un composant change de poids."""
    for n in etat["normes"]:
        if not n["verrous"]:
            continue
        comp = c.COMPOSITIONS[n["cle"]]
        total = sum(x["poids"] for x in comp)
        bloques = set()
        for v in n["verrous"]:
            bloques |= set(v["bloque"])
        libres = sum(x["poids"] for x in comp if x["cle"] not in bloques)
        attendu = int(round(100.0 * libres / total))
        assert n["plafond"] == attendu, (
            "%s : plafond %d, part non bloquée %d %%"
            % (n["cle"], n["plafond"], attendu))


def test_un_VERROU_n_existe_que_la_ou_un_TIERS_refuse_de_poursuivre():
    """LA LIGNE QUI SÉPARE UN VERROU D'UNE RÉSERVE, ET ELLE EST VÉRIFIABLE.

    Trois « verrous » ont d'abord été écrits dans ce module avant d'être
    reconnus pour autre chose : ils bloquaient TOUS les composants de leur
    norme, donc imposaient un plafond de zéro. Un taux toujours nul n'est pas
    un plafond, c'est un effacement.

    Un verrou existe là où un tiers refuse d'aller plus loin — l'auditeur qui
    s'arrête sur une déclaration irrecevable. Ne pas savoir si l'on est entité
    essentielle ou importante n'est pas une porte fermée : les dix mesures
    sont le même plancher dans les deux régimes.
    """
    for cle in c.VERROUS:
        assert c.NORMES_PAR_CLE[cle]["nature"] == "certifiable", (
            "%s porte un verrou sans être certifiable : sans auditeur au "
            "bout, ce n'est pas un verrou mais une réserve" % cle)
    for cle, verrous in c.VERROUS.items():
        total = sum(x["poids"] for x in c.COMPOSITIONS[cle])
        for v in verrous:
            bloque = sum(x["poids"] for x in c.COMPOSITIONS[cle]
                         if x["cle"] in set(v["bloque"]))
            assert 0 < bloque < total, (
                "%s/%s bloque %d des %d points de poids : un verrou qui "
                "bloque tout efface, il ne plafonne pas"
                % (cle, v["cle"], bloque, total))


def test_une_reserve_ne_DEPLACE_pas_le_taux_mais_en_fixe_le_SENS():
    """LE CRA SUPPOSE « FABRICANT » QUAND LE RÔLE N'EST PAS DIT, et c'est le
    bon défaut — c'est le rôle le plus chargé. Mais le taux porte alors une
    hypothèse, et il doit le dire. Une première version lisait le rôle dans le
    RÉSULTAT, toujours rempli : la réserve n'est jamais tombée, et l'écran
    promettait un taux sans dire contre quoi il était calculé.
    """
    dec = {"cra": {"nom": "P", "marche_ue": True,
                   "ecarts": {"ei-01": "conforme"}}}
    sans = _norme(c.etat_des_lieux(dec), "cra")
    dec["cra"]["role"] = "fabricant"
    avec = _norme(c.etat_des_lieux(dec), "cra")
    assert [r["cle"] for r in sans["reserves"]] == ["role_absent"]
    assert avec["reserves"] == []
    assert sans["taux"] == avec["taux"], (
        "la réserve a déplacé le taux : elle en fixe le sens, elle ne le "
        "corrige pas (%r vs %r)" % (sans["taux"], avec["taux"]))
    assert sans["reserves"][0]["porte_sur"], (
        "la réserve ne délimite pas ce qu'elle met en doute : le lecteur "
        "doutera de tout le taux, ou de rien")


# ══════════════════════════════════════════════════════════════════════════
#  3. LE PLUS BAS COMMANDE — LA MOYENNE NE COMMANDE PAS
# ══════════════════════════════════════════════════════════════════════════

def test_le_consolide_est_le_MINIMUM_et_pas_la_moyenne(etat):
    """DEUX CADRES À 90 % ET UN À 30 % RENDENT 70 % EN MOYENNE, et le 30 % —
    le seul qui décide de quelque chose — disparaît de la vue. L'aide de
    l'écran de ce dépôt disait déjà « traitez d'abord la composante la plus
    basse, c'est elle qui tire l'indice vers le bas » ; c'était faux de
    l'indice affiché, puisqu'une moyenne dilue au lieu de se laisser tirer.
    """
    mesures = [n["taux"] for n in etat["normes"]
               if n["taux"] is not None and n["renseigne"]]
    cons = etat["consolide"]
    assert cons["commande"] == min(mesures), (
        "le consolidé rend %r, le plus bas des taux est %r"
        % (cons["commande"], min(mesures)))
    moyenne = int(round(sum(mesures) / float(len(mesures))))
    assert cons["moyenne"] == moyenne
    assert cons["commande"] <= cons["moyenne"]
    assert cons["qui"], "le consolidé ne dit pas QUELLE norme commande"
    assert cons["avertissement"], (
        "la moyenne est rendue sans l'avertissement qui dit qu'elle "
        "n'additionne pas des natures comparables")


def test_l_ecran_applique_la_MEME_regle_que_le_serveur():
    """DEUX VÉRITÉS SUR LE MÊME INDICE SERAIT LE DÉFAUT À NE PAS REFAIRE. La
    fonction de l'écran qui consolide les trois cadres historiques doit, elle
    aussi, rendre le minimum — et nommer la moyenne à côté."""
    # ON DÉCOUPE SUR LES DEUX AFFECTATIONS, PAS SUR UN NOMBRE DE CARACTÈRES.
    # Une première version lisait « les 900 caractères qui suivent » et
    # tombait dès qu'on ajoutait un commentaire au-dessus du calcul : la
    # règle mesurait la longueur du commentaire, pas la formule.
    i = PAGEJS.index("var vals=[ia,rg,iso]")
    j = PAGEJS.index("function fw(", i)
    bloc = PAGEJS[i:j]
    assert "Math.min.apply" in bloc, (
        "l'indice de l'écran est encore une moyenne alors que le serveur "
        "rend le minimum")
    assert "var moy" in bloc, "la moyenne a disparu au lieu d'être nommée"
    assert "var g = vals.length ? Math.min" in bloc, (
        "l'indice mis en avant n'est pas le minimum")


def test_le_MEME_audit_ne_donne_pas_deux_pourcentages_selon_l_ecran():
    """LE DÉFAUT MESURÉ, ET CORRIGÉ. `auditUpdateScore`, sur la page de
    l'audit, compte un point partiel pour une moitié ; `gcAuditPct`, qui
    alimente l'indice de conformité, ne comptait que les points « done » et
    jetait les partiels. Un utilisateur qui cochait « partiellement » voyait
    son score monter d'un côté et pas de l'autre.
    """
    def _bloc(nom):
        i = PAGEJS.index(nom)
        return PAGEJS[i:PAGEJS.index("\n};", i) if "\n};" in PAGEJS[i:i + 2000]
                      else i + 1200]
    a = _bloc("window.gcAuditPct = function()")
    b = _bloc("function auditUpdateScore()")
    for nom, bloc in (("gcAuditPct", a), ("auditUpdateScore", b)):
        assert "'partial'" in bloc, (
            "%s ne regarde pas les points partiels" % nom)
        assert "0.5" in bloc, (
            "%s ne compte pas un point partiel pour une moitié" % nom)


def test_le_serveur_compte_AUSSI_le_point_partiel_pour_une_moitie():
    """LA TROISIÈME SURFACE. Deux écrans d'accord entre eux et un serveur qui
    compterait autrement rendrait le défaut au premier rafraîchissement."""
    pts = [p[0] for p in c.AUDIT_IA_ACT if p[4] == "p1"]
    tout_tenu = c.etat_des_lieux({"ia_act": {k: "tenu" for k in pts}})
    tout_partiel = c.etat_des_lieux({"ia_act": {k: "partiel" for k in pts}})
    p1_tenu = [x for x in _norme(tout_tenu, "ia_act")["composants"]
               if x["cle"] == "p1"][0]["taux"]
    p1_partiel = [x for x in _norme(tout_partiel, "ia_act")["composants"]
                  if x["cle"] == "p1"][0]["taux"]
    assert p1_tenu == 100, p1_tenu
    assert p1_partiel == 50, (
        "un point partiel vaut %r %% au serveur, une moitié aux deux écrans"
        % p1_partiel)


# ══════════════════════════════════════════════════════════════════════════
#  4. UNE CASE VIDE N'EST PAS UNE CASE VERTE
# ══════════════════════════════════════════════════════════════════════════

def test_une_part_non_renseignee_compte_pour_ZERO_et_pas_pour_RIEN():
    """LA SORTIR DU DÉNOMINATEUR FERAIT MONTER LE TAUX À MESURE QU'ON
    RENSEIGNE MOINS DE CHOSES — le pire réglage possible, puisqu'il récompense
    l'ignorance. On le mesure en retirant une part : le taux doit BAISSER.
    """
    complet = {cat["cle"]: "prouve" for cat in _nist.CATEGORIES}
    partiel = {k: v for k, v in complet.items()
               if not k.startswith("MANAGE")}
    plein = _norme(c.etat_des_lieux({"nist_ai_rmf": complet}), "nist_ai_rmf")
    creux = _norme(c.etat_des_lieux({"nist_ai_rmf": partiel}), "nist_ai_rmf")
    assert plein["taux"] == 100, plein["taux"]
    assert creux["taux"] < plein["taux"], (
        "retirer une fonction entière n'a pas fait baisser le taux : les "
        "parts muettes sont sorties du dénominateur")


def test_la_couverture_d_un_cadre_compte_les_categories_JAMAIS_OUVERTES():
    """LA NOTE DU MODULE NIST EST UNE MOYENNE SUR LES SEULES CATÉGORIES
    RENSEIGNÉES, et c'est juste pour ce qu'elle mesure — le niveau de ce qu'on
    a regardé. Ce n'est PAS une couverture. Mesuré : une seule catégorie sur
    six déclarée « prouvé » rendait 100 %, alors que cinq sixièmes n'avaient
    jamais été ouverts.
    """
    une = [cat["cle"] for cat in _nist.CATEGORIES
           if cat["fonction"] == "GOVERN"][0]
    n = _norme(c.etat_des_lieux({"nist_ai_rmf": {une: "prouve"}}),
               "nist_ai_rmf")
    govern = [x for x in n["composants"] if x["cle"] == "govern"][0]
    total = len([cat for cat in _nist.CATEGORIES
                 if cat["fonction"] == "GOVERN"])
    assert govern["taux"] == int(round(100.0 / total)), (
        "une catégorie sur %d déclarée « prouvé » rend %r %% de couverture"
        % (total, govern["taux"]))


# ══════════════════════════════════════════════════════════════════════════
#  5. LE PLAN MÈNE OÙ IL DIT QU'IL MÈNE
# ══════════════════════════════════════════════════════════════════════════

def test_les_gains_annonces_MENENT_au_plafond_et_jamais_au_dela(etat):
    """LE CONTRÔLE QUI DÉCIDE DE TOUT LE RESTE.

    Les gains ne sont pas indépendants : deux actions qui touchent le même
    composant se partagent le même chemin restant. Calculés séparément puis
    additionnés, ils menaient le Top 10 OWASP à 102 % — le plan promettait
    plus qu'il n'existe. Ils sont donc calculés À LA SUITE, et leur somme doit
    se télescoper exactement jusqu'au plafond de chaque norme.
    """
    for n in etat["normes"]:
        if n["taux"] is None:
            continue
        somme = n["taux"] + sum(
            g["gain"] for a in etat["plan"]["actions"] for g in a["gains"]
            if g["norme"] == n["cle"] and not a.get("leve_un_verrou"))
        assert somme == n["plafond"], (
            "%s : %d %% aujourd'hui + les gains du plan = %d %%, alors que "
            "le plafond est à %d %%"
            % (n["cle"], n["taux"], somme, n["plafond"]))


def test_aucune_action_ne_promet_un_gain_qui_depasse_le_plafond(etat):
    for a in etat["plan"]["actions"]:
        # L'ACTION QUI LÈVE UN VERROU EST CELLE DONT LE MÉTIER EST DE FAIRE
        # SAUTER LE PLAFOND : lui appliquer la règle reviendrait à lui
        # interdire d'être utile. Elle annonce donc le brut, et c'est exact.
        if a.get("leve_un_verrou"):
            for g in a["gains"]:
                assert g.get("plafond_a") == 100, a["cle"]
            continue
        for g in a["gains"]:
            if g.get("a") is None:
                continue
            n = _norme(etat, g["norme"])
            assert g["a"] <= n["plafond"], (
                "l'action %s mène %s à %d %% alors que son plafond est %d %%"
                % (a["cle"], g["norme"], g["a"], n["plafond"]))


def test_les_verrous_passent_AVANT_tout_le_reste(etat):
    """TANT QU'UN VERROU TIENT, TOUT LE RESTE BUTE SUR LE MÊME PLAFOND. Ce
    n'est pas une préférence de méthode, c'est de l'arithmétique — et le plan
    doit les ranger en premier même s'ils ne rapportent aucun point
    aujourd'hui."""
    rangs = [a["rang"] for a in etat["plan"]["actions"]]
    assert rangs == sorted(rangs), "le plan n'est pas ordonné par rang"
    verrous = [a for a in etat["plan"]["actions"] if a.get("leve_un_verrou")]
    assert verrous, "le dossier de banc ne porte plus de verrou"
    for a in verrous:
        assert a["rang"] == 1, a["cle"]
        assert a["plafond_gagne"] > 0, (
            "l'action de verrou %s n'annonce aucun plafond gagné : elle se "
            "lit alors comme inutile alors qu'elle est la seule à pouvoir "
            "rendre les autres payantes" % a["cle"])


def test_un_gain_nul_dit_POURQUOI_il_est_nul(etat):
    """UN « +0 » A DEUX CAUSES TRÈS DIFFÉRENTES : il n'y avait rien à gagner,
    ou le verrou confisque ce qui aurait été gagné. Les afficher pareil fait
    passer un travail utile pour un travail inutile."""
    for a in etat["plan"]["actions"]:
        for g in a["gains"]:
            if g["gain"]:
                continue
            assert g.get("dit") or "confisque" in g, (
                "l'action %s annonce un gain nul sur %s sans dire pourquoi"
                % (a["cle"], g["norme"]))


def test_les_actions_a_DOUBLE_EFFET_ne_citent_que_des_ponts_DECLARES(etat):
    """LE SEUL VRAI BÉNÉFICE À TENIR NEUF RÉFÉRENTIELS AU MÊME ENDROIT, et la
    seule façon de le rendre défendable : un rapprochement inventé ici ne
    serait reconnu ni par l'auditeur 27001 ni par l'autorité NIS 2.
    """
    connus = set()
    for cle_nis, _nom, mesures in _i27.NIS2_VERS_ANNEXE_A:
        connus.add("nis2_" + cle_nis)
    for cle_llm in (_ow.pont_42001().get("rencontres") or {}):
        connus.add("owasp_" + cle_llm)
    doubles = [a for a in etat["plan"]["actions"]
               if a["rang"] == 2 and len(a["normes"]) > 1]
    assert doubles, (
        "aucune action ne sert deux normes : le pont ne rapporte rien, ou "
        "le dossier de banc ne le sollicite plus")
    for a in (x for x in etat["plan"]["actions"] if x["rang"] == 2):
        assert a["cle"] in connus, (
            "l'action %s invente un rapprochement entre référentiels"
            % a["cle"])


def test_chaque_action_dit_OU_elle_se_traite(etat):
    """UNE ACTION SANS DESTINATION EST UN REPROCHE, PAS UN PLAN."""
    for a in etat["plan"]["actions"]:
        assert a.get("ou"), "l'action %s ne dit pas où elle se traite" % a["cle"]


def test_chaque_taux_MENE_a_l_ecran_ou_on_le_corrige(etat):
    """MÊME RÈGLE, CÔTÉ TAUX. Les panneaux visés doivent exister dans
    sentinel.html — un lien mort renvoie le lecteur nulle part, et c'est pire
    que pas de lien."""
    for n in etat["normes"]:
        if n["nature"] == "sans_instrument":
            assert not n["panneau"]
            continue
        assert n["panneau"], "%s ne mène à aucun écran" % n["cle"]
        assert ('id="p-%s"' % n["panneau"]) in SENTINEL, (
            "%s renvoie au panneau %s, qui n'existe pas"
            % (n["cle"], n["panneau"]))


def test_un_composant_a_CENT_POUR_CENT_ne_porte_plus_aucun_ecart(etat):
    """LE TAUX ET LES ÉCARTS DOIVENT LIRE LA MÊME CHOSE.

    Ils ne la lisaient pas : le taux d'une déclaration d'applicabilité était
    calculé par le module, qui reconnaît l'état « conforme », pendant que
    l'extracteur d'écarts cherchait « oui ». Une mesure réellement mise en
    œuvre comptait dans le taux ET restait dans le plan — qui réclamait donc
    un travail déjà fait.

    Le défaut a survécu parce que le dossier d'essai ne portait AUCUNE mesure
    en œuvre : les deux côtés étaient faux de la même façon, donc d'accord.
    Cette règle les confronte composant par composant.
    """
    for n in etat["normes"]:
        if n["taux"] is None or not n["ecarts"]:
            continue
        ouverts = {}
        for a in etat["plan"]["actions"]:
            if a.get("composant") and n["cle"] in a["normes"]:
                ouverts[a["composant"]] = ouverts.get(a["composant"], 0) \
                    + a["combien"]
        for comp in n["composants"]:
            if comp["taux"] == 100:
                assert not ouverts.get(comp["cle"]), (
                    "%s/%s est à 100 %% et le plan y réclame encore %d "
                    "action(s) : le taux et les écarts ne lisent pas la "
                    "même chose"
                    % (n["cle"], comp["cle"], ouverts[comp["cle"]]))


# ══════════════════════════════════════════════════════════════════════════
#  6. CE QUE LE PLAN NE PEUT PAS FAIRE
# ══════════════════════════════════════════════════════════════════════════

def test_le_plan_DIT_ce_qu_il_ne_peut_pas_faire(etat):
    """LA MOITIÉ QU'ON NE MONTRE JAMAIS. Un plan qui promet 100 % sur les onze
    ment sur plusieurs points connus d'avance ; les taire ne les supprime
    pas, cela les fait découvrir devant l'auditeur.

    LES TROIS LIMITES DORA ONT REMPLACÉ « SANS INSTRUMENT » — la limite s'est
    déplacée avec le branchement au lieu de disparaître avec lui : ce n'est
    plus l'absence de mesure, c'est la PORTÉE de ce qui est mesuré."""
    cles = {l["cle"] for l in etat["limites"]}
    assert "dora_hors_taux" in cles
    assert "dora_tlpt_autorites" in cles
    assert "dora_nis2_ne_se_presume_pas" in cles
    assert "dora_sans_instrument" not in cles, (
        "la limite « sans instrument » survit alors que DORA a ses moteurs")
    assert "nist_non_certifiable" in cles
    assert "owasp_hors_annexe_a" in cles
    for l in etat["limites"]:
        assert l["quoi"] and l["pourquoi"] and l["quoi_faire"], l["cle"]


def test_les_risques_hors_annexe_A_sont_ceux_que_le_module_OWASP_declare(etat):
    """TROIS RISQUES DU TOP 10 NE RENCONTRENT AUCUNE MESURE DE L'ANNEXE A
    42001. Les nommer de mémoire ici les figerait ; on les redemande au module
    qui les tient."""
    hors = (_ow.pont_42001() or {}).get("hors_portee") or []
    assert hors, "le pont ne déclare plus aucun risque hors portée"
    lim = [l for l in etat["limites"] if l["cle"] == "owasp_hors_annexe_a"][0]
    for cle in hors:
        assert cle in lim["quoi"], (
            "%s est hors de l'annexe A mais la limite ne le nomme pas" % cle)


def test_cent_pour_cent_sur_une_norme_certifiable_ne_vaut_PAS_certificat():
    """IL RESTE L'AUDIT INTERNE, LA REVUE DE DIRECTION ET L'ORGANISME
    ACCRÉDITÉ. Aucune case cochée ici ne remplace ces trois-là, et c'est au
    moment où le taux atteint 100 % que la confusion est la plus probable."""
    # LA RÈGLE NE SE DÉROBE PAS. Une première version s'arrêtait avec un
    # `skip` quand le dossier n'atteignait pas 100 % — c'est-à-dire qu'elle
    # ne mesurait rien tout en passant au vert. On construit donc un dossier
    # COMPLET, et on vérifie d'abord qu'il atteint bien 100 %.
    dec = {"iso42001": {
        "nom": "Complet",
        "articles": {n: "conforme" for ch in _i42.CHAPITRES
                     for n, *_ in ch[2]},
        "mesures": {m[0]: {"decision": "retenue", "justification": "SoA",
                           "mise_en_oeuvre": "conforme"}
                    for obj in _i42.ANNEXE_A for m in obj[3]}}}
    r = c.etat_des_lieux(dec)
    n = _norme(r, "iso42001")
    assert n["taux"] == 100, (
        "le dossier complet n'atteint que %r %% : la règle ne peut plus "
        "éprouver ce qui se passe À 100 %%" % n["taux"])
    assert n["ecarts"] == 0, (
        "un dossier à 100 %% porte encore %d écart(s) : le taux et les "
        "écarts ne lisent pas la même chose" % n["ecarts"])
    lim = [l for l in r["limites"] if l["cle"] == "audit_reel"]
    assert lim, "100 % atteint sans rappeler qu'il reste l'audit réel"
    assert "audit interne" in lim[0]["pourquoi"]
    assert "accrédité" in lim[0]["pourquoi"]


# ══════════════════════════════════════════════════════════════════════════
#  7. LE RÉFÉRENTIEL DE L'AUDIT IA ACT, ÉCRIT DEUX FOIS
# ══════════════════════════════════════════════════════════════════════════

def test_l_audit_IA_ACT_du_Python_et_du_JavaScript_sont_IDENTIQUES():
    """LA DUPLICATION QUI NUIT EST CELLE QUE PERSONNE NE VÉRIFIE.

    Les points de l'audit vivent dans `conformite.py` et dans
    `sentinel.page.js`. Ce dépôt refuse d'ordinaire ce genre de double
    écriture — le titre des « neuf normes maîtrisées » vient d'être corrigé
    pour cette raison exacte. Ce qui la rend acceptable ici est CETTE
    RÈGLE : identifiants, section et priorité sont comparés un par un, et la
    moindre divergence tombe.
    """
    i = PAGEJS.index("var AUDIT_SECTIONS = [")
    bloc = PAGEJS[i:PAGEJS.index("window.AUDIT_SECTIONS", i)]
    secs = [m.group(1) for m in
            re.finditer(r"\{\s*id:'([a-z0-9_]+)', title:'(?:[^'\\]|\\.)*', "
                        r"art:'", bloc)]
    assert secs == [s[0] for s in c.AUDIT_IA_ACT_SECTIONS], (
        "les sections diffèrent — JS %s, Python %s"
        % (secs, [s[0] for s in c.AUDIT_IA_ACT_SECTIONS]))

    points_js = []
    for k, sec in enumerate(secs):
        debut = bloc.index("id:'%s', title:" % sec)
        fin = (bloc.index("id:'%s', title:" % secs[k + 1])
               if k + 1 < len(secs) else len(bloc))
        for m in re.finditer(r"\{id:'([a-z0-9_]+)', title:'(?:[^'\\]|\\.)*'"
                             r".*?prio:'(p\d)'\}", bloc[debut:fin]):
            points_js.append((m.group(1), sec, m.group(2)))
    points_py = [(p[0], p[1], p[4]) for p in c.AUDIT_IA_ACT]
    assert points_js == points_py, (
        "l'audit IA Act a divergé entre le JavaScript (%d points) et le "
        "Python (%d points)" % (len(points_js), len(points_py)))


def test_la_lecture_du_JS_n_est_pas_vide():
    """LE GARDE-FOU DE LA RÈGLE PRÉCÉDENTE. Une extraction qui rendrait zéro
    point ferait passer la comparaison pour une comparaison de vides — c'est
    arrivé une fois dans ce dépôt, et la recette est restée verte."""
    assert len(c.AUDIT_IA_ACT) >= 30, len(c.AUDIT_IA_ACT)
    assert len(c.AUDIT_IA_ACT_SECTIONS) == 8


# ══════════════════════════════════════════════════════════════════════════
#  8. LES DEUX ROUTES, ET L'ÉCRAN
# ══════════════════════════════════════════════════════════════════════════

def test_les_routes_existent_et_rendent_les_neuf():
    from app import app as flask_app
    cl = flask_app.test_client()
    r = cl.get("/api/conformite/referentiel")
    assert r.status_code == 200
    j = r.get_json()
    assert len(j["normes"]) == len(c.NORMES)
    assert j["audit_ia_act"]["points"], "le référentiel ne sert pas l'audit"
    r2 = cl.post("/api/conformite/etat-des-lieux",
                 json={"declarations": _dossier()})
    assert r2.status_code == 200
    j2 = r2.get_json()
    assert len(j2["normes"]) == len(c.NORMES)
    assert j2["plan"]["total"] > 0
    assert j2["limites"]


def test_l_ecran_ne_REFAIT_aucun_calcul():
    """TOUT LE CALCUL EST AU SERVEUR, et refaire ici la moindre arithmétique
    donnerait deux vérités sur le même taux — le défaut que ce module passe
    son temps à corriger ailleurs."""
    i = PAGEJS.index("function confRendre()")
    bloc = PAGEJS[i:PAGEJS.index("\n}", PAGEJS.index("conf-limites-corps", i))]
    for interdit in ("Math.round", "Math.min", "reduce("):
        assert interdit not in bloc, (
            "le rendu recalcule (%r trouvé) : le taux affiché pourrait "
            "différer du taux servi" % interdit)


def test_l_ecran_CONSTRUIT_la_phrase_qui_dit_ce_que_cent_ne_veut_pas_dire():
    """RELÉGUÉE EN BAS DE PAGE, la phrase s'applique à un chiffre qu'on ne
    regarde plus. Elle doit donc être sur la carte.

    CE QUE CETTE RÈGLE MESURE VRAIMENT, ET CE QU'ELLE NE MESURE PAS. Elle lit
    la SOURCE : que le champ soit lu, qu'il produise le bloc `conf-c-cent`, et
    que ce bloc soit concaténé dans la carte rendue. Elle ne peut pas voir le
    résultat à l'écran — c'est la recette navigateur qui s'en charge, et une
    mutation qui neutraliserait la condition sans toucher au texte lui
    échapperait ici. Les deux se tiennent, et aucune ne remplace l'autre.
    """
    i = PAGEJS.index("function confRendre()")
    bloc = PAGEJS[i:i + 6000]
    assert "n.cent_ne_veut_pas_dire" in bloc, (
        "le rendu ne lit plus le champ")
    assert "conf-c-cent" in bloc, "le bloc dédié a disparu"
    assert "+ cent" in bloc, (
        "la phrase est construite mais jamais ajoutée à la carte")


def test_le_tiroir_et_ses_trois_ecrans_existent():
    # ON CHERCHE LA SECTION, PAS L'ATTRIBUT. Les trois entrées du tiroir
    # portent le même `data-grp` : une règle qui se contentait de l'attribut
    # restait verte quand la SECTION — la seule chose qui rend le tiroir
    # visible et repliable — changeait de nom.
    assert ('<div class="sb-section sb-pliable" data-grp="taux-conformite" '
            'data-fam="conformite"') in SENTINEL, (
        "le tiroir « taux de conformité » n'est plus une section de la "
        "famille conformité : ses trois écrans deviennent inatteignables")
    for pid in ("conf-taux", "conf-plan", "conf-limites"):
        assert ('id="p-%s"' % pid) in SENTINEL, pid
        assert ("go('%s'" % pid) in SENTINEL, (
            "%s n'est atteignable par aucune entrée de la barre latérale"
            % pid)
