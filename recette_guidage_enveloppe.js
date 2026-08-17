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
  titre('2. Les neuf étapes sont des BOUTONS : bleus battants, verts une fois faits');

  /* CE QUE CETTE SECTION SUIT DÉSORMAIS. L'état était porté par un disque de
     vingt pixels dans une carte blanche : de loin — la distance à laquelle on
     embrasse les neuf d'un coup — neuf rectangles blancs se ressemblent. Le
     BOUTON ENTIER porte donc la couleur, et c'est lui qui bat. Ces contrôles
     visaient le disque ; ils visent maintenant le bouton, sans quoi ils
     testeraient un élément qui ne décide plus de rien. */

  /* ON PRODUIT UNE ÉTAPE VALIDÉE AVANT D'EN PARLER. Cette section s'appuyait
     sur l'étape 1, verte dès le chargement parce que la puissance arrive
     pré-remplie à 100 MW. Le fil ne crédite plus une valeur par défaut — un
     avancement qui se félicite d'un formulaire livré rempli ne veut rien dire
     — et il n'y a donc plus AUCUNE étape verte à l'arrivée. Les contrôles ne
     sont pas devenus faux : leur mise en scène l'était. On donne une vraie
     réponse, et on observe ce qu'elle produit. */
  await pg.evaluate(() => {
    const e = document.getElementById('fin-mw');
    e.value = '250';
    e.dispatchEvent(new Event('input', { bubbles: true }));
  });
  await pg.waitForTimeout(800);
  ok('une réponse du lecteur produit bien une étape validée à observer',
     await pg.evaluate(() =>
       document.querySelectorAll('#fin-fil .fin-e.fait').length === 1),
     await pg.evaluate(() =>
       document.querySelectorAll('#fin-fil .fin-e.fait').length + ' validée(s)'));

  const bat = await pg.evaluate(() => {
    const lire = (sel) => [...document.querySelectorAll(sel)].map(b => {
      const sb = getComputedStyle(b);
      const d = b.querySelector('.fin-e-n');
      const sd = d ? getComputedStyle(d) : null;
      const t = b.querySelector('.fin-e-c b');
      return { nom: sb.animationName, duree: sb.animationDuration,
               iter: sb.animationIterationCount, fond: sb.backgroundColor,
               encre: t ? getComputedStyle(t).color : sb.color,
               disque: sd ? sd.backgroundColor : null,
               chiffre: sd ? sd.color : null,
               cadre: sb.borderTopColor,
               epaisseur: parseFloat(sb.borderTopWidth) || 0 };
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
      reste: lire('#fin-fil .fin-e.reste button'),
      cours: lire('#fin-fil .fin-e.cours button'),
      fait: lire('#fin-fil .fin-e.fait button'),
      bleu: jeton('--blue'), vert: jeton('--green')
    };
  });
  ok('les étapes qui restent battent',
     bat.reste.length > 0 && bat.reste.every(x => x.nom !== 'none'),
     bat.reste.length + ' bouton(s), animation ' + (bat.reste[0] || {}).nom);
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
  ok('les boutons en attente d’un clic sont BLEUS, pas blancs',
     bat.reste.every(x => bleuit(x.fond)) && bat.cours.every(x => bleuit(x.fond)),
     'reste ' + (bat.reste[0] || {}).fond + ' · courante ' + (bat.cours[0] || {}).fond);
  /* LE DISQUE S'INVERSE SUR FOND PLEIN : bleu sur bleu, il disparaîtrait. */
  ok('…et leur disque s’inverse, pour ne pas se fondre dans le bouton',
     bat.reste.every(x => !bleuit(x.disque)) && bat.cours.every(x => !bleuit(x.disque)),
     'disque ' + (bat.reste[0] || {}).disque + ', chiffre ' + (bat.reste[0] || {}).chiffre);

  /* LE CADRE VERT. Il ne suffit pas qu'il soit vert quelque part : il doit
     être vert LÀ et nulle part ailleurs, sinon il ne distingue rien. */
  const memeCouleur = (a, b) => a && b
    && a.match(/[\d.]+/g).slice(0, 3).join() === b.match(/[\d.]+/g).slice(0, 3).join();
  ok('LES ÉTAPES VALIDÉES SONT VERTES — le bouton entier, pas un liseré',
     bat.fait.length > 0 && bat.fait.every(x => memeCouleur(x.fond, bat.vert)),
     bat.fait.length + ' validée(s), fond ' + (bat.fait[0] || {}).fond
       + ' pour --green ' + bat.vert);
  ok('…leur disque aussi s’inverse, chiffre vert sur blanc',
     bat.fait.every(x => memeCouleur(x.chiffre, bat.vert)),
     'disque ' + (bat.fait[0] || {}).disque + ', chiffre ' + (bat.fait[0] || {}).chiffre);
  ok('…tandis que les étapes NON validées ne sont PAS vertes — sinon rien ne dirait',
     bat.reste.every(x => !memeCouleur(x.fond, bat.vert))
       && bat.cours.every(x => !memeCouleur(x.fond, bat.vert)),
     'reste ' + (bat.reste[0] || {}).fond + ' · courante ' + (bat.cours[0] || {}).fond);
  /* L'ÉTAPE COURANTE NE SE FOND PAS DANS LES SUIVANTES : sur neuf boutons du
     même bleu, il faut encore savoir lequel est le prochain. */
  ok('…et l’étape courante se distingue par un liseré, malgré le même bleu',
     bat.cours.length === 1 && bat.cours[0].epaisseur >= 2
       && bat.reste.every(x => x.epaisseur < 2),
     'courante ' + (bat.cours[0] || {}).epaisseur + 'px contre '
       + (bat.reste[0] || {}).epaisseur + 'px');

  // ── 3 ────────────────────────────────────────────────────────────────────
  titre('3. Sécurité : cadence bornée, et le LIBELLÉ lisible à CHAQUE phase');

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
     évident pour « faire clignoter » — et il rend le texte illisible une
     demi-seconde sur deux. On relit donc les images-clés elles-mêmes, on
     résout les variables de charte en les appliquant à une sonde, et on
     mesure le contraste À CHAQUE PHASE.

     LE BATTEMENT PORTE MAINTENANT SUR LE BOUTON ENTIER : ce qui doit rester
     lisible n'est plus un chiffre sur un disque, mais le TITRE et le
     SOUS-TITRE de l'étape sur le fond du bouton. Le texte, lui, garde sa
     couleur d'un bout à l'autre — la faire varier ferait clignoter les mots
     eux-mêmes. On mesure donc les deux encres réellement appliquées contre
     chacun des fonds du cycle. */
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
    /* LES DEUX ENCRES RÉELLEMENT APPLIQUÉES au titre et au sous-titre : c'est
       contre elles que le fond doit tenir, pas contre une valeur supposée. */
    const b0 = document.querySelector('#fin-fil .fin-e button');
    const encres = b0
      ? [getComputedStyle(b0.querySelector('.fin-e-c b')).color,
         getComputedStyle(b0.querySelector('.fin-e-c i')).color]
      : ['rgb(255, 255, 255)'];
    const sonde = document.createElement('span');
    document.body.appendChild(sonde);
    const out = kfs.map(kf => ({
      nom: kf.name,
      images: [...kf.cssRules].map(k => {
        sonde.style.cssText = k.style.cssText;
        const s = getComputedStyle(sonde);
        return { cle: k.keyText,
                 declareFond: !!(k.style.background || k.style.backgroundColor),
                 declareOpacite: !!k.style.opacity,
                 fond: s.backgroundColor,
                 encre: encres.join(' + '),
                 contraste: Math.min.apply(null,
                   encres.map(e => contraste(s.backgroundColor, e))) };
      })
    }));
    sonde.remove();
    return out;
  }, ['fin-bat-reste', 'fin-bat-cours']);

  const toutes = phases.flatMap(p => p.images);
  ok('les deux battements sont bien relus depuis la feuille de style',
     phases.length === 2 && toutes.length >= 4,
     phases.map(p => p.nom + ' (' + p.images.length + ' images)').join(' · '));
  ok('CHAQUE IMAGE PEINT LE FOND — sans quoi le bouton ne battrait pas',
     toutes.length > 0 && toutes.every(i => i.declareFond),
     toutes.filter(i => !i.declareFond).length + ' image(s) sans fond');
  ok('…et le fond change vraiment d’une phase à l’autre',
     phases.every(p => new Set(p.images.map(i => i.fond)).size >= 2),
     phases.map(p => p.nom + ' : ' + [...new Set(p.images.map(i => i.fond))].length
       + ' fond(s)').join(' · '));
  const pire = Math.min.apply(null, toutes.map(i => i.contraste));
  ok('LE LIBELLÉ RESTE LISIBLE À CHAQUE PHASE — 4,5:1 au minimum',
     pire >= 4.5,
     'phase la plus faible : ' + pire.toFixed(2) + ':1 — '
       + toutes.map(i => i.cle + ' ' + i.contraste.toFixed(2)).join(' · '));
  ok('…et aucun battement ne se joue sur l’opacité, qui efface le texte',
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

  // ── 6 ────────────────────────────────────────────────────────────────────
  titre('6. Les BOUTONS parlent la même langue que les pastilles');

  /* CE QUE CETTE SECTION PROTÈGE. Le bandeau disait, en haut, ce qui restait à
     faire — pendant que les boutons qui le font, plus bas, gardaient tous la
     même apparence. Le lecteur descendait dans la page et n'avait plus aucun
     repère. Les commandes portent donc l'état de LEUR étape : bleu battant
     tant qu'elle reste, vert immobile une fois franchie.

     ET L'ÉTAT VIENT DU FIL, PAS D'UNE SECONDE COMPTABILITÉ : un bouton vert
     au-dessus d'une pastille qui reste, et plus personne ne croirait ni l'un
     ni l'autre. C'est le dernier contrôle de la section qui l'éprouve. */
  const lireCmd = () => pg.evaluate(() => {
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
    const faites = (window.finFaites ? window.finFaites() : null);
    return (window.FIN_ETAPES || []).filter(e => e.commande).map(e => {
      const b = document.querySelector(e.commande);
      if (!b) return { cle: e.cle, absent: true };
      const s = getComputedStyle(b);
      const av = getComputedStyle(b, '::before');
      const pastille = [...document.querySelectorAll('#fin-fil .fin-e')]
        .map((li, i) => ({ li, e: (window.FIN_ETAPES || [])[i] }))
        .filter(x => x.e && x.e.cle === e.cle)[0];
      return {
        cle: e.cle, n: e.n,
        att: b.classList.contains('fin-cmd-att'),
        fait: b.classList.contains('fin-cmd-fait'),
        fond: s.backgroundColor, encre: s.color,
        anim: s.animationName, duree: parseFloat(s.animationDuration) || 0,
        contraste: contraste(s.backgroundColor, s.color),
        marque: (av.content || '').replace(/["']/g, '').trim(),
        titre: b.getAttribute('title') || '',
        pastilleFaite: pastille ? pastille.li.classList.contains('fait') : null,
        selonFil: faites ? !!faites[e.cle] : null
      };
    });
  });

  const c0 = await lireCmd();
  ok('chaque étape à commande a bien son bouton sur la page',
     c0.length > 0 && c0.every(x => !x.absent),
     c0.filter(x => x.absent).map(x => x.cle).join(', ') || c0.length + ' bouton(s)');
  ok('AUCUN bouton ne reste sans repère d’état',
     c0.every(x => x.att || x.fait),
     c0.filter(x => !(x.att || x.fait)).map(x => x.cle).join(', ') || 'tous marqués');
  ok('au départ, les commandes non franchies BATTENT en bleu',
     c0.filter(x => x.att).length > 0
       && c0.filter(x => x.att).every(x => x.anim !== 'none'
            && (() => { const [r, , b] = x.fond.match(/[\d.]+/g).map(Number);
                        return b > r + 30; })()),
     c0.filter(x => x.att).length + ' en attente, ' + (c0[0] || {}).fond);
  ok('…à la MÊME cadence que les pastilles, sous le seuil de sécurité',
     c0.filter(x => x.att).every(x => x.duree >= 1.0),
     'cycle ' + (c0.find(x => x.att) || {}).duree + ' s');
  ok('…et le libellé reste lisible : 4,5:1 au minimum',
     c0.every(x => x.contraste >= 4.5),
     'le plus faible : '
       + Math.min.apply(null, c0.map(x => x.contraste)).toFixed(2) + ':1');
  ok('…chaque bouton DIT son rang et son état, il ne le peint pas seulement',
     c0.every(x => /Étape \d+ sur \d+/.test(x.titre)),
     (c0[0] || {}).titre);

  /* LE CONTRÔLE QUI PROTÈGE LE PLUS, ET IL A MANQUÉ AU PREMIER JET. Mesurer la
     couleur du bouton à un instant donné ne dit rien de ce qu'il devient à
     mi-cycle : un battement ramené à l'opacité — le geste évident — passait
     tous les contrôles ci-dessus tout en rendant le libellé illisible une
     demi-seconde sur deux. On relit donc les images-clés elles-mêmes, on
     résout les variables de charte sur une sonde, et on mesure le contraste
     du libellé contre CHAQUE fond du cycle.

     Le libellé, lui, garde sa couleur d'un bout à l'autre : sur un bouton, la
     faire varier ferait clignoter le texte lui-même. C'est le fond et le halo
     qui portent le battement — d'où une règle différente de celle des
     pastilles, où c'est le chiffre qui doit bouger. */
  const phasesCmd = await pg.evaluate(() => {
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
    let kf = null;
    for (const ss of document.styleSheets) {
      let rr; try { rr = ss.cssRules } catch (e) { continue }
      for (const r of rr) if (r.type === 7 && r.name === 'fin-cmd-bat') kf = r;
    }
    if (!kf) return null;
    const b = document.querySelector('#moe-go');
    const encre = b ? getComputedStyle(b).color : 'rgb(255,255,255)';
    const sonde = document.createElement('span');
    document.body.appendChild(sonde);
    const images = [...kf.cssRules].map(k => {
      sonde.style.cssText = k.style.cssText;
      const s = getComputedStyle(sonde);
      return { cle: k.keyText,
               opacite: !!k.style.opacity,
               fond: s.backgroundColor,
               contraste: contraste(s.backgroundColor, encre) };
    });
    sonde.remove();
    return { encre: encre, images: images };
  });
  ok('le battement des commandes est relu depuis la feuille de style',
     !!phasesCmd && phasesCmd.images.length >= 2,
     phasesCmd ? phasesCmd.images.length + ' image(s)' : 'keyframes introuvables');
  ok('AUCUNE PHASE NE SE JOUE SUR L’OPACITÉ — elle effacerait le libellé',
     !!phasesCmd && phasesCmd.images.every(i => !i.opacite),
     phasesCmd
       ? phasesCmd.images.filter(i => i.opacite).length + ' image(s) à opacité variable'
       : '');
  ok('LE LIBELLÉ RESTE LISIBLE À CHAQUE PHASE DU CYCLE — 4,5:1 au minimum',
     !!phasesCmd && phasesCmd.images.every(i => i.contraste >= 4.5),
     phasesCmd
       ? phasesCmd.images.map(i => i.cle + ' ' + i.contraste.toFixed(2)).join(' · ')
       : '');

  /* LE POINT QUI DÉCIDE : franchir une étape doit faire basculer SA commande,
     et elle seule. Une bascule globale colorerait tout en vert au premier
     calcul et ne dirait plus rien. */
  await pg.evaluate(() => document.getElementById('fin-go').click());
  await pg.waitForFunction(() => window.FIN_DERNIER && window.FIN_DERNIER(),
    null, { timeout: 60000 });
  await pg.waitForTimeout(3000);
  const c1 = await lireCmd();
  const calc = c1.filter(x => x.cle === 'calculer')[0];
  ok('FRANCHIR UNE ÉTAPE FAIT PASSER SA COMMANDE AU VERT',
     !!calc && calc.fait && !calc.att, calc && calc.fond);
  ok('…et le vert ne bat pas — c’est ce qui le distingue',
     !!calc && calc.anim === 'none', calc && calc.anim);
  ok('…il porte une marque, pas seulement une couleur',
     !!calc && /✓/.test(calc.marque), (calc && calc.marque) || 'aucune');
  ok('…et les AUTRES commandes restent bleues : la bascule n’est pas globale',
     c1.filter(x => x.cle !== 'calculer').every(x => x.att && !x.fait),
     c1.filter(x => x.fait).map(x => x.cle).join(', '));
  ok('…son infobulle bascule elle aussi', !!calc && /faite/i.test(calc.titre),
     calc && calc.titre);
  ok('LE BOUTON NE PEUT PAS CONTREDIRE SA PASTILLE — même source d’état',
     c1.every(x => x.selonFil === null || x.fait === x.selonFil),
     c1.filter(x => x.selonFil !== null && x.fait !== x.selonFil)
       .map(x => x.cle).join(', ') || 'tous d’accord');
  ok('…ni le bandeau des étapes, qui se coche de la même façon',
     c1.every(x => x.pastilleFaite === null || x.fait === x.pastilleFaite),
     c1.filter(x => x.pastilleFaite !== null && x.fait !== x.pastilleFaite)
       .map(x => x.cle).join(', ') || 'tous d’accord');

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  // ── 7 ────────────────────────────────────────────────────────────────────
  titre('7. Mouvement réduit : plus rien ne bouge, et rien n’est perdu');

  const pg2 = await ouvrir(true);
  /* MÊME MISE EN SCÈNE QU'À LA SECTION 2 : cette page est neuve, donc sans
     aucune étape validée — le fil ne crédite plus la valeur par défaut. Sans
     réponse du lecteur, il n'y aurait rien de vert à observer, et le contrôle
     du vert en mouvement réduit ne prouverait rien. */
  await pg2.evaluate(() => {
    const e = document.getElementById('fin-mw');
    if (e) { e.value = '250'; e.dispatchEvent(new Event('input', { bubbles: true })); }
  });
  await pg2.waitForTimeout(800);
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
    const lire = (sel) => [...document.querySelectorAll(sel)].map(b => {
      const s = getComputedStyle(b);
      const t = b.querySelector('.fin-e-c b');
      const encre = t ? getComputedStyle(t).color : s.color;
      return { anim: s.animationName, fond: s.backgroundColor, encre: encre,
               opacite: parseFloat(s.opacity),
               contraste: contraste(s.backgroundColor, encre),
               cadre: s.backgroundColor };
    });
    const f = document.getElementById('fin-fleche-guide');
    return {
      pastilles: lire('#fin-fil .fin-e button'),
      attente: lire('#fin-fil .fin-e.reste button, #fin-fil .fin-e.cours button'),
      fait: lire('#fin-fil .fin-e.fait button'),
      cours: lire('#fin-fil .fin-e.cours button'),
      fleche: f ? getComputedStyle(f).animationName : null,
      flechePresente: !!f
    };
  });
  const memeVert = (c) => c && bat.vert
    && c.match(/[\d.]+/g).slice(0, 3).join()
       === bat.vert.match(/[\d.]+/g).slice(0, 3).join();
  ok('aucun bouton d’étape ne bat', immobile.pastilles.every(x => x.anim === 'none'),
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
  ok('les boutons en attente gardent leur bleu plein, sans être atténués',
     immobile.attente.length > 0
       && immobile.attente.every(x => bleuit(x.fond) && x.opacite === 1),
     immobile.attente.map(x => x.fond + ' à ' + x.opacite).slice(0, 2).join(' · '));
  ok('…et leur libellé reste lisible — 4,5:1 au minimum',
     immobile.attente.every(x => x.contraste >= 4.5),
     'le plus faible : '
       + Math.min.apply(null, immobile.attente.map(x => x.contraste)).toFixed(2) + ':1');
  ok('le vert du validé survit au mouvement réduit',
     immobile.fait.length > 0 && immobile.fait.every(x => memeVert(x.cadre)),
     immobile.fait.length + ' validée(s), fond ' + (immobile.fait[0] || {}).cadre);

  /* LES COMMANDES AUSSI : le battement est refusé, le REPÈRE ne l'est pas. */
  const cmdRed = await pg2.evaluate(() =>
    (window.FIN_ETAPES || []).filter(e => e.commande).map(e => {
      const b = document.querySelector(e.commande);
      if (!b) return null;
      const s = getComputedStyle(b);
      return { cle: e.cle, anim: s.animationName, fond: s.backgroundColor,
               marque: b.classList.contains('fin-cmd-att')
                 || b.classList.contains('fin-cmd-fait'),
               contour: s.outlineStyle + ' ' + s.outlineWidth };
    }).filter(Boolean));
  ok('aucune commande ne bat en mouvement réduit',
     cmdRed.length > 0 && cmdRed.every(x => x.anim === 'none'),
     cmdRed.filter(x => x.anim !== 'none').map(x => x.cle).join(', ') || 'toutes immobiles');
  ok('…MAIS elles gardent leur état : on ne prive pas de repère',
     cmdRed.every(x => x.marque));
  ok('…et celles qui restent à faire reçoivent un contour, faute de battement',
     cmdRed.some(x => /solid/.test(x.contour)),
     (cmdRed[0] || {}).contour);
  await pg2.close();

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec') + '\n');
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
