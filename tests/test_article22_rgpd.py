# -*- coding: utf-8 -*-
"""L'ARTICLE 22 EST UN TEST, ET SENTINEL N'EN DONNAIT QUE LE RÉSULTAT.

CE QUI A DÉCLENCHÉ CE FICHIER. La fiche « Art. 22 » tenait en trois phrases et
trois obligations. Elle disait juste — décision exclusivement automatisée, effets
juridiques, trois exceptions — mais elle ne disait pas comment on TESTE. Or
l'article ne s'applique que si trois conditions sont réunies CUMULATIVEMENT, et
tout le contentieux se joue sur la troisième : à partir de quand une revue
humaine compte-t-elle ?

Le lecteur repartait donc avec « garantir une intervention humaine
significative » sans savoir ce que « significative » veut dire. C'est la seule
phrase de la fiche qui décidait de quelque chose, et c'était la seule qui n'était
pas explicitée.

CE QUE CES RÈGLES GARDENT, DANS L'ORDRE DE CE QUI FAIT MAL :

1. QUE LES TROIS CONDITIONS RESTENT PRÉSENTÉES COMME CUMULATIVES. Les énumérer
   sans le dire laisse croire qu'une seule suffit à déclencher l'article — et
   fait manquer l'inverse, qui est l'enjeu réel : une seule qui tombe l'écarte.
2. QUE LES GARANTIES NE SOIENT PAS PRÉSENTÉES COMME ÉTEINTES PAR L'EXCEPTION.
   Les trois droits du § 3 restent dus SOUS exception. Les lire l'un après
   l'autre, exceptions d'abord, produit exactement le contresens inverse.
3. QUE « CE QUI NE SUFFIT PAS » SURVIVE. C'est la partie coûteuse à écrire, la
   première qu'on abrège, et la seule qui empêche de croire qu'un point de
   validation dans un flux règle la question.
4. QU'UN MONTANT DE SANCTION PORTE DE QUOI LE RETROUVER. Un nombre recopié de
   proche en proche finit par n'avoir plus de source du tout.
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

import sys  # noqa: E402
sys.path.insert(0, ICI)
import juridique      # noqa: E402
import librejustice   # noqa: E402


def _articles():
    """ÉVALUE le catalogue plutôt que de le lire au motif. Les fiches portent
    des apostrophes échappées et des guillemets typographiques ; les lire à
    l'expression rationnelle marche jusqu'au jour où une phrase contient
    « num: »."""
    if not NODE:
        pytest.skip('node absent : le catalogue des articles ne peut pas être évalué')
    d = MOTEUR.index('var ARTICLES = [')
    src = MOTEUR[d:MOTEUR.index('\n];', d) + 3]
    r = subprocess.run([NODE, '-e', src + '\nconsole.log(JSON.stringify(ARTICLES));'],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        pytest.fail("ARTICLES ne s'évalue pas :\n%s" % (r.stderr or '')[-1200:])
    return json.loads(r.stdout)


ARTICLES = _articles()


def _art22():
    for ch in ARTICLES:
        if ch.get('reglement') != 'rgpd':
            continue
        for a in ch['arts']:
            if a['num'] == 'Art. 22':
                return a
    pytest.fail("la fiche « Art. 22 » a disparu du chapitre RGPD")


def _an():
    an = _art22().get('analyse')
    assert an, ("la fiche Art. 22 ne porte plus d'analyse : le lecteur retrouve "
                "« garantir une intervention humaine significative » sans savoir "
                "ce que « significative » veut dire")
    return an


def _plat(x):
    """Tout le texte d'un sous-arbre, à plat."""
    if isinstance(x, str):
        return x
    if isinstance(x, list):
        return ' '.join(_plat(i) for i in x)
    if isinstance(x, dict):
        return ' '.join(_plat(v) for v in x.values())
    return ''


# ── 1. LE TEST, ET SON CARACTÈRE CUMULATIF ───────────────────────────────

def test_les_trois_conditions_sont_enoncees():
    conds = _an()['test']['conditions']
    assert len(conds) == 3, (
        "le test de l'art. 22 compte trois conditions, la fiche en annonce %d"
        % len(conds))
    plat = ' '.join(conds).lower()
    for attendu, quoi in (('exclusivement', "la décision fondée EXCLUSIVEMENT sur l'automatisé"),
                          ('profilage', "le profilage, expressément visé par le texte"),
                          ('juridique', "l'effet juridique"),
                          ('significati', "l'effet significatif similaire")):
        assert attendu in plat, "le test ne mentionne pas %s" % quoi


