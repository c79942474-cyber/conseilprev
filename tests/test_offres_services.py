# -*- coding: utf-8 -*-
"""Les six offres de services mènent à leur module Sentinel.

LA DEMANDE : « connecter avec des liens les 6 offres de services, renvoyer
aux bons modules du site Sentinel ».

TROIS FAÇONS DE RATER CE LIEN, ET ELLES SE RATENT EN SILENCE.

  1. LE LIEN MÈNE À UN ÉCRAN QUI N'EXISTE PAS. `/sentinel?goto=xxx` sur un
     identifiant inconnu n'affiche pas d'erreur : Sentinel ouvre sa page
     d'accueil, et le visiteur croit avoir mal cliqué. Un lien mort se
     remarque ; un lien qui atterrit à côté ne se remarque pas.

  2. LE LIEN EST EFFACÉ PAR LA TRADUCTION. `applyLang` fait
     `el.innerHTML = <traduction>` sur tout élément porteur d'un `data-i18n`.
     Un <a> écrit à l'intérieur disparaît au chargement, sans erreur et sans
     trace. Ce dépôt a déjà payé ce défaut : la mention « texte seul » de la
     carte DORA était morte pour cette raison exacte, et personne ne l'a vu
     avant une capture d'écran.

  3. LE LIEN MÈNE AU MAUVAIS MODULE. Une flèche vers un écran seulement
     voisin du sujet apprend au lecteur à ne plus croire les flèches — un
     prix bien plus élevé que celui d'une ligne sans lien. Les règles de la
     §3 exigent donc que la destination soit NOMMÉE par la ligne qui la
     porte.
"""
import io
import json
import os
import re

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _lire(nom):
    with io.open(os.path.join(_RACINE, nom), encoding="utf-8") as f:
        return f.read()


INDEX = _lire("index.html")
INDEXJS = _lire("index.page.js")
SENTINEL = _lire("sentinel.html")
SENTINELJS = _lire("sentinel.page.js")


def _bloc_services():
    deb = INDEX.index('<section class="sec" id="services">')
    fin = INDEX.index("</section>", INDEX.index("</div>\n</section>", deb))
    return INDEX[deb:fin]


BLOC = _bloc_services()
CARTES = re.compile(r'class="sv-card-go" href="/sentinel\?goto=([a-z0-9-]+)"')
PUCES = re.compile(r'class="sv-go" href="/sentinel\?goto=([a-z0-9-]+)"')


def _panneaux():
    return set(re.findall(r'<div class="page[^"]*" id="p-([A-Za-z0-9_-]+)"',
                          SENTINEL))


def _onglets():
    return set(re.findall(r"go\('([a-z0-9-]+)',this,", SENTINEL))


def _dico(lg):
    m = re.search(r"\n\s*%s:JSON\.parse\(`(.*?)`\)" % lg, INDEXJS, re.S)
    assert m, "dictionnaire %s introuvable" % lg
    return json.loads(m.group(1).replace("\\`", "`"))


# ══════════════════════════════════════════════════════════════════════════
#  1. LES SIX OFFRES SONT LIÉES — TOUTES LES SIX
# ══════════════════════════════════════════════════════════════════════════

def test_la_lecture_du_bloc_n_est_pas_vide():
    """LE GARDE-FOU DES RÈGLES SUIVANTES. Une lecture qui rendrait zéro carte
    ferait passer toutes les comparaisons pour des comparaisons de vides —
    c'est arrivé une fois dans ce dépôt, et la recette est restée verte."""
    assert len(BLOC) > 2000
    assert BLOC.count('class="diff-card"') == 6, (
        "le bloc des services ne porte plus six cartes : %d"
        % BLOC.count('class="diff-card"'))


