# -*- coding: utf-8 -*-
"""LE PARCOURS DORA — CELUI QUI SE VALIDE AU LIEU DE SE VISITER.

CE QUI A ÉTÉ DEMANDÉ. « Pour le parcours guidé détaillé avec infobulles de
DORA, créer un parcours spécifique ultra fluide pour accompagner le client
avec des flèches, des validations de blocs en vert, bleu clignotant en
attente de validation, passage automatique au module ou au calcul suivant
ou au bloc réglementaire et questionnaire suivant. »

CE QUE CELA CHANGE, ET CE N'EST PAS COSMÉTIQUE. Le guidage général de
Sentinel peint trois états — ouverte, à faire, pas atteinte — et porte
partout la même réserve :

    « Le vert dit que chaque étape a été OUVERTE, pas que le travail de
      chacune a été fait. Sentinel ne peut pas mesurer le second. »

Cette réserve est honnête sur la plupart des écrans : rien ne dit quand une
cartographie est finie. Elle ne l'est PAS sur DORA, dont chaque bloc porte
un jeu FERMÉ de déclarations. Le vert de ce parcours dit donc quelque chose
de plus fort — tous les champs attendus sont renseignés —, et ce sont ces
règles qui l'empêchent de retomber à « visité ».
"""
import io
import os
import re

import pytest

import dora
import dora_parcours
import dora_ponts

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _lire(nom):
    return io.open(os.path.join(_RACINE, nom), encoding="utf-8").read()


SENTINEL = _lire("sentinel.html")
PAGEJS = _lire("sentinel.page.js")
APP = _lire("app.py")

BANQUE = {"entite": "etablissement_credit", "identifiee_nis2": True}
PRESTA = {"entite": "prestataire_tic", "identifiee_nis2": True}
EXCLUE = {"entite": "retraite_professionnelle", "irp_quinze_affilies": True,
          "identifiee_nis2": False}


def _bloc(av, cle):
    return [b for b in av["blocs"] if b["cle"] == cle][0]


# ══════════════════════════════════════════════════════════════════════════
#  1. LE VERT DIT « VALIDÉ », ET CE N'EST PAS « VISITÉ »
# ══════════════════════════════════════════════════════════════════════════

def test_ouvrir_un_bloc_ne_le_valide_PAS():
    """LA DIFFÉRENCE AVEC TOUT LE RESTE DU SITE, EN UNE RÈGLE.

    Le guidage général note une étape « ouverte » dès qu'il y conduit. Si
    ce parcours-ci faisait de même, son vert vaudrait exactement le vert
    des autres — et la réserve qui dit « le vert ne dit pas que le travail
    est fait » redeviendrait nécessaire. Le seul juge est la DÉCLARATION :
    un moteur qui ne reçoit rien ne valide rien, quel que soit le nombre
    d'écrans ouverts.
    """
    av = dora_parcours.avancement({})
    assert av["valides"] == 0, av["valides"]
    assert av["courante"] == "qualifier"
    assert _bloc(av, "qualifier")["etat"] == "courante"


def test_un_bloc_se_valide_QUAND_ses_champs_sont_renseignes():
    """ET IL SE VALIDE ALORS SANS QU'ON AIT À LE DIRE. Le vert suit la
    déclaration, il ne se coche pas."""
    av = dora_parcours.avancement(BANQUE)
    assert _bloc(av, "qualifier")["etat"] == "validee"
    assert _bloc(av, "qualifier")["manque"] == []
    assert av["valides"] == 1


def test_chaque_bloc_NON_valide_nomme_ce_qui_lui_manque():
    """UN BLOC QUI CLIGNOTE SANS DIRE CE QU'IL ATTEND N'EST PAS UN
    GUIDAGE, C'EST UNE HUMEUR.

    Chaque entrée doit porter de quoi agir : le champ visé et ce qu'il
    est. Un compteur — « 3 réponses manquantes » — ne fait avancer
    personne, parce qu'il ne dit pas lesquelles.
    """
    for dossier in ({}, BANQUE):
        av = dora_parcours.avancement(dossier)
        for b in av["blocs"]:
            if b["etat"] in ("validee", "sans_objet"):
                continue
            assert b["manque"], (
                "le bloc « %s » est %s et ne nomme RIEN de ce qui lui "
                "manque" % (b["nom"], b["etat"]))
            for m in b["manque"]:
                assert m.get("champ") and m.get("quoi"), m
                assert len(m["quoi"]) > 20, (
                    "« %s » ne dit pas assez pour agir : %r"
                    % (b["nom"], m["quoi"]))


