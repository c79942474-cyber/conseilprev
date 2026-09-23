# -*- coding: utf-8 -*-
"""LES INFOBULLES S'OUVRENT AU DOIGT — ET PAS SEULEMENT AU SURVOL.

CE QUI A ÉTÉ SIGNALÉ, PUIS MESURÉ. « Les infobulles ne s'ouvrent jamais sur
un appareil tactile. » Relevé au navigateur en contexte tactile réel
(Pixel 7, hasTouch, `(hover:none)` vrai) : l'opacité de la bulle valait 0
AVANT et APRÈS un appui du doigt. Les trente-deux infobulles de la page
d'accueil n'existaient donc pas sur un téléphone.

ET LE CLAVIER N'ALLAIT PAS MIEUX. Les cartes sont des <div> sans tabindex :
`element.focus()` n'y prenait même pas — `document.activeElement` restait
sur le <body>. Le second chemin sans souris était fermé lui aussi.

CE QUE LA CORRECTION NE FAIT PAS, ET C'EST LE POINT. Elle ne dessine AUCUNE
bulle. Chaque page a la sienne, réglée au pixel près — l'une d'elles a coûté
une recette entière à cause d'un `overflow:hidden`. Une seconde bulle
dessinée en JavaScript s'afficherait EN PLUS de celle du survol sur un poste
fixe. `/infobulles.js` DÉRIVE donc l'état ouvert des règles de survol déjà
écrites dans la page, et ne pose qu'une classe.

LE DÉFAUT QUE SEUL LE NAVIGATEUR POUVAIT MONTRER. Une première version
fermait la bulle au défilement. La classe était POSÉE puis RETIRÉE dans la
foulée : la page défile en `scroll-behavior:smooth`, et amener une carte à
l'écran émet des dizaines d'événements de défilement APRÈS l'appui. Aucune
erreur, aucune trace, et une infobulle qui ne s'ouvre jamais. C'est le
défaut que ce dépôt traque : un mécanisme qui échoue pour une raison sans
rapport avec ce qu'il prétend faire.

LE SECOND, SUR LE RAIL DORA. Ses six blocs sont des <boutons> qui mènent à
leur panneau. Au doigt, l'appui ouvrait la bulle — puis naviguait, et la
navigation repeint le rail, donc détruit le bouton qui la portait. Opacité
relevée : 0. Le premier appui ouvre désormais et retient le clic ; le second
y va.
"""
import io
import os
import re

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _lire(nom):
    return io.open(os.path.join(_RACINE, nom), encoding="utf-8").read()


SCRIPT = _lire("infobulles.js")
INDEX = _lire("index.html")
SENTINEL = _lire("sentinel.html")
PAGE_JS = _lire("sentinel.page.js")


# ══════════════════════════════════════════════════════════════════════════
#  1. LE SCRIPT EST LÀ OÙ IL Y A DES INFOBULLES — ET LA LISTE EST DÉRIVÉE
# ══════════════════════════════════════════════════════════════════════════

def _pages_a_infobulles():
    """Les pages qui portent RÉELLEMENT une infobulle, lues sur le disque.

    ON NE TIENT PAS DE LISTE À LA MAIN. Vingt pages portent la FEUILLE des
    infobulles ; une seule portait des attributs quand ce défaut a été
    mesuré. Une liste recopiée ici ne saurait pas qu'une page en a reçu."""
    out = {}
    for nom in sorted(os.listdir(_RACINE)):
        if not nom.endswith(".html"):
            continue
        txt = _lire(nom)
        n = len(re.findall(r'\sdata-tooltip="', txt)) \
            + len(re.findall(r'\sdata-tip="', txt))
        if n:
            out[nom] = n
    return out


