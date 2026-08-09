/* Deux gestes que la carte ne permettait pas, et ce qu'ils exigent.
 *
 * 1. LIRE UNE COUCHE SANS L'AUTRE. La carte superpose deux cent quarante-neuf
 *    centres de données et soixante-douze systèmes d'IA sur la même projection.
 *    On pouvait masquer les centres — jamais les systèmes — et jamais lire les
 *    centres SEULS avec un symbole à leur mesure. Trois états désormais, et le
 *    drapeau grossit quand la place se libère.
 *
 *    Ce qui doit tenir : masquer une couche ne masque PAS son compte. Un parc
 *    qu'on cesse de dessiner ne cesse pas d'exister, et un compteur qui
 *    disparaît avec son symbole laisserait croire le contraire.
 *
 * 2. ALLER DU RANG À SES CHIFFRES. Un podium qui ne conduit nulle part oblige
 *    le lecteur à chercher lui-même la ligne du pays qu'il vient de voir
 *    premier — dans une grille de vingt-quatre entrées, ou après cinq dossiers
 *    de plusieurs écrans. Les puces ET les pastilles chiffrées de la carte
 *    mènent maintenant au détail calculé, chacune dans sa propre section.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = 'http://127.0.0.1:5401';
let ko = 0;
const ok = (n, c, d) => { console.log('  ' + (c ? 'OK ' : 'KO ') + '  ' + n + (d ? ' — ' + d : '')); if (!c) ko++; };

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1440, height: 1150 } });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e)));
  await pg.goto(BASE + '/auth/recette_locale_idf_0123456789abcdef', { waitUntil: 'domcontentloaded' });
  await pg.goto(BASE + '/panorama', { waitUntil: 'networkidle' });
  await pg.waitForFunction(() => document.querySelector('#couche-quoi'), null, { timeout: 30000 });

  console.log('\n══ 1. Trois états, et chacun montre ce qu’il annonce ══\n');
  const etat = async v => {
    await pg.selectOption('#couche-quoi', v);
    await pg.waitForTimeout(850);
    return pg.evaluate(() => ({
      dc: document.querySelectorAll('#dc-couche .dc-pt, #dc-couche .dc-reg').length,
      sia: document.querySelectorAll('#pan-detail .pan-pt').length,
      /* La hauteur du mât porte l'échelle : c'est la cote la plus lisible du
         drapeau, et elle suit le facteur appliqué à toutes les autres. */
      mat: (() => { const m = document.querySelector('#dc-couche .dc-pt rect');
                    return m ? parseFloat(m.getAttribute('height')) : null; })(),
      nDC: (document.getElementById('dc-n') || {}).textContent,
      nSIA: (document.getElementById('sia-n') || {}).textContent,
      couche: typeof COUCHE !== 'undefined' ? COUCHE : '?',
      dcVisible: typeof DC_VISIBLE !== 'undefined' ? DC_VISIBLE : '?',
    }));
  };
  const les2 = await etat('les2');
  ok('« les deux » dessine les centres ET les systèmes',
     les2.dc > 200 && les2.sia > 50, les2.dc + ' centres · ' + les2.sia + ' SIA');
  const dcSeul = await etat('dc');
  ok('« centres seuls » garde les centres', dcSeul.dc === les2.dc, dcSeul.dc);
  ok('…et retire TOUS les panneaux d’IA', dcSeul.sia === 0, dcSeul.sia);
  ok('…et le drapeau grossit, puisque la place se libère',
     dcSeul.mat > les2.mat * 1.4, les2.mat + ' → ' + dcSeul.mat);
  const siaSeul = await etat('sia');
  ok('« systèmes seuls » garde les panneaux', siaSeul.sia === les2.sia, siaSeul.sia);
  ok('…et retire TOUS les centres', siaSeul.dc === 0, siaSeul.dc);
  ok('DC_VISIBLE est DÉRIVÉ de la couche, jamais tenu à part',
     siaSeul.dcVisible === false && dcSeul.dcVisible === true && les2.dcVisible === true,
     [les2.dcVisible, dcSeul.dcVisible, siaSeul.dcVisible].join(' / '));

  console.log('\n══ 2. Masquer une couche ne masque pas son compte ══\n');
  ok('le compte des centres survit à « systèmes seuls »',
     siaSeul.nDC === les2.nDC && +siaSeul.nDC > 200, siaSeul.nDC);
  ok('le compte des systèmes survit à « centres seuls »',
     dcSeul.nSIA === les2.nSIA && +dcSeul.nSIA > 50, dcSeul.nSIA);
  /* Chercher le libellé par son TEXTE trouvait celui du sélecteur, dont les
     options disent elles aussi « centres de données seuls ». On vise le libellé
     qui PORTE le compteur : il n'y en a qu'un, et c'est celui qu'on grise. */
  const grise = await pg.evaluate(() => {
    const par = id => { const b = document.getElementById(id);
      const l = b && b.closest ? b.closest('label') : null;
      return l ? (l.getAttribute('style') || '') : 'LIBELLÉ INTROUVABLE'; };
    return { dc: par('dc-n'), sia: par('sia-n') };
  });
  ok('…mais celui qui n’est pas dessiné est grisé, pas effacé',
     /opacity/.test(grise.dc) && !/opacity/.test(grise.sia),
     'centres «' + grise.dc + '» · SIA «' + grise.sia + '»');
  await pg.selectOption('#couche-quoi', 'les2');
  await pg.waitForTimeout(700);

  console.log('\n══ 3. Le podium d’implantation conduit au détail calculé ══\n');
  await pg.evaluate(() => chargerImplantation());
  await pg.waitForFunction(() => typeof IMPL !== 'undefined' && IMPL && IMPL.pays, null, { timeout: 30000 });
  await pg.waitForTimeout(700);
  const imp = await pg.evaluate(() => {
    renderImplClassement();
    return {
      puces: [...document.querySelectorAll('#imp-classement .imp-podium')]
        .map(b => ({ code: b.getAttribute('data-podium'), t: b.tagName.toLowerCase(),
                     txt: b.innerText.replace(/\n/g, ' · ') })),
      rangs: [...document.querySelectorAll('#imp-classement .cres-rg[data-podium]')]
        .map(g => g.getAttribute('data-podium')),
    };
  });
  ok('trois puces de podium', imp.puces.length === 3, imp.puces.length);
  ok('…et ce sont des BOUTONS, pas des div décoratives',
     imp.puces.every(p => p.t === 'button'), imp.puces.map(p => p.t).join(','));
  ok('…chacune désignant son pays', imp.puces.every(p => /^[A-Z]{2}$/.test(p.code)),
     imp.puces.map(p => p.code).join(','));
  ok('…et disant où elle mène', imp.puces.every(p => /voir le détail/.test(p.txt)),
     imp.puces[0].txt);
  ok('les pastilles chiffrées de la carte mènent aux MÊMES pays',
     JSON.stringify(imp.rangs.slice().sort()) === JSON.stringify(imp.puces.map(p => p.code).sort()),
     imp.rangs.join(',') + ' vs ' + imp.puces.map(p => p.code).join(','));

  const clicImp = await pg.evaluate(() => {
    const b = document.querySelector('#imp-classement .imp-podium');
    const code = b.getAttribute('data-podium');
    b.click();
    const f = document.querySelector('.imp-fiche[data-pays="' + code + '"]');
    return { code: code, deplie: IMPL_DEPLIE, ouverte: !!(f && f.hasAttribute('open')),
             texte: f ? f.innerText.slice(0, 120) : '' };
  });
  await pg.waitForTimeout(500);
  ok('un clic ouvre la fiche du pays', clicImp.ouverte, clicImp.code);
  ok('…et l’état de dépliement suit', clicImp.deplie === clicImp.code, clicImp.deplie);
  ok('…la fiche atteinte porte bien SES chiffres',
     clicImp.texte.length > 40, clicImp.texte.slice(0, 60).replace(/\n/g, ' · '));
  ok('…et un halo signale où l’on vient d’arriver',
     await pg.evaluate(() => !!document.querySelector('.cres-cible')));
  /* DISCRIMINATION : le troisième du podium doit mener au TROISIÈME, pas au
     premier. Un gestionnaire qui ignorerait `data-podium` passerait le premier
     contrôle et échouerait ici. */
  const clic3 = await pg.evaluate(() => {
    const b = [...document.querySelectorAll('#imp-classement .imp-podium')][2];
    const code = b.getAttribute('data-podium');
    b.click();
    return { code: code, deplie: IMPL_DEPLIE };
  });
  ok('la troisième puce mène au troisième pays, pas au premier',
     clic3.deplie === clic3.code && clic3.code !== clicImp.code,
     clic3.code + ' vs ' + clicImp.code);

  console.log('\n══ 4. Le podium d’investissement mène au dossier chiffré ══\n');
  await pg.locator('#fin-go').scrollIntoViewIfNeeded();
  await pg.locator('#fin-go').click();
  await pg.waitForTimeout(4200);
  const fin = await pg.evaluate(() => ({
    puces: [...document.querySelectorAll('.fin-podium')]
      .map(b => ({ code: b.getAttribute('data-podium'), t: b.tagName.toLowerCase(),
                   txt: b.innerText.replace(/\n/g, ' · ') })),
    ancres: [...document.querySelectorAll('[id^="fin-dos-"]')].map(x => x.id),
  }));
  ok('le calcul produit un podium', fin.puces.length >= 3, fin.puces.length);
  ok('…en boutons', fin.puces.every(p => p.t === 'button'));
  ok('chaque pays comparé a son ancre de dossier',
     fin.puces.every(p => fin.ancres.indexOf('fin-dos-' + p.code) >= 0),
     fin.ancres.join(', '));
  ok('…et la puce nomme le pays, comme le titre qu’elle vise',
     !/^\d\. [A-Z]{2} /.test(fin.puces[0].txt), fin.puces[0].txt.slice(0, 40));
  const clicFin = await pg.evaluate(() => {
    const b = document.querySelector('.fin-podium');
    const code = b.getAttribute('data-podium');
    b.click();
    const t = document.getElementById('fin-dos-' + code);
    return { code: code, cible: t ? t.id : null, titre: t ? t.innerText : '' };
  });
  await pg.waitForTimeout(600);
  ok('un clic atteint le dossier du bon pays',
     clicFin.cible === 'fin-dos-' + clicFin.code, clicFin.cible);
  ok('…et ce dossier porte son enveloppe chiffrée',
     /enveloppe/.test(clicFin.titre) && /M€/.test(clicFin.titre), clicFin.titre);
  ok('…avec le halo d’arrivée',
     await pg.evaluate(() => { const t = document.querySelector('.cres-cible');
       return !!t && /^fin-dos-/.test(t.id || ''); }));

  console.log('\n══ 5. LE geste attendu : cliquer le PAYS sur la carte ══\n');
  /* Les contrôles précédents appellent `.click()` sur des <button> : ils
     prouvent que le gestionnaire route bien, jamais qu'un lecteur PEUT
     l'atteindre. C'est ainsi qu'une pastille `pointer-events:none` a pu porter
     un curseur en forme de main sans jamais recevoir un clic. On vise donc ici
     avec la VRAIE souris, à des coordonnées d'écran. */
  /* Viser un pays sur une carte demande deux précautions.
     1. Le centre de la boîte englobante tombe souvent EN MER — la Suède en est
        l'exemple : on balaie jusqu'à toucher le pays lui-même.
     2. La page défile encore quand on mesure. Des coordonnées relevées pendant
        un défilement doux désignent, une demi-seconde plus tard, le pays
        d'à côté : on a vu le clic partir en Espagne au lieu de la France. On
        amène donc la carte à sa place, on ATTEND, puis on mesure — et on
        revérifie le point juste avant de cliquer. */
  const pointer = async (sel) => pg.evaluate((s) => {
    const el = document.querySelector(s);
    if (!el) return null;
    const b = el.getBoundingClientRect();
    for (let fy = 0.5; fy <= 0.86; fy += 0.12) {
      for (let fx = 0.2; fx <= 0.8; fx += 0.1) {
        const x = b.x + b.width * fx, y = b.y + b.height * fy;
        if (document.elementFromPoint(x, y) === el)
          return { x: x, y: y, code: el.getAttribute('data-code') };
      }
    }
    return null;
  }, sel);
  const viser = async (sel) => {
    await pg.evaluate((s) => { const e = document.querySelector(s);
      if (e) e.scrollIntoView({ block: 'center', behavior: 'instant' }); }, sel);
    await pg.waitForTimeout(400);
    const p = await pointer(sel);
    if (!p) return null;
    const surPlace = await pg.evaluate((q) => {
      const t = document.elementFromPoint(q.x, q.y);
      return t ? t.getAttribute('data-code') : null; }, p);
    return surPlace === p.code ? p : await pointer(sel);
  };

  await pg.evaluate(() => { IMPL_DEPLIE = null; renderImplAvis(); });
  const cible = await viser('#imp-classement .cres-pays[data-podium]');
  ok('un pays coloré est atteignable à la souris', !!cible, JSON.stringify(cible));
  if (cible) {
    await pg.mouse.click(cible.x, cible.y);
    await pg.waitForTimeout(700);
    const apres = await pg.evaluate(() => ({ deplie: IMPL_DEPLIE,
      ouverte: !!document.querySelector('.imp-fiche[open]'),
      halo: !!document.querySelector('.imp-fiche.cres-cible') }));
    ok('…et le cliquer ouvre SA fiche, pas celle d’un autre',
       apres.deplie === cible.code, apres.deplie + ' vs ' + cible.code);
    ok('…la fiche est effectivement dépliée', apres.ouverte);
    ok('…et un halo dit où l’on vient d’arriver', apres.halo);
  }

  /* LA PASTILLE, à la souris. C'est elle que le lecteur vise en premier :
     elle porte le chiffre du rang. */
  await pg.evaluate(() => { IMPL_DEPLIE = null; renderImplAvis(); });
  const past = await pg.evaluate(() => {
    const g = document.querySelector('#imp-classement .cres-rg[data-podium]');
    if (!g) return null;
    g.scrollIntoView({ block: 'center' });
    const b = g.getBoundingClientRect();
    return { x: b.x + b.width / 2, y: b.y + b.height / 2,
             code: g.getAttribute('data-podium'),
             pe: getComputedStyle(g).pointerEvents };
  });
  ok('la pastille de rang n’est plus inerte', past && past.pe === 'auto',
     past && past.pe);

  /* Ce que `pointer-events:none` protégeait, et qui doit survivre : la pastille
     est posée sur le centroïde, c'est-à-dire là où l'on vise pour survoler le
     pays. Rendue cliquable, elle doit donc porter l'infobulle de ce pays.
     Ce contrôle passe AVANT le clic : le clic fait défiler la page vers la
     fiche, et la pastille ne serait plus sous le pointeur. */
  if (past) {
    await pg.mouse.move(5, 5);           /* `mouseover` ne naît que d'une ENTRÉE */
    await pg.waitForTimeout(200);
    await pg.mouse.move(past.x, past.y);
    await pg.waitForTimeout(350);
    /* L'infobulle est en position fixe : son `offsetParent` vaut null même
       affichée. C'est la classe `on` qui dit si elle est ouverte. */
    const tip = await pg.evaluate(() => {
      const t = document.querySelector('.cres-tip');
      return t && t.classList.contains('on') ? t.innerText.replace(/\n/g, ' · ') : null; });
    ok('survoler la pastille montre toujours l’infobulle du pays',
       !!tip && tip.length > 10, tip && tip.slice(0, 70));
    ok('…et c’est bien celle du pays de la pastille',
       !!tip && tip.indexOf(await pg.evaluate(c => nomPays(c) || c, past.code)) >= 0,
       tip && tip.slice(0, 40));

    await pg.mouse.click(past.x, past.y);
    await pg.waitForTimeout(700);
    ok('…et la cliquer mène au détail de SON pays',
       (await pg.evaluate(() => IMPL_DEPLIE)) === past.code, past.code);
  }

  console.log('\n══ 6. Le guidage : bleu, clignotement bref, et une consigne ══\n');
  /* Une liaison qui ne se découvre qu'en survolant ne se découvre pas. Trois
     signes la portent — et chacun a ses limites, qu'on vérifie aussi. */
  await pg.evaluate(() => { IMPL_DEPLIE = null; renderImplClassement(); });
  await pg.waitForTimeout(200);
  const signes = await pg.evaluate(() => {
    const q = s => [...document.querySelectorAll('#imp-classement ' + s)];
    const top = q('.cres-pays.cres-top');
    const cs = top.length ? getComputedStyle(top[0]) : null;
    /* Le trait se mesure AU REPOS. Pendant le battement, le style calculé rend
       la valeur interpolée de l'instant — on a lu un bleu délavé à 1,98 px là
       où la règle en pose un franc à 1,5. Un contrôle qui mesure une animation
       en cours ne mesure rien de stable. */
    const t2 = top.length ? top[0].cloneNode(false) : null;
    if (t2) { t2.classList.remove('cres-appel');
              top[0].parentNode.appendChild(t2); }
    const repos = t2 ? getComputedStyle(t2) : null;
    const val = { trait: repos && repos.stroke, epaisseur: repos && parseFloat(repos.strokeWidth) };
    if (t2) t2.remove();
    return {
      nTop: top.length,
      nAppel: q('.cres-pays.cres-appel').length,
      pastAppel: q('.cres-rg.cres-appel').length,
      trait: val.trait, epaisseur: val.epaisseur,
      anim: cs && cs.animationName,
      cycles: cs && cs.animationIterationCount,
      duree: cs && cs.animationDuration,
      /* Le surlignage doit désigner LE PODIUM, pas tous les pays : autrement il
         ne désigne rien. */
      codes: top.map(p => p.getAttribute('data-code')).sort(),
      rangs: q('.cres-rg[data-podium]').map(g => g.getAttribute('data-podium')).sort(),
      autresSoulignes: q('.cres-pays:not(.cres-top)').filter(
        p => getComputedStyle(p).stroke === 'rgb(28, 92, 171)').length,
    };
  });
  ok('trois pays seulement portent le surlignage', signes.nTop === 3, signes.nTop);
  ok('…et ce sont exactement ceux du podium',
     JSON.stringify(signes.codes) === JSON.stringify(signes.rangs),
     signes.codes.join(',') + ' vs ' + signes.rangs.join(','));
  ok('…aucun autre pays n’est cerclé de bleu', signes.autresSoulignes === 0,
     signes.autresSoulignes);
  ok('le surlignage est BLEU, et épais', signes.trait === 'rgb(28, 92, 171)'
     && signes.epaisseur >= 1.4, signes.trait + ' · ' + signes.epaisseur + 'px');
  ok('les trois clignotent', signes.nAppel === 3 && signes.anim === 'cres-appel',
     signes.nAppel + ' · ' + signes.anim);
  ok('…et leurs pastilles avec eux', signes.pastAppel === 3, signes.pastAppel);

  /* LE HALO. Un liseré fin ne suffit pas quand les trois premiers sont
     VOISINS — Suède, Norvège, Finlande ne forment qu'un bloc, et le trait qui
     les sépare est intérieur, donc invisible. */
  const halo = await pg.evaluate(() => {
    const h = [...document.querySelectorAll('#imp-classement .cres-halo')];
    const cs = h.length ? getComputedStyle(h[0]) : null;
    const svg = document.querySelector('#imp-classement .cres-svg');
    const kids = [...svg.children];
    const iHalo = kids.indexOf(h[0]);
    const iPays = kids.findIndex(x => x.classList.contains('cres-pays'));
    const iRang = kids.findIndex(x => x.classList.contains('cres-rg'));
    return { n: h.length, trait: cs && cs.stroke, clics: cs && cs.pointerEvents,
             flou: cs && cs.filter, anim: cs && cs.animationName,
             cycles: cs && cs.animationIterationCount,
             sousLesPays: iHalo >= 0 && iPays >= 0 && iHalo < iPays,
             sousLesRangs: iHalo >= 0 && iRang >= 0 && iHalo < iRang,
             /* Le halo reprend le contour EXACT du pays qu'il désigne. */
             memeContour: h.every(x => [...document.querySelectorAll('#imp-classement .cres-top')]
               .some(p => p.getAttribute('d') === x.getAttribute('d'))) };
  });
  ok('trois halos bleus, un par pays du podium', halo.n === 3
     && halo.trait === 'rgb(28, 92, 171)', halo.n + ' · ' + halo.trait);
  ok('…flous, pour déborder du contour sans le durcir', /blur/.test(halo.flou || ''),
     halo.flou);
  ok('…et posés SOUS les pays et sous les pastilles',
     halo.sousLesPays && halo.sousLesRangs);
  ok('…sur le contour exact du pays désigné, pas un cercle approximatif',
     halo.memeContour);
  /* Un halo qui intercepterait le pointeur volerait le clic au pays : la
     liaison qu'on vient de créer serait cassée par son propre signal. */
  ok('…et il n’intercepte NI le clic NI le survol', halo.clics === 'none', halo.clics);
  ok('le halo bat au même rythme que le reste, et compté',
     halo.anim === 'cres-appel-halo' && +halo.cycles === +signes.cycles,
     halo.anim + ' × ' + halo.cycles);
  /* UN CLIGNOTEMENT SANS FIN EST UNE NUISANCE, et c'est aussi une faute
     d'accessibilité. Il doit être BREF et COMPTÉ. */
  ok('le clignotement est compté, pas infini',
     signes.cycles !== 'infinite' && +signes.cycles > 0 && +signes.cycles <= 8,
     signes.cycles + ' battements de ' + signes.duree);
  ok('…et sa durée totale reste sous huit secondes',
     +signes.cycles * parseFloat(signes.duree) < 8,
     (+signes.cycles * parseFloat(signes.duree)).toFixed(1) + ' s');
  ok('…à plus d’une seconde par battement — jamais un stroboscope',
     parseFloat(signes.duree) >= 1, signes.duree);

  /* Il s'éteint au premier geste : une invitation acceptée cesse d'insister.
     Le voisinage se teste sur une carte TÉMOIN posée pour l'occasion : mesurer
     l'état de la carte de l'enveloppe dépendrait de tout ce que les sections
     précédentes lui ont fait survoler, et le contrôle dirait le hasard. */
  const apaise = await pg.evaluate(() => {
    const t = document.createElement('div');
    t.id = 'recette-temoin';
    t.innerHTML = window.carteResultat(
      { FR: { couleur: '#2D7A47', rang: 1, valeur: 1 } }, { rangsMax: 3 });
    document.body.appendChild(t);
    const avant = t.querySelectorAll('.cres-appel').length;
    const p = document.querySelector('#imp-classement .cres-pays.cres-appel');
    p.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
    const r = { avantTemoin: avant,
                imp: document.querySelectorAll('#imp-classement .cres-appel').length,
                temoin: t.querySelectorAll('.cres-appel').length,
                topRestants: document.querySelectorAll('#imp-classement .cres-pays.cres-top').length,
                classes: document.querySelector('#imp-classement .cres-pays.cres-top').getAttribute('class') };
    t.remove();
    return r;
  });
  ok('un survol éteint le clignotement de CETTE carte', apaise.imp === 0, apaise.imp);
  ok('…et une autre carte clignotait bien au même moment',
     apaise.avantTemoin > 0, apaise.avantTemoin);
  ok('…qu’il n’éteint PAS : chaque carte s’apaise pour elle seule',
     apaise.temoin === apaise.avantTemoin, apaise.temoin);
  ok('…mais le surlignage bleu, lui, demeure',
     apaise.topRestants === 3 && /cres-top/.test(apaise.classes), apaise.classes);

  /* L'INFOBULLE DIT CE QU'UN CLIC FERAIT. Sans cette ligne, elle donnait les
     chiffres sans jamais nommer la porte. */
  const guide = await pg.evaluate(() => {
    const dire = (sel) => {
      const el = document.querySelector(sel);
      if (!el) return null;
      el.dispatchEvent(new MouseEvent('mouseover', { bubbles: true, clientX: 300, clientY: 300 }));
      const t = document.querySelector('.cres-tip');
      return t && t.classList.contains('on') ? t.innerText : null;
    };
    return { top: dire('#imp-classement .cres-pays[data-podium]'),
             gris: dire('#imp-classement .cres-abs'),
             fin: dire('.cres-pays[data-podium]:not(#imp-classement .cres-pays)') };
  });
  ok('l’infobulle du comparateur invite à ouvrir la FICHE',
     /cliquez pour ouvrir la fiche détaillée/i.test(guide.top || ''),
     (guide.top || '').split('\n').pop());
  ok('celle de l’enveloppe invite à ouvrir le DOSSIER CHIFFRÉ',
     /cliquez pour aller au dossier chiffré/i.test(guide.fin || ''),
     (guide.fin || '').split('\n').pop());
  ok('…les deux cartes ne se copient donc pas l’une l’autre',
     (guide.top || '') !== (guide.fin || ''));
  ok('un pays NON calculé ne reçoit aucune invitation',
     !/cliquez pour/i.test(guide.gris || ''),
     (guide.gris || '').split('\n').pop());
  ok('…et il explique quand même pourquoi il est gris',
     /non comparé|hors du référentiel/i.test(guide.gris || ''));
  const notes = await pg.evaluate(() =>
    [...document.querySelectorAll('.cres-note')].map(x => x.innerText));
  ok('les deux notes annoncent le signal bleu',
     notes.filter(t => /cerclés de bleu et clignotent/.test(t)).length >= 2,
     notes.filter(t => /cerclés de bleu/.test(t)).length + ' notes sur ' + notes.length);

  console.log('\n══ 7. Discrimination : l’ancienne carte ne répondait pas ══\n');
  /* On remet la carte dans l'état d'hier — pastilles inertes, pays sans cible —
     et on refait EXACTEMENT les mêmes gestes. */
  const avant = await pg.evaluate(async () => {
    IMPL_DEPLIE = null; renderImplAvis();
    const st = document.createElement('style');
    st.id = 'recette-avant';
    st.textContent = '.cres-rg{pointer-events:none !important}';
    document.head.appendChild(st);
    const r = {};
    document.querySelectorAll('#imp-classement .cres-pays[data-podium]')
      .forEach(p => p.removeAttribute('data-podium'));
    r.paysCiblables = document.querySelectorAll('#imp-classement .cres-pays[data-podium]').length;
    return r;
  });
  ok('la carte d’hier n’offrait aucun pays cliquable', avant.paysCiblables === 0);
  if (cible) await pg.mouse.click(cible.x, cible.y);
  if (past) await pg.mouse.click(past.x, past.y);
  await pg.waitForTimeout(600);
  ok('…et ni le pays ni la pastille ne conduisaient nulle part',
     (await pg.evaluate(() => IMPL_DEPLIE)) === null,
     await pg.evaluate(() => IMPL_DEPLIE));
  await pg.evaluate(() => { const s = document.getElementById('recette-avant');
    if (s) s.remove(); renderImplClassement(); });
  await pg.waitForTimeout(400);
  ok('la vraie carte est bien revenue',
     (await pg.evaluate(() =>
       document.querySelectorAll('#imp-classement .cres-pays[data-podium]').length)) > 10);

  console.log('\n══ 8. Une cible n’est offerte que si elle existe ══\n');
  const gris = await pg.evaluate(() => ({
    absents: document.querySelectorAll('#imp-classement .cres-abs[data-podium]').length,
    horsUE: document.querySelectorAll('#imp-classement .cres-hue[data-podium]').length,
    curseurGris: (() => { const g = document.querySelector('#imp-classement .cres-abs');
      return g ? getComputedStyle(g).cursor : null; })(),
    /* `aller:false` doit retirer la cible ET le rôle de bouton : une carte de
       contrôle fabriquée ici prouve la règle sans dépendre des données. */
    faux: (() => {
      const d = document.createElement('div');
      d.innerHTML = window.carteResultat(
        { FR: { couleur: '#2D7A47', rang: 1, valeur: 1, aller: false },
          DE: { couleur: '#C47C1A', rang: 2, valeur: 2 } }, { rangsMax: 3 });
      return { sansCible: !!d.querySelector('.cres-pays[data-code="FR"]:not([data-podium])'),
               roleFR: d.querySelector('.cres-pays[data-code="FR"]').getAttribute('role'),
               avecCible: !!d.querySelector('.cres-pays[data-code="DE"][data-podium]'),
               roleDE: d.querySelector('.cres-pays[data-code="DE"]').getAttribute('role'),
               pastilleFR: d.querySelector('.cres-rg[data-code="FR"]').hasAttribute('data-podium') };
    })(),
  }));
  ok('un pays NON comparé n’est pas cliquable', gris.absents === 0, gris.absents);
  ok('…ni un pays hors de l’Union', gris.horsUE === 0, gris.horsUE);
  ok('…et leur curseur ne promet rien', gris.curseurGris !== 'pointer', gris.curseurGris);
  ok('un pays sans destination ne s’annonce pas cliquable',
     gris.faux.sansCible && gris.faux.roleFR === 'img', gris.faux.roleFR);
  ok('…sa pastille non plus', gris.faux.pastilleFR === false);
  ok('…tandis qu’un pays qui en a une la porte, en rôle de bouton',
     gris.faux.avecCible && gris.faux.roleDE === 'button', gris.faux.roleDE);

  console.log('\n══ 9. Au clavier, et malgré un filtre actif ══\n');
  await pg.evaluate(() => { IMPL_DEPLIE = null; renderImplAvis(); });
  const clav = await pg.evaluate(() => {
    const p = document.querySelector('#imp-classement .cres-pays[data-podium]');
    p.focus();
    return { code: p.getAttribute('data-podium'),
             focalise: document.activeElement === p };
  });
  ok('un pays prend le focus au clavier', clav.focalise, clav.code);
  await pg.keyboard.press('Enter');
  await pg.waitForTimeout(600);
  ok('…et Entrée mène au même détail que la souris',
     (await pg.evaluate(() => IMPL_DEPLIE)) === clav.code, clav.code);

  /* LE PIÈGE DU FILTRE. Un filtre actif peut avoir écarté la fiche visée : le
     lecteur serait conduit vers un bloc où son pays n'est pas. */
  const filtre = await pg.evaluate(() => {
    const codes = [...document.querySelectorAll('#imp-classement .cres-pays[data-podium]')]
      .map(p => p.getAttribute('data-podium'));
    const vise = codes[0], autre = codes.find(c => c !== vise);
    TF.imp = { pays: autre };                       /* on cache exprès le pays visé */
    IMPL_DEPLIE = null; renderImplAvis();
    const avantClic = !!document.querySelector('.imp-fiche[data-pays="' + vise + '"]');
    implVoirPays(vise);
    /* La barre se redessine et repose ses clés à vide : ce n'est donc pas
       l'objet qu'il faut lire, mais l'absence de valeur ACTIVE. */
    return { vise: vise, autre: autre, avantClic: avantClic,
             apresClic: !!document.querySelector('.imp-fiche[data-pays="' + vise + '"]'),
             actifs: Object.keys(TF.imp || {}).filter(k => TF.imp[k]),
             fiches: document.querySelectorAll('.imp-fiche').length };
  });
  ok('le filtre cachait bien la fiche visée', filtre.avantClic === false,
     filtre.vise + ' masqué par le filtre ' + filtre.autre);
  ok('…et l’aller la fait tout de même apparaître', filtre.apresClic, filtre.vise);
  ok('…en levant le filtre, visiblement, plutôt qu’en échouant en silence',
     filtre.actifs.length === 0, filtre.actifs.join(','));
  ok('…et le bloc reprend bien toutes ses fiches', filtre.fiches > 10, filtre.fiches);

  console.log('\n══ 10. La même liaison sur la carte de l’enveloppe ══\n');
  const cibleFin = await viser('.cres-pays[data-podium]:not(#imp-classement .cres-pays)');
  ok('un pays comparé y est atteignable à la souris', !!cibleFin,
     JSON.stringify(cibleFin));
  if (cibleFin) {
    await pg.mouse.click(cibleFin.x, cibleFin.y);
    await pg.waitForTimeout(800);
    const arr = await pg.evaluate((c) => {
      const t = document.getElementById('fin-dos-' + c);
      return { existe: !!t, halo: !!(t && t.classList.contains('cres-cible')),
               titre: t ? t.innerText : '' };
    }, cibleFin.code);
    ok('…et le cliquer atteint SON dossier chiffré',
       arr.existe && arr.halo, cibleFin.code + ' → ' + arr.titre.slice(0, 46));
    ok('…lequel porte bien une enveloppe en euros',
       /enveloppe/.test(arr.titre) && /M€/.test(arr.titre), arr.titre.slice(0, 50));
  }
  const dits = await pg.evaluate(() => ({
    imp: (document.querySelector('#imp-classement .cres-note') || {}).innerText || '',
    fin: [...document.querySelectorAll('.cres-note')].map(x => x.innerText).join(' ~~ '),
  }));
  ok('la carte du classement DIT que ses pays sont cliquables',
     /Cliquez un pays coloré/.test(dits.imp), dits.imp.slice(-90));
  ok('…et celle de l’enveloppe aussi',
     (dits.fin.match(/Cliquez un pays coloré/g) || []).length >= 2,
     (dits.fin.match(/Cliquez un pays coloré/g) || []).length + ' mentions');

  console.log('\n══ 11. Ce que ces deux gestes ne devaient PAS casser ══\n');
  const reste = await pg.evaluate(() => ({
    horizon: !!document.getElementById('dc-horizon'),
    fond: !!document.getElementById('vue-fond'),
    legende: !!document.getElementById('lg-ouvrir'),
    cartes: document.querySelectorAll('[data-cres]').length,
    lignes: document.querySelectorAll('#imp-classement .imp-l').length,
  }));
  ok('le curseur d’année est toujours là', reste.horizon);
  ok('le choix du fond de carte aussi', reste.fond);
  ok('…et le bouton de légende', reste.legende);
  ok('les deux cartes de résultat coexistent', reste.cartes >= 2, reste.cartes);
  ok('le classement complet reste accessible ligne à ligne',
     reste.lignes > 10, reste.lignes + ' lignes');
  ok('aucune erreur JavaScript', err.length === 0, err.slice(0, 2).join(' | '));

  await nav.close();
  console.log('');
  console.log(ko ? ko + ' contrôle(s) en échec\n' : 'tout est vert\n');
  process.exit(ko ? 1 : 0);
})();
