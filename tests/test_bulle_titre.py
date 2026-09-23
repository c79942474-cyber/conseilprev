# -*- coding: utf-8 -*-
"""LES `title` NATIFS SE LISENT AU DOIGT ET AU CLAVIER — /bulle-titre.js.

LE DÉFAUT MESURÉ. Un `title` ne s'affiche qu'à la souris posée dessus.
Relevé au navigateur en contexte tactile (Pixel 7, recette_bulle_titre.js,
colonne « avant ») : un appui sur une pastille « P1 », sur une ligne du
menu, sur un bloc de score n'affiche RIEN ; un appui long sur une ligne du
menu sélectionne son texte. Au clavier, la tabulation atteint la ligne du
menu et rien ne s'affiche non plus. Plus de quatre mille `title` dans
Sentinel, lisibles à la souris seulement.

POURQUOI UN SCRIPT À PART. /infobulles.js ne ramasse que `data-tooltip` et
`data-tip`, et deux règles de la suite le figent ainsi (pas de `[title]`,
pas d'écouteur de défilement). Elles restent vraies : le chemin `title` vit
dans /bulle-titre.js, avec ses propres règles — celles-ci.

CES RÈGLES EXÉCUTENT LE SCRIPT. Le harnais charge le VRAI /bulle-titre.js
dans node, sur un DOM réduit à ce qu'il touche — sélecteurs composés,
rectangles, fenêtre visuelle, horloge maîtrisée — et joue les gestes : un
appui, un balayage, un appui long, une tabulation, Échap dans une fenêtre
modale. On lit ce que le script fait de chacun. La recette mesure le reste
au navigateur : le vrai `contextmenu`, la vraie sélection, la vraie
géométrie.
"""
import functools
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


SCRIPT = _lire("bulle-titre.js")
INFOBULLES = _lire("infobulles.js")
PAGE_JS = _lire("sentinel.page.js")
SENTINEL = _lire("sentinel.html")


def _code(src):
    """Le CODE, sans ses commentaires : un commentaire peut citer
    `mouseover` pour dire pourquoi on ne l'écoute pas."""
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", "", src)


CODE = _code(SCRIPT)


# ══════════════════════════════════════════════════════════════════════════
#  LE HARNAIS — le vrai script, un DOM minuscule, une horloge maîtrisée
# ══════════════════════════════════════════════════════════════════════════

