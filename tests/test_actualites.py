"""LA PAGE ACTUALITÉS DIT LA MÊME CHOSE AVANT ET APRÈS L'EXÉCUTION DU SCRIPT.

COMMENT CETTE PAGE EST FAITE. Chaque communiqué existe DEUX FOIS : une fois en
français dans le HTML, pour qu'il s'affiche sans attendre le script et pour que
les moteurs de recherche le lisent ; une fois dans un objet JavaScript qui
porte les trois langues et que `naSet()` réinjecte à chaque changement de
langue — y compris quand on revient au français.

CE QUE CETTE DUPLICATION COÛTE. Corriger une coquille d'un seul côté ne casse
rien de visible : la page s'affiche, le texte change simplement sous le clic.
Un lecteur qui clique FR après avoir cliqué EN ne lit plus le même article que
celui qu'il avait sous les yeux en arrivant. Rien ne le signale, et aucun
contrôle d'affichage ne le voit.

CE QUE CES RÈGLES GARDENT.
  — que les deux exemplaires du texte français soient identiques, caractère
    pour caractère ;
  — que tout article présent dans la page soit connu du registre qui pilote le
    changement de langue, et réciproquement — un article oublié dans le
    registre reste figé en français, et le registre qui nomme un article absent
    montrait, avant le regroupement, un premier bloc sans garde ;
  — que chaque thème déclaré ait un bouton de filtre : un thème sans bouton
    n'est pas seulement inaccessible, il FAIT DISPARAÎTRE l'article dès qu'un
    autre filtre est actif ;
  — que la citation de la présidente de la Commission soit reproduite mot pour
    mot, et sans emphase ajoutée.
"""
import io
import json
import os
import re

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = io.open(os.path.join(ICI, 'actualites.html'), encoding='utf-8').read()

# Les corps français écrits dans le HTML, indexés par préfixe d'identifiant.
CORPS_INLINE = dict(re.findall(
    r'<div class="na-body" id="([\w-]+)-body">(.*?)</div>\s*\n', PAGE, re.S))

# Les articles tels que la page les présente, dans l'ordre où ils s'y trouvent.
ARTICLES = re.findall(
    r'<article class="na-article" data-theme="([^"]*)">\s*'
    r'<span class="na-theme">([^<]*)</span>\s*'
    r'<div class="na-eyebrow" id="([\w-]+)-date">', PAGE)

# Le registre qui pilote le changement de langue.
REGISTRE = re.findall(r"\{\s*id:\s*'([\w-]+)'\s*,\s*data:\s*(NA\d*)\s*\}", PAGE)

# LES COMMUNIQUÉS À CONTRÔLER SONT DÉRIVÉS DE LA PAGE, PAS ÉNUMÉRÉS.
# Ils l'étaient : `[('na','NA'), ('na2','NA2'), ('na3','NA3')]`, écrit à la main.
# Le quatrième communiqué est entré sans que la règle qui garde l'identité des
# deux exemplaires français ne le voie — et le cinquième y aurait échappé de
# même. Une liste figée cesse de décrire la page dès qu'on y ajoute quelque
# chose, et c'est précisément quand on ajoute qu'on introduit l'écart.
COMMUNIQUES = REGISTRE


def _communique(nom):
    """L'objet JSON d'un communiqué, lu dans le source de la page."""
    m = re.search(r'^var %s=(\{.*\});\s*$' % re.escape(nom), PAGE, re.M)
    assert m, "le communiqué %s a disparu de la page" % nom
    return json.loads(m.group(1))


def test_la_page_contient_bien_des_communiques():
    """Les règles suivantes portent toutes sur cette liste. Si l'extraction
    cassait — une balise reformatée, un attribut déplacé — elles passeraient
    toutes en ne vérifiant rien."""
    assert len(ARTICLES) >= 3, (
        "moins de trois articles reconnus dans la page (%d) : soit des "
        "communiqués ont été retirés, soit la structure a changé et ces "
        "contrôles ne lisent plus rien" % len(ARTICLES))
    assert len(CORPS_INLINE) == len(ARTICLES), (
        "%d corps d'article pour %d en-têtes : l'extraction est désalignée"
        % (len(CORPS_INLINE), len(ARTICLES)))


# ── LES DEUX EXEMPLAIRES DU TEXTE FRANÇAIS ───────────────────────────────

