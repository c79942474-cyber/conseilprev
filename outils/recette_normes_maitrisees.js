/* RECETTE NAVIGATEUR — LE CLIC SUR UNE DES SEIZE NORMES, JUSQU'À L'ÉCRAN.
 *
 * CE QU'ELLE MESURE, ET POURQUOI AUCUNE RÈGLE PYTHON NE LE FAIT.
 * `tests/test_normes_maitrisees.py` garde quatre maillons — la carte porte un
 * lien, la porte reporte la destination, la page de connexion n'accepte qu'un
 * chemin interne, l'onglet existe —, et son propre en-tête déclare ce qu'elle
 * ne peut pas faire : « Ouvrir un navigateur : /sentinel exige une
 * authentification, et la peinture du panneau se fait en JavaScript après
 * chargement. Elles vérifient que chaque maillon tient ; elles ne regardent
 * pas l'écran final. »
 *
 * C'est cet écran final que cette recette regarde. Elle clique pour de vrai,
 * se connecte pour de vrai par le formulaire, et lit le texte peint.
 *
 * ═══ CE QU'ELLE A TROUVÉ LA PREMIÈRE FOIS ════════════════════════════════
 * Le clic sur les seize cartes marche : les seize mènent à leur panneau, la
 * porte reporte, la connexion ramène, l'écran se peint. Le défaut était un
 * cran plus loin — sur les AUTRES chemins vers le même écran. Appelés par
 * `go(id)` seul, sans passer par l'onglet de la barre (c'est ce que font le
 * bouton « ↓ » du rail, son passage automatique, les boutons « → » d'un écran
 * à l'autre, le pont des règlements de données vers le RGPD, et le repli du
 * lien profond), TREIZE écrans sur dix-huit restaient sur « Chargement… »
 * sans fin — dont le hub RGPD, le registre des traitements, la vue d'ensemble
 * IA Act, les trois écrans NIST AI RMF, les deux OWASP, 800-53 et 800-82.
 * Quatre d'entre eux sont des blocs de SAISIE d'un parcours : un
 * questionnaire qui ne se peint pas ne peut pas être rempli, donc le rail ne
 * peut pas verdir, donc le taux de la norme ne peut pas monter.
 *
 * §5 NE S'ARRÊTE PAS À CES DIX-HUIT. Les dix-huit étaient les écrans dont
 * `go()` ne connaissait pas l'amorce ; la correction, elle, passe par un
 * mécanisme qui vaut pour TOUT écran ayant un onglet. §5 lit donc la barre et
 * éprouve chaque entrée qui porte une amorce — il y en a beaucoup plus que
 * dix-huit, et c'est le mécanisme qu'on mesure, pas la liste d'hier.
 *
 * ═══ ET CE QU'ELLE A TROUVÉ ENSUITE, QUI ÉTAIT LA VRAIE RÉPONSE ═════════
 * Avec un compte réel au plan GRATUIT, après une connexion par le
 * formulaire, sur `/sentinel?goto=rgpd-hub` : l'écran peint était
 * l'Observatoire, 106 des 111 onglets portaient un cadenas, et une modale
 * disait « Module verrouillé ». La chaîne du clic tenait ; c'est l'offre du
 * compte qui refusait le module. Et le refus n'était pas stable :
 * `planIsAllowed` autorise tant que l'offre n'est pas connue, le plan est
 * demandé à 300 ms et le lien profond partait à 350 ms — le même clic, sur
 * la même norme, par le même compte, ouvrait le module ou le refusait selon
 * lequel des deux arrivait d'abord. §6 mesure ce refus : qu'il nomme l'écran
 * demandé, qu'il garde la demande, et qu'il soit TOUJOURS le même.
 *
 * ═══ DEUX COMPTES RÉELS, ET ILS SONT RENDUS ═════════════════════════════
 * §3 se connecte par le formulaire : il faut donc un compte. La recette en
 * crée deux dans la base SQLite locale (`registre_ia.db`, hors du dépôt) —
 * un Pro pour §1-§5, un Gratuit pour §6 — et les SUPPRIME à la fin, quoi
 * qu'il arrive. Sans cela, §3 mesurerait le lien maître `/auth/<jeton>` —
 * qui ne passe ni par le formulaire, ni par `__authDest()`, ni par la porte
 * des offres, c'est-à-dire pas par les maillons qu'on veut mesurer.
 *
 * ═══ POURQUOI §4 NE RECHARGE PAS SEIZE FOIS ═════════════════════════════
 * Mesuré : le serveur borne une adresse à 120 requêtes par minute, toutes
 * routes confondues, et un chargement de /sentinel en consomme une trentaine
 * (page, scripts, référentiels). Au TROISIÈME rechargement, toutes les routes
 * répondent 429 et les panneaux retombent sur « momentanément indisponible » :
 * la recette mesurerait le limiteur, pas le produit. §4 charge donc la page
 * UNE fois et rejoue, pour chaque norme, la fonction que le navigateur
 * exécute au chargement — `sentinelGotoDeepLink()`, après avoir posé l'URL
 * réelle. §2 et §3 font, eux, le chemin complet pour deux normes : une
 * ancienne et une récente. C'est le témoin qui interdit à §4 de mentir.
 *
 *   node outils/recette_normes_maitrisees.js
 */
