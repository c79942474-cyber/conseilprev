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
import re as _re

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
    j = PAGE.index("JSON.stringify({", i) + len("JSON.stringify({") - 1
    # LES ACCOLADES SE COMPTENT. S'arrêter au premier « }) » a suffi tant que le
    # corps était plat ; depuis que les séances y sont une liste d'objets, cette
    # borne tombe AU MILIEU du corps et le relevé ne voit plus que trois clés.
    # Une règle qui lit un tiers de ce qu'elle croit mesurer est verte pour rien.
    prof, k = 0, j
    while k < len(PAGE):
        if PAGE[k] == "{":
            prof += 1
        elif PAGE[k] == "}":
            prof -= 1
            if prof == 0:
                break
        k += 1
    return PAGE[j + 1:k]


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
    interdits = ("montant", "prix", "ht_cents", "ttc", "tarif",
                 "rang", "amount", "price")
    cles = {c.lower() for c in _cles_postees()}
    fautes = sorted(c for c in cles if any(m in c for m in interdits))
    assert not fautes, (
        "le corps posté contient une clé de PRIX (%s) : le tarif ne doit jamais "
        "venir du client, il se décide au serveur." % ", ".join(fautes))
    # « GRATUIT » N'EST PLUS INTERDIT, ET CE N'EST PAS UN RELÂCHEMENT.
    # Il ne porte plus un prix mais la CLÉ DU SUJET que le client veut offert —
    # le serveur décide seul s'il reste une séance offerte à donner, et refuse
    # une clé qui n'est pas dans le panier. Ce qui reste interdit, c'est qu'il
    # porte un MONTANT ou un booléen : « gratuit: true » serait la porte que
    # cette règle ferme depuis le début.
    m = _re.search(r"\bgratuit\s*:\s*([^,\n]+)", _corps_inscription())
    assert m, "la séance offerte n'est plus désignée dans le corps posté"
    valeur = m.group(1).strip()
    assert "state.gratuit" in valeur, (
        "« gratuit » n'envoie pas la clé du sujet choisi mais : %s" % valeur)
    for interdit in ("true", "false", "1", "0"):
        assert not valeur.startswith(interdit), (
            "« gratuit » porte un booléen ou un nombre (%s) : ce serait au "
            "client de décider du prix." % valeur)


def test_la_confirmation_lit_la_decision_du_serveur():
    """Après l'inscription, ce qui s'affiche vient de la RÉPONSE du serveur
    (gratuit, montant), non d'un prix recomposé côté page."""
    i = PAGE.index("function afficherConfirmation(")
    corps = PAGE[i:PAGE.index("\n  }", i)]
    # CE QUI A CHANGÉ : la réponse porte désormais un DEVIS et une liste de
    # séances, parce qu'on en réserve jusqu'à quatre. La règle suit la forme,
    # pas l'inverse — mais elle exige toujours la même chose : chaque montant
    # affiché vient du serveur.
    assert "j.seances" in corps, "la confirmation ne lit pas les séances réservées"
    assert "j.devis" in corps or "dev." in corps, (
        "la confirmation ne lit pas le devis décidé au serveur")
    assert "ht_cents" in corps, "la confirmation n'affiche aucun montant du serveur"
    # ET ELLE N'EN RECOMPOSE AUCUN. Un tarif écrit ici survivrait à un
    # changement de prix, et la page annoncerait un montant que le serveur ne
    # pratique plus.
    for ecrit in ("800", "TARIF", "* 1.2", "tva_pct *"):
        assert ecrit not in corps, (
            "la confirmation recompose un prix (« %s ») au lieu de lire celui "
            "du serveur" % ecrit)


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


# ══════════════════════════════════════════════════════════════════════════
# La zone d'intervention, et les bulles d'info
# ══════════════════════════════════════════════════════════════════════════
def _autour_du_lieu():
    """La fenêtre qui entoure le champ du lieu : son libellé (bulle comprise) et
    sa note. On mesure LÀ, et non « quelque part dans la page » — une première
    version cherchait la zone n'importe où, et la trouvait dans une carte
    d'information à l'autre bout : elle restait verte alors que le champ, lui,
    n'annonçait plus rien."""
    i = PAGE.index('id="fo-lieu"')
    return PAGE[max(0, i - 800):i + 500]


