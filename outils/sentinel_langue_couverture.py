# -*- coding: utf-8 -*-
"""LA COUVERTURE DU CATALOGUE PAR LES DICTIONNAIRES — en mots, côté serveur.

POURQUOI EN MOTS ET PAS EN CLÉS. Un catalogue de Sentinel compte quelques
milliers de clés, dont des centaines d'un seul mot (« Voir », « Oui ») et
des dizaines de paragraphes de cinquante mots. Compter les clés dirait
« 90 % traduit » quand les paragraphes — ce qu'on lit — manquent encore.
La couverture est donc la part des MOTS du catalogue dont la clé a une
traduction : c'est ce qui se rapproche le plus de ce qu'un lecteur verrait.

LE GARDIEN DURABLE. tests/test_sentinel_langue_gardien.py lit le catalogue
(i18n/sentinel/CATALOGUE.json, produit par l'outil d'inventaire), les
dictionnaires i18n/sentinel/*.json, et exige la couverture minimale écrite
dans i18n/sentinel/SEUIL. Quand quelqu'un ajoutera une page en français sans
la traduire, le catalogue grossira, la couverture baissera, et la règle
tombera — sans navigateur, à chaque passage de la suite.

CE QUI N'EST PAS UN DICTIONNAIRE dans le dossier : le catalogue lui-même
(des clés françaises, pas des traductions) et les mesures (MESURE_*.json).
Les compter comme dictionnaires ferait passer du français pour de l'anglais.
"""
import glob
import io
import json
import os
import re

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSSIER = os.path.join(RACINE, 'i18n', 'sentinel')
CATALOGUE = os.path.join(DOSSIER, 'CATALOGUE.json')
SEUIL = os.path.join(DOSSIER, 'SEUIL')

#: Les régimes du catalogue et le dictionnaire où chacun se cherche : les
#: attributs (title, aria-label…) se traduisent par le dictionnaire « texte ».
REGIMES = {'texte': 'texte', 'bloc': 'bloc', 'attr': 'texte'}
_MOT = re.compile(u'[A-Za-zÀ-ÖØ-öø-ÿŒœ]+'
                  u'(?:[\'’][A-Za-zÀ-ÖØ-öø-ÿŒœ]+)*')


def mots(texte):
    """Le nombre de mots (suites de lettres) d'un texte — « # » et la
    ponctuation ne comptent pas."""
    return len(_MOT.findall(u'' if texte is None else u'%s' % texte))


def est_dictionnaire(chemin):
    """Un fichier du dossier qui porte des TRADUCTIONS : ni le catalogue,
    ni une mesure."""
    nom = os.path.basename(chemin)
    if not nom.endswith('.json'):
        return False
    if nom == 'CATALOGUE.json' or nom.startswith('MESURE_'):
        return False
    return True


def lire_json(chemin):
    with io.open(chemin, encoding='utf-8') as f:
        return json.load(f)


def cles_du_catalogue(catalogue):
    """{régime: {clé: nombre de mots}} — pour chaque régime connu du
    catalogue. Une entrée peut être une chaîne (le français aplani) ou un
    objet portant `fr` : la clé est la clé, le nombre de mots se lit sur
    elle. Un format inconnu est une erreur nommée, pas un catalogue vide :
    un gardien qui verrait « 0 mot, 100 % couvert » ne garderait rien."""
    if not isinstance(catalogue, dict):
        raise ValueError(u'le catalogue n\'est pas un objet JSON')
    out = {}
    for regime in REGIMES:
        entrees = catalogue.get(regime)
        if entrees is None:
            continue
        if not isinstance(entrees, dict):
            raise ValueError(u'le régime « %s » du catalogue n\'est pas un objet' % regime)
        out[regime] = {}
        for cle in entrees:
            out[regime][cle] = mots(cle)
    if not out:
        raise ValueError(u'le catalogue ne porte aucun des régimes %s'
                         % ', '.join(sorted(REGIMES)))
    return out


def dictionnaires_du_dossier(dossier=None):
    """Les traductions du dossier, fusionnées : {'texte': {clé: en},
    'bloc': {clé: en}}. Une valeur qui n'est pas une chaîne non vide n'est
    pas une traduction."""
    dossier = DOSSIER if dossier is None else dossier
    dico = {'texte': {}, 'bloc': {}}
    for p in sorted(glob.glob(os.path.join(dossier, '*.json'))):
        if not est_dictionnaire(p):
            continue
        lot = lire_json(p)
        if not isinstance(lot, dict):
            continue
        for regime in ('texte', 'bloc'):
            entrees = lot.get(regime) or {}
            if not isinstance(entrees, dict):
                continue
            for cle, val in entrees.items():
                if isinstance(val, u''.__class__) and val.strip() and cle not in dico[regime]:
                    dico[regime][cle] = val
    return dico


def couverture(catalogue, dico):
    """{mots_total, mots_couverts, part, cles_total, cles_couvertes,
    manquantes: [(régime, clé, mots)…] triées des plus longues aux plus
    courtes}. `part` vaut 1.0 sur un catalogue vide : rien à traduire, tout
    est traduit."""
    cles = cles_du_catalogue(catalogue)
    total = couverts = n_cles = n_couv = 0
    manquantes = []
    for regime, entrees in cles.items():
        cible = dico.get(REGIMES[regime]) or {}
        for cle, n in entrees.items():
            total += n
            n_cles += 1
            if cle in cible:
                couverts += n
                n_couv += 1
            else:
                manquantes.append((regime, cle, n))
    manquantes.sort(key=lambda m: (-m[2], m[0], m[1]))
    return {
        'mots_total': total, 'mots_couverts': couverts,
        'part': (float(couverts) / total) if total else 1.0,
        'cles_total': n_cles, 'cles_couvertes': n_couv,
        'manquantes': manquantes,
    }


def lire_seuil(chemin=None):
    """Le seuil (0 à 1) écrit dans i18n/sentinel/SEUIL : les lignes vides et
    celles qui commencent par « # » sont des commentaires ; il reste UNE
    valeur. Tout autre contenu est une erreur nommée."""
    chemin = SEUIL if chemin is None else chemin
    with io.open(chemin, encoding='utf-8') as f:
        lignes = [l.strip() for l in f.read().splitlines()]
    valeurs = [l for l in lignes if l and not l.startswith('#')]
    if len(valeurs) != 1:
        raise ValueError(u'%s : attendu une seule valeur hors commentaires, trouvé %d'
                         % (os.path.basename(chemin), len(valeurs)))
    try:
        s = float(valeurs[0].replace(',', '.'))
    except ValueError:
        raise ValueError(u'%s : « %s » n\'est pas un nombre' % (os.path.basename(chemin), valeurs[0]))
    if not (0.0 <= s <= 1.0):
        raise ValueError(u'%s : le seuil doit être entre 0 et 1, lu %s' % (os.path.basename(chemin), s))
    return s
