"""Le CADRE de l'article 50 : ce que le texte EXIGE, à côté de ce que la maison FAIT.

CE QUE CES TESTS PROTÈGENT, ET LA FAUTE QU'ILS EMPÊCHENT.

Le registre de transparence disait ce que la plateforme fait — « EN PLACE »,
ligne après ligne — sans jamais dire ce que le règlement impose. Deux défauts en
découlaient, et ce sont eux que ces règles tiennent fermés.

1. UN PARAGRAPHE JAMAIS EXAMINÉ NE SE DISTINGUE PAS D'UN OUBLI. Le § 3 —
   reconnaissance des émotions, catégorisation biométrique, obligation du
   déployeur — n'apparaissait nulle part. Il est sans objet ici ; encore
   faut-il l'écrire. Une qualification non documentée équivaut à une absence
   de qualification.

2. UN ENGAGEMENT PRÉSENTÉ COMME UNE OBLIGATION AFFAIBLIT LES VRAIES. Les
   propriétés de chaque livrable portaient « signalé comme tel au titre du
   règlement … art. 50 ». Or l'article 50 n'impose pas à un prestataire
   d'étiqueter le document qu'il rédige avec l'aide d'une IA : le 50.2 impose
   au FOURNISSEUR un marquage lisible par machine, rien de plus. La mention
   visible est un engagement de la maison — et le dire est ce qui donne sa
   valeur au marquage là où il est dû.

Ces tests vérifient des PROPRIÉTÉS, pas des libellés : que le dû change avec le
rôle dans les deux sens, que les verdicts restent dans une liste fermée, que le
document généré à l'instant porte le paragraphe, le rôle et le mot
« engagement », et qu'une propriété trop longue n'emporte plus ses voisines.
"""
import io
import os
import sys
import zipfile

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

os.environ.setdefault('AUTH_MASTER_TOKEN', 'recette_locale_idf_0123456789abcdef')

import app as application  # noqa: E402
import livrables_export  # noqa: E402


@pytest.fixture
def conseilprev(monkeypatch):
    """Client de test authentifié comme CONSEILPREV."""
    monkeypatch.setattr(application, 'sentauth_current_client',
                        lambda *a, **k: {'id': 1, 'is_conseilprev': True})
    return application.app.test_client()


# ── Les cinq paragraphes, et qui chacun oblige ─────────────────────────────

def test_les_cinq_paragraphes_sont_la_avec_un_destinataire():
    cles = [p['cle'] for p in application.IA50_PARAGRAPHES]
    for attendu in ('50.1', '50.2', '50.3', '50.4', '50.5'):
        assert attendu in cles, 'paragraphe %s absent du cadre' % attendu
    for p in application.IA50_PARAGRAPHES:
        assert p['qui'] in application.IA50_QUI, (
            'paragraphe %s : destinataire « %s » hors liste fermée' % (p['cle'], p['qui']))
        for champ in ('impose', 'n_impose_pas', 'chez_nous'):
            assert str(p.get(champ) or '').strip(), (
                'paragraphe %s : « %s » vide' % (p['cle'], champ))


def test_le_paragraphe_3_est_present_et_motive():
    """Sentinel ne fait pas de reconnaissance d'émotions. Une absence non
    motivée reste indistinguable d'un oubli : c'est pour cela que le § 3 doit
    figurer AVEC son motif de mise hors d'objet, et non disparaître."""
    p3 = [p for p in application.IA50_PARAGRAPHES if p['cle'] == '50.3']
    assert p3, 'le § 3 a disparu du cadre'
    dit = p3[0]['chez_nous']
    assert 'SANS OBJET' in dit.upper(), 'le § 3 est là sans dire pourquoi il ne joue pas'
    assert 'biometrique' in dit.lower() or 'emotions' in dit.lower(), (
        'la mise hors d\'objet du § 3 ne dit pas ce qui est absent')
    assert p3[0]['qui'] == 'deployeur'


def test_le_du_du_fournisseur_n_est_pas_celui_du_deployeur():
    """Dans les DEUX SENS. Une règle qui vérifierait seulement ce que chaque
    rôle doit resterait verte si le calcul rendait tout à tout le monde."""
    f = application.ia50_du_pour('fournisseur')
    d = application.ia50_du_pour('deployeur')
    assert f['paragraphes'] == ['50.1', '50.2'], f['paragraphes']
    assert d['paragraphes'] == ['50.3', '50.4'], d['paragraphes']
    assert '50.3' not in f['paragraphes'] and '50.4' not in f['paragraphes']
    assert '50.1' not in d['paragraphes'] and '50.2' not in d['paragraphes']
    # Le § 5 ne crée pas d'obligation : il régit la forme de celles qui jouent.
    assert f['modalites'] == d['modalites'] == ['50.5']
    assert f['connu'] and d['connu']