def test_CHACUNE_des_six_offres_porte_son_lien_vers_un_module():
    """CINQ CARTES SUR SIX LIÉES, C'EST UNE SECTION QUI PARAÎT LIÉE et dont
    une offre reste muette — le lecteur conclut qu'il a mal cliqué, pas que
    ce lien-là n'existe pas."""
    titres = re.findall(r'<h3 class="diff-title" data-i18n="(sv\.[a-z0-9]+)\.t">',
                        BLOC)
    liens = CARTES.findall(BLOC)
    assert len(titres) == 6, titres
    assert len(liens) == 6, (
        "%d offre(s) sur %d portent un lien vers leur module"
        % (len(liens), len(titres)))


def test_les_six_offres_ne_mènent_pas_toutes_au_MEME_module():
    """SIX LIENS VERS LE MÊME ÉCRAN NE CONNECTENT RIEN : ils déplacent le
    problème d'un cran. Chaque offre a son instrument, et c'est ce qui rend
    la section utile."""
    liens = CARTES.findall(BLOC)
    assert len(set(liens)) == len(liens), (
        "deux offres mènent au même module : %s"
        % [c for c in set(liens) if liens.count(c) > 1])


#  ─── CHAQUE OFFRE VA À SON MODULE, ET PAS À UN AUTRE ──────────────────
#
# LE TROU QUE CES RÈGLES LAISSAIENT. Elles exigeaient six liens, six
# destinations DIFFÉRENTES, et six panneaux existants. Échanger deux cartes
# — « Formation » vers la gouvernance, « Gouvernance » vers la formation —
# satisfaisait les trois : six liens, six cibles distinctes, six panneaux
# réels. La section aurait été entièrement fausse et entièrement verte.
#
# CE QUE LA TABLE AJOUTE, ET CE QU'ELLE NE PEUT PAS AJOUTER. Elle fige le
# couple (offre, module) et, pour cinq des six, le MOT que l'offre et le
# module partagent — lu dans `PAGE_META`, c'est-à-dire dans la déclaration
# de Sentinel lui-même, pas dans une copie tenue ici. Renommer la page
# Sentinel fait donc tomber la règle, et c'est voulu : un lien survit mal à
# une page qui a changé de sujet.
#
# LA SIXIÈME N'A PAS DE MOT COMMUN, et c'est déclaré plutôt que contourné.
# « Intégration Solutions IA » ouvre « Développement assisté par IA »,
# rangé sous « BUSINESS ». Les deux disent la même chose dans deux
# vocabulaires — celui du client et celui de l'outil. Le seul mot partagé
# serait « IA », qui figure dans presque tous les libellés du produit :
# l'exiger ferait passer n'importe quel lien. On l'écrit `None` pour que le
# trou soit visible, plutôt qu'aveuglé par un contrôle complaisant.

CARTE_VERS = {
    "sv.audit": ("audit-ia-act", "audit"),
    "sv.r8":    ("radar",        "risque"),
    "sv.conf":  ("conf-taux",    "conformité"),
    "sv.integ": ("ingenierie",   None),
    "sv.form":  ("training",     "formation"),
    "sv.grc":   ("gouvernance",  "gouvernance"),
}


def _page_meta():
    """{identifiant: « section label »} tel que Sentinel le déclare."""
    i = SENTINELJS.index("var PAGE_META = {")
    bloc = SENTINELJS[i:SENTINELJS.index("\n};", i)]
    return {c: (sec + " " + lab).lower() for c, sec, lab in re.findall(
        r"'?([A-Za-z0-9_-]+)'?\s*:\s*\{\s*section\s*:\s*'([^']*)'\s*,"
        r"\s*label\s*:\s*'([^']*)'", bloc)}


