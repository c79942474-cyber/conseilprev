# -*- coding: utf-8 -*-
"""La navigation entre les sept modules de « Cartographier », et son rail.

CE QUI ÉTAIT MESURÉ AVANT, dans un navigateur, sur les sept onglets du groupe
« Cartographier » de la barre latérale de Sentinel :

    au chargement               0 / 7 onglets portent une pastille
    après ouverture d'un écran  0 / 7  — `data-rail` absent partout
    contour de l'onglet         `border-width` = 0px sur TOUS les états
    registre rempli             le rail dit « aucun système déclaré »
    écran de qualification vu   le rail dit « ouvrez l'écran, le lot n'a pas
                                  encore été demandé au moteur »

Quatre défauts distincts, tous mesurés :

1. LE GROUPE N'A PAS DE TIROIR. Le rail se peignait à l'ouverture d'un tiroir
   (`aria-expanded`) ou d'un écran. « Cartographier » est un en-tête sans
   tiroir : ses sept onglets sont visibles d'emblée, donc rien ne les peignait
   jamais tant qu'on n'avait pas cliqué au hasard dans l'un d'eux.
2. L'ÉTAT NE VIVAIT QUE DANS LA PASTILLE — 18 px au bout d'une ligne de menu.
   L'onglet lui-même n'avait aucun contour, et aucun signal ne disait « celui-ci
   vient d'être rempli ».
3. `regCompleteness` VIVAIT DANS `regRender`, et `regFetch` l'appelait : la
   ReferenceError était avalée par le `.catch` de `regFetch` en « Erreur de
   chargement », la table du registre ne s'affichait plus, et le rail ne
   recevait jamais les systèmes.
4. LA ROUTE DES PROPOSITIONS NE COMPTAIT PAS CE QUI RESTE À CLASSER. Le dépôt
   lisait `restants`, une clé que cette route ne renvoie pas (elle appartient à
   la route qui PROPOSE, où elle désigne le reste d'un lot).

APRÈS, même parcours mesuré au navigateur, les sept modules remplis l'un après
l'autre :

    au chargement, rien d'ouvert   7 / 7 peints, étape 1 bleue et clignotante,
                                   les 3 dépendants en orange verrouillé
    « j'ai lu » sur Shadow AI       → vert, CLIGNOTEMENT VERT, passage immédiat
    simulateur rempli               → vert + « Passage à Systèmes IA dans 3 s »
    un système complet au registre  → vert, et les 3 verrous tombent
    qualification, FinOps, empreinte, maturité → verts l'un après l'autre
    fin                             7 blocs faits sur 7 · « Parcours terminé »
                                    · « ce n'est pas une conformité »
    erreurs de page                 aucune
"""
import io
import json
import os
import re
import shutil
import subprocess

import pytest

import parcours_normes
import qualification_assistee

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE = shutil.which("node")


def _lire(nom):
    with io.open(os.path.join(RACINE, nom), encoding="utf-8") as f:
        return f.read()


ECRAN = _lire("sentinel.page.js")
VUE = _lire("sentinel.html")
SERVEUR = _lire("app.py")


def _bloc(texte, depuis, jusqu_a):
    i = texte.index(depuis)
    return texte[i:texte.index(jusqu_a, i)]


def _noeud(prog):
    if not NODE:
        pytest.skip("node absent")
    r = subprocess.run([NODE, "-e", prog], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-900:]
    return json.loads(r.stdout.strip())


#: Une déclaration complète : les sept blocs ont ce qu'ils attendent.
PLEIN = {
    "lus": ["shadow-ai"],
    "simulateur": {"nom": "Assistant de tri", "secteur": "Services",
                   "type": "Traitement du langage", "niveau": "limite"},
    "registre": {"systemes": [{"nom": "Assistant de tri", "completude": 100}]},
    "qualification": {"a_qualifier": 0},
    "finops": {"couverture": {"total": 1, "instruites": 1, "non_chiffres": []}},
    "empreinte": {"couverture": {"systemes": 1, "chiffrable": 1,
                                 "volume_manquant": []}},
    "maturite": {"repondues": 16, "total": 16},
}

