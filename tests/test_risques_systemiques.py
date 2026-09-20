# -*- coding: utf-8 -*-
"""Les huit risques systémiques IA mènent au module qui les adresse.

LA DEMANDE : « faire pareil pour les 8 risques systémiques IA que nous
adressons dans Sentinel » — après les six offres de services.

CE QUE LA SECTION FAISAIT AVANT. Huit cartes qui nomment huit risques, et une
seule bannière en pied vers « /sentinel » tout court, c'est-à-dire l'accueil.
Après une section qui vient de nommer huit sujets précis, atterrir sur un
sommaire ne résout pas la question « où est-ce traité ? » : elle la déplace
d'un cran, et c'est le visiteur qui doit chercher.

UNE MIRE QUE PERSONNE NE SURVEILLAIT. `sentinel.page.js` déclare les huit
risques dans `SYSTEMIC_RISKS`, avec ce commentaire : « identiques a la page
d'accueil CONSEILPREV ». Rien ne le vérifiait. Les deux listes pouvaient
diverger — un libellé réécrit d'un côté, un risque ajouté de l'autre — sans
qu'aucune recette ne tombe, et le radar aurait pondéré des risques que la
vitrine ne nomme plus. La §1 tient cette mire.

LE RESTE REPREND LA DOCTRINE DES SIX OFFRES, pour les mêmes raisons : un
`?goto=` inconnu n'affiche aucune erreur, et un lien écrit dans un élément
traduit est effacé au chargement par `applyLang`.
"""
import html
import io
import json
import os
import re

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _lire(nom):
    with io.open(os.path.join(_RACINE, nom), encoding="utf-8") as f:
        return f.read()


INDEX = _lire("index.html")
INDEXJS = _lire("index.page.js")
SENTINEL = _lire("sentinel.html")
PAGEJS = _lire("sentinel.page.js")


def _bloc():
    deb = INDEX.index('<section class="sec sec-a" id="risques">')
    return INDEX[deb:INDEX.index("</section>", deb)]


BLOC = _bloc()

#  UNE DESTINATION EST UN COUPLE (PAGE, POINT), PLUS UNE PAGE.
#
#  POURQUOI CE N'EST PAS UN RAFFINEMENT COSMÉTIQUE. La carte Supply Chain
#  annonçait « Value Chain and Component Integration ». Le lien ouvrait la
#  page qui contient cet item — et le visiteur tombait sur une liste où rien
#  ne portait ce nom en façade. La navigation réussissait, la promesse non.
#  `?point=` nomme l'endroit ; ces règles le lisent donc aussi, sans quoi
#  elles continueraient de valider une page en ignorant ce qu'on y cherche.
LIENS = re.compile(
    r'class="risk-go" href="/sentinel\?goto=([a-z0-9-]+)'
    r'(?:&amp;point=([A-Za-z0-9_-]+))?"')


def _destinations():
    """(page, point) pour chaque carte ; point vaut '' quand la carte vise
    la page entière."""
    return LIENS.findall(BLOC)


def _pages():
    return [pg for pg, _ in _destinations()]


def _libelle(dest):
    pg, pt = dest
    return pg + ('#' + pt if pt else '')


def _cartes():
    """(clé, libellé) des huit cartes de la vitrine."""
    return [(c, html.unescape(t)) for c, t in re.findall(
        r'<h3 class="risk-title" data-i18n="rk\.([a-z]+)\.t">([^<]*)</h3>',
        BLOC)]


def _declares():
    """(id, libellé) des huit risques déclarés dans Sentinel."""
    i = PAGEJS.index("var SYSTEMIC_RISKS = [")
    return re.findall(r'\{id:"([a-z_]+)", label:"([^"]*)"',
                      PAGEJS[i:PAGEJS.index("];", i)])


def _panneaux():
    return set(re.findall(r'<div class="page[^"]*" id="p-([A-Za-z0-9_-]+)"',
                          SENTINEL))


def _onglets():
    return set(re.findall(r"go\('([a-z0-9-]+)',this,", SENTINEL))


# ══════════════════════════════════════════════════════════════════════════
#  1. LA MIRE QUE PERSONNE NE SURVEILLAIT
# ══════════════════════════════════════════════════════════════════════════

def test_la_lecture_des_deux_listes_n_est_pas_vide():
    """LE GARDE-FOU DE TOUTE LA §1. Une lecture qui rendrait zéro risque d'un
    côté ferait passer la comparaison pour une comparaison de vides — c'est
    arrivé une fois dans ce dépôt, et la recette est restée verte.

    ON COMPTE LES CARTES, PAS SEULEMENT LEURS TITRES. Une première version
    ne relevait que les <h3> : une carte qui perdait sa classe `risk-card`
    gardait son titre, et le compte restait à huit — alors que la carte
    n'était plus une carte, que la mise en page en colonne tombait avec elle
    et que son appel cessait de s'aligner. Mesuré par une mutation, ce
    contrôle n'a rien vu.
    """
    titres = _cartes()
    cartes = BLOC.count('<div class="risk-card">')
    liens = len(LIENS.findall(BLOC))
    assert len(titres) == 8, titres
    assert len(_declares()) == 8, _declares()
    assert cartes == 8, (
        "%d carte(s) portent la classe `risk-card` pour %d titre(s)"
        % (cartes, len(titres)))
    assert liens == cartes, (
        "%d lien(s) pour %d carte(s)" % (liens, cartes))


