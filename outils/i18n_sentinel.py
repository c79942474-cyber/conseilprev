#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L'OUTILLAGE DE LA TRADUCTION PAR CONTENU DE SENTINEL — côté fichiers.

CE QUI EXISTE, ET CE QUE CET OUTIL AJOUTE. Le corps de Sentinel se traduit
par contenu (sentinel.i18n.js) : la clé d'une traduction est le texte
français normalisé, et /sentinel.en.json sert la fusion des fichiers
i18n/sentinel/*.json. Entre le relevé de ce qu'il y a à traduire (le
catalogue, produit par outils/i18n_sentinel.js dans un navigateur) et les
fichiers que la route sert, il faut : ce que le JavaScript porte en dur et
qu'un navigateur n'a pas forcément peint, des fichiers de travail pour les
traducteurs, une vérification de ce qu'ils rendent, et une mesure de ce qui
reste. C'est ici.

LES CINQ COMMANDES :
  litteraux   relève dans sentinel.page.js les chaînes françaises que le
              JavaScript rend (littéraux d'au moins deux mots avec un marqueur
              français ; pour un littéral HTML, les textes entre balises) et
              les ajoute au catalogue avec la page « _js » — en effaçant
              d'abord le passage précédent : on peut le rejouer ;
  verifier    éprouve chaque fichier i18n/sentinel/*.json (hors CATALOGUE) :
              clé présente au catalogue, balises de bloc dans la liste blanche
              et sans attribut, même nombre de « # », noms propres conservés,
              pas de valeur vide ni recopiée, pas de conflit entre fichiers ;
  couverture  mots couverts / mots inventoriés, par page et en global, avec
              les entrées manquantes classées par poids ;
  lots        découpe le catalogue en fichiers de travail équilibrés
              (i18n/sentinel/a_traduire/<lot>.json), groupés par rubrique du
              menu — une lourde coupée en parts égales, des légères réunies
              entières —, avec une case « en » vide à remplir ;
  assembler   des fichiers de travail remplis vers i18n/sentinel/<lot>.json
              au format de la route, en refusant ce que « verifier » refuse.

LA NORMALISATION EST CELLE DU MODULE. `sentinel_i18n.normaliser` est la
réimplémentation Python de `sentNormaliser` ; tests/test_i18n_sentinel_outil
prouve l'identité des deux sur trente chaînes pièges. Une clé calculée ici
avec une autre règle ne serait jamais retrouvée par le navigateur.

Usage :  python outils/i18n_sentinel.py <commande> [options]  (--aide par commande)
"""
import argparse
import datetime
import glob
import html as _html
import io
import json
import math
import os
import re
import sys
import unicodedata

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)
import sentinel_i18n  # noqa: E402
from sentinel_i18n import aplanir, normaliser  # noqa: E402

DOSSIER = sentinel_i18n.DOSSIER
CATALOGUE = os.path.join(DOSSIER, 'CATALOGUE.json')
A_TRADUIRE = os.path.join(DOSSIER, 'a_traduire')
PAGE_JS = os.path.join(RACINE, 'sentinel.page.js')

#: LA MÊME DÉFINITION D'UN MOT QUE outils/i18n_sentinel.js : une suite de
#: lettres latines, accents compris. Les deux comptent les mêmes mots.
MOT = re.compile(u'[A-Za-z\u00c0-\u024f]+')

#: LA LISTE BLANCHE DU RÉGIME BLOC — celle de SENT_INLINE, à la lettre.
BALISES_PERMISES = frozenset(['b', 'strong', 'i', 'em', 'u', 's', 'sup', 'sub',
                              'small', 'mark', 'code', 'kbd', 'abbr', 'br',
                              'wbr', 'span'])

#: LES NOMS PROPRES QU'UNE TRADUCTION DOIT GARDER : un cadre, une norme, une
#: autorité, un produit. Comparés sous leur forme normalisée (« NIS # »),
#: puisque c'est celle des clés.
NOMS_PROPRES = ['EU AI Act', 'NIS 2', 'DORA', 'CRA', 'ReCyF', 'ISO 27001',
                'ISO 42001', 'NIST AI RMF', 'NIST SP 800-53', 'NIST SP 800-82',
                'OWASP LLM', 'EBIOS RM', 'ANSSI', 'CNIL', 'Sentinel', 'CONSEILPREV']

#: CE QUI DIT QU'UNE CHAÎNE EST DU FRANÇAIS : un accent, ou un mot-outil que
#: l'anglais n'emploie pas. « plus », « en », « on » sont exclus : ils sont
#: aussi anglais.
ACCENTS = re.compile(u'[àâäéèêëîïôöùûüÿçœæÀÂÄÉÈÊËÎÏÔÖÙÛÜŸÇŒÆ]')
MOTS_OUTILS = frozenset([
    'le', 'la', 'les', 'de', 'des', 'du', 'un', 'une', 'et', 'ou', 'au', 'aux',
    'pour', 'sur', 'par', 'dans', 'avec', 'sans', 'sous', 'chez', 'vers',
    'pas', 'ne', 'est', 'sont', 'qui', 'que', 'quoi', 'dont', 'ce', 'cet',
    'cette', 'ces', 'vos', 'votre', 'nos', 'notre', 'leur', 'leurs', 'ses',
    'mais', 'donc', 'chaque', 'tout', 'tous', 'toute', 'toutes', 'aucun',
    'aucune', 'être', 'avoir', 'selon', 'depuis', 'entre', 'ici', 'aussi',
    'encore', 'déjà', 'très', 'peu', 'trop', 'bien', 'mal', 'oui', 'non',
])


# ══════════════════════════════════════════════════════════════════════════
#  LE SOCLE — mots, catalogue, rubriques
# ══════════════════════════════════════════════════════════════════════════

def compter_mots(s):
    return len(MOT.findall(u'' if s is None else u'%s' % s))


def est_francais(s):
    """Au moins deux mots, et un marqueur français."""
    mots = MOT.findall(s)
    if len(mots) < 2:
        return False
    if ACCENTS.search(s):
        return True
    return any(m.lower() in MOTS_OUTILS for m in mots)


def charger_json(chemin):
    with io.open(chemin, encoding='utf-8') as f:
        return json.load(f)


def ecrire_json(chemin, obj):
    """Le texte est produit AVANT d'ouvrir le fichier : une valeur qui ne se
    sérialise pas ne doit pas laisser un fichier vide à la place du
    catalogue — c'est arrivé, et l'inventaire de 118 pages était à refaire."""
    texte = json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + u'\n'
    texte.encode('utf-8')
    d = os.path.dirname(chemin)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(chemin, 'w', encoding='utf-8') as f:
        f.write(texte)


def charger_catalogue(chemin=None):
    chemin = CATALOGUE if chemin is None else chemin
    cat = charger_json(chemin)
    for regime in ('bloc', 'texte', 'attr'):
        cat.setdefault(regime, {})
    cat.setdefault('rubriques', {})
    return cat


def lire_rubriques_page_js(chemin=None):
    """{page: rubrique du menu}, lu dans PAGE_META de sentinel.page.js."""
    src = io.open(PAGE_JS if chemin is None else chemin, encoding='utf-8').read()
    i = src.index('var PAGE_META = {')
    j = src.index('\n};', i)
    out = {}
    #  DEUX GRAPHIES DANS LA TABLE : `'fiche-fr': { section: '…' }` et
    #  `apercu:   {section:'…', …}` — la clé est citée ou nue, l'espace
    #  après les deux-points est libre.
    for m in re.finditer(r"(?m)^\s*'?([A-Za-z0-9_-]+)'?\s*:\s*\{\s*section\s*:\s*'((?:[^'\\]|\\.)*)'", src[i:j]):
        out[m.group(1)] = _dechapper_js(m.group(2))
    return out


def rubrique_de(page, rubriques):
    if page in ('_coquille', '_js'):
        return page
    return rubriques.get(page) or '_autre'


def dico_de(regime):
    """Le régime du dictionnaire servi : les attributs sont cherchés dans
    « texte » par le module."""
    return 'bloc' if regime == 'bloc' else 'texte'


# ══════════════════════════════════════════════════════════════════════════
#  LITTERAUX — ce que sentinel.page.js porte en dur
# ══════════════════════════════════════════════════════════════════════════

_ECHAPPEMENTS = {'n': '\n', 't': '\t', 'r': '\r', 'b': '\b', 'f': '\f', 'v': '\v',
                 '0': '\0', "'": "'", '"': '"', '\\': '\\', '`': '`', '/': '/'}


def _dechapper_js(s):
    def rem(m):
        e = m.group(1)
        if e.startswith('u{'):
            return chr(int(e[2:-1], 16))
        if e[0] == 'u':
            return chr(int(e[1:], 16))
        if e[0] == 'x':
            return chr(int(e[1:], 16))
        if e == '\n':
            return ''
        return _ECHAPPEMENTS.get(e, e)
    s = re.sub(r'\\(u\{[0-9a-fA-F]+\}|u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|\n|.)', rem, s, flags=re.S)
    #  UN DRAPEAU S'ÉCRIT EN DEUX \\uXXXX (une paire de substitution) : les deux
    #  moitiés sont recollées, sinon la chaîne ne s'encode plus en UTF-8.
    return s.encode('utf-16', 'surrogatepass').decode('utf-16', 'replace')


_AVANT_REGEX = frozenset('(,=:[!&|?{};+-*%<>~^')


def litteraux_js(src):
    """Les littéraux de chaînes du code, hors commentaires et expressions
    régulières. Un gabarit (`…${x}…`) rend UNE chaîne par morceau entre ses
    expressions : dans le document, chaque morceau est de toute façon ce
    qu'on retrouve autour d'une valeur calculée."""
    out = []
    i, n = 0, len(src)
    dernier = ''  # le dernier caractère de code significatif, pour reconnaître une regex
    while i < n:
        c = src[i]
        if c == '/' and src.startswith('//', i):
            i = src.find('\n', i)
            i = n if i < 0 else i
            continue
        if c == '/' and src.startswith('/*', i):
            j = src.find('*/', i + 2)
            i = n if j < 0 else j + 2
            continue
        if c in '\'"':
            j = i + 1
            while j < n and src[j] != c:
                j += 2 if src[j] == '\\' else 1
            out.append(_dechapper_js(src[i + 1:j]))
            i = j + 1
            dernier = c
            continue
        if c == '`':
            j, morceau, prof = i + 1, [], 0
            while j < n:
                if src[j] == '\\':
                    morceau.append(src[j:j + 2]); j += 2; continue
                if src.startswith('${', j):
                    out.append(_dechapper_js(''.join(morceau))); morceau = []
                    prof, j = 1, j + 2
                    while j < n and prof:
                        prof += {'{': 1, '}': -1}.get(src[j], 0); j += 1
                    continue
                if src[j] == '`':
                    break
                morceau.append(src[j]); j += 1
            out.append(_dechapper_js(''.join(morceau)))
            i = j + 1
            dernier = '`'
            continue
        if c == '/' and (dernier == '' or dernier in _AVANT_REGEX):
            j, classe = i + 1, False
            while j < n and (classe or src[j] != '/') and src[j] != '\n':
                if src[j] == '\\':
                    j += 1
                elif src[j] == '[':
                    classe = True
                elif src[j] == ']':
                    classe = False
                j += 1
            i = j + 1
            continue
        if not c.isspace():
            dernier = c
        i += 1
    return out


