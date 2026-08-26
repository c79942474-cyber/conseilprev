"""LES FLUX DE PRESSE — un article n'est pas un fait, et le site doit le dire.

CE QUI CHANGE AVEC CES QUINZE SOURCES. Les dix premières du registre livrent
des FAITS : un identifiant de vulnérabilité, une part de production
électrique, une technique répertoriée. Un flux de presse livre autre chose —
le compte rendu qu'un tiers donne d'un fait, que ce site n'a pas vérifié. La
tentation est de les servir pareil, parce qu'ils s'affichent pareil ; c'est
exactement ce que ces contrôles empêchent.

SIX RÈGLES QU'ILS GARDENT

  1. AUCUNE FICHE DE PRESSE N'EST « VÉRIFIÉE À LA SOURCE PRIMAIRE », pas même
     celle d'une autorité. Lire un flux, c'est lire un avis de publication :
     un titre, une date, une adresse. Le document n'a pas été ouvert.
  2. SANS DATE, ON NE RETIENT PAS. La revue hebdomadaire est bâtie sur les
     dates ; une fiche datée du jour de la collecte ferait passer un article
     de l'an dernier pour l'actualité de la semaine.
  3. UN FLUX MUET N'EST PAS UN FLUX INJOIGNABLE. Les additionner ferait
     passer une panne de réseau pour une semaine sans actualité.
  4. LE SUJET SE DÉCIDE PAR UN MOT ÉCRIT, et la fiche dit lequel. Un
     classement dont on ne peut pas donner la raison ne se conteste pas, et
     ce qui ne se conteste pas cesse d'être vérifié.
  5. ON NE RECONNAÎT LES ORGANISATIONS QUE DANS LE TEXTE DE L'ÉDITEUR, jamais
     dans le nôtre — la règle vaut ici comme ailleurs, et le nom des champs
     lus doit permettre de le constater.
  6. AUCUNE DE CES QUINZE SOURCES NE PORTE « VÉRIFIÉE ». Aucune n'a pu être
     atteinte depuis l'environnement de conception : la politique réseau y
     refuse les vingt adresses, sans exception. Écrire une date de
     vérification qu'on n'a pas faite serait un mensonge à l'endroit exact où
     ce site promet de dire vrai.
"""
import os
import re
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import ingestion as I  # noqa: E402
import organisations as ORG  # noqa: E402
import revue as R  # noqa: E402
import sources as SRC  # noqa: E402
import veille as V  # noqa: E402


RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Flux</title>
<item><title>Sanction de 12 millions d&#39;euros pour un syst&#232;me d&#39;IA contraire au RGPD</title>
<link>https://www.cnil.fr/fr/sanction</link>
<description>&lt;p&gt;La formation restreinte a &lt;b&gt;prononc&#233;&lt;/b&gt; une amende.&lt;/p&gt;</description>
<pubDate>Tue, 19 Aug 2026 08:30:00 +0200</pubDate></item>
</channel></rss>"""

ATOM = b"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"><title>Flux</title>
<entry><title>Siemens patches a SCADA vulnerability exploited in the wild</title>
<link rel="alternate" href="https://arstechnica.com/ai/siemens"/>
<summary>Schneider Electric and Siemens both shipped fixes.</summary>
<updated>2026-08-21T14:02:00Z</updated></entry></feed>"""


def _art(**kw):
    base = {"title": "Une vulnérabilité SCADA exploitée sur un automate",
            "link": "https://www.cert.ssi.gouv.fr/avis/1",
            "summary": "L'éditeur publie un correctif.",
            "date": "2026-08-19"}
    base.update(kw)
    return base


def _sources_presse():
    return {c for c, s in SRC.SOURCES.items() if s.get("presse")}


# ═══════════════════════════════════════════════════════════════════════════
#  1. UN ARTICLE N'EST PAS UN FAIT
# ═══════════════════════════════════════════════════════════════════════════

