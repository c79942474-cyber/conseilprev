# -*- coding: utf-8 -*-
"""Sentinel se lit en français ou en anglais, et la bascule est en haut du menu.

CE QUI N'EXISTAIT PAS. La page d'accueil se traduit depuis longtemps — trois
langues, 240 porteurs de `data-i18n`. Sentinel, lui, n'en avait AUCUN :
27 000 mots, tous en français, sans le moindre point d'entrée.

CE QUI EST TRADUIT, ET CE QUI NE L'EST PAS. La COQUILLE NAVIGABLE : les
douze rubriques du menu, ses cinquante-huit entrées, le sous-titre et le fil
d'Ariane des 107 pages. Un lecteur anglophone traverse Sentinel et sait où
il est. Le CORPS des panneaux — environ 24 000 mots de doctrine
réglementaire — reste en français. Ces règles gardent la coquille ; elles ne
prétendent pas que le tout est traduit.

LE PIÈGE QU'ON NE REPRODUIT PAS, ET QUI A COÛTÉ DEUX FOIS ICI. `applyLang`,
sur l'accueil, fait `el.innerHTML = <traduction>` : un lien écrit DANS un
élément traduit disparaît au chargement, sans erreur et sans trace. La
mention « texte seul » de la carte DORA, puis les dix-neuf liens des offres
de services, sont morts comme ça. Le moteur de Sentinel écrit `textContent`
et rien d'autre — et la §3 interdit de marquer un élément qui contient du
balisage, plutôt que de le laisser s'effacer en silence.
"""
import io
import os
import re

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _lire(nom):
    with io.open(os.path.join(_RACINE, nom), encoding="utf-8") as f:
        return f.read()


SENTINEL = _lire("sentinel.html")
PAGEJS = _lire("sentinel.page.js")


def _dico(lg):
    """Le dictionnaire d'une langue, lu dans le moteur."""
    i = PAGEJS.index("var SENT_T = {")
    bloc = PAGEJS[i:PAGEJS.index("\n};", i)]
    j = bloc.index("  %s: {" % lg)
    return dict(re.findall(r"'([^']+)':\s*'((?:[^'\\]|\\.)*)'",
                           bloc[j:bloc.index("\n  }", j)]))


def _marques():
    """{clé: texte français} pour chaque porteur de `data-i18n`."""
    return dict(re.findall(r'data-i18n="([^"]+)">([^<]*)<', SENTINEL))


def _blocs():
    """{clé: HTML français} pour chaque porteur de `data-i18n-bloc`.

    UN TITRE OU UN CHAPEAU PORTE DU GRAS ET DE L'ITALIQUE. Les découper en
    fragments traduits un à un donnerait des clés illisibles et une phrase
    recousue mot à mot. Ces éléments reçoivent donc leur HTML entier — sous
    la garde stricte de la §3."""
    return {cle: corps for _b, cle, corps in re.findall(
        r'<([a-z0-9]+)[^>]*data-i18n-bloc="([^"]+)"[^>]*>(.*?)</\1>',
        SENTINEL, re.S)}


#  CE QU'UN BLOC TRADUIT A LE DROIT DE CONTENIR. Du gras, de l'italique, du
#  code, un retour à la ligne : de la mise en forme, et rien qui porte un
#  comportement. Tout le reste — un lien, un identifiant, un gestionnaire —
#  serait DÉTRUIT par la réécriture, et c'est le défaut que ce dépôt a payé
#  deux fois.
BALISES_PERMISES = {"b", "strong", "em", "i", "code", "br", "sup", "sub"}


# ══════════════════════════════════════════════════════════════════════════
#  1. LA BASCULE EST LÀ, ET EN HAUT DU MENU
# ══════════════════════════════════════════════════════════════════════════

def test_la_bascule_est_en_HAUT_du_menu_et_pas_dans_un_reglage():
    """UN VISITEUR ANGLOPHONE QUI DOIT D'ABORD TROUVER UN MENU DE
    PRÉFÉRENCES pour comprendre le menu ne le trouvera pas. Le choix se
    présente là où le regard arrive, avant toute lecture."""
    i = SENTINEL.index('<aside class="sb"')
    tete = SENTINEL[i:i + 2500]
    assert '<div class="sb-lang"' in tete, (
        "la bascule n'est plus en tête de la barre latérale")
    #  ELLE PRÉCÈDE LE PREMIER TIROIR : « en haut du menu » est une position,
    #  pas une intention.
    assert SENTINEL.index('<div class="sb-lang"') < \
        SENTINEL.index('<div class="sb-section"'), (
        "la bascule est passée SOUS les rubriques du menu")
    for lg in ("fr", "en"):
        assert 'data-lang="%s"' % lg in tete and \
            "sentSetLang('%s')" % lg in tete, lg