def test_le_caractere_cumulatif_est_dit_et_son_corollaire_avec():
    """ÉNUMÉRER TROIS CONDITIONS SANS DIRE QU'ELLES SONT CUMULATIVES est le
    contresens le plus coûteux de la fiche : le lecteur croit qu'une seule
    suffit à déclencher l'article, et manque l'inverse — qu'une seule qui tombe
    l'écarte. C'est précisément là que se joue le contentieux."""
    intro = _an()['test']['intro'].lower()
    assert 'trois' in intro or 'les trois' in _an()['test']['titre'].lower()
    assert 'cumulativ' in _an()['test']['titre'].lower() or 'réunies' in intro, (
        "rien ne dit que les trois conditions sont cumulatives : « %s »" % intro)
    assert 'une seule' in intro, (
        "le corollaire n'est pas dit — qu'il suffit d'UNE condition manquante "
        "pour écarter l'article : « %s »" % intro)


# ── 2. LES GARANTIES SURVIVENT AUX EXCEPTIONS ────────────────────────────

def test_les_trois_exceptions_sont_completes():
    plat = _plat(_an()['exceptions']).lower()
    for attendu in ('contrat', 'droit de l\'union', 'consentement explicite'):
        assert attendu in plat, "l'exception « %s » manque" % attendu


def test_les_trois_garanties_sont_completes():
    plat = _plat(_an()['garanties']).lower()
    for attendu, quoi in (('intervention humaine', "le droit d'obtenir une intervention humaine"),
                          ('point de vue', "le droit d'exprimer son point de vue"),
                          ('contester', "le droit de contester la décision")):
        assert attendu in plat, "%s manque aux garanties" % quoi


def test_les_garanties_sont_dites_dues_malgre_l_exception():
    """LE CONTRESENS QUE CETTE RÈGLE EMPÊCHE. Une exception lève l'interdiction
    de principe ; elle ne lève pas les garanties du § 3, qui restent dues. Un
    intitulé neutre — « Garanties » — posé à côté de « Exceptions » laisse
    exactement croire l'inverse."""
    titre = _an()['garanties']['titre'].lower()
    assert 'exception' in titre and ('même' in titre or 'malgré' in titre), (
        "l'intitulé des garanties ne dit pas qu'elles survivent à l'exception : "
        "« %s »" % _an()['garanties']['titre'])


# ── 3. CE QUE « SIGNIFICATIVE » VEUT DIRE ────────────────────────────────

def test_ce_qui_ne_suffit_pas_est_dit():
    """LA PARTIE QU'ON ABRÈGE EN PREMIER, ET LA SEULE QUI DÉCIDE. Sans elle, un
    point de validation posé dans un flux passe pour une intervention
    humaine."""
    ko = _plat(_an()['humain']['insuffisant']).lower()
    for attendu, quoi in (
            ('validation automatique', "la validation automatique du résultat"),
            ('superficiel', "la revue superficielle"),
            ('compréhension', "l'absence de compréhension de la logique du score"),
            ('modifier', "l'impossibilité de modifier la décision")):
        assert attendu in ko, "« ce qui ne suffit pas » ne mentionne pas %s" % quoi


def test_ce_qui_est_attendu_est_dit():
    ok = _plat(_an()['humain']['attendu']).lower()
    for attendu, quoi in (
            ('compétent', "un réviseur compétent et formé"),
            ('accès', "l'accès aux données et aux raisons de la décision"),
            ('réexamen', "le pouvoir réel de réexamen"),
            ('annuler', "la possibilité de confirmer, modifier ou annuler"),
            ('traçabilité', "la traçabilité de la revue")):
        assert attendu in ok, "« ce qui est attendu » ne mentionne pas %s" % quoi


def test_les_deux_colonnes_ne_se_confondent_pas():
    """Si l'attendu répétait l'insuffisant, la fiche n'apprendrait rien : c'est
    l'ÉCART entre les deux qui porte le sens."""
    ko = set(_an()['humain']['insuffisant']['items'])
    ok = set(_an()['humain']['attendu']['items'])
    assert not (ko & ok), "les deux colonnes partagent des entrées : %s" % (ko & ok)


def test_la_conclusion_porte_l_exigence_de_demonstration():
    """« Avoir un humain dans la boucle » et « pouvoir démontrer qu'il comprend »
    sont deux exigences différentes, et seule la seconde est opposable."""
    c = _an()['conclusion'].lower()
    assert 'démontrer' in c
    for verbe in ('comprend', 'réexamine', 'modifier'):
        assert verbe in c, "la conclusion ne dit pas que l'humain doit %s" % verbe


