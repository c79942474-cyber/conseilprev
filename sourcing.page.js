/* Extrait de sourcing.html — 5 bloc(s) en ligne, dans leur ordre d'origine.
   Le HTML est servi en no-store : ce fichier, lui, obtient un ETag
   et répond 304 dès la deuxième visite. */

;/* ── bloc 1/5 ── */

// Formulaire sourcing
document.getElementById('sourcing-form').addEventListener('submit', function(e){
  e.preventDefault();
  var prenom = document.getElementById('sf-prenom').value.trim();
  var nom    = document.getElementById('sf-nom').value.trim();
  var email  = document.getElementById('sf-email').value.trim();
  var profil = document.getElementById('sf-profil').value.trim();
  if(!prenom||!nom||!email||!profil){ return; }
  var consent = document.getElementById('sf-consent-cb');
  if(!consent || !consent.checked){
    var block = consent ? consent.closest('.sf-consent') : null;
    if(block){
      block.classList.add('error');
      block.scrollIntoView({behavior:'smooth',block:'center'});
      setTimeout(function(){ block.classList.remove('error'); }, 2500);
    }
    return;
  }
  var btn = document.getElementById('sf-submit');
  var txt = document.getElementById('sf-txt');
  btn.disabled = true; txt.textContent = 'Envoi…';

  var fd = new FormData();
  fd.append('form_type',   'sourcing_profil');
  fd.append('prenom',      prenom);
  fd.append('nom',         nom);
  fd.append('email',       email);
  fd.append('telephone',   document.getElementById('sf-tel').value.trim());
  fd.append('entreprise',  document.getElementById('sf-entreprise').value.trim());
  fd.append('fonction',    document.getElementById('sf-fonction').value.trim());
  fd.append('message',     profil);
  fd.append('consent',     'true');
  fd.append('source_url',  window.location.pathname);

  fetch('/api/apply', { method:'POST', body:fd })
    .then(function(r){ return r.json(); })
    .then(function(res){
      btn.disabled = false;
      var msg = document.getElementById('sf-msg');
      if(res.ok){
        if(res.email_sent){
          // ✅ Email envoyé
          txt.textContent = 'Envoyé ✓';
          if(msg){
            msg.style.display='block';
            msg.style.color='var(--teal)';
            msg.textContent='✓ Demande envoyée — réponse sous 48h ouvrées';
          }
        } else {
          // ⚠ SMTP absent → fallback mailto automatique
          txt.textContent = 'Envoi alternatif…';
          if(msg){
            msg.style.display='block';
            msg.style.color='#fde68a';
            msg.style.background='rgba(251,191,36,.08)';
            msg.style.border='1px solid rgba(251,191,36,.3)';
            msg.textContent='⚠ Envoi par votre client mail dans 1s…';
          }
          setTimeout(function(){
            var body = [
              '=== DEMANDE SOURCING CONSEILPREV ===',
              '',
              'Prénom     : ' + prenom,
              'Nom        : ' + nom,
              'Email      : ' + email,
              'Téléphone  : ' + document.getElementById('sf-tel').value.trim(),
              'Entreprise : ' + document.getElementById('sf-entreprise').value.trim(),
              'Fonction   : ' + document.getElementById('sf-fonction').value.trim(),
              '',
              'Profil recherché :',
              profil,
              '',
              '---',
              'Source : conseilprev.onrender.com/sourcing',
              'Date   : ' + new Date().toLocaleString('fr-FR'),
            ].join('\n');
            window.open(
              'mailto:christophe.cerf@outlook.com'
              + '?subject=' + encodeURIComponent('[SOURCING] ' + prenom + ' ' + nom + ' — ' + profil.slice(0,40))
              + '&body='    + encodeURIComponent(body),
              '_blank'
            );
            txt.textContent = 'Envoyé ✓';
            if(msg){
              msg.style.color='var(--teal)';
              msg.style.background='rgba(94,234,212,.08)';
              msg.style.border='1px solid rgba(94,234,212,.25)';
              msg.innerHTML='✓ Demande transmise — réponse sous 48h.<br>' +
                '<span style="font-size:10px;opacity:.75">Email ouvert dans votre client mail.</span>';
            }
          }, 900);
        }
        document.getElementById('sourcing-form').reset();
        var cb = document.getElementById('sf-consent-cb');
        if(cb){ cb.checked = false; }
      } else {
        txt.textContent = 'Envoyer';
        if(msg){
          msg.style.display='block';
          msg.style.color='#fca5a5';
          msg.textContent='⚠ ' + (res.error || 'Erreur — réessayez');
        }
      }
    })
    .catch(function(){
      // Erreur réseau → fallback mailto direct
      btn.disabled = false; txt.textContent = 'Réessayer';
      window.open(
        'mailto:christophe.cerf@outlook.com'
        + '?subject=' + encodeURIComponent('[SOURCING] ' + prenom + ' ' + nom)
        + '&body='    + encodeURIComponent('Demande sourcing de ' + prenom + ' ' + nom + ' (' + email + ')\n\nProfil : ' + profil),
        '_blank'
      );
    });
});
document.addEventListener('contextmenu',function(e){e.preventDefault();});


