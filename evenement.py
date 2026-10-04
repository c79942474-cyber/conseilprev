# -*- coding: utf-8 -*-
"""LES FAITS DE L'ÉVÉNEMENT, ÉCRITS UNE FOIS.

POURQUOI CE MODULE EXISTE. L'invitation à la formation du 9 novembre 2026 est
servie à DEUX endroits : le bandeau en tête de l'accueil (`index.html`) et la
page d'invitation (`formation-ia.html`), celle qu'on partage par courriel ou
sur LinkedIn. Deux copies d'un même programme divergent — ce dépôt a déjà payé
ce défaut-là, et son commentaire sur `/enveloppe` le dit en toutes lettres :
« c'est toujours l'exemplaire qu'on oublie de corriger qui reste en ligne ».

CE QUE CE MODULE N'EST PAS. Il ne peint aucun écran. Les deux copies sont du
HTML écrit à la main, et c'est voulu : une page d'invitation partagée doit
s'afficher sans JavaScript et être lisible par un moteur de recherche le jour
où quelqu'un la cherche. On ne supprime donc pas la duplication, on la REND
MESURABLE : ce module est la source, et les règles de
`tests/test_evenement_invitation.py` refusent qu'une des deux copies s'en
écarte — un horaire, une étape du programme, une condition, l'adresse
d'inscription.

L'HEURE EST ÉCRITE EN UTC, ET C'EST VOULU. 14 h et 18 h à Paris le 9 novembre
2026, en heure d'hiver (le passage a eu lieu le 25 octobre) : UTC+1. Une heure
laissée au fuseau du lecteur aurait décalé le fichier d'agenda, et le retrait
du bandeau, pour tout visiteur qui n'est pas en France.
"""
import datetime as _dt

#: Le nom de l'événement, tel qu'il s'affiche partout.
TITRE = "Gouverner et sécuriser l'IA"

#: À qui la formation s'adresse — la ligne sous le titre.
PUBLIC = ("Formation pratique pour RSSI, DSI, CAIO, dirigeants et grands "
          "comptes")

#: LE PITCH : pourquoi venir, en quelques phrases. Il ouvre la page
#: d'invitation, et c'est le texte qu'on recopie dans un courriel ou dans un
#: message LinkedIn — d'où sa place ici plutôt que dans le HTML.
#: IL NE PROMET QUE CE QUE LE PROGRAMME TIENT. Chaque phrase renvoie à un
#: module : la technologie (module 1), la conformité (module 2), la sécurité
#: (module 3), la cartographie (module 4), la feuille de route (17:30).
PITCH = (
    "Votre entreprise a commencé à gouverner son IA — un registre, une charte, "
    "un début de conformité à l'AI Act. Mais une IA gouvernée n'est pas une IA "
    "sécurisée, et c'est l'écart que cette après-midi vient combler.\n"
    "En quatre heures, nous relions les deux bouts : choisir la technologie "
    "qui convient à chaque usage, tenir la conformité (AI Act, RGPD, "
    "ISO 42001), puis affronter ce que la gouvernance ne couvre pas — "
    "injection de prompt, agents autonomes, Shadow IA, et les attaques que "
    "l'IA arme désormais.\n"
    "Le format est volontairement court et pratique : pas d'exposé de "
    "principes, un atelier sur vos propres usages et une feuille de route "
    "que vous emportez."
)

#: CE QU'ON EMPORTE EN PARTANT. Trois acquis, chacun produit par une étape du
#: programme : une promesse sans son étape serait une promesse en l'air.
ACQUIS = (
    ("La cartographie de vos usages",
     "Autorisé, interdit ou à valider : l'atelier la construit sur vos "
     "propres cas, pas sur un exemple."),
    ("Vos priorités à 90 jours",
     "Ce que NIS 2 et le Cyber Resilience Act vous imposent en premier, "
     "dans l'ordre où le faire."),
    ("La ligne entre gouverner et sécuriser",
     "De quoi savoir, pour chaque sujet, s'il relève de votre conformité ou "
     "de votre défense — et qui s'en charge."),
)

#: Le jour, en ISO, et les deux bornes en UTC.
JOUR = '2026-11-09'
DEBUT_UTC = _dt.datetime(2026, 11, 9, 13, 0, tzinfo=_dt.timezone.utc)
FIN_UTC = _dt.datetime(2026, 11, 9, 17, 0, tzinfo=_dt.timezone.utc)