#: Les trois écrans qui ne se remplissent PAS chez eux : ils lisent le registre.
DEPENDANTS = ("qualification", "finops", "empreinte")


def _etats(declaration):
    av = parcours_normes.avancement("cartographier", declaration)
    return {b["cle"]: b["etat"] for b in av["blocs"]}, av


# ── 1. LE MOTEUR : SEPT BLOCS, ET UN VERROU QUI SE MOTIVE ────────────────

def test_le_parcours_cartographier_a_sept_blocs_dans_l_ordre_de_la_barre():
    av = parcours_normes.avancement("cartographier", {})
    assert av["ok"] is True
    assert [b["cle"] for b in av["blocs"]] == [
        "shadow", "simulateur", "registre", "qualification", "finops",
        "empreinte", "maturite"]
    assert [b["panneau"] for b in av["blocs"]] == [
        "shadow-ai", "simulateur", "registre", "qualif-assistee", "finops",
        "empreinte-ia", "maturite"]


def test_rien_de_rempli_ne_donne_aucun_vert_et_designe_le_premier_ecran():
    etats, av = _etats({})
    assert av["faits"] == 0 and av["total"] == 7
    assert etats["shadow"] == "courante"
    assert av["suivant"] == "simulateur"
    assert not [c for c, e in etats.items() if e in ("validee", "lue")]


@pytest.mark.parametrize("cle", DEPENDANTS)
def test_les_trois_ecrans_qui_lisent_le_registre_sont_verrouilles_sans_lui(cle):
    """UN VERROU QUI NE DIT PAS SUR QUOI IL PORTE est une porte fermée sans
    serrure : le client cherche ce qu'il n'a pas fait."""
    etats, _ = _etats({})
    assert etats[cle] == "verrouillee"
    bloc = [b for b in parcours_normes.avancement("cartographier", {})["blocs"]
            if b["cle"] == cle][0]
    assert "Registre IA" in (bloc.get("motif") or ""), bloc.get("motif")


@pytest.mark.parametrize("cle", DEPENDANTS)
def test_le_verrou_tombe_quand_le_registre_est_rempli(cle):
    """ET IL TOMBE SUR LE REGISTRE, PAS SUR L'ÉCRAN LUI-MÊME : un système
    déclaré suffit à ouvrir les trois, même si aucun des trois n'a été vu."""
    d = dict(PLEIN)
    d["qualification"], d["finops"], d["empreinte"] = {}, {}, {}
    etats, _ = _etats(d)
    assert etats["registre"] == "validee"
    assert etats[cle] != "verrouillee", (
        "« %s » reste verrouillé alors que le registre est rempli" % cle)


def test_un_registre_vide_dit_qui_d_autre_en_depend():
    bloc = [b for b in parcours_normes.avancement("cartographier", {})["blocs"]
            if b["cle"] == "registre"][0]
    quoi = " ".join(m["quoi"] for m in bloc["manque"])
    for autre in ("FinOps", "Empreinte", "qualification"):
        assert autre in quoi, quoi


# ── 2. LE VERT, ET CE QU'IL NE DIT PAS ───────────────────────────────────

def test_les_sept_blocs_remplis_donnent_sept_faits_sur_sept():
    etats, av = _etats(PLEIN)
    assert av["faits"] == 7 and av["part"] == 100
    assert av["fini"] is True
    assert etats["shadow"] == "lue"
    assert [c for c, e in etats.items() if e == "validee"] != []


def test_la_conclusion_refuse_de_dire_conformite():
    """« CARTOGRAPHIER » N'EST PAS UNE CONFORMITÉ : c'est un inventaire, et
    personne ne prononce sa validité. Le parcours terminé doit le dire, sinon
    sept pastilles vertes se liraient comme un quitus."""
    av = parcours_normes.avancement("cartographier", PLEIN)
    assert "inventaire" in av["conclusion"]
    assert "n'est pas une conformité" in av["conclusion"]
    assert "inventaire" in av["reserve"]


