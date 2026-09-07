# -*- coding: utf-8 -*-
"""L'AVANCEMENT D'UN PARCOURS GUIDÉ — ET LA PASTILLE QUI MENTAIT.

CE QUI A DÉCLENCHÉ CE FICHIER. Une demande : « lorsque l'on progresse dans un
parcours guidé avec un rôle choisi, afficher le parcours fini et validé en vert,
sinon en bleu pour dire qu'il est en cours, et intégrer des barres de
progression ».

CE QUE LA VÉRIFICATION A TROUVÉ AVANT D'AJOUTER QUOI QUE CE SOIT. Le bandeau
peignait déjà des pastilles, et il les peignait ainsi :

    dots += '<span class="gb-dot'+(k===i?' on':(k<i?' done':''))+'"></span>';

Autrement dit : TOUT CE QUI PRÉCÈDE L'ÉTAPE COURANTE était marqué fait, qu'on y
soit passé ou non. Ouvrir directement l'étape 3 d'un parcours de quinze en
colorait deux jamais vues. Rien ne levait — l'affichage était cohérent, et faux.
C'est la version visuelle du défaut poursuivi partout ailleurs dans ce dépôt :
une chose qui passe pour une raison sans rapport avec ce qu'elle prétend.

L'AVANCEMENT N'ÉTAIT NI MESURÉ NI CONSERVÉ. `window.__activeGuided` vivait en
mémoire : un rechargement de page effaçait tout, et la carte du parcours — celle
qu'on rouvre trois jours plus tard — ne portait aucun état.

CE QUE CES RÈGLES GARDENT
  · qu'une étape jamais ouverte ne soit JAMAIS marquée faite, et — témoin
    inverse — qu'une étape ouverte le soit ;
  · que le vert n'apparaisse qu'au complet, et qu'il porte sa réserve : il dit
    que chaque étape a été OUVERTE, pas que son travail a été fait ;
  · que les deux états se lisent sans couleur, l'échelle vert/bleu étant
    justement celle que la deutéranopie confond ;
  · qu'un seul endroit calcule l'état, et que les trois écrans l'appellent ;
  · qu'arriver sur un panneau par le menu ne fasse pas avancer un parcours
    qu'on ne suit pas.

CE QU'ELLES NE PEUVENT PAS FAIRE. Dire que le travail d'une étape a été fait.
Sentinel ne le mesure pas, et c'est précisément pourquoi le vert porte une
réserve écrite plutôt qu'une promesse muette.
"""
import io
import json
import os
import re
import shutil
import subprocess
import tempfile

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOTEUR = io.open(os.path.join(ICI, "sentinel.page.js"), encoding="utf-8").read()
PAGE = io.open(os.path.join(ICI, "sentinel.html"), encoding="utf-8").read()
NODE = shutil.which("node")


# ═══════════════════════════════════════════════════════════════════════════
#  LE HARNAIS — LE CODE EST EXÉCUTÉ, PAS LU
#
#  Une règle qui chercherait « parcoursEtapeVue » dans la source serait verte
#  le jour où le nom ne figurerait plus que dans un commentaire. Le bloc est
#  donc évalué sous node, avec le CATALOGUE RÉEL des parcours et un
#  `localStorage` de recette — c'est la seule façon de mesurer ce qui est peint.
# ═══════════════════════════════════════════════════════════════════════════

