/* LA BASCULE FRANÇAIS / ANGLAIS — et ce qu'elle refuse de faire.
   ──────────────────────────────────────────────────────────────
   CE QUI EST TRADUIT : l'interface. Les intitulés, les rubriques, les
   libellés de filtre, les réserves éditoriales — tout ce que le cabinet a
   écrit. Chaque phrase anglaise de ce fichier a été ÉCRITE, pas produite : ce
   site n'emploie aucune traduction automatique, et s'en servir pour sa propre
   interface pendant qu'il l'interdit à son corpus serait une hypocrisie.

   CE QUI NE L'EST PAS : la lecture critique, la portée et l'incertitude de
   chaque fiche. Elles sont DÉRIVÉES par des gabarits écrits en français dans
   `ingestion.py`. Les traduire demanderait des gabarits anglais — un vrai
   travail, pas un réglage. Les passer à la machine reviendrait à produire du
   texte par modèle de langage, ce que ce site refuse à chaque page.

   ET CELA SE DIT, À L'ÉCRAN, AU MOMENT DE LA BASCULE. Une interface anglaise
   posée sur un corpus français est un mensonge par omission : le lecteur qui
   voit des paragraphes français en conclut que le site est cassé, ou pire, ne
   les lit pas et croit avoir tout vu. Le compte affiché vient du serveur
   (`veille.langues()`), jamais d'une phrase écrite une fois pour toutes.

   POURQUOI UN DICTIONNAIRE ET NON QUATRE PAGES DUPLIQUÉES. Deux jeux de
   fichiers HTML divergeraient à la première correction — et c'est toujours la
   version la moins lue qui reste en arrière, c'est-à-dire l'anglaise. */
