/* RECETTE NAVIGATEUR — L'ANIMATION « SECURITY ADVISOR — BANQUE » DE L'ACCUEIL.
 *
 * CE QU'ELLE MESURE, ET QU'AUCUNE RÈGLE PYTHON NE PEUT MESURER : que la vidéo
 * JOUE. Les règles de `tests/test_hero_video.py` lisent le HTML, le script,
 * le dictionnaire et décodent le fichier ; elles ne voient pas un navigateur
 * refuser l'autolecture, un bouton qui ne fait rien, ou un serveur qui coupe
 * les requêtes par plage d'octets.
 *
 *   §1  le fichier est servi par plage d'octets (206), en video/mp4 ;
 *   §2  à l'ouverture de l'accueil, l'animation JOUE : le temps avance ;
 *   §3  le bouton l'arrête, la relance, et son libellé dit ce qu'il fera ;
 *   §4  le libellé suit la langue : en anglais, il est anglais ;
 *   §5  sous `prefers-reduced-motion`, elle ne démarre pas d'elle-même ;
 *   §6  le bandeau du 9 novembre n'est plus là.
 *
 *   node outils/recette_hero_video.js
 */
'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn } = require('child_process');

const RACINE = path.dirname(__dirname);
const JETON = 'recette-hero-video-000000000';
const NAVIGATEUR = 'Mozilla/5.0 (X11; Linux x86_64) Firefox/130.0';

function portLibre() {
  const net = require('net');
  const essayer = (p) => new Promise((r) => {
    const s = net.createServer();
    s.once('error', () => r(false));
    s.listen(p, '127.0.0.1', () => s.close(() => r(true)));
  });
  return (async () => {
    for (let p = 9942; p <= 9970; p++) if (await essayer(p)) return p;
    throw new Error('aucun port libre entre 9942 et 9970');
  })();
}

function porteLePort(pid, port) {
  try {
    const env = fs.readFileSync('/proc/' + pid + '/environ', 'latin1');
    return env.split('\0').indexOf('PORT=' + port) >= 0;
  } catch (e) { return false; }
}

function sonder(url) {
  return fetch(url, { headers: { 'User-Agent': NAVIGATEUR } });
}

async function attendre(base, limite) {
  const t0 = Date.now();
  for (;;) {
    try { if ((await sonder(base + '/')).status === 200) return; } catch (e) { /* pas levé */ }
    if (Date.now() - t0 > limite) throw new Error('le serveur ne répond pas');
    await new Promise((r) => setTimeout(r, 250));
  }
}

async function lancer() {
  const port = await portLibre();
  const journal = path.join(os.tmpdir(), 'recette_hero_video_' + port + '.log');
  const fd = fs.openSync(journal, 'w');
  const enfant = spawn('python', ['app.py'], {
    cwd: RACINE, detached: true, stdio: ['ignore', fd, fd],
    env: Object.assign({}, process.env,
                       { PORT: String(port), AUTH_MASTER_TOKEN: JETON }),
  });
  enfant.unref();
  const base = 'http://127.0.0.1:' + port;
  await attendre(base, 90000);
  if (enfant.exitCode !== null || !porteLePort(enfant.pid, port)) {
    throw new Error('le serveur lancé n\'a pas pris le port ' + port + '\n'
                    + fs.readFileSync(journal, 'utf8').slice(-600));
  }
  return { pid: enfant.pid, port, base, journal };
}

function arreter(s, garder) {
  if (!s || !porteLePort(s.pid, s.port)) return;
  try { process.kill(s.pid, 'SIGTERM'); } catch (e) { /* déjà parti */ }
  if (garder) { console.log('  journal du serveur : ' + s.journal); return; }
  try { fs.unlinkSync(s.journal); } catch (e) { /* rien */ }
}

