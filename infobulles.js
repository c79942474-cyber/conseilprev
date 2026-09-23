/* Les infobulles s'ouvrent aussi au DOIGT et au CLAVIER.
   ═══════════════════════════════════════════════════════════════════════

   LE DÉFAUT, MESURÉ AU NAVIGATEUR EN CONTEXTE TACTILE (Pixel 7, hasTouch,
   `(hover:none)` vrai) : sur la page d'accueil, l'opacité de la bulle reste
   à 0 AVANT et APRÈS un appui du doigt. Les trente-deux infobulles du site
   public ne s'ouvrent jamais sur un téléphone. Elles ne s'ouvrent pas
   davantage au clavier : les cartes sont des <div> sans tabindex, et
   `element.focus()` n'y prend même pas — le focus reste sur le <body>.

   POURQUOI. L'ouverture est écrite `:hover::after` et rien d'autre. Il n'y a
   pas de survol sur un écran tactile, et un <div> n'est pas focusable.

   LE MÊME DÉFAUT, MESURÉ ENSUITE DANS SENTINEL, PAR UNE AUTRE PORTE. Le
   script ne reconnaissait que les bulles écrites dans un ATTRIBUT. Sentinel
   en porte quatre autres familles dont le texte est un ÉLÉMENT ENFANT,
   révélé par `A:hover B` — maturité, modèles, tarification, budget : cent
   quatre-vingt-sept déclencheurs, aucun reconnu. Au doigt, les badges
   d'article n'ouvraient JAMAIS leur bulle : chacun est posé dans une carte
   cliquable, et l'appui ouvrait la fiche du document par-dessus. Les trois
   autres familles ne s'ouvraient que par accident — un survol ou un focus
   que le navigateur laisse collés à l'élément touché — et c'est ce même
   accident qui les empêchait de se refermer : ni le second appui ni Échap
   n'ôtent un survol collé. Aucune n'était annoncée.

   CE QUE CE FICHIER FAIT, ET CE QU'IL NE FAIT PAS

   Il ne dessine AUCUNE bulle. Chaque page a déjà la sienne — position,
   couleurs, flèche, largeur — réglée au pixel près, parfois contre un
   `overflow:hidden` qui lui a coûté une recette entière. Une seconde bulle
   dessinée ici s'afficherait EN PLUS de celle du survol sur un poste fixe :
   deux bulles pour une infobulle. Ce script ne fait donc qu'une chose :
   poser une classe, et publier une règle qui ouvre la bulle EXISTANTE quand
   cette classe est là. Le réglage reste où il est.

   POURQUOI LA RÈGLE EST INJECTÉE ICI ET NON ÉCRITE DANS LES PAGES. Vingt
   pages portent la feuille des infobulles. Vingt copies d'une même règle
   divergent — ce dépôt a déjà payé ce défaut-là. Une seule déclaration, au
   même endroit que le comportement qu'elle sert.

   LE LECTEUR D'ÉCRAN. Le texte vit dans un attribut, invisible aux
   technologies d'assistance. À l'ouverture, il est déposé dans une région
   `aria-live` unique pour toute la page : une seule balise en plus, et le
   texte est annoncé au moment où quelqu'un le demande. */
