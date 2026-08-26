/* Extrait de business-developer.html — 2 bloc(s) en ligne, dans leur ordre d'origine.
   Le HTML est servi en no-store : ce fichier, lui, obtient un ETag
   et répond 304 dès la deuxième visite. */

;/* ── bloc 1/2 ── */

// Upload CV — afficher nom du fichier
document.getElementById('af-cv').addEventListener('change', function(){
  var nameEl = document.getElementById('af-cv-name');
  if(this.files && this.files[0]){
    nameEl.textContent = this.files[0].name;
    nameEl.classList.add('has-file');
  } else {
    nameEl.textContent = 'Aucun fichier sélectionné';
    nameEl.classList.remove('has-file');
  }
});

// Soumission formulaire
document.getElementById('apply-form').addEventListener('submit', function(e){
  e.preventDefault();
  var prenom  = document.getElementById('af-prenom').value.trim();
  var nom     = document.getElementById('af-nom').value.trim();
  var email   = document.getElementById('af-email').value.trim();
  var consent = document.getElementById('af-consent-cb');
  var cvInput = document.getElementById('af-cv');

  // Validation consentement
  if(!consent.checked){
    var block = consent.closest('.af-consent');
    block.classList.add('error');
    block.scrollIntoView({behavior:'smooth',block:'center'});
    setTimeout(function(){ block.classList.remove('error'); }, 2500);
    return;
  }
  if(!prenom || !nom || !email){ return; }

  var btn = document.getElementById('af-submit');
  var txt = document.getElementById('af-txt');
  btn.disabled = true;
  txt.textContent = 'Envoi en cours…';

  // ── Construire FormData avec le fichier CV ──
  var fd = new FormData();
  fd.append('form_type',  'candidature_bd');
  fd.append('prenom',     prenom);
  fd.append('nom',        nom);
  fd.append('email',      email);
  fd.append('telephone',  document.getElementById('af-tel').value.trim());
  fd.append('message',    document.getElementById('af-message').value.trim());
  fd.append('consent',    'true');
  fd.append('source_url', window.location.pathname);

  if(cvInput.files && cvInput.files[0]){
    fd.append('cv', cvInput.files[0]);
  }

  // ── Appel API ──
  fetch('/api/apply', { method:'POST', body:fd })
    .then(function(r){ return r.json(); })
    .then(function(res){
      btn.disabled = false;
      if(res.ok){
        var cvOk   = res.cv_received;
        var mailOk = res.email_sent;
        var suc = document.getElementById('af-success');

        if(mailOk){
          // ✅ Email envoyé avec CV
          txt.textContent = 'Envoyé ✓';
          if(suc){
            suc.style.display = 'block';
            suc.style.background = 'rgba(94,234,212,.1)';
            suc.style.border = '1px solid rgba(94,234,212,.3)';
            suc.innerHTML = '✓ Candidature' + (cvOk ? ' + CV' : '') + ' envoyée à CONSEILPREV — réponse sous 48h ouvrées';
          }
        } else {
          // ⚠ SMTP non configuré → fallback mailto
          txt.textContent = 'Relancer →';
          if(suc){
            suc.style.display = 'block';
            suc.style.background = 'rgba(251,191,36,.08)';
            suc.style.border = '1px solid rgba(251,191,36,.3)';
            suc.style.color = '#fde68a';
            suc.innerHTML =
              '✓ Candidature sauvegardée sur le serveur.<br><br>' +
              '<span style="font-size:11px;line-height:1.7">Pour garantir la réception par CONSEILPREV, ' +
              'cliquez ce bouton :</span><br><br>' +
              '<button onclick="openMailtoFallback()" style="' +
                'background:linear-gradient(135deg,#6d28d9,#d946ef);' +
                'color:#fff;border:none;padding:10px 22px;border-radius:9px;' +
                'font-size:13px;font-weight:700;cursor:pointer;font-family:DM Sans,sans-serif;' +
                'box-shadow:0 4px 16px rgba(217,70,239,.4);' +
              '">📨 Ouvrir mon email →</button>';
          }
          // Fallback mailto automatique avec toutes les infos
          setTimeout(function(){
            var cvName = document.getElementById('af-cv-name').textContent;
            var body = encodeURIComponent(
              '=== CANDIDATURE BUSINESS DEVELOPER INDÉPENDANT ===\n\n' +
              'Prénom    : ' + prenom + '\n' +
              'Nom       : ' + nom + '\n' +
              'Email     : ' + email + '\n' +
              'Téléphone : ' + (document.getElementById('af-tel').value.trim() || '—') + '\n\n' +
              'CV        : ' + (cvOk ? res.cv_filename || cvName : cvName + ' (joindre manuellement)') + '\n\n' +
              'Message   :\n' + (document.getElementById('af-message').value.trim() || '—') + '\n\n' +
              '---\n' +
              'Consentement RGPD : OUI (Art. 6.1.a) — ' + new Date().toLocaleString('fr-FR') + '\n' +
              'Source : conseilprev.onrender.com/business-developer'
            );
            window.location.href =
              'mailto:christophe.cerf@outlook.com' +
              '?subject=' + encodeURIComponent('[CANDIDATURE BD] ' + prenom + ' ' + nom) +
              '&body=' + body;
          }, 800);
        }

        if(suc) suc.scrollIntoView({behavior:'smooth',block:'center'});
        document.getElementById('apply-form').reset();
        var nameEl = document.getElementById('af-cv-name');
        if(nameEl){ nameEl.textContent = 'Aucun fichier sélectionné'; nameEl.classList.remove('has-file'); }

      } else {
        txt.textContent = 'Réessayer';
        var suc = document.getElementById('af-success');
        if(suc){
          suc.style.display = 'block';
          suc.style.background = 'rgba(248,113,113,.08)';
          suc.style.border = '1px solid rgba(248,113,113,.3)';
          suc.style.color = '#fca5a5';
          suc.textContent = '⚠ ' + (res.error || 'Erreur — réessayez');
        }
      }
    })
    .catch(function(err){
      btn.disabled = false;
      txt.textContent = 'Réessayer';
      // Fallback direct mailto si erreur réseau
      var body = encodeURIComponent(
        'Candidature Business Developer\n\n' +
        'Prénom : ' + prenom + '\nNom : ' + nom + '\nEmail : ' + email
      );
      window.location.href = 'mailto:christophe.cerf@outlook.com?subject=' +
        encodeURIComponent('[CANDIDATURE BD] ' + prenom + ' ' + nom) + '&body=' + body;
    });
});
document.addEventListener('contextmenu', function(e){ e.preventDefault(); });

function openMailtoFallback(){
  if(window._mailtoFallback){
    window.open(window._mailtoFallback, '_blank');
  } else {
    window.open('mailto:christophe.cerf@outlook.com?subject=[CANDIDATURE BD]', '_blank');
  }
}


;/* ── bloc 2/2 ── */

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

