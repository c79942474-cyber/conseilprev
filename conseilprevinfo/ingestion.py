"""LA COLLECTE — comment une source ouverte devient une fiche de veille.

CE QUE CE MODULE FAIT, ET SURTOUT CE QU'IL NE FAIT PAS. Il va chercher des
données publiques, il en tire des FAITS, et il compose la lecture critique
par des RÈGLES ÉCRITES ci-dessous. Il n'appelle aucun modèle de langage, et
ce n'est pas une économie : c'est la condition pour que deux collectes sur la
même donnée rendent le même texte, mot pour mot. Une veille dont l'analyse
change à chaque passage n'est pas une veille, c'est un générateur.

POURQUOI DES RÈGLES PLUTÔT QU'UNE RÉDACTION. Sur un catalogue de 1 674
vulnérabilités, personne ne rédigera 1 674 analyses. L'alternative honnête
n'est pas de faire rédiger un modèle — ce serait 1 674 avis plausibles que
personne n'a tenus. C'est de dériver, par des règles publiées, ce que la
donnée dit DÉJÀ : cette faille est exploitée, cet éditeur est un
automaticien, l'échéance est passée. La lecture qui en sort est modeste et
vraie, et elle porte la mention « dérivée par règles » pour qu'on ne la
prenne pas pour un avis du cabinet.

CE QUI RESTE À LA MAIN. Les fiches de rupture — un texte qui entre en
vigueur, une technologie qui déplace un arbitrage — se rédigent et se
signent. Le pipeline ne les fabrique pas : il les laisse vides plutôt que de
les inventer.

RÉSERVE D'ENVIRONNEMENT. La machine de conception n'a pas d'accès sortant
libre ; seules quelques adresses passent. Les collecteurs ci-dessous ONT été
exécutés contre les vraies sources depuis cet environnement. Ceux qui
dépendent d'adresses refusées sont écrits mais non exécutés, et le disent.
"""
import json
import re
import ssl
import urllib.error
import urllib.request
from datetime import date, datetime, timezone

import sources as SRC
import veille as V

VERSION = "2026.08.22"

# ── QUI EST UN ÉDITEUR INDUSTRIEL ─────────────────────────────────────────
# CETTE LISTE EST UN JUGEMENT DU CABINET, PAS UNE DONNÉE DE SOURCE, et elle
# est écrite ici pour être contestable. Le catalogue KEV ne dit pas si un
# éditeur relève de l'automatisme : il donne un nom. Classer « Siemens » comme
# industriel et « Adobe » comme bureautique est une décision — raisonnable,
# mais une décision. Elle est donc nommée, datée, et le lecteur peut la
# refuser.
#
# La liste est volontairement CONSERVATRICE : mieux vaut manquer un éditeur
# que ranger en « industriel » un produit qui ne l'est pas, ce qui ferait
# monter des fiches sans rapport en tête de rubrique.
EDITEURS_INDUSTRIELS = {
    "siemens", "schneider electric", "rockwell automation", "rockwell",
    "abb", "honeywell", "emerson", "yokogawa", "mitsubishi electric",
    "omron", "hitachi", "hitachi energy", "ge", "general electric",
    "moxa", "advantech", "phoenix contact", "wago", "beckhoff",
    "delta electronics", "unitronics", "automated logic", "johnson controls",
    "iconics", "aveva", "osisoft", "inductive automation", "codesys",
    "3s-smart software solutions", "festo", "pilz", "sick", "wibu-systems",
    "red lion", "opto 22", "trihedral", "vtscada",
}

# Les mots qui, dans un NOM DE PRODUIT, trahissent un usage industriel même
# quand l'éditeur n'est pas au répertoire ci-dessus. Même statut : jugement.
INDICES_PRODUIT_INDUSTRIEL = {
    "scada", "plc", "hmi", "rtu", "modbus", "profinet", "ethernet/ip",
    "opc ua", "opc-ua", "dcs", "ics", "iiot", "automation",
}

_MOIS = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet",
         "août", "septembre", "octobre", "novembre", "décembre")


def _fr_date(iso):
    """« 2026-08-21 » → « 21 août 2026 ». Une date ISO dans un texte français
    signale un contenu non relu."""
    try:
        d = date.fromisoformat(str(iso)[:10])
    except (TypeError, ValueError):
        return str(iso)
    return "%d %s %d" % (d.day, _MOIS[d.month - 1], d.year)


def _lire(url, delai=60, octets_max=40_000_000):
    """Télécharge, ou dit pourquoi il n'a pas pu. Jamais d'exception nue :
    une collecte qui échoue est une information d'exploitation, pas un
    plantage."""
    req = urllib.request.Request(
        url, headers={"User-Agent": "conseilprevinfo/%s (veille sourcée)" % VERSION})
    try:
        with urllib.request.urlopen(req, timeout=delai) as r:
            brut = r.read(octets_max)
        return {"ok": True, "octets": len(brut), "corps": brut}
    except urllib.error.HTTPError as e:
        return {"ok": False, "erreur": "http", "code": e.code,
                "message": "L'éditeur a répondu %s." % e.code}
    except (urllib.error.URLError, ssl.SSLError, TimeoutError, OSError) as e:
        return {"ok": False, "erreur": "injoignable",
                "message": "Adresse injoignable : %s" % e}


# ═══════════════════════════════════════════════════════════════════════════
#  COLLECTEUR 1 — CISA KEV, les vulnérabilités dont l'exploitation est AVÉRÉE
# ═══════════════════════════════════════════════════════════════════════════

def _industriel(vendeur, produit):
    """DÉFAUT CORRIGÉ — la recherche par sous-chaîne nue classait à tort.

    « Intel Ethernet DIAGNOSTICS Driver » ressortait industriel parce que
    « diagnostics » contient « ics » ; « Kaseya VIRTUAL System » parce que
    « virtual » contient « rtu ». Deux faux positifs sur les six premières
    fiches de la une — c'est-à-dire à l'endroit le plus visible du site, et
    avec un motif écrit noir sur blanc sous les yeux du lecteur.

    La recherche se fait donc sur des MOTS ENTIERS. Un indice de trois
    lettres se cache dans trop de mots ordinaires pour être cherché
    autrement.
    """
    v = str(vendeur or "").strip().lower()
    p = str(produit or "").strip().lower()
    if v in EDITEURS_INDUSTRIELS:
        return True, "éditeur au répertoire industriel du cabinet"
    for indice in sorted(INDICES_PRODUIT_INDUSTRIEL):
        # LE SIGLE SUIVI D'UN NUMÉRO EST UNE RÉFÉRENCE DE MODÈLE, pas un mot.
        # Les caméras « D-Link DCS-2530L » entraient au périmètre industriel
        # par le sigle DCS (systeme numérique de contrôle-commande) alors que
        # « DCS » n'y est qu'un préfixe de gamme. Trois des neuf fiches
        # retenues venaient de là.
        if re.search(r"(?<![a-z0-9])%s(?![a-z0-9])(?!-\d)" % re.escape(indice), p):
            return True, "le nom du produit porte le mot « %s »" % indice
    return False, ""


def _lecture_kev(e, industriel, motif, aujourdhui):
    """LES RÈGLES DE LECTURE D'UNE ENTRÉE KEV, écrites une fois et publiées.

    Chaque phrase produite ici est adossée à un champ du catalogue. Aucune
    n'ajoute d'information : elles disent ce que la donnée porte déjà, dans
    l'ordre où un exploitant doit le lire.
    """
    rancon = str(e.get("knownRansomwareCampaignUse", "")).lower() == "known"
    phrases = []

    if industriel:
        phrases.append(
            "L'éditeur relève du périmètre industriel (%s) : la faille est "
            "donc à instruire côté OT, où le correctif ne se pose pas au "
            "même rythme qu'en bureautique." % motif)
    else:
        phrases.append(
            "L'éditeur n'est pas au répertoire industriel du cabinet. La "
            "faille reste à instruire si le produit est présent dans votre "
            "chaîne — un poste d'ingénierie ou un serveur d'historisation "
            "compte comme surface industrielle.")

    if rancon:
        phrases.append(
            "Elle est associée à des campagnes de rançongiciel connues : "
            "c'est le signal le plus fort du catalogue, car il indique une "
            "exploitation outillée et non un cas isolé.")
    else:
        phrases.append(
            "Aucune campagne de rançongiciel n'y est associée à ce jour — ce "
            "qui ne vaut pas absence d'exploitation, seulement absence "
            "d'exploitation par ce mode opératoire.")

    echeance = str(e.get("dueDate") or "")
    if echeance:
        depasse = echeance < aujourdhui.isoformat()
        phrases.append(
            "L'échéance de remédiation imposée aux agences fédérales "
            "américaines était le %s%s. Elle ne vous oblige pas, mais elle "
            "date le moment où le risque a été jugé non tenable par une "
            "autorité." % (_fr_date(echeance),
                           " — elle est dépassée" if depasse else ""))
    return " ".join(phrases)


def _impact_kev(industriel, rancon):
    if industriel and rancon:
        return "rupture"
    if industriel or rancon:
        return "structurant"
    return "incremental"


