/* RECETTE — LES BULLES D'AIDE DE SENTINEL S'OUVRENT AU DOIGT, PAS SEULEMENT À LA SOURIS
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LE DÉFAUT SIGNALÉ : « ailleurs dans Sentinel, les bulles d'aide ne
 * s'ouvrent qu'à la souris, pas au toucher ». Le mécanisme partagé
 * (/infobulles.js) ne connaissait que les bulles écrites dans un ATTRIBUT
 * (`data-tooltip`, `data-tip`). Sentinel en porte quatre autres familles,
 * dont le texte est un ÉLÉMENT ENFANT révélé par `:hover` :
 *
 *   · maturité      `.mat-tooltip-wrap`  → `.mat-tooltip`      (42)
 *   · modèles       `.tmpl-art-badge`    → `.tmpl-tip`         (118)
 *   · tarification  `.prx-tip-icon`      → `.prx-tip-bubble`   (21)
 *   · budget        `.bud-tip`           → `.bud-tip-bubble`   (6)
 *
 * CE QUE LA MESURE « AVANT » A TROUVÉ — et ce n'était pas le défaut attendu.
 * Au doigt, trois familles sur quatre s'OUVRAIENT déjà, par accident :
 * Chromium laisse le survol « collé » à l'élément touché (maturité), et donne
 * le focus à un élément `tabindex` (tarification, budget), que leur feuille
 * ouvre aussi sur `:focus`. Deux accidents qui ne tiennent pas partout — un
 * navigateur qui ne colle pas le survol n'ouvre rien — et qui ont leur
 * revers, mesuré : une bulle ouverte ainsi ne se REFERME ni au second appui
 * ni à Échap, puisque le survol ou le focus restent là. Aucune n'était
 * annoncée au lecteur d'écran. Maturité et modèles n'étaient pas
 * atteignables au clavier.
 *
 * ET LA QUATRIÈME NE S'OUVRAIT JAMAIS. Chaque badge d'article est posé DANS
 * une carte cliquable : l'appui ouvrait la fiche du document, qui recouvre la
 * page — la bulle de l'article n'était lisible qu'à la souris. Même chose,
 * mesurée, pour le « ? » d'une formule (l'appui CHOISIT la formule) et pour
 * celui d'un libellé de champ (l'appui donne le focus au champ, ce qui ôte le
 * `:focus` qui ouvrait la bulle).
 *
 * LES CONTRÔLES QUI DÉCIDENT sont donc de quatre sortes : l'appui ouvre PAR
 * LE MÉCANISME (et non par un accident de navigateur), il se REFERME comme
 * partout ailleurs, il n'ACTIONNE PAS le conteneur au premier appui, et la
 * bulle ouverte par la classe est EXACTEMENT celle du survol — sinon le doigt
 * ouvrirait une autre bulle que la souris.
 */
const { chromium, devices } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5901';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
/* LE LIMITEUR : un chargement de Sentinel coûte près d'une centaine de
   requêtes, pour une limite de 120 par minute. Deux chargements d'affilée
   se feraient refuser le second — et la recette mesurerait des 429. */
const ATTENTE = Number(process.env.ATTENTE || 62000);
let ko = 0, n = 0;
const ok = (t, c, d) => { n++; if (!c) ko++;
  console.log((c ? '  OK   ' : '  KO   ') + t + (d ? ' — ' + d : '')); };
const pause = (ms) => new Promise(r => setTimeout(r, ms));

/* LES QUATRE FAMILLES, et l'élément que chacune révèle. La recette les
   nomme : elle mesure des écrans précis. Le script, lui, ne les nomme pas
   — il les reconnaît à ce qu'elles font (voir /infobulles.js). */
const FAMILLES = [
  { nom: 'maturité', page: 'maturite', decl: '.mat-tooltip-wrap', bulle: '.mat-tooltip', appui: '.mat-tooltip-icon' },
  { nom: 'modèles', page: 'templates', decl: '.tmpl-art-badge', bulle: '.tmpl-tip', carte: true },
  { nom: 'tarification', page: 'pricing', decl: '.prx-tip-icon', bulle: '.prx-tip-bubble' },
  { nom: 'budget', page: 'pricing', decl: '.bud-tip', bulle: '.bud-tip-bubble' },
];
const CLIQUABLE = 'a[href],button,label[for],[onclick],[role=button],summary';