def test_les_huit_cartes_et_les_huit_risques_DECLARES_disent_la_meme_chose():
    """`SYSTEMIC_RISKS` PORTE LE COMMENTAIRE « identiques a la page d'accueil
    CONSEILPREV », et rien ne le vérifiait.

    Les deux listes pouvaient diverger sans bruit : un libellé réécrit d'un
    côté, un risque ajouté de l'autre, et le radar aurait pondéré des risques
    que la vitrine ne nomme plus — ou l'inverse. Le visiteur qui suit le lien
    d'une carte arriverait alors sur un écran qui ne connaît pas son risque.

    ON DÉSÉCHAPPE AVANT DE COMPARER. La vitrine écrit « Data &amp; IA » là où
    le JavaScript écrit « Data & IA » : une règle qui comparerait les chaînes
    brutes tomberait sur une différence d'encodage, c'est-à-dire pour une
    raison sans rapport avec ce qu'elle prétend mesurer.
    """
    vitrine = [t for _, t in _cartes()]
    sentinel = [t for _, t in _declares()]
    assert vitrine == sentinel, (
        "la vitrine et Sentinel ne nomment plus les mêmes risques, ou plus "
        "dans le même ordre :\n  vitrine  : %s\n  sentinel : %s"
        % (vitrine, sentinel))


def test_le_radar_enumere_EXACTEMENT_ces_huit_risques():
    """LE RADAR ANNONCE SA MÉTHODE en énumérant les huit risques. Un libellé
    changé ailleurs et pas ici laisserait la méthodologie décrire un modèle
    qui n'existe plus."""
    i = SENTINEL.index("Méthodologie : les 6 dimensions")
    methodo = SENTINEL[i:i + 700]
    for _, libelle in _declares():
        court = libelle.replace(" Techno", "")
        assert court in html.unescape(methodo), (
            "le risque « %s » est déclaré mais absent de la méthodologie "
            "affichée par le radar" % libelle)


# ══════════════════════════════════════════════════════════════════════════
#  2. LES HUIT SONT LIÉS, ET VERS HUIT ENDROITS DIFFÉRENTS
# ══════════════════════════════════════════════════════════════════════════

def test_CHACUN_des_huit_risques_porte_son_lien():
    """SEPT CARTES SUR HUIT LIÉES, C'EST UNE SECTION QUI PARAÎT LIÉE et dont
    un risque reste muet — le lecteur conclut qu'il a mal cliqué, pas que ce
    lien-là n'existe pas."""
    liens = _destinations()
    assert len(liens) == len(_cartes()), (
        "%d risque(s) sur %d portent un lien" % (len(liens), len(_cartes())))


def test_les_huit_risques_ne_menent_pas_au_MEME_ENDROIT():
    """HUIT LIENS VERS LE MÊME ÉCRAN NE CONNECTENT RIEN : c'est la bannière de
    pied d'avant, répétée huit fois.

    DEUX CARTES PEUVENT PARTAGER UNE PAGE, à une condition : qu'elles ne
    déposent pas le visiteur au même endroit. « Data & IA » ouvre le profil
    IA générative dans son ensemble — ses douze risques, dont six hors cyber,
    c'est le propos de la carte. « Supply Chain » ouvre le douzième en
    particulier. Exiger huit PAGES distinctes interdirait ce cas et pousserait
    à choisir une page voisine plutôt que la bonne, ce qui est précisément le
    défaut que ces règles existent pour empêcher. On exige donc huit ENDROITS
    distincts, et on interdit qu'une page partagée le soit sans point nommé."""
    dests = _destinations()
    assert len(set(dests)) == len(dests), (
        "deux risques déposent le visiteur au même endroit : %s"
        % sorted(_libelle(d) for d in set(dests) if dests.count(d) > 1))
    pages = _pages()
    for pg in set(pages):
        if pages.count(pg) == 1:
            continue
        points = [pt for p, pt in dests if p == pg]
        assert all(points) or sum(1 for pt in points if not pt) == 1, (
            "« %s » est visée par %d cartes dont %d sans point nommé : elles "
            "arrivent toutes en haut de la même page, et rien ne distingue ce "
            "que chacune promettait" % (pg, len(points),
                                        sum(1 for pt in points if not pt)))


def test_chaque_destination_existe_comme_PANNEAU_ET_comme_ONGLET():
    """`/sentinel?goto=xxx` SUR UN IDENTIFIANT INCONNU N'AFFICHE PAS D'ERREUR :
    Sentinel ouvre son accueil, et le visiteur croit avoir mal cliqué."""
    panneaux, onglets = _panneaux(), _onglets()
    assert len(panneaux) > 50 and len(onglets) > 50, (
        "lecture de sentinel.html : %d panneaux, %d onglets — ce contrôle ne "
        "prouve plus rien" % (len(panneaux), len(onglets)))
    for cible in _pages():
        assert cible in panneaux, "« %s » n'est pas un panneau" % cible
        assert cible in onglets, (
            "« %s » est un panneau mais aucun onglet n'y mène : le visiteur "
            "y arrive et ne saura pas y revenir" % cible)


