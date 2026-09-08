# -*- coding: utf-8 -*-
"""LE PANNEAU DE L'EMPREINTE IA — ce qu'il peint, mesuré en l'exécutant.

POURQUOI CES RÈGLES EXÉCUTENT LE CODE AU LIEU DE LE LIRE. Une règle qui
cherche le mot « couverture » dans `sentinel.page.js` reste verte quand le
bloc est peint APRÈS les totaux, quand une absence de déclaration ressort à
zéro, ou quand l'indicateur non servi disparaît au lieu de se déclarer absent.
C'est le défaut corrigé dix fois dans ces dépôts : *une règle qui passe pour
une raison sans rapport avec ce qu'elle prétend*. Le peintre est donc évalué
sous node contre un DOM postiche, et les règles lisent ce qu'il a RÉELLEMENT
écrit dans chaque zone.

CE QU'ELLES GARDENT

  — LA COUVERTURE PRÉCÈDE LES TOTAUX, à l'écran comme dans le moteur. Un total
    qui tait ce qu'il ignore est un total faux.

  — UNE ABSENCE N'EST JAMAIS UN ZÉRO. « 0 kWh » se lit « cela ne consomme
    rien » ; l'absence se lit « personne ne l'a déclaré ». Confondre les deux
    fait paraître sobre un parc à moitié inscrit.

  — L'INDICATEUR NON SERVI SE DÉCLARE ABSENT, avec ce qu'il faudrait pour
    l'établir. Le taire donnerait quatre indicateurs sur cinq sans le dire.

  — RIEN N'EST RECOPIÉ DANS L'ÉCRAN. Facteurs, réserves, leviers et champs à
    déclarer sont SERVIS. Une valeur recopiée ferait dériver l'écran du code,
    et c'est l'écran qu'on croirait.
"""
import io
import json
import os
import re
import subprocess

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = io.open(os.path.join(ICI, "sentinel.page.js"), encoding="utf-8").read()
PAGE = io.open(os.path.join(ICI, "sentinel.html"), encoding="utf-8").read()

MARQUE = "EMPREINTE IA DU PARC — la couverture d'abord"


def _peintre():
    """Le peintre SEUL, découpé dans le vrai fichier — jamais recopié ici."""
    d = JS.index(MARQUE)
    d = JS.index("(function(){", d)
    f = JS.index("\n})();", d)
    return JS[d:f + len("\n})();")]


PEINTRE = _peintre()

#: Les zones que le panneau peint. Relevées sur la PAGE, pas listées de tête :
#: une zone ajoutée demain sans peintre tombe dans le filet le jour même.
ZONES = sorted(set(re.findall(r'id="(ei-[a-z-]+)"', PAGE)))


def _executer(reponse, ok=True):
    """Évalue le peintre contre un DOM postiche et rend ce qu'il a écrit."""
    code = """
var ZONES = %s;
var peint = {};
var elements = {};
ZONES.forEach(function(z){
  elements[z] = {_h:'', _t:'',
    get innerHTML(){return this._h}, set innerHTML(v){this._h = v; peint[z] = v},
    get textContent(){return this._t}, set textContent(v){this._t = v; peint[z] = v},
    value: (z === 'ei-pays' ? 'FR' : (z === 'ei-horizon' ? '2030' : ''))};
});
var telecharge = null;
var document = {
  getElementById: function(id){ return elements[id] || null; },
  createElement: function(){ return {click: function(){ telecharge = this.href; },
                                     set href(v){ this._href = v; },
                                     get href(){ return this._href; },
                                     download: ''}; },
  body: {appendChild: function(){}, removeChild: function(){}}
};
var CORPS = null;
function Blob(parts){ CORPS = parts.join(''); }
var URL = {createObjectURL: function(){ return 'blob:x'; }, revokeObjectURL: function(){}};
var window = {};
var REPONSE = %s;
var OK = %s;
function fetch(){ return Promise.resolve({ok: OK, json: function(){ return Promise.resolve(REPONSE); }}); }
%s
window.empIaLoad();
setTimeout(function(){
  if(window.empIaExport) window.empIaExport();
  console.log(JSON.stringify({peint: peint, csv: CORPS}));
}, 30);
""" % (json.dumps(ZONES), json.dumps(reponse), "true" if ok else "false", PEINTRE)
    r = subprocess.run(["node", "-e", code], capture_output=True, text=True)
    assert r.returncode == 0, "le peintre n'est plus évaluable : %s" % r.stderr[-900:]
    return json.loads(r.stdout)


