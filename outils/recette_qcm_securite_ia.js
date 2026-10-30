/* RECETTE NAVIGATEUR — LE QCM DE SÉCURITÉ DE L'IA, DE L'ONGLET À LA MÉDAILLE.
 *
 * CE QU'ELLE MESURE, ET POURQUOI AUCUNE RÈGLE PYTHON NE LE FAIT. Les règles
 * de `tests/test_qcm_securite_ia.py` éprouvent la banque, les seuils, le rang
 * et la traduction, et exécutent deux fonctions de l'écran. Elles ne jouent
 * pas un niveau : la carte de question, le mélange des options, le clavier,
 * la correction, le bilan, la médaille, la progression gardée et l'écran
 * anglais ne se voient que dans un navigateur, après une vraie connexion.
 *
 * CE QUI EST JOUÉ :
 *   §1  la route sert la banque, et ses totaux sont cohérents ;
 *   §2  lien profond → porte → connexion → hub peint (quatre niveaux, les
 *       domaines, les médailles) ;
 *   §3  le niveau débutant joué AU CLAVIER, en choisissant chaque fois la
 *       touche de la bonne réponse — dont la position change d'une question
 *       à l'autre : la correction s'ouvre, dit pourquoi les autres options
 *       sont fausses, et le bilan rend la médaille du sans-faute ;
 *   §4  le niveau intermédiaire joué entièrement FAUX : aucune médaille, et
 *       l'écran le dit au lieu de se taire ;
 *   §5  la page rechargée : la progression est revenue ;
 *   §6  pendant tout cela, AUCUNE requête n'est partie vers le serveur en
 *       dehors de la lecture de la banque — c'est la promesse de l'écran ;
 *   §7  l'écran anglais : le hub survit à la bascule et se lit en anglais ;
 *   §8  un compte Gratuit est refusé explicitement.
 *
 * DEUX COMPTES RÉELS, rendus à la fin quoi qu'il arrive. La progression est
 * celle du navigateur de la recette, jeté avec lui.
 *
 *   node outils/recette_qcm_securite_ia.js
 */
'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn, execFileSync } = require('child_process');

const RACINE = path.dirname(__dirname);
const JETON = 'recette-qcm-securite-ia-0000000';
const COMPTE = 'recette-qcm@local.invalid';
const COMPTE_GRATUIT = 'recette-qcm-gratuit@local.invalid';
const SECRET = 'Recette-Qcm-Securite-2026!x';
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

/* POSÉ ET RETIRÉ PAR LA MÊME FONCTION, pour qu'on ne puisse pas poser sans
   savoir retirer. Le mot de passe passe par le `generate_password_hash` de
   l'inscription : un hachage écrit à la main ne serait pas reconnu. */