def test_la_modalite_du_module_porte_la_zone():
    """LA SOURCE. La page affiche la modalité servie par le référentiel : c'est
    elle qui doit dire où la séance se tient. Une garde au chargement du module
    refuse déjà une modalité qui l'aurait perdue — cette règle en est le pendant
    lisible."""
    assert F.ZONE in F.OFFRE["modalite"], (
        "la modalité du module ne dit plus la zone (%s)" % F.ZONE)


def test_la_bulle_du_lieu_annonce_la_zone():
    """LA BULLE DEMANDÉE : au moment de saisir le lieu, le client apprend que la
    séance se tient en Île-de-France, sur SON site."""
    m = re.search(r'<label[^>]*for="fo-lieu"[^>]*>(.*?)</label>', PAGE, re.S)
    assert m, "libellé du lieu introuvable"
    tip = re.search(r'data-tip="([^"]*)"', m.group(1))
    assert tip, "le champ du lieu n'a pas de bulle"
    assert F.ZONE in tip.group(1), (
        "la bulle du lieu n'annonce pas la zone (%s)" % F.ZONE)


def test_la_zone_reste_visible_sans_survol_pres_du_champ():
    """UNE INFORMATION CACHÉE DERRIÈRE UN SURVOL N'EXISTE PAS AU DOIGT. La zone
    est une limite de l'offre : elle doit rester lisible à côté du champ, hors
    de tout attribut de bulle, sur un écran tactile comme ailleurs."""
    fenetre = _autour_du_lieu()
    visible = re.sub(r'data-tip="[^"]*"', '', fenetre)
    visible = re.sub(r'aria-label="[^"]*"', '', visible)
    assert F.ZONE in visible, (
        "près du champ du lieu, la zone (%s) n'apparaît que dans une bulle : "
        "elle est invisible sur un écran tactile" % F.ZONE)


def test_chaque_champ_du_formulaire_porte_sa_bulle():
    """Les pastilles « i » expliquent ce qu'on attend de chaque champ. Une seule
    oubliée, et c'est le champ le moins évident qui reste sans explication."""
    for champ in ("fo-prenom", "fo-nom", "fo-email", "fo-phone", "fo-entreprise",
                  "fo-siret", "fo-lieu", "fo-fonction", "fo-message"):
        m = re.search(r'<label[^>]*for="%s"[^>]*>(.*?)</label>' % champ, PAGE, re.S)
        assert m, "libellé de %s introuvable" % champ
        assert 'class="ent-tip"' in m.group(1) and "data-tip=" in m.group(1), (
            "le champ %s n'a pas de bulle d'info" % champ)


def test_les_bulles_sont_atteignables_au_clavier():
    """Une bulle qui ne s'ouvre qu'au survol exclut qui navigue au clavier. La
    pastille est focalisable, et la règle d'affichage répond aussi à `:focus`."""
    for m in re.finditer(r'<span class="ent-tip"[^>]*>', PAGE):
        assert 'tabindex="0"' in m.group(0), "une pastille n'est pas focalisable"
    assert ".ent-tip:focus::after" in PAGE, (
        "la bulle ne s'ouvre pas au focus clavier")


def test_le_cadre_de_sentinel_pulse_et_sait_s_arreter():
    """Le cadre « Angles morts » se signale par une pulsation. CE QUI COMPTE
    AUTANT : qu'elle CESSE pour qui demande moins de mouvement — une animation
    qu'on ne peut pas arrêter est une gêne, pas une mise en valeur."""
    i = SENTINEL.index('id="p-training"')
    bloc = SENTINEL[i:i + 6000]
    assert "@keyframes formation-eclat" in bloc, "le cadre ne pulse plus"
    assert 'class="formation-eclat"' in bloc, "la bannière ne porte plus l'animation"
    j = bloc.index("@keyframes formation-eclat")
    regles = bloc[j:j + 1400]
    assert "prefers-reduced-motion" in regles, (
        "aucun repli pour qui demande moins de mouvement")
    repli = regles[regles.index("prefers-reduced-motion"):]
    assert "animation:none" in repli, (
        "le repli ne coupe pas l'animation")


def test_le_honeypot_est_hors_ecran():
    """Le leurre ne doit pas se voir : un humain qui le remplirait serait refusé
    à tort. Il est sorti de l'écran, pas simplement masqué."""
    assert 'name="website"' in PAGE
    m = re.search(r'\.hp-field\{([^}]*)\}', PAGE)
    assert m and ("-9999px" in m.group(1) or "clip" in m.group(1)), (
        "le champ leurre n'est pas mis hors écran")