def test_un_role_inconnu_ne_doit_rien_et_le_dit():
    r = application.ia50_du_pour('sous-traitant')
    assert r['connu'] is False
    assert r['paragraphes'] == []


# ── La grille des sept situations ──────────────────────────────────────────

def test_les_sept_cas_portent_un_verdict_de_la_liste_fermee():
    assert len(application.IA50_CAS) == 7, len(application.IA50_CAS)
    for c in application.IA50_CAS:
        assert c['verdict'] in application.IA50_VERDICTS, (
            'cas %s : verdict « %s » hors liste fermée' % (c['cle'], c['verdict']))
        assert str(c.get('motif') or '').strip(), 'cas %s sans motif' % c['cle']
        assert str(c.get('chez_nous') or '').strip(), 'cas %s sans application' % c['cle']
    # Les quatre verdicts servent : une liste fermée dont trois valeurs ne
    # seraient jamais employées ne fermerait rien.
    rendus = {c['verdict'] for c in application.IA50_CAS}
    assert rendus == set(application.IA50_VERDICTS), rendus


def test_le_livrable_client_n_est_pas_impose_par_l_article_50():
    """Le cas qui a motivé toute la correction : un prestataire qui rédige un
    livrable avec l'aide d'une IA ne doit rien au titre de l'article 50."""
    c = [x for x in application.IA50_CAS if x['cle'] == 'livrable_client']
    assert c, 'le cas du livrable client a disparu de la grille'
    c = c[0]
    assert c['verdict'] == 'non_en_principe', c['verdict']
    assert c['paragraphe'] == 'aucun'
    assert 'engagement' in c['chez_nous'].lower(), (
        'le cas ne dit pas que la mention portée sur nos livrables est un engagement')


def test_le_support_commercial_reste_a_verifier():
    """Ne pas transformer une nuance juridique en verdict : là où la lecture
    dit « à vérifier », le cadre ne doit pas trancher."""
    c = [x for x in application.IA50_CAS if x['cle'] == 'support_commercial'][0]
    assert c['verdict'] == 'a_verifier'


# ── Le troisième niveau ────────────────────────────────────────────────────

def test_le_troisieme_niveau_nomme_les_faux_avis():
    """« L'AI Act ne s'applique pas » ne veut pas dire « rien à faire »."""
    assert len(application.IA50_AUTRES_OBLIGATIONS) == 3
    cles = {o['cle'] for o in application.IA50_AUTRES_OBLIGATIONS}
    assert cles == {'contrat', 'consommation', 'rgpd'}, cles
    conso = [o for o in application.IA50_AUTRES_OBLIGATIONS if o['cle'] == 'consommation'][0]
    tout = ' '.join(conso['points']).lower()
    assert 'faux avis' in tout, 'le droit de la consommation est cité sans les faux avis'
    rgpd = [o for o in application.IA50_AUTRES_OBLIGATIONS if o['cle'] == 'rgpd'][0]
    assert 'TRAITEMENT' in ' '.join(rgpd['points']), (
        'le RGPD est cité sans rappeler que la transparence porte sur le traitement')


# ── Les routes ─────────────────────────────────────────────────────────────

def test_le_cadre_est_reserve_a_conseilprev():
    r = application.app.test_client().get('/api/ia50/cadre')
    assert r.status_code == 403, r.status_code


def test_le_cadre_servi_porte_les_cinq_paragraphes(conseilprev):
    d = conseilprev.get('/api/ia50/cadre').get_json()
    assert d['ok'] is True
    assert len(d['paragraphes']) == 5
    assert len(d['cas']) == 7
    assert len(d['autres_obligations']) == 3
    assert 'ciblee' in d['point_cle'] or 'ciblée' in d['point_cle']
    assert d['du']['fournisseur']['paragraphes'] == ['50.1', '50.2']


