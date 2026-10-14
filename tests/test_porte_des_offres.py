# -*- coding: utf-8 -*-
"""LA PORTE DES OFFRES, ET CE QU'ELLE DOIT DIRE QUAND ELLE REFUSE.

CE QUI A DÉCLENCHÉ CE FICHIER. Une demande : « lorsqu'on clique sur une des
16 normes maîtrisées dans Sentinel, il faut que l'on se connecte directement
sur la norme concernée et qu'elle soit affichée à l'écran. »

ET LA RÉPONSE N'ÉTAIT PAS DANS LA CHAÎNE DU CLIC. Mesuré dans un navigateur,
avec un compte réel au plan Gratuit, après une connexion par le formulaire,
sur `/sentinel?goto=rgpd-hub` :

    URL                    /sentinel?goto=rgpd-hub
    écran peint            p-apercu  (l'Observatoire)
    titre                  « Observatoire IA — Sentinel »
    onglets verrouillés    106 sur 111
    modale                 « Module verrouillé »

La carte portait son lien, la porte reportait la destination, `__authDest()`
la rendait, `hubGo` trouvait l'onglet, `go()` était appelé avec lui. Et
l'écran demandé ne s'affichait pas : c'est l'OFFRE DU COMPTE qui refusait le
module. Ce n'est pas un défaut — c'est le modèle commercial, et il est écrit
dans le fichier : « Les offres Pro et Entreprise sont attribuées par
l'administration CONSEILPREV APRÈS confirmation de paiement. »

TROIS DÉFAUTS, EUX, EN SONT BIEN DES DÉFAUTS, ET CE FICHIER LES GARDE :

 1. LE REFUS NE DISAIT PAS CE QU'IL REFUSAIT. « Ce module n'est pas inclus
    dans votre plan Gratuit » — alors que le lecteur venait de cliquer sur une
    carte nommée « RGPD », depuis une page qui annonce seize normes
    maîtrisées. Un refus anonyme se lit comme un lien cassé.

 2. LE REFUS N'ÉTAIT PAS STABLE. `planIsAllowed` autorise tant que l'offre
    n'est pas connue — `if(!p) return true` —, l'offre est demandée à 300 ms,
    et le lien profond partait à 350 ms. Le même clic, sur la même norme, par
    le même compte, ouvrait le module ou affichait la modale selon lequel des
    deux arrivait d'abord. Une porte qui s'ouvre sur un délai réseau n'est
    pas une porte — ni pour le lecteur, ni pour ce qu'elle protège.

 3. LE BANDEAU ANNONÇAIT UN NOMBRE DE MODULES ÉCRIT À LA MAIN, démenti par la
    liste qui le détermine, et que personne ne recompte.

UNE DETTE EST OUVERTE ICI, ET ELLE EST DÉCLARÉE PLUTÔT QUE TAIRE. La ligne
« Vous avez demandé : … » est du français neuf servi à l'écran, et le
dictionnaire ne la porte pas. Ce n'est pas un oubli isolé : la modale est
assemblée à partir de littéraux français dont un seul — « Module
verrouillé » — figure au dictionnaire. Et l'inventaire ne peut pas la voir :
il sonde des routes, et cette modale n'apparaît qu'à un compte dont l'offre
refuse un écran. Le plancher de couverture ne la compte donc pas, et il ne
descend pas. Le bandeau, lui, est désormais DANS le dictionnaire par
construction : « — Accès limité à # modules. » y était déjà, avec son dièse ;
c'est le nombre écrit à la main qui en sortait.

CE QUE CES RÈGLES NE FONT PAS. Elles ne décident pas quels modules relèvent
de quelle offre : c'est une décision commerciale, et une règle qui la
figerait interdirait de la changer. Elles exigent seulement que la porte dise
ce qu'elle fait, et qu'elle le fasse toujours pareil.
"""
import io
import os
import re

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = io.open(os.path.join(_RACINE, "sentinel.page.js"), encoding="utf-8").read()


def _lien_profond():
    d = JS.index("window.sentinelGotoDeepLink = function()")
    return JS[d:JS.index("\n", d)]


def _porte():
    """LA PORTE : l'enveloppe de `go()` qui lit l'offre et refuse."""
    d = JS.index("var _planOrigGo = window.go;")
    return JS[d:JS.index("\n};", d)]


def test_la_lecture_du_fichier_trouve_bien_les_trois_morceaux():
    """LE GARDE-FOU. Trois règles lisent trois extraits ; si l'un cessait
    d'être reconnaissable, elles chercheraient dans du vide et passeraient."""
    assert 100 < len(_porte()) < 1200, "la porte des offres ne se lit plus"
    assert 400 < len(_lien_profond()) < 2500, "le lien profond ne se lit plus"
    assert "function planIsAllowed(id)" in JS, "planIsAllowed a disparu"
    assert "function sentinelLockPrompt(" in JS, "la modale de verrou a disparu"


# ═══════════════════════════════════════════════════════════════════════════
#  1. LE REFUS EST TOUJOURS LE MÊME — LE LIEN PROFOND ATTEND L'OFFRE
# ═══════════════════════════════════════════════════════════════════════════

def test_le_lien_profond_ATTEND_que_l_offre_du_compte_soit_connue():
    """SANS CETTE ATTENTE, LE VERDICT EST TIRÉ AU SORT PAR LE RÉSEAU."""
    corps = _lien_profond()
    assert "__SENTINEL_PLAN_CONNU" in corps, (
        "le lien profond n'attend plus de connaître l'offre : le même clic "
        "ouvrira le module ou le refusera selon un délai réseau")
    assert "clearInterval(attente)" in corps, (
        "l'attente du lien profond ne s'arrête plus : %r" % corps[:200])
    assert re.search(r"\+\+n <= \d+", corps), (
        "l'attente du lien profond n'est plus BORNÉE : une route tombée "
        "empêcherait le lien d'aboutir, ce qui est pire que le défaut corrigé")
    assert "hubGo(g)" in corps and "go(g)" in corps, (
        "le lien profond n'ouvre plus l'écran demandé")


