"""Les deux pieds de page, et pourquoi ils doivent rester jumeaux.

LE DÉFAUT QUI A COÛTÉ UN ALLER-RETOUR. Vingt-trois pages chargent
`footer-shared.html` par un emplacement et un chargeur. L'ACCUEIL NON : il porte
sa propre copie du pied de page, écrite en dur dans `index.html`. Une colonne
ajoutée au partagé arrive donc partout SAUF sur la page la plus vue — et rien ne
le signale : les deux fichiers sont valides, la suite était verte, le
déploiement en ligne. Seul un œil sur la page l'a vu.

CE QUE CES RÈGLES MESURENT. Que les deux copies portent LES MÊMES colonnes et
LES MÊMES liens. Elles ne demandent pas des fichiers identiques — l'accueil a
ses propres classes et son propre habillage — mais que rien n'existe d'un côté
sans exister de l'autre.

POURQUOI DEUX COPIES SUBSISTENT. Les supprimer voudrait dire faire charger à
l'accueil un pied de page qu'il rend aujourd'hui d'emblée : sur la page la plus
vue, cela retarderait l'affichage et le lierait à la réussite d'un appel. Tant
que la duplication est TENUE, elle est un arbitrage ; c'est de n'être pas tenue
qu'elle devient un défaut.
"""
import io
import os
import re

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _lire(nom):
    return io.open(os.path.join(ICI, nom), encoding="utf-8").read()


ACCUEIL = _lire("index.html")
PARTAGE = _lire("footer-shared.html")


def _grille(src):
    """La GRILLE du pied de page — les colonnes, sans la lettre d'information
    ni la barre du bas, qui ne sont pas en cause ici."""
    d = src.index('<div class="ft-top-grid">')
    for borne in ("<!-- ── NEWSLETTER ── -->", '<div class="ft-newsletter">'):
        if borne in src[d:]:
            return src[d:d + src[d:].index(borne)]
    raise AssertionError("la grille du pied de page n'a plus de borne connue")


def _titres(src):
    return re.findall(r'data-i18n="(ft\.[\w.]+\.lbl)"[^>]*>([^<]+)<', _grille(src))


def _liens(src):
    return re.findall(r'<a href="([^"]+)"[^>]*data-i18n="(ft\.[\w.]+)"', _grille(src))


def test_les_deux_pieds_de_page_existent_et_ne_sont_pas_vides():
    """LE TÉMOIN. Si l'un des deux extracteurs cessait de trouver sa grille,
    toutes les comparaisons ci-dessous passeraient sur des listes vides."""
    assert len(_titres(ACCUEIL)) >= 6, _titres(ACCUEIL)
    assert len(_titres(PARTAGE)) >= 6, _titres(PARTAGE)
    assert len(_liens(ACCUEIL)) >= 15
    assert len(_liens(PARTAGE)) >= 15


def test_LES_MEMES_COLONNES_des_deux_cotes_et_dans_le_meme_ordre():
    """C'EST LE CONTRÔLE QUI MANQUAIT. La colonne « Investisseurs » a été
    ajoutée au partagé et pas à l'accueil ; les deux fichiers restaient
    valides, la suite verte, le site déployé — et la rubrique n'apparaissait
    pas là où on la cherchait."""
    a, p = _titres(ACCUEIL), _titres(PARTAGE)
    manque_accueil = [t for t in p if t not in a]
    manque_partage = [t for t in a if t not in p]
    assert not manque_accueil, (
        "colonnes absentes de l'accueil : %r" % ([t[1] for t in manque_accueil],))
    assert not manque_partage, (
        "colonnes absentes du pied de page partagé : %r"
        % ([t[1] for t in manque_partage],))
    assert [c for _, c in a] == [c for _, c in p], (
        "ordre des colonnes différent — accueil %r, partagé %r"
        % ([c for _, c in a], [c for _, c in p]))


#: LES DIFFÉRENCES VOULUES, ÉCRITES ICI PLUTÔT QUE TOLÉRÉES EN SILENCE.
#: Une règle qui interdisait TOUTE différence tombait sur des écarts justes, et
#: une règle qui n'en mesure aucune ne sert à rien. Celles-ci sont déclarées, et
#: tout ce qui n'y figure pas fait tomber la règle.
ECARTS_VOULUS = {
    "ft.plans.l1": "L'accueil mène à l'inscription en portant la formule "
                   "(/login?plan=gratuit) ; les autres pages mènent à la "
                   "plateforme. Le parcours d'entrée n'est pas le même selon "
                   "qu'on découvre le site ou qu'on le parcourt déjà.",
    "ft.plans.l3": "Même motif pour la formule Entreprise : l'accueil porte la "
                   "formule jusqu'à l'inscription (/login?plan=entreprise), les "
                   "autres pages renvoient à la plateforme.",
}