@pytest.mark.parametrize('prefixe,nom', COMMUNIQUES)
def test_le_francais_du_html_est_celui_du_script(prefixe, nom):
    """LA RÈGLE PRINCIPALE. Le lecteur qui clique EN puis FR doit retrouver
    exactement l'article qu'il avait en arrivant."""
    inline = CORPS_INLINE.get(prefixe)
    assert inline is not None, "aucun corps inline pour l'article %s" % prefixe
    attendu = _communique(nom)['fr']['body']
    assert inline.strip() == attendu.strip(), (
        "le texte français de l'article %s diffère entre le HTML et l'objet "
        "%s : cliquer FR changerait l'article sous les yeux du lecteur" % (prefixe, nom))


@pytest.mark.parametrize('nom', [n for _, n in COMMUNIQUES])
def test_chaque_communique_est_complet_dans_les_trois_langues(nom):
    """Une langue manquante ne lève pas d'erreur : `naSet` retombe sur le
    français. L'utilisateur clique DE, la page reste en français, et rien ne
    dit que la traduction n'existe pas."""
    d = _communique(nom)
    for langue in ('fr', 'en', 'de'):
        assert langue in d, "%s n'a pas de version « %s »" % (nom, langue)
        for champ in ('title', 'date', 'body'):
            valeur = (d[langue].get(champ) or '').strip()
            assert valeur, "%s[%s][%s] est vide" % (nom, langue, champ)


@pytest.mark.parametrize('prefixe,nom', COMMUNIQUES)
def test_le_titre_du_html_est_celui_du_script(prefixe, nom):
    # LE COUPLE VIENT DU REGISTRE, pas d'une table écrite à côté : c'est le
    # registre qui fait autorité sur ce qui s'appelle comment, et une table
    # parallèle aurait dû être tenue à jour à chaque communiqué.
    m = re.search(r'<h2 class="na-title" id="%s-title">(.*?)</h2>' % prefixe, PAGE, re.S)
    assert m, "titre inline introuvable pour %s" % nom
    assert m.group(1).strip() == _communique(nom)['fr']['title'].strip(), (
        "le titre français de %s diffère entre le HTML et le script" % nom)


# ── LE REGISTRE ET LA PAGE SE CORRESPONDENT ──────────────────────────────

def test_tout_article_de_la_page_est_dans_le_registre():
    """Un article absent du registre reste figé en français : les boutons de
    langue n'ont simplement aucun effet sur lui, sans erreur ni message."""
    dans_la_page = [a[2] for a in ARTICLES]
    dans_le_registre = [r[0] for r in REGISTRE]
    oublies = [p for p in dans_la_page if p not in dans_le_registre]
    assert not oublies, (
        "article(s) présent(s) dans la page mais absent(s) de NA_COMMUNIQUES : "
        "%s — les boutons de langue resteront sans effet sur eux"
        % ', '.join(oublies))


def test_tout_communique_du_registre_est_dans_la_page():
    dans_la_page = [a[2] for a in ARTICLES]
    fantomes = [p for p, _ in REGISTRE if p not in dans_la_page]
    assert not fantomes, (
        "communiqué(s) nommé(s) dans NA_COMMUNIQUES sans article correspondant "
        "dans la page : %s" % ', '.join(fantomes))


def test_le_registre_suit_l_ordre_de_la_page():
    """Le commentaire du registre affirme que son ordre est celui de la page,
    le plus récent d'abord. Une affirmation que rien ne vérifie cesse d'être
    vraie à la première insertion faite ailleurs."""
    assert [r[0] for r in REGISTRE] == [a[2] for a in ARTICLES], (
        "l'ordre de NA_COMMUNIQUES (%s) n'est plus celui de la page (%s)"
        % (', '.join(r[0] for r in REGISTRE), ', '.join(a[2] for a in ARTICLES)))


def test_le_changement_de_langue_ne_traite_plus_les_articles_un_par_un():
    """LA RÈGLE QUI GARDE LE REGROUPEMENT. `naSet` nommait chaque article :
    ajouter un communiqué demandait d'y penser, et le premier bloc, sans garde
    d'existence, faisait échouer la fonction entière — donc TOUS les autres
    articles — si son élément disparaissait de la page."""
    d = PAGE.index('function naSet(l){')
    corps = PAGE[d:PAGE.index('\n}', d)]
    assert 'NA_COMMUNIQUES' in corps, (
        "naSet ne parcourt plus le registre : les articles sont de nouveau "
        "traités un par un, et le prochain sera oublié")
    for code_en_dur in ("'na-title'", "'na2-title'", "'na3-title'"):
        assert code_en_dur not in corps, (
            "naSet nomme de nouveau %s en dur" % code_en_dur)