;/* ── bloc 2/5 ── */

// ════════ AUTHENTIFICATION CLIENT ════════
function switchAuth(mode){
  document.getElementById('tab-login').classList.toggle('active', mode==='login');
  document.getElementById('tab-register').classList.toggle('active', mode==='register');
  document.getElementById('form-login').classList.toggle('show', mode==='login');
  document.getElementById('form-register').classList.toggle('show', mode==='register');
}

function checkPwStrength(){
  var pw = document.getElementById('reg-password').value;
  function set(id, ok){
    var el = document.getElementById(id);
    el.classList.toggle('ok', ok);
    el.textContent = (ok?'● ':'○ ') + el.textContent.slice(2);
  }
  set('r-len', pw.length>=8);
  set('r-maj', /[A-Z]/.test(pw));
  set('r-min', /[a-z]/.test(pw));
  set('r-num', /[0-9]/.test(pw));
}

function showAuthMsg(id, type, text){
  var el = document.getElementById(id);
  el.className = 'auth-msg ' + type;
  el.innerHTML = text;
}

// Inscription
document.getElementById('form-register').addEventListener('submit', function(e){
  e.preventDefault();
  var consent = document.getElementById('reg-consent');
  if(!consent.checked){ showAuthMsg('reg-msg','error','⚠ Le consentement RGPD est requis.'); return; }
  var btn = document.getElementById('reg-btn');
  btn.disabled = true; btn.textContent = 'Création…';
  fetch('/api/auth/register', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({
      prenom: document.getElementById('reg-prenom').value.trim(),
      nom: document.getElementById('reg-nom').value.trim(),
      entreprise: document.getElementById('reg-entreprise').value.trim(),
      email: document.getElementById('reg-email').value.trim(),
      password: document.getElementById('reg-password').value,
      consent: true
    })
  })
  .then(function(r){ return r.json(); })
  .then(function(res){
    btn.disabled = false; btn.textContent = 'Créer mon compte';
    if(res.ok){
      // LE SERVEUR DIT LUI-MÊME QUOI FAIRE, et la page ne rajoute plus de
      // lien. Elle en affichait un — le jeton de confirmation renvoyé dans
      // la réponse — qui permettait de confirmer une adresse sans y avoir
      // accès dès que l'envoi de courrier tombait. Voir `auth_register`.
      showAuthMsg('reg-msg', res.email_sent ? 'success' : 'info', '✓ ' + res.message)
      document.getElementById('form-register').reset();
    } else {
      showAuthMsg('reg-msg','error','⚠ ' + (res.error||'Erreur'));
    }
  })
  .catch(function(){ btn.disabled=false; btn.textContent='Créer mon compte'; showAuthMsg('reg-msg','error','⚠ Erreur réseau'); });
});

// Connexion
document.getElementById('form-login').addEventListener('submit', function(e){
  e.preventDefault();
  var btn = document.getElementById('login-btn');
  btn.disabled = true; btn.textContent = 'Connexion…';
  fetch('/api/auth/login', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({
      email: document.getElementById('login-email').value.trim(),
      password: document.getElementById('login-password').value
    })
  })
  .then(function(r){ return r.json(); })
  .then(function(res){
    btn.disabled = false; btn.textContent = 'Se connecter';
    if(res.ok){
      try{ sessionStorage.setItem('cp_user', JSON.stringify(res.user)); sessionStorage.setItem('cp_token', res.token); }catch(e){}
      showLoggedIn(res.user);
    } else {
      showAuthMsg('login-msg','error','⚠ ' + (res.error||'Erreur'));
    }
  })
  .catch(function(){ btn.disabled=false; btn.textContent='Se connecter'; showAuthMsg('login-msg','error','⚠ Erreur réseau'); });
});

function showLoggedIn(user){
  var card = document.getElementById('auth-card');
  card.innerHTML =
    '<div class="auth-logged">'+
      '<div class="auth-logged-avatar">'+(user.prenom?user.prenom[0].toUpperCase():'👤')+'</div>'+
      '<div class="auth-logged-name">Bienvenue, '+user.prenom+' !</div>'+
      '<div class="auth-logged-email">'+user.email+(user.entreprise?' · '+user.entreprise:'')+'</div>'+
      '<a href="/platform" class="auth-btn" style="display:inline-block;text-decoration:none;margin-bottom:14px">🚀 Accéder à la plateforme B2B →</a>'+
      '<div><button class="auth-logout" onclick="logout()">Se déconnecter</button></div>'+
    '</div>';
}

function logout(){
  try{ sessionStorage.removeItem('cp_user'); sessionStorage.removeItem('cp_token'); }catch(e){}
  location.reload();
}

// Restaurer la session au chargement
(function(){
  try{
    var u = sessionStorage.getItem('cp_user');
    if(u){ showLoggedIn(JSON.parse(u)); }
  }catch(e){}
})();


;/* ── bloc 3/5 ── */

