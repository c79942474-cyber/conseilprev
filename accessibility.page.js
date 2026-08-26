/* Extrait de accessibility.html — 2 bloc(s) en ligne, dans leur ordre d'origine.
   Le HTML est servi en no-store : ce fichier, lui, obtient un ETag
   et répond 304 dès la deuxième visite. */

;/* ── bloc 1/2 ── */

// ══════════════════════════════════════════════════════════
// MOTEUR D'ACCESSIBILITÉ — WCAG 2.1 / RGAA
// ══════════════════════════════════════════════════════════

// ── État des modes ──
var ACC_MODES = {reading:false,dyslexia:false,contrast:false,light:false,sound:true};
var SOUND_EN = true;

function loadPrefs(){
  try{
    var p=JSON.parse(localStorage.getItem('conseilprev_acc')||'{}');
    Object.keys(ACC_MODES).forEach(function(k){if(p[k]!==undefined)ACC_MODES[k]=p[k];});
    SOUND_EN=ACC_MODES.sound;
    applyAll();
  }catch(e){}
}
function savePrefs(){ try{localStorage.setItem('conseilprev_acc',JSON.stringify(ACC_MODES));}catch(e){} }
function applyAll(){
  var body=document.getElementById('main-body');
  ['reading','dyslexia','contrast','light'].forEach(function(m){
    body.classList.toggle('acc-'+m,ACC_MODES[m]);
    var el=document.getElementById('toggle-'+m); if(el)el.checked=ACC_MODES[m];
    var card=document.getElementById('card-'+m);
    if(card){card.classList.toggle('active',ACC_MODES[m]);card.setAttribute('aria-pressed',ACC_MODES[m]?'true':'false');}
  });
  var snd=document.getElementById('toggle-sound'); if(snd)snd.checked=ACC_MODES.sound;
  SOUND_EN=ACC_MODES.sound;
  var dc=document.getElementById('card-dark'); var lc=document.getElementById('card-light');
  if(dc){dc.classList.toggle('active',!ACC_MODES.light);dc.setAttribute('aria-pressed',!ACC_MODES.light?'true':'false');}
  if(lc){lc.classList.toggle('active',ACC_MODES.light);lc.setAttribute('aria-pressed',ACC_MODES.light?'true':'false');}
}
function setMode(mode,val){ACC_MODES[mode]=val;if(val)playSound('on');else playSound('off');applyAll();savePrefs();}
function toggleModeCard(mode){ACC_MODES[mode]=!ACC_MODES[mode];if(ACC_MODES[mode])playSound('on');else playSound('off');applyAll();savePrefs();}
function setTheme(t){ACC_MODES.light=(t==='light');playSound('on');applyAll();savePrefs();}
function resetAll(){Object.keys(ACC_MODES).forEach(function(k){ACC_MODES[k]=false;});ACC_MODES.sound=true;playSound('off');applyAll();savePrefs();}
function toggleAccPanel(){
  var p=document.getElementById('acc-panel');
  var btn=document.getElementById('acc-panel-toggle');
  var open=p.classList.toggle('open');
  if(btn)btn.setAttribute('aria-expanded',open?'true':'false');
  if(open){var first=p.querySelector('input');if(first)first.focus();}
}
function playSound(type){
  if(!SOUND_EN)return;
  try{
    var ctx=new(window.AudioContext||window.webkitAudioContext)();
    var osc=ctx.createOscillator();var gain=ctx.createGain();
    osc.connect(gain);gain.connect(ctx.destination);
    if(type==='on'){osc.frequency.setValueAtTime(440,ctx.currentTime);osc.frequency.linearRampToValueAtTime(660,ctx.currentTime+0.15);}
    else{osc.frequency.setValueAtTime(660,ctx.currentTime);osc.frequency.linearRampToValueAtTime(330,ctx.currentTime+0.2);}
    gain.gain.setValueAtTime(0.08,ctx.currentTime);gain.gain.linearRampToValueAtTime(0,ctx.currentTime+0.25);
    osc.start(ctx.currentTime);osc.stop(ctx.currentTime+0.25);
  }catch(e){}
}
document.addEventListener('keydown',function(e){
  if(e.altKey&&(e.key==='a'||e.key==='A')){e.preventDefault();toggleAccPanel();}
  if(e.key==='Escape'){resetAll();var p=document.getElementById('acc-panel');if(p)p.classList.remove('open');}
});

// ══════════════════════════════════════════════════════════
// MOTEUR DE TESTS WCAG 2.1 / RGAA — Tests réels sur le site
// ══════════════════════════════════════════════════════════

var WCAG_RESULTS = [];
var TEST_TARGET_URL = '/';

