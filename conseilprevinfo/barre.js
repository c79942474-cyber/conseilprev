/* LA BARRE LATÉRALE — et pourquoi elle ne peut pas mentir.
   ────────────────────────────────────────────────────────
   LES SECTIONS NE SONT PAS ÉCRITES ICI, ELLES SONT LUES DANS LA PAGE. Une
   liste tenue à la main dans ce fichier promettrait « Pistes d'instruction »
   le jour où la rubrique serait retirée, et le lecteur cliquerait dans le
   vide. Toute `h2.rubrique` portant un identifiant devient une entrée ; aucune
   autre n'en devient une. La barre ne peut donc pas diverger de la page — de
   la même façon que le registre des sources dérive de la table qui collecte.

   LES COMPTES VIENNENT DES MÊMES ÉLÉMENTS QUE LES TITRES. Chaque rubrique
   porte déjà son compteur (`<span id="c-fil">98</span>`) que le moteur
   remplit ; la barre le recopie et le suit. Un second calcul, même juste,
   finirait par afficher un autre nombre que celui d'à côté.

   LA LÉGENDE VIENT DU SERVEUR, ET PORTE LES CLASSES DES FICHES. Les couleurs
   du site sont un code — rouge la rupture, bleu le sujet, vert la source
   vérifiée, ambre la réserve — et ce code n'était écrit nulle part : un
   lecteur voyait une pastille rouge sans savoir ce qu'elle affirmait. La
   légende le dit, avec les MÊMES noms que le référentiel et les MÊMES classes
   CSS que les cartes. Recopier les intitulés ici les aurait fait diverger au
   premier ajout de portée ; peindre les témoins à la main les aurait fait
   diverger à la première retouche de feuille de style.

   ELLE SE REPLIE À TOUTE LARGEUR, ET S'EN SOUVIENT. Elle se repliait déjà
   sous 1100 px, où une colonne de 236 px sur un écran de 390 prend la moitié
   de la largeur pour de la navigation. Au-dessus, elle ne se repliait pas du
   tout : un lecteur qui veut la pleine largeur pour un tableau de sources
   n'avait aucun moyen de l'obtenir. Le choix est retenu dans le navigateur —
   et c'est le seul état que ce fichier écrit quelque part. */
