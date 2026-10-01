/* LA COULEUR DES ÉCRANS NIST ET OWASP, MESURÉE DANS UN VRAI NAVIGATEUR.
 *
 * POURQUOI UNE RECETTE ET PAS SEULEMENT DES RÈGLES PYTHON. Les règles lisent
 * la feuille de style ; elles ne peuvent pas dire QUI GAGNE. Le défaut trouvé
 * ici était exactement celui-là : les règles d'état étaient écrites, correctes,
 * et perdaient la cascade contre `.nist-cats li` — la barre restait grise et
 * le fichier avait l'air juste. Seul `getComputedStyle` le dit.
 *
 * AUCUNE ÉCRITURE : tout vit dans la mémoire de l'écran. Rien n'est prélevé.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = 'http://127.0.0.1:9941', TOKEN = 'recette_locale_idf_0123456789abcdef';
const pad = (s, n) => String(s == null ? '—' : s).padEnd(n).slice(0, n);
let verdict = 0;
const dit = (ok, quoi, detail) => {
  if (!ok) verdict = 1;
  console.log('  ' + (ok ? '✓' : '✗') + ' ' + pad(quoi, 58) + (detail == null ? '' : detail));
};
/* L'OPACITÉ D'UNE BARRE SE LIT DANS LA COULEUR CALCULÉE : « rgba(r,g,b,a) ».
   On la sort pour pouvoir dire que l'échelle MONTE, et non qu'elle est
   simplement « colorée » — une échelle qui descendrait serait colorée aussi. */
