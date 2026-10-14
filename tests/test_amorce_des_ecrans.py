# -*- coding: utf-8 -*-
"""L'AMORCE D'UN ÉCRAN DE SENTINEL, ET LE CHEMIN PAR LEQUEL ON Y ENTRE.

CE QUI A DÉCLENCHÉ CE FICHIER. Une demande : « lorsqu'on clique sur une des
16 normes maîtrisées dans Sentinel, il faut que l'on se connecte directement
sur la norme concernée et qu'elle soit affichée à l'écran. »

CE QUE LA MESURE A TROUVÉ, ET CE N'ÉTAIT PAS LÀ OÙ ON CHERCHAIT. Le clic sur
une carte de l'accueil marche : mesuré dans un navigateur, les seize mènent à
leur panneau, la porte reporte la destination, la page de connexion la rend et
l'écran se peint. Le défaut était un cran plus loin — sur les AUTRES chemins
vers le même écran :

    go(id) seul, sans passer par l'onglet     13 écrans sur 18 restaient
                                              sur « Chargement… », sans fin

    ia-act-hub · rgpd-hub · rgpd-traitements · rgpd-cartographie · rgpd-aipd
    nist-profil · nist-cadre · nist-genai · owasp-dix · owasp-pont
    nist53-socle · nist82-ot · juridique

    Les cinq autres (conformite-globale, rgpd-pbd, rgpd-doc,
    rgpd-sensibilisation, rgpd-conformite) ne disaient pas « Chargement… » :
    elles affichaient leur chapô et RIEN de leurs données. Un écran qui
    attend se voit ; un écran qui a renoncé ne se voit pas.

POURQUOI, ET POURQUOI C'EST LA SIXIÈME FOIS. L'amorce de chaque écran était
écrite DANS le `onclick` de son onglet (`;nistInit()`). Qui n'arrive pas par
l'onglet n'amorce rien — et beaucoup n'arrivent pas par l'onglet : le bouton
« ↓ » du rail de validation et son passage automatique appellent `go()`
directement, les boutons « → » d'un écran vers un autre aussi, le pont des
deux règlements de données vers le RGPD aussi, et le repli du lien profond
`?goto=` également. Le dépôt avait déjà réparé ce défaut cinq fois, famille
par famille : DORA, prEN 18286, les trois écrans du taux, l'OCDE, les sept de
« Données & Partage ». Les commentaires de `go()` le racontent cinq fois.

CE QUE CES RÈGLES GARDENT, ET POURQUOI EN CE POINT-LÀ. Elles ne listent pas
les dix-huit : une liste serait la dix-neuvième chose à tenir à jour. Elles
gardent le MÉCANISME qui rend la liste inutile — `go()` rejoue ce que
l'onglet aurait fait —, et elles gardent les deux conditions sans lesquelles
ce mécanisme serait faux :

  1. il ne joue PAS quand on arrive par l'onglet (sinon chaque amorce
     partirait deux fois, et le référentiel avec) ;
  2. aucune amorce d'onglet ne nomme une fonction qui n'existe pas — un
     onglet qui appelle un nom mort ouvre un écran vide sans rien signaler.

ET CE QU'ELLES NE PEUVENT PAS FAIRE. Dire ce qu'un écran MONTRE. C'est
`outils/recette_normes_maitrisees.js` qui l'ouvre dans un vrai navigateur et
lit le texte peint ; ces règles-ci vérifient que le mécanisme tient.
"""
import io
import os
import re
import sys

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RACINE not in sys.path:
    sys.path.insert(0, _RACINE)

SENTINEL = io.open(os.path.join(_RACINE, "sentinel.html"), encoding="utf-8").read()
JS = io.open(os.path.join(_RACINE, "sentinel.page.js"), encoding="utf-8").read()


def _corps_de_go():
    """LE CORPS DE `go()`, ET PAS LE FICHIER ENTIER. Chercher une amorce dans
    1,4 Mo de JavaScript la trouverait partout : c'est dans `go()` qu'elle
    doit être, puisque c'est `go()` que tous les chemins traversent."""
    d = JS.index("function go(id, el, sec, pg) {")
    m = re.search(r"\n\}\n", JS[d:])
    assert m, "la fin du corps de go() n'est plus reconnaissable"
    return JS[d:d + m.start()]


CORPS = _corps_de_go()


def _entrees_de_barre():
    """Les entrées de la barre latérale, avec le panneau visé et les appels
    SANS ARGUMENT écrits après `go(...)` — c'est-à-dire leurs amorces."""
    out = []
    for oc in re.findall(r'class="sb-item[^"]*"[^>]*onclick="([^"]+)"', SENTINEL):
        m = re.match(r"go\('([^']+)'", oc)
        if not m:
            continue
        noms = [n for n in re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(\s*\)", oc)
                if n != "go"]
        out.append((m.group(1), oc, noms))
    return out


ENTREES = _entrees_de_barre()


