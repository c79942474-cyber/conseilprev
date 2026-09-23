/* RECETTE — DORA, LES SIX ÉCRANS DANS UN VRAI NAVIGATEUR
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * LA DEMANDE : « dans les 11 normes maîtrisées de Sentinel, connecter et
 * ajouter DORA à "votre mise en conformité réglementaire" du menu latéral et
 * proposer une analyse de risque […] claire, fiable, détaillée ».
 *
 * CE QUE LES RÈGLES PYTHON NE PEUVENT PAS VOIR. Elles lisent les moteurs et
 * la SOURCE de l'écran. Elles ne savent pas ce qui s'affiche réellement, et
 * quatre choses ne vivent que dans un navigateur :
 *
 *   · la carte DORA de l'accueil ouvre-t-elle le bon panneau, ou l'accueil
 *     de Sentinel — le défaut déjà mesuré sur la qualification assistée,
 *     où le `;doraInit()` du menu ne s'exécute PAS par `?goto=` ;
 *   · les six panneaux quittent-ils « Chargement… », ou restent-ils dessus ;
 *   · le verdict d'un prestataire tiers dit-il « rien n'est écarté », ou
 *     recopie-t-il l'écran d'une banque ;
 *   · l'écran de risque REFUSE-t-il visiblement de travailler sans régime,
 *     ou reste-t-il muet — un refus muet se lit comme une panne.
 *
 *     BASE=http://127.0.0.1:5901 node recette_dora.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');

const BASE = process.env.BASE || 'http://127.0.0.1:5901';
const TOKEN = process.env.TOKEN || 'recette_locale_idf_0123456789abcdef';

let ko = 0, n = 0;
const ok = (t, cond, siKo, mesure) => {
  n++;
  if (!cond) ko++;
  console.log((cond ? '  OK   ' : '  KO   ') + t
              + (mesure ? ' — ' + mesure : '')
              + (!cond && siKo ? ' — ' + siKo : ''));
};
const titre = t => console.log('\n' + t);

const PANNEAUX = ['dora-qualifier', 'dora-risque', 'dora-tiers',
                  'dora-incident', 'dora-iso', 'dora-supervision'];

(async () => {
  const nav = await chromium.launch();
  const ctx = await nav.newContext({ viewport: { width: 1500, height: 1100 } });
  await ctx.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
  });
  const pg = await ctx.newPage();
  const err = [];
  pg.on('pageerror', e => err.push(String(e).slice(0, 160)));

  await pg.goto(BASE + '/auth/' + TOKEN, { waitUntil: 'commit' });
  await pg.waitForTimeout(400);

  /* ── 1. LA CARTE DE L'ACCUEIL OUVRE LE PANNEAU, PAS L'ACCUEIL ─────── */
  titre('1. La carte DORA de l\'accueil, par ?goto= — le chemin du visiteur');
  const rep = await pg.goto(BASE + '/sentinel?goto=dora-qualifier',
                            { waitUntil: 'domcontentloaded' });
  ok('la page répond', rep && rep.status() === 200,
     rep ? 'HTTP ' + rep.status() : 'pas de réponse');
  if (!rep || rep.status() !== 200) { await nav.close(); process.exit(2); }
  await pg.waitForTimeout(2600);

  const ouvert = await pg.evaluate(() => {
    const p = document.getElementById('p-dora-qualifier');
    return { visible: !!p && p.classList.contains('on'),
             actif: (document.querySelector('.page.on') || {}).id || null };
  });
  ok('le panneau de qualification est celui qui s\'affiche', ouvert.visible,
     'page affichée : ' + ouvert.actif, ouvert.actif);

  /* LE FORMULAIRE EST PEINT, ET C'EST CE QUE `doraInit` A DÛ FAIRE SANS
     QUE LE `onclick` DU MENU SOIT JAMAIS EXÉCUTÉ. */
  const champs = await pg.evaluate(() => {
    const q = document.getElementById('dora-q');
    const sel = q ? q.querySelector('#dora-entite') : null;
    return { rempli: !!(q && q.innerHTML.trim()),
             options: sel ? sel.options.length : 0,
             groupes: sel ? sel.querySelectorAll('optgroup').length : 0 };
  });
  ok('le formulaire est peint sans passer par le menu', champs.rempli,
     'dora-q est vide : doraInit n\'a pas été amorcé par go()');
  ok('les vingt et un types de l\'article 2 sont proposés',
     champs.options === 22, 'options : ' + champs.options,
     champs.options + ' entrées (dont le libellé vide)');
  ok('les entités financières sont SÉPARÉES du prestataire tiers',
     champs.groupes === 2, 'optgroup : ' + champs.groupes);

  /* ── 2. UNE BANQUE IDENTIFIÉE : L'ARTICLE 4 ÉCARTE ────────────────── */
  titre('2. Établissement de crédit identifié — ce que l\'article 4 écarte');
  /* LA COURSE, FORCÉE — CE CONTRÔLE ÉTAIT INSTABLE, ET C'ÉTAIT L'APPLICATION.
     Les deux champs partent dans la même milliseconde : deux requêtes de
     qualification sont en route, la première avec NIS 2 encore inconnu. Au
     naturel, sa réponse arrivait APRÈS l'autre deux fois sur seize — et
     repeignait l'articulation à vide : « 0 disposition ». Mesuré sur
     l'ancien code comme sur le nouveau, jamais sur un contrôle voisin.
     On ne laisse plus le hasard choisir : la réponse PÉRIMÉE est retardée
     de 400 ms, à chaque passage. L'ancien écran la peignait en dernier,
     à chaque fois ; l'écran corrigé ne peint que la réponse à la DERNIÈRE
     demande. */
  let retardees = 0;
  const retarder = async (route) => {
    const corps = route.request().postData() || '';
    if (/"identifiee_nis2":null/.test(corps)) {
      retardees++;
      const rep = await route.fetch();
      await new Promise(r => setTimeout(r, 400));
      return route.fulfill({ response: rep });
    }
    return route.continue();
  };
  await pg.route('**/api/dora/qualifier', retarder);
  await pg.evaluate(() => {
    window.doraChamp('entite', 'etablissement_credit');
    window.doraChamp('identifiee_nis2', 'oui');
  });
  const lire = () => pg.evaluate(() => {
    const a = document.getElementById('dora-articulation');
    return a ? (a.textContent.match(/Article 2[013]|Chapitre VII/g) || []).length : 0;
  });
  /* Deux lectures : AVANT que la réponse retardée n'arrive (la bonne est là),
     puis bien APRÈS. C'est la seconde qui tombait à 0. */
  await pg.waitForTimeout(250);
  const avantPerimee = await lire();
  await pg.waitForTimeout(1600);
  const apresPerimee = await lire();
  ok('la réponse périmée a bien été retardée — la course est forcée, pas espérée',
     retardees >= 1, retardees + ' réponse(s) retardée(s)');
  ok('LA RÉPONSE PÉRIMÉE NE REPEINT PAS l\'articulation',
     avantPerimee >= 4 && apresPerimee >= 4,
     'avant la réponse périmée : ' + avantPerimee + ', après : ' + apresPerimee);
  await pg.unroute('**/api/dora/qualifier', retarder);
  const banque = await pg.evaluate(() => {
    const v = document.getElementById('dora-verdict');
    const a = document.getElementById('dora-articulation');
    return { verdict: v ? v.textContent.trim().slice(0, 90) : '',
             articulation: a ? a.textContent : '',
             ecartes: a ? (a.textContent.match(/Article 2[013]|Chapitre VII/g)
                           || []).length : 0 };
  });
  ok('le verdict annonce le cadre complet',
     /Cadre complet/.test(banque.verdict), banque.verdict, banque.verdict);
  ok('l\'articulation nomme les quatre dispositions écartées',
     banque.ecartes >= 4, banque.ecartes + ' nommée(s)',
     banque.ecartes + ' dispositions');
  ok('elle dit AUSSI ce qui reste dû — l\'article 3, §3 et §4',
     /article 3, paragraphe 3/.test(banque.articulation)
     && /article 3, paragraphe 4/.test(banque.articulation),
     'l\'écran ne montre que la moitié de la phrase');

  /* ── 3. LE VERROU : UN PRESTATAIRE TIERS NE VOIT RIEN D'ÉCARTÉ ────── */
  titre('3. Prestataire tiers de services TIC — le verrou du module');
  await pg.evaluate(() => { window.doraChamp('entite', 'prestataire_tic'); });
  await pg.waitForTimeout(1600);
  const presta = await pg.evaluate(() => {
    const a = document.getElementById('dora-articulation');
    const t = a ? a.textContent : '';
    return { texte: t,
             ecartes: (t.match(/Article 2[013] —|Chapitre VII —/g) || []).length,
             cumul: /chacun à son titre/.test(t) };
  });
  ok('l\'écran annonce le CUMUL, pas la mise à l\'écart', presta.cumul,
     'l\'écran d\'un hébergeur recopie celui d\'une banque');
  ok('AUCUNE disposition de NIS 2 n\'est présentée comme écartée',
     presta.ecartes === 0, presta.ecartes + ' disposition(s) écartée(s)',
     presta.ecartes + ' écartée(s)');

  /* ── 4. LES SIX PANNEAUX QUITTENT « CHARGEMENT… » ─────────────────── */
  titre('4. Les six écrans du tiroir, ouverts un par un');
  for (const p of PANNEAUX) {
    await pg.evaluate((id) => {
      const it = [...document.querySelectorAll('.sb-item[data-grp="dora"]')]
        .find(x => (x.getAttribute('onclick') || '').indexOf("go('" + id + "'") >= 0);
      if (it) it.click();
    }, p);
    await pg.waitForTimeout(1300);
    const etat = await pg.evaluate((id) => {
      const el = document.getElementById('p-' + id);
      if (!el) return { existe: false };
      const t = el.textContent || '';
      const zones = [...el.querySelectorAll('.veille-loading')]
        .map(z => (z.textContent || '').trim());
      return { existe: true, on: el.classList.contains('on'),
               chargement: zones.filter(z => /^Chargement/.test(z)).length,
               longueur: t.length };
    }, p);
    ok('« ' + p +' » s\'ouvre et n\'attend plus',
       etat.existe && etat.on && etat.chargement === 0,
       etat.existe ? (etat.on ? etat.chargement + ' zone(s) en « Chargement… »'
                              : 'panneau non affiché')
                   : 'panneau absent',
       etat.longueur + ' caractères');
  }

  /* ── 4 bis. ET ILS PEIGNENT VRAIMENT, PAS SEULEMENT UN REFUS ──────
     MESURÉ, ET C'EST CE QUI A FAIT AJOUTER CETTE SECTION. Le contrôle
     ci-dessus ne vérifie que l'absence de « Chargement… ». Or le message
     « le régime n'est pas déterminé » le satisfait AUSSI — et c'est
     exactement ce qui se passait, puisque le type sélectionné à l'étape 3
     était le prestataire tiers, qui n'a pas de régime. Deux panneaux
     passaient donc pour une raison sans rapport avec ce qu'on prétendait
     mesurer. On qualifie d'abord, puis on compte les LIGNES. */
  titre('4 bis. Avec un régime déclaré, les deux tableaux se remplissent');
  await pg.evaluate(() => {
    window.go('dora-qualifier');
    window.doraChamp('entite', 'etablissement_credit');
  });
  await pg.waitForTimeout(1800);

  await pg.evaluate(() => { window.go('dora-risque'); });
  await pg.waitForTimeout(1600);
  const risque = await pg.evaluate(() => {
    const b = document.getElementById('dora-risque-body');
    return { lignes: b ? b.querySelectorAll('tbody tr').length : 0,
             selects: b ? b.querySelectorAll('select').length : 0,
             chapitres: b ? b.querySelectorAll('.cnf-chap').length : 0 };
  });
  ok('les vingt-six articles du titre II sont posés, un par ligne',
     risque.lignes === 26, risque.lignes + ' ligne(s)',
     risque.lignes + ' articles');
  ok('chacun porte sa liste d\u2019états', risque.selects === 26,
     risque.selects + ' liste(s)');
  ok('les cinq chapitres du titre II sont séparés', risque.chapitres === 5,
     risque.chapitres + ' chapitre(s)');

  await pg.evaluate(() => { window.go('dora-iso'); });
  await pg.waitForTimeout(2200);
  const iso = await pg.evaluate(() => {
    const b = document.getElementById('dora-iso-body');
    const t = b ? b.textContent : '';
    return { lignes: b ? b.querySelectorAll('tbody tr').length : 0,
             desamorce: /pas une conformité/.test(t),
             propres: /art\. 27/.test(t) };
  });
  ok('le pont ISO rend les vingt-six articles', iso.lignes === 26,
     iso.lignes + ' ligne(s)', iso.lignes + ' articles');
  ok('le taux est DÉSAMORCÉ dans le même bloc que le nombre',
     iso.desamorce, 'la phrase « pas une conformité » n\u2019est pas à l\u2019écran');
  ok('l\u2019article 27 est nommé comme propre à DORA', iso.propres,
     'le seul article sans répondant dans la norme n\u2019est pas signalé');

  /* ── 5. LE REFUS EST VISIBLE, PAS MUET ───────────────────────────── */
  titre('5. Sans régime, l\'analyse de risque REFUSE — et le dit');
  await pg.evaluate(() => { window.doraChamp('entite', ''); });
  await pg.waitForTimeout(900);
  await pg.evaluate(() => { window.go('dora-risque'); });
  await pg.waitForTimeout(1200);
  const refus = await pg.evaluate(() => {
    const b = document.getElementById('dora-risque-body');
    return b ? b.textContent.trim() : '';
  });
  ok('l\'écran explique le refus au lieu de rester muet',
     /régime n’est pas déterminé/.test(refus),
     'texte affiché : ' + refus.slice(0, 80), refus.slice(0, 72) + '…');
  ok('il propose la marche à suivre', /Qualifier l’entité/.test(refus),
     'aucun renvoi vers la qualification');

  /* ── 5 bis. LE RAIL — CE QUI NE VIT QUE DANS UN NAVIGATEUR ────────
     LES RÈGLES PYTHON LISENT LE MOTEUR ET LA SOURCE. Elles ne savent pas
     si le bloc courant BAT réellement, si les flèches sont tracées, ni
     si le passage automatique déplace vraiment quelqu'un. Trois choses
     n'existent qu'ici, et ce sont celles que le client voit. */
  titre('5 bis. Le rail : les couleurs, les flèches, et le passage automatique');
  await pg.evaluate(() => {
    window.DORA_DECL = { entite: '', identifiee_nis2: null };
    window.DORA_ETATS = {};
    window.go('dora-qualifier');
  });
  await pg.waitForTimeout(900);
  await pg.evaluate(() => { window.doraParcours(); });
  await pg.waitForTimeout(1500);

  const repos = await pg.evaluate(() => {
    const r = document.querySelector('#p-dora-qualifier .dora-rail');
    if (!r) return { absent: true };
    const bs = [...r.querySelectorAll('.dr-bloc')];
    const cour = bs.filter(b => b.classList.contains('courante'));
    return {
      etats: bs.map(b => [...b.classList].filter(c => c !== 'dr-bloc')[0]),
      fleches: r.querySelectorAll('.dr-fleche').length,
      bat: cour.length === 1
        && getComputedStyle(cour[0]).animationName === 'dr-battement',
      manque: (r.querySelector('.dr-manque') || {}).textContent || '',
      /* L'INFOBULLE A QUITTÉ `title` POUR `data-tooltip`, et cette ancre
         est passée avec elle. Un `title` natif ne s'ouvre pas au doigt :
         sur un téléphone, les six infobulles du rail n'existaient pas.
         La convention `data-tooltip` est ouverte au survol, à l'appui ET
         au clavier par /infobulles.js. */
      bulle: bs[0] ? (bs[0].getAttribute('data-tooltip') || '') : '',
      /* ET ON MESURE QUE `title` A BIEN DISPARU : deux infobulles sur le
         même bouton s'afficheraient l'une sur l'autre à la souris. */
      titreNatif: bs.filter(b => b.getAttribute('title')).length
    };
  });
  ok('le rail est peint sur le panneau de qualification', !repos.absent,
     'aucun rail dans le DOM');
  ok('cinq flèches relient les six blocs', repos.fleches === 5,
     repos.fleches + ' flèche(s)', repos.fleches + ' flèches');
  ok('un seul bloc bat, et il bat vraiment', repos.bat,
     'aucun bloc ne porte l’animation dr-battement');
  ok('les cinq autres sont verrouillés faute de qualification',
     repos.etats.filter(e => e === 'verrouillee').length === 5,
     repos.etats.join(' · '), repos.etats.join(' · '));
  ok('le bloc qui bat NOMME ce qui lui manque',
     /type d[’']entité/.test(repos.manque)
     && /identification/i.test(repos.manque),
     'le rail dit qu’il attend, sans dire quoi');
  ok('l’infobulle porte le piège du bloc',
     /Le piège ?:/.test(repos.bulle) || /Le piège :/.test(repos.bulle),
     repos.bulle.slice(0, 70));
  ok('aucun bloc ne garde un `title` natif en plus',
     repos.titreNatif === 0,
     repos.titreNatif + ' bloc(s) porteraient deux infobulles');

  /* ── LA VALIDATION VERDIT, ET LE DÉCOMPTE PART ─────────────────── */
  await pg.evaluate(() => {
    window.doraChamp('entite', 'etablissement_credit');
  });
  await pg.waitForTimeout(1200);
  await pg.evaluate(() => { window.doraChamp('identifiee_nis2', 'oui'); });
  await pg.waitForTimeout(2000);

  const valide = await pg.evaluate(() => {
    const r = document.querySelector('.page.on .dora-rail');
    const bs = r ? [...r.querySelectorAll('.dr-bloc')] : [];
    return {
      etats: bs.map(b => [...b.classList].filter(c => c !== 'dr-bloc')[0]),
      barre: r ? ((r.querySelector('.dr-barre i') || {}).style || {}).width : '',
      auto: r ? ((r.querySelector('.dr-auto') || {}).textContent || '')
                  .replace(/\s+/g, ' ') : ''
    };
  });
  ok('le premier bloc passe au VERT', valide.etats[0] === 'validee',
     'état : ' + valide.etats[0], valide.etats[0]);
  ok('le bloc suivant prend le relais en bleu',
     valide.etats[1] === 'courante', valide.etats.join(' · '));
  ok('la supervision devient SANS OBJET pour une entité financière',
     valide.etats[5] === 'sans_objet', valide.etats.join(' · '),
     'article 31, §8, i)');
  ok('la barre suit l’avancement', valide.barre === '20%',
     'largeur : ' + valide.barre, valide.barre);
  ok('le décompte du passage automatique s’affiche',
     /Passage à/.test(valide.auto), valide.auto.slice(0, 90),
     valide.auto.slice(0, 60) + '…');
  ok('il offre de rester', /Rester ici/.test(valide.auto),
     'on est déplacé sans pouvoir refuser');

  /* ── ET IL DÉPLACE VRAIMENT ────────────────────────────────────── */
  await pg.waitForTimeout(5200);
  const arrive = await pg.evaluate(() => (document.querySelector('.page.on')
                                          || {}).id || '');
  ok('le passage automatique ouvre le bloc suivant',
     arrive === 'p-dora-iso', 'page ouverte : ' + arrive, arrive);

  /* ── LE FREIN MARCHE, ET C'EST AUSSI IMPORTANT QUE LE DÉPART ───── */
  titre('5 ter. Le frein : « Rester ici » retient vraiment');
  await pg.evaluate(() => {
    window.go('dora-iso');
    window.DORA_ISO.certifie = null;
  });
  await pg.waitForTimeout(900);
  await pg.evaluate(() => { window.doraIso('iso27001_certifie', 'non'); });
  await pg.waitForTimeout(1600);
  const avant = await pg.evaluate(() => (document.querySelector('.page.on')
                                         || {}).id || '');
  await pg.evaluate(() => {
    const b = [...document.querySelectorAll('.page.on .dr-auto button')]
      .find(x => /Rester ici/.test(x.textContent));
    if (b) b.click();
  });
  await pg.waitForTimeout(5200);
  const apresFrein = await pg.evaluate(() => ({
    page: (document.querySelector('.page.on') || {}).id || '',
    auto: document.querySelectorAll('.page.on .dr-auto').length
  }));
  ok('« Rester ici » retient sur place',
     apresFrein.page === avant && avant === 'p-dora-iso',
     'parti de ' + avant + ' vers ' + apresFrein.page, apresFrein.page);
  ok('le décompte disparaît une fois annulé', apresFrein.auto === 0,
     apresFrein.auto + ' décompte(s) encore à l’écran');

  /* ── 6. AUCUNE ERREUR DE PAGE ────────────────────────────────────── */
  titre('6. La console');
  ok('aucune erreur JavaScript', err.length === 0, err.join(' | '),
     err.length + ' erreur(s)');

  console.log('\n' + (ko ? 'KO ' + ko + '/' + n : 'TOUT VERT ' + n + '/' + n));
  await nav.close();
  process.exit(ko ? 1 : 0);
})();