const alpha = (c) => {
  const m = /rgba?\(([^)]+)\)/.exec(c || '');
  if (!m) return null;
  const p = m[1].split(',').map(x => parseFloat(x));
  return p.length > 3 ? p[3] : 1;
};
const teinte = (c) => {
  const m = /rgba?\(([^)]+)\)/.exec(c || '');
  return m ? m[1].split(',').slice(0, 3).map(x => parseInt(x, 10)).join(' ') : null;
};

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1400, height: 1200 } });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e).slice(0, 160)));
  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg.waitForFunction(() => typeof go === 'function', null, { timeout: 40000 });
  /* UNE RÉPONSE PAR ÉTAT : une grille vide ne montre aucune couleur d'état,
     et la recette conclurait « tout est gris » sur une page sans réponses. */
  await pg.evaluate(() => {
    localStorage.setItem('cp-sentinel-nist-profil-v1', JSON.stringify({
      'GOVERN 1': 'absent', 'GOVERN 2': 'amorce', 'GOVERN 3': 'tenu',
      'GOVERN 4': 'prouve', 'GOVERN 5': 'sans_objet' }));
    localStorage.setItem('cp-sentinel-owasp-declares-v1', JSON.stringify({
      LLM01: 'non', LLM02: 'partiel', LLM03: 'oui', LLM04: 'sans_objet' }));
    localStorage.setItem('cp-sentinel-nist-genai-v1', JSON.stringify({
      genai: true, risques: [2, 5, 8], actions: {} }));
  });
  await pg.reload({ waitUntil: 'commit' });
  await pg.waitForFunction(() => typeof go === 'function', null, { timeout: 40000 });
  await pg.waitForTimeout(2500);

  /* ── 1. LES CARTES ONT ENFIN UNE SURFACE ET UNE RÉGLURE ───────────────── */
  console.log('\n══ 1. Le défaut de départ : ni surface ni bordure ══');
  await pg.evaluate(() => { go('nist-profil'); nistInit(); });
  await pg.waitForTimeout(3000);
  let r = await pg.evaluate(() => {
    const c = getComputedStyle(document.querySelector('#p-nist-profil .nist-f'));
    const v = getComputedStyle(document.documentElement);
    return { fond: c.backgroundColor, style: c.borderTopStyle,
             large: c.borderTopWidth, bord: c.borderTopColor,
             line: v.getPropertyValue('--line').trim(),
             panel: v.getPropertyValue('--panel').trim() };
  });
  dit(r.line !== '' && r.panel !== '',
      'les jetons --line et --panel existent', r.line + ' / ' + r.panel);
  dit(r.style === 'solid' && r.large === '1px',
      'la carte a retrouvé sa réglure', r.large + ' ' + r.style);
  dit(alpha(r.fond) === 1 && r.fond !== 'rgba(0, 0, 0, 0)',
      'et sa surface — elle ne flotte plus sur le fond de page', r.fond);

  /* ── 2. L'ÉCHELLE MONTE, ELLE N'EST PAS SEULEMENT COLORÉE ─────────────── */
  console.log('\n══ 2. NIST : une teinte qui fonce avec l\'état ══');
  r = await pg.evaluate(() => {
    const out = {};
    document.querySelectorAll('#p-nist-profil .nist-cats li[data-etat]')
      .forEach(li => { const e = li.getAttribute('data-etat');
        if (!out[e]) out[e] = { bord: getComputedStyle(li).borderLeftColor,
                                style: getComputedStyle(li).borderLeftStyle,
                                fond: getComputedStyle(li).backgroundColor,
                                texte: (li.querySelector('select') || {}).value }; });
    const vide = document.querySelector('#p-nist-profil .nist-cats li:not([data-etat])');
    out.__sans_reponse = vide ? getComputedStyle(vide).borderLeftStyle : null;
    return out;
  });
  const echelle = ['absent', 'amorce', 'tenu', 'prouve'].map(e => alpha(r[e] && r[e].bord));
  dit(echelle.every(a => a !== null), 'les quatre niveaux portent une barre',
      echelle.join(' → '));
  dit(echelle.every((a, i) => i === 0 || a > echelle[i - 1]),
      'et elle FONCE du plus bas au plus haut', echelle.join(' < '));
  dit(r.sans_objet && r.sans_objet.style === 'dashed'
      && teinte(r.sans_objet.bord) !== teinte(r.prouve.bord),
      '« sans objet » sort de l\'échelle : tireté, et hors teinte',
      r.sans_objet && r.sans_objet.style + ' ' + teinte(r.sans_objet.bord));
  dit(r.__sans_reponse === 'dotted',
      'et « pas encore répondu » garde le pointillé', r.__sans_reponse);
  dit(['absent', 'amorce', 'tenu', 'prouve', 'sans_objet']
        .every(e => r[e] && r[e].texte === e),
      'chaque ligne dit AUSSI son état en toutes lettres — la couleur ne '
      + 'porte jamais seule');

  /* ── 3. LA TEINTE DIT LE RÉFÉRENTIEL ──────────────────────────────────── */
  console.log('\n══ 3. OWASP : la même mécanique, une autre teinte ══');
  await pg.evaluate(() => { go('owasp-dix'); if (window.owaspInit) owaspInit(); });
  await pg.waitForTimeout(3000);
  const ow = await pg.evaluate(() => {
    const out = {};
    document.querySelectorAll('#p-owasp-dix .ow-liste li[data-etat]')
      .forEach(li => { const e = li.getAttribute('data-etat');
        if (!out[e]) out[e] = getComputedStyle(li).borderLeftColor; });
    return out;
  });
  const eo = ['non', 'partiel', 'oui'].map(e => alpha(ow[e]));
  dit(eo.every((a, i) => a !== null && (i === 0 || a > eo[i - 1])),
      'l\'échelle OWASP monte elle aussi', eo.join(' < '));
  dit(teinte(ow.oui) !== teinte(r.prouve.bord),
      'et les deux référentiels ne portent PAS la même teinte',
      'owasp ' + teinte(ow.oui) + ' · nist ' + teinte(r.prouve.bord));
  const pastilles = await pg.evaluate(() => {
    const l = (g) => {
      const e = document.querySelector('.sb-nav [data-grp="' + g + '"]');
      return e ? getComputedStyle(e).getPropertyValue('--sb-ic').trim() : null;
    };
    return { nist: l('nist-ai-rmf'), owasp: l('owasp-llm') };
  });
  const hex = (t) => '#' + t.split(' ').map(x => (+x).toString(16).padStart(2, '0')).join('');
  dit(hex(teinte(ow.oui)) === pastilles.owasp.toLowerCase()
      && hex(teinte(r.prouve.bord)) === pastilles.nist.toLowerCase(),
      'chaque écran reprend la pastille de SON tiroir dans la barre',
      pastilles.nist + ' / ' + pastilles.owasp);

  /* ── 4. L'AMBRE, ET SEULEMENT POUR UNE RÉSERVE ────────────────────────── */
  console.log('\n══ 4. L\'ambre dit une réserve, jamais un niveau ══');
  await pg.evaluate(() => { go('owasp-pont'); if (window.owaspInit) owaspInit(); });
  await pg.waitForTimeout(3000);
  const pont = await pg.evaluate(() => {
    const t = document.querySelectorAll('#p-owasp-pont tr.ow-non td:first-child');
    const n = document.querySelectorAll('#p-owasp-pont tbody tr:not(.ow-non) td:first-child');
    return { angles: t.length, total: t.length + n.length,
             bord: t.length ? getComputedStyle(t[0]).borderLeftColor : null,
             large: t.length ? getComputedStyle(t[0]).borderLeftWidth : null,
             fond: t.length ? getComputedStyle(t[0]).backgroundColor : null,
             neutre: n.length ? getComputedStyle(n[0]).borderLeftWidth : null };
  });
  dit(pont.angles === 3 && pont.total === 10,
      'trois angles morts sur les dix risques', pont.angles + ' / ' + pont.total);
  dit(pont.large === '3px' && alpha(pont.fond) > 0,
      'ils portent la barre ambre et leur teinte', pont.large + ' ' + pont.bord);
  dit(pont.neutre === '0px',
      'et les sept autres lignes ne portent rien — sinon la barre ne '
      + 'distinguerait rien', pont.neutre);

  console.log('\n══ 5. Cyber et hors cyber : deux espèces, deux teintes ══');
  await pg.evaluate(() => { go('nist-genai'); nistInit(); });
  await pg.waitForTimeout(3200);
  const gen = await pg.evaluate(() => {
    const cy = document.querySelector('#p-nist-genai .nist-gen li:not(.gen-non) .gen-n');
    const no = document.querySelector('#p-nist-genai .nist-gen li.gen-non .gen-n');
    return { cy: cy ? getComputedStyle(cy).color : null,
             no: no ? getComputedStyle(no).color : null,
             horsCyber: document.querySelectorAll('#p-nist-genai .nist-gen li.gen-non').length,
             total: document.querySelectorAll('#p-nist-genai .nist-gen li').length,
             motCy: cy ? cy.closest('li').innerText.indexOf('Hors cyber') : -2,
             motNo: no ? no.closest('li').innerText.indexOf('Hors cyber') : -2 };
  });
  dit(gen.horsCyber === 6 && gen.total === 12,
      'six des douze risques ne relèvent pas de la cyber',
      gen.horsCyber + ' / ' + gen.total);
  dit(gen.cy && gen.no && teinte(gen.cy) !== teinte(gen.no),
      'leurs pastilles portent deux teintes distinctes, pas deux densités',
      teinte(gen.cy) + ' / ' + teinte(gen.no));
  dit(gen.motCy < 0 && gen.motNo >= 0,
      'et le mot « Hors cyber » est écrit là où il s\'applique — la couleur '
      + 'ne porte pas seule');

  console.log('\n══ Erreurs de page ══');
  dit(err.length === 0, 'aucune erreur JavaScript', err.slice(0, 2).join(' | '));
  console.log('\nVERDICT : ' + (verdict ? 'ÉCHEC' : 'OK'));
  await nav.close();
  process.exit(verdict);
})();