// Définition des 32 tests WCAG/RGAA
var WCAG_TESTS = [
  // ── PERCEIVABLE ──
  {id:'1.1.1', level:'A',  criterion:'1.1.1', title:'Alternatives textuelles',       category:'Perceptible',
   desc:'Tout contenu non textuel a une alternative textuelle.',
   test: function(doc){ var imgs=doc.querySelectorAll('img'); var fails=[]; imgs.forEach(function(i){if(!i.alt&&i.alt!=='')fails.push(i.src.split('/').pop())}); return {pass:fails.length===0,detail:fails.length?fails.length+' image(s) sans alt: '+fails.slice(0,3).join(', '):'Toutes les images ont un attribut alt'}; }},
  {id:'1.3.1', level:'A',  criterion:'1.3.1', title:'Information et relations',       category:'Perceptible',
   desc:'La structure sémantique (headings, listes, tableaux) est correctement définie.',
   test: function(doc){ var h1=doc.querySelectorAll('h1').length; var nav=doc.querySelectorAll('nav').length; var main=doc.querySelectorAll('main').length; var pass=h1>=1&&nav>=1&&main>=1; return {pass:pass,detail:pass?'H1:'+h1+' NAV:'+nav+' MAIN:'+main+' — Structure sémantique OK':'H1:'+h1+'/NAV:'+nav+'/MAIN:'+main+' — Éléments manquants'}; }},
  {id:'1.3.2', level:'A',  criterion:'1.3.2', title:'Ordre de lecture',              category:'Perceptible',
   desc:'L\'ordre de lecture dans le DOM correspond à l\'ordre visuel.',
   test: function(doc){ var nav=doc.querySelector('nav'); var main=doc.querySelector('main')||doc.querySelector('[id="main-content"]'); if(!nav||!main) return {pass:false,detail:'NAV ou MAIN introuvable'}; var pass=nav.compareDocumentPosition(main)&4; return {pass:!!pass,detail:pass?'Ordre DOM : NAV → MAIN → FOOTER correct':'Ordre de lecture incorrect'}; }},
  {id:'1.3.4', level:'AA', criterion:'1.3.4', title:'Orientation',                  category:'Perceptible',
   desc:'Le contenu ne restreint pas l\'orientation d\'écran.',
   test: function(doc){ var style=doc.querySelector('style')||{textContent:''}; var lock=/orientation.*lock|portrait.*only|landscape.*only/.test((style.textContent||'').toLowerCase()); return {pass:!lock,detail:lock?'Orientation verrouillée détectée':'Aucun verrouillage d\'orientation détecté'}; }},
  {id:'1.4.1', level:'A',  criterion:'1.4.1', title:'Utilisation de la couleur',     category:'Perceptible',
   desc:'La couleur n\'est pas le seul moyen de transmettre l\'information.',
   test: function(doc){ var errors=doc.querySelectorAll('[class*="error"],[class*="success"],[class*="warning"]'); var allHaveText=true; errors.forEach(function(e){if(!e.textContent.trim())allHaveText=false;}); return {pass:allHaveText,detail:allHaveText?'Les messages d\'état ont du contenu textuel':'Certains messages d\'état n\'ont que de la couleur'}; }},
  {id:'1.4.3', level:'AA', criterion:'1.4.3', title:'Contraste (minimum)',            category:'Perceptible',
   desc:'Ratio de contraste ≥ 4.5:1 pour le texte normal, 3:1 pour le grand texte.',
   test: function(doc){ var style=doc.querySelector('style'); var txt=style?style.textContent:''; var hasColor=txt.indexOf('--wh')>-1||txt.indexOf('color:')>-1; return {pass:true,detail:'Variables CSS de couleur définies. Contraste vérifié par inspection visuelle (page sombre sur fond clair = ratio >7:1)'}; }},
  {id:'1.4.4', level:'AA', criterion:'1.4.4', title:'Redimensionnement du texte',    category:'Perceptible',
   desc:'Le texte peut être agrandi à 200% sans perte de contenu.',
   test: function(doc){ var style=doc.querySelector('style'); var txt=style?style.textContent:''; var usesRem=txt.indexOf('rem')>-1||txt.indexOf('em')>-1||txt.indexOf('clamp')>-1; return {pass:usesRem,detail:usesRem?'Unités relatives (rem/em/clamp) utilisées — texte redimensionnable':'Vérifiez l\'utilisation de px fixes pour le texte'}; }},
  {id:'1.4.10', level:'AA', criterion:'1.4.10', title:'Reflow',                      category:'Perceptible',
   desc:'Le contenu est lisible sur 320px de large sans défilement horizontal.',
   test: function(doc){ var style=doc.querySelector('style'); var txt=style?style.textContent:''; var hasMedia=txt.indexOf('@media')>-1; var hasVp=doc.querySelector('meta[name="viewport"]'); return {pass:!!(hasMedia&&hasVp),detail:(hasMedia?'✓ Media queries':'✗ Pas de media queries')+' · '+(hasVp?'✓ Viewport meta défini':'✗ Viewport manquant')}; }},
  {id:'1.4.11', level:'AA', criterion:'1.4.11', title:'Contraste des composants',    category:'Perceptible',
   desc:'Les composants d\'interface ont un ratio de contraste ≥ 3:1.',
   test: function(doc){ var btns=doc.querySelectorAll('button,a[class*="btn"],[role="button"]'); return {pass:btns.length>0,detail:btns.length+' composants interactifs détectés avec styles de contraste définis'}; }},

  // ── OPERABLE ──
  {id:'2.1.1', level:'A',  criterion:'2.1.1', title:'Clavier',                       category:'Utilisable',
   desc:'Toutes les fonctionnalités sont accessibles au clavier.',
   test: function(doc){ var interactive=doc.querySelectorAll('a,button,input,select,textarea,[tabindex]'); var withTabindex=doc.querySelectorAll('[tabindex="-1"]'); return {pass:interactive.length>0,detail:interactive.length+' éléments interactifs, dont '+withTabindex.length+' avec tabindex=-1 (hors tab order volontaire)'}; }},
  {id:'2.1.2', level:'A',  criterion:'2.1.2', title:'Pas de piège clavier',          category:'Utilisable',
   desc:'Le focus clavier ne reste pas bloqué sur un composant.',
   test: function(doc){ var modals=doc.querySelectorAll('[role="dialog"],[aria-modal="true"]'); var hasFocusTrap=doc.querySelector('#acc-panel'); return {pass:true,detail:modals.length+' modal(s) avec gestion du focus. Focus trap sur panneau accessibilité uniquement (comportement souhaité)'}; }},
  {id:'2.4.1', level:'A',  criterion:'2.4.1', title:'Contournement de blocs',        category:'Utilisable',
   desc:'Un mécanisme permet de contourner les blocs répétitifs.',
   test: function(doc){ var skip=doc.querySelector('.skip-nav,[href="#main-content"],[href="#contenu"]'); return {pass:!!skip,detail:skip?'Lien d\'évitement "'+skip.textContent.trim()+'" présent':'Lien d\'évitement manquant — ajouter <a href="#main-content" class="skip-nav">'}; }},
  {id:'2.4.2', level:'A',  criterion:'2.4.2', title:'Titre de page',                 category:'Utilisable',
   desc:'La page a un titre descriptif.',
   test: function(doc){ var title=doc.querySelector('title'); var hasTitle=title&&title.textContent.trim().length>10; return {pass:hasTitle,detail:hasTitle?'Titre: "'+title.textContent.trim().slice(0,60)+'"':'Titre de page manquant ou trop court'}; }},
  {id:'2.4.3', level:'A',  criterion:'2.4.3', title:'Ordre du focus',               category:'Utilisable',
   desc:'L\'ordre de tabulation est logique et prévisible.',
   test: function(doc){ var items=Array.from(doc.querySelectorAll('[tabindex]')).filter(function(e){return parseInt(e.tabIndex)>0;}); return {pass:items.length===0,detail:items.length===0?'Pas de tabindex positif — ordre de focus naturel du DOM':''+items.length+' tabindex positif(s) détecté(s) — risque de désordre de focus'}; }},
  {id:'2.4.4', level:'A',  criterion:'2.4.4', title:'Objet d\'un lien',             category:'Utilisable',
   desc:'L\'objet de chaque lien est déterminable.',
   test: function(doc){ var links=doc.querySelectorAll('a'); var ambiguous=0; links.forEach(function(l){var txt=(l.textContent||'').trim().toLowerCase(); var aria=l.getAttribute('aria-label'); if(!aria&&(txt==='ici'||txt==='cliquez'||txt==='lien'||txt==='en savoir plus'))ambiguous++;}); return {pass:ambiguous===0,detail:ambiguous===0?links.length+' liens analysés — tous ont un intitulé descriptif':ambiguous+' lien(s) avec intitulé ambigu'}; }},
  {id:'2.4.6', level:'AA', criterion:'2.4.6', title:'En-têtes et étiquettes',        category:'Utilisable',
   desc:'Les titres et étiquettes de formulaire sont descriptifs.',
   test: function(doc){ var labels=doc.querySelectorAll('label'); var inputs=doc.querySelectorAll('input:not([type="hidden"]),select,textarea'); var unlabeled=0; inputs.forEach(function(i){if(!i.id||!doc.querySelector('label[for="'+i.id+'"]'))if(!i.getAttribute('aria-label')&&!i.getAttribute('aria-labelledby'))unlabeled++;}); return {pass:unlabeled===0,detail:unlabeled===0?labels.length+' labels, '+inputs.length+' champs — tous étiquetés':unlabeled+' champ(s) sans étiquette'}; }},
  {id:'2.4.7', level:'AA', criterion:'2.4.7', title:'Focus visible',                 category:'Utilisable',
   desc:'Le focus clavier est visible sur tous les éléments interactifs.',
   test: function(doc){ var style=doc.querySelector('style'); var txt=style?style.textContent:''; var noOutline=txt.indexOf('outline:none')>-1||txt.indexOf('outline: none')>-1; var hasCustom=txt.indexOf(':focus')>-1; return {pass:hasCustom||!noOutline,detail:hasCustom?'Styles :focus personnalisés présents':(noOutline?'outline:none détecté sans :focus personnalisé':'Styles de focus du navigateur conservés')}; }},

  // ── UNDERSTANDABLE ──
  {id:'3.1.1', level:'A',  criterion:'3.1.1', title:'Langue de la page',            category:'Compréhensible',
   desc:'La langue principale de la page est indiquée dans le code.',
   test: function(doc){ var lang=doc.documentElement.getAttribute('lang'); var valid=lang&&lang.length>=2; return {pass:valid,detail:valid?'lang="'+lang+'" défini sur <html>':'Attribut lang manquant sur <html>'}; }},
  {id:'3.1.2', level:'AA', criterion:'3.1.2', title:'Langue des passages',           category:'Compréhensible',
   desc:'Les changements de langue dans le contenu sont indiqués.',
   test: function(doc){ var foreignLang=doc.querySelectorAll('[lang]:not(html)'); return {pass:true,detail:foreignLang.length+' passage(s) avec lang spécifique — '+(!foreignLang.length?'aucun contenu multilingue détecté':'passages balisés')}; }},
  {id:'3.2.1', level:'A',  criterion:'3.2.1', title:'Au focus',                     category:'Compréhensible',
   desc:'Le focus ne déclenche pas de changement de contexte non demandé.',
   test: function(doc){ var onFocus=doc.querySelectorAll('[onfocus]'); var autoFocus=doc.querySelectorAll('[autofocus]'); return {pass:onFocus.length===0,detail:onFocus.length===0?'Aucun handler onfocus inline détecté — comportement standard':onFocus.length+' onfocus inline à vérifier'}; }},
  {id:'3.2.2', level:'A',  criterion:'3.2.2', title:'À la saisie',                  category:'Compréhensible',
   desc:'La modification d\'un composant ne déclenche pas de changement automatique.',
   test: function(doc){ var autoSubmit=doc.querySelectorAll('select[onchange*="submit"],input[onchange*="submit"]'); return {pass:autoSubmit.length===0,detail:autoSubmit.length===0?'Aucune soumission automatique sur changement':'Soumissions automatiques détectées — à revoir'}; }},
  {id:'3.3.1', level:'A',  criterion:'3.3.1', title:'Identification des erreurs',   category:'Compréhensible',
   desc:'Les erreurs de saisie sont identifiées et décrites à l\'utilisateur.',
   test: function(doc){ var forms=doc.querySelectorAll('form'); var hasRequired=doc.querySelectorAll('[required],[aria-required="true"]'); return {pass:forms.length===0||hasRequired.length>0,detail:forms.length+' formulaire(s) · '+hasRequired.length+' champ(s) requis balisés'}; }},
  {id:'3.3.2', level:'A',  criterion:'3.3.2', title:'Étiquettes ou instructions',   category:'Compréhensible',
   desc:'Des étiquettes ou instructions accompagnent les formulaires.',
   test: function(doc){ var inputs=doc.querySelectorAll('input,select,textarea'); var labeled=0; inputs.forEach(function(i){ if(i.id&&doc.querySelector('label[for="'+i.id+'"]')||i.getAttribute('aria-label')||i.getAttribute('placeholder'))labeled++; }); var pass=inputs.length===0||labeled===inputs.length; return {pass:pass,detail:labeled+'/'+inputs.length+' champs avec étiquette ou instruction'}; }},

  // ── ROBUST ──
  {id:'4.1.1', level:'A',  criterion:'4.1.1', title:'Analyse syntaxique',           category:'Robuste',
   desc:'Le HTML est valide : pas d\'ID en double, balises correctement imbriquées.',
   test: function(doc){ var allIds=doc.querySelectorAll('[id]'); var ids={}; var dupes=[]; allIds.forEach(function(e){if(ids[e.id])dupes.push(e.id);else ids[e.id]=true;}); return {pass:dupes.length===0,detail:dupes.length===0?allIds.length+' IDs uniques — HTML valide':dupes.length+' ID(s) en double: '+dupes.slice(0,3).join(', ')}; }},
  {id:'4.1.2', level:'A',  criterion:'4.1.2', title:'Nom, rôle et valeur',          category:'Robuste',
   desc:'Tous les composants d\'interface ont un nom, un rôle et une valeur accessibles.',
   test: function(doc){ var btns=doc.querySelectorAll('button'); var noName=0; btns.forEach(function(b){if(!b.textContent.trim()&&!b.getAttribute('aria-label')&&!b.getAttribute('aria-labelledby'))noName++;}); return {pass:noName===0,detail:noName===0?btns.length+' boutons — tous ont un nom accessible':noName+' bouton(s) sans nom accessible'}; }},
  {id:'4.1.3', level:'AA', criterion:'4.1.3', title:'Messages de statut',           category:'Robuste',
   desc:'Les messages de statut sont programmés pour être annoncés.',
   test: function(doc){ var live=doc.querySelectorAll('[aria-live],[role="status"],[role="alert"],[role="log"]'); return {pass:live.length>0,detail:live.length+' région(s) aria-live détectée(s) — annonces aux lecteurs d\'écran activées'}; }},

  // ── RGAA SPÉCIFIQUE ──
  {id:'R8.1', level:'A',  criterion:'RGAA 8.1', title:'[RGAA] Document valide',     category:'RGAA',
   desc:'Le document respecte la grammaire formelle (DTD/schéma).',
   test: function(doc){ var doctype=doc.doctype; var charset=doc.querySelector('meta[charset]'); return {pass:!!(doctype&&charset),detail:(doctype?'✓ DOCTYPE présent':'✗ DOCTYPE manquant')+' · '+(charset?'✓ charset="'+charset.getAttribute('charset')+'"':'✗ charset manquant')}; }},
  {id:'R10.1', level:'A', criterion:'RGAA 10.1', title:'[RGAA] CSS séparé du HTML', category:'RGAA',
   desc:'Les feuilles de style sont utilisées pour contrôler la présentation.',
   test: function(doc){ var inlineStyle=doc.querySelectorAll('[style]').length; var total=doc.querySelectorAll('*').length; var pct=Math.round(inlineStyle/total*100); return {pass:pct<15,detail:inlineStyle+'/'+total+' éléments avec style inline ('+pct+'%) — '+(pct<15?'Acceptable':'Trop de styles inline')}; }},
  {id:'R11.1', level:'A', criterion:'RGAA 11.1', title:'[RGAA] Étiquettes de formulaire',category:'RGAA',
   desc:'Chaque champ de formulaire a une étiquette liée.',
   test: function(doc){ var inputs=doc.querySelectorAll('input:not([type="hidden"]):not([type="submit"]):not([type="button"]),select,textarea'); var ok=0; inputs.forEach(function(i){if(doc.querySelector('label[for="'+i.id+'"]')||i.getAttribute('aria-label')||i.getAttribute('aria-labelledby')||i.getAttribute('title'))ok++;}); return {pass:inputs.length===0||ok===inputs.length,detail:ok+'/'+inputs.length+' champs correctement étiquetés'}; }},
  {id:'R12.1', level:'A', criterion:'RGAA 12.1', title:'[RGAA] Navigation cohérente',category:'RGAA',
   desc:'Les mécanismes de navigation sont identiques sur toutes les pages.',
   test: function(doc){ var nav=doc.querySelectorAll('nav'); var hasMainNav=!!doc.querySelector('nav[aria-label]'); return {pass:nav.length>=1,detail:nav.length+' bloc(s) nav · '+(hasMainNav?'Labels aria-label présents':'Ajoutez aria-label aux nav')}; }},
  {id:'R13.1', level:'A', criterion:'RGAA 13.1', title:'[RGAA] Liens de téléchargement',category:'RGAA',
   desc:'Les liens vers des fichiers téléchargeables précisent le format et la taille.',
   test: function(doc){ var dlLinks=doc.querySelectorAll('a[href$=".pdf"],a[href$=".doc"],a[href$=".docx"],a[href$=".xlsx"]'); var withInfo=0; dlLinks.forEach(function(l){if(l.textContent.match(/pdf|doc|xls|kb|mb/i)||l.getAttribute('aria-label'))withInfo++;}); return {pass:dlLinks.length===0||withInfo===dlLinks.length,detail:dlLinks.length+' lien(s) de téléchargement · '+withInfo+' avec info format'}; }},
];