# ── 4. L'ANCRAGE : UN MONTANT PORTE DE QUOI LE RETROUVER ─────────────────

def test_la_sanction_porte_sa_date_son_montant_et_son_autorite():
    a = _an()['ancrage']
    for champ in ('date', 'montant', 'autorite', 'portee'):
        assert (a.get(champ) or '').strip(), "la sanction citée n'a pas de %s" % champ
    assert re.search(r'\d', a['montant']), "le montant ne contient aucun chiffre"


def test_le_montant_porte_le_moyen_de_le_verifier():
    """UN NOMBRE SANS SOURCE SE RECOPIE JUSQU'À N'EN PLUS AVOIR. C'est la règle
    de la maison sur toute valeur publiée, et un montant de sanction est
    exactement le genre de chiffre qui circule de note en note."""
    a = _an()['ancrage']
    v = (a.get('verifier') or '').lower()
    assert v, "le montant de la sanction ne dit pas où le vérifier"
    assert 'registre' in v or 'référence' in v, (
        "la mention de vérification n'indique pas quoi aller chercher : « %s »"
        % a.get('verifier'))


def test_la_portee_de_la_sanction_est_la_lecon_pas_le_montant():
    """Ce qu'un lecteur doit retenir n'est pas le nombre : c'est qu'une revue
    formelle ne suffit pas."""
    p = _an()['ancrage']['portee'].lower()
    assert 'formel' in p and ('ne suffit pas' in p or 'insuffisant' in p)


def test_le_parallele_ne_reste_pas_cantonne_au_credit():
    """Le scoring crédit est l'exemple ; le raisonnement vaut partout où un score
    ouvre ou ferme un droit. Le cantonner au crédit ferait manquer l'assurance,
    la fraude et la désactivation de compte — qui est le fait de la sanction
    citée juste au-dessus."""
    t = _plat(_an()['parallele']).lower()
    for autre in ('assurance', 'fraude', 'accès à un service'):
        assert autre in t, "le parallèle ne s'étend pas à %s" % autre


# ── 5. LA CHECKLIST SUIT L'ORDRE DU TEST ─────────────────────────────────

def test_la_checklist_suit_l_ordre_du_raisonnement():
    """Une checklist qui demande la preuve avant de demander si l'article
    s'applique fait travailler pour rien."""
    items = [x.lower() for x in _an()['checklist']['items']]
    assert len(items) >= 5
    assert 'décision individuelle' in items[0]
    assert 'juridique' in items[1] or 'significatif' in items[1]
    assert 'humaine' in items[2]
    assert 'preuve' in items[-1], (
        "la checklist ne se termine pas par la preuve, qui est ce qui reste "
        "quand le contrôle arrive")


# ── 6. LE RENDU AFFICHE L'ANALYSE ────────────────────────────────────────

