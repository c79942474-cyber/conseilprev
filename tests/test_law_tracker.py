# -*- coding: utf-8 -*-
"""Le bandeau du suivi législatif européen, sur la page Réglementations.

POURQUOI IL EXISTE. La page « Réglementations » part du Règlement (UE)
2024/1689 — c'est-à-dire d'un texte ADOPTÉ. Ce qui est encore en procédure n'y
figure nulle part, et c'est exactement l'angle mort qu'un suivi législatif
comble. Le bandeau est donc EN TÊTE : le placer en bas reviendrait à le
proposer à qui a déjà fini de lire.

CE QUE CES RÈGLES REFUSENT DE LAISSER PASSER. Ce module n'a pas pu joindre
law-tracker.europa.eu — le proxy de sortie le bloque — et ne peut donc pas
vérifier ce que le site annonce de lui-même. Le bandeau ne dit par conséquent
que ce qui est vérifiable : le nom de l'outil et son domaine. Une règle
interdit d'y ajouter une description de périmètre, parce que décrire un
service sur la foi de son nom, dans une page dont tout le propos est de
renvoyer aux textes officiels, serait exactement la faute que cette page
combat.

LE CONTRASTE EST CALCULÉ, PAS CONSTATÉ. Un bandeau en tête de page qui ne se
lit pas ne sert à rien, et « une couleur est déclarée » ne mesure pas qu'elle
se voit.
"""
import io
import os
import re

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = "https://law-tracker.europa.eu/homepage?lang=fr"


@pytest.fixture(scope="module")
def page():
    return io.open(os.path.join(ICI, "sentinel.html"), encoding="utf-8").read()


def _bloc(page, ancre, taille=2200):
    i = page.index(ancre)
    return page[i:i + taille]


# ── 1. IL EST LÀ, ET IL EST EN TÊTE ────────────────────────────────────────

def test_le_bandeau_est_sur_la_page_reglementations():
    """Pas ailleurs : c'est la page des textes, c'est là que le manque se voit."""
    p = io.open(os.path.join(ICI, "sentinel.html"), encoding="utf-8").read()
    assert p.count(URL) == 1, (
        "le lien figure %d fois ; une seule est voulue" % p.count(URL))
    debut = p.index('id="p-regs"')
    fin = p.index('<div class="page" id="p-', debut + 10)
    assert debut < p.index(URL) < fin, (
        "le bandeau n'est pas dans le panneau des Réglementations")


def test_le_bandeau_precede_la_veille_et_les_onglets():
    """EN HAUT veut dire AVANT ce qui prend l'écran.

    Mesuré par les positions, pas par une impression : placé après la veille
    et les onglets, il serait sous la ligne de flottaison sur la plupart des
    écrans — et le demandeur a dit « en haut ».
    """
    p = io.open(os.path.join(ICI, "sentinel.html"), encoding="utf-8").read()
    debut = p.index('id="p-regs"')
    lien = p.index(URL)
    veille = p.index('id="veille-regs"', debut)
    onglets = p.index('class="regs-tabbar"', debut)
    assert lien < veille, "le bandeau passe après le bloc de veille"
    assert lien < onglets, "le bandeau passe après la barre d'onglets"


def test_le_lien_s_ouvre_ailleurs_sans_donner_la_main_a_la_cible(page):
    """`target="_blank"` sans `rel` laisse la page ouverte manipuler celle-ci.

    Ce n'est pas une précaution de principe ici : la page d'où l'on part porte
    une session d'administration.
    """
    bloc = _bloc(page, 'class="lawtrack"')
    assert 'target="_blank"' in bloc, bloc[:300]
    assert "noopener" in bloc, bloc[:300]
    assert "noreferrer" in bloc, bloc[:300]


# ── 2. IL NE DIT QUE CE QU'ON A PU VÉRIFIER ────────────────────────────────

def test_le_bandeau_nomme_l_outil_et_son_domaine(page):
    """Les deux seules choses vérifiables sans joindre le site."""
    bloc = _bloc(page, 'class="lawtrack"')
    assert "EU Law Tracker" in bloc, bloc[:400]
    assert "law-tracker.europa.eu" in bloc, bloc[:400]