# ── LES THÈMES ET LEURS BOUTONS ──────────────────────────────────────────

BOUTONS = set(re.findall(r'<button class="na-f[^"]*" data-t="([^"]*)"', PAGE))


@pytest.mark.parametrize('themes,libelle,prefixe', ARTICLES)
def test_chaque_theme_declare_a_son_bouton(themes, libelle, prefixe):
    """UN THÈME SANS BOUTON EST PIRE QU'INUTILE. `naFilter` masque tout article
    dont les thèmes ne contiennent pas celui qu'on demande : un thème orphelin
    n'ajoute pas un filtre manquant, il retire l'article de tous les autres."""
    for t in [x.strip() for x in themes.split(',') if x.strip()]:
        assert t in BOUTONS, (
            "l'article %s déclare le thème « %s », qu'aucun bouton de filtre "
            "ne propose : il ne sera atteignable par aucun filtre" % (prefixe, t))


@pytest.mark.parametrize('themes,libelle,prefixe', ARTICLES)
def test_le_libelle_visible_dit_les_vrais_themes(themes, libelle, prefixe):
    """L'étiquette affichée sous la date et l'attribut qui pilote le filtre
    sont deux écritures de la même chose. Quand elles divergent, l'article
    annonce un thème et se range sous un autre."""
    declares = [x.strip() for x in themes.split(',') if x.strip()]
    affiches = [x.strip() for x in libelle.split('·') if x.strip()]
    assert declares == affiches, (
        "l'article %s affiche « %s » mais se filtre sur « %s »"
        % (prefixe, ' · '.join(affiches), ', '.join(declares)))


# ── LES CITATIONS ────────────────────────────────────────────────────────

# Reproduite depuis la déclaration de la présidente de la Commission
# accompagnant la proposition de Cloud and AI Development Act du 3 juin 2026.
CITATION_VDL = (
    "Nous ne pouvons pas nous permettre de dépendre d'autres acteurs pour les "
    "technologies qui assurent le fonctionnement de nos hôpitaux, la stabilité "
    "de nos réseaux énergétiques et la sécurité de nos services. Il s'agit de "
    "protéger nos citoyens, de défendre nos intérêts et de préserver notre "
    "capacité à faire nos propres choix. L'Europe dispose des talents, de "
    "l'excellence en matière de recherche, de la base industrielle et du marché "
    "unique nécessaires. Ensemble, nous devons transformer ces atouts en "
    "souveraineté technologique."
)


def test_la_citation_est_reproduite_mot_pour_mot():
    """Une citation attribuée nommément n'est pas du texte de communiqué : elle
    ne se reformule pas au fil des relectures. Cette règle fige la version
    française telle qu'elle a été publiée.

    LES DEUX EXEMPLAIRES, PAS UN SEUL. Une première version ne lisait que
    l'objet JavaScript. La mutation qui reformulait la citation dans le HTML a
    survécu : la règle regardait ailleurs. Ce sont deux copies du même texte,
    et une citation doit être exacte dans les deux."""
    for source, corps in (('le script', _communique('NA3')['fr']['body']),
                          ('le HTML', CORPS_INLINE.get('na3', ''))):
        assert CITATION_VDL in corps, (
            "la citation attribuée à la présidente de la Commission a été "
            "modifiée dans %s : une citation se corrige à la source ou se "
            "retire, elle ne se réécrit pas" % source)


def test_la_citation_est_bien_dans_un_bloc_de_citation():
    """Hors <blockquote>, elle perd sa marque de citation — et le surligneur
    reprend ses droits dessus."""
    corps = _communique('NA3')['fr']['body']
    blocs = re.findall(r'<blockquote>(.*?)</blockquote>', corps, re.S)
    assert any(CITATION_VDL in b for b in blocs), (
        "la citation de la présidente de la Commission n'est plus dans un "
        "<blockquote> : rien ne la distingue du texte du communiqué")