def test_les_vingt_six_articles_du_cadre_complet_sont_nommes_UN_A_UN():
    """LE CAS QUI ÉPROUVE LA RÈGLE PRÉCÉDENTE POUR DE BON. Vingt-six
    articles non déclarés doivent produire vingt-six lignes nommées, et
    non « le cadre de gestion du risque est incomplet »."""
    av = dora_parcours.avancement(BANQUE)
    manque = _bloc(av, "risque")["manque"]
    assert len(manque) == 26, len(manque)
    assert all(m["quoi"].startswith("Article ") for m in manque), manque[:2]


# ══════════════════════════════════════════════════════════════════════════
#  2. UN SEUL BLOC CLIGNOTE, ET IL EST LE PREMIER NON VALIDÉ
# ══════════════════════════════════════════════════════════════════════════

def test_UN_SEUL_etat_est_anime():
    """DEUX CHOSES QUI BATTENT À L'ÉCRAN NE DÉSIGNENT PLUS RIEN. Le
    clignotement cesse alors d'être un guidage pour devenir un décor, et
    c'est précisément ce qu'il ne doit pas être."""
    animes = [k for k, v in dora_parcours.ETATS.items() if v["anime"]]
    assert animes == ["courante"], animes


def test_la_GARDE_D_IMPORT_refuse_un_second_etat_anime():
    """LA VRAIE PROTECTION EST LA GARDE, ET ELLE MÉRITE SA PROPRE RÈGLE.

    La règle ci-dessus lit la table ; la garde d'import, elle, REFUSE que
    le module se charge si un second état s'anime. C'est la protection la
    plus forte — un défaut qui ne peut même pas démarrer — mais elle est
    invisible tant que rien ne l'éprouve : l'affaiblir ne casserait aucune
    règle, et le jour où quelqu'un animerait « attente », plus rien ne
    l'arrêterait.

    LA RÈGLE FABRIQUE DONC LE DÉFAUT et vérifie que la garde le nomme.
    """
    vrai = dora_parcours.ETATS["attente"]["anime"]
    try:
        dora_parcours.ETATS["attente"]["anime"] = True
        dora_parcours.ANIMES = tuple(
            k for k, v in dora_parcours.ETATS.items() if v["anime"])
        fautes = dora_parcours._verifier()
    finally:
        dora_parcours.ETATS["attente"]["anime"] = vrai
        dora_parcours.ANIMES = tuple(
            k for k, v in dora_parcours.ETATS.items() if v["anime"])
    assert any("animation" in f for f in fautes), (
        "la garde laisse passer un second état animé : %s" % fautes)
    assert not dora_parcours._verifier(), "la garde reste bruyante après coup"


def test_un_seul_bloc_est_COURANT_a_la_fois():
    """SUR CHACUNE DES SITUATIONS D'ESSAI, et pas seulement sur la plus
    simple : c'est en s'adaptant au profil que le parcours pourrait en
    désigner deux."""
    for dossier in ({}, BANQUE, PRESTA, EXCLUE):
        av = dora_parcours.avancement(dossier)
        courants = [b for b in av["blocs"] if b["etat"] == "courante"]
        assert len(courants) <= 1, (
            "%d blocs clignotent en même temps : %s"
            % (len(courants), [b["cle"] for b in courants]))
        if av["courante"]:
            assert courants and courants[0]["cle"] == av["courante"]


def test_le_courant_est_le_PREMIER_non_valide_et_non_le_suivant_du_dernier():
    """QUELQU'UN QUI A REMPLI 1, 2 ET 5 DOIT ÊTRE RAMENÉ À 3, qu'il a
    sauté — et non poussé vers 6. L'ordre des blocs porte une décision :
    le régime de l'article 16 commande ce que les suivants mesurent."""
    # Un dossier où l'incident (rang 5) est rempli mais pas les rangs 2 à 4.
    d = dict(BANQUE, services_critiques=True, connaissance="2026-03-01T08:00")
    av = dora_parcours.avancement(d)
    assert _bloc(av, "incident")["etat"] == "validee"
    assert av["courante"] == "iso", (
        "le parcours pousse vers %r alors que le bloc 2 est vide"
        % av["courante"])


# ══════════════════════════════════════════════════════════════════════════
#  3. LE PASSAGE AUTOMATIQUE A TOUJOURS UNE CIBLE
# ══════════════════════════════════════════════════════════════════════════

