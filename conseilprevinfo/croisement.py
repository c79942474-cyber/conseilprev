"""LE CROISEMENT — ce qu'aucune source ne dit toute seule.

CE QUI SÉPARE UNE VEILLE D'UN AGRÉGATEUR. Un agrégateur empile des fiches
venues de sources différentes et laisse le lecteur faire le lien. Or le lien
EST le travail : une vulnérabilité chez un automaticien et un mode opératoire
qui vise ce type d'actif ne se lisent pas de la même façon quand on sait
qu'ils portent sur la même décision. Ce module établit ces liens, et
surtout : il DIT POURQUOI chacun existe.

TROIS RÈGLES QUE CE MODULE S'IMPOSE.

  1. UN LIEN SANS MOTIF ÉCRIT N'EST PAS UN LIEN. « Articles similaires » est
     une promesse creuse : le lecteur ne sait pas s'il tient une coïncidence
     de vocabulaire ou une vraie dépendance. Chaque lien porte donc sa raison
     en toutes lettres, et sa FORCE.

  2. AUCUN LIEN N'EST INFÉRÉ PAR UN MODÈLE. Les règles sont écrites ici et
     lisibles. Deux exécutions sur le même corpus rendent les mêmes liens,
     dans le même ordre.

  3. LE CROISEMENT NE FABRIQUE AUCUN FAIT. Il rapproche des fiches qui
     portent déjà leur source. Il ne conclut pas : dire « ces deux éléments
     rapprochés prouvent que… » serait produire une information que ni l'une
     ni l'autre des sources ne porte, et c'est précisément la faute qu'un
     site de veille ne peut pas se permettre.

CE QU'IL NE FAIT PAS. Il ne détecte pas les contradictions entre sources —
avec le corpus actuel, les sources ne se recouvrent pas assez pour qu'une
contradiction soit détectable autrement que par un jugement. Le jour où deux
sources chiffreront la même grandeur, ce sera la fonction la plus utile de ce
fichier ; elle est laissée vide plutôt qu'approximée.
"""
import unicodedata
from datetime import date

import veille as V

VERSION = "2026.08.22"

# ── Les types de lien, et ce que chacun vaut ──────────────────────────────
# La FORCE n'est pas un score : c'est un rang. « 0,73 de similarité »
# emprunterait le vocabulaire de la mesure pour désigner une règle.
LIENS = {
    # LE SEUL LIEN QUI N'ENGAGE PAS LE CABINET, donc le plus fort. Tous les
    # autres sont des règles que J'AI écrites : défendables, mais de moi.
    # Celui-ci reprend un objet `relationship` publié par le référentiel —
    # « Sandworm Team emploie Industroyer ». Ce n'est pas inférer, c'est
    # citer, et la citation d'origine voyage avec le lien.
    "declaree_par_la_source": {
        "nom": "Déclaré par la source",
        "force": 1,
        "dit": "Le référentiel d'origine affirme lui-même la relation entre "
               "ces deux fiches, et fournit les références sur lesquelles il "
               "s'appuie. Ce site ne fait que la reprendre : le lecteur peut "
               "remonter au rapport d'origine sans passer par lui.",
    },
    "meme_editeur": {
        "nom": "Même éditeur",
        "force": 2,
        "dit": "Les deux fiches portent sur le même fournisseur. C'est le lien "
               "le plus opérationnel : elles concernent le même contrat, le "
               "même interlocuteur et souvent la même fenêtre de maintenance.",
    },
    "meme_pays": {
        "nom": "Même pays",
        "force": 3,
        "dit": "Les deux fiches portent sur le même territoire, donc sur le "
               "même régime juridique et le même réseau électrique.",
    },
    "meme_technologie": {
        "nom": "Même technologie",
        "force": 4,
        "dit": "Les deux fiches partagent au moins une technologie déclarée.",
    },
    "meme_periode": {
        "nom": "Même période",
        "force": 5,
        "dit": "Faits rapprochés dans le temps sur le même sujet. La "
               "proximité de date n'est PAS une relation de cause : c'est un "
               "repère de lecture, et rien de plus.",
    },
}
ORDRE_LIENS = ["declaree_par_la_source", "meme_editeur", "meme_pays",
               "meme_technologie", "meme_periode"]

