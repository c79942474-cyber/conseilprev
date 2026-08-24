"""LES GABARITS DE DÉRIVATION — un texte, deux langues, écrites côte à côte.

CE QUE CE FICHIER CHANGE, ET POURQUOI IL EXISTE. Jusqu'ici la bascule FR/EN
traduisait l'interface et DÉCLARAIT ne pas traduire les analyses : la lecture
critique, la portée et l'incertitude sont dérivées par des règles, à partir de
gabarits qui n'existaient qu'en français. `veille.langues()` comptait ce reste
et l'affichait — une réserve honnête, mais une réserve.

Le site annonçait aussi ce qu'il faudrait pour la lever : « des gabarits
anglais — un vrai travail, pas un réglage —, et les traduire par machine
serait exactement ce que ce site refuse partout ailleurs ». C'est ce travail.
Chaque phrase anglaise de ce fichier a été ÉCRITE ; aucune n'est passée par un
traducteur automatique, et le contrôle qui interdit les bibliothèques de
modèle de langage dans la chaîne de collecte vaut ici comme ailleurs.

POURQUOI LES DEUX LANGUES SONT DANS LE MÊME FICHIER, SUR LA MÊME LIGNE. Un
fichier `anglais.py` en regard d'`ingestion.py` aurait divergé à la première
correction — et c'est toujours la version la moins lue qui reste en arrière,
c'est-à-dire l'anglaise. Ici on ne peut pas retoucher une phrase sans avoir
l'autre sous les yeux.

CE QUI EST GARANTI PAR LA FORME, ET NON PAR LA DISCIPLINE :

  · Une entrée porte TOUJOURS ses deux colonnes — une entrée à une seule
    langue ne se compile pas en un couple, et `sante()` la refuse.
  · Les deux colonnes portent LES MÊMES EMPLACEMENTS de substitution, en même
    nombre et dans le même ordre. Sans ce contrôle, un `%s` oublié côté
    anglais lèverait une exception au moment de la collecte — donc en
    production, et pour les seuls lecteurs anglophones.
  · La LOGIQUE qui choisit les phrases ne s'écrit qu'une fois : `Deux`
    accumule dans les deux langues en même temps. Deux fonctions parallèles
    auraient fini par ne plus choisir les mêmes phrases dans les mêmes cas,
    et personne ne l'aurait vu — le français, lui, aurait continué à marcher.

CE QUI N'EST PAS TRADUIT ICI, ET NE PEUT PAS L'ÊTRE. Ce qui vient de la
source : titres d'origine, résumés, noms de techniques, descriptions. MITRE,
CISA et OWASP publient en anglais, ce qui tombe bien ; mais si une source
publiait en allemand, ce site servirait de l'allemand plutôt que d'inventer.
"""

#: Les deux langues servies. Écrite ici plutôt que répétée : une troisième
#: langue se déclarerait à cet endroit, et les contrôles la réclameraient
#: partout d'un coup.
LANGUES = ("fr", "en")


def _place(s):
    """Les emplacements de substitution d'un gabarit, dans l'ordre.

    Sert au contrôle de parité entre les deux colonnes. On ne compare pas le
    NOMBRE seulement : `%s %d` et `%d %s` prennent les mêmes arguments dans un
    ordre différent, ce qui produit « 3 pays » d'un côté et « France
    countries » de l'autre.
    """
    out, i = [], 0
    while i < len(s):
        if s[i] == "%":
            if i + 1 < len(s) and s[i + 1] == "%":
                i += 2
                continue
            j = i + 1
            while j < len(s) and s[j] not in "sdifgr":
                j += 1
            out.append(s[i:j + 1])
            i = j + 1
        else:
            i += 1
    return out


# ═══════════════════════════════════════════════════════════════════════════
#  LA TABLE. Clé → (français, anglais).
#
#  L'ORDRE SUIT LES COLLECTEURS, pas l'alphabet : on relit un gabarit dans le
#  contexte de la fiche qu'il compose, jamais isolé.
# ═══════════════════════════════════════════════════════════════════════════

