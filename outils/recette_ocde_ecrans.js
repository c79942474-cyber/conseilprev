/* RECETTE NAVIGATEUR — LES QUATRE ÉCRANS DE LA DILIGENCE OCDE.
 *
 * CE QU'ELLE MESURE, ET POURQUOI AUCUNE RÈGLE PYTHON NE LE FAIT. Les quatre
 * écrans sont PEINTS par `ocdePeindre` depuis la route du référentiel : le
 * HTML ne porte qu'un « Chargement… ». Une règle qui lit le fichier voit donc
 * le gabarit, jamais l'écran. Trois défauts de ce dépôt ont été mesurés ainsi
 * et pas autrement : un `go()` sans crochet laissant « Chargement… » sans
 * fin, un référentiel partiel peint comme un référentiel complet, et une
 * mention de licence restée dans la charge sans jamais atteindre l'écran.
 *
 * LA LICENCE EST LE POINT DE CETTE RECETTE. Les deux mentions que CC BY 4.0
 * impose et la citation de l'œuvre doivent être LUES à l'écran, pas seulement
 * servies : c'est la condition à laquelle ce module a le droit d'exister.
 *
 *   node outils/recette_ocde_ecrans.js
 */
'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn } = require('child_process');

const RACINE = path.dirname(__dirname);
const JETON = 'recette-ocde-ecrans-0000000000000000';
const ECRANS = ['ocde-processus', 'ocde-questionnaire', 'ocde-conformite',
                'ocde-analyse'];

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

function porteLePort(pid, port) {
  try {
    const env = fs.readFileSync('/proc/' + pid + '/environ', 'latin1');
    return env.split('\0').indexOf('PORT=' + port) >= 0;
  } catch (e) { return false; }
}

/* L'AGENT D'UN NAVIGATEUR, ET C'EST MESURÉ : le serveur rend 404 aux agents
   qui ressemblent à un robot (« UA=node »), et la sonde croyait le serveur
   mort alors qu'il refusait poliment de lui parler. */
const NAVIGATEUR = 'Mozilla/5.0 (X11; Linux x86_64) Firefox/130.0';

function sonder(url) {
  return fetch(url, { headers: { 'User-Agent': NAVIGATEUR } });
}

function attendre(base, limite) {
  const t0 = Date.now();
  return (async () => {
    for (;;) {
      try {
        const r = await sonder(base + '/');
        if (r.status === 200) return;
      } catch (e) { /* pas encore levé */ }
      if (Date.now() - t0 > limite) throw new Error('le serveur ne répond pas');
      await new Promise((r) => setTimeout(r, 250));
    }
  })();
}

