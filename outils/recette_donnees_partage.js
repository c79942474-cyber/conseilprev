/* RECETTE NAVIGATEUR — LES SEPT ÉCRANS DE « DONNÉES & PARTAGE » (DGA, Data Act).
 *
 * CE QU'ELLE MESURE, ET POURQUOI AUCUNE RÈGLE PYTHON NE LE FAIT. Les sept
 * écrans sont PEINTS par `dpPeindre` depuis les deux routes de référentiel :
 * le HTML ne porte qu'un « Chargement… ». Une règle qui lit le fichier voit
 * donc le gabarit, jamais l'écran.
 *
 * TROIS DÉFAUTS DE CE DÉPÔT ONT ÉTÉ MESURÉS AINSI, ET PAS AUTREMENT :
 *   1. `go()` n'amorçait PAS `dpInit`. Aucun chemin ne peignait les sept
 *      panneaux — ni l'onglet, ni `?goto=`, ni les huit étapes du parcours :
 *      les quinze conditions de l'article 12 et les trente-trois obligations
 *      du Data Act n'étaient affichées nulle part.
 *   2. LE LIMITEUR ET LA DÉTECTION ANTI-SCRAPING. Un navigateur qui ne
 *      déclare pas ses greffons est signalé à /api/client-signal, le serveur
 *      BLOQUE l'adresse 1 800 s, et le blocage ferme TOUTES les routes : les
 *      panneaux retombent sur « Le référentiel est momentanément
 *      indisponible ». C'est pour cela que cette recette spoofe les TROIS
 *      signaux et vérifie qu'aucune réponse 429 n'est arrivée.
 *   3. « aucune » EST EXCLUSIVE, et c'est une règle de produit : déclarer
 *      « aucune de ces qualités » doit vider les autres, parce que le
 *      règlement ne vous saisit alors pas. Un cumul laisserait un taux sur un
 *      chantier qui n'existe pas.
 *
 * LE JOUR EST FIXÉ. Les deux modules comparent des ÉCHÉANCES à aujourd'hui :
 * l'article 37 du DGA est échu depuis le 24 septembre 2025, l'article 50 du
 * Data Act s'échelonne jusqu'au 12 septembre 2027. Un écran qui dirait
 * « passée » ou « à venir » selon le jour de l'exécution rendrait la recette
 * non reproductible : l'horloge du navigateur est donc figée au
 * 5 octobre 2026, et les verdicts attendus sont écrits pour CE jour-là.
 *
 *   node outils/recette_donnees_partage.js
 */
'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn } = require('child_process');

const RACINE = path.dirname(__dirname);
const JETON = 'recette-donnees-partage-00000000000';
const ECRANS = ['dga-qualifier', 'dga-obligations', 'dga-pont-rgpd',
                'data-act-qualifier', 'data-act-obligations',
                'data-act-cloud', 'data-act-pont-rgpd'];

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
      .filter((l) => /RATE_LIMIT|SCRAPING|BLOCK|HEADLESS|dga|data.act/.test(l)).slice(-12);
  } catch (e) { return []; }
}

/* L'HORLOGE FIGÉE — posée AVANT tout script de la page, pour que `new Date()`
   du module voie le 5 octobre 2026 et pas le jour de l'exécution. Les deux
   modules comparent des échéances à aujourd'hui : sans ce gel, « passée » et
   « à venir » changeraient de place au fil des mois. */
