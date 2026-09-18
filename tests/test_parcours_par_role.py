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
import re
import shutil
import subprocess
import tempfile

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
    # ═══ LE PROGRAMME PASSE PAR UN FICHIER, PAS PAR `node -e` ═══════════
    #
    # CE QUI S'EST PASSÉ. Le catalogue a dépassé 128 Kio et la COLLECTE de ce
    # fichier s'est mise à lever `OSError: [Errno 7] Argument list too long` —
    # c'est-à-dire que la recette entière s'interrompait avant d'avoir exécuté
    # une seule règle. Pas une règle rouge : une recette qui ne démarre pas.
    #
    # POURQUOI CE N'EST PAS RÉCUPÉRABLE EN RACCOURCISSANT LE CATALOGUE. Linux
    # limite UN SEUL argument à MAX_ARG_STRLEN = 32 pages, soit 131 072 octets,
    # indépendamment d'ARG_MAX qui vaut 2 Mio ici. Le catalogue ne fait que
    # grandir : la limite serait franchie à nouveau au parcours suivant.
    # Le fichier temporaire n'a pas de plafond de cet ordre.
    programme = prelude + src + '\nconsole.log(JSON.stringify(%s));' % nom
    with tempfile.TemporaryDirectory() as d:
        chemin = os.path.join(d, 'catalogue.js')
        io.open(chemin, 'w', encoding='utf-8').write(programme)
        r = subprocess.run([NODE, chemin], capture_output=True, text=True,
                           timeout=60)
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


# ═══════════════════════════════════════════════════════════════════════════
#  LA LIMITE QUI A ARRÊTÉ LA RECETTE ENTIÈRE, ET QUI NE PRÉVIENT PAS
# ═══════════════════════════════════════════════════════════════════════════
#
# CE QUI S'EST PASSÉ. Sept parcours de plus, et la COLLECTE de ce fichier a
# levé `OSError: [Errno 7] Argument list too long`. Pas une règle rouge : une
# recette qui ne démarre pas, et dont le message ne nomme ni le catalogue ni
# la cause.
#
# POURQUOI ÇA NE SE VOIT PAS VENIR. Linux limite UN SEUL argument à
# MAX_ARG_STRLEN = 32 pages, soit 131 072 octets — indépendamment d'ARG_MAX,
# qui vaut 2 Mio ici et qu'on regarde d'abord parce que c'est celui que
# `getconf` affiche. Le catalogue ne fait que grandir : la limite serait
# franchie à nouveau au parcours suivant.

_MAX_ARG_STRLEN = 131072


def test_le_catalogue_ne_passe_plus_par_un_argument_de_ligne_de_commande():
    """LA CORRECTION DE FOND, VÉRIFIÉE À LA SOURCE. Ce fichier écrit son
    programme dans un fichier temporaire ; `node -e` aurait replongé sous la
    limite au premier parcours ajouté."""
    src = io.open(os.path.abspath(__file__), encoding="utf-8").read()
    corps = src[src.index("def _tableau("):src.index("\nPARCOURS = ")]
    assert "'-e'" not in corps and '"-e"' not in corps, (
        "le programme repasse par `node -e` : la recette s'arrêtera à la "
        "collecte dès que le catalogue franchira 128 Kio")
    assert "tempfile" in corps, (
        "le programme doit passer par un fichier : c'est ce qui le libère de "
        "MAX_ARG_STRLEN")


def test_le_catalogue_a_DEJA_franchi_la_limite_que_la_correction_leve():
    """LE GARDE-FOU DE LA RÈGLE PRÉCÉDENTE, et il n'est pas décoratif. Si le
    catalogue repassait sous 128 Kio — un élagage, une refonte —, la règle
    ci-dessus resterait verte sans plus rien protéger, et quelqu'un
    « simplifierait » en revenant à `node -e`. Tant que cette règle-ci passe,
    on sait que la correction sert à quelque chose AUJOURD'HUI."""
    d = MOTEUR.index("var GUIDED_PATHS = [")
    f = MOTEUR.index("\n];", d)
    octets = len(MOTEUR[d:f + 3].encode("utf-8"))
    assert octets > _MAX_ARG_STRLEN, (
        "le catalogue ne fait plus que %d octets, sous la limite de %d : la "
        "règle précédente ne protège plus rien de mesurable"
        % (octets, _MAX_ARG_STRLEN))


