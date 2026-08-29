"""LE NAVIGATEUR A REMPLI LE FILTRE DU MENU AVEC UNE ADRESSE E-MAIL, ET TOUTE LA
NAVIGATION A DISPARU.

CE QUI A ÉTÉ VU, LE 29 AOÛT 2026, SUR UNE CAPTURE D'ÉCRAN. La barre latérale de
Sentinel porte un champ « Filtrer le menu ». Le navigateur l'avait rempli tout
seul avec « christophe.cerf@outlook.com ». Aucun onglet ne contient d'arobase :
les cinquante-deux ont été masqués, et la barre annonçait « aucun onglet ne
correspond ». Plus rien à cliquer — ni les modules, ni les parcours, ni le moyen
de s'en sortir. La barre latérale étant unique et partagée, le défaut valait
pour TOUTES les pages à la fois.

`autocomplete="off"` ÉTAIT DÉJÀ LÀ. Chrome l'ignore pour tout champ que ses
heuristiques prennent pour une saisie d'identité — un `<input>` étroit en tête
de colonne, sans `name`, y ressemble. On lui donne donc ce qu'il regarde
vraiment : un `name` qui ne désigne rien d'identifiant, et les marqueurs que les
gestionnaires de mots de passe respectent, eux.

MAIS AUCUNE DE CES PARADES N'EST FIABLE, et c'est pourquoi la vraie correction
est ailleurs. Un filtre est une AIDE À TROUVER : quand il ne trouve rien, il
n'a rien à retirer. Il le dit, et rend la liste entière. Cette règle tient quel
que soit ce qui a rempli le champ — le visiteur, son gestionnaire de mots de
passe, ou un collage malheureux. Se défendre du remplissage automatique reste
utile ; ne pas dépendre de sa défaite est la correction.

VÉRIFIÉ EN NAVIGATEUR, en reproduisant le défaut exact : le champ rempli avec
l'adresse e-mail laisse les 52 onglets visibles, le message explique, et un
bouton « Effacer le filtre » ramène à l'état neutre.
"""
import io
import os
import re

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = io.open(os.path.join(ICI, 'sentinel.html'), encoding='utf-8').read()
MOTEUR = io.open(os.path.join(ICI, 'sentinel.page.js'), encoding='utf-8').read()


def _champ():
    m = re.search(r'<input[^>]*id="sb-filtre"[^>]*>', PAGE, re.S)
    assert m, "le champ de filtrage du menu a disparu de la barre latérale"
    return m.group(0)


def _corps_filtrer():
    d = MOTEUR.index('window.sbFiltrer = function(q){')
    return MOTEUR[d:MOTEUR.index('\n};', d)]


# ── LA CORRECTION QUI COMPTE : LE MENU NE SE VIDE JAMAIS ─────────────────

def test_un_filtre_sans_resultat_rend_le_menu_entier():
    """LA RÈGLE PRINCIPALE. Sans elle, n'importe quelle saisie sans
    correspondance — dont un remplissage automatique — supprime la navigation
    de toutes les pages à la fois."""
    corps = _corps_filtrer()
    d = corps.find('if(m && vus === 0)')
    assert d >= 0, (
        "le filtre ne rétablit plus le menu quand rien ne correspond : une "
        "saisie sans résultat videra de nouveau toute la barre latérale")
    bloc = corps[d:d + 700]
    assert bloc.count("removeAttribute('hidden')") >= 2, (
        "le rétablissement ne rend pas à la fois les rubriques et leurs "
        "onglets : la moitié du menu resterait masquée")


def test_le_message_dit_que_le_menu_est_de_nouveau_complet():
    """« aucun onglet ne correspond » était exact et sans recours. Le lecteur
    doit savoir que ce qu'il voit est la liste entière, pas un reliquat."""
    corps = _corps_filtrer()
    assert 'menu complet affiché' in corps, (
        "le message ne dit plus que le menu entier est affiché : le visiteur "
        "croira la liste tronquée")


def test_une_porte_de_sortie_est_offerte_tant_qu_un_filtre_est_actif():
    """La croix native de `type=\"search\"` n'existe pas partout, et un champ
    rempli automatiquement ne se remarque pas toujours."""
    assert 'id="sb-filtre-effacer"' in PAGE, (
        "le bouton d'effacement du filtre a disparu")
    corps = _corps_filtrer()
    assert 'sb-filtre-effacer' in corps, (
        "le bouton n'est plus piloté par le filtre : il restera affiché ou "
        "caché en permanence")
    assert re.search(r'eff\.hidden\s*=\s*!m', corps), (
        "le bouton ne suit plus l'état du filtre")


