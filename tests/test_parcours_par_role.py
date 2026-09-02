"""AUCUN PARCOURS NE SUIVAIT LA TAXONOMIE DU RÈGLEMENT, ET VINGT-TROIS PANNEAUX
N'ÉTAIENT ATTEINTS PAR AUCUN CHEMIN DE LECTURE.

CE QUI A DÉCLENCHÉ CE FICHIER. Le relevé du 28 août 2026 : les seize parcours
guidés de Sentinel suivent des MÉTIERS — directeur de programme, DPO, risk
manager, directeur de centre de données. C'est utile. Ce n'est pas la façon
dont le règlement s'organise : lui répartit les obligations entre fournisseur,
déployeur, importateur et distributeur, et c'est cette répartition qui décide
de ce que chacun doit. Un client qui savait exactement ce qu'il est au sens de
l'IA Act n'avait aucun chemin à sa mesure.

Le même relevé montrait vingt-trois panneaux sur soixante-dix-huit qu'aucun
parcours n'atteignait — dont « Découverte Shadow AI », que le guide
d'application place en tête de ce que doit faire un déployeur, et
« Obligations article par article », qui porte les articles 43, 47, 48 et 49
sans lesquels aucune mise sur le marché n'est régulière.

CE QUE CES RÈGLES GARDENT. Que les deux parcours par rôle existent et suivent
les obligations du rôle qu'ils annoncent ; que chaque étape mène à un panneau
QUI EXISTE — une étape dont l'identifiant ne correspond à rien n'affiche pas
d'erreur, elle ne va simplement nulle part ; que le catalogue et les familles
affichées ne divergent pas ; et que les quatre panneaux réintroduits le
restent.
"""
import io
import json
import os
import shutil
import subprocess

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOTEUR = io.open(os.path.join(ICI, 'sentinel.page.js'), encoding='utf-8').read()
PAGE = io.open(os.path.join(ICI, 'sentinel.html'), encoding='utf-8').read()
NODE = shutil.which('node')