def test_le_registre_sert_le_du_calcule_et_il_change_avec_le_role(conseilprev):
    """Le dû n'est jamais stocké dans la ligne : il est calculé depuis la
    doctrine et joint au service. Deux exemplaires dériveraient."""
    d = conseilprev.get('/api/ia50/usages').get_json()
    assert d['ok'] is True
    assert d['usages'], 'registre vide'
    vus = set()
    for u in d['usages']:
        assert 'du' in u, 'une ligne servie sans son dû'
        attendu = application.ia50_du_pour(u['role'])['paragraphes']
        assert u['du']['paragraphes'] == attendu
        vus.add(tuple(attendu))
    assert (('50.1', '50.2') in vus) and (('50.3', '50.4') in vus), (
        'le registre par défaut ne fait pas jouer les deux rôles : la règle ne '
        'prouverait pas que le dû change')


def test_la_colonne_du_nest_pas_une_colonne_de_la_table():
    """La doctrine est du code, le registre est une table. Si « du » entrait
    dans le schéma, une ligne ancienne garderait un dû périmé."""
    ddl = [l for l in open(os.path.join(ICI, 'app.py'), encoding='utf-8')
           if 'CREATE TABLE IF NOT EXISTS ia50_usages' in l]
    assert ddl, 'schéma du registre introuvable'
    assert ' du ' not in ddl[0], 'le dû a été stocké en base : il dérivera'


# ── Les mesures, et leur pouvoir de discrimination ─────────────────────────

def test_la_mesure_du_cadre_est_verte_sur_le_cadre_reel():
    r = application._ia50_mesure_cadre()
    assert r['statut'] == 'conforme', r['preuve']


def test_la_mesure_du_cadre_tombe_si_le_paragraphe_3_disparait(monkeypatch):
    monkeypatch.setattr(application, 'IA50_PARAGRAPHES',
                        [p for p in application.IA50_PARAGRAPHES if p['cle'] != '50.3'])
    r = application._ia50_mesure_cadre()
    assert r['statut'] == 'non-conforme', (
        'le § 3 retiré, la mesure dit encore conforme : elle ne mesure rien')
    assert '50.3' in r['preuve']


def test_la_mesure_du_cadre_tombe_si_le_paragraphe_3_perd_son_motif(monkeypatch):
    """Présent mais muet, le § 3 ne prouve plus qu'il a été examiné."""
    faux = [dict(p) for p in application.IA50_PARAGRAPHES]
    for p in faux:
        if p['cle'] == '50.3':
            p['chez_nous'] = 'Rien a signaler.'
    monkeypatch.setattr(application, 'IA50_PARAGRAPHES', faux)
    r = application._ia50_mesure_cadre()
    assert r['statut'] == 'non-conforme', r['preuve']


def test_la_mesure_du_cadre_tombe_sur_un_verdict_hors_liste(monkeypatch):
    faux = [dict(c) for c in application.IA50_CAS]
    faux[0]['verdict'] = 'plutot oui'
    monkeypatch.setattr(application, 'IA50_CAS', faux)
    r = application._ia50_mesure_cadre()
    assert r['statut'] == 'non-conforme', r['preuve']
    assert 'hors liste' in r['preuve']


def test_la_mesure_des_roles_signale_une_ligne_qui_invoque_le_mauvais_paragraphe():
    """Elle ne TRANCHE pas — qualifier un usage est une décision juridique.
    Elle refuse seulement que la qualification et la référence se contredisent
    sans que personne ne le voie."""
    r = application._ia50_mesure_roles([
        {'systeme': 'Export de rapports', 'role': 'deployeur', 'contenu': '',
         'marquage': 'metadonnees au titre de l\'art. 50.2', 'etiquetage': '',
         'exception': 'Aucune'}])
    assert r['statut'] == 'partiel', r['preuve']
    assert 'fournisseur' in r['preuve'], (
        'la mesure signale l\'écart sans dire qui doit vraiment ce paragraphe')


def test_la_mesure_des_roles_laisse_passer_une_ligne_coherente():
    r = application._ia50_mesure_roles([
        {'systeme': 'Actualites', 'role': 'deployeur', 'contenu': '',
         'marquage': '', 'etiquetage': 'exception invoquee',
         'exception': 'Controle editorial humain (art. 50 par. 4)'}])
    assert r['statut'] == 'conforme', r['preuve']


def test_un_registre_illisible_nest_pas_conforme():
    assert application._ia50_mesure_roles(None)['statut'] == 'non-mesurable'


# ── Le marquage des documents ──────────────────────────────────────────────

