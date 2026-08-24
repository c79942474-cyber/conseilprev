# -*- coding: utf-8 -*-
"""LA REVUE DE PRESSE — hebdomadaire, et mensuelle internationale.

CE MODULE NE RÉDIGE RIEN. Il DÉCOUPE le corpus déjà publié dans une fenêtre de
dates et le range. Chaque nombre qu'il rend est un compte sur des fiches, et
chaque fiche porte déjà sa source, son statut et son incertitude. Il n'ajoute
aucune phrase d'appréciation : une revue de presse qui commente cesse d'être
une revue.

════════════════════════════════════════════════════════════════════════════
CE QUE LA REVUE COMPTE — ET C'EST LA PREMIÈRE CHOSE À COMPRENDRE
════════════════════════════════════════════════════════════════════════════
Elle compte les fiches dont LE FAIT tombe dans la période, jamais celles que
NOUS avons collectées pendant la période. Les deux dates existent et ne
coïncident pas : CISA inscrit au catalogue une faille exploitée depuis des
mois, MITRE publie en août une étude de cas d'un incident de mars.

Une revue bâtie sur la date de collecte dirait « la semaine du 17 août » en
alignant des faits de 2021. Une revue bâtie sur la date du fait dit ce qui
s'est passé cette semaine-là — et se tait quand rien ne s'y est passé.

LA CONSÉQUENCE EST ASSUMÉE : la semaine en cours est souvent VIDE. C'est un
résultat, pas une panne, et la revue l'écrit — avec le nombre de jours qui
séparent la fin de la période du fait le plus récent que le corpus porte.

════════════════════════════════════════════════════════════════════════════
LES DATES DE CONVENTION SONT COMPTÉES À PART
════════════════════════════════════════════════════════════════════════════
Une partie du corpus porte une date POSÉE par ce site faute de mieux — un
mix électrique annuel devient le 1er janvier. Ces fiches tomberaient toutes
dans la même semaine et gonfleraient une revue de janvier sans qu'aucun fait
ne s'y soit produit. Elles ne sont donc pas retenues dans le corps de la
revue, et leur nombre est dit : les taire ferait disparaître du corpus des
fiches réelles, sans un mot.

════════════════════════════════════════════════════════════════════════════
« INTERNATIONALE » EST UNE RÈGLE ÉCRITE, PAS UNE IMPRESSION
════════════════════════════════════════════════════════════════════════════
La revue mensuelle a été demandée « de revue internationale ». Le mot ne veut
rien dire tant qu'on n'a pas dit par rapport à QUOI. La règle retenue, servie
avec la revue pour que le lecteur la pèse :

    Est retenue la fiche qui rattache le fait à un territoire HORS DE FRANCE
    — soit par le pays du fait, soit par le siège d'une entreprise que la
    source nomme.

Ce qui est écarté est compté et dit : une fiche que rien ne rattache à un
territoire n'est pas « française », elle est SANS TERRITOIRE, et la faire
passer pour internationale ou pour nationale serait deux fois faux.
"""

import calendar
from datetime import date, timedelta

import organisations as ORG
import redaction as RED
import veille as V

VERSION = "2026.08.24"

GENRES = ("semaine", "mois")

#: LA RÈGLE « INTERNATIONALE », EN TOUTES LETTRES ET DANS LES DEUX LANGUES.
#: Servie avec la revue : une sélection dont on ignore le critère ne se
#: discute pas, elle se croit.
REGLE_INTERNATIONALE = (
    "Est retenue la fiche qui rattache le fait à un territoire hors de "
    "France — par le pays du fait, ou par le siège d'une entreprise que la "
    "source nomme. Une fiche que rien ne rattache à un territoire est écartée "
    "et comptée à part : elle n'est ni internationale ni française.",
    "An entry is kept when it ties the fact to a territory outside France — "
    "either through the country of the fact, or through the head office of a "
    "company the source names. An entry tied to no territory at all is set "
    "aside and counted separately: it is neither international nor French.",
)

#: LE PAYS DE RÉFÉRENCE. Écrit une fois, nommé, plutôt que « FR » dispersé
#: dans trois conditions — c'est le cabinet qui est français, et le jour où
#: cette revue servirait ailleurs, une seule ligne changerait.
PAYS_DU_CABINET = "FR"

_MOIS = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet",
         "août", "septembre", "octobre", "novembre", "décembre")
_MOIS_EN = ("January", "February", "March", "April", "May", "June", "July",
            "August", "September", "October", "November", "December")


def _jour(x):
    """Une date ISO en `date`, ou None. Ce module ne devine aucune date."""
    try:
        return date.fromisoformat(str(x)[:10])
    except (TypeError, ValueError):
        return None


