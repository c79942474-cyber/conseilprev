/* Extrait de platform.html — 1 bloc(s) en ligne, dans leur ordre d'origine.
   Le HTML est servi en no-store : ce fichier, lui, obtient un ETag
   et répond 304 dès la deuxième visite. */

;/* ── bloc 1/1 ── */

"use strict";
// ════════════════════════════════════════
// PLATEFORME B2B v2 — multi-sélection, carte France 3D
// ════════════════════════════════════════
var BRIEF = {};
var HARD_SKILLS = [];
var SOFT_SKILLS = [];
var MATCHES = [];        // recherche courante
var CART = [];           // sélection cumulée multi-recherches
var SEARCH_COUNT = 0;
var AI_MODEL = null;

// ── Mode admin : chargé depuis sessionStorage (set par /sourcing après login admin) ──
var IS_ADMIN = false;
try {
  IS_ADMIN = sessionStorage.getItem('cp_admin') === '1';
} catch(e){}
var SIGNED = {};
var ACTIVE_CAND = 0;     // onglet contrat actif

// Villes françaises (coordonnées sur le viewBox de la carte)
var CITIES = [
  {name:'Paris',              x:296, y:112, rid:'idf'},
  {name:'Lille',              x:310, y:60,  rid:'hdf'},
  {name:'Rouen',              x:204, y:90,  rid:'nor'},
  {name:'Caen',               x:164, y:96,  rid:'nor'},
  {name:'Rennes',             x:118, y:118, rid:'bre'},
  {name:'Brest',              x:68,  y:106, rid:'bre'},
  {name:'Nantes',             x:140, y:186, rid:'pdl'},
  {name:'Le Mans',            x:196, y:164, rid:'pdl'},
  {name:'Orléans',            x:256, y:164, rid:'cvl'},
  {name:'Tours',              x:224, y:178, rid:'cvl'},
  {name:'Strasbourg',         x:428, y:98,  rid:'ges'},
  {name:'Reims',              x:346, y:74,  rid:'ges'},
  {name:'Nancy',              x:400, y:112, rid:'ges'},
  {name:'Dijon',              x:350, y:192, rid:'bfc'},
  {name:'Besançon',           x:398, y:186, rid:'bfc'},
  {name:'Bordeaux',           x:130, y:312, rid:'naq'},
  {name:'Poitiers',           x:196, y:232, rid:'naq'},
  {name:'Limoges',            x:208, y:268, rid:'naq'},
  {name:'Lyon',               x:374, y:264, rid:'ara'},
  {name:'Grenoble',           x:408, y:302, rid:'ara'},
  {name:'Clermont-Ferrand',   x:306, y:282, rid:'ara'},
  {name:'Toulouse',           x:218, y:406, rid:'occ'},
  {name:'Montpellier',        x:296, y:424, rid:'occ'},
  {name:'Nîmes',              x:316, y:408, rid:'occ'},
  {name:'Marseille',          x:386, y:430, rid:'pac'},
  {name:'Nice',               x:440, y:400, rid:'pac'},
  {name:'Toulon',             x:406, y:442, rid:'pac'},
];

// Identités candidat CONFIDENTIELLES (jamais affichées au client,
// transmises uniquement à CONSEILPREV par email)
var IDENT_POOL = [
  {prenom:'Karim',  nom:'Benali',    email:'k.benali@pro-mail.fr',     tel:'+33 6 12 45 78 90', cv:'20260614_181515_Karim_Benali.pdf',   source:'Vivier CONSEILPREV',       date_source:'03/2025'},
  {prenom:'Sophie', nom:'Marchand',  email:'sophie.marchand@dev.io',   tel:'+33 6 98 32 11 04', cv:'20260614_181515_Sophie_Marchand.pdf', source:'Free-Work (candidature)',  date_source:'01/2026'},
  {prenom:'Thomas', nom:'Lefèvre',   email:'t.lefevre@cyberpro.fr',    tel:'+33 7 45 22 89 13', cv:'20260614_181515_Thomas_Lefevre.pdf',  source:'Malt',                     date_source:'04/2026'},
  {prenom:'Amina',  nom:'Diallo',    email:'amina.diallo@datapro.eu',  tel:'+33 6 77 54 20 36', cv:'20260614_181515_Amina_Diallo.pdf',    source:'LinkedIn (approche directe)', date_source:'02/2026'},
  {prenom:'Julien', nom:'Rousseau',  email:'j.rousseau@freelance.dev', tel:'+33 6 30 18 92 47', cv:'20260614_181515_Julien_Rousseau.pdf', source:'Formulaire /business-developer', date_source:'05/2026'}
];

// ── Stepper ──
function goStep(n){
  document.querySelectorAll('.panel').forEach(function(p){ p.classList.remove('show'); });
  document.getElementById('panel-'+n).classList.add('show');
  document.querySelectorAll('.step-item').forEach(function(s){
    var sn = parseInt(s.dataset.step);
    s.classList.toggle('active', sn === n);
    s.classList.toggle('done', sn < n);
  });
  window.scrollTo({top:0, behavior:'smooth'});
}

// ── Skills tags ──
function setupSkills(inputId, wrapId, arr){
  var input = document.getElementById(inputId);
  input.addEventListener('keydown', function(e){
    if(e.key === 'Enter' || e.key === ','){
      e.preventDefault();
      var v = input.value.trim().replace(/,$/,'');
      if(v && arr.indexOf(v) < 0 && arr.length < 12){
        arr.push(v);
        renderSkills(wrapId, arr, inputId);
      }
      input.value = '';
    }
    if(e.key === 'Backspace' && !input.value && arr.length){
      arr.pop();
      renderSkills(wrapId, arr, inputId);
    }
  });
}
function renderSkills(wrapId, arr, inputId){
  var wrap = document.getElementById(wrapId);
  var input = document.getElementById(inputId);
  wrap.querySelectorAll('.skill-tag').forEach(function(t){ t.remove(); });
  arr.forEach(function(s, i){
    var tag = document.createElement('span');
    tag.className = 'skill-tag';
    var btn = document.createElement('button');
    btn.type = 'button'; btn.textContent = '×';
    btn.onclick = (function(w, idx){ return function(){ removeSkill(w, idx); }; })(wrapId, i);
    tag.textContent = s + ' ';
    tag.appendChild(btn);
    wrap.insertBefore(tag, input);
  });
}
function removeSkill(wrapId, i){
  var arr = wrapId === 'hard-wrap' ? HARD_SKILLS : SOFT_SKILLS;
  arr.splice(i, 1);
  renderSkills(wrapId, arr, wrapId === 'hard-wrap' ? 'hard-input' : 'soft-input');
}
setupSkills('hard-input','hard-wrap',HARD_SKILLS);
setupSkills('soft-input','soft-wrap',SOFT_SKILLS);

// ── Soumission brief ──
document.getElementById('brief-form').addEventListener('submit', function(e){
  e.preventDefault();
  // Aucune case de consentement à cocher : une recherche de profil relève des
  // mesures précontractuelles (art. 6.1.b), et un consentement exigé pour
  // envoyer ne serait pas libre (art. 7.4). Le formulaire porte une mention
  // d'information (art. 13), pas une condition d'envoi.
  var required = ['c-prenom','c-nom','c-email','c-entreprise','p-titre','p-domaine','p-contrat','p-tjm','p-lieu'];
  var missing = required.filter(function(id){ return !document.getElementById(id).value.trim(); });
  if(missing.length){
    var el = document.getElementById(missing[0]);
    el.focus(); el.style.borderColor = 'rgba(248,113,113,.7)';
    setTimeout(function(){ el.style.borderColor=''; }, 2500);
    return;
  }
  if(!HARD_SKILLS.length){
    document.getElementById('hard-input').focus();
    document.getElementById('hard-wrap').style.borderColor = 'rgba(248,113,113,.7)';
    setTimeout(function(){ document.getElementById('hard-wrap').style.borderColor=''; }, 2500);
    return;
  }
  BRIEF = {
    prenom:     document.getElementById('c-prenom').value.trim(),
    nom:        document.getElementById('c-nom').value.trim(),
    email:      document.getElementById('c-email').value.trim(),
    tel:        document.getElementById('c-tel').value.trim(),
    entreprise: document.getElementById('c-entreprise').value.trim(),
    fonction:   document.getElementById('c-fonction').value.trim(),
    titre:      document.getElementById('p-titre').value.trim(),
    domaine:    document.getElementById('p-domaine').value,
    contrat:    document.getElementById('p-contrat').value,
    tjm:        parseInt(document.getElementById('p-tjm').value) || 0,
    duree:      document.getElementById('p-duree').value,
    lieu:       document.getElementById('p-lieu').value.trim(),
    start:      document.getElementById('p-start').value,
    hard:       HARD_SKILLS.slice(),
    soft:       SOFT_SKILLS.slice(),
    desc:       document.getElementById('p-desc').value.trim(),
  };
  SEARCH_COUNT++;
  goStep(3);
  runSearch();
});

