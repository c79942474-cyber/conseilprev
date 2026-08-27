/* ══════════════════════════════════════════════════════════════════════════
   GUIDE DE PAGE — le bouton d'aide de CONSEILPREV INFO

   POURQUOI. Les deux autres sites du cabinet ont leurs guides : soixante-dix-
   huit panneaux sur Sentinel, cinquante-six pages sur conseilprevcyber,
   vingt-huit sur le site public. Celui-ci n'en avait aucun, alors que c'est
   celui dont les conventions sont les moins devinables : une fiche y distingue
   le FAIT de la LECTURE CRITIQUE, une lecture dérivée par règles d'une lecture
   signée, et la portée d'une incertitude. Rien de tout cela ne se déduit de la
   mise en page.

   CE QUE LE GUIDE DIT, ET DANS QUEL ORDRE. À quoi sert la page, comment s'en
   servir, puis ce qu'elle NE fait pas. La troisième partie est celle qui
   manque partout, et c'est elle qui évite de chercher dans une page ce qui
   n'y est pas.

   POURQUOI DEUX LANGUES ÉCRITES, ET NON UNE TRADUITE. Ce site refuse la
   traduction automatique à son corpus ; s'en servir pour sa propre aide serait
   exactement l'hypocrisie que `langue.js` nomme en tête. Les deux versions
   sont donc écrites, et le guide suit la bascule de l'interface — pas celle
   des analyses, qui est un réglage distinct.

   L'ANCRAGE EST UNE PROPRIÉTÉ, PAS UNE CLASSE. Sur conseilprevcyber le bouton
   s'ancrait sur `h1.page-h` ; vingt-cinq pages titraient autrement et leur
   guide, pourtant écrit, restait inatteignable sans qu'aucune erreur ne le
   signale. Ici la barre se pose avant le bloc qui porte le premier titre —
   quel que soit son nom — et, à défaut, flotte.
   ══════════════════════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  /* ── LES GUIDES, DANS LES DEUX LANGUES ─────────────────────────────────
     `t` le titre, `p` le chapeau, `s` les étapes, `k` les notions, `l` les
     liens. Les liens ne sont pas traduits pour leur adresse, seulement pour
     leur libellé. */
  var GUIDES = {};

  GUIDES["/"] = {
    fr: {
      t: "Le fil de la veille",
      p: "Le corpus entier, filtrable : les dossiers qu'il forme de lui-même, ce qui rompt avec ce qui précède, les pistes d'instruction qu'il ouvre, et le registre de ce que ce site a le droit de lire.",
      s: ["Commencez par « Dossiers » : ce sont des regroupements calculés sur le corpus, pas des rubriques décidées à l'avance.",
        "« À la une » ne veut pas dire « important » mais « en rupture » avec ce qui précédait sur le même sujet.",
        "Le registre des sources dit ce qui est lu ET ce qui ne l'est pas encore, avec la raison. Une source absente y est nommée, jamais passée sous silence."],
      k: [["Un article n'est pas un fait", "Le corpus enregistre des publications. Ce qu'elles affirment reste attribué à leur source, y compris quand plusieurs se recopient."],
        ["Ce que ce site ne lit pas encore", "La dernière section de la page. Un périmètre qui ne dit pas ses trous se lit comme une couverture complète."]],
      l: [["La revue", "/revue"], ["Confronter un document", "/confronter"]]
    },
    en: {
      t: "The intelligence feed",
      p: "The whole corpus, filterable: the dossiers it forms on its own, what breaks with what came before, the lines of enquiry it opens, and the register of what this site is allowed to read.",
      s: ["Start with “Dossiers”: these are groupings computed over the corpus, not sections decided in advance.",
        "“Front page” does not mean “important” but “a break” with what preceded it on the same subject.",
        "The source register states what is read AND what is not yet, with the reason. A missing source is named there, never passed over in silence."],
      k: [["An article is not a fact", "The corpus records publications. What they assert stays attributed to their source, including when several copy one another."],
        ["What this site does not read yet", "The last section of the page. A perimeter that does not state its gaps reads as complete coverage."]],
      l: [["The review", "/revue"], ["Compare a document", "/confronter"]]
    }
  };

  GUIDES["/revue"] = {
    fr: {
      t: "La revue",
      p: "Deux découpes du même corpus : la semaine, et le mois vu hors de France. Rien n'y est réécrit pour l'occasion — chaque entrée renvoie à sa fiche, avec sa source et son statut.",
      s: ["Choisissez la découpe avant de lire : la semaine et le mois ne répondent pas à la même question.",
        "Suivez le lien d'une entrée vers sa fiche dès qu'un point vous arrête : c'est là que se trouvent la source et la portée.",
        "« Reportages et entretiens » est une section à part : ce qui ne se dérive pas de règles y est signalé comme tel."],
      k: [["Rien n'est réécrit", "La revue assemble ; elle ne rédige pas. Une formule que vous lisez ici se retrouve mot pour mot sur la fiche."],
        ["Le mois vu hors de France", "La même période, lue dans des sources étrangères. L'écart entre les deux découpes est une information à part entière."]],
      l: [["Le fil complet", "/"], ["Votre abonnement", "/abonnement"]]
    },
    en: {
      t: "The review",
      p: "Two cuts of the same corpus: the week, and the month as seen from outside France. Nothing is rewritten for the occasion — each entry links to its record, with its source and status.",
      s: ["Choose the cut before reading: the week and the month do not answer the same question.",
        "Follow an entry's link to its record as soon as a point stops you: that is where the source and the scope are.",
        "“Reports and interviews” is a section apart: what cannot be derived from rules is flagged as such."],
      k: [["Nothing is rewritten", "The review assembles; it does not compose. A phrase you read here appears word for word on the record."],
        ["The month seen from outside France", "The same period, read in foreign sources. The gap between the two cuts is itself information."]],
      l: [["The full feed", "/"], ["Your subscription", "/abonnement"]]
    }
  };

  GUIDES["/confronter"] = {
    fr: {
      t: "Confronter un document",
      p: "Déposez un document — politique de sécurité, cahier des charges, note d'architecture — et voyez quelles fiches du corpus traitent de ce dont il parle. C'est une entrée dans la veille par votre propre vocabulaire.",
      s: ["Déposez le document : il est analysé pour ses TERMES, et la comparaison part de là.",
        "Lisez « Ce que votre document touche » pour les recoupements, puis « Ce qu'il ne nomme pas » — c'est la seconde qui apprend quelque chose.",
        "Un compte est requis : la page le dit avant le dépôt, pas après."],
      k: [["Ce qu'il ne nomme pas", "Les sujets que le corpus rattache aux vôtres et que votre document ignore. C'est le seul résultat qui ne se devine pas à l'avance."],
        ["Ce n'est pas un audit", "L'outil rapproche des vocabulaires. Il ne juge ni la qualité, ni la conformité de ce que vous déposez."]],
      l: [["Le fil complet", "/"], ["Ce que ce site garde de vous", "/confidentialite"]]
    },
    en: {
      t: "Compare a document",
      p: "Upload a document — a security policy, a specification, an architecture note — and see which records in the corpus deal with what it talks about. It is a way into the intelligence feed through your own vocabulary.",
      s: ["Upload the document: it is analysed for its TERMS, and the comparison starts from there.",
        "Read “What your document touches” for the overlaps, then “What it does not name” — the second is the one that teaches you something.",
        "An account is required: the page says so before the upload, not after."],
      k: [["What it does not name", "The subjects the corpus links to yours that your document ignores. It is the only result you cannot guess in advance."],
        ["This is not an audit", "The tool brings vocabularies together. It judges neither the quality nor the compliance of what you upload."]],
      l: [["The full feed", "/"], ["What this site keeps about you", "/confidentialite"]]
    }
  };

  GUIDES["/abonnement"] = {
    fr: {
      t: "Votre abonnement",
      p: "Vous choisissez les sujets que vous suivez et le seuil à partir duquel un fait mérite de vous être signalé. Le bulletin ne contient rien qui ne soit déjà publié sur ce site.",
      s: ["Réglez d'abord les sujets, ensuite le seuil : un seuil serré sur un périmètre trop large ne filtre rien d'utile.",
        "« Votre bulletin, tel qu'il partirait » montre l'envoi réel avant tout envoi — vérifiez-le plutôt que de l'imaginer.",
        "Le classeur garde ce que vous mettez de côté ; il est à vous et s'efface d'un geste."],
      k: [["Ni analyse rédigée pour l'envoi", "Le bulletin n'écrit rien de neuf. Un fait n'y est jamais requalifié pour remplir une semaine creuse."],
        ["Le seuil", "Il porte sur la RUPTURE, pas sur le volume : un sujet très couvert mais sans rien de nouveau ne franchit pas un seuil élevé."]],
      l: [["Ce que ce site garde de vous", "/confidentialite"], ["Le fil complet", "/"]]
    },
    en: {
      t: "Your subscription",
      p: "You choose the subjects you follow and the threshold above which a fact deserves to be flagged to you. The bulletin contains nothing that is not already published on this site.",
      s: ["Set the subjects first, the threshold second: a tight threshold over too wide a perimeter filters nothing useful.",
        "“Your bulletin, as it would go out” shows the real send before any send — check it rather than imagining it.",
        "The folder keeps what you set aside; it is yours and clears in one gesture."],
      k: [["No analysis written for the send", "The bulletin composes nothing new. A fact is never requalified in it to fill a quiet week."],
        ["The threshold", "It bears on the BREAK, not the volume: a heavily covered subject with nothing new does not clear a high threshold."]],
      l: [["What this site keeps about you", "/confidentialite"], ["The full feed", "/"]]
    }
  };

  GUIDES["/confidentialite"] = {
    fr: {
      t: "Ce que ce site garde de vous",
      p: "Aucun cookie, aucune requête vers un tiers, aucune mesure d'audience. Ce n'est pas une promesse : c'est un inventaire de ce qui est écrit, où, pourquoi, combien de temps, et comment l'effacer.",
      s: ["Lisez l'inventaire de ce qui est écrit dans votre navigateur : c'est la partie qui vous concerne directement.",
        "« Ce que le serveur garde » est distinct : ce qui reste chez vous et ce qui part ne se confondent pas.",
        "Chaque droit est décrit avec le chemin pour l'exercer, pas seulement avec son nom."],
      k: [["Un inventaire, pas une promesse", "Cette page est modifiée en même temps que ce qu'elle décrit. Une politique écrite une fois puis oubliée finit par affirmer le contraire de ce que le site fait."],
        ["Pas de tiers", "Aucune requête ne quitte ce site vers un autre domaine — polices comprises. C'est pourquoi il n'y a pas de bandeau de consentement à refuser."]],
      l: [["Votre abonnement", "/abonnement"], ["Le fil complet", "/"]]
    },
    en: {
      t: "What this site keeps about you",
      p: "No cookies, no third-party requests, no audience measurement. This is not a promise: it is an inventory of what is stored, where, why, for how long, and how to erase it.",
      s: ["Read the inventory of what is written in your browser: that is the part that concerns you directly.",
        "“What the server keeps” is separate: what stays with you and what leaves must not be confused.",
        "Each right is described with the path to exercise it, not merely with its name."],
      k: [["An inventory, not a promise", "This page is changed at the same time as what it describes. A policy written once and then forgotten ends up asserting the opposite of what the site does."],
        ["No third parties", "No request leaves this site for another domain — fonts included. That is why there is no consent banner to refuse."]],
      l: [["Your subscription", "/abonnement"], ["The full feed", "/"]]
    }
  };

  GUIDES["/fiche"] = {
    fr: {
      t: "Une fiche du corpus",
      p: "Un fait publié, sa source, et ce que le site en dit — en gardant les deux séparés. La lecture critique porte sa provenance : dérivée par règles, ou rédigée et signée.",
      s: ["Lisez le fait et sa source avant la lecture critique : l'ordre n'est pas décoratif.",
        "Regardez la mention de provenance de l'analyse. « Dérivée par règles » veut dire reproductible et sans modèle de langage ; « signée » veut dire qu'une personne l'assume.",
        "La portée et l'incertitude sont affichées avec le fait. Un fait sans portée déclarée s'applique à tout, ce qui revient à ne s'appliquer à rien."],
      k: [["La lecture critique n'est pas le fait", "Les deux vivent sur la même page et ne se mélangent jamais. C'est la convention principale de ce site."],
        ["Les analyses ne sont pas traduites d'office", "Elles sont dérivées de gabarits écrits dans une langue. La bascule des analyses est un réglage distinct de celui de l'interface, et elle le dit à l'écran."]],
      l: [["Le fil complet", "/"], ["La revue", "/revue"]]
    },
    en: {
      t: "A record from the corpus",
      p: "A published fact, its source, and what the site says about it — keeping the two apart. The critical reading carries its provenance: derived by rules, or written and signed.",
      s: ["Read the fact and its source before the critical reading: the order is not decorative.",
        "Look at the provenance of the analysis. “Derived by rules” means reproducible and without a language model; “signed” means a person stands behind it.",
        "Scope and uncertainty are shown with the fact. A fact with no declared scope applies to everything, which amounts to applying to nothing."],
      k: [["The critical reading is not the fact", "Both live on the same page and never blend. It is this site's main convention."],
        ["Analyses are not translated by default", "They are derived from templates written in one language. Switching the language of analyses is a setting distinct from the interface, and it says so on screen."]],
      l: [["The full feed", "/"], ["The review", "/revue"]]
    }
  };

  var DEFAUT = {
    fr: {
      t: "Aide",
      p: "Cette page fait partie de CONSEILPREV INFO — une veille sourcée sur la cybersécurité industrielle, l'intelligence artificielle et les centres de données.",
      s: ["Le fil rassemble tout le corpus, filtrable par sujet et par portée.",
        "Chaque fait renvoie à sa fiche, où la source et la lecture critique restent séparées."],
      k: [], l: [["Le fil complet", "/"], ["La revue", "/revue"]]
    },
    en: {
      t: "Help",
      p: "This page is part of CONSEILPREV INFO — sourced intelligence on industrial cybersecurity, artificial intelligence and data centres.",
      s: ["The feed gathers the whole corpus, filterable by subject and scope.",
        "Every fact links to its record, where the source and the critical reading stay apart."],
      k: [], l: [["The full feed", "/"], ["The review", "/revue"]]
    }
  };

  /* Les fiches ont une adresse par identifiant : `/fiche/2026-08-…`. Écrire un
     guide par fiche les condamnerait à diverger dès la première correction —
     elles ont la même structure, seul le fait change. */
  function guidePour(chemin) {
    var p = String(chemin || "/").replace(/\/+$/, "") || "/";
    if (GUIDES[p]) return GUIDES[p];
    if (p.indexOf("/fiche/") === 0 || p === "/fiche") return GUIDES["/fiche"];
    return null;
  }

  function langue() {
    try {
      if (window.L && typeof window.L.courante === "function") return window.L.courante();
    } catch (e) { /* la langue par défaut s'applique */ }
    return "fr";
  }

  function contenu() {
    var g = guidePour(location.pathname) || DEFAUT;
    return g[langue()] || g.fr;
  }

  function echapper(s) {
    return ("" + (s == null ? "" : s)).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  var LIBELLES = {
    bouton:  ["Guide de la page", "Page guide"],
    ouvrir:  ["Ouvrir le guide de cette page", "Open this page's guide"],
    fermer:  ["Fermer le guide", "Close the guide"],
    sur:     ["Guide de la page", "Page guide"],
    usage:   ["Comment l’utiliser", "How to use it"],
    savoir:  ["À savoir", "Worth knowing"],
    plus:    ["Aller plus loin", "Going further"]
  };

  function lib(cle) {
    return LIBELLES[cle][langue() === "en" ? 1 : 0];
  }

  function poserStyle() {
    if (document.getElementById("cpi-guide-style")) return;
    var st = document.createElement("style");
    st.id = "cpi-guide-style";
    /* Les couleurs viennent des variables du site quand elles existent, avec
       un repli littéral : une feuille chargée plus tard ne doit pas laisser le
       panneau sans fond. */
    st.textContent = [
      ".cpi-guide-bar{display:flex;justify-content:flex-end;max-width:1180px;margin:0 auto;padding:10px 22px 0;position:relative;z-index:40}",
      ".cpi-guide-bar.flottante{position:fixed;top:12px;right:12px;left:auto;width:auto;max-width:none;padding:0;margin:0;z-index:1200}",
      ".cpi-guide-btn{display:inline-flex;align-items:center;gap:7px;padding:6px 14px;border-radius:999px;cursor:pointer;",
      "  font:600 12px/1 var(--sans, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif);",
      "  color:var(--encre, #0E1319);background:var(--papier, #FCFCFD);border:1px solid var(--filet, #E3E7ED)}",
      ".cpi-guide-btn:hover,.cpi-guide-btn:focus-visible{border-color:var(--rouge, #A81509)}",
      ".cpi-guide-btn .pastille{display:inline-flex;align-items:center;justify-content:center;width:16px;height:16px;",
      "  border-radius:50%;background:var(--rouge, #A81509);color:#fff;font-size:10px;font-weight:800}",
      ".cpi-guide-voile{position:fixed;inset:0;background:rgba(28,28,28,.44);display:none;align-items:center;justify-content:center;padding:24px;z-index:2000}",
      ".cpi-guide-voile.ouvert{display:flex}",
      ".cpi-guide-panneau{position:relative;max-width:640px;width:100%;max-height:82vh;overflow:auto;border-radius:14px;padding:26px 28px 22px;",
      "  background:var(--papier, #FCFCFD);border:1px solid var(--filet, #E3E7ED);color:var(--encre, #0E1319);",
      "  font:400 14px/1.62 var(--sans, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif);",
      "  box-shadow:0 24px 60px rgba(0,0,0,.28)}",
      ".cpi-guide-panneau .sur{font:700 10px/1 var(--gothique, ui-monospace, SFMono-Regular, Menlo, monospace);letter-spacing:.16em;",
      "  text-transform:uppercase;color:var(--rouge, #A81509);margin-bottom:9px}",
      ".cpi-guide-panneau h2{font-size:20px;line-height:1.25;margin:0 0 10px;font-weight:700}",
      ".cpi-guide-panneau p{margin:0 0 16px;color:var(--encre2, #333C47)}",
      ".cpi-guide-panneau h3{font-size:11px;letter-spacing:.12em;text-transform:uppercase;margin:18px 0 8px;color:var(--rouge, #A81509);font-weight:700}",
      ".cpi-guide-panneau ol,.cpi-guide-panneau ul{margin:0;padding-left:20px}",
      ".cpi-guide-panneau li{margin-bottom:7px;color:var(--encre2, #333C47)}",
      ".cpi-guide-panneau li b{color:var(--encre, #0E1319)}",
      ".cpi-guide-liens{display:flex;flex-wrap:wrap;gap:9px}",
      ".cpi-guide-liens a{display:inline-block;padding:6px 13px;border-radius:999px;text-decoration:none;font-size:12px;font-weight:600;",
      "  color:var(--encre, #0E1319);border:1px solid var(--filet, #E3E7ED)}",
      ".cpi-guide-liens a:hover{border-color:var(--rouge, #A81509)}",
      ".cpi-guide-fermer{position:absolute;top:14px;right:14px;width:30px;height:30px;border-radius:50%;cursor:pointer;",
      "  background:transparent;border:1px solid var(--filet, #E3E7ED);color:var(--encre, #0E1319);font-size:15px;line-height:1}",
      "@media (max-width:640px){.cpi-guide-bar{padding:8px 14px 0}.cpi-guide-panneau{padding:22px 18px 18px}}"
    ].join("\n");
    document.head.appendChild(st);
  }

  function poserBarre(btn) {
    var bar = document.createElement("div");
    bar.className = "cpi-guide-bar";
    bar.appendChild(btn);

    var h1 = document.querySelector("h1");
    if (h1) {
      var bloc = h1;
      while (bloc.parentNode && bloc.parentNode !== document.body) bloc = bloc.parentNode;
      if (bloc.parentNode === document.body) {
        bloc.parentNode.insertBefore(bar, bloc);
        return bar;
      }
    }
    bar.classList.add("flottante");
    document.body.insertBefore(bar, document.body.firstChild);
    return bar;
  }

  function corpsDuPanneau() {
    var g = contenu();
    var html = '<button type="button" class="cpi-guide-fermer" aria-label="' + echapper(lib("fermer")) + '">✕</button>'
      + '<div class="sur">' + echapper(lib("sur")) + "</div>"
      + "<h2>" + echapper(g.t) + "</h2><p>" + echapper(g.p) + "</p>";
    if (g.s && g.s.length) {
      html += "<h3>" + echapper(lib("usage")) + "</h3><ol>";
      g.s.forEach(function (x) { html += "<li>" + echapper(x) + "</li>"; });
      html += "</ol>";
    }
    if (g.k && g.k.length) {
      html += "<h3>" + echapper(lib("savoir")) + "</h3><ul>";
      g.k.forEach(function (x) { html += "<li><b>" + echapper(x[0]) + "</b> — " + echapper(x[1]) + "</li>"; });
      html += "</ul>";
    }
    if (g.l && g.l.length) {
      html += "<h3>" + echapper(lib("plus")) + '</h3><div class="cpi-guide-liens">';
      g.l.forEach(function (x) { html += '<a href="' + echapper(x[1]) + '">' + echapper(x[0]) + "</a>"; });
      html += "</div>";
    }
    return html;
  }

  function demarrer() {
    if (document.querySelector(".cpi-guide-btn")) return;
    poserStyle();

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "cpi-guide-btn";
    btn.setAttribute("aria-haspopup", "dialog");
    poserBarre(btn);

    var voile = document.createElement("div");
    voile.className = "cpi-guide-voile";
    var panneau = document.createElement("div");
    panneau.className = "cpi-guide-panneau";
    panneau.setAttribute("role", "dialog");
    panneau.setAttribute("aria-modal", "true");
    voile.appendChild(panneau);
    document.body.appendChild(voile);

    function basculer(ouvert) {
      voile.classList.toggle("ouvert", ouvert);
      if (ouvert) {
        var f = panneau.querySelector(".cpi-guide-fermer");
        if (f) f.focus();
      } else btn.focus();
    }

    /* LA BASCULE DE LANGUE RÉÉCRIT TOUT CE QUI EST AFFICHÉ. Le panneau est
       rendu en JavaScript : les attributs `data-i18n` du site ne l'atteignent
       pas, et un guide resté français sous une interface anglaise est
       exactement le reste qui fait douter du reste. */
    function redessiner() {
      btn.innerHTML = '<span class="pastille" aria-hidden="true">?</span><span>'
        + echapper(lib("bouton")) + "</span>";
      btn.title = lib("ouvrir");
      btn.setAttribute("aria-label", lib("ouvrir"));
      panneau.setAttribute("aria-label", lib("sur"));
      panneau.innerHTML = corpsDuPanneau();
      panneau.querySelector(".cpi-guide-fermer")
        .addEventListener("click", function () { basculer(false); });
    }

    redessiner();
    document.addEventListener("langue", redessiner);
    btn.addEventListener("click", function () { basculer(true); });
    voile.addEventListener("click", function (e) { if (e.target === voile) basculer(false); });
    document.addEventListener("keydown", function (e) {
      if ((e.key === "Escape" || e.key === "Esc") && voile.classList.contains("ouvert")) basculer(false);
    });
  }

  window.cpiGuidePour = guidePour;     /* exposés pour la recette */
  window.cpiGuideDefaut = DEFAUT;

  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", demarrer);
  else demarrer();
})();
