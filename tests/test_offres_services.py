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
#  6. SEUL L'APPEL REDIRIGE — LE BLOC EST FAIT POUR ÊTRE LU
# ══════════════════════════════════════════════════════════════════════════
#
# CE QUI A ÉTÉ ESSAYÉ, PUIS RETIRÉ. Les six cartes de service ont porté une
# « surface étirée » : un pseudo-élément transparent du pied, tendu sur toute
# la carte, qui rendait le bloc entier cliquable. Les huit cartes de risque
# l'ont porté aussi. Retiré des unes puis des autres, à la demande : sur les
# quatorze, seul « Ouvrir le module » redirige.
#
# CE QUE LE MOTIF COÛTAIT, ET QU'ON NE VOIT QU'À L'USAGE. Une surface posée
# par-dessus le corps intercepte le clic PARTOUT : plus moyen de sélectionner
# un titre ni une description à la souris, et chaque lecture un peu appuyée
# devient une navigation. Ces cartes se parcourent du regard avant qu'on
# choisisse — le bloc est fait pour être LU, l'appel pour être CLIQUÉ.
#
# MESURER UNE ABSENCE EST PLUS FRAGILE QUE MESURER UNE PRÉSENCE : la règle
# passe aussi le jour où c'est TOUT le bloc qui a disparu. Chacune de celles
# qui suivent porte donc son garde-fou — quelque chose qui doit EXISTER pour
# que l'absence ait un sens.


def _specificite(selecteur):
    """(identifiants, classes+attributs+pseudo-classes, éléments).

    Gardée pour la règle qui surveille la règle décorative `.diff-card > *` :
    le combinateur `>` et le sélecteur universel `*` ne pèsent rien, et c'est
    précisément ce qui s'était fait oublier."""
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
    lisait `index.html` brut : le commentaire qui EXPLIQUE ce motif le cite
    pour l'expliquer, et l'analyseur a recollé la prose et le code en une
    règle qui n'existe pas. Une règle qui tombe — ou qui passe — pour une
    raison sans rapport avec ce qu'elle prétend mesurer ne vaut rien."""
    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", INDEX, re.S))
    return re.sub(r"/\*.*?\*/", " ", css, flags=re.S)


def _regles():
    return [(sel.strip(), corps)
            for sel, corps in re.findall(r"([^{}@]+)\{([^{}]*)\}", _feuille())
            if sel.strip()]


def _declaration(propriete, selecteur_contient, exact=False):
    for sel, corps in _regles():
        if sel != selecteur_contient if exact else selecteur_contient not in sel:
            continue
        m = re.search(r"(?:^|;)\s*%s\s*:\s*([^;]+)" % propriete, corps)
        if m:
            return sel, m.group(1).strip()
    return None, None


def test_AUCUNE_carte_ne_porte_de_surface_etiree():
    """LA DEMANDE, DANS LES DEUX SECTIONS : seul « Ouvrir le module » redirige.

    LE GARDE-FOU. Une règle qui exige l'absence de `::after` passerait aussi
    sur une page vide. On vérifie donc d'abord que les quatorze appels sont
    toujours là — c'est EUX qui doivent rester la seule porte."""
    feuille = _feuille()
    appels = len(CARTES.findall(BLOC))
    assert appels == 6, (
        "%d appel(s) de carte relevés sur 6 : la section a changé de forme et "
        "cette règle ne prouve plus rien" % appels)
    for motif in (".sv-card-go::after", ".risk-go::after"):
        assert motif not in feuille, (
            "%s est revenu : le corps de la carte redirige à nouveau, alors "
            "que seul l'appel le doit" % motif)


def test_aucune_carte_n_annonce_un_clic_qu_elle_ne_rend_pas():
    """UN CURSEUR EN MAIN SUR UNE ZONE INERTE PROMET, PUIS NE TIENT PAS : on
    clique, rien ne se passe, et le visiteur conclut que le site est cassé
    plutôt que de chercher le vrai appel.

    L'APPEL, LUI, DOIT TOUJOURS SE DISTINGUER — sans quoi on aurait retiré
    le faux signal sans laisser le vrai."""
    for carte in (".diff-card:has(.sv-card-go)", ".risk-card:has(.risk-go)"):
        _, v = _declaration("cursor", carte)
        assert v is None, "%s annonce encore un clic : %r" % (carte, v)
    feuille = _feuille()
    assert ".sv-card-go:hover" in feuille and ".risk-go:hover" in feuille, (
        "les appels n'ont plus d'état de survol : rien ne les distingue du "
        "texte qui les entoure")


def test_les_reglages_QUI_NE_SERVAIENT_QUE_le_motif_sont_partis_avec_lui():
    """DU CODE QUI SURVIT À SA RAISON D'ÊTRE EST UNE CHARGE, et pire, un
    piège : le prochain lecteur le prend pour une intention.

    TROIS RÉGLAGES N'EXISTAIENT QUE POUR TENIR LA SURFACE ÉTIRÉE :
      · `position:static` forcé sur le pied, pour qu'il ne devienne pas son
        propre bloc conteneur et que `inset:0` se résolve contre la carte ;
      · `z-index` + `pointer-events:none` sur la liste des puces, pour que
        ses flèches repassent au-dessus de la surface ;
      · `pointer-events:auto` sur la flèche, pour qu'elle reprenne le clic.
    Sans surface, plus rien ne recouvre les flèches : elles ouvrent leur
    module parce que ce sont des liens, et c'est tout."""
    feuille = _feuille()
    for reste in ("> .sv-card-go{position:static",
                  "> .diff-sublist{position:relative",
                  ".diff-sublist .sv-go{position:relative"):
        assert reste not in feuille, (
            "réglage orphelin du motif retiré : %r" % reste)
    _, pe = _declaration("pointer-events", "> .diff-sublist")
    assert pe is None, (
        "la liste des puces est encore privée du pointeur : son texte ne se "
        "sélectionne plus, pour tenir un motif qui n'existe plus")


