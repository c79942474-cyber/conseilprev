"""UN PRÉCHARGEMENT QUI RATE SA CLÉ NE FAIT PAS GAGNER DE TEMPS : IL DOUBLE LA REQUÊTE.

CE QUI A ÉTÉ TROUVÉ, LE 29 AOÛT 2026, EN AUDITANT LES PAGES DE SENTINEL.
Le chargement du tableau de bord émettait quatre-vingt-quatorze requêtes, dont
neuf vers `/api/implantation` et six vers `/api/sources`. Deux défauts distincts
s'additionnaient, et chacun était invisible : la page fonctionnait.

LE PREMIER — LA CLÉ QUI NE CORRESPOND PAS. `panorama.html` ouvre par un bloc de
préchargement : cinq requêtes partent pendant que le navigateur analyse encore
les 800 Ko qui suivent, et `preAPI(url)` rend plus tard la promesse déjà lancée,
retrouvée PAR SON URL. Quatre des cinq URL étaient consommées à l'identique.
La cinquième était préchargée « /api/implantation » et demandée
« /api/implantation?horizon=2030 » : la clé ne correspondait jamais. Le
préchargement partait, sa réponse n'était jamais lue, et une seconde requête
était émise derrière.

LE SECOND — LE GARDE-FOU DÉCLARÉ AU MAUVAIS ENDROIT. `renderAll()` est rejoué à
l'arrivée des données en direct, c'est délibéré. Il appelle `reste()`, protégé
par un drapeau `fait`… déclaré DANS `renderAll`. Un second `renderAll` repart
donc avec un drapeau neuf, et tout `reste()` se rejoue — dont la requête des
sources, qui ne dépend pas des données en direct.

MESURÉ, session administrateur, `/panorama?embed=1` :

    avant                          après
    /api/implantation   ×3         ×1
    /api/sources        ×2         ×1
    28 pays, 28 boutons            28 pays, 28 boutons

Et sur un chargement complet de Sentinel, qui embarque trois fois ce module :
94 requêtes et 2 182 Ko avant, 85 requêtes et 1 960 Ko après.

CE QUE CES RÈGLES GARDENT. Que toute URL préchargée soit consommée sous LA MÊME
clé — c'est la propriété générale dont l'absence a produit le premier défaut ;
et que la requête des sources reste protégée contre le second rendu, avec un
drapeau qui se rabaisse en cas d'échec.
"""
import io
import os
import re

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = io.open(os.path.join(ICI, 'panorama.html'), encoding='utf-8').read()


def _cibles():
    """Les URL que le bloc d'ouverture précharge."""
    m = re.search(r'var CIBLES = \[(.*?)\];', PAGE, re.S)
    assert m, "le bloc de préchargement de panorama.html est introuvable"
    return re.findall(r'"([^"]+)"', m.group(1))


def _consommateurs():
    """Le premier littéral de chaque appel `preAPI(...)`.

    `preAPI("/api/implantation?horizon=" + h)` construit son URL : on retient
    « /api/implantation?horizon= », la part fixe, qui suffit à décider si la
    clé préchargée peut correspondre."""
    return re.findall(r'preAPI\(\s*"([^"]*)"', PAGE)


def test_le_bloc_de_prechargement_se_lit_toujours():
    """Toutes les règles de ce fichier en dépendent."""
    cibles, cons = _cibles(), _consommateurs()
    assert len(cibles) >= 4, "moins de quatre URL préchargées : %s" % cibles
    assert len(cons) >= 4, "moins de quatre consommateurs `preAPI` : %s" % cons


@pytest.mark.parametrize('url', _cibles())
def test_toute_url_prechargee_est_consommee_sous_la_meme_cle(url):
    """LA RÈGLE PRINCIPALE. `preAPI` retrouve la promesse par son URL exacte.
    Une URL préchargée que personne ne demande sous cette forme coûte une
    requête et n'en évite aucune."""
    cons = _consommateurs()
    exact = [c for c in cons if c == url]
    construit = [c for c in cons if c != url and url.startswith(c) and c.endswith(('=', '/', '?', '&'))]
    assert exact or construit, (
        "« %s » est préchargée mais aucun appel `preAPI` ne la demande sous "
        "cette clé. Les clés demandées sont : %s.\n"
        "Le préchargement partira, sa réponse ne sera jamais lue, et une "
        "seconde requête sera émise derrière." % (url, ', '.join(cons)))