_HARNAIS = r"""
"use strict";
const fs = require("fs");
const [, , SCRIPT, OPTS] = process.argv;
const src = fs.readFileSync(SCRIPT, "utf8");
const opts = JSON.parse(OPTS);

/* ── L'HORLOGE. Les minuteurs ne partent que quand le scénario AVANCE le
   temps : « à 400 ms rien, à 600 ms ouvert » se mesure, il ne se devine
   pas. */
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
const _Date = { now: () => horloge };

/* ── UN DOM RÉDUIT À CE QUE LE SCRIPT TOUCHE. Les sélecteurs COMPOSÉS
   (`a[href]`, `[role=button]`, `[contenteditable=""]`) sont lus ; une
   combinaison (espace, `>`, `+`, `~`) LÈVE une erreur, pour qu'aucun
   contrôle ne passe sur un sélecteur que le harnais n'a pas su lire. */
function Texte(t) { this.nodeType = 3; this.parentElement = null; this.data = String(t); }
function El(tag, attrs, rect) {
  this.nodeType = 1;
  this.tagName = /^(svg|rect|g|circle|path)$/.test(tag) ? tag : String(tag).toUpperCase();
  this.parentElement = null; this.enfants = []; this.attrs = {}; this.style = {};
  this.rect = rect || null; this.masque = false; this.curseur = "auto";
  for (const k in (attrs || {})) this.attrs[k] = String(attrs[k]);
  const moi = this;
  this.classList = {
    contains: c => (moi.attrs["class"] || "").split(/\s+/).indexOf(c) >= 0,
    add: c => { if (!moi.classList.contains(c)) moi.attrs["class"] = ((moi.attrs["class"] || "") + " " + c).trim(); },
    remove: c => { moi.attrs["class"] = (moi.attrs["class"] || "").split(/\s+/).filter(x => x !== c).join(" "); },
  };
}
El.prototype.getAttribute = function (k) { return k in this.attrs ? this.attrs[k] : null; };
El.prototype.hasAttribute = function (k) { return k in this.attrs; };
El.prototype.setAttribute = function (k, v) { this.attrs[k] = String(v); poses.push([this.attrs.id || this.tagName, k]); };
El.prototype.removeAttribute = function (k) { delete this.attrs[k]; };
El.prototype.appendChild = function (e) { e.parentElement = this; this.enfants.push(e); return e; };
El.prototype.remove = function () { if (this.parentElement) { const p = this.parentElement; p.enfants = p.enfants.filter(x => x !== this); this.parentElement = null; } };
Object.defineProperty(El.prototype, "id", { get() { return this.attrs.id || ""; }, set(v) { this.attrs.id = String(v); } });
Object.defineProperty(El.prototype, "hidden", {
  get() { return "hidden" in this.attrs; },
  set(v) {
    const avant = "hidden" in this.attrs;
    if (v) this.attrs.hidden = ""; else delete this.attrs.hidden;
    if (this === bulleVue() && avant && !v) ouvertures++;
  },
});
Object.defineProperty(El.prototype, "textContent", {
  get() { return this.enfants.map(e => e.nodeType === 3 ? e.data : e.textContent).join(""); },
  set(v) { this.enfants = []; this.appendChild(new Texte(v)); },
});
Object.defineProperty(El.prototype, "isConnected", {
  get() { for (let e = this; e; e = e.parentElement) if (e === racine) return true; return false; },
});
El.prototype.cache = function () { for (let e = this; e; e = e.parentElement) if (e.masque) return true; return false; };
/* LA BULLE A UNE LARGEUR NATURELLE — celle de son texte —, que sa
   `max-width` borne. 200 px par défaut ; un scénario la porte à 320 ou 600
   pour éprouver la borne. Un premier harnais la plafonnait à 200 en dur :
   aucune règle ne pouvait voir une bulle de 320 px déborder sur le menu
   (revue de conformité, constats 4 et 5). */
let largeurNaturelle = 200;
El.prototype.getBoundingClientRect = function () {
  if (this === bulleVue()) {
    const mw = parseFloat(this.style.maxWidth);
    const w = Math.min(largeurNaturelle, isNaN(mw) ? Infinity : mw), h = 40;
    const l = parseFloat(this.style.left) || 0, t = parseFloat(this.style.top) || 0;
    return { left: l, top: t, right: l + w, bottom: t + h, width: w, height: h };
  }
  if (this.cache() || !this.rect) return { left: 0, top: 0, right: 0, bottom: 0, width: 0, height: 0 };
  const r = this.rect;
  return { left: r[0], top: r[1], right: r[2], bottom: r[3], width: r[2] - r[0], height: r[3] - r[1] };
};
El.prototype.getClientRects = function () { return this.cache() || !this.rect ? [] : [this.getBoundingClientRect()]; };
El.prototype.contains = function (o) { for (let e = o; e; e = e.parentElement) if (e === this) return true; return false; };
El.prototype.compose = function (s) {
  s = s.trim();
  if (/[\s>+~]/.test(s.replace(/\[[^\]]*\]/g, ""))) throw new Error("sélecteur hors du harnais : " + s);
  const m = /^([a-zA-Z][\w-]*|\*)?(.*)$/.exec(s);
  if (m[1] && m[1] !== "*" && this.tagName.toUpperCase() !== m[1].toUpperCase()) return false;
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
function couper(txt) {
  const out = []; let prof = 0, q = "", d = 0;
  for (let i = 0; i < txt.length; i++) {
    const c = txt[i];
    if (q) { if (c === q) q = ""; continue; }
    if (c === '"' || c === "'") q = c;
    else if (c === "[" || c === "(") prof++;
    else if (c === "]" || c === ")") prof--;
    else if (c === "," && prof === 0) { out.push(txt.slice(d, i)); d = i + 1; }
  }
  out.push(txt.slice(d));
  return out;
}
El.prototype.matches = function (sel) { return couper(sel).some(s => this.compose(s)); };
El.prototype.closest = function (sel) { for (let e = this; e; e = e.parentElement) if (e.matches(sel)) return e; return null; };
function tous(e) { return [e].concat(...e.enfants.filter(x => x.nodeType === 1).map(tous)); }

const poses = [];
const racine = new El("html"), head = racine.appendChild(new El("head")), body = racine.appendChild(new El("body"));
body.rect = [0, 0, 400, 800];
const bulleVue = () => tous(racine).find(e => e.id === "bulle-titre") || null;
let ouvertures = 0, selectionsVidees = 0, observateurs = 0;

/* LES ÉCOUTEURS, rangés par NŒUD et par PHASE, appelés dans l'ordre du
   navigateur : `window` en capture, `document` en capture, `document` en
   remontée, `window` en remontée. */
const ecouteurs = {}, inscrits = [];
const inscrire = (ou) => function (type, fn, opt) {
  const capture = opt === true || !!(opt && opt.capture);
  (ecouteurs[ou + ":" + type + ":" + capture] = ecouteurs[ou + ":" + type + ":" + capture] || []).push(fn);
  inscrits.push({ ou, type, capture, passif: !!(opt && opt.passive) });
};
const document = {
  readyState: "interactive", head, body, documentElement: racine, activeElement: body,
  getElementById: id => tous(racine).find(e => e.id === id) || null,
  createElement: tag => new El(tag),
  addEventListener: inscrire("document"),
};
const visualViewport = { offsetLeft: 0, offsetTop: 0, width: 400, height: 800,
                         addEventListener: inscrire("vv") };
const window = {
  innerWidth: 400, innerHeight: 800, visualViewport,
  addEventListener: inscrire("window"),
  getComputedStyle: el => ({ cursor: el.curseur || "auto" }),
  getSelection: () => ({ removeAllRanges() { selectionsVidees++; } }),
  requestAnimationFrame: fn => _setTimeout(fn, 16),
};
/* /infobulles.js, réduit à ce que ce script en LIT (`selecteur`) et en
   APPELLE (`fermer`, compté). */
let infobullesFermees = 0;
if (opts.infobulles) window.infobulles = { selecteur: "[data-tooltip],[data-tip],.mat-tooltip-wrap",
                                           fermer() { infobullesFermees++; } };
function MutationObserver() { observateurs++; return { observe() {} }; }

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
  const ev = Object.assign({ retenu: false, arrete: false, immediat: false, pointerId: 1,
                             clientX: 0, clientY: 0 }, extra);
  ev.preventDefault = () => { ev.retenu = true; };
  ev.stopPropagation = () => { ev.arrete = true; };
  ev.stopImmediatePropagation = () => { ev.immediat = true; ev.arrete = true; };
  return ev;
}
/* LES GESTES, tels que le navigateur les émet. */
const pt = (type, cible, extra) => emettre(type, evenement(Object.assign({ pointerType: "touch", target: cible }, extra)));
function appui(cible, extra) {
  pt("pointerdown", cible, extra); avancer(80); pt("pointerup", cible, extra);
  return emettre("click", evenement({ target: cible }));
}
function appuiLong(cible, duree, extra) {
  pt("pointerdown", cible, extra); avancer(duree || 700); pt("pointerup", cible, extra);
  return emettre("click", evenement({ target: cible }));
}
function balayage(cible) { pt("pointerdown", cible); avancer(24); pt("pointercancel", cible); pt("pointerup", cible); }
function clicSouris(cible) {
  pt("pointerdown", cible, { pointerType: "mouse" }); pt("pointerup", cible, { pointerType: "mouse" });
  return emettre("click", evenement({ target: cible }));
}
function tab(cible, touche) {
  emettre("keydown", evenement({ key: touche || "Tab" }));
  const avant = document.activeElement;
  document.activeElement = cible;
  emettre("focusout", evenement({ target: avant, relatedTarget: cible }));
  emettre("focusin", evenement({ target: cible, relatedTarget: avant }));
}
function focusSur(cible) {
  const avant = document.activeElement; document.activeElement = cible;
  emettre("focusout", evenement({ target: avant, relatedTarget: cible }));
  emettre("focusin", evenement({ target: cible, relatedTarget: avant }));
}
function quitter(cible, vers) {
  document.activeElement = vers || body;
  emettre("focusout", evenement({ target: cible, relatedTarget: vers || null }));
  if (vers) emettre("focusin", evenement({ target: vers, relatedTarget: cible }));
}

/* ── LA PAGE : un exemplaire de chaque cas que le script doit trancher. */
function el(parent, tag, attrs, texte, rect) {
  const e = parent.appendChild(new El(tag, attrs, rect || [10, 200, 110, 220]));
  if (texte !== undefined) e.appendChild(new Texte(texte));
  return e;
}
const P = {};
P.sb = el(body, "aside", { id: "sb" }, undefined, [0, 0, 240, 800]);
P.item = el(P.sb, "div", { "class": "sb-item", role: "button", tabindex: "0", onclick: "go()",
  title: "Panorama mondial : scores de risque sur 24 juridictions." }, "Observatoire IA", [8, 100, 232, 130]);
P.item2 = el(P.sb, "div", { "class": "sb-item", role: "button", tabindex: "0", onclick: "go()",
  title: "Tableau de bord personnel." }, "Mon Espace", [8, 130, 232, 160]);
P.puce = el(P.item, "span", { "class": "rail-puce", "data-tooltip": "Bloc — en cours", title: "" }, "↓", [200, 105, 220, 125]);
P.icone = el(P.item, "span", { "class": "sb-icon" }, "", [12, 105, 26, 125]);
P.prio = el(body, "span", { "class": "audit-item-prio", title: "P1 : obligation critique, à traiter en premier" }, "P1", [150, 300, 180, 320]);
P.prioTexte = P.prio.enfants[0];
P.kpi = el(body, "div", { "class": "audit-kpi", title: "Calcul : points conformes sur points applicables." }, "72 %", [20, 340, 200, 400]);
P.lien = el(body, "a", { href: "/texte-officiel", title: "Règlement, texte officiel consolidé" }, "Art. 5", [20, 420, 80, 440]);
P.bouton = el(body, "button", { title: "Enregistrer cette évaluation dans l'historique" }, "Enregistrer", [100, 420, 200, 450]);
P.raccourci = el(body, "button", { title: "Suivant (Alt+→)" }, "Suivant", [210, 420, 300, 450]);
P.repete = el(body, "span", { title: "« Score global. »" }, "Score  global", [20, 460, 120, 480]);
P.court = el(body, "span", { title: "x" }, "a", [130, 460, 150, 480]);
P.lbl = el(body, "span", { id: "lbl-note" }, "Note finale", [160, 460, 240, 480]);
P.nomme = el(body, "span", { "aria-labelledby": "lbl-note", title: "note finale" }, "B+", [250, 460, 280, 480]);
P.etiquete = el(body, "span", { "aria-label": "Retirer", title: "Retirer." }, "×", [290, 460, 310, 480]);
P.champ = el(body, "input", { title: "Date prévue de la session" }, undefined, [20, 500, 200, 530]);
/* Une case à cocher qui porte SON `title` : exclue comme tout <input> —
   seule celle qui l'emprunte à son libellé en a une. */
P.caseTitree = el(body, "input", { type: "checkbox", title: "Relance automatique à chaque échéance" }, undefined, [205, 470, 221, 486]);
P.iframe = el(body, "iframe", { title: "Aperçu du rapport" }, undefined, [20, 540, 200, 600]);
P.select = el(body, "select", {}, undefined, [210, 500, 380, 530]);
P.option = el(P.select, "option", { title: "Une option expliquée" }, "Option", [210, 500, 380, 530]);
P.svg = el(body, "svg", {}, undefined, [20, 610, 120, 660]);
P.svgRect = el(P.svg, "rect", { title: "Un point du graphique" }, undefined, [30, 620, 40, 630]);
P.graphe = el(body, "div", { "data-graphe": "geo" }, undefined, [130, 610, 200, 660]);
P.dansGraphe = el(P.graphe, "span", { title: "Une barre du graphique" }, "12", [140, 620, 160, 640]);
P.tt = el(body, "span", { "data-tt": "Bulle du panorama", title: "Titre du panorama" }, "Zone", [210, 610, 260, 630]);
P.bloc = el(body, "div", { title: "Explication du bloc entier" }, "Bloc ", [20, 670, 380, 700]);
P.tipDansBloc = el(P.bloc, "span", { "data-tip": "Bulle data-tip" }, "(i)", [300, 675, 320, 695]);
P.tipParent = el(body, "div", { "data-tip": "Bulle du parent" }, "Parent ", [20, 710, 380, 740]);
P.titreDansTip = el(P.tipParent, "span", { title: "Explication de l'enfant" }, "enfant", [100, 715, 160, 735]);
P.parentTitre = el(body, "div", { title: "Titre du parent, explicatif" }, "Parent ", [20, 745, 200, 765]);
P.silence = el(P.parentTitre, "span", { title: "" }, "muet", [100, 748, 140, 762]);
P.curseur = el(body, "div", { title: "Une carte qui écoute le clic" }, "Carte", [210, 745, 380, 765]);
P.curseur.curseur = "pointer";
P.bas = el(body, "span", { title: "Un élément tout en bas" }, "Bas", [150, 770, 190, 790]);
P.droite = el(body, "span", { title: "Un élément contre le bord droit" }, "Droite", [360, 200, 398, 220]);
P.large = el(body, "span", { title: "Sur un écran plus large que la fenêtre visuelle" }, "Large", [440, 250, 480, 270]);
P.aide = el(body, "button", { "class": "aide-titre", type: "button", "aria-label": "Aide : Score global",
  "aria-expanded": "false", "aria-describedby": "aide-score" }, "?", [210, 340, 234, 364]);
P.aideTexte = el(body, "span", { id: "aide-score", hidden: "" }, "Calcul : (points conformes + points en cours × 0,5).", [0, 0, 0, 0]);
P.ecran = el(body, "section", { "class": "page" }, undefined, [0, 0, 400, 800]);
P.dansEcran = el(P.ecran, "span", { title: "Un élément d'un écran que go() masquera" }, "E", [20, 230, 60, 250]);
P.demonte = el(body, "span", { title: "Un élément que l'écran va démonter" }, "D", [70, 230, 110, 250]);
P.change = el(body, "button", { title: "Répondez aux 10 questions pour activer l'enregistrement." }, "Enregistrer", [120, 230, 200, 250]);
P.fuyant = el(body, "span", { title: "Un élément qui sortira de l'écran" }, "F", [210, 230, 250, 250]);
/* LES CHAMPS SOUS UN `title` PRÊTÉ PAR LEUR CONTENEUR. */
P.blocSaisie = el(body, "div", { title: "Aide du bloc de saisie" }, "Bloc ", [260, 230, 398, 330]);
P.champDansBloc = el(P.blocSaisie, "input", {}, undefined, [270, 260, 390, 280]);
P.zoneDansBloc = el(P.blocSaisie, "textarea", {}, undefined, [270, 285, 390, 325]);
P.labelSaisie = el(body, "label", { title: "Le numéro SIREN à neuf chiffres" }, "SIREN ", [260, 335, 398, 360]);
P.champDansLabel = el(P.labelSaisie, "input", { type: "text" }, undefined, [300, 338, 390, 357]);
P.labelCase = el(body, "label", { title: "Cocher pour activer la relance automatique" }, "Relance ", [260, 365, 398, 390]);
P.case = el(P.labelCase, "input", { type: "checkbox" }, undefined, [370, 370, 386, 386]);
const tabindexAvant = tous(racine).filter(e => e.hasAttribute("tabindex")).length;

/* ── LE SCRIPT. */
new Function("window", "document", "setTimeout", "clearTimeout", "setInterval", "clearInterval",
             "Date", "MutationObserver", src)(
  window, document, _setTimeout, _clear, _setInterval, _clear, _Date, MutationObserver);
const inscritsParLeScript = inscrits.slice();

/* LA FENÊTRE MODALE DE SENTINEL, telle qu'elle écoute Échap : sur
   `document`, en remontée. Et l'ACTION d'un élément : le clic qui atteint
   la remontée. */
let modaleFermee = 0, actions = 0;
document.addEventListener("keydown", ev => { if (ev.key === "Escape") modaleFermee++; });
document.addEventListener("click", () => { actions++; });

const B = () => bulleVue();
const vue = () => { const b = B(); return b ? { visible: !b.hidden, texte: b.textContent } : { visible: false, texte: "" }; };
const geo = () => B().getBoundingClientRect();
const croise = (a, b) => a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom;
const reinit = () => { if (window.bulleTitre) window.bulleTitre.fermer(); avancer(2000); document.activeElement = body; };

const out = { inscrits: inscritsParLeScript, sc: {} };
function scenario(nom, fn) {
  try { reinit(); out.sc[nom] = fn(); } catch (e) { out.sc[nom] = { erreur: String(e && e.stack || e).slice(0, 600) }; }
}

scenario("demarrage", () => {
  const b = B(), css = document.getElementById("css-bulle-titre");
  return {
    bulle: !!b, parent: b && b.parentElement === body, ariaHidden: b && b.getAttribute("aria-hidden"),
    role: b && b.getAttribute("role"), cachee: b && b.hidden,
    css: css ? css.textContent : null, cssDansHead: !!css && css.parentElement === head,
    api: window.bulleTitre ? Object.keys(window.bulleTitre).sort() : null,
    infobulles: opts.infobulles ? Object.keys(window.infobulles).sort() : (window.infobulles === undefined ? "absent" : "créé"),
    observateurs,
  };
});

scenario("appui", () => {
  const r = {};
  const c1 = appui(P.prio); r.premier = vue(); r.clic1 = { retenu: c1.retenu, arrete: c1.arrete };
  r.ariaHidden = B().getAttribute("aria-hidden");
  appui(P.prio); r.second = vue();
  appui(P.prio); r.troisieme = vue();
  appui(body); r.ailleurs = vue();
  appui(P.prio); appui(P.kpi); r.autre = vue();
  return r;
});

scenario("souris", () => {
  const r = {}; const a0 = actions;
  clicSouris(P.prio); r.generique = vue();
  pt("pointerdown", P.item, { pointerType: "mouse" }); avancer(700); pt("pointerup", P.item, { pointerType: "mouse" });
  r.long = vue();
  const c = emettre("click", evenement({ target: P.item })); r.clic = { retenu: c.retenu, arrete: c.arrete };
  const cm = emettre("contextmenu", evenement({ target: P.item, pointerType: "mouse" }));
  r.menu = { retenu: cm.retenu, vue: vue() };
  r.actions = actions - a0;
  reinit(); appui(P.prio); r.temoinDoigt = vue().visible;
  return r;
});

scenario("balayage", () => {
  const r = {};
  balayage(P.prio); r.sur = vue();
  balayage(P.kpi); appui(P.kpi); r.puisAppui = vue();
  appui(P.prio); balayage(P.kpi); r.ailleurs = vue();
  return r;
});

scenario("seuil", () => {
  const r = {};
  pt("pointerdown", P.prio); pt("pointermove", P.prio, { clientY: 40 }); pt("pointerup", P.prio, { clientY: 40 });
  r.glisse = vue(); reinit();
  pt("pointerdown", P.prio); pt("pointermove", P.prio, { clientX: 3, clientY: 5 }); pt("pointerup", P.prio, { clientX: 3, clientY: 5 });
  r.tremble = vue(); reinit();
  pt("pointerdown", P.prio); pt("pointermove", body, { pointerId: 2, clientY: 60 }); pt("pointerup", P.prio);
  r.autreDoigt = vue(); reinit();
  pt("pointerdown", P.prio); pt("pointerup", P.prio, { pointerId: 2 });
  r.autreRelache = vue(); reinit();
  pt("pointerdown", P.prio); pt("pointerup", P.kpi);
  r.relacheAilleurs = vue();
  return r;
});

scenario("longSurInerte", () => {
  appuiLong(P.prio, 700); const r = vue();
  /* LE TÉMOIN : le même élément, appuyé court, s'ouvre. */
  reinit(); appui(P.prio); r.temoin = vue().visible;
  return r;
});

scenario("appuiLong", () => {
  const r = {}; const a0 = actions;
  pt("pointerdown", P.item); avancer(400); r.a400 = vue();
  avancer(200); r.a600 = vue();
  pt("pointerup", P.item);
  const c = emettre("click", evenement({ target: P.item }));
  r.clic = { retenu: c.retenu, immediat: c.immediat }; r.actionsLong = actions - a0;
  r.apres = vue();
  avancer(500);
  const c2 = emettre("click", evenement({ target: P.item }));
  r.clicSuivant = { retenu: c2.retenu, immediat: c2.immediat };
  r.ouvertures = ouvertures;
  reinit();
  /* Le clic avalé ne vaut que pour l'élément tenu, et une seule fois. */
  pt("pointerdown", P.item); avancer(600); pt("pointerup", P.item);
  const c3 = emettre("click", evenement({ target: P.bouton }));
  r.clicAilleurs = { retenu: c3.retenu };
  reinit();
  /* ANDROID N'ÉMET PAS DE CLIC après un appui long : le clic à avaler ne
     vient jamais. Un appui ordinaire, une seconde plus tard, doit agir. */
  pt("pointerdown", P.item); avancer(600); pt("pointerup", P.item);
  avancer(1000);
  const a1 = actions; const c4 = appui(P.item);
  r.clicPlusTard = { retenu: c4.retenu, actions: actions - a1 };
  reinit();
  /* ANNULÉ PAR UN DÉFILEMENT OU UN GLISSÉ PENDANT L'APPUI. */
  pt("pointerdown", P.item); avancer(200); emettre("scroll", evenement({ target: document })); avancer(500);
  r.defile = vue(); pt("pointercancel", P.item); reinit();
  pt("pointerdown", P.item); avancer(200); pt("pointermove", P.item, { clientX: 20 }); avancer(500);
  r.glisse = vue(); pt("pointerup", P.item); reinit();
  pt("pointerdown", P.item); avancer(200); pt("pointercancel", P.item); avancer(500);
  r.annule = vue();
  return r;
});

scenario("appuiCourtQuiAgit", () => {
  const a0 = actions;
  const c = appui(P.bouton);
  const r = { vue: vue(), retenu: c.retenu, actions: actions - a0 };
  reinit(); pt("pointerdown", P.bouton); avancer(600); r.temoinLong = vue().visible; pt("pointerup", P.bouton);
  return r;
});

scenario("appuiCourtFermeLaBulleDeLElement", () => {
  const r = {};
  pt("pointerdown", P.item); avancer(600); pt("pointerup", P.item); emettre("click", evenement({ target: P.item }));
  r.ouverte = vue();
  avancer(1000);
  const a0 = actions;
  appui(P.item); r.apres = vue(); r.actions = actions - a0;
  return r;
});

scenario("lien", () => {
  const r = {};
  appui(P.lien); r.appui = vue();
  appuiLong(P.lien, 700); r.long = vue();
  pt("pointerdown", P.lien); avancer(550);
  const cm = emettre("contextmenu", evenement({ target: P.lien, pointerType: "touch" }));
  r.menu = { retenu: cm.retenu, vue: vue() };
  pt("pointerup", P.lien);
  /* LE TÉMOIN : le même lien, au clavier, a sa bulle — il est éligible. */
  reinit(); tab(P.lien); avancer(600); r.temoinClavier = vue().visible;
  return r;
});

scenario("contextmenu", () => {
  const r = {};
  let s0 = selectionsVidees, o0 = ouvertures;
  pt("pointerdown", P.item); avancer(300);
  let cm = emettre("contextmenu", evenement({ target: P.item, pointerType: "touch" }));
  r.touch = { retenu: cm.retenu, vue: vue(), selection: selectionsVidees - s0, ouvertures: ouvertures - o0 };
  avancer(400); r.touch.ouverturesApresMinuteur = ouvertures - o0;
  pt("pointerup", P.item); const c = emettre("click", evenement({ target: P.item }));
  r.touch.clic = c.retenu;
  reinit();
  /* LE MINUTEUR D'ABORD, `contextmenu` ENSUITE : l'ouverture est idempotente. */
  o0 = ouvertures;
  pt("pointerdown", P.item); avancer(600);
  cm = emettre("contextmenu", evenement({ target: P.item, pointerType: "touch" }));
  r.apresMinuteur = { retenu: cm.retenu, vue: vue(), ouvertures: ouvertures - o0 };
  pt("pointerup", P.item); reinit();
  cm = emettre("contextmenu", evenement({ target: P.item, pointerType: "pen" }));
  r.stylet = { retenu: cm.retenu, vue: vue() }; reinit();
  pt("pointerdown", P.item); avancer(300);
  cm = emettre("contextmenu", evenement({ target: P.item }));
  r.sansTypeApresDoigt = { retenu: cm.retenu, vue: vue() }; pt("pointerup", P.item); reinit();
  pt("pointerdown", P.item, { pointerType: "mouse" }); pt("pointerup", P.item, { pointerType: "mouse" });
  cm = emettre("contextmenu", evenement({ target: P.item }));
  r.sansTypeApresSouris = { retenu: cm.retenu, vue: vue() }; reinit();
  cm = emettre("contextmenu", evenement({ target: P.item, pointerType: "mouse" }));
  r.clavier = { retenu: cm.retenu, vue: vue() }; reinit();
  pt("pointerdown", P.prio); avancer(550);
  cm = emettre("contextmenu", evenement({ target: P.prio, pointerType: "touch" }));
  r.inerte = { retenu: cm.retenu, vue: vue() }; pt("pointerup", P.prio);
  return r;
});

scenario("selection", () => {
  const r = {};
  pt("pointerdown", P.item); avancer(100);
  const texte = P.item.enfants.find(e => e.nodeType === 3);
  r.longTexte = emettre("selectstart", evenement({ target: texte })).retenu;
  pt("pointerup", P.item); reinit();
  pt("pointerdown", P.prio); avancer(100);
  r.inerte = emettre("selectstart", evenement({ target: P.prioTexte })).retenu;
  pt("pointerup", P.prio); reinit();
  r.sansGeste = emettre("selectstart", evenement({ target: texte })).retenu;
  return r;
});

scenario("exclusions", () => {
  const r = {};
  for (const k of ["champ", "caseTitree", "iframe", "option", "svgRect", "dansGraphe", "tt"]) {
    reinit(); appui(P[k]); const a = vue().visible;
    reinit(); appuiLong(P[k], 700); r[k] = a || vue().visible;
  }
  reinit(); appui(P.prio); r.temoin = vue().visible;
  return r;
});

scenario("preseance", () => {
  const r = {};
  appui(P.tipDansBloc); r.tipDansTitre = vue();
  reinit(); appui(P.bloc); r.titreAutour = vue();
  reinit(); appui(P.titreDansTip); r.titreDansTip = vue();
  reinit(); appui(P.silence); r.silence = vue();
  reinit(); appuiLong(P.puce, 700); r.puce = vue();
  reinit(); appuiLong(P.icone, 700); r.iconeDeLaLigne = vue();
  return r;
});

scenario("nonInformatif", () => {
  const r = {};
  for (const k of ["raccourci", "repete", "court", "nomme", "etiquete"]) {
    reinit(); appui(P[k]); const a = vue().visible;
    reinit(); appuiLong(P[k], 700); r[k] = a || vue().visible;
  }
  reinit(); appui(P.kpi); r.temoin = vue().visible;
  reinit(); pt("pointerdown", P.curseur); avancer(80); pt("pointerup", P.curseur); r.curseurAppuiCourt = vue().visible;
  reinit(); pt("pointerdown", P.curseur); avancer(600); r.curseurAppuiLong = vue().visible; pt("pointerup", P.curseur);
  return r;
});

scenario("clavier", () => {
  const r = {};
  tab(P.item); avancer(400); r.a400 = vue(); avancer(200); r.a600 = vue();
  quitter(P.item, body); r.depart = vue();
  reinit();
  /* LE FOCUS PART VERS RIEN avant les 500 ms : pas de bulle pour un
     élément qu'on a quitté. */
  tab(P.item); avancer(200); quitter(P.item); avancer(600); r.partiAvant = vue();
  reinit();
  const o0 = ouvertures, items = [P.item, P.item2, P.lien, P.bouton, P.item];
  let intermediaires = 0;
  for (const e of items) { tab(e); avancer(100); if (vue().visible) intermediaires++; }
  r.cinq = { intermediaires, avant: ouvertures - o0 };
  avancer(450); r.cinq.apres500 = ouvertures - o0; r.cinq.texte = vue().texte;
  reinit();
  /* Une tabulation, PUIS un appui du doigt : le focus qui suit est celui du
     doigt, même dans la seconde qui suit la touche. */
  emettre("keydown", evenement({ key: "Tab" }));
  pt("pointerdown", P.bouton); pt("pointerup", P.bouton); focusSur(P.item); avancer(600);
  r.focusApresDoigt = vue();
  reinit();
  emettre("keydown", evenement({ key: "Tab" })); emettre("keydown", evenement({ key: "Enter" }));
  focusSur(P.item); avancer(600); r.focusApresEntree = vue();
  reinit();
  emettre("keydown", evenement({ key: "Tab" })); avancer(1200); focusSur(P.item); avancer(600);
  r.focusTardif = vue();
  reinit();
  tab(P.item, "ArrowDown"); avancer(600); r.fleche = vue();
  reinit();
  tab(P.lien); avancer(600); r.lien = vue();
  reinit();
  tab(P.champ); avancer(600); r.champ = vue();
  reinit();
  tab(P.item); avancer(600); quitter(P.item, P.puce); r.versLeDedans = vue();
  return r;
});

scenario("echap", () => {
  const r = {};
  tab(P.item); avancer(600); r.ouverte = vue(); modaleFermee = 0;
  const e1 = emettre("keydown", evenement({ key: "Escape" }));
  r.premier = { vue: vue(), modale: modaleFermee, retenu: e1.retenu, immediat: e1.immediat };
  const e2 = emettre("keydown", evenement({ key: "Escape" }));
  r.second = { modale: modaleFermee, retenu: e2.retenu };
  /* REPLIÉE tant que le focus reste sur l'élément. */
  focusSur(P.icone); emettre("keydown", evenement({ key: "Tab" })); focusSur(P.item); avancer(600);
  r.repliee = vue();
  tab(P.item2); avancer(600); tab(P.item); avancer(600);
  r.apresDepart = vue();
  reinit(); modaleFermee = 0;
  appui(P.prio); const e3 = emettre("keydown", evenement({ key: "Escape" }));
  r.auDoigt = { vue: vue(), modale: modaleFermee, retenu: e3.retenu };
  return r;
});

scenario("placement", () => {
  const r = {};
  appui(P.prio); const g = geo(), a = P.prio.getBoundingClientRect();
  r.dessous = { top: g.top, attendu: a.bottom + 6, croise: croise(g, a),
                centre: Math.round(g.left + g.width / 2), centreAncre: (a.left + a.right) / 2 };
  reinit(); appui(P.bas); const gb = geo(), ab = P.bas.getBoundingClientRect();
  r.dessus = { bas: gb.bottom, attendu: ab.top - 6, croise: croise(gb, ab), dansVV: gb.top >= 8 };
  reinit(); appui(P.droite); const gd = geo();
  r.droite = { droite: gd.right, borne: 400 - 8, croise: croise(gd, P.droite.getBoundingClientRect()) };
  reinit();
  /* LA FENÊTRE VISUELLE PLUS ÉTROITE QUE LA MISE EN PAGE (Pixel 7, écran de
     maturité : 491 contre 412). */
  window.innerWidth = 491; visualViewport.width = 412; visualViewport.offsetLeft = 40;
  P.large.rect = [440, 250, 480, 270];
  appui(P.large); const gl = geo();
  r.fenetreVisuelle = { droite: gl.right, borne: 40 + 412 - 8, gauche: gl.left, borneGauche: 40 + 8 };
  reinit();
  window.innerWidth = 400; visualViewport.width = 400; visualViewport.offsetLeft = 0;
  tab(P.item); avancer(600); const gm = geo();
  r.menuEtroit = { gauche: gm.left, croise: croise(gm, P.item.getBoundingClientRect()) };
  reinit();
  window.innerWidth = 1280; visualViewport.width = 1280;
  tab(P.item); avancer(600); const gp = geo(), ai = P.item.getBoundingClientRect();
  r.menuPoste = { gauche: gp.left, attendu: 240 + 8, top: gp.top, topAncre: ai.top, croise: croise(gp, ai) };
  reinit();
  window.innerWidth = 400; visualViewport.width = 400;
  return r;
});

scenario("sorties", () => {
  const r = {};
  /* Un BOUTON : ouvert au clavier, comme le lirait qui tabule. */
  tab(P.change); avancer(600); r.ouverte = vue();
  P.change.attrs.title = "Enregistrer cette évaluation FRIA dans l'historique.";
  avancer(260); r.titreChange = vue();
  P.change.attrs.title = ""; avancer(260); r.titreVide = vue();
  P.change.attrs.title = "Répondez aux 10 questions pour activer l'enregistrement.";
  reinit(); appui(P.dansEcran); r.ecranOuvert = vue();
  P.ecran.masque = true; avancer(260); r.ecranMasque = vue(); P.ecran.masque = false;
  reinit(); appui(P.demonte); r.demonteOuvert = vue();
  P.demonte.remove(); avancer(260); r.demonte = vue();
  reinit();
  r.minuteursAuRepos = minuteurs.filter(m => m.every).length;
  appui(P.fuyant); r.intervalleOuvert = minuteurs.filter(m => m.every).length;
  window.bulleTitre.fermer(); r.intervalleFerme = minuteurs.filter(m => m.every).length;
  appui(P.fuyant);
  P.fuyant.rect = [210, -100, 250, -80]; emettre("scroll", evenement({ target: document })); avancer(20);
  r.horsEcran = vue();
  return r;
});

scenario("defilement", () => {
  const r = {};
  P.fuyant.rect = [210, 230, 250, 250];
  appui(P.fuyant); r.ouverte = vue(); P.fuyant.rect = [210, 180, 250, 200];
  emettre("scroll", evenement({ target: document })); avancer(20);
  r.suit = { vue: vue(), top: geo().top, attendu: 200 + 6 };
  emettreVV("scroll"); emettreVV("resize"); avancer(20); r.vv = vue();
  emettre("resize", evenement({})); avancer(20); r.hauteurSeule = vue();
  window.innerWidth = 500; emettre("resize", evenement({})); r.largeur = vue(); window.innerWidth = 400;
  emettre("resize", evenement({}));
  appui(P.prio); emettre("orientationchange", evenement({})); r.orientation = vue();
  P.fuyant.rect = [210, 230, 250, 250];
  return r;
});

scenario("aide", () => {
  const r = {};
  clicSouris(P.aide);
  r.clic1 = { vue: vue(), expanded: P.aide.getAttribute("aria-expanded") };
  clicSouris(P.aide);
  r.clic2 = { vue: vue(), expanded: P.aide.getAttribute("aria-expanded") };
  /* CHAQUE SORTIE PART D'UNE BULLE RÉELLEMENT OUVERTE : sinon « fermée,
     aria-expanded=false » serait vrai d'avance. */
  clicSouris(P.aide); let avant = vue().visible && P.aide.getAttribute("aria-expanded") === "true";
  emettre("keydown", evenement({ key: "Escape" }));
  r.echap = { vue: vue(), expanded: P.aide.getAttribute("aria-expanded"), avant };
  focusSur(P.aide); clicSouris(P.aide); avant = vue().visible && P.aide.getAttribute("aria-expanded") === "true";
  quitter(P.aide, body);
  r.depart = { vue: vue(), expanded: P.aide.getAttribute("aria-expanded"), avant };
  appui(P.aide); r.doigt = { vue: vue(), expanded: P.aide.getAttribute("aria-expanded") };
  avant = r.doigt.vue.visible && r.doigt.expanded === "true";
  appui(body); r.ailleurs = { vue: vue(), expanded: P.aide.getAttribute("aria-expanded"), avant };
  /* OUVERT, PUIS APPUYÉ AU DOIGT : le relâcher ne doit pas le fermer avant
     que son clic ne fasse la bascule — sinon le clic le rouvre. */
  reinit(); clicSouris(P.aide); avant = vue().visible;
  appui(P.aide); r.doigtFerme = { vue: vue(), expanded: P.aide.getAttribute("aria-expanded"), avant };
  return r;
});

/* ── ENTRÉE ET ESPACE : l'élément est activé, sa bulle a fini de servir. */
scenario("entree", () => {
  const r = {};
  tab(P.bouton); avancer(600); r.ouverte = vue();
  const e = emettre("keydown", evenement({ key: "Enter" }));
  r.entree = { vue: vue(), retenu: e.retenu };
  emettre("click", evenement({ target: P.bouton })); avancer(600);
  r.pasRouverte = vue();
  reinit();
  tab(P.item); avancer(600); r.ouverteMenu = vue();
  emettre("keydown", evenement({ key: " " })); r.espace = vue();
  reinit();
  /* ESPACE HORS DE L'ÉLÉMENT : la page défile, la bulle reste. */
  appui(P.prio); r.ouverteDoigt = vue();
  emettre("keydown", evenement({ key: " " })); r.espaceAilleurs = vue();
  reinit();
  /* LE BOUTON D'AIDE : Entrée, puis son clic natif, trois fois. */
  focusSur(P.aide);
  r.aide = [];
  for (let i = 0; i < 3; i++) {
    emettre("keydown", evenement({ key: "Enter" })); emettre("click", evenement({ target: P.aide }));
    r.aide.push({ vue: vue().visible, expanded: P.aide.getAttribute("aria-expanded") });
  }
  return r;
});

/* ── UNE BULLE À LA FOIS, D'UN SCRIPT À L'AUTRE. */
scenario("croise", () => {
  const r = {};
  let f0 = infobullesFermees;
  balayage(P.prio); r.balayage = infobullesFermees - f0;
  f0 = infobullesFermees; appui(P.prio); r.appui = { vue: vue(), fermees: infobullesFermees - f0 };
  reinit();
  f0 = infobullesFermees; tab(P.item); avancer(600); r.tab = { vue: vue(), fermees: infobullesFermees - f0 };
  reinit();
  f0 = infobullesFermees; pt("pointerdown", P.item); avancer(600); r.long = { vue: vue(), fermees: infobullesFermees - f0 };
  pt("pointerup", P.item); emettre("click", evenement({ target: P.item }));
  /* LA PASTILLE TUE DANS LA LIGNE OUVERTE : un appui ailleurs. */
  reinit(); appuiLong(P.item, 700); r.puceAvant = vue().visible;
  appui(P.puce); r.puce = vue();
  /* LE DÉCLENCHEUR data-tip DANS UN BLOC À `title` OUVERT : ailleurs aussi. */
  reinit(); appui(P.bloc); r.tipAvant = vue().visible;
  appui(P.tipDansBloc); r.tip = vue();
  return r;
});

/* ── `prend` : CE RELÂCHER EST-IL À NOUS ? Demandé au moment où
   /infobulles.js le lit : après le contact, avant le relâcher. */
scenario("prend", () => {
  const r = {};
  const demande = (cible, extra) => window.bulleTitre.prend(evenement(Object.assign({ pointerType: "touch", target: cible }, extra)));
  pt("pointerdown", P.titreDansTip); avancer(80); r.inerte = demande(P.titreDansTip); pt("pointerup", P.titreDansTip);
  reinit(); pt("pointerdown", P.item); avancer(600); r.long = demande(P.item); pt("pointerup", P.item);
  emettre("click", evenement({ target: P.item }));
  reinit(); pt("pointerdown", P.bouton); avancer(80); r.boutonCourt = demande(P.bouton); pt("pointerup", P.bouton);
  reinit(); pt("pointerdown", P.prio); avancer(700); r.inerteTenu = demande(P.prio); pt("pointerup", P.prio);
  reinit(); pt("pointerdown", P.prio); avancer(80); r.autreDoigt = demande(P.prio, { pointerId: 2 }); pt("pointerup", P.prio);
  reinit(); r.sansGeste = demande(P.prio);
  pt("pointerdown", P.prio); avancer(80); r.autreAncre = demande(P.kpi); pt("pointerup", P.prio);
  return r;
});

/* ── LES CHAMPS N'EMPRUNTENT PAS LA BULLE DE LEUR CONTENEUR. */
scenario("saisie", () => {
  const r = {};
  appui(P.champDansBloc); r.appuiDansBloc = vue().visible;
  reinit(); appui(P.zoneDansBloc); r.zoneDansBloc = vue().visible;
  reinit(); tab(P.champDansBloc); avancer(600); r.tabDansBloc = vue().visible;
  reinit(); pt("pointerdown", P.champDansLabel); avancer(300);
  const cm = emettre("contextmenu", evenement({ target: P.champDansLabel, pointerType: "touch" }));
  r.menuDansLabel = cm.retenu || vue().visible; pt("pointerup", P.champDansLabel);
  reinit(); pt("pointerdown", P.champDansLabel); avancer(700); r.longDansLabel = vue().visible; pt("pointerup", P.champDansLabel);
  /* LES TÉMOINS : le bloc lui-même, le libellé lui-même, la case à cocher. */
  reinit(); appui(P.blocSaisie); r.temoinBloc = vue().visible;
  reinit(); pt("pointerdown", P.labelSaisie); avancer(300);
  const cm2 = emettre("contextmenu", evenement({ target: P.labelSaisie, pointerType: "touch" }));
  r.temoinLabel = cm2.retenu && vue().visible; pt("pointerup", P.labelSaisie);
  reinit(); tab(P.case); avancer(600); r.temoinCase = vue().visible;
  return r;
});

/* ── LA LARGEUR : À DROITE DU MENU, ET DANS UNE FENÊTRE ÉTROITE. */
scenario("largeur", () => {
  const r = {};
  /* LE MENU SERRÉ : 280 px à droite du menu, une bulle qui en voudrait 320. */
  window.innerWidth = 520; visualViewport.width = 520; largeurNaturelle = 320;
  tab(P.item); avancer(600);
  const g = geo(), sb = P.sb.getBoundingClientRect();
  r.menuSerre = { vue: vue().visible, gauche: g.left, droite: g.right, borne: 520 - 8, sbDroite: sb.right,
                  croiseLigne: croise(g, P.item.getBoundingClientRect()), croiseMenu: croise(g, sb) };
  reinit();
  /* UNE BULLE PLUS LARGE QUE LA FENÊTRE VISUELLE. */
  window.innerWidth = 400; visualViewport.width = 400; largeurNaturelle = 600;
  appui(P.prio); const l = geo();
  r.large = { vue: vue().visible, gauche: l.left, droite: l.right, borneGauche: 8, borneDroite: 400 - 8 };
  reinit(); largeurNaturelle = 200;
  return r;
});

/* ── LA FENÊTRE VISUELLE BOUGE SANS QUE LA PAGE DÉFILE (zoom, clavier
   virtuel) : la bulle suit AVANT l'intervalle de 250 ms. */
scenario("fenetreVisuelle", () => {
  const r = {};
  appui(P.fuyant); r.ouverte = { vue: vue(), top: geo().top };
  /* La fenêtre visuelle raccourcit à 300 px : dessous ne tient plus, dessus. */
  visualViewport.height = 300; emettreVV("resize"); avancer(20);
  r.resize = { vue: vue(), top: geo().top, attendu: 230 - 6 - 40 };
  /* Elle revient : dessous de nouveau. */
  visualViewport.height = 800; emettreVV("scroll"); avancer(20);
  r.scroll = { vue: vue(), top: geo().top, attendu: 250 + 6 };
  return r;
});

scenario("api", () => {
  const r = {};
  window.bulleTitre.ouvrirPour(P.prio); r.ouvre = vue(); const o0 = ouvertures;
  window.bulleTitre.ouvrirPour(P.prio); r.idempotent = { vue: vue(), ouvertures: ouvertures - o0 };
  window.bulleTitre.fermer(); r.ferme = vue();
  return r;
});

out.tabindex = { avant: tabindexAvant, apres: tous(racine).filter(e => e.hasAttribute("tabindex")).length,
                 poses: poses.filter(p => p[1] === "tabindex") };
out.observateurs = observateurs;
process.stdout.write(JSON.stringify(out));
"""