def test_la_lecture_de_la_barre_n_est_pas_vide():
    """LE GARDE-FOU DES RÈGLES SUIVANTES. Une lecture qui rendrait zéro entrée
    ferait passer toutes les boucles ci-dessous pour des boucles vides — et
    c'est arrivé une fois dans ce dépôt, recette verte comprise."""
    assert len(ENTREES) > 80, (
        "%d entrée(s) de barre lues : la barre latérale ne se lit plus"
        % len(ENTREES))
    porteuses = [e for e in ENTREES if e[2]]
    assert len(porteuses) > 10, (
        "%d entrée(s) portent une amorce : la lecture des amorces ne marche "
        "plus" % len(porteuses))


# ═══════════════════════════════════════════════════════════════════════════
#  1. LE MÉCANISME — `go()` REJOUE CE QUE L'ONGLET AURAIT FAIT
# ═══════════════════════════════════════════════════════════════════════════

def test_go_rejoue_l_amorce_ECRITE_DANS_L_ONGLET_de_l_ecran_qu_il_ouvre():
    """CE QUI REMPLACE DIX-HUIT LIGNES À ÉCRIRE UNE PAR UNE. `go()` retrouve
    l'onglet de l'écran, lit son `onclick`, et programme les appels sans
    argument qui y sont écrits. Un dix-neuvième écran est couvert le jour où
    on l'ajoute, sans rien ajouter ici."""
    assert "if (!el) (function () {" in CORPS, (
        "l'amorce générique a disparu de go() : treize écrans retombent sur "
        "« Chargement… » dès qu'on y entre autrement que par l'onglet")
    d = CORPS.index("if (!el) (function () {")
    bloc = CORPS[d:CORPS.index("})();", d)]
    assert ".sb-item[onclick*=" in bloc and "+ id +" in bloc, (
        "l'amorce générique ne cherche plus l'onglet de l'écran ouvert : %r"
        % bloc[:200])
    assert "getAttribute('onclick')" in bloc, (
        "l'amorce générique ne lit plus le onclick de l'onglet")
    assert re.search(r"\(\?=\\s\*\\\(\\s\*\\\)\)", bloc), (
        "l'amorce générique ne relève plus les appels SANS ARGUMENT : elle "
        "reprendrait des appels dont elle n'a pas les arguments — %r" % bloc)
    assert "window[nom]" in bloc, (
        "l'amorce générique ne cherche plus la fonction par son nom")
    assert "_amorcer(f)" in bloc, (
        "l'amorce générique ne passe plus par le mémo : chaque référentiel "
        "repartirait deux fois")


def test_l_amorce_generique_REFUSE_un_identifiant_qui_n_est_pas_un_panneau():
    """CE QUE `?goto=` PEUT METTRE DANS UN SÉLECTEUR CSS, ET IL VIENT DE L'URL.
    `go(id)` reçoit la valeur du paramètre telle quelle ; l'amorce générique la
    pose dans `.sb-item[onclick*="go('<id>'"]`. Une apostrophe ou un crochet y
    rend le sélecteur invalide, `querySelector` LÈVE, et `go()` s'arrête — sur
    une page dont les panneaux ont déjà été décrochés, c'est-à-dire sur un
    écran vide, par un lien que n'importe qui peut fabriquer."""
    d = CORPS.index("if (!el) (function () {")
    bloc = CORPS[d:CORPS.index("})();", d)]
    assert "/^[A-Za-z0-9_-]+$/.test(String(id))" in bloc, (
        "l'amorce générique ne vérifie plus la forme de l'identifiant avant "
        "de le poser dans un sélecteur CSS : %r" % bloc[:260])
    #  ON COMPARE DEUX POSITIONS DANS LE CODE, PAS DANS LE COMMENTAIRE. La
    #  première version cherchait « querySelector », qui apparaît aussi dans
    #  l'explication juste au-dessus : la règle comparait alors la garde à une
    #  mention en prose et tombait sur un code juste.
    i = bloc.index("test(String(id))")
    j = bloc.index("document.querySelector")
    assert i < j, (
        "la vérification de l'identifiant vient APRÈS le sélecteur : elle "
        "n'empêche rien")


def test_l_amorce_generique_NE_JOUE_PAS_quand_on_arrive_par_l_onglet():
    """LA CONDITION SANS LAQUELLE LE MÉCANISME SERAIT FAUX. L'onglet exécute
    DÉJÀ sa propre amorce, juste après `go()`. Si `go()` la rejouait aussi,
    chaque ouverture partirait deux fois sur le réseau — et le limiteur du
    serveur (120 requêtes par minute et par adresse) ferme le site entier
    quand il mord, pas seulement l'écran fautif.

    `el` SUFFIT À DISTINGUER LES DEUX CAS, et c'est mesuré ci-dessous : les
    onglets passent `this`, les autres appelants passent `null` ou rien."""
    assert "if (!el) (function () {" in CORPS, (
        "l'amorce générique n'est plus conditionnée à l'absence de `el` : "
        "elle doublerait l'amorce de l'onglet")
    sans_this = [p for p, oc, noms in ENTREES
                 if noms and not re.match(r"go\('[^']+',\s*this\b", oc)]
    assert not sans_this, (
        "ces onglets ne passent pas `this` à go() : l'amorce générique s'y "
        "ajouterait à la leur — %s" % sans_this)


