# -*- coding: utf-8 -*-
"""LE DICTIONNAIRE ANGLAIS DU CORPS DE SENTINEL — côté serveur.

CE QUI EXISTAIT, ET CE QUI MANQUAIT. Le moteur bilingue de Sentinel
(sentinel.page.js, SENT_T) traduit la COQUILLE : menu, fil d'Ariane, surtitre,
titre et chapeau des pages — 213 clés portées par des attributs `data-i18n`.
Le corps des 118 pages, 25 900 mots dans le HTML et 4 000 chaînes rendues par
le JavaScript, restait en français. Marquer 4 300 éléments un à un dans un
fichier de 890 Ko aurait été fragile et ne couvrait de toute façon pas ce que
le JavaScript rend après coup.

LE CORPS SE TRADUIT DONC PAR CONTENU : la clé d'une traduction est le texte
français lui-même, NORMALISÉ, et le navigateur retrouve chaque chaîne au
moment de l'afficher (sentinel.i18n.js). Ce module est la moitié serveur :
  · `normaliser()` — LE MÊME algorithme que `sentNormaliser()` côté
    JavaScript, à la lettre : un outil d'inventaire qui produirait des clés
    différentes de celles que le navigateur calcule ne traduirait rien ;
  · `fusionner()` — les fichiers i18n/sentinel/*.json réunis en un seul
    dictionnaire, avec les conflits nommés ;
  · `servir()` — le corps JSON et son ETag, recalculés seulement quand un
    fichier du dossier change.

POURQUOI LES CHIFFRES DEVIENNENT « # ». « 46 juridictions analysées selon 12
critères » est une phrase, pas quarante-six phrases : un compteur que le
JavaScript fait varier ne doit pas rendre la clé introuvable. Les chiffres
d'origine sont réinjectés dans la valeur anglaise à l'affichage, dans l'ordre.
"""
import glob
import hashlib
import io
import json
import os
import re
import unicodedata

DOSSIER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       'i18n', 'sentinel')

#  CHAQUE CARACTÈRE BLANC, y compris ceux que `str.split()` ou `\s` ne
#  couvrent pas tous de la même façon selon le langage : l'insécable, la fine
#  insécable, l'espace fine, la marque d'ordre des octets. La liste est écrite
#  en clair pour être IDENTIQUE à celle de sentinel.i18n.js.
_BLANCS = re.compile(u'[\\s\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f'
                     u'\u205f\u3000\ufeff]+')
#  UNE SUITE DE CHIFFRES, décimales comprises : « 2,5 » et « 2024.1 » sont un
#  seul nombre, « 12 critères » en contient un.
_CHIFFRES = re.compile(r'[0-9]+(?:[.,][0-9]+)*')


def aplanir(s):
    """NFC, chaque blanc devient une espace, les suites se réduisent, trim.
    C'est la forme « lisible » d'un texte : celle qu'un inventaire montre à
    la personne qui traduit."""
    s = unicodedata.normalize('NFC', u'' if s is None else u'%s' % s)
    s = _BLANCS.sub(u' ', s)
    return s.strip(u' ')


def normaliser(s):
    """La CLÉ d'un texte français : aplani, puis chaque nombre devient « # »."""
    return _CHIFFRES.sub(u'#', aplanir(s))


def _fichiers(dossier):
    return sorted(glob.glob(os.path.join(dossier, '*.json')))


def signature(dossier=None):
    """Ce qui change quand un fichier du dossier change : nom, taille, date.
    Sert à ne relire le dossier que quand c'est utile."""
    dossier = DOSSIER if dossier is None else dossier
    sig = []
    for p in _fichiers(dossier):
        try:
            st = os.stat(p)
            sig.append((os.path.basename(p), st.st_size, st.st_mtime_ns))
        except OSError:
            sig.append((os.path.basename(p), -1, -1))
    return tuple(sig)


def fusionner(dossier=None):
    """Tous les fichiers du dossier en un dictionnaire {'texte', 'bloc'}.

    Rend (dico, fautes). UNE MÊME CLÉ AVEC DEUX VALEURS DIFFÉRENTES est une
    faute nommée — fichier, régime, clé — et la PREMIÈRE valeur (ordre
    alphabétique des fichiers) gagne : deux traductions concurrentes ne
    doivent pas se remplacer au hasard d'un ordre de lecture. Un fichier
    illisible est nommé aussi, et les autres sont servis quand même : un
    dictionnaire amputé vaut mieux qu'une page qui ne se traduit plus."""
    dossier = DOSSIER if dossier is None else dossier
    dico = {'texte': {}, 'bloc': {}}
    origine = {'texte': {}, 'bloc': {}}
    fautes = []
    for p in _fichiers(dossier):
        nom = os.path.basename(p)
        try:
            with io.open(p, encoding='utf-8') as f:
                lot = json.load(f)
        except (OSError, ValueError) as e:
            fautes.append(u'%s : illisible (%s)' % (nom, e))
            continue
        if not isinstance(lot, dict):
            fautes.append(u'%s : la racine n\'est pas un objet' % nom)
            continue
        for regime in ('texte', 'bloc'):
            entrees = lot.get(regime) or {}
            if not isinstance(entrees, dict):
                fautes.append(u'%s : « %s » n\'est pas un objet' % (nom, regime))
                continue
            for cle, val in entrees.items():
                if not isinstance(val, (str, u''.__class__)):
                    fautes.append(u'%s : %s « %s » n\'est pas une chaîne'
                                  % (nom, regime, cle[:60]))
                    continue
                deja = dico[regime].get(cle)
                if deja is None:
                    dico[regime][cle] = val
                    origine[regime][cle] = nom
                elif deja != val:
                    fautes.append(
                        u'%s : %s « %s » déjà défini dans %s avec une autre '
                        u'valeur — la première gagne'
                        % (nom, regime, cle[:60], origine[regime][cle]))
    return dico, fautes


#: dossier → (signature, corps JSON, etag). Un seul dossier en pratique ; le
#: dictionnaire fait ce que fera la table quand elle aura plusieurs entrées.
_CACHE = {}


def servir(dossier=None, journal=None):
    """Le corps JSON à servir et son ETag — relus si le dossier a changé.

    Un dossier absent ou vide rend un dictionnaire VIDE, pas une erreur : le
    navigateur qui le reçoit garde la coquille traduite et le corps en
    français, ce qui est exactement l'état d'avant ce module.

    `dossier` se résout à l'APPEL (DOSSIER du module), pas à la définition :
    une règle qui pointe le module vers un dossier d'essai doit être suivie."""
    dossier = DOSSIER if dossier is None else dossier
    sig = signature(dossier)
    ent = _CACHE.get(dossier)
    if ent is not None and ent[0] == sig:
        return ent[1], ent[2]
    dico, fautes = fusionner(dossier)
    if journal is not None:
        for f in fautes:
            journal.error(u'SENTINEL_I18N_CONFLIT %s' % f)
    corps = json.dumps(dico, ensure_ascii=False, separators=(',', ':'),
                       sort_keys=True)
    etag = '"sentinel-en-%s"' % hashlib.sha1(corps.encode('utf-8')).hexdigest()[:16]
    _CACHE[dossier] = (sig, corps, etag)
    return corps, etag