async function lancer() {
  const port = await portLibre();
  const journal = path.join(os.tmpdir(), 'recette_ocde_' + port + '.log');
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

/* LE JOURNAL SURVIT QUAND IL Y A UNE FAUTE : « le corps ne se peint pas »
   ne dit pas POURQUOI, et la raison est côté serveur (429, 404, blocage). */
function arreter(s, garder) {
  if (!s || !porteLePort(s.pid, s.port)) return;
  try { process.kill(s.pid, 'SIGTERM'); } catch (e) { /* déjà parti */ }
  if (garder) { console.log('  journal du serveur : ' + s.journal); return; }
  try { fs.unlinkSync(s.journal); } catch (e) { /* rien */ }
}

function refus(journal) {
  try {
    return fs.readFileSync(journal, 'utf8').split('\n')
      .filter((l) => /RATE_LIMIT|SCRAPING|BLOCK|ocde/.test(l)).slice(-12);
  } catch (e) { return []; }
}

(async () => {
  const { chromium } = require('/opt/node22/lib/node_modules/playwright');
  let serveur = null, nav = null;
  const fautes = [], dits = [];
  try {
    serveur = await lancer();
    console.log('  serveur : ' + serveur.base + ' (pid ' + serveur.pid + ')');
    nav = await chromium.launch();
    const ctx = await nav.newContext({ viewport: { width: 1500, height: 1000 },
                                      userAgent: NAVIGATEUR });
    await ctx.addInitScript(() => {
      Object.defineProperty(navigator, 'webdriver', { get: () => false });
      Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
      Object.defineProperty(navigator, 'plugins',
                            { get: () => ({ length: 3, 0: {}, 1: {}, 2: {} }) });
    });
    const pg = await ctx.newPage();
    const erreurs = [];
    pg.on('pageerror', (e) => erreurs.push(String(e).slice(0, 200)));
    await pg.goto(serveur.base + '/auth/' + JETON, { waitUntil: 'commit' });
    await pg.waitForFunction(
      () => typeof go === 'function' && typeof window.ocdeInit === 'function',
      null, { timeout: 90000 });

    /* ── 1. LE TIROIR EXISTE, ET SA TEINTE N'EST PAS LE BLEU DE L'OCDE ──── */
    const tiroir = await pg.evaluate(() => {
      const sec = document.querySelector('.sb-section[data-grp="ocde"]');
      const items = document.querySelectorAll('.sb-item[data-norme="ocde"]');
      if (!sec) return null;
      return { teinte: getComputedStyle(sec).getPropertyValue('--sb-ic').trim(),
               onglets: items.length };
    });
    if (!tiroir) fautes.push('le tiroir « ocde » est absent de la barre');
    else {
      dits.push('tiroir : ' + tiroir.onglets + ' onglet(s), teinte ' + tiroir.teinte);
      if (tiroir.onglets !== 4) fautes.push('le tiroir porte ' + tiroir.onglets + ' onglets au lieu de 4');
      if (!/^#?550707$/i.test(tiroir.teinte.replace('#', '#'))) {
        fautes.push('la teinte du tiroir est ' + tiroir.teinte + ' et non #550707');
      }
    }

    /* ── 2. UN GROUPE EST DÉCLARÉ AVANT TOUT : l'écran « questionnaire »
           ne peint RIEN sans lui, et c'est voulu — le questionnaire ne sait
           pas lesquels des 115 exemples visent ce client avant les groupes.
           Une recette qui l'ouvrirait d'abord lirait ce refus comme un
           défaut de peinture. Mesuré. ─────────────────────────────────── */
    await pg.evaluate((x) => go(x), 'ocde-processus');
    await pg.waitForFunction(
      () => { const e = document.getElementById('ocde-processus-body');
              return e && e.querySelector('[data-cle]'); },
      null, { timeout: 30000 });
    const groupe = await pg.evaluate(() => {
      const b = document.querySelector('#ocde-processus-body [data-cle]');
      if (!b) return null;
      const cle = b.getAttribute('data-cle');
      b.click();
      return cle;
    });
    if (!groupe) {
      fautes.push('aucun groupe cliquable sur l\'écran « processus »');
    } else {
      dits.push('groupe déclaré : « ' + groupe + ' »');
    }
    await pg.waitForTimeout(600);

    /* ── 3. CHAQUE ÉCRAN SE PEINT PAR go() SEUL, SANS RECHARGEMENT ─────── */
    for (const id of ECRANS) {
      await pg.evaluate((x) => go(x), id);
      const corps = id + '-body';
      try {
        await pg.waitForFunction((c) => {
          const e = document.getElementById(c);
          return e && !e.classList.contains('veille-loading')
                 && e.textContent.indexOf('Chargement') < 0
                 && e.textContent.length > 400;
        }, corps, { timeout: 30000 });
      } catch (e) {
        const vu = await pg.evaluate((c) => {
          const el = document.getElementById(c);
          return el ? el.textContent.slice(0, 120) : '(absent)';
        }, corps);
        fautes.push(id + ' : le corps ne se peint pas — « ' + vu + ' »');
        continue;
      }
      const n = await pg.evaluate((c) => document.getElementById(c).textContent.length, corps);
      dits.push(id + ' : ' + n + ' caractères peints');
    }

    /* ── 4. LA LICENCE EST LUE À L'ÉCRAN, PAS SEULEMENT SERVIE ─────────── */
    const PY = [
      'import json, ocde_ia as m',
      'print(json.dumps({"citation": m.SOURCE["citation"],',
      '                  "mention_traduction": m.MENTION_TRADUCTION,',
      '                  "mention_adaptation": m.MENTION_ADAPTATION}))',
    ].join('\n');
    const ref = JSON.parse(require('child_process').execFileSync(
      'python3', ['-c', PY], { cwd: RACINE, encoding: 'utf8' }));
    let licenceOk = true;
    for (const id of ['ocde-processus', 'ocde-conformite', 'ocde-analyse']) {
      await pg.evaluate((x) => go(x), id);
      await pg.waitForTimeout(500);
      const txt = await pg.evaluate((c) => {
        const e = document.getElementById(c);
        return e ? e.textContent : '';
      }, id + '-body');
      for (const [nom, attendu] of [['citation', ref.citation],
                                    ['mention de traduction', ref.mention_traduction],
                                    ['mention d\'adaptation', ref.mention_adaptation]]) {
        if (txt.indexOf(attendu.slice(0, 60)) < 0) {
          fautes.push(id + ' : la ' + nom + ' n\'est pas peinte');
          licenceOk = false;
        }
      }
      if (txt.indexOf('OCDE') < 0) {
        fautes.push(id + ' : l\'écran ne nomme pas l\'OCDE');
        licenceOk = false;
      }
    }
    if (licenceOk) {
      dits.push('licence : citation + deux mentions lues sur les trois écrans');
    }

    /* ── 5. LE TAUX NE S'APPELLE PAS « CONFORMITÉ » ────────────────────── */
    await pg.evaluate((x) => go(x), 'ocde-questionnaire');
    await pg.waitForTimeout(600);
    const q = await pg.evaluate(() => {
      const e = document.getElementById('ocde-questionnaire-body');
      return e ? e.textContent : '';
    });
    if (q.indexOf('Couverture des exemples retenus') < 0) {
      fautes.push('le questionnaire ne nomme pas « Couverture des exemples retenus »');
    } else {
      dits.push('le taux s\'appelle « Couverture des exemples retenus »');
    }

    /* ── 6. LA DÉCLARATION SE GARDE AU RECHARGEMENT ────────────────────── */
    if (groupe) {
      await pg.reload({ waitUntil: 'commit' });
      await pg.waitForFunction(() => typeof window.ocdeInit === 'function',
                               null, { timeout: 60000 });
      await pg.evaluate(() => go('ocde-processus'));
      await pg.waitForTimeout(1500);
      const garde = await pg.evaluate(() => {
        try {
          return (JSON.parse(localStorage.getItem('cp-sentinel-ocde-v1')) || {}).qualification;
        } catch (e) { return null; }
      });
      if (!garde || (garde.groupes || []).indexOf(groupe) < 0) {
        fautes.push('le groupe « ' + groupe + ' » n\'est pas gardé au rechargement : '
                    + JSON.stringify(garde));
      } else {
        dits.push('mémoire : le groupe « ' + groupe + ' » survit au rechargement');
      }
    }

    if (erreurs.length) fautes.push('erreurs de page : ' + erreurs.slice(0, 3).join(' | '));
  } finally {
    if (nav) await nav.close();
    if (fautes.length && serveur) {
      for (const l of refus(serveur.journal)) console.log('    | ' + l.slice(0, 150));
    }
    arreter(serveur, fautes.length > 0);
  }
  for (const d of dits) console.log('  · ' + d);
  if (fautes.length) {
    console.log('\n  ' + fautes.length + ' FAUTE(S) :');
    for (const f of fautes) console.log('    ✗ ' + f);
    process.exit(1);
  }
  console.log('\n  recette OCDE : aucune faute');
})().catch((e) => { console.error(e); process.exit(1); });