_BALISE = re.compile(r'<(/?)([a-zA-Z][a-zA-Z0-9-]*)((?:\s[^>]*)?)/?>')
_ATTR_TEXTE = re.compile(r'\b(title|aria-label|placeholder|alt)\s*=\s*(?:"([^"]*)"|\'([^\']*)\')')


def entrees_d_un_html(fragment):
    """Les entrées qu'un fragment HTML rend, classées comme le module
    classerait le DOM qu'il produit : un morceau qui remplit un élément et ne
    porte que des balises de mise en forme nues est un BLOC ; sinon chaque
    texte entre balises est une entrée TEXTE ; les title/aria-label/
    placeholder/alt des balises sont des entrées ATTR.
    Rend [(regime, fr, html|None)] — sans filtre de langue."""
    out = []
    morceaux = re.split(r'(<[^>]*>)', fragment)
    textes, html, inline, ouvert, muet = [], [], False, True, None
    #  LES ÉLÉMENTS OUVERTS QUI FONT FRONTIÈRE (un <div>, un <span class>) :
    #  leur balise fermante clôt le morceau, même si « span » est dans la
    #  liste blanche — c'est l'élément à attribut qu'elle ferme.
    pile = []

    def clore(complet):
        tc = _html.unescape(''.join(textes))
        if inline and complet and ouvert:
            out.append(('bloc', tc, ''.join(html)))
        else:
            for t in textes:
                out.append(('texte', _html.unescape(t), None))

    for m in morceaux:
        if not m:
            continue
        if m.startswith('<!--'):
            continue
        b = _BALISE.match(m) if m.startswith('<') else None
        if b:
            fermante, nom, attrs = b.group(1) == '/', b.group(2).lower(), b.group(3).strip()
            #  CE QUE LE MODULE NE PARCOURT PAS (SENT_EXCLUS) n'est pas relevé
            #  non plus : le CSS d'un <style>, le code d'un <script>.
            if muet:
                if fermante and nom == muet:
                    muet = None
                continue
            for a in _ATTR_TEXTE.finditer(attrs):
                out.append(('attr', _html.unescape(a.group(2) if a.group(2) is not None else a.group(3)), None))
            if nom in BALISES_PERMISES and not attrs and not (fermante and nom in pile):
                html.append(m); inline = True
                continue
            clore(complet=fermante)
            textes, html, inline, ouvert = [], [], False, not fermante
            if fermante:
                if nom in pile:
                    del pile[len(pile) - 1 - pile[::-1].index(nom):]
            else:
                pile.append(nom)
                if nom in _MUETS:
                    muet = nom
            continue
        if muet:
            continue
        #  UN LITTÉRAL COUPÉ AU MILIEU D'UNE BALISE (`'<a href="' + url + '">Voir'`)
        #  laisse la fin de la balise en tête du texte, ou son début en queue :
        #  ce n'est pas du texte, on le retire.
        m = re.sub(r'^[^<>]*>', '', m)
        m = re.sub(r'<[^>]*$', '', m)
        if '{' in m or '}' in m:
            continue
        textes.append(m); html.append(m)
    clore(complet=True)
    return out