_SOCLE = r"""
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const deb = src.indexOf("(function(){\n  var CLE = 'cpParcoursVues';");
if (deb < 0) throw new Error("le moteur d'avancement est introuvable");
const fin = src.indexOf('window.guidedEndBanner = function()');
const bloc = src.slice(deb, fin);

const dCat = src.indexOf('var GUIDED_PATHS = [');
const fCat = src.indexOf('\n];', dCat) + 3;
const mil = src.match(/^var DC_MILLESIME = .*;$/m);
eval((mil ? mil[0] + '\n' : '') + src.slice(dCat, fCat));

const magasin = {};
const REFUSE = process.argv[4] === 'refuse';
global.localStorage = {
  getItem: function(k){ if (REFUSE) throw new Error('stockage refusé');
                        return k in magasin ? magasin[k] : null; },
  setItem: function(k, v){ if (REFUSE) throw new Error('stockage refusé');
                           magasin[k] = String(v); },
};
const zones = {};
function zone(id, select){
  if(zones[id]) return zones[id];
  const el = {id:id, style:{}, options:[], value:'',
    classList:{add:function(){},remove:function(){}},
    setAttribute:function(){}, removeAttribute:function(){}};
  let html = '';
  Object.defineProperty(el, 'innerHTML', {
    get: function(){ return html; },
    set: function(v){
      html = String(v);
      if(!select) return;
      /* DANS UN NAVIGATEUR, écrire innerHTML sur un <select> détruit ses
         options ET remet la valeur à vide. Un objet factice qui garderait sa
         valeur ferait passer une implémentation qui perd la sélection — le
         piège exact que ce fichier garde. */
      el.options = (html.match(/<option value="([^"]*)"/g) || []).map(function(m){
        return { value: m.slice('<option value="'.length, -1) };
      });
      el.value = '';
    }
  });
  zones[id] = el;
  return el;
}
global.document = {
  getElementById: function(id){ return zones[id] || null; },
  createElement: function(){ return zone('__cree'); },
  body: {appendChild: function(){}},
  querySelectorAll: function(){ return []; },
};
global.window = global;
global.GUIDED_PATHS = GUIDED_PATHS;
global.GP_FAMILLES = [];
global.guidedFindPath = function(id){
  return GUIDED_PATHS.filter(function(p){ return p.id === id; })[0] || null; };
global.guidedFiche = function(){ return ''; };
global.guidedPathsClose = function(){};
global.go = function(){ global.__vuParLeMenu = true; };
zone('guided-banner'); zone('sb-role', true); zone('guided-paths-list');
eval(bloc);
const P = GUIDED_PATHS[0];
const out = {};
"""


def _executer(scenario, stockage="ok"):
    if not NODE:
        pytest.skip("node absent : le moteur d'avancement ne peut pas être exécuté")
    with tempfile.TemporaryDirectory() as d:
        h = os.path.join(d, "h.js")
        io.open(h, "w", encoding="utf-8").write(
            _SOCLE + scenario + "\nprocess.stdout.write(JSON.stringify(out));\n")
        r = subprocess.run([NODE, h, os.path.join(ICI, "sentinel.page.js"), "", stockage],
                           capture_output=True, text=True, timeout=90)
    if r.returncode != 0:
        pytest.fail("le scénario n'a pas tourné :\n%s" % (r.stderr or "")[-1800:])
    return json.loads(r.stdout)


def _texte(html_):
    import html as _h
    return re.sub(r"\s+", " ", _h.unescape(re.sub(r"<[^>]+>", " ", html_)))


# ═══════════════════════════════════════════════════════════════════════════
#  1. LE DÉFAUT MESURÉ : UNE ÉTAPE JAMAIS OUVERTE N'EST PAS FAITE
# ═══════════════════════════════════════════════════════════════════════════

def test_LE_DEFAUT_MESURE_un_saut_direct_ne_marque_pas_faites_les_etapes_sautees():
    """LA RÈGLE CENTRALE. Avant, « k < i » devenait `done` : ouvrir l'étape 3
    colorait les étapes 1 et 2, jamais vues. Le scénario saute donc DIRECTEMENT
    à la troisième — un parcours suivi dans l'ordre ne distinguerait pas les
    deux implémentations."""
    r = _executer("""
      guidedStartStep(P.id, 2);
      out.bandeau = zones['guided-banner'].innerHTML;
      out.etat = parcoursEtat(P);
    """)
    assert r["etat"]["vues"] == 1, r["etat"]
    assert r["bandeau"].count("gb-dot done") == 0, (
        "%d pastille(s) marquées faites alors qu'une seule étape a été ouverte, "
        "et ce n'est pas l'une d'elles" % r["bandeau"].count("gb-dot done"))
    assert r["bandeau"].count("gb-dot on") == 1


def test_LE_TEMOIN_INVERSE_une_etape_reellement_ouverte_EST_marquee_faite():
    """Sans ce témoin, la règle précédente serait verte sur une implémentation
    qui ne marque JAMAIS rien — c'est-à-dire sur la suppression pure et simple
    de la fonctionnalité demandée."""
    r = _executer("""
      guidedStartStep(P.id, 0);
      guidedStartStep(P.id, 1);
      guidedStartStep(P.id, 3);
      out.bandeau = zones['guided-banner'].innerHTML;
    """)
    assert r["bandeau"].count("gb-dot done") == 2, (
        "deux étapes ouvertes précèdent la courante, elles doivent être "
        "marquées : %d le sont" % r["bandeau"].count("gb-dot done"))