def test_chaque_offre_ouvre_SON_module_et_le_nomme_comme_Sentinel():
    """DEUX CARTES ÉCHANGÉES PASSAIENT TOUTES LES AUTRES RÈGLES. Celle-ci
    lie chaque offre à son module, et vérifie que le mot qui justifie le
    lien se trouve bien dans ce que SENTINEL dit de sa page."""
    meta = _page_meta()
    assert len(meta) > 40, (
        "la lecture de PAGE_META rend %d entrées : ce contrôle ne prouve "
        "plus rien" % len(meta))

    cartes = re.findall(
        r'<h3 class="diff-title" data-i18n="(sv\.[a-z0-9]+)\.t">'
        r'(?:(?!</div>).)*?'
        r'class="sv-card-go" href="/sentinel\?goto=([a-z0-9-]+)"',
        BLOC, re.S)
    assert len(cartes) == 6, (
        "%d couple(s) (titre, destination) relevés sur 6 : la lecture a "
        "glissé d'une carte à l'autre" % len(cartes))

    for cle, cible in cartes:
        attendu = CARTE_VERS.get(cle)
        assert attendu, (
            "l'offre « %s » n'est pas déclarée dans CARTE_VERS : ajoutez-la "
            "avec le module qu'elle doit ouvrir" % cle)
        module, mot = attendu
        assert cible == module, (
            "l'offre « %s » ouvre « %s » au lieu de « %s »"
            % (cle, cible, module))
        if mot is None:
            continue
        assert module in meta, (
            "« %s » n'a plus de fiche dans PAGE_META : le visiteur y arrive "
            "sans savoir où il est" % module)
        assert mot in meta[module], (
            "l'offre « %s » ouvre « %s », que Sentinel intitule « %s » : le "
            "mot « %s » qui justifiait le lien n'y est plus — relire le lien "
            "avant de le garder" % (cle, module, meta[module], mot))


# ══════════════════════════════════════════════════════════════════════════
#  2. AUCUN LIEN NE MÈNE DANS LE VIDE
# ══════════════════════════════════════════════════════════════════════════

def test_chaque_destination_existe_comme_PANNEAU_ET_comme_ONGLET():
    """`/sentinel?goto=xxx` SUR UN IDENTIFIANT INCONNU N'AFFICHE PAS D'ERREUR :
    Sentinel ouvre sa page d'accueil et le visiteur croit avoir mal cliqué.

    LES DEUX CONDITIONS COMPTENT. Un panneau sans onglet s'ouvre par le lien
    mais reste introuvable ensuite ; un onglet sans panneau ouvre du vide.
    """
    panneaux, onglets = _panneaux(), _onglets()
    assert len(panneaux) > 50 and len(onglets) > 50, (
        "la lecture de sentinel.html rend %d panneaux et %d onglets : ce "
        "contrôle ne prouve plus rien" % (len(panneaux), len(onglets)))
    for cible in CARTES.findall(BLOC) + PUCES.findall(BLOC):
        assert cible in panneaux, (
            "le lien mène à « %s », qui n'est pas un panneau de Sentinel"
            % cible)
        assert cible in onglets, (
            "« %s » est un panneau mais aucun onglet n'y mène : le visiteur "
            "y arrive et ne saura pas y revenir" % cible)


def test_aucun_lien_de_service_ne_sort_du_site():
    """UN LIEN ABSOLU VERS LE SITE DE PRODUCTION casserait la navigation en
    recette et en local, et personne ne s'en apercevrait avant la mise en
    ligne suivante."""
    for href in re.findall(r'class="sv-(?:card-)?go" href="([^"]+)"', BLOC):
        assert href.startswith("/sentinel?goto="), (
            "lien de service hors du site : %r" % href)


# ══════════════════════════════════════════════════════════════════════════
#  3. LE LIEN MÈNE LÀ OÙ SA LIGNE LE DIT
# ══════════════════════════════════════════════════════════════════════════