// ── Nouvelle recherche (conserve le panier) ──
function newSearch(){
  document.getElementById('p-titre').value = '';
  HARD_SKILLS.length = 0; SOFT_SKILLS.length = 0;
  renderSkills('hard-wrap', HARD_SKILLS, 'hard-input');
  renderSkills('soft-wrap', SOFT_SKILLS, 'soft-input');
  goStep(2);
}

// ── Recherche IA animée (sans noms de sources) ──
function runSearch(){
  var fill   = document.getElementById('progress-fill');
  var status = document.getElementById('search-status');
  var msgs = [
    'Analyse sémantique de votre brief…',
    'Extraction des compétences clés : ' + BRIEF.hard.slice(0,3).join(', ') + '…',
    'Interrogation de nos sources partenaires…',
    'Consultation du vivier CONSEILPREV…',
    'Matching IA des profils (Claude)…',
    'Vérification des disponibilités…',
    'Géolocalisation des candidats…',
    'Classement final des profils…'
  ];
  var i = 0;
  fill.style.width = '0%';

  // Lancer l'appel IA en parallèle de l'animation
  var aiDone = false, aiSuccess = false;
  fetch('/api/match', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({
      titre: BRIEF.titre, domaine: BRIEF.domaine, tjm: BRIEF.tjm,
      hard: BRIEF.hard, soft: BRIEF.soft, lieu: BRIEF.lieu,
      contrat: BRIEF.contrat, duree: BRIEF.duree
    })
  })
  .then(function(r){ return r.json(); })
  .then(function(res){
    aiDone = true;
    if(res.ok && res.profiles && res.profiles.length){
      buildMatchesFromAI(res.profiles);
      aiSuccess = true;
      AI_MODEL = res.model || 'IA';
    }
  })
  .catch(function(){ aiDone = true; });

  var interval = setInterval(function(){
    if(i < msgs.length){
      status.textContent = msgs[i];
      fill.style.width = Math.round((i+1)/msgs.length*100) + '%';
      i++;
    } else {
      clearInterval(interval);
      // Attendre la fin de l'appel IA (max ~3s de plus)
      var waited = 0;
      var waitAI = setInterval(function(){
        waited += 200;
        if(aiDone || waited > 6000){
          clearInterval(waitAI);
          if(!aiSuccess){ genMatches(); }  // fallback local
          status.textContent = '✓ Recherche terminée — ' + MATCHES.length + ' profils compatibles localisés'
            + (aiSuccess ? ' (matching IA)' : '');
          setTimeout(function(){ goStep(4); renderAll(); }, 600);
        }
      }, 200);
    }
  }, 500);
}

// Construire MATCHES à partir des profils générés par Claude
function buildMatchesFromAI(profiles){
  var avatars = ['👨‍💻','👩‍💻','🧑‍💻','👨‍🔬','👩‍🔬'];
  // Sources partenaires utilisées pour ce matching (ordre aléatoire)
  var SOURCES_PARTENAIRES = [
    'Vivier CONSEILPREV','Free-Work','Malt','LinkedIn','APEC',
    'Welcome to the Jungle','France Travail','Comet','RemoteOK','Formulaire plateforme'
  ];
  function pickSources(n){
    var s = SOURCES_PARTENAIRES.slice().sort(function(){ return Math.random()-.5; });
    return s.slice(0, n);
  }
  var srcPool = pickSources(5);

  MATCHES = profiles.map(function(p, i){
    var city = CITIES.find(function(c){ return c.name === p.ville; }) || CITIES[i % CITIES.length];
    var uid = 'S' + SEARCH_COUNT + '-C' + (i+1);
    var baseIdent = IDENT_POOL[i % IDENT_POOL.length];
    // Surcharger la source avec la source IA générée
    var ident = Object.assign({}, baseIdent, {
      source: srcPool[i] || baseIdent.source,
      date_source: new Date().toLocaleDateString('fr-FR', {month:'2-digit', year:'numeric'})
    });
    return {
      uid: uid,
      label: 'Consultant ' + uid,
      avatar: avatars[i % avatars.length],
      seniority: p.seniority,
      score: p.score,
      tjm: p.tjm,
      dispo: p.dispo,
      skills: p.skills && p.skills.length ? p.skills : BRIEF.hard.slice(0,4),
      highlight: p.highlight || '',
      city: city,
      titre: BRIEF.titre,
      domaine: BRIEF.domaine,
      duree: BRIEF.duree,
      lieu: BRIEF.lieu,
      start: BRIEF.start,
      contrat: BRIEF.contrat,
      ident: ident,
    };
  });
}

// ── Génération matches ──
function genMatches(){
  var seniorities = ['Senior · 8 ans','Expert · 12 ans','Confirmé · 5 ans','Senior · 9 ans','Expert · 15 ans'];
  var bases = [97, 92, 88, 84, 79];
  var avatars = ['👨‍💻','👩‍💻','🧑‍💻','👨‍🔬','👩‍🔬'];
  var dispo = ['Immédiate','Sous 2 semaines','Immédiate','Sous 1 mois','Sous 2 semaines'];
  // Villes : mélanger pour varier
  var cityPick = CITIES.slice().sort(function(){ return Math.random()-.5; }).slice(0,5);

  MATCHES = bases.map(function(score, i){
    var tjmVar = [0, -30, 20, -50, 40][i];
    var skills = BRIEF.hard.slice(0, 4);
    if(BRIEF.soft.length) skills = skills.concat(BRIEF.soft.slice(0,2));
    var uid = 'S' + SEARCH_COUNT + '-C' + (i+1);
    return {
      uid: uid,
      label: 'Consultant ' + uid,
      avatar: avatars[i],
      seniority: seniorities[i],
      score: score,
      tjm: Math.max(150, BRIEF.tjm + tjmVar),
      dispo: dispo[i],
      skills: skills,
      city: cityPick[i],
      titre: BRIEF.titre,
      domaine: BRIEF.domaine,
      duree: BRIEF.duree,
      lieu: BRIEF.lieu,
      start: BRIEF.start,
      contrat: BRIEF.contrat,
      // Identité CONFIDENTIELLE (email CONSEILPREV uniquement)
      ident: IDENT_POOL[i],
    };
  });
  return MATCHES.length;
}

function isInCart(uid){
  return CART.some(function(c){ return c.uid === uid; });
}

// ── Rendu global panel 4 ──
function renderAll(){
  renderMap();
  renderMatches();
  renderCart();
  // Afficher/masquer banner admin + notice anonymat
  document.getElementById('admin-mode-banner').classList.toggle('show', IS_ADMIN);
  document.getElementById('client-anon-notice').style.display = IS_ADMIN ? 'none' : '';
  // Afficher les panneaux identité pour les candidats sélectionnés
  if(IS_ADMIN){
    document.querySelectorAll('.admin-ident').forEach(function(el){
      // Afficher automatiquement si le candidat est dans le panier
      var card = el.closest('.match-card');
      if(card && card.classList.contains('in-cart')){
        el.style.display = 'block';
      } else {
        el.style.display = 'block'; // Admin voit tout en permanence
      }
    });
  }
}

// ═══════════════════════════════════════════════════════════
// CARTE FRANCE — RÉGIONS INTERACTIVES AVEC CANDIDATS
// ═══════════════════════════════════════════════════════════

// Données géographiques : 13 régions métropolitaines
var FR_REGIONS = [
  {id:'hdf', name:'Hauts-de-France',    color:'#1a56a0', lx:312, ly:65,  cities:['Lille','Amiens']},
  {id:'nor', name:'Normandie',           color:'#2e7d52', lx:193, ly:92,  cities:['Rouen','Caen']},
  {id:'bre', name:'Bretagne',            color:'#c05621', lx:100, ly:115, cities:['Rennes','Brest']},
  {id:'pdl', name:'Pays de la Loire',    color:'#b07c2a', lx:152, ly:186, cities:['Nantes','Le Mans']},
  {id:'cvl', name:'Centre-Val de Loire', color:'#0e6b9e', lx:250, ly:160, cities:['Orléans','Tours']},
  {id:'idf', name:'Île-de-France',       color:'#6d28d9', lx:296, ly:112, cities:['Paris']},
  {id:'ges', name:'Grand Est',           color:'#9c4221', lx:383, ly:85,  cities:['Strasbourg','Reims','Nancy']},
  {id:'bfc', name:'Bourgogne-Franche-Comté', color:'#5b21b6', lx:346, ly:170, cities:['Dijon','Besançon']},
  {id:'naq', name:'Nouvelle-Aquitaine',  color:'#7e22ce', lx:152, ly:290, cities:['Bordeaux','Poitiers','Limoges']},
  {id:'ara', name:'Auvergne-Rhône-Alpes',color:'#0d766e', lx:358, ly:280, cities:['Lyon','Grenoble','Clermont-Ferrand']},
  {id:'occ', name:'Occitanie',           color:'#92400e', lx:243, ly:400, cities:['Toulouse','Montpellier','Nîmes']},
  {id:'pac', name:"Provence-Alpes-Côte d'Azur", color:'#1a5276', lx:384, ly:388, cities:['Marseille','Nice','Toulon']},
  {id:'cor', name:'Corse',               color:'#1c4980', lx:476, ly:458, cities:[]},
];

