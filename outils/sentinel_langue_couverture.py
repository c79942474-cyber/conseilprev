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
dans i18n/sentinel/SEUIL_COUVERTURE. Quand quelqu'un ajoutera une page en
français sans la traduire, le catalogue grossira, la couverture baissera, et
la règle tombera — sans navigateur, à chaque passage de la suite.

DEUX SEUILS, ET ILS NE DISENT PAS LA MÊME CHOSE. i18n/sentinel/SEUIL porte
la PART FRANÇAISE MESURÉE À L'ÉCRAN qu'on promet de ne pas dépasser (gardée
par tests/test_sentinel_donnees_saisies.py sur MESURE_APRES.json) ;
i18n/sentinel/SEUIL_COUVERTURE porte la couverture MINIMALE du catalogue par
les dictionnaires, gardée ici. L'une est un plafond, l'autre un plancher :
les confondre dans un seul fichier désarmerait l'un des deux en silence.

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
SEUIL = os.path.join(DOSSIER, 'SEUIL_COUVERTURE')
SANS_TRADUCTION = os.path.join(DOSSIER, 'SANS_TRADUCTION.json')

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
    #  « motif » EST DU DOSSIER LUI AUSSI, et il y manquait. Les libellés
    #  composés (« ↓ {} », « Bloc # sur # · {} — Verrouillé ») ne sont des
    #  clés littérales d'aucun fichier : c'est un motif qui les sert, dans le
    #  navigateur comme dans la mesure. Les omettre ici comptait comme NON
    #  TRADUIT ce que le lecteur voit pourtant en anglais.
    dico = {'texte': {}, 'bloc': {}, 'motif': {}}
    for p in sorted(glob.glob(os.path.join(dossier, '*.json'))):
        if not est_dictionnaire(p):
            continue
        lot = lire_json(p)
        if not isinstance(lot, dict):
            continue
        for regime in ('texte', 'bloc', 'motif'):
            entrees = lot.get(regime) or {}
            if not isinstance(entrees, dict):
                continue
            for cle, val in entrees.items():
                if isinstance(val, u''.__class__) and val.strip() and cle not in dico[regime]:
                    dico[regime][cle] = val
    return dico


def lire_sans_traduction(chemin=None):
    """{clé: raison} — CE QUI N'A RIEN À TRADUIRE, déclaré clé par clé dans
    i18n/sentinel/SANS_TRADUCTION.json : une citation d'un texte anglais, un
    nom propre, un identifiant, une valeur. Un fichier absent rend {}, ce qui
    rend la mesure PLUS exigeante et jamais moins.

    LA TABLE EST BORNÉE AILLEURS, et c'est important : la règle
    tests/test_i18n_sentinel_outil éprouve que chaque clé est au catalogue,
    porte une raison écrite, n'est pas traduite par ailleurs, et que le POIDS
    total garé reste sous un plafond. Sans ce plafond, la table serait le
    moyen de tenir ce plancher-ci sans traduire une ligne."""
    chemin = SANS_TRADUCTION if chemin is None else chemin
    d = lire_json(chemin)
    if not isinstance(d, dict):
        return {}
    cles = d.get('cles')
    return cles if isinstance(cles, dict) else {}


def couverture(catalogue, dico, sans_traduction=None):
    """{mots_total, mots_couverts, part, cles_total, cles_couvertes,
    manquantes: [(régime, clé, mots)…] triées des plus longues aux plus
    courtes}. `part` vaut 1.0 sur un catalogue vide : rien à traduire, tout
    est traduit.

    UNE CLÉ EST COUVERTE DE TROIS FAÇONS, LES MÊMES QUE DANS LE NAVIGATEUR :
    son entrée exacte au dictionnaire ; un MOTIF qui s'applique à elle (le
    navigateur fait de même — `sentChercherTexte` essaie l'entrée, puis les
    motifs) ; ou sa déclaration dans SANS_TRADUCTION.
    POURQUOI LES TROIS SONT ICI. Cette mesure et celle de
    outils/i18n_sentinel.py répondent à la MÊME question, et elles avaient
    divergé : l'une connaissait les motifs et la table, l'autre non. Deux
    chiffres pour une question, c'est un chiffre de trop —
    tests/test_sentinel_langue_gardien éprouve désormais leur ÉGALITÉ sur le
    catalogue du dépôt, et la divergence retombera le jour où elle revient."""
    cles = cles_du_catalogue(catalogue)
    sans = lire_sans_traduction() if sans_traduction is None else sans_traduction
    #  LES MOTIFS, COMPILÉS PAR LE MODULE PARTAGÉ : c'est `sentinel_i18n` qui
    #  porte la règle, et le navigateur la joue à l'identique.
    try:
        import sys
        if RACINE not in sys.path:
            sys.path.insert(0, RACINE)
        import sentinel_i18n as _m
        motifs = _m.motifs_compiles(dico.get('motif') or {})
    except Exception:
        motifs, _m = [], None
    total = couverts = n_cles = n_couv = 0
    manquantes = []
    for regime, entrees in cles.items():
        cible = dico.get(REGIMES[regime]) or {}
        for cle, n in entrees.items():
            total += n
            n_cles += 1
            ok = cle in cible
            #  LE RÉGIME BLOC N'A PAS DE MOTIFS : `sentChercherBloc` ne les
            #  consulte pas, donc la mesure ne doit pas les lui accorder.
            if not ok and regime != 'bloc' and motifs and _m is not None:
                ok = bool(_m.motif_traduire(cle, motifs, dico.get('texte') or {}))
            if not ok and cle in sans:
                ok = True
            if ok:
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
    """Le seuil (0 à 1) écrit dans un fichier de seuil : les lignes vides et
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
