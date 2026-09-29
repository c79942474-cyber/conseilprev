/* ═══════════════════════════════════════════════════════════════════════════
   UN DOM MINIMAL POUR LA TRADUCTION PAR CONTENU — ET POURQUOI IL EST MINIMAL

   CE QU'IL FAIT : il analyse un fragment HTML en un arbre d'éléments et de
   nœuds texte — avec ce que sentinel.i18n.js touche, et rien de plus :
   nodeType, tagName, attributes, childNodes, parentNode, textContent,
   innerHTML (lu ET écrit), nodeValue — puis charge le VRAI module et joue
   une suite d'opérations reçue en JSON. Chaque opération rend son résultat ;
   la sortie est un JSON que les règles Python lisent.

   POURQUOI PAS DE jsdom : il n'est pas installé, et l'installer pour six
   propriétés ferait dépendre la recette d'un paquet de plus. La recette
   navigateur (recette_sentinel_langue_moteur.js) mesure ce que ce harnais
   ne peut pas : la vraie sérialisation, le vrai observateur, le vrai fetch.

   LA SÉRIALISATION EST STABLE : ce que `innerHTML` rend après une écriture
   est ce qu'il rendrait de la même chaîne relue — c'est ce qui donne un sens
   à « octet pour octet » dans les règles de restitution.
   ═══════════════════════════════════════════════════════════════════════ */
'use strict';
const fs = require('fs');
const [, , MODULE, PROGRAMME] = process.argv;
const M = require(MODULE);
const prog = JSON.parse(fs.readFileSync(PROGRAMME, 'utf8'));

const VIDES = { br: 1, wbr: 1, input: 1, img: 1, hr: 1, meta: 1, link: 1 };
const BRUTS = { script: 1, style: 1, textarea: 1 };

