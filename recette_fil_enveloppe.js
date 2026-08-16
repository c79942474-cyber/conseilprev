/* LE FIL CONDUCTEUR DE L'ENVELOPPE — ses étapes, des flèches, deux ponts.
 *
 * CE QU'IL RÉSOUT. La vue enchaîne des blocs qui se lisent DANS UN ORDRE, et
 * rien ne le disait : un lecteur arrivé au milieu tombait sur « Calculez d'abord
 * l'enveloppe ci-dessus » sans savoir où était ce « ci-dessus ».
 *
 * LES QUATRE POINTS QUE CE FICHIER PROTÈGE :
 *
 *   1. L'AVANCEMENT EST DÉDUIT DE LA PAGE, JAMAIS TENU À PART. Une barre qui
 *      garderait sa propre comptabilité afficherait « fait » devant un bloc
 *      vidé au recalcul suivant. Le contrôle vérifie que l'état SUIT vraiment —
 *      il lance un calcul et regarde le fil changer.
 *
 *   2. LA PULSATION EST BORNÉE ET INTERRUPTIBLE. C'est ce qui la sépare d'un
 *      clignotement : deux cycles lents, puis plus rien ; et toute action du
 *      lecteur l'arrête. Une mise en évidence permanente cesse d'en être une, et
 *      un clignotement continu est une gêne — au-delà de trois éclats par
 *      seconde, un risque.
 *
 *   3. LES ANIMATIONS RÉDUITES SONT SERVIES, PAS PUNIES. Quand le système le
 *      demande, la pulsation est REMPLACÉE par un cadre fixe — pas supprimée.
 *      Ne rien afficher aurait privé de la désignation ceux qui en ont le plus
 *      besoin. Le contrôle rejoue toute la manœuvre dans ce réglage.
 *
 *   4. LES DEUX PONTS DISENT CE QU'ILS N'EMPORTENT PAS. L'un ne transporte
 *      aucun montant, l'autre transporte une assiette de travaux. Confondus,
 *      ils laissaient croire que le premier transmettait tout.
 *
 *   POUR L'EXÉCUTER :  BASE=http://127.0.0.1:5450 node recette_fil_enveloppe.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5450';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
let ko = 0;
const ok = (n, c, d) => {
  console.log('  ' + (c ? 'OK ' : 'KO ') + '  ' + n + (d ? ' — ' + d : ''));
  if (!c) ko++;
};
const titre = t => console.log('\n══ ' + t + ' ══\n');

const ETATS = () => [...document.querySelectorAll('#fin-fil .fin-e')]
  .map(x => ({ nom: (x.querySelector('b') || {}).textContent || '',
               etat: x.className.replace('fin-e', '').trim() }));

(async () => {
  const nav = await chromium.launch();

  /* Deux contextes : le réglage par défaut, puis « animations réduites ». La
     seconde passe n'est pas un supplément — c'est la moitié du contrat. */
  const ouvrir = async (reduit) => {
    const ctx = await nav.newContext({ viewport: { width: 1500, height: 1100 },
      reducedMotion: reduit ? 'reduce' : 'no-preference' });
    /* CE MASQUE N'EST PAS UN CONFORT, IL EST INDISPENSABLE — et son absence
       ici a coûté cher en diagnostics. La page envoie un signal au serveur
       quand elle se voit pilotée (`navigator.webdriver`, aucun greffon,
       aucune langue) ; le serveur BLOQUE alors l'adresse pendant TRENTE
       MINUTES. Ce fichier se coupait donc l'herbe sous le pied, et coupait
       surtout celle de toutes les recettes lancées après lui : on croyait
       lire des pannes du site, on lisait la trace de ce blocage.
       Les autres recettes posent ce masque ; celle-ci l'avait oublié. */
    await ctx.addInitScript(() => {
      Object.defineProperty(navigator, 'webdriver', { get: () => false });
      Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
      Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
    });
    await ctx.route('**/*', r => (['image', 'font', 'media'].includes(r.request().resourceType())
      ? r.abort() : r.continue()));
    const pg = await ctx.newPage();
    await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
    await pg.goto(BASE + '/enveloppe', { waitUntil: 'domcontentloaded' });
    return pg;
  };

  const pg = await ouvrir(false);
  const err = [];
  pg.on('pageerror', e => err.push(String(e)));

  titre('1. Le fil conducteur est là, et il oriente');

  const vu = await pg.waitForSelector('#fin-fil .fin-e', { timeout: 60000 })
    .then(() => true).catch(() => false);
  if (!vu) {
    ok('LE FIL CONDUCTEUR S’AFFICHE', false,
       'aucune étape dans #fin-fil après 60 s : la section reste un mur de blocs');
    await nav.close();
    console.log('\n' + (ko + 1) + ' contrôle(s) en échec\n');
    process.exit(1);
  }
  const e0 = await pg.evaluate(ETATS);
  /* LE COMPTE VIENT DE LA PAGE. Figé à six, ce contrôle est tombé le jour où
     le fil a couvert toute la vue — équipements, maturité, pilotage —, en
     criant à la régression sur un ajout voulu. Ce qu'il protège est ailleurs :
     toutes les étapes déclarées sont affichées, et elles sont séparées. */
  const declarees = await pg.evaluate(() => FIN_ETAPES.length);
  ok('toutes les étapes déclarées sont affichées', e0.length === declarees,
     e0.length + ' affichée(s) pour ' + declarees + ' déclarée(s) : '
     + e0.map(x => x.nom).join(' · '));
  const fl = await pg.evaluate(() =>
    document.querySelectorAll('#fin-fil .fin-e-fl').length);
  ok('…séparées par des flèches', fl === declarees - 1,
     fl + ' flèche(s) pour ' + declarees + ' étape(s)');
  /* AUCUNE ÉTAPE NE PEUT ÊTRE « FAITE » AVANT D'AVOIR ÉTÉ FRANCHIE. Ce
     contrôle manquait, et il aurait fallu qu'il existe : la dernière étape
     s'affichait faite dès le chargement, parce que son test comptait un lien
     statique au lieu d'un lien CRÉÉ. Une barre qui coche ce que personne n'a
     franchi détruit la confiance dans tout le reste. */
  ok('AUCUNE ÉTAPE D’ACTION N’EST « FAITE » AVANT D’AVOIR ÉTÉ FRANCHIE',
     e0.filter((x, i) => i >= 2 && x.etat === 'fait').length === 0,
     e0.filter((x, i) => i >= 2 && x.etat === 'fait').map(x => x.nom).join(' | ')
     || 'aucune');
  ok('une seule étape est « en cours »',
     e0.filter(x => x.etat === 'cours').length === 1,
     e0.filter(x => x.etat === 'cours').map(x => x.nom).join(''));
  ok('…et le fil dit qu’il n’enferme pas',
     await pg.evaluate(() => /n’enferme pas/.test(
       document.querySelector('#fin-fil .fin-fil-t').innerText)));

  titre('2. LE POINT QUI DÉCIDE : l’avancement suit la page, il ne s’invente pas');

  const avant = e0.map(x => x.etat).join(',');
  await pg.waitForFunction(
    () => document.querySelectorAll('#fin-pays button[data-p]').length > 0,
    null, { timeout: 30000 });
  await pg.click('#fin-go');
  await pg.waitForSelector('#fin-res .fin-dos', { state: 'attached', timeout: 60000 });
  await pg.waitForTimeout(1200);
  const e1 = await pg.evaluate(ETATS);
  const apres = e1.map(x => x.etat).join(',');
  ok('le calcul fait AVANCER le fil', avant !== apres,
     avant + '  →  ' + apres);
  ok('…l’étape « Calculer l’enveloppe » est passée à faite',
     (e1.find(x => /Calculer/.test(x.nom)) || {}).etat === 'fait');
  ok('…et le curseur s’est déplacé sur la suivante',
     (e1.find(x => x.etat === 'cours') || {}).nom !== (e0.find(x => x.etat === 'cours') || {}).nom,
     (e1.find(x => x.etat === 'cours') || {}).nom);
  /* ET APRÈS RE-RENDU. Le contrôle de la section 1 ne suffisait pas : au tout
     premier affichage, le bloc des ponts n'est pas encore écrit, si bien qu'une
     étape 6 qui se cocherait sur le lien STATIQUE ne se voyait pas. Elle ne se
     voit qu'après un recalcul, quand le fil se redessine sur une page complète.
     L'injection l'a montré — le contrôle de la section 1 restait vert. */
  ok('L’ÉTAPE « POURSUIVRE » RESTE À FAIRE : aucun lien n’a été créé',
     (e1.find(x => /Poursuivre/.test(x.nom)) || {}).etat !== 'fait',
     (e1.find(x => /Poursuivre/.test(x.nom)) || {}).etat);

  titre('3. Chaque étape mène à son bloc, et le DÉSIGNE');

  const saut = await pg.evaluate(async () => {
    const b = [...document.querySelectorAll('#fin-fil [data-fin-etape]')]
      .find(x => x.getAttribute('data-fin-etape') === 'moe');
    if (!b) return null;
    b.click();
    await new Promise(r => setTimeout(r, 300));
    const c = document.getElementById('moe-bloc');
    return { vise: c.classList.contains('fin-vise'),
             fixe: c.classList.contains('fin-vise-fixe') };
  });
  ok('cliquer une étape désigne son bloc', saut && (saut.vise || saut.fixe));
  ok('…par une PULSATION en réglage par défaut', saut && saut.vise && !saut.fixe);

  /* LA BORNE. Une pulsation qui ne s'arrêterait pas serait un clignotement. */
  await pg.waitForTimeout(4200);
  const fini = await pg.evaluate(() => {
    const c = document.getElementById('moe-bloc');
    return c.classList.contains('fin-vise') || c.classList.contains('fin-vise-fixe');
  });
  /* CE QUI BORNE LA PULSATION EST LE RETRAIT DE LA CLASSE, pas le nombre de
     cycles écrit dans l'animation. On l'a vérifié en portant l'animation à
     « infinite » : le comportement restait borné, parce que la classe part au
     bout de 3,2 s et emporte l'animation avec elle. Le contrôle porte donc sur
     ce qui borne réellement — et l'injection qui l'éprouve retire le minuteur,
     pas le compte de cycles. */
  ok('LA PULSATION S’ARRÊTE D’ELLE-MÊME', !fini,
     fini ? 'elle dure toujours après 4 s — c’est un clignotement, pas une désignation' : '');

  const arret = await pg.evaluate(async () => {
    const b = [...document.querySelectorAll('#fin-fil [data-fin-etape]')]
      .find(x => x.getAttribute('data-fin-etape') === 'kpi');
    b.click();
    await new Promise(r => setTimeout(r, 200));
    const c = document.getElementById('kpi-bloc');
    const pendant = c.classList.contains('fin-vise');
    /* Le lecteur agit : la marque doit céder la place. */
    document.body.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }));
    await new Promise(r => setTimeout(r, 150));
    return { pendant: pendant, apres: c.classList.contains('fin-vise') };
  });
  ok('…et TOUTE ACTION DU LECTEUR L’INTERROMPT',
     arret && arret.pendant && !arret.apres,
     arret ? ('pendant=' + arret.pendant + ' après=' + arret.apres) : '');

  titre('4. Le mode « guidez-moi »');

  const g = await pg.evaluate(async () => {
    const b = document.getElementById('fin-fil-g');
    if (!b) return null;
    const avant = b.getAttribute('aria-pressed');
    b.click();
    await new Promise(r => setTimeout(r, 400));
    const b2 = document.getElementById('fin-fil-g');
    return { avant: avant, apres: b2.getAttribute('aria-pressed'),
             texte: b2.textContent,
             marque: !!document.querySelector('.fin-vise, .fin-vise-fixe') };
  });
  ok('le bouton de guidage existe et bascule', g && g.avant === 'false' && g.apres === 'true');
  ok('…il annonce comment l’arrêter', g && /Arrêter/.test(g.texte), g && g.texte);
  ok('…et il désigne aussitôt l’étape courante', g && g.marque);

  titre('5. Les flèches entre blocs disent ce qu’on emporte');

  const fls = await pg.evaluate(() =>
    [...document.querySelectorAll('#s-finance .fin-fleche')]
      .map(x => (x.innerText || '').replace(/\s+/g, ' ')));
  ok('des flèches séparent les blocs décisifs', fls.length >= 3, fls.length + ' flèches');
  ok('…et aucune n’est muette', fls.every(t => t.length > 60),
     fls.filter(t => t.length <= 60).join(' | ') || 'toutes portent leur texte');
  ok('…celle qui mène à la maîtrise d’œuvre nomme les deux grandeurs transmises',
     fls.some(t => /montant des travaux/.test(t) && /lot technique/.test(t)));

  titre('6. Les deux ponts vers l’autre site, séparés et nommés');

  const pt = await pg.evaluate(() => {
    const z = document.getElementById('fin-ponts');
    if (!z) return null;
    return { n: z.querySelectorAll('.fin-pt').length,
             texte: (z.innerText || '').replace(/\s+/g, ' '),
             liens: [...z.querySelectorAll('a')].map(a => a.getAttribute('href')) };
  });
  ok('les deux ponts sont présentés côte à côte', pt && pt.n === 2, pt && (pt.n + ' ponts'));
  if (pt) {
    ok('…le premier dit qu’il n’emporte AUCUN montant',
       /n’emporte AUCUN montant/.test(pt.texte));
    ok('…le second dit qu’il porte une assiette de travaux',
       /porte une assiette de travaux/.test(pt.texte));
    ok('…et il mène à la section de maîtrise d’œuvre de l’autre site',
       pt.liens.some(h => /conseilprevcyber/.test(h) && /ig-moe/.test(h)),
       pt.liens.join(' '));
    ok('…l’accès réservé est annoncé', /abonné/.test(pt.texte));
  }

  ok('aucune erreur de script', err.length === 0, err.slice(0, 2).join(' | '));

  titre('7. Animations réduites : la désignation est REMPLACÉE, pas supprimée');

  const pg2 = await ouvrir(true);
  const err2 = [];
  pg2.on('pageerror', e => err2.push(String(e)));
  await pg2.waitForSelector('#fin-fil .fin-e', { timeout: 60000 });
  const r = await pg2.evaluate(async () => {
    const b = [...document.querySelectorAll('#fin-fil [data-fin-etape]')]
      .find(x => x.getAttribute('data-fin-etape') === 'moe');
    b.click();
    await new Promise(r => setTimeout(r, 300));
    const c = document.getElementById('moe-bloc');
    const cs = getComputedStyle(c);
    return { fixe: c.classList.contains('fin-vise-fixe'),
             pulse: c.classList.contains('fin-vise'),
             contour: cs.outlineWidth + ' ' + cs.outlineStyle };
  });
  ok('LE BLOC EST DÉSIGNÉ MALGRÉ TOUT', r && (r.fixe || r.pulse));
  ok('…par un cadre FIXE, pas par une pulsation', r && r.fixe && !r.pulse);
  ok('…et ce cadre est réellement peint', r && parseFloat(r.contour) > 0, r && r.contour);
  ok('aucune erreur de script en réglage réduit', err2.length === 0,
     err2.slice(0, 2).join(' | '));

  await nav.close();
  console.log('\n' + (ko ? ko + ' contrôle(s) en échec' : 'tout est vert') + '\n');
  process.exit(ko ? 1 : 0);
})();
