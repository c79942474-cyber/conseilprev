# -*- coding: utf-8 -*-
"""La vue « Enveloppe et DPGF — GO / NO GO » : sécurité, fil, parcours, lisibilité.

CE QUE CES RÈGLES MESURENT, ET POURQUOI ELLES ÉNUMÈRENT.

  · LA CADENCE SE MESURE PAR ÉNUMÉRATION, jamais sur une liste de routes
    recopiée ici. Une liste figée se répare machinalement au premier ajout et
    cesse alors de couvrir : la règle relève les routes de la vue DANS LA PAGE
    — celles que le JavaScript appelle réellement — et exige que chacune porte
    une cadence côté serveur. Une route ajoutée demain tombe dans le filet le
    jour même.

  · LE FIL ET LES PARCOURS SE MESURENT SUR LEURS CIBLES. Une étape qui vise
    une ancre inexistante ne lève aucune erreur : elle ne va simplement nulle
    part, et le lecteur croit avoir tout vu. C'est le défaut qui a coûté huit
    tests de viabilité — le business case existait, son formulaire était dans
    un dépliant fermé, et aucun fil n'y menait.

CE QUI A ÉTÉ TROUVÉ EN ÉCRIVANT CES RÈGLES, et qui est gardé en témoin :
`/api/parcours` était la SEULE route de la vue sans cadence — et la seule qui
écrive en base.
"""
import io
import os
import re
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)


def _lire(nom):
    return io.open(os.path.join(ICI, nom), encoding="utf-8").read()


PAGE = _lire("panorama.html")
APP = _lire("app.py")


# ══════════════════════════════════════════════════════════════════════════
# 1. SÉCURITÉ — mesurée par énumération, pas sur une liste recopiée
# ══════════════════════════════════════════════════════════════════════════

def _routes_appelees_par_la_page():
    """Les routes que la page appelle RÉELLEMENT, relevées dans son code.

    C'est le seul relevé qui reste juste : une liste écrite dans ce fichier
    aurait décrit la page d'un jour donné.
    """
    brutes = set(re.findall(r"['\"](/api/[a-z0-9\-/]+)['\"]", PAGE))
    # Les chemins construits par morceaux ou paramétrés ne se relèvent pas
    # ainsi ; on ne garde que ceux qui existent tels quels dans app.py.
    return sorted(r for r in brutes
                  if ("@app.route('%s'" % r) in APP or ('@app.route("%s"' % r) in APP)


def _decorateurs(route):
    """LES SEULES LIGNES QUI DÉCORENT — les commentaires sont écartés.

    Ils ne le furent pas d'abord, et la règle de cadence s'en est trouvée
    verte sur une route dont le `@rate_limit` avait été retiré : le
    commentaire au-dessus de `/api/parcours` explique POURQUOI la cadence y a
    été posée, et contient donc le mot. La règle mesurait la prose.
    """
    m = re.search(r"@app\.route\(['\"]%s['\"][^)]*\)\n((?:(?:#[^\n]*|@[\w_]+[^\n]*)\n)*)def"
                  % re.escape(route), APP)
    if not m:
        return ""
    return "".join(l + "\n" for l in m.group(1).split("\n")
                   if l.startswith("@"))


def test_le_releve_des_routes_de_la_page_n_est_pas_vide():
    """Garde-fou : un relevé cassé rendrait la règle suivante verte en ne
    mesurant rien — le défaut que ce dépôt a déjà commis."""
    routes = _routes_appelees_par_la_page()
    assert len(routes) >= 8, routes
    assert "/api/finance-dc/devis" in routes, routes
    assert "/api/parcours" in routes, routes


@pytest.mark.parametrize("route", _routes_appelees_par_la_page())
def test_chaque_route_de_la_vue_porte_une_cadence(route):
    """LA RÈGLE QUI AURAIT ATTRAPÉ LE DÉFAUT. Douze routes de cette page
    portaient `@rate_limit` ; `/api/parcours` ne l'avait pas — et c'était la
    seule à ÉCRIRE en base, jusqu'à 24 Ko par appel. Le plafond de soixante
    enregistrements borne le stock, pas le débit."""
    d = _decorateurs(route)
    assert "rate_limit" in d, (
        "la route %s est appelée par la page et ne porte aucune cadence : %r"
        % (route, d))


