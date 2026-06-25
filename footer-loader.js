/* ══ FOOTER PARTAGÉ — chargement dynamique sur les pages secondaires ══ */
(function(){
  var placeholder = document.getElementById('shared-footer-placeholder');
  if(!placeholder) return;
  fetch('/footer-shared.html', {cache:'no-store'})
    .then(function(r){ return r.text(); })
    .then(function(html){ placeholder.outerHTML = html; })
    .catch(function(){ /* echec silencieux : la page reste fonctionnelle sans footer */ });
})();
