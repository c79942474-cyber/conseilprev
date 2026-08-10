/* Emporter les calculs ET les cartes — côté navigateur.
 *
 * 1. LE SERVEUR N'A JAMAIS VU LES CARTES. Elles sont dessinées ici, en SVG, à
 *    partir des calculs qu'il a servis. Un export qui ne les emporte pas livre
 *    des tableaux — et perd ce qui fait qu'on regarde une carte plutôt qu'une
 *    colonne de nombres. Le sérialiseur les rembobine en PNG.
 *
 * 2. LE PIÈGE DU STYLE. Un SVG affiché emprunte le CSS de la page. Sérialisé
 *    tel quel puis rendu hors de la page, il perd ses couleurs d'un coup : on
 *    obtient une silhouette noire et personne ne comprend pourquoi. Le contrôle
 *    regarde donc les PIXELS de l'image produite, pas seulement sa taille.
 *
 * 3. CE QU'ON REFUSE. Un sélecteur qui désigne le conteneur et non le dessin
 *    est une erreur silencieuse — on a sérialisé un <div> comme du SVG et la
 *    carte du Panorama a manqué sans que rien ne le dise. Le helper refuse
 *    désormais ce qui n'est pas un <svg>, et le manque est NOMMÉ.
 *
 * 4. LA VUE AFFICHÉE PART AVEC. Si le lecteur a basculé les brevets sur
 *    « Composition », c'est cela qu'il veut dans son document.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = 'http://127.0.0.1:5401';
let ko = 0;
const ok = (n, c, d) => { console.log('  ' + (c ? 'OK ' : 'KO ') + '  ' + n + (d ? ' — ' + d : '')); if (!c) ko++; };

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1440, height: 1000 },
                                     acceptDownloads: true });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e)));
  await pg.goto(BASE + '/auth/recette_locale_idf_0123456789abcdef', { waitUntil: 'domcontentloaded' });
  await pg.goto(BASE + '/observatoire', { waitUntil: 'networkidle' });
  await pg.waitForFunction(() => document.querySelector('#brev-chart svg') && window.FIG,
                           null, { timeout: 30000 });

  console.log('\n══ 1. Le sérialiseur rembobine un SVG en PNG ══\n');
  const outil = await pg.evaluate(() => ({
    charge: typeof FIG === 'object',
    fns: ['svgEnPng', 'collecter', 'telecharger'].filter(k => typeof FIG[k] === 'function'),
  }));
  ok('l’outil est chargé sur la page', outil.charge);
  ok('…et expose ses trois fonctions', outil.fns.length === 3, outil.fns.join(','));

  /* LE contrôle de fond : les COULEURS survivent. On lit les pixels. */
  const pixels = await pg.evaluate(() => FIG.svgEnPng(
      document.querySelector('#brev-chart svg'), 600, 1).then(d => {
    if (!d) return null;
    return new Promise(r => {
      const im = new Image();
      im.onload = function(){
        const c = document.createElement('canvas');
        c.width = im.width; c.height = im.height;
        const x = c.getContext('2d');
        x.drawImage(im, 0, 0);
        const px = x.getImageData(0, 0, c.width, c.height).data;
        const vus = {};
        for (let i = 0; i < px.length; i += 4){
          if (px[i + 3] < 200) continue;
          vus[px[i] + ',' + px[i + 1] + ',' + px[i + 2]] = 1;
        }
        const cles = Object.keys(vus);
        /* Les quatre couleurs des séries doivent se retrouver dans l'image. */
        const proche = (r0, g0, b0) => cles.some(k => {
          const p = k.split(',').map(Number);
          return Math.abs(p[0]-r0) < 26 && Math.abs(p[1]-g0) < 26 && Math.abs(p[2]-b0) < 26;
        });
        r({ largeur: im.width, hauteur: im.height, teintes: cles.length,
            chine: proche(184, 50, 34), us: proche(30, 99, 168),
            europe: proche(196, 124, 26), reste: proche(110, 90, 168),
            blanc: proche(255, 255, 255) });
      };
      im.onerror = function(){ r(null); };
      im.src = d;
    });
  }));
  ok('l’image se produit', !!pixels, pixels && (pixels.largeur + '×' + pixels.hauteur));
  ok('…avec un fond BLANC, jamais transparent', !!pixels && pixels.blanc);
  /* Sans la recopie des styles calculés, l'image serait une silhouette noire :
     ces quatre couleurs viennent d'attributs de présentation ET de la feuille
     de style de la page. */
  ok('…et les quatre couleurs des séries ont survécu à la sortie de la page',
     !!pixels && pixels.chine && pixels.us && pixels.europe && pixels.reste,
     pixels && JSON.stringify({ cn: pixels.chine, us: pixels.us,
                                eu: pixels.europe, reste: pixels.reste }));
  ok('…l’image porte des dizaines de teintes, pas deux',
     !!pixels && pixels.teintes > 30, pixels && pixels.teintes);

  console.log('\n══ 2. Un sélecteur qui rate est NOMMÉ, pas escamoté ══\n');
  const refus = await pg.evaluate(() => Promise.all([
    /* Le conteneur, et non le dessin : l'erreur qui a fait manquer la carte du
       Panorama sans que rien ne le signale. */
    FIG.svgEnPng(document.getElementById('brev-chart'), 400, 1),
    FIG.svgEnPng(null, 400, 1),
    FIG.collecter([{ cle: 'vraie', sel: '#brev-chart svg' },
                   { cle: 'fausse', sel: '#il-nexiste-pas' },
                   { cle: 'conteneur', sel: '#brev-chart' }])
  ]).then(([div, rien, r]) => ({
    div: div, rien: rien,
    faites: Object.keys(r.figures), manques: r.manques
  })));
  ok('un <div> n’est pas accepté comme dessin', refus.div === null);
  ok('…ni un élément absent', refus.rien === null);
  ok('la récolte ne rend que ce qu’elle a produit',
     refus.faites.join(',') === 'vraie', refus.faites.join(','));
  ok('…et NOMME les deux manques', refus.manques.length === 2
     && refus.manques.indexOf('fausse') >= 0
     && refus.manques.indexOf('conteneur') >= 0, refus.manques.join(','));

  console.log('\n══ 3. L’Observatoire s’emporte, dans les deux formats ══\n');
  const bloc = await pg.evaluate(() => ({
    existe: !!document.getElementById('obs-dl'),
    boutons: [...document.querySelectorAll('[data-obs-fmt]')].map(b => b.getAttribute('data-obs-fmt')),
    note: (document.querySelector('#obs-dl .dl-note') || {}).innerText || '',
  }));
  ok('le bloc de téléchargement est sur la page', bloc.existe);
  ok('…avec Word et PDF', bloc.boutons.join(',') === 'docx,pdf', bloc.boutons.join(','));
  ok('…et il annonce que les figures partent avec',
     /cartes et graphiques affichés/i.test(bloc.note));
  ok('…ainsi que la licence sans dérivée',
     /sans dérivée/i.test(bloc.note), bloc.note.slice(-70));

  const fichiers = {};
  for (const fmt of ['docx', 'pdf']) {
    const [dl] = await Promise.all([
      pg.waitForEvent('download', { timeout: 90000 }),
      pg.click('[data-obs-fmt="' + fmt + '"]')
    ]);
    const chemin = '/tmp/claude-0/-home-user-conseilprev/'
                 + 'e6d7dc5d-fcdb-52f0-a89f-586f900c30d5/scratchpad/rec_obs.' + fmt;
    await dl.saveAs(chemin);
    fichiers[fmt] = { nom: dl.suggestedFilename(),
                      taille: require('fs').statSync(chemin).size,
                      octets: require('fs').readFileSync(chemin) };
  }
  ok('le Word se télécharge, et il est lourd de ses images',
     fichiers.docx.taille > 300 * 1024, Math.round(fichiers.docx.taille / 1024) + ' Ko');
  ok('…sous un nom daté et signé', /^CONSEILPREV-observatoire-ia-\d{4}-\d{2}-\d{2}\.docx$/
     .test(fichiers.docx.nom), fichiers.docx.nom);
  ok('…et c’est bien un document Office',
     fichiers.docx.octets.slice(0, 2).toString() === 'PK');
  ok('le PDF aussi', fichiers.pdf.taille > 150 * 1024
     && fichiers.pdf.octets.slice(0, 4).toString() === '%PDF',
     Math.round(fichiers.pdf.taille / 1024) + ' Ko');
  ok('…et il porte ses trois images',
     (fichiers.pdf.octets.toString('latin1').match(/\/Subtype\s*\/Image/g) || []).length === 3,
     (fichiers.pdf.octets.toString('latin1').match(/\/Subtype\s*\/Image/g) || []).length);
  const msg = await pg.evaluate(() => document.getElementById('obs-dl-msg').textContent);
  ok('le message compte les figures jointes', /3 figures jointes/.test(msg), msg);
  ok('…et ne signale aucun manque', !/non jointe/.test(msg));

  console.log('\n══ 4. La vue affichée part avec le document ══\n');
  /* Si le lecteur a basculé les brevets sur « Composition », c'est cette
     image-là qu'il veut — pas une vue canonique qu'il n'a jamais vue. */
  const suit = await pg.evaluate(async () => {
    const png = async () => {
      const d = await FIG.svgEnPng(document.querySelector('#brev-chart svg'), 500, 1);
      return d ? d.length : 0;
    };
    document.querySelector('.bv-vues [data-vue="part"]').click();
    await new Promise(r => setTimeout(r, 400));
    const a = await png();
    document.querySelector('.bv-vues [data-vue="rang"]').click();
    await new Promise(r => setTimeout(r, 400));
    const b = await png();
    return { part: a, rang: b, vue: BV_VUE };
  });
  ok('changer de vue change l’image produite',
     suit.part > 0 && suit.rang > 0 && Math.abs(suit.part - suit.rang) > 2000,
     suit.part + ' vs ' + suit.rang + ' octets');
  ok('…et c’est bien la vue courante qui est saisie', suit.vue === 'rang');

  console.log('\n══ 5. Le Panorama emporte ses cartes aussi ══\n');
  await pg.goto(BASE + '/panorama', { waitUntil: 'networkidle' });
  await pg.waitForFunction(() => document.querySelector('#dl-jeux .dl-b') && window.FIG,
                           null, { timeout: 30000 });
  const pan = await pg.evaluate(() => ({
    outil: typeof FIG === 'object',
    carte: !!document.querySelector('#panmap svg'),
    cres: document.querySelectorAll('.cres-svg').length,
  }));
  ok('l’outil est chargé là aussi', pan.outil);
  ok('…la carte principale est un vrai SVG', pan.carte);
  ok('…et les cartes de résultat existent', pan.cres >= 1, pan.cres);
  const bouton = pg.locator('#dl-jeux .dl-b[data-dl="parc"][data-fmt="pdf"]').first();
  await bouton.scrollIntoViewIfNeeded();
  const [dlp] = await Promise.all([
    pg.waitForEvent('download', { timeout: 90000 }),
    bouton.click()
  ]);
  const cp = '/tmp/claude-0/-home-user-conseilprev/'
           + 'e6d7dc5d-fcdb-52f0-a89f-586f900c30d5/scratchpad/rec_parc.pdf';
  await dlp.saveAs(cp);
  const oct = require('fs').readFileSync(cp);
  ok('le dossier « parc » se télécharge', oct.length > 300 * 1024,
     Math.round(oct.length / 1024) + ' Ko');
  /* AVANT, ce même dossier pesait 130 Ko et ne portait aucune image : le
     sélecteur visait le conteneur. C'est le contrôle qui l'a montré. */
  ok('…et il porte MAINTENANT la carte du parc',
     (oct.toString('latin1').match(/\/Subtype\s*\/Image/g) || []).length >= 1,
     (oct.toString('latin1').match(/\/Subtype\s*\/Image/g) || []).length + ' image(s)');
  ok('aucune erreur JavaScript', err.length === 0, err.slice(0, 2).join(' | '));

  await nav.close();
  console.log('');
  console.log(ko ? ko + ' contrôle(s) en échec\n' : 'tout est vert\n');
  process.exit(ko ? 1 : 0);
})();