# CE QUE CHAQUE DESTINATION DOIT PORTER DANS LE TEXTE QUI LA DÉSIGNE. La
# règle ne juge pas la pertinence — elle vérifie que la ligne NOMME ce vers
# quoi elle pointe. Une flèche « ISO 27001 » qui ouvrirait le RGPD tombe ici.
NOMME = {
    "iso42001": ("iso 42001", "42001"),
    "iso27001": ("iso 27001", "27001"),
    "iso27001-risques": ("iso 27001", "27001"),
    "nis2": ("nis2", "nis 2"),
    "nis2-qualifier": ("nis2", "nis 2"),
    "rgpd-pbd": ("rgpd", "privacy"),
    "conf-plan": ("conformité", "écarts"),
    "simulateur": ("classification", "risque"),
    "fria": ("impact",),
    "matrice": ("matrice",),
    "adoption": ("change management", "adoption"),
    "report": ("reporting", "kpi"),
}


def test_chaque_PUCE_liée_nomme_le_module_qu_elle_ouvre():
    """LA RÈGLE QUI EMPÊCHE LE LIEN APPROXIMATIF. Une flèche vers un écran
    seulement voisin du sujet apprend au lecteur à ne plus croire les
    flèches, et ce prix-là est bien plus élevé que celui d'une ligne sans
    lien.
    """
    puces = re.findall(
        r'<li><span data-i18n="([^"]+)">([^<]*)</span>'
        r'<a class="sv-go" href="/sentinel\?goto=([a-z0-9-]+)"', BLOC)
    assert len(puces) >= 10, "seulement %d puces liées" % len(puces)
    for cle, texte, cible in puces:
        attendus = NOMME.get(cible)
        assert attendus, (
            "la puce « %s » mène à « %s », dont aucun mot n'est attendu : "
            "ajoutez-le à NOMME avec ce que la ligne doit dire, ou changez "
            "de destination" % (texte, cible))
        bas = texte.lower()
        assert any(a in bas for a in attendus), (
            "la puce « %s » ouvre « %s » sans le nommer — attendu l'un de %s"
            % (texte, cible, list(attendus)))


def test_une_puce_qui_ne_nomme_aucun_module_N_EST_PAS_liée():
    """LES PUCES SANS FLÈCHE NE SONT PAS UN OUBLI, et cette règle le fige.

    « Jumeaux numériques & IoT », « MLOps & monitoring IA », « Coaching
    équipes DSI/RSSI », « Monitoring post-déploiement » : aucun écran de
    Sentinel ne porte précisément ces sujets. Les lier à un module voisin
    serait le défaut que la règle précédente interdit — celle-ci empêche de
    le réintroduire par l'autre bout, en « complétant » la section.
    """
    sans_module = ["jumeaux", "mlops", "coaching", "post-déploiement",
                   "architecture ia"]
    for li in re.findall(r"<li>.*?</li>", BLOC, re.S):
        bas = re.sub(r"<[^>]+>", " ", li).lower()
        if not any(m in bas for m in sans_module):
            continue
        assert 'class="sv-go"' not in li, (
            "cette ligne a reçu une flèche alors qu'aucun écran ne porte son "
            "sujet : %s" % re.sub(r"\s+", " ", bas).strip()[:70])


# ══════════════════════════════════════════════════════════════════════════
#  4. LA TRADUCTION NE PEUT PAS EFFACER LE LIEN
# ══════════════════════════════════════════════════════════════════════════

def test_applyLang_remplace_bien_l_innerHTML_et_pas_le_texte():
    """LE GARDE-FOU DE TOUTE LA §4. Si `applyLang` posait un `textContent`,
    le danger que les règles suivantes écartent n'existerait pas — et elles
    passeraient au vert en ne mesurant plus rien. On vérifie donc d'abord
    que le danger est réel."""
    i = INDEXJS.index("function applyLang()")
    bloc = INDEXJS[i:i + 400]
    assert "innerHTML" in bloc, (
        "applyLang n'écrase plus l'innerHTML : ces règles doivent être "
        "revues, pas supprimées")


