/* ════════════════════════════════════════════════════════════════════════════
   FLÈCHES DE NAVIGATION VERTICALE — une même page, sans molette

   Certaines pages de ces sites font huit à quatorze fois la hauteur d'un écran.
   Revenir en haut y coûtait une dizaine de tours de molette, et rien ne
   permettait d'atteindre le pied de page — ni les sources, ni le contact.

   Ce module pose une colonne de commandes à droite :

       ⤒   haut de page
       ▲   section précédente     (seulement si la page en expose)
       ▼   section suivante
       ⤓   bas de page

   Trois principes tiennent tout le reste :

   1. RIEN QUAND CE N'EST PAS UTILE. Sous une page et demie de défilement, la
      colonne ne paraît pas. Des flèches sur une page qui tient à l'écran ne
      font pas gagner un geste : elles ajoutent du bruit.

   2. ON DÉFILE CE QUI DÉFILE VRAIMENT. Le bouton « retour en haut » de Sentinel
      visait .main sans vérifier que .main défile ; comme ce n'était pas le cas,
      il lisait un scrollTop toujours nul et n'est jamais apparu. Ici l'élément
      qui défile est CHERCHÉ, pas supposé, et rechercché quand la page change.

   3. AUCUN DOUBLON. Une page qui possède déjà un navigateur de sections — la
      barre d'onglets du Panorama, la colonne de l'accueil — ne reçoit que les
      deux bornes. Deux commandes pour la même chose donnent toujours, tôt ou
      tard, deux états contradictoires.

   Le module ne dépend de rien, ne suppose aucune palette et ne modifie aucune
   page : il lit la couleur de fond réelle et s'accorde clair ou sombre.
   ════════════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  if (window.__FLECHES) return;              /* double inclusion : on n'en pose qu'une */
  window.__FLECHES = true;

  var ID = 'fl-nav';
  var SEUIL = 1.5;      /* on ne paraît qu'au-delà d'une page et demie à parcourir */
  var MARGE_HAUT = 90;  /* en-têtes collants : viser le titre, pas le dessous */

  /* ── Ce qui défile ────────────────────────────────────────────────────────
     Le document dans l'immense majorité des cas. Mais certaines mises en page
     laissent le document immobile et font défiler un conteneur : on le trouve
     alors en cherchant le plus grand élément réellement débordant. */
  function defilant() {
    var de = document.scrollingElement || document.documentElement;
    if (de && de.scrollHeight - de.clientHeight > 40) return de;
    var meilleur = null, mieux = 0;
    var cand = document.querySelectorAll('main, .main, #main, [role="main"], .contenu, .content');
    for (var i = 0; i < cand.length; i++) {
      var el = cand[i], s = getComputedStyle(el);
      if (!/auto|scroll/.test(s.overflowY)) continue;
      var d = el.scrollHeight - el.clientHeight;
      if (d > mieux && el.clientHeight > 200) { mieux = d; meilleur = el; }
    }
    return meilleur || de;
  }

  function haut(el) { return el === document.scrollingElement || el === document.documentElement
    ? (window.pageYOffset || document.documentElement.scrollTop || 0) : el.scrollTop; }
  function vue(el) { return el === document.scrollingElement || el === document.documentElement
    ? window.innerHeight : el.clientHeight; }
  function course(el) { return Math.max(0, el.scrollHeight - vue(el)); }

  var douce = !window.matchMedia || !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function aller(el, y) {
    y = Math.max(0, Math.min(y, course(el)));
    var opt = { top: y, behavior: douce ? 'smooth' : 'auto' };
    if (el === document.scrollingElement || el === document.documentElement) window.scrollTo(opt);
    else el.scrollTo(opt);
  }

  /* ── Les sections ─────────────────────────────────────────────────────────
     On prend le premier jeu de repères qui donne au moins trois entrées : une
     page qui n'a que deux titres n'a pas de « sections » à parcourir, elle a un
     début et une fin — et les deux bornes y suffisent. */
  /* Ordre du plus explicite au plus approximatif. « main > section » et
     « main > article » rattrapent les pages qui découpent leur contenu sans
     poser d'identifiant — c'est le cas le plus fréquent ici. On ne descend
     jamais jusqu'à `section` tout court : les gabarits enveloppent l'en-tête et
     le pied dans des sections, et le pas s'arrêterait sur des repères qui ne
     sont pas du contenu. */
  var REPERES = ['[data-fl-section]', 'main > section[id]', 'section[id]',
                 'article[id]', 'main > section', 'main > article', 'main h2', 'h2'];
  function sections(el) {
    var base = haut(el);
    for (var r = 0; r < REPERES.length; r++) {
      var lot = document.querySelectorAll(REPERES[r]);
      if (lot.length < 3) continue;
      var out = [];
      for (var i = 0; i < lot.length; i++) {
        var n = lot[i];
        if (!n.offsetParent && n.offsetHeight === 0) continue;   /* replié ou masqué */
        var rect = n.getBoundingClientRect();
        var conteneur = (el === document.scrollingElement || el === document.documentElement)
          ? 0 : el.getBoundingClientRect().top;
        out.push({ y: Math.max(0, Math.round(rect.top - conteneur + base - MARGE_HAUT)),
                   nom: (n.getAttribute('data-fl-nom') || n.getAttribute('aria-label')
                      || (n.querySelector('h1,h2,h3') || n).textContent || '')
                      .replace(/\s+/g, ' ').trim().slice(0, 42) });
      }
      out.sort(function (a, b) { return a.y - b.y; });
      /* Deux repères à moins de 60 px l'un de l'autre désignent le même endroit. */
      var net = [];
      for (var k = 0; k < out.length; k++)
        if (!net.length || out[k].y - net[net.length - 1].y > 60) net.push(out[k]);
      if (net.length >= 3) return net;
    }
    return [];
  }

  /* Une page qui possède DÉJÀ un navigateur de sections ne reçoit que les
     bornes : la barre d'onglets du Panorama et la colonne de l'accueil font ce
     travail, et mieux, parce qu'elles nomment les sections en toutes lettres. */
  function dejaNavigable() {
    return !!document.querySelector('#pnav, #nav-arrows, [data-fl="bornes"]')
        || document.body.getAttribute('data-fl') === 'bornes';
  }

  /* Et une page qui possède déjà SES bornes haut/bas n'en reçoit aucune : deux
     jeux de flèches au même endroit se recouvrent. Sentinel pose #nav-top et
     #nav-bottom au bord droit, conseilprevcyber deux blocs .pagenav — capture
     à l'appui, la colonne se superposait au « module suivant » de Sentinel.
     On se retire entièrement plutôt que de chercher une place libre : un seul
     navigateur par page, c'est la seule règle qui tienne dans la durée. */
  function dejaBornee() {
    return !!(document.getElementById('nav-top') && document.getElementById('nav-bottom'))
        || !!document.querySelector('.pagenav')
        || !!document.getElementById('nav-arrows')
        || document.body.getAttribute('data-fl') === 'aucune';
  }

  /* ── Clair ou sombre ──────────────────────────────────────────────────────
     On remonte la chaîne à la recherche d'une couleur de fond OPAQUE. Sur ces
     sites elle n'existe pas : l'accueil est violet foncé par un dégradé en
     background-image, et body comme html rendent rgba(0,0,0,0). Mesuré.
     La COULEUR DU TEXTE tranche alors sans ambiguïté — une page dont le texte
     est clair a forcément un fond sombre, quel que soit le moyen employé. */
  function luminance(c) {
    var m = c && c.match(/rgba?\(([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s]+([\d.]+))?/);
    if (!m || (m[4] !== undefined && +m[4] <= 0.5)) return null;
    return (0.2126 * +m[1] + 0.7152 * +m[2] + 0.0722 * +m[3]) / 255;
  }
  function fondSombre() {
    var el = document.body;
    while (el) {
      var l = luminance(getComputedStyle(el).backgroundColor);
      if (l !== null) return l < 0.5;
      el = el.parentElement;
    }
    var t = luminance(getComputedStyle(document.body).color);
    return t !== null && t > 0.6;
  }

  /* ── Le style ─────────────────────────────────────────────────────────────
     Injecté une fois, sans toucher aux feuilles des pages. Les couleurs sont
     posées en variables pour qu'un site puisse les redéfinir sans toucher ici. */
  function style() {
    if (document.getElementById('fl-style')) return;
    var s = document.createElement('style');
    s.id = 'fl-style';
    s.textContent = [
      /* Les remises à zéro ne sont pas décoratives. Les pages stylent leur
         barre de menu par le SÉLECTEUR D'ÉLÉMENT — nav{position:fixed;left:0;
         right:0;height:56px;padding:0 32px} — et une colonne posée dans un
         <nav> héritait de left:0 et d'une hauteur imposée : elle s'étalait sur
         toute la largeur de l'écran. Mesuré : 1422 × 60 px au lieu de 36 × 165.
         L'élément est devenu un <div role="navigation">, ce qui met la colonne
         hors d'atteinte de ces règles, et les propriétés qui l'avaient déformée
         sont malgré tout remises à plat — une page peut en styler d'autres. */
      '#' + ID + '{position:fixed;right:18px;left:auto;top:50%;bottom:auto;',
      '  transform:translateY(-50%);z-index:9988;width:auto;height:auto;',
      '  margin:0;padding:0;background:none;border:0;box-shadow:none;',
      '  display:flex;flex-direction:column;gap:7px;align-items:center;justify-content:center;',
      '  opacity:0;pointer-events:none;transition:opacity .18s;',
      '  --fl-fond:rgba(255,255,255,.92);--fl-encre:#1C1C1C;--fl-bord:rgba(0,0,0,.14);',
      '  --fl-actif:rgba(0,0,0,.06)}',
      '#' + ID + '.fl-sombre{--fl-fond:rgba(14,12,26,.86);--fl-encre:#F2EFEA;',
      '  --fl-bord:rgba(255,255,255,.22);--fl-actif:rgba(255,255,255,.14)}',
      '#' + ID + '.fl-on{opacity:1;pointer-events:auto}',
      '#' + ID + ' button{width:36px;height:36px;border-radius:50%;cursor:pointer;',
      '  display:flex;align-items:center;justify-content:center;font-size:15px;line-height:1;',
      '  background:var(--fl-fond);color:var(--fl-encre);border:1px solid var(--fl-bord);',
      '  box-shadow:0 2px 10px rgba(0,0,0,.18);transition:background .15s,transform .15s,opacity .15s;',
      '  font-family:inherit;padding:0;-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px)}',
      '#' + ID + ' button:hover:not(:disabled){background:var(--fl-actif);transform:scale(1.08)}',
      '#' + ID + ' button:active:not(:disabled){transform:scale(.94)}',
      '#' + ID + ' button:focus-visible{outline:2px solid currentColor;outline-offset:2px}',
      /* Désactivé et non masqué : la commande reste lisible, elle dit
         simplement qu'on est déjà arrivé. Masquer ferait sauter la colonne. */
      '#' + ID + ' button:disabled{opacity:.32;cursor:default}',
      '#' + ID + ' .fl-sep{width:16px;height:1px;background:var(--fl-bord);margin:1px 0}',
      /* Une page sans repères n'a pas de sections à parcourir : le pas
         disparaît au lieu de proposer deux commandes qui sautent au bas. */
      '#' + ID + '.fl-sans-sections .fl-pas{display:none}',
      '#fl-etiq{position:fixed;right:62px;z-index:9988;padding:4px 10px;border-radius:6px;',
      '  background:var(--fl-fond,rgba(255,255,255,.95));color:var(--fl-encre,#1C1C1C);',
      '  border:1px solid var(--fl-bord,rgba(0,0,0,.14));font-size:11px;white-space:nowrap;',
      '  box-shadow:0 2px 10px rgba(0,0,0,.16);opacity:0;pointer-events:none;transition:opacity .18s;',
      '  max-width:34vw;overflow:hidden;text-overflow:ellipsis}',
      '#fl-etiq.fl-on{opacity:1}',
      /* Sur téléphone le défilement est PLUS pénible, pas moins : on garde les
         flèches, en plus petit et plus près du bord. */
      '@media(max-width:640px){#' + ID + '{right:9px;gap:6px}',
      '  #' + ID + ' button{width:32px;height:32px;font-size:13px}',
      '  #fl-etiq{display:none}}',
      '@media print{#' + ID + ',#fl-etiq{display:none!important}}',
      '@media(prefers-reduced-motion:reduce){#' + ID + ' button{transition:none}}'
    ].join('\n');
    (document.head || document.documentElement).appendChild(s);
  }

  /* ── La colonne ───────────────────────────────────────────────────────── */
  var boite = null, etiq = null, bHaut, bPrec, bSuiv, bBas, SECT = [], minuteur = null;

  function bouton(glyphe, nom, aide, onclick) {
    var b = document.createElement('button');
    b.type = 'button';
    b.textContent = glyphe;
    b.setAttribute('aria-label', nom);
    b.title = aide;
    b.addEventListener('click', onclick);
    return b;
  }

  function batir(avecSections) {
    style();
    /* Un <div>, pas un <nav> : les pages stylent « nav » comme leur barre de
       menu, et la colonne en héritait la largeur pleine. Le rôle ARIA porte la
       sémantique sans exposer l'élément à ces règles. */
    boite = document.createElement('div');
    boite.id = ID;
    boite.setAttribute('role', 'navigation');
    boite.setAttribute('aria-label', 'Navigation dans la page');
    bHaut = bouton('⤒', 'Haut de page',
      'Haut de page (Alt + Origine)', function () { aller(SCR, 0); });
    boite.appendChild(bHaut);
    if (avecSections) {
      bPrec = bouton('▲', 'Section précédente',
        'Section précédente (Alt + flèche haut)', function () { pas(-1); });
      bSuiv = bouton('▼', 'Section suivante',
        'Section suivante (Alt + flèche bas)', function () { pas(1); });
      bPrec.className = bSuiv.className = 'fl-pas';
      boite.appendChild(bPrec);
      var sep = document.createElement('div'); sep.className = 'fl-sep fl-pas'; boite.appendChild(sep);
      boite.appendChild(bSuiv);
    }
    bBas = bouton('⤓', 'Bas de page',
      'Bas de page (Alt + Fin)', function () { aller(SCR, course(SCR)); });
    boite.appendChild(bBas);
    document.body.appendChild(boite);

    etiq = document.createElement('div');
    etiq.id = 'fl-etiq';
    etiq.setAttribute('aria-live', 'polite');
    document.body.appendChild(etiq);

    if (fondSombre()) boite.classList.add('fl-sombre');
  }

  function montrerEtiq(txt) {
    if (!etiq || !txt) return;
    etiq.textContent = txt;
    etiq.className = 'fl-on' + (boite.classList.contains('fl-sombre') ? ' fl-sombre' : '');
    var r = boite.getBoundingClientRect();
    etiq.style.top = Math.round(r.top + r.height / 2 - 12) + 'px';
    clearTimeout(minuteur);
    minuteur = setTimeout(function () { etiq.classList.remove('fl-on'); }, 1800);
  }

  function pas(sens) {
    if (!SECT.length) { aller(SCR, sens < 0 ? 0 : course(SCR)); return; }
    var y = haut(SCR), i;
    if (sens > 0) {
      for (i = 0; i < SECT.length; i++) if (SECT[i].y > y + 8) break;
      if (i >= SECT.length) { aller(SCR, course(SCR)); montrerEtiq('Bas de page'); return; }
    } else {
      for (i = SECT.length - 1; i >= 0; i--) if (SECT[i].y < y - 8) break;
      if (i < 0) { aller(SCR, 0); montrerEtiq('Haut de page'); return; }
    }
    aller(SCR, SECT[i].y);
    montrerEtiq(SECT[i].nom);
  }

  /* ── Mise à jour ──────────────────────────────────────────────────────── */
  var SCR = null, dernierH = -1, attente = false;

  function rafraichir() {
    SCR = defilant();
    var c = course(SCR), v = vue(SCR), y = haut(SCR);
    var utile = c > v * (SEUIL - 1);
    boite.classList.toggle('fl-on', utile);
    if (!utile) return;
    bHaut.disabled = y < 8;
    bBas.disabled = y > c - 8;
    if (bPrec) { bPrec.disabled = y < 8; bSuiv.disabled = y > c - 8; }
    if (SCR.scrollHeight !== dernierH) {          /* la page a changé de taille */
      dernierH = SCR.scrollHeight;
      if (bPrec) SECT = sections(SCR);
    }
    /* Deux commandes de section sur une page qui n'en a pas sautent droit au
       bas : c'est exactement ce qu'elles promettent de ne PAS faire. Elles se
       retirent donc, et reviennent si un module en apporte — dans une
       application d'une seule page, le jeu de repères change en cours de
       route. */
    if (bPrec) boite.classList.toggle('fl-sans-sections', SECT.length < 3);
  }

  function auDefilement() {
    if (attente) return;
    attente = true;
    requestAnimationFrame(function () { attente = false; rafraichir(); });
  }

  function demarrer() {
    if (!document.body) return;
    /* Les commandes de la page peuvent être posées par un script qui s'exécute
       après celui-ci : on laisse passer un tour avant de conclure qu'il n'y en
       a pas. Sans ce délai, Sentinel recevrait la colonne parce que navInit()
       n'aurait pas encore tourné. */
    if (dejaBornee()) return;
    if (!demarrer.reporte) {
      demarrer.reporte = true;
      setTimeout(demarrer, 400);
      return;
    }
    SCR = defilant();
    batir(!dejaNavigable());
    if (bPrec) SECT = sections(SCR);
    rafraichir();
    window.addEventListener('scroll', auDefilement, { passive: true });
    window.addEventListener('resize', auDefilement, { passive: true });
    if (SCR !== document.scrollingElement && SCR !== document.documentElement)
      SCR.addEventListener('scroll', auDefilement, { passive: true });

    /* Une application d'une seule page change de contenu sans recharger : sans
       cette observation, les flèches resteraient calées sur le premier module.
       Différée, pour ne pas recalculer à chaque nœud inséré. */
    if (window.MutationObserver) {
      var t = null;
      new MutationObserver(function () {
        clearTimeout(t);
        t = setTimeout(function () { dernierH = -1; rafraichir(); }, 350);
      }).observe(document.body, { childList: true, subtree: true });
    }

    document.addEventListener('keydown', function (e) {
      if (!e.altKey || e.ctrlKey || e.metaKey) return;
      var t = e.target;
      if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return;
      if (e.key === 'ArrowUp')      { e.preventDefault(); pas(-1); }
      else if (e.key === 'ArrowDown'){ e.preventDefault(); pas(1); }
      else if (e.key === 'Home')    { e.preventDefault(); aller(SCR, 0); }
      else if (e.key === 'End')     { e.preventDefault(); aller(SCR, course(SCR)); }
    });
  }

  if (document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', demarrer);
  else demarrer();
})();