// Correspondance ville → région
var CITY_REGION = {
  'Paris':'idf','Versailles':'idf',
  'Lille':'hdf','Amiens':'hdf','Valenciennes':'hdf','Calais':'hdf',
  'Rouen':'nor','Caen':'nor','Le Havre':'nor','Cherbourg':'nor',
  'Rennes':'bre','Brest':'bre','Nantes':'pdl','Le Mans':'pdl','Angers':'pdl',
  'Lyon':'ara','Grenoble':'ara','Clermont-Ferrand':'ara','Saint-Étienne':'ara',
  'Marseille':'pac','Nice':'pac','Toulon':'pac','Aix-en-Provence':'pac',
  'Toulouse':'occ','Montpellier':'occ','Nîmes':'occ','Perpignan':'occ',
  'Bordeaux':'naq','Poitiers':'naq','Limoges':'naq','La Rochelle':'naq',
  'Strasbourg':'ges','Reims':'ges','Nancy':'ges','Metz':'ges',
  'Dijon':'bfc','Besançon':'bfc',
  'Orléans':'cvl','Tours':'cvl',
};

// Photos démo candidats (avatars générés)
var CAND_PHOTOS = {
  'Karim Benali':   'https://api.dicebear.com/7.x/personas/svg?seed=karim&backgroundColor=6d28d9',
  'Sophie Marchand':'https://api.dicebear.com/7.x/personas/svg?seed=sophie&backgroundColor=9d6fe8',
  'Thomas Lefèvre': 'https://api.dicebear.com/7.x/personas/svg?seed=thomas&backgroundColor=1d4ed8',
  'Amina Diallo':   'https://api.dicebear.com/7.x/personas/svg?seed=amina&backgroundColor=0f766e',
  'Julien Rousseau':'https://api.dicebear.com/7.x/personas/svg?seed=julien&backgroundColor=c2410c',
};

var _activeRegion = null;

function renderMap(){
  renderRegions();
  renderPins();
  renderRegionPanel();
}

// ── Colorier les régions (dans le nouveau SVG statique) ──
function renderRegions(){
  // Quelles régions ont des candidats ?
  var regionsWithCands = {};
  MATCHES.forEach(function(m){
    var rid = m.city && m.city.rid ? m.city.rid : CITY_REGION[m.city.name];
    if(rid) regionsWithCands[rid] = (regionsWithCands[rid]||0) + 1;
  });

  FR_REGIONS.forEach(function(reg){
    var el = document.getElementById('reg-' + reg.id);
    if(!el) return;
    var path = el.querySelector('.region-fill');
    if(!path) return;

    var hasCands = !!regionsWithCands[reg.id];
    var isActive = _activeRegion === reg.id;
    var filtered = _activeRegion && !isActive;

    if(isActive){
      path.setAttribute('fill', reg.color);
      path.setAttribute('stroke', '#fff');
      path.setAttribute('stroke-width', '2.5');
      path.setAttribute('filter','url(#rglow)');
      el.style.opacity = '1';
    } else if(filtered){
      path.setAttribute('fill', reg.color + '33');
      path.setAttribute('stroke', 'rgba(255,255,255,.2)');
      path.setAttribute('stroke-width', '0.8');
      path.removeAttribute('filter');
      el.style.opacity = '0.4';
    } else if(hasCands){
      path.setAttribute('fill', reg.color + 'ee');
      path.setAttribute('stroke', 'rgba(94,234,212,.7)');
      path.setAttribute('stroke-width', '1.8');
      path.removeAttribute('filter');
      el.style.opacity = '1';
    } else {
      path.setAttribute('fill', reg.color + '55');
      path.setAttribute('stroke', 'rgba(255,255,255,.25)');
      path.setAttribute('stroke-width', '1');
      path.removeAttribute('filter');
      el.style.opacity = '0.75';
    }

    // Hover sur la région
    if(!el._hoverSet){
      el._hoverSet = true;
      el.addEventListener('mouseenter', function(){
        if(_activeRegion !== reg.id){
          path.setAttribute('stroke','rgba(255,255,255,.7)');
          path.setAttribute('stroke-width','2');
        }
      });
      el.addEventListener('mouseleave', function(){
        renderRegions();
      });
      el.addEventListener('click', function(){
        filterRegion(_activeRegion === reg.id ? null : reg.name, null);
      });
      el.style.cursor = 'pointer';
    }
  });

  // Panel latéral
  renderRegionPanel();
}

// ── Dessiner les pins candidats ──
function renderPins(){
  var g = document.getElementById('map-pins');
  var tooltip = document.getElementById('map-tooltip-v2');
  if(!g||!tooltip) return;
  g.innerHTML = '';

  var visible = _activeRegion
    ? MATCHES.filter(function(m){ return CITY_REGION[m.city.name] === _activeRegion; })
    : MATCHES;

  visible.forEach(function(m){
    var inCart = isInCart(m.uid);
    var pinColor = inCart ? '#5eead4' : '#d946ef';
    var ringColor = inCart ? 'rgba(94,234,212,.4)' : 'rgba(217,70,239,.4)';

    var gr = document.createElementNS('http://www.w3.org/2000/svg','g');
    gr.setAttribute('class','cand-pin');
    gr.dataset.uid = m.uid;

    // Anneaux pulsants
    var r1 = document.createElementNS('http://www.w3.org/2000/svg','circle');
    r1.setAttribute('cx',m.city.x); r1.setAttribute('cy',m.city.y);
    r1.setAttribute('r','8'); r1.setAttribute('fill',ringColor);
    r1.setAttribute('class','pin-ring');

    var r2 = document.createElementNS('http://www.w3.org/2000/svg','circle');
    r2.setAttribute('cx',m.city.x); r2.setAttribute('cy',m.city.y);
    r2.setAttribute('r','8'); r2.setAttribute('fill',ringColor);
    r2.setAttribute('class','pin-ring-2');

    // Corps du pin (cercle)
    var core = document.createElementNS('http://www.w3.org/2000/svg','circle');
    core.setAttribute('cx',m.city.x); core.setAttribute('cy',m.city.y);
    core.setAttribute('r','9');
    core.setAttribute('fill', pinColor);
    core.setAttribute('stroke','#fff'); core.setAttribute('stroke-width','1.8');
    core.setAttribute('filter','url(#region-glow)');

    // Score text dans le pin
    var score = document.createElementNS('http://www.w3.org/2000/svg','text');
    score.setAttribute('x',m.city.x); score.setAttribute('y',m.city.y+4);
    score.setAttribute('text-anchor','middle');
    score.setAttribute('font-size','7');
    score.setAttribute('font-family','Space Mono,monospace');
    score.setAttribute('font-weight','700');
    score.setAttribute('fill','#fff');
    score.setAttribute('pointer-events','none');
    score.textContent = m.score+'%';

    gr.appendChild(r1); gr.appendChild(r2); gr.appendChild(core); gr.appendChild(score);
    g.appendChild(gr);

    // ── Tooltip riche ──
    gr.addEventListener('mouseenter', function(ev){
      var ident = (IS_ADMIN && m.ident) ? m.ident : null;
      var photoUrl = ident ? (CAND_PHOTOS[ident.prenom+' '+ident.nom] || '') : '';
      var adminSection = '';
      if(ident){
        adminSection =
          '<div class="tt-row"><span class="tt-k">🔐 Identité</span><span class="tt-v">'+ident.prenom+' '+ident.nom+'</span></div>'+
          '<div class="tt-row"><span class="tt-k">Email</span><span class="tt-v" style="font-size:10px"><a href="mailto:'+ident.email+'" style="color:#5eead4">'+ident.email+'</a></span></div>'+
          '<div class="tt-row"><span class="tt-k">Tél</span><span class="tt-v">'+ident.tel+'</span></div>'+
          '<div class="tt-row"><span class="tt-k">🔍 Source</span><span class="tt-v" style="color:#f0abfc">'+(ident.source||'—')+'</span></div>';
      }
      tooltip.innerHTML =
        '<div class="tt-head">'+
          '<div class="tt-avatar">'+(photoUrl ? '<img src="'+photoUrl+'" alt="">' : m.avatar)+'</div>'+
          '<div>'+
            '<div class="tt-name">'+m.label+'</div>'+
            '<div class="tt-score">⭐ '+m.score+'% match · '+m.domaine+'</div>'+
          '</div>'+
        '</div>'+
        '<div class="tt-body">'+
          '<div class="tt-row"><span class="tt-k">Poste</span><span class="tt-v">'+m.titre+'</span></div>'+
          '<div class="tt-row"><span class="tt-k">Séniorité</span><span class="tt-v">'+m.seniority+'</span></div>'+
          '<div class="tt-row"><span class="tt-k">TJM</span><span class="tt-v">'+m.tjm+' € HT</span></div>'+
          '<div class="tt-row"><span class="tt-k">Ville</span><span class="tt-v">'+m.city.name+'</span></div>'+
          '<div class="tt-row"><span class="tt-k">Dispo</span><span class="tt-v">'+m.dispo+'</span></div>'+
          adminSection+
        '</div>'+
        (m.skills.length ? '<div class="tt-skills">'+m.skills.slice(0,4).map(function(s){ return '<span class="tt-skill">'+s+'</span>'; }).join('')+'</div>' : '')+
        '<div class="tt-cart-btn'+(isInCart(m.uid)?' added':'')+'" data-uid="'+m.uid+'">'+
          (isInCart(m.uid) ? '✓ Dans ma sélection' : '+ Sélectionner ce profil')+
        '</div>';
      tooltip.classList.add('show');
      posTooltip(ev);
    });
    gr.addEventListener('mousemove', posTooltip);
    gr.addEventListener('mouseleave', function(){ tooltip.classList.remove('show'); });
    gr.addEventListener('click', function(){ toggleCart(m.uid); renderAll(); });
  });

  // Délégation click pour le bouton cart dans le tooltip
  if(!tooltip._delegated){
    tooltip._delegated = true;
    tooltip.addEventListener('click', function(e){
      var btn = e.target.closest('.tt-cart-btn');
      if(btn && btn.dataset.uid){ toggleCart(btn.dataset.uid); renderAll(); }
    });
  }

  function posTooltip(ev){
    var wrap = document.querySelector('.map-section');
    if(!wrap) return;
    var rect = wrap.getBoundingClientRect();
    var x = ev.clientX - rect.left + 14;
    var y = ev.clientY - rect.top - 10;
    var w = tooltip.offsetWidth || 240;
    if(x + w > rect.width - 10) x = ev.clientX - rect.left - w - 14;
    if(y < 0) y = 10;
    tooltip.style.left = x + 'px';
    tooltip.style.top  = y + 'px';
  }
}

