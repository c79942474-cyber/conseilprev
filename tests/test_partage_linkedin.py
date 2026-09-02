# -*- coding: utf-8 -*-
"""Partager un communiqué sur LinkedIn — et pourquoi le bouton n'est pas l'essentiel.

LA CONTRAINTE QUI COMMANDE TOUT. **LinkedIn ne prend qu'une URL.** Son point
d'entrée `share-offsite` a cessé, en 2021, d'honorer `title`, `summary` et
`mini` : ils sont ignorés en silence. La carte publiée dans le fil est
construite par SON robot, qui va lire la page visée et y chercher ses balises
OpenGraph.

CONSÉQUENCE, ET C'EST ELLE QUI FAIT LE TRAVAIL. Un bouton pointant vers
`/actualites` ferait que les quatre communiqués produisent la MÊME carte — même
titre, même résumé, même lien. Celui qui en partage deux publierait deux fois la
même chose. Le bouton seul n'aurait donc rien valu : ce qui compte est
l'ADRESSE PAR COMMUNIQUÉ, et les balises qu'elle porte.

CE QUE CES RÈGLES ÉPROUVENT :

  · que deux communiqués ne produisent JAMAIS la même carte — comparées entre
    elles, pas relues une par une ;
  · que le permalien soit ABSOLU : LinkedIn ne connaît pas le domaine d'où
    part le clic, et un chemin relatif publierait un lien mort ;
  · qu'un créneau inconnu rende 404 plutôt que la liste — servir la page sous
    une adresse inventée ferait qu'un lien erroné a l'air de marcher ;
  · qu'un titre corrigé ne casse pas un lien déjà publié ;
  · que la page ne fabrique aucune adresse elle-même ;
  · et qu'aucun paramètre de texte ne soit ajouté à l'adresse LinkedIn — les y
    remettre allongerait l'URL sans changer un mot de la publication.

UN DÉFAUT TROUVÉ EN CHEMIN, et qui n'a rien à voir avec LinkedIn : la
description de `/actualites` décrivait **la politique de confidentialité**. Un
copier-coller invisible à l'écran — elle ne s'affiche nulle part — et lisible
partout ailleurs : c'est elle que Google indexe et que LinkedIn met sous le
titre. Le défaut est resté tant que personne ne partageait la page ; le premier
partage l'aurait publié.
"""
import io
import os
import re
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import partage as P                                               # noqa: E402
import app as A                                                   # noqa: E402
import seo                                                        # noqa: E402

PAGE = io.open(os.path.join(ICI, "actualites.html"), encoding="utf-8").read()
ENTETES = {"User-Agent": "Mozilla/5.0 (recette)", "Accept-Language": "fr-FR",
           "Accept-Encoding": "identity"}


@pytest.fixture
def client():
    return A.app.test_client()


def _tete(html, motif):
    m = re.search(motif, html, re.S)
    return m.group(1).strip() if m else None


# ═══════════════════════════════════════════════════════════════════════════
#  1. LE POINT QUI DÉCIDE : DEUX COMMUNIQUÉS, DEUX CARTES
# ═══════════════════════════════════════════════════════════════════════════

def test_LE_POINT_QUI_DECIDE_deux_communiques_ne_partagent_jamais_la_meme_carte(client):
    """ÉPROUVÉ EN COMPARANT LES CARTES ENTRE ELLES, pas en relisant chacune.

    Une règle qui vérifierait « la page porte un og:title » passerait encore le
    jour où les quatre en portent le MÊME — c'est-à-dire le jour où la
    fonctionnalité ne sert plus à rien. Ce qui est vérifié est la DISTINCTION.
    """
    cartes = []
    for c in P.communiques():
        r = client.get(c["chemin"], headers=ENTETES)
        assert r.status_code == 200, (c["chemin"], r.status_code)
        h = r.get_data(as_text=True)
        cartes.append({
            "titre": _tete(h, r'<title>(.*?)</title>'),
            "og_titre": _tete(h, r'<meta property="og:title" content="([^"]*)"'),
            "desc": _tete(h, r'<meta name="description" content="([^"]*)"'),
            "og_url": _tete(h, r'<meta property="og:url" content="([^"]*)"'),
        })
    assert len(cartes) >= 2, "il faut deux communiqués pour que la règle distingue"
    for champ in ("titre", "og_titre", "desc", "og_url"):
        valeurs = [c[champ] for c in cartes]
        assert all(valeurs), "un communiqué ne porte pas de %s" % champ
        assert len(set(valeurs)) == len(valeurs), (
            "deux communiqués publient le même %s : partager l'un ou l'autre "
            "donne la même publication — %s" % (champ, valeurs))


