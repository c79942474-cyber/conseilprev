"""LE MODÈLE ÉDITORIAL — une fiche de veille, et ce qui l'autorise à paraître.

CE QUE CE SITE PROMET, ET QU'IL DOIT DONC TENIR. Il ne promet pas d'être le
plus rapide ni le plus complet : il promet que tout ce qu'il affiche porte son
origine, sa date, et une lecture critique SIGNÉE. C'est peu de mots et
beaucoup de conséquences — la première étant qu'une fiche sans source ne peut
pas exister dans ce moteur. Elle n'est pas « affichée avec une réserve » :
elle est REFUSÉE.

LES QUATRE CHOSES QU'UNE FICHE SÉPARE, ET QUE PRESQUE TOUS LES SITES DE VEILLE
CONFONDENT :

  1. LE FAIT — ce qui est établi, avec la source qui l'établit et la date du
     fait (jamais la date où on l'a lu, qui ne dit rien).
  2. LA LECTURE — ce que le cabinet en comprend. C'est un AVIS. Il est daté,
     signé, et présenté comme tel : le confondre avec le fait est la faute
     qui transforme une veille en publicité.
  3. LA PORTÉE — ce que cela change pour une décision. C'est là qu'un lecteur
     professionnel va directement, et c'est le seul endroit où ce site vaut
     mieux qu'un fil d'actualité.
  4. CE QU'ON NE SAIT PAS. Un point d'incertitude déclaré vaut mieux qu'une
     assurance empruntée. Le champ est OBLIGATOIRE.

LE STATUT DE VÉRIFICATION N'EST PAS DÉCORATIF. Il commande la publication :
seule une fiche `verifiee_source_primaire` ou `source_secondaire` peut être
servie au public. Le reste reste en réserve, visible des seuls rédacteurs.
Une fiche rédigée par un modèle de langage entre au statut le plus bas et n'en
sort que par une main humaine — le moteur n'a aucun chemin pour l'en sortir
tout seul, et c'est délibéré.

AUCUNE FICHE N'EST ÉCRITE DANS CE FICHIER. Le corpus vit en base, alimenté
par `ingestion.py` depuis les sources du registre. Ce module tient la RÈGLE,
pas le contenu — un corpus figé dans le code serait périmé le jour de sa
première mise en ligne.
"""
import re
import unicodedata
from datetime import date, datetime, timezone

import sources as SRC

VERSION = "2026.08.22"

# ── Les sujets ────────────────────────────────────────────────────────────
# Quatre, et la distinction IA / SIA est volontaire : un système d'IA au sens
# du règlement européen n'est pas la même chose qu'une technologie d'IA. Le
# premier porte des obligations, la seconde non — et les confondre fait
# promettre une conformité à qui n'y est pas soumis, ou l'inverse.
SUJETS = {
    "cyber_industriel": {
        "nom": "Cybersécurité industrielle",
        "nom_en": "Industrial cybersecurity",
        "sous_titre": "IT · OT · IIoT",
        "quoi": "Les systèmes d'automatisation et de contrôle, leurs "
                "vulnérabilités avérées, les modes opératoires observés et "
                "les obligations qui s'y attachent.",
    },
    "ia": {
        "nom": "Intelligence artificielle",
        "nom_en": "Artificial intelligence",
        "sous_titre": "Modèles, matériel, usages",
        "quoi": "L'état de la technique : capacités mesurées, coûts, "
                "matériel, et ce que les évaluations publiques établissent "
                "réellement.",
    },
    "sia": {
        "nom": "Systèmes d'IA & conformité",
        "nom_en": "AI systems & compliance",
        "sous_titre": "AI Act · ISO/IEC 42001 · gouvernance",
        "quoi": "Le régime juridique des systèmes d'IA : classification, "
                "obligations par rôle, échéances, et la gouvernance qui les "
                "rend tenables.",
    },
    "datacenter": {
        "nom": "Centres de données",
        "nom_en": "Data centres",
        "sous_titre": "Énergie · eau · carbone",
        "quoi": "L'infrastructure de calcul et ses ressources : puissance, "
                "refroidissement, eau, carbone, implantation et les textes "
                "qui les encadrent.",
    },
}
ORDRE_SUJETS = ["cyber_industriel", "ia", "sia", "datacenter"]


