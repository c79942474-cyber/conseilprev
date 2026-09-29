"""LE CALCULATEUR DE SANCTIONS RENDAIT LE PLUS BAS DES DEUX PLAFONDS — LA LOI DIT LE PLUS ÉLEVÉ.

CE QUI A ÉTÉ TROUVÉ, LE 29 SEPTEMBRE 2026. En confrontant Sentinel à
l'infographie « AI Act — Comprendre les règles, maîtriser les usages », puis
au texte du règlement (UE) 2024/1689 et à celui du règlement (UE) 2026/1744
qui le modifie, la première chose exécutée a été le calcul des sanctions. Il
se trompait dans les deux écrans qui le portent :

  — LE CALCULATEUR (`calcSanctions`) écrivait `Math.min(ca * pct, plafond)`.
    L'article 99 dit, pour une entreprise, « le plus ÉLEVÉ » des deux plafonds
    (§3, §4, §5). Pour une pratique interdite et 50 M€ de chiffre d'affaires,
    la page affichait 3,5 M€ là où le plafond légal est 35 M€ : dix fois trop
    peu, par défaut, sur le cas que le formulaire propose à l'ouverture. Il
    était juste pour les PME — par accident. Il ajoutait en outre une
    « majoration récidive × 1,5 » et des plafonds PME/TPE à 50 % et 25 % que
    le règlement ne contient nulle part ;
  — LE SIMULATEUR (`simSanctions`) rangeait la transparence de l'article 50 à
    7,5 M€ / 1,5 % — l'article 99(4)(g) la range à 15 M€ / 3 % —, donnait le
    plus élevé des deux plafonds à une PME (35 M€ au lieu de 2,1 M€ pour une
    PME à 30 M€ de CA, qui relève du plus bas, §6), affichait « 8 M€ » pour
    7,5 M€ (`toFixed(0)`), « 2 % » pour 1,5 %, et « undefined » sous le
    montant fixe d'un système à risque minimal.

RIEN NE LE SIGNALAIT : les deux calculs rendaient un montant plausible, mis en
forme, avec une base légale à côté. Aucun test ne portait sur eux.

CE QUE CES RÈGLES GARDENT. Elles ne lisent pas le code : elles l'EXÉCUTENT.
La source unique (`AI_ACT_SANCTIONS` / `aiActSanctionMax`), le calculateur
(sur un DOM de substitution) et le simulateur sont extraits du fichier et
évalués dans Node, puis leurs réponses sont comparées à une arithmétique de
l'article 99 réécrite ICI, indépendamment, à partir du texte : plus élevé pour
une entreprise, plus bas pour les PME et start-up (§6) et, sur les §4 et §5
seulement, pour les petites capitalisations intermédiaires (§6 bis, ajouté par
le règlement (UE) 2026/1744). L'article 101 (modèles GPAI) a son plafond, sans
la règle des PME.

CE QU'ELLES NE PEUVENT PAS FAIRE. Dire si les montants du règlement sont ceux
qu'une autorité prononcera : ce sont des PLAFONDS, l'amende se fixe dessous
(art. 99(7)). Ni décider qu'une organisation est une PME : le seuil tient à
l'effectif et au bilan autant qu'au chiffre d'affaires, et la page le dit.
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

DEBUT_SOURCE = 'var AI_ACT_SANCTIONS = {'
FIN_SOURCE = '/* ══ FIN SANCTIONS — SOURCE UNIQUE ══ */'

# ── L'ARITHMÉTIQUE DE L'ARTICLE 99, RÉÉCRITE ICI, À PARTIR DU TEXTE ────────
# (plafond fixe, part du chiffre d'affaires mondial, PME §6, petite cap. §6 bis)
LOI = {
    'interdit':     (35_000_000, 0.07, True, False),   # 99(3)
    'obligations':  (15_000_000, 0.03, True, True),    # 99(4)
    'transparence': (15_000_000, 0.03, True, True),    # 99(4)(g)
    'info':         (7_500_000,  0.01, True, True),    # 99(5)
    'gpai':         (15_000_000, 0.03, False, False),  # 101
}
TAILLES = ['tpe', 'pme', 'smc', 'eti', 'ge']
CA = [1_000_000, 5_000_000, 30_000_000, 50_000_000, 150_000_000, 2_000_000_000]


def attendu(palier, ca, taille):
    fixe, pct, pme, smc = LOI[palier]
    sur_ca = round(ca * pct)
    bas = (pme and taille in ('tpe', 'pme')) or (smc and taille == 'smc')
    return min(fixe, sur_ca) if bas else max(fixe, sur_ca)


def _tranche(debut, fin=None):
    d = MOTEUR.index(debut)
    if fin is not None:
        return MOTEUR[d:MOTEUR.index(fin, d)]
    m = re.compile(r'\n}\n').search(MOTEUR, d)
    return MOTEUR[d:m.end()]


def _node(programme):
    if not NODE:
        pytest.skip('node absent : le calcul des sanctions ne peut pas être exécuté')
    r = subprocess.run([NODE, '-e', programme], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        pytest.fail("le calcul ne s'exécute pas :\n%s" % (r.stderr or '')[-1500:])
    return json.loads(r.stdout.strip())


def _source():
    """La source unique — ou rien : sans elle, chaque règle tombe sur SON
    constat (le calcul ne se fait plus, ou se fait faux), pas sur une erreur
    d'import qui les emporterait toutes d'un bloc."""
    return _tranche(DEBUT_SOURCE, FIN_SOURCE) if DEBUT_SOURCE in MOTEUR else ''


SOURCE = _source()


# ── LA SOURCE UNIQUE ────────────────────────────────────────────────────────

def test_la_source_unique_rend_le_plafond_de_l_article_99_pour_chaque_palier_et_chaque_taille():
    assert SOURCE, "la table des sanctions (AI_ACT_SANCTIONS) n'existe pas : deux arithmétiques se partagent l'article 99"
    cas = [(p, ca, t) for p in LOI for ca in CA for t in TAILLES]
    prog = ('var window = {};\n%s\nvar cas = %s;\n'
            'console.log(JSON.stringify(cas.map(function(c){ return aiActSanctionMax(c[0], c[1], c[2]).max; })));'
            % (SOURCE, json.dumps(cas)))
    rendu = _node(prog)
    fautes = ['%s CA=%s taille=%s : rendu %s, attendu %s' % (p, ca, t, r, attendu(p, ca, t))
              for (p, ca, t), r in zip(cas, rendu) if r != attendu(p, ca, t)]
    assert not fautes, "plafond faux :\n  - " + "\n  - ".join(fautes[:12])


def test_pour_une_entreprise_c_est_le_plus_eleve_des_deux_plafonds():
    """LE DÉFAUT QUI VALAIT DIX FOIS TROP PEU. 50 M€ de CA, pratique interdite :
    7 % ne font que 3,5 M€, le plafond fixe de 35 M€ est le plus élevé."""
    prog = ('var window = {};\n%s\nconsole.log(JSON.stringify(['
            'aiActSanctionMax("interdit", 50000000, "eti").max,'
            'aiActSanctionMax("interdit", 2000000000, "ge").max]));' % SOURCE)
    petit, grand = _node(prog)
    assert petit == 35_000_000, "à 50 M€ de CA, une pratique interdite plafonne à 35 M€ (le plus élevé) : rendu %s" % petit
    assert grand == 140_000_000, "à 2 Md€ de CA, 7 % font 140 M€, au-dessus du plafond fixe : rendu %s" % grand


def test_pour_une_pme_c_est_le_plus_bas_et_pour_une_petite_capitalisation_seulement_sur_les_paragraphes_4_et_5():
    prog = ('var window = {};\n%s\nconsole.log(JSON.stringify(['
            'aiActSanctionMax("interdit", 30000000, "pme").max,'
            'aiActSanctionMax("obligations", 100000000, "smc").max,'
            'aiActSanctionMax("interdit", 100000000, "smc").max,'
            'aiActSanctionMax("gpai", 5000000, "pme").max]));' % SOURCE)
    pme, smc_4, smc_3, gpai_pme = _node(prog)
    assert pme == 2_100_000, "PME à 30 M€, pratique interdite : 7 % = 2,1 M€, le plus bas (§6) — rendu %s" % pme
    assert smc_4 == 3_000_000, "petite capitalisation, §4 : le plus bas (§6 bis), 3 % de 100 M€ — rendu %s" % smc_4
    assert smc_3 == 35_000_000, ("petite capitalisation, §3 : l'allègement du §6 bis ne vise que les §4 et §5 ; "
                                 "le plafond reste le plus élevé — rendu %s" % smc_3)
    assert gpai_pme == 15_000_000, ("l'article 101 ne connaît pas la règle des PME de l'article 99(6) : "
                                    "3 % de 5 M€ = 150 k€ mais le plafond est le plus élevé — rendu %s" % gpai_pme)


def test_la_source_nomme_l_article_de_chaque_palier():
    prog = ('var window = {};\n%s\nconsole.log(JSON.stringify(Object.keys(AI_ACT_SANCTIONS).map(function(k){'
            'return [k, AI_ACT_SANCTIONS[k].art];})));' % SOURCE)
    arts = dict(_node(prog))
    assert arts == {'interdit': 'Art. 99(3)', 'obligations': 'Art. 99(4)',
                    'transparence': 'Art. 99(4)(g)', 'info': 'Art. 99(5)', 'gpai': 'Art. 101'}, arts


# ── LE CALCULATEUR : ce que la page affiche ────────────────────────────────

def _calculateur():
    """Exécute `calcSanctions` sur un DOM de substitution, pour chaque combinaison.

    Le DOM enregistre les identifiants demandés : une règle qui exige qu'un champ
    supprimé ne soit plus lu doit voir la demande, pas la deviner."""
    corps = _tranche('function calcSanctions(){')
    cas = [(t, ca, s) for t in ('interdit', 'haut', 'transparence', 'info', 'gpai')
           for ca in CA for s in TAILLES]
    prog = """