const FURTIF = (ctx) => ctx.addInitScript(() => {
  Object.defineProperty(navigator, 'webdriver', { get: () => false });
  Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
  Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
});

/* MARQUER L'ÉLÉMENT MESURÉ, une fois pour toutes. Chercher « le premier
   visible » à chaque étape pourrait viser un autre élément après un
   défilement — et le contrôle mesurerait deux bulles différentes. */
const MARQUER = ([page, decl, filtre, marque, CLIQUABLE]) => {
  const vis = e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  const conteneur = e => {
    let a = e.parentElement;
    while (a && a !== document.body) { if (a.matches(CLIQUABLE)) return a; a = a.parentElement; }
    return null;
  };
  const tous = [...document.querySelectorAll('#p-' + page + ' ' + decl)].filter(vis);
  const el = tous.filter(e => {
    const c = conteneur(e);
    if (filtre === 'seul') return !c;
    if (filtre === 'fiche') return c && /^tmplOpen\(/.test(c.getAttribute('onclick') || '');
    if (filtre === 'formule') return c && c.classList.contains('plan-card');
    if (filtre === 'champ') return c && c.tagName === 'LABEL' && !!c.htmlFor;
    return true;
  })[0];
  if (!el) return null;
  el.setAttribute('data-recette', marque);
  const c = conteneur(el);
  return { conteneur: c ? (c.id || c.className || c.tagName) : null,
           pour: c && c.tagName === 'LABEL' ? c.htmlFor : null };
};

/* L'ÉTAT DE LA BULLE, lu sur l'élément ENFANT qui la porte. « Ouverte »
   veut dire : affichée, visible, et opaque — les trois, puisque chaque
   famille s'allume par une propriété différente. */
const ETAT = ([marque, bulle]) => {
  const el = document.querySelector('[data-recette="' + marque + '"]');
  if (!el) return null;
  const b = el.querySelector(bulle);
  const cs = getComputedStyle(b), r = b.getBoundingClientRect();
  const ouverte = cs.display !== 'none' && cs.visibility !== 'hidden' && parseFloat(cs.opacity) > 0.9;
  const norme = s => (s || '').replace(/\s+/g, ' ').trim();
  return {
    ouverte, display: cs.display, visibility: cs.visibility, opacite: cs.opacity,
    rect: [r.x, r.y, r.width, r.height].map(v => Math.round(v)).join(','),
    classe: el.classList.contains((window.infobulles || {}).classe || 'bulle-ouverte'),
    reconnue: !!(window.infobulles && el.matches(window.infobulles.selecteur)),
    focus: document.activeElement === el,
    focusVisible: el.matches(':focus-visible'),
    survol: el.matches(':hover'),
    texte: norme(b.textContent),
    annonce: norme((document.getElementById('bulle-annonce') || {}).textContent),
    fiche: !!document.querySelector('#tmpl-modal.open'),
  };
};
const annonce = (e) => !!e && e.texte.length > 10 && e.annonce.indexOf(e.texte.slice(0, 30)) >= 0;

async function aller(p, page) {
  await p.evaluate(pg => window.go(pg), page);
  await p.waitForTimeout(1500);
}
async function ailleurs(p, page) {
  await p.locator('#p-' + page + ' h1, #p-' + page + ' .page-h').first().tap({ timeout: 5000 }).catch(() => {});
  await p.waitForTimeout(500);
}
async function fermerLaFiche(p) {
  await p.evaluate(() => { const m = document.getElementById('tmpl-modal'); if (m) m.classList.remove('open'); });
  await p.waitForTimeout(300);
}

(async () => {
  const nav = await chromium.launch();
  const erreurs = [], refus = [];
  const surveiller = (p) => {
    p.on('pageerror', e => erreurs.push(String(e).slice(0, 160)));
    p.on('response', r => { if (r.status() === 429) refus.push(r.url()); });
  };

  // ══ 1. AU DOIGT ════════════════════════════════════════════════════════
  console.log('\n══ 1. Au doigt — chaque famille s’ouvre, s’annonce, se referme ══\n');
  let ctx = await nav.newContext({ ...devices['Pixel 7'], hasTouch: true, isMobile: true });
  await FURTIF(ctx);
  let p = await ctx.newPage();
  surveiller(p);
  await p.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'domcontentloaded' });
  const rep = await p.goto(BASE + '/sentinel?goto=maturite', { waitUntil: 'domcontentloaded' });
  ok('la page répond', rep && rep.status() === 200, rep && rep.status());
  await p.waitForFunction(() => !!document.getElementById('css-bulle-ouverte'), null, { timeout: 15000 })
    .catch(() => {});
  await p.waitForTimeout(2500);
  ok('le contexte est bien tactile', await p.evaluate(() => matchMedia('(hover:none)').matches));

  /* I-4 — LA RÉGION D'ANNONCE EXISTE DÈS LE CHARGEMENT, VIDE.
     LE DÉFAUT MESURÉ : elle n'était créée qu'au premier texte à annoncer —
     absente au chargement. Une région `aria-live` insérée dans le même
     geste que son premier contenu est souvent TUE par les lecteurs d'écran :
     ils ne l'observaient pas encore quand le texte y est arrivé. Mesuré
     AVANT tout geste : sinon un appui l'aurait créée, et le contrôle
     passerait pour une raison sans rapport. */
  const r4 = await p.evaluate(() => {
    const r = document.getElementById('bulle-annonce');
    return r ? { presente: true, texte: r.textContent, live: r.getAttribute('aria-live') }
             : { presente: false };
  });
  ok('I-4 la région d’annonce existe dès le chargement, avant tout appui', r4.presente);
  ok('I-4 …vide, et déjà « live »', r4.presente && r4.texte === '' && r4.live === 'polite',
     r4.presente ? '« ' + r4.texte.slice(0, 30) + ' », aria-live=' + r4.live : 'absente');

  for (const f of FAMILLES) {
    console.log('\n  — ' + f.nom + ' (' + f.decl + ')');
    await aller(p, f.page);
    const marque = 'doigt-' + f.page + f.decl;
    const m = await p.evaluate(MARQUER, [f.page, f.decl, f.carte ? 'fiche' : 'seul', marque, CLIQUABLE]);
    ok(f.nom + ' — un déclencheur est à l’écran', !!m, m && m.conteneur);
    if (!m) continue;
    const vise = p.locator('[data-recette="' + marque + '"]' + (f.appui ? ' ' + f.appui : ''));
    const lire = () => p.evaluate(ETAT, [marque, f.bulle]);

    let e = await lire();
    ok(f.nom + ' — reconnue par le mécanisme partagé', e.reconnue);
    ok(f.nom + ' — au repos, la bulle est fermée', !e.ouverte, e.display + '/' + e.visibility + '/' + e.opacite);

    await vise.tap(); await p.waitForTimeout(600);
    e = await lire();
    ok(f.nom + ' — APRÈS L’APPUI, la bulle est ouverte', e.ouverte,
       e.display + '/' + e.visibility + '/' + e.opacite + (e.fiche ? ' — la fiche du document s’est ouverte à la place' : ''));
    /* LE CONTRÔLE QUI SÉPARE LE MÉCANISME DE L'ACCIDENT. Une bulle ouverte
       par un survol collant ou par un focus s'ouvre ici, dans Chromium ;
       elle ne s'ouvre pas là où le navigateur ne colle pas le survol. */
    ok(f.nom + ' — …et c’est le mécanisme qui l’ouvre, pas un survol ou un focus restés collés', e.classe);
    ok(f.nom + ' — le texte est annoncé au lecteur d’écran', annonce(e), '« ' + e.annonce.slice(0, 50) + ' »');
    if (f.carte) {
      ok(f.nom + ' — LE PREMIER APPUI N’OUVRE PAS la fiche du document', !e.fiche);
      await fermerLaFiche(p);
    }

    /* CHAQUE SORTIE SE MESURE DEPUIS UN ÉTAT RÉELLEMENT OUVERT — sinon le
       contrôle passerait sur une bulle déjà fermée. */
    e = await lire();
    ok(f.nom + ' — la bulle est ouverte avant d’éprouver le second appui', e.ouverte);
    await vise.tap(); await p.waitForTimeout(600);
    e = await lire();
    if (f.carte) {
      ok(f.nom + ' — LE SECOND APPUI ouvre la fiche du document', e.fiche);
      await fermerLaFiche(p);
    } else {
      ok(f.nom + ' — un second appui referme', !e.ouverte, e.display + '/' + e.visibility + '/' + e.opacite);
    }

    await vise.tap(); await p.waitForTimeout(600);
    e = await lire();
    ok(f.nom + ' — la bulle est rouverte avant d’éprouver Échap', e.ouverte);
    if (f.carte) await fermerLaFiche(p);
    await p.keyboard.press('Escape'); await p.waitForTimeout(500);
    e = await lire();
    ok(f.nom + ' — Échap referme', !e.ouverte, e.display + '/' + e.visibility + '/' + e.opacite);

    await vise.tap(); await p.waitForTimeout(600);
    if (f.carte) await fermerLaFiche(p);
    ok(f.nom + ' — rouverte avant d’éprouver un appui ailleurs', (await lire()).ouverte);
    await ailleurs(p, f.page);
    ok(f.nom + ' — un appui ailleurs referme', !(await lire()).ouverte);
  }

  // — Le « ? » posé DANS une carte de formule, et dans un libellé de champ.
  console.log('\n  — tarification : le « ? » d’une formule, et celui d’un champ');
  await aller(p, 'pricing');
  await p.waitForFunction(() => !!document.querySelector('#p-pricing .plan-card .prx-tip-icon'),
                          null, { timeout: 10000 }).catch(() => {});
  let m = await p.evaluate(MARQUER, ['pricing', '.prx-tip-icon', 'formule', 'doigt-formule', CLIQUABLE]);
  ok('un « ? » de formule est à l’écran', !!m, m && m.conteneur);
  if (m) {
    const carte = m.conteneur;
    const choisie = () => p.evaluate(id => { const c = document.getElementById(id);
      return !!c && c.classList.contains('plan-selected'); }, carte);
    await p.evaluate(() => document.querySelectorAll('.plan-card').forEach(c => c.classList.remove('plan-selected')));
    await p.locator('[data-recette="doigt-formule"]').tap(); await p.waitForTimeout(600);
    const e = await p.evaluate(ETAT, ['doigt-formule', '.prx-tip-bubble']);
    ok('LE PREMIER APPUI sur le « ? » ne CHOISIT PAS la formule', !(await choisie()), carte);
    ok('…et la bulle de la formule est ouverte', e.ouverte);
    await p.locator('[data-recette="doigt-formule"]').tap(); await p.waitForTimeout(900);
    ok('le SECOND appui rend la carte à son action : la formule est choisie', await choisie());
    /* LE SECOND APPUI FERME AUSSI LA BULLE, alors même que son clic passe à
       la carte — qui choisit la formule et déplace le focus vers le
       formulaire. Une bulle restée ouverte masquerait la carte choisie. */
    const apres = await p.evaluate(ETAT, ['doigt-formule', '.prx-tip-bubble']);
    ok('…et la bulle de la formule s’est refermée, la carte ayant agi',
       !!apres && !apres.ouverte, apres ? apres.display : 'la carte a été repeinte');
  }
  await aller(p, 'pricing');
  m = await p.evaluate(MARQUER, ['pricing', '.prx-tip-icon', 'champ', 'doigt-champ', CLIQUABLE]);
  ok('un « ? » de libellé de champ est à l’écran', !!m, m && m.pour);
  if (m) {
    const champ = m.pour;
    await p.evaluate(() => { if (document.activeElement) document.activeElement.blur(); });
    await p.locator('[data-recette="doigt-champ"]').tap(); await p.waitForTimeout(600);
    const e = await p.evaluate(ETAT, ['doigt-champ', '.prx-tip-bubble']);
    const focusChamp = await p.evaluate(id => document.activeElement === document.getElementById(id), champ);
    ok('LE PREMIER APPUI sur le « ? » ne donne PAS le focus au champ', !focusChamp, champ);
    ok('…et la bulle du champ est ouverte', e.ouverte, e.display);
    await p.locator('[data-recette="doigt-champ"]').tap(); await p.waitForTimeout(600);
    ok('le SECOND appui rend le libellé à son action : le champ a le focus',
       await p.evaluate(id => document.activeElement === document.getElementById(id), champ));
    /* MÊME CHOSE DANS LE LIBELLÉ : le second appui laisse le libellé donner
       le focus à son champ — et la bulle se ferme, au lieu de rester posée
       au-dessus du champ qu'on s'apprête à remplir. */
    const apres = await p.evaluate(ETAT, ['doigt-champ', '.prx-tip-bubble']);
    ok('…et la bulle du champ s’est refermée quand le focus est passé au champ',
       !apres.ouverte, apres.display);
  }

  // — I-5 : une bulle ouverte au doigt DANS une fenêtre modale, puis Échap.
  console.log('\n  — I-5 : une bulle ouverte dans une fenêtre modale, puis Échap');
  /* LE DÉFAUT MESURÉ : une seule frappe d'Échap fermait la bulle ET la
     fenêtre modale qui la contient — les deux écoutaient `keydown` sur
     `document`. On perdait la fenêtre (et ce qu'on y avait saisi) en voulant
     seulement fermer une explication.
     LA FENÊTRE : celle d'un guide de procédure, ouverte par sa fonction
     d'ouverture, qui ne fait QUE l'afficher — la génération par IA attend un
     bouton sur lequel la recette n'appuie jamais. Aucune modale de Sentinel
     ne porte aujourd'hui de bulle `data-tip` : la recette en pose une dans
     le corps de la fenêtre, et le script la ramasse comme n'importe quelle
     autre (son observateur la rend atteignable au clavier). */
  await aller(p, 'maturite');
  const pose = await p.evaluate(() => {
    if (typeof window.procOpenDoc !== 'function') return 'procOpenDoc absente';
    window.procOpenDoc('01');
    const m = document.getElementById('proc-modal'), corps = document.getElementById('proc-modal-body');
    if (!m || !corps || !m.classList.contains('on') || !m.classList.contains('mat-modal')) return 'la fenêtre ne s’est pas ouverte';
    const t = document.createElement('span');
    t.id = 'recette-tip-modale';
    t.setAttribute('data-tip', 'Bulle posée par la recette dans la fenêtre modale');
    t.textContent = '(i)';
    t.style.cssText = 'display:inline-block;padding:10px 14px';
    corps.insertBefore(t, corps.firstChild);
    return '';
  });
  ok('I-5 une fenêtre .mat-modal est ouverte, une bulle data-tip posée dedans', pose === '', pose);
  if (pose === '') {
    const I5 = () => p.evaluate(() => ({
      bulle: document.getElementById('recette-tip-modale').classList.contains('bulle-ouverte'),
      modale: document.getElementById('proc-modal').classList.contains('on'),
      annonce: ((document.getElementById('bulle-annonce') || {}).textContent || '').slice(0, 40) }));
    await p.waitForTimeout(300);
    await p.locator('#recette-tip-modale').tap(); await p.waitForTimeout(500);
    let e5 = await I5();
    ok('I-5 l’appui ouvre la bulle dans la fenêtre', e5.bulle && e5.modale, JSON.stringify(e5));
    await p.keyboard.press('Escape'); await p.waitForTimeout(400);
    e5 = await I5();
    ok('I-5 LE PREMIER ÉCHAP ferme la bulle', !e5.bulle);
    ok('I-5 …et LAISSE la fenêtre ouverte', e5.modale, 'fenêtre .on = ' + e5.modale);
    /* Le second Échap ne se juge que sur une fenêtre ENCORE ouverte : sinon
       « fermée » serait vrai d'avance. */
    const ouverteAvant = e5.modale;
    await p.keyboard.press('Escape'); await p.waitForTimeout(400);
    e5 = await I5();
    ok('I-5 le SECOND Échap ferme la fenêtre', ouverteAvant && !e5.modale,
       'ouverte avant : ' + ouverteAvant + ', après : ' + e5.modale);
    await p.evaluate(() => { const m = document.getElementById('proc-modal'); if (m) m.classList.remove('on');
      const t = document.getElementById('recette-tip-modale'); if (t) t.remove();
      if (window.infobulles) window.infobulles.fermer(); });
  }

  // ══ 2. LE RECENSEMENT ══════════════════════════════════════════════════
  console.log('\n══ 2. Recensement — tout déclencheur niché dans un élément cliquable est protégé ══\n');
  /* UNE BULLE D'AIDE DANS UNE CARTE CLIQUABLE, C'EST UNE BULLE ILLISIBLE AU
     DOIGT — le badge d'article l'a montré. On recense donc TOUS les
     déclencheurs des quatre familles, écran par écran, et non l'échantillon
     appuyé plus haut : un seul oublié rend le défaut à cet endroit-là.
     Protégé veut dire : il déclare « lire d'abord » (`data-bulle-avant-clic`)
     ou il arrête lui-même son clic (`event.stopPropagation()`). */
  for (const pg of ['maturite', 'templates', 'pricing', 'clients']) await aller(p, pg);
  const recense = await p.evaluate(([fams, CLIQUABLE]) => {
    const sel = (window.infobulles || {}).selecteur || '';
    const out = { total: 0, reconnus: 0, nus: [], nichés: 0 };
    for (const f of fams) {
      document.querySelectorAll(f).forEach(el => {
        out.total++;
        try { if (sel && el.matches(sel)) out.reconnus++; } catch (e) { /* sélecteur illisible */ }
        let a = el.parentElement, c = null;
        while (a && a !== document.body) { if (a.matches(CLIQUABLE)) { c = a; break; } a = a.parentElement; }
        if (!c) return;
        out.nichés++;
        const arrete = /stopPropagation/.test(el.getAttribute('onclick') || '');
        if (!el.hasAttribute('data-bulle-avant-clic') && !arrete) {
          out.nus.push(f + ' dans ' + (c.id || c.className.toString().split(' ')[0] || c.tagName));
        }
      });
    }
    return out;
  }, [FAMILLES.map(f => f.decl), CLIQUABLE]);
  ok('les quatre familles sont recensées', recense.total >= 150, recense.total + ' déclencheurs');
  ok('CHAQUE déclencheur est reconnu par le mécanisme partagé', recense.reconnus === recense.total,
     recense.reconnus + ' / ' + recense.total);
  const parConteneur = {};
  recense.nus.forEach(x => { parConteneur[x] = (parConteneur[x] || 0) + 1; });
  ok('AUCUN déclencheur niché dans un élément cliquable n’est laissé nu', recense.nus.length === 0,
     recense.nichés + ' nichés, ' + recense.nus.length + ' nus'
     + (recense.nus.length ? ' : ' + Object.entries(parConteneur).slice(0, 4).map(([k, v]) => v + '× ' + k).join(' · ') : ''));
  /* ET LE FILTRE NE RAMASSE RIEN D'AUTRE. Une règle de survol qui révèle un
     MENU (cliquable) n'est pas une bulle : si le script la prenait, un
     appui ouvrirait le menu et retiendrait son clic. */
  const autres = await p.evaluate((fams) => {
    const sel = (window.infobulles || {}).selecteur;
    if (!sel) return ['(pas de sélecteur publié)'];
    const connus = '[data-tooltip],[data-tip],' + fams.join(',');
    return [...document.querySelectorAll(sel)].filter(e => !e.matches(connus))
      .slice(0, 5).map(e => e.tagName + '.' + e.className);
  }, FAMILLES.map(f => f.decl));
  ok('le mécanisme ne ramasse rien d’autre que des bulles', autres.length === 0, autres.join(' · '));
  await ctx.close();

  // ══ 3. AU CLAVIER ══════════════════════════════════════════════════════
  console.log('\n══ 3. Au clavier — atteindre, lire, refermer sans perdre sa place ══\n');
  await pause(ATTENTE);
  ctx = await nav.newContext({ viewport: { width: 1280, height: 900 } });
  await FURTIF(ctx);
  p = await ctx.newPage();
  surveiller(p);
  await p.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'domcontentloaded' });
  await p.goto(BASE + '/sentinel?goto=maturite', { waitUntil: 'domcontentloaded' });
  await p.waitForFunction(() => !!document.getElementById('css-bulle-ouverte'), null, { timeout: 15000 })
    .catch(() => {});
  await p.waitForTimeout(2500);
  for (const f of FAMILLES) {
    await aller(p, f.page);
    const marque = 'clavier-' + f.page + f.decl;
    const m = await p.evaluate(MARQUER, [f.page, f.decl, f.carte ? 'fiche' : 'seul', marque, CLIQUABLE]);
    if (!m) { ok(f.nom + ' — un déclencheur est à l’écran', false); continue; }
    /* UN FOCUS DE CLAVIER, PAS UN FOCUS DE SCRIPT : une touche d'abord,
       puis le focus. C'est la modalité que `:focus-visible` reconnaît. */
    await p.keyboard.press('Shift');
    await p.evaluate(mq => document.querySelector('[data-recette="' + mq + '"]').focus(), marque);
    await p.waitForTimeout(600);
    let e = await p.evaluate(ETAT, [marque, f.bulle]);
    ok(f.nom + ' — le déclencheur PREND le focus', e.focus);
    ok(f.nom + ' — le focus ouvre la bulle', e.ouverte, e.display + '/' + e.visibility + '/' + e.opacite
       + (e.focus && !e.focusVisible ? ' (focus non reconnu comme clavier)' : ''));
    ok(f.nom + ' — le focus annonce le texte', annonce(e), '« ' + e.annonce.slice(0, 40) + ' »');
    await p.keyboard.press('Escape'); await p.waitForTimeout(500);
    e = await p.evaluate(ETAT, [marque, f.bulle]);
    ok(f.nom + ' — Échap referme SANS déplacer le focus', e.focus && !e.ouverte,
       (e.focus ? 'focus gardé' : 'focus perdu') + ', ' + e.display + '/' + e.visibility + '/' + e.opacite);
    await p.evaluate(() => { if (document.activeElement) document.activeElement.blur(); });
  }

  // ══ 4. À LA SOURIS ═════════════════════════════════════════════════════
  console.log('\n══ 4. À la souris — rien n’a changé, et la bulle du doigt est LA MÊME ══\n');
  for (const f of FAMILLES) {
    await aller(p, f.page);
    const marque = 'souris-' + f.page + f.decl;
    const m = await p.evaluate(MARQUER, [f.page, f.decl, f.carte ? 'fiche' : 'seul', marque, CLIQUABLE]);
    if (!m) { ok(f.nom + ' — un déclencheur est à l’écran', false); continue; }
    const vise = p.locator('[data-recette="' + marque + '"]' + (f.appui ? ' ' + f.appui : ''));
    await vise.hover(); await p.waitForTimeout(700);
    const survol = await p.evaluate(ETAT, [marque, f.bulle]);
    ok(f.nom + ' — le survol ouvre toujours la bulle', survol.ouverte);
    /* LE CONTRÔLE DIFFÉRENTIEL, DANS LA MÊME FENÊTRE : la bulle ouverte par
       la CLASSE doit être exactement celle du SURVOL — affichage, opacité,
       visibilité, et la boîte au pixel près. Une valeur devinée dans le
       script la décalerait ; une jumelle mal dérivée ne l'ouvrirait pas. */
    await p.mouse.move(2, 2); await p.waitForTimeout(700);
    await p.evaluate(mq => window.infobulles.ouvrir(document.querySelector('[data-recette="' + mq + '"]')), marque);
    await p.waitForTimeout(700);
    const classe = await p.evaluate(ETAT, [marque, f.bulle]);
    const ecarts = ['display', 'visibility', 'opacite', 'rect'].filter(k => survol[k] !== classe[k]);
    ok(f.nom + ' — la bulle OUVERTE PAR LA CLASSE est exactement celle du SURVOL', ecarts.length === 0,
       ecarts.length ? ecarts.map(k => k + ' : survol=' + survol[k] + ' classe=' + classe[k]).join(' · ')
                     : 'affichage, opacité, visibilité et boîte identiques');
    await p.evaluate(() => window.infobulles.fermer());
    await p.waitForTimeout(300);

    /* ÉCHAP SOUS LA SOURIS (WCAG 1.4.13) : la bulle doit pouvoir se
       fermer sans bouger le pointeur — puis revenir quand on repasse. */
    await vise.hover(); await p.waitForTimeout(700);
    ok(f.nom + ' — ouverte au survol avant d’éprouver Échap', (await p.evaluate(ETAT, [marque, f.bulle])).ouverte);
    await p.keyboard.press('Escape'); await p.waitForTimeout(500);
    ok(f.nom + ' — Échap referme sous la souris', !(await p.evaluate(ETAT, [marque, f.bulle])).ouverte);
    await p.mouse.move(2, 2); await p.waitForTimeout(500);
    await vise.hover(); await p.waitForTimeout(700);
    ok(f.nom + ' — et le survol suivant la rouvre', (await p.evaluate(ETAT, [marque, f.bulle])).ouverte);
    await p.mouse.move(2, 2); await p.waitForTimeout(300);

    if (f.carte) {
      /* LA SOURIS N'A RIEN À LIRE D'ABORD : elle a déjà lu au survol. Un
         clic sur le badge ouvre la fiche, comme avant, en UN clic. */
      await vise.click(); await p.waitForTimeout(700);
      const e = await p.evaluate(ETAT, [marque, f.bulle]);
      ok(f.nom + ' — un clic de souris ouvre la fiche du premier coup, comme avant', e.fiche);
      ok(f.nom + ' — et ne laisse aucune bulle collante',
         await p.evaluate(() => document.querySelectorAll('.bulle-ouverte').length === 0));
      await fermerLaFiche(p);
    }
  }

  // ══ 4 bis. LE FOCUS PART, LA SOURIS RESTE ══════════════════════════════
  console.log('\n══ 4 bis. Fermée par Échap : le focus part, la souris reste — elle reste fermée ══\n');
  /* LE CAS QUI JUSTIFIE LA GARDE DU FOCUS, REPRODUIT AU NAVIGATEUR. Une
     bulle fermée par Échap tient tant que l'élément est tenu — survolé OU
     focalisé. Focus clavier sur le déclencheur, souris posée dessus, Échap,
     puis Tab : le focus part, la souris reste. Mesuré sur le code sans la
     garde : la bulle se ROUVRAIT sous la souris, que l'on venait de fermer.
     Au doigt, le cas ne se produit pas dans Chromium (le survol collé part
     avec le défilement) — c'est au poste fixe qu'il se reproduit. */
  for (const f of FAMILLES.filter(x => !x.carte)) {
    await aller(p, f.page);
    const marque = 'tenu-' + f.page + f.decl;
    const m = await p.evaluate(MARQUER, [f.page, f.decl, 'seul', marque, CLIQUABLE]);
    if (!m) { ok(f.nom + ' — un déclencheur est à l’écran', false); continue; }
    await p.evaluate(mq => document.querySelector('[data-recette="' + mq + '"]')
      .scrollIntoView({ block: 'center', behavior: 'instant' }), marque);
    await p.keyboard.press('Shift');
    await p.evaluate(mq => document.querySelector('[data-recette="' + mq + '"]').focus(), marque);
    const b = await p.locator('[data-recette="' + marque + '"]').boundingBox();
    await p.mouse.move(b.x + b.width / 2, b.y + b.height / 2);
    await p.waitForTimeout(600);
    let e = await p.evaluate(ETAT, [marque, f.bulle]);
    ok(f.nom + ' — focus clavier ET souris dessus : la bulle est ouverte',
       e.focus && e.survol && e.ouverte, 'focus ' + e.focus + ', survol ' + e.survol);
    await p.keyboard.press('Escape'); await p.waitForTimeout(500);
    ok(f.nom + ' — Échap la ferme', !(await p.evaluate(ETAT, [marque, f.bulle])).ouverte);
    await p.keyboard.press('Tab'); await p.waitForTimeout(600);
    e = await p.evaluate(ETAT, [marque, f.bulle]);
    ok(f.nom + ' — Tab : le focus est parti, la souris est restée', !e.focus && e.survol,
       'focus ' + e.focus + ', survol ' + e.survol);
    ok(f.nom + ' — LE POINT QUI DÉCIDE : la bulle fermée ne se rouvre pas sous la souris',
       !e.ouverte, e.display + '/' + e.visibility + '/' + e.opacite);
    await p.mouse.move(2, 2); await p.waitForTimeout(500);
    await p.mouse.move(b.x + b.width / 2, b.y + b.height / 2); await p.waitForTimeout(700);
    ok(f.nom + ' — la souris partie puis revenue, le survol la rouvre',
       (await p.evaluate(ETAT, [marque, f.bulle])).ouverte);
    await p.mouse.move(2, 2); await p.waitForTimeout(300);
  }
  await ctx.close();

  // ══ 5. PROPRETÉ ════════════════════════════════════════════════════════
  console.log('\n══ 5. Rien ne s’est cassé en route ══\n');
  ok('aucune erreur de script', erreurs.length === 0, erreurs.slice(0, 2).join(' | '));
  ok('aucune requête refusée par le limiteur — la recette a mesuré les écrans', refus.length === 0,
     refus.length + ' refus');

  console.log('\n' + (ko ? ko + ' contrôle(s) en échec sur ' + n : n + ' contrôles passés, 0 en échec — TOUT EST VERT'));
  await nav.close();
  process.exit(ko ? 1 : 0);
})();