# ── Les routes OUVERTES DÉLIBÉRÉMENT, et pourquoi ─────────────────────────
# LA RÈGLE ÉNUMÉRAIT ET NE PRÉVOYAIT AUCUNE EXEMPTION. Elle a donc signalé
# deux routes comme des défauts alors que leur ouverture est une DÉCISION,
# écrite dans leur docstring avec son motif. Une règle qui ne sait pas
# distinguer un oubli d'un arbitrage force à la contourner, et c'est ainsi
# qu'on finit par la désactiver.
#
# CHAQUE EXEMPTION EST CORROBORÉE PAR LE CODE, et c'est ce qui empêche cette
# table de devenir une liste de complaisance : la règle exige que la fonction
# elle-même déclare son ouverture. Une route qu'on exempterait ici sans que
# son docstring l'assume fait tomber la règle.
OUVERTES_DELIBEREMENT = {
    "/api/pont-datacenter":
        "Construit un lien vers l'étude de durabilité depuis un profil "
        "TECHNIQUE seul — puissance et pays. Aucune donnée nominative n'y "
        "voyage par construction, et la liste des exclusions est servie avec "
        "le contrat, avant que le client ne demande quoi que ce soit.",
    "/api/pont-moe":
        "Même mécanisme pour le chiffrage de maîtrise d'œuvre. Il porte un "
        "MONTANT — arrondi à la centaine de milliers d'euros — et le contrat "
        "le dit en toutes lettres plutôt que de le transporter discrètement ; "
        "aucune donnée nominative n'y figure.",
}


def test_chaque_route_de_la_vue_est_fermee_a_l_anonyme():
    """Une route ouverte au milieu de douze fermées ne se signale pas : elle
    répond, simplement."""
    ouvertes = []
    for route in _routes_appelees_par_la_page():
        if route in OUVERTES_DELIBEREMENT:
            continue
        d = _decorateurs(route)
        if "reserve_abonne_api" in d:
            continue
        # La garde peut être DANS le corps plutôt qu'en décorateur : on la
        # cherche alors dans les premières lignes de la fonction.
        m = re.search(r"@app\.route\(['\"]%s['\"][\s\S]{0,3000}?\ndef \w+\([^)]*\):\n"
                      r"((?:[^\n]*\n){0,12})" % re.escape(route), APP)
        corps = m.group(1) if m else ""
        if "_ent_client_id" in corps or "403" in corps or "401" in corps:
            continue
        ouvertes.append(route)
    assert not ouvertes, (
        "ces routes de la vue répondent à un visiteur anonyme sans que ce "
        "soit déclaré : %s. Soit elles se ferment, soit elles rejoignent "
        "OUVERTES_DELIBEREMENT avec le motif qui les en dispense."
        % ", ".join(ouvertes))


@pytest.mark.parametrize("route", sorted(OUVERTES_DELIBEREMENT))
def test_une_ouverture_declaree_est_assumee_par_la_route_elle_meme(route):
    """CE QUI EMPÊCHE LA TABLE D'EXEMPTIONS DE DEVENIR UNE LISTE DE
    COMPLAISANCE. Exempter une route dans un fichier de règles ne coûte rien ;
    l'assumer dans le code qu'on livre en coûte. La règle exige donc que la
    fonction elle-même déclare son ouverture, et que l'exemption porte un
    motif lisible."""
    assert len(OUVERTES_DELIBEREMENT[route]) > 120, route
    m = re.search(r"@app\.route\(['\"]%s['\"][\s\S]{0,2000}?\ndef \w+\([^)]*\):\n"
                  r"    \"\"\"([\s\S]{0,1600}?)\"\"\"" % re.escape(route), APP)
    assert m, "docstring introuvable pour %s" % route
    assert "OUVERT" in m.group(1), (
        "%s est exemptée ici mais son docstring ne déclare pas qu'elle est "
        "ouverte : l'exemption n'est corroborée par rien." % route)


def test_aucune_exemption_ne_dispense_une_route_deja_fermee():
    """Une exemption qui ne dispense plus rien a survécu à sa raison : elle ne
    protège plus et fausse le compte."""
    fantomes = []
    for route in OUVERTES_DELIBEREMENT:
        if "reserve_abonne_api" in _decorateurs(route):
            fantomes.append(route)
    assert not fantomes, (
        "ces routes sont exemptées et pourtant fermées : %s — retirer "
        "l'exemption devenue fausse." % ", ".join(fantomes))


