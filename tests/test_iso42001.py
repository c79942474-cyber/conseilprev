# -*- coding: utf-8 -*-
"""ISO/IEC 42001 — LA DÉCLARATION QUI ARRÊTE L'AUDIT, ET LE DROIT D'AUTEUR.

CE QUI A DÉCLENCHÉ CE FICHIER. Une demande : « créer l'analyse de mise en
conformité ISO 42001 ». Deux choses pouvaient mal tourner, et une seule se
voit.

LA PREMIÈRE SE VOIT : un tableau de maturité à trente-deux lignes, un taux, et
un client qui prépare son audit sur un chiffre qui ne prédit rien. Parce que
l'audit d'étape 1 ne regarde pas un taux : il regarde LA DÉCLARATION
D'APPLICABILITÉ, et une mesure ni retenue ni écartée l'arrête là, avant que
quiconque ait vu ce que l'organisme fait vraiment.

    Trente-six mesures mises en œuvre, deux cases vides → l'audit s'arrête.
    Dix-huit retenues, vingt écartées, toutes motivées → l'audit passe.

LA SECONDE NE SE VOIT PAS, ET ELLE EST PIRE. ISO/IEC 42001:2023 est PROTÉGÉE
PAR LE DROIT D'AUTEUR — son propre en-tête interdit toute reproduction. Un
module qui « enrichirait » sa table avec le texte des exigences serait une
contrefaçon publiée sur une page servie à des clients. Rien ne lèverait : le
code marcherait, les écrans seraient plus complets, et le dépôt porterait un
passif. Une règle ci-dessous ferme cette porte en énumérant les champs
autorisés de la table des mesures — numéro et titre, rien d'autre.

CE QUE CES RÈGLES NE PEUVENT PAS FAIRE. Dire qu'un organisme obtiendra son
certificat : l'étape 2 s'audite sur des preuves d'exécution que Sentinel ne
détient pas. Elles disent seulement ce qui, à coup sûr, l'en empêche.
"""
import io
import os
import re

import pytest

import iso42001 as iso

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _source(nom):
    return io.open(os.path.join(_RACINE, nom), encoding="utf-8").read()


# ═══════════════════════════════════════════════════════════════════════════
#  1. LE DROIT D'AUTEUR — LA PORTE QU'ON FERME AVANT QU'ELLE S'OUVRE
# ═══════════════════════════════════════════════════════════════════════════

def test_la_table_des_mesures_ne_porte_QUE_des_numeros_et_des_titres():
    """LA RÈGLE QUI PROTÈGE LE DÉPÔT. Elle n'inspecte pas le contenu — une
    inspection de contenu se contourne en reformulant trois mots — elle
    énumère les CHAMPS AUTORISÉS. Ajouter un champ `exigence`, `texte` ou
    `mesure` pour « enrichir » la restitution fait tomber cette règle avant
    que la contrefaçon n'atteigne une page servie."""
    permises = {"objectif", "objectif_titre", "objectif_dit", "titre"}
    for num, m in iso.MESURES.items():
        en_trop = set(m) - permises
        assert not en_trop, (
            "la mesure %s porte un champ non prévu (%s) : la table ne doit "
            "contenir que des numéros et des titres, jamais le texte normatif"
            % (num, ", ".join(sorted(en_trop))))


def test_la_source_declare_la_norme_protegee_et_non_reutilisable():
    """LA DIFFÉRENCE AVEC LES TROIS AUTRES CADRES, ÉCRITE DANS LA SOURCE. CRA
    et NIS 2 sont des textes du Journal officiel, réutilisables au titre de la
    décision 2011/833/UE. 42001 ne l'est pas, et un module qui déclarerait la
    même licence pour les trois autoriserait la copie."""
    assert iso.SOURCE["reproduction"] is False
    assert "DROIT D'AUTEUR" in iso.SOURCE["licence"].upper()
    assert "2011/833" not in iso.SOURCE["licence"], (
        "la licence de réutilisation du JO ne s'applique PAS à une norme ISO")
    assert iso.SOURCE["achat"], (
        "le module doit dire que la norme s'achète : Sentinel ne la remplace "
        "pas")