def _proprietes(meta):
    blob = livrables_export.build_docx('# Controle\n\nTexte.\n', meta)
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        return z.read('docProps/core.xml').decode('utf-8', 'replace')


def test_la_note_nomme_le_fournisseur_le_50_2_et_l_engagement():
    core = _proprietes({'ia': True, 'label': 'Controle', 'model': 'trame-locale'})
    assert 'art. 50.2' in core, 'le paragraphe qui impose le marquage n\'est pas nommé'
    assert 'fournisseur' in core, 'le rôle qui doit ce marquage n\'est pas nommé'
    assert 'engagement' in core, (
        'la mention visible n\'est pas donnée pour ce qu\'elle est : un engagement')


def test_la_note_tient_dans_la_limite_des_proprietes_word():
    note = livrables_export._marque_ia({'ia': True, 'model': 'claude'})['note']
    assert len(note) <= livrables_export.LIMITE_PROPRIETE, len(note)


def test_une_propriete_trop_longue_n_emporte_pas_les_autres(monkeypatch):
    """La faute apprise à l'identique ailleurs : les sept propriétés étaient
    posées dans un seul `try`. Une note refusée par python-docx emportait EN
    SILENCE la note et tout ce qui la suivait — l'auteur compris."""
    vrai = livrables_export._marque_ia

    def enorme(meta):
        m = dict(vrai(meta))
        m['note'] = 'x' * 400
        return m

    monkeypatch.setattr(livrables_export, '_marque_ia', enorme)
    core = _proprietes({'ia': True, 'label': 'Controle', 'model': 'claude'})
    assert 'CONSEILPREV' in core, (
        'la note trop longue a emporté l\'auteur : les propriétés retombent '
        'dans un seul essai')


def test_la_mesure_des_documents_tombe_si_la_note_redevient_generale(monkeypatch):
    """La mutation qui compte : revenir à « au titre du … art. 50 » sans
    paragraphe ni rôle. L'ancien critère (« art. 50 » en sous-chaîne) restait
    vert des deux côtés de la correction — il ne mesurait pas ce qu'il
    annonçait."""
    monkeypatch.setattr(livrables_export, 'MARQUE_REF',
                        'Reglement (UE) 2024/1689, art. 50')

    def ancienne(meta):
        return {'marque': livrables_export.MARQUE_IA,
                'producteur': 'CONSEILPREV',
                'mots_cles': 'AI-generated',
                'note': 'Contenu produit avec l\'assistance d\'un systeme d\'intelligence '
                        'artificielle et signale comme tel au titre du Reglement (UE) '
                        '2024/1689, art. 50.'}

    monkeypatch.setattr(livrables_export, '_marque_ia', ancienne)
    r = application._ia50_mesure_documents()
    assert r['statut'] == 'non-conforme', (
        'la note revenue à sa rédaction fautive, la mesure dit encore conforme')
    assert '50.2' in r['preuve']


# ── La page sert le cadre, et ne le recopie pas ────────────────────────────

def test_la_page_porte_les_ancres_du_cadre():
    page = application._ia50_page('sentinel.html')
    for ancre in ('ia50-pointcle', 'ia50-paragraphes', 'ia50-cas', 'ia50-autres'):
        assert 'id="%s"' % ancre in page, 'ancre %s absente de la page' % ancre


def test_le_script_va_chercher_le_cadre_au_lieu_de_le_recopier():
    js = open(os.path.join(ICI, 'sentinel.page.js'), encoding='utf-8').read()
    assert "'/api/ia50/cadre'" in js, 'la page ne demande jamais le cadre'
    assert 'ia50Cadre()' in js, 'le cadre est écrit mais jamais rendu'
    # Ce qui serait la faute : recopier les libellés du cadre dans le script.
    assert 'reconnaissance des emotions' not in js.lower(), (
        'le texte du cadre est recopié dans la page : il dérivera du code')


def test_l_attestation_porte_le_du():
    """L'attestation est ce qu'on produit en cas de contrôle. Sans le dû, elle
    présente les engagements de la maison comme des obligations légales."""
    js = open(os.path.join(ICI, 'sentinel.page.js'), encoding='utf-8').read()
    i = js.index('window.ia50Rapport')
    bloc = js[i:i + 4000]
    assert '/api/ia50/cadre' in bloc, 'l\'attestation n\'embarque pas le cadre'
    assert 'D\\u00fb (art. 50)' in bloc, 'l\'attestation ne porte pas la colonne « Dû »'
