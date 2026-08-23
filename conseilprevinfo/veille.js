/* CONSEILPREV INFO — l'interface de veille.
   ─────────────────────────────────────────
   CE FICHIER N'ÉCRIT AUCUN CONTENU. Il rend ce que le serveur sert : les
   fiches, les facettes, le vocabulaire. Recopier ici un intitulé de statut ou
   une liste de sujets les figerait au jour de l'écriture, et c'est l'écran
   qui ferait foi pour le lecteur alors que le moteur dirait autre chose.

   AUCUNE REQUÊTE SANS DÉLAI. Une requête suspendue ne rejette jamais : la
   page resterait sur « Chargement… » indéfiniment, sans un mot. Bornée, elle
   rend la main et l'explique. */
(function () {
  "use strict";

  var DELAI = 20000;
  var REF = null, FACETTES = null;

  /* Nommé `tr` et non `t` : deux fonctions de ce fichier emploient déjà `t`
     comme variable locale — le minuteur de `demander`, la liste des termes de
     `chargerDossiers`. Une ombre silencieuse y aurait fait appeler un tableau
     comme une fonction, au premier usage et pas avant. */
  function tr(c) { return (window.L && window.L.t) ? window.L.t(c) : c; }

  /* LES LIBELLÉS DU RÉFÉRENTIEL, DANS LES DEUX LANGUES. Le serveur sert
     `sujet_nom` en français sur chaque fiche : le recopier tel quel laisserait
     des pastilles françaises sur une interface anglaise. La table est bâtie
     depuis `/api/veille/referentiel`, qui porte `nom` ET `nom_en` — la page
     ne traduit rien elle-même, elle choisit parmi ce que le moteur déclare. */
  var NOMS = {};
  /* LE LIBELLÉ SUIT LA LANGUE DE CE QU'IL NOMME, pas celle de l'interface.
     La portée, le sujet et le statut qualifient LA FICHE : « Lecture dérivée
     par règles » en tête d'un paragraphe anglais est un libellé qui ment sur
     ce qu'il coiffe. Le serveur a déjà posé le bon nom dans la fiche — c'est
     lui qui détient les deux colonnes — et `defaut` le porte ; la table
     locale ne sert que de repli, dans la langue des analyses. */
  function nommer(genre, cle, defaut) {
    var l = (window.L && window.L.analyses) ? window.L.analyses()
            : (window.L && window.L.courante ? window.L.courante() : "fr");
    var e = NOMS[genre] && NOMS[genre][cle];
    if (!e) return defaut || cle || "";
    return (l === "en" && e.en) ? e.en : e.fr;
  }
  function ranger(genre, liste) {
    NOMS[genre] = {};
    (liste || []).forEach(function (x) {
      NOMS[genre][x.cle] = { fr: x.nom, en: x.nom_en || x.nom };
    });
  }

  function $(id) { return document.getElementById(id); }
  function esc(x) {
    return String(x == null ? "" : x).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function demander(url) {
    var ctrl = (typeof AbortController !== "undefined") ? new AbortController() : null;
    var fini = false;
    var t = setTimeout(function () {
      if (!fini && ctrl) { try { ctrl.abort(); } catch (e) {} }
    }, DELAI);
    return fetch(url, { credentials: "same-origin",
                        signal: ctrl ? ctrl.signal : undefined })
      .then(function (r) {
        fini = true; clearTimeout(t);
        if (!r.ok) { var e = new Error("http"); e.statut = r.status; throw e; }
        return r.json();
      }, function (e) {
        fini = true; clearTimeout(t);
        if (e && e.name === "AbortError") {
          var d = new Error("delai"); d.name = "DelaiDepasse"; throw d;
        }
        throw e;
      });
  }

  var MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
              "août", "septembre", "octobre", "novembre", "décembre"];
  /* LA DATE SUIT LA LANGUE — `langue.js` la formate pour les quatre pages.
     DÉFAUT CONSTATÉ AU NAVIGATEUR : la table de mois locale rendait
     « collected on 23 août 2026 » au milieu d'une phrase anglaise, et
     « 23 février 2026 » sur chaque carte. Un reste de ce genre fait douter
     de tout le reste. */
  function frDate(iso) {
    if (window.L && window.L.date) return window.L.date(iso);
    if (!iso) return "—";
    var p = String(iso).slice(0, 10).split("-");
    if (p.length !== 3) return String(iso);
    return Number(p[2]) + " " + MOIS[Number(p[1]) - 1] + " " + p[0];
  }

  /* ── UNE FICHE ────────────────────────────────────────────────────────
     Les trois blocs — lecture, portée, réserve — sont rendus SÉPARÉMENT et
     étiquetés. Fondus en un paragraphe, l'avis deviendrait indiscernable du
     constat, ce qui est exactement la confusion que ce site refuse. */
  function fiche(f, rang) {
    /* LE RANG N'EST PAS UNE DÉCORATION, C'EST L'ORDRE DU MOTEUR RENDU
       LISIBLE. Le site classe déjà par portée puis par date — « le plus
       important d'abord, puis le plus récent » — mais l'affichait à plat, si
       bien qu'un lecteur ne pouvait pas voir ce qui vient en tête. Une
       première page de journal fait exactement cela : elle donne à la tête la
       place qui dit son rang. Rien n'est ajouté, rien n'est noté ; c'est le
       même tri, montré. */
    /* L'ÉTAT DE LECTURE EST PORTÉ PAR LA CARTE, pas par une pastille : les
       pastilles disent ce que la fiche EST, ce contour dit où VOUS en êtes.
       Deux natures d'information, deux canaux. */
    var etat = (window.LU ? window.LU.classe(f.id) : "");
    /* LA FICHE DIT ELLE-MÊME QUAND SON ANALYSE N'A PAS SUIVI. Le bandeau de
       tête annonce la réserve pour tout le corpus ; il ne dit pas LAQUELLE
       des soixante cartes à l'écran est concernée. Sans ce repère, un lecteur
       anglophone tombe sur un paragraphe français au milieu de la page et en
       conclut que le site est cassé. */
    var repli = (langueAnalyses() === "en" && f.analyses_traduites === false);
    var h = '<article class="fiche ' + etat
      + (rang === "tete" ? " tete" : "")
      + (repli ? " an-repli" : "") + '" data-fid="' + esc(f.id) + '">';
    h += '<div class="fmeta">'
      + '<span class="past ' + esc(f.impact) + '">'
      + esc(nommer("impact", f.impact, f.impact_nom)) + '</span>'
      + '<span class="past sujet">'
      + esc(nommer("sujet", f.sujet, f.sujet_nom)) + '</span>'
      + (f.horizon === "projete"
          ? '<span class="past signal_faible">Projection</span>' : "")
      /* UNE DATE FABRIQUÉE PORTE SA MARQUE DÈS LA VIGNETTE. Sans elle, le
         fil aligne des dates dont certaines sont observées et d'autres
         posées par nous, sans que rien ne les distingue. */
      + '<span class="fdate">' + esc(frDate(f.date_fait))
      + (f.date_convention ? ' <b class="conv">convention</b>' : "")
      + '</span></div>';

    /* CHAQUE FICHE A SON ADRESSE. Sans lien, rien ne se cite ni ne se
       transmet : un lecteur ne peut renvoyer un collègue qu'au site entier. */
    h += '<h3 class="ftitre"><a href="/fiche/' + esc(f.id)
      + '" class="nu">' + esc(f.titre)
      + '</a></h3>';
    if (f.chapeau) h += '<p class="fchapeau">' + esc(f.chapeau) + '</p>';

    if (repli) h += '<p class="an-r" lang="fr">' + esc(tr("an.repli")) + '</p>';
    h += '<div class="fbloc lecture"><span class="fbloc-t">' + esc(tr("js.lecture"))
      + esc(nommer("lecture", f.lecture_nature, f.lecture_nom))
      + '</span><p>' + esc(f.lecture) + '</p></div>';
    h += '<div class="fbloc portee"><span class="fbloc-t">' + esc(tr("js.change"))
      + '</span><p>' + esc(f.portee) + '</p></div>';
    h += '<div class="fbloc doute"><span class="fbloc-t">' + esc(tr("js.doute"))
      + '</span><p>' + esc(f.incertitude) + '</p></div>';

    var s = f.source || {};
    var faible = f.statut !== "verifiee_source_primaire";
    h += '<div class="fsource">'
      + '<span class="st' + (faible ? " faible" : "") + '">● '
      + esc(nommer("statut", f.statut, f.statut_nom)) + '</span>'
      + esc(s.nom || "") + ' — ' + esc(s.editeur || "")
      + (s.url ? ' · <a href="' + esc(s.url) + '" target="_blank" rel="noopener">'
                 + esc(tr("js.consulter")) + '</a>' : "")
      + (s.licence ? '<br>' + esc(s.licence) : "")
      + '</div></article>';
    return h;
  }

  /* UN MENU VIDE DIT POURQUOI IL L'EST — il ne se contente pas de l'être.

     Depuis que les menus décrivent LES FICHES TROUVÉES, certains se vident
     légitimement : la rubrique « Systèmes d'IA » ne porte aucun pays, et son
     menu Pays n'a donc rien à proposer. C'est une information, pas une panne
     — mais un menu réduit à « Tous », désactivé sans un mot, se lit
     exactement comme un chargement raté. Il porte donc son motif, à
     l'endroit même où le lecteur allait cliquer. */
  function options(sel, liste, valeur, libelle, compte, videDit) {
    var el = $(sel);
    if (!el) return;
    var garde = el.value;
    var premier = el.options.length ? el.options[0] : null;
    var neutre = premier ? premier.getAttribute("data-i18n") : null;
    var h = premier ? premier.outerHTML : "";
    (liste || []).forEach(function (x) {
      h += '<option value="' + esc(x[valeur]) + '">' + esc(x[libelle])
        + (compte && x.n != null ? " (" + x.n + ")" : "") + "</option>";
    });
    el.innerHTML = h;
    if (garde) el.value = garde;

    var vide = !(liste || []).length && !garde;
    el.disabled = vide && !!videDit;
    el.classList.toggle("vide-dit", vide && !!videDit);
    if (el.options[0]) {
      /* L'intitulé neutre reprend sa place dès que l'axe redonne quelque
         chose : sans cela, « aucun pays » resterait affiché après un
         élargissement du filtre. */
      el.options[0].textContent = vide && videDit ? tr(videDit)
        : (neutre ? tr(neutre) : el.options[0].textContent);
    }
  }

  /* LA SEULE TABLE DES FILTRES. Elle sert à interroger le serveur, à écrire
     l'adresse et à la relire : trois listes séparées auraient divergé, et une
     vue partagée se serait ouverte différemment de celle qu'on avait sous les
     yeux. */
  var FILTRES = [["sujet", "f-sujet"], ["pays", "f-pays"],
                 ["techno", "f-techno"], ["impact", "f-impact"],
                 ["horizon", "f-horizon"], ["depuis", "f-depuis"],
                 ["q", "f-q"]];

  /* COMBIEN DE FILTRES SONT ACTIFS — compté depuis la MÊME table que la
     requête et l'adresse. Un compte tenu à part finirait par annoncer
     « 2 actifs » sur une page qui n'en applique qu'un, et c'est le genre
     d'écart qui fait douter du reste.

     REMONTÉE AU NIVEAU DU MODULE : elle vivait dans `demarrer()`, où elle ne
     servait qu'au bouton de repli. L'ordre de lecture noté pour les flèches a
     besoin du même nombre, et le recompter à côté aurait produit exactement
     l'écart que le commentaire ci-dessus décrit. */
  function compterActifs() {
    var n = FILTRES.filter(function (f) {
      var el = $(f[1]); return el && el.value;
    }).length;
    var e = $("f-actifs");
    if (e) e.textContent = n ? n + " " + tr("f.actifs") : tr("f.aucun.actif");
    return n;
  }

  /* LA LANGUE DES ANALYSES VOYAGE AVEC LA REQUÊTE, jamais après. Traduire au
     client supposerait d'avoir les deux colonnes en mémoire ; c'est le serveur
     qui les a, et lui seul sait laquelle existe pour chaque fiche. */
  function langueAnalyses() {
    return (window.L && window.L.analyses) ? window.L.analyses() : "fr";
  }

  function parametres(pourAdresse) {
    var q = [];
    FILTRES.forEach(function (p) {
      var v = ($(p[1]) || {}).value;
      if (v) q.push(p[0] + "=" + encodeURIComponent(v));
    });
    /* L'ADRESSE DE LA PAGE NE PORTE PAS LA LANGUE : c'est un réglage de
       lecteur, pas un filtre. Collée dans l'adresse, elle voyagerait avec
       chaque lien partagé et imposerait au destinataire la langue de
       l'expéditeur. */
    if (!pourAdresse && langueAnalyses() === "en") q.push("analyses=en");
    return q.length ? "?" + q.join("&") : "";
  }

  /* ── UNE VUE FILTRÉE DOIT POUVOIR SE TRANSMETTRE ──────────────────────
     Ce site écrit, sur chaque fiche : « sans lien, rien ne se cite ni ne se
     transmet ». L'argument valait pour les fiches et pas pour les vues : un
     lecteur qui filtrait « systèmes d'IA, depuis janvier » ne pouvait
     envoyer à un collègue que l'adresse du site entier, à charge pour lui de
     refaire les mêmes gestes — et rien ne garantissait qu'il les refasse.

     `replaceState` et non `pushState` : un filtre n'est pas une navigation.
     Empiler une entrée d'historique par frappe dans la recherche obligerait
     à appuyer douze fois sur « Précédent » pour sortir de la page. */
  function ecrireAdresse() {
    if (!window.history || !history.replaceState) return;
    try {
      history.replaceState(null, "", parametres(true) || location.pathname);
    } catch (e) { /* adresse non modifiable : la page reste utilisable */ }
  }

  /* Lue AVANT le premier chargement, sinon la page s'ouvre sur le corpus
     entier puis se rétracte — et le lecteur voit passer des fiches qu'il n'a
     pas demandées. */
  function lireAdresse() {
    var p;
    try { p = new URLSearchParams(location.search); } catch (e) { return; }
    FILTRES.forEach(function (f) {
      var el = $(f[1]), v = p.get(f[0]);
      if (!el || v == null) return;
      /* UNE VALEUR ABSENTE DE LA LISTE EST IGNORÉE, pas forcée. Une adresse
         ancienne peut nommer un pays que le corpus ne porte plus ; l'imposer
         afficherait un écran vide sans dire pourquoi. */
      if (el.tagName === "SELECT"
          && !Array.prototype.some.call(el.options, function (o) {
               return o.value === v; })) return;
      el.value = v;
    });
  }

  function rendreEtat(d, ruptures) {
    var e = $("etat");
    if (!e) return;
    var et = d.etat || {};
    var mauvaises = (et.journal || []).filter(function (j) { return !j.ok; });
    var quand = et.collecte_le ? frDate(et.collecte_le) : "—";

    /* LA MANCHETTE — LE CAS NORMAL, EN UNE LIGNE. Ses quatre valeurs sortent
       des MÊMES variables que le bandeau et que la barre, et c'est tout le
       point : trois endroits qui affichent le même compte ne valent que s'ils
       ne peuvent pas diverger, et la seule façon de s'en assurer est qu'un
       seul calcul les remplisse tous les trois. */
    var mn = $("manchette");
    if (mn) {
      $("mn-date").textContent = quand;
      $("mn-fiches").textContent = et.fiches || 0;
      $("mn-rupt").textContent = (ruptures == null ? "—" : ruptures);
      var s = $("mn-src");
      s.className = "mn-src " + (mauvaises.length ? "ko" : "ok");
      s.textContent = mauvaises.length
        ? mauvaises.length + " " + tr("js.muettes")
        : tr("mn.src.ok");
      mn.hidden = false;
    }

    /* LE BANDEAU NE RESTE QUE POUR CE QUI NE VA PAS. Il annonçait « Corpus :
       98 fiches, collectées le 23 août 2026. Toutes les sources interrogées
       ont répondu. » à chaque visite — un bandeau d'alerte qui s'affiche aussi
       quand il n'y a pas d'alerte n'alerte plus. Il nomme les sources muettes,
       ce que la manchette ne peut pas faire en une ligne : c'est ce qui lui
       reste, et c'est ce pour quoi il servait vraiment. */
    if (!mauvaises.length) {
      e.hidden = true;
      e.innerHTML = "";
    } else {
      e.hidden = false;
      e.className = "bandeau-etat alerte";
      e.innerHTML = "<b>" + esc(tr("js.corpus")) + (et.fiches || 0) + " "
        + esc(tr("js.fiches")) + "</b>" + esc(tr("js.collectees")) + esc(quand)
        + "." + " <b>" + mauvaises.length + " " + esc(tr("js.muettes")) + "</b> "
        + mauvaises.map(function (j) {
            return esc(j.source) + " — " + esc(j.message || j.erreur || "");
          }).join(" ; ")
        + esc(tr("js.muettes.fin"));
    }

    /* LA BARRE PORTE L'ÉTAT DISTILLÉ, DEPUIS LE MÊME CALCUL. Le bandeau dit
       tout ; la barre dit l'essentiel — combien de fiches, de quand, et si
       une source a manqué — parce que le bandeau disparaît dès qu'on
       descend, et qu'un lecteur au milieu du fil ne sait plus si ce qu'il
       lit date d'aujourd'hui ou de la semaine dernière.

       ELLE RECOPIE, ELLE NE RECALCULE PAS. Un second calcul, même juste,
       finirait par afficher un autre nombre que celui d'à côté. */
    var b = $("bl-etat");
    if (b) {
      b.innerHTML =
        '<span class="bl-n">' + (et.fiches || 0) + '</span>'
        + '<span class="bl-q">' + esc(tr("js.fiches")) + '</span>'
        + '<span class="bl-d">' + esc(quand) + '</span>'
        + (mauvaises.length
            ? '<span class="bl-ko">' + mauvaises.length + ' '
              + esc(tr("bl.muettes")) + '</span>' : "");
      b.hidden = false;
    }
  }

  /* LE NUMÉRO DE DEMANDE — pourquoi il existe.

     DÉFAUT CORRIGÉ, constaté au navigateur. Chercher « rockwell » puis
     cliquer « Tout afficher » laissait UNE SEULE fiche à l'écran alors que
     le dernier appel envoyé était bien le bon, sans filtre. La réponse au
     filtre précédent arrivait après celle du dégagement et réécrivait la
     page : le lecteur voyait donc un fil qui contredisait ses propres
     filtres, tous remis à zéro à l'écran.

     C'est la faute la plus traître d'une page filtrable, parce qu'elle ne
     ressemble pas à une panne — elle ressemble à un corpus pauvre. Un
     lecteur en conclurait qu'il n'existe qu'une fiche.

     La règle : seule la réponse à la DERNIÈRE demande émise a le droit
     d'écrire dans la page. Les autres sont abandonnées en silence — elles
     ne sont pas des erreurs, elles sont périmées. */
  var DEMANDE = 0;

  /* OUVRIR UNE FICHE LA MARQUE LUE, et la carte change sous les yeux — sans
     recharger le fil, qui ferait perdre la position de défilement au moment
     précis où l'on revient de la lecture. */
  function suivreLecture() {
    var f = $("fil"), u = $("une");
    [f, u].forEach(function (z) {
      if (!z) return;
      z.addEventListener("click", function (ev) {
        var a = ev.target.closest && ev.target.closest("a[href^='/fiche/']");
        if (!a) return;
        var carte = a.closest(".fiche");
        var id = carte && carte.getAttribute("data-fid");
        if (window.LU && window.LU.marquer(id)) {
          carte.classList.remove("neuf");
          carte.classList.add("lu");
          window.LU.pulser(carte);
        }
      });
    });
  }

  /* AU RETOUR SUR LE FIL, les fiches lues entre-temps changent d'état. Le
     navigateur restitue la page depuis son cache sans relancer le script :
     sans cette écoute, un lecteur reviendrait sur un fil qui ignore ce qu'il
     vient de lire. */
  function rafraichirEtats() {
    if (!window.LU) return;
    Array.prototype.forEach.call(document.querySelectorAll(".fiche[data-fid]"),
      function (c) {
        var id = c.getAttribute("data-fid");
        var lue = window.LU.estLue(id);
        var avant = c.classList.contains("lu");
        c.classList.toggle("lu", lue);
        c.classList.toggle("neuf", !lue);
        if (lue && !avant) window.LU.pulser(c);
      });
    direLecture();
  }

  /* LE COMPTE DE LECTURE — rempli par la page, comme l'état du corpus. Il dit
     ce qui reste, pas ce qui est lu : c'est ce qui reste qui décide de la
     visite suivante. */
  function direLecture() {
    var e = $("bl-lu");
    if (!e || !window.LU) return;
    /* SANS ACCORD, LE COMPTE N'EST PAS ZÉRO — IL N'EXISTE PAS. Afficher
       « 98 à lire » à qui a refusé la mémoire de lecture affirmerait un suivi
       qui n'a pas lieu, et le nombre ne bougerait jamais : le lecteur en
       conclurait une panne. La barre dit donc ce qui est, et où le changer. */
    if (window.LU.autorise && !window.LU.autorise()) {
      e.hidden = false;
      e.innerHTML = '<span class="bl-lu-non">' + esc(tr("bl.lu.non"))
        + ' <a href="/confidentialite">' + esc(tr("bl.lu.non.lien")) + "</a></span>";
      return;
    }
    var total = (FACETTES && FACETTES.total_publiable) || 0;
    var lues = window.LU.combien();
    var reste = Math.max(0, total - lues);
    e.hidden = false;
    e.innerHTML = "<b>" + reste + "</b><span>" + esc(tr("bl.reste")) + "</span>"
      + (lues ? '<button type="button" id="bl-oubli">'
                + esc(tr("bl.oublier")) + "</button>" : "");
    var b = $("bl-oubli");
    if (b) b.addEventListener("click", function () {
      /* PAS DE « ÊTES-VOUS SÛR ? » CREUX : la question dit ce qui disparaît,
         et rien d'autre ne disparaît. */
      if (window.confirm(tr("bl.oublier.sur"))) window.LU.oublier();
    });
  }

  /* LES INTERTITRES DE PORTÉE — l'ordre du moteur, rendu visible.
     ─────────────────────────────────────────────────────────────
     LE FIL EST CLASSÉ « le plus important d'abord, puis le plus récent ». Ce
     classement était invisible : soixante cartes identiques dont un lecteur
     ne pouvait pas savoir qu'elles étaient rangées, ni selon quoi. Il
     parcourait donc le haut de la liste en croyant lire du récent, alors
     qu'il lisait du structurant.

     RIEN N'EST AJOUTÉ, RIEN N'EST RÉORDONNÉ. Un intertitre est posé LÀ OÙ LA
     PORTÉE CHANGE, en lisant la liste dans l'ordre où elle arrive. Le jour où
     le tri du moteur changerait, ces marques changeraient avec lui — et si le
     tri cessait de grouper les portées, elles se répéteraient, ce qui est
     exactement ce qu'il faudrait voir. Une mise en page qui trierait
     elle-même cacherait ce défaut au lieu de le montrer.

     LE COMPTE DE CHAQUE BLOC EST MESURÉ sur la même liste, dans la même
     passe. */
  function composerFil(fil) {
    var blocs = [], prec = null;
    fil.forEach(function (f) {
      if (f.impact !== prec) { blocs.push([f]); prec = f.impact; }
      else blocs[blocs.length - 1].push(f);
    });
    return blocs.map(function (b) {
      var f = b[0];
      return '<h3 class="intertitre ' + esc(f.impact) + '">'
        + '<span>' + esc(nommer("impact", f.impact, f.impact_nom)) + '</span>'
        + '<i>' + b.length + ' ' + esc(tr("js.fiches")) + '</i></h3>'
        + b.map(function (x) { return fiche(x); }).join("");
    }).join("");
  }

  function charger() {
    var url = "/api/veille" + parametres();
    /* L'ADRESSE EST ÉCRITE AVANT LA RÉPONSE, pas après : elle décrit ce qui a
       été DEMANDÉ. Attendre la réponse laisserait, le temps d'un aller-retour,
       une adresse qui contredit l'écran — et c'est cet instant-là qu'un
       lecteur choisit pour copier le lien. */
    ecrireAdresse();
    /* LES MENUS SUIVENT LE FIL, dans la même respiration. Rechargés à part,
       ils décriraient l'état précédent le temps d'un aller-retour — et c'est
       cet instant-là que le lecteur choisit pour ouvrir un menu. */
    chargerFacettes();
    var mien = ++DEMANDE;
    demander(url).then(function (d) {
      if (mien !== DEMANDE) return;
      if (!d.ok) throw new Error("api");
      var toutes = d.fiches || [];
      /* LA UNE : ce qui rompt, et rien d'autre. Une « une » qui reprendrait
         les premières fiches du fil ne serait qu'un doublon de mise en page. */
      var une = toutes.filter(function (f) { return f.impact === "rupture"; });
      var fil = toutes.filter(function (f) { return f.impact !== "rupture"; });
      /* L'ÉTAT EST RENDU APRÈS LA SÉPARATION, et non avant : la manchette
         porte le nombre de ruptures, qui est la longueur de la une. Le
         recompter dans `rendreEtat` referait le même filtre à un second
         endroit — le genre d'écart qui finit par afficher deux nombres. */
      rendreEtat(d, une.length);

      $("une").innerHTML = une.length
        ? une.map(function (f, i) { return fiche(f, i === 0 ? "tete" : ""); }).join("")
        : '<div class="vide"><b>' + esc(tr("js.une.rien")) + '</b>'
          + esc(tr("js.une.vide")) + ' ' + esc(tr("js.une.vide2")) + '</div>';
      $("c-une").textContent = une.length + " " + tr("js.fiches");

      $("fil").innerHTML = fil.length
        ? composerFil(fil)
        : '<div class="vide"><b>' + esc(tr("js.fil.vide")) + '</b>'
          + esc(tr("js.fil.vide2")) + '</div>';
      $("c-fil").textContent = fil.length + " " + tr("js.fiches");
      direLecture();

      /* L'ORDRE DE LECTURE EST NOTÉ ICI, ET NULLE PART AILLEURS — c'est le
         seul endroit qui connaisse l'ordre RÉELLEMENT AFFICHÉ : la une
         d'abord, le fil ensuite, tous deux issus du tri du moteur et de VOS
         filtres. Le reconstruire ailleurs, même correctement, produirait tôt
         ou tard un « suivant » qui n'est pas celui de l'écran.

         Il sert aux flèches ← et →, qui portent alors le rang et la taille du
         fil. Sans lui, elles s'éteignent en disant pourquoi plutôt que de
         renvoyer au hasard du corpus entier. */
      if (window.FL) {
        window.FL.noter(
          toutes.map(function (f) { return f.id; }),
          compterActifs()
            ? tr("fl.filtre").replace("{n}", compterActifs())
            : tr("fl.toutcorpus"));
      }

      /* LA COUPE EST ANNONCÉE, jamais laissée à la soustraction du lecteur.
         Le serveur dit lui-même s'il a coupé : le client ne le déduit pas de
         deux nombres, sans quoi la règle vivrait à deux endroits et l'un des
         deux finirait faux. */
      $("f-compte").innerHTML = "<b>" + d.total + "</b> " + esc(tr("js.fiches"))
        + " " + esc(tr("js.retenues"))
        + (d.tronque ? ", <b>" + d.affichees + "</b> " + esc(tr("js.affichees")) : "");
      var c = $("f-coupe");
      if (c) {
        c.textContent = d.tronque_dit || "";
        c.hidden = !d.tronque;
      }
    }).catch(function (e) {
      /* Une demande périmée qui échoue ne doit pas non plus alarmer : son
         résultat n'intéresse plus personne. */
      if (mien !== DEMANDE) return;
      var msg = (e && e.name === "DelaiDepasse")
        ? tr("js.delai") : tr("js.erreur");
      $("etat").className = "bandeau-etat alerte";
      $("etat").textContent = msg;
    });
  }

  /* LE RÉFÉRENTIEL EST LU AVANT LE PREMIER RENDU : sans lui, `nommer()`
     retomberait sur le libellé français servi avec la fiche, et l'interface
     anglaise s'ouvrirait avec des pastilles françaises avant de se corriger.
     Il porte aussi la RÉSERVE DE TRADUCTION, mesurée par le serveur. */
  function chargerReferentiel() {
    return demander("/api/veille/referentiel").then(function (d) {
      if (!d.ok) return;
      REF = d;
      ranger("sujet", d.sujets); ranger("impact", d.impacts);
      ranger("horizon", d.horizons); ranger("statut", d.statuts);
      ranger("lecture", d.lectures);
      direReserve();
    }).catch(function () { /* les libellés servis avec la fiche font foi */ });
  }

  /* CE QUE LA BASCULE NE TRADUIT PAS, DIT QUAND ELLE SERT — et seulement
     alors. Afficher la réserve en français à un lecteur français serait lui
     expliquer que le site français est en français. */
  function direReserve() {
    var e = $("tr-dit");
    if (!e) return;
    var lg = REF && REF.langues;
    var en = window.L && window.L.courante() === "en";
    if (!lg || !en) { e.hidden = true; return; }
    e.hidden = false;
    e.innerHTML = "<b>" + esc(tr("tr.titre")) + ".</b> " + esc(lg.dit_en);
  }

  /* LES MENUS DÉCRIVENT LES FICHES TROUVÉES, donc ils suivent les filtres :
     la requête porte les MÊMES paramètres que le fil. Servis sur le corpus
     entier, ils proposaient des combinaisons qui ne rendent rien — choisir
     « Systèmes d'IA » laissait le menu Pays offrir quatorze pays, alors
     qu'aucune fiche de cette rubrique n'en porte. */
  /* LE NUMÉRO DE DEMANDE VAUT AUSSI POUR LES MENUS. Le fil le porte déjà,
     pour une raison mesurée au navigateur : une réponse tardive réécrivait la
     page après un dégagement de filtre. Les menus courent le même risque, en
     pire — ils sont des `<select>`, et une réponse en retard les reconstruit
     SOUS LE DOIGT du lecteur, effaçant le choix qu'il vient de faire. */
  var DEMANDE_F = 0;

  function chargerFacettes() {
    var mien = ++DEMANDE_F;
    return demander("/api/veille/facettes" + parametres()).then(function (d) {
      if (mien !== DEMANDE_F || !d.ok) return;
      FACETTES = d;
      /* LES PAYS ET LES TECHNOLOGIES NE SE TRADUISENT PAS : ce sont des
         données du corpus, pas des libellés du cabinet. « Modbus » et « FR »
         s'écrivent de la même façon dans les deux langues, et les traduire
         reviendrait à réécrire ce que la source déclare. */
      var lib = (window.L && window.L.courante() === "en") ? "nom_en" : "nom";
      options("f-sujet", d.sujets, "cle", lib, true);
      /* LE PAYS PORTE SON NOM. Un menu de codes ISO oblige le lecteur à
         savoir que la France s'écrit FR, et à la chercher entre ES et GB. */
      options("f-pays", d.pays, "cle", lib, true, "f.pays.vide");
      options("f-techno", d.technologies, "cle", "cle", true, "f.techno.vide");
      options("f-impact", d.impacts, "cle", lib, true);
      options("f-horizon", d.horizons, "cle", lib, true);
    }).catch(function () { /* les filtres restent sur « Tous » */ });
  }

  /* LES PISTES. L'ordre des blocs à l'écran est celui du module : ce qui
     déclenche, puis CE QUE LA PISTE N'ÉTABLIT PAS, et seulement ensuite les
     fiches. Un lecteur pressé doit buter sur la réserve, pas la découvrir en
     bas après avoir décidé — c'est pourquoi elle n'est pas reléguée en note. */
  function chargerPistes() {
    demander("/api/veille/pistes").then(function (d) {
      if (!d.ok) return;
      var ps = d.pistes || [];
      $("c-pistes").textContent = ps.length + " " + tr("js.pistes");
      $("pistes").innerHTML = ps.map(function (p) {
        return '<article class="piste">'
          + '<span class="pi-sol s' + p.solidite + '">' + esc(p.solidite_nom)
          + '</span>'
          + '<h3>' + esc(p.titre) + '</h3>'
          + '<div class="fbloc"><span class="fbloc-t">Ce qui la déclenche</span>'
          + '<p>' + esc(p.declencheur) + '</p></div>'
          + '<div class="fbloc doute"><span class="fbloc-t">Ce qu\'elle '
          + 'n\'établit pas</span><p>' + esc(p.n_etablit_pas) + '</p></div>'
          + '<div class="fbloc"><span class="fbloc-t">Ce qu\'elle suppose</span>'
          + '<p>' + esc(p.suppose) + '</p></div>'
          + '<div class="fbloc"><span class="fbloc-t">Ce qui la disqualifierait'
          + '</span><p>' + esc(p.disqualifie_par) + '</p></div>'
          + '<p class="pi-src"><b>Déclenchée par ' + p.n_fiches
          + ' fiche(s) :</b> '
          + (p.fiches || []).map(function (f) {
              return '<a href="/fiche/' + esc(f.id) + '">' + esc(f.titre) + '</a>';
            }).join(' · ')
          + (p.fiches_non_listees
              ? ' <i>(+' + p.fiches_non_listees + ' '
                + esc(tr("js.non_listees")) + ')</i>' : '')
          + '</p></article>';
      }).join("") || '<div class="vide"><b>' + esc(tr("js.pistes.vide")) + '</b>'
        + esc(tr("js.pistes.vide2")) + '</div>';
      var m = d.mesure, e = $("pistes-mesure");
      if (e && m && m.dit) e.textContent = m.dit;
    }).catch(function () { /* les pistes sont dérivées, pas le contenu */ });
  }

  /* Cliquer un dossier revient à chercher son terme : le dossier N'EST QUE
     cela, et le présenter autrement laisserait croire à un classement
     éditorial qui n'existe pas. */
  function chargerDossiers() {
    demander("/api/veille/dossiers").then(function (d) {
      if (!d.ok) return;
      var t = d.par_terme || [];
      $("c-dos").textContent = t.length + " " + tr("js.dossiers");
      $("dossiers").innerHTML = t.map(function (x) {
        return '<button type="button" class="dos" data-terme="' + esc(x.libelle)
          + '"><b>' + esc(x.libelle) + '</b><span class="n">' + x.n + '</span></button>';
      }).join("") || '<span class="dos-dit">' + esc(tr("js.dos.vide")) + '</span>';
      /* L'AXE PAR ENTITÉ DIT CE QU'IL A MESURÉ, MÊME QUAND IL NE FORME RIEN.
         Le taire laisserait croire que le site regroupe par fournisseur et
         qu'il n'y a rien à signaler — alors que c'est la matière des sources
         qui ne s'y prête pas. */
      var m = d.mesure_entites, e = $("dos-ent");
      if (e && m && m.dit) e.textContent = m.dit;
    }).catch(function () { /* les dossiers sont un confort, pas le contenu */ });
  }

  document.addEventListener("click", function (ev) {
    var b = ev.target && ev.target.closest ? ev.target.closest("[data-terme]") : null;
    if (!b) return;
    var q = $("f-q");
    if (q) { q.value = b.getAttribute("data-terme"); charger(); }
  });

  function chargerSources() {
    demander("/api/sources").then(function (d) {
      if (!d.ok) return;
      /* ADMISE N'EST PAS LUE, ET LA CARTE LE DIT.
         Le registre affichait neuf sources, chacune avec son bouton
         « Sonder » prouvant qu'elle répond — alors que cinq seulement
         nourrissent le corpus. Un lecteur en concluait que le site s'appuie
         sur neuf. L'état vient du serveur, dérivé de la table des
         collecteurs : il ne peut pas diverger de la réalité. */
      $("sources").innerHTML = (d.sources || []).map(function (s) {
        var lue = s.collectee === true, ind = s.collectee === null;
        return '<div class="src' + (lue || ind ? '' : ' src-dormante') + '">'
          + '<span class="na">' + esc(s.nature_nom) + '</span>'
          + '<span class="lue ' + (ind ? 'ind' : (lue ? 'oui' : 'non')) + '">'
          + (ind ? 'état indéterminé' : (lue ? 'lue par la collecte'
                                             : 'admise, pas encore lue')) + '</span>'
          + '<h3>' + esc(s.nom) + '</h3>'
          + '<p class="ed">' + esc(s.editeur) + '</p>'
          + '<p>' + esc(s.couvre) + '</p>'
          + '<p class="non"><b>Ne couvre pas.</b> ' + esc(s.ne_couvre_pas) + '</p>'
          + (!lue && s.pourquoi_pas_lue
              ? '<p class="non"><b>Pourquoi elle n\'alimente pas le corpus.</b> '
                + esc(s.pourquoi_pas_lue) + '</p>' : '')
          + '<p class="lic">' + esc(s.licence) + ' · mise à jour '
          + esc(s.cadence) + '</p>'
          + '<button type="button" class="sonde" data-sonde="' + esc(s.cle)
          + '">Sonder cette source</button>'
          + '<div class="resu" id="resu-' + esc(s.cle) + '"></div>'
          + '</div>';
      }).join("");
      rendreABrancher(d);
    }).catch(function () {
      $("sources").innerHTML = '<div class="vide">Le registre des sources '
        + 'n\'a pas pu être chargé.</div>';
    });
  }

  /* ── CE QUE CE SITE NE LIT PAS ENCORE, ET POURQUOI ──────────────────────
     LA LISTE EXISTAIT DANS L'INTERFACE DEPUIS LE PREMIER JOUR, ET PERSONNE NE
     LA VOYAIT : `/api/sources` servait `a_brancher`, aucune page ne l'affichait.
     Un registre qui dit ce qu'il lit sans dire ce qu'il ne lit pas enseigne au
     lecteur une couverture qu'il n'a pas — c'est le défaut même que la colonne
     « lue / non lue » avait corrigé pour les sources admises.

     ELLES SONT GROUPÉES PAR NATURE D'OBSTACLE, parce que « bloqué par la
     politique réseau de l'environnement de conception » et « licence
     commerciale requise » ne se règlent pas du tout pareil : le premier se
     règle en déployant, le second demande un contrat. Les afficher pêle-mêle
     laisserait croire qu'un développeur peut tout brancher. */
  function rendreABrancher(d) {
    var z = $("brancher");
    if (!z) return;
    var liste = d.a_brancher || [];
    var natures = d.obstacles || [];
    if (!liste.length) { z.innerHTML = ""; return; }
    var en = window.L && window.L.courante() === "en";
    var h = "";
    natures.forEach(function (n) {
      var siennes = liste.filter(function (x) {
        return x.nature_obstacle === n.cle;
      });
      if (!siennes.length) return;
      h += '<div class="brg"><p class="brg-t">' + esc(en && n.nom_en ? n.nom_en : n.nom)
        + '<i>' + siennes.length + '</i></p>'
        + '<p class="brg-d">' + esc(en && n.dit_en ? n.dit_en : n.dit) + '</p>';
      siennes.forEach(function (x) {
        h += '<div class="brs"><b>' + esc(x.nom) + '</b>'
          + '<p class="brs-p">' + esc(x.pourquoi) + '</p>'
          + '<p class="brs-o">' + esc(x.obstacle) + '</p>'
          + (x.ce_qu_il_faudrait
              ? '<p class="brs-f">' + esc(tr("br.faudrait")) + " "
                + esc(x.ce_qu_il_faudrait) + '</p>' : "")
          + '</div>';
      });
      h += "</div>";
    });
    z.innerHTML = h;
    var c = $("c-brancher");
    if (c) c.textContent = liste.length + " " + tr("br.sources");
  }

  /* Sonder : on va RÉELLEMENT chercher la source. C'est ce qui rend
     vérifiable la promesse « nos sources sont atteignables » — au lieu de la
     répéter. */
  document.addEventListener("click", function (ev) {
    var b = ev.target && ev.target.closest ? ev.target.closest("[data-sonde]") : null;
    if (!b) return;
    var cle = b.getAttribute("data-sonde");
    var z = $("resu-" + cle);
    if (z) { z.className = "resu"; z.textContent = "Interrogation…"; }
    demander("/api/sources/sonde/" + encodeURIComponent(cle))
      .then(function (r) {
        if (!z) return;
        z.className = "resu";
        z.textContent = "✓ " + r.code + " — " + Math.round(r.octets_lus / 1024)
          + " ko lus en " + r.ms + " ms";
      })
      .catch(function () {
        if (!z) return;
        z.className = "resu ko";
        z.textContent = "✗ " + tr("js.sonde.ko");
      });
  });

  function demarrer() {
    var d = new Date();
      /* LA DATE SE REDESSINE À LA BASCULE. Posée une seule fois au chargement,
     elle restait « 23 août 2026 » sur une interface anglaise — le genre de
     reste qui fait douter de tout le reste. */
  function dater() {
    var e = $("or-date");
    if (!e) return;
    e.textContent = (window.L && window.L.date)
      ? window.L.date(d.toISOString().slice(0, 10))
      : d.toISOString().slice(0, 10);
  }
  dater();
  document.addEventListener("langue", dater);

    FILTRES.forEach(function (f) {
      var el = $(f[1]);
      if (el) el.addEventListener("change", charger);
    });
    /* La recherche se déclenche à la frappe, mais PAS à chaque caractère :
       une requête par lettre ferait clignoter la page et taperait le serveur
       pour rien. */
    var qel = $("f-q"), minuteur = null;
    if (qel) qel.addEventListener("input", function () {
      clearTimeout(minuteur);
      minuteur = setTimeout(charger, 320);
    });
    var plier = $("f-plier"), champs = $("f-champs");
    if (plier && champs) {
      var ouvrirF = function (o) {
        champs.classList.toggle("f-ouvert", o);
        plier.setAttribute("aria-expanded", o ? "true" : "false");
      };
      plier.addEventListener("click", function () {
        ouvrirF(!champs.classList.contains("f-ouvert"));
      });
      ouvrirF(false);
      /* LE COMPTE SUIT CHAQUE CHANGEMENT, y compris ceux qui viennent de
         l'adresse partagée : sans cela, une vue ouverte sur deux filtres
         annoncerait « aucun » tant que le lecteur n'y touche pas. */
      FILTRES.forEach(function (f) {
        var el = $(f[1]);
        if (el) el.addEventListener("change", compterActifs);
      });
      document.addEventListener("langue", compterActifs);
    }

    var raz = $("f-raz");
    if (raz) raz.addEventListener("click", function () {
      FILTRES.forEach(function (f) { var el = $(f[1]); if (el) el.value = ""; });
      charger();
    });

    suivreLecture();
    window.addEventListener("pageshow", rafraichirEtats);
    document.addEventListener("visibilitychange", function () {
      if (!document.hidden) rafraichirEtats();
    });
    document.addEventListener("lecture-effacee", rafraichirEtats);

    chargerReferentiel();
    chargerFacettes().then(function () {
      lireAdresse(); compterActifs(); charger();
    });
    chargerSources();
    chargerDossiers();
    chargerPistes();

    /* LA BASCULE NE RECHARGE PAS LA PAGE — elle perdrait les filtres en
       cours, et un lecteur qui a construit sa vue ne doit pas la payer pour
       changer de langue. Les listes de filtres sont reconstruites (leurs
       libellés changent), et le fil est redemandé : `garde` dans `options()`
       préserve la valeur choisie. */
    document.addEventListener("langue", function () {
      direReserve();
      chargerFacettes().then(charger);
      chargerSources();
      chargerDossiers();
      chargerPistes();
    });
    /* CHANGER LA LANGUE DES ANALYSES NE RETRADUIT PAS L'INTERFACE : seul le
       fil est redemandé, avec les filtres en cours. Les menus, les dossiers
       et les pistes ne portent pas d'analyse — les recharger serait quatre
       requêtes pour rien. */
    document.addEventListener("analyses", function () {
      direReserve();
      charger();
    });
  }

  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", demarrer);
  else demarrer();
})();