def test_le_bandeau_n_affirme_rien_du_contenu_du_site(page):
    """LA RÈGLE QUI TIENT L'HONNÊTETÉ DE CE BANDEAU.

    Le site n'a pas pu être joint. Lui prêter un éditeur, un périmètre ou une
    exhaustivité serait une affirmation invérifiable — dans une page dont tout
    le propos est de renvoyer aux textes officiels. Ces formulations sont donc
    interdites ici tant que personne n'est allé voir.
    """
    bloc = _bloc(page, 'class="lawtrack"')
    interdits = [
        "publié par", "édité par", "Commission européenne", "Parlement européen",
        "officiel de l", "toutes les procédures", "l'ensemble des textes",
        "exhaustif", "mis à jour quotidiennement", "en temps réel",
    ]
    trouves = [x for x in interdits if x.lower() in bloc.lower()]
    assert not trouves, (
        "le bandeau affirme ce qui n'a pas pu être vérifié : %r" % trouves)


def test_le_bandeau_dit_pourquoi_il_est_la(page):
    """Un lien nu se lit comme une publicité. Celui-ci dit ce qu'il comble :
    cette page traite d'un texte ADOPTÉ, le reste est en procédure."""
    bloc = _bloc(page, 'class="lawtrack"')
    assert "2024/1689" in bloc, bloc[:600]
    assert "procédure" in bloc, bloc[:600]


# ── 3. IL SE VOIT ET IL SE LIT — MESURÉ ────────────────────────────────────

def _lum(hexa):
    h = hexa.lstrip("#")
    def c(i):
        v = int(h[i:i + 2], 16) / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return .2126 * c(0) + .7152 * c(2) + .0722 * c(4)