_MUETS = frozenset(['script', 'style', 'textarea', 'code', 'pre', 'svg', 'canvas',
                    'iframe', 'select', 'option'])


#: UN IDENTIFIANT N'EST PAS DU TEXTE RENDU, même s'il contient « des » ou un
#: accent : une route (/api/conformite/etat-des-lieux), une valeur de liste
#: (non_mise_en_oeuvre), une clé de traduction (nav.sec.evaluer-le-risque),
#: un appel (go('fria',…)). Il n'a pas d'espace ; « Coût/an » ou
#: « Finalité(s) », sans espace eux aussi, sont des libellés et restent.
_IDENTIFIANT = re.compile(r"^/|_|\('|^[a-z0-9]+(?:\.[a-z0-9-]+)+$")


def est_identifiant(s):
    return u' ' not in s and bool(_IDENTIFIANT.search(s))


def entrees_des_litteraux(src):
    """{regime: {clé: {fr, html?, mots}}} — ce que le JavaScript rend et qui
    est du français."""
    out = {'bloc': {}, 'texte': {}, 'attr': {}}
    for lit in litteraux_js(src):
        if '<' in lit and '>' in lit and _BALISE.search(lit):
            candidats = entrees_d_un_html(lit)
        else:
            if '{' in lit or '}' in lit:
                continue
            #  UN MORCEAU DE BALISE SANS SON « < » (`' title="Effacer…">'`)
            #  est de la concaténation, pas du texte rendu.
            lit = re.sub(r'^[^<>]*>', '', lit)
            if re.search(r'(?:^|\s)[a-z-]+="', lit):
                continue
            candidats = [('texte', lit, None)]
        for regime, fr, html in candidats:
            fr = aplanir(fr)
            if not est_francais(fr) or est_identifiant(fr):
                continue
            cle = normaliser(fr)
            if cle in out[regime]:
                continue
            ent = {'fr': fr, 'mots': compter_mots(fr)}
            if regime == 'bloc':
                ent['html'] = aplanir(html)
            out[regime][cle] = ent
    return out


