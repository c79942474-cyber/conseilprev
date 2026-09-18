# -*- coding: utf-8 -*-
"""ISO/IEC 27001 — DEUX DATES, UNE SIGNATURE, ET UNE TROISIÈME COLONNE.

CE QUI A DÉCLENCHÉ CE FICHIER. Un questionnaire d'auto-évaluation ISO 27001 en
pièce jointe, et une demande : « ajouter ISO 27001 analyse de risque
conformité ».

LE PREMIER FAIT À DIRE EST QUE LA PIÈCE JOINTE EST PÉRIMÉE. Elle porte sur
ISO/IEC 27001:2013 — © BSI Group, réf. BSI/UK/820/SC/0316/EN/BLD, 2016 — et la
version en vigueur est 27001:2022. L'annexe A y est passée de 114 mesures en
14 chapitres à 93 en 4 thèmes, dont ONZE entièrement nouvelles. Un organisme
qui remplit ce questionnaire conclut qu'il est prêt, et découvre à l'audit
qu'on lui demande onze mesures dont il n'a jamais entendu parler, sur une
numérotation qui n'existe plus.

LES TROIS DÉFAUTS QUE CES RÈGLES GARDENT, ET AUCUN NE SE VOIT À LA LECTURE
DU DOCUMENT FINAL

  1. LES CRITÈRES D'ACCEPTATION ÉCRITS APRÈS LA COTATION. L'article 6.1.2 a)
     demande de les ÉTABLIR ; les fixer après avoir vu les résultats donne un
     registre où tout est acceptable. Seul l'ORDRE DES DEUX DATES distingue un
     registre honnête d'un registre arrangé.

  2. LE PROPRIÉTAIRE NOMMÉ MAIS PAS SIGNATAIRE. L'article 6.1.3 e) demande
     l'acceptation des risques résiduels PAR LES PROPRIÉTAIRES. Une colonne
     « propriétaire » remplie ne vaut pas une acceptation datée : l'auditeur
     demande la signature, pas le nom.

  3. LA TROISIÈME COLONNE DE LA DÉCLARATION D'APPLICABILITÉ. L'article
     6.1.3 d) demande, pour chaque mesure : la décision, sa justification dans
     les DEUX sens, ET le statut de mise en œuvre. Celle d'ISO 42001 n'en
     demande que deux ; servir le même gabarit aux deux normes fait perdre
     exactement la colonne que l'auditeur recoupe avec le terrain.

CE QUE CES RÈGLES NE PEUVENT PAS FAIRE. Dire qu'un organisme obtiendra son
certificat : l'étape 2 s'audite sur des preuves d'exécution que Sentinel ne
détient pas. Et elles ne connaissent pas la date de fin de transition des
certificats 2013 — le module la déclare comme non vérifiée, et une règle
ci-dessous garde cette réserve.
"""
import io
import os
import re

import pytest

import iso27001 as iso

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _source(nom):
    return io.open(os.path.join(_RACINE, nom), encoding="utf-8").read()


def _criteres(etabli="2026-01-01", apprecie="2026-02-01", seuil=6):
    return {"seuil_acceptation": seuil, "etabli_le": etabli,
            "apprecie_le": apprecie}


def _risque(**kw):
    base = {"nom": "Rançongiciel", "vraisemblance": 3, "consequence": 4,
            "disponibilite": True, "proprietaire": "DSI"}
    base.update(kw)
    return base


# ═══════════════════════════════════════════════════════════════════════════
#  1. LES DEUX DATES — L'ORDRE EST LA RÈGLE
# ═══════════════════════════════════════════════════════════════════════════

def test_des_criteres_POSTERIEURS_a_l_appreciation_invalident_le_registre():
    """LA RÈGLE CENTRALE DE CE FICHIER, et elle tient en deux cas jumeaux.

    Le même risque, les mêmes critères, la même cotation. Seul l'ORDRE des
    deux dates change — et c'est la seule chose qui distingue un registre
    honnête d'un registre dont les critères ont été taillés sur les
    résultats. Aucune relecture du document final ne fait cette différence.
    """
    tardif = iso.apprecier([_risque()], _criteres("2026-05-01", "2026-04-01"))
    tot = iso.apprecier([_risque()], _criteres("2026-03-01", "2026-04-01"))
    assert tardif["valide"] is False
    assert tardif["criteres"]["ordre"]["cle"] == "criteres_posterieurs"
    assert "POSTÉRIEURS" in tardif["criteres"]["ordre"]["dit"]
    assert tot["valide"] is True, (
        "des critères antérieurs doivent valider : %s"
        % tot["criteres"]["ordre"])


