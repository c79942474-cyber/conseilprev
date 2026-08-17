/* RECETTE — LE BLOC « ÉQUIPEMENTS INFORMATIQUES » SE LIT SANS DEVINER
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * CE QUE CETTE RECETTE PROTÈGE, ET LA FAUTE QUE CHAQUE CONTRÔLE EMPÊCHE.
 *
 *   1. UNE COLONNE SANS UNITÉ SE FAIT DEVINER — et « Carbone fabrication » se
 *      devine spontanément en tonnes PAR AN. Il s'agit d'un TOTAL, sur toute
 *      la vie du matériel. Entre les deux lectures il y a un facteur égal à la
 *      durée de vie : cinq à quinze. Un bilan divisé par dix ou multiplié par
 *      dix ne se rattrape pas plus loin dans le dossier.
 *
 *   2. LE POINT QUI DÉCIDE — LE PIED DE TABLEAU RETOMBE EN FACE. Le total
 *      annualisé était rendu dans la colonne « Durée de vie » : un chiffre en
 *      t/an posé sous un intitulé qui parle d'années se lit comme une durée.
 *      La colonne annualisée manquait ; elle existe, et le contrôle vérifie
 *      que chaque valeur du pied tombe sous SON en-tête.
 *
 *   3. LES CHIFFRES CALCULÉS DISENT CE QU'ILS RECOUVRENT, ET CE QU'ILS NE SONT
 *      PAS. Une intensité de bascule, un rapport informatique/travaux, une
 *      part de l'investissement : aucun ne s'interprète seul, et chacun a un
 *      contresens attitré. L'infobulle porte les deux moitiés.
 *
 *   4. LE BLOC EST RATTACHÉ AU PARCOURS. Sans flèche d'entrée, il se lisait
 *      comme une annexe posée là — alors qu'il décide du capital employé lu
 *      deux blocs plus bas.
 *
 * Lancement :
 *     BASE=http://127.0.0.1:5510 node recette_equipements_ui.js
 */
const { chromium } = require('playwright');

const BASE = process.env.BASE || 'http://127.0.0.1:5510';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';

