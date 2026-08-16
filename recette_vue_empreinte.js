/* TROIS VUES, UN SEUL DOCUMENT — l'empreinte sort du panorama.
 *
 * MÊME OPÉRATION QUE POUR L'ENVELOPPE, MÊMES PIÈGES. L'étude d'empreinte
 * devient un module à part dans le menu de Sentinel, sous l'enveloppe. Elle
 * n'est PAS recopiée dans un second fichier : elle est tissée dans le registre
 * des sources, dans des étapes de parcours guidé et dans la barre de navigation
 * de page. Le document reste unique et choisit sa vue d'après son adresse.
 *
 * CE QUI NE SE PROUVE QUE DANS UN VRAI NAVIGATEUR :
 *
 *   · que /panorama ne montre PLUS l'empreinte — c'est l'objet de l'opération ;
 *   · que /empreinte-parc ne montre QU'ELLE, et qu'elle y FONCTIONNE : les
 *     chiffres arrivent, le bilan d'eau se rend, la confrontation s'affiche ;
 *   · QUE FERMER UNE FICHE DE PAYS RAMÈNE QUELQUE PART. Les fiches de pays et
 *     de site n'appartiennent à aucune vue : on les ouvre depuis la CARTE dans
 *     le panorama et depuis le TABLEAU dans l'empreinte. Leur fermeture visait
 *     `#s-empreinte` en dur. Depuis que cette section sort du panorama, fermer
 *     une fiche ouverte depuis la carte renverrait vers un bloc RETIRÉ : rien
 *     ne lève, rien ne défile, le lecteur reste où il est sans comprendre. Ce
 *     contrôle est le seul qui puisse le voir ;
 *   · que la barre de navigation ne garde aucun lien vers une section retirée ;
 *   · qu'AUCUNE section n'est perdue entre les trois vues.
 *
 *   POUR L'EXÉCUTER :  BASE=http://127.0.0.1:5413 node recette_vue_empreinte.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5413';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
let ko = 0;
const ok = (n, c, d) => {
  console.log('  ' + (c ? 'OK ' : 'KO ') + '  ' + n + (d ? ' — ' + d : ''));
  if (!c) ko++;
};
const titre = t => console.log('\n══ ' + t + ' ══\n');

/* Les sections VISIBLES, au sens du lecteur : présentes et non retirées. */
const VISIBLES = () => [].slice.call(document.querySelectorAll('section.panel[id]'))
  .filter(s => !s.hidden).map(s => s.id);

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1400, height: 1000 } });
  await ctx.route('**/*', r => (['image', 'font', 'media'].includes(r.request().resourceType())
    ? r.abort() : r.continue()));
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e)));
  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });

  titre('1. /empreinte-parc ouvre l’étude, et rien d’autre');

  await pg.goto(BASE + '/empreinte-parc', { waitUntil: 'domcontentloaded' });
  const e1 = await pg.evaluate(() => ({
    vue: document.body.getAttribute('data-vue'),
    visibles: [].slice.call(document.querySelectorAll('section.panel[id]'))
      .filter(s => !s.hidden).map(s => s.id),
    pnav: [].slice.call(document.querySelectorAll('.pnav a[href^="#s-"]'))
      .map(a => a.getAttribute('href')),
  }));
  ok('la vue déclarée est « empreinte »', e1.vue === 'empreinte', e1.vue);
  /* ON DEMANDE LA COMPOSITION À LA PAGE, ON NE LA RECOPIE PAS. Ce contrôle
     exigeait « une seule section, s-empreinte » : un inventaire figé, qui
     tombe à la première section ajoutée à la vue et n'atteste plus rien
     d'autre que son propre âge. Ce qu'il protège, lui, ne change pas : la
     vue empreinte montre ce qu'elle déclare, et rien qui appartienne à une
     autre lecture. */
  const decl = await pg.evaluate(() => MODULE_VUES);
  ok('la vue empreinte montre EXACTEMENT ce qu’elle déclare',
     e1.visibles.length === decl.empreinte.length
       && e1.visibles.every(id => decl.empreinte.indexOf(id) >= 0),
     'affichées : ' + e1.visibles.join(', ') + '  |  déclarées : '
       + decl.empreinte.join(', '));
  ok('…et l’empreinte du parc en fait partie',
     e1.visibles.indexOf('s-empreinte') >= 0, e1.visibles.join(', '));
  ok('la barre de navigation ne garde aucun lien mort',
     e1.pnav.every(h => decl.empreinte.indexOf(h.slice(1)) >= 0), e1.pnav.join(' '));

  titre('2. …et l’étude y FONCTIONNE, sinon la séparation l’a cassée');

  /* NE PAS LEVER. Si les chiffres n'arrivent pas, c'est le défaut même qu'on
     traque, et il doit être NOMMÉ — un « Timeout » se lit comme une panne
     d'outil là où le contrôle vient de trouver ce qu'il cherchait. */
  const chiffres = await pg.waitForSelector('#emp-kpis .kpi, #emp-kpis .kpi-c',
    { timeout: 60000 }).then(() => true).catch(() => false);
  ok('LES CHIFFRES DE L’EMPREINTE ARRIVENT', chiffres,
     chiffres ? '' : 'aucun indicateur dans #emp-kpis après 60 s');
  /* `state: 'attached'` ET NON la visibilité par défaut. La confrontation vit
     désormais dans un dépliant REPLIÉ — c'est voulu, la section en compte neuf
     et un seul s'ouvre. `waitForSelector` attend la visibilité par défaut :
     il expirait donc sur un bloc parfaitement présent, et déclarait absent ce
     qui était simplement fermé. */
  const eau = await pg.waitForSelector('#eau-source .eau-conf',
    { state: 'attached', timeout: 60000 }).then(() => true).catch(() => false);
  ok('le bilan d’eau et sa confrontation aux repères s’y rendent', eau);
  const dep = await pg.evaluate(() =>
    document.querySelectorAll('#eau-source details.eau-d').length);
  ok('…et la section est bien réagencée en dépliants', dep >= 7, dep + ' dépliants');
  /* `[data-pays]` ET NON `tr` : le bloc se présente en TUILES par défaut, et en
     tableau seulement si le lecteur choisit « Tableau détaillé ». Compter les
     lignes ne voyait donc qu'une des deux présentations — et rendait zéro sur
     celle que tout le monde voit. C'est l'attribut que les deux partagent, et
     c'est lui que la délégation de clic écoute. */
  const tab = await pg.evaluate(() =>
    document.querySelectorAll('#emp-table [data-pays]').length);
  ok('le tableau par pays est peuplé', tab > 3, tab + ' pays');

  titre('3. LE POINT QUI DÉCIDE : fermer une fiche ramène quelque part');

  /* Dans l'empreinte : on ouvre un pays depuis le tableau, on referme. */
  const rEmp = await pg.evaluate(async () => {
    const l = document.querySelector('#emp-table [data-pays], #emp-table tr[data-pays]');
    if (l) l.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    else if (window.ouvrirPays) window.ouvrirPays('FR');
    await new Promise(r => setTimeout(r, 400));
    const ouvert = !document.getElementById('s-pays').hidden;
    if (window.fermerPays) window.fermerPays();
    await new Promise(r => setTimeout(r, 200));
    const cible = location.hash.slice(1);
    const el = cible && document.getElementById(cible);
    return { ouvert: ouvert, cible: cible, visible: !!(el && !el.hidden) };
  });
  ok('une fiche de pays s’ouvre depuis le tableau', rEmp.ouvert);
  ok('…et sa fermeture ramène vers un bloc RÉELLEMENT présent',
     rEmp.visible, 'retour vers #' + (rEmp.cible || '(rien)'));

  titre('4. /panorama ne montre plus l’empreinte — et n’est pas cassé pour autant');

  await pg.goto(BASE + '/panorama', { waitUntil: 'domcontentloaded' });
  const p1 = await pg.evaluate(() => ({
    vue: document.body.getAttribute('data-vue'),
    visibles: [].slice.call(document.querySelectorAll('section.panel[id]'))
      .filter(s => !s.hidden).map(s => s.id),
    pnav: [].slice.call(document.querySelectorAll('.pnav a[href^="#s-"]'))
      .map(a => a.getAttribute('href')),
  }));
  ok('la vue déclarée est « panorama »', p1.vue === 'panorama', p1.vue);
  ok('L’EMPREINTE N’Y EST PLUS', p1.visibles.indexOf('s-empreinte') < 0);
  ok('…l’enveloppe non plus', p1.visibles.indexOf('s-finance') < 0);
  ok('…et la carte, elle, est bien là', p1.visibles.indexOf('s-carte') >= 0,
     p1.visibles.join(', '));
  ok('aucun lien de navigation ne vise une section retirée',
     p1.pnav.indexOf('#s-empreinte') < 0 && p1.pnav.indexOf('#s-finance') < 0,
     p1.pnav.join(' '));

  /* LE DÉFAUT QUE LA SÉPARATION AURAIT INTRODUIT. Sur le panorama, la fiche de
     pays s'ouvre depuis la CARTE — et son retour visait `#s-empreinte`, qui
     n'existe plus ici. */
  await pg.waitForFunction(() => typeof window.ouvrirPays === 'function',
    null, { timeout: 30000 });
  const rPan = await pg.evaluate(async () => {
    window.ouvrirPays('FR');
    await new Promise(r => setTimeout(r, 400));
    const ouvert = !document.getElementById('s-pays').hidden;
    window.fermerPays();
    await new Promise(r => setTimeout(r, 200));
    const cible = location.hash.slice(1);
    const el = cible && document.getElementById(cible);
    return { ouvert: ouvert, cible: cible, visible: !!(el && !el.hidden) };
  });
  ok('une fiche de pays s’ouvre depuis le panorama', rPan.ouvert);
  ok('…ET SA FERMETURE NE RENVOIE PAS VERS UN BLOC RETIRÉ',
     rPan.visible, 'retour vers #' + (rPan.cible || '(rien)')
     + (rPan.visible ? '' : ' — cette section est absente de la vue panorama'));

  titre('5. Aucune section n’est perdue entre les trois vues');

  const vues = { panorama: p1.visibles, empreinte: e1.visibles };
  await pg.goto(BASE + '/enveloppe', { waitUntil: 'domcontentloaded' });
  vues.enveloppe = await pg.evaluate(VISIBLES);
  ok('/enveloppe montre EXACTEMENT ce que la vue enveloppe déclare',
     vues.enveloppe.length === decl.enveloppe.length
       && vues.enveloppe.every(id => decl.enveloppe.indexOf(id) >= 0),
     'affichées : ' + vues.enveloppe.join(', ') + '  |  déclarées : '
       + decl.enveloppe.join(', '));

  const declarees = await pg.evaluate(() => {
    const out = {};
    Object.keys(MODULE_VUES).forEach(v => MODULE_VUES[v].forEach(s => { out[s] = v; }));
    return { map: out, panneaux: PANNEAUX_DETAIL,
             toutes: [].slice.call(document.querySelectorAll('section.panel[id]'))
               .map(s => s.id) };
  });
  const orphelines = declarees.toutes.filter(
    s => !declarees.map[s] && declarees.panneaux.indexOf(s) < 0);
  ok('AUCUNE SECTION N’EST ORPHELINE — elle disparaîtrait des trois vues',
     orphelines.length === 0, orphelines.join(', '));
  const doublons = Object.keys(declarees.map).filter(
    s => declarees.toutes.indexOf(s) < 0);
  ok('aucune vue ne réclame une section qui n’existe pas',
     doublons.length === 0, doublons.join(', '));
  /* UNE UNION, PAS UNE SOMME. Additionner les trois vues comptait deux fois
     toute section partagée — « s-equipements » sert la lecture budget ET la
     lecture carbone — et déclarait un excédent là où la couverture était
     exacte. Ce qu'on veut savoir est : chaque section est-elle atteignable
     depuis au moins une vue ? C'est une réunion d'ensembles. */
  const atteintes = new Set([].concat(vues.panorama, vues.enveloppe, vues.empreinte));
  const attendues = declarees.toutes.filter(
    s => declarees.panneaux.indexOf(s) < 0);
  const jamaisVues = attendues.filter(s => !atteintes.has(s));
  ok('les trois vues couvrent ensemble toutes les sections',
     jamaisVues.length === 0,
     jamaisVues.join(', ') || (atteintes.size + ' atteintes / '
       + attendues.length + ' attendues'));

  ok('aucune erreur de script', err.length === 0, err.slice(0, 2).join(' | '));

  await nav.close();
  console.log('\n' + (ko ? ko + ' contrôle(s) en échec' : 'tout est vert') + '\n');
  process.exit(ko ? 1 : 0);
})();