def collecter_kev(limite=40, depuis=None, seulement_industriel=True):
    """Construit des fiches depuis le catalogue CISA KEV.

    `seulement_industriel` par défaut : ce site parle de cyber INDUSTRIELLE,
    et verser 1 674 vulnérabilités bureautiques noierait ce qui le distingue.
    """
    s = SRC.SOURCES["cisa_kev"]
    r = _lire(s["url_donnee"])
    if not r["ok"]:
        return {"ok": False, "source": "cisa_kev", **r}
    try:
        d = json.loads(r["corps"])
    except ValueError as e:
        return {"ok": False, "source": "cisa_kev", "erreur": "json_illisible",
                "message": str(e)}

    aujourdhui = date.today()
    catalogue = d.get("catalogVersion") or "?"
    fiches, retenues, ecartees = [], 0, 0

    for e in d.get("vulnerabilities", []):
        ajoute = str(e.get("dateAdded") or "")
        if depuis and ajoute < str(depuis):
            continue
        industriel, motif = _industriel(e.get("vendorProject"), e.get("product"))
        if seulement_industriel and not industriel:
            ecartees += 1
            continue
        rancon = str(e.get("knownRansomwareCampaignUse", "")).lower() == "known"
        cve = str(e.get("cveID") or "").strip()
        if not cve:
            continue

        fiche = {
            "id": "kev-%s" % cve.lower(),
            "titre": "%s — %s %s" % (cve, e.get("vendorProject") or "",
                                     e.get("product") or ""),
            "chapeau": V._texte(e.get("vulnerabilityName") or "")
                       + ". Inscrite au catalogue des vulnérabilités dont "
                         "l'exploitation est avérée le %s." % _fr_date(ajoute),
            "lecture": _lecture_kev(e, industriel, motif, aujourdhui),
            "lecture_nature": "regle",
            "portee": "À confronter à votre inventaire : si ce produit est "
                      "présent, la question n'est plus s'il faut corriger "
                      "mais quand, et par quelle mesure compensatoire d'ici "
                      "là. Une fenêtre d'arrêt de production se demande des "
                      "semaines à l'avance — c'est ce délai, pas le correctif, "
                      "qui commande le calendrier.",
            "incertitude": "Le catalogue dit qu'une exploitation existe, pas "
                           "qu'elle vous vise, ni qu'elle atteindrait votre "
                           "installation compte tenu de sa segmentation. "
                           "L'absence d'un produit au catalogue ne vaut pas "
                           "absence de faille.",
            "sujet": "cyber_industriel",
            # L'ÉDITEUR EST DÉCLARÉ, pas deviné plus tard depuis les
            # étiquettes : seul ce collecteur sait ce qu'est un fournisseur
            # dans sa source.
            "editeur": V._texte(e.get("vendorProject")) or None,
            "technologies": _technos_kev(e, industriel),
            "pays": [],
            "date_fait": ajoute,
            "source_cle": "cisa_kev",
            "source_url": s["url_humaine"],
            "statut": "verifiee_source_primaire",
            "impact": _impact_kev(industriel, rancon),
            "horizon": "constate",
            "signe_par": "Collecte automatique — règles publiées dans ingestion.py",
            "collecte": {"catalogue": catalogue, "le": aujourdhui.isoformat()},
        }
        n = V.normaliser(fiche)
        if n["ok"]:
            fiches.append(n["fiche"])
            retenues += 1

    # LE TRI PRÉCÈDE LA COUPE, et l'inverse était un vrai défaut : appliquée
    # pendant le parcours, la limite retenait les PREMIÈRES entrées du
    # catalogue — les plus anciennes — et la une d'un site d'actualité
    # affichait des vulnérabilités de 2022. Trier d'abord, couper ensuite.
    fiches.sort(key=lambda f: f["date_fait"], reverse=True)
    total_perimetre = len(fiches)
    if limite:
        fiches = fiches[:limite]
    retenues = len(fiches)
    return {
        "ok": True, "source": "cisa_kev", "catalogue": catalogue,
        "fiches": fiches, "retenues": retenues, "ecartees_hors_perimetre": ecartees,
        "dans_le_perimetre": total_perimetre,
        # ON DIT CE QU'ON A COUPÉ. Une troncature silencieuse se lit comme une
        # couverture complète — c'est le même mensonge qu'un compte figé.
        "dit": "%d fiche(s) servies, les plus récentes de %d entrées du "
               "périmètre industriel ; %d écartées comme hors périmètre. Le "
               "tri s'appuie sur un répertoire d'éditeurs tenu par le cabinet, "
               "qui est un jugement et non une donnée du catalogue."
               % (retenues, total_perimetre, ecartees),
    }


def _technos_kev(e, industriel):
    t = []
    v = str(e.get("vendorProject") or "").strip()
    if v:
        t.append(v)
    if industriel:
        t.append("OT / IACS")
    if str(e.get("knownRansomwareCampaignUse", "")).lower() == "known":
        t.append("Rançongiciel")
    return t


# ═══════════════════════════════════════════════════════════════════════════
#  COLLECTEUR 2 — OWID, le mix électrique par pays (substrat des centres)
# ═══════════════════════════════════════════════════════════════════════════

# Les pays retenus : ceux où se décident aujourd'hui les implantations de
# centres de données en Europe, plus les repères hors UE. Restreindre est un
# choix — servir 200 pays produirait un filtre inutilisable.
PAYS_SUIVIS = {
    "FR": "France", "DE": "Germany", "IE": "Ireland", "NL": "Netherlands",
    "SE": "Sweden", "NO": "Norway", "FI": "Finland", "DK": "Denmark",
    "ES": "Spain", "IT": "Italy", "PL": "Poland", "BE": "Belgium",
    "GB": "United Kingdom", "US": "United States",
}


def collecter_mix_electrique(annee=None, limite=None):
    """Construit une fiche par pays suivi : part bas-carbone du mix.

    POURQUOI CETTE GRANDEUR PLUTÔT QU'UNE AUTRE. C'est celle qui décide de
    l'empreinte d'un centre à consommation égale, et elle est publiée par
    pays et par année sans hypothèse intermédiaire. Une intensité carbone en
    gCO2/kWh serait plus parlante, mais elle demanderait un facteur par
    filière que cette source ne porte pas — on ne le fabrique pas.
    """
    s = SRC.SOURCES["owid_energie"]
    r = _lire(s["url_donnee"])
    if not r["ok"]:
        return {"ok": False, "source": "owid_energie", **r}

    import csv
    import io
    texte = r["corps"].decode("utf-8", "replace")
    lignes = list(csv.DictReader(io.StringIO(texte)))
    if not lignes:
        return {"ok": False, "source": "owid_energie", "erreur": "csv_vide"}

    inverse = {v: k for k, v in PAYS_SUIVIS.items()}
    # L'ANNÉE N'EST PAS CHOISIE À L'AVANCE : on prend la dernière année où la
    # série est réellement renseignée. Figée dans le code, elle rendrait des
    # fiches vides le jour où la source prend un an de retard.
    dispo = {}
    for L in lignes:
        pays = L.get("country")
        if pays not in inverse:
            continue
        part = L.get("low_carbon_share_elec") or ""
        if not part.strip():
            continue
        try:
            an = int(L.get("year") or 0)
        except ValueError:
            continue
        dispo.setdefault(an, {})[inverse[pays]] = (float(part), L)

    if not dispo:
        return {"ok": False, "source": "owid_energie", "erreur": "serie_absente",
                "message": "La colonne « low_carbon_share_elec » n'est "
                           "renseignée pour aucun pays suivi."}
    an = int(annee) if annee else max(dispo)
    jeu = dispo.get(an) or {}
    fiches = []
    for code, (part, L) in sorted(jeu.items(), key=lambda x: -x[1][0]):
        fiches.append(_fiche_mix(code, part, an, L, s))
        if limite and len(fiches) >= limite:
            break
    return {"ok": True, "source": "owid_energie", "annee": an,
            "fiches": fiches, "retenues": len(fiches),
            "dit": "Dernière année renseignée pour les pays suivis : %d. "
                   "L'année n'est pas figée dans le code — elle est LUE." % an}


def _fiche_mix(code, part, an, L, s):
    nom = PAYS_SUIVIS[code]
    renouv = (L.get("renewables_share_elec") or "").strip()
    fossile = round(100.0 - part, 1)
    if part >= 90:
        lecture = ("Un mix à %.1f %% bas carbone place ce pays parmi ceux où "
                   "l'électricité pèse peu dans l'empreinte d'exploitation "
                   "d'un centre. L'arbitrage s'y déplace vers le carbone "
                   "INCORPORÉ — construction et serveurs — qui devient "
                   "majoritaire dès lors que l'usage est décarboné." % part)
        impact = "structurant"
    elif part >= 60:
        lecture = ("À %.1f %% bas carbone, l'électricité reste un poste "
                   "significatif sans être dominant. C'est la zone où le "
                   "choix du mode de refroidissement se juge sur l'eau ET sur "
                   "le carbone ensemble, l'un ne dominant pas l'autre." % part)
        impact = "structurant"
    else:
        lecture = ("Avec %.1f %% bas carbone — donc environ %.1f %% de "
                   "production fossile — l'électricité domine l'empreinte "
                   "d'exploitation. C'est aussi la configuration où le WUE de "
                   "SOURCE s'écarte le plus du WUE de site : l'eau prélevée "
                   "en amont pour produire le courant devient le terme "
                   "principal, et un refroidissement sec peut y consommer "
                   "plus d'eau qu'une tour." % (part, fossile))
        impact = "structurant"

    return V.normaliser({
        "id": "mix-elec-%s-%d" % (code.lower(), an),
        "titre": "%s — %.1f %% d'électricité bas carbone (%d)" % (nom, part, an),
        "chapeau": "Part de l'électricité produite sans carbone (nucléaire et "
                   "renouvelables) dans le mix national de %s en %d%s."
                   % (nom, an,
                      ", dont %.1f %% de renouvelables" % float(renouv)
                      if renouv else ""),
        "lecture": lecture,
        "lecture_nature": "regle",
        "portee": "Cette part commande l'empreinte d'exploitation à "
                  "consommation égale, et donc l'arbitrage entre implanter "
                  "près de la charge ou près de l'électricité propre. Elle ne "
                  "décide pas seule : le stress hydrique, le prix et le délai "
                  "de raccordement pèsent au moins autant.",
        "incertitude": "Une moyenne ANNUELLE et NATIONALE. Elle ne dit rien de "
                       "l'intensité à l'heure où tourne votre charge, ni du "
                       "mix réellement livré par votre contrat. Un centre "
                       "adossé à un contrat d'achat direct peut s'en écarter "
                       "fortement, dans les deux sens.",
        "sujet": "datacenter",
        "technologies": ["Mix électrique", "Empreinte carbone"],
        "pays": [code],
        "date_fait": "%d-12-31" % an,
        "source_cle": "owid_energie",
        "source_url": s["url_humaine"],
        "statut": "verifiee_source_primaire",
        "impact": impact,
        "horizon": "constate",
        "signe_par": "Collecte automatique — règles publiées dans ingestion.py",
    })["fiche"]


# ═══════════════════════════════════════════════════════════════════════════

