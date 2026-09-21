# -*- coding: utf-8 -*-
"""
LA QUALIFICATION ASSISTÉE — CE QUI EST AUTOMATISÉ, ET CE QUI NE PEUT PAS L'ÊTRE.

LE DÉFAUT CHASSÉ ICI a un nom précis : une classification qui entrerait au
registre sans qu'une personne l'ait prononcée, et qui deviendrait ensuite
indiscernable de celles qu'une personne a prononcées. Le registre de
l'article 49 est une pièce opposable ; une valeur écrite par un programme
s'y lit exactement comme une décision.

L'ÉCRITURE DE RÉFÉRENCE DU SDK — `allowed_tools=["Read","Edit","Bash"]` —
ouvre précisément ce chemin : trois outils, et l'agent peut lire la base,
la réécrire, exécuter n'importe quoi. Les règles de ce fichier mesurent que
ce chemin n'existe pas ici, et qu'il ne peut pas être rouvert par
distraction.

CHAQUE RÈGLE MESURE UN FAIT, PAS UNE INTENTION. Là où une règle risquerait
de passer pour une raison sans rapport — parce que tout est refusé, parce
qu'un champ est absent —, elle porte son garde-fou : un cas jumeau qui,
lui, doit réussir.
"""

import io
import json
import os
import re
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

os.environ.setdefault('AUTH_MASTER_TOKEN', 'recette_locale_idf_0123456789abcdef')
os.environ.setdefault('FLASK_SECRET_KEY', 'recette-qualification')

import finops_ia                     # noqa: E402
import qualification_assistee as qa   # noqa: E402
import qualification_moteur as qm     # noqa: E402

SOURCE_APP = io.open(os.path.join(ICI, 'app.py'), encoding='utf-8').read()
SENTINEL_HTML = io.open(os.path.join(ICI, 'sentinel.html'), encoding='utf-8').read()
SENTINEL_JS = io.open(os.path.join(ICI, 'sentinel.page.js'), encoding='utf-8').read()
REQUIREMENTS = io.open(os.path.join(ICI, 'requirements.txt'), encoding='utf-8').read()


# ── LE SYSTÈME DE RÉFÉRENCE, ET SES VARIANTES ───────────────────────────

SYSTEME = {
    "id": 1,
    "nom": "Scoring credit automatise",
    "finalite": "Evaluer la solvabilite pour l'octroi de credit",
    "type_systeme": "Regression logistique / XGBoost",
    "donnees_utilisees": "Donnees identite, revenus, historique credit",
    "secteur": "Finance",
    "classification": "a_evaluer",
}

# Deux indices RECOPIÉS de la déclaration ci-dessus. C'est la seule forme
# que le moteur accepte, et ces essais s'y tiennent.
REPONSE_JUSTE = {
    "classe": "haut",
    "article": "annexe_iii",
    "motivation": "Acces a un service financier essentiel.",
    "indices": ["Evaluer la solvabilite pour l'octroi de credit",
                "historique credit"],
    "confiance": 0.9,
}


def _moteur(reponse, compteur=None):
    """Un moteur de recette : il rend ce qu'on lui dit, et compte ses appels."""
    texte = reponse if isinstance(reponse, str) else json.dumps(
        reponse, ensure_ascii=False)

    def repondre(prompt, systeme_prompt):
        if compteur is not None:
            compteur.append(prompt)
        return True, texte
    return repondre


def _proposition_juste(systeme=None):
    p = qa.proposer(systeme or SYSTEME, _moteur(REPONSE_JUSTE))
    assert p["classe_proposee"] == "haut", (
        "l'ancre de ce fichier ne tient plus : la réponse de référence ne "
        "produit plus de proposition (%s). Toutes les règles de refus "
        "passeraient alors pour une raison sans rapport." % p.get("motif"))
    return p


# ══════════════════════════════════════════════════════════════════════
# 1. CE QUI EST REFUSÉ AVANT MÊME D'APPELER UN MOTEUR
# ══════════════════════════════════════════════════════════════════════

def test_une_ligne_sans_finalite_ne_declenche_AUCUN_appel_de_moteur():
    """L'annexe III est une liste de FINALITÉS. Sans finalité écrite, il n'y
    a rien à lui comparer — et payer un appel pour l'apprendre serait deux
    fautes : la dépense, et la proposition meublée qui en sortirait."""
    appels = []
    maigre = {"id": 2, "nom": "Outil interne", "classification": "a_evaluer"}
    p = qa.proposer(maigre, _moteur(REPONSE_JUSTE, appels))

    assert appels == [], (
        "le moteur a été appelé %d fois sur une ligne irrecevable" % len(appels))
    assert p["motif"] == "champs_manquants", p["motif"]
    assert p["classe_proposee"] is None
    manquants = [m["champ"] for m in p["manquants"] if m["obligatoire"]]
    assert set(manquants) == {"finalite", "type_systeme", "donnees_utilisees"}, manquants

    # LE GARDE-FOU. Si la même mécanique refusait AUSSI la ligne complète,
    # la règle ci-dessus ne mesurerait que « ce module refuse tout ».
    appels_2 = []
    qa.proposer(SYSTEME, _moteur(REPONSE_JUSTE, appels_2))
    assert len(appels_2) == 1, (
        "une ligne complète n'atteint pas le moteur : le refus mesuré "
        "au-dessus n'est donc pas celui de la recevabilité")