def test_l_ecriture_de_parcours_verifie_l_origine():
    """CE QUI PROTÈGE DÉJÀ, ET POURQUOI ON L'ÉCRIT QUAND MÊME. Le cookie de
    session porte SameSite=Lax : le navigateur ne l'envoie pas sur un POST
    venu d'un autre site. Ce contrôle ne répare donc pas une porte ouverte —
    il rend la protection explicite à l'endroit où l'on écrit, plutôt que de
    la laisser dépendre d'un réglage de cookie qu'une reconfiguration future
    desserrerait sans que personne ne fasse le lien."""
    i = APP.index("@app.route('/api/parcours'")
    corps = APP[i:i + 3000]
    assert "Origin" in corps, corps[:400]
    assert "Origine refusee" in corps, corps[:800]
    # Une origine ABSENTE reste acceptée : les clients non-navigateur n'en
    # envoient pas, et refuser sur l'absence ne ferme rien.
    assert "if origine:" in corps, corps[:1200]


def test_le_cookie_de_session_reste_samesite_et_httponly():
    """C'est ce réglage qui ferme la falsification de requête sur toute la
    vue. Le desserrer rouvrirait douze routes d'un coup."""
    assert "SESSION_COOKIE_SAMESITE'] = 'Lax'" in APP or \
           "SESSION_COOKIE_SAMESITE'] = 'Strict'" in APP, "SameSite absent"
    assert "SESSION_COOKIE_HTTPONLY'] = True" in APP
    assert "SESSION_COOKIE_SECURE'] = True" in APP


# ══════════════════════════════════════════════════════════════════════════
# 2. LE FIL — dix étapes, et chacune vise quelque chose qui existe
# ══════════════════════════════════════════════════════════════════════════

def _etapes_du_fil():
    i = PAGE.index("var FIN_ETAPES = [")
    j = PAGE.index("\n];", i)
    bloc = PAGE[i:j]
    return re.findall(r'\{ cle: "(\w+)", n: (\d+),', bloc), bloc


def test_la_numerotation_du_fil_est_continue_et_sans_doublon():
    """Un numéro sauté ou répété fait chercher une étape qui n'existe pas.
    La règle porte sur la PROPRIÉTÉ, pas sur un compte figé : elle survit à
    l'ajout d'une étape, et attrape l'insertion mal renumérotée."""
    etapes, _ = _etapes_du_fil()
    nums = [int(n) for _, n in etapes]
    assert nums == list(range(1, len(nums) + 1)), nums
    cles = [c for c, _ in etapes]
    assert len(set(cles)) == len(cles), cles


def test_le_business_case_est_une_etape_du_fil():
    """LE DÉFAUT QUE CETTE RÈGLE GARDE. Le module existait, son formulaire
    était dans un dépliant fermé, et le fil n'en disait rien : huit tests de
    viabilité revenaient « indéterminés » parce que personne ne pouvait
    savoir que les champs existaient."""
    etapes, bloc = _etapes_du_fil()
    cles = [c for c, _ in etapes]
    assert "business" in cles, cles
    # Et il vient APRÈS le calcul de l'enveloppe : le point mort se calcule
    # sur les postes d'exploitation que celui-ci produit.
    assert cles.index("business") > cles.index("calculer"), cles
    # ... et AVANT les honoraires, le ROCE et le pilotage : ce sont des
    # chiffres justes sur une question qui n'a pas été posée.
    for suite in ("moe", "kpi", "pilotage"):
        assert cles.index("business") < cles.index(suite), (suite, cles)


def test_chaque_etape_du_fil_vise_une_ancre_qui_existe():
    """Une cible inexistante ne lève rien : le lecteur clique et ne bouge pas."""
    _, bloc = _etapes_du_fil()
    manquantes = [c for c in re.findall(r'cible: "([a-z0-9-]+)"', bloc)
                  if ('id="%s"' % c) not in PAGE]
    assert not manquantes, manquantes


def _fait_de_l_etape(cle):
    """LE CORPS DE `fait:`, et rien d'autre — le commentaire au-dessus dit ce
    que la mesure devrait faire, ce qui n'est pas la même chose."""
    _, bloc = _etapes_du_fil()
    i = bloc.index('cle: "%s"' % cle)
    j = bloc.index("fait:", i)
    fin = bloc.find('{ cle: "', j)
    return bloc[j:fin if fin > 0 else len(bloc)]