# ── Les pays, et pourquoi une seule table ─────────────────────────────────
# DÉFAUT CONSTATÉ À L'ÉCRAN. Le menu « Pays » proposait « BE (2) », « DK (2) »,
# « FI (2) » — des codes ISO. Un lecteur qui cherche la France doit savoir
# qu'elle s'écrit FR, et parcourir une liste alphabétique de sigles pour la
# trouver entre ES et GB. Un filtre qu'on n'ose pas employer ne filtre rien.
#
# `owid` EST LA CLÉ D'APPARIEMENT, PAS UN LIBELLÉ. Les jeux de données de Our
# World in Data et d'Electricity Maps nomment leurs entités en anglais ; c'est
# ce nom-là qu'`ingestion.py` compare. Le séparer du nom affiché est ce qui
# permet de traduire l'un sans casser l'autre — et les tenir dans DEUX tables
# les aurait fait diverger au premier ajout de pays.
PAYS = {
    "FR": {"fr": "France",        "en": "France",         "owid": "France"},
    "DE": {"fr": "Allemagne",     "en": "Germany",        "owid": "Germany"},
    "IE": {"fr": "Irlande",       "en": "Ireland",        "owid": "Ireland"},
    "NL": {"fr": "Pays-Bas",      "en": "Netherlands",    "owid": "Netherlands"},
    "SE": {"fr": "Suède",         "en": "Sweden",         "owid": "Sweden"},
    "NO": {"fr": "Norvège",       "en": "Norway",         "owid": "Norway"},
    "FI": {"fr": "Finlande",      "en": "Finland",        "owid": "Finland"},
    "DK": {"fr": "Danemark",      "en": "Denmark",        "owid": "Denmark"},
    "ES": {"fr": "Espagne",       "en": "Spain",          "owid": "Spain"},
    "IT": {"fr": "Italie",        "en": "Italy",          "owid": "Italy"},
    "PL": {"fr": "Pologne",       "en": "Poland",         "owid": "Poland"},
    "BE": {"fr": "Belgique",      "en": "Belgium",        "owid": "Belgium"},
    "GB": {"fr": "Royaume-Uni",   "en": "United Kingdom", "owid": "United Kingdom"},
    "US": {"fr": "États-Unis",    "en": "United States",  "owid": "United States"},
}


def nom_pays(code):
    """Le nom d'un pays, ou son code s'il n'est pas au registre.

    UN CODE INCONNU SORT TEL QUEL. Le masquer ferait disparaître du menu un
    pays réellement présent dans le corpus : mieux vaut « ZZ » lisible qu'une
    fiche introuvable."""
    e = PAYS.get(str(code).upper())
    return {"fr": e["fr"], "en": e["en"]} if e else {"fr": code, "en": code}

# ── Le statut de vérification ─────────────────────────────────────────────
# `publiable` est la seule chose qui compte : elle décide de ce qui sort.
STATUTS = {
    "verifiee_source_primaire": {
        "nom": "Vérifiée à la source",
        "nom_en": "Verified against the primary source",
        "dit": "Le fait a été confronté au document d'origine, pas à un "
               "article qui en parle.",
        "dit_en": "The fact was checked against the original document, not against an article about it.",
        "publiable": True, "rang": 1,
    },
    "source_secondaire": {
        "nom": "Source secondaire",
        "nom_en": "Secondary source",
        "dit": "Le fait vient d'un intermédiaire fiable, sans que l'original "
               "ait été lu. Utilisable, à condition que ce soit écrit.",
        "dit_en": "The fact comes from a reliable intermediary, without the original having been read. Usable, provided that is stated.",
        "publiable": True, "rang": 2,
    },
    "a_verifier": {
        "nom": "À vérifier",
        "nom_en": "To be verified",
        "dit": "Retenue pour instruction, pas encore confrontée à sa source. "
               "Ne sort pas.",
        "dit_en": "Kept for review, not yet checked against its source. Does not go out.",
        "publiable": False, "rang": 3,
    },
    "redigee_par_ia": {
        "nom": "Rédigée par IA — non validée",
        "nom_en": "Written by AI — not validated",
        "dit": "Produite par un modèle de langage. Ne sort JAMAIS sans "
               "relecture humaine, et le moteur n'a aucun moyen de l'en "
               "sortir seul.",
        "dit_en": "Produced by a language model. NEVER goes out without human review, and the engine has no way of releasing it on its own.",
        "publiable": False, "rang": 4,
    },
    "refutee": {
        "nom": "Réfutée",
        "nom_en": "Refuted",
        "dit": "Confrontée et démentie. Conservée — une réfutation est une "
               "information, et l'effacer reviendrait à réécrire l'histoire "
               "de sa propre veille.",
        "dit_en": "Checked and disproved. Kept — a refutation is information, and erasing it would mean rewriting the history of one's own intelligence work.",
        "publiable": False, "rang": 5,
    },
}
ORDRE_STATUTS = ["verifiee_source_primaire", "source_secondaire", "a_verifier",
                 "redigee_par_ia", "refutee"]

# ── D'où vient la LECTURE ─────────────────────────────────────────────────
# Le champ le plus important de ce modèle après la source. Une lecture
# critique peut venir de trois endroits qui n'engagent pas la même chose, et
# les afficher pareillement serait exactement la confusion que ce site existe
# pour ne pas commettre.
LECTURES = {
    "regle": {
        "nom": "Lecture dérivée par règles",
        "nom_en": "Reading derived by published rules",
        "dit": "Composée automatiquement à partir des seules données de la "
               "source, par des règles écrites et publiées. Reproductible : "
               "deux passages sur la même donnée rendent le même texte. "
               "Aucun modèle de langage n'intervient.",
        "dit_en": "Composed automatically from the source's data alone, by written and published rules. Reproducible: two passes over the same data produce the same text. No language model is involved.",
        "engage_le_cabinet": False,
        "publiable": True,
    },
    "redaction": {
        "nom": "Lecture rédigée et signée",
        "nom_en": "Reading written and signed",
        "dit": "Écrite par un analyste du cabinet, datée et signée. C'est un "
               "AVIS — argumenté, révisable, et qui engage celui qui le "
               "signe.",
        "dit_en": "Written by an analyst of the firm, dated and signed. It is an OPINION — argued, open to revision, and binding on whoever signs it.",
        "engage_le_cabinet": True,
        "publiable": True,
    },
    "modele": {
        "nom": "Brouillon de modèle — non validé",
        "nom_en": "Model draft — not validated",
        "dit": "Proposé par un modèle de langage. Sert de point de départ à "
               "un analyste, jamais de contenu. Ne sort pas.",
        "dit_en": "Suggested by a language model. Serves an analyst as a starting point, never as content. Does not go out.",
        "engage_le_cabinet": False,
        "publiable": False,
    },
}
ORDRE_LECTURES = ["regle", "redaction", "modele"]