function decoder(s) {
  return s.replace(/&(#x[0-9a-f]+|#[0-9]+|[a-z]+);/gi, (m, e) => {
    if (e[0] === '#') return String.fromCharCode(parseInt(e[1] === 'x' || e[1] === 'X' ? e.slice(2) : e.slice(1), e[1] === 'x' || e[1] === 'X' ? 16 : 10));
    return { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: String.fromCharCode(160) }[e.toLowerCase()] || m;
  });
}
function encoderTexte(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/ /g, '&nbsp;'); }
function encoderAttr(s) { return s.replace(/&/g, '&amp;').replace(/"/g, '&quot;'); }

function Texte(v) { this.nodeType = 3; this.nodeValue = v; this.parentNode = null; }
Object.defineProperty(Texte.prototype, 'textContent', { get() { return this.nodeValue; } });

function El(tag) {
  this.nodeType = 1; this.tagName = tag.toUpperCase(); this.nodeName = this.tagName;
  this.parentNode = null; this.childNodes = []; this._attrs = [];
  const moi = this;
  this.attributes = { get length() { return moi._attrs.length; } };
}
El.prototype.getAttribute = function (n) { const a = this._attrs.find(x => x[0] === n); return a ? a[1] : null; };
El.prototype.hasAttribute = function (n) { return this._attrs.some(x => x[0] === n); };
El.prototype.setAttribute = function (n, v) { const a = this._attrs.find(x => x[0] === n); if (a) a[1] = String(v); else this._attrs.push([n, String(v)]); };
El.prototype.removeAttribute = function (n) { this._attrs = this._attrs.filter(x => x[0] !== n); };
El.prototype.appendChild = function (e) { if (e.parentNode) e.parentNode.removeChild(e); e.parentNode = this; this.childNodes.push(e); return e; };
El.prototype.removeChild = function (e) { this.childNodes = this.childNodes.filter(x => x !== e); e.parentNode = null; return e; };
El.prototype.contains = function (e) { for (let n = e; n; n = n.parentNode) if (n === this) return true; return false; };
Object.defineProperty(El.prototype, 'children', { get() { return this.childNodes.filter(n => n.nodeType === 1); } });
Object.defineProperty(El.prototype, 'textContent', {
  get() { return this.childNodes.map(n => n.textContent).join(''); },
  set(v) { this.childNodes.forEach(n => { n.parentNode = null; }); this.childNodes = v === '' ? [] : [Object.assign(new Texte(String(v)), { parentNode: this })]; }
});
Object.defineProperty(El.prototype, 'innerHTML', {
  get() { return this.childNodes.map(serialiser).join(''); },
  set(v) { this.childNodes.forEach(n => { n.parentNode = null; }); this.childNodes = []; analyser(String(v), this); }
});
function serialiser(n) {
  if (n.nodeType === 3) return encoderTexte(n.nodeValue);
  const tag = n.tagName.toLowerCase();
  const attrs = n._attrs.map(([k, v]) => ' ' + k + '="' + encoderAttr(v) + '"').join('');
  if (VIDES[tag]) return '<' + tag + attrs + '>';
  return '<' + tag + attrs + '>' + n.innerHTML + '</' + tag + '>';
}
El.prototype.querySelectorAll = function (sel) {
  const out = [];
  const m = sel.match(/^#([\w-]+)$|^([a-z0-9]+)$|^\.([\w-]+)$/i);
  if (!m) throw new Error('sélecteur non géré : ' + sel);
  (function marcher(e) {
    for (const c of e.childNodes) {
      if (c.nodeType !== 1) continue;
      if ((m[1] && c.getAttribute('id') === m[1]) || (m[2] && c.tagName === m[2].toUpperCase())
          || (m[3] && (' ' + (c.getAttribute('class') || '') + ' ').indexOf(' ' + m[3] + ' ') >= 0)) out.push(c);
      marcher(c);
    }
  })(this);
  return out;
};
El.prototype.querySelector = function (sel) { return this.querySelectorAll(sel)[0] || null; };

/* L'ANALYSEUR : balises, attributs, texte, commentaires, contenu brut des
   scripts et styles. Assez pour les fragments des règles ; une construction
   qu'il ne sait pas lire lève, plutôt que de rendre un arbre faux. */
function analyser(html, racine) {
  let i = 0, courant = racine;
  while (i < html.length) {
    if (html.startsWith('<!--', i)) { const f = html.indexOf('-->', i); i = f < 0 ? html.length : f + 3; continue; }
    if (html[i] === '<') {
      const m = /^<\/?([a-zA-Z][a-zA-Z0-9-]*)((?:\s+[^\s=>\/]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+))?)*)\s*\/?>/.exec(html.slice(i));
      if (!m) throw new Error('balise illisible à ' + i + ' : ' + html.slice(i, i + 30));
      i += m[0].length;
      const tag = m[1].toLowerCase();
      if (m[0][1] === '/') {
        let e = courant; while (e && e !== racine && e.tagName.toLowerCase() !== tag) e = e.parentNode;
        if (e && e !== racine) courant = e.parentNode;
        continue;
      }
      const el = new El(tag);
      const ra = /([^\s=]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g; let a;
      while ((a = ra.exec(m[2])) !== null) el.setAttribute(a[1], decoder(a[2] !== undefined ? a[2] : a[3] !== undefined ? a[3] : a[4] !== undefined ? a[4] : ''));
      courant.appendChild(el);
      if (VIDES[tag] || m[0].endsWith('/>')) continue;
      if (BRUTS[tag]) {
        const f = html.toLowerCase().indexOf('</' + tag, i);
        el.appendChild(new Texte(html.slice(i, f < 0 ? html.length : f)));
        i = f < 0 ? html.length : html.indexOf('>', f) + 1;
        continue;
      }
      courant = el;
      continue;
    }
    let f = html.indexOf('<', i); if (f < 0) f = html.length;
    courant.appendChild(new Texte(decoder(html.slice(i, f))));
    i = f;
  }
}

const body = new El('body');
analyser(prog.html || '', body);
const document = { nodeType: 9, body, documentElement: body };

const trouver = (sel) => { if (sel === 'body') return body; const e = body.querySelector(sel); if (!e) throw new Error('introuvable : ' + sel); return e; };
const noeud = (op) => {
  const e = trouver(op.sel);
  return op.enfant === undefined ? e : e.childNodes[op.enfant];
};

const sorties = [];
for (const op of prog.ops) {
  let r;
  try {
    switch (op.op) {
      case 'classer': r = M.sentClasser(trouver(op.sel)); break;
      case 'inventaire': r = M.sentInventaire(op.sel ? trouver(op.sel) : document); break;
      case 'traduire': r = M.sentTraduireCorps(op.sel ? noeud(op) : document, op.dico === undefined ? prog.dico : op.dico, op.langue); break;
      case 'html': r = op.sel ? trouver(op.sel).innerHTML : body.innerHTML; break;
      case 'texte': r = noeud(op).textContent; break;
      case 'attr': r = trouver(op.sel).getAttribute(op.nom); break;
      case 'setTexte': noeud(op).nodeType === 3 ? (noeud(op).nodeValue = op.valeur) : (noeud(op).textContent = op.valeur); r = true; break;
      case 'setHtml': trouver(op.sel).innerHTML = op.valeur; r = true; break;
      case 'append': { const e = trouver(op.sel); analyser(op.html, e); r = e.childNodes.length; break; }
      case 'memorise': r = M.SENT_ORIG.get(noeud(op)) !== undefined; break;
      case 'normaliser': r = M.sentNormaliser(op.valeur); break;
      case 'digits': r = M.sentDigits(op.en, op.fr); break;
      /* LES MOTIFS COMPILÉS : l'ordre d'essai, et la même liste rendue pour
         le même dictionnaire — compilés une fois, pas à chaque nœud. */
      case 'motifs': {
        /* `paires` garde l'ordre d'insertion voulu, que le JSON trié du
           programme perdrait : c'est lui qui départage un tri sans règle. */
        const src = op.paires ? Object.fromEntries(op.paires) : op.motif;
        const a = M.sentMotifsCompiler(src), b = M.sentMotifsCompiler(src);
        r = { meme: a === b, cles: a.map(m => m.cle) };
        break;
      }
      default: throw new Error('opération inconnue : ' + op.op);
    }
  } catch (e) { r = { erreur: String(e && e.stack || e) }; }
  sorties.push(r);
}
process.stdout.write(JSON.stringify(sorties));