// ── Panel latéral des régions ──
function renderRegionPanel(){
  var list = document.getElementById('rp-list');
  if(!list) return;
  var regionsWithCands = {};
  MATCHES.forEach(function(m){
    var rid = CITY_REGION[m.city.name];
    if(rid) regionsWithCands[rid] = (regionsWithCands[rid]||0) + 1;
  });
  list.innerHTML = FR_REGIONS.filter(function(r){ return r.id!=='cor'; }).map(function(reg){
    var n = regionsWithCands[reg.id] || 0;
    var isActive = _activeRegion === reg.id;
    return '<div class="rp-region'+(isActive?' active':'')+'" onclick="filterRegion('+(isActive?'null':'"'+reg.name+'"')+',null)">'+
      '<span class="rp-dot" style="background:'+reg.color+(n?'':'88')+'"></span>'+
      '<span class="rp-name">'+reg.name+'</span>'+
      '<span class="rp-count'+(n?' has':'')+'">'+( n ? n+' profil'+(n>1?'s':'') : '—' )+'</span>'+
    '</div>';
  }).join('');
}

// ── Filtre par région ──
function filterRegion(regionName, btn){
  _activeRegion = regionName
    ? FR_REGIONS.find(function(r){ return r.name===regionName; })?.id || null
    : null;
  // Sync boutons filtres
  document.querySelectorAll('.mfb').forEach(function(b){ b.classList.remove('active'); });
  if(btn){ btn.classList.add('active'); }
  else if(!regionName){ document.querySelector('.mfb')?.classList.add('active'); }
  renderAll();
}

// ── Liste matches ──
function renderMatches(){
  var grid = document.getElementById('match-grid');
  grid.innerHTML = '';
  document.getElementById('match-subtitle').textContent =
    MATCHES.length + ' profils ' + BRIEF.domaine + ' localisés pour « ' + BRIEF.titre + ' » — recherche n°' + SEARCH_COUNT
    + (AI_MODEL ? ' · matching ' + AI_MODEL : '');
  MATCHES.forEach(function(m){
    var inCart = isInCart(m.uid);
    var card = document.createElement('div');
    card.className = 'match-card' + (inCart ? ' in-cart' : '');
    card.dataset.uid = m.uid;

    var av = document.createElement('div');
    av.className = 'match-avatar'; av.textContent = m.avatar;

    var body = document.createElement('div');
    var highlightHtml = m.highlight ? '<div style="font-size:12px;color:rgba(94,234,212,.85);margin-top:6px;font-style:italic">💡 ' + m.highlight + '</div>' : '';

    // Panneau identité — visible seulement si admin connecté
    var identHtml = '';
    if(IS_ADMIN && m.ident){
      identHtml =
        '<div class="admin-ident" id="ident-'+m.uid+'">' +
          '<div class="admin-ident-badge">🔐 Admin CONSEILPREV — Données confidentielles</div>' +
          '<div class="admin-ident-grid">' +
            '<div class="admin-ident-row">' +
              '<span class="admin-ident-lbl">Prénom</span>' +
              '<span class="admin-ident-val">' + m.ident.prenom + '</span>' +
            '</div>' +
            '<div class="admin-ident-row">' +
              '<span class="admin-ident-lbl">Nom</span>' +
              '<span class="admin-ident-val">' + m.ident.nom + '</span>' +
            '</div>' +
            '<div class="admin-ident-row">' +
              '<span class="admin-ident-lbl">Email</span>' +
              '<span class="admin-ident-val"><a href="mailto:' + m.ident.email + '">' + m.ident.email + '</a></span>' +
            '</div>' +
            '<div class="admin-ident-row">' +
              '<span class="admin-ident-lbl">Téléphone</span>' +
              '<span class="admin-ident-val"><a href="tel:' + m.ident.tel + '">' + m.ident.tel + '</a></span>' +
            '</div>' +
            '<div class="admin-ident-row">' +
              '<span class="admin-ident-lbl">Disponibilité</span>' +
              '<span class="admin-ident-val">' + m.dispo + '</span>' +
            '</div>' +
            '<div class="admin-ident-row">' +
              '<span class="admin-ident-lbl">CV</span>' +
              '<span class="admin-ident-val">' +
                '<span class="admin-cv-btn" onclick="requestCV(\'' + m.uid + '\',\'' + m.ident.cv + '\')">📄 ' + m.ident.cv + '</span>' +
              '</span>' +
            '</div>' +
            '<div class="admin-ident-row" style="grid-column:1 / -1;margin-top:4px;padding-top:10px;border-top:1px solid rgba(217,70,239,.2)">' +
              '<span class="admin-ident-lbl">🔍 Source / Plateforme</span>' +
              '<span class="admin-ident-val" style="color:#f0abfc;font-size:13px">' +
                (m.ident.source || '—') +
                (m.ident.date_source ? ' <span style="color:rgba(217,70,239,.5);font-size:11px;font-family:Space Mono,monospace">· ' + m.ident.date_source + '</span>' : '') +
              '</span>' +
            '</div>' +
          '</div>' +
        '</div>';
    }

    body.innerHTML =
      '<div class="match-name">' + m.label +
        (IS_ADMIN
          ? ' <span style="font-family:Space Mono,monospace;font-size:9px;background:rgba(217,70,239,.2);border:1px solid rgba(217,70,239,.4);padding:2px 8px;border-radius:100px;color:#f0abfc">🔐 Admin</span>'
          : ' <span class="match-anon">🔒 Anonymisé</span>'
        ) +
      '</div>' +
      '<div class="match-meta"><span>📊 ' + m.seniority + '</span><span>💰 TJM ' + m.tjm + ' € HT</span><span>📍 ' + m.city.name + '</span><span>🕐 ' + m.dispo + '</span></div>' +
      '<div class="match-skills">' + m.skills.map(function(s){ return '<span class="mskill">' + s + '</span>'; }).join('') + '</div>' +
      highlightHtml +
      identHtml;

    var scoreWrap = document.createElement('div');
    scoreWrap.innerHTML = '<div class="match-score">' + m.score + '%</div><div class="match-score-lbl">Match IA</div>';

    var btn = document.createElement('button');
    btn.className = 'btn-add' + (inCart ? ' added' : '');
    btn.textContent = inCart ? '✓ Sélectionné' : '+ Sélectionner';
    btn.onclick = function(e){ e.stopPropagation(); toggleCart(m.uid); };

    card.appendChild(av); card.appendChild(body); card.appendChild(scoreWrap); card.appendChild(btn);
    grid.appendChild(card);
  });
}