@pytest.mark.parametrize('url', _cibles())
def test_aucune_url_prechargee_n_est_plus_courte_que_ce_qui_est_demande(url):
    """LE DÉFAUT EXACT, PRIS DANS L'AUTRE SENS. Précharger « /api/x » quand le
    code demande « /api/x?param=… », c'est précharger une réponse qui ne sera
    jamais réclamée. C'est ce qui se passait pour le référentiel
    d'implantation."""
    trop_courtes = [c for c in _consommateurs()
                    if c != url and c.startswith(url) and len(c) > len(url)]
    assert not trop_courtes, (
        "« %s » est préchargée, mais le code demande « %s » — plus long. La "
        "clé ne correspondra jamais." % (url, ', '.join(trop_courtes)))


# ── LE SECOND RENDU NE REDEMANDE PAS CE QUI NE CHANGE PAS ────────────────

def _corps(nom):
    d = PAGE.index('function %s(' % nom)
    return PAGE[d:PAGE.index('\n}', d)]


def test_la_requete_des_sources_est_protegee_contre_le_second_rendu():
    """`renderAll()` est rejoué à l'arrivée des données en direct — c'est
    voulu. Le drapeau qui protège `reste()` est déclaré DANS `renderAll` : il
    ne protège donc rien d'un rendu à l'autre."""
    corps = _corps('registreSources')
    assert 'SRC_LANCE' in corps, (
        "la requête des sources n'est plus protégée : elle repartira à chaque "
        "rendu, alors que la liste des sources ne dépend pas des données en "
        "direct")
    assert re.search(r'if\s*\(\s*SRC_LANCE\s*\)\s*return', corps), (
        "le drapeau existe mais n'interrompt plus la fonction")
    assert re.search(r'SRC_LANCE\s*=\s*true', corps), (
        "le drapeau n'est jamais levé : il ne protège rien")


def test_le_drapeau_des_sources_se_rabaisse_en_cas_d_echec():
    """Un drapeau levé et jamais rabaissé condamnerait la section pour toute la
    visite au premier incident réseau."""
    corps = _corps('registreSources')
    m = re.search(r'\.catch\(function\([^)]*\)\s*\{(.{0,400})', corps, re.S)
    assert m, "la branche d'échec de registreSources a disparu"
    assert 'SRC_LANCE = false' in m.group(1), (
        "le drapeau n'est pas rabaissé en cas d'échec : un incident réseau "
        "priverait le visiteur de la section pour toute sa visite")


def test_le_referentiel_d_implantation_n_est_demande_qu_une_fois():
    """Deux endroits de la page lisaient ce référentiel, chacun avec sa propre
    requête : la carte d'implantation, et la liste de pays du comparateur
    financier. Ils partagent désormais la même promesse."""
    assert 'function implReponse(' in PAGE, (
        "le chargeur partagé du référentiel d'implantation a disparu")
    directs = re.findall(r"fetch\(\s*'(/api/implantation[^']*)'", PAGE)
    directs += re.findall(r'fetch\(\s*"(/api/implantation[^"]*)"', PAGE)
    assert not directs, (
        "appel(s) direct(s) à %s, hors du chargeur partagé : la même réponse "
        "sera demandée deux fois" % ', '.join(directs))


def test_une_promesse_rejetee_ne_reste_pas_en_cache():
    """Mémoriser une promesse rejetée condamnerait tout appel ultérieur à
    échouer sans même réessayer."""
    d = PAGE.index('function implReponse(')
    corps = PAGE[d:PAGE.index('\n}', d)]
    assert 'delete _IMPL_PROMESSES' in corps, (
        "une promesse rejetée reste mémorisée : le changement d'horizon "
        "échouera définitivement après un seul incident réseau")
