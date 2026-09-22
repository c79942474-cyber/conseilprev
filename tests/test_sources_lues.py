# -*- coding: utf-8 -*-
"""CE QU'UN MODULE A LU, ET CE QU'IL SE CONTENTE DE CITER.

LE DÉFAUT, ET IL EST ARRIVÉ PAR UN FICHIER VIDE. Le catalogue NIST SP 800-53
Rev. 4 a été demandé au cabinet. Le fichier joint — `NIST.SP.800-53r4.docx` —
est arrivé SANS CONTENU. Le module qui porte son nom a donc été bâti sur une
autre publication : SP 800-82 Rev. 2, qui énumère les dix-huit familles à son
§6.2 pour les besoins de sa propre surcharge industrielle.

CE QUE LE REGISTRE DISAIT. Les deux publications y figuraient de la même
façon : même forme, même date, même DOI. Rien ne séparait celle qu'on avait
lue de celle qu'on n'avait jamais ouverte. Un lecteur de
`/api/nist53/referentiel` en concluait raisonnablement que les deux avaient
été consultées.

CITER N'EST PAS UNE FAUTE. Nommer le référentiel qu'on vise est souvent
nécessaire : c'est lui qui donne son nom à ce qu'on mesure, et c'est lui que
l'auditeur reconnaîtra. Laisser croire qu'on l'a lu en est une — et c'est
exactement la classe de défaut que ce dépôt traque partout ailleurs : une
affirmation vraie en apparence, fausse dans ce qu'elle laisse entendre.

CE QUE CES RÈGLES IMPOSENT, À TOUS LES MODULES ET PAS SEULEMENT À CELUI-LÀ :
deux champs par source — ce qu'elle a APPORTÉ, et si elle a été LUE. Elles
s'appliquent à tout module qui déclare un registre, présent ou à venir.
"""
import importlib
import io
import os
import re

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _modules_a_registre():
    """Les modules qui déclarent un registre de sources, lus sur le disque.

    ON NE TIENT PAS DE LISTE À LA MAIN. Un douzième module arriverait sans
    que personne ne pense à ce fichier — et c'est justement un registre
    oublié qui a produit le défaut."""
    out = []
    for nom in sorted(os.listdir(_RACINE)):
        if not nom.endswith(".py") or nom.startswith("test_"):
            continue
        chemin = os.path.join(_RACINE, nom)
        if not os.path.isfile(chemin):
            continue
        txt = io.open(chemin, encoding="utf-8").read()
        if re.search(r"^SOURCES = \(", txt, re.M):
            out.append(nom[:-3])
    return out


MODULES = _modules_a_registre()


def test_on_a_bien_trouve_des_registres_de_sources():
    """LE GARDE-FOU DE TOUT CE FICHIER. Si la lecture cessait de trouver des
    registres, les règles paramétrées ci-dessous ne s'exécuteraient sur
    RIEN — et passeraient toutes, en silence."""
    assert len(MODULES) >= 5, (
        "%d module(s) à registre relevé(s) : la lecture a changé de forme, "
        "et les règles suivantes ne mesurent plus rien — %s"
        % (len(MODULES), MODULES))


@pytest.mark.parametrize("nom", MODULES)
def test_CHAQUE_source_dit_ce_qu_elle_a_apporte(nom):
    """UNE SOURCE SANS APPORT DÉCLARÉ EST UNE SOURCE INVÉRIFIABLE. Le lecteur
    voit un titre et un identifiant ; il ne peut pas savoir si ce document a
    fourni quarante-deux articles ou seulement son nom."""
    m = importlib.import_module(nom)
    for s in m.SOURCES:
        apporte = s.get("apporte")
        assert apporte, (
            "%s : la source %r ne dit pas ce qu'elle a apporté — le lecteur "
            "ne peut pas savoir ce qui, dans ce module, en vient"
            % (nom, s.get("cle")))
        assert len(apporte) >= 40, (
            "%s : l'apport de %r tient en %d caractères (%r) — trop court "
            "pour dire quoi que ce soit de vérifiable"
            % (nom, s.get("cle"), len(apporte), apporte))


@pytest.mark.parametrize("nom", MODULES)
def test_CHAQUE_source_dit_si_elle_a_ete_LUE(nom):
    """`apporte` ET `lue` NE SE DÉDUISENT PAS L'UN DE L'AUTRE. On peut tirer
    beaucoup d'un texte qu'on cite sans l'avoir ouvert — le nom de ce qu'on
    mesure, par exemple. C'est précisément le cas de SP 800-53 Rev. 4."""
    m = importlib.import_module(nom)
    for s in m.SOURCES:
        assert "lue" in s, (
            "%s : la source %r ne dit pas si elle a été lue" % (nom, s.get("cle")))
        assert isinstance(s["lue"], bool), (
            "%s : `lue` de %r vaut %r — on attend un booléen, pas une nuance"
            % (nom, s.get("cle"), s["lue"]))


@pytest.mark.parametrize("nom", MODULES)
def test_un_module_ne_repose_PAS_uniquement_sur_du_non_lu(nom):
    """UN MODULE DONT AUCUNE SOURCE N'A ÉTÉ LUE NE MESURE RIEN. Il nomme des
    référentiels et invente le reste. La règle précédente accepte qu'une
    source soit citée sans être lue ; celle-ci interdit que ce soit le cas de
    TOUTES."""
    m = importlib.import_module(nom)
    lues = [s for s in m.SOURCES if s.get("lue")]
    assert lues, (
        "%s : aucune de ses %d source(s) n'a été lue — ce module ne repose "
        "sur rien de vérifiable" % (nom, len(m.SOURCES)))