def test_LE_POINT_QUI_DECIDE_aucune_fiche_de_presse_n_est_verifiee_a_la_source():
    """Le statut primaire dit « le fait a été confronté au document
    d'origine ». Lire un flux, c'est lire un avis de publication — le
    document n'a pas été ouvert.

    LE CONTRÔLE PORTE SUR LES QUINZE SOURCES, autorités comprises. C'est le
    cas de l'autorité qui compte : la tentation de se réclamer du primaire
    parce que c'est la CNIL qui parle est précisément celle qui confondrait
    le canal et l'acte."""
    art = {c: [_art()] for c in _sources_presse()}
    r = I.collecter_presse(articles=art)
    assert r["fiches"], "le contrôle ne prouve rien : aucune fiche produite"
    for f in r["fiches"]:
        assert f["statut"] == "source_secondaire", (
            "%s (%s) se réclame du statut %s"
            % (f["source_cle"], f["source"]["nature_nom"], f["statut"]))
    # Et une autorité a bien été traversée, sans quoi le cas qui compte n'a
    # pas été éprouvé.
    natures = {f["source"]["nature"] for f in r["fiches"]}
    assert "autorite_publique" in natures


def test_la_fiche_dit_que_le_contenu_n_a_pas_ete_verifie():
    """La réserve doit voyager AVEC la fiche : servie ailleurs, elle resterait
    sur la page pendant que le titre, lui, partirait en revue de presse."""
    f = I.collecter_presse(articles={"cnil": [_art()]})["fiches"][0]
    assert "n'a pas vérifié" in f["portee"] or "n'a pas vérifié" in f["incertitude"]
    assert "publication, pas son" in f["incertitude"]


def test_la_lecture_distingue_une_autorite_d_un_editeur():
    """Ce qu'une fiche gagne à venir d'une autorité est écrit dans sa lecture,
    et c'est tout ce qu'elle y gagne."""
    a = I.collecter_presse(articles={"cnil": [_art()]})["fiches"][0]
    e = I.collecter_presse(articles={"techcrunch_ia": [_art(
        title="A new language model claims better reasoning",
        link="https://techcrunch.com/x")]})["fiches"][0]
    assert "autorité publique" in a["lecture"]
    assert "article de presse, pas un acte" in e["lecture"]
    assert a["lecture"] != e["lecture"]


def test_la_lecture_est_derivee_par_regles_jamais_redigee():
    """La promesse du site : deux collectes sur la même donnée rendent le
    même texte, mot pour mot."""
    a = I.collecter_presse(articles={"cnil": [_art()]})["fiches"][0]
    b = I.collecter_presse(articles={"cnil": [_art()]})["fiches"][0]
    assert a["lecture"] == b["lecture"]
    assert a["lecture_nature"] == "regle"


# ═══════════════════════════════════════════════════════════════════════════
#  2. SANS DATE, ON NE RETIENT PAS
# ═══════════════════════════════════════════════════════════════════════════

def test_LE_POINT_QUI_DECIDE_un_article_sans_date_est_ecarte():
    """La revue hebdomadaire est bâtie sur les dates. Une fiche datée du jour
    de la collecte ferait passer un article de l'an dernier pour l'actualité
    de la semaine — et personne ne le verrait, puisque la date paraîtrait
    normale."""
    r = I.collecter_presse(articles={"cnil": [_art(date=None)]})
    assert r["fiches"] == []
    # LE MOTIF, PAS SEULEMENT LE COMPTE. Le contrôle de fiche rattrape aussi
    # l'absence de date ; sans le motif, retirer la garde d'entrée ne
    # changeait rien d'observable, et deux filets dont on ne sait pas lequel
    # a retenu ne se maintiennent pas.
    assert r["ecartees_par_motif"]["sans_date"] == 1
    assert r["ecartees_par_motif"]["refusee_au_controle"] == 0, (
        "l'article est passé la garde d'entrée et n'a été arrêté qu'au "
        "contrôle de fiche : la garde ne sert plus")