def test_chaque_champ_manquant_dit_POURQUOI_il_bloque():
    """Une liste de cases vides ne dit pas ce qu'elle empêche. Le motif est
    ce qui permet de compléter la bonne ligne du registre."""
    r = qa.recevabilite({"nom": "x"})
    for m in r["manquants"]:
        assert len(m["pourquoi"]) > 30, (
            "le champ %s ne dit pas pourquoi il compte" % m["champ"])


# ══════════════════════════════════════════════════════════════════════
# 2. CE QUI EST VÉRIFIÉ DANS LA RÉPONSE DU MOTEUR
# ══════════════════════════════════════════════════════════════════════

def test_un_indice_PARAPHRASE_fait_tomber_la_proposition():
    """LE CONTRÔLE QUI COMPTE.

    Un extrait reformulé peut être juste ; il n'est pas VÉRIFIABLE. Et
    toute la proposition repose dessus. La reformulation ci-dessous dit la
    même chose que la déclaration — et c'est précisément le cas dangereux,
    parce qu'elle se lit comme une citation.
    """
    paraphrase = dict(REPONSE_JUSTE,
                      indices=["le systeme evalue le risque de defaut du client"])
    p = qa.proposer(SYSTEME, _moteur(paraphrase))
    assert p["motif"] == "indice_non_retrouve", p["motif"]
    assert p["classe_proposee"] is None
    assert p["a_completer"] is True

    # LE GARDE-FOU : la MÊME classe, le MÊME article, seuls les indices
    # changent. Sans lui, la règle passerait aussi si le module refusait
    # « haut » pour une raison sans rapport.
    juste = _proposition_juste()
    assert juste["article"] == paraphrase["article"]


def test_les_accents_et_la_casse_ne_font_PAS_tomber_une_vraie_citation():
    """L'autre moitié de la règle précédente. Un contrôle qui tomberait sur
    une apostrophe typographique refuserait des propositions justes, et on
    le désactiverait au bout d'une semaine."""
    sys_accents = dict(SYSTEME,
                       finalite="Évaluer la solvabilité pour l’octroi de crédit")
    rep = dict(REPONSE_JUSTE,
               indices=["evaluer la solvabilite pour l'octroi de credit"])
    p = qa.proposer(sys_accents, _moteur(rep))
    assert p["classe_proposee"] == "haut", p.get("motif")


def test_un_article_hors_de_la_liste_fermee_est_refuse():
    """« Article 6 bis » n'existe pas. La liste fermée est la seule défense
    qui tienne contre une référence inventée, parce qu'elle ne demande pas
    au lecteur de connaître le règlement."""
    p = qa.proposer(SYSTEME, _moteur(dict(REPONSE_JUSTE, article="art_6_bis")))
    assert p["motif"] == "article_inconnu", p["motif"]
    assert p["detail"] == "art_6_bis"


def test_un_article_qui_ne_SOUTIENT_pas_la_classe_est_refuse():
    """L'article 50 impose une transparence ; il ne fait pas un haut risque.
    Une proposition qui les associe est fausse même si les deux termes
    existent séparément."""
    p = qa.proposer(SYSTEME, _moteur(dict(REPONSE_JUSTE, article="art_50")))
    assert p["motif"] == "article_incompatible", p["motif"]

    # GARDE-FOU : l'article 50 est bien acceptable pour « limite ».
    ok = qa.proposer(SYSTEME, _moteur(dict(REPONSE_JUSTE, article="art_50",
                                           classe="limite")))
    assert ok["classe_proposee"] == "limite", ok.get("motif")


def test_a_evaluer_n_est_pas_une_classe_que_le_moteur_peut_PROPOSER():
    """Proposer « à évaluer » à un système déjà à évaluer ne dit rien, et
    remplirait la file d'attente de décisions sans objet."""
    p = qa.proposer(SYSTEME, _moteur(dict(REPONSE_JUSTE, classe="a_evaluer")))
    assert p["motif"] == "classe_non_proposable", p["motif"]
    assert "a_evaluer" not in qa.PROPOSABLES


def test_une_reponse_vide_ou_bavarde_ne_devient_JAMAIS_une_classe():
    for brut, attendu in ((" ", "reponse_vide"),
                          ("Je pense que c'est du haut risque.", "reponse_illisible"),
                          ("[]", "reponse_illisible")):
        p = qa.verifier(SYSTEME, brut)
        assert p["classe_proposee"] is None, brut
        assert p["motif"] == attendu, (brut, p["motif"])


def test_une_proposition_NON_MOTIVEE_est_refusee():
    """Une classe et un article sans une phrase qui les relie ne se
    contredit pas : elle ne s'examine pas. La personne qui décide n'aurait
    rien à lire avant de trancher."""
    p = qa.proposer(SYSTEME, _moteur(dict(REPONSE_JUSTE, motivation="")))
    assert p["motif"] == "motivation_absente", p["motif"]
    assert p["classe_proposee"] is None


