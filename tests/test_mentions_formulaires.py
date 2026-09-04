# -*- coding: utf-8 -*-
"""Tout formulaire public qui collecte des données porte sa mention d'information.

POURQUOI CETTE RÈGLE ÉNUMÈRE AU LIEU DE NOMMER. Le défaut corrigé ici n'était
pas « il manque une mention sous le formulaire de contact » : c'était que
CHAQUE formulaire du site avait été écrit séparément, chacun avec sa propre
idée du RGPD. Cinq d'entre eux exigeaient une case « j'accepte que mes données
soient traitées » pour pouvoir envoyer — un montage qui cumule deux défauts :

  · il invoque le CONSENTEMENT (art. 6.1.a) là où traiter une demande, instruire
    une candidature ou ouvrir un compte relève des MESURES PRÉCONTRACTUELLES et
    de l'exécution du contrat (art. 6.1.b). Un consentement se retire à tout
    moment (art. 7.3) : il aurait fallu cesser de traiter une demande qu'on a le
    droit de traiter, et fermer un compte qu'on a le droit de tenir ;
  · un consentement exigé pour envoyer le formulaire n'est PAS LIBRE (art. 7.4),
    donc invalide. La case était à la fois obligatoire et sans effet.

LE CONSEIL D'ÉTAT L'A JUGÉ SUR CETTE FORME (11 mars 2015, n° 368624, mentionné
aux tables) : un consentement donné globalement ne vaut pas consentement
spécifique ; la personne doit marquer son assentiment « de manière distincte en
cochant une case spécifique » pour l'usage auquel elle consent.

Une règle qui nommerait les formulaires d'aujourd'hui laisserait passer celui
qui sera écrit dans six mois. Celle-ci RELÈVE tous les `<form>` des pages
publiques, en écarte ceux qui n'appellent pas de mention selon des critères
énoncés ici, et exige de chaque autre les cinq composantes de l'article 13 :
finalité, base légale, durée, droits, lien vers la politique.

CE QU'ELLE NE FAIT PAS, ET POURQUOI C'EST DIT. Elle ne mesure pas la qualité de
la rédaction ; elle mesure la présence de ce qui est dû. Une mention exacte mais
illisible passerait. Le remède est la relecture, pas une règle de plus.
"""
import io
import os
import re

import pytest

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ══════════════════════════════════════════════════════════════════════════
# Relever les formulaires — sans en nommer aucun
# ══════════════════════════════════════════════════════════════════════════
# CE QUE LE PREMIER JET RELEVAIT, ET POURQUOI C'ÉTAIT TROP ÉTROIT. La règle
# lisait le tableau `PAGES` d'app.py. Or `login.html`, `invitation.html` et
# `reset-password.html` ne sont pas servies par ce tableau mais par des routes
# à elles : les trois pages qui ouvrent un compte échappaient donc au filet, et
# la règle censée les tenir passait sans rien mesurer — verte pour une raison
# sans rapport avec ce qu'elle prétendait. Le relevé porte désormais sur TOUS
# les fichiers HTML du dépôt : une page nouvelle y tombe qu'on ait pensé à
# l'inscrire quelque part ou non.
def _pages_html():
    return sorted(n for n in os.listdir(RACINE) if n.endswith(".html"))

# Un formulaire qui n'AUTHENTIFIE que sur un compte déjà ouvert ne recueille
# rien de neuf : l'information a été délivrée à l'ouverture. La liste des
# INTENTIONS est ici, pas la liste des fichiers — un nouveau formulaire de
# connexion tombera dedans par ses champs, pas par son nom.
CHAMPS_AUTHENTIFIANTS = ("password", "mot de passe", "identifiant")
# Ce qui trahit une COLLECTE : des champs d'identité ou de contact.
CHAMPS_COLLECTE = ("email", "prenom", "prénom", "nom", "telephone", "téléphone",
                   "entreprise", "societe", "société", "message", "cv")


def _formulaires():
    """(fichier, identifiant, corps) pour chaque <form> d'une page publique."""
    releve = []
    for nom in _pages_html():
        chemin = os.path.join(RACINE, nom)
        if not os.path.exists(chemin):
            continue
        html = io.open(chemin, encoding="utf-8").read()
        for m in re.finditer(r"<form\b[^>]*>", html):
            ouverture = m.group(0)
            fermeture = html.find("</form>", m.end())
            corps = html[m.end():fermeture if fermeture != -1 else len(html)]
            ident = re.search(r'id="([^"]+)"', ouverture)
            releve.append((nom, ident.group(1) if ident else ouverture[:40], corps))
    return releve