def test_aucun_titre_de_mesure_ne_contient_une_phrase_d_exigence():
    """LE TÉMOIN DE BON SENS À CÔTÉ DE LA RÈGLE DE CHAMPS. Un titre d'annexe A
    est un SYNTAGME NOMINAL de quelques mots. Si l'un d'eux se mettait à
    contenir « doit » ou « l'organisme », c'est que du texte normatif a coulé
    dans la colonne des titres — ce qu'une règle sur les noms de champs ne
    voit pas."""
    for num, m in iso.MESURES.items():
        t = m["titre"]
        assert len(t) < 80, (
            "le titre de %s fait %d caractères : un titre d'annexe A est "
            "court, une exigence est longue — %r" % (num, len(t), t))
        assert " doit " not in (" " + t.lower() + " "), (
            "le titre de %s contient une formulation d'exigence : %r"
            % (num, t))
        assert "organisme" not in t.lower(), (
            "le titre de %s nomme l'organisme : c'est une phrase de norme, "
            "pas un titre — %r" % (num, t))


def test_les_ecrans_portent_la_reserve_de_droit_d_auteur_visible():
    """PAS EN NOTE DE BAS DE PAGE. Un lecteur qui cherche le texte de la norme
    et ne le trouve pas doit comprendre POURQUOI dès le haut de l'écran,
    sinon il croit à une restitution incomplète."""
    html = _source("sentinel.html")
    for pid in ("p-iso42001", "p-iso42001-soa", "p-iso42001-certif",
                "p-iso42001-ponts"):
        d = html.index('id="%s"' % pid)
        f = html.index('<div class="page" id=', d + 10)
        bloc = html[d:f]
        assert "cnf-copy" in bloc, (
            "le panneau %s ne porte pas la réserve de droit d'auteur" % pid)
        assert "ISO/IEC 2023" in bloc, (
            "le panneau %s ne nomme pas le titulaire des droits" % pid)


def test_la_route_du_referentiel_ne_renvoie_que_numeros_et_titres():
    """LA MÊME DISCIPLINE, MESURÉE SUR LA SORTIE HTTP. La table peut être
    propre et la route ajouter un champ en la sérialisant : c'est la réponse
    JSON qui est publiée, pas la table."""
    js = _source("app.py")
    d = js.index("def api_iso42001_referentiel")
    f = js.index("@app.route", d)
    bloc = js[d:f]
    m = re.search(r'"mesures": \[([^\]]*)\]', bloc)
    assert m, "la route ne sérialise plus les mesures comme attendu"
    champs = set(re.findall(r'"(\w+)":', m.group(1)))
    assert champs == {"numero", "titre"}, (
        "la route publie %s pour chaque mesure : seuls le numéro et le titre "
        "sont citables" % sorted(champs))


# ═══════════════════════════════════════════════════════════════════════════
#  2. LA DÉCLARATION D'APPLICABILITÉ — CE QUI ARRÊTE L'AUDIT
# ═══════════════════════════════════════════════════════════════════════════

def _toutes(decision, justification=None, mise_en_oeuvre=None):
    d = {}
    for n in iso.MESURES:
        e = {"decision": decision}
        if justification:
            e["justification"] = justification
        if mise_en_oeuvre:
            e["mise_en_oeuvre"] = mise_en_oeuvre
        d[n] = e
    return d


def test_trente_six_mises_en_oeuvre_et_deux_cases_vides_ne_passent_PAS():
    """LA DÉMONSTRATION CENTRALE DE CE FICHIER. Un taux de mise en œuvre de
    100 % ET une déclaration irrecevable, dans la même réponse. Le taux ne
    prédit rien ; le compteur « non décidées » décide."""
    d = _toutes("retenue", "issue de l'appréciation", "conforme")
    del d["A.7.5"]
    del d["A.9.3"]
    soa = iso.declaration_applicabilite(d)
    assert soa["taux_mise_en_oeuvre"] == 100, (
        "les trente-six retenues sont toutes mises en œuvre : %s"
        % soa["taux_mise_en_oeuvre"])
    assert soa["recevable"] is False, (
        "deux mesures ni retenues ni écartées arrêtent l'étape 1, quel que "
        "soit le taux")
    assert sorted(soa["non_decidees"]) == ["A.7.5", "A.9.3"]