def test_la_carte_dit_ce_que_dit_l_article_et_non_ce_qu_on_a_recopie(client):
    """Le titre servi est CELUI de l'article, extrait du HTML. Un titre recopié
    dans un module en produirait un second exemplaire, et c'est celui qu'on
    oublie de corriger qui partirait sur LinkedIn."""
    for c in P.communiques():
        h = client.get(c["chemin"], headers=ENTETES).get_data(as_text=True)
        titre = _tete(h, r'<title>(.*?)</title>')
        # Le titre servi est échappé pour l'attribut ; on compare sur le texte.
        import html as _h
        assert c["titre"] in _h.unescape(titre), (c["id"], titre[:80])
        assert c["resume"], "un communiqué sans résumé donnerait une carte nue"


# ═══════════════════════════════════════════════════════════════════════════
#  2. L'ADRESSE PARTAGÉE
# ═══════════════════════════════════════════════════════════════════════════

def test_le_permalien_est_absolu_sinon_le_partage_publie_un_lien_mort(client):
    """LinkedIn ne connaît pas le domaine d'où part le clic. Un chemin relatif
    produirait une publication vers une page introuvable — et une publication
    ne se reprend pas."""
    j = client.get("/api/partage/communiques", headers=ENTETES).get_json()
    assert j["ok"] and j["communiques"]
    for c in j["communiques"]:
        assert c["permalien"].startswith("http"), c
        assert c["linkedin"], c
        assert c["permalien"].rstrip("/") != seo.BASE.rstrip("/"), (
            "le permalien désigne la racine du site : tous les partages "
            "mèneraient à l'accueil")
    assert P.url_linkedin("/actualites/na4") is None, (
        "un chemin relatif est accepté comme permalien")
    assert P.url_linkedin("") is None


def test_aucun_texte_n_est_pre_rempli_dans_l_adresse_linkedin():
    """`title`, `summary` et `mini` traînent dans beaucoup d'exemples en ligne
    et sont ignorés depuis 2021. Les poser allongerait l'adresse sans changer un
    mot de la publication — et laisserait croire que le texte est maîtrisé ici,
    alors qu'il vient des balises de la page visée."""
    url = P.url_linkedin("https://exemple.test/actualites/na4-x")
    for mort in ("&title=", "&summary=", "&mini=", "&source="):
        assert mort not in url, (
            "un paramètre ignoré par LinkedIn est ajouté à l'adresse : %s" % mort)
    assert url.startswith(P.LINKEDIN)
    assert url.count("?") == 1


def test_un_creneau_inconnu_rend_404_et_non_la_liste(client):
    """Servir la liste sous une adresse inventée ferait qu'un lien erroné
    partagé sur LinkedIn paraît fonctionner, et publierait une carte qui ne
    correspond à rien de ce que l'auteur croyait envoyer."""
    for faux in ("nawak", "na9-inconnu", "quelque-chose", "na99"):
        assert client.get("/actualites/" + faux,
                          headers=ENTETES).status_code == 404, faux


def test_un_titre_corrige_ne_casse_pas_un_lien_deja_publie(client):
    """LA RÉSOLUTION NE REGARDE QUE LE PRÉFIXE. Un lien partagé il y a six mois
    porte le créneau d'alors ; le titre a pu être corrigé depuis. Faire dépendre
    la résolution du titre entier tuerait ce lien — et un lien mort publié sous
    votre nom coûte davantage qu'une adresse un peu vieillie."""
    c = P.communiques()[0]
    ancien = "/actualites/%s-un-titre-qui-n-existe-plus" % c["id"]
    r = client.get(ancien, headers=ENTETES)
    assert r.status_code == 200, ancien
    h = r.get_data(as_text=True)
    # …et la canonique désigne l'adresse ACTUELLE, pour que le moteur sache
    # laquelle des deux compte.
    assert c["chemin"] in _tete(h, r'<link rel="canonical" href="([^"]*)"'), h[:200]


