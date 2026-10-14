/* RECETTE NAVIGATEUR — LE RÉFÉRENTIEL DE COMPÉTENCES IA, DU CHOIX À LA SORTIE.
 *
 * CE QU'ELLE MESURE, ET POURQUOI AUCUNE RÈGLE PYTHON NE LE FAIT. Les règles
 * de `tests/test_competences_ia.py` éprouvent le moteur et les routes : la
 * cible est un maximum rabattu, rien n'est proposé au-delà, chaque formation
 * citée existe au catalogue. Elles ne peuvent pas ouvrir un navigateur — or
 * les quatre listes déroulantes se remplissent en JavaScript APRÈS le
 * chargement, et la sortie est peinte par un second appel. Une liste vide,
 * un `onchange` qui n'appelle rien, ou une sortie qui reste sur
 * « Chargement… » ne se voient que là.
 *
 * ELLE MESURE AUSSI CE QUE LE MOTEUR SEUL NE PROUVE PAS : que le PLAFOND DE
 * RÔLE arrive jusqu'à l'écran. Un collaborateur de la direction des systèmes
 * d'information a, dans les tables, une fonction qui exige le niveau 5 sur
 * « protéger ». Si le rabattement se perdait entre le moteur et l'écran, la
 * page afficherait « Concevoir ou expertiser » à quelqu'un dont l'intitulé
 * dit « sans encadrement ». §5 regarde l'écran, pas la fonction.
 *
 * DEUX COMPTES RÉELS, ET ILS SONT RENDUS. Le module n'est pas dans
 * PLAN_GRATUIT_MODULES : il faut donc un compte Pro pour §2-§5, et un compte
 * Gratuit pour §6, qui mesure que le refus est explicite et nomme l'écran.
 * Les deux sont supprimés à la fin, quoi qu'il arrive.
 *
 * LE SOUFFLE. Le serveur borne une adresse à 120 requêtes par minute et un
 * chargement de /sentinel en coûte une centaine : la recette compte ce
 * qu'elle a consommé et attend d'avoir la place, sans quoi elle mesurerait
 * le limiteur.
 *
 *   node outils/recette_competences_ia.js
 */
'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn, execFileSync } = require('child_process');

