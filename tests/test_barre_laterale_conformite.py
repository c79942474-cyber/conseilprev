# -*- coding: utf-8 -*-
"""« VOTRE MISE EN CONFORMITÉ RÉGLEMENTAIRE » — LES QUATRE TIROIRS.

CE QUI A DÉCLENCHÉ CE FICHIER. Une demande : « dans le menu latéral de
Sentinel, créer et regrouper sous un menu principal “Votre Mise en Conformité
Réglementaire” : insérer avec des listes déroulantes RGPD & Privacy, ISO 42001,
NIS2, CRA ».

DEUX PIÈGES DANS CETTE DEMANDE, ET AUCUN NE SE VOIT À L'ŒIL.

  1. LE FILTRE DE LA BARRE LATÉRALE PARCOURT LES FRÈRES d'une `.sb-section`
     jusqu'à la suivante. Écrire le titre de famille comme une section de plus
     aurait coupé le groupe RGPD en deux : neuf onglets rangés sous un titre
     qui n'est pas le leur, et un filtre qui compte juste et affiche faux.

  2. LE PLI ET LE FILTRE ÉCRIVENT SUR LE MÊME ÉCRAN. Si les deux se servaient
     de `hidden`, taper « nis2 » dans un groupe replié aurait rendu
     « 5 onglets sur 95 » au compteur et une colonne où l'on n'en voit aucun.
     Le compte aurait eu raison et l'écran tort — la pire des deux façons de
     se tromper, parce qu'on croit l'écran.

CE QUE CES RÈGLES ÉPROUVENT. Le VRAI balisage de sentinel.html et le VRAI bloc
de sentinel.page.js, exécutés sous node avec un DOM minimal. Une règle qui
chercherait « sbReplier » dans la source serait verte le jour où le nom ne
figurerait plus que dans un commentaire.

CE QU'ELLES NE PEUVENT PAS FAIRE. Dire ce que le navigateur affiche : `hidden`
et `data-replie` sont des attributs, et c'est la feuille de style qui les rend
invisibles. Une règle ci-dessous vérifie que la feuille de style le fait.
"""
import io
import json
import os
import re
import shutil
import subprocess
import tempfile

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_HARNAIS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "_dom_barre_laterale.js")
HTML = io.open(os.path.join(_RACINE, "sentinel.html"), encoding="utf-8").read()
NODE = shutil.which("node")

# L'ORDRE EST CELUI QUI A ÉTÉ DEMANDÉ, et il n'est pas alphabétique : RGPD
# d'abord parce que c'est le cadre que tout le monde porte déjà, CRA en
# dernier parce que c'est le plus récent.
#
# ISO 27001 S'EST INSÉRÉE AVANT ISO 42001, ET PAS AILLEURS. Les deux normes
# partagent la structure harmonisée des articles 4 à 10, et 42001 se GREFFE
# sur ce socle — c'est ce que déclare le pont du moteur, dans les deux sens.
# Les ranger dans l'autre ordre ferait lire la greffe avant le support.
# LE TAUX PASSE DEVANT, ET CE N'EST PAS UNE PRÉFÉRENCE D'AFFICHAGE. Les sept
# tiroirs qui suivent sont les instruments, un par référentiel ; celui-ci est
# la SYNTHÈSE de tous — il dit où l'on en est sur chacun et par quoi
# commencer. Le placer après eux obligerait à connaître les sept avant de
# savoir lequel ouvrir, ce qui est exactement la question à laquelle il
# répond.
TIROIRS = ["taux-conformite",
           "rgpd-et-privacy", "iso27001", "iso42001", "nis2", "cra",
           "nist-ai-rmf", "owasp-llm"]