def test_la_banniere_de_pied_vise_le_RADAR_et_plus_l_accueil():
    """ELLE OUVRAIT `/sentinel` TOUT COURT. Le radar est le seul écran qui
    porte les huit risques — sa propre méthodologie les énumère."""
    m = re.search(r'risk-cta-banner.*?<a href="([^"]+)"', BLOC, re.S)
    assert m, "la bannière de pied a disparu"
    assert m.group(1) == "/sentinel?goto=radar", (
        "la bannière ouvre %r : après huit risques nommés, l'accueil déplace "
        "la question au lieu d'y répondre" % m.group(1))


# ══════════════════════════════════════════════════════════════════════════
#  3. CHAQUE LIEN MÈNE LÀ OÙ SA CARTE LE DIT
# ══════════════════════════════════════════════════════════════════════════

# CE QUE LA CARTE DOIT DIRE POUR AVOIR LE DROIT D'OUVRIR CE MODULE. La règle
# ne juge pas la pertinence — elle vérifie que la carte NOMME le sujet vers
# lequel elle pointe. Deux d'entre eux viennent d'ailleurs de la SOURCE que
# le risque déclare lui-même dans `SYSTEMIC_RISKS` (voir la règle suivante),
# ce qui est la justification la plus forte disponible.
#  AUCUN MOT-PARAPLUIE DANS CETTE TABLE, ET C'EST UNE CORRECTION.
#
#  Quatre entrées acceptaient le mot que la carte porte DÉJÀ dans son titre :
#  « juridictionnel », « économique », « géopolitique », « supply chain ». La
#  règle passait donc sans jamais lire la description — et un mot-parapluie
#  ne distingue rien : « géopolitique » aurait tout aussi bien justifié un
#  lien vers l'observatoire R&D que vers les tensions normatives, et
#  « juridictionnel » vaut autant pour la carte mondiale que pour le
#  comparateur. Une mutation l'a montré : vider la description de la carte
#  Géopolitique de tout son vocabulaire ne faisait tomber aucune règle.
#
#  Chaque entrée ne retient donc que des mots qui NOMMENT LA DESTINATION et
#  qu'aucune autre destination du même thème ne revendiquerait. Ils se
#  trouvent dans la description de la carte, pas dans son titre.
#  LA TABLE EST CLASSÉE PAR ENDROIT, ET C'EST CE QUI PERMET LE PARTAGE.
#  « nist-genai » sans point, c'est le profil dans son ensemble — les douze
#  risques, dont six hors cyber. « nist-genai#nist-gen-12 », c'est le
#  douzième en particulier. Deux cartes, deux vocabulaires attendus, un seul
#  écran : la table le dit, au lieu de le cacher derrière un identifiant
#  commun.
NOMME = {
    "carto": ("extraterritoriales", "souveraineté"),
    "finops": ("dépenses", "tarifaire"),
    "nist-genai": ("biais", "qualité des données"),
    "training": ("compétences",),
    "geo": ("tensions", "fragmentation"),
    "owasp-dix": ("adversarial", "hallucinations", "attaque"),
    "nist-genai#nist-gen-12": ("lock-in", "interopérabilité"),
    "empreinte-ia": ("carbone", "énergivores", "empreinte"),
}


def test_chaque_carte_NOMME_le_sujet_du_module_qu_elle_ouvre():
    """LA RÈGLE QUI EMPÊCHE LE LIEN APPROXIMATIF. Un lien vers un écran
    seulement voisin du sujet apprend au lecteur à ne plus croire les liens —
    un prix bien plus élevé que celui d'une carte sans lien.
    """
    cartes = re.findall(
        r'<h3 class="risk-title" data-i18n="rk\.([a-z]+)\.t">([^<]*)</h3>\s*'
        r'<p class="risk-desc"[^>]*>([^<]*)</p>\s*'
        r'<span class="risk-tag[^"]*"[^>]*>([^<]*)</span>\s*'
        r'<a class="risk-go" href="/sentinel\?goto=([a-z0-9-]+)'
        r'(?:&amp;point=([A-Za-z0-9_-]+))?"', BLOC)
    assert len(cartes) == 8, (
        "%d carte(s) relevées avec leur lien — la lecture a changé de forme"
        % len(cartes))
    for _cle, titre, desc, tag, page, point in cartes:
        cible = _libelle((page, point))
        attendus = NOMME.get(cible)
        assert attendus, (
            "« %s » ouvre « %s », dont aucun mot n'est attendu : ajoutez-le à "
            "NOMME avec ce que la carte doit dire, ou changez de destination"
            % (titre, cible))
        texte = html.unescape(" ".join((titre, desc, tag))).lower()
        assert any(a in texte for a in attendus), (
            "la carte « %s » ouvre « %s » sans le nommer — attendu l'un de %s"
            % (titre, cible, list(attendus)))


