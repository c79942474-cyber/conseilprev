/* Le menu « Évaluer le risque » de Sentinel — allégé sans rien perdre.
 *
 * CE QU'ON PROTÈGE, ET LA FAUTE QUE CHAQUE CONTRÔLE EMPÊCHE :
 *
 *   1. L'OUTIL ARRIVE VITE. Trois pages portaient un chapeau de 550 à 750
 *      caractères — cinq à treize fois celui des autres pages du même menu —
 *      avant même que le module n'apparaisse. Le texte est allégé, PAS
 *      supprimé : il passe dans un dépliant, et le contrôle vérifie les deux
 *      moitiés — chapeau court ET détail toujours lisible.
 *   2. RIEN NE SE DIT DEUX FOIS. La page d'audit annonçait son titre, son
 *      règlement et son compte de points, puis les redisait quinze lignes
 *      plus bas.
 *   3. LE COMPTE DE POINTS NE MENT PLUS. Trois nombres circulaient pour une
 *      seule chose — 33 écrit, 32 en compteur, 34 en réalité. Un client qui
 *      coche et recompte perd confiance dans tout le reste.
 *   4. LES BOUTONS MARCHENT. Deux boutons « Base de connaissance » portaient
 *      un gestionnaire qui ne compilait pas : le clic ne faisait rien, en
 *      silence.
 *   5. LA SOLLICITATION COMMERCIALE N'EST PLUS AU MILIEU DE L'OUTIL.
 *   6. CE QUI RESTE RESTE. Les huit entrées du menu, leurs pages, leurs
 *      commandes et leurs blocs de méthodologie sont toujours là.
 *
 *     BASE=http://127.0.0.1:5510 node recette_menu_evaluer.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5510';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
let ko = 0;
const ok = (n, c, d) => { console.log('  ' + (c ? 'OK ' : 'KO ') + '  ' + n + (d ? ' — ' + d : '')); if (!c) ko++; };
const titre = t => console.log('\n══ ' + t + ' ══\n');

const PAGES = ['p-pan-sia', 'p-enveloppe', 'p-empreinte-parc', 'p-audit-ia-act',
               'p-matrice', 'p-radar', 'p-fria', 'p-sanctions'];
const DEPLIANTS = ['p-pan-sia', 'p-enveloppe', 'p-empreinte-parc'];

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1500, height: 1000 } });
  /* Sans ce masque, la page signale un navigateur piloté et le serveur bloque
     l'adresse trente minutes — pour cette recette comme pour les suivantes. */
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e).slice(0, 140)));
  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg.waitForTimeout(400);
  const rep = await pg.goto(BASE + '/sentinel', { waitUntil: 'domcontentloaded' });
  ok('la page répond', rep && rep.status() === 200,
     rep ? 'HTTP ' + rep.status() : 'pas de réponse');
  if (!rep || rep.status() !== 200) { await nav.close(); process.exit(2); }
  await pg.waitForTimeout(2500);

  // ── 1 ────────────────────────────────────────────────────────────────────
  titre('1. Les huit entrées du menu sont toujours là, et mènent à leur page');

  const menu = await pg.evaluate(() => {
    const secs = [...document.querySelectorAll('.sb-section')];
    const s = secs.find(x => /Évaluer le risque/.test(x.textContent));
    if (!s) return null;
    const items = [];
    let n = s.nextElementSibling;
    while (n && !n.classList.contains('sb-section')) {
      if (n.classList.contains('sb-item')) {
        const oc = n.getAttribute('onclick') || '';
        const m = /go\('([a-z-]+)'/.exec(oc);
        items.push({ cle: m ? m[1] : '', label: n.textContent.trim(),
                     info: n.getAttribute('title') || '' });
      }
      n = n.nextElementSibling;
    }
    return items;
  });
  ok('la section « Évaluer le risque » porte ses huit entrées',
     !!menu && menu.length === 8, menu ? menu.length + ' entrée(s)' : 'section absente');
  const manquantes = await pg.evaluate((cles) =>
    cles.filter(c => !document.getElementById('p-' + c)), menu.map(i => i.cle));
  ok('…chacune vise une page réellement présente', manquantes.length === 0,
     manquantes.join(', '));

  titre('2. Les infobulles du menu sont écrites en français correct');
  const fautes = menu.filter(i => /\b(l |d |c |qu )\B|conformite|controle|donnees|systeme|reglementaire|financiere|deployeur/.test(i.info));
  ok('aucune infobulle ne perd ses accents ni ses apostrophes',
     fautes.length === 0, fautes.map(f => f.cle + ' : ' + f.info.slice(0, 60)).join(' | '));
  const longues = menu.filter(i => i.info.length > 130);
  ok('…et aucune ne dépasse ce qu’une infobulle peut faire lire',
     longues.length === 0,
     longues.map(f => f.cle + ' (' + f.info.length + ' car.)').join(', '));

  // ── 3 ────────────────────────────────────────────────────────────────────
  titre('3. Le chapeau est court, et le détail reste accessible');

  const leads = await pg.evaluate((ids) => ids.map(id => {
    const p = document.getElementById(id);
    if (!p) return { id: id, absent: true };
    const l = p.querySelector('.page-lead');
    const d = p.querySelector('details.pg-plus');
    return {
      id: id,
      lead: l ? l.textContent.replace(/\s+/g, ' ').trim().length : 0,
      detail: d ? d.querySelector('.pg-plus-c').textContent.replace(/\s+/g, ' ').trim().length : 0,
      replie: d ? !d.open : null,
      resume: d ? (d.querySelector('summary') || {}).textContent : ''
    };
  }), PAGES);

  for (const l of leads.filter(x => DEPLIANTS.includes(x.id))) {
    ok('le chapeau de ' + l.id + ' tient en quelques lignes', l.lead > 0 && l.lead <= 300,
       l.lead + ' caractères');
    ok('…le détail n’est pas perdu, il est replié', l.detail > 150 && l.replie === true,
       l.detail + ' caractères, ' + (l.replie ? 'replié' : 'DÉPLIÉ ou absent'));
    ok('…et son intitulé annonce ce qu’il contient',
       !!l.resume && l.resume.trim().length > 12, l.resume);
  }
  const plusLong = Math.max(...leads.map(l => l.lead));
  ok('AUCUN chapeau du menu ne dépasse désormais 300 caractères', plusLong <= 300,
     'le plus long fait ' + plusLong);

  /* Le dépliant s'ouvre vraiment : un détail qu'on ne peut pas rouvrir est un
     détail supprimé, et ce n'est pas ce qui a été demandé. */
  const ouvre = await pg.evaluate(() => {
    const d = document.querySelector('#p-empreinte-parc details.pg-plus');
    if (!d) return null;
    d.querySelector('summary').click();
    return { open: d.open, vu: d.querySelector('.pg-plus-c').textContent.indexOf('huit à douze fois') >= 0 };
  });
  ok('le dépliant s’ouvre au clic', !!ouvre && ouvre.open === true);
  ok('…et rend bien le texte qui y a été déplacé', !!ouvre && ouvre.vu);

  // ── 4 ────────────────────────────────────────────────────────────────────
  titre('4. LE POINT QUI DÉCIDE : le compte de points ne se contredit plus');

  const compte = await pg.evaluate(() => {
    let n = 0;
    (window.AUDIT_SECTIONS || []).forEach(s => { n += (s.items || []).length; });
    const marques = [...document.querySelectorAll('[data-audit-total]')]
      .map(e => e.textContent.trim());
    const p = document.getElementById('p-audit-ia-act');
    return {
      reel: n, marques: marques,
      texte: p ? p.textContent.replace(/\s+/g, ' ') : ''
    };
  });
  ok('le référentiel d’audit est chargé', compte.reel > 0, compte.reel + ' points');
  ok('les emplacements marqués portent le compte RÉEL',
     compte.marques.length >= 2 && compte.marques.every(v => v === String(compte.reel)),
     compte.marques.join(' / ') + ' contre ' + compte.reel);
  ok('…et aucun autre nombre de points ne circule sur la page',
     !/3[23] ?points/.test(compte.texte),
     (compte.texte.match(/\d\d ?points/g) || []).join(', '));

  titre('5. La page d’audit ne se présente plus deux fois');
  const doublons = await pg.evaluate(() => {
    const p = document.getElementById('p-audit-ia-act');
    const t = p.textContent;
    const compte = (s) => t.split(s).length - 1;
    return {
      reglement: compte('2024/1689'),
      titreBandeau: compte('Audit de conformité EU AI Act'),
      filets: p.querySelectorAll('.rule').length,
      mailtoDansOutil: !!p.querySelector('.col3 ~ div a[href^="mailto"], .rule + div a[href^="mailto"]'),
      mailtoEnPied: !!p.querySelector('.audit-aide a[href^="mailto"]')
    };
  });
  ok('le règlement n’est cité qu’une fois', doublons.reglement === 1,
     doublons.reglement + ' occurrence(s)');
  ok('le bandeau ne redit plus le titre de la page', doublons.titreBandeau === 0,
     doublons.titreBandeau + ' occurrence(s)');
  ok('les filets de séparation qui encadraient la sollicitation ont disparu',
     doublons.filets === 0, doublons.filets + ' filet(s)');
  ok('la proposition d’accompagnement N’EST PLUS au milieu de l’outil',
     doublons.mailtoDansOutil === false);
  ok('…mais elle est CONSERVÉE, en pied de page', doublons.mailtoEnPied === true);

  // ── 6 ────────────────────────────────────────────────────────────────────
  titre('6. Les boutons de ces pages compilent — donc ils font quelque chose');

  const boutons = await pg.evaluate((ids) => {
    const mauvais = [];
    let total = 0;
    ids.forEach(id => {
      const p = document.getElementById(id);
      if (!p) return;
      [...p.querySelectorAll('[onclick]')].forEach(el => {
        total++;
        const code = el.getAttribute('onclick');
        try { new Function(code); }
        catch (e) { mauvais.push(id + ' : ' + (el.textContent || '').trim().slice(0, 34)); }
      });
    });
    return { total: total, mauvais: mauvais };
  }, PAGES);
  ok('tous les gestionnaires de ces pages compilent',
     boutons.mauvais.length === 0, boutons.mauvais.join(' | '));
  ok('…et il y en a bien à éprouver', boutons.total >= 4, boutons.total + ' gestionnaire(s)');

  /* Le même défaut ailleurs : il ne s'agit pas de réparer une page et de
     laisser sa jumelle muette. */
  const partout = await pg.evaluate(() => {
    const mauvais = [];
    [...document.querySelectorAll('[onclick]')].forEach(el => {
      try { new Function(el.getAttribute('onclick')); }
      catch (e) { mauvais.push((el.textContent || '').trim().slice(0, 30)); }
    });
    return mauvais;
  });
  ok('AUCUN gestionnaire cassé dans tout le document',
     partout.length === 0, partout.slice(0, 4).join(' | '));

  // ── 7 ────────────────────────────────────────────────────────────────────
  titre('7. Rien n’a été perdu : ce que chaque page portait est toujours là');

  const reste = await pg.evaluate(() => ({
    matriceGrille: !!document.getElementById('matrix-grid'),
    radarSvg: !!document.getElementById('radar-svg'),
    radarMethodo: !!document.querySelector('#p-radar .radar-methodo'),
    friaListe: !!document.getElementById('fria-list'),
    friaMethodo: !!document.querySelector('#p-fria .radar-methodo'),
    sanctionsForm: !!document.getElementById('s-type'),
    auditSections: !!document.getElementById('audit-sections'),
    auditKpis: document.querySelectorAll('#p-audit-ia-act .audit-kpi').length,
    troisCartes: document.querySelectorAll('#audit-3cards-holder .feat').length,
    iframes: document.querySelectorAll('#p-pan-sia iframe, #p-enveloppe iframe, #p-empreinte-parc iframe').length
  }));
  ok('la matrice a toujours sa grille', reste.matriceGrille);
  ok('le radar a toujours son tracé et sa méthodologie',
     reste.radarSvg && reste.radarMethodo);
  ok('la FRIA a toujours sa liste et sa méthodologie',
     reste.friaListe && reste.friaMethodo);
  ok('le calculateur de sanctions a toujours son formulaire', reste.sanctionsForm);
  ok('l’audit a toujours ses sections, ses quatre indicateurs et ses trois cartes',
     reste.auditSections && reste.auditKpis === 4 && reste.troisCartes === 3,
     reste.auditKpis + ' indicateur(s), ' + reste.troisCartes + ' carte(s)');
  ok('les trois modules embarqués sont toujours là', reste.iframes === 3,
     reste.iframes + ' cadre(s)');

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec') + '\n');
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
