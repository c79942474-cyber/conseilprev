/* RECETTE — LES INFOBULLES S'OUVRENT AU DOIGT, AU CLAVIER, ET TOUJOURS AU SURVOL
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LE DÉFAUT SIGNALÉ : « les infobulles ne s'ouvrent jamais sur un appareil
 * tactile ». Mesuré avant correction, en contexte tactile réel (Pixel 7,
 * hasTouch, `(hover:none)` vrai) : l'opacité de la bulle valait 0 AVANT et
 * APRÈS un appui du doigt. Et le clavier n'allait pas mieux — les cartes sont
 * des <div> sans tabindex, `element.focus()` n'y prenait même pas.
 *
 * POURQUOI UNE RECETTE, ET NON DES RÈGLES SEULES. Une règle Python lit le
 * fichier : elle voit l'écouteur, la classe, la règle CSS. Elle ne voit pas
 * qu'un événement de défilement, émis APRÈS l'appui, retire la classe qu'on
 * vient de poser. C'est exactement ce qui est arrivé ici : la page défile en
 * `scroll-behavior:smooth`, amener une carte à l'écran émet des dizaines
 * d'événements de défilement, et la première version du script fermait la
 * bulle à chacun. La classe était posée puis retirée dans la foulée — aucune
 * erreur, aucune trace, et une infobulle qui ne s'ouvre jamais sur téléphone.
 *
 * LE CONTRÔLE QUI COMPTE EST DIFFÉRENTIEL. L'état ouvert n'est pas déclaré :
 * il est DÉRIVÉ des règles de survol déjà écrites dans la page. Vérifier
 * « la bulle est visible » ne prouverait pas cette dérivation — une valeur
 * devinée au hasard donnerait le même verdict. On mesure donc la géométrie de
 * la bulle DEUX FOIS : au survol à la souris, puis à l'appui du doigt. Les
 * deux relevés doivent être identiques, sinon le doigt ouvre une bulle qui
 * n'est pas celle du survol.
 *
 * ET LE SURVOL NE DOIT PAS AVOIR RÉGRESSÉ : sur un poste fixe, le script ne
 * doit dessiner aucune seconde bulle et ne doit pas détourner un clic.
 */
const { chromium, devices } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5901';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
const SEL = '#differenciateurs .diff-card[data-tooltip]';
let ko = 0, n = 0;
const ok = (t, c, d) => { n++; if (!c) ko++;
  console.log((c ? '  OK   ' : '  KO   ') + t + (d ? ' — ' + d : '')); };

/* LA GÉOMÉTRIE DE LA BULLE, dans le repère de la page. On lit le
 * pseudo-élément ::after, qui EST la bulle : ni un enfant, ni un voisin. */
const BULLE = (s) => {
  const e = document.querySelector(s);
  if (!e) return null;
  const cs = getComputedStyle(e, '::after');
  return { opacite: cs.opacity, transform: cs.transform,
           bas: cs.bottom, gauche: cs.left, largeur: cs.width };
};

const FURTIF = (ctx) => ctx.addInitScript(() => {
  Object.defineProperty(navigator, 'webdriver', { get: () => false });
  Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
  Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
});