def test_le_memo_interdit_la_DOUBLE_amorce_et_TOUTES_y_passent():
    """UN MÉMO QUE QUELQU'UN CONTOURNE NE SERT À RIEN. Les lignes explicites
    de `go()` visent des préfixes (`dora`, `conf-`…) qui recoupent ce que
    l'amorce générique trouve : sans mémo partagé, les deux mécanismes
    programmeraient la même fonction. La règle vérifie donc le mémo ET que
    plus aucune amorce ne passe directement par `_apresPeinture`."""
    assert "function _amorcer(f)" in CORPS, "le mémo des amorces a disparu"
    d = CORPS.index("function _amorcer(f)")
    memo = CORPS[d:CORPS.index("\n  }", d)]
    assert "_amorcees.indexOf(f)" in memo, (
        "le mémo ne refuse plus une amorce déjà programmée : %r" % memo)
    assert "typeof f !== 'function'" in memo, (
        "le mémo ne refuse plus un nom qui n'est pas une fonction : go() "
        "lèverait sur un onglet dont l'amorce a été renommée")
    assert "_apresPeinture(f)" in memo, (
        "le mémo ne programme plus rien après la peinture")
    directes = re.findall(r"_apresPeinture\(window\.[A-Za-z0-9_]+\)", CORPS)
    assert not directes, (
        "ces amorces contournent le mémo et partiront deux fois : %s"
        % directes)


# ═══════════════════════════════════════════════════════════════════════════
#  2. L'INVENTAIRE — AUCUN ONGLET N'APPELLE UN NOM MORT
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("panneau,noms", [(p, n) for p, _oc, n in ENTREES if n],
                         ids=[p for p, _oc, n in ENTREES if n])
def test_l_amorce_d_un_onglet_nomme_une_fonction_QUI_EXISTE(panneau, noms):
    """UN ONGLET QUI APPELLE UN NOM MORT OUVRE UN ÉCRAN VIDE, EN SILENCE.
    `onclick` avale la ReferenceError : la page s'affiche, le panneau reste
    sur son gabarit, et rien dans la console du serveur ne le dit. C'est
    exactement la forme qu'avait le défaut de `regCompleteness`, déjà payé
    dans ce dépôt."""
    for nom in noms:
        vu = ("window.%s =" % nom in JS or "window.%s=" % nom in JS
              or "function %s(" % nom in JS or "var %s =" % nom in JS)
        assert vu, (
            "l'onglet « %s » appelle %s(), qui n'est définie nulle part : "
            "l'écran s'ouvrira vide sans que rien ne le signale"
            % (panneau, nom))


# ═══════════════════════════════════════════════════════════════════════════
#  3. CE QUE LE RAIL DEMANDE — CHAQUE BLOC DE PARCOURS EST AMORÇABLE
# ═══════════════════════════════════════════════════════════════════════════

def _blocs_de_parcours():
    import parcours_normes as P
    out = []
    for norme, blocs in P.BLOCS.items():
        for b in blocs:
            pan = b.get("panneau") if isinstance(b, dict) else None
            if pan:
                out.append((norme, pan))
    return out


def test_chaque_bloc_de_parcours_est_AMORCABLE_par_go():
    """LE RAIL EST LE PREMIER APPELANT À NE PAS PASSER PAR L'ONGLET, et c'est
    lui qui a payé le défaut. Son bouton « ↓ », son passage automatique et son
    saut direct appellent `go(panneau)` sans élément : l'écran doit donc être
    amorçable par ce chemin-là.

    DEUX FAÇONS DE L'ÊTRE, et la règle accepte les deux : avoir un onglet
    (l'amorce générique le retrouve) ou être nommé dans une ligne explicite de
    `go()` (pour les écrans qui n'ont pas d'onglet du tout). Un bloc qui n'a
    ni l'un ni l'autre est un écran que le parcours ouvrira vide — et quatre
    des treize écrans mesurés muets étaient des blocs de SAISIE : un
    questionnaire qui ne se peint pas ne peut pas être rempli, donc le rail ne
    peut pas verdir, donc le taux de la norme ne peut pas monter."""
    blocs = _blocs_de_parcours()
    assert len(blocs) > 40, (
        "%d bloc(s) de parcours lus : la lecture de parcours_normes ne marche "
        "plus, et la règle ne mesure plus rien" % len(blocs))
    onglets = {p for p, _oc, _n in ENTREES}
    orphelins = []
    for norme, pan in blocs:
        if pan in onglets:
            continue
        if ("'%s'" % pan) in CORPS:
            continue
        orphelins.append((norme, pan))
    assert not orphelins, (
        "ces blocs de parcours ne sont amorçables par aucun chemin : %s. "
        "Le rail les ouvrira sur leur gabarit." % orphelins)