# ── LA TABLE DES COLLECTEURS, ET POURQUOI ELLE EST ICI ────────────────────
# Elle était écrite en clair dans la boucle de `collecter_tout`. Rien ne
# permettait alors de savoir, DE L'EXTÉRIEUR, quelles sources du registre sont
# réellement lues — et le registre en annonçait neuf quand le corpus en
# employait quatre, sans que rien ne le signale. Hissée ici, la même table
# sert à collecter ET à répondre à la question « cette source est-elle lue ? ».
#
# UNE SEULE TABLE, DEUX USAGES : la déclaration ne peut plus diverger de la
# réalité, puisqu'elle EST la réalité. Une seconde liste écrite à côté aurait
# recommencé la dérive qu'on répare.
#
# La clé de gauche est la clé de source du registre — sauf `mitre_atlas_tech`,
# qui lit la même source qu'`mitre_atlas` sous un autre angle : la
# correspondance est donnée par SOURCE_DU_COLLECTEUR.
def _table_collecteurs(limite_kev, limite_mix):
    return (("cisa_kev", lambda: collecter_kev(limite=limite_kev)),
            ("mitre_attack_ics", lambda: collecter_attack_ics()),
            ("mitre_atlas", lambda: collecter_atlas()),
            ("mitre_atlas_tech", lambda: collecter_atlas_techniques()),
            ("owid_energie", lambda: collecter_mix_electrique(limite=limite_mix)),
            # BRANCHÉE APRÈS COUP, et c'est le sujet : elle était au registre
            # depuis le premier jour sans qu'aucun collecteur ne la lise.
            ("electricity_maps", lambda: collecter_electricity_maps()),
            # La rubrique IA ne portait que des INCIDENTS (ATLAS). OWASP
            # apporte l'autre face : ce qui est reconnu comme risque,
            # indépendamment de ce qui a été observé.
            ("owasp_llm", lambda: collecter_owasp_llm()))


SOURCE_DU_COLLECTEUR = {"mitre_atlas_tech": "mitre_atlas"}


def sources_collectees():
    """Les clés de source qu'un collecteur lit RÉELLEMENT.

    Dérivée de la table ci-dessus, jamais recopiée : c'est ce qui empêche le
    registre d'annoncer une source que plus personne ne lit.
    """
    return {SOURCE_DU_COLLECTEUR.get(nom, nom)
            for nom, _ in _table_collecteurs(0, None)}


def collecter_tout(limite_kev=30, limite_mix=None):
    """Lance les collecteurs et rend le corpus, avec le journal de ce qui a
    échoué. Un échec ne fait pas tomber les autres : une source injoignable
    ne doit pas priver le site de celles qui répondent."""
    corpus, journal = [], []
    for nom, fn in _table_collecteurs(limite_kev, limite_mix):
        try:
            r = fn()
        except Exception as e:  # noqa: BLE001
            journal.append({"source": nom, "ok": False, "erreur": "exception",
                            "message": str(e)})
            continue
        if r.get("ok"):
            corpus.extend(r["fiches"])
            journal.append({"source": nom, "ok": True,
                            "retenues": r.get("retenues"), "dit": r.get("dit")})
        else:
            journal.append({"source": nom, "ok": False,
                            "erreur": r.get("erreur"),
                            "message": r.get("message")})
    # LES RELATIONS QUI TRAVERSENT DEUX COLLECTEURS s'établissent ici, une
    # fois le corpus réuni : une étude de cas ATLAS et la technique qu'elle
    # emploie sont servies par deux fonctions différentes, et aucune des deux
    # ne peut savoir seule ce que l'autre a retenu.
    n = _relier_atlas(corpus)
    journal.append({"source": "croisement_atlas", "ok": True, "retenues": n,
                    "dit": "%d relation(s) étude de cas ↔ technique, DÉCLARÉES "
                           "par ATLAS dans ses propres étapes de procédure. "
                           "Aucune n'est déduite : chacune porte la phrase par "
                           "laquelle la source décrit l'étape." % n})

    # LE PONT ENTRE LES DEUX NATURES DE LA RUBRIQUE. ATLAS documente ce qui
    # EST ARRIVÉ, OWASP ce qui EST RECONNU comme menaçant ; jusqu'ici les deux
    # cohabitaient sans se toucher. OWASP publie la correspondance lui-même,
    # dans sa section des cadres apparentés — ce site la reprend, il ne
    # l'invente pas.
    ajoutees, perdues = completer_atlas_techniques(corpus)
    m = relier_owasp_atlas(corpus)
    journal.append({"source": "croisement_owasp_atlas", "ok": True,
                    "retenues": m,
                    "dit": "%d correspondance(s) risque reconnu ↔ technique "
                           "observée, DÉCLARÉES par OWASP%s.%s Une "
                           "correspondance vers une technique que ce site ne "
                           "sert pas n'est pas posée : elle donnerait un lien "
                           "mort."
                           % (m,
                              " ; %d technique(s) servies parce qu'OWASP les "
                              "nomme, et non parce qu'elles ont été révisées "
                              "récemment" % ajoutees if ajoutees else "",
                              " %d référence(s) restent introuvables au "
                              "référentiel." % perdues if perdues else "")})

    return {"ok": True, "corpus": corpus, "journal": journal,
            "collecte_le": datetime.now(timezone.utc).isoformat(timespec="seconds")}


def _relier_atlas(corpus, atlas=None):
    """Rattache chaque étude de cas ATLAS aux techniques qu'elle EMPLOIE.

    POURQUOI C'EST LE MEILLEUR LIEN DU SITE. ATLAS ne se contente pas de dire
    que la technique a servi : chaque étape de `procedure` porte la PHRASE qui
    décrit ce qui a été fait, dans ce cas précis. Le motif du rapprochement
    n'est donc pas une catégorie (« même technologie ») mais le récit de
    l'étape — et il est de la source, pas de nous.

    Rien n'est déduit ici : la correspondance étape → technique est un champ
    du fichier ATLAS. Ce module ne retient que les relations dont les DEUX
    extrémités sont servies, pour ne produire aucun lien mort.

    `atlas` permet de fournir le document plutôt que de l'aller chercher.
    C'est ce qui rend la règle « une seule relation par couple » vérifiable :
    aucune étude de cas du référentiel n'emploie aujourd'hui DEUX FOIS une
    technique que ce site sert, si bien qu'un contrôle branché sur les données
    réelles passerait au vert sans rien garder du tout.
    """
    d, err = (atlas, None) if atlas is not None else _atlas_charge()
    if err:
        return 0
    par_id = {f.get("id"): f for f in corpus if f.get("id")}
    n = 0
    for c in (d.get("case-studies") or []):
        cas = par_id.get("atlas-%s" % str(c.get("id")).lower().replace(".", "-"))
        if not cas:
            continue
        vus = set()
        for p in (c.get("procedure") or []):
            cle = "atlas-tech-%s" % str(p.get("technique")).lower().replace(".", "-")
            tech = par_id.get(cle)
            # UNE SEULE RELATION PAR COUPLE : une technique employée à quatre
            # étapes du même incident donnerait quatre fois le même lien, et
            # le lecteur y lirait quatre faits là où il n'y en a qu'un.
            if not tech or cle in vus:
                continue
            vus.add(cle)
            phrase = _abrege(_propre_stix(p.get("description")), 260)
            for de, vers in ((cas, tech), (tech, cas)):
                de.setdefault("relations", []).append({
                    "vers": vers["id"], "titre": vers["titre"],
                    "nature": "procedure", "nature_nom": "employée dans",
                    "dit": "ATLAS décrit ainsi cette étape de l'incident : "
                           "« %s »" % phrase,
                    # LES RÉFÉRENCES DU CAS, pas celles de l'étape : ATLAS
                    # documente ses sources au niveau de l'étude.
                    "citations": [r.get("title") for r in (c.get("references") or [])
                                  if r.get("title")][:2],
                })
            n += 1
    return n


def sante():
    return {
        "module": "ingestion", "version": VERSION,
        "collecteurs": 7,
        "editeurs_industriels": len(EDITEURS_INDUSTRIELS),
        "indices_produit": len(INDICES_PRODUIT_INDUSTRIEL),
        "pays_suivis": len(PAYS_SUIVIS),
        "modeles_de_langage": 0,
        "portee": "Transforme une source ouverte en fiches. La lecture "
                  "critique est DÉRIVÉE par règles publiées ; aucun modèle de "
                  "langage n'intervient, pour que deux collectes rendent le "
                  "même texte.",
    }


# ═══════════════════════════════════════════════════════════════════════════
#  COLLECTEUR 3 — MITRE ATT&CK for ICS : les modes opératoires OBSERVÉS
#
#  POURQUOI CE COLLECTEUR EXISTE. Le catalogue KEV, mesuré, ne porte que neuf
#  entrées d'éditeurs industriels sur mille six cent soixante-quatorze : il
#  décrit surtout un parc bureautique. Une veille de cybersécurité
#  INDUSTRIELLE qui s'y limiterait parlerait d'autre chose que son sujet.
#  ATT&CK ICS, lui, ne recense pas des failles mais des MODES OPÉRATOIRES
#  observés sur des installations réelles — c'est la matière qui manque.
#
#  CE QU'UNE FICHE DE GROUPE N'EST PAS : une attribution. ATT&CK décrit ce
#  qu'un ensemble d'activités fait, pas qui le commandite. Le module ne
#  franchit pas ce pas, et le dit dans chaque fiche.
# ═══════════════════════════════════════════════════════════════════════════

def _abrege(t, n):
    """Coupe sur un MOT, jamais au milieu : une troncature en plein mot
    signale un texte que personne n'a relu."""
    t = str(t or "")
    if len(t) <= n:
        return t
    coupe = t[:n].rsplit(" ", 1)[0].rstrip(" ,;:.")
    return coupe + "…"


def _propre_stix(t):
    """Nettoie une description STIX de son balisage.

    ATT&CK écrit ses descriptions en Markdown et y insère ses références
    sous la forme « (Citation: …) ». Servies telles quelles, elles
    affichaient « [APT38](https://attack.mitre.org/groups/G0082) is a North
    Korean… (Citation: CISA AA20-239A) » — du balisage brut sur une page
    publiée, ce qui se lit comme un contenu non relu.

    Le lien n'est pas perdu : chaque fiche porte l'adresse ATT&CK de l'objet
    dans son bloc source. Ce sont les liens INTERNES au texte qui partent.
    """
    t = str(t or "")
    t = re.sub(r"\(Citation:[^)]*\)", "", t)          # marqueurs de référence
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)     # [libellé](adresse)
    t = re.sub(r"<[^>]+>", "", t)                     # balises résiduelles
    t = t.replace("`", "")
    return " ".join(t.split())


def _stix_date(o):
    for c in ("modified", "created"):
        v = str(o.get(c) or "")[:10]
        if re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            return v
    return date.today().isoformat()


