const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const BASE = process.env.BASE || 'http://127.0.0.1:5415';
const TOKEN = 'recette_locale_idf_0123456789abcdef';
let ko = 0;
const ok=(n,c,d)=>{console.log('  '+(c?'OK ':'KO ')+'  '+n+(d?' — '+d:''));if(!c)ko++;};
const MES=`(el)=>{const lum=c=>{const a=c.map(v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)});return .2126*a[0]+.7152*a[1]+.0722*a[2]};
const rgb=s=>{const m=String(s).match(/[\\d.]+/g);return m?m.map(Number):null};
let fond=[255,255,255];for(let n=el;n&&n.nodeType===1;n=n.parentElement){const c=rgb(getComputedStyle(n).backgroundColor);if(c&&(c.length<4||c[3]>0.99)){fond=c.slice(0,3);break}}
const t=rgb(getComputedStyle(el).color)||[0,0,0];const l1=lum(t.slice(0,3)),l2=lum(fond);
return Math.round(((Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05))*100)/100}`;
(async()=>{
  const nav=await chromium.launch();
  const ctx=await nav.newContext({viewport:{width:1500,height:1100}});
  await ctx.route('**/*',r=>(['image','font','media'].includes(r.request().resourceType())?r.abort():r.continue()));
  const pg=await ctx.newPage(); const err=[]; pg.on('pageerror',e=>err.push(String(e)));
  await pg.goto(BASE+'/auth/'+TOKEN,{waitUntil:'commit'});
  await pg.goto(BASE+'/panorama',{waitUntil:'domcontentloaded'});
  const vu=await pg.waitForSelector('.imp-conc',{timeout:60000}).then(()=>1).catch(()=>0);
  ok('le bloc de conception s’affiche sous les curseurs',!!vu);
  if(!vu){await nav.close();console.log('\n1 échec\n');process.exit(1);}
  const c=await pg.evaluate(()=>{const z=document.querySelector('.imp-conc');
    return{t:(z.innerText||'').replace(/\s+/g,' '),inc:z.querySelectorAll('.imp-i').length,q:z.querySelectorAll('.imp-conc-q li').length}});
  ok('…avec la température de projet',/37,7 °C/.test(c.t));
  ok('…et la période de retour qui est le défaut',/200 ans/.test(c.t));
  ok('…la prescription chiffrée',/11 %/.test(c.t)&&/48 %/.test(c.t));
  ok('les défaillances sont listées avec leur mécanisme',c.inc>=4,c.inc+' entrées');
  ok('…dont Pantin, et l’eau y est nommée comme cause',/Pantin/.test(c.t)&&/ALIMENTATION EN EAU/.test(c.t));
  ok('les questions au concepteur sont là',c.q>=3,c.q+' questions');
  ok('la règle de conjonction est publiée avec ses pays',/DEUX conditions/.test(c.t)&&/pays/.test(c.t));
  /* LE PAYS TÉMOIN DÉPEND DE L'HORIZON, et l'horizon par défaut est 2030.
     Écrit sur la France, ce contrôle tombait — non parce que le drapeau manque,
     mais parce que la France n'est signalée qu'à 2050. Un contrôle qui ignore
     la date accuse à tort le jour où la règle fait exactement son travail.
     On prend donc la Belgique, signalée dès 2030 (eau déjà classée élevée). */
  const fr=await pg.evaluate(()=>{const f=document.querySelector('.imp-fiche[data-pays="BE"]');
    if(!f)return null;f.open=true;const z=f.querySelector('.imp-conj');
    return z?(z.innerText||'').replace(/\s+/g,' '):''});
  ok('la fiche Belgique porte le drapeau dès l’horizon 2030',!!fr,(fr||'').slice(0,60));
  const nb=await pg.evaluate(()=>document.querySelectorAll('.imp-conj').length);
  ok('…et le drapeau reste RARE à cet horizon — sinon il ne signale plus rien',
     nb>0&&nb<=5,nb+' pays signalés sur la page');
  if(fr){ok('…il dit qu’il n’entre dans AUCUNE note',/aucune note/.test(fr));
         ok('…et il porte son motif',/été doux/.test(fr));}
  const es=await pg.evaluate(()=>{const f=document.querySelector('.imp-fiche[data-pays="ES"]');
    if(!f)return null;f.open=true;return !!f.querySelector('.imp-conj')});
  ok('l’Espagne, méridionale, ne porte PAS le drapeau',es===false);
  const m=await pg.evaluate((f)=>{const g=eval('('+f+')');
    return [['chiffre de conception','.imp-conc-k em'],['note de période de retour','.imp-conc-k i'],
            ['mécanisme d’un incident','.imp-i-m'],['éditeur de la prescription','.imp-conc-p .imp-src'],
            ['drapeau de conjonction','.imp-conj p']]
      .map(([n,s])=>{const e=document.querySelector(s);return{n:n,t:!!e,r:e?g(e):null}})},MES);
  m.forEach(x=>ok(x.n+' se lit',x.t&&x.r>=4.5,x.t?x.r+':1':'introuvable'));
  ok('aucune erreur de script',err.length===0,err.slice(0,2).join(' | '));
  await nav.close();console.log('\n'+(ko?ko+' contrôle(s) en échec':'tout est vert')+'\n');process.exit(ko?1:0);
})();