# ── LE LIEN QUE J'AI RETIRÉ, ET POURQUOI C'EST ÉCRIT ICI ──────────────────
# « Technique et faille » devait rapprocher un mode opératoire ATT&CK d'une
# vulnérabilité KEV sur le même terrain — le croisement le plus utile qu'un
# site puisse offrir, puisque aucune des deux sources ne le fait.
#
# IL A ÉTÉ RETIRÉ APRÈS MESURE. Sa seule condition réalisable sur les données
# disponibles était « même sujet », ce qui reliait une CVE Rockwell aux
# QUATORZE groupes du référentiel, avec le même motif recopié. Un lien qui
# relie tout à tout ne renseigne sur rien, et il coûte davantage qu'il ne
# rapporte : il apprend au lecteur à ne plus lire les motifs.
#
# CE QU'IL FAUDRAIT POUR LE RÉTABLIR : une correspondance entre le produit
# d'une entrée KEV et les types d'actifs d'ATT&CK ICS (objets
# `x-mitre-asset`, dix-huit au référentiel). Elle n'existe dans aucune des
# deux sources — il faudrait la tenir à la main, et ce serait alors un
# jugement du cabinet, à déclarer comme tel.
LIEN_RETIRE = {
    "cle": "technique_et_faille",
    "pourquoi": "Aucune donnée des deux sources ne permet de le fonder "
                "autrement que par « même sujet », ce qui reliait chaque "
                "vulnérabilité à l'ensemble des modes opératoires.",
    "ce_qu_il_faudrait": "Une correspondance produit KEV → type d'actif "
                         "ATT&CK ICS, tenue à la main et déclarée comme un "
                         "jugement du cabinet.",
}

# Les technologies trop génériques pour fonder un lien : présentes sur
# presque toutes les fiches d'un sujet, elles relieraient tout à tout et le
# croisement ne dirait plus rien.
# Ce sont des ÉTIQUETTES DE CATÉGORIE posées par les collecteurs, pas des
# technologies. Les laisser fonder un lien reliait les vingt fiches ATT&CK
# entre elles par « mode operatoire » — un lien vrai et sans aucun intérêt.
TROP_GENERIQUES = {"ot / iacs", "att&ck ics", "mitre atlas", "mix electrique",
                   "empreinte carbone", "securite des systemes d'ia",
                   "mode operatoire", "logiciel malveillant", "incident reel",
                   "rancongiciel"}

FENETRE_JOURS = 45


