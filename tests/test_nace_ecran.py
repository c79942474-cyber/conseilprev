# -*- coding: utf-8 -*-
"""LE BLOC NACE À L'ÉCRAN — hiérarchie, état actif, et fin du doublon muet.

CE QUI A ÉTÉ RELEVÉ EN NAVIGATEUR, ET QUE LES RÈGLES EXISTANTES NE VOYAIENT
PAS. `tests/test_secteurs_nace.py` garde la nomenclature : les vingt-deux
sections, leur source, leur réserve, le fait qu'aucun profil de repli ne soit
choisi à la place du client. Toutes ces règles étaient vertes pendant que
l'écran montrait ceci, pour la section C :

  — QUATRE PROFILS PRÉSENTÉS EN PAIRS. « Industrie » couvre TOUTE la section ;
    « Télécom », « Santé » et « Transport » n'en couvrent qu'une tranche — les
    équipementiers réseau, les fabricants de dispositifs, les constructeurs de
    véhicules. Rien ne les distinguait, ce qui invitait un industriel à cocher
    Télécom.

  — LES NOTES DÉTACHÉES DE LEURS BOUTONS. Quatre boutons, puis quatre notes en
    bloc : le lecteur devait deviner laquelle allait avec lequel.

  — AUCUN ÉTAT ACTIF DANS LA PROPOSITION. `MAT_CUR` vivait dans une autre
    fonction anonyme : le bloc NACE ne POUVAIT pas savoir quel profil était en
    vigueur. L'écran affichait donc « votre activité : C — Industrie
    manufacturière » au-dessus d'un audit tournant sur Télécom, sans rien qui
    relie les deux.

  — DOUZE BOUTONS POUR HUIT PROFILS. Quatre étaient affichés deux fois, même
    dessin et même action, sans qu'un libellé dise qu'il s'agit du même bouton.
"""
import io
import json
import os
import re
import subprocess

import pytest

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = io.open(os.path.join(RACINE, "sentinel.page.js"), encoding="utf-8").read()
PAGE = io.open(os.path.join(RACINE, "sentinel.html"), encoding="utf-8").read()

import sys
sys.path.insert(0, RACINE)
import secteurs_nace as N                                            # noqa: E402


# ══════════════════════════════════════════════════════════════════════════
#  1. LA HIÉRARCHIE EXISTE DANS LES DONNÉES, ET ELLE EST EXPLICITE
# ══════════════════════════════════════════════════════════════════════════

def test_la_section_principale_d_un_profil_est_la_PREMIERE_de_sa_liste():
    """LA CONVENTION QUI PORTE TOUTE LA HIÉRARCHIE, et elle était tacite.
    `sections[0]` est la section où l'essentiel de l'activité du profil se
    range ; les suivantes sont des tranches. Les notes le disent en prose —
    « les opérateurs relèvent de K ; les équipementiers réseau, qui fabriquent,
    de C » — mais rien ne le garantissait. Un tri fait un jour sur cette liste
    inverserait la hiérarchie sans qu'aucune règle ne rougisse."""
    for cle, p in N.PROFILS_SENTINEL.items():
        assert p["sections"], cle
        principale = p["sections"][0]
        r = N.choisir(principale)
        assert cle in [x["cle"] for x in r["principaux"]], (
            "%s a %s pour première section, mais n'y est pas principal"
            % (cle, principale))


