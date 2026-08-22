/* La page d'une fiche. Elle rend le CROISEMENT, pas des « articles
   similaires » : chaque voisine porte le motif de son rapprochement. */
(function () {
  "use strict";
  function esc(x) {
    return String(x == null ? "" : x).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  var MOIS = ["janvier","février","mars","avril","mai","juin","juillet",
              "août","septembre","octobre","novembre","décembre"];
  function frDate(iso) {
    if (!iso) return "—";
    var p = String(iso).slice(0,10).split("-");
    return p.length === 3 ? Number(p[2]) + " " + MOIS[Number(p[1])-1] + " " + p[0]
                          : String(iso);
  }
  var ident = decodeURIComponent(location.pathname.replace(/^\/fiche\//, ""));
  var d = new Date();
  document.getElementById("or-date").textContent =
    d.getDate() + " " + MOIS[d.getMonth()] + " " + d.getFullYear();

  fetch("/api/veille/fiche/" + encodeURIComponent(ident), {credentials:"same-origin"})
    .then(function (r) { if (!r.ok) throw new Error("404"); return r.json(); })
    .then(function (j) {
      var f = j.fiche, s = f.source || {};
      document.title = f.titre + " — CONSEILPREV INFO";
      var h = '<div class="fmeta" style="margin-bottom:14px">'
        + '<span class="past ' + esc(f.impact) + '">' + esc(f.impact_nom) + '</span>'
        + '<span class="past sujet">' + esc(f.sujet_nom) + '</span>'
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
        + 'Lecture — ' + esc(f.lecture_nom) + '</span><p>' + esc(f.lecture) + '</p></div>';
      h += '<div class="fbloc portee"><span class="fbloc-t">Ce que cela change</span>'
        + '<p>' + esc(f.portee) + '</p></div>';
      h += '<div class="fbloc doute"><span class="fbloc-t">Ce qu\'on ne sait pas</span>'
        + '<p>' + esc(f.incertitude) + '</p></div>';

      h += '<div class="src" style="margin-top:24px">'
        + '<span class="na">' + esc(s.nature_nom || "") + ' · ' + esc(f.statut_nom) + '</span>'
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
          + '<span class="past ' + esc(l.impact) + '">' + esc(l.impact_nom) + '</span>'
          + '<span class="fdate">' + esc(frDate(l.date_fait)) + '</span></div>'
          + '<h3 class="ftitre" style="font-size:17px"><a href="/fiche/'
          + esc(l.id) + '" style="color:inherit;text-decoration:none">'
          + esc(l.titre) + '</a></h3>'
          + '<div class="fbloc"><span class="fbloc-t">' + mot + ' — '
          + esc(l.lien_nom) + '</span><p>' + esc(l.pourquoi) + '</p>'
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
      h += '<h2 class="rubrique">Croisement — ce qui porte sur la même décision'
        + '<span>' + liens.length + ' lien(s)</span></h2>';
      if (!liens.length) {
        var co = j.composition || {};
        /* L'ÉTAT D'ENSEMBLE, PAS SEULEMENT CELUI DE CETTE FICHE. Lu seul,
           « aucun lien » passe pour une particularité ; répété sur tout le
           corpus sans un mot, il passe pour une panne. Il n'est ni l'un ni
           l'autre : c'est ce que les sources actuelles permettent. */
        h += '<div class="vide"><b>Aucun lien établi.</b>Le corpus ne porte '
          + 'aujourd\'hui aucune autre fiche rattachable à celle-ci par une '
          + 'règle écrite — ni le même fournisseur, ni le même territoire, ni '
          + 'une technologie commune. Rapprocher sans motif serait pire que '
          + 'de ne rien proposer.'
          + (co.fiches_sans_lien_fort === co.fiches && co.fiches
              ? ' <b>Et ce n\'est pas propre à cette fiche :</b> aucune des '
                + co.fiches + ' fiches du corpus n\'a de lien fort '
                + 'aujourd\'hui. Les sources branchées ne se recouvrent pas '
                + 'encore — un catalogue de vulnérabilités nomme un produit '
                + 'par entrée, un référentiel de modes opératoires n\'en '
                + 'nomme aucun. La rubrique n\'est pas en panne : elle est '
                + 'vide, et elle le dit.'
              : '')
          + '</div>';
      } else {
        h += '<div class="grille">'
          + liens.map(function (l) { return vignette(l, "Lien"); }).join("")
          + '</div>';
      }

      /* LE VOISINAGE DE DATE, SOUS SON VRAI NOM ET APRÈS LES LIENS.
         Présenté avec eux, il les noyait : il est de loin le plus abondant,
         et c'est lui qui aurait donné le ton — le lecteur aurait appris que
         « croisement » veut dire « paru la même semaine ». */
      var vois = j.voisinage || [];
      if (vois.length) {
        h += '<h2 class="rubrique">Autour de la même date — <i>ce n\'est pas '
          + 'un lien</i><span>' + vois.length
          + (j.voisinage_total > vois.length ? ' sur ' + j.voisinage_total : '')
          + '</span></h2>';
        h += '<p class="dos-dit">' + esc(j.voisinage_dit || "") + '</p>';
        h += '<div class="grille">'
          + vois.map(function (l) { return vignette(l, "Rapprochement"); }).join("")
          + '</div>';
      }
      h += '<p style="margin-top:26px"><a href="/">← Retour au fil</a></p>';
      document.getElementById("page").innerHTML = h;
    })
    .catch(function () {
      document.getElementById("page").innerHTML =
        '<div class="vide"><b>Fiche introuvable.</b>Aucune fiche publiée ne '
        + 'porte cet identifiant. <a href="/">Retour au fil</a></div>';
    });
})();