@functools.lru_cache(maxsize=None)
def _executer(infobulles=True):
    if not NODE:
        pytest.skip("node absent : le script ne peut pas être exécuté")
    with tempfile.TemporaryDirectory() as d:
        h = os.path.join(d, "h.js")
        io.open(h, "w", encoding="utf-8").write(_HARNAIS)
        r = subprocess.run([NODE, h, os.path.join(_RACINE, "bulle-titre.js"),
                            json.dumps({"infobulles": infobulles})],
                           capture_output=True, text=True, timeout=90)
    if r.returncode != 0:
        pytest.fail("le script n'a pas tourné :\n%s" % (r.stderr or "")[-2500:])
    return json.loads(r.stdout)


def _sc(nom, infobulles=True):
    r = _executer(infobulles)["sc"][nom]
    assert "erreur" not in r, "le scénario %s a levé : %s" % (nom, r.get("erreur"))
    return r


def _corps_ecouteur(type_, src=CODE):
    """Le corps de chaque `addEventListener("<type>", function … { … })` du
    script, accolades équilibrées — lu dans le CODE, pas les commentaires."""
    corps = []
    for m in re.finditer(r'addEventListener\("%s",\s*function\s*\([^)]*\)\s*\{' % re.escape(type_), src):
        i, prof = m.end(), 1
        while i < len(src) and prof:
            prof += {"{": 1, "}": -1}.get(src[i], 0)
            i += 1
        corps.append(src[m.end():i - 1])
    return corps


