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
LIENS = re.compile(r'class="risk-go" href="/sentinel\?goto=([a-z0-9-]+)"')


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
    liens = LIENS.findall(BLOC)
    assert len(liens) == len(_cartes()), (
        "%d risque(s) sur %d portent un lien" % (len(liens), len(_cartes())))


def test_les_huit_risques_ne_menent_pas_tous_au_MEME_module():
    """HUIT LIENS VERS LE MÊME ÉCRAN NE CONNECTENT RIEN : c'est la bannière de
    pied d'avant, répétée huit fois."""
    liens = LIENS.findall(BLOC)
    assert len(set(liens)) == len(liens), (
        "deux risques mènent au même module : %s"
        % sorted(c for c in set(liens) if liens.count(c) > 1))


def test_chaque_destination_existe_comme_PANNEAU_ET_comme_ONGLET():
    """`/sentinel?goto=xxx` SUR UN IDENTIFIANT INCONNU N'AFFICHE PAS D'ERREUR :
    Sentinel ouvre son accueil, et le visiteur croit avoir mal cliqué."""
    panneaux, onglets = _panneaux(), _onglets()
    assert len(panneaux) > 50 and len(onglets) > 50, (
        "lecture de sentinel.html : %d panneaux, %d onglets — ce contrôle ne "
        "prouve plus rien" % (len(panneaux), len(onglets)))
    for cible in LIENS.findall(BLOC):
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
NOMME = {
    "carto": ("juridictionnel", "extraterritoriales", "souveraineté"),
    "finops": ("dépenses", "tarifaire", "économique"),
    "nist-genai": ("biais", "qualité des données"),
    "training": ("compétences",),
    "obs-rd": ("géopolitique", "export", "technologiques"),
    "owasp-dix": ("adversarial", "hallucinations", "attaque"),
    "nist-cadre": ("supply chain", "lock-in", "interopérabilité"),
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
        r'<a class="risk-go" href="/sentinel\?goto=([a-z0-9-]+)"', BLOC)
    assert len(cartes) == 8, (
        "%d carte(s) relevées avec leur lien — la lecture a changé de forme"
        % len(cartes))
    for _cle, titre, desc, tag, cible in cartes:
        attendus = NOMME.get(cible)
        assert attendus, (
            "« %s » ouvre « %s », dont aucun mot n'est attendu : ajoutez-le à "
            "NOMME avec ce que la carte doit dire, ou changez de destination"
            % (titre, cible))
        texte = html.unescape(" ".join((titre, desc, tag))).lower()
        assert any(a in texte for a in attendus), (
            "la carte « %s » ouvre « %s » sans le nommer — attendu l'un de %s"
            % (titre, cible, list(attendus)))


def test_deux_destinations_viennent_de_la_SOURCE_declaree_du_risque():
    """LA JUSTIFICATION LA PLUS FORTE DISPONIBLE, ET ELLE EST DANS LES DONNÉES.

    Chaque risque de `SYSTEMIC_RISKS` déclare la source qui le fonde. Deux
    d'entre elles nomment un cadre dont Sentinel porte le module :

      supply_chain    → « NIST AI RMF — Value Chain and Component Integrity »
      data_ia         → « NIST AI 600-1 — Harmful Bias, Data Privacy… »

    Leurs liens ne relèvent donc d'aucune interprétation : ils suivent ce que
    le risque dit lui-même. Si une de ces sources changeait de cadre, le lien
    deviendrait faux — et cette règle tombe.
    """
    i = PAGEJS.index("var SYSTEMIC_RISKS = [")
    corps = PAGEJS[i:PAGEJS.index("];", i)]
    sources = dict(re.findall(r'\{id:"([a-z_]+)".*?source:"([^"]*)"',
                              corps, re.S))
    assert len(sources) == 8, sources
    attendu = {"supply_chain": ("NIST AI RMF", "nist-cadre"),
               "data_ia": ("NIST AI 600-1", "nist-genai")}
    cartes = dict(zip([c for c, _ in _cartes()], LIENS.findall(BLOC)))
    cle_vitrine = {"supply_chain": "sc", "data_ia": "data"}
    for rid, (cadre, cible) in attendu.items():
        assert cadre in sources[rid], (
            "le risque %s ne cite plus %s comme source : son lien vers %s "
            "n'est plus fondé sur rien" % (rid, cadre, cible))
        assert cartes[cle_vitrine[rid]] == cible, (
            "%s cite %s mais sa carte ouvre %r"
            % (rid, cadre, cartes[cle_vitrine[rid]]))


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


def test_la_surface_etiree_couvre_la_carte_de_risque_entiere():
    """LA CARTE EST LE REPÈRE, LE PIED NE DOIT PAS L'ÊTRE.

    `inset:0` se résout contre le plus proche ancêtre POSITIONNÉ. Une règle
    décorative écrite deux mille lignes plus bas — `.risk-card > *
    {position:relative;z-index:1}`, posée pour faire passer le contenu
    au-dessus du halo `::before` — positionne déjà le pied. La surface
    mesurait alors la taille de l'étiquette, pas celle de la carte. On
    mesure donc les deux faits qui décident."""
    assert _declaration("position", ".risk-card", exact=False) is not None
    assert ".diff-card,.risk-card{position:relative}" in _feuille(), (
        "la carte n'est plus le repère de position : la surface étirée se "
        "cale sur un ancêtre quelconque")
    assert _declaration(
        "position", ".diff-card > .sv-card-go,.risk-card > .risk-go",
        exact=True) == "static", (
        "le pied de carte reste positionné : il devient son propre bloc "
        "conteneur et la surface ne couvre que l'étiquette")
    assert _declaration("inset", ".risk-go::after") == "0", (
        "la surface étirée ne se cale plus sur les quatre côtés")


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


def test_la_carte_cliquable_le_dit_par_son_curseur():
    """RIEN NE SIGNALE UNE ZONE CLIQUABLE COMME LE CURSEUR. Une carte qui se
    clique sans le montrer ne sera cliquée que par accident — et le `:has`
    ne vise QUE celles qui portent un pied, jamais une carte sans
    destination."""
    assert _declaration("cursor", ".risk-card:has(.risk-go)") == "pointer", (
        "la carte de risque ne montre pas qu'elle se clique")
    assert ":has(.risk-go)" in _feuille(), (
        "le curseur est posé sur toutes les cartes, y compris celles qui ne "
        "mèneraient nulle part")
