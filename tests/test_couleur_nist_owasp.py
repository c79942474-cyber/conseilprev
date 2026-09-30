# -*- coding: utf-8 -*-
"""LA COULEUR DES ÉCRANS NIST ET OWASP — ET LE DÉFAUT QU'ELLE A DÉBUSQUÉ.

CE QUI A ÉTÉ MESURÉ AVANT D'ÉCRIRE UNE SEULE COULEUR. Trente-six règles de
ces écrans lisaient `var(--line)`, `var(--panel)`, `var(--acc)`, `var(--gd)`
ou `var(--warn)` — cinq variables DÉCLARÉES NULLE PART. Ce n'est pas une
question de goût : `border:1px solid var(--line)` est un raccourci INVALIDE
quand la variable est vide, et les trois composantes retombent sur leur
valeur initiale — donc `border-style:none`. Relevé dans le navigateur, sur
la page réelle :

    .nist-cats li → fond transparent, bordure « none »
    .ow-liste li  → fond transparent, bordure « none »

Dix-neuf catégories, douze risques et dix lignes OWASP flottaient sur le
fond de page, sans surface ni réglure. Les replis écrits ailleurs disent
d'où vient le défaut : `#2a2a2a`, `#6ea8fe` — ces blocs ont été écrits pour
un thème SOMBRE et posés sur une page claire.

CE QUE CES RÈGLES GARDENT :
  1. aucune variable lue sans repli n'est indéfinie — la porte du défaut ;
  2. chaque état que les MOTEURS connaissent a sa couleur — ajouter un état
     sans sa nuance le rendrait invisible sur l'écran ;
  3. la teinte vient du référentiel, et toute page qui s'en sert la déclare.
"""
import io
import os
import re

import pytest

import nist_ai_rmf
import nist_genai
import owasp_llm

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def _sans_commentaires(src):
    r"""La source DÉBARRASSÉE de ses commentaires.

    MESURÉ PAR LA BATTERIE DE MUTATIONS, ET C'EST ELLE QUI L'A TROUVÉ :
    commenter `--line:#E1DFE7;` en `/* --line:#E1DFE7; */` ne faisait
    tomber aucune règle. Elles cherchaient `--line\s*:` dans le fichier
    entier — et le trouvaient dans le commentaire. Une déclaration commentée
    ne déclare rien, et c'est justement la façon dont on retire une ligne
    sans la supprimer.
    """
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", "", src)


HTML = _sans_commentaires(
    io.open(os.path.join(_RACINE, "sentinel.html"), encoding="utf-8").read())
JS = _sans_commentaires(
    io.open(os.path.join(_RACINE, "sentinel.page.js"), encoding="utf-8").read())

#: Les cinq jetons qui manquaient. Le nombre est ici pour que la règle tombe
#: si l'un d'eux disparaît sans que personne ne s'en aperçoive.
JETONS_RETROUVES = ("--line", "--panel", "--acc", "--gd", "--warn")


def _declarees(src):
    """Toutes les variables CSS déclarées, où qu'elles le soient."""
    return {m.group(1) for m in re.finditer(r"(--[A-Za-z0-9-]+)\s*:", src)}


def _lues_sans_repli(src):
    """Celles qui sont LUES sans valeur de secours — les seules qui peuvent
    casser une propriété entière."""
    return {m.group(1) for m in re.finditer(r"var\(\s*(--[A-Za-z0-9-]+)\s*\)", src)}


# ══════════════════════════════════════════════════════════════════════════
#  1. LA PORTE DU DÉFAUT
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("jeton", JETONS_RETROUVES)
def test_le_jeton_qui_manquait_est_DECLARE(jeton):
    """LES CINQ QUI N'EXISTAIENT PAS. Chacun était lu par des règles
    d'écran ; aucun n'était déclaré."""
    assert jeton in _declarees(HTML), (
        "%s est lu par les écrans et n'est déclaré nulle part : toute "
        "propriété qui le lit sans repli retombe sur sa valeur initiale"
        % jeton)


def test_AUCUNE_variable_lue_sans_repli_n_est_indefinie():
    """LA GARDE GÉNÉRALE, et celle qui vaut pour les écrans à venir. Une
    variable lue sans repli et jamais déclarée ne rend pas une couleur
    fausse : elle INVALIDE la propriété entière. Un `border` disparaît, un
    `background` devient transparent, et personne ne voit d'erreur."""
    manquantes = sorted(_lues_sans_repli(HTML) - _declarees(HTML))
    assert not manquantes, (
        "lues sans repli et jamais déclarées : %s" % manquantes)