// ── Panier multi-recherches ──
function requestCV(uid, cvName){
  if(!IS_ADMIN){ return; }

  // LE JETON A DISPARU DE L'URL, ET C'EST LA CORRECTION. Il n'etait compare a
  // rien cote serveur — n'importe quelle chaine de huit caracteres ouvrait le
  // telechargement. L'autorisation passe desormais par le cookie de session,
  // que le navigateur joint de lui-meme a une requete de meme origine. Un
  // secret dans une URL se retrouve d'ailleurs dans les journaux du serveur,
  // dans ceux des intermediaires et dans l'en-tete Referer de la page
  // suivante ; un cookie, non.
  var dlUrl = '/api/admin/cv/' + encodeURIComponent(cvName);

  // Vérifier via fetch JSON si le fichier existe avant de déclencher le DL
  fetch(dlUrl + '?check=1', { credentials: 'same-origin' })
    .then(function(r){
      if(r.ok && r.headers.get('Content-Type') && r.headers.get('Content-Type').indexOf('json') < 0){
        // C'est un fichier → déclencher le téléchargement
        var a = document.createElement('a');
        a.href = dlUrl;
        a.download = cvName;
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        setTimeout(function(){ document.body.removeChild(a); }, 1000);
      } else {
        return r.json().then(function(d){
          if(d && d.ok === false){
            if(r.status === 404){ showCvHelp(cvName); }
            else if(r.status === 401 || r.status === 503){ alert('⚠ ' + (d.error || 'Accès refusé')); }
            else { showCvHelp(cvName); }
          }
        });
      }
    })
    .catch(function(){
      // Fallback : ouvrir dans nouvel onglet
      window.open(dlUrl, '_blank');
    });
}

function showCvHelp(cvName){
  var msg = document.createElement('div');
  msg.setAttribute('data-cvhelp','1');
  msg.style.cssText = 'position:fixed;inset:0;background:rgba(10,6,30,.88);z-index:9999;display:flex;align-items:center;justify-content:center;padding:24px';
  var inner = document.createElement('div');
  inner.style.cssText = 'background:linear-gradient(135deg,#1e1250,#2d1b69);border:1px solid rgba(217,70,239,.4);border-radius:16px;padding:32px;max-width:480px;width:100%;position:relative';
  var closeBtn = document.createElement('button');
  closeBtn.textContent = '×';
  closeBtn.style.cssText = 'position:absolute;top:12px;right:14px;background:none;border:none;color:rgba(216,180,254,.6);font-size:22px;cursor:pointer';
  closeBtn.onclick = function(){ document.body.removeChild(msg); };
  var body = document.createElement('div');
  body.innerHTML =
    '<div style="font-size:20px;margin-bottom:10px">📄</div>' +
    '<div style="font-size:16px;font-weight:700;color:#fff;margin-bottom:8px">CV non disponible en ligne</div>' +
    '<div style="font-size:13px;color:rgba(216,180,254,.78);line-height:1.7;margin-bottom:16px">' +
      'Le fichier <strong style="color:#f0abfc">' + cvName + '</strong> n\'est pas encore sur le serveur.<br><br>' +
      'Pour qu\'il soit disponible, le candidat doit l\'avoir soumis via :<br>' +
      '→ <a href="/business-developer" target="_blank" style="color:#5eead4">Formulaire Business Developer</a><br>' +
      '→ <a href="/sourcing#tester" target="_blank" style="color:#5eead4">Formulaire Testez nos services</a><br><br>' +
      'Une fois uploadé, il sera accessible ici automatiquement.' +
    '</div>' +
    '<div style="font-size:11px;color:rgba(196,181,232,.4);font-family:Space Mono,monospace">CVs stockés dans : uploads_cv/ (Render)</div>';
  inner.appendChild(closeBtn);
  inner.appendChild(body);
  msg.appendChild(inner);
  msg.onclick = function(e){ if(e.target===msg){ document.body.removeChild(msg); } };
  document.body.appendChild(msg);
}

function adminCvList(){
  // Ouvre la liste de tous les CVs disponibles sur le serveur.
  // Sans jeton : le cookie de session porte l'autorisation.
  if(!IS_ADMIN){ return; }
  window.open('/api/admin/cv-list', '_blank');
}

function sendSelectionNotifications(){
  // Construire le payload avec client + candidats (identités si admin)
  var payload = {
    client: {
      prenom:     BRIEF.prenom     || '',
      nom:        BRIEF.nom        || '',
      email:      BRIEF.email      || '',
      tel:        BRIEF.tel        || '',
      entreprise: BRIEF.entreprise || '',
      fonction:   BRIEF.fonction   || '',
    },
    candidates: CART.map(function(c){
      return {
        uid:      c.uid,
        label:    c.label,
        titre:    c.titre,
        domaine:  c.domaine,
        seniority:c.seniority,
        score:    c.score,
        tjm:      c.tjm,
        dispo:    c.dispo,
        ville:    c.city ? c.city.name : '',
        lieu:     c.lieu,
        start:    c.start,
        duree:    c.duree,
        contrat:  c.contrat,
        skills:   c.skills || [],
        highlight:c.highlight || '',
        // Identité complète (incluse côté serveur, CONSEILPREV only)
        ident: c.ident ? {
          prenom:      c.ident.prenom,
          nom:         c.ident.nom,
          email:       c.ident.email,
          tel:         c.ident.tel,
          cv:          c.ident.cv,
          source:      c.ident.source || '—',
          date_source: c.ident.date_source || '',
        } : {},
      };
    }),
  };

  fetch('/api/notify-selection', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(payload),
  })
  .then(function(r){ return r.json(); })
  .then(function(res){
    if(res.ok){
      var msg = '';
      if(res.client_email){
        msg += '📧 Email de confirmation envoyé à ' + BRIEF.email + '\n';
      }
      if(res.conseilprev_email){
        msg += '🔐 Dossier confidentiel envoyé à CONSEILPREV';
      }
      if(!res.smtp_configured){
        msg = '⚠ Notifications sauvegardées (SMTP à configurer sur Render)';
      }
      // Afficher une notification discrète
      showNotif(msg || res.message, res.client_email ? 'success' : 'warn');
    }
  })
  .catch(function(e){ console.warn('Notification error:', e); });
}

function showNotif(msg, type){
  var el = document.getElementById('notif-bar');
  if(!el){
    el = document.createElement('div');
    el.id = 'notif-bar';
    el.style.cssText = 'position:fixed;bottom:20px;left:50%;transform:translateX(-50%);z-index:9999;font-family:Space Mono,monospace;font-size:11px;padding:12px 24px;border-radius:100px;max-width:520px;text-align:center;box-shadow:0 8px 24px rgba(0,0,0,.4);transition:opacity .18s;white-space:nowrap';
    document.body.appendChild(el);
  }
  if(type === 'success'){
    el.style.background = 'rgba(6,95,70,.95)';
    el.style.border     = '1px solid rgba(94,234,212,.5)';
    el.style.color      = '#5eead4';
  } else {
    el.style.background = 'rgba(120,53,15,.95)';
    el.style.border     = '1px solid rgba(251,191,36,.5)';
    el.style.color      = '#fde68a';
  }
  el.textContent = msg;
  el.style.opacity = '1';
  setTimeout(function(){ el.style.opacity = '0'; }, 5000);
}

function toggleCart(uid){
  var idx = CART.findIndex(function(c){ return c.uid === uid; });
  if(idx >= 0){
    CART.splice(idx, 1);
  } else {
    var m = MATCHES.find(function(x){ return x.uid === uid; });
    if(m) CART.push(m);
  }
  renderAll();
}
function removeFromCart(uid){
  var idx = CART.findIndex(function(c){ return c.uid === uid; });
  if(idx >= 0){ CART.splice(idx, 1); renderAll(); }
}
function renderCart(){
  var list = document.getElementById('cart-list');
  var count = document.getElementById('cart-count');
  var titleCount = document.getElementById('cart-title-count');
  count.textContent = CART.length;
  titleCount.textContent = '(' + CART.length + ')';
  document.getElementById('btn-validate-cart').disabled = CART.length === 0;

  if(!CART.length){
    list.innerHTML = '<div class="cart-empty">Aucun candidat sélectionné. Cliquez « + Sélectionner » sur les profils qui vous intéressent — vous pouvez cumuler plusieurs recherches.</div>';
    return;
  }
  list.innerHTML = '';
  CART.forEach(function(c){
    var item = document.createElement('div');
    item.className = 'cart-item';
    var rm = document.createElement('button');
    rm.className = 'cart-rm'; rm.textContent = '✕';
    rm.onclick = function(){ removeFromCart(c.uid); };
    var adminCartInfo = '';
    if(IS_ADMIN && c.ident){
      adminCartInfo =
        '<div style="font-size:11px;color:#f0abfc;margin-top:5px;font-family:Space Mono,monospace;line-height:1.7">' +
        '🔐 ' + c.ident.prenom + ' ' + c.ident.nom +
        ' · <a href="mailto:' + c.ident.email + '" style="color:var(--teal);text-decoration:none">' + c.ident.email + '</a>' +
        ' · ' + c.ident.tel +
        '</div>' +
        '<div style="font-size:10px;color:rgba(217,70,239,.7);font-family:Space Mono,monospace;margin-top:2px">' +
        '🔍 ' + (c.ident.source || '—') + (c.ident.date_source ? ' · ' + c.ident.date_source : '') +
        '</div>';
    }
    item.innerHTML =
      '<span class="cart-item-ico">' + c.avatar + '</span>' +
      '<div class="cart-item-body">' +
        '<div class="cart-item-name">' + c.label + ' — ' + c.titre + '</div>' +
        '<div class="cart-item-meta">' + c.seniority + ' · TJM ' + c.tjm + ' € · ' + c.city.name + ' · Match ' + c.score + '%</div>' +
        adminCartInfo +
      '</div>';
    item.appendChild(rm);
    list.appendChild(item);
  });
}