def _normaliser(h):
    """Une ancre de MÊME PAGE et son équivalent depuis une autre page.

    Sur l'accueil, « #services » suffit et ne recharge rien ; depuis une autre
    page il faut « /#services ». Les deux désignent la même destination, et
    exiger la même écriture ferait tomber la règle sur du balisage correct."""
    return "/" + h if h.startswith("#") else h


def test_LES_MEMES_LIENS_des_deux_cotes_avec_la_meme_destination():
    """UNE COLONNE PRÉSENTE DES DEUX CÔTÉS MAIS DONT UN LIEN DIFFÈRE est pire
    qu'une colonne absente : elle a l'air juste. C'est le cas des trois ancres
    de la rubrique investisseurs, qui ouvrent chacune un onglet distinct."""
    a = {k: _normaliser(h) for h, k in _liens(ACCUEIL)}
    p = {k: _normaliser(h) for h, k in _liens(PARTAGE)}
    assert set(a) == set(p), (
        "clés de lien divergentes — accueil seulement %r, partagé seulement %r"
        % (sorted(set(a) - set(p)), sorted(set(p) - set(a))))
    ecarts = {k: (a[k], p[k]) for k in a
              if a[k] != p[k] and k not in ECARTS_VOULUS}
    assert not ecarts, (
        "destinations divergentes et NON DÉCLARÉES (accueil, partagé) : %r "
        "— si l'écart est voulu, il s'écrit dans ECARTS_VOULUS avec son motif"
        % ecarts)


def test_les_ecarts_declares_EXISTENT_encore_et_portent_leur_motif():
    """UNE DÉROGATION QUI SURVIT À CE QU'ELLE COUVRAIT devient un trou. Si les
    deux pieds de page se rejoignaient sur `ft.plans.l1`, la dérogation
    resterait ouverte pour un futur écart que personne n'aurait décidé."""
    a = {k: _normaliser(h) for h, k in _liens(ACCUEIL)}
    p = {k: _normaliser(h) for h, k in _liens(PARTAGE)}
    for cle, motif in ECARTS_VOULUS.items():
        assert len(motif) > 60, cle
        assert cle in a and cle in p, "%s n'existe plus des deux côtés" % cle
        assert a[cle] != p[cle], (
            "%s ne diverge plus : la dérogation doit sortir de ECARTS_VOULUS" % cle)


def test_la_rubrique_investisseurs_est_dans_LES_DEUX():
    """La règle précédente le couvre déjà. Celle-ci nomme le cas qui a servi
    de révélateur : une règle générale que rien n'ancre se relâche."""
    for nom, src in (("accueil", ACCUEIL), ("partagé", PARTAGE)):
        cles = {k for _, k in _liens(src)}
        assert 'ft.inv.lbl' in {k for k, _ in _titres(src)}, nom
        for a in ("relations", "financier", "gouvernance"):
            assert ('/investisseurs#%s' % a) in [h for h, _ in _liens(src)], (nom, a)
        assert {"ft.inv.l1", "ft.inv.l2", "ft.inv.l3"} <= cles, nom


def test_l_accueil_est_le_SEUL_a_porter_sa_propre_copie():
    """SI UNE TROISIÈME COPIE APPARAISSAIT, ces règles n'en sauraient rien :
    elles ne comparent que deux fichiers. La règle relève donc toutes les
    pages qui portent une grille en dur, et refuse la troisième."""
    en_dur = sorted(n for n in os.listdir(ICI)
                    if n.endswith(".html") and '<div class="ft-top-grid">' in _lire(n))
    assert en_dur == ["footer-shared.html", "index.html"], (
        "des pages portent une grille de pied de page en dur sans être "
        "comparées : %r" % en_dur)


#: LES PAGES QUI N'ONT PAS DE PIED DE PAGE, ET POURQUOI.
#: Ce ne sont pas des oublis : ce sont des écrans d'application et d'accès. Un
#: pied de page marchand — services, abonnements, lettre d'information — n'a
#: rien à y faire, et sur les écrans d'authentification il ouvrirait des sorties
#: au milieu d'un geste en cours. Les nommer ici est ce qui distingue une
#: décision d'un oubli.
SANS_PIED_DE_PAGE = {
    "sentinel.html":      "la plateforme elle-même : une application, pas une page",
    "panorama.html":      "étude plein écran, servie dans le cadre de la plateforme",
    "observatoire.html":  "étude plein écran, servie dans le cadre de la plateforme",
    "map.html":           "carte plein écran",
    "map_test.html":      "banc d'essai de la carte, non servi au public",
    "login.html":         "écran d'accès : aucune sortie au milieu d'une connexion",
    "invitation.html":    "écran d'accès : une invitation se poursuit ou se ferme",
    "invitation-expiree.html": "écran d'accès, invitation périmée",
    "reset-password.html": "écran d'accès : réinitialisation en cours",
}