def test_dix_huit_retenues_et_vingt_ecartees_motivees_passent():
    """L'AUTRE MOITIÉ DE LA DÉMONSTRATION, et sans elle la précédente
    passerait sur un moteur qui refuserait tout. Écarter est un DROIT."""
    ordre = sorted(iso.MESURES, key=iso._ordre)
    d = {}
    for i, n in enumerate(ordre):
        d[n] = ({"decision": "retenue", "justification": "risque retenu",
                 "mise_en_oeuvre": "conforme"} if i < 18 else
                {"decision": "ecartee", "justification": "aucun développement "
                                                         "interne"})
    soa = iso.declaration_applicabilite(d)
    assert soa["recevable"] is True, (
        "une déclaration entièrement tranchée et motivée est recevable : %s"
        % soa["bloquants"])
    assert (soa["retenues"], soa["ecartees"]) == (18, 20)


def test_ecarter_sans_justification_n_est_pas_recevable():
    """L'ARTICLE 6.1.3 f) EXIGE LA JUSTIFICATION DE L'EXCLUSION COMME DE
    L'INCLUSION. Un moteur qui n'exigerait le motif que pour les exclusions —
    ou que pour les inclusions — laisserait passer la moitié du défaut."""
    sans = iso.declaration_applicabilite(_toutes("ecartee"))
    assert sans["recevable"] is False
    assert len(sans["sans_justification"]) == len(iso.MESURES)
    avec = iso.declaration_applicabilite(_toutes("ecartee", "hors périmètre"))
    assert avec["recevable"] is True


def test_retenir_sans_justification_n_est_pas_recevable_non_plus():
    """LE SYMÉTRIQUE, et c'est celui qu'on oublie : retenir une mesure sans
    dire pourquoi est aussi un défaut de l'article 6.1.3 f)."""
    sans = iso.declaration_applicabilite(_toutes("retenue"))
    assert sans["recevable"] is False
    assert len(sans["sans_justification"]) == len(iso.MESURES)


def test_le_taux_de_mise_en_oeuvre_ne_porte_que_sur_les_mesures_RETENUES():
    """ÉCARTER UNE MESURE JUSTIFIÉE NE DOIT NI PÉNALISER NI FLATTER. Si les
    écartées entraient au dénominateur, écarter deviendrait coûteux et
    l'organisme retiendrait tout pour ne pas perdre de points — exactement
    l'inverse de ce que la norme demande."""
    d = _toutes("ecartee", "hors périmètre")
    for n in list(iso.MESURES)[:4]:
        d[n] = {"decision": "retenue", "justification": "retenue",
                "mise_en_oeuvre": "conforme"}
    soa = iso.declaration_applicabilite(d)
    assert soa["taux_mise_en_oeuvre"] == 100, (
        "quatre retenues toutes mises en œuvre = 100 %%, rendu %s"
        % soa["taux_mise_en_oeuvre"])


def test_sans_aucune_mesure_retenue_aucun_taux_n_est_rendu():
    """UN TAUX SUR ZÉRO DÉNOMINATEUR EST UN CHIFFRE INVENTÉ. `None` dit qu'il
    n'y a rien à mesurer ; 0 % dirait qu'on a échoué, et 100 % qu'on a
    réussi."""
    soa = iso.declaration_applicabilite(_toutes("ecartee", "hors périmètre"))
    assert soa["taux_mise_en_oeuvre"] is None