def periode(genre="semaine", ancre=None):
    """LES BORNES D'UNE PÉRIODE, ET SON INTITULÉ DANS LES DEUX LANGUES.

    LA SEMAINE EST CELLE DE LA NORME ISO — du lundi au dimanche. Une « semaine
    glissante de sept jours » aurait produit des revues qui se chevauchent, et
    deux revues successives auraient compté deux fois les mêmes faits.
    """
    if genre not in GENRES:
        raise ValueError("genre inconnu : %r" % (genre,))
    a = _jour(ancre) or date.today()
    if genre == "semaine":
        debut = a - timedelta(days=a.weekday())
        fin = debut + timedelta(days=6)
    else:
        debut = a.replace(day=1)
        fin = a.replace(day=calendar.monthrange(a.year, a.month)[1])
    return {
        "genre": genre,
        "debut": debut.isoformat(),
        "fin": fin.isoformat(),
        "libelle": _libelle(genre, debut, fin, "fr"),
        "libelle_en": _libelle(genre, debut, fin, "en"),
    }


def _libelle(genre, debut, fin, langue):
    mois = _MOIS_EN if langue == "en" else _MOIS
    if genre == "mois":
        return "%s %d" % (mois[debut.month - 1], debut.year)
    if langue == "en":
        return "Week of %d %s to %d %s %d" % (
            debut.day, mois[debut.month - 1], fin.day, mois[fin.month - 1],
            fin.year)
    return "Semaine du %d %s au %d %s %d" % (
        debut.day, mois[debut.month - 1], fin.day, mois[fin.month - 1],
        fin.year)


def precedente(p):
    """La période d'avant, calculée sur ses propres bornes — jamais « moins
    sept jours » : un mois n'en fait pas trente."""
    d = _jour(p["debut"])
    return periode(p["genre"], (d - timedelta(days=1)).isoformat())


def derniere_ancre(fiches, genre="semaine", international=False):
    """LA PÉRIODE LA PLUS RÉCENTE QUE LE CORPUS DOCUMENTE.

    POURQUOI CE DÉFAUT PLUTÔT QUE « CETTE SEMAINE ». Mesuré sur le corpus
    servi : le fait le plus récent a plusieurs semaines. Ouvrir la revue sur
    la semaine en cours servirait donc une page vide à chaque visite, et le
    lecteur en conclurait une panne plutôt qu'un état du corpus.

    LA PAGE DIT LAQUELLE ELLE OUVRE, ET DE COMBIEN ELLE EST EN ARRIÈRE. Sans
    cette mention, ouvrir une revue de juillet le 24 août serait la même
    tromperie dans l'autre sens.

    L'ANCRE SUIT LA RÈGLE DE LA REVUE QU'ELLE OUVRE. Mesuré : le mois le plus
    récent du corpus ne porte AUCUNE fiche rattachée à un territoire hors de
    France. Ouvrir la revue internationale sur ce mois-là servirait une page
    vide alors que le corpus en documente d'autres — le lecteur conclurait
    que la rubrique ne marche pas, quand elle marche et ne trouve rien ICI.
    """
    lot = _retenues(fiches)
    if international:
        lot = [f for f in lot if _international(f) is True]
    dates = [_jour(f.get("date_fait")) for f in lot]
    dates = [d for d in dates if d]
    return max(dates).isoformat() if dates else None


def _retenues(fiches):
    """Les fiches qu'une revue a le droit de compter : publiées, et dont la
    date est un CONSTAT. Voir l'en-tête pour les dates de convention."""
    return [f for f in V.publiables(fiches) if not f.get("date_convention")]


def _dans(fiches, p):
    return [f for f in fiches
            if p["debut"] <= str(f.get("date_fait", ""))[:10] <= p["fin"]]


def _international(f):
    """La règle écrite plus haut, appliquée — et rien de plus.

    Rend `True` (hors de France), `False` (France seulement) ou `None` (rien
    ne rattache cette fiche à un territoire). Les trois cas sont distincts, et
    les confondre est exactement ce que cette fonction évite : `None` n'est
    pas `False`.
    """
    territoires = {str(x).upper() for x in (f.get("pays") or [])}
    territoires |= {ORG.siege(c) for c in (f.get("organisations") or [])}
    territoires.discard(None)
    if not territoires:
        return None
    return bool(territoires - {PAYS_DU_CABINET})


