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
  function frDate(iso) {
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
      + '<span class="past ' + esc(f.impact) + '">' + esc(f.impact_nom) + '</span>'
      + '<span class="past sujet">' + esc(f.sujet_nom) + '</span>'
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

    h += '<div class="fbloc lecture"><span class="fbloc-t">Lecture — '
      + esc(f.lecture_nom) + '</span><p>' + esc(f.lecture) + '</p></div>';
    h += '<div class="fbloc portee"><span class="fbloc-t">Ce que cela change</span>'
      + '<p>' + esc(f.portee) + '</p></div>';
    h += '<div class="fbloc doute"><span class="fbloc-t">Ce qu\'on ne sait pas</span>'
      + '<p>' + esc(f.incertitude) + '</p></div>';

    var s = f.source || {};
    var faible = f.statut !== "verifiee_source_primaire";
    h += '<div class="fsource">'
      + '<span class="st' + (faible ? " faible" : "") + '">● '
      + esc(f.statut_nom) + '</span>'
      + esc(s.nom || "") + ' — ' + esc(s.editeur || "")
      + (s.url ? ' · <a href="' + esc(s.url) + '" target="_blank" rel="noopener">'
                 + 'consulter la source</a>' : "")
      + (s.licence ? '<br>' + esc(s.licence) : "")
      + '</div></article>';
    return h;
  }

  function options(sel, liste, valeur, libelle, compte) {
    var el = $(sel);
    if (!el) return;
    var garde = el.value;
    var h = el.options.length ? el.options[0].outerHTML : "";
    (liste || []).forEach(function (x) {
      h += '<option value="' + esc(x[valeur]) + '">' + esc(x[libelle])
        + (compte && x.n != null ? " (" + x.n + ")" : "") + "</option>";
    });
    el.innerHTML = h;
    if (garde) el.value = garde;
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
    var h = "<b>Corpus : " + (et.fiches || 0) + " fiche(s)</b>, collectées le "
      + esc(quand) + ".";
    if (mauvaises.length) {
      h += " <b>" + mauvaises.length + " source(s) n'ont pas répondu :</b> "
        + mauvaises.map(function (j) {
            return esc(j.source) + " — " + esc(j.message || j.erreur || "");
          }).join(" ; ")
        + ". Les fiches affichées viennent des sources qui ont répondu ; "
        + "aucune n'est complétée d'estimation.";
      e.className = "bandeau-etat alerte";
    } else {
      e.className = "bandeau-etat";
      h += " Toutes les sources interrogées ont répondu.";
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
        : '<div class="vide"><b>Rien ne rompt aujourd\'hui.</b>'
          + 'Aucune fiche du corpus filtré n\'est classée « rupture ». '
          + 'C\'est une information, pas un manque — et c\'est pourquoi cette '
          + 'zone ne se remplit pas des fiches suivantes.</div>';
      $("c-une").textContent = une.length + " fiche(s)";

      $("fil").innerHTML = fil.length
        ? fil.map(fiche).join("")
        : '<div class="vide"><b>Aucune fiche pour ces filtres.</b>'
          + 'Élargissez la sélection — le corpus ne contient peut-être rien '
          + 'sur ce croisement, et le site ne comble pas ce vide.</div>';
      $("c-fil").textContent = fil.length + " fiche(s)";

      /* LA COUPE EST ANNONCÉE, jamais laissée à la soustraction du lecteur.
         Le serveur dit lui-même s'il a coupé : le client ne le déduit pas de
         deux nombres, sans quoi la règle vivrait à deux endroits et l'un des
         deux finirait faux. */
      $("f-compte").innerHTML = "<b>" + d.total + "</b> fiche(s) retenues"
        + (d.tronque ? ", <b>" + d.affichees + "</b> affichées" : "");
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
        ? "Le serveur n'a pas répondu en " + Math.round(DELAI / 1000)
          + " secondes. La veille n'est pas perdue : rechargez dans un instant."
        : "La veille n'a pas pu être chargée. Rechargez la page.";
      $("etat").className = "bandeau-etat alerte";
      $("etat").textContent = msg;
    });
  }

  function chargerFacettes() {
    return demander("/api/veille/facettes").then(function (d) {
      if (!d.ok) return;
      FACETTES = d;
      options("f-sujet", d.sujets, "cle", "nom", true);
      options("f-pays", d.pays, "cle", "cle", true);
      options("f-techno", d.technologies, "cle", "cle", true);
      options("f-impact", d.impacts, "cle", "nom", true);
      options("f-horizon", d.horizons, "cle", "nom", true);
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
      $("c-pistes").textContent = ps.length + " piste(s)";
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
              ? ' <i>(+' + p.fiches_non_listees + ' non listée(s))</i>' : '')
          + '</p></article>';
      }).join("") || '<div class="vide"><b>Aucune piste aujourd\'hui.</b>'
        + 'Aucun déclencheur ne trouve dans le corpus de quoi en former une. '
        + 'Proposer quand même serait proposer sans matière.</div>';
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
      $("c-dos").textContent = t.length + " dossier(s)";
      $("dossiers").innerHTML = t.map(function (x) {
        return '<button type="button" class="dos" data-terme="' + esc(x.libelle)
          + '"><b>' + esc(x.libelle) + '</b><span class="n">' + x.n + '</span></button>';
      }).join("") || '<span class="dos-dit">Aucun terme ne revient sur assez '
        + 'de fiches pour former un dossier.</span>';
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
        z.textContent = "✗ injoignable depuis ce serveur — l'état est dit, "
          + "pas masqué";
      });
  });

  function demarrer() {
    var d = new Date();
    $("or-date").textContent = d.getDate() + " " + MOIS[d.getMonth()] + " "
      + d.getFullYear();

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

    chargerFacettes().then(function () { lireAdresse(); charger(); });
    chargerSources();
    chargerDossiers();
    chargerPistes();
  }

  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", demarrer);
  else demarrer();
})();