def test_aucun_lien_de_service_ne_vit_DANS_un_element_traduit():
    """LE DÉFAUT DÉJÀ PAYÉ UNE FOIS DANS CE DÉPÔT. Un <a> placé à l'intérieur
    d'un porteur de `data-i18n` est effacé au chargement par
    `el.innerHTML = <traduction>` : le lien disparaît sans erreur, et la page
    paraît simplement ne pas en avoir.
    """
    for m in re.finditer(r'<(li|h3|p|div)([^>]*data-i18n="[^"]+"[^>]*)>(.*?)</\1>',
                         BLOC, re.S):
        assert 'class="sv-go"' not in m.group(3) \
            and 'class="sv-card-go"' not in m.group(3), (
            "un lien de service est écrit DANS un élément traduit (%s) : la "
            "traduction l'effacera au chargement" % m.group(0)[:90])


def test_le_libelle_de_l_appel_est_traduit_dans_les_TROIS_langues():
    """UNE CLÉ PRÉSENTE D'UN CÔTÉ SEULEMENT laisse l'appel en français sur la
    version anglaise, et rien ne le signale à qui relit le français."""
    assert BLOC.count('<span data-i18n="sv.go">') == 6, (
        "les six appels ne portent pas tous la clé traduite : %d"
        % BLOC.count('<span data-i18n="sv.go">'))
    for lg in ("fr", "en", "de"):
        d = _dico(lg)
        assert d.get("sv.go"), "sv.go absent du dictionnaire %s" % lg
    assert len({_dico(lg)["sv.go"] for lg in ("fr", "en", "de")}) == 3, (
        "deux langues partagent le même libellé d'appel : l'une des trois "
        "n'a pas été traduite")


def test_la_fleche_de_chaque_puce_reste_hors_du_span_traduit():
    """LA MÊME RÈGLE, VUE DE L'AUTRE CÔTÉ : la flèche doit être VOISINE du
    <span> traduit, jamais dedans. C'est ce qui la rend intouchable."""
    puces = re.findall(r'<li><span data-i18n="[^"]+">[^<]*</span>'
                       r'<a class="sv-go"', BLOC)
    total = BLOC.count('class="sv-go"')
    assert len(puces) == total, (
        "%d flèche(s) sur %d ne sont pas posées en voisines d'un span "
        "traduit" % (total - len(puces), total))


# ══════════════════════════════════════════════════════════════════════════
#  5. CE QUI SE CLIQUE SE VOIT, ET SE VISE AU CLAVIER
# ══════════════════════════════════════════════════════════════════════════

def test_chaque_lien_dit_OU_il_mene_avant_le_clic():
    """UNE FLÈCHE NUE NE DIT RIEN — ni au survol, ni à un lecteur d'écran."""
    for m in re.finditer(r'<a class="sv-go"([^>]*)>', BLOC):
        attrs = m.group(1)
        assert 'title="Ouvre ' in attrs, attrs[:80]
        assert 'aria-label="Ouvrir ' in attrs, (
            "flèche sans nom accessible : elle se lira « lien » et rien de "
            "plus : %s" % attrs[:80])
    for m in re.finditer(r'<a class="sv-card-go"([^>]*)>', BLOC):
        assert 'title="Ouvre ' in m.group(1), m.group(1)[:80]


def test_les_deux_sortes_de_liens_ont_un_etat_de_focus_visible():
    """AU CLAVIER, UN LIEN SANS ÉTAT DE FOCUS EST UN LIEN QU'ON NE PEUT PAS
    SUIVRE : on ne sait jamais où l'on est."""
    for cls in (".sv-go", ".sv-card-go"):
        assert ("%s:focus-visible{" % cls) in INDEX, (
            "%s n'a pas d'état de focus visible" % cls)


def test_le_mouvement_de_la_fleche_se_coupe_pour_qui_le_demande():
    src = INDEX.replace(" ", "")
    blocs = re.findall(r"prefers-reduced-motion:reduce\)\{(.*?)\}\n", src, re.S)
    vise = [b for b in blocs if ".sv-go" in b]
    assert vise, (
        "la flèche se déplace au survol sans que `prefers-reduced-motion` "
        "n'arrête rien")
    assert any("transition:none" in b for b in vise), vise

