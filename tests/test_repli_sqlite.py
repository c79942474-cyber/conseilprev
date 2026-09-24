"""LE REPLI SQLITE — ce qu'il coûte, et pourquoi il doit le dire.

CE QUI S'EST PASSÉ. Un nouveau service a été mis en ligne sans `DATABASE_URL`.
L'application est repartie sur son repli SQLite et l'a annoncé ainsi :

    INFO REGISTRE_IA — moteur actif : SQLite (local, fallback dev)

Une ligne d'information, parmi vingt au démarrage, avec le mot « dev ». En
développement, elle est exacte. En ligne, elle signifie tout autre chose : le
fichier est écrit DANS le dossier de l'application, reconstruit depuis git à
chaque déploiement, et `registre_ia.db` n'est pas suivi par git. Les tables du
registre repartent donc VIDES à chaque mise en ligne — comptes, contrats,
factures, événements Stripe (dont dépend l'idempotence des notifications de
paiement), preuves de consentement et registre RGPD compris.

La preuve était dans le même journal, deux lignes plus haut :
`CONSEILPREV_CLIENT_CREATED id=1` — l'application venait de recréer son
premier client, parce que la table était vide.

ET DEUX WORKERS ONT AGGRAVÉ LE CAS. Tant que le service tournait avec un seul
processus, un seul ouvrait ce fichier. La correction du timeout de worker en a
mis deux — soit jusqu'à seize fils écrivains sur un fichier qui n'en admet
qu'un à la fois. Sans `journal_mode=WAL` ni `busy_timeout`, la seconde
écriture rend « database is locked », que le visiteur lit en erreur 500.

CE QUE CES CONTRÔLES GARDENT : que le repli reste utilisable à plusieurs
processus, et qu'il ne puisse plus être silencieux.
"""
import io
import os
import re
import sqlite3
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

os.environ.setdefault('AUTH_MASTER_TOKEN', 'recette_locale_idf_0123456789abcdef')
os.environ.setdefault('FLASK_SECRET_KEY', 'recette-repli')
os.environ.pop('DATABASE_URL', None)

import app as application  # noqa: E402

SOURCE = io.open(os.path.join(ICI, 'app.py'), encoding='utf-8').read()


@pytest.fixture
def connexion():
    c = application.registre_get_db()
    yield c
    try:
        c.close()
    except Exception:                                              # noqa: BLE001
        pass


# ── LE REPLI DOIT SURVIVRE À PLUSIEURS PROCESSUS ─────────────────────────

def test_une_base_NEUVE_part_en_mode_wal(tmp_path, monkeypatch):
    """SUR UN FICHIER NEUF, ET C'EST TOUT L'INTÉRÊT. Le mode de journal est
    inscrit DANS le fichier : une base déjà en WAL le reste, si bien qu'un
    contrôle mené sur la base du poste de développement passe même quand la
    ligne qui l'active a disparu — c'est la mutation qui a survécu au premier
    passage. Or chaque déploiement recrée un fichier neuf, en mode « delete ».
    C'est donc une base neuve qu'il faut éprouver."""
    assert application.REGISTRE_USE_PG is False, (
        'ce contrôle mesure le repli : il ne veut rien dire sous PostgreSQL')
    neuve = tmp_path / 'registre_neuf.db'
    monkeypatch.setattr(application, 'REGISTRE_SQLITE_PATH', str(neuve))
    c = application.registre_get_db()
    try:
        mode = c.execute('PRAGMA journal_mode').fetchone()[0]
    finally:
        c.close()
    assert str(mode).lower() == 'wal', (
        'une base neuve démarre en « %s » : une écriture bloquera toutes les '
        'lectures, et avec deux workers c\'est une erreur 500' % mode)


def test_une_ecriture_attend_le_verrou_au_lieu_dabandonner(connexion):
    """L'attente du verrou vient de `timeout=` passé à `sqlite3.connect` —
    ce paramètre EST le `busy_timeout`, en secondes. Sans lui, Python
    abandonne à cinq secondes et rend « database is locked »."""
    busy = connexion.execute('PRAGMA busy_timeout').fetchone()[0]
    assert busy >= 10000, (
        'busy_timeout à %s ms : trop court pour deux workers de huit fils' % busy)
    assert busy == application.REGISTRE_SQLITE_ATTENTE * 1000


def test_le_delai_dattente_est_reglable_sans_redeployer():
    assert "REGISTRE_SQLITE_ATTENTE = int(os.environ.get(" in SOURCE


def test_deux_connexions_simultanees_ecrivent_sans_se_bloquer():
    """LA MESURE, PAS L'INTENTION. Deux connexions ouvertes en même temps,
    comme deux workers : la seconde doit pouvoir écrire."""
    a = application.registre_get_db()
    b = application.registre_get_db()
    try:
        a.execute('CREATE TABLE IF NOT EXISTS recette_verrou (n INTEGER)')
        a.commit()
        b.execute('INSERT INTO recette_verrou (n) VALUES (1)')
        b.commit()
        a.execute('INSERT INTO recette_verrou (n) VALUES (2)')
        a.commit()
        n = a.execute('SELECT COUNT(*) FROM recette_verrou').fetchone()[0]
        assert n >= 2
    finally:
        try:
            a.execute('DROP TABLE IF EXISTS recette_verrou')
            a.commit()
        except Exception:                                          # noqa: BLE001
            pass
        a.close()
        b.close()


