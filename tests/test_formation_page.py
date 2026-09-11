# -*- coding: utf-8 -*-
"""La page publique /formation — mesurée sur ce qu'elle FAIT, pas sur sa présence.

CE QUE CES RÈGLES ÉPROUVENT. La page est surtout dynamique : elle peuple ses
sujets et son calendrier depuis /api/formation/referentiel, et poste une
inscription à /api/formation/inscription. Une règle qui se contenterait de
vérifier que le fichier existe passerait alors qu'aucun de ces deux fils ne
serait branché. On mesure donc les fils eux-mêmes :

  · la route /formation sert bien LE fichier de la fonctionnalité ;
  · la page appelle les DEUX routes de l'offre — sans quoi le formulaire est
    un formulaire mort, et le calendrier une liste vide ;
  · le corps posté porte le sujet, le créneau et les coordonnées que le serveur
    EXIGE — un contrat qui diverge se traduit par un 400 que rien n'annonce ;
  · le client N'ENVOIE AUCUN PRIX. C'est le cœur de l'offre : le tarif se décide
    au serveur (rang → gratuit puis 800 € HT), jamais sur parole du client. Une
    clé de prix dans le corps posté serait une porte pour le fixer soi-même ;
  · le prix ANNONCÉ sur la page est celui du module — pas un « 800 » écrit à la
    main qui survivrait à un changement de tarif, la faute déjà corrigée
    ailleurs sur le catalogue ;
  · la confirmation lit la DÉCISION du serveur (gratuit / montant), et ne
    recompose pas un prix de son côté ;
  · Sentinel CONDUIT à la page : sans le lien, l'offre n'est atteignable qu'en
    connaissant son adresse.

Ce que ces règles NE font pas : rendre la page dans un navigateur. Il n'y en a
pas ici. Elles lisent le fil, pas le pixel — et le fil est ce qui casse en
silence.
"""
import io
import os
import re

import pytest

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import app as A
import formations_ia as F

PAGE = io.open(os.path.join(RACINE, "formation.html"), encoding="utf-8").read()
SENTINEL = io.open(os.path.join(RACINE, "sentinel.html"), encoding="utf-8").read()


def _corps_inscription():
    """L'objet JSON réellement posté à /api/formation/inscription.

    On l'isole entre `JSON.stringify({` qui suit l'appel d'inscription et
    l'accolade fermante — pour ne mesurer QUE ce que le client envoie, et non
    ce qu'il lit ensuite dans la réponse (où « montant_cents » figure à bon
    droit)."""
    i = PAGE.index("/api/formation/inscription")
    j = PAGE.index("JSON.stringify({", i) + len("JSON.stringify({")
    k = PAGE.index("})", j)
    return PAGE[j:k]


def _cles_postees():
    return set(re.findall(r"(\w+)\s*:", _corps_inscription()))


# ══════════════════════════════════════════════════════════════════════════
# Le relevé lit bien la page — sans quoi tout le reste serait vert pour rien
# ══════════════════════════════════════════════════════════════════════════
def test_le_releve_trouve_bien_le_formulaire_et_le_corps_poste():
    """LE TÉMOIN. Si l'extraction se cassait, les règles suivantes passeraient
    sur des chaînes vides — le défaut « verte pour une raison sans rapport »."""
    assert 'id="formation-form"' in PAGE
    assert len(_corps_inscription()) > 40, "le corps posté est introuvable"
    assert len(_cles_postees()) >= 6, _cles_postees()


# ══════════════════════════════════════════════════════════════════════════
# Les fils sont branchés
# ══════════════════════════════════════════════════════════════════════════
def test_la_route_formation_sert_le_bon_fichier():
    """/formation existe et mène AU fichier de l'offre, pas ailleurs."""
    assert A.PAGES.get("/formation") == "formation.html", (
        "/formation ne sert pas formation.html : %r" % A.PAGES.get("/formation"))
    assert os.path.exists(os.path.join(RACINE, "formation.html"))


def test_la_page_appelle_le_referentiel_et_l_inscription():
    """Les deux routes de la fonctionnalité. En retirer une rend le calendrier
    vide ou le formulaire muet — sans aucune erreur visible.

    On cherche la route ENTRE GUILLEMETS : sans cela, « /inscriptionX »
    contiendrait encore « /inscription » et la règle passerait sur une adresse
    qui n'existe pas."""
    for route in ("'/api/formation/referentiel'", "'/api/formation/inscription'"):
        assert route in PAGE, "la page n'appelle pas %s" % route


def test_la_page_envoie_le_sujet_le_creneau_et_les_coordonnees():
    """Le corps posté doit porter ce que le serveur EXIGE. Un contrat qui
    diverge se solde par un 400 que la page ne sait pas expliquer."""
    cles = _cles_postees()
    for requis in ("sujet", "creneau", "prenom", "nom", "email", "entreprise"):
        assert requis in cles, (
            "le corps posté à l'inscription ne contient pas « %s » : %s"
            % (requis, sorted(cles)))


# ══════════════════════════════════════════════════════════════════════════
# Le client ne fixe jamais le prix — le cœur de l'offre
# ══════════════════════════════════════════════════════════════════════════
def test_le_client_n_envoie_aucun_prix():
    """Le tarif est décidé au serveur (rang → gratuit puis 800 € HT). Une clé
    de prix dans le corps posté serait une porte pour le fixer soi-même : le
    serveur l'ignore déjà, mais la laisser écrite est un piège pour la suite."""
    interdits = ("montant", "prix", "ht_cents", "ttc", "tarif", "gratuit",
                 "rang", "amount", "price")
    cles = {c.lower() for c in _cles_postees()}
    fautes = sorted(c for c in cles if any(m in c for m in interdits))
    assert not fautes, (
        "le corps posté contient une clé de PRIX (%s) : le tarif ne doit jamais "
        "venir du client, il se décide au serveur." % ", ".join(fautes))