# ── La portée d'une information ───────────────────────────────────────────
# Un rang, pas une note. Un site qui afficherait « impact 8,4/10 » emprunterait
# le vocabulaire de la mesure pour désigner un jugement.
IMPACTS = {
    "rupture": {
        "nom": "Rupture",
        "nom_en": "Break",
        "dit": "Change ce qu'il est possible ou obligatoire de faire. Se "
               "traite en comité, pas en veille.",
        "dit_en": "Changes what it is possible or mandatory to do. Handled in committee, not in a watch list.",
        "rang": 1,
    },
    "structurant": {
        "nom": "Structurant",
        "nom_en": "Structural",
        "dit": "Déplace un arbitrage ou une trajectoire déjà engagée.",
        "dit_en": "Moves a trade-off or a course of action already under way.",
        "rang": 2,
    },
    "incremental": {
        "nom": "Incrémental",
        "nom_en": "Incremental",
        "dit": "S'inscrit dans une tendance connue sans l'infléchir.",
        "dit_en": "Falls within a known trend without bending it.",
        "rang": 3,
    },
    "signal_faible": {
        "nom": "Signal faible",
        "nom_en": "Weak signal",
        "dit": "Isolé, mal établi, mais qui mérite d'être daté pour qu'on "
               "puisse y revenir. Sa fragilité est la donnée principale.",
        "dit_en": "Isolated, poorly established, but worth dating so it can be revisited. Its fragility is the main datum.",
        "rang": 4,
    },
}
ORDRE_IMPACTS = ["rupture", "structurant", "incremental", "signal_faible"]

# ── L'horizon ─────────────────────────────────────────────────────────────
HORIZONS = {
    "constate": {"nom": "Constaté", "nom_en": "Established",
                 "dit": "Établi à la date indiquée.",
                 "dit_en": "Established as at the date shown."},
    "engage": {"nom": "Engagé", "nom_en": "Committed",
               "dit": "Décidé, daté, pas encore en vigueur ou pas encore "
                      "déployé.",
               "dit_en": "Decided, dated, not yet in force or not yet "
                         "deployed."},
    "projete": {"nom": "Projeté", "nom_en": "Projected",
                "dit": "Projection à horizon 2030. C'est une HYPOTHÈSE, "
                       "portée par qui la publie — jamais un fait.",
                "dit_en": "A projection to 2030. It is a HYPOTHESIS, carried "
                          "by whoever publishes it — never a fact."},
}
ORDRE_HORIZONS = ["constate", "engage", "projete"]

_CHAMPS_OBLIGATOIRES = ("id", "titre", "chapeau", "lecture", "lecture_nature",
                        "portee", "incertitude", "sujet", "date_fait",
                        "source_cle", "source_url", "statut", "impact",
                        "horizon")

_ID = re.compile(r"^[a-z0-9][a-z0-9-]{2,79}$")
_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _texte(x):
    return " ".join(str(x or "").split())


def sujets():
    return [dict(SUJETS[c], cle=c) for c in ORDRE_SUJETS]


def statuts():
    return [dict(STATUTS[c], cle=c) for c in ORDRE_STATUTS]


def lectures():
    return [dict(LECTURES[c], cle=c) for c in ORDRE_LECTURES]


def impacts():
    return [dict(IMPACTS[c], cle=c) for c in ORDRE_IMPACTS]


def horizons():
    return [dict(HORIZONS[c], cle=c) for c in ORDRE_HORIZONS]