def test_le_SUIVANT_existe_meme_quand_les_blocs_d_apres_sont_VERROUILLES():
    """MESURÉ, ET CORRIGÉ.

    Une première version ne retenait comme suivant que les blocs
    « courante » ou « attente ». Sur une déclaration vide, les cinq blocs
    d'après sont VERROUILLÉS — faute de qualification — et le suivant
    valait donc None : le passage automatique n'avait aucune cible au
    moment précis où il en a le plus besoin, c'est-à-dire juste après la
    validation du premier bloc, qui les déverrouille tous.
    """
    av = dora_parcours.avancement({})
    assert av["courante"] == "qualifier"
    assert av["suivant"] == "iso", av["suivant"]
    assert _bloc(av, "iso")["etat"] == "verrouillee"


def test_le_suivant_SAUTE_les_blocs_sans_objet():
    """AVANCER AUTOMATIQUEMENT VERS UN BLOC BARRÉ serait pire que ne pas
    avancer : le client arriverait sur un écran qui lui dit qu'il ne le
    concerne pas, et il chercherait ce qu'il a mal fait."""
    av = dora_parcours.avancement(PRESTA)
    assert _bloc(av, "iso")["etat"] == "sans_objet"
    assert _bloc(av, "risque")["etat"] == "sans_objet"
    assert _bloc(av, "incident")["etat"] == "sans_objet"
    assert av["courante"] == "tiers"
    assert av["suivant"] == "supervision", av["suivant"]


def test_un_parcours_FINI_n_a_ni_courant_ni_suivant():
    """PEINDRE UN BLOC « À FAIRE » SUR UN PARCOURS ACHEVÉ rouvrirait un
    travail terminé, et le passage automatique tournerait en rond."""
    av = dora_parcours.avancement(EXCLUE)
    assert av["fini"] is True
    assert av["courante"] is None and av["suivant"] is None


# ══════════════════════════════════════════════════════════════════════════
#  4. LE PARCOURS S'ADAPTE, ET IL DIT POURQUOI
# ══════════════════════════════════════════════════════════════════════════

def test_le_prestataire_tiers_n_a_PAS_les_memes_blocs_qu_une_banque():
    """LE PARCOURS S'ADAPTE À QUI VOUS ÊTES. Les chapitres II à IV ne sont
    pas opposables à un prestataire tiers de services TIC ; lui présenter
    le cadre de gestion du risque « verrouillé » laisserait croire qu'il
    s'ouvrira plus tard. Il ne s'ouvrira jamais."""
    banque = dora_parcours.avancement(BANQUE)
    presta = dora_parcours.avancement(PRESTA)
    assert banque["total"] == 5, banque["total"]
    assert presta["total"] == 3, presta["total"]
    assert _bloc(banque, "supervision")["etat"] == "sans_objet", (
        "une entité financière reçoit le bloc de supervision : l'article "
        "31, §8, i), l'exclut expressément de la désignation")


def test_tout_bloc_SANS_OBJET_porte_son_motif():
    """UN BLOC BARRÉ SANS RAISON SE LIT COMME UNE PANNE. Avec son motif,
    il se comprend — et le motif cite l'article qui le fonde."""
    for dossier in (BANQUE, PRESTA, EXCLUE):
        av = dora_parcours.avancement(dossier)
        for b in av["blocs"]:
            if b["etat"] != "sans_objet":
                continue
            assert b["motif"] and len(b["motif"]) > 40, (b["cle"], b["motif"])
            # UN CHAPITRE CITE AUSSI PRÉCISÉMENT QU'UN ARTICLE, et c'est
            # même la bonne maille ici : « les chapitres II à IV ne sont
            # pas opposables » dit le motif entier, là où un article
            # isolé n'en dirait qu'un morceau. La règle exigeait
            # « article » et tombait sur un motif juste.
            motif = b["motif"].lower()
            assert "article" in motif or "chapitre" in motif, (
                "le motif de « %s » ne cite aucune disposition : %r"
                % (b["nom"], b["motif"]))


def test_tout_bloc_VERROUILLE_nomme_celui_dont_il_depend():
    """« VERROUILLÉ » SANS DIRE PAR QUOI OBLIGE À CHERCHER. Le motif nomme
    le bloc à compléter d'abord, et c'est ce qui fait la différence entre
    un guidage et un mur."""
    av = dora_parcours.avancement({})
    for b in av["blocs"]:
        if b["etat"] != "verrouillee":
            continue
        assert b["prerequis_manquants"], b["cle"]
        for p in b["prerequis_manquants"]:
            assert dora_parcours.BLOCS_PAR_CLE[p]["nom"] in b["motif"], (
                b["cle"], b["motif"])