def test_une_section_separe_ses_profils_PRINCIPAUX_de_ses_tranches():
    """LE DÉFAUT RELEVÉ SUR LA SECTION C. Quatre profils la mentionnent ; un
    seul en est le profil. Les servir dans un seul sac les rend équivalents."""
    r = N.choisir("C")
    assert [x["cle"] for x in r["principaux"]] == ["industrie"], r["principaux"]
    partiels = {x["cle"]: x["principale"] for x in r["partiels"]}
    # « agro » S'AJOUTE AUX TROIS, ET C'EST DÉLIBÉRÉ : l'annexe II de NIS2 ne
    # vise pas la production primaire mais bien la transformation alimentaire
    # INDUSTRIELLE, qui se range en C. Le profil a donc A pour section
    # principale et C pour tranche — exactement la convention des trois autres.
    assert partiels == {"agro": "A", "sante": "R",
                        "telecom": "K", "transport": "H"}, partiels
    # LES DEUX ENSEMBLES SONT DISJOINTS ET COUVRENT TOUT : sans quoi un profil
    # disparaîtrait de l'écran, ou y figurerait deux fois.
    for code in [s["code"] for s in N.SECTIONS]:
        c = N.choisir(code)
        cles = [x["cle"] for x in c["principaux"]] + [x["cle"] for x in c["partiels"]]
        assert sorted(cles) == sorted(c["profils"]), code
        assert len(cles) == len(set(cles)), "profil en double pour %s" % code


def test_chaque_profil_voyage_avec_SA_note():
    """Deux listes parallèles se désynchronisent au premier tri fait d'un seul
    côté, et l'écran attribue alors la note d'un profil à un autre sans que
    rien ne le signale."""
    for code in [s["code"] for s in N.SECTIONS]:
        for x in N.choisir(code)["principaux"] + N.choisir(code)["partiels"]:
            assert x["note"] == N.PROFILS_SENTINEL[x["cle"]]["note"], (
                "%s / %s : la note ne suit pas son profil" % (code, x["cle"]))


# ══════════════════════════════════════════════════════════════════════════
#  2. L'ÉCRAN LIT LE SECTEUR EN COURS — ET NE PEUT PAS L'ÉCRIRE
# ══════════════════════════════════════════════════════════════════════════

def test_le_secteur_courant_est_LISIBLE_par_le_bloc_nace():
    """LA CAUSE STRUCTURELLE DU DÉSACCORD À L'ÉCRAN. Sans accesseur, le bloc
    NACE ne peut pas savoir quel profil est en vigueur, et peint ses boutons
    sans état actif quoi qu'il arrive."""
    assert "window.matSecteurCourant = function()" in JS, (
        "l'accesseur en lecture a disparu : le bloc NACE redeviendra aveugle")
    assert "window.matSecteurCourant ? window.matSecteurCourant()" in JS, (
        "le bloc NACE ne lit plus le secteur courant")


def test_le_secteur_courant_n_est_PAS_exposé_en_ecriture():
    """Exposer `MAT_CUR` lui-même ouvrirait une seconde porte d'écriture à côté
    de `matSelect`, qui est la seule à réinitialiser les réponses et à
    recalculer les scores. Deux portes, et l'état se met à diverger."""
    assert not re.search(r"window\.MAT_CUR\s*=", JS), (
        "MAT_CUR est exposé en écriture sur window")


def test_choisir_un_secteur_REPEINT_la_proposition_nace():
    """Sans ce rappel, les deux rangées affichent des états contradictoires :
    le sélecteur marque le profil retenu, la proposition reste muette."""
    d = JS.index("window.matSelect = function(k){")
    f = JS.index("\n", JS.index("window.scrollTo", d))
    assert "window.naceRepeindre" in JS[d:f], (
        "matSelect ne repeint plus le bloc NACE")
    assert "window.naceRepeindre = function()" in JS, (
        "le point de repeinture a disparu")


def test_le_bouton_propose_porte_son_etat_actif():
    """MESURÉ SUR LA CLASSE ET SUR L'ATTRIBUT. `on` peint ; `aria-pressed`
    annonce. Un bouton qui n'a que la couleur ne dit rien à un lecteur
    d'écran, et l'état actif est précisément ce qui manquait."""
    d = JS.index("function bouton(cle, note, encart, courant)")
    f = JS.index("\n  }", d)
    corps = JS[d:f]
    assert "var actif = (cle === courant)" in corps, corps[:200]
    assert "(actif ? ' on' : '')" in corps, "la classe active n'est plus posée"
    assert "aria-pressed" in corps, "l'état n'est pas annoncé aux lecteurs d'écran"