@pytest.mark.parametrize("bloc,cle,couverture,attendu", [
    ("finops", "finops",
     {"total": 2, "instruites": 1, "non_chiffres": ["Chatbot RH"]},
     ["Chatbot RH", "modèle", "Registre IA"]),
    ("empreinte", "empreinte",
     {"systemes": 2, "chiffrable": 1, "volume_manquant": ["Chatbot RH"]},
     ["Chatbot RH", "Registre IA"]),
])
def test_le_manque_nomme_le_systeme_ET_l_ecran_ou_le_remplir(bloc, cle, couverture, attendu):
    """C'EST LA QUESTION QUI A ÉTÉ POSÉE : « on ne sait pas quelles données
    choisir ». Dire « couverture 50 % » sans dire où saisir la laisse entière."""
    d = dict(PLEIN)
    d[cle] = {"couverture": couverture}
    b = [x for x in parcours_normes.avancement("cartographier", d)["blocs"]
         if x["cle"] == bloc][0]
    quoi = " ".join(m["quoi"] for m in b["manque"])
    assert b["etat"] != "validee"
    for mot in attendu:
        assert mot in quoi, quoi


def test_un_ecran_jamais_ouvert_le_dit_au_lieu_de_supposer_un_parc_vide():
    """AUCUN DÉPÔT N'EST PAS UN PARC À ZÉRO. Supposer l'un pour l'autre
    peindrait un vert — ou un rouge — sur une mesure jamais faite."""
    d = dict(PLEIN)
    d["finops"] = {}
    b = [x for x in parcours_normes.avancement("cartographier", d)["blocs"]
         if x["cle"] == "finops"][0]
    assert b["etat"] != "validee"
    assert "Ouvrez l'écran" in " ".join(m["quoi"] for m in b["manque"])


# ── 3. CE QUI RESTE À CLASSER, COMPTÉ UNE SEULE FOIS ─────────────────────

@pytest.mark.parametrize("valeur", [None, "", "  ", "a_evaluer"])
def test_une_classification_non_prononcee_compte_dans_ce_qui_reste(valeur):
    assert qualification_assistee.sans_classification(
        {"classification": valeur}) is True


@pytest.mark.parametrize("valeur", ["limite", "haut_risque", "minimal",
                                    "interdit"])
def test_une_classification_prononcee_ne_compte_plus(valeur):
    assert qualification_assistee.sans_classification(
        {"classification": valeur}) is False


def test_un_systeme_sans_colonne_de_classification_reste_a_classer():
    assert qualification_assistee.sans_classification({}) is True


def test_la_definition_python_et_le_sql_de_la_route_qui_propose_s_accordent():
    """DEUX EXPRESSIONS DU MÊME LOT DÉRIVERAIENT. La route qui propose vise ce
    qui n'est pas classé en SQL ; le comptage du rail le fait en Python. Cette
    règle casse si l'une des deux nomme une valeur que l'autre ignore."""
    sql = _bloc(SERVEUR,
                "# LE DEFAUT VISE CE QUI N'EST PAS CLASSE",
                "lignes = cur.fetchall()")
    valeurs = set(re.findall(r"classification='([^']*)'", sql))
    assert valeurs, sql[:400]
    assert valeurs == set(qualification_assistee.CLASSES_NON_PRONONCEES), (
        "le SQL vise %s, le module %s"
        % (sorted(valeurs), sorted(qualification_assistee.CLASSES_NON_PRONONCEES)))
    assert "classification IS NULL" in sql


def test_la_route_qui_liste_les_propositions_compte_ce_qui_reste_a_classer():
    """LE DÉFAUT MESURÉ : elle ne renvoyait ni `restants` ni rien d'équivalent,
    et le rail répétait « ouvrez l'écran » à qui venait de l'ouvrir."""
    corps = _bloc(SERVEUR, "def api_qualif_propositions():",
                  "@app.route('/api/qualification/<int:prop_id>/decider'")
    assert "'a_qualifier': a_qualifier" in corps
    assert "qualification_assistee.sans_classification" in corps, (
        "le comptage réinvente sa définition au lieu de lire celle du module")


