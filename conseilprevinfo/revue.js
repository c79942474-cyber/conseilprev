/* LA REVUE — deux découpes du même corpus, et rien d'écrit ici.
   ────────────────────────────────────────────────────────────
   CE FICHIER NE COMPOSE AUCUNE PHRASE D'APPRÉCIATION. Il rend ce que
   `/api/revue` sert : des fiches rangées par portée, des comptes, et les
   absences. Le jour où quelqu'un voudra ajouter « une semaine chargée » en
   tête, il faudra l'écrire ici — et ce commentaire est là pour qu'il sache
   qu'il franchit une règle plutôt qu'il n'améliore une page.

   L'ÉTAT DE LA PAGE TIENT EN TROIS VALEURS : le genre de période, l'ancre, et
   le fait de retenir ou non la règle internationale. Elles vivent dans
   l'adresse, ce qui rend la revue d'une semaine CITABLE — un lien vers « la
   semaine du 27 juillet » doit ouvrir cette semaine-là chez le destinataire,
   pas la sienne. */
(function () {
  "use strict";

  var DELAI = 20000;
  var ETAT = { genre: "semaine", ancre: null, international: false };
  var DEMANDE = 0;

  function tr(c) { return (window.L && window.L.t) ? window.L.t(c) : c; }
  function $(id) { return document.getElementById(id); }
  function esc(x) {
    return String(x == null ? "" : x).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function en() { return !!(window.L && window.L.courante() === "en"); }
  function frDate(iso) {
    if (window.L && window.L.date) return window.L.date(iso);
    return String(iso || "—");
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
        if (!r.ok) throw new Error("http");
        return r.json();
      }, function (e) { fini = true; clearTimeout(t); throw e; });
  }

  /* ── L'ADRESSE PORTE L'ÉTAT ─────────────────────────────────────────────
     ELLE EST ÉCRITE SANS RECHARGER (`replaceState`) : recharger perdrait la
     position de défilement au moment précis où le lecteur compare deux
     périodes. Et elle est RELUE au chargement, sans quoi un lien partagé
     ouvrirait la semaine du destinataire au lieu de celle qu'on lui
     envoie. */
  function lireAdresse() {
    var p;
    try { p = new URLSearchParams(location.search); } catch (e) { return; }
    if (p.get("genre") === "mois" || p.get("genre") === "semaine")
      ETAT.genre = p.get("genre");
    if (/^\d{4}-\d{2}-\d{2}$/.test(p.get("ancre") || "")) ETAT.ancre = p.get("ancre");
    ETAT.international = p.get("international") === "1";
  }

  function ecrireAdresse() {
    var q = ["genre=" + ETAT.genre];
    if (ETAT.ancre) q.push("ancre=" + ETAT.ancre);
    if (ETAT.international) q.push("international=1");
    try {
      history.replaceState(null, "", location.pathname + "?" + q.join("&"));
    } catch (e) { /* une adresse non réécrite n'empêche pas de lire */ }
  }

  function parametres() {
    var q = ["genre=" + encodeURIComponent(ETAT.genre)];
    if (ETAT.ancre) q.push("ancre=" + encodeURIComponent(ETAT.ancre));
    if (ETAT.international) q.push("international=1");
    if (window.L && window.L.analyses && window.L.analyses() === "en")
      q.push("analyses=en");
    return "?" + q.join("&");
  }

  /* ── LES DEUX ONGLETS ────────────────────────────────────────────────────
     CHANGER D'ONGLET REMET L'ANCRE À ZÉRO, et c'est voulu : la semaine la
     plus récente du corpus et le mois le plus récent DOCUMENTÉ SOUS LA RÈGLE
     INTERNATIONALE ne sont pas la même date. Garder l'ancre ferait ouvrir la
     revue mensuelle sur un mois vide, et le lecteur conclurait que la
     rubrique ne marche pas — alors qu'elle marche et ne trouve rien là. */
  function onglet(international) {
    ETAT.international = international;
    ETAT.genre = international ? "mois" : "semaine";
    ETAT.ancre = null;
    peindreOnglets();
    charger();
  }

  function peindreOnglets() {
    [["rv-hebdo", false], ["rv-mensuel", true]].forEach(function (x) {
      var b = $(x[0]);
      if (!b) return;
      b.setAttribute("aria-selected", ETAT.international === x[1] ? "true" : "false");
      b.classList.toggle("actif", ETAT.international === x[1]);
    });
  }

  function charger() {
    var mien = ++DEMANDE;
    var c = $("rv-corps");
    if (c) c.innerHTML = '<p class="bandeau-etat">' + esc(tr("rv.chargement")) + "</p>";
    demander("/api/revue" + parametres()).then(function (d) {
      /* SEULE LA RÉPONSE À LA DERNIÈRE DEMANDE ÉCRIT DANS LA PAGE. Deux clics
         rapides sur « période précédente » lançaient deux requêtes ; la plus
         lente écrasait la plus récente, et la page affichait une semaine que
         personne n'avait demandée. */
      if (mien !== DEMANDE) return;
      if (!d || !d.ok) throw new Error("api");
      rendre(d);
    }).catch(function () {
      if (mien !== DEMANDE) return;
      if (c) c.innerHTML = '<div class="vide"><b>' + esc(tr("rv.panne"))
        + "</b>" + esc(tr("rv.panne2")) + "</div>";
    });
  }

  var DERNIERE = null;

  function rendre(d) {
    DERNIERE = d;
    ETAT.ancre = d.periode.debut;
    ecrireAdresse();

    var per = $("rv-per");
    if (per) per.textContent = en() ? d.periode.libelle_en : d.periode.libelle;

    /* LE RETARD EST DIT, ET IL EST DIT EN DEUX NOMBRES. Le premier situe la
       période par rapport à aujourd'hui ; le second dit jusqu'où le CORPUS
       va. Sans le second, un lecteur qui ouvre une revue de juillet le
       24 août croit que la page est en retard, alors que c'est le corpus qui
       s'arrête là — et c'est une information sur les sources, pas sur la
       revue. */
    var r = $("rv-retard");
    if (r) {
      var t = d.retard || {};
      if (d.corpus_vide) {
        /* LE CORPUS VIDE N'EST PAS UNE PÉRIODE VIDE. Dire « aucun fait daté
           de cette période n'est entré au corpus » quand RIEN n'est encore
           entré au corpus ferait porter au silence des sources ce qui n'est
           qu'un serveur en cours de collecte. */
        r.hidden = false;
        r.className = "bandeau-etat alerte grave";
        r.innerHTML = "<b>" + esc(tr("rv.nocorpus")) + "</b> "
          + esc(tr("rv.nocorpus.t"));
      } else if (t.jours_depuis_la_fin > 6) {
        r.hidden = false;
        r.className = "bandeau-etat alerte";
        /* LA PHRASE « c'est la plus récente que le corpus documente » NE SE
           DIT QUE SI ELLE EST VRAIE. Constaté au navigateur : elle restait
           affichée après un clic sur « période précédente », au-dessus d'une
           semaine vide qui n'était évidemment pas la plus récente. */
        r.innerHTML = "<b>" + esc(tr("rv.retard")) + "</b> "
          + esc(tr(t.est_la_plus_recente ? "rv.retard.t" : "rv.retard.ancienne")
                  .replace("%j", t.jours_depuis_la_fin))
          + (t.dernier_fait
              ? " " + esc(tr("rv.retard.dernier")) + " " + esc(frDate(t.dernier_fait)) + "."
              : "");
      } else { r.hidden = true; }
    }

    /* LA RÈGLE DE SÉLECTION EST SERVIE AVEC LA SÉLECTION. Une sélection dont
       on ignore le critère ne se discute pas : elle se croit. */
    var g = $("rv-regle");
    if (g) {
      if (d.international && d.regle_internationale) {
        g.hidden = false;
        g.innerHTML = "<b>" + esc(tr("rv.regle")) + "</b> "
          + esc(d.regle_internationale);
      } else { g.hidden = true; }
    }

    var h = "";
    h += sommaire(d);
    if (!d.n) {
      h += '<div class="vide"><b>' + esc(tr("rv.vide")) + "</b>"
        + esc(tr("rv.vide2")) + "</div>";
    } else {
      d.blocs.forEach(function (b) {
        h += '<h2 class="rubrique rv-bloc"><span>' + esc(b.nom) + "</span>"
          + '<span class="rv-n">' + b.n + " " + esc(tr("rv.fiches")) + "</span></h2>";
        h += '<div class="grille">';
        b.fiches.forEach(function (f) { h += carte(f); });
        h += "</div>";
      });
    }
    h += absences(d);
    $("rv-corps").innerHTML = h;

    /* L'ÉTAT DE LECTURE EST POSÉ APRÈS LE RENDU, comme sur le fil : les
       cartes de la revue mènent aux mêmes fiches, et un lecteur qui a lu
       « CVE-2021-22681 » hier doit le voir ici aussi. */
    etats();
    $("rv-rubriques").innerHTML = (d.rubriques || []).map(rubrique).join("");
  }

  function sommaire(d) {
    var h = '<div class="rv-som">';
    h += '<span class="rv-som-n"><b>' + d.n + "</b> " + esc(tr("rv.fiches")) + "</span>";
    /* L'ÉCART AVEC LA PÉRIODE PRÉCÉDENTE EST UN NOMBRE, PAS UNE TENDANCE.
       « En hausse » sur deux points serait une affirmation que rien ne
       fonde. */
    if (d.precedente) {
      var e = d.precedente.ecart;
      h += '<span class="rv-som-e">' + esc(tr("rv.precedente")) + " "
        + '<b>' + d.precedente.n + "</b> "
        + "(" + (e > 0 ? "+" : "") + e + ")</span>";
    }
    (d.par_sujet || []).forEach(function (s) {
      h += '<span class="past sujet">' + esc(s.nom) + " (" + s.n + ")</span>";
    });
    (d.par_source || []).forEach(function (s) {
      h += '<span class="rv-src">' + esc(s.nom) + " (" + s.n + ")</span>";
    });
    return h + "</div>";
  }

  /* ── CE QUE LA PÉRIODE NE DIT PAS ────────────────────────────────────────
     UNE REVUE QUI N'AFFICHE QUE SES RUBRIQUES FÉCONDES enseigne au lecteur
     une couverture qu'elle n'a pas. Les sujets muets sont nommés ; les fiches
     écartées sont comptées, avec le motif de leur écart. Taire les écarts
     ferait disparaître des fiches réelles du corpus, sans un mot. */
  function absences(d) {
    var l = [];
    if ((d.muets || []).length) {
      l.push("<b>" + esc(tr("rv.muets")) + "</b> "
        + d.muets.map(function (m) { return esc(m.nom); }).join(" · "));
    }
    if (d.conventions_ecartees) {
      l.push("<b>" + esc(tr("rv.conv")) + "</b> "
        + esc(tr("rv.conv.t").replace("%n", d.conventions_ecartees)));
    }
    if (d.ecartees_sans_territoire) {
      l.push("<b>" + esc(tr("rv.hors")) + "</b> "
        + esc(tr("rv.hors.t").replace("%n", d.ecartees_sans_territoire)));
    }
    if (d.ecartees_france) {
      l.push("<b>" + esc(tr("rv.fr")) + "</b> "
        + esc(tr("rv.fr.t").replace("%n", d.ecartees_france)));
    }
    if (!l.length) return "";
    return '<div class="rv-abs"><p class="rv-abs-t">'
      + esc(tr("rv.absences")) + "</p><p>" + l.join("</p><p>") + "</p></div>";
  }

  function carte(f) {
    var etat = (window.LU ? window.LU.classe(f.id) : "");
    var h = '<article class="fiche ' + etat + '" data-fid="' + esc(f.id) + '">';
    /* LA PASTILLE PORTE LE SUJET, ET DONC LA CLASSE DU SUJET.
       DÉFAUT VU À L'ÉCRAN : elle affichait le nom du SUJET dans la couleur de
       la PORTÉE — « Cybersécurité industrielle » peint en ambre parce que la
       fiche est structurante. Le code de couleur que la légende enseigne
       s'en trouvait démenti sur chaque carte de cette page. La portée, elle,
       est déjà donnée par l'intertitre qui coiffe le bloc : la répéter sur
       chaque carte n'apprendrait rien. */
    h += '<div class="fmeta">'
      + '<span class="past sujet">' + esc(f.sujet_nom || f.sujet) + "</span>"
      + '<span class="fdate">' + esc(frDate(f.date_fait)) + "</span>"
      + (etat === "lu" ? '<span class="fmarque">' + esc(tr("lc.marque"))
                         + "</span>" : "")
      + "</div>";
    h += '<h3 class="ftitre"><a class="nu" href="/fiche/' + esc(f.id) + '">'
      + esc(f.titre) + "</a></h3>";
    if (f.chapeau) h += '<p class="fchapeau">' + esc(f.chapeau) + "</p>";
    /* LES ENTREPRISES NOMMÉES SONT SUR LA CARTE DE LA REVUE, ET PAS SUR CELLE
       DU FIL. Le fil sert quatre-vingt-dix-huit cartes dont seize en portent :
       elles y seraient du bruit. La revue mensuelle, elle, est SÉLECTIONNÉE
       sur un critère de territoire — le lecteur doit voir ce qui a valu à
       chaque entrée d'y figurer. */
    if ((f.organisations || []).length || (f.pays || []).length) {
      h += '<p class="rv-terr">'
        + (f.organisations || []).map(function (o) {
            return '<span class="orga">' + esc(o) + "</span>"; }).join("")
        + (f.pays || []).map(function (p) {
            return '<span class="orga">' + esc(p) + "</span>"; }).join("")
        + "</p>";
    }
    h += '<div class="fsource"><span class="st">● ' + esc(f.statut_nom || "")
      + "</span>" + esc(f.source_nom || "") + "</div>";
    return h + "</article>";
  }

  /* ── UNE RUBRIQUE SIGNÉE — ou son absence, écrite ────────────────────── */
  function rubrique(r) {
    /* LA CLASSE S'APPELLE `rv-vide` ET NON `vide`. Constatée à l'écran : la
       feuille porte déjà un bloc `.vide` — un cadre en pointillés, texte
       CENTRÉ — pour les listes sans résultat. La rubrique vide en héritait et
       s'affichait centrée au milieu d'une page qui ne l'est nulle part. Un
       nom de classe emprunté finit toujours par emprunter aussi le style. */
    var h = '<div class="rv-rub' + (r.n ? "" : " rv-vide") + '">';
    h += '<h3>' + esc(r.nom) + "</h3>";
    h += '<p class="rv-rub-d">' + esc(r.dit) + "</p>";
    if (!r.n) {
      h += '<p class="rv-rub-v"><b>' + esc(r.vide_motif) + "</b> "
        + esc(r.ce_qu_il_faudrait) + "</p>";
      return h + "</div>";
    }
    r.pieces.forEach(function (p) {
      h += '<article class="rv-piece"><h4>' + esc(p.titre) + "</h4>"
        + '<p class="fchapeau">' + esc(p.chapeau) + "</p>"
        + '<div class="rv-sign"><b>' + esc(p.auteur) + "</b> · "
        + esc(frDate(p.date))
        + (p.interlocuteur ? " · " + esc(p.interlocuteur)
                             + (p.fonction ? ", " + esc(p.fonction) : "") : "")
        + '<span>' + esc(p.methode) + "</span></div></article>";
    });
    return h + "</div>";
  }

  function etats() {
    if (!window.LU) return;
    Array.prototype.forEach.call(document.querySelectorAll(".fiche[data-fid]"),
      function (c) {
        var e = window.LU.classe(c.getAttribute("data-fid"));
        c.classList.toggle("lu", e === "lu");
        c.classList.toggle("neuf", e === "neuf");
      });
  }

  function decaler(sens) {
    /* LE DÉCALAGE EST FAIT SUR LES BORNES SERVIES, jamais « moins sept
       jours » : un mois n'en fait pas trente, et février encore moins. La
       veille du début d'une période est toujours dans la précédente. */
    if (!DERNIERE) return;
    var d = new Date((sens < 0 ? DERNIERE.periode.debut : DERNIERE.periode.fin)
                     + "T12:00:00Z");
    d.setUTCDate(d.getUTCDate() + (sens < 0 ? -1 : 1));
    ETAT.ancre = d.toISOString().slice(0, 10);
    charger();
  }

  function demarrer() {
    lireAdresse();
    peindreOnglets();
    var b;
    if ((b = $("rv-hebdo"))) b.addEventListener("click", function () { onglet(false); });
    if ((b = $("rv-mensuel"))) b.addEventListener("click", function () { onglet(true); });
    if ((b = $("rv-prec"))) b.addEventListener("click", function () { decaler(-1); });
    if ((b = $("rv-suiv"))) b.addEventListener("click", function () { decaler(1); });
    if ((b = $("rv-dernier"))) b.addEventListener("click", function () {
      ETAT.ancre = null; charger();
    });
    /* LA BASCULE NE RECHARGE PAS LA PAGE : les intitulés viennent du serveur
       comme les fiches, et la période en cours doit survivre au changement de
       langue — sans quoi comparer deux traductions ferait perdre sa place. */
    document.addEventListener("langue", charger);
    document.addEventListener("analyses", charger);
    document.addEventListener("lecture-effacee", etats);
    window.addEventListener("pageshow", etats);
    charger();
  }

  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", demarrer);
  else demarrer();
})();