# ══════════════════════════════════════════════════════════════════════════
#  3. LE DÉSACCORD EST NOMMÉ, JAMAIS CORRIGÉ D'OFFICE
# ══════════════════════════════════════════════════════════════════════════

def _peintre():
    """Le peintre NACE SEUL, découpé dans le vrai fichier — jamais recopié."""
    d = JS.index("window.naceCharger = function()")
    deb = JS.rindex("(function(){", 0, d)
    fin = JS.index("\n})();", JS.index("window.naceChoisir", d)) + len("\n})();")
    return JS[deb:fin]


def _peindre(code, courant, section):
    """Évalue le peintre contre un DOM postiche et rend le HTML écrit.

    ON EXÉCUTE, ON NE LIT PAS. La première version de la règle ci-dessous
    cherchait les phrases d'avertissement DANS LA SOURCE. Une mutation qui
    remplaçait `if(courant && !dedans)` par `if(false && …)` la laissait verte :
    les mots restaient écrits, la branche était morte. C'est le défaut que ces
    dépôts corrigent partout — une règle qui constate une propriété syntaxique
    au lieu de mesurer un effet."""
    code_js = """
var ecrit = '';
var zone = {set innerHTML(v){ ecrit = v; }, get innerHTML(){ return ecrit; }};
var document = {getElementById: function(id){
  return id === 'mat-nace-reponse' ? zone : null; }};
var choisis = [];
var replis = [];
var window = {MAT_SECTORS: %s, matSecteurCourant: function(){ return %s; },
              matSelect: function(k){ choisis.push(k); }};
document.getElementById = (function(vrai){
  return function(id){
    if(id === 'mat-secteurs-repli')
      return {set open(v){ replis.push(v); }, get open(){ return true; }};
    return vrai(id);
  };
})(document.getElementById);
%s
window.__nace = {sections: [%s], a_renseigner: {x: 'y'}};
window.naceChoisir(%s);
console.log(JSON.stringify({html: ecrit, choisis: choisis, replis: replis}));
""" % (json.dumps({k: {"icon": "•", "label": k.upper()}
                   for k in N.PROFILS_SENTINEL}),
       json.dumps(courant), _peintre(), json.dumps(section), json.dumps(code))
    r = subprocess.run(["node", "-e", code_js], capture_output=True, text=True)
    assert r.returncode == 0, "peintre inévaluable : %s" % r.stderr[-800:]
    return json.loads(r.stdout)["html"]


def _geste(code, courant, section):
    """LE GESTE DU CLIENT, pas le simple repeint. `naceChoisir` est ce que la
    liste déroulante appelle ; c'est la seule porte qui a le droit d'appliquer
    un profil. Le harnais rend ce qui a été CHOISI, pour mesurer quand."""
    code_js = """
var ecrit = '';
var zone = {set innerHTML(v){ ecrit = v; }, get innerHTML(){ return ecrit; }};
var choisis = [];
var replis = [];
var document = {getElementById: function(id){
  if(id === 'mat-nace-reponse') return zone;
  if(id === 'mat-secteurs-repli')
    return {set open(v){ replis.push(v); }, get open(){ return true; }};
  return null; }};
var window = {MAT_SECTORS: %s, matSecteurCourant: function(){ return %s; },
              matSelect: function(k){ choisis.push(k); }};
%s
window.__nace = {sections: [%s], a_renseigner: {x: 'y'}};
window.naceChoisir(%s);
console.log(JSON.stringify({html: ecrit, choisis: choisis, replis: replis}));
""" % (json.dumps({k: {"icon": "\u2022", "label": k.upper()}
                   for k in N.PROFILS_SENTINEL}),
       json.dumps(courant), _peintre(), json.dumps(section), json.dumps(code))
    r = subprocess.run(["node", "-e", code_js], capture_output=True, text=True)
    assert r.returncode == 0, "peintre inévaluable : %s" % r.stderr[-800:]
    return json.loads(r.stdout)


