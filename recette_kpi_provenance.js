/* LES ENTRÉES DE CRÉATION DE VALEUR : D'OÙ VIENT CHAQUE CHIFFRE.
 *
 * CE QUE CE BLOC PRÉSENTAIT. Sept cases vides. Le lecteur venait de faire
 * calculer une enveloppe complète — investissement, exploitation, DPGF, coût
 * total — et on lui redemandait tout à zéro, sans lui dire lesquelles de ces
 * sept valeurs son propre calcul rendait déductibles. On saisissait au jugé, ou
 * on renonçait.
 *
 * LA LIGNE QUE CE FICHIER GARDE. Proposer n'est pas inventer — et c'est la
 * NATURE annoncée de chaque chiffre qui fait la différence. Trois natures
 * seulement, et chacune se vérifie : « calculé » pour ce qui sort de
 * l'enveloppe par une formule écrite, « statutaire » pour un taux publié par
 * un État, « jalon » pour ce qui n'est NI l'un NI l'autre — un repère rond
 * posé pour éprouver la sensibilité du résultat.
 *
 * LE COÛT DU CAPITAL ET LE TAUX D'IMPÔT étaient refusés, motif juste : ce sont
 * des décisions, pas des résultats. Mais une case obligatoire et vide n'est pas
 * neutre non plus — elle se remplit au jugé, ou elle arrête le lecteur. Les
 * deux reçoivent donc un menu, ET une RÉSERVE qui dit ce que ce menu n'est pas.
 * C'est cette réserve que ce fichier garde désormais : sans elle, quatre
 * chiffres ronds dans une liste déroulante passeraient pour une référence de
 * marché que ce module n'a pas.
 *
 * LES QUATRE POINTS PROTÉGÉS :
 *   1. chaque menu de décision porte sa RÉSERVE — sans quoi il promettrait une
 *      autorité qu'il n'a pas ;
 *   2. chaque valeur affichée dit D'OÙ ELLE VIENT, et le badge suit quand le
 *      lecteur retape — laisser « enveloppe » sur un chiffre saisi à la main
 *      serait un mensonge sur l'origine ;
 *   3. le seuil de revenu est un SEUIL, jamais une prévision, et il n'apparaît
 *      qu'une fois les deux décisions prises ;
 *   4. le pré-remplissage ne piétine aucune valeur déjà saisie, et rend compte
 *      de ce qu'il n'a PAS rempli.
 *
 *   POUR L'EXÉCUTER :  BASE=http://127.0.0.1:5501 node recette_kpi_provenance.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5501';
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

  await ctx.route('**/*', r => (['image', 'font', 'media'].includes(r.request().resourceType())
    ? r.abort() : r.continue()));
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e)));
  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg.goto(BASE + '/enveloppe', { waitUntil: 'domcontentloaded' });

  titre('1. Le calcul d’enveloppe, puis la première lecture de valeur');

  /* AUCUNE ATTENTE NUE DANS LA MISE EN PLACE NON PLUS. Une régression qui casse
     le script de la page fait échouer la TOUTE PREMIÈRE attente : `waitForFunction`
     levait alors un « Timeout 30000ms exceeded » avec une pile Node, et ce
     fichier mourait AVANT d'avoir imprimé l'erreur de page qu'il venait pourtant
     de recueillir — un `SyntaxError` déjà dans `err`, c'est-à-dire le diagnostic
     exact, perdu. On rend donc l'échec de mise en place comme un contrôle nommé,
     ET on montre les erreurs de script : la cause avec le symptôme. */
  const abandon = async (quoi, detail) => {
    ok(quoi, false, detail + (err.length ? ' | erreur de script : ' + err[0] : ''));
    await nav.close();
    console.log('\n' + ko + ' contrôle(s) en échec\n');
    process.exit(1);
  };
  const attendre = fn => fn().then(() => true).catch(() => false);

  if (!await attendre(() => pg.waitForFunction(
        () => document.querySelectorAll('#fin-pays button[data-p]').length > 0,
        null, { timeout: 30000 }))) {
    await abandon('LA PAGE D’ENVELOPPE S’ARME',
                  'aucun pays proposé dans #fin-pays après 30 s');
  }
  await pg.click('#fin-go');
  if (!await attendre(() => pg.waitForSelector('#fin-res .fin-dos',
        { state: 'attached', timeout: 60000 }))) {
    await abandon('LE CALCUL D’ENVELOPPE ABOUTIT', 'aucun dossier rendu après 60 s');
  }
  if (!await attendre(() => pg.waitForSelector('#kpi-form .kpi-ch',
        { timeout: 30000 }))) {
    await abandon('LE BLOC DE CRÉATION DE VALEUR EST LÀ',
                  'aucune entrée dans #kpi-form');
  }
  await pg.click('#kpi-go');
  /* NE PAS LEVER : si les propositions n’arrivent pas, c’est le défaut traqué,
     et il doit être NOMMÉ plutôt que rendu comme un « Timeout ». */
  if (!await attendre(() => pg.waitForSelector('#kpi-form .kpi-src',
        { timeout: 45000 }))) {
    await abandon('LES MENUS DE PROVENANCE APPARAISSENT',
                  'aucun .kpi-src après le calcul : le bloc reste sept cases vides');
  }
  /* AUCUN DÉRÉFÉRENCEMENT NU DANS CE FICHIER. Une régression qui EFFACE un
     élément est plus grave que celle qu'on traque, pas moins : si l'évaluation
     lève, Playwright rend « Cannot read properties of null » et le contrôle se
     lit comme une panne d'outil au lieu du défaut trouvé. Chaque absence est
     donc NOMMÉE et rendue comme une donnée. */
  const f0 = await pg.evaluate(() => ({
    champs: document.querySelectorAll('#kpi-form .kpi-ch').length,
    menus: document.querySelectorAll('#kpi-form .kpi-src').length,
    refus: [...document.querySelectorAll('#kpi-form .kpi-refus')].map(x => {
      const l = x.closest('.kpi-ch') && x.closest('.kpi-ch').querySelector('label');
      return l ? l.textContent.trim() : '(refus hors de toute entrée)';
    }),
    pre: !!document.getElementById('kpi-pre')
      && !document.getElementById('kpi-pre').hidden,
    manquePre: !document.getElementById('kpi-pre'),
  }));
  ok('les sept entrées sont là', f0.champs === 7, f0.champs + ' entrées');
  ok('des menus de provenance apparaissent', f0.menus >= 4, f0.menus + ' menus');
  ok('le bouton de pré-remplissage devient disponible', f0.pre,
     f0.manquePre ? '#kpi-pre est ABSENT de la page' : '');

  titre('2. LE POINT QUI DÉCIDE : ce qu’un chiffre proposé annonce de lui-même');

  /* CE CONTRÔLE GARDAIT UN REFUS QUI N'EXISTE PLUS. Le coût du capital et le
     taux d'impôt étaient refusés — motif juste : ce sont des décisions. Mais
     un champ obligatoire et vide n'est pas neutre : il se remplit au jugé, ou
     il arrête le lecteur. Les deux reçoivent désormais un MENU.

     CE QUI ÉTAIT PROTÉGÉ RESTE PROTÉGÉ, et c'est ce que ces contrôles suivent
     maintenant : le lecteur ne doit jamais prendre pour une donnée de marché
     un chiffre qui n'en est pas. La RÉSERVE porte cette distinction, et la
     NATURE de chaque proposition la porte jusque dans la donnée servie. */
  const menus = await pg.evaluate(() => {
    const m = {};
    document.querySelectorAll('#kpi-form select.kpi-src').forEach(s => {
      m[s.id.replace('kpi-s-', '')] = s.options.length - 1;
    });
    return { menus: m,
             reserves: [...document.querySelectorAll('#kpi-form .kpi-reserve')]
               .map(x => x.textContent) };
  });
  ok('LES DEUX DÉCISIONS REÇOIVENT UN MENU — plus de case nue et obligatoire',
     menus.menus.wacc >= 4 && menus.menus.is_taux >= 4,
     'CMPC ' + menus.menus.wacc + ' · IS ' + menus.menus.is_taux + ' options');
  ok('…et CHACUN porte sa réserve, sans quoi il promettrait une autorité qu’il n’a pas',
     menus.reserves.length >= 2, menus.reserves.length + ' réserve(s)');
  ok('…les coûts du capital se déclarent NON DONNÉES DE MARCHÉ',
     menus.reserves.some(t => /PAS une référence de marché/i.test(t)),
     (menus.reserves.find(t => /marché/i.test(t)) || '').slice(0, 60));
  ok('…et les taux d’impôt se déclarent NOMINAUX, donc à confirmer',
     menus.reserves.some(t => /NOMINAUX/.test(t) && /conseil fiscal/i.test(t)),
     (menus.reserves.find(t => /NOMINAUX/.test(t)) || '').slice(0, 60));
  /* LE REVENU, LUI, RESTE REFUSÉ TANT QUE LES DEUX TAUX MANQUENT : ses paliers
     s'inversent depuis eux, et sans eux il n'y a rien à inverser. C'est un
     refus D'ATTENTE, et la section 4 vérifie qu'il se lève. */
  ok('le revenu reste refusé tant que les deux taux manquent — refus d’attente',
     f0.refus.length === 1 && /revenu/i.test(f0.refus[0]),
     f0.refus.join(' | ') || 'aucun refus');

  titre('3. Chaque valeur dit d’où elle vient — et le badge suit');

  const b1 = await pg.evaluate(async () => {
    const sel = document.getElementById('kpi-s-amort_ans');
    const ch = document.getElementById('kpi-amort_ans');
    const bd = document.getElementById('kpi-o-amort_ans');
    if (!sel || !ch || !bd) {
      return { manque: [!sel && '#kpi-s-amort_ans', !ch && '#kpi-amort_ans',
                        !bd && '#kpi-o-amort_ans'].filter(Boolean).join(' ') };
    }
    sel.value = '0';
    sel.dispatchEvent(new Event('change', { bubbles: true }));
    await new Promise(r => setTimeout(r, 150));
    return { valeur: ch.value, badge: bd.textContent, classe: bd.className };
  });
  ok('choisir une provenance remplit le champ', !!b1 && b1.valeur !== undefined
     && b1.valeur !== '', b1 && (b1.manque ? 'ABSENT : ' + b1.manque : b1.valeur));
  ok('…et le badge nomme cette provenance',
     !!b1 && !!b1.badge && /enveloppe/.test(b1.badge),
     b1 && (b1.manque ? 'ABSENT : ' + b1.manque : b1.badge));

  /* LE CONTRÔLE QUI COMPTE ICI : retaper doit DÉFAIRE la provenance. */
  const b2 = await pg.evaluate(async () => {
    const c = document.getElementById('kpi-amort_ans');
    const bd = document.getElementById('kpi-o-amort_ans');
    const sel = document.getElementById('kpi-s-amort_ans');
    if (!c || !bd || !sel) {
      return { manque: [!c && '#kpi-amort_ans', !bd && '#kpi-o-amort_ans',
                        !sel && '#kpi-s-amort_ans'].filter(Boolean).join(' ') };
    }
    c.value = '15';
    c.dispatchEvent(new Event('input', { bubbles: true }));
    await new Promise(r => setTimeout(r, 150));
    return { badge: bd.textContent, menu: sel.value };
  });
  ok('UNE VALEUR RETAPÉE CESSE D’ÊTRE « PROPOSÉE »',
     !!b2 && !!b2.badge && /saisie/.test(b2.badge) && b2.menu === '',
     b2 && (b2.manque ? 'ABSENT : ' + b2.manque
                      : 'badge=' + b2.badge + ' menu=' + (b2.menu || '(vide)')));

  titre('4. Le seuil de revenu — un seuil, pas une prévision');

  const av = await pg.evaluate(() => !!document.getElementById('kpi-s-revenu_meur_an'));
  ok('sans les deux décisions, AUCUN revenu n’est proposé', !av);
  const refRev = await pg.evaluate(() => {
    const z = [...document.querySelectorAll('#kpi-form .kpi-ch')]
      .find(x => /Revenu annuel/.test(x.textContent));
    const r = z && z.querySelector('.kpi-refus');
    return r ? r.textContent : null;
  });
  ok('…et le motif dit qu’il le sera dès que les deux le seront',
     !!refRev && /coût du capital et le taux d[’']impôt/.test(refRev),
     refRev ? '' : 'aucun motif de refus sur le revenu');

  /* On prend les deux décisions, on relance : le seuil doit apparaître. */
  await pg.evaluate(() => {
    document.getElementById('kpi-wacc').value = '8';
    document.getElementById('kpi-is_taux').value = '25';
  });
  await pg.click('#kpi-go');
  const ap = await pg.waitForSelector('#kpi-s-revenu_meur_an', { timeout: 45000 })
    .then(() => true).catch(() => false);
  ok('LE SEUIL DE REVENU APPARAÎT une fois les deux décisions prises', ap);
  /* ET PLUS AUCUN REFUS NE DEMEURE : celui du revenu était un refus D'ATTENTE,
     il se lève dès que les deux taux sont posés. Les deux autres n'existent
     plus — ils sont devenus des menus, chacun sous sa réserve. */
  const refApres = await pg.evaluate(() =>
    document.querySelectorAll('#kpi-form .kpi-refus').length);
  ok('…et le refus d’attente du revenu s’est levé', refApres === 0,
     refApres + ' refus restants');
  if (ap) {
    const t = await pg.evaluate(() => {
      const s = document.getElementById('kpi-s-revenu_meur_an');
      return [...s.options].map(o => o.textContent).join(' | ');
    });
    ok('…et il s’annonce comme un ÉQUILIBRE, pas comme une prévision',
       /équilibre/i.test(t) && /EVA/.test(t), t.slice(0, 90));
  }

  titre('5. Le pré-remplissage ne piétine rien, et rend compte');

  const pre = await pg.evaluate(async () => {
    /* Une valeur déjà saisie, qui doit SURVIVRE au pré-remplissage. */
    const c = document.getElementById('kpi-montee_ans');
    const b = document.getElementById('kpi-pre');
    const z = document.getElementById('kpi-prerempli');
    if (!c || !b || !z) {
      return { manque: [!c && '#kpi-montee_ans', !b && '#kpi-pre',
                        !z && '#kpi-prerempli'].filter(Boolean).join(' ') };
    }
    c.value = '7';
    c.dispatchEvent(new Event('input', { bubbles: true }));
    b.click();
    await new Promise(r => setTimeout(r, 300));
    return { montee: c.value, compte: z.textContent, visible: !z.hidden };
  });
  const absent = pre && pre.manque ? 'ABSENT : ' + pre.manque : '';
  ok('LA VALEUR DÉJÀ SAISIE N’EST PAS ÉCRASÉE', !!pre && pre.montee === '7',
     absent || (pre && pre.montee));
  ok('le compte rendu s’affiche', !!pre && pre.visible === true, absent);
  /* CE CONTRÔLE ÉTAIT ÉPINGLÉ SUR UNE FORMULE — « entrée(s) pré-remplie(s) ».
     Il est tombé le jour où le bouton a changé de rôle : les quatre valeurs de
     référentiel se posant désormais seules à l'ouverture, il ne pose plus que
     le revenu d'équilibre, et le libellé le dit. Ce qu'il protège ne dépend
     pas des mots : le compte rendu doit ANNONCER UN NOMBRE d'entrées. */
  ok('…il dit combien d’entrées ont été remplies',
     !!pre && !!pre.compte && /\d+\s*entrée\(s\)\s+\S+/.test(pre.compte),
     absent || (pre && (pre.compte || '').replace(/\s+/g, ' ').slice(0, 70)));
  /* CES DEUX CONTRÔLES GARDAIENT UN COMPTE RENDU DE CE QUI N'AVAIT PAS ÉTÉ
     REMPLI — « 2 laissées vides délibérément ». Il n'y en a plus : les deux
     décisions ont désormais leur menu, et le bouton ne pose plus que le revenu
     d'équilibre. Exiger encore cette phrase reviendrait à demander au module
     d'annoncer un refus qu'il ne fait plus.

     CE QUI COMPTE VRAIMENT À CET ENDROIT N'A PAS CHANGÉ : le geste doit dire ce
     qu'il vient de faire, et SURTOUT avertir que le revenu posé est un cas
     limite et non une prévision. C'est le seul chiffre de ce bloc qui, mal lu,
     ferait conclure « projet à l'équilibre » sur une hypothèse renvoyée au
     lecteur. */
  ok('…et il AVERTIT que le revenu posé est un équilibre, pas une prévision',
     !!pre && !!pre.compte && /n’est pas une prévision/i.test(pre.compte)
       && /équilibre/i.test(pre.compte),
     absent || (pre && pre.compte.replace(/\s+/g, ' ').slice(0, 110)));
  ok('…en nommant ce que ce cas limite sert à voir',
     !!pre && !!pre.compte && /au-dessus/i.test(pre.compte)
       && /en dessous/i.test(pre.compte),
     absent);
  /* ET IL N'ANNONCE PAS DE REFUS QU'IL NE FAIT PLUS : un compte rendu qui
     parlerait encore d'entrées « laissées vides délibérément » alors qu'aucune
     ne l'est décrirait faussement ce que le lecteur a sous les yeux. */
  ok('…et il ne prétend PAS avoir laissé des entrées de côté quand il n’en laisse aucune',
     !!pre && !!pre.compte
       && (/laissée\(s\) vide\(s\)/.test(pre.compte)
             === /\d+ laissée\(s\) vide\(s\)/.test(pre.compte)),
     absent);

  titre('6. Infobulles et parcours guidé');

  const inf = await pg.evaluate(() =>
    [...document.querySelectorAll('#kpi-form [data-aide]:not(.aide)')]
      .map(x => ({ cle: x.getAttribute('data-aide'),
                   bouton: !!x.querySelector(':scope > .aide') })));
  ok('chaque entrée porte une infobulle', inf.length === 7, inf.length + ' infobulles');
  ok('…et chacune est branchée', inf.every(x => x.bouton),
     inf.filter(x => !x.bouton).map(x => x.cle).join(' ') || 'toutes');
  const bulle = await pg.evaluate(async () => {
    const b = document.querySelector('#kpi-form .aide');
    if (!b) return null;
    b.click();
    await new Promise(r => setTimeout(r, 300));
    const z = document.querySelector('.aide-bulle.on');
    return z ? (z.innerText || '').replace(/\s+/g, ' ') : '';
  });
  ok('une infobulle s’ouvre et porte la QUESTION du référentiel',
     !!bulle && bulle.length > 40, (bulle || '').slice(0, 80));
  ok('…et dit ce que le module n’estime PAS à votre place',
     !!bulle && /pas à votre place/.test(bulle));

  const gp = await pg.evaluate(async () => {
    const a = document.querySelector('[data-gp-kpi]');
    if (!a) return null;
    a.click();
    await new Promise(r => setTimeout(r, 600));
    const c = document.getElementById('gp-carte'), ch = document.getElementById('gp-choix');
    return !!((c && c.classList.contains('on')) || (ch && ch.classList.contains('on')));
  });
  ok('le lien de parcours ouvre réellement un parcours', gp === true);

  ok('aucune erreur de script', err.length === 0, err.slice(0, 2).join(' | '));

  await nav.close();
  console.log('\n' + (ko ? ko + ' contrôle(s) en échec' : 'tout est vert') + '\n');
  process.exit(ko ? 1 : 0);
})();
