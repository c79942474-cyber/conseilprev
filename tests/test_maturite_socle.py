"""Le socle de l'audit : relevé, ou seulement encadré — et jamais confondu.

CE QUE CE FICHIER TIENT. Vingt et un profils sectoriels couvrent les vingt-deux
sections de la NACE. Huit portent un socle RELEVÉ : un point de départ observé
sur des organisations du secteur, un budget et une durée issus de missions
réelles. Treize portent un RÉGIME lu dans les textes — annexe III du règlement
(UE) 2024/1689, annexes I et II de la directive (UE) 2022/2555 — et rien
d'autre.

LE DÉFAUT QUE CES RÈGLES EMPÊCHENT DE REVENIR. Ce n'est pas d'oublier un
profil : c'est qu'un profil de cadre RESSEMBLE à un profil relevé. Même mise en
page, même score, mêmes phases. Vingt endroits du moteur lisent `pillars`,
`budget` et `duree` ; si chacun inventait son propre repli, un profil non
calibré afficherait 0,0 ici, « null semaines » là et un montant NaN ailleurs —
trois mensonges différents pour un seul manque, et aucun ne lève d'erreur.

LES RÈGLES EXÉCUTENT LE MOTEUR. Chercher `matSocle` dans le fichier dirait
seulement que la fonction existe. Ce qui se mesure est ce qu'elle REND, et ce
que `matBudget` fait d'une absence.
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import secteurs_nace as N                                           # noqa: E402

MOTEUR = io.open(os.path.join(ICI, "sentinel.page.js"), encoding="utf-8").read()
PAGE = io.open(os.path.join(ICI, "sentinel.html"), encoding="utf-8").read()


def _bloc(debut, fin):
    """Un morceau du moteur, pris entre deux ancres — et PROUVÉ non vide.

    Un extracteur qui rend une chaîne vide ferait passer toutes les règles qui
    s'en servent, en silence."""
    d = MOTEUR.index(debut)
    f = MOTEUR.index(fin, d) + len(fin)
    morceau = MOTEUR[d:f]
    assert len(morceau) > len(debut) + 10, (debut, len(morceau))
    return morceau


def _profils():
    d = MOTEUR.index("var MAT_SECTORS = ")
    f = MOTEUR.index("};", d) + 1
    p = json.loads(MOTEUR[d + len("var MAT_SECTORS = "):f])
    assert len(p) == len(N.PROFILS_SENTINEL)
    return p


def _executer(script):
    """Le VRAI code du moteur, exécuté sous node.

    Les trois fonctions sont reprises telles quelles dans le fichier servi :
    une copie réécrite ici mesurerait la copie."""
    node = shutil.which("node")
    if not node:
        pytest.skip("node absent : le moteur ne peut pas être exécuté")
    src = ("\n".join([
        _bloc("var MAT_SECTORS = ", "};"),
        _bloc("function matMoyenneSocle(soc){", "\n}"),
        _bloc("function matSocle(s){", "\n}"),
        _bloc("function matBudget(sectorBudget){", "\n}"),
    ]) + "\n" + script)
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "h.js")
        with io.open(f, "w", encoding="utf-8") as fh:
            fh.write(src)
        p = subprocess.run([node, f], capture_output=True, text=True, timeout=60)
    if p.returncode != 0:
        pytest.fail("le moteur ne tourne pas :\n%s" % (p.stderr or "")[-1500:])
    return json.loads(p.stdout)


JOUE = _executer("""
var rapport = {};
Object.keys(MAT_SECTORS).forEach(function(k){
  var s = MAT_SECTORS[k];
  var soc = matSocle(s);
  var b = matBudget(soc.budget);
  var total = b.reduce(function(a,x){ return a + x.cost; }, 0);
  rapport[k] = {
    calibre: soc.calibre,
    budget: soc.budget, duree: soc.duree,
    piliers: Object.keys(soc.pillars).length,
    moyenne: matMoyenneSocle(soc),
    lignes: b.length,
    total: total,
    fini: isFinite(total),
    mention: soc.mention
  };
});
process.stdout.write(JSON.stringify(rapport));
""")