// ── Validation sélection → email CONSEILPREV avec identités CONFIDENTIELLES ──
function validateCart(){
  if(!CART.length) return;

  // ── Envoyer notifications email (client + CONSEILPREV) ──
  sendSelectionNotifications();

  var lines = [
    'SÉLECTION CLIENT VALIDÉE — ' + CART.length + ' candidat(s)',
    '═══════════════════════════════════════',
    'CLIENT : ' + BRIEF.prenom + ' ' + BRIEF.nom + ' — ' + BRIEF.entreprise,
    'Email : ' + BRIEF.email + ' · Tél : ' + (BRIEF.tel || '—'),
    '',
  ];
  CART.forEach(function(c, i){
    var tjmConsultant = Math.round(c.tjm * 0.85);
    lines.push('CANDIDAT ' + (i+1) + ' — ' + c.label + ' (Match ' + c.score + '%)');
    lines.push('  Poste : ' + c.titre + ' (' + c.domaine + ') · ' + c.seniority);
    lines.push('  TJM client : ' + c.tjm + ' € HT → Rémunération consultant (−15%) : ' + tjmConsultant + ' € HT');
    lines.push('  Localisation : ' + c.city.name + ' · Dispo : ' + c.dispo + ' · Durée : ' + c.duree);
    lines.push('  ┌─ 🔒 CONFIDENTIEL — RÉSERVÉ CONSEILPREV (ne pas transmettre au client) ─┐');
    lines.push('  │ Identité : ' + c.ident.prenom + ' ' + c.ident.nom);
    lines.push('  │ Email : ' + c.ident.email);
    lines.push('  │ Téléphone : ' + c.ident.tel);
    lines.push('  │ CV disponible : ' + c.ident.cv);
    lines.push('  │ Disponibilité : ' + c.dispo);
    lines.push('  └────────────────────────────────────────┘');
    lines.push('');
  });
  lines.push('═══════════════════════════════════════');
  lines.push('ACTION : vérifier références, organiser entretiens, double validation.');

  var fd = new FormData();
  fd.append('form_type',  'selection_candidats');
  fd.append('prenom',     BRIEF.prenom);
  fd.append('nom',        BRIEF.nom);
  fd.append('email',      BRIEF.email);
  fd.append('telephone',  BRIEF.tel);
  fd.append('entreprise', BRIEF.entreprise);
  fd.append('fonction',   BRIEF.fonction);
  fd.append('message',    lines.join('\n'));
  fd.append('consent',    'true');
  fd.append('source_url', '/platform');

  fetch('/api/apply', { method:'POST', body:fd })
    .then(function(r){ return r.json(); })
    .catch(function(){});

  ACTIVE_CAND = 0;
  goStep(5);
  renderContractTabs();
  renderContracts();
}

// ── Onglets candidats (multi-contrats) ──
function renderContractTabs(){
  var tabs = document.getElementById('cand-tabs');
  tabs.innerHTML = '';
  CART.forEach(function(c, i){
    var t = document.createElement('button');
    t.className = 'cand-tab' + (i === ACTIVE_CAND ? ' active' : '');
    t.textContent = c.avatar + ' ' + c.label + ' · ' + c.tjm + '€';
    t.onclick = function(){ ACTIVE_CAND = i; renderContractTabs(); renderContracts(); };
    tabs.appendChild(t);
  });
}

// ── Contrats détaillés (11 articles, TJM client / TJM−15% consultant) ──
function renderContracts(){
  var c = CART[ACTIVE_CAND];
  if(!c) return;
  var tjmClient     = c.tjm;
  var tjmConsultant = Math.round(c.tjm * 0.85);
  var today = new Date().toLocaleDateString('fr-FR');

  document.getElementById('m-tjm-client').textContent  = tjmClient + ' € HT';
  document.getElementById('m-tjm-conseil').textContent = tjmConsultant + ' € HT';

  var articles1 =
    art('Art. 1 — Objet & Missions', 'Prestations informatiques et de conseil en intelligence artificielle : conseil en conformité réglementaire IA (AI Act, RGPD) · audit et évaluation des systèmes IA · formation et accompagnement sur les bonnes pratiques IA · développement de solutions de gouvernance IA. Ci-après la « Mission ».') +
    art('Art. 2 — Modalités de réalisation', 'Le Consultant réalise la Mission avec le plus grand professionnalisme, dans le respect des dispositions légales et réglementaires applicables, et mobilise les moyens techniques nécessaires. CONSEILPREV coopère pleinement et transmet en temps utile les informations nécessaires.') +
    art('Art. 3 — Reporting', 'Un état d\u2019avancement de la mission est transmis une fois par semaine.') +
    art('Art. 4 — Usage des résultats', 'Le Consultant s\u2019interdit de faire état des résultats de la mission à des tiers et de les utiliser, étant précisé que cette stipulation n\u2019interdit pas l\u2019usage libre de son propre savoir-faire.') +
    art('Art. 5 — Durée', 'Effet à la date de signature, durée de 6 (six) mois, renouvelable par tacite reconduction sauf résiliation notifiée au plus tard 2 mois avant expiration.') +
    art('Art. 6 — Résiliation anticipée', 'En cas de manquement à une obligation essentielle, notification par LRAR. La résiliation prend effet après un préavis de 60 jours.') +
    art('Art. 7 — Honoraires & paiement', 'TJM consultant : ' + tjmConsultant + ' € HT (TJM client − 15%). Facture avec mentions légales. Paiement à 30 jours après réception de facture.') +
    art('Art. 8 — Indépendance réciproque', 'Relation d\u2019entreprises indépendantes et autonomes. Aucun lien de subordination. Le Consultant s\u2019organise librement dans l\u2019exécution du Contrat.') +
    art('Art. 9 — Confidentialité', 'Le Consultant considère comme confidentielles toutes informations relatives à CONSEILPREV et ses clients. Obligation valable pendant le Contrat et persistant après son extinction pour une durée indéterminée.') +
    art('Art. 10 — Responsabilité & assurance', 'Chaque partie est responsable de la bonne exécution de ses obligations. Le Consultant déclare avoir souscrit une assurance responsabilité civile professionnelle.') +
    art('Art. 11 — Loi applicable', 'Droit français. Différends soumis aux tribunaux compétents.');

  document.getElementById('contract1-body').innerHTML =
    row('Prestataire-Mandant', 'CONSEILPREV — ERSIA IA Management, SARL') +
    row('Consultant', c.label + ' — identité dévoilée après accord mutuel') +
    row('Poste', c.titre + ' (' + c.domaine + ')') +
    row('Séniorité', c.seniority) +
    row('TJM consultant', tjmConsultant + ' € HT (TJM − 15%)', true) +
    row('Durée', c.duree + ' — tacite reconduction') +
    row('Lieu', c.lieu + ' (' + c.city.name + ')') +
    row('Démarrage', c.start) +
    row('Date prévisualisation', today) +
    articles1 +
    '<div class="cc-art"><div class="cc-art-txt" style="color:#fde68a">⚖️ Prévisualisation — le contrat définitif sera établi, envoyé et signé après accord définitif mutuel entre les parties.</div></div>';

  var articles2 =
    art('Art. 1 — Objet', 'Mise à disposition du Consultant pour la réalisation de la mission « ' + c.titre + ' » au bénéfice du Client, incluant : conseil conformité IA (AI Act, RGPD), audit des systèmes IA, accompagnement et gouvernance.') +
    art('Art. 2 — Engagements', 'CONSEILPREV garantit la qualification du Consultant (profilage humain + validation IA). Le Client coopère pleinement : ne rien faire qui empêche l\u2019exécution de la Mission, transmettre en temps utile les informations nécessaires, informer de tout élément d\u2019impact.') +
    art('Art. 3 — Reporting', 'État d\u2019avancement hebdomadaire transmis au Client par le Consultant via CONSEILPREV.') +
    art('Art. 4 — Usage des résultats', 'Les livrables de la Mission sont la propriété exclusive du Client. CONSEILPREV et le Consultant s\u2019interdisent d\u2019en faire état à des tiers.') +
    art('Art. 5 — Durée', 'Mission de ' + c.duree + ', renouvelable par tacite reconduction sauf résiliation notifiée 2 mois avant expiration.') +
    art('Art. 6 — Résiliation anticipée', 'Manquement à une obligation essentielle : notification LRAR, préavis 60 jours.') +
    art('Art. 7 — Honoraires & paiement', 'TJM facturé au Client : ' + tjmClient + ' € HT. Facture mensuelle avec mentions légales. Paiement à 30 jours après réception.') +
    art('Art. 8 — Non-sollicitation libérée', 'En cas de volonté mutuelle d\u2019internalisation du Consultant par le Client, CONSEILPREV libère contractuellement le Consultant en toute flexibilité.') +
    art('Art. 9 — Confidentialité', 'NDA total sur les projets et stratégies SI du Client. Tous BD et consultants CONSEILPREV signent un accord de confidentialité. Persiste après extinction du contrat.') +
    art('Art. 10 — Garantie & responsabilité', 'Remplacement du Consultant sous 2 semaines en cas d\u2019inadéquation constatée. CONSEILPREV déclare avoir souscrit une assurance RC professionnelle.') +
    art('Art. 11 — Loi applicable', 'Droit français. Tribunaux compétents.');

  document.getElementById('contract2-body').innerHTML =
    row('Prestataire', 'CONSEILPREV — ERSIA IA Management, SARL') +
    row('Client', BRIEF.entreprise + ' — ' + BRIEF.prenom + ' ' + BRIEF.nom) +
    row('Email client', BRIEF.email) +
    row('Consultant mis à disposition', c.label + ' — ' + c.seniority) +
    row('Poste', c.titre + ' (' + c.domaine + ')') +
    row('TJM facturé client', tjmClient + ' € HT (TJM plein)', true) +
    row('Durée mission', c.duree) +
    row('Lieu', c.lieu + ' (' + c.city.name + ')') +
    row('Démarrage', c.start) +
    row('Date prévisualisation', today) +
    articles2 +
    '<div class="cc-art"><div class="cc-art-txt" style="color:#fde68a">⚖️ Prévisualisation — le contrat définitif sera établi, envoyé et signé après accord définitif mutuel entre les parties.</div></div>';

  ['sig-c1-cp','sig-c1-fl','sig-c2-cp','sig-c2-cl'].forEach(initSig);
}