def retirer_litteraux(cat):
    """Efface la contribution « _js » d'un passage précédent : les entrées
    qui n'étaient QUE du JavaScript, et l'étiquette « _js » des autres. Sans
    cela, rejouer « litteraux » après une correction du code garderait les
    chaînes disparues du JavaScript — un catalogue qui ne maigrit jamais ne
    mesure plus rien. Rend le nombre d'entrées effacées."""
    effacees = 0
    for regime in ('bloc', 'texte', 'attr'):
        for cle in list(cat[regime]):
            pages = cat[regime][cle].get('pages') or []
            if '_js' not in pages:
                continue
            if pages == ['_js']:
                del cat[regime][cle]
                effacees += 1
            else:
                pages.remove('_js')
    return effacees


def ajouter_litteraux(cat, entrees):
    """Ajoute au catalogue, page « _js » ; une clé déjà relevée à l'écran
    reçoit « _js » en plus. Rend (nouvelles, déjà vues)."""
    nouvelles, vues = 0, 0
    for regime in ('bloc', 'texte', 'attr'):
        for cle, ent in entrees[regime].items():
            deja = cat[regime].get(cle)
            if deja is None:
                cat[regime][cle] = dict(ent, pages=['_js'])
                nouvelles += 1
            else:
                vues += 1
                if '_js' not in deja['pages']:
                    deja['pages'].append('_js')
    return nouvelles, vues


def cmd_litteraux(args):
    cat = charger_catalogue(args.catalogue)
    src = io.open(args.js, encoding='utf-8').read()
    entrees = entrees_des_litteraux(src)
    effacees = retirer_litteraux(cat)
    if effacees:
        print(u'  passage précédent effacé : %d entrée(s) « _js »' % effacees)
    nouvelles, vues = ajouter_litteraux(cat, entrees)
    cat['js'] = {'fichier': os.path.basename(args.js),
                 'entrees': {r: len(entrees[r]) for r in ('bloc', 'texte', 'attr')},
                 'mots': {r: sum(e['mots'] for e in entrees[r].values()) for r in ('bloc', 'texte', 'attr')}}
    ecrire_json(args.catalogue, cat)
    print(u'  %s : %d entrées françaises (bloc %d, texte %d, attr %d) — %d nouvelles au catalogue, %d déjà vues à l\'écran'
          % (os.path.basename(args.js), sum(len(entrees[r]) for r in entrees),
             len(entrees['bloc']), len(entrees['texte']), len(entrees['attr']), nouvelles, vues))
    for r in ('bloc', 'texte', 'attr'):
        print(u'  %-6s %6d entrées %7d mots' % (r, cat['js']['entrees'][r], cat['js']['mots'][r]))
    return 0


# ══════════════════════════════════════════════════════════════════════════
#  VERIFIER — ce qu'un fichier de dictionnaire n'a pas le droit de porter
# ══════════════════════════════════════════════════════════════════════════

def _dieses(s):
    """Les « # » qui sont des emplacements de nombre — pas ceux d'une entité
    HTML (&#39;), que le module ignore de même."""
    return len(re.findall(r'(?<!&)#', s))


def _frontiere(motif):
    return re.compile(u'(?<![A-Za-z0-9\u00c0-\u024f#])' + re.escape(motif)
                      + u'(?![A-Za-z0-9\u00c0-\u024f#])', re.I)


_NOMS_NORMALISES = [(n, _frontiere(normaliser(n))) for n in NOMS_PROPRES]


def _peut_rester_identique(cle):
    """Une clé qui n'est qu'un nom propre, un sigle, un nombre ou de la
    ponctuation n'a rien à traduire : « CNIL », « GB », « A.# »."""
    reste = cle
    for _, rx in _NOMS_NORMALISES:
        reste = rx.sub(' ', reste)
    return not any(len(m) > 3 for m in MOT.findall(reste))