def test_les_replis_de_THEME_SOMBRE_ne_commandent_plus_la_page_claire():
    """LA TRACE DU DÉFAUT, ET SA CORRECTION. Quinze règles portent encore
    `var(--line,#2a2a2a)` — une réglure presque noire, écrite pour un fond
    sombre. Le repli ne s'applique plus, puisque la variable existe
    désormais ; la règle vérifie qu'elle existe ET qu'elle est claire, sans
    quoi la page reprendrait cette réglure de deuil."""
    m = re.search(r"--line\s*:\s*([^;]+);", HTML)
    assert m, "--line n'est plus déclarée"
    valeur = m.group(1).strip().lower()
    assert valeur != "#2a2a2a", (
        "--line reprend le repli du thème sombre : sur cette page claire, "
        "une réglure presque noire sur chaque carte")
    #  claire = les trois composantes au-dessus de 0x80
    rgb = re.fullmatch(r"#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})", valeur)
    assert rgb and all(int(x, 16) > 0x80 for x in rgb.groups()), valeur


# ══════════════════════════════════════════════════════════════════════════
#  2. CHAQUE ÉTAT QUE LE MOTEUR CONNAÎT A SA COULEUR
# ══════════════════════════════════════════════════════════════════════════

ECHELLES = {
    "nist_ai_rmf": (".nist-cats li", sorted(nist_ai_rmf.ETATS)),
    "owasp_llm": (".ow-liste li", sorted(owasp_llm.ETATS)),
    "nist_genai": (".gen-act li", sorted(nist_genai.ETATS_ACTION)),
}


@pytest.mark.parametrize("moteur", sorted(ECHELLES))
def test_chaque_etat_du_MOTEUR_porte_sa_couleur_a_l_ecran(moteur):
    """LE COUPLAGE QUI COMPTE. Ajouter un état à un moteur sans lui donner
    sa nuance le rendrait INVISIBLE sur l'écran — la ligne garderait le
    pointillé de « pas encore répondu », et le client lirait « je n'ai pas
    répondu » là où il a répondu."""
    ligne, etats = ECHELLES[moteur]
    for e in etats:
        motif = re.escape(ligne) + r'\[data-etat="' + re.escape(e) + r'"\]'
        assert re.search(motif, HTML), (
            "%s : l'état « %s » du moteur n'a aucune couleur déclarée pour "
            "%s" % (moteur, e, ligne))


def test_SANS_OBJET_sort_de_l_echelle_et_ne_prend_PAS_la_teinte():
    """CE N'EST PAS UN NIVEAU, C'EST UN REFUS D'ÉCHELLE. Peint dans une
    nuance de la teinte, « sans objet » se lirait « un peu tenu » — et c'est
    exactement l'inverse : la catégorie ne s'applique pas."""
    bloc = re.search(
        r'\.nist-cats li\[data-etat="sans_objet"\][^}]*\{([^}]*)\}', HTML)
    assert bloc, "la règle du « sans objet » a disparu"
    corps = bloc.group(1)
    assert "var(--ref)" not in corps, (
        "« sans objet » prend la teinte du référentiel : il se lirait comme "
        "un niveau de l'échelle")
    assert "dashed" in corps, (
        "« sans objet » n'a plus sa forme propre : la couleur seule ne le "
        "distinguerait pas pour qui ne la voit pas")


def test_PAS_ENCORE_REPONDU_ne_se_confond_pas_avec_ABSENT():
    """DEUX CHOSES DIFFÉRENTES, ET LA NUANCE DÉCIDE D'UN CHANTIER. « Pas
    encore regardé » n'est pas « regardé, et il n'y a rien ». Le pointillé
    dit le premier, le trait plein le second."""
    base = re.search(
        r"\.nist-cats li,\.ow-liste li,\.gen-act li\{([^}]*)\}", HTML)
    assert base and "dotted" in base.group(1), (
        "la ligne sans réponse n'a plus son pointillé")
    plein = re.search(
        r"\.nist-cats li\[data-etat\],[^{]*\{([^}]*)\}", HTML)
    assert plein and "solid" in plein.group(1), (
        "une ligne répondue ne passe plus au trait plein")


# ══════════════════════════════════════════════════════════════════════════
#  3. LA TEINTE VIENT DU RÉFÉRENTIEL, ET SA PAGE LA DÉCLARE
# ══════════════════════════════════════════════════════════════════════════