def test_une_date_de_format_inconnu_ne_devient_pas_une_date_fausse():
    """Deviner un format inconnu produirait une date plausible et fausse. Le
    croisement rapproche les fiches PAR LES DATES : une date inventée y
    fabriquerait un rapprochement qui n'existe pas."""
    assert I._date_flux("le 19 août 2026") is None
    assert I._date_flux("19/08/2026") is None
    assert I._date_flux("") is None
    assert I._date_flux(None) is None
    # Les deux formats que les flux emploient réellement, eux, sont lus.
    assert I._date_flux("Tue, 19 Aug 2026 08:30:00 +0200") == "2026-08-19"
    assert I._date_flux("2026-08-21T14:02:00Z") == "2026-08-21"


def test_un_article_sans_adresse_chiffree_est_ecarte():
    for lien in ("", "http://exemple.fr/a", "javascript:alert(1)"):
        r = I.collecter_presse(articles={"cnil": [_art(link=lien)]})
        assert r["fiches"] == [], lien
        assert r["ecartees_par_motif"]["sans_adresse"] == 1, lien
        assert r["ecartees_par_motif"]["refusee_au_controle"] == 0, lien


def test_chaque_ecart_dit_son_motif():
    """« 40 articles écartés » n'apprend rien : quarante hors sujet sur un
    flux généraliste est normal, quarante sans date est une panne de
    l'éditeur, et quarante refusés au contrôle de fiche est une régression de
    ce site. Les trois demandent des gestes différents."""
    A = {"cnil": [
        _art(title="Sanction pour un système contraire au RGPD"),
        _art(title="Sans date", date=None),
        _art(title="Adresse en clair", link="http://www.cnil.fr/y"),
        _art(title="La CNIL recrute un juriste")]}
    r = I.collecter_presse(articles=A)
    m = r["ecartees_par_motif"]
    assert m["sans_date"] == 1 and m["sans_adresse"] == 1 and m["annonce"] == 1
    assert r["ecartees"] == sum(m.values()) == 3
    # Le texte servi à l'exploitant nomme les motifs, pas seulement le total.
    assert "sans_date : 1" in r["dit"] and "annonce : 1" in r["dit"]


def test_le_dernier_filet_signale_une_regression_pas_un_defaut_d_editeur():
    """Arriver au contrôle de fiche signifie que les gardes d'entrée ont
    laissé passer quelque chose qu'elles auraient dû attraper. Le motif le dit
    séparément pour que l'exploitant sache où chercher."""
    r = I.collecter_presse(articles={"cnil": [_art(
        title="X", summary="RGPD")]})     # titre trop court pour le contrôle
    m = r["ecartees_par_motif"]
    assert "refusee_au_controle" in m


# ═══════════════════════════════════════════════════════════════════════════
#  3. MUET N'EST PAS INJOIGNABLE
# ═══════════════════════════════════════════════════════════════════════════

def test_LE_POINT_QUI_DECIDE_un_flux_muet_et_un_flux_injoignable_ne_se_confondent_pas():
    """Les additionner ferait passer une panne de réseau pour une semaine sans
    actualité — et l'exploitant chercherait un problème éditorial là où il y a
    un problème de réseau."""
    r = I.collecter_presse(articles={"cnil": [], "mit_tr": [_art(
        title="A language model benchmark", link="https://www.technologyreview.com/x")]})
    muets = {m["cle"] for m in r["muets"]}
    injoign = {x["cle"] for x in r["injoignables"]}
    assert "cnil" in muets, "un flux qui répond sans rien donner n'est pas muet"
    assert "cnil" not in injoign
    # Les treize non fournis sont injoignables, pas muets.
    assert len(injoign) == len(_sources_presse()) - 2
    assert not (muets & injoign), "un flux ne peut pas être les deux"


