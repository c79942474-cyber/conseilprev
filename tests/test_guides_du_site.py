"""LE GUIDE DE PAGE DU SITE PUBLIC — INSTALLÉ PARTOUT, ET ATTEIGNABLE.

CE QUI A DÉCLENCHÉ CE FICHIER. Sentinel a ses guides depuis longtemps :
soixante-dix-huit panneaux, un guide chacun. Le SITE, lui, n'en avait aucun.
Vingt-huit adresses publiques — dont le panorama, l'observatoire, l'étude
d'enveloppe et l'empreinte du parc, qui sont les documents les plus denses des
deux sites — n'offraient au lecteur aucune indication sur ce qu'il regardait ni
sur l'ordre dans lequel le lire.

CE QUE LES DEUX AUTRES SITES ONT APPRIS, ET QUI EST TENU ICI.

  · L'ANCRAGE EST UNE PROPRIÉTÉ, PAS UNE CLASSE. Sur conseilprevcyber le bouton
    s'ancrait sur `h1.page-h` ; vingt-cinq panneaux titraient autrement et leur
    guide, pourtant écrit, restait inatteignable — sans qu'aucune erreur ne le
    signale. Ici l'ancrage descend une échelle de replis, et une page sans titre
    ni navigation garde son bouton.

  · LA CLÉ RÉPÉTÉE NE LÈVE RIEN. `GUIDES["/x"] = …` écrit deux fois écrase le
    premier guide en silence. Vingt-six guides de Sentinel avaient disparu
    ainsi.

  · UN CONTRÔLE QUI ACCEPTE 200 ACCEPTE AUSSI LA PAGE DE CONNEXION. Les quatre
    études sont réservées : sans vérifier l'adresse d'arrivée, on mesure le
    guide du formulaire de connexion en croyant mesurer celui de l'étude.

CE QUE CES CONTRÔLES NE PEUVENT PAS FAIRE. Juger qu'un guide décrit fidèlement
sa page : cela se vérifie en lisant la page. Ni mesurer la lisibilité réelle du
panneau, qui dépend du fond de la page et se constate dans un navigateur — ce
qui a été fait, et reste dans le presse-papier de la mise au point.
"""
import io
import json
import os
import re
import subprocess

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _lire(nom):
    return io.open(os.path.join(ICI, nom), encoding="utf-8").read()


JS = _lire("guide.js")
APP = _lire("app.py")


# ── LES ADRESSES PUBLIQUES, D'APRÈS LE REGISTRE DU SERVEUR ───────────────

def _registre(nom):
    """Le contenu du dictionnaire `nom = { … }` de app.py, sous forme
    (adresse, fichier). Lu dans le REGISTRE, jamais recopié ici."""
    d = APP.index("%s = {" % nom)
    f = APP.index("\n}", d)
    return re.findall(r"'([^']+)':\s*'([^']+)'", APP[d:f])


PUBLIQUES = _registre("PAGES")
RESERVEES = _registre("PAGES_RESERVEES")
ADRESSES = [a for a, _ in PUBLIQUES + RESERVEES]
FICHIERS = sorted({f for _, f in PUBLIQUES + RESERVEES})


# ── LES GUIDES, RELEVÉS DANS guide.js ────────────────────────────────────

CLES = re.findall(r'GUIDES\[\s*"([^"]+)"\s*\]\s*=', JS)


def test_le_relevé_des_adresses_n_est_pas_vide():
    """Si la lecture du registre cessait de fonctionner, tous les contrôles de
    couverture passeraient sur une liste vide."""
    assert len(PUBLIQUES) >= 20, "seulement %d pages publiques relevées" % len(PUBLIQUES)
    assert len(RESERVEES) >= 3, "seulement %d pages réservées relevées" % len(RESERVEES)
    assert len(CLES) >= 20, "seulement %d guides relevés" % len(CLES)


def test_aucune_clé_de_guide_répétée():
    """Une affectation répétée écrase le guide précédent sans rien lever."""
    vus, doubles = set(), []
    for c in CLES:
        (doubles.append(c) if c in vus else vus.add(c))
    assert not doubles, (
        "guides écrits deux fois — le second écrase le premier en silence : %s"
        % ", ".join(sorted(set(doubles))))


@pytest.mark.parametrize("adresse", sorted(set(ADRESSES)))
def test_chaque_adresse_publiée_a_son_guide(adresse):
    assert adresse in CLES, (
        "%s tombe sur le guide générique : « cette page fait partie du site » "
        "n'apprend rien à personne" % adresse)


def test_aucun_guide_sans_adresse():
    """Un guide dont l'adresse n'est plus publiée ne s'ouvre jamais, et fait
    croire à une couverture qu'il ne rend pas."""
    fantomes = sorted(c for c in CLES if c not in ADRESSES)
    assert not fantomes, (
        "guides écrits pour des adresses que le serveur ne publie pas : %s"
        % ", ".join(fantomes))