# ── LE REPLI NE PEUT PLUS ÊTRE SILENCIEUX ────────────────────────────────

def _bloc_annonce():
    """Le code qui annonce le moteur retenu, et rien d'autre.

    L'ANCRAGE EST PRÉCIS, ET IL A FALLU L'APPRENDRE : chercher
    « registre_init_db() » seul tombait sur un COMMENTAIRE qui cite ce nom
    quelques milliers de lignes plus haut, et le contrôle lisait alors un tout
    autre morceau de fichier en croyant lire celui-ci."""
    ancre = 'try:\n    registre_init_db()\n    if REGISTRE_USE_PG:'
    assert SOURCE.count(ancre) == 1, (
        "le bloc d'annonce du moteur est introuvable ou dupliqué")
    i = SOURCE.index(ancre)
    return SOURCE[i:SOURCE.index('except Exception as _e:', i)]


def test_le_repli_sannonce_en_erreur_pas_en_information():
    """Une ligne « INFO » ne se voit pas dans un journal de démarrage qui en
    compte vingt. C'est exactement ce qui s'est produit."""
    bloc = _bloc_annonce()
    i = bloc.index('else:')
    assert 'logger.error(' in bloc[i:], (
        'le repli SQLite s\'annonce encore en INFO : il passera inaperçu')
    assert 'logger.info(' in bloc[:i], (
        'PostgreSQL n\'a pas à crier : ce n\'est pas une anomalie')


def _message_derreur():
    """Le TEXTE réellement journalisé — pas le commentaire qui l'entoure.

    Une première version cherchait ces mots dans tout le bloc. Le commentaire
    au-dessus explique le défaut et cite « DATABASE_URL » : retirer la mention
    du VRAI message laissait donc le contrôle vert. C'est la troisième fois
    dans ce dépôt qu'une règle prend de la prose pour du code."""
    bloc = _bloc_annonce()
    i = bloc.index('logger.error(')
    appel = bloc[i:]
    # Les seuls littéraux de chaîne de l'appel : c'est ce qui part au journal.
    return ' '.join(re.findall(r"'((?:[^'\\]|\\.)*)'", appel))


def test_lannonce_dit_la_consequence_et_le_remede():
    """« fallback dev » ne dit ni ce qu'on perd, ni comment le réparer."""
    msg = _message_derreur()
    for attendu in ('DATABASE_URL', 'VIDES', 'consentement', 'RGPD', 'Stripe'):
        assert attendu in msg, (
            'le message journalisé ne mentionne pas « %s » — il est dans un '
            'commentaire, ce qui n\'aide personne à trois heures du matin'
            % attendu)


def test_le_nombre_de_tables_est_compte_et_non_ecrit():
    """Un chiffre recopié serait faux à la première table ajoutée, et
    personne ne reviendrait le corriger."""
    bloc = _bloc_annonce()
    # ═══ LE NOM DE LA TABLE SYSTÈME EST EXIGÉ ENTIER ══════════════════
    # Une mutation qui écrivait « FROM sqlite_master_absent » SURVIVAIT : la
    # sous-chaîne « FROM sqlite_master » y est, et le test passait alors que
    # le compte ne portait plus sur rien. Une recherche de sous-chaîne sur un
    # identifiant est une mesure qui accepte tout ce qui commence pareil.
    assert re.search(r"FROM sqlite_master\b", bloc), (
        'le nombre de tables n\'est pas compté sur la base réelle')
    # Aucun nombre à deux chiffres écrit en dur dans le message lui-même.
    i = bloc.index('logger.error(')
    message = bloc[i:]
    en_dur = re.findall(r'\b\d{2,}\b', message)
    assert not en_dur, 'nombre écrit à la main dans l\'annonce : %s' % en_dur