def test_LE_POINT_QUI_DECIDE_aucun_flux_atteint_est_un_echec_pas_une_semaine_calme():
    """Le journal de collecte lit `ok`. Rendre `True` avec quinze flux
    injoignables y écrirait « presse : 0 retenue » — une ligne qui se lit
    comme une actualité creuse, et l'exploitant chercherait un problème
    éditorial là où il y a une panne de réseau.

    C'est le cas RÉEL de cet environnement : la politique du tunnel refuse
    les quinze adresses, et le collecteur doit le dire plutôt que rendre une
    semaine vide."""
    r = I.collecter_presse(articles={})
    assert r["ok"] is False
    assert r["erreur"] == "tous_injoignables"
    assert "15" in r["message"]
    # UN SEUL FLUX QUI RÉPOND SUFFIT À REDEVENIR UN SUCCÈS, même s'il ne
    # donne rien : le réseau fonctionne, et c'est ce que `ok` dit.
    assert I.collecter_presse(articles={"cnil": []})["ok"] is True


def test_chaque_flux_injoignable_dit_pourquoi():
    r = I.collecter_presse(articles={"cnil": [_art()]})
    assert r["injoignables"]
    for x in r["injoignables"]:
        assert x["nom"] and x["pourquoi"], x


def test_un_flux_illisible_est_une_information_pas_une_exception():
    d = I.lire_flux(b"<ceci n'est pas du xml")
    assert d["ok"] is False and d["erreur"] == "xml_illisible"
    assert "XML" in d["message"]


# ═══════════════════════════════════════════════════════════════════════════
#  4. LE SUJET SE DÉCIDE PAR UN MOT ÉCRIT
# ═══════════════════════════════════════════════════════════════════════════

def test_LE_POINT_QUI_DECIDE_la_fiche_dit_le_mot_qui_l_a_classee():
    """Un classement dont on ne peut pas donner la raison ne se conteste pas,
    et ce qui ne se conteste pas cesse d'être vérifié."""
    f = I.collecter_presse(articles={"ars_technica_ia": [_art(
        title="Siemens patches a SCADA vulnerability",
        link="https://arstechnica.com/ai/x")]})["fiches"][0]
    assert f["sujet"] == "cyber_industriel"
    assert f["presse_mot"] == "scada"
    assert "scada" in f["lecture"]


def test_le_sujet_ne_se_devine_pas_quand_la_source_en_couvre_plusieurs():
    """Ranger au hasard entre deux rubriques est pire que ne pas ranger : le
    lecteur croit la rubrique complète."""
    multi = [c for c, s in SRC.SOURCES.items()
             if s.get("presse") and len(s["sujets"]) > 1]
    assert multi, "aucune source multi-sujets : le contrôle ne prouve rien"
    r = I.collecter_presse(articles={multi[0]: [_art(
        title="Un communiqué sans aucun mot reconnaissable",
        summary="Rien de saillant.", link="https://exemple.invalid/x")]})
    assert r["fiches"] == []
    assert r["ecartees"] == 1


def test_une_source_a_sujet_unique_retombe_sur_ce_qu_elle_declare():
    seul = [c for c, s in SRC.SOURCES.items()
            if s.get("presse") and len(s["sujets"]) == 1]
    assert seul
    cle = seul[0]
    r = I.collecter_presse(articles={cle: [_art(
        title="Un titre sans mot reconnaissable", summary="Rien.",
        link="https://exemple.invalid/x")]})
    assert len(r["fiches"]) == 1
    f = r["fiches"][0]
    assert f["sujet"] == SRC.SOURCES[cle]["sujets"][0]
    # Et la fiche ne prétend PAS avoir été classée par un mot.
    assert f["presse_mot"] is None


