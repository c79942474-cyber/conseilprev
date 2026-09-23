/* Les `title` natifs se lisent aussi au DOIGT et au CLAVIER.
   ═══════════════════════════════════════════════════════════════════════

   LE DÉFAUT MESURÉ. Un attribut `title` n'a qu'un lecteur : la souris
   posée dessus une seconde. Relevé au navigateur en contexte tactile
   (Pixel 7) : un appui sur une pastille de priorité « P1 », sur une ligne
   du menu, sur un bloc de score — rien ne s'affiche, jamais. Un appui long
   sur une ligne du menu SÉLECTIONNE son texte et ouvre le menu système.
   Au clavier, rien non plus : la tabulation atteint la ligne du menu, le
   navigateur n'affiche pas le `title`. Sentinel en porte plus de quatre
   mille : autant d'explications réservées à qui tient une souris.

   CE QUE CE FICHIER FAIT. Il montre le `title` dans UNE bulle à lui,
   `#bulle-titre`, et seulement quand la souris n'y est pas :
     · au doigt, sur un élément INERTE (une pastille, un bloc) : un appui
       ouvre, un second appui ferme, un appui ailleurs ferme ;
     · au doigt, sur un élément qui AGIT (bouton, ligne de menu) : l'appui
       court garde son action, l'appui LONG (500 ms) ouvre la bulle et
       avale le clic du relâcher ;
     · au doigt, sur un LIEN : rien. Le menu du lien (copier, ouvrir dans
       un onglet) vaut plus que l'explication ;
     · au clavier : 500 ms après une tabulation ou une flèche qui a amené
       le focus sur l'élément.

   CE QU'IL NE FAIT PAS, ET POURQUOI.
     · RIEN À LA SOURIS. Le navigateur y montre déjà le `title` : une
       seconde bulle ferait deux bulles l'une sur l'autre au poste fixe.
     · AUCUN `tabindex`. Mesuré dans Chromium : un <div> focalisable qui
       porte un `title` prend ce `title` pour NOM, et la valeur visible
       (« 72 % ») disparaît de ce qu'entend un lecteur d'écran.
     · AUCUNE annonce `aria-live`. Le `title` est déjà le nom ou la
       description de l'élément : l'annoncer le ferait entendre deux fois.
       La bulle est `aria-hidden` — elle se voit, elle ne se lit pas.
     · AUCUN balayage de la page, AUCUN observateur. Mesuré : parcourir
       les 4 684 `[title]` de Sentinel coûte 10,2 ms, à refaire à chacun
       des 679 rappels qu'un observateur recevrait pendant un chargement.
       L'éligibilité est calculée AU MOMENT DE L'ÉVÉNEMENT, sur le seul
       élément touché.

   POURQUOI UN FICHIER À PART, ET NON /infobulles.js. Celui-ci ne ramasse
   que `data-tooltip` et `data-tip`, et deux règles de la suite le figent —
   à raison : pas de `title`, pas d'écouteur de défilement. Les deux
   restent vraies.

   UNE BULLE À LA FOIS — ET « L'APPUI AILLEURS » N'Y SUFFISAIT PAS.
   LE DÉFAUT MESURÉ (revue de robustesse, Sentinel en tablette et banc) :
   les deux scripts ne se parlaient pas, chacun fermant sa bulle sur un
   appui ailleurs. Trois gestes laissaient DEUX bulles ouvertes :
     · la ligne du menu tenue, puis un appui sur SA pastille du rail : la
       pastille est DANS la ligne, l'appui n'était pas « ailleurs » ;
     · une bulle data-tip ouverte, puis une ligne du menu tenue 500 ms :
       les deux jusqu'au relâcher ;
     · un `title` DANS un déclencheur data-tip : l'appui ouvrait les deux,
       le troisième aussi.
   CE QU'ON FAIT. Trois gestes, pas de bus :
     · un appui sur une partie de l'élément qui n'est pas SON ancre (la
       pastille tue par `title=""`) est un appui ailleurs ;
     · ouvrir ici ferme la bulle d'/infobulles.js (`infobulles.fermer`) ;
     · /infobulles.js demande `bulleTitre.prend(ev)` au relâcher : si ce
       geste est le nôtre — un `title` plus proche de la cible que son
       déclencheur, ou un appui long qu'on a servi —, il n'ouvre rien.
       C'est la préséance de `ancreDe`, lue de l'autre côté. */