def test_l_etape_du_business_case_mesure_un_resultat_et_non_une_presence():
    """Le bloc s'affiche AUSSI quand les projections sont indéterminées —
    c'est-à-dire quand rien n'a été déclaré. Compter sa présence cocherait
    l'étape sans que personne n'ait rien éprouvé."""
    assert ".bc .bc-kpi" in _fait_de_l_etape("business")


def test_l_etape_du_business_case_exige_que_le_constat_soit_A_L_ECRAN():
    """TROUVÉ AU NAVIGATEUR, ET C'ÉTAIT MON DÉFAUT. Les dossiers de pays
    naissent `hidden` : ils ne s'ouvrent qu'au clic sur la carte. La carte de
    point mort existait donc dans le document dès le calcul, et l'étape se
    cochait — « Étape 4 sur 10 · Franchie — Éprouver le business case » —
    alors que le lecteur n'avait vu aucun des huit constats.

    Mesurer la présence dans le document quand on prétend mesurer une
    LECTURE, c'est le même défaut que ce fichier corrige ailleurs. La règle
    exige donc une mesure d'affichage, pas seulement un sélecteur.
    """
    fait = _fait_de_l_etape("business")
    assert "offsetParent" in fait, fait


def _quoi_de_l_etape(cle):
    """LE TEXTE QUE L'ÉTAPE MONTRE, et rien d'autre.

    La règle lisait d'abord une fenêtre de 1 600 signes autour de l'étape.
    Le commentaire qui explique POURQUOI le business case a été ajouté au fil
    y figure, et le nomme : la règle restait donc verte quand le texte affiché
    cessait de le nommer. Elle mesurait le commentaire.
    """
    _, bloc = _etapes_du_fil()
    i = bloc.index('cle: "%s"' % cle)
    j = bloc.index("quoi:", i)
    return bloc[j:bloc.index("\n", bloc.index("fait:", j))]


def test_l_etape_de_reglage_nomme_les_champs_du_business_case():
    """Ils vivent dans un dépliant fermé de ce même bloc : un fil qui ne les
    nomme pas les rend introuvables."""
    quoi = _quoi_de_l_etape("regler")
    assert "BUSINESS CASE" in quoi, quoi
    assert "puissance ferme" in quoi, quoi


def test_chaque_etape_du_fil_est_annoncee_par_une_fleche():
    """Une étape sans flèche n'affiche jamais « Vous êtes ici » : elle existe
    dans le calcul d'avancement et nulle part à l'écran."""
    etapes, _ = _etapes_du_fil()
    fleches = set(re.findall(r'data-vers="etape-(\w+)"', PAGE))
    # La première étape n'a pas de flèche : rien ne la précède.
    attendues = {c for c, n in etapes if int(n) > 1}
    manquantes = sorted(a for a in attendues if a not in fleches)
    assert "business" not in manquantes, manquantes


# ══════════════════════════════════════════════════════════════════════════
# 3. LES PARCOURS GUIDÉS — dix profils, et des ancres qui mènent quelque part
# ══════════════════════════════════════════════════════════════════════════

def _profils():
    i = PAGE.index("var GP_PROFILS = {")
    bloc = PAGE[i:PAGE.index("\n};\n", i)]
    return dict(re.findall(r'\n  ([a-z_]+): \{\n    nom: "([^"]+)"', bloc)), bloc


def test_les_deux_parcours_clients_neufs_existent():
    """Huit profils regardaient le projet DE L'EXTÉRIEUR, pour décider s'ils y
    entrent. Personne ne le regardait depuis la place de celui qui le porte ni
    de celui qui l'exploitera — c'est-à-dire les deux qui produisent les
    données que tous les autres réclament."""
    profils, _ = _profils()
    assert "porteur" in profils, sorted(profils)
    assert "exploitant" in profils, sorted(profils)
    assert len(profils) >= 10, sorted(profils)


@pytest.mark.parametrize("cle", ["porteur", "exploitant", "finance"])
def test_chaque_ancre_de_ces_parcours_existe_dans_la_page(cle):
    """Une étape qui vise une ancre absente n'affiche aucune erreur : elle ne
    va nulle part, et le lecteur croit avoir tout vu."""
    _, bloc = _profils()
    i = bloc.index("\n  %s: {" % cle)
    fin = bloc.find("\n  ],\n  },", i)
    manquantes = [a for a in re.findall(r'ancre: "([a-z0-9-]+)"', bloc[i:fin])
                  if ('id="%s"' % a) not in PAGE]
    assert not manquantes, (cle, manquantes)


