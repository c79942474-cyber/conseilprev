/* RECETTE NAVIGATEUR — LE BANDEAU D'INVITATION DE L'ACCUEIL.
 *
 * Le bandeau « Gouverner et sécuriser l'IA » (formation du lundi 9 novembre
 * 2026, Novotel Paris Les Halles) remplace le badge « Sentinel AI —
 * Gouvernance IA » en tête de l'accueil. Une règle qui lit le fichier voit
 * le gabarit ; cette recette CLIQUE, et mesure ce que chaque clic produit :
 *
 *   - l'inscription : le lien mailto est celui de l'invitation PDF, octet
 *     pour octet, et un message dit quoi faire si aucune messagerie ne s'ouvre ;
 *   - le programme : il s'ouvre et se referme à la souris ET au clavier ;
 *   - « Voir les conditions » : ouvre le programme et met les conditions à
 *     l'écran, focalisées — elles se lisent AVANT de s'inscrire ;
 *   - l'agenda : un vrai fichier .ics, heure de Paris, lignes de 75 octets
 *     au plus (RFC 5545), conditions comprises ; et le lien Google Agenda ;
 *   - la copie de l'adresse, l'itinéraire, les liens de contact, le PDF servi ;
 *   - le placement : le bandeau sous ce que la barre fixe MONTRE, de 390 à
 *     1 440 px — sa dernière rangée déborde de sa boîte entre 800 et 1 100 px ;
 *   - FR, EN, DE, compte à rebours compris ;
 *   - le temps : « Demain », « Aujourd'hui », puis le retrait du bandeau et le
 *     retour du badge le 9 novembre à 18 h, heure de Paris.
 *
 * L'HORLOGE EST FIXÉE, ET C'EST VOULU : jouée un autre jour, une recette qui
 * lirait l'heure réelle verrait un autre compte à rebours — puis, après le
 * 9 novembre, plus de bandeau du tout. Elle échouerait pour une raison qui
 * n'est pas un défaut.
 *
 *   node outils/recette_bandeau_formation.js
 */
'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn } = require('child_process');

const RACINE = path.dirname(__dirname);
const AUJOURDHUI = '2026-10-04T12:00:00+02:00';
/* Le lien de l'annotation « Cliquez pour vous inscrire » du PDF, recopié tel
   quel : c'est la référence que le bandeau doit reproduire. */
const PDF_MAILTO = 'mailto:christophe.cerf@outlook.com?subject=Inscription%20-%20Formation%20IA%20du%209%20novembre%202026&body=Bonjour%2C%0A%0AJe%20souhaite%20m%27inscrire%20%C3%A0%20la%20formation%20%C2%AB%20Gouverner%20et%20s%C3%A9curiser%20l%27IA%20%C2%BB%20du%20lundi%209%20novembre%202026%20(14h-18h)%20au%20Novotel%20Paris%20Les%20Halles.%0A%0ANom%20%3A%0AFonction%20%3A%0ASoci%C3%A9t%C3%A9%20%3A%0AT%C3%A9l%C3%A9phone%20%3A%0A%0ACordialement';

/* L'AGENT D'UN NAVIGATEUR : le serveur rend 404 aux agents qui ressemblent à
   un robot, et bloque l'adresse sur les signaux d'un navigateur sans tête —
   d'où les trois signaux masqués dans contexte(). */
const NAVIGATEUR = 'Mozilla/5.0 (X11; Linux x86_64) Firefox/130.0';

function portLibre() {
  const net = require('net');
  const essayer = (p) => new Promise((r) => {
    const s = net.createServer();
    s.once('error', () => r(false));
    s.listen(p, '127.0.0.1', () => s.close(() => r(true)));
  });
  return (async () => {
    for (let p = 9962; p <= 9990; p++) if (await essayer(p)) return p;
    throw new Error('aucun port libre entre 9962 et 9990');
  })();
}

