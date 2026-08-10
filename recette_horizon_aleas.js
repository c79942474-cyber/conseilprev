/* L'horizon des aléas dans le comparateur — ce que le geste doit produire.
 *
 * 1. CHANGER D'HORIZON DOIT CHANGER QUELQUE CHOSE. Un bouton qui s'allume sans
 *    déplacer une note serait pire qu'absent : il ferait croire à une
 *    projection. On mesure donc les notes AVANT et APRÈS, sur les six critères
 *    d'aléas — et on vérifie qu'elles baissent.
 *
 * 2. ET NE DOIT PAS EN CHANGER D'AUTRES. Le prix de l'électricité de 2050
 *    n'est pas connu. Les dix critères de socle doivent rester rigoureusement
 *    identiques, sinon la page laisserait croire qu'on a projeté un prix. C'est
 *    le contrôle central de ce fichier.
 *
 * 3. LE DOUBLE COMPTAGE DOIT SE DIRE. Trois aléas recouvrent un critère XDI
 *    déjà présent. Mettre les deux à poids fort compte deux fois le même
 *    risque ; l'avertissement doit apparaître quand c'est le cas, et
 *    DISPARAÎTRE quand ça ne l'est plus.
 *
 * 4. LA SATURATION DOIT SE LIRE. Le Portugal est au cran maximal du feu dès
 *    2030 : son écart 2030-2050 vaut zéro. Sans mention, ce zéro se lit « ça se
 *    calme ». La fiche doit écrire que l'échelle bute.
 *
 * 5. LES TROIS PAYS QUI N'AVAIENT RIEN doivent afficher leurs six aléas.
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
  await pg.waitForFunction(() => typeof IMPL !== 'undefined' && IMPL && IMPL.pays,
                           null, { timeout: 40000 });
  await pg.waitForTimeout(400);

  console.log('\n══ 1. Le sélecteur existe, et il dit ce qu’il ne fait pas ══\n');

  const hz = await pg.evaluate(() => {
    const b = [...document.querySelectorAll('#imp-horizon [data-horizon]')];
    return {
      n: b.length,
      valeurs: b.map(x => x.getAttribute('data-horizon')),
      actif: b.filter(x => x.classList.contains('on')).map(x => x.textContent.trim()),
      presses: b.map(x => x.getAttribute('aria-pressed')),
      portee: (document.querySelector('.imp-hz-p') || {}).textContent || '',
      mer: (document.querySelector('.imp-hz-m') || {}).textContent || '',
      courant: typeof IMPL_HORIZON !== 'undefined' ? IMPL_HORIZON : null,
    };
  });
  ok('deux horizons sont proposés', hz.n === 2 && hz.valeurs.join(',') === '2030,2050',
     hz.valeurs.join(','));
  ok('un seul est actif à la fois', hz.actif.length === 1, hz.actif.join(','));
  ok('…et c’est 2030 au chargement', hz.actif[0] === '2030' && hz.courant === 2030);
  ok('l’état est porté pour les lecteurs d’écran',
     hz.presses.filter(p => p === 'true').length === 1, hz.presses.join(','));
  // LE point d'honnêteté : la portée est écrite, pas sous-entendue.
  ok('la page écrit que l’horizon ne déplace QUE les aléas',
     /aléas/i.test(hz.portee) && /prix/i.test(hz.portee), hz.portee.slice(0, 90));
  ok('…et pourquoi : projeter le prix serait l’inventer',
     /invent/i.test(hz.portee));
  ok('le niveau de la mer de l’horizon est affiché', /mer/i.test(hz.mer), hz.mer.slice(0, 70));
  ok('…et 2030 est signalé comme CALCULÉ, non publié par le GIEC',
     /CALCULÉE/.test(hz.mer), hz.mer.slice(0, 120));

  console.log('\n══ 2. Changer d’horizon change les aléas… ══\n');

  const notes = () => pg.evaluate(() => {
    const o = {};
    IMPL.pays.forEach(p => { o[p.pays] = Object.assign({}, p.notes); });
    return { notes: o, horizon: IMPL.horizon, version: IMPL.version };
  });
  const av = await notes();

  await pg.click('#imp-horizon [data-horizon="2050"]');
  await pg.waitForFunction(() => IMPL && IMPL.horizon === 2050, null, { timeout: 20000 });
  await pg.waitForTimeout(300);
  const ap = await notes();

  ok('le référentiel servi est bien celui de 2050', ap.horizon === 2050, ap.horizon);
  const ALEAS = ['alea_submersion', 'alea_feu', 'alea_secheresse', 'alea_pluie',
                 'alea_glissement', 'alea_hydrologie'];
  const bouge = [];
  const monte = [];
  Object.keys(av.notes).forEach(p => ALEAS.forEach(c => {
    const a = av.notes[p][c], b = ap.notes[p][c];
    if (a !== b) bouge.push(p + '/' + c);
    if (b > a) monte.push(p + '/' + c);
  }));
  ok('des dizaines de notes d’aléas ont changé', bouge.length > 60, bouge.length + ' cases');
  // Le sens compte : un aléa qui S'AMÉLIORE en 2050 serait suspect.
  ok('…et aucune ne s’améliore', monte.length === 0, monte.slice(0, 4).join(' · '));

  console.log('\n══ 3. …et ne change RIEN d’autre ══\n');

  const SOCLE = ['carbone', 'mix', 'eau', 'climat', 'prix', 'parc',
                 'climat_physique', 'feux', 'inondations', 'pipeline'];
  const socleBouge = [];
  Object.keys(av.notes).forEach(p => SOCLE.forEach(c => {
    if (av.notes[p][c] !== ap.notes[p][c]) socleBouge.push(p + '/' + c);
  }));
  ok('les dix critères de socle sont IDENTIQUES aux deux horizons',
     socleBouge.length === 0, socleBouge.slice(0, 5).join(' · '));
  ok('…y compris le prix, que personne ne sait projeter',
     Object.keys(av.notes).every(p => av.notes[p].prix === ap.notes[p].prix));
  ok('le millésime du référentiel ne change pas non plus',
     av.version === ap.version, av.version + ' → ' + ap.version);
  ok('le nombre de pays est le même',
     Object.keys(av.notes).length === Object.keys(ap.notes).length);

  console.log('\n══ 4. Le double comptage se dit, et se tait ══\n');

  const doublon = () => pg.evaluate(() => {
    const b = document.getElementById('imp-doublon');
    return { cache: !b || b.hidden, txt: b ? b.textContent : '' };
  });
  const regle = (cle, v) => pg.evaluate(([c, x]) => {
    const r = document.querySelector('input[data-critere="' + c + '"]');
    r.value = x; r.dispatchEvent(new Event('input', { bubbles: true }));
  }, [cle, v]);

  // Par défaut, feu (1) et feux XDI (1) sont tous deux > 0 : l'avertissement doit être là.
  let d = await doublon();
  ok('au chargement, l’avertissement de double comptage est VISIBLE',
     !d.cache, d.txt.slice(0, 60));
  ok('…il nomme les deux critères en cause',
     /recouvre/.test(d.txt) && /Feu de forêt/i.test(d.txt), d.txt.slice(0, 110));
  // Un avertissement qui dit « attention » sans dire quoi arbitrer est du bruit.
  ok('…et il dit ce qui distingue les deux familles',
     /vingt-sept/.test(d.txt) && /vingt-neuf/.test(d.txt));

  await regle('feux', 0); await regle('inondations', 0); await regle('eau', 0);
  await regle('climat_physique', 0);
  await pg.waitForTimeout(150);
  d = await doublon();
  ok('les critères XDI à 0, l’avertissement DISPARAÎT', d.cache, d.txt.slice(0, 60));

  await regle('feux', 3);
  await pg.waitForTimeout(150);
  d = await doublon();
  ok('…et revient dès qu’un recouvrement réapparaît', !d.cache);
  ok('…en ne citant QUE le recouvrement réellement actif',
     /Feu de forêt/i.test(d.txt) && !/Précipitations/i.test(d.txt), d.txt.slice(0, 110));

  // Un aléa sans recouvrement ne doit jamais déclencher l'avertissement.
  await regle('feux', 0);
  await regle('alea_glissement', 4);
  await pg.waitForTimeout(150);
  d = await doublon();
  ok('le glissement de terrain, qui ne recouvre rien, n’alerte pas', d.cache);

  console.log('\n══ 5. Les poids d’aléas pèsent réellement sur le classement ══\n');

  const premier = () => pg.evaluate(() => {
    const l = IMPL.pays.map(p => ({ p: p.pays, s: implScore(p) }))
      .filter(x => x.s !== null).sort((a, b) => b.s - a.s);
    return { tete: l[0].p, scores: l.slice(0, 5).map(x => x.p + ':' + x.s).join(' ') };
  });
  await pg.evaluate(() => {
    ['alea_submersion', 'alea_feu', 'alea_secheresse', 'alea_pluie',
     'alea_glissement', 'alea_hydrologie'].forEach(c => {
      const r = document.querySelector('input[data-critere="' + c + '"]');
      r.value = 0; r.dispatchEvent(new Event('input', { bubbles: true }));
    });
  });
  await pg.waitForTimeout(150);
  const sansAleas = await premier();
  await pg.click('[data-fam-poids="3"]');
  await pg.waitForTimeout(200);
  const avecAleas = await premier();
  ok('le bouton « tous à 3 » règle les six curseurs d’un coup',
     await pg.evaluate(() => ['alea_submersion', 'alea_feu', 'alea_secheresse',
       'alea_pluie', 'alea_glissement', 'alea_hydrologie']
       .every(c => IMPL_POIDS[c] === 3)));
  ok('…et le classement s’en trouve modifié',
     sansAleas.scores !== avecAleas.scores,
     'sans : ' + sansAleas.scores + ' | avec : ' + avecAleas.scores);
  await pg.click('[data-fam-poids="0"]');
  await pg.waitForTimeout(150);
  ok('« tous à 0 » les remet tous à zéro',
     await pg.evaluate(() => ['alea_submersion', 'alea_feu', 'alea_secheresse',
       'alea_pluie', 'alea_glissement', 'alea_hydrologie']
       .every(c => IMPL_POIDS[c] === 0)));

  console.log('\n══ 6. La fiche d’un pays montre ses six aléas ══\n');

  const fiche = async code => {
    await pg.evaluate(c => { IMPL_DEPLIE = c; renderImplAvis(); }, code);
    await pg.waitForTimeout(200);
    return pg.evaluate(c => {
      const f = document.querySelector('.imp-fiche[data-pays="' + c + '"] .imp-aleas');
      if (!f) return null;
      return {
        n: f.querySelectorAll('.imp-al').length,
        noms: [...f.querySelectorAll('.imp-al-n')].map(e => e.textContent.trim()),
        conf: [...f.querySelectorAll('.imp-al-c')].map(e => e.textContent.trim()),
        sat: !!f.querySelector('.imp-al-sat'),
        satTxt: (f.querySelector('.imp-al-sat') || {}).textContent || '',
        up: f.querySelectorAll('.imp-al-up').length,
        so: [...f.querySelectorAll('.imp-al.so .imp-al-h')].map(e => e.textContent.trim()),
        mer: (f.querySelector('.imp-al-mer') || {}).textContent || '',
        dom: f.querySelectorAll('.imp-al.dominant').length,
        txt: f.textContent,
      };
    }, code);
  };

  for (const c of ['GB', 'CH', 'SE']) {
    const f = await fiche(c);
    ok(c + ' affiche bien six aléas', f && f.n === 6, f ? f.n : 'aucun bloc');
    ok('…chacun avec sa confiance déclarée',
       f && f.conf.length === 6 && f.conf.every(x => /Confiance/.test(x)));
  }

  const ch = await fiche('CH');
  ok('la Suisse porte « pays sans littoral » et non une case vide',
     ch.so.length === 1 && /sans littoral/.test(ch.so[0]), ch.so.join(''));
  const pt = await fiche('PT');
  // LE contresens à empêcher : un écart nul ne veut pas dire que ça se calme.
  ok('le Portugal signale une case SATURÉE', pt.sat, pt.satTxt);
  ok('…et dit que c’est l’échelle qui bute, pas l’aléa qui se calme',
     /échelle bute/.test(pt.satTxt) && /ne se calme pas/.test(pt.satTxt), pt.satTxt);
  const fi = await fiche('FI');
  ok('la Finlande porte son mouvement du sol', /relèvement/.test(fi.mer), fi.mer.slice(0, 70));
  ok('…et le fait que le niveau relatif y BAISSE', /BAISSE/.test(fi.mer));
  const nl = await fiche('NL');
  ok('les Pays-Bas portent au contraire un enfoncement',
     /enfoncement/.test(nl.mer), nl.mer.slice(0, 70));
  ok('chaque fiche désigne son ou ses aléas dominants', nl.dom >= 1 && ch.dom >= 1,
     'NL ' + nl.dom + ' · CH ' + ch.dom);

  console.log('\n══ 7. Ce que cette manœuvre ne devait PAS casser ══\n');

  const etat = await pg.evaluate(() => ({
    fiches: document.querySelectorAll('.imp-fiche').length,
    curseurs: document.querySelectorAll('#imp-ponderations input[type=range]').length,
    familles: document.querySelectorAll('#imp-ponderations .imp-fam').length,
    tips: document.querySelectorAll('#imp-ponderations .ttip').length,
    classement: document.querySelectorAll('#imp-classement .cres-pays').length,
  }));
  ok('les seize curseurs sont là', etat.curseurs === 16, etat.curseurs);
  ok('…répartis en deux familles', etat.familles === 2, etat.familles);
  ok('…et chacun porte son explication', etat.tips === 16, etat.tips);
  ok('les fiches pays sont toujours servies', etat.fiches >= 20, etat.fiches);
  ok('la carte du classement est toujours dessinée', etat.classement > 20, etat.classement);
  ok('aucune erreur de script sur toute la manœuvre', err.length === 0, err.slice(0, 2).join(' | '));

  // Le retour à 2030 doit être instantané ET juste : le cache par horizon ne
  // doit pas servir le mauvais document.
  await pg.click('#imp-horizon [data-horizon="2030"]');
  await pg.waitForFunction(() => IMPL && IMPL.horizon === 2030, null, { timeout: 20000 });
  const retour = await notes();
  ok('revenir à 2030 restitue exactement les notes de départ',
     JSON.stringify(retour.notes) === JSON.stringify(av.notes));
  ok('…et le bouton actif suit', await pg.evaluate(() =>
     document.querySelector('#imp-horizon [data-horizon="2030"]').classList.contains('on')
     && !document.querySelector('#imp-horizon [data-horizon="2050"]').classList.contains('on')));

  await nav.close();
  console.log(ko ? '\n' + ko + ' contrôle(s) en échec\n' : '\ntout est vert\n');
  process.exit(ko ? 1 : 0);
})();