def revue(fiches, genre="semaine", ancre=None, international=False,
          langue="fr"):
    """LA REVUE D'UNE PÉRIODE — ce qu'elle contient, et ce qu'elle ne contient
    pas.

    L'ORDRE DES BLOCS EST CELUI DU MOTEUR : la portée d'abord, la date
    ensuite. C'est le même tri que le fil, et pour la même raison — trier
    d'abord par date ferait descendre une rupture sous trois brèves du
    lendemain.
    """
    i = 1 if langue == "en" else 0
    p = periode(genre, ancre)
    publiees = V.publiables(fiches)
    retenues = _retenues(publiees)

    # LE CORPUS VIDE N'EST PAS UNE PÉRIODE VIDE, ET LES CONFONDRE EST LE PIRE
    # DES DEUX. Constaté au navigateur, sur un serveur qui venait de démarrer :
    # la première visite tombait avant la fin de la collecte, `ancre` valait
    # donc `None`, la revue s'ouvrait sur la semaine EN COURS et annonçait
    # « aucun fait daté de cette période n'est entré au corpus » — une phrase
    # exacte sur une page qui ne l'était pas. Le lecteur en tirait un jugement
    # sur les sources, alors que rien n'avait encore été lu.
    corpus_vide = not publiees

    dans = _dans(retenues, p)
    # LES DATES DE CONVENTION ÉCARTÉES SONT COMPTÉES, jamais tues.
    conventions = len([f for f in _dans(publiees, p) if f.get("date_convention")])

    ecartees_sans_territoire = 0
    ecartees_france = 0
    if international:
        garde = []
        for f in dans:
            etat = _international(f)
            if etat is True:
                garde.append(f)
            elif etat is None:
                ecartees_sans_territoire += 1
            else:
                ecartees_france += 1
        dans = garde

    dans = sorted(dans, key=lambda f: (V.IMPACTS.get(f.get("impact"), {})
                                       .get("rang", 9),
                                       V._inverse(f.get("date_fait", ""))))

    # LE BLOC EST LA PORTÉE, dans l'ordre du référentiel — et une portée sans
    # fiche n'ouvre pas de bloc : un intertitre vide se lit comme une panne
    # d'affichage.
    blocs = []
    for cle in V.ORDRE_IMPACTS:
        lot = [f for f in dans if f.get("impact") == cle]
        if not lot:
            continue
        im = V.IMPACTS[cle]
        blocs.append({
            "cle": cle,
            "nom": (im.get("nom_en") or im["nom"]) if i else im["nom"],
            "n": len(lot),
            "fiches": [_vignette(f, langue) for f in lot],
        })

    prec = precedente(p)
    lot_prec = _dans(retenues, prec)
    if international:
        lot_prec = [f for f in lot_prec if _international(f) is True]

    return {
        "ok": True,
        "version": VERSION,
        "corpus_vide": corpus_vide,
        "periode": p,
        "international": bool(international),
        "regle_internationale": REGLE_INTERNATIONALE[i] if international else None,
        "blocs": blocs,
        "n": len(dans),
        "par_sujet": _compter(dans, "sujet", langue),
        "par_source": _par_source(dans),
        # CE QUE LA PÉRIODE NE DIT PAS — la moitié du travail d'une revue.
        "muets": _muets(dans, publiees, langue),
        "conventions_ecartees": conventions,
        "ecartees_sans_territoire": ecartees_sans_territoire,
        "ecartees_france": ecartees_france,
        # LA COMPARAISON EST UN COMPTE, PAS UNE TENDANCE. « En hausse » sur
        # deux points serait une affirmation que rien ne fonde.
        "precedente": {"periode": prec, "n": len(lot_prec),
                       "ecart": len(dans) - len(lot_prec)},
        "retard": _retard(p, retenues),
        # LES DEUX RUBRIQUES QUI NE SE DÉRIVENT PAS. Elles sont vides, et
        # elles disent pourquoi — voir `redaction.py`.
        "rubriques": [RED.rubrique(n, langue, p["debut"], p["fin"])
                      for n in RED.ORDRE_NATURES],
    }


def _vignette(f, langue):
    """CE QU'UNE ENTRÉE DE REVUE PORTE. Assez pour se lire seule — un titre
    sans source ni statut serait un titre de dépêche, ce que ce site n'écrit
    pas — et pas le corps de l'analyse, qui vit sur la fiche."""
    s = f.get("source") or {}
    return {
        "id": f.get("id"),
        "titre": f.get("titre"),
        "chapeau": f.get("chapeau"),
        "date_fait": f.get("date_fait"),
        "impact": f.get("impact"),
        "sujet": f.get("sujet"),
        "sujet_nom": f.get("sujet_nom"),
        "statut": f.get("statut"),
        "statut_nom": f.get("statut_nom"),
        "source_nom": s.get("nom"),
        "source_url": f.get("source_url"),
        "organisations": [ORG.nom(c, langue)
                          for c in (f.get("organisations") or [])],
        "pays": [V.nom_pays(c)["en" if langue == "en" else "fr"]
                 for c in (f.get("pays") or [])],
    }


