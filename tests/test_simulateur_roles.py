"""LE SIMULATEUR NE DEMANDAIT JAMAIS LE RÔLE, ET RÉPONDAIT COMME SI C'ÉTAIT LE FOURNISSEUR.

CE QUI A DÉCLENCHÉ CE FICHIER. La confrontation de Sentinel au guide
d'application de l'IA Act, le 28 août 2026. Le simulateur posait vingt et une
questions — secteur, type, biométrie, profilage, impact, GPAI, données,
chiffre d'affaires, territoire — et pas une seule sur la PLACE occupée dans la
chaîne de valeur. Il rendait ensuite, pour tout système classé à haut risque,
les articles 9, 10, 11, 12, 13, 14 et 17.

Ce sont les obligations du FOURNISSEUR. Les articles 26 et 27, qui portent
celles du déployeur, n'apparaissaient dans aucune sortie du simulateur — ni
dans les listes, ni dans les notes, ni dans le calendrier. Or la plupart des
organisations qui emploient cet outil ACHÈTENT leurs systèmes : elles sont
déployeurs. Elles recevaient une liste plausible, détaillée, chiffrée en euros
de sanction — et fausse de bout en bout. En excès sur ce qu'elles doivent, et
muette sur ce qu'elles doivent réellement.

RIEN NE LE SIGNALAIT, et c'est la propriété commune des défauts coûteux : le
simulateur ne plantait pas, ne se contredisait pas, ne rendait aucune erreur.
Il répondait bien à une question que personne ne lui avait posée.

CE QUE CES RÈGLES GARDENT. Elles ne lisent pas le code, elles l'EXÉCUTENT :
le moteur de rôle et de gap est extrait du fichier et évalué dans Node, avec
des réponses fabriquées. Une règle qui chercherait « Art. 26 » dans la source
serait satisfaite par un commentaire ; celles-ci exigent que l'article 26
sorte du moteur pour un déployeur, et n'en sorte pas pour un fournisseur.
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
PAGE = io.open(os.path.join(ICI, 'sentinel.html'), encoding='utf-8').read()

NODE = shutil.which('node')

# Les bornes de l'extrait exécuté. Elles sont vérifiées par un contrôle dédié :
# si elles se déplaçaient sans qu'on le voie, toutes les règles de ce fichier
# cesseraient de mesurer quoi que ce soit.
DEBUT = 'var SIM_ROLES = {'
FIN = "/* Timeline d'application */"


def _extrait():
    d = MOTEUR.index(DEBUT)
    return MOTEUR[d:MOTEUR.index(FIN, d)]


def _evaluer(reponses, classif=None, expression='simGap(CLASSIF).map(function(x){return x.obl.id;})'):
    """Exécute le moteur du simulateur sur des réponses fabriquées.

    EN SOUS-PROCESSUS NODE, ET PAS EN RELISANT LE TEXTE. Une règle qui cherche
    un numéro d'article dans la source est satisfaite par le commentaire qui
    l'explique. Celle-ci exige que l'article sorte réellement du moteur."""
    if not NODE:
        pytest.skip('node absent : le moteur du simulateur ne peut pas être exécuté')
    classif = dict({'level': 'haut', 'art5': False, 'extra_territorial': False}, **(classif or {}))
    programme = (
        'var SIM_DATA = %s;\nvar CLASSIF = %s;\n%s\n'
        'console.log(JSON.stringify(%s));'
        % (json.dumps(reponses), json.dumps(classif), _extrait(), expression))
    r = subprocess.run([NODE, '-e', programme], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        pytest.fail('le moteur du simulateur ne s\'exécute pas :\n%s' % (r.stderr or '')[-1500:])
    return json.loads(r.stdout.strip())


def _reponses(**kw):
    base = {'role': 'fournisseur', 'art25': 'non', 'fria': 'non',
            'definition': ['def-machine', 'def-autonomie', 'def-inference',
                           'def-objectifs', 'def-sorties', 'def-influence'],
            'anteriorite': 'apres', 'annexe3': ['annexe3-emploi'],
            'interaction': 'non', 'gpai': 'non', 'rgpd': 'non'}
    base.update(kw)
    return base


# Ce qui doit sortir, et ce qui ne doit pas, pour chaque rôle.
FOURNISSEUR = ['art9', 'art10', 'art11', 'art12', 'art13', 'art14', 'art17',
               'art15', 'art43', 'art47_48', 'art49', 'art72', 'art73']
DEPLOYEUR = ['art26_notice', 'art26_supervision', 'art26_donnees', 'art26_surveillance',
             'art26_journaux', 'art26_travailleurs', 'art26_personnes', 'art86']
IMPORTATEUR = ['art23_verif', 'art23_abstention', 'art23_identite']
DISTRIBUTEUR = ['art24_verif', 'art24_abstention']


def test_les_bornes_de_l_extrait_existent_toujours():
    """Toutes les règles de ce fichier passent par cet extrait. S'il ne se
    découpait plus, elles s'exécuteraient sur du vide en passant."""
    assert DEBUT in MOTEUR, "le catalogue des rôles a disparu du moteur"
    assert FIN in MOTEUR, "la borne de fin de l'extrait a disparu"
    extrait = _extrait()
    for attendu in ('function simRole(', 'function simGap(', 'function simDefinition(',
                    'function simOpenSource(', 'function simAnteriorite('):
        assert attendu in extrait, "%s n'est plus dans l'extrait exécuté" % attendu