G = {

    # ── CISA KEV — vulnérabilités dont l'exploitation est avérée ──────────
    "kev.chapeau": (
        ". Inscrite au catalogue des vulnérabilités dont l'exploitation est "
        "avérée le %s.",
        ". Added to the catalog of known exploited vulnerabilities on %s."),
    "kev.industriel": (
        "L'éditeur relève du périmètre industriel (%s) : la faille est donc à "
        "instruire côté OT, où le correctif ne se pose pas au même rythme "
        "qu'en bureautique.",
        "The vendor falls within the industrial perimeter (%s), so this flaw "
        "must be worked through on the OT side, where patching does not "
        "follow the same tempo as it does in office IT."),
    # LE MOTIF DU CLASSEMENT INDUSTRIEL — bilingue, parce qu'il est INTERPOLÉ
    # dans une phrase. Constaté au premier essai : « The vendor falls within
    # the industrial perimeter (éditeur au répertoire industriel du cabinet) ».
    # Un argument qui est lui-même du texte doit voyager dans les deux langues.
    "kev.motif.repertoire": (
        "éditeur au répertoire industriel du cabinet",
        "vendor in the firm's industrial directory"),
    "kev.motif.mot": (
        "le nom du produit porte le mot « %s »",
        "the product name carries the word “%s”"),
    "kev.non_industriel": (
        "L'éditeur n'est pas au répertoire industriel du cabinet. La faille "
        "reste à instruire si le produit est présent dans votre chaîne — un "
        "poste d'ingénierie ou un serveur d'historisation compte comme "
        "surface industrielle.",
        "The vendor is not in the firm's industrial directory. The flaw still "
        "has to be worked through if the product sits anywhere in your chain "
        "— an engineering workstation or a historian server counts as "
        "industrial surface."),
    "kev.rancon": (
        "Elle est associée à des campagnes de rançongiciel connues : c'est le "
        "signal le plus fort du catalogue, car il indique une exploitation "
        "outillée et non un cas isolé.",
        "It is associated with known ransomware campaigns: that is the "
        "strongest signal the catalog carries, because it indicates tooled "
        "exploitation rather than an isolated case."),
    "kev.sans_rancon": (
        "Aucune campagne de rançongiciel n'y est associée à ce jour — ce qui "
        "ne vaut pas absence d'exploitation, seulement absence d'exploitation "
        "par ce mode opératoire.",
        "No ransomware campaign is associated with it to date — which is not "
        "the same as no exploitation, only no exploitation through that "
        "particular playbook."),
    "kev.echeance": (
        "L'échéance de remédiation imposée aux agences fédérales américaines "
        "était le %s%s. Elle ne vous oblige pas, mais elle date le moment où "
        "le risque a été jugé non tenable par une autorité.",
        "The remediation deadline imposed on US federal agencies was %s%s. It "
        "does not bind you, but it dates the moment an authority judged the "
        "risk untenable."),
    "kev.echeance.depasse": (
        " — elle est dépassée",
        " — and it has passed"),
    "kev.portee": (
        "À confronter à votre inventaire : si ce produit est présent, la "
        "question n'est plus s'il faut corriger mais quand, et par quelle "
        "mesure compensatoire d'ici là. Une fenêtre d'arrêt de production se "
        "demande des semaines à l'avance — c'est ce délai, pas le correctif, "
        "qui commande le calendrier.",
        "Check this against your inventory: if the product is present, the "
        "question is no longer whether to patch but when, and what "
        "compensating measure holds until then. A production shutdown window "
        "is requested weeks ahead — it is that lead time, not the patch, that "
        "sets the schedule."),
    "kev.incertitude": (
        "Le catalogue dit qu'une exploitation existe, pas qu'elle vous vise, "
        "ni qu'elle atteindrait votre installation compte tenu de sa "
        "segmentation. L'absence d'un produit au catalogue ne vaut pas "
        "absence de faille.",
        "The catalog says exploitation exists — not that it targets you, nor "
        "that it would reach your installation given how it is segmented. A "
        "product's absence from the catalog is not the absence of a flaw."),

    # ── OWID — part d'électricité bas carbone ─────────────────────────────
    "mix.titre": (
        "%s — %.1f %% d'électricité bas carbone (%d)",
        "%s — %.1f%% low-carbon electricity (%d)"),
    "mix.chapeau": (
        "Part de l'électricité produite sans carbone (nucléaire et "
        "renouvelables) dans le mix national de %s en %d%s.",
        "Share of electricity generated without carbon (nuclear and "
        "renewables) in the national mix of %s in %d%s."),
    "mix.chapeau.renouv": (
        ", dont %.1f %% de renouvelables",
        ", of which %.1f%% renewables"),
    "mix.haut": (
        "Un mix à %.1f %% bas carbone place ce pays parmi ceux où "
        "l'électricité pèse peu dans l'empreinte d'exploitation d'un centre. "
        "L'arbitrage s'y déplace vers le carbone INCORPORÉ — construction et "
        "serveurs — qui devient majoritaire dès lors que l'usage est "
        "décarboné.",
        "A mix at %.1f%% low carbon places this country among those where "
        "electricity weighs little in a data centre's operational footprint. "
        "The trade-off shifts to EMBODIED carbon — construction and servers — "
        "which becomes the larger term once usage is decarbonised."),
    "mix.moyen": (
        "À %.1f %% bas carbone, l'électricité reste un poste significatif "
        "sans être dominant. C'est la zone où le choix du mode de "
        "refroidissement se juge sur l'eau ET sur le carbone ensemble, l'un "
        "ne dominant pas l'autre.",
        "At %.1f%% low carbon, electricity remains a significant line without "
        "being the dominant one. This is the band where the choice of cooling "
        "must be judged on water AND carbon together, neither one "
        "overriding the other."),
    "mix.bas": (
        "Avec %.1f %% bas carbone — donc environ %.1f %% de production "
        "fossile — l'électricité domine l'empreinte d'exploitation. C'est "
        "aussi la configuration où le WUE de SOURCE s'écarte le plus du WUE "
        "de site : l'eau prélevée en amont pour produire le courant devient "
        "le terme principal, et un refroidissement sec peut y consommer plus "
        "d'eau qu'une tour.",
        "At %.1f%% low carbon — so roughly %.1f%% fossil generation — "
        "electricity dominates the operational footprint. It is also the "
        "configuration where source WUE departs furthest from site WUE: the "
        "water withdrawn upstream to generate the power becomes the leading "
        "term, and dry cooling can consume more water there than a tower."),
    "mix.portee": (
        "Cette part commande l'empreinte d'exploitation à consommation égale, "
        "et donc l'arbitrage entre implanter près de la charge ou près de "
        "l'électricité propre. Elle ne décide pas seule : le stress hydrique, "
        "le prix et le délai de raccordement pèsent au moins autant.",
        "This share governs the operational footprint at equal consumption, "
        "and therefore the trade-off between siting near the load and siting "
        "near clean electricity. It does not decide alone: water stress, "
        "price and grid connection lead time weigh at least as much."),
    "mix.incertitude": (
        "Une moyenne ANNUELLE et NATIONALE. Elle ne dit rien de l'intensité à "
        "l'heure où tourne votre charge, ni du mix réellement livré par votre "
        "contrat. Un centre adossé à un contrat d'achat direct peut s'en "
        "écarter fortement, dans les deux sens.",
        "An ANNUAL and NATIONAL average. It says nothing about the intensity "
        "at the hour your load actually runs, nor about the mix your contract "
        "really delivers. A site backed by a direct purchase agreement can "
        "depart from it sharply, in either direction."),

    # ── MITRE ATT&CK for ICS — modes opératoires et logiciels ─────────────
    "attack.groupe.titre": (
        "%s — mode opératoire documenté contre l'ICS%s",
        "%s — playbook documented against ICS%s"),
    "attack.groupe.lecture": (
        "ATT&CK ICS décrit ici un ensemble d'activités OBSERVÉES sur des "
        "installations industrielles, pas une attribution : le référentiel "
        "dit ce qui a été fait, jamais qui l'a commandité. Sa présence au "
        "référentiel signifie que les techniques employées sont documentées "
        "et donc détectables — c'est le seul point qui vous concerne "
        "directement, et il se traduit en règles de supervision, pas en "
        "communiqué.",
        "ATT&CK ICS describes here a set of activities OBSERVED on industrial "
        "installations, not an attribution: the framework says what was done, "
        "never who ordered it. Its presence in the framework means the "
        "techniques used are documented and therefore detectable — that is "
        "the only part that concerns you directly, and it translates into "
        "monitoring rules, not into a press release."),
    "attack.groupe.portee": (
        "À confronter à votre cartographie de zones et conduits : les "
        "techniques rattachées à ce mode opératoire désignent des points de "
        "détection concrets. Un plan de supervision qui ne couvre aucune des "
        "techniques documentées pour votre filière surveille ce qui est "
        "facile à voir, pas ce qui arrive.",
        "Check this against your zone and conduit map: the techniques "
        "attached to this playbook point to concrete detection points. A "
        "monitoring plan that covers none of the techniques documented for "
        "your industry watches what is easy to see, not what actually "
        "happens."),
    "attack.groupe.incertitude": (
        "Le référentiel recense ce qui a été observé ET publié. Ce qui n'a "
        "pas été détecté, ou l'a été sans être documenté, n'y figure pas — "
        "l'absence d'une technique ne vaut donc pas absence de risque.",
        "The framework records what was observed AND published. What went "
        "undetected, or was detected without being documented, is not in it — "
        "so the absence of a technique is not the absence of risk."),
    "attack.logiciel.titre": (
        "%s — logiciel malveillant documenté contre l'ICS%s",
        "%s — malware documented against ICS%s"),
    "attack.logiciel.lecture": (
        "Un logiciel inscrit au référentiel ICS a été employé contre des "
        "systèmes d'automatisation, pas seulement contre de la bureautique. "
        "La distinction commande la réponse : sur un procédé qui tourne, "
        "l'isolement d'un poste n'est pas une mesure neutre, et la remise en "
        "service se prépare avant l'incident, pas pendant.",
        "Software recorded in the ICS framework was used against automation "
        "systems, not only against office IT. That distinction governs the "
        "response: on a running process, isolating a workstation is not a "
        "neutral measure, and bringing it back into service is prepared "
        "before the incident, not during it."),
    "attack.logiciel.portee": (
        "À verser au plan de continuité OT plutôt qu'au seul plan cyber : ce "
        "qui se joue est la capacité à redémarrer un procédé dans un état "
        "sûr, ce qu'aucune restauration de données ne fait à elle seule.",
        "File this under the OT continuity plan rather than the cyber plan "
        "alone: what is at stake is the ability to restart a process in a "
        "safe state, which no data restore achieves on its own."),
    "attack.logiciel.incertitude": (
        "La description dit ce que le logiciel PEUT faire, sur les cas "
        "analysés. Elle ne dit ni sa prévalence, ni s'il circule encore, ni "
        "s'il atteindrait votre architecture compte tenu de sa segmentation.",
        "The description says what the software CAN do, on the cases "
        "analysed. It says nothing about its prevalence, whether it is still "
        "circulating, or whether it would reach your architecture given how "
        "it is segmented."),

    # ── MITRE ATLAS — incidents et exercices sur des systèmes d'IA ────────
    "atlas.lecture": (
        "ATLAS documente ici un incident %s contre un système d'IA en "
        "production%s. Le déroulé est décomposé en %d étape(s) rattachées aux "
        "tactiques du référentiel : ce n'est pas un récit, c'est une séquence "
        "technique reproductible côté défense, donc traduisible en points de "
        "contrôle. %s",
        "ATLAS documents here a %s incident against an AI system in "
        "production%s. The sequence is broken into %d step(s) mapped to the "
        "framework's tactics: this is not a narrative, it is a technical "
        "sequence reproducible on the defensive side, and therefore "
        "translatable into control points. %s"),
    "atlas.reel": ("réel", "real"),
    "atlas.exercice": (
        "documenté (exercice ou démonstration cadrée)",
        "documented (exercise or controlled demonstration)"),
    "atlas.cible": (" visant %s", " targeting %s"),
    "atlas.date.jour": (
        "La date est donnée au jour par la source.",
        "The source gives the date to the day."),
    "atlas.date.annee": (
        "L'incident n'est daté qu'à l'ANNÉE par la source ; le jour affiché "
        "est une convention de classement, pas une observation.",
        "The source dates the incident to the YEAR only; the day shown is a "
        "filing convention, not an observation."),
    "atlas.date.mois": (
        "L'incident n'est daté qu'au MOIS par la source ; le jour affiché est "
        "une convention de classement.",
        "The source dates the incident to the MONTH only; the day shown is a "
        "filing convention."),
    "atlas.avertissement.exercice": (
        " Attention à la nature du cas : c'est un EXERCICE, pas une attaque "
        "subie. Il établit qu'une chose est faisable, pas qu'elle a été faite "
        "contre un tiers.",
        " Mind what kind of case this is: it is an EXERCISE, not an attack "
        "suffered. It establishes that something is feasible, not that it was "
        "done to anyone."),
    "atlas.acteur.equipe": (
        " La source nomme l'équipe qui a conduit l'exercice : %s.",
        " The source names the team that ran the exercise: %s."),
    "atlas.acteur.entite": (
        " La source nomme l'entité à laquelle elle rattache l'incident : %s.",
        " The source names the entity it attributes the incident to: %s."),
    "atlas.acteur.inconnu": (
        " La source ne nomme aucune entité : elle inscrit « %s », c'est-à-dire "
        "qu'elle ne sait pas.",
        " The source names no entity: it records “%s”, which is to say it "
        "does not know."),
    "atlas.portee": (
        "À confronter à vos propres usages d'IA : si un modèle décide, filtre "
        "ou authentifie chez vous, la question n'est plus de savoir si ce "
        "type d'attaque existe — ATLAS l'établit — mais si votre chaîne "
        "d'entraînement et votre interface d'inférence y sont exposées. C'est "
        "un point à porter au registre des systèmes d'IA exigé par le "
        "règlement européen, pas seulement au plan cyber.",
        "Check this against your own uses of AI: if a model decides, filters "
        "or authenticates in your organisation, the question is no longer "
        "whether this kind of attack exists — ATLAS establishes that — but "
        "whether your training chain and your inference interface are exposed "
        "to it. This belongs in the AI system register required by the "
        "European regulation, not only in the cyber plan."),
    "atlas.incertitude": (
        "ATLAS recense ce qui a été observé ET publié : l'absence d'un cas ne "
        "vaut pas absence d'incident. La base ne dit ni la fréquence de ces "
        "attaques, ni leur coût, ni si votre configuration y est vulnérable.",
        "ATLAS records what was observed AND published: the absence of a case "
        "is not the absence of an incident. The database says nothing about "
        "how often these attacks occur, what they cost, or whether your "
        "configuration is vulnerable to them."),

    # ── MITRE ATLAS — techniques ──────────────────────────────────────────
    "atlastech.titre": (
        "%s — technique documentée contre l'IA (%s)",
        "%s — technique documented against AI (%s)"),
    "atlastech.lecture": (
        "Technique rattachée à %s. Une technique au référentiel signifie "
        "qu'elle a été employée ou démontrée, donc qu'elle est descriptible "
        "et détectable — c'est ce qui la sépare d'un risque théorique. Elle "
        "se traduit en contrôle sur la chaîne d'entraînement, sur l'accès au "
        "modèle ou sur l'interface d'inférence, selon la tactique qu'elle "
        "sert.",
        "Technique mapped to %s. A technique in the framework means it has "
        "been used or demonstrated, and is therefore describable and "
        "detectable — which is what separates it from a theoretical risk. It "
        "translates into a control on the training chain, on model access or "
        "on the inference interface, depending on the tactic it serves."),
    "atlastech.tactique.aucune": (
        "une tactique du référentiel",
        "a tactic of the framework"),
    "atlastech.portee": (
        "Sert à instruire la question que l'AI Act pose sans y répondre : "
        "quelles mesures de robustesse et de cybersécurité sont appropriées "
        "pour ce système. Une liste de techniques documentées est un point de "
        "départ défendable ; « nous avons sécurisé le modèle » n'en est pas "
        "un.",
        "This serves to work through the question the AI Act asks without "
        "answering: which robustness and cybersecurity measures are "
        "appropriate for this system. A list of documented techniques is a "
        "defensible starting point; “we secured the model” is not."),
    "atlastech.incertitude": (
        "Le référentiel dit ce qui est faisable, pas ce qui est fréquent ni "
        "ce qui vous vise. Il ne hiérarchise pas les techniques entre elles "
        "et ne dit pas lesquelles s'appliquent à votre architecture.",
        "The framework says what is feasible, not what is frequent nor what "
        "targets you. It does not rank techniques against one another and "
        "does not say which apply to your architecture."),

    # ── Electricity Maps — facteurs d'émission ────────────────────────────
    "em.titre": (
        "%s — facteurs d'émission par filière, du simple au %s",
        "%s — emission factors by generation type, from one to %s"),
    "em.titre.quintuple": ("quintuple", "fivefold"),
    "em.titre.double": ("double", "twofold"),
    "em.chapeau": (
        "Facteurs d'émission en cycle de vie retenus par Electricity Maps "
        "pour la zone %s : %s.",
        "Life-cycle emission factors used by Electricity Maps for zone "
        "%s: %s."),
    "em.lecture": (
        "Facteurs d'émission en CYCLE DE VIE — construction, combustible et "
        "démantèlement compris, pas seulement la combustion. C'est le seul "
        "périmètre qui compare l'éolien au gaz sans avantager le premier par "
        "omission, et c'est celui qui compte pour un arbitrage d'implantation "
        "qui engage des décennies. %s. Chaque valeur porte ici SA source et "
        "SA date, ce qui est rare : elles ne viennent pas toutes du même "
        "millésime, et la fiche affiche celui de chacune.",
        "LIFE-CYCLE emission factors — construction, fuel and "
        "decommissioning included, not combustion alone. It is the only scope "
        "that compares wind with gas without favouring the former by "
        "omission, and it is the one that matters for a siting decision that "
        "commits decades. %s. Each value here carries ITS OWN source and ITS "
        "OWN date, which is rare: they do not all come from the same vintage, "
        "and the entry shows each one's."),
    "em.ecart": (
        " L'écart entre la filière la plus émettrice (%s) et la moins "
        "émettrice (%s) est d'un facteur %s : sur ce territoire, l'heure à "
        "laquelle un centre consomme pèse davantage que son PUE.",
        " The gap between the most emitting generation type (%s) and the "
        "least emitting (%s) is a factor of %s: in this territory, the hour "
        "at which a data centre draws power weighs more than its PUE."),
    "em.portee": (
        "À confronter au contrat d'électricité du site : un facteur moyen "
        "annuel ne dit rien de l'heure à laquelle vous consommez. Si l'écart "
        "entre filières est large, un décalage de charge de quelques heures "
        "déplace davantage l'empreinte qu'un point de PUE gagné — et il ne "
        "coûte aucun matériel.",
        "Check this against the site's electricity contract: an annual "
        "average factor says nothing about the hour at which you draw power. "
        "Where the gap between generation types is wide, shifting load by a "
        "few hours moves the footprint more than a point of PUE gained — and "
        "it costs no hardware."),
    "em.incertitude": (
        "Ces facteurs sont des moyennes de filière, pas des mesures de votre "
        "fourniture. Ils ne disent ni le mix horaire réel, ni ce que porte "
        "votre contrat (garanties d'origine, approche « market-based »). Les "
        "millésimes diffèrent d'une filière à l'autre : la fiche les affiche "
        "plutôt que de les uniformiser.",
        "These factors are averages by generation type, not measurements of "
        "your supply. They say nothing about the real hourly mix, nor about "
        "what your contract carries (guarantees of origin, the market-based "
        "approach). Vintages differ from one generation type to another: the "
        "entry shows them rather than levelling them."),
    "em.source.anonyme": ("source non nommée", "source not named"),

    # ── OWASP Top 10 pour les applications à modèle de langage ────────────
    "owasp.titre": (
        "%s — risque reconnu pour les applications à modèle de langage "
        "(OWASP %s:%s)",
        "%s — recognised risk for language-model applications "
        "(OWASP %s:%s)"),
    "owasp.lecture": (
        "OWASP range ce risque parmi les dix qui menacent une application "
        "bâtie sur un modèle de langage. C'est un CONSENSUS DE PRATICIENS, et "
        "il faut le lire comme tel : la liste ne dit pas que ce risque s'est "
        "réalisé chez quelqu'un — c'est ce que documente ATLAS, sur ce même "
        "site —, elle dit qu'il est reconnu comme sérieux par ceux qui "
        "construisent ces systèmes. Confondre les deux ferait passer un "
        "risque reconnu pour un incident constaté.",
        "OWASP ranks this risk among the ten that threaten an application "
        "built on a language model. It is a CONSENSUS OF PRACTITIONERS and "
        "must be read as such: the list does not say the risk materialised at "
        "anyone's premises — that is what ATLAS documents, on this same site "
        "— it says the risk is recognised as serious by the people who build "
        "these systems. Confusing the two would pass off a recognised risk as "
        "an observed incident."),
    "owasp.parades": (
        " La source publie ses parades, ce qui rend le risque actionnable : "
        "%s%s.",
        " The source publishes its mitigations, which makes the risk "
        "actionable: %s%s."),
    "owasp.parades.autres": (" (et d'autres)", " (and others)"),
    "owasp.portee": (
        "À confronter à l'inventaire de vos systèmes d'IA : la question n'est "
        "pas de savoir si ce risque existe — OWASP l'établit — mais si votre "
        "application y est exposée, et si les parades publiées y sont en "
        "place. C'est un point à porter au registre exigé par le règlement "
        "européen sur l'IA, où la maîtrise des risques doit être documentée, "
        "pas seulement affirmée.",
        "Check this against the inventory of your AI systems: the question is "
        "not whether the risk exists — OWASP establishes that — but whether "
        "your application is exposed to it, and whether the published "
        "mitigations are in place. This belongs in the register required by "
        "the European AI regulation, where risk control must be documented, "
        "not merely asserted."),
    "owasp.manifestations": (
        " Exemples de manifestation : %s.",
        " Examples of how it shows up: %s."),
    "owasp.incertitude": (
        "Consensus de praticiens, pas une norme opposable : aucune obligation "
        "n'en découle, et le classement des dix familles ne reflète pas une "
        "fréquence mesurée. L'édition %s n'est pas datée entrée par entrée — "
        "le jour affiché est une convention de classement, pas une "
        "observation.",
        "A practitioner consensus, not an enforceable standard: no obligation "
        "follows from it, and the ranking of the ten families does not "
        "reflect a measured frequency. The %s edition is not dated entry by "
        "entry — the day shown is a filing convention, not an observation."),

    "owasp.convention": (
        "OWASP date son ÉDITION (%s), pas chacune de ses entrées. Le "
        "1er janvier tient lieu de rang de classement ; la source ne dit pas "
        "quand ce risque a été reconnu.",
        "OWASP dates its EDITION (%s), not each of its entries. 1 January "
        "stands in as a filing rank; the source does not say when this risk "
        "was recognised."),

    # ── LE DOCUMENT EMPORTÉ ───────────────────────────────────────────────
    # UN PDF EXPORTÉ DEPUIS UNE INTERFACE ANGLAISE AVEC DES INTERTITRES
    # FRANÇAIS EST PIRE QU'UN DOCUMENT ENTIÈREMENT FRANÇAIS : le lecteur qui
    # le reçoit ne sait plus dans quelle langue est le texte qu'il n'a pas
    # encore lu.
    "exp.lecture": ("Lecture — %s", "Reading — %s"),
    "exp.change": ("Ce que cela change", "What this changes"),
    "exp.ignore": ("Ce qu'on ne sait pas", "What is not known"),
    "exp.source": ("La source", "The source"),
    "exp.statut": ("Statut : %s. %s", "Status: %s. %s"),
    "exp.origine": ("Document d'origine : %s", "Original document: %s"),
    "exp.licence": ("Licence : %s", "Licence: %s"),
    "exp.convention": (
        "  —  CETTE DATE N'EST PAS UNE OBSERVATION. %s",
        "  —  THIS DATE IS NOT AN OBSERVATION. %s"),
    "exp.pied": (
        "Exporté de CONSEILPREV INFO le %s",
        "Exported from CONSEILPREV INFO on %s"),
    "exp.pied.regle": (
        "Ce document reprend une fiche publiée, sans rien y réécrire. La "
        "lecture critique n'est pas le fait : sa nature est indiquée "
        "ci-dessus.",
        "This document reproduces a published entry without rewriting any of "
        "it. The critical reading is not the fact: its nature is stated "
        "above."),
    # LE DOCUMENT DIT DANS QUELLE LANGUE IL EST, et ce qui a été traduit.
    "exp.langue.fr": (
        "Version française. Les analyses de ce site sont écrites en français "
        "et traduites à la main ; ce document porte l'original.",
        "French version. This site's analyses are written in French and "
        "translated by hand; this document carries the original."),
    "exp.langue.en": (
        "Version anglaise. Les analyses sont dérivées de gabarits anglais "
        "écrits à la main — aucune traduction automatique n'intervient. Les "
        "titres, résumés et noms de techniques gardent la langue de leur "
        "source.",
        "English version. The analyses are derived from hand-written English "
        "templates — no machine translation is involved. Titles, summaries "
        "and technique names keep their source's own language."),
    "exp.langue.repli": (
        "RÉSERVE : cette fiche n'a pas encore de gabarit anglais. Les "
        "analyses ci-dessus sont donc en français, telles qu'elles ont été "
        "écrites, plutôt que passées à une machine.",
        "RESERVATION: this entry has no English template yet. The analyses "
        "above are therefore in French, as written, rather than run through "
        "a machine."),

    # ── LA REVUE EMPORTÉE ─────────────────────────────────────────────────
    # UNE REVUE DE PRESSE EST LE DOCUMENT QUI CIRCULE LE PLUS. Elle est
    # transférée, jointe à un comité, relue par quelqu'un qui n'a jamais vu le
    # site — et elle a l'autorité d'un résumé : le lecteur lui accorde d'avoir
    # vu ce qu'il n'a pas lu. Tout ce qui la relativise doit donc partir AVEC
    # elle, en tête et non en annexe.
    "exp.rv.hebdo": ("Revue de presse hebdomadaire",
                     "Weekly press review"),
    "exp.rv.mensuel": ("Revue mensuelle internationale",
                       "Monthly international review"),
    "exp.rv.compte": (
        "CE QUE CETTE REVUE COMPTE. Les fiches dont LE FAIT est daté de la "
        "période — jamais celles collectées pendant la période. Les deux "
        "dates ne coïncident pas : une faille est inscrite au catalogue des "
        "mois après avoir été exploitée. Une période sans entrée ne dit donc "
        "pas qu'il ne s'est rien passé : elle dit qu'aucun fait daté de ces "
        "jours-là n'est entré au corpus.",
        "WHAT THIS REVIEW COUNTS. The entries whose FACT is dated within the "
        "period — never the ones collected during the period. The two dates "
        "do not coincide: a flaw is catalogued months after being exploited. "
        "A period with no items therefore does not say that nothing "
        "happened: it says that no fact dated within those days has entered "
        "the corpus."),
    "exp.rv.regle": ("LA RÈGLE DE SÉLECTION. %s",
                     "THE SELECTION RULE. %s"),
    "exp.rv.compteur": ("%s fiche(s) — période précédente : %s (%s)",
                        "%s entry(ies) — previous period: %s (%s)"),
    "exp.rv.sujets": ("Par sujet : %s", "By topic: %s"),
    "exp.rv.sources": ("Par source : %s", "By source: %s"),
    "exp.rv.vide": (
        "Aucun fait daté de cette période n'est entré au corpus.",
        "No fact dated within this period has entered the corpus."),
    "exp.rv.retard": (
        "Cette période n'est pas celle en cours : elle s'est achevée il y a "
        "%s jours. Le fait le plus récent que le corpus porte est daté du %s.",
        "This period is not the current one: it ended %s days ago. The most "
        "recent fact the corpus carries is dated %s."),
    "exp.rv.absences": ("Ce que cette période ne dit pas",
                        "What this period does not say"),
    "exp.rv.muets": ("Sujets sans aucune entrée : %s",
                     "Topics with no item at all: %s"),
    "exp.rv.conv": (
        "Dates posées, écartées : %s fiche(s) de cette période portent une "
        "date que ce site a posée faute de mieux — un jeu annuel devient le "
        "1er janvier. Elles tomberaient toutes dans la même semaine.",
        "Set dates, left out: %s entry(ies) in this period carry a date this "
        "site set for want of better — an annual dataset becomes 1 January. "
        "They would all fall in the same week."),
    "exp.rv.hors": (
        "Sans territoire, écartées : %s fiche(s) ne rattachent le fait à "
        "aucun pays et ne nomment aucune entreprise. Elles ne sont ni "
        "internationales ni françaises.",
        "With no territory, left out: %s entry(ies) tie the fact to no "
        "country and name no company. They are neither international nor "
        "French."),
    "exp.rv.fr": (
        "France seulement, écartées : %s fiche(s) ne rattachent le fait qu'à "
        "la France.",
        "France only, left out: %s entry(ies) tie the fact to France alone."),
    "exp.rv.signees": ("Reportages et entretiens — ce qui ne se dérive pas",
                       "Reports and interviews — what cannot be derived"),
    "exp.rv.entree": ("%s · %s", "%s · %s"),
    "exp.rv.terr": ("Nommées : %s", "Named: %s"),
    "exp.rv.signe": ("Signé : %s, le %s", "Signed: %s, on %s"),
    "exp.rv.entretien": ("Entretien avec %s, %s — recueilli le %s",
                         "Interview with %s, %s — gathered on %s"),
    "exp.rv.pied.regle": (
        "Ce document reprend des fiches publiées, sans rien y réécrire ni "
        "rien y ajouter. Le classement par portée est celui du moteur, déjà "
        "publié sur chaque fiche ; les comptes sont des comptes. Aucune "
        "phrase de ce document n'apprécie ce qu'il range.",
        "This document reproduces published entries without rewriting or "
        "adding anything. The ordering by reach is the engine's, already "
        "published on each entry; the counts are counts. No sentence in this "
        "document appraises what it files."),
    "exp.rv.corpus.vide": (
        "AVERTISSEMENT : le corpus était vide au moment de cet export. Ce "
        "document ne dit donc rien de la période — il n'y avait rien à "
        "découper.",
        "WARNING: the corpus was empty when this document was exported. It "
        "therefore says nothing about the period — there was nothing to cut."),
}


