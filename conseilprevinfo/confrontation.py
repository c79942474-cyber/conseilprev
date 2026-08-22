"""LA CONFRONTATION — votre document en regard du corpus.

CE QUE CE MODULE FAIT, ET CE QU'IL NE FERA JAMAIS.

Il compare le VOCABULAIRE d'un document que vous déposez à celui du corpus.
Il ne le lit pas. Il ne le comprend pas. Il ne le juge pas. Il ne certifie
aucune conformité. La distinction n'est pas une précaution de style : elle
commande ce qu'on a le droit de faire du résultat.

CE QUE CE MODULE VOULAIT FAIRE, ET CE QUE LA MESURE A IMPOSÉ.

L'intention était de mettre en avant l'ABSENCE : savoir que votre politique
parle de « segmentation » comme quatorze fiches ne vous apprend rien, vous le
saviez en l'écrivant ; savoir qu'elle ne nomme jamais un terme qui revient
dans le corpus serait un point à instruire.

MESURÉ, CELA NE MARCHE PAS SUR CE CORPUS — et il a fallu trois corrections
pour s'en convaincre plutôt qu'une pour s'en persuader :

  · d'abord les questions portaient sur « gco2e » et « nucleaire », parce que
    quatorze fiches issues d'un même gabarit gonflaient les comptes ;
  · puis sur « malware » et « targeted », parce qu'on comparait un document
    français aux titres anglais de MITRE ;
  · puis sur « votre », « point » et « seulement » — c'est-à-dire sur MA
    PROPRE PROSE, uniforme d'une fiche à l'autre par construction, puisque ce
    site DÉRIVE ses lectures par règles au lieu de les rédiger.

La quatrième cause n'est pas corrigeable : un corpus dont les analyses sont
composées par règles n'a pas de vocabulaire varié à opposer. L'absence n'est
donc PAS proposée par défaut. Le module la calcule, mesure si elle tient
debout, et le dit quand elle ne tient pas — au lieu de servir une liste
plausible que personne n'aurait vérifiée.

CE QUI MARCHE, EN REVANCHE, CE SONT LES PONTS. « Votre document emploie
périmètre, segmentation, architecture, bureautique — voici les fiches qui en
traitent » est modeste, vrai, et immédiatement utile : c'est une entrée dans
le corpus par le vocabulaire du lecteur.

L'ABSENCE D'UN MOT N'EST PAS L'ABSENCE DE LA CHOSE — et c'est la réserve
capitale. Un document peut traiter parfaitement d'un sujet en l'appelant
autrement : « cloisonnement » pour « segmentation », « journalisation » pour
« traçabilité ». Le résultat rendu ici est une LISTE DE QUESTIONS À POSER À
SON DOCUMENT, jamais une liste de manques constatés. Chaque écran le dit.

CE QUE DEVIENT LE DOCUMENT. Rien. Il est lu en mémoire, confronté, et jeté
avec la requête. Aucune copie n'est écrite sur disque, aucun extrait n'est
conservé, et le résultat rendu ne contient pas le texte déposé — seulement
des termes et des comptes. Un cabinet qui garderait les documents de ses
prospects pour « améliorer son service » ferait exactement ce qu'un
industriel redoute en confiant son schéma d'architecture.

AUCUN MODÈLE DE LANGAGE. Comme partout ici : deux confrontations du même
document sur le même corpus rendent le même résultat.
"""
import io
import re
import unicodedata
import zipfile
from collections import Counter

import croisement as X
import veille as V

VERSION = "2026.08.22"

# Un document plus gros n'est pas refusé pour économiser la machine : au-delà,
# le vocabulaire d'un dossier entier se confond avec celui de la langue, et la
# confrontation ne distingue plus rien.
OCTETS_MAX = 4 * 1024 * 1024
MOTS_MIN = 120

FORMATS = {
    ".txt": "texte brut",
    ".md": "texte brut (Markdown)",
    ".docx": "document Word (XML, lu sans bibliothèque tierce)",
    ".pdf": "PDF (lu si la bibliothèque pypdf est disponible)",
}