# ══════════════════════════════════════════════════════════════════════════
#  6. LE BLOC ENTIER EST LE LIEN, PAS SEULEMENT SON PIED
# ══════════════════════════════════════════════════════════════════════════

def test_la_carte_entiere_declenche_le_lien_de_son_pied():
    """CE QUI MANQUAIT, ET QUI SE VOYAIT À L'USAGE. Chaque carte portait bien
    sa destination, mais seule l'étiquette « Ouvrir le module » la
    déclenchait : cliquer sur le titre, l'icône ou la description ne faisait
    rien. Une carte qui s'éclaire au survol sur toute sa surface et ne répond
    que sur vingt pixels enseigne au visiteur qu'elle n'est pas cliquable.
    """
    assert ".diff-card{position:relative}" in INDEX, (
        "sans repère de position sur la carte, la surface étirée du pied se "
        "cale sur un ancêtre quelconque")
    assert ".sv-card-go::after{content:'';position:absolute;" \
        "inset:0;z-index:1}" in INDEX, (
        "le pied de carte ne couvre plus la carte : seule l'étiquette reste "
        "cliquable")
    #  LE MOTIF NE DOIT PAS REVENIR SUR LES CARTES DE RISQUE. Elles l'ont
    #  porté quelques heures, puis on l'a retiré : sur elles, seul
    #  « Ouvrir le module » redirige. Le rebrancher par une liste de
    #  sélecteurs élargie, sans y penser, est l'erreur facile.
    assert ".risk-go::after" not in INDEX, (
        "les cartes de risque ont retrouvé une surface étirée : sur elles, "
        "seul « Ouvrir le module » doit rediriger")


def test_le_pied_reste_un_VRAI_lien_et_pas_un_gestionnaire_de_clic():
    """UN `onclick` SUR LA CARTE AURAIT ÉTÉ PLUS COURT À ÉCRIRE, et aurait
    coûté le clavier, le clic du milieu, « ouvrir dans un nouvel onglet » et
    l'annonce par un lecteur d'écran. La surface étirée garde un <a>."""
    for bloc_nom, motif in (("services", r'<a class="sv-card-go" href="/sentinel'),
                            ("risques", r'<a class="risk-go" href="/sentinel')):
        assert re.search(motif, INDEX), bloc_nom
    for interdit in ("onclick=\"location", "onclick='location",
                     "addEventListener('click'"):
        i = INDEX.find('<section class="sec" id="services">')
        j = INDEX.index("</section>", INDEX.index("</div>\n</section>", i))
        assert interdit not in INDEX[i:j], (
            "la carte navigue par script plutôt que par lien : %r" % interdit)


def _specificite(selecteur):
    """(identifiants, classes+attributs+pseudo-classes, éléments).

    Assez pour arbitrer les sélecteurs de cette feuille : ni `:has()`, ni
    `:is()`, ni `!important` n'y interviennent sur les règles en cause. Le
    combinateur `>` et le sélecteur universel `*` ne pèsent rien — c'est
    précisément ce qui s'est fait oublier : `.diff-card > *` vaut (0,1,0),
    pas (0,1,1)."""
    net = re.sub(r"[>+~]", " ", selecteur)
    ids = len(re.findall(r"#[\w-]+", net))
    cls = (len(re.findall(r"\.[\w-]+", net))
           + len(re.findall(r"\[[^\]]+\]", net))
           + len(re.findall(r"(?<!:):[\w-]+(?:\([^)]*\))?", net)))
    elt = len(re.findall(r"(?:^|\s)(?!\*)([a-zA-Z][\w-]*)", net))
    return (ids, cls, elt)