def test_le_JSON_entoure_d_un_bloc_de_code_reste_lisible():
    """Un modèle qui enveloppe sa réponse dans ```json répond quand même.
    Refuser pour cette raison ferait payer un appel pour rien."""
    brut = "```json\n" + json.dumps(REPONSE_JUSTE, ensure_ascii=False) + "\n```"
    assert qa.verifier(SYSTEME, brut)["classe_proposee"] == "haut"


# ══════════════════════════════════════════════════════════════════════
# 3. LE CHIFFRE D'APPUI — CALCULÉ ICI, PAS DÉCLARÉ PAR LE MOTEUR
# ══════════════════════════════════════════════════════════════════════

def test_le_chiffre_d_appui_ne_vient_PAS_de_la_confiance_du_modele():
    """Un modèle à qui l'on demande sa confiance répond un nombre ; ce
    nombre n'est pas une mesure. Deux réponses identiques à la confiance
    près doivent donner le MÊME appui — sans quoi l'écran classerait les
    propositions par l'assurance du modèle."""
    sur = qa.proposer(SYSTEME, _moteur(dict(REPONSE_JUSTE, confiance=0.99)))
    hesitant = qa.proposer(SYSTEME, _moteur(dict(REPONSE_JUSTE, confiance=0.01)))
    assert sur["appui"] == hesitant["appui"], (sur["appui"], hesitant["appui"])
    # Elle est CONSERVÉE — la jeter effacerait une information —, mais elle
    # ne commande rien.
    assert sur["confiance_declaree"] == 0.99
    assert hesitant["confiance_declaree"] == 0.01


def test_l_appui_BAISSE_quand_la_declaration_porte_moins_de_champs():
    """L'autre moitié : si l'appui ne bougeait jamais, la règle précédente
    passerait pour une raison sans rapport — un nombre constant."""
    complet = _proposition_juste()
    sans_secteur = dict(SYSTEME)
    sans_secteur.pop("secteur")
    sans_secteur.pop("personnes_concernees", None)
    maigre = qa.proposer(sans_secteur, _moteur(REPONSE_JUSTE))
    assert maigre["classe_proposee"] == "haut", maigre.get("motif")
    assert maigre["appui"] < complet["appui"], (maigre["appui"], complet["appui"])


# ══════════════════════════════════════════════════════════════════════
# 4. LA PORTE VERS LE REGISTRE
# ══════════════════════════════════════════════════════════════════════

def test_valider_SANS_decideur_nomme_n_ecrit_RIEN():
    """LA RÈGLE CENTRALE. Sans le nom d'une personne, il n'y a pas de
    validation humaine — il y a une écriture automatique avec un mot de
    plus dans l'interface."""
    p = _proposition_juste()
    for vide in ("", "   ", None):
        r = qa.appliquer(SYSTEME, p, "valider", vide)
        assert r["ok"] is False, vide
        assert r["motif"] == "decideur_absent", r["motif"]
        assert "ecriture" not in r or r.get("ecriture") is None

    # GARDE-FOU : avec un nom, la même proposition s'inscrit.
    ok = qa.appliquer(SYSTEME, p, "valider", "C. Cerf — DPO")
    assert ok["ok"] is True and ok["ecriture"]["classification"] == "haut"


def test_ecarter_ne_rend_JAMAIS_de_ligne_a_ecrire():
    p = _proposition_juste()
    r = qa.appliquer(SYSTEME, p, "ecarter", "C. Cerf")
    assert r["ok"] is True and r["statut"] == "ecartee"
    assert r["ecriture"] is None


def test_une_proposition_DEJA_decidee_ne_se_decide_pas_deux_fois():
    """Sans quoi une même proposition pourrait réécrire le registre
    indéfiniment, chaque passage effaçant la décision précédente."""
    p = dict(_proposition_juste(), statut="validee")
    r = qa.appliquer(SYSTEME, p, "valider", "Quelqu'un d'autre")
    assert r["ok"] is False and r["motif"] == "deja_decidee", r


def test_valider_un_REFUS_est_refuse():
    """Une proposition tombée sur « à compléter » n'en est pas une : il n'y
    a pas de classe à inscrire, et valider ne doit pas en inventer une."""
    refus = qa.proposer(SYSTEME, _moteur(dict(REPONSE_JUSTE, article="art_6_bis")))
    r = qa.appliquer(SYSTEME, refus, "valider", "C. Cerf")
    assert r["ok"] is False and r["motif"] == "rien_a_valider", r


def test_la_personne_peut_CORRIGER_la_classe_et_la_trace_le_dit():
    """Valider ou rejeter enfermerait la personne dans le choix du moteur.
    Ce qu'elle retient est inscrit, et ce qui lui avait été proposé reste
    lisible à côté."""
    p = _proposition_juste()
    r = qa.appliquer(SYSTEME, p, "valider", "C. Cerf — DPO",
                     classe_retenue="limite")
    assert r["ok"] is True and r["corrigee"] is True
    assert r["ecriture"]["classification"] == "limite"
    j = r["ecriture"]["justification"]
    assert "CORRIG" in j.upper(), j
    assert "Haut risque" in j, j        # ce qui avait été proposé
    assert "C. Cerf — DPO" in j, j      # qui a tranché


