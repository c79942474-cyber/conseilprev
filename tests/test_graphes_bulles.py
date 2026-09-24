# -*- coding: utf-8 -*-
"""LES BULLES DES GRAPHIQUES SE LISENT AU DOIGT, AU CLAVIER, ET SE FERMENT À
ÉCHAP — le pilote `grapheBulle` de sentinel.page.js (lot 4).

LE DÉFAUT MESURÉ (recette_graphes_bulles.js, colonne « avant », commit
be93b64, serveur neuf ; Pixel 7 et poste 1280 × 900) :
  · au doigt, la bulle d'un point du radar de maturité s'ouvrait et se
    refermait en 13 à 16 ms (les événements de souris de compatibilité qui
    suivent l'appui), et la page défilait jusqu'à 516 px ; 0 point sur 8
    lisible ; même chose pour le radar de risque, la courbe de tarification,
    le schéma de l'écosystème ;
  · au clavier, aucune cible : ni barre, ni mois, ni point — et onze arrêts de
    tabulation muets dans le schéma de l'écosystème, que /infobulles.js
    ramassait pour leur `data-tip` et annonçait ;
  · Échap ne fermait aucune bulle de graphique ; la bulle du radar restait
    lue par l'arbre d'accessibilité, à opacité 0 ;
  · un clic sur une barre géopolitique la DÉTRUISAIT (redessin), focus sur
    <body> ; la barre « low » porte la clé « moderate » ;
  · la bulle suivait le curseur à 14 px, ou se posait sur le point, et
    recouvrait sa propre cible : au poste, 1 graphique sur 5 ouvrait sa
    bulle sans se recouvrir.

CES RÈGLES EXÉCUTENT LE CODE. Le pilote est extrait tel quel de
sentinel.page.js et joué sous node, sur un DOM réduit à ce qu'il touche
(sélecteurs, rectangles, fenêtre visuelle, horloge maîtrisée, écouteurs
rangés par nœud et par phase comme dans un navigateur). Chaque famille de
graphique est jouée par ses VRAIES fonctions — le rendu des barres, du radar,
de la courbe, du schéma, la mise en évidence, la bulle — sur un DOM qui
analyse le HTML qu'elles écrivent. Le code des graphiques est avant la ligne
`var CRA_REF = null;` : le harnais de tests/test_memoire_ecrans.py ne
l'exécute pas, celui-ci si. La recette mesure le reste au navigateur : les
vrais gestes, la vraie géométrie, la vraie capture.
"""
import functools
import html as _html
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import tempfile

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE = shutil.which("node")


def _lire(nom):
    return io.open(os.path.join(_RACINE, nom), encoding="utf-8").read()


PAGE_JS = _lire("sentinel.page.js")
SENTINEL = _lire("sentinel.html")
BULLE_TITRE = _lire("bulle-titre.js")

DEBUT_PILOTE = "window.grapheBulle = (function(){"


def _bloc(debut, fin, src=PAGE_JS):
    """Un morceau du VRAI fichier, de `debut` à la première `fin` qui suit
    (incluse). Absent : la règle tombe en le disant."""
    i = src.find(debut)
    assert i >= 0, "%r est introuvable dans le code" % debut[:70]
    j = src.find(fin, i + len(debut))
    assert j > i, "la fin de %r est introuvable" % debut[:70]
    return src[i:j + len(fin)]


def _fonction(debut, src=PAGE_JS):
    """Une fonction déclarée à la marge : jusqu'à sa première ligne `}`."""
    return _bloc(debut, "\n}\n", src)


def _affectation(debut, src=PAGE_JS):
    """`window.x = function(…){ … };` — jusqu'à sa ligne `};`."""
    return _bloc(debut, "\n};", src)


def _node(harnais, *args):
    if not NODE:
        pytest.skip("node absent : le code ne peut pas être exécuté")
    with tempfile.TemporaryDirectory() as d:
        h = os.path.join(d, "h.js")
        io.open(h, "w", encoding="utf-8").write(harnais)
        chemins = []
        for k, a in enumerate(args):
            p = os.path.join(d, "a%d.js" % k)
            io.open(p, "w", encoding="utf-8").write(a)
            chemins.append(p)
        r = subprocess.run([NODE, h] + chemins, capture_output=True, text=True, timeout=90)
    if r.returncode != 0:
        pytest.fail("le code n'a pas tourné :\n%s" % (r.stderr or "")[-2500:])
    return json.loads(r.stdout)