def test_le_bloquant_NOMME_les_mesures_en_cause():
    """UN VERDICT QUI DIT « NON RECEVABLE » SANS DIRE LESQUELLES fait relire
    trente-huit lignes. Le message porte les numéros."""
    d = _toutes("retenue", "motif")
    del d["A.10.4"]
    soa = iso.declaration_applicabilite(d)
    assert any("A.10.4" in b for b in soa["bloquants"]), (
        "le bloquant ne nomme pas la mesure en cause : %s" % soa["bloquants"])


def test_une_declaration_vide_compte_TOUTES_les_mesures_comme_non_decidees():
    vide = iso.declaration_applicabilite({})
    assert len(vide["non_decidees"]) == len(iso.MESURES) == 38
    assert vide["recevable"] is False


# ═══════════════════════════════════════════════════════════════════════════
#  3. LES ARTICLES 4 À 10 — DES EXIGENCES, ET ELLES NE S'ÉCARTENT PAS
# ═══════════════════════════════════════════════════════════════════════════

def test_un_article_declare_sans_objet_est_REFUSE_et_le_module_le_dit():
    """LA CONFUSION QUE CETTE RÈGLE EMPÊCHE. Les mesures de l'annexe A
    s'écartent ; les articles 4 à 10 sont des EXIGENCES. Un organisme qui
    déclarerait « 9.2 Audit interne : sans objet » n'a pas écarté une mesure,
    il a renoncé à la certification. Accepter silencieusement cette déclaration
    lui rendrait un taux flatteur sur un système non certifiable."""
    m = iso.maturite({"9.2.1": "sans_objet", "4.1": "conforme"})
    assert "9.2.1" in m["refus_sans_objet"]
    assert m["dit_refus"], "le refus doit être expliqué, pas silencieux"
    ligne = [l for c in m["chapitres"] for l in c["lignes"]
             if l["numero"] == "9.2.1"][0]
    assert ligne["etat"] == "non_renseigne", (
        "l'article refusé doit retomber sur « non renseigné », pas rester "
        "« sans objet » : %s" % ligne["etat"])


def test_sans_refus_le_module_ne_fabrique_pas_de_message():
    """LE TÉMOIN INVERSE : `dit_refus` vaut None quand rien n'a été refusé,
    sinon l'écran porterait un avertissement permanent que personne ne lit."""
    m = iso.maturite({"4.1": "conforme"})
    assert m["refus_sans_objet"] == []
    assert m["dit_refus"] is None


def test_les_deux_taux_divergent_pour_un_organisme_deja_certifie_27001():
    """LA MESURE QUI JUSTIFIE LE SECOND TAUX. Un organisme qui tient TOUS les
    articles mutualisables et AUCUN des articles propres à l'IA affiche un
    taux global rassurant et un taux d'effort réel à zéro. C'est le second qui
    dit où va le budget."""
    art = {n: "conforme" for n, v in iso.SOUS_CHAPITRES.items()
           if v["mutualisable"]}
    m = iso.maturite(art)
    assert m["taux"] > 60, (
        "le taux global doit être élevé : %d %%" % m["taux"])
    assert m["propres_a_l_ia"]["taux"] == 0, (
        "aucun article propre à l'IA n'est tenu : le second taux doit valoir "
        "0 %%, rendu %d %%" % m["propres_a_l_ia"]["taux"])
    assert m["taux"] != m["propres_a_l_ia"]["taux"], (
        "les deux taux ne mesurent pas la même chose et ne doivent pas "
        "coïncider dans ce cas")


def test_les_articles_propres_a_l_IA_sont_ceux_que_42001_ajoute():
    """LA LISTE EST CONTRÔLÉE DES DEUX CÔTÉS. Y mettre un article de la
    structure harmonisée gonflerait faussement l'effort ; en retirer la
    politique d'IA ou l'appréciation des risques le sous-estimerait."""
    propres = set(iso.PROPRES_A_L_IA)
    for n in ("5.2", "6.1.2", "6.1.3", "6.1.4", "8.2", "8.3", "8.4"):
        assert n in propres, (
            "l'article %s est ce que 42001 ajoute : il doit être propre à "
            "l'IA" % n)
    for n in ("9.2.1", "9.2.2", "9.3.1", "9.3.2", "9.3.3", "10.1", "10.2",
              "7.5.1", "7.5.2", "7.5.3"):
        assert n not in propres, (
            "l'article %s appartient à la structure harmonisée : il se greffe "
            "sur un système existant" % n)