def test_arriver_par_le_menu_ne_fait_pas_avancer_un_parcours_qu_on_ne_suit_pas():
    """Compter l'ouverture d'un panneau ferait progresser tous les parcours qui
    le contiennent, y compris ceux qu'on n'a jamais choisis — et le vert
    apparaîtrait sur un parcours jamais suivi."""
    r = _executer("""
      go('finops');
      out.etat = parcoursEtat(P);
    """)
    assert r["etat"]["vues"] == 0 and r["etat"]["statut"] == "neuf"


# ═══════════════════════════════════════════════════════════════════════════
#  2. LES TROIS ÉTATS, ET CE QUE LE VERT SIGNIFIE
# ═══════════════════════════════════════════════════════════════════════════

def test_les_trois_etats_se_succedent_dans_le_bon_ordre():
    r = _executer("""
      out.neuf = parcoursEtat(P);
      guidedStartStep(P.id, 0);
      out.cours = parcoursEtat(P);
      for (var i = 0; i < P.steps.length; i++) guidedStartStep(P.id, i);
      out.fini = parcoursEtat(P);
    """)
    assert r["neuf"]["statut"] == "neuf" and r["neuf"]["part"] == 0
    assert r["cours"]["statut"] == "cours" and 0 < r["cours"]["part"] < 100
    assert r["fini"]["statut"] == "fini" and r["fini"]["part"] == 100


def test_LE_VERT_N_APPARAIT_QU_AU_COMPLET():
    """Une seule étape manquante, et l'état reste bleu. C'est ce qui donne sa
    valeur au vert : un vert accordé à quatorze quinzièmes ne dirait plus rien."""
    r = _executer("""
      for (var i = 0; i < P.steps.length - 1; i++) guidedStartStep(P.id, i);
      out.presque = parcoursEtat(P);
      out.cartePresque = guidedPathCard(P);
      guidedStartStep(P.id, P.steps.length - 1);
      out.complet = parcoursEtat(P);
      out.carteComplet = guidedPathCard(P);
    """)
    assert r["presque"]["statut"] == "cours"
    assert "gp-etat cours" in r["cartePresque"]
    assert "gp-etat fini" not in r["cartePresque"]
    assert r["complet"]["statut"] == "fini"
    assert "gp-etat fini" in r["carteComplet"]


def test_LE_VERT_PORTE_SA_RESERVE_et_seulement_quand_il_apparait():
    """Il dit que chaque étape a été OUVERTE, pas que son travail a été fait —
    Sentinel ne mesure pas le second. Un vert non qualifié se lirait « c'est
    fait », et vaudrait moins que pas de vert du tout. La réserve n'est en
    revanche pas servie sur un parcours en cours : elle n'y répondrait à aucune
    question, et une réserve permanente cesse d'être lue."""
    r = _executer("""
      guidedStartStep(P.id, 0);
      out.carteCours = guidedPathCard(P);
      for (var i = 0; i < P.steps.length; i++) guidedStartStep(P.id, i);
      out.carteFinie = guidedPathCard(P);
      out.reserve = window.PARCOURS_RESERVE;
    """)
    assert "pas que le travail" in r["reserve"]
    assert r["reserve"] in _texte(r["carteFinie"]) or \
        r["reserve"] in r["carteFinie"]
    assert r["reserve"] not in r["carteCours"]


def test_les_deux_etats_se_lisent_SANS_COULEUR():
    """Vert et bleu sont exactement la paire que la deutéranopie confond. La
    puce et le compte en toutes lettres portent donc la même information —
    sinon la fonctionnalité demandée serait invisible pour une part des
    lecteurs."""
    r = _executer("""
      guidedStartStep(P.id, 0);
      out.cours = _texte = guidedPathCard(P);
      for (var i = 0; i < P.steps.length; i++) guidedStartStep(P.id, i);
      out.fini = guidedPathCard(P);
    """)
    cours, fini = _texte(r["cours"]), _texte(r["fini"])
    assert "●" in cours and "En cours" in cours
    assert "✓" in fini and "Parcouru en entier" in fini
    assert re.search(r"1 / \d+ étapes? ouverte", cours), cours[:200]
    assert re.search(r"(\d+) / \1 étapes? ouvertes", fini), fini[:200]


