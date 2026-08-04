/* ══ FOOTER PARTAGÉ — chargement dynamique sur les pages secondaires ══ */
(function(){
  /* Bandeau cookies mutualise (conforme CNIL) sur toutes les pages */
  if(!document.getElementById('ck-banner') && !window.__ckSharedLoaded){
    var cs=document.createElement('script'); cs.src='/cookies.js'; cs.defer=true; document.head.appendChild(cs);
  }
  var placeholder = document.getElementById('shared-footer-placeholder');
  if(!placeholder) return;
  fetch('/footer-shared.html', {cache:'no-store'})
    .then(function(r){ return r.text(); })
    .then(function(html){
      placeholder.outerHTML = html;
      /* Le pied de page arrive APRES le chargement du document : un script de
         bascule branche sur DOMContentLoaded ne trouverait aucun lien vers
         i-aes.com et ne ferait rien, silencieusement. Il se charge donc ICI,
         une fois le pied de page reellement insere. */
      if(!window.basculeIaes && !document.getElementById('js-bascule')){
        var b = document.createElement('script');
        b.id = 'js-bascule'; b.src = '/bascule.js'; b.defer = true;
        document.head.appendChild(b);
      }
    })
    .catch(function(){ /* echec silencieux : la page reste fonctionnelle sans footer */ });
})();