def verifier_entree(regime, cle, en, cat):
    """Les motifs de refus d'une entrée (regime ∈ bloc|texte) — vide si elle
    est acceptable. C'est LA règle, partagée par « verifier » et
    « assembler »."""
    motifs = []
    if not isinstance(en, str):
        return [u'la valeur n\'est pas une chaîne']
    if normaliser(cle) != cle:
        motifs.append(u'clé non normalisée')
    if regime == 'bloc':
        connue = cle in cat['bloc']
    else:
        connue = cle in cat['texte'] or cle in cat['attr']
    if not connue:
        motifs.append(u'périmée : la clé n\'est plus au catalogue')
    if not en.strip():
        motifs.append(u'valeur vide')
        return motifs
    if _dieses(cle) != _dieses(en):
        motifs.append(u'« # » : %d dans la clé, %d dans la valeur' % (_dieses(cle), _dieses(en)))
    for nom, rx in _NOMS_NORMALISES:
        if rx.search(cle) and not rx.search(en):
            motifs.append(u'nom propre « %s » absent de la traduction' % nom)
    if regime == 'bloc':
        for m in _BALISE.finditer(en):
            nom, attrs = m.group(2).lower(), m.group(3).strip()
            if nom not in BALISES_PERMISES:
                motifs.append(u'balise <%s> hors liste blanche' % nom)
            if attrs:
                motifs.append(u'balise <%s> avec attribut' % nom)
    if aplanir(en) == aplanir(cle) or aplanir(en) == aplanir(cat.get(regime, {}).get(cle, {}).get('fr', '') or '') \
            or aplanir(en) == aplanir(cat.get('attr', {}).get(cle, {}).get('fr', '') or ''):
        if not _peut_rester_identique(cle):
            motifs.append(u'identique au français')
    return motifs


def fichiers_du_dossier(dossier):
    return sorted(p for p in glob.glob(os.path.join(dossier, '*.json'))
                  if os.path.basename(p) != 'CATALOGUE.json')


def verifier_fichiers(fichiers, cat, deja=None):
    """Les fautes d'une liste de fichiers de dictionnaire, chacune
    (fichier, régime, clé, motif). `deja` : {(régime, clé): (fichier, en)}
    d'autres fichiers déjà admis, pour les conflits."""
    fautes = []
    vus = dict(deja or {})
    for chemin in fichiers:
        nom = os.path.basename(chemin)
        try:
            lot = charger_json(chemin)
        except (OSError, ValueError) as e:
            fautes.append((nom, '', '', u'illisible (%s)' % e))
            continue
        for regime in ('texte', 'bloc'):
            entrees = lot.get(regime) or {}
            if not isinstance(entrees, dict):
                fautes.append((nom, regime, '', u'n\'est pas un objet'))
                continue
            for cle, en in entrees.items():
                for motif in verifier_entree(regime, cle, en, cat):
                    fautes.append((nom, regime, cle, motif))
                if isinstance(en, str):
                    autre = vus.get((regime, cle))
                    if autre is None:
                        vus[(regime, cle)] = (nom, en)
                    elif autre[1] != en:
                        fautes.append((nom, regime, cle, u'conflit avec %s (« %s »)' % (autre[0], autre[1][:40])))
    return fautes


def _afficher_fautes(fautes):
    for nom, regime, cle, motif in fautes:
        print(u'  %s  %-5s  %s\n        %s' % (nom, regime, (cle[:70] + u'…') if len(cle) > 70 else cle, motif))


def cmd_verifier(args):
    cat = charger_catalogue(args.catalogue)
    fichiers = args.fichiers or fichiers_du_dossier(args.dossier)
    fautes = verifier_fichiers(fichiers, cat)
    _afficher_fautes(fautes)
    print(u'  %d fichier(s), %d faute(s)' % (len(fichiers), len(fautes)))
    return 1 if fautes else 0


# ══════════════════════════════════════════════════════════════════════════
#  COUVERTURE — ce qui est traduit, ce qui manque, page par page
# ══════════════════════════════════════════════════════════════════════════

def couverture(cat, dico):
    """{'pages': {page: {mots, couverts, entrees, traduites, manquantes}},
    'global': {...}}. Une entrée est couverte si sa clé est au dictionnaire
    servi (les attributs dans « texte ») avec une valeur non vide. Une entrée
    vue sur deux pages compte pour les deux ; le global la compte une fois."""
    pages, glob_ = {}, {'mots': 0, 'couverts': 0, 'entrees': 0, 'traduites': 0, 'manquantes': []}
    for regime in ('bloc', 'texte', 'attr'):
        d = dico.get(dico_de(regime)) or {}
        for cle, ent in cat[regime].items():
            ok = bool((d.get(cle) or '').strip()) if isinstance(d.get(cle), str) else False
            m = ent.get('mots', compter_mots(ent['fr']))
            cibles = [glob_] + [pages.setdefault(p, {'mots': 0, 'couverts': 0, 'entrees': 0, 'traduites': 0, 'manquantes': []})
                                for p in ent.get('pages') or ['_sans_page']]
            for c in cibles:
                c['mots'] += m; c['entrees'] += 1
                if ok:
                    c['couverts'] += m; c['traduites'] += 1
                else:
                    c['manquantes'].append({'regime': regime, 'cle': cle, 'mots': m})
    for c in [glob_] + list(pages.values()):
        c['manquantes'].sort(key=lambda e: (-e['mots'], e['cle']))
        c['pct'] = round(100.0 * c['couverts'] / c['mots'], 1) if c['mots'] else 100.0
    return {'pages': pages, 'global': glob_}