def test_les_autres_pages_chargent_bien_LE_PARTAGE():
    """Le versant positif : une page qui n'a ni copie ni emplacement n'a pas
    de pied de page du tout, et personne ne s'en aperçoit avant un visiteur.

    LES ÉCRANS D'APPLICATION SONT EXCLUS, ET NOMMÉS. Une règle qui exigeait un
    pied de page partout tombait sur la plateforme et sur les écrans de
    connexion, où il n'a rien à faire."""
    sans = []
    for n in sorted(os.listdir(ICI)):
        if not n.endswith(".html") or n in ("footer-shared.html", "index.html"):
            continue
        if n in SANS_PIED_DE_PAGE:
            continue
        src = _lire(n)
        # LE BALISAGE, PAS LE MOT. Une première version cherchait « ft-mini »
        # n'importe où : la classe figure aussi dans la FEUILLE DE STYLE de
        # chaque page, si bien qu'une page ayant perdu son pied de page
        # continuait de passer. La règle lit donc l'attribut, pas le jeton.
        if ('id="shared-footer-placeholder"' not in src
                and 'class="ft-mini"' not in src):
            sans.append(n)
    assert not sans, "pages sans aucun pied de page : %r" % sans


def test_la_liste_des_pages_sans_pied_de_page_ne_couvre_QUE_des_pages_reelles():
    """UNE DISPENSE POUR UN FICHIER DISPARU couvre en silence la page qui
    reprendrait son nom. Et une dispense pour une page qui a FINALEMENT un pied
    de page laisse croire à une décision qui n'a plus d'objet."""
    for nom, motif in SANS_PIED_DE_PAGE.items():
        assert os.path.exists(os.path.join(ICI, nom)), "dispense orpheline : %s" % nom
        assert len(motif) > 15, nom
        src = _lire(nom)
        assert 'id="shared-footer-placeholder"' not in src, (
            "%s charge le pied de page partagé : la dispense n'a plus d'objet" % nom)


# ═══════════════════════════════════════════════════════════════════════════
#  L'ÉCHAPPEMENT QUI SE VOIT À L'ÉCRAN
# ═══════════════════════════════════════════════════════════════════════════

MOTEUR = _lire("index.page.js")


def _tables():
    """Les trois tables de traduction, telles que le fichier les porte."""
    out = {}
    for lang in ("fr", "en", "de"):
        tete = "\n  %s:JSON.parse(`" % lang
        d = MOTEUR.index(tete) + len(tete)
        out[lang] = MOTEUR[d:MOTEUR.index("`)", d)]
    assert all(len(v) > 5000 for v in out.values()), \
        "une table de traduction est introuvable ou vide"
    return out


def test_aucune_apostrophe_ne_s_affiche_precedee_d_une_barre_oblique():
    """LE DÉFAUT SE VOYAIT SUR LA PAGE D'ACCUEIL : « Centre d\\'aide »,
    « Profiter de l\\'offre », « Secteurs d\\'Intervention ».

    LE CHEMIN, ET POURQUOI SIX BARRES DONNENT UNE BARRE VISIBLE. La table est
    écrite dans un gabarit `…` qui consomme un niveau d'échappement, puis
    passée à JSON.parse qui en consomme un second. Six barres deviennent trois,
    puis JSON rend « une barre + une apostrophe ». Deux barres suffisent : le
    gabarit en laisse une, JSON lit `\\u0027` et rend l'apostrophe seule.
    """
    fautes = {lang: t.count("\\" * 6 + "u0027") for lang, t in _tables().items()}
    assert not any(fautes.values()), (
        "des apostrophes sur-échappées s'afficheront avec leur barre : %r" % fautes)


def test_les_tables_de_traduction_se_lisent_encore():
    """LE TÉMOIN DE LA RÈGLE PRÉCÉDENTE. Corriger un échappement en cassant la
    table rendrait toute la page muette — chaque libellé retomberait sur le
    texte du balisage, ce qui ne lève rien et ne se voit qu'en changeant de
    langue."""
    import json
    for lang, t in _tables().items():
        # Le gabarit ` consomme un niveau : on le reproduit avant JSON.parse.
        apres_gabarit = t.replace("\\\\", "\\")
        obj = json.loads(apres_gabarit)
        assert len(obj) > 100, (lang, len(obj))
        assert obj.get("ft.inv.lbl"), "la table %s a perdu la rubrique" % lang
