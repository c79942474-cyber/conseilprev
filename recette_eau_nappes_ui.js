/* LA SECTION D'EAU RÉAGENCÉE, ET LES NAPPES FRANÇAISES SOUS LE FONCIER ANNONCÉ.
 *
 * DEUX DEMANDES, UN SEUL ÉCRAN. La section comptait neuf blocs à la suite, tous
 * dépliés : personne ne lit neuf blocs. Elle est désormais faite de dépliants
 * dont UN SEUL est ouvert — celui qui tranche l'arbitrage — et dont aucun n'est
 * MUET une fois replié : chaque résumé porte de quoi décider s'il faut l'ouvrir.
 * S'y ajoute le contraste que la note nationale du comparateur écrase : l'état
 * des nappes françaises, croisé au foncier que l'État a identifié pour les
 * centres de données.
 *
 * CE QUI NE SE PROUVE QUE DANS UN NAVIGATEUR :
 *   · qu'un seul dépliant est ouvert, et que c'est le bon ;
 *   · qu'aucun résumé n'est muet — un sommaire qui obligerait à tout ouvrir
 *     pour savoir où regarder ne serait pas un sommaire ;
 *   · que les infobulles sont RÉELLEMENT branchées et s'ouvrent ;
 *   · que le lien de pédagogie démarre un vrai parcours guidé ;
 *   · que le bloc des nappes arrive jusqu'à la page — il a d'abord disparu, et
 *     pour une raison qui n'était pas dans ce fichier : la tâche de fond
 *     écrasait le cache de l'empreinte avec une charge plus pauvre, toutes les
 *     trente minutes. C'est ce contrôle qui l'a mis au jour.
 *
 *   POUR L'EXÉCUTER :  BASE=http://127.0.0.1:5419 node recette_eau_nappes_ui.js
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE=process.env.BASE||'http://127.0.0.1:5418', TOKEN='recette_locale_idf_0123456789abcdef';
let ko=0; const ok=(n,c,d)=>{console.log('  '+(c?'OK ':'KO ')+'  '+n+(d?' — '+d:''));if(!c)ko++;};
const titre=t=>console.log('\n══ '+t+' ══\n');
(async()=>{
  const nav=await chromium.launch();
  const ctx=await nav.newContext({viewport:{width:1500,height:1100}});
  await ctx.route('**/*',r=>(['image','font','media'].includes(r.request().resourceType())?r.abort():r.continue()));
  const pg=await ctx.newPage(); const err=[]; pg.on('pageerror',e=>err.push(String(e)));
  await pg.goto(BASE+'/auth/'+TOKEN,{waitUntil:'commit'});
  await pg.goto(BASE+'/empreinte-parc',{waitUntil:'domcontentloaded'});

  titre('1. La section est réagencée en dépliants');
  const vu=await pg.waitForSelector('#eau-source .eau-d',{timeout:60000}).then(()=>1).catch(()=>0);
  ok('les dépliants sont là',!!vu);
  if(!vu){await nav.close();console.log('\n1 échec\n');process.exit(1);}
  const d=await pg.evaluate(()=>[...document.querySelectorAll('#eau-source .eau-d')]
    .map(x=>({s:(x.querySelector('summary').innerText||'').replace(/\s+/g,' '),
              ouvert:x.hasAttribute('open'),
              indice:!!x.querySelector('.dpl-i')})));
  ok('la section compte plusieurs blocs repliables',d.length>=7,d.length+' dépliants');
  ok('AUCUN DÉPLIANT N’EST MUET UNE FOIS REPLIÉ',d.every(x=>x.indice),
     d.filter(x=>!x.indice).map(x=>x.s.slice(0,30)).join(' | ')||'tous portent leur indice');
  ok('un seul est ouvert par défaut : celui qui tranche',
     d.filter(x=>x.ouvert).length===1,d.filter(x=>x.ouvert).map(x=>x.s.slice(0,40)).join(''));

  titre('2. La pédagogie : par où commencer, et le parcours guidé');
  const g=await pg.evaluate(()=>{const z=document.querySelector('#eau-source .eau-guide');
    return z?{t:(z.innerText||'').replace(/\s+/g,' '),lien:!!z.querySelector('[data-gp]')}:null});
  ok('la bande « par où commencer » est là',!!g);
  if(g){ok('…elle dit quels blocs décident',/mode par mode/.test(g.t));
        ok('…et elle propose le parcours guidé',g.lien);}
  const gp=await pg.evaluate(async()=>{const a=document.querySelector('#eau-source [data-gp]');
    if(!a)return null;a.click();await new Promise(r=>setTimeout(r,600));
    /* Les panneaux de parcours sont des IDENTIFIANTS, pas des classes — mon
       sélecteur les cherchait par classe et ne trouvait rien : un faux échec. */
    const c=document.getElementById('gp-carte'), ch=document.getElementById('gp-choix');
    return {ouvert:!!((c&&c.classList.contains('on'))||(ch&&ch.classList.contains('on')))}});
  ok('le lien ouvre réellement un parcours',gp&&gp.ouvert);
  /* REFERMER LE PARCOURS AVANT LA SUITE. Échap ne suffisait pas : le parcours
     restait ouvert, son voile par-dessus la section, et le contrôle suivant
     déclarait le bloc des nappes absent alors qu'il était simplement recouvert.
     Une recette qui laisse un état ouvert accuse le contrôle d'après. */
  await pg.evaluate(() => { if (typeof gpFermer === 'function') gpFermer(); });
  await pg.waitForTimeout(300);

  titre('3. Les infobulles sur les termes qui bloquent');
  /* `:not(.aide)` : aideBrancher pose un BOUTON qui porte lui aussi data-aide.
     Sans cette exclusion, chaque terme était compté deux fois et le bouton
     lui-même passait pour un terme non équipé — un faux échec sur un mécanisme
     qui fonctionnait. */
  const inf=await pg.evaluate(()=>[...document.querySelectorAll('#eau-source [data-aide]:not(.aide)')]
    .map(x=>({cle:x.getAttribute('data-aide'),bouton:!!x.querySelector(':scope > .aide')})));
  ok('des termes portent une infobulle',inf.length>=4,inf.map(x=>x.cle).join(' '));
  ok('…et chacune a bien reçu son bouton',inf.every(x=>x.bouton),
     inf.filter(x=>!x.bouton).map(x=>x.cle).join(' ')||'toutes branchées');
  const bulle=await pg.evaluate(async()=>{const b=document.querySelector('#eau-source .aide');
    if(!b)return null;b.click();await new Promise(r=>setTimeout(r,300));
    const z=document.querySelector('.aide-bulle.on');
    return z?(z.innerText||'').replace(/\s+/g,' ').slice(0,80):''});
  ok('une infobulle s’ouvre vraiment',!!bulle,bulle||'rien');

  titre('4. LE POINT DEMANDÉ : les nappes françaises sous le foncier annoncé');
  const nap=await pg.evaluate(()=>{const z=[...document.querySelectorAll('#eau-source .eau-d')]
    .find(x=>/bassin par bassin/.test(x.querySelector('summary').innerText));
    if(!z)return null; z.open=true;
    return {resume:(z.querySelector('summary').innerText||'').replace(/\s+/g,' '),
            regions:z.querySelectorAll('.eau-n').length,
            foncier:z.querySelectorAll('.eau-n.fonc').length,
            tresbas:z.querySelectorAll('.eau-n.tresbas').length,
            gris:z.querySelectorAll('.eau-n.gris').length,
            texte:(z.innerText||'').replace(/\s+/g,' ')}});
  ok('le bloc des nappes existe',!!nap);
  if(nap){
    ok('…son résumé annonce déjà le résultat',/foncier identifié/.test(nap.resume)&&/BAISSE/.test(nap.resume),nap.resume.slice(0,90));
    ok('…les régions sont affichées',nap.regions>=10,nap.regions+' régions');
    ok('…celles à foncier identifié sont marquées',nap.foncier>=8,nap.foncier+' marquées');
    ok('…les nappes très basses se voient au liseré',nap.tresbas>=3,nap.tresbas+' en très bas');
    ok('L’AVERTISSEMENT DE SAISON PRÉCÈDE LES CHIFFRES',/creux de l’année/i.test(nap.texte));
    ok('…et le bloc dit qu’AUCUNE note n’en sort',/Aucune note n’en sort/.test(nap.texte));
    ok('…la source BRGM et sa date sont citées',/BRGM/.test(nap.texte)&&/1er août 2026/.test(nap.texte));
    ok('…le gris est déclaré absence de donnée, pas feu vert',
       nap.gris===0||/absence de donnée/.test(nap.texte));
  }

  titre('5. Les mots-clés qui mènent ailleurs');
  const v=await pg.evaluate(()=>{const z=document.querySelector('#eau-source .eau-vers');
    return z?[...z.querySelectorAll('a')].map(a=>a.getAttribute('href')):null});
  ok('la section renvoie vers les modules voisins',v&&v.length>=3,(v||[]).join(' '));
  ok('…dont le comparateur d’implantation',(v||[]).some(x=>/s-implantation/.test(x)));
  ok('aucune erreur de script',err.length===0,err.slice(0,2).join(' | '));
  await nav.close();console.log('\n'+(ko?ko+' contrôle(s) en échec':'tout est vert')+'\n');process.exit(ko?1:0);
})();