def test_la_confirmation_lit_la_decision_du_serveur():
    """Après l'inscription, ce qui s'affiche vient de la RÉPONSE du serveur
    (gratuit, montant), non d'un prix recomposé côté page."""
    i = PAGE.index("function afficherConfirmation(")
    corps = PAGE[i:PAGE.index("\n  }", i)]
    assert "j.gratuit" in corps, "la confirmation ne lit pas la gratuité décidée au serveur"
    assert "j.montant_cents" in corps, (
        "la confirmation ne lit pas le montant décidé au serveur")


# ══════════════════════════════════════════════════════════════════════════
# Le prix annoncé est celui du module — une seule source
# ══════════════════════════════════════════════════════════════════════════
def test_le_prix_affiche_sur_la_page_est_celui_du_module():
    """CE QUI A DÉJÀ ÉTÉ CORRIGÉ AILLEURS. Un « 800 » écrit à la main survit à
    un changement de tarif : la page annonce alors un prix que le serveur ne
    prélève pas. Chaque montant « € HT » affiché doit égaler le tarif du
    module — la même discipline que le catalogue, où le prix vient d'un seul
    calcul."""
    attendu = str(F.TARIF_HT_CENTS // 100)
    texte = PAGE.replace("&nbsp;", " ").replace("\xa0", " ")
    montants = set(re.findall(r"(\d[\d\s]*)\s*€\s*HT", texte))
    montants = {m.replace(" ", "") for m in montants}
    assert montants, "aucun montant « € HT » n'est annoncé sur la page"
    faux = sorted(m for m in montants if m != attendu)
    assert not faux, (
        "la page annonce %s € HT alors que le module fixe %s € HT : le prix "
        "affiché a divergé du tarif servi." % (", ".join(faux), attendu))


# ══════════════════════════════════════════════════════════════════════════
# La mention d'information de CETTE page
# ══════════════════════════════════════════════════════════════════════════
def test_la_mention_de_la_page_annonce_la_duree_et_la_base():
    """Le contrôle global (test_mentions_formulaires) tient déjà les cinq
    composantes de l'article 13 ; celui-ci nomme la page et ancre les deux
    valeurs qui lui sont propres — 24 mois et la base 6.1.b —, pour qu'un
    changement muet de l'une d'elles tombe ici même."""
    mention = re.search(r'class="[^"]*rgpd-mention[^"]*"[^>]*>(.*?)</p>', PAGE, re.S)
    assert mention, "la page ne porte pas de mention d'information reconnaissable"
    m = mention.group(1)
    assert re.search(r"24\s*mois", m), "la mention n'annonce pas la durée de 24 mois"
    assert re.search(r"art\.\s*6\.1\.b", m), "la mention n'annonce pas la base 6.1.b"
    assert 'href="/confidentialite"' in m, "la mention ne renvoie pas à la politique"


# ══════════════════════════════════════════════════════════════════════════
# Sentinel conduit à la page
# ══════════════════════════════════════════════════════════════════════════
def test_sentinel_conduit_a_la_page_formation():
    """Sans un lien depuis le bloc « Formations conformité IA », l'offre n'est
    atteignable qu'en connaissant son adresse — et on ne cherche que ce dont on
    sait déjà l'existence."""
    i = SENTINEL.index('id="p-training"')
    bloc = SENTINEL[i:i + 4000]
    assert 'href="/formation"' in bloc, (
        "le bloc p-training ne conduit pas à /formation")


# ══════════════════════════════════════════════════════════════════════════
# Le durcissement, vu de la page
# ══════════════════════════════════════════════════════════════════════════
def test_le_corps_poste_porte_le_lieu_et_le_honeypot():
    """Le lieu (sur site) et le champ leurre partent au serveur : sans eux, le
    serveur ne pourrait ni exiger le lieu ni démasquer un robot."""
    cles = _cles_postees()
    assert "lieu" in cles, "le lieu de formation n'est pas envoyé au serveur"
    assert "website" in cles, "le champ leurre anti-robot n'est pas envoyé au serveur"


def test_la_page_marque_requis_les_six_champs_exiges():
    """Prénom, nom, adresse électronique, téléphone, entreprise, lieu : chacun
    porte `required` dans sa balise. Le serveur les exige de toute façon ; la
    page ne doit pas laisser croire qu'ils sont facultatifs."""
    for champ in ("fo-prenom", "fo-nom", "fo-email", "fo-phone",
                  "fo-entreprise", "fo-lieu"):
        m = re.search(r'<input[^>]*id="%s"[^>]*>' % champ, PAGE)
        assert m, "champ %s introuvable" % champ
        assert "required" in m.group(0), "%s n'est pas marqué requis" % champ


def test_le_honeypot_est_hors_ecran():
    """Le leurre ne doit pas se voir : un humain qui le remplirait serait refusé
    à tort. Il est sorti de l'écran, pas simplement masqué."""
    assert 'name="website"' in PAGE
    m = re.search(r'\.hp-field\{([^}]*)\}', PAGE)
    assert m and ("-9999px" in m.group(1) or "clip" in m.group(1)), (
        "le champ leurre n'est pas mis hors écran")