const LE_JOUR = '2026-10-05T09:00:00Z';

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
    /* LES TROIS SIGNAUX, ET PAS DEUX. sentinel.page.js signale un navigateur
       automatisé dès que l'un des trois est vrai ; le serveur bloque alors
       l'adresse 1 800 s et TOUTES les routes répondent 429. */
    await ctx.addInitScript(() => {
      Object.defineProperty(navigator, 'webdriver', { get: () => false });
      Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
      Object.defineProperty(navigator, 'plugins',
                            { get: () => ({ length: 3, 0: {}, 1: {}, 2: {} }) });
    });
    await ctx.addInitScript(`(() => {
      const T = new Date('${LE_JOUR}').getTime();
      const V = Date;
      function D(...a) { return a.length ? new V(...a) : new V(T); }
      D.now = () => T; D.parse = V.parse; D.UTC = V.UTC; D.prototype = V.prototype;
      window.Date = D;
    })();`);
    const pg = await ctx.newPage();
    const erreurs = [];
    let refus429 = 0;
    pg.on('pageerror', (e) => erreurs.push(String(e).slice(0, 200)));
    pg.on('response', (r) => { if (r.status() === 429) refus429++; });
    await pg.goto(serveur.base + '/auth/' + JETON, { waitUntil: 'commit' });
    await pg.waitForFunction(
      () => typeof go === 'function' && typeof window.dpInit === 'function',
      null, { timeout: 90000 });
    const jour = await pg.evaluate(() => new Date().toISOString().slice(0, 10));
    if (jour !== '2026-10-05') fautes.push("l'horloge n'est pas figée : la page voit " + jour);
    else dits.push("horloge figée au " + jour);

    /* ── 1. LE TIROIR, SA TEINTE NEUTRE ET SES SEPT ONGLETS ─────────────── */
    const tiroir = await pg.evaluate(() => {
      const sec = document.querySelector('.sb-section[data-grp="donnees-et-partage"]');
      if (!sec) return null;
      const dga = document.querySelectorAll('.sb-item[data-norme="dga"]');
      const da = document.querySelectorAll('.sb-item[data-norme="data_act"]');
      const cs = getComputedStyle(sec);
      return { teinte: cs.getPropertyValue('--sb-ic').trim(),
               dga: dga.length, da: da.length,
               cdga: getComputedStyle(dga[0] || sec).getPropertyValue('--sb-ic').trim(),
               cda: getComputedStyle(da[0] || sec).getPropertyValue('--sb-ic').trim() };
    });
    if (!tiroir) fautes.push("le tiroir « donnees-et-partage » est absent de la barre");
    else {
      dits.push('tiroir : ' + tiroir.dga + ' onglet(s) DGA, ' + tiroir.da
                + ' Data Act ; teinte du titre ' + tiroir.teinte);
      if (tiroir.dga + tiroir.da !== 7) {
        fautes.push('le tiroir porte ' + (tiroir.dga + tiroir.da) + ' onglets au lieu de 7');
      }
      /*  UN TIROIR QUI TIENT DEUX RÉFÉRENTIELS RESTE NEUTRE : prendre la
          couleur de l'un des deux ferait croire que le groupe est à lui. */
      if (tiroir.teinte === tiroir.cdga || tiroir.teinte === tiroir.cda) {
        fautes.push('le titre du tiroir porte la couleur d\'un des deux '
                    + 'référentiels (' + tiroir.teinte + ') alors qu\'il en tient deux');
      }
      if (!tiroir.cdga || tiroir.cdga === tiroir.cda) {
        fautes.push('les deux référentiels ne se distinguent pas : DGA '
                    + tiroir.cdga + ', Data Act ' + tiroir.cda);
      } else {
        dits.push('couleurs : DGA ' + tiroir.cdga + ', Data Act ' + tiroir.cda);
      }
    }

    /* ── 2. LES SEPT ÉCRANS PEIGNENT — PAR go(), PAS PAR L'ONGLET ───────── */
    const lu = {};
    for (const id of ECRANS) {
      await pg.evaluate((i) => go(i), id);
      await pg.waitForTimeout(1200);
      const n = await pg.evaluate((i) => {
        const e = document.getElementById('p-' + i);
        return e ? (e.innerText || '').replace(/\s+/g, ' ').trim() : '';
      }, id);
      lu[id] = n;
      if (/Chargement…/.test(n)) {
        fautes.push(id + " reste sur « Chargement… » : aucun chemin n'amorce dpInit");
      } else if (/momentanément indisponible/.test(n)) {
        fautes.push(id + ' : le référentiel n\'a pas été servi (429 ou route en faute)');
      } else if (n.length < 400) {
        fautes.push(id + ' ne peint que ' + n.length + ' caractères');
      }
    }
    /*  LA RECETTE DIT CE QU'ELLE A MESURÉ, PAS SEULEMENT CE QU'ELLE
        REPROCHE. Sans cette ligne, une boucle sautée et sept écrans sains
        rendent le même verdict : « aucune faute ». Le plus court des sept
        est le chiffre utile — c'est lui qui approche le seuil. */
    const tailles = ECRANS.map((i) => (lu[i] || '').length);
    dits.push(ECRANS.length + ' écran(s) peints par go(), le plus court à '
              + Math.min.apply(null, tailles) + ' caractères');
    if (refus429) fautes.push(refus429 + ' réponse(s) 429 : le limiteur ou la détection a mordu');
    else dits.push('aucune réponse 429 — les trois signaux suffisent');

    /* ── 3. CE QUE LES ÉCRANS DOIVENT DIRE, MOT POUR MOT ────────────────── */
    const ATTENDU = [
      ['dga-qualifier', /quatre cadres/i, 'les quatre cadres de l\'article 1er §1'],
      ['dga-obligations', /quinze|qualité/i, 'les obligations de la qualité déclarée'],
      ['dga-pont-rgpd', /RGPD/, 'le pont vers le RGPD'],
      ['data-act-qualifier', /sept qualités|lieu d\u2019établissement|lieu d'établissement/i,
       'les sept qualités, extraterritoriales'],
      ['data-act-obligations', /chapitre/i, 'les obligations par chapitre'],
      ['data-act-cloud', /changement|fournisseur/i, 'le changement de fournisseur'],
      ['data-act-pont-rgpd', /RGPD/, 'le pont vers le RGPD'],
    ];
    for (const [id, motif, quoi] of ATTENDU) {
      if (!motif.test(lu[id] || '')) fautes.push(id + ' ne dit pas ' + quoi);
    }
    /*  L'ÉCHÉANCE ÉCHUE EST DITE ÉCHUE, et c'est le gel de l'horloge qui
        rend ce verdict reproductible : au 5 octobre 2026, l'article 37 du
        DGA est passé depuis plus d'un an. */
    if (!/passée|échu|infraction/i.test(lu['dga-obligations'] || '')) {
      fautes.push("dga-obligations ne dit pas que l'échéance de l'article 37 est passée");
    } else {
      dits.push("l'échéance échue de l'article 37 est dite passée");
    }

    /* ── 4. « AUCUNE » EST EXCLUSIVE, et le module s'arrête ─────────────── */
    await pg.evaluate(() => go('dga-qualifier'));
    await pg.waitForTimeout(600);
    const apres = await pg.evaluate(() => {
      dpQualite('dga', 'intermediaire');
      dpQualite('dga', 'aucune');
      const d = JSON.parse(localStorage.getItem('cp-sentinel-dga-v1') || '{}');
      return d.qualites || [];
    });
    if (apres.length !== 1 || apres[0] !== 'aucune') {
      fautes.push('« aucune de ces qualités » n\'est pas exclusive : ' + JSON.stringify(apres));
    } else {
      dits.push('« aucune » est exclusive — elle a chassé « intermediaire »');
    }

    /* ── 5. LA DÉCLARATION SURVIT AU RECHARGEMENT ──────────────────────── */
    await pg.evaluate(() => { dpQualite('data_act', 'fabricant'); });
    await pg.waitForTimeout(300);
    await pg.goto(serveur.base + '/sentinel', { waitUntil: 'commit' });
    await pg.waitForFunction(() => typeof window.dpInit === 'function', null, { timeout: 90000 });
    await pg.evaluate(() => go('data-act-qualifier'));
    await pg.waitForTimeout(1500);
    const garde = await pg.evaluate(() =>
      (JSON.parse(localStorage.getItem('cp-sentinel-data-act-v1') || '{}').qualites) || []);
    if (garde.indexOf('fabricant') < 0) {
      fautes.push('la qualité déclarée ne survit pas au rechargement : ' + JSON.stringify(garde));
    } else {
      dits.push('la qualité « fabricant » survit au rechargement');
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
  console.log('\n  recette Données & Partage : aucune faute');
})().catch((e) => { console.error(e); process.exit(1); });