#: La date telle qu'elle est ÉCRITE au visiteur, en toutes lettres.
DATE_LISIBLE = 'Lundi 9 novembre 2026, de 14h00 à 18h00'

#: Le lieu, en trois lignes — celles de l'invitation d'origine.
LIEU = 'Novotel Paris Les Halles'
ADRESSE = '8 place Marguerite de Navarre'
VILLE = '75001 Paris'
PAYS = 'France'
ACCES = 'Métro et RER : Châtelet – Les Halles'

#: L'adresse à laquelle on s'inscrit.
INSCRIPTION = 'christophe.cerf@outlook.com'

#: LE LIEN D'INSCRIPTION DE L'INVITATION PDF, OCTET POUR OCTET. C'est
#: l'annotation « Cliquez pour vous inscrire » du document d'origine : même
#: destinataire, même objet, même corps pré-rempli. Le bandeau et la page le
#: servent tel quel — un courriel d'inscription qui n'aurait pas le même objet
#: ne se classerait pas avec les autres.
MAILTO = (
    'mailto:christophe.cerf@outlook.com'
    '?subject=Inscription%20-%20Formation%20IA%20du%209%20novembre%202026'
    '&body=Bonjour%2C%0A%0AJe%20souhaite%20m%27inscrire%20%C3%A0%20la%20'
    'formation%20%C2%AB%20Gouverner%20et%20s%C3%A9curiser%20l%27IA%20%C2%BB%20'
    'du%20lundi%209%20novembre%202026%20(14h-18h)%20au%20Novotel%20Paris%20'
    'Les%20Halles.%0A%0ANom%20%3A%0AFonction%20%3A%0ASoci%C3%A9t%C3%A9%20%3A%0A'
    'T%C3%A9l%C3%A9phone%20%3A%0A%0ACordialement'
)

#: L'invitation d'origine, servie telle qu'elle a été fournie.
PDF = '/evenements/invitation-formation-ia-2026-11-09.pdf'

#: L'adresse de la page d'invitation — celle qu'on partage.
PAGE = '/formation-ia'

#: Le programme : heure, intitulé, et le détail quand il y en a un.
#: Les quatre modules portent `True` : ce sont eux que la frise met en
#: évidence, et le compte des modules se dérive d'ici plutôt que d'être écrit.
PROGRAMME = (
    ('14:00', 'Accueil des participants', '', False),
    ('14:15', 'Ouverture : votre IA est gouvernée, est-elle sécurisée ?',
     'Enjeux pour les directions et les grands comptes', False),
    ('14:30', 'Module 1 · Choisir la bonne IA',
     'Règles, ML, deep learning, IA générative, agents : la technologie '
     'adaptée à chaque problème', True),
    ('15:00', 'Module 2 · Gouvernance et conformité',
     'AI Act, RGPD, ISO 42001, registre des systèmes et Charte IA', True),
    ('15:45', 'Pause café et échanges', '', False),
    ('16:00', 'Module 3 · Cyber for AI et AI Security',
     "Injection de prompt, agents, Shadow IA et menaces armées par l'IA", True),
    ('16:45', 'Module 4 · Atelier pratique',
     'Cartographier vos usages : autorisé, interdit ou à valider', True),
    ('17:30', 'Feuille de route NIS 2 et CRA',
     'Vos priorités à 90 jours, questions et échanges', False),
    ('18:00', 'Clôture', '', False),
)

#: Qui anime, et à quel titre.
ANIMATEUR = 'Christophe CERF'
ANIMATEUR_QUALITE = ('CEO de CONSEILPREV, expert Cyber GRC, AI Security et '
                     'Safety Engineering, certifié AIGP (IAPP).')

#: LES CONDITIONS, ET ELLES SE LISENT AVANT DE S'INSCRIRE. Elles voyagent
#: aussi dans le fichier d'agenda et dans le lien Google Agenda : une entrée
#: de calendrier qui affirmerait une date et un lieu fermes tairait ce que la
#: page dit.
GRATUITE = 'Gratuit sur inscription · places limitées'
CONDITIONS = (
    "L'événement peut être reporté ou décalé en cas de participation "
    "insuffisante, ou annulé au plus tard 10 jours avant.",
    "Si besoin, l'événement pourra se dérouler dans un autre Novotel à Paris, "
    "à une autre date à définir.",
)