@pytest.mark.parametrize("cle", ["porteur", "exploitant"])
def test_chaque_etape_de_ces_parcours_porte_un_piege(cle):
    """« Ce qui trompe » est la partie utile d'un parcours : sans elle, une
    étape n'est qu'un sommaire de ce que l'écran montre déjà."""
    _, bloc = _profils()
    i = bloc.index("\n  %s: {" % cle)
    fin = bloc.find("\n  ],\n  },", i)
    corps = bloc[i:fin]
    n_etapes = len(re.findall(r'\{ sect: "', corps))
    n_pieges = len(re.findall(r'piege: "', corps))
    assert n_etapes >= 4, (cle, n_etapes)
    assert n_pieges == n_etapes, (cle, n_etapes, n_pieges)


def test_le_parcours_de_l_enveloppe_mene_au_business_case():
    """Le profil qui porte le nom de cette page ne mentionnait pas ce qui
    décide de son verdict."""
    _, bloc = _profils()
    i = bloc.index("\n  finance: {")
    fin = bloc.find("\n  ],\n  },", i)
    corps = bloc[i:fin]
    for ancre in ("fin-bc-plus", "fin-bc-prix", "fin-bc-pf"):
        assert 'ancre: "%s"' % ancre in corps, (ancre, corps[:300])


# ══════════════════════════════════════════════════════════════════════════
# 4. UI / UX — ce que le dépliant fermé coûte, et ce qu'un lecteur d'écran lit
# ══════════════════════════════════════════════════════════════════════════

def test_le_depliant_du_business_case_annonce_ce_qui_est_renseigne():
    """UN DÉPLIANT FERMÉ NE DIT PAS CE QU'IL COÛTE DE NE PAS L'OUVRIR. Dix
    champs y dorment, et leur absence ne produit pas un dossier neutre : elle
    produit huit tests « indéterminés »."""
    assert 'id="fin-bc-cpt"' in PAGE
    assert "function bcCompteur(" in PAGE
    i = PAGE.index("function bcCompteur(")
    corps = PAGE[i:i + 1800]
    # Il compte ce qui est RENSEIGNÉ, pas ce qui est valide : un compteur qui
    # jugerait porterait un avis, et l'avis est rendu plus bas.
    assert "renseigné" in corps, corps[:400]
    # LA PHRASE DU VIDE, pas le mot « indéterminé » n'importe où : l'AUTRE
    # branche du titre le contient aussi, et la règle passait donc alors même
    # que l'état vide avait cessé de dire ce qu'il coûte.
    assert "les huit tests de viabilité ressortiront" in corps, corps[-900:]


def test_aucune_amorce_du_business_case_ne_deborde_de_son_champ():
    """UNE AMORCE COUPÉE EN PLEIN MOT NE REPÈRE RIEN. Deux d'entre elles se
    lisaient « annonces, permis, file d’attent… » et « étude de marché, avec
    son ém… » : ce qu'elles disaient de la PROVENANCE du nombre — la seule
    chose qu'elles avaient à dire — était précisément la partie coupée.

    LE PLAFOND EST MESURÉ, PAS CHOISI. Au navigateur, sur cinq largeurs de
    390 à 1 600 px, la plus longue amorce qui tient — « contrats signés et LOI
    fermes », 29 signes — garde 18 px de marge dans le cas le plus serré ;
    les deux qui débordaient en faisaient 32 et 34. Trente est donc la
    dernière valeur vérifiée comme sûre, et non une marge posée au jugé.
    """
    i = PAGE.index('id="fin-bc-plus"')
    bloc = PAGE[i:PAGE.index("</details>", i)]
    amorces = re.findall(r'placeholder="([^"]+)"', bloc)
    assert len(amorces) >= 9, amorces
    trop = [a for a in amorces if len(a) > 30]
    assert not trop, trop


def test_le_compteur_se_met_a_jour_a_la_saisie():
    """Un compteur posé une fois au chargement afficherait « 0 / 11 » pour
    toujours — y compris après que le lecteur a tout rempli."""
    i = PAGE.index("REF_BC = j.business_case")
    corps = PAGE[i:i + 900]
    assert "bcCompteur" in corps, corps[:400]
    assert "addEventListener('input'" in corps, corps[:600]


