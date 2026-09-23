# -*- coding: utf-8 -*-
"""UNE COULEUR PAR RÉFÉRENTIEL — DÉCLARÉE UNE FOIS, DÉRIVÉE PARTOUT.

CE QUI A ÉTÉ DEMANDÉ : « dans le menu latéral de Sentinel, mettre les onze
référentiels avec chacun une couleur différente ».

CE QUE LA COULEUR DIT, ET CE QU'ELLE NE DIT PAS. Elle dit « cet écran
appartient à ce référentiel-là ». Elle ne classe pas, ne hiérarchise pas, et
surtout ne signale aucun ÉTAT : dans Sentinel, la terre cuite dit « ici », le
vert « bloc validé », le bleu « bloc attendu », l'ambre « bloc verrouillé ».

TROIS DÉFAUTS ONT ÉTÉ MESURÉS SUR UNE PREMIÈRE VERSION, ET CES RÈGLES LES
RENDENT IMPOSSIBLES :

  1. La couleur de NIS 2 était à ΔE 4,8 du vert de validation, celle
     d'ISO 42001 à 0,6 de l'ambre du verrou, celle du RGPD à 2,2 de la terre
     cuite : neuf des onze tombaient à moins de ΔE 15 d'une couleur d'état.
  2. L'onglet ouvert porte la classe `on`, et les règles d'état avaient été
     écrites pour `.active`, que rien ne pose jamais : elles ne
     s'appliquaient nulle part, sans que rien ne le dise.
  3. La barre avait déjà son canal de teinte (`--sb-ic`), et la première
     version en posait un second à côté : l'icône d'ISO 42001 portait un
     anneau ambre autour d'un dessin vert.

LES SEUILS VIENNENT DU VALIDATEUR DE PALETTES, pas d'un choix fait ici :
ΔE 15 en vision normale et 8 en vision déficiente entre couleurs voisines,
3:1 de contraste pour une icône (WCAG 1.4.11).
"""
import io
import itertools
import math
import os
import re

import pytest

import conformite

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _lire(nom):
    return io.open(os.path.join(_RACINE, nom), encoding="utf-8").read()


HTML = _lire("sentinel.html")
JS = _lire("sentinel.page.js")
#: LA FEUILLE DE STYLE SEULE. Chercher des règles dans le document entier
#: ferait parcourir le balisage — un mégaoctet sans accolade — par des motifs
#: qui reviennent en arrière : la règle mettait plus de deux minutes.
CSS = "\n}\n".join(re.findall(r"<style[^>]*>(.*?)</style>", HTML, re.S))


# ══ LA MESURE DES COULEURS — les calculs du validateur, refaits ici ══════
# OKLab (Ottosson), écarts ×100 ; vision déficiente par les matrices de
# Machado, Oliveira & Fernandes (2009) à sévérité 1 — celles du validateur,
# faute de quoi ses seuils ne vaudraient plus.