def test_les_permaliens_figurent_au_plan_du_site(client):
    """Une adresse servie, indexable et partagée que le plan tait : un moteur
    ne connaîtrait que la liste, et un lien LinkedIn mènerait vers une page que
    rien n'a jamais annoncée."""
    x = client.get("/sitemap.xml", headers=ENTETES).get_data(as_text=True)
    for c in P.communiques():
        assert c["chemin"] in x, c["chemin"]


# ═══════════════════════════════════════════════════════════════════════════
#  3. LA PAGE NE FABRIQUE AUCUNE ADRESSE
# ═══════════════════════════════════════════════════════════════════════════

def test_la_page_ne_fabrique_aucune_adresse_de_partage():
    """Elle est statique : elle ne connaît ni le domaine servi — il vient de
    `SITE_BASE_URL` — ni la forme du point d'entrée LinkedIn. Les écrire ici en
    produirait un second exemplaire, qui se séparerait du premier au premier
    changement de domaine et publierait des liens vers un site qu'on a quitté."""
    i = PAGE.index("/api/partage/communiques")
    bloc = PAGE[max(0, i - 3000):i + 3000]
    sans_commentaires = re.sub(r"/\*.*?\*/", "", bloc, flags=re.S)
    assert "linkedin.com" not in sans_commentaires, (
        "la page fabrique elle-même l'adresse LinkedIn")
    assert "onrender.com" not in sans_commentaires
    assert "https://" not in sans_commentaires.replace('"/api/partage', '')


def test_chaque_communique_porte_son_bloc_de_partage():
    """Un communiqué sans bouton est un communiqué qu'on ne partagera pas.
    La règle compte les blocs face aux communiqués RÉELLEMENT lus, jamais face
    à un nombre écrit à la main."""
    ids_page = set(re.findall(r'class="na-share" data-na="(na\d*)"', PAGE))
    ids_lus = {c["id"] for c in P.communiques()}
    assert ids_page == ids_lus, (
        "des communiqués n'ont pas de bloc de partage, ou l'inverse : %s"
        % (ids_page ^ ids_lus))


def test_le_bloc_reste_masque_tant_que_le_serveur_n_a_pas_repondu():
    """Un bouton peint d'avance et câblé ensuite est cliquable pendant la
    seconde où il ne mène nulle part — et un partage LinkedIn vers une adresse
    vide se publie une fois, sans reprise possible."""
    for bloc in re.findall(r'<div class="na-share"[^>]*>', PAGE):
        assert "hidden" in bloc, bloc
    assert ".na-share[hidden]{display:none}" in PAGE, (
        "rien ne garantit que l'attribut `hidden` masque réellement le bloc")


# ═══════════════════════════════════════════════════════════════════════════
#  4. LE DÉFAUT TROUVÉ EN CHEMIN
# ═══════════════════════════════════════════════════════════════════════════

def test_la_description_de_la_page_decrit_LA_PAGE(client):
    """ELLE DÉCRIVAIT LA POLITIQUE DE CONFIDENTIALITÉ. Invisible à l'écran,
    lisible partout ailleurs : c'est elle que Google indexe et que LinkedIn met
    sous le titre. La règle ne fige aucune phrase — elle exige que la
    description parle de ce dont la page parle, en confrontant son vocabulaire
    aux thèmes déclarés par les articles."""
    h = client.get("/actualites", headers=ENTETES).get_data(as_text=True)
    desc = _tete(h, r'<meta name="description" content="([^"]*)"')
    assert desc, "la page n'a plus de description"
    import unicodedata

    def pur(t):
        return "".join(x for x in unicodedata.normalize("NFD", t)
                       if unicodedata.category(x) != "Mn").lower()
    themes = {t for c in P.communiques() for t in c["themes"]}
    assert themes, "aucun thème déclaré : la règle ne compare rien"
    plat = pur(desc)
    touches = [t for t in themes if pur(t) in plat]
    assert touches, (
        "la description ne nomme aucun des thèmes des communiqués (%s) : "
        "décrit-elle encore cette page ? — %r" % (sorted(themes), desc))
    for etranger in ("confidentialit", "donnees personnelles", "cookies"):
        assert etranger not in plat, (
            "la description parle d'une AUTRE page (%s) : %r" % (etranger, desc))