#  LES DEUX FAMILLES VIENNENT DE LA DÉCLARATION DU MODULE, JAMAIS DU DRAPEAU
#  QUE CES RÈGLES MESURENT. Une première version les tirait de `calibre`, rendu
#  par `matSocle` — la fonction même qu'on éprouve. Une mutation qui faisait
#  déclarer TOUT LE MONDE relevé vidait donc la liste des profils de cadre, et
#  la règle « un profil de cadre ne rend ni budget ni durée » passait à VIDE :
#  verte, sur zéro profil, pendant que le défaut était installé.

def _cadres():
    return sorted(k for k, p in N.PROFILS_SENTINEL.items() if p["socle"] == "cadre")


def _releves():
    return sorted(k for k, p in N.PROFILS_SENTINEL.items() if p["socle"] == "releve")


# ═══════════════════════════════════════════════════════════════════════════
#  LA PORTE UNIQUE REND CE QU'ELLE PROMET
# ═══════════════════════════════════════════════════════════════════════════


def test_le_drapeau_CALIBRE_rendu_est_EXACTEMENT_le_socle_declare():
    """DEUX CHOSES À LA FOIS, ET ELLES VONT ENSEMBLE.

    LE TÉMOIN QUI TIENT TOUT LE FICHIER : si plus aucun profil n'était relevé,
    ou si plus aucun ne l'était pas, toutes les règles ci-dessous passeraient en
    ne mesurant rien du tout.

    ET LA CORRESPONDANCE : `calibre` doit être exactement le socle déclaré. Un
    `matSocle` qui rendrait tout le monde relevé ne changerait pourtant RIEN à
    ce qu'un profil de cadre affiche — ses données sont vides, `matBudget` rend
    une liste vide — mais `buildDetailedBudget` cesserait de refuser : il
    diviserait `null` par la référence, obtiendrait zéro, et servirait un budget
    intégralement à 0 €. Un tableau de coûts nuls d'apparence normale."""
    assert len(_releves()) == 8, _releves()
    assert len(_cadres()) == 13, _cadres()
    assert len(JOUE) == len(N.PROFILS_SENTINEL)
    # ET LE MOTEUR REND BIEN DEUX FAMILLES, pas une seule : sans cela, les
    # listes ci-dessus seraient justes et `matSocle` mentirait quand même.
    rendus = {k: v["calibre"] for k, v in JOUE.items()}
    assert sorted(k for k, c in rendus.items() if c) == _releves(), rendus
    assert sorted(k for k, c in rendus.items() if not c) == _cadres(), rendus


def test_un_profil_de_cadre_ne_rend_NI_budget_NI_duree_NI_socle():
    for k in _cadres():
        v = JOUE[k]
        assert v["budget"] is None, k
        assert v["duree"] is None, k
        assert v["piliers"] == 0, k


def test_un_profil_releve_rend_les_trois():
    for k in _releves():
        v = JOUE[k]
        assert isinstance(v["budget"], (int, float)) and v["budget"] > 0, k
        assert isinstance(v["duree"], (int, float)) and v["duree"] > 0, k
        assert v["piliers"] == 8, k


def test_matBudget_ne_rend_JAMAIS_un_montant_NON_FINI():
    """LE DÉFAUT LE PLUS COÛTEUX, ET LE PLUS DISCRET. `matBudget` divisait le
    budget du secteur par une référence : sur une absence, k valait NaN et se
    propageait dans les dix postes, puis dans le total, le TJM moyen et le coût
    mensuel. Un tableau de coûts entièrement faux, d'apparence normale, qui ne
    lève aucune erreur. La règle mesure le TOTAL CALCULÉ, pas la présence d'un
    garde-fou dans la source."""
    for k, v in JOUE.items():
        assert v["fini"], "%s : le total du budget n'est pas un nombre fini" % k
    for k in _cadres():
        assert JOUE[k]["lignes"] == 0, (
            "%s : un tableau de budget est construit sans budget relevé" % k)
    for k in _releves():
        assert JOUE[k]["lignes"] > 0 and JOUE[k]["total"] > 0, k