def test_trois_destinations_viennent_de_la_SOURCE_declaree_du_risque():
    """LA JUSTIFICATION LA PLUS FORTE DISPONIBLE, ET ELLE EST DANS LES DONNÉES.

    Chaque risque de `SYSTEMIC_RISKS` déclare la source qui le fonde. Trois
    d'entre elles nomment le sujet dont Sentinel porte le module :

      supply_chain    → « NIST AI 600-1 — Value Chain and Component Integration »
      data_ia         → « NIST AI 600-1 — Harmful Bias, Data Privacy… »
      geopolitique    → « OECD.AI — tensions normatives, fragmentation… »

    CETTE PREMIÈRE LIGNE PORTAIT DEUX ERREURS, ET LE LIEN LES SUIVAIT. Elle
    disait « NIST AI RMF » pour un item qui appartient à AI 600-1 — le profil
    IA générative, où il est le risque 12 sur 12 — et l'appelait
    « Integrity » là où `nist_ai_rmf.py`, la référence du dépôt, écrit
    « Integration ». La carte ouvrait donc le CADRE, dix-neuf catégories
    repliées dont aucune ne porte ce nom, en promettant un item qui vit
    ailleurs. C'est ce qui s'est vu à l'usage sous la forme « ça ouvre le
    mauvais module ».

    Leurs liens ne relèvent donc d'aucune interprétation : ils suivent ce que
    le risque dit lui-même. Si une de ces sources changeait de sujet, le lien
    deviendrait faux — et cette règle tombe.

    LA TROISIÈME EST ARRIVÉE EN CORRIGEANT UN LIEN. « Géopolitique » ouvrait
    l'observatoire R&D — OÙ l'IA se fabrique — alors que sa source parle de
    TENSIONS NORMATIVES, c'est-à-dire du sujet de la page « Tensions &
    alliances réglementaires ». Le lien précédent n'était pas absurde : il
    était simplement fondé sur autre chose que ce que la carte déclare.
    """
    i = PAGEJS.index("var SYSTEMIC_RISKS = [")
    corps = PAGEJS[i:PAGEJS.index("];", i)]
    sources = dict(re.findall(r'\{id:"([a-z_]+)".*?source:"([^"]*)"',
                              corps, re.S))
    assert len(sources) == 8, sources
    attendu = {
        "supply_chain": ("Value Chain and Component Integration",
                         "nist-genai#nist-gen-12"),
        "data_ia":      ("NIST AI 600-1", "nist-genai"),
        "geopolitique": ("tensions normatives", "geo")}
    cartes = dict(zip([c for c, _ in _cartes()],
                      [_libelle(d) for d in _destinations()]))
    cle_vitrine = {"supply_chain": "sc", "data_ia": "data",
                   "geopolitique": "geo"}
    for rid, (cadre, cible) in attendu.items():
        assert cadre in sources[rid], (
            "le risque %s ne cite plus %s comme source : son lien vers %s "
            "n'est plus fondé sur rien" % (rid, cadre, cible))
        assert cartes[cle_vitrine[rid]] == cible, (
            "%s cite %s mais sa carte ouvre %r"
            % (rid, cadre, cartes[cle_vitrine[rid]]))


def test_l_infobulle_promet_le_nom_que_la_REFERENCE_porte():
    """UNE INTERDICTION NOMMÉE N'EST PAS UNE MESURE.

    Une première version interdisait la chaîne « Component Integrity » dans
    la vitrine et dans le script. Elle empêchait le retour de CETTE faute-là
    et d'aucune autre : renommer l'item dans `nist_ai_rmf.py` la laissait
    verte, alors que l'infobulle se mettait à promettre un intitulé que la
    page n'affiche plus. Mesuré par une mutation, ce contrôle n'a rien vu.

    La règle joint donc les deux bouts, sans rien recopier : le point visé
    par la carte donne le numéro du risque, le numéro donne l'item dans la
    référence, et l'intitulé de cet item doit se lire dans l'infobulle. Le
    jour où l'item change de nom, la carte doit changer avec lui — c'est
    l'auditeur qui ira chercher cet intitulé dans le document du NIST.
    """
    import nist_ai_rmf
    liens = re.findall(
        r'class="risk-go" href="/sentinel\?goto=([a-z0-9-]+)'
        r'(?:&amp;point=nist-gen-(\d+))?" title="([^"]*)"', BLOC)
    assert len(liens) == 8, len(liens)
    vises = [(n, html.unescape(t)) for _pg, n, t in liens if n]
    assert vises, (
        "aucune carte ne vise un risque numéroté du profil : cette règle ne "
        "prouve plus rien et il faut la retirer plutôt que la laisser verte")
    par_n = {r["n"]: r for r in nist_ai_rmf.RISQUES_GENAI}
    for n, titre in vises:
        item = par_n.get(int(n))
        assert item, (
            "la carte vise le risque %s du profil, qui n'existe pas dans la "
            "référence — elle compte %d risques" % (n, len(par_n)))
        assert item["cle"] in titre, (
            "l'infobulle promet « %s » ; la référence nomme ce risque « %s » "
            "et c'est ce que la page affichera"
            % (titre, item["cle"]))
        sources = dict(re.findall(r'\{id:"([a-z_]+)".*?source:"([^"]*)"',
                                  PAGEJS[PAGEJS.index("var SYSTEMIC_RISKS = ["):
                                         PAGEJS.index("];", PAGEJS.index(
                                             "var SYSTEMIC_RISKS = ["))], re.S))
        assert any(item["cle"] in v for v in sources.values()), (
            "aucun risque ne déclare « %s » comme source : le lien vers ce "
            "point ne repose plus sur rien" % item["cle"])