@pytest.mark.parametrize("nom", MODULES)
def test_deux_sources_n_ont_pas_le_MEME_apport(nom):
    """UN APPORT RECOPIÉ D'UNE SOURCE À L'AUTRE NE DIT PLUS RIEN. C'est la
    forme que prendrait le retour du défaut : remplir le champ pour faire
    passer la règle, avec la même phrase partout."""
    m = importlib.import_module(nom)
    vus = {}
    for s in m.SOURCES:
        a = (s.get("apporte") or "").strip()
        assert a not in vus, (
            "%s : %r et %r déclarent le MÊME apport — au moins l'un des deux "
            "est faux" % (nom, vus.get(a), s.get("cle")))
        vus[a] = s.get("cle")


# ══════════════════════════════════════════════════════════════════════════
#  LE CAS QUI A RÉVÉLÉ LE DÉFAUT
# ══════════════════════════════════════════════════════════════════════════

def test_le_catalogue_800_53_est_declare_NON_LU():
    """LE FICHIER JOINT ÉTAIT VIDE, ET LE MODULE DOIT LE DIRE.

    Ce module porte le nom de SP 800-53 Rev. 4 et mesure contre lui — sans
    en avoir lu une page. Tant que ce sera vrai, le registre doit le dire ;
    le jour où le catalogue arrivera, cette règle tombera, et c'est ce qu'on
    veut : elle signalera qu'il faut reprendre la maille."""
    import nist_800_53 as m
    src = dict((s["cle"], s) for s in m.SOURCES)
    assert src["sp80053r4"]["lue"] is False, (
        "le catalogue 800-53 Rev. 4 est déclaré lu : s'il l'est désormais, "
        "ce module doit descendre à la maille de la MESURE, qu'il refuse "
        "aujourd'hui faute du document")
    assert src["sp80082r2"]["lue"] is True, (
        "SP 800-82 Rev. 2 n'est plus déclarée lue — or c'est d'elle que "
        "viennent les dix-huit familles de ce module")


def test_le_module_800_53_NE_PROMET_PAS_une_maille_qu_il_n_a_pas():
    """LA CONSÉQUENCE DU DOCUMENT MANQUANT, ET ELLE EST DÉJÀ ÉCRITE. Sans le
    catalogue, la répartition des mesures par socle ne s'invente pas : un
    pourcentage au dénominateur supposé vaudrait moins que son absence. Le
    module travaille donc par FAMILLE, et le dit.

    C'EST LE GARDE-FOU DE LA RÈGLE PRÉCÉDENTE : déclarer une source non lue
    ne suffit pas si l'écran, lui, promet une précision qu'elle n'autorise
    pas."""
    import nist_800_53 as m
    # LA MAILLE EST RENDUE PAR `evaluer`, avec le taux qu'elle borne : c'est
    # là qu'elle sert, et là qu'on la mesure — pas dans une constante qu'un
    # écran pourrait ne jamais lire.
    maille = (m.evaluer("moderate", {}) or {}).get("maille", "")
    assert "FAMILLE" in maille, (
        "le module ne dit plus travailler par famille : %r" % maille[:90])
    assert "dénominateur supposé" in maille, (
        "le module ne dit plus POURQUOI il s'arrête à la famille : %r"
        % maille[:90])


def test_l_ecran_MONTRE_le_registre_et_separe_les_deux_etats():
    """LE REGISTRE EXISTAIT ET N'ÉTAIT MONTRÉ NULLE PART. Il sortait dans
    `/api/nist53/referentiel`, et aucun écran ne l'affichait : un client
    lisant « NIST SP 800-53 Rev. 4 » en tête de son questionnaire n'avait
    aucun moyen de savoir ce qui en vient réellement.

    ET « lu » DOIT SE DISTINGUER DE « cité » SANS LIRE : un état qui ne se
    voit qu'en lisant la phrase ne sera pas vu."""
    js = io.open(os.path.join(_RACINE, "sentinel.page.js"),
                 encoding="utf-8").read()
    html = io.open(os.path.join(_RACINE, "sentinel.html"),
                   encoding="utf-8").read()
    assert "function nistSources(" in js, (
        "l'écran n'a plus de rendu du registre des sources")
    assert js.count("nistSources(") >= 3, (
        "le registre n'est rendu que sur %d écran(s) : les deux panneaux "
        "NIST doivent le montrer" % (js.count("nistSources(") - 1))
    assert re.search(r"s\.lue \? '' : ' non-lue'", js), (
        "l'écran ne distingue plus une source lue d'une source citée")
    assert re.search(r"s\.lue \? 'lu' : 'cité'", js), (
        "l'écran n'écrit plus l'état de la source en toutes lettres")
    assert "nistEsc(s.apporte" in js, (
        "l'écran n'affiche plus ce que la source a apporté — il ne reste "
        "qu'une liste de titres, ce qui était l'état du défaut")
    assert ".nist-src.non-lue .nist-src-etat{" in html, (
        "une source citée s'affiche comme une source lue : la différence ne "
        "se voit plus")
