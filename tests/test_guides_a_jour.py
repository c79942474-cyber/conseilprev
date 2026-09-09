# -*- coding: utf-8 -*-
"""LES GUIDES DISENT-ILS ENCORE LA VÉRITÉ SUR LEUR PANNEAU ?

CE QUI A DÉCLENCHÉ CE FICHIER. `test_guides_sentinel` tient les propriétés
STRUCTURELLES des guides : une clé par panneau, un panneau par clé, un bouton
sur chaque panneau, de la substance derrière chaque titre. Il le dit lui-même :
« CE QUE CES CONTRÔLES NE PEUVENT PAS FAIRE. Juger la JUSTESSE d'un guide. »

Or un guide est de la PROSE, et la prose recopie. Un guide qui annonce « six
champs » là où le code en déclare huit n'est pas un guide un peu vieux : c'est
un guide qui envoie chercher deux champs qui n'existent pas, ou qui en laisse
deux de côté. Et il reste vert éternellement, puisque aucune règle ne lit le
nombre.

CE QUI A ÉTÉ TROUVÉ EN ÉCRIVANT CE FICHIER. La doctrine de `finops_ia` annonçait
« Six champs comblent cela » DEPUIS SON ORIGINE, alors que le registre en avait
reçu huit et que le module en lisait huit. La phrase a traversé une migration,
une revue et deux batteries de mutations sans que rien ne la contredise — parce
qu'aucune batterie ne mute un nombre écrit en toutes lettres dans un
commentaire.

CE QUE CES RÈGLES GARDENT. Chaque nombre qu'un guide ou une doctrine ANNONCE est
comparé à la table qui le DÉTERMINE. Pas la formulation, pas le ton : le nombre.

CE QU'ELLES NE PEUVENT PAS FAIRE. Juger qu'un guide décrit fidèlement son
panneau — cela se vérifie en lisant le panneau. Elles attrapent la classe
d'erreur qui survit le plus longtemps : le chiffre qui a cessé d'être vrai.
"""
import io
import os
import re
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import finops_ia as F                                              # noqa: E402
import secteurs_nace as N                                          # noqa: E402

MOTEUR = io.open(os.path.join(ICI, "sentinel.page.js"), encoding="utf-8").read()
DOCTRINE = io.open(os.path.join(ICI, "finops_ia.py"), encoding="utf-8").read()

LETTRES = {6: "[Ss]ix", 8: "[Hh]uit", 9: "[Nn]euf", 13: "[Tt]reize",
           22: "[Vv]ingt-deux"}


def _sans_commentaires(js):
    """Le JavaScript débarrassé de ses commentaires.

    LE DÉFAUT QUE CETTE FONCTION ÉVITE, RENCONTRÉ ICI MÊME. Une règle exigeait
    « ne peut pas mesurer » dans l'intro des parcours. La mutation qui
    supprimait la phrase VUE PAR LE LECTEUR a survécu : le commentaire qui
    explique pourquoi cette phrase existe contient les mêmes mots. La règle
    était verte grâce à sa propre justification."""
    js = re.sub(r"/\*.*?\*/", " ", js, flags=re.S)
    return re.sub(r"^\s*//.*$", " ", js, flags=re.M)


def _docstring(source):
    """Le docstring de module, et non les vingt-quatre caractères qui le précèdent.

    UN PREMIER JET écrivait `source[:source.index('\"\"\"', 3)]`, en croyant
    borner le docstring par sa fermeture. Le fichier commence par une ligne
    d'encodage : l'index 3 tombe avant l'OUVERTURE, et la règle mesurait la
    ligne `# -*- coding: utf-8 -*-`. Elle était verte quoi qu'il arrive."""
    d = source.index('"""')
    return source[d + 3:source.index('"""', d + 3)]


def _guide(cle):
    """Le corps d'un guide de page, borné par la clé suivante du littéral."""
    d = MOTEUR.index("var PAGE_GUIDES = {")
    bloc = MOTEUR[d:MOTEUR.index("window.PAGE_GUIDES", d)]
    i = bloc.index("\n  %s: {" % cle)
    j = bloc.index("\n    ]\n  },", i)
    return bloc[i:j]