def test_la_barre_porte_son_role_et_ses_bornes_pour_un_lecteur_d_ecran():
    """Une barre purement graphique ne dit rien à un lecteur d'écran : il faut
    que la valeur, le minimum et le maximum soient annoncés."""
    r = _executer("""
      guidedStartStep(P.id, 1);
      out.bandeau = zones['guided-banner'].innerHTML;
    """)
    assert 'role="progressbar"' in r["bandeau"]
    for attribut in ("aria-valuenow", "aria-valuemin", "aria-valuemax",
                     "aria-label"):
        assert attribut in r["bandeau"], attribut


# ═══════════════════════════════════════════════════════════════════════════
#  3. L'AVANCEMENT SURVIT, ET NE SE DEVINE PAS
# ═══════════════════════════════════════════════════════════════════════════

def test_l_avancement_survit_a_la_visite():
    """`window.__activeGuided` vivait en mémoire : un rechargement effaçait
    tout, et la carte qu'on rouvre trois jours plus tard ne portait rien."""
    r = _executer("""
      guidedStartStep(P.id, 0);
      guidedStartStep(P.id, 1);
      out.ecrit = JSON.parse(localStorage.getItem('cpParcoursVues'));
    """)
    assert r["ecrit"], "rien n'est conservé : l'avancement meurt avec l'onglet"
    cle = list(r["ecrit"])[0]
    assert len(r["ecrit"][cle]) == 2


def test_LA_CLE_EST_LE_COUPLE_RANG_IDENTIFIANT_et_non_l_un_des_deux():
    """L'index seul ferait qu'un parcours réordonné hériterait de l'avancement
    de l'ancien ordre — deux étapes différentes au même rang seraient
    confondues. L'identifiant seul confondrait deux étapes qui mènent au même
    panneau, et il y en a. Le couple perd l'avancement d'une étape modifiée,
    ce qui est le comportement juste : on ne sait plus si elle a été vue, donc
    on ne le dit pas."""
    r = _executer("""
      guidedStartStep(P.id, 0);
      out.cles = JSON.parse(localStorage.getItem('cpParcoursVues'))[P.id];
      out.attendu = 0 + ':' + P.steps[0].id;
      /* Le même panneau à un autre rang ne doit PAS hériter de l'avancement. */
      var faux = {id:'recette-couple', steps:[
        {id:'zzz', label:'a'}, {id:P.steps[0].id, label:'b'}]};
      window.__monParcours = faux;
      out.autreRang = parcoursEtapeVue(faux, 1);
    """)
    assert r["cles"] == [r["attendu"]], r["cles"]
    assert r["autreRang"] is False


def test_un_stockage_refuse_ne_fait_pas_tomber_la_page():
    """Navigation privée, réglage du navigateur : `localStorage` peut lever à
    la lecture comme à l'écriture. Un parcours sans mémoire reste un parcours ;
    une page blanche, non."""
    r = _executer("""
      guidedStartStep(P.id, 0);
      out.etat = parcoursEtat(P);
      out.carte = guidedPathCard(P).length;
      out.bandeau = zones['guided-banner'].innerHTML.length;
    """, stockage="refuse")
    assert r["etat"]["statut"] == "neuf", "un stockage refusé ne doit rien inventer"
    assert r["carte"] > 200 and r["bandeau"] > 200


def test_repartir_de_zero_efface_vraiment():
    r = _executer("""
      for (var i = 0; i < P.steps.length; i++) guidedStartStep(P.id, i);
      out.avant = parcoursEtat(P);
      parcoursOublier(P.id);
      out.apres = parcoursEtat(P);
    """)
    assert r["avant"]["statut"] == "fini"
    assert r["apres"]["statut"] == "neuf" and r["apres"]["vues"] == 0


# ═══════════════════════════════════════════════════════════════════════════
#  4. LES TROIS ÉCRANS DISENT LA MÊME CHOSE
# ═══════════════════════════════════════════════════════════════════════════

def test_la_liste_des_roles_dit_l_avancement():
    """Sans cela, un client qui revient doit ouvrir chaque parcours pour
    retrouver celui qu'il avait commencé."""
    r = _executer("""
      out.neuve = gpOption(P);
      guidedStartStep(P.id, 0);
      out.cours = gpOption(P);
      for (var i = 0; i < P.steps.length; i++) guidedStartStep(P.id, i);
      out.finie = gpOption(P);
    """)
    assert "vues" not in r["neuve"] and "terminé" not in r["neuve"]
    assert re.search(r"● 1/\d+ vues", r["cours"]), r["cours"]
    assert "✓ terminé" in r["finie"]