var window = {};
%s
%s
var __demandes = {};
var __sortie = {};
var __vals = {};
var document = { getElementById: function(id){
  __demandes[id] = true;
  if (Object.prototype.hasOwnProperty.call(__vals, id)) return { value: __vals[id] };
  return __sortie[id] || (__sortie[id] = { textContent:'', innerHTML:'', classList:{add:function(){}}, scrollIntoView:function(){} });
}};
var cas = %s;
var res = cas.map(function(c){
  __vals = { 's-type': c[0], 's-ca': String(c[1]), 's-size': c[2] };
  calcSanctions();
  return [__sortie['sanc-amount'].textContent, __sortie['sanc-basis-txt'].textContent, __sortie['sanc-details'].innerHTML];
});
console.log(JSON.stringify({ cas: cas, res: res, demandes: Object.keys(__demandes) }));
""" % (SOURCE, corps, json.dumps(cas))
    return _node(prog)


CALC = None


def _calc():
    global CALC
    if CALC is None:
        CALC = _calculateur()
    return CALC


def _montant(texte):
    return int(re.sub(r'[^\d]', '', texte) or 0)


PALIER_DU_TYPE = {'interdit': 'interdit', 'haut': 'obligations', 'transparence': 'transparence',
                  'info': 'info', 'gpai': 'gpai'}


def test_le_calculateur_affiche_le_plafond_de_l_article_99_pour_chaque_type_et_chaque_taille():
    c = _calc()
    fautes = []
    for (t, ca, s), (montant, _base, _det) in zip(c['cas'], c['res']):
        att = attendu(PALIER_DU_TYPE[t], ca, s)
        if _montant(montant) != att:
            fautes.append('%s CA=%s taille=%s : affiché %s, attendu %s' % (t, ca, s, montant, att))
    assert not fautes, "calculateur faux :\n  - " + "\n  - ".join(fautes[:12])


def test_le_cas_par_defaut_du_formulaire_n_est_plus_dix_fois_trop_bas():
    """Le formulaire s'ouvre sur 50 M€ de CA et une ETI. Pour une pratique
    interdite, la page affichait 3,5 M€."""
    c = _calc()
    i = c['cas'].index(['interdit', 50_000_000, 'eti'])
    assert _montant(c['res'][i][0]) == 35_000_000, c['res'][i][0]


def test_le_calculateur_ne_lit_plus_de_recidive_et_ses_details_n_en_parlent_plus():
    """Le règlement ne contient aucune majoration de récidive ni réduction
    forfaitaire pour les PME : l'une et l'autre étaient inventées."""
    c = _calc()
    assert 's-recid' not in c['demandes'], "le calculateur lit encore le champ « récidive »"
    for (_m, _b, det) in c['res']:
        assert 'récidive' not in det.lower() and '× 1,5' not in det, det
    assert 'id="s-recid"' not in PAGE, "le champ « récidive » est encore dans la page"


def test_le_calculateur_dit_la_regle_appliquee_et_ne_pretend_pas_fixer_le_montant():
    c = _calc()
    i_pme = c['cas'].index(['haut', 5_000_000, 'pme'])
    i_ge = c['cas'].index(['haut', 2_000_000_000, 'ge'])
    i_smc = c['cas'].index(['haut', 150_000_000, 'smc'])
    assert 'plus bas' in c['res'][i_pme][2] and '99(6)' in c['res'][i_pme][2], c['res'][i_pme][2]
    assert 'plus élevé' in c['res'][i_ge][2], c['res'][i_ge][2]
    assert '99(6a)' in c['res'][i_smc][2], c['res'][i_smc][2]
    assert '99(7)' in c['res'][i_ge][2], "le montant effectif se fixe sous le plafond, d'après l'art. 99(7)"


def test_le_calculateur_range_la_transparence_et_le_gpai_sous_leur_article():
    c = _calc()
    base = {t: c['res'][c['cas'].index([t, 50_000_000, 'ge'])][1] for t in ('transparence', 'gpai', 'haut', 'info')}
    assert '99(4)(g)' in base['transparence'], base['transparence']
    assert 'Art. 101' in base['gpai'], base['gpai']
    assert '99(4)' in base['haut'] and '99(5)' in base['info']


def test_la_page_propose_les_types_et_les_tailles_que_le_calcul_sait_traiter():
    types = re.findall(r'<option value="([^"]+)"[^>]*>[^<]*</option>',
                       PAGE[PAGE.index('id="s-type"'):PAGE.index('</select>', PAGE.index('id="s-type"'))])
    tailles = re.findall(r'<option value="([^"]+)"[^>]*>[^<]*</option>',
                         PAGE[PAGE.index('id="s-size"'):PAGE.index('</select>', PAGE.index('id="s-size"'))])
    assert set(types) == set(PALIER_DU_TYPE), types
    assert set(tailles) == set(TAILLES), tailles
    # Chaque option annonce le palier de sa source : 35 M€ / 7 % pour le §3, etc.
    bloc = PAGE[PAGE.index('id="s-type"'):PAGE.index('</select>', PAGE.index('id="s-type"'))]
    assert 'Art. 99(4)(g) (15 M€ / 3 %)' in bloc, "la transparence est au palier du §4(g)"
    assert 'Art. 101' in bloc


def test_la_page_ne_promet_ni_majoration_ni_reduction_forfaitaire():
    m = PAGE[PAGE.index('id="p-sanctions"'):PAGE.index('id="p-benchmark"')]
    plat = re.sub(r'<[^>]*>', '', m)
    assert re.search(r'ni majoration automatique', plat), "la page ne dit plus qu'il n'y a pas de majoration"
    assert '99(7)' in plat and '99(6a)' in plat and '2026/1744' in plat


def test_l_enregistrement_dans_l_historique_ne_lit_plus_le_champ_supprime():
    corps = _tranche('window.histoSaveSanctions = function(){', "\n};")
    assert 's-recid' not in corps and 'recidive' not in corps


# ── LE SIMULATEUR : ce que la page de résultats affiche ────────────────────

CLASSES_CA = {'startup': 5_000_000, 'sme': 30_000_000, 'mid': 150_000_000,
              'large': 500_000_000, 'xlarge': 2_000_000_000}
NIVEAU_PALIER = {'interdit': 'interdit', 'haut': 'obligations', 'limite': 'transparence', 'minimal': 'info'}


def _simulateur():
    corps = _tranche('function simSanctions(classif){')
    cas = [[niv, ca] for niv in NIVEAU_PALIER for ca in CLASSES_CA]
    prog = """
