/* ══════════════════════════════════════════════════════════════════════════
   GUIDE DE PAGE — le bouton d'aide des pages publiques de CONSEILPREV

   POURQUOI. Sentinel a ses guides depuis longtemps : soixante-dix-huit
   panneaux, un guide chacun. Le SITE, lui, n'en avait aucun. Vingt-huit pages
   publiques — dont le panorama, l'observatoire, l'étude d'enveloppe et
   l'empreinte du parc, qui sont les documents les plus denses des deux sites —
   n'offraient au lecteur aucune indication sur ce qu'il regardait ni sur
   l'ordre dans lequel le lire.

   CE QUE CE MODULE POSE. Une barre discrète en tête de page, un bouton, et une
   fenêtre qui dit trois choses : à quoi sert la page, comment s'en servir, et
   ce qu'elle ne fait PAS. La troisième est celle qui manque partout ailleurs,
   et c'est celle qui évite de chercher dans une page ce qui n'y est pas.

   TROIS DÉCISIONS, ET CE QUI LES MOTIVE.

   1. L'ANCRAGE EST UNE PROPRIÉTÉ, PAS UNE CLASSE. Sur conseilprevcyber, le
      bouton s'ancrait sur `h1.page-h` ; les vingt-quatre fiches pays titrent
      autrement, et leur guide — pourtant écrit — est resté inatteignable des
      mois durant sans qu'aucune erreur ne le signale. Ici l'ancrage descend
      une échelle de replis : la barre de navigation de tête, sinon le bloc qui
      porte le premier titre, sinon un bouton flottant. Une page sans titre ni
      navigation — la carte plein écran en est une — garde son bouton.

   2. LA PALETTE SE LIT SUR LA PAGE. Le site public est sombre et violet ; le
      panorama et l'observatoire sont clairs, sur fond crème et accent terre
      cuite. Une palette écrite en dur serait juste sur la moitié des pages et
      illisible sur l'autre. Le module lit donc le fond réel du document et
      choisit un panneau clair ou sombre en conséquence.

   3. RIEN N'EST DEMANDÉ AUX PAGES. Aucune balise à ajouter, aucune feuille de
      style à modifier : vingt-huit fichiers à retoucher, c'est vingt-huit
      occasions d'en oublier un. Le style est injecté d'ici.
   ══════════════════════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  /* ── LES GUIDES ─────────────────────────────────────────────────────────
     Chacun est écrit à partir de ce que la page dit d'elle-même — titre,
     chapeau, intertitres. `t` le titre, `p` le chapeau, `s` les étapes,
     `k` les notions, `l` les liens. */
  var GUIDES = {};

  GUIDES["/"] = {
    t: "Tour de contrôle de la gouvernance IA",
    p: "La porte d’entrée de CONSEILPREV : les secteurs d’intervention, les six normes couvertes, les huit risques systémiques traités, et l’accès aux offres Sentinel.",
    s: ["Commencez par les huit risques systémiques : c’est la grille qui explique tout le reste du site.",
      "Passez aux offres Sentinel si vous cherchez l’outil, aux secteurs si vous cherchez la mission.",
      "Le bandeau du haut rappelle l’échéance du 2 août 2026 — c’est la date qui commande le calendrier de la plupart des organisations."],
    k: [["EU AI Act", "Le règlement (UE) 2024/1689. Il classe les systèmes d’IA par niveau de risque et attache des obligations à chaque niveau."],
      ["Sentinel", "La plateforme de conformité. Le site en présente les offres ; la plateforme elle-même se rejoint par la connexion."]],
    l: [["Les formules Sentinel", "/tarifications"], ["Nous écrire", "/support"]]
  };

  GUIDES["/support"] = {
    t: "Support et centre d’aide",
    p: "Le point de contact : réponse sous 24 heures ouvrées, et un numéro direct pour les urgences techniques.",
    s: ["Décrivez le problème avec la page ou l’écran concerné : c’est ce qui fait gagner le premier aller-retour.",
      "Pour une urgence technique, le téléphone est plus rapide que le formulaire.",
      "Une question sur la conformité elle-même n’est pas une demande de support : la FAQ y répond souvent mieux."],
    k: [["24 heures ouvrées", "Le délai porte sur les jours ouvrés : une demande du vendredi soir est traitée le lundi."]],
    l: [["Questions fréquentes", "/faq"], ["Ressources", "/ressources"]]
  };

  GUIDES["/faq"] = {
    t: "Questions fréquentes",
    p: "Les réponses courtes sur l’IA Act, le RGPD et la conformité — celles qui reviennent avant tout engagement.",
    s: ["Cherchez d’abord ici : la moitié des questions posées au support y ont déjà leur réponse.",
      "Une réponse courte n’est pas un avis juridique : pour votre cas, c’est un échange qu’il faut.",
      "Le lien de bas de page mène à un expert quand la réponse générique ne suffit pas."],
    k: [["Conformité et gouvernance", "Deux questions distinctes : être en règle, et savoir qui décide. La FAQ traite les deux, sans les confondre."]],
    l: [["Parler à un expert", "/support"], ["Ressources", "/ressources"]]
  };

  GUIDES["/tarifications"] = {
    t: "Comparer les formules",
    p: "Les trois formules Sentinel, comparées ligne à ligne : ce que chacune ouvre, ce qu’elle laisse fermé, et à partir de combien de systèmes elle cesse de suffire.",
    s: ["Partez du nombre de systèmes d’IA que vous devez inscrire au registre : c’est ce qui départage les formules.",
      "Comparez les colonnes plutôt que les prix : une formule moins chère qui exclut un module que vous devrez ouvrir de toute façon ne l’est pas.",
      "La formule gratuite existe et n’est pas une période d’essai : elle donne accès à un sous-ensemble durable."],
    k: [["Ce que la formule ne décide pas", "Le prix couvre l’outil, pas l’accompagnement. Un audit conduit et une plateforme ouverte sont deux dépenses distinctes."]],
    l: [["Les offres Sentinel", "/aies"], ["Nous écrire", "/support"]]
  };

  GUIDES["/formations"] = {
    t: "Formations conformité IA",
    p: "Dix formations, du cadrage réglementaire à la preuve opposable en contrôle. À distance en visioconférence, ou en présentiel à Paris.",
    s: ["Repérez d’abord votre rôle dans la colonne « public » : le même sujet ne se traite pas de la même façon pour un juriste et pour un ingénieur.",
      "Lisez les objectifs avant le programme : ils disent ce que vous saurez faire à la sortie, ce que le sommaire ne dit pas.",
      "Chaque module comporte un atelier sur un cas réel — prévoyez d’apporter le vôtre."],
    k: [["Preuve opposable", "Ce qu’un contrôle demande : non pas que vous ayez compris, mais que vous puissiez le démontrer, document en main."],
      ["Présentiel", "À Paris uniquement. Les sessions sur site se traitent au cas par cas."]],
    l: [["Nous écrire", "/support"], ["Les formules Sentinel", "/tarifications"]]
  };

  GUIDES["/empreinte"] = {
    t: "Notre empreinte numérique",
    p: "Ce que pèsent le site, la plateforme Sentinel et les modèles de langage utilisés, mesuré à partir de l’usage réel — méthode publiée, sources ouvertes, incertitudes affichées.",
    s: ["Lisez « Ce que nous comptons » avant les chiffres : un total dont on ignore le périmètre ne se compare à rien.",
      "Les trois méthodes sont appliquées aux MÊMES données : l’écart entre elles est l’information, pas le chiffre le plus flatteur.",
      "Terminez par « Ce que nous ne prétendons pas » — c’est la section qui borne la portée de tout le reste."],
    k: [["Intensité carbone", "Le facteur qui change tout : le même kilowattheure ne pèse pas le même carbone en France et en Pologne."],
      ["Incertitude affichée", "Une valeur sans fourchette est une valeur qu’on ne peut pas contredire, donc une valeur qu’on ne peut pas vérifier."]],
    l: [["Notre empreinte du parc étudié", "/empreinte-parc"], ["Ressources", "/ressources"]]
  };

  GUIDES["/actualites"] = {
    t: "Actualités",
    p: "Décryptages réglementaires et communiqués sur la gouvernance de l’IA, le RGPD et la cybersécurité.",
    s: ["Les décryptages datent : lisez la date avant le texte, la réglementation de l’IA bouge d’un trimestre à l’autre.",
      "Un décryptage explique un texte ; il ne remplace pas le texte, qui est toujours cité."],
    k: [["Décryptage", "Notre lecture d’un texte, avec ce qu’elle engage. Ce n’est pas une position officielle du législateur."]],
    l: [["Ressources", "/ressources"], ["Livre blanc", "/livre-blanc"]]
  };

  GUIDES["/ressources"] = {
    t: "Ressources",
    p: "Actualités, analyses, vidéos et podcasts sur l’IA Act, le RGPD et la gouvernance de l’IA.",
    s: ["Les quatre rubriques ne se lisent pas dans le même temps : les analyses se lisent, les démonstrations se regardent.",
      "Pour un sujet précis et daté, allez aux actualités ; pour une vue d’ensemble, au livre blanc."],
    k: [["Analyses et insights", "Des lectures argumentées, signées. Elles engagent leur auteur, pas le régulateur."]],
    l: [["Actualités", "/actualites"], ["Livre blanc", "/livre-blanc"]]
  };

  GUIDES["/livre-blanc"] = {
    t: "Baromètre IA et ROI des PME françaises",
    p: "L’analyse de deux cents déploiements d’IA et de leurs retours sur investissement, à partir de données opérationnelles réelles.",
    s: ["Lisez la méthodologie AVANT les chiffres : elle dit sur quoi porte l’échantillon, et donc à qui ces chiffres s’appliquent.",
      "Les cinq causes d’échec valent le retour sur investissement : elles disent où l’argent se perd, ce que les moyennes masquent.",
      "Le retour par secteur et par taille se lit ensemble — une PME de la santé ne ressemble pas à une PME de la logistique."],
    k: [["ROI", "Le retour sur investissement observé, non projeté. Les projections des éditeurs et les mesures des utilisateurs ne racontent pas la même histoire."],
      ["Limites", "Elles sont écrites en fin de document. Un baromètre sans limites déclarées est un argumentaire."]],
    l: [["Ressources", "/ressources"], ["Nous écrire", "/support"]]
  };

  GUIDES["/aies"] = {
    t: "AIES Platform — la suite de gouvernance",
    p: "Six modules intégrés pour la conformité IA Act, RGPD et cybersécurité, dans une interface unique.",
    s: ["Parcourez les six modules : ils correspondent aux six moments d’une démarche, pas à six produits.",
      "La feuille de route produit dit ce qui existe et ce qui vient — lisez-la avant de bâtir un plan sur une fonction annoncée."],
    k: [["Modules intégrés", "Ils partagent le même registre de systèmes. C’est ce partage qui distingue une suite d’une collection d’outils."]],
    l: [["Voir la plateforme en action", "/demo"], ["Les formules", "/tarifications"]]
  };

  GUIDES["/demo"] = {
    t: "AIES en action",
    p: "La démonstration : la gouvernance de l’IA en temps réel, sur des données de démonstration.",
    s: ["Suivez le parcours proposé plutôt que de cliquer au hasard : il montre l’enchaînement, qui est le sujet.",
      "Les données affichées sont des données de démonstration : les chiffres ne sont pas les vôtres et ne prétendent pas l’être."],
    k: [["Temps réel", "Les indicateurs se recalculent à mesure que le registre change. C’est ce que la démonstration cherche à montrer."]],
    l: [["La suite complète", "/aies"], ["Les formules", "/tarifications"]]
  };

  GUIDES["/platform"] = {
    t: "Plateforme de recrutement",
    p: "Décrivez un besoin, l’IA recherche les consultants, la carte les situe, la sélection se constitue et les contrats se préparent.",
    s: ["Décrivez le besoin en compétences ET en contexte : le contexte est ce qui départage deux profils équivalents sur le papier.",
      "La carte n’est pas décorative : la localisation décide souvent de la faisabilité d’une mission.",
      "La prévisualisation des contrats est un brouillon à relire, jamais un document à signer en l’état."],
    k: [["Recherche assistée", "L’outil propose ; le choix reste un choix humain, et il doit le rester — c’est aussi ce qu’exige l’IA Act sur les usages en ressources humaines."]],
    l: [["Le moteur de sourcing", "/sourcing"], ["Nous écrire", "/support"]]
  };

  GUIDES["/sourcing"] = {
    t: "Moteur de sourcing",
    p: "Trouver des experts IA, data science et cybersécurité, avec la conformité IA Act et RGPD intégrée à chaque mission.",
    s: ["Déposez un brief plutôt qu’une liste de mots-clés : c’est la mission qui trouve le profil, pas l’inverse.",
      "Regardez les profils disponibles pour calibrer votre brief avant de l’écrire."],
    k: [["Conformité intégrée", "Le rapprochement de profils est un usage d’IA en ressources humaines : il relève de l’Annexe III de l’IA Act, et la traçabilité du choix en fait partie."]],
    l: [["La plateforme de recrutement", "/platform"], ["Nous écrire", "/support"]]
  };

  GUIDES["/donnees"] = {
    t: "Conformité pilotée par la donnée",
    p: "Le raccordement aux données publiques françaises, pour ancrer la conformité IA Act, NIS2 et RGPD dans la réalité réglementaire.",
    s: ["Regardez d’abord quelles sources sont branchées : une donnée publique non raccordée est une intention, pas une source.",
      "Les données publiques datent, et leur fraîcheur est affichée — c’est elle qui décide de ce qu’on peut en conclure."],
    k: [["Donnée publique", "Ouverte et opposable, mais rarement à jour à la semaine. Elle situe ; elle ne remplace pas un relevé chez vous."]],
    l: [["La suite AIES", "/aies"], ["Nous écrire", "/support"]]
  };

  GUIDES["/team"] = {
    t: "Notre équipe",
    p: "Qui conduit les missions : parcours, spécialités et implantations.",
    s: ["Cherchez la spécialité plutôt que le titre : c’est elle qui dit qui répondra à votre sujet."],
    k: [["Équipe et réseau", "Les missions se conduisent avec un noyau permanent et des experts associés selon le domaine."]],
    l: [["Nous rejoindre", "/careers"], ["Nous écrire", "/support"]]
  };

  GUIDES["/careers"] = {
    t: "Nous rejoindre",
    p: "Les postes ouverts et les raisons de venir : une équipe internationale sur la conformité de l’IA.",
    s: ["Lisez « Pourquoi nous rejoindre » avant la liste : elle dit comment on travaille, ce que l’intitulé d’un poste ne dit jamais.",
      "Aucun poste ne correspond ? Une candidature spontanée argumentée se lit aussi."],
    k: [["Poste ouvert", "Ouvert signifie en cours de recrutement. Une annonce retirée l’est parce que le poste est pourvu."]],
    l: [["Notre équipe", "/team"], ["Nous écrire", "/support"]]
  };

  GUIDES["/business-developer"] = {
    t: "Business developer indépendant",
    p: "L’ouverture de la Business Unit IA et Cyber : un projet entrepreneurial avec des objectifs chiffrés et datés.",
    s: ["Lisez les objectifs chiffrés en premier : ils disent la nature de l’engagement attendu mieux qu’une description de poste.",
      "Le statut est indépendant, pas salarié — c’est la première question à trancher avant toute autre."],
    k: [["Business Unit", "Une activité distincte avec son compte d’exploitation. Ce n’est pas un rattachement à l’existant."]],
    l: [["Nous rejoindre", "/careers"], ["Nous écrire", "/support"]]
  };

  GUIDES["/map"] = {
    t: "Carte des acteurs IA, data et cyber",
    p: "Les implantations des acteurs de l’IA, de la donnée et de la cybersécurité en France, à partir de données publiques ouvertes.",
    s: ["Zoomez avant de cliquer : les repères se regroupent, et un repère peut en cacher plusieurs.",
      "Cliquez un repère pour sa fiche : nom, activité, score et source.",
      "Le compteur en haut à droite dit combien d’acteurs sont dans la vue courante — il change quand vous déplacez la carte."],
    k: [["Données publiques ouvertes", "Elles situent une implantation déclarée, pas une activité vérifiée sur place."],
      ["Ce que la carte ne dit pas", "Ni la taille réelle des équipes, ni leur disponibilité. Pour cela, c’est le moteur de sourcing."]],
    l: [["Le moteur de sourcing", "/sourcing"], ["Conformité par la donnée", "/donnees"]]
  };

  GUIDES["/accessibility"] = {
    t: "Accessibilité",
    p: "Les fonctions d’accessibilité de la plateforme et les raccourcis clavier disponibles.",
    s: ["Réglez d’abord le contraste et la taille : les deux se conservent d’une page à l’autre.",
      "Les raccourcis clavier sont listés en toutes lettres — ils fonctionnent sur l’ensemble du site.",
      "Une gêne qui n’est pas traitée ici se signale au support : c’est ainsi que la liste s’allonge."],
    k: [["WCAG 2.1 et RGAA", "Le référentiel international et sa déclinaison française. Le niveau atteint est affiché, critère par critère, et non revendiqué en bloc."]],
    l: [["Support", "/support"], ["Mentions légales", "/mentions-legales"]]
  };

  GUIDES["/mentions-legales"] = {
    t: "Mentions légales",
    p: "L’éditeur du site, l’hébergement, la propriété intellectuelle et les limites de responsabilité.",
    s: ["Cherchez l’éditeur et l’hébergeur : ce sont les deux mentions qu’une réclamation exige.",
      "Pour ce qui touche à vos données personnelles, c’est la politique de protection des données qui fait foi, pas cette page."],
    k: [["Propriété intellectuelle", "Le contenu du site est protégé. Une citation reste possible ; une reprise intégrale ne l’est pas."]],
    l: [["Protection des données", "/protection-donnees"], ["Conditions générales", "/cgv"]]
  };

  GUIDES["/protection-donnees"] = {
    t: "Protection des données",
    p: "Ce que nous collectons, pourquoi, sur quelle base légale, pour combien de temps — et comment exercer vos droits.",
    s: ["Trouvez la finalité qui vous concerne : c’est elle qui commande la base légale et la durée.",
      "La section « Vos droits » donne la marche à suivre et le délai de réponse.",
      "Les transferts et sous-traitants sont nommés : c’est la question à regarder si l’hébergement hors Union vous importe."],
    k: [["Base légale", "Consentement, contrat, obligation légale, intérêt légitime. Sans l’une d’elles, un traitement n’a pas le droit d’exister."],
      ["Articles 15 à 22", "Accès, rectification, effacement, limitation, portabilité, opposition, et le droit de ne pas subir une décision entièrement automatisée."]],
    l: [["Confidentialité", "/confidentialite"], ["Support", "/support"]]
  };

  GUIDES["/confidentialite"] = {
    t: "Politique de confidentialité",
    p: "Le détail du traitement de vos données, cookies et reCAPTCHA compris, au regard du RGPD et de l’IA Act.",
    s: ["Lisez la section cookies si vous voulez comprendre ce que le bandeau de consentement engage réellement.",
      "reCAPTCHA a sa propre section : c’est un service tiers, et il est nommé comme tel."],
    k: [["Cookies et technologies similaires", "Le stockage local et les pixels sont soumis aux mêmes règles que les cookies, même quand le mot n’apparaît pas."]],
    l: [["Protection des données", "/protection-donnees"], ["Mentions légales", "/mentions-legales"]]
  };

  GUIDES["/cgv"] = {
    t: "Conditions générales de vente",
    p: "Ce qui régit la relation contractuelle : services, tarifs, rétractation, résiliation, garanties et responsabilités.",
    s: ["Regardez la rétractation et la résiliation avant de souscrire : ce sont les deux clauses qu’on lit toujours trop tard.",
      "Les garanties disent ce qui est dû ; les responsabilités disent ce qui ne l’est pas. Les deux se lisent ensemble."],
    k: [["Droit de rétractation", "Il ne s’applique pas de la même façon à un professionnel et à un particulier : la section le précise."]],
    l: [["Les formules", "/tarifications"], ["Mentions légales", "/mentions-legales"]]
  };

  GUIDES["/dsa"] = {
    t: "Notre conformité au DSA",
    p: "Comment la plateforme applique le règlement européen sur les services numériques : pratiques interdites, signalement, transparence algorithmique et rapport.",
    s: ["Pour signaler un contenu, allez directement à la section « Signaler » — elle porte la procédure de l’article 16.",
      "La transparence algorithmique dit ce qui est recommandé et sur quel critère : c’est la section à lire si vous vous demandez pourquoi vous voyez ce que vous voyez."],
    k: [["Article 16", "L’obligation de mettre à disposition un mécanisme de signalement accessible et de traiter les signalements reçus."],
      ["Article 27", "L’obligation d’expliquer les paramètres principaux des systèmes de recommandation, en termes compréhensibles."]],
    l: [["Protection des données", "/protection-donnees"], ["Support", "/support"]]
  };

  /* ── LES QUATRE ÉTUDES ─────────────────────────────────────────────────
     Elles sont réservées aux abonnés, et ce sont les documents les plus
     denses des deux sites. Un lecteur qui y arrive sans guide cherche
     longtemps ce qu'il regarde. */

  GUIDES["/panorama"] = {
    t: "Panorama de l’IA déployée dans l’Union",
    p: "Deux inventaires sur la même carte : les cas d’IA documentés de mi-2023 à mi-2026, classés selon le Règlement (UE) 2024/1689, et les centres de données — avec profil de vulnérabilités, couche réglementaire des vingt-sept États membres et score d’exposition.",
    s: ["Choisissez d’abord la COUCHE — cas d’usage ou centres de données : la carte ne montre pas la même chose selon la couche active.",
      "Filtrez par classe de risque avant de conclure quoi que ce soit : un total qui mélange les classes ne dit rien d’opposable.",
      "Chaque point ouvre sa fiche, et chaque fiche cite sa source. Une valeur sans source affichée n’est pas dans ce document."],
    k: [["POC, pilote, production, abandon", "Quatre états distincts. Compter un abandon comme un déploiement gonfle le total de la façon la plus courante et la moins visible."],
      ["Score d’exposition", "Il croise la classe réglementaire et le profil de vulnérabilités. C’est un indicateur de priorité, pas un diagnostic de sécurité."],
      ["Ce que le panorama n’est pas", "Un recensement exhaustif. Il porte sur les cas DOCUMENTÉS : ce qui n’a pas été publié n’y figure pas, et c’est dit."]],
    l: [["L’enveloppe d’investissement", "/enveloppe"], ["L’empreinte du parc", "/empreinte-parc"]]
  };

  GUIDES["/enveloppe"] = {
    t: "Enveloppe d’investissement et DPGF",
    p: "Le chiffrage : enveloppe, décomposition par lot, comparaison entre pays et création de valeur — la suite du panorama, une fois le terrain situé.",
    s: ["Suivez le fil des étapes : chacune reprend les résultats de la précédente, et sauter une étape laisse un chiffre non fondé.",
      "Regardez la décomposition par lot avant le total : c’est elle qui se discute avec un maître d’ouvrage.",
      "La comparaison entre pays porte sur des coûts unitaires, pas sur des projets réels : elle situe un ordre de grandeur."],
    k: [["DPGF", "Décomposition du prix global et forfaitaire : le détail lot par lot derrière un prix unique."],
      ["Un chiffrage n’est pas un devis", "Il est bâti sur des quantités et des prix unitaires déclarés. Il sert à décider d’engager, pas à contracter."]],
    l: [["Le panorama", "/panorama"], ["L’empreinte du parc", "/empreinte-parc"]]
  };

  GUIDES["/empreinte-parc"] = {
    t: "Empreinte environnementale du parc",
    p: "Ce que pèse le parc recensé sur son cycle de vie : électricité, CO₂e selon le pays, fabrication amortie, eau de site et eau de la source — confronté aux repères publiés.",
    s: ["Comparez les sites entre eux plutôt que de lire un total : c’est l’écart qui désigne où agir.",
      "Distinguez l’eau de site de l’eau de la source : la seconde inclut celle consommée pour produire l’électricité, et elle est souvent la plus grande des deux.",
      "La confrontation aux repères publiés dit si votre valeur est ordinaire ou remarquable — un chiffre seul ne le dit jamais."],
    k: [["Fabrication amortie", "Le carbone de fabrication des équipements, réparti sur leur durée de vie. L’ignorer fait passer un renouvellement pour une amélioration."],
      ["Le périmètre est celui du parc CARTOGRAPHIÉ", "Un site non recensé ne pèse rien dans ce total. Le chiffre mesure ce qu’on a compté, pas ce qui existe."]],
    l: [["Le panorama", "/panorama"], ["Notre propre empreinte", "/empreinte"]]
  };

  GUIDES["/observatoire"] = {
    t: "Observatoire R&D IA",
    p: "Où se crée l’intelligence artificielle : modèles remarquables, chercheurs d’élite, brevets et adoption en entreprise — recomposé depuis les sources primaires publiques.",
    s: ["Chaque vue nomme sa source et sa date : lisez-les, elles ne couvrent pas toutes la même période.",
      "Les quatre angles — modèles, talents, brevets, adoption — se contredisent parfois. La contradiction est l’information : un pays peut publier beaucoup et déployer peu.",
      "Un brevet déposé n’est pas un brevet délivré, et aucun des deux n’est un produit."],
    k: [["Sources primaires", "Epoch AI, MacroPolo/NeurIPS, AI Index/CSET, Eurostat. Les vues sont recomposées depuis ces jeux, jamais recopiées d’un commentaire."],
      ["Chercheur d’élite", "La définition vient de la source (présence aux conférences de premier rang). Elle mesure une visibilité académique, pas une capacité industrielle."]],
    l: [["Le panorama", "/panorama"], ["Ressources", "/ressources"]]
  };

  var GUIDE_DEFAULT = {
    t: "Aide",
    p: "Cette page fait partie du site CONSEILPREV — gouvernance de l’intelligence artificielle, conformité et données.",
    s: ["Utilisez la navigation de tête pour revenir à l’accueil.",
      "Le support répond sous 24 heures ouvrées si cette page ne dit pas ce que vous cherchez."],
    k: [],
    l: [["Accueil", "/"], ["Support", "/support"]]
  };

  function guidePour(chemin) {
    var p = String(chemin || "/").replace(/\/+$/, "") || "/";
    return GUIDES[p] || null;
  }

  /* ── LA PALETTE SE LIT SUR LA PAGE ──────────────────────────────────────
     Le site public est sombre, les études sont claires. Une palette écrite
     en dur serait illisible sur la moitié des pages. */
  function _lum(c) {
    /* Une couleur ENTIÈREMENT TRANSPARENTE n'est pas une couleur : `rgba(0,0,0,0)`
       se lit « noir » si l'on ignore le canal alpha, et c'est exactement ce qui
       s'est produit — le fond déclaré de `body` est transparent sur les vingt-huit
       pages, si bien qu'un premier essai concluait « sombre » partout, y compris
       sur le panorama et l'observatoire, qui sont crème. */
    var m = String(c || "").match(/(\d+(?:\.\d+)?)[,\s]+(\d+(?:\.\d+)?)[,\s]+(\d+(?:\.\d+)?)(?:[,\s/]+(\d*\.?\d+))?/);
    if (!m) return null;
    if (m[4] !== undefined && parseFloat(m[4]) < 0.5) return null;
    return (0.2126 * +m[1] + 0.7152 * +m[2] + 0.0722 * +m[3]) / 255;
  }

  function _fondDe(el) {
    var st = getComputedStyle(el);
    var l = _lum(st.backgroundColor);
    if (l !== null) return l;
    /* UN DÉGRADÉ N'EST PAS UNE `backgroundColor`. Le site public peint son
       fond violet avec `linear-gradient(…)` : la couleur calculée reste
       transparente, et un relevé qui s'arrête là conclut « clair » sur une
       page sombre. La première teinte du dégradé suffit à trancher. */
    var img = st.backgroundImage || "";
    var m = img.match(/rgba?\([^)]*\)|#[0-9a-f]{6}\b/i);
    if (!m) return null;
    var c = m[0];
    if (c.charAt(0) === "#")
      c = "rgb(" + parseInt(c.substr(1, 2), 16) + "," + parseInt(c.substr(3, 2), 16)
          + "," + parseInt(c.substr(5, 2), 16) + ")";
    return _lum(c);
  }

  function fondSombre() {
    try {
      /* CE QUI EST RÉELLEMENT PEINT DERRIÈRE LE BOUTON, et non ce que `body`
         déclare. Trois pages du site — la foire aux questions, le livre blanc,
         la carte — ne peignent leur fond ni sur `body` ni sur `html` : il vient
         d'un conteneur intermédiaire. Interroger `body` seul y répondait
         « transparent », et un panneau clair se posait sur une page sombre.
         On part donc du point où la barre s'installe et on remonte la pile
         jusqu'au premier fond opaque. */
      var l = null;
      var el = document.elementFromPoint(Math.floor(innerWidth / 2), 8);
      while (el && l === null) { l = _fondDe(el); el = el.parentElement; }
      if (l === null) l = _fondDe(document.body);
      if (l === null) l = _fondDe(document.documentElement);
      if (l !== null) return l < 0.5;
      /* Dernier recours : un texte clair suppose une page sombre. */
      var t = _lum(getComputedStyle(document.body).color);
      return t === null ? true : t > 0.5;
    } catch (e) { return true; }
  }

  function poserStyle(sombre) {
    if (document.getElementById("cp-guide-style")) return;
    var enc = sombre ? "rgba(255,255,255,.06)" : "#FFFFFF";
    var trait = sombre ? "rgba(180,138,247,.30)" : "#E3E1DC";
    var texte = sombre ? "#f8f4ff" : "#1C1C1C";
    var doux = sombre ? "rgba(212,186,255,.72)" : "#5A5A5A";
    var vif = sombre ? "#b48af7" : "#B83222";
    var voile = sombre ? "rgba(6,3,18,.72)" : "rgba(28,28,28,.42)";
    var st = document.createElement("style");
    st.id = "cp-guide-style";
    st.textContent = [
      ".cp-guide-bar{display:flex;justify-content:flex-end;max-width:1180px;margin:0 auto;padding:10px 20px 0;position:relative;z-index:40}",
      /* `max-width` et `margin:auto` de la barre en flux la recentraient une
         fois flottante, et le bouton sortait de l'écran par la droite : la
         règle doit défaire CHACUNE des propriétés du flux, pas seulement la
         position. */
      ".cp-guide-bar.flottante{position:fixed;top:12px;right:12px;left:auto;width:auto;max-width:none;padding:0;margin:0;z-index:1200}",
      ".cp-guide-btn{display:inline-flex;align-items:center;gap:7px;padding:7px 15px;border-radius:999px;cursor:pointer;",
      "  font:600 12px/1 ui-sans-serif,system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;letter-spacing:.02em;",
      "  color:" + texte + ";background:" + enc + ";border:1px solid " + trait + ";transition:border-color .18s,background .18s}",
      ".cp-guide-btn:hover,.cp-guide-btn:focus-visible{border-color:" + vif + ";background:" + (sombre ? "rgba(180,138,247,.14)" : "rgba(184,50,34,.08)") + "}",
      ".cp-guide-btn .pastille{display:inline-flex;align-items:center;justify-content:center;width:16px;height:16px;",
      "  border-radius:50%;background:" + vif + ";color:" + (sombre ? "#160a2e" : "#fff") + ";font-size:10px;font-weight:800}",
      ".cp-guide-voile{position:fixed;inset:0;background:" + voile + ";display:none;align-items:center;justify-content:center;padding:24px;z-index:2000}",
      ".cp-guide-voile.ouvert{display:flex}",
      ".cp-guide-panneau{position:relative;max-width:640px;width:100%;max-height:82vh;overflow:auto;border-radius:16px;padding:26px 28px 22px;",
      "  background:" + (sombre ? "#140a2f" : "#FFFFFF") + ";border:1px solid " + trait + ";color:" + texte + ";",
      "  font:400 14px/1.6 ui-sans-serif,system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;box-shadow:0 24px 60px rgba(0,0,0,.35)}",
      ".cp-guide-panneau .sur{font:700 10px/1 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.16em;text-transform:uppercase;color:" + vif + ";margin-bottom:9px}",
      ".cp-guide-panneau h2{font-size:20px;line-height:1.25;margin:0 0 10px;font-weight:700;color:" + texte + "}",
      ".cp-guide-panneau p{margin:0 0 16px;color:" + doux + "}",
      ".cp-guide-panneau h3{font-size:11px;letter-spacing:.12em;text-transform:uppercase;margin:18px 0 8px;color:" + vif + ";font-weight:700}",
      ".cp-guide-panneau ol,.cp-guide-panneau ul{margin:0;padding-left:20px}",
      ".cp-guide-panneau li{margin-bottom:7px;color:" + doux + "}",
      ".cp-guide-panneau li b{color:" + texte + "}",
      ".cp-guide-liens{display:flex;flex-wrap:wrap;gap:9px;margin-top:4px}",
      ".cp-guide-liens a{display:inline-block;padding:6px 13px;border-radius:999px;text-decoration:none;font-size:12px;font-weight:600;",
      "  color:" + texte + ";border:1px solid " + trait + "}",
      ".cp-guide-liens a:hover{border-color:" + vif + "}",
      ".cp-guide-fermer{position:absolute;top:14px;right:14px;width:30px;height:30px;border-radius:50%;cursor:pointer;",
      "  background:transparent;border:1px solid " + trait + ";color:" + texte + ";font-size:15px;line-height:1}",
      ".cp-guide-pied{margin:18px 0 0;font-size:12px;color:" + doux + "}",
      ".cp-guide-pied a{color:" + vif + "}",
      "@media (prefers-reduced-motion:reduce){.cp-guide-btn{transition:none}}",
      "@media (max-width:640px){.cp-guide-bar{padding:8px 14px 0}.cp-guide-panneau{padding:22px 18px 18px}}"
    ].join("\n");
    document.head.appendChild(st);
  }

  /* ── L'ANCRAGE EST UNE PROPRIÉTÉ ────────────────────────────────────────
     Trois replis successifs, du plus précis au plus général. La page sans
     titre ni navigation garde son bouton, en flottant. */
  function poserBarre(btn) {
    var bar = document.createElement("div");
    bar.className = "cp-guide-bar";
    bar.appendChild(btn);

    var entete = document.querySelector("body > header, body > nav");
    if (entete && entete.parentNode) {
      entete.parentNode.insertBefore(bar, entete.nextSibling);
      return bar;
    }
    var h1 = document.querySelector("h1");
    if (h1) {
      var bloc = h1;
      while (bloc.parentNode && bloc.parentNode !== document.body) bloc = bloc.parentNode;
      bloc.parentNode.insertBefore(bar, bloc);
      return bar;
    }
    /* FLOTTANT, MAIS PAS PAR-DESSUS CE QUI EST DÉJÀ LÀ. Le coin haut-droit est
       le premier endroit où une page pose son compteur, son badge ou son
       bouton de plein écran — la carte y met le sien. On regarde donc qui
       occupe ce coin, AVANT d'y poser quoi que ce soit, et l'on descend sous
       lui plutôt que de le recouvrir. Sonder après l'insertion ne trouverait
       que la barre elle-même : c'est l'erreur qu'un premier essai a faite, et
       elle ne se voit pas — le bouton s'affiche, simplement il en cache un
       autre. */
    var dessous = 0;
    try {
      var occupant = document.elementFromPoint(innerWidth - 24, 24);
      if (occupant && occupant !== document.body && occupant !== document.documentElement) {
        var r = occupant.getBoundingClientRect();
        if (r.height > 0 && r.height < 160 && r.right > innerWidth - 220)
          dessous = Math.round(r.bottom + 10);
      }
    } catch (e) { /* la page reste utilisable si le relevé échoue */ }
    bar.classList.add("flottante");
    if (dessous) bar.style.top = dessous + "px";
    document.body.insertBefore(bar, document.body.firstChild);
    return bar;
  }

  function echapper(s) {
    return ("" + (s == null ? "" : s)).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function init() {
    if (document.querySelector(".cp-guide-btn")) return;
    /* Sentinel a son propre mécanisme de guides, panneau par panneau : y
       poser celui-ci mettrait deux boutons d'aide côte à côte, dont l'un
       ignorerait le panneau ouvert. */
    if (document.getElementById("page-guide-btn") || window.PAGE_GUIDES) return;

    var guide = guidePour(location.pathname) || GUIDE_DEFAULT;
    var sombre = fondSombre();
    poserStyle(sombre);

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "cp-guide-btn";
    btn.setAttribute("aria-haspopup", "dialog");
    btn.setAttribute("aria-label", "Ouvrir le guide de cette page");
    btn.title = "Ouvrir le guide de cette page";
    btn.innerHTML = '<span class="pastille" aria-hidden="true">?</span><span>Guide de la page</span>';
    poserBarre(btn);

    var voile = document.createElement("div");
    voile.className = "cp-guide-voile";
    var html = '<div class="cp-guide-panneau" role="dialog" aria-modal="true" aria-label="Guide de la page">'
      + '<button type="button" class="cp-guide-fermer" aria-label="Fermer le guide">✕</button>'
      + '<div class="sur">Guide de la page</div>'
      + "<h2>" + echapper(guide.t) + "</h2>"
      + "<p>" + echapper(guide.p) + "</p>";
    if (guide.s && guide.s.length) {
      html += "<h3>Comment l’utiliser</h3><ol>";
      guide.s.forEach(function (x) { html += "<li>" + echapper(x) + "</li>"; });
      html += "</ol>";
    }
    if (guide.k && guide.k.length) {
      html += "<h3>À savoir</h3><ul>";
      guide.k.forEach(function (x) { html += "<li><b>" + echapper(x[0]) + "</b> — " + echapper(x[1]) + "</li>"; });
      html += "</ul>";
    }
    if (guide.l && guide.l.length) {
      html += '<h3>Aller plus loin</h3><div class="cp-guide-liens">';
      guide.l.forEach(function (x) { html += '<a href="' + echapper(x[1]) + '">' + echapper(x[0]) + "</a>"; });
      html += "</div>";
    }
    html += '<p class="cp-guide-pied">Besoin d’aide humaine ? <a href="/support">Écrivez-nous</a> — réponse sous 24 heures ouvrées.</p></div>';
    voile.innerHTML = html;
    document.body.appendChild(voile);

    var fermer = voile.querySelector(".cp-guide-fermer");
    function basculer(ouvert) {
      voile.classList.toggle("ouvert", ouvert);
      (ouvert ? fermer : btn).focus();
    }
    btn.addEventListener("click", function () { basculer(true); });
    fermer.addEventListener("click", function () { basculer(false); });
    voile.addEventListener("click", function (e) { if (e.target === voile) basculer(false); });
    document.addEventListener("keydown", function (e) {
      if ((e.key === "Escape" || e.key === "Esc") && voile.classList.contains("ouvert")) basculer(false);
    });
  }

  window.cpGuidePour = guidePour;      /* exposé pour la recette */
  window.cpGuideDefaut = GUIDE_DEFAULT;

  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", init);
  else init();
})();