def test_la_justification_inscrite_au_registre_NOMME_la_personne():
    """Une justification qui dirait seulement « annexe III » laisserait
    croire, six mois plus tard, qu'un juriste l'a écrite."""
    r = qa.appliquer(SYSTEME, _proposition_juste(), "valider", "M. Dupont — RSSI")
    j = r["ecriture"]["justification"]
    assert "M. Dupont — RSSI" in j, j
    assert "assist" in j.lower(), (
        "la justification ne dit pas que la proposition était assistée : %s" % j)


def test_une_classe_retenue_INCONNUE_est_refusee():
    r = qa.appliquer(SYSTEME, _proposition_juste(), "valider", "C. Cerf",
                     classe_retenue="tres_haut")
    assert r["ok"] is False and r["motif"] == "classe_retenue_inconnue", r


def test_l_ecart_dit_si_la_validation_CHANGERAIT_quelque_chose():
    """Faire valider quarante fois une classification identique à celle
    déjà inscrite use l'attention qu'on veut garder pour les vraies."""
    p = _proposition_juste()
    assert qa.ecart(SYSTEME, p)["change"] is True
    deja = dict(SYSTEME, classification="haut")
    assert qa.ecart(deja, p)["change"] is False


# ══════════════════════════════════════════════════════════════════════
# 5. LE VOCABULAIRE EST CELUI DU REGISTRE, PAS UN SECOND
# ══════════════════════════════════════════════════════════════════════

def test_les_classes_sont_celles_du_FORMULAIRE_du_registre():
    """Deux vocabulaires pour une seule colonne, et l'un des deux finit par
    écrire une valeur que l'autre ne sait pas lire."""
    du_module = set(qa.CLASSES)
    du_registre = {c["cle"] for c in finops_ia.CLASSIFICATION_IA_ACT}
    assert du_module == du_registre, du_module ^ du_registre

    # Et le formulaire servi au navigateur porte les mêmes.
    bloc = re.search(r'id="rf-classif"[^>]*>.*?sel\("classification",\[(.*?)\]\)',
                     SENTINEL_JS, re.S)
    assert bloc, "le formulaire du registre n'a pas été retrouvé"
    du_formulaire = set(re.findall(r'v:"([a-z_]+)"', bloc.group(1)))
    assert du_formulaire == du_registre, du_formulaire ^ du_registre


def test_chaque_classe_proposable_a_au_moins_un_article_qui_la_SOUTIENT():
    """Une classe qu'aucun article ne peut soutenir ne serait jamais
    proposée : elle figurerait au référentiel sans jamais servir."""
    couverte = set()
    for a in qa.ARTICLES:
        couverte |= set(a["soutient"])
    assert couverte == set(qa.PROPOSABLES), set(qa.PROPOSABLES) - couverte


def test_le_prompt_PORTE_la_liste_fermee_plutot_que_de_la_supposer():
    """Un modèle à qui l'on ne donne pas la liste la devine."""
    txt = qa.prompt(SYSTEME)
    for a in qa.ARTICLES:
        assert a["cle"] in txt, a["cle"]
    for c in qa.PROPOSABLES:
        assert c in txt, c
    assert "mot pour mot" in qa.PROMPT_SYSTEME.lower().replace("MOT POUR MOT", "mot pour mot")


# ══════════════════════════════════════════════════════════════════════
# 6. LA LAISSE DU MOTEUR
# ══════════════════════════════════════════════════════════════════════

def test_le_SDK_ne_recoit_AUCUN_outil():
    """L'écriture de référence du SDK donne Read, Edit et Bash. Ici la liste
    est vide — et c'est mesuré sur l'OBJET passé au SDK, pas sur le code
    source : une règle qui lirait le source passerait encore le jour où une
    autre ligne, plus bas, remplit la liste."""
    o = qm.options_sdk("systeme")
    assert list(o.allowed_tools) == [], o.allowed_tools


@pytest.mark.parametrize("outil", ["Read", "Write", "Edit", "Bash"])
def test_les_outils_qui_touchent_la_machine_sont_refuses_NOMMEMENT(outil):
    """Une liste vide se remplit par distraction ; un refus explicite se
    remarque en relecture."""
    o = qm.options_sdk("systeme")
    assert outil in o.disallowed_tools, outil
    assert outil not in o.allowed_tools, outil


def test_le_SDK_ne_charge_ni_le_CLAUDE_md_du_depot_ni_ses_competences():
    """Sans cela, l'agent hériterait de consignes écrites pour tout autre
    chose, que personne n'a relues pour une qualification réglementaire."""
    o = qm.options_sdk("systeme")
    assert list(o.setting_sources) == [], o.setting_sources


def test_le_moteur_n_a_qu_UN_tour():
    o = qm.options_sdk("systeme")
    assert o.max_turns == 1, o.max_turns


def _code_seul(corps):
    """Le code, sans la prose qui l'entoure.

    PREMIÈRE ÉCRITURE DE CETTE RÈGLE, ET POURQUOI ELLE ÉTAIT FAUSSE. Elle
    cherchait « ai_complete » dans le texte de la fonction de repli — et
    tombait sur la docstring de cette fonction, qui explique justement
    pourquoi `ai_complete` n'est PAS employé. Une règle qui échoue parce
    que le code se justifie est exactement le défaut qu'on chasse ailleurs,
    retourné : elle mesurait le commentaire, pas l'appel.
    """
    sans_doc = re.sub(r'"""".*?"""|\'\'\'.*?\'\'\'|""".*?"""', '', corps, flags=re.S)
    return re.sub(r'#[^\n]*', '', sans_doc)