def test_CHAQUE_page_qui_porte_une_infobulle_charge_le_script():
    """SANS LE SCRIPT, L'INFOBULLE RESTE UNE DÉCORATION DE POSTE FIXE.

    C'est la règle qui empêche la correction de rester partielle : une page
    qui gagnerait des infobulles demain sans charger le script rendrait le
    défaut, sans que rien ne le dise."""
    pages = _pages_a_infobulles()
    assert pages, ("aucune page ne porte d'attribut d'infobulle : la lecture "
                   "a changé de forme, cette règle ne mesure plus rien")
    manquantes = [p for p in pages if '/infobulles.js' not in _lire(p)]
    assert not manquantes, (
        "ces pages portent des infobulles sans charger /infobulles.js — "
        "elles ne s'ouvriront ni au doigt ni au clavier : %s "
        "(relevé : %s)" % (manquantes, pages))


def test_le_script_ne_ramasse_QUE_les_deux_conventions_du_depot():
    """UN `title` NATIF N'EST PAS RAMASSÉ, ET C'EST VOULU.

    Il appartient au navigateur, sert aussi aux champs de formulaire, et le
    détourner produirait DEUX infobulles sur un poste fixe : celle du
    navigateur et la nôtre."""
    m = re.search(r'var SELECTEUR\s*=\s*"([^"]+)"', SCRIPT)
    assert m, "le sélecteur du script est introuvable"
    assert m.group(1) == "[data-tooltip],[data-tip]", (
        "le script ramasse autre chose que les deux conventions : %r"
        % m.group(1))
    assert "[title]" not in SCRIPT, (
        "le script ramasse les `title` natifs : un poste fixe afficherait "
        "deux infobulles l'une sur l'autre")


# ══════════════════════════════════════════════════════════════════════════
#  2. L'ÉTAT OUVERT EST DÉRIVÉ DU SURVOL, JAMAIS REDÉCLARÉ
# ══════════════════════════════════════════════════════════════════════════

def test_l_etat_ouvert_est_DERIVE_des_regles_de_survol_de_la_page():
    """LE PIÈGE ÉVITÉ. Une règle générique « à l'ouverture, opacité 1 » a
    l'air de suffire. Elle ne suffit pas : le survol ANNULE AUSSI le
    décalage d'entrée de la bulle, et ce décalage n'est pas le même partout
    — 4 px sur la bulle générique, 6 px sur les cartes de l'accueil. Une
    valeur devinée laisserait la bulle deux pixels plus bas au doigt qu'à la
    souris, et se déréglerait au premier changement de page.

    On lit donc les feuilles de la page et on republie la règle de survol
    avec la classe à la place de `:hover`."""
    # ═══ CES TROIS CONTRÔLES ONT ÉTÉ RESSERRÉS APRÈS DEUX SURVIVANTES ═══
    # Ils cherchaient d'abord la PRÉSENCE d'un mot — « document.styleSheets »,
    # « regles[i].style.cssText ». Deux mutations les ont traversés : l'une
    # remplaçait la lecture des règles par `null`, l'autre remplaçait les
    # déclarations reprises par un `opacity:1` inventé. Les deux mots
    # restaient écrits ailleurs dans le fichier, et la règle passait pour une
    # raison sans rapport avec ce qu'elle prétend mesurer. On vise désormais
    # l'EXPRESSION qui fait le travail, pas le mot qui la nomme.
    assert re.search(r"regles = feuilles\[i\]\.cssRules;", SCRIPT), (
        "le script ne lit plus les règles des feuilles de la page : l'état "
        "ouvert est redéclaré au lieu d'être dérivé, et divergera du survol")
    assert re.search(
        r'out\.push\(s2\.split\(":hover"\)\.join\("\." \+ OUVERTE\)\s*\+\s*"\{"\s*'
        r'\+\s*regles\[i\]\.style\.cssText\s*\+\s*"\}"\);', SCRIPT), (
        "la jumelle n'est plus construite à partir de la règle de survol : "
        "soit `:hover` n'est plus remplacé par la classe, soit les "
        "déclarations sont inventées au lieu d'être reprises")


