/* La page d'une fiche. Elle rend le CROISEMENT, pas des « articles
   similaires » : chaque voisine porte le motif de son rapprochement. */
(function () {
  "use strict";
  function esc(x) {
    return String(x == null ? "" : x).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function tr(c) { return (window.L && window.L.t) ? window.L.t(c) : c; }

  /* LES LIBELLÉS DU RÉFÉRENTIEL, DANS LA LANGUE COURANTE — même mécanique que
     le fil : le serveur sert le français sur la fiche, la table dit les deux. */
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

  var MOIS = ["janvier","février","mars","avril","mai","juin","juillet",
              "août","septembre","octobre","novembre","décembre"];
  /* La date suit la langue : `langue.js` la formate pour les quatre pages. */
  function frDate(iso) {
    if (window.L && window.L.date) return window.L.date(iso);
    if (!iso) return "—";
    var p = String(iso).slice(0,10).split("-");
    return p.length === 3 ? Number(p[2]) + " " + MOIS[Number(p[1])-1] + " " + p[0]
                          : String(iso);
  }
  var ident = decodeURIComponent(location.pathname.replace(/^\/fiche\//, ""));
  var d = new Date();
  /* LA DATE SE REDESSINE À LA BASCULE. Posée une seule fois au chargement,
     elle restait « 23 août 2026 » sur une interface anglaise — le genre de
     reste qui fait douter de tout le reste. */
  function dater() {
    var e = document.getElementById("or-date");
    if (!e) return;
    e.textContent = (window.L && window.L.date)
      ? window.L.date(d.toISOString().slice(0, 10))
      : d.getDate() + " " + MOIS[d.getMonth()] + " " + d.getFullYear();
  }
  dater();
  document.addEventListener("langue", dater);

  /* LE RÉFÉRENTIEL EST LU EN PARALLÈLE de la fiche : sans lui, `nommer()`
     retombe sur le libellé français servi avec la fiche, et une page anglaise
     s'ouvre avec des pastilles françaises. */
  var DERNIERE = null;
  fetch("/api/veille/referentiel", {credentials:"same-origin"})
    .then(function (r) { return r.json(); })
    .then(function (d) {
      if (!d || !d.ok) return;
      ranger("sujet", d.sujets); ranger("impact", d.impacts);
      ranger("statut", d.statuts); ranger("lecture", d.lectures);
      if (DERNIERE) rendre(DERNIERE);
    })
    .catch(function () { /* les libellés servis avec la fiche font foi */ });

  /* Une bascule redessine la fiche depuis la réponse déjà reçue : la
     redemander au serveur pour changer trois intitulés serait la payer deux
     fois. */
  document.addEventListener("langue", function () {
    if (DERNIERE) rendre(DERNIERE);
  });

  fetch("/api/veille/fiche/" + encodeURIComponent(ident), {credentials:"same-origin"})
    .then(function (r) { if (!r.ok) throw new Error("404"); return r.json(); })
    .then(function (j) { DERNIERE = j; rendre(j); })
    .catch(function () {
      document.getElementById("page").innerHTML =
        '<div class="vide"><b>' + esc(tr("fi.absente")) + '</b>'
        + esc(tr("fi.absente2")) + ' <a href="/">' + esc(tr("fi.retour")) + '</a></div>';
    });

  /* LE RENDU EST UNE FONCTION, pas un corps de promesse : la bascule de
     langue le rejoue sur la réponse déjà reçue. La redemander au serveur pour
     changer trois intitulés la ferait payer deux fois. */
  function rendre(j) {
      var f = j.fiche, s = f.source || {};
      document.title = f.titre + " — CONSEILPREV INFO";
      var h = '<div class="fmeta" style="margin-bottom:14px">'
        + '<span class="past ' + esc(f.impact) + '">'
        + esc(nommer("impact", f.impact, f.impact_nom)) + '</span>'
        + '<span class="past sujet">'
        + esc(nommer("sujet", f.sujet, f.sujet_nom)) + '</span>'
        + '<span class="fdate">' + esc(frDate(f.date_fait))
        + (f.date_convention ? ' <b class="conv">convention</b>' : "")
        + '</span></div>';
      h += '<h1 class="titre-journal" style="font-size:clamp(26px,3.6vw,40px);'
        + 'line-height:1.1;margin:0 0 12px">' + esc(f.titre) + '</h1>';
      h += '<p class="devise" style="font-size:16px">' + esc(f.chapeau) + '</p>';

      /* UNE DATE FABRIQUÉE LE DIT SOUS ELLE-MÊME. Elle est écrite en toutes
         lettres dans l'incertitude, mais l'incertitude se lit APRÈS la
         lecture critique — trop tard pour un lecteur qui a déjà pris la date
         pour un constat. La réserve va donc là où la date est lue. */
      if (f.date_convention) {
        h += '<p class="conv-dit"><b>Cette date n\'est pas une observation.</b> '
          + esc(f.date_convention_dit || "") + ' ' + esc(f.horizon_dit || "")
          + '</p>';
      }

      h += '<div class="fbloc lecture" style="margin-top:22px"><span class="fbloc-t">'
        + esc(tr("js.lecture")) + esc(nommer("lecture", f.lecture_nature, f.lecture_nom))
        + '</span><p>' + esc(f.lecture) + '</p></div>';
      h += '<div class="fbloc portee"><span class="fbloc-t">' + esc(tr("js.change")) + '</span>'
        + '<p>' + esc(f.portee) + '</p></div>';
      h += '<div class="fbloc doute"><span class="fbloc-t">' + esc(tr("js.doute")) + '</span>'
        + '<p>' + esc(f.incertitude) + '</p></div>';

      h += '<div class="src" style="margin-top:24px">'
        + '<span class="na">' + esc(s.nature_nom || "") + ' · '
        + esc(nommer("statut", f.statut, f.statut_nom)) + '</span>'
        + '<h3>' + esc(s.nom || "") + '</h3>'
        + '<p class="ed">' + esc(s.editeur || "") + '</p>'
        + '<p>' + esc(f.statut_dit || "") + '</p>'
        + '<p>' + esc(f.lecture_dit || "") + '</p>'
        + (s.url ? '<p><a href="' + esc(s.url) + '" target="_blank" rel="noopener">'
                   + 'Consulter la source →</a></p>' : "")
        + '<p class="lic">' + esc(s.licence || "") + '</p></div>';

      /* UNE VIGNETTE, DEUX EMPLOIS — mais jamais le même mot. Le bloc dit
         « Lien » quand une règle rattache vraiment les deux fiches, et
         « Rapprochement » quand il n'y a qu'une date en commun. */
      function vignette(l, mot) {
        return '<article class="fiche"><div class="fmeta">'
          + '<span class="past ' + esc(l.impact) + '">'
          + esc(nommer("impact", l.impact, l.impact_nom)) + '</span>'
          + '<span class="fdate">' + esc(frDate(l.date_fait)) + '</span></div>'
          + '<h3 class="ftitre" style="font-size:17px"><a href="/fiche/'
          + esc(l.id) + '" style="color:inherit;text-decoration:none">'
          + esc(l.titre) + '</a></h3>'
          + '<div class="fbloc"><span class="fbloc-t">' + mot + ' — '
          + esc((window.L && window.L.courante() === "en" && l.lien_nom_en)
                ? l.lien_nom_en : l.lien_nom)
          + '</span><p>' + esc(l.pourquoi) + '</p>'
          /* LES RÉFÉRENCES SUR LESQUELLES LA SOURCE S'APPUIE. Reprendre son
             affirmation sans elles obligerait à nous croire sur parole —
             exactement ce que ce site reproche aux agrégateurs. */
          + ((l.citations || []).length
              ? '<p class="cit"><b>Le référentiel s\'appuie sur :</b> '
                + l.citations.map(esc).join(' · ') + '</p>'
              : '')
          + '</div></article>';
      }

      var liens = j.liens || [];
      h += '<h2 class="rubrique">' + esc(tr("fi.croisement"))
        + '<span>' + liens.length + ' ' + esc(tr("fi.liens")) + '</span></h2>';
      if (!liens.length) {
        var co = j.composition || {};
        /* L'ÉTAT D'ENSEMBLE, PAS SEULEMENT CELUI DE CETTE FICHE. Lu seul,
           « aucun lien » passe pour une particularité ; répété sur tout le
           corpus sans un mot, il passe pour une panne. Il n'est ni l'un ni
           l'autre : c'est ce que les sources actuelles permettent. */
        h += '<div class="vide"><b>' + esc(tr("fi.aucun")) + '</b>'
          + esc(tr("fi.aucun2"))
          + (co.fiches_sans_lien_fort === co.fiches && co.fiches
              ? ' <b>' + esc(tr("fi.aucun.b")) + '</b> '
                + esc(tr("fi.aucun3")).replace("{n}", co.fiches)
              : '')
          + '</div>';
      } else {
        h += '<div class="grille">'
          + liens.map(function (l) { return vignette(l, tr("fi.lien")); }).join("")
          + '</div>';
      }

      /* LE VOISINAGE DE DATE, SOUS SON VRAI NOM ET APRÈS LES LIENS.
         Présenté avec eux, il les noyait : il est de loin le plus abondant,
         et c'est lui qui aurait donné le ton — le lecteur aurait appris que
         « croisement » veut dire « paru la même semaine ». */
      var vois = j.voisinage || [];
      if (vois.length) {
        h += '<h2 class="rubrique">' + esc(tr("fi.voisinage"))
          + '<span>' + vois.length
          + (j.voisinage_total > vois.length
              ? ' ' + esc(tr("fi.sur")) + ' ' + j.voisinage_total : '')
          + '</span></h2>';
        h += '<p class="dos-dit">' + esc(j.voisinage_dit || "") + '</p>';
        h += '<div class="grille">'
          + vois.map(function (l) { return vignette(l, tr("fi.rapproch")); }).join("")
          + '</div>';
      }
      h += '<p style="margin-top:26px"><a href="/">' + esc(tr("fi.retour"))
        + '</a></p>';
      document.getElementById("page").innerHTML = h;
  }
})();