def _section(code):
    """La section telle que la route la sert, lue du module."""
    import copy
    for s in N.etat()["sections"]:
        if s["code"] == code:
            return copy.deepcopy(s)
    raise AssertionError(code)


def test_un_profil_etranger_a_la_section_est_SIGNALE():
    """L'audit démarre sur un profil par défaut. Si le client désigne ensuite
    une section dont ce profil ne relève pas, l'écran montrait les deux sans
    les relier — c'est exactement ce qu'une capture d'écran a révélé.

    LA RÈGLE EXÉCUTE LE PEINTRE. Elle vérifie les DEUX cas, sans quoi elle ne
    mesurerait pas ce qu'elle prétend : le message paraît quand le profil est
    étranger à la section, et NE paraît PAS quand il en relève."""
    etranger = _peindre("C", "finance", _section("C"))
    assert "ne relève pas de la" in etranger, (
        "le désaccord n'est pas signalé : %s" % etranger[-400:])
    assert "changé pour vous" in etranger, (
        "la page ne dit pas qu'elle s'abstient de choisir")
    # TÉMOIN NÉGATIF : « telecom » EST une tranche de C (les équipementiers
    # réseau). Le signaler serait une fausse alerte, et une règle qui ne
    # vérifie que le cas positif ne verrait pas la différence.
    parent = _peindre("C", "telecom", _section("C"))
    assert "ne relève pas de la" not in parent, (
        "un profil qui relève bien de la section est signalé à tort")


def test_le_pluriel_de_PROFIL_PRINCIPAL_est_ecrit_correctement():
    """RELEVÉ EN RECETTE SUR LA SECTION K, qui désigne deux profils : l'écran
    affichait « Profils principalaux ». Le pluriel était fabriqué en collant
    « aux » à « principal ». Une seule section sur vingt-deux le déclenche —
    c'est exactement le genre de faute qu'on ne voit qu'en exécutant."""
    deux = _peindre("K", None, _section("K"))
    assert "principaux" in deux and "principalaux" not in deux, deux[:400]
    un = _peindre("C", None, _section("C"))
    assert "Profil principal de cette section" in un, un[:400]
    assert "Profils" not in un.split("de cette section")[0], (
        "le singulier porte une marque de pluriel")


def test_le_profil_principal_est_peint_AVANT_les_tranches():
    """L'ordre est la moitié du message : montrer « Télécom » avant
    « Industrie » pour la section C invite à cocher le mauvais."""
    html = _peindre("C", "industrie", _section("C"))
    assert "Profil principal de cette section" in html
    assert "Une partie seulement" in html
    assert html.index("Profil principal") < html.index("Une partie seulement")
    # La tranche dit où elle est chez elle, sinon « une partie » ne dit pas
    # laquelle.
    assert "Principalement en K" in html and "Principalement en H" in html, html[-500:]


def test_une_section_a_socle_de_cadre_explique_au_lieu_de_rester_vide():
    """LA RÈGLE A SUIVI UN CHANGEMENT D'ÉTAT DE FAIT, et le motif est écrit ici.
    Elle visait les treize sections SANS PROFIL — plus de la moitié de la
    nomenclature — dont l'écran devait dire pourquoi il ne proposait rien. Ces
    treize ont désormais un profil ; ce qu'il reste à expliquer est que leur
    socle n'est pas calibré. Un bloc vide y serait toujours pire qu'un refus."""
    html = _peindre("A", None, _section("A"))
    assert "socle" in html, html[:300]
    assert "<li>" in html, "ce qu'il faudrait pour l'établir n'est plus listé"
    # ÉMIS NE VEUT PAS DIRE LU. Le harnais node n'applique aucune feuille de
    # style : une liste masquée en `display:none` lui paraît présente, alors
    # qu'elle est invisible au lecteur. Une mutation qui remplaçait la classe
    # par `style="display:none"` a survécu à la première version de cette
    # règle. Le masquage en ligne se mesure, lui, dans le HTML rendu.
    assert "display:none" not in html.replace(" ", ""), (
        "un bloc du peintre est masqué en ligne : émis, mais illisible")


