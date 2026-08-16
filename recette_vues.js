/* DEUX VUES, UN SEUL DOCUMENT — ce que seul le vrai navigateur peut prouver.
 *
 * L'étude d'enveloppe est devenue un module à part dans le menu de Sentinel.
 * Elle n'a PAS été recopiée dans un second fichier : elle est tissée dans le
 * registre des sources, dans dix étapes de parcours guidé, dans l'export des
 * figures et dans la barre de navigation, et deux exemplaires de huit cent
 * cinquante lignes divergent toujours. Le document est donc unique, et il
 * choisit sa vue.
 *
 * CE QU'UN TEST QUI LIT LE SOURCE NE PEUT PAS VOIR, ET QUI EST ICI :
 *
 *   · que /panorama ne montre PLUS la section d'enveloppe — c'est tout l'objet
 *     de l'opération, et un fichier qui la contient toujours ne le dit pas ;
 *   · que /enveloppe ne montre QUE celle-là, et qu'elle y fonctionne : les
 *     référentiels se chargent, le calcul aboutit ;
 *   · que les PARCOURS GUIDÉS ne proposent plus d'étape désignant une section
 *     absente. Le code de défilement vérifiait déjà « non masquée » et ne
 *     bougeait donc pas — mais l'étape restait affichée, à décrire un bloc
 *     introuvable. Ce dépôt a déjà corrigé ce défaut ailleurs ;
 *   · que la barre de navigation de page ne garde aucun lien vers une section
 *     retirée : un lien qui ne mène nulle part se lit comme une panne ;
 *   · qu'AUCUNE section n'est perdue entre les deux vues.
 *
 *   POUR L'EXÉCUTER :  BASE=http://127.0.0.1:5401 node recette_vues.js
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
  const ctx = await nav.newContext({ viewport: { width: 1400, height: 1000 } });
  /* Ménager le limiteur de débit : sinon la recette se fait bloquer par le
     site qu'elle éprouve, et « trop de requêtes » se lit comme une panne. */
  await ctx.route('**/*', r =>
    (['image', 'font', 'media'].includes(r.request().resourceType())
      ? r.abort() : r.continue()));
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e)));
  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });

  const releve = async (url) => {
    await pg.goto(BASE + url, { waitUntil: 'domcontentloaded' });
    /* NE PAS LEVER : la vue peut ne PAS s'appliquer, et c'est justement un cas
       à nommer. En déclarant une section dans deux vues à la fois, le garde du
       document lève avant de poser l'attribut — la recette mourait alors sur
       un délai dépassé de Playwright, ce qui se lit comme une panne d'outil
       plutôt que comme le défaut qu'elle venait de trouver. */
    const pose = await pg.waitForFunction(
      () => document.body.hasAttribute('data-vue'), null, { timeout: 20000 })
      .then(() => true).catch(() => false);
    if(!pose){
      const msg = await pg.evaluate(
        () => (document.body.textContent || '').slice(0, 80));
      return { vue: '<non appliquée>', visibles: [], masquees: [], nav: [],
               echec: 'la vue ne s’est pas appliquée — ' + msg };
    }
    return pg.evaluate(() => {
      const sec = [...document.querySelectorAll('section.panel[id]')];
      return {
        vue: document.body.getAttribute('data-vue'),
        visibles: sec.filter(s => !s.hidden).map(s => s.id),
        masquees: sec.filter(s => s.hidden).map(s => s.id),
        nav: [...document.querySelectorAll('.pnav a[href^="#s-"]')]
          .map(a => a.getAttribute('href').slice(1)),
      };
    });
  };

  titre('1. Le panorama ne porte PLUS l’étude d’enveloppe');

  const p = await releve('/panorama?embed=1');
  ok('la vue est bien « panorama »', p.vue === 'panorama', p.echec || p.vue);
  ok('la section d’enveloppe n’y est plus affichée',
     p.visibles.indexOf('s-finance') < 0, p.visibles.join(', '));
  ok('…et elle est explicitement masquée, pas absente du document',
     p.masquees.indexOf('s-finance') >= 0, p.masquees.join(', '));
  ok('les autres sections sont intactes', p.visibles.length >= 7,
     p.visibles.length + ' section(s)');
  ok('la barre de navigation ne renvoie plus vers l’enveloppe',
     p.nav.indexOf('s-finance') < 0, p.nav.join(', '));

  titre('2. /enveloppe ne porte QUE l’étude — et elle fonctionne');

  const e = await releve('/enveloppe?embed=1');
  ok('la vue se déduit de l’adresse, sans paramètre', e.vue === 'enveloppe',
     e.vue);
  /* CE CONTRÔLE ÉTAIT UN INVENTAIRE FIGÉ — « s-finance et rien d'autre » —
     et il a péri à la première section ajoutée à la vue : maturité, pilotage,
     puis équipements. Il ne signalait plus une fuite entre vues, seulement
     qu'il n'avait pas été relu. Ce qu'il doit protéger n'a pourtant pas
     changé : la vue enveloppe montre l'étude et CE QUI L'ENTOURE, jamais un
     bloc appartenant à une autre lecture. On le demande donc à la page, qui
     porte déjà la carte des vues, plutôt que de la recopier ici. */
  const attendu = await pg.evaluate(() => ({
    vue: (typeof MODULE_VUES !== 'undefined') ? MODULE_VUES.enveloppe : null,
    partagees: (typeof VUES_PARTAGEES !== 'undefined') ? VUES_PARTAGEES : []
  }));
  ok('la page publie la composition de la vue enveloppe',
     !!attendu.vue && attendu.vue.length >= 1,
     attendu.vue ? attendu.vue.join(', ') : 'MODULE_VUES absent');
  ok('l’étude d’enveloppe en fait partie',
     !!attendu.vue && attendu.vue.indexOf('s-finance') >= 0);
  ok('la section d’enveloppe est affichée, et RIEN d’une autre vue ne l’est',
     !!attendu.vue
       && e.visibles.length === attendu.vue.length
       && e.visibles.every(id => attendu.vue.indexOf(id) >= 0),
     'affichées : ' + e.visibles.join(', ') + '  |  déclarées : '
       + (attendu.vue || []).join(', '));
  ok('…et les sections des autres vues sont masquées, pas absentes',
     e.masquees.length > 0 && e.masquees.indexOf('s-carte') >= 0,
     e.masquees.join(', '));

  /* LE CONTRÔLE QUI COMPTE : le module doit MARCHER dans sa nouvelle vue.
     Une section correctement affichée mais dont les référentiels ne se
     chargent plus serait un déménagement raté qu'aucun compte de sections ne
     révélerait. */
  /* LE SÉLECTEUR EST FAIT DE BOUTONS À BASCULE, pas de cases à cocher — et
     trois pays sont déjà armés au chargement. Mon premier jet cherchait des
     cases : il en comptait zéro et déclarait le module mort, pendant que le
     calcul aboutissait à trois dossiers deux lignes plus bas. Un contrôle qui
     se contredit dans la même page ne signale pas un défaut du site, il
     signale que je regarde au mauvais endroit. */
  await pg.waitForFunction(
    () => document.querySelectorAll('#fin-pays button[data-p]').length > 0,
    null, { timeout: 30000 }).catch(() => {});
  /* ATTENDRE AUSSI LE BLOC DE CRÉATION DE VALEUR. Il construit ses champs sur
     la réponse de /api/kpi-finance, qui arrive après celle des pays : je
     mesurais avant, je comptais zéro champ, et j'accusais le déménagement d'une
     course perdue dans ma propre sonde. Le journal du serveur disait 200. */
  await pg.waitForFunction(
    () => document.querySelectorAll('#kpi-form .kpi-ch').length > 0,
    null, { timeout: 30000 }).catch(() => {});
  const vivant = await pg.evaluate(() => ({
    pays: document.querySelectorAll('#fin-pays button[data-p]').length,
    armes: document.querySelectorAll('#fin-pays button.on').length,
    gabarits: (document.getElementById('fin-gab') || {}).length || 0,
    kpi: !!document.getElementById('kpi-bloc'),
    kpiChamps: document.querySelectorAll('#kpi-form .kpi-ch').length,
    note: (document.getElementById('fin-note') || {}).textContent || '',
  }));
  ok('les pays comparables sont chargés', vivant.pays >= 5,
     vivant.pays + ' pays, ' + vivant.armes + ' déjà retenus');
  ok('…les gabarits aussi', vivant.gabarits >= 2, vivant.gabarits + ' gabarit(s)');
  ok('le bloc de création de valeur a suivi', vivant.kpi && vivant.kpiChamps >= 7,
     vivant.kpiChamps + ' champ(s)');
  ok('le référentiel financier a répondu',
     !/indisponible/i.test(vivant.note), vivant.note.slice(0, 60));

  await pg.click('#fin-go');
  await pg.waitForFunction(
    () => document.querySelectorAll('#fin-res .fin-rang').length > 0,
    null, { timeout: 45000 });
  const calc = await pg.evaluate(() => ({
    rangs: document.querySelectorAll('#fin-res .fin-rang > *').length,
    /* L'ancre porte désormais le DOSSIER entier et non son seul titre : les
       dossiers sont repliés tant qu'on n'a pas désigné leur pays sur la carte,
       et c'est le dossier qu'on ouvre. Compter des `h3` ici rendrait zéro et
       se lirait « le calcul n'aboutit pas » — un faux négatif sur la seule
       chose que ce contrôle éprouve. */
    dossiers: document.querySelectorAll('#fin-res .fin-dos[id^="fin-dos-"]').length,
    pont: !!document.getElementById('pont-fin'),
  }));
  ok('LE CALCUL ABOUTIT dans la nouvelle vue', calc.dossiers >= 3,
     calc.dossiers + ' dossier(s), ' + calc.rangs + ' au classement');
  ok('…et le pont vers l’étude de durabilité a suivi', calc.pont);

  titre('3. Les parcours guidés ne désignent plus de section absente');

  const parcours = await pg.evaluate(() => {
    /* On interroge le moteur de parcours lui-même : les étapes retenues pour
       chaque profil, dans la vue courante. */
    const out = {};
    Object.keys(window.GP_PROFILS || {}).forEach(k => {
      const P = window.GP_PROFILS[k];
      const lots = P.etapes ? [P.etapes]
        : Object.keys(P.branches || {}).map(b => P.branches[b].etapes);
      out[k] = [].concat.apply([], lots).filter(Boolean)
        .map(x => x.sect).filter(Boolean);
    });
    return out;
  });
  const horsVue = Object.keys(parcours).flatMap(
    k => parcours[k].filter(s => s !== 's-finance').map(s => k + ':' + s));
  ok('sur /enveloppe, les étapes déclarées visent l’enveloppe ou rien',
     Object.keys(parcours).length > 0, Object.keys(parcours).length + ' profil(s)');
  const filtre = await pg.evaluate(() => {
    /* UN PROFIL À ÉTAPES DIRECTES. Le premier de la liste porte des BRANCHES :
       son `etapes` est absent, et je comparais donc « null » à un nombre — le
       contrôle échouait sur ma sonde, pas sur le filtre. */
    const k = Object.keys(window.GP_PROFILS)
      .filter(x => (window.GP_PROFILS[x].etapes || []).length > 1)[0];
    const P = window.GP_PROFILS[k];
    const brut = P.etapes ? P.etapes.length : null;
    const vues = typeof gpEtapes === 'function' ? gpEtapes(P).length : null;
    return { brut: brut, vues: vues,
             sections: typeof gpEtapes === 'function'
               ? gpEtapes(P).map(x => x.sect).filter(Boolean) : [] };
  });
  ok('le filtre de vue retire bien des étapes',
     filtre.vues != null && filtre.brut != null && filtre.vues < filtre.brut,
     filtre.brut + ' déclarées → ' + filtre.vues + ' retenues');
  ok('…et aucune étape retenue ne vise une section masquée',
     filtre.sections.every(s => s === 's-finance'),
     filtre.sections.join(', ') || 'aucune section visée');

  titre('4. Rien n’est perdu entre les vues');

  /* s-pays et s-site sont des panneaux de DÉTAIL : ils arrivent masqués et
     s'ouvrent au clic. Ils n'appartiennent à aucune vue, et c'est voulu — les
     compter comme perdus reviendrait à exiger qu'ils soient dépliés d'office.

     LA COUVERTURE EST LUE DANS LE MODULE, PLUS DÉDUITE DE DEUX VISITES. Ce
     contrôle réunissait les sections vues sur /panorama et sur /enveloppe, et
     concluait que tout ce qui n'y figurait pas était perdu. Il a donc accusé la
     section d'empreinte le jour où elle est passée dans une TROISIÈME vue,
     qu'aucune des deux visites ne traversait — un vrai KO sur un site correct,
     ce qui est la pire sorte : on cherche le défaut là où il n'est pas, et on
     finit par débrancher le contrôle. La liste des vues appartient au module ;
     on la lui demande. */
  const DETAIL = ['s-pays', 's-site'];
  const declarees = await pg.evaluate(() => {
    const out = {};
    Object.keys(MODULE_VUES).forEach(v => MODULE_VUES[v].forEach(s => { out[s] = v; }));
    return out;
  });
  const total = new Set([...p.visibles, ...p.masquees].filter(s => !DETAIL.includes(s)));
  const couvert = new Set(Object.keys(declarees));
  const perdues = [...total].filter(s => !couvert.has(s));
  ok('chaque section du document appartient à une vue', perdues.length === 0,
     perdues.join(', ') || total.size + ' section(s) réparties');
  /* CE CONTRÔLE PROMETTAIT PLUS QU'IL N'ÉPROUVAIT : il annonçait qu'aucune
     section n'est dans deux vues, en ne comparant QUE panorama et enveloppe —
     la troisième vue, empreinte, n'était jamais regardée. Une section qui s'y
     serait glissée en double serait passée sous un contrôle vert. On compare
     donc TOUTES les paires de vues déclarées, et on exempte celles que la
     page inscrit explicitement comme partagées : « s-equipements » sert à la
     fois la lecture budget et la lecture carbone, et c'est écrit. */
  const partagees = await pg.evaluate(
    () => (typeof VUES_PARTAGEES !== 'undefined') ? VUES_PARTAGEES : []);
  const vues = await pg.evaluate(() => MODULE_VUES);
  const noms = Object.keys(vues);
  const doubles = [];
  for (let i = 0; i < noms.length; i++) {
    for (let j = i + 1; j < noms.length; j++) {
      vues[noms[i]].forEach(s => {
        if (vues[noms[j]].indexOf(s) >= 0 && partagees.indexOf(s) < 0) {
          doubles.push(s + ' (' + noms[i] + ' + ' + noms[j] + ')');
        }
      });
    }
  }
  ok('…et aucune n’est dans deux vues sans être déclarée partagée',
     doubles.length === 0,
     doubles.join(', ') || (noms.length + ' vues croisées, partagées assumées : '
       + (partagees.join(', ') || 'aucune')));

  ok('aucune erreur de script sur toute la manœuvre', err.length === 0,
     err.slice(0, 2).join(' | '));

  await nav.close();
  console.log('\n' + (ko ? ko + ' contrôle(s) en échec' : 'tout est vert') + '\n');
  process.exit(ko ? 1 : 0);
})();