def test_le_surligneur_epargne_les_citations():
    """AJOUTER UNE EMPHASE DANS UNE CITATION, C'EST LA MODIFIER. Le surligneur
    met en exergue « souveraineté technologique », qui figure dans la
    déclaration citée : sans cette garde, il accentuerait des mots que
    l'auteure citée n'a pas accentués, sans le signaler."""
    d = PAGE.index('window.naHighlight = function()')
    corps = PAGE[d:PAGE.index('\n};', d)]
    assert 'blockquote' in corps, (
        "le surligneur ne met plus les citations à part : il ajoutera une "
        "emphase à l'intérieur des guillemets sans l'indiquer")


# ── CE QUE LA PAGE DOIT CONTINUER DE DIRE ────────────────────────────────

def test_la_responsabilite_editoriale_reste_publiee():
    """`_ia50_mesure_actualites()` mesure la conformité de cette page à
    l'exception de l'article 50.4 sur cette seule mention. La retirer ferait
    basculer la ligne du registre en « non-conforme » sans que personne ne
    touche au registre."""
    assert 'responsabilité éditoriale' in PAGE, (
        "la mention de responsabilité éditoriale a disparu de la page "
        "Actualités : l'exception de l'article 50.4 y est invoquée sans être "
        "documentée, et la mesure IA-50 passera en non-conforme")


# Les deux choses que le communiqué doit dire sur le statut du texte, dans
# chaque langue : qu'il est encore entre les mains des colégislateurs, et que
# rien n'en est exigible. Les DEUX sont exigées — une seule se retrouverait par
# hasard dans n'importe quel article traitant de législation européenne.
RESERVE_DE_STATUT = {
    'fr': ("Parlement européen et le Conseil", "Rien n'en est aujourd'hui exigible"),
    'en': ("European Parliament and the Council", "Nothing in it is enforceable today"),
    'de': ("Europäischen Parlament und vom Rat", "Nichts daraus ist heute einforderbar"),
}


@pytest.mark.parametrize('langue', ['fr', 'en', 'de'])
def test_le_communique_reserve_le_statut_du_texte_hors_mention_legale(langue):
    """Un cabinet de conformité qui présenterait une proposition de la
    Commission comme du droit applicable ferait exactement l'erreur qu'il vend
    d'éviter. La réserve doit tenir dans le corps de l'article, pas seulement
    dans la mention légale en petits caractères que personne ne lit.

    CE QUE CETTE RÈGLE NE MESURE PAS, ET IL FAUT LE DIRE. Une première version
    cherchait le mot « proposition » avant le <small>. Elle passait encore
    après qu'on eut remplacé « texte proposé par la Commission » par « texte
    adopté par la Commission » — le mot restait ailleurs dans l'article, et la
    règle était satisfaite par un texte devenu faux. Un mot n'est pas une
    propriété.

    Ce qui est mesurable, c'est que la réserve EXISTE et qu'elle est complète :
    les colégislateurs sont encore saisis, et rien n'est exigible. Que le reste
    de l'article ne la contredise pas relève de la relecture humaine, qu'aucune
    machine ne remplace — c'est la même limite que celle reconnue par
    `_ia50_mesure_actualites()` pour l'examen humain de l'article 50.4."""
    corps = _communique('NA3')[langue]['body']
    avant_mention = corps.split('<small>')[0]
    for exigee in RESERVE_DE_STATUT[langue]:
        assert exigee in avant_mention, (
            "la version « %s » du communiqué du 28 août ne dit plus « %s » "
            "dans le corps de l'article : le Cloud and AI Development Act y "
            "serait présenté comme du droit applicable, alors qu'il n'est "
            "qu'une proposition de la Commission" % (langue, exigee))


