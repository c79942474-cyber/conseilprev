/* Extrait de reset-password.html — 1 bloc(s) en ligne, dans leur ordre d'origine.
   Le HTML est servi en no-store : ce fichier, lui, obtient un ETag
   et répond 304 dès la deuxième visite. */

;/* ── bloc 1/1 ── */

var token = location.pathname.split('/').pop();
var passwordEl = document.getElementById('password');

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
  passwordEl.type = 'text';
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
    len: pw.length >= 10,
    upper: /[A-Z]/.test(pw),
    lower: /[a-z]/.test(pw),
    digit: /[0-9]/.test(pw),
    special: /[^A-Za-z0-9]/.test(pw)
  };
  var score = Object.values(rules).filter(Boolean).length;

  var ruleLabels = {
    len: '10 caractères minimum', upper: 'Une majuscule', lower: 'Une minuscule',
    digit: 'Un chiffre', special: 'Un caractère spécial'
  };
  Object.keys(ruleLabels).forEach(function(key){
    var el = document.getElementById('rule-' + key);
    if(el){
      el.classList.toggle('ok', rules[key]);
      el.textContent = (rules[key] ? '✓ ' : '○ ') + ruleLabels[key];
    }
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

fetch('/api/sentinel-auth/reset-password-info/' + token).then(function(r){ return r.json().then(function(d){ return {status:r.status,data:d}; }); })
.then(function(res){
  if(!res.data.valid){
    document.querySelector('.box').innerHTML = '<div class="logo">Sentinel <span class="ai">AI</span></div><div class="sub">Lien invalide</div><p style="font-size:13px;color:var(--ink2);margin-top:16px">' + res.data.error + ' Refaites une demande de réinitialisation depuis la page de connexion.</p>';
    return;
  }
  document.getElementById('welcome-nom').textContent = res.data.nom_entreprise;
  document.getElementById('email-display').value = res.data.email_masque;
  document.getElementById('captcha-question').textContent = res.data.captcha_question;
});

document.getElementById('reset-form').addEventListener('submit', function(e){
  e.preventDefault();
  var errEl = document.getElementById('error-msg');
  var btn = document.getElementById('submit-btn');
  errEl.style.display = 'none';

  if(!checkPasswordStrength()){
    errEl.textContent = 'Le mot de passe ne respecte pas tous les critères de sécurité.';
    errEl.style.display = 'block';
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Modification…';

  fetch('/api/sentinel-auth/reset-password', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({
      token: token,
      password: passwordEl.value,
      captcha_answer: document.getElementById('captcha-answer').value
    })
  }).then(function(r){ return r.json().then(function(d){ return {status:r.status, data:d}; }); })
  .then(function(res){
    if(res.status === 200){
      document.getElementById('reset-form').style.display = 'none';
      document.getElementById('success-msg').style.display = 'block';
      setTimeout(function(){ window.location.href = '/login'; }, 2800);
    } else {
      btn.disabled = false;
      btn.textContent = 'Définir le nouveau mot de passe';
      errEl.textContent = res.data.error || 'Erreur lors de la réinitialisation.';
      errEl.style.display = 'block';
    }
  }).catch(function(){
    btn.disabled = false;
    btn.textContent = 'Définir le nouveau mot de passe';
    errEl.textContent = 'Erreur réseau. Réessayez.';
    errEl.style.display = 'block';
  });
});

