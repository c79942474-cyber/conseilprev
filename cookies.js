/* ══════════════════════════════════════════════════════════════════
   CONSEILPREV — Bandeau cookies mutualisé (conforme CNIL / art. 82)
   Autonome : s'auto-injecte sur toute page qui le charge.
   Ne fait rien si un bandeau (#ck-banner) existe déjà (ex. page d'accueil).
   Consentement partagé via la clé 'conseilprev_cookies' (13 mois).
   ══════════════════════════════════════════════════════════════════ */
(function(){
  if(window.__ckSharedLoaded) return;
  window.__ckSharedLoaded = true;
  if(document.getElementById('ck-banner')) return; // bandeau déjà présent sur la page

  var CK_KEY = 'conseilprev_cookies';
  var CK_TTL = 1000*60*60*24*30*13; // 13 mois

  function ckLoad(){
    try{ var raw=localStorage.getItem(CK_KEY); if(!raw) return null;
         var d=JSON.parse(raw); if(Date.now()-d.ts>CK_TTL){ localStorage.removeItem(CK_KEY); return null; } return d;
    }catch(e){ return null; }
  }
  function ckSave(p){
    var d={ necessary:true, functional:!!p.functional, analytics:!!p.analytics, marketing:!!p.marketing,
            ts:Date.now(), date:new Date().toLocaleString('fr-FR'), version:'1.0' };
    try{ localStorage.setItem(CK_KEY, JSON.stringify(d)); }catch(e){}
    /* LA PREUVE PART AU SERVEUR (art. 7). Le choix rangé dans localStorage
       n'est une preuve pour personne : il vit dans le navigateur du visiteur,
       et la charge de la preuve du consentement pèse sur le responsable de
       traitement — pas sur le visiteur. Seule la page d'accueil déposait
       cette preuve ; les autres pages recueillaient sans pouvoir prouver.
       Le refus est enregistré au même titre que l'acceptation : prouver
       qu'on a respecté un refus est exactement aussi nécessaire. */
    try{
      var toutRefuse = !d.functional && !d.analytics && !d.marketing;
      fetch('/api/rgpd/consentement', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({
          finalites: { fonctionnel:d.functional, analytique:d.analytics, marketing:d.marketing },
          methode: 'banniere-partagee:' + (location.pathname || '/'),
          retrait: toutRefuse
        })
      }).catch(function(){});
    }catch(e){}
    return d;
  }
  function ckApply(p){
    // Aucun traceur tiers actif. Points d'ancrage pour l'avenir :
    if(typeof window.gtag === 'function'){
      try{ window.gtag('consent','update',{ analytics_storage: p.analytics?'granted':'denied',
            ad_storage: p.marketing?'granted':'denied' }); }catch(e){}
    }
  }

  // ── Styles autonomes ──
  var css =
  '#ck-banner{position:fixed;left:16px;right:16px;bottom:16px;z-index:99999;background:#161616;color:#f2f2f2;'
  +'border:1px solid #2a2a2a;border-radius:14px;box-shadow:0 12px 40px rgba(0,0,0,.45);padding:18px 20px;'
  +'display:none;gap:18px;align-items:center;flex-wrap:wrap;font-family:Inter,system-ui,Arial,sans-serif;max-width:1100px;margin:0 auto}'
  +'#ck-banner.show{display:flex;animation:ckup .35s ease}'
  +'@keyframes ckup{from{transform:translateY(20px);opacity:0}to{transform:none;opacity:1}}'
  +'.ckb-left{flex:1;min-width:260px}'
  +'.ckb-title{font-weight:700;font-size:15px;margin-bottom:5px}'
  +'.ckb-txt{font-size:12px;line-height:1.55;color:#c9c9c9}'
  +'.ckb-txt a{color:#E0A800;text-decoration:underline}'
  +'.ckb-btns{display:flex;gap:8px;flex-wrap:wrap}'
  +'.ckb-btn{border:0;border-radius:8px;padding:10px 16px;font-size:13px;font-weight:600;cursor:pointer;font-family:inherit}'
  +'.ckb-config{background:transparent;color:#f2f2f2;border:1px solid #444}'
  +'.ckb-refuse{background:#333;color:#fff}'
  +'.ckb-all{background:#E0A800;color:#161616}'
  +'#ck-reopen{position:fixed;left:16px;bottom:16px;z-index:99998;display:none;align-items:center;gap:6px;'
  +'background:#161616;color:#E0A800;border:1px solid #2a2a2a;border-radius:30px;padding:9px 14px;font-size:12px;'
  +'font-weight:600;cursor:pointer;font-family:Inter,system-ui,Arial,sans-serif;box-shadow:0 6px 20px rgba(0,0,0,.3)}'
  +'#ck-modal{position:fixed;inset:0;z-index:100000;background:rgba(0,0,0,.6);display:none;align-items:center;'
  +'justify-content:center;padding:20px;font-family:Inter,system-ui,Arial,sans-serif}'
  +'#ck-modal.open{display:flex}'
  +'.ckm-card{background:#fff;color:#1c1c1c;border-radius:14px;max-width:560px;width:100%;max-height:85vh;overflow:auto;padding:22px 24px}'
  +'.ckm-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}'
  +'.ckm-head h3{margin:0;font-size:17px}'
  +'.ckm-close{background:none;border:0;font-size:22px;cursor:pointer;color:#888}'
  +'.ckm-intro{font-size:12.5px;color:#555;line-height:1.55;margin-bottom:16px}'
  +'.ckm-intro a{color:#8a6d00;text-decoration:underline}'
  +'.ckm-cat{border:1px solid #e6e6e6;border-radius:10px;padding:12px 14px;margin-bottom:10px}'
  +'.ckm-cat-h{display:flex;justify-content:space-between;align-items:center;gap:10px}'
  +'.ckm-cat-t{font-weight:700;font-size:13px}'
  +'.ckm-cat-d{font-size:11.5px;color:#666;line-height:1.5;margin-top:5px}'
  +'.ckm-actions{display:flex;justify-content:flex-end;gap:8px;margin-top:14px}'
  +'.ckm-sw{position:relative;width:42px;height:22px;flex:0 0 auto}'
  +'.ckm-sw input{opacity:0;width:0;height:0}'
  +'.ckm-sl{position:absolute;inset:0;background:#ccc;border-radius:22px;transition:.2s;cursor:pointer}'
  +'.ckm-sl:before{content:"";position:absolute;height:16px;width:16px;left:3px;top:3px;background:#fff;border-radius:50%;transition:.2s}'
  +'.ckm-sw input:checked + .ckm-sl{background:#E0A800}'
  +'.ckm-sw input:checked + .ckm-sl:before{transform:translateX(20px)}'
  +'.ckm-sw input:disabled + .ckm-sl{background:#8a8a8a;cursor:not-allowed}';
  var st=document.createElement('style'); st.textContent=css; document.head.appendChild(st);

  // ── HTML ──
  var html =
  '<div id="ck-banner" role="dialog" aria-modal="true" aria-label="Gestion des cookies" aria-live="polite">'
  +'<div class="ckb-left"><div class="ckb-title">\ud83c\udf6a Ce site utilise des cookies</div>'
  +'<div class="ckb-txt">Nous utilisons des cookies \u00e0 des finalit\u00e9s de mesure d\'audience, de personnalisation du contenu et d\'am\u00e9lioration de votre exp\u00e9rience, conform\u00e9ment au '
  +'<a href="https://www.cnil.fr/fr/cookies-et-autres-traceurs" target="_blank" rel="noopener">RGPD</a> et \u00e0 la recommandation '
  +'<a href="https://www.cnil.fr/fr/cookies-et-autres-traceurs/regles/cookies-solutions-pour-les-outils-de-mesure-daudience" target="_blank" rel="noopener">CNIL</a>. '
  +'Responsable de traitement\u00a0: CONSEILPREV SARL, 19 rue Auguste Chabri\u00e8res, 75015 Paris. Vous pouvez accepter, refuser ou param\u00e9trer les cookies, et modifier ou retirer votre consentement \u00e0 tout moment. '
  +'<a href="confidentialite.html">En savoir plus</a>.</div></div>'
  +'<div class="ckb-btns">'
  +'<button class="ckb-btn ckb-config" onclick="ckOpenModal()">\u2699 Param\u00e9trer</button>'
  +'<button class="ckb-btn ckb-refuse" onclick="ckRefuseAll()">Refuser</button>'
  +'<button class="ckb-btn ckb-all" onclick="ckAcceptAll()">Tout accepter</button>'
  +'</div></div>'
  +'<button id="ck-reopen" onclick="ckOpenModal()" aria-label="Rouvrir les pr\u00e9f\u00e9rences cookies">\ud83c\udf6a Cookies</button>'
  +'<div id="ck-modal" onclick="ckModalBg(event)"><div class="ckm-card">'
  +'<div class="ckm-head"><h3>\ud83c\udf6a Param\u00e8tres des cookies</h3><button class="ckm-close" onclick="ckCloseModal()" aria-label="Fermer">\u2715</button></div>'
  +'<div class="ckm-intro">Nous respectons votre vie priv\u00e9e. Vous pouvez choisir, par finalit\u00e9, quels cookies activer. Le responsable de traitement est CONSEILPREV SARL, 19 rue Auguste Chabri\u00e8res, 75015 Paris. Vous pouvez modifier ou retirer votre consentement \u00e0 tout moment en rouvrant ce panneau, et consulter notre <a href="confidentialite.html">politique de confidentialit\u00e9</a>. Vos pr\u00e9f\u00e9rences sont conserv\u00e9es 13 mois, conform\u00e9ment aux recommandations CNIL.</div>'
  +'<div class="ckm-cat"><div class="ckm-cat-h"><span class="ckm-cat-t">\ud83d\udd12 Cookies n\u00e9cessaires</span><label class="ckm-sw"><input type="checkbox" checked disabled><span class="ckm-sl"></span></label></div><div class="ckm-cat-d">Essentiels au fonctionnement du site (session, authentification, s\u00e9curit\u00e9). Ne peuvent pas \u00eatre d\u00e9sactiv\u00e9s.</div></div>'
  +'<div class="ckm-cat"><div class="ckm-cat-h"><span class="ckm-cat-t">\u2699\ufe0f Cookies fonctionnels</span><label class="ckm-sw"><input type="checkbox" id="ckx-functional"><span class="ckm-sl"></span></label></div><div class="ckm-cat-d">Am\u00e9liorent les fonctionnalit\u00e9s et la personnalisation (pr\u00e9f\u00e9rences de langue, param\u00e8tres d\'affichage).</div></div>'
  +'<div class="ckm-cat"><div class="ckm-cat-h"><span class="ckm-cat-t">\ud83d\udcca Cookies analytiques</span><label class="ckm-sw"><input type="checkbox" id="ckx-analytics"><span class="ckm-sl"></span></label></div><div class="ckm-cat-d">Mesure d\'audience anonymis\u00e9e pour am\u00e9liorer le site.</div></div>'
  +'<div class="ckm-cat"><div class="ckm-cat-h"><span class="ckm-cat-t">\ud83d\udce3 Cookies marketing</span><label class="ckm-sw"><input type="checkbox" id="ckx-marketing"><span class="ckm-sl"></span></label></div><div class="ckm-cat-d">Personnalisation des contenus et mesure des campagnes. Aucun n\'est actif \u00e0 ce jour.</div></div>'
  +'<div class="ckm-actions"><button class="ckb-btn ckb-refuse" onclick="ckRefuseAll()">Tout refuser</button><button class="ckb-btn ckb-all" onclick="ckSavePrefs()">Enregistrer mes choix</button></div>'
  +'</div></div>';
  var wrap=document.createElement('div'); wrap.id='ck-shared-wrap'; wrap.innerHTML=html; document.body.appendChild(wrap);

  function hideBanner(){ var b=document.getElementById('ck-banner'); if(b) b.classList.remove('show'); var r=document.getElementById('ck-reopen'); if(r) r.style.display='flex'; }
  function syncToggles(p){ ['functional','analytics','marketing'].forEach(function(k){ var el=document.getElementById('ckx-'+k); if(el) el.checked=!!(p&&p[k]); }); }

  window.ckOpenModal = function(){ syncToggles(ckLoad()||{}); var m=document.getElementById('ck-modal'); if(m) m.classList.add('open'); };
  window.ckCloseModal = function(){ var m=document.getElementById('ck-modal'); if(m) m.classList.remove('open'); };
  window.ckModalBg = function(e){ if(e.target && e.target.id==='ck-modal') ckCloseModal(); };
  window.ckAcceptAll = function(){ var s=ckSave({functional:true,analytics:true,marketing:true}); hideBanner(); ckCloseModal(); ckApply(s); };
  window.ckRefuseAll = function(){ var s=ckSave({functional:false,analytics:false,marketing:false}); hideBanner(); ckCloseModal(); ckApply(s); };
  window.ckSavePrefs = function(){
    var s=ckSave({ functional:!!(document.getElementById('ckx-functional')||{}).checked,
                   analytics:!!(document.getElementById('ckx-analytics')||{}).checked,
                   marketing:!!(document.getElementById('ckx-marketing')||{}).checked });
    hideBanner(); ckCloseModal(); ckApply(s);
  };

  var prefs=ckLoad();
  if(!prefs){ setTimeout(function(){ var b=document.getElementById('ck-banner'); if(b) b.classList.add('show'); }, 450); }
  else { var r=document.getElementById('ck-reopen'); if(r) r.style.display='flex'; ckApply(prefs); }
})();