def _charger(nom):
    """Un module de règles voisin, chargé À PART (ses règles ne sont pas
    recueillies une seconde fois)."""
    spec = importlib.util.spec_from_file_location(
        "_harnais_" + nom, os.path.join(_RACINE, "tests", nom + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ══════════════════════════════════════════════════════════════════════════
#  LE DOM RÉDUIT, commun aux deux harnais : des éléments qui savent `closest`,
#  `matches` (sélecteurs composés, descendance), des rectangles, le focus ;
#  et un analyseur du HTML que le code écrit dans `innerHTML`.
# ══════════════════════════════════════════════════════════════════════════

_DOM = r"""
"use strict";
let horloge = 1000000, seq = 1, minuteurs = [];
const _setTimeout = (fn, ms) => { const id = seq++; minuteurs.push({ id, at: horloge + (ms || 0), fn, every: 0 }); return id; };
const _setInterval = (fn, ms) => { const id = seq++; minuteurs.push({ id, at: horloge + ms, fn, every: ms }); return id; };
const _clear = (id) => { minuteurs = minuteurs.filter(m => m.id !== id); };
function avancer(ms) {
  const fin = horloge + ms;
  for (;;) {
    minuteurs.sort((a, b) => a.at - b.at || a.id - b.id);
    const m = minuteurs[0];
    if (!m || m.at > fin) break;
    horloge = m.at;
    if (m.every) m.at += m.every; else minuteurs.shift();
    m.fn();
  }
  horloge = fin;
}
const _Date = function () { return new Date(horloge); };
_Date.now = () => horloge;

function Texte(t) { this.nodeType = 3; this.parentNode = null; this.data = String(t); }
Object.defineProperty(Texte.prototype, "parentElement", { get() { return this.parentNode; } });
Object.defineProperty(Texte.prototype, "textContent", { get() { return this.data; }, set(v) { this.data = String(v); } });
const VIDES = { area: 1, base: 1, br: 1, col: 1, embed: 1, hr: 1, img: 1, input: 1, link: 1, meta: 1, source: 1, wbr: 1,
                circle: 1, line: 1, polygon: 1, polyline: 1, rect: 1, stop: 1, path: 1, ellipse: 1 };
const SVGS = { svg: 1, g: 1, rect: 1, circle: 1, line: 1, polygon: 1, polyline: 1, text: 1, tspan: 1, path: 1, defs: 1, marker: 1, linearGradient: 1, stop: 1 };
function El(tag, attrs) {
  this.nodeType = 1;
  this.localName = String(tag);
  this.tagName = SVGS[tag] ? String(tag) : String(tag).toUpperCase();
  this.parentNode = null; this.enfants = []; this.attrs = {}; this.rect = null; this.masque = false;
  this.ecoutes = []; this.taille = null;
  const st = {};
  st.setProperty = (k, v) => { st[k] = String(v); };
  st.getPropertyValue = (k) => st[k] || "";
  this.style = st;
  for (const k in (attrs || {})) this.attrs[k] = String(attrs[k]);
  const moi = this;
  this.classList = {
    contains: c => (moi.attrs["class"] || "").split(/\s+/).indexOf(c) >= 0,
    add: c => { if (!moi.classList.contains(c)) moi.attrs["class"] = ((moi.attrs["class"] || "") + " " + c).trim(); },
    remove: c => { moi.attrs["class"] = (moi.attrs["class"] || "").split(/\s+/).filter(x => x && x !== c).join(" "); },
    toggle: (c, f) => { const on = f === undefined ? !moi.classList.contains(c) : !!f; if (on) moi.classList.add(c); else moi.classList.remove(c); return on; },
  };
}
El.prototype.getAttribute = function (k) { return k in this.attrs ? this.attrs[k] : null; };
El.prototype.hasAttribute = function (k) { return k in this.attrs; };
El.prototype.setAttribute = function (k, v) { this.attrs[k] = String(v); };
El.prototype.removeAttribute = function (k) { delete this.attrs[k]; };
El.prototype.appendChild = function (e) { if (e.parentNode) e.parentNode.removeChild(e); e.parentNode = this; this.enfants.push(e); return e; };
El.prototype.removeChild = function (e) { this.enfants = this.enfants.filter(x => x !== e); e.parentNode = null; return e; };
El.prototype.remove = function () { if (this.parentNode) this.parentNode.removeChild(this); };
El.prototype.addEventListener = function (type) { this.ecoutes.push(type); };
El.prototype.scrollIntoView = function () { defilements.push(this.attrs.id || this.attrs["class"] || this.localName); };
El.prototype.focus = function () {
  const avant = document.activeElement;
  if (avant === this) return;
  document.activeElement = this;
  if (typeof emettre === "function") {
    emettre("focusout", evenement({ target: avant, relatedTarget: this }));
    emettre("focusin", evenement({ target: this, relatedTarget: avant }));
  }
};
El.prototype.blur = function () { if (document.activeElement === this) document.activeElement = document.body; };
Object.defineProperty(El.prototype, "parentElement", { get() { return this.parentNode && this.parentNode.nodeType === 1 ? this.parentNode : null; } });
Object.defineProperty(El.prototype, "children", { get() { return this.enfants.filter(e => e.nodeType === 1); } });
Object.defineProperty(El.prototype, "id", { get() { return this.attrs.id || ""; }, set(v) { this.attrs.id = String(v); } });
Object.defineProperty(El.prototype, "className", { get() { return this.attrs["class"] || ""; }, set(v) { this.attrs["class"] = String(v); } });
Object.defineProperty(El.prototype, "hidden", { get() { return "hidden" in this.attrs; },
  set(v) { if (v) this.attrs.hidden = ""; else delete this.attrs.hidden; } });
Object.defineProperty(El.prototype, "textContent", {
  get() { return this.enfants.map(e => e.textContent).join(""); },
  set(v) { this.enfants.forEach(e => { e.parentNode = null; }); this.enfants = []; if (v !== "" && v !== null && v !== undefined) this.appendChild(new Texte(v)); },
});
function echapper(s) { return String(s).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;"); }
function serialiser(e) {
  if (e.nodeType === 3) return e.data.replace(/&/g, "&amp;").replace(/</g, "&lt;");
  const a = Object.keys(e.attrs).map(k => " " + k + '="' + echapper(e.attrs[k]) + '"').join("");
  return "<" + e.localName + a + ">" + e.enfants.map(serialiser).join("") + (VIDES[e.localName] ? "" : "</" + e.localName + ">");
}
function decoder(s) { return String(s).replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&nbsp;/g, "\u00a0").replace(/&amp;/g, "&"); }
function analyser(html, parent) {
  const re = /<!--[\s\S]*?-->|<(\/?)([a-zA-Z][\w:-]*)((?:\s+[\w:-]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>"']+))?)*)\s*(\/?)>|([^<]+)/g;
  const pile = [parent];
  let m;
  while ((m = re.exec(html))) {
    if (m[5] !== undefined) { pile[pile.length - 1].appendChild(new Texte(decoder(m[5]))); continue; }
    if (!m[2]) continue;
    const tag = m[2];
    if (m[1]) {
      for (let i = pile.length - 1; i > 0; i--) if (pile[i].localName.toLowerCase() === tag.toLowerCase()) { pile.length = i; break; }
      continue;
    }
    const e = new El(tag);
    const ra = /([\w:-]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>"']+)))?/g;
    let a;
    while ((a = ra.exec(m[3]))) e.attrs[a[1]] = decoder(a[2] !== undefined ? a[2] : a[3] !== undefined ? a[3] : a[4] !== undefined ? a[4] : "");
    pile[pile.length - 1].appendChild(e);
    if (!m[4] && !VIDES[tag]) pile.push(e);
  }
}
Object.defineProperty(El.prototype, "innerHTML", {
  get() { return this.enfants.map(serialiser).join(""); },
  set(v) { this.enfants.forEach(e => { e.parentNode = null; }); this.enfants = []; analyser(String(v), this); },
});
Object.defineProperty(El.prototype, "outerHTML", { get() { return serialiser(this); } });
Object.defineProperty(El.prototype, "viewBox", { get() {
  const v = (this.getAttribute("viewBox") || "0 0 0 0").split(/[\s,]+/).map(Number);
  return { baseVal: { x: v[0], y: v[1], width: v[2], height: v[3] } }; } });
Object.defineProperty(El.prototype, "isConnected", {
  get() { for (let e = this; e; e = e.parentNode) if (e === racine) return true; return false; } });
El.prototype.cache = function () {
  for (let e = this; e && e.nodeType === 1; e = e.parentNode) if (e.masque || "hidden" in e.attrs || e.style.display === "none") return true;
  return false;
};
El.prototype.getBoundingClientRect = function () {
  if (this.taille) {
    if (this.cache()) return { left: 0, top: 0, right: 0, bottom: 0, width: 0, height: 0 };
    const mw = parseFloat(this.style.maxWidth);
    const w = Math.min(this.taille[0], isNaN(mw) ? Infinity : mw), h = this.taille[1];
    const l = parseFloat(this.style.left) || 0, t = parseFloat(this.style.top) || 0;
    return { left: l, top: t, right: l + w, bottom: t + h, width: w, height: h };
  }
  if (this.cache() || !this.rect) return { left: 0, top: 0, right: 0, bottom: 0, width: 0, height: 0 };
  const r = this.rect;
  return { left: r[0], top: r[1], right: r[2], bottom: r[3], width: r[2] - r[0], height: r[3] - r[1] };
};
El.prototype.getClientRects = function () {
  const r = this.getBoundingClientRect();
  return (this.cache() || (!this.rect && !this.taille)) ? [] : [r];
};
El.prototype.contains = function (o) { for (let e = o; e; e = e.parentNode) if (e === this) return true; return false; };
/* LES SÉLECTEURS : composés (balise, #id, .classe, [attr], [attr=v],
   [attr="v"]), listes, et la DESCENDANCE (espace). `:hover` et les autres
   pseudo-classes LÈVENT : aucun contrôle ne passe sur un sélecteur que le
   harnais n'a pas su lire. */
function coupe(txt, sep) {
  const out = []; let prof = 0, q = "", d = 0;
  for (let i = 0; i < txt.length; i++) {
    const c = txt[i];
    if (q) { if (c === q) q = ""; continue; }
    if (c === '"' || c === "'") q = c;
    else if (c === "[" || c === "(") prof++;
    else if (c === "]" || c === ")") prof--;
    else if (sep.test(c) && prof === 0) { out.push(txt.slice(d, i)); d = i + 1; }
  }
  out.push(txt.slice(d));
  return out.map(s => s.trim()).filter(Boolean);
}
El.prototype.compose = function (s) {
  const m = /^([a-zA-Z][\w-]*|\*)?(.*)$/.exec(s);
  if (m[1] && m[1] !== "*" && this.localName.toLowerCase() !== m[1].toLowerCase()) return false;
  let reste = m[2], p;
  const re = /^(?:\.([\w-]+)|#([\w-]+)|\[([\w-]+)(?:=(?:"([^"]*)"|'([^']*)'|([^\]]*)))?\])/;
  while (reste) {
    p = re.exec(reste);
    if (!p) throw new Error("sélecteur hors du harnais : " + s);
    if (p[1] !== undefined && !this.classList.contains(p[1])) return false;
    if (p[2] !== undefined && this.id !== p[2]) return false;
    if (p[3] !== undefined) {
      if (!this.hasAttribute(p[3])) return false;
      const v = p[4] !== undefined ? p[4] : p[5] !== undefined ? p[5] : p[6];
      if (v !== undefined && this.getAttribute(p[3]) !== v) return false;
    }
    reste = reste.slice(p[0].length);
  }
  return true;
};
El.prototype.chaine = function (parts) {
  if (!this.compose(parts[parts.length - 1])) return false;
  let reste = parts.slice(0, -1), e = this.parentNode;
  while (reste.length) {
    while (e && e.nodeType === 1 && !e.compose(reste[reste.length - 1])) e = e.parentNode;
    if (!e || e.nodeType !== 1) return false;
    reste = reste.slice(0, -1); e = e.parentNode;
  }
  return true;
};
El.prototype.matches = function (sel) { return coupe(sel, /,/).some(s => this.chaine(coupe(s, /\s/))); };
El.prototype.closest = function (sel) { for (let e = this; e && e.nodeType === 1; e = e.parentNode) if (e.matches(sel)) return e; return null; };
function tous(e) { return [].concat(...e.enfants.filter(x => x.nodeType === 1).map(x => [x].concat(tous(x)))); }
El.prototype.querySelectorAll = function (sel) { return tous(this).filter(e => e.matches(sel)); };
El.prototype.querySelector = function (sel) { return this.querySelectorAll(sel)[0] || null; };

const racine = new El("html"), head = racine.appendChild(new El("head")), body = racine.appendChild(new El("body"));
body.rect = [0, 0, 400, 800];
const defilements = [], placements = [];
function el(tag, attrs, parent, rect) { const e = (parent || body).appendChild(new El(tag, attrs)); if (rect) e.rect = rect; return e; }
function par(id) { return tous(racine).find(e => e.id === id) || null; }
"""


# ══════════════════════════════════════════════════════════════════════════
#  1. LE PILOTE, EXÉCUTÉ
# ══════════════════════════════════════════════════════════════════════════

_PILOTE = _DOM + r"""
const fs = require("fs");
const src = fs.readFileSync(process.argv[2], "utf8");

/* LES ÉCOUTEURS, rangés par NŒUD et par PHASE, appelés dans l'ordre du
   navigateur : `window` en capture, `document` en capture, `document` en
   remontée, `window` en remontée. */
const ecouteurs = {}, inscrits = [];
const inscrire = (ou) => function (type, fn, opt) {
  const capture = opt === true || !!(opt && opt.capture);
  (ecouteurs[ou + ":" + type + ":" + capture] = ecouteurs[ou + ":" + type + ":" + capture] || []).push(fn);
  inscrits.push({ ou, type, capture, passif: !!(opt && opt.passive) });
};
function emettre(type, ev) {
  for (const [ou, cap] of [["window", true], ["document", true], ["document", false], ["window", false]]) {
    for (const fn of (ecouteurs[ou + ":" + type + ":" + cap] || []).slice()) {
      fn(ev);
      if (ev.immediat) return ev;
    }
    if (ev.arrete) return ev;
  }
  return ev;
}
function emettreVV(type) { for (const fn of (ecouteurs["vv:" + type + ":false"] || [])) fn({}); }
function evenement(extra) {
  const ev = Object.assign({ retenu: false, arrete: false, immediat: false, pointerId: 1, clientX: 0, clientY: 0 }, extra);
  ev.preventDefault = () => { ev.retenu = true; };
  ev.stopPropagation = () => { ev.arrete = true; };
  ev.stopImmediatePropagation = () => { ev.immediat = true; ev.arrete = true; };
  return ev;
}
const document = { readyState: "interactive", head, body, documentElement: racine, activeElement: body,
  getElementById: id => par(id), createElement: t => new El(t),
  querySelector: s => tous(racine).find(e => e.matches(s)) || null,
  querySelectorAll: s => tous(racine).filter(e => e.matches(s)),
  addEventListener: inscrire("document") };
const visualViewport = { offsetLeft: 0, offsetTop: 0, width: 400, height: 800, scale: 1, addEventListener: inscrire("vv") };
let ibFermes = 0, btFermes = 0;
const window = { innerWidth: 400, innerHeight: 800, visualViewport, addEventListener: inscrire("window"),
  getComputedStyle: e => ({ position: e.position || "static", maxWidth: e.maxWidthCss || "none", cursor: "auto" }),
  requestAnimationFrame: fn => _setTimeout(fn, 16),
  infobulles: { selecteur: "[data-tooltip],[data-tip],.mat-tooltip-wrap", fermer() { ibFermes++; } },
  bulleTitre: { fermer() { btFermes++; } } };

/* ── LA PAGE : un exemplaire de chaque cas que le pilote doit trancher. */
const barre = el("header", { "class": "topbar" }, body, [0, 0, 400, 52]); barre.position = "fixed";
const geo = el("div", { id: "geo" }, body, [20, 280, 380, 500]);
const g1 = el("div", { id: "g1", "data-graphe": "geo", tabindex: "0" }, geo, [40, 300, 100, 480]);
const g1t = el("span", { id: "g1t" }, g1, [50, 460, 90, 478]);
const g2 = el("div", { id: "g2", "data-graphe": "geo", tabindex: "-1" }, geo, [120, 300, 180, 480]);
const g3 = el("div", { id: "g3", "data-graphe": "geo", tabindex: "-1" }, geo, [200, 300, 260, 480]);
const bGeo = el("div", { id: "geo-tip" }, body); bGeo.taille = [150, 40]; bGeo.position = "fixed"; bGeo.hidden = true;
const radar = el("svg", { id: "radar" }, body, [60, 520, 240, 560]);
const z1 = el("circle", { id: "z1", "data-graphe": "mat" }, radar, [100, 525, 130, 555]);
const z2 = el("circle", { id: "z2", "data-graphe": "mat" }, radar, [160, 525, 190, 555]);
const liste = el("div", { id: "liste" }, body, [20, 600, 380, 700]);
const r1 = el("div", { id: "r1", "data-graphe-ligne": "mat" }, liste, [20, 600, 380, 640]);
const r1t = el("span", { id: "r1t" }, r1, [30, 610, 300, 630]);
const i1 = el("span", { id: "i1", "class": "mat-tooltip-wrap", tabindex: "0" }, r1, [340, 610, 360, 630]);
const bMat = el("div", { id: "mat-tip" }, body); bMat.taille = [180, 60]; bMat.position = "fixed"; bMat.hidden = true;
const ailleurs = el("div", { id: "ailleurs" }, body, [20, 700, 380, 740]);
const tip = el("span", { id: "tip", "data-tip": "Une bulle data-tip" }, body, [20, 750, 100, 770]);
/* LE SCHÉMA : s2 a un nœud juste au-dessus (s1), s3 est collé sous la barre. */
const schema = el("svg", { id: "schema" }, body, [100, 55, 300, 280]);
const s1 = el("g", { id: "s1", "data-graphe": "eco" }, schema, [150, 150, 250, 200]);
const s2 = el("g", { id: "s2", "data-graphe": "eco" }, schema, [150, 230, 250, 260]);
const s3 = el("g", { id: "s3", "data-graphe": "eco" }, schema, [150, 60, 250, 90]);
const bEco = el("div", { id: "eco-tip" }, body); bEco.taille = [200, 40]; bEco.position = "fixed"; bEco.hidden = true;
/* UNE CIBLE CONTRE LE BORD DROIT, pour une fenêtre visuelle décalée. */
const bord = el("div", { id: "bord" }, body, [0, 300, 480, 480]);
const g4 = el("div", { id: "g4", "data-graphe": "geo" }, bord, [440, 330, 470, 480]);

/* ── LE PILOTE. */
new Function("window", "document", "setTimeout", "clearTimeout", "setInterval", "clearInterval", "Date", src)(
  window, document, _setTimeout, _clear, _setInterval, _clear, _Date);
const inscritsAuChargement = inscrits.slice();

/* CE QUI ÉCOUTE ÉCHAP APRÈS LUI : /infobulles.js et /bulle-titre.js sur
   `window` en capture (chargés après sentinel.page.js), la fenêtre modale sur
   `document`. */
let apresEchap = 0, modale = 0;
window.addEventListener("keydown", ev => { if (ev.key === "Escape") apresEchap++; }, true);
document.addEventListener("keydown", ev => { if (ev.key === "Escape") modale++; });

/* LES FAMILLES : elles notent ce que le pilote leur demande, et placent leur
   bulle par le VRAI `placer`. */
const journal = [];
function famille(nom, bulle) {
  return {
    bulle: () => bulle,
    montrer(e, source, opts) {
      journal.push({ quoi: "montrer", id: e.id, source, replacer: !!(opts && opts.replacer) });
      if (e.hasAttribute("data-graphe-ligne")) { bulle.hidden = true; return; }
      bulle.hidden = false;
      bulle.dernier = window.grapheBulle.placer(bulle, e.getBoundingClientRect(), { cible: e });
    },
    cacher(e) { journal.push({ quoi: "cacher", id: e.id }); bulle.hidden = true; },
  };
}
const GB = window.grapheBulle;
if (GB) { GB.enregistrer("geo", famille("geo", bGeo)); GB.enregistrer("mat", famille("mat", bMat)); GB.enregistrer("eco", famille("eco", bEco)); }

const pt = (type, cible, extra) => emettre(type, evenement(Object.assign({ pointerType: "touch", target: cible }, extra)));
function appui(cible, extra) { pt("pointerdown", cible, extra); avancer(60); pt("pointerup", cible, extra); avancer(20); }
function survol(vers, depuis, type) {
  if (depuis) emettre("pointerout", evenement({ pointerType: type || "mouse", target: depuis, relatedTarget: vers }));
  if (vers) emettre("pointerover", evenement({ pointerType: type || "mouse", target: vers, relatedTarget: depuis }));
}
const touche = (key, extra) => emettre("keydown", evenement(Object.assign({ key, target: document.activeElement }, extra)));
function tab(cible) { touche("Tab"); cible.focus(); }
const ouverte = (b) => !b.hidden;
const derniers = (n) => journal.slice(-n).map(j => j.quoi + ":" + j.id + (j.source ? ":" + j.source : "") + (j.replacer ? ":replacer" : ""));
function reinit() {
  if (GB) GB.fermer();
  document.activeElement = body;
  survol(null, null);
  avancer(2000);
  journal.length = 0;
}

const out = { inscrits: inscritsAuChargement, sc: {} };
function scenario(nom, fn) {
  try { reinit(); out.sc[nom] = fn(); } catch (e) { out.sc[nom] = { erreur: String(e && e.stack || e).slice(0, 700) }; }
}

scenario("appui", () => {
  const r = {};
  appui(z1); r.premier = ouverte(bMat); r.source = derniers(1)[0];
  appui(z1); r.second = ouverte(bMat);
  appui(z1); r.troisieme = ouverte(bMat);
  appui(ailleurs); r.ailleurs = ouverte(bMat);
  appui(z1); appui(bMat); r.surLaBulle = ouverte(bMat);
  appui(z2); r.autre = { z1: journal.some(j => j.quoi === "cacher" && j.id === "z1"), vue: ouverte(bMat), id: derniers(1)[0] };
  return r;
});

scenario("balayage", () => {
  const r = {};
  pt("pointerdown", z1); avancer(24); pt("pointercancel", z1); pt("pointerup", z1); r.annule = ouverte(bMat);
  pt("pointerdown", z1); pt("pointermove", z1, { clientY: 40 }); pt("pointerup", z1, { clientY: 40 }); r.glisse = ouverte(bMat);
  pt("pointerdown", z1); pt("pointermove", z1, { clientX: 3, clientY: 5 }); pt("pointerup", z1, { clientX: 3, clientY: 5 }); r.tremble = ouverte(bMat);
  reinit(); pt("pointerdown", z1); pt("pointerup", z2); r.relacheAilleurs = ouverte(bMat);
  reinit(); pt("pointerdown", z1); pt("pointerup", z1, { pointerId: 2 }); r.autreDoigt = ouverte(bMat);
  reinit(); appui(z1); pt("pointerdown", ailleurs); avancer(24); pt("pointercancel", ailleurs); pt("pointerup", ailleurs);
  r.balayageAilleurs = ouverte(bMat);
  reinit(); pt("pointerdown", z1, { pointerType: "mouse" }); pt("pointerup", z1, { pointerType: "mouse" }); r.souris = ouverte(bMat);
  return r;
});

scenario("survol", () => {
  const r = {};
  survol(z1, null, "touch"); r.doigt = ouverte(bMat);
  survol(z1, null, "mouse"); r.souris = { vue: ouverte(bMat), source: derniers(1)[0] };
  survol(ailleurs, z1); avancer(200); r.grace200 = ouverte(bMat); avancer(150); r.grace350 = ouverte(bMat);
  survol(z1, ailleurs); survol(bMat, z1); avancer(400); r.surLaBulle = ouverte(bMat);
  survol(z1, bMat); avancer(400); r.retour = ouverte(bMat);
  survol(ailleurs, z1); avancer(100); survol(z1, ailleurs); avancer(400); r.revenuAVant = ouverte(bMat);
  survol(ailleurs, z1); avancer(350); r.sortie = ouverte(bMat);
  /* L'AGITATION AILLEURS : le pointeur sorti, des éléments qui bougent sous
     lui (le bas du menu) émettent des sorties toutes les 50 ms — la grâce ne
     repart pas pour autant. */
  survol(z1, ailleurs); survol(ailleurs, z1);
  for (let k = 0; k < 7; k++) { avancer(50); survol(k % 2 ? ailleurs : tip, k % 2 ? tip : ailleurs); }
  r.agitation = ouverte(bMat);
  /* PAR LE VIDE : entre la cible et sa bulle, 8 px de rien — la grâce part,
     le survol de la bulle l'arrête. */
  survol(z1, ailleurs); survol(ailleurs, z1); avancer(100); survol(bMat, ailleurs); avancer(400); r.parLeVide = ouverte(bMat);
  reinit(); survol(g1, null, "pen"); r.stylet = ouverte(bGeo);
  appui(g1, { pointerType: "pen" }); r.styletAppui = ouverte(bGeo);
  appui(g1, { pointerType: "pen" }); r.styletSecond = ouverte(bGeo);
  return r;
});

scenario("clavier", () => {
  const r = {};
  tab(g1); r.tab = { vue: ouverte(bGeo), source: derniers(1)[0] };
  const e = touche("ArrowRight");
  r.fleche = { actif: document.activeElement.id, vue: ouverte(bGeo), retenu: e.retenu,
               tabindex: [g1, g2, g3].map(x => x.getAttribute("tabindex")).join(","), montre: derniers(1)[0] };
  touche("End"); r.fin = document.activeElement.id;
  touche("ArrowRight"); r.auBout = document.activeElement.id;
  touche("Home"); r.debut = { actif: document.activeElement.id, tabindex: [g1, g2, g3].map(x => x.getAttribute("tabindex")).join(",") };
  const alt = touche("ArrowRight", { altKey: true }); r.alt = { actif: document.activeElement.id, retenu: alt.retenu };
  document.activeElement = body; emettre("focusout", evenement({ target: g1, relatedTarget: null })); r.depart = ouverte(bGeo);
  reinit(); avancer(1200); g2.focus(); r.sansTouche = ouverte(bGeo);
  /* LE SECOND APPUI FERME ; le focus qui le suit (un élément qui ne
     l'avait pas) ne doit pas rouvrir. */
  /* …même dans la seconde qui suit une tabulation : c'est l'appui qui a
     déplacé le focus. */
  reinit(); touche("Tab"); appui(g3); appui(g3); g3.focus();
  r.apresAppui = { vue: ouverte(bGeo), arret: [g1, g2, g3].map(x => x.getAttribute("tabindex")).join(",") };
  return r;
});

scenario("echap", () => {
  const r = {};
  survol(z1, null, "mouse"); r.avant = ouverte(bMat);
  apresEchap = 0; modale = 0;
  const e1 = touche("Escape");
  r.premier = { vue: ouverte(bMat), retenu: e1.retenu, immediat: e1.immediat, apres: apresEchap, modale };
  survol(z1, z1, "mouse"); avancer(50); r.replie = ouverte(bMat);
  survol(ailleurs, z1); avancer(400); survol(z1, ailleurs); r.retour = ouverte(bMat);
  apresEchap = 0; modale = 0;
  reinit(); const e2 = touche("Escape"); r.sansBulle = { retenu: e2.retenu, apres: apresEchap, modale };
  /* UNE BULLE QU'ON NE VOIT PLUS : son écran masqué par go(). */
  reinit(); survol(z1, null, "mouse"); radar.masque = true; bMat.masque = true;
  apresEchap = 0; const e3 = touche("Escape"); r.masquee = { retenu: e3.retenu, apres: apresEchap };
  radar.masque = false; bMat.masque = false;
  /* AU CLAVIER : Échap ferme, le focus reste, la bulle ne revient pas. */
  reinit(); tab(g1); const e4 = touche("Escape"); r.clavier = { vue: ouverte(bGeo), actif: document.activeElement.id, retenu: e4.retenu };
  emettre("focusin", evenement({ target: g1, relatedTarget: body })); r.clavierRefocus = ouverte(bGeo);
  touche("ArrowRight"); r.clavierSuivant = { actif: document.activeElement.id, vue: ouverte(bGeo) };
  return r;
});

scenario("preseance", () => {
  const r = {};
  appui(z1); r.avant = ouverte(bMat);
  const j0 = journal.length;
  appui(i1); r.appuiI = { vue: ouverte(bMat), ferme: journal.slice(j0).some(j => j.quoi === "cacher" && j.id === "z1"),
                          ligne: journal.slice(j0).some(j => j.quoi === "montrer" && j.id === "r1") };
  reinit(); survol(i1, null, "mouse"); r.survolI = journal.filter(j => j.quoi === "montrer").map(j => j.id);
  reinit(); const f0 = ibFermes; i1.focus(); r.focusI = { montre: derniers(1)[0], vue: ouverte(bMat), ibFermes: ibFermes - f0 };
  i1.blur(); emettre("focusout", evenement({ target: i1, relatedTarget: null })); r.departI = derniers(1)[0];
  /* LE SURVOL D'UNE LIGNE PASSE SUR SON « i » : le survol du « i » est
     ignoré, mais le pointeur n'a pas quitté la ligne. */
  reinit(); survol(r1t, null, "mouse"); survol(i1, r1t); avancer(400);
  r.ligneI = { montre: journal.filter(j => j.quoi === "montrer").map(j => j.id), eteinte: journal.some(j => j.quoi === "cacher" && j.id === "r1") };
  survol(ailleurs, i1); avancer(350); r.ligneSortie = journal.some(j => j.quoi === "cacher" && j.id === "r1");
  reinit(); appui(r1t); r.appuiLigne = { montre: derniers(1)[0], vue: ouverte(bMat) };
  appui(r1t); r.secondAppuiLigne = derniers(1)[0];
  return r;
});

scenario("uneALaFois", () => {
  const r = {};
  let f0 = ibFermes, b0 = btFermes;
  appui(z1); r.graphe = { ib: ibFermes - f0, bt: btFermes - b0 };
  reinit(); f0 = ibFermes; b0 = btFermes; appui(r1t); r.ligne = { ib: ibFermes - f0, bt: btFermes - b0 };
  reinit(); f0 = ibFermes; b0 = btFermes; pt("pointerdown", ailleurs); avancer(24); pt("pointercancel", ailleurs);
  r.balayage = { ib: ibFermes - f0, bt: btFermes - b0 };
  reinit(); appui(z1); appui(tip); r.appuiTip = ouverte(bMat);
  return r;
});

scenario("replacement", () => {
  const r = {};
  appui(g2); const j0 = journal.length;
  emettre("scroll", evenement({ target: document })); avancer(20);
  r.defilement = journal.slice(j0).map(j => j.quoi + ":" + j.id + (j.replacer ? ":replacer" : ""));
  r.resteOuverte = ouverte(bGeo);
  const j1 = journal.length; emettreVV("resize"); emettreVV("scroll"); avancer(20);
  r.vv = journal.slice(j1).filter(j => j.replacer).length;
  g2.remove(); avancer(260); r.demontee = ouverte(bGeo);
  geo.appendChild(g2);
  reinit(); appui(g3); geo.masque = true; avancer(260); r.masquee = ouverte(bGeo); geo.masque = false;
  reinit(); r.intervalleAuRepos = minuteurs.filter(m => m.every).length;
  appui(g3); r.intervalleOuvert = minuteurs.filter(m => m.every).length;
  GB.fermer(); r.intervalleFerme = minuteurs.filter(m => m.every).length;
  return r;
});

scenario("placement", () => {
  const r = {};
  appui(g2); const b = bGeo.getBoundingClientRect(), a = g2.getBoundingClientRect();
  r.dessus = { bas: b.bottom, attendu: a.top - 8, centre: (b.left + b.right) / 2, centreCible: (a.left + a.right) / 2, dessous: bGeo.classList.contains("dessous") };
  reinit(); appui(s3); const b3 = bEco.getBoundingClientRect();
  r.sousLaBarre = { haut: b3.top, attendu: 90 + 8, dessous: bEco.classList.contains("dessous") };
  reinit(); appui(s2); const b2 = bEco.getBoundingClientRect();
  r.voisine = { haut: b2.top, attendu: 260 + 8, dessous: bEco.classList.contains("dessous") };
  reinit(); s1.remove(); appui(s2); const b2b = bEco.getBoundingClientRect(); schema.appendChild(s1);
  r.sansVoisine = { bas: b2b.bottom, attendu: 230 - 8 };
  reinit(); window.innerWidth = 491; visualViewport.width = 412; visualViewport.offsetLeft = 60;
  appui(g4); const b4 = bGeo.getBoundingClientRect();
  r.fenetreVisuelle = { droite: b4.right, borne: 60 + 412 - 8, gauche: b4.left, borneGauche: 60 + 8 };
  window.innerWidth = 400; visualViewport.width = 400; visualViewport.offsetLeft = 0;
  reinit(); bGeo.taille = [600, 40]; appui(g2); const bl = bGeo.getBoundingClientRect(); bGeo.taille = [150, 40];
  r.large = { gauche: bl.left, droite: bl.right, borneGauche: 8, borneDroite: 392 };
  return r;
});

process.stdout.write(JSON.stringify(out));
"""


@functools.lru_cache(maxsize=None)
def _pilote():
    return _node(_PILOTE, _bloc(DEBUT_PILOTE, "\n})();\n"))


def _sc(nom):
    r = _pilote()["sc"][nom]
    assert "erreur" not in r, "le scénario %s a levé : %s" % (nom, r.get("erreur"))
    return r


def test_le_pilote_est_la_et_s_inscrit_AU_CHARGEMENT():
    """LE PILOTE EST UN BLOC DE sentinel.page.js, et il écoute dès son
    exécution — pas à `DOMContentLoaded` : c'est ce qui place son Échap AVANT
    ceux d'/infobulles.js et de /bulle-titre.js (voir la règle d'ordre)."""
    inscrits = _pilote()["inscrits"]
    types = set((i["ou"], i["type"], i["capture"]) for i in inscrits)
    for attendu in [("window", "keydown", True), ("document", "pointerover", True), ("document", "pointerout", True),
                    ("document", "pointerdown", True), ("document", "pointerup", True), ("document", "pointercancel", True),
                    ("document", "focusin", False), ("document", "focusout", False), ("document", "scroll", True)]:
        assert attendu in types, "le pilote n'écoute pas %s au chargement : %s" % (attendu, sorted(types))
    passifs = [i for i in inscrits if i["ou"] == "document" and i["type"] in ("pointermove", "scroll")]
    assert passifs and all(i["passif"] for i in passifs), "un écouteur de défilement ou de glissé n'est pas passif : %s" % passifs


def test_au_DOIGT_un_appui_ouvre_le_second_ferme_un_appui_ailleurs_ferme():
    """LE CŒUR DU DÉFAUT : au doigt, la bulle d'un point s'ouvrait et se
    refermait en 13 à 16 ms. Le pilote décide AU RELÂCHER, en bascule ; un
    appui sur la bulle elle-même la laisse lire."""
    r = _sc("appui")
    assert r["premier"] and r["source"] == "montrer:z1:toucher", r
    assert not r["second"], "le second appui ne ferme pas"
    assert r["troisieme"], "le troisième appui ne rouvre pas"
    assert not r["ailleurs"], "un appui ailleurs laisse la bulle ouverte"
    assert r["surLaBulle"], "un appui SUR la bulle la ferme : on ne peut plus la lire"
    assert r["autre"]["z1"] and r["autre"]["vue"] and r["autre"]["id"] == "montrer:z2:toucher", (
        "l'appui sur une autre cible ne passe pas à elle : %r" % r["autre"])


@pytest.mark.parametrize("geste", ["annule", "glisse", "relacheAilleurs", "autreDoigt", "souris"])
def test_ce_qui_n_est_PAS_un_appui_n_ouvre_rien(geste):
    """UN BALAYAGE (le navigateur annule le pointeur), un glissé de plus de
    10 px, un relâcher sur une autre cible ou d'un autre doigt, un clic de
    souris : rien. LE TÉMOIN : un tremblement de 6 px ouvre."""
    r = _sc("balayage")
    assert r["tremble"], "un tremblement de 6 px n'ouvre plus : le contrôle ne mesurerait rien"
    assert not r[geste], "« %s » ouvre la bulle" % geste


def test_un_balayage_AILLEURS_ne_ferme_pas_la_bulle():
    """LA BULLE SURVIT AU DÉFILEMENT DU DOIGT — /infobulles.js a payé le
    contraire : amener un élément à l'écran le refermait avant lecture."""
    assert _sc("balayage")["balayageAilleurs"], "un balayage ailleurs a fermé la bulle"


def test_la_SOURIS_survole_et_la_bulle_se_SURVOLE():
    """1.4.13 : la bulle ouverte au survol reste tant que le pointeur est sur
    la cible OU sur la bulle ; elle part 300 ms après qu'il a quitté les deux.
    Le doigt, lui, ne survole pas : `pointerType` « touch » est ignoré."""
    r = _sc("survol")
    assert not r["doigt"], "un survol de type « touch » ouvre la bulle"
    assert r["souris"]["vue"] and r["souris"]["source"] == "montrer:z1:souris", r["souris"]
    assert r["grace200"], "la bulle se ferme avant 300 ms de grâce"
    assert not r["grace350"], "la bulle ne se ferme pas après 300 ms de grâce"
    assert r["surLaBulle"], "le pointeur SUR la bulle la ferme : elle n'est pas survolable"
    assert r["retour"] and r["revenuAVant"], "revenir sur la cible pendant la grâce ne garde pas la bulle"
    assert not r["sortie"], "la bulle reste après la sortie des deux"
    assert not r["agitation"], "des sorties d'éléments étrangers relancent la grâce : la bulle ne se ferme plus"
    assert r["parLeVide"], "le pointeur passé par le vide entre la cible et sa bulle la ferme"


def test_le_STYLET_garde_son_survol_et_l_appui_qui_suit_la_garde():
    """G-11. Filtré sur `pointerType !== 'touch'` : le stylet qui plane ouvre ;
    son appui sur la même cible ne la referme pas sous la pointe ; le second
    la ferme."""
    r = _sc("survol")
    assert r["stylet"], "un stylet qui plane n'ouvre pas la bulle"
    assert r["styletAppui"], "l'appui du stylet referme la bulle qu'il vient d'ouvrir en planant"
    assert not r["styletSecond"], "le second appui du stylet ne ferme pas"


def test_au_CLAVIER_un_arret_itinerant_et_les_fleches():
    """UN ARRÊT DE TABULATION PAR GRAPHIQUE : le focus clavier ouvre la bulle,
    → passe à la cible suivante (le tabindex la suit), Fin et Début vont aux
    extrémités, on ne sort pas par le bout ; Alt+flèche reste à la navigation
    entre modules. Le départ du focus ferme."""
    r = _sc("clavier")
    assert r["tab"]["vue"] and r["tab"]["source"] == "montrer:g1:clavier", r["tab"]
    f = r["fleche"]
    assert f["actif"] == "g2" and f["vue"] and f["retenu"] and f["tabindex"] == "-1,0,-1" and f["montre"] == "montrer:g2:clavier", f
    assert r["fin"] == "g3" and r["auBout"] == "g3", "Fin, puis → au bout : %r / %r" % (r["fin"], r["auBout"])
    assert r["debut"] == {"actif": "g1", "tabindex": "0,-1,-1"}, r["debut"]
    assert r["alt"]["actif"] == "g1" and not r["alt"]["retenu"], "Alt+→ est pris par le graphique : %r" % r["alt"]
    assert not r["depart"], "le départ du focus laisse la bulle ouverte"


@pytest.mark.parametrize("cas", ["sansTouche", "apresAppui"])
def test_un_focus_qui_ne_vient_pas_du_CLAVIER_n_ouvre_rien(cas):
    """LE FOCUS D'UN APPUI (l'appui a déjà décidé : un second appui fermait,
    le focus rouvrait), le focus d'il y a plus d'une seconde : pas une
    tabulation. L'appui déplace pourtant l'arrêt de tabulation sur sa cible.
    LE TÉMOIN : la tabulation ouvre (règle précédente)."""
    r = _sc("clavier")
    assert r["tab"]["vue"], "le témoin (tabulation) ne s'ouvre pas : le contrôle ne mesurerait rien"
    v = r[cas]
    vue = v["vue"] if isinstance(v, dict) else v
    if cas == "apresAppui":
        assert not vue, "le focus qui suit un appui a rouvert la bulle que l'appui venait de basculer"
        assert v["arret"] == "-1,-1,0", "l'arrêt de tabulation ne suit pas la cible touchée : %r" % v
    else:
        assert not vue, "un focus sans touche ouvre la bulle"


def test_ECHAP_ferme_la_bulle_du_graphique_ET_ELLE_SEULE():
    """A7. Écouté sur `window` en capture : quand une bulle de graphique est
    VISIBLE, la frappe est la sienne — ni /infobulles.js, ni /bulle-titre.js,
    ni la fenêtre modale ne la voient. Sans bulle, elle passe."""
    r = _sc("echap")
    assert r["avant"], "la bulle n'était pas ouverte : le contrôle ne mesurerait rien"
    p = r["premier"]
    assert not p["vue"] and p["retenu"] and p["immediat"] and p["apres"] == 0 and p["modale"] == 0, (
        "Échap ne ferme pas la bulle seule : %r" % p)
    assert r["sansBulle"] == {"retenu": False, "apres": 1, "modale": 1}, (
        "sans bulle, Échap est retenu : %r" % r["sansBulle"])


def test_ECHAP_une_bulle_qu_on_ne_voit_plus_ne_retient_pas_la_frappe():
    """LA LEÇON D'/infobulles.js : un écran masqué par `go()` masque la bulle
    avec lui ; le premier Échap ne doit pas être avalé par une bulle
    invisible."""
    r = _sc("echap")
    assert r["masquee"] == {"retenu": False, "apres": 1}, r["masquee"]


def test_apres_ECHAP_la_bulle_ne_revient_pas_tant_que_le_pointeur_ou_le_focus_reste():
    """REPLIÉE : un mouvement sur la cible ne la rouvre pas ; le pointeur
    parti puis revenu, si. Au clavier, Échap ferme, le focus reste, un
    nouveau `focusin` sur la même cible n'ouvre rien ; → ouvre la suivante."""
    r = _sc("echap")
    assert not r["replie"], "la bulle fermée par Échap se rouvre sous le pointeur"
    assert r["retour"], "après le départ du pointeur, la bulle ne se rouvre plus"
    assert not r["clavier"]["vue"] and r["clavier"]["actif"] == "g1" and r["clavier"]["retenu"], r["clavier"]
    assert not r["clavierRefocus"], "le focus resté sur la cible rouvre la bulle fermée par Échap"
    assert r["clavierSuivant"] == {"actif": "g2", "vue": True}, r["clavierSuivant"]


def test_la_PRESEANCE_le_i_d_une_ligne_garde_sa_bulle():
    """§4.1 : un déclencheur d'/infobulles.js DANS une cible (le « i » d'une
    ligne du radar de maturité) l'emporte. Son appui est un appui AILLEURS
    pour le pilote (la bulle du graphique se ferme, la ligne ne s'allume pas
    par lui) ; son survol est ignoré ; son FOCUS allume le point de la ligne,
    sans bulle, et sans fermer la sienne."""
    r = _sc("preseance")
    assert r["avant"], "la bulle n'était pas ouverte : le contrôle ne mesurerait rien"
    assert not r["appuiI"]["vue"] and r["appuiI"]["ferme"] and not r["appuiI"]["ligne"], r["appuiI"]
    assert r["survolI"] == [], "le survol du « i » allume sa ligne : %r" % r["survolI"]
    f = r["focusI"]
    assert f["montre"] == "montrer:r1:clavier" and not f["vue"] and f["ibFermes"] == 0, (
        "le focus du « i » : %r" % f)
    assert r["departI"] == "cacher:r1", "le départ du focus du « i » n'éteint pas le point : %r" % r["departI"]
    assert r["ligneI"] == {"montre": ["r1"], "eteinte": False}, (
        "le pointeur passé de la ligne à son « i » éteint la ligne : %r" % r["ligneI"])
    assert r["ligneSortie"], "le pointeur sorti de la ligne ne l'éteint pas"


def test_une_LIGNE_allume_son_point_sans_bulle_et_se_bascule():
    r = _sc("preseance")
    assert r["appuiLigne"] == {"montre": "montrer:r1:toucher", "vue": False}, r["appuiLigne"]
    assert r["secondAppuiLigne"] == "cacher:r1", r["secondAppuiLigne"]


def test_UNE_BULLE_A_LA_FOIS_ouvrir_un_graphique_ferme_les_deux_autres():
    """OUVRIR ICI FERME /infobulles.js ET /bulle-titre.js — pas une ligne (sa
    lumière n'est pas une bulle, et c'est le focus de son « i » qui
    l'allume), pas un balayage (il n'ouvre rien). Et un appui sur un
    déclencheur data-tip est un appui ailleurs pour le pilote."""
    r = _sc("uneALaFois")
    assert r["graphe"] == {"ib": 1, "bt": 1}, r["graphe"]
    assert r["ligne"] == {"ib": 0, "bt": 0}, r["ligne"]
    assert r["balayage"] == {"ib": 0, "bt": 0}, r["balayage"]
    assert not r["appuiTip"], "un appui sur un déclencheur data-tip laisse la bulle du graphique ouverte"


def test_le_DEFILEMENT_replace_la_bulle_et_une_cible_disparue_la_ferme():
    """LE DÉFILEMENT REPLACE, IL NE FERME JAMAIS (G-8) ; la fenêtre visuelle
    aussi. Une cible démontée (graphique redessiné) ou masquée (écran quitté
    par `go()`) ferme sa bulle en 250 ms. L'intervalle ne tourne que bulle
    ouverte."""
    r = _sc("replacement")
    assert r["defilement"] == ["montrer:g2:replacer"] and r["resteOuverte"], r["defilement"]
    assert r["vv"] >= 1, "la fenêtre visuelle qui bouge ne replace pas la bulle"
    assert not r["demontee"] and not r["masquee"], "une cible démontée ou masquée garde sa bulle : %r" % r
    assert (r["intervalleAuRepos"], r["intervalleOuvert"], r["intervalleFerme"]) == (0, 1, 0), r


def test_la_bulle_est_AU_DESSUS_centree_et_passe_DESSOUS_sous_la_barre_du_haut():
    """AU-DESSUS DE LA CIBLE, à 8 px, centrée ; DESSOUS quand la barre du haut
    (fixe, 52 px) ne laisse pas la place — mesuré au Pixel 7 : une bulle
    « au-dessus » d'un point en haut de l'écran passait sous la barre."""
    r = _sc("placement")
    d = r["dessus"]
    assert d["bas"] == d["attendu"] and abs(d["centre"] - d["centreCible"]) <= 1 and not d["dessous"], d
    s = r["sousLaBarre"]
    assert s["haut"] == s["attendu"] and s["dessous"], "la bulle ne passe pas dessous : %r" % s


def test_la_bulle_evite_ses_VOISINES_et_reste_dans_la_FENETRE_VISUELLE():
    """DESSOUS QUAND DESSUS RECOUVRIRAIT UNE VOISINE que dessous épargne (le
    schéma de l'écosystème a des nœuds sous des nœuds) — LE TÉMOIN : sans la
    voisine, dessus. Bornée à la fenêtre VISUELLE (491 de mise en page pour
    412 visibles au Pixel 7) et à sa largeur."""
    r = _sc("placement")
    assert r["voisine"]["haut"] == r["voisine"]["attendu"] and r["voisine"]["dessous"], r["voisine"]
    assert r["sansVoisine"]["bas"] == r["sansVoisine"]["attendu"], r["sansVoisine"]
    f = r["fenetreVisuelle"]
    assert f["droite"] <= f["borne"] and f["gauche"] >= f["borneGauche"], "hors de la fenêtre visuelle : %r" % f
    lg = r["large"]
    assert lg["gauche"] >= lg["borneGauche"] and lg["droite"] <= lg["borneDroite"], "trop large pour la fenêtre : %r" % lg


# ══════════════════════════════════════════════════════════════════════════
#  2. LES FAMILLES, EXÉCUTÉES PAR LEURS VRAIES FONCTIONS
# ══════════════════════════════════════════════════════════════════════════

_FAMILLES = _DOM + r"""
const fs = require("fs");
const vm = require("vm");
const code = fs.readFileSync(process.argv[2], "utf8");
const scen = fs.readFileSync(process.argv[3], "utf8");
function emettre() {}
function evenement(x) { return x; }
const document = { readyState: "interactive", head, body, documentElement: racine, activeElement: body,
  getElementById: id => par(id), createElement: t => new El(t), createElementNS: (ns, t) => new El(t),
  createTextNode: t => new Texte(t),
  querySelector: s => tous(racine).find(e => e.matches(s)) || null,
  querySelectorAll: s => tous(racine).filter(e => e.matches(s)),
  addEventListener() {} };
const contexte = { document, console,
  setTimeout: _setTimeout, clearTimeout: _clear, setInterval: _setInterval, clearInterval: _clear, Date: _Date,
  innerWidth: 1280, innerHeight: 900, visualViewport: { offsetLeft: 0, offsetTop: 0, width: 1280, height: 900, scale: 1 },
  getComputedStyle: e => ({ display: e.style.display || "block", position: "fixed", maxWidth: "none", cursor: "auto" }),
  requestAnimationFrame: fn => _setTimeout(fn, 16),
  el, par, tous, avancer, defilements, placements, body, El, sortie: {} };
contexte.window = contexte;
contexte.grapheBulle = { defs: {}, enregistrer(f, d) { this.defs[f] = d; },
  placer(b, r, o) { placements.push({ bulle: b.id, r: { left: r.left, top: r.top, right: r.right, bottom: r.bottom },
    x: o && o.x !== undefined ? o.x : null, cible: o && o.cible ? o.cible : null }); return {}; },
  fermer() {} };
vm.createContext(contexte);
function essai(nom, fn) { try { contexte.sortie[nom] = fn(); } catch (e) { contexte.sortie[nom] = { erreur: String(e && e.stack || e).slice(0, 700) }; } }
contexte.essai = essai;
try { vm.runInContext(code, contexte); } catch (e) { contexte.sortie.chargement = { erreur: String(e && e.stack || e).slice(0, 700) }; }
vm.runInContext(scen, contexte);
process.stdout.write(JSON.stringify(contexte.sortie));
"""


def _famille(code, scen):
    return _node(_FAMILLES, code, scen)


def _essai(sortie, nom):
    assert "chargement" not in sortie, "le code n'a pas pu être chargé : %s" % sortie["chargement"]
    r = sortie.get(nom)
    assert r is not None, "le scénario %s n'a rien rendu" % nom
    assert not (isinstance(r, dict) and "erreur" in r), "le scénario %s a levé : %s" % (nom, r["erreur"])
    return r


def _registration(famille):
    """L'enregistrement d'une famille auprès du pilote, tel qu'écrit."""
    return _bloc("if(window.grapheBulle) window.grapheBulle.enregistrer('%s', {" % famille, "\n});")


# ── 2 a. LES BARRES GÉOPOLITIQUES ───────────────────────────────────────

_GEO_SCEN = r"""
essai("rendu", () => {
  const cols = document.querySelectorAll("#geo-chart .geo-bar-col");
  const chart = par("geo-chart");
  return { n: cols.length, attrs: cols.map(c => c.attrs), ecoutes: cols.map(c => c.ecoutes),
           chart: { role: chart.getAttribute("role"), label: chart.getAttribute("aria-label") },
           grille: chart.querySelectorAll(".geo-chart-grid").map(g => g.getAttribute("aria-hidden")),
           titres: tous(chart).filter(e => e.hasAttribute("title") || e.localName === "title").length };
});
essai("bulles", () => {
  const def = window.grapheBulle.defs.geo, tip = par("geo-tooltip");
  return document.querySelectorAll("#geo-chart .geo-bar-col").map(c => {
    placements.length = 0; def.montrer(c, "toucher");
    const p = placements[0] || {};
    return { cle: c.getAttribute("data-geo-key"), texte: tip.textContent, display: tip.style.display,
             cible: p.cible === c, bulle: p.bulle };
  });
});
essai("cacher", () => { const def = window.grapheBulle.defs.geo; def.cacher(null); return par("geo-tooltip").style.display; });
essai("puces", () => {
  window.geoFilterRisk("critical", par("f-critical"));
  const a = document.querySelectorAll(".geo-filter-chip[data-filter]").map(c => c.getAttribute("data-filter") + "=" + c.getAttribute("aria-pressed") + (c.classList.contains("on") ? "*" : ""));
  window.geoFilterCat("CHANGEMENT POLITIQUE", par("c-pol"));
  const b = document.querySelectorAll(".geo-filter-chip[data-cat]").map(c => c.getAttribute("data-cat").slice(0, 5) + "=" + c.getAttribute("aria-pressed"));
  return { risque: a, frise: b, doc: par("doc").classList.contains("on") };
});
essai("refocus", () => {
  const cols = document.querySelectorAll("#geo-chart .geo-bar-col");
  cols.forEach(c => c.setAttribute("tabindex", c.getAttribute("data-geo-key") === "elevated" ? "0" : "-1"));
  const avant = cols.find(c => c.getAttribute("data-geo-key") === "high");
  document.activeElement = avant;
  window.geoFilterRisk("all", par("f-all"));
  const apres = document.querySelectorAll("#geo-chart .geo-bar-col");
  const a = document.activeElement;
  return { actif: a && a.getAttribute ? a.getAttribute("data-geo-key") : null, recree: a !== avant, connecte: !!a && a.isConnected,
           arret: apres.filter(c => c.getAttribute("tabindex") === "0").map(c => c.getAttribute("data-geo-key")) };
});
"""

_GEO_PAGE = r"""
const chartEl = el("div", { id: "geo-chart", "class": "geo-chart" });
el("div", { id: "geo-tooltip", "class": "geo-tooltip" });
for (const k of ["all", "critical", "high", "moderate"]) el("button", { id: "f-" + k, "class": "geo-filter-chip" + (k === "all" ? " on" : ""), "data-filter": k, "aria-pressed": k === "all" ? "true" : "false" });
for (const [id, k] of [["c-all", "all"], ["c-vig", "ENTRÉE EN VIGUEUR"], ["c-pol", "CHANGEMENT POLITIQUE"], ["c-tec", "RUPTURE TECHNOLOGIQUE"]]) el("button", { id, "class": "geo-filter-chip" + (k === "all" ? " on" : ""), "data-cat": k, "aria-pressed": k === "all" ? "true" : "false" });
/* Une carte de document qui porte aussi `data-cat` : un filtre de la frise ne la touche pas. */
el("div", { id: "doc", "class": "doc-card on", "data-cat": "guide" });
"""


@functools.lru_cache(maxsize=None)
def _geo():
    iife = _bloc("(function(){\n\n/* DONNEES */\n", "geoRenderTL();\n\n})();")
    return _famille(_GEO_PAGE + iife, _GEO_SCEN)


def test_les_barres_sont_des_IMAGES_NOMMEES_sans_ecouteur_de_souris():
    """A2, §4.2, G-7. LE DÉFAUT : chaque barre écoutait `mousemove`,
    `mouseleave` et `click` — le clic appelait un filtre qui ne filtre rien et
    DÉTRUISAIT la barre (mesuré : focus sur <body>). Exécuté : le vrai
    `geoRenderChart`. Chaque barre porte `data-graphe="geo"`, une clé
    propre, `role="img"`, un nom « niveau : nombre — description », et
    n'écoute plus rien."""
    r = _essai(_geo(), "rendu")
    assert r["n"] == 5, "%d barres" % r["n"]
    assert all(e == [] for e in r["ecoutes"]), "des barres écoutent encore : %r" % r["ecoutes"]
    for a in r["attrs"]:
        assert a.get("data-graphe") == "geo" and a.get("role") == "img", a
        assert re.match(r"^\S.* : \d+ juridictions? — \S", a.get("aria-label", "")), a.get("aria-label")
    assert len(set(a.get("data-geo-key") for a in r["attrs"])) == 5, (
        "deux barres partagent une clé : %r" % [a.get("data-geo-key") for a in r["attrs"]])
    assert r["chart"] == {"role": "group", "label": "Répartition des juridictions par niveau de risque"}, r["chart"]
    assert r["grille"] and all(g == "true" for g in r["grille"]), "la graduation se lit : %r" % r["grille"]


def test_les_barres_ont_UN_arret_de_tabulation():
    r = _essai(_geo(), "rendu")
    assert [a.get("tabindex") for a in r["attrs"]] == ["0", "-1", "-1", "-1", "-1"], [a.get("tabindex") for a in r["attrs"]]


def test_chaque_barre_montre_SES_donnees():
    """LA CLÉ D'UNE BARRE EST SA CLÉ. `d.key` vaut « moderate » pour « low » et
    « moderate », « high » pour « elevated » et « high » : y chercher la barre
    montrait la bulle « Modéré » sur la barre « low ». Exécuté : la vraie
    famille « geo », barre par barre ; la bulle s'ancre à la barre."""
    r = _essai(_geo(), "bulles")
    attendus = {"low": "Faible", "moderate": "Modéré", "elevated": "Élevé", "high": "Haut", "critical": "Critique"}
    assert [b["cle"] for b in r] == list(attendus), [b["cle"] for b in r]
    for b in r:
        assert b["texte"].startswith(attendus[b["cle"]] + " — "), "barre %s : bulle « %s »" % (b["cle"], b["texte"])
        assert b["display"] == "block" and b["cible"] and b["bulle"] == "geo-tooltip", b
    assert _essai(_geo(), "cacher") == "none"


def test_les_puces_de_filtre_disent_laquelle_est_PRESSEE():
    """A2 : les puces sont des boutons à bascule ; le filtre tient
    `aria-pressed` à jour, sur SES puces seulement (une carte de document qui
    porte `data-cat` n'est pas une puce)."""
    r = _essai(_geo(), "puces")
    assert r["risque"] == ["all=false", "critical=true*", "high=false", "moderate=false"], r["risque"]
    assert r["frise"] == ["all=false", "ENTRÉ=false", "CHANG=true", "RUPTU=false"], r["frise"]
    assert r["doc"], "le filtre de la frise a éteint une carte de document"


def test_apres_un_redessin_le_focus_et_l_arret_RESTENT_sur_la_meme_barre():
    """P8, en filet : `innerHTML = ''` détruit la barre focalisée. La barre de
    même clé reprend le focus, et l'arrêt de tabulation reste où il était."""
    r = _essai(_geo(), "refocus")
    assert r["actif"] == "high" and r["recree"] and r["connecte"], r
    assert r["arret"] == ["elevated"], r["arret"]


def test_les_puces_sont_des_BOUTONS_a_bascule_dans_la_page():
    """<span onclick> ne prend ni le focus ni Entrée : huit <button type="button"
    aria-pressed>, la même classe (le même style)."""
    puces = re.findall(r"<(\w+)([^>]*class=\"geo-filter-chip[^\"]*\"[^>]*)>", SENTINEL)
    assert len(puces) == 8, "%d puces" % len(puces)
    for tag, attrs in puces:
        assert tag == "button" and 'type="button"' in attrs and re.search(r'aria-pressed="(true|false)"', attrs), (tag, attrs)


# ── 2 b. LE RADAR DE MATURITÉ ───────────────────────────────────────────

_MAT_SCEN = r"""
essai("rendu", () => {
  const holder = el("div", { id: "mat-radar-holder" });
  holder.innerHTML = matRadar({ explicabilite: 3, controlabilite: 2, transparence: 4, surete: 1, equite: 5, gouvernance: 2, confidentialite: 3, robustesse: 4 });
  const svg = holder.querySelector("svg");
  const liste = el("div", { "class": "mat-pillars-list" });
  MAT_PILLARS.forEach(p => { const r = el("div", { "class": "mat-pillar-row", "data-graphe-ligne": "mat", "data-pillar": p.id, id: "ligne-" + p.id }, liste, [0, 0, 10, 10]);
    el("div", { "class": "mat-pillar-fill matq-bar", "data-pillar": p.id }, r); });
  holder.querySelectorAll(".mat-radar-hitzone").forEach(z => { z.rect = [10, 10, 30, 30]; });
  return { svg: svg.attrs, zones: holder.querySelectorAll(".mat-radar-hitzone").map(z => z.attrs),
           tip: (par("mat-radar-tooltip") || { attrs: null }).attrs,
           titres: tous(holder).filter(e => e.hasAttribute("title") || e.localName === "title").length };
});
function etat(pid) {
  const tip = par("mat-radar-tooltip"), pt = document.querySelector('.mat-radar-pt[data-pillar="' + pid + '"]');
  return { defile: defilements.length, on: tip.classList.contains("on"), point: pt.getAttribute("r"),
           ligne: par("ligne-" + pid).classList.contains("mat-pillar-row-highlighted"),
           placer: placements.map(p => p.cible && p.cible.getAttribute ? p.cible.getAttribute("class") + "/" + p.cible.getAttribute("data-pillar") : null) };
}
function essaie(nom, fn) { essai(nom, () => { window.matRadarUnhighlight(); defilements.length = 0; placements.length = 0; fn(); return etat("surete"); }); }
essaie("defaut", () => window.matRadarHighlight("surete", null));
essaie("defilerSouris", () => window.matRadarHighlight("surete", null, { defiler: true }));
essaie("sansBulle", () => window.matRadarHighlight("surete", null, { bulle: false }));
const zone = () => document.querySelector('.mat-radar-hitzone[data-pillar="surete"]');
essaie("familleSouris", () => window.grapheBulle.defs.mat.montrer(zone(), "souris"));
essaie("familleDoigt", () => window.grapheBulle.defs.mat.montrer(zone(), "toucher"));
essaie("familleClavier", () => window.grapheBulle.defs.mat.montrer(zone(), "clavier"));
essaie("familleReplacer", () => window.grapheBulle.defs.mat.montrer(zone(), "souris", { replacer: true }));
essaie("familleLigne", () => window.grapheBulle.defs.mat.montrer(par("ligne-surete"), "souris"));
essai("familleCacher", () => { window.grapheBulle.defs.mat.montrer(zone(), "toucher"); window.grapheBulle.defs.mat.cacher(zone()); return etat("surete"); });
"""


@functools.lru_cache(maxsize=None)
def _mat():
    code = (_bloc("var MAT_PILLARS = [", "];") + "\n"
            + _bloc("var MAT_PILLAR_COLORS = {", "};") + "\nwindow.MAT_PILLAR_COLORS = MAT_PILLAR_COLORS;\n"
            + _fonction("function matRadar(pillars){") + "\n"
            + _affectation("window.matRadarHighlight = function(") + "\n"
            + _affectation("window.matRadarUnhighlight = function(){") + "\n")
    if "enregistrer('mat'" in PAGE_JS:
        code += _registration("mat") + "\n"
    return _famille(code, _MAT_SCEN)


def test_le_radar_de_maturite_est_UNE_image_nommee_et_ses_zones_ne_prennent_pas_le_focus():
    """A4, G-4. Exécuté : le vrai `matRadar`. Le svg est une image au nom de
    synthèse ; les zones ne sont ni focalisables ni nommées, et n'écoutent
    plus la souris : le pilote les sert (`data-graphe="mat"`). La bulle est
    muette en permanence (A10)."""
    r = _essai(_mat(), "rendu")
    assert r["svg"].get("role") == "img" and "liste" in (r["svg"].get("aria-label") or ""), r["svg"]
    assert len(r["zones"]) == 8
    for z in r["zones"]:
        assert z.get("data-graphe") == "mat" and "tabindex" not in z and not any(k.startswith("onmouse") for k in z), z
    assert r["tip"] and r["tip"].get("aria-hidden") == "true", r["tip"]


def test_mettre_en_evidence_ne_fait_PLUS_defiler_la_page():
    """P3, G-1. MESURÉ AU PIXEL 7 (avant) : un appui sur un point faisait
    défiler la page jusqu'à 516 px, le point et la bulle sortaient de
    l'écran. Exécuté : `matRadarHighlight` ne défile que si on le lui
    demande — et le pilote ne le demande qu'à la souris, qui survole le radar
    à côté de la liste."""
    m = _mat()
    assert _essai(m, "defaut")["defile"] == 0, "matRadarHighlight défile sans qu'on le demande"
    assert _essai(m, "defilerSouris")["defile"] == 1, "le défilement demandé (souris) ne se fait plus"
    assert _essai(m, "familleSouris")["defile"] == 1, "la famille ne fait plus défiler à la souris"
    for cas in ("familleDoigt", "familleClavier", "familleReplacer", "familleLigne"):
        assert _essai(m, cas)["defile"] == 0, "%s fait défiler la page" % cas


def test_le_point_a_sa_bulle_la_ligne_non():
    """Une LIGNE de la liste allume son point, sans bulle — elle dit déjà tout.
    Le point montre la bulle, ancrée à sa zone."""
    m = _mat()
    for cas in ("defaut", "familleDoigt"):
        e = _essai(m, cas)
        assert e["on"] and e["point"] == "7" and e["ligne"], (cas, e)
        assert e["placer"] == ["mat-radar-hitzone/surete"], "la bulle n'est pas ancrée à la zone du point : %r" % e["placer"]
    for cas in ("sansBulle", "familleLigne"):
        e = _essai(m, cas)
        assert not e["on"] and e["point"] == "7" and e["ligne"] and e["placer"] == [], (cas, e)
    c = _essai(m, "familleCacher")
    assert not c["on"] and not c["ligne"], c


def test_la_ligne_de_pilier_n_ecoute_plus_la_souris_et_se_declare():
    """§4.2 : la ligne portait `onmouseenter`/`onmouseleave`. Elle se déclare
    au pilote (`data-graphe-ligne="mat"`, son pilier), sans rôle ni tabindex :
    elle contient le « i » focalisable."""
    m = re.search(r"return '<div class=\"mat-pillar-row\"([^>]*)>", PAGE_JS)
    assert m, "le gabarit de la ligne de pilier est introuvable"
    attrs = m.group(1)
    assert 'data-graphe-ligne="mat"' in attrs and "data-pillar=" in attrs, attrs
    assert "onmouse" not in attrs and "tabindex" not in attrs and "role=" not in attrs, attrs


# ── 2 c. LE RADAR DE RISQUE ─────────────────────────────────────────────

_RISQUE_SCEN = r"""
const holder = el("div", { "class": "tbl-wrap" });
const svg = el("svg", { "class": "radar-svg", id: "radar-svg" }, holder);
el("div", { id: "radar-scores", "class": "reg-stack" });
window.radarComputeDimensionScores = () => ({ dims: { gouvernance: .5, transparence: .57, securite: .4, donnees: .6, supervision: .3, droits: .7 }, riskScores: {}, regFactor: { count: 0 } });
window.radarComputeAverage = () => ({ gouvernance: .4, transparence: .4, securite: .4, donnees: .4, supervision: .4, droits: .4 });
window.SYSTEMIC_RISKS = [];
essai("rendu", () => {
  radarRenderAll();
  return { zones: svg.querySelectorAll(".radar-hitzone").map(z => z.attrs), tip: (par("radar-tooltip") || { attrs: null }).attrs,
           lignes: document.querySelectorAll("#radar-scores .reg-item").map(r => r.attrs),
           titres: tous(svg).concat(tous(par("radar-scores"))).filter(e => e.hasAttribute("title") || e.localName === "title").length };
});
function etat(dim) {
  const tip = par("radar-tooltip");
  return { on: tip.classList.contains("on"),
           lignes: document.querySelectorAll("#radar-scores .mat-pillar-row-highlighted").map(r => r.getAttribute("data-dim")),
           placer: placements.map(p => p.cible && p.cible.getAttribute ? p.cible.getAttribute("class") + "/" + p.cible.getAttribute("data-dim") : null) };
}
function essaie(nom, fn) { essai(nom, () => { window.radarUnhighlight(); placements.length = 0; fn(); return etat("transparence"); }); }
essaie("point", () => window.grapheBulle.defs.risque.montrer(svg.querySelector('.radar-hitzone[data-dim="transparence"]'), "toucher"));
essaie("ligne", () => window.grapheBulle.defs.risque.montrer(document.querySelector('#radar-scores .reg-item[data-dim="transparence"]'), "toucher"));
essai("cacher", () => { window.grapheBulle.defs.risque.montrer(svg.querySelector('.radar-hitzone[data-dim="transparence"]'), "toucher");
  window.grapheBulle.defs.risque.cacher(null); return etat("transparence"); });
"""


@functools.lru_cache(maxsize=None)
def _risque():
    code = (_bloc("var RADAR_DIMENSIONS = [", "];") + "\n"
            + _bloc("var RADAR_DIM_COLORS = {", "};") + "\nwindow.RADAR_DIM_COLORS = RADAR_DIM_COLORS;\n"
            + _fonction("function radarRenderSVG(you, avg){") + "\n"
            + _affectation("window.radarHighlight = function(") + "\n"
            + _affectation("window.radarUnhighlight = function(){") + "\n"
            + _fonction("function radarRenderAll(){") + "\n")
    if "enregistrer('risque'" in PAGE_JS:
        code += _registration("risque") + "\n"
    return _famille(code, _RISQUE_SCEN)


def test_le_radar_de_risque_se_declare_au_pilote_et_sa_bulle_est_muette():
    """R2, §4.2. Exécuté : les vrais `radarRenderSVG` et `radarRenderAll`.
    Les zones (`data-graphe="risque"`) et les lignes (`data-dim`,
    `data-graphe-ligne`) n'écoutent plus la souris ; la bulle, créée à la
    volée, naît `aria-hidden`."""
    r = _essai(_risque(), "rendu")
    assert len(r["zones"]) == 6 and len(r["lignes"]) == 6, r
    for z in r["zones"]:
        assert z.get("data-graphe") == "risque" and "tabindex" not in z and not any(k.startswith("onmouse") for k in z), z
    for l in r["lignes"]:
        assert l.get("data-graphe-ligne") == "risque" and l.get("data-dim") and not any(k.startswith("onmouse") for k in l), l
    assert r["tip"] and r["tip"].get("aria-hidden") == "true", r["tip"]


def test_le_radar_de_risque_a_UN_nom_de_synthese():
    m = re.search(r'<svg class="radar-svg"[^>]*id="radar-svg"[^>]*>', SENTINEL)
    assert m and 'role="img"' in m.group(0) and re.search(r'aria-label="Radar de risque[^"]+"', m.group(0)), m and m.group(0)


def test_la_ligne_du_radar_de_risque_allume_son_point_SANS_bulle():
    rq = _risque()
    p = _essai(rq, "point")
    assert p["on"] and p["lignes"] == ["transparence"] and p["placer"] == ["radar-hitzone/transparence"], p
    l = _essai(rq, "ligne")
    assert not l["on"] and l["lignes"] == ["transparence"] and l["placer"] == [], l
    c = _essai(rq, "cacher")
    assert not c["on"] and c["lignes"] == [], c


# ── 2 d. LA COURBE DE TARIFICATION ──────────────────────────────────────

_TARIF_SCEN = r"""
const titre = el("span", { id: "pricing-chart-title" });
el("div", { id: "pricing-chart-legend" }); el("div", { id: "pricing-chart-insight" }); el("span", { id: "pricing-chart-eq-badge" });
const donnees = el("div", { id: "pricing-chart-donnees" });
const tt = el("div", { id: "pricing-chart-tooltip", "class": "pricing-chart-tooltip" });
const svg = el("svg", { id: "pricing-chart-svg", viewBox: "0 0 640 320" });
svg.rect = [100, 200, 420, 360];
const sec = el("select", { id: "pricing-secteur" }); sec.value = "it";
const seg = el("select", { id: "pricing-segment" }); seg.value = "pme";
function serie(base, pas) { const out = []; for (let i = 0; i < 18; i++) out.push({ total: base + pas * i, socle: 158, variable: base + pas * i - 158 }); return out; }
const SC = { realiste: serie(632, 10), pessimiste: serie(700, 12), optimiste: serie(600, 8) };
window.pricingComputeMilestoneSchedule = (s, g, c, r, n) => ({ serie: r.slice(0, n).map((x, i) => ({ total: 500 + i, cumul: 500 * (i + 1), socle: 158, jalons: 342 + i })) });
const bandes = () => svg.querySelectorAll('[data-graphe="tarif"]');
essai("rendu", () => {
  pricingRenderChartFull(2000, SC, 6, "monthly");
  return { svg: { role: svg.getAttribute("role"), label: svg.getAttribute("aria-label"), titre: titre.textContent },
           bandes: bandes().map(b => b.attrs), cercles: svg.querySelectorAll(".pricing-chart-hover-zone").length,
           ecoutes: tous(svg).reduce((n, e) => n + e.ecoutes.length, 0),
           titres: tous(svg).filter(e => e.hasAttribute("title") || e.localName === "title").length,
           table: { lignes: donnees.querySelectorAll("tbody tr").length, valeurs: donnees.querySelectorAll("tbody td").length,
                    entetes: donnees.querySelectorAll("thead th").map(t => t.textContent), resume: donnees.querySelectorAll("caption").map(c => c.textContent) } };
});
essai("bulle", () => {
  const b = bandes()[2];
  placements.length = 0;
  window.grapheBulle.defs.tarif.montrer(b, "toucher");
  const halos = svg.querySelectorAll(".chart-hover-halo");
  return { texte: tt.textContent, display: tt.style.display, placer: placements.map(p => ({ x: p.x, cible: p.cible === b })),
           dataX: +b.getAttribute("data-x"), halos: halos.map(h => ({ pe: h.getAttribute("pointer-events"), cy: h.getAttribute("cy") })),
           ys: ["hybride", "pessimiste", "optimiste", "jalons"].map(s => b.getAttribute("data-y-" + s)) };
});
essai("cacher", () => { window.grapheBulle.defs.tarif.cacher(null); return { display: tt.style.display, halos: svg.querySelectorAll(".chart-hover-halo").length }; });
essai("refocus", () => {
  const b3 = bandes()[3]; document.activeElement = b3;
  pricingRenderChartFull(2000, SC, 6, "cumul");
  const a = document.activeElement;
  return { actif: a && a.getAttribute ? a.getAttribute("data-mois") : null, recree: a !== b3,
           arret: bandes().filter(b => b.getAttribute("tabindex") === "0").map(b => b.getAttribute("data-mois")) };
});
essai("horizon", () => {
  document.activeElement = body;
  const avant = bandes().filter(b => b.getAttribute("tabindex") === "0").map(b => b.getAttribute("data-mois"));
  pricingRenderChartFull(2000, SC, 18, "monthly");
  const b = bandes();
  const l = b.map(x => +x.getAttribute("width"));
  const long = { n: b.length, arret: b.filter(x => x.getAttribute("tabindex") === "0").map(x => x.getAttribute("data-mois")) };
  b.forEach(x => x.setAttribute("tabindex", x.getAttribute("data-mois") === "12" ? "0" : "-1"));
  pricingRenderChartFull(2000, SC, 6, "monthly");
  return { avant, n: long.n, arret: long.arret, court: bandes().filter(x => x.getAttribute("tabindex") === "0").map(x => x.getAttribute("data-mois")),
           plusEtroite: Math.min(...l), ecart: 552 / 17 };
});
"""


@functools.lru_cache(maxsize=None)
def _tarif():
    code = (_fonction("function _pChartTag(tag,attrs,inner){") + "\n"
            + _fonction("function pricingRenderChartFull(saasMonthly,scenarios,months,view){") + "\n")
    for debut, fin in (("function pricingEuros(v){", "}\n"), ("function pricingAttr(v){", "}\n")):
        if debut in PAGE_JS:
            code += _bloc(debut, fin) + "\n"
    code += _affectation("window.pricingShowTooltip = function(") + "\n"
    if "function pricingHalos(svg){" in PAGE_JS:
        code += _fonction("function pricingHalos(svg){") + "\n"
    code += _affectation("window.pricingHideTooltip = function(){") + "\n"
    if "enregistrer('tarif'" in PAGE_JS:
        code += _registration("tarif") + "\n"
    return _famille(code, _TARIF_SCEN)


def test_la_courbe_a_UNE_bande_par_mois_nommee_par_ses_quatre_series():
    """P7, A5, G-5. MESURÉ AVANT (Pixel 7) : 24 cercles de 8,8 px, jusqu'à 0 px
    entre deux centres, aucun au clavier. Exécuté : le vrai
    `pricingRenderChartFull`. Une bande par mois, image nommée « Mois m :
    Hybride continu … €, Pessimiste … €, Optimiste … €, RaaS Jalons … €
    (socle, variable) », ses séries en `data-*` ; plus aucun cercle, plus
    aucun écouteur ; le svg est un groupe nommé par son titre."""
    r = _essai(_tarif(), "rendu")
    assert len(r["bandes"]) == 6 and r["cercles"] == 0 and r["ecoutes"] == 0, (len(r["bandes"]), r["cercles"], r["ecoutes"])
    for i, b in enumerate(r["bandes"]):
        assert b.get("data-graphe") == "tarif" and b.get("data-mois") == str(i + 1) and b.get("role") == "img", b
        nom = b.get("aria-label", "")
        assert nom.startswith("Mois %d : " % (i + 1)) and nom.count("€") >= 4, nom
        for s in ("Hybride continu", "Pessimiste", "Optimiste", "RaaS Jalons"):
            assert s in nom, "%r absent de « %s »" % (s, nom)
        for s in ("hybride", "pessimiste", "optimiste", "jalons"):
            for k in ("lbl", "socle", "variable", "total", "couleur", "y"):
                assert b.get("data-%s-%s" % (k, s)) not in (None, ""), "data-%s-%s absent" % (k, s)
    assert r["svg"]["role"] == "group" and r["svg"]["label"] == r["svg"]["titre"] and r["svg"]["label"], r["svg"]


def test_les_bandes_couvrent_le_trace_centrees_sur_leur_mois():
    """Chaque bande est centrée sur son mois et large de l'écart entre deux
    mois (tracé 552 unités / 5 écarts à 6 mois), bornée au graphique : pas de
    trou entre deux bandes, aucune ne déborde du svg."""
    r = _essai(_tarif(), "rendu")
    xs = [(float(b["x"]), float(b["width"]), float(b["data-x"])) for b in r["bandes"]]
    assert len(xs) == 6, "%d bandes : le contrôle ne mesurerait rien" % len(xs)
    for i, (x, w, cx) in enumerate(xs):
        assert x >= 0 and x + w <= 640 + 1e-6, xs[i]
        if 0 < i < len(xs) - 1:
            assert abs(w - 552 / 5) < 1e-6 and abs(x + w / 2 - cx) < 1e-6, xs[i]
    for (x, w, _), (x2, _, _) in zip(xs, xs[1:]):
        assert abs(x + w - x2) < 1e-6, "un trou ou un chevauchement entre deux bandes : %r" % xs


def test_la_courbe_a_UN_arret_de_tabulation_qui_survit_au_redessin():
    """UN SEUL ARRÊT (le mois 1 au départ) ; la bande qui avait le focus le
    retrouve après un redessin (`innerHTML`), l'arrêt reste sur elle ; un
    horizon plus court le ramène au dernier mois."""
    t = _tarif()
    r = _essai(t, "rendu")
    assert [b.get("tabindex") for b in r["bandes"]] == ["0", "-1", "-1", "-1", "-1", "-1"], [b.get("tabindex") for b in r["bandes"]]
    f = _essai(t, "refocus")
    assert f["actif"] == "4" and f["recree"] and f["arret"] == ["4"], f
    h = _essai(t, "horizon")
    assert h["n"] == 18 and h["arret"] == ["4"], h
    assert h["court"] == ["6"], "l'arrêt n'est pas ramené au dernier mois d'un horizon plus court : %r" % h


def test_les_donnees_se_lisent_aussi_en_TABLEAU():
    """A5 : « Voir les données » — les mois en lignes, les quatre séries en
    colonnes, sous le graphique."""
    r = _essai(_tarif(), "rendu")
    t = r["table"]
    assert t["lignes"] == 6 and t["valeurs"] == 24, t
    assert t["entetes"] == ["Mois", "Hybride continu", "Pessimiste", "Optimiste", "RaaS Jalons"], t["entetes"]
    assert '<details class="chart-donnees"><summary>Voir les données</summary><div id="pricing-chart-donnees"></div></details>' in SENTINEL


def test_la_bulle_d_un_mois_lit_la_bande_et_l_echelle_du_VIEWBOX():
    """P9 : l'ancienne bulle lisait le curseur et une échelle 600 × 280 écrite
    en dur pour un graphique de 640 × 320 (mesuré : 28 à 43 px de décalage).
    Exécuté : la bulle liste les quatre séries du mois ; elle vise
    `svg.left + data-x × largeur / viewBox` (ici 320 / 640) ; le halo marque
    les quatre points, sans capter le pointeur ; cacher efface tout."""
    t = _tarif()
    r = _essai(t, "bulle")
    for s in ("Mois 3", "Hybride continu", "Pessimiste", "Optimiste", "RaaS Jalons", "socle", "variable"):
        assert s in r["texte"], "%r absent de la bulle « %s »" % (s, r["texte"])
    assert r["display"] == "block"
    assert r["placer"] == [{"x": 100 + r["dataX"] * 320 / 640, "cible": True}], r["placer"]
    assert len(r["halos"]) == 4 and all(h["pe"] == "none" for h in r["halos"]), r["halos"]
    assert sorted(h["cy"] for h in r["halos"]) == sorted(r["ys"]), (r["halos"], r["ys"])
    assert _essai(t, "cacher") == {"display": "none", "halos": 0}


# ── 2 e. LE SCHÉMA DE L'ÉCOSYSTÈME ──────────────────────────────────────

def _schema():
    m = re.search(r'<svg viewBox="0 0 680 610" class="carto-eco-svg"[^>]*>.*?</svg>', SENTINEL, re.S)
    assert m, "le schéma de l'écosystème est introuvable"
    return m.group(0)


_ECO_SCEN = r"""
const cadre = el("div", { "class": "carto-eco" });
cadre.innerHTML = SCHEMA;
const tip = el("div", { id: "carto-eco-tip", "class": "carto-eco-tip" }, cadre);
const noeuds = cadre.querySelectorAll(".eco-node");
noeuds.forEach((g, i) => { g.rect = [10 * i, 100, 10 * i + 80, 130]; });
essai("bulles", () => noeuds.map(g => {
  placements.length = 0;
  window.grapheBulle.defs.eco.montrer(g, "toucher");
  const p = placements[0] || {};
  return { texte: tip.textContent, attendu: g.getAttribute("data-eco-tip"), display: tip.style.display, cible: p.cible === g, x: p.x };
}));
essai("cacher", () => { window.grapheBulle.defs.eco.cacher(noeuds[0]); return tip.style.display; });
essai("titres", () => tous(cadre).filter(e => e.hasAttribute("title") || e.localName === "title").length);
"""


@functools.lru_cache(maxsize=None)
def _eco():
    code = (_affectation("window.ecoTip = function(ev, el){") + "\n"
            + _bloc("window.ecoTipHide = function(){", "};") + "\n")
    if "enregistrer('eco'" in PAGE_JS:
        code += _registration("eco") + "\n"
    return _famille("var SCHEMA = " + json.dumps(_schema()) + ";\n" + code, _ECO_SCEN)


class _Noeuds(object):
    def __init__(self):
        self.g = []
        self.svg = None
        self._p = None

    def lire(self, src):
        from html.parser import HTMLParser
        moi = self

        class P(HTMLParser):
            def __init__(self):
                HTMLParser.__init__(self, convert_charrefs=True)
                self.pile = []

            def handle_starttag(self, tag, attrs):
                a = dict((k, v or "") for k, v in attrs)
                if tag == "svg":
                    moi.svg = a
                if tag == "g" and "eco-node" in a.get("class", ""):
                    moi.g.append({"attrs": a, "textes": []})
                    self.pile.append(len(moi.g) - 1)
                elif tag == "text" and self.pile:
                    moi.g[self.pile[-1]]["textes"].append("")

            def handle_endtag(self, tag):
                if tag == "g" and self.pile:
                    self.pile.pop()

            def handle_data(self, d):
                if self.pile and moi.g[self.pile[-1]]["textes"]:
                    moi.g[self.pile[-1]]["textes"][-1] += d
        P().feed(src)
        return self


def test_les_noeuds_du_schema_sortent_du_chemin_data_tip():
    """§4.3 : /infobulles.js ramassait les onze nœuds pour leur `data-tip`, leur
    posait un tabindex (onze arrêts muets) et annonçait leur texte, pendant
    que la bulle du schéma suivait la souris. Ils portent `data-eco-tip` et
    `data-graphe="eco"`, n'écoutent plus la souris."""
    n = _Noeuds().lire(_schema())
    assert len(n.g) == 11, "%d nœuds" % len(n.g)
    for g in n.g:
        a = g["attrs"]
        assert "data-tip" not in a and a.get("data-eco-tip") and a.get("data-graphe") == "eco", a
        assert not any(k.startswith("onmouse") for k in a), a


def test_chaque_noeud_est_une_image_nommee_D_ABORD_par_son_texte_visible():
    """A11, 2.5.3 : svg `role="group"` au nom de synthèse ; chaque nœud
    `role="img"`, son nom commence par le texte qu'on voit, puis dit
    l'explication. Un seul arrêt de tabulation (le premier nœud)."""
    n = _Noeuds().lire(_schema())
    assert n.svg.get("role") == "group" and n.svg.get("aria-label"), n.svg
    for g in n.g:
        a, t = g["attrs"], [x.strip() for x in g["textes"]]
        assert a.get("role") == "img", a
        nom = a.get("aria-label", "")
        assert t and nom.startswith(t[0]) and all(x in nom for x in t), "« %s » / visible %r" % (nom, t)
        assert nom.endswith(a["data-eco-tip"]), "le nom ne dit pas l'explication : « %s »" % nom
    assert [g["attrs"].get("tabindex") for g in n.g] == ["0"] + ["-1"] * 10, [g["attrs"].get("tabindex") for g in n.g]


def test_plus_aucune_sequence_litterale_backslash_u2019():
    """UN ÉCHAPPEMENT JAVASCRIPT RECOPIÉ DANS DU HTML s'affiche tel quel :
    « l\\u2019AI Act » — six nœuds le montraient (mesuré au poste, avant)."""
    s = _schema()
    assert "\\u2019" not in s, "%d séquences \\u2019 dans le schéma" % s.count("\\u2019")
    assert "’" in s, "le schéma n'a plus d'apostrophe : le contrôle ne mesurerait rien"


def test_la_bulle_du_schema_dit_le_texte_du_noeud_ancree_au_noeud():
    """Exécuté : la vraie famille « eco » et le vrai `ecoTip`, sur les onze
    nœuds du vrai schéma. La bulle dit `data-eco-tip`, s'ancre au nœud (le
    pseudo-événement vise son centre) — plus au curseur."""
    r = _essai(_eco(), "bulles")
    assert len(r) == 11
    for b in r:
        assert b["texte"] == b["attendu"] and b["display"] == "block" and b["cible"], b
        assert b["x"] == 10 * r.index(b) + 40, "la bulle ne vise pas le centre du nœud : %r" % b
    assert _essai(_eco(), "cacher") == "none"


def _ancetres_titres(src):
    """Pour chaque conteneur de graphique de la page, les `title` de ses
    ANCÊTRES — lus dans le HTML comme un navigateur l'arbore. Et, en témoin,
    le nombre d'éléments de la page qui ont un ancêtre à `title`."""
    from html.parser import HTMLParser
    VIDES = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "wbr"}
    CIBLES = {"geo-chart", "radar-svg", "radar-scores", "pricing-chart-svg", "mat-content"}
    out, temoin = {}, [0]

    class P(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self, convert_charrefs=True)
            self.pile = []

        def handle_starttag(self, tag, attrs):
            a = dict((k, v or "") for k, v in attrs)
            titres = [x.get("title") for x in self.pile if (x.get("title") or "").strip()]
            if titres:
                temoin[0] += 1
            cle = a.get("id") if a.get("id") in CIBLES else ("carto-eco-svg" if "carto-eco-svg" in a.get("class", "") else None)
            if cle:
                out[cle] = titres + ([a["title"]] if (a.get("title") or "").strip() else [])
            if tag not in VIDES:
                self.pile.append(a)

        def handle_startendtag(self, tag, attrs):
            self.handle_starttag(tag, attrs)
            if tag not in VIDES and self.pile:
                self.pile.pop()

        def handle_endtag(self, tag):
            if self.pile:
                self.pile.pop()
    P().feed(src)
    return out, temoin[0]


def test_aucune_cible_de_graphique_ni_son_graphique_ne_porte_de_TITLE():
    """UN `title` SUR UNE CIBLE OU SUR UN ANCÊTRE, c'est une seconde bulle :
    /bulle-titre.js prendrait l'ancêtre à `title` le plus proche, au doigt et
    au clavier, et le navigateur l'afficherait à la souris — à côté de la
    bulle du graphique. De même un <title> SVG. Lu sur ce que les VRAIES
    fonctions peignent, et sur les ancêtres de chaque graphique dans la page.
    LE TÉMOIN : le même relevé trouve des ancêtres à `title` ailleurs."""
    rendus = {"geo": _essai(_geo(), "rendu")["titres"], "mat": _essai(_mat(), "rendu")["titres"],
              "risque": _essai(_risque(), "rendu")["titres"], "tarif": _essai(_tarif(), "rendu")["titres"],
              "eco": _essai(_eco(), "titres")}
    assert all(v == 0 for v in rendus.values()), "title ou <title> dans ce que peignent les graphiques : %r" % rendus
    ancetres, temoin = _ancetres_titres(SENTINEL)
    assert set(ancetres) == {"geo-chart", "radar-svg", "radar-scores", "pricing-chart-svg", "mat-content", "carto-eco-svg"}, sorted(ancetres)
    assert temoin > 0, "le relevé ne trouve aucun ancêtre à title dans la page : il ne mesurerait rien"
    fautes = dict((k, v) for k, v in ancetres.items() if v)
    assert not fautes, "des graphiques ont un ancêtre à title : %r" % fautes


# ══════════════════════════════════════════════════════════════════════════
#  3. LES BULLES : MUETTES, FIXES, SURVOLABLES, AU-DESSUS ; LE FOCUS DESSINÉ
# ══════════════════════════════════════════════════════════════════════════

def _regle_css(selecteur):
    m = re.search(r"(?m)^%s\{([^}]*)\}" % re.escape(selecteur), SENTINEL)
    assert m, "la règle %s est introuvable" % selecteur
    return m.group(1)


@pytest.mark.parametrize("classe", [".geo-tooltip", ".mat-radar-tooltip", ".pricing-chart-tooltip", ".carto-eco-tip"])
def test_la_bulle_est_FIXE_SURVOLABLE_et_AU_DESSUS_de_la_barre_du_haut(classe):
    """1.4.13 : survolable (`pointer-events:auto`). FIXE : dans `.tbl-wrap`
    (`overflow:hidden`) une bulle absolue était rognée au bord du cadre.
    `z-index` au moins 9999 : au-dessus de la barre du haut (100) et des
    flèches de navigation (9995) — sous les fenêtres modales (10020)."""
    r = _regle_css(classe)
    assert "position:fixed" in r and "pointer-events:auto" in r, r
    z = re.search(r"z-index:(\d+)", r)
    assert z and 9999 <= int(z.group(1)) < 10020, "z-index %r" % (z and z.group(1))


def test_la_bulle_du_radar_se_CACHE_par_display_et_non_par_l_opacite():
    """A10, G-3. MESURÉ AVANT : `#mat-radar-tooltip` restait `display:block`, à
    opacité 0, et lu dans l'arbre d'accessibilité."""
    r = _regle_css(".mat-radar-tooltip")
    assert "display:none" in r and "opacity:0" not in r, r
    assert "display:block" in _regle_css(".mat-radar-tooltip.on"), _regle_css(".mat-radar-tooltip.on")


@pytest.mark.parametrize("ident", ["geo-tooltip", "pricing-chart-tooltip", "carto-eco-tip"])
def test_la_bulle_est_MUETTE_dans_la_page(ident):
    m = re.search(r'<div[^>]*id="%s"[^>]*>' % ident, SENTINEL)
    assert m and 'aria-hidden="true"' in m.group(0), m and m.group(0)


def test_le_focus_d_une_cible_est_DESSINE():
    """G-12 : aucun contour carré du navigateur ; un trait (forme SVG), le
    premier enfant d'un nœud <g> (le schéma rogne ce qui déborde), un contour
    pour une barre <div>. La recette mesure le contraste sur la capture."""
    for regle in ("[data-graphe]:focus{outline:none}",
                  "rect[data-graphe]:focus-visible,circle[data-graphe]:focus-visible{stroke:currentColor;stroke-width:2}",
                  "g[data-graphe]:focus-visible > :first-child{stroke:currentColor;stroke-width:3}",
                  "div[data-graphe]:focus-visible{outline:2px solid currentColor;outline-offset:2px}"):
        assert regle in SENTINEL, "règle absente : %s" % regle


def test_plus_aucune_bulle_de_graphique_n_ecoute_la_souris():
    """§4.2, R3 : les sept sites, relus dans le code (hors commentaires).
    Au doigt, les événements de souris de compatibilité qui suivent l'appui
    refermaient la bulle en 13 à 16 ms."""
    code = re.sub(r"/\*.*?\*/", "", PAGE_JS, flags=re.S)
    fautes = re.findall(r"onmouse(?:enter|leave|move)=\\?\"(?:matRadar|radar|ecoTip)\w*", code)
    fautes += re.findall(r"onmouse(?:enter|leave|move)=\"(?:matRadar|radar|ecoTip)\w*", SENTINEL)
    for f in ("function geoRenderChart(){", "function pricingRenderChartFull(saasMonthly,scenarios,months,view){"):
        corps = re.sub(r"/\*.*?\*/", "", _fonction(f), flags=re.S)
        fautes += re.findall(r"addEventListener\(\s*'mouse\w+'", corps)
    assert not fautes, "écouteurs de souris restants : %s" % fautes


def test_sentinel_page_js_est_charge_AVANT_infobulles_et_bulle_titre():
    """L'ORDRE DES ÉCHAP. Les trois écoutent `keydown` sur `window` en capture ;
    à cible et phase égales, l'ordre d'inscription décide. Le pilote
    s'inscrit à l'exécution de sentinel.page.js (règle d'inscription au
    chargement) : il faut que ce fichier passe le premier — mesuré par la
    recette, « sentinel.page.js → infobulles.js → bulle-titre.js »."""
    i = SENTINEL.find('<script src="/sentinel.page.js" defer></script>')
    j = SENTINEL.find('<script src="/infobulles.js" defer></script>')
    k = SENTINEL.find('<script src="/bulle-titre.js" defer></script>')
    assert 0 <= i < j < k, (i, j, k)


# ══════════════════════════════════════════════════════════════════════════
#  4. UNE BULLE À LA FOIS : /bulle-titre.js FERME CELLE D'UN GRAPHIQUE
# ══════════════════════════════════════════════════════════════════════════

_BT = _DOM + r"""
const fs = require("fs");
const src = fs.readFileSync(process.argv[2], "utf8");
const ecouteurs = {};
const inscrire = (ou) => function (type, fn, opt) {
  const capture = opt === true || !!(opt && opt.capture);
  (ecouteurs[ou + ":" + type + ":" + capture] = ecouteurs[ou + ":" + type + ":" + capture] || []).push(fn);
};
function emettre(type, ev) {
  for (const [ou, cap] of [["window", true], ["document", true], ["document", false], ["window", false]]) {
    for (const fn of (ecouteurs[ou + ":" + type + ":" + cap] || []).slice()) { fn(ev); if (ev.immediat) return ev; }
    if (ev.arrete) return ev;
  }
  return ev;
}
function evenement(extra) {
  const ev = Object.assign({ retenu: false, arrete: false, immediat: false, pointerId: 1, clientX: 0, clientY: 0 }, extra);
  ev.preventDefault = () => { ev.retenu = true; }; ev.stopPropagation = () => { ev.arrete = true; };
  ev.stopImmediatePropagation = () => { ev.immediat = true; ev.arrete = true; };
  return ev;
}
const document = { readyState: "interactive", head, body, documentElement: racine, activeElement: body,
  getElementById: id => par(id), createElement: t => new El(t), addEventListener: inscrire("document") };
const visualViewport = { offsetLeft: 0, offsetTop: 0, width: 400, height: 800, addEventListener: inscrire("vv") };
let graphesFermes = 0;
const window = { innerWidth: 400, innerHeight: 800, visualViewport, addEventListener: inscrire("window"),
  getComputedStyle: () => ({ cursor: "auto" }), getSelection: () => ({ removeAllRanges() {} }),
  requestAnimationFrame: fn => _setTimeout(fn, 16) };
if (fs.readFileSync(process.argv[3], "utf8") === "avec") window.grapheBulle = { fermer() { graphesFermes++; } };
const bouton = el("button", { title: "Enregistrer cette évaluation dans l'historique" }, body, [20, 300, 200, 330]);
bouton.appendChild(new Texte("Enregistrer"));
new Function("window", "document", "setTimeout", "clearTimeout", "setInterval", "clearInterval", "Date", "MutationObserver", src)(
  window, document, _setTimeout, _clear, _setInterval, _clear, _Date, function () { return { observe() {} }; });
const vue = () => { const b = par("bulle-titre"); return !!b && !b.hidden; };
const out = {};
emettre("keydown", evenement({ key: "Tab" })); bouton.focus(); avancer(400);
out.clavier400 = { vue: vue(), fermes: graphesFermes };
avancer(200); out.clavier600 = { vue: vue(), fermes: graphesFermes };
window.bulleTitre.fermer(); document.activeElement = body; avancer(1500);
const f0 = graphesFermes;
emettre("pointerdown", evenement({ pointerType: "touch", target: bouton })); avancer(600);
out.long = { vue: vue(), fermes: graphesFermes - f0 };
emettre("pointerup", evenement({ pointerType: "touch", target: bouton }));
process.stdout.write(JSON.stringify(out));
"""


@pytest.mark.parametrize("pourquoi", ["clavier600", "long"])
def test_bulle_titre_qui_s_ouvre_FERME_la_bulle_d_un_graphique(pourquoi):
    """LE DÉFAUT : une bulle de graphique ouverte au SURVOL restait à côté de
    celle d'un `title` ouverte à la tabulation ou à l'appui long — deux
    bulles. Exécuté : le vrai /bulle-titre.js, un `window.grapheBulle` qui
    compte ; à l'ouverture, il est fermé. LE TÉMOIN : à 400 ms, rien n'est
    ouvert, rien n'est fermé ; sans pilote, la bulle s'ouvre quand même."""
    r = _node(_BT, BULLE_TITRE, "avec")
    assert not r["clavier400"]["vue"] and r["clavier400"]["fermes"] == 0, r["clavier400"]
    assert r[pourquoi]["vue"], "la bulle du title ne s'ouvre pas : le contrôle ne mesurerait rien"
    assert r[pourquoi]["fermes"] >= 1, "%s : la bulle du graphique n'est pas fermée" % pourquoi
    sans = _node(_BT, BULLE_TITRE, "sans")
    assert sans[pourquoi]["vue"], "sans pilote de graphique, /bulle-titre.js ne s'ouvre plus"


# ══════════════════════════════════════════════════════════════════════════
#  5. LA RECETTE NE SE PÉRIME PAS EN SILENCE (règles sur la recette elle-même)
# ══════════════════════════════════════════════════════════════════════════

RECETTE = _lire("recette_graphes_bulles.js")


def _peint(genre, nom, code=None):
    """Combien de fois le code PEINT l'identifiant : un attribut `class` ou
    `id` écrit dans le HTML ou dans une chaîne de JavaScript, une propriété
    posée (`className`, `classList.add`, `.id =`), une globale affectée.
    UNE RÈGLE CSS NE COMPTE PAS, ni une simple mention : `.geo-bar-col{…}`
    survit au rendu qui a changé de nom, et la recette viserait alors une
    classe que plus rien ne porte — elle ne mesurerait plus rien, en vert."""
    code = SENTINEL + "\n" + PAGE_JS if code is None else code
    n = re.escape(nom)
    if genre == "classe":
        motifs = [r"""\bclass\s*=\s*\\?["'][^"'<>]*?(?<![\w-])%s(?![\w-])""" % n,
                  r"""\.className\s*=\s*["'][^"']*?(?<![\w-])%s(?![\w-])""" % n,
                  r"""\.classList\.(?:add|toggle)\(\s*["']%s["']""" % n]
    elif genre == "id":
        motifs = [r"""\bid\s*=\s*\\?["']%s\\?["']""" % n, r"""\.id\s*=\s*["']%s["']""" % n]
    elif genre == "attribut":
        a, v = nom.split("=", 1)
        motifs = [r"""(?<![\w-])%s\s*=\s*\\?["']%s\\?["']""" % (re.escape(a), re.escape(v.strip('"')))]
    elif genre == "balise":
        t, c = nom.split(".", 1)
        motifs = [r"""<%s\b[^>]*\bclass\s*=\s*["'][^"']*?(?<![\w-])%s(?![\w-])""" % (re.escape(t), re.escape(c))]
    else:
        motifs = [r"""\bwindow\.%s\s*=""" % n]
    return sum(len(re.findall(m, code)) for m in motifs)


_ANCRES = [("classe", "geo-bar-col"), ("classe", "mat-radar-hitzone"), ("classe", "radar-hitzone"),
           ("attribut", 'data-graphe="tarif"'), ("classe", "eco-node"), ("id", "geo-tooltip"),
           ("id", "mat-radar-tooltip"), ("id", "radar-tooltip"), ("id", "pricing-chart-tooltip"),
           ("id", "carto-eco-tip"), ("classe", "mat-pillar-row"), ("classe", "mat-tooltip-wrap"),
           ("id", "pricing-chart-donnees"), ("classe", "geo-filter-chip"), ("classe", "mat-sector-btn"),
           ("balise", "header.topbar"), ("global", "grapheBulle"), ("id", "radar-scores"),
           ("id", "mat-radar-svg-el"), ("id", "radar-svg")]


@pytest.mark.parametrize("genre,ancre", _ANCRES, ids=[a for _, a in _ANCRES])
def test_la_recette_vise_des_ancres_QUI_EXISTENT(genre, ancre):
    """Chaque identifiant que la recette vise est encore PEINT par le code —
    pas seulement nommé dans une feuille de style. LE TÉMOIN : le même relevé
    ne trouve aucune peinture d'un nom inventé."""
    assert ancre in RECETTE, "la recette ne vise plus %r" % ancre
    assert _peint(genre, ancre + "-inconnu" if genre != "attribut" else 'data-graphe="inconnu"') == 0, "le relevé compte n'importe quoi"
    assert _peint(genre, ancre) >= 1, "%r n'est plus peint par le code : la recette mesure un identifiant mort" % ancre


def _cibles_recette():
    """La table `G` de la recette : pour chaque graphique, les sélecteurs de
    sa cible, de sa bulle, de sa ligne — ce que TOUS ses contrôles visent."""
    m = re.search(r"^const G = \{\n(.*?)\n\};", RECETTE, re.S | re.M)
    assert m, "la table G de la recette est introuvable"
    out = {}
    for fam, corps in re.findall(r"^\s*(\w+):\s*\{(.*)\},?$", m.group(1), re.M):
        out[fam] = dict(re.findall(r"(\w+):\s*'([^']*)'", corps))
    return out


def _jetons(compose):
    """`#a .b[c="d"]` → [('id','a'), ('classe','b'), ('attribut','c="d"')]."""
    out = []
    for p in re.finditer(r"""#([\w-]+)|\.([\w-]+)|\[([\w-]+)=["']?([^"'\]]*)["']?\]""", compose):
        if p.group(1):
            out.append(("id", p.group(1)))
        elif p.group(2):
            out.append(("classe", p.group(2)))
        else:
            out.append(("attribut", '%s="%s"' % (p.group(3), p.group(4))))
    return out


@pytest.mark.parametrize("famille", ["geo", "mat", "risque", "tarif", "eco"])
def test_les_cibles_de_la_recette_sont_PEINTES_par_le_code(famille):
    """La table `G` de la recette désigne, pour chaque graphique, la cible,
    la bulle et la ligne que visent tous ses contrôles. Chaque sélecteur doit
    désigner ce que le code PEINT : au moins une de ses variantes (la courbe
    en garde deux — la bande d'aujourd'hui, le cercle de be93b64, pour la
    colonne d'avant) dont chaque identifiant est peint. Un sélecteur mort
    ferait passer les contrôles « rien ne s'ouvre » sans rien viser."""
    g = _cibles_recette()
    assert set(g) == {"geo", "mat", "risque", "tarif", "eco"}, sorted(g)
    assert set(g) == set(re.findall(r"window\.grapheBulle\.enregistrer\('(\w+)'", PAGE_JS)), "la recette et le pilote ne parlent pas des mêmes graphiques"
    for champ in ("cible", "bulle", "ligne"):
        sel = g[famille].get(champ)
        if not sel:
            continue
        variantes = [_jetons(v) for v in sel.split(",")]
        assert all(variantes), "%s.%s : un sélecteur sans identifiant ne vise rien de précis : %r" % (famille, champ, sel)
        mortes = [[j for j in v if not _peint(*j)] for v in variantes]
        assert any(not m for m in mortes), "%s.%s = %r : rien de peint (%s)" % (famille, champ, sel, mortes)


def test_la_recette_compare_a_une_colonne_AVANT_relevee():
    """Les deux colonnes : AVANT_FIGE relevé sur be93b64 par CETTE recette —
    une colonne vide ne comparerait rien."""
    m = re.search(r"const AVANT_FIGE = \{\n(.*?)\n\};", RECETTE, re.S)
    assert m, "AVANT_FIGE introuvable"
    cles = re.findall(r"^\s*'([^']+)':", m.group(1), re.M)
    assert len(cles) >= 25, "%d mesures d'avant seulement" % len(cles)
    faites = set(re.findall(r"ok\('([^']+)'", RECETTE))
    assert set(cles) <= faites, "des mesures d'avant ne correspondent à aucun contrôle : %s" % sorted(set(cles) - faites)