def test_le_compte_annonce_est_celui_de_la_base_A_CET_INSTANT():
    """La mesure elle-même doit être juste — et elle l'est sur ce qui EXISTE.

    ═══ LA PRÉMISSE QUE CETTE RÈGLE PORTAIT, ET QUI ÉTAIT FAUSSE ═════════
    Elle exigeait que la base de repli porte AU MOINS autant de tables que
    `app.py` en déclare : 24 contre 36, elle tombait à chaque passage. Le
    code n'y était pour rien. Quatorze tables sont créées PARESSEUSEMENT, à
    la première utilisation de leur fonctionnalité — `_rgpd_tables2()`,
    `_form_tables()`, `_gouv_table()`, `_parcours_table()`, `_ia50_table()`
    et les trois routes `entreprise_*`. Elles n'existent pas au démarrage, et
    c'est voulu : créer trente-six tables pour un service qui n'en servira
    peut-être qu'une n'aide personne.

    L'ANNONCE, ELLE, EST JUSTE : elle dit ce qui sera perdu AU MOMENT où elle
    est écrite, c'est-à-dire ce qui existe. Vingt-quatre. La règle mesure donc
    cela — que le compte annoncé soit celui de la base à cet instant, et non
    un chiffre hérité d'un démarrage précédent.

    C'est la même faute que ce dépôt poursuit partout, retournée contre une
    règle : elle tombait pour une raison sans rapport avec ce qu'elle
    prétendait garder.
    """
    c = sqlite3.connect(application.REGISTRE_SQLITE_PATH)
    n = c.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' "
                  "AND name NOT LIKE 'sqlite_%'").fetchone()[0]
    c.close()
    assert n > 0, "la base de repli ne porte aucune table : l'annonce ne peut " \
                  "rien annoncer"
    declarees = set(re.findall(r'CREATE TABLE IF NOT EXISTS ([a-z_]+)', SOURCE))
    assert n <= len(declarees), (
        "la base porte %d tables pour %d DÉCLARÉES dans app.py : elle en "
        "contient que le code ne crée plus — un reste d'une version "
        "précédente, qui repartirait vide sans que personne l'ait voulu"
        % (n, len(declarees)))


def _fonction_contenant(source, position):
    lignes = source[:position].splitlines()
    for ligne in reversed(lignes):
        m = re.match(r"def ([a-zA-Z_0-9]+)\(", ligne)
        if m:
            return m.group(1)
    return None


def test_aucune_table_declaree_n_est_ORPHELINE():
    """CE QUE L'ANCIENNE RÈGLE CHERCHAIT SANS LE TROUVER.

    Le vrai risque n'est pas qu'une table manque au démarrage — c'est qu'une
    instruction `CREATE TABLE` soit écrite dans une fonction que PLUS RIEN
    n'appelle. Elle passerait la revue, passerait la recette, et la
    fonctionnalité échouerait à la première utilisation chez un client en
    repli, là où il n'y a ni collègue ni journal pour le dire.

    UNE ROUTE COMPTE COMME ATTEINTE, et il a fallu le mesurer pour le savoir :
    `entreprise_connecteurs`, `entreprise_entites` et `entreprise_formations`
    ne sont appelées par leur nom nulle part — ce sont des gestionnaires de
    route, joignables en HTTP. Un détecteur qui l'ignorerait signalerait trois
    fausses orphelines, et l'on apprendrait à ne plus le lire.
    """
    orphelines = []
    for m in re.finditer(r"CREATE TABLE IF NOT EXISTS ([a-z_]+)", SOURCE):
        table = m.group(1)
        fn = _fonction_contenant(SOURCE, m.start())
        if fn is None:
            orphelines.append("%s : hors de toute fonction" % table)
            continue
        appelee = len(re.findall(r"(?<![\w.])%s\s*\(" % re.escape(fn), SOURCE)) > 1
        route = re.search(r"@app\.route\([^)]*\)\s*(?:@[^\n]*\s*)*def %s\("
                          % re.escape(fn), SOURCE)
        if not appelee and not route:
            orphelines.append("%s : %s() n'est ni appelée ni servie par une "
                              "route" % (table, fn))
    assert not orphelines, (
        "instructions CREATE TABLE que rien n'atteint — la table n'existera "
        "jamais sur le repli : %s" % orphelines)


def test_le_fichier_de_repli_nest_pas_suivi_par_git():
    """S'il l'était, chaque déploiement écraserait les données en ligne par
    l'instantané du dépôt — pire que de repartir vide."""
    import subprocess
    suivis = subprocess.check_output(
        ['git', '-C', ICI, 'ls-files'], text=True).split('\n')
    assert 'registre_ia.db' not in suivis


@pytest.mark.parametrize("compagnon", ["registre_ia.db-wal", "registre_ia.db-shm"])
def test_les_compagnons_WAL_du_repli_sont_IGNORES(compagnon):
    """LE MODE WAL (registre_get_db) POSE DEUX FICHIERS À CÔTÉ DE LA BASE :
    le journal `-wal` et la mémoire partagée `-shm`. Ils existent tant
    qu'une connexion est ouverte, et restent après un arrêt brutal ou une
    lecture seule. MESURÉ : après une recette, `git status` les montrait
    comme fichiers nouveaux — prêts à partir dans un commit avec les pages
    de données qu'ils recopient. Ignorés, comme la base.
    La règle lit les motifs de .gitignore (elle vaut aussi dans une copie
    sans dépôt, où tournent les batteries), et demande à git quand il est
    là."""
    import fnmatch
    import subprocess
    motifs = [l.strip() for l in io.open(os.path.join(ICI, '.gitignore'), encoding='utf-8')
              if l.strip() and not l.lstrip().startswith('#')]
    assert any(fnmatch.fnmatch(compagnon, m) for m in motifs), (
        "%s n'est couvert par aucun motif de .gitignore" % compagnon)
    if os.path.isdir(os.path.join(ICI, '.git')):
        r = subprocess.run(['git', '-C', ICI, 'check-ignore', '-q', compagnon])
        assert r.returncode == 0, "git ne l'ignore pas : %s" % compagnon
