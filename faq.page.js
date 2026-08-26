/* Extrait de faq.html — 3 bloc(s) en ligne, dans leur ordre d'origine.
   Le HTML est servi en no-store : ce fichier, lui, obtient un ETag
   et répond 304 dès la deuxième visite. */

;/* ── bloc 1/3 ── */

function faqToggle(id){
  var item=document.getElementById(id);
  var btn=item.querySelector('.faq-q');
  var ans=item.querySelector('.faq-a');
  var isOpen=item.classList.contains('open');
  // Fermer tous les autres dans la même section
  var siblings=item.closest('.faq-list').querySelectorAll('.faq-item.open');
  siblings.forEach(function(s){
    if(s!==item){
      s.classList.remove('open');
      s.querySelector('.faq-q').setAttribute('aria-expanded','false');
    }
  });
  item.classList.toggle('open',!isOpen);
  btn.setAttribute('aria-expanded',!isOpen?'true':'false');
}
// Ouvrir si ancre dans l'URL
window.addEventListener('load',function(){
  var hash=window.location.hash.slice(1);
  if(hash){var el=document.getElementById(hash);if(el&&el.classList.contains('faq-item'))faqToggle(hash);}
});
// Recherche rapide
document.addEventListener('keydown',function(e){
  if((e.ctrlKey||e.metaKey)&&e.key==='f'){
    e.preventDefault();
    var q=prompt('Rechercher dans la FAQ :');
    if(q){
      var items=document.querySelectorAll('.faq-item');
      var found=0;
      items.forEach(function(item){
        var txt=item.textContent.toLowerCase();
        if(txt.indexOf(q.toLowerCase())>-1){
          item.style.border='1px solid rgba(217,70,239,.6)';
          if(found===0)item.scrollIntoView({behavior:'smooth',block:'center'});
          found++;
        }else{item.style.border='';}
      });
      if(!found)alert('Aucun résultat pour "'+q+'"');
    }
  }
});


;/* ── bloc 2/3 ── */

(function(){
  var SIDS=["section-0", "section-1", "section-2", "section-3", "section-4"];
  var SLBL={
  "section-0":"⚖️ AI Act",
  "section-1":"🔒 RGPD",
  "section-2":"🏭 Cas d'usage",
  "section-3":"⚖️ Comparaisons",
  "section-4":"🛠️ Guides"
};
  var cur=0,scrolling=false;
  function initDots(){var c=document.getElementById('nav-section-dots');if(!c)return;SIDS.forEach(function(id,i){var d=document.createElement('div');d.className='nav-dot'+(i===0?' active':'');d.title=SLBL[id]||id;d.onclick=function(){go(i);};c.appendChild(d);});}
  function go(idx){if(idx<0)idx=0;if(idx>=SIDS.length)idx=SIDS.length-1;var el=document.getElementById(SIDS[idx]);if(!el)return;scrolling=true;var nh=document.querySelector('nav')?document.querySelector('nav').offsetHeight:70;window.scrollTo({top:el.getBoundingClientRect().top+window.scrollY-nh-8,behavior:'smooth'});cur=idx;upd();showLbl(SIDS[idx]);setTimeout(function(){scrolling=false;},800);}
  window.navSection=function(d){go(cur+d);};
  window.goToSection=go;
  function upd(){var u=document.getElementById('nav-up');var d=document.getElementById('nav-down');if(u)u.disabled=(cur===0);if(d)d.disabled=(cur===SIDS.length-1);document.querySelectorAll('.nav-dot').forEach(function(dot,i){dot.classList.toggle('active',i===cur);});}
  var lt=null;
  function showLbl(id){var l=document.getElementById('nav-section-label');if(!l)return;l.textContent=SLBL[id]||id;l.classList.add('show');clearTimeout(lt);lt=setTimeout(function(){l.classList.remove('show');},2000);var a=document.getElementById('nav-arrows');if(a)l.style.top=(a.getBoundingClientRect().top+window.scrollY+40)+'px';}
  window.addEventListener('scroll',function(){
    var p=document.getElementById('read-progress');if(p){var s=window.scrollY,t=document.body.scrollHeight-window.innerHeight;p.style.width=(t>0?Math.round(s/t*100):0)+'%';}
    var nh=document.querySelector('nav')?document.querySelector('nav').offsetHeight:70;var mid=window.scrollY+nh+(window.innerHeight-nh)/3;var f=0;SIDS.forEach(function(id,i){var el=document.getElementById(id);if(el){var top=el.getBoundingClientRect().top+window.scrollY;if(top<=mid)f=i;}});if(f!==cur&&!scrolling){cur=f;upd();}
    var ar=document.getElementById('nav-arrows');if(ar)ar.classList.toggle('visible',window.scrollY>150);
  },{passive:true});
  document.addEventListener('keydown',function(e){if(e.target.tagName==='INPUT'||e.target.tagName==='TEXTAREA')return;if(e.altKey&&e.key==='ArrowUp'){e.preventDefault();navSection(-1);}if(e.altKey&&e.key==='ArrowDown'){e.preventDefault();navSection(1);}});
  document.addEventListener('DOMContentLoaded',function(){initDots();upd();});
})();


;/* ── bloc 3/3 ── */


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