# Le seuil au-delà duquel un terme du corpus mérite d'être confronté. Sous
# trois fiches, c'est un mot de circonstance, pas un thème.
MINI_FICHES = 3

# ── DEUX FILTRES SANS LESQUELS LA CONFRONTATION EST UN BRUIT ──────────────
# MESURÉ SUR LE CORPUS RÉEL, avant mise en ligne. Confrontée à une politique
# de cybersécurité industrielle, la première version demandait sérieusement au
# lecteur si son document traitait de « gco2e », « nucleaire » et « filiere ».
#
# DEUX CAUSES DISTINCTES, ET IL FALLAIT CORRIGER LES DEUX.
#
#   1. LES FICHES GABARIT GONFLENT LES COMPTES. Les quatorze fiches de mix
#      électrique sont quatorze exemplaires d'une même phrase, à un pays près.
#      Un terme qui y figure paraît donc porté par quatorze fiches alors qu'il
#      n'est porté que par UN gabarit. Le remède : ne retenir que les termes
#      portés par PLUSIEURS SOURCES. Ce qu'une seule source répète est son
#      vocabulaire à elle, pas un thème du corpus.
#
#   2. LE CORPUS COUVRE QUATRE SUJETS, LE DOCUMENT UN SEUL. Confronter une
#      politique OT au carbone des centres de données ne produit pas une
#      question, mais une incongruité — et trois incongruités suffisent à ce
#      qu'on cesse de lire les suivantes. Le sujet est donc DÉDUIT du document
#      lui-même, affiché, et le lecteur peut le refuser.
MINI_SOURCES = 2
# LE SUJET SE RECONNAÎT PAR ÉCART, PAS PAR SEUIL ABSOLU.
# Premier réglage posé sans mesurer : 18 % de recouvrement exigé. Mesuré
# ensuite, le recouvrement réel plafonne à 2 % — le vocabulaire d'une rubrique
# entière compte des centaines de termes, celui d'un document quelques
# centaines aussi, et l'intersection reste faible par construction. Aucun
# document n'aurait jamais franchi ce seuil.
# On compare donc les rubriques ENTRE ELLES : la première l'emporte si elle
# devance nettement la deuxième. À égalité, on ne devine pas.
AVANCE_SUJET_MIN = 1.4

# ── LE PLAFOND : CE QUI EST PARTOUT N'EST NULLE PART ──────────────────────
# TROISIÈME FORME DU MÊME DÉFAUT, et la plus embarrassante : après avoir
# écarté le vocabulaire d'un gabarit de collecte, puis la langue de la source,
# les questions se sont mises à porter sur MA PROPRE PROSE — « votre » (80
# fiches sur 80), « point », « confronter », « seulement », « référentiel ».
# Ce sont mes tics d'écriture, répétés dans chaque lecture critique.
#
# Un terme présent sur plus d'un quart du corpus ne désigne pas un thème : il
# désigne la façon dont ce site écrit. Le plafond est celui qu'emploie déjà
# `croisement.dossiers_par_terme`, et pour la même raison.
PART_MAX_CORPUS = 0.25

# Les mots que la liste de `croisement` ne couvre pas et qui traversent tous
# les filtres sans rien désigner. Écrits ici plutôt que devinés : une liste
# calculée sur ce corpus retirerait aussi les termes utiles, qui y sont rares
# par construction.
_VIDES_EN_PLUS = {
    "autre", "autres", "service", "services", "meme", "memes", "cette",
    "leurs", "elles", "chaque", "entre", "toute", "toutes", "tous",
    "plus", "moins", "aussi", "alors", "donc", "ainsi", "encore",
}


def _est_vide(mot):
    return mot in X._VIDES or mot in _VIDES_EN_PLUS