'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn, execFileSync } = require('child_process');

const RACINE = path.dirname(__dirname);
const JETON = 'recette-normes-maitrisees-0000';
const COMPTE = 'recette-normes@local.invalid';
const SECRET = 'Recette-Normes-2026!x';
/* DEUX COMPTES, PARCE QU'IL Y A DEUX CHOSES À MESURER, et qu'un seul compte
   ne peut pas les mesurer toutes les deux. L'offre du compte décide si un
   module s'ouvre : avec le plan Gratuit, les seize normes sont verrouillées
   et §3 mesurerait la porte des offres au lieu de la chaîne du clic. §1 à §5
   travaillent donc sur un compte Pro ; §6 crée un compte Gratuit, exprès,
   pour mesurer que le refus est explicite et qu'il est TOUJOURS le même. */
const COMPTE_GRATUIT = 'recette-normes-gratuit@local.invalid';
const NAVIGATEUR = 'Mozilla/5.0 (X11; Linux x86_64) Firefox/130.0';

/* LES SEIZE DESTINATIONS NE SONT PAS ÉCRITES ICI : elles sont LUES sur la
   page d'accueil, au §1. Une liste écrite dans la recette serait une
   dix-septième chose à tenir à jour — et elle dirait « seize » même le jour
   où la grille en montrerait quinze. */

/* LES DIX-HUIT ÉCRANS dont l'amorce est écrite dans le `onclick` de leur
   onglet. Ceux-là SONT lus dans sentinel.html, pour la même raison. */
function amorcesDeLaBarre() {
  const html = fs.readFileSync(path.join(RACINE, 'sentinel.html'), 'utf8');
  const out = [];
  const re = /class="sb-item[^"]*"[^>]*onclick="([^"]+)"/g;
  let m;
  while ((m = re.exec(html)) !== null) {
    const oc = m[1];
    const id = /^go\('([^']+)'/.exec(oc);
    if (!id) continue;
    const noms = (oc.match(/[A-Za-z_][A-Za-z0-9_]*(?=\s*\(\s*\))/g) || [])
      .filter((n) => n !== 'go');
    if (noms.length) out.push(id[1]);
  }
  return out;
}

function portLibre() {
  const net = require('net');
  const essayer = (p) => new Promise((r) => {
    const s = net.createServer();
    s.once('error', () => r(false));
    s.listen(p, '127.0.0.1', () => s.close(() => r(true)));
  });
  return (async () => {
    for (let p = 9912; p <= 9940; p++) if (await essayer(p)) return p;
    throw new Error('aucun port libre entre 9912 et 9940');
  })();
}

function porteLePort(pid, port) {
  try {
    const env = fs.readFileSync('/proc/' + pid + '/environ', 'latin1');
    return env.split('\0').indexOf('PORT=' + port) >= 0;
  } catch (e) { return false; }
}

/* LE COMPTE DE RECETTE — POSÉ ET RETIRÉ PAR LA MÊME PAIRE DE FONCTIONS, pour
   qu'on ne puisse pas poser sans savoir retirer. Le mot de passe est haché
   par le même `generate_password_hash` que l'inscription : un hachage écrit à
   la main ne serait pas reconnu par la route de connexion. */