def test_les_deux_referentiels_ont_des_teintes_DISTINCTES():
    """AVANT, LES DEUX ÉCRANS ÉTAIENT RIGOUREUSEMENT GRIS — donc
    indiscernables. La teinte est reprise de la pastille du tiroir dans la
    barre : le lecteur sait d'où il vient sans lire le fil d'Ariane."""
    teintes = dict(re.findall(r"#p-(nist-profil|owasp-dix)[^{]*\{--ref:\s*([^;}]+)",
                              HTML))
    assert len(teintes) == 2, teintes
    assert teintes["nist-profil"].strip() != teintes["owasp-dix"].strip()
    #  ET CE SONT CELLES DE LA BARRE : deux codes pour un seul référentiel
    #  feraient deux couleurs pour la même chose.
    for grp, ref in (("nist-ai-rmf", "nist-profil"), ("owasp-llm", "owasp-dix")):
        m = re.search(r'\[data-grp="%s"\]\{--sb-ic:(#[0-9A-Fa-f]{6})\}' % grp, HTML)
        assert m, grp
        r, v, b = (int(m.group(1)[i:i + 2], 16) for i in (1, 3, 5))
        assert teintes[ref].strip() == "%d %d %d" % (r, v, b), (
            "%s : la page (%s) ne reprend pas la pastille du tiroir (%s)"
            % (grp, teintes[ref], m.group(1)))


def test_les_CINQ_ecrans_teintes_declarent_tous_la_teinte():
    """LE MÊME DÉFAUT, UN CRAN PLUS HAUT. Un écran qui lirait `--ref` sans
    la déclarer perdrait silencieusement toute sa couleur — et ses bordures
    avec, puisque `rgb(var(--ref) / .5)` invalide la propriété entière,
    exactement comme `var(--line)` vide effaçait les bordures.

    LA LISTE DE CINQ EST LE CONTRAT, et c'est pour cela qu'elle est écrite
    en toutes lettres : un sixième écran qui reprendrait ces classes doit
    passer par ici. Que la teinte ATTEIGNE vraiment la page se mesure dans
    le navigateur — `recette_couleur_nist_owasp.js` lit la couleur calculée
    sur les cinq écrans, ce qu'aucune lecture de feuille de style ne peut
    faire."""
    #  LA LISTE DE SÉLECTEURS SE LIT EN ENTIER, PAS SEULEMENT SON PREMIER
    #  TERME. Une première version s'arrêtait au premier `#p-…` de chaque
    #  règle, et ne voyait donc que deux pages sur cinq — la règle mesurait
    #  la forme de ma propre expression, pas la feuille de style.
    #  ON DÉCOUPE, ON NE RÉGEXE PAS. Une expression à deux quantificateurs
    #  imbriqués (`[^}]*…[^}]*`) sur 600 Ko de HTML part en retour arrière
    #  exponentiel : la règle ne tombait pas, elle ne RENDAIT PAS LA MAIN.
    #  Le découpage sur `}` fait le même travail en temps linéaire.
    def _pages_du_bloc(bloc):
        return set(re.findall(r"#p-([a-z0-9-]+)", bloc))

    pages, lisent = set(), set()
    for morceau in HTML.split("}"):
        if "{" not in morceau:
            continue
        selecteur, corps = morceau.rsplit("{", 1)
        if "--ref:" in corps.replace(" ", ""):
            pages |= _pages_du_bloc(selecteur)
        if "var(--ref)" in corps:
            lisent |= _pages_du_bloc(selecteur)
    assert lisent <= pages, (
        "ces pages lisent --ref sans la déclarer : %s" % sorted(lisent - pages))
    attendues = {"nist-profil", "nist-cadre", "nist-genai",
                 "owasp-dix", "owasp-pont"}
    assert pages >= attendues, (
        "ces écrans portent les classes teintées et ne déclarent pas --ref : "
        "%s" % sorted(attendues - pages))