def test_LE_PEINTRE_ne_choisit_jamais_de_profil():
    """LA MOITIÉ DE LA GARDE QUI NE BOUGE PAS. `matSelect` repeint le bloc
    NACE pour que les deux rangées s'accordent ; si le peintre appliquait un
    profil à son tour, la première sélection partirait en boucle infinie. Le
    peintre DESSINE, il n'applique pas."""
    d = JS.index("  function peindre(code){")
    f = JS.index("\n    zone.innerHTML = html;\n  }", d)
    corps = JS[d:f]
    appels = re.findall(r"matSelect\([^)]*\)", corps)
    # Seuls les `onclick` en attendent un : ce sont des gestes de l'utilisateur.
    assert not [a for a in appels if "\\'" not in a], (
        "le peintre applique un profil : la repeinture boucle, et le choix se "
        "fait sans geste du client — %s" % appels)


def test_le_profil_SUIT_la_section_quand_elle_n_en_designe_qu_UN():
    """CE QUE CETTE RÈGLE A REMPLACÉ, ET POURQUOI. La version précédente
    interdisait TOUT appel à `matSelect` hors d'un clic, au motif que « le
    moins faux » appartient au client. Le motif était juste, sa portée trop
    large : appliquer l'UNIQUE profil qu'une section désigne n'est pas choisir
    à la place du client, c'est la conséquence directe de ce qu'il vient de
    déclarer. L'écran annonçait sinon « votre activité : C » au-dessus d'un
    audit resté sur le profil par défaut, et il fallait re-cliquer.

    LA RÈGLE MESURE DONC LE *QUAND*, pas le *si* — en exécutant les trois cas."""
    # UN SEUL CANDIDAT → le profil suit.
    r = _geste("C", "telecom", _section("C"))
    assert r["choisis"] == ["industrie"], (
        "la section C désigne « industrie » et un seul profil : il devait être "
        "appliqué, or %s" % r["choisis"])
    # DÉJÀ LE BON → on n'applique pas deux fois, ce qui relancerait le calcul.
    r = _geste("C", "industrie", _section("C"))
    assert r["choisis"] == [], (
        "le profil déjà en vigueur est ré-appliqué : les réponses seraient "
        "réinitialisées sans raison")


def test_l_arbitrage_ENTRE_CANDIDATS_reste_au_client():
    """L'ABSTENTION S'EST RÉDUITE À UN SEUL CAS, ET C'EST LE BON — le motif est
    écrit ici parce que la règle vient de perdre la moitié de son périmètre.

    ELLE COUVRAIT DEUX CAS. Le premier tient toujours : la section K désigne
    l'édition logicielle ET les télécoms, et trancher entre elles serait
    arbitrer à la place du client. Le second — « aucun profil relevé » — a
    disparu avec le défaut qu'il abritait : une section sans profil laissait
    l'audit sur le SECTEUR PRÉCÉDENT. S'abstenir n'y était pas neutre, c'était
    laisser en place l'audit d'un autre métier.

    CE QUI EST MESURÉ ICI : quand le profil courant est DÉJÀ l'un des candidats
    de la section, on n'y touche pas. Le client a choisi, on ne rechoisit pas
    pour lui."""
    # K désigne « it » et « telecom ». Le courant est « telecom » : il est
    # parmi les candidats, donc rien ne bouge.
    r = _geste("K", "telecom", _section("K"))
    assert r["choisis"] == [], (
        "un profil a été appliqué alors que le courant était déjà candidat : %s"
        % (r["choisis"],))