def test_des_dates_manquantes_ne_valent_pas_des_dates_dans_le_bon_ordre():
    """LE CAS QUI PASSERAIT SANS ÇA. Un moteur qui ne comparerait les dates
    que lorsqu'elles existent laisserait passer un registre non daté — et
    c'est le cas le plus fréquent, parce que personne ne date volontairement
    un document qu'il a écrit après coup."""
    sans_criteres = iso.apprecier([_risque()], _criteres("", "2026-04-01"))
    sans_appreciation = iso.apprecier([_risque()], _criteres("2026-01-01", ""))
    assert sans_criteres["criteres"]["ordre"]["cle"] == "criteres_non_dates"
    assert sans_appreciation["criteres"]["ordre"]["cle"] == "appreciation_non_datee"
    assert not sans_criteres["valide"] and not sans_appreciation["valide"]


def test_le_meme_jour_est_accepte():
    """LA BORNE. « Établis avant » n'exige pas « la veille » : critères et
    appréciation écrits le même jour sont ordinaires, et les refuser
    inventerait une exigence que la norme ne pose pas."""
    r = iso.apprecier([_risque()], _criteres("2026-04-01", "2026-04-01"))
    assert r["criteres"]["ordre"]["ok"] is True


# ═══════════════════════════════════════════════════════════════════════════
#  2. LE PROPRIÉTAIRE — NOMMÉ NE SUFFIT PAS, IL FAUT SIGNÉ ET DATÉ
# ═══════════════════════════════════════════════════════════════════════════

def test_un_risque_sans_proprietaire_rend_le_registre_invalide():
    """L'ARTICLE 6.1.2 c) 2) demande un propriétaire POUR CHAQUE RISQUE. Une
    ligne sans propriétaire ne pourra être acceptée par personne — le défaut
    se propage jusqu'à l'article 6.1.3 e)."""
    sans = iso.apprecier([_risque(proprietaire="")], _criteres())
    assert sans["valide"] is False
    assert sans["defauts"] and "propriétaire" in sans["defauts"][0]["manques"]
    avec = iso.apprecier([_risque()], _criteres())
    assert avec["valide"] is True


def test_un_risque_qui_n_atteint_aucune_des_trois_proprietes_est_incomplet():
    """CONFIDENTIALITÉ, INTÉGRITÉ, DISPONIBILITÉ — art. 6.1.2 c) 1). Un
    risque qui n'en atteint aucune peut être réel ; il relève d'un autre
    registre, et le compter ici gonfle une analyse de sécurité avec des
    risques qui n'en sont pas."""
    r = iso.apprecier([_risque(disponibilite=False)], _criteres())
    assert r["valide"] is False
    assert "propriété atteinte" in r["defauts"][0]["manques"]


def test_maintenir_un_risque_exige_une_acceptation_ECRITE_ET_DATEE():
    """LE FAIT QUI COÛTE UN AUDIT. « Maintenir » est une option légitime —
    à condition que le propriétaire l'ait écrit et daté. Sans cela, le
    registre dit que quelqu'un a accepté, et personne ne l'a fait."""
    sans = iso.traiter([_risque(option="maintenir")], _criteres())
    assert sans["recevable"] is False
    assert "Rançongiciel" in sans["sans_acceptation"]
    avec = iso.traiter([_risque(option="maintenir", accepte_par="DSI",
                                accepte_le="2026-05-02")], _criteres())
    assert avec["recevable"] is True, avec["bloquants"]


def test_choisir_MAINTENIR_exige_une_acceptation_MEME_sous_le_seuil():
    """CE QUE LA BATTERIE DE MUTATIONS A MONTRÉ, et la règle qui manquait.

    La règle précédente employait un risque à 12, très au-dessus du seuil :
    l'acceptation y était déjà exigée par le NIVEAU, et supprimer la clause
    « ou l'option est maintenir » ne changeait rien. Elle mesurait donc le
    seuil, pas la clause qu'elle nomme.

    ICI LE RISQUE EST À 2, SOUS LE SEUIL. Seule la clause « maintenir »
    peut exiger une signature — et elle doit l'exiger : choisir de maintenir
    est une DÉCISION, et une décision que personne n'a signée est exactement
    le défaut que ce module existe pour faire voir. Le module l'écrit dans
    sa table des options, cette règle le tient."""
    sans = iso.traiter([_risque(vraisemblance=1, consequence=2,
                                option="maintenir")], _criteres())
    assert sans["lignes"][0]["acceptable_retenu"] is True, (
        "le risque doit être SOUS le seuil : sinon la règle mesure le "
        "niveau, pas la clause")
    assert sans["lignes"][0]["acceptation_requise"] is True
    assert sans["recevable"] is False
    avec = iso.traiter([_risque(vraisemblance=1, consequence=2,
                                option="maintenir", accepte_par="DSI",
                                accepte_le="2026-05-02")], _criteres())
    assert avec["recevable"] is True