async function lancer() {
  const port = await portLibre();
  const journal = path.join(os.tmpdir(), 'recette_bandeau_' + port + '.log');
  const fd = fs.openSync(journal, 'w');
  const enfant = spawn('python3', ['app.py'], {
    cwd: RACINE, detached: true, stdio: ['ignore', fd, fd],
    env: Object.assign({}, process.env, { PORT: String(port) }),
  });
  enfant.unref();
  const base = 'http://127.0.0.1:' + port;
  const t0 = Date.now();
  for (;;) {
    try {
      const r = await fetch(base + '/', { headers: { 'User-Agent': NAVIGATEUR } });
      if (r.status === 200) break;
    } catch (e) { /* pas encore levé */ }
    if (Date.now() - t0 > 90000) {
      throw new Error('le serveur ne répond pas\n' + fs.readFileSync(journal, 'utf8').slice(-600));
    }
    await new Promise((r) => setTimeout(r, 250));
  }
  return { pid: enfant.pid, base, journal };
}

function arreter(s, garder) {
  if (!s) return;
  try { process.kill(s.pid, 'SIGTERM'); } catch (e) { /* déjà parti */ }
  if (garder) { console.log('  journal du serveur : ' + s.journal); return; }
  try { fs.unlinkSync(s.journal); } catch (e) { /* rien */ }
}

async function contexte(nav, opts = {}) {
  const ctx = await nav.newContext(Object.assign({ viewport: { width: 1440, height: 900 }, userAgent: NAVIGATEUR, locale: 'fr-FR', acceptDownloads: true }, opts));
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
    Object.defineProperty(navigator, 'plugins', { get: () => ({ length: 3, 0: {}, 1: {}, 2: {} }) });
  });
  return ctx;
}