def _dit(texte, nombre):
    """Le nombre est-il annoncé, en chiffres ou en toutes lettres ?"""
    return bool(re.search(r"\b%d\b" % nombre, texte)
                or re.search(LETTRES[nombre], texte))


# ═══════════════════════════════════════════════════════════════════════════
#  LE DÉFAUT TROUVÉ : UN COMPTE DE PROSE QUI NE SE VÉRIFIE PAS TOUT SEUL
# ═══════════════════════════════════════════════════════════════════════════

def test_LE_DEFAUT_TROUVE_la_doctrine_annonce_le_bon_nombre_de_champs():
    """« Six champs comblent cela » a traversé une migration, une revue et deux
    batteries de mutations sans que rien ne le contredise. Le registre en avait
    reçu huit. Aucune batterie ne mute un nombre écrit en toutes lettres dans
    un commentaire : il faut une règle qui LISE la table."""
    n = len(F.CHAMPS_FINOPS)
    entete = _docstring(DOCTRINE)
    # CE QUI SE MESURE EST LA PHRASE QUI ANNONCE, pas la présence du mot. Le
    # docstring explique aussi le défaut corrigé, et cite donc le bon nombre
    # une seconde fois : une règle qui chercherait « huit » n'importe où serait
    # verte alors même que la phrase d'annonce dirait « six ».
    annonce = re.search(r"(\w+)\s+champs\s+comblent", entete)
    assert annonce, (
        "la doctrine de finops_ia n'annonce plus combien de champs comblent "
        "ce qui manquait — la phrase a-t-elle été réécrite ?")
    assert re.fullmatch(LETTRES[n], annonce.group(1)), (
        "la doctrine annonce « %s champs » alors que CHAMPS_FINOPS en déclare "
        "%d" % (annonce.group(1), n))


def test_le_guide_FinOps_annonce_le_bon_nombre_de_champs_a_saisir():
    """C'est le chiffre sur lequel un lecteur règle son travail : il ouvre le
    registre et remplit ce nombre de cases."""
    n = len(F.CHAMPS_FINOPS)
    g = _guide("'finops'")
    assert _dit(g, n), "le guide FinOps n'annonce pas %d champs" % n
    assert not re.search(LETTRES[6] + r"\s+champs", g), (
        "le guide annonce encore « six champs »")


def test_le_guide_FinOps_dit_ce_qu_il_NE_redemande_PAS():
    """C'est la moitié utile du message : « le service, le propriétaire, le
    niveau de risque, l'étape du cycle de vie sont déjà au Registre ». Sans
    elle, le lecteur croit devoir tout ressaisir."""
    g = _guide("'finops'")
    assert "Registre" in g and ("le LIT" in g or "lit au lieu" in g.lower()
                                or "au lieu de vous le redemander" in g)
    for champ in ("risque", "cycle de vie"):
        assert champ in g, champ


def test_le_guide_FinOps_explique_les_angles_morts_et_le_partage_des_lacunes():
    """Les deux apports du lot. Un guide qui ne les nomme pas laisse le lecteur
    devant un premier bloc qu'il ne sait pas lire, et devant un compteur de
    lacunes qu'il prendra pour un reproche."""
    g = _guide("'finops'")
    assert "HAUT RISQUE" in g or "haut risque" in g.lower()
    assert "CONCEPTION" in g or "conception" in g
    assert "PRODUCTION" in g or "production" in g
    assert "pas une lacune" in g or "ce n’est pas une lacune" in g


def test_le_guide_FinOps_maintient_la_reserve_sur_les_leviers():
    """Déclarés, jamais vérifiés. Une case cochée dit qu'un cache existe, pas
    qu'il est branché — et le guide est le seul endroit où le lecteur
    l'apprend avant de citer le tableau en comité."""
    g = _guide("'finops'")
    assert "levier" in g.lower()
    assert "branché" in g or "vérifi" in g


# ═══════════════════════════════════════════════════════════════════════════
#  LE GUIDE DE L'AUDIT DE MATURITÉ SUIT LA COUVERTURE RÉELLE
# ═══════════════════════════════════════════════════════════════════════════

