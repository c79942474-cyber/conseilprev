/* Extrait de login.html — 2 bloc(s) en ligne, dans leur ordre d'origine.
   Le HTML est servi en no-store : ce fichier, lui, obtient un ETag
   et répond 304 dès la deuxième visite. */

;/* ── bloc 1/2 ── */

function switchTab(name){
  document.getElementById('tab-login').classList.toggle('on', name==='login');
  document.getElementById('tab-register').classList.toggle('on', name==='register');
  document.getElementById('panel-login').classList.toggle('on', name==='login');
  document.getElementById('panel-register').classList.toggle('on', name==='register');
  if(name === 'register') loadCaptcha();
}

if(new URLSearchParams(location.search).get('verified') === '1'){
  document.getElementById('verified-banner').style.display = 'block';
}

var REQUESTED_PLAN = new URLSearchParams(location.search).get('plan') === 'gratuit' ? 'gratuit' : 'pro';
var __rawPlan = new URLSearchParams(location.search).get('plan');
/* La destination d'après-connexion. Un module réservé renvoie ici avec
   ?suite=<son chemin> : sans cela, le visiteur qui vient d'être refusé sur le
   Panorama se retrouve sur l'accueil de Sentinel et doit retrouver seul la
   page qu'il demandait.
   On n'accepte QUE des chemins internes. Une URL absolue ferait de cette page
   un redirect ouvert — un lien /login?suite=https://ailleurs.exemple mènerait
   un visiteur hors du site en lui laissant croire qu'il y est resté. */
function __suiteSure(){
  var s = new URLSearchParams(location.search).get('suite') || '';
  if(!s || s.charAt(0) !== '/' || s.slice(0,2) === '//' || s.indexOf('\\') >= 0) return '';
  return s;
}
function __authDest(){
  var goPricing = (__rawPlan === 'pro' || __rawPlan === 'entreprise');
  try{ if(!goPricing && localStorage.getItem('sentinelGotoPricing') === '1') goPricing = true; if(goPricing) localStorage.removeItem('sentinelGotoPricing'); }catch(e){}
  if(goPricing) return '/sentinel?goto=pricing';
  return __suiteSure() || '/sentinel';
}
if(REQUESTED_PLAN === 'gratuit'){
  switchTab('register');
}

document.getElementById('login-form').addEventListener('submit', function(e){
  e.preventDefault();
  var btn = document.getElementById('login-btn');
  var errEl = document.getElementById('login-error');
  var email = document.getElementById('login-email').value.trim();
  var password = document.getElementById('login-password').value;

  btn.disabled = true; btn.textContent = 'Connexion…'; errEl.style.display = 'none';

  fetch('/api/sentinel-auth/login', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({email: email, password: password})
  })
  .then(function(r){ return r.json().then(function(d){ return {status:r.status, data:d}; }); })
  .then(function(res){
    if(res.status === 200){ window.location.href = __authDest(); }
    else {
      btn.disabled = false; btn.textContent = 'Se connecter';
      errEl.textContent = res.data.error || 'Identifiants incorrects.';
      errEl.style.display = 'block';
    }
  })
  .catch(function(){
    btn.disabled = false; btn.textContent = 'Se connecter';
    errEl.textContent = 'Erreur réseau. Réessayez.';
    errEl.style.display = 'block';
  });
});

document.getElementById('forgot-password-link').addEventListener('click', function(e){
  e.preventDefault();
  document.getElementById('login-form').style.display = 'none';
  document.getElementById('forgot-form').style.display = 'block';
});

document.getElementById('back-to-login-link').addEventListener('click', function(e){
  e.preventDefault();
  document.getElementById('forgot-form').style.display = 'none';
  document.getElementById('login-form').style.display = 'block';
  document.getElementById('forgot-success').style.display = 'none';
});