def _champs(corps):
    """Les jetons qui NOMMENT les champs — id, name, placeholder, libellés.

    Le premier jet cherchait « nom » dans tout le corps du formulaire : il le
    trouvait dans `autocomplete`, dans `nombre`, partout. Un mot cherché dans
    du HTML brut se trouve toujours ; la question est de savoir s'il NOMME un
    champ. On ne lit donc que ce qui nomme.
    """
    jetons = []
    for attribut in ("id", "name", "placeholder"):
        jetons += re.findall(r'%s="([^"]*)"' % attribut, corps)
    jetons += re.findall(r"<label[^>]*>(.*?)</label>", corps, re.S)
    return " ".join(jetons).lower()


def _editable(balise):
    return not re.search(r"\b(disabled|readonly)\b", balise)


def _collecte(corps):
    """Ce formulaire collecte-t-il des données personnelles ?

    Trois cas, et ils se distinguent par ce que le formulaire DEMANDE :
      · il demande une identité ou des coordonnées MODIFIABLES — il collecte ;
      · il n'affiche qu'un mot de passe sur un compte existant — il
        authentifie, l'information a été délivrée à l'ouverture ;
      · il AFFICHE une donnée que le site détient déjà (adresse pré-remplie,
        non modifiable) — la personne rencontre là le traitement, et
        l'information lui est due (art. 13 et 14).
    """
    champs = _champs(corps)
    entrees = re.findall(r"<(?:input|textarea|select)\b[^>]*>", corps)

    # Une donnée déjà détenue, affichée en clair : la page informe.
    for balise in entrees:
        if re.search(r'(?:id|name)="[^"]*(?:email|mail|nom)[^"]*"', balise) \
                and not _editable(balise):
            return True

    modifiables = " ".join(
        b for b in entrees if _editable(b)
        and not re.search(r'type="(?:hidden|submit|button|checkbox)"', b))
    noms_modifiables = _champs(modifiables) + " " + champs
    demande_identite = any(re.search(r"\b%s\b" % re.escape(c), noms_modifiables)
                           for c in CHAMPS_COLLECTE)
    authentifie = bool(re.search(r'type="password"', corps))
    if authentifie and not re.search(r'autocomplete="new-password"',
                                     corps):
        # Connexion pure : rien de neuf n'est recueilli.
        return demande_identite and not re.search(
            r'autocomplete="(?:username|current-password)"', corps)
    return demande_identite


TOUS = _formulaires()
COLLECTEURS = [(f, i, c) for (f, i, c) in TOUS if _collecte(c)]


# LE POINT AVEUGLE DE TOUTE RÈGLE QUI ÉNUMÈRE CE QUI EXISTE, dit ici plutôt
# que tu, parce qu'il est réel : supprimer un formulaire supprime aussi l'essai
# qui le surveillait, et la suite reste verte. Un formulaire qui perdrait sa
# mention par disparition passerait donc inaperçu.
#
# Le remède n'est pas de nommer les formulaires — ce serait renoncer à ce que
# la règle attrape les prochains. C'est un PLANCHER : le nombre de formulaires
# collecteurs ne descend pas tout seul. Le faire baisser reste possible, mais
# devient un geste délibéré, daté et motivé ici même.
#
# Relevé du 4 septembre 2026 : 13 formulaires, dont 11 collectent.
PLANCHER_FORMULAIRES = 13
PLANCHER_COLLECTEURS = 11


def test_le_releve_trouve_bien_des_formulaires():
    """Sans ce garde-fou, une expression cassée rendrait toutes les autres
    règles vertes en ne mesurant rien. C'est exactement la faute que ce dépôt
    a déjà commise ailleurs : une règle verte pour une raison sans rapport."""
    assert len(TOUS) >= PLANCHER_FORMULAIRES, (
        "le relevé est tombé à %d formulaire(s), pour un plancher de %d. Soit "
        "un formulaire a été supprimé — abaisser le plancher ici, en disant "
        "lequel et pourquoi —, soit le relevé s'est cassé et ne mesure plus "
        "rien." % (len(TOUS), PLANCHER_FORMULAIRES))
    assert len(COLLECTEURS) >= PLANCHER_COLLECTEURS, (
        "le nombre de formulaires vus comme collecteurs est tombé à %d, pour "
        "un plancher de %d : soit le tri s'est cassé, soit un formulaire de "
        "collecte a disparu sans que le plancher suive."
        % (len(COLLECTEURS), PLANCHER_COLLECTEURS))