var window = {};
%s
var SIM_DATA = {};
%s
var cas = %s;
console.log(JSON.stringify(cas.map(function(c){
  SIM_DATA = { ca: c[1] };
  return simSanctions({ level: c[0] });
})));
""" % (SOURCE, corps, json.dumps(cas))
    return cas, _node(prog)


SIM = None


def _sim():
    global SIM
    if SIM is None:
        SIM = _simulateur()
    return SIM


def _pour(niveau, ca):
    cas, res = _sim()
    return res[cas.index([niveau, ca])]


def test_le_simulateur_rend_le_plafond_de_l_article_99_pour_chaque_niveau_et_chaque_classe_de_ca():
    cas, res = _sim()
    fautes = []
    for (niv, classe), s in zip(cas, res):
        taille = 'pme' if classe in ('startup', 'sme') else 'eti'
        att = attendu(NIVEAU_PALIER[niv], CLASSES_CA[classe], taille)
        if s['max_eur'] != att:
            fautes.append('%s / %s : rendu %s, attendu %s' % (niv, classe, s['max_eur'], att))
    assert not fautes, "simulateur faux :\n  - " + "\n  - ".join(fautes)


def test_la_transparence_de_l_article_50_est_au_palier_du_paragraphe_4():
    """Le simulateur la rangeait à 7,5 M€ / 1,5 % : c'est le palier du §5."""
    s = _pour('limite', 'xlarge')
    assert s['art'] == 'Art. 99(4)(g)', s['art']
    assert s['pct'] == '3%' and s['sanction_flat'] == '15 M€', s
    assert s['max_eur'] == 60_000_000, s