def test_une_acceptation_SIGNEE_MAIS_NON_DATEE_ne_compte_pas():
    """L'AUTRE MOITIÉ QUE LA BATTERIE A TROUVÉE. Les règles éprouvaient
    « aucune signature » et « la mauvaise signature », jamais « la bonne
    signature sans date ». Or c'est le cas réel : un tableur avec une
    colonne « accepté par » remplie et aucune colonne de date. Sans date,
    rien ne dit que l'acceptation précède l'audit — ni même qu'elle a eu
    lieu."""
    sans_date = iso.traiter([_risque(option="maintenir", accepte_par="DSI")],
                            _criteres())
    assert sans_date["lignes"][0]["acceptation"]["par_le_proprietaire"] is True, (
        "le signataire EST le propriétaire : c'est bien la date seule qui "
        "manque")
    assert sans_date["lignes"][0]["acceptation"]["valide"] is False
    assert sans_date["recevable"] is False
    assert "Rançongiciel" in sans_date["sans_acceptation"]


def test_l_acceptation_par_QUELQU_UN_D_AUTRE_que_le_proprietaire_ne_compte_pas():
    """CE QUE CETTE RÈGLE ATTRAPE, ET QU'UNE CASE COCHÉE NE DIT PAS. Le RSSI
    signe à la place du métier : le document a l'air complet, la signature
    existe, elle n'est pas celle que l'article 6.1.3 e) demande."""
    r = iso.traiter([_risque(option="maintenir", accepte_par="RSSI",
                             accepte_le="2026-05-02")], _criteres())
    assert r["recevable"] is False
    ligne = r["lignes"][0]
    assert ligne["acceptation"]["par_le_proprietaire"] is False
    assert ligne["acceptation"]["valide"] is False


def test_un_risque_sous_le_seuil_n_exige_aucune_acceptation():
    """LE TÉMOIN INVERSE, sans lequel la règle précédente passerait sur un
    moteur qui exigerait une signature partout — et rendrait le registre
    impossible à clore."""
    r = iso.traiter([_risque(vraisemblance=1, consequence=2)], _criteres())
    assert r["lignes"][0]["acceptation_requise"] is False
    assert r["recevable"] is True


# ═══════════════════════════════════════════════════════════════════════════
#  3. UN PLAN N'EST PAS UNE MESURE
# ═══════════════════════════════════════════════════════════════════════════

def test_le_niveau_residuel_n_est_retenu_que_si_les_mesures_sont_MISES_EN_OEUVRE():
    """LA FAÇON LA PLUS COURANTE DE RENDRE UN REGISTRE VERT SANS RIEN FAIRE.
    On coche l'option, on saisit un résiduel optimiste, et le tableau passe
    au vert sur une PRÉVISION. Le module retient le niveau initial tant que
    la mise en œuvre n'est pas déclarée."""
    prevu = iso.traiter([_risque(option="modifier",
                                 residuel_vraisemblance=1,
                                 residuel_consequence=2)], _criteres())
    fait = iso.traiter([_risque(option="modifier",
                                mesures_mises_en_oeuvre=True,
                                residuel_vraisemblance=1,
                                residuel_consequence=2)], _criteres())
    assert prevu["lignes"][0]["niveau"] == 12
    assert prevu["lignes"][0]["niveau_retenu"] == 12, (
        "un résiduel prévu ne doit pas faire baisser le niveau retenu : %s"
        % prevu["lignes"][0]["niveau_retenu"])
    assert prevu["lignes"][0]["residuel_acquis"] is False
    assert fait["lignes"][0]["niveau_retenu"] == 2
    assert fait["lignes"][0]["residuel_acquis"] is True


def test_declarer_des_mesures_faites_sans_coter_le_residuel_est_signale():
    """SINON LE MOTEUR RETOMBERAIT SILENCIEUSEMENT SUR LE NIVEAU INITIAL, et
    l'utilisateur croirait que sa saisie n'a servi à rien alors qu'elle est
    incomplète."""
    r = iso.traiter([_risque(option="modifier",
                             mesures_mises_en_oeuvre=True)], _criteres())
    assert "Rançongiciel" in r["residuel_non_cote"]
    assert r["recevable"] is False


def test_un_risque_au_dessus_du_seuil_sans_option_est_bloquant():
    r = iso.traiter([_risque()], _criteres())
    assert "Rançongiciel" in r["sans_option"]
    assert r["recevable"] is False


def test_le_niveau_est_le_produit_des_deux_cotations():
    assert iso.niveau(3, 4) == 12
    assert iso.niveau(1, 1) == 1
    assert iso.niveau(4, 4) == 16
    assert iso.niveau(0, 3) is None, "une cotation hors échelle est acceptée"
    assert iso.niveau(3, 9) is None


# ═══════════════════════════════════════════════════════════════════════════
#  4. LA DÉCLARATION D'APPLICABILITÉ — TROIS COLONNES, PAS DEUX
# ═══════════════════════════════════════════════════════════════════════════

def _toutes(decision, justification=None, statut=None, sauf=()):
    d = {}
    for n in iso.MESURES:
        if n in sauf:
            continue
        e = {"decision": decision}
        if justification:
            e["justification"] = justification
        if statut:
            e["statut"] = statut
        d[n] = e
    return d