# ═══════════════════════════════════════════════════════════════════════════
#  LA TYPOGRAPHIE : UN PLANCHER DE LECTURE, ET UNE HIÉRARCHIE
# ═══════════════════════════════════════════════════════════════════════════
#
# POURQUOI CES RÈGLES EXISTENT. La demande était « réduire la taille de police
# pour gagner de la place », et elle était fondée : la police est le premier
# levier, elle paie deux fois — les lignes rétrécissent ET il en tient plus par
# ligne. Mesuré sur les cinq communiqués, elle vaut 9,2 % de la hauteur à elle
# seule, contre 5,1 % pour l'interligne et moins de 2 % pour chaque marge.
#
# MAIS CE LEVIER N'A PAS DE FOND. Rien, dans la page, n'empêchait de le tirer
# une fois de plus — et la fois suivante, et celle d'après. La suite complète
# est passée sans broncher sur ce changement : AUCUNE règle ne tenait la
# typographie des articles. Un « gagner encore un peu de place » aurait amené
# le corps à 12 px sans que rien ne le signale.
#
# CE QU'ELLES NE FONT PAS : figer les valeurs d'aujourd'hui. Une règle qui
# verrouille « 14 px » interdit de passer à 15 px le jour où l'on décide que
# c'était trop serré. Elles bornent un PLANCHER et une RELATION, ce qui laisse
# le réglage libre entre les deux.

_STYLES = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", PAGE, re.S))

# LES REQUÊTES MÉDIA NE SONT PAS DE LA CASCADE, et les confondre a produit un
# faux mesuré : `.na-title` est déclaré à 26 px dans la feuille, puis à 22 px
# sous `@media(max-width:640px)`. Lire « la dernière déclaration » ramenait
# donc la valeur MOBILE pour juger du rendu de bureau — et une mutation qui
# ramenait le titre de bureau au niveau de l'intertitre survivait, la règle
# lisant tranquillement les 22 px du téléphone. Une déclaration conditionnelle
# se juge dans sa condition, pas dans le flux.
_MEDIA = re.findall(r"(@media[^{]*)\{((?:[^{}]|\{[^{}]*\})*)\}", _STYLES)
_BASE = re.sub(r"@media[^{]*\{(?:[^{}]|\{[^{}]*\})*\}", "", _STYLES)


def _px(selecteur, propriete="font-size", feuille=None):
    """La valeur déclarée pour ce sélecteur, lue dans la feuille de la page.

    Lire la feuille plutôt que recopier le nombre est ce qui distingue une
    règle d'une note : recopié, le nombre cesse de décrire la page au premier
    changement, et la règle continue de passer en vérifiant sa propre copie.
    """
    blocs = re.findall(re.escape(selecteur) + r"\{([^}]*)\}", feuille or _BASE)
    assert blocs, "sélecteur %r absent de la feuille de la page" % selecteur
    # LA CASCADE, PAS LA PREMIÈRE OCCURRENCE. Un sélecteur paraît plusieurs
    # fois dans cette page — `.na-body h4` deux fois, dont une qui ne pose
    # qu'une couleur. Lire la première déclaration trouvée revenait à lire
    # un bloc qui ne dit rien de la taille, et la règle tombait en accusant
    # la feuille d'un manque qui n'existait pas. À spécificité égale, c'est
    # la DERNIÈRE déclaration qui s'applique : c'est elle qu'il faut lire.
    valeurs = [re.search(propriete + r":\s*([\d.]+)", b) for b in blocs]
    valeurs = [v for v in valeurs if v]
    assert valeurs, "aucun des %d blocs %s ne déclare %s" % (
        len(blocs), selecteur, propriete)
    return float(valeurs[-1].group(1))


def test_le_texte_suivi_d_un_article_ne_descend_pas_sous_le_plancher():
    """UN ARTICLE SE LIT EN SUIVI, PAS EN COUP D'ŒIL, et c'est ce qui sépare
    son corps d'une pastille ou d'un libellé. Sur le fond sombre de ces
    cartes, sous 14 px la lecture d'un communiqué de cinq mille signes cesse
    d'être confortable — c'est le plancher, et il vaut pour le corps, pour la
    citation en exergue, et pour la liste de sources qui se lit elle aussi
    ligne à ligne.

    Les libellés — la pastille de thème, la mention « sans lien » — sont hors
    de cette règle À DESSEIN : ils se glancent, ils sont capitalisés et
    interlettrés, et les tenir au même plancher les ferait grossir sans que
    personne y gagne.
    """
    planchers = [
        (".na-body p", 14.0, "le corps de l'article"),
        (".na-body blockquote", 14.0, "la citation en exergue"),
        (".na-sources li", 12.5, "la liste des sources"),
    ]
    trop_petits = ["%s : %s à %.3g px, plancher %.3g px"
                   % (sel, quoi, _px(sel), mini)
                   for sel, mini, quoi in planchers if _px(sel) < mini]
    assert not trop_petits, (
        "du texte qui se lit en suivi passe sous son plancher de "
        "lisibilité :\n  " + "\n  ".join(trop_petits))