# ══════════════════════════════════════════════════════════════════════════
#  1. LE SCRIPT EST CHARGÉ LÀ OÙ IL Y A DES `title` — APRÈS /infobulles.js
# ══════════════════════════════════════════════════════════════════════════

def _pages_a_titres():
    """Les pages qui chargent /infobulles.js ET portent un `title`, lues sur
    le disque — pas une liste recopiée, qui ne saurait pas qu'une page en a
    reçu."""
    out = []
    for nom in sorted(os.listdir(_RACINE)):
        if nom.endswith(".html"):
            txt = _lire(nom)
            if "/infobulles.js" in txt and 'title="' in txt:
                out.append(nom)
    return out


def test_toute_page_a_title_qui_charge_infobulles_charge_AUSSI_bulle_titre():
    """SANS LE SCRIPT, LE `title` RESTE UNE DÉCORATION DE POSTE FIXE. Une
    page qui gagnerait des `title` demain sans le charger rendrait le défaut
    sans que rien ne le dise."""
    pages = _pages_a_titres()
    assert len(pages) >= 3, (
        "moins de trois pages à `title` chargent /infobulles.js (%s) : la "
        "lecture a changé de forme, cette règle ne mesure plus rien" % pages)
    manquantes = [p for p in pages if "/bulle-titre.js" not in _lire(p)]
    assert not manquantes, (
        "ces pages portent des `title` sans charger /bulle-titre.js — ils ne "
        "se liront ni au doigt ni au clavier : %s" % manquantes)