def valider(fiche):
    """Dit si une fiche a le droit d'exister, et NOMME chaque manque.

    Rend une liste de fautes plutôt qu'une exception : un rédacteur doit voir
    tout ce qui manque d'un coup, pas le découvrir une erreur à la fois.
    """
    f = dict(fiche or {})
    fautes = []

    for champ in _CHAMPS_OBLIGATOIRES:
        if not _texte(f.get(champ)):
            fautes.append("champ obligatoire vide : %s" % champ)

    if f.get("id") and not _ID.match(str(f["id"])):
        fautes.append("identifiant non conforme (minuscules, chiffres et "
                      "tirets, 3 à 80 signes) : %r" % f["id"])

    if f.get("sujet") and f["sujet"] not in SUJETS:
        fautes.append("sujet inconnu : %r" % f["sujet"])
    if f.get("statut") and f["statut"] not in STATUTS:
        fautes.append("statut inconnu : %r" % f["statut"])
    if f.get("impact") and f["impact"] not in IMPACTS:
        fautes.append("portée inconnue : %r" % f["impact"])
    if f.get("horizon") and f["horizon"] not in HORIZONS:
        fautes.append("horizon inconnu : %r" % f["horizon"])
    if f.get("lecture_nature") and f["lecture_nature"] not in LECTURES:
        fautes.append("nature de lecture inconnue : %r" % f["lecture_nature"])
    # UNE LECTURE DE MODÈLE NE PEUT PAS ÊTRE PORTÉE PAR UNE FICHE PUBLIABLE.
    # Les deux champs sont indépendants ; sans ce contrôle croisé, il
    # suffirait d'oublier l'un pour publier l'autre.
    if (f.get("lecture_nature") == "modele"
            and STATUTS.get(f.get("statut"), {}).get("publiable")):
        fautes.append("une lecture de modèle de langage ne peut pas porter un "
                      "statut publiable : relisez-la et signez-la, ou "
                      "laissez-la en réserve")
    # UNE LECTURE SIGNÉE DOIT NOMMER SON SIGNATAIRE.
    if f.get("lecture_nature") == "redaction" and not _texte(f.get("signe_par")):
        fautes.append("une lecture rédigée doit être signée (champ "
                      "« signe_par ») : un avis anonyme n'engage personne")

    # LA SOURCE DOIT ÊTRE AU REGISTRE. C'est ce qui empêche d'inventer une
    # provenance : on ne peut citer que ce qui a été admis et sondé.
    if f.get("source_cle") and f["source_cle"] not in SRC.SOURCES:
        fautes.append("source hors registre : %r — une fiche ne peut citer "
                      "qu'une source admise" % f["source_cle"])
    if f.get("source_url") and not str(f["source_url"]).startswith("https://"):
        fautes.append("adresse de source non chiffrée")

    if f.get("date_fait") and not _ISO.match(str(f["date_fait"])):
        fautes.append("date du fait mal formée (AAAA-MM-JJ) : %r" % f["date_fait"])
    else:
        try:
            d = date.fromisoformat(str(f.get("date_fait")))
            if d > date.today():
                fautes.append("date du fait dans l'avenir : %s" % d)
        except (TypeError, ValueError):
            pass

    # LES TROIS TEXTES QUI FONT LA VALEUR DU SITE ont une longueur minimale.
    # Une « lecture critique » de six mots est un slogan ; l'exiger courte
    # produirait exactement ce qu'on veut éviter.
    for champ, mini, quoi in (("lecture", 80, "la lecture critique"),
                              ("portee", 60, "ce que cela change"),
                              ("incertitude", 40, "ce qu'on ne sait pas")):
        v = _texte(f.get(champ))
        if v and len(v) < mini:
            fautes.append("%s est trop courte (%d signes, minimum %d) : ce "
                          "champ porte l'essentiel de la valeur du site"
                          % (quoi, len(v), mini))

    # UNE PROJECTION N'EST PAS UN CONSTAT. Si l'horizon est « projeté », la
    # fiche doit dire QUI projette — sinon elle présente une hypothèse comme
    # un fait, ce qui est la faute la plus coûteuse de ce site.
    if f.get("horizon") == "projete" and not _texte(f.get("projette_qui")):
        fautes.append("une projection doit nommer qui la porte "
                      "(champ « projette_qui ») : sans cela, une hypothèse "
                      "se lit comme un fait établi")

    # ── UNE DATE INVENTÉE DOIT SE DÉCLARER COMME TELLE ────────────────────
    # DÉFAUT CONSTATÉ EN SERVICE, sur les dix fiches OWASP. La source publie
    # une ÉDITION datée, pas des entrées datées ; le collecteur leur a donc
    # posé le 1er janvier — une convention de classement, et il l'écrivait
    # honnêtement dans l'incertitude de chaque fiche.
    #
    # SAUF QUE LA PROSE NE PROTÈGE RIEN. Le croisement, lui, ne lit pas
    # l'incertitude : il a vu dix fiches à la même date, et les a rapprochées
    # « à moins de 45 jours ». Le site reliait donc des fiches par une valeur
    # QU'IL AVAIT LUI-MÊME FABRIQUÉE, en affichant sous le rapprochement que
    # la date était « la seule chose qu'elles aient en commun ». C'était vrai,
    # et c'est bien ce qui était grave.
    #
    # La convention devient donc un CHAMP, que le collecteur qui l'invente
    # déclare. Aucune règle ne la devine — deviner rouvrirait la même faute
    # sous une autre forme.
    if f.get("date_convention") and not _texte(f.get("date_convention_dit")):
        fautes.append("une date de convention doit dire de quoi elle tient "
                      "lieu (champ « date_convention_dit ») : sans cela, une "
                      "date fabriquée se lit comme une observation")

    return fautes