# ══════════════════════════════════════════════════════════════════════════
#  Une réponse de référence, de la FORME que la route sert réellement
# ══════════════════════════════════════════════════════════════════════════
# Elle n'est pas inventée : `test_empreinte_parc.py` mesure que la route sert
# ces clés, et `test_empreinte_ia.py` que le moteur les produit. Ici on garde
# ce que l'ÉCRAN en fait.

REPONSE = {
    "ok": True, "version": "2026-09-a", "pays": "FR",
    "intensite": 60.0, "source_intensite": "RTE éCO2mix",
    "intensite_hebergement": 380.0, "source_intensite_hebergement": "AIE 2024",
    "couverture": {"systemes": 4, "volume_declare": 3, "chiffrable": 3, "part": 0.75,
                   "volume_manquant": ["Vision qualité"],
                   "ajustement_declare": 1, "ajustement_incomplet": ["Copilote métier"]},
    "lignes": [
        {"nom": "Assistant support",
         "inference": {"nature": "declare", "motif": None, "wh": 57600.0, "g_co2": 4492.8,
                       "mj": 393.98, "hebergement_derive": False, "profil_connu": True},
         "ajustement_fin": {"nature": "incomplet", "wh_mois": None, "g_co2_mois": None,
                            "manquants": ["amorti_mois", "puissance_w"],
                            "motif": "un ajustement fin ne s'estime pas"}},
        {"nom": "Vision qualité",
         "inference": {"nature": "non_instruit", "motif": "aucun volume de sortie déclaré",
                       "wh": None, "g_co2": None, "mj": None},
         "ajustement_fin": {"nature": "incomplet", "wh_mois": None, "g_co2_mois": None,
                            "manquants": ["pue"], "motif": "à déclarer"}},
        {"nom": "Copilote métier",
         "inference": {"nature": "declare", "motif": None, "wh": 19869.0, "g_co2": 3361.8,
                       "mj": 135.9, "hebergement_derive": True, "profil_connu": True},
         "ajustement_fin": {"nature": "declare", "wh_mois": 4096.0, "g_co2_mois": 245.8}},
    ],
    "inference_mois": {"wh": 77469.0, "g_co2": 7854.6, "mj": 529.9, "eau_m3": 0.1007},
    "ajustement_fin_mois": {"wh": 4096.0, "g_co2": 245.8, "mj": 28.0},
    "total_mois": {"wh": 81565.0, "g_co2": 8100.4, "mj": 557.9, "eau_m3": 0.1007},
    "hebergement_non_derivable": ["Assistant support"],
    "base_annuelle_kg": 97.2,
    "trajectoires": [
        {"nature": "projete", "cle": "progression_reguliere", "nom": "Progression régulière",
         "lecture": "Adoption modérée · efficacité limitée", "multiple": 1.42,
         "points": [{"annee": 2026, "valeur": 97.2}, {"annee": 2030, "valeur": 138.0}]},
    ],
    "indicateurs": [
        {"cle": "electricite", "libelle": "Électricité", "unite": "kWh", "servi": True, "manque": ""},
        {"cle": "ges", "libelle": "Émissions de GES", "unite": "kg CO₂ éq.", "servi": True, "manque": ""},
        {"cle": "eau", "libelle": "Eau", "unite": "m³ éq.", "servi": True, "manque": ""},
        {"cle": "energie_primaire", "libelle": "Énergie primaire", "unite": "MJ", "servi": True, "manque": ""},
        {"cle": "ressources", "libelle": "Ressources", "unite": "kg Sb éq.", "servi": False,
         "manque": "Aucun facteur d'épuisement abiotique sourçable n'a été retenu."},
    ],
    "facteurs": {
        "pef_electricite": {"libelle": "Coefficient d'énergie primaire", "valeur": 1.9,
                            "unite": "", "source": "CELEX 32023R0807", "date": "2023-04-14",
                            "nature": "texte_reglementaire",
                            "reserve": "Ce coefficient vaut pour l'électricité du réseau.",
                            "point_ouvert": "La refonte 2023/1791 n'a pas pu être lue.",
                            # L'HÔTE EST RÉSERVÉ (RFC 2606), ET C'EST DÉLIBÉRÉ.
                            # `test_secteurs_nace` interdit à toute règle de la
                            # suite de nommer l'hôte de la source : une suite
                            # qui rougit quand le réseau bouge finit par ne
                            # plus être lue. Ce qui est mesuré ici est que le
                            # lien SOIT PEINT, pas où il mène.
                            "url": "https://texte.invalid/eli/reg_del/2023/807/oj"},
        "fabrication_pct": {"libelle": "Majoration de fabrication", "valeur": 30,
                            "unite": "%", "source": "Boavizta", "date": "2025-01-01",
                            "nature": "hypothese_cabinet"},
    },
    "a_declarer_ajustement_fin": {
        "heures_accelerateur": "Durée de la campagne, en heures d'accélérateur cumulées.",
        "pue": "Rendement du centre de données où la campagne a tourné.",
    },
    "scenarios_source": "REPÈRES DU CABINET, PAS UN RÉFÉRENTIEL.",
    "leviers_2030": [
        {"cle": "mix_electrique", "nom": "Mix électrique", "agit_sur": "ges",
         "quoi": "Localisation des centres, contrats d'origine.",
         "porte": "Ne change RIEN à l'électricité consommée ni à l'énergie primaire."},
    ],
    "etat_module": {"substitues": []},
}