def test_une_mesure_retenue_SANS_STATUT_n_est_pas_recevable():
    """LA COLONNE PROPRE À 27001, ET LA DÉMONSTRATION QU'ELLE COMPTE. Toutes
    les mesures retenues, toutes justifiées — et la déclaration ne passe pas,
    parce qu'aucune ne dit où elle en est. Le gabarit d'ISO 42001, qui ne
    demande que deux colonnes, produit exactement ce document-là."""
    sans = iso.declaration_applicabilite(_toutes("retenue", "motif"))
    assert sans["recevable"] is False
    assert len(sans["sans_statut"]) == len(iso.MESURES) == 93
    avec = iso.declaration_applicabilite(
        _toutes("retenue", "motif", "mise_en_oeuvre"))
    assert avec["recevable"] is True


def test_une_mesure_ECARTEE_n_a_pas_besoin_de_statut():
    """LE TÉMOIN INVERSE, ET IL N'EST PAS DE PURE FORME. Exiger un statut
    d'une mesure écartée ferait compter comme un manque ce qui est une
    décision — et pousserait à tout retenir pour éviter des lignes rouges."""
    r = iso.declaration_applicabilite(_toutes("ecartee", "hors périmètre"))
    assert r["recevable"] is True
    assert r["sans_statut"] == []
    assert r["taux_mise_en_oeuvre"] is None


def test_la_justification_est_exigee_dans_les_DEUX_sens():
    """ART. 6.1.3 d) : justification de l'inclusion COMME de l'exclusion. Un
    moteur qui ne l'exigerait que d'un côté laisserait passer la moitié du
    défaut."""
    ret = iso.declaration_applicabilite(_toutes("retenue", None,
                                                "mise_en_oeuvre"))
    eca = iso.declaration_applicabilite(_toutes("ecartee"))
    assert len(ret["sans_justification"]) == 93
    assert len(eca["sans_justification"]) == 93
    assert not ret["recevable"] and not eca["recevable"]


def test_une_mesure_non_decidee_arrete_l_audit_quel_que_soit_le_taux():
    """92 MESURES SUR 93 MISES EN ŒUVRE, UNE CASE VIDE, ET L'AUDIT S'ARRÊTE.
    Le taux ne prédit rien ; le compteur « non décidées » décide."""
    d = _toutes("retenue", "motif", "mise_en_oeuvre", sauf=("A.8.23",))
    soa = iso.declaration_applicabilite(d)
    assert soa["taux_mise_en_oeuvre"] == 100
    assert soa["recevable"] is False
    assert soa["non_decidees"] == ["A.8.23"]
    assert any("A.8.23" in b for b in soa["bloquants"])


def test_le_taux_de_mise_en_oeuvre_ne_porte_que_sur_les_mesures_retenues():
    d = _toutes("ecartee", "hors périmètre")
    for n in ("A.5.1", "A.5.2", "A.5.3", "A.5.4"):
        d[n] = {"decision": "retenue", "justification": "retenue",
                "statut": "mise_en_oeuvre"}
    soa = iso.declaration_applicabilite(d)
    assert soa["taux_mise_en_oeuvre"] == 100
    assert soa["retenues"] == 4


# ═══════════════════════════════════════════════════════════════════════════
#  5. LE MILLÉSIME — LE FAIT PRINCIPAL DU MODULE
# ═══════════════════════════════════════════════════════════════════════════

def test_l_organisme_certifie_2013_a_ONZE_mesures_devant_lui_et_pas_93():
    """LA MESURE QUI PORTE TOUT LE MODULE. Un organisme certifié contre la
    version 2013 a traité 82 mesures sur 93 ; son reste à faire est de ONZE,
    et son taux de mise en œuvre affiche 100 % sur ce qu'il a traité. Les
    deux chiffres sont vrais, et seul le second rassure à tort."""
    d = _toutes("retenue", "issue du traitement", "mise_en_oeuvre",
                sauf=iso.NOUVELLES_2022)
    soa = iso.declaration_applicabilite(d)
    assert soa["taux_mise_en_oeuvre"] == 100
    assert soa["retenues"] == 82
    assert sorted(soa["non_decidees"]) == sorted(iso.NOUVELLES_2022)
    assert soa["nouvelles_2022"]["total"] == 11
    assert sorted(soa["nouvelles_2022"]["non_decidees"]) == sorted(iso.NOUVELLES_2022)


def test_le_questionnaire_fourni_vise_une_version_QUI_N_EST_PLUS_la_norme():
    """LE PREMIER FAIT À DIRE, ET LE MODULE LE PORTE DANS SA SOURCE. Un
    module qui déclarerait le questionnaire conforme à la version en vigueur
    laisserait un client préparer son audit contre une norme retirée."""
    q = iso.SOURCE_QUESTIONNAIRE
    assert q["vise"] == "ISO/IEC 27001:2013"
    assert q["vise"] != iso.SOURCE["court"]
    assert iso.SOURCE["court"] == "ISO/IEC 27001:2022"
    assert "retirée" in q["reserve"] or "succédé" in q["reserve"]


