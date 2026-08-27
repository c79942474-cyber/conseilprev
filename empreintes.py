"""DIX-SEPT ALLERS-RETOURS POUR DES FICHIERS QUI N'AVAIENT PAS CHANGÉ.

CE QUI A DÉCLENCHÉ CE MODULE. Chronométrage d'une session Sentinel ordinaire —
seconde visite, cache du navigateur intact, puis ouverture des quatre modules
cartographiques :

    5×  /fleches.js
    4×  /drapeaux.js
    4×  /figures_export.js
    3×  /factcheck.js
    1×  /sentinel.page.js
    ──
    17 requêtes de revalidation

Aucun de ces fichiers n'avait bougé. Le navigateur les avait tous en cache. Il
a quand même demandé au serveur, dix-sept fois, la permission de s'en servir.

POURQUOI. Flask sert les fichiers statiques avec `Cache-Control: no-cache`.
Cette directive n'interdit pas de GARDER la réponse — elle interdit de la
SERVIR sans demander. Le navigateur repose donc la question à chaque
chargement, et à chaque iframe : le corps ne repart pas (304, trois cents
octets), mais l'aller-retour, lui, est payé plein tarif. Depuis un navigateur
français vers Francfort, c'est quarante millisecondes par question.

POURQUOI ON NE POUVAIT PAS SIMPLEMENT ALLONGER LE CACHE. Un `max-age` long sur
`/sentinel.page.js` rendrait toute mise en ligne invisible pendant sa durée :
les visiteurs continueraient d'exécuter l'ancien fichier sans jamais le savoir.
C'est la raison, parfaitement valable, pour laquelle le cache était court.

CE QUE FAIT CE MODULE. Il déplace la question de « ce fichier a-t-il changé ? »
vers l'ADRESSE elle-même. `/sentinel.page.js` devient
`/sentinel.page.js?v=1a2b3c4d5e`, où l'empreinte se déduit du fichier sur
disque. Une adresse qui porte sa version peut être mise en cache un an sans
risque : quand le fichier change, l'empreinte change, l'adresse change, et le
navigateur redemande — non pas parce qu'on le lui a permis, mais parce que ce
n'est plus le même fichier.

CE QUI GARANTIT QU'UNE MISE EN LIGNE EST VUE TOUT DE SUITE. Les pages HTML,
elles, restent en `no-cache` : elles revalident à chaque visite, sans corps
(304). C'est là que la nouvelle adresse est annoncée. Le raccourci d'un an ne
s'applique donc qu'à ce que la page vient de nommer.

CE QUE CE MODULE NE FAIT PAS. Il ne touche à rien d'extérieur : ni Google
Fonts, ni une adresse relative, ni un chemin qu'il ne retrouve pas sur disque.
Une empreinte qu'on ne peut pas calculer n'est pas inventée — l'adresse reste
telle quelle, et le fichier retombe sur l'ancien comportement.
"""
import hashlib
import os
import re

_DOSSIER = os.path.dirname(os.path.abspath(__file__))

#: La politique servie à une adresse qui porte la bonne empreinte. « immutable »
#: dit au navigateur de ne pas revalider même sur un rechargement forcé — c'est
#: exact ici : cette adresse-là ne désignera jamais un autre contenu.
IMMUABLE = 'public, max-age=31536000, immutable'

#: Ce qu'on marque : des adresses ABSOLUES de notre propre site vers des
#: fichiers servis depuis la racine. Le `//` d'une adresse externe
#: (`https://unpkg.com/…`) ne peut pas correspondre, puisqu'on exige un `/`
#: suivi d'un caractère de nom de fichier.
#:
#: CETTE ANCRE N'EST PAS CE QUI PROTÈGE LES ADRESSES EXTERNES. Une mutation
#: l'a montré : en l'élargissant à n'importe quoi, `https://unpkg.com/x.css`
#: est bien capturé — et ressort quand même intact, parce qu'aucun fichier de
#: ce nom n'existe sur le disque et qu'on n'invente pas d'empreinte. La
#: garantie tient donc à `version()`, pas à l'expression. Ce qu'apporte
#: l'ancre est le coût : sans elle, chaque adresse distante d'une page
#: déclencherait un `os.stat` inutile.
_ATTRIBUT = re.compile(
    r'(?P<avant>\s(?:src|href)=")(?P<chemin>/[A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]+)*'
    r'\.(?:js|css))(?P<apres>")')


def version(chemin):
    """Empreinte courte d'un fichier, recalculée quand il change sur disque.

    LA MÊME CLÉ QUE LE CACHE DES PAGES : horodatage de modification et taille.
    Deux mécanismes qui se périmeraient sur des critères différents finiraient
    par se contredire — une page servie depuis le cache mémoire annoncerait une
    version que le disque a déjà remplacée.

    Rend None si le fichier n'existe pas : on ne fabrique pas une empreinte
    pour une adresse qu'on ne sait pas relire.

    IL N'Y A PAS DE CACHE ICI, ET C'EST VOULU. La première version en gardait
    un, avec son verrou. Une mutation l'a démasqué : le retirer ne changeait
    RIEN au résultat — la clé est déjà lue sur le disque, et ce qu'on économise
    est un sha256 sur une trentaine d'octets. Un cache qui n'accélère rien est
    du code à maintenir, plus une occasion de se désynchroniser du disque.
    L'appel à `os.stat`, lui, reste : c'est lui qui détecte le changement.
    """
    if not chemin or '..' in chemin:
        return None
    piste = os.path.join(_DOSSIER, chemin.lstrip('/'))
    try:
        st = os.stat(piste)
    except OSError:
        return None
    return hashlib.sha256(
        ('%d-%d' % (st.st_mtime_ns, st.st_size)).encode('ascii')).hexdigest()[:10]


def marquer(html):
    """Ajoute son empreinte à chaque adresse locale de script ou de feuille.

    Appelé UNE FOIS par version de page, depuis le cache mémoire — jamais par
    visite. Le coût est celui d'une expression régulière sur le fichier, payé
    au démarrage puis à chaque mise en ligne.
    """
    def _un(m):
        v = version(m.group('chemin'))
        if not v:
            return m.group(0)
        return '%s%s?v=%s%s' % (m.group('avant'), m.group('chemin'), v, m.group('apres'))
    return _ATTRIBUT.sub(_un, html)


def immuable(chemin, demandee):
    """Vrai si l'empreinte demandée est bien celle du fichier sur disque.

    ON NE FAIT PAS CONFIANCE À LA PRÉSENCE D'UN `?v=`. Une adresse portant une
    empreinte périmée — page très ancienne gardée par un intermédiaire, adresse
    recopiée à la main — désigne un contenu qui n'est plus celui-là. La servir
    pour un an la figerait pour de bon. On revalide, comme avant.
    """
    if not demandee:
        return False
    return version(chemin) == demandee
