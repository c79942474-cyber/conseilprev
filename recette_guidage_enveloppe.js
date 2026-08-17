/* Le guidage de la vue Enveloppe : phases qui battent, flèche qui pointe.
 *
 * CE QU'ON PROTÈGE, ET LA FAUTE QUE CHAQUE CONTRÔLE EMPÊCHE :
 *
 *   1. LE GUIDAGE EST ARMÉ D'EMBLÉE. Il partait éteint : sur une page de
 *      quatorze écrans, le lecteur devait d'abord trouver le bouton
 *      « Guidez-moi » pour qu'il se passe quoi que ce soit. Un parcours guidé
 *      qu'il faut débloquer soi-même ne guide personne.
 *   2. LES PHASES NON VALIDÉES BATTENT, les validées non. Sans cela le fil ne
 *      distinguait le fait du reste que par une couleur, immobile.
 *   3. LA CADENCE RESTE SOUS LE SEUIL DE SÉCURITÉ. Au-delà de trois éclats par
 *      seconde, un clignotement devient un risque pour les personnes
 *      photosensibles. Ce contrôle mesure la durée du cycle : ce n'est pas un
 *      détail de style, c'est une limite.
 *   4. LE POINT QUI DÉCIDE — LA FLÈCHE POINTE DANS LA BONNE DIRECTION. Vers le
 *      bas quand le bloc est plus loin, vers le HAUT quand on l'a dépassé. Une
 *      flèche qui pointerait toujours vers le bas ferait descendre quelqu'un
 *      qui devait remonter, et ruinerait la confiance dans tout le guidage.
 *   5. ELLE SE TAIT QUAND ELLE N'A RIEN À DIRE : bloc sous les yeux, parcours
 *      terminé, ou guide fermé par le lecteur.
 *   6. MOUVEMENT RÉDUIT : plus rien ne bouge, et rien n'est perdu.
 *
 *     BASE=http://127.0.0.1:5510 node recette_guidage_enveloppe.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5510';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
let ko = 0;
const ok = (n, c, d) => { console.log('  ' + (c ? 'OK ' : 'KO ') + '  ' + n + (d ? ' — ' + d : '')); if (!c) ko++; };
const titre = t => console.log('\n══ ' + t + ' ══\n');

(async () => {
  const nav = await chromium.launch();

  const ouvrir = async (reduit) => {
    const ctx = await nav.newContext({ viewport: { width: 1500, height: 950 },
      reducedMotion: reduit ? 'reduce' : 'no-preference' });
    await ctx.addInitScript(() => {
      Object.defineProperty(navigator, 'webdriver', { get: () => false });
      Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
      Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
    });
    const pg = await ctx.newPage();
    await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
    await pg.waitForTimeout(300);
    await pg.goto(BASE + '/enveloppe', { waitUntil: 'domcontentloaded' });
    await pg.waitForFunction(() => !!document.querySelector('#fin-fil .fin-fil-p'),
                             null, { timeout: 30000 }).catch(() => {});
    await pg.waitForTimeout(700);
    return pg;
  };

  const pg = await ouvrir(false);
  const err = [];
  pg.on('pageerror', e => err.push(String(e).slice(0, 130)));

  const fleche = () => pg.evaluate(() => {
    const f = document.getElementById('fin-fleche-guide');
    if (!f) return null;
    return {
      sens: f.getAttribute('data-sens'),
      fleche: (f.querySelector('.fin-fg-a') || {}).textContent || '',
      texte: f.textContent.replace(/\s+/g, ' ').trim(),
      aria: f.getAttribute('aria-label') || '',
      fixe: getComputedStyle(f).position,
      fermeture: !!f.querySelector('.fin-fg-x')
    };
  });

  // ── 1 ────────────────────────────────────────────────────────────────────
  titre('1. Le guidage est armé d’emblée — plus rien à débloquer');

  ok('le mode pas à pas est actif dès l’arrivée',
     await pg.evaluate(() => window.FIN_GUIDE === true));
  const f0 = await fleche();
  ok('une flèche de guidage est posée sans rien cliquer', !!f0,
     f0 ? f0.texte.slice(0, 50) : 'aucune');
  ok('…elle ne défile pas avec la page', !!f0 && f0.fixe === 'fixed', f0 && f0.fixe);
  ok('…elle nomme l’étape et son rang', !!f0 && /Étape \d+ sur \d+/.test(f0.texte),
     f0 && f0.texte.slice(0, 46));
  ok('…et elle porte sa propre fermeture', !!f0 && f0.fermeture);

  // ── 2 ────────────────────────────────────────────────────────────────────
  titre('2. Ce qui attend un clic bat en bleu, ce qui est validé s’encadre de vert');

  const bat = await pg.evaluate(() => {
    const lire = (sel) => [...document.querySelectorAll(sel)].map(e => {
      const s = getComputedStyle(e);
      const b = e.closest('button');
      const sb = b ? getComputedStyle(b) : null;
      return { nom: s.animationName, duree: s.animationDuration,
               iter: s.animationIterationCount, fond: s.backgroundColor,
               cadre: sb ? sb.borderTopColor : null,
               epaisseur: sb ? parseFloat(sb.borderTopWidth) : 0 };
    });
    /* On résout le jeton de charte EN L'APPLIQUANT : lu brut il vaut « #2D7A47 »
       alors que la bordure calculée vaut « rgb(45, 122, 71) », et comparer les
       deux écritures ferait échouer un contrôle sur une couleur pourtant juste. */
    const jeton = (n) => {
      const s = document.createElement('span');
      s.style.color = 'var(' + n + ')';
      document.body.appendChild(s);
      const c = getComputedStyle(s).color;
      s.remove();
      return c;
    };
    return {
      reste: lire('#fin-fil .fin-e.reste .fin-e-n'),
      cours: lire('#fin-fil .fin-e.cours .fin-e-n'),
      fait: lire('#fin-fil .fin-e.fait .fin-e-n'),
      bleu: jeton('--blue'), vert: jeton('--green')
    };
  });
  ok('les étapes qui restent battent',
     bat.reste.length > 0 && bat.reste.every(x => x.nom !== 'none'),
     bat.reste.length + ' pastille(s), animation ' + (bat.reste[0] || {}).nom);
  ok('l’étape COURANTE bat aussi, et différemment',
     bat.cours.length === 1 && bat.cours[0].nom !== 'none'
       && bat.cours[0].nom !== (bat.reste[0] || {}).nom,
     (bat.cours[0] || {}).nom);
  ok('les étapes VALIDÉES ne battent pas — c’est ce qui les distingue',
     bat.fait.length > 0 && bat.fait.every(x => x.nom === 'none'),
     bat.fait.length + ' validée(s), animation ' + (bat.fait[0] || {}).nom);

  /* LES CADRANS EN ATTENTE SONT BLEUS — pas gris. On ne compare pas à une
     teinte écrite en dur, qui interdirait de nuancer la charte : on mesure la
     TEINTE. Comparer les canaux ne suffisait pas — un bleu très clair
     (#DCE9F7) n'a que 27 points d'écart entre rouge et bleu et se serait fait
     rejeter, alors que sa teinte vaut 211°, franchement bleue. On exige aussi
     un minimum de saturation, sinon un gris neutre passerait par accident. */
  const bleuit = (c) => {
    const [r, g, b] = c.match(/[\d.]+/g).slice(0, 3).map(Number);
    const max = Math.max(r, g, b), min = Math.min(r, g, b), d = max - min;
    if (d < 12) return false;
    let h;
    if (max === r) h = 60 * (((g - b) / d) % 6);
    else if (max === g) h = 60 * ((b - r) / d + 2);
    else h = 60 * ((r - g) / d + 4);
    if (h < 0) h += 360;
    return h >= 185 && h <= 255;
  };
  ok('les cadrans en attente d’un clic sont BLEUS, pas gris',
     bat.reste.every(x => bleuit(x.fond)) && bat.cours.every(x => bleuit(x.fond)),
     'reste ' + (bat.reste[0] || {}).fond + ' · courante ' + (bat.cours[0] || {}).fond);

  /* LE CADRE VERT. Il ne suffit pas qu'il soit vert quelque part : il doit
     être vert LÀ et nulle part ailleurs, sinon il ne distingue rien. */
  const memeCouleur = (a, b) => a && b
    && a.match(/[\d.]+/g).slice(0, 3).join() === b.match(/[\d.]+/g).slice(0, 3).join();
  ok('les étapes validées portent un cadre VERT',
     bat.fait.length > 0 && bat.fait.every(x => memeCouleur(x.cadre, bat.vert)),
     bat.fait.length + ' validée(s), cadre ' + (bat.fait[0] || {}).cadre
       + ' pour --green ' + bat.vert);
  ok('…et il est assez épais pour se voir à distance',
     bat.fait.every(x => x.epaisseur >= 2), (bat.fait[0] || {}).epaisseur + 'px');
  ok('…tandis que les étapes NON validées ne l’ont pas — sinon il ne dirait rien',
     bat.reste.every(x => !memeCouleur(x.cadre, bat.vert))
       && bat.cours.every(x => !memeCouleur(x.cadre, bat.vert)),
     'reste ' + (bat.reste[0] || {}).cadre + ' · courante ' + (bat.cours[0] || {}).cadre);

  // ── 3 ────────────────────────────────────────────────────────────────────
  titre('3. Sécurité : cadence bornée, et le chiffre lisible à CHAQUE phase');

  const cycles = [...bat.reste, ...bat.cours].map(x => parseFloat(x.duree));
  const plusRapide = Math.min.apply(null, cycles.concat([
    parseFloat(await pg.evaluate(() => {
      const f = document.getElementById('fin-fleche-guide');
      return f ? getComputedStyle(f).animationDuration : '99s';
    }))]));
  ok('aucun clignotement ne descend sous 0,34 s de cycle',
     plusRapide >= 0.34,
     'cycle le plus court : ' + plusRapide + ' s (' + (1 / plusRapide).toFixed(2) + ' Hz)');
  ok('…et la cadence retenue reste lente, donc lisible',
     plusRapide >= 1.0, plusRapide + ' s');

  /* LE CONTRÔLE QUI PROTÈGE LE PLUS. Faire varier l'opacité est le geste
     évident pour « faire clignoter » — et il rend le chiffre illisible une
     demi-seconde sur deux. On relit donc les images-clés elles-mêmes, on
     résout les variables de charte en les appliquant à une sonde, et on
     mesure le contraste fond/chiffre À CHAQUE PHASE. */
  const phases = await pg.evaluate((noms) => {
    const lum = (c) => {
      const v = c.match(/[\d.]+/g).slice(0, 3).map(Number).map(x => {
        x /= 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4);
      });
      return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2];
    };
    const contraste = (a, b) => {
      const [h, l] = [lum(a), lum(b)].sort((p, q) => q - p);
      return (h + 0.05) / (l + 0.05);
    };
    const kfs = [];
    for (const ss of document.styleSheets) {
      let rr; try { rr = ss.cssRules } catch (e) { continue }
      for (const r of rr) if (r.type === 7 && noms.includes(r.name)) kfs.push(r);
    }
    const sonde = document.createElement('span');
    document.body.appendChild(sonde);
    const out = kfs.map(kf => ({
      nom: kf.name,
      images: [...kf.cssRules].map(k => {
        sonde.style.cssText = k.style.cssText;
        const s = getComputedStyle(sonde);
        return { cle: k.keyText,
                 declareFond: !!(k.style.background || k.style.backgroundColor),
                 declareEncre: !!k.style.color,
                 declareOpacite: !!k.style.opacity,
                 fond: s.backgroundColor, encre: s.color,
                 contraste: contraste(s.backgroundColor, s.color) };
      })
    }));
    sonde.remove();
    return out;
  }, ['fin-bat-reste', 'fin-bat-cours']);

  const toutes = phases.flatMap(p => p.images);
  ok('les deux battements sont bien relus depuis la feuille de style',
     phases.length === 2 && toutes.length >= 4,
     phases.map(p => p.nom + ' (' + p.images.length + ' images)').join(' · '));
  ok('LE DISQUE ET LE CHIFFRE CHANGENT TOUS LES DEUX à chaque image',
     toutes.length > 0 && toutes.every(i => i.declareFond && i.declareEncre),
     toutes.filter(i => !(i.declareFond && i.declareEncre)).length + ' image(s) incomplète(s)');
  ok('…et le chiffre change vraiment de couleur d’une phase à l’autre',
     phases.every(p => new Set(p.images.map(i => i.encre)).size >= 2),
     phases.map(p => p.nom + ' : ' + [...new Set(p.images.map(i => i.encre))].length
       + ' encre(s)').join(' · '));
  const pire = Math.min.apply(null, toutes.map(i => i.contraste));
  ok('LE CHIFFRE RESTE LISIBLE À CHAQUE PHASE — 4,5:1 au minimum',
     pire >= 4.5,
     'phase la plus faible : ' + pire.toFixed(2) + ':1 — '
       + toutes.map(i => i.cle + ' ' + i.contraste.toFixed(2)).join(' · '));
  ok('…et aucun battement ne se joue sur l’opacité, qui efface le chiffre',
     toutes.every(i => !i.declareOpacite),
     toutes.filter(i => i.declareOpacite).length + ' image(s) à opacité variable');

  // ── 4 : LE POINT QUI DÉCIDE ──────────────────────────────────────────────
  titre('4. LE POINT QUI DÉCIDE : la flèche pointe dans la bonne direction');

  /* On se place AU-DESSUS du bloc courant : elle doit inviter à descendre. */
  await pg.evaluate(() => window.scrollTo(0, 0));
  await pg.waitForTimeout(450);
  const enHaut = await fleche();
  ok('au-dessus du bloc, la flèche pointe VERS LE BAS',
     !!enHaut && enHaut.sens === 'bas' && enHaut.fleche.indexOf('▼') >= 0,
     enHaut ? enHaut.sens + ' ' + enHaut.fleche : 'aucune');
  ok('…et son libellé accessible le dit aussi',
     !!enHaut && /plus bas/.test(enHaut.aria), enHaut && enHaut.aria);

  /* On descend BIEN AU-DELÀ : elle doit inviter à remonter. */
  await pg.evaluate(() => window.scrollTo(0, document.body.scrollHeight - 1200));
  await pg.waitForTimeout(600);
  const enBas = await fleche();
  ok('sous le bloc, la flèche pointe VERS LE HAUT',
     !!enBas && enBas.sens === 'haut' && enBas.fleche.indexOf('▲') >= 0,
     enBas ? enBas.sens + ' ' + enBas.fleche : 'aucune');
  ok('…et son libellé accessible le dit aussi',
     !!enBas && /plus haut/.test(enBas.aria), enBas && enBas.aria);
  ok('LES DEUX SENS SONT BIEN DIFFÉRENTS — la flèche ne pointe pas toujours pareil',
     !!enHaut && !!enBas && enHaut.sens !== enBas.sens,
     (enHaut || {}).sens + ' puis ' + (enBas || {}).sens);

  titre('5. Elle se tait quand elle n’a rien à dire, et elle mène où elle dit');

  /* Cliquer la flèche doit conduire au bloc — et donc la faire disparaître. */
  await pg.evaluate(() => window.scrollTo(0, 0));
  await pg.waitForTimeout(400);
  const cible = await pg.evaluate(() => FIN_ETAPES[finPasCourant()].cible);
  await pg.click('#fin-fleche-guide');
  await pg.waitForTimeout(1400);
  const arrive = await pg.evaluate((id) => {
    const e = document.getElementById(id);
    if (!e) return null;
    const r = e.getBoundingClientRect();
    return { visible: r.top > -200 && r.top < window.innerHeight };
  }, cible);
  ok('cliquer la flèche mène au bloc de l’étape', !!arrive && arrive.visible);
  ok('…et une fois le bloc sous les yeux, elle s’efface',
     (await fleche()) === null);

  /* La fermeture doit tenir. */
  await pg.evaluate(() => window.scrollTo(0, 0));
  await pg.waitForTimeout(450);
  ok('elle revient quand on s’éloigne du bloc', (await fleche()) !== null);
  await pg.click('.fin-fg-x');
  await pg.waitForTimeout(300);
  ok('le lecteur peut la fermer', (await fleche()) === null);
  await pg.evaluate(() => window.scrollTo(0, 4000));
  await pg.waitForTimeout(500);
  ok('…et elle ne revient pas sans qu’il le demande', (await fleche()) === null);

  /* Couper le guidage retire tout ; le rallumer rouvre la flèche fermée. */
  await pg.evaluate(() => { document.getElementById('fin-fil-g').click(); });
  await pg.waitForTimeout(400);
  ok('couper le guidage éteint le mode', await pg.evaluate(() => window.FIN_GUIDE === false));
  await pg.evaluate(() => { document.getElementById('fin-fil-g').click(); });
  await pg.waitForTimeout(500);
  await pg.evaluate(() => window.scrollTo(0, 4000));
  await pg.waitForTimeout(500);
  ok('le rallumer rouvre la flèche, même fermée auparavant',
     (await fleche()) !== null);

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  // ── 6 ────────────────────────────────────────────────────────────────────
  titre('6. Mouvement réduit : plus rien ne bouge, et rien n’est perdu');

  const pg2 = await ouvrir(true);
  const immobile = await pg2.evaluate(() => {
    const lum = (c) => {
      const v = c.match(/[\d.]+/g).slice(0, 3).map(Number).map(x => {
        x /= 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4);
      });
      return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2];
    };
    const contraste = (a, b) => {
      const [h, l] = [lum(a), lum(b)].sort((p, q) => q - p);
      return (h + 0.05) / (l + 0.05);
    };
    const lire = (sel) => [...document.querySelectorAll(sel)].map(e => {
      const s = getComputedStyle(e);
      const b = e.closest('button');
      return { anim: s.animationName, fond: s.backgroundColor, encre: s.color,
               opacite: parseFloat(s.opacity),
               contraste: contraste(s.backgroundColor, s.color),
               cadre: b ? getComputedStyle(b).borderTopColor : null };
    });
    const f = document.getElementById('fin-fleche-guide');
    return {
      pastilles: lire('#fin-fil .fin-e-n'),
      attente: lire('#fin-fil .fin-e.reste .fin-e-n, #fin-fil .fin-e.cours .fin-e-n'),
      fait: lire('#fin-fil .fin-e.fait .fin-e-n'),
      cours: lire('#fin-fil .fin-e.cours .fin-e-n'),
      fleche: f ? getComputedStyle(f).animationName : null,
      flechePresente: !!f
    };
  });
  const memeVert = (c) => c && bat.vert
    && c.match(/[\d.]+/g).slice(0, 3).join()
       === bat.vert.match(/[\d.]+/g).slice(0, 3).join();
  ok('aucune pastille ne bat', immobile.pastilles.every(x => x.anim === 'none'),
     immobile.pastilles.filter(x => x.anim !== 'none').map(x => x.anim).join(', ')
       || 'toutes immobiles');
  ok('la flèche ne bat pas non plus',
     immobile.fleche === null || immobile.fleche === 'none', immobile.fleche);
  ok('…MAIS elle est toujours là : on ne prive pas de guidage',
     immobile.flechePresente);
  ok('…et l’étape courante reste distinguée', immobile.cours.length === 1);
  /* CE QUI EST REFUSÉ, C'EST LE MOUVEMENT — PAS L'INFORMATION. Les cadrans en
     attente gardent leur bleu et leur lisibilité, et le cadre vert du validé
     ne dépend d'aucune animation : il doit survivre tel quel. */
  ok('les cadrans en attente gardent leur bleu, sans être atténués',
     immobile.attente.length > 0
       && immobile.attente.every(x => bleuit(x.fond) && x.opacite === 1),
     immobile.attente.map(x => x.fond + ' à ' + x.opacite).slice(0, 2).join(' · '));
  ok('…et leur chiffre reste lisible — 4,5:1 au minimum',
     immobile.attente.every(x => x.contraste >= 4.5),
     'le plus faible : '
       + Math.min.apply(null, immobile.attente.map(x => x.contraste)).toFixed(2) + ':1');
  ok('le cadre vert du validé survit au mouvement réduit',
     immobile.fait.length > 0 && immobile.fait.every(x => memeVert(x.cadre)),
     immobile.fait.length + ' validée(s), cadre ' + (immobile.fait[0] || {}).cadre);
  await pg2.close();

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec') + '\n');
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
