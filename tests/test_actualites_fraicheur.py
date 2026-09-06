# -*- coding: utf-8 -*-
"""La page d'actualités dit sa fraîcheur — en la lisant, jamais en la recopiant.

POURQUOI CE BANDEAU. Rien sur `conseilprevia` ne rafraîchit les actualités : les
communiqués sont écrits dans `actualites.html` et changent quand la page est
déployée. Mesuré dans l'historique : huit modifications sur cinq jours entre le
4 août et le 2 septembre 2026 — quelques salves par mois, sans régularité.

Une page qui ne peut pas promettre un rythme peut au moins dire OÙ ELLE EN EST.
Le lecteur juge alors la fraîcheur lui-même, au lieu de la supposer.

CE QUE CES RÈGLES TIENNENT. La date affichée en haut ne doit pas devenir une
SECONDE vérité : chaque communiqué porte déjà la sienne, et c'est celle qu'on
oublierait de corriger qui resterait affichée. Le bandeau se calcule donc à
partir des articles eux-mêmes, à chaque affichage.

Et il ne doit rien afficher quand il n'a rien à dire : « Dernier communiqué : — »
serait une promesse vide, c'est-à-dire pire que son absence.

DEUX DÉFAUTS TROUVÉS EN CONFRONTANT LE CODE AUX VRAIES DONNÉES, pas en relisant
le motif : la page contient « le 1er septembre 2026 », que la première version
de la lecture ne savait pas lire — elle aurait affiché la deuxième plus récente
sans que rien ne le signale ; et le texte affiché était RECOMPOSÉ à partir des
groupes capturés, ce qui perdait le « er ». Les deux ont leur règle.
"""
import io
import os
import re
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import partage                                                     # noqa: E402

PAGE = io.open(os.path.join(ICI, "actualites.html"), encoding="utf-8").read()

BANDEAU = PAGE[PAGE.rindex("/* LA FRAÎCHEUR SE LIT DANS LA PAGE"):]
BANDEAU = BANDEAU[:BANDEAU.index("</script>")]


# ══════════════════════════════════════════════════════════════════════════
# 1. UNE SEULE VÉRITÉ : LA PAGE SE LIT ELLE-MÊME
# ══════════════════════════════════════════════════════════════════════════

def test_aucune_date_n_est_recopiee_dans_le_bandeau():
    """L'élément livré est VIDE. Y écrire une date en dur créerait une seconde
    vérité — et c'est celle qu'on oublie de corriger qui resterait affichée
    devant un communiqué plus récent."""
    m = re.search(r'<p class="na-fraicheur" id="na-fraicheur"([^>]*)>(.*?)</p>', PAGE)
    assert m, "le bandeau n'est pas dans la page"
    assert m.group(2).strip() == "", (
        "le bandeau porte un texte en dur : %r" % m.group(2))
    assert "hidden" in m.group(1), (
        "le bandeau n'est pas caché au départ : il s'afficherait vide le temps "
        "que le script tourne, ou pour toujours s'il ne tourne pas")


def test_le_bandeau_lit_les_dates_des_articles_de_la_page():
    """Le témoin de la règle précédente : ne rien recopier ne vaut que si l'on
    lit vraiment quelque chose."""
    assert '.na-article [id$=\'-date\']' in BANDEAU, BANDEAU


# ══════════════════════════════════════════════════════════════════════════
# 2. LA PLUS RÉCENTE, ET NON LA PREMIÈRE
# ══════════════════════════════════════════════════════════════════════════

def test_la_plus_recente_est_choisie_par_comparaison_et_non_par_position():
    """L'ordre du document n'est pas garanti chronologique : « le plus haut »
    n'est pas « le plus récent ». Prendre le premier afficherait une date
    plausible et fausse — le pire des deux, parce qu'elle ne se remarque pas."""
    assert "lu.date > recent.date" in BANDEAU, BANDEAU
    assert "dates[0]" not in BANDEAU, (
        "le bandeau prend le premier article du document\n%s" % BANDEAU)