def _page_meta():
    """{identifiant: « section label »} tel que Sentinel le déclare."""
    i = PAGEJS.index("var PAGE_META = {")
    bloc = PAGEJS[i:PAGEJS.index("\n};", i)]
    return {c: (sec + " " + lab).lower() for c, sec, lab in re.findall(
        r"'?([A-Za-z0-9_-]+)'?\s*:\s*\{\s*section\s*:\s*'([^']*)'\s*,"
        r"\s*label\s*:\s*'([^']*)'", bloc)}


#  LE MOT QUE CHAQUE DESTINATION DOIT ENCORE PORTER.
#
#  Il est relevé dans PAGE_META, c'est-à-dire dans ce que SENTINEL dit de sa
#  page — pas dans une description tenue ici, qui ne vieillirait jamais parce
#  que personne ne la relirait. Une première version attendait « coût » sur
#  `finops` : la page s'intitule « CARTOGRAPHIER · FinOps IA » et la règle est
#  tombée au premier essai. C'est exactement ce qu'on lui demande de faire.
PORTE = {
    "geo":          "tensions",
    "owasp-dix":    "owasp",
    "finops":       "finops",
    "empreinte-ia": "empreinte",
    "carto":        "carte",
    "nist-genai":   "générative",
    "training":     "training",
}


def test_le_module_vise_PORTE_le_sujet_que_la_carte_annonce():
    """LA RÈGLE PRÉCÉDENTE LIE UNE SOURCE À UN IDENTIFIANT ; celle-ci vérifie
    que l'identifiant désigne encore une page qui PARLE de ce sujet.

    Sans elle, renommer `geo` en « Observatoire des modèles » laisserait le
    lien vert : la carte pointerait toujours vers `geo`, dont la source dirait
    toujours « tensions normatives », et la page ne parlerait plus de rien de
    tel. Un lien survit mal à une page qui a changé de sujet, et rien
    n'avertit quand cela arrive.
    """
    meta = _page_meta()
    assert len(meta) > 40, (
        "la lecture de PAGE_META rend %d entrées : ce contrôle ne prouve "
        "plus rien" % len(meta))
    cibles = _pages()
    assert len(cibles) == 8, cibles
    for cible in cibles:
        mot = PORTE.get(cible)
        assert mot, (
            "la carte mène à « %s », dont aucun mot n'est attendu : ajoutez-le "
            "à PORTE avec ce que la page Sentinel doit dire, ou changez de "
            "destination" % cible)
        assert cible in meta, (
            "« %s » n'a plus de fiche dans PAGE_META : le visiteur y arrive "
            "sans savoir où il est" % cible)
        assert mot in meta[cible], (
            "la carte mène à « %s », que Sentinel intitule désormais « %s » : "
            "le mot « %s » qui justifiait le lien n'y est plus — relire le "
            "lien avant de le garder" % (cible, meta[cible], mot))


def _points_rendus():
    """Les identifiants que la peinture de Sentinel produit RÉELLEMENT.

    On ne les recopie pas : on les DÉRIVE de la référence NIST du dépôt avec
    la même recette que le JavaScript, après avoir vérifié que c'est bien
    celle-là. Une liste tenue à la main ici vieillirait en silence, et cette
    règle finirait par comparer deux copies au lieu de comparer au produit.
    """
    import nist_ai_rmf
    ids = set("nist-gen-%d" % r["n"] for r in nist_ai_rmf.RISQUES_GENAI)
    ids |= set("nist-cat-" + re.sub(r"[^A-Za-z0-9]+", "-", c["cle"])
               for c in nist_ai_rmf.CATEGORIES)
    return ids


def test_la_recette_des_identifiants_est_bien_CELLE_du_JavaScript():
    """LE GARDE-FOU DE LA RÈGLE SUIVANTE. Elle dérive les identifiants
    rendus ; si le JavaScript changeait sa façon de les fabriquer, elle
    continuerait de comparer un lien à une liste que plus rien ne produit —
    verte, et sans rapport avec l'écran."""
    assert '\'<li id="nist-gen-\' + r.n + \'"' in PAGEJS, (
        "le profil IA générative ne numérote plus ses risques ainsi")
    assert '\'<details class="nist-cat" id="nist-cat-\'' in PAGEJS and \
           "c.cle.replace(/[^A-Za-z0-9]+/g, '-')" in PAGEJS, (
        "le cadre ne fabrique plus ses identifiants de catégorie ainsi")
    rendus = _points_rendus()
    assert len(rendus) == 31, (
        "%d identifiants dérivés (12 risques + 19 catégories attendus) : la "
        "référence a changé de forme" % len(rendus))