def test_la_CONCLUSION_dit_ce_que_cent_pour_cent_signifie():
    """UN PARCOURS D'UN SEUL BLOC QUI SE SOLDE PAR « HORS CHAMP » NE SE
    FÉLICITE PAS. Cent pour cent sans cette phrase se lirait comme une
    réussite ; c'est une sortie du champ, et les deux ne se confondent
    pas."""
    av = dora_parcours.avancement(EXCLUE)
    assert av["part"] == 100.0
    assert av["conclusion"] and "exclue" in av["conclusion"], av["conclusion"]
    assert "pas que le travail est fait" in av["conclusion"], av["conclusion"]


# ══════════════════════════════════════════════════════════════════════════
#  5. AUCUN BLOC N'EST UNE IMPASSE
# ══════════════════════════════════════════════════════════════════════════

def test_chaque_bloc_ouvrable_PEUT_reellement_etre_valide():
    """LE DÉFAUT MESURÉ, ET C'EST LE PIRE QU'UN PARCOURS PUISSE AVOIR.

    Le bloc ISO exigeait, en plus de la question « êtes-vous certifié ? »,
    les mesures de l'annexe A déclarées en place — sans qu'aucun champ ne
    permette de les saisir. Il ne pouvait donc JAMAIS passer au vert, et
    le parcours s'arrêtait là pour tout organisme certifié.

    LA RÈGLE PARCOURT LE CHEMIN EN ENTIER, bloc par bloc, en répondant à
    tout ce qui est demandé. Si un bloc reste rouge alors que toutes ses
    réponses ont été données, c'est une impasse — et elle ne se voit
    autrement qu'en la rencontrant.
    """
    d = dict(BANQUE, iso27001_certifie=True,
             etats={a[0]: "prouve"
                    for a in dora_parcours.dora_risque.articles("complet")},
             contrats=[{"fonction_critique": False,
                        "clauses": {"commune_%s" % l: "presente"
                                    for l in "abcdefghi"}}],
             services_critiques=True, connaissance="2026-03-01T08:00")
    av = dora_parcours.avancement(d)
    bloques = [b["cle"] for b in av["blocs"]
               if b["etat"] not in ("validee", "sans_objet")]
    assert not bloques, (
        "ces blocs restent non validés alors que tout est renseigné : %s"
        % bloques)
    assert av["fini"] is True


def test_le_bloc_ISO_se_valide_sur_la_SEULE_question_qui_le_justifie():
    """CE QUE CE BLOC SERT À SAVOIR : s'il y a des preuves à reprendre.
    Les mesures précisent la carte ; elles ne conditionnent pas la
    réponse, sans quoi le bloc devient plus lourd que son objet."""
    for reponse in (True, False):
        av = dora_parcours.avancement(dict(BANQUE, iso27001_certifie=reponse))
        assert _bloc(av, "iso")["etat"] == "validee", reponse


def test_les_quatre_themes_de_l_annexe_A_sont_offerts_pour_AFFINER():
    """ET ILS SONT DÉRIVÉS D'`iso27001`, JAMAIS RECOPIÉS. Un second
    tableau des quatre-vingt-treize mesures divergerait du premier à la
    première mise à jour."""
    import iso27001
    themes = dora_ponts.themes_iso()
    assert [t["cle"] for t in themes] == ["A.5", "A.6", "A.7", "A.8"]
    citees = {m for _n, _c, mes, _ch, _m in dora_ponts.CORRESPONDANCE
              for m in mes}
    assert sum(len(t["mesures"]) for t in themes) == len(citees)
    for t in themes:
        for m in t["mesures"]:
            assert iso27001.MESURES[m]["theme"] == t["cle"], (m, t["cle"])


# ══════════════════════════════════════════════════════════════════════════
#  6. L'ÉCRAN — LES FLÈCHES, LES COULEURS, ET LE FREIN
# ══════════════════════════════════════════════════════════════════════════

PANNEAUX = ("dora-qualifier", "dora-iso", "dora-risque", "dora-tiers",
            "dora-incident", "dora-supervision")


