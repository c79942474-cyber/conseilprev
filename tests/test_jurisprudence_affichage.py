# -*- coding: utf-8 -*-
"""UNE DÉCISION INVENTÉE A EXACTEMENT LA FORME D'UNE VRAIE.

CE QUE CES RÈGLES GARDENT, ET POURQUOI ELLES SONT SÉPARÉES DE CELLES DU MOTEUR.
Le module `librejustice` sait dire qu'une décision citée ne figurait pas dans
celles qu'on a montrées au modèle. Cela ne sert à rien si la page ne le dit pas
au lecteur — et une référence de texte inventée n'a pas la même gravité qu'une
décision inventée : la première se vérifie sur EUR-Lex en trente secondes, la
seconde porte une chambre, une date et un numéro de pourvoi de la bonne forme,
et rien ne la distingue d'une vraie sans aller la chercher.

Trois propriétés, dans l'ordre de ce qui fait mal :

1. QUE L'ALERTE SOIT ALARMANTE. « Non reconnue » invite à vérifier ;
   « inexistante » dit ce qu'il faut faire.
2. QUE L'APPROBATION NE S'AFFICHE PAS QUAND IL N'Y AVAIT RIEN À CONTRÔLER. Un
   « ✓ contrôle de la jurisprudence » sur une analyse où aucune décision n'a été
   rapportée est un faux témoignage de vérification.
3. QUE L'ADRESSE D'UNE DÉCISION NE PUISSE PAS EXÉCUTER DE CODE. Intitulés et
   adresses viennent d'un service tiers ; échapper le balisage ne protège pas du
   schéma.
"""
import io
import json
import os
import re
import shutil
import subprocess

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOTEUR = io.open(os.path.join(ICI, 'sentinel.page.js'), encoding='utf-8').read()
NODE = shutil.which('node')


# CE QUE LE RENDU EXIGE POUR S'EXÉCUTER. Repris du fichier tel qu'il est écrit
# plutôt que reconstruit ici : une table de traduction réécrite dans le contrôle
# ferait passer les règles sur autre chose que le code servi.
PRELUDE = ('juEsc', 'JU_PUBLICATION', 'JU_SOLUTION', 'juCode',
           'juOrd', 'juCreneau', 'juChambre',
           'juJurisprudence', 'juDecisions')


def _extraire(nom):
    """Une déclaration du moteur, fonction ou objet, telle qu'elle est écrite."""
    if nom[0].isupper() or nom.startswith('JU_'):
        d = MOTEUR.index('var %s=' % nom)
        f = MOTEUR.index('\n};', d)
        return MOTEUR[d:f + 3]
    d = MOTEUR.index('function %s(' % nom)
    return MOTEUR[d:MOTEUR.index('\n}\n', d) + 2]