def test_la_moyenne_d_un_socle_VIDE_ne_se_lit_pas_comme_une_note_basse():
    """`Object.keys(pillars).reduce(...)/8` rendait 0 sur un socle vide, et 0
    se lit « maturité nulle » — un jugement porté sur un secteur qu'on n'a
    justement pas observé. La moyenne ne doit exister que là où le socle
    existe ; ailleurs, c'est le questionnaire du client qui fait foi."""
    for k in _cadres():
        assert JOUE[k]["moyenne"] == 0, k
        # ET LA CONSÉQUENCE : la page ne doit PAS afficher cette moyenne. La
        # règle suivante mesure la mention qui la remplace.
        assert JOUE[k]["mention"], "%s ne dit pas pourquoi son socle est vide" % k
    for k in _releves():
        assert 0 < JOUE[k]["moyenne"] <= 5, (k, JOUE[k]["moyenne"])
        assert JOUE[k]["mention"] == "", k


def test_la_moyenne_divise_par_CE_QU_ELLE_COMPTE_et_non_par_huit():
    """UN PIÈGE QUE LA PREMIÈRE VERSION PORTAIT. Diviser par 8 en dur donne un
    résultat juste tant qu'il y a exactement huit piliers, et faux en silence
    le jour où un neuvième arrive — ou le jour où un profil n'en porte que
    six. La règle éprouve un socle volontairement partiel."""
    r = _executer("""
      var soc = {calibre:true, pillars:{a:4, b:2}};
      process.stdout.write(JSON.stringify({m: matMoyenneSocle(soc)}));
    """)
    assert r["m"] == 3, (
        "la moyenne divise par un nombre fixe : deux piliers à 4 et 2 donnent "
        "%r au lieu de 3" % r["m"])


# ═══════════════════════════════════════════════════════════════════════════
#  CE QUE L'ÉCRAN EN DIT
# ═══════════════════════════════════════════════════════════════════════════


def test_la_mention_du_socle_est_PEINTE_et_pas_seulement_calculee():
    """Une mention calculée que la page n'affiche pas ne protège de rien."""
    assert 'id="mat-socle-mention"' in MOTEUR, (
        "la bande qui dit le socle n'est plus posée par le peintre")
    bloc = MOTEUR[MOTEUR.index("if(!soc.calibre){"):]
    bloc = bloc[:bloc.index("/* Export bar */")]
    assert "socle non calibré" in bloc.lower()
    assert "audit reste entier" in bloc.lower(), (
        "l'écran ne dit pas que l'audit reste utilisable — le lecteur croit "
        "être devant une impasse")
    # ÉMIS NE VEUT PAS DIRE LU : la classe doit exister dans la feuille servie.
    assert ".mat-socle-cadre{" in PAGE, "la bande n'a aucun style : invisible"
    style = PAGE[PAGE.index(".mat-socle-cadre{"):]
    style = style[:style.index("}")]
    assert "display:none" not in style.replace(" ", "")


def test_la_modale_BUDGET_dit_pourquoi_au_lieu_de_lever():
    """Sans garde-fou elle levait sur `b.sector` : un bouton qui ne fait rien
    et une erreur en console. Le lecteur en conclut que l'outil est cassé,
    alors que la seule chose vraie à dire est qu'on n'a pas ce chiffre-là."""
    bloc = MOTEUR[MOTEUR.index("window.matOpenBudget = function(){"):]
    bloc = bloc[:bloc.index("function budgetBodyHTML")]
    assert "if(!b){" in bloc, "la modale ne se garde pas d'un budget absent"
    garde = bloc[bloc.index("if(!b){"):bloc.index("return;", bloc.index("if(!b){"))]
    assert "missions réelles" in garde
    assert "modal.classList.add" in garde, (
        "la modale se construit mais ne s'ouvre pas : le bouton reste muet")


