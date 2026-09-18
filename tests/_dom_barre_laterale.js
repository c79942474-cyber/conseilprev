/* ═══════════════════════════════════════════════════════════════════════════
   UN DOM MINIMAL POUR LA BARRE LATÉRALE — ET POURQUOI IL EST MINIMAL

   CE QU'IL FAIT : il parse la VRAIE barre latérale de sentinel.html en une
   liste plate d'éléments — c'est exactement la forme que le code attend, et
   c'est cette forme-là que les règles doivent éprouver. Puis il évalue le
   VRAI bloc de sentinel.page.js.

   POURQUOI PAS DE jsdom : il n'est pas installé, et l'installer pour quatre
   sélecteurs ferait dépendre la recette d'un paquet de plus. Les sélecteurs
   employés par le bloc sont peu nombreux et connus ; celui qui en écrirait un
   autre verra ce harnais lever « sélecteur non géré », ce qui vaut mieux
   qu'un faux vert silencieux.

   CE QU'IL NE PEUT PAS FAIRE : dire ce que le navigateur AFFICHE. `hidden` et
   `data-replie` sont des attributs ; c'est la feuille de style qui les rend
   invisibles, et une règle séparée vérifie qu'elle le fait.
   ═══════════════════════════════════════════════════════════════════════ */
const fs = require('fs');
const html = fs.readFileSync(process.argv[2], 'utf8');
const src  = fs.readFileSync(process.argv[3], 'utf8');

const deb = html.indexOf('<nav class="sb-nav"') >= 0
  ? html.indexOf('<nav class="sb-nav"') : html.indexOf('class="sb-nav"');
if (deb < 0) throw new Error('.sb-nav introuvable');
const fin = html.indexOf('</nav>', deb);
const zone = html.slice(deb, fin < 0 ? html.length : fin);

function El(tag, attrs, texte){
  this.tag = tag; this.attrs = attrs || {}; this._texte = texte || '';
  this.enfants = [];
  const self = this;
  this.classList = {
    contains: function(c){ return (self.attrs['class']||'').split(/\s+/).indexOf(c) >= 0; },
    add: function(c){ if(!this.contains(c)) self.attrs['class'] = ((self.attrs['class']||'') + ' ' + c).trim(); },
    remove: function(c){ self.attrs['class'] = (self.attrs['class']||'').split(/\s+/).filter(x => x && x !== c).join(' '); },
    toggle: function(c, v){ if(v === undefined) v = !this.contains(c); v ? this.add(c) : this.remove(c); },
  };
}
El.prototype.getAttribute = function(n){ return n in this.attrs ? this.attrs[n] : null; };
El.prototype.setAttribute = function(n, v){ this.attrs[n] = String(v); };
El.prototype.removeAttribute = function(n){ delete this.attrs[n]; };
El.prototype.hasAttribute = function(n){ return n in this.attrs; };
Object.defineProperty(El.prototype, 'textContent', {
  get: function(){ return this._texte + this.enfants.map(e => e.textContent).join(''); },
  set: function(v){ this._texte = String(v); this.enfants = []; } });
Object.defineProperty(El.prototype, 'hidden', {
  get: function(){ return this.hasAttribute('hidden'); },
  set: function(v){ v ? this.setAttribute('hidden','') : this.removeAttribute('hidden'); } });
El.prototype.querySelector = function(sel){ return this.querySelectorAll(sel)[0] || null; };
El.prototype.querySelectorAll = function(sel){
  sel = sel.trim().replace(/^\.sb-nav\s+/, '');
  const m = sel.match(/^\.([\w-]+)(?:\.([\w-]+))?(?:\[([\w-]+)(?:="([^"]*)")?\])?$/);
  if(!m) throw new Error('sélecteur non géré : ' + sel);
  return this.enfants.filter(function(e){
    if(!e.classList.contains(m[1])) return false;
    if(m[2] && !e.classList.contains(m[2])) return false;
    if(m[3]){
      if(!e.hasAttribute(m[3])) return false;
      if(m[4] !== undefined && e.getAttribute(m[3]) !== m[4]) return false;
    }
    return true;
  });
};

const nav = new El('nav', {'class':'sb-nav'});
/* Une div de premier niveau par onglet ou par titre : on ne descend pas dans
   les <svg>, ils n'ont pas de classe qui nous intéresse. */
const re = /<div ([^>]*class="(?:sb-section|sb-item|sb-famille)[^"]*"[^>]*)>([\s\S]*?)<\/div>\s*(?=<div|<!--|$)/g;
let mm;
while((mm = re.exec(zone))){
  const brut = mm[1]; const attrs = {};
  let am; const rea = /([\w-]+)="([^"]*)"/g;
  while((am = rea.exec(brut))) attrs[am[1]] = am[2];
  const texte = mm[2].replace(/<svg[\s\S]*?<\/svg>/g, '').replace(/<[^>]+>/g, '');
  const el = new El('div', attrs, texte);
  el.parent = nav; nav.enfants.push(el);
}
nav.enfants.forEach(function(e, i){
  e.nextElementSibling = nav.enfants[i+1] || null;
  e.previousElementSibling = nav.enfants[i-1] || null;
  /* .sb-famille-n vit DANS le titre de famille */
  if(e.classList.contains('sb-famille')){
    const cpt = new El('span', {'class':'sb-famille-n'});
    e.enfants.push(cpt);
  }
});
/* querySelector sur un titre de famille doit trouver son compteur */
El.prototype._qsaLocal = El.prototype.querySelectorAll;

const boites = {'sb-filtre-cpt': new El('span',{}), 'sb-filtre-effacer': new El('button',{})};
global.document = {
  querySelector: function(s){
    if(s.indexOf('.sb-nav') === 0 && s.trim() === '.sb-nav') return nav;
    return nav.querySelector(s);
  },
  querySelectorAll: function(s){ return nav.querySelectorAll(s); },
  getElementById: function(id){ return boites[id] || null; },
};
const magasin = {};
global.localStorage = {
  getItem: k => (k in magasin ? magasin[k] : null),
  setItem: (k, v) => { magasin[k] = String(v); },
};
global.window = global;

/* On n'évalue QUE le bloc de la barre latérale — le reste du moteur touche
   au DOM complet. */
const d1 = src.indexOf('window.sbFiltrer = function(q){');
const f1 = src.indexOf('try { window.sbRestaurerPlis(); window.sbCompterFamilles(); } catch(e){}');
if(d1 < 0 || f1 < 0) throw new Error('le bloc de la barre latérale est introuvable');
eval(src.slice(d1, f1));
global.__nav = nav; global.__magasin = magasin; global.__boites = boites;