def test_la_hierarchie_typographique_tient_dans_les_deux_sens():
    """RÉDUIRE UN SEUL ÉTAGE CASSE LA HIÉRARCHIE, et c'est le risque propre à
    une demande de densité : on descend le corps, on oublie l'intertitre, et
    le titre de section cesse de se distinguer du paragraphe. La règle borne
    la RELATION et non les valeurs — chaque étage garde une avance mesurable
    sur le suivant, quel que soit le réglage retenu.
    """
    etages = [("le titre de l'article", _px(".na-title")),
              ("l'intertitre", _px(".na-body h4")),
              ("le corps", _px(".na-body p")),
              ("les sources", _px(".na-sources li"))]
    for (h, a), (b_, b) in zip(etages, etages[1:]):
        assert a >= b * 1.06, (
            "%s (%.3g px) ne se distingue plus de %s (%.3g px) : moins de 6 %% "
            "d'écart, la hiérarchie ne se voit plus" % (h, a, b_, b))


def test_l_interligne_du_corps_reste_au_dessus_de_ce_qu_un_lecteur_impose():
    """L'INTERLIGNE EST LE SECOND LEVIER, ET LE PLUS TENTANT : il ne se voit
    pas dans une capture, il rapporte 5 % de hauteur, et il coûte au lecteur
    exactement là où on ne le mesure pas.

    Le critère 1.4.12 du RGAA/WCAG demande qu'une page reste utilisable quand
    son lecteur impose un interligne de 1,5. Il porte sur ce que la page doit
    SUPPORTER, non sur ce qu'elle doit servir — servir au moins cette valeur
    n'y satisfait donc pas à soi seul, mais descendre en dessous revient à
    livrer d'emblée moins que ce qu'un lecteur est fondé à réclamer.
    """
    lh = _px(".na-body p", "line-height")
    assert lh >= 1.5, (
        "l'interligne du corps est tombé à %.3g : sous 1,5, un article long "
        "sur fond sombre devient pénible, et la page sert d'emblée moins que "
        "ce qu'un lecteur peut imposer" % lh)


def test_les_variantes_mobiles_respectent_les_memes_planchers():
    """CORRIGER LA LECTURE NE DOIT PAS SUPPRIMER LE CONTRÔLE. En écartant les
    requêtes média du flux — ce qu'il fallait faire, une déclaration
    conditionnelle ne se juge pas hors de sa condition — je les ai du même
    coup sorties de la portée des trois règles précédentes. Un plancher qui
    ne vaut que sur grand écran ne protège personne : c'est sur téléphone que
    la place manque, donc c'est là qu'on est tenté de tirer sur le levier.

    Chaque variante est donc jugée DANS sa condition, en repartant des
    valeurs de base pour tout ce qu'elle ne redéfinit pas.
    """
    planchers = {".na-body p": 14.0, ".na-body blockquote": 14.0,
                 ".na-sources li": 12.5}
    fautes = []
    for condition, corps in _MEDIA:
        for sel, mini in planchers.items():
            if not re.search(re.escape(sel) + r"\{", corps):
                continue                      # non redéfini : la base vaut
            v = _px(sel, feuille=corps)
            if v < mini:
                fautes.append("%s : %s à %.3g px, plancher %.3g px"
                              % (condition.strip(), sel, v, mini))
        # La hiérarchie titre > intertitre > corps doit tenir aussi ici, en
        # complétant par les valeurs de base ce que la variante ne dit pas.
        etages = []
        for sel in (".na-title", ".na-body h4", ".na-body p"):
            v = (_px(sel, feuille=corps)
                 if re.search(re.escape(sel) + r"\{[^}]*font-size", corps)
                 else _px(sel))
            etages.append((sel, v))
        for (h, x), (b_, y) in zip(etages, etages[1:]):
            if x < y * 1.06:
                fautes.append("%s : %s (%.3g px) ne se distingue plus de %s "
                              "(%.3g px)" % (condition.strip(), h, x, b_, y))
    assert not fautes, (
        "une variante d'écran sert un texte que la version de bureau "
        "n'aurait pas le droit de servir :\n  " + "\n  ".join(fautes))
