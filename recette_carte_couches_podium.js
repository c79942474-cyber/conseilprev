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

  console.log('\n══ 5. Ce que ces deux gestes ne devaient PAS casser ══\n');
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
