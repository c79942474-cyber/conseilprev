"""Le dossier d'ingénierie financière : versé tel que servi, jamais recalculé.

CE QUE CES TESTS PROTÈGENT. Les quatre moteurs récents de la page —
équipements, création de valeur, maturité, pilotage — n'entraient dans aucun
document téléchargeable : leurs chiffres mouraient à l'écran. Le dossier
« ingenierie » les verse, et ces tests garantissent les trois règles qui le
rendent honnête :

  1. LES CHARGES SONT RÉELLES. Les payloads de test sortent des moteurs
     eux-mêmes, jamais d'un dictionnaire écrit à la main — un dictionnaire
     recopié aurait cessé d'être vrai au premier changement de clé, et le
     test n'aurait plus protégé que de lui-même.
  2. UN BLOC ABSENT S'ÉCRIT. Le document dit « n'a pas été lancé » — il ne
     tait pas le bloc et n'invente rien à sa place.
  3. UN REFUS SE REPRODUIT. Une série non instruite entre dans le document
     comme refus motivé, avec les hypothèses manquantes nommées.
"""
import io
import os
import sys
import zipfile

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import equipements_it  # noqa: E402
import export_dc  # noqa: E402
import kpi_finance  # noqa: E402
import maturite_decision  # noqa: E402
import pilotage_dc  # noqa: E402


def _complements_reels():
    """Les charges telles que les routes les assemblent — mêmes appels de
    moteur, mêmes clés."""
    nomen = equipements_it.nomenclature(50000, 'dense')
    eq = {
        'ok': True,
        'nomenclature': nomen,
        'part': equipements_it.part_investissement(nomen, 1500 * 1e6, 'propre'),
        'prolongation': equipements_it.prolongation(50000, 5, 8, 'FR'),
        'scope3': equipements_it.bilan_scope3(nomen),
    }
    hyp = {'revenu_meur_an': 400, 'wacc': 8, 'is_taux': 25}
    serie = kpi_finance.serie([1200, 1800], [60, 110], 10, hyp)
    kpi = {'ok': True, 'serie': serie,
           'lecture': kpi_finance.lecture(serie, {}),
           'seuil_revenu': kpi_finance.seuil_revenu([1200, 1800], [60, 110],
                                                    10, 8, 25)}
    mat = dict(maturite_decision.diagnostic({}, {}), ok=True)
    pil = dict(pilotage_dc.piloter({}, None), ok=True)
    return {'equipements': eq, 'kpi': kpi, 'maturite': mat, 'pilotage': pil}


def test_le_dossier_existe_au_catalogue():
    cat = export_dc.catalogue()
    cles = [d['cle'] for d in cat['dossiers']]
    assert 'ingenierie' in cles
    d = next(x for x in cat['dossiers'] if x['cle'] == 'ingenierie')
    assert d['besoin_devis'] is False


def test_les_quatre_blocs_entrent_avec_leurs_chiffres():
    md = export_dc.composer('ingenierie', complements=_complements_reels())
    # Équipements : le total du moteur, pas un total local.
    nomen = _complements_reels()['equipements']['nomenclature']
    assert 'Équipements informatiques' in md
    assert export_dc._n(nomen['total_eur'], 0) in md
    assert 'Création de valeur' in md
    assert 'EVA' in md
    assert 'Maturité analytique' in md
    assert 'Pilotage, seuils et alertes' in md
    assert 'Ce que ce dossier ne dit pas' in md


def test_un_bloc_jamais_lance_est_ecrit_absent():
    c = _complements_reels()
    del c['pilotage']
    md = export_dc.composer('ingenierie', complements=c)
    assert "Pilotage, seuils et alertes" in md
    assert "n'a pas été lancé" in md
    # …et les autres blocs restent complets.
    assert 'Équipements informatiques' in md


def test_sans_aucun_complement_le_document_le_dit_partout():
    md = export_dc.composer('ingenierie', complements=None)
    assert md.count("n'a pas été lancé") >= 4
    assert 'Ce que ce dossier ne dit pas' in md


def test_un_refus_du_moteur_entre_comme_refus():
    """Une série sans revenu n'est pas instruite : le moteur refuse, et le
    document reproduit le refus avec les hypothèses manquantes nommées."""
    serie = kpi_finance.serie([1200, 1800], [60, 110], 10, {})
    assert not serie.get('instruit')
    c = {'kpi': {'ok': True, 'serie': serie, 'lecture': {}}}
    md = export_dc.composer('ingenierie', complements=c)
    assert 'refuse' in md
    for m in (serie.get('manquantes') or [])[:2]:
        assert m['nom'] in md and m['question'] in md


def test_les_reserves_des_moteurs_voyagent():
    md = export_dc.composer('ingenierie', complements=_complements_reels())
    # La réserve de la prolongation : un gain carbone ne justifie pas de
    # garder un serveur qui ne se met plus à jour.
    assert 'ne se met plus' in md
    # Les incertitudes de la nomenclature.
    assert '±' in md


def test_le_document_word_se_construit_et_reste_sans_marquage_ia():
    """Le dossier est un calcul déterministe : il ne reçoit PAS le marquage
    article 50, et ses propriétés le disent (doctrine du module d'export)."""
    octets, mime, nom = export_dc.produire('ingenierie', 'docx',
                                           complements=_complements_reels())
    assert nom.endswith('.docx') and len(octets) > 10000
    with zipfile.ZipFile(io.BytesIO(octets)) as z:
        core = z.read('docProps/core.xml').decode('utf-8', 'replace')
    assert 'deterministe' in core
    import livrables_export
    assert livrables_export.MARQUE_IA not in core


def test_le_pdf_se_construit_aussi():
    octets, mime, nom = export_dc.produire('ingenierie', 'pdf',
                                           complements=_complements_reels())
    assert mime == 'application/pdf'
    assert octets[:4] == b'%PDF'