# ═══════════════════════════════════════════════════════════════════════════
#  LE RENDU
# ═══════════════════════════════════════════════════════════════════════════

#: LES MOIS, DANS LES DEUX LANGUES. Ils vivent ici et non dans chaque module :
#: `ingestion.py` datait les fiches, `exporter.py` datait les documents, et les
#: deux auraient fini par écrire deux formats.
_MOIS = (("janvier", "January"), ("février", "February"), ("mars", "March"),
         ("avril", "April"), ("mai", "May"), ("juin", "June"),
         ("juillet", "July"), ("août", "August"), ("septembre", "September"),
         ("octobre", "October"), ("novembre", "November"),
         ("décembre", "December"))


def date(iso, langue):
    """« 2026-08-21 » → « 21 août 2026 » ou « 21 August 2026 ».

    LA FORME ANGLAISE EST BRITANNIQUE, sans virgule ni ordinal : c'est celle
    des normes et des textes réglementaires que ce corpus cite, et elle ne se
    confond avec aucune autre — « 08/21 » et « 21/08 » ne se distinguent pas à
    l'œil. Une date ISO laissée nue dans un texte signale un contenu non relu,
    dans les deux langues."""
    from datetime import date as _d
    try:
        v = _d.fromisoformat(str(iso)[:10])
    except (TypeError, ValueError):
        return str(iso)
    return "%d %s %d" % (v.day, _MOIS[v.month - 1][LANGUES.index(langue)], v.year)