def test_LE_DEFAUT_CORRIGE_l_audit_ne_reste_JAMAIS_sur_un_secteur_etranger():
    """LE DÉFAUT QUE CE LOT CORRIGE, MESURÉ SUR LES VINGT-DEUX SECTIONS.

    Un client en construction choisissait F, lisait « aucun profil relevé » —
    et l'audit affiché juste en dessous restait celui des télécoms : ses
    systèmes, ses régimes, son budget. Rien ne le démentait. Treize sections
    sur vingt-deux étaient dans ce cas.

    LA RÈGLE PARCOURT TOUTE LA NOMENCLATURE plutôt que deux cas choisis : c'est
    la seule forme qui attrape la quatorzième section le jour où elle arrive.
    """
    etranger = []
    for s in N.SECTIONS:
        code = s["code"]
        candidats = [x["cle"] for x in N.choisir(code)["principaux"]] + \
                    [x["cle"] for x in N.choisir(code)["partiels"]]
        assert candidats, "section %s sans aucun candidat" % code
        # On part d'un profil qui n'est PAS candidat de la section, pour que
        # l'abstention se voie si elle a lieu.
        depart = "telecom" if "telecom" not in candidats else "energie"
        if depart in candidats:
            continue
        r = _geste(code, depart, _section(code))
        applique = r["choisis"][-1] if r["choisis"] else depart
        if applique not in candidats:
            etranger.append((code, applique))
    assert not etranger, (
        "l'audit reste sur un profil étranger à la section choisie : %r"
        % (etranger,))


def test_la_rangee_des_huit_se_replie_QUAND_la_section_a_decide():
    """Tant qu'aucune activité n'est déclarée, la rangée est le SEUL moyen de
    choisir : la fermer d'office priverait de commande celui qui arrive. Une
    fois la section connue et le profil appliqué, elle n'est plus qu'un
    recours — et deux commandes également visibles pour une seule décision,
    c'est ce qui faisait lire deux fois les mêmes boutons."""
    # `replis` ENREGISTRE `open`, PAS « replié » — les deux sont inverses, et
    # ma première version comparait au mauvais sens : elle réclamait True là
    # où replier pose open=false. Une règle qui se trompe de polarité échoue
    # sur du code juste, ou pire, passe sur du code faux.
    for code in ("C", "A"):
        # « A » A CHANGÉ DE CAMP, et c'est la conséquence directe du lot : elle
        # désignait zéro profil, elle en désigne un seul. Une section qui a
        # décidé n'a plus besoin de la rangée.
        assert _geste(code, "telecom", _section(code))["replis"] == [False], (
            "section %s : la rangée reste OUVERTE alors que la section a "
            "décidé" % code)
    # K reste le cas où la rangée SERT : deux candidats, l'arbitrage au client.
    assert _geste("K", "telecom", _section("K"))["replis"] == [True], (
        "la rangée se replie alors que le choix reste à faire — le client "
        "perdrait sa seule commande")


# ══════════════════════════════════════════════════════════════════════════
#  4. LE DOUBLON MUET
# ══════════════════════════════════════════════════════════════════════════

def test_la_rangee_des_huit_profils_dit_ce_qu_elle_est():
    """Quatre des huit profils sont affichés DEUX FOIS : proposés d'après la
    section, puis listés en entier. Même dessin, même action. Le titre est ce
    qui distingue une recommandation motivée d'un second sélecteur."""
    d = PAGE.index('id="mat-sector-bar"')
    amont = PAGE[max(0, d - 900):d]
    assert "huit profils relevés" in amont, (
        "la rangée complète n'est plus introduite : elle redevient un doublon "
        "muet de la proposition NACE")


def test_la_reserve_ne_renvoie_plus_a_un_ci_dessous_qui_est_au_dessus():
    """L'intitulé officiel est servi DANS la réponse, au-dessus de la réserve.
    « ci-dessous » envoyait le lecteur chercher plus bas ce qu'il venait de
    lire."""
    assert "ci-dessous" not in N.SOURCE["reserve"], N.SOURCE["reserve"][:120]
    assert "reproduits ici" in N.SOURCE["reserve"]
