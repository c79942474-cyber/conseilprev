"""SENTINEL APPLIQUAIT LE RÈGLEMENT DE 2024, PAS CELUI QUI EST EN VIGUEUR DEPUIS LE 27 JUILLET 2026.

CE QUI A ÉTÉ TROUVÉ, LE 29 SEPTEMBRE 2026. L'infographie « AI Act — Comprendre
les règles, maîtriser les usages » (repères au 28 septembre 2026, après
l'Omnibus IA) a été confrontée, article par article, au texte du règlement (UE)
2024/1689 et à celui du règlement (UE) 2026/1744 qui le modifie, puis à
Sentinel. Ce que l'analyse de risque d'un système d'IA rendait :

  — DES DIX PRATIQUES INTERDITES DE L'ARTICLE 5(1), DEUX ÉTAIENT POSÉES. La
    manipulation (a) et l'identification biométrique en temps réel (h). La
    notation sociale, la reconnaissance des émotions au travail, le moissonnage
    de visages, la catégorisation biométrique sortaient « haut risque » ou
    « minimal » — jamais « interdit » — et les deux pratiques ajoutées au
    2 décembre 2026 (hypertrucages sexuels sans consentement, matériel d'abus
    sexuel d'enfants) n'existaient pas. L'identification biométrique à distance
    était interdite d'office, alors que le point (h) ne vise que l'usage
    répressif ;
  — LE SECTEUR SUFFISAIT À RENDRE UN SYSTÈME « HAUT RISQUE », alors que
    l'annexe III liste des USAGES : un système de paie n'est pas à haut risque
    parce qu'il sert dans l'emploi ;
  — LES PRODUITS DE L'ANNEXE I ET LE CHAMP DE L'ARTICLE 2 N'ÉTAIENT PAS
    INTERROGÉS : impossible de sortir du champ (militaire, recherche, usage
    personnel), impossible d'être classé par l'article 6(1) ;
  — LES OBLIGATIONS DATAIENT : l'article 4 (« niveau suffisant de maîtrise »)
    a été remplacé par une obligation de moyens sans niveau garanti ; l'article
    10(5) est supprimé au profit de l'article 4a ; l'article 50 était partagé
    en deux lignes qui attribuaient au marquage le §4, devoir du déployeur, et
    omettaient le §3 ; l'article 25(2) et (4) n'apparaissait pas ;
  — LE CALENDRIER : la fiche de l'article annonçait « Applicable août 2026 »
    pour le haut risque ; la feuille de route affichait « 02 AOÛT 2026 — haut
    risque » à côté d'un libellé qui disait « 2 décembre 2027 » ; le statut
    « prochain » de la ligne du 2 août 2026 restait affiché deux mois après son
    échéance ; les deux dates du 2 décembre 2026 et du 2 août 2027 manquaient.

CE QUE CES RÈGLES GARDENT. Elles EXÉCUTENT le vrai code — la classification, le
calcul d'écart, le périmètre, la frise, les statuts du calendrier — dans Node,
sur des réponses fabriquées, et comparent ce qui sort au texte des deux
règlements. Une règle qui chercherait « Art. 4a » dans la source serait
satisfaite par un commentaire ; celles-ci exigent que l'article sorte du moteur
pour le bon rôle, et pas pour l'autre.

CE QU'ELLES NE PEUVENT PAS FAIRE. Dire qu'une classification est juridiquement
juste pour un cas réel : elles vérifient que le moteur suit le TEXTE, pas qu'une
organisation a répondu vrai. Ni prouver qu'aucune autre prescription du
règlement ne manque : la matrice des écarts dresse la liste de ce qui a été
confronté, pas de ce qui ne l'a pas été.
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)
MOTEUR = io.open(os.path.join(ICI, 'sentinel.page.js'), encoding='utf-8').read()
PAGE = io.open(os.path.join(ICI, 'sentinel.html'), encoding='utf-8').read()
NODE = shutil.which('node')

DEBUT_MOTEUR = 'function simEtatAudit(numero){'
FIN_MOTEUR = 'function simTimeline(classif){'
DEBUT_SANCTIONS = 'var AI_ACT_SANCTIONS = {'
FIN_SANCTIONS = '/* ══ FIN SANCTIONS — SOURCE UNIQUE ══ */'
DEBUT_CALENDRIER = 'var AI_ACT_TIMELINE = ['
FIN_CALENDRIER = 'window.aiActProchaine = aiActProchaine;'


def _tranche(debut, fin, repli_fin=None):
    """Une tranche du moteur, ou rien du tout : sans son ancre, chaque règle tombe sur SON constat
    (la fonction n'existe pas, ou elle rend faux), pas sur une erreur d'import qui les emporterait
    toutes d'un bloc. `repli_fin` : la fin d'une version antérieure du même bloc."""
    if debut not in MOTEUR:
        return ''
    d = MOTEUR.index(debut)
    if fin == FIN_CALENDRIER:
        if fin in MOTEUR[d:]:
            return MOTEUR[d:MOTEUR.index(fin, d) + len(fin)]
        return MOTEUR[d:MOTEUR.index(repli_fin, d) + len(repli_fin)] if repli_fin else ''
    return MOTEUR[d:MOTEUR.index(fin, d)]


def _simtimeline():
    d = MOTEUR.index(FIN_MOTEUR)
    return MOTEUR[d:MOTEUR.index('\n}', d) + 2]


SANCTIONS = _tranche(DEBUT_SANCTIONS, FIN_SANCTIONS)
MOTEUR_SIM = _tranche(DEBUT_MOTEUR, FIN_MOTEUR)
CALENDRIER = _tranche(DEBUT_CALENDRIER, FIN_CALENDRIER, 'window.AI_ACT_TIMELINE = AI_ACT_TIMELINE;')


def _node(corps, avec_calendrier=False, avec_timeline=False, avant=''):
    """Exécute `corps` dans le moteur réel : sanctions, simulateur, et à la demande le
    calendrier et la frise. Rend le JSON écrit sur la sortie standard."""
    if not NODE:
        pytest.skip('node absent : le moteur du simulateur ne peut pas être exécuté')
    prog = ['var window = {};', avant, SANCTIONS, 'var SIM_DATA = {};', MOTEUR_SIM]
    if avec_calendrier or avec_timeline:
        prog.append(CALENDRIER)
    if avec_timeline:
        prog.append(_simtimeline())
    prog.append(corps)
    r = subprocess.run([NODE, '-e', '\n'.join(prog)], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        pytest.fail("le moteur ne s'exécute pas :\n%s" % (r.stderr or '')[-1800:])
    return json.loads(r.stdout.strip())


def _classer(cas):
    """simClassify sur une liste de réponses. Rend la liste des résultats."""
    return _node('var cas = %s;\nconsole.log(JSON.stringify(cas.map(function(c){ SIM_DATA = c; return simClassify(); })));'
                 % json.dumps(cas))


def _un(**reponses):
    return _classer([reponses])[0]


# ── 1. LES DIX PRATIQUES INTERDITES ─────────────────────────────────────────

POINTS_PAR_REPONSE = [
    ('a',  {'subliminal': 'oui'}),
    ('b',  {'art5': ['art5-b']}),
    ('c',  {'art5': ['art5-c']}),
    ('d',  {'art5': ['art5-d']}),
    ('e',  {'art5': ['art5-e']}),
    ('f',  {'art5': ['art5-f']}),
    ('g',  {'art5': ['art5-g']}),
    ('h',  {'biometrie': 'oui'}),
    ('ba', {'art5': ['art5-ba']}),
    ('bb', {'art5': ['art5-bb']}),
]


def test_chacune_des_dix_pratiques_de_l_article_5_rend_un_systeme_interdit():
    """LE DÉFAUT CENTRAL : huit pratiques sur dix ne pouvaient pas produire « interdit »."""
    res = _classer([dict({'secteur': 'autre', 'type': 'reco'}, **rep) for _p, rep in POINTS_PAR_REPONSE])
    fautes = []
    for (p, _rep), r in zip(POINTS_PAR_REPONSE, res):
        if r['level'] != 'interdit' or r['art5_points'] != [p]:
            fautes.append('point %s : niveau %s, points %s' % (p, r['level'], r.get('art5_points')))
        if not r['art5'] or r['badge'] != 'PRATIQUE INTERDITE':
            fautes.append('point %s : art5=%s badge=%s' % (p, r['art5'], r['badge']))
    assert not fautes, "pratique non reconnue :\n  - " + "\n  - ".join(fautes)


def test_plusieurs_pratiques_sont_rendues_dans_l_ordre_du_texte_et_le_sanction_est_celle_du_paragraphe_3():
    r = _un(secteur='autre', type='reco', subliminal='oui', art5=['art5-ba', 'art5-c', 'art5-e'])
    assert r['art5_points'] == ['a', 'c', 'e', 'ba'], r['art5_points']
    assert r['sanctions']['art'] == 'Art. 99(3)' and r['score'] == 10.0
    assert 'points a, c, e, ba' in r['article'], r['article']


def test_sans_reponse_aucune_pratique_n_est_reconnue():
    r = _un(secteur='autre', type='reco', art5=[])
    assert r['level'] == 'minimal' and r['art5'] is False and 'art5_points' not in r


def test_la_reconnaissance_des_emotions_au_travail_ou_a_l_ecole_est_interdite_sauf_raison_medicale_ou_de_securite():
    """Le point (f). Le type « émotion » dans l'emploi ou l'éducation suffit, sans
    case cochée — et l'exception médicale ou de sécurité est la seule qui la lève."""
    res = _classer([
        {'type': 'emotion', 'secteur': 'emploi'},
        {'type': 'emotion', 'secteur': 'education'},
        {'type': 'emotion', 'secteur': 'emploi', 'art5': ['art5-f-exception']},
        {'type': 'emotion', 'secteur': 'finance'},
        {'type': 'reco', 'secteur': 'emploi', 'art5': ['art5-f', 'art5-f-exception']},
    ])
    niveaux = [r['level'] for r in res]
    assert niveaux[0] == 'interdit' and res[0]['art5_points'] == ['f'], res[0]
    assert niveaux[1] == 'interdit', res[1]
    assert niveaux[2] == 'haut', ("avec l'exception médicale ou de sécurité, ce n'est plus interdit "
                                  "mais reste à haut risque (annexe III, point 1(c)) : %s" % res[2])
    assert niveaux[3] == 'haut', "hors travail et enseignement, l'émotion est à haut risque, pas interdite"
    assert niveaux[4] != 'interdit', "l'exception cochée lève le point (f)"


def test_l_identification_biometrique_en_temps_reel_n_est_interdite_que_si_elle_est_repressive():
    """LE POINT (h) NE VISE QUE L'USAGE RÉPRESSIF. Le simulateur interdisait d'office tout système
    de ce type ; un usage privé est à haut risque (annexe III, point 1(a)), pas interdit."""
    res = _classer([
        {'biometrie': 'oui'},
        {'biometrie': 'oui_autre'},
        {'type': 'bio_remote', 'biometrie': 'oui_autre'},
        {'type': 'bio_remote'},
        {'type': 'bio_remote', 'biometrie': 'non'},
    ])
    assert res[0]['level'] == 'interdit' and res[0]['art5_points'] == ['h']
    assert res[1]['level'] == 'haut', "temps réel sans finalité répressive : haut risque, pas interdit — %s" % res[1]
    assert res[2]['level'] == 'haut' and 'a_confirmer' not in res[2], res[2]
    assert res[3]['level'] == 'haut' and res[3]['a_confirmer'] == 'bio_remote', (
        "le type seul ne tranche pas : haut risque PRÉSUMÉ, finalité à confirmer — %s" % res[3])
    assert res[4]['level'] == 'haut'


def test_les_deux_nouvelles_pratiques_sont_datees_par_le_calendrier_et_pas_par_le_simulateur():
    """Les points ba et bb s'appliquent à compter du 2 décembre 2026. Le verdict est « interdit » ;
    la date d'effet vient de la ligne `interdictions_2026` du calendrier consolidé."""
    cal = _node('console.log(JSON.stringify(AI_ACT_TIMELINE.filter(function(r){ return r.cle === "interdictions_2026"; })));',
                avec_calendrier=True)
    assert len(cal) == 1 and cal[0]['date'] == '2 décembre 2026' and cal[0]['iso'] == '2026-12-02', cal
    assert 'points ba et bb' in cal[0]['quoi']


# ── 2. LE SECTEUR NE SUFFIT PAS : L'ANNEXE III LISTE DES USAGES ─────────────

def test_un_usage_coche_de_l_annexe_iii_est_un_constat_le_secteur_seul_est_une_presomption():
    res = _classer([
        {'secteur': 'emploi', 'type': 'aide_decision', 'annexe3': ['annexe3-emploi']},
        {'secteur': 'emploi', 'type': 'aide_decision'},
        {'secteur': 'autre', 'type': 'aide_decision'},
        {'secteur': 'autre', 'type': 'aide_decision', 'annexe3': ['annexe3-law']},
    ])
    assert res[0]['level'] == 'haut' and 'a_confirmer' not in res[0], "usage coché : constat — %s" % res[0]
    assert res[1]['level'] == 'haut' and res[1]['a_confirmer'] == 'usage', (
        "le secteur seul reste une PRÉSOMPTION conservatrice, mais elle doit être dite « à confirmer » : %s" % res[1])
    assert res[2]['level'] == 'minimal'
    assert res[3]['level'] == 'haut' and 'a_confirmer' not in res[3]


def test_l_exception_de_l_article_6_3_leve_le_haut_risque_sauf_profilage():
    res = _classer([
        {'secteur': 'emploi', 'annexe3': ['annexe3-emploi'], 'exception6_3': 'preparatoire', 'profilage': 'non'},
        {'secteur': 'emploi', 'annexe3': ['annexe3-emploi'], 'exception6_3': 'preparatoire', 'profilage': 'oui'},
        {'secteur': 'emploi', 'annexe3': ['annexe3-emploi'], 'exception6_3': 'aucune'},
        {'secteur': 'emploi', 'exception6_3': 'detection', 'profilage': 'non'},
    ])
    assert res[0]['level'] != 'haut' and 'Art. 6(3)' in res[0]['exception_note'], res[0]
    note = res[0]['exception_note']
    assert 'Art. 6(4)' in note and 'avant mise sur le marché' in note, "l'évaluation se documente AVANT la mise sur le marché : " + note
    assert 'Art. 49(2)' in note and 'points 7 et 9' in note, "l'enregistrement reste dû, allégé par l'Omnibus (annexe VIII, section B) : " + note
    assert res[1]['level'] == 'haut', "le profilage de personnes physiques annule l'exception (6(3), dernier alinéa)"
    assert res[2]['level'] == 'haut'
    assert res[3]['level'] != 'haut', "secteur seul + exception applicable : pas de haut risque"


def test_la_voie_du_haut_risque_est_nommee_pour_souligner_la_bonne_ligne_du_calendrier():
    res = _classer([
        {'annexe3': ['annexe3-emploi']},
        {'annexe1': 'oui_tiers'},
        {'annexe3': ['annexe3-emploi'], 'annexe1': 'oui_tiers'},
    ])
    assert res[0]['haut_via'] == ['annexe3']
    assert res[1]['haut_via'] == ['annexe1']
    assert res[2]['haut_via'] == ['annexe3', 'annexe1']


# ── 3. L'ANNEXE I : COMPOSANT DE SÉCURITÉ ET ÉVALUATION PAR UN TIERS ────────

def test_un_produit_de_l_annexe_i_a_evaluation_par_un_tiers_est_a_haut_risque_au_titre_de_l_article_6_1():
    r = _un(annexe1='oui_tiers')
    assert r['level'] == 'haut' and r['article'] == 'Art. 6(1) + Annexe I', r['article']
    assert 'Art. 2(13)' in r['annexe1_note'] and '2 août 2027' in r['annexe1_note'], r['annexe1_note']


def test_les_quatre_autres_reponses_sur_l_annexe_i_ne_rendent_pas_le_systeme_haut_risque_et_disent_pourquoi():
    res = _classer([{'annexe1': v} for v in ('oui_sans_tiers', 'fonction_non_securite', 'machines', 'non')])
    for r in res:
        assert r['level'] != 'haut', r
    assert '6(1)(b)' in res[0]['annexe1_note'] and '6(1c)' in res[0]['annexe1_note']
    assert '6(1a)' in res[1]['annexe1_note'] and '6(1b)' in res[1]['annexe1_note']
    assert '2023/1230' in res[2]['annexe1_note'] and 'section B' in res[2]['annexe1_note'] and 'Art. 2(2)' in res[2]['annexe1_note']
    assert 'annexe1_note' not in res[3]


# ── 4. LE CHAMP DU RÈGLEMENT : L'ARTICLE 2 ──────────────────────────────────

def _perimetre(cas):
    return _node('var cas = %s;\nconsole.log(JSON.stringify(cas.map(function(c){ SIM_DATA = c; return simPerimetre(); })));'
                 % json.dumps(cas))


def test_chaque_exclusion_de_l_article_2_sort_du_champ_avec_son_article():
    cas = [{'perimetre': [c], 'role': 'fournisseur'} for c in ('per-militaire', 'per-recherche', 'per-avantmarche')]
    res = _perimetre(cas)
    assert [r['statut'] for r in res] == ['hors_champ'] * 3, res
    assert [r['motifs'][0]['art'] for r in res] == ['Art. 2(3)', 'Art. 2(6)', 'Art. 2(8)']


def test_aucune_case_cochee_c_est_dans_le_champ():
    """Ce sont des exceptions, pas des questions : ne rien cocher ne doit jamais sortir du champ."""
    res = _perimetre([{}, {'perimetre': []}])
    assert [r['statut'] for r in res] == ['dans_le_champ'] * 2


def test_l_usage_personnel_ne_libere_que_les_deployeurs():
    """L'article 2(10) ne vise que les OBLIGATIONS DES DÉPLOYEURS personnes physiques."""
    res = _perimetre([{'perimetre': ['per-personnel'], 'role': 'deployeur'},
                      {'perimetre': ['per-personnel'], 'role': 'fournisseur'},
                      {'perimetre': ['per-personnel'], 'role': 'indetermine'}])
    assert res[0]['statut'] == 'hors_champ' and res[0]['motifs'][0]['art'] == 'Art. 2(10)'
    assert res[1]['statut'] == 'dans_le_champ' and res[1]['ecartes'][0]['art'] == 'Art. 2(10)', res[1]
    assert 'DÉPLOYEURS' in res[1]['ecartes'][0]['motif']
    assert res[2]['statut'] == 'hors_champ'


# ── 5. LES OBLIGATIONS À JOUR ───────────────────────────────────────────────

def _gap(cas):
    """simGap pour chaque (réponses, classification). Rend, pour chacun, {id: obligation}."""
    prog = ('var cas = %s;\nconsole.log(JSON.stringify(cas.map(function(c){ SIM_DATA = c[0]; '
            'var o = {}; simGap(c[1]).forEach(function(x){ o[x.obl.id] = x.obl; }); return o; })));'
            % json.dumps(cas))
    return _node(prog)


H = {'level': 'haut', 'art5': False, 'extra_territorial': False}
L = {'level': 'limite', 'art5': False, 'extra_territorial': False}
M = {'level': 'minimal', 'art5': False, 'extra_territorial': False}
I = {'level': 'interdit', 'art5': True, 'extra_territorial': False}


def test_l_article_4_est_une_obligation_de_moyens_sans_niveau_garanti():
    """Le règlement (UE) 2026/1744 a REMPLACÉ l'article 4 : les fournisseurs et déployeurs prennent des
    mesures pour soutenir la culture de l'IA ; l'obligation ne garantit aucun niveau précis."""
    o = _gap([[{'role': 'deployeur'}, M]])[0]['art4']
    assert 'ne garantit pas' in o['desc'] and 'moyens' in o['desc'], o['desc']
    assert 'Niveau suffisant' not in o['desc'] and 'Niveau suffisant' not in o['name']
    assert '2026/1744' in o['desc']
    assert o['name'].startswith('Culture de l')


def test_l_article_10_renvoie_a_l_article_4a_qui_remplace_l_ancien_10_5():
    o = _gap([[{'role': 'fournisseur'}, H]])[0]['art10']
    assert o['refs'] == ['Art. 10', 'Art. 4a'], o['refs']
    assert "4a" in o['desc'] and "10(5)" in o['desc'] and 'remplace' in o['desc']


def test_les_allegements_pme_et_petites_capitalisations_sont_dits_a_l_endroit_ou_ils_jouent():
    g = _gap([[{'role': 'fournisseur'}, H]])[0]
    assert 'formulaire simplifié' in g['art11']['desc'] and 'petites capitalisations' in g['art11']['desc']
    assert 'proportionnée' in g['art17']['desc'] and 'Art. 63' in g['art17']['desc']


def test_l_article_50_se_partage_entre_le_fournisseur_et_le_deployeur_paragraphe_par_paragraphe():
    """Le fournisseur doit les §1 et §2, le déployeur les §3 et §4. Le simulateur attribuait le §4 au
    marquage et omettait le §3."""
    cas = [
        [{'role': 'fournisseur', 'interaction': 'oui'}, L],
        [{'role': 'fournisseur', 'interaction': 'genere'}, L],
        [{'role': 'deployeur', 'interaction': 'genere'}, L],
        [{'role': 'deployeur', 'type': 'emotion', 'secteur': 'finance'}, H],
        [{'role': 'indetermine', 'interaction': 'genere', 'type': 'emotion'}, H],
        [{'role': 'importateur', 'interaction': 'genere'}, L],
        [{'role': 'fournisseur', 'interaction': 'genere'}, I],
        [{'role': 'fournisseur', 'type': 'chatbot'}, L],
        [{'role': 'deployeur', 'interaction': 'oui'}, L],
        [{'role': 'deployeur', 'type': 'deepfake'}, L],
        [{'role': 'fournisseur', 'type': 'copilot'}, L],
        [{'role': 'deployeur', 'type': 'face_reco'}, H],
    ]
    g = [set(x) for x in _gap(cas)]
    art50 = lambda s: sorted(k for k in s if k.startswith('art50_'))
    assert art50(g[0]) == ['art50_chat'], art50(g[0])
    assert art50(g[1]) == ['art50_marquage'], art50(g[1])
    assert art50(g[2]) == ['art50_hypertrucage'], "le §4 est un devoir du DÉPLOYEUR : %s" % art50(g[2])
    assert 'art50_emotion' in g[3] and 'art50_chat' not in g[3], art50(g[3])
    assert art50(g[4]) == ['art50_emotion', 'art50_hypertrucage', 'art50_marquage'], art50(g[4])
    assert art50(g[5]) == [], "un importateur n'a pas de devoir propre au titre de l'article 50"
    assert art50(g[6]) == [], "un système interdit n'a pas d'obligation de transparence à remplir"
    assert art50(g[7]) == ['art50_chat'], "le type « chatbot » suffit, sans réponse à la question d'interaction"
    assert art50(g[8]) == [], "l'information du §1 est un devoir du fournisseur"
    assert art50(g[9]) == ['art50_hypertrucage'], "le type « deepfake » déclenche le §4 du déployeur : %s" % art50(g[9])
    assert art50(g[10]) == ['art50_chat'], "le type « copilote » interagit avec des personnes (§1)"
    assert art50(g[11]) == ['art50_emotion'], "la catégorisation biométrique relève du §3 : %s" % art50(g[11])


def test_le_marquage_dit_le_delai_du_2_decembre_2026_pour_les_systemes_deja_commercialises():
    o = _gap([[{'role': 'fournisseur', 'interaction': 'genere'}, L]])[0]['art50_marquage']
    assert 'Art. 111(4)' in o['refs'] and '2 décembre 2026' in o['desc'] and '2 août 2026' in o['desc'], o
    assert 'aucune mention visible' in o['desc'], "le §2 n'impose aucune mention visible au fournisseur"


def test_l_article_25_2_est_du_par_le_fournisseur_initial_et_par_lui_seul():
    g = _gap([
        [{'role': 'fournisseur', 'art25_amont': 'oui'}, M],
        [{'role': 'fournisseur', 'art25_amont': 'non'}, M],
        [{'role': 'deployeur', 'art25_amont': 'oui'}, M],
        [{'role': 'fournisseur', 'art25_amont': 'oui'}, I],
        [{'role': 'fournisseur'}, M],
    ])
    assert 'art25_2' in g[0] and g[0]['art25_2']['refs'] == ['Art. 25(2)']
    assert 'art25_2' not in g[1] and 'art25_2' not in g[2] and 'art25_2' not in g[3]
    assert 'art25_2' not in g[4], "sans réponse, aucune obligation n'est inventée"
    d = g[0]['art25_2']['desc']
    assert 'documentation technique' in d and 'modes de défaillance' in d and 'accès technique' in d, d


def test_l_article_25_4_le_contrat_ecrit_est_du_par_le_fournisseur_d_un_systeme_a_haut_risque():
    g = _gap([[{'role': 'fournisseur'}, H], [{'role': 'deployeur'}, H], [{'role': 'fournisseur'}, L]])
    assert 'art25_4' in g[0] and g[0]['art25_4']['refs'] == ['Art. 25(4)']
    assert 'licence libre et ouverte' in g[0]['art25_4']['desc']
    assert 'art25_4' not in g[1] and 'art25_4' not in g[2]


def test_l_article_26_8_ne_vise_que_les_autorites_publiques_deployeuses():
    g = _gap([[{'role': 'deployeur', 'fria': 'public'}, H],
              [{'role': 'deployeur', 'fria': 'credit_assurance'}, H],
              [{'role': 'deployeur', 'fria': 'service_public'}, H]])
    assert 'art26_registre' in g[0] and 'Art. 26(8)' in g[0]['art26_registre']['refs']
    assert 'art26_registre' not in g[1] and 'art26_registre' not in g[2]


def test_l_incident_grave_se_signale_dans_l_ordre_du_26_5():
    o = _gap([[{'role': 'deployeur'}, H]])[0]['art26_surveillance']
    d = o['desc']
    assert "fournisseur d'abord" in d and 'importateur ou du distributeur' in d and 'article 73' in d, d
    assert o['refs'] == ['Art. 26(5)', 'Art. 73'], o['refs']


def test_l_aidf_peut_renvoyer_a_l_analyse_d_impact_rgpd_et_l_aipd_cite_le_bon_article():
    g = _gap([[{'role': 'deployeur', 'fria': 'public', 'rgpd': 'sensibles'}, H]])[0]
    assert '27(4)' in g['art27']['desc']
    assert g['aipd']['refs'] == ['RGPD Art. 35', 'AI Act Art. 26(9)'], g['aipd']['refs']


# ── 6. LA FRISE ET LE CALENDRIER ────────────────────────────────────────────

def _calendrier(corps, avant=''):
    return _node(corps, avec_calendrier=True, avant=avant)


def test_le_calendrier_est_ordonne_a_des_dates_iso_uniques_et_chaque_ligne_porte_une_cle():
    rows = _calendrier('console.log(JSON.stringify(AI_ACT_TIMELINE));')
    isos = [r['iso'] for r in rows]
    assert isos == sorted(isos) and len(set(isos)) == len(isos), isos
    cles = [r['cle'] for r in rows]
    assert len(set(cles)) == len(cles) and all(cles), cles
    for attendu in ('interdictions', 'transparence', 'interdictions_2026', 'gpai_herites', 'annexe3', 'annexe1'):
        assert attendu in cles, attendu
    assert all(re.match(r'^\d{4}-\d{2}-\d{2}$', i) for i in isos)


def test_les_lignes_modifiees_par_l_omnibus_le_disent():
    rows = {r['cle']: r for r in _calendrier('console.log(JSON.stringify(AI_ACT_TIMELINE));')}
    for cle in ('interdictions_2026', 'annexe3', 'annexe1'):
        assert '2026/1744' in rows[cle]['ref'], (cle, rows[cle]['ref'])
    assert rows['gpai_herites']['date'] == '2 août 2027' and 'Art. 111(3)' in rows['gpai_herites']['ref']


def test_l_exemple_des_machines_a_quitte_la_ligne_de_l_annexe_i():
    """Le règlement Machines est passé de la section A à la section B de l'annexe I : il n'est plus l'exemple
    d'un système à haut risque intégré à un produit."""
    r = {x['cle']: x for x in _calendrier('console.log(JSON.stringify(AI_ACT_TIMELINE));')}['annexe1']
    assert 'machines' not in r['quoi'].lower() and 'section A' in r['quoi'], r['quoi']
    assert 'section B' in r['retenir'] and '2023/1230' in r['retenir'], r['retenir']


def test_le_statut_se_lit_dans_la_date_et_jamais_dans_une_etiquette():
    """La ligne du 2 août 2026 restait « prochaine » deux mois après son échéance."""
    def statuts(jour):
        rows = _calendrier('aiActStatuts(AI_ACT_TIMELINE, %s);\nconsole.log(JSON.stringify(AI_ACT_TIMELINE));' % json.dumps(jour))
        return {r['cle']: r['statut'] for r in rows}
    aujourdhui = statuts('2026-09-29')
    assert aujourdhui['transparence'] == 'passe', aujourdhui
    assert aujourdhui['interdictions_2026'] == 'prochain', aujourdhui
    assert aujourdhui['gpai_herites'] == aujourdhui['annexe3'] == aujourdhui['annexe1'] == 'futur'
    avant = statuts('2026-07-01')
    assert avant['transparence'] == 'prochain' and avant['interdictions_2026'] == 'futur', avant
    assert list(statuts('2029-01-01').values()) == ['passe'] * 8
    le_jour = statuts('2026-12-02')
    assert le_jour['interdictions_2026'] == 'passe' and le_jour['gpai_herites'] == 'prochain', le_jour
    for jour in ('2024-01-01', '2026-09-29', '2027-06-01'):
        assert list(statuts(jour).values()).count('prochain') <= 1


def test_le_statut_est_calcule_au_chargement_d_apres_la_date_du_jour_et_non_ecrit_a_la_main():
    """Le calendrier se charge avec la date du jour : ici, une horloge figée au 29 septembre 2026, puis au
    1er juillet 2026. Sans le calcul au chargement, les étiquettes écrites à la main resteraient."""
    def charger(jour):
        horloge = "var __D = Date; Date = function(){ return new __D('%sT12:00:00Z'); };" % jour
        prog = "console.log(JSON.stringify(AI_ACT_TIMELINE.map(function(r){ return [r.cle, r.statut]; })));"
        return dict(_calendrier(prog, avant=horloge))
    a = charger('2026-09-29')
    assert a['transparence'] == 'passe' and a['interdictions_2026'] == 'prochain', a
    b = charger('2026-07-01')
    assert b['transparence'] == 'prochain' and b['interdictions_2026'] == 'futur', b


def test_la_date_affichee_de_chaque_ligne_est_celle_de_sa_date_iso():
    mois = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
    for r in _calendrier('console.log(JSON.stringify(AI_ACT_TIMELINE));'):
        y, m, d = (int(x) for x in r['iso'].split('-'))
        attendu = '%s %s %d' % ('1er' if d == 1 else str(d), mois[m - 1], y)
        assert r['date'] == attendu, "la ligne %s affiche « %s » pour la date %s" % (r['cle'], r['date'], r['iso'])


def test_la_prochaine_echeance_et_l_echeance_d_une_cle_se_lisent_dans_le_calendrier():
    prog = ("aiActStatuts(AI_ACT_TIMELINE, '2026-09-29');\n"
            "console.log(JSON.stringify({ prochaine: window.aiActProchaine().date, annexe3: window.aiActEcheance('annexe3').date,"
            " inconnue: window.aiActEcheance('nexiste-pas') }));")
    r = _calendrier(prog)
    assert r == {'prochaine': '2 décembre 2026', 'annexe3': '2 décembre 2027', 'inconnue': None}, r


def test_l_etiquette_d_une_fiche_derive_du_calendrier_ou_de_la_fiche_elle_meme():
    """Elle disait « Applicable août 2026 » pour tout le haut risque, et « Applicable 2027 » pour un
    article du CRA qui s'applique depuis le 11 septembre 2026."""
    prog = ("var r = [aiActStatutArticle({status:'applicable'}, {}), aiActStatutArticle({status:'applicable'}, {reglement:'ai_act'}),"
            " aiActStatutArticle({status:'futur', statut_txt:'Applicable 11 septembre 2026'}, {reglement:'cra'}),"
            " aiActStatutArticle({status:'actif'}, {}), aiActStatutArticle({status:'futur'}, {reglement:'cra'})];\n"
            "console.log(JSON.stringify(r));")
    a, b, c, d, e = _calendrier(prog)
    assert '2 décembre 2027' in a and '2 août 2028' in a and 'août 2026' not in a, a
    assert a == b
    assert c == 'Applicable 11 septembre 2026'
    assert d == 'Applicable' and e == 'À venir'


def _frise(classif):
    prog = ("aiActStatuts(AI_ACT_TIMELINE, '2026-09-29');\nwindow = {AI_ACT_TIMELINE: AI_ACT_TIMELINE};\n"
            "console.log(JSON.stringify(simTimeline(%s).filter(function(x){ return x.urgent; }).map(function(x){ return x.date; })));"
            % json.dumps(classif))
    return _node(prog, avec_timeline=True)


def test_la_frise_souligne_la_ligne_du_systeme_analyse_et_elle_seule():
    assert _frise({'level': 'interdit', 'art5': True}) == ['2 février 2025'], "sans point nommé : la ligne de l'ancien régime"
    assert _frise({'level': 'interdit', 'art5': True, 'art5_points': ['c']}) == ['2 février 2025']
    assert _frise({'level': 'interdit', 'art5': True, 'art5_points': ['ba']}) == ['2 décembre 2026']
    assert _frise({'level': 'interdit', 'art5': True, 'art5_points': ['c', 'bb']}) == ['2 février 2025', '2 décembre 2026']
    assert _frise({'level': 'haut', 'haut_via': ['annexe1']}) == ['2 août 2028']
    assert _frise({'level': 'haut', 'haut_via': ['annexe3', 'annexe1']}) == ['2 décembre 2027', '2 août 2028']
    assert _frise({'level': 'haut'}) == ['2 décembre 2027'], "sans voie nommée, l'annexe III reste la lecture par défaut"
    assert _frise({'level': 'limite'}) == ['2 août 2026']
    assert _frise({'level': 'minimal'}) == []


# ── 7. LA FEUILLE DE ROUTE LIT LE CALENDRIER ────────────────────────────────

def _carte_feuille_de_route(retouche=''):
    """Exécute le vrai fragment de `roadmapRenderPage` qui peint la carte de la prochaine échéance, sur un
    calendrier dont on peut retoucher les lignes (`retouche` : du JavaScript, joué après le calcul des statuts)."""
    d = MOTEUR.index('/* La carte lit le calendrier consolidé')
    f = MOTEUR.index('    }', MOTEUR.index('var eta = document.getElementById("road-next-deadline-bar");', d))
    f = MOTEUR.index('\n', f) + 1
    fragment = MOTEUR[d:f]
    if not NODE:
        pytest.skip('node absent')
    prog = ("var window = {};\n%s\naiActStatuts(AI_ACT_TIMELINE, '2026-09-29');\n%s\n"
            "var dashboard = {auditPct: 40};\nvar d = dashboard;\n"
            "var __el = {};\nvar document = { getElementById: function(id){ return __el[id] || (__el[id] = { style:{}, textContent:'' }); } };\n"
            "%s\nconsole.log(JSON.stringify({date: __el['road-next-deadline-date'].textContent, titre: __el['road-next-deadline-title'].textContent,"
            " sous: __el['road-next-deadline-sub'].textContent, barre: __el['road-next-deadline-bar'].style.width,"
            " libelle: __el['road-next-deadline-lbl'].textContent, e3: aiActEcheance('annexe3')}));"
            % (CALENDRIER, retouche, fragment))
    r = subprocess.run([NODE, '-e', prog], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-1000:]
    return json.loads(r.stdout)


def test_la_carte_de_la_feuille_de_route_lit_le_calendrier_au_lieu_de_porter_sa_propre_date():
    """La carte annonçait « 02 AOÛT 2026 — haut risque » pendant que son libellé disait « 2 décembre 2027 »."""
    out = _carte_feuille_de_route()
    assert out['date'] == '2 DÉCEMBRE 2026', out
    assert 'points ba et bb' in out['titre'] and '2026/1744' in out['sous'], out
    assert out['barre'] == '40%'
    assert '40%' in out['libelle'] and '2 décembre 2027' in out['libelle'], out['libelle']
    assert out['libelle'].endswith('échéance %s (%s)' % (out['e3']['date'], out['e3']['ref'])), \
        "le libellé porte la date ET la référence de la ligne de l'annexe III : " + out['libelle']
    # Et elle SUIT le calendrier : on change les lignes, la carte change avec elles.
    out = _carte_feuille_de_route("var _p = aiActProchaine(); _p.date = 'date-test'; _p.quoi = 'quoi-test'; _p.ref = 'ref-test';"
                                  " var _e = aiActEcheance('annexe3'); _e.date = 'D-TEST'; _e.ref = 'R-TEST';")
    assert (out['date'], out['titre'], out['sous']) == ('DATE-TEST', 'quoi-test', 'ref-test'), out
    assert out['libelle'].endswith('échéance D-TEST (R-TEST)'), out['libelle']


def test_la_carte_statique_ne_dit_plus_haut_risque_au_2_aout_2026():
    carte = PAGE[PAGE.index('Prochaine échéance critique'):PAGE.index('Résumé avancement')]
    plat = re.sub(r'<[^>]*>', ' ', carte)
    assert '02 AOÛT 2026' not in plat and 'Systèmes haut risque (Art. 113)' not in plat, plat
    for i in ('road-next-deadline-date', 'road-next-deadline-title', 'road-next-deadline-sub'):
        assert 'id="%s"' % i in carte, i


# ── 8. LES FICHES D'ARTICLE ET LES MODÈLES DE DOCUMENTS ─────────────────────

def _evaluer_tableau(nom, debut, fin):
    d = MOTEUR.index(debut)
    src = MOTEUR[d:MOTEUR.index(fin, d) + len(fin)]
    if not NODE:
        pytest.skip('node absent')
    r = subprocess.run([NODE, '-e', src + '\nconsole.log(JSON.stringify(%s));' % nom], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-800:]
    return json.loads(r.stdout)


ARTICLES = None


def _articles():
    global ARTICLES
    if ARTICLES is None:
        ARTICLES = _evaluer_tableau('ARTICLES', 'var ARTICLES = [', '\n];')
    return ARTICLES


def _fiche(num, url_suffixe):
    for ch in _articles():
        for a in ch['arts']:
            if a['num'] == num and a['url'].endswith(url_suffixe):
                return a
    pytest.fail('fiche %s introuvable' % num)


FICHES = [
    # (numéro, article de l'url, ce que la fiche DOIT dire, ce qu'elle NE DOIT PLUS dire)
    ('Art. 2', '/2/', ['militaires', "l'Art. 60a", '2(10)', 'recherche'], []),
    ('Art. 3', '/3/', ['68 points', '3(14a)', '3(14b)', 'déduit à partir des entrées'], ['65 termes', "techniques d'apprentissage automatique"]),
    ('Art. 4', '/4/', ["n'impose pas de garantir un niveau précis", 'prennent des mesures', '2026/1744'], ['doivent veiller']),
    ('Art. 5', '/5/', ['(ba)', '(bb)', 'toute entité publique ou privée', '2 décembre 2026', 'uniquement sur le profilage'],
     ['notation sociale par autorités publiques']),
    ('Art. 6', '/6/', ['6(1a)', '6(3)', 'profilage', 'annexe I'], []),
    ('Art. 10', '/10/', ['Art. 4a', 'six garanties'], []),
    ('Art. 16', '/16/', ['12 obligations', 'points a à l'], ['10 obligations']),
    ('Art. 25', '/25/', ['25(2)', '25(4)', 'licence libre et ouverte'], []),
    ('Art. 26', '/26/', ['six mois', "d'abord le fournisseur", 'représentants des travailleurs'], []),
    ('Art. 27', '/27/', ['27(4)', 'renvoyer'], []),
    ('Art. 49', '/49/', ['Art. 6(3)', 'forme allégée'], []),
    ('Art. 50', '/50/', ['lisible par machine', 'reconnaissance des émotions', 'hypertrucage', '2 décembre 2026', '111(4)', 'volontaire'],
     ['watermarking', 'machine-readable']),
]


@pytest.mark.parametrize('num,suffixe,doit,ne_doit_pas', FICHES, ids=[f[0].replace(' ', '') + f[1].strip('/') for f in FICHES])
def test_la_fiche_de_l_article_dit_le_texte_en_vigueur(num, suffixe, doit, ne_doit_pas):
    a = _fiche(num, suffixe)
    tout = a['texte'] + ' ' + ' '.join(a['obligations']) + ' ' + str(a.get('sanction') or '')
    for s in doit:
        assert s in tout, "la fiche %s ne dit plus « %s »" % (num, s)
    for s in ne_doit_pas:
        assert s not in tout, "la fiche %s redit « %s »" % (num, s)


# Ce que le TEXTE de la fiche — son corps, pas la liste d'obligations qui le suit — doit porter lui-même. La règle
# ci-dessus lit texte + obligations + sanction : une phrase supprimée du corps mais redite dans une obligation la laisse passer.
FICHES_TEXTE = [
    ('Art. 5', '/5/', ['(ba)', '(bb)', '2026/1744', 'À compter du 2 décembre 2026']),
    ('Art. 10', '/10/', ['Art. 4a', '2026/1744', 'six garanties']),
    ('Art. 25', '/25/', ['25(2)', '25(4)', 'par écrit', 'le tiers qui lui fournit']),
    ('Art. 50', '/50/', ['(§1)', '(§2', '(§3)', '(§4)', 'Art. 111(4)']),
]


@pytest.mark.parametrize('num,suffixe,doit', FICHES_TEXTE, ids=[f[0].replace(' ', '') + f[1].strip('/') for f in FICHES_TEXTE])
def test_le_texte_de_la_fiche_porte_lui_meme_la_regle(num, suffixe, doit):
    a = _fiche(num, suffixe)
    for s in doit:
        assert s in a['texte'], "le corps de la fiche %s ne dit plus « %s »" % (num, s)


def test_l_enregistrement_est_au_chapitre_iii_et_la_transparence_a_son_chapitre_iv():
    """L'article 49 (enregistrement) et l'article 50 (transparence) étaient rangés sous « Chapitre V — GPAI »."""
    chapitres = [(c['chapter'], [a['num'] for a in c['arts']]) for c in _articles() if c.get('reglement', 'ai_act') == 'ai_act']
    par_tete = {c.split(' — ')[0]: arts for c, arts in chapitres}
    assert 'Art. 49' in par_tete['CHAPITRE III'], chapitres
    assert par_tete['CHAPITRE IV'] == ['Art. 50'], chapitres
    assert 'Art. 49' not in par_tete['CHAPITRE V'] and 'Art. 50' not in par_tete['CHAPITRE V'], chapitres


# ── LES POINTS DE L'AUDIT (34, comme avant) : ce que ceux que le règlement a fait bouger disent maintenant ──

AUDIT = None


def _points_d_audit():
    global AUDIT
    if AUDIT is None:
        AUDIT = _evaluer_tableau('AUDIT_SECTIONS', 'var AUDIT_SECTIONS = [', '\n];')
    return {it['id']: it for sec in AUDIT for it in sec['items']}


POINTS_D_AUDIT = [
    # (identifiant, ce que le point DOIT dire, ce qu'il NE DOIT PLUS dire)
    ('a5_1', ['(ba)', '(bb)', 'À compter du 2 décembre 2026', 'moissonnage', 'scoring social', 'toute entité'], ['Depuis le 2 décembre']),
    ('a5_4', ['moyens', 'ne garantit pas', '2026/1744', 'Art. 4'], ['Niveau suffisant', 'niveau suffisant']),
    ('a6_2', ['Annexe III', 'Annexe I', 'Art. 6(1)', 'composant de sécurité', 'évaluation de conformité par un tiers'], []),
    ('a9_5', ['Art. 4a', 'Art. 10(5)', 'cumulatives'], []),
    ('a11_1', ['formulaire simplifié', 'petites capitalisations intermédiaires', 'Art. 11(1)'], []),
    ('a13_2', ['§1', '§2', '§3', '§4', '2 décembre 2026', 'hypertrucages', 'Art. 50(1) à (4)'], []),
]


def test_l_audit_garde_ses_trente_quatre_points():
    assert len(_points_d_audit()) == 34


@pytest.mark.parametrize('ident,doit,ne_doit_pas', POINTS_D_AUDIT, ids=[p[0] for p in POINTS_D_AUDIT])
def test_le_point_d_audit_dit_le_texte_en_vigueur(ident, doit, ne_doit_pas):
    it = _points_d_audit()[ident]
    tout = ' '.join([it['title'], it['desc'], it.get('art') or ''])
    for x in doit:
        assert x in tout, "le point %s ne dit plus « %s » : %s" % (ident, x, tout)
    for x in ne_doit_pas:
        assert x not in tout, "le point %s redit « %s »" % (ident, x)


def test_les_fiches_du_haut_risque_portent_les_dates_du_calendrier_et_celles_du_cra_les_leurs():
    prog_src = MOTEUR[MOTEUR.index('function aiActStatutArticle(a, ch){'):MOTEUR.index('window.AI_ACT_TIMELINE = AI_ACT_TIMELINE;')]
    arts = _articles()
    etiquettes = {}
    if not NODE:
        pytest.skip('node absent')
    prog = ("var window = {};\n%s\naiActStatuts(AI_ACT_TIMELINE, '2026-09-29');\nvar ARTICLES = %s;\nvar r = {};\n"
            "ARTICLES.forEach(function(ch){ ch.arts.forEach(function(a){ r[(ch.reglement || 'ai_act') + ' ' + a.num + ' ' + a.status] = aiActStatutArticle(a, ch); }); });\n"
            "console.log(JSON.stringify(r));" % (CALENDRIER, json.dumps(arts)))
    r = subprocess.run([NODE, '-e', prog], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-800:]
    etiquettes = json.loads(r.stdout)
    for cle, txt in etiquettes.items():
        assert 'août 2026' not in txt, "%s : « %s » porte la date d'avant l'Omnibus" % (cle, txt)
    assert '2 décembre 2027' in etiquettes['ai_act Art. 9 applicable'], etiquettes['ai_act Art. 9 applicable']
    assert etiquettes['cra Art. 14 futur'] == 'Applicable 11 septembre 2026'
    assert etiquettes['cra Art. 13 applicable'] == 'Applicable 11 décembre 2027'


def test_les_modeles_de_documents_ne_citent_plus_les_references_fausses_ou_supprimees():
    """Ces listes nourrissent le prompt des documents générés pour les clients : une référence fausse s'y recopie."""
    cat = _evaluer_tableau('TMPL_CATALOG', 'var TMPL_CATALOG=[', '\n];')
    lignes = [o for m in cat for o in (m.get('oblig') or [])] + [m.get('meta', '') + ' ' + m.get('desc', '') for m in cat]
    # … et la liste des modèles que la page AFFICHE (une troisième occurrence de « août 2025 » s'y cachait)
    affiches = _evaluer_tableau('TMPL_DATA', 'var TMPL_DATA = [', '\n];')
    affiches = [m for m in affiches if m]
    assert len(affiches) > 50, len(affiches)
    lignes += [m.get('name', '') + ' ' + m.get('meta', '') + ' ' + m.get('desc', '') for m in affiches]
    tout = '\n'.join(lignes)
    interdits = [
        ('(Art. 83)', "l'article 83 est la non-conformité formelle, pas la modification substantielle (Art. 3(23), Art. 43(4))"),
        ('(Art. 10(5))', "l'article 10(5) est supprimé : c'est l'article 4a"),
        ('par autorites publiques (Art. 5(1)(c))', "la notation sociale est interdite pour toute entité, publique ou privée"),
        ('depuis le 2 aout 2025', "l'article 50 s'applique depuis le 2 août 2026"),
        ('Applicable depuis août 2025', "l'article 50 s'applique depuis le 2 août 2026"),
        ('Evaluation des 8 categories de pratiques interdites (Art. 5(1)(a)-(h))', "il y a dix pratiques, dont deux au 2 décembre 2026"),
        ('à août 2027 (systèmes existants)', "le calendrier va jusqu'à août 2028"),
    ]
    for motif, raison in interdits:
        assert motif not in tout, "« %s » est revenu : %s" % (motif, raison)
    assert 'Art. 3(23), Art. 43(4)' in tout and "l’Art. 4a" in tout and 'Art. 49 ; base de donnees : Art. 71' in tout
    assert 'a des fins repressives' in tout


# ── 9. LES AUTRES PAGES ─────────────────────────────────────────────────────

def test_la_faq_donne_les_bons_plafonds_le_calendrier_d_aujourd_hui_et_les_dix_pratiques():
    faq = io.open(os.path.join(ICI, 'faq.html'), encoding='utf-8').read()
    plat = re.sub(r'<[^>]*>', ' ', faq)
    assert '30M€ ou 6%' not in plat, "les plafonds du projet (30 M€ / 6 %) sont revenus : le règlement dit 15 M€ / 3 % et 35 M€ / 7 %"
    assert '15 M€ ou 3 % du CA mondial' in plat and '35 M€ ou 7 %' in plat
    assert 'Août 2026 : Obligations pour les systèmes à haut risque' not in plat
    for d in ('2 décembre 2026', '2 décembre 2027', '2 août 2028'):
        assert d in plat, d
    assert 'moissonnage' in plat and 'deepfakes sexuels' in plat and 'toute entité, publique ou privée' in plat
    assert 'par les gouvernements' not in plat
    assert 'risque minimal (pas d\'obligations majeures)' not in plat, "un chatbot est à risque limité (Art. 50)"


def test_le_balisage_faq_dit_ce_que_la_page_montre():
    import seo
    faq = io.open(os.path.join(ICI, 'faq.html'), encoding='utf-8').read()
    assert seo.bloc_faq_en_place(faq) == seo.jsonld_faq(faq), (
        "le JSON-LD de la FAQ n'est plus dérivé de la page : régénérer avec seo.bloc_faq")


def test_les_jalons_du_referentiel_juridique_portent_les_deux_dates_manquantes():
    import juridique
    j = ' | '.join(juridique.texte('ai-act')['jalons'])
    assert '2 décembre 2026' in j and 'points ba et bb' in j and 'Art. 111(4)' in j or 'art. 111(4)' in j
    assert '2 août 2027' in j and 'art. 111(3)' in j
    assert '2 décembre 2027' in j and '2026/1744' in j


def test_la_question_type_sur_le_scoring_ne_vise_plus_une_date_passee():
    import juridique
    qs = [x['q'] for x in juridique.SUGGESTIONS_ARBITRAGE if x['groupe'] == 'IA']
    assert qs and all('avant le 2 août 2026' not in q for q in qs), qs
    assert any('2 décembre 2027' in q for q in qs), qs


def test_le_compte_a_rebours_de_l_article_50_vise_la_prochaine_echeance_legale():
    """Il visait le 2 août 2026 en dur : deux mois après, « Échéance dépassée » alors qu'une échéance
    légale restait à venir. Et le 2 février 2027 est la date du CODE de bonnes pratiques, pas du règlement."""
    os.environ.setdefault('AUTH_MASTER_TOKEN', 'recette_locale_idf_0123456789abcdef')
    import datetime
    import app as application
    f = application.ia50_prochaine_echeance
    assert f(datetime.datetime(2026, 9, 29))['date'] == '2026-12-02'
    assert f(datetime.datetime(2026, 7, 1))['date'] == '2026-08-02'
    assert f(datetime.datetime(2026, 12, 2))['date'] == '2026-12-02', "le jour même, l'échéance reste à venir"
    assert f(datetime.datetime(2026, 12, 3)) is None, "le 2 février 2027 n'est pas une échéance du règlement"
    cadres = {e['date']: e['cadre'] for e in application.IA50_ECHEANCES}
    assert cadres == {'2026-08-02': 'reglement', '2026-12-02': 'reglement', '2027-02-02': 'code'}, cadres


def test_la_note_de_source_ne_pretend_plus_que_le_reglement_porte_la_date_du_code():
    import actualites_sources as A
    note = A.SOURCES_COMMUNIQUES['na2'][0]['note']
    assert 'Les trois échéances' not in note, note
    assert 'ne figure pas dans le règlement' in note and '2 février 2027' in note, note
    page = io.open(os.path.join(ICI, 'actualites.html'), encoding='utf-8').read()
    assert 'Les trois échéances citées' not in page


def test_le_bloc_des_echeances_de_l_article_50_dans_sentinel_distingue_le_reglement_du_code():
    i = PAGE.index('1 · Échéances à retenir')
    bloc = re.sub(r'<[^>]*>', ' ', PAGE[i:i + 2500])
    assert 'pas une échéance du règlement' in re.sub(r'\s+', ' ', bloc), bloc
    assert 'art. 111, § 4' in bloc


def _ia50_load(reponse):
    """Exécute le vrai début de `window.ia50Load` (jusqu'à la liste des échéances) sur une réponse fabriquée de
    /api/ia50/usages. Rend le texte des deux éléments du compte à rebours."""
    if not NODE:
        pytest.skip('node absent')
    d = MOTEUR.index('window.ia50Load = function(){')
    f = MOTEUR.index("var e = document.getElementById('ia50-echeances');", d)
    prog = ("var __el = {};\nvar document = { getElementById: function(id){ return __el[id] || (__el[id] = { style:{}, textContent:'' }); } };\n"
            "var window = {};\nfunction ia50Verifier(){ return null; }\nfunction ia50Cadre(){}\nfunction ia50AutoToggle(){}\n"
            "var __reponse = %s;\nvar fetch = function(){ return Promise.resolve({ json: function(){ return Promise.resolve(__reponse); } }); };\n"
            "%s\n});\n};\nwindow.ia50Load();\n"
            "setTimeout(function(){ console.log(JSON.stringify({ lbl: (__el['ia50-jours-lbl'] || {}).textContent,"
            " jours: (__el['ia50-jours'] || {}).textContent })); }, 40);\n" % (json.dumps(reponse), MOTEUR[d:f]))
    r = subprocess.run([NODE, '-e', prog], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-800:]
    return json.loads(r.stdout)


def test_le_libelle_du_compte_a_rebours_n_est_plus_ecrit_en_dur():
    assert 'Avant le 2 août 2026' not in PAGE
    assert 'id="ia50-jours-lbl"' in PAGE
    assert "d.prochaine_echeance" in MOTEUR
    # Le moteur ÉCRIT le libellé, d'après la réponse du serveur.
    out = _ia50_load({'ok': True, 'taux': 50, 'jours_avant_echeance': 64, 'prochaine_echeance': {'date': '2026-12-02'}, 'echeances': []})
    assert out['lbl'] == 'Avant le 02/12/2026' and out['jours'] == '64 jour(s)', out
    # Sans échéance légale à venir : le libellé reste celui de la page, le compteur le dit.
    out = _ia50_load({'ok': True, 'taux': 50, 'jours_avant_echeance': None, 'prochaine_echeance': None, 'echeances': []})
    assert out['lbl'] == '' and out['jours'] == 'Aucune echeance legale a venir', out


def _date_barre(langue_finale, basculer):
    """Exécute `sentDateBarre` (et `sentSetLang` si `basculer`) au mardi 29 septembre 2026, langue initiale « fr »."""
    if not NODE:
        pytest.skip('node absent')
    d = MOTEUR.index('function sentDateBarre() {')
    f = MOTEUR.index('\n}\n', d) + 3
    g = MOTEUR.index('window.sentSetLang = function (lg) {')
    h = MOTEUR.index('\n};\n', g) + 4
    prog = ("var __D = Date; Date = function(){ return new __D(2026, 8, 29, 12, 0, 0); }; Date.prototype = __D.prototype;\n"
            "var SENT_LANG = 'fr', SENT_LANG_CLE = 'k';\nvar localStorage = { setItem: function(){} };\n"
            "var __el = { textContent: '' };\nvar document = { getElementById: function(id){ return id === 'tb-date' ? __el : null; } };\n"
            "var window = {};\nfunction sentAppliquer(){}\n%s\n%s\n"
            "sentDateBarre();\nvar avant = __el.textContent;\n%s\nconsole.log(JSON.stringify({ avant: avant, apres: __el.textContent }));"
            % (MOTEUR[d:f], MOTEUR[g:h], "window.sentSetLang('%s');" % langue_finale if basculer else ''))
    r = subprocess.run([NODE, '-e', prog], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-800:]
    return json.loads(r.stdout)


def test_la_date_de_la_barre_du_haut_suit_la_langue_sans_passer_par_le_dictionnaire():
    """« MARDI # SEPTEMBRE # » ne couvre que les mardis de septembre : le jour de la semaine change chaque matin."""
    assert 'id="tb-date" translate="no"' in PAGE, "le dictionnaire ne doit pas toucher la date : elle est peinte par le moteur"
    fr = _date_barre('fr', basculer=False)
    assert fr['avant'] == 'MARDI 29 SEPTEMBRE 2026', fr
    en = _date_barre('en', basculer=True)
    assert en['avant'] == 'MARDI 29 SEPTEMBRE 2026', en
    assert re.match(r'^TUESDAY,? 29 SEPTEMBER 2026$', en['apres']), "la bascule vers l'anglais repeint la date : %r" % en['apres']
    retour = _date_barre('fr', basculer=True)
    assert retour['apres'] == 'MARDI 29 SEPTEMBRE 2026', retour


def test_une_date_a_venir_ne_se_dit_pas_avec_depuis():
    """Le 2 décembre 2026 n'était pas passé : « Depuis le 2 décembre 2026 » disait le contraire de la date.
    « À compter du » est vrai avant comme après."""
    faq = io.open(os.path.join(ICI, 'faq.html'), encoding='utf-8').read()
    for nom, texte in (('sentinel.page.js', MOTEUR), ('sentinel.html', PAGE), ('faq.html', faq)):
        trouve = re.findall(r'(?:[Dd]epuis le|applicables? depuis le) (?:2|02) décembre 2026', texte)
        assert not trouve, "%s : %s" % (nom, trouve)


def test_les_invites_du_copilote_ne_donnent_plus_le_haut_risque_au_2_aout_2026():
    assert 'haut risque aout 2026' not in MOTEUR
    assert 'haut risque annexe III au 2 dec 2027' in MOTEUR
    assert "8 pratiques interdites, plus 2 au 2 dec 2026" in MOTEUR


def test_la_liste_historique_des_articles_ne_confond_plus_l_annexe_i_et_l_annexe_ii():
    assert 'Annexe II : produits soumis' not in MOTEUR
    assert "{num:'Art. 51',title:'Enregistrement dans la base de données EU'" not in MOTEUR


# ── 10. LE SIMULATEUR DANS LA PAGE : chaque question a son groupe, chaque case son identifiant ──

def test_les_nouvelles_questions_sont_dans_la_page_avec_les_identifiants_que_le_moteur_lit():
    for groupe in ('cb-perimetre', 'r-art25-amont', 'cb-art5', 'r-annexe1'):
        assert 'id="%s"' % groupe in PAGE, groupe
    for coche in ('per-militaire', 'per-recherche', 'per-avantmarche', 'per-personnel',
                  'art5-b', 'art5-c', 'art5-d', 'art5-e', 'art5-f', 'art5-f-exception', 'art5-g', 'art5-ba', 'art5-bb'):
        assert "simCheckbox(this,'%s')" % coche in PAGE, coche
    for val in ('oui_tiers', 'oui_sans_tiers', 'fonction_non_securite', 'machines', 'non'):
        assert "simRadio('r-annexe1','%s')" % val in PAGE, val
    for val in ('oui', 'oui_autre', 'aposteriori', 'non'):
        assert "simRadio('r-biometrie','%s')" % val in PAGE, val
    assert "simRadio('r-art25-amont','oui')" in PAGE


def test_le_moteur_lit_les_nouvelles_reponses_a_chaque_etape():
    e1 = MOTEUR[MOTEUR.index('window.simNext = function(from){'):MOTEUR.index('  if(from === 2){')]
    e2 = MOTEUR[MOTEUR.index('  if(from === 2){'):MOTEUR.index('  /* L\'ÉTAPE 3 NE RELÈVE PLUS RIEN')]
    assert "SIM_DATA.perimetre = simGetCheckboxes('cb-perimetre');" in e1
    assert "SIM_DATA.art25_amont = simGetRadio('r-art25-amont');" in e1
    assert "SIM_DATA.art5 = simGetCheckboxes('cb-art5');" in e2
    assert "SIM_DATA.annexe1 = simGetRadio('r-annexe1');" in e2


def test_aucune_valeur_de_radio_n_est_le_prefixe_d_une_autre_dans_un_meme_groupe():
    """`simRadio` retrouve l'option choisie par la sous-chaîne « 'valeur' » : « oui » ne doit jamais
    sélectionner « oui_autre ». Le piège est celui d'Art. 5 / Art. 50, en radio."""
    for groupe in ('r-biometrie', 'r-annexe1', 'r-art25-amont', 'r-art25'):
        opts = re.findall(r"simRadio\('%s','([^']+)'\)" % groupe, PAGE)
        assert opts and len(set(opts)) == len(opts), (groupe, opts)
        for v in opts:
            assert sum(1 for o in re.findall(r"onclick=\"simRadio\('%s','[^']+'\)\"" % groupe, PAGE) if "'%s'" % v in o) == 1, (groupe, v)