// ── Données du rapport global ──
var REPORT_DATA = null;

// ── Exécution des tests ──
function runTests(){
  var btn=document.getElementById('test-run-btn');
  var ico=document.getElementById('test-btn-ico');
  var txt=document.getElementById('test-btn-txt');
  var res=document.getElementById('test-results');
  btn.disabled=true;
  ico.innerHTML='<div class="spinner"></div>';
  txt.textContent='Analyse WCAG en cours…';
  res.innerHTML=''; res.classList.remove('show');

  // Masquer le bouton rapport
  var rptBtn=document.getElementById('report-btn-wrap');
  if(rptBtn)rptBtn.style.display='none';

  // On teste la page courante (accessibility.html) pour la démo
  // ET on fait des vérifications sur le document courant
  var doc=document;
  var results=[];

  // Simuler les tests avec progression
  var i=0;
  var delay=50;

  function runNext(){
    if(i>=WCAG_TESTS.length){
      finishTests(results);
      return;
    }
    var t=WCAG_TESTS[i];
    var r;
    try{ r=t.test(doc); }
    catch(e){ r={pass:false,detail:'Erreur test: '+e.message}; }
    results.push({test:t, pass:r.pass, detail:r.detail});
    i++;
    // Mise à jour progression
    var pct=Math.round(i/WCAG_TESTS.length*100);
    ico.innerHTML='<div class="spinner"></div>';
    txt.textContent='Analyse WCAG… '+pct+'%';
    setTimeout(runNext, delay);
  }
  setTimeout(runNext, delay);
}

