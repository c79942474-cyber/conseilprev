# -*- coding: utf-8 -*-
"""La veille IA est LUE chez le site cyber, jamais collectée une seconde fois.

CE QUE LA MESURE A ÉTABLI, le 6 septembre 2026, en lançant
`outils/recette_veille_flux.py` depuis le shell du service cyber : sur les
trente-six adresses de son catalogue, VINGT SERVENT UN FLUX NON VIDE — dont
quatre sources institutionnelles en gouvernance de l'IA : CNIL (10 éléments),
Commission européenne (10), NIST (40), CEPD (10).

C'est ce chiffre qui a tranché. Écrire ici un second collecteur — catalogue,
lecture Atom, états de santé, rotation, budget — pour atteindre exactement ces
quatre sources aurait produit DEUX DÉFINITIONS DU MÊME MÉTIER, qui divergeraient
le jour où l'une des deux serait corrigée.

CES RÈGLES SONT COMPORTEMENTALES. Le module ne touche ni au réseau ni à une
base : on lui donne un texte, on mesure ce qu'il en tire. Une fonction qui ouvre
une socket ne s'éprouve qu'en ouvrant une socket — donc jamais dans une suite de
règles, donc jamais vraiment.
"""
import os
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import veille_ia                                                   # noqa: E402

# Un flux tel que `conseilprevcyber` le sert — forme relevée sur sa route
# `/veille.xml`, pas inventée : `<category scheme="domaine" term="…"/>`.
FLUX = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Veille</title>
  <updated>2026-09-06T08:00:00Z</updated>
  <entry>
    <title>La CNIL publie ses recommandations sur les systèmes d'IA</title>
    <link rel="alternate" href="https://www.cnil.fr/fr/exemple"/>
    <id>cnil-1</id>
    <updated>2026-09-05T09:00:00Z</updated>
    <author><name>CNIL</name></author>
    <category scheme="domaine" term="ia_gouvernance"/>
    <category scheme="pays" term="FR"/>
    <category scheme="theme" term="IA Act"/>
    <category scheme="theme" term="RGPD"/>
    <summary>Un chapeau tel que l'éditeur le publie dans son flux.</summary>
  </entry>
  <entry>
    <title>Avis de sécurité sur un automate programmable</title>
    <link rel="alternate" href="https://www.cert.ssi.gouv.fr/exemple"/>
    <id>certfr-1</id>
    <updated>2026-09-04T09:00:00Z</updated>
    <author><name>CERT-FR</name></author>
    <category scheme="domaine" term="cyber_industriel"/>
    <summary>Un avis qui ne relève pas de la gouvernance de l'IA.</summary>
  </entry>
  <entry>
    <title>NIST — mise à jour du cadre de gestion des risques de l'IA</title>
    <id>nist-1</id>
    <updated>2026-09-03T09:00:00Z</updated>
    <author><name>NIST</name></author>
    <category scheme="domaine" term="ia_gouvernance"/>
    <summary>Une entrée sans lien : publiée quand même, sans lien.</summary>
  </entry>
</feed>"""


# ══════════════════════════════════════════════════════════════════════════
# 1. LE FILTRE PORTE SUR LA FACETTE, JAMAIS SUR LES MOTS
# ══════════════════════════════════════════════════════════════════════════
#
# LES RÈGLES CI-DESSOUS PASSENT LE DOMAINE EXPLICITEMENT, et s'identifient par
# `guid`. C'est une correction : écrites d'un jet, elles s'identifiaient par
# `emetteur` et s'appuyaient sur la valeur par défaut — si bien qu'une mutation
# de la constante, ou de l'extraction de l'émetteur, en faisait tomber quatre à
# la fois. Une règle qui dépend de tout ne dit plus lequel de ses appuis a cédé.

IA = "ia_gouvernance"


def _guids(flux=FLUX, **kw):
    return [e["guid"] for e in veille_ia.entrees(flux, **kw)]


def test_seules_les_entrees_du_domaine_ia_sont_retenues():
    """Le classement est un travail que le site amont a déjà fait. Le refaire
    au jugé sur les mots du titre ferait entrer « le RGPD des caméras » dans la
    gouvernance de l'IA et sortir un avis qui ne prononce pas le mot."""
    assert _guids(domaine=IA) == ["cnil-1", "nist-1"], _guids(domaine=IA)


def test_le_filtre_ne_regarde_pas_le_texte_des_entrees():
    """LE TÉMOIN QUI DISTINGUE LES DEUX IMPLÉMENTATIONS. Une entrée dont le
    titre parle abondamment d'IA mais que le site amont a classée ailleurs ne
    doit PAS remonter : c'est exactement ce qu'un filtre par mots-clés ferait,
    et il paraîtrait correct sur tous les autres exemples."""
    piege = FLUX.replace(
        "<title>Avis de sécurité sur un automate programmable</title>",
        "<title>Intelligence artificielle et IA Act dans les automates</title>")
    assert "certfr-1" not in _guids(piege, domaine=IA), (
        "une entrée classée « cyber_industriel » est remontée parce que son "
        "titre parle d'IA : le filtre lit le texte au lieu de la facette")


