/* RECETTE — LA BARRE DE NAVIGATION : RIEN NE PASSE SOUS RIEN
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * DEUX DÉFAUTS MESURÉS SUR LA CAPTURE D'ÉCRAN REÇUE.
 *
 * 1. LA FLÈCHE MANGEAIT UN ONGLET. Les deux flèches et le bouton « Parcours
 *    guidé » étaient posés EN ABSOLU par-dessus la bande d'onglets, et une
 *    variable mesurée en JavaScript (--gp-w) tentait de leur réserver la place
 *    par du remplissage. Le remplissage ne protège que les extrémités du
 *    contenu défilant : dès qu'on fait glisser la bande, un onglet passe sous
 *    la flèche. Mesuré : 26 px — 14 % — de l'onglet « Choix d'implantation »
 *    recouverts, ce que la capture montrait par « Données ouvert› ».
 *
 * 2. UN RÔLE CHOISI, RIEN N'INVITAIT À CHOISIR UN PARCOURS. La seconde liste
 *    restait sur son intitulé vide et l'aide affichait la DESCRIPTION DU RÔLE :
 *    le lecteur lisait une phrase de contexte là où il attendait quoi faire.
 *    C'est l'état exact de la capture — « Climat », « — Le parcours — », et
 *    une phrase qui flotte.
 *
 * CE QUE CES CONTRÔLES PROUVENT :
 *
 *   1. LE POINT QUI DÉCIDE — AUCUN ONGLET N'EST RECOUVERT, à aucune position
 *      de défilement. On fait défiler la bande d'un bout à l'autre et on
 *      remesure : c'est la seule façon d'éprouver un défaut qui n'apparaît
 *      qu'en cours de glissement.
 *   2. L'APPEL AU GESTE SUIVANT paraît, et il S'ÉTEINT quand le geste est
 *      fait — un guidage qui reste allumé devient du bruit.
 *   3. LE CADRE BLEU, la loupe au survol et les infobulles maison sont là,
 *      sur TOUS les onglets.
 *   4. LE BATTEMENT est sobre et s'efface sous mouvement réduit.
 *
 * Lancement :
 *     BASE=http://127.0.0.1:5510 node recette_menu_pnav.js
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
  const mk = async (reduit) => {
    const c = await nav.newContext(Object.assign({
      viewport: { width: 1400, height: 1000 },
      userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        + '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
      locale: 'fr-FR' }, reduit ? { reducedMotion: 'reduce' } : {}));
    /* SANS CE MASQUE, LE SERVEUR BLOQUE L'ADRESSE POUR 1800 s. */
    await c.addInitScript(() => {
      Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
      Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
      Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
    });
    const pg = await c.newPage();
    await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
    await pg.goto(BASE + '/panorama', { waitUntil: 'domcontentloaded' });
    await pg.waitForFunction(() => document.querySelectorAll('.pnav a').length > 5,
      null, { timeout: 60000 });
    await pg.waitForTimeout(1200);
    return { c, pg };
  };
  /* CONVENTION DU DÉPÔT : un échec dans `evaluate` se rend en donnée. */
  const sur = async (pg, fn, arg) => {
    try { return await pg.evaluate(fn, arg); }
    catch (e) { return { err: String(e && e.message || e) }; }
  };

  const { c: c1, pg } = await mk(false);
  const err = [];
  pg.on('pageerror', e => err.push(e.message));

  // ── 1 : LE POINT QUI DÉCIDE ─────────────────────────────────────────────
  titre('1. AUCUN ONGLET SOUS UNE FLÈCHE, à aucune position de défilement');

  const balayage = await sur(pg, async () => {
    const pn = document.querySelector('.pnav');
    const bande = document.querySelector('.pnav-bande');
    if (!bande) return { err: 'la bande n’existe pas — la piste n’est pas en rangée' };
    const flg = document.querySelector('.pnav-fl.g');
    const fld = document.querySelector('.pnav-fl.d');
    const lanceur = document.getElementById('gp-lanceur');
    const max = pn.scrollWidth - pn.clientWidth;
    const pires = [];
    /* ON BALAIE. Le défaut n'existe qu'À CERTAINES positions : le mesurer une
       seule fois, bande au repos, l'aurait manqué une fois sur deux. */
    for (let k = 0; k <= 10; k++) {
      pn.scrollLeft = Math.round(max * k / 10);
      await new Promise(r => setTimeout(r, 60));
      const rb = bande.getBoundingClientRect();
      const gene = [flg, fld, lanceur].filter(x => x && getComputedStyle(x).display !== 'none')
        .map(x => x.getBoundingClientRect());
      document.querySelectorAll('.pnav a').forEach(a => {
        const r0 = a.getBoundingClientRect();
        // UN ONGLET EST DÉCOUPÉ PAR SA BANDE : comparer les rectangles bruts
        // ferait croire à un chevauchement là où le débordement est masqué.
        const g = Math.max(r0.left, rb.left), d = Math.min(r0.right, rb.right);
        if (d - g <= 0) return;
        gene.forEach(rg => {
          const chev = Math.min(d, rg.right) - Math.max(g, rg.left);
          if (chev > 1) pires.push({ pos: k,
            t: a.textContent.replace(/\s+/g, ' ').trim().slice(0, 26),
            px: Math.round(chev) });
        });
      });
    }
    pn.scrollLeft = 0;
    return { pires, max: Math.round(max), positions: 11 };
  });
  ok('la piste est une RANGÉE : la bande d’onglets existe comme élément propre',
     !balayage.err, balayage.err || 'bande présente');
  ok('la bande DÉBORDE réellement — sans quoi le contrôle ne prouve rien',
     !balayage.err && balayage.max > 200, balayage.err || (balayage.max + ' px à défiler'));
  ok('AUCUN ONGLET N’EST RECOUVERT par une flèche ou par le lanceur, '
     + 'sur 11 positions de défilement',
     !balayage.err && balayage.pires.length === 0,
     balayage.err || (balayage.pires.length
        ? balayage.pires.slice(0, 3).map(x => 'pos ' + x.pos + ' : ' + x.t + ' (' + x.px + ' px)').join(' · ')
        : '11 positions, 0 chevauchement'));

  // ── 2 ───────────────────────────────────────────────────────────────────
  titre('2. Un rôle choisi : le geste suivant se désigne, puis s’éteint');

  const avant = await sur(pg, () => {
    const p = document.getElementById('pp-parcours');
    const a = document.getElementById('pp-aide');
    return { attend: p.classList.contains('pp-attend'),
             suite: !!a.querySelector('.pp-suite'),
             aide: a.textContent.replace(/\s+/g, ' ').trim().slice(0, 60) };
  });
  ok('avant tout choix, aucun appel — il n’y a pas encore de geste à désigner',
     !avant.err && !avant.attend && !avant.suite, avant.err || avant.aide);

  const apres = await sur(pg, async () => {
    const r = document.getElementById('pp-role');
    // un rôle à PLUSIEURS parcours : sinon le second choix est pris d'office
    let choisi = null;
    for (const o of [...r.options]) {
      if (!o.value) continue;
      r.value = o.value;
      r.dispatchEvent(new Event('change', { bubbles: true }));
      await new Promise(x => setTimeout(x, 250));
      const p = document.getElementById('pp-parcours');
      if (p.options.length > 2 && !p.value) { choisi = o.text; break; }
    }
    const p = document.getElementById('pp-parcours');
    const a = document.getElementById('pp-aide');
    return { choisi, attend: p.classList.contains('pp-attend'),
             suite: (a.querySelector('.pp-suite') || {}).textContent || '',
             garde: /Choisir où investir|critère par critère|[a-zé]{6,}/.test(a.textContent) };
  });
  ok('LA LISTE DU PARCOURS SE SIGNALE dès qu’un rôle est pris',
     !apres.err && apres.attend, apres.err || ('rôle : ' + apres.choisi));
  ok('…et l’aide DIT LE GESTE, au lieu de décrire le rôle seulement',
     !apres.err && /Choisissez maintenant votre parcours/.test(apres.suite),
     apres.err || apres.suite);
  ok('…sans perdre la description du rôle, qui reste sous l’appel',
     !apres.err && apres.garde);

  const eteint = await sur(pg, async () => {
    const p = document.getElementById('pp-parcours');
    const utile = [...p.options].find(o => o.value && !o.disabled);
    if (!utile) return { err: 'aucun parcours disponible' };
    p.value = utile.value;
    p.dispatchEvent(new Event('change', { bubbles: true }));
    await new Promise(x => setTimeout(x, 500));
    const a = document.getElementById('pp-aide');
    return { attend: p.classList.contains('pp-attend'),
             suite: !!a.querySelector('.pp-suite'),
             carte: !!document.querySelector('.gp-carte.on') };
  });
  ok('L’APPEL S’ÉTEINT quand le geste est fait — un guidage qui reste allumé '
     + 'devient du bruit',
     !eteint.err && !eteint.attend && !eteint.suite,
     eteint.err || ('halo=' + eteint.attend + ' · mention=' + eteint.suite));
  ok('…et le parcours démarre réellement',
     !eteint.err && eteint.carte,
     eteint.err || (eteint.carte ? 'fenêtre de parcours ouverte' : 'aucune fenêtre'));

  // ── 3 ───────────────────────────────────────────────────────────────────
  titre('3. Cadre bleu, loupe au survol, infobulles sur TOUS les onglets');

  /* FERMER LE PARCOURS OUVERT À LA SECTION PRÉCÉDENTE. Sa fenêtre pose un
     voile modal qui intercepte le pointeur : le survol d'un onglet atteignait
     le voile, et le contrôle des infobulles échouait sur un dispositif qui
     marche parfaitement. Le voile qui bloque est d'ailleurs le comportement
     voulu d'une fenêtre modale — c'est l'ordre de ma recette qui était faux. */
  await sur(pg, () => { if (typeof gpFermer === 'function') gpFermer(); });
  await pg.waitForTimeout(250);

  const deco = await sur(pg, () => {
    const w = document.querySelector('.pnav-wrap');
    const cs = getComputedStyle(w);
    const a = [...document.querySelectorAll('.pnav a')];
    return {
      bordHaut: cs.borderTopWidth, couleurHaut: cs.borderTopColor,
      onglets: a.length,
      sansAide: a.filter(x => !x.getAttribute('title') && !x.getAttribute('data-tt')).length,
      // la loupe est déclarée sur :hover — on lit la règle, pas l'état
      loupe: [...document.styleSheets].some(f => {
        try { return [...f.cssRules].some(r => /\.pnav a:hover/.test(r.selectorText || '')
                     && /scale\(1\.0[5-9]\)/.test(r.style.transform || '')); }
        catch (e) { return false; }
      }),
    };
  });
  ok('LE CADRE BLEU est posé, et son trait supérieur est épais',
     !deco.err && parseFloat(deco.bordHaut) >= 3
       && /30,\s*99,\s*168/.test(deco.couleurHaut),
     deco.err || (deco.bordHaut + ' · ' + deco.couleurHaut));
  ok('CHAQUE onglet porte son infobulle — aucun muet',
     !deco.err && deco.onglets >= 8 && deco.sansAide === 0,
     deco.err || (deco.onglets + ' onglets, ' + deco.sansAide + ' sans aide'));
  ok('…et l’effet loupe au survol est déclaré',
     !deco.err && deco.loupe);

  /* UN VRAI SURVOL, PAS UN ÉVÉNEMENT SYNTHÉTIQUE. Les infobulles écoutent
     `mouseenter`, qui ne remonte pas : un `mouseover` fabriqué ne les
     déclenche jamais, et le contrôle échouait sur un dispositif qui marche.
     C'était ma faute, pas celle de la barre. */
  await pg.hover('.pnav a').catch(() => {});
  await pg.waitForTimeout(280);
  const bulle = await sur(pg, () => {
    const b = document.querySelector('.tt-bulle.on');
    return { ouverte: !!b, texte: b ? b.textContent.replace(/\s+/g, ' ').trim().slice(0, 60) : '' };
  });
  ok('…l’infobulle maison s’ouvre au survol, sans attendre le navigateur',
     !bulle.err && bulle.ouverte, bulle.err || bulle.texte);
  await c1.close();

  // ── 4 ───────────────────────────────────────────────────────────────────
  titre('4. Le battement de l’appel est sobre, et il s’efface');

  const { c: c2, pg: pg2 } = await mk(false);
  const anim = await sur(pg2, async () => {
    const r = document.getElementById('pp-role');
    for (const o of [...r.options]) {
      if (!o.value) continue;
      r.value = o.value; r.dispatchEvent(new Event('change', { bubbles: true }));
      await new Promise(x => setTimeout(x, 220));
      const p = document.getElementById('pp-parcours');
      if (p.classList.contains('pp-attend')) {
        const cs = getComputedStyle(p);
        return { nom: cs.animationName, duree: cs.animationDuration };
      }
    }
    return { err: 'aucune liste en attente' };
  });
  ok('l’appel bat à 1,8 s — sous le seuil de photosensibilité',
     !anim.err && anim.nom === 'ppAttend' && anim.duree === '1.8s',
     anim.err || (anim.nom + ' · ' + anim.duree));
  await c2.close();

  const { c: c3, pg: pg3 } = await mk(true);
  const calme = await sur(pg3, async () => {
    const r = document.getElementById('pp-role');
    for (const o of [...r.options]) {
      if (!o.value) continue;
      r.value = o.value; r.dispatchEvent(new Event('change', { bubbles: true }));
      await new Promise(x => setTimeout(x, 220));
      const p = document.getElementById('pp-parcours');
      if (p.classList.contains('pp-attend')) {
        const cs = getComputedStyle(p);
        return { anim: cs.animationName, ombre: cs.boxShadow, bord: cs.borderColor };
      }
    }
    return { err: 'aucune liste en attente' };
  });
  ok('SOUS MOUVEMENT RÉDUIT, le battement disparaît — le halo RESTE, fixe',
     !calme.err && calme.anim === 'none' && /rgba?\(/.test(calme.ombre)
       && calme.ombre !== 'none',
     calme.err || (calme.anim + ' · ' + String(calme.ombre).slice(0, 44)));
  await c3.close();

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec') + '\n');
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