def test_chaque_POINT_visé_existe_vraiment_dans_la_page():
    """LE DÉFAUT QUE `?point=` INTRODUIT, ET QUI NE SE VOIT PAS.

    Un identifiant inconnu ne produit AUCUNE erreur : la page demandée
    s'ouvre, le pointage échoue en silence, et le visiteur se retrouve en
    haut d'une liste sans savoir ce qu'on lui avait promis. C'est exactement
    le défaut qu'on vient de corriger, sous une autre forme — un lien qui
    réussit à moitié est plus coûteux qu'un lien qui manque, parce qu'il ne
    se signale pas.

    La règle exige donc que chaque point visé soit un identifiant que la
    page FABRIQUE réellement."""
    rendus = _points_rendus()
    vises = [(pg, pt) for pg, pt in _destinations() if pt]
    assert vises, (
        "aucune carte ne vise un point précis : cette règle ne prouve plus "
        "rien et il faut la retirer plutôt que la laisser verte à vide")
    for pg, pt in vises:
        assert pt in rendus, (
            "la carte ouvre « %s » en visant « %s », que cette page ne "
            "fabrique jamais : la navigation réussira et le pointage "
            "échouera en silence" % (pg, pt))


def test_la_machinerie_du_lien_profond_existe_et_echoue_EN_SILENCE():
    """DEUX EXIGENCES OPPOSÉES, ET LES DEUX COMPTENT. Le lien profond doit
    atteindre son point — sinon la promesse de la carte est vide. Et il doit
    renoncer sans bruit sur un identifiant inconnu — sinon une faute de
    frappe casse une navigation qui, elle, a réussi."""
    assert "window.sentinelPointer" in PAGEJS, (
        "la fonction de pointage a disparu : `?point=` ne fait plus rien")
    assert "q.get('point')" in PAGEJS, (
        "le paramètre `point` n'est plus lu à l'ouverture de la page")
    i = PAGEJS.index("window.sentinelPointer")
    corps = PAGEJS[i:PAGEJS.index("window.sentinelGotoDeepLink", i)]
    assert "if(!el) return false" in corps, (
        "un identifiant inconnu ne renonce plus proprement")
    assert "catch" in corps, (
        "le pointage peut lever et emporter le reste du chargement")
    assert "d.open = true" in corps or "el.open = true" in corps, (
        "le point visé n'est plus déplié : sur une page d'accordéons fermés, "
        "l'amener à l'écran ne le montre pas")


# ══════════════════════════════════════════════════════════════════════════
#  4. LA TRADUCTION NE PEUT PAS EFFACER LE LIEN
# ══════════════════════════════════════════════════════════════════════════

def test_aucun_lien_de_risque_ne_vit_DANS_un_element_traduit():
    """`applyLang` FAIT `el.innerHTML = <traduction>` : un <a> écrit dans un
    porteur de `data-i18n` disparaît au chargement, sans erreur et sans
    trace. Ce dépôt a déjà payé ce défaut avec la mention « texte seul » de
    la carte DORA.
    """
    for m in re.finditer(r'<(h3|p|span)([^>]*data-i18n="[^"]+"[^>]*)>(.*?)</\1>',
                         BLOC, re.S):
        assert 'class="risk-go"' not in m.group(3), (
            "un lien de risque est écrit DANS un élément traduit : %s"
            % m.group(0)[:90])


def test_le_libelle_de_l_appel_est_le_MEME_que_celui_des_offres():
    """DEUX LIBELLÉS POUR LE MÊME GESTE apprennent au lecteur qu'il s'agit de
    deux gestes différents. Les huit risques réemploient la clé des six
    offres — un seul mot à traduire, une seule chose à dire."""
    assert BLOC.count('<span data-i18n="sv.go">') == 8, (
        "%d appel(s) sur 8 portent la clé traduite"
        % BLOC.count('<span data-i18n="sv.go">'))
    for lg in ("fr", "en", "de"):
        m = re.search(r"\n\s*%s:JSON\.parse\(`(.*?)`\)" % lg, INDEXJS, re.S)
        d = json.loads(m.group(1).replace("\\`", "`"))
        assert d.get("sv.go"), "sv.go absent du dictionnaire %s" % lg


# ══════════════════════════════════════════════════════════════════════════
#  5. CE QUI SE CLIQUE SE VOIT, ET SE VISE AU CLAVIER
# ══════════════════════════════════════════════════════════════════════════

def test_chaque_lien_dit_OU_il_mene_avant_le_clic():
    liens = re.findall(r'<a class="risk-go"([^>]*)>', BLOC)
    assert len(liens) == 8, len(liens)
    for attrs in liens:
        assert 'title="Ouvre ' in attrs, attrs[:90]


def test_l_appel_a_un_etat_de_focus_visible():
    """AU CLAVIER, UN LIEN SANS ÉTAT DE FOCUS EST UN LIEN QU'ON NE PEUT PAS
    SUIVRE : on ne sait jamais où l'on est."""
    assert ".risk-go:focus-visible{" in INDEX


def test_l_appel_reste_en_bas_de_carte_quelle_que_soit_la_description():
    """SANS CELA, UNE CARTE À DESCRIPTION COURTE laisserait son appel flotter
    au milieu du vide pendant que sa voisine le pose en bas — et huit cartes
    dont les appels ne s'alignent pas se lisent comme huit cartes de natures
    différentes."""
    assert ".risk-card{display:flex;flex-direction:column}" in INDEX
    assert ".risk-card .risk-tag{margin-top:auto}" in INDEX

