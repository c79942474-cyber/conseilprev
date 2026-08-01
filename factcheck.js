/* ── CONTRÔLES FACTUELS — composant partagé par toutes les pages ────────────
   Un chiffre de ce site peut entrer dans une note d'investissement, un dossier
   de crédit, un questionnaire de souscription ou un inventaire d'émissions.
   Aucun de ces usages ne se satisfait d'un résultat : il faut le verdict du
   contrôle, la source, et la date.

   Ce fichier est SERVI À TOUTES LES PAGES et n'a aucune dépendance : ni cadre,
   ni helper de la page hôte. Trois pages l'utilisent aujourd'hui, une
   quatrième pourra l'utiliser demain sans que rien ne soit recopié — c'est la
   raison d'être d'un fichier séparé plutôt que d'un bloc dans chaque page.

   Deux emplois :
     — `fcBadge(cle)` pose une pastille EN REGARD d'une valeur précise ;
     — `fcRegistre(id)` déroule le registre complet dans un conteneur.

   Le style est injecté par le script lui-même : une feuille séparée serait une
   requête de plus et une occasion d'oublier. */
(function () {
  "use strict";

  var FC = { data: null, portee: null, attente: [] };

  /* ── Style ─────────────────────────────────────────────────────────────── */
  var CSS =
    ".fc-b{display:inline-flex;align-items:center;gap:4px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;" +
    "font-size:8.5px;text-transform:uppercase;letter-spacing:.05em;font-weight:700;padding:2px 6px;" +
    "border-radius:2px;vertical-align:1px;margin-left:6px;white-space:nowrap;cursor:help;border:1px solid transparent}" +
    ".fc-b:focus-visible{outline:2px solid #1E63A8;outline-offset:2px}" +
    ".fc-b i{width:6px;height:6px;border-radius:50%;display:inline-block;flex:0 0 auto}" +
    ".fc-b.v-confirme{background:rgba(30,99,54,.12);color:#1E6336}" +
    ".fc-b.v-corrige{background:rgba(196,124,26,.16);color:#8A5310}" +
    ".fc-b.v-plausible{background:rgba(30,99,168,.12);color:#17497E}" +
    ".fc-b.v-inverifiable{background:rgba(122,122,122,.14);color:#5A5A5A}" +
    ".fc-tf{display:flex;align-items:flex-end;gap:10px;flex-wrap:wrap;margin:0 0 12px;padding:10px 12px;background:#F7F6F3;border:1px solid #E3E1DC;border-radius:6px}" +
    ".fc-tf label{display:flex;flex-direction:column;gap:3px;min-width:170px}" +
    ".fc-tf span{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:8.5px;letter-spacing:.12em;text-transform:uppercase;color:#8A8A8A}" +
    ".fc-tf select{font:inherit;font-size:12px;color:#1C1C1C;background:#fff;border:1px solid #E3E1DC;border-radius:4px;padding:6px 8px;cursor:pointer;max-width:250px}" +
    ".fc-tf select:hover{border-color:#1C5CAB}" +
    ".fc-tf button{font:inherit;font-size:11.5px;color:#1E63A8;background:#fff;border:1px solid #E3E1DC;border-radius:4px;padding:6px 10px;cursor:pointer;white-space:nowrap}" +
    ".fc-tf button:hover{border-color:#1E63A8;background:#F2F5FA}" +
    ".fc-tf-n{margin-left:auto;font-family:'JetBrains Mono',ui-monospace,monospace;font-size:11px;color:#8A8A8A;padding-bottom:7px;white-space:nowrap;text-transform:none;letter-spacing:0}" +
    ".fc-tf-n.on{color:#8A5310;font-weight:700}" +
    "@media print{.fc-tf{display:none}}" +
    ".fc-bulle{position:absolute;z-index:80;max-width:360px;background:rgba(28,28,28,.97);color:#fff;" +
    "border-radius:5px;padding:11px 14px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;" +
    "font-size:12px;font-weight:400;line-height:1.55;text-align:left;box-shadow:0 5px 20px rgba(0,0,0,.3);" +
    "opacity:0;transition:opacity .12s;text-transform:none;letter-spacing:0;pointer-events:none}" +
    ".fc-bulle.on{opacity:1;pointer-events:auto}" +
    ".fc-bulle b{color:#fff}.fc-bulle a{color:#9CC4EE}" +
    ".fc-bulle .fc-av{display:block;margin-top:7px;padding-top:7px;border-top:1px solid rgba(255,255,255,.18);color:#D9D5CF}" +
    ".fc-reg{margin-top:6px}" +
    ".fc-tete{display:flex;gap:16px;flex-wrap:wrap;align-items:baseline;margin-bottom:10px}" +
    ".fc-c{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11px}" +
    ".fc-c b{font-size:15px;font-family:Georgia,serif;font-weight:400;margin-right:4px}" +
    ".fc-wrap{overflow-x:auto;border:1px solid #E3E1DC;border-radius:4px}" +
    ".fc-t{width:100%;border-collapse:collapse;font-size:11.5px;min-width:760px}" +
    ".fc-t th{text-align:left;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:9px;" +
    "text-transform:uppercase;letter-spacing:.06em;color:#8A8A8A;font-weight:400;padding:8px 10px;" +
    "border-bottom:1px solid #E3E1DC;white-space:nowrap;background:#F7F6F3}" +
    ".fc-t td{border-bottom:1px solid #E3E1DC;padding:8px 10px;vertical-align:top;line-height:1.5}" +
    ".fc-t tbody tr:hover{background:#FAFAF8}" +
    ".fc-t .fc-src{font-size:10.5px;color:#5A5A5A}" +
    ".fc-t .fc-av{display:block;margin-top:4px;font-size:10.5px;color:#8A5310}" +
    "@media print{.fc-b{border-color:#999}}";

  function style() {
    if (document.getElementById("fc-style")) return;
    var s = document.createElement("style");
    s.id = "fc-style";
    s.textContent = CSS;
    document.head.appendChild(s);
  }

  function esc(t) {
    return String(t == null ? "" : t).replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  /* ── Une seule bulle, déplacée ─────────────────────────────────────────── */
  var BULLE = null;

  function bulle() {
    if (!BULLE) {
      BULLE = document.createElement("div");
      BULLE.className = "fc-bulle";
      BULLE.setAttribute("role", "tooltip");
      document.body.appendChild(BULLE);
    }
    return BULLE;
  }

  function montrer(el) {
    var c = FC.index && FC.index[el.getAttribute("data-fc")];
    if (!c) return;
    var v = (FC.data.verdicts || {})[c.verdict] || {};
    var s = c.source || {};
    var b = bulle();
    b.innerHTML =
      "<b>" + esc(v.nom || c.verdict) + " — " + esc(c.sujet) + "</b><br>" + esc(c.constat)
      + (c.avant ? '<span class="fc-av"><b>Valeur d’origine :</b> ' + esc(c.avant)
                 + " — remplacée après contrôle.</span>" : "")
      + (s.titre ? '<span class="fc-av">' + esc(s.editeur || "")
          + (s.url ? ' · <a href="' + esc(s.url) + '" target="_blank" rel="noopener">'
                     + esc(s.titre) + "</a>" : " · " + esc(s.titre))
          + (c.verifie_le ? "<br>Contrôlé le " + esc(c.verifie_le) : "") + "</span>" : "");
    b.classList.add("on");
    /* Position en coordonnées de PAGE : la bulle est en position absolute, il
       faut donc ajouter le défilement, sans quoi elle saute dès qu'on défile. */
    var r = el.getBoundingClientRect();
    var x = r.left + window.scrollX - 8;
    var y = r.bottom + window.scrollY + 7;
    var larg = document.documentElement.clientWidth;
    if (x + b.offsetWidth > window.scrollX + larg - 10) x = window.scrollX + larg - b.offsetWidth - 10;
    if (x < window.scrollX + 6) x = window.scrollX + 6;
    if (r.bottom + b.offsetHeight + 16 > document.documentElement.clientHeight) {
      y = r.top + window.scrollY - b.offsetHeight - 7;
    }
    b.style.left = Math.round(x) + "px";
    b.style.top = Math.round(y) + "px";
  }

  function cacher() { if (BULLE) BULLE.classList.remove("on"); }

  /* ── Pastille en regard d'une valeur ───────────────────────────────────── */
  function html(c) {
    var v = (FC.data.verdicts || {})[c.verdict] || {};
    return '<button type="button" class="fc-b v-' + esc(c.verdict) + '" data-fc="' + esc(c.cle)
      + '" aria-label="Contrôle factuel : ' + esc(v.nom || c.verdict) + " — " + esc(c.sujet) + '">'
      + '<i style="background:' + esc(v.couleur || "#7A7A7A") + '"></i>' + esc(v.nom || c.verdict)
      + "</button>";
  }

  /* Pose les pastilles sur tous les éléments portant `data-factcheck`.
     Idempotent : la fonction est rejouée après chaque redessin d'une page. */
  function brancher(racine) {
    if (!FC.data) return;
    (racine || document).querySelectorAll("[data-factcheck]").forEach(function (el) {
      if (el.querySelector(":scope > .fc-b")) return;
      var c = FC.index[el.getAttribute("data-factcheck")];
      if (!c) return;
      el.insertAdjacentHTML("beforeend", html(c));
    });
  }

  document.addEventListener("mouseover", function (ev) {
    var b = ev.target.closest ? ev.target.closest(".fc-b") : null;
    if (b) montrer(b);
  });
  document.addEventListener("mouseout", function (ev) {
    if (ev.target.closest && ev.target.closest(".fc-b")) cacher();
  });
  document.addEventListener("focusin", function (ev) {
    if (ev.target.closest && ev.target.closest(".fc-b")) montrer(ev.target.closest(".fc-b"));
  });
  document.addEventListener("focusout", cacher);
  document.addEventListener("keydown", function (ev) { if (ev.key === "Escape") cacher(); });
  /* Au doigt il n'y a pas de survol : le clic ouvre et referme. */
  document.addEventListener("click", function (ev) {
    var b = ev.target.closest ? ev.target.closest(".fc-b") : null;
    if (!b) { cacher(); return; }
    ev.preventDefault();
    if (BULLE && BULLE.classList.contains("on")) cacher(); else montrer(b);
  });
  window.addEventListener("scroll", cacher, { passive: true });

  /* ── Le registre complet ───────────────────────────────────────────────── */
  function registre(idConteneur) {
    var h = document.getElementById(idConteneur);
    if (!h || !FC.data) return;
    var d = FC.data, r = d.resume || {}, V = d.verdicts || {};
    var compte = Object.keys(V).map(function (k) {
      return '<span class="fc-c"><b style="color:' + esc(V[k].couleur) + '">'
        + ((r.compte || {})[k] || 0) + "</b>" + esc(V[k].nom.toLowerCase()) + "</span>";
    }).join("");

    /* Filtre par verdict et par editeur de source. Les listes se construisent
       depuis les donnees : une option ecrite en dur survivrait a la
       disparition de ce qu'elle designe. */
    FC.filtre = FC.filtre || { verdict: "", editeur: "" };
    var tous = d.controles || [];
    var vus = tous.filter(function (c) {
      if (FC.filtre.verdict && c.verdict !== FC.filtre.verdict) return false;
      if (FC.filtre.editeur && ((c.source || {}).editeur || "") !== FC.filtre.editeur) return false;
      return true;
    });
    var editeurs = {};
    tous.forEach(function (c) { var e = (c.source || {}).editeur; if (e) editeurs[e] = 1; });
    var actif = !!(FC.filtre.verdict || FC.filtre.editeur);

    var barre = '<div class="fc-tf">'
      + '<label><span>Verdict</span><select data-fc-f="verdict">'
      + '<option value="">Tous les verdicts</option>'
      + Object.keys(V).map(function (k) {
          return '<option value="' + esc(k) + '"' + (FC.filtre.verdict === k ? " selected" : "")
            + ">" + esc(V[k].nom) + " (" + ((r.compte || {})[k] || 0) + ")</option>";
        }).join("")
      + "</select></label>"
      + '<label><span>Éditeur de la source</span><select data-fc-f="editeur">'
      + '<option value="">Tous les éditeurs</option>'
      + Object.keys(editeurs).sort(function (a, b) { return a.localeCompare(b, "fr"); })
          .map(function (e) {
            return '<option value="' + esc(e) + '"' + (FC.filtre.editeur === e ? " selected" : "")
              + ">" + esc(e) + "</option>";
          }).join("")
      + "</select></label>"
      + '<button type="button" data-fc-raz="1"'
      + (actif ? "" : ' style="visibility:hidden"') + ">Tout afficher</button>"
      + '<span class="fc-tf-n' + (actif ? " on" : "") + '">'
      + (actif ? vus.length + " sur " + tous.length + " affiché(s)" : tous.length + " contrôle(s)")
      + "</span></div>";

    var lignes = vus.map(function (c) {
      var v = V[c.verdict] || {};
      var s = c.source || {};
      return "<tr><th scope=\"row\">" + esc(c.sujet) + "</th>"
        + '<td><span class="fc-b v-' + esc(c.verdict) + '" style="margin:0;cursor:default">'
        + '<i style="background:' + esc(v.couleur || "#7A7A7A") + '"></i>' + esc(v.nom || c.verdict)
        + "</span></td>"
        + "<td>" + esc(c.constat)
        + (c.avant ? '<span class="fc-av">Valeur d’origine : ' + esc(c.avant) + " — remplacée.</span>" : "")
        + "</td>"
        + '<td class="fc-src">' + (s.url
            ? '<a href="' + esc(s.url) + '" target="_blank" rel="noopener">' + esc(s.titre || s.editeur) + "</a>"
            : esc(s.titre || "—"))
        + (s.editeur ? "<br>" + esc(s.editeur) : "")
        + (c.verifie_le ? "<br>" + esc(c.verifie_le) : "") + "</td></tr>";
    }).join("");

    h.innerHTML =
      '<div class="fc-reg"><div class="fc-tete">' + compte
      + (r.verifie_jusqu_a ? '<span class="fc-c" style="color:#8A8A8A">contrôle du '
          + esc(r.verifie_depuis === r.verifie_jusqu_a ? r.verifie_jusqu_a
                : r.verifie_depuis + " au " + r.verifie_jusqu_a) + "</span>" : "")
      + "</div>"
      + barre
      + (lignes
          ? '<div class="fc-wrap"><table class="fc-t"><caption class="sr-only">'
            + "Registre des contrôles factuels</caption><thead><tr>"
            + '<th scope="col">Affirmation contrôlée</th><th scope="col">Verdict</th>'
            + '<th scope="col">Constat</th><th scope="col">Source et date</th>'
            + "</tr></thead><tbody>" + lignes + "</tbody></table></div>"
          : '<p style="font-size:12px;color:#5A5A5A;margin:0">'
            + (actif ? "Aucun contrôle ne correspond à ces filtres — sur "
                       + tous.length + " enregistrés pour cette page."
                     : "Aucun contrôle enregistré pour cette page.") + "</p>")
      + "</div>";

    h.querySelectorAll("[data-fc-f]").forEach(function (sel) {
      sel.addEventListener("change", function () {
        FC.filtre[this.getAttribute("data-fc-f")] = this.value;
        registre(idConteneur);
      });
    });
    var raz = h.querySelector("[data-fc-raz]");
    if (raz) raz.addEventListener("click", function () {
      FC.filtre = { verdict: "", editeur: "" };
      registre(idConteneur);
    });
  }

  /* ── Chargement ────────────────────────────────────────────────────────── */
  function charger(portee, apres) {
    style();
    if (FC.data && FC.portee === portee) { if (apres) apres(FC.data); return; }
    FC.attente.push(apres);
    if (FC.enCours) return;
    FC.enCours = true;
    fetch("/api/factcheck" + (portee ? "?portee=" + encodeURIComponent(portee) : ""),
          { cache: "no-store" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) {
        FC.enCours = false;
        if (!d || !d.ok) return;
        FC.data = d; FC.portee = portee;
        FC.index = {};
        (d.controles || []).forEach(function (c) { if (c.cle) FC.index[c.cle] = c; });
        brancher();
        var f = FC.attente; FC.attente = [];
        f.forEach(function (fn) { if (fn) fn(d); });
      })
      .catch(function () { FC.enCours = false; /* la page vit sans le registre */ });
  }

  window.factcheck = {
    charger: charger, brancher: brancher, registre: registre,
    donnees: function () { return FC.data; },
    controle: function (cle) { return FC.index && FC.index[cle]; },
  };
})();