RENDU = _executer(REPONSE)
PEINT = RENDU["peint"]


# ══════════════════════════════════════════════════════════════════════════
#  0. Le garde-fou : une lecture cassée rendrait tout le reste vert
# ══════════════════════════════════════════════════════════════════════════

def test_le_releve_lit_bien_la_page_et_le_peintre():
    """Le défaut que ces dépôts ont déjà commis : mesurer le vide et le
    trouver conforme."""
    assert len(ZONES) >= 10, "zones relevées : %s" % ZONES
    assert len(PEINTRE) > 4000, "peintre découpé : %d caractères" % len(PEINTRE)
    assert len(PEINT) >= 8, "zones réellement peintes : %s" % sorted(PEINT)


# ══════════════════════════════════════════════════════════════════════════
#  1. LA COUVERTURE PRÉCÈDE LES TOTAUX — dans le document, pas en intention
# ══════════════════════════════════════════════════════════════════════════

def test_la_couverture_est_peinte_AVANT_les_totaux_dans_le_document():
    """MESURÉE SUR L'ORDRE DU DOCUMENT, pas sur la présence d'un bloc. Un
    panneau qui porte les deux mais montre les totaux en premier laisse lire
    un chiffre avant de dire ce qu'il ignore — et c'est exactement l'erreur
    que la couverture existe pour empêcher."""
    couv = PAGE.index('id="ei-couverture"')
    for apres in ("ei-indicateurs", "ei-lignes", "ei-trajectoires"):
        assert couv < PAGE.index('id="%s"' % apres), (
            "« %s » est placé AVANT le bloc de couverture" % apres)


def test_la_couverture_dit_la_part_ET_nomme_ce_qui_manque():
    d = PEINT["ei-couv-detail"]
    assert "75 %" in d, d
    assert "Vision qualité" in d, "le système sans volume n'est pas nommé"
    assert "Copilote métier" in d, "l'ajustement incomplet n'est pas nommé"
    assert PEINT["ei-couv-chiffre"] == "3 / 4", PEINT["ei-couv-chiffre"]


# ══════════════════════════════════════════════════════════════════════════
#  2. UNE ABSENCE N'EST JAMAIS UN ZÉRO
# ══════════════════════════════════════════════════════════════════════════