_RIEN_ETABLI = (
    "Cette confrontation ne lit pas votre document : elle compare des mots. "
    "Un terme absent ne signifie PAS que le sujet est absent — votre document "
    "peut le traiter sous un autre nom. Ce qui suit est une liste de questions "
    "à poser à votre document, jamais une liste de manques constatés, et "
    "encore moins un avis de conformité.")


def _sansaccent(x):
    s = unicodedata.normalize("NFD", str(x or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


# ── LIRE LE DOCUMENT, ET DIRE QUAND ON NE SAIT PAS ────────────────────────

def _texte_docx(brut):
    """Un .docx est un zip d'XML : la bibliothèque standard suffit.

    On évite ainsi une dépendance de plus pour lire un format documenté. Le
    jour où le fichier n'est pas un zip valide, on le dit — plutôt que de
    rendre un texte vide qui se lirait comme un document sans vocabulaire.
    """
    try:
        with zipfile.ZipFile(io.BytesIO(brut)) as z:
            xml = z.read("word/document.xml").decode("utf-8", "replace")
    except (zipfile.BadZipFile, KeyError, OSError) as e:
        return None, "Fichier .docx illisible : %s" % e
    # Les balises <w:t> portent le texte ; le reste est de la mise en forme.
    morceaux = re.findall(r"<w:t[^>]*>(.*?)</w:t>", xml, re.S)
    if not morceaux:
        return None, "Aucun texte trouvé dans ce .docx."
    txt = " ".join(morceaux)
    txt = re.sub(r"&lt;", "<", re.sub(r"&gt;", ">", re.sub(r"&amp;", "&", txt)))
    return txt, ""


def _texte_pdf(brut):
    try:
        import pypdf
    except ImportError:
        return None, ("Le PDF n'a pas pu être lu : la bibliothèque `pypdf` "
                      "n'est pas installée sur ce serveur. Déposez le document "
                      "en .txt ou .docx, ou faites installer `pypdf`.")
    try:
        lec = pypdf.PdfReader(io.BytesIO(brut))
        txt = "\n".join((p.extract_text() or "") for p in lec.pages)
    except Exception as e:  # noqa: BLE001
        return None, "PDF illisible : %s" % e
    if not txt.strip():
        return None, ("Ce PDF ne porte aucun texte extractible — il est "
                      "probablement composé d'images numérisées. Une "
                      "reconnaissance de caractères serait nécessaire ; ce "
                      "site n'en fait pas, et ne le simule pas.")
    return txt, ""


def lire(nom, brut):
    """Le texte d'un document, ou la raison pour laquelle on ne l'a pas."""
    if not brut:
        return None, "Fichier vide."
    if len(brut) > OCTETS_MAX:
        return None, ("Fichier trop volumineux (%.1f Mo, maximum %d Mo). "
                      "Au-delà, le vocabulaire d'un dossier entier se confond "
                      "avec celui de la langue et la confrontation ne "
                      "distingue plus rien."
                      % (len(brut) / 1048576.0, OCTETS_MAX // 1048576))
    ext = ("." + nom.rsplit(".", 1)[-1].lower()) if "." in (nom or "") else ""
    if ext not in FORMATS:
        return None, ("Format non pris en charge (%s). Formats lus : %s."
                      % (ext or "sans extension", ", ".join(sorted(FORMATS))))
    if ext == ".docx":
        return _texte_docx(brut)
    if ext == ".pdf":
        return _texte_pdf(brut)
    return brut.decode("utf-8", "replace"), ""


# ── LE VOCABULAIRE, PAR LES MÊMES RÈGLES QUE LE CORPUS ────────────────────

def termes(texte, mini_longueur=4):
    """Les termes distinctifs d'un texte.

    LES RÈGLES SONT CELLES DE `croisement._termes`, et c'est délibéré : si le
    document et le corpus étaient découpés autrement, la comparaison porterait
    sur deux vocabulaires incomparables et rendrait des absences fictives.
    """
    brut = _sansaccent(texte)
    mots = re.findall(r"[a-z][a-z0-9-]{%d,}" % (mini_longueur - 1), brut)
    out = Counter()
    for m in mots:
        m = m.strip("-")
        if len(m) < mini_longueur or _est_vide(m):
            continue
        if re.match(r"^[a-z]?\d", m) or re.search(r"\d{3,}", m):
            continue
        out[m] += 1
    return out


def _vocabulaire_francais(f):
    """Le vocabulaire d'une fiche, DANS LA LANGUE DU LECTEUR.

    DÉFAUT CORRIGÉ, mesuré avant mise en ligne. La confrontation puisait dans
    le TITRE et le CHAPEAU — qui viennent de la source, donc en anglais pour
    MITRE et CISA. Une politique de sécurité française se voyait alors
    demander si elle traitait de « targeted », « malware » et « threat ».
    C'est le même bruit que les questions sur le « gCO2e », par une autre
    cause : on comparait deux langues.

    Les champs retenus sont ceux que ce site RÉDIGE : la lecture, la portée
    et l'incertitude, composées en français par les règles d'`ingestion`. Le
    titre et le chapeau restent affichés — ils sont la source — mais ils ne
    servent plus à confronter.
    """
    return (set(termes(f.get("lecture") or "", 5))
            | set(termes(f.get("portee") or "", 5))
            | set(termes(f.get("incertitude") or "", 5)))


def _termes_du_corpus(corpus):
    """Les termes du corpus, avec les fiches ET LES SOURCES qui les portent.

    On compte des fiches et non des occurrences : un mot répété trente fois
    dans une seule fiche n'est pas un thème du corpus, c'est un tic de cette
    fiche-là. Et l'on retient AUSSI les sources, parce que quatorze fiches
    issues d'un même gabarit ne valent pas quatorze témoignages.
    """
    par_terme = Counter()
    porteurs, sources = {}, {}
    for f in V.publiables(corpus):
        vus = _vocabulaire_francais(f)
        cle = (f.get("source") or {}).get("cle") or "?"
        for t in vus:
            par_terme[t] += 1
            porteurs.setdefault(t, []).append(f)
            sources.setdefault(t, set()).add(cle)
    return par_terme, porteurs, sources


def sujet_probable(texte, corpus):
    """Le sujet auquel ce document ressemble le plus, et à quel point.

    DÉDUIT, PAS DEMANDÉ. Poser la question au déposant reporterait sur lui un
    choix qu'il n'a aucune raison de savoir faire — les quatre rubriques sont
    les nôtres, pas les siennes. Déduit, le sujet est AFFICHÉ et refusable :
    c'est la seule forme honnête d'un choix fait à sa place.
    """
    mots = set(termes(texte))
    if not mots:
        return None, 0.0, {}
    scores = {}
    for c in V.ORDRE_SUJETS:
        fiches = [f for f in V.publiables(corpus) if f.get("sujet") == c]
        if not fiches:
            continue
        voc = set()
        for f in fiches:
            voc |= _vocabulaire_francais(f)
        # La part du VOCABULAIRE DU SUJET que le document emploie. Rapportée
        # au sujet et non au document : un document long recouvrirait sinon
        # tous les sujets par sa seule longueur.
        scores[c] = (len(mots & voc) / len(voc)) if voc else 0.0
    if not scores:
        return None, 0.0, {}
    classes = sorted(scores.items(), key=lambda kv: -kv[1])
    gagnant, premier = classes[0]
    second = classes[1][1] if len(classes) > 1 else 0.0
    # L'AVANCE, PAS LE NIVEAU : c'est l'écart au suivant qui dit si une
    # rubrique se détache, pas la valeur absolue du recouvrement.
    avance = (premier / second) if second else (float("inf") if premier else 0.0)
    return gagnant, premier, scores, avance


def confronter(texte, corpus, maxi_questions=12, maxi_echos=8, sujet=None):
    """Le document en regard du corpus. Ce qu'il ne dit pas, d'abord.

    L'ORDRE DES BLOCS RENDUS N'EST PAS DÉCORATIF. Ce que le document ne
    mentionne pas vient AVANT ce qu'il partage : l'écho est flatteur et sans
    valeur — vous saviez déjà de quoi parle votre document —, tandis que
    l'absence est le seul apport possible d'une machine qui ne lit pas.
    """
    mots = termes(texte)
    total_mots = sum(mots.values())
    if total_mots < MOTS_MIN:
        return {"ok": False, "erreur": "trop_court",
                "message": ("Ce document ne porte que %d mot(s) distinctif(s) : "
                            "en dessous de %d, la confrontation ne mesure que "
                            "du bruit et rendrait des absences qui n'en sont "
                            "pas." % (total_mots, MOTS_MIN))}

    # ── À QUOI CONFRONTE-T-ON ? ─────────────────────────────────────────
    devine, part, scores, avance = sujet_probable(texte, corpus)
    impose = sujet in V.SUJETS
    if impose:
        retenu, pourquoi_sujet = sujet, "rubrique imposée par vous."
    elif devine and avance >= AVANCE_SUJET_MIN:
        retenu = devine
        pourquoi_sujet = ("rubrique déduite de votre document : son vocabulaire "
                          "y est %s fois plus présent que dans la rubrique "
                          "suivante. Vous pouvez la changer."
                          % ("%.1f" % avance).replace(".", ","))
    else:
        retenu = None
        pourquoi_sujet = ("aucune rubrique ne se détache — la première ne "
                          "devance la deuxième que de %s fois, sous le seuil "
                          "de %s. La confrontation porte donc sur le corpus "
                          "entier, ce qui produit des questions hors de votre "
                          "domaine : choisissez une rubrique pour les écarter."
                          % (("%.1f" % avance).replace(".", ","),
                             ("%.1f" % AVANCE_SUJET_MIN).replace(".", ",")))

    presents = set(mots)

    def _mesurer(portee):
        """Ce que le document et un ensemble de fiches se disent l'un à
        l'autre. Extrait de la suite parce que la mesure peut être REFAITE :
        une rubrique déduite qui ne donne rien est élargie au corpus entier,
        et deux copies de ce calcul auraient divergé.
        """
        par_terme, porteurs, sources = _termes_du_corpus(portee)

        # ── CE QUE LE CORPUS PORTE ET QUE LE DOCUMENT NE NOMME PAS ───────
        plafond = max(MINI_FICHES, int(len(portee) * PART_MAX_CORPUS))
        questions, ecartes_gabarit, ecartes_partout = [], 0, 0
        for t, n in par_terme.most_common():
            if n < MINI_FICHES or t in presents:
                continue
            # CE QUI EST PARTOUT N'EST NULLE PART : au-delà du plafond, le terme
            # décrit la façon dont ce site écrit, pas un thème du corpus.
            if n > plafond:
                ecartes_partout += 1
                continue
            # UN SEUL GABARIT N'EST PAS UN THÈME. Quatorze fiches issues d'une
            # même phrase ne valent pas quatorze témoignages.
            if len(sources.get(t, ())) < MINI_SOURCES:
                ecartes_gabarit += 1
                continue
            fs = porteurs[t]
            sujets = sorted({f.get("sujet") for f in fs})
            questions.append({
                "terme": t, "fiches": n,
                "sources": sorted(x for x in sources[t] if x),
                "sujets": sujets,
                "sujets_nom": [V.SUJETS.get(x, {}).get("nom", x) for x in sujets],
                "exemples": [{"id": f.get("id"), "titre": f.get("titre")}
                             for f in sorted(fs, key=lambda x: str(x.get("date_fait")),
                                             reverse=True)[:3]],
                "question": ("« %s » revient dans %d fiche(s) issues de %d source(s) "
                             "et n'apparaît pas dans votre document. Le sujet y "
                             "est-il traité sous un autre nom ?"
                             % (t, n, len(sources[t]))),
            })
            if len(questions) >= maxi_questions:
                break

        # ── CE QUE LE DOCUMENT ET LE CORPUS ONT EN COMMUN ────────────────────
        echos = []
        for t in sorted(presents & set(par_terme), key=lambda x: -par_terme[x]):
            if (par_terme[t] < MINI_FICHES or par_terme[t] > plafond
                    or len(sources.get(t, ())) < MINI_SOURCES):
                continue
            echos.append({
                "terme": t, "fiches": par_terme[t],
                "occurrences_document": mots[t],
                "exemples": [{"id": f.get("id"), "titre": f.get("titre")}
                             for f in porteurs[t][:2]],
            })
            if len(echos) >= maxi_echos:
                break
        return {"questions": questions, "echos": echos, "plafond": plafond,
                "portee": portee, "ecartes_gabarit": ecartes_gabarit,
                "ecartes_partout": ecartes_partout}

    # ── LA RUBRIQUE DÉDUITE PEUT NE RIEN DONNER, ET ALORS ON ÉLARGIT ──────
    # DÉFAUT MESURÉ. Les seuils de terme — trois fiches, deux sources, un
    # plafond de part — sont calibrés sur le corpus entier. Appliqués à une
    # seule rubrique, ils peuvent ne rien laisser passer : une rubrique servie
    # par DEUX sources exige qu'un terme figure dans les deux, ce qui
    # n'arrive presque jamais. Le document rendait alors zéro pont là où le
    # corpus entier en donnait six.
    #
    # LA RÈGLE NE S'APPLIQUE QU'À UNE RUBRIQUE DÉDUITE. Si vous l'avez
    # imposée, ce site ne passe pas outre : il dit que cette rubrique-là ne
    # donne rien, et c'est une réponse.
    m = _mesurer([f for f in V.publiables(corpus) if f.get("sujet") == retenu]
                 if retenu else V.publiables(corpus))
    elargi = False
    if retenu and not impose and not m["echos"] and len(m["questions"]) < 3:
        large = _mesurer(V.publiables(corpus))
        if large["echos"] or large["questions"]:
            m, elargi = large, True
            pourquoi_sujet += (" CETTE RUBRIQUE N'A RIEN DONNÉ — trop peu de "
                               "fiches pour que les seuils de terme y laissent "
                               "passer quoi que ce soit —, la confrontation a "
                               "donc été refaite sur le corpus entier. Les "
                               "rapprochements ci-dessous peuvent sortir de "
                               "votre domaine.")

    questions, echos, plafond = m["questions"], m["echos"], m["plafond"]
    portee = m["portee"]
    ecartes_gabarit, ecartes_partout = m["ecartes_gabarit"], m["ecartes_partout"]

    # ── LES QUESTIONS TIENNENT-ELLES DEBOUT ? ────────────────────────────
    # On ne sert pas une liste parce qu'elle est non vide. Un corpus dont les
    # analyses sont dérivées par règles porte un vocabulaire uniforme : les
    # termes qui restent après les trois filtres sont souvent des mots de
    # liaison, et une liste de mots de liaison présentée comme des « points à
    # instruire » ferait perdre confiance dans tout le reste de la page.
    #
    # LE CRITÈRE EST LA DIVERSITÉ DE SOURCES, faute de mieux : un terme porté
    # par trois sources ou plus a traversé trois gabarits différents, donc il
    # désigne autre chose qu'une tournure. En dessous, on s'abstient et on
    # explique.
    solides = [q for q in questions if len(q["sources"]) >= 3]
    questions_utiles = len(solides) >= 3
    if questions_utiles:
        questions = solides
        pourquoi_questions = ("%d terme(s) portés par au moins trois sources "
                              "différentes : ils ont traversé trois gabarits, "
                              "donc ils désignent un sujet et non une "
                              "tournure." % len(solides))
    else:
        pourquoi_questions = (
            "AUCUNE QUESTION N'EST PROPOSÉE, et c'est un constat, pas une "
            "panne. Ce site DÉRIVE ses lectures par règles publiées plutôt "
            "que de les rédiger : son vocabulaire français est donc uniforme "
            "d'une fiche à l'autre, et ce qui en reste après filtrage tient "
            "davantage de la tournure que du sujet. Servir cette liste "
            "reviendrait à vous présenter des mots de liaison comme des "
            "points à instruire. Les ponts ci-dessous, eux, sont réels.")

    return {
        "ok": True,
        "mots_document": total_mots,
        "termes_distincts": len(mots),
        "sujet": retenu,
        "sujet_nom": V.SUJETS.get(retenu, {}).get("nom") if retenu else None,
        "sujet_pourquoi": pourquoi_sujet,
        # L'ÉLARGISSEMENT EST DÉCLARÉ, pas seulement raconté dans la phrase :
        # une page qui l'affiche doit pouvoir le marquer, et un contrôle doit
        # pouvoir le lire sans analyser du texte.
        "sujet_elargi": elargi,
        "sujet_scores": {c: round(v * 100) for c, v in (scores or {}).items()},
        "fiches_confrontees": len(portee),
        "fiches_corpus": len(V.publiables(corpus)),
        "questions": questions if questions_utiles else [],
        "n_questions": len(questions) if questions_utiles else 0,
        "questions_utiles": questions_utiles,
        "questions_pourquoi": pourquoi_questions,
        "questions_brutes": len(questions),
        "echos": echos,
        "n_echos": len(echos),
        "seuil_fiches": MINI_FICHES,
        "seuil_sources": MINI_SOURCES,
        # LA COUPE EST DITE, comme partout sur ce site.
        "termes_ecartes_gabarit": ecartes_gabarit,
        "termes_ecartes_partout": ecartes_partout,
        "plafond_fiches": plafond,
        "ecartes_dit": " ".join(x for x in (
            ("%d terme(s) écartés parce qu'ils ne viennent que d'UNE source : "
             "ce qu'un seul gabarit répète est son vocabulaire à lui, pas un "
             "thème du corpus." % ecartes_gabarit) if ecartes_gabarit else "",
            ("%d terme(s) écartés parce qu'ils figurent sur plus de %d fiches "
             "(un quart du corpus) : ils décrivent la façon dont ce site "
             "écrit, pas un sujet." % (ecartes_partout, plafond))
            if ecartes_partout else "") if x),
        "n_etablit_pas": _RIEN_ETABLI,
        "dit": ("%d pont(s) entre votre document et %d fiche(s) de la "
                "rubrique « %s »%s."
                % (len(echos), len(portee),
                   V.SUJETS.get(retenu, {}).get("nom", "toutes rubriques"),
                   " ; %d question(s) à instruire" % len(questions)
                   if questions_utiles else " ; aucune question proposée")),
        # LE TEXTE DÉPOSÉ NE REVIENT PAS DANS LA RÉPONSE. Le renvoyer, fût-ce
        # par commodité d'affichage, le ferait transiter une fois de plus et
        # apparaître dans les journaux du navigateur.
        "document_conserve": False,
    }


def sante():
    return {
        "module": "confrontation", "version": VERSION,
        "formats": sorted(FORMATS),
        "octets_max": OCTETS_MAX,
        "modeles_de_langage": 0,
        "document_conserve": False,
        "portee": "Compare le VOCABULAIRE d'un document au corpus. Ne lit pas "
                  "le document, ne le juge pas, ne certifie aucune conformité. "
                  "Rend des questions à poser, jamais des manques constatés.",
    }


def _verifier():
    if MINI_FICHES < 2:
        raise RuntimeError(
            "confrontation : le seuil est tombé sous deux fiches — un mot de "
            "circonstance serait présenté comme un thème du corpus")
    for mot in ("ne lit pas votre document", "questions à poser"):
        if mot not in _RIEN_ETABLI:
            raise RuntimeError(
                "confrontation : la réserve ne dit plus que le module ne lit "
                "pas le document — c'est la seule phrase qui empêche de "
                "prendre le résultat pour un audit")


_verifier()