# ── CHAQUE RÔLE REÇOIT SES OBLIGATIONS, ET SEULEMENT LES SIENNES ─────────

def test_le_deployeur_recoit_l_article_26():
    """LA RÈGLE PRINCIPALE, celle dont l'absence a motivé tout ce fichier.
    L'article 26 ne sortait d'aucune branche du simulateur."""
    obls = _evaluer(_reponses(role='deployeur'))
    manquants = [o for o in DEPLOYEUR if o not in obls]
    assert not manquants, (
        "un déployeur de système à haut risque ne reçoit pas %s : ce sont ses "
        "obligations propres, et le simulateur ne les rendait pas du tout "
        "avant le 28 août 2026" % ', '.join(manquants))


def test_le_deployeur_ne_recoit_pas_les_obligations_du_fournisseur():
    """L'AUTRE MOITIÉ, et la plus coûteuse : on ne fait pas faire à une
    organisation un dossier technique d'annexe IV pour un logiciel acheté."""
    obls = _evaluer(_reponses(role='deployeur'))
    en_trop = [o for o in FOURNISSEUR if o in obls]
    assert not en_trop, (
        "un déployeur reçoit %s, qui sont les obligations du fournisseur : le "
        "simulateur lui demande de refaire ce que son fournisseur doit faire"
        % ', '.join(en_trop))


def test_le_fournisseur_recoit_les_siennes_et_pas_celles_du_deployeur():
    obls = _evaluer(_reponses(role='fournisseur'))
    manquants = [o for o in FOURNISSEUR if o not in obls]
    assert not manquants, "un fournisseur ne reçoit pas %s" % ', '.join(manquants)
    en_trop = [o for o in DEPLOYEUR if o in obls]
    assert not en_trop, (
        "un fournisseur reçoit %s, qui relèvent du déployeur" % ', '.join(en_trop))


@pytest.mark.parametrize('role,attendus,ecartes', [
    ('importateur', IMPORTATEUR, FOURNISSEUR + DEPLOYEUR + DISTRIBUTEUR),
    ('distributeur', DISTRIBUTEUR, FOURNISSEUR + DEPLOYEUR + IMPORTATEUR),
])
def test_les_roles_intermediaires_ont_leurs_propres_articles(role, attendus, ecartes):
    """Les articles 23 et 24 ne figuraient nulle part dans les sorties. Un
    importateur qui interrogeait le simulateur recevait le régime du
    fournisseur, qu'il n'a pas les moyens d'exécuter — il n'a pas conçu le
    système."""
    obls = _evaluer(_reponses(role=role))
    manquants = [o for o in attendus if o not in obls]
    assert not manquants, "un %s ne reçoit pas %s" % (role, ', '.join(manquants))
    en_trop = [o for o in ecartes if o in obls]
    assert not en_trop, "un %s reçoit %s, qui ne le concernent pas" % (role, ', '.join(en_trop))