# ══════════════════════════════════════════════════════════════════════════
# Les cinq composantes de l'article 13
# ══════════════════════════════════════════════════════════════════════════
# CE QUE LE PREMIER JET ACCEPTAIT, ET POURQUOI C'ÉTAIT TROP LARGE. « Base
# légale » se contentait de `art. 6.1.x` n'importe où dans la mention. Retirer
# la base de la COLLECTE laissait celle de la PROSPECTION (6.1.f), et la règle
# restait verte alors que la finalité principale n'avait plus de fondement
# annoncé. La base de la collecte est donc exigée pour elle-même.
DUREE = (r"\d+\s*mois|trois ans|jusqu'à (?:votre|la) désinscription|"
         r"le temps du compte")
COMPOSANTES = {
    # « Finalité » n'a pas de signature mécanique : ce motif est un repère, pas
    # une mesure. Il attrape les verbes par lesquels une mention dit à quoi la
    # donnée sert. Une mention qui dirait la finalité autrement échouerait ici
    # à tort — le remède est d'ajouter la tournure, pas d'affaiblir la règle.
    "finalité": (r"\bser(?:t|vent|vir)\b|traiter votre|instruire votre|"
                 r"recevoir|ouvrir et à tenir|créer et à tenir|tenir votre accès"),
    "base légale de la collecte": r"art\.\s*6\.1\.[ab]",
    "durée": DUREE,
    "droits": r"droits d'accès|rectification|effacement|opposition|se retire",
    "lien vers la politique": r'href="/(?:confidentialite|protection-donnees)"',
}


def _mention(corps):
    """Le texte de la mention portée par ce formulaire, s'il y en a une."""
    blocs = re.findall(r'<(p|div|span)[^>]*class="[^"]*rgpd-mention[^"]*"[^>]*>'
                       r'(.*?)</\1>', corps, re.S)
    return "\n".join(b for _, b in blocs)


@pytest.mark.parametrize("fichier,ident,corps", COLLECTEURS,
                         ids=["%s#%s" % (f, i) for f, i, _ in COLLECTEURS])
def test_un_formulaire_qui_collecte_porte_sa_mention(fichier, ident, corps):
    """La mention existe, et elle est reconnaissable à sa classe.

    La classe `rgpd-mention` n'est pas décorative : c'est ce qui permet à cette
    règle de trouver la mention sans deviner. Un texte juste mais sans la
    classe échoue ici — et c'est voulu, sinon la règle suivante n'aurait rien à
    mesurer.
    """
    assert _mention(corps).strip(), (
        "%s#%s collecte des données personnelles et ne porte aucune mention "
        "d'information (art. 13). Ajouter un bloc de classe « rgpd-mention » "
        "sous le formulaire." % (fichier, ident))


@pytest.mark.parametrize("fichier,ident,corps", COLLECTEURS,
                         ids=["%s#%s" % (f, i) for f, i, _ in COLLECTEURS])
def test_la_mention_porte_les_cinq_composantes(fichier, ident, corps):
    """Finalité, base légale, durée, droits, lien — l'article 13 les exige
    toutes. Une mention qui n'en porte que trois informe à moitié, et c'est la
    moitié manquante qui compte."""
    texte = _mention(corps)
    if not texte.strip():
        pytest.skip("mention absente : la règle précédente le dit déjà")
    manquantes = [nom for nom, motif in COMPOSANTES.items()
                  if not re.search(motif, texte, re.I)]
    assert not manquantes, (
        "%s#%s : la mention ne dit pas %s" % (fichier, ident,
                                              ", ".join(manquantes)))


@pytest.mark.parametrize("fichier,ident,corps", COLLECTEURS,
                         ids=["%s#%s" % (f, i) for f, i, _ in COLLECTEURS])