def collecter_attack_ics(limite_groupes=10, limite_logiciels=10):
    """Fiches sur les groupes et les logiciels documentés contre l'ICS."""
    s = SRC.SOURCES["mitre_attack_ics"]
    r = _lire(s["url_donnee"])
    if not r["ok"]:
        return {"ok": False, "source": "mitre_attack_ics", **r}
    try:
        d = json.loads(r["corps"])
    except ValueError as e:
        return {"ok": False, "source": "mitre_attack_ics",
                "erreur": "stix_illisible", "message": str(e)}

    objets = d.get("objects", [])
    vivant = lambda o: not o.get("revoked") and not o.get("x_mitre_deprecated")
    version = next((o.get("x_mitre_version") for o in objets
                    if o.get("type") == "x-mitre-collection"), "?")
    techniques = [o for o in objets
                  if o.get("type") == "attack-pattern" and vivant(o)]
    groupes = [o for o in objets if o.get("type") == "intrusion-set" and vivant(o)]
    logiciels = [o for o in objets if o.get("type") == "malware" and vivant(o)]

    def _url(o):
        for ref in o.get("external_references", []):
            if ref.get("source_name") == "mitre-attack" and ref.get("url"):
                return ref["url"]
        return s["url_humaine"]

    def _ident(o):
        for ref in o.get("external_references", []):
            if ref.get("source_name") == "mitre-attack":
                return ref.get("external_id") or ""
        return ""

    fiches = []
    for o in sorted(groupes, key=_stix_date, reverse=True)[:limite_groupes]:
        ident = _ident(o)
        fiches.append(V.normaliser({
            "id": "attack-ics-groupe-%s" % (ident or o["id"][-8:]).lower(),
            "titre": "%s — mode opératoire documenté contre l'ICS%s"
                     % (o.get("name"), " (%s)" % ident if ident else ""),
            "chapeau": _abrege(_propre_stix(o.get("description")), 330),
            "lecture": "ATT&CK ICS décrit ici un ensemble d'activités OBSERVÉES "
                       "sur des installations industrielles, pas une "
                       "attribution : le référentiel dit ce qui a été fait, "
                       "jamais qui l'a commandité. Sa présence au référentiel "
                       "signifie que les techniques employées sont documentées "
                       "et donc détectables — c'est le seul point qui vous "
                       "concerne directement, et il se traduit en règles de "
                       "supervision, pas en communiqué.",
            "lecture_nature": "regle",
            "portee": "À confronter à votre cartographie de zones et conduits : "
                      "les techniques rattachées à ce mode opératoire désignent "
                      "des points de détection concrets. Un plan de supervision "
                      "qui ne couvre aucune des techniques documentées pour "
                      "votre filière surveille ce qui est facile à voir, pas ce "
                      "qui arrive.",
            "incertitude": "Le référentiel recense ce qui a été observé ET "
                           "publié. Ce qui n'a pas été détecté, ou l'a été sans "
                           "être documenté, n'y figure pas — l'absence d'une "
                           "technique ne vaut donc pas absence de risque.",
            "sujet": "cyber_industriel",
            "technologies": ["ATT&CK ICS", "Mode opératoire"],
            "pays": [],
            "date_fait": _stix_date(o),
            "source_cle": "mitre_attack_ics",
            "source_url": _url(o),
            "statut": "verifiee_source_primaire",
            "impact": "structurant",
            "horizon": "constate",
            "signe_par": "Collecte automatique — règles publiées dans ingestion.py",
            # Retiré après établissement des relations : c'est une clé de
            # rapprochement, pas une information pour le lecteur.
            "stix_id": o["id"],
        })["fiche"])

    for o in sorted(logiciels, key=_stix_date, reverse=True)[:limite_logiciels]:
        ident = _ident(o)
        fiches.append(V.normaliser({
            "id": "attack-ics-logiciel-%s" % (ident or o["id"][-8:]).lower(),
            "titre": "%s — logiciel malveillant documenté contre l'ICS%s"
                     % (o.get("name"), " (%s)" % ident if ident else ""),
            "chapeau": _abrege(_propre_stix(o.get("description")), 330),
            "lecture": "Un logiciel inscrit au référentiel ICS a été employé "
                       "contre des systèmes d'automatisation, pas seulement "
                       "contre de la bureautique. La distinction commande la "
                       "réponse : sur un procédé qui tourne, l'isolement d'un "
                       "poste n'est pas une mesure neutre, et la remise en "
                       "service se prépare avant l'incident, pas pendant.",
            "lecture_nature": "regle",
            "portee": "À verser au plan de continuité OT plutôt qu'au seul plan "
                      "cyber : ce qui se joue est la capacité à redémarrer un "
                      "procédé dans un état sûr, ce qu'aucune restauration de "
                      "données ne fait à elle seule.",
            "incertitude": "La description dit ce que le logiciel PEUT faire, "
                           "sur les cas analysés. Elle ne dit ni sa prévalence, "
                           "ni s'il circule encore, ni s'il atteindrait votre "
                           "architecture compte tenu de sa segmentation.",
            "sujet": "cyber_industriel",
            "technologies": ["ATT&CK ICS", "Logiciel malveillant"],
            "pays": [],
            "date_fait": _stix_date(o),
            "source_cle": "mitre_attack_ics",
            "source_url": _url(o),
            "statut": "verifiee_source_primaire",
            "impact": "structurant",
            "horizon": "constate",
            "signe_par": "Collecte automatique — règles publiées dans ingestion.py",
            # Retiré après établissement des relations : c'est une clé de
            # rapprochement, pas une information pour le lecteur.
            "stix_id": o["id"],
        })["fiche"])

    # ── LES RELATIONS QUE LA SOURCE DÉCLARE ELLE-MÊME ─────────────────────
    # C'EST LA SEULE ESPÈCE DE LIEN QUI N'ENGAGE PAS LE CABINET. Tous les
    # autres rapprochements du site sont des règles que J'AI écrites : elles
    # se défendent, mais elles sont de moi. Ici, MITRE publie des objets
    # `relationship` — 1 667 au référentiel — qui affirment qu'un groupe
    # EMPLOIE tel logiciel. Reprendre cette affirmation n'est pas inférer,
    # c'est citer.
    #
    # LA CHAÎNE DE PREUVE RESTE ENTIÈRE : chaque relation porte les références
    # externes sur lesquelles MITRE s'appuie, et elles sont transmises telles
    # quelles. Un lecteur peut donc remonter du rapprochement affiché jusqu'au
    # rapport d'origine, sans passer par ce site.
    #
    # SEULES LES RELATIONS ENTRE FICHES SERVIES SONT RETENUES. Pointer vers
    # une entité dont ce site ne publie rien donnerait un lien mort — et le
    # référentiel en compte des centaines qui sortent de ce que nous servons.
    par_stix = {}
    for f in fiches:
        if f.get("stix_id"):
            par_stix[f["stix_id"]] = f
    noms = {o["id"]: o.get("name") for o in objets if o.get("id")}
    natures = {
        "uses": ("emploie", "%s emploie %s, selon le référentiel."),
        "attributed-to": ("est rattaché à", "%s est rattaché à %s par le "
                                            "référentiel."),
    }
    relations = 0
    for o in objets:
        if o.get("type") != "relationship" or not vivant(o):
            continue
        a, b = par_stix.get(o.get("source_ref")), par_stix.get(o.get("target_ref"))
        nat = natures.get(o.get("relationship_type"))
        if not (a and b and nat):
            continue
        verbe, gabarit = nat
        citations = [x.get("source_name") for x in o.get("external_references", [])
                     if x.get("source_name")]
        # LA PHRASE EST LA MÊME DES DEUX CÔTÉS, et c'est voulu : « Sandworm
        # Team emploie Industroyer » est ce que la source affirme, quel que
        # soit le bout par lequel on arrive. La retourner en « Industroyer est
        # employé par… » serait déjà une reformulation, donc un début
        # d'interprétation.
        phrase = gabarit % (noms.get(o["source_ref"], "?"),
                            noms.get(o["target_ref"], "?"))
        for de, vers in ((a, b), (b, a)):
            de.setdefault("relations", []).append({
                "vers": vers["id"], "titre": vers["titre"],
                "nature": o["relationship_type"], "nature_nom": verbe,
                "dit": phrase, "citations": citations[:3],
            })
        relations += 1

    # Le champ technique de rapprochement ne regarde pas le lecteur : il sort
    # de la fiche une fois les relations établies.
    for f in fiches:
        f.pop("stix_id", None)

    return {"ok": True, "source": "mitre_attack_ics", "version_referentiel": version,
            "fiches": fiches, "retenues": len(fiches),
            "relations_declarees": relations,
            "dit": "ICS ATT&CK v%s — %d techniques actives au référentiel ; %d "
                   "fiche(s) servies sur %d groupes et %d logiciels documentés, "
                   "reliées par %d relation(s) que le référentiel DÉCLARE "
                   "lui-même. Les fiches portent les entrées les plus "
                   "récemment révisées."
                   % (version, len(techniques), len(fiches), len(groupes),
                      len(logiciels), relations)}


# ═══════════════════════════════════════════════════════════════════════════
#  COLLECTEUR 4 — MITRE ATLAS : les attaques OBSERVÉES contre des systèmes d'IA
#
#  POURQUOI CE COLLECTEUR EST LE PLUS UTILE DES QUATRE. Sur l'IA, presque
#  tout ce qui circule est soit de la démonstration de laboratoire, soit du
#  communiqué d'éditeur. ATLAS documente des INCIDENTS RÉELS, datés, avec leur
#  cible nommée et le déroulé technique — c'est la seule base publique qui le
#  fasse. Une veille « systèmes d'IA » qui n'en parlerait pas raconterait des
#  intentions.
#
#  LA DATE EST CELLE DE L'INCIDENT, PAS DE SA PUBLICATION. ATLAS porte une
#  granularité déclarée (`incident-date-granularity`) : quand elle vaut YEAR,
#  le jour affiché est une convention, pas une observation. La fiche le dit
#  plutôt que d'afficher un 1er janvier qui se lirait comme une date exacte.
# ═══════════════════════════════════════════════════════════════════════════

