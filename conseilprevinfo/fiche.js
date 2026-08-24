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
  var DERNIERE = null, ORGS = null, ORIGINE_SIEGE = "", ORIGINE_SIEGE_EN = "";
  fetch("/api/veille/referentiel", {credentials:"same-origin"})
    .then(function (r) { return r.json(); })
    .then(function (d) {
      if (!d || !d.ok) return;
      ranger("sujet", d.sujets); ranger("impact", d.impacts);
      ranger("statut", d.statuts); ranger("lecture", d.lectures);
      /* LE RÉPERTOIRE DES ORGANISATIONS EST RANGÉ PAR CLÉ. La fiche ne porte
         que des clés — c'est le référentiel qui les nomme, comme pour les
         sujets et les statuts. Une fiche ancienne peut nommer une entreprise
         absente du corpus du jour : c'est pourquoi le répertoire est servi en
         entier, et non déduit des facettes. */
      ORGS = {};
      (d.organisations || []).forEach(function (o) { ORGS[o.cle] = o; });
      ORIGINE_SIEGE = d.origine_du_siege || "";
      ORIGINE_SIEGE_EN = d.origine_du_siege_en || "";
      if (DERNIERE) rendre(DERNIERE);
    })
    .catch(function () { /* les libellés servis avec la fiche font foi */ });

  /* Une bascule redessine la fiche depuis la réponse déjà reçue : la
     redemander au serveur pour changer trois intitulés serait la payer deux
     fois. */
  document.addEventListener("langue", function () {
    if (DERNIERE) rendre(DERNIERE);
  });

  /* ET QUAND L'ÉTAT DE LECTURE CHANGE SOUS LA PAGE — accord donné au bandeau,
     ou « Oublier mes lectures » depuis la barre. Les vignettes de croisement
     portent cet état ; les laisser figées afficherait un code de couleur que
     le lecteur vient d'éteindre ou d'allumer. */
  document.addEventListener("lecture-effacee", function () {
    if (DERNIERE) rendre(DERNIERE);
  });

  function langueAnalyses() {
    return (window.L && window.L.analyses) ? window.L.analyses() : "fr";
  }

  /* LA FICHE EST REDEMANDÉE quand le lecteur change la langue des analyses :
     c'est le serveur qui détient les deux colonnes, et lui seul sait laquelle
     existe pour cette fiche-là. */
  document.addEventListener("analyses", function () { charger(); });

  function charger() {
  fetch("/api/veille/fiche/" + encodeURIComponent(ident)
        + (langueAnalyses() === "en" ? "?analyses=en" : ""),
        {credentials:"same-origin"})
    .then(function (r) { if (!r.ok) throw new Error("404"); return r.json(); })
    .then(function (j) {
      DERNIERE = j;
      /* OUVRIR UNE FICHE LA MARQUE LUE. Le clic sur le fil la marque déjà,
         mais une fiche atteinte par une adresse partagée, un signet ou le
         croisement d'une autre fiche ne passe par aucun clic du fil — et
         resterait « à lire » alors qu'elle vient de l'être. */
      if (window.LU) window.LU.marquer(j.fiche && j.fiche.id);
      rendre(j);
    })
    .catch(function () {
      document.getElementById("page").innerHTML =
        '<div class="vide"><b>' + esc(tr("fi.absente")) + '</b>'
        + esc(tr("fi.absente2")) + ' <a href="/">' + esc(tr("fi.retour")) + '</a></div>';
    });
  }
  charger();

  /* LE RENDU EST UNE FONCTION, pas un corps de promesse : la bascule de
     langue le rejoue sur la réponse déjà reçue. La redemander au serveur pour
     changer trois intitulés la ferait payer deux fois. */
  function rendre(j) {
      var f = j.fiche, s = f.source || {};
      document.title = f.titre + " — CONSEILPREV INFO";
      /* LA FICHE SE COMPOSE COMME UN ARTICLE, ET LE RESTE COMME UNE PAGE.
         La colonne courait sur les 1 240 px de la page : les paragraphes de
         lecture critique faisaient cent quatre-vingts signes par ligne, soit
         près du triple de ce qui se lit sans perdre la ligne suivante. Le
         corps de l'article est donc borné à sa mesure ; le croisement et le
         voisinage, qui sont des grilles de vignettes et non du texte suivi,
         gardent toute la largeur. */
      var h = '<article class="art">';
      h += '<div class="fmeta fi-meta">'
        + '<span class="past ' + esc(f.impact) + '">'
        + esc(nommer("impact", f.impact, f.impact_nom)) + '</span>'
        + '<span class="past sujet">'
        + esc(nommer("sujet", f.sujet, f.sujet_nom)) + '</span>'
        + '<span class="fdate">' + esc(frDate(f.date_fait))
        + (f.date_convention ? ' <b class="conv">convention</b>' : "")
        + '</span></div>';
      h += '<h1 class="titre-journal fi-titre">' + esc(f.titre) + '</h1>';
      h += '<p class="devise fi-chapeau">' + esc(f.chapeau) + '</p>';

      /* UNE DATE FABRIQUÉE LE DIT SOUS ELLE-MÊME. Elle est écrite en toutes
         lettres dans l'incertitude, mais l'incertitude se lit APRÈS la
         lecture critique — trop tard pour un lecteur qui a déjà pris la date
         pour un constat. La réserve va donc là où la date est lue. */
      if (f.date_convention) {
        h += '<p class="conv-dit"><b>Cette date n\'est pas une observation.</b> '
          + esc(f.date_convention_dit || "") + ' ' + esc(f.horizon_dit || "")
          + '</p>';
      }

      if (langueAnalyses() === "en" && f.analyses_traduites === false)
        h += '<p class="an-r" lang="fr">' + esc(tr("an.repli")) + '</p>';
      h += '<div class="fbloc lecture fi-lecture"><span class="fbloc-t">'
        + esc(tr("js.lecture")) + esc(nommer("lecture", f.lecture_nature, f.lecture_nom))
        + '</span><p>' + esc(f.lecture) + '</p></div>';
      h += '<div class="fbloc portee"><span class="fbloc-t">' + esc(tr("js.change")) + '</span>'
        + '<p>' + esc(f.portee) + '</p></div>';
      h += '<div class="fbloc doute"><span class="fbloc-t">' + esc(tr("js.doute")) + '</span>'
        + '<p>' + esc(f.incertitude) + '</p></div>';

      /* LES ENTREPRISES QUE LA SOURCE NOMME — et rien d'autre.
         ─────────────────────────────────────────────────────
         POURQUOI CE BLOC EXISTE. Le fil porte un filtre « Entreprise
         nommée » ; sans ce bloc, un lecteur qui filtre sur Siemens ouvre une
         fiche où le mot Siemens n'apparaît nulle part à l'écran, et il ne
         peut ni vérifier le rattachement ni le contester.

         POURQUOI IL DIT « NOMMÉE » ET NON « CONCERNÉE ». Ce site ne sait pas
         qui est concerné par une faille — il sait qui la source a nommé dans
         son champ d'entité. La nuance est tout l'écart entre un constat et
         une mise en cause, et c'est l'intitulé qui la tient.

         LE SIÈGE PORTE SA MENTION. Il ne vient d'aucune source lue : il est
         écrit à la main par ce cabinet, et il se lit ici comme il se lit dans
         le menu — jamais comme le pays du fait. */
      if ((f.organisations || []).length && ORGS) {
        /* LES DEUX COLONNES SONT SERVIES, ET C'EST ICI QUE L'UNE EST PRISE.
           Le répertoire arrive une fois ; la bascule de langue rejoue ce
           rendu sans rien redemander — c'est la règle du site pour les
           sujets et les statuts, et elle vaut pour les entreprises.

           LA LANGUE DE L'INTERFACE, ET NON CELLE DES ANALYSES. Ces mots-ci —
           « siège disputé », le nom du pays — sont de ce site, pas de la
           source ; le nom de l'entreprise, lui, ne change pas de langue. */
        var en = !!(window.L && window.L.courante() === "en");
        var lo = (f.organisations || []).map(function (c) {
          var o = ORGS[c];
          if (!o) return '<span class="orga">' + esc(c) + '</span>';
          var pn = (en && o.pays_nom_en) ? o.pays_nom_en : o.pays_nom;
          var pm = (en && o.pays_motif_en) ? o.pays_motif_en : o.pays_motif;
          return '<span class="orga">' + esc((en && o.nom_en) ? o.nom_en : o.nom)
            + (o.pays ? '<i>' + esc(pn || o.pays) + '</i>'
                      : '<i class="dispute" title="' + esc(pm || "") + '">'
                        + esc(tr("og.dispute")) + '</i>')
            + '</span>';
        }).join("");
        h += '<div class="fi-orgs"><span class="fbloc-t">'
          + esc(tr("og.titre")) + '</span>' + lo
          + '<p class="fi-orgs-dit">'
          + esc((en ? ORIGINE_SIEGE_EN : ORIGINE_SIEGE) || "") + '</p></div>';
      }

      h += '<div class="src fi-src">'
        + '<span class="na">' + esc(s.nature_nom || "") + ' · '
        + esc(nommer("statut", f.statut, f.statut_nom)) + '</span>'
        + '<h3>' + esc(s.nom || "") + '</h3>'
        + '<p class="ed">' + esc(s.editeur || "") + '</p>'
        + '<p>' + esc(f.statut_dit || "") + '</p>'
        + '<p>' + esc(f.lecture_dit || "") + '</p>'
        + (s.url ? '<p><a href="' + esc(s.url) + '" target="_blank" rel="noopener">'
                   + 'Consulter la source →</a></p>' : "")
        + '<p class="lic">' + esc(s.licence || "") + '</p></div>';
      h += '</article>';

      /* UNE VIGNETTE, DEUX EMPLOIS — mais jamais le même mot. Le bloc dit
         « Lien » quand une règle rattache vraiment les deux fiches, et
         « Rapprochement » quand il n'y a qu'une date en commun. */
      function vignette(l, mot) {
        /* LE CROISEMENT MÈNE À D'AUTRES FICHES, DONC IL PORTE LEUR ÉTAT.
           Sans lui, un lecteur qui suit un lien de voisinage retombe sur une
           fiche qu'il a déjà lue sans qu'aucune de ces vignettes ne l'ait
           prévenu — et le code de couleur du fil s'arrête à la porte de la
           fiche, ce qui le rend deux fois moins fiable qu'il ne l'est. */
        var e = (window.LU ? window.LU.classe(l.id) : "");
        return '<article class="fiche ' + e + '" data-fid="' + esc(l.id)
          + '"><div class="fmeta">'
          + '<span class="past ' + esc(l.impact) + '">'
          + esc(nommer("impact", l.impact, l.impact_nom)) + '</span>'
          + '<span class="fdate">' + esc(frDate(l.date_fait)) + '</span>'
          + (e === "lu"
              ? '<span class="fmarque">' + esc(tr("lc.marque")) + '</span>' : "")
          + '</div>'
          + '<h3 class="ftitre vg-titre"><a class="nu" href="/fiche/'
          + esc(l.id) + '">'
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

      /* LES RUBRIQUES DE LA FICHE PORTENT UN IDENTIFIANT, comme celles de
         l'accueil. Sans lui, la barre latérale — qui LIT les rubriques de la
         page — n'en trouvait aucune ici : sur la page la plus longue du site
         après le fil, elle n'offrait que la liste des pages. */
      var liens = j.liens || [];
      h += '<h2 class="rubrique" id="r-croisement"><span>'
        + esc(tr("fi.croisement")) + '</span>'
        + '<span id="c-liens">' + liens.length + ' ' + esc(tr("fi.liens"))
        + '</span></h2>';
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
        h += '<h2 class="rubrique" id="r-voisinage"><span>'
          + esc(tr("fi.voisinage")) + '</span>'
          + '<span id="c-vois">' + vois.length
          + (j.voisinage_total > vois.length
              ? ' ' + esc(tr("fi.sur")) + ' ' + j.voisinage_total : '')
          + '</span></h2>';
        h += '<p class="dos-dit">' + esc(j.voisinage_dit || "") + '</p>';
        h += '<div class="grille">'
          + vois.map(function (l) { return vignette(l, tr("fi.rapproch")); }).join("")
          + '</div>';
      }
      /* EMPORTER LA FICHE. Placé APRÈS la source et le croisement, jamais en
         tête : on emporte ce qu'on a lu. Un bouton de téléchargement au-dessus
         du texte invite à emporter sans lire, et c'est précisément ce qu'un
         document sorti de son contexte fait de pire. */
      /* LE DOCUMENT EMPORTÉ EST DANS LA LANGUE OÙ IL A ÉTÉ LU. Un PDF anglais
         obtenu depuis une page anglaise est ce qu'attend celui qui clique ;
         un PDF français le surprendrait au moment où il l'ouvre, c'est-à-dire
         trop tard. */
      var q = langueAnalyses() === "en" ? "?analyses=en" : "";
      h += '<div class="emporter">'
        + '<span class="emp-t">' + esc(tr("fi.emporter")) + '</span>'
        + '<a class="emp-b" href="/fiche/' + esc(f.id) + '.pdf' + q + '">PDF</a>'
        + '<a class="emp-b" href="/fiche/' + esc(f.id) + '.docx' + q + '">Word</a>'
        + '<span class="emp-d">' + esc(tr("fi.emporter.dit")) + '</span>'
        + '</div>';

      h += '<p class="fi-retour"><a href="/">' + esc(tr("fi.retour"))
        + '</a></p>';
      document.getElementById("page").innerHTML = h;
  }
})();