def test_le_filtre_des_jumelles_est_ETROIT():
    """SANS CE FILTRE, LA CARTE GROSSIRAIT À CHAQUE APPUI.

    `.diff-card:hover{transform:scale(1.10)}` est une règle de survol comme
    une autre. Jumelée, elle ferait grossir la carte quand la bulle s'ouvre
    — ce qui n'a rien à voir avec une infobulle. Seules les règles qui
    citent une convention d'infobulle ET un pseudo-élément de bulle sont
    reprises."""
    for jeton in ('css.indexOf("attr(data-tooltip") >= 0',
                  'css.indexOf("attr(data-tip") >= 0',
                  'if (!bases[_base(s2)]) continue;'):
        assert jeton in SCRIPT, (
            "le filtre des jumelles a perdu %r : des règles de survol sans "
            "rapport avec les infobulles seraient reprises" % jeton)

    # ET IL NE DOIT PAS REDEVENIR UNE LISTE DE NOMS. Le dépôt en compte
    # déjà trois — `.ent-tip`, `.ttip`, `[data-tooltip]` — et c'est une
    # règle de cette suite qui a trouvé les deux pages oubliées, pas une
    # relecture. Une liste écrite en dur ne saurait pas qu'une quatrième
    # famille est née.
    for nom in (".ent-tip", ".ttip", ".diff-card"):
        assert '"%s"' % nom not in SCRIPT, (
            "le script cite %r en dur : le filtre est redevenu une liste, "
            "et la prochaine famille d'infobulles sera oubliée" % nom)


# ══════════════════════════════════════════════════════════════════════════
#  3. LE DÉFAUT MESURÉ : NE PAS FERMER AU DÉFILEMENT
# ══════════════════════════════════════════════════════════════════════════

def test_la_bulle_ne_se_referme_PAS_au_defilement():
    """LE DÉFAUT, RELEVÉ AU NAVIGATEUR. La classe était posée puis retirée
    dans la foulée. La page défile en `scroll-behavior:smooth` : amener une
    carte à l'écran émet des dizaines d'événements de défilement APRÈS
    l'appui. Sur un vrai téléphone c'est le cas ORDINAIRE — on tape une
    carte à demi visible, le navigateur l'amène à l'écran, et la bulle se
    referme avant d'avoir été lue.

    Fermer au défilement ne servait à rien par ailleurs : la bulle est
    positionnée par rapport à sa cible et voyage avec elle.

    LE GARDE-FOU : sans lui, cette règle passerait sur un script qui ne
    ferme JAMAIS rien — ce qui serait un autre défaut. On vérifie que les
    trois sorties voulues sont là."""
    assert not re.search(r'addEventListener\(\s*"scroll"', SCRIPT), (
        "le script se ferme encore au défilement : sur un téléphone, la "
        "bulle se referme avant d'avoir été lue")
    assert re.search(r'ev\.key === "Escape"', SCRIPT), (
        "la touche d'échappement ne referme plus")
    assert "if (ouvert === el) return fermer();" in SCRIPT, (
        "un second appui ne referme plus")
    assert re.search(r'if \(!el\) return fermer\(\);', SCRIPT), (
        "un appui ailleurs ne referme plus")


def test_le_redimensionnement_ne_compte_que_s_il_change_la_LARGEUR():
    """LA MÊME PORTE, PAR UN AUTRE CHEMIN. Sur un téléphone, la barre
    d'adresse qui se rétracte pendant un défilement émet un `resize` — de
    HAUTEUR seulement. Le traiter comme un changement de mise en page
    ramènerait exactement le défaut qu'on vient de corriger."""
    assert "window.innerWidth === largeur" in SCRIPT, (
        "le script ferme sur tout redimensionnement : la barre d'adresse "
        "d'un téléphone refermerait la bulle pendant le défilement")


# ══════════════════════════════════════════════════════════════════════════
#  4. LE SURVOL N'EST PAS VOLÉ AU POSTE FIXE
# ══════════════════════════════════════════════════════════════════════════