def _cote(valeur, langue):
    """Un argument peut être bilingue. Passé en couple `(fr, en)`, il suit la
    langue du gabarit qui l'accueille — sans quoi une phrase anglaise
    porterait « éolien » au milieu."""
    if isinstance(valeur, tuple) and len(valeur) == 2 \
            and all(isinstance(x, str) for x in valeur):
        return valeur[LANGUES.index(langue)]
    return valeur


def dire(cle, langue, *args):
    if cle not in G:
        raise KeyError("gabarit inconnu : %s" % cle)
    if langue not in LANGUES:
        raise ValueError("langue inconnue : %s" % langue)
    modele = G[cle][LANGUES.index(langue)]
    if not args:
        return modele
    return modele % tuple(_cote(a, langue) for a in args)


def deux(cle, *args):
    """Le même gabarit dans les deux langues, avec les mêmes arguments."""
    return tuple(dire(cle, l, *args) for l in LANGUES)


class Deux(object):
    """UN ACCUMULATEUR DE PHRASES DANS LES DEUX LANGUES À LA FOIS.

    POURQUOI CETTE FORME PLUTÔT QUE DEUX FONCTIONS PARALLÈLES. La lecture
    critique d'une fiche KEV se compose de trois à quatre phrases choisies
    selon les champs du catalogue. Écrire un constructeur français et un
    constructeur anglais reviendrait à tenir deux fois la même logique de
    choix : elles finiraient par ne plus retenir les mêmes phrases dans les
    mêmes cas, et personne ne le verrait — le français, lui, continuerait à
    marcher. Ici la logique s'écrit une fois ; seule la table a deux colonnes.
    """

    def __init__(self):
        self._fr, self._en = [], []

    def plus(self, cle, *args):
        fr, en = deux(cle, *args)
        self._fr.append(fr)
        self._en.append(en)
        return self

    def brut(self, fr, en=None):
        """Un fragment qui n'est pas un gabarit — une donnée de la source, un
        nombre, une énumération déjà composée. `en` vaut `fr` par défaut : une
        liste de valeurs chiffrées est la même dans les deux langues."""
        self._fr.append(fr)
        self._en.append(fr if en is None else en)
        return self

    def coller(self, cle, *args):
        """Comme `plus`, mais sans espace devant — pour un gabarit qui porte
        déjà son espace ou sa ponctuation d'attaque."""
        fr, en = deux(cle, *args)
        if self._fr:
            self._fr[-1] += fr
            self._en[-1] += en
        else:
            self._fr.append(fr)
            self._en.append(en)
        return self

    def rendre(self, sep=" "):
        return sep.join(self._fr).strip(), sep.join(self._en).strip()