def test_le_survol_de_la_fleche_est_REVENU_sur_sa_ligne():
    """LE CONTOURNEMENT PART AVEC SA CAUSE. Le survol de la flèche avait été
    déplacé de la ligne vers la carte parce que `pointer-events:none`
    empêchait `li:hover` de se déclencher. La cause est partie ; garder le
    contournement rendrait le repère moins précis qu'il ne peut l'être —
    survoler n'importe où éclairerait les quatre flèches à la fois."""
    feuille = _feuille()
    assert ".diff-sublist li:hover .sv-go{opacity:1" in feuille, (
        "la flèche ne s'éclaire plus au survol de SA ligne")
    assert ".diff-card:hover .sv-go{opacity:1" not in feuille, (
        "le survol de la flèche est resté accroché à la carte entière : les "
        "quatre flèches s'éclairent ensemble et ne désignent plus rien")


def test_le_pied_reste_un_VRAI_lien_et_pas_un_gestionnaire_de_clic():
    """UN `onclick` SUR LA CARTE AURAIT ÉTÉ PLUS COURT À ÉCRIRE, et aurait
    coûté le clavier, le clic du milieu, « ouvrir dans un nouvel onglet » et
    l'annonce par un lecteur d'écran. L'appel reste un <a>."""
    for bloc_nom, motif in (("services", r'<a class="sv-card-go" href="/sentinel'),
                            ("risques", r'<a class="risk-go" href="/sentinel')):
        assert re.search(motif, INDEX), bloc_nom
    for interdit in ("onclick=\"location", "onclick='location",
                     "addEventListener('click'"):
        assert interdit not in BLOC, (
            "la carte navigue par script plutôt que par lien : %r" % interdit)


def test_la_regle_decorative_qui_avait_piege_le_motif_est_toujours_la():
    """CE QUI AVAIT RENDU LE MOTIF FAUX, ET QUI SURVIT AU MOTIF.

    `.card > *,…,.diff-card > *,.risk-card > *{position:relative;z-index:1}`
    positionne tous les enfants directs d'une carte, pour les faire passer
    au-dessus du halo `::before`. C'est elle qui faisait du pied son propre
    bloc conteneur et réduisait la surface étirée à la taille de l'étiquette
    — 152 × 36 px au lieu de 388 × 356.

    LA SURFACE EST PARTIE, LE PIÈGE RESTE. Quiconque rebranchera un
    pseudo-élément positionné sur un enfant de carte le retrouvera. La règle
    ne garde donc plus un réglage : elle garde une CONNAISSANCE, et tombe le
    jour où cette règle décorative change — moment où il faudra relire ce
    commentaire avant de s'appuyer dessus."""
    sel = next((s for s, _ in _regles() if ".diff-card > *" in s), None)
    assert sel, (
        "la règle décorative `.diff-card > *` a disparu : le piège qu'elle "
        "tendait n'existe plus, et ce commentaire est devenu faux")
    _, pos = _declaration("position", ".diff-card > *")
    assert pos == "relative", pos
    assert _specificite(sel) > _specificite(".sv-card-go"), (
        "%s (%s) ne bat plus `.sv-card-go` (%s) : le piège a changé de forme"
        % (sel, _specificite(sel), _specificite(".sv-card-go")))


def test_les_liens_PUBLICS_vers_Sentinel_gardent_la_page_d_accueil():
    """LA RÉGRESSION QUE LE RETRAIT DU MOTIF A CRÉÉE, ET QU'ON N'AVAIT PAS VUE.

    CE QUI SE PASSAIT AVANT, ET QUI FAISAIT UNE CHOSE BIEN. Un script
    attrape-tout ouvrait « /sentinel » dans un NOUVEL ONGLET au clic sur une
    carte. On l'a retiré — il menait au sommaire au lieu du module, et
    doublait l'appel — et on a emporté avec lui la seule chose qu'il faisait
    bien : garder la page d'accueil ouverte.

    CE QUE ÇA DONNAIT. Ces vingt-sept liens partent d'une page PUBLIQUE et
    visent un produit derrière authentification : ils s'adressent par
    construction à quelqu'un qui n'est PAS connecté. En restant dans l'onglet
    courant, un clic remplaçait l'accueil par un formulaire de connexion. Le
    lien marchait, la destination était juste, et la visite s'arrêtait là.
    Mesuré au navigateur : « après un vrai clic → /login?suite=… ».

    `rel="noopener"` N'EST PAS DÉCORATIF : sans lui, la page ouverte reçoit
    une référence sur celle qui l'a ouverte et peut la rediriger ailleurs.
    """
    liens = re.findall(
        r'<a class="(risk-go|sv-card-go|sv-go)" href="/sentinel\?goto=[^"]*"'
        r'([^>]*)>', INDEX)
    assert len(liens) == 27, (
        "%d lien(s) publics vers Sentinel relevés sur 27 : la lecture a "
        "changé de forme et cette règle ne prouve plus rien" % len(liens))
    for classe, attrs in liens:
        assert 'target="_blank"' in attrs, (
            "un lien %s reste dans l'onglet courant : le visiteur non "
            "connecté perd la page d'accueil pour un formulaire" % classe)
        assert "noopener" in attrs, (
            "un lien %s ouvre un onglet sans `noopener` : la page ouverte "
            "garde la main sur celle qui l'a ouverte" % classe)
