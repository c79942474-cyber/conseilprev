/* LA PAGE DE CONFRONTATION.

   LE DOCUMENT NE PASSE PAS PAR `JSON.stringify`. Il part en `FormData`,
   c'est-à-dire en flux : encodé en base64 dans un corps JSON, il serait
   d'abord chargé EN ENTIER dans la mémoire de l'onglet, et un fichier de
   quelques mégaoctets ferait ramer la page avant même l'envoi.

   RIEN N'EST GARDÉ CÔTÉ NAVIGATEUR NON PLUS. Le champ de fichier est vidé
   après l'envoi : un document laissé dans un formulaire repart au prochain
   envoi accidentel, et sur un poste partagé il reste visible au suivant. */
(function () {
  "use strict";
  var CLE = "cpinfo.jeton";
  var DELAI = 45000;   /* plus long qu'ailleurs : un document se téléverse */

  function $(i) { return document.getElementById(i); }
  function esc(x) {
    return String(x == null ? "" : x).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function jeton() {
    try { return sessionStorage.getItem(CLE) || ""; } catch (e) { return ""; }
  }

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

  function dire(msg, alerte) {
    var e = $("etat");
    e.textContent = msg || "";
    e.className = "bandeau-etat" + (alerte ? " alerte" : "");
    e.hidden = !msg;
  }

  function demander(url, options) {
    var o = options || {};
    var ctrl = new AbortController();
    var t = setTimeout(function () { ctrl.abort(); }, DELAI);
    var entetes = {};
    if (jeton()) entetes.Authorization = "Bearer " + jeton();
    if (!o.corpsForm) entetes["Content-Type"] = "application/json";
    return fetch(url, {
      method: o.method || "GET", signal: ctrl.signal,
      credentials: "same-origin", headers: entetes,
      body: o.corpsForm || undefined
    }).then(function (r) {
      clearTimeout(t);
      return r.json().then(function (j) { j._statut = r.status; return j; });
    }).catch(function (e) {
      clearTimeout(t);
      if (e && e.name === "AbortError") {
        var x = new Error("délai"); x.name = "DelaiDepasse"; throw x;
      }
      throw e;
    });
  }

  /* La liste des rubriques vient du serveur : la recopier ici la figerait au
     jour de l'écriture, et l'écran ferait foi contre le moteur. */
  function rubriques() {
    return demander("/api/veille/referentiel").then(function (r) {
      if (!r.ok) return;
      var sel = $("c-sujet");
      (r.sujets || []).forEach(function (s) {
        var o = document.createElement("option");
        /* LE LIBELLÉ SUIT LA LANGUE. Le serveur porte les deux ; recopier
           `nom` laissait des rubriques françaises dans un formulaire
           anglais. */
        o.value = s.cle;
        o.textContent = (window.L && window.L.courante() === "en" && s.nom_en)
          ? s.nom_en : s.nom;
        sel.appendChild(o);
      });
    }).catch(function () { /* le champ reste sur « déduire » */ });
  }

  function moi() {
    if (!jeton()) { $("hors").hidden = false; return Promise.resolve(); }
    return demander("/api/abonnes/moi").then(function (r) {
      var ouvert = !!(r && r.ok);
      $("hors").hidden = ouvert;
      $("dedans").hidden = !ouvert;
    }).catch(function () { $("hors").hidden = false; });
  }

  function rendre(r) {
    $("resultat").hidden = false;

    /* LA RUBRIQUE RETENUE EST DITE, et pourquoi. Un filtrage silencieux
       laisserait croire que le corpus ne porte que cela.

       QUAND LA RUBRIQUE A ÉTÉ ÉLARGIE, ÇA SE VOIT. La phrase le dit déjà,
       mais elle est longue : un lecteur pressé la survole et croit lire son
       domaine. La marque, elle, ne se survole pas. */
    $("c-portee").textContent = r.sujet_pourquoi + " " + r.dit;
    $("c-portee").className = r.sujet_elargi ? "dos-dit elargi" : "dos-dit";
    $("c-ponts").textContent = r.n_echos + " terme(s) en commun";

    $("c-echos").innerHTML = (r.echos || []).map(function (e) {
      return '<span class="dos"><b>' + esc(e.terme) + '</b>'
        + '<span class="n">' + e.fiches + '</span></span>';
    }).join("") || '<span class="dos-dit">Aucun terme de votre document ne '
      + 'revient sur assez de fiches pour former un pont. Ce n\'est pas un '
      + 'jugement sur le document : c\'est que le corpus, sur cette rubrique, '
      + 'n\'en traite pas encore.</span>';

    $("c-fiches").innerHTML = (r.echos || []).map(function (e) {
      return '<div class="fbloc"><span class="fbloc-t">« ' + esc(e.terme)
        + ' » — ' + e.fiches + ' fiche(s), ' + e.occurrences_document
        + ' fois dans votre document</span><p>'
        + (e.exemples || []).map(function (f) {
            return '<a href="/fiche/' + esc(f.id) + '">' + esc(f.titre) + '</a>';
          }).join(' · ')
        + '</p></div>';
    }).join("");

    /* LE BLOC DES ABSENCES DIT POURQUOI IL EST VIDE QUAND IL L'EST. Vide sans
       un mot, il passerait pour une panne — ou pour un document sans défaut,
       ce qui serait pire. */
    $("c-nq").textContent = r.questions_utiles
      ? r.n_questions + " question(s)" : "aucune, et voici pourquoi";
    $("c-questions-dit").textContent = r.questions_pourquoi || "";
    $("c-questions").innerHTML = (r.questions || []).map(function (q) {
      return '<div class="fbloc doute"><span class="fbloc-t">« '
        + esc(q.terme) + ' » — ' + q.fiches + ' fiche(s), '
        + (q.sources || []).length + ' source(s)</span><p>'
        + esc(q.question) + '</p><p>'
        + (q.exemples || []).map(function (f) {
            return '<a href="/fiche/' + esc(f.id) + '">' + esc(f.titre) + '</a>';
          }).join(' · ')
        + '</p></div>';
    }).join("");

    $("c-ecartes").textContent = r.ecartes_dit || "";
    $("c-reserve").textContent = r.n_etablit_pas || "";
  }

  $("f-conf").addEventListener("submit", function (ev) {
    ev.preventDefault();
    var f = $("c-fichier").files[0];
    if (!f) { dire("Choisissez un document.", true); return; }
    var fd = new FormData();
    fd.append("document", f);
    if ($("c-sujet").value) fd.append("sujet", $("c-sujet").value);
    dire("Confrontation en cours — le document est lu en mémoire, pas écrit.");
    demander("/api/confrontation", { method: "POST", corpsForm: fd })
      .then(function (r) {
        /* LE CHAMP EST VIDÉ QUOI QU'IL ARRIVE : un document laissé dans le
           formulaire repart au prochain envoi accidentel, et sur un poste
           partagé il reste visible au suivant. */
        $("c-fichier").value = "";
        if (!r.ok) {
          $("resultat").hidden = true;
          dire(r.message || "La confrontation n'a pas abouti.", true);
          return;
        }
        dire("");
        rendre(r);
      })
      .catch(function (e) {
        $("c-fichier").value = "";
        dire(e && e.name === "DelaiDepasse"
             ? "Le serveur n'a pas répondu dans le délai. Le document n'a pas "
               + "été conservé — réessayez."
             : "Le serveur n'a pas répondu.", true);
      });
  });

  /* À la bascule, la liste des rubriques est reconstruite : ses libellés
     changent de langue, et le choix en cours est préservé. */
  document.addEventListener("langue", function () {
    var sel = $("c-sujet"), garde = sel.value;
    while (sel.options.length > 1) sel.remove(1);
    rubriques().then(function () { sel.value = garde; });
  });

  rubriques().then(moi);
})();