def test_une_pme_recoit_le_plus_bas_des_deux_plafonds_dans_le_simulateur():
    s = _pour('interdit', 'sme')
    assert s['max_eur'] == 2_100_000, "PME à 30 M€ : 7 % = 2,1 M€, pas 35 M€ — rendu %s" % s['max_eur']
    assert s['regle'] == 'plus_bas' and '99(6)' in s['regle_txt'], s


def test_une_grande_entreprise_garde_le_plus_eleve_et_le_dit():
    s = _pour('interdit', 'xlarge')
    assert s['max_eur'] == 140_000_000 and s['regle'] == 'plus_haut', s
    assert 'plus élevé' in s['regle_txt']


def test_la_tranche_eti_signale_l_allegement_possible_sans_l_appliquer():
    """L'effectif n'est pas connu du simulateur : la tranche 50-250 M€ reçoit le
    plafond sans allègement, et le dit s'il existe pour ce palier."""
    s = _pour('haut', 'mid')
    assert s['max_eur'] == 15_000_000, s
    assert 'petite capitalisation intermédiaire' in s['note'] and '99(6a)' in s['note'], s['note']
    assert '4,5 M€' in s['note'], "le plafond allégé (3 % de 150 M€) doit être chiffré : %s" % s['note']
    # Pour une pratique interdite, le §6 bis ne s'applique pas : pas de mention.
    assert 'petite capitalisation' not in _pour('interdit', 'mid')['note']