(async () => {
  const { chromium } = require('/opt/node22/lib/node_modules/playwright');
  let serveur = null, nav = null;
  const fautes = [], dits = [];
  try {
    serveur = await lancer();
    console.log('  serveur : ' + serveur.base + ' (pid ' + serveur.pid + ')');

    /* ── §1. SERVIE PAR PLAGE ────────────────────────────────────────── */
    const r = await fetch(serveur.base + '/hero-security-advisor.mp4',
                          { headers: { 'User-Agent': NAVIGATEUR, Range: 'bytes=0-1023' } });
    const corps = Buffer.from(await r.arrayBuffer());
    if (r.status !== 206 || !/video\/mp4/.test(r.headers.get('content-type') || '') || corps.length !== 1024) {
      fautes.push('§1 : la vidéo n\'est pas servie par plage — ' + r.status + ', '
                  + r.headers.get('content-type') + ', ' + corps.length + ' octets');
    } else {
      dits.push('§1 — servie par plage d\'octets : 206, video/mp4, ' + r.headers.get('content-range'));
    }

    nav = await chromium.launch();
    const ouvrir = async (mouvement) => {
      const ctx = await nav.newContext({ viewport: { width: 1280, height: 900 }, locale: 'fr-FR',
                                         userAgent: NAVIGATEUR, reducedMotion: mouvement });
      await ctx.addInitScript(() => {
        Object.defineProperty(navigator, 'webdriver', { get: () => false });
        Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
        Object.defineProperty(navigator, 'plugins', { get: () => ({ length: 3, 0: {}, 1: {}, 2: {} }) });
      });
      const pg = await ctx.newPage();
      const erreurs = [];
      pg.on('pageerror', (e) => erreurs.push(String(e).slice(0, 200)));
      await pg.goto(serveur.base + '/', { waitUntil: 'load' });
      await pg.waitForTimeout(2500);
      return { ctx, pg, erreurs };
    };
    const etat = (pg) => pg.evaluate(() => {
      const v = document.getElementById('hero-video-lecteur');
      const b = document.getElementById('hero-video-btn');
      return { t: v ? v.currentTime : -1, paused: v ? v.paused : null, duree: v ? v.duration : 0,
               src: v ? v.currentSrc : '', etat: b ? b.getAttribute('data-etat') : null,
               libelle: b ? (b.textContent || '').trim() : '' };
    });

    /* ── §2. ELLE JOUE ───────────────────────────────────────────────── */
    const a = await ouvrir('no-preference');
    const e1 = await etat(a.pg);
    await a.pg.waitForTimeout(1500);
    const e2 = await etat(a.pg);
    if (e1.paused || !(e2.t > e1.t) || !/hero-security-advisor\.mp4$/.test(e2.src)) {
      fautes.push('§2 : l\'animation ne joue pas — ' + JSON.stringify([e1, e2]));
    } else {
      dits.push('§2 — elle joue : ' + e1.t.toFixed(2) + ' s → ' + e2.t.toFixed(2) + ' s, durée '
                + e2.duree.toFixed(1) + ' s');
    }

    /* ── §3. LE BOUTON ───────────────────────────────────────────────── */
    await a.pg.click('#hero-video-btn');
    await a.pg.waitForTimeout(400);
    const p1 = await etat(a.pg);
    await a.pg.waitForTimeout(800);
    const p2 = await etat(a.pg);
    await a.pg.click('#hero-video-btn');
    await a.pg.waitForTimeout(600);
    const p3 = await etat(a.pg);
    if (!p1.paused || p2.t !== p1.t || p1.etat !== 'pause' || !/Relancer/.test(p1.libelle)
        || p3.paused || p3.etat !== 'lecture' || !/pause/i.test(p3.libelle)) {
      fautes.push('§3 : le bouton ne commande pas l\'animation — ' + JSON.stringify([p1, p2, p3]));
    } else {
      dits.push('§3 — le bouton l\'arrête (« ' + p1.libelle + ' ») et la relance (« ' + p3.libelle + ' »)');
    }

    /* ── §4. LA LANGUE ───────────────────────────────────────────────── */
    await a.pg.evaluate(() => setLang('en'));
    await a.pg.waitForTimeout(300);
    const en = await a.pg.evaluate(() => ({
      btn: (document.getElementById('hero-video-btn').textContent || '').trim(),
      desc: (document.getElementById('hero-video-desc').textContent || '').trim() }));
    await a.pg.click('#hero-video-btn');
    await a.pg.waitForTimeout(300);
    const enPause = (await etat(a.pg)).libelle;
    if (en.btn !== 'Pause the animation' || !/^“Security Advisor/.test(en.desc) || enPause !== 'Play the animation') {
      fautes.push('§4 : les libellés ne suivent pas la langue — ' + JSON.stringify([en, enPause]));
    } else {
      dits.push('§4 — en anglais : « ' + en.btn + ' », puis « ' + enPause + ' », et la description traduite');
    }
    if (a.erreurs.length) fautes.push('erreurs JavaScript : ' + a.erreurs.join(' | '));

    /* ── §6. LE BANDEAU N'EST PLUS LÀ ────────────────────────────────── */
    const reste = await a.pg.evaluate(() => ({
      bandeau: !!document.getElementById('inv-bandeau'),
      texte: /Invitation gratuite|9 novembre 2026/i.test(document.querySelector('.hero').innerText || '') }));
    if (reste.bandeau || reste.texte) {
      fautes.push('§6 : le héros porte encore le bandeau du 9 novembre — ' + JSON.stringify(reste));
    } else {
      dits.push('§6 — le bandeau du 9 novembre a quitté le héros');
    }
    await a.ctx.close();

    /* ── §5. LE MOUVEMENT RÉDUIT ─────────────────────────────────────── */
    const b = await ouvrir('reduce');
    const r1 = await etat(b.pg);
    await b.pg.waitForTimeout(1200);
    const r2 = await etat(b.pg);
    if (!r1.paused || r2.t !== r1.t || r1.etat !== 'pause') {
      fautes.push('§5 : sous prefers-reduced-motion, elle démarre seule — ' + JSON.stringify([r1, r2]));
    } else {
      dits.push('§5 — mouvement réduit : arrêtée sur son affiche, bouton « ' + r1.libelle + ' »');
    }
    await b.ctx.close();
  } catch (e) {
    fautes.push('la recette s\'est interrompue : ' + (e && e.message ? e.message : e));
  } finally {
    if (nav) { try { await nav.close(); } catch (e) { /* rien */ } }
    arreter(serveur, fautes.length > 0);
  }

  console.log('\n── CE QUI A ÉTÉ MESURÉ ──');
  dits.forEach((d) => console.log('  · ' + d));
  if (fautes.length) {
    console.log('\n── FAUTES (' + fautes.length + ') ──');
    fautes.forEach((f) => console.log('  ✗ ' + f));
    process.exit(1);
  }
  console.log('\n✓ Animation de l\'accueil : tout ce qui est mesuré tient.');
})();
