"""SENTINEL N'AVAIT AUCUN ONGLET DE CONNEXION.

CE QUI A ÉTÉ SIGNALÉ. Douze rubriques, cinquante-deux onglets, et pas un seul
ne parlait du compte. La seule trace de la session était un bouton
« Déconnexion » dans la barre du haut, entre « ← Retour Accueil » et « Lancer un
audit » — trois boutons de même apparence, dont un seul engage.

ET RIEN NULLE PART NE PERMETTAIT DE SE CONNECTER. Un visiteur dont la session
expire pendant qu'il travaille voit les modules se vider un à un — Registre
vide, audit vide, analyses vides — sans qu'aucun écran ne lui dise pourquoi ni
par où revenir. Les données sont pourtant intactes : c'est la session qui a
disparu.

CE QUI EST AJOUTÉ. Une rubrique « Compte », un onglet « Connexion & session »,
et un panneau qui lit l'état COURANT de la session : qui est connecté, sous
quelle offre, et les actions qui vont avec — se déconnecter et changer de compte
quand la session est ouverte, se connecter quand elle ne l'est pas.

LE PIÈGE, ANNONCÉ PUIS COMMIS. Le commentaire du module dit qu'un état de
session mémorisé serait faux au moment précis où on vient le consulter. Deux
lignes plus bas, la première version appelait `sentAuthMoi()` — qui mémorise sa
promesse pour toute la vie de la page. Éprouvé en navigateur : session ouverte,
cookie retiré, panneau rouvert — il annonçait encore « session ouverte ». La
route est désormais interrogée directement, et `sentAuthMoi` n'est pas touché :
ses six autres appelants demandent précisément cette déduplication.
"""
import io
import os
import re

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = io.open(os.path.join(ICI, 'sentinel.html'), encoding='utf-8').read()
MOTEUR = io.open(os.path.join(ICI, 'sentinel.page.js'), encoding='utf-8').read()


def _corps_rendre(sans_commentaires=False):
    d = MOTEUR.index('window.compteRendre = function(){')
    corps = MOTEUR[d:MOTEUR.index('\n  };', d)]
    if not sans_commentaires:
        return corps
    # LE CODE, PAS LES COMMENTAIRES — et cette précaution a été ajoutée après
    # coup. La première version de la règle « le panneau n'emploie pas le
    # raccourci qui mémorise » butait sur le COMMENTAIRE qui nommait ce
    # raccourci pour expliquer pourquoi on ne l'emploie plus. Une règle qu'un
    # commentaire peut mettre en défaut ne mesure pas le code.
    corps = re.sub(r'/\*.*?\*/', '', corps, flags=re.S)
    corps = re.sub(r'^\s*//.*$', '', corps, flags=re.M)
    return corps


# ── L'ONGLET EXISTE, ET IL EST ATTEIGNABLE ───────────────────────────────

def test_l_onglet_de_connexion_existe_dans_le_menu():
    """LA RÈGLE PRINCIPALE, celle dont l'absence a motivé ce fichier."""
    assert 'id="sb-compte"' in PAGE, (
        "l'onglet « Connexion & session » a disparu du menu : la session "
        "redevient invisible, et un visiteur déconnecté n'a plus de chemin de "
        "retour depuis Sentinel")
    m = re.search(r'id="sb-compte"[^>]*onclick="go\(\'([^\']+)\'', PAGE)
    assert m and m.group(1) == 'compte', (
        "l'onglet n'ouvre plus le panneau « compte »")


def test_la_rubrique_compte_est_declaree():
    """Un onglet sans rubrique se range dans celle du dessus, et se lit comme
    un module d'administration."""
    assert re.search(r'class="sb-section" data-grp="compte"', PAGE), (
        "la rubrique « Compte » a disparu de la barre latérale")
    assert re.search(r'class="sb-item" data-grp="compte"', PAGE), (
        "l'onglet n'appartient plus à la rubrique « Compte » : le filtre du "
        "menu, qui cherche aussi le nom de la rubrique, ne le trouvera plus "
        "sur « compte »")


def test_le_panneau_existe():
    assert 'id="p-compte"' in PAGE, "le panneau du compte a disparu"
    for element in ('compte-corps', 'compte-actions', 'compte-etat-pastille'):
        assert 'id="%s"' % element in PAGE, (
            "le panneau n'a plus son élément « %s » : le module écrira dans le "
            "vide, sans erreur" % element)


# ── LE PANNEAU LIT L'ÉTAT COURANT, PAS UN ÉTAT MÉMORISÉ ──────────────────