def test_le_bouton_vide_le_champ_et_rejoue_le_filtre():
    """Vider le champ sans rejouer le filtre laisserait le menu dans l'état
    filtré, avec un champ vide : incompréhensible."""
    m = re.search(r'id="sb-filtre-effacer"[^>]*onclick="([^"]+)"', PAGE, re.S)
    assert m, "le bouton d'effacement n'a plus de gestionnaire"
    action = m.group(1)
    assert "value=''" in action.replace('"', "'"), "le bouton ne vide pas le champ"
    assert 'sbFiltrer(' in action, "le bouton ne rejoue pas le filtre"


# ── LE PIS-ALLER : DIRE AU NAVIGATEUR QUE CE N'EST PAS UN CHAMP D'IDENTITÉ ──

@pytest.mark.parametrize('marqueur,pourquoi', [
    ('autocomplete="off"', "la demande standard, que Chrome ignore souvent"),
    ('name="sb-filtre-menu"', "un champ sans `name` ressemble à une saisie de compte"),
    ('data-lpignore="true"', "LastPass"),
    ('data-1p-ignore', "1Password"),
    ('data-form-type="other"', "les gestionnaires qui lisent cet attribut"),
])
def test_le_champ_est_marque_comme_non_identifiant(marqueur, pourquoi):
    champ = _champ()
    assert marqueur in champ, (
        "le champ de filtrage ne porte plus %s (%s) : il redeviendra une cible "
        "de remplissage automatique" % (marqueur, pourquoi))


def test_le_champ_reste_un_champ_de_recherche():
    assert 'type="search"' in _champ(), (
        "le champ n'est plus déclaré comme recherche : il perd sa croix native "
        "et son rôle d'assistance")


def test_le_filtre_ignore_toujours_accents_et_casse():
    """La correction ne doit pas avoir emporté ce que le filtre faisait bien.
    « evaluer » doit trouver « Évaluer »."""
    corps = _corps_filtrer()
    assert 'normalize' in corps and 'toLowerCase' in corps, (
        "le filtre ne replie plus les accents ni la casse : il ne servirait "
        "plus qu'à ceux qui savent écrire l'intitulé exact")


# ── CE QUI RESTE ATTEIGNABLE ─────────────────────────────────────────────

def test_la_deconnexion_reste_atteignable():
    """Le visiteur dont le menu s'était vidé ne trouvait plus rien — pas même
    de quoi se déconnecter. Le bouton est dans la barre du haut, hors du menu :
    il faut qu'il y reste."""
    assert re.search(r'onclick="sentinelLogout\(\)"', PAGE), (
        "le bouton de déconnexion a disparu de la barre d'outils")


# ── L'ENCODAGE DES TITRES ────────────────────────────────────────────────

CORRUPTION = re.compile(r'\?{1,3}️|�')


@pytest.mark.parametrize('fichier', ['sentinel.html', 'index.html', 'panorama.html',
                                     'actualites.html', 'sentinel.page.js'])
def test_aucun_caractere_perdu_a_l_encodage(fichier):
    """TROUVÉ EN LISANT CE QUE LA PAGE AFFICHE, pas en relisant le code. Trois
    titres de la section Veille portaient « ??️ » : un emoji hors BMP perdu à
    l'encodage — deux points d'interrogation là où étaient les deux unités du
    couple de substitution, et le sélecteur de variante resté seul derrière.
    Le visiteur lisait « ??️ Veille réglementaire IA ».

    L'icône d'origine n'était plus récupérable : les trois occurrences étaient
    corrompues, et aucune sœur intacte ne la révélait. On a retiré ce qui était
    cassé plutôt que d'inventer un choix qui n'était pas le nôtre."""
    chemin = os.path.join(ICI, fichier)
    if not os.path.exists(chemin):
        pytest.skip('%s absent' % fichier)
    contenu = io.open(chemin, encoding='utf-8', errors='replace').read()
    trouves = [re.sub(r'\s+', ' ', contenu[max(0, m.start() - 50):m.end() + 50])
               for m in CORRUPTION.finditer(contenu)]
    assert not trouves, (
        "caractère(s) perdu(s) à l'encodage dans %s — le visiteur lit des "
        "points d'interrogation :\n  - %s" % (fichier, '\n  - '.join(trouves[:5])))