(function () {
  "use strict";

  var ID = "bulle-titre";
  var CSS_ID = "css-bulle-titre";
  /* Un doigt réel bouge toujours un peu ; au-delà, il glisse. */
  var SEUIL = 10;
  /* L'appui long — le même seuil que le menu système d'Android. */
  var LONG = 500;
  /* Le clic qui suit le relâcher d'un appui long arrive dans ce délai. */
  var APRES_LONG = 400;
  /* Au clavier : le temps de lire le nom avant que la bulle ne s'ouvre, et
     la fenêtre pendant laquelle un focus est dû à la dernière touche. */
  var DELAI_CLAVIER = 500;
  var FENETRE_CLAVIER = 1000;
  var AIDE = "aide-titre";

  /* CE QUI AGIT. Un appui court sur ces éléments garde son action ; la
     bulle ne s'ouvre qu'à l'appui long. */
  var INTERACTIF = 'a[href],button,label,summary,[onclick],[role=button],[role=link],'
    + '[role=tab],[role=menuitem],[role=checkbox],[role=switch],[role=option],'
    + '[contenteditable=""],[contenteditable=true]';
  /* Les CHAMPS n'ont pas de bulle : le clavier virtuel et le sélecteur
     natif la recouvriraient. Leur `title` doit devenir un nom ou une aide
     visible, pas une bulle. */
  var CHAMPS = /^(IFRAME|INPUT|SELECT|TEXTAREA|OPTION)$/;
  /* …ET UN CHAMP N'EN EMPRUNTE PAS NON PLUS À SON CONTENEUR.
     LE DÉFAUT MESURÉ (revue de robustesse, banc) : l'exclusion ne portait
     que sur l'élément qui PORTE le `title`. Un <input> dans un
     `div[title]` ouvrait la bulle du bloc, à l'appui comme à la
     tabulation — au-dessus du clavier virtuel ; un appui long Android
     dans un <input> sous un `label[title]` annulait `contextmenu` : le
     menu Coller disparaissait. On regarde donc aussi l'élément TOUCHÉ. La
     case à cocher et le bouton radio gardent la bulle de leur libellé :
     ni clavier virtuel ni menu Coller, et le libellé les explique. */
  var SAISIE = /^(INPUT|SELECT|TEXTAREA|OPTION)$/;
  function saisie(n) {
    return SAISIE.test(String(n.tagName).toUpperCase())
      && !/^(checkbox|radio)$/i.test(n.getAttribute("type") || "");
  }
  /* « Suivant (Alt+→) » : le raccourci ne fait pas une information.
     « Fermer (Échap) », sans touche de modification, en est une au sens de
     cette règle — c'est la spécification (§2.2) : le lot 3 donne à ces
     boutons un nom qui rend leur `title` redondant. */
  var RACCOURCI = /^\s*\((?:alt|ctrl|maj|shift|⌘|cmd)[^)]*\)$/i;
  /* Les touches qui DÉPLACENT le focus. Un focus qui suit une autre touche
     — Entrée qui ouvre une fenêtre et y place le focus — n'a pas été
     demandé par qui tabule : il n'ouvre rien. */
  var NAVIGATION = { Tab: 1, ArrowUp: 1, ArrowDown: 1, ArrowLeft: 1, ArrowRight: 1,
                     Home: 1, End: 1 };

  function maintenant() { return Date.now(); }

  function norm(s) {
    return String(s == null ? "" : s).toLowerCase()
      .replace(/["«»“”„]/g, "")
      .replace(/\s+/g, " ").trim()
      .replace(/[\s.:;!?…]+$/, "");
  }

  /* LE NOM, APPROCHÉ comme le navigateur le calcule — assez pour savoir si
     le `title` le RÉPÈTE. Un `title` qui répète le nom n'apprend rien : ni
     bulle au doigt, ni bulle au clavier. */
  function nom(t) {
    var ids = (t.getAttribute("aria-labelledby") || "").trim();
    if (ids) {
      var parts = ids.split(/\s+/).map(function (id) {
        var e = document.getElementById(id);
        return e ? e.textContent : "";
      }).join(" ");
      if (norm(parts)) return parts;
    }
    var al = t.getAttribute("aria-label");
    if (al && norm(al)) return al;
    if (t.labels && t.labels.length) {
      var l = [];
      for (var i = 0; i < t.labels.length; i++) l.push(t.labels[i].textContent);
      if (norm(l.join(" "))) return l.join(" ");
    }
    return t.textContent || "";
  }

  function informatif(t) {
    var ti = norm(t.getAttribute("title")), n = norm(nom(t));
    if (ti.length < 2) return false;
    if (ti === n) return false;
    if (n && ti.indexOf(n) === 0 && RACCOURCI.test(ti.slice(n.length))) return false;
    return true;
  }

  /* L'ANCRE D'UN ÉVÉNEMENT : l'élément dont on montrerait le `title`, ou
     rien. Calculée à chaque événement, jamais retenue d'avance. */
  function ancreDe(n) {
    /* `selectstart` vise le NŒUD TEXTE, qui n'a pas de `closest`. */
    if (n && n.nodeType === 3) n = n.parentElement;
    if (!n || !n.closest) return null;
    if (saisie(n)) return null;
    var t = n.closest("[title]");
    /* UN `title=""` EST UN SILENCE EXPLICITE : il masque aussi le `title`
       d'un ancêtre. C'est ainsi que la pastille du rail, qui a sa propre
       bulle, se tait sous la ligne du menu qui la porte. */
    if (!t || !norm(t.getAttribute("title"))) return null;
    if (CHAMPS.test(String(t.tagName).toUpperCase()) || t.closest("select,datalist")) return null;
    /* Les graphiques ont leur propre bulle ; le panorama ses `data-tt`. */
    if (t.closest("svg") || t.closest("[data-graphe]")) return null;
    if (t.closest("[data-tt]")) return null;
    /* LA PRÉSÉANCE. Une bulle d'/infobulles.js posée SUR l'élément ou EN
       DESSOUS l'emporte : le déclencheur le plus proche de la cible parle,
       l'autre se tait. Lu à l'usage — l'autre script a pu démarrer après. */
    var sel = window.infobulles && window.infobulles.selecteur;
    if (sel) {
      var d = null;
      try { d = n.closest(sel); } catch (e) { /* sélecteur illisible */ }
      if (d && (t === d || t.contains(d))) return null;
    }
    if (!informatif(t)) return null;
    return t;
  }

  /* TROIS GESTES, SELON CE QUE L'ÉLÉMENT FAIT DÉJÀ. */
  function mode(t) {
    if (t.closest("a[href]")) return "lien";
    if (t.closest(INTERACTIF)) return "long";
    /* Un <div> qui écoute `click` sans le dire : son curseur le dit. */
    try { if (window.getComputedStyle(t).cursor === "pointer") return "long"; } catch (e) { /* rien */ }
    return "appui";
  }

  function estAide(el) {
    return !!(el && el.classList && el.classList.contains(AIDE));
  }

  function texteDe(a) {
    if (estAide(a)) {
      var ids = (a.getAttribute("aria-describedby") || "").trim().split(/\s+/);
      var out = [];
      for (var i = 0; i < ids.length; i++) {
        var e = ids[i] && document.getElementById(ids[i]);
        if (e) out.push(e.textContent);
      }
      return out.join(" ").replace(/\s+/g, " ").trim();
    }
    return a.getAttribute("title") || "";
  }

  /* ── LA BULLE ─────────────────────────────────────────────────────────
     Une seule pour la page. `aria-hidden` : ce qu'elle montre est déjà le
     nom ou la description de l'élément. `pointer-events:none` : elle
     n'est jamais ouverte par un survol, donc rien n'oblige à pouvoir la
     survoler (1.4.13) — et elle ne vole aucun appui. */
  var bulle = null;
  var ouverte = null;
  var intervalle = null;
  var rafEnCours = false;

  function publierLaFeuille() {
    if (document.getElementById(CSS_ID)) return;
    var s = document.createElement("style");
    s.id = CSS_ID;
    s.textContent =
      /* L'APPUI LONG NE DOIT NI SÉLECTIONNER NI OUVRIR L'APERÇU. Seulement
         sur ce qui agit, et seulement sur un écran tactile : le texte
         d'une pastille inerte reste sélectionnable pour être copié, un
         lien garde son menu. */
      "@media (hover:none) and (pointer:coarse){"
      + "button[title],[role=button][title],[role=tab][title],[role=menuitem][title],"
      + "[onclick][title],summary[title],label[title]{"
      + "-webkit-touch-callout:none;-webkit-user-select:none;user-select:none}}"
      /* Au-dessus de la fenêtre modale (10020) et de sa surcouche (10050).
         Blanc sur #1f2328 : contraste supérieur à 4,5:1. */
      + "#" + ID + "{position:fixed;z-index:10060;max-width:min(320px,calc(100vw - 16px));"
      + "padding:8px 10px;border-radius:6px;background:#1f2328;color:#fff;"
      + "font:13px/1.4 system-ui,sans-serif;box-shadow:0 4px 14px rgba(0,0,0,.25);"
      + "pointer-events:none;white-space:normal;overflow-wrap:anywhere;text-align:left;"
      + "left:8px;top:8px;box-sizing:border-box}"
      + "#" + ID + "[hidden]{display:none}"
      /* LE BOUTON D'AIDE : une cible de 24 px au moins, un focus visible. */
      + "." + AIDE + "{min-width:24px;min-height:24px}"
      + "." + AIDE + ":focus-visible{outline:2px solid currentColor;outline-offset:2px}";
    (document.head || document.documentElement).appendChild(s);
  }

  function creerLaBulle() {
    bulle = document.getElementById(ID);
    if (bulle) return;
    bulle = document.createElement("div");
    bulle.id = ID;
    bulle.setAttribute("aria-hidden", "true");
    bulle.setAttribute("role", "presentation");
    bulle.hidden = true;
    (document.body || document.documentElement).appendChild(bulle);
  }

  /* LA FENÊTRE VISUELLE, et non `innerWidth`. MESURÉ AU PIXEL 7 : sur
     l'écran de maturité, `innerWidth` vaut 491 pour 412 px réellement
     visibles — une bulle bornée à 491 sort de l'écran de 79 px. */
  function fenetre() {
    var vv = window.visualViewport;
    if (vv && vv.width) return vv;
    return { offsetLeft: 0, offsetTop: 0, width: window.innerWidth, height: window.innerHeight };
  }

  function borner(v, min, max) {
    return Math.max(min, Math.min(v, max));
  }

  /* PLACER, C'EST AUSSI VÉRIFIER QUE LA BULLE A ENCORE LIEU D'ÊTRE.
     L'écran peut avoir changé sous elle sans qu'aucun événement le dise :
     `go()` masque un écran entier par `display:none`, le passage
     automatique aussi. Le texte est RELU à chaque fois — un bouton peut
     changer de `title` pendant qu'on le lit. */
  function placer() {
    if (!ouverte || !bulle) return;
    var a = ouverte;
    var txt = texteDe(a);
    if (!a.isConnected || !a.getClientRects().length || !norm(txt)
        || (!estAide(a) && !informatif(a))) return fermer();
    var vv = fenetre();
    var r = a.getBoundingClientRect();
    var gaucheVV = vv.offsetLeft, hautVV = vv.offsetTop;
    var droiteVV = vv.offsetLeft + vv.width, basVV = vv.offsetTop + vv.height;
    /* Hors de la fenêtre visuelle, l'élément ne se lit plus : sa bulle non
       plus. Inégalités STRICTES : le rectangle nul d'un élément masqué
       (0,0,0,0) ne doit pas passer pour « hors de l'écran » — il a sa propre
       garde, plus haut, et sa propre règle. */
    if (r.bottom < hautVV || r.top > basVV || r.right < gaucheVV || r.left > droiteVV) {
      return fermer();
    }
    if (bulle.textContent !== txt) bulle.textContent = txt;
    var sb = document.getElementById("sb");
    var rs = (sb && sb.contains(a)) ? sb.getBoundingClientRect() : null;
    var aDroite = !!rs && droiteVV - rs.right >= 208;
    var largeurMax = Math.min(320, vv.width - 16);
    /* À DROITE DU MENU, LA BULLE PREND LA PLACE QU'IL Y A — PAS PLUS.
       LE DÉFAUT MESURÉ (revues de conformité et de robustesse) : le seuil
       de 208 px disait « il y a la place », mais la bulle, elle, pouvait
       faire 320 px. Entre 208 et 336 px de place, le bornage à droite la
       ramenait PAR-DESSUS le menu, à la hauteur de la ligne qui a le
       focus — banc à 520 px : bulle [192 → 512], ligne [0 → 260]. C'est ce
       que 2.4.11 interdit. On l'étroitise donc AVANT de la mesurer : elle
       s'allonge en hauteur, elle ne déborde plus sur la ligne. */
    if (aDroite) largeurMax = Math.min(largeurMax, droiteVV - rs.right - 16);
    bulle.style.maxWidth = Math.max(0, largeurMax) + "px";
    /* Mesurée à une place qui ne rétrécit pas sa largeur disponible. */
    bulle.style.left = (gaucheVV + 8) + "px";
    bulle.style.top = (hautVV + 8) + "px";
    var b = bulle.getBoundingClientRect(), w = b.width, h = b.height;
    var gauche, haut;
    if (aDroite) {
      /* LE MENU : À DROITE DU MENU, à la hauteur de la ligne. Dessous, la
         bulle recouvrirait les lignes suivantes — celles qu'on tabule. */
      gauche = rs.right + 8;
      haut = borner(r.top, hautVV + 8, basVV - 8 - h);
    } else {
      /* DESSOUS DE PRÉFÉRENCE, DESSUS SI LA PLACE MANQUE — jamais SUR
         l'élément (2.4.11 : ce qu'on lit ne doit pas masquer ce qui a le
         focus). Si aucun côté ne tient, le plus grand, borné. */
      var dessous = r.bottom + 6, dessus = r.top - 6 - h;
      if (dessous + h <= basVV - 8) haut = dessous;
      else if (dessus >= hautVV + 8) haut = dessus;
      else haut = borner((basVV - r.bottom) >= (r.top - hautVV) ? dessous : dessus,
                         hautVV + 8, basVV - 8 - h);
      gauche = r.left + r.width / 2 - w / 2;
    }
    gauche = borner(gauche, gaucheVV + 8, droiteVV - 8 - w);
    bulle.style.left = Math.round(gauche) + "px";
    bulle.style.top = Math.round(haut) + "px";
  }

  function planifier() {
    if (!ouverte || rafEnCours) return;
    rafEnCours = true;
    var suite = function () { rafEnCours = false; placer(); };
    if (window.requestAnimationFrame) window.requestAnimationFrame(suite);
    else setTimeout(suite, 16);
  }

  function fermer() {
    if (intervalle) { clearInterval(intervalle); intervalle = null; }
    var a = ouverte;
    ouverte = null;
    if (bulle && !bulle.hidden) bulle.hidden = true;
    if (estAide(a)) a.setAttribute("aria-expanded", "false");
  }

  /* OUVRIR EST IDEMPOTENT — ce n'est jamais une bascule. L'appui long est
     reconnu DEUX fois sur Android (le minuteur, puis `contextmenu`) : une
     bascule refermerait au second ce que le premier vient d'ouvrir. */
  function ouvrirPour(el) {
    if (!el) return;
    if (ouverte === el && bulle && !bulle.hidden) return;
    fermer();
    /* UNE BULLE À LA FOIS, D'UN SCRIPT À L'AUTRE : celle d'/infobulles.js
       se ferme quand celle-ci s'ouvre — au minuteur de l'appui long comme à
       la tabulation. Mesuré avant : une bulle data-tip ouverte, puis une
       ligne du menu tenue, et les deux bulles l'une à côté de l'autre
       jusqu'au relâcher. Lu à l'usage, comme `selecteur`. */
    var ib = window.infobulles;
    if (ib && typeof ib.fermer === "function") ib.fermer();
    creerLaBulle();
    ouverte = el;
    bulle.hidden = false;
    if (estAide(el)) el.setAttribute("aria-expanded", "true");
    placer();
    /* L'INTERVALLE couvre ce qu'aucun événement ne signale : un écran
       masqué sans défilement, un `title` réécrit. Arrêté à la fermeture. */
    if (ouverte) intervalle = setInterval(placer, 250);
  }

  function demarrer() {
    publierLaFeuille();
    creerLaBulle();

    /* ── LE DOIGT ─────────────────────────────────────────────────────────
       RIEN N'EST DÉCIDÉ AU CONTACT : le navigateur ne sait pas encore si le
       doigt appuie ou fait défiler. Le contact MÉMORISE ; le relâcher
       décide (un `pointerup` sans annulation est une activation « au
       relâcher », WCAG 2.5.2). Pas `click` : iOS n'en émet pas sur un
       <div> inerte quand l'écouteur est délégué sur `document`. */
    var geste = null;
    var minuteur = null;
    var mangerClic = null;
    var dernierContact = { t: 0, type: null };
    var modalite = null;
    var derniereTouche = 0;
    var focusMinuteur = null;
    var repliee = null;

    function annulerMinuteur() {
      if (minuteur) { clearTimeout(minuteur); minuteur = null; }
    }
    /* Un geste qui s'achève après avoir ouvert au long : le clic qui
       suivra le relâcher est encore à avaler, pas au-delà. */
    function finir(g) {
      annulerMinuteur();
      if (g && g.long && mangerClic) mangerClic.jusqua = maintenant() + APRES_LONG;
    }

    document.addEventListener("pointerdown", function (ev) {
      modalite = ev.pointerType;
      dernierContact = { t: maintenant(), type: ev.pointerType };
      annulerMinuteur();
      geste = null;
      /* LA SOURIS N'OUVRE RIEN : le navigateur montre déjà le `title`. */
      if (ev.pointerType === "mouse") return;
      var a = ancreDe(ev.target);
      var g = geste = { id: ev.pointerId, x: ev.clientX, y: ev.clientY, t0: maintenant(),
                        ancre: a, mode: a ? mode(a) : null, long: false };
      if (a && g.mode === "long") {
        /* Chaque fin de geste — relâcher, annulation, glissé, défilement —
           arrête ce minuteur : c'est la seule garde, et chacune a sa règle. */
        minuteur = setTimeout(function () {
          minuteur = null;
          g.long = true;
          ouvrirPour(a);
          /* LE REPLI iOS : Safari n'émet pas `contextmenu`, et peut émettre
             un clic au relâcher — qui déclencherait l'action qu'on voulait
             seulement comprendre. */
          mangerClic = { el: a, jusqua: Infinity };
        }, LONG);
      }
    }, true);

    /* Le navigateur a pris le geste pour lui : il défile, il zoome. Un
       balayage n'ouvre rien — et NE FERME RIEN : la bulle survit au
       défilement du doigt. */
    document.addEventListener("pointercancel", function () {
      var g = geste; geste = null;
      finir(g);
    }, true);

    /* Passif : cet écouteur ne doit jamais retarder le défilement. */
    document.addEventListener("pointermove", function (ev) {
      if (geste && geste.id === ev.pointerId
          && Math.hypot(ev.clientX - geste.x, ev.clientY - geste.y) > SEUIL) {
        var g = geste; geste = null;
        finir(g);
      }
    }, { capture: true, passive: true });

    /* La souris n'a jamais de geste en mémoire (voir le contact) : son
       relâcher s'arrête à la première ligne. */
    document.addEventListener("pointerup", function (ev) {
      if (!geste || geste.id !== ev.pointerId) return;
      var g = geste; geste = null;
      finir(g);
      if (g.long) return;
      /* Au-delà de 500 ms sur un élément inerte : la sélection native,
         pour copier. Rien d'autre. */
      if (maintenant() - g.t0 >= LONG) return;
      var a = ancreDe(ev.target);
      /* Relâché sur une autre ancre que celle du contact : pas un appui. */
      if (a !== g.ancre) return;
      /* UN APPUI AILLEURS ferme la bulle ouverte — « ailleurs » voulant
         dire : pas sur SON ancre. Une partie de l'élément qui a une autre
         ancre, ou aucune, est ailleurs. MESURÉ AVANT, en Sentinel à la
         tablette : la ligne du menu tenue, puis un appui sur sa pastille du
         rail (`title=""`, sa propre bulle data-tooltip) — la pastille étant
         DANS la ligne, sa bulle restait ouverte à côté de celle de la
         pastille. Seul le bouton d'aide garde la sienne : son clic, qui
         suit, fait la bascule. */
      if (ouverte && ouverte !== a && !(estAide(ouverte) && ouverte.contains(ev.target))) fermer();
      if (!a) return;
      /* L'appui COURT sur ce qui agit garde son action, sans bulle ; celui
         sur un lien aussi. */
      if (g.mode !== "appui") { if (ouverte === a) fermer(); return; }
      /* SUR CE QUI N'AGIT PAS : une bascule. On n'annule rien — le texte
         reste sélectionnable. */
      if (ouverte === a) fermer(); else ouvrirPour(a);
    }, true);

    /* CE RELÂCHER EST-IL À NOUS ? Demandé par /infobulles.js, dont
       l'écouteur passe AVANT celui-ci (il est chargé avant) : il n'ouvre
       rien quand la réponse est oui. Oui, si ce geste, relâché sur son
       ancre, a été servi par l'appui long, ou va l'être par la bascule
       d'un élément inerte. MESURÉ AVANT, au banc : un `title` DANS un
       déclencheur data-tip ouvrait les deux bulles à l'appui, et un bouton
       à `title` tenu dans ce déclencheur voyait la bulle data-tip s'ouvrir
       au relâcher, à côté de la sienne. L'appui court sur ce qui agit
       n'est PAS à nous : il laisse à /infobulles.js sa lecture d'abord. */
    prendre = function (ev) {
      var g = geste;
      if (!g || !ev || g.id !== ev.pointerId || !g.ancre) return false;
      if (ancreDe(ev.target) !== g.ancre) return false;
      return g.long || (g.mode === "appui" && maintenant() - g.t0 < LONG);
    };

    /* LE CLIC DU RELÂCHER D'UN APPUI LONG EST AVALÉ ; tout autre passe. */
    document.addEventListener("click", function (ev) {
      var m = mangerClic;
      mangerClic = null;
      if (m && maintenant() <= m.jusqua && m.el.contains(ev.target)) {
        ev.preventDefault();
        ev.stopImmediatePropagation();
        return;
      }
      /* LE BOUTON D'AIDE : une bascule, souris comprise — il n'a pas de
         `title`, donc pas de seconde bulle au poste fixe. Entrée et Espace
         arrivent ici aussi, en `click` natif du bouton. */
      var b = ev.target && ev.target.closest && ev.target.closest("." + AIDE);
      if (b) { if (ouverte === b) fermer(); else ouvrirPour(b); }
    }, true);

    /* L'APPUI LONG ANDROID : `contextmenu`, sur ce qui agit et pas sur un
       lien. On regarde le `pointerType` DE CET ÉVÉNEMENT : la touche Menu
       et Maj+F10 en donnent un de type souris, et gardent leur menu. */
    document.addEventListener("contextmenu", function (ev) {
      var tactile = ev.pointerType === "touch" || ev.pointerType === "pen"
        || (ev.pointerType === undefined && maintenant() - dernierContact.t < 1000
            && dernierContact.type && dernierContact.type !== "mouse");
      if (!tactile) return;
      var a = ancreDe(ev.target);
      if (!a || mode(a) !== "long") return;
      ev.preventDefault();
      /* Le filet : la sélection a pu être posée avant cet événement. */
      try { window.getSelection().removeAllRanges(); } catch (e) { /* rien */ }
      ouvrirPour(a);
      annulerMinuteur();
      if (geste && geste.ancre === a) geste.long = true;
      mangerClic = { el: a, jusqua: geste ? Infinity : maintenant() + APRES_LONG };
    }, true);

    /* PENDANT UN APPUI LONG SUR CE QUI AGIT, PAS DE SÉLECTION. Mesuré :
       l'annuler supprime les `selectionchange` sans empêcher `contextmenu`. */
    document.addEventListener("selectstart", function (ev) {
      if (geste && geste.mode === "long" && ancreDe(ev.target) === geste.ancre) ev.preventDefault();
    }, true);

    /* ── LE CLAVIER ───────────────────────────────────────────────────────
       LA MODALITÉ EST SUIVIE, PAS DEVINÉE. `:focus-visible` est vrai au
       clic de souris sur un champ : on ne s'y fie pas. Un focus ouvre la
       bulle s'il suit, de moins d'une seconde, une touche qui DÉPLACE le
       focus. */
    window.addEventListener("keydown", function (ev) {
      if (NAVIGATION[ev.key]) {
        modalite = "clavier";
        derniereTouche = maintenant();
        return;
      }
      /* Entrée, Espace, une lettre : le focus qui suivra n'a pas été
         demandé par qui tabule. */
      derniereTouche = 0;
      /* ENTRÉE ET ESPACE ACTIVENT L'ÉLÉMENT : SA BULLE A FINI DE SERVIR.
         LE DÉFAUT MESURÉ (revues navigateur et robustesse, Sentinel au
         poste) : Tab jusqu'au bouton « Guide d'utilisation », sa bulle
         s'ouvre ; Entrée ouvre la fenêtre du guide SANS y déplacer le focus
         — aucun `focusout`, et la bulle (10060) restait PAR-DESSUS la
         fenêtre (10020). Le premier Échap ne fermait qu'elle. Même chose
         sur une ligne du menu : Entrée naviguait, la bulle restait sur le
         nouvel écran. On ferme. Le focus, resté sur l'élément, ne la
         rouvre pas : Entrée a remis la modalité à zéro (plus haut) — un
         `focus()` posé ensuite par la page n'ouvre rien. Seulement si le
         focus est DANS l'ancre
         — Espace sur la page fait défiler, et le défilement ne ferme pas.
         Pas le bouton d'aide : pour lui, Entrée EST la bascule (son clic). */
      if ((ev.key === "Enter" || ev.key === " " || ev.key === "Spacebar") && ouverte
          && !estAide(ouverte) && ouverte.contains(document.activeElement)) {
        fermer();
        return;
      }
      if (ev.key === "Escape" || ev.key === "Esc") {
        /* ÉCHAP NE FERME QU'UNE CHOSE À LA FOIS. Écouté sur `window`, en
           capture — avant la fenêtre modale, qui écoute sur `document`. Si
           une bulle est visible, cette frappe-là est consommée ; la
           suivante ferme la fenêtre. */
        if (!ouverte) return;
        repliee = ouverte;
        fermer();
        ev.preventDefault();
        ev.stopImmediatePropagation();
      }
    }, true);

    function annulerFocus() {
      if (focusMinuteur) { clearTimeout(focusMinuteur); focusMinuteur = null; }
    }

    /* 500 MS AVANT D'OUVRIR : qui tabule dans le menu traverse dix lignes
       sans vouloir dix bulles. */
    document.addEventListener("focusin", function (ev) {
      annulerFocus();
      /* Le repli ne vaut que tant que le focus reste sur l'élément replié. */
      if (repliee && !repliee.contains(ev.target)) repliee = null;
      if (modalite !== "clavier" || maintenant() - derniereTouche >= FENETRE_CLAVIER) return;
      var a = ancreDe(ev.target);
      if (!a || a === repliee) return;
      /* Le délai court encore si le focus part vers un autre élément (le
         `focusin` suivant l'arrête) ou vers RIEN — un clic dans le vide, la
         fenêtre quittée : c'est alors cette garde qui l'arrête. */
      focusMinuteur = setTimeout(function () {
        focusMinuteur = null;
        if (a.contains(document.activeElement)) ouvrirPour(a);
      }, DELAI_CLAVIER);
    });

    document.addEventListener("focusout", function (ev) {
      var vers = ev.relatedTarget;
      if (ouverte && ouverte.contains(ev.target) && !(vers && ouverte.contains(vers))) fermer();
    });

    /* ── LE REPLACEMENT ───────────────────────────────────────────────────
       ═══ LE DÉFILEMENT REPLACE, IL NE FERME JAMAIS ═══
       /infobulles.js l'a payé : fermer au défilement refermait la bulle
       avant qu'elle soit lue, parce qu'amener un élément à l'écran émet
       des dizaines d'événements APRÈS l'appui. La bulle SUIT l'élément ;
       elle ne se ferme que s'il sort de l'écran (voir `placer`). Un
       défilement pendant un appui annule en revanche l'appui long : le
       doigt ne visait plus rien. */
    document.addEventListener("scroll", function () {
      annulerMinuteur();
      planifier();
    }, { capture: true, passive: true });
    /* LE REDIMENSIONNEMENT NE FERME QUE S'IL CHANGE LA LARGEUR : la barre
       d'adresse qui se rétracte n'émet qu'un changement de hauteur. */
    var largeur = window.innerWidth;
    window.addEventListener("resize", function () {
      if (window.innerWidth !== largeur) { largeur = window.innerWidth; fermer(); return; }
      planifier();
    });
    window.addEventListener("orientationchange", fermer);
    if (window.visualViewport && window.visualViewport.addEventListener) {
      window.visualViewport.addEventListener("resize", planifier);
      window.visualViewport.addEventListener("scroll", planifier);
    }
  }

  /* `prend` ne répond qu'une fois le script démarré ; avant, aucun geste
     n'est à lui. */
  var prendre = function () { return false; };
  window.bulleTitre = { fermer: fermer, ouvrirPour: ouvrirPour,
                        prend: function (ev) { return prendre(ev); } };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", demarrer);
  } else {
    demarrer();
  }
})();
