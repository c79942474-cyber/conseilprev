/* RECETTE — SENTINEL BASCULE EN ANGLAIS, ET RIEN NE S'EFFACE
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LA DEMANDE : « comme pour l'accueil, traduire les pages de Sentinel en
 * anglais — FR ou EN — en le proposant en haut du menu ».
 *
 * CE QUE LES RÈGLES PYTHON NE PEUVENT PAS VOIR. Elles lisent les fichiers ;
 * elles ne savent pas ce qui reste à l'écran APRÈS le passage de la
 * traduction. Or c'est exactement là qu'est le danger : sur l'accueil,
 * `applyLang` remplace l'innerHTML de tout porteur de `data-i18n`, et ce
 * dépôt a payé deux fois ce défaut — la mention « texte seul » de la carte
 * DORA, puis les dix-neuf liens des offres de services, morts au chargement
 * sans erreur et sans trace.
 *
 * D'OÙ LE CONTRÔLE QUI COMPTE ICI : les SOIXANTE icônes du menu sont
 * comptées avant et après la bascule. Une seule disparition et la traduction
 * mange le balisage.
 *
 * LES TRENTE-CINQ PAGES DE CONFORMITÉ. Sept d'entre elles sont relevées
 * dans les deux langues : leur titre doit changer, leur mise en forme
 * rester à l'identique, et le volume du chapeau anglais rester comparable —
 * une traduction deux fois plus courte est une traduction tronquée.
 *
 * DEUX CONTRÔLES ONT DÛ ÊTRE RÉ-AIMÉS, et c'est la sonde qui se trompait :
 * « CRA · Article 14 » est identique dans les deux langues — nom propre de
 * règlement suivi d'un numéro d'article — et le chapeau RGPD n'a jamais
 * porté de gras. Exiger le contraire aurait fait tomber la recette sur une
 * identité VOULUE et sur une mise en forme qui n'existe pas.
 *
 * LES AUTRES CONTRÔLES : la bascule marque la langue active, les douze
 * rubriques et les cinquante-huit entrées changent ensemble, le fil d'Ariane
 * suit SANS qu'on ait à recliquer sur la page ouverte, le retour au français
 * restitue le texte d'origine, et le choix survit à la fermeture de l'onglet.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5901';
const TOKEN = 'recette_locale_idf_0123456789abcdef';
let ko = 0, n = 0;
const ok = (t,c,d) => { n++; if(!c) ko++;
  console.log((c?'  OK   ':'  KO   ')+t+(d?' — '+d:'')); };
const RELEVE = () => ({
  langue: document.documentElement.lang,
  actif: (document.querySelector('.sb-lbtn.on')||{}).textContent,
  sections: [...document.querySelectorAll('.sb-section [data-i18n]')].map(e=>e.textContent),
  entrees: [...document.querySelectorAll('.sb-item [data-i18n]')].map(e=>e.textContent),
  sousTitre: (document.querySelector('.sb-sub')||{}).textContent,
  fil: [(document.getElementById('tb-sec')||{}).textContent,
        (document.getElementById('tb-pg')||{}).textContent],
  titre: document.title,
  /* LE PIÈGE DE L'ACCUEIL : un lien dans un élément traduit disparaîtrait. */
  liensMenu: document.querySelectorAll('.sb-item a, .sb-section a').length,
  iconesMenu: document.querySelectorAll('.sb-item .sb-icon svg').length
});
(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport:{width:1500,height:1000} });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator,'webdriver',{get:()=>false});
    Object.defineProperty(navigator,'plugins',{get:()=>[1,2,3]});
    Object.defineProperty(navigator,'languages',{get:()=>['fr-FR','fr']});
  });
  const pg = await ctx.newPage();
  const err = []; pg.on('pageerror', e => err.push(String(e).slice(0,180)));
  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil:'commit' });
  await pg.waitForTimeout(4000);

  const fr = await pg.evaluate(RELEVE);
  ok('la bascule est présente et marque le français',
     fr.actif === 'FR' && fr.langue === 'fr', fr.actif + ' · lang=' + fr.langue);
  ok('les 12 rubriques et les 58 entrées sont balisées',
     fr.sections.length === 12 && fr.entrees.length >= 55,
     fr.sections.length + ' rubriques, ' + fr.entrees.length + ' entrées');
  ok('le menu est en français', fr.sections.includes('Pilotage'),
     fr.sections.slice(0,4).join(' · '));

  /* ── ON BASCULE ───────────────────────────────────────────────────── */
  await pg.evaluate(() => sentSetLang('en'));
  await pg.waitForTimeout(600);
  const en = await pg.evaluate(RELEVE);
  ok('la page se déclare en anglais', en.langue === 'en' && en.actif === 'EN',
     en.actif + ' · lang=' + en.langue);
  ok('les 12 rubriques sont traduites',
     en.sections.includes('Steering') && !en.sections.includes('Pilotage'),
     en.sections.slice(0,5).join(' · '));
  const traduites = en.entrees.filter((v,i) => v !== fr.entrees[i]).length;
  ok('les entrées de menu sont traduites', traduites >= 50,
     traduites + ' / ' + en.entrees.length + ' changées');
  ok('le sous-titre suit', en.sousTitre === 'Risk mapping', en.sousTitre);
  ok('AUCUNE icône du menu n’a été effacée par la traduction',
     en.iconesMenu === fr.iconesMenu && fr.iconesMenu > 40,
     fr.iconesMenu + ' → ' + en.iconesMenu);

  /* ── LE FIL D'ARIANE SUIT, SUR UNE PAGE OUVERTE ───────────────────── */
  await pg.evaluate(() => go('radar'));
  await pg.waitForTimeout(500);
  const r1 = await pg.evaluate(RELEVE);
  ok('le fil d’Ariane est en anglais', /ASSESS RISK/i.test(r1.fil[0] || ''),
     r1.fil.join(' › ') + ' · ' + r1.titre);
  await pg.evaluate(() => sentSetLang('fr'));
  await pg.waitForTimeout(500);
  const r2 = await pg.evaluate(RELEVE);
  ok('et il repasse en français sans recliquer',
     /ÉVALUER LE RISQUE/i.test(r2.fil[0] || ''), r2.fil.join(' › '));
  ok('le menu aussi', r2.sections.includes('Pilotage'),
     r2.sections.slice(0,4).join(' · '));

  /* ── LES TRENTE-CINQ PAGES DE CONFORMITÉ ──────────────────────────── */
  const entetes = async (lg) => {
    await pg.evaluate((l) => sentSetLang(l), lg);
    await pg.waitForTimeout(500);
    return pg.evaluate(() => {
      const ids = ['conf-taux','nis2-chiffre','iso42001-soa','owasp-dix',
                   'nist-profil','cra-signalement','rgpd-aipd'];
      return ids.map(i => {
        const p = document.getElementById('p-' + i);
        if (!p) return { i, absent: true };
        const eb = p.querySelector('.eyebrow'), h = p.querySelector('.page-h');
        const t = p.querySelector('.page-lead, .page-p');
        return { i, eb: eb && eb.textContent.trim(),
                 h: h && h.textContent.replace(/\s+/g,' ').trim().slice(0,52),
                 mots: t ? t.textContent.split(/\s+/).length : 0,
                 gras: t ? t.querySelectorAll('b,strong,em').length : 0,
                 liens: t ? t.querySelectorAll('a').length : 0 };
      });
    });
  };
  const eFr = await entetes('fr');
  const eEn = await entetes('en');
  ok('les sept pages témoins existent', eFr.every(x => !x.absent),
     eFr.filter(x => x.absent).map(x => x.i).join(', '));
  /* LE TITRE DOIT CHANGER ; LE SURTITRE, PAS FORCÉMENT.
     « CRA · Article 14 » et « NIS 2 · Article 34 » sont identiques dans les
     deux langues — un nom propre de règlement suivi d'un numéro d'article.
     Exiger qu'ils diffèrent aurait fait tomber la recette sur une identité
     VOULUE : c'est la sonde qui se serait trompée, pas le produit. */
  const nonTrad = eEn.filter((x, k) => x.h === eFr[k].h);
  ok('les TITRES passent en anglais', nonTrad.length === 0,
     nonTrad.map(x => x.i).join(', ') || eEn.map(x => x.h).slice(0,2).join(' | '));
  const surtitres = eEn.filter((x, k) => x.eb !== eFr[k].eb).length;
  ok('et les surtitres aussi, sauf les pures références',
     surtitres >= eEn.length - 2, surtitres + ' / ' + eEn.length + ' changés');
  /* LA MISE EN FORME SE CONSERVE — celle qui existe. Un chapeau sans gras
     n'en acquiert pas, un chapeau qui en a n'en perd pas. */
  ok('les chapeaux gardent exactement leur mise en forme',
     eEn.every((x, k) => x.gras === eFr[k].gras),
     eEn.map((x,k) => x.i + ' ' + eFr[k].gras + '→' + x.gras).join(' · '));
  ok('et la mise en forme n’a pas disparu partout',
     eEn.filter(x => x.gras > 0).length >= 5,
     eEn.filter(x => x.gras > 0).length + ' chapeaux formatés');
  ok('et n’ont acquis aucun lien au passage',
     eEn.every(x => x.liens === 0), '');
  ok('les chapeaux anglais ont un volume comparable',
     eEn.every((x, k) => x.mots > eFr[k].mots * 0.5 && x.mots < eFr[k].mots * 1.8),
     eEn.map((x,k) => x.i + ' ' + eFr[k].mots + '→' + x.mots).join(' · '));
  const retour = await entetes('fr');
  ok('le retour au français restitue le texte d’origine',
     retour.every((x, k) => x.h === eFr[k].h && x.eb === eFr[k].eb),
     retour.filter((x,k) => x.h !== eFr[k].h).map(x => x.i).join(', '));

  /* ── LE CHOIX SURVIT AU RECHARGEMENT ──────────────────────────────── */
  await pg.evaluate(() => sentSetLang('en'));
  await pg.waitForTimeout(400);
  const garde = await pg.evaluate(() => localStorage.getItem('cp-sentinel-langue-v1'));
  ok('le choix est conservé', garde === 'en', String(garde));
  ok('aucune erreur JavaScript', err.length === 0, err.join(' | '));
  await nav.close();
  console.log('\n' + (n-ko) + ' contrôles passés, ' + ko + ' en échec');
  process.exit(ko ? 1 : 0);
})().catch(e => { console.error('KO rompu : ' + e); process.exit(2); });