def test_le_depot_du_rail_lit_la_cle_que_la_route_renvoie():
    depot = _bloc(ECRAN, "function qualifCharger() {", "qualifPeindre();")
    assert "d.a_qualifier" in depot
    assert "d.restants" not in depot, (
        "le dépôt lit encore `restants`, qui appartient à la route qui propose")


# ── 4. LA BARRE SE PEINT SANS QU'ON AIT À DEVINER OÙ CLIQUER ─────────────

def test_les_sept_onglets_de_cartographier_declarent_leur_parcours():
    items = re.findall(r'<div class="sb-item"[^>]*data-grp="cartographier"[^>]*>', VUE)
    assert len(items) == 7, len(items)
    for it in items:
        assert 'data-norme="cartographier"' in it, it[:120]


def test_un_groupe_sans_tiroir_recoit_son_rail_des_le_chargement():
    """LE DÉFAUT MESURÉ : 0 pastille sur 7 au chargement. Le rail attendait
    l'ouverture d'un tiroir ; « Cartographier » n'en a pas."""
    init = _bloc(ECRAN, "function railInit(apres) {", "if (document.readyState")
    assert "railGroupesDeployes()" in init


def test_le_groupe_deploye_est_celui_qui_n_a_pas_d_aria_expanded():
    """ET UNE DEMANDE PAR NORME, PAS UNE PAR ONGLET : sept onglets de
    « Cartographier » valent un seul appel au moteur — le limiteur du serveur
    coupe à cent vingt requêtes par minute."""
    corps = _bloc(ECRAN, "function railGroupesDeployes() {",
                  "window.railGroupesDeployes")
    prog = """
      var demandes = [];
      function railDemander(n, vite){ demandes.push([n, !!vite]); }
      function _faux(grp, expanded, normes){
        var items = normes.map(function(n){
          return { getAttribute: function(k){ return k === 'data-norme' ? n : null; },
                   classList: { contains: function(){ return false; } } };
        });
        items.forEach(function(it, i){ it.nextElementSibling = items[i + 1] || null; });
        return { hasAttribute: function(k){ return expanded; },
                 nextElementSibling: items[0] };
      }
      var sections = [
        _faux('cartographier', false, ['cartographier','cartographier','cartographier']),
        _faux('normes', true, ['nis2','iso27001'])
      ];
      var document = { querySelectorAll: function(){ return sections; } };
      var window = {};
      %s
      railGroupesDeployes();
      console.log(JSON.stringify(demandes));
    """ % corps
    assert _noeud(prog) == [["cartographier", True]]


# ── 5. L'ÉTAT SE VOIT SUR L'ONGLET, ET LE PASSAGE AU VERT SE REMARQUE ────

#: Ce que chaque état pose sur l'onglet lui-même — pas sur sa pastille.
FILETS = {"validee": "--green", "lue": "--green",
          "courante": "--blue", "verrouillee": "--orange"}


@pytest.mark.parametrize("etat", sorted(FILETS))
def test_chaque_etat_pose_un_filet_visible_sur_l_onglet(etat):
    """LE DÉFAUT MESURÉ : `border-width` valait 0px sur tous les états, donc
    aucun contour. Le filet est en `box-shadow` intérieur, et pas en bordure :
    une bordure décalerait les sept lignes au premier état peint."""
    regle = re.search(
        r'\.sb-nav \.sb-item\[data-rail="%s"\]\{([^}]*)\}' % etat, VUE)
    assert regle, "aucun filet pour l'état « %s »" % etat
    corps = regle.group(1)
    assert "box-shadow:inset 2px 0 0 0 var(%s)" % FILETS[etat] in corps, corps
    assert "border:" not in corps and "border-width" not in corps, corps


def test_le_vert_plein_reste_le_vert_du_valide_et_pas_celui_du_lu():
    """« LU » N'EST PAS « VALIDÉ », et la doctrine du rail le dit. Le filet vert
    signale qu'un écran de lecture est fait ; le fond plein reste au bloc dont
    une déclaration a été mesurée."""
    assert re.search(r'\.sb-item\[data-rail="validee"\] \.rail-puce\{[^}]*'
                     r'background:var\(--green\)', VUE)
    lue = re.search(r'\.sb-item\[data-rail="lue"\] \.rail-puce\{([^}]*)\}', VUE)
    assert lue and "background:var(--green)" not in lue.group(1), lue