function compte(action, email, plan) {
  const py = [
    'import sqlite3, datetime, sys',
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
  const journal = path.join(os.tmpdir(), 'recette_normes_' + port + '.log');
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
    nav = await chromium.launch();
    /* LA LANGUE EST FIXÉE, ET C'EST UNE MESURE QUI L'A IMPOSÉ. Sans
       `locale`, Playwright annonce en-US : la page a basculé en anglais et la
       recette a lu « 16 standards mastered » là où elle cherchait des normes.
       Elle mesurait alors le dictionnaire, pas la grille. */
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

    /* ═══ LE SOUFFLE, ET C'EST LA MESURE QUI L'A DICTÉ ═══════════════════
       Le serveur borne une adresse à 120 requêtes par minute, toutes routes
       confondues. Mesuré : un chargement de l'accueil coûte 12 réponses, la
       page de connexion 3, et un chargement de /sentinel CENT UNE — page,
       scripts, référentiels, parcours. Deux chargements de Sentinel dans la
       même minute dépassent donc le plafond à eux seuls, et la recette
       mesurait alors le limiteur : cinquante-six réponses 429, des écrans
       vides partout, et seize fautes qui n'étaient pas dans le produit.

       Plutôt que d'espacer à l'aveugle, la recette COMPTE ce qu'elle a
       consommé dans la dernière minute et attend d'avoir la place. Elle
       prend donc le temps qu'il faut — plusieurs minutes — et ce temps est
       le prix d'une mesure qui porte sur le produit. */
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

    /* ── §1. L'ACCUEIL, VRAIMENT PEINT ──────────────────────────────────── */
    await souffler(14);
    await pg.goto(serveur.base + '/', { waitUntil: 'domcontentloaded' });
    await pg.waitForSelector('.ng .nc-go', { timeout: 30000 });
    const grille = await pg.evaluate(() => {
      const t = document.querySelector('[data-i18n="nr.ttl"]');
      /* LE NOMBRE, PAS LA LANGUE : la recette fixe le français, mais si la
         page basculait elle doit dire « le titre et la grille se
         contredisent », pas « le titre n'annonce rien ». */
      const n = /(\d+)\s+(?:normes|standards)/.exec((t && t.textContent) || '');
      return {
        annonce: n ? parseInt(n[1], 10) : null,
        cartes: [...document.querySelectorAll('.ng .nc')].map((c) => {
          const a = c.querySelector('a.nc-go');
          const nom = c.querySelector('.nn');
          return { nom: nom ? nom.textContent.trim() : null,
                   href: a ? a.getAttribute('href') : null,
                   /* LA SURFACE CLIQUABLE, MESURÉE : une carte dont le lien
                      ne couvre rien se lit comme un lien mort. */
                   h: a ? Math.round(a.getBoundingClientRect().height) : 0 };
        }),
      };
    });
    /* ── §1 bis. L'OFFRE EST ANNONCÉE, ET ELLE EST VISIBLE ───────────────
       UNE PASTILLE PRÉSENTE DANS LE HTML N'EST PAS UNE PASTILLE LUE. Celle-ci
       vit dans le lien de la carte, sous la description, dans une grille qui
       grossit au survol : une règle Python la trouve dans le fichier, elle ne
       sait pas si elle a une hauteur. On la mesure donc peinte, puis dans les
       deux autres langues — un libellé qui ne bouge pas à la bascule est un
       libellé resté français. */
    const politique = (() => {
      const js = fs.readFileSync(path.join(RACINE, 'sentinel.page.js'), 'utf8');
      const lire = (nom) => {
        const m = new RegExp('var ' + nom + ' = \\[([^\\]]*)\\]').exec(js);
        return m ? m[1].split(',').map((x) => x.trim().replace(/^'|'$/g, ''))
                        .filter(Boolean) : null;
      };
      return { gratuit: lire('PLAN_GRATUIT_MODULES'),
               entreprise: lire('PLAN_ENTREPRISE_ONLY') };
    })();
    if (!politique.gratuit || !politique.entreprise) {
      fautes.push('la politique des offres ne se lit plus dans sentinel.page.js : '
                  + '§1 bis ne mesure plus rien');
    }
    const pastilles = await pg.evaluate(() => [...document.querySelectorAll('.ng .nc')]
      .map((c) => {
        const a = c.querySelector('a.nc-go');
        const p = c.querySelector('.nc-offre');
        const n = c.querySelector('.nn');
        return { nom: n ? n.textContent.trim() : null,
                 id: a ? (a.getAttribute('href') || '').split('goto=')[1] : null,
                 offre: p ? p.getAttribute('data-offre') : null,
                 h: p ? Math.round(p.getBoundingClientRect().height) : 0,
                 texte: p ? (p.innerText || '').replace(/\s+/g, ' ').trim() : null,
                 dedans: !!(p && a && a.contains(p)) };
      }));
    let annoncees = 0;
    pastilles.forEach((x) => {
      const attendue = politique.gratuit && politique.gratuit.indexOf(x.id) >= 0
        ? null
        : (politique.entreprise && politique.entreprise.indexOf(x.id) >= 0
           ? 'entreprise' : 'pro');
      if (attendue === null) {
        if (x.offre) fautes.push('« ' + x.nom + ' » annonce l\'offre ' + x.offre
                                 + ' alors que ' + x.id + ' est ouvert à tous');
        return;
      }
      if (!x.offre) {
        fautes.push('« ' + x.nom + ' » n\'annonce aucune offre alors que la porte '
                    + 'exige ' + attendue + ' : le clic finira sur « Module verrouillé »');
        return;
      }
      if (x.offre !== attendue) {
        fautes.push('« ' + x.nom + ' » annonce ' + x.offre + ', la porte exige ' + attendue);
      }
      if (x.h < 8) {
        fautes.push('la pastille d\'offre de « ' + x.nom + ' » ne fait que ' + x.h
                    + ' px de haut : elle est dans le HTML, pas sur l\'écran');
      }
      if (!x.dedans) {
        fautes.push('la pastille d\'offre de « ' + x.nom + ' » est hors du lien');
      }
      if (!x.texte) {
        fautes.push('la pastille d\'offre de « ' + x.nom + ' » ne dit rien');
      }
      annoncees++;
    });
    if (annoncees) {
      dits.push(annoncees + ' carte(s) annoncent l\'offre exigée, visible et dans le lien — '
                + 'la plus basse à ' + Math.min.apply(null, pastilles.filter((x) => x.h)
                  .map((x) => x.h)) + ' px, « ' + (pastilles.find((x) => x.texte) || {}).texte + ' »');
    }
    /* LES DEUX AUTRES LANGUES : le libellé doit CHANGER. */
    const fr0 = (pastilles.find((x) => x.texte) || {}).texte;
    for (const lg of ['en', 'de']) {
      const vu = await pg.evaluate((l) => {
        if (typeof setLang !== 'function') return null;
        setLang(l);
        const p = document.querySelector('.ng .nc-offre');
        return p ? (p.innerText || '').replace(/\s+/g, ' ').trim() : null;
      }, lg);
      if (vu === null) {
        fautes.push('la bascule de langue de l\'accueil est introuvable : §1 bis '
                    + 'ne peut pas mesurer la traduction de la pastille');
      } else if (vu === fr0) {
        fautes.push('en ' + lg + ', la pastille d\'offre dit encore « ' + vu
                    + ' » : le libellé n\'est pas traduit');
      } else {
        dits.push('la pastille d\'offre en ' + lg + ' : « ' + vu + ' »');
      }
    }
    await pg.evaluate(() => { if (typeof setLang === 'function') setLang('fr'); });

    const cibles = [];
    grille.cartes.forEach((c) => {
      const m = c.href && /^\/sentinel\?goto=(.+)$/.exec(c.href);
      if (!m) { fautes.push('la carte « ' + c.nom + ' » ne mène à aucun module : ' + c.href); return; }
      if (c.h < 40) fautes.push('le lien de « ' + c.nom + ' » ne couvre que ' + c.h + ' px de hauteur');
      cibles.push({ nom: c.nom, id: m[1] });
    });
    if (grille.annonce !== grille.cartes.length) {
      fautes.push('le titre annonce ' + grille.annonce + ' normes, la grille en peint '
                  + grille.cartes.length);
    } else {
      dits.push(grille.cartes.length + ' cartes peintes, et le titre annonce le même nombre');
    }
    if (cibles.length < 5) throw new Error('la grille ne se lit pas : ' + cibles.length + ' cible(s)');

    /* ── §2+§3. LE CHEMIN COMPLET, POUR UNE NORME ANCIENNE ET UNE RÉCENTE ─
       CLIC RÉEL → PORTE → FORMULAIRE DE CONNEXION → ÉCRAN PEINT.
       Deux suffisent, et deux sont nécessaires : une seule ne dirait pas si
       le chemin vaut pour les normes ajoutées après lui. */
    const temoins = ['rgpd-hub', 'data-act-qualifier']
      .filter((id) => cibles.some((c) => c.id === id));
    if (temoins.length !== 2) {
      fautes.push('les deux normes témoins de §3 ne sont plus dans la grille : '
                  + temoins.join(', '));
    }
    for (const id of temoins) {
      await souffler(18);
      await pg.goto(serveur.base + '/', { waitUntil: 'domcontentloaded' });
      await pg.waitForSelector('.ng .nc-go', { timeout: 30000 });
      await Promise.all([
        pg.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 30000 }),
        pg.click('.ng a.nc-go[href="/sentinel?goto=' + id + '"]'),
      ]);
      const ou = pg.url().replace(serveur.base, '');
      if (ou.indexOf('/login?suite=') !== 0 || ou.indexOf(id) < 0) {
        fautes.push('le clic sur « ' + id + ' » mène à ' + ou
                    + ' : la destination demandée ne survit pas à la porte');
        continue;
      }
      const dest = await pg.evaluate(
        () => (typeof __authDest === 'function' ? __authDest() : null));
      if (dest !== '/sentinel?goto=' + id) {
        fautes.push('la page de connexion rendrait ' + dest + ' au lieu de /sentinel?goto=' + id);
        continue;
      }
      /* LA CONNEXION, PAR LE FORMULAIRE — pas par une route de service. */
      await pg.fill('#login-email', COMPTE);
      await pg.fill('#login-password', SECRET);
      await souffler(105);          /* le chargement de Sentinel qui suit */
      await Promise.all([
        pg.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 60000 }),
        pg.click('#login-btn'),
      ]);
      const apres = pg.url().replace(serveur.base, '');
      if (apres !== '/sentinel?goto=' + id) {
        const err = await pg.evaluate(() => {
          const e = document.getElementById('login-error');
          return e && e.style.display !== 'none' ? e.textContent : null; });
        fautes.push('après connexion le navigateur est sur ' + apres
                    + ' au lieu de /sentinel?goto=' + id
                    + (err ? ' — la page dit : ' + err : ''));
        continue;
      }
      await pg.waitForFunction(() => typeof go === 'function', null, { timeout: 90000 });
      await pg.waitForTimeout(2600);
      const vu = await pg.evaluate((i) => {
        const on = [...document.querySelectorAll('.page.on')].map((e) => e.id);
        const p = document.getElementById('p-' + i);
        const t = p ? (p.innerText || '').replace(/\s+/g, ' ').trim() : '';
        return { on, n: t.length, titre: document.title,
                 onglet: !!document.querySelector('.sb-item.on'),
                 att: /Chargement|momentanément indisponible/.test(t) };
      }, id);
      if (vu.on.length !== 1 || vu.on[0] !== 'p-' + id) {
        fautes.push('connecté sur ' + id + ', l\'écran peint est ' + (vu.on.join(',') || 'AUCUN'));
      } else if (vu.att || vu.n < 300) {
        fautes.push(id + ' est bien l\'écran ouvert mais il ne montre que ' + vu.n
                    + ' caractères' + (vu.att ? ' et reste en attente' : ''));
      } else {
        dits.push('chemin complet pour ' + id + ' : clic → porte → formulaire → « '
                  + vu.titre + ' », ' + vu.n + ' caractères'
                  + (vu.onglet ? ', onglet marqué' : ', MAIS AUCUN ONGLET MARQUÉ'));
        if (!vu.onglet) fautes.push(id + ' : aucun onglet n\'est marqué courant');
      }
      /* ON REPART ANONYME POUR LE TÉMOIN SUIVANT : sans cela le second clic
         ne traverserait plus la porte, et §2 ne mesurerait plus rien. Mais
         PAS après le dernier : sa page, déjà chargée et déjà connectée, est
         celle sur laquelle §4 et §5 travaillent. Un chargement de Sentinel
         coûte cent une requêtes ; en reprendre un ici obligerait la recette
         à attendre une minute de plus pour rien. */
      if (id !== temoins[temoins.length - 1]) {
        await pg.evaluate(() => fetch('/api/sentinel-auth/logout', { method: 'POST' }));
        await pg.waitForTimeout(800);
      }
    }

    /* ── §4. LES SEIZE ÉCRANS FINAUX, SUR UNE SEULE PAGE ─────────────────── */
    const dejaDedans = await pg.evaluate(() => typeof go === 'function'
      && typeof window.sentinelGotoDeepLink === 'function');
    if (!dejaDedans) {
      /* LE REPLI, quand §3 n'a pas abouti : le lien maître ouvre Sentinel
         sans passer par le formulaire. Il ne remplace pas §3 — il permet à
         §4 et §5 de mesurer quand même. */
      await souffler(105);
      await pg.goto(serveur.base + '/auth/' + JETON, { waitUntil: 'domcontentloaded' });
      await pg.waitForFunction(
        () => typeof go === 'function' && typeof window.sentinelGotoDeepLink === 'function',
        null, { timeout: 90000 });
      dits.push('§4 et §5 ont rouvert Sentinel par le lien maître');
    } else {
      dits.push('§4 et §5 travaillent sur la page ouverte par la connexion de §3');
    }
    let muets4 = 0, court = Infinity;
    for (const c of cibles) {
      await souffler(6);
      await pg.evaluate((i) => {
        history.replaceState({}, '', '/sentinel?goto=' + i);
        document.querySelectorAll('.page.on').forEach((e) => e.classList.remove('on'));
        window.sentinelGotoDeepLink();
      }, c.id);
      await pg.waitForTimeout(2300);
      const m = await pg.evaluate((i) => {
        const on = [...document.querySelectorAll('.page.on')].map((e) => e.id);
        const p = document.getElementById('p-' + i);
        const t = p ? (p.innerText || '').replace(/\s+/g, ' ').trim() : '';
        return { on, n: t.length, att: /Chargement|momentanément indisponible/.test(t),
                 titre: document.title };
      }, c.id);
      court = Math.min(court, m.n);
      if (m.on.length !== 1 || m.on[0] !== 'p-' + c.id) {
        muets4++;
        fautes.push('?goto=' + c.id + ' peint ' + (m.on.join(',') || 'AUCUN écran'));
      } else if (m.att || m.n < 300) {
        muets4++;
        fautes.push('?goto=' + c.id + ' ouvre le bon écran mais il ne montre que '
                    + m.n + ' caractères' + (m.att ? ' et reste en attente' : ''));
      }
    }
    if (!muets4) {
      dits.push('les ' + cibles.length + ' normes s\'ouvrent sur LEUR écran par ?goto=, '
                + 'le plus maigre à ' + court + ' caractères');
    }

    /* ── §5. L'AMORCE PAR go() SEUL — LE DÉFAUT MESURÉ ICI LA PREMIÈRE FOIS ─ */
    const amorces = amorcesDeLaBarre();
    if (amorces.length < 10) {
      fautes.push('la lecture des amorces de la barre ne rend que ' + amorces.length
                  + ' écran(s) : §5 ne mesure plus rien');
    }
    let muets5 = 0;
    for (const id of amorces) {
      await souffler(6);
      const m = await pg.evaluate((i) => {
        document.querySelectorAll('.page.on').forEach((e) => e.classList.remove('on'));
        go(i);                     /* SANS élément : c'est ce que fait le rail */
        return new Promise((r) => setTimeout(() => {
          const p = document.getElementById('p-' + i);
          const t = p ? (p.innerText || '').replace(/\s+/g, ' ').trim() : '';
          r({ n: t.length, att: /Chargement|momentanément indisponible/.test(t) });
        }, 2300));
      }, id);
      if (m.att || m.n < 300) {
        muets5++;
        fautes.push('go(\'' + id + '\') sans onglet laisse l\'écran à ' + m.n
                    + ' caractères' + (m.att ? ' et en attente' : '')
                    + ' : le rail, les boutons « → » et le pont RGPD y mènent');
      }
    }
    if (!muets5) {
      dits.push('les ' + amorces.length + ' écrans dont l\'amorce est écrite dans leur '
                + 'onglet s\'amorcent AUSSI par go() seul');
    }

    /* ── §6. L'OFFRE QUI REFUSE, ET CE QU'ELLE DOIT DIRE ─────────────────
       CE QUE §3 NE POUVAIT PAS VOIR, parce qu'il travaille sur un compte Pro.
       Avec le plan Gratuit, les seize normes sont verrouillées : la chaîne du
       clic tient de bout en bout et l'écran demandé ne s'affiche pas. Ce
       n'est pas un défaut en soi — c'est le modèle commercial. Les défauts
       sont ailleurs, et ils sont trois, tous mesurés ici :
         1. le refus doit NOMMER ce qu'on a demandé (il disait « ce module ») ;
         2. la demande ne doit pas être perdue — l'URL garde `?goto=` pour que
            la souscription y ramène ;
         3. le refus doit être TOUJOURS LE MÊME. `planIsAllowed` autorise
            quand le plan n'est pas encore connu, et le lien profond partait
            avant la réponse : le même clic ouvrait le module ou le refusait
            selon un délai réseau. On rejoue donc le lien plusieurs fois, et
            on exige le même verdict. */
    const idG = (cibles.find((c) => c.id === 'rgpd-hub') || cibles[0]).id;
    /* ON QUITTE LE COMPTE PRO. Sans cela le clic ne passerait plus par la
       page de connexion — la session de §3 est encore ouverte — et §6
       mesurerait le compte Pro en croyant mesurer le Gratuit. */
    await pg.evaluate(() => fetch('/api/sentinel-auth/logout', { method: 'POST' }));
    await pg.waitForTimeout(800);
    await souffler(18);
    await pg.goto(serveur.base + '/', { waitUntil: 'domcontentloaded' });
    await pg.waitForSelector('.ng .nc-go', { timeout: 30000 });
    await Promise.all([
      pg.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 30000 }),
      pg.click('.ng a.nc-go[href="/sentinel?goto=' + idG + '"]'),
    ]);
    await pg.fill('#login-email', COMPTE_GRATUIT);
    await pg.fill('#login-password', SECRET);
    await souffler(105);
    await Promise.all([
      pg.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 60000 }),
      pg.click('#login-btn'),
    ]);
    await pg.waitForFunction(() => typeof go === 'function', null, { timeout: 90000 });
    await pg.waitForTimeout(4000);
    const refus = await pg.evaluate(() => {
      const m = document.getElementById('sentinel-lock-modal');
      const b = document.getElementById('sentinel-plan-banner');
      return {
        url: location.pathname + location.search,
        plan: window.__SENTINEL_PLAN,
        connu: window.__SENTINEL_PLAN_CONNU === true,
        ecran: [...document.querySelectorAll('.page.on')].map((e) => e.id),
        modale: m ? (m.innerText || '').replace(/\s+/g, ' ').trim() : null,
        bandeau: b ? (b.innerText || '').replace(/\s+/g, ' ').trim() : null,
      };
    });
    if (refus.plan !== 'gratuit') {
      fautes.push('§6 voulait un compte au plan Gratuit, la page dit ' + refus.plan);
    } else if (!refus.connu) {
      fautes.push('§6 : l\'offre du compte n\'est pas déclarée connue — la porte '
                  + 'des offres autoriserait tout le temps de la course');
    } else if (!refus.modale) {
      fautes.push('§6 : le module est refusé en silence — aucune modale, et '
                  + 'l\'écran est ' + (refus.ecran.join(',') || 'AUCUN'));
    } else {
      /* LE REFUS NOMME CE QU'ON A DEMANDÉ — c'est la seule chose qui
         distingue « votre offre ne couvre pas cet écran » d'un lien cassé. */
      const meta = await pg.evaluate((i) => {
        const m = (typeof PAGE_META === 'object') ? PAGE_META[i] : null;
        return m ? (m.label || '') : ''; }, idG);
      if (meta && refus.modale.indexOf(meta) < 0) {
        fautes.push('§6 : la modale ne nomme pas l\'écran demandé (« ' + meta
                    + ' ») : ' + refus.modale.slice(0, 120));
      }
      if (refus.url.indexOf('goto=' + idG) < 0) {
        fautes.push('§6 : la demande est perdue — l\'URL est ' + refus.url
                    + ', la souscription ne saura pas où ramener le lecteur');
      }
      /* LE BANDEAU COMPTE CE QUI EST DÉCLARÉ, et pas un nombre écrit. */
      const js = fs.readFileSync(path.join(RACINE, 'sentinel.page.js'), 'utf8');
      const dec = /var PLAN_GRATUIT_MODULES = \[([^\]]*)\]/.exec(js);
      const combien = dec ? dec[1].split(',').filter((x) => x.trim()).length : null;
      if (combien === null) {
        fautes.push('§6 : la liste des modules du plan Gratuit ne se lit plus');
      } else if (refus.bandeau && refus.bandeau.indexOf(String(combien)) < 0) {
        fautes.push('§6 : le bandeau annonce « ' + refus.bandeau
                    + ' » alors que la liste en déclare ' + combien);
      }
      dits.push('§6 — plan Gratuit : « ' + refus.modale.split('Souscrire')[0].trim()
                + ' », écran ' + (refus.ecran.join(',') || 'AUCUN')
                + ', demande gardée dans ' + refus.url);
    }
    /* LA DÉTERMINATION : trois fois le même lien profond, trois fois le même
       verdict. Un seul écart et le refus dépend d'une course. */
    const verdicts = [];
    for (let i = 0; i < 3; i++) {
      await souffler(6);
      verdicts.push(await pg.evaluate((id) => {
        const m = document.getElementById('sentinel-lock-modal');
        if (m && m.parentNode) m.parentNode.removeChild(m);
        document.querySelectorAll('.page.on').forEach((e) => e.classList.remove('on'));
        history.replaceState({}, '', '/sentinel?goto=' + id);
        window.sentinelGotoDeepLink();
        return new Promise((r) => setTimeout(() => {
          r(([...document.querySelectorAll('.page.on')].map((e) => e.id).join(',') || 'AUCUN')
            + (document.getElementById('sentinel-lock-modal') ? '+modale' : ''));
        }, 2600));
      }, idG));
    }
    if (new Set(verdicts).size !== 1) {
      fautes.push('§6 : le même lien profond rend des verdicts différents — '
                  + verdicts.join(' / ') + ' : la porte des offres dépend d\'une course');
    } else {
      dits.push('§6 — le même lien profond rend trois fois le même verdict : ' + verdicts[0]);
    }

    if (refus429) fautes.push(refus429 + ' réponse(s) 429 : le limiteur a mordu, '
                              + 'la mesure n\'est pas celle du produit');
    else dits.push('aucune réponse 429 — la mesure porte sur le produit');
    if (erreurs.length) fautes.push('erreur(s) de page : ' + erreurs.slice(0, 4).join(' | '));

    console.log('\n  MESURÉ');
    dits.forEach((d) => console.log('   · ' + d));
    if (fautes.length) {
      console.log('\n  FAUTES (' + fautes.length + ')');
      fautes.forEach((f) => console.log('   ! ' + f));
    }
  } catch (e) {
    fautes.push('la recette s\'est arrêtée : ' + e.message);
    console.log('\n  ARRÊT : ' + e.message);
  } finally {
    if (nav) { try { await nav.close(); } catch (e) { /* déjà fermé */ } }
    arreter(serveur, fautes.length > 0);
    /* LE COMPTE EST RENDU, MÊME SI LA RECETTE TOMBE. */
    if (pose) {
      try { compte('retirer', COMPTE); compte('retirer', COMPTE_GRATUIT); }
      catch (e) { console.log('  !! un compte de recette n\'a pas pu être retiré : '
                              + e.message); }
    }
  }
  console.log(fautes.length ? '\n  ÉCHEC' : '\n  OK');
  process.exit(fautes.length ? 1 : 0);
})();