def test_chaque_finalite_annoncee_porte_sa_duree(fichier, ident, corps):
    """L'article 13.2.a exige la durée POUR CHAQUE finalité.

    CE QUE LA RÈGLE PRÉCÉDENTE LAISSAIT PASSER. Elle se contentait d'UNE durée
    quelque part dans la mention. Une mention qui annonce deux finalités — la
    demande, puis la prospection — et une seule durée informe à moitié, et
    c'est la moitié manquante qui compte. Retirer « 24 mois » d'une mention qui
    dit aussi « trois ans » ne la faisait pas tomber : elle tombe maintenant.

    La mention est coupée à l'endroit où la prospection commence (art. 6.1.f) :
    chaque moitié doit porter sa durée.
    """
    texte = _mention(corps)
    if not texte.strip():
        pytest.skip("mention absente : une autre règle le dit")
    coupe = re.search(r"art\.\s*6\.1\.f", texte, re.I)
    if not coupe:
        return  # une seule finalité : la règle précédente suffit
    collecte, prospection = texte[:coupe.start()], texte[coupe.start():]
    for part, quoi in ((collecte, "la demande elle-même"),
                       (prospection, "la prospection annoncée")):
        assert re.search(DUREE, part, re.I), (
            "%s#%s : aucune durée n'est annoncée pour %s (art. 13.2.a)"
            % (fichier, ident, quoi))


# ══════════════════════════════════════════════════════════════════════════
# Aucune case cochée ne conditionne un envoi
# ══════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("fichier,ident,corps", TOUS,
                         ids=["%s#%s" % (f, i) for f, i, _ in TOUS])
def test_aucune_case_de_consentement_ne_conditionne_l_envoi(fichier, ident, corps):
    """Un consentement exigé pour envoyer n'est pas libre (art. 7.4).

    La règle porte sur TOUS les formulaires, pas seulement sur les collecteurs :
    une case obligatoire est invalide où qu'elle soit.
    """
    for m in re.finditer(r"<input\b[^>]*type=\"checkbox\"[^>]*>", corps):
        balise = m.group(0)
        if "required" in balise:
            pytest.fail(
                "%s#%s : une case à cocher est obligatoire pour envoyer "
                "(%s). Un consentement exigé pour envoyer n'est pas libre "
                "(art. 7.4) ; remplacer la case par une mention "
                "d'information." % (fichier, ident, balise.strip()))


@pytest.mark.parametrize("fichier,ident,corps", TOUS,
                         ids=["%s#%s" % (f, i) for f, i, _ in TOUS])
def test_aucune_case_n_est_precochee(fichier, ident, corps):
    """Une case cochée d'avance ne recueille aucun consentement : il faut un
    acte positif de la personne (CJUE, Planet49, C-673/17, 1er oct. 2019)."""
    for m in re.finditer(r"<input\b[^>]*type=\"checkbox\"[^>]*>", corps):
        balise = m.group(0)
        if re.search(r"\bchecked\b", balise):
            pytest.fail(
                "%s#%s : une case est cochée d'avance (%s) — aucun "
                "consentement n'est recueilli ainsi (CJUE, Planet49, "
                "C-673/17)." % (fichier, ident, balise.strip()))


# ══════════════════════════════════════════════════════════════════════════
# Ce que la mention annonce est ce que la politique publie
# ══════════════════════════════════════════════════════════════════════════
# LE DÉFAUT QUI A MOTIVÉ CETTE RÈGLE. La page d'assistance annonçait sous son
# formulaire une conservation de « 13 mois max » — la durée des COOKIES, reprise
# par inadvertance. Deux durées différentes pour la même donnée, sur le même
# site : l'information est fausse quelle que soit celle qui a raison.
POLITIQUES = ("confidentialite.html", "protection-donnees.html")


# LA COMPARAISON PORTE SUR LA VALEUR, PAS SUR L'ORTHOGRAPHE. Une mention qui
# dit « trois ans » et une politique qui dit « 3 ans » annoncent la même chose ;
# une règle qui comparerait les chaînes crierait au désaccord là où il n'y en a
# pas, et manquerait le vrai désaccord — « 12 mois » contre « 13 mois ». Les
# deux textes sont donc ramenés en MOIS avant d'être confrontés.
_NOMBRES = {"un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5,
            "six": 6, "sept": 7, "huit": 8, "neuf": 9, "dix": 10, "onze": 11,
            "douze": 12, "treize": 13, "vingt-quatre": 24, "trente-six": 36}