def test_le_comparatif_sectoriel_NE_COMPARE_PAS_a_une_reference_absente():
    """0 % se lit « ce secteur est au plus bas » et non « on ne l'a pas
    relevé ». Les treize profils de cadre doivent sortir du comparatif avec un
    tiret, qui ne se confond avec aucune valeur."""
    bloc = MOTEUR[MOTEUR.index("var rows = Object.keys(window.MAT_SECTORS)"):]
    bloc = bloc[:bloc.index("holder.innerHTML")]
    assert "window.matSocle" in bloc, (
        "le comparatif lit les piliers sans passer par la porte du socle")
    assert "maturityAvg = null" in bloc.replace("\n", " ") or \
           "? null" in bloc or ": null" in bloc, bloc[-300:]


def test_le_socle_declare_dans_le_module_et_dans_l_audit_ne_divergent_pas():
    """Deux déclarations, une seule vérité — et aucune des deux erreurs
    possibles ne lèverait quoi que ce soit à l'exécution."""
    audit = {k: v.get("socle") for k, v in _profils().items()}
    module = {k: p["socle"] for k, p in N.PROFILS_SENTINEL.items()}
    assert audit == module, {k: (module.get(k), audit.get(k))
                             for k in set(audit) | set(module)
                             if audit.get(k) != module.get(k)}


def test_les_textes_LUS_sont_consignes_avec_leur_version():
    """Une lecture qu'on ne peut pas refaire n'est pas une lecture. La date de
    version compte autant que la référence : l'annexe III a été modifiée par le
    règlement (UE) 2026/1744, et une lecture d'avant serait fausse."""
    assert len(N.SOURCES_REGIMES) >= 3
    for s in N.SOURCES_REGIMES:
        assert s["acte"] and s["celex"] and s["version_lue"] and s["consulte_le"]
        assert len(s["retenu"]) > 60, s["acte"]
    actes = " ".join(s["acte"] for s in N.SOURCES_REGIMES)
    assert "2024/1689" in actes and "2022/2555" in actes
    versions = " ".join(s["version_lue"] for s in N.SOURCES_REGIMES)
    assert "2026/1744" in versions, (
        "la version consolidée de l'annexe III n'est pas datée de son "
        "règlement modificatif : une lecture d'avant serait fausse")


def test_chaque_profil_de_cadre_dit_ce_que_CHACUN_DES_DEUX_TEXTES_etablit():
    """UN PROFIL QUI NE CITERAIT AUCUN TEXTE serait une opinion sur un secteur.
    Ce qui distingue ces treize d'un remplissage est qu'ils rendent compte de la
    LECTURE — y compris pour dire qu'un texte ne les nomme pas, ce qui est un
    résultat et non un trou.

    LA RÈGLE EXIGE LES DEUX TEXTES SÉPARÉMENT, et c'est ce qui la rend utile.
    Une première version cherchait « une annexe » n'importe où dans le profil :
    elle était satisfaite par une seule citation, et trois des treize profils
    passaient en ne disant RIEN de l'un des deux textes — `education` et
    `services_personne` muets sur NIS2, `extractif` muet sur l'annexe III.
    C'est la mutation qui l'a montré : retirer un ancrage laissait la règle
    verte parce qu'il en restait un autre, sur l'autre texte.
    """
    profils = _profils()
    nis2 = re.compile(r"NIS2|annexe\s+I{1,2}\b", re.I)
    iaact = re.compile(r"annexe\s+III\b", re.I)
    muets = {}
    for cle in _cadres():
        texte = " ".join(s["t"] + " " + s["d"] for s in profils[cle]["specifics"])
        absents = [n for n, m in (("NIS2", nis2), ("annexe III", iaact))
                   if not m.search(texte)]
        if absents:
            muets[cle] = absents
    assert not muets, (
        "ces profils de cadre ne disent rien de l'un des deux textes lus : %r"
        % muets)