@pytest.mark.parametrize("page", ["sentinel.html", "index.html", "panorama.html"])
def test_la_page_charge_bulle_titre_APRES_infobulles(page):
    """APRÈS : /bulle-titre.js lit `window.infobulles.selecteur` pour céder
    la place à une bulle data-tip posée sur le même élément. Chargé avant,
    il la lirait encore à l'usage — mais l'ordre dit l'intention, et un
    `defer` les exécute dans cet ordre."""
    txt = _lire(page)
    i = txt.find('<script src="/infobulles.js" defer></script>')
    j = txt.find('<script src="/bulle-titre.js" defer></script>')
    assert i >= 0, "%s ne charge plus /infobulles.js" % page
    assert j >= 0, "%s ne charge pas /bulle-titre.js en `defer`" % page
    assert j > i, "%s charge /bulle-titre.js AVANT /infobulles.js" % page
    assert txt.count("/bulle-titre.js") == 1, "%s charge /bulle-titre.js deux fois" % page


def test_la_formation_n_a_aucun_title_et_ne_charge_pas_le_script():
    """PAS DE SCRIPT SANS OBJET. `formation.html` n'a aucun `title`."""
    txt = _lire("formation.html")
    assert "/infobulles.js" in txt, "la formation ne charge plus /infobulles.js : règle à revoir"
    assert 'title="' not in txt and "/bulle-titre.js" not in txt


def test_infobulles_garde_ses_DEUX_conventions_et_rien_d_autre():
    """LES INVARIANTS D'/infobulles.js RESTENT VRAIS. Le chemin `title` vit
    ailleurs ; il n'a pas été glissé dans l'autre script."""
    m = re.search(r'var SELECTEUR\s*=\s*"([^"]+)"', INFOBULLES)
    assert m and m.group(1) == "[data-tooltip],[data-tip]", m and m.group(1)
    assert "[title]" not in INFOBULLES, "/infobulles.js ramasse les `title` natifs"
    assert "/bulle-titre.js" in INFOBULLES, (
        "/infobulles.js ne dit plus où vit le chemin `title`")


# ══════════════════════════════════════════════════════════════════════════
#  2. CE QUE LE SCRIPT S'INTERDIT
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("interdit", ["mouseover", "mouseenter", "pointerover",
                                      'setAttribute("tabindex"', "MutationObserver"],
                         ids=["mouseover", "mouseenter", "pointerover", "tabindex", "MutationObserver"])
def test_le_script_n_ecrit_pas(interdit):
    """PAS DE SURVOL : la souris a déjà la bulle du navigateur — une seconde
    ferait deux bulles l'une sur l'autre. PAS DE `tabindex` : mesuré dans
    Chromium, un <div> focalisable prend son `title` pour NOM, et « 72 % »
    disparaît. PAS D'OBSERVATEUR : l'éligibilité se calcule à l'événement."""
    assert "function ancreDe" in CODE, "le code du script n'a pas pu être isolé"
    assert interdit not in CODE, "le script écrit %r" % interdit


def test_le_script_ne_pose_AUCUN_tabindex_a_l_execution():
    """LU À L'EXÉCUTION, APRÈS TOUS LES SCÉNARIOS : aucun élément n'a gagné
    de `tabindex`, et aucun observateur n'a été créé."""
    r = _executer()
    # LE TÉMOIN : le script a bien ouvert des bulles pendant ces scénarios.
    # Un script qui ne ferait RIEN ne poserait aucun tabindex non plus.
    assert _sc("appui")["premier"]["visible"] and _sc("clavier")["a600"]["visible"], (
        "le script n'a rien ouvert : le contrôle ne mesurerait rien")
    assert r["tabindex"]["poses"] == [] and r["tabindex"]["apres"] == r["tabindex"]["avant"], r["tabindex"]
    assert r["observateurs"] == 0, "%d observateur(s) créé(s)" % r["observateurs"]


def test_aucun_ecouteur_de_DEFILEMENT_n_appelle_fermer():
    """FERMER AU DÉFILEMENT, C'EST NE JAMAIS OUVRIR AU DOIGT — mesuré sur
    /infobulles.js : amener l'élément à l'écran émet des dizaines de
    défilements APRÈS l'appui. Lu dans le code…"""
    corps = _corps_ecouteur("scroll")
    assert corps, "aucun écouteur de défilement : la bulle ne suivrait plus son élément"
    fautifs = [c for c in corps if "fermer" in c]
    assert not fautifs, "un écouteur de défilement ferme la bulle : %s" % fautifs


def test_au_DEFILEMENT_la_bulle_SUIT_son_element():
    """…et mesuré à l'exécution : un défilement replace, il ne ferme pas."""
    r = _sc("defilement")
    assert r["ouverte"]["visible"], "la bulle n'était pas ouverte : le contrôle ne mesurerait rien"
    assert r["suit"]["vue"]["visible"], "le défilement a fermé la bulle"
    assert r["suit"]["top"] == r["suit"]["attendu"], (
        "la bulle ne suit pas son élément : top %r au lieu de %r" % (r["suit"]["top"], r["suit"]["attendu"]))
    assert r["vv"]["visible"], "un défilement de la fenêtre visuelle a fermé la bulle"


def test_le_redimensionnement_ne_ferme_que_s_il_change_la_LARGEUR():
    """LA BARRE D'ADRESSE QUI SE RÉTRACTE n'émet qu'un changement de hauteur :
    la bulle reste. Une largeur qui change, une rotation : elle ferme."""
    r = _sc("defilement")
    assert r["hauteurSeule"]["visible"], "un redimensionnement en hauteur seule a fermé la bulle"
    assert not r["largeur"]["visible"], "un changement de largeur laisse la bulle ouverte"
    assert not r["orientation"]["visible"], "une rotation laisse la bulle ouverte"


# ══════════════════════════════════════════════════════════════════════════
#  3. CE QUE LE SCRIPT PUBLIE AU DÉMARRAGE
# ══════════════════════════════════════════════════════════════════════════

def test_la_bulle_existe_au_demarrage_CACHEE_et_MUETTE():
    """UNE SEULE BULLE, dans `body`, `aria-hidden` : ce qu'elle montre est
    déjà le nom ou la description de l'élément — l'annoncer le ferait
    entendre deux fois."""
    r = _sc("demarrage")
    assert r["bulle"] and r["parent"], "la bulle n'est pas créée dans body au démarrage"
    assert r["ariaHidden"] == "true" and r["role"] == "presentation", r
    assert r["cachee"], "la bulle est visible au repos"


def test_la_feuille_est_A_PART_et_la_bulle_passe_AU_DESSUS_des_fenetres():
    """`z-index` 10060 : au-dessus de `.mat-modal` (10020) et de sa
    surcouche (10050). Une feuille à elle, distincte de celle
    d'/infobulles.js."""
    r = _sc("demarrage")
    css = r["css"]
    assert css and r["cssDansHead"], "la feuille #css-bulle-titre n'est pas publiée dans <head>"
    m = re.search(r"#bulle-titre\{([^}]*)\}", css)
    assert m, "la bulle n'a pas de règle dans la feuille"
    z = re.search(r"z-index:(\d+)", m.group(1))
    assert z and int(z.group(1)) >= 10060, "z-index de la bulle : %r" % (z and z.group(1))
    assert "position:fixed" in m.group(1) and "pointer-events:none" in m.group(1), m.group(1)
    assert "#bulle-titre[hidden]{display:none}" in css


def test_l_appui_long_ne_selectionne_pas_ce_qui_AGIT_et_seulement_cela():
    """SUR UN ÉCRAN TACTILE, sur ce qui agit : ni sélection, ni aperçu. Rien
    sur un lien (il garde son menu), rien sur un élément inerte (son texte
    reste à copier)."""
    css = _sc("demarrage")["css"]
    m = re.search(r"@media \(hover:none\) and \(pointer:coarse\)\{([^{}]*)\{([^}]*)\}\}", css)
    assert m, "la règle tactile de l'appui long n'est pas publiée"
    sels = set(s.strip() for s in m.group(1).split(","))
    assert {"button[title]", "[role=button][title]", "[onclick][title]"} <= sels, sels
    assert not any(s.startswith("a") or s == "[title]" for s in sels), sels
    assert "user-select:none" in m.group(2) and "-webkit-touch-callout:none" in m.group(2), m.group(2)