(async () => {
  const { chromium } = require('/opt/node22/lib/node_modules/playwright');
  const fautes = [], vus = [];
  const ok = (c, m) => (c ? vus : fautes).push(m);
  let serveur = null, nav = null;
  try {
    serveur = await lancer();
    const base = serveur.base;
    nav = await chromium.launch();
    // ── 1. Français, le 4 octobre 2026 (J-36) ──────────────────────────── ─────────────────────────────────────────────
    const ctx = await contexte(nav);
    await ctx.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: base });
    const pg = await ctx.newPage();
    await pg.clock.setFixedTime(new Date(AUJOURDHUI));
    const erreurs = [];
    pg.on('pageerror', e => erreurs.push(String(e)));
    await pg.goto(base + '/?lang=fr', { waitUntil: 'load' });
    await pg.waitForTimeout(600);

    ok(await pg.isVisible('#inv-bandeau'), 'bandeau visible');
    ok(await pg.isHidden('#hero-badge-sentinel'), 'ancien badge masqué tant que la formation n\'a pas eu lieu');
    const cta = await pg.getAttribute('#inv-inscrire', 'href');
    ok(cta === PDF_MAILTO, 'inscription : lien IDENTIQUE à celui du PDF');
    const pied = await pg.$$eval('.inv-pied a[href^="mailto:"]', as => as.map(a => a.getAttribute('href')));
    ok(pied.length === 1 && pied[0] === PDF_MAILTO, 'lien e-mail du pied identique au PDF');
    ok((await pg.textContent('#inv-compte')).trim() === 'J-36', 'compte à rebours J-36 le 4 octobre : ' + (await pg.textContent('#inv-compte')));

    // Le clic sur l'inscription : on intercepte la navigation mailto
    await pg.evaluate(() => { document.getElementById('inv-inscrire').addEventListener('click', e => e.preventDefault()); });
    await pg.click('#inv-inscrire');
    const st1 = (await pg.textContent('#inv-statut')).trim();
    ok(/messagerie s'ouvre/.test(st1) && /christophe\.cerf@outlook\.com/.test(st1), 'inscription : message de repli affiché — « ' + st1 + ' »');

    // Programme
    ok(await pg.isHidden('#inv-programme'), 'programme fermé au départ');
    await pg.click('#inv-prog-btn');
    ok(await pg.isVisible('#inv-programme'), 'programme ouvert au clic');
    ok(await pg.getAttribute('#inv-prog-btn', 'aria-expanded') === 'true', 'aria-expanded=true');
    const etapes = await pg.$$eval('.inv-frise li', l => l.map(x => x.querySelector('time').textContent + ' ' + x.querySelector('strong').textContent));
    ok(etapes.length === 9 && etapes[0] === '14:00 Accueil des participants' && etapes[8] === '18:00 Clôture', 'programme : 9 étapes, 14:00 → 18:00');
    await pg.keyboard.press('Shift+Tab'); // le focus reste utilisable
    await pg.focus('#inv-prog-btn'); await pg.keyboard.press('Enter');
    ok(await pg.isHidden('#inv-programme'), 'programme refermé au clavier (Entrée)');
    await pg.keyboard.press('Space');
    ok(await pg.isVisible('#inv-programme'), 'programme rouvert au clavier (Espace)');

    // Conditions : l'appel sous l'inscription ouvre le programme et y mène
    await pg.click('#inv-prog-btn');                       // refermer d'abord
    ok(await pg.isHidden('#inv-programme'), 'programme refermé avant le test des conditions');
    ok(await pg.isVisible('#inv-cond-btn'), '« Voir les conditions » visible sous l\'inscription');
    await pg.click('#inv-cond-btn');
    await pg.waitForTimeout(900);
    ok(await pg.isVisible('#inv-programme') && await pg.getAttribute('#inv-prog-btn', 'aria-expanded') === 'true', 'conditions : le programme s\'ouvre, aria-expanded suit');
    const vue = await pg.evaluate(() => { const r = document.getElementById('inv-conditions').getBoundingClientRect(); return { haut: r.top, bas: r.bottom, h: innerHeight, focus: document.activeElement && document.activeElement.id }; });
    ok(vue.haut >= 0 && vue.bas <= vue.h && vue.focus === 'inv-conditions', 'conditions : à l\'écran et focalisées (' + Math.round(vue.haut) + '→' + Math.round(vue.bas) + ' / ' + vue.h + ')');
    const cond = await pg.$$eval('.inv-cond-liste li', l => l.map(x => x.textContent.trim()));
    ok(cond.length === 3
       && cond[0] === 'Gratuit sur inscription · places limitées'
       && cond[1] === "L'événement peut être reporté ou décalé en cas de participation insuffisante, ou annulé au plus tard 10 jours avant."
       && cond[2] === "Si besoin, l'événement pourra se dérouler dans un autre Novotel à Paris, à une autre date à définir.",
       'conditions : les trois lignes, mot pour mot');
    const gd = new URL(await pg.getAttribute('#inv-gcal', 'href')).searchParams.get('details');
    ok(/reporté ou décalé en cas de participation insuffisante, ou annulé au plus tard 10 jours avant\. Si besoin, l'événement pourra se dérouler dans un autre Novotel à Paris/.test(gd), 'Google Agenda : les conditions dans la description');

    // Agenda .ics
    const [dl] = await Promise.all([pg.waitForEvent('download'), pg.click('#inv-agenda')]);
    const chemin = await dl.path();
    const ics = fs.readFileSync(chemin, 'utf8');
    ok(dl.suggestedFilename() === 'formation-ia-conseilprev-2026-11-09.ics', 'agenda : nom du fichier ' + dl.suggestedFilename());
    ok(/\r\nDTSTART:20261109T130000Z\r\n/.test(ics) && /\r\nDTEND:20261109T170000Z\r\n/.test(ics), 'agenda : 14 h – 18 h heure de Paris (13 h – 17 h UTC)');
    const lignes = ics.split('\r\n').filter(Boolean);
    ok(lignes.every(l => Buffer.byteLength(l, 'utf8') <= 75), 'agenda : aucune ligne au-delà de 75 octets (RFC 5545)');
    const deplie = ics.replace(/\r\n /g, '');
    ok(/SUMMARY:Gouverner et sécuriser l'IA — formation CONSEILPREV/.test(deplie), 'agenda : titre intact après dépliage');
    ok(/LOCATION:Novotel Paris Les Halles\\, 8 place Marguerite de Navarre\\, 75001 Paris/.test(deplie), 'agenda : lieu échappé');
    ok(/BEGIN:VALARM[\s\S]*TRIGGER:-P1D/.test(deplie), 'agenda : rappel la veille');
    ok(/Conditions : L'événement peut être reporté ou décalé en cas de participation insuffisante\\, ou annulé au plus tard 10 jours avant\. Si besoin\\, l'événement pourra se dérouler dans un autre Novotel à Paris\\, à une autre date à définir\./.test(deplie), 'agenda : les conditions dans la description, virgules échappées');
    ok(/Fichier agenda téléchargé/.test(await pg.textContent('#inv-statut')), 'agenda : message affiché');

    // Copier l'adresse
    await pg.click('#inv-copier');
    await pg.waitForTimeout(200);
    const presse = await pg.evaluate(() => navigator.clipboard.readText());
    ok(presse === 'christophe.cerf@outlook.com', 'copier : presse-papiers = ' + presse);
    ok(/Adresse copiée/.test(await pg.textContent('#inv-statut')), 'copier : message affiché');

    // Liens
    const liens = await pg.$$eval('#inv-bandeau a', as => as.map(a => ({ h: a.getAttribute('href'), t: a.getAttribute('target'), r: a.getAttribute('rel'), d: a.getAttribute('download'), txt: a.textContent.trim() })));
    const par = h => liens.filter(l => l.h && l.h.indexOf(h) === 0);
    const maps = par('https://www.google.com/maps/dir/');
    ok(maps.length === 2 && maps.every(l => l.t === '_blank' && /noopener/.test(l.r)), 'itinéraire : 2 liens Google Maps, nouvel onglet, noopener');
    ok(decodeURIComponent(new URL(maps[0].h).searchParams.get('destination')) === 'Novotel Paris Les Halles, 8 place Marguerite de Navarre, 75001 Paris', 'itinéraire : destination exacte');
    const gc = par('https://calendar.google.com/');
    const gp = gc.length && new URL(gc[0].h).searchParams;
    ok(gc.length === 1 && gp.get('dates') === '20261109T130000Z/20261109T170000Z' && gp.get('action') === 'TEMPLATE', 'Google Agenda : dates et action');
    ok(par('tel:+33660692145').length === 1, 'téléphone : tel:+33660692145');
    ok(par('mailto:christophe.cerf@i-aes.com').length === 1, 'e-mail i-aes');
    ok(par('https://www.linkedin.com/in/cerfchristophe').length === 1, 'LinkedIn');
    ok(par('https://i-aes.eu').length === 1, 'i-aes.eu');
    ok(liens.some(l => l.h && /i-aes\.com/.test(l.h) && !/^mailto/.test(l.h)), 'i-aes.com (ou son relais si le site est injoignable)');
    const pdf = par('/evenements/invitation-formation-ia-2026-11-09.pdf');
    ok(pdf.length === 1 && pdf[0].d === 'Conseilprev_Invitation_Formation_IA_9_novembre_2026.pdf', 'PDF : lien de téléchargement');
    const rep = await pg.request.get(base + '/evenements/invitation-formation-ia-2026-11-09.pdf', { headers: { 'Accept-Language': 'fr-FR', 'Accept-Encoding': 'gzip' } });
    const corps = await rep.body();
    ok(rep.status() === 200 && corps.slice(0, 5).toString() === '%PDF-' && corps.length === fs.statSync(path.join(RACINE, 'evenements', 'invitation-formation-ia-2026-11-09.pdf')).size, 'PDF : servi (' + rep.status() + ', ' + rep.headers()['content-type'] + ', ' + corps.length + ' octets)');

    // Bulle de l'inscription : elle s'ouvre VERS LE BAS (sinon sous la barre fixe)
    const bulle = await pg.evaluate(() => { const s = getComputedStyle(document.getElementById('inv-inscrire'), '::after'); return { top: s.top, bottom: s.bottom, contenu: s.content }; });
    ok(bulle.top !== 'auto' && /messagerie/.test(bulle.contenu), 'bulle de l\'inscription vers le bas : top=' + bulle.top);

    // Placement : le bandeau sous ce que la barre montre
    for (const w of [1440, 1100, 800, 390]) {
      await pg.setViewportSize({ width: w, height: 900 });
      await pg.waitForTimeout(300);
      const g = await pg.evaluate(() => {
        const n = document.querySelector('nav'); let bas = n.getBoundingClientRect().bottom;
        for (const c of n.children) { const r = c.getBoundingClientRect(); if (r.height && r.bottom > bas) bas = r.bottom; }
        window.scrollTo(0, 0);
        return { bas: Math.round(bas), haut: Math.round(document.getElementById('inv-bandeau').getBoundingClientRect().top + window.scrollY), deborde: document.documentElement.scrollWidth > innerWidth };
      });
      ok(g.haut >= g.bas + 8 && !g.deborde, w + ' px : bandeau à ' + g.haut + ' px, barre jusqu\'à ' + g.bas + ' px, pas de défilement horizontal');
    }
    await pg.setViewportSize({ width: 1440, height: 900 });

    // ── 2. Anglais et allemand : textes ET compte à rebours ──────────────────
    await pg.evaluate(() => setLang('en'));
    await pg.waitForTimeout(150);
    ok((await pg.textContent('#inv-titre')).trim() === 'Governing and securing AI', 'EN : titre');
    ok((await pg.textContent('#inv-compte')).trim() === '36 days to go', 'EN : compte « ' + (await pg.textContent('#inv-compte')) + ' »');
    ok(/delivered in French/.test(await pg.textContent('.inv-pour')), 'EN : « delivered in French »');
    ok((await pg.getAttribute('#inv-inscrire', 'data-tooltip')) === 'Opens your email app with a ready-to-send registration email', 'EN : bulle traduite');
    ok(await pg.getAttribute('#inv-inscrire', 'href') === PDF_MAILTO, 'EN : le lien d\'inscription n\'a pas bougé');
    ok((await pg.textContent('#inv-cond-btn')).trim() === 'See the conditions' && /postponed or rescheduled if participation is insufficient, or cancelled no later than 10 days beforehand/.test(await pg.textContent('#inv-conditions')), 'EN : conditions traduites');
    await pg.evaluate(() => setLang('de'));
    await pg.waitForTimeout(150);
    ok((await pg.textContent('#inv-titre')).trim() === 'KI steuern und absichern', 'DE : titre');
    ok((await pg.textContent('#inv-compte')).trim() === 'noch 36 Tage', 'DE : compte « ' + (await pg.textContent('#inv-compte')) + ' »');
    ok(/in einem anderen Novotel in Paris zu einem noch festzulegenden Termin/.test(await pg.textContent('#inv-conditions')), 'DE : conditions traduites');
    const restes = await pg.evaluate(() => Array.from(document.querySelectorAll('#inv-bandeau [data-i18n]')).filter(e => e.innerHTML === e.dataset.i18n).map(e => e.dataset.i18n));
    ok(restes.length === 0, 'DE : aucune clé brute affichée ' + JSON.stringify(restes));
    await pg.evaluate(() => setLang('fr'));
    ok(erreurs.length === 0, 'aucune erreur JavaScript' + (erreurs.length ? ' : ' + erreurs.join(' | ') : ''));
    await ctx.close();

    // ── 3. Le temps : veille, jour J, après la fin ──────────────────────────
    const cas = [
      ['2026-11-08T20:00:00+01:00', 'Demain', true],
      ['2026-11-09T09:00:00+01:00', "Aujourd'hui", true],
      ['2026-11-09T17:59:00+01:00', "Aujourd'hui", true],
      ['2026-11-09T18:00:00+01:00', null, false],
      ['2026-12-01T10:00:00+01:00', null, false],
    ];
    for (const [quand, attendu, visible] of cas) {
      const c2 = await contexte(nav);
      const p2 = await c2.newPage();
      await p2.clock.setFixedTime(new Date(quand));
      await p2.goto(base + '/?lang=fr', { waitUntil: 'load' });
      await p2.waitForTimeout(300);
      const v = await p2.isVisible('#inv-bandeau');
      const b = await p2.isVisible('#hero-badge-sentinel');
      if (visible) ok(v && !b && (await p2.textContent('#inv-compte')).trim() === attendu, quand + ' : bandeau, « ' + (await p2.textContent('#inv-compte')).trim() + ' »');
      else ok(!v && b && /Sentinel AI/.test(await p2.textContent('#hero-badge-sentinel')), quand + ' : bandeau retiré, badge « Sentinel AI — Gouvernance IA » rendu');
      await c2.close();
    }
  } finally {
    if (nav) await nav.close();
    arreter(serveur, fautes.length > 0);
  }
  console.log(vus.map((m) => '  ✓ ' + m).join('\n'));
  if (fautes.length) {
    console.log('\n  ' + fautes.length + ' FAUTE(S) :\n' + fautes.map((m) => '    ✗ ' + m).join('\n'));
    process.exit(1);
  }
  console.log('\n  recette du bandeau : ' + vus.length + ' vérifications, aucune faute');
})().catch((e) => { console.error(e); process.exit(1); });