def _compter(fiches, cle, langue):
    c = {}
    for f in fiches:
        c[f.get(cle)] = c.get(f.get(cle), 0) + 1
    table = V.SUJETS if cle == "sujet" else {}
    out = []
    for k, n in c.items():
        e = table.get(k) or {}
        nom = (e.get("nom_en") or e.get("nom") or k) if langue == "en" \
            else (e.get("nom") or k)
        out.append({"cle": k, "nom": nom, "n": n})
    return sorted(out, key=lambda x: (-x["n"], x["nom"]))


def _par_source(fiches):
    c = {}
    for f in fiches:
        s = (f.get("source") or {}).get("nom") or f.get("source_cle")
        c[s] = c.get(s, 0) + 1
    return sorted(({"nom": k, "n": v} for k, v in c.items()),
                  key=lambda x: (-x["n"], x["nom"]))


def _muets(dans, publiees, langue):
    """LES AXES QUI N'ONT RIEN DONNÉ CETTE PÉRIODE-LÀ.

    UNE REVUE QUI N'AFFICHE QUE SES RUBRIQUES FÉCONDES enseigne au lecteur une
    couverture qu'elle n'a pas. Le sujet muet est nommé, et il est nommé PARMI
    CEUX QUE LE CORPUS PORTE — pas parmi tous les sujets du référentiel, ce
    qui reprocherait à la semaine un silence qui est celui du corpus entier.
    """
    vus = {f.get("sujet") for f in dans}
    au_corpus = {f.get("sujet") for f in publiees}
    out = []
    for cle in V.ORDRE_SUJETS:
        if cle in au_corpus and cle not in vus:
            e = V.SUJETS[cle]
            out.append({"cle": cle,
                        "nom": (e.get("nom_en") or e["nom"]) if langue == "en"
                               else e["nom"]})
    return out


def _retard(p, retenues):
    """DE COMBIEN LA PÉRIODE EST EN ARRIÈRE SUR AUJOURD'HUI, et sur quoi.

    DEUX NOMBRES, PAS UN. Le premier dit l'écart entre la fin de la période et
    le jour où la page est lue ; le second, l'écart entre ce jour et le fait
    le plus récent du corpus, toutes périodes confondues. Le second est le
    seul qui parle du CORPUS : si la revue de juillet est ouverte en août,
    ce n'est pas la revue qui est en retard, c'est le corpus qui s'arrête là.

    ET ON NE DIT PAS « IL NE S'EST RIEN PASSÉ ». Aucune de ces deux mesures ne
    permet cette phrase : elles disent qu'aucun fait daté de cette période
    n'est ENTRÉ AU CORPUS, ce qui dépend d'abord de ce que les sept
    collecteurs couvrent.
    """
    dates = [_jour(f.get("date_fait")) for f in retenues]
    dates = [d for d in dates if d]
    dernier = max(dates).isoformat() if dates else None
    fin = _jour(p["fin"])
    today = date.today()
    return {
        "aujourdhui": today.isoformat(),
        "jours_depuis_la_fin": max(0, (today - fin).days) if fin else None,
        "dernier_fait": dernier,
        "jours_depuis_le_dernier_fait": (
            (today - _jour(dernier)).days if dernier else None),
        # « C'EST LA PLUS RÉCENTE QUE LE CORPUS DOCUMENTE » NE SE DIT QUE SI
        # C'EST VRAI. Constaté au navigateur : la phrase restait affichée après
        # un clic sur « période précédente », au-dessus d'une semaine vide qui
        # n'était évidemment pas la plus récente. Une réserve qui suit le
        # lecteur sans se vérifier devient une affirmation fausse.
        "est_la_plus_recente": bool(
            dernier and p["debut"] <= dernier <= p["fin"]),
    }


def sante(fiches=None):
    """CE QUE CE MODULE DÉCOUPE, MESURÉ SUR LE CORPUS SERVI."""
    f = list(fiches or [])
    pub = V.publiables(f)
    ret = _retenues(f)
    terr = [_international(x) for x in ret]
    return {
        "module": "revue",
        "version": VERSION,
        "portee": "Découpe le corpus publié en périodes ISO et le range. "
                  "N'écrit aucune phrase, ne commente rien, et compte à part "
                  "ce qu'elle écarte.",
        "genres": list(GENRES),
        "fiches_publiees": len(pub),
        "fiches_retenues": len(ret),
        "dates_de_convention_ecartees": len(pub) - len(ret),
        "hors_de_france": sum(1 for x in terr if x is True),
        "france_seulement": sum(1 for x in terr if x is False),
        "sans_territoire": sum(1 for x in terr if x is None),
        "derniere_semaine_documentee": derniere_ancre(f, "semaine"),
        "modeles_de_langage": 0,
        "redaction": RED.sante(),
    }