(function () {
  "use strict";

  var CLE = "cpinfo.langue";
  var DEFAUT = "fr";

  var D = {
    /* ── Ce qui est commun aux quatre pages ─────────────────────────── */
    "or.retour":       ["← CONSEILPREV INFO", "← CONSEILPREV INFO"],
    "or.marque":       ["CONSEILPREV INFO — ", "CONSEILPREV INFO — "],
    "or.veille":       ["veille sourcée", "sourced intelligence"],
    "or.confronter":   ["Confronter un document", "Compare a document"],
    "or.abonnement":   ["Votre abonnement", "Your subscription"],
    "lg.titre":        ["Langue", "Language"],

    /* ── La barre latérale ──────────────────────────────────────────── */
    "bl.ouvrir":       ["Ouvrir le menu", "Open the menu"],
    "bl.fermer":       ["Fermer le menu", "Close the menu"],
    "bl.etat":         ["Le corpus", "The corpus"],
    "bl.muettes":      ["source(s) muette(s)", "source(s) silent"],
    "bl.reste":        ["à lire", "left to read"],
    "bl.oublier":      ["Oublier", "Forget"],
    "bl.oublier.sur":  ["Oublier ce que vous avez lu ? Cette mémoire ne quitte jamais votre navigateur ; l'effacer ne touche à rien d'autre.",
                        "Forget what you have read? This memory never leaves your browser; clearing it touches nothing else."],
    "bl.pages":        ["Le site", "The site"],
    "bl.sections":     ["Sur cette page", "On this page"],
    "bl.fil":          ["Le fil", "The feed"],
    "bl.fil.dit":      ["Le corpus, filtrable", "The corpus, filterable"],
    "bl.conf":         ["Confronter un document", "Compare a document"],
    "bl.conf.dit":     ["Votre document en regard du corpus",
                        "Your document against the corpus"],
    "bl.abo":          ["Votre abonnement", "Your subscription"],
    "bl.abo.dit":      ["Sujets suivis et seuil d'alerte",
                        "Topics followed and alert threshold"],
    "bl.legende":      ["La légende", "The key"],
    "bl.leg.non":      ["Le référentiel n'a pas répondu. La légende manque, plutôt que d'être écrite en dur ici — où elle survivrait à la panne en affirmant des couleurs que le moteur n'emploie peut-être plus.",
                        "The reference index did not answer. The key is missing rather than hard-coded here, where it would outlive the failure and assert colours the engine may no longer use."],
    "bl.leg.neuf":     ["Fiche non encore ouverte", "Card not yet opened"],
    "bl.leg.lu":       ["Fiche déjà ouverte", "Card already opened"],
    "bl.vieprivee":    ["Ce que ce site garde de vous",
                        "What this site keeps about you"],
    "bl.lu.non":       ["Mémoire de lecture non tenue.",
                        "Reading memory not kept."],
    "bl.lu.non.lien":  ["L'activer", "Turn it on"],

    /* ── La manchette ───────────────────────────────────────────────
       L'« édition » n'est pas une décision d'éditeur : c'est la date de
       collecte, et elle est écrite comme telle. */
    "mn.edition":      ["Édition du", "Edition of"],
    "mn.fiches":       ["fiches au corpus", "entries in the corpus"],
    "mn.rupt":         ["en rupture", "breaking"],
    "mn.src.ok":       ["toutes les sources ont répondu",
                        "every source answered"],

    /* ── Les quatre flèches ─────────────────────────────────────────
       CHAQUE INTITULÉ DIT CE QUE LE BOUTON FERA, ou pourquoi il ne fera
       rien. Une flèche éteinte sans motif se lit comme une panne ; avec le
       motif, elle enseigne comment s'en servir. */
    "fl.titre":        ["Parcourir la page et le fil",
                        "Move through the page and the feed"],
    "fl.haut":         ["Haut de la page", "Top of the page"],
    "fl.bas":          ["Bas de la page", "Bottom of the page"],
    "fl.courte":       ["La page tient à l'écran : il n'y a rien à parcourir.",
                        "The page fits on the screen: there is nothing to scroll to."],
    "fl.prec":         ["Fiche précédente", "Previous entry"],
    "fl.suiv":         ["Fiche suivante", "Next entry"],
    "fl.rang":         ["{r} sur {n} du fil", "{r} of {n} in the feed"],
    "fl.prem":         ["Première fiche du fil que vous lisiez.",
                        "First entry of the feed you were reading."],
    "fl.dern":         ["Dernière fiche du fil que vous lisiez.",
                        "Last entry of the feed you were reading."],
    "fl.sansfil":      ["Cette fiche a été ouverte par un lien direct : il n'y a pas de fil autour d'elle. Passez par la première page pour en avoir un.",
                        "This entry was opened from a direct link: there is no feed around it. Go through the front page to get one."],
    "fl.horsfiche":    ["Ces deux flèches parcourent le fil, d'une fiche à la suivante. Il n'y a pas de fiche ici.",
                        "These two arrows move through the feed, from one entry to the next. There is no entry here."],
    "fl.rub.prec":     ["Rubrique précédente", "Previous section"],
    "fl.rub.suiv":     ["Rubrique suivante", "Next section"],
    "fl.rub.prem":     ["Première rubrique de la page.", "First section of the page."],
    "fl.rub.dern":     ["Dernière rubrique de la page.", "Last section of the page."],
    "fl.filtre":       ["{n} filtre(s) actif(s)", "{n} filter(s) active"],
    "fl.toutcorpus":   ["tout le corpus", "the whole corpus"],

    /* ── Ce que ce site ne lit pas encore ───────────────────────────── */
    "r.brancher":      ["Ce que ce site ne lit pas encore — et pourquoi",
                        "What this site does not read yet — and why"],
    "r.brancher.b":    ["Toutes ne se règlent pas de la même façon.",
                        "They are not all fixed the same way."],
    "r.brancher.t":    ["Certaines sont refusées par le réseau de l'environnement de conception et se brancheront au déploiement ; d'autres demandent un contrat commercial, et aucune quantité de code n'y supplée. C'est le cas des dépêches d'agence. Ce site cite la licence de chaque source sous chaque fiche : publier sans licence reviendrait à écrire une mention fausse à l'endroit précis où il promet de dire vrai.",
                        "Some are refused by the design environment's network and will connect on deployment; others require a commercial contract, and no amount of code substitutes for one. That is the case for wire-service dispatches. This site cites each source's licence under every entry: publishing without one would mean writing a false notice at the exact place where it promises to tell the truth."],
    "br.faudrait":     ["Ce qu'il faudrait :", "What it would take:"],
    "br.sources":      ["source(s)", "source(s)"],

    /* ── La langue des analyses ──────────────────────────────────────
       DEUX RÉGLAGES ET NON UN, parce que les deux sens existent : un
       francophone qui travaille en anglais veut l'interface en anglais et
       les analyses dans leur version d'origine ; un anglophone qui reçoit
       un lien veut l'inverse. */
    "an.titre":        ["Les analyses", "The analyses"],
    "an.suit":         ["Elles suivent la langue de l'interface. Choisissez pour fixer.",
                        "They follow the interface language. Choose one to fix it."],
    "an.fixe":         ["Fixée par vous : la bascule d'interface ne la changera plus.",
                        "Fixed by you: the interface switch will no longer change it."],
    "an.repli":        ["Analyse en français — pas encore de gabarit anglais pour cette source. Rien n'est passé à une machine.",
                        "Reading in French — no English template for this source yet. Nothing has been run through a machine."],

    /* ── L'accord, et l'inventaire de ce qui est gardé ──────────────── */
    "vp.titre":        ["Une seule chose vous est demandée",
                        "One thing, and one only, is asked of you"],
    "vp.dit":          ["Ce site ne pose aucun cookie. Il peut garder, dans votre navigateur seul, les fiches que vous avez ouvertes — pour vous montrer ce qui est arrivé depuis votre dernière visite. C'est la seule chose qui s'écrirait sans que vous l'ayez demandée, donc la seule que nous demandons. Ne rien répondre vaut refus.",
                        "This site sets no cookie. It can keep, in your browser only, which cards you have opened — so it can show you what has arrived since your last visit. That is the only thing that would be written without your asking, so it is the only thing we ask about. Not answering counts as a refusal."],
    "vp.oui":          ["Garder ma progression", "Keep my progress"],
    "vp.non":          ["Ne rien garder", "Keep nothing"],
    "vp.savoir":       ["L'inventaire complet", "The full inventory"],
    "vp.etat.on":      ["Votre progression de lecture est gardée dans ce navigateur.",
                        "Your reading progress is kept in this browser."],
    "vp.etat.off":     ["Rien n'est gardé de votre lecture.",
                        "Nothing is kept about your reading."],

    /* ── La réserve de traduction ───────────────────────────────────── */
    "tr.titre":        ["Ce que la bascule ne traduit pas",
                        "What this switch does not translate"],

    /* ── L'accueil ──────────────────────────────────────────────────── */
    "ac.devise":       ["Cybersécurité industrielle · Intelligence artificielle · Systèmes d'IA · Centres de données.",
                        "Industrial cybersecurity · Artificial intelligence · AI systems · Data centres."],
    "ac.devise.b":     ["Chaque information porte sa source, sa date et une lecture critique dont la provenance est écrite",
                        "Every item carries its source, its date and a critical reading whose provenance is stated"],
    "ac.devise.fin":   ["— dérivée par règles publiées, ou rédigée et signée. Rien n'est produit par un modèle de langage.",
                        "— derived by published rules, or written and signed. Nothing here is produced by a language model."],

    "f.sujet":         ["Sujet", "Topic"],
    "f.pays":          ["Pays", "Country"],
    "f.techno":        ["Technologie", "Technology"],
    "f.portee":        ["Portée", "Reach"],
    "f.horizon":       ["Horizon", "Horizon"],
    "f.depuis":        ["Depuis", "Since"],
    "f.recherche":     ["Recherche", "Search"],
    "f.tous":          ["Tous", "All"],
    "f.toutes":        ["Toutes", "All"],
    "f.placeholder":   ["mot du titre ou du texte", "word from the title or the text"],
    "f.pays.vide":     ["Aucun pays sur ces fiches", "No country on these entries"],
    "f.techno.vide":   ["Aucune technologie sur ces fiches",
                        "No technology on these entries"],
    "f.plier":         ["Filtres", "Filters"],
    "f.actifs":        ["actif(s)", "active"],
    "f.aucun.actif":   ["aucun", "none"],
    "f.raz":           ["Tout afficher", "Show everything"],

    "et.chargement":   ["Chargement de la veille…", "Loading…"],

    "r.dossiers":      ["Dossiers — ce que le corpus regroupe de lui-même",
                        "Clusters — what the corpus groups on its own"],
    "r.dossiers.dit":  ["Ces regroupements ne sont pas des rubriques décidées à l'avance : ce sont les termes qui reviennent dans plusieurs titres, toutes sources confondues.",
                        "These groupings are not sections decided in advance: they are the terms recurring across several titles, all sources taken together."],
    "r.dossiers.dit.b": ["C'est un rapprochement de vocabulaire",
                         "This is a vocabulary match"],
    "r.dossiers.fin":  ["— il signale une famille de faits, il ne prouve aucune relation entre eux.",
                        "— it flags a family of facts, it proves no relation between them."],

    "r.une":           ["À la une — ce qui rompt", "Front page — what breaks"],
    "r.fil":           ["Le fil — tout le corpus filtré", "The feed — the whole filtered corpus"],

    "r.pistes":        ["Pistes d'instruction — ce que le corpus permet d'ouvrir",
                        "Lines of enquiry — what the corpus lets you open"],
    "r.pistes.b1":     ["Ce ne sont pas des recommandations.", "These are not recommendations."],
    "r.pistes.t1":     ["Chaque piste dit ce qui la déclenche, avec les fiches nommées, ce qu'elle suppose, et",
                        "Each one states what triggers it, naming the entries, what it assumes, and"],
    "r.pistes.b2":     ["ce qu'elle n'établit pas", "what it does not establish"],
    "r.pistes.t2":     ["— à commencer par l'existence d'un acheteur. Aucune ne porte de chiffre de marché : le corpus n'en contient aucun, et en produire un reviendrait à l'inventer. Elles sont rangées par",
                        "— starting with whether a buyer exists at all. None carries a market figure: the corpus holds none, and producing one would mean inventing it. They are ordered by"],
    "r.pistes.b3":     ["solidité du déclencheur", "strength of the trigger"],
    "r.pistes.t3":     [", pas par attrait commercial supposé, que ce site n'a aucun moyen d'évaluer.",
                        ", not by presumed commercial appeal, which this site has no way of assessing."],

    "r.sources":       ["Le registre des sources", "The register of sources"],
    "r.sources.st":    ["ce dont ce site a le droit de parler",
                        "what this site is allowed to speak about"],
    "r.sources.b1":    ["Une fiche qui ne cite aucune de ces sources n'est pas publiable",
                        "An entry citing none of these sources cannot be published"],
    "r.sources.t1":    ["— le moteur la refuse, elle n'est pas « affichée avec une réserve ». Chaque source porte ce qu'elle couvre",
                        "— the engine refuses it; it is not “shown with a caveat”. Each source carries what it covers"],
    "r.sources.b2":    ["et ce qu'elle ne couvre pas", "and what it does not cover"],
    "r.sources.t2":    [": une source dont on ne dirait que les forces finirait citée hors de son domaine. Le bouton « Sonder » va réellement chercher l'adresse et rend ce qu'elle répond, à l'instant.",
                        ": a source described only by its strengths ends up cited outside its domain. The “Probe” button actually fetches the address and reports what it answers, right now."],

    "pi.b1":           ["Ce que ce site ne fait pas.", "What this site does not do."],
    "pi.t1":           ["Il ne classe pas par pertinence supposée, ne note aucune information sur dix, et ne conclut pas à votre place. Il n'agrège pas non plus : deux sources qui se contredisent restent deux fiches contradictoires — la contradiction est l'information.",
                        "It does not rank by presumed relevance, does not score anything out of ten, and does not conclude on your behalf. Nor does it aggregate: two sources that contradict each other remain two contradictory entries — the contradiction is the information."],
    "pi.b2":           ["Ce que « vérifié » veut dire ici.", "What “verified” means here."],
    "pi.t2":           ["Que le fait a été confronté au document d'origine, pas à un article qui en parle. Le statut est écrit sur chaque fiche, et il commande la publication.",
                        "That the fact was checked against the original document, not against an article about it. The status is written on every entry, and it governs publication."],
    "pi.b3":           ["La lecture critique n'est pas le fait.", "The critical reading is not the fact."],
    "pi.t3":           ["Elle est signalée comme dérivée par règles — reproductible, sans modèle de langage — ou rédigée et signée par un analyste. Dans le second cas elle engage celui qui la signe.",
                        "It is flagged as derived by rules — reproducible, no language model — or written and signed by an analyst. In the second case it commits whoever signs it."],
    "pi.fam":          ["CONSEILPREV — Paris · Ce site complète",
                        "CONSEILPREV — Paris · This site complements"],
    "pi.fam2":         ["(cybersécurité industrielle et ingénierie de centres de données) et",
                        "(industrial cybersecurity and data-centre engineering) and"],
    "pi.fam3":         ["(gouvernance de l'IA et décision d'investissement).",
                        "(AI governance and investment decisions)."],

    /* ── Confronter un document ─────────────────────────────────────── */
    "cf.titre":        ["Confronter un document", "Compare a document"],
    "cf.devise":       ["Déposez un document — politique de sécurité, cahier des charges, note d'architecture — et voyez",
                        "Upload a document — a security policy, a specification, an architecture note — and see"],
    "cf.devise.b":     ["quelles fiches du corpus traitent de ce dont il parle",
                        "which entries in the corpus deal with what it talks about"],
    "cf.devise.fin":   [". C'est une entrée dans la veille par votre propre vocabulaire.",
                        ". It is a way into the corpus through your own vocabulary."],
    "cf.ne.b":         ["Ce que cet outil ne fait pas, et ne fera pas.",
                        "What this tool does not do, and will not do."],
    "cf.ne.t":         ["Il", "It"],

    "cf.l.fichier":    ["Votre document", "Your document"],
    "cf.l.sujet":      ["Rubrique de comparaison", "Section to compare against"],
    "cf.o.deduire":    ["Déduire de mon document", "Infer it from my document"],
    "cf.b.envoyer":    ["Confronter au corpus", "Compare against the corpus"],
    "cf.formats":      ["Formats lus : .txt, .md, .docx, .pdf (le PDF doit porter du texte, pas des images numérisées).",
                        "Formats read: .txt, .md, .docx, .pdf (a PDF must carry text, not scanned images)."],
    "cf.aide.sujet":   ["Le corpus couvre quatre rubriques, votre document une seule. Confronté au tout, il reçoit des questions hors de son domaine. La rubrique est déduite de votre document et affichée — vous pouvez la corriger.",
                        "The corpus covers four sections, your document only one. Compared against all of it, it gets questions outside its field. The section is inferred from your document and displayed — you can correct it."],
    "cf.dev.b":        ["Ce que devient votre document.", "What becomes of your document."],
    "cf.dev.t":        ["Rien. Il est lu en mémoire, confronté, puis jeté avec la requête. Aucune copie n'est écrite sur disque, aucun extrait n'est conservé, et la réponse renvoyée à votre navigateur ne contient pas le texte déposé — seulement des termes et des comptes. Un cabinet qui garderait les documents de ses prospects pour « améliorer son service » ferait précisément ce qu'un industriel redoute en confiant son architecture. Si vous voulez qu'un document reste, c'est un acte distinct et délibéré : le classeur de votre compte, qui dit exactement ce qu'il garde et jusqu'à quand.",
                        "Nothing. It is read in memory, compared, then discarded with the request. No copy is written to disk, no extract is kept, and the answer sent back to your browser does not contain the uploaded text — only terms and counts. A firm that kept its prospects' documents to “improve its service” would do precisely what an industrial operator fears when handing over its architecture. If you want to keep a document here, that is a separate and deliberate act: your account's folder, which says exactly what it keeps and for how long."],
    "cf.compte.t":     ["Le document que vous déposez est une donnée d'exposition : ce qu'il contient renseigne sur votre installation. Le dépôt anonyme n'est donc pas ouvert.",
                        "The document you upload is exposure data: what it contains tells someone about your installation. Anonymous upload is therefore not open."],
    "cf.compte.a":     ["Connectez-vous ou créez un compte", "Sign in or create an account"],
    "cf.compte.fin":   [", puis revenez sur cette page.", ", then come back to this page."],
    "cf.pi.b":         ["Pourquoi l'absence d'un mot ne vaut pas l'absence de la chose.",
                        "Why a missing word is not a missing thing."],
    "cf.pi.t":         ["Votre document peut traiter parfaitement d'un sujet en l'appelant autrement — « cloisonnement » pour « segmentation », « journalisation » pour « traçabilité ». Tout ce qui est présenté ici comme manquant est donc une question à poser à votre document, jamais un manque constaté.",
                        "Your document may cover a topic perfectly well under another name — “partitioning” for “segmentation”, “logging” for “traceability”. Everything presented here as missing is therefore a question to put to your document, never an established gap."],

    /* ── Votre abonnement ───────────────────────────────────────────── */
    "ab.titre":        ["Votre abonnement", "Your subscription"],

    "cf.r.compte":     ["Compte requis", "Account required"],
    "cf.r.touche":     ["Ce que votre document touche", "What your document touches"],
    "cf.r.nomme":      ["Ce qu'il ne nomme pas", "What it does not name"],
    "ab.r.compte":     ["S'inscrire ou se connecter", "Sign up or sign in"],
    "ab.r.suivi":      ["Ce que vous suivez", "What you follow"],
    "cl.titre":        ["Votre classeur", "Your folder"],
    "cl.l.fichier":    ["Document à ranger", "Document to file"],
    "cl.b.ranger":     ["Ranger", "File it"],
    "cl.b.effacer":    ["Effacer", "Delete"],
    "cl.b.telecharger": ["Récupérer", "Download"],
    "cl.vide":         ["Votre classeur est vide.", "Your folder is empty."],
    "cl.vide2":        ["Ce que vous rangez ici n'est lisible que par votre compte, et par personne d'autre.",
                        "What you file here is readable by your account alone, and by no one else."],
    "cl.formats":      ["Formats rangés :", "Formats accepted:"],
    "cl.plafond":      ["Plafonds :", "Limits:"],
    "cl.plafond.dit":  ["%d documents, %d Mio par compte, %d Mio par document.",
                        "%d documents, %d MiB per account, %d MiB per document."],
    "cl.occupe":       ["occupé", "used"],
    "cl.effacer.sur":  ["Effacer ce document de votre classeur ? L'effacement est immédiat et ne peut pas être annulé.",
                        "Delete this document from your folder? Deletion is immediate and cannot be undone."],
    "cl.envoi":        ["Rangement en cours…", "Filing…"],
    "cl.range":        ["Document rangé.", "Document filed."],
    "cl.empreinte":    ["empreinte", "checksum"],
    "ab.r.bulletin":   ["Votre bulletin, tel qu'il partirait",
                        "Your bulletin, as it would be sent"],

    /* ── Ce que le JavaScript compose ───────────────────────────────── */
    /* Ces libellés ne sont pas dans le HTML : ils sont assemblés au rendu.
       Les laisser en français ferait une interface anglaise dont toutes les
       cartes restent françaises — le pire des deux. */
    "js.une.rien":     ["Rien ne rompt aujourd'hui.", "Nothing breaks today."],
    "js.fil.vide2":    ["Élargissez la sélection — le corpus ne contient peut-être rien sur ce croisement, et le site ne comble pas ce vide.",
                        "Widen the selection — the corpus may hold nothing on this intersection, and the site does not paper over the gap."],
    "js.lecture":      ["Lecture — ", "Reading — "],
    "js.change":       ["Ce que cela change", "What this changes"],
    "js.doute":        ["Ce qu'on ne sait pas", "What is not known"],
    "js.consulter":    ["consulter la source", "consult the source"],
    "js.corpus":       ["Corpus : ", "Corpus: "],
    "js.fiches":       ["fiche(s)", "entries"],
    "js.dossiers":     ["dossier(s)", "cluster(s)"],
    "js.pistes":       ["piste(s)", "line(s)"],
    "js.collectees":   [", collectées le ", ", collected on "],
    "js.muettes":      ["source(s) n'ont pas répondu :", "source(s) did not answer:"],
    "js.muettes.fin":  [". Les fiches affichées viennent des sources qui ont répondu ; aucune n'est complétée d'estimation.",
                        ". The entries shown come from the sources that answered; none is padded with an estimate."],
    "js.toutes.ok":    ["Toutes les sources interrogées ont répondu.",
                        "Every source queried answered."],
    "js.retenues":     ["retenues", "kept"],
    "js.affichees":    ["affichées", "shown"],
    "js.une.vide":     ["Aucune fiche du corpus filtré n'est classée « rupture ».",
                        "No entry in the filtered corpus is classed as a break."],
    "js.une.vide2":    ["C'est un constat, pas une panne : cette zone ne se remplit pas des fiches suivantes.",
                        "That is a finding, not a fault: this area is not padded with the next entries down."],
    "js.fil.vide":     ["Aucune fiche pour ces filtres.", "No entry matches these filters."],
    "js.pistes.vide":  ["Aucune piste aujourd'hui.", "No line of enquiry today."],
    "js.pistes.vide2": ["Aucun déclencheur ne trouve dans le corpus de quoi en former une.",
                        "No trigger finds enough in the corpus to form one."],
    "js.dos.vide":     ["Aucun terme ne revient sur assez de fiches pour former un dossier.",
                        "No term recurs across enough entries to form a cluster."],
    "js.non_listees":  ["non listée(s)", "not listed"],
    "js.delai":        ["Le serveur n'a pas répondu dans le délai.",
                        "The server did not answer within the time limit."],
    "js.erreur":       ["La veille n'a pas pu être chargée. Rechargez la page.",
                        "The feed could not be loaded. Reload the page."],
    "js.sonde.ko":     ["injoignable depuis ce serveur — l'état est dit, pas masqué",
                        "unreachable from this server — the state is stated, not hidden"],

    "ab.l.email":      ["Adresse professionnelle", "Work email address"],
    "ab.l.mdp":        ["Mot de passe", "Password"],
    "ab.l.seuil":      ["Seuil de signalement", "Alert threshold"],
    "ab.b.connexion":  ["Se connecter", "Sign in"],
    "ab.b.inscription": ["Créer un compte", "Create an account"],
    "ab.b.enregistrer": ["Enregistrer", "Save"],
    "ab.b.deconnexion": ["Se déconnecter", "Sign out"],
    "ab.b.effacer":    ["Effacer mon compte", "Delete my account"],
    "ab.devise.t":     ["Vous choisissez les sujets que vous suivez et le seuil à partir duquel un fait mérite de vous être signalé. Le bulletin ne contient rien qui ne soit déjà publié sur ce site : ni analyse rédigée pour l'envoi, ni fait requalifié pour remplir la semaine.",
                        "You choose the topics you follow and the threshold above which a fact is worth flagging to you. The bulletin contains nothing that is not already published on this site: no analysis written for the mailing, no fact requalified to fill the week."],
    "ab.devise.b":     ["Quand rien ne franchit votre seuil, le bulletin est vide et il le dit.",
                        "When nothing clears your threshold, the bulletin is empty and says so."],
    "ab.audessus":     ["et au-dessus", "and above"],
    "ab.aide.mdp":     ["Douze caractères au minimum. Une phrase entière vaut mieux qu'un mot compliqué : elle est plus longue, et vous la retenez.",
                        "Twelve characters minimum. A whole phrase beats a complicated word: it is longer, and you will remember it."],
    "ab.aide.defauts": ["Un nouveau compte suit d'abord tous les sujets, au seuil « structurant ». Vous réglez ce que vous suivez dès la connexion, sur cette page.",
                        "A new account starts by following every topic, at the “structural” threshold. You set what you follow as soon as you sign in, on this page."],
    "ab.mdp.garde":    ["Ce site ne conserve aucun mot de passe, ni en clair ni sous une forme réversible : seul un dérivé scrypt est gardé.",
                        "This site keeps no password, neither in clear text nor in any reversible form: only an scrypt derivation is stored."],
    "ab.aide.seuil":   ["Vous ne recevez que ce qui atteint ce seuil. Rien n'est ajouté « parce que c'était intéressant » : élargir votre bulletin sans vous le dire reviendrait à décider à votre place de ce qui mérite votre attention.",
                        "You receive only what reaches this threshold. Nothing is added “because it was interesting”: widening your bulletin without telling you would mean deciding on your behalf what deserves your attention."],
    "ab.pi.adresse":   ["Ce que devient votre adresse. Elle sert à composer et, le jour où l'envoi existera, à expédier ce bulletin. Rien d'autre : elle n'est ni revendue, ni recoupée, ni employée pour vous relancer.",
                        "What becomes of your address. It is used to compose and, once sending exists, to deliver this bulletin. Nothing else: it is not sold, cross-referenced, or used to chase you."],
    "ab.pi.effacement": ["L'effacement est réel. « Effacer mon compte » retire le compte du registre et ferme ses sessions. Rien n'est marqué « supprimé » tout en restant lisible.",
                         "Deletion is real. “Delete my account” removes the account from the register and closes its sessions. Nothing is flagged “deleted” while remaining readable."],

    /* ── La fiche ───────────────────────────────────────────────────── */
    "fi.croisement":   ["Croisement — ce qui porte sur la même décision",
                        "Cross-reference — what bears on the same decision"],
    "fi.liens":        ["lien(s)", "link(s)"],
    "fi.lien":         ["Lien", "Link"],
    "fi.rapproch":     ["Rapprochement", "Proximity"],
    "fi.voisinage":    ["Autour de la même date — ce n'est pas un lien",
                        "Around the same date — this is not a link"],
    "fi.sur":          ["sur", "of"],
    "fi.aucun":        ["Aucun lien établi.", "No link established."],
    "fi.aucun2":       ["Le corpus ne porte aujourd'hui aucune autre fiche rattachable à celle-ci par une règle écrite — ni le même fournisseur, ni le même territoire, ni une technologie commune. Rapprocher sans motif serait pire que de ne rien proposer.",
                        "The corpus currently holds no other entry attachable to this one by a written rule — not the same vendor, not the same territory, not a shared technology. Linking without a stated reason would be worse than offering nothing."],
    "fi.aucun.b":      ["Et ce n'est pas propre à cette fiche :",
                        "And this is not particular to this entry:"],
    "fi.aucun3":       ["aucune des {n} fiches du corpus n'a de lien fort aujourd'hui. Les sources branchées ne se recouvrent pas encore — un catalogue de vulnérabilités nomme un produit par entrée, un référentiel de modes opératoires n'en nomme aucun. La rubrique n'est pas en panne : elle est vide, et elle le dit.",
                        "none of the {n} entries in the corpus has a strong link today. The sources connected do not yet overlap — a vulnerability catalogue names one product per entry, a catalogue of attack techniques names none. The section is not broken: it is empty, and it says so."],
    "fi.absente":      ["Fiche introuvable.", "Entry not found."],
    "fi.absente2":     ["Aucune fiche publiée ne porte cet identifiant.",
                        "No published entry carries this identifier."],
    "fi.emporter":     ["Emporter cette fiche", "Take this entry with you"],
    "fi.emporter.dit": ["Le document reprend la fiche telle qu'elle est publiée — son statut, la nature de sa lecture, ce qu'on ne sait pas et sa source. Rien n'y est résumé ni réécrit : un document emporté circule sans sa page, il doit porter de quoi en juger.",
                        "The file carries the entry exactly as published — its status, the nature of its reading, what is not known, and its source. Nothing is summarised or rewritten: a document taken away travels without its page, so it must carry what is needed to judge it."],
    "fi.retour":       ["← Retour au fil", "← Back to the feed"],
    "fi.chargement":   ["Chargement de la fiche…", "Loading the entry…"],
    "fi.pi.b":         ["La lecture critique n'est pas le fait.",
                        "The critical reading is not the fact."],
    "fi.pi.t":         ["Elle est signalée comme dérivée par règles — reproductible, sans modèle de langage — ou rédigée et signée par un analyste.",
                        "It is flagged as derived by rules — reproducible, no language model — or written and signed by an analyst."],

    /* ── La page « ce que ce site garde de vous » ────────────────────
       ELLE EST TRADUITE COMME LE RESTE, et ce n'est pas un zèle. Une
       politique de confidentialité française servie sous une interface
       anglaise est le seul texte du site qu'un lecteur DOIT pouvoir lire
       dans sa langue : c'est celui par lequel il exerce ses droits. */
    "vp.h1":           ["Ce que ce site garde de vous",
                        "What this site keeps about you"],
    "vp.h1.b":         ["Aucun cookie. Aucune requête vers un tiers. Aucune mesure d'audience.",
                        "No cookie. No third-party request. No audience measurement."],
    "vp.h1.t":         ["Ce n'est pas une promesse : c'est un inventaire, et il tient sur cette page. Ce qui suit dit ce qui est écrit, où, pourquoi, combien de temps, et comment l'effacer.",
                        "This is not a promise: it is an inventory, and it fits on this page. What follows says what is written, where, why, for how long, and how to erase it."],
    "vp.r.choix":      ["Votre choix, et il n'y en a qu'un",
                        "Your choice, and there is only one"],
    "vp.choix.b":      ["Pourquoi ce site ne vous montre pas un mur de cookies.",
                        "Why this site does not show you a cookie wall."],
    "vp.choix.t":      ["Parce qu'il n'en pose aucun, et qu'un bandeau « Tout accepter » posé sur un site qui ne dépose rien apprend au lecteur que celui-ci fait comme les autres — alors que sa seule promesse est de ne pas le faire. L'article 5(3) de la directive ePrivacy exempte ce qui est strictement nécessaire au service que vous avez demandé : la langue que vous avez choisie, la barre que vous avez repliée, le jeton de votre session, le refus que vous avez exprimé. Une seule chose ici s'écrit toute seule, sans que vous l'ayez demandée — la liste des fiches que vous avez ouvertes. C'est donc la seule qui vous soit demandée.",
                        "Because it sets none, and an “Accept all” banner on a site that stores nothing teaches the reader that this site behaves like the others — when its only promise is that it does not. Article 5(3) of the ePrivacy Directive exempts what is strictly necessary for the service you asked for: the language you chose, the sidebar you collapsed, your session token, the refusal you expressed. One thing here writes itself, without your asking — the list of entries you have opened. That is therefore the only thing you are asked about."],
    "vp.choix.f":      ["Refuser coûte un clic, comme accepter, et peut se faire à tout moment depuis cette page. Ne rien répondre vaut refus : c'est le défaut, et il n'y a rien à faire pour l'obtenir.",
                        "Refusing costs one click, exactly like accepting, and can be done at any time from this page. Not answering counts as a refusal: that is the default, and nothing need be done to obtain it."],
    "vp.r.inv":        ["L'inventaire de ce qui est écrit dans votre navigateur",
                        "The inventory of what is written in your browser"],
    "vp.th.nom":       ["Nom", "Name"],
    "vp.th.quoi":      ["Ce que c'est", "What it is"],
    "vp.th.duree":     ["Combien de temps", "For how long"],
    "vp.th.regime":    ["Régime", "Regime"],
    "vp.l.langue":     ["La langue que vous avez choisie, FR ou EN.",
                        "The language you chose, FR or EN."],
    "vp.l.barre":      ["La barre latérale, repliée ou dépliée.",
                        "The sidebar, collapsed or open."],
    "vp.l.accord":     ["Votre réponse à la question ci-dessus.",
                        "Your answer to the question above."],
    "vp.l.analyses":   ["La langue dans laquelle vous avez choisi de lire les analyses, quand vous l'avez fixée séparément de celle de l'interface.",
                        "The language you chose for reading the analyses, when you have fixed it separately from the interface language."],
    "vp.l.jeton":      ["Le jeton de votre session, si vous vous connectez.",
                        "Your session token, if you sign in."],
    "vp.l.ordre":      ["L'ordre des fiches du fil que vous parcourez, tel qu'il est affiché — ce qui permet aux flèches « précédente » et « suivante » de dire où vous en êtes.",
                        "The order of the entries in the feed you are browsing, as displayed — which is what lets the “previous” and “next” arrows say where you are."],
    "vp.l.lues":       ["Les identifiants des fiches que vous avez ouvertes — au plus six cents, les plus anciens sortent.",
                        "The identifiers of the entries you have opened — six hundred at most, the oldest drop out."],
    "vp.d.jusqua":     ["Jusqu'à ce que vous effaciez les données du site.",
                        "Until you clear this site's data."],
    "vp.d.onglet":     ["La durée de l'onglet — il disparaît à sa fermeture.",
                        "The lifetime of the tab — it vanishes when you close it."],
    "vp.reg.exempt":   ["Exempté — c'est le service demandé",
                        "Exempt — this is the service you asked for"],
    "vp.reg.refus":    ["Exempté — garder un refus est nécessaire pour l'honorer",
                        "Exempt — keeping a refusal is necessary to honour it"],
    "vp.reg.auth":     ["Exempté — authentification", "Exempt — authentication"],
    "vp.reg.demande":  ["Demandé — voir ci-dessus", "Asked — see above"],
    "vp.inv.b":        ["Rien de tout cela n'est envoyé au serveur.",
                        "None of this is sent to the server."],
    "vp.inv.t":        ["Ce ne sont pas des cookies : un cookie accompagne chaque requête, celles-ci restent dans le navigateur et n'en sortent jamais. Le code qui les écrit ne contient ni fetch, ni XMLHttpRequest, ni sendBeacon — et un contrôle automatique refuse qu'ils y entrent.",
                        "These are not cookies: a cookie rides along with every request, whereas these stay in the browser and never leave it. The code that writes them contains no fetch, no XMLHttpRequest, no sendBeacon — and an automated check refuses to let them in."],
    "vp.r.srv":        ["Ce que le serveur garde", "What the server keeps"],
    "vp.srv.b":        ["Si vous n'avez pas de compte : rien.",
                        "If you have no account: nothing."],
    "vp.srv.t":        ["Lire ce site n'écrit aucune ligne à votre sujet. Il n'y a ni profil, ni identifiant de visiteur, ni mesure d'audience — aucun outil de ce genre n'est installé, et il n'y a donc rien à désactiver.",
                        "Reading this site writes no line about you. There is no profile, no visitor identifier, no audience measurement — no such tool is installed, so there is nothing to switch off."],
    "vp.srv.c1":       ["Un compte", "An account"],
    "vp.srv.t1":       ["porte votre adresse électronique, l'empreinte de votre mot de passe — jamais le mot de passe —, les sujets que vous suivez et votre seuil d'alerte. Rien d'autre.",
                        "holds your email address, the derivation of your password — never the password — the topics you follow and your alert threshold. Nothing else."],
    "vp.srv.c2":       ["Votre classeur", "Your file drawer"],
    "vp.srv.t2":       ["garde les documents que vous y déposez, et eux seuls, pour votre compte seul.",
                        "keeps the documents you put in it, and those alone, for your account alone."],
    "vp.srv.c3":       ["Un document confronté n'est pas conservé.",
                        "A compared document is not kept."],
    "vp.srv.t3":       ["Il est lu en mémoire, comparé, puis oublié avec la requête. La réponse ne contient jamais le texte déposé — seulement des termes et des comptes.",
                        "It is read in memory, compared, then forgotten with the request. The answer never contains the text you submitted — only terms and counts."],
    "vp.srv.mem.b":    ["Ces données vivent en mémoire du processus, et disparaissent à chaque redémarrage.",
                        "This data lives in the process's memory, and vanishes at every restart."],
    "vp.srv.mem.t":    ["Ce n'est pas une garantie de confidentialité, c'est une limite technique, et elle est écrite ici parce qu'elle vous concerne : un redémarrage de l'hébergeur — mise à jour, inactivité, incident — efface les comptes et les classeurs. Le site le dit aussi au moment du dépôt. Le jour où une base durable sera branchée, cette page changera avant elle.",
                        "This is not a privacy guarantee, it is a technical limit, and it is written here because it concerns you: a restart of the host — an update, idleness, an incident — erases accounts and file drawers. The site says so at the moment you upload, too. The day a durable database is connected, this page will change before it does."],
    "vp.r.tiers":      ["Les tiers, et pourquoi il n'y en a pas",
                        "Third parties, and why there are none"],
    "vp.t.c1":         ["Aucune police distante.", "No remote font."],
    "vp.t.t1":         ["Les caractères venaient de fonts.googleapis.com : une requête vers Google à chaque visite, avant tout consentement, emportant votre adresse IP, votre page de provenance et la signature de votre navigateur — pour de la typographie. Le tribunal régional de Munich a jugé ce montage contraire au RGPD le 20 janvier 2022. Les fichiers sont désormais servis par ce site.",
                        "The typefaces came from fonts.googleapis.com: a request to Google on every visit, before any consent, carrying your IP address, your referring page and your browser's signature — for typography. The Munich Regional Court held this arrangement contrary to the GDPR on 20 January 2022. The files are now served by this site."],
    "vp.t.c2":         ["Aucune image, aucun script, aucun cadre extérieur.",
                        "No external image, script or frame."],
    "vp.t.t2":         ["La politique de sécurité de contenu de ce site s'écrit default-src 'self', sans exception : le navigateur lui-même refuserait une requête vers un tiers.",
                        "This site's content security policy reads default-src 'self', with no exception: the browser itself would refuse a third-party request."],
    "vp.t.c3":         ["Les sources sont lues par le serveur, jamais par votre navigateur.",
                        "Sources are fetched by the server, never by your browser."],
    "vp.t.t3":         ["Consulter une fiche sur une vulnérabilité ne signale rien à la CISA, au MITRE ni à la Commission européenne. C'est le point : une veille qui ferait charger ses sources par le poste du lecteur renseignerait ces sources sur ce que cherche son entreprise. Suivre un lien vers une source, en revanche, vous y emmène — comme tout lien, et ce site n'envoie alors même pas la page d'où vous venez.",
                        "Reading an entry about a vulnerability signals nothing to CISA, MITRE or the European Commission. That is the point: an intelligence service that had the reader's machine load its sources would tell those sources what their company is looking for. Following a link to a source does take you there — as any link does, and this site does not even send the page you came from."],
    "vp.r.dr":         ["Vos droits, et par où ils passent",
                        "Your rights, and where they go through"],
    "vp.dr.c1":        ["Effacement.", "Erasure."],
    "vp.dr.t1":        ["Le bouton « Effacer mon compte », sur la page d'abonnement, efface le compte, ses réglages et son classeur dans la même opération. Il n'y a pas de corbeille ni de délai de grâce : rien n'en subsiste dans ce processus.",
                        "The “Delete my account” button, on the subscription page, erases the account, its settings and its file drawer in one operation. There is no bin and no grace period: nothing of it survives in this process."],
    "vp.dr.l1":        ["Aller à la page d'abonnement", "Go to the subscription page"],
    "vp.dr.c2":        ["Accès et rectification.", "Access and rectification."],
    "vp.dr.t2":        ["La page d'abonnement affiche tout ce que le serveur détient de vous — il n'y a pas d'autre champ ailleurs — et permet d'en changer les réglages.",
                        "The subscription page displays everything the server holds about you — there is no other field anywhere — and lets you change the settings."],
    "vp.dr.c3":        ["Ce qui est dans votre navigateur vous appartient.",
                        "What is in your browser belongs to you."],
    "vp.dr.t3":        ["Le bouton « Oublier », dans la barre latérale, efface la mémoire de lecture. Les réglages de votre navigateur effacent le reste, sans passer par ce site.",
                        "The “Forget” button, in the sidebar, clears the reading memory. Your browser's own settings clear the rest, without going through this site."],
    "vp.dr.man.b":     ["Ce que cette page n'a pas encore.",
                        "What this page does not have yet."],
    "vp.dr.man.t":     ["L'identité complète du responsable de traitement, son adresse postale et une adresse de contact dédiée aux demandes RGPD relèvent du cabinet, pas du moteur : les inventer ici donnerait une mention légale fausse, ce qui est pire que son absence. Elles seront écrites à cet endroit. En attendant, une demande passe par l'adresse de contact de CONSEILPREV.",
                        "The full identity of the data controller, its postal address and a contact address dedicated to GDPR requests are the firm's to give, not the engine's: inventing them here would produce a false legal notice, which is worse than none. They will be written in this spot. In the meantime, a request goes through CONSEILPREV's contact address."],
    "vp.r.sec":        ["Ce qui protège la connexion", "What protects the connection"],
    "vp.s.c1":         ["Le jeton de session ne voyage jamais dans l'adresse.",
                        "The session token never travels in the URL."],
    "vp.s.t1":         ["Il passe par l'en-tête Authorization : une adresse se retrouve dans les journaux du serveur, dans l'historique du navigateur et dans le référent envoyé aux tiers.",
                        "It goes through the Authorization header: a URL ends up in server logs, in browser history and in the referrer sent to third parties."],
    "vp.s.c2":         ["Le mot de passe n'est pas conservé.", "The password is not kept."],
    "vp.s.t2":         ["Seule son empreinte l'est, dérivée avec un sel propre à chaque compte.",
                        "Only its derivation is, computed with a salt unique to each account."],
    "vp.s.c3":         ["Les en-têtes de sécurité sont posés par l'application, pas par l'hébergeur.",
                        "Security headers are set by the application, not by the host."],
    "vp.s.t3":         ["Politique de sécurité de contenu fermée, nosniff, aucun référent, encadrement interdit, HSTS sur connexion chiffrée. Un réglage d'hébergeur disparaîtrait au premier déménagement sans que rien ne le signale ; ceux-ci voyagent avec le code, et des contrôles automatiques les vérifient sur des réponses réelles.",
                        "A closed content security policy, nosniff, no referrer, framing forbidden, HSTS over an encrypted connection. A host-side setting would vanish at the first move with nothing to signal it; these travel with the code, and automated checks verify them on real responses."],
    "vp.s.c4":         ["Une réponse d'inscription ne dit jamais si l'adresse était déjà connue.",
                        "A sign-up response never says whether the address was already known."],
    "vp.s.t4":         ["Ce serait confirmer à un tiers qu'une personne est abonnée ici.",
                        "That would confirm to a third party that someone subscribes here."],
    "vp.fin":          ["Cette page décrit l'état du code au jour de sa lecture. Elle est modifiée en même temps que ce qu'elle décrit, et jamais après : une politique de confidentialité écrite une fois puis oubliée finit par affirmer le contraire de ce que le site fait.",
                        "This page describes the state of the code on the day you read it. It is changed at the same time as what it describes, never after: a privacy policy written once and then forgotten ends up asserting the opposite of what the site does."]
  };

  function courante() {
    try {
      var v = localStorage.getItem(CLE);
      return (v === "fr" || v === "en") ? v : DEFAUT;
    } catch (e) { return DEFAUT; }
  }

  /* Le libellé demandé, dans la langue courante. UNE CLÉ INCONNUE SE VOIT :
     elle sort telle quelle, entre chevrons. Rendre une chaîne vide masquerait
     l'oubli, et c'est ainsi qu'une page finit par afficher des blancs. */
  function t(cle) {
    var e = D[cle];
    if (!e) return "‹" + cle + "›";
    return courante() === "en" ? e[1] : e[0];
  }

  function appliquer(racine) {
    var r = racine || document;
    Array.prototype.forEach.call(r.querySelectorAll("[data-i18n]"), function (el) {
      el.textContent = t(el.getAttribute("data-i18n"));
    });
    Array.prototype.forEach.call(r.querySelectorAll("[data-i18n-ph]"), function (el) {
      el.setAttribute("placeholder", t(el.getAttribute("data-i18n-ph")));
    });
    Array.prototype.forEach.call(r.querySelectorAll("[data-i18n-aria]"), function (el) {
      el.setAttribute("aria-label", t(el.getAttribute("data-i18n-aria")));
    });
    document.documentElement.setAttribute("lang", courante());
  }

  /* ── LA LANGUE DES ANALYSES, DISTINCTE DE CELLE DE L'INTERFACE ──────────
     POURQUOI DEUX RÉGLAGES ET NON UN. Depuis que les gabarits anglais
     existent, la bascule pourrait tout traduire d'un coup. Ce serait décider
     à la place du lecteur, et dans les deux sens :

       · un francophone qui travaille en anglais veut souvent l'interface en
         anglais ET les analyses dans leur version d'origine — c'est le texte
         que le cabinet a écrit, et il le relit tel quel ;
       · un anglophone qui reçoit un lien vers une fiche veut l'inverse.

     LE DÉFAUT SUIT L'INTERFACE, ce qui donne le comportement attendu sans
     rien régler. Une valeur écrite ne s'obtient que par un clic explicite, et
     elle prime alors — c'est ce que « ou pas » veut dire. */
  var CLE_ANALYSES = "cpinfo.analyses";

  function analyses() {
    try {
      var v = localStorage.getItem(CLE_ANALYSES);
      if (v === "fr" || v === "en") return v;
    } catch (e) { /* navigation privée : le défaut s'applique */ }
    return courante();
  }

  function analysesChoisies() {
    try {
      var v = localStorage.getItem(CLE_ANALYSES);
      return v === "fr" || v === "en";
    } catch (e) { return false; }
  }

  function choisirAnalyses(l) {
    if (l !== "fr" && l !== "en") return;
    try { localStorage.setItem(CLE_ANALYSES, l); } catch (e) { /* idem */ }
    marquer();
    /* UN ÉVÉNEMENT DISTINCT DE `langue` : changer la langue des analyses ne
       doit pas retraduire l'interface, et les pages n'ont pas les mêmes
       choses à refaire dans les deux cas. */
    document.dispatchEvent(new CustomEvent("analyses", { detail: { langue: l } }));
  }

  function choisir(l) {
    if (l !== "fr" && l !== "en") return;
    try { localStorage.setItem(CLE, l); } catch (e) { /* navigation privée */ }
    appliquer();
    marquer();
    /* LES PAGES RENDENT LEUR CONTENU EN JAVASCRIPT : les attributs ne
       suffisent pas. Chacune écoute cet évènement et se redessine — sans
       recharger, ce qui perdrait les filtres en cours. */
    document.dispatchEvent(new CustomEvent("langue", { detail: { langue: l } }));
  }

  function marquer() {
    var l = courante();
    Array.prototype.forEach.call(document.querySelectorAll("[data-lg]"), function (b) {
      var sien = b.getAttribute("data-lg") === l;
      b.className = "lg" + (sien ? " lg-on" : "");
      b.setAttribute("aria-pressed", sien ? "true" : "false");
    });
    var a = analyses();
    Array.prototype.forEach.call(document.querySelectorAll("[data-an]"), function (b) {
      var sien = b.getAttribute("data-an") === a;
      b.className = "lg" + (sien ? " lg-on" : "");
      b.setAttribute("aria-pressed", sien ? "true" : "false");
    });
    /* LE RÉGLAGE DIT S'IL SUIT L'INTERFACE OU S'IL A ÉTÉ CHOISI. Sans cela,
       un lecteur voit « FR » sélectionné et ne peut pas savoir si c'est son
       choix ou le défaut — donc s'il changera tout seul à la bascule
       suivante. */
    var e = document.getElementById("an-dit");
    if (e) e.textContent = t(analysesChoisies() ? "an.fixe" : "an.suit");
  }

  /* LA COMMANDE EST POSÉE PAR CE FICHIER, pas recopiée dans quatre pages.
     Quatre copies auraient divergé, et c'est toujours celle qu'on regarde le
     moins qui reste en arrière. */
  function monter() {
    var hote = document.querySelector("[data-langue]");
    if (!hote) return;
    hote.innerHTML =
      '<span class="lg-grp" role="group" data-i18n-aria="lg.titre">'
      + '<button type="button" class="lg" data-lg="fr" lang="fr">FR</button>'
      + '<button type="button" class="lg" data-lg="en" lang="en">EN</button>'
      + '</span>';
    Array.prototype.forEach.call(hote.querySelectorAll("[data-lg]"), function (b) {
      b.addEventListener("click", function () { choisir(b.getAttribute("data-lg")); });
    });
  }

  /* LA COMMANDE DES ANALYSES, posée là où la page la demande. Elle n'est pas
     dans l'oreille avec celle de l'interface : deux bascules côte à côte se
     confondent, et celle-ci demande une phrase pour dire ce qu'elle règle. */
  function monterAnalyses() {
    var hote = document.querySelector("[data-analyses]");
    if (!hote) return;
    hote.innerHTML =
      '<p class="an-t"><span data-i18n="an.titre">Les analyses</span>'
      + '<span class="lg-grp" role="group" data-i18n-aria="an.titre">'
      + '<button type="button" class="lg" data-an="fr" lang="fr">FR</button>'
      + '<button type="button" class="lg" data-an="en" lang="en">EN</button>'
      + '</span></p>'
      + '<p class="an-d" id="an-dit"></p>';
    Array.prototype.forEach.call(hote.querySelectorAll("[data-an]"), function (b) {
      b.addEventListener("click", function () {
        choisirAnalyses(b.getAttribute("data-an"));
      });
    });
  }

  function demarrer() {
    monter();
    monterAnalyses();
    appliquer();
    marquer();
  }

  /* LA DATE SUIT LA LANGUE, et elle est écrite ici pour les quatre pages.
     Quatre tables de mois recopiées auraient donné « 23 août 2026 » sur une
     interface anglaise — ce qui s'est produit, et qui est le genre de reste
     qui fait douter de tout le reste. */
  var MOIS = {
    fr: ["janvier","février","mars","avril","mai","juin","juillet","août",
         "septembre","octobre","novembre","décembre"],
    en: ["January","February","March","April","May","June","July","August",
         "September","October","November","December"]
  };
  function date(iso) {
    if (!iso) return "—";
    var p = String(iso).slice(0, 10).split("-");
    if (p.length !== 3) return String(iso);
    var l = courante(), m = MOIS[l][Number(p[1]) - 1], j = Number(p[2]);
    /* L'ordre change avec la langue : « 23 août 2026 » contre
       « 23 August 2026 » — même ordre ici, mais le mois, lui, doit suivre. */
    return j + " " + m + " " + p[0];
  }

  window.L = { t: t, courante: courante, appliquer: appliquer,
               choisir: choisir, date: date,
               analyses: analyses, choisirAnalyses: choisirAnalyses,
               analysesChoisies: analysesChoisies,
               /* La barre latérale se réécrit à chaque bascule : elle doit
                  pouvoir remonter la commande dans son hôte neuf. */
               monterAnalyses: function () { monterAnalyses(); marquer(); } };

  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", demarrer);
  else demarrer();
})();