def test_la_carte_marque_les_etapes_ouvertes_ET_SEULEMENT_ELLES():
    """La carte est ce qu'on rouvre trois jours plus tard : c'est là qu'il faut
    savoir où l'on en était, étape par étape. La règle compte les deux côtés —
    une implémentation qui marquerait TOUTES les étapes passerait un contrôle
    de simple présence."""
    r = _executer("""
      guidedStartStep(P.id, 0);
      guidedStartStep(P.id, 2);
      out.carte = guidedPathCard(P);
      out.total = P.steps.length;
    """)
    assert r["carte"].count("guided-step vue") == 2, (
        "%d étapes marquées ouvertes alors que deux l'ont été"
        % r["carte"].count("guided-step vue"))
    assert r["carte"].count('class="guided-step"') == r["total"] - 2
    # Et le bouton ne ment pas sur ce qui s'est passé.
    assert r["carte"].count("Revenir à cette page") == 2
    assert r["carte"].count("Aller à cette page") == r["total"] - 2


def test_LE_PIEGE_la_selection_survit_a_la_reconstruction_de_la_liste():
    """Les options portent désormais l'avancement, donc la liste est refaite à
    chaque étape franchie. `innerHTML =` remet alors la valeur à vide, et le
    rôle en cours disparaît de la barre latérale au moment précis où on le
    suit. Le piège a été rencontré en écrivant ce lot."""
    r = _executer("""
      window.__activeGuided = { pathId: P.id, i: 0 };
      zones['sb-role'].value = P.id;
      sbRolesRemplir();
      out.valeur = zones['sb-role'].value;
    """)
    assert r["valeur"], "la barre latérale a perdu le rôle en cours"


def test_UN_SEUL_ENDROIT_CALCULE_L_ETAT():
    """Le bandeau, la carte et la liste l'appellent tous les trois. Trois
    calculs séparés divergeraient au premier changement, et c'est celui qu'on
    regarde le moins qu'on oublierait de corriger. La règle compte les
    définitions dans le fichier, hors commentaires — un nom cité dans une
    explication n'est pas une seconde définition."""
    sans_commentaires = re.sub(r"/\*.*?\*/", " ", MOTEUR, flags=re.S)
    sans_commentaires = re.sub(r"^\s*//.*$", " ", sans_commentaires, flags=re.M)
    for nom in ("parcoursEtat", "parcoursEtapeVue", "parcoursNoter"):
        n = len(re.findall(r"window\.%s\s*=" % nom, sans_commentaires))
        assert n == 1, "%s est défini %d fois" % (nom, n)


def test_le_passage_est_note_dans_guidedStartStep_et_nulle_part_ailleurs():
    """Noter en amont (au clic) compterait une étape qu'un `return` peut encore
    refuser ; noter en aval (à la peinture du panneau) compterait une arrivée
    par le menu."""
    sans_commentaires = re.sub(r"/\*.*?\*/", " ", MOTEUR, flags=re.S)
    # La DÉFINITION s'écrit « window.parcoursNoter = function », sans
    # parenthèse accolée au nom : le motif ne compte donc que les APPELS, et il
    # doit y en avoir exactement un.
    appels = re.findall(r"parcoursNoter\(", sans_commentaires)
    assert len(appels) == 1, (
        "`parcoursNoter` est appelé %d fois : le passage doit être noté à un "
        "seul endroit" % len(appels))
    d = sans_commentaires.index("window.guidedStartStep = function")
    f = sans_commentaires.index("\n};", d)
    assert "parcoursNoter(" in sans_commentaires[d:f]


def test_les_styles_des_trois_etats_existent_et_se_distinguent():
    """Une classe posée par le JS et absente de la feuille ne lève rien : elle
    ne peint simplement pas."""
    for classe in (".gp-etat.fini", ".gp-etat.cours", ".gp-etat.neuf",
                   ".gp-barre.fini>i", ".gp-barre.cours>i",
                   ".guided-step.vue", ".guided-banner .gb-barre"):
        assert classe in PAGE, classe
    fini = re.search(r"\.gp-etat\.fini\{([^}]+)\}", PAGE).group(1)
    cours = re.search(r"\.gp-etat\.cours\{([^}]+)\}", PAGE).group(1)
    assert "--green" in fini and "--blue" in cours
    assert fini != cours