def test_la_langue_active_se_lit_sans_la_couleur():
    """UN ÉTAT PORTÉ PAR LA SEULE COULEUR n'existe pas pour qui ne la
    distingue pas, ni pour un lecteur d'écran."""
    i = SENTINEL.index('<div class="sb-lang"')
    bloc = SENTINEL[i:SENTINEL.index("</div>", SENTINEL.index("EN</button>", i))]
    assert bloc.count('aria-pressed=') == 2, bloc.count('aria-pressed=')
    assert 'role="group"' in bloc and 'aria-label=' in bloc


# ══════════════════════════════════════════════════════════════════════════
#  2. AUCUNE CLÉ MARQUÉE N'EST LAISSÉE SANS TRADUCTION
# ══════════════════════════════════════════════════════════════════════════

def test_la_lecture_du_balisage_et_du_dictionnaire_n_est_pas_vide():
    """LE GARDE-FOU DE TOUTE LA §2. Une lecture qui rendrait zéro clé d'un
    côté ferait passer la comparaison pour une comparaison de vides."""
    m, b, en = _marques(), _blocs(), _dico("en")
    assert len(m) >= 70, "%d porteurs de data-i18n relevés" % len(m)
    assert len(b) >= 60, "%d porteurs de data-i18n-bloc relevés" % len(b)
    assert len(en) >= 170, "%d entrées dans le dictionnaire anglais" % len(en)


def test_CHAQUE_cle_marquee_a_sa_traduction_anglaise():
    """UN MENU À TROUS EST PIRE QU'UN MENU BILINGUE : le lecteur croit que
    l'entrée non traduite désigne autre chose que ce qu'elle désigne.

    Le moteur garde le français à défaut — il ne vide jamais l'élément —
    mais cette règle empêche que le défaut devienne la règle."""
    m, en = dict(_marques(), **_blocs()), _dico("en")
    manquantes = sorted(k for k in m if k not in en)
    assert not manquantes, (
        "%d clé(s) marquées sans traduction anglaise : %s"
        % (len(manquantes), manquantes[:8]))


def test_le_dictionnaire_ne_porte_pas_de_cle_MORTE():
    """UNE TRADUCTION QUI NE VISE PLUS RIEN se maintient indéfiniment : elle
    ne s'affiche jamais, donc personne ne voit qu'elle est fausse."""
    m, en = dict(_marques(), **_blocs()), _dico("en")
    mortes = sorted(k for k in en if k not in m)
    assert not mortes, (
        "%d traduction(s) ne visent plus aucun élément : %s"
        % (len(mortes), mortes[:8]))


# ══════════════════════════════════════════════════════════════════════════
#  3. LE PIÈGE DE L'ACCUEIL N'EST PAS REPRODUIT
# ══════════════════════════════════════════════════════════════════════════

def test_la_traduction_ecrit_textContent_et_JAMAIS_innerHTML():
    """LA DIFFÉRENCE QUI SÉPARE CE MOTEUR DE CELUI DE L'ACCUEIL. `applyLang`
    fait `el.innerHTML = <traduction>` : un lien écrit dans un élément
    traduit disparaît au chargement. Ce dépôt l'a payé deux fois."""
    i = PAGEJS.index("function sentAppliquer()")
    corps = PAGEJS[i:PAGEJS.index("\n}", i)]
    #  DEUX BOUCLES, DEUX RÉGIMES. Celle des `data-i18n` écrit le TEXTE et
    #  rien d'autre : c'est elle qui couvre le menu, où vivent les icônes.
    #  Celle des `data-i18n-bloc` réécrit le HTML, et n'a le droit de le
    #  faire que parce que la règle suivante lui interdit tout ce qui porte
    #  un comportement. Une règle qui bannirait `innerHTML` partout aurait
    #  interdit le second chemin sans rien protéger de plus.
    j = corps.index("[data-i18n-bloc]")
    simple, bloc = corps[:j], corps[j:]
    assert "textContent" in simple, "la traduction n'écrit plus le texte"
    assert "innerHTML" not in simple, (
        "la boucle des éléments simples écrit innerHTML : tout lien, bouton "
        "ou identifiant placé dans un élément traduit sera effacé au "
        "chargement, sans erreur et sans trace")
    assert "innerHTML" in bloc, "le chemin des blocs n'écrit plus le HTML"
    #  DEUX GESTES, ET CHERCHER LE NOM DE L'ATTRIBUT NE PROUVE NI L'UN NI
    #  L'AUTRE. Une première version se contentait de `"data-i18n-bloc-fr"
    #  in bloc` : retirer la CAPTURE la laissait verte, parce que le nom
    #  survivait dans la RESTITUTION deux lignes plus bas. Le retour au
    #  français aurait vidé chaque titre, et rien ne serait tombé.
    assert "setAttribute('data-i18n-bloc-fr'" in bloc, (
        "le HTML français d'origine n'est plus CAPTURÉ : le retour en "
        "français videra les titres et les chapeaux")
    assert "getAttribute('data-i18n-bloc-fr')" in bloc, (
        "le HTML français d'origine n'est plus RESTITUÉ")