// ════════ ACCÈS ADMINISTRATEUR ════════
document.getElementById('form-admin').addEventListener('submit', function(e){
  e.preventDefault();
  var btn = document.getElementById('admin-btn');
  btn.disabled = true; btn.textContent = 'Vérification…';
  fetch('/api/auth/admin-login', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({
      email: document.getElementById('admin-email').value.trim(),
      password: document.getElementById('admin-password').value
    })
  })
  .then(function(r){ return r.json(); })
  .then(function(res){
    btn.disabled = false; btn.textContent = 'Connexion sécurisée';
    if(res.ok && res.admin){
      try{ sessionStorage.setItem('cp_user', JSON.stringify(res.user)); sessionStorage.setItem('cp_token', res.token); sessionStorage.setItem('cp_admin','1'); }catch(e){}
      showAuthMsg('admin-msg','success','✓ Accès accordé — redirection…');
      setTimeout(function(){ window.location.href = '/platform'; }, 800);
    } else {
      showAuthMsg('admin-msg','error','⚠ ' + (res.error||'Accès refusé'));
    }
  })
  .catch(function(){ btn.disabled=false; btn.textContent='Connexion sécurisée'; showAuthMsg('admin-msg','error','⚠ Erreur réseau'); });
});
// Fermer modal au clic extérieur
document.getElementById('admin-modal').addEventListener('click', function(e){
  if(e.target === this) this.classList.remove('show');
});


;/* ── bloc 4/5 ── */

function openMailtoSourcing(){
  var v = function(id){ var el = document.getElementById(id); return (el && el.value) ? el.value.trim() : ''; };
  var prenom = v('sf-prenom'), nom = v('sf-nom'), email = v('sf-email');
  var tel = v('sf-tel'), ent = v('sf-entreprise'), fn_ = v('sf-fonction');
  var profil = v('sf-profil');
  var body = ['=== DEMANDE SOURCING CONSEILPREV ===','',
    'Prénom : '+(prenom||'—'),'Nom : '+(nom||'—'),'Email : '+(email||'—'),
    'Tél : '+(tel||'—'),'Entreprise : '+(ent||'—'),'Fonction : '+(fn_||'—'),'',
    'Profil recherché :', profil||'—','','---',
    'Source : conseilprev.onrender.com/sourcing',
    'Date : '+new Date().toLocaleString('fr-FR')
  ].join('\n');
  window.open('mailto:christophe.cerf@outlook.com'
    +'?subject='+encodeURIComponent('[SOURCING] '+(prenom||'')+' '+(nom||''))
    +'&body='+encodeURIComponent(body),'_blank');
}


;/* ── bloc 5/5 ── */

/* ══ SÉCURITÉ FORMULAIRES — Protection universelle ══ */
(function(){
  // 1. Débounce sur tous les boutons submit (évite double-clic)
  document.addEventListener('DOMContentLoaded', function(){
    document.querySelectorAll('form').forEach(function(form){
      form.addEventListener('submit', function(){
        var btns = form.querySelectorAll('[type="submit"]');
        btns.forEach(function(btn){
          if(!btn.dataset.debounced){
            btn.dataset.debounced = '1';
            // Ré-activer après 5s max (en cas d'erreur réseau)
            setTimeout(function(){ btn.disabled = false; delete btn.dataset.debounced; }, 5000);
          }
        });
      });
    });

    // 2. Limiter longueur visible des champs texte
    var limits = {
      'pf-prenom':80,'pf-nom':80,'pf-email':150,'pf-tel':30,'pf-co':120,
      'pf-role':100,'pf-msg':3000,'sf-prenom':80,'sf-nom':80,'sf-email':150,
      'sf-profil':2000,'af-prenom':80,'af-nom':80,'af-email':150,'af-message':2000
    };
    Object.keys(limits).forEach(function(id){
      var el = document.getElementById(id);
      if(el) el.setAttribute('maxlength', limits[id]);
    });

    // 3. Détection auto-fill suspect (bots)
    var hpFields = document.querySelectorAll('#hp, #_hp, [name="website"], [name="_hp"]');
    hpFields.forEach(function(el){
      el.value = '';
      el.setAttribute('tabindex','-1');
      el.setAttribute('autocomplete','off');
    });

    // 4. Protection copier-coller sur champs sensibles (optionnel)
    // Désactivé pour l'UX

    // 5. Timeout session visuel (avertissement après 25min d'inactivité)
    var inactiveTimer;
    var SESSION_WARNING = 25 * 60 * 1000;
    function resetTimer(){
      clearTimeout(inactiveTimer);
      inactiveTimer = setTimeout(function(){
        // Avertissement discret si formulaire en cours de remplissage
        var hasInput = Array.from(document.querySelectorAll('input,textarea'))
          .some(function(el){ return el.value.trim().length > 0; });
        if(hasInput){
          console.info('CONSEILPREV: session bientôt expirée');
        }
      }, SESSION_WARNING);
    }
    ['mousemove','keydown','click','touchstart'].forEach(function(e){
      document.addEventListener(e, resetTimer, {passive:true});
    });
    resetTimer();
  });
})();