def test_une_ligne_non_instruite_sort_en_tiret_JAMAIS_en_zero():
    """LE DÉFAUT QUE CETTE RÈGLE PREND, ET IL EST SILENCIEUX : « 0 kWh » se lit
    « cela ne consomme rien », l'absence se lit « personne ne l'a déclaré ».
    Confondre les deux fait paraître sobre un parc à moitié inscrit — et
    aucune erreur ne s'affiche."""
    lignes = PEINT["ei-lignes"]
    bloc = lignes[lignes.index("Vision qualité"):]
    bloc = bloc[:bloc.index("</tr>")]
    cellules = re.findall(r"<td[^>]*>(.*?)</td>", bloc, re.S)
    # La première cellule est le nom ; les trois suivantes sont des montants.
    # LE MOTIF CHERCHE DANS LE CONTENU DÉJÀ EXTRAIT, DONC SANS CHEVRON. La
    # première version cherchait `>\s*0` dans une chaîne d'où les chevrons
    # avaient précisément été retirés : elle ne pouvait rien trouver, et
    # restait verte quel que soit le montant affiché.
    for c in cellules[1:4]:
        assert "—" in c, "une ligne non instruite affiche un montant : %r" % c
        assert not re.match(r"^\s*[-+]?[\d\u202f\u00a0 ]*[\d]", c), (
            "une ligne non instruite affiche un NOMBRE : %r" % c)
    assert "aucun volume de sortie déclaré" in cellules[-1], cellules[-1]


def test_un_ajustement_incomplet_NOMME_les_champs_a_declarer():
    """« Incomplet » tout seul renvoie l'utilisateur chercher quoi ; la liste
    lui dit quoi saisir. C'est la différence entre un reproche et une
    consigne."""
    lignes = PEINT["ei-lignes"]
    bloc = lignes[lignes.index("Assistant support"):]
    bloc = bloc[:bloc.index("</tr>")]
    for champ in ("amorti_mois", "puissance_w"):
        assert champ in bloc, "le champ manquant « %s » n'est pas nommé" % champ


# ══════════════════════════════════════════════════════════════════════════
#  3. L'INFÉRENCE ET L'AJUSTEMENT FIN RESTENT SÉPARÉS
# ══════════════════════════════════════════════════════════════════════════

def test_les_deux_postes_sont_TOTALISES_SEPAREMENT_puis_additionnes():
    """LES MÊLER FERAIT DISPARAÎTRE le terme qui, sur un parc qui affine ses
    modèles, est souvent le plus lourd. La règle ne compare pas un total à une
    somme — cette identité reste vraie quand l'ajustement a déjà été fondu
    dans l'inférence. Elle exige TROIS lignes de pied distinctes, et que celle
    de l'inférence ne porte PAS le total."""
    pied = PEINT["ei-lignes"]
    pied = pied[pied.index("<tfoot>"):]
    assert "Inférence" in pied and "Ajustement fin" in pied and "Total du parc" in pied, (
        "le pied de tableau ne distingue plus les deux postes")
    inf = pied[pied.index("Inférence"):pied.index("Ajustement fin")]
    # 77 469 Wh d'inférence, 81 565 au total : le pied de l'inférence doit
    # porter le premier, jamais le second.
    assert "77,5" in inf, "la ligne d'inférence ne porte pas le total d'inférence : %r" % inf
    assert "81,6" not in inf, "la ligne d'inférence porte le TOTAL — les deux postes sont fondus"


def test_la_base_des_trajectoires_est_ANNONCEE_comme_le_total_annualise():
    """Une trajectoire assise sur la seule inférence sous-estimerait
    durablement un parc qui affine ses modèles. La page dit sur quoi elle
    projette, sans quoi le lecteur le suppose."""
    t = PEINT["ei-trajectoires"]
    assert "ajustement fin" in t.lower(), t[-400:]
    assert "97,2" in t, "la base annuelle servie n'est pas affichée"


# ══════════════════════════════════════════════════════════════════════════
#  4. L'INDICATEUR NON SERVI SE DÉCLARE ABSENT
# ══════════════════════════════════════════════════════════════════════════

def test_l_indicateur_non_servi_est_DECLARE_absent_avec_ce_qui_manque():
    """Le taire donnerait quatre indicateurs sur cinq sans le dire, et un
    lecteur croirait l'étude complète. Le remplir d'un ordre de grandeur
    trouvé ailleurs serait pire : un nombre sans auteur."""
    z = PEINT["ei-indicateurs"]
    assert "Ressources" in z, "l'indicateur absent a disparu de l'écran"
    assert "Non servi" in z, "l'indicateur absent n'est pas signalé comme tel"
    assert "épuisement abiotique" in z, "ce qu'il faudrait pour l'établir n'est pas dit"


