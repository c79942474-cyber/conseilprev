/* LA PAGE D'ABONNEMENT.

   LE JETON VIT DANS `sessionStorage`, PAS DANS `localStorage` : il disparaît
   à la fermeture de l'onglet. Sur un poste partagé — et un poste d'atelier
   l'est presque toujours — un jeton qui survit à la fermeture ouvre le compte
   au suivant. La commodité de rester connecté ne vaut pas ce risque-là.

   IL N'EST JAMAIS MIS DANS L'URL : une adresse se retrouve dans les journaux
   du serveur, dans l'historique du navigateur, et dans l'en-tête `Referer`
   envoyé aux tiers. */
(function () {
  "use strict";
  function tr(c) { return (window.L && window.L.t) ? window.L.t(c) : c; }
  var CLE = "cpinfo.jeton";
  var DELAI = 15000;

  function $(i) { return document.getElementById(i); }
  function esc(x) {
    return String(x == null ? "" : x).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  /* sessionStorage jette dans une fenêtre privée ou quand le navigateur
     bloque les données de site : la page doit rester utilisable sans lui. */
  var memoire = null;
  function jeton(v) {
    if (v !== undefined) {
      memoire = v;
      try { v ? sessionStorage.setItem(CLE, v) : sessionStorage.removeItem(CLE); }
      catch (e) { /* la session ne survivra pas au rechargement, sans plus */ }
      return v;
    }
    if (memoire !== null) return memoire;
    try { return sessionStorage.getItem(CLE) || ""; } catch (e) { return ""; }
  }

  function demander(url, options) {
    var o = options || {};
    var ctrl = new AbortController();
    var minuteur = setTimeout(function () { ctrl.abort(); }, DELAI);
    var entetes = { "Content-Type": "application/json" };
    if (jeton()) entetes.Authorization = "Bearer " + jeton();
    return fetch(url, {
      method: o.method || "GET", signal: ctrl.signal,
      credentials: "same-origin", headers: entetes,
      body: o.corps ? JSON.stringify(o.corps) : undefined
    }).then(function (r) {
      clearTimeout(minuteur);
      return r.json().then(function (j) { j._statut = r.status; return j; });
    }).catch(function (e) {
      clearTimeout(minuteur);
      if (e && e.name === "AbortError") {
        var t = new Error("délai dépassé"); t.name = "DelaiDepasse"; throw t;
      }
      throw e;
    });
  }

  function dire(msg, alerte) {
    var e = $("etat");
    e.textContent = msg || "";
    e.className = "bandeau-etat" + (alerte ? " alerte" : "");
    e.hidden = !msg;
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

  var REF = null;

  function referentiel() {
    return demander("/api/veille/referentiel").then(function (r) {
      if (!r.ok) return;
      REF = r;
      $("a-sujets").innerHTML = (r.sujets || []).map(function (s) {
        return '<label class="case"><input type="checkbox" value="'
          + esc(s.cle) + '"> ' + esc((window.L && window.L.courante() === "en" && s.nom_en) ? s.nom_en : s.nom) + '</label>';
      }).join("");
      $("a-seuil").innerHTML = (r.impacts || []).map(function (i) {
        return '<option value="' + esc(i.cle) + '">'
          + esc((window.L && window.L.courante() === "en" && i.nom_en)
                ? i.nom_en : i.nom)
          + " " + esc(tr("ab.audessus")) + "</option>";
      }).join("");
    });
  }

  function montrer(compte) {
    $("hors").hidden = !!compte;
    $("dedans").hidden = !compte;
    if (!compte) return;
    $("c-email").textContent = compte.email;
    var suivis = compte.sujets || [];
    Array.prototype.forEach.call(
      $("a-sujets").querySelectorAll("input"),
      function (c) { c.checked = suivis.indexOf(c.value) >= 0; });
    $("a-seuil").value = compte.seuil;
  }

  function moi() {
    if (!jeton()) { montrer(null); return Promise.resolve(); }
    return demander("/api/abonnes/moi").then(function (r) {
      if (!r.ok) { jeton(""); montrer(null); return; }
      montrer(r.compte);
      /* L'ABSENCE D'ENVOI EST ANNONCÉE ICI, à côté du bulletin, et pas
         seulement dans les conditions générales : c'est là que le lecteur
         croirait qu'il va recevoir quelque chose. */
      var e = $("envoi");
      e.textContent = r.pourquoi_pas_d_envoi || "";
      e.className = "bandeau-etat" + (r.pourquoi_pas_d_envoi ? " alerte" : "");
      e.hidden = !r.pourquoi_pas_d_envoi;
      return bulletin();
    }).catch(function () { dire("Le serveur n'a pas répondu.", true); });
  }

  function bulletin() {
    return demander("/api/abonnes/bulletin").then(function (r) {
      if (!r.ok) return;
      $("bulletin").textContent = r.texte || "";
      var b = r.bulletin || {};
      $("c-bul").textContent = b.vide
        ? "vide — et c'est une information"
        : b.n_servies + " fait(s) sur " + b.n_retenues + " retenu(s)";
    });
  }

  function identifiants() {
    return { email: $("a-email").value.trim(), motdepasse: $("a-mdp").value };
  }

  $("f-compte").addEventListener("submit", function (ev) {
    ev.preventDefault();
    dire("Connexion…");
    demander("/api/abonnes/connexion", { method: "POST", corps: identifiants() })
      .then(function (r) {
        if (!r.ok) { dire(r.message || "Connexion refusée.", true); return; }
        jeton(r.jeton);
        $("a-mdp").value = "";
        dire("");
        return moi();
      }).catch(function () { dire("Le serveur n'a pas répondu.", true); });
  });

  /* L'INSCRIPTION NE LIT PAS LES PRÉFÉRENCES, et c'est délibéré : les cases
     de sujets appartiennent à la section du compte, qui est masquée tant
     qu'on n'est pas connecté. Les interroger ici renverrait une liste vide
     en croyant lire un choix — le compte se serait créé sur des réglages que
     personne n'a faits, sans que rien ne le signale.

     Le compte naît donc sur les réglages par défaut du moteur (tous les
     sujets, seuil « structurant »), et la page le dit avant le bouton. */
  $("b-inscription").addEventListener("click", function () {
    var id = identifiants();
    dire("Enregistrement…");
    demander("/api/abonnes/inscription", {
      method: "POST",
      corps: { email: id.email, motdepasse: id.motdepasse }
    }).then(function (r) {
      /* LE MESSAGE EST LE MÊME que l'adresse ait été libre ou déjà prise :
         le contraire ferait de ce formulaire un annuaire d'abonnés. */
      dire(r.message || "", !r.ok);
      if (r.ok) $("a-mdp").value = "";
    }).catch(function () { dire("Le serveur n'a pas répondu.", true); });
  });

  $("f-reglages").addEventListener("submit", function (ev) {
    ev.preventDefault();
    var sujets = Array.prototype.map.call(
      $("a-sujets").querySelectorAll("input:checked"), function (c) { return c.value; });
    dire("Enregistrement…");
    demander("/api/abonnes/reglages", {
      method: "POST", corps: { sujets: sujets, seuil: $("a-seuil").value }
    }).then(function (r) {
      if (!r.ok) { dire(r.message || "Réglage refusé.", true); return; }
      dire("Réglages enregistrés. Le bulletin ci-dessous les applique déjà.");
      return bulletin();
    }).catch(function () { dire("Le serveur n'a pas répondu.", true); });
  });

  $("b-deconnexion").addEventListener("click", function () {
    demander("/api/abonnes/deconnexion", { method: "POST" })
      .then(function () { jeton(""); montrer(null); dire("Session fermée."); })
      .catch(function () { jeton(""); montrer(null); });
  });

  $("b-effacer").addEventListener("click", function () {
    /* UNE CONFIRMATION, PARCE QUE L'ACTE EST IRRÉVERSIBLE — et le texte dit
       ce qui disparaît, pas « êtes-vous sûr ? ». */
    if (!window.confirm("Effacer votre compte, vos préférences et vos "
        + "sessions ? Cette action est immédiate et ne peut pas être "
        + "annulée.")) return;
    demander("/api/abonnes/effacer", { method: "POST" }).then(function (r) {
      jeton(""); montrer(null);
      dire(r.message || "Compte effacé.");
    }).catch(function () { dire("Le serveur n'a pas répondu.", true); });
  });

  /* LES LISTES SE REDESSINENT À LA BASCULE. Composées une seule fois au
     chargement, les sujets suivis et les seuils restaient français sur une
     interface anglaise — et ce sont précisément les libellés sur lesquels le
     lecteur clique. Le choix en cours est repris depuis le compte, que
     `moi()` relit. */
  document.addEventListener("langue", function () {
    referentiel().then(moi);
  });

  referentiel().then(moi);
})();