def _feuille():
    """Le CSS de la page, commentaires retirés.

    SANS CE NETTOYAGE, LA RÈGLE SE MENT À ELLE-MÊME. Une première version
    lisait `index.html` brut : le commentaire qui EXPLIQUE ce défaut cite
    `.card > *,…{position:relative;z-index:1}` et nomme `.sv-card-go`
    quelques lignes plus bas. L'analyseur a recollé les deux et a cru lire
    une règle qui n'existe pas — la garde tombait sur sa propre prose. Une
    règle qui échoue pour une raison sans rapport avec ce qu'elle prétend
    mesurer ne vaut pas mieux qu'une règle qui passe pour une telle raison.
    """
    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", INDEX, re.S))
    return re.sub(r"/\*.*?\*/", " ", css, flags=re.S)


def _regles():
    """(sélecteur, corps) pour chaque règle de la feuille. Les blocs `@media`
    sont aplatis : leur en-tête ne survit pas au découpage, et aucune des
    règles en cause ici n'y figure."""
    return [(sel.strip(), corps)
            for sel, corps in re.findall(r"([^{}@]+)\{([^{}]*)\}", _feuille())
            if sel.strip()]


def _declaration(propriete, selecteur_contient, exact=False):
    """La valeur déclarée pour `propriete` dans la règle dont le sélecteur
    contient — ou vaut exactement — `selecteur_contient`."""
    for sel, corps in _regles():
        if sel != selecteur_contient if exact else selecteur_contient not in sel:
            continue
        m = re.search(r"(?:^|;)\s*%s\s*:\s*([^;]+)" % propriete, corps)
        if m:
            return sel, m.group(1).strip()
    return None, None


def test_le_pied_de_carte_ne_devient_PAS_son_propre_bloc_conteneur():
    """LE DÉFAUT MESURÉ, ET CE QUI LE RENDAIT INVISIBLE À LA LECTURE.

    `inset:0` ne se résout pas contre la carte : il se résout contre le PLUS
    PROCHE ANCÊTRE POSITIONNÉ. Une règle décorative écrite bien plus haut
    dans cette feuille — `.card > *,…,.diff-card > *,.risk-card > *
    {position:relative;z-index:1}`, posée pour faire passer le contenu
    au-dessus du halo `::before` — positionne DÉJÀ le pied de carte. Le pied
    devenait alors son propre bloc conteneur, et la surface étirée mesurait
    152 × 36 px au lieu de 388 × 356 : elle ne couvrait que l'étiquette. Le
    CSS avait l'air juste, ligne à ligne ; c'est la RENCONTRE de deux règles
    écrites à deux mille lignes d'écart qui était fausse.

    La règle mesure donc les deux faits qui décident, pas le texte :
    le pied est ramené à `position:static`, et il l'est par un sélecteur
    ASSEZ SPÉCIFIQUE pour battre celui qui le positionnait."""
    sel_pied, pos = _declaration(
        "position", ".diff-card > .sv-card-go", exact=True)
    assert pos == "static", (
        "le pied de carte est positionné (%r) : `inset:0` se résout contre "
        "LUI et la surface ne couvre plus que l'étiquette" % (pos,))

    sel_enfants = next((sel for sel, _ in _regles()
                        if ".diff-card > *" in sel), None)
    assert sel_enfants, (
        "la règle décorative `.diff-card > *` a disparu ; cette garde ne "
        "protège donc plus de rien et doit être réécrite sur ce qui la "
        "remplace")
    assert _specificite(sel_pied) > _specificite(".diff-card > *"), (
        "%r (%s) ne bat pas `.diff-card > *` (%s) : le pied reste positionné"
        % (sel_pied, _specificite(sel_pied), _specificite(".diff-card > *")))