def test_le_repli_n_est_JAMAIS_un_autre_fournisseur():
    """`ai_complete()` bascule sur Mistral quand Claude ne répond pas. Une
    qualification réglementaire qui changerait de moteur en silence
    changerait de raisonnement, sans que la trace écrite à côté de la
    proposition le dise."""
    bloc = re.search(r'def _qualif_secours\(.*?\n(?=\n@app\.route|\ndef )',
                     SOURCE_APP, re.S)
    assert bloc, "la fonction de repli n'a pas été retrouvée dans app.py"
    corps = _code_seul(bloc.group(0))
    assert 'call_anthropic' in corps, corps[:300]
    assert 'ai_complete' not in corps, (
        "le repli passe par ai_complete, qui bascule sur Mistral")
    assert 'mistral' not in corps.lower(), corps

    # GARDE-FOU : le dépouillement ne doit pas avoir tout effacé. Sans lui,
    # la règle passerait le jour où `_code_seul` rendrait une chaîne vide.
    assert 'qualification_moteur.MODELE' in corps, (
        "le dépouillement a emporté le code : la règle ne mesure plus rien")


def test_aucune_route_de_qualification_n_appelle_un_autre_fournisseur():
    """La règle précédente vise une fonction ; celle-ci vise le chemin
    entier. Un appel à Mistral ajouté dans la route plutôt que dans le
    repli passerait sous l'autre."""
    for nom in ('api_qualif_proposer', 'api_qualif_decider',
                'api_qualif_referentiel'):
        m = re.search(r'def %s\(.*?\n(?=\n@app\.route|\ndef |\Z)' % nom,
                      SOURCE_APP, re.S)
        assert m, nom
        corps = _code_seul(m.group(0)).lower()
        assert 'mistral' not in corps, nom
        assert 'ai_complete' not in corps, nom


def test_le_paquet_du_SDK_est_DECLARE_dans_requirements():
    """Installé sur la machine de développement et absent du déploiement,
    le SDK tomberait en ligne seulement."""
    assert 'claude-agent-sdk' in REQUIREMENTS, REQUIREMENTS


def test_l_absence_de_l_executable_est_MESUREE_et_non_supposee():
    """Le SDK lance l'exécutable Claude Code ; une image Python nue n'en a
    pas. `etat()` doit le dire au lieu de promettre un moteur qui tombera
    au premier appel."""
    e = qm.etat()
    assert isinstance(e["executable_claude_code"], bool)
    assert e["moteur_retenu"] in ("sdk", "api")
    if not e["executable_claude_code"]:
        assert e["moteur_retenu"] == "api", e


def test_sans_moteur_ni_repli_rien_n_est_propose():
    repondre, nom = qm.repondeur(secours=None, forcer="api")
    assert nom == "aucun"
    assert repondre("p", "s") == (False, "aucun_moteur")


# ══════════════════════════════════════════════════════════════════════
# 7. LES ROUTES — DEUX PORTES, UNE SEULE QUI ÉCRIT
# ══════════════════════════════════════════════════════════════════════

def test_la_route_qui_PROPOSE_n_ecrit_jamais_la_colonne_classification():
    """Mesuré sur le SOURCE des deux routes : celle qui propose ne contient
    aucun UPDATE de `systemes_ia`, celle qui décide en contient un."""
    def corps(nom):
        m = re.search(r'def %s\(.*?\n(?=\n@app\.route)' % nom, SOURCE_APP, re.S)
        assert m, nom
        return m.group(0)

    propose = corps('api_qualif_proposer')
    assert 'UPDATE systemes_ia' not in propose, (
        "la route qui propose écrit le registre")
    assert 'INSERT INTO qualifications_ia' in propose

    decide = re.search(r'def api_qualif_decider\(.*', SOURCE_APP, re.S).group(0)
    assert 'UPDATE systemes_ia' in decide, (
        "la route qui décide n'écrit PAS le registre : la règle ci-dessus "
        "passerait alors parce que personne ne l'écrit")


def test_le_lot_est_PLAFONNE():
    """Sans plafond, un registre de trois cents systèmes lance trois cents
    appels sur un clic."""
    m = re.search(r'QUALIF_LOT_MAX = (\d+)', SOURCE_APP)
    assert m, "aucun plafond de lot"
    assert 1 <= int(m.group(1)) <= 50, m.group(1)
    assert '[:QUALIF_LOT_MAX]' in SOURCE_APP, (
        "le plafond est déclaré mais jamais appliqué")


def test_les_deux_routes_sensibles_sont_derriere_un_plan_paye():
    for nom in ('api_qualif_proposer', 'api_qualif_propositions',
                'api_qualif_decider'):
        bloc = re.search(r'((?:@[^\n]+\n)+)def %s\(' % nom, SOURCE_APP)
        assert bloc, nom
        assert '@require_paid_plan' in bloc.group(1), nom
        assert '@rate_limit' in bloc.group(1), nom