def test_AUCUN_element_traduit_ne_contient_de_balisage():
    """L'AUTRE MOITIÉ DE LA GARDE. Écrire `textContent` protège des
    disparitions silencieuses, mais efface quand même ce qu'un élément
    contenait. La règle interdit donc de marquer un porteur qui contient
    autre chose que du texte — un lien, un bouton, une icône, un élément
    identifié que du JavaScript irait chercher."""
    for m in re.finditer(r'<([a-z]+)[^>]*data-i18n="([^"]+)"[^>]*>(.*?)</\1>',
                         SENTINEL, re.S):
        balise, cle, dedans = m.group(1), m.group(2), m.group(3)
        assert "<" not in dedans, (
            "l'élément traduit « %s » contient du balisage, que la "
            "traduction effacera : %r" % (cle, dedans[:70]))


def test_une_cle_sans_traduction_GARDE_son_francais():
    """VIDER L'ÉLÉMENT LE FERAIT DISPARAÎTRE DE L'ÉCRAN. Le moteur conserve
    le texte français d'origine dans un attribut, et y retombe — à
    l'affichage comme au retour en français."""
    i = PAGEJS.index("function sentAppliquer()")
    corps = PAGEJS[i:PAGEJS.index("\n}", i)]
    assert "data-i18n-fr" in corps, (
        "le texte français d'origine n'est plus conservé : le retour en "
        "français ne pourra pas le restituer")
    assert "=== null || v === undefined" in corps or "v === null" in corps, (
        "une clé sans traduction n'a plus de repli : l'élément se videra")


# ══════════════════════════════════════════════════════════════════════════
#  4. CE QUI NE SE TRADUIT PAS, ET NE DOIT PAS
# ══════════════════════════════════════════════════════════════════════════

#  LES NOMS PROPRES DE TEXTES ET DE RÉFÉRENTIELS. Traduits, ils deviennent
#  introuvables dans le document officiel — ce qu'un auditeur vient
#  précisément chercher. La règle les fige des deux côtés.
NOMS_PROPRES = ("EU AI ACT", "NIS 2", "ISO 42001", "ISO 27001",
                "NIST AI RMF", "OWASP LLM")


def test_les_noms_de_reglements_ne_sont_PAS_traduits():
    """« EU AI ACT » RENDU PAR « LOI IA UE » ferait chercher à l'auditeur un
    texte qui n'existe pas sous ce nom. Ces rubriques traversent la bascule
    inchangées, et c'est un choix — écrit ici pour qu'il ne se défasse pas
    par mégarde."""
    i = PAGEJS.index("var SENT_SECTIONS_EN = {")
    table = PAGEJS[i:PAGEJS.index("\n};", i)]
    for nom in NOMS_PROPRES:
        assert "'%s':" % nom not in table, (
            "« %s » a reçu une traduction : c'est un nom propre de texte "
            "réglementaire, il doit traverser la bascule inchangé" % nom)


def test_les_rubriques_du_fil_d_Ariane_sont_COUVERTES_ou_nommees():
    """UNE RUBRIQUE OUBLIÉE RESTE EN FRANÇAIS AU MILIEU D'UN FIL ANGLAIS,
    et rien ne le signale. La règle exige que chacune des rubriques de
    PAGE_META soit soit traduite, soit déclarée nom propre."""
    i = PAGEJS.index("var PAGE_META = {")
    bloc = PAGEJS[i:PAGEJS.index("\n};", i)]
    rubriques = set(re.findall(r"section:\s*'([^']*)'", bloc))
    assert len(rubriques) >= 20, "%d rubriques relevées" % len(rubriques)
    j = PAGEJS.index("var SENT_SECTIONS_EN = {")
    table = dict(re.findall(r"'([^']+)':\s*'([^']*)'",
                            PAGEJS[j:PAGEJS.index("\n};", j)]))
    orphelines = sorted(r for r in rubriques
                        if r not in table and r not in NOMS_PROPRES)
    assert not orphelines, (
        "%d rubrique(s) du fil d'Ariane ne sont ni traduites ni déclarées "
        "noms propres : %s" % (len(orphelines), orphelines))


# ══════════════════════════════════════════════════════════════════════════
#  5. LE CHOIX SURVIT, ET LE FIL D'ARIANE SUIT
# ══════════════════════════════════════════════════════════════════════════