def cmd_couverture(args):
    cat = charger_catalogue(args.catalogue)
    dico, fautes = sentinel_i18n.fusionner(args.dossier)
    for f in fautes:
        print(u'  fusion : %s' % f)
    res = couverture(cat, dico)
    if args.json:
        ecrire_json(args.json, res)
    pages = sorted(res['pages'].items(), key=lambda kv: (-kv[1]['mots'], kv[0]))
    if args.page:
        pages = [kv for kv in pages if kv[0] in args.page]
    print(u'  %-28s %8s %8s %6s' % ('page', 'mots', 'couverts', '%'))
    for page, c in pages:
        print(u'  %-28s %8d %8d %5.1f%%' % (page, c['mots'], c['couverts'], c['pct']))
    g = res['global']
    print(u'  %-28s %8d %8d %5.1f%%   (%d / %d entrées)' % ('GLOBAL', g['mots'], g['couverts'], g['pct'], g['traduites'], g['entrees']))
    if args.manquantes:
        source = res['pages'][args.page[0]] if args.page and args.page[0] in res['pages'] else g
        print(u'  les %d entrées manquantes les plus lourdes :' % args.manquantes)
        for e in source['manquantes'][:args.manquantes]:
            print(u'    %-5s %4d mots  %s' % (e['regime'], e['mots'], e['cle'][:90]))
    if args.seuil is not None and g['pct'] < args.seuil:
        print(u'  SOUS LE SEUIL : %.1f%% < %.1f%%' % (g['pct'], args.seuil))
        return 1
    return 0


# ══════════════════════════════════════════════════════════════════════════
#  LOTS — les fichiers de travail des traducteurs
# ══════════════════════════════════════════════════════════════════════════

def _slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'-+', '-', re.sub(r'[^A-Za-z0-9]+', '-', s)).strip('-').lower() or 'autre'


def decouper_lots(cat, taille=2500, rubriques=None, dico=None):
    """Les lots de travail : [{nom, rubrique, rubriques, pages, mots, texte,
    bloc}]. Chaque entrée va dans la rubrique de sa PREMIÈRE page.
      · UNE RUBRIQUE PLUS LOURDE QU'UN LOT est coupée en parts ÉGALES (et non
        « taille pleine puis reste ») pour que le dernier lot ne soit pas un
        fond de tiroir ;
      · LES RUBRIQUES PLUS LÉGÈRES sont REGROUPÉES entières, dans l'ordre du
        menu (par-dessus les lourdes), jusqu'à la taille d'un lot (10 % de
        marge) : une rubrique de 80 mots ne fait pas un fichier à elle
        seule, et une rubrique n'est jamais coupée pour remplir un lot.
    « _coquille » et « _js » ne sont pas des rubriques du menu : ils ne se
    regroupent avec rien. Avec `dico`, les entrées déjà traduites sont
    laissées de côté."""
    rubriques = cat.get('rubriques') or rubriques or {}
    par_rubrique = {}
    for regime in ('bloc', 'texte', 'attr'):
        d = (dico or {}).get(dico_de(regime)) or {}
        for cle, ent in cat[regime].items():
            if dico is not None and (d.get(cle) or '').strip():
                continue
            #  UN ATTRIBUT DONT LA CLÉ EST AUSSI UN TEXTE est la même entrée
            #  pour la route (les deux se cherchent dans « texte ») : une
            #  seule case à remplir, pas deux.
            if regime == 'attr' and cle in cat['texte']:
                continue
            pages = ent.get('pages') or ['_sans_page']
            rub = rubrique_de(pages[0], rubriques)
            par_rubrique.setdefault(rub, []).append((pages[0], regime, cle, ent))
    lots = []
    groupe = []  # [(rubrique, entrées)] légères, en attente d'un lot commun
    mots_groupe = [0]

    def clore_groupe():
        if groupe:
            lots.append(_lot([r for r, _ in groupe], 1, 1, [e for _, es in groupe for e in es]))
            del groupe[:]
            mots_groupe[0] = 0

    for rub in sorted(par_rubrique):
        entrees = sorted(par_rubrique[rub], key=lambda e: (e[0], e[1], e[2]))
        total = sum(e[3].get('mots', 0) for e in entrees)
        if total < taille and rub not in ('_coquille', '_js'):
            if groupe and mots_groupe[0] + total > taille * 1.1:
                clore_groupe()
            groupe.append((rub, entrees))
            mots_groupe[0] += total
            continue
        parts = max(1, int(math.ceil(float(total) / taille))) if total else 1
        cible = float(total) / parts
        courant, cumul, k = [], 0, 0
        for e in entrees:
            courant.append(e); cumul += e[3].get('mots', 0)
            if k < parts - 1 and cumul >= cible * (k + 1):
                lots.append(_lot([rub], k + 1, parts, courant))
                courant, k = [], k + 1
        if courant or not lots or lots[-1]['rubriques'] != [rub]:
            lots.append(_lot([rub], k + 1, parts, courant))
    clore_groupe()
    #  UN REGROUPEMENT ENJAMBE LES RUBRIQUES LOURDES (AUDIT, 80 mots, attend
    #  COMPTE par-dessus BUSINESS) : il se clôt plus tard qu'il ne commence.
    #  Les lots sont donc rangés par leur première rubrique, puis par part —
    #  l'ordre du menu, pas l'ordre de clôture.
    lots.sort(key=lambda l: (l['rubriques'][0], l['part']))
    for i, lot in enumerate(lots):
        lot['nom'] = '%02d-%s' % (i + 1, _nom_de_lot(lot))
    return lots