def _rendu():
    if not NODE:
        pytest.skip('node absent')
    src = ''
    for n in ('artListe', 'artAnalyse'):
        d = MOTEUR.index('function %s(' % n)
        src += MOTEUR[d:MOTEUR.index('\n}\n', d) + 2] + '\n'
    prog = src + '\nconsole.log(JSON.stringify(artAnalyse(%s)));' % json.dumps(
        _an(), ensure_ascii=False)
    r = subprocess.run([NODE, '-e', prog], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        pytest.fail("artAnalyse ne s'évalue pas :\n%s" % (r.stderr or '')[-1200:])
    return json.loads(r.stdout)


def test_l_analyse_est_reellement_rendue():
    h = _rendu()
    for morceau in ('Les trois conditions cumulatives', 'Exceptions',
                    'Ce qui ne suffit pas', 'Ce qui est attendu',
                    '824 990 000 €', 'Checklist'):
        assert morceau in h, "le rendu n'affiche pas « %s »" % morceau


def test_un_article_sans_analyse_ne_rend_rien():
    """Le champ est optionnel : les trente autres fiches ne doivent pas gagner
    une section vide."""
    if not NODE:
        pytest.skip('node absent')
    d = MOTEUR.index('function artAnalyse(')
    src = MOTEUR[d:MOTEUR.index('\n}\n', d) + 2]
    r = subprocess.run(
        [NODE, '-e', src + "\nconsole.log(JSON.stringify([artAnalyse(null),artAnalyse(undefined)]));"],
        capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-600:]
    assert json.loads(r.stdout) == ['', '']


def test_le_renderer_est_branche_dans_la_fiche():
    d = MOTEUR.index('function artRender(')
    bloc = MOTEUR[d:d + 4000]
    assert 'artAnalyse(a.analyse)' in bloc, (
        "l'analyse est écrite mais la fiche ne l'affiche pas")


def test_toute_classe_employee_par_le_rendu_est_stylee():
    """LA CSS DÉCIDE DE LA MISE EN PAGE, PAS L'INTENTION. Une classe inventée
    dans le rendu et absente de la feuille de style produit un bloc sans forme,
    et rien ne le signale."""
    h = _rendu()
    manquantes = []
    for attr in re.findall(r'class="([^"]+)"', h):
        for classe in attr.split():
            if not classe.startswith('art-an'):
                continue
            if ('.%s{' % classe) not in PAGE and ('.%s ' % classe) not in PAGE \
                    and ('.%s:' % classe) not in PAGE and ('.%s,' % classe) not in PAGE:
                manquantes.append(classe)
    assert not manquantes, (
        "classe(s) employée(s) par le rendu et stylée(s) nulle part : %s"
        % ', '.join(sorted(set(manquantes))))


def test_les_exceptions_et_les_garanties_sont_cote_a_cote():
    """LA MISE EN PAGE PORTE ICI UNE IDÉE. Empilées, elles se lisent comme une
    séquence — d'abord l'exception, ensuite les garanties — et suggèrent que la
    première éteint les secondes. Côte à côte, elles se lisent comme deux
    régimes qui coexistent, ce qu'ils sont."""
    h = _rendu()
    i = h.index('Exceptions')
    duo = h.rfind('art-an-duo', 0, i)
    assert duo >= 0, "les exceptions ne sont pas dans une colonne double"
    # LA RÈGLE VISE SA PROPRE RÈGLE CSS, PAS N'IMPORTE LAQUELLE. « 1fr 1fr »
    # apparaît trente-deux fois dans la page : chercher la chaîne seule rendait
    # ce contrôle satisfait par la mise en page d'un autre module, et il aurait
    # continué de passer après la suppression de celle-ci.
    m = re.search(r'\.art-an-duo\s*\{([^}]*)\}', PAGE)
    assert m, "la classe .art-an-duo n'est pas définie dans la feuille de style"
    assert re.search(r'grid-template-columns\s*:\s*1fr\s+1fr', m.group(1)), (
        "la colonne double n'en est pas une : .art-an-duo{%s}" % m.group(1).strip())


# ── 7. LE POINT D'INTERPRÉTATION EST ADOSSÉ AU CORPUS ────────────────────

def test_le_point_d_interpretation_existe():
    ids = {c['id'] for c in juridique.CONTROVERSES}
    assert 'rgpd-22-humain' in ids, (
        "l'analyse juridique assistée ne mobilise pas la question de "
        "l'intervention humaine significative")


def test_les_deux_lectures_s_opposent_reellement():
    """Deux lectures qui concluent pareil ne sont pas deux lectures."""
    c = [x for x in juridique.CONTROVERSES if x['id'] == 'rgpd-22-humain'][0]
    assert len(c['lectures']) == 2
    formelle, subst = c['lectures']
    assert 'formel' in formelle['nom'].lower()
    assert 'substantiel' in subst['nom'].lower()
    assert 'exclusivement' in formelle['these'].lower(), (
        "la lecture formelle ne s'appuie pas sur le mot du texte dont elle tire "
        "tout son argument")
    for attendu in ('compétent', 'annuler'):
        assert attendu in subst['these'].lower() or attendu in subst['consequence'].lower()


def test_l_arbitrage_designe_la_charge_de_la_preuve():
    c = [x for x in juridique.CONTROVERSES if x['id'] == 'rgpd-22-humain'][0]
    a = c['arbitrage'].lower()
    assert 'preuve' in a and 'responsable de traitement' in a, (
        "l'arbitrage ne dit pas sur qui pèse la charge de la preuve, qui est "
        "l'information décisive")


def test_la_requete_de_jurisprudence_vise_les_bonnes_juridictions():
    """L'art. 22 se juge devant la CNIL et le Conseil d'État sur recours ;
    interroger tout le corpus rendrait des décisions de baux."""
    spec = librejustice.REQUETES_CONTROVERSES['rgpd-22-humain']
    assert 'CNIL' in spec['filtres']['jurisdiction_type']
    assert 'intervention humaine' in spec['requete']