def test_l_API_est_publiee_et_window_infobulles_n_est_pas_touche():
    """`window.bulleTitre = { fermer, ouvrirPour, prend }`. Le script LIT
    `window.infobulles` et appelle son `fermer` ; il ne le crée ni ne le
    modifie. `prend` est la question qu'/infobulles.js lui pose au relâcher
    (écart assumé à la spécification §2.1 : voir la règle de `prend`)."""
    r = _sc("demarrage")
    assert r["api"] == ["fermer", "ouvrirPour", "prend"], r["api"]
    assert r["infobulles"] == ["fermer", "selecteur"], "window.infobulles a été modifié : %r" % r["infobulles"]
    assert _sc("demarrage", infobulles=False)["infobulles"] == "absent", (
        "le script crée window.infobulles quand /infobulles.js est absent")
    assert _sc("appui", infobulles=False)["premier"]["visible"], (
        "sans /infobulles.js, l'appui n'ouvre plus rien")


def test_l_API_ouvre_sans_basculer():
    r = _sc("api")
    assert r["ouvre"]["visible"] and r["idempotent"]["vue"]["visible"], r
    assert r["idempotent"]["ouvertures"] == 0, "ouvrirPour sur la bulle déjà ouverte l'a rouverte"
    assert not r["ferme"]["visible"]


# ══════════════════════════════════════════════════════════════════════════
#  4. AU DOIGT — exécuté
# ══════════════════════════════════════════════════════════════════════════

def test_l_APPUI_sur_un_element_inerte_ouvre_et_le_second_ferme():
    """LE CŒUR DU DÉFAUT : la pastille « P1 », au doigt, n'affichait rien.
    Et l'appui n'annule rien — le texte reste sélectionnable, le clic passe."""
    r = _sc("appui")
    assert r["premier"]["visible"], "l'appui n'ouvre pas la bulle"
    assert r["premier"]["texte"] == "P1 : obligation critique, à traiter en premier", r["premier"]
    assert r["ariaHidden"] == "true"
    assert not r["clic1"]["retenu"] and not r["clic1"]["arrete"], "l'appui sur un élément inerte retient son clic"
    assert not r["second"]["visible"], "le second appui ne ferme pas"
    assert r["troisieme"]["visible"], "le troisième appui ne rouvre pas"


def test_un_appui_AILLEURS_ferme_ou_passe_a_l_autre():
    r = _sc("appui")
    assert not r["ailleurs"]["visible"], "un appui ailleurs laisse la bulle ouverte"
    assert r["autre"]["visible"] and r["autre"]["texte"].startswith("Calcul"), (
        "l'appui sur un autre élément n'ouvre pas SA bulle : %r" % r["autre"])


def test_la_SOURIS_n_ouvre_jamais_rien():
    """LE NAVIGATEUR MONTRE DÉJÀ LE `title` À LA SOURIS : une seconde bulle
    ferait deux bulles au poste fixe. Ni le clic, ni le clic tenu, ni le
    menu contextuel de la souris ou du clavier."""
    r = _sc("souris")
    assert r["temoinDoigt"], "le même élément ne s'ouvre pas au doigt : le contrôle ne mesurerait rien"
    assert not r["generique"]["visible"], "un clic de souris ouvre la bulle"
    assert not r["long"]["visible"], "un clic tenu de souris ouvre la bulle"
    assert not r["clic"]["retenu"] and not r["menu"]["retenu"], r
    assert not r["menu"]["vue"]["visible"]
    assert r["actions"] == 2, "les clics de souris n'ont pas agi : %r" % r["actions"]


def test_un_BALAYAGE_n_ouvre_rien_et_ne_ferme_rien():
    """LE NAVIGATEUR ANNULE LE POINTEUR QUAND LA PAGE DÉFILE : ce n'est pas un
    appui. La bulle ouverte survit à un balayage ailleurs ; l'appui qui suit
    un balayage ouvre normalement."""
    r = _sc("balayage")
    assert not r["sur"]["visible"], "un balayage a ouvert la bulle"
    assert r["puisAppui"]["visible"], "après un balayage, l'appui n'ouvre plus"
    assert r["ailleurs"]["visible"], "un balayage ailleurs a fermé la bulle"


def test_le_seuil_de_10_px_et_le_MEME_doigt_sur_la_MEME_ancre():
    r = _sc("seuil")
    assert not r["glisse"]["visible"], "un glissé de 40 px a ouvert la bulle"
    assert r["tremble"]["visible"], "un tremblement de 6 px n'ouvre plus"
    assert r["autreDoigt"]["visible"], "le glissé d'un autre doigt a annulé l'appui"
    assert not r["autreRelache"]["visible"], "le relâcher d'un autre doigt a ouvert la bulle"
    assert not r["relacheAilleurs"]["visible"], "un geste relâché sur une autre ancre a ouvert"


def test_l_appui_long_sur_un_element_INERTE_garde_la_selection_native():
    """AU-DELÀ DE 500 MS SUR UN ÉLÉMENT INERTE : rien. Son texte reste à
    sélectionner pour être copié."""
    r = _sc("longSurInerte")
    assert r["temoin"], "le témoin (appui court) ne s'ouvre pas : le contrôle ne mesurerait rien"
    assert not r["visible"], "l'appui long sur un élément inerte ouvre la bulle"


def test_l_APPUI_LONG_ouvre_sur_ce_qui_agit_et_AVALE_le_clic_du_relacher():
    """LA LIGNE DU MENU, AU DOIGT : l'appui court y va, l'appui long explique.
    Le minuteur de 500 ms est le chemin iOS (Safari n'émet pas
    `contextmenu`) ; le clic que Safari peut émettre au relâcher est avalé —
    sinon on naviguerait en voulant seulement lire."""
    r = _sc("appuiLong")
    assert not r["a400"]["visible"], "la bulle s'ouvre avant 500 ms"
    assert r["a600"]["visible"], "l'appui long n'ouvre pas la bulle"
    assert r["clic"]["retenu"] and r["clic"]["immediat"], "le clic du relâcher n'est pas avalé : %r" % r["clic"]
    assert r["actionsLong"] == 0, "l'élément a agi après un appui long"
    assert r["apres"]["visible"], "la bulle se ferme au relâcher de l'appui long"
    assert not r["clicSuivant"]["retenu"], "un clic ultérieur est encore avalé"
    assert not r["clicAilleurs"]["retenu"], "un clic sur un AUTRE élément a été avalé"
    assert not r["clicPlusTard"]["retenu"] and r["clicPlusTard"]["actions"] == 1, (
        "sans clic au relâcher, l'appui suivant est avalé : %r" % r["clicPlusTard"])


@pytest.mark.parametrize("annulation", ["defile", "glisse", "annule"])
def test_l_appui_long_est_ANNULE_par_un_defilement_un_glisse_ou_le_navigateur(annulation):
    r = _sc("appuiLong")
    assert r["a600"]["visible"], "le témoin (appui long) ne s'ouvre pas : le contrôle ne mesurerait rien"
    assert not r[annulation]["visible"], (
        "l'appui long s'ouvre malgré « %s »" % annulation)


def test_l_appui_COURT_sur_ce_qui_agit_garde_son_action_sans_bulle():
    r = _sc("appuiCourtQuiAgit")
    assert r["temoinLong"], "le bouton ne s'ouvre pas à l'appui long : le contrôle ne mesurerait rien"
    assert not r["vue"]["visible"], "l'appui court sur un bouton ouvre la bulle"
    assert not r["retenu"] and r["actions"] == 1, "l'appui court n'a pas agi : %r" % r
    r = _sc("appuiCourtFermeLaBulleDeLElement")
    assert r["ouverte"]["visible"], "l'appui long n'a pas ouvert"
    assert not r["apres"]["visible"] and r["actions"] == 1, (
        "l'appui court sur l'élément dont la bulle est ouverte : %r" % r)


def test_un_LIEN_garde_son_menu_et_n_a_aucun_geste():
    """LE MENU DU LIEN — copier, ouvrir dans un onglet — vaut plus que
    l'explication. Ni appui, ni appui long, et `contextmenu` passe."""
    r = _sc("lien")
    assert r["temoinClavier"], "le lien n'a pas de bulle au clavier : le contrôle ne mesurerait rien"
    assert not r["appui"]["visible"] and not r["long"]["visible"], r
    assert not r["menu"]["retenu"], "le menu du lien est annulé"
    assert not r["menu"]["vue"]["visible"]


def test_contextmenu_au_DOIGT_ouvre_annule_le_menu_et_vide_la_selection():
    """L'APPUI LONG ANDROID. Le `pointerType` lu est celui de `contextmenu`
    LUI-MÊME : la touche Menu et Maj+F10 en donnent un de souris."""
    r = _sc("contextmenu")
    assert r["touch"]["retenu"] and r["touch"]["vue"]["visible"], r["touch"]
    assert r["touch"]["selection"] >= 1, "la sélection n'est pas vidée"
    assert r["touch"]["ouverturesApresMinuteur"] == 1, (
        "le minuteur a rouvert la bulle déjà ouverte par contextmenu : %r" % r["touch"])
    assert r["touch"]["clic"], "le clic qui suit l'appui long n'est pas avalé"
    assert r["stylet"]["retenu"] and r["stylet"]["vue"]["visible"], r["stylet"]
    assert r["sansTypeApresDoigt"]["retenu"], "un ancien navigateur (sans pointerType) n'est pas pris en charge"
    assert not r["sansTypeApresSouris"]["retenu"] and not r["clavier"]["retenu"], r
    assert not r["clavier"]["vue"]["visible"]
    assert not r["inerte"]["retenu"], "le menu d'un élément INERTE est annulé : sa sélection ne se copie plus"


def test_contextmenu_teste_pointerType_touch():
    """LU DANS LE CODE : c'est le type de l'événement lui-même qui décide."""
    corps = _corps_ecouteur("contextmenu")
    assert len(corps) == 1, "écouteurs contextmenu : %d" % len(corps)
    assert 'ev.pointerType === "touch"' in corps[0], corps[0][:300]


def test_contextmenu_OUVRE_il_ne_bascule_pas():
    """ANDROID RECONNAÎT L'APPUI LONG DEUX FOIS — le minuteur, puis
    `contextmenu`. Une bascule refermerait au second ce que le premier vient
    d'ouvrir."""
    r = _sc("contextmenu")["apresMinuteur"]
    assert r["retenu"] and r["vue"]["visible"], "contextmenu après le minuteur a fermé la bulle : %r" % r
    assert r["ouvertures"] == 1, "une seule ouverture attendue : %r" % r


def test_pas_de_SELECTION_pendant_un_appui_long_sur_ce_qui_agit():
    """`selectstart` vise le NŒUD TEXTE : l'ancre se retrouve par son parent.
    Sur un élément inerte, la sélection reste permise."""
    r = _sc("selection")
    assert r["longTexte"], "la sélection démarre pendant l'appui long (cible : nœud texte)"
    assert not r["inerte"], "la sélection d'un élément inerte est empêchée"
    assert not r["sansGeste"], "la sélection est empêchée hors de tout geste"