def test_la_table_des_propositions_porte_QUI_a_decide_et_QUAND():
    """Ce sont les deux colonnes qui font la différence entre un registre
    opposable et une base de données."""
    for colonne in ('decide_par', 'decide_le', 'classe_retenue', 'statut',
                    'moteur', 'modele', 'classe_avant'):
        assert re.search(r'^\s+%s ' % colonne, SOURCE_APP, re.M), colonne
    # Les deux moteurs de base, pas un seul.
    assert SOURCE_APP.count('CREATE TABLE IF NOT EXISTS qualifications_ia') == 2


# ══════════════════════════════════════════════════════════════════════
# 8. L'ÉCRAN
# ══════════════════════════════════════════════════════════════════════

def test_l_ecran_DIT_quels_outils_le_moteur_n_a_pas():
    """C'est la première question d'un auditeur, et la réponse ne doit pas
    demander de lire le code."""
    assert 'outils_interdits' in SENTINEL_JS, SENTINEL_JS[:0]
    assert 'aucun outil' in SENTINEL_JS
    assert "n’ouvre aucun fichier et n’écrit nulle part" in SENTINEL_JS


def test_l_ecran_a_son_entree_son_panneau_son_meta_et_son_guide():
    assert 'id="p-qualif-assistee"' in SENTINEL_HTML
    assert "go('qualif-assistee'" in SENTINEL_HTML
    assert "'qualif-assistee': {section:'CARTOGRAPHIER'" in SENTINEL_JS
    assert "'qualif-assistee': {\n    title: \"Qualification assistée\"" in SENTINEL_JS


def test_l_ecran_annonce_que_le_moteur_N_ECRIT_PAS():
    """Un écran qui dit « assisté par IA » sans dire ce que l'IA ne fait pas
    laisse le lecteur supposer le pire — ou le meilleur."""
    bloc = re.search(r'id="p-qualif-assistee".*?</div>\s*\n</div>',
                     SENTINEL_HTML, re.S)
    assert bloc, "le panneau n'a pas été retrouvé"
    assert "Il n'écrit rien" in bloc.group(0) or "n'écrit rien" in bloc.group(0)


@pytest.mark.parametrize("cle", [
    'nav.item.qualif-assistee', 'pg.qualif-assistee.eb',
    'pg.qualif-assistee.h1', 'pg.qualif-assistee.p'])
def test_la_page_existe_AUSSI_en_anglais(cle):
    assert "'%s':" % cle in SENTINEL_JS, cle


# ══════════════════════════════════════════════════════════════════════
# 9. LA CHAÎNE COMPLÈTE, EXÉCUTÉE — PAS SEULEMENT LUE
# ══════════════════════════════════════════════════════════════════════
# Les règles de la section 7 lisent le source des routes. Celles-ci les
# FONT TOURNER sur une vraie base : elles inscrivent un système, demandent
# une proposition, et regardent la colonne `classification`. Une route qui
# écrirait le registre par un chemin que la lecture de source n'a pas vu —
# une fonction appelée, un déclencheur — tomberait ici et nulle part
# ailleurs.

import app as application  # noqa: E402


def _entetes():
    """Sans `Accept-Language`, l'application journalise HEADERS_INCOHERENTS
    et écarte la requête avant la vue : la règle accuserait alors le code
    pour un défaut d'en-tête."""
    return {'X-Forwarded-For': '203.0.113.19',
            'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                           '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'),
            'Accept-Language': 'fr-FR,fr;q=0.9',
            'Accept': 'application/json'}


@pytest.fixture
def client_connecte():
    c = application.app.test_client()
    with c.session_transaction() as s:
        s['is_conseilprev'] = True
    return c


@pytest.fixture
def moteur_de_recette(monkeypatch):
    """Le moteur est remplacé, PAS contourné : la route l'appelle comme en
    ligne. Ce qui est neutralisé, c'est l'appel réseau — pas la
    vérification, qui reste celle de production."""
    def faux_repondeur(secours=None, forcer=None):
        return _moteur(REPONSE_JUSTE), 'recette'
    monkeypatch.setattr(application.qualification_moteur, 'repondeur',
                        faux_repondeur)


def _creer_systeme(c, nom):
    r = c.post('/api/registre', headers=_entetes(), json={
        'nom': nom,
        'finalite': SYSTEME['finalite'],
        'type_systeme': SYSTEME['type_systeme'],
        'donnees_utilisees': SYSTEME['donnees_utilisees'],
        'secteur': SYSTEME['secteur'],
    })
    assert r.status_code in (200, 201), r.status_code
    d = r.get_json()
    sid = (d.get('systeme') or d).get('id')
    assert sid, d
    return sid


def _classification(c, sid):
    r = c.get('/api/registre', headers=_entetes())
    assert r.status_code == 200, r.status_code
    for s in r.get_json()['systemes']:
        if s['id'] == sid:
            return s['classification']
    raise AssertionError("système %s absent du registre" % sid)