def test_l_annexe_A_a_maigri_entre_2013_et_2022_et_la_table_le_sait():
    assert iso.MILLESIMES["2013"]["mesures"] == 114
    assert iso.MILLESIMES["2022"]["mesures"] == 93
    assert iso.MILLESIMES["2013"]["groupes"] == 14
    assert iso.MILLESIMES["2022"]["groupes"] == 4
    assert iso.MILLESIMES["2013"]["en_vigueur"] is False
    assert iso.MILLESIMES["2022"]["en_vigueur"] is True


def test_les_onze_nouvelles_existent_toutes_dans_l_annexe_A():
    """UNE LISTE DE NOUVEAUTÉS QUI CITERAIT UNE MESURE INEXISTANTE ferait
    chercher longtemps."""
    assert len(iso.NOUVELLES_2022) == 11
    for n in iso.NOUVELLES_2022:
        assert n in iso.MESURES, "mesure nouvelle inconnue : %s" % n
        assert iso.MESURES[n]["nouvelle_2022"] is True
    autres = [n for n, m in iso.MESURES.items()
              if m["nouvelle_2022"] and n not in iso.NOUVELLES_2022]
    assert not autres, "des mesures se déclarent nouvelles hors liste : %s" % autres


# ═══════════════════════════════════════════════════════════════════════════
#  6. LE DROIT D'AUTEUR — DEUX TITULAIRES, DEUX RÉSERVES
# ═══════════════════════════════════════════════════════════════════════════

def test_la_table_des_mesures_ne_porte_QUE_numeros_titres_et_millesime():
    """LA RÈGLE QUI PROTÈGE LE DÉPÔT. Elle énumère les CHAMPS AUTORISÉS
    plutôt que d'inspecter le contenu — une inspection de contenu se
    contourne en reformulant trois mots. Ajouter un champ `exigence` ou
    `texte` pour « enrichir » la restitution fait tomber cette règle avant
    que la contrefaçon n'atteigne une page servie."""
    permises = {"theme", "theme_titre", "theme_dit", "titre", "nouvelle_2022"}
    for num, m in iso.MESURES.items():
        en_trop = set(m) - permises
        assert not en_trop, (
            "la mesure %s porte un champ non prévu (%s)"
            % (num, ", ".join(sorted(en_trop))))


def test_les_deux_sources_declarent_leur_reproduction_interdite():
    """DEUX TITULAIRES DISTINCTS, ET AUCUN N'AUTORISE LA COPIE : l'ISO pour
    la norme, BSI pour le questionnaire. Les textes du Journal officiel du
    CRA et de NIS 2 sont réutilisables ; ceux-ci ne le sont pas, et déclarer
    la même licence pour les quatre autoriserait la copie de deux d'entre
    eux."""
    assert iso.SOURCE["reproduction"] is False
    assert "DROIT D'AUTEUR" in iso.SOURCE["licence"].upper()
    assert "2011/833" not in iso.SOURCE["licence"]
    assert iso.SOURCE_QUESTIONNAIRE["reproduction"] is False
    assert "BSI" in iso.SOURCE_QUESTIONNAIRE["editeur"]
    assert "question" in iso.SOURCE_QUESTIONNAIRE["licence"].lower()


def test_aucun_titre_de_mesure_ne_contient_une_phrase_d_exigence():
    """LE TÉMOIN DE BON SENS À CÔTÉ DE LA RÈGLE DE CHAMPS. Un titre d'annexe A
    est un syntagme nominal. S'il se mettait à contenir « doit » ou
    « l'organisme », c'est que du texte normatif a coulé dans la colonne des
    titres — ce qu'une règle sur les noms de champs ne voit pas."""
    for num, m in iso.MESURES.items():
        t = m["titre"]
        assert len(t) < 110, (
            "le titre de %s fait %d caractères : %r" % (num, len(t), t))
        assert " doit " not in (" " + t.lower() + " "), (
            "le titre de %s contient une formulation d'exigence : %r" % (num, t))
        assert "organisme" not in t.lower(), (
            "le titre de %s nomme l'organisme : %r" % (num, t))


def test_la_route_du_referentiel_ne_publie_que_numero_titre_et_millesime():
    """LA MÊME DISCIPLINE, MESURÉE SUR LA SORTIE HTTP. La table peut être
    propre et la route ajouter un champ en la sérialisant : c'est la réponse
    JSON qui est publiée, pas la table."""
    src = _source("app.py")
    d = src.index("def api_iso27001_referentiel")
    f = src.index("@app.route", d)
    bloc = src[d:f]
    m = re.search(r'"mesures": \[\{(.*?)\}\s*\n?\s*for mn, mt in liste\]',
                  bloc, re.S)
    assert m, "la route ne sérialise plus les mesures comme attendu"
    champs = set(re.findall(r'"(\w+)":', m.group(1)))
    assert champs == {"numero", "titre", "nouvelle_2022"}, (
        "la route publie %s pour chaque mesure : seuls le numéro, le titre et "
        "le millésime d'apparition sont citables" % sorted(champs))