def test_la_profondeur_de_decoupe_suit_la_norme_et_pas_une_commodite():
    """CE QU'UN TOTAL N'ATTRAPE PAS. La norme subdivise 6.1, 7.5, 9.2 et 9.3,
    et seulement ceux-là. Une table qui garderait « 6.1 » ET ses quatre
    enfants compterait cinq articles là où il y en a quatre ; une table qui
    inventerait « 8.4.1 » sans frère créerait un article qui n'existe pas.
    Les deux passent un total ajusté après coup."""
    profonds = {}
    for n in iso.SOUS_CHAPITRES:
        bouts = n.split(".")
        assert len(bouts) in (2, 3), "numérotation inattendue : %s" % n
        if len(bouts) == 3:
            profonds.setdefault(".".join(bouts[:2]), []).append(n)
    assert sorted(profonds) == ["6.1", "7.5", "9.2", "9.3"]
    for parent, enfants in profonds.items():
        assert parent not in iso.SOUS_CHAPITRES, (
            "« %s » est déclaré en plus de ses enfants : compté deux fois"
            % parent)
        assert len(enfants) >= 2, (
            "« %s » n'a qu'un enfant : un niveau de découpe inventé" % parent)


# ═══════════════════════════════════════════════════════════════════════════
#  4. L'ORDRE, LA CERTIFICATION, LES PONTS
# ═══════════════════════════════════════════════════════════════════════════

def test_les_mesures_se_trient_numeriquement_et_non_alphabetiquement():
    """« A.10 » PASSE AVANT « A.2 » EN TRI TEXTE. La restitution afficherait
    alors les relations avec les tiers entre les politiques et l'organisation
    interne — un ordre qui ne correspond à rien dans la norme."""
    tries = sorted(iso.MESURES, key=iso._ordre)
    assert tries[0] == "A.2.2" and tries[-1] == "A.10.4"
    assert tries.index("A.9.4") < tries.index("A.10.2"), (
        "A.9.4 doit précéder A.10.2 : %s" % tries[-6:])


def test_chaque_etape_de_certification_dit_ce_qui_la_fait_echouer():
    """UNE ÉTAPE DÉCRITE SANS SON MODE D'ÉCHEC NE PRÉPARE À RIEN."""
    assert len(iso.CERTIFICATION["etapes"]) == 3
    for e in iso.CERTIFICATION["etapes"]:
        assert e["ce_qui_fait_tomber"].strip(), (
            "l'étape %s ne dit pas ce qui la fait tomber" % e["cle"])
    etape1 = iso.CERTIFICATION["etapes"][0]
    assert "applicabilité" in etape1["ce_qui_fait_tomber"], (
        "l'étape 1 tombe sur la déclaration d'applicabilité : c'est le fait "
        "central de ce module")


def test_la_norme_est_declaree_certifiable_ce_que_les_trois_autres_ne_sont_pas():
    """CE QUI FAIT DE 42001 UN ACTIF ET PAS SEULEMENT UN COÛT : le certificat
    se montre à un client, à un acheteur public, à un assureur."""
    assert iso.SOURCE["certifiable"] is True
    assert "tiers" in iso.CERTIFICATION["nature"]


def test_chaque_pont_dit_ce_qu_il_NE_remplace_PAS():
    """LA CONFUSION LA PLUS COÛTEUSE DU DOMAINE. Les trois évaluations
    d'impact portent sur le même objet et ne sont pas la même. Un pont qui ne
    dirait que ce qui se réutilise ferait croire qu'un document en remplace
    un autre — et ça se découvre au contrôle."""
    for p in iso.PONTS:
        assert p["ne_remplace_pas"].strip(), (
            "le pont vers %s ne dit pas ce qu'il ne remplace pas" % p["cle"])
        assert p["reutilise"].strip()