@pytest.mark.parametrize("panneau", PANNEAUX)
def test_chaque_panneau_DORA_porte_le_rail(panneau):
    """LE RAIL EST DANS LES SIX, et pas seulement sur le premier : un
    parcours qu'on perd de vue dès la deuxième page n'est pas un
    parcours."""
    assert 'id="dora-rail-%s"' % panneau.replace("dora-", "") in SENTINEL, (
        "le panneau %s n'a pas de rail" % panneau)


def test_les_CINQ_etats_ont_leur_classe_et_UNE_SEULE_est_animee():
    """LE MOTEUR DIT QU'UN SEUL ÉTAT S'ANIME ; LA FEUILLE DE STYLE DOIT
    LE TENIR. Deux animations déclarées en CSS feraient battre deux blocs
    quoi que dise le moteur — c'est l'écran que le client regarde."""
    for etat in dora_parcours.ETATS:
        assert ".dr-bloc.%s{" % etat in SENTINEL.replace(" ", ""), etat
    # « animation:none » EST L'INVERSE D'UNE ANIMATION, et la règle le
    # comptait comme une. Elle tombait donc sur la ligne qui ARRÊTE le
    # battement sous `prefers-reduced-motion` — c'est-à-dire sur la
    # correction, pas sur le défaut.
    animes = [m.group(1) for m in
              re.finditer(r"\.dr-bloc\.(\w+)\{[^}]*?animation:\s*(\w+)",
                          SENTINEL)
              if m.group(2) != "none"]
    assert animes == ["courante"], (
        "ces états portent une animation : %s" % animes)


def test_le_battement_S_ARRETE_pour_qui_le_demande():
    """UN MOUVEMENT QU'ON NE PEUT PAS FAIRE CESSER EST UNE GÊNE, PAS UN
    GUIDAGE. Et le bloc ne doit pas se perdre pour autant : le contour
    s'épaissit là où le battement s'arrête."""
    i = SENTINEL.index("@media(prefers-reduced-motion:reduce){\n  .dr-bloc")
    bloc = SENTINEL[i:SENTINEL.index("}", SENTINEL.index("}", i) + 1)]
    assert "animation:none" in bloc.replace(" ", ""), bloc
    assert "border-width" in bloc, (
        "le battement s'arrête sans que rien ne désigne plus le bloc : %r"
        % bloc)


def test_les_fleches_relient_les_blocs():
    """SANS ELLES, SIX PASTILLES ALIGNÉES SE LISENT COMME SIX ONGLETS
    INTERCHANGEABLES — or l'ordre porte une décision."""
    assert ".dr-fleche{" in SENTINEL.replace(" ", "")
    assert "dr-fleche" in PAGEJS, "le rail ne pose aucune flèche"


def test_le_passage_automatique_a_un_FREIN_visible():
    """DÉPLACER QUELQU'UN SANS PRÉVENIR EST HOSTILE. Le décompte
    s'affiche, il s'annule d'un clic, et le client peut aussi y aller
    tout de suite."""
    assert "doraAutoAnnuler" in PAGEJS and "doraAutoMaintenant" in PAGEJS
    i = PAGEJS.index("function doraAutoLancer")
    corps = PAGEJS[i:PAGEJS.index("\nfunction doraAutoAnnuler", i)]
    assert "Rester ici" in corps, (
        "le décompte part sans offrir de rester")
    assert "setInterval" in corps and "dans ' + reste" in corps, (
        "le décompte n'est pas visible : on est déplacé sans préavis")


def test_le_passage_automatique_ne_part_QUE_sur_une_validation():
    """PARTIR AU PREMIER AFFICHAGE DÉPLACERAIT QUELQU'UN QUI VIENT
    D'OUVRIR L'ÉCRAN, et qui n'a rien validé du tout."""
    i = PAGEJS.index("function doraAutoSuite")
    corps = PAGEJS[i:PAGEJS.index("\nfunction doraAutoLancer", i)]
    assert "if (!avant" in corps, (
        "le premier affichage n'est pas distingué d'une validation")
    assert "devenu.etat !== 'validee'" in corps, (
        "le passage part sans vérifier que le bloc quitté est VALIDÉ")