def _atlas_charge():
    s = SRC.SOURCES["mitre_atlas"]
    r = _lire(s["url_donnee"])
    if not r["ok"]:
        return None, {"ok": False, "source": "mitre_atlas", **r}
    try:
        import yaml
    except ImportError:
        return None, {"ok": False, "source": "mitre_atlas", "erreur": "pyyaml_absent",
                      "message": "PyYAML n'est pas installé : ATLAS est publié "
                                 "en YAML. `pip install pyyaml`."}
    try:
        return yaml.safe_load(r["corps"].decode("utf-8", "replace")), None
    except Exception as e:  # noqa: BLE001
        return None, {"ok": False, "source": "mitre_atlas",
                      "erreur": "yaml_illisible", "message": str(e)}


def collecter_atlas(limite_cas=18):
    """Une fiche par étude de cas ATLAS — un incident réel, daté, contre un
    système d'IA en production."""
    d, err = _atlas_charge()
    if err:
        return err
    s = SRC.SOURCES["mitre_atlas"]
    version = str(d.get("version") or "?")
    cas = [c for c in (d.get("case-studies") or []) if c.get("id")]

    def _quand(c):
        v = c.get("incident-date")
        return str(v)[:10] if v else "0000-00-00"

    cas.sort(key=_quand, reverse=True)
    fiches = []
    for c in cas[:limite_cas]:
        iso = _quand(c)
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", iso):
            continue
        gran = str(c.get("incident-date-granularity") or "").upper()
        procedures = c.get("procedure") or []
        cible = V._texte(c.get("target") or "")
        acteur = V._texte(c.get("actor") or "")
        typ = str(c.get("case-study-type") or "").lower()

        # LA GRANULARITÉ EST DITE. Un « 1er janvier » issu d'une date connue à
        # l'année près se lirait comme une observation au jour près.
        precision = {
            "YEAR": "L'incident n'est daté qu'à l'ANNÉE par la source ; le jour "
                    "affiché est une convention de classement, pas une "
                    "observation.",
            "MONTH": "L'incident n'est daté qu'au MOIS par la source ; le jour "
                     "affiché est une convention de classement.",
        }.get(gran, "")

        lecture = (
            "ATLAS documente ici un incident %s contre un système d'IA en "
            "production%s. Le déroulé est décomposé en %d étape(s) rattachées "
            "aux tactiques du référentiel : ce n'est pas un récit, c'est une "
            "séquence technique reproductible côté défense, donc traduisible "
            "en points de contrôle. %s"
            % ("réel" if typ == "incident" else "documenté (exercice ou "
               "démonstration cadrée)",
               " visant %s" % cible if cible else "",
               len(procedures),
               precision or "La date est donnée au jour par la source.")
        ).strip()

        if typ == "exercise":
            lecture += (" Attention à la nature du cas : c'est un EXERCICE, "
                        "pas une attaque subie. Il établit qu'une chose est "
                        "faisable, pas qu'elle a été faite contre un tiers.")

        # L'ENTITÉ NOMMÉE PAR LA SOURCE, AVEC SON RÔLE — en toutes lettres.
        # Le champ `actor` d'ATLAS désigne tantôt l'attaquant, tantôt l'équipe
        # qui a conduit l'exercice. Cette ambiguïté interdit d'en faire une
        # clé de tri ou de lien (voir plus bas), mais elle ne justifie pas de
        # jeter l'information : la PHRASE, elle, peut dire lequel des deux
        # c'est, puisque `case-study-type` le distingue. Ce qu'un libellé
        # unique ne peut pas porter, une phrase le porte.
        if acteur and "unknown" not in acteur.lower():
            lecture += (" La source nomme %s %s."
                        % ("l'équipe qui a conduit l'exercice :"
                           if typ == "exercise" else
                           "l'entité à laquelle elle rattache l'incident :",
                           acteur))
        elif acteur:
            lecture += (" La source ne nomme aucune entité : elle inscrit "
                        "« %s », c'est-à-dire qu'elle ne sait pas." % acteur)

        fiches.append(V.normaliser({
            "id": "atlas-%s" % str(c["id"]).lower().replace(".", "-"),
            "titre": "%s — %s" % (V._texte(c.get("name")), c["id"]),
            "chapeau": _abrege(_propre_stix(c.get("summary")), 330),
            "lecture": lecture,
            "lecture_nature": "regle",
            "portee": "À confronter à vos propres usages d'IA : si un modèle "
                      "décide, filtre ou authentifie chez vous, la question "
                      "n'est plus de savoir si ce type d'attaque existe — "
                      "ATLAS l'établit — mais si votre chaîne d'entraînement "
                      "et votre interface d'inférence y sont exposées. C'est "
                      "un point à porter au registre des systèmes d'IA exigé "
                      "par le règlement européen, pas seulement au plan cyber.",
            "incertitude": "ATLAS recense ce qui a été observé ET publié : "
                           "l'absence d'un cas ne vaut pas absence d'incident. "
                           "La base ne dit ni la fréquence de ces attaques, ni "
                           "leur coût, ni si votre configuration y est "
                           "vulnérable."
                           + (" " + precision if precision else ""),
            "sujet": "sia",
            # L'ACTEUR N'EST NI UN ÉDITEUR NI UNE TECHNOLOGIE — il a été retiré
            # des deux, et voici pourquoi c'est écrit plutôt que silencieux.
            #
            # CE QU'IL FAISAIT. Il alimentait `editeur`, qui fonde le lien
            # « Même éditeur » ; or ce lien annonce au lecteur « même contrat,
            # même interlocuteur, même fenêtre de maintenance » — phrase
            # entièrement fausse appliquée à un attaquant. Il alimentait aussi
            # `technologies`, ce qui offrait « Jamieson O'Reilly » et
            # « Backslash Security Research Team » dans le filtre par
            # TECHNOLOGIE, et faisait des DEUX seuls liens forts du corpus des
            # liens fondés sur « Unknown Threat Actor » — c'est-à-dire sur
            # l'aveu de la source qu'elle ne sait pas qui c'est.
            #
            # POURQUOI PAS UN CHAMP « ACTEUR » DÉDIÉ. Parce que la donnée est
            # hétérogène : mesuré sur les 57 cas, `actor` nomme tantôt
            # l'attaquant (« lkmanka58 »), tantôt le CHERCHEUR qui a conduit
            # l'exercice (« HiddenLayer », « DepthFirst »). Un lien « même
            # acteur » signifierait donc parfois « même attaquant », parfois
            # « même équipe de recherche », sous un seul libellé. C'est la
            # faute pour laquelle le lien « technique et faille » a été retiré
            # du croisement, et elle ne vaut pas mieux ici.
            #
            # CE QU'IL FAUDRAIT POUR LE RÉTABLIR : que la source distingue le
            # rôle de l'entité nommée. `case-study-type` distingue l'incident
            # de l'exercice, mais pas dans le champ `actor` lui-même — il
            # faudrait le déduire, donc en faire un jugement du cabinet, à
            # déclarer comme tel.
            "editeur": None,
            "technologies": ["MITRE ATLAS", "Sécurité des systèmes d'IA"]
                            + (["Incident réel"] if typ == "incident" else []),
            "pays": [],
            "date_fait": iso,
            "source_cle": "mitre_atlas",
            "source_url": "https://atlas.mitre.org/studies/%s" % c["id"],
            "statut": "verifiee_source_primaire",
            # UN INCIDENT RÉEL PÈSE PLUS QU'UN EXERCICE, et le référentiel
            # distingue les deux : ne pas s'en servir reviendrait à mettre une
            # démonstration cadrée au même rang qu'une attaque subie.
            "impact": "rupture" if typ == "incident" else "structurant",
            "horizon": "constate",
            "signe_par": "Collecte automatique — règles publiées dans ingestion.py",
        })["fiche"])

    return {"ok": True, "source": "mitre_atlas", "version_referentiel": version,
            "fiches": fiches, "retenues": len(fiches),
            "dit": "ATLAS v%s — %d fiche(s) servies, les plus récentes de %d "
                   "études de cas datées. Le référentiel distingue les "
                   "incidents subis des exercices ; les fiches le reprennent."
                   % (version, len(fiches), len(cas))}


def collecter_atlas_techniques(limite=8):
    """Les techniques ATLAS les plus récemment révisées — le volet « IA »
    proprement dit : ce qu'on sait faire contre un modèle."""
    d, err = _atlas_charge()
    if err:
        return err
    s = SRC.SOURCES["mitre_atlas"]
    version = str(d.get("version") or "?")
    mat = (d.get("matrices") or [{}])[0]
    tech = [t for t in (mat.get("techniques") or []) if t.get("id")]
    tact = {t.get("id"): t.get("name") for t in (mat.get("tactics") or [])}
    # Le référentiel entier, indexé : une sous-technique a besoin de son
    # parent pour porter son nom complet et sa tactique.
    par_ref = {t["id"]: t for t in tech}

    def _quand(t):
        v = t.get("modified_date") or t.get("created_date")
        return str(v)[:10] if v else "0000-00-00"

    tech.sort(key=_quand, reverse=True)
    fiches = []
    for t in tech:
        iso = _quand(t)
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", iso):
            continue
        fiches.append(_fiche_technique_atlas(t, tact, iso, par_ref))
        if len(fiches) >= limite:
            break

    return {"ok": True, "source": "mitre_atlas", "version_referentiel": version,
            "fiches": fiches, "retenues": len(fiches),
            "dit": "ATLAS v%s — %d technique(s) servies sur %d au référentiel, "
                   "les plus récemment révisées." % (version, len(fiches), len(tech))}


def _nom_technique_atlas(t, par_ref):
    """Le nom COMPLET d'une technique, sous-technique comprise.

    DÉFAUT CONSTATÉ EN SERVICE, apparu avec les sous-techniques qu'OWASP
    désigne. ATLAS ne nomme qu'un SUFFIXE : « AML.T0051.000 » s'appelle
    « Direct », et « AML.T0024.001 » s'appelle « Invert AI Model ». Servies
    telles quelles, elles produisaient des fiches intitulées « Direct —
    technique documentée contre l'IA » : un titre qui ne dit rien, et qui ne
    dit surtout pas de quoi il est le cas particulier.

    Le champ `specializes` porte le parent. Le nom rendu est donc « LLM Prompt
    Injection: Direct » — celui-là même qu'OWASP emploie quand il cite la
    technique, ce qui n'est pas un hasard : c'est ainsi qu'elle se lit.
    """
    nom = V._texte(t.get("name"))
    parent = par_ref.get(t.get("specializes")) if t.get("specializes") else None
    if parent and V._texte(parent.get("name")):
        return "%s : %s" % (V._texte(parent["name"]), nom)
    return nom