def champs(prefixe, cle, *args):
    """Un champ de fiche et son jumeau anglais, en un seul appel.

    `champs("portee", "kev.portee")` rend `{"portee": …, "portee_en": …}`.
    Écrire les deux clés à la main marcherait aussi — jusqu'au jour où l'une
    des deux serait oubliée, et ce jour-là c'est l'anglaise.
    """
    fr, en = deux(cle, *args)
    return {prefixe: fr, prefixe + "_en": en}


# ═══════════════════════════════════════════════════════════════════════════
#  L'ÉTAT DE LA TABLE — servi par `/api/sante`, comme tout le reste.
# ═══════════════════════════════════════════════════════════════════════════

def defauts():
    """Ce qui ne va pas dans la table, énuméré plutôt que supposé.

    Un gabarit dont les deux colonnes ne portent pas les mêmes emplacements de
    substitution lève une exception À LA COLLECTE, donc en production, et pour
    la seule langue fautive. Il vaut mieux le savoir ici."""
    out = []
    for cle, v in sorted(G.items()):
        if not isinstance(v, tuple) or len(v) != len(LANGUES):
            out.append("%s : %d colonne(s) au lieu de %d"
                       % (cle, len(v) if isinstance(v, tuple) else 1,
                          len(LANGUES)))
            continue
        for i, x in enumerate(v):
            if not isinstance(x, str) or not x.strip():
                out.append("%s : colonne %s vide" % (cle, LANGUES[i]))
        places = [_place(x) for x in v if isinstance(x, str)]
        if len(set(map(tuple, places))) > 1:
            out.append("%s : emplacements différents %s"
                       % (cle, " / ".join(map(str, places))))
    return out


def sante():
    return {"gabarits": len(G), "langues": list(LANGUES), "defauts": defauts()}