def test_le_panneau_demande_une_lecture_fraiche():
    """LE PIÈGE ANNONCÉ PUIS COMMIS. `sentAuthMoi()` sans argument rend la
    réponse mémorisée au chargement — fausse dès que la session expire,
    c'est-à-dire au moment précis où l'on vient consulter cette page. Éprouvé
    en navigateur : cookie retiré, panneau rouvert, il annonçait encore
    « session ouverte ».

    ET LA PREMIÈRE CORRECTION A ÉTÉ REFUSÉE PAR UNE AUTRE RECETTE. Elle ouvrait
    un second `fetch` vers `/api/sentinel-auth/me` ;
    `test_la_session_nest_demandee_quen_un_seul_endroit` l'interdit, et elle a
    raison — cette route porte du travail de fond côté serveur, et sept
    appelants pour une réponse identique sont exactement ce qui avait été
    consolidé. D'où l'argument `frais` : une lecture neuve, sans point d'appel
    supplémentaire."""
    corps = _corps_rendre(sans_commentaires=True)
    assert re.search(r'sentAuthMoi\(\s*true\s*\)', corps), (
        "le panneau ne demande plus de lecture fraîche : il affichera "
        "« session ouverte » après l'expiration, au moment précis où on vient "
        "le consulter")
    assert 'fetch(' not in corps, (
        "le panneau ouvre son propre appel réseau : la session doit rester "
        "demandée en un seul endroit")


def test_le_raccourci_partage_memorise_toujours_par_defaut():
    """L'argument `frais` ne devait pas retirer aux six autres appelants la
    déduplication qu'ils demandent : sans argument, la promesse reste
    mémorisée."""
    d = MOTEUR.index('window.sentAuthMoi = function(')
    corps = MOTEUR[d:MOTEUR.index('\n};', d)]
    # LA GARDE, PAS LA MENTION. Une première version cherchait le nom de la
    # variable : remplacer `if(!_sentAuthPromesse)` par `if(true)` la laissait
    # en place — assignée à chaque appel, ne mémorisant plus rien — et la règle
    # passait. Une variable citée ne prouve pas qu'elle garde quelque chose.
    assert re.search(r'if\s*\(\s*!\s*_sentAuthPromesse\s*\)', corps), (
        "`sentAuthMoi` ne mémorise plus : la promesse est relancée à chaque "
        "appel, et les six appels du chargement déclencheront six requêtes là "
        "où une suffisait")
    assert re.search(r'if\s*\(\s*frais\s*\)\s*_sentAuthPromesse = null', corps), (
        "`frais` ne vide plus la mémoire : le panneau du compte redeviendra "
        "aveugle à l'expiration de la session")


def test_le_panneau_est_rendu_a_chaque_ouverture():
    """Rendu une seule fois au chargement de Sentinel, il montrerait l'état
    d'alors — pas celui du moment où on l'ouvre."""
    d = MOTEUR.index('window.compteRendre = function(){')
    apres = MOTEUR[d:]
    assert re.search(r"if\(id === 'compte'\) window\.compteRendre\(\);", apres), (
        "le panneau n'est plus rafraîchi à son ouverture")


def test_l_enrobage_de_go_rend_bien_la_valeur_d_origine():
    """`go` est enrobé pour rafraîchir le panneau. Un enrobage qui avale la
    valeur de retour casserait silencieusement les appelants qui s'en servent
    — et il y en a déjà un dans ce fichier, pour la matrice RACI."""
    d = MOTEUR.index("if(id === 'compte') window.compteRendre();")
    corps = MOTEUR[max(0, d - 400):d + 200]
    assert 'var r = _origGo' in corps and 'return r;' in corps, (
        "l'enrobage de `go` ne restitue plus la valeur de la fonction "
        "d'origine")


# ── LES DEUX ÉTATS SONT TRAITÉS ──────────────────────────────────────────

def test_l_etat_connecte_offre_de_se_deconnecter_et_de_changer_de_compte():
    corps = _corps_rendre()
    assert 'sentinelLogout()' in corps, (
        "le panneau n'offre plus de se déconnecter")
    assert "/login" in corps, (
        "le panneau n'offre plus d'atteindre la page de connexion")


def test_l_etat_deconnecte_explique_et_donne_le_chemin():
    """C'est le cas utile : la session expire pendant le travail, les modules
    se vident, et rien ne dit pourquoi. Le panneau doit dire les deux choses —
    ce qui se passe, et que les données ne sont pas perdues."""
    corps = _corps_rendre()
    assert 'Non connecté' in corps, (
        "le panneau ne nomme plus l'état déconnecté")
    assert 'Se connecter' in corps, (
        "le panneau ne propose plus de se connecter")
    assert 'rattachés à un compte' in corps or 'rattaches a un compte' in corps, (
        "le panneau ne dit plus que les données appartiennent au compte et "
        "ne sont pas perdues : le visiteur croira les avoir perdues")


def test_la_deconnexion_reste_aussi_dans_la_barre_du_haut():
    """L'onglet s'ajoute, il ne remplace pas. Retirer le bouton de la barre
    obligerait à connaître le nouvel onglet pour se déconnecter."""
    assert 'onclick="sentinelLogout()"' in PAGE, (
        "le bouton de déconnexion a disparu de la barre d'outils")