def test_un_domaine_inexistant_rend_une_liste_vide_sans_lever():
    """Un libellé voisin de celui du site amont ne lèverait rien et rendrait
    zéro élément — panne muette. La règle mesure le comportement du filtre ;
    le NOM de la facette est tenu par la règle suivante."""
    assert veille_ia.entrees(FLUX, domaine="gouvernance_ia") == []


def test_la_facette_porte_exactement_le_nom_du_site_amont():
    """`veille_sources.DOMAINES` du site cyber nomme ce domaine
    « ia_gouvernance ». Un libellé voisin écrit ici — `gouvernance_ia`,
    `ia-gouvernance` — filtrerait sur un domaine qui n'existe pas : aucune
    erreur, aucune trace, un bloc vide pour toujours.

    Cette règle est SEULE à tenir le nom, et les autres passent donc le domaine
    explicitement : sans cela, une mutation de la constante les ferait toutes
    tomber, et aucune ne dirait ce qui a cédé.
    """
    assert veille_ia.DOMAINE_IA == "ia_gouvernance"


def test_le_domaine_par_defaut_est_celui_de_la_constante():
    """Le témoin des deux règles précédentes : nommer la facette ne sert à rien
    si l'appel sans argument filtre sur autre chose."""
    assert veille_ia.entrees(FLUX) == veille_ia.entrees(
        FLUX, domaine=veille_ia.DOMAINE_IA)


# ══════════════════════════════════════════════════════════════════════════
# 2. CE QUI RESTE À L'ÉMETTEUR
# ══════════════════════════════════════════════════════════════════════════

def _par_guid(guid, flux=FLUX):
    trouve = [e for e in veille_ia.entrees(flux, domaine=IA) if e["guid"] == guid]
    return trouve[0] if trouve else None


def test_chaque_entree_porte_son_emetteur_et_son_chapeau():
    """Les titres et les chapeaux appartiennent aux éditeurs. Republier un
    chapeau sans son émetteur en ferait notre propos, ce qu'il n'est pas."""
    cnil = _par_guid("cnil-1")
    assert cnil is not None, _guids(domaine=IA)
    assert cnil["emetteur"] == "CNIL", cnil
    assert cnil["resume"].startswith("Un chapeau"), cnil
    assert cnil["lien"] == "https://www.cnil.fr/fr/exemple", cnil
    assert cnil["themes"] == ["IA Act", "RGPD"], cnil


def test_une_entree_sans_lien_est_publiee_sans_lien_et_non_omise():
    """Faire disparaître l'actualité par-dessus le marché priverait le lecteur
    de l'information ET de la raison de son absence. C'est la règle que le site
    amont s'applique à lui-même ; on ne la contredit pas en aval."""
    nist = _par_guid("nist-1")
    assert nist is not None, (
        "l'entrée sans lien a disparu de la liste au lieu d'y figurer sans lien")
    assert nist["lien"] == "", nist


def test_une_entree_sans_titre_est_ecartee():
    """Elle produirait une carte vide et cliquable, qui ne dit rien de ce
    qu'elle ouvre."""
    sans_titre = FLUX.replace(
        "<title>NIST — mise à jour du cadre de gestion des risques de l'IA</title>",
        "<title></title>")
    assert "nist-1" not in _guids(sans_titre, domaine=IA), _guids(sans_titre, domaine=IA)


# ══════════════════════════════════════════════════════════════════════════
# 3. UN FLUX ABSENT NE FAIT PAS TOMBER LA PAGE
# ══════════════════════════════════════════════════════════════════════════

def test_un_flux_illisible_rend_une_liste_vide_sans_lever():
    """Le site amont peut être indisponible, redéployé, ou servir une page
    d'erreur. La page qui affiche ce bloc a d'autres choses à montrer."""
    for illisible in ("", "<html><body>502 Bad Gateway</body></html>",
                      "<feed", "{\"json\": true}"):
        assert veille_ia.entrees(illisible) == [], repr(illisible)


# ══════════════════════════════════════════════════════════════════════════
# 4. LA CADENCE — HEBDOMADAIRE, ET MESURÉE PAR SES DEUX BORDS
# ══════════════════════════════════════════════════════════════════════════

def test_six_jours_ne_suffisent_pas_et_huit_jours_declenchent():
    """Vérifier seulement qu'une semaine déclenche laisserait passer un `>= 0` :
    tout déclencherait, et la règle resterait verte."""
    maintenant = 1_800_000_000.0
    assert veille_ia.est_du(maintenant - 6 * 86400, maintenant) is False
    assert veille_ia.est_du(maintenant - 8 * 86400, maintenant) is True
    assert veille_ia.INTERVALLE_HEURES == 168


def test_un_horodatage_absent_ou_illisible_declenche():
    """Rien à comparer n'est pas une raison d'attendre : ce serait laisser un
    bloc vide une semaine pour se conformer à une cadence qu'on ne mesure pas.

    `float("NaN")` NE LÈVE RIEN, et toute comparaison avec NaN vaut faux : un
    horodatage corrompu bloquerait le rafraîchissement POUR TOUJOURS, sans une
    ligne de journal. Le défaut a été trouvé par une règle sur le site cyber ;
    cette règle-ci est là pour qu'on ne le réintroduise pas.
    """
    maintenant = 1_800_000_000.0
    for illisible in (None, "", "bientôt", "NaN", "inf", "-inf", float("nan")):
        assert veille_ia.est_du(illisible, maintenant) is True, repr(illisible)
