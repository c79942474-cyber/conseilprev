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
  function nommer(genre, cle, defaut) {
    var e = NOMS[genre] && NOMS[genre][cle];
    if (!e) return defaut || cle || "";
    return (window.L && window.L.courante() === "en" && e.en) ? e.en : e.fr;
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
  function fiche(f) {
    var h = '<article class="fiche">';
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
      + '" style="color:inherit;text-decoration:none">' + esc(f.titre)
      + '</a></h3>';
    if (f.chapeau) h += '<p class="fchapeau">' + esc(f.chapeau) + '</p>';

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

  function parametres() {
    var q = [];
    FILTRES.forEach(function (p) {
      var v = ($(p[1]) || {}).value;
      if (v) q.push(p[0] + "=" + encodeURIComponent(v));
    });
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
      history.replaceState(null, "", parametres() || location.pathname);
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

  function rendreEtat(d) {
    var e = $("etat");
    if (!e) return;
    var et = d.etat || {};
    var mauvaises = (et.journal || []).filter(function (j) { return !j.ok; });
    var quand = et.collecte_le ? frDate(et.collecte_le) : "—";
    var h = "<b>" + esc(tr("js.corpus")) + (et.fiches || 0) + " "
      + esc(tr("js.fiches")) + "</b>" + esc(tr("js.collectees")) + esc(quand) + ".";
    if (mauvaises.length) {
      h += " <b>" + mauvaises.length + " " + esc(tr("js.muettes")) + "</b> "
        + mauvaises.map(function (j) {
            return esc(j.source) + " — " + esc(j.message || j.erreur || "");
          }).join(" ; ")
        + esc(tr("js.muettes.fin"));
      e.className = "bandeau-etat alerte";
    } else {
      e.className = "bandeau-etat";
      h += " " + esc(tr("js.toutes.ok"));
    }
    e.innerHTML = h;
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
      rendreEtat(d);
      var toutes = d.fiches || [];
      /* LA UNE : ce qui rompt, et rien d'autre. Une « une » qui reprendrait
         les premières fiches du fil ne serait qu'un doublon de mise en page. */
      var une = toutes.filter(function (f) { return f.impact === "rupture"; });
      var fil = toutes.filter(function (f) { return f.impact !== "rupture"; });

      $("une").innerHTML = une.length
        ? une.map(fiche).join("")
        : '<div class="vide"><b>' + esc(tr("js.une.rien")) + '</b>'
          + esc(tr("js.une.vide")) + ' ' + esc(tr("js.une.vide2")) + '</div>';
      $("c-une").textContent = une.length + " " + tr("js.fiches");

      $("fil").innerHTML = fil.length
        ? fil.map(fiche).join("")
        : '<div class="vide"><b>' + esc(tr("js.fil.vide")) + '</b>'
          + esc(tr("js.fil.vide2")) + '</div>';
      $("c-fil").textContent = fil.length + " " + tr("js.fiches");

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
    }).catch(function () {
      $("sources").innerHTML = '<div class="vide">Le registre des sources '
        + 'n\'a pas pu être chargé.</div>';
    });
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
    var raz = $("f-raz");
    if (raz) raz.addEventListener("click", function () {
      FILTRES.forEach(function (f) { var el = $(f[1]); if (el) el.value = ""; });
      charger();
    });

    chargerReferentiel();
    chargerFacettes().then(function () { lireAdresse(); charger(); });
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
  }

  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", demarrer);
  else demarrer();
})();