def normaliser(fiche):
    """Complète une fiche valide de ce qui se DÉDUIT, et de rien d'autre."""
    fautes = valider(fiche)
    if fautes:
        return {"ok": False, "erreur": "fiche_invalide", "fautes": fautes}
    f = dict(fiche)
    s = SRC.SOURCES[f["source_cle"]]
    st = STATUTS[f["statut"]]
    f["source"] = {
        "cle": f["source_cle"], "nom": s["nom"], "editeur": s["editeur"],
        "nature": s["nature"], "nature_nom": SRC.NATURES[s["nature"]]["nom"],
        "licence": s["licence"], "url": f["source_url"],
        "url_editeur": s["url_humaine"],
    }
    f["statut_nom"] = st["nom"]
    f["statut_dit"] = st["dit"]
    f["publiable"] = bool(st["publiable"])
    f["sujet_nom"] = SUJETS[f["sujet"]]["nom"]
    f["impact_nom"] = IMPACTS[f["impact"]]["nom"]
    f["impact_rang"] = IMPACTS[f["impact"]]["rang"]
    f["horizon_nom"] = HORIZONS[f["horizon"]]["nom"]
    f["horizon_dit"] = HORIZONS[f["horizon"]]["dit"]
    # « CONSTATÉ » DIT « ÉTABLI À LA DATE INDIQUÉE » — et c'est exactement la
    # promesse qu'une date de convention ne tient pas. Aucun autre horizon ne
    # conviendrait pour autant : un risque reconnu par OWASP EST établi, il
    # n'est ni « engagé » ni « projeté ». Ce n'est donc pas l'horizon qu'il
    # faut changer, c'est sa phrase — là où la promesse est faite.
    if f.get("date_convention"):
        f["horizon_dit"] = ("Établi — mais PAS à la date affichée : %s"
                            % _texte(f["date_convention_dit"]))
    ln = LECTURES[f["lecture_nature"]]
    f["lecture_nom"] = ln["nom"]
    f["lecture_dit"] = ln["dit"]
    f["lecture_engage"] = bool(ln["engage_le_cabinet"])
    f.setdefault("pays", [])
    f.setdefault("technologies", [])
    f.setdefault("signe_par", "CONSEILPREV")
    f.setdefault("lecture_datee_le", f["date_fait"])
    return {"ok": True, "fiche": f}


def publiables(fiches):
    """Ce qui sort. Le filtre est ici et NULLE PART AILLEURS.

    Une seule porte, pour qu'on puisse la lire en entier. Répartie sur les
    gabarits, la règle deviendrait invérifiable — et c'est exactement le
    genre d'endroit où une fiche non validée finit à l'écran.
    """
    return [f for f in fiches
            if STATUTS.get(f.get("statut"), {}).get("publiable")
            and LECTURES.get(f.get("lecture_nature"), {}).get("publiable")]


def filtrer(fiches, sujet=None, pays=None, techno=None, depuis=None,
            jusqua=None, impact=None, horizon=None, statut=None,
            inclure_non_publiables=False):
    """Les filtres du site. Aucun ne peut faire sortir une fiche non publiable
    sauf demande EXPLICITE — réservée à l'espace de rédaction."""
    out = list(fiches)
    if not inclure_non_publiables:
        out = publiables(out)
    if sujet:
        out = [f for f in out if f.get("sujet") == sujet]
    if pays:
        p = str(pays).upper()
        out = [f for f in out if p in [str(x).upper() for x in f.get("pays", [])]]
    if techno:
        t = _sansaccent(techno)
        out = [f for f in out
               if any(t in _sansaccent(x) for x in f.get("technologies", []))]
    if depuis:
        out = [f for f in out if str(f.get("date_fait", "")) >= str(depuis)]
    if jusqua:
        out = [f for f in out if str(f.get("date_fait", "")) <= str(jusqua)]
    if impact:
        out = [f for f in out if f.get("impact") == impact]
    if horizon:
        out = [f for f in out if f.get("horizon") == horizon]
    if statut:
        out = [f for f in out if f.get("statut") == statut]
    # LE PLUS IMPORTANT D'ABORD, PUIS LE PLUS RÉCENT. Trier d'abord par date
    # ferait descendre une rupture sous trois brèves du lendemain.
    out.sort(key=lambda f: (IMPACTS.get(f.get("impact"), {}).get("rang", 9),
                            _inverse(f.get("date_fait", ""))))
    return out


def _inverse(d):
    """Clef de tri décroissant sur une date ISO, sans dépendre du type."""
    return tuple(-int(x) for x in str(d).split("-")) if _ISO.match(str(d)) else (0,)