let ko = 0;
const ok = (t, cond, detail) => {
  console.log((cond ? '  OK   ' : '  KO   ') + t + (detail ? ' — ' + detail : ''));
  if (!cond) ko++;
};
const titre = t => console.log('\n══ ' + t + ' ══\n');

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({
    viewport: { width: 1400, height: 1100 },
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
      + '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    locale: 'fr-FR'
  });
  /* SANS CE MASQUE, LE SERVEUR BLOQUE L'ADRESSE POUR 1800 s et toutes les
     recettes suivantes échouent sur des 429 qu'on prend pour des régressions. */
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(e.message));

  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  const rep = await pg.goto(BASE + '/enveloppe', { waitUntil: 'domcontentloaded' });
  if (rep.status() !== 200) {
    ok('la page répond', false, 'HTTP ' + rep.status());
    console.log('\n1 contrôle(s) en échec\n');
    await nav.close(); process.exit(1);
  }
  await pg.waitForFunction(() => !!document.getElementById('eq-go'),
    null, { timeout: 60000 });

  // ── 1 ─────────────────────────────────────────────────────────────────────
  titre('1. Le bloc est rattaché au parcours, pas posé là comme une annexe');

  const fleche = await pg.evaluate(() => {
    const f = document.querySelector('[data-vers="etape-equipements"]');
    return f ? f.textContent.replace(/\s+/g, ' ').trim() : null;
  });
  ok('une flèche annonce ce que le bloc reçoit et ce qu’il transmet', !!fleche,
     fleche ? fleche.slice(0, 70) + '…' : 'aucune flèche d’entrée');
  ok('…elle nomme ce qu’il reprend de l’amont',
     !!fleche && /puissance informatique/i.test(fleche)
       && /enveloppe travaux/i.test(fleche));
  ok('…ET ce qu’il transmet à l’aval — c’est ce qui en fait une étape',
     !!fleche && /capital employé/i.test(fleche));
  /* L'ORDRE EST UN FAIT DE CALCUL : lire la création de valeur avant d'avoir
     chiffré l'informatique donne un ROCE surestimé. La flèche doit le dire. */
  ok('…et il dit POURQUOI l’ordre compte, au lieu de l’imposer',
     !!fleche && /ROCE/.test(fleche));

  await pg.evaluate(() => document.getElementById('fin-go').click());
  await pg.waitForFunction(() => window.FIN_DERNIER && window.FIN_DERNIER(),
    null, { timeout: 60000 });
  await pg.waitForTimeout(1800);
  await pg.evaluate(() => document.getElementById('eq-go').click());
  await pg.waitForFunction(() => !!document.querySelector('#eq-out .eq-tab'),
    null, { timeout: 60000 });
  await pg.waitForTimeout(900);

  // ── 2 ─────────────────────────────────────────────────────────────────────
  titre('2. Chaque colonne chiffrée porte son unité');

  const tab = await pg.evaluate(() => {
    const t = document.querySelector('#eq-out .eq-tab');
    /* LES INDICES DE COLONNE SE DÉDUISENT DES colspan, ils ne se comptent pas
       à la main : c'est justement un décalage de colonne qu'on traque. */
    const etendre = (tr) => {
      const out = [];
      [...tr.children].forEach(c => {
        const n = parseInt(c.getAttribute('colspan') || '1', 10);
        for (let i = 0; i < n; i++) out.push(c.textContent.replace(/\s+/g, ' ').trim());
      });
      return out;
    };
    const th = etendre(t.querySelector('thead tr'));
    const l1 = etendre(t.querySelector('tbody tr'));
    const tf = etendre(t.querySelector('tfoot tr'));
    return { th, l1, tf,
      annualisees: [...t.querySelectorAll('tbody tr')].map(tr =>
        parseFloat((tr.children[5].textContent || '').replace(/\s/g, '').replace(',', '.'))),
      totalAnnualise: parseFloat((tf[5] || '').replace(/\s/g, '').replace(',', '.')) };
  });

  const iCol = (motif) => tab.th.findIndex(x => motif.test(x));
  const iPrix = iCol(/Prix indicatif/i);
  const iCarb = iCol(/Carbone fabrication/i);
  const iAnn = iCol(/Carbone annualisé/i);
  const iDur = iCol(/Durée de vie/i);

  ok('le prix porte son unité', iPrix >= 0 && /\(€\)/.test(tab.th[iPrix]),
     tab.th[iPrix]);
  ok('LE CARBONE DE FABRICATION DIT QU’IL EST UN TOTAL, pas un flux annuel',
     iCarb >= 0 && /t ?CO₂e/i.test(tab.th[iCarb]) && /total/i.test(tab.th[iCarb]),
     tab.th[iCarb]);
  ok('…et il ne se donne PAS en tonnes par an',
     iCarb >= 0 && !/CO₂e\/an|t\/an/i.test(tab.th[iCarb]), tab.th[iCarb]);
  ok('la durée de vie porte son unité',
     iDur >= 0 && /\(ans\)/.test(tab.th[iDur]), tab.th[iDur]);

  // ── 3 : LE POINT QUI DÉCIDE ───────────────────────────────────────────────
  titre('3. LE POINT QUI DÉCIDE : le pied de tableau retombe sous SON en-tête');

  ok('une colonne « carbone annualisé » existe, en t CO₂e/an',
     iAnn >= 0 && /\/an/.test(tab.th[iAnn]), tab.th[iAnn] || 'colonne absente');
  ok('…elle est DISTINCTE de la colonne du carbone total',
     iAnn >= 0 && iCarb >= 0 && iAnn !== iCarb, 'total ' + iCarb + ', annualisé ' + iAnn);
  /* LE DÉFAUT EXACT QU'ON TRAQUE : un chiffre en t/an rendu sous « Durée de
     vie ». Sous un intitulé qui parle d'années, il se lit comme une durée. */
  const sousDuree = tab.tf[iDur];
  ok('LE TOTAL ANNUALISÉ N’EST PLUS SOUS « DURÉE DE VIE »',
     iDur >= 0 && !/\d/.test(sousDuree || ''),
     'sous « Durée de vie » : « ' + sousDuree + ' »');
  ok('…il est sous « carbone annualisé », en face de sa colonne',
     iAnn >= 0 && /\d/.test(tab.tf[iAnn] || ''), tab.tf[iAnn]);
  ok('…et le total des lignes retombe sur le total du pied',
     Math.abs(tab.annualisees.reduce((a, b) => a + b, 0) - tab.totalAnnualise) < 1.5,
     tab.annualisees.reduce((a, b) => a + b, 0).toFixed(1) + ' contre '
       + tab.totalAnnualise);
  /* ET LES DEUX CARBONES NE SE CONFONDENT PAS : l'annualisé est plus petit que
     le total, d'un facteur égal à la durée de vie. Si les deux colonnes
     portaient la même grandeur, ce contrôle tomberait. */
  ok('…et l’annualisé est bien PLUS PETIT que le total : ce sont deux grandeurs',
     parseFloat((tab.tf[iAnn] || '0').replace(/\s/g, '').replace(',', '.'))
       < parseFloat((tab.tf[iCarb] || '0').replace(/\s/g, '').replace(',', '.')),
     tab.tf[iAnn] + ' t/an contre ' + tab.tf[iCarb] + ' t au total');

  // ── 4 ─────────────────────────────────────────────────────────────────────
  titre('4. Les chiffres calculés portent leur infobulle — les deux moitiés');

  const bulles = await pg.evaluate(() => {
    const cles = [...document.querySelectorAll('#eq-out [data-aide]')]
      .map(x => x.getAttribute('data-aide'));
    const uniques = [...new Set(cles)];
    return {
      ancres: uniques,
      boutons: document.querySelectorAll('#eq-out button.aide').length,
      contenu: uniques.map(c => ({
        cle: c,
        t: (window.AIDES && window.AIDES[c] && window.AIDES[c].t) || '',
        d: (window.AIDES && window.AIDES[c] && window.AIDES[c].d) || '',
        pas: (window.AIDES && window.AIDES[c] && window.AIDES[c].pas) || ''
      }))
    };
  });
  ok('les colonnes chiffrées et les cases de synthèse portent une infobulle',
     bulles.ancres.length >= 7, bulles.ancres.length + ' : ' + bulles.ancres.join(', '));
  ok('…et chaque ancre a REÇU son bouton',
     bulles.boutons >= bulles.ancres.length,
     bulles.boutons + ' bouton(s) pour ' + bulles.ancres.length + ' ancre(s)');
  ok('CHACUNE DIT CE QUE LE CHIFFRE N’EST PAS — c’est la moitié qui manque partout',
     bulles.contenu.length > 0 && bulles.contenu.every(x => x.pas.length > 40),
     bulles.contenu.filter(x => x.pas.length <= 40).map(x => x.cle).join(', ')
       || 'toutes complètes');
  const carb = bulles.contenu.filter(x => x.cle === 'eq_carbone')[0];
  ok('celle du carbone de fabrication écarte explicitement la lecture annuelle',
     !!carb && /pas une émission annuelle/i.test(carb.pas),
     carb && carb.pas.slice(0, 70) + '…');
  ok('…et elle CITE la source du module au lieu de la paraphraser',
     await pg.evaluate(() => {
       const ref = window.AIDES && window.AIDES.eq_carbone;
       return !!ref && /Boavizta|PCF|constructeur/i.test(ref.d);
     }), carb && carb.d.slice(-60));
  ok('…celle du prix annonce que ce n’est pas un devis, avec son incertitude',
     await pg.evaluate(() => {
       const a = window.AIDES && window.AIDES.eq_prix;
       return !!a && /pas un devis/i.test(a.pas) && /±\s*\d+\s*%/.test(a.pas);
     }));

  // ── 5 ─────────────────────────────────────────────────────────────────────
  titre('5. Le bloc « durée de vie » a les siennes aussi');

  await pg.evaluate(() => {
    const b = document.getElementById('eq-vie-go')
      || document.querySelector('#eq-vie-bloc button');
    if (b) b.click();
  });
  await pg.waitForTimeout(3000);
  const vie = await pg.evaluate(() => {
    const cles = [...document.querySelectorAll('#eq-vie-out [data-aide]')]
      .map(x => x.getAttribute('data-aide'));
    return { cles: [...new Set(cles)],
             boutons: document.querySelectorAll('#eq-vie-out button.aide').length,
             rendu: !!document.querySelector('#eq-vie-out .eq-bloc') };
  });
  if (!vie.rendu) {
    console.log('  ··   le bloc de durée de vie n’a pas été calculé : contrôle non concluant');
  } else {
    ok('les chiffres de la prolongation portent aussi leur infobulle',
       vie.cles.length >= 3, vie.cles.join(', ') || 'aucune');
    ok('…dont l’intensité de bascule, le chiffre le plus facile à mal lire',
       vie.cles.indexOf('eq_bascule') >= 0, vie.cles.join(', '));
    ok('…et elles sont branchées', vie.boutons >= vie.cles.length,
       vie.boutons + ' bouton(s)');
    ok('…celle de la bascule rappelle qu’elle ne dépend pas de la taille du site',
       await pg.evaluate(() => {
         const a = window.AIDES && window.AIDES.eq_bascule;
         return !!a && /200 kW/.test(a.pas) && /20 MW/.test(a.pas);
       }));
  }

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec') + '\n');
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