def _fiche_technique_atlas(t, tact, iso, par_ref=None):
    """La fiche d'une technique ATLAS.

    Extraite de son collecteur parce que DEUX passes la construisent : celle
    qui sert les techniques les plus récemment révisées, et celle qui complète
    avec les techniques que nos propres sources désignent. Deux copies du même
    texte auraient divergé au premier ajustement.
    """
    par_ref = par_ref or {}
    # UNE SOUS-TECHNIQUE N'A PAS DE TACTIQUE PROPRE : elle hérite celle de son
    # parent. Sans cet héritage, sa lecture disait « rattachée à une tactique
    # du référentiel » — une phrase qui remplit la place sans rien apprendre.
    tactiques = t.get("tactics") or []
    if not tactiques and t.get("specializes"):
        tactiques = (par_ref.get(t["specializes"]) or {}).get("tactics") or []
    noms = [tact.get(x) for x in tactiques if tact.get(x)]
    return V.normaliser({
            "id": "atlas-tech-%s" % str(t["id"]).lower().replace(".", "-"),
            "titre": "%s — technique documentée contre l'IA (%s)"
                     % (_nom_technique_atlas(t, par_ref), t["id"]),
            "chapeau": _abrege(_propre_stix(t.get("description")), 330),
            "lecture": "Technique rattachée à %s. Une technique au référentiel "
                       "signifie qu'elle a été employée ou démontrée, donc "
                       "qu'elle est descriptible et détectable — c'est ce qui "
                       "la sépare d'un risque théorique. Elle se traduit en "
                       "contrôle sur la chaîne d'entraînement, sur l'accès au "
                       "modèle ou sur l'interface d'inférence, selon la "
                       "tactique qu'elle sert."
                       % (", ".join("« %s »" % n for n in noms) if noms
                          else "une tactique du référentiel"),
            "lecture_nature": "regle",
            "portee": "Sert à instruire la question que l'AI Act pose sans y "
                      "répondre : quelles mesures de robustesse et de "
                      "cybersécurité sont appropriées pour ce système. Une "
                      "liste de techniques documentées est un point de départ "
                      "défendable ; « nous avons sécurisé le modèle » n'en est "
                      "pas un.",
            "incertitude": "Le référentiel dit ce qui est faisable, pas ce qui "
                           "est fréquent ni ce qui vous vise. Il ne hiérarchise "
                           "pas les techniques entre elles et ne dit pas "
                           "lesquelles s'appliquent à votre architecture.",
            "sujet": "ia",
            "technologies": ["MITRE ATLAS"] + noms[:2],
            "pays": [],
            "date_fait": iso,
            "source_cle": "mitre_atlas",
            "source_url": "https://atlas.mitre.org/techniques/%s" % t["id"],
            "statut": "verifiee_source_primaire",
            "impact": "structurant",
            "horizon": "constate",
            "signe_par": "Collecte automatique — règles publiées dans ingestion.py",
        })["fiche"]


# ═══════════════════════════════════════════════════════════════════════════
#  COLLECTEUR 6 — ELECTRICITY MAPS : le facteur d'émission, avec SA source
#
#  POURQUOI CETTE SOURCE MÉRITAIT D'ÊTRE BRANCHÉE. Elle était au registre
#  depuis le premier jour, avec son bouton « Sonder » qui prouvait qu'elle
#  répond — et AUCUN collecteur ne la lisait. Le registre annonçait donc neuf
#  sources quand le corpus en employait quatre : c'est le genre d'écart qui ne
#  se voit pas de l'extérieur et qui vide le registre de son sens.
#
#  CE QU'ELLE APPORTE QUE LES AUTRES N'ONT PAS. Chaque facteur d'émission y
#  porte SA PROPRE SOURCE et SA DATE — « EU-ETS 2025, ENTSO-E 2025 » pour le
#  charbon français, « UNECE 2022 » pour l'hydraulique. Ailleurs sur ce site,
#  une valeur porte la source du jeu de données entier ; ici, elle porte la
#  sienne. C'est la granularité qu'on aimerait partout.
#
#  ELLE COMPLÈTE OWID SANS LE DOUBLER. OWID donne la PART bas-carbone du mix,
#  Electricity Maps donne le FACTEUR D'ÉMISSION par filière. Deux grandeurs
#  différentes sur le même pays : c'est précisément ce qui fait un croisement
#  utile — et les premiers liens « même pays » du site.
# ═══════════════════════════════════════════════════════════════════════════

# Les filières qui décident de l'empreinte d'un centre de données. On ne sert
# pas les dix modes du fichier : le stockage et la décharge de batterie sont
# des grandeurs dérivées du mix, les servir ferait compter deux fois.
FILIERES_EM = ("coal", "gas", "oil", "nuclear", "hydro", "wind", "solar",
               "biomass", "geothermal")
FILIERES_EM_NOM = {
    "coal": "charbon", "gas": "gaz", "oil": "fioul", "nuclear": "nucléaire",
    "hydro": "hydraulique", "wind": "éolien", "solar": "solaire",
    "biomass": "biomasse", "geothermal": "géothermie",
}
_EM_GABARIT = ("https://raw.githubusercontent.com/electricitymaps/"
               "electricitymaps-contrib/master/config/zones/%s.yaml")


def _em_dernier(entrees):
    """La valeur la PLUS RÉCENTE d'une série, avec sa date et sa source.

    Le fichier porte l'historique : prendre la première entrée servirait un
    facteur de 2014 pour un pays dont le mix a changé depuis. On prend la
    dernière datée, et on garde la date pour que la fiche la porte.
    """
    if isinstance(entrees, dict):
        entrees = [entrees]
    if not isinstance(entrees, list) or not entrees:
        return None
    datees = [e for e in entrees if isinstance(e, dict) and e.get("value") is not None]
    if not datees:
        return None
    return sorted(datees, key=lambda e: str(e.get("datetime") or ""))[-1]


def collecter_electricity_maps(pays=None, limite=None):
    """Une fiche par zone : les facteurs d'émission en cycle de vie.

    LE CYCLE DE VIE PLUTÔT QUE LE DIRECT, et c'est un choix qui se discute :
    le facteur « direct » ne compte que la combustion, le « cycle de vie »
    ajoute la construction, le combustible et le démantèlement. Pour un
    centre de données, dont l'arbitrage porte sur des décennies, le second
    est le seul qui compare l'éolien au gaz sans avantager l'éolien par
    omission. La fiche dit lequel elle emploie.
    """
    codes = list(pays or PAYS_SUIVIS)
    if limite:
        codes = codes[:limite]
    s = SRC.SOURCES["electricity_maps"]
    try:
        import yaml
    except ImportError:
        return {"ok": False, "source": "electricity_maps", "erreur": "pyyaml_absent",
                "message": "PyYAML n'est pas installé : les zones sont en YAML."}

    fiches, muettes, injoignables = [], [], []
    for code in codes:
        r = _lire(_EM_GABARIT % code, delai=30)
        if not r["ok"]:
            injoignables.append(code)
            continue
        try:
            z = yaml.safe_load(r["corps"].decode("utf-8", "replace")) or {}
        except Exception:  # noqa: BLE001
            injoignables.append(code)
            continue

        lc = ((z.get("emissionFactors") or {}).get("lifecycle") or {})
        retenus = {}
        for f in FILIERES_EM:
            d = _em_dernier(lc.get(f))
            if d:
                retenus[f] = d
        if not retenus:
            # UNE ZONE SANS FACTEUR N'EST PAS UNE ERREUR : certaines zones du
            # référentiel n'en publient pas. On le dit plutôt que de servir
            # une fiche vide ou d'inventer un repli.
            muettes.append(code)
            continue

        nom = V._texte(z.get("zone_name") or z.get("country_name") or code)
        # La date de la fiche est celle du facteur le plus récent EMPLOYÉ :
        # dater d'aujourd'hui une valeur de 2020 la ferait passer pour neuve.
        dates = sorted(str(d.get("datetime") or "")[:10] for d in retenus.values())
        iso = dates[-1] if dates and re.match(r"^\d{4}-\d{2}-\d{2}$", dates[-1]) else None
        if not iso:
            muettes.append(code)
            continue

        ordonnes = sorted(retenus.items(), key=lambda kv: -float(kv[1]["value"]))
        pire, meilleur = ordonnes[0], ordonnes[-1]
        ecart = (float(pire[1]["value"]) / float(meilleur[1]["value"])
                 if float(meilleur[1]["value"]) else 0.0)

        detail = " ; ".join(
            "%s %s gCO2e/kWh (%s, %s)"
            % (FILIERES_EM_NOM.get(f, f), _nb(d["value"]),
               str(d.get("datetime"))[:4], V._texte(d.get("source")) or "source non nommée")
            for f, d in ordonnes[:5])

        lecture = (
            "Facteurs d'émission en CYCLE DE VIE — construction, combustible et "
            "démantèlement compris, pas seulement la combustion. C'est le seul "
            "périmètre qui compare l'éolien au gaz sans avantager le premier par "
            "omission, et c'est celui qui compte pour un arbitrage "
            "d'implantation qui engage des décennies. %s. "
            "Chaque valeur porte ici SA source et SA date, ce qui est rare : "
            "elles ne viennent pas toutes du même millésime, et la fiche "
            "affiche celui de chacune."
            % detail)
        if ecart >= 5:
            lecture += (" L'écart entre la filière la plus émettrice (%s) et la "
                        "moins émettrice (%s) est d'un facteur %s : sur ce "
                        "territoire, l'heure à laquelle un centre consomme pèse "
                        "davantage que son PUE."
                        % (FILIERES_EM_NOM.get(pire[0], pire[0]),
                           FILIERES_EM_NOM.get(meilleur[0], meilleur[0]),
                           _nb(round(ecart))))

        fiches.append(V.normaliser({
            "id": "em-facteurs-%s" % code.lower(),
            "titre": "%s — facteurs d'émission par filière, du simple au %s"
                     % (nom, "quintuple" if ecart >= 5 else "double"),
            "chapeau": _abrege(
                "Facteurs d'émission en cycle de vie retenus par Electricity "
                "Maps pour la zone %s : %s." % (code, detail), 330),
            "lecture": lecture,
            "lecture_nature": "regle",
            "portee": "À confronter au contrat d'électricité du site : un "
                      "facteur moyen annuel ne dit rien de l'heure à laquelle "
                      "vous consommez. Si l'écart entre filières est large, un "
                      "décalage de charge de quelques heures déplace davantage "
                      "l'empreinte qu'un point de PUE gagné — et il ne coûte "
                      "aucun matériel.",
            "incertitude": "Ces facteurs sont des moyennes de filière, pas des "
                           "mesures de votre fourniture. Ils ne disent ni le mix "
                           "horaire réel, ni ce que porte votre contrat "
                           "(garanties d'origine, approche « market-based »). "
                           "Les millésimes diffèrent d'une filière à l'autre : "
                           "la fiche les affiche plutôt que de les uniformiser.",
            "sujet": "datacenter",
            "editeur": None,
            # LES FILIÈRES NE SONT PAS DES TECHNOLOGIES DE LA FICHE.
            # DÉFAUT CORRIGÉ AVANT MISE EN LIGNE. Les trois filières les plus
            # émettrices entraient ici : mesuré, cela produisait 132 liens
            # « même technologie » portant tous le motif identique
            # « charbon, fioul, gaz » — parce que ces trois-là sont en tête
            # dans presque tous les pays. Le champ reliait donc chaque zone à
            # toutes les autres, avec la même phrase recopiée.
            #
            # C'est mot pour mot la faute pour laquelle « mode operatoire » a
            # été écarté et « technique et faille » retiré du croisement. Une
            # filière n'est pas une technologie DE LA FICHE : c'est une ligne
            # de son tableau. Le lien utile entre deux fiches de pays est
            # « même pays » avec la fiche de mix OWID, pas « même charbon ».
            "technologies": ["Mix électrique", "Empreinte carbone"],
            "pays": [code],
            "date_fait": iso,
            "source_cle": "electricity_maps",
            "source_url": _EM_GABARIT % code,
            "statut": "verifiee_source_primaire",
            "impact": "structurant",
            "horizon": "constate",
            "signe_par": "Collecte automatique — règles publiées dans ingestion.py",
        })["fiche"])

    if not fiches:
        return {"ok": False, "source": "electricity_maps", "erreur": "aucune_zone",
                "message": "Aucune zone n'a rendu de facteur exploitable."}
    return {
        "ok": True, "source": "electricity_maps", "fiches": fiches,
        "retenues": len(fiches),
        "dit": "%d zone(s) servies sur %d demandées%s%s. Chaque facteur porte "
               "sa propre source et sa propre date — la fiche les affiche "
               "plutôt que de les uniformiser."
               % (len(fiches), len(codes),
                  " ; %d sans facteur publié" % len(muettes) if muettes else "",
                  " ; %d injoignables" % len(injoignables) if injoignables else ""),
    }