def _contraste(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def _composer(rgb, alpha, fond):
    f = fond.lstrip("#")
    return "#%02X%02X%02X" % tuple(
        int(round(rgb[k] * alpha + int(f[k * 2:k * 2 + 2], 16) * (1 - alpha)))
        for k in (0, 1, 2))


def _token(page, nom):
    m = re.search(r"--%s\s*:\s*(#[0-9A-Fa-f]{6})" % re.escape(nom), page)
    assert m, "le jeton --%s n'est plus déclaré" % nom
    return m.group(1)


def _regles_bandeau(page):
    """Chaque règle CSS `.lawtrack…` du fichier, en {sélecteur: corps}."""
    out = {}
    for m in re.finditer(r"(\.lawtrack[\w-]*(?::[\w-]+)?)\{([^}]*)\}", page):
        out.setdefault(m.group(1), m.group(2))
    assert out, "plus aucune règle .lawtrack dans la feuille"
    return out


def _resoudre(page, valeur):
    """Une couleur CSS → « #RRGGBB ». `var(--x)` est suivi jusqu'au jeton."""
    valeur = valeur.strip()
    m = re.match(r"var\(\s*--([\w-]+)\s*\)", valeur)
    if m:
        return _token(page, m.group(1))
    m = re.match(r"#([0-9A-Fa-f]{3})$", valeur)
    if m:
        return "#" + "".join(c * 2 for c in m.group(1))
    m = re.match(r"#([0-9A-Fa-f]{6})$", valeur)
    if m:
        return "#" + m.group(1).upper()
    m = re.match(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", valeur)
    if m:
        return "#%02X%02X%02X" % tuple(int(m.group(i)) for i in (1, 2, 3))
    raise AssertionError("couleur illisible : %r" % valeur)


def _fond_compose(page):
    """Le fond RÉEL du bandeau : son voile composé sur le blanc de la page."""
    corps = _regles_bandeau(page)[".lawtrack"]
    m = re.search(r"background:\s*rgba\((\d+),\s*(\d+),\s*(\d+),\s*"
                  r"(\.\d+|\d?\.\d+)\)", corps)
    assert m, "le fond du bandeau n'est plus un voile lisible : %r" % corps
    rgb = tuple(int(m.group(i)) for i in (1, 2, 3))
    return _composer(rgb, float(m.group(4)), "#FFFFFF")


def test_le_bandeau_se_lit_sur_son_propre_fond(page):
    """TOUTES les encres du bandeau tiennent l'AA sur SON fond composé.

    ELLE LIT LES COULEURS DÉCLARÉES, ELLE NE LES NOMME PLUS. La version
    d'origine mesurait `--ink`, `--muted` et `--accent` — les trois encres du
    jour. Le bandeau est passé au bleu et au vert, et la règle est restée
    VERTE en mesurant `--accent`, une couleur qu'il n'emploie plus nulle part.
    Une règle qui passe pour une raison sans rapport avec ce qu'elle prétend
    est pire que pas de règle : elle rassure.

    Elle relève donc les `color:` effectivement posées sur `.lawtrack*` — quel
    que soit leur nom — et les mesure une par une.
    """
    fond = _fond_compose(page)
    encres = {}
    for sel, corps in _regles_bandeau(page).items():
        # UNE ENCRE SE MESURE SUR LA SURFACE QUI EST DERRIÈRE ELLE. Un
        # sélecteur qui pose SON PROPRE fond — la pastille pleine — ne se lit
        # pas sur le voile du bandeau : le compter ici accusait le blanc de la
        # pastille de tenir 1,11:1, ce qui est vrai et hors sujet. Il a sa
        # propre règle, juste en dessous.
        if re.search(r"(?<![-\w])background(-color)?:", corps):
            continue
        for m in re.finditer(r"(?<![-\w])color:\s*([^;}]+)", corps):
            val = m.group(1).strip()
            if val.startswith("#") or val.startswith("var(") or val.startswith("rgb"):
                encres[sel] = _resoudre(page, val)
    assert len(encres) >= 4, (
        "seules %d encres relevées : la règle ne couvre plus le bandeau — %r"
        % (len(encres), encres))
    faibles = {s: (c, round(_contraste(c, fond), 2))
               for s, c in encres.items() if _contraste(c, fond) < 4.5}
    assert not faibles, (
        "ces encres ne tiennent pas l'AA sur le fond %s : %r" % (fond, faibles))


def test_la_pastille_pleine_porte_un_texte_lisible(page):
    """Blanc sur fond plein : l'inverse du reste, donc mesuré à part.

    ELLE AUSSI LISAIT UN NOM. Elle exigeait `background: var(--accent)` et
    n'a plus rien trouvé le jour où la pastille est passée au bleu — c'est
    elle qui a signalé le changement, ce qui est le bon comportement, mais
    elle aurait tout aussi bien pu rester muette sur une pastille illisible
    si la nouvelle couleur avait gardé le nom. Elle suit maintenant la
    couleur posée.
    """
    corps = _regles_bandeau(page)[".lawtrack-tag"]
    m = re.search(r"background:\s*([^;}]+)", corps)
    assert m, "la pastille n'a plus de fond : %r" % corps
    fond = _resoudre(page, m.group(1))
    m = re.search(r"(?<![-\w])color:\s*([^;}]+)", corps)
    assert m, "la pastille n'a plus d'encre : %r" % corps
    encre = _resoudre(page, m.group(1))
    c = _contraste(encre, fond)
    assert c >= 4.5, "la pastille tient %.2f:1 (%s sur %s)" % (c, encre, fond)


# ── 4. LE CADRE QUI RESPIRE — BLEU ET VERT ─────────────────────────────────

def _images_cles(page, nom):
    """Les paliers d'une animation : {position: corps de l'image-clé}."""
    m = re.search(r"@keyframes\s+%s\s*\{" % re.escape(nom), page)
    assert m, "l'animation « %s » n'existe pas" % nom
    i, profond, fin = m.end(), 1, None
    while i < len(page):
        if page[i] == "{":
            profond += 1
        elif page[i] == "}":
            profond -= 1
            if profond == 0:
                fin = i
                break
        i += 1
    assert fin, "l'animation « %s » n'est pas refermée" % nom
    bloc = page[m.end():fin]
    return {p.strip(): c for p, c in
            re.findall(r"([\d%,\s]+)\{([^}]*)\}", bloc)}


def _teinte(hexa):
    """La teinte en degrés (0 = rouge, 120 = vert, 240 = bleu)."""
    h = hexa.lstrip("#")
    r, g, b = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    mx, mn = max(r, g, b), min(r, g, b)
    if mx == mn:
        return None
    d = mx - mn
    if mx == r:
        t = ((g - b) / d) % 6
    elif mx == g:
        t = (b - r) / d + 2
    else:
        t = (r - g) / d + 4
    return t * 60


def test_le_cadre_bat_entre_un_BLEU_et_un_VERT(page):
    """LA RÈGLE DÉCISIVE DE CE TOUR.

    Elle ne cherche pas les mots « bleu » et « vert » : elle CALCULE la teinte
    des deux couleurs que l'animation pose, et vérifie qu'elles tombent bien
    l'une dans le bleu et l'autre dans le vert. Une animation qui battrait
    entre deux rouges passerait n'importe quelle règle écrite sur les noms.
    """
    cles = _images_cles(page, "lawtrack-veille")
    bords = []
    for corps in cles.values():
        m = re.search(r"border-color:\s*([^;}]+)", corps)
        assert m, "un palier de l'animation ne pose pas de bordure : %r" % corps
        bords.append(_resoudre(page, m.group(1)))
    teintes = [_teinte(c) for c in bords]
    assert all(t is not None for t in teintes), (
        "une des couleurs du cadre est grise : %r" % list(zip(bords, teintes)))
    verts = [t for t in teintes if 90 <= t <= 165]
    bleus = [t for t in teintes if 195 <= t <= 260]
    assert verts, "aucun vert dans le cadre — teintes relevées : %r" % teintes
    assert bleus, "aucun bleu dans le cadre — teintes relevées : %r" % teintes


def test_le_cadre_ne_disparait_JAMAIS_en_cours_de_battement(page):
    """CE QUI SÉPARE UN ENCADREMENT D'UN CLIGNOTANT.

    Un contour qui s'efface à mi-cycle laisse le bandeau NU la moitié du
    temps. On mesure que CHAQUE palier pose une bordure pleinement opaque,
    et que sa couleur se détache du fond (WCAG 1.4.11, 3:1 pour une limite
    d'élément).
    """
    fond = _fond_compose(page)
    for pos, corps in _images_cles(page, "lawtrack-veille").items():
        m = re.search(r"border-color:\s*([^;}]+)", corps)
        val = m.group(1).strip()
        assert not re.match(r"rgba\(", val) or not re.search(
            r",\s*(0|\.\d+)\s*\)$", val), (
            "au palier %s le cadre est translucide : %r" % (pos, val))
        c = _contraste(_resoudre(page, val), fond)
        assert c >= 3.0, (
            "au palier %s le cadre tient %.2f:1 sur le fond : il ne se "
            "détache pas" % (pos, c))


def test_le_battement_ne_repose_pas_QUE_sur_la_teinte(page):
    """BLEU ET VERT SE DISTINGUENT MAL POUR UNE PART DES LECTEURS.

    Le halo doit donc varier AUSSI en étendue : sans cela, le battement est
    invisible à qui ne sépare pas les deux teintes, et « ça clignote »
    devient une affirmation plutôt qu'un fait.
    """
    etendues = set()
    for corps in _images_cles(page, "lawtrack-veille").values():
        m = re.search(r"box-shadow:\s*([^;}]+)", corps)
        assert m, "un palier ne pose pas de halo : %r" % corps
        etendues.add(tuple(re.findall(r"(\d+)px", m.group(1))))
    assert len(etendues) >= 2, (
        "le halo est identique à tous les paliers : le battement ne tient "
        "qu'à la teinte — %r" % etendues)


def test_le_mouvement_peut_etre_arrete_sans_perdre_le_cadre(page):
    """UN MOUVEMENT QU'ON NE PEUT PAS FAIRE CESSER EST UNE GÊNE.

    Sous `prefers-reduced-motion`, l'animation s'arrête — et le cadre garde
    les DEUX couleurs en même temps, bordure d'un côté, anneau de l'autre.
    Ce qui est demandé ici tient donc sans aucune animation.
    """
    m = re.search(r"@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{"
                  r"\s*\.lawtrack\{([^}]*)\}", page)
    assert m, "aucun repli sans animation pour le bandeau"
    corps = m.group(1)
    assert re.search(r"animation:\s*none", corps), corps
    couleurs = [_resoudre(page, v) for v in
                re.findall(r"#[0-9A-Fa-f]{6}|rgba?\([^)]*\)", corps)]
    teintes = [t for t in (_teinte(c) for c in couleurs) if t is not None]
    assert any(90 <= t <= 165 for t in teintes), (
        "le repli perd le vert — teintes : %r" % teintes)
    assert any(195 <= t <= 260 for t in teintes), (
        "le repli perd le bleu — teintes : %r" % teintes)


def test_l_animation_est_BRANCHEE_sur_le_bandeau_et_ne_stroboscope_pas(page):
    """CE QUI MANQUAIT, ET QUI A ÉTÉ TROUVÉ PAR MUTATION.

    Retirer `animation:` de `.lawtrack` laissait les images-clés en place, la
    pause au survol en place, le repli sans mouvement en place — et toutes les
    règles VERTES pendant que plus rien ne bougeait. Une feuille peut décrire
    une animation magnifique que personne ne joue.

    ELLE RELIE LES DEUX BOUTS : le nom posé sur le bandeau doit être celui
    d'une animation qui existe vraiment. Renommer l'un des deux côtés la fait
    tomber.

    ET ELLE BORNE LA CADENCE. Un cadre qui bat plus de trois fois par seconde
    est un stroboscope — c'est un risque, pas une mise en valeur (WCAG 2.3.1).
    Trop lent, il ne se remarque pas davantage qu'un cadre fixe.
    """
    corps = _regles_bandeau(page)[".lawtrack"]
    m = re.search(r"(?<![-\w])animation:\s*([^;}]+)", corps)
    assert m, (
        "le bandeau ne joue AUCUNE animation : les images-clés peuvent être "
        "parfaites, rien ne bouge à l'écran — %r" % corps)
    decl = m.group(1)
    nom = decl.split()[0]
    paliers = _images_cles(page, nom)      # lève si l'animation n'existe pas
    assert len(paliers) >= 2, (
        "l'animation « %s » n'a qu'un palier : rien ne peut changer" % nom)
    d = re.search(r"(?<![\d.])(\d+(?:\.\d+)?)s\b", decl)
    assert d, "l'animation n'a pas de durée : %r" % decl
    duree = float(d.group(1))
    assert 1.2 <= duree <= 6.0, (
        "un cycle de %.1f s : %s" % (duree, "c'est un stroboscope"
                                     if duree < 1.2 else "ça ne se remarque pas"))
    assert "infinite" in decl, (
        "le battement s'arrête après un tour : %r" % decl)


def test_le_survol_met_le_battement_en_pause(page):
    """Qui s'apprête à cliquer doit pouvoir lire sans que ça bouge."""
    corps = _regles_bandeau(page).get(".lawtrack:hover", "")
    assert "animation-play-state:paused" in corps.replace(" ", ""), corps


def test_le_cadre_ENTOURE_au_lieu_de_border_un_seul_cote(page):
    """« Entourer » : les quatre côtés. Une barre à gauche ne l'est pas."""
    corps = _regles_bandeau(page)[".lawtrack"]
    m = re.search(r"(?<![-\w])border:\s*(\d+)px\s+solid", corps)
    assert m, "le bandeau n'a pas de bordure sur ses quatre côtés : %r" % corps
    assert int(m.group(1)) >= 2, (
        "un cadre de %spx ne s'entoure pas, il se devine" % m.group(1))
    assert not re.search(r"border-left:\s*\d+px", corps), (
        "une barre latérale subsiste : le cadre n'est plus homogène")


def test_le_bandeau_reste_atteignable_au_clavier(page):
    """Un bandeau qui est un lien entier doit montrer son focus : sans cela il
    devient invisible pour qui navigue à la tabulation."""
    assert ".lawtrack:focus-visible{" in page, (
        "aucun état de focus : le bandeau disparaît au clavier")
    bloc = _bloc(page, ".lawtrack:focus-visible{", 160)
    assert "outline" in bloc, bloc