def test_le_guide_maturite_annonce_la_couverture_MESUREE_des_sections():
    """Trois nombres, et ils décident de ce que le lecteur attend : combien de
    sections existent, combien portent un profil relevé, combien n'en portent
    pas. Les recopier sans les tenir, c'est promettre treize profils qui
    n'existent pas."""
    c = N.couverture()
    g = _guide("maturite")
    # LES NOMBRES ONT CHANGÉ AVEC LA DISTINCTION QU'ILS PORTENT, et le motif est
    # écrit ici. « sections sans profil » valait 13 et vaut 0 : la question
    # n'est plus si une section est couverte — elles le sont toutes — mais si
    # son socle est relevé. Un `_dit(g, 0)` ne mesurerait plus rien : le guide
    # doit annoncer les nombres qui DÉCIDENT de ce que le lecteur attend.
    for nombre, quoi in ((c["total"], "sections de la nomenclature"),
                         (len(c["codes_socle_releve"]), "sections à socle relevé"),
                         (len(c["codes_socle_cadre"]), "sections à socle de cadre"),
                         (len(c["profils_releves"]), "profils relevés"),
                         (len(N.PROFILS_SENTINEL), "profils au total")):
        assert _dit(g, nombre), (
            "le guide de l'audit n'annonce pas %d %s" % (nombre, quoi))
    assert c["sans_profil"] == 0, (
        "une section sans profil laisserait l'audit sur le secteur précédent")


def test_le_guide_maturite_dit_la_revision_et_sa_date():
    """Sans la révision et sa date, « NACE » désigne deux nomenclatures dont
    les lettres diffèrent à partir de G — et le lecteur qui connaît l'ancienne
    croira à une erreur de la page."""
    g = _guide("maturite")
    assert N.SOURCE["revision"] in g or "2.1" in g
    assert "2025" in g


def test_le_guide_maturite_dit_que_treize_sections_n_ont_PAS_de_socle():
    """C'est ce que le module refuse de faire, et donc ce que le guide doit
    dire : sans socle de départ, sans budget de référence, sans spécificités.
    Le taire donnerait vingt-deux entrées d'apparence homogène."""
    g = _guide("maturite")
    assert "socle" in g.lower()
    assert "budget" in g.lower()
    assert "questionnaire ne dépendent pas du secteur" in g or \
           "ne dépendent pas du secteur" in g


# ═══════════════════════════════════════════════════════════════════════════
#  LE GUIDE DE LECTURE DES PARCOURS
# ═══════════════════════════════════════════════════════════════════════════

def _intro_parcours():
    """Le texte SERVI AU LECTEUR, commentaires retirés — voir
    `_sans_commentaires` pour ce que cela évite."""
    d = MOTEUR.index("window.guidedPathsOpen = function()")
    return _sans_commentaires(MOTEUR[d:MOTEUR.index("modal.classList.add('on')", d)])


def test_le_guide_des_parcours_explique_les_TROIS_etats():
    """Les trois, pas deux : « pas commencé » est un état, et l'absence de
    marque doit être expliquée comme le reste — sinon elle se lit comme une
    panne d'affichage."""
    intro = _intro_parcours()
    assert "terminé" in intro
    assert "n’a pas été commencé" in intro or "pas été commencé" in intro
    for puce in ("✓", "●"):
        assert puce in intro, puce


def test_le_guide_des_parcours_dit_CE_QUE_LE_VERT_NE_DIT_PAS():
    """La phrase qui empêche le vert de se lire « c'est fait ». Une relecture
    qui trouve le ton lourd la supprimerait ; une règle la garde."""
    intro = _intro_parcours()
    assert "ouverte" in intro and "fait" in intro
    assert "ne peut pas mesurer" in intro


def test_le_guide_des_parcours_dit_ou_l_avancement_est_conserve():
    """Un état qui survit à un rechargement pose la question de où il est
    gardé. Ne pas y répondre laisse supposer un envoi au serveur."""
    intro = _intro_parcours()
    assert "navigateur" in intro
    assert "ne quitte jamais" in intro or "votre poste" in intro


def test_le_guide_des_parcours_dit_qu_une_arrivee_par_le_menu_ne_compte_pas():
    """C'est la règle de comptage, et elle surprend : ouvrir la même page par
    le menu ne fait pas avancer le parcours. Le taire ferait passer le
    compteur pour cassé."""
    intro = _intro_parcours()
    assert "menu" in intro
    assert "ne fait pas avancer" in intro