def test_les_quatre_sujets_du_site_sont_atteignables():
    """Une rubrique qu'aucun mot ne peut atteindre resterait vide sans que
    personne ne sache que c'est la table de mots qui est en cause."""
    assert set(I.MOTS_SUJET) == set(V.SUJETS)
    assert set(I.ORDRE_SUJET_PRESSE) == set(V.SUJETS)


def test_les_annonces_qui_ne_sont_pas_de_l_actualite_sont_ecartees():
    for titre in ("La CNIL recrute un juriste",
                  "Webinaire : la conformité en 30 minutes",
                  "Téléchargez notre livre blanc sur la sécurité SCADA"):
        r = I.collecter_presse(articles={"cnil": [_art(title=titre)]})
        assert r["fiches"] == [], titre


# ═══════════════════════════════════════════════════════════════════════════
#  5. LE FLUX SE LIT, DANS LES DEUX FORMATS
# ═══════════════════════════════════════════════════════════════════════════

def test_les_deux_formats_que_les_flux_emploient_sont_lus():
    """RSS et Atom : refuser l'un couperait un tiers des sources sans qu'un
    message ne le dise — le flux paraîtrait simplement vide."""
    a = I.lire_flux(RSS)
    assert a["ok"] and len(a["articles"]) == 1
    assert a["articles"][0]["date"] == "2026-08-19"
    assert a["articles"][0]["link"].startswith("https://")
    b = I.lire_flux(ATOM)
    assert b["ok"] and len(b["articles"]) == 1
    assert b["articles"][0]["date"] == "2026-08-21"
    assert b["articles"][0]["link"].startswith("https://")


def test_le_balisage_html_ne_traverse_pas_le_flux():
    """Les flux servent couramment du HTML dans le résumé. Le laisser passer
    mettrait des balises dans un chapeau, et un jour un script."""
    a = I.lire_flux(RSS)["articles"][0]
    assert "<" not in a["summary"] and ">" not in a["summary"]
    assert "prononcé une amende" in a["summary"]
    # Et les entités sont rendues, sans quoi le titre s'afficherait en code.
    assert "12 millions d'euros" in a["title"]


def test_les_cles_rendues_sont_celles_du_flux():
    """`title`, `summary`, `link` : ce sont les balises de l'éditeur. Un champ
    nommé « titre » se lirait comme un titre composé par le cabinet — ce
    qu'il est partout ailleurs sur ce site — et brouillerait la règle sur la
    reconnaissance des organisations."""
    for brut in (RSS, ATOM):
        a = I.lire_flux(brut)["articles"][0]
        assert set(a) == {"title", "summary", "link", "date"}


# ═══════════════════════════════════════════════════════════════════════════
#  6. LE REGISTRE NE MENT PAS SUR CES QUINZE SOURCES
# ═══════════════════════════════════════════════════════════════════════════

def test_LE_POINT_QUI_DECIDE_aucun_flux_ne_se_dit_verifie():
    """Aucune des vingt adresses n'a pu être atteinte depuis l'environnement
    de conception : la politique réseau les refuse toutes, au niveau du
    tunnel. Écrire une date de vérification qu'on n'a pas faite serait un
    mensonge à l'endroit exact où ce site promet de dire vrai — et il ne se
    verrait pas, puisqu'une date a l'air vraie."""
    for cle in _sources_presse():
        s = SRC.SOURCES[cle]
        assert not s.get("verifie_le"), (
            "%s se dit vérifiée alors qu'elle n'a jamais répondu ici" % cle)


def test_les_quinze_flux_sont_declares_lus_par_un_collecteur():
    """Le registre ne peut pas annoncer une source que plus personne ne lit :
    quinze entrées ajoutées sans collecteur auraient fait exactement cela."""
    lues = I.sources_collectees()
    assert _sources_presse() <= lues, sorted(_sources_presse() - lues)