# ══════════════════════════════════════════════════════════════════════════
#  6. LE BLOC ENTIER EST LE LIEN, PAS SEULEMENT SON PIED
# ══════════════════════════════════════════════════════════════════════════
#
# CE QUI MANQUAIT, ET QUI SE VOYAIT À L'USAGE. Chaque carte portait bien sa
# destination, mais seule l'étiquette « Ouvrir le module » la déclenchait :
# cliquer sur le titre, l'icône ou la description ne faisait rien. Une carte
# qui s'éclaire au survol sur TOUTE sa surface et ne répond que sur vingt
# pixels enseigne au visiteur qu'elle n'est pas cliquable.
#
# CE QUI EST MESURÉ ICI, ET CE QUI NE L'EST PAS. La mécanique commune aux
# deux sections — surface étirée, bloc conteneur, liste des puces — est
# gardée par tests/test_offres_services.py, où elle a été introduite. Ce
# fichier mesure ce qui n'appartient qu'aux cartes de risque : elles n'ont
# aucun lien interne, donc leur ÉTIQUETTE DE CATÉGORIE entre dans la surface
# cliquable, et c'est justement pour elle que l'enveloppement par un <a>
# avait été écarté.


def _feuille():
    """Le CSS de la page, commentaires retirés.

    SANS CE NETTOYAGE, LA RÈGLE SE MENT À ELLE-MÊME : les commentaires de
    cette feuille CITENT des règles CSS pour les expliquer, et un analyseur
    naïf recolle la prose et le code en règles qui n'existent pas."""
    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", INDEX, re.S))
    return re.sub(r"/\*.*?\*/", " ", css, flags=re.S)


def _declaration(propriete, selecteur, exact=False):
    for sel, corps in re.findall(r"([^{}@]+)\{([^{}]*)\}", _feuille()):
        sel = sel.strip()
        if not sel or (sel != selecteur if exact else selecteur not in sel):
            continue
        m = re.search(r"(?:^|;)\s*%s\s*:\s*([^;]+)" % propriete, corps)
        if m:
            return m.group(1).strip()
    return None


def test_SEUL_l_appel_redirige_et_rien_d_autre_dans_la_carte():
    """LA DEMANDE : « pour les 8 risques systémiques, seul le clic sur
    Ouvrir le module doit rediriger vers la bonne page Sentinel ».

    CE QUE LA CARTE A PORTÉ QUELQUES HEURES, ET QU'ELLE NE PORTE PLUS. Une
    surface étirée couvrait la carte entière et déclenchait l'appel de son
    pied. C'est juste pour une OFFRE — la carte est un appel, tout y pousse
    vers le même module — et faux pour un CONSTAT : « Cloud Act · lois
    extraterritoriales · sanctions » se lit pour lui-même, et le rendre
    cliquable partout transforme chaque lecture en navigation involontaire.

    ON MESURE L'ABSENCE, PAS LA PRÉSENCE, et c'est plus fragile : une règle
    qui exige qu'une chose manque passe aussi le jour où c'est TOUT le bloc
    qui a disparu. D'où le garde-fou : la déclaration du motif doit exister
    pour les cartes de service, sans quoi cette règle ne prouve plus rien.
    """
    feuille = _feuille()
    assert ".sv-card-go::after" in feuille, (
        "le motif de surface étirée a disparu de la feuille entière : cette "
        "règle ne prouve plus l'absence sur les cartes de RISQUE, elle "
        "constate une absence générale — la réécrire sur ce qui l'a remplacé")
    assert ".risk-go::after" not in feuille, (
        "les cartes de risque ont retrouvé une surface étirée : le corps de "
        "la carte redirige à nouveau, alors que seul l'appel le doit")
    assert _declaration("cursor", ".risk-card:has(.risk-go)") is None, (
        "la carte de risque annonce un clic qu'elle ne rend plus")


def test_aucun_gestionnaire_ATTRAPE_TOUT_ne_vise_les_cartes_de_risque():
    """LE DÉFAUT QUI SE CACHAIT DERRIÈRE LE CSS, ET QUI LE PRÉCÉDAIT.

    Un bloc de `index.page.js` rendait cliquables `.sector-card,
    .norm-card, .risk-card` et ouvrait « /sentinel » — l'ACCUEIL — dans un
    nouvel onglet. Sur les cartes de secteur, c'est un filet utile : onze
    sur douze n'ont aucun lien propre. Sur les cartes de risque, qui
    portent toutes leur appel vers LEUR module, il faisait deux dégâts :

      · cliquer le corps ouvrait le sommaire de Sentinel, pas le module
        que la carte venait d'annoncer ;
      · cliquer « Ouvrir le module » déclenchait LES DEUX — le lien dans
        l'onglet courant, l'accueil dans un second par-dessus.

    ET IL ÉCHAPPAIT AUX SONDES. `window.open` n'est pas une navigation de
    lien : une recette qui n'écoute que les clics sur <a> déclarait ces
    cartes « inertes » alors qu'elles ouvraient un onglet. Une sonde qui ne
    connaît qu'une sortie certifie l'absence de toutes les autres.
    """
    m = re.search(r"var selectors = '([^']*)';", INDEXJS)
    assert m, (
        "le bloc qui rend des cartes entières cliquables a changé de forme : "
        "cette règle ne surveille plus rien et doit être réécrite")
    vises = [x.strip() for x in m.group(1).split(",")]
    #  ON CHERCHE LA CLASSE N'IMPORTE OÙ DANS LA LISTE, PAS UNE ENTRÉE EXACTE.
    #  Une mutation l'a montré : `#risques .risk-card` passait la comparaison
    #  d'entrées tout en rebranchant exactement le même gestionnaire. Une
    #  garde qu'on contourne en préfixant un sélecteur ne garde rien.
    assert "risk-card" not in m.group(1), (
        "les cartes de risque sont revenues dans le gestionnaire attrape-tout "
        "(%s) : leur corps rouvrira l'accueil de Sentinel dans un nouvel "
        "onglet, et leur appel déclenchera deux sorties" % m.group(1))
    assert ".sector-card" in vises, (
        "les cartes de secteur ont quitté le filet : onze sur douze n'ont "
        "aucun lien propre et ne mèneraient plus nulle part")


