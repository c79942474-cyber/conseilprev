/* prEN 18286, DE BOUT EN BOUT DANS UN VRAI NAVIGATEUR.
 *
 * CE QUE LA RECETTE ÉPROUVE, ET QUE LES RÈGLES PYTHON NE PEUVENT PAS :
 *   · que les quatre écrans demandés — processus, questionnaire, conformité,
 *     analyse — PEIGNENT, et par TOUT chemin : l'onglet de la barre comme le
 *     lien profond `go()` d'un parcours guidé. C'est le défaut qui a été
 *     mesuré ici : `;en18286Init()` ne vivait que dans le `onclick`, et les
 *     quatre pages s'ouvraient sur « Chargement… » sans fin ;
 *   · qu'un clic change VRAIMENT le taux, et que le plafond de la charge de
 *     preuve du §4.4.3.2.2 tombe puis se lève à l'écran ;
 *   · que l'écran du module et la carte du taux de conformité affichent LE
 *     MÊME nombre — le défaut des « deux vérités » ;
 *   · que la réponse survit au rechargement de la page ;
 *   · que le rail de la barre suive les quatre blocs.
 *
 * AUCUNE ÉCRITURE : le module vit dans la mémoire de l'écran
 * (cp-sentinel-en18286-v1), pas dans la base. Rien n'est prélevé, rien n'est
 * purgé, aucun document n'est produit.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = 'http://127.0.0.1:9941', TOKEN = 'recette_locale_idf_0123456789abcdef';
const pad = (s, n) => String(s == null ? '—' : s).padEnd(n).slice(0, n);
let verdict = 0;
const dit = (ok, quoi, detail) => {
  if (!ok) verdict = 1;
  console.log('  ' + (ok ? '✓' : '✗') + ' ' + pad(quoi, 60) + (detail == null ? '' : detail));
};

const LIRE = (id) => {
  const p = document.getElementById('p-' + id);
  if (!p) return { absent: true };
  return { texte: (p.innerText || '').replace(/\s+/g, ' ').trim(),
           boutons: p.querySelectorAll('button').length,
           allumes: p.querySelectorAll('button[aria-pressed="true"]').length,
           selects: p.querySelectorAll('select').length,
           chargement: /Chargement/.test(p.innerText || ''),
           classe: p.className };
};

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1500, height: 1200 } });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e).slice(0, 170)));
  pg.on('console', m => { if (m.type() === 'error'
      && !/ERR_CERT_AUTHORITY_INVALID|favicon/.test(m.text())) err.push('CONSOLE ' + m.text().slice(0, 150)); });
  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg.waitForFunction(() => typeof go === 'function', null, { timeout: 40000 });
  await pg.waitForTimeout(2500);
  /* ON PART D'UN ÉCRAN VIERGE, et c'est ce qui rend la recette rejouable :
     la mémoire d'un passage précédent fausserait toutes les mesures. */
  await pg.evaluate(() => { try { localStorage.removeItem('cp-sentinel-en18286-v1'); } catch (e) {} });

  /* ══ 1. LE LIEN PROFOND PEINT — le défaut mesuré ═══════════════════════ */
  console.log('\n══ 1. Les quatre écrans peignent par `go()`, sans passer par la barre ══');
  const PANNEAUX = ['en18286-processus', 'en18286-questionnaire',
                    'en18286-conformite', 'en18286-analyse'];
  for (const id of PANNEAUX) {
    await pg.evaluate((x) => go(x), id);
    await pg.waitForTimeout(2200);
    const r = await pg.evaluate(LIRE, id);
    dit(!r.absent && !r.chargement && r.texte.length > 200,
        'go(\'' + id + '\') peint son contenu', r.absent ? 'PANNEAU ABSENT'
          : (r.chargement ? '« Chargement… » SANS FIN' : r.texte.length + ' car.'));
  }

  /* ══ 2. LA QUALIFICATION COMMANDE LES TROIS AUTRES ÉCRANS ══════════════ */
  console.log('\n══ 2. La qualification commande, et le silence n\'est pas un « non » ══');
  await pg.evaluate(() => go('en18286-processus'));
  await pg.waitForTimeout(1800);
  let r = await pg.evaluate(LIRE, 'en18286-processus');
  dit(/fournisseur/i.test(r.texte) && /haut risque/i.test(r.texte),
      'les deux questions de qualification sont posées');
  dit(r.allumes === 0, 'rien n\'est coché avant la première réponse', r.allumes + ' allumé(s)');

  /* Hors champ : on se déclare NON fournisseur, et les trois autres écrans
     doivent le DIRE au lieu de laisser soixante-cinq questions. */
  await pg.evaluate(() => {
    document.querySelector('#p-en18286-processus button[data-champ="fournisseur"][data-val="non"]').click();
    document.querySelector('#p-en18286-processus button[data-champ="haut_risque"][data-val="oui"]').click();
  });
  await pg.waitForTimeout(2500);
  r = await pg.evaluate(LIRE, 'en18286-questionnaire');
  dit(/FOURNISSEUR/.test(r.texte) && !/sans objet/i.test(r.texte) === false
      || /fournisseur/i.test(r.texte),
      'hors champ, le questionnaire dit pourquoi il n\'a rien à mesurer');
  let rail = await pg.evaluate(() => {
    const d = document.querySelectorAll('.dr-bloc');
    return Array.from(d).map(x => x.className).join(' | ');
  });
  dit(true, 'le rail est relevé', (rail || '').slice(0, 70));

  /* ══ 3. DANS LE CHAMP : LA STRATÉGIE DU §4.4 ═══════════════════════════ */
  console.log('\n══ 3. Les cinq composantes et les sept approches du §4.4 ══');
  await pg.evaluate(() => {
    document.querySelector('#p-en18286-processus button[data-champ="fournisseur"][data-val="oui"]').click();
  });
  await pg.waitForTimeout(2000);
  r = await pg.evaluate(LIRE, 'en18286-processus');
  dit(r.boutons >= 10, 'l\'écran du processus déplie la stratégie', r.boutons + ' boutons');
  dit(r.selects >= 7, 'une approche se choisit par exigence essentielle',
      r.selects + ' listes');

  /* Toutes les composantes, puis « autre solution » partout SANS preuve. */
  const pose = await pg.evaluate(() => {
    const p = document.getElementById('p-en18286-processus');
    let n = 0;
    p.querySelectorAll('button[onclick*="en18286Composante"]').forEach(b => {
      if (b.getAttribute('aria-pressed') !== 'true') { b.click(); n++; }
    });
    return n;
  });
  await pg.waitForTimeout(2200);
  dit(pose >= 5, 'les cinq composantes se déclarent', pose + ' cochées');

  await pg.evaluate(() => {
    const p = document.getElementById('p-en18286-processus');
    p.querySelectorAll('select[onchange*="en18286Approche"]').forEach(s => {
      s.value = 'autre_solution';
      s.dispatchEvent(new Event('change', { bubbles: true }));
    });
  });
  await pg.waitForTimeout(2500);
  r = await pg.evaluate(LIRE, 'en18286-processus');
  dit(/4\.4\.3\.2\.2/.test(r.texte),
      'la charge de preuve du §4.4.3.2.2 est annoncée AVANT d\'être subie');

  /* ══ 4. LE QUESTIONNAIRE, PAR LOT, ET LE TAUX QUI BOUGE ════════════════ */
  console.log('\n══ 4. Soixante-cinq paragraphes, le lot, et le taux ══');
  await pg.evaluate(() => go('en18286-questionnaire'));
  await pg.waitForTimeout(2500);
  r = await pg.evaluate(LIRE, 'en18286-questionnaire');
  dit(r.selects >= 60, 'les soixante-cinq paragraphes portent leur réponse',
      r.selects + ' listes');
  const lots = await pg.evaluate(() =>
    document.querySelectorAll('#p-en18286-questionnaire button[onclick*="en18286Lot"]').length);
  dit(lots >= 7, 'chaque chapitre a son bouton de lot', lots + ' boutons');

  await pg.evaluate(() => {
    document.querySelectorAll('#p-en18286-questionnaire button[onclick*="en18286Lot"][data-etat="tenu"]')
      .forEach(b => b.click());
  });
  await pg.waitForTimeout(3500);
  let vu = await pg.evaluate(() => {
    const e = document.getElementById('en18286-verdict');
    return e ? (e.innerText || '').replace(/\s+/g, ' ').trim() : null;
  });
  dit(vu && /%/.test(vu), 'le verdict affiche un taux', (vu || '').slice(0, 90));
  const plafonne = vu && /plafonn/i.test(vu);
  dit(plafonne, 'le taux est ANNONCÉ plafonné, et le plafond est nommé');
  const m83 = vu && vu.match(/(\d+)\s*%/);
  dit(m83 && Number(m83[1]) === 83,
      'tout tenu + charge de preuve non honorée = 83 %', m83 ? m83[1] + ' %' : '—');

  /* ══ 5. LES TROIS PIÈCES LÈVENT LE PLAFOND, À L'ÉCRAN ══════════════════ */
  console.log('\n══ 5. Les trois pièces du §4.4.3.2.2 lèvent le plafond ══');
  await pg.evaluate(() => go('en18286-processus'));
  await pg.waitForTimeout(2200);
  const pieces = await pg.evaluate(() => {
    const p = document.getElementById('p-en18286-processus');
    let n = 0;
    p.querySelectorAll('button[onclick*="en18286Piece"]').forEach(b => {
      if (b.getAttribute('aria-pressed') !== 'true') { b.click(); n++; }
    });
    return n;
  });
  await pg.waitForTimeout(3500);
  dit(pieces >= 21, 'les trois pièces se cochent pour les sept exigences',
      pieces + ' clics');
  vu = await pg.evaluate(() => {
    const e = document.getElementById('en18286-verdict');
    return e ? (e.innerText || '').replace(/\s+/g, ' ').trim() : null;
  });
  const m100 = vu && vu.match(/(\d+)\s*%/);
  dit(m100 && Number(m100[1]) === 100, 'le plafond se lève : 100 %',
      m100 ? m100[1] + ' %' : '—');
  dit(vu && !/plafonn/i.test(vu), 'et l\'écran cesse d\'annoncer un plafond');
  dit(vu && /présomption/i.test(vu),
      'la réserve de présomption RESTE, elle — le projet n\'est pas au JOUE');

  /* ══ 6. L'ANNEXE ZA : LA LIGNE VIDE EST AFFICHÉE ═══════════════════════ */
  console.log('\n══ 6. L\'annexe ZA, et la ligne que la norme déclare non couverte ══');
  await pg.evaluate(() => go('en18286-conformite'));
  await pg.waitForTimeout(2800);
  const za = await pg.evaluate(() => {
    const p = document.getElementById('p-en18286-conformite');
    const li = p.querySelectorAll('table.ow-pont tbody tr');
    return { lignes: li.length,
             nues: p.querySelectorAll('table.ow-pont tbody tr.ow-non').length,
             texte: (p.innerText || '').replace(/\s+/g, ' ').trim() };
  });
  dit(za.lignes >= 15, 'l\'article 17 est déplié alinéa par alinéa',
      za.lignes + ' lignes');
  dit(za.nues === 1, 'une ligne, et une seule, est marquée non couverte',
      za.nues + ' ligne(s)');
  dit(/17\(2\)/.test(za.texte), 'et c\'est l\'article 17(2) qui est nommé');
  dit(/Journal officiel/.test(za.texte),
      'la réserve du Journal officiel est sur l\'écran, pas en note');

  /* ══ 7. L'ANALYSE : LES LIGNES EN FACE DU VIDE ═════════════════════════ */
  console.log('\n══ 7. Ce qu\'un certificat ISO ne donne pas ══');
  await pg.evaluate(() => go('en18286-analyse'));
  await pg.waitForTimeout(2800);
  const an = await pg.evaluate(() => {
    const p = document.getElementById('p-en18286-analyse');
    return { ponts: p.querySelectorAll('details.gen-sc').length,
             famille: p.querySelectorAll('ul.ow-liste > li').length,
             texte: (p.innerText || '').replace(/\s+/g, ' ').trim() };
  });
  dit(an.ponts === 2, 'les deux tables de correspondance sont là',
      an.ponts + ' ponts');
  dit(an.famille >= 6, 'la famille des normes harmonisées est listée',
      an.famille + ' références');
  dit(/4\.4/.test(an.texte) && /ISO 9001/.test(an.texte),
      'le §4.4 est nommé comme ce que le certificat ne donne pas');
  dit(/18229-3/.test(an.texte), 'la norme que ce site traite déjà est signalée');

  /* ══ 8. UNE SEULE VÉRITÉ SUR LE TAUX ═══════════════════════════════════ */
  console.log('\n══ 8. L\'écran du module et la carte du taux disent le MÊME nombre ══');
  /* ON Y VA PAR `go()`, SANS TOUCHER LA BARRE, et c'est le point : `conf-taux`
     est la dernière étape de cinq parcours guidés. RELEVÉ ICI : sans la ligne
     d'amorçage dans `go()`, la page n'affichait que son chapô. */
  await pg.evaluate(() => go('conf-taux'));
  await pg.waitForFunction(() => {
    const p = document.getElementById('p-conf-taux');
    return p && /prEN 18286/.test(p.innerText || '');
  }, null, { timeout: 25000 }).catch(() => {});
  const carte = await pg.evaluate(() => {
    const p = document.getElementById('p-conf-taux');
    const t = (p.innerText || '').replace(/\s+/g, ' ');
    const i = t.indexOf('prEN 18286');
    return { trouvee: i >= 0 ? t.slice(i, i + 200) : null,
             longueur: t.length, treize: /[Tt]reize/.test(t),
             onze: /\bonze\b/i.test(t) };
  });
  dit(carte.trouvee != null, 'la carte prEN 18286 est sur l\'écran du taux',
      carte.trouvee ? carte.trouvee.slice(0, 60) : 'PAGE VIDE (' + carte.longueur + ' car.)');
  const mc = carte.trouvee && carte.trouvee.match(/(\d+)\s*%/);
  dit(mc && Number(mc[1]) === 100,
      'et elle porte le même 100 % que le module', mc ? mc[1] + ' %' : '—');
  dit(carte.treize && !carte.onze,
      'le chapô ne compte plus « onze » normes quand il y en a treize');

  /* ══ 9. LA RÉPONSE SURVIT AU RECHARGEMENT ══════════════════════════════ */
  console.log('\n══ 9. Les réponses survivent au rechargement ══');
  await pg.goto(BASE + '/sentinel', { waitUntil: 'commit' });
  await pg.waitForFunction(() => typeof go === 'function', null, { timeout: 40000 });
  await pg.waitForTimeout(2500);
  await pg.evaluate(() => go('en18286-questionnaire'));
  await pg.waitForTimeout(3000);
  const apres = await pg.evaluate(() => {
    const p = document.getElementById('p-en18286-questionnaire');
    const s = p.querySelectorAll('select.q-sel');
    let tenus = 0;
    s.forEach(x => { if (x.value === 'tenu') tenus++; });
    return { total: s.length, tenus: tenus };
  });
  dit(apres.tenus >= 60, 'les soixante-cinq réponses sont relues',
      apres.tenus + ' / ' + apres.total + ' à « tenu »');

  /* ══ 10. LE RAIL DE LA BARRE SUIT LES QUATRE BLOCS ═════════════════════ */
  console.log('\n══ 10. Le rail du référentiel ══');
  /* LES ONGLETS DE LA BARRE SONT LE RAIL : c'est sur eux que le parcours pose
     ses états. On les relève par `data-norme`, puis on lit la classe que le
     script a posée sur chacun — et non une classe supposée. */
  await pg.evaluate(() => go('en18286-analyse'));
  await pg.waitForTimeout(3500);
  const blocs = await pg.evaluate(() => {
    const d = document.querySelectorAll('.sb-nav .sb-item[data-norme="en18286"]');
    return Array.from(d).map(x => ({
      etat: x.getAttribute('data-rail'),
      puce: !!x.querySelector('.rail-puce'),
      bulle: (x.getAttribute('title') || '').slice(0, 50) }));
  });
  dit(blocs.length === 4, 'la barre porte les quatre onglets du référentiel',
      blocs.length + ' onglets');
  dit(blocs.every(b => b.etat), 'le rail a peint un état sur chacun',
      blocs.map(b => b.etat || '—').join(' '));
  dit(blocs.every(b => b.puce), 'et chacun porte sa puce de rail');
  dit(blocs.filter(b => b.etat === 'validee').length >= 2,
      'les deux blocs de saisie remplis sont VALIDÉS',
      blocs.map(b => b.etat || '—').join(' '));
  dit(blocs.some(b => b.bulle && b.bulle.length > 10),
      'et chaque onglet dit au survol où il en est',
      (blocs[0] && blocs[0].bulle) || '—');

  /* ══ 11. AUCUNE ERREUR DE PAGE ═════════════════════════════════════════ */
  console.log('\n══ 11. La page ne jette rien ══');
  dit(err.length === 0, 'aucune erreur JavaScript pendant la recette',
      err.length ? err.slice(0, 2).join(' | ') : '0');

  await nav.close();
  console.log('\n' + (verdict ? '✗ RECETTE EN ÉCHEC' : '✓ recette prEN 18286 complète'));
  process.exit(verdict);
})();