def test_le_clignotement_vert_s_arrete_et_respecte_le_mouvement_reduit():
    """SEPT ONGLETS VERTS QUI CLIGNOTENT EN PERMANENCE NE SIGNALENT PLUS RIEN :
    ce qui se remarque est le passage au vert. Trois battements, puis le filet."""
    regle = re.search(r'\.sb-nav \.sb-item\.rail-fete\{([^}]*)\}', VUE)
    assert regle, "aucun clignotement au passage au vert"
    assert re.search(r'animation:rail-fete [^;}]*\b3\b', regle.group(1)), regle.group(1)
    assert "@keyframes rail-fete{" in VUE
    reduit = _bloc(VUE, '.sb-item[data-rail="courante"] .rail-puce{animation:none',
                   "\n}\n/* \u2500\u2500 CE QUI MANQUE")
    assert ".sb-nav .sb-item.rail-fete" in reduit, reduit
    assert reduit.count("animation:none") >= 2, reduit


def test_le_clignotement_part_au_changement_d_etat_et_pas_a_chaque_repeint():
    """LA BARRE SE REPEINT À CHAQUE RÉPONSE. Un clignotement posé sans
    comparer l'état précédent repartirait à chaque frappe de clavier."""
    corps = (_bloc(ECRAN, "var RAIL_FETE = {};", "window.railPeindreBarre")
             .replace("function railPeindreBarre(norme, p) {",
                      "function peindre(norme, p) {", 1))
    prog = """
      var fetes = [];
      function setTimeout(f, ms){ return 0; }
      function clearTimeout(){}
      function _railPanneau(it){ return it.panneau; }
      function railBulle(){ return 'bulle'; }
      var faux = {
        panneau: 'registre', rail: null,
        classList: { remove: function(){}, add: function(){ fetes.push(1); },
                     contains: function(){ return false; } },
        offsetWidth: 1,
        querySelector: function(){ return this.puce || null; },
        appendChild: function(p){ this.puce = p; },
        getAttribute: function(k){ return k === 'data-rail' ? this.rail : null; },
        setAttribute: function(k, v){ if (k === 'data-rail') this.rail = v; },
        removeAttribute: function(){ this.rail = null; }
      };
      var document = { querySelectorAll: function(){ return [faux]; },
                       createElement: function(){
                         return { className: '', textContent: '',
                                  setAttribute: function(){}, };
                       } };
      var window = {};
      %s
      var p = function(etat){
        return { blocs: [{ cle: 'registre', panneau: 'registre', etat: etat,
                           nom: 'Systèmes IA', rang: 3, manque: [] }],
                 etats: { attente: { nom: 'Pas encore atteint', puce: '\\u25cb' },
                          validee: { nom: 'Validé', puce: '\\u2713' } } };
      };
      peindre('cartographier', p('attente'));   /* premier peint : pas de fête */
      var apres_premier = fetes.length;
      peindre('cartographier', p('validee'));   /* passage au vert : une fête */
      var au_passage = fetes.length;
      peindre('cartographier', p('validee'));   /* repeint identique : rien */
      console.log(JSON.stringify([apres_premier, au_passage, fetes.length,
                                  faux.rail]));
    """ % corps
    assert _noeud(prog) == [0, 1, 1, "validee"], (
        "le clignotement ne suit pas le CHANGEMENT d'état")


# ── 6. LE REGISTRE ARRIVE VRAIMENT AU RAIL ───────────────────────────────

def test_la_completude_d_une_fiche_est_atteignable_hors_de_regRender():
    """LE DÉFAUT MESURÉ. `regCompleteness` vivait dans `regRender` ; `regFetch`
    l'appelait, la ReferenceError tombait dans son `.catch`, et l'écran
    affichait « Erreur de chargement » au lieu de la table du registre."""
    assert "\nfunction regCompleteness(s){" in ECRAN, (
        "regCompleteness n'est pas déclarée au premier niveau de son bloc")
    assert ECRAN.index("function regCompleteness(s){") < ECRAN.index(
        "function regFetch(){")
    corps = _bloc(ECRAN, "function regRender(){", "window.regSearch")
    assert "function regCompleteness" not in corps, (
        "regCompleteness est de nouveau enfermée dans regRender")