def test_l_AMBRE_ne_sert_QU_A_une_reserve():
    """UNE COULEUR, UN SENS. L'ambre dit le plafond du profil, les risques
    que la cyber ne tient pas, et ceux qu'aucune mesure de l'annexe A ne
    couvre. Trois avertissements, un seul code à apprendre — s'il servait
    aussi de niveau, le lecteur en apprendrait deux."""
    #  ON LIT LA DERNIÈRE OCCURRENCE, PAS LA PREMIÈRE. `.ow-pont tr.ow-non
    #  td:first-child` est déclaré deux fois dans le fichier ; à spécificité
    #  égale c'est la seconde qui peint, et une règle qui lirait la première
    #  validerait une couleur que personne ne voit — le défaut même que la
    #  recette a trouvé sur trois règles.
    for sel in (r"\.q-am\{", r"\.ow-pont tr\.ow-non td:first-child\{"):
        corps = re.findall(sel + r"([^}]*)", HTML)
        assert corps, sel
        assert "--warn" in corps[-1] or "--hors" in corps[-1], (
            "%s : la DERNIÈRE déclaration, celle qui peint, ne porte pas "
            "l'ambre — %r" % (sel, corps[-1][:60]))
    #  et l'ambre n'est JAMAIS une marche de l'échelle
    for e in ("absent", "amorce", "tenu", "prouve", "non", "partiel", "oui"):
        bloc = re.search(r'li\[data-etat="%s"\][^}]*\{([^}]*)\}' % e, HTML)
        if bloc:
            assert "--warn" not in bloc.group(1) and "--hors" not in bloc.group(1), e


def test_le_CYBER_et_le_HORS_CYBER_sont_deux_ESPECES_pas_deux_niveaux():
    """SIX DES DOUZE RISQUES NE RELÈVENT PAS DE LA CYBER, et c'est le fait
    le plus utile de cet écran. Deux espèces se distinguent par la TEINTE,
    pas par la densité d'une seule — une nuance plus claire dirait « moins
    cyber », ce qui ne veut rien dire."""
    assert re.search(r"\.gen-n\{[^}]*var\(--cy\)", HTML)
    assert re.search(r"\.nist-gen li\.gen-non \.gen-n\{[^}]*var\(--hors\)", HTML)
    cy = re.search(r"--cy:\s*([^;}]+)", HTML)
    hors = re.search(r"--hors:\s*([^;}]+)", HTML)
    assert cy and hors and cy.group(1).strip() != hors.group(1).strip()
    #  LE MOTEUR DÉCIDE QUI EST CYBER, PAS L'ÉCRAN : six sur douze.
    assert len([r for r in nist_ai_rmf.RISQUES_GENAI if not r["cyber"]]) == 6


# ══════════════════════════════════════════════════════════════════════════
#  4. LA COULEUR NE PORTE JAMAIS SEULE
# ══════════════════════════════════════════════════════════════════════════

def test_l_etat_repondu_atteint_le_DOM_pour_que_la_feuille_de_style_le_voie():
    """LA VALEUR D'UN <select> NE SE SÉLECTIONNE PAS EN CSS. Sans la
    recopie en `data-etat`, la feuille de style n'a rien à peindre — et
    c'est le genre de branchement qu'on croit fait parce qu'on a écrit la
    couleur."""
    assert "function _marquerEtat(sel)" in JS
    for f in ("window.nistRepondre", "window.owaspRepondre", "window.genaiAction"):
        bloc = JS.split(f, 1)[1].split("};", 1)[0]
        assert "_marquerEtat(sel)" in bloc, (
            "%s ne marque pas l'état : la ligne gardera la couleur de la "
            "réponse précédente" % f)
    #  ET LE LOT AUSSI : il répond pour toute une sous-catégorie.
    lot = JS.split("window.genaiLot", 1)[1].split("};", 1)[0]
    assert "_marquerEtat(s)" in lot


def test_chaque_ligne_colorée_porte_AUSSI_son_etat_en_toutes_lettres():
    """ON DOIT POUVOIR LIRE CES ÉCRANS EN NIVEAUX DE GRIS. Le champ de
    réponse reste un <select> dont l'option sélectionnée NOMME l'état —
    « Tenu », « Prouvé », « Sans objet ». La couleur redit ce que le mot
    dit déjà ; elle ne le remplace pas."""
    assert 'nistEsc(etats[k].nom)' in JS, (
        "le champ n'affiche plus le nom de l'état")
    assert '<select class="q-sel"' in JS
    #  et chaque moteur NOMME ses états, ce que l'écran recopie
    for mod, table in ((nist_ai_rmf, nist_ai_rmf.ETATS),
                       (owasp_llm, owasp_llm.ETATS),
                       (nist_genai, nist_genai.ETATS_ACTION)):
        for cle, e in table.items():
            assert e.get("nom"), "%s : l'état %s n'a pas de nom" % (mod.__name__, cle)