# ── LE MODULE EST CHARGÉ PAR CHAQUE PAGE ─────────────────────────────────

@pytest.mark.parametrize("fichier", FICHIERS)
def test_chaque_gabarit_publié_charge_le_module(fichier):
    """Sans le script, pas de bouton — et rien ne le signale : une page qui ne
    charge pas un script n'est pas une page en erreur."""
    assert '/guide.js' in _lire(fichier), (
        "%s ne charge pas /guide.js : la page n'aura aucun bouton d'aide"
        % fichier)


def test_sentinel_ne_charge_pas_le_module_du_site():
    """Sentinel a son propre mécanisme, panneau par panneau. Deux boutons
    d'aide côte à côte, dont l'un ignore le panneau ouvert, valent moins
    qu'un seul."""
    assert '/guide.js' not in _lire("sentinel.html"), (
        "sentinel.html charge le guide du site : il doublerait son propre "
        "bouton, qui lui est contextuel au panneau ouvert")


def test_le_module_se_retire_devant_celui_de_sentinel():
    """La consigne ci-dessus ne suffit pas : le module doit refuser de lui-même
    si les guides de panneau sont présents."""
    i = JS.index("function init()")
    corps = JS[i:i + 900]
    assert "window.PAGE_GUIDES" in corps and "return" in corps, (
        "le module ne se retire plus devant les guides de panneau de Sentinel")


# ── L'ANCRAGE EST UNE PROPRIÉTÉ ──────────────────────────────────────────

def _corps_ancrage():
    i = JS.index("function poserBarre(")
    return JS[i:JS.index("\n  }", i)]


def test_l_ancrage_ne_dépend_d_aucune_classe():
    """C'est le défaut qui a rendu vingt-cinq guides inatteignables sur l'autre
    site : `querySelector(\"h1.page-h\")` rendait null, la fonction sortait, et
    le bouton n'existait pas."""
    corps = _corps_ancrage()
    assert 'querySelector("body > header, body > nav")' in corps, (
        "l'ancrage de tête a changé de forme : vérifier qu'il ne repose pas "
        "sur un nom de classe")
    assert 'querySelector("h1")' in corps, (
        "le repli sur le premier titre a disparu")
    for classe in re.findall(r'querySelector\("([^"]+)"\)', corps):
        assert "." not in classe, (
            "l'ancrage repose de nouveau sur une classe (%s) : toute page qui "
            "titre autrement perdra son bouton, en silence" % classe)


def test_une_page_sans_titre_ni_navigation_garde_son_bouton():
    """La carte plein écran n'a ni l'un ni l'autre. Sans ce dernier repli, elle
    n'aurait aucun bouton — et c'est une des pages qui en a le plus besoin."""
    corps = _corps_ancrage()
    assert "flottante" in corps and "document.body.insertBefore" in corps, (
        "le repli flottant a disparu : une page sans en-tête ni titre perdrait "
        "son bouton")
    carte = _lire("map.html")
    assert not re.search(r"<body[^>]*>\s*<(?:header|nav)\b", carte), (
        "map.html a désormais une navigation de tête : le repli flottant n'est "
        "plus éprouvé par aucune page réelle, et ce contrôle doit être revu")


def test_le_bouton_flottant_défait_la_mise_en_page_du_flux():
    """`max-width` et `margin:auto` de la barre en flux la recentraient une
    fois flottante, et le bouton sortait de l'écran par la droite. La règle
    doit défaire chacune de ces propriétés, pas seulement la position."""
    i = JS.index(".cp-guide-bar.flottante{")
    regle = JS[i:JS.index("}", i)]
    for prop in ("max-width:none", "margin:0", "width:auto", "left:auto"):
        assert prop in regle, (
            "la règle flottante ne défait plus « %s » : le bouton se recentre "
            "et déborde de l'écran" % prop)


def test_le_bouton_flottant_ne_recouvre_pas_le_coin_occupé():
    """La carte pose son compteur dans le coin haut-droit. Le relevé doit se
    faire AVANT l'insertion : sondé après, il ne trouve que la barre elle-même
    — et le bouton s'affiche en cachant l'autre, sans que rien ne le dise."""
    corps = _corps_ancrage()
    i = corps.index("elementFromPoint(innerWidth - 24, 24)")
    j = corps.index('bar.classList.add("flottante")')
    assert i < j, (
        "le coin est sondé APRÈS l'insertion de la barre : le relevé ne "
        "trouvera qu'elle-même, et le bouton recouvrira ce qui s'y trouvait")