#: Les coordonnées du pied de l'invitation.
TELEPHONE = '+33 6 60 69 21 45'
TELEPHONE_LIEN = 'tel:+33660692145'
COURRIEL = 'christophe.cerf@i-aes.com'
LINKEDIN = 'https://www.linkedin.com/in/cerfchristophe'
SITES = ('https://i-aes.eu', 'https://i-aes.com')


def itineraire():
    """Le lien d'itinéraire, construit depuis l'adresse — pas recopié.

    Une destination écrite deux fois est une destination qui finira par
    désigner deux endroits."""
    from urllib.parse import quote
    dest = '%s, %s, %s' % (LIEU, ADRESSE, VILLE)
    return ('https://www.google.com/maps/dir/?api=1&destination='
            + quote(dest, safe=''))


def google_agenda(details=None):
    """Le lien Google Agenda, bornes comprises, conditions comprises."""
    from urllib.parse import quote
    corps = details if details is not None else (
        PUBLIC + '. Gratuit sur inscription : ' + INSCRIPTION)
    horo = lambda t: t.strftime('%Y%m%dT%H%M%SZ')  # noqa: E731
    return ('https://calendar.google.com/calendar/render?action=TEMPLATE'
            '&text=' + quote(TITRE + ' — formation CONSEILPREV', safe='')
            + '&dates=' + horo(DEBUT_UTC) + '%2F' + horo(FIN_UTC)
            + '&ctz=Europe%2FParis'
            + '&location=' + quote('%s, %s, %s' % (LIEU, ADRESSE, VILLE), safe='')
            + '&details=' + quote(corps, safe=''))


def _verifier():
    """Les incohérences que ce module ne doit pas pouvoir porter."""
    f = []
    if FIN_UTC <= DEBUT_UTC:
        f.append('la fin précède le début')
    if DEBUT_UTC.strftime('%Y-%m-%d') != JOUR:
        f.append('DEBUT_UTC ne tombe pas le jour déclaré (%s)' % JOUR)
    #  14 h – 18 h à Paris, en heure d'hiver : 13 h – 17 h UTC. Écrit ici
    #  parce que c'est l'erreur qu'on ne voit pas — une entrée d'agenda
    #  décalée d'une heure ne se signale qu'au moment où la salle est vide.
    if (DEBUT_UTC.hour, FIN_UTC.hour) != (13, 17):
        f.append('les bornes UTC ne valent plus 14 h – 18 h à Paris')
    heures = [h for h, _, _, _ in PROGRAMME]
    if heures != sorted(heures):
        f.append('le programme n\'est pas dans l\'ordre : %s' % heures)
    if heures[0] != '14:00' or heures[-1] != '18:00':
        f.append('le programme ne couvre pas 14:00 → 18:00')
    if not any(m for _, _, _, m in PROGRAMME):
        f.append('aucun module dans le programme')
    if INSCRIPTION not in MAILTO:
        f.append("l'adresse d'inscription n'est pas celle du lien mailto")
    if not PAGE.startswith('/') or not PDF.startswith('/'):
        f.append('PAGE et PDF doivent être des chemins absolus')
    for i, c in enumerate(CONDITIONS):
        if len(c) < 30:
            f.append('condition %d trop courte pour dire quoi que ce soit' % i)
    #  UN PITCH VIDE OU D'UNE LIGNE NE PRÉSENTE RIEN, et c'est le genre de
    #  champ qu'on vide « en attendant » sans que rien ne le signale.
    if len(PITCH.split('\n')) < 2 or len(PITCH) < 200:
        f.append('le pitch ne présente pas l\'événement')
    if len(ACQUIS) < 3:
        f.append('moins de trois acquis annoncés')
    for titre, detail in ACQUIS:
        if len(titre) < 8 or len(detail) < 40:
            f.append('acquis « %s » : sans contenu' % titre)
    return f


_FAUTES = _verifier()
if _FAUTES:
    #  RuntimeError, ET PAS AssertionError : une assertion disparaît sous
    #  `python -O`, et la garde avec elle.
    raise RuntimeError('evenement : ' + ' | '.join(_FAUTES))