(function () {
  "use strict";

  /* LES DEUX CONVENTIONS DU DÉPÔT, ET RIEN D'AUTRE. `data-tooltip` sur le
     site public, `data-tip` dans Sentinel. Un `title` natif n'est PAS
     ramassé : il appartient au navigateur, sert aussi aux champs de
     formulaire, et le détourner produirait deux infobulles sur un poste
     fixe — celle du navigateur et la nôtre. L'attribut title natif est pris
     en charge ailleurs, par /bulle-titre.js, qui ne réagit jamais à la
     souris.

     Les bulles ENFANTS s'y ajoutent à l'exécution, lues dans les feuilles de
     la page (voir `jumelles`) : aucune n'est nommée ici. */
  var ATTRS = ["data-tooltip", "data-tip"];
  var SELECTEUR = "[data-tooltip],[data-tip]";
  var OUVERTE = "bulle-ouverte";
  /* FERMÉE À LA DEMANDE — ET NON SIMPLEMENT « PAS OUVERTE ».
     ═══════════════════════════════════════════════════════════════════
     LE DÉFAUT MESURÉ. Au doigt, Chromium laisse le survol COLLÉ à
     l'élément touché, et donne le focus à tout élément `tabindex`. Une
     bulle de maturité s'ouvrait donc par son `:hover`, une bulle de
     tarification par son `:focus` — et ni le second appui ni Échap ne la
     refermaient : retirer notre classe ne retire ni un survol ni un focus.
     Relevé au navigateur : opacité 1 après le second appui, 1 après Échap.

     CE QU'ON FAIT : fermer à la demande pose une SECONDE classe, dont la
     règle éteint la bulle malgré le survol ou le focus. Elle tient tant que
     l'élément est TENU — survolé ou focalisé, l'un comme l'autre — et tombe
     dès qu'il ne l'est plus : un appui ailleurs, le pointeur qui s'en va sans
     focus derrière lui, le focus qui part sans survol derrière lui. */
  var FERMEE = "bulle-fermee";
  var REGION = "bulle-annonce";
  /* « LIRE D'ABORD, AGIR ENSUITE » — ET SEULEMENT LÀ OÙ C'EST DEMANDÉ.
     ═══════════════════════════════════════════════════════════════════
     LE DÉFAUT MESURÉ. Sur le rail DORA, chaque bloc est un <bouton> qui
     mène à son panneau. Au doigt, l'appui ouvrait bien la bulle — puis
     déclenchait la navigation, qui repeint le rail et DÉTRUIT le bouton
     qui la portait. Relevé au navigateur : opacité 0. L'infobulle était
     donc illisible au doigt, exactement comme avec le `title` natif
     qu'elle venait remplacer.

     CE QU'ON FAIT : sur ces éléments-là, le premier appui OUVRE et retient
     le clic ; le second laisse passer. C'est la convention mobile
     ordinaire pour un contrôle qui porte une explication, et c'est
     précisément ce que ce rail demande — savoir ce qu'un bloc fait AVANT
     d'y aller.

     POURQUOI UN ATTRIBUT, ET NON POUR TOUT LE MONDE. Retenir le premier
     clic partout changerait le comportement de chaque lien du site au
     doigt. L'élément qui le veut le déclare. */
  var AVANT_CLIC = "data-bulle-avant-clic";

  /* LES BULLES ENFANTS RECONNUES DANS LA PAGE : [déclencheur, bulle], lues
     dans les feuilles au démarrage. Et le sélecteur de TOUS les
     déclencheurs, les deux conventions d'abord. */
  var ENFANTS = [];
  var DECLENCHEURS = SELECTEUR;

  function _norme(s) {
    return (s || "").replace(/\s+/g, " ").trim();
  }

  function texte(el) {
    for (var i = 0; i < ATTRS.length; i++) {
      var v = el.getAttribute(ATTRS[i]);
      if (v) return v;
    }
    /* Une bulle ENFANT porte son texte dans l'élément qu'elle révèle. */
    for (var j = 0; j < ENFANTS.length; j++) {
      var b = null;
      try {
        if (el.matches(ENFANTS[j][0])) b = el.querySelector(ENFANTS[j][1]);
      } catch (e) { /* sélecteur illisible par ce navigateur */ }
      if (b) return _norme(b.textContent);
    }
    return "";
  }

  /* L'ÉTAT OUVERT EST DÉRIVÉ DU SURVOL DÉJÀ ÉCRIT, JAMAIS REDÉCLARÉ.
     ═══════════════════════════════════════════════════════════════════
     LE PIÈGE ÉVITÉ. Une règle générique du genre « à l'ouverture,
     opacité 1 » a l'air de suffire. Elle ne suffit pas : le survol ne fait
     pas qu'allumer la bulle, il annule aussi son décalage d'entrée — et ce
     décalage n'est pas le même partout (4 px sur la bulle générique, 6 px
     sur les cartes de l'accueil, avec ou sans centrage `translateX(-50%)`).
     Une valeur devinée ici laisserait la bulle deux pixels plus bas au
     doigt qu'à la souris, et se déréglerait au premier changement de page.

     CE QU'ON FAIT À LA PLACE : on lit les feuilles de la page, on retient
     les règles qui ouvrent une infobulle au survol, et on en republie une
     JUMELLE où `:hover` devient notre classe. Tout ce que le survol fait,
     l'appui du doigt le fait — sans qu'aucune valeur soit recopiée.

     LE FILTRE EST ÉTROIT, ET IL EST DÉRIVÉ LUI AUSSI. Sans lui,
     `.diff-card:hover{transform:scale(1.10)}` serait jumelée : la carte
     grossirait à chaque appui, ce qui n'a rien à voir avec une infobulle.

     MAIS IL NE PEUT PAS ÊTRE UNE LISTE DE NOMS DE CLASSES. Le dépôt en
     compte déjà trois — `.ent-tip` dans Sentinel, `.ttip` sur le panorama,
     `[data-tooltip]` sur le site public — et une quatrième arriverait sans
     que personne ne pense à ce fichier. C'est d'ailleurs une règle de la
     suite qui a trouvé les deux pages oubliées, pas une relecture.

     ON RECONNAÎT DONC UNE INFOBULLE À CE QU'ELLE FAIT : une règle qui REND
     l'attribut, c'est-à-dire qui porte `content:attr(data-tip…)`. Le
     sélecteur de cette règle, privé de ses pseudo-éléments, donne la
     « base » de la famille — `.ttip`, `.ent-tip`, `[data-tooltip]`. On
     jumelle ensuite tout ce qui survole cette base, et rien d'autre.

     LE REPLI. Une feuille d'une autre origine lève une erreur à la lecture
     de ses règles — le navigateur l'interdit. On garde alors la règle
     générique : la bulle s'ouvre, au décalage près. */
  function _toutesLesRegles() {
    var out = [];
    var feuilles = document.styleSheets;
    for (var i = 0; i < feuilles.length; i++) {
      var regles;
      try { regles = feuilles[i].cssRules; } catch (e) { continue; }
      if (!regles) continue;
      for (var j = 0; j < regles.length; j++) {
        if (regles[j].selectorText) out.push(regles[j]);
      }
    }
    return out;
  }

  /* UNE LISTE DE SÉLECTEURS SE TRAITE PARTIE PAR PARTIE — c'est un défaut
     mesuré, pas une précaution. Collée devant une liste, une pseudo-classe
     ne vise que sa DERNIÈRE partie : « [data-tooltip],[data-tip] » suivi de
     « :focus-visible{outline…} » donnait `[data-tooltip]` tout court, et
     CHAQUE infobulle de l'accueil portait un contour permanent. De même,
     jumeler en bloc `.prx-tip-icon:hover .x,.prx-tip-icon:focus .x`
     recopiait la moitié `:focus` telle quelle — sans dommage à
     l'ouverture, mais une règle de FERMETURE écrite ainsi aurait éteint la
     bulle de tout élément qui a le focus.
     On coupe aux virgules de premier niveau seulement : `:is(a, b)` et
     `[x="a,b"]` ne sont pas deux sélecteurs. */
  function _parties(sel) {
    var out = [], prof = 0, guillemet = "", debut = 0;
    for (var i = 0; i < sel.length; i++) {
      var c = sel.charAt(i);
      if (guillemet) {
        if (c === guillemet && sel.charAt(i - 1) !== "\\") guillemet = "";
      } else if (c === '"' || c === "'") {
        guillemet = c;
      } else if (c === "(" || c === "[") {
        prof++;
      } else if (c === ")" || c === "]") {
        prof--;
      } else if (c === "," && prof === 0) {
        out.push(sel.slice(debut, i).trim());
        debut = i + 1;
      }
    }
    out.push(sel.slice(debut).trim());
    return out;
  }

  /* Chaque partie d'une liste, suivie du même suffixe. */
  function _suffixer(liste, suffixe) {
    return _parties(liste).map(function (p) { return p + suffixe; }).join(",");
  }

  function _base(sel) {
    return sel.split("::")[0].split(":hover")[0].trim();
  }

  /* CE QU'« ALLUMER » VEUT DIRE, ET SON CONTRAIRE. Une bulle se montre par
     l'une de quatre propriétés, et chaque famille choisit la sienne :
     `display` (modèles, tarification, budget), `opacity` et `visibility`
     (maturité, accueil), `content` (une bulle `::after` qui n'existe pas au
     repos, comme `.ent-tip`). Éteindre, c'est rendre à CELLES QUE LE SURVOL
     ALLUME leur valeur éteinte — rien d'autre : ni position, ni couleur. */
  var ETEINT = { display: "none", visibility: "hidden", opacity: "0", content: "none" };

  function _allume(style) {
    var d = style.getPropertyValue("display");
    var v = style.getPropertyValue("visibility");
    var o = style.getPropertyValue("opacity");
    return (d !== "" && d !== "none") || v === "visible"
           || (o !== "" && parseFloat(o) > 0);
  }

  function _eteindre(style) {
    var out = "";
    for (var p in ETEINT) {
      if (style.getPropertyValue(p) !== "") out += p + ":" + ETEINT[p] + " !important;";
    }
    return out;
  }

  /* LES BULLES ENFANTS, RECONNUES À CE QU'ELLES FONT, ELLES AUSSI.
     ═══════════════════════════════════════════════════════════════════
     Leur texte n'est dans aucun attribut : il est dans un élément que le
     survol de son parent révèle — `A:hover B`. Mais un MENU déroulant
     s'écrit exactement ainsi, et le prendre pour une bulle retiendrait
     son clic. La différence est dans ce que devient B : une bulle FLOTTE
     hors du flux (`position:absolute` ou `fixed`) et se laisse TRAVERSER
     par le pointeur (`pointer-events:none`) — on la lit, on n'y clique
     pas, ouverte ou fermée. Un menu, lui, doit recevoir le clic une fois
     ouvert, et sa règle de survol le dit : le menu de l'accueil repose en
     `pointer-events:none` comme une bulle, et s'ouvre en
     `pointer-events:all`. Une première version s'arrêtait à l'état de
     repos et l'a pris pour une bulle — mesuré au navigateur.
     Rendu : [A, B], ou rien si la partie n'a pas cette forme. B est UN
     élément — ni pseudo-élément, ni pseudo-classe, ni seconde combinaison. */
  function _enfant(partie) {
    var i = partie.indexOf(":hover");
    if (i < 0) return null;
    var a = partie.slice(0, i).trim();
    var reste = partie.slice(i + ":hover".length);
    var combinaison = /^(\s*>\s*|\s+)/.exec(reste);
    if (!a || !combinaison) return null;
    var b = reste.slice(combinaison[0].length).trim();
    if (!b || /[\s>+~:]/.test(b)) return null;
    return [a, b];
  }

  /* La règle de survol ne rend pas B cliquable. */
  function _inerte(style) {
    var pe = style.getPropertyValue("pointer-events");
    return pe === "" || pe === "none";
  }

  function _flottante(styles) {
    var hors = false, traversee = false;
    for (var i = 0; i < styles.length; i++) {
      var pos = styles[i].getPropertyValue("position");
      if (pos === "absolute" || pos === "fixed") hors = true;
      if (styles[i].getPropertyValue("pointer-events") === "none") traversee = true;
    }
    return hors && traversee;
  }

  function jumelles() {
    var regles = _toutesLesRegles(), bases = {}, parSelecteur = {};
    var out = { ouvertes: [], fermees: [] }, vus = {}, i, j;
    for (i = 0; i < regles.length; i++) {
      var ps = _parties(regles[i].selectorText);
      for (j = 0; j < ps.length; j++) {
        (parSelecteur[ps[j]] = parSelecteur[ps[j]] || []).push(regles[i].style);
      }
    }
    /* Premier passage : QUI REND UN ATTRIBUT D'INFOBULLE. */
    for (i = 0; i < regles.length; i++) {
      var css = regles[i].style.cssText || "";
      var sel = regles[i].selectorText;
      if (css.indexOf("attr(data-tooltip") >= 0
          || css.indexOf("attr(data-tip") >= 0
          || sel.indexOf("[data-tooltip]") >= 0
          || sel.indexOf("[data-tip]") >= 0) {
        var b = _base(sel);
        if (b) bases[b] = true;
      }
    }
    /* …et QUI RÉVÈLE UNE BULLE ENFANT au survol de son parent. */
    for (i = 0; i < regles.length; i++) {
      if (!_allume(regles[i].style) || !_inerte(regles[i].style)) continue;
      var pr = _parties(regles[i].selectorText);
      for (j = 0; j < pr.length; j++) {
        var ab = _enfant(pr[j]);
        if (!ab || !_flottante(parSelecteur[ab[1]] || [])) continue;
        bases[ab[0]] = true;
        if (!vus[ab[0] + " " + ab[1]]) {
          vus[ab[0] + " " + ab[1]] = true;
          ENFANTS.push(ab);
        }
      }
    }
    /* Second passage : tout ce qui survole une de ces bases — partie par
       partie. Chaque règle de survol donne trois jumelles : la CLASSE qui
       ouvre au doigt, le FOCUS CLAVIER qui ouvre au clavier, et la classe
       qui FERME à la demande malgré un survol ou un focus collés. */
    for (i = 0; i < regles.length; i++) {
      var parties = _parties(regles[i].selectorText);
      for (j = 0; j < parties.length; j++) {
        var s2 = parties[j];
        if (s2.indexOf(":hover") < 0) continue;
        if (!bases[_base(s2)]) continue;
        out.ouvertes.push(s2.split(":hover").join("." + OUVERTE) + "{"
                          + regles[i].style.cssText + "}");
        out.ouvertes.push(s2.split(":hover").join(":focus-visible") + "{"
                          + regles[i].style.cssText + "}");
        var eteint = _eteindre(regles[i].style);
        if (eteint) out.fermees.push(s2.split(":hover").join("." + FERMEE)
                                     + "{" + eteint + "}");
      }
    }
    DECLENCHEURS = [SELECTEUR].concat(ENFANTS.map(function (e) { return e[0]; }))
      .filter(function (s, k, t) { return t.indexOf(s) === k; }).join(",");
    return out;
  }

  function publierLaRegle() {
    if (document.getElementById("css-bulle-ouverte")) return;
    var j = jumelles();
    var s = document.createElement("style");
    s.id = "css-bulle-ouverte";
    s.textContent = j.ouvertes.join("")
      /* LE SOCLE, qui tient même si aucune jumelle n'a pu être lue.
         `!important` n'est pas un confort : cette feuille passe après celle
         de la page, dont certaines rouvrent `[data-tooltip]::after` avec
         leurs propres `!important` de thème. Elle ne touche QUE l'ouverture,
         jamais la couleur, la position ni la largeur. */
      + "." + OUVERTE + "::after{opacity:1 !important;pointer-events:none}"
      + "." + OUVERTE + "::before{opacity:1 !important}"
      /* Ce que le doigt révèle, le clavier doit le révéler aussi. */
      + _suffixer(SELECTEUR, ":focus-visible::after") + "{opacity:1 !important}"
      + _suffixer(SELECTEUR, ":focus-visible::before") + "{opacity:1 !important}"
      + _suffixer(DECLENCHEURS, ":focus-visible") + "{outline:2px solid currentColor;"
      + "outline-offset:2px}"
      /* La région d'annonce est lue, jamais vue. `clip-path` plutôt que
         `display:none`, qui la retirerait de l'arbre d'accessibilité. */
      + "#" + REGION + "{position:absolute;width:1px;height:1px;overflow:hidden;"
      + "clip-path:inset(50%);white-space:nowrap}"
      /* LA FERMETURE EN DERNIER : à spécificité égale, la règle écrite
         après l'emporte — et elle doit l'emporter sur le socle du focus. */
      + j.fermees.join("");
    (document.head || document.documentElement).appendChild(s);
  }

  function region() {
    var r = document.getElementById(REGION);
    if (!r) {
      r = document.createElement("div");
      r.id = REGION;
      r.setAttribute("aria-live", "polite");
      r.setAttribute("aria-atomic", "true");
      (document.body || document.documentElement).appendChild(r);
    }
    return r;
  }

  var ouvert = null;
  /* L'élément dont le PROCHAIN clic doit être retenu. Il est posé à
     l'appui et consommé par le clic qui suit — jamais conservé au-delà. */
  var aRetenir = null;
  /* L'élément fermé à la demande, que le survol ou le focus rouvriraient. */
  var ferme = null;

  function lever() {
    if (!ferme) return;
    ferme.classList.remove(FERMEE);
    ferme = null;
  }

  function replier(el) {
    lever();
    el.classList.add(FERMEE);
    ferme = el;
  }

  function fermer() {
    if (!ouvert) return;
    ouvert.classList.remove(OUVERTE);
    ouvert = null;
    try { region().textContent = ""; } catch (e) { /* rien à annoncer */ }
  }

  function ouvrir(el) {
    /* Un second appui referme — À LA DEMANDE : un survol ou un focus collés
       à l'élément le garderaient ouvert sans cela. */
    if (ouvert === el) { fermer(); return replier(el); }
    fermer();
    lever();
    el.classList.add(OUVERTE);
    ouvert = el;
    try { region().textContent = texte(el); } catch (e) { /* idem */ }
  }

  /* L'ÉLÉMENT QUE L'ON TIENT QUAND ON APPUIE SUR ÉCHAP : celui que le doigt
     a ouvert, sinon celui qui a le focus, sinon celui sous la souris. Une
     bulle ouverte par le focus ou le survol doit pouvoir se fermer sans
     déplacer ni l'un ni l'autre (WCAG 1.4.13). */
  function _tenu() {
    if (ouvert) return ouvert;
    var a = document.activeElement;
    var el = a && a.closest ? a.closest(DECLENCHEURS) : null;
    if (el) return el;
    var survoles = document.querySelectorAll(":hover");
    var d = survoles.length ? survoles[survoles.length - 1] : null;
    return d && d.closest ? d.closest(DECLENCHEURS) : null;
  }

  /* CE QUI REND LA CIBLE ATTEIGNABLE AU CLAVIER. Un <div> n'est pas
     focusable ; un <button> ou un <a> l'est déjà, et lui poser un tabindex
     ne ferait que dupliquer son rang de tabulation. */
  function preparer(el) {
    if (el.hasAttribute("data-bulle-prete")) return;
    el.setAttribute("data-bulle-prete", "1");
    var focusable = /^(A|BUTTON|INPUT|SELECT|TEXTAREA)$/.test(el.tagName)
                    || el.hasAttribute("tabindex");
    if (!focusable) el.setAttribute("tabindex", "0");
  }

  function balayer() {
    var n = document.querySelectorAll(DECLENCHEURS);
    for (var i = 0; i < n.length; i++) preparer(n[i]);
    return n.length;
  }

  function demarrer() {
    publierLaRegle();
    /* LA RÉGION D'ANNONCE EXISTE DÈS LE DÉMARRAGE, VIDE.
       LE DÉFAUT MESURÉ : elle n'était créée qu'au premier texte à annoncer
       — absente au chargement de Sentinel. Or une région `aria-live`
       insérée dans le même geste que son premier contenu est souvent TUE
       par les lecteurs d'écran : ils ne l'observaient pas encore quand le
       texte y est arrivé. La première bulle ouverte était donc la seule
       qu'on risquait de ne pas entendre. */
    region();
    window.infobulles.selecteur = DECLENCHEURS;
    balayer();

    /* L'APPUI EST DÉCIDÉ AU RELÂCHER — JAMAIS AU CONTACT.
       ═══════════════════════════════════════════════════════════════════
       LE DÉFAUT MESURÉ. La décision se prenait au `pointerdown`, c'est-à-
       dire avant que le navigateur sache si le doigt APPUIE ou FAIT
       DÉFILER. Relevé au navigateur, contexte tactile :
         · un balayage commencé sur un grand déclencheur (une carte de
           l'accueil, un bloc) OUVRAIT sa bulle et annonçait son texte — le
           navigateur annule le pointeur 24 ms après le contact, trop tard ;
         · ce même balayage retenait un clic qui ne venait jamais. L'appui
           suivant trouvait la bulle « déjà ouverte », la refermait et
           LAISSAIT PASSER son clic : le bloc du rail DORA naviguait sans
           avoir été lu — exactement ce que « lire d'abord » devait empêcher ;
         · un balayage commencé AILLEURS refermait la bulle qu'on lisait,
           alors que la page ne faisait que défiler (185 px).

       CE QU'ON FAIT. Le contact ne fait que MÉMORISER le geste : quel
       pointeur, où, sur quoi. Le relâcher décide. N'est PAS un appui — et
       n'ouvre ni ne ferme rien — un geste que le navigateur annule (il
       défile), un geste qui glisse de plus de 10 px, un geste relâché sur
       une autre cible, un relâcher d'un autre doigt.

       POURQUOI PAS `click`. iOS ne synthétise pas de clic sur un <div> non
       cliquable quand l'écouteur est délégué sur `document` : une carte ou
       une pastille ne s'ouvrirait plus sur iPhone. Un `pointerup`
       sans annulation est une activation « au relâcher » (WCAG 2.5.2).

       ET TOUJOURS PAS LA SOURIS. `pointerdown` couvre le doigt, le stylet
       et la souris ; on ne retient que ce qui n'est PAS une souris, pour ne
       pas voler le survol à un poste fixe. Un clic de souris sur une carte
       doit continuer de suivre son lien, pas d'ouvrir une bulle. */
    var geste = null;
    document.addEventListener("pointerdown", function (ev) {
      geste = (ev.pointerType !== "mouse")
        ? { id: ev.pointerId, x: ev.clientX, y: ev.clientY, cible: ev.target }
        : null;
    }, true);
    /* Le navigateur a pris le geste pour lui : il défile, il zoome. */
    document.addEventListener("pointercancel", function () { geste = null; }, true);
    /* Un doigt qui glisse sans que le navigateur annule — un stylet, une
       zone en `touch-action:none` — ne fait pas un appui non plus. Passif :
       cet écouteur ne doit jamais retarder le défilement. */
    document.addEventListener("pointermove", function (ev) {
      if (geste && geste.id === ev.pointerId
          && Math.hypot(ev.clientX - geste.x, ev.clientY - geste.y) > 10) geste = null;
    }, { capture: true, passive: true });
    document.addEventListener("pointerup", function (ev) {
      if (ev.pointerType === "mouse") return;
      if (!geste || geste.id !== ev.pointerId) return;
      var g = geste; geste = null;
      var el = ev.target && ev.target.closest && ev.target.closest(DECLENCHEURS);
      var el0 = g.cible && g.cible.closest && g.cible.closest(DECLENCHEURS);
      /* Relâché sur une autre cible que celle du contact : ce n'est pas un
         appui — ni ouverture, ni fermeture. */
      if (el !== el0) return;
      /* UN `title` PLUS PROCHE QUE LE DÉCLENCHEUR PARLE SEUL. Le script des
         `title` natifs (`window.bulleTitre`, chargé après celui-ci) a son
         écouteur qui passe APRÈS celui-ci. Quand il
         répond que ce geste est le sien — un `title` inerte DANS ce
         déclencheur, ou un appui long qu'il a servi —, cet appui n'ouvre
         rien ici : il est « ailleurs ». MESURÉ AVANT, au banc : un `title`
         dans un déclencheur data-tip ouvrait les DEUX bulles, à chaque
         appui impair. Lu à l'usage : l'autre script peut être absent. */
      var bt = window.bulleTitre;
      if (el && bt && typeof bt.prend === "function" && bt.prend(ev)) el = null;
      /* Un appui AILLEURS emporte le survol collé : la fermeture demandée
         n'a plus rien à retenir. */
      if (ferme && ferme !== el) lever();
      if (!el) return fermer();
      /* UN APPUI SUR UN LIEN OU UN BOUTON DOIT RESTER UN APPUI SUR CE
         LIEN. On ouvre la bulle SANS empêcher l'action : l'infobulle
         explique, elle ne remplace pas la navigation. */
      preparer(el);
      var etaitOuvert = (ouvert === el);
      ouvrir(el);
      /* Le premier appui sur un élément qui l'a demandé retient son clic.
         Le second — celui qui referme, ou celui qui suit une lecture —
         le laisse passer. */
      aRetenir = (!etaitOuvert && el.hasAttribute(AVANT_CLIC)) ? el : null;
    }, true);

    /* LE CLIC EST RETENU ICI, ET NON À L'APPUI. `preventDefault` sur
       `pointerdown` ne supprime pas partout le clic que le navigateur
       synthétise après un appui : on attend donc ce clic-là et on l'arrête
       au vol, en capture, avant que le gestionnaire du bouton ne le voie.
       `preventDefault` a ici un second office : dans un <label for>, c'est
       lui qui empêche le libellé de donner le focus à son champ. */
    document.addEventListener("click", function (ev) {
      if (!aRetenir) return;
      var el = ev.target && ev.target.closest && ev.target.closest(DECLENCHEURS);
      if (el !== aRetenir) { aRetenir = null; return; }
      aRetenir = null;
      ev.preventDefault();
      ev.stopPropagation();
    }, true);

    /* La tabulation ouvre par `:focus-visible` (règle CSS ci-dessus) ; il
       reste à annoncer le texte, ce que le CSS ne sait pas faire. */
    document.addEventListener("focusin", function (ev) {
      var el = ev.target && ev.target.closest && ev.target.closest(DECLENCHEURS);
      if (el) { try { region().textContent = texte(el); } catch (e) {} }
    });
    document.addEventListener("focusout", function (ev) {
      /* LE FOCUS PART : la fermeture demandée tombe — SAUF si le survol tient
         encore l'élément. C'est la même règle que pour la souris qui s'en va
         (plus bas), vue de l'autre côté.
         MESURÉ AU NAVIGATEUR, AU POSTE FIXE : focus clavier sur la bulle,
         souris posée dessus, Échap, puis Tab. Sans cette garde, la bulle
         qu'on venait de fermer se ROUVRAIT sous la souris dès que le focus
         partait — sur les quatre familles éprouvées (accueil, rail DORA,
         tarification, maturité). Au doigt, le cas ne se produit pas dans
         Chromium : le survol collé part avec le défilement. */
      if (ferme && ev.target === ferme
          && !(ev.relatedTarget && ferme.contains(ev.relatedTarget))
          && !ferme.matches(":hover")) lever();
      if (ouvert !== ev.target) { try { region().textContent = ""; } catch (e) {} }
    });
    /* LA SOURIS QUI S'EN VA rend la bulle à son survol : Échap l'avait
       fermée sous le pointeur, le passage suivant doit la rouvrir. */
    document.addEventListener("pointerout", function (ev) {
      if (!ferme || ev.pointerType !== "mouse") return;
      if (!ferme.contains(ev.target)) return;
      if (ev.relatedTarget && ferme.contains(ev.relatedTarget)) return;
      if (ferme.contains(document.activeElement)) return;
      lever();
    });

    /* LES SORTIES, parce qu'une bulle ouverte qu'on ne sait pas fermer masque
       le contenu qu'elle devait éclairer : un second appui, un appui
       ailleurs (plus haut), et la touche d'échappement.

       ═══ ET PAS AU DÉFILEMENT — C'EST UN DÉFAUT MESURÉ, PAS UNE OPINION ═══
       Une première version fermait aussi au défilement. Mesure au
       navigateur, contexte tactile : la classe était POSÉE puis RETIRÉE
       dans la foulée, et la bulle ne s'ouvrait jamais. La page défile en
       `scroll-behavior:smooth` — amener une carte à l'écran émet des
       dizaines d'événements de défilement APRÈS l'appui. Sur un vrai
       téléphone, c'est le cas ordinaire : on tape une carte à demi visible,
       le navigateur l'amène à l'écran, et la bulle se referme avant d'avoir
       été lue. Fermer au défilement ne servait à rien par ailleurs : la
       bulle est positionnée par rapport à sa cible et voyage avec elle.

       LE REDIMENSIONNEMENT NE COMPTE QUE S'IL CHANGE LA LARGEUR. Sur un
       téléphone, la barre d'adresse qui se rétracte pendant un défilement
       émet un `resize` — de hauteur seulement. Le prendre pour un
       changement de mise en page ramènerait le défaut qu'on vient de
       corriger, par une autre porte.

       ÉCHAP NE FERME QU'UNE CHOSE À LA FOIS.
       LE DÉFAUT MESURÉ : une bulle ouverte au doigt dans une fenêtre
       `.mat-modal`, une frappe d'Échap — et la bulle ET la fenêtre se
       fermaient. Les deux écoutaient `keydown` sur `document` ; on perdait
       la fenêtre, et ce qu'on y avait saisi, en voulant seulement fermer
       une explication.
       CE QU'ON FAIT : on écoute sur `window`, EN CAPTURE — le tout premier
       maillon de la propagation, avant tout écouteur de `document`. Si une
       bulle était ouverte, cette frappe-là est consommée ; la suivante
       ferme la fenêtre. Une bulle ouverte par le focus ou le survol ne
       retient PAS la frappe : rien ne l'a « ouverte » au sens du doigt, et
       Échap doit continuer de fermer la fenêtre du premier coup pour qui
       tabule.
       UNE BULLE QU'ON NE VOIT PLUS NE RETIENT PAS LA FRAPPE. LE DÉFAUT
       MESURÉ (revue de robustesse, banc) : `ouvert` n'est jamais revu. Un
       déclencheur masqué juste après l'appui — un bouton qui se cache en
       ouvrant une fenêtre, un écran masqué par `go()` — gardait sa bulle
       « ouverte » : le premier Échap était avalé par une bulle invisible,
       et la fenêtre restait. On ne compte donc que ce qui est encore
       affiché : un élément masqué ou démonté n'a plus aucun rectangle. */
    window.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" || ev.key === "Esc") {
        var tenu = _tenu();
        var etaitOuverte = !!ouvert && ouvert.getClientRects().length > 0;
        fermer();
        if (tenu) replier(tenu);
        if (etaitOuverte) { ev.preventDefault(); ev.stopImmediatePropagation(); }
      }
    }, true);
    var largeur = window.innerWidth;
    window.addEventListener("resize", function () {
      if (window.innerWidth === largeur) return;
      largeur = window.innerWidth;
      fermer();
    });
    window.addEventListener("orientationchange", fermer);

    /* Les pages de Sentinel réécrivent des panneaux entiers : les cibles
       arrivées après coup doivent devenir atteignables sans rechargement. */
    try {
      new MutationObserver(balayer).observe(document.documentElement,
        { childList: true, subtree: true });
    } catch (e) { /* pas d'observateur : le balayage initial tient */ }
  }

  window.infobulles = { ouvrir: ouvrir, fermer: fermer, balayer: balayer,
                        selecteur: SELECTEUR, classe: OUVERTE, fermee: FERMEE,
                        enfants: ENFANTS };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", demarrer);
  } else {
    demarrer();
  }
})();