def test_le_depot_porte_la_meme_completude_que_la_pastille_de_la_ligne():
    """LE VRAI CODE, EXÉCUTÉ : les dix questions essentielles comptées une
    fois, pour l'écran comme pour le rail."""
    corps = _bloc(ECRAN, "function regCompleteness(s){", "function regFetch(){")
    prog = """
      var depose = null;
      var window = { cartoDeposer: function(cle, v){ depose = [cle, v]; } };
      var REG_DATA = [
        { nom: 'Complet', service: 'RC', finalite: 'trier',
          donnees_utilisees: 'courriels', personnes_concernees: 'clients',
          roles: ['deployeur'], transparence_art50: 'oui',
          classification: 'limite', preuves_conformite: 'note',
          fournisseur: 'éditeur' },
        { nom: 'À moitié', service: 'RC', finalite: 'trier',
          donnees_utilisees: 'courriels', personnes_concernees: 'clients',
          roles: [], transparence_art50: 'a_evaluer',
          classification: 'a_evaluer', preuves_conformite: '',
          fournisseur: '' }
      ];
      %s
      regDeposerAuRail();
      console.log(JSON.stringify(depose));
    """ % corps
    cle, valeur = _noeud(prog)
    assert cle == "cartographier" if cle != "registre" else True
    assert cle == "registre", cle
    assert valeur["systemes"] == [{"nom": "Complet", "completude": 100},
                                  {"nom": "À moitié", "completude": 50}], valeur


def test_le_chargement_du_registre_depose_vraiment_au_rail():
    """LE DÉFAUT D'ORIGINE, REJOUÉ : `regFetch` appelait `regCompleteness`
    depuis une portée où elle n'existait pas. La ReferenceError tombait dans
    son `.catch`, l'écran affichait « Erreur de chargement » — et le rail ne
    recevait rien. Ici le VRAI `regFetch` tourne, avec le registre pour seule
    entrée : ce que le rail reçoit est mesuré, pas déduit du texte du code."""
    corps = _bloc(ECRAN, "function regCompleteness(s){", "function regFilteredData(){")
    prog = """
      var depose = null, erreur = null;
      var window = {
        cartoDeposer: function(cle, v){ depose = [cle, v]; },
        sentRegistre: function(){
          return Promise.resolve({ systemes: [
            { nom: 'Complet', service: 'RC', finalite: 'trier',
              donnees_utilisees: 'courriels', personnes_concernees: 'clients',
              roles: ['deployeur'], transparence_art50: 'oui',
              classification: 'limite', preuves_conformite: 'note',
              fournisseur: 'éditeur' }] });
        }
      };
      var document = { getElementById: function(){
        return { set innerHTML(v){ erreur = v; } }; } };
      var REG_DATA = [];
      function regSkeletonHTML(){ return ''; }
      function regRender(){}
      %s
      regFetch();
      setTimeout(function(){
        console.log(JSON.stringify({ depose: depose, erreur: erreur }));
      }, 30);
    """ % corps
    r = _noeud(prog)
    assert r["depose"], (
        "le chargement du registre ne dépose rien au rail — erreur d'écran : %r"
        % r["erreur"])
    cle, valeur = r["depose"]
    assert cle == "registre"
    assert valeur["systemes"] == [{"nom": "Complet", "completude": 100}], valeur
    assert "Erreur de chargement" not in (r["erreur"] or ""), r["erreur"]


#: Les trois moments où le registre change, et que le rail doit apprendre.
MUTATIONS = {
    "chargement": ("REG_DATA = d.systemes || [];", "regRender();"),
    "enregistrement": ("        REG_DATA.unshift(d.systeme);\n      }", "regRender();"),
    "suppression": ("REG_DATA = REG_DATA.filter(function(s){ return s.id !== id; });",
                    "regRender();"),
}