def test_aucune_couche_ne_garantit_l_ordre_chronologique():
    """POURQUOI LA COMPARAISON N'EST PAS DU LUXE — ET LA RÈGLE QUE J'AI DÛ
    CORRIGER. Je l'avais d'abord écrite pour affirmer que la page N'EST PAS
    rangée chronologiquement. Elle est tombée, et elle avait raison : la page
    l'est, du plus récent au plus ancien.

    Ce qui rend la comparaison INDISPENSABLE, c'est justement cela. Prendre
    `dates[0]` donnerait aujourd'hui le bon résultat — donc aucun essai, aucune
    règle, aucun coup d'œil ne signalerait quoi que ce soit. Le jour où un
    communiqué serait inséré ailleurs qu'en tête, le bandeau afficherait une
    date plausible et fausse, c'est-à-dire celle qui ne se remarque pas.

    Ce que cette règle mesure, c'est qu'AUCUNE COUCHE n'impose cet ordre :
    `partage.communiques()` rend les communiqués « dans leur ordre
    d'affichage » et ne trie rien ; le bandeau ne trie pas davantage. L'ordre
    est une habitude de rédaction, pas une garantie — et on ne bâtit pas sur
    une habitude.
    """
    import inspect
    # ON CHERCHE UN APPEL DE TRI, PAS LA SOUS-CHAÎNE « sort ». La première
    # rédaction de cette règle est tombée sur `sortie`, la variable française de
    # `partage.communiques()` — une règle rouge pour une raison sans rapport
    # avec ce qu'elle prétend, dans la règle même qui traque ce défaut.
    tri = re.compile(r"\bsorted\s*\(|\.sort\s*\(")
    lecture = inspect.getsource(partage.communiques)
    assert not tri.search(lecture), (
        "partage.communiques() trie désormais : l'ordre devient une garantie, "
        "et cette règle doit être revue\n%s" % lecture)
    assert not tri.search(BANDEAU), (
        "le bandeau trie au lieu de comparer : un tri sur des dates textuelles "
        "rangerait « 13 juillet » avant « 2 septembre »")


# ══════════════════════════════════════════════════════════════════════════
# 3. CE QUE LA PAGE ÉCRIT VRAIMENT
# ══════════════════════════════════════════════════════════════════════════

def test_l_ordinal_du_premier_du_mois_est_lu():
    """« 1er septembre » — et la page en contient un. Sans le `er` optionnel,
    cette date-là ne se lisait pas : le bandeau affichait la deuxième plus
    récente, et rien ne signalait l'écart."""
    assert any(re.search(r"\d+er\s", c["date"] or "")
               for c in partage.communiques()), (
        "aucun ordinal dans la page : le témoin de cette règle a disparu")
    assert r"(\d{1,2})(?:er)?\s+" in BANDEAU, (
        "la lecture n'accepte plus l'ordinal français\n%s" % BANDEAU)


def test_le_texte_affiche_est_celui_qui_a_ete_trouve():
    """Recomposer la date à partir des groupes capturés perdrait le « er », et
    le bandeau écrirait une date que la page n'écrit nulle part."""
    assert "texte: m[0]" in BANDEAU, BANDEAU
    assert 'm[1] + " " + m[2]' not in BANDEAU, (
        "la date est recomposée au lieu d'être reprise\n%s" % BANDEAU)


# ══════════════════════════════════════════════════════════════════════════
# 4. RIEN À DIRE, RIEN D'AFFICHÉ
# ══════════════════════════════════════════════════════════════════════════

def test_sans_date_lisible_le_bandeau_reste_cache():
    """« Dernier communiqué : — » serait une promesse vide. Le retour anticipé
    doit précéder toute écriture dans l'élément."""
    i = BANDEAU.index("if(!recent) return;")
    j = BANDEAU.index("cible.textContent")
    assert i < j, ("le bandeau est rempli avant qu'on sache s'il y a une date\n%s"
                   % BANDEAU)
    assert BANDEAU.index("cible.hidden = false") > j, (
        "le bandeau est dévoilé avant d'être rempli")


def test_le_compte_annonce_est_celui_des_communiques_reellement_presents():
    """Le nombre vient de ce que le script a TROUVÉ, jamais d'un chiffre écrit.
    La règle le confronte au compte qu'obtient `partage.communiques()`, une
    lecture entièrement indépendante de la même page : deux lecteurs qui
    divergeraient signaleraient qu'un communiqué échappe à l'un des deux."""
    # LE COMPTE AFFICHÉ, pas « dates.length quelque part » : l'expression
    # apparaît AUSSI dans le test du pluriel, si bien qu'une première rédaction
    # de cette règle restait verte devant un chiffre écrit en dur à la place du
    # compte. Une mutation l'a montré.
    assert '+ " · " + dates.length + " communiqué"' in BANDEAU, BANDEAU
    combien = len(partage.communiques())
    assert combien >= 1, "partage.communiques() ne lit plus rien"
    assert len(re.findall(r'id="na\d*-date"', PAGE)) == combien, (
        "le script compterait %d dates là où partage.py lit %d communiqués"
        % (len(re.findall(r'id="na\d*-date"', PAGE)), combien))