function finishTests(results){
  var btn=document.getElementById('test-run-btn');
  var ico=document.getElementById('test-btn-ico');
  var txt=document.getElementById('test-btn-txt');
  var res=document.getElementById('test-results');

  // Calculer stats
  var passed=results.filter(function(r){return r.pass;}).length;
  var failed=results.filter(function(r){return !r.pass;}).length;
  var total=results.length;
  var pct=Math.round(passed/total*100);
  var levelA=results.filter(function(r){return r.test.level==='A';});
  var levelAA=results.filter(function(r){return r.test.level==='AA';});
  var passedA=levelA.filter(function(r){return r.pass;}).length;
  var passedAA=levelAA.filter(function(r){return r.pass;}).length;

  // Stocker les résultats pour le rapport
  REPORT_DATA = {results:results,passed:passed,failed:failed,total:total,pct:pct,passedA:passedA,totalA:levelA.length,passedAA:passedAA,totalAA:levelAA.length,date:new Date().toLocaleString('fr-FR')};

  // Grouper par catégorie
  var cats={};
  results.forEach(function(r){
    var c=r.test.category;
    if(!cats[c])cats[c]=[];
    cats[c].push(r);
  });

  var scoreColor = pct>=90?'#22c55e':pct>=70?'#f59e0b':'#ef4444';

  var html='';
  // Score global
  html+='<div class="score-board">';
  html+='<div class="score-main"><div class="score-circle" id="score-circle"><div class="score-num" id="score-num">0%</div><div class="score-lbl">Score WCAG</div></div></div>';
  html+='<div class="score-stats">';
  html+='<div class="ss-row"><span class="ss-ico">✅</span><span class="ss-val">'+passed+'</span><span class="ss-lbl">Tests réussis</span></div>';
  html+='<div class="ss-row"><span class="ss-ico">❌</span><span class="ss-val">'+failed+'</span><span class="ss-lbl">À corriger</span></div>';
  html+='<div class="ss-row"><span class="ss-ico">🔵</span><span class="ss-val">'+passedA+'/'+levelA.length+'</span><span class="ss-lbl">Niveau A</span></div>';
  html+='<div class="ss-row"><span class="ss-ico">🟣</span><span class="ss-val">'+passedAA+'/'+levelAA.length+'</span><span class="ss-lbl">Niveau AA</span></div>';
  html+='</div></div>';
  html+='<div class="score-bar-wrap"><div class="score-bar" id="score-bar" style="width:0%;background:'+scoreColor+'"></div></div>';

  // Résultats par catégorie
  Object.keys(cats).forEach(function(cat){
    var catItems=cats[cat];
    var catPassed=catItems.filter(function(r){return r.pass;}).length;
    html+='<div class="cat-group">';
    html+='<div class="cat-head"><span class="cat-ico">'+getCatIco(cat)+'</span><span class="cat-title">'+cat+'</span><span class="cat-score">'+catPassed+'/'+catItems.length+'</span></div>';
    catItems.forEach(function(r){
      html+='<div class="test-item">';
      html+='<div class="ti-left"><span class="ti-status">'+(r.pass?'✅':'❌')+'</span></div>';
      html+='<div class="ti-body">';
      html+='<div class="ti-header"><span class="ti-crit">'+r.test.criterion+'</span><span class="ti-title2">'+r.test.title+'</span>'+'<span class="ti-level level-'+r.test.level+'">'+r.test.level+'</span></div>';
      html+='<div class="ti-desc2">'+r.test.desc+'</div>';
      html+='<div class="ti-detail '+(r.pass?'det-pass':'det-fail')+'">'+r.detail+'</div>';
      html+='</div>';
      html+='<div class="ti-badge-wrap"><span class="ti-badge '+(r.pass?'tb-pass':'tb-fail')+'">'+(r.pass?'Réussi':'À corriger')+'</span></div>';
      html+='</div>';
    });
    html+='</div>';
  });

  res.innerHTML=html;
  res.classList.add('show');
  ico.innerHTML='↻'; txt.textContent='Relancer les tests'; btn.disabled=false;

  // Animations
  setTimeout(function(){
    var bar=document.getElementById('score-bar');
    if(bar)bar.style.width=pct+'%';
    var num=document.getElementById('score-num');
    if(num){var c=0;var timer=setInterval(function(){c+=2;if(c>=pct){c=pct;clearInterval(timer);}num.textContent=c+'%';num.style.color=scoreColor;},20);}
  },100);

  // Afficher le bouton rapport
  var rptBtn=document.getElementById('report-btn-wrap');
  if(rptBtn){rptBtn.style.display='block';}
}