def test_les_ecrans_portent_la_reserve_de_droit_d_auteur_visible():
    """PAS EN NOTE DE BAS DE PAGE. Un lecteur qui cherche le texte de la
    norme et ne le trouve pas doit comprendre POURQUOI dès le haut de
    l'écran, sinon il croit à une restitution incomplète."""
    html = _source("sentinel.html")
    for pid in ("p-iso27001", "p-iso27001-risques", "p-iso27001-soa"):
        d = html.index('id="%s"' % pid)
        f = html.index('<div class="page" id=', d + 10)
        bloc = html[d:f]
        assert "cnf-copy" in bloc, (
            "le panneau %s ne porte pas la réserve de droit d'auteur" % pid)
        assert "ISO/IEC" in bloc


def test_aucune_question_du_questionnaire_BSI_n_est_recopiee():
    """CE QUE CETTE RÈGLE MESURE VRAIMENT. Les questions de BSI ont une
    signature reconnaissable — « Avez-vous », « L'organisation a-t-elle »,
    « Êtes-vous » suivis d'un point d'interrogation. Le module pose ses
    propres questions ; s'il se mettait à interroger dans cette forme-là,
    c'est qu'on aurait recopié."""
    src = _source("iso27001.py")
    formes = re.findall(
        r"(Avez-vous|Êtes-vous|La direction s'est-elle|"
        r"L'organisation a-t-elle|Un processus[^.]{0,60}a-t-il)", src)
    assert not formes, (
        "le module emploie des tournures interrogatives du questionnaire "
        "BSI — ses questions sont sa propriété : %s" % formes[:5])


# ═══════════════════════════════════════════════════════════════════════════
#  7. LA STRUCTURE DE LA NORME
# ═══════════════════════════════════════════════════════════════════════════

def test_l_annexe_A_2022_compte_93_mesures_en_quatre_themes():
    assert len(iso.ANNEXE_A) == 4
    assert len(iso.MESURES) == 93
    compte = {t: len(l) for t, _tt, _td, l in iso.ANNEXE_A}
    assert compte == {"A.5": 37, "A.6": 8, "A.7": 14, "A.8": 34}


def test_les_mesures_se_trient_numeriquement_et_non_alphabetiquement():
    """« A.8.10 » PASSE AVANT « A.8.9 » EN TRI TEXTE, et « A.5 » après
    « A.10 ». La restitution afficherait un ordre qui ne correspond à rien
    dans la norme."""
    tries = sorted(iso.MESURES, key=iso._ordre)
    assert tries[0] == "A.5.1" and tries[-1] == "A.8.34"
    assert tries.index("A.8.9") < tries.index("A.8.10")
    assert tries.index("A.5.37") < tries.index("A.6.1")


def test_l_article_6_3_ajoute_par_la_version_2022_est_present():
    """LE SEUL ARTICLE NEUF DU CORPS DE LA NORME. Sans lui, la table serait
    celle de 2013 déguisée."""
    assert "6.3" in iso.SOUS_CHAPITRES
    assert "modification" in iso.SOUS_CHAPITRES["6.3"]["titre"].lower()


def test_un_article_declare_sans_objet_est_REFUSE():
    """MÊME RÈGLE QUE POUR 42001 : les mesures de l'annexe A s'écartent, les
    articles 4 à 10 non. « 9.2 Audit interne : sans objet » n'écarte pas une
    mesure, ça renonce à la certification."""
    m = iso.maturite({"9.2.1": "sans_objet", "4.1": "conforme"})
    assert "9.2.1" in m["refus_sans_objet"]
    assert m["dit_refus"]
    ligne = [l for c in m["chapitres"] for l in c["lignes"]
             if l["numero"] == "9.2.1"][0]
    assert ligne["etat"] == "non_renseigne"
    sans = iso.maturite({"4.1": "conforme"})
    assert sans["refus_sans_objet"] == [] and sans["dit_refus"] is None


def test_les_deux_taux_divergent_pour_un_organisme_deja_certifie_ailleurs():
    """LE SECOND TAUX EST LE SEUL UTILE À QUI PORTE DÉJÀ UN AUTRE SYSTÈME DE
    MANAGEMENT : sept articles ne se reprennent de nulle part."""
    art = {n: "conforme" for n, v in iso.SOUS_CHAPITRES.items()
           if v["mutualisable"]}
    m = iso.maturite(art)
    assert m["taux"] > 60
    assert m["propres_a_la_securite"]["taux"] == 0
    assert m["propres_a_la_securite"]["total"] == 7


# ═══════════════════════════════════════════════════════════════════════════
#  8. L'ORDRE DE L'ÉVALUATION — RISQUE, PUIS DOCUMENTS
# ═══════════════════════════════════════════════════════════════════════════

def test_le_perimetre_absent_arrete_avant_tout_le_reste():
    """L'ARTICLE 4.3 EST LA PREMIÈRE DÉCISION DE LA CERTIFICATION, et tout ce
    qui n'en est pas exclu par écrit sera audité."""
    r = iso.evaluer({"nom": "ACME"})
    assert r["etape"] == "perimetre_absent"