def test_le_choix_de_langue_survit_a_la_fermeture_de_l_onglet():
    """REDEMANDER SA LANGUE À CHAQUE VISITE revient à ne pas l'avoir
    demandée."""
    assert "'cp-sentinel-langue-v1'" in PAGEJS
    assert "localStorage.setItem(SENT_LANG_CLE" in PAGEJS
    assert "localStorage.getItem(SENT_LANG_CLE" in PAGEJS


def test_le_fil_d_Ariane_passe_par_PAGE_META_et_plus_par_les_onclick():
    """CE QUI RENDAIT LE FIL INTRADUISIBLE. `go()` recevait sa section et son
    libellé EN DUR depuis le `onclick` de chaque entrée : quarante-huit
    chaînes françaises qu'aucune bascule ne pouvait atteindre. PAGE_META les
    porte pour les 107 pages, dans une seule table."""
    i = PAGEJS.index("function go(id, el, sec, pg) {")
    corps = PAGEJS[i:PAGEJS.index("\nfunction ", i + 10)]
    assert "sentFilAriane(id)" in corps, (
        "le fil d'Ariane ne passe plus par la table traduite : il repart des "
        "chaînes françaises figées dans les onclick")
    #  ET L'ANCIEN CHEMIN RESTE, POUR LES PAGES SANS FICHE.
    assert "PAGE_META[id]" in corps


def test_un_bloc_traduit_ne_porte_QUE_de_la_mise_en_forme():
    """LA GARDE QUI REND LE CHEMIN « BLOC » ACCEPTABLE.

    Ce chemin réécrit l'innerHTML — le geste exact qui a effacé deux fois
    des liens dans ce dépôt. Il n'est donc pas interdit, il est ENCADRÉ :
    un élément traduit par bloc ne peut contenir que de la mise en forme,
    rien qui porte un comportement. Du gras et de l'italique, l'effacer et
    le réécrire ne perd rien ; un lien, un identifiant ou un gestionnaire,
    si — et personne ne le verrait.

    LA RÈGLE PORTE SUR LES DEUX CÔTÉS : le français dans la page ET
    l'anglais dans le dictionnaire, parce qu'une traduction peut très bien
    introduire un lien que l'original n'avait pas."""
    en = _dico("en")
    for source, quoi in ((_blocs(), "la page"), 
                         ({k: v for k, v in en.items() if k.startswith("pg.")},
                          "le dictionnaire anglais")):
        assert source, quoi
        for cle, corps in source.items():
            for interdit in ("<a ", "<a>", "id=", "onclick=", "href=",
                             "<script", "<button", "<input", "<img"):
                assert interdit not in corps, (
                    "le bloc « %s » de %s contient %r : la traduction "
                    "l'effacerait sans que rien ne le signale"
                    % (cle, quoi, interdit))
            balises = set(re.findall(r"</?([a-z0-9]+)", corps))
            hors = sorted(balises - BALISES_PERMISES)
            assert not hors, (
                "le bloc « %s » de %s emploie %s, hors de la liste des "
                "balises de pure mise en forme" % (cle, quoi, hors))


def test_les_trente_cinq_pages_de_CONFORMITE_sont_traduites():
    """CE QUI A ÉTÉ LIVRÉ, ET CE QUI NE L'A PAS ÉTÉ. Les trente-cinq pages
    des huit tiroirs de conformité annoncent leur identité en anglais :
    surtitre, titre, chapeau. Le corps des panneaux reste en français, et
    c'est écrit pour que personne ne prenne l'un pour l'autre.

    LA LISTE DES PAGES N'EST PAS RECOPIÉE : elle est DÉRIVÉE des tiroirs
    marqués `data-fam="conformite"`. Ajouter une page de conformité sans la
    traduire fait donc tomber cette règle, ce qui est le but."""
    grp = sorted(set(re.findall(
        r'data-grp="([a-z0-9-]+)" data-fam="conformite"', SENTINEL)))
    assert len(grp) >= 8, "%d tiroirs de conformité relevés" % len(grp)
    ids = []
    for g in grp:
        ids += re.findall(
            r'data-grp="%s" role="button"[^>]*onclick="go\(.([a-z0-9-]+)' % g,
            SENTINEL)
    ids = list(dict.fromkeys(ids))
    assert len(ids) >= 30, "%d pages de conformité relevées" % len(ids)
    en = _dico("en")
    sans = sorted(i for i in ids
                  if not all("pg.%s.%s" % (i, c) in en for c in ("eb", "h1", "p")))
    assert not sans, (
        "%d page(s) de conformité sans en-tête anglais : %s"
        % (len(sans), sans[:6]))