def test_la_souris_est_IGNOREE_par_le_script():
    """UN CLIC DE SOURIS DOIT RESTER UN CLIC. Si le script traitait aussi la
    souris, un clic sur une carte ouvrirait une bulle collante en plus de
    suivre le lien — et le survol, qui marche déjà, aurait un concurrent."""
    assert 'if (ev.pointerType === "mouse") return;' in SCRIPT, (
        "le script traite aussi la souris : il vole le survol au poste fixe")


def test_le_script_ne_pose_PAS_de_tabindex_sur_ce_qui_est_deja_focusable():
    """UN <bouton> EST DÉJÀ ATTEIGNABLE. Lui poser un tabindex ne ferait que
    dupliquer son rang de tabulation — et les six blocs du rail DORA sont
    des boutons."""
    assert re.search(r'/\^\(A\|BUTTON\|INPUT\|SELECT\|TEXTAREA\)\$/', SCRIPT), (
        "le script ne reconnaît plus les éléments déjà focusables")
    assert re.search(r'if \(!focusable\) el\.setAttribute\("tabindex", "0"\)',
                     SCRIPT), (
        "le script ne rend plus les <div> atteignables au clavier : c'est "
        "la moitié du défaut mesuré")


def test_le_texte_est_ANNONCE_au_lecteur_d_ecran():
    """UN ATTRIBUT EST INVISIBLE AUX TECHNOLOGIES D'ASSISTANCE. Le texte de
    l'infobulle vit dans `data-tooltip` : sans région d'annonce, l'ouvrir ne
    le rend lisible qu'aux yeux."""
    assert 'setAttribute("aria-live", "polite")' in SCRIPT, (
        "la région d'annonce n'est plus une région live")
    assert "clip-path:inset(50%)" in SCRIPT, (
        "la région d'annonce n'est plus masquée visuellement — ou l'est par "
        "`display:none`, qui la retirerait aussi de l'arbre d'accessibilité")


# ══════════════════════════════════════════════════════════════════════════
#  5. LE RAIL DORA — LIRE D'ABORD, ALLER ENSUITE
# ══════════════════════════════════════════════════════════════════════════

def test_le_rail_DORA_a_quitte_le_title_natif():
    """UN `title` NE S'OUVRE PAS AU DOIGT. Les six infobulles du rail — ce
    que le bloc fait, pourquoi il est là, son piège, ce que son état veut
    dire — n'existaient pas sur un téléphone. Or c'est ce parcours-là qu'on
    demande de suivre pas à pas."""
    bloc = re.search(r"piste \+= '<button type=\"button\" class=\"dr-bloc"
                     r".*?</button>';", PAGE_JS, re.S)
    assert bloc, "le bloc du rail est introuvable"
    txt = bloc.group(0)
    assert "data-tooltip=" in txt, (
        "le bloc du rail ne porte plus data-tooltip : son infobulle "
        "redevient muette au doigt")
    assert " title=" not in txt, (
        "le bloc du rail porte encore un `title` natif : deux infobulles "
        "s'afficheraient sur un poste fixe")