def test_l_infobulle_du_rail_porte_le_piege_de_chaque_bloc():
    """UNE PASTILLE DE QUELQUES PIXELS NE SE LIT PAS. L'infobulle porte ce
    que la pastille ne peut pas : ce que le bloc fait, pourquoi il est là,
    et le piège qui lui est propre."""
    # L'ANCRE EST PRISE DANS `doraRailPeindre`, ET NON DANS LE FICHIER
    # ENTIER : « var bulle = » existe aussi dans le bandeau générique du
    # site, et la règle lisait ce bloc-là — elle mesurait autre chose que
    # ce qu'elle nomme, ce qui est le défaut qu'elle est censée attraper
    # ailleurs.
    debut = PAGEJS.index("function doraRailPeindre()")
    i = PAGEJS.index("var bulle = ", debut)
    corps = PAGEJS[i:i + 420]
    for champ in ("b.quoi", "b.pourquoi", "b.piege", "e.dit"):
        assert champ in corps, (
            "l'infobulle du rail ne porte pas %s : %r" % (champ, corps[:120]))


def test_la_route_du_parcours_existe_et_sa_cadence_est_LARGE():
    """ELLE EST APPELÉE À CHAQUE CHAMP RENSEIGNÉ — c'est ce qui rend le
    guidage vivant. Lui donner la cadence d'un calcul ferait mourir le
    rail au milieu d'un questionnaire de vingt-six articles, c'est-à-dire
    exactement là où il sert."""
    assert "@app.route('/api/dora/parcours'" in APP
    i = APP.index("@app.route('/api/dora/parcours'")
    m = re.search(r"@rate_limit\(limit=(\d+), window=(\d+)\)", APP[i:i + 200])
    assert m, APP[i:i + 200]
    assert int(m.group(1)) >= 120, (
        "la cadence de %s par %s s ne tient pas un questionnaire de "
        "vingt-six articles" % (m.group(1), m.group(2)))


def test_chaque_saisie_DORA_redemande_l_avancement():
    """UN RAIL QUI NE SE RAFRAÎCHIRAIT QU'AU CHANGEMENT D'ÉCRAN laisserait
    le bloc courant clignoter alors qu'il vient d'être complété, et le
    client chercherait ce qui manque encore."""
    for saisie in ("doraChamp", "doraPorte", "doraEtat", "doraContrat",
                   "doraClause", "doraInc", "doraSeuil", "doraSup",
                   "doraIso"):
        i = PAGEJS.index("window.%s = %s;" % (saisie, saisie))
        debut = PAGEJS.rindex("function %s(" % saisie, 0, i)
        assert "doraParcours()" in PAGEJS[debut:i], (
            "« %s » modifie la déclaration sans redemander l'avancement : "
            "le rail restera faux jusqu'au prochain changement d'écran"
            % saisie)


def test_chaque_ancre_de_la_batterie_du_parcours_EXISTE_ENCORE():
    """UNE BATTERIE DONT LES ANCRES ONT GLISSÉ EST UNE BATTERIE INERTE, et
    le banc la lit comme une régression du code.

    MESURÉ DEUX FOIS SUR CETTE BATTERIE-CI : deux ancres écrites avec les
    échappements `\\uXXXX` ne se trouvaient pas, parce que les fichiers
    portent les CARACTÈRES eux-mêmes. Les mutations ne modifiaient rien,
    le banc les comptait survivantes, et les deux règles qu'elles
    éprouvaient ne l'étaient plus par personne.
    """
    import json
    table = json.load(io.open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "mutations_dora_parcours.json"), encoding="utf-8"))
    perimees = []
    for m in table["mutations"]:
        n = _lire(m["fichier"]).count(m["avant"])
        if n != 1:
            perimees.append("%s — %s : %d occurrence(s)"
                            % (m["fichier"], m["nom"], n))
    assert not perimees, (
        "%d ancre(s) périmée(s) :\n    %s"
        % (len(perimees), "\n    ".join(perimees)))


def test_chaque_mutation_du_parcours_NOMME_une_regle_QUI_EXISTE():
    """UNE MUTATION QUI VISE UNE RÈGLE DISPARUE se compte comme survivante
    pour une raison qui n'a rien à voir avec le code.

    ET LE NOM D'UNE RÈGLE PARAMÉTRÉE PORTE SON PARAMÈTRE : le banc compare
    des noms exacts, et `test_x` ne vaut pas `test_x[dora-supervision]`.
    """
    import json
    table = json.load(io.open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "mutations_dora_parcours.json"), encoding="utf-8"))
    source = (io.open(os.path.abspath(__file__), encoding="utf-8").read()
              + _lire(os.path.join("tests", "test_dora.py")))
    for m in table["mutations"]:
        nom = m["regle"].split("[")[0]
        assert ("def %s(" % nom) in source, (
            "la mutation « %s » vise %s, qui n'existe dans aucune cible"
            % (m["nom"], m["regle"]))
