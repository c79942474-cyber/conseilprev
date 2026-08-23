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
    "cf.dev.t":        ["Rien. Il est lu en mémoire, confronté, puis jeté avec la requête. Aucune copie n'est écrite sur disque, aucun extrait n'est conservé, et la réponse renvoyée à votre navigateur ne contient pas le texte déposé — seulement des termes et des comptes. Un cabinet qui garderait les documents de ses prospects pour « améliorer son service » ferait précisément ce qu'un industriel redoute en confiant son architecture.",
                        "Nothing. It is read in memory, compared, then discarded with the request. No copy is written to disk, no extract is kept, and the answer sent back to your browser does not contain the uploaded text — only terms and counts. A firm that kept its prospects' documents to “improve its service” would do precisely what an industrial operator fears when handing over its architecture."],
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
    "fi.retour":       ["← Retour au fil", "← Back to the feed"],
    "fi.chargement":   ["Chargement de la fiche…", "Loading the entry…"],
    "fi.pi.b":         ["La lecture critique n'est pas le fait.",
                        "The critical reading is not the fact."],
    "fi.pi.t":         ["Elle est signalée comme dérivée par règles — reproductible, sans modèle de langage — ou rédigée et signée par un analyste.",
                        "It is flagged as derived by rules — reproducible, no language model — or written and signed by an analyst."]
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

  function demarrer() {
    monter();
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
               choisir: choisir, date: date };

  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", demarrer);
  else demarrer();
})();