def _sansaccent(x):
    s = unicodedata.normalize("NFD", str(x or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def chercher(fiches, q):
    """Recherche plein texte, sans accent ni casse.

    Elle porte sur ce que le lecteur voit — titre, chapeau, lecture, portée,
    réserve, technologies — et PAS sur les champs internes. Chercher dans un
    identifiant technique rendrait des résultats qu'aucun mot de la page ne
    justifie, et le lecteur croirait le moteur détraqué.

    Tous les mots doivent être présents : une recherche à deux mots qui rend
    tout ce qui contient l'un OU l'autre ne filtre rien.
    """
    mots = [_sansaccent(m) for m in str(q or "").split() if len(m) > 1]
    if not mots:
        return list(fiches)
    out = []
    for f in fiches:
        foin = _sansaccent(" ".join([
            str(f.get("titre", "")), str(f.get("chapeau", "")),
            str(f.get("lecture", "")), str(f.get("portee", "")),
            str(f.get("incertitude", "")),
            " ".join(str(x) for x in (f.get("technologies") or [])),
            str((f.get("source") or {}).get("nom", "")),
        ]))
        if all(m in foin for m in mots):
            out.append(f)
    return out


def facettes(fiches, **filtres):
    """Ce que les filtres peuvent réellement proposer — COMPTÉ SUR LES FICHES
    TROUVÉES, et non sur le corpus entier.

    DÉFAUT MESURÉ À L'ÉCRAN, ET C'ÉTAIT LE PIRE GENRE. Les menus étaient
    calculés sur tout le corpus, quels que soient les filtres en cours.
    Choisir « Systèmes d'IA » laissait donc le menu Pays proposer quatorze
    pays avec leurs comptes — alors qu'AUCUNE des vingt-huit fiches de cette
    rubrique ne porte de pays. Le lecteur cliquait « DE (2) », obtenait un
    écran vide, et n'avait aucun moyen de savoir si le site était cassé ou si
    le corpus était pauvre. Un menu qui promet des résultats inexistants est
    pire qu'un menu absent.

    CHAQUE AXE EST COMPTÉ HORS DE SON PROPRE FILTRE. C'est la règle d'une
    recherche à facettes, et elle n'est pas un raffinement : sans elle,
    choisir un pays réduirait le menu Pays à ce seul pays, et l'on ne pourrait
    plus en changer sans tout remettre à zéro. Le menu Pays voit donc l'effet
    du sujet, de la technologie et des dates — mais pas le sien.

    Jamais une liste écrite à la main : une facette qui propose un pays sans
    aucune fiche rend un écran vide, et le lecteur croit le site cassé.
    """
    def _garde(sauf):
        """Les fiches retenues par tous les filtres SAUF celui de cet axe."""
        aut = {k: v for k, v in filtres.items() if k != sauf and v}
        q = aut.pop("q", None)
        out = filtrer(fiches, **aut)
        return chercher(out, q) if q else out

    def _compte(cle, sauf):
        c = {}
        for f in _garde(sauf):
            for v in (f.get(cle) or []):
                c[str(v)] = c.get(str(v), 0) + 1
        return c

    pub = _garde(None)          # tous les filtres appliqués : le fil affiché
    par_sujet = {}
    for f in _garde("sujet"):
        par_sujet[f.get("sujet")] = par_sujet.get(f.get("sujet"), 0) + 1
    annees = sorted({str(f.get("date_fait", ""))[:4] for f in pub if f.get("date_fait")},
                    reverse=True)
    par_impact = _garde("impact")
    par_horizon = _garde("horizon")
    return {
        "sujets": [dict(SUJETS[c], cle=c, n=par_sujet.get(c, 0))
                   for c in ORDRE_SUJETS if par_sujet.get(c)],
        # LE PAYS PORTE SON NOM, dans les deux langues. Un menu de codes ISO
        # oblige le lecteur à savoir que la France s'écrit FR et à la chercher
        # entre ES et GB.
        "pays": sorted(({"cle": k, "n": v,
                         "nom": nom_pays(k)["fr"], "nom_en": nom_pays(k)["en"]}
                        for k, v in _compte("pays", "pays").items()),
                       key=lambda x: (-x["n"], x["nom"])),
        "technologies": sorted(({"cle": k, "n": v}
                                for k, v in _compte("technologies", "techno").items()),
                               key=lambda x: (-x["n"], x["cle"])),
        "impacts": [dict(IMPACTS[c], cle=c,
                         n=sum(1 for f in par_impact if f.get("impact") == c))
                    for c in ORDRE_IMPACTS
                    if any(f.get("impact") == c for f in par_impact)],
        "horizons": [dict(HORIZONS[c], cle=c,
                          n=sum(1 for f in par_horizon if f.get("horizon") == c))
                     for c in ORDRE_HORIZONS
                     if any(f.get("horizon") == c for f in par_horizon)],
        "annees": annees,
        # CE QUE LES MENUS DÉCRIVENT : le nombre de fiches trouvées, pas la
        # taille du corpus. Les deux étaient confondus, et c'est ce qui rendait
        # l'écart invisible.
        "total_trouve": len(pub),
        "total_publiable": len(publiables(fiches)),
        "total_corpus": len(fiches),
        "filtre": {k: v for k, v in filtres.items() if v},
    }


def langues(fiches=None):
    """CE QUE LA BASCULE FR/EN TRADUIT, ET CE QU'ELLE NE TRADUIT PAS.

    UNE INTERFACE ANGLAISE POSÉE SUR UN CORPUS FRANÇAIS EST UN MENSONGE PAR
    OMISSION. Le lecteur qui bascule en anglais et voit des paragraphes
    français en conclut que le site est cassé — ou pire, il ne les lit pas et
    croit avoir tout vu.

    CE QUI A CHANGÉ. Cette fonction disait « les analyses sont en français, et
    voilà pourquoi ». La raison était juste : la lecture, la portée et
    l'incertitude sont DÉRIVÉES par des gabarits, et il n'en existait qu'en
    français. Le site annonçait aussi le remède — « des gabarits anglais, un
    vrai travail, pas un réglage ». Ils sont écrits : `gabarits.py` porte les
    deux colonnes côte à côte. Cette fonction ne raconte donc plus une
    absence, elle MESURE une couverture.

    ELLE NE SUPPOSE TOUJOURS RIEN. Une fiche est comptée traduite si elle
    porte RÉELLEMENT ses trois champs dérivés en anglais. Un collecteur
    ajouté demain sans gabarits anglais fera baisser ce nombre tout seul, et
    l'écran le dira — c'est le seul mécanisme qui empêche la promesse de
    survivre à sa propre fausseté.

    LA DISTINCTION DE FOND N'A PAS BOUGÉ :

      · Le TITRE et le CHAPEAU sont MIXTES. Ce que la source publie reste
        dans sa langue — MITRE, CISA et OWASP publient en anglais —, ce que
        ce site y ajoute est traduit. Un titre n'est donc jamais « traduit »
        en entier, et c'est voulu : recomposer le nom d'une technique du
        référentiel reviendrait à en inventer un second.
      · La LECTURE, la PORTÉE et l'INCERTITUDE sont entièrement de ce site :
        elles sont traduites, ou elles ne le sont pas, et le compte le dit.
    """
    pub = publiables(fiches or [])
    avec_analyse = [f for f in pub if _texte(f.get("lecture"))]
    traduites = [f for f in avec_analyse if _traduite(f)]
    manquantes = [f for f in avec_analyse if not _traduite(f)]
    # PAR SOURCE, parce que c'est par là qu'on répare : une source manquante
    # désigne le collecteur dont les gabarits anglais restent à écrire.
    par_source = {}
    for f in manquantes:
        c = (f.get("source") or {}).get("cle") or f.get("source_cle") or "?"
        par_source[c] = par_source.get(c, 0) + 1
    n, t = len(traduites), len(avec_analyse)
    return {
        "interface": ["fr", "en"],
        "analyses": n,
        "analyses_traduites": n,
        "analyses_total": t,
        "analyses_manquantes": t - n,
        "manquantes_par_source": dict(sorted(par_source.items())),
        "complet": n == t,
        "total": len(pub),
        # LES DEUX PHRASES SONT COMPOSÉES DEPUIS LE MÊME COMPTE. Écrire « tout
        # est traduit » en dur laisserait la phrase vraie le jour où elle
        # cesserait de l'être.
        "dit_fr": (
            "Les %d analyses du corpus sont dérivées par des gabarits publiés, "
            "et elles existent en français comme en anglais : ce site n'emploie "
            "aucune traduction automatique, chaque phrase des deux colonnes a "
            "été écrite. Les titres et les chapeaux restent mixtes — ce que la "
            "source publie garde sa langue, ce que ce site y ajoute est traduit."
            % t
            if n == t else
            "%d des %d analyses du corpus existent en anglais. Les %d autres "
            "n'ont pas encore de gabarit anglais et restent en français : %s. "
            "Ce site n'emploie aucune traduction automatique — une analyse non "
            "traduite s'affiche donc telle quelle, signalée, plutôt que passée "
            "à la machine."
            % (n, t, t - n,
               " ; ".join("%s (%d)" % (c, k) for c, k in sorted(par_source.items()))
               or "source non identifiée")),
        "dit_en": (
            "The %d critical readings in this corpus are derived from published "
            "rule templates, and they exist in French and in English alike: this "
            "site uses no machine translation anywhere, and every sentence in "
            "both columns was written. Titles and summaries stay mixed — what "
            "the source publishes keeps its own language, what this site adds "
            "is translated."
            % t
            if n == t else
            "%d of the %d critical readings in this corpus exist in English. "
            "The other %d have no English template yet and remain in French: "
            "%s. This site uses no machine translation — an untranslated "
            "reading is therefore shown as it is, flagged, rather than run "
            "through a machine."
            % (n, t, t - n,
               " ; ".join("%s (%d)" % (c, k) for c, k in sorted(par_source.items()))
               or "source not identified")),
    }


#: Les champs qui sont ENTIÈREMENT de ce site, donc entièrement traduisibles.
#: Le titre et le chapeau n'y sont pas : ils portent du texte de la source,
#: qu'on ne recompose pas.
CHAMPS_TRADUITS = ("lecture", "portee", "incertitude")


def _traduite(f):
    """Une fiche est traduite quand ses TROIS champs dérivés le sont.

    DEUX SUR TROIS NE COMPTE PAS. Une fiche dont la lecture serait anglaise et
    l'incertitude française est pire qu'une fiche entièrement française : le
    lecteur, ayant lu deux paragraphes dans sa langue, prend le troisième pour
    une citation et ne le lit pas."""
    return all(_texte(f.get(c + "_en")) for c in CHAMPS_TRADUITS)


def dans(f, langue):
    """La fiche vue dans une langue — les champs traduits remplacés quand ils
    existent, et un drapeau qui dit ce qui ne l'était pas.

    LE REPLI EST LE FRANÇAIS, ET IL SE DIT. Servir un champ vide serait pire
    que servir du français : le lecteur croirait la fiche incomplète."""
    if langue != "en":
        return dict(f, langue_analyses="fr", analyses_traduites=True)
    out = dict(f)
    for c in CHAMPS_TRADUITS + ("titre", "chapeau"):
        v = _texte(f.get(c + "_en"))
        if v:
            out[c] = v
    # LES LIBELLÉS DU RÉFÉRENTIEL AUSSI. Ils sont posés par `normaliser()`
    # depuis les tables ci-dessus, qui portent leurs deux colonnes. Les
    # oublier laissait « Reading — Lecture dérivée par règles » en tête du
    # document exporté : le pire des mélanges, parce qu'il se lit comme une
    # citation et qu'il n'en est pas une.
    for champ, table, cle in (
            ("statut", STATUTS, "statut"), ("sujet", SUJETS, "sujet"),
            ("impact", IMPACTS, "impact"), ("horizon", HORIZONS, "horizon"),
            ("lecture", LECTURES, "lecture_nature")):
        e = table.get(f.get(cle))
        if not e:
            continue
        if e.get("nom_en"):
            out[champ + "_nom"] = e["nom_en"]
        if e.get("dit_en"):
            out[champ + "_dit"] = e["dit_en"]
    # LA RÉSERVE DE DATE EST RECOMPOSÉE, pas traduite : `normaliser()` colle
    # une phrase française devant le motif. On la refait dans la langue.
    if f.get("date_convention"):
        # LE MOTIF LUI-MÊME EST TRADUIT quand le collecteur l'a écrit dans les
        # deux langues ; sinon on garde le français plutôt qu'un blanc.
        motif = _texte(f.get("date_convention_dit_en")) \
            or _texte(f.get("date_convention_dit"))
        out["date_convention_dit"] = motif
        out["horizon_dit"] = ("Established — but NOT on the date shown: %s"
                              % motif)
    # LA LICENCE AUSSI : elle est affichée sous chaque fiche et dans chaque
    # document emporté. « réutilisation libre avec citation » sous un texte
    # anglais est le genre de reste qui fait douter du reste.
    src = out.get("source")
    if isinstance(src, dict):
        e = SRC.SOURCES.get(src.get("cle")) or {}
        if e.get("licence_en"):
            out["source"] = dict(src, licence=e["licence_en"])
    out["langue_analyses"] = "en" if _traduite(f) else "fr"
    out["analyses_traduites"] = _traduite(f)
    return out


def sante(fiches=None):
    fiches = list(fiches or [])
    par_statut = {c: sum(1 for f in fiches if f.get("statut") == c)
                  for c in ORDRE_STATUTS}
    invalides = []
    for f in fiches:
        if valider(f):
            invalides.append(f.get("id") or "?")
    return {
        "module": "veille", "version": VERSION,
        "sujets": len(SUJETS), "statuts": len(STATUTS),
        "corpus": len(fiches),
        "publiables": len(publiables(fiches)),
        "par_statut": par_statut,
        "fiches_invalides": sorted(invalides),
        "par_lecture": {c: sum(1 for f in fiches
                               if f.get("lecture_nature") == c)
                        for c in ORDRE_LECTURES},
        "sources_admises": len(SRC.SOURCES),
        "portee": "Tient la RÈGLE éditoriale, jamais le contenu. Une fiche "
                  "sans source admise, sans lecture critique ou sans "
                  "incertitude déclarée est refusée.",
    }


def _verifier():
    if set(ORDRE_SUJETS) != set(SUJETS):
        raise RuntimeError("veille : l'ordre des sujets ne les couvre pas")
    if set(ORDRE_STATUTS) != set(STATUTS):
        raise RuntimeError("veille : l'ordre des statuts ne les couvre pas")
    if set(ORDRE_IMPACTS) != set(IMPACTS):
        raise RuntimeError("veille : l'ordre des portées ne les couvre pas")
    if set(ORDRE_HORIZONS) != set(HORIZONS):
        raise RuntimeError("veille : l'ordre des horizons ne les couvre pas")

    # LA GARDE QUI COMPTE LE PLUS DANS TOUT CE FICHIER. Si une fiche rédigée
    # par un modèle devenait publiable, tout l'édifice tomberait — et il
    # tomberait en silence, parce que rien à l'écran ne distingue une bonne
    # fiche d'une fiche plausible.
    if STATUTS["redigee_par_ia"]["publiable"]:
        raise RuntimeError(
            "veille : une fiche rédigée par un modèle de langage est devenue "
            "publiable sans relecture — c'est la seule faute que ce site ne "
            "peut pas se permettre")
    if STATUTS["refutee"]["publiable"] or STATUTS["a_verifier"]["publiable"]:
        raise RuntimeError("veille : un statut non validé est devenu publiable")
    if not STATUTS["verifiee_source_primaire"]["publiable"]:
        raise RuntimeError("veille : plus aucune fiche ne peut être publiée")

    if set(ORDRE_LECTURES) != set(LECTURES):
        raise RuntimeError("veille : l'ordre des lectures ne les couvre pas")
    if LECTURES["modele"]["publiable"]:
        raise RuntimeError(
            "veille : une lecture de modèle de langage est devenue publiable — "
            "c'est la porte par laquelle un avis fabriqué passerait pour une "
            "analyse du cabinet")
    if LECTURES["regle"]["engage_le_cabinet"]:
        raise RuntimeError(
            "veille : une lecture dérivée par règles ne doit pas être "
            "présentée comme engageant le cabinet")

    rangs = sorted(IMPACTS[c]["rang"] for c in IMPACTS)
    if rangs != list(range(1, len(IMPACTS) + 1)):
        raise RuntimeError("veille : les rangs de portée ne forment pas une suite")


_verifier()