def _nom_de_lot(lot):
    """« 04-business-2 » pour une part, « 12-cra-produits-dora-empreinte »
    pour un regroupement — tronqué au mot, un nom de fichier reste lisible."""
    if lot['parts'] > 1:
        return '%s-%d' % (_slug(lot['rubrique']), lot['part'])
    nom = ''
    for r in lot['rubriques']:
        suite = (nom + '-' if nom else '') + _slug(r)
        if nom and len(suite) > 48:
            return nom + '-etc'
        nom = suite
    return nom


def _lot(rubs, part, parts, entrees):
    lot = {'rubrique': ' + '.join(rubs), 'rubriques': list(rubs), 'part': part, 'parts': parts,
           'pages': [], 'mots': 0, 'texte': {}, 'bloc': {}}
    for page, regime, cle, ent in entrees:
        if page not in lot['pages']:
            lot['pages'].append(page)
        lot['mots'] += ent.get('mots', 0)
        if regime == 'bloc':
            lot['bloc'][cle] = {'fr': ent['fr'], 'html': ent.get('html', ent['fr']), 'en': ''}
        else:
            lot['texte'][cle] = {'fr': ent['fr'], 'en': ''}
    return lot


def fichier_de_lot(lot):
    return {'_lot': lot['nom'], '_rubrique': lot['rubrique'], '_pages': lot['pages'],
            '_mots': lot['mots'], 'texte': lot['texte'], 'bloc': lot['bloc']}


def _a_du_travail_rempli(chemin):
    try:
        lot = charger_json(chemin)
    except (OSError, ValueError):
        return False
    for regime in ('texte', 'bloc'):
        for ent in (lot.get(regime) or {}).values():
            if isinstance(ent, dict) and (ent.get('en') or '').strip():
                return True
    return False


def cmd_lots(args):
    cat = charger_catalogue(args.catalogue)
    rubriques = cat.get('rubriques') or lire_rubriques_page_js()
    dico = None
    if args.restants:
        dico, _ = sentinel_i18n.fusionner(args.dictionnaires)
    lots = decouper_lots(cat, taille=args.taille, rubriques=rubriques, dico=dico)
    if not os.path.isdir(args.dossier):
        os.makedirs(args.dossier)
    ecrits, gardes = 0, 0
    for lot in lots:
        chemin = os.path.join(args.dossier, lot['nom'] + '.json')
        if os.path.exists(chemin) and not args.forcer and _a_du_travail_rempli(chemin):
            print(u'  %s : déjà rempli, gardé (--forcer pour l\'écraser)' % lot['nom'])
            gardes += 1
            continue
        ecrire_json(chemin, fichier_de_lot(lot))
        ecrits += 1
        print(u'  %-40s %5d mots  %4d entrées  %s' % (lot['nom'], lot['mots'],
                                                     len(lot['texte']) + len(lot['bloc']),
                                                     ', '.join(lot['pages'][:4]) + (u'…' if len(lot['pages']) > 4 else '')))
    #  UN FICHIER DE TRAVAIL QUI NE CORRESPOND PLUS À AUCUN LOT (le catalogue a
    #  changé, la découpe aussi) est retiré s'il est vide : laissé là, il
    #  doublerait des clés d'un autre lot. Rempli, il est gardé et nommé —
    #  c'est du travail de traducteur, « assembler » le reprendra.
    noms = set(lot['nom'] + '.json' for lot in lots)
    retires = 0
    for chemin in sorted(glob.glob(os.path.join(args.dossier, '*.json'))):
        if os.path.basename(chemin) in noms:
            continue
        if _a_du_travail_rempli(chemin):
            print(u'  %s : hors de la découpe mais rempli, gardé' % os.path.basename(chemin))
        else:
            os.remove(chemin)
            retires += 1
    print(u'  %d lot(s) écrit(s), %d gardé(s), %d périmé(s) retiré(s), dans %s'
          % (ecrits, gardes, retires, os.path.relpath(args.dossier, RACINE)))
    return 0


# ══════════════════════════════════════════════════════════════════════════
#  ASSEMBLER — du travail rempli au format de la route
# ══════════════════════════════════════════════════════════════════════════

def assembler(fichiers, cat, deja=None):
    """Rend ([(nom, {_lot, texte, bloc})], refus) : les entrées remplies de
    chaque fichier de travail, au format de la route, MOINS celles que
    « verifier » refuserait — nommées dans `refus` (fichier, régime, clé,
    motif). `deja` : {(régime, clé): (fichier, en)} des dictionnaires déjà en
    place, pour refuser un conflit avant qu'il n'atteigne la route."""
    sorties, refus = [], []
    vus = dict(deja or {})
    for chemin in fichiers:
        nom = os.path.basename(chemin)
        lot = charger_json(chemin)
        nom_lot = lot.get('_lot') or os.path.splitext(nom)[0]
        sortie = {'_lot': nom_lot, 'texte': {}, 'bloc': {}}
        for regime in ('texte', 'bloc'):
            for cle, ent in (lot.get(regime) or {}).items():
                en = ent.get('en') if isinstance(ent, dict) else ent
                if not isinstance(en, str) or not en.strip():
                    continue  # pas encore traduit : ce n'est pas une faute
                motifs = verifier_entree(regime, cle, en, cat)
                autre = vus.get((regime, cle))
                if autre is not None and autre[1] != en:
                    motifs.append(u'conflit avec %s (« %s »)' % (autre[0], autre[1][:40]))
                if motifs:
                    refus.extend((nom, regime, cle, m) for m in motifs)
                    continue
                sortie[regime][cle] = en
                vus.setdefault((regime, cle), (nom_lot + '.json', en))
        sorties.append((nom_lot, sortie))
    return sorties, refus