def _nb(x):
    """Un nombre lisible : « 1 028 » plutôt que « 1028.5 » dans une phrase."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return str(x)
    return ("%d" % round(v)) if abs(v) >= 10 else ("%.1f" % v).replace(".", ",")


# ═══════════════════════════════════════════════════════════════════════════
#  COLLECTEUR 7 — OWASP LLM TOP 10 : le CONSENSUS, en regard des incidents
#
#  POURQUOI CETTE SOURCE, ET POURQUOI MAINTENANT. La rubrique IA ne portait
#  que huit fiches, toutes issues d'ATLAS — donc toutes de la même nature :
#  des INCIDENTS OBSERVÉS. Une veille qui ne connaît d'un domaine que ses
#  incidents n'en donne qu'une face, celle qui s'est déjà produite. OWASP
#  apporte l'autre : ce qu'une communauté de praticiens RECONNAÎT comme
#  menaçant, indépendamment de ce qui a été constaté.
#
#  LA DISTINCTION EST LE TOUT. « C'est arrivé » et « c'est reconnu comme un
#  risque » sont deux énoncés différents, qu'un agrégateur confondrait en les
#  empilant. Chaque fiche le dit dans sa lecture, et la source le dit dans son
#  « ne couvre pas ».
# ═══════════════════════════════════════════════════════════════════════════

_OWASP_BASE = ("https://raw.githubusercontent.com/OWASP/www-project-top-10-"
               "for-large-language-model-applications/main/2_0_vulns/")

# Les dix entrées de l'édition 2025, avec le nom de fichier et un intitulé
# français. L'intitulé est du cabinet : OWASP publie en anglais, et laisser
# « Improper Output Handling » brut sur un site français reviendrait à ne pas
# faire le travail.
OWASP_LLM = [
    ("LLM01_PromptInjection", "Injection d'invite"),
    ("LLM02_SensitiveInformationDisclosure", "Divulgation d'information sensible"),
    ("LLM03_SupplyChain", "Chaîne d'approvisionnement"),
    ("LLM04_DataModelPoisoning", "Empoisonnement des données et du modèle"),
    ("LLM05_ImproperOutputHandling", "Traitement fautif des sorties"),
    ("LLM06_ExcessiveAgency", "Agentivité excessive"),
    ("LLM07_SystemPromptLeakage", "Fuite de l'invite système"),
    ("LLM08_VectorAndEmbeddingWeaknesses", "Faiblesses des index vectoriels"),
    ("LLM09_Misinformation", "Désinformation"),
    ("LLM10_UnboundedConsumption", "Consommation non bornée"),
]

# L'ÉDITION EST DATÉE, PAS L'ENTRÉE. OWASP publie une édition 2025 sans dater
# chaque risque. Afficher une date au jour près serait inventer une précision
# que la source ne porte pas ; la convention est donc écrite ici ET dans
# l'incertitude de chaque fiche.
OWASP_EDITION = "2025"
OWASP_DATE_CONVENTION = "%s-01-01" % OWASP_EDITION


def _owasp_bloc(texte, motif):
    r"""Le contenu d'une section désignée par un MOTIF, pas par un titre exact.

    DÉFAUT CORRIGÉ AVANT MISE EN LIGNE. Les dix entrées n'emploient pas les
    mêmes intitulés : « Common Examples of Risks » ici, « … of Risk » là,
    « … of Vulnerability » ailleurs, et LLM01 titre carrément « Types of
    Prompt Injection Vulnerabilities ». Chercher un libellé exact rejetait
    deux entrées sur trois — silencieusement, en les comptant « illisibles ».
    Une source qu'on lit mal ressemble en tout point à une source qui répond
    mal.

    SECOND DÉFAUT, TROUVÉ PAR LE CONTRÔLE QUI GARDE LE PREMIER — et pire que
    lui. Le motif s'appliquait sous `re.S`, où le point traverse les retours à
    la ligne : « Types of .+ » avalait le document entier, et le bloc rendu
    était sa QUEUE. La fiche LLM01 publiait ainsi « AML.T0054 — LLM Jailbreak
    Injection » comme exemple de manifestation : c'est le pied de page des
    références. Le contrôle « dix entrées sur dix lues » passait au vert,
    puisqu'il mesurait qu'une section sorte, pas qu'elle soit la bonne.

    Le titre est donc borné à SA LIGNE — `re.S` ne vaut plus que pour le corps
    capturé, et `[ \t]*` remplace `\s*`, qui franchit lui aussi les lignes.
    """
    m = re.search(r"^#{2,4}[ \t]*(?:%s)[ \t]*\n(?s:(.+?))(?=\n#{2,3}[ \t]|\Z)"
                  % motif, texte, re.M | re.I)
    return m.group(1) if m else ""


def _owasp_section(texte, motif):
    return " ".join(_owasp_bloc(texte, motif).split())


def _owasp_puces(texte, motif, maxi=4):
    """Les items d'une section, qu'ils soient en puces OU en sous-titres.

    Les parades sont tantôt des puces, tantôt des sous-titres numérotés
    (`#### 1. Constrain model behavior`). Ne lire que les puces revenait à
    déclarer sans parade les entrées les mieux structurées.
    """
    bloc = _owasp_bloc(texte, motif)
    if not bloc:
        return []
    out = []
    for l in bloc.splitlines():
        l = l.strip()
        m = (re.match(r"^#{3,5}\s*(?:\d+[.)]\s*)?(.+)$", l)
             or re.match(r"^(?:[-*]|\d+[.)])\s+(.+)$", l))
        if not m:
            continue
        t = re.sub(r"\*\*(.+?)\*\*", r"\1", m.group(1)).strip()
        t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
        t = t.rstrip(":").strip()
        if len(t) > 8 and t.lower() not in {x.lower() for x in out}:
            out.append(t)
        if len(out) >= maxi:
            break
    return out


def _owasp_atlas(texte):
    """Les techniques ATLAS qu'OWASP RATTACHE LUI-MÊME à ce risque.

    C'EST LE PONT QUE LA RUBRIQUE ATTENDAIT. Elle porte deux natures — les
    incidents observés d'ATLAS, les risques reconnus d'OWASP — et rien ne les
    joignait : les fiches OWASP se retrouvaient isolées une fois retiré le
    faux rapprochement par leur date de convention.

    Or OWASP publie une section « Related Frameworks and Taxonomies » où il
    nomme les techniques ATLAS correspondantes. Le rapprochement n'est donc
    pas de nous : c'est la source qui l'affirme, et c'est le seul type de lien
    de ce site qui n'engage pas le cabinet. Nous ne faisons que le reprendre.

    Les sous-techniques (`AML.T0051.000`) sont conservées telles quelles : les
    replier sur leur technique mère reviendrait à dire « injection d'invite »
    là où la source dit « injection d'invite DIRECTE ». La correspondance avec
    une fiche réellement servie est vérifiée plus loin, jamais ici.
    """
    bloc = _owasp_bloc(texte, r"Related Frameworks and Taxonomies")
    out = []
    for m in re.finditer(r"\[(AML\.T[0-9.]*[0-9])\s*[-–—]\s*([^\]]+)\]", bloc):
        ref, nom = m.group(1), " ".join(m.group(2).split())
        if ref not in [x[0] for x in out]:
            out.append((ref, nom))
    return out


def completer_atlas_techniques(corpus):
    """Sert les techniques ATLAS que NOS PROPRES SOURCES désignent.

    POURQUOI CETTE PASSE EXISTE. Le collecteur de techniques retient les huit
    « les plus récemment révisées » — un critère arbitraire, et qui ne dit rien
    de ce corpus-ci : une technique éditée le mois dernier n'est pas plus
    pertinente qu'une autre pour un lecteur de ce site. Résultat mesuré : sur
    les onze correspondances qu'OWASP déclare vers ATLAS, DEUX seulement
    tombaient sur une fiche servie ; les neuf autres n'auraient donné aucun
    lien, faute d'un bout.

    Le critère ajouté vaut mieux parce qu'il vient du corpus et non d'un
    proxy : une technique qu'une source déjà servie NOMME EXPLICITEMENT
    appartient à ce que ce site couvre. Elle n'est pas ajoutée pour faire
    nombre — elle est ajoutée parce qu'une fiche pointe dessus.

    Rendu : le nombre de techniques ajoutées, et le nombre de références
    restées introuvables au référentiel. Le second cas ne se produit pas
    aujourd'hui, mais un identifiant retiré d'ATLAS le produirait, et il ne
    doit pas passer en silence.
    """
    voulues = set()
    for f in corpus:
        for ref, _ in (f.get("_owasp_atlas") or []):
            voulues.add(ref)
    deja = {f.get("id") for f in corpus}
    voulues = {r for r in voulues
               if "atlas-tech-%s" % r.lower().replace(".", "-") not in deja}
    if not voulues:
        return 0, 0

    d, err = _atlas_charge()
    if err:
        return 0, len(voulues)
    mat = (d.get("matrices") or [{}])[0]
    tact = {t.get("id"): t.get("name") for t in (mat.get("tactics") or [])}
    par_ref = {t.get("id"): t for t in (mat.get("techniques") or []) if t.get("id")}

    ajoutees, introuvables = 0, 0
    for ref in sorted(voulues):
        t = par_ref.get(ref)
        iso = str((t or {}).get("modified_date")
                  or (t or {}).get("created_date") or "")[:10]
        if not t or not re.match(r"^\d{4}-\d{2}-\d{2}$", iso):
            introuvables += 1
            continue
        corpus.append(_fiche_technique_atlas(t, tact, iso, par_ref))
        ajoutees += 1
    return ajoutees, introuvables


def relier_owasp_atlas(corpus):
    """Pose les relations OWASP ↔ ATLAS dont les DEUX bouts sont servis.

    Une relation vers une technique que ce site ne publie pas donnerait un
    lien mort ; ATLAS en référence plus de cent quarante, le site en sert une
    poignée. La règle est celle de `_relier_atlas`, et pour la même raison.
    """
    par_id = {f.get("id"): f for f in corpus if f.get("id")}
    n = 0
    for f in corpus:
        for ref, nom in (f.get("_owasp_atlas") or []):
            cle = "atlas-tech-%s" % ref.lower().replace(".", "-")
            tech = par_id.get(cle)
            if not tech:
                continue
            for de, vers, sens in ((f, tech, "technique correspondante"),
                                   (tech, f, "risque reconnu correspondant")):
                de.setdefault("relations", []).append({
                    "vers": vers["id"], "titre": vers["titre"],
                    "nature": "correspondance_owasp_atlas", "nature_nom": sens,
                    "dit": "OWASP rattache lui-même ce risque à la technique "
                           "ATLAS « %s » (%s), dans sa section des cadres "
                           "apparentés. Le rapprochement est de la source, "
                           "pas de ce site." % (nom, ref),
                    "citations": ["OWASP Top 10 for LLM Applications %s — "
                                  "Related Frameworks and Taxonomies"
                                  % OWASP_EDITION],
                })
            n += 1
    for f in corpus:
        f.pop("_owasp_atlas", None)
    return n


def collecter_owasp_llm(limite=None, documents=None):
    """Une fiche par famille de risque de l'édition 2025.

    CHAQUE FICHE DIT CE QU'ELLE EST : un consensus de praticiens, pas un
    incident et pas une norme opposable. C'est la seule chose qui empêche un
    lecteur de la lire comme ATLAS — dont les fiches, elles, décrivent des
    faits survenus.

    `documents` est une COUTURE DE CONTRÔLE, sur le modèle de `_relier_atlas` :
    la règle « sans description ni parade, on ne sert pas la fiche » ne peut
    pas être éprouvée sur les données réelles, puisque les dix entrées d'OWASP
    portent aujourd'hui les deux. Un contrôle branché sur le réseau passerait
    au vert sans rien garder.
    """
    s = SRC.SOURCES["owasp_llm"]
    entrees = OWASP_LLM[:limite] if limite else OWASP_LLM
    fiches, muettes, sans_manifestation = [], [], []
    for fichier, intitule in entrees:
        if documents is not None:
            if fichier not in documents:
                muettes.append(fichier)
                continue
            t = documents[fichier]
        else:
            r = _lire(_OWASP_BASE + fichier + ".md", delai=25)
            if not r["ok"]:
                muettes.append(fichier)
                continue
            t = r["corps"].decode("utf-8", "replace")
        ref = fichier.split("_")[0]                      # LLM01, LLM02, …
        description = _owasp_section(t, "Description")
        # LES INTITULÉS VARIENT D'UNE ENTRÉE À L'AUTRE : on les désigne par
        # famille. « Risks », « Risk », « Vulnerability », « Types of … » —
        # quatre formulations pour la même section sur dix entrées.
        risques = _owasp_puces(t, r"(?:Common Examples? of \w+|Types of .+)")
        parades = _owasp_puces(t, r"Prevention and Mitigation Strategies")
        if not description or not parades:
            # SANS DESCRIPTION NI PARADE, LA FICHE N'APPRENDRAIT RIEN. On ne
            # sert pas une entrée vide sous prétexte que la source l'annonce.
            muettes.append(fichier)
            continue
        # UNE SECTION QU'ON NE SAIT PAS LIRE SE COMPTE. Les manifestations ne
        # conditionnent pas la publication — la fiche vaut sans elles —, mais
        # leur absence ne doit pas être SILENCIEUSE : c'est précisément par ce
        # silence que le libellé exact a pu rejeter sept entrées sur dix sans
        # que rien ne bouge à l'écran. OWASP les publie sur les dix ; un
        # compteur non nul dit donc que NOUS lisons mal, pas que la source
        # s'est tue.
        if not risques:
            sans_manifestation.append(fichier)

        lecture = (
            "OWASP range ce risque parmi les dix qui menacent une application "
            "bâtie sur un modèle de langage. C'est un CONSENSUS DE PRATICIENS, "
            "et il faut le lire comme tel : la liste ne dit pas que ce risque "
            "s'est réalisé chez quelqu'un — c'est ce que documente ATLAS, sur "
            "ce même site —, elle dit qu'il est reconnu comme sérieux par ceux "
            "qui construisent ces systèmes. Confondre les deux ferait passer "
            "un risque reconnu pour un incident constaté.")
        if parades:
            lecture += (" La source publie ses parades, ce qui rend le risque "
                        "actionnable : %s%s."
                        % ("; ".join(_abrege(p, 130) for p in parades[:3]),
                           " (et d'autres)" if len(parades) > 3 else ""))

        fiches.append(V.normaliser({
            "id": "owasp-llm-%s" % ref.lower(),
            "titre": "%s — %s (OWASP %s:%s)"
                     % (intitule, "risque reconnu pour les applications à "
                        "modèle de langage", ref, OWASP_EDITION),
            "chapeau": _abrege(description, 330),
            "lecture": lecture,
            "lecture_nature": "regle",
            "portee": "À confronter à l'inventaire de vos systèmes d'IA : la "
                      "question n'est pas de savoir si ce risque existe — "
                      "OWASP l'établit — mais si votre application y est "
                      "exposée, et si les parades publiées y sont en place. "
                      "C'est un point à porter au registre exigé par le "
                      "règlement européen sur l'IA, où la maîtrise des risques "
                      "doit être documentée, pas seulement affirmée."
                      + (" Exemples de manifestation : %s."
                         % "; ".join(_abrege(x, 110) for x in risques[:2])
                         if risques else ""),
            "incertitude": "Consensus de praticiens, pas une norme opposable : "
                           "aucune obligation n'en découle, et le classement "
                           "des dix familles ne reflète pas une fréquence "
                           "mesurée. L'édition %s n'est pas datée entrée par "
                           "entrée — le jour affiché est une convention de "
                           "classement, pas une observation."
                           % OWASP_EDITION,
            "sujet": "sia",
            "editeur": None,
            # Transporté jusqu'à `relier_owasp_atlas`, qui a besoin du corpus
            # entier pour savoir lesquelles de ces techniques sont servies. Le
            # champ est retiré une fois les relations posées : il n'a rien à
            # faire dans ce que le site publie.
            "_owasp_atlas": _owasp_atlas(t),
            "technologies": ["Sécurité des systèmes d'IA", "Risque reconnu"],
            "pays": [],
            "date_fait": OWASP_DATE_CONVENTION,
            # LA DATE EST DÉCLARÉE FABRIQUÉE, et pas seulement dans la prose.
            # L'écrire dans l'incertitude ne suffisait pas : le croisement ne
            # lit pas l'incertitude, il lit les dates — il rapprochait donc
            # les dix fiches « à moins de 45 jours » sur une valeur que ce
            # fichier venait d'inventer. Un champ, lui, se vérifie.
            "date_convention": True,
            "date_convention_dit":
                "OWASP date son ÉDITION (%s), pas chacune de ses entrées. Le "
                "1er janvier tient lieu de rang de classement ; la source ne "
                "dit pas quand ce risque a été reconnu."
                % OWASP_EDITION,
            "source_cle": "owasp_llm",
            "source_url": _OWASP_BASE + fichier + ".md",
            "statut": "verifiee_source_primaire",
            "impact": "structurant",
            "horizon": "constate",
            "signe_par": "Collecte automatique — règles publiées dans ingestion.py",
        })["fiche"])

    if not fiches:
        return {"ok": False, "source": "owasp_llm", "erreur": "aucune_entree",
                "message": "Aucune entrée OWASP n'a pu être lue."}
    return {
        "ok": True, "source": "owasp_llm", "fiches": fiches,
        "retenues": len(fiches),
        "sans_manifestation": len(sans_manifestation),
        "dit": "OWASP LLM Top 10, édition %s — %d famille(s) de risque "
               "servies sur %d%s%s. Ce sont des risques RECONNUS, pas des "
               "incidents constatés : la distinction est portée par chaque "
               "fiche."
               % (OWASP_EDITION, len(fiches), len(entrees),
                  " ; %d entrée(s) illisibles" % len(muettes) if muettes else "",
                  " ; %d servie(s) sans leurs exemples de manifestation, que "
                  "la source publie pourtant — c'est notre lecture qui a "
                  "échoué" % len(sans_manifestation)
                  if sans_manifestation else ""),
    }