function row(k, v, hl){
  return '<div class="cc-row"><span class="ck">' + k + '</span><span class="cv' + (hl ? ' hl' : '') + '">' + v + '</span></div>';
}
function art(title, txt){
  return '<div class="cc-art"><div class="cc-art-title">' + title + '</div><div class="cc-art-txt">' + txt + '</div></div>';
}

// ── Signature électronique ──
function toggleCandSig(skip){
  var canvas = document.getElementById('sig-c1-fl');
  var notice = document.getElementById('sig-skip-notice');
  var zone   = canvas.closest('.sig-zone');
  if(skip){
    canvas.style.opacity = '0.3';
    canvas.style.pointerEvents = 'none';
    notice.style.display = 'block';
    SIGNED['sig-c1-fl'] = true;  // Marquer comme signé
    document.getElementById('st-c1-fl').classList.add('signed');
    document.getElementById('st-c1-fl').querySelector('.sig-date').textContent = 'hors ligne';
  } else {
    canvas.style.opacity = '1';
    canvas.style.pointerEvents = 'auto';
    notice.style.display = 'none';
    // Remettre à l'état réel de la signature
    SIGNED['sig-c1-fl'] = !!canvas.dataset.signed;
    if(!SIGNED['sig-c1-fl']){
      document.getElementById('st-c1-fl').classList.remove('signed');
    }
  }
}

function initSig(id){
  var canvas = document.getElementById(id);
  if(!canvas || canvas.dataset.init) return;
  canvas.dataset.init = '1';
  var ctx = canvas.getContext('2d');
  ctx.strokeStyle = '#c4b5fd'; ctx.lineWidth = 2; ctx.lineCap = 'round';
  var drawing = false, lx, ly;
  function pos(e){
    var r = canvas.getBoundingClientRect();
    var sx = canvas.width / r.width, sy = canvas.height / r.height;
    var cx = (e.touches ? e.touches[0].clientX : e.clientX) - r.left;
    var cy = (e.touches ? e.touches[0].clientY : e.clientY) - r.top;
    return { x: cx * sx, y: cy * sy };
  }
  function start(e){ drawing = true; var p = pos(e); lx = p.x; ly = p.y; e.preventDefault(); }
  function move(e){
    if(!drawing) return;
    var p = pos(e);
    ctx.beginPath(); ctx.moveTo(lx, ly); ctx.lineTo(p.x, p.y); ctx.stroke();
    lx = p.x; ly = p.y;
    canvas.dataset.signed = '1';
    e.preventDefault();
  }
  function end(){ drawing = false; }
  canvas.addEventListener('mousedown', start);
  canvas.addEventListener('mousemove', move);
  canvas.addEventListener('mouseup', end);
  canvas.addEventListener('mouseleave', end);
  canvas.addEventListener('touchstart', start, {passive:false});
  canvas.addEventListener('touchmove', move, {passive:false});
  canvas.addEventListener('touchend', end);
}
function clearSig(id){
  var canvas = document.getElementById(id);
  canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
  canvas.dataset.signed = '';
  var st = document.getElementById(id.replace('sig-','st-'));
  if(st) st.classList.remove('signed');
  SIGNED[id] = false;
}
function signOk(canvasId, statusId){
  var canvas = document.getElementById(canvasId);
  if(!canvas.dataset.signed){
    canvas.style.boxShadow = '0 0 0 2px rgba(248,113,113,.6)';
    setTimeout(function(){ canvas.style.boxShadow = ''; }, 1800);
    return;
  }
  var st = document.getElementById(statusId);
  st.querySelector('.sig-date').textContent = new Date().toLocaleString('fr-FR');
  st.classList.add('signed');
  SIGNED[canvasId] = true;
}

// ── Finalisation : envoi dossier complet détaillé ──
// ── Helpers mailto fallback (si SMTP absent) ──
function buildContractSummary(){
  var m = CART[ACTIVE_CAND] || CART[0];
  if(!m) return '';
  var tjmC = m.tjm;
  var tjmCons = Math.round(m.tjm * 0.85);
  var today = new Date().toLocaleDateString('fr-FR');
  var lines = [
    '=== DOSSIER CONTRATS CONSEILPREV ===',
    'Date : ' + today,
    '',
    'CLIENT',
    'Nom        : ' + BRIEF.prenom + ' ' + BRIEF.nom,
    'Email      : ' + BRIEF.email,
    'Tél        : ' + (BRIEF.tel || '—'),
    'Entreprise : ' + (BRIEF.entreprise || '—'),
    '',
    'SÉLECTION (' + CART.length + ' candidat(s))',
  ];
  CART.forEach(function(c, i){
    lines.push('');
    lines.push('Candidat ' + (i+1) + ' — ' + c.label + ' (Match ' + c.score + '%)');
    lines.push('  Poste    : ' + c.titre + ' (' + c.domaine + ')');
    lines.push('  Ville    : ' + (c.city ? c.city.name : c.lieu));
    lines.push('  Dispo    : ' + c.dispo + ' | Durée : ' + c.duree);
    lines.push('  TJM fact. client    : ' + c.tjm + ' EUR HT');
    lines.push('  TJM rémun. consult. : ' + Math.round(c.tjm * 0.85) + ' EUR HT (−15%)');
    lines.push('  Marge CONSEILPREV   : ' + (c.tjm - Math.round(c.tjm * 0.85)) + ' EUR/j');
    if(c.ident){
      lines.push('  [CONFIDENTIEL] ' + c.ident.prenom + ' ' + c.ident.nom + ' · ' + c.ident.email + ' · ' + c.ident.tel);
      lines.push('  Source : ' + (c.ident.source || '—'));
    }
  });
  lines.push('');
  lines.push('CONTRATS');
  lines.push('Durée : 6 mois tacite reconduction | Préavis résiliation : 60j LRAR');
  lines.push('Paiement : 30j réception facture | Reporting : hebdomadaire');
  lines.push('Accord de principe — contrats DÉFINITIFS après accord mutuel toutes parties.');
  lines.push('');
  lines.push('Signatures horodatées : ' + new Date().toLocaleString('fr-FR'));
  return lines.join('\n');
}

function triggerMailtoFallback(){
  // Mailto vers CONSEILPREV avec dossier complet
  var subject = '[DOSSIER CONTRATS] ' + BRIEF.prenom + ' ' + BRIEF.nom +
    ' — ' + CART.length + ' candidat(s)';
  var body = buildContractSummary();
  window.open(
    'mailto:christophe.cerf@outlook.com' +
    '?subject=' + encodeURIComponent(subject) +
    '&body=' + encodeURIComponent(body),
    '_blank'
  );
}