def test_un_role_non_renseigne_rend_tous_les_roles_au_lieu_de_trancher():
    """« Je ne sais pas » est une réponse. Un simulateur qui choisit à la place
    de l'utilisateur fabrique une certitude que rien ne fonde — et c'est
    exactement ce que faisait l'ancien, silencieusement, pour tout le monde."""
    obls = _evaluer(_reponses(role=None))
    for jeu, nom in ((FOURNISSEUR, 'fournisseur'), (DEPLOYEUR, 'déployeur'),
                     (IMPORTATEUR, 'importateur'), (DISTRIBUTEUR, 'distributeur')):
        manquants = [o for o in jeu if o not in obls]
        assert not manquants, (
            "rôle non renseigné : les obligations du %s ne sont pas rendues (%s "
            "manquent). Le simulateur tranche donc à la place de l'utilisateur."
            % (nom, ', '.join(manquants)))


# ── LA REQUALIFICATION DE L'ARTICLE 25 ───────────────────────────────────

@pytest.mark.parametrize('motif', ['nom', 'substantielle', 'finalite'])
def test_l_article_25_requalifie_le_deployeur_en_fournisseur(motif):
    """LA BASCULE QUE LES ORGANISATIONS DÉCOUVRENT LE PLUS TARD. Apposer son
    nom, modifier substantiellement, ou changer la destination : chacune fait
    du déployeur le fournisseur, avec toutes ses obligations."""
    obls = _evaluer(_reponses(role='deployeur', art25=motif))
    manquants = [o for o in FOURNISSEUR if o not in obls]
    assert not manquants, (
        "art. 25(1) « %s » ne requalifie pas en fournisseur : %s manquent"
        % (motif, ', '.join(manquants)))


def test_sans_declencheur_il_n_y_a_pas_de_requalification():
    """La règle inverse, sans laquelle la précédente serait satisfaite par un
    moteur qui requalifierait TOUT LE MONDE en fournisseur."""
    obls = _evaluer(_reponses(role='deployeur', art25='non'))
    en_trop = [o for o in FOURNISSEUR if o in obls]
    assert not en_trop, (
        "un déployeur qui n'a rien modifié est tout de même requalifié en "
        "fournisseur : %s" % ', '.join(en_trop))


def test_la_requalification_est_annoncee_et_motivee():
    r = _evaluer(_reponses(role='deployeur', art25='substantielle'), expression='simRole()')
    assert r['role'] == 'fournisseur', "le rôle effectif n'est pas fournisseur"
    assert r['requalifie'] is True, "la requalification n'est pas signalée"
    assert r['motif'], "la requalification ne dit pas POURQUOI elle a lieu"


# ── L'ANALYSE D'IMPACT SUR LES DROITS FONDAMENTAUX — ART. 27 ─────────────

@pytest.mark.parametrize('cas', ['public', 'service_public', 'credit_assurance'])
def test_l_aidf_est_due_dans_les_cas_de_l_article_27(cas):
    obls = _evaluer(_reponses(role='deployeur', fria=cas))
    assert 'art27' in obls, (
        "l'analyse d'impact sur les droits fondamentaux n'est pas rendue pour "
        "le cas « %s », alors que l'article 27(1) la prévoit" % cas)


def test_l_aidf_n_est_pas_due_hors_de_ces_cas():
    """L'imposer à tous serait aussi faux que ne l'imposer à personne — et
    coûterait au client un travail que le règlement ne lui demande pas."""
    obls = _evaluer(_reponses(role='deployeur', fria='non'))
    assert 'art27' not in obls, (
        "l'AIDF est rendue à un déployeur privé hors solvabilité et assurance : "
        "l'article 27(1) ne l'y oblige pas")


def test_l_aidf_ne_concerne_pas_le_fournisseur():
    obls = _evaluer(_reponses(role='fournisseur', fria='public'))
    assert 'art27' not in obls, (
        "l'AIDF est rendue à un fournisseur : c'est une obligation de déployeur")


# ── CE QUI VAUT POUR TOUS, ET CE QUI NE VAUT QU'AU HAUT RISQUE ──────────