def test_les_trois_evaluations_d_impact_passent_par_l_article_8_4():
    """LE POINT DE COUTURE EST NOMMÉ, et c'est ce qui rend le pont
    actionnable : on sait quel article ISO rouvrir."""
    for cle in ("ia_act", "rgpd"):
        p = [x for x in iso.PONTS if x["cle"] == cle][0]
        assert "8.4" in p["articles_iso"], (
            "le pont vers %s doit passer par l'article 8.4" % cle)
    ia = [x for x in iso.PONTS if x["cle"] == "ia_act"][0]
    assert "27" in ia["ne_remplace_pas"], (
        "le pont vers l'IA Act doit nommer l'article 27 — l'AIDF")
    rgpd = [x for x in iso.PONTS if x["cle"] == "rgpd"][0]
    assert "35" in rgpd["ne_remplace_pas"], (
        "le pont vers le RGPD doit nommer l'article 35 dans la phrase qu'on "
        "cite en réunion : « ça ne remplace pas » se conteste, « ça ne "
        "remplace pas l'article 35 » se vérifie")


def test_le_pont_vers_27001_ne_liste_que_des_articles_mutualisables():
    """SINON IL PROMETTRAIT UNE GREFFE SUR CE QUI NE SE GREFFE PAS, et
    l'organisme découvrirait l'écart à l'audit."""
    p = [x for x in iso.PONTS if x["cle"] == "iso27001"][0]
    for n in p["articles_iso"]:
        assert iso.SOUS_CHAPITRES[n]["mutualisable"], (
            "le pont vers 27001 annonce l'article %s comme greffable alors "
            "qu'il est propre à l'IA" % n)
    assert len(p["articles_iso"]) == len(iso.SOUS_CHAPITRES) - len(iso.PROPRES_A_L_IA)


# ═══════════════════════════════════════════════════════════════════════════
#  5. LE VERDICT D'ENSEMBLE — L'ORDRE DE L'AUDIT, PAS CELUI DU CONFORT
# ═══════════════════════════════════════════════════════════════════════════

def test_une_maturite_elevee_ne_rattrape_pas_une_declaration_irrecevable():
    """« PRESQUE PRÊT » EST LE MOT QUI COÛTE. Un organisme à 100 % de maturité
    dont la déclaration n'est pas tranchée est ARRÊTÉ, pas presque prêt."""
    art = {n: "conforme" for n in iso.SOUS_CHAPITRES}
    r = iso.evaluer({"nom": "ACME", "articles": art, "mesures": {}})
    assert r["maturite"]["taux"] == 100
    assert r["etape"] == "etape_1_bloquee"
    assert "aucun taux" in r["dit"].lower() or "Aucun taux" in r["dit"]


def test_une_declaration_recevable_et_des_articles_tenus_ouvrent_l_etape_2():
    """LE CHEMIN COMPLET, sans lequel la règle précédente passerait sur un
    moteur qui rendrait toujours « bloqué »."""
    art = {n: "conforme" for n in iso.SOUS_CHAPITRES}
    d = _toutes("retenue", "motif", "conforme")
    r = iso.evaluer({"nom": "ACME", "articles": art, "mesures": d})
    assert r["applicabilite"]["recevable"] is True
    assert r["etape"] == "pret"


def test_le_moteur_refuse_une_evaluation_sans_nom():
    r = iso.evaluer({"articles": {}})
    assert r["ok"] is False and r["motif"] == "nom_manquant"


def test_la_garde_du_module_est_passee_au_chargement():
    """`_FAUTES` EST LA PREUVE QUE `_verifier()` A COURU."""
    assert iso._FAUTES == []


def test_l_annexe_A_compte_neuf_objectifs_et_trente_huit_mesures():
    assert len(iso.ANNEXE_A) == 9
    assert len(iso.MESURES) == 38
    assert len(iso.SOUS_CHAPITRES) == 32