def _rvb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _lineaire(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _oklab_lin(r, g, b):
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = [math.copysign(abs(x) ** (1 / 3), x) for x in (l, m, s)]
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def _oklab(h):
    return _oklab_lin(*[_lineaire(c) for c in _rvb(h)])


def _teinte(h):
    _, a, b = _oklab(h)
    return math.degrees(math.atan2(b, a)) % 360


def _chroma(h):
    _, a, b = _oklab(h)
    return math.hypot(a, b)


def _ecart(h1, h2):
    return 100 * math.dist(_oklab(h1), _oklab(h2))


_MACHADO = {
    "protanopie": ((0.152286, 1.052583, -0.204868),
                   (0.114503, 0.786281, 0.099216),
                   (-0.003882, -0.048116, 1.051998)),
    "deutéranopie": ((0.367322, 0.860646, -0.227968),
                     (0.280085, 0.672501, 0.047413),
                     (-0.011820, 0.042940, 0.968881)),
}


def _ecart_deficient(h1, h2):
    """Le PIRE des deux écarts : protanopie et deutéranopie."""
    def vu(h, m):
        r = [_lineaire(c) for c in _rvb(h)]
        s = [max(0.0, min(1.0, sum(m[i][j] * r[j] for j in range(3))))
             for i in range(3)]
        return _oklab_lin(*s)
    return min(100 * math.dist(vu(h1, m), vu(h2, m)) for m in _MACHADO.values())


def _luminance(h):
    r, g, b = [_lineaire(c) for c in _rvb(h)]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contraste(h1, h2):
    a, b = sorted((_luminance(h1), _luminance(h2)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def _melange(h1, part, h2):
    """`color-mix(in srgb, h1 part, h2)` — le mélange que fait le navigateur."""
    a, b = _rvb(h1), _rvb(h2)
    return "#%02X%02X%02X" % tuple(
        round((part * x + (1 - part) * y) * 255) for x, y in zip(a, b))


# ══ CE QUE LA PAGE DÉCLARE — relu dans la page, jamais recopié ══════════

def _jetons():
    """Les jetons de couleur de `:root`, résolus en hexadécimal."""
    racine = re.search(r":root\{(.*?)\}", CSS, re.S).group(1)
    return {m.group(1): m.group(2).upper()
            for m in re.finditer(r"--([a-z0-9-]+):\s*(#[0-9A-Fa-f]{6})\s*;",
                                 racine)}


def _corps(selecteur, propriete):
    """Le corps de LA règle qui porte ce sélecteur ET déclare cette propriété.

    Un même sélecteur revient parfois — sous `prefers-reduced-motion`, ou pour
    un réglage d'alignement : on garde la règle qui décide de la propriété
    visée, et on exige qu'il n'y en ait qu'une."""
    trouves = [c for c in re.findall(r"(?:^|\})\s*" + re.escape(selecteur)
                                     + r"\{([^}]*)\}", CSS, re.M)
               if re.search(r"(?:^|;|\s)" + re.escape(propriete) + r"\s*:", c)]
    assert len(trouves) == 1, (
        "la règle %r qui décide de %s est introuvable ou déclarée %d fois"
        % (selecteur, propriete, len(trouves)))
    return trouves[0]


def _jeton_de(selecteur, propriete):
    corps = _corps(selecteur, propriete)
    m = re.search(r"(?:^|;|\s)" + re.escape(propriete)
                  + r"\s*:\s*var\(--([a-z0-9-]+)\)", corps)
    assert m, "%s ne prend pas %s d'un jeton : %r" % (selecteur, propriete,
                                                     corps[:80])
    return m.group(1)


def _couleurs_d_etat():
    """LES COULEURS QUI DISENT DÉJÀ QUELQUE CHOSE, lues là où elles le disent :
    dans la règle qui pose l'état, pas dans une liste écrite ici."""
    j = _jetons()
    return {
        "le bloc validé du rail": j[_jeton_de(".dr-bloc.validee", "border-color")],
        "le bloc attendu du rail": j[_jeton_de(".dr-bloc.courante", "border-color")],
        "le bloc verrouillé du rail": j[_jeton_de(".dr-bloc.verrouillee",
                                                  "border-color")],
        "l'icône survolée": j[_jeton_de(".sb-item:hover .sb-icon", "color")],
        "la pastille de l'onglet ouvert": j[_jeton_de(".sb-item.on .sb-icon",
                                                      "background")],
    }


def _releve_barre():
    """Chaque tiroir de la barre, les référentiels de ses onglets, et s'il
    appartient à la famille « conformité ». La barre est une suite de
    frères : un onglet appartient au dernier titre qui le précède."""
    nav = HTML[HTML.index('class="sb-nav"'):]
    tiroirs, famille, courant = {}, {}, None
    for m in re.finditer(r'<div class="(sb-section[^"]*|sb-item)"[^>]*>', nav):
        balise = m.group(0)
        g = re.search(r'data-grp="([^"]+)"', balise)
        if m.group(1).startswith("sb-section"):
            courant = g.group(1) if g else None
            if courant:
                tiroirs.setdefault(courant, set())
                famille[courant] = 'data-fam="conformite"' in balise
            continue
        n = re.search(r'data-norme="([^"]+)"', balise)
        if n and courant:
            tiroirs[courant].add(n.group(1))
    return tiroirs, famille


def _tiroirs():
    return _releve_barre()[0]


def _entrees():
    """Les référentiels des onglets RÉELS de la barre, dans l'ordre du document.

    PAS `data-norme="…"` cherché dans tout le fichier : la feuille de style,
    placée AVANT le balisage, cite chaque référentiel dans ses sélecteurs — et
    dans l'ordre validé, puisqu'elle en est engendrée. Une règle d'ordre ou de
    présence qui la lirait passerait toujours, quoi que devienne la barre."""
    nav = HTML[HTML.index('class="sb-nav"'):]
    return [m.group(1) for m in re.finditer(
        r'<div class="sb-item"[^>]*\sdata-norme="([a-z0-9_]+)"', nav)]


def _classes_posees_sur_les_onglets():
    """Les classes que le script pose SUR LES ONGLETS de la barre — pas
    n'importe où : `active`, par exemple, est posée sur des pastilles de
    carrousel et des boutons, jamais sur un onglet.

    Deux chemins sont reconnus, les deux qu'emploie le script : un parcours
    `querySelectorAll('.sb-item…').forEach(function (v) { v.classList… })`,
    et une fonction appelée sur `v` qui pose elle-même la classe (`_ici`)."""
    def corps(depuis):
        n, i = 0, depuis
        while i < len(JS):
            n += {"{": 1, "}": -1}.get(JS[i], 0)
            if n == 0:
                return JS[depuis + 1:i]
            i += 1
        return ""
    aides = {}
    for m in re.finditer(r"function\s+(\w+)\s*\(\s*(\w+)\s*\)\s*\{", JS):
        b = corps(m.end() - 1)
        aides[m.group(1)] = set(re.findall(
            r"\b%s\.classList\.(?:add|toggle)\(\s*'([\w-]+)'" % m.group(2), b))
    posees = set()
    for m in re.finditer(r"querySelectorAll\(\s*'[^']*\.sb-item[^']*'\s*\)\.forEach\("
                         r"\s*function\s*\(\s*(\w+)\s*\)\s*\{", JS):
        v, b = m.group(1), corps(m.end() - 1)
        posees |= set(re.findall(
            r"\b%s\.classList\.(?:add|toggle)\(\s*'([\w-]+)'" % v, b))
        for f in re.findall(r"\b(\w+)\(\s*%s\s*\)" % v, b):
            posees |= aides.get(f, set())
    return posees


def _tiroirs_voues():
    """Les tiroirs de la famille « conformité » qui ne portent qu'UN
    référentiel — ceux dont le titre prend sa couleur.

    LA FAMILLE, PAS UNE LISTE D'EXCLUSIONS. Une première version écartait
    « Pilotage » par son nom ; le jour où l'audit IA Act a porté son
    référentiel, « Évaluer le risque » est passé pour un tiroir voué à l'IA
    Act. Une rubrique hors de la famille abrite des écrans de toute sorte :
    elle garde sa teinte de rubrique."""
    tiroirs, famille = _releve_barre()
    return {g: next(iter(n)) for g, n in tiroirs.items()
            if len(n) == 1 and famille.get(g)}


# ══ LES RÈGLES ══════════════════════════════════════════════════════════

def test_CHAQUE_norme_a_sa_couleur_et_aucune_n_est_partagee():
    """LES ONZE, ET ONZE TEINTES DISTINCTES. Deux référentiels de la même
    couleur, c'est une couleur qui ne dit plus rien — et qui ment sur
    l'appartenance de l'écran qu'elle marque."""
    assert conformite._verifier_couleurs() == (), conformite._verifier_couleurs()
    assert len(conformite.COULEURS) == conformite.NORMES_ANNONCEES, (
        "%d couleurs pour %d normes annoncées"
        % (len(conformite.COULEURS), conformite.NORMES_ANNONCEES))
    teintes = [c.upper() for c in conformite.COULEURS.values()]
    assert len(set(teintes)) == len(teintes), "deux normes partagent une teinte"


@pytest.mark.parametrize("defaut, table, attendu", [
    pytest.param("sans_couleur", lambda c: {k: v for k, v in c.items() if k != "nis2"},
                 "la norme nis2 n'a pas de couleur", id="sans-couleur"),
    pytest.param("orpheline", lambda c: dict(c, fantome="#123456"),
                 "la couleur fantome ne vise aucune norme", id="orpheline"),
    pytest.param("partagee", lambda c: dict(c, cra=c["dora"].lower()),
                 "partagent la couleur", id="partagee"),
    pytest.param("mal_ecrite", lambda c: dict(c, cra="#12345"),
                 "n'est pas un hexadécimal", id="mal-ecrite"),
], )
def test_la_GARDE_des_couleurs_NOMME_ce_qui_se_defait(monkeypatch, defaut, table,
                                                      attendu):
    """LA GARDE DU MODULE, ÉPROUVÉE SUR UNE TABLE FAUSSÉE. Qu'elle rende un
    tuple vide sur la table saine ne prouve rien : une garde qui ne regarde
    rien le rendrait aussi. On lui donne donc chaque défaut, un par un, et
    on exige qu'elle le NOMME."""
    monkeypatch.setattr(conformite, "COULEURS", table(dict(conformite.COULEURS)))
    fautes = " | ".join(conformite._verifier_couleurs())
    assert attendu in fautes, "défaut %s non signalé : %r" % (defaut, fautes)


def test_la_GARDE_refuse_un_ORDRE_de_barre_qui_cite_une_cle_perdue(monkeypatch):
    monkeypatch.setattr(conformite, "ORDRE_BARRE",
                        conformite.ORDRE_BARRE + ("disparue",))
    fautes = " | ".join(conformite._verifier_couleurs())
    assert "l'ordre de barre cite disparue" in fautes, fautes


def test_la_feuille_de_style_NE_SE_SEPARE_PAS_de_la_table():
    """LE DÉFAUT QUE CETTE RÈGLE REND IMPOSSIBLE. Le CSS est engendré depuis
    `conformite.COULEURS`, mais il vit dans un autre fichier : rien
    n'empêche de changer une teinte d'un seul côté. La barre afficherait
    alors une couleur que le moteur ne connaît pas."""
    for cle, coul in conformite.COULEURS.items():
        attendu = '.sb-nav .sb-item[data-norme="%s"]{--sb-ic:%s}' % (cle, coul)
        assert attendu in HTML, (
            "la feuille de style ne déclare pas %s, ou pas avec la couleur "
            "du moteur (%s) — ligne attendue : %s" % (cle, coul, attendu))
    declarees = set(re.findall(
        r'\.sb-item\[data-norme="([a-z0-9_]+)"\]\{--sb-ic:', HTML))
    orphelines = declarees - set(conformite.COULEURS)
    assert not orphelines, (
        "la feuille de style colore des référentiels que le moteur ne "
        "connaît pas : %s" % sorted(orphelines))


def test_le_TITRE_d_un_tiroir_voue_a_un_referentiel_porte_SA_couleur():
    """LE TIROIR, PAS SEULEMENT SES ONGLETS. Tiroirs repliés — c'est leur
    état par défaut —, on ne voit que les titres : si le titre gardait
    l'ancienne teinte de rubrique, la couleur du référentiel n'apparaîtrait
    qu'une fois le tiroir ouvert.

    ET AUCUNE TEINTE PÉRIMÉE NE RESTE DERRIÈRE. Une ancienne règle de même
    poids, écrite plus bas, l'emporterait en silence."""
    voues = _tiroirs_voues()
    assert len(voues) >= 8, "tiroirs voués relevés : %s" % voues
    for grp, cle in voues.items():
        regles = re.findall(r'\.sb-nav \[data-grp="%s"\]\{--sb-ic:([^}]*)\}'
                            % re.escape(grp), HTML)
        assert regles == [conformite.COULEURS[cle]], (
            "le tiroir %s (%s) devrait porter %s et rien d'autre ; la feuille "
            "de style lui donne %s" % (grp, cle, conformite.COULEURS[cle], regles))


def test_un_tiroir_voue_a_AUCUN_referentiel_reste_NEUTRE():
    """DEUX TIROIRS DE LA FAMILLE « CONFORMITÉ » NE SONT À PERSONNE : le taux,
    transversal aux onze, et celui où les deux NIST cohabitent. Leur donner la
    couleur de l'un rangerait l'autre sous une couleur qui n'est pas la
    sienne.

    ET « SANS COULEUR » NE VEUT PAS DIRE « TERRE CUITE ». Faute de teinte, le
    titre retombait sur la valeur de repli de son icône — la terre cuite, qui
    dit « ici ». Un tiroir neutre déclare donc une teinte SANS CHROMA."""
    tiroirs, famille = _releve_barre()
    neutres = [g for g, n in tiroirs.items() if famille.get(g) and len(n) != 1]
    assert "nist-ot" in neutres and "taux-conformite" in neutres, neutres
    jetons = _jetons()
    for grp in neutres:
        regles = re.findall(r'\.sb-nav \[data-grp="%s"\]\{--sb-ic:var\(--([a-z0-9-]+)\)\}'
                            % re.escape(grp), CSS)
        assert len(regles) == 1, (
            "le tiroir %s devrait déclarer UNE teinte neutre, il en déclare %s"
            % (grp, regles))
        assert _chroma(jetons[regles[0]]) < 0.02, (
            "le tiroir %s prend --%s (%s), qui n'est pas neutre"
            % (grp, regles[0], jetons[regles[0]]))
    # …et aucune règle ne lui donne la couleur d'un référentiel
    for grp in neutres:
        assert not re.search(r'\[data-grp="%s"\]\{--sb-ic:#' % re.escape(grp), CSS), (
            "le tiroir %s a reçu une couleur de référentiel" % grp)


def test_la_pastille_VIDE_porte_la_couleur_par_un_POINT():
    """LE DÉFAUT CONSTATÉ À L'ÉCRAN. Vingt-huit onglets de référentiel n'ont
    pas de dessin dans leur pastille. Teintée à 9 %, elle rendait la couleur
    presque invisible : DORA et NIS 2 paraissaient gris.

    Le point doit prendre `currentColor` — c'est ce qui le fait suivre la
    couleur de l'icône : celle du référentiel au repos, la terre cuite au
    survol, le blanc sur l'onglet ouvert. Une couleur écrite en dur ne
    suivrait aucun des trois états."""
    vides = re.findall(r'<div class="sb-item" data-norme="[^"]+"[^>]*>'
                       r'<span class="sb-icon"[^>]*></span>', HTML)
    assert len(vides) >= 20, "%d pastille(s) vide(s) relevée(s)" % len(vides)
    corps = _corps(".sb-item .sb-icon:empty::before", "background")
    assert re.search(r"(^|;|\s)background\s*:\s*currentColor", corps), corps
    assert "content:''" in corps.replace('"', "'"), corps
    for dim in ("width", "height"):
        m = re.search(r"(?:^|;|\s)%s\s*:\s*(\d+)px" % dim, corps)
        assert m and int(m.group(1)) >= 6, "%s du point : %r" % (dim, corps)


def test_CHAQUE_norme_est_ATTEIGNABLE_depuis_la_barre():
    """UNE COULEUR DÉCLARÉE POUR UN RÉFÉRENTIEL QU'AUCUNE ENTRÉE NE PORTE
    serait une couleur morte. On mesure donc le balisage, pas la
    déclaration."""
    portees = set(_entrees())
    manquantes = sorted(set(conformite.COULEURS) - portees)
    assert not manquantes, (
        "ces référentiels ont une couleur mais aucune entrée de barre ne la "
        "porte : %s" % manquantes)


@pytest.mark.parametrize("cle", sorted(conformite.COULEURS))
def test_chaque_referentiel_garde_son_NOM_ecrit(cle):
    """LA COULEUR NE REMPLACE JAMAIS LE NOM. Onze teintes ne sont pas toutes
    séparables deux à deux — c'est mesuré plus bas ; le nom, lui, tranche."""
    trouvees = 0
    for m in re.finditer(r'<div class="sb-item" data-norme="%s"[^>]*>(.*?)</div>'
                         % cle, HTML, re.S):
        trouvees += 1
        texte = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        assert len(texte) >= 4, (
            "une entrée %s n'a pas de libellé lisible : %r" % (cle, texte))
    assert trouvees, "aucune entrée %s relevée" % cle


def test_la_couleur_passe_par_le_CANAL_de_la_barre_et_ne_teint_NI_texte_NI_fond():
    """LA COULEUR NE VA QUE LÀ OÙ LA BARRE MET DÉJÀ UNE TEINTE : l'icône, sa
    pastille, le filet sous le titre du tiroir.

    Colorer le TEXTE de onze teintes, c'est promettre onze contrastes de
    lecture qu'une palette de onze ne tient pas. Colorer le FOND de l'entrée,
    c'est une barre en arc-en-ciel où l'onglet ouvert se perd.

    DEUX CÔTÉS À GARDER. Les règles de couleur ne déclarent QUE la variable ;
    et la variable n'est lue que par des icônes ou par le filet du titre."""
    for m in re.finditer(r'\.sb-nav (?:\.sb-item)?\[data-(?:norme|grp)="[^"]+"\]'
                         r'\{([^}]*)\}', HTML):
        assert re.fullmatch(r"--sb-ic:(#[0-9A-F]{6}|var\(--[a-z0-9-]+(,[^)]*)?\))",
                            m.group(1)), (
            "une règle de teinte déclare autre chose que la variable : %r"
            % m.group(0))
    lecteurs = []
    for m in re.finditer(r"\{([^{}]*var\(--sb-ic[^{}]*)\}", CSS):
        avant = CSS[:m.start()]
        debut = max(avant.rfind("}"), avant.rfind("*/"))
        lecteurs.append((avant[debut + 1:].lstrip("/").strip(), m.group(1)))
    assert len(lecteurs) >= 3, lecteurs
    for selecteur, corps in lecteurs:
        if re.search(r"\.sb-(icon|sec-ic)\s*$", selecteur):
            continue
        usages = [d.split(":")[0].strip() for d in corps.split(";")
                  if "var(--sb-ic" in d]
        assert usages == ["border-bottom"], (
            "%s lit la couleur du référentiel pour %s — seul le filet sous le "
            "titre y a droit" % (selecteur, usages))


def test_l_ORDRE_de_la_barre_est_celui_qui_a_ete_VALIDE():
    """LA SÉPARATION SE MESURE ENTRE VOISINES, ET LES VOISINES SONT CELLES DE
    L'ÉCRAN. `ORDRE_BARRE` fixe l'ordre réel ; cette règle le confronte à
    l'ordre d'apparition des `data-norme` dans la page."""
    vus = []
    for cle in _entrees():
        if cle not in vus:
            vus.append(cle)
    dans_barre = [c for c in vus if c != "ia_act"]
    assert dans_barre == list(conformite.ORDRE_BARRE), (
        "l'ordre d'affichage a changé sans que la palette soit revalidée :\n"
        "  écran  : %s\n  validé : %s" % (dans_barre, list(conformite.ORDRE_BARRE)))


def test_les_tiroirs_VOISINS_se_distinguent_meme_en_vision_deficiente():
    """LE CONTRÔLE QUI COMPTE POUR UNE BARRE : deux tiroirs qui se touchent
    doivent se séparer à l'œil. Planchers du validateur : ΔE 15 en vision
    normale, 8 en protanopie comme en deutéranopie."""
    ordre = [conformite.COULEURS[c] for c in conformite.ORDRE_BARRE]
    fautes = []
    for (a, ca), (b, cb) in zip(zip(conformite.ORDRE_BARRE, ordre),
                                zip(conformite.ORDRE_BARRE[1:], ordre[1:])):
        n, d = _ecart(ca, cb), _ecart_deficient(ca, cb)
        if n < 15:
            fautes.append("%s/%s à ΔE %.1f en vision normale" % (a, b, n))
        if d < 8:
            fautes.append("%s/%s à ΔE %.1f en vision déficiente" % (a, b, d))
    assert not fautes, " | ".join(fautes)


def test_aucune_couleur_n_IMITE_une_couleur_d_ETAT():
    """LE DÉFAUT MESURÉ SUR LA PREMIÈRE PALETTE : neuf teintes sur onze à
    moins de ΔE 15 d'une couleur qui dit déjà un état — l'ISO 42001 à 0,6 de
    l'ambre du verrou, le RGPD à 2,2 de la terre cuite.

    On exige qu'aucune ne soit le même PAS de couleur : ΔE 8 au moins, le
    plancher du validateur pour deux couleurs qu'on doit distinguer. Les
    couleurs d'état sont relues dans les règles qui les posent."""
    etats = _couleurs_d_etat()
    assert len(set(etats.values())) >= 4, etats
    fautes = ["%s (%s) à ΔE %.1f de %s (%s)" % (cle, coul, _ecart(coul, e), nom, e)
              for cle, coul in conformite.COULEURS.items()
              for nom, e in etats.items() if _ecart(coul, e) < 8]
    assert not fautes, " | ".join(fautes)


def test_le_VERT_de_validation_n_est_la_couleur_d_AUCUN_referentiel():
    """LE VERT EST TENU À L'ÉCART TOUT ENTIER, pas seulement son pas exact.
    Le parcours peint en vert un bloc rempli, dans ces onze modules mêmes :
    un référentiel vert dans la barre se lirait « acquis ».

    « Vert » se mesure sans liste écrite ici : une teinte est de la famille
    du vert si, parmi les teintes que Sentinel déclare dans `:root`, c'est
    du vert de validation qu'elle est la plus proche sur le cercle."""
    jetons = _jetons()
    vert = jetons[_jeton_de(".dr-bloc.validee", "border-color")]
    maison = {nom: h for nom, h in jetons.items() if _chroma(h) >= 0.08}
    assert vert in maison.values() and len(set(maison.values())) >= 6, maison

    def distance(a, b):
        d = abs(a - b) % 360
        return min(d, 360 - d)

    fautes = []
    for cle, coul in conformite.COULEURS.items():
        t = _teinte(coul)
        proche = min(maison.values(), key=lambda h: distance(t, _teinte(h)))
        if proche == vert:
            fautes.append("%s (%s, teinte %.0f°)" % (cle, coul, t))
    assert not fautes, "de la famille du vert de validation : " + ", ".join(fautes)


def test_l_icone_reste_LISIBLE_sur_sa_propre_pastille():
    """L'ICÔNE EST DESSINÉE DE LA COULEUR SUR UN FOND QUI EN CONTIENT UN PEU.
    Le mélange est relu dans la feuille de style — sa part et son fond —, et
    le contraste d'un élément graphique doit atteindre 3:1 (WCAG 1.4.11)."""
    corps = _corps(".sb-item .sb-icon", "background")
    m = re.search(r"background:color-mix\(in srgb,var\(--sb-ic[^)]*\)\)\s*"
                  r"(\d+)%,var\(--([a-z0-9-]+)\)\)", corps)
    assert m, "la pastille n'est plus un mélange de la teinte : %r" % corps
    part, fond = int(m.group(1)) / 100, _jetons()[m.group(2)]
    fautes = []
    for cle, coul in conformite.COULEURS.items():
        c = _contraste(coul, _melange(coul, part, fond))
        if c < 3.0:
            fautes.append("%s %.2f:1" % (cle, c))
    assert not fautes, "icône illisible sur sa pastille : " + ", ".join(fautes)


def test_une_classe_d_ETAT_de_l_onglet_est_une_classe_que_le_script_POSE():
    """LE DÉFAUT QUI NE SE VOIT PAS À LA LECTURE. L'onglet ouvert porte `on` ;
    une première version stylait `.active`, que rien ne pose jamais — ses
    règles ne s'appliquaient nulle part, et le fichier se lisait très bien.

    Chaque classe d'état écrite en `.sb-item.<classe>` doit donc être une
    classe que le script ajoute ou bascule réellement SUR UN ONGLET. Posée
    n'importe où ne suffit pas : le script pose `active` sur des pastilles
    de carrousel, et une première version de cette règle s'en contentait —
    elle aurait laissé passer le défaut même qu'elle devait arrêter."""
    classes = set(re.findall(r"\.sb-item\.([a-zA-Z_-]+)", CSS))
    assert "on" in classes, classes
    posees = _classes_posees_sur_les_onglets()
    assert {"on", "sb-locked"} <= posees, (
        "le relevé ne retrouve plus les deux classes que le script pose sur "
        "les onglets : %s" % sorted(posees))
    mortes = sorted(classes - posees)
    assert not mortes, (
        "des règles visent des classes d'onglet que le script ne pose jamais : "
        "%s" % mortes)