def _sansaccent(x):
    s = unicodedata.normalize("NFD", str(x or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def _technos(f):
    return {_sansaccent(t) for t in (f.get("technologies") or []) if t}


def _technos_utiles(f):
    return _technos(f) - TROP_GENERIQUES


def _jours(a, b):
    try:
        return abs((date.fromisoformat(str(a)[:10])
                    - date.fromisoformat(str(b)[:10])).days)
    except (TypeError, ValueError):
        return 10**6


def _editeur(f):
    """L'éditeur est un champ DÉCLARÉ par le collecteur, plus une devinette.

    DÉFAUT CORRIGÉ. Il était deviné en prenant la première technologie non
    générique de la fiche — ce qui rangeait « Logiciel malveillant » et
    « Mode opératoire » parmi les fournisseurs, et produisait des dossiers
    intitulés d'après mes propres étiquettes de catégorie. Un dossier
    « Éditeur : Mode opératoire » se lit comme une erreur de programmation,
    parce que c'en était une.

    Seul le collecteur sait ce qu'est un fournisseur dans sa source ; il le
    dit maintenant explicitement dans `editeur`.
    """
    e = f.get("editeur")
    return _sansaccent(e) if e else None


def liens(fiche, corpus, maxi=6):
    """Les fiches qui portent sur la même décision que celle-ci, avec le
    MOTIF de chaque rapprochement.

    L'ordre est celui de la force du lien, puis de la fraîcheur : un lien
    fort et ancien vaut mieux qu'un lien faible et récent, parce que c'est
    le lien qui décide de l'intérêt, pas la date.
    """
    ident = fiche.get("id")
    out = []
    # CE QUE LA SOURCE DÉCLARE ELLE-MÊME, indexé par fiche visée. Il est lu en
    # premier parce qu'il prime sur toutes les règles écrites ici : quand le
    # référentiel affirme la relation, il n'y a rien à inférer.
    declarees = {}
    for rel in (fiche.get("relations") or []):
        if rel.get("vers"):
            declarees.setdefault(rel["vers"], rel)
    ed_a = _editeur(fiche)
    techs_a = _technos_utiles(fiche)
    pays_a = {str(p).upper() for p in (fiche.get("pays") or [])}

    for g in V.publiables(corpus):
        if g.get("id") == ident:
            continue
        motifs = []

        decl = declarees.get(g.get("id"))
        if decl:
            motifs.append(("declaree_par_la_source", decl.get("dit") or
                           "Relation affirmée par le référentiel d'origine."))

        ed_b = _editeur(g)
        if ed_a and ed_b and ed_a == ed_b:
            motifs.append(("meme_editeur",
                           "Les deux portent sur « %s »."
                           % (fiche.get("editeur") or ed_a)))

        pays_b = {str(p).upper() for p in (g.get("pays") or [])}
        communs = pays_a & pays_b
        if communs:
            motifs.append(("meme_pays",
                           "Même territoire : %s." % ", ".join(sorted(communs))))

        techs_c = techs_a & _technos_utiles(g)
        if techs_c:
            motifs.append(("meme_technologie",
                           "Technologie commune : %s."
                           % ", ".join(sorted(techs_c)[:3])))

        if (not motifs and fiche.get("sujet") == g.get("sujet")
                and _jours(fiche.get("date_fait"), g.get("date_fait")) <= FENETRE_JOURS):
            motifs.append(("meme_periode",
                           "Même sujet, à moins de %d jours." % FENETRE_JOURS))

        if not motifs:
            continue
        motifs.sort(key=lambda m: LIENS[m[0]]["force"])
        type_, pourquoi = motifs[0]
        out.append({
            "id": g.get("id"), "titre": g.get("titre"),
            "sujet": g.get("sujet"), "sujet_nom": g.get("sujet_nom"),
            "date_fait": g.get("date_fait"),
            "impact": g.get("impact"), "impact_nom": g.get("impact_nom"),
            "lien": type_, "lien_nom": LIENS[type_]["nom"],
            "lien_force": LIENS[type_]["force"],
            "pourquoi": pourquoi,
            # LA CHAÎNE DE PREUVE VOYAGE AVEC LE LIEN. Un rapprochement repris
            # d'un référentiel sans les références sur lesquelles il s'appuie
            # obligerait à nous croire sur parole — exactement ce que ce site
            # reproche aux agrégateurs.
            "citations": (decl.get("citations") or []) if decl else [],
        })

    out.sort(key=lambda x: (x["lien_force"], _inv(x["date_fait"])))
    return out[:maxi]


# ── CE QUI N'EST PAS UN LIEN, ET QUI NE DOIT PAS EN PORTER LE NOM ─────────
# MESURE SUR LE CORPUS RÉEL : sur 314 rapprochements, 312 tenaient au seul
# « même sujet, à moins de 45 jours ». Le site n'ayant que quatre sujets,
# cette condition est presque vide : elle rapproche à peu près tout de tout à
# l'intérieur d'un sujet, et chaque fiche affichait six voisines portant le
# MÊME motif recopié.
#
# C'est exactement la faute pour laquelle « technique et faille » a été
# retiré plus haut, et ce module se l'appliquait à lui-même : « un lien qui
# relie tout à tout n'apprend rien, et coûte plus qu'il ne rapporte — il
# apprend au lecteur à ne plus lire les motifs ».
#
# LE REMÈDE N'EST PAS DE LE SUPPRIMER. Savoir ce qui est tombé d'autre dans
# la même quinzaine est utile ; c'est le NOM qui était faux. Une proximité de
# calendrier est un VOISINAGE, pas un lien, et elle est présentée à part,
# sous son vrai nom, en quantité bornée.
LIENS_FAIBLES = {"meme_periode"}


def croiser(fiche, corpus, maxi=6, maxi_voisinage=3):
    """Sépare ce qui est un LIEN de ce qui n'est qu'un voisinage de date.

    Les mélanger laisse croire qu'une coïncidence de calendrier vaut une
    dépendance — et comme le voisinage est de loin le plus abondant, c'est
    lui qui aurait donné le ton de toute la rubrique.
    """
    tout = liens(fiche, corpus, maxi=10**6)
    forts = [v for v in tout if v["lien"] not in LIENS_FAIBLES][:maxi]
    faibles = [v for v in tout if v["lien"] in LIENS_FAIBLES][:maxi_voisinage]
    return {
        "liens": forts,
        "voisinage": faibles,
        "voisinage_total": sum(1 for v in tout if v["lien"] in LIENS_FAIBLES),
        "voisinage_dit": "Ces fiches ne sont PAS rattachées à celle-ci : elles "
                         "portent le même sujet et sont tombées dans les %d "
                         "jours. C'est un repère de lecture — la proximité de "
                         "date n'établit aucune relation, et elle est ici la "
                         "seule chose qu'elles aient en commun."
                         % FENETRE_JOURS,
    }


def mesure_liens(corpus):
    """DE QUOI LE CROISEMENT EST FAIT — la mesure qui l'empêche de mentir.

    Un module qui rapproche doit pouvoir dire par quoi il rapproche. Sans ce
    compte, la rubrique garde le vocabulaire du croisement de sources alors
    que ses rapprochements peuvent tous tenir à la même règle faible, et
    personne ne s'en aperçoit — c'est ainsi que le défaut ci-dessus a vécu.
    """
    pub = V.publiables(corpus)
    par_type = {k: 0 for k in LIENS}
    sans = 0
    for f in pub:
        vs = liens(f, corpus, maxi=10**6)
        if not [v for v in vs if v["lien"] not in LIENS_FAIBLES]:
            sans += 1
        for v in vs:
            par_type[v["lien"]] += 1
    total = sum(par_type.values())
    forts = sum(n for k, n in par_type.items() if k not in LIENS_FAIBLES)
    return {
        "par_type": par_type, "total": total, "liens_forts": forts,
        "fiches_sans_lien_fort": sans, "fiches": len(pub),
        "dit": ("Aucun rapprochement sur ce corpus." if not total else
                "%d rapprochement(s), dont %d qui tiennent à autre chose qu'à "
                "une proximité de date. %d fiche(s) sur %d n'ont aucun lien "
                "fort : c'est ce que les sources portent, et le site ne "
                "comble pas ce vide."
                % (total, forts, sans, len(pub))),
    }


def _inv(d):
    try:
        p = [int(x) for x in str(d)[:10].split("-")]
        return (-p[0], -p[1], -p[2])
    except (ValueError, IndexError):
        return (0, 0, 0)


# Mots qui ne peuvent pas fonder un dossier : trop courants dans les titres
# du corpus pour désigner quoi que ce soit. Écrits ici plutôt que devinés —
# une liste de mots vides calculée sur un petit corpus retire les mots utiles.
_VIDES = {
    "mode", "operatoire", "documente", "documentee", "contre", "logiciel",
    "malveillant", "technique", "systeme", "systemes", "attack", "atlas",
    "multiple", "products", "produit", "produits", "electricite", "carbone",
    "bas", "part", "dont", "pour", "avec", "dans", "les", "des", "une", "sur",
    "and", "the", "for", "via", "attaque", "ics", "ia", "cve", "aml",
}


def _termes(f):
    """Les termes distinctifs d'un titre.

    On garde les mots d'au moins quatre lettres, hors mots vides, et on
    écarte ce qui ressemble à une référence technique (CVE-…, AML.CS…, G0082)
    — un identifiant est unique par construction et ne regroupe rien.
    """
    import re as _re
    # L'APOSTROPHE EST UNE COUPURE, PAS UNE LETTRE, et c'est la classe de
    # caractères ci-dessous qui l'impose : elle ne l'admet pas, donc une
    # apostrophe termine toujours le mot en cours.
    #
    # DÉFAUT CORRIGÉ ICI. Une classe qui admettait l'apostrophe faisait de
    # « l'ICS » et « d'électricité » des termes entiers, et ils formaient les
    # plus gros dossiers du site — alors qu'ils ne désignent que l'article
    # français collé au mot suivant, lequel est déjà écarté comme trop
    # courant. La règle tient donc au motif, pas à un nettoyage en aval :
    # un nettoyage se retire par mégarde, le motif se lit.
    brut = _sansaccent(f.get("titre", ""))
    mots = _re.findall(r"[a-z][a-z0-9-]{3,}", brut)
    out = set()
    for m in mots:
        m = m.strip("-")
        if len(m) < 4 or m in _VIDES:
            continue
        if _re.match(r"^[a-z]?\d", m) or _re.search(r"\d{3,}", m):
            continue
        out.add(m)
    return out


def dossiers_par_terme(corpus, mini=2, maxi=8):
    """Les dossiers que le VOCABULAIRE du corpus fait apparaître.

    POURQUOI CET AXE PLUTÔT QU'UN AUTRE. Le regroupement par fournisseur ou
    par acteur ne forme rien sur ce corpus : mesuré, chaque fiche porte une
    entité différente. Ce qui se répète, en revanche, ce sont les NOMS
    PROPRES dans les titres — une famille d'incidents visant le même produit
    revient sous le même nom. La règle est donc : un terme distinctif présent
    dans au moins deux titres forme un dossier, et le terme est AFFICHÉ pour
    que le lecteur juge lui-même du bien-fondé du regroupement.

    C'est un rapprochement de vocabulaire, et la fonction le dit : il ne
    prouve aucune relation entre les faits.
    """
    pub = V.publiables(corpus)
    par_terme = {}
    for f in pub:
        for t in _termes(f):
            par_terme.setdefault(t, []).append(f)
    out = []
    for terme, fs in par_terme.items():
        # UN TERME PRÉSENT SUR PLUS DU QUART DU CORPUS ne désigne plus une
        # famille : il désigne le sujet, que les filtres rendent déjà.
        if len(fs) < mini or len(fs) > max(mini, len(pub) // 4):
            continue
        out.append(_dossier(
            "terme", terme,
            "%d fiche(s) dont le titre porte « %s ». Rapprochement de "
            "VOCABULAIRE : il signale une famille de faits, il ne prouve "
            "aucune relation entre eux." % (len(fs), terme), fs))
    out.sort(key=lambda d: (-d["n"], d["libelle"]))
    return out[:maxi]


def dossiers(corpus, mini=2):
    """Les regroupements que le corpus FORME de lui-même.

    Ce ne sont pas des rubriques décidées à l'avance : ce sont les éditeurs
    et les territoires sur lesquels plusieurs fiches se rejoignent. Une
    rubrique écrite d'avance resterait vide ou trop pleine ; celle-ci suit ce
    qui est réellement là.
    """
    pub = V.publiables(corpus)
    par_editeur, par_pays = {}, {}
    for f in pub:
        ed = _editeur(f)
        if ed:
            par_editeur.setdefault(ed, []).append(f)
        for p in (f.get("pays") or []):
            par_pays.setdefault(str(p).upper(), []).append(f)

    out = []
    for ed, fs in par_editeur.items():
        if len(fs) < mini:
            continue
        libelle = next((f.get("editeur") for f in fs if f.get("editeur")), ed)
        out.append(_dossier("editeur", libelle,
                            "%d fiche(s) portant sur ce fournisseur. Elles "
                            "concernent le même contrat et souvent la même "
                            "fenêtre de maintenance." % len(fs), fs))
    for p, fs in par_pays.items():
        if len(fs) < mini:
            continue
        out.append(_dossier("pays", p,
                            "%d fiche(s) sur ce territoire — même régime "
                            "juridique, même réseau électrique." % len(fs), fs))

    out.sort(key=lambda d: (-d["n"], d["libelle"]))
    return out


def mesure_entites(corpus):
    """CE QUE L'AXE PAR ENTITÉ A TROUVÉ — y compris quand il ne trouve rien.

    POURQUOI CETTE FONCTION EXISTE. `dossiers()` regroupe par fournisseur et
    par territoire. Sur le corpus actuel elle rend une liste VIDE : mesuré,
    46 fiches sur 66 ne déclarent aucun fournisseur, et chaque fournisseur
    comme chaque territoire déclaré n'apparaît qu'une fois. Rendre `[]` sans
    rien dire laisserait croire à une panne, ou pire, à une absence de sujet.

    Un site qui n'affiche que ses axes qui donnent quelque chose enseigne au
    lecteur une couverture qu'il n'a pas. L'axe dit donc lui-même ce qu'il a
    compté, et pourquoi il ne forme rien.
    """
    pub = V.publiables(corpus)
    avec_editeur = sum(1 for f in pub if _editeur(f))
    avec_pays = sum(1 for f in pub if f.get("pays"))
    formes = len(dossiers(corpus))
    if formes:
        dit = ("%d regroupement(s) par fournisseur ou territoire."
               % formes)
    elif not pub:
        dit = "Corpus vide : aucun regroupement à mesurer."
    else:
        dit = ("Aucun regroupement par fournisseur ni par territoire sur ce "
               "corpus : %d fiche(s) sur %d déclarent un fournisseur, et "
               "aucun fournisseur ni territoire n'y revient deux fois. Ce "
               "n'est pas une panne — c'est ce que les sources actuelles "
               "portent. Les sources de vulnérabilités nomment un produit "
               "par entrée, et les référentiels de modes opératoires ne "
               "nomment aucun fournisseur du tout."
               % (avec_editeur, len(pub)))
    return {
        "fiches": len(pub), "avec_editeur": avec_editeur,
        "avec_pays": avec_pays, "dossiers_formes": formes, "dit": dit,
    }


def _dossier(genre, libelle, dit, fs):
    fs = sorted(fs, key=lambda f: _inv(f.get("date_fait")))
    return {
        "genre": genre, "libelle": libelle, "dit": dit, "n": len(fs),
        "du": fs[-1].get("date_fait"), "au": fs[0].get("date_fait"),
        "sujets": sorted({f.get("sujet") for f in fs}),
        "fiches": [{"id": f.get("id"), "titre": f.get("titre"),
                    "date_fait": f.get("date_fait"),
                    "impact": f.get("impact")} for f in fs[:8]],
    }


def tension(corpus):
    """CE QUE LE CORPUS NE COUVRE PAS — et qui se voit en le comptant.

    La fonction la plus inconfortable de ce module, donc la plus utile : elle
    dit sur quels sujets le site est mince. Un site de veille qui n'afficherait
    que ses rubriques bien fournies laisserait croire à une couverture
    homogène, et un lecteur en tirerait qu'il ne se passe rien là où, en
    réalité, on ne regarde pas.
    """
    pub = V.publiables(corpus)
    par_sujet = {c: sum(1 for f in pub if f.get("sujet") == c)
                 for c in V.ORDRE_SUJETS}
    vides = [c for c, n in par_sujet.items() if n == 0]
    minces = [c for c, n in par_sujet.items() if 0 < n < 5]
    sources = {(f.get("source") or {}).get("cle") for f in pub}
    return {
        "par_sujet": par_sujet,
        "sujets_vides": vides,
        "sujets_minces": minces,
        "sources_employees": sorted(x for x in sources if x),
        "dit": ("Aucun sujet n'est vide." if not vides else
                "Sujet(s) sans aucune fiche : %s. Ce n'est pas qu'il ne s'y "
                "passe rien — c'est que ce site n'y a pas encore branché de "
                "source." % ", ".join(V.SUJETS[c]["nom"] for c in vides)),
    }


def sante(corpus=None):
    corpus = list(corpus or [])
    return {
        "module": "croisement", "version": VERSION,
        "types_de_lien": len(LIENS),
        "modeles_de_langage": 0,
        "dossiers_par_entite": len(dossiers(corpus)) if corpus else 0,
        "dossiers_par_terme": len(dossiers_par_terme(corpus)) if corpus else 0,
        # LA COMPOSITION EST EXPOSÉE, pas seulement les totaux. C'est faute de
        # la mesurer qu'on a laissé 312 rapprochements sur 314 tenir à la
        # règle la plus faible tout en portant le nom de « croisement ».
        "composition": mesure_liens(corpus) if corpus else None,
        "entites": mesure_entites(corpus) if corpus else None,
        "portee": "Rapproche des fiches qui portent sur la même décision, en "
                  "DISANT pourquoi. Ne conclut rien : le rapprochement ne "
                  "produit aucun fait que les sources ne portent pas.",
    }


def _verifier():
    if set(ORDRE_LIENS) != set(LIENS):
        raise RuntimeError("croisement : l'ordre des liens ne les couvre pas")
    for cle, l in LIENS.items():
        if len(l["dit"]) < 40:
            raise RuntimeError(
                "croisement : le lien %s n'explique pas ce qu'il vaut — un "
                "lien sans motif écrit est une promesse creuse" % cle)
        if not isinstance(l["force"], int) or not 1 <= l["force"] <= 9:
            raise RuntimeError("croisement : force hors barème sur %s" % cle)
    # LA PROXIMITÉ DE DATE NE DOIT JAMAIS ÊTRE LE LIEN LE PLUS FORT : elle ne
    # dit rien d'une dépendance, et la promouvoir ferait passer une
    # coïncidence pour une relation.
    if "technique_et_faille" in LIENS:
        raise RuntimeError(
            "croisement : le lien retiré est revenu sans que la correspondance "
            "produit → actif qui le fonderait ait été écrite")
    if LIENS["meme_periode"]["force"] < max(l["force"] for l in LIENS.values()):
        raise RuntimeError(
            "croisement : la proximité de date est devenue un lien fort — "
            "une coïncidence de calendrier se lirait comme une cause")


_verifier()