def _tableau(nom):
    """Évalue une déclaration du fichier plutôt que de la lire au motif.

    Les parcours sont des objets JavaScript avec apostrophes échappées,
    guillemets typographiques et séquences unicode. Les lire à l'expression
    rationnelle marche jusqu'au jour où une description contient « id: » ;
    l'évaluer donne exactement ce que la page emploie."""
    if not NODE:
        pytest.skip('node absent : le catalogue des parcours ne peut pas être évalué')
    d = MOTEUR.index('var %s = [' % nom)
    f = MOTEUR.index('\n];', d)
    src = MOTEUR[d:f + 3]
    # LES CONSTANTES DONT LE CATALOGUE DÉPEND. Une étape des parcours « centres
    # de données » interpole `DC_MILLESIME` dans sa liste de sources : évaluer
    # le tableau seul échoue sur un ReferenceError. On reprend la déclaration
    # telle qu'elle est écrite, plutôt que d'en fabriquer une — une valeur
    # inventée ici ferait passer un contrôle sur autre chose que le fichier.
    prelude = ''
    for constante in ('DC_MILLESIME',):
        m = __import__('re').search(r'^var %s = .*;$' % constante, MOTEUR, __import__('re').M)
        if m:
            prelude += m.group(0) + '\n'
    r = subprocess.run([NODE, '-e', prelude + src + '\nconsole.log(JSON.stringify(%s));' % nom],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        pytest.fail('%s ne s\'évalue pas :\n%s' % (nom, (r.stderr or '')[-1200:]))
    return json.loads(r.stdout)


PARCOURS = _tableau('GUIDED_PATHS')
FAMILLES = _tableau('GP_FAMILLES')
PANNEAUX = set(__import__('re').findall(r'id="p-([a-z0-9-]+)"', PAGE))


def test_le_catalogue_se_lit():
    assert len(PARCOURS) >= 18, (
        "le catalogue ne compte que %d parcours : les deux parcours par rôle "
        "ont-ils disparu ?" % len(PARCOURS))
    assert PANNEAUX, "aucun panneau reconnu dans la page : le contrôle doit être revu"


# ── CHAQUE ÉTAPE MÈNE QUELQUE PART ───────────────────────────────────────

def test_toute_etape_de_parcours_mene_a_un_panneau_existant():
    """UNE ÉTAPE MORTE NE SE VOIT PAS. L'identifiant ne correspond à rien, le
    clic n'ouvre rien, aucune erreur n'est levée — le lecteur croit avoir mal
    cliqué et poursuit. C'est le défaut le moins visible d'un parcours guidé."""
    morts = []
    for p in PARCOURS:
        for e in p.get('steps', []):
            if e.get('id') not in PANNEAUX:
                morts.append('%s → %s' % (p['id'], e.get('id')))
    assert not morts, (
        "étape(s) de parcours pointant vers un panneau inexistant : %s"
        % ', '.join(morts))


@pytest.mark.parametrize('champ', ['label', 'action', 'gain'])
def test_chaque_etape_dit_quoi_faire_et_ce_que_cela_apporte(champ):
    """Une étape sans « gain » est une consigne sans raison : le lecteur
    l'exécute ou la saute au hasard."""
    vides = []
    for p in PARCOURS:
        for e in p.get('steps', []):
            if not (e.get(champ) or '').strip():
                vides.append('%s → %s' % (p['id'], e.get('id')))
    assert not vides, "étape(s) sans « %s » : %s" % (champ, ', '.join(vides))


# ── LE CATALOGUE ET LES FAMILLES NE DIVERGENT PAS ────────────────────────

def test_toute_famille_ne_nomme_que_des_parcours_existants():
    connus = {p['id'] for p in PARCOURS}
    fantomes = [i for f in FAMILLES for i in f['ids'] if i not in connus]
    assert not fantomes, (
        "famille(s) nommant un parcours absent du catalogue : %s — la liste "
        "affichera une entrée qui n'ouvre rien" % ', '.join(fantomes))


def test_aucun_parcours_n_est_range_dans_deux_familles():
    vus, doublons = set(), []
    for f in FAMILLES:
        for i in f['ids']:
            if i in vus:
                doublons.append(i)
            vus.add(i)
    assert not doublons, "parcours rangé(s) dans deux familles : %s" % ', '.join(doublons)


def test_les_parcours_par_role_sont_declares_dans_une_famille():
    """Un parcours absent des familles retombe dans « Autres parcours ». Ce
    n'est pas une panne, mais pour ces deux-là c'en serait une : ils existent
    précisément pour être trouvés par un lecteur qui raisonne en rôles."""
    declares = {i for f in FAMILLES for i in f['ids']}
    for p in ('role_deployeur', 'role_fournisseur'):
        assert p in declares, (
            "%s n'est déclaré dans aucune famille : il se retrouvera dans "
            "« Autres parcours », loin de ce qu'il sert" % p)


# ── LES DEUX PARCOURS SUIVENT LES OBLIGATIONS DU RÔLE QU'ILS ANNONCENT ──

def _parcours(pid):
    trouve = [p for p in PARCOURS if p['id'] == pid]
    assert trouve, "le parcours %s a disparu du catalogue" % pid
    return trouve[0]


def _texte(p):
    return ' '.join([p.get('pitch', '')] + [
        ' '.join([e.get('label', ''), e.get('action', ''), e.get('gain', ''), e.get('tip', '')])
        for e in p['steps']])


def test_le_parcours_deployeur_couvre_les_obligations_du_deployeur():
    """L'article 26 n'apparaissait dans AUCUN parcours, comme il n'apparaissait
    dans aucune sortie du simulateur."""
    t = _texte(_parcours('role_deployeur'))
    for attendu in ('article 25', 'article 26(2)', 'article 26(5)', 'article 26(6)',
                    'article 26(7)', 'article 26(11)', 'article 27', 'article 86'):
        assert attendu in t, (
            "le parcours du déployeur ne traite pas l'%s" % attendu)


@pytest.mark.parametrize('pid,destinations', [
    ('role_deployeur', ['shadow-ai', 'simulateur', 'registre', 'fria', 'ia50', 'radar']),
    ('role_fournisseur', ['simulateur', 'registre', 'audit-ia-act', 'templates',
                          'articles', 'conformite-globale', 'radar']),
])
def test_chaque_parcours_par_role_mene_bien_aux_panneaux_qu_il_annonce(pid, destinations):
    """LE TEXTE N'EST PAS LA DESTINATION, et cette règle existe parce que
    l'autre ne suffisait pas. Une mutation qui laissait intacte l'étape
    « Analyse d'impact sur les droits fondamentaux » — son titre, sa consigne,
    sa mention de l'article 27 — mais changeait son identifiant de panneau a
    SURVÉCU au contrôle voisin : le lecteur lisait la bonne consigne et
    atterrissait sur le Registre. Vérifier que les mots sont là ne dit rien de
    l'endroit où le clic conduit."""
    atteints = [e['id'] for e in _parcours(pid)['steps']]
    manquants = [x for x in destinations if x not in atteints]
    assert not manquants, (
        "le parcours %s ne conduit plus à %s : la consigne peut rester juste, "
        "le clic n'y mène plus" % (pid, ', '.join(manquants)))


def test_le_parcours_deployeur_commence_par_le_shadow_ai():
    """Le guide d'application place cette étape en tête, et pour une raison
    littérale : on ne peut pas être déployeur conforme d'un système dont on
    ignore l'existence."""
    p = _parcours('role_deployeur')
    assert p['steps'][0]['id'] == 'shadow-ai', (
        "le parcours du déployeur commence par « %s » et non par la découverte "
        "du Shadow AI" % p['steps'][0]['id'])


def test_le_parcours_fournisseur_couvre_la_mise_sur_le_marche():
    t = _texte(_parcours('role_fournisseur'))
    for attendu in ('annexe IV', 'article 9', 'articles 43, 47, 48 et 49',
                    'article 72', 'article 73', 'marquage CE'):
        assert attendu in t, (
            "le parcours du fournisseur ne traite pas « %s » — sans quoi il "
            "décrit la conformité sans décrire la mise sur le marché" % attendu)


def test_les_deux_parcours_ne_se_confondent_pas():
    """S'ils portaient les mêmes étapes, les distinguer n'apprendrait rien —
    et ce serait la redite que ce travail cherchait justement à supprimer."""
    d = [e['id'] for e in _parcours('role_deployeur')['steps']]
    f = [e['id'] for e in _parcours('role_fournisseur')['steps']]
    communs = set(d) & set(f)
    assert len(communs) <= 3, (
        "les parcours déployeur et fournisseur partagent %d étapes sur %d et "
        "%d : ils ne décrivent plus deux régimes distincts"
        % (len(communs), len(d), len(f)))
    assert 'audit-ia-act' not in d, (
        "le parcours du déployeur envoie à l'audit des articles 9 à 17, qui "
        "sont les obligations de son FOURNISSEUR")


# ── LES PANNEAUX RÉINTRODUITS LE RESTENT ─────────────────────────────────

@pytest.mark.parametrize('panneau,pourquoi', [
    ('shadow-ai', "l'IA déjà présente sans décision — la première étape du déployeur"),
    ('ia50', "la transparence de l'article 50 et l'information des personnes"),
    ('articles', "les articles 43, 47, 48 et 49, qui conditionnent la mise sur le marché"),
    ('conformite-globale', "l'état consolidé avant signature de la déclaration UE"),
])
def test_les_panneaux_reintroduits_restent_atteignables(panneau, pourquoi):
    """Ces quatre-là n'étaient atteints par aucun parcours avant le 28 août
    2026. Les y avoir fait entrer ne vaut que tant qu'ils y restent."""
    atteints = {e['id'] for p in PARCOURS for e in p.get('steps', [])}
    assert panneau in atteints, (
        "le panneau « %s » n'est plus atteint par aucun parcours : %s"
        % (panneau, pourquoi))


# ── LE PARCOURS DE CADRAGE, ET CE QU'IL S'INTERDIT DE PROMETTRE ──────────
#
# CE QUI A DÉCLENCHÉ CE BLOC. Une offre de cabinet — cadrage stratégique et
# architecture des cas d'usage IA — décrit un métier qui va de l'idéation à
# l'industrialisation. Sentinel porte 79 panneaux et n'en a AUCUN pour trois
# points centraux de ce métier : le choix d'architecture (modèle de fondation,
# RAG, système agentique, ML prédictif), l'estimation des coûts d'infrastructure
# (compute et jetons), et les indicateurs de qualité des modèles — précision,
# latence, taux d'hallucination, explicabilité, robustesse.
#
# LA TENTATION ÉTAIT DE LES RATTACHER À UN PANNEAU VOISIN. « Cartographie des
# cas d'usage » chiffre un retour attendu : on aurait pu y accrocher le business
# case complet, et « Roadmap » aurait pu passer pour le pilotage PoC → MVP. Un
# renvoi approximatif ne se voit pas à la lecture ; il se découvre au moment où
# le lecteur ouvre le panneau et n'y trouve pas ce qu'on lui a annoncé — et il
# cesse alors de croire les treize autres étapes.
#
# Le parcours DIT donc ce qu'il ne porte pas. Ces règles gardent cette phrase :
# sans elles, la première relecture qui trouve le ton négatif la supprimerait,
# et le parcours se mettrait à promettre une couverture qu'il n'a pas.

CADRAGE = 'consultant_ia_cadrage'

# Les panneaux fermés aux plans inférieurs. Une étape qui y mène est un cul-de-sac
# pour tout lecteur qui n'a pas le plan — sans message, puisque le panneau est
# simplement absent de son menu.
RESERVES = set(json.loads(
    __import__('re').search(r'var PLAN_ENTREPRISE_ONLY = (\[[^\]]*\]);', MOTEUR)
    .group(1).replace("'", '"')))

# LE NOMBRE D'ÉTAPES RÉSERVÉES DÉJÀ CONNUES, ET C'EST UN BUDGET, PAS UN CONSTAT.
# `role_deployeur` mène à « Transparence IA Act » (art. 50), qui est réservé au
# plan Entreprise : le contenu est juste — l'article 50.4 EST une obligation du
# déployeur — mais le lecteur d'un plan inférieur n'atteint pas le panneau.
# C'était vrai avant ce bloc ; le noter interdit qu'une deuxième s'ajoute sans
# décision, sans corriger en douce un arbitrage qui n'est pas le nôtre.
RENVOIS_RESERVES_CONNUS = {('role_deployeur', 'ia50')}


def test_le_parcours_de_cadrage_existe_et_suit_l_ordre_du_metier():
    p = _parcours(CADRAGE)
    assert len(p['steps']) >= 10, (
        "le parcours de cadrage est tombé à %d étapes : il ne couvre plus "
        "l'idéation, l'arbitrage, l'industrialisation et la capitalisation"
        % len(p['steps']))
    ids = [e['id'] for e in p['steps']]
    # L'ORDRE EST LA MOITIÉ DU PARCOURS. Classer un cas d'usage après l'avoir
    # arbitré, c'est découvrir son coût réglementaire une fois le budget voté.
    assert ids.index('carto-uc') < ids.index('simulateur'), (
        "la classification IA Act passe avant la cartographie : le cadrage "
        "commencerait par la conformité au lieu du besoin métier")
    assert ids.index('simulateur') < ids.index('report'), (
        "le dossier d'arbitrage est constitué avant la classification : le "
        "comité déciderait sans connaître le coût réglementaire")
    assert ids.index('registre') < ids.index('roadmap')


def test_le_parcours_de_cadrage_couvre_les_trois_blocs_de_l_offre():
    """Idéation et opportunités ; conception vers industrialisation ;
    développement du cabinet. Un parcours qui perdrait un bloc resterait
    cohérent à la lecture — c'est pour cela qu'on le vérifie."""
    t = _texte(_parcours(CADRAGE)).lower()
    for attendu, bloc in (
            ("goulot", "idéation : partir des goulots d'étranglement du métier"),
            ("arbitrage", "business case : le dossier d'arbitrage"),
            ("poc", "pilotage de la conception à l'industrialisation"),
            ("mvp", "pilotage : le passage du PoC au MVP"),
            ("capitalis", "développement du cabinet : la capitalisation d'expertise")):
        assert attendu in t, "le parcours ne dit plus rien du bloc « %s »" % bloc


def test_le_parcours_de_cadrage_nomme_ce_que_sentinel_ne_porte_pas():
    """LA RÈGLE QUI TIENT L'HONNÊTETÉ DU PARCOURS. Trois points centraux du
    métier n'ont aucun panneau. Les taire ferait promettre au parcours une
    couverture qu'il n'a pas ; les rattacher à un panneau voisin serait pire."""
    p = _parcours(CADRAGE)
    aveux = [e for e in p['steps'] if 'NE PORTE PAS' in (e.get('tip') or '')]
    assert len(aveux) >= 2, (
        "le parcours ne nomme plus ce que Sentinel ne porte pas (%d mention(s)) "
        "— il promet désormais une couverture complète du métier" % len(aveux))
    dit = ' '.join(e['tip'] for e in aveux).lower()
    for manque in ('rag', 'agentique', 'jetons', 'hallucination'):
        assert manque in dit, (
            "le manque « %s » n'est plus nommé : le lecteur croira le trouver "
            "dans un des panneaux du parcours" % manque)


def test_le_parcours_de_cadrage_ne_mene_a_aucun_panneau_reserve():
    """Un panneau fermé au plan du lecteur n'affiche pas de refus : il est
    absent de son menu, et l'étape ne va nulle part."""
    culs_de_sac = [e['id'] for e in _parcours(CADRAGE)['steps'] if e['id'] in RESERVES]
    assert not culs_de_sac, (
        "le parcours de cadrage mène à un panneau réservé au plan Entreprise : "
        "%s — le lecteur d'un plan inférieur n'y arrivera pas, sans message"
        % ', '.join(culs_de_sac))


def test_aucun_renvoi_vers_un_panneau_reserve_ne_s_ajoute_sans_decision():
    """Le budget déclaré : les renvois connus sont nommés, un de plus doit être
    une décision. Corriger celui qui existe ne nous revient pas — le contenu de
    l'étape est juste, c'est le plan qui ferme le panneau."""
    trouves = {(p['id'], e['id']) for p in PARCOURS for e in p['steps']
               if e['id'] in RESERVES}
    nouveaux = trouves - RENVOIS_RESERVES_CONNUS
    assert not nouveaux, (
        "renvoi(s) neuf(s) vers un panneau réservé : %s"
        % ', '.join('%s → %s' % c for c in sorted(nouveaux)))
    disparus = RENVOIS_RESERVES_CONNUS - trouves
    assert not disparus, (
        "renvoi(s) réservé(s) corrigé(s) sans mettre à jour la liste : %s — "
        "une bonne nouvelle, mais la liste doit la refléter"
        % ', '.join('%s → %s' % c for c in sorted(disparus)))


def test_le_parcours_de_cadrage_est_dans_sa_propre_famille():
    """Il ne part ni d'une obligation ni d'un intitulé de poste, mais d'un
    goulot d'étranglement opérationnel. Le ranger dans « Gouvernance & IA Act »
    le ferait chercher par les mauvais lecteurs."""
    familles = [f for f in FAMILLES if CADRAGE in f['ids']]
    assert len(familles) == 1, (
        "le parcours de cadrage est dans %d famille(s)" % len(familles))
    assert 'adrage' in familles[0]['titre'] or 'aleur' in familles[0]['titre'], (
        "la famille qui porte le parcours de cadrage s'appelle « %s » : elle ne "
        "dit plus ce qu'elle range" % familles[0]['titre'])