def test_les_huit_cartes_de_risque_portent_TOUTES_leur_propre_appel():
    """LA CONDITION QUI REND LE RETRAIT LÉGITIME. Sortir une famille de
    cartes du filet ne se justifie que si chacune a déjà sa destination.
    Une seule carte sans appel et le retrait la rendrait muette."""
    cartes = BLOC.split('<div class="risk-card">')[1:]
    assert len(cartes) == 8, len(cartes)
    sans = [i for i, c in enumerate(cartes, 1)
            if 'class="risk-go" href="/sentinel' not in c]
    assert not sans, (
        "la ou les carte(s) %s n'ont pas d'appel propre : les sortir du "
        "gestionnaire attrape-tout les laisse sans aucune destination" % sans)


def test_l_etiquette_de_categorie_entre_dans_la_surface_sans_devenir_un_lien():
    """LA RAISON POUR LAQUELLE L'ENVELOPPEMENT PAR UN <a> AVAIT ÉTÉ ÉCARTÉ.

    Mettre la carte entière dans un <a> aurait fait de « Sécurité » ou
    « ESG » un lien : souligné au survol, annoncé comme lien par un lecteur
    d'écran, ouvrable dans un nouvel onglet — pour une étiquette qui n'est
    pas une destination mais une classification. La surface étirée obtient
    le même clic sans rien de tout cela : l'étiquette reste un <span>.

    Ce que la règle mesure, c'est l'absence d'imbrication dans la SOURCE :
    un <a> autour des cartes se verrait ici même."""
    cartes = BLOC.split('<div class="risk-card">')[1:]
    assert len(cartes) == 8, len(cartes)
    for c in cartes:
        assert re.search(r'<span class="risk-tag', c), (
            "l'étiquette de catégorie n'est plus un <span>")
        assert not re.search(r'<a[^>]*>\s*(?:(?!</a>).)*?<span class="risk-tag',
                             c, re.S), (
            "l'étiquette de catégorie est passée DANS un lien : elle "
            "s'annonce comme une destination alors qu'elle n'en est pas")


def test_le_pied_reste_un_VRAI_lien_et_pas_un_gestionnaire_de_clic():
    """UN `onclick` SUR LA CARTE AURAIT ÉTÉ PLUS COURT À ÉCRIRE, et aurait
    coûté le clavier, le clic du milieu, « ouvrir dans un nouvel onglet » et
    l'annonce par un lecteur d'écran. La surface étirée garde un <a>."""
    assert len(re.findall(r'<a class="risk-go" href="/sentinel\?goto=', BLOC)) == 8
    for interdit in ('onclick="location', "onclick='location",
                     "addEventListener('click'", "window.location"):
        assert interdit not in BLOC, (
            "la carte navigue par script plutôt que par lien : %r" % interdit)


def test_la_carte_de_risque_n_annonce_PAS_un_clic_qu_elle_ne_rend_pas():
    """UN CURSEUR EN MAIN SUR UNE ZONE INERTE EST PIRE QUE PAS DE CURSEUR :
    il promet, on clique, rien ne se passe, et le visiteur conclut que le
    site est cassé plutôt que de chercher le vrai appel.

    LE CURSEUR ÉTAIT POSÉ PAR UN SCRIPT, PAS PAR LA FEUILLE — `card.style
    .cursor = 'pointer'` en style en ligne. Une règle qui n'aurait lu que le
    CSS aurait certifié l'absence ; c'est le navigateur qui l'a dit.
    """
    assert _declaration("cursor", ".risk-card:has(.risk-go)") is None
    m = re.search(r"var selectors = '([^']*)';", INDEXJS)
    assert m and ".risk-card" not in m.group(1), (
        "le script repose un curseur de lien sur la carte entière")
    #  L'APPEL, LUI, DOIT TOUJOURS LE MONTRER.
    assert ".risk-go{" in _feuille() or ".risk-go:hover" in _feuille(), (
        "l'appel n'a plus de style propre : rien ne le distingue du texte")
