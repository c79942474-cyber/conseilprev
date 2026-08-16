/* LES NOUVEAUX BLOCS D'EAU ET D'IMPLANTATION, VUS DEPUIS LA PAGE.
 *
 * CE QUE LA RECETTE PYTHON NE PEUT PAS DIRE. Elle éprouve le référentiel et le
 * calcul, et c'est l'essentiel. Elle ne voit pas si le lecteur, lui, voit
 * quelque chose : un référentiel juste et un rendu muet donnent exactement le
 * même écran qu'avant. Trois choses ne se prouvent donc qu'ici.
 *
 *   1. LES BLOCS EXISTENT ET PORTENT LEUR CONTENU. Les repères, les origines
 *      d'eau, les familles hors parc, le paradoxe, le cadre juridique.
 *
 *   2. L'AVERTISSEMENT DU CIRCUIT OUVERT SE VOIT. C'est le seul endroit où le
 *      modèle est en défaut ; si la mention se perd au rendu, la ligne se lit
 *      comme un excellent résultat — l'inverse exact de ce qu'elle dit.
 *
 *   3. TOUT CELA SE LIT. Deux collisions de classes ont failli passer :
 *      `eau-t` est la PISTE des fourchettes et `eau-f` leur SEGMENT en position
 *      absolue. Les réutiliser aurait cassé les deux blocs sans lever d'erreur.
 *      On mesure donc le contraste RÉELLEMENT PEINT — en compositant les fonds
 *      des ancêtres, parce que getComputedStyle rend rgba(0,0,0,0) pour un fond
 *      hérité et ment alors d'un facteur trois.
 *
 *   POUR L'EXÉCUTER :
 *     BASE=http://127.0.0.1:5411 node recette_eau_sources_ui.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5411';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';
let ko = 0;
const ok = (n, c, d) => {
  console.log('  ' + (c ? 'OK ' : 'KO ') + '  ' + n + (d && !c ? ' — ' + d : (d ? ' — ' + d : '')));
  if (!c) ko++;
};
const titre = t => console.log('\n══ ' + t + ' ══\n');

/* Le contraste RÉELLEMENT PEINT. getComputedStyle rend rgba(0,0,0,0) pour un
   fond hérité : il faut remonter les ancêtres jusqu'au premier fond opaque, et
   appliquer les opacités rencontrées. Sans cela on mesure un contraste qui
   n'existe sur aucun écran. */