def test_un_montant_non_entier_n_est_plus_arrondi_a_l_unite_superieure():
    """« 8 M€ » pour 7,5 M€ : `toFixed(0)` arrondit. Le palier du §5 est le seul
    à ce montant."""
    s = _pour('minimal', 'xlarge')
    assert s['sanction_flat'] == '7,5 M€', s
    assert '8 M€' not in json.dumps(s, ensure_ascii=False), s


def test_le_risque_minimal_ne_pretend_pas_a_une_amende_propre():
    s = _pour('minimal', 'large')
    assert s['art'] == 'Art. 99(5)' and s['palier'] == 'info', s
    assert 'aucune obligation propre' in s['note'], s['note']


def test_aucun_champ_du_simulateur_n_est_indefini():
    cas, res = _sim()
    for c, s in zip(cas, res):
        for cle in ('sanction_ca', 'sanction_flat', 'sanction_max', 'pct', 'art', 'regle_txt', 'note'):
            assert s.get(cle) not in (None, '', 'undefined'), (c, cle, s)


def test_la_classification_lit_ses_references_de_sanction_dans_la_source():
    """`simClassify` posait `Art. 99(2)` pour le haut risque (le §2 est la
    notification aux États membres) et laissait `{}` au risque minimal."""
    corps = _tranche('function simSanctionsRef(palier){', '/* ══ LE RÔLE COMMANDE LES OBLIGATIONS')
    cas = [({'secteur': 'autre', 'type': 'reco'}, 'minimal'),
           ({'secteur': 'emploi', 'type': 'scoring', 'annexe3': ['annexe3-emploi']}, 'haut'),
           ({'secteur': 'autre', 'type': 'chatbot'}, 'limite'),
           ({'secteur': 'autre', 'type': 'reco', 'subliminal': 'oui'}, 'interdit')]
    prog = """
var window = {};
%s
var SIM_DATA = {};
%s
var cas = %s;
console.log(JSON.stringify(cas.map(function(c){ SIM_DATA = c[0]; var r = simClassify(); return [r.level, r.sanctions]; })));
""" % (SOURCE, corps, json.dumps(cas))
    res = dict((n, s) for n, s in _node(prog))
    assert res == {
        'minimal':  {'max_pct': '1% du CA mondial', 'max_flat': '7 500 000 €',  'art': 'Art. 99(5)'},
        'haut':     {'max_pct': '3% du CA mondial', 'max_flat': '15 000 000 €', 'art': 'Art. 99(4)'},
        'limite':   {'max_pct': '3% du CA mondial', 'max_flat': '15 000 000 €', 'art': 'Art. 99(4)(g)'},
        'interdit': {'max_pct': '7% du CA mondial', 'max_flat': '35 000 000 €', 'art': 'Art. 99(3)'},
    }, res