@pytest.mark.parametrize('niveau', ['haut', 'limite', 'minimal'])
def test_la_maitrise_de_l_ia_est_due_a_tous_les_niveaux(niveau):
    """Article 4 : la maîtrise de l'IA ne dépend pas du niveau de risque. Elle
    ne sortait d'aucune branche du simulateur."""
    obls = _evaluer(_reponses(), classif={'level': niveau})
    assert 'art4' in obls, (
        "la maîtrise de l'IA (art. 4) n'est pas rendue au niveau « %s », alors "
        "qu'elle est due quel que soit le niveau de risque" % niveau)


def test_les_obligations_de_role_ne_sortent_pas_hors_du_haut_risque():
    """Les articles 9 à 17 et 26 sont attachés au régime des systèmes à haut
    risque. Les rendre pour un système à risque limité ferait faire un travail
    que rien n'impose."""
    obls = _evaluer(_reponses(role='deployeur'), classif={'level': 'limite'})
    en_trop = [o for o in DEPLOYEUR + FOURNISSEUR if o in obls]
    assert not en_trop, (
        "des obligations du régime haut risque sortent pour un système à "
        "risque limité : %s" % ', '.join(en_trop))


# ── LA DÉFINITION DE L'ARTICLE 3(1) ──────────────────────────────────────

def test_une_definition_non_renseignee_ne_conclut_rien():
    """LA RÈGLE QUI ÉVITE LE PIRE FAUX POSITIF. Sans elle, tout utilisateur qui
    saute cet écran verrait son système déclaré hors du champ du règlement —
    la conclusion la plus dangereuse que l'outil puisse rendre."""
    r = _evaluer(_reponses(definition=[]), expression='simDefinition()')
    assert r['statut'] == 'non_renseigne', (
        "une case à cocher jamais touchée est lue comme une réponse négative : "
        "le simulateur conclut « %s » sans qu'on lui ait rien dit" % r['statut'])


def test_sans_inference_le_systeme_sort_du_champ():
    """L'élément décisif de la définition. Un logiciel de règles écrites à la
    main n'est pas un système d'IA, et le règlement ne s'y applique pas."""
    r = _evaluer(_reponses(definition=['def-machine', 'def-autonomie', 'def-objectifs',
                                       'def-sorties', 'def-influence']),
                 expression='simDefinition()')
    assert r['statut'] == 'hors_champ', (
        "l'inférence n'est pas cochée et le système reste dans le champ : "
        "statut rendu « %s »" % r['statut'])


def test_les_six_elements_cumules_qualifient_le_systeme():
    r = _evaluer(_reponses(), expression='simDefinition()')
    assert r['statut'] == 'systeme_ia', "les six éléments cochés ne qualifient plus"


def test_un_element_manquant_appelle_une_verification_sans_trancher():
    r = _evaluer(_reponses(definition=['def-inference', 'def-machine', 'def-sorties']),
                 expression='simDefinition()')
    assert r['statut'] == 'a_verifier', (
        "une définition incomplète mais avec inférence devrait appeler une "
        "vérification, pas un verdict — statut rendu « %s »" % r['statut'])


# ── L'EXEMPTION LIBRE ET OUVERTE ─────────────────────────────────────────

def test_sans_licence_libre_la_question_ne_se_pose_pas():
    r = _evaluer(_reponses(oss='non'), expression='simOpenSource(CLASSIF)')
    assert r['statut'] == 'sans_objet'


@pytest.mark.parametrize('declencheur', ['mon-prix', 'mon-service', 'mon-support', 'mon-dons'])
def test_une_seule_contrepartie_fait_tomber_l_exemption(declencheur):
    """Sentinel citait l'exemption sans donner le moyen de savoir si elle
    s'applique — ce qui revient à laisser croire qu'elle s'applique. C'est la
    contrepartie, non la licence, qui décide."""
    r = _evaluer(_reponses(oss='oui', monetisation=[declencheur]),
                 expression='simOpenSource(CLASSIF)')
    assert r['statut'] == 'tombe', (
        "« %s » ne fait pas tomber l'exemption libre et ouverte" % declencheur)
    assert r['declencheurs'], "l'exemption tombe sans dire à cause de quoi"


def test_sans_contrepartie_l_exemption_tient_mais_ses_limites_sont_dites():
    """Une exemption annoncée sans ses exclusions s'entend comme générale.
    Elle ne l'est pas : elle ne couvre ni l'article 5, ni le haut risque, ni
    l'article 50, ni les modèles à risque systémique."""
    r = _evaluer(_reponses(oss='oui', monetisation=[]),
                 expression='simOpenSource(CLASSIF)')
    assert r['statut'] == 'tient'
    assert r['exclusions'], (
        "l'exemption est annoncée applicable pour un système à HAUT RISQUE "
        "sans dire qu'elle ne couvre pas ce régime")