# ══════════════════════════════════════════════════════════════════════════
#  5. L'ÉLIGIBILITÉ — calculée à l'événement
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("cas", ["champ", "caseTitree", "iframe", "option", "svgRect", "dansGraphe", "tt"])
def test_les_EXCLUS_n_ont_pas_de_bulle(cas):
    """LES CHAMPS (clavier virtuel, sélecteur natif), les IFRAMES, les
    GRAPHIQUES (leur propre bulle), le PANORAMA (`data-tt`).

    L'IFRAME EST UN FILET, PAS UN CHEMIN. Mesuré au navigateur (revue de
    conformité, constat 8) : un appui, un appui long ou une tabulation sur
    `#pan-sia-iframe` n'émettent AUCUN événement dans le document parent —
    ils vont au document de l'iframe. Cette règle éprouve l'exclusion du
    code, écrite au cas où un navigateur les y enverrait ; la recette
    (T-17) mesure, elle, que rien n'arrive."""
    r = _sc("exclusions")
    assert r["temoin"], "le témoin ne s'ouvre pas : le contrôle ne mesurerait rien"
    assert not r[cas], "%s ouvre une bulle" % cas


def test_la_PRESEANCE_le_declencheur_le_plus_proche_parle():
    """UNE BULLE data-tip DANS UN BLOC À `title` : l'appui sur elle est à
    elle. Un `title` DANS un bloc data-tip : à lui. Un `title=""` masque
    l'ancêtre — la pastille du rail."""
    r = _sc("preseance")
    assert not r["tipDansTitre"]["visible"], "la bulle data-tip et la bulle `title` s'ouvrent ensemble"
    assert r["titreAutour"]["visible"], "le bloc à `title` n'ouvre plus sa bulle hors de la data-tip"
    assert r["titreDansTip"]["visible"], "un `title` dans un bloc data-tip ne s'ouvre pas"
    assert not r["silence"]["visible"], "un `title` vide ne masque pas l'ancêtre"
    assert not r["puce"]["visible"], "la pastille du rail ouvre la bulle de la ligne du menu"
    assert r["iconeDeLaLigne"]["visible"], "l'icône de la ligne du menu n'ouvre pas sa bulle à l'appui long"


@pytest.mark.parametrize("cas", ["raccourci", "repete", "court", "nomme", "etiquete"])
def test_un_title_qui_n_APPREND_RIEN_n_a_pas_de_bulle(cas):
    """UN `title` ÉGAL AU NOM (texte, `aria-label`, `aria-labelledby`), au nom
    suivi d'un raccourci, ou de moins de deux caractères n'apprend rien."""
    r = _sc("nonInformatif")
    assert r["temoin"], "le témoin ne s'ouvre pas : le contrôle ne mesurerait rien"
    assert not r[cas], "%s ouvre une bulle" % cas


def test_un_div_au_curseur_POINTER_est_traite_comme_ce_qui_agit():
    """LES <div> À `addEventListener('click')` ne disent rien d'autre que
    leur curseur : l'appui court doit rester leur action."""
    r = _sc("nonInformatif")
    assert not r["curseurAppuiCourt"], "l'appui court sur une carte cliquable ouvre la bulle"
    assert r["curseurAppuiLong"], "l'appui long sur une carte cliquable n'ouvre pas"


# ══════════════════════════════════════════════════════════════════════════
#  6. AU CLAVIER — exécuté
# ══════════════════════════════════════════════════════════════════════════

def test_la_TABULATION_ouvre_500_ms_apres_et_le_depart_ferme():
    r = _sc("clavier")
    assert not r["a400"]["visible"], "la bulle s'ouvre avant 500 ms"
    assert r["a600"]["visible"] and r["a600"]["texte"].startswith("Panorama mondial"), r["a600"]
    assert not r["depart"]["visible"], "le départ du focus laisse la bulle ouverte"
    assert not r["partiAvant"]["visible"], "le focus parti avant 500 ms, la bulle s'ouvre quand même"
    assert r["versLeDedans"]["visible"], "le focus passé DANS l'élément a fermé sa bulle"


def test_CINQ_tabulations_rapides_une_seule_bulle_a_la_fin():
    """QUI TABULE DANS LE MENU traverse dix lignes sans vouloir dix bulles."""
    r = _sc("clavier")["cinq"]
    assert r["intermediaires"] == 0 and r["avant"] == 0, "des bulles intermédiaires : %r" % r
    assert r["apres500"] == 1 and r["texte"].startswith("Panorama mondial"), r


@pytest.mark.parametrize("cas", ["focusApresDoigt", "focusApresEntree", "focusTardif"])
def test_un_focus_QUI_N_A_PAS_ETE_TABULE_n_ouvre_rien(cas):
    """LE FOCUS D'UN APPUI, LE FOCUS PROGRAMMATIQUE (Entrée ouvre une
    fenêtre et y place le focus), LE FOCUS D'IL Y A PLUS D'UNE SECONDE : ni
    l'un ni l'autre n'est un déplacement demandé au clavier."""
    r = _sc("clavier")
    assert r["a600"]["visible"], "le témoin (tabulation) ne s'ouvre pas : le contrôle ne mesurerait rien"
    assert not r[cas]["visible"], "%s ouvre une bulle" % cas


def test_les_FLECHES_et_les_LIENS_comptent_au_clavier_les_CHAMPS_non():
    r = _sc("clavier")
    assert r["fleche"]["visible"], "une flèche qui déplace le focus n'ouvre pas"
    assert r["lien"]["visible"], "un lien n'ouvre pas sa bulle au clavier"
    assert not r["champ"]["visible"], "un champ ouvre une bulle au clavier"


def test_Echap_est_ecoute_sur_WINDOW_en_CAPTURE():
    """AVANT LA FENÊTRE MODALE, qui écoute sur `document`. Relevé sur ce que
    le script INSCRIT à l'exécution."""
    touches = [i for i in _executer()["inscrits"] if i["type"] == "keydown"]
    assert touches == [{"ou": "window", "type": "keydown", "capture": True, "passif": False}], touches
    corps = [c for c in _corps_ecouteur("keydown") if "Escape" in c]
    assert corps and "stopImmediatePropagation" in corps[0], "Échap ne retient pas la frappe"


def test_Echap_ferme_la_BULLE_puis_la_FENETRE_une_frappe_chacune():
    """LE DÉFAUT QU'/infobulles.js A PAYÉ : une frappe fermait la bulle ET la
    fenêtre. La fenêtre est jouée ici comme Sentinel l'écrit — un
    `keydown` sur `document`."""
    r = _sc("echap")
    assert r["ouverte"]["visible"], "la bulle n'était pas ouverte : le contrôle ne mesurerait rien"
    assert not r["premier"]["vue"]["visible"], "Échap ne ferme pas la bulle"
    assert r["premier"]["modale"] == 0 and r["premier"]["retenu"] and r["premier"]["immediat"], (
        "la première frappe a aussi fermé la fenêtre : %r" % r["premier"])
    assert r["second"]["modale"] == 1 and not r["second"]["retenu"], (
        "la seconde frappe n'atteint pas la fenêtre : %r" % r["second"])
    assert not r["auDoigt"]["vue"]["visible"] and r["auDoigt"]["modale"] == 0, r["auDoigt"]


def test_apres_Echap_la_bulle_ne_se_ROUVRE_pas_tant_que_le_focus_reste():
    r = _sc("echap")
    assert not r["repliee"]["visible"], "la bulle fermée par Échap s'est rouverte sur le même élément"
    assert r["apresDepart"]["visible"], "le repli survit au départ du focus"


# ══════════════════════════════════════════════════════════════════════════
#  7. LE PLACEMENT ET LES SORTIES — exécuté
# ══════════════════════════════════════════════════════════════════════════

def test_la_bulle_se_place_DESSOUS_centree_sans_jamais_recouvrir_l_element():
    r = _sc("placement")["dessous"]
    assert r["top"] == r["attendu"], "la bulle n'est pas sous l'élément : %r" % r
    assert not r["croise"], "la bulle recouvre l'élément (2.4.11)"
    assert abs(r["centre"] - r["centreAncre"]) <= 1, "la bulle n'est pas centrée : %r" % r


def test_la_bulle_passe_DESSUS_quand_la_place_manque_dessous():
    r = _sc("placement")["dessus"]
    assert r["bas"] == r["attendu"] and not r["croise"] and r["dansVV"], r


def test_la_bulle_reste_dans_la_FENETRE_VISUELLE():
    """MESURÉ AU PIXEL 7 : `innerWidth` 491 pour une fenêtre visuelle de
    412. Bornée à `innerWidth`, la bulle sortirait de l'écran."""
    r = _sc("placement")
    assert r["droite"]["droite"] <= r["droite"]["borne"] and not r["droite"]["croise"], r["droite"]
    f = r["fenetreVisuelle"]
    assert f["droite"] <= f["borne"] and f["gauche"] >= f["borneGauche"], (
        "la bulle sort de la fenêtre visuelle : %r" % f)


def test_dans_le_MENU_la_bulle_passe_A_DROITE_quand_il_y_a_la_place():
    """AU POSTE, à droite du menu, à la hauteur de la ligne : dessous, elle
    recouvrirait les lignes qu'on tabule. Sur un écran étroit, dessous."""
    r = _sc("placement")
    p = r["menuPoste"]
    assert p["gauche"] == p["attendu"] and p["top"] == p["topAncre"] and not p["croise"], p
    assert r["menuEtroit"]["gauche"] < 240 and not r["menuEtroit"]["croise"], r["menuEtroit"]


def test_le_TEXTE_est_relu_et_une_bulle_sans_objet_se_ferme():
    """UN `title` RÉÉCRIT pendant la lecture (le bouton d'enregistrement
    FRIA) ; un `title` vidé ; un écran masqué par `go()` ; un élément
    démonté ; un élément sorti de l'écran — en 250 ms au plus."""
    r = _sc("sorties")
    assert r["ouverte"]["visible"]
    assert r["titreChange"]["texte"] == "Enregistrer cette évaluation FRIA dans l'historique.", r["titreChange"]
    assert not r["titreVide"]["visible"], "un `title` vidé laisse la bulle ouverte"
    assert r["ecranOuvert"]["visible"] and not r["ecranMasque"]["visible"], "un écran masqué garde sa bulle"
    assert r["demonteOuvert"]["visible"] and not r["demonte"]["visible"], "un élément démonté garde sa bulle"
    assert not r["horsEcran"]["visible"], "un élément sorti de l'écran garde sa bulle"


def test_l_intervalle_ne_tourne_QUE_bulle_ouverte():
    r = _sc("sorties")
    assert r["minuteursAuRepos"] == 0 and r["intervalleOuvert"] == 1 and r["intervalleFerme"] == 0, r


# ══════════════════════════════════════════════════════════════════════════
#  8. LE BOUTON D'AIDE — servi par le même script
# ══════════════════════════════════════════════════════════════════════════

def test_le_bouton_d_AIDE_bascule_a_la_souris_comme_au_doigt():
    """PAS DE `title` SUR LE BOUTON, DONC PAS DE DOUBLE BULLE : il s'ouvre à la
    souris aussi. Le texte vient de l'élément `aria-describedby`, et
    `aria-expanded` suit."""
    r = _sc("aide")
    assert r["clic1"]["vue"]["visible"] and r["clic1"]["expanded"] == "true", r["clic1"]
    assert r["clic1"]["vue"]["texte"] == "Calcul : (points conformes + points en cours × 0,5).", r["clic1"]
    assert not r["clic2"]["vue"]["visible"] and r["clic2"]["expanded"] == "false", r["clic2"]
    assert r["doigt"]["vue"]["visible"] and r["doigt"]["expanded"] == "true", r["doigt"]


@pytest.mark.parametrize("sortie", ["echap", "depart", "ailleurs"])
def test_le_bouton_d_aide_se_REFERME_et_le_dit(sortie):
    r = _sc("aide")[sortie]
    assert r["avant"], "la bulle d'aide n'était pas ouverte : le contrôle ne mesurerait rien"
    assert not r["vue"]["visible"] and r["expanded"] == "false", r


def test_un_APPUI_sur_le_bouton_d_aide_OUVERT_le_referme():
    """LE RELÂCHER NE FERME PAS LA BULLE DU BOUTON D'AIDE : c'est son clic,
    qui suit, qui bascule. Si le relâcher la fermait comme « un appui
    ailleurs » (le bouton n'a pas de `title`, donc pas d'ancre), le clic la
    rouvrirait : au doigt, elle ne se refermerait plus."""
    r = _sc("aide")["doigtFerme"]
    assert r["avant"], "la bulle d'aide n'était pas ouverte : le contrôle ne mesurerait rien"
    assert not r["vue"]["visible"] and r["expanded"] == "false", r