_DUREE = re.compile(
    r"(\d+|%s)\s*(mois|ans?)" % "|".join(sorted(_NOMBRES, key=len, reverse=True)),
    re.I)


def _en_mois(texte):
    """Les durées d'un texte, exprimées en mois."""
    trouvees = set()
    for valeur, unite in _DUREE.findall(texte):
        v = _NOMBRES.get(valeur.lower()) if not valeur.isdigit() else int(valeur)
        if v is None:
            continue
        trouvees.add(v * 12 if unite.lower().startswith("an") else v)
    return trouvees


def _durees_publiees():
    textes = []
    for nom in POLITIQUES:
        chemin = os.path.join(RACINE, nom)
        if os.path.exists(chemin):
            textes.append(io.open(chemin, encoding="utf-8").read())
    assert textes, "aucune politique n'a été lue : la règle ne mesure rien"
    return _en_mois("\n".join(textes))


def test_les_politiques_publient_bien_des_durees():
    """Garde-fou : si l'extraction se cassait, la règle suivante deviendrait
    verte en comparant à un ensemble vide."""
    publiees = _durees_publiees()
    assert len(publiees) >= 4, (
        "durées relevées dans les politiques : %s — relevé suspect" % sorted(publiees))


@pytest.mark.parametrize("fichier,ident,corps", COLLECTEURS,
                         ids=["%s#%s" % (f, i) for f, i, _ in COLLECTEURS])
def test_les_durees_annoncees_figurent_dans_une_politique(fichier, ident, corps):
    """Toute durée écrite sous un formulaire doit se retrouver dans une des
    politiques publiées. Sinon la mention invente un chiffre que rien
    n'appuie."""
    texte = _mention(corps)
    if not texte.strip():
        pytest.skip("mention absente : une autre règle le dit")
    publiees = _durees_publiees()
    orphelines = sorted(_en_mois(texte) - publiees)
    assert not orphelines, (
        "%s#%s annonce %s mois alors qu'aucune politique publiée ne fixe cette "
        "durée : soit la mention se trompe, soit la politique est à "
        "compléter." % (fichier, ident, orphelines))


# ══════════════════════════════════════════════════════════════════════════
# Le serveur suit ce que les pages déclarent
# ══════════════════════════════════════════════════════════════════════════
def test_le_serveur_n_exige_plus_de_consentement_pour_ouvrir_un_compte():
    """Retirer la case des pages sans retirer le refus côté serveur produirait
    un formulaire qui ne peut plus être envoyé : le visiteur ne voit rien à
    cocher et le serveur refuse toujours. La règle mesure le serveur."""
    src = io.open(os.path.join(RACINE, "app.py"), encoding="utf-8").read()
    # Le motif est ancré : « rgpd_consent » suivi de rien d'alphanumérique.
    # Sans cette ancre il attrapait `rgpd_consentement_public`, une fonction
    # sans rapport — une règle rouge pour une raison étrangère à ce qu'elle
    # prétend mesurer vaut la règle verte pour une mauvaise raison.
    motif = re.compile(r"\brgpd_consent(?![A-Za-z0-9_])")
    fautes = [l for l in src.splitlines() if motif.search(l)]
    assert not fautes, (
        "app.py lit encore « rgpd_consent » alors que les formulaires ne "
        "l'envoient plus : %s" % " | ".join(f.strip() for f in fautes))


def test_les_pages_de_compte_informent_meme_sans_champ_de_contact():
    """Inscription et activation ne demandent ni prénom ni message : elles
    échappent au tri des collecteurs. Elles ouvrent pourtant un traitement
    durable, et doivent informer. La règle les rattrape par leur nature —
    un formulaire qui pose un mot de passe NEUF crée un compte."""
    manquantes = []
    for nom, ident, corps in TOUS:
        neuf = re.search(r'autocomplete="new-password"', corps)
        if neuf and not _mention(corps).strip():
            manquantes.append("%s#%s" % (nom, ident))
    assert not manquantes, (
        "ces formulaires ouvrent un compte sans mention d'information "
        "(art. 13) : %s" % ", ".join(manquantes))