def test_la_palette_est_lue_sur_ce_qui_est_peint():
    """Le site public est sombre, les études sont claires. Une palette écrite
    en dur serait juste sur la moitié des pages et illisible sur l'autre. Trois
    pages ne peignent leur fond ni sur `body` ni sur `html`, et le site public
    le peint par un dégradé : un relevé qui s'arrête à `backgroundColor` de
    `body` répond « transparent » et se trompe de moitié."""
    i = JS.index("function fondSombre(")
    corps = JS[i:JS.index("\n  }", i)]
    assert "elementFromPoint" in corps, (
        "le module ne regarde plus ce qui est peint derrière le bouton : il "
        "retombe sur la déclaration de `body`, transparente sur tout le site")
    fond = JS[JS.index("function _fondDe("):JS.index("function fondSombre(")]
    assert "backgroundImage" in fond, (
        "un dégradé n'est pas une `backgroundColor` : sans lire l'image de "
        "fond, le site public est classé « clair »")
    lum = JS[JS.index("function _lum("):JS.index("function _fondDe(")]
    assert "0.2126" in lum, "le calcul de luminance a disparu"
    assert "parseFloat(m[4]) < 0.5" in lum, (
        "le canal alpha n'est plus regardé : `rgba(0,0,0,0)` se lira « noir » "
        "et toute page transparente sera classée sombre")


# ── CE QUE LE GUIDE REND VRAIMENT ────────────────────────────────────────

def _rendu(adresses):
    """La résolution TELLE QUE LE NAVIGATEUR L'EXÉCUTE. Chercher un nom dans le
    fichier ne prouverait rien : renommer le repli à sa déclaration laisse le
    nom présent à son point d'usage."""
    d = JS.index("  var GUIDES = {};")
    f = JS.index("  function fondSombre(")
    code = (JS[d:f]
            + "\nvar demandes = " + json.dumps(adresses) + ";\n"
            + "var out = {};\n"
            + "demandes.forEach(function(c){\n"
            + "  var g = guidePour(c) || GUIDE_DEFAULT;\n"
            + "  out[c] = {t: g.t, p: g.p, s: g.s, k: g.k, l: g.l};\n"
            + "});\n"
            + "console.log(JSON.stringify(out));\n")
    r = subprocess.run(["node", "-e", code], capture_output=True, text=True)
    assert r.returncode == 0, "guide.js n'est plus évaluable : %s" % r.stderr[-500:]
    return json.loads(r.stdout)


RENDUS = _rendu(sorted(set(ADRESSES)) + ["/adresse-qui-n-existe-pas"])
REPLI = RENDUS["/adresse-qui-n-existe-pas"]


def test_une_adresse_inconnue_reçoit_quand_même_un_guide():
    """Le repli doit rester opérant : une page ajoutée demain, avant qu'on lui
    écrive son guide, doit ouvrir quelque chose plutôt que rien."""
    assert REPLI["t"], "une adresse inconnue n'obtient plus aucun guide"
    assert len(REPLI["s"] or []) >= 2


@pytest.mark.parametrize("adresse", sorted(set(ADRESSES)))
def test_aucune_page_ne_tombe_sur_le_repli(adresse):
    assert RENDUS[adresse]["t"] != REPLI["t"], (
        "%s rend le guide générique — « %s »" % (adresse, REPLI["t"]))


@pytest.mark.parametrize("adresse", sorted(set(ADRESSES)))
def test_un_guide_situe_la_page_et_dit_quoi_en_faire(adresse):
    g = RENDUS[adresse]
    assert len(g["t"].strip()) >= 5, "%s : titre trop court" % adresse
    assert len(g["p"].strip()) >= 60, (
        "%s : chapeau de %d caractères, trop court pour situer la page"
        % (adresse, len(g["p"].strip())))
    assert len(g["s"] or []) >= 1, "%s : aucune indication d'usage" % adresse
    for x in (g["s"] or []):
        assert len(x.strip()) >= 40, "%s : étape trop courte — « %s »" % (adresse, x)


@pytest.mark.parametrize("adresse", sorted(set(ADRESSES)))
def test_les_liens_d_un_guide_mènent_quelque_part(adresse):
    """Un guide qui renvoie vers une adresse supprimée envoie le lecteur dans
    le mur — et c'est le guide qui l'y a envoyé."""
    connues = set(ADRESSES) | {"/sentinel", "/login"}

    def nu(x):
        return x.split("#")[0].rstrip("/") or "/"

    morts = [x[1] for x in (RENDUS[adresse]["l"] or []) if nu(x[1]) not in connues]
    assert not morts, "%s : liens vers des adresses inexistantes — %s" % (adresse, morts)


def test_chaque_guide_dit_aussi_ce_que_la_page_ne_fait_pas():
    """La section « à savoir » n'est pas un glossaire de courtoisie : c'est là
    que se dit la limite de la page — ce qu'elle ne fait pas, ou ce qu'un
    chiffre n'y prouve pas. C'est précisément ce qu'un titre ne dit jamais, et
    ce qu'un guide générique ne peut pas dire."""
    sans = sorted(a for a in set(ADRESSES) if not (RENDUS[a]["k"] or []))
    assert not sans, (
        "guides sans aucune notion ni limite énoncée : %s" % ", ".join(sans))