def test_le_premier_appui_sur_le_rail_OUVRE_avant_de_naviguer():
    """LE DÉFAUT MESURÉ, OPACITÉ 0. Au doigt, l'appui ouvrait la bulle puis
    naviguait — et la navigation repeint le rail, donc DÉTRUIT le bouton qui
    la portait. L'infobulle était aussi illisible qu'avec le `title` qu'elle
    remplaçait.

    ET C'EST UN OPT-IN, PAS UNE RÈGLE GÉNÉRALE : retenir le premier clic
    partout changerait le comportement de chaque lien du site au doigt."""
    assert 'var AVANT_CLIC = "data-bulle-avant-clic"' in SCRIPT, (
        "la convention d'opt-in a disparu du script")
    assert re.search(r'el\.hasAttribute\(AVANT_CLIC\)', SCRIPT), (
        "le script n'honore plus l'opt-in : le premier appui naviguerait")
    assert "ev.stopPropagation();" in SCRIPT and "ev.preventDefault();" in SCRIPT, (
        "le clic n'est plus retenu")
    # LES DEUX RAILS, CHACUN. La règle cherchait l'attribut n'importe où
    # dans la page : le rail des dix référentiels l'a ajouté à ses pastilles,
    # et cette seconde occurrence rendait muette la perte de la première —
    # la mutation qui l'ôte au rail DORA survivait.
    assert "+ ' data-bulle-avant-clic>'" in PAGE_JS, (
        "le rail DORA ne demande plus la lecture avant la navigation")
    assert "puce.setAttribute('data-bulle-avant-clic', '');" in PAGE_JS, (
        "le rail des dix référentiels ne demande plus la lecture avant la "
        "navigation")


def test_l_opt_in_reste_une_EXCEPTION():
    """SI L'ATTRIBUT SE RÉPANDAIT, chaque lien du site demanderait deux
    appuis au doigt — une gêne générale pour corriger un cas particulier."""
    porteurs = re.findall(r"data-bulle-avant-clic", INDEX)
    assert not porteurs, (
        "%d élément(s) de l'accueil retiennent leur premier clic : un lien "
        "qui demande deux appuis sans raison est une gêne" % len(porteurs))


def test_la_bulle_du_rail_s_ouvre_VERS_LE_BAS():
    """LE RAIL EST EN TÊTE DU PANNEAU. La convention maison pose la bulle
    AU-DESSUS de l'élément ; ici, elle sortirait de la zone défilante par le
    haut, là où rien ne la rattraperait."""
    m = re.search(r"\.dr-bloc\[data-tooltip\]::after\{(.*?)\}", SENTINEL, re.S)
    assert m, "la bulle du rail est introuvable"
    regle = m.group(1)
    assert re.search(r"top:calc\(100% \+ \d+px\)", regle), (
        "la bulle du rail ne s'ouvre plus sous le bloc : top=%r" % regle[:80])
    assert "white-space:pre-line" in regle, (
        "la bulle du rail perd ses sauts de ligne : ses quatre paragraphes "
        "se colleraient en un seul bloc")
    assert "opacity:0" in regle, (
        "la bulle du rail n'est plus fermée au repos")
    assert re.search(r"\.dr-bloc\[data-tooltip\]:hover::after\{opacity:1\}",
                     SENTINEL), (
        "la bulle du rail n'a plus de règle de survol : le script n'aurait "
        "rien à dériver, et elle ne s'ouvrirait ni au doigt ni à la souris")


# ══════════════════════════════════════════════════════════════════════════
#  6. LA RECETTE NE SE PÉRIME PAS EN SILENCE
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("ancre", [
    "#differenciateurs .diff-card[data-tooltip]",
    "#dora-rail-qualifier .dr-bloc[data-tooltip]",
    "css-bulle-ouverte",
    "bulle-annonce",
])
def test_la_recette_vise_des_ancres_QUI_EXISTENT(ancre):
    """UNE RECETTE QUI VISE UN SÉLECTEUR DISPARU NE MESURE PLUS RIEN — elle
    échouerait bruyamment, ou pire, sauterait son contrôle. Ce dépôt a déjà
    payé trois fois des ancres périmées."""
    recette = _lire("recette_infobulles_toucher.js")
    assert ancre in recette, (
        "la recette ne vise plus %r" % ancre)
    source = SCRIPT + SENTINEL + PAGE_JS + INDEX
    if ancre in ("css-bulle-ouverte", "bulle-annonce"):
        assert ancre in SCRIPT, (
            "%r a disparu du script : la recette mesure un identifiant mort"
            % ancre)
    else:
        cle = ancre.split()[-1].split("[")[0].lstrip(".#")
        assert cle in source, (
            "%r a disparu du code : la recette mesure un sélecteur mort"
            % cle)
