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
    .then(function(html){ placeholder.outerHTML = html; })
    .catch(function(){ /* echec silencieux : la page reste fonctionnelle sans footer */ });
})();
