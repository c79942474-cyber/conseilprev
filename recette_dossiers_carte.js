/* SOUS LA CARTE, SEULS LES DOSSIERS DÉSIGNÉS SUR LA CARTE UE.
 *
 * CE QUE CE CONTRÔLE ÉPROUVE. Le module compare jusqu'à six pays et rendait
 * pour chacun un dossier complet — avis de faisabilité, DPGF de quatorze lots,
 * échéancier, écarts. Six dossiers déroulés d'affilée enterraient la carte qui
 * les résume. Désormais ils sont TOUS CALCULÉS et REPLIÉS : on ouvre celui dont
 * on clique le pays sur la carte de l'UE.
 *
 * CE QU'IL FAUT PROUVER, ET QU'UNE LECTURE DU SOURCE NE PROUVERAIT PAS :
 *   · qu'après le calcul, AUCUN dossier n'est déplié — pas « qu'un attribut est
 *     posé » mais que le navigateur ne les rend pas ;
 *   · qu'un clic sur la carte n'ouvre QUE ce pays-là ;
 *   · que deux clics ouvrent deux dossiers, et pas l'un à la place de l'autre ;
 *   · que le blanc sous la carte est OCCUPÉ par une consigne — un vide se lit
 *     comme un calcul qui n'a rien rendu ;
 *   · que l'écart d'un pays voyage AVEC son dossier : laissé en bas de page, il
 *     commenterait des chiffres repliés ;
 *   · et que le TÉLÉCHARGEMENT n'est pas amputé — c'est le piège de ce genre de
 *     repli, et le seul qui coûterait cher.
 *
 * MÉNAGER LE LIMITEUR : on ouvre /enveloppe directement, on bloque images et
 * polices, et on ne fait qu'UN calcul pour tout le contrôle.
 *
 *   POUR L'EXÉCUTER :  BASE=http://127.0.0.1:5401 node recette_dossiers_carte.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5401';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
let ko = 0;
const ok = (n, c, d) => {
  console.log('  ' + (c ? 'OK ' : 'KO ') + '  ' + n + (d ? ' — ' + d : ''));
  if (!c) ko++;
};
const titre = t => console.log('\n══ ' + t + ' ══\n');

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1500, height: 1100 } });
  /* SANS CE MASQUE, LA RECETTE SE FAIT BANNIR — et bannit les suivantes. La
     page signale au serveur qu'elle se voit pilotée (`navigator.webdriver`,
     aucun greffon, aucune langue) et le serveur bloque alors l'adresse
     TRENTE MINUTES. Un fichier qui l'oublie ne rate pas seulement ses propres
     contrôles : il fait échouer toutes les recettes lancées dans la
     demi-heure, sur un site parfaitement sain. */
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });

  await ctx.route('**/*', r => {
    const t = r.request().resourceType();
    if (['image', 'font', 'media'].includes(t)) return r.abort();
    return r.continue();
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e)));

  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg.goto(BASE + '/enveloppe', { waitUntil: 'domcontentloaded' });
  await pg.waitForSelector('#fin-go', { timeout: 30000 });

  /* Le formulaire charge son référentiel de pays par requête : sans cette
     attente, on lancerait le calcul sur une liste vide. */
  await pg.waitForFunction(
    () => document.querySelectorAll('#fin-pays button').length >= 4,
    null, { timeout: 30000 });

  /* Quatre pays : assez pour que « seuls ceux qu'on clique » veuille dire
     quelque chose, et pour qu'il reste des dossiers NON ouverts à la fin. */
  const choisis = await pg.evaluate(() => {
    const bs = [...document.querySelectorAll('#fin-pays button')];
    bs.filter(b => b.classList.contains('on')).forEach(b => b.click());
    const pris = bs.slice(0, 4);
    pris.forEach(b => b.click());
    return pris.map(b => b.getAttribute('data-p') || b.dataset.p || b.textContent.trim());
  });
  console.log('  … pays comparés : ' + choisis.join(', '));

  await pg.click('#fin-go');
  /* `attached` et non `visible` : les dossiers sont précisément ce qu'on
     attend de trouver REPLIÉ. Attendre leur visibilité serait attendre
     l'échec de ce qu'on éprouve. */
  await pg.waitForSelector('#fin-res .fin-dos', { state: 'attached', timeout: 60000 });

  titre('1. Après le calcul, la carte est là et AUCUN dossier n’est déplié');

  const apres = await pg.evaluate(() => {
    const tous = [...document.querySelectorAll('#fin-res .fin-dos')];
    /* offsetParent === null : ce que le NAVIGATEUR rend, pas ce que l'attribut
       prétend. Un `hidden` neutralisé par une règle CSS passerait ici. */
    const vus = tous.filter(d => d.offsetParent !== null);
    return { total: tous.length, vus: vus.length,
             carte: !!document.querySelector('#fin-res .cres svg'),
             rangs: document.querySelectorAll('#fin-res .fin-rang .fin-carte').length,
             hauteur: Math.round(document.querySelector('#fin-res').scrollHeight) };
  });
  ok('les quatre dossiers sont calculés', apres.total === 4, apres.total + ' dossier(s)');
  ok('LA CARTE DE L’UE EST RENDUE', apres.carte);
  ok('le classement reste visible au-dessus', apres.rangs === 4, apres.rangs + ' fiche(s) de rang');
  ok('AUCUN N’EST DÉPLIÉ — tel que le navigateur les rend',
     apres.vus === 0, apres.vus + ' déplié(s) sur ' + apres.total);

  titre('2. Le blanc sous la carte est OCCUPÉ — un vide se lirait comme une panne');

  const barre = await pg.evaluate(() => {
    const v = document.getElementById('fin-ouvre-v');
    const n = document.querySelector('#fin-ouvre .fin-ouvre-n');
    return { texte: v ? v.textContent.trim() : '',
             visible: !!v && v.offsetParent !== null,
             note: n ? n.textContent.trim() : '' };
  });
  ok('une consigne occupe la place des dossiers', barre.visible && barre.texte.length > 60,
     barre.texte.slice(0, 72) + '…');
  ok('…elle dit quoi cliquer, et où', /cliquez/i.test(barre.texte) && /carte/i.test(barre.texte));
  ok('…et que les dossiers repliés ne sont pas des dossiers manquants',
     /calcul/i.test(barre.note), barre.note.slice(0, 70) + '…');
  ok('LE PIÈGE EST DÉSAMORCÉ : l’export ne suit PAS ce qui est à l’écran',
     /Word/i.test(barre.note) && /PDF/i.test(barre.note));

  titre('3. LE POINT QUI DÉCIDE : un clic sur la carte n’ouvre QUE ce pays');

  const premier = choisis[0];
  await pg.evaluate(c => {
    const el = document.querySelector('#fin-res .cres [data-podium="' + c + '"]');
    if (el) el.dispatchEvent(new MouseEvent('click', { bubbles: true }));
  }, premier);
  await pg.waitForFunction(
    c => { const d = document.querySelector('#fin-res .fin-dos[data-pays="' + c + '"]');
           return d && d.offsetParent !== null; },
    premier, { timeout: 15000 });

  const un = await pg.evaluate(() => {
    const vus = [...document.querySelectorAll('#fin-res .fin-dos')]
      .filter(d => d.offsetParent !== null);
    return { n: vus.length, pays: vus.map(d => d.getAttribute('data-pays')),
             dpgf: vus.length ? vus[0].querySelectorAll('.fin-tab tbody tr').length : 0,
             avis: vus.length ? !!vus[0].querySelector('.fai') : false };
  });
  ok('le dossier du pays cliqué s’ouvre', un.pays.indexOf(premier) >= 0, un.pays.join(', '));
  ok('…ET LUI SEUL', un.n === 1, un.n + ' déplié(s)');
  ok('…avec son avis de faisabilité et sa DPGF', un.avis && un.dpgf >= 10,
     un.dpgf + ' ligne(s) de lot');

  titre('4. Un deuxième clic AJOUTE, il ne remplace pas');

  const second = choisis[1];
  await pg.evaluate(c => {
    const el = document.querySelector('#fin-res .cres [data-podium="' + c + '"]');
    if (el) el.dispatchEvent(new MouseEvent('click', { bubbles: true }));
  }, second);
  await pg.waitForFunction(
    c => { const d = document.querySelector('#fin-res .fin-dos[data-pays="' + c + '"]');
           return d && d.offsetParent !== null; },
    second, { timeout: 15000 });

  const deux = await pg.evaluate(() => {
    const vus = [...document.querySelectorAll('#fin-res .fin-dos')]
      .filter(d => d.offsetParent !== null).map(d => d.getAttribute('data-pays'));
    const puces = [...document.querySelectorAll('#fin-ouvre-l [data-fermer]')]
      .map(b => b.getAttribute('data-fermer'));
    return { vus: vus, puces: puces,
             etat: (document.getElementById('fin-ouvre-v') || {}).textContent || '' };
  });
  ok('les DEUX dossiers sont ouverts', deux.vus.length === 2, deux.vus.join(', '));
  ok('…les deux autres restent repliés',
     deux.vus.indexOf(choisis[2]) < 0 && deux.vus.indexOf(choisis[3]) < 0,
     'repliés : ' + choisis.slice(2).join(', '));
  ok('…la barre nomme ceux qui sont ouverts, et offre de les replier',
     deux.puces.indexOf(premier) >= 0 && deux.puces.indexOf(second) >= 0
     && deux.puces.indexOf('*') >= 0, deux.puces.join(', '));
  ok('…et elle dit combien sur combien', /2 dossiers ouverts sur 4/.test(deux.etat),
     deux.etat.trim().slice(0, 46));

  titre('5. L’écart voyage AVEC le dossier du pays comparé');

  const ec = await pg.evaluate(() => {
    const orphelins = [...document.querySelectorAll('#fin-res > .fin-ecart')].length;
    const dedans = [...document.querySelectorAll('#fin-res .fin-dos .fin-ecart')]
      .map(e => { const s = e.closest('.fin-dos'); return s.getAttribute('data-pays'); });
    const visibles = [...document.querySelectorAll('#fin-res .fin-ecart')]
      .filter(e => e.offsetParent !== null).length;
    return { orphelins: orphelins, dedans: dedans, visibles: visibles };
  });
  ok('AUCUN écart ne flotte hors d’un dossier', ec.orphelins === 0,
     ec.orphelins + ' orphelin(s)');
  ok('…chacun est rangé dans le dossier du pays qu’il compare', ec.dedans.length === 3,
     ec.dedans.join(', '));
  ok('…et aucun écart d’un dossier replié ne s’affiche', ec.visibles <= 2,
     ec.visibles + ' visible(s) pour 2 dossiers ouverts');

  titre('6. On referme, et on revient à un état lisible');

  await pg.evaluate(c => {
    const b = document.querySelector('#fin-ouvre-l [data-fermer="' + c + '"]');
    if (b) b.click();
  }, premier);
  const apresFermeture = await pg.evaluate(() => {
    return { vus: [...document.querySelectorAll('#fin-res .fin-dos')]
                    .filter(d => d.offsetParent !== null).map(d => d.getAttribute('data-pays')),
             etat: (document.getElementById('fin-ouvre-v') || {}).textContent || '' };
  });
  ok('replier un dossier ne referme que celui-là',
     apresFermeture.vus.length === 1 && apresFermeture.vus[0] === second,
     apresFermeture.vus.join(', '));

  await pg.evaluate(() => {
    const b = document.querySelector('#fin-ouvre-l [data-fermer]');
    if (b) b.click();
  });
  const vide = await pg.evaluate(() => ({
    vus: [...document.querySelectorAll('#fin-res .fin-dos')]
           .filter(d => d.offsetParent !== null).length,
    etat: (document.getElementById('fin-ouvre-v') || {}).textContent || '' }));
  ok('…et tout replier ramène la consigne, pas un blanc',
     vide.vus === 0 && /Aucun dossier ouvert/.test(vide.etat), vide.etat.trim().slice(0, 40));

  titre('7. CE QUI PART EN WORD N’EST PAS CE QUI EST À L’ÉCRAN');

  /* Le repli est un choix d'affichage. Si l'export suivait l'écran, un lecteur
     qui n'a rien ouvert téléchargerait un dossier vide — et ne s'en rendrait
     compte qu'en le remettant. On éprouve donc la charge utile réellement
     envoyée, aucun dossier n'étant ouvert à cet instant. */
  const envoye = await pg.evaluate(async () => {
    let capte = null;
    const vrai = window.fetch;
    window.fetch = function (u, o) {
      if (String(u).indexOf('/api/export-dc') >= 0 && o && o.body) capte = String(o.body);
      return vrai.apply(this, arguments);
    };
    const b = document.querySelector('#fin-res .dl-b[data-dl="enveloppe"]');
    if (b) b.click();
    await new Promise(r => setTimeout(r, 1200));
    window.fetch = vrai;
    if (!capte) return { trouve: false };
    let j = null; try { j = JSON.parse(capte); } catch (e) { return { trouve: true, lu: false }; }
    const d = (j.devis || j).dossiers || [];
    return { trouve: true, lu: true, dossiers: d.length,
             pays: d.map(x => x.pays), ecarts: ((j.devis || j).ecarts || []).length };
  });
  ok('le téléchargement part bien avec une charge utile', envoye.trouve && envoye.lu);
  ok('LES QUATRE DOSSIERS Y SONT — aucun n’était ouvert à l’écran',
     envoye.dossiers === 4, envoye.dossiers + ' dossier(s) : ' + (envoye.pays || []).join(', '));
  ok('…et les trois écarts aussi', envoye.ecarts === 3, envoye.ecarts + ' écart(s)');

  titre('8. L’ASSIETTE SUIT LE PAYS QU’ON DÉSIGNE, en temps réel');

  /* LE DÉFAUT QUE CECI ATTRAPE. Le bloc d'honoraires lisait `classement[0]` —
     le meilleur coût total. C'était défendable tant que les dossiers se
     déroulaient tous ensemble ; depuis qu'on les ouvre PAYS PAR PAYS sur la
     carte, c'était un piège muet : on ouvrait l'Allemagne, on chiffrait, et on
     obtenait les honoraires de la France. Deux pays à l'écran, un seul dans le
     calcul, et rien pour le dire. */
  const av = await pg.evaluate(() => ({
    pays: (document.getElementById('moe-pays') || {}).value || '',
    trav: (document.getElementById('moe-trav') || {}).textContent || '',
    pt: (document.getElementById('moe-pt') || {}).textContent || '',
  }));
  ok('les deux grandeurs du barème sont affichées AVANT tout calcul',
     /M€/.test(av.trav) && /%/.test(av.pt), av.trav + ' · ' + av.pt);
  ok('…et le pays retenu est l’un des pays comparés',
     choisis.indexOf(av.pays) >= 0, av.pays + ' parmi ' + choisis.join(', '));

  /* On ouvre le dossier d'un AUTRE pays : le pays retenu doit suivre.

     CE QU'ON N'EXIGE PAS, ET POURQUOI : que les DEUX NOMBRES changent. À
     puissance et gabarit égaux, l'enveloppe est identique d'un pays à l'autre
     par construction — ce module le répète à chaque écran — et deux pays dont
     aucun lot n'est modulé différemment donnent donc la même assiette. Ma
     première version l'exigeait et tombait sur BE → BG : elle aurait fait
     corriger un comportement juste. Ce qui doit suivre, c'est le pays LU, et
     la provenance qui le nomme. */
  /* NI LE COURANT, NI LE PREMIER DU CLASSEMENT. Ma première version prenait
     « le premier qui n'est pas le courant » — c'est-à-dire, neuf fois sur dix,
     `classement[0]` lui-même. Les deux chemins concordaient alors par hasard,
     et le contrôle restait vert avec le défaut réinjecté. Un contrôle qui ne
     peut pas distinguer les deux réponses n'éprouve rien. */
  const autre = await pg.evaluate(c => {
    const p = window.FIN_DERNIER().classement.map(x => x.pays);
    return p.filter((x, i) => x !== c && i > 0)[0] || p.filter(x => x !== c)[0];
  }, av.pays);
  await pg.evaluate(c => {
    const el = document.querySelector('#fin-res .cres-pod [data-podium="' + c + '"]');
    if (el) el.dispatchEvent(new MouseEvent('click', { bubbles: true }));
  }, autre);
  await pg.waitForTimeout(600);
  const ap = await pg.evaluate(() => ({
    pays: (document.getElementById('moe-pays') || {}).value || '',
    trav: (document.getElementById('moe-trav') || {}).textContent || '',
    pt: (document.getElementById('moe-pt') || {}).textContent || '',
    src: (document.getElementById('moe-src-n') || {}).textContent || '',
  }));
  ok('OUVRIR UN AUTRE PAYS CHANGE LE PAYS RETENU', ap.pays === autre,
     av.pays + ' → ' + ap.pays);
  /* LE CONTRÔLE QUI DÉCIDE, et ma première version le manquait. Elle vérifiait
     que la provenance EXISTE, pas qu'elle nomme le pays SÉLECTIONNÉ — or c'est
     exactement là que se logeait le défaut : le sélecteur affichait la Suisse
     pendant que les grandeurs venaient d'Autriche, chacun lisant sa propre
     source. Un écran qui se contredit lui-même ne se voit qu'en confrontant
     les deux. */
  const nomAttendu = await pg.evaluate(c => (window.nomPays && window.nomPays(c)) || c, autre);
  ok('…LA PROVENANCE NOMME LE PAYS SÉLECTIONNÉ — pas un autre',
     ap.src.indexOf(nomAttendu) >= 0,
     'attendu « ' + nomAttendu +' » dans « ' + ap.src.slice(0, 58) + '… »');
  ok('…et les grandeurs restent cohérentes', /M€/.test(ap.trav) && /%/.test(ap.pt),
     ap.trav + ' · ' + ap.pt);

  /* LE CHANGEMENT DE PAYS EFFACE UN CHIFFRAGE DEVENU FAUX. Laissé à l'écran
     sous une assiette qui vient de changer, il ferait lire deux études pour
     une. */
  await pg.evaluate(() => {
    const s = document.getElementById('moe-pays');
    const p = [...s.options].map(o => o.value).filter(v => v !== s.value)[0];
    if (p) { s.value = p; s.dispatchEvent(new Event('change', { bubbles: true })); }
  });
  await pg.waitForTimeout(300);
  const efface = await pg.evaluate(() => ({
    out: (document.getElementById('moe-out') || {}).innerHTML || '',
    msg: (document.getElementById('moe-msg') || {}).textContent || '',
  }));
  ok('changer de pays au sélecteur ne laisse pas subsister un chiffrage d’un autre pays',
     !efface.out, efface.out ? 'un chiffrage subsiste' : 'effacé');

  titre('9. Le dossier se lit sur trois colonnes');

  const grille = await pg.evaluate(() => {
    const g = document.querySelector('#fin-res .fin-dos:not([hidden]) .fin-dos-g');
    if (!g) return null;
    const cs = getComputedStyle(g);
    const enfants = [...g.children];
    return {
      colonnes: cs.gridTemplateColumns.split(' ').length,
      enfants: enfants.length,
      pleine: enfants.filter(e => getComputedStyle(e).gridColumnEnd === '-1').length,
      tables_pleine: enfants.filter(e => e.tagName === 'TABLE'
        && getComputedStyle(e).gridColumnEnd === '-1').length,
      tables: enfants.filter(e => e.tagName === 'TABLE').length,
      constats: (() => { const c = document.querySelector(
        '#fin-res .fin-dos:not([hidden]) .fai-c');
        return c ? getComputedStyle(c).gridTemplateColumns.split(' ').length : 0; })(),
    };
  });
  ok('le corps du dossier est en trois colonnes', grille.colonnes === 3,
     grille.colonnes + ' colonne(s), ' + grille.enfants + ' blocs');
  ok('LES TABLEAUX GARDENT TOUTE LA LARGEUR — une DPGF de quatorze lots '
     + 'comprimée au tiers serait illisible',
     grille.tables > 0 && grille.tables_pleine === grille.tables,
     grille.tables_pleine + '/' + grille.tables);
  ok('…et les constats de l’avis se répartissent aussi', grille.constats === 3,
     grille.constats + ' colonne(s)');

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  await nav.close();
  console.log('\n' + (ko ? ko + ' contrôle(s) en échec' : 'tout est vert') + '\n');
  process.exit(ko ? 1 : 0);
})();