(async () => {
  const nav = await chromium.launch();

  // ══ 1. AU DOIGT ════════════════════════════════════════════════════════
  console.log('\n1. Au doigt — ce qui ne marchait pas du tout');
  let ctx = await nav.newContext({ ...devices['Pixel 7'], hasTouch: true, isMobile: true });
  await FURTIF(ctx);
  let p = await ctx.newPage();
  await p.goto(BASE + '/', { waitUntil: 'domcontentloaded' });
  await p.waitForSelector(SEL);
  await p.waitForFunction(() => !!document.getElementById('css-bulle-ouverte'),
                          null, { timeout: 8000 });
  ok('le contexte est bien tactile',
     await p.evaluate(() => matchMedia('(hover:none)').matches));
  const repos = await p.evaluate(BULLE, SEL);
  ok('au repos la bulle est fermée', repos.opacite === '0', 'opacité ' + repos.opacite);
  ok('la carte est devenue atteignable au clavier',
     await p.evaluate(s => document.querySelector(s).getAttribute('tabindex'), SEL) === '0');

  await p.locator(SEL).first().tap();
  await p.waitForTimeout(500);
  const doigt = await p.evaluate(BULLE, SEL);
  ok('APRÈS L’APPUI la bulle est OUVERTE', doigt.opacite === '1',
     'opacité ' + doigt.opacite);
  ok('le texte est annoncé au lecteur d’écran',
     (await p.evaluate(() => (document.getElementById('bulle-annonce') || {}).textContent || '')
     ).length > 30);

  /* LE TÉMOIN DU DÉFAUT CORRIGÉ : un défilement APRÈS l'appui ne doit plus
     refermer la bulle. C'est la situation ordinaire sur un téléphone. */
  await p.evaluate(() => window.scrollBy(0, 40));
  await p.waitForTimeout(500);
  ok('un défilement après l’appui NE referme PAS (le défaut mesuré)',
     (await p.evaluate(BULLE, SEL)).opacite === '1');

  /* LES SORTIES — chacune mesurée depuis un état RÉELLEMENT ouvert, sinon
     le contrôle passerait sur une bulle déjà fermée, pour une raison sans
     rapport avec ce qu'il prétend. */
  ok('la bulle est bien ouverte avant d’éprouver le second appui',
     (await p.evaluate(BULLE, SEL)).opacite === '1');
  await p.locator(SEL).first().tap();
  await p.waitForTimeout(400);
  ok('un second appui referme', (await p.evaluate(BULLE, SEL)).opacite === '0');

  await p.locator(SEL).first().tap();
  await p.waitForTimeout(400);
  ok('la bulle est bien ouverte avant d’éprouver Échap',
     (await p.evaluate(BULLE, SEL)).opacite === '1');
  await p.keyboard.press('Escape');
  await p.waitForTimeout(300);
  ok('Échap referme', (await p.evaluate(BULLE, SEL)).opacite === '0');
  await ctx.close();

  // ══ 2. LA SOURIS, ET LE CONTRÔLE DIFFÉRENTIEL ══════════════════════════
  console.log('\n2. À la souris — le survol, et la bulle du doigt est LA MÊME');
  ctx = await nav.newContext({ viewport: { width: 1280, height: 900 } });
  await FURTIF(ctx);
  p = await ctx.newPage();
  await p.goto(BASE + '/', { waitUntil: 'domcontentloaded' });
  await p.waitForSelector(SEL);
  await p.locator(SEL).first().scrollIntoViewIfNeeded();
  await p.waitForTimeout(600);
  await p.waitForFunction(() => !!document.getElementById('css-bulle-ouverte'),
                          null, { timeout: 8000 });
  /* LE CONTOUR AU REPOS — UN DÉFAUT TROUVÉ APRÈS COUP, EN RELISANT LE SOCLE.
     Collée derrière « [data-tooltip],[data-tip] », la pseudo-classe
     `:focus-visible` ne visait que la dernière partie de la liste : la
     première restait `[data-tooltip]` tout court, et CHAQUE infobulle
     portait un contour de 2 px sans avoir le focus. Mesuré : 32 sur 32. */
  const contours = await p.evaluate(() => {
    const t = [...document.querySelectorAll('[data-tooltip],[data-tip]')];
    const avec = t.filter(e => { const cs = getComputedStyle(e);
      return cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0; });
    return { total: t.length, avec: avec.length,
             focus: document.activeElement === document.body };
  });
  ok('au repos, AUCUNE infobulle ne porte de contour',
     contours.focus && contours.total > 0 && contours.avec === 0,
     contours.avec + ' sur ' + contours.total + (contours.focus ? '' : ' (le focus n’est pas au repos)'));
  const b = await p.locator(SEL).first().boundingBox();
  await p.mouse.move(b.x + b.width / 2, b.y + b.height / 2);
  await p.waitForTimeout(700);
  const souris = await p.evaluate(BULLE, SEL);
  ok('au survol la bulle est ouverte', souris.opacite === '1');

  /* LE CONTRÔLE DIFFÉRENTIEL, DANS LA MÊME FENÊTRE.
     Une première version comparait le relevé du téléphone à celui du poste
     fixe et tombait sur la largeur : 354 px contre 298. Ce n'était pas un
     défaut du script — la bulle est réglée `left:16px;right:16px`, donc sa
     largeur suit celle de la carte, qui suit celle de l'écran. Comparer
     deux fenêtres de largeurs différentes ne prouve rien, et un contrôle
     qui tombe pour une raison sans rapport avec ce qu'il mesure est
     exactement le défaut que ce dépôt traque partout ailleurs.
     ON COMPARE DONC LES DEUX ÉTATS DANS LA MÊME FENÊTRE : la bulle ouverte
     par le SURVOL, puis la même ouverte par la CLASSE. C'est précisément ce
     que la dérivation prétend faire — reprendre la règle de survol —, et
     rien ne peut faire passer ce contrôle par accident. */
  await p.mouse.move(0, 0);
  await p.waitForTimeout(600);
  /* L'OUVERTURE EST UNE TRANSITION, PAS UN INTERRUPTEUR. Lire le style
     dans le même tour que la pose de la classe rend l'état d'AVANT :
     l'opacité part de 0 et met 180 ms à monter. On pose, on laisse la
     transition finir, puis on lit. */
  await p.evaluate(s => window.infobulles.ouvrir(document.querySelector(s)), SEL);
  await p.waitForTimeout(600);
  const classe = await p.evaluate((s) => {
    const e = document.querySelector(s), cs = getComputedStyle(e, '::after');
    return { opacite: cs.opacity, transform: cs.transform, bas: cs.bottom,
             gauche: cs.left, largeur: cs.width };
  }, SEL);
  const memes = ['opacite', 'transform', 'bas', 'gauche', 'largeur']
    .filter(k => souris[k] !== classe[k]);
  ok('la bulle OUVERTE PAR LA CLASSE est exactement celle du SURVOL',
     memes.length === 0,
     memes.length ? memes.map(k => k + ' : survol=' + souris[k] + ' classe=' + classe[k]).join(' · ')
                  : 'opacité, transform, position et largeur identiques');
  await p.evaluate(() => window.infobulles.fermer());

  ok('aucune seconde bulle n’a été dessinée',
     await p.evaluate(() => document.querySelectorAll(
       '.bulle-ouverte, .tooltip-js, [class*="infobulle-"]').length) === 0);
  await p.mouse.move(b.x + 5, b.y + 5);
  await p.mouse.down(); await p.mouse.up();
  await p.waitForTimeout(300);
  ok('un clic de souris n’ouvre pas de bulle collante',
     await p.evaluate(() => document.querySelectorAll('.bulle-ouverte').length) === 0);
  await ctx.close();

  // ══ 3. LE CLAVIER ══════════════════════════════════════════════════════
  console.log('\n3. Au clavier — la carte ne prenait même pas le focus');
  ctx = await nav.newContext({ viewport: { width: 1280, height: 900 } });
  await FURTIF(ctx);
  p = await ctx.newPage();
  await p.goto(BASE + '/', { waitUntil: 'domcontentloaded' });
  await p.waitForSelector(SEL);
  await p.waitForFunction(() => !!document.getElementById('css-bulle-ouverte'),
                          null, { timeout: 8000 });
  const clav = await p.evaluate((s) => {
    const e = document.querySelector(s); e.focus();
    return { actif: document.activeElement === e,
             annonce: (document.getElementById('bulle-annonce') || {}).textContent || '' };
  }, SEL);
  ok('la carte PREND le focus', clav.actif);
  ok('le focus annonce le texte', clav.annonce.length > 30);
  await ctx.close();

  // ══ 4. LE RAIL DORA, QUI PORTAIT UN `title` NATIF ══════════════════════
  console.log('\n4. Le rail DORA — son infobulle était un `title`, muet au doigt');
  ctx = await nav.newContext({ ...devices['Pixel 7'], hasTouch: true, isMobile: true });
  await FURTIF(ctx);
  p = await ctx.newPage();
  await p.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'domcontentloaded' });
  await p.goto(BASE + '/sentinel?goto=dora-qualifier', { waitUntil: 'domcontentloaded' });
  const RAIL = '#dora-rail-qualifier .dr-bloc[data-tooltip]';
  const vu = await p.waitForSelector(RAIL, { timeout: 15000 }).then(() => true)
                    .catch(() => false);
  ok('les blocs du rail portent data-tooltip et non title', vu);
  if (vu) {
    ok('aucun bloc du rail ne garde un `title` natif',
       await p.evaluate(() => [...document.querySelectorAll('.dr-bloc')]
         .every(b => !b.getAttribute('title'))));
    const avant = await p.evaluate(s => getComputedStyle(
      document.querySelector(s), '::after').opacity, RAIL);
    ok('au repos la bulle du rail est fermée', avant === '0', 'opacité ' + avant);
    await p.locator(RAIL).first().tap();
    await p.waitForTimeout(500);
    const apres = await p.evaluate(s => getComputedStyle(
      document.querySelector(s), '::after').opacity, RAIL);
    ok('APRÈS L’APPUI la bulle du rail est ouverte', apres === '1',
       'opacité ' + apres);
    /* Elle s'ouvre VERS LE BAS : le rail est en tête du panneau, une bulle
       posée au-dessus sortirait de la zone défilante par le haut. */
    ok('la bulle du rail s’ouvre vers le bas',
       await p.evaluate(s => getComputedStyle(document.querySelector(s), '::after')
         .top !== 'auto', RAIL));
    /* LE TÉMOIN DU DÉFAUT CORRIGÉ : le premier appui ne doit PAS avoir
       navigué, sinon le repeint aurait détruit le bouton qui porte la
       bulle — et c'est exactement ce qui se passait. */
    ok('le premier appui n’a pas navigué (la bulle a survécu)',
       await p.evaluate(s => !!document.querySelector(s), RAIL));
    /* ET LE SECOND APPUI, LUI, Y VA. Sans ce contrôle, « lire d’abord »
       pourrait avoir bloqué la navigation pour toujours, ce qui serait un
       défaut pire que celui qu’on corrige. */
    await p.locator(RAIL).first().tap();
    await p.waitForTimeout(900);
    ok('le SECOND appui mène bien au panneau',
       await p.evaluate(() => {
         var v = document.getElementById('p-dora-qualifier');
         return !!v && getComputedStyle(v).display !== 'none';
       }));
  }
  await ctx.close();

  // ══ 5. LA SECONDE FAMILLE — LE FILTRE EST-IL VRAIMENT DÉRIVÉ ? ════════
  console.log('\n5. La seconde famille (.ent-tip) — sans elle, « dérivé » n\u2019est qu\u2019un mot');
  /* POURQUOI CETTE SECTION EXISTE. Le script prétend reconnaître une
     infobulle à ce qu'elle REND l'attribut, et non à une liste de noms de
     classes. Tout ce qui précède ne mesure QUE la famille [data-tooltip] :
     un script qui citerait `[data-tooltip]` en dur passerait à l'identique.
     `.ent-tip` porte un autre nom, un autre attribut (data-tip) et un autre
     réglage — c'est le témoin qui sépare les deux. */
  ctx = await nav.newContext({ ...devices['Pixel 7'], hasTouch: true, isMobile: true });
  await FURTIF(ctx);
  p = await ctx.newPage();
  await p.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'domcontentloaded' });
  await p.goto(BASE + '/sentinel', { waitUntil: 'domcontentloaded' });
  const ENT = '.ent-tip[data-tip]';
  /* `state:'attached'` ET NON la visibilité : Sentinel range ses panneaux
     et n'en montre qu'un. La famille existe dans la page entière ; on
     cherche ensuite celle qui est à l'écran pour l'appuyer. */
  const vue = await p.waitForSelector(ENT, { timeout: 15000, state: 'attached' })
                     .then(() => true).catch(() => false);
  ok('Sentinel porte bien la seconde famille', vue);
  if (vue) {
    ok('la jumelle de .ent-tip a été publiée', await p.evaluate(() => {
      const st = document.getElementById('css-bulle-ouverte');
      return !!st && st.textContent.indexOf('.ent-tip.bulle-ouverte') >= 0;
    }));
    /* ON OUVRE PAR L'API, ET C'EST LE BON CONTRÔLE ICI.
       Sentinel range ses panneaux et n'en montre qu'un : la pastille
       `.ent-tip` qu'on voudrait appuyer dépend du panneau ouvert, ce qui
       ferait de cette section un contrôle instable mesurant la navigation
       plutôt que l'infobulle. `window.infobulles.ouvrir()` est EXACTEMENT
       ce que l'appui appelle — la mécanique de l'appui est déjà éprouvée
       deux fois plus haut. Ce qui se joue ici est autre chose : `.ent-tip`
       est la SEULE famille dont le sélecteur ne cite pas l'attribut. Elle
       n'est reconnue que par `content:attr(data-tip)`. Si la jumelle
       fonctionne pour elle, le filtre est bien dérivé. */
    const CONTENU = (s) => {
      const e = document.querySelector(s);
      return getComputedStyle(e, '::after').content;
    };
    const av = await p.evaluate(CONTENU, ENT);
    await p.evaluate(s => window.infobulles.ouvrir(document.querySelector(s)), ENT);
    await p.waitForTimeout(400);
    const ap = await p.evaluate(CONTENU, ENT);
    /* `.ent-tip` n'a AUCUNE bulle au repos : sa règle de survol crée le
       ::after de toutes pièces. On mesure donc l'apparition du CONTENU, et
       non une opacité qui n'existe pas. */
    ok('au repos la bulle .ent-tip n\u2019a pas de contenu', av === 'none', av);
    ok('UNE FOIS OUVERTE, la bulle .ent-tip a son contenu',
       ap !== 'none' && ap.length > 6, String(ap).slice(0, 46) + '…');
  }
  await ctx.close();

  console.log('\n' + (ko ? 'ÉCHECS ' + ko + '/' + n : 'TOUT VERT ' + n + '/' + n));
  await nav.close();
  process.exit(ko ? 1 : 0);
})();
