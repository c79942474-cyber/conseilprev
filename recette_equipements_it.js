/* Équipements informatiques, sur /enveloppe ET /empreinte-parc — vue par un
 * lecteur.
 *
 * CE QU'ON PROTÈGE, ET LA FAUTE QUE CHAQUE CONTRÔLE EMPÊCHE :
 *
 *   1. LE BLOC EST DANS LES DEUX VUES. Le même calcul répond à la question du
 *      budget et à celle du carbone. Le mettre dans une seule obligerait à
 *      changer de vue pour lire deux colonnes du même tableau, et l'une des
 *      deux finirait par être oubliée — c'est le trou que ce bloc comble.
 *   2. LA PART DANS LES LOTS VAUT ZÉRO, ET LA PAGE DIT POURQUOI. C'est le
 *      constat de périmètre : le lot d'aménagement des salles porte la
 *      mention « hors serveurs ». Afficher un pourcentage laisserait croire
 *      que l'informatique est budgétée dans les travaux.
 *   3. CHAQUE QUANTITÉ PORTE SA RÈGLE. Sans elle, « 168 commutateurs » se
 *      recopie dans un budget sans que personne ne sache d'où ça sort.
 *   4. LE VERDICT DE L'ALLONGEMENT CHANGE DE PAYS EN PAYS, et le seuil qui
 *      commande ce changement est affiché. Une page qui dirait « favorable »
 *      partout serait une plaquette.
 *   5. LES QUANTITÉS SONT LES MÊMES QUE CHEZ CONSEILPREVCYBER. Le module est
 *      partagé octet pour octet : si les deux sites divergeaient, l'écart se
 *      découvrirait en comité.
 *
 *     BASE=http://127.0.0.1:5510 node recette_equipements_it.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5510';
const TOKEN = process.env.RECETTE_TOKEN || 'recette_locale_idf_0123456789abcdef';
let ko = 0;
const ok = (n, c, d) => { console.log('  ' + (c ? 'OK ' : 'KO ') + '  ' + n + (d ? ' — ' + d : '')); if (!c) ko++; };
const titre = (t) => console.log('\n══ ' + t + ' ══\n');

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1400, height: 950 } });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e)));
  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg.waitForTimeout(500);

  /* Le pare-feu applicatif rejette les clients HTTP synthétiques : les appels
     d'API partent DE LA PAGE, avec son cookie de session. */
  const api = (url, corps) => pg.evaluate(async ([u, c]) => {
    const r = await fetch(u, {
      method: c ? 'POST' : 'GET', credentials: 'same-origin',
      headers: c ? { 'Content-Type': 'application/json' } : {},
      body: c ? JSON.stringify(c) : undefined
    });
    return { statut: r.status, j: await r.json().catch(() => null) };
  }, [url, corps || null]);

  /* ATTENDRE LE RÉSULTAT, PAS UNE DURÉE. Un délai fixe parie sur la vitesse du
     serveur : sur une base momentanément contrariée, une réponse met plusieurs
     secondes, la recette lit une page pas encore rendue et dénonce un défaut
     du site là où il n'y a qu'une attente. On attend que le bloc CHANGE, et
     l'expiration est NOMMÉE — un délai dépassé de Playwright se lirait comme
     une panne d'outil. */
  const htmlDe = (sel) => pg.evaluate(
    (s) => { const e = document.querySelector(s); return e ? e.innerHTML : ''; }, sel);
  const rendu = async (sel, avant, quoi) => {
    const vu = await pg.waitForFunction(([s, a]) => {
      const e = document.querySelector(s);
      return !!e && e.innerHTML.length > 0 && e.innerHTML !== a;
    }, [sel, avant], { timeout: 30000 }).then(() => true).catch(() => false);
    if (!vu) ok('le serveur rend ' + quoi + ' en moins de 30 s', false,
                'rien de nouveau dans ' + sel);
    return vu;
  };

  // ── 1 ────────────────────────────────────────────────────────────────────
  titre('1. Le bloc est présent dans LES DEUX vues — investissement et empreinte');

  /* L'ORDRE N'EST PAS INDIFFÉRENT : /enveloppe vient EN DERNIER pour que la
     suite s'y déroule sans recharger la page. Chaque chargement de panorama
     tire une vingtaine d'API, et le limiteur de débit global bloque l'adresse
     pour 30 s au-delà — une recette qui recharge trois fois se fait couper au
     milieu et dénonce alors une panne qui n'existe pas. */
  for (const vue of ['/empreinte-parc', '/enveloppe']) {
    const rep = await pg.goto(BASE + vue, { waitUntil: 'domcontentloaded' });
    ok('la page répond — ' + vue, rep && rep.status() === 200,
       rep ? 'HTTP ' + rep.status() : 'pas de réponse');
    if (!rep || rep.status() !== 200) { await nav.close(); process.exit(2); }
    let arme = true;
    try {
      await pg.waitForFunction(() =>
        !!document.getElementById('eq-pit'), null, { timeout: 25000 });
    } catch (e) { arme = false; }
    const v = await pg.evaluate(() => {
      const s = document.getElementById('s-equipements');
      const vis = (e) => !!e && !e.hidden && e.getBoundingClientRect().height > 0;
      return {
        visible: vis(s),
        titre: (document.getElementById('t-eq') || {}).textContent || '',
        champs: ['eq-pit', 'eq-densite', 'eq-perimetre', 'eq-enveloppe', 'eq-go']
          .filter(i => document.getElementById(i)).length,
        densites: (document.getElementById('eq-densite') || { options: [] }).options.length,
        perimetres: (document.getElementById('eq-perimetre') || { options: [] }).options.length
      };
    });
    ok('…le référentiel s’arme — ' + vue, arme);
    ok('…la section est VISIBLE — ' + vue, v.visible);
    ok('…son titre dit que l’enveloppe ne le contient pas — ' + vue,
       /ne contient pas/i.test(v.titre), v.titre);
    ok('…les cinq commandes sont là — ' + vue, v.champs === 5, v.champs + '/5');
    ok('…densités et périmètres viennent du serveur — ' + vue,
       v.densites >= 4 && v.perimetres === 3, v.densites + ' / ' + v.perimetres);
  }

  // ── 2 ────────────────────────────────────────────────────────────────────
  titre('2. La nomenclature s’affiche, chaque quantité avec sa règle');

  /* On est DÉJÀ sur /enveloppe : la boucle ci-dessus s'y est terminée. La
     recharger coûterait une vingtaine d'appels d'API pour rien. */
  await pg.fill('#eq-pit', '1000');
  await pg.fill('#eq-enveloppe', '25000000');
  await pg.selectOption('#eq-perimetre', 'propre');
  await pg.click('#eq-go');
  await pg.waitForFunction(() => {
    const o = document.getElementById('eq-out');
    return o && o.querySelector('.eq-tab');
  }, null, { timeout: 25000 }).catch(() => {});

  const tab = await pg.evaluate(() => {
    const t = document.querySelector('#eq-out .eq-tab');
    if (!t) return null;
    const lignes = [...t.querySelectorAll('tbody tr')].map(tr => ({
      poste: (tr.querySelector('th') || {}).textContent || '',
      regle: (tr.children[1] || {}).textContent || '',
      qte: (tr.children[2] || {}).textContent || ''
    }));
    return {
      n: lignes.length,
      sansRegle: lignes.filter(l => !l.regle.trim()).map(l => l.poste),
      sansQte: lignes.filter(l => !/\d/.test(l.qte)).map(l => l.poste),
      badges: t.querySelectorAll('.eq-badge').length,
      legende: (t.querySelector('caption') || {}).textContent || '',
      gestes: document.querySelectorAll('#eq-out .eq-dl dt').length
    };
  });
  ok('le tableau des postes s’affiche', !!tab && tab.n >= 8, tab ? String(tab.n) : 'absent');
  ok('…CHAQUE poste porte sa règle de quantité',
     !!tab && tab.sansRegle.length === 0, tab && tab.sansRegle.join(', '));
  ok('…chaque poste porte une quantité chiffrée',
     !!tab && tab.sansQte.length === 0, tab && tab.sansQte.join(', '));
  ok('…indispensable ou utile est marqué sur chaque ligne',
     !!tab && tab.badges === tab.n, tab && tab.badges + '/' + tab.n);
  ok('…la légende rappelle puissance ET densité retenues',
     !!tab && /kW\/baie/.test(tab.legende) && /baies/.test(tab.legende), tab && tab.legende);
  ok('…le geste d’achat durable est donné poste par poste',
     !!tab && tab.gestes === tab.n, tab && tab.gestes + '/' + tab.n);

  // ── 3 : LE CONSTAT DE PÉRIMÈTRE ──────────────────────────────────────────
  titre('3. L’informatique n’est PAS dans les lots travaux — et la page le dit');

  const part = await pg.evaluate(() => {
    const b = [...document.querySelectorAll('#eq-out .eq-bloc')]
      .find(x => /investissement/i.test((x.querySelector('h4') || {}).textContent || ''));
    if (!b) return null;
    return {
      cartes: [...b.querySelectorAll('.eq-c')].map(x => ({
        v: (x.querySelector('.v') || {}).textContent || '',
        l: (x.querySelector('.l') || {}).textContent || ''
      })),
      texte: b.textContent || ''
    };
  });
  const lots = part && part.cartes.find(x => /lots travaux/i.test(x.l));
  ok('la carte « part dans les lots travaux » existe', !!lots,
     part && part.cartes.map(x => x.l).join(' | '));
  ok('…et elle vaut ZÉRO', !!lots && /^0\s*%$/.test(lots.v.trim()), lots && lots.v);
  ok('…la page explique pourquoi (aménagement des salles ≠ serveurs)',
     !!part && /aménagement des salles/i.test(part.texte));
  ok('…et donne la part de l’investissement TOTAL en centre propre',
     !!part && part.cartes.some(x => /investissement total/i.test(x.l)));

  titre('4. En colocation, deux bilans distincts ne sont pas additionnés');
  await pg.selectOption('#eq-perimetre', 'colocation');
  let avantOut = await htmlDe('#eq-out');
  await pg.click('#eq-go');
  await rendu('#eq-out', avantOut, 'la part en colocation');
  const coloc = await pg.evaluate(() => {
    const b = [...document.querySelectorAll('#eq-out .eq-bloc')]
      .find(x => /investissement/i.test((x.querySelector('h4') || {}).textContent || ''));
    return b ? {
      texte: b.textContent || '',
      total: [...b.querySelectorAll('.eq-c .l')].some(x => /investissement total/i.test(x.textContent))
    } : null;
  });
  ok('aucune part d’investissement total n’est affichée', !!coloc && coloc.total === false);
  ok('…et la page dit pourquoi : deux bilans distincts',
     !!coloc && /deux bilans/i.test(coloc.texte));
  await pg.selectOption('#eq-perimetre', 'propre');
  avantOut = await htmlDe('#eq-out');
  await pg.click('#eq-go');
  await rendu('#eq-out', avantOut, 'le retour en centre propre');

  // ── 5 : LA BASCULE ───────────────────────────────────────────────────────
  titre('5. L’allongement de durée de vie affiche son point de bascule');

  const visible = await pg.evaluate(() => {
    const b = document.getElementById('eq-vie-bloc');
    return !!b && !b.hidden && !!document.getElementById('eq-pays');
  });
  ok('le formulaire de durée de vie apparaît après le dimensionnement', visible);

  async function bascule(pays) {
    await pg.selectOption('#eq-pays', pays);
    await pg.fill('#eq-d0', '5');
    await pg.fill('#eq-d1', '8');
    await pg.fill('#eq-pue', '1.3');
    const avantVie = await htmlDe('#eq-vie-out');
    await pg.click('#eq-vie-go');
    await rendu('#eq-vie-out', avantVie, 'la bascule pour ' + pays);
    return pg.evaluate(() => {
      const b = document.querySelector('#eq-vie-out .eq-bloc');
      if (!b) return null;
      const s = [...b.querySelectorAll('.eq-c')]
        .find(x => /bascule/i.test((x.querySelector('.l') || {}).textContent || ''));
      return {
        classe: b.className,
        verdict: (b.querySelector('.eq-verdict') || {}).textContent || '',
        seuil: s ? (s.querySelector('.v') || {}).textContent : '',
        texte: b.textContent || '',
        formules: b.querySelectorAll('.eq-formules li').length
      };
    });
  }

  const fr = await bascule('FR');
  ok('sur le mix français, l’allongement est FAVORABLE',
     !!fr && /eq-fav/.test(fr.classe) && /Favorable/i.test(fr.verdict), fr && fr.verdict);
  ok('…le verdict porte une icône directionnelle, pas seulement une couleur',
     !!fr && /[▲▼]/.test(fr.verdict), fr && fr.verdict);
  ok('…l’intensité de bascule est affichée en g/kWh',
     !!fr && /g\/kWh/.test(fr.seuil), fr && fr.seuil);
  ok('…les formules sont publiées pour être refaites',
     !!fr && fr.formules >= 4, fr && String(fr.formules));
  ok('…la réserve non-carbone est dite (sécurité, correctifs)',
     !!fr && /correctifs/i.test(fr.texte));

  const pl = await bascule('PL');
  ok('sur un mix carboné, le MÊME allongement devient DÉFAVORABLE',
     !!pl && /eq-def/.test(pl.classe) && /Défavorable/i.test(pl.verdict), pl && pl.verdict);
  ok('…et la page nomme le levier qui reste : décarboner l’alimentation',
     !!pl && /décarboner/i.test(pl.texte));
  ok('…le seuil est le MÊME dans les deux pays : il ne dépend que du matériel',
     !!fr && !!pl && fr.seuil.trim() === pl.seuil.trim(),
     fr && pl ? fr.seuil + ' ≠ ' + pl.seuil : '');

  // ── 6 : LE SCOPE 3 ───────────────────────────────────────────────────────
  titre('6. Le scope 3 dit ce qu’il couvre, et ce qu’il ne couvre pas');
  const s3 = await pg.evaluate(() => {
    const b = [...document.querySelectorAll('#eq-s3-out .eq-bloc')]
      .find(x => /scope/i.test((x.querySelector('h4') || {}).textContent || ''));
    return b ? { texte: b.textContent || '', cartes: b.querySelectorAll('.eq-c').length,
                 trous: b.querySelectorAll('.eq-trous li').length } : null;
  });
  ok('le bilan scope 3 s’affiche', !!s3 && s3.cartes >= 4, s3 && String(s3.cartes));
  ok('…il se présente en complément des scopes 1 et 2',
     !!s3 && /scope/i.test(s3.texte) && /complèt/i.test(s3.texte));
  ok('…il NOMME au moins trois postes non couverts', !!s3 && s3.trous >= 3,
     s3 && String(s3.trous));
  ok('…il avertit du transfert entre scopes quand on prolonge',
     !!s3 && /scope 2/i.test(s3.texte));

  // ── 7 : LES REFUS ────────────────────────────────────────────────────────
  titre('7. Le module refuse plutôt que d’inventer');
  const r1 = await api('/api/equipements-it', { puissance_it_kw: 1000, densite: 'supersonique' });
  ok('une densité inconnue est refusée avec son motif',
     r1.statut === 200 && r1.j && r1.j.nomenclature && r1.j.nomenclature.ok === false
       && /supersonique/.test(r1.j.nomenclature.motif || ''),
     JSON.stringify(r1.j && r1.j.nomenclature).slice(0, 110));

  const r2 = await api('/api/equipements-it',
                       { puissance_it_kw: 1000, duree_base: 5, duree_cible: 20 });
  ok('un allongement au-delà de quinze ans est refusé',
     r2.statut === 200 && r2.j && r2.j.prolongation && r2.j.prolongation.ok === false
       && /quinze ans/.test(r2.j.prolongation.motif || ''),
     JSON.stringify(r2.j && r2.j.prolongation).slice(0, 110));

  const r3 = await api('/api/equipements-it',
                       { puissance_it_kw: 1000, duree_base: 5, duree_cible: 8, pue: 0.8 });
  ok('un PUE inférieur à 1 est refusé comme physiquement impossible',
     r3.statut === 200 && r3.j && r3.j.prolongation && r3.j.prolongation.ok === false
       && /impossible/.test(r3.j.prolongation.motif || ''),
     JSON.stringify(r3.j && r3.j.prolongation).slice(0, 110));

  const r4 = await api('/api/equipements-it',
                       { puissance_it_kw: 1000, duree_base: 5, duree_cible: 8, pays: 'ZZ' });
  ok('un pays dont le mix est inconnu est refusé, jamais supposé',
     r4.statut === 200 && r4.j && r4.j.prolongation && r4.j.prolongation.ok === false);

  // ── 8 : LE MODULE PARTAGÉ ────────────────────────────────────────────────
  titre('8. Les quantités sont celles du module partagé, pas une seconde table');
  const ref = await api('/api/equipements-it');
  ok('le référentiel est servi', ref.statut === 200 && ref.j && ref.j.ok);
  ok('…il nomme le moteur dont il lit l’intensité carbone',
     !!ref.j && !!ref.j.moteur_lu, ref.j && String(ref.j.moteur_lu));
  ok('…il publie sa dérive d’efficacité, qui commande la bascule',
     !!ref.j && ref.j.derive_efficacite_an > 0, ref.j && String(ref.j.derive_efficacite_an));
  ok('…et il dit d’emblée que les lots ne portent pas d’informatique',
     !!ref.j && /hors|aménagement des salles/i.test(ref.j.lots_sans_it || ''));

  const calc = await api('/api/equipements-it', { puissance_it_kw: 1000, densite: 'dense' });
  ok('mille kilowatts denses donnent 84 baies — le même compte que sur l’autre site',
     !!calc.j && calc.j.nomenclature.baies === 84,
     calc.j && String(calc.j.nomenclature.baies));

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0, err.join(' | '));

  console.log('\n' + (ko === 0 ? 'tout est vert' : ko + ' contrôle(s) en échec'));
  await nav.close();
  process.exit(ko === 0 ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