def _evaluer(expression):
    """ÉVALUE le code servi au lieu de lire le fichier.

    Une règle qui cherche « rel="noopener" » dans le source est satisfaite par un
    commentaire — ce dépôt s'est déjà fait prendre. On exécute donc les
    déclarations telles qu'elles sont écrites et on regarde ce qu'elles
    produisent."""
    if not NODE:
        pytest.skip('node absent : le rendu ne peut pas être évalué')
    src = '\n'.join(_extraire(n) for n in PRELUDE)
    prog = src + '\nconsole.log(JSON.stringify(%s));' % expression
    r = subprocess.run([NODE, '-e', prog], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        pytest.fail('%s ne s\'évalue pas :\n%s' % (expression, (r.stderr or '')[-1200:]))
    return json.loads(r.stdout)


def _rendre(appel, argument):
    return _evaluer('%s(%s)' % (appel, json.dumps(argument, ensure_ascii=False)))


DECISION = {
    "titre": "Cour de cassation, Chambre commerciale, 22 octobre 1996",
    "url": "https://librejustice.fr/decision/cc-1996-10-22",
    "juridiction": "Cour de cassation", "chambre": "COMMERCIALE",
    "date": "1996-10-22", "numero": "93-18.632",
    "publication": "PUBLIE_BULLETIN", "solution": "CASSATION",
    "sort": "CONFIRMATION — confirmée le 9 juillet 2002",
}


# ── L'ALERTE ─────────────────────────────────────────────────────────────

def test_une_decision_hors_liste_est_signalee_comme_inexistante():
    """« Non reconnue » invite à vérifier — et personne ne vérifie. Le lecteur
    doit savoir qu'il n'y a rien à vérifier : la décision n'existe pas."""
    h = _rendre('juJurisprudence',
                {"ok": False, "suspectes": [{"type": "pourvoi", "cle": "9999999"}],
                 "montrees": 2})
    assert '9999999' in h
    assert 'INEXISTANTES' in h, (
        "l'alerte ne dit pas quoi faire de la décision citée : %s" % h[:200])


def test_l_approbation_ne_s_affiche_pas_sans_decision_rapportee():
    """UN FAUX TÉMOIGNAGE DE VÉRIFICATION. La plupart des analyses n'auront
    aucune jurisprudence — les textes en cause datent de 2024. Afficher
    « ✓ contrôle de la jurisprudence » sur celles-là ferait croire à un contrôle
    qui n'a rien contrôlé."""
    h = _rendre('juJurisprudence',
                {"ok": True, "suspectes": [], "montrees": 0})
    assert h == '', "une approbation s'affiche alors qu'aucune décision n'a été rapportée"


def test_l_approbation_ne_promet_pas_ce_qu_elle_ne_verifie_pas():
    """Le contrôle dit qu'aucune décision n'a été AJOUTÉE. Il ne dit pas que la
    lecture qu'on en fait est juste — et un lecteur pressé lira la coche verte
    comme une validation du raisonnement."""
    h = _rendre('juJurisprudence',
                {"ok": True, "suspectes": [], "montrees": 3})
    assert h, "aucune mention du contrôle alors que des décisions ont été rapportées"
    assert 'lisez-la' in h or 'ne dit pas ce que chacune juge' in h, (
        "l'approbation ne réserve pas la lecture des décisions : %s" % h[:300])


# ── LES DÉCISIONS AFFICHÉES ──────────────────────────────────────────────

def test_chaque_decision_est_liee_a_sa_source():
    """C'est ce qui rend le contrôle vérifiable par le lecteur, et ce qui lui
    permet d'aller lire l'arrêt au lieu de croire ce qu'on lui en dit."""
    h = _rendre('juDecisions', [DECISION])
    assert 'href="https://librejustice.fr/decision/cc-1996-10-22"' in h
    assert 'Chambre commerciale' in h
    assert '93-18.632' in h


def test_les_decisions_ne_sont_pas_rendues_dans_le_conteneur_a_pastilles():
    """LA CSS DÉCIDE DE LA MISE EN PAGE, PAS L'INTENTION. `.ju-srcs` est un
    conteneur flex à pastilles ; un titre et des retours de ligne placés dedans
    deviennent des éléments flex distincts et la liste se disloque. Vérifié en
    lisant la feuille de style, pas en la supposant."""
    h = _rendre('juDecisions', [DECISION])
    assert 'ju-srcs' not in h, (
        "les décisions sont rendues dans le conteneur flex des sources")
    page = io.open(os.path.join(ICI, 'sentinel.html'), encoding='utf-8').read()
    for classe in re.findall(r'class="(ju-jur[a-z-]*)"', h):
        assert '.%s{' % classe in page or '.%s ' % classe in page, (
            "la classe « %s » est employée mais n'est stylée nulle part" % classe)


def test_la_reserve_accompagne_les_decisions():
    """Une réserve rangée dans les mentions légales n'accompagne pas ce qu'elle
    doit accompagner : elle doit être là où le lecteur lit la décision."""
    h = _rendre('juDecisions', [DECISION])
    assert 'décision cassée ne dit plus rien' in h


@pytest.mark.parametrize('code,attendu', [
    ('INEDIT_BULLETIN', 'ne fait pas jurisprudence'),
    ('INEDIT_LEBON', 'ne fait pas jurisprudence'),
    ('PUBLIE_BULLETIN', 'publiée au Bulletin'),
    ('PUBLIE_RAPPORT', 'portée maximale'),
])
def test_la_publication_est_dite_en_francais_avec_sa_portee(code, attendu):
    """« INEDIT_BULLETIN » n'est pas seulement du jargon : c'est l'information la
    plus utile de la ligne. Une décision inédite NE FAIT PAS jurisprudence, et un
    sigle en majuscules escamote précisément cela.

    LA TRADUCTION EST CONTRÔLÉE SUR ELLE-MÊME, pas dans le bloc entier. Une
    mutation qui vidait « inédite — ne fait pas jurisprudence » de sa portée a
    SURVÉCU à la première version : la réserve, trois lignes plus bas, porte déjà
    « une décision non publiée ne fait pas jurisprudence ». La règle lisait la
    réserve et croyait lire la traduction."""
    traduit = _evaluer('juCode(%s, JU_PUBLICATION)' % json.dumps(code))
    assert attendu in traduit, (
        "« %s » se traduit « %s » et devrait porter « %s »" % (code, traduit, attendu))
    h = _rendre('juDecisions', [dict(DECISION, publication=code)])
    assert code not in h, "le code du référentiel est affiché tel quel"
    assert traduit in h, "la traduction n'est pas employée par le rendu"


@pytest.mark.parametrize('cle,attendu', [
    ('COMMERCIALE', 'chambre commerciale'),
    ('SOCIALE', 'chambre sociale'),
    ('P5.C4', 'pôle 5, 4e chambre'),
    ('P5.C1', 'pôle 5, 1re chambre'),
    ('SC4.C6', '4e section, 6e chambre'),
    ('CD', 'chambre D'),
    ('C4-7', 'chambre 4-7'),
    ('S1', '1re section'),
    ('LB', 'section B'),
    ('Q1-4', 'sous-sections 1/4 réunies'),
    ('R3-8', 'chambres 3/8 réunies'),
])
def test_la_formation_est_dite_en_clair(cle, attendu):
    """« P5.C4 » n'est pas une formation, c'est une clé. Un lecteur juriste doit
    lire « pôle 5, 4e chambre » — la grammaire des créneaux est celle du
    référentiel, on la décode, on ne la devine pas."""
    h = _rendre('juChambre', cle)
    assert h == attendu, "« %s » se lit « %s » et non « %s »" % (cle, h, attendu)
    # ET LE RENDU S'EN SERT. Une mutation qui remplaçait juChambre(d.chambre) par
    # d.chambre a SURVÉCU tant que cette règle n'appelait que la fonction :
    # traduire correctement une valeur que personne n'affiche ne sert à rien.
    bloc = _rendre('juDecisions', [dict(DECISION, chambre=cle)])
    assert attendu in bloc, (
        "« %s » est traduit mais le rendu affiche encore la clé brute" % cle)


@pytest.mark.parametrize('inconnu', ['XZ9', 'FORMATION-PLENIERE', 'W12-3'])
def test_un_creneau_non_documente_passe_tel_quel(inconnu):
    """INVENTER UNE LECTURE SERAIT PIRE QUE DE NE PAS LIRE. Une formation
    fabriquée sur une décision de justice est une erreur de fond ; une clé brute
    n'est qu'une gêne."""
    assert _rendre('juChambre', inconnu) == inconnu


def test_la_solution_est_dite_en_francais():
    h = _rendre('juDecisions',
                [dict(DECISION, solution='CASSATION_PARTIELLE')])
    assert 'cassation partielle' in h and 'CASSATION_PARTIELLE' not in h


def test_un_code_inconnu_est_rendu_lisible_et_non_masque():
    """Le corpus peut ajouter des valeurs. Les masquer perdrait une information ;
    les afficher en majuscules à souligné donnerait du jargon."""
    h = _rendre('juDecisions',
                [dict(DECISION, solution='SURSIS_A_STATUER')])
    assert 'sursis a statuer' in h, (
        "un code inconnu a disparu au lieu d'être rendu lisible : %s" % h[:300])
    assert 'SURSIS_A_STATUER' not in h, "le code brut est affiché tel quel"


def test_le_sort_de_la_decision_est_affiche():
    """Une décision infirmée ne fonde rien. Ne pas l'afficher revient à
    présenter comme autorité ce qui n'en est plus une."""
    h = _rendre('juDecisions', [DECISION])
    assert 'Sort de cette décision' in h and 'confirmée' in h


def test_aucune_decision_aucun_bloc():
    for vide in ([], None):
        assert _rendre('juDecisions', vide) == ''


@pytest.mark.parametrize('adresse', [
    'javascript:alert(1)',
    'JaVaScRiPt:alert(1)',
    'data:text/html,<script>alert(1)</script>',
    'vbscript:msgbox(1)',
])
def test_une_adresse_qui_n_est_pas_http_n_est_pas_rendue_cliquable(adresse):
    """ÉCHAPPER PROTÈGE DU BALISAGE, PAS DU SCHÉMA. juEsc empêche de sortir de
    l'attribut ; il n'empêche pas « javascript: » d'y être exécuté au clic. Les
    adresses viennent d'un service tiers : on n'ouvre que http et https."""
    d = dict(DECISION, url=adresse)
    h = _rendre('juDecisions', [d])
    assert '<a ' not in h, (
        "une adresse « %s » a été rendue cliquable : %s" % (adresse, h[:220]))
    assert 'Chambre commerciale' in h, "l'intitulé doit rester affiché, en texte"


def test_un_intitule_hostile_ne_produit_pas_de_balise():
    """L'intitulé vient du corpus, pas de l'application."""
    d = dict(DECISION, titre='<img src=x onerror=alert(1)>')
    h = _rendre('juDecisions', [d])
    assert '<img' not in h, "l'intitulé a produit une balise : %s" % h[:200]
    assert '&lt;img src=x onerror=alert(1)&gt;' in h, (
        "l'intitulé n'a pas été échappé, ou a été supprimé au lieu de l'être")


def test_un_lien_externe_ne_donne_pas_la_main_a_la_page_ouverte():
    h = _rendre('juDecisions', [DECISION])
    assert 'rel="noopener' in h, (
        "le lien s'ouvre sans noopener : la page ouverte garde une référence "
        "sur celle-ci")


# ── LE BRANCHEMENT DANS LES DEUX RENDUS ──────────────────────────────────

@pytest.mark.parametrize('rendu,ce_que_c_est', [
    ('juRendreAnalyse', "l'analyse juridique et la revue de contrat"),
    ('ju-arb-res', "la note d'arbitrage"),
])
def test_les_deux_rendus_portent_le_controle_de_jurisprudence(rendu, ce_que_c_est):
    """Une note d'arbitrage se lit en comité de direction ; il n'y a aucune
    raison qu'elle affiche moins de garde-fous qu'une analyse."""
    if rendu == 'juRendreAnalyse':
        d = MOTEUR.index('function juRendreAnalyse(')
        bloc = MOTEUR[d:MOTEUR.index('\n}\n', d)]
    else:
        d = MOTEUR.index("juApi('/api/juridique/arbitrage'")
        bloc = MOTEUR[d:d + 3000]
    assert 'juJurisprudence(' in bloc, (
        "%s n'affiche pas le contrôle des décisions citées" % ce_que_c_est)
    assert 'juDecisions(' in bloc, (
        "%s n'affiche pas les décisions consultées" % ce_que_c_est)


def test_le_controle_des_textes_est_toujours_affiche():
    """L'ajout ne doit pas avoir remplacé le contrôle qui existait."""
    assert MOTEUR.count('juCitations(j.citations)') >= 2


def test_aucune_regle_ici_ne_se_contente_de_lire_le_fichier():
    """CETTE RÈGLE GARDE LES AUTRES. Chercher « rel="noopener" » dans le source
    est satisfait par un commentaire, et ce dépôt s'est déjà fait prendre. Les
    contrôles de rendu passent donc par une ÉVALUATION dans Node ; ceux qui
    lisent le fichier ne portent que sur le branchement, où il n'y a rien à
    exécuter."""
    src = io.open(os.path.abspath(__file__), encoding='utf-8').read()
    corps = src[src.index('DECISION = {'):]
    # Les seules règles autorisées à lire MOTEUR directement.
    lectrices = re.findall(r'def (test_\w+)\([^)]*\):(.*?)(?=\ndef |\Z)', corps, re.S)
    for nom, corps_regle in lectrices:
        if 'MOTEUR' in corps_regle and '_rendre' not in corps_regle:
            assert nom in ('test_les_deux_rendus_portent_le_controle_de_jurisprudence',
                           'test_le_controle_des_textes_est_toujours_affiche'), (
                "%s lit le fichier au lieu d'exécuter le rendu" % nom)