const RACINE = path.dirname(__dirname);
const JETON = 'recette-competences-ia-000000';
const COMPTE = 'recette-competences@local.invalid';
const COMPTE_GRATUIT = 'recette-competences-gratuit@local.invalid';
const SECRET = 'Recette-Competences-2026!x';
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
  const journal = path.join(os.tmpdir(), 'recette_competences_' + port + '.log');
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

    /* ── §1. LES DEUX ROUTES, AVANT TOUT NAVIGATEUR ──────────────────────
       Si la table n'arrive pas, les quatre listes resteront vides et §3
       dirait « la liste des secteurs est vide » là où la faute est la
       route. On sépare donc les deux mesures. */
    const ref = await (await sonder(serveur.base + '/api/competences-ia/referentiel')).json();
    if (!ref || !ref.ok) {
      fautes.push('/api/competences-ia/referentiel ne rend pas de table');
    } else {
      const r = ref.referentiel;
      const n = [r.populations.length, r.fonctions.length, r.secteurs.length,
                 r.niveaux.length, r.familles.length];
      dits.push('table servie : ' + n[0] + ' populations, ' + n[1] + ' fonctions, '
                + n[2] + ' secteurs, ' + n[3] + ' niveaux, ' + n[4] + ' familles');
      if (n.some((x) => x < 2)) {
        fautes.push('une des cinq listes de la table est vide ou presque : ' + n.join('/'));
      }
    }

    nav = await chromium.launch();
    /* LA LANGUE EST FIXÉE : sans `locale`, Playwright annonce en-US, la page
       bascule en anglais, et la recette lirait le dictionnaire au lieu de
       l'écran. */
    const ctx = await nav.newContext({ viewport: { width: 1500, height: 1000 },
                                       locale: 'fr-FR',
                                       userAgent: NAVIGATEUR });
    /* LES TROIS SIGNAUX D'AUTOMATISATION, SPOOFÉS — mesuré ailleurs dans ce
       dépôt : sans eux le serveur bloque l'adresse 1 800 s et TOUTES les
       routes répondent 429. */
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

    /* ── §2. LE CHEMIN COMPLET : LIEN PROFOND → PORTE → FORMULAIRE → ÉCRAN ── */
    await souffler(6);
    await pg.goto(serveur.base + '/sentinel?goto=competences',
                  { waitUntil: 'domcontentloaded' });
    const ou = pg.url().replace(serveur.base, '');
    if (ou.indexOf('/login?suite=') !== 0 || ou.indexOf('competences') < 0) {
      fautes.push('la porte mène à ' + ou + ' : la destination ne survit pas');
    }
    await pg.fill('#login-email', COMPTE);
    await pg.fill('#login-password', SECRET);
    await souffler(105);
    await Promise.all([
      pg.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 60000 }),
      pg.click('#login-btn'),
    ]);
    const apres = pg.url().replace(serveur.base, '');
    if (apres !== '/sentinel?goto=competences') {
      const err = await pg.evaluate(() => {
        const e = document.getElementById('login-error');
        return e && e.style.display !== 'none' ? e.textContent : null; });
      throw new Error('après connexion le navigateur est sur ' + apres
                      + (err ? ' — la page dit : ' + err : ''));
    }
    await pg.waitForFunction(() => typeof go === 'function', null, { timeout: 90000 });
    await pg.waitForTimeout(3000);

    const ouvert = await pg.evaluate(() => {
      const on = [...document.querySelectorAll('.page.on')].map((e) => e.id);
      const p = document.getElementById('p-competences');
      const t = p ? (p.innerText || '').replace(/\s+/g, ' ').trim() : '';
      return { on, n: t.length, onglet: !!document.querySelector('.sb-item.on'),
               att: /Chargement|momentanément indisponible/.test(t) };
    });
    if (ouvert.on.length !== 1 || ouvert.on[0] !== 'p-competences') {
      fautes.push('l\'écran peint est ' + (ouvert.on.join(',') || 'AUCUN')
                  + ' au lieu de p-competences');
    } else if (ouvert.att) {
      fautes.push('p-competences est ouvert mais reste en attente');
    } else {
      dits.push('chemin complet : lien profond → porte → formulaire → écran peint, '
                + ouvert.n + ' caractères'
                + (ouvert.onglet ? ', onglet marqué' : ', MAIS AUCUN ONGLET MARQUÉ'));
      if (!ouvert.onglet) fautes.push('aucun onglet n\'est marqué courant');
    }

    /* ── §3. LES QUATRE LISTES DÉROULANTES, VRAIMENT REMPLIES ──────────── */
    const listes = await pg.evaluate(() => {
      const l = (id) => {
        const s = document.getElementById(id);
        return s ? { n: s.options.length, val: s.value,
                     premier: s.options.length ? s.options[0].textContent : '' }
                 : null;
      };
      return { population: l('comp-population'), fonction: l('comp-fonction'),
               secteur: l('comp-secteur'), niveau: l('comp-niveau') };
    });
    for (const k of ['population', 'fonction', 'secteur', 'niveau']) {
      const v = listes[k];
      if (!v) fautes.push('la liste déroulante « ' + k + ' » est absente de l\'écran');
      else if (v.n < 2) fautes.push('la liste « ' + k + ' » ne porte que ' + v.n + ' entrée(s)');
      else dits.push('liste « ' + k + ' » : ' + v.n + ' entrées, premier « '
                     + v.premier.slice(0, 48) + ' »');
    }

    /* ── §4. LA SORTIE : TRAJECTOIRE, SIX FAMILLES, ET UNE PROPOSITION ───
       On choisit une personne dont on SAIT ce qu'elle doit produire : un
       collaborateur du marketing dans la santé, parti de zéro. Le secteur Q
       élève « évaluer » et « protéger », l'écart est de trois paliers, et
       le catalogue a de quoi les combler. Une sortie vide ici ne serait pas
       un cas limite. */
    const choisir = async (pop, fon, sec, niv) => {
      await souffler(4);
      await pg.evaluate(([p, f, s, n]) => {
        const mettre = (id, v) => {
          const e = document.getElementById(id);
          e.value = v;
          e.dispatchEvent(new Event('change', { bubbles: true }));
        };
        mettre('comp-population', p); mettre('comp-fonction', f);
        mettre('comp-secteur', s); mettre('comp-niveau', n);
      }, [pop, fon, sec, niv]);
      await pg.waitForTimeout(1200);
      return pg.evaluate(() => {
        const e = document.getElementById('comp-sortie');
        const t = e ? (e.innerText || '').replace(/\s+/g, ' ').trim() : '';
        return {
          t, n: t.length,
          familles: e ? e.querySelectorAll('.comp-fam').length : 0,
          crans: e ? e.querySelectorAll('.comp-cran.comp-vise').length : 0,
          /* LE CHIFFRE SEUL : `textContent` collait le niveau à son
             étiquette (« 3Niveau visé · … »). Le premier nœud texte de la
             pastille EST le niveau. */
          niveaux: e ? [...e.querySelectorAll('.comp-niv')]
            .map((x) => (x.firstChild ? String(x.firstChild.textContent).trim() : '')) : [],
          trous: e ? e.querySelectorAll('.comp-trou').length : 0,
          reserves: e ? e.querySelectorAll('.comp-res').length : 0,
          lignes: e ? e.querySelectorAll('.comp-list > li').length : 0,
        };
      });
    };
    const s1 = await choisir('collaborateur', 'marketing', 'Q', '0');
    if (s1.familles !== 6) {
      fautes.push('la sortie montre ' + s1.familles + ' famille(s) au lieu de six');
    }
    if (s1.lignes < 1) {
      fautes.push('aucune formation n\'est proposée à un collaborateur parti de '
                  + 'zéro dans la santé : la sortie ne propose rien');
    }
    if (s1.reserves < 3) {
      fautes.push('la sortie ne porte que ' + s1.reserves + ' réserve(s) : le '
                  + 'niveau de départ est déclaré, et l\'écran doit le dire');
    }
    /* LA CASSE EST IGNORÉE, ET C'EST UNE MESURE QUI L'A IMPOSÉ : `innerText`
       rend le texte TEL QU'IL EST PEINT, donc passé par `text-transform:
       uppercase`. La première version de §4 cherchait « Départ déclaré » dans
       « DÉPART DÉCLARÉ » et ne le trouvait jamais ; pire, §5 cherchait
       « Piloter et transmettre » et ne pouvait donc rien refuser. */
    if (!/Départ déclaré/i.test(s1.t) || !/Niveau visé/i.test(s1.t)) {
      fautes.push('la trajectoire ne nomme pas ses deux bouts — départ et '
                  + 'niveau visé. La sortie commence par : « '
                  + s1.t.slice(0, 160) + ' »');
    } else {
      dits.push('collaborateur/marketing/Q, niveau 0 : départ ' + s1.niveaux[0]
                + ' → visé ' + s1.niveaux[1] + ', ' + s1.familles + ' familles, '
                + s1.lignes + ' ligne(s) de proposition, ' + s1.reserves + ' réserves');
    }

    /* ── §4 bis. LE SECTEUR CHANGE LA CIBLE, ET L'ÉCRAN LE MONTRE ────────
       Même personne, secteur neutre : la cible doit DESCENDRE. Si la sortie
       était identique, l'écran n'enverrait pas le secteur, ou le moteur ne
       le lirait pas — et les vingt-deux entrées de la liste seraient un
       décor. */
    const s2 = await choisir('collaborateur', 'marketing', 'A', '0');
    if (s2.t === s1.t) {
      fautes.push('la sortie est IDENTIQUE pour le secteur Q et le secteur A : '
                  + 'le secteur choisi ne change rien');
    } else {
      dits.push('secteur A au lieu de Q : la sortie change ('
                + s1.n + ' → ' + s2.n + ' caractères)');
    }

    /* ── §5. LE PLAFOND DE RÔLE ARRIVE JUSQU'À L'ÉCRAN ───────────────────
       La fonction « systèmes d'information » exige le niveau 5 sur
       « protéger ». Un collaborateur n'occupe aucun rôle : l'écran ne doit
       jamais montrer « Concevoir ou expertiser » comme niveau visé, et doit
       DIRE qu'il a rabattu. */
    const s3 = await choisir('collaborateur', 'si_data', 'K', '1');
    if (/Niveau visé · (Concevoir ou expertiser|Piloter et transmettre)/i.test(s3.t)) {
      fautes.push('un collaborateur est envoyé à un niveau de RÔLE : « ' +
                  (s3.t.match(/Niveau visé · [^0-9]{3,40}/) || [''])[0] + ' »');
    }
    if (!/rabattu/.test(s3.t)) {
      fautes.push('la sortie ne dit pas qu\'elle a rabattu l\'exigence de la '
                  + 'fonction : le rabattement est muet');
    } else {
      dits.push('collaborateur/si_data/K : visé ' + s3.niveaux[1]
                + ', et le rabattement est écrit');
    }

    /* ── §6. L'OFFRE QUI REFUSE, ET CE QU'ELLE DOIT DIRE ─────────────────
       Le module n'est pas dans PLAN_GRATUIT_MODULES. Un compte Gratuit doit
       donc être refusé — explicitement, en nommant l'écran. */
    await pg.evaluate(() => fetch('/api/sentinel-auth/logout', { method: 'POST' }));
    await pg.waitForTimeout(800);
    await souffler(8);
    await pg.goto(serveur.base + '/login?suite=%2Fsentinel%3Fgoto%3Dcompetences',
                  { waitUntil: 'domcontentloaded' });
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
      /* L'IDENTIFIANT RÉEL, LU DANS `sentinelLockPrompt` : la première
         version cherchait deux sélecteurs qui n'existent nulle part, et
         concluait que le refus était silencieux alors qu'il ne l'était pas. */
      const m = document.getElementById('sentinel-lock-modal');
      return {
        plan: window.__SENTINEL_PLAN || null,
        connu: window.__SENTINEL_PLAN_CONNU === true,
        modale: m ? (m.innerText || '').replace(/\s+/g, ' ').trim() : null,
        verrou: !!document.querySelector('.sb-item.sb-locked[onclick*="competences"]'),
        on: [...document.querySelectorAll('.page.on')].map((e) => e.id),
      };
    });
    if (refus.plan !== 'gratuit') {
      fautes.push('§6 voulait un compte au plan Gratuit, la page dit ' + refus.plan);
    }
    if (!refus.connu) {
      fautes.push('§6 : l\'offre du compte n\'est pas déclarée connue — le refus '
                  + 'dépendrait alors de l\'ordre d\'arrivée');
    }
    if (refus.on.indexOf('p-competences') >= 0) {
      fautes.push('§6 : le module s\'ouvre au plan Gratuit alors qu\'il n\'est '
                  + 'pas dans PLAN_GRATUIT_MODULES');
    } else if (!refus.modale) {
      fautes.push('§6 : le module est refusé EN SILENCE — aucune modale');
    } else if (!refus.verrou) {
      fautes.push('§6 : l\'onglet du module ne porte pas de cadenas');
    } else {
      dits.push('§6 — plan Gratuit : refus explicite, « '
                + refus.modale.split('Souscrire')[0].trim().slice(0, 120) + ' »');
    }

    if (erreurs.length) fautes.push('erreurs JavaScript : ' + erreurs.join(' | '));
    if (refus429) fautes.push(refus429 + ' réponse(s) 429 : la recette a mesuré '
                              + 'le limiteur, pas le produit');
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
  console.log('\n✓ Référentiel de compétences IA : tout ce qui est mesuré tient.');
})();