def test_l_offre_est_declaree_CONNUE_sur_CHAQUE_sortie_de_sa_lecture():
    """UN DRAPEAU POSÉ SUR TROIS CHEMINS SUR QUATRE FAIT ATTENDRE LE LIEN
    PROFOND JUSQU'AU BOUT DE SA BORNE, puis partir quand même — c'est-à-dire
    exactement le défaut qu'on corrige, mais six secondes plus tard.

    LES QUATRE SORTIES, ET ELLES COMPTENT TOUTES : pas de session, compte
    CONSEILPREV, compte client, et l'échec de la route."""
    d = JS.index("function sentinelFetchPlan()")
    corps = JS[d:JS.index("_auDomPret(sentinelFetchPlan", d)]
    sorties = [
        ("pas de session", "!d || !d.authenticated"),
        ("compte CONSEILPREV", "d.is_conseilprev || d.nom_entreprise === 'CONSEILPREV'"),
        ("compte client", "window.__SENTINEL_PLAN = d.plan || 'gratuit';"),
        ("échec de la route", ".catch(function(){"),
    ]
    for quoi, ancre in sorties:
        assert ancre in corps, (
            "la sortie « %s » de la lecture de l'offre n'est plus "
            "reconnaissable : la règle ne la mesure plus" % quoi)
        i = corps.index(ancre)
        fenetre = corps[i:i + 240]
        assert "__SENTINEL_PLAN_CONNU = true" in fenetre, (
            "la sortie « %s » ne déclare pas l'offre connue : le lien profond "
            "attendra sa borne entière puis partira sans savoir" % quoi)
    assert "window.__SENTINEL_PLAN_CONNU = false" in corps, (
        "l'offre n'est plus déclarée INCONNUE au départ : le drapeau vaudrait "
        "`undefined`, et `=== true` serait faux par accident plutôt que par "
        "mesure")


# ═══════════════════════════════════════════════════════════════════════════
#  2. LE REFUS NOMME CE QU'IL REFUSE
# ═══════════════════════════════════════════════════════════════════════════

def test_la_porte_passe_a_la_modale_L_ECRAN_qu_elle_refuse():
    """UNE MODALE QUI NE SAIT PAS CE QU'ON A DEMANDÉ NE PEUT PAS LE DIRE."""
    porte = _porte()
    assert "sentinelLockPrompt(id)" in porte, (
        "la porte refuse sans dire quel écran : la modale retombera sur « ce "
        "module » — %r" % porte)
    assert "function sentinelLockPrompt(id)" in JS, (
        "la modale n'accepte plus l'écran refusé")


def test_la_modale_NOMME_l_ecran_refuse_en_le_prenant_a_PAGE_META():
    """LE NOM VIENT DE LA TABLE QUI LE PORTE DÉJÀ, et pas d'une seconde liste.
    PAGE_META tient le libellé de chaque page et se traduit ; un libellé
    recopié ici serait français pour toujours."""
    d = JS.index("function sentinelLockPrompt(id)")
    corps = JS[d:JS.index("\n}\n", d)]
    assert "PAGE_META[id]" in corps, (
        "la modale ne prend plus le nom de l'écran dans PAGE_META")
    assert "Vous avez demandé" in corps, (
        "la modale ne dit plus ce qui a été demandé")
    assert "replace(/[&<>\"]/g" in corps, (
        "le nom de l'écran n'est plus échappé avant d'entrer dans la modale")


# ═══════════════════════════════════════════════════════════════════════════
#  3. LE BANDEAU COMPTE, IL N'ANNONCE PAS
# ═══════════════════════════════════════════════════════════════════════════

def test_le_bandeau_du_plan_gratuit_COMPTE_ses_modules():
    """LE MÊME DÉFAUT QUE « N NORMES MAÎTRISÉES », DÉJÀ PAYÉ UNE FOIS : un
    nombre écrit à la main au-dessus d'une liste qui en contient un autre.
    Le bandeau annonçait quatre modules ; la liste n'en déclarait pas quatre.
    """
    d = JS.index("function sentinelPlanBanner(plan)")
    corps = JS[d:JS.index("\n}\n", d)]
    assert "PLAN_GRATUIT_MODULES.length" in corps, (
        "le bandeau n'est plus dérivé de la liste des modules du plan Gratuit")
    ecrits = re.findall(r"(?:à|a)\s+(\d+)\s+modules", corps)
    assert not ecrits, (
        "le bandeau annonce encore un nombre écrit à la main : %s" % ecrits)


def test_la_liste_des_modules_du_plan_gratuit_est_LISIBLE_et_non_vide():
    """CE DONT LA RÈGLE PRÉCÉDENTE DÉPEND. Une liste vide ferait annoncer
    « 0 modules » et la dérivation passerait pour juste."""
    m = re.search(r"var PLAN_GRATUIT_MODULES = \[([^\]]*)\]", JS)
    assert m, "la liste des modules du plan Gratuit ne se lit plus"
    modules = [x.strip().strip("'\"") for x in m.group(1).split(",") if x.strip()]
    assert len(modules) >= 3, (
        "le plan Gratuit ne déclare que %d module(s) : %s" % (len(modules), modules))
    assert "apercu" in modules, (
        "l'Observatoire n'est plus dans le plan Gratuit — c'est l'écran sur "
        "lequel la porte renvoie : un compte Gratuit n'aurait plus AUCUN "
        "écran ouvert")