def test_une_analyse_de_risque_bloquee_arrete_avant_la_declaration():
    """L'ORDRE EST CELUI DE LA NORME. Les mesures se DÉDUISENT du traitement
    des risques : servir un verdict de déclaration d'applicabilité à un
    organisme dont l'analyse ne tient pas l'encourage à construire le
    document d'abord — exactement l'inverse de ce que l'article 6.1.3
    demande."""
    r = iso.evaluer({
        "nom": "ACME", "perimetre": "DSI, site de Lyon",
        "criteres": _criteres("2026-05-01", "2026-04-01"),
        "risques": [_risque(option="modifier")],
        "mesures": _toutes("retenue", "motif", "mise_en_oeuvre")})
    assert r["etape"] == "risque_bloque"
    assert r["applicabilite"]["recevable"] is True, (
        "la déclaration est bonne — c'est bien le risque qui arrête, et le "
        "verdict doit le dire")


def test_le_chemin_complet_mene_a_pret():
    """LE TÉMOIN QUI INTERDIT DE RENDRE TOUJOURS « BLOQUÉ »."""
    r = iso.evaluer({
        "nom": "ACME", "perimetre": "DSI, site de Lyon",
        "criteres": _criteres(),
        "risques": [_risque(option="modifier", mesures_mises_en_oeuvre=True,
                            residuel_vraisemblance=1, residuel_consequence=2)],
        "mesures": _toutes("retenue", "motif", "mise_en_oeuvre"),
        "articles": {n: "conforme" for n in iso.SOUS_CHAPITRES}})
    assert r["etape"] == "pret", r["dit"]


def test_le_moteur_refuse_une_evaluation_sans_nom():
    r = iso.evaluer({"perimetre": "x"})
    assert r["ok"] is False and r["motif"] == "nom_manquant"


# ═══════════════════════════════════════════════════════════════════════════
#  9. LES PONTS — ET CELUI QUI SE MESURE DES DEUX CÔTÉS
# ═══════════════════════════════════════════════════════════════════════════

def test_les_deux_normes_s_accordent_sur_ce_qui_se_greffe():
    """LE PONT CESSE D'ÊTRE UNE PROMESSE. iso42001 annonce quels de ses
    articles se greffent sur un système existant ; iso27001 en dit autant.
    Si l'une déclarait « mutualisable » un article que l'autre tient pour
    propre, le pont mentirait à l'une des deux audiences — et personne ne
    s'en apercevrait, puisque chaque module est cohérent tout seul."""
    import iso42001 as ia
    communs = set(ia.SOUS_CHAPITRES) & set(iso.SOUS_CHAPITRES)
    assert len(communs) >= 25, (
        "les deux normes partagent la structure harmonisée : %d articles "
        "communs seulement" % len(communs))
    desaccords = [n for n in sorted(communs)
                  if ia.SOUS_CHAPITRES[n]["mutualisable"]
                  != iso.SOUS_CHAPITRES[n]["mutualisable"]]
    assert not desaccords, (
        "ces articles sont déclarés greffables d'un côté et propres de "
        "l'autre : %s" % desaccords)
    # ET LES DEUX SEULS ARTICLES QUE 42001 AJOUTE SONT CEUX DE L'ÉVALUATION
    # D'IMPACT — le fait qui distingue vraiment les deux normes.
    ajoutes = sorted(set(ia.SOUS_CHAPITRES) - set(iso.SOUS_CHAPITRES))
    assert ajoutes == ["6.1.4", "8.4"], (
        "42001 ajoute au corps de la norme l'évaluation d'impact du système "
        "d'IA, et rien d'autre : %s" % ajoutes)


def test_chaque_pont_dit_ce_qu_il_NE_remplace_PAS():
    for p in iso.PONTS:
        assert p["ne_remplace_pas"].strip(), (
            "le pont vers %s ne dit pas ce qu'il ne remplace pas" % p["cle"])
        assert p["reutilise"].strip()
        for n in p["mesures_iso"]:
            assert n in iso.MESURES, (
                "le pont %s cite une mesure inconnue : %s" % (p["cle"], n))