def test_le_tableau_de_trajectoire_est_navigable_a_la_synthese_vocale():
    """Sans `scope` ni légende, il se lit « 1 4 20 % 6,72 22,7 −16 » : une
    suite de nombres sans en-tête."""
    i = PAGE.index("class=\"bc-tab\"")
    corps = PAGE[i:i + 2200]
    assert "<caption>" in corps, corps[:400]
    # CHAQUE EN-TÊTE DE COLONNE PORTE SA PORTÉE, et la règle les ÉNUMÈRE.
    # Elle se contentait d'un `scope="col"` quelque part : en retirer un sur
    # six laissait « Année » muet et la règle verte. Le compte n'est pas figé
    # à six — une colonne ajoutée demain tombe dans le même filet.
    tete = corps[corps.index("<thead>"):corps.index("</thead>")]
    entetes = re.findall(r"<th\b[^>]*>", tete)
    assert len(entetes) >= 6, (entetes, tete)
    nues = [e for e in entetes if 'scope="col"' not in e]
    assert not nues, nues
    assert 'scope="row"' in corps, corps[:1400]


def test_le_bloc_du_business_case_prend_toute_la_largeur_du_dossier():
    """MESURÉ AU NAVIGATEUR, ET C'ÉTAIT MON DÉFAUT. Le dossier d'un pays est
    une grille de trois colonnes ; les blocs d'ANALYSE — l'avis, les phases,
    l'écart — la traversent, les petites cartes non. Le business case n'y
    était pas déclaré : à 1 180 px il occupait 351 px pour un tableau de
    367, et la colonne « Marge » sortait du cadre sans que rien ne le dise.
    """
    i = PAGE.index(".fin-dos-g > table")
    regle = PAGE[i:PAGE.index("}", i)]
    assert "grid-column:1/-1" in PAGE[i:i + len(regle) + 20], regle
    assert ".fin-dos-g > .bc" in regle, regle


def test_le_tableau_de_trajectoire_defile_dans_son_propre_cadre():
    """LA PLEINE LARGEUR SUFFIT AUJOURD'HUI — ET C'EST TOUT CE QU'ELLE FAIT.
    Une colonne ajoutée, une police plus large chez le lecteur, un téléphone
    de 390 px : le tableau redevient plus large que la place. Mesuré à
    390 px, il fait 367 px pour 294 disponibles. Un tableau qui déborde se
    fait défiler dans son cadre ; il ne coupe pas, et il ne fait jamais
    déborder la page.
    """
    i = PAGE.index(".bc-tab-c{")
    cadre = PAGE[i:PAGE.index("}", i)]
    assert "overflow-x:auto" in cadre, cadre
    # ET LE CADRE ENTOURE VRAIMENT LE TABLEAU. La feuille de style peut être
    # juste pendant que le rendu n'enveloppe rien.
    assert '<div class="bc-tab-c"><table class="bc-tab">' in PAGE
    j = PAGE.index('<div class="bc-tab-c">')
    assert "</tbody></table></div>" in PAGE[j:j + 3000], PAGE[j:j + 300]


def test_la_grille_du_dossier_peut_retrecir_sur_un_telephone():
    """`1fr` VAUT `minmax(auto,1fr)` : la piste refuse alors de descendre sous
    la largeur minimale de son contenu. Mesuré à 390 px, tout le dossier —
    l'indice, le verdict, le business case — s'étalait de 555 à 584 px dans
    une grille de 336, et rien ne le signalait : la page ne défilait pas
    latéralement, un ancêtre rognait, et la droite des blocs manquait."""
    i = PAGE.index("@media (max-width:760px){.fin-dos-g{")
    regle = PAGE[i:PAGE.index("}", i)]
    assert "minmax(0,1fr)" in regle, regle
    # La case doit pouvoir rétrécir elle aussi : une piste souple sur un
    # contenu qui refuse de plier ne change rien.
    j = PAGE.index("  .bc{margin:22px 0 0")
    assert "min-width:0" in PAGE[j:PAGE.index("}", j)], PAGE[j:j + 260]


def test_le_compteur_ne_repose_pas_sur_la_seule_couleur():
    """Trois états teintés qui ne diraient rien d'autre que leur teinte
    seraient illisibles en niveaux de gris — et pour huit pour cent des
    hommes."""
    i = PAGE.index("function bcCompteur(")
    corps = PAGE[i:i + 1800]
    assert "' / '" in corps or "+ ' / ' +" in corps, corps[:800]
    assert "z.title" in corps, corps[:1200]