def test_le_risque_systemique_est_exclu_de_l_exemption():
    r = _evaluer(_reponses(oss='oui', monetisation=[], gpai='oui_flop'),
                 classif={'level': 'minimal'}, expression='simOpenSource(CLASSIF)')
    assert any('systémique' in e for e in r['exclusions']), (
        "l'exemption de l'article 53(2) est présentée comme jouant pour un "
        "modèle à risque systémique")


# ── L'ANTÉRIORITÉ DE L'ARTICLE 111(2) ────────────────────────────────────

def test_l_anteriorite_differe_le_regime_sans_l_effacer():
    r = _evaluer(_reponses(anteriorite='avant_inchange'), expression='simAnteriorite(CLASSIF)')
    assert r and r['statut'] == 'differe'
    for reste_du in ('article 5', 'article 50', 'article 4'):
        assert reste_du in r['texte'], (
            "l'aménagement de l'article 111(2) est présenté sans dire que %s "
            "reste dû : le lecteur en conclura qu'il n'a rien à faire" % reste_du)


def test_une_modification_importante_fait_tomber_l_anteriorite():
    r = _evaluer(_reponses(anteriorite='avant_modifie'), expression='simAnteriorite(CLASSIF)')
    assert r and r['statut'] == 'perdue'


def test_l_anteriorite_ne_s_invente_pas_quand_la_question_n_est_pas_posee():
    r = _evaluer(_reponses(anteriorite=None), expression='simAnteriorite(CLASSIF)')
    assert r is None, "une antériorité est affirmée sans que la question ait été posée"


# ── LES GROUPES INTERROGÉS EXISTENT DANS LA PAGE ─────────────────────────

def test_tout_groupe_lu_par_le_moteur_existe_dans_la_page():
    """UN IDENTIFIANT MAL ORTHOGRAPHIÉ NE LÈVE AUCUNE ERREUR : `simGetRadio`
    rend `null`, et la réponse est traitée comme non donnée. Le simulateur
    continue de répondre, avec une question de moins."""
    lus = set(re.findall(r"simGetRadio\('([^']+)'\)", MOTEUR))
    lus |= set(re.findall(r"simGetCheckboxes\('([^']+)'\)", MOTEUR))
    assert lus, "plus aucun groupe n'est lu : le contrôle doit être revu"
    absents = sorted(g for g in lus if ('id="%s"' % g) not in PAGE)
    assert not absents, (
        "groupe(s) interrogé(s) par le moteur et absent(s) de la page : %s — "
        "la réponse sera silencieusement nulle" % ', '.join(absents))


def test_tout_groupe_present_dans_la_page_est_bien_relu():
    """L'inverse : une question posée à l'utilisateur mais jamais relue par le
    moteur est du travail qu'on lui demande pour rien."""
    poses = set(re.findall(r"simRadio\('([^']+)',", PAGE))
    poses |= set(re.findall(r"simCheckbox\(this,'([^']+)'\)", PAGE))
    # Les cases sont nommées par leur valeur, pas par leur groupe : on ne
    # retient ici que les groupes de boutons radio.
    poses = {g for g in poses if g.startswith('r-')}
    lus = set(re.findall(r"simGetRadio\('([^']+)'\)", MOTEUR))
    orphelins = sorted(poses - lus)
    assert not orphelins, (
        "question(s) posée(s) dans le simulateur et jamais relue(s) par le "
        "moteur : %s" % ', '.join(orphelins))


def test_le_role_est_releve_a_l_etape_1():
    d = MOTEUR.index('window.simNext = function(from){')
    corps = MOTEUR[d:MOTEUR.index('window.simPrev', d)]
    for champ in ('role', 'art25', 'fria', 'definition', 'anteriorite'):
        assert ('SIM_DATA.' + champ) in corps, (
            "SIM_DATA.%s n'est plus relevé à la validation d'une étape : la "
            "question reste posée à l'écran mais sa réponse est perdue" % champ)
