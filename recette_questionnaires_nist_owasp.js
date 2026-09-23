/* RECETTE — LES DEUX DERNIERS MODULES SE REMPLISSENT ENFIN
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LA DEMANDE : « améliorer OWASP (2 pages) et NIST (3 pages) — parcours
 * guidés pour le questionnaire et conformité ».
 *
 * CE QUE LA MESURE A TROUVÉ AVANT D'ÉCRIRE UNE LIGNE. Les moteurs
 * `nist_ai_rmf.evaluer` et `owasp_llm.evaluer` existent, leurs routes aussi,
 * et RIEN ne les appelait. Les cinq pages de ces deux modules ne portaient
 * pas un seul champ de saisie : ni <select>, ni <input>, aucune persistance.
 * Elles affichaient le référentiel, point. Le parcours guidé NIST disait
 * pourtant déjà « Renseignez d'abord les six catégories de GOVERN » — une
 * consigne adressée à une page en lecture seule.
 *
 * ET UN GLOBAL LU MAIS JAMAIS ÉCRIT. `confDeclarations()` relevait
 * `window.CONF_DECL[norme]` pour six normes ; rien n'écrivait ce global.
 * (Le taux lit aujourd'hui la collecte du rail : c'est elle qu'on relit.)
 * Deux cartes du taux de conformité étaient condamnées au tiret, quoi que
 * fasse le visiteur — et pas faute d'avoir rempli : faute d'avoir eu quoi
 * remplir.
 *
 * POURQUOI RIEN NE TOMBAIT. Une déclaration vide est un état LÉGITIME : le
 * moteur rend « — » plutôt qu'un zéro, à dessein, parce qu'un sujet non
 * ouvert n'est pas un sujet à zéro. L'écran vide et l'écran jamais branché
 * rendent exactement la même chose. Cette recette sépare les deux : elle
 * RÉPOND, puis regarde ce qui sort.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5901';
const TOKEN = 'recette_locale_idf_0123456789abcdef';
(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport:{width:1500,height:1100} });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator,'webdriver',{get:()=>false});
    Object.defineProperty(navigator,'plugins',{get:()=>[1,2,3]});
    Object.defineProperty(navigator,'languages',{get:()=>['fr-FR','fr']});
  });
  const pg = await ctx.newPage();
  const err = []; pg.on('pageerror', e => err.push(String(e).slice(0,200)));
  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil:'commit' });
  await pg.waitForTimeout(4000);
  const compte = await pg.evaluate(() => {
    if (typeof nistInit === 'function') nistInit();
    if (typeof owaspInit === 'function') owaspInit();
    return true;
  });
  await pg.waitForTimeout(2500);
  const v = await pg.evaluate(() => ({
    nistSelects: document.querySelectorAll('#p-nist-profil .q-sel').length,
    owaspSelects: document.querySelectorAll('#p-owasp-dix .q-sel').length,
    nistVerdict: !!document.getElementById('nist-verdict'),
    owaspVerdict: !!document.getElementById('owasp-verdict')
  }));
  console.log('rendu :', JSON.stringify(v));
  /* ON RÉPOND, ET ON REGARDE CE QUI SORT. */
  const rep = await pg.evaluate(async () => {
    const n = document.querySelector('#p-nist-profil .q-sel[data-cle="GOVERN 1"]');
    const o = document.querySelector('#p-owasp-dix .q-sel[data-cle="LLM05"]');
    if (n) { n.value = 'tenu'; n.dispatchEvent(new Event('change')); }
    if (o) { o.value = 'non'; o.dispatchEvent(new Event('change')); }
    await new Promise(r => setTimeout(r, 1800));
    return {
      nistVerdict: (document.getElementById('nist-verdict')||{}).textContent
        ? document.getElementById('nist-verdict').textContent.replace(/\s+/g,' ').trim().slice(0,150) : null,
      owaspVerdict: (document.getElementById('owasp-verdict')||{}).textContent
        ? document.getElementById('owasp-verdict').textContent.replace(/\s+/g,' ').trim().slice(0,170) : null,
      collecte: window.declarationsDesEcrans
        ? JSON.stringify({ nist_ai_rmf: window.declarationsDesEcrans().nist_ai_rmf,
                           owasp_llm: window.declarationsDesEcrans().owasp_llm }) : null,
      stock: [localStorage.getItem('cp-sentinel-nist-profil-v1'),
              localStorage.getItem('cp-sentinel-owasp-declares-v1')]
    };
  });
  console.log(JSON.stringify(rep, null, 2));
  console.log('erreurs JS :', err.length ? err.join(' | ') : 'aucune');
  await nav.close();
})();