# ── UNE SEULE ARITHMÉTIQUE : plus aucun montant écrit à la main ailleurs ───

@pytest.mark.parametrize('debut', ['function calcSanctions(){', 'function simSanctions(classif){',
                                   'function simSanctionsRef(palier){'],
                         ids=['calcSanctions', 'simSanctions', 'simSanctionsRef'])
def test_aucun_montant_de_l_article_99_n_est_recopie_hors_de_la_source_unique(debut):
    """LA RÈGLE QUI EMPÊCHE LA DEUXIÈME ARITHMÉTIQUE DE REVENIR. Tant que ces
    fonctions lisent la table, elles ne peuvent plus diverger de l'article 99
    l'une de l'autre. Un montant recopié dedans repartira dans son coin."""
    corps = _tranche(debut)
    corps = re.sub(r'/\*.*?\*/', '', corps, flags=re.S)
    corps = re.sub(r'//[^\n]*', '', corps)
    montants = re.findall(r'(?<!\d)(?:35|15)\s?000\s?000(?!\d)|(?<!\d)7\s?500\s?000(?!\d)|\b0\.07\b|\b0\.03\b|\b0\.015\b', corps)
    assert not montants, "%s recopie un montant de l'article 99 : %s" % (debut, montants)


def test_le_simulateur_et_le_calculateur_appellent_la_meme_fonction():
    assert 'aiActSanctionMax(' in _tranche('function calcSanctions(){')
    assert 'aiActSanctionMax(' in _tranche('function simSanctions(classif){')
    assert 'window.aiActSanctionMax = aiActSanctionMax;' in MOTEUR


# ── LES FICHES D'ARTICLE ───────────────────────────────────────────────────

def _fiche(num):
    """L'entrée de la liste des articles dont `num` est le numéro."""
    d = MOTEUR.index("num:'%s'," % num)
    return MOTEUR[d:MOTEUR.index("\n      url:", d)]


def test_la_fiche_de_l_article_50_donne_le_palier_du_paragraphe_4():
    f = _fiche('Art. 50')
    assert re.search(r"sanction:'15 M€ ou 3% CA mondial", f), (
        "la fiche de l'article 50 range la transparence sous un autre palier : %s" % f[:300])
    assert '7,5 M€' not in f


def test_la_fiche_de_l_article_99_distingue_les_trois_paliers_et_la_regle_des_pme():
    f = _fiche('Art. 99')
    for attendu_ in ('35 M€ ou 7%', '15 M€ ou 3%', '7,5 M€ ou 1%', 'plus ÉLEVÉ', 'plus BAS', 'Art. 101', '2026/1744'):
        assert attendu_ in f, "la fiche de l'article 99 ne dit plus « %s »" % attendu_
    assert 'proportionnalité garantie' not in f, "la formule vague qui remplaçait la règle du §6 est revenue"