def test_les_quatre_indicateurs_servis_portent_leur_valeur_ET_leur_periode():
    """Un nombre sans période n'est pas opposable : « 8 100 » se lit annuel
    aussi facilement que mensuel."""
    z = PEINT["ei-indicateurs"]
    for libelle in ("Électricité", "Émissions de GES", "Eau", "Énergie primaire"):
        assert libelle in z, libelle
    assert z.count("par mois") == 4, (
        "les quatre indicateurs servis ne portent pas tous leur période : %d"
        % z.count("par mois"))
    assert "81,6" in z, "le total d'électricité en kWh n'est pas peint"


# ══════════════════════════════════════════════════════════════════════════
#  5. LE PÉRIMÈTRE INCOMPLET EST NOMMÉ — ET LE BLOC S'EFFACE QUAND IL EST VIDE
# ══════════════════════════════════════════════════════════════════════════

def test_le_perimetre_incomplet_NOMME_les_systemes_concernes():
    z = PEINT["ei-perimetre"]
    assert "Assistant support" in z, "le système au périmètre incomplet n'est pas nommé"
    assert "requête" in z.lower(), "la raison — 0,15 Wh par requête — n'est pas dite"


def test_le_bloc_de_perimetre_S_EFFACE_quand_rien_ne_manque():
    """Un encadré vide finit par ne plus être lu, et celui-ci doit se voir le
    jour où il se remplit."""
    r = dict(REPONSE); r["hebergement_non_derivable"] = []
    z = _executer(r)["peint"].get("ei-perimetre", "")
    assert z.strip() == "", "le bloc de périmètre subsiste alors qu'il n'a rien à dire : %r" % z


# ══════════════════════════════════════════════════════════════════════════
#  6. RIEN N'EST RECOPIÉ DANS L'ÉCRAN
# ══════════════════════════════════════════════════════════════════════════

#: Ce qui doit venir du SERVEUR, et le fragment qui le prouverait recopié.
SERVIS = [
    ("le libellé d'un levier", "Ne change RIEN à l'électricité"),
    ("la source des scénarios", "REPÈRES DU CABINET"),
    ("une réserve de facteur", "vaut pour l'électricité du réseau"),
    ("un champ à déclarer", "heures d'accélérateur cumulées"),
    ("le nom d'un facteur", "CELEX 32023R0807"),
]


@pytest.mark.parametrize("quoi,fragment", SERVIS)
def test_ce_que_le_moteur_sert_n_est_pas_RECOPIE_dans_l_ecran(quoi, fragment):
    """LA RÈGLE MESURE LES DEUX CÔTÉS, et c'est ce qui la rend utile : le
    fragment est ABSENT du peintre (donc pas recopié) et PRÉSENT dans ce qu'il
    a peint (donc bien servi). Vérifier seulement l'absence laisserait passer
    un peintre qui n'affiche rien du tout."""
    assert fragment not in PEINTRE, (
        "%s est recopié dans sentinel.page.js — l'écran dérivera du code, "
        "et c'est l'écran qu'on croira" % quoi)
    # ON DÉSÉCHAPPE AVANT DE CHERCHER. `ech()` transforme l'apostrophe en
    # `&#39;` : chercher le texte brut dans le HTML peint échouerait sur une
    # mécanique d'affichage, pas sur un contenu manquant — et la règle
    # accuserait le peintre d'un défaut qu'il n'a pas.
    partout = "".join(PEINT.values())
    for e, c in (("&#39;", "'"), ("&quot;", '"'), ("&amp;", "&"),
                 ("&lt;", "<"), ("&gt;", ">")):
        partout = partout.replace(e, c)
    assert fragment in partout, (
        "%s n'est pas peint : la règle d'absence serait verte pour rien" % quoi)