document.getElementById('forgot-form').addEventListener('submit', function(e){
  e.preventDefault();
  var btn = document.getElementById('forgot-btn');
  var errEl = document.getElementById('forgot-error');
  var successEl = document.getElementById('forgot-success');
  var email = document.getElementById('forgot-email').value.trim();
  errEl.style.display = 'none';

  btn.disabled = true; btn.textContent = 'Envoi…';

  fetch('/api/sentinel-auth/forgot-password', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({email: email})
  })
  .then(function(r){ return r.json(); })
  .then(function(){
    document.getElementById('forgot-email').value = '';
    successEl.style.display = 'block';
    btn.disabled = false; btn.textContent = 'Envoyer le lien';
  })
  .catch(function(){
    btn.disabled = false; btn.textContent = 'Envoyer le lien';
    errEl.textContent = 'Erreur réseau. Réessayez.';
    errEl.style.display = 'block';
  });
});

var passwordEl = document.getElementById('reg-password');

function generateStrongPassword(){
  var chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789!@#$%&*';
  var arr = new Uint32Array(14);
  crypto.getRandomValues(arr);
  var pw = '';
  for(var i=0;i<14;i++) pw += chars[arr[i] % chars.length];
  return pw;
}

document.getElementById('btn-generate').addEventListener('click', function(){
  passwordEl.value = generateStrongPassword();
  passwordEl.type = 'text'; /* affiche temporairement le mdp genere, pour que le client puisse le noter/copier */
  document.getElementById('btn-toggle-pw').textContent = '🙈';
  checkPasswordStrength();
});

document.getElementById('btn-toggle-pw').addEventListener('click', function(){
  var isHidden = passwordEl.type === 'password';
  passwordEl.type = isHidden ? 'text' : 'password';
  this.textContent = isHidden ? '🙈' : '👁';
});

function checkPasswordStrength(){
  var pw = passwordEl.value;
  var rules = {
    len: pw.length >= 10, upper: /[A-Z]/.test(pw), lower: /[a-z]/.test(pw),
    digit: /[0-9]/.test(pw), special: /[^A-Za-z0-9]/.test(pw)
  };
  var score = Object.values(rules).filter(Boolean).length;

  var ruleLabels = {len:'10 caractères minimum', upper:'Une majuscule', lower:'Une minuscule', digit:'Un chiffre', special:'Un caractère spécial'};
  Object.keys(ruleLabels).forEach(function(key){
    var el = document.getElementById('rule-' + key);
    if(el){ el.classList.toggle('ok', rules[key]); el.textContent = (rules[key] ? '✓ ' : '○ ') + ruleLabels[key]; }
  });

  var bars = [document.getElementById('bar1'), document.getElementById('bar2'), document.getElementById('bar3'), document.getElementById('bar4')];
  var colors = ['var(--accent)','var(--orange)','var(--orange)','var(--green)'];
  var labels = ['Trop faible','Faible','Correct','Fort'];
  var level = pw.length === 0 ? -1 : Math.min(3, Math.floor(score * 4 / 5));
  bars.forEach(function(b,i){ b.style.background = i <= level ? colors[level] : 'var(--rule)'; });
  document.getElementById('strength-label').textContent = pw.length === 0 ? 'Saisissez ou générez un mot de passe' : labels[level];

  return rules.len && rules.upper && rules.lower && rules.digit && rules.special;
}
passwordEl.addEventListener('input', checkPasswordStrength);

function loadCaptcha(){
  fetch('/api/sentinel-auth/register-captcha').then(function(r){ return r.json(); }).then(function(d){
    document.getElementById('captcha-question').textContent = d.captcha_question;
  });
}