def test_la_liste_des_flux_lus_se_derive_du_registre():
    """Une seconde liste écrite dans `ingestion.py` divergerait au premier
    ajout — et c'est toujours celle qu'on relit le moins qui reste fausse."""
    src = open(os.path.join(ICI, "ingestion.py"), encoding="utf-8").read()
    i = src.index("SOURCES_DU_COLLECTEUR")
    bloc = src[i:i + 400]
    assert "SRC.SOURCES.items()" in bloc, (
        "la liste des flux lus est écrite à la main au lieu d'être dérivée")
    # DISCRIMINATION : une seizième source de presse est lue sans qu'on
    # touche à `ingestion.py`.
    SRC.SOURCES["essai_presse"] = dict(
        SRC.SOURCES["cnil"], nom="Essai", url_donnee="https://exemple.invalid/f")
    try:
        assert "essai_presse" in I.sources_collectees()
    finally:
        del SRC.SOURCES["essai_presse"]


def test_LE_POINT_QUI_DECIDE_le_registre_ne_peut_pas_se_contredire_sur_une_source():
    """DÉFAUT RÉEL, commis en branchant ces flux. Le CERT-FR a été admis sous
    la clé `cert_fr_flux` alors qu'il figurait encore « à brancher » sous
    `cert_fr` : le registre disait en même temps « on ne sait pas l'atteindre »
    et « elle est admise ». Le contrôle par clé ne l'a pas vu — deux clés, un
    seul organisme. La comparaison porte maintenant sur l'hôte."""
    SRC.A_BRANCHER.append({
        "cle": "essai", "nom": "Essai", "pourquoi": "x", "obstacle": "y",
        "nature_obstacle": "environnement", "hote": "www.cnil.fr"})
    try:
        with pytest.raises(RuntimeError, match="se contredit"):
            SRC._verifier()
    finally:
        SRC.A_BRANCHER.pop()
    # Et il passe sur le registre réel, sans quoi il réussirait pour la
    # mauvaise raison.
    SRC._verifier()


def test_aucune_source_de_presse_ne_reste_a_brancher():
    """La contrepartie du contrôle précédent, sur les données : les entrées
    périmées de `A_BRANCHER` doivent avoir été retirées."""
    hotes = {SRC.SOURCES[c]["url_donnee"].split("//", 1)[-1].split("/", 1)[0].lower()
             for c in _sources_presse()}
    for a in SRC.A_BRANCHER:
        h = (a.get("hote") or "").lower()
        assert h not in hotes, "%s est à brancher et déjà servie" % a["cle"]


def test_un_agregateur_n_est_pas_admis_comme_source():
    """Une requête Google News rend de vrais articles, mais la source d'un
    article n'est pas le moteur qui l'a trouvé. L'admettre ferait entrer par
    une porte dérobée n'importe quel éditeur que la requête rapporte."""
    for cle, s in SRC.SOURCES.items():
        assert "news.google.com" not in s["url_donnee"], cle
    assert any(a["cle"].startswith("gnews") for a in SRC.A_BRANCHER), (
        "les flux d'agrégateur ont disparu au lieu d'être déclarés à brancher")


def test_les_deux_etiquettes_trompeuses_sont_corrigees():
    """`artificialintelligenceact.eu` et `dig.watch` sont repris de
    conseilprev, où ils figurent comme sources réglementaires de confiance. Le
    premier est édité par le Future of Life Institute, le second par la Geneva
    Internet Platform : deux organisations privées. Le nom de domaine du
    premier prête particulièrement à confusion — les classer « autorité »
    aurait recopié l'erreur en lui donnant l'apparence d'une vérification."""
    for cle in ("ai_act_eu", "digital_watch"):
        s = SRC.SOURCES[cle]
        assert s["nature"] == "publication_editeur", cle
    assert "PAS UNE SOURCE OFFICIELLE" in SRC.SOURCES["ai_act_eu"]["ne_couvre_pas"]