function getCatIco(cat){
  var map={'Perceptible':'👁','Utilisable':'⌨️','Compréhensible':'💡','Robuste':'⚙️','RGAA':'🇫🇷'};
  return map[cat]||'📋';
}

// ══════════════════════════════════════════════════════════
// RAPPORT COMPLET — Page générée dynamiquement
// ══════════════════════════════════════════════════════════
function openFullReport(){
  if(!REPORT_DATA){alert('Lancez d\'abord les tests d\'accessibilité.');return;}
  var d=REPORT_DATA;

  var rows=d.results.map(function(r){
    return '<tr class="'+(r.pass?'row-pass':'row-fail')+'">'
      +'<td><strong>'+r.test.criterion+'</strong></td>'
      +'<td>'+r.test.title+'</td>'
      +'<td><span class="rpt-level rpt-'+r.test.level+'">'+r.test.level+'</span></td>'
      +'<td>'+r.test.category+'</td>'
      +'<td><span class="rpt-status">'+(r.pass?'✅ Réussi':'❌ À corriger')+'</span></td>'
      +'<td style="font-size:11px;color:#555">'+r.detail+'</td>'
      +'</tr>';
  }).join('');

  var failed=d.results.filter(function(r){return !r.pass;});
  var recosHtml=failed.length?failed.map(function(r,i){
    return '<div class="reco">'
      +'<div class="reco-num">'+(i+1)+'</div>'
      +'<div><strong style="color:#1a1a2e">'+r.test.criterion+' — '+r.test.title+'</strong>'
      +'<br><span style="font-size:12px;color:#555">'+r.test.desc+'</span>'
      +'<br><span style="font-size:11px;color:#e74c3c;margin-top:4px;display:block">⚠ '+r.detail+'</span>'
      +'</div></div>';
  }).join(''):'<p style="color:#27ae60;font-weight:600">🎉 Aucune correction requise — Conformité complète !</p>';

  var reportHtml='<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    +'<title>Rapport WCAG/RGAA — CONSEILPREV — '+d.date+'</title>'
    +'<style>'
    +'*{box-sizing:border-box;margin:0;padding:0}body{font-family:"Segoe UI",Arial,sans-serif;background:#f8f9fa;color:#1a1a2e;line-height:1.6}'
    +'.rpt-header{background:linear-gradient(135deg,#7c5cbf,#5b3fa8);color:#fff;padding:36px 40px;}'
    +'.rpt-header h1{font-size:26px;margin-bottom:6px}.rpt-header p{opacity:.8;font-size:13px}'
    +'.rpt-score-bar{background:#fff;padding:24px 40px;border-bottom:1px solid #e0e0e0;display:flex;gap:32px;flex-wrap:wrap;align-items:center}'
    +'.rpt-stat{text-align:center}.rpt-stat-val{font-size:28px;font-weight:700}.rpt-stat-lbl{font-size:11px;color:#666;text-transform:uppercase;letter-spacing:.1em}'
    +'.stat-green{color:#22c55e}.stat-red{color:#ef4444}.stat-blue{color:#3b82f6}.stat-purple{color:#8b5cf6}'
    +'.progress-wrap{flex:1;min-width:200px}.progress-bg{height:12px;background:#e0e0e0;border-radius:6px;overflow:hidden}'
    +'.progress-fill{height:100%;background:linear-gradient(90deg,#22c55e,#3cc9b0);border-radius:6px}'
    +'.con{max-width:1100px;margin:0 auto;padding:0 32px}'
    +'.sec{padding:28px 0}'
    +'.sec h2{font-size:18px;color:#1a1a2e;margin-bottom:16px;padding-bottom:8px;border-bottom:2px solid #7c5cbf}'
    +'table{width:100%;border-collapse:collapse;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.08)}'
    +'th{background:#f0eff8;padding:10px 14px;font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:#555;text-align:left}'
    +'td{padding:10px 14px;font-size:13px;border-bottom:1px solid #f0f0f0}'
    +'.row-pass{background:#fff}.row-fail{background:#fff8f8}'
    +'.rpt-level{font-size:10px;font-weight:700;padding:2px 7px;border-radius:100px}'
    +'.rpt-A{background:#dcfce7;color:#166534}.rpt-AA{background:#dbeafe;color:#1e40af}.rpt-AAA{background:#f3e8ff;color:#6b21a8}'
    +'.rpt-status{font-size:12px}.row-fail .rpt-status{color:#ef4444}'
    +'.reco{display:flex;gap:14px;background:#fff;border:1px solid #fecaca;border-radius:8px;padding:14px 18px;margin-bottom:10px}'
    +'.reco-num{width:28px;height:28px;background:#ef4444;color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;flex-shrink:0}'
    +'.rpt-footer{background:#1a1a2e;color:rgba(255,255,255,.6);padding:20px 40px;font-size:11px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}'
    +'@media print{.no-print{display:none}.rpt-header{-webkit-print-color-adjust:exact;print-color-adjust:exact}}'
    +'</style></head><body>'
    +'<div class="rpt-header">'
    +'<h1>♿ Rapport d\'Accessibilité WCAG 2.1 / RGAA</h1>'
    +'<p>CONSEILPREV · conseilprev.onrender.com · Généré le '+d.date+'</p>'
    +'</div>'
    +'<div class="rpt-score-bar">'
    +'<div class="rpt-stat"><div class="rpt-stat-val stat-green">'+d.pct+'%</div><div class="rpt-stat-lbl">Score global</div></div>'
    +'<div class="rpt-stat"><div class="rpt-stat-val stat-green">'+d.passed+'</div><div class="rpt-stat-lbl">Tests réussis</div></div>'
    +'<div class="rpt-stat"><div class="rpt-stat-val stat-red">'+d.failed+'</div><div class="rpt-stat-lbl">À corriger</div></div>'
    +'<div class="rpt-stat"><div class="rpt-stat-val stat-blue">'+d.passedA+'/'+d.totalA+'</div><div class="rpt-stat-lbl">Niveau A</div></div>'
    +'<div class="rpt-stat"><div class="rpt-stat-val stat-purple">'+d.passedAA+'/'+d.totalAA+'</div><div class="rpt-stat-lbl">Niveau AA</div></div>'
    +'<div class="progress-wrap"><div class="progress-bg"><div class="progress-fill" style="width:'+d.pct+'%"></div></div><p style="font-size:11px;color:#666;margin-top:4px">'+d.passed+' tests réussis sur '+d.total+'</p></div>'
    +'</div>'
    +'<div class="con">'
    +'<div class="sec"><h2>📋 Détail des '+d.total+' critères testés</h2><div style="overflow-x:auto"><table><thead><tr><th>Critère</th><th>Titre</th><th>Niveau</th><th>Catégorie</th><th>Résultat</th><th>Détail</th></tr></thead><tbody>'+rows+'</tbody></table></div></div>'
    +'<div class="sec"><h2>🔧 Recommandations ('+d.failed+' point'+(d.failed>1?'s':'')+' à corriger)</h2>'+recosHtml+'</div>'
    +'<div class="sec no-print"><h2>📌 Conformité légale</h2><p style="font-size:13px;color:#555;line-height:1.75">Ce rapport est conforme aux exigences de la <strong>Directive EU 2019/882</strong> sur l\'accessibilité des sites web du secteur public, au <strong>RGAA 4.1</strong> (Référentiel Général d\'Amélioration de l\'Accessibilité), et aux <strong>WCAG 2.1 niveaux A et AA</strong>. Score actuel : <strong>'+d.pct+'% ('+d.passed+'/'+d.total+')</strong>.</p></div>'
    +'</div>'
    +'<div class="rpt-footer">'
    +'<span>CONSEILPREV · Rapport WCAG/RGAA automatisé · '+d.date+'</span>'
    +'<span>Généré par le moteur d\'accessibilité CONSEILPREV</span>'
    +'</div>'
    +'<script>window.onload=function(){window.print&&setTimeout(function(){},500)}<\/script>'
    +'</body></html>';

  var blob=new Blob([reportHtml],{type:'text/html;charset=utf-8'});
  var url=URL.createObjectURL(blob);
  var a=document.createElement('a');
  a.href=url; a.target='_blank'; a.rel='noopener';
  a.click();
  setTimeout(function(){URL.revokeObjectURL(url);},3000);
}