def test_les_fleches_INTERNES_repassent_au_dessus_de_la_surface_etiree():
    """LE DÉFAUT QUE CE MOTIF CRÉE QUAND ON L'APPLIQUE SANS Y PENSER, et il
    ne vient pas d'où on le croit.

    La surface étirée du pied recouvre toute la carte. Les treize flèches
    des puces passaient dessous et ouvraient le module de LEUR CARTE au lieu
    du leur — 13 sur 13, mesuré au clic. La cause n'est pas un z-index
    manquant sur la flèche : `.diff-sublist` porte `opacity:.75` depuis
    toujours, et une opacité inférieure à 1 crée un CONTEXTE D'EMPILEMENT.
    Tout z-index posé à l'intérieur y reste prisonnier. C'est la liste
    entière qu'il faut élever.

    La règle compare donc deux nombres tirés de la feuille — celui de la
    surface et celui de la liste — au lieu de vérifier qu'une ligne est
    écrite. Baisser l'un, monter l'autre ou supprimer l'opacité sans revoir
    le reste la fait tomber."""
    _, z_surface = _declaration("z-index", ".sv-card-go::after")
    sel_liste, z_liste = _declaration("z-index", "> .diff-sublist")
    assert z_surface and z_liste, (z_surface, z_liste)
    assert int(z_liste) > int(z_surface), (
        "la liste des puces (z-index:%s) passe sous la surface étirée "
        "(z-index:%s) : ses flèches ouvriraient le module de la carte"
        % (z_liste, z_surface))

    _, opacite = _declaration("opacity", ".diff-sublist", exact=True)
    assert opacite is not None and float(opacite) < 1, (
        "`.diff-sublist` n'atténue plus ses lignes : le contexte "
        "d'empilement qu'elle créait a disparu, et l'élévation ci-dessus "
        "n'a plus de raison d'être — relire le motif avant de la garder")


def test_seule_la_FLECHE_reprend_le_pointeur_dans_la_liste_elevee():
    """CE QU'ÉLEVER LA LISTE COÛTERAIT SI ON S'ARRÊTAIT LÀ.

    Une liste au-dessus de la surface intercepte aussi le clic sur le TEXTE
    de ses puces — et ce texte ne mène nulle part. Le visiteur trouverait
    alors, au milieu d'une carte cliquable partout, quatre lignes mortes.
    La liste rend donc le pointeur (`pointer-events:none`) et seule la
    flèche le reprend."""
    _, pe_liste = _declaration("pointer-events", "> .diff-sublist")
    _, pe_fleche = _declaration("pointer-events", ".diff-sublist .sv-go")
    assert pe_liste == "none", (
        "le texte des puces intercepte le clic sans mener nulle part : %r"
        % (pe_liste,))
    assert pe_fleche == "auto", (
        "la flèche ne reprend pas le pointeur : elle est décorative %r"
        % (pe_fleche,))


def test_le_survol_de_la_fleche_suit_la_CARTE_et_non_la_ligne():
    """LA CONSÉQUENCE OUBLIÉE DE `pointer-events:none`. `li:hover` ne se
    déclenche plus. Une règle restée sur la ligne laisserait les treize
    flèches à `opacity:.55` en permanence : visibles, mais jamais mises en
    avant. Elles suivent donc le survol de la carte, qui est de toute façon
    devenue l'objet cliquable."""
    assert ".diff-sublist li:hover .sv-go" not in INDEX, (
        "le survol de la flèche est accroché à la ligne, qui ne reçoit plus "
        "le pointeur : la règle ne se déclenchera jamais")
    assert ".diff-card:hover .sv-go{opacity:1" in INDEX, (
        "rien ne met la flèche en avant quand la carte est survolée")


def test_la_carte_cliquable_le_dit_par_son_curseur():
    """RIEN NE SIGNALE UNE ZONE CLIQUABLE COMME LE CURSEUR. Une carte qui se
    clique sans le montrer ne sera cliquée que par accident."""
    assert ".diff-card:has(.sv-card-go){cursor:pointer}" in INDEX, (
        "la carte ne montre pas qu'elle se clique — et le `:has` vise celles "
        "QUI PORTENT un pied, jamais une carte sans destination")
    assert ".risk-card:has(.risk-go){cursor:pointer}" not in INDEX, (
        "la carte de risque annonce un clic qu'elle ne rend plus")