def test_chaque_flux_dit_ce_qu_il_ne_couvre_pas():
    """La règle du registre, appliquée aux quinze nouvelles : une source dont
    on ne dit que les forces finit citée hors de son périmètre."""
    for cle in _sources_presse():
        s = SRC.SOURCES[cle]
        assert len(s["ne_couvre_pas"]) >= 40, cle
        assert s["editeur"] and s["licence"] and s["cadence"]


# ═══════════════════════════════════════════════════════════════════════════
#  7. LA REVUE HEBDOMADAIRE LES REÇOIT
# ═══════════════════════════════════════════════════════════════════════════

def test_LE_POINT_QUI_DECIDE_la_revue_hebdomadaire_recoit_les_fiches_de_presse():
    """C'est l'objet du branchement : jusqu'ici la revue ne disposait que de
    fiches nées de catalogues, qui bougent au mois. Une revue de presse sans
    presse est un sommaire vide."""
    art = {"cnil": [_art(title="Sanction pour un système d'IA contraire au RGPD",
                         link="https://www.cnil.fr/fr/s", date="2026-08-19")],
           "ars_technica_ia": [_art(title="Siemens patches a SCADA flaw",
                                    summary="Schneider Electric shipped fixes.",
                                    link="https://arstechnica.com/ai/s",
                                    date="2026-08-21")]}
    fiches = I.collecter_presse(articles=art)["fiches"]
    assert len(fiches) == 2
    d = R.revue(fiches, genre="semaine", ancre="2026-08-21")
    assert d["ok"] and not d["corpus_vide"]
    dedans = sum(len(b.get("fiches", [])) for b in d["blocs"])
    assert dedans == 2, "la revue n'a pas repris les fiches de presse"


def test_la_revue_mensuelle_internationale_ecarte_ce_qui_n_a_pas_de_territoire():
    """Un article dont aucune organisation n'est reconnue n'a pas de pays. La
    revue internationale doit l'écarter EN LE DISANT, pas le ranger sous un
    drapeau choisi au hasard."""
    art = {"ars_technica_ia": [_art(title="Siemens patches a SCADA flaw",
                                    summary="Schneider Electric shipped fixes.",
                                    link="https://arstechnica.com/ai/s",
                                    date="2026-08-05")],
           "techcrunch_ia": [_art(title="A language model claims better reasoning",
                                  summary="No company named.",
                                  link="https://techcrunch.com/x",
                                  date="2026-08-06")]}
    fiches = I.collecter_presse(articles=art)["fiches"]
    d = R.revue(fiches, genre="mois", ancre="2026-08-15", international=True)
    dedans = sum(len(b.get("fiches", [])) for b in d["blocs"])
    assert dedans == 1
    assert d["ecartees_sans_territoire"] == 1


def test_les_organisations_viennent_du_texte_de_l_editeur():
    """La règle générale du site, sur ce collecteur : le pays d'une fiche
    doit venir de ce que la SOURCE nomme, jamais de ce que nous écrivons."""
    f = I.collecter_presse(articles={"ars_technica_ia": [_art(
        title="Siemens patches a SCADA flaw",
        summary="Schneider Electric shipped fixes.",
        link="https://arstechnica.com/ai/s")]})["fiches"][0]
    assert set(f["organisations"]) == {"siemens", "schneider"}
    assert set(f["pays"]) == {"DE", "FR"}
    # DISCRIMINATION : une organisation nommée seulement dans NOTRE texte ne
    # doit pas être reconnue. La lecture cite les organisations déjà trouvées
    # — elle ne peut donc pas en ajouter.
    src = open(os.path.join(ICI, "ingestion.py"), encoding="utf-8").read()
    i = src.index("def collecter_presse")
    corps = src[i:]
    assert "ORG.reconnaitre(a.get(\"title\")" in corps, (
        "la reconnaissance ne porte plus sur le texte du flux")
    assert re.search(r'ORG\.reconnaitre\([^)]*lecture', corps) is None