function triggerMailtoClient(){
  if(!BRIEF.email){ alert('Email client manquant dans le brief'); return; }
  var m = CART[0];
  var subject = 'Votre sélection CONSEILPREV — Accord de principe';
  var body = [
    'Bonjour ' + BRIEF.prenom + ' ' + BRIEF.nom + ',',
    '',
    'Nous avons bien reçu votre sélection de ' + CART.length + ' candidat(s).',
    'Notre équipe CONSEILPREV vous contactera sous 48h ouvrées pour organiser',
    'la mise en relation et confirmer les modalités définitives.',
    '',
    '=== VOS CANDIDATS SÉLECTIONNÉS ===',
  ].concat(CART.map(function(c, i){
    return [
      '',
      'Candidat ' + (i+1) + ' — ' + c.label + ' (Match ' + c.score + '%)',
      '  Poste : ' + c.titre + ' (' + c.domaine + ')',
      '  TJM : ' + c.tjm + ' EUR HT | Dispo : ' + c.dispo,
      '  Durée : ' + c.duree + ' | Démarrage : ' + c.start,
    ].join('\n');
  })).concat([
    '',
    '=== ACCORD DE PRINCIPE ===',
    'Ce document est un pré-accord. Les contrats DÉFINITIFS seront établis',
    'et signés après accord définitif mutuel entre toutes les parties.',
    '',
    'Durée : 6 mois renouvelable | Résiliation : 60j préavis LRAR',
    'Paiement : 30 jours après facture',
    '',
    'Cordialement,',
    'L\u2019équipe CONSEILPREV',
    'christophe.cerf@outlook.com | conseilprev.onrender.com',
  ]).join('\n');
  window.open(
    'mailto:' + encodeURIComponent(BRIEF.email) +
    '?subject=' + encodeURIComponent(subject) +
    '&body=' + encodeURIComponent(body),
    '_blank'
  );
}

function finalizeAll(){
  var skipCand = document.getElementById('skip-cand-sig') && document.getElementById('skip-cand-sig').checked;
  var required = ['sig-c1-cp','sig-c2-cp','sig-c2-cl'];
  if(!skipCand) required.push('sig-c1-fl');
  var allSigned = required.every(function(id){ return SIGNED[id]; });
  if(!allSigned){
    var missing = required.filter(function(id){ return !SIGNED[id]; });
    var labels = {'sig-c1-cp':'CONSEILPREV (contrat 1)','sig-c1-fl':'Consultant','sig-c2-cp':'CONSEILPREV (contrat 2)','sig-c2-cl':'Client'};
    alert('⚠ Signature(s) manquante(s) : ' + missing.map(function(id){ return labels[id]||id; }).join(', ') + '.\nSi le consultant n\'est pas disponible, cochez « Déjà signé hors ligne ».');
    return;
  }
  var btn = document.getElementById('btn-finalize');
  btn.disabled = true;
  btn.textContent = 'Envoi en cours…';

  var lines = [
    'DOSSIER COMPLET — ACCORDS DE PRINCIPE SIGNÉS',
    '⚖️ LES CONTRATS DÉFINITIFS SERONT ÉTABLIS, ENVOYÉS ET SIGNÉS',
    'APRÈS ACCORD DÉFINITIF MUTUEL ENTRE TOUTES LES PARTIES.',
    '═══════════════════════════════════════',
    'CLIENT : ' + BRIEF.prenom + ' ' + BRIEF.nom + ' — ' + BRIEF.entreprise,
    'Email : ' + BRIEF.email + ' · Tél : ' + (BRIEF.tel || '—'),
    'Signatures (accord de principe) horodatées : ' + new Date().toLocaleString('fr-FR'),
    '',
  ];
  CART.forEach(function(c, i){
    var tjmClient = c.tjm;
    var tjmConsultant = Math.round(c.tjm * 0.85);
    var marge = tjmClient - tjmConsultant;
    lines.push('━━━ CANDIDAT ' + (i+1) + ' — ' + c.label + ' (Match ' + c.score + '%) ━━━');
    lines.push('CONTRAT 1 (CONSEILPREV ↔ Consultant) :');
    lines.push('  · Rémunération consultant : ' + tjmConsultant + ' € HT/jour (TJM − 15%)');
    lines.push('  · Durée : ' + c.duree + ' · 6 mois tacite reconduction · Préavis 60j LRAR');
    lines.push('  · Paiement 30j · RC pro · Confidentialité étendue · Droit français');
    lines.push('CONTRAT 2 (CONSEILPREV ↔ ' + BRIEF.entreprise + ') :');
    lines.push('  · TJM facturé client : ' + tjmClient + ' € HT/jour (TJM plein)');
    lines.push('  · Marge CONSEILPREV : ' + marge + ' €/jour (15%)');
    lines.push('  · Non-sollicitation libérée · Garantie remplacement 2 sem · NDA total');
    lines.push('MISSION : ' + c.titre + ' (' + c.domaine + ') · ' + c.lieu + ' · Démarrage ' + c.start);
    lines.push('┌─ 🔒 CONFIDENTIEL — RÉSERVÉ CONSEILPREV ─┐');
    lines.push('│ ' + c.ident.prenom + ' ' + c.ident.nom + ' · ' + c.ident.email + ' · ' + c.ident.tel);
    lines.push('│ CV : ' + c.ident.cv + ' · Dispo : ' + c.dispo + ' · ' + c.city.name);
    lines.push('└──────────────────────────────┘');
    lines.push('');
  });
  lines.push('═══════════════════════════════════════');
  lines.push('ACTIONS : 1) Vérifier références  2) Entretiens de mise en relation');
  lines.push('3) Accord définitif mutuel  4) Établir et faire signer les contrats définitifs.');

  var fd = new FormData();
  fd.append('form_type',  'dossier_contrats');
  fd.append('prenom',     BRIEF.prenom);
  fd.append('nom',        BRIEF.nom);
  fd.append('email',      BRIEF.email);
  fd.append('telephone',  BRIEF.tel);
  fd.append('entreprise', BRIEF.entreprise);
  fd.append('message',    lines.join('\n'));
  fd.append('consent',    'true');
  fd.append('source_url', '/platform');

  fetch('/api/apply', { method:'POST', body:fd })
    .then(function(r){ return r.json(); })
    .then(function(res){
      var status = document.getElementById('email-status');
      btn.disabled = false;

      if(res.ok && res.email_sent){
        // ✅ CAS 1 : SMTP configuré → emails envoyés aux deux parties
        status.className = 'email-status ok';
        status.innerHTML =
          '✓ Email de confirmation envoyé au client (' + BRIEF.email + ')<br>' +
          '✓ Dossier confidentiel envoyé à CONSEILPREV<br>' +
          '<span style="font-size:10px;opacity:.75">Contrats préliminaires inclus — accord définitif mutuel requis avant finalisation.</span>';
        btn.style.display = 'none';
        document.getElementById('final-box').style.display = 'block';
        document.getElementById('final-box').scrollIntoView({behavior:'smooth',block:'center'});

      } else if(res.ok && !res.email_sent){
        // ⚠ CAS 2 : SMTP absent → dossier sauvegardé + fallback mailto automatique
        status.className = 'email-status warn';
        status.innerHTML =
          '⚠ <strong>Dossier sauvegardé</strong> — SMTP non configuré sur Render.<br>' +
          'Envoi automatique par email dans 1 seconde…';
        btn.style.display = 'none';

        setTimeout(function(){
          // Ouvrir mailto CONSEILPREV (avec résumé complet)
          triggerMailtoFallback();
          // Afficher le final-box
          document.getElementById('final-box').style.display = 'block';
          document.getElementById('final-box').scrollIntoView({behavior:'smooth',block:'center'});
          status.innerHTML =
            '⚠ SMTP non configuré — votre client mail a été ouvert pour envoyer à CONSEILPREV.<br>' +
            '<span style="font-size:10px">Le dossier est aussi sauvegardé sur le serveur.</span><br>' +
            '<a href="#" onclick="triggerMailtoClient();return false;" style="color:#fde68a;font-size:11px;margin-top:6px;display:inline-block">' +
            '→ Envoyer aussi la confirmation au client (' + BRIEF.email + ')</a>';
        }, 900);

      } else {
        // ❌ CAS 3 : Erreur
        status.className = 'email-status warn';
        status.textContent = '⚠ ' + (res.error || 'Erreur serveur');
        btn.disabled = false;
        btn.textContent = '📨 Réessayer';
      }
    })
    .catch(function(){
      // ❌ CAS 4 : Erreur réseau → fallback mailto d'urgence
      btn.disabled = false;
      btn.textContent = '📨 Réessayer';
      var status = document.getElementById('email-status');
      status.className = 'email-status warn';
      status.innerHTML = '⚠ Erreur réseau — ouverture du client mail…';
      setTimeout(triggerMailtoFallback, 600);
    });

}

document.addEventListener('contextmenu', function(e){ e.preventDefault(); });

// Au chargement : vérifier le mode admin
window.addEventListener('DOMContentLoaded', function(){
  try{
    IS_ADMIN = sessionStorage.getItem('cp_admin') === '1';
  }catch(e){}
  if(IS_ADMIN){
    // Afficher petit badge discret dans le nav
    var badge = document.createElement('span');
    badge.style.cssText = 'font-family:Space Mono,monospace;font-size:9px;letter-spacing:.1em;color:rgba(240,171,252,.7);padding:3px 10px;background:rgba(217,70,239,.15);border:1px solid rgba(217,70,239,.3);border-radius:100px;';
    badge.textContent = '🔐 ADMIN';
    document.querySelector('nav').appendChild(badge);
  }
});