const MESURE = `(el) => {
  const lum = (c) => { const a = c.map(v => { v /= 255;
    return v <= 0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); });
    return 0.2126*a[0] + 0.7152*a[1] + 0.0722*a[2]; };
  const rgb = (s) => { const m = String(s).match(/[\\d.]+/g); return m ? m.map(Number) : null; };
  const melange = (av, ar, alpha) => av.map((v,i) => v*alpha + ar[i]*(1-alpha));
  let fond = [255,255,255], pile = [];
  for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
    const cs = getComputedStyle(n), c = rgb(cs.backgroundColor);
    pile.push(parseFloat(cs.opacity));
    if (c && (c.length < 4 || c[3] > 0.99)) { fond = c.slice(0,3); break; }
    if (c && c.length === 4 && c[3] > 0) pile.push(-1), fond = fond;
  }
  const cs = getComputedStyle(el);
  let txt = rgb(cs.color) || [0,0,0];
  const op = pile.filter(x => x > 0 && x <= 1).reduce((a,b) => a*b, 1);
  if (op < 1) txt = melange(txt.slice(0,3), fond, op);
  if (txt.length === 4 && txt[3] < 1) txt = melange(txt.slice(0,3), fond, txt[3]);
  const l1 = lum(txt.slice(0,3)), l2 = lum(fond);
  return Math.round(((Math.max(l1,l2)+0.05)/(Math.min(l1,l2)+0.05)) * 100) / 100;
}`;

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
  /* L'ADRESSE A CHANGÉ, ET CETTE RECETTE A FAILLI LE MANQUER. Le bilan d'eau
     vit dans la section d'empreinte, et l'empreinte est devenue un module à
     part : cette recette continuait d'ouvrir /panorama, où la section n'est
     plus. C'est la panne exacte que ce dépôt a déjà rencontrée deux fois en
     déplaçant un module — et elle l'a DITE cette fois, au lieu d'expirer sur un
     « Timeout » qu'on aurait pris pour une panne d'outil. C'est tout l'intérêt
     d'un échec nommé. */
  await pg.goto(BASE + '/empreinte-parc', { waitUntil: 'domcontentloaded' });

  titre('1. Le modèle confronté aux repères publiés');

  /* NE PAS LEVER sur l'attente : si le bloc n'arrive pas, c'est le défaut même
     qu'on traque, et il doit être NOMMÉ — pas rendu comme un « Timeout » qu'on
     prendrait pour une panne d'outil. */
  const vu = await pg.waitForSelector('#eau-source .eau-conf', { timeout: 60000 })
    .then(() => true).catch(() => false);
  if (!vu) {
    ok('LE BLOC DE CONFRONTATION S’AFFICHE', false,
       'aucun .eau-conf dans #eau-source après 60 s : le calcul est fait mais '
       + 'le lecteur ne le voit pas');
    await nav.close();
    console.log('\n' + (ko + 1) + ' contrôle(s) en échec\n');
    process.exit(1);
  }
  const conf = await pg.evaluate(() => {
    const z = document.querySelector('#eau-source .eau-conf');
    return { texte: (z.innerText || '').replace(/\s+/g, ' '),
             reperes: [...z.querySelectorAll('.eau-rp b')].map(b => b.textContent.trim()),
             large: z.classList.contains('large') };
  });
  ok('les deux repères publiés sont affichés', conf.reperes.length === 2,
     conf.reperes.join(' · '));
  ok('…avec leur périmètre et leur éditeur',
     /Arcep/.test(conf.texte) && /Berkeley/.test(conf.texte));
  ok('LE BLOC REFUSE DE PRENDRE LA CONTENANCE POUR UNE VALIDATION',
     /pas une validation/.test(conf.texte));
  ok('…et il est teinté en conséquence, pas en vert de réussite', conf.large);
  ok('la France est confrontée à son propre repère',
     /France seule/.test(conf.texte));

  titre('2. D’où vient l’eau');

  const src = await pg.evaluate(() => {
    const l = [...document.querySelectorAll('#eau-source .eau-s')];
    return { n: l.length,
             premier: l.length ? l[0].querySelector('em').textContent.trim() : '',
             tensions: l.map(x => x.querySelector('.eau-tn').textContent.trim()),
             potable: l.some(x => /potable/i.test(x.textContent)
                                  && /Arcep|quasi-totalité/i.test(x.textContent)) };
  });
  ok('les origines d’eau sont affichées', src.n >= 5, src.n + ' origines');
  ok('la plus tendue vient en tête', /potable/i.test(src.premier), src.premier);
  ok('…et porte le constat de l’Arcep', src.potable);
  ok('les coefficients sont posés en PASTILLE, pas en barre',
     src.tensions.length === src.n && src.tensions.every(t => /^[0-9]/.test(t)),
     src.tensions.join(' '));

  titre('3. LE POINT QUI DÉCIDE : le circuit ouvert ne se lit pas comme sobre');

  const hp = await pg.evaluate(() => {
    const l = [...document.querySelectorAll('#eau-source .eau-h')];
    return l.map(x => ({
      nom: (x.querySelector('b') || {}).textContent || '',
      alerte: x.classList.contains('alerte'),
      avert: !!x.querySelector('.eau-hm'),
      texte: (x.innerText || '').replace(/\s+/g, ' '),
    }));
  });
  ok('les trois familles hors parc sont affichées', hp.length === 3,
     hp.map(x => x.nom).join(' · '));
  const riv = hp.find(x => /circuit ouvert/i.test(x.nom));
  ok('le circuit ouvert figure parmi elles', !!riv);
  if (riv) {
    ok('IL PORTE SON AVERTISSEMENT, VISIBLEMENT', riv.avert && riv.alerte);
    ok('…qui dit que l’eau est restituée, non consommée',
       /RESTITUÉE/.test(riv.texte));
    ok('…et nomme les deux impacts que le calcul ne voit pas',
       /débit/.test(riv.texte) && /échauffement/.test(riv.texte));
    /* Le piège se referme ici : la ligne ne doit PAS afficher un WUE flatteur
       à côté de son avertissement — le chiffre l’emporterait sur le texte. */
    ok('…et n’affiche AUCUN chiffre de WUE qui contredirait l’avertissement',
       !/WUE de site/.test(riv.texte));
  }
  const dlc = hp.find(x => /liquide/i.test(x.nom));
  ok('le DLC, lui, affiche bien ses bornes', !!dlc && /WUE de site/.test(dlc.texte));
  ok('…et dit que la chaleur reste à évacuer', !!dlc && /DÉPLACE/i.test(dlc.texte));

  /* LES MESURES DE CONTRASTE SE FONT SUR LA PAGE OÙ VIT LA CIBLE. Depuis que
     l'empreinte et le comparateur sont deux modules, une seule passe de mesure
     rendrait « introuvable » pour la moitié des cibles — un faux échec, qui est
     la pire sorte : il fait chercher un défaut absent, puis débrancher le
     contrôle. On mesure donc l'eau ICI, avant de changer de page. */
  const mesEau = await pg.evaluate((f) => {
    const m = eval('(' + f + ')');
    return [
      ['pastille de tension', '#eau-source .eau-tn'],
      ['avertissement du circuit ouvert', '#eau-source .eau-hm'],
      ['maturité d’une famille', '#eau-source .eau-mat'],
      ['éditeur d’un repère', '#eau-source .eau-rp i'],
      ['fait de cadrage', '#eau-source .eau-ft i'],
      ['éditeur d’un fait', '#eau-source .eau-ft i span'],
    ].map(([nom, sel]) => {
      const el = document.querySelector(sel);
      return { nom: nom, trouve: !!el, ratio: el ? m(el) : null };
    });
  }, MESURE);

  titre('4. Le comparateur : le paradoxe et le droit du sol');

  /* Le comparateur, lui, est resté dans le panorama : on change de page. */
  await pg.goto(BASE + '/panorama', { waitUntil: 'domcontentloaded' });
  const par = await pg.waitForSelector('.imp-paradoxe', { timeout: 45000 })
    .then(() => true).catch(() => false);
  ok('le paradoxe de l’évaporation est posé SOUS les curseurs', par);
  if (par) {
    const t = await pg.evaluate(() =>
      (document.querySelector('.imp-paradoxe').innerText || '').replace(/\s+/g, ' '));
    ok('…il dit que l’évaporatif rend mieux en air sec', /air sec/.test(t));
    ok('…il prévient que la bonne note d’eau contredit l’optimum thermique',
       /à l’encontre/.test(t));
  }

  /* Le cadre juridique vit dans la fiche du pays : on déplie la France. */
  const cad = await pg.evaluate(() => {
    const f = document.querySelector('.imp-fiche[data-pays="FR"]');
    if (!f) return null;
    f.open = true;
    const c = f.querySelector('.imp-cadre');
    return c ? (c.innerText || '').replace(/\s+/g, ' ') : '';
  });
  ok('la fiche France porte son cadre juridique', !!cad, (cad || '').slice(0, 50));
  if (cad) {
    ok('…il dit ce que le texte ASSOUPLIT', /assouplit/i.test(cad));
    ok('…il dit AUSSI ce qu’il durcit', /durcit/i.test(cad));
    ok('…et le motif de refus hydrique est nommé', /ressource en eau/.test(cad));
  }

  titre('5. Tout cela se lit');

  const mesImp = await pg.evaluate((f) => {
    const m = eval('(' + f + ')');
    const cibles = [
      ['paradoxe', '.imp-paradoxe p'],
      ['sortie du paradoxe', '.imp-paradoxe .imp-sortie'],
      ['étiquette du cadre juridique', '.imp-cadre-2 em'],
    ];
    return cibles.map(([nom, sel]) => {
      const el = document.querySelector(sel);
      return { nom: nom, trouve: !!el, ratio: el ? m(el) : null };
    });
  }, MESURE);
  const mes = mesEau.concat(mesImp);
  mes.forEach(x => {
    /* 4,5:1 est le seuil AA du texte courant ; 3:1 celui du texte large et des
       éléments d'interface. On applique le plus strict — ces textes sont petits. */
    ok(x.nom + ' se lit', x.trouve && x.ratio >= 4.5,
       x.trouve ? x.ratio + ':1' : 'introuvable');
  });

  /* La bordure des cartes d'indicateurs : `var(--rule2)` n'existe pas dans les
     jetons de cette page, et une propriété personnalisée non définie SANS repli
     rend la déclaration invalide — la bordure disparaît sans erreur. */
  await pg.goto(BASE + '/empreinte-parc', { waitUntil: 'domcontentloaded' });
  await pg.waitForSelector('#eau-source .eau-k', { timeout: 60000 })
    .then(() => true).catch(() => false);
  const bord = await pg.evaluate(() => {
    const el = document.querySelector('#eau-source .eau-k');
    if (!el) return null;
    const cs = getComputedStyle(el);
    return { largeur: cs.borderTopWidth, style: cs.borderTopStyle };
  });
  ok('les cartes d’indicateurs ont retrouvé leur bordure',
     !!bord && parseFloat(bord.largeur) > 0 && bord.style !== 'none',
     bord ? bord.largeur + ' ' + bord.style : 'introuvable');

  ok('aucune erreur de script', err.length === 0, err.slice(0, 2).join(' | '));

  await nav.close();
  console.log('\n' + (ko ? ko + ' contrôle(s) en échec' : 'tout est vert') + '\n');
  process.exit(ko ? 1 : 0);
})();