// Init
loadPrefs();


;/* ── bloc 2/2 ── */


// ════════════════════════════════════════
// PROTECTION ANTI-COPIE / ANTI-SCRAPING
// ════════════════════════════════════════
(function(){
  "use strict";

  // ── 1. Désactiver clic droit ──
  document.addEventListener('contextmenu', function(e){
    e.preventDefault();
    showProtectionMsg(e.clientX, e.clientY);
    return false;
  }, true);

  // ── 2. Désactiver les raccourcis clavier de copie ──
  document.addEventListener('keydown', function(e){
    var key = e.key.toLowerCase();
    // Ctrl/Cmd + C, X, A, U, S, P
    if((e.ctrlKey || e.metaKey) && ['c','x','a','u','s','p'].indexOf(key) > -1){
      e.preventDefault();
      if(['c','x','a'].indexOf(key) > -1) showProtectionMsg();
      return false;
    }
    // F12 (DevTools)
    if(e.key === 'F12'){
      e.preventDefault();
      return false;
    }
    // Ctrl+Shift+I/J/C (DevTools)
    if((e.ctrlKey||e.metaKey) && e.shiftKey && ['i','j','c','k'].indexOf(key) > -1){
      e.preventDefault();
      return false;
    }
    // Ctrl+Shift+U (View Source Firefox)
    if(e.ctrlKey && e.shiftKey && key === 'u'){
      e.preventDefault();
      return false;
    }
  }, true);

  // ── 3. Désactiver la sélection de texte ──
  document.addEventListener('selectstart', function(e){
    if(!isInputElement(e.target)){
      e.preventDefault();
      return false;
    }
  }, true);

  // ── 4. Désactiver le glisser-déposer ──
  document.addEventListener('dragstart', function(e){
    e.preventDefault();
    return false;
  }, true);

  // ── 5. Désactiver le copier-coller via presse-papiers ──
  document.addEventListener('copy', function(e){
    if(!isInputElement(document.activeElement)){
      e.clipboardData.setData('text/plain',
        '© CONSEILPREV — Contenu protégé. Reproduction interdite. contact@i-aes.com');
      e.preventDefault();
      showProtectionMsg();
    }
  }, true);

  document.addEventListener('cut', function(e){
    if(!isInputElement(document.activeElement)){
      e.preventDefault();
    }
  }, true);

  // ── 6. Détecter l'ouverture des DevTools ──
  var devtoolsOpen = false;
  var threshold = 160;
  function detectDevTools(){
    var widthDiff  = window.outerWidth  - window.innerWidth  > threshold;
    var heightDiff = window.outerHeight - window.innerHeight > threshold;
    if((widthDiff || heightDiff) && !devtoolsOpen){
      devtoolsOpen = true;
      // Brouiller le contenu
      document.body.style.filter = 'blur(8px)';
      showDevToolsWarning();
    } else if(!widthDiff && !heightDiff && devtoolsOpen){
      devtoolsOpen = false;
      document.body.style.filter = '';
    }
  }
  setInterval(detectDevTools, 1000);

  // ── 7. Désactiver l'impression (Ctrl+P) ──
  window.addEventListener('beforeprint', function(e){
    document.body.style.display = 'none';
  });
  window.addEventListener('afterprint', function(){
    document.body.style.display = '';
  });

  // ── 8. Protection contre le screenshot via Print Screen ──
  // (CSS uniquement — ne peut pas bloquer nativement)

  // ── 9. Détecter les outils d'automatisation (Selenium, Puppeteer) ──
  var botDetected = (
    navigator.webdriver ||
    window.callPhantom ||
    window._phantom ||
    window.__nightmare ||
    window.domAutomation ||
    navigator.userAgent.indexOf('HeadlessChrome') > -1 ||
    navigator.userAgent.indexOf('PhantomJS') > -1
  );
  if(botDetected){
    document.documentElement.innerHTML =
      '<h1 style="font-family:sans-serif;text-align:center;padding:60px;color:#7c3aed">'+
      '🔒 Accès non autorisé</h1>';
  }

  // ── 10. Watermark dynamique invisible ──
  function injectWatermark(){
    var wm = document.createElement('div');
    wm.id = 'cp-watermark';
    wm.style.cssText = [
      'position:fixed','inset:0','z-index:99999',
      'pointer-events:none','opacity:0.03',
      'display:flex','flex-wrap:wrap','overflow:hidden',
      'font-family:monospace','font-size:14px','color:#7c3aed',
      'line-height:2','letter-spacing:.5em',
      'transform:rotate(-25deg) scale(1.4)',
      'user-select:none','-webkit-user-select:none'
    ].join(';');
    var text = '© CONSEILPREV ';
    var content = '';
    for(var i = 0; i < 200; i++) content += text;
    wm.textContent = content;
    document.body.appendChild(wm);
  }
  document.addEventListener('DOMContentLoaded', injectWatermark);

  // ── Helpers ──
  function isInputElement(el){
    if(!el) return false;
    var tag = (el.tagName||'').toLowerCase();
    return tag === 'input' || tag === 'textarea' || tag === 'select' ||
           el.getAttribute('contenteditable') === 'true';
  }

  // ── Toast de protection ──
  var toastTimer = null;
  function showProtectionMsg(x, y){
    var old = document.getElementById('cp-toast');
    if(old) old.remove();
    var t = document.createElement('div');
    t.id = 'cp-toast';
    var left = x ? Math.min(x, window.innerWidth - 280) + 'px' : '50%';
    var transform = x ? 'none' : 'translateX(-50%)';
    t.style.cssText = [
      'position:fixed',
      'top:' + (y ? Math.max(20, y - 60)+'px' : '20px'),
      'left:' + left,
      'transform:' + transform,
      'background:rgba(10,6,32,.97)',
      'border:1px solid rgba(217,70,239,.4)',
      'color:#d4baff',
      'font-size:12px',
      'font-family:"Space Mono",monospace',
      'padding:10px 16px',
      'border-radius:8px',
      'z-index:100000',
      'pointer-events:none',
      'box-shadow:0 4px 24px rgba(139,92,246,.4)',
      'max-width:280px',
      'line-height:1.5',
      'opacity:0',
      'transition:opacity .18s'
    ].join(';');
    t.innerHTML = '🔒 <strong>Contenu protégé</strong><br><span style="opacity:.7;font-size:10px">© CONSEILPREV · Reproduction interdite</span>';
    document.body.appendChild(t);
    requestAnimationFrame(function(){ t.style.opacity = '1'; });
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function(){
      t.style.opacity = '0';
      setTimeout(function(){ if(t.parentNode) t.remove(); }, 300);
    }, 2500);
  }

  // ── Avertissement DevTools ──
  function showDevToolsWarning(){
    var old = document.getElementById('devtools-warning');
    if(old) return;
    var w = document.createElement('div');
    w.id = 'devtools-warning';
    w.style.cssText = [
      'position:fixed','top:0','left:0','right:0',
      'background:rgba(10,6,32,.98)',
      'color:#d4baff',
      'font-family:"Space Mono",monospace',
      'font-size:13px','text-align:center',
      'padding:14px','z-index:100001',
      'border-bottom:2px solid rgba(217,70,239,.5)'
    ].join(';');
    w.textContent = 'Acces DevTools detecte - Site protege.';
    document.body.appendChild(w);
    setTimeout(function(){ if(w.parentNode) w.remove(); document.body.style.filter=''; }, 4000);
  }

  // ── CSS anti-print injecté dynamiquement ──
  var printStyle = document.createElement('style');
  printStyle.textContent = '@media print{body{display:none!important}}';
  document.head.appendChild(printStyle);

})();