def _dictionnaires_en_place(dossier, exclure=()):
    vus = {}
    for chemin in fichiers_du_dossier(dossier):
        nom = os.path.basename(chemin)
        if nom in exclure:
            continue
        try:
            lot = charger_json(chemin)
        except (OSError, ValueError):
            continue
        for regime in ('texte', 'bloc'):
            for cle, en in (lot.get(regime) or {}).items():
                if isinstance(en, str):
                    vus.setdefault((regime, cle), (nom, en))
    return vus


def cmd_assembler(args):
    cat = charger_catalogue(args.catalogue)
    fichiers = args.fichiers or sorted(glob.glob(os.path.join(args.dossier, '*.json')))
    noms = set()
    for chemin in fichiers:
        lot = charger_json(chemin)
        noms.add((lot.get('_lot') or os.path.splitext(os.path.basename(chemin))[0]) + '.json')
    deja = _dictionnaires_en_place(args.sortie, exclure=noms)
    sorties, refus = assembler(fichiers, cat, deja)
    _afficher_fautes(refus)
    ecrits = 0
    for nom_lot, sortie in sorties:
        n = len(sortie['texte']) + len(sortie['bloc'])
        if not n:
            continue
        ecrire_json(os.path.join(args.sortie, nom_lot + '.json'), sortie)
        ecrits += 1
        print(u'  %-40s %5d entrées → %s' % (nom_lot, n, os.path.relpath(args.sortie, RACINE)))
    refusees = len(set((f, r, c) for f, r, c, _ in refus))
    print(u'  %d fichier(s) écrit(s), %d entrée(s) refusée(s)' % (ecrits, refusees))
    return 1 if refus else 0


# ══════════════════════════════════════════════════════════════════════════
#  LA LIGNE DE COMMANDE
# ══════════════════════════════════════════════════════════════════════════

def analyseur():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0], add_help=True)
    sp = p.add_subparsers(dest='commande')
    sp.required = True

    a = sp.add_parser('litteraux', help='ajoute au catalogue les chaînes françaises de sentinel.page.js (page _js)')
    a.add_argument('--catalogue', default=CATALOGUE)
    a.add_argument('--js', default=PAGE_JS)
    a.set_defaults(fn=cmd_litteraux)

    a = sp.add_parser('verifier', help='éprouve les fichiers i18n/sentinel/*.json contre le catalogue')
    a.add_argument('fichiers', nargs='*', help='fichiers à vérifier (défaut : tout le dossier hors CATALOGUE)')
    a.add_argument('--catalogue', default=CATALOGUE)
    a.add_argument('--dossier', default=DOSSIER)
    a.set_defaults(fn=cmd_verifier)

    a = sp.add_parser('couverture', help='mots couverts / mots inventoriés, par page et en global')
    a.add_argument('--catalogue', default=CATALOGUE)
    a.add_argument('--dossier', default=DOSSIER, help='les dictionnaires servis')
    a.add_argument('--json', default=None, help='écrit aussi le résultat en JSON')
    a.add_argument('--page', action='append', default=None, help='ne montre que cette page (répétable)')
    a.add_argument('--manquantes', type=int, default=0, help='montre les N entrées manquantes les plus lourdes')
    a.add_argument('--seuil', type=float, default=None, help='code de sortie 1 sous ce pourcentage global')
    a.set_defaults(fn=cmd_couverture)

    a = sp.add_parser('lots', help='découpe le catalogue en fichiers de travail (~2 500 mots, par rubrique)')
    a.add_argument('--catalogue', default=CATALOGUE)
    a.add_argument('--dossier', default=A_TRADUIRE, help='où écrire les fichiers de travail')
    a.add_argument('--taille', type=int, default=2500, help='mots par lot, environ')
    a.add_argument('--restants', action='store_true', help='laisse de côté ce qui est déjà traduit')
    a.add_argument('--dictionnaires', default=DOSSIER, help='avec --restants : les dictionnaires servis')
    a.add_argument('--forcer', action='store_true', help='écrase un fichier de travail déjà rempli')
    a.set_defaults(fn=cmd_lots)

    a = sp.add_parser('assembler', help='des fichiers de travail remplis vers i18n/sentinel/<lot>.json')
    a.add_argument('fichiers', nargs='*', help='fichiers de travail (défaut : tout a_traduire/)')
    a.add_argument('--catalogue', default=CATALOGUE)
    a.add_argument('--dossier', default=A_TRADUIRE)
    a.add_argument('--sortie', default=DOSSIER)
    a.set_defaults(fn=cmd_assembler)
    return p


def main(argv=None):
    args = analyseur().parse_args(argv)
    try:
        return args.fn(args)
    except BrokenPipeError:
        #  `| head` a refermé la sortie : ce n'est pas une erreur de l'outil.
        return 0


if __name__ == '__main__':
    sys.exit(main())