function compte(action, email, plan) {
  const py = [
    'import sqlite3, datetime',
    'from werkzeug.security import generate_password_hash',
    'c = sqlite3.connect(' + JSON.stringify(path.join(RACINE, 'registre_ia.db')) + ')',
    'cur = c.cursor()',
    'cur.execute("DELETE FROM clients WHERE email=?", (' + JSON.stringify(email) + ',))',
    action === 'poser'
      ? ('cur.execute("INSERT INTO clients (nom_entreprise,email,mot_de_passe_hash,'
         + 'actif,date_creation,plan) VALUES (?,?,?,1,?,?)", '
         + '("Recette", ' + JSON.stringify(email) + ', '
         + 'generate_password_hash(' + JSON.stringify(SECRET) + '), '
         + 'datetime.datetime.utcnow().isoformat(), ' + JSON.stringify(plan) + '))')
      : 'pass',
    'c.commit(); c.close()',
    'print("ok")',
  ].join('\n');
  execFileSync('python', ['-c', py], { cwd: RACINE, stdio: 'pipe' });
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
  const journal = path.join(os.tmpdir(), 'recette_qcm_' + port + '.log');
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
  let serveur = null, nav = null, pose = false;
  const fautes = [], dits = [];
  try {
    compte('poser', COMPTE, 'pro');
    compte('poser', COMPTE_GRATUIT, 'gratuit');
    pose = true;
    serveur = await lancer();
    console.log('  serveur : ' + serveur.base + ' (pid ' + serveur.pid + ')');

    /* ── §1. LA ROUTE, AVANT TOUT NAVIGATEUR ─────────────────────────── */
    const brut = await (await sonder(serveur.base + '/api/qcm-securite-ia/referentiel')).json();
    if (!brut || !brut.ok) throw new Error('/api/qcm-securite-ia/referentiel ne rend pas de banque');
    const REF = brut.referentiel;
    const total = REF.questions.length;
    const somme = Object.values(REF.par_niveau).reduce((a, b) => a + b, 0);
    if (somme !== total || REF.niveaux.length !== 4 || REF.domaines.length < 2) {
      fautes.push('§1 : banque incohérente — ' + total + ' questions, ' + somme
                  + ' par niveau, ' + REF.niveaux.length + ' niveaux');
    } else {
      dits.push('§1 — banque servie : ' + total + ' questions, '
                + REF.niveaux.map((n) => n.cle + ' ' + REF.par_niveau[n.cle]).join(', '));
    }

    nav = await chromium.launch();
    const ctx = await nav.newContext({ viewport: { width: 1400, height: 1000 },
                                       locale: 'fr-FR', userAgent: NAVIGATEUR });
    await ctx.addInitScript(() => {
      Object.defineProperty(navigator, 'webdriver', { get: () => false });
      Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
      Object.defineProperty(navigator, 'language', { get: () => 'fr-FR' });
      Object.defineProperty(navigator, 'plugins',
                            { get: () => ({ length: 3, 0: {}, 1: {}, 2: {} }) });
    });
    const pg = await ctx.newPage();
    const erreurs = [];
    let refus429 = 0;
    pg.on('pageerror', (e) => erreurs.push(String(e).slice(0, 200)));
    pg.on('response', (r) => { if (r.status() === 429) refus429++; });
    const PLAFOND_MINUTE = 120;
    const horloge = [];
    pg.on('response', () => horloge.push(Date.now()));
    const souffler = async (cout) => {
      for (;;) {
        const limite = Date.now() - 60000;
        while (horloge.length && horloge[0] < limite) horloge.shift();
        if (horloge.length + cout <= PLAFOND_MINUTE - 10) return;
        await pg.waitForTimeout(2500);
      }
    };
    /* §6 SE MESURE EN CONTINU. LA PREMIÈRE VERSION REFUSAIT TOUTE REQUÊTE
       pendant le jeu, et elle est tombée sur `GET /api/finance-dc`,
       `/api/kpi-finance`… : les rafraîchissements de fond de Sentinel, qui
       tournent que le QCM soit ouvert ou non. Ce n'est pas la promesse de
       l'écran. La promesse est que les RÉPONSES ne partent pas : on refuse
       donc toute requête qui n'est pas une lecture, toute route du QCM autre
       que la banque, et toute requête dont l'adresse ou le corps porte la
       progression ou le texte d'une question. Les lectures de fond sont
       comptées, et dites. */
    let enJeu = false;
    const emises = [], fond = [];
    pg.on('request', (r) => {
      if (!enJeu) return;
      const u = r.url().replace(serveur.base, '');
      if (u === '/api/qcm-securite-ia/referentiel' && r.method() === 'GET') return;
      if (['image', 'font', 'stylesheet'].indexOf(r.resourceType()) >= 0) return;
      const corps = r.postData() || '';
      const porte = /qcm|sentinel_qcm_ia/i.test(u + corps)
        || REF.questions.some((q) => corps.indexOf(q.q.slice(0, 40)) >= 0);
      if (r.method() !== 'GET' || porte) emises.push(r.method() + ' ' + u);
      else fond.push(u);
    });

    /* ── §2. LIEN PROFOND → PORTE → CONNEXION → HUB ──────────────────── */
    await souffler(6);
    await pg.goto(serveur.base + '/sentinel?goto=qcm-ia', { waitUntil: 'domcontentloaded' });
    await pg.fill('#login-email', COMPTE);
    await pg.fill('#login-password', SECRET);
    await souffler(105);
    await Promise.all([
      pg.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 60000 }),
      pg.click('#login-btn'),
    ]);
    if (pg.url().replace(serveur.base, '') !== '/sentinel?goto=qcm-ia') {
      throw new Error('après connexion le navigateur est sur ' + pg.url());
    }
    await pg.waitForFunction(() => typeof go === 'function', null, { timeout: 90000 });
    await pg.evaluate(() => { try { localStorage.removeItem('sentinel_qcm_ia_v1'); } catch (e) {} });
    await pg.waitForFunction(() => document.querySelectorAll('#qcm-hub .qcm-niv').length > 0,
                             null, { timeout: 30000 }).catch(() => {});
    const hub = async () => pg.evaluate(() => {
      const h = document.getElementById('qcm-hub');
      return {
        on: [...document.querySelectorAll('.page.on')].map((e) => e.id),
        niveaux: h.querySelectorAll('.qcm-niv').length,
        domaines: h.querySelectorAll('.qcm-dom').length,
        medailles: [...h.querySelectorAll('.qcm-niv .qcm-med')].map((m) => m.className.replace('qcm-med ', '')),
        anneau: (h.querySelector('.qcm-anneau-n') || {}).innerText || '',
        t: (h.innerText || '').replace(/\s+/g, ' '),
      };
    });
    const h0 = await hub();
    if (h0.on.join() !== 'p-qcm-ia' || h0.niveaux !== 4 || h0.domaines !== REF.domaines.length) {
      fautes.push('§2 : hub mal peint — page ' + h0.on.join() + ', ' + h0.niveaux
                  + ' niveau(x), ' + h0.domaines + ' domaine(s)');
    } else {
      dits.push('§2 — hub peint après connexion par lien profond : 4 niveaux, '
                + h0.domaines + ' domaines, anneau « ' + h0.anneau.replace(/\s+/g, ' ') + ' »');
    }

    /* ── §3 et §4. JOUER UN NIVEAU, AU CLAVIER ───────────────────────── */
    enJeu = true;
    const jouer = async (niveau, juste) => {
      await pg.evaluate((n) => qcmJouer(n), niveau);
      const n = REF.par_niveau[niveau];
      const positions = new Set();
      let motifs = 0, fiches = 0, verdicts = 0;
      for (let i = 0; i < n; i++) {
        await pg.waitForSelector('#qcm-jeu .qcm-opt:not([disabled])', { timeout: 10000 });
        const carte = await pg.evaluate(() => ({
          ordre: [...document.querySelectorAll('#qcm-jeu .qcm-opt')].map((b) => +b.getAttribute('data-qcm-o')),
          q: (document.querySelector('#qcm-jeu .qcm-q') || {}).textContent || '' }));
        const q = REF.questions.filter((x) => x.q === carte.q)[0];
        if (!q) { fautes.push('la question affichée n\'est pas dans la banque : « ' + carte.q.slice(0, 60) + ' »'); break; }
        const cible = juste ? q.a : (q.a + 1) % q.o.length;
        const pos = carte.ordre.indexOf(cible);
        if (juste) positions.add(pos);
        await pg.keyboard.press(['A', 'B', 'C', 'D'][pos]);
        await pg.waitForSelector('#qcm-fb .qcm-fb', { timeout: 5000 });
        const fb = await pg.evaluate(() => ({
          verdict: (document.querySelector('#qcm-fb .qcm-verdict') || {}).className || '',
          autres: document.querySelectorAll('#qcm-fb .qcm-autre').length,
          choix: document.querySelectorAll('#qcm-fb .qcm-autre-c').length,
          fiche: !!document.querySelector('#qcm-fb details.qcm-owasp'),
          pratique: document.querySelectorAll('#qcm-fb .qcm-prat li').length,
        }));
        if (/\bok\b/.test(fb.verdict) === juste) verdicts++;
        if (fb.autres === q.o.length - 1 && fb.pratique >= 3 && fb.choix === (juste ? 0 : 1)) motifs++;
        if (fb.fiche) fiches++;
        await pg.keyboard.press('Enter');
      }
      await pg.waitForSelector('#qcm-bilan:not([hidden]) .qcm-score-n', { timeout: 10000 });
      const bilan = await pg.evaluate(() => ({
        score: (document.querySelector('#qcm-bilan .qcm-score-n') || {}).textContent,
        med: (document.querySelector('#qcm-bilan .qcm-score .qcm-med') || {}).className || '',
        t: (document.getElementById('qcm-bilan').innerText || '').replace(/\s+/g, ' '),
        revue: document.querySelectorAll('#qcm-bilan .qcm-rev').length,
      }));
      return { n, positions, motifs, fiches, verdicts, bilan };
    };
    const haut = REF.medailles[0].cle;
    const j1 = await jouer('debutant', true);
    if (j1.verdicts !== j1.n || j1.motifs !== j1.n || j1.fiches !== j1.n) {
      fautes.push('§3 : correction incomplète — ' + j1.verdicts + ' verdicts justes, '
                  + j1.motifs + ' corrections complètes, ' + j1.fiches + ' fiches OWASP sur ' + j1.n);
    }
    if (j1.positions.size < 2) {
      fautes.push('§3 : la bonne réponse est toujours sous la même touche — le mélange ne mélange pas');
    }
    if (+j1.bilan.score !== j1.n || j1.bilan.med.indexOf(haut) < 0 || j1.bilan.revue !== j1.n) {
      fautes.push('§3 : bilan du sans-faute faux — score ' + j1.bilan.score + '/' + j1.n
                  + ', médaille « ' + j1.bilan.med + ' », revue ' + j1.bilan.revue);
    } else {
      dits.push('§3 — débutant au clavier, sans faute : ' + j1.n + '/' + j1.n + ', médaille « '
                + haut + ' », bonne réponse sous ' + j1.positions.size + ' touches différentes, '
                + 'chaque correction complète (motifs, pratique, fiche OWASP)');
    }
    const j2 = await jouer('medium', false);
    /* `innerText` REND LE TEXTE APRÈS `text-transform` : la phrase se
       cherche sans tenir compte de la casse (mesuré sur la recette des
       compétences, où l'oubli rendait §5 incapable de rien refuser). */
    const dit = new RegExp(REF.sans_medaille.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i');
    if (+j2.bilan.score !== 0 || j2.bilan.med.indexOf('aucune') < 0 || !dit.test(j2.bilan.t)
        || j2.motifs !== j2.n) {
      fautes.push('§4 : un passage à zéro est mal rendu — score ' + j2.bilan.score + ', « '
                  + j2.bilan.t.slice(0, 160) + ' », ' + j2.motifs + '/' + j2.n + ' corrections complètes');
    } else {
      dits.push('§4 — intermédiaire entièrement faux : 0/' + j2.n + ', « ' + REF.sans_medaille
                + ' », et « VOTRE CHOIX » marqué à chacune des ' + j2.n + ' corrections');
    }
    enJeu = false;

    /* ── §5. LA PROGRESSION SURVIT AU RECHARGEMENT ───────────────────── */
    await souffler(110);
    await pg.reload({ waitUntil: 'domcontentloaded' });
    await pg.waitForFunction(() => typeof go === 'function', null, { timeout: 90000 });
    await pg.waitForFunction(() => document.querySelectorAll('#qcm-hub .qcm-niv').length === 4,
                             null, { timeout: 30000 }).catch(() => {});
    const h1 = await hub();
    const attendu = Math.round(100 * j1.n / total) + '%';
    if (h1.medailles.indexOf(haut) < 0 || h1.anneau.indexOf(attendu) < 0) {
      fautes.push('§5 : après rechargement, médailles ' + JSON.stringify(h1.medailles)
                  + ', anneau « ' + h1.anneau + ' » (attendu ' + attendu + ')');
    } else {
      dits.push('§5 — page rechargée : la médaille du débutant et l\'anneau (' + attendu
                + ' de la banque) sont revenus du navigateur');
    }

    /* ── §6. RIEN N'EST PARTI ────────────────────────────────────────── */
    if (emises.length) {
      fautes.push('§6 : l\'écran a émis pendant le jeu : ' + emises.slice(0, 5).join(' | '));
    } else {
      dits.push('§6 — ' + (j1.n + j2.n) + ' réponses données : aucune n\'est partie vers le serveur '
                + '(seules ' + fond.length + ' lectures de fond de Sentinel ont eu lieu, sans rien du QCM)');
    }

    /* ── §7. L'ÉCRAN ANGLAIS ─────────────────────────────────────────── */
    await pg.evaluate(() => sentSetLang('en'));
    await pg.waitForFunction(() => /Beginner level/i.test(document.getElementById('qcm-hub').innerText || ''),
                             null, { timeout: 15000 }).catch(() => {});
    const en = await hub();
    if (en.niveaux !== 4) {
      fautes.push('§7 : à l\'écran anglais, le hub a disparu — « ' + en.t.slice(0, 80) + ' »');
    } else if (!/Beginner level/i.test(en.t) || !/Retake the level/i.test(en.t) || /NIVEAU D[ÉE]BUTANT/i.test(en.t)) {
      fautes.push('§7 : le hub reste en français à l\'écran anglais — « ' + en.t.slice(0, 160) + ' »');
    } else {
      await pg.evaluate(() => qcmJouer('expert'));
      await pg.waitForTimeout(1200);
      const q = await pg.evaluate(() => ({
        q: (document.querySelector('#qcm-jeu .qcm-q') || {}).textContent || '',
        compte: (document.querySelector('#qcm-jeu .qcm-compte') || {}).textContent || '' }));
      const resteFr = REF.questions.some((x) => x.q === q.q);
      if (resteFr || !/^Question\s+\d+ \/ \d+$/.test(q.compte.trim())) {
        fautes.push('§7 : la question expert reste en français — « ' + q.q.slice(0, 90) + ' » / « ' + q.compte + ' »');
      } else {
        dits.push('§7 — écran anglais : le hub survit et se lit en anglais, une question expert '
                  + 's\'affiche traduite (« ' + q.q.slice(0, 60) + '… »)');
      }
    }
    await pg.evaluate(() => sentSetLang('fr'));

    /* ── §8. LE COMPTE GRATUIT ───────────────────────────────────────── */
    await pg.evaluate(() => fetch('/api/sentinel-auth/logout', { method: 'POST' }));
    await pg.waitForTimeout(800);
    await souffler(8);
    await pg.goto(serveur.base + '/login?suite=%2Fsentinel%3Fgoto%3Dqcm-ia', { waitUntil: 'domcontentloaded' });
    await pg.fill('#login-email', COMPTE_GRATUIT);
    await pg.fill('#login-password', SECRET);
    await souffler(105);
    await Promise.all([
      pg.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 60000 }),
      pg.click('#login-btn'),
    ]);
    await pg.waitForFunction(() => typeof go === 'function', null, { timeout: 90000 });
    await pg.waitForTimeout(3000);
    const refus = await pg.evaluate(() => {
      const m = document.getElementById('sentinel-lock-modal');
      return { plan: window.__SENTINEL_PLAN || null,
               modale: m ? (m.innerText || '').replace(/\s+/g, ' ').trim() : null,
               on: [...document.querySelectorAll('.page.on')].map((e) => e.id) };
    });
    if (refus.plan !== 'gratuit' || refus.on.indexOf('p-qcm-ia') >= 0 || !refus.modale
        || !/QCM S[ée]curit[ée]/i.test(refus.modale)) {
      fautes.push('§8 : refus du plan Gratuit absent ou muet — ' + JSON.stringify(refus).slice(0, 200));
    } else {
      dits.push('§8 — plan Gratuit : refus explicite qui nomme l\'écran, « '
                + refus.modale.split('Souscrire')[0].trim().slice(0, 110) + ' »');
    }

    if (erreurs.length) fautes.push('erreurs JavaScript : ' + erreurs.join(' | '));
    if (refus429) fautes.push(refus429 + ' réponse(s) 429 : la recette a mesuré le limiteur, pas le produit');
  } catch (e) {
    fautes.push('la recette s\'est interrompue : ' + (e && e.message ? e.message : e));
  } finally {
    if (nav) { try { await nav.close(); } catch (e) { /* rien */ } }
    arreter(serveur, fautes.length > 0);
    if (pose) {
      try { compte('retirer', COMPTE); compte('retirer', COMPTE_GRATUIT); }
      catch (e) { fautes.push('le compte de recette n\'a pas pu être retiré : ' + e.message); }
    }
  }

  console.log('\n── CE QUI A ÉTÉ MESURÉ ──');
  dits.forEach((d) => console.log('  · ' + d));
  if (fautes.length) {
    console.log('\n── FAUTES (' + fautes.length + ') ──');
    fautes.forEach((f) => console.log('  ✗ ' + f));
    process.exit(1);
  }
  console.log('\n✓ QCM sécurité de l\'IA : tout ce qui est mesuré tient.');
})();