def _executer(scenario):
    """Exécute le vrai bloc de la barre latérale sur le vrai balisage."""
    if not NODE:
        pytest.skip("node absent : la barre latérale ne peut pas être exécutée")
    with tempfile.TemporaryDirectory() as d:
        chemin = os.path.join(d, "s.js")
        io.open(chemin, "w", encoding="utf-8").write(
            "require(%s);\n" % json.dumps(_HARNAIS) + scenario)
        r = subprocess.run(
            [NODE, chemin, os.path.join(_RACINE, "sentinel.html"),
             os.path.join(_RACINE, "sentinel.page.js")],
            capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        pytest.fail("le scénario ne s'exécute pas :\n%s"
                    % (r.stderr or "")[-1500:])
    return json.loads(r.stdout)


_OUTILS = r"""
const nav = global.__nav;
function section(grp){
  return nav.querySelectorAll('.sb-section').filter(function(s){
    return s.getAttribute('data-grp') === grp; })[0] || null;
}
function items(grp){
  var sec = section(grp); if(!sec) return [];
  var n = sec.nextElementSibling, r = [];
  while(n && !n.classList.contains('sb-section')){
    if(n.classList.contains('sb-item')) r.push(n);
    n = n.nextElementSibling;
  }
  return r;
}
function plies(grp){ return items(grp).filter(function(i){
  return i.hasAttribute('data-replie'); }).length; }
function visibles(grp){ return items(grp).filter(function(i){
  return !i.hasAttribute('hidden') && !i.hasAttribute('data-replie'); }).length; }
function famille(){ return nav.querySelectorAll('.sb-famille')[0]; }
function rendre(o){ console.log(JSON.stringify(o)); }
"""


# ═══════════════════════════════════════════════════════════════════════════
#  1. LA STRUCTURE — CE QUE LA DEMANDE DEMANDAIT
# ═══════════════════════════════════════════════════════════════════════════

def test_la_famille_existe_et_porte_l_intitule_demande():
    """L'INTITULÉ EST CELUI QUI A ÉTÉ DEMANDÉ, mot pour mot. Le reformuler en
    « Conformité » aurait été plus court et n'aurait pas été ce qu'on a
    commandé."""
    assert 'class="sb-famille" data-fam="conformite"' in HTML
    assert "Votre Mise en Conformité Réglementaire" in HTML


def test_le_titre_de_famille_n_est_PAS_une_sb_section():
    """LE PIÈGE N°1, ÉPROUVÉ SUR LE BALISAGE. `sbFiltrer` parcourt les frères
    d'une `.sb-section` jusqu'à la suivante : un titre de famille écrit comme
    une section aurait coupé le groupe RGPD en deux, et ses neuf onglets
    seraient comptés sous un titre qui n'est pas le leur."""
    d = HTML.index('class="sb-famille"')
    # LA BALISE COMMENCE AVANT L'ATTRIBUT, DONC ON REMONTE. Chercher « <div »
    # en avant trouvait la balise SUIVANTE, et la règle mesurait un autre
    # élément que celui qu'elle nomme — le défaut même qu'elle est censée
    # attraper ailleurs.
    balise = HTML[HTML.rindex("<div", 0, d):HTML.index(">", d)]
    assert 'class="sb-famille"' in balise, (
        "la balise relue n'est pas celle du titre de famille : %r" % balise)
    assert "sb-section" not in balise, (
        "le titre de famille ne doit pas être une `.sb-section` : %r" % balise)


def test_les_tiroirs_sont_ceux_demandes_et_dans_cet_ordre():
    """RGPD & PRIVACY, ISO 27001, ISO 42001, NIS 2, CRA — l'ordre voulu, ni
    alphabétique ni chronologique. 27001 précède 42001 parce que c'est le
    socle sur lequel 42001 se greffe."""
    r = _executer(_OUTILS + r"""
rendre(nav.querySelectorAll('.sb-section[data-fam]')
  .map(function(s){ return s.getAttribute('data-grp'); }));
""")
    assert r == TIROIRS, "les tiroirs rendus : %s" % r


def test_chaque_tiroir_est_annonce_repliable_a_l_assistance_technique():
    """UN TIROIR QUI NE DIT PAS QU'IL S'OUVRE N'EST PAS UN TIROIR pour qui
    navigue au clavier ou au lecteur d'écran : c'est un titre inerte."""
    r = _executer(_OUTILS + r"""
rendre(nav.querySelectorAll('.sb-section[data-fam]').map(function(s){
  return {grp:s.getAttribute('data-grp'), role:s.getAttribute('role'),
          tab:s.getAttribute('tabindex'), aria:s.hasAttribute('aria-expanded')};
}));
""")
    for x in r:
        assert x["role"] == "button", "%s n'a pas de rôle de bouton" % x["grp"]
        assert x["tab"] == "0", "%s n'est pas atteignable au clavier" % x["grp"]
        assert x["aria"], "%s n'annonce pas son état d'ouverture" % x["grp"]


def test_le_pli_a_son_propre_attribut_et_la_feuille_de_style_le_masque():
    """LE PIÈGE N°2, ÉPROUVÉ SUR LA FEUILLE DE STYLE. Le pli n'écrit pas
    `hidden` — c'est l'attribut du filtre — donc quelque chose doit rendre
    `data-replie` invisible, sinon le pli ne plie rien."""
    assert ".sb-item[data-replie]" in HTML
    d = HTML.index(".sb-item[data-replie]")
    regle = HTML[d:HTML.index("}", d)]
    assert "display:none" in regle.replace(" ", ""), (
        "`data-replie` ne masque rien : %r" % regle)


# ═══════════════════════════════════════════════════════════════════════════
#  2. LE PLI — PAR DÉFAUT FERMÉ, ET IL SE SOUVIENT
# ═══════════════════════════════════════════════════════════════════════════

def test_tous_les_tiroirs_sont_replies_au_premier_chargement():
    """C'EST LA RAISON D'ÊTRE DU REGROUPEMENT. Quatre cadres dépliés, ce sont
    vingt-trois onglets d'affilée — exactement ce que le regroupement devait
    faire disparaître."""
    r = _executer(_OUTILS + r"""
window.sbRestaurerPlis();
var o = {};
%s.forEach(function(g){ o[g] = [plies(g), items(g).length]; });
rendre(o);
""" % json.dumps(TIROIRS))
    for grp, (plies, total) in r.items():
        assert total > 0, "le tiroir %s n'a aucun onglet" % grp
        assert plies == total, (
            "le tiroir %s n'est pas replié au chargement : %d/%d"
            % (grp, plies, total))


def test_les_groupes_hors_famille_ne_sont_PAS_replies():
    """LE TÉMOIN QUI INTERDIT DE TOUT REPLIER. Si le pli s'appliquait à toutes
    les sections, la barre latérale entière se refermerait — et cette règle
    passerait sur un moteur qui ne fait aucune distinction."""
    r = _executer(_OUTILS + r"""
window.sbRestaurerPlis();
rendre({pilotage: plies('pilotage'), juridique: plies('juridique'),
        total_pilotage: items('pilotage').length});
""")
    assert r["total_pilotage"] > 0
    assert r["pilotage"] == 0 and r["juridique"] == 0, (
        "seuls les tiroirs de la famille se replient : %s" % r)


def test_un_clic_deplie_et_un_second_replie():
    r = _executer(_OUTILS + r"""
window.sbRestaurerPlis();
var sec = section('nis2'), o = {};
o.avant = visibles('nis2');
window.sbReplier(sec); o.apres_un_clic = visibles('nis2');
o.aria_ouvert = sec.getAttribute('aria-expanded');
window.sbReplier(sec); o.apres_deux_clics = visibles('nis2');
o.aria_ferme = sec.getAttribute('aria-expanded');
o.total = items('nis2').length;
rendre(o);
""")
    assert r["avant"] == 0
    assert r["apres_un_clic"] == r["total"] > 0
    assert r["apres_deux_clics"] == 0
    assert (r["aria_ouvert"], r["aria_ferme"]) == ("true", "false")


def test_le_pli_se_souvient_d_une_visite_a_l_autre():
    """UN TIROIR QUI SE REFERME À CHAQUE CHANGEMENT D'ONGLET n'est pas un
    tiroir, c'est une animation."""
    r = _executer(_OUTILS + r"""
window.sbRestaurerPlis();
window.sbReplier(section('cra'));
var memoire = Object.assign({}, global.__magasin);
/* SECONDE VISITE : on rejoue la restauration sur le même stockage. */
window.sbRestaurerPlis();
rendre({memoire: memoire, visibles_cra: visibles('cra'),
        total_cra: items('cra').length});
""")
    assert r["memoire"].get("sentinel.sb.pli.cra") == "0", (
        "le pli déplié n'est pas mémorisé : %s" % r["memoire"])
    assert r["visibles_cra"] == r["total_cra"], (
        "le tiroir déplié doit le rester à la visite suivante")


def test_un_stockage_refuse_ne_casse_pas_le_pli():
    """NAVIGATION PRIVÉE, STOCKAGE BLOQUÉ : le pli doit fonctionner sans se
    souvenir, pas lever."""
    r = _executer(_OUTILS + r"""
global.localStorage = {
  getItem: function(){ throw new Error('stockage refusé'); },
  setItem: function(){ throw new Error('stockage refusé'); } };
window.sbRestaurerPlis();
var sec = section('nis2');
window.sbReplier(sec);
rendre({visibles: visibles('nis2'), total: items('nis2').length});
""")
    assert r["visibles"] == r["total"] > 0, (
        "sans stockage, le pli doit quand même s'ouvrir : %s" % r)


# ═══════════════════════════════════════════════════════════════════════════
#  3. LE FILTRE — IL GAGNE TOUJOURS, ET IL N'EFFACE RIEN
# ═══════════════════════════════════════════════════════════════════════════

def test_le_filtre_ouvre_un_tiroir_replie_qui_contient_un_resultat():
    """LE PIÈGE N°2, ÉPROUVÉ SUR LE COMPORTEMENT. Sans cette règle, taper
    « nis 2 » dans un tiroir replié rendait « 6 onglets sur 69 » au compteur
    et une colonne où l'on n'en voyait aucun."""
    r = _executer(_OUTILS + r"""
window.sbRestaurerPlis();
var avant = visibles('nis2');
window.sbFiltrer('nis 2');
rendre({avant: avant, pendant: visibles('nis2'), total: items('nis2').length,
        compteur: global.__boites['sb-filtre-cpt'].textContent});
""")
    assert r["avant"] == 0, "le tiroir doit partir replié"
    assert r["pendant"] == r["total"] > 0, (
        "le filtre doit ouvrir le tiroir qui porte le résultat : %s" % r)
    assert r["compteur"], "le compteur du filtre doit dire combien"


def test_le_filtre_n_ecrit_PAS_dans_la_memoire_du_pli():
    """UNE RECHERCHE N'EST PAS UNE DÉCISION. Si le filtre mémorisait
    l'ouverture, chercher « nis2 » une fois aurait déplié ce tiroir pour
    toujours."""
    r = _executer(_OUTILS + r"""
window.sbRestaurerPlis();
window.sbFiltrer('nis 2');
var pendant = Object.assign({}, global.__magasin);
window.sbFiltrer('');
rendre({memoire: pendant, apres_effacement: visibles('nis2')});
""")
    assert "sentinel.sb.pli.nis2" not in r["memoire"], (
        "le filtre a écrit dans la mémoire du pli : %s" % r["memoire"])
    assert r["apres_effacement"] == 0, (
        "le filtre effacé, la mémoire du pli reprend la main")


def test_un_tiroir_deplie_a_la_main_le_reste_apres_un_filtre():
    """L'AUTRE SENS, et il compte autant : une décision de l'utilisateur ne
    doit pas être annulée par une recherche."""
    r = _executer(_OUTILS + r"""
window.sbRestaurerPlis();
window.sbReplier(section('cra'));       /* ouvert à la main */
window.sbFiltrer('rgpd');
window.sbFiltrer('');
rendre({visibles_cra: visibles('cra'), total_cra: items('cra').length});
""")
    assert r["visibles_cra"] == r["total_cra"], (
        "le tiroir ouvert à la main doit se retrouver ouvert : %s" % r)


def test_le_titre_de_famille_disparait_quand_aucun_tiroir_ne_survit():
    """RIEN NE MASQUE LE TITRE DE FAMILLE AUTOMATIQUEMENT — il n'est pas une
    `.sb-section`, et c'est justement ce qui l'exposait : un filtre qui ne
    garde que « Pilotage » laissait « Votre Mise en Conformité Réglementaire »
    planté au-dessus du vide."""
    r = _executer(_OUTILS + r"""
window.sbRestaurerPlis();
window.sbFiltrer('pilotage');
var masquee = famille().hasAttribute('hidden');
window.sbFiltrer('rgpd');
var revenue = !famille().hasAttribute('hidden');
rendre({masquee: masquee, revenue: revenue});
""")
    assert r["masquee"] is True, (
        "le titre de famille reste affiché au-dessus du vide")
    assert r["revenue"] is True, (
        "le titre doit revenir dès qu'un de ses tiroirs a un résultat")


def test_un_filtre_sans_resultat_rend_la_barre_entiere():
    """LE COMPORTEMENT EXISTANT, QUE LE REMANIEMENT NE DOIT PAS CASSER. Un
    champ rempli par le gestionnaire de mots de passe ne doit pas vider la
    navigation — c'est un défaut déjà corrigé une fois ici."""
    r = _executer(_OUTILS + r"""
window.sbRestaurerPlis();
window.sbFiltrer('zzz-introuvable-aaa');
rendre({rgpd: visibles('rgpd-et-privacy'),
        pilotage: visibles('pilotage'),
        famille_masquee: famille().hasAttribute('hidden'),
        compteur: global.__boites['sb-filtre-cpt'].textContent});
""")
    assert r["pilotage"] > 0 and r["rgpd"] > 0, (
        "un filtre sans résultat rend la liste entière : %s" % r)
    assert r["famille_masquee"] is False
    assert "aucun onglet" in r["compteur"]


def test_le_filtre_continue_de_masquer_hors_famille():
    """LE TÉMOIN QUI INTERDIT DE NEUTRALISER LE FILTRE. Après le remaniement,
    filtrer doit encore filtrer : une règle qui ne vérifierait que
    l'OUVERTURE des tiroirs passerait sur un `sbFiltrer` devenu inerte."""
    r = _executer(_OUTILS + r"""
window.sbRestaurerPlis();
window.sbFiltrer('rgpd');
rendre({pilotage: visibles('pilotage'), rgpd: visibles('rgpd-et-privacy')});
""")
    assert r["pilotage"] == 0, (
        "les groupes sans résultat doivent être masqués : %s" % r)
    assert r["rgpd"] > 0


def test_le_pli_ecrit_data_replie_et_JAMAIS_hidden():
    """LA SÉPARATION DES DEUX ATTRIBUTS, MESURÉE À L'EXÉCUTION.

    CE QUE LA BATTERIE DE MUTATIONS A MONTRÉ. Remplacer `data-replie` par
    `hidden` dans le pli faisait tomber deux règles — celle du compteur et
    celle du pli par défaut — mais aucune ne DISAIT la vraie faute, qui est
    que les deux mécanismes se marchent dessus. Une règle qui tombe sans
    nommer la cause envoie chercher au mauvais endroit.

    LA RÈGLE INVERSE COMPTE AUTANT : le filtre, lui, doit écrire `hidden` et
    jamais `data-replie`. Sinon effacer le filtre laisserait des onglets
    repliés que personne n'a repliés."""
    r = _executer(_OUTILS + r"""
window.sbRestaurerPlis();
var apres_pli = items('nis2').map(function(i){
  return [i.hasAttribute('data-replie'), i.hasAttribute('hidden')]; });
window.sbReplier(section('nis2'));            /* déplié */
window.sbFiltrer('rgpd');                     /* nis2 masqué par le filtre */
var apres_filtre = items('nis2').map(function(i){
  return [i.hasAttribute('data-replie'), i.hasAttribute('hidden')]; });
rendre({pli: apres_pli, filtre: apres_filtre});
""")
    for replie, cache in r["pli"]:
        assert replie is True, "le pli n'a pas posé `data-replie`"
        assert cache is False, (
            "le pli a posé `hidden` — c'est l'attribut du filtre, et les deux "
            "s'écraseront")
    for replie, cache in r["filtre"]:
        assert cache is True, "le filtre n'a pas posé `hidden`"
        assert replie is False, (
            "le filtre a posé `data-replie` — effacer le filtre laisserait "
            "des onglets repliés que personne n'a repliés")


def test_aucun_appel_de_la_barre_laterale_n_est_neutralise_par_une_branche_morte():
    """CE QUE LA BATTERIE DE MUTATIONS A MONTRÉ, ET QUI VALAIT LA PEINE.

    Une règle qui cherche `sbOuvrirFamilleDeCourant` dans le corps de `go()`
    reste VERTE quand on remplace la condition par `if (false)` : le nom est
    toujours là, l'appel ne se fait plus. C'est la forme la plus discrète de
    code mort — celle qui garde toutes ses preuves d'existence.

    LA RÈGLE MESURE LA CLASSE, pas le cas. `if (false)`, `if (0)`,
    `while (false)` : aucune de ces formes n'a de raison d'exister dans ce
    fichier, et chacune neutralise un appel en le laissant lisible."""
    js = io.open(os.path.join(_RACINE, "sentinel.page.js"),
                 encoding="utf-8").read()
    mortes = re.findall(r"(?:if|while)\s*\(\s*(?:false|0)\s*\)", js)
    assert not mortes, (
        "%d branche(s) morte(s) dans sentinel.page.js : un appel neutralisé "
        "y garde son nom, et toute règle qui cherche ce nom reste verte — %s"
        % (len(mortes), mortes[:5]))


def test_chaque_panneau_de_la_famille_est_ouvert_par_un_onglet_du_menu():
    """CE QUE LA BATTERIE DE MUTATIONS A MONTRÉ. Faire pointer l'onglet
    « Ponts » vers le panneau de la déclaration d'applicabilité ne faisait
    tomber AUCUNE règle : le panneau visé existe, celui qui reste existe
    aussi, et le parcours guidé continue de le citer. Le panneau devenait
    simplement inatteignable depuis le menu — et rien ne le disait.

    LA RÈGLE LIT LES `go('…')` DES ONGLETS et exige que chacun des vingt-trois
    panneaux de la famille en reçoive un."""
    cibles = set(re.findall(r"onclick=\"go\('([a-z0-9-]+)'", HTML))
    attendus = ["iso27001", "iso27001-risques", "iso27001-soa",
                "iso27001-millesime",
                "iso42001", "iso42001-soa", "iso42001-certif", "iso42001-ponts",
                "nis2-qualifier", "nis2", "nis2-gouvernance",
                "nis2-signalement", "nis2-chiffre",
                "cra", "cra-role", "cra-ecarts", "cra-chiffre",
                "cra-signalement"]
    manquants = [p for p in attendus if p not in cibles]
    assert not manquants, (
        "ces panneaux n'ont plus d'onglet qui les ouvre : %s" % manquants)
    # LE GARDE-FOU : une lecture qui rendrait un ensemble vide ferait passer
    # la règle ci-dessus pour une comparaison de deux vides.
    assert len(cibles) > 50, (
        "seulement %d cibles lues dans le menu : la lecture est cassée"
        % len(cibles))


# ═══════════════════════════════════════════════════════════════════════════
#  4. LE COMPTEUR — DÉRIVÉ, JAMAIS ÉCRIT À LA MAIN
# ═══════════════════════════════════════════════════════════════════════════

def test_le_compte_de_la_famille_est_derive_du_menu():
    """« 7 ALERTES ACTIVES » ÉTAIT UN LIBELLÉ DE MENU DANS CE DÉPÔT, et il
    mentait dès la huitième. Un compte écrit à la main ment le jour où
    quelqu'un ajoute un onglet ailleurs."""
    r = _executer(_OUTILS + r"""
window.sbRestaurerPlis(); window.sbCompterFamilles();
var attendu = 0;
%s.forEach(function(g){ attendu += items(g).length; });
rendre({affiche: famille().querySelector('.sb-famille-n').textContent,
        attendu: attendu});
""" % json.dumps(TIROIRS))
    assert r["affiche"] == "%d onglets" % r["attendu"], (
        "le compte affiché (%r) ne suit pas le menu (%d)"
        % (r["affiche"], r["attendu"]))
    assert r["attendu"] >= 25, (
        "le garde-fou : une lecture qui rendrait zéro ferait passer la règle "
        "ci-dessus pour une comparaison de deux zéros")


def test_le_compte_de_la_famille_suit_le_filtre():
    """LE COMPTE TOMBE AU NOMBRE DE RÉSULTATS — DE TOUS LES TIROIRS.

    CE QUE CETTE RÈGLE MESURAIT AVANT, ET QUI ÉTAIT UNE COÏNCIDENCE. Elle
    comparait le compte affiché au nombre d'onglets du SEUL tiroir ISO 42001,
    et elle passait parce qu'aucun autre tiroir ne parlait d'ISO. Le jour où
    un onglet d'un autre tiroir a mentionné la norme — « ce qu'ISO 42001 ne
    couvre pas », sous OWASP — la règle est tombée, alors que le produit
    faisait exactement ce qu'il fallait : montrer les deux résultats. Elle
    mesurait donc la taille d'un tiroir, pas le suivi du filtre.

    ELLE COMPTE MAINTENANT LES ONGLETS RESTÉS VISIBLES DANS TOUTE LA FAMILLE,
    ce qui est la définition de « nombre de résultats ».
    """
    r = _executer(_OUTILS + r"""
window.sbRestaurerPlis();
window.sbFiltrer('iso 42001');
var vus = 0, ou = [];
%s.forEach(function(g){
  var n = visibles(g);
  vus += n;
  if(n) ou.push(g + ':' + n);
});
rendre({pendant: famille().querySelector('.sb-famille-n').textContent,
        vus: vus, ou: ou});
""" % json.dumps(TIROIRS))
    assert r["pendant"] == "%d onglets" % r["vus"], (
        "pendant un filtre, le compte doit tomber au nombre de résultats de "
        "TOUTE la famille : %r pour %d visible(s) — %s"
        % (r["pendant"], r["vus"], ", ".join(r["ou"])))
    assert r["vus"] >= 1, (
        "le garde-fou : un filtre qui ne laisse rien ferait passer la règle "
        "ci-dessus pour une comparaison de deux zéros")


# ═══════════════════════════════════════════════════════════════════════════
#  5. L'ONGLET COURANT NE SE CACHE PAS DANS UN TIROIR FERMÉ
# ═══════════════════════════════════════════════════════════════════════════

def test_l_onglet_courant_rouvre_son_tiroir():
    """SANS CETTE RÈGLE, arriver sur « Registre des traitements » par un lien
    direct affichait la page ET une barre latérale où RGPD était replié :
    l'onglet en cours, peint en terre cuite, était invisible. Le repère de
    position disparaissait au moment précis où il sert."""
    r = _executer(_OUTILS + r"""
window.sbRestaurerPlis();
/* `go()` RETIRE `on` DE TOUS LES ONGLETS AVANT D'EN PEINDRE UN. La page
   en sert déjà un — « Aperçu », dans Pilotage —, et sans ce nettoyage le
   scénario en aurait DEUX : `querySelector` rendrait le premier, et la
   règle mesurerait l'ouverture du mauvais tiroir. */
nav.querySelectorAll('.sb-item').forEach(function(i){ i.classList.remove('on'); });
var cible = items('nis2')[2];
cible.classList.add('on');
window.sbOuvrirFamilleDeCourant();
rendre({nis2: visibles('nis2'), total: items('nis2').length,
        rgpd: visibles('rgpd-et-privacy')});
""")
    assert r["nis2"] == r["total"] > 0, (
        "le tiroir de l'onglet courant doit s'ouvrir : %s" % r)
    assert r["rgpd"] == 0, (
        "et seulement celui-là — les autres restent repliés")


def test_la_page_ne_sert_QU_UN_SEUL_onglet_courant():
    """CE QUE LE DÉBOGAGE DE LA RÈGLE PRÉCÉDENTE A FAIT APPARAÎTRE.
    `sbOuvrirFamilleDeCourant` prend le PREMIER `.sb-item.on` du document. Si
    le balisage en servait deux — un oubli de copier-coller —, le tiroir
    ouvert au chargement serait celui du premier, pas celui de la page
    affichée, et le repère de position pointerait ailleurs.

    `go()` garantit l'unicité à l'exécution ; cette règle la garantit au
    repos, c'est-à-dire au tout premier affichage, avant que `go()` n'ait
    jamais couru."""
    assert HTML.count('class="sb-item on"') == 1, (
        "la page sert %d onglets marqués courants : le tiroir ouvert au "
        "chargement serait celui du premier"
        % HTML.count('class="sb-item on"'))
    assert HTML.count('aria-current="page"') == 1, (
        "un seul onglet doit s'annoncer courant à l'assistance technique")


def test_go_appelle_l_ouverture_du_tiroir_courant():
    """LE BRANCHEMENT, CHERCHÉ DANS `go()` ET NULLE PART AILLEURS. La fonction
    peut exister et n'être appelée par personne."""
    js = io.open(os.path.join(_RACINE, "sentinel.page.js"),
                 encoding="utf-8").read()
    d = js.index("function go(id, el, sec, pg) {")
    f = js.index("\n}\n", d)
    corps = js[d:f]
    assert "sbOuvrirFamilleDeCourant" in corps, (
        "`go()` n'ouvre pas le tiroir de l'onglet courant : un lien direct "
        "affichera la page sans son repère de position")


# ═══════════════════════════════════════════════════════════════════════════
#  6. LES DEUX NOUVEAUX MODULES SONT BRANCHÉS DE BOUT EN BOUT
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("grp,attendus", [
    ("iso27001", 4), ("iso42001", 4), ("nis2", 5)])
def test_chaque_nouveau_tiroir_porte_ses_onglets(grp, attendus):
    r = _executer(_OUTILS + "rendre(items(%s).length);" % json.dumps(grp))
    assert r == attendus, "%s porte %d onglets au lieu de %d" % (grp, r, attendus)


@pytest.mark.parametrize("pid", [
    "iso27001", "iso27001-risques", "iso27001-soa", "iso27001-millesime",
    "iso42001", "iso42001-soa", "iso42001-certif", "iso42001-ponts",
    "nis2-qualifier", "nis2", "nis2-gouvernance", "nis2-signalement",
    "nis2-chiffre"])
def test_chaque_onglet_neuf_mene_a_un_panneau_qui_existe(pid):
    """LA RECHERCHE PORTE SUR L'IDENTIFIANT, PAS SUR LA BALISE ENTIÈRE.

    CE QUE LA BATTERIE DE MUTATIONS A MONTRÉ. Écrite `'<div class="page"
    id="p-%s">' in HTML`, cette règle tombait dès qu'on ajoutait UN ATTRIBUT
    au panneau — un `data-`, un `role`, une classe. Elle annonçait « le
    panneau n'existe pas » alors qu'il existait : une règle qui tombe pour une
    raison sans rapport avec ce qu'elle prétend, exactement ce que ce dépôt
    traque ailleurs."""
    assert 'id="p-%s"' % pid in HTML, (
        "l'onglet %s mène à un panneau qui n'existe pas" % pid)


@pytest.mark.parametrize("cle,appel", [
    ("iso27001", "iso27Init"), ("iso42001", "isoInit"), ("nis2", "nis2Init")])
def test_go_amorce_le_module_meme_sans_passer_par_l_onglet(cle, appel):
    """UN LIEN DIRECT, UN PARCOURS GUIDÉ OU UN BOUTON « → » D'UN AUTRE ÉCRAN
    passent par `go()` sans exécuter le `onclick` de l'onglet. Sans ce
    branchement, la page s'affichait avec « Chargement… » qui ne finissait
    jamais."""
    js = io.open(os.path.join(_RACINE, "sentinel.page.js"),
                 encoding="utf-8").read()
    d = js.index("function go(id, el, sec, pg) {")
    corps = js[d:js.index("\n}\n", d)]
    assert "window.%s" % appel in corps, (
        "`go()` n'amorce pas %s : un lien direct vers un panneau %s "
        "n'affichera rien" % (appel, cle))