def test_le_pont_vers_NIS2_couvre_les_dix_mesures_et_nomme_les_trois_angles_morts():
    """LE PONT LE PLUS DEMANDÉ ET LE PLUS MAL COMPRIS. Il est réel et large ;
    et trois choses lui échappent complètement — les délais de l'article 23,
    la responsabilité personnelle de l'article 20, l'enregistrement de
    l'article 3, §4. Un pont qui ne dirait que ce qui se réutilise ferait
    croire qu'un certificat vaut conformité à une directive."""
    p = [x for x in iso.PONTS if x["cle"] == "nis2"][0]
    cles = [c for c, _n, _ms in iso.NIS2_VERS_ANNEXE_A]
    assert cles == list("abcdefghij"), (
        "le rapprochement doit couvrir les dix mesures de l'article 21, §2 : "
        "%s" % cles)
    for c, nom, ms in iso.NIS2_VERS_ANNEXE_A:
        assert ms, "la mesure %s) ne renvoie à aucune mesure de l'annexe A" % c
        for m in ms:
            assert m in iso.MESURES, "mesure inconnue : %s" % m
    # LES ARTICLES SONT CHERCHÉS AVEC LEUR PRÉFIXE, pas comme des nombres
    # nus : « 20 » se trouve dans « 2024 », et la règle passerait alors sur
    # un texte qui ne nomme aucun article.
    for article in ("art. 23", "art. 20", "art. 3"):
        assert article in p["ne_remplace_pas"], (
            "le pont vers NIS 2 doit nommer l'%s parmi ce qu'il ne couvre "
            "pas — « ça ne couvre pas les délais » se discute, « ça ne "
            "couvre pas l'article 23 » se vérifie" % article)


def test_le_rapprochement_NIS2_se_declare_comme_une_LECTURE_et_non_une_norme():
    """UNE CORRESPONDANCE PRÉSENTÉE COMME OFFICIELLE SE CITE DEVANT UNE
    AUTORITÉ. Celle-ci est l'analyse du cabinet, et le module doit le dire."""
    src = _source("iso27001.py")
    d = src.index("NIS2_VERS_ANNEXE_A = (")
    entete = src[max(0, d - 1400):d]
    assert "LECTURE DU CABINET" in entete.upper(), (
        "le rapprochement NIS 2 ne se déclare pas comme la lecture du "
        "cabinet — il se citerait comme une correspondance officielle")


# ═══════════════════════════════════════════════════════════════════════════
#  10. CE QUE LE MODULE NE SAIT PAS, ET LE DIT
# ═══════════════════════════════════════════════════════════════════════════

def test_le_module_declare_ce_qu_il_n_a_PAS_pu_verifier():
    """LA DISCIPLINE QUI VAUT MIEUX QU'UNE DATE INVENTÉE. La fin de la
    période de transition des certificats 2013 n'a pas pu être vérifiée
    depuis cet environnement — iso.org, iaf.nu et cofrac.fr y sont
    injoignables. La taire rendrait une restitution qui a l'air complète ;
    la rendre comme établie ferait citer en comité un chiffre que personne
    n'a vérifié."""
    assert len(iso.A_VERIFIER) >= 2, (
        "le module ne déclare plus ses angles morts : %d" % len(iso.A_VERIFIER))
    for x in iso.A_VERIFIER:
        assert x["quoi"].strip() and x["ou"].strip() and x["pourquoi"].strip()
    # L'ANGLE MORT PRINCIPAL EST NOMMÉ, pas seulement compté : c'est la fin
    # de la période de transition, et c'est elle qu'on cherchera.
    assert any("transition" in x["quoi"].lower() for x in iso.A_VERIFIER), (
        "la fin de la période de transition n'est plus déclarée comme non "
        "vérifiée — quelqu'un la citera comme si elle l'était")
    transition = iso.CERTIFICATION["transition"]
    assert transition["reserve"], "la transition a perdu sa réserve"
    assert "vérifi" in transition["reserve"].lower()
    # ET AUCUNE DATE N'EST AVANCÉE POUR CETTE TRANSITION.
    assert not re.search(r"\b20\d\d-\d\d-\d\d\b", transition["quoi"] + transition["reserve"]), (
        "une date de fin de transition est avancée alors qu'elle n'a pas pu "
        "être vérifiée")


def test_la_garde_du_module_est_passee_au_chargement():
    assert iso._FAUTES == []


def test_les_quatre_options_de_traitement_sont_nommees():
    """MODIFIER, PARTAGER, ÉVITER, MAINTENIR. « Partager » porte la réserve
    qui compte : l'assurance déplace la charge financière, pas la
    responsabilité."""
    assert len(iso.OPTIONS_TRAITEMENT) == 4
    assert set(iso.OPTIONS_TRAITEMENT) == {"modifier", "partager", "eviter",
                                           "maintenir"}
    assert "responsabilité" in iso.OPTIONS_TRAITEMENT["partager"]["dit"]


def test_les_echelles_sont_declarees_comme_celles_du_CABINET():
    """LA NORME N'IMPOSE AUCUNE ÉCHELLE. Présenter celle du cabinet comme
    normative serait un faux — et le client la défendrait devant un auditeur
    comme si elle l'était."""
    src = _source("iso27001.py")
    d = src.index("ECHELLES = {")
    entete = src[max(0, d - 900):d]
    assert "AUCUNE échelle" in entete or "AUCUNE ÉCHELLE" in entete.upper(), (
        "le module ne dit plus que la norme n'impose aucune échelle")
    for cle, ech in iso.ECHELLES.items():
        assert [r for r, _n, _d in ech] == [1, 2, 3, 4]
        for _r, nom, dit in ech:
            assert nom.strip() and len(dit.strip()) > 20, (
                "l'échelle %s a un échelon sans description utilisable" % cle)