@pytest.mark.parametrize("moment", sorted(MUTATIONS))
def test_le_rail_apprend_chaque_changement_du_registre(moment):
    """L'ÉCRAN MODIFIE `REG_DATA` SUR PLACE pour éviter un aller-retour réseau :
    sans dépôt à cet endroit, le rail resterait sur la liste d'avant, et le vert
    d'un module rempli n'arriverait qu'au rechargement de la page."""
    depuis, jusqu_a = MUTATIONS[moment]
    corps = _bloc(ECRAN, depuis, jusqu_a)
    assert "regDeposerAuRail()" in corps, (
        "le rail n'apprend pas le changement du registre au moment « %s »" % moment)


# ── 7. LE COLLECTEUR : CE QUE LE NAVIGATEUR ENVOIE AU MOTEUR ─────────────

def test_le_collecteur_rassemble_les_sept_ecrans_sans_rien_fabriquer():
    """UN ÉCRAN JAMAIS OUVERT NE DÉPOSE RIEN, et le collecteur ne comble pas :
    le moteur dira « ouvrez l'écran », ce qui est vrai."""
    corps = _bloc(ECRAN, "  cartographier: function () {", "  nis2: function () {")
    prog = """
      var CARTO_ETAT = {
        registre: { systemes: [{ nom: 'X', completude: 100 }] },
        qualification: { a_qualifier: 0 }
      };
      var window = {
        simDonnees: function(){ return { name: 'X', secteur: 'S', type: 'T' }; },
        simClassifier: function(){ return { level: 'limite' }; },
        matGetCur: function(){ return 'services'; },
        matRepondu: function(){ return { repondues: 16, total: 16 }; }
      };
      var RAIL_DECL = { %s nis2: function () {} };
      console.log(JSON.stringify(RAIL_DECL.cartographier()));
    """ % corps
    d = _noeud(prog)
    assert d["simulateur"] == {"nom": "X", "secteur": "S", "type": "T",
                              "niveau": "limite"}
    assert d["registre"]["systemes"] == [{"nom": "X", "completude": 100}]
    assert d["qualification"] == {"a_qualifier": 0}
    assert d["finops"] == {} and d["empreinte"] == {}
    assert d["maturite"] == {"repondues": 16, "total": 16}


def test_ce_que_le_collecteur_rend_est_ce_que_le_moteur_sait_lire():
    """LES DEUX CÔTÉS BRANCHÉS, MESURÉS ENSEMBLE : la déclaration que le
    navigateur compose passe dans le VRAI moteur, et rend les sept blocs."""
    corps = _bloc(ECRAN, "  cartographier: function () {", "  nis2: function () {")
    prog = """
      var CARTO_ETAT = {
        registre: { systemes: [{ nom: 'X', completude: 100 }] },
        qualification: { a_qualifier: 0 },
        finops: { couverture: { total: 1, instruites: 1, non_chiffres: [] } },
        empreinte: { couverture: { systemes: 1, chiffrable: 1, volume_manquant: [] } }
      };
      var window = {
        simDonnees: function(){ return { name: 'X', secteur: 'S', type: 'T' }; },
        simClassifier: function(){ return { level: 'limite' }; },
        matGetCur: function(){ return 'services'; },
        matRepondu: function(){ return { repondues: 16, total: 16 }; }
      };
      var RAIL_DECL = { %s nis2: function () {} };
      var d = RAIL_DECL.cartographier();
      d.lus = ['shadow-ai'];
      console.log(JSON.stringify(d));
    """ % corps
    d = _noeud(prog)
    av = parcours_normes.avancement("cartographier", d)
    assert av["ok"] is True
    assert av["faits"] == 7, [(b["cle"], b["etat"], b["manque"]) for b in av["blocs"]]
    assert av["fini"] is True


def test_un_depot_repeint_la_barre_sans_attendre_le_prochain_ecran():
    porte = _bloc(ECRAN, "window.cartoDeposer = function (cle, valeur) {",
                  "var RAIL_DECL = {")
    assert "railDemander('cartographier')" in porte
