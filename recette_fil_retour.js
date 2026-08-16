/* Le fil des étapes RAMÈNE au menu à chaque étape franchie — /enveloppe.
 *
 * CE QU'ON PROTÈGE, ET LA FAUTE QUE CHAQUE CONTRÔLE EMPÊCHE :
 *
 *   1. LE FIL NOMME LA PROCHAINE ÉTAPE, et un bouton y mène. Une rangée de
 *      pastilles laisse au lecteur le soin de chercher laquelle vient
 *      ensuite ; un menu qu'il faut déchiffrer ne sert qu'une fois.
 *   2. FRANCHIR UNE ÉTAPE RAMÈNE AU FIL. C'est la demande : on valide, on
 *      revient au menu, on repart. Sans cela le fil se met à jour tout en
 *      haut et personne ne le voit.
 *   3. LE RETOUR NE PART QUE SUR UN FRANCHISSEMENT RÉEL. Un recalcul qui ne
 *      change aucun état ne doit RIEN déplacer — une page qui remonte le
 *      lecteur sans raison est pire qu'une page qui ne l'aide pas.
 *   4. LE CHARGEMENT NE RAMÈNE PAS. L'étape 1 est faite dès l'arrivée : la
 *      compter comme franchie remonterait le lecteur avant qu'il n'ait rien
 *      fait.
 *   5. LE RETOUR SE COUPE. Un lecteur qui étudie la DPGF ne doit pas être
 *      remonté toutes les trente secondes.
 *   6. L'AVANCEMENT RESTE DÉDUIT DE LA PAGE. Vider un bloc décoche son étape :
 *      un compteur tenu à part afficherait « fait » devant un bloc vide.
 *
 *     BASE=http://127.0.0.1:5510 node recette_fil_retour.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5510';
const TOKEN = process.env.RECETTE_TOKEN || 'recette_locale_idf_0123456789abcdef';
let ko = 0;
const ok = (n, c, d) => { console.log('  ' + (c ? 'OK ' : 'KO ') + '  ' + n + (d ? ' — ' + d : '')); if (!c) ko++; };
const titre = (t) => console.log('\n══ ' + t + ' ══\n');

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1400, height: 900 } });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e)));
  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg.waitForTimeout(400);

  const rep = await pg.goto(BASE + '/enveloppe', { waitUntil: 'domcontentloaded' });
  ok('la page répond', rep && rep.status() === 200,
     rep ? 'HTTP ' + rep.status() : 'pas de réponse');
  if (!rep || rep.status() !== 200) { await nav.close(); process.exit(2); }
  await pg.waitForFunction(() => !!document.querySelector('#fin-fil .fin-fil-p'),
                           null, { timeout: 25000 }).catch(() => {});

  /* La position du fil dans la fenêtre : c'est la SEULE preuve qu'on y a été
     ramené. Comparer l'étape courante recalculée ne prouverait rien — elle
     change de toute façon. */
  const posFil = () => pg.evaluate(() => {
    const el = document.getElementById('fin-fil');
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return { haut: Math.round(r.top), dansLaVue: r.top > -40 && r.top < 320 };
  });
  const etatFil = () => pg.evaluate(() => {
    const p = document.querySelector('#fin-fil .fin-fil-p');
    const a = document.getElementById('fin-fil-a');
    return {
      compteur: (p && p.querySelector('.fin-fil-pn') || {}).textContent || '',
      prochaine: (p && p.querySelector('.fin-fil-px') || {}).textContent || '',
      bouton: (p && p.querySelector('[data-fin-suite]') || {}).textContent || '',
      cible: p && p.querySelector('[data-fin-suite]')
        ? p.querySelector('[data-fin-suite]').getAttribute('data-fin-suite') : '',
      annonce: (a || {}).textContent || '',
      faites: document.querySelectorAll('#fin-fil .fin-e.fait').length,
      total: document.querySelectorAll('#fin-fil .fin-e').length
    };
  });

  // ── 1 ────────────────────────────────────────────────────────────────────
  titre('1. Le fil dit où l’on en est ET ce qui vient ensuite');

  const d = await etatFil();
  /* LE COMPTE VIENT DE LA PAGE, PAS D'ICI. Ce contrôle exigeait six étapes :
     il est tombé le jour où le fil a couvert toute la vue — équipements,
     maturité et pilotage —, en signalant une régression là où il n'y avait
     qu'un inventaire figé de plus. Ce qu'il protège n'a pas changé : le fil
     affiche autant de pastilles qu'il déclare d'étapes, et son compteur
     s'accorde avec elles. */
  const attendu = await pg.evaluate(() => FIN_ETAPES.length);
  ok('le fil affiche autant de pastilles qu’il déclare d’étapes',
     d.total === attendu, d.total + ' pastille(s) pour ' + attendu + ' déclarée(s)');
  ok('un compteur d’avancement est donné',
     new RegExp('^\\d+ / ' + attendu + '$').test(d.compteur.trim()), d.compteur);
  ok('…et il correspond aux étapes cochées',
     d.compteur.trim().split('/')[0].trim() === String(d.faites),
     d.compteur + ' contre ' + d.faites + ' cochée(s)');
  ok('la PROCHAINE étape est nommée, pas seulement montrée',
     /Prochaine étape/i.test(d.prochaine) && d.prochaine.length > 40, d.prochaine.slice(0, 90));
  ok('…et un bouton y mène', /Aller à l’étape/.test(d.bouton), d.bouton);
  ok('…il vise bien une étape du fil', !!d.cible, d.cible);

  // ── 2 ────────────────────────────────────────────────────────────────────
  titre('2. LE CHARGEMENT NE RAMÈNE PAS — l’étape 1 est faite d’office');

  ok('aucune annonce de franchissement à l’arrivée', d.annonce.trim() === '',
     d.annonce);
  await pg.evaluate(() => window.scrollTo(0, 1400));
  await pg.waitForTimeout(400);
  const avantRien = await posFil();
  /* Un recalcul qui ne franchit rien : on redéclenche l'événement de pays sans
     rien changer à la sélection. */
  await pg.evaluate(() => document.dispatchEvent(new Event('fin-pays')));
  await pg.waitForTimeout(700);
  const apresRien = await posFil();
  ok('un recalcul SANS franchissement ne déplace pas la page',
     Math.abs(apresRien.haut - avantRien.haut) < 30,
     avantRien.haut + ' → ' + apresRien.haut);

  /* UNE ÉTAPE QUI SE COCHE TOUTE SEULE NE DOIT RIEN BOUSCULER. Le cas est
     réel : le référentiel des pays arrive après le chargement et arme d'office
     l'étape 2. Un lecteur descendu lire la DPGF se retrouverait projeté en
     haut de page sans avoir rien demandé. On le reproduit ici SANS aucun
     événement de souris ni de clavier — c'est ce qui distingue « la page a
     avancé » de « le lecteur a agi ». */
  const cocheSeule = await pg.evaluate(() => {
    const r = document.getElementById('fin-res');
    if (!r) return null;
    const avant = Math.round(window.scrollY);
    const n0 = document.querySelectorAll('#fin-fil .fin-e.fait').length;
    /* On fait croire au fil que l'étape « calculer » vient d'aboutir. */
    const d = document.createElement('div');
    d.className = 'fin-dos';
    r.appendChild(d);
    document.dispatchEvent(new Event('fin-calcul'));
    return { avant: avant, n0: n0 };
  });
  await pg.waitForTimeout(900);
  const seule = await pg.evaluate((c) => ({
    bouge: Math.abs(Math.round(window.scrollY) - c.avant),
    n1: document.querySelectorAll('#fin-fil .fin-e.fait').length,
    annonce: (document.getElementById('fin-fil-a') || {}).textContent || ''
  }), cocheSeule);
  ok('le fil enregistre bien l’étape cochée toute seule',
     seule.n1 > cocheSeule.n0, cocheSeule.n0 + ' → ' + seule.n1);
  ok('…MAIS il ne remonte PAS un lecteur qui n’a rien fait',
     seule.bouge < 30, 'déplacement de ' + seule.bouge + ' px');
  ok('…et il n’annonce rien qu’on n’ait demandé', seule.annonce.trim() === '',
     seule.annonce.slice(0, 80));
  /* On remet la page dans l'état où on l'a trouvée : la suite éprouve un
     franchissement RÉEL, elle ne doit pas hériter d'un faux. */
  await pg.evaluate(() => {
    const r = document.getElementById('fin-res');
    if (r) r.innerHTML = '';
    document.dispatchEvent(new Event('fin-calcul'));
  });
  await pg.waitForTimeout(400);

  // ── 3 : LE POINT QUI DÉCIDE ──────────────────────────────────────────────
  titre('3. LE POINT QUI DÉCIDE : franchir une étape ramène au fil');

  /* On se place LOIN du fil, puis on franchit l'étape « calculer ». Si la page
     ne remonte pas, le menu se met à jour là où personne ne le voit — et la
     demande n'est pas tenue. */
  await pg.waitForFunction(
    () => document.querySelectorAll('#fin-pays button[data-p]').length > 0,
    null, { timeout: 30000 }).catch(() => {});
  await pg.evaluate(() => {
    const b = document.getElementById('fin-go');
    if (b) b.scrollIntoView({ block: 'center', behavior: 'instant' });
  });
  await pg.waitForTimeout(300);
  const avant = await posFil();
  ok('le fil est bien HORS de la vue avant le clic', !avant.dansLaVue,
     'haut = ' + avant.haut);

  await pg.click('#fin-go');
  /* On attend que le fil soit revenu dans la vue, sans dépasser la durée que
     la page s'accorde pour surveiller la réponse du serveur. */
  const revenu = await pg.waitForFunction(() => {
    const el = document.getElementById('fin-fil');
    if (!el) return false;
    const t = el.getBoundingClientRect().top;
    return t > -40 && t < 320;
  }, null, { timeout: 20000 }).then(() => true).catch(() => false);
  const apres = await posFil();
  ok('FRANCHIR L’ÉTAPE RAMÈNE AU FIL', revenu && apres.dansLaVue,
     'haut = ' + apres.haut + (revenu ? '' : ' — jamais revenu'));

  const e3 = await etatFil();
  ok('…le fil ANNONCE l’étape franchie', /faite/i.test(e3.annonce), e3.annonce.slice(0, 110));
  ok('…et nomme la suivante dans la même phrase',
     /Prochaine\s*:/i.test(e3.annonce), e3.annonce.slice(0, 110));
  ok('…le compteur a progressé', e3.faites > d.faites,
     d.faites + ' → ' + e3.faites);
  ok('…et le bouton vise désormais une AUTRE étape', e3.cible !== d.cible,
     d.cible + ' → ' + e3.cible);

  titre('4. …et le bouton du fil mène bien au bloc de l’étape suivante');
  const cible = e3.cible;
  await pg.click('[data-fin-suite]');
  await pg.waitForTimeout(1200);
  const vise = await pg.evaluate((cle) => {
    /* La cible du bloc, telle que la page la déclare — on ne la recopie pas
       ici, sinon le contrôle mesurerait ma copie et non la page. */
    let e = null;
    FIN_ETAPES.forEach(x => { if (x.cle === cle) e = x; });
    if (!e) return null;
    const el = document.getElementById(e.cible);
    if (!el) return { manque: e.cible };
    const r = el.getBoundingClientRect();
    return { id: e.cible, haut: Math.round(r.top),
             dansLaVue: r.top > -200 && r.top < window.innerHeight };
  }, cible);
  ok('le bloc de l’étape suivante est atteint', !!vise && vise.dansLaVue,
     vise ? (vise.manque ? 'bloc absent : ' + vise.manque
                         : vise.id + ' à ' + vise.haut) : 'étape inconnue');

  // ── 5 ────────────────────────────────────────────────────────────────────
  titre('5. Le retour se coupe — et le fil continue de se tenir à jour');

  await pg.evaluate(() => {
    document.getElementById('fin-fil').scrollIntoView({ block: 'start', behavior: 'instant' });
  });
  await pg.waitForTimeout(200);
  const presse = await pg.evaluate(() => {
    const b = document.getElementById('fin-fil-r');
    return b ? b.getAttribute('aria-pressed') : null;
  });
  ok('le fil annonce qu’il ramène, AVANT de l’avoir fait', presse === 'true', presse);
  await pg.click('#fin-fil-r');
  await pg.waitForTimeout(300);
  const coupe = await pg.evaluate(() => ({
    presse: (document.getElementById('fin-fil-r') || {}).getAttribute
      ? document.getElementById('fin-fil-r').getAttribute('aria-pressed') : null,
    dit: (document.getElementById('fin-fil-a') || {}).textContent || ''
  }));
  ok('…et il se coupe', coupe.presse === 'false', coupe.presse);
  ok('…en disant ce qui change', /ne vous ramènera plus/i.test(coupe.dit),
     coupe.dit.slice(0, 90));

  /* Coupé, un franchissement ne doit PLUS déplacer la page — mais le fil doit
     rester juste. On franchit l’étape « MOE ». */
  await pg.evaluate(() => {
    const b = document.getElementById('moe-go');
    if (b) b.scrollIntoView({ block: 'center', behavior: 'instant' });
  });
  await pg.waitForTimeout(300);
  const avantCoupe = await posFil();
  const aMoe = await pg.evaluate(() => !!document.getElementById('moe-go'));
  if (aMoe) {
    await pg.click('#moe-go');
    await pg.waitForTimeout(6000);
    const apresCoupe = await posFil();
    ok('retour coupé : la page ne remonte plus',
       Math.abs(apresCoupe.haut - avantCoupe.haut) < 40,
       avantCoupe.haut + ' → ' + apresCoupe.haut);
    const e5 = await etatFil();
    ok('…mais le fil s’est bien mis à jour sur place', e5.faites >= e3.faites,
       e3.faites + ' → ' + e5.faites);
  } else {
    ok('le bloc de maîtrise d’œuvre est présent', false, '#moe-go absent');
  }

  // ── 6 ────────────────────────────────────────────────────────────────────
  titre('6. L’avancement reste DÉDUIT de la page, jamais tenu à part');

  const avantVidage = (await etatFil()).faites;
  await pg.evaluate(() => {
    const r = document.getElementById('fin-res');
    if (r) r.innerHTML = '';
    document.dispatchEvent(new Event('fin-calcul'));
  });
  await pg.waitForTimeout(600);
  const apresVidage = await etatFil();
  ok('vider un bloc DÉCOCHE son étape', apresVidage.faites < avantVidage,
     avantVidage + ' → ' + apresVidage.faites);
  ok('…et le compteur suit',
     apresVidage.compteur.trim().split('/')[0].trim() === String(apresVidage.faites),
     apresVidage.compteur + ' contre ' + apresVidage.faites);

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec') + '\n');
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