# ══════════════════════════════════════════════════════════════════════════
#  8 bis. LES CORRECTIFS DE LA REVUE — chacun mesuré avant au navigateur
#  (…/p9/correctifs/banc_avant.json) et rejoué ici sur le vrai script
# ══════════════════════════════════════════════════════════════════════════

def test_ENTREE_sur_l_element_ferme_sa_bulle_et_ne_la_rouvre_pas():
    """LE DÉFAUT MESURÉ (revues navigateur et robustesse, Sentinel au poste) :
    Tab jusqu'au bouton « Guide d'utilisation », sa bulle s'ouvre ; Entrée
    ouvre la fenêtre du guide sans y déplacer le focus, et la bulle (10060)
    restait par-dessus la fenêtre (10020) — le premier Échap n'était que pour
    elle. Même chose avec Espace sur une ligne du menu, qui navigue."""
    r = _sc("entree")
    assert r["ouverte"]["visible"] and r["ouverteMenu"]["visible"], (
        "la bulle n'était pas ouverte au clavier : le contrôle ne mesurerait rien")
    assert not r["entree"]["vue"]["visible"], "Entrée sur l'élément laisse sa bulle ouverte"
    assert not r["entree"]["retenu"], "Entrée est retenue : l'élément n'agirait plus"
    assert not r["pasRouverte"]["visible"], "la bulle fermée par Entrée se rouvre, le focus resté sur l'élément"
    assert not r["espace"]["visible"], "Espace sur une ligne du menu laisse sa bulle ouverte"


def test_ESPACE_qui_fait_defiler_ne_ferme_pas_la_bulle_d_un_AUTRE_element():
    """ENTRÉE ET ESPACE NE FERMENT QUE LA BULLE DE L'ÉLÉMENT QUI A LE FOCUS.
    Une pastille ouverte au doigt, le focus ailleurs : Espace fait défiler
    la page, et le défilement ne ferme pas."""
    r = _sc("entree")
    assert r["ouverteDoigt"]["visible"], "la pastille ne s'est pas ouverte : le contrôle ne mesurerait rien"
    assert r["espaceAilleurs"]["visible"], "Espace, le focus ailleurs, a fermé la bulle"


def test_ENTREE_sur_le_bouton_d_aide_reste_une_BASCULE():
    """POUR LE BOUTON D'AIDE, ENTRÉE EST LA BASCULE (son clic natif). La
    fermer à la touche, c'est la rouvrir au clic : elle ne se fermerait
    plus au clavier."""
    r = _sc("entree")["aide"]
    assert [x["vue"] for x in r] == [True, False, True], r
    assert [x["expanded"] for x in r] == ["true", "false", "true"], r


def test_OUVRIR_ici_ferme_la_bulle_d_infobulles():
    """LE DÉFAUT MESURÉ (banc, tablette) : une bulle data-tip ouverte, puis une
    ligne du menu tenue 500 ms — les deux bulles, l'une à côté de l'autre,
    jusqu'au relâcher. Ouvrir ici ferme l'autre, à l'appui, au minuteur de
    l'appui long et à la tabulation ; un balayage, qui n'ouvre rien, ne ferme
    rien non plus."""
    r = _sc("croise")
    assert r["balayage"] == 0, "un balayage, qui n'ouvre rien, a fermé la bulle data-tip"
    for k in ("appui", "long", "tab"):
        assert r[k]["vue"]["visible"], "%s n'a rien ouvert : le contrôle ne mesurerait rien" % k
        assert r[k]["fermees"] >= 1, "%s ouvre sans fermer la bulle d'/infobulles.js" % k


def test_un_appui_sur_une_partie_TUE_de_l_element_est_un_appui_AILLEURS():
    """LE DÉFAUT MESURÉ (Sentinel, tablette) : la ligne du menu tenue, puis un
    appui sur SA pastille du rail (`title=""`, sa propre bulle data-tooltip)
    — la pastille étant DANS la ligne, la bulle de la ligne restait ouverte
    à côté de celle de la pastille. Idem pour un déclencheur data-tip dans
    un bloc à `title`."""
    r = _sc("croise")
    assert r["puceAvant"] and r["tipAvant"], "la bulle n'était pas ouverte : le contrôle ne mesurerait rien"
    assert not r["puce"]["visible"], "l'appui sur la pastille laisse la bulle de sa ligne ouverte"
    assert not r["tip"]["visible"], "l'appui sur le déclencheur data-tip laisse la bulle du bloc ouverte"


@pytest.mark.parametrize("cas,attendu", [("inerte", True), ("long", True), ("boutonCourt", False),
                                         ("inerteTenu", False), ("autreDoigt", False),
                                         ("sansGeste", False), ("autreAncre", False)])
def test_prend_dit_si_le_relacher_est_A_NOUS(cas, attendu):
    """LA PRÉSÉANCE, LUE PAR /infobulles.js. LE DÉFAUT MESURÉ (banc) : un
    `title` DANS un déclencheur data-tip ouvrait les deux bulles, et un
    bouton à `title` TENU dans ce déclencheur voyait la bulle data-tip
    s'ouvrir au relâcher, à côté de la sienne. /infobulles.js, dont
    l'écouteur passe avant, demande donc `prend(ev)`. OUI pour la bascule
    d'un élément inerte et pour l'appui long servi ; NON pour l'appui court
    sur ce qui agit (la lecture d'abord d'/infobulles.js reste la sienne),
    pour l'élément inerte tenu (la sélection native), pour un autre doigt,
    sans geste, ou relâché sur une autre ancre.

    ÉCART À LA SPÉCIFICATION (§0.5, §2.1, R7 : « pas de bus, API
    { fermer, ouvrirPour } ») : l'« appui ailleurs » seul laissait deux
    bulles ouvertes — mesuré. Une question posée à l'usage n'est pas un
    bus : ni événement, ni état partagé."""
    r = _sc("prend")
    assert r[cas] is attendu, "prend() pour « %s » : %r au lieu de %r" % (cas, r[cas], attendu)


@pytest.mark.parametrize("cas", ["appuiDansBloc", "zoneDansBloc", "tabDansBloc", "menuDansLabel",
                                 "longDansLabel"])
def test_un_CHAMP_n_emprunte_pas_la_bulle_de_son_CONTENEUR(cas):
    """LE DÉFAUT MESURÉ (banc) : l'exclusion des champs ne portait que sur
    l'élément QUI PORTE le `title`. Un <input> dans un `div[title]` ouvrait
    la bulle du bloc, à l'appui comme à la tabulation — sous le clavier
    virtuel ; un appui long Android dans un <input> sous un `label[title]`
    annulait `contextmenu` : le menu Coller disparaissait. Les témoins : le
    bloc et le libellé eux-mêmes gardent leur bulle, et la case à cocher
    celle de son libellé."""
    r = _sc("saisie")
    assert r["temoinBloc"] and r["temoinLabel"] and r["temoinCase"], (
        "un témoin ne s'ouvre pas : le contrôle ne mesurerait rien — %r" % r)
    assert not r[cas], "%s : le champ emprunte la bulle de son conteneur" % cas


def test_la_CASE_a_cocher_garde_la_bulle_de_son_LIBELLE():
    """LE CHAMP DE SAISIE N'EMPRUNTE RIEN, LA CASE À COCHER SI : ni clavier
    virtuel ni menu Coller, et c'est son libellé qui l'explique. Tab jusqu'à
    la case d'un `label[title]` : la bulle du libellé s'ouvre."""
    assert _sc("saisie")["temoinCase"], "la case à cocher a perdu la bulle de son libellé"


def test_a_droite_du_menu_la_bulle_ne_deborde_PAS_sur_la_ligne():
    """LE DÉFAUT MESURÉ (banc à 520 px, et harnais de la revue) : le seuil de
    208 px disait « il y a la place », la bulle pouvait en faire 320 ; le
    bornage la ramenait par-dessus la ligne qui a le focus (2.4.11). Elle
    reste à droite du menu, plus étroite."""
    r = _sc("largeur")["menuSerre"]
    assert r["vue"], "la bulle ne s'ouvre pas : le contrôle ne mesurerait rien"
    assert r["gauche"] == r["sbDroite"] + 8, "la bulle n'est plus à droite du menu : %r" % r
    assert not r["croiseLigne"] and not r["croiseMenu"], "la bulle recouvre le menu : %r" % r
    assert r["droite"] <= r["borne"], "la bulle sort de la fenêtre : %r" % r


def test_une_bulle_plus_LARGE_que_la_fenetre_est_BORNEE():
    """UNE BULLE QUI VOUDRAIT 600 PX DANS UNE FENÊTRE DE 400 : `max-width`
    la ramène à la fenêtre visuelle moins 16 px — sans quoi le bornage la
    colle au bord gauche et elle sort à droite. Le harnais plafonnait sa
    largeur à 200 px : cette borne n'était mesurée par rien (sonde S2)."""
    r = _sc("largeur")["large"]
    assert r["vue"], "la bulle ne s'ouvre pas : le contrôle ne mesurerait rien"
    assert r["gauche"] >= r["borneGauche"] and r["droite"] <= r["borneDroite"], r


@pytest.mark.parametrize("evenement", ["resize", "scroll"])
def test_la_bulle_SUIT_la_fenetre_visuelle_avant_l_intervalle(evenement):
    """LA FENÊTRE VISUELLE BOUGE SANS QUE LA PAGE DÉFILE — un zoom à deux
    doigts, le clavier virtuel qui monte. La bulle se replace dans les 20 ms,
    bien avant l'intervalle de 250 ms. Aucune règle ne mesurait ces deux
    écouteurs : les retirer ne faisait rien tomber (sonde S1)."""
    r = _sc("fenetreVisuelle")
    assert r["ouverte"]["vue"]["visible"], "la bulle n'était pas ouverte : le contrôle ne mesurerait rien"
    c = r[evenement]
    assert c["vue"]["visible"] and c["top"] == c["attendu"], (
        "après « %s » de la fenêtre visuelle, top %r au lieu de %r" % (evenement, c["top"], c["attendu"]))


# ══════════════════════════════════════════════════════════════════════════
#  9. LA PASTILLE DU RAIL SE TAIT SOUS LA LIGNE DU MENU (§3.6)
# ══════════════════════════════════════════════════════════════════════════

def test_la_pastille_du_rail_porte_un_title_VIDE():
    """SANS LUI, DEUX BULLES AU SURVOL DE LA PASTILLE : la sienne (data-tooltip)
    et celle, native, héritée de la ligne du menu."""
    m = re.search(r"function railPeindreBarre\(.*?\n\}", PAGE_JS, re.S)
    assert m, "railPeindreBarre est introuvable"
    assert re.search(r"puce\.setAttribute\('title', ''\);", m.group(0)), (
        "la pastille du rail ne pose pas de `title` vide")


# ══════════════════════════════════════════════════════════════════════════
#  10. LA RECETTE NE SE PÉRIME PAS EN SILENCE
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("ancre", ["sb-item", "audit-item-prio", "audit-kpi", "rail-puce",
                                   "procOpenDoc", "proc-modal-body", "mat-modal-close",
                                   "legal-ref-link", "pan-sia-iframe", "page-guide-btn",
                                   "audit-export-btn", "mat-sector-btn", "pricingSetEstim",
                                   "pnav", "z-niv"])
def test_la_recette_vise_des_ancres_QUI_EXISTENT(ancre):
    recette = _lire("recette_bulle_titre.js")
    assert ancre in recette, "la recette ne vise plus %r" % ancre
    assert ancre in SENTINEL + PAGE_JS + _lire("panorama.html"), (
        "%r a disparu du code : la recette mesure un identifiant mort" % ancre)