def test_APRES_avoir_propose_le_registre_n_a_PAS_bouge(client_connecte,
                                                       moteur_de_recette):
    """LA RÈGLE QUE TOUT LE RESTE SERT. Le moteur a proposé « haut risque » ;
    la colonne du registre doit encore dire « à évaluer »."""
    c = client_connecte
    sid = _creer_systeme(c, 'Recette — proposition sans écriture')
    assert _classification(c, sid) == 'a_evaluer'

    r = c.post('/api/qualification/proposer', headers=_entetes(),
               json={'systemes': [sid]})
    assert r.status_code == 200, r.status_code
    d = r.get_json()
    assert d['traites'] == 1, d
    assert d['registre_modifie'] is False, d
    assert d['propositions'][0]['classe_proposee'] == 'haut', d['propositions'][0]

    assert _classification(c, sid) == 'a_evaluer', (
        "la route qui propose a écrit la classification")

    # La proposition existe bel et bien, et elle attend.
    r2 = c.get('/api/qualification/propositions', headers=_entetes())
    props = [p for p in r2.get_json()['propositions'] if p['systeme_id'] == sid]
    assert len(props) == 1 and props[0]['statut'] == 'en_attente', props


def test_C_EST_LA_DECISION_qui_ecrit_le_registre(client_connecte,
                                                 moteur_de_recette):
    """L'autre moitié : sans elle, la règle précédente passerait parce que
    RIEN n'écrit jamais le registre."""
    c = client_connecte
    sid = _creer_systeme(c, 'Recette — la décision écrit')
    c.post('/api/qualification/proposer', headers=_entetes(),
           json={'systemes': [sid]})
    pid = [p for p in c.get('/api/qualification/propositions',
                            headers=_entetes()).get_json()['propositions']
           if p['systeme_id'] == sid][0]['id']

    r = c.post('/api/qualification/%d/decider' % pid, headers=_entetes(),
               json={'decision': 'valider', 'decideur': 'C. Cerf — DPO'})
    assert r.status_code == 200, r.get_json()
    d = r.get_json()
    assert d['registre_modifie'] is True and d['decide_par'] == 'C. Cerf — DPO'

    assert _classification(c, sid) == 'haut', (
        "la décision validée n'a pas atteint le registre")


def test_ECARTER_laisse_le_registre_INTACT(client_connecte, moteur_de_recette):
    c = client_connecte
    sid = _creer_systeme(c, 'Recette — écartée')
    c.post('/api/qualification/proposer', headers=_entetes(),
           json={'systemes': [sid]})
    pid = [p for p in c.get('/api/qualification/propositions',
                            headers=_entetes()).get_json()['propositions']
           if p['systeme_id'] == sid][0]['id']

    r = c.post('/api/qualification/%d/decider' % pid, headers=_entetes(),
               json={'decision': 'ecarter', 'decideur': 'C. Cerf'})
    assert r.status_code == 200 and r.get_json()['registre_modifie'] is False
    assert _classification(c, sid) == 'a_evaluer'


def test_la_MEME_proposition_ne_se_decide_pas_deux_fois(client_connecte,
                                                        moteur_de_recette):
    c = client_connecte
    sid = _creer_systeme(c, 'Recette — deux fois')
    c.post('/api/qualification/proposer', headers=_entetes(),
           json={'systemes': [sid]})
    pid = [p for p in c.get('/api/qualification/propositions',
                            headers=_entetes()).get_json()['propositions']
           if p['systeme_id'] == sid][0]['id']

    a = c.post('/api/qualification/%d/decider' % pid, headers=_entetes(),
               json={'decision': 'valider', 'decideur': 'Première'})
    assert a.status_code == 200
    b = c.post('/api/qualification/%d/decider' % pid, headers=_entetes(),
               json={'decision': 'valider', 'decideur': 'Seconde',
                     'classe_retenue': 'minimal'})
    assert b.status_code == 400 and b.get_json()['motif'] == 'deja_decidee'
    assert _classification(c, sid) == 'haut', (
        "la seconde décision a tout de même réécrit le registre")


def test_la_trace_NOMME_toujours_quelqu_un(client_connecte, moteur_de_recette):
    """Même sans nom saisi, la décision est portée par le compte
    authentifié — jamais par « le système »."""
    c = client_connecte
    sid = _creer_systeme(c, 'Recette — sans nom saisi')
    c.post('/api/qualification/proposer', headers=_entetes(),
           json={'systemes': [sid]})
    pid = [p for p in c.get('/api/qualification/propositions',
                            headers=_entetes()).get_json()['propositions']
           if p['systeme_id'] == sid][0]['id']

    d = c.post('/api/qualification/%d/decider' % pid, headers=_entetes(),
               json={'decision': 'valider'}).get_json()
    qui = (d.get('decide_par') or '').strip()
    assert qui, d
    assert qui.lower() not in ('systeme', 'système', 'auto', 'ia', 'moteur',
                               'claude', 'none'), qui
    assert qui in _classification_justification(c, sid), (
        "le nom du décideur n'est pas inscrit dans la justification du "
        "registre : la trace ne survit pas à la table des propositions")


def _classification_justification(c, sid):
    for s in c.get('/api/registre', headers=_entetes()).get_json()['systemes']:
        if s['id'] == sid:
            return s.get('justification') or ''
    return ''


def test_un_anonyme_ne_propose_ni_ne_decide():
    c = application.app.test_client()
    for chemin, charge in (('/api/qualification/proposer', {}),
                           ('/api/qualification/1/decider',
                            {'decision': 'valider', 'decideur': 'X'})):
        r = c.post(chemin, headers=_entetes(), json=charge)
        assert r.status_code in (401, 403), (chemin, r.status_code)
    r = c.get('/api/qualification/propositions', headers=_entetes())
    assert r.status_code in (401, 403), r.status_code