(function () {
  "use strict";

  var CLE_ETAT = "cpinfo.barre";

  function $(i) { return document.getElementById(i); }
  function esc(x) {
    return String(x == null ? "" : x).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function t(c) { return (window.L && window.L.t) ? window.L.t(c) : c; }
  function langue() {
    return (window.L && window.L.courante) ? window.L.courante() : "fr";
  }

  /* ── LES SILHOUETTES ─────────────────────────────────────────────────────
     UNE ICÔNE N'EST JAMAIS SEULE À PORTER L'INFORMATION : chaque entrée garde
     son intitulé écrit à côté, et les silhouettes sont distinctes entre elles
     — pas la même forme en quatre teintes. C'est la règle WCAG 1.4.1 prise au
     sérieux : un lecteur qui ne distingue pas les couleurs, ou qui a coupé les
     images, perd une commodité et rien d'autre.

     UNE ICÔNE ABSENTE NE CASSE RIEN — l'entrée s'affiche sans. Mais elle ne
     doit pas manquer par oubli : `test_presentation` exige une silhouette pour
     chaque `h2.rubrique[id]` des pages servies, de sorte qu'une rubrique
     ajoutée sans son icône fasse tomber un contrôle plutôt que de passer. */
  var ICONES = {
    /* Les pages du site */
    "/": '<path d="M4 5.5h16v13H4z"/><path d="M4 9h16"/><path d="M8 12.5h8"/><path d="M8 15.5h5"/>',
    "/confronter": '<path d="M12 4v16"/><path d="M6.5 7.5 3.5 14h6z"/><path d="M17.5 7.5 14.5 14h6z"/><path d="M6 5.5h12"/>',
    "/abonnement": '<path d="M12 3.5a5 5 0 0 0-5 5c0 5-2 6.5-2 6.5h14s-2-1.5-2-6.5a5 5 0 0 0-5-5z"/><path d="M10.4 18a1.9 1.9 0 0 0 3.2 0"/>',
    /* LES QUATRE GROUPES DU MENU. Les icônes de rubrique, plus haut dans la
       colonne, portent la teinte de leur groupe à pleine intensité ; celles
       des entrées la reprennent en retrait. Deux niveaux également voyants et
       l'on ne sait plus lequel structure l'autre — c'est la leçon du tiroir de
       conseilprevcyber, et elle vaut ici. */
    "g-corpus": '<path d="M4 6.5h16v13H4z"/><path d="M8 10h8"/><path d="M8 13h8"/><path d="M8 16h5"/>',
    "g-site": '<path d="m3 10.5 9-7 9 7"/><path d="M5.5 9v11.5h13V9"/><path d="M10 20.5v-6h4v6"/>',
    "g-sections": '<path d="M4 5.5h16"/><path d="M7 10h13"/><path d="M7 14.5h13"/><path d="M7 19h9"/><path d="M4.2 10h.01"/><path d="M4.2 14.5h.01"/><path d="M4.2 19h.01"/>',
    "g-legende": '<circle cx="7.5" cy="8" r="3"/><circle cx="7.5" cy="16.5" r="3"/><path d="M13.5 8h7"/><path d="M13.5 16.5h7"/>',
    /* Les rubriques de l'accueil — mêmes identifiants que dans index.html */
    "r-dossiers": '<path d="M3.5 6.5h6l1.6 2.2h9.4v9.8H3.5z"/><path d="M3.5 11h17"/>',
    "r-une": '<path d="M13 3 4.5 13.6h6L10 21l8.5-10.6h-6z"/>',
    "r-fil": '<path d="M4 6.5h16"/><path d="M4 12h16"/><path d="M4 17.5h10"/>',
    "r-pistes": '<path d="M6 20.5V9"/><path d="M6 9c4-3 8 3 12 0V4c-4 3-8-3-12 0z"/>',
    "r-sources": '<path d="M5 4.5h9l5 5v10H5z"/><path d="M14 4.5v5h5"/><path d="M8.5 13h7"/><path d="M8.5 16h4.5"/>',
    /* Les rubriques de la fiche — posées par `fiche.js` */
    "r-croisement": '<circle cx="8.5" cy="8.5" r="4.8"/><circle cx="15.5" cy="15.5" r="4.8"/><path d="m11.6 11.6 1 1"/>',
    "r-voisinage": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.2V12l3.2 2"/>',
    /* Les rubriques des pages secondaires */
    "r-compte": '<circle cx="12" cy="8.5" r="3.6"/><path d="M4.8 20.2a7.2 7.2 0 0 1 14.4 0"/>',
    "r-suivi": '<path d="M12 3.5a5 5 0 0 0-5 5c0 5-2 6.5-2 6.5h14s-2-1.5-2-6.5a5 5 0 0 0-5-5z"/><path d="M10.4 18a1.9 1.9 0 0 0 3.2 0"/>',
    "r-classeur": '<rect x="3.5" y="6" width="17" height="13" rx="1.6"/><path d="M9 6V4.6A1.1 1.1 0 0 1 10.1 3.5h3.8A1.1 1.1 0 0 1 15 4.6V6"/><path d="M3.5 11.5h17"/>',
    "r-bulletin": '<rect x="2.8" y="5.5" width="18.4" height="13" rx="1.6"/><path d="m3.6 6.6 8.4 6.2 8.4-6.2"/>',
    "r-touche": '<path d="M4 12h4.6l2.2-5.4 2.6 11 2.2-5.6H20"/>',
    "r-nomme": '<circle cx="12" cy="12" r="8.5"/><path d="m7.2 7.2 9.6 9.6"/>'
  };

  function icone(cle, classe) {
    var d = ICONES[cle];
    if (!d) return "";
    return '<svg class="' + classe + '" viewBox="0 0 24 24" width="15" height="15"'
      + ' fill="none" stroke="currentColor" stroke-width="1.6"'
      + ' stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"'
      + ' focusable="false">' + d + "</svg>";
  }

  /* Les pages du site. Elles sont peu nombreuses et stables ; les découvrir
     demanderait un index que ce site n'a pas, et l'inventer serait pire. */
  var PAGES = [
    { href: "/", cle: "bl.fil", dit: "bl.fil.dit" },
    { href: "/confronter", cle: "bl.conf", dit: "bl.conf.dit" },
    { href: "/abonnement", cle: "bl.abo", dit: "bl.abo.dit" }
  ];

  function ici(href) {
    var p = location.pathname;
    return href === "/" ? (p === "/" || p === "") : p.indexOf(href) === 0;
  }

  /* CE QUI EST DANS LA PAGE N'EST PAS FORCÉMENT SUR L'ÉCRAN.

     DÉFAUT CONSTATÉ AU NAVIGATEUR, sur la page d'abonnement. Elle porte deux
     panneaux exclusifs — « hors compte » et « dans le compte » — dont un seul
     est affiché à la fois, l'autre étant `hidden`. La barre lisait les
     rubriques des DEUX et en annonçait quatre quand une seule était à
     l'écran : trois entrées qui menaient à du vide.

     C'est exactement le défaut que la lecture dans la page devait rendre
     impossible — « une liste écrite ici promettrait une rubrique le jour où
     elle serait retirée, et le lecteur cliquerait dans le vide ». Lire un
     élément masqué produit le même mensonge par un autre chemin : il ne
     suffit pas qu'une rubrique EXISTE, il faut qu'elle SOIT RENDUE.

     `getClientRects()` est le bon juge — vide dès qu'aucune boîte n'est
     dessinée, quelle que soit la cause : attribut `hidden`, `display:none`,
     ancêtre replié. Une vérification du seul attribut `hidden` manquerait les
     deux autres cas, et ce site en emploie au moins un de plus. */
  function rendue(h) {
    return h.getClientRects().length > 0;
  }

  function sections() {
    return Array.prototype.slice.call(
      document.querySelectorAll("main h2.rubrique[id]")
    ).filter(rendue).map(function (h) {
      /* LE TITRE EST LE PREMIER SPAN SANS IDENTIFIANT ; LE COMPTEUR EST
         CELUI QUI EN PORTE UN.

         DÉFAUT CONSTATÉ AU NAVIGATEUR. Premier essai : retirer TOUS les spans
         et garder le reste — ce qui marchait tant que le titre était du texte
         nu. Depuis qu'il est lui-même dans un span, pour être traduisible,
         cette règle le supprimait : la barre affichait « 53 fiche(s) » sans
         jamais dire de quoi. Le compteur, lui, reste suivi à part — le
         recopier dans le libellé le figerait à la valeur du chargement. */
      var c = h.querySelector("span[id]");
      var premier = h.querySelector("span:not([id])");
      var brut = premier ? premier.textContent
        : (c ? h.textContent.replace(c.textContent, "") : h.textContent);
      /* LE TITRE DE LA BARRE S'ARRÊTE AU TIRET. Les rubriques de ce site
         s'intitulent « nom court — ce que c'est » : « Le fil — tout le corpus
         filtré ». La glose est utile en tête de section, elle ne l'est pas
         dans une colonne de 236 px, où elle repousse le compteur hors du
         cadre et fait de chaque entrée trois lignes. Le nom court suffit :
         c'est celui que le lecteur cherche.

         MAIS ELLE N'EST PAS PERDUE — elle devient l'infobulle de l'entrée.
         Couper sans rien offrir en échange, c'était retirer au lecteur la
         seule phrase qui dit ce que la rubrique contient. */
      var titre = brut.replace(/\s+/g, " ").trim();
      var i = titre.indexOf(" — ");
      return {
        id: h.id,
        titre: i > 0 ? titre.slice(0, i) : titre,
        glose: i > 0 ? titre : "",
        compteur: c ? c.id : null
      };
    });
  }

  /* ── LA LÉGENDE ──────────────────────────────────────────────────────────
     Elle n'est rendue que si la page la DEMANDE (`data-barre-legende` sur
     l'hôte). Sur la page d'abonnement, aucune pastille n'apparaît : une
     légende y expliquerait des couleurs qu'on n'y voit pas.

     LE RÉFÉRENTIEL EST LU UNE FOIS, puis gardé — la barre est reconstruite à
     chaque bascule de langue, et refaire l'appel à chaque fois taperait sur le
     serveur pour un contenu qui n'a pas changé. */
  var _ref = null, _refDemande = false, _refEchec = false;

  function referentiel(apres) {
    if (_ref || _refEchec) { apres(); return; }
    if (_refDemande) return;
    _refDemande = true;
    fetch("/api/veille/referentiel")
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d && d.ok) _ref = d; else _refEchec = true;
        apres();
      })
      .catch(function () { _refEchec = true; apres(); });
  }

  function nom(x) {
    return (langue() === "en" && x.nom_en) ? x.nom_en : x.nom;
  }

  function legende() {
    /* L'AXE QUI NE DONNE RIEN LE DIT. Sans référentiel, la barre écrit
       pourquoi la légende manque au lieu d'afficher un cadre vide — ou, pire,
       une légende écrite en dur qui survivrait à la panne en mentant. */
    if (!_ref) {
      return '<p class="bl-lg-non">' + esc(t("bl.leg.non")) + "</p>";
    }
    /* LA GLOSE EST L'INFOBULLE, PAS LE TEXTE. « Change ce qu'il est possible
       ou obligatoire de faire. Se traite en comité, pas en veille. » fait
       quatre lignes dans une colonne de 236 px ; quatre portées ainsi
       déployées font de la légende le plus long bloc de la barre. Le nom seul
       suffit à relier la pastille à son sens ; la phrase entière reste à un
       survol, et elle vient du référentiel comme le nom. */
    var h = '<ul class="bl-lg">';
    (_ref.impacts || []).forEach(function (im) {
      h += '<li title="' + esc(im.dit || "") + '"><span class="past '
        + esc(im.cle) + '">' + esc(nom(im)) + "</span></li>";
    });
    /* LES DEUX STATUTS QUI SORTENT, et eux seuls. Les trois autres
       (« à vérifier », « rédigée par IA », « réfutée ») ne sont jamais servis :
       les mettre en légende ferait croire qu'on peut les rencontrer. */
    (_ref.statuts || []).filter(function (s) { return s.publiable; })
      .forEach(function (s, i) {
        h += '<li title="' + esc(s.dit || "") + '"><span class="fsource"><span class="st'
          + (i ? " faible" : "") + '">●</span></span><b>' + esc(nom(s))
          + "</b></li>";
      });
    /* LE CONTOUR DE LA FICHE. Ces deux-là n'ont pas de référentiel côté
       serveur : l'état de lecture ne quitte jamais le navigateur, le serveur
       ne le connaît donc pas et ne peut pas le nommer. */
    h += '<li><span class="bl-lg-c neuf"></span><b>' + esc(t("bl.leg.neuf")) + "</b></li>"
      + '<li><span class="bl-lg-c lu"></span><b>' + esc(t("bl.leg.lu")) + "</b></li>";
    return h + "</ul>";
  }

  /* UN GROUPE DU MENU — son titre, son icône, sa teinte.

     LA TEINTE EST PORTÉE PAR UNE CLASSE, PAS PAR UN ATTRIBUT `style`.
     conseilprevcyber écrit `style="--nav-ic:var(--cyan)"` sur chaque section,
     et c'est très bien chez lui. Ici la politique de sécurité de contenu se
     ferme sur `style-src 'self'` : un attribut `style` serait refusé par le
     navigateur lui-même, et les icônes sortiraient toutes grises sans qu'une
     erreur ne s'affiche nulle part. La teinte vit donc dans la feuille de
     style, avec le reste des décisions de couleur — ce qui est de toute façon
     sa place. */
  function groupe(cle, titre, dedans) {
    return '<section class="bl-g g-' + cle + '">'
      + '<p class="bl-t">' + icone("g-" + cle, "bl-ic-g") + "<span>"
      + esc(titre) + "</span></p>" + dedans + "</section>";
  }

  function rendre() {
    var hote = document.querySelector("[data-barre]");
    if (!hote) return;
    var secs = sections();
    var h = '<div class="bl-tete">'
      + '<span class="bl-marque">CONSEILPREV <b>INFO</b></span>'
      + '<button type="button" class="bl-x" id="bl-x" aria-label="'
      + esc(t("bl.fermer")) + '" title="' + esc(t("bl.fermer")) + '">✕</button>'
      + "</div>"
      + '<nav class="bl-nav" aria-label="' + esc(t("bl.pages")) + '">';

    /* L'ÉTAT DU CORPUS EN TÊTE DE BARRE. Il est REMPLI par la page — la
       barre ne sait pas compter des fiches et ne doit pas apprendre : elle
       réserve la place, le moteur écrit dedans. Caché tant qu'il est vide,
       pour ne pas afficher un cadre creux pendant le chargement.

       ET LA PLACE N'EST RÉSERVÉE QUE LÀ OÙ QUELQU'UN L'ÉCRIT. Constaté au
       navigateur : sur la page de confidentialité, où aucun moteur ne tourne,
       la barre affichait « LE CORPUS » suivi de deux cadres vides — un titre
       qui promet un état et ne le donne jamais. La page déclare donc si elle
       remplit ce bloc, comme elle déclare si elle veut la légende. */
    if (hote.hasAttribute("data-barre-etat")) {
      h += groupe("corpus", t("bl.etat"),
        '<div class="bl-etat" id="bl-etat" hidden></div>'
        /* CE QUI RESTE À LIRE, ET DE QUOI L'OUBLIER. Une mémoire qu'on ne peut
           pas effacer n'est pas une commodité, c'est un fichier — même tenu
           dans le navigateur du lecteur. Le bouton est donc à côté du compte,
           pas dans une page de réglages qu'on ne trouve jamais. */
        + '<div class="bl-lu" id="bl-lu" hidden></div>');
    }

    var l = "";
    PAGES.forEach(function (p) {
      l += '<li><a href="' + p.href + '"' + (ici(p.href) ? ' aria-current="page"' : "")
        + '>' + icone(p.href, "bl-ic")
        + '<span class="bl-lb"><b>' + esc(t(p.cle)) + "</b><span>"
        + esc(t(p.dit)) + "</span></span></a></li>";
    });
    h += groupe("site", t("bl.pages"), '<ul class="bl-l">' + l + "</ul>");

    if (secs.length) {
      l = "";
      secs.forEach(function (s) {
        l += '<li><a href="#' + esc(s.id) + '" data-va="' + esc(s.id) + '"'
          + (s.glose ? ' title="' + esc(s.glose) + '"' : "")
          + ">" + icone(s.id, "bl-ic bl-ic-s")
          + "<span>" + esc(s.titre) + "</span>"
          + (s.compteur ? '<i data-de="' + esc(s.compteur) + '"></i>' : "")
          + "</a></li>";
      });
      h += groupe("sections", t("bl.sections"), '<ul class="bl-l bl-s">' + l + "</ul>");
    }

    if (hote.hasAttribute("data-barre-legende")) {
      h += groupe("legende", t("bl.legende"), legende());
    }

    /* CE QUE LE SITE GARDE DE VOUS, à un clic de toutes les pages. Une
       politique de confidentialité qu'on ne trouve qu'au pied de l'accueil
       n'est pas consultée ; celle-ci dit un inventaire court, et c'est
       justement parce qu'il est court qu'il faut le rendre facile à vérifier. */
    h += '<p class="bl-pied"><a href="/confidentialite">'
      + esc(t("bl.vieprivee")) + "</a></p>";

    h += "</nav>";
    hote.innerHTML = h;
    suivreCompteurs();
    suivreLecture(secs);
    var x = $("bl-x");
    if (x) x.addEventListener("click", function () { ouvrir(false); });
  }

  /* LE COMPTE DE LA BARRE EST CELUI DE LA RUBRIQUE, recopié à chaque fois
     qu'il change. Deux nombres différents pour la même chose sur le même
     écran valent moins qu'aucun nombre. */
  function suivreCompteurs() {
    Array.prototype.forEach.call(document.querySelectorAll("[data-de]"), function (cible) {
      var src = $(cible.getAttribute("data-de"));
      if (!src) return;
      var copier = function () {
        var v = (src.textContent || "").replace(/\s+/g, " ").trim();
        cible.textContent = v;
        cible.hidden = !v;
      };
      copier();
      try { new MutationObserver(copier).observe(src, { childList: true, characterData: true, subtree: true }); }
      catch (e) { /* sans observateur, le compte reste celui du chargement */ }
    });
  }

  /* LA SECTION EN COURS DE LECTURE EST MARQUÉE. Sans cela, une barre de
     navigation sur une page longue dit où l'on peut aller sans jamais dire
     où l'on est. */
  function suivreLecture(secs) {
    var titres = secs.map(function (s) { return $(s.id); }).filter(Boolean);
    if (!titres.length || typeof IntersectionObserver === "undefined") return;
    var vus = {};
    var obs = new IntersectionObserver(function (entrees) {
      entrees.forEach(function (e) { vus[e.target.id] = e.isIntersecting; });
      var courant = null;
      titres.forEach(function (h) { if (vus[h.id] && !courant) courant = h.id; });
      Array.prototype.forEach.call(document.querySelectorAll("[data-va]"), function (a) {
        a.classList.toggle("bl-ici", a.getAttribute("data-va") === courant);
      });
    }, { rootMargin: "-70px 0px -70% 0px" });
    titres.forEach(function (h) { obs.observe(h); });
  }

  /* ── LE REPLI ────────────────────────────────────────────────────────────
     UNE BARRE REPLIÉE N'EST PAS SEULEMENT INVISIBLE : elle doit sortir du
     parcours. Déplacée par `transform` ou masquée par la grille, elle reste
     dans l'ordre de tabulation et dans l'arbre d'accessibilité — un lecteur au
     clavier traverse donc une dizaine de liens hors écran avant d'atteindre la
     page, et un lecteur d'écran les annonce tous. `inert` l'en retire, et
     `aria-hidden` le dit aux navigateurs qui ne le connaissent pas encore.

     LE CHOIX EST RETENU, MAIS PAS LE MÊME PARTOUT. Sous 1100 px la barre est
     un panneau qui recouvre la page : l'ouvrir par défaut mettrait le lecteur
     devant un menu au lieu du journal. Au-dessus, c'est une colonne à côté du
     texte : la replier par défaut ferait disparaître les repères que la page
     vient de construire. Le défaut suit donc la largeur ; le choix explicite,
     lui, est le même partout et vaut jusqu'à ce qu'on en change. */
  var _large = null;

  function large() {
    try { return window.matchMedia("(min-width:1100px)").matches; }
    catch (e) { return true; }
  }

  function lu() {
    try { return localStorage.getItem(CLE_ETAT); }
    catch (e) { return null; }           /* navigation privée : sans mémoire */
  }

  function ecrire(v) {
    try { localStorage.setItem(CLE_ETAT, v); } catch (e) { /* idem */ }
  }

  function ouvrir(o, retenir) {
    var b = $("bl-bouton"), c = document.querySelector("[data-barre]");
    if (!b || !c) return;
    c.classList.toggle("bl-ouverte", o);
    document.documentElement.classList.toggle("bl-repliee", !o);
    b.setAttribute("aria-expanded", o ? "true" : "false");
    b.setAttribute("aria-label", t(o ? "bl.fermer" : "bl.ouvrir"));
    b.setAttribute("title", t(o ? "bl.fermer" : "bl.ouvrir"));
    if (o) { c.removeAttribute("inert"); c.removeAttribute("aria-hidden"); }
    else { c.setAttribute("inert", ""); c.setAttribute("aria-hidden", "true"); }
    if (retenir) ecrire(o ? "ouverte" : "repliee");
  }

  function etatVoulu() {
    var v = lu();
    return v === "ouverte" ? true : (v === "repliee" ? false : large());
  }

  function replier() {
    var b = $("bl-bouton"), c = document.querySelector("[data-barre]");
    if (!b || !c) return;
    _large = large();
    /* Au changement de largeur, un choix explicite reste ; sans choix, le
       défaut de la nouvelle largeur s'applique. Sans cela, une barre ouverte
       en colonne devenait un panneau plein écran au premier pivotement de
       téléphone. */
    try {
      window.matchMedia("(min-width:1100px)").addEventListener("change", function () {
        var n = large();
        if (n === _large) return;
        _large = n;
        ouvrir(etatVoulu(), false);
      });
    } catch (e) { /* navigateur ancien : l'état du chargement fait foi */ }
    b.addEventListener("click", function () {
      ouvrir(!c.classList.contains("bl-ouverte"), true);
    });
    /* Un clic sur un lien de PAGE referme quand la barre recouvre le texte ;
       un clic sur une ancre de section aussi, pour la même raison. En colonne,
       fermer serait une punition pour avoir navigué. */
    c.addEventListener("click", function (e) {
      if (e.target.closest("a") && !large()) ouvrir(false, false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !large() && c.classList.contains("bl-ouverte"))
        ouvrir(false, false);
    });
    ouvrir(etatVoulu(), false);
  }

  /* ── LA PAGE QUI ARRIVE APRÈS LA BARRE ───────────────────────────────────
     DÉFAUT CONSTATÉ AU NAVIGATEUR. Les rubriques de l'accueil sont dans le
     HTML servi ; celles d'une fiche sont écrites par `fiche.js` une fois la
     réponse revenue — c'est-à-dire APRÈS que la barre s'est construite. Elle
     n'en trouvait donc aucune et n'offrait, sur la deuxième page la plus
     longue du site, que la liste des pages.

     Une convocation explicite depuis `fiche.js` aurait marché le jour où on
     l'écrit, et serait tombée le jour où quelqu'un ajoute une troisième page
     à rendu différé. L'observation ne peut pas être oubliée. Elle ne
     reconstruit QUE si la liste des identifiants a changé : les compteurs, eux,
     sont suivis un par un et n'ont pas à faire refaire la barre entière. */
  var _signature = null;

  function signature() {
    return sections().map(function (s) { return s.id; }).join("|");
  }

  function suivrePage() {
    var m = document.querySelector("main");
    if (!m || typeof MutationObserver === "undefined") return;
    _signature = signature();
    var attente = null;
    var obs = new MutationObserver(function () {
      if (attente) return;
      attente = setTimeout(function () {
        attente = null;
        var s = signature();
        if (s === _signature) return;
        _signature = s;
        rendre();
      }, 60);
    });
    /* LES ATTRIBUTS COMPTENT AUTANT QUE LES ENFANTS. Un panneau qu'on révèle
       en retirant `hidden` ne change aucun nœud : sans cette ligne, la barre
       resterait sur les rubriques d'avant la connexion, et resterait fausse
       jusqu'au prochain rechargement. */
    obs.observe(m, { childList: true, subtree: true,
                     attributes: true, attributeFilter: ["hidden", "class"] });
  }

  function demarrer() {
    rendre();
    replier();
    suivrePage();
    if (document.querySelector("[data-barre-legende]")) referentiel(rendre);
    /* La barre est réécrite à la bascule de langue : ses libellés viennent du
       dictionnaire, et les titres de section viennent de la page — qui vient
       elle aussi d'être retraduite. L'ordre importe, d'où l'écoute. */
    document.addEventListener("langue", rendre);
  }

  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", demarrer);
  else demarrer();
})();