def test_la_valeur_d_un_facteur_est_ecrite_A_LA_FRANCAISE():
    """RELEVÉ EN NAVIGATEUR, PAS DEVINÉ : le panneau affichait « 1.9 », avec un
    point, au milieu d'une page qui écrit partout ailleurs à la française. La
    règle mesure aussi que la précision NATURELLE est gardée — un formateur à
    décimales fixes écrirait « 30,0 » pour une majoration entière, et « 0,1 »
    pour un facteur réseau de 0,06, ce qui est faux."""
    z = PEINT["ei-facteurs"]
    assert "1,9" in z, "la valeur du coefficient n'est pas à la française : %r" % z[:200]
    assert "1.9" not in z, "la valeur garde son point décimal"
    assert ">30<" in z or "30 %" in z or ">30 " in z or "30</span>" in z, (
        "la majoration entière n'est plus affichée telle quelle : %r" % z[:400])
    assert "30,0" not in z, (
        "un formateur à décimales fixes a été appliqué à une valeur entière")


def test_un_facteur_substitue_par_configuration_est_SIGNALE():
    """Sans cela, la page citerait un règlement européen pour une valeur qui
    n'en vient plus."""
    assert "substitu" not in PEINT["ei-limites"].lower(), (
        "aucun facteur n'est substitué, et la page le dit quand même")
    r = json.loads(json.dumps(REPONSE))
    r["etat_module"]["substitues"] = ["pef_electricite"]
    z = _executer(r)["peint"]["ei-limites"]
    assert "pef_electricite" in z and "substitu" in z.lower(), z


# ══════════════════════════════════════════════════════════════════════════
#  7. L'EXPORT REPART DE LA RÉPONSE, PAS DU TABLEAU PEINT
# ══════════════════════════════════════════════════════════════════════════

def test_l_export_porte_les_nombres_BRUTS_et_non_le_formatage_d_ecran():
    """Relire le DOM rendrait l'export dépendant du formatage : « 4 492,80 »
    avec son espace fine ne se recharge dans aucun tableur. La règle mesure la
    forme des nombres écrits, pas l'intention."""
    csv = RENDU["csv"]
    assert csv, "aucun export produit"
    assert "57.600" in csv, "les kWh ne sortent pas en écriture décimale brute : %r" % csv[:300]
    assert " " not in csv and "4 492" not in csv, "l'export reprend le formatage d'écran"
    assert "Vision qualité;;;" in csv, (
        "une ligne non instruite doit sortir avec des champs VIDES, jamais des zéros")
    assert "hebergement non derivable" in csv, (
        "l'export tait le périmètre incomplet, que l'écran affiche")


# ══════════════════════════════════════════════════════════════════════════
#  8. LE PANNEAU EST ATTEIGNABLE — menu, aiguillage, guide
# ══════════════════════════════════════════════════════════════════════════

def test_le_panneau_est_atteignable_par_le_menu_et_l_aiguillage():
    """Un panneau que `go()` n'aiguille pas s'ouvre VIDE : aucune erreur ne
    s'affiche, il ne se peint simplement jamais."""
    assert 'id="p-empreinte-ia"' in PAGE
    assert "go('empreinte-ia'" in PAGE, "aucune entrée de menu ne mène au panneau"
    assert ("if (id === 'empreinte-ia' && typeof window.empIaLoad === 'function')"
            in JS), "go() n'appelle pas le peintre : le panneau s'ouvrirait vide"
    assert "'empreinte-ia': { section:" in JS, "le panneau n'a pas d'entrée PAGE_META"
    assert "'empreinte-ia': {\n    title:" in JS, "le panneau n'a pas de guide"


def test_le_panneau_ne_se_confond_pas_avec_les_DEUX_autres_empreintes():
    """Trois panneaux portent le mot « empreinte » et mesurent trois choses
    différentes : ce que CONSEILPREV consomme, ce que pèsent les ÉQUIPEMENTS
    d'un centre, et ce que déclare le REGISTRE d'un client. Les identifiants
    doivent rester distincts, sinon `go()` en ouvre un pour l'autre."""
    for autre in ("p-empreinte", "p-empreinte-parc", "p-empreinte-ia"):
        assert 'id="%s"' % autre in PAGE, autre
    assert PAGE.count('id="p-empreinte-ia"') == 1