document.getElementById('register-form').addEventListener('submit', function(e){
  e.preventDefault();
  try{ if(__rawPlan === 'pro' || __rawPlan === 'entreprise') localStorage.setItem('sentinelGotoPricing','1'); }catch(e){}
  var btn = document.getElementById('register-btn');
  var errEl = document.getElementById('register-error');
  var successEl = document.getElementById('register-success');
  errEl.style.display = 'none'; successEl.style.display = 'none';

  if(!checkPasswordStrength()){
    errEl.textContent = 'Le mot de passe ne respecte pas tous les critères de sécurité.';
    errEl.style.display = 'block';
    return;
  }
  // Aucune case à cocher : créer un compte relève de l'exécution du contrat et
  // des mesures précontractuelles (art. 6.1.b), et un consentement exigé pour
  // envoyer ne serait pas libre (art. 7.4). La page porte une mention
  // d'information (art. 13).

  btn.disabled = true; btn.textContent = 'Création…';

  fetch('/api/sentinel-auth/register', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({
      nom_entreprise: document.getElementById('reg-nom').value.trim(),
      email: document.getElementById('reg-email').value.trim().toLowerCase(),
      password: passwordEl.value,
      captcha_answer: document.getElementById('captcha-answer-reg').value,
      plan: REQUESTED_PLAN
    })
  }).then(function(r){ return r.json().then(function(d){ return {status:r.status, data:d}; }); })
  .then(function(res){
    if(res.status === 201){
      document.getElementById('register-form').reset();
      if(res.data.verification_email_sent === false){
        successEl.innerHTML = '⚠️ Compte créé, mais l\'email de confirmation n\'a pas pu être envoyé. Contactez <a href="mailto:christophe.cerf@outlook.com" style="color:inherit;text-decoration:underline">CONSEILPREV</a> pour activer votre accès manuellement.';
        successEl.style.color = 'var(--orange)';
      } else {
        successEl.textContent = '✅ Compte créé ! Vérifiez votre boîte mail pour confirmer votre adresse email avant de vous connecter.';
      }
      successEl.style.display = 'block';
      btn.disabled = false; btn.textContent = 'Créer mon compte';
    } else {
      btn.disabled = false; btn.textContent = 'Créer mon compte';
      errEl.textContent = res.data.error || 'Erreur lors de la création.';
      errEl.style.display = 'block';
      loadCaptcha();
    }
  }).catch(function(){
    btn.disabled = false; btn.textContent = 'Créer mon compte';
    errEl.textContent = 'Erreur réseau. Réessayez.';
    errEl.style.display = 'block';
  });
});


;/* ── bloc 2/2 ── */

/* Essai gratuit 15 jours : arrivee depuis le bandeau (bouton Demo du site).
   Pre-remplit l'adresse, ouvre l'onglet d'inscription et rappelle le contexte. */
(function cpEssaiInit(){
  function run(){
    try{
      var q = new URLSearchParams(location.search);
      if(q.get('essai') !== '1') return;
      var mail = (q.get('email') || '').trim();
      if(typeof switchTab === 'function'){ try { switchTab('register'); } catch(e){} }
      var champs = ['reg-email','login-email'];
      for(var i=0;i<champs.length;i++){
        var el = document.getElementById(champs[i]);
        if(el && mail && !el.value) el.value = mail;
      }
      var cible = document.getElementById('reg-email') || document.getElementById('login-email');
      if(cible && cible.parentNode && !document.getElementById('cp-essai-note')){
        var note = document.createElement('div');
        note.id = 'cp-essai-note';
        note.style.cssText = 'margin:0 0 14px 0;padding:10px 12px;border-left:3px solid #c9a227;background:rgba(201,162,39,.08);border-radius:6px;font-size:12.5px;line-height:1.5;color:#3a4250';
        note.innerHTML = '<strong>Essai gratuit \u2014 15 jours.</strong> Cr\u00e9ez votre compte pour acc\u00e9der au plan Gratuit de Sentinel pendant 15 jours. Sans carte bancaire. \u00c0 l\u2019\u00e9ch\u00e9ance, une souscription sera n\u00e9cessaire pour poursuivre.';
        var form = cible.closest('form') || cible.parentNode.parentNode;
        if(form && form.parentNode) form.parentNode.insertBefore(note, form);
      }
    }catch(e){}
  }
  if(document.readyState === 'loading'){ document.addEventListener('DOMContentLoaded', run); } else { run(); }
})();