def _requetes_sql(nom_de_fonction):
    """Toutes les requêtes SQL écrites dans une fonction, quelle que soit la
    forme de la chaîne.

    PREMIÈRE ÉCRITURE, ET POURQUOI ELLE MESURAIT MAL. Une expression
    régulière sur les guillemets simples ne voyait pas les chaînes triples —
    or c'est sous cette forme que sont écrits les INSERT longs. Elle
    laissait donc passer exactement les requêtes les plus faciles à oublier.
    L'arbre syntaxique, lui, les voit toutes.
    """
    import ast
    arbre = ast.parse(SOURCE_APP)
    cible = next((n for n in ast.walk(arbre)
                  if isinstance(n, ast.FunctionDef) and n.name == nom_de_fonction),
                 None)
    assert cible is not None, nom_de_fonction
    trouvees = []
    for noeud in ast.walk(cible):
        if isinstance(noeud, ast.Constant) and isinstance(noeud.value, str):
            t = noeud.value.strip()
            if re.match(r'^(SELECT|UPDATE|INSERT INTO|DELETE FROM)\b', t, re.I):
                trouvees.append(" ".join(t.split()))
    return trouvees


def test_chaque_requete_des_routes_porte_le_client():
    """L'isolation ne se vérifie pas à l'œil : une requête qui oublierait
    `client_id` montrerait les propositions d'un client à un autre."""
    for nom in ('api_qualif_proposer', 'api_qualif_propositions',
                'api_qualif_decider'):
        requetes = _requetes_sql(nom)
        assert requetes, (
            "aucune requête trouvée dans %s : la règle ne mesure rien" % nom)
        for r in requetes:
            assert 'client_id' in r, (nom, r[:160])


def test_la_route_qui_PROPOSE_ne_touche_pas_a_la_table_des_systemes():
    """Mesuré sur les requêtes elles-mêmes : celle qui propose ne fait que
    LIRE `systemes_ia`, et n'écrit que dans `qualifications_ia`."""
    ecritures = [r for r in _requetes_sql('api_qualif_proposer')
                 if not r.upper().startswith('SELECT')]
    assert ecritures, "la route ne conserve donc rien ?"
    for r in ecritures:
        assert 'systemes_ia' not in r, r[:160]
        assert 'qualifications_ia' in r, r[:160]

    # L'AUTRE MOITIÉ : la route qui décide, elle, écrit bien les deux.
    tables = {t for r in _requetes_sql('api_qualif_decider')
              if not r.upper().startswith('SELECT')
              for t in ('systemes_ia', 'qualifications_ia') if t in r}
    assert tables == {'systemes_ia', 'qualifications_ia'}, tables


# ══════════════════════════════════════════════════════════════════════
# 10. LA BATTERIE DE MUTATIONS SE PÉRIME SI PERSONNE NE LA GARDE
# ══════════════════════════════════════════════════════════════════════

def test_chaque_ancre_de_la_batterie_de_mutations_EXISTE_ENCORE():
    """Une mutation dont l'ancre ne se retrouve plus ne mute rien : elle
    passe pour « survivante » au prochain passage, et on cherche un défaut
    qui n'existe pas. Trois ancres se sont ainsi périmées en une seule
    séance, au fil de mes propres retouches."""
    table = json.load(io.open(os.path.join(ICI, 'tests',
                                           'mutations_qualification.json'),
                              encoding='utf-8'))
    sources = {}
    problemes = []
    for m in table['mutations']:
        f = m['fichier']
        if f not in sources:
            sources[f] = io.open(os.path.join(ICI, f), encoding='utf-8').read()
        n = sources[f].count(m['avant'])
        if n != 1:
            problemes.append("%s : %d occurrence(s) dans %s" % (m['nom'], n, f))
    assert not problemes, "\n".join(problemes)
    assert len(table['mutations']) >= 30, len(table['mutations'])


def test_une_ETAPE_DE_PARCOURS_ouvre_la_page_PEINTE_et_non_vide():
    """MESURÉ PAR LA RECETTE, PAS DEVINÉ.

    Le `onclick` de la barre latérale porte `;qualifInit()`. Mais une étape
    de parcours guidé appelle `go(step.id)` — la ligne est explicite dans
    `sentinel.page.js` — et ne passe donc jamais par ce `onclick`. Sans
    aiguillage dans `go()`, l'étape « Qualification assistée » du parcours
    du directeur de programme ouvrait un panneau VIDE.
    """
    assert re.search(
        r"if \(id === 'qualif-assistee' && typeof window\.qualifInit === "
        r"'function'\) _apresPeinture\(window\.qualifInit\);", SENTINEL_JS), (
        "go() n'aiguille pas vers qualifInit : une étape de parcours ouvrira "
        "un panneau vide")
    # La fonction doit être trouvable là où l'aiguillage la cherche.
    assert 'window.qualifInit = qualifInit;' in SENTINEL_JS
    # Et l'étape existe bien dans un parcours — sans quoi la règle ci-dessus
    # protégerait un chemin que personne n'emprunte.
    assert "{id:'qualif-assistee', label:'Qualification assistée'," in SENTINEL_JS