def test_le_garde_fou_de_conftest_attrape_l_argument_trop_long():
    """LA COUVERTURE QUE LA RÈGLE PRÉCÉDENTE NE PEUT PAS DONNER.

    Dix autres fichiers de recette évaluent des morceaux de sentinel.page.js
    par `node -e`, chacun avec ses propres bornes de découpe. Aucune lecture
    statique ne dit quelle taille ils passeront : il faudrait les exécuter.
    Chacun tombera donc le jour où son bloc franchira la limite — et tombera
    de la même façon : à la COLLECTE, avec un message qui nomme
    l'interpréteur, qui n'y est pour rien.

    `conftest.py` enveloppe donc `subprocess.run` et refuse l'appel AVANT
    l'OS, avec un message qui nomme le programme, sa taille, la limite et la
    correction. Cette règle vérifie que l'enveloppe est en place et qu'elle
    MORD — pas qu'elle existe."""
    import subprocess as sp
    import conftest

    assert sp.run is not conftest._run_origine, (
        "`subprocess.run` n'est plus enveloppé : une panne de collecte "
        "reviendra sans diagnostic")

    trop = "x" * (conftest.MAX_ARG_STRLEN + 1)
    with pytest.raises(AssertionError) as capture:
        sp.run(["/bin/true", trop], capture_output=True)
    message = str(capture.value)
    assert "MAX_ARG_STRLEN" in message
    assert "fichier temporaire" in message, (
        "le message doit nommer la correction, pas seulement la panne : %r"
        % message[:200])

    # LE TÉMOIN INVERSE : un argument ordinaire passe, sinon l'enveloppe
    # casserait tous les appels de la recette au lieu d'un seul.
    ok = sp.run(["/bin/true", "court"], capture_output=True)
    assert ok.returncode == 0


def test_aucun_fichier_de_recette_ne_passe_un_bloc_trop_gros_a_node_e():
    """LA MARGE RESTANTE, POUR LES BLOCS QU'UNE LECTURE STATIQUE RÉSOUT.

    CE QU'ELLE COUVRE : les fichiers qui nomment leur tableau en clair —
    `MOTEUR.index('var ARTICLES = [')`. On peut alors mesurer exactement ce
    qui partira sur la ligne de commande, et le dire avant la panne.

    CE QU'ELLE NE COUVRE PAS, ET C'EST DIT : les fichiers qui construisent
    leur programme par bornes calculées. Pour ceux-là, le garde-fou de
    `conftest.py` prend le relais à l'exécution — il ne prévient pas, mais il
    diagnostique.

    LE SEUIL EST À 80 % DE LA LIMITE, pas à 100 %. Prévenir au moment exact
    où ça casse ne prévient de rien."""
    dossier = os.path.dirname(os.path.abspath(__file__))
    serres, lus = [], []
    for nom in sorted(os.listdir(dossier)):
        if not nom.startswith("test_") or not nom.endswith(".py"):
            continue
        src = io.open(os.path.join(dossier, nom), encoding="utf-8").read()
        if "'-e'" not in src and '"-e"' not in src:
            continue
        # LE PLUS GROS BLOC QUE CE FICHIER PEUT DÉCOUPER dans le moteur. On
        # ne devine pas lequel il prend : on prend le pire cas parmi les
        # tableaux qu'il nomme.
        for tableau in re.findall(r"index\('var (\w+) = \['\)", src) or []:
            try:
                d = MOTEUR.index("var %s = [" % tableau)
                f = MOTEUR.index("\n];", d)
            except ValueError:
                continue
            octets = len(MOTEUR[d:f + 3].encode("utf-8"))
            lus.append((nom, tableau, octets))
            if octets > _MAX_ARG_STRLEN * 0.8:
                serres.append("%s → %s : %d octets" % (nom, tableau, octets))
    assert lus, (
        "aucun bloc n'a pu être résolu : la règle ne mesure plus rien. Soit "
        "plus aucun fichier n'emploie `node -e` — et elle peut partir —, "
        "soit la forme d'appel a changé et elle est devenue vide.")
    assert not serres, (
        "ces fichiers passent à `node -e` un bloc proche ou au-delà de %d "
        "octets — ils s'arrêteront à la collecte : %s"
        % (_MAX_ARG_STRLEN, " ; ".join(serres)))
