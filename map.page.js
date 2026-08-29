/* Extrait de map.html — 1 bloc(s) en ligne, dans leur ordre d'origine.
   Le HTML est servi en no-store : ce fichier, lui, obtient un ETag
   et répond 304 dès la deuxième visite. */

;/* ── bloc 1/1 ── */

/* Repli visible : sans Leaflet, on explique au lieu de laisser un ecran blanc. */
if (typeof L === 'undefined') {
  document.getElementById('map').innerHTML =
    '<div style="height:100%;display:flex;align-items:center;justify-content:center;'
  + 'padding:32px;font-family:Inter,system-ui,sans-serif;background:#F7F6F2">'
  + '<div style="max-width:440px;text-align:center">'
  + '<div style="font-size:34px;margin-bottom:14px">🗺️</div>'
  + '<div style="font-size:15px;font-weight:600;color:#1C1C1C;margin-bottom:8px">'
  + 'La carte n\u2019a pas pu se charger</div>'
  + '<p style="font-size:13px;color:#5B6472;line-height:1.6;margin-bottom:16px">'
  + 'Sa biblioth\u00e8que cartographique est servie par un domaine tiers '
  + '(unpkg.com) que votre r\u00e9seau ou votre navigateur n\u2019a pas pu joindre. '
  + 'Les donn\u00e9es, elles, sont intactes.</p>'
  + '<a href="/panorama#s-carte" style="display:inline-block;font-size:13px;font-weight:600;'
  + 'color:#fff;background:#0F3D6E;padding:9px 18px;border-radius:5px;text-decoration:none">'
  + 'Voir les m\u00eames juridictions dans le Panorama \u2192</a></div></div>';
  var b = document.getElementById('map-count');
  if (b) b.textContent = 'carte indisponible';
} else {
var map = L.map('map',{center:[38,15],zoom:2.4,minZoom:2,maxZoom:7,scrollWheelZoom:false});
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',{
  attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>',
  subdomains:'abcd',maxZoom:19
}).addTo(map);

/* ── Jeu de donnees complet (fallback si charge hors iframe / sans message du parent) ──
   Synchronise avec JURS dans sentinel.html (46 juridictions). */
var GEO = [
  {n:'Union européenne', c:'EU', r:'EU AI Act — Règlement 2024/1689 (transparence art. 50 depuis le 2 août 2026 ; haut risque annexe III au 2 décembre 2027)', s:9.2, lat:50.5, lng:15.0},
  {n:'Allemagne', c:'DE', r:'EU AI Act + loi nationale d application + BSI', s:8.8, lat:51.2, lng:10.4},
  {n:'France', c:'FR', r:'EU AI Act + Stratégie nationale IA + CNIL', s:8.5, lat:46.2, lng:2.2},
  {n:'Corée du Sud', c:'KR', r:'AI Basic Act — en vigueur depuis le 22 janvier 2026', s:8.3, lat:36.0, lng:127.9},
  {n:'Chine', c:'CN', r:'Generative AI Measures + AI Labeling Rules + amendements loi cybersécurité (1er janv. 2026)', s:8.2, lat:35.8, lng:104.2},
  {n:'Russie', c:'RU', r:'National AI Strategy + Digital Code', s:7.5, lat:61.5, lng:90.0},
  {n:'Espagne', c:'ES', r:'EU AI Act + AESIA (agence nationale de supervision IA)', s:7.3, lat:40.4, lng:-3.7},
  {n:'Singapour', c:'SG', r:'Cadre de gouvernance Agentic AI (1er mondial, janv. 2026) + AI Verify', s:7.0, lat:1.35, lng:103.8},
  {n:'Japon', c:'JP', r:'AI Promotion Act (mai 2025) + Hiroshima AI Process', s:6.8, lat:36.2, lng:138.2},
  {n:'Canada', c:'CA', r:'AIDA (Artificial Intelligence and Data Act) — en cours d adoption', s:6.5, lat:56.1, lng:-106.3},
  {n:'Suisse', c:'CH', r:'Convention-cadre IA Conseil de l Europe + LPD révisée', s:6.5, lat:46.8, lng:8.2},
  {n:'Kazakhstan', c:'KZ', r:'Loi sur l intelligence artificielle (interdit scoring social et manipulation)', s:6.3, lat:48.0, lng:66.9},
  {n:'Brésil', c:'BR', r:'PL 2338/2023 (cadre IA complet, vote final attendu) + LGPD', s:6.2, lat:-14.2, lng:-51.9},
  {n:'Royaume-Uni', c:'GB', r:'AI (Regulation) Bill au Parlement + approche sectorielle par régulateurs', s:6.0, lat:54.0, lng:-2.5},
  {n:'Turquie', c:'TR', r:'Projet de loi IA basé sur les risques (au Parlement) + KVKK', s:5.8, lat:38.9, lng:35.2},
  {n:'Australie', c:'AU', r:'AI Ethics Framework + Mandatory Guardrails (proposé)', s:5.7, lat:-25.3, lng:133.8},
  {n:'Inde', c:'IN', r:'AI Ethics and Accountability Bill (déc. 2025) + obligations MeitY étiquetage (fév. 2026)', s:5.5, lat:20.6, lng:78.9},
  {n:'Pays-Bas', c:'NL', r:'EU AI Act + régulateur algorithmique national renforcé', s:5.4, lat:52.1, lng:5.3},
  {n:'États-Unis', c:'US', r:'NIST AI RMF + lois étatiques (Colorado, Texas, Californie 2026) + EO 14179', s:5.2, lat:39.5, lng:-98.4},
  {n:'Arabie Saoudite', c:'SA', r:'PDPL + décisions d application SDAIA (48 en 2025) — approche souple', s:5.0, lat:24.0, lng:45.0},
  {n:'Maroc', c:'MA', r:'Loi protection des données (CNDP) + stratégie Maroc IA 2030', s:4.8, lat:31.8, lng:-7.1},
  {n:'Ghana', c:'GH', r:'Data Protection Act + National AI Strategy 10 ans (autorité IA responsable proposée)', s:4.7, lat:7.9, lng:-1.0},
  {n:'Kenya', c:'KE', r:'Data Protection Act contraignant + stratégie nationale IA', s:4.6, lat:-0.0, lng:37.9},
  {n:'Rwanda', c:'RW', r:'Politique nationale IA complète (référence Afrique) + loi protection données', s:4.5, lat:-1.9, lng:29.9},
  {n:'Afrique du Sud', c:'ZA', r:'National AI Policy Framework (projet) + loi protection données contraignante', s:4.4, lat:-28.5, lng:24.7},
  {n:'Malaisie', c:'MY', r:'National AI Roadmap 2021-2025 + PDPA', s:4.3, lat:4.2, lng:108.5},
  {n:'Géorgie', c:'GE', r:'Loi protection données alignée RGPD (nouvelle) + service de protection des données', s:4.2, lat:42.3, lng:43.4},
  {n:'Jordanie', c:'JO', r:'Feuille de route nationale IA (5 ans) + loi protection données récente', s:4.1, lat:30.6, lng:36.2},
  {n:'Sri Lanka', c:'LK', r:'1ère loi protection données d Asie du Sud + nouvelle stratégie nationale IA', s:4.0, lat:7.9, lng:80.8},
  {n:'Pakistan', c:'PK', r:'National AI Policy 2025 approuvée + loi protection données en projet', s:3.9, lat:30.4, lng:69.3},
  {n:'Uruguay', c:'UY', r:'Régime de protection des données mature + stratégie nationale IA et éthique', s:3.8, lat:-32.5, lng:-55.8},
  {n:'Oman', c:'OM', r:'Loi protection des données (MTCIT) + programme national IA', s:3.7, lat:21.5, lng:55.9},
  {n:'Costa Rica', c:'CR', r:'Loi protection des données + stratégie nationale IA soutenue par l UNESCO', s:3.6, lat:9.7, lng:-83.8},
  {n:'Israël', c:'IL', r:'Politique de régulation de l IA (2023) + loi protection données', s:3.5, lat:31.5, lng:35.0},
  {n:'Tunisie', c:'TN', r:'Loi protection des données de longue date + stratégies nationales IA successives', s:3.4, lat:33.9, lng:9.6},
  {n:'Qatar', c:'QA', r:'Stratégie nationale IA + lignes directrices éthiques + loi vie privée contraignante', s:3.3, lat:25.3, lng:51.2},
  {n:'Bahreïn', c:'BH', r:'Loi protection des données + politique IA secteur public en déploiement', s:3.2, lat:26.0, lng:50.5},
  {n:'Koweït', c:'KW', r:'Régulation protection des données (CITRA) + stratégie et cadre de gouvernance IA émergents', s:3.1, lat:29.3, lng:47.5},
  {n:'Chili', c:'CL', r:'National AI Policy + projet de loi IA', s:3.0, lat:-35.7, lng:-71.5},
  {n:'Philippines', c:'PH', r:'Stratégie nationale IA + feuille de route DTI + loi vie privée contraignante', s:2.9, lat:12.9, lng:121.8},
  {n:'Équateur', c:'EC', r:'Loi protection des données type RGPD + projets de loi IA en discussion', s:2.8, lat:-1.8, lng:-78.2},
  {n:'Émirats Arabes Unis', c:'AE', r:'UAE AI Strategy 2031 + AI Charter', s:2.8, lat:23.4, lng:53.8},
  {n:'Argentine', c:'AR', r:'Recommandation éthique IA + loi protection données (loi 25.326)', s:2.7, lat:-34.0, lng:-64.0},
  {n:'Cambodge / ASEAN', c:'KH', r:'Cadre régional ASEAN sur la gouvernance IA + lois nationales émergentes', s:2.5, lat:12.6, lng:104.9},
  {n:'Mexique', c:'MX', r:'Aucun cadre IA spécifique — initiatives sectorielles uniquement', s:2.4, lat:23.6, lng:-102.6},
  {n:'Nigéria', c:'NG', r:'National AI Strategy (projet 2024) + NDPA', s:2.3, lat:9.1, lng:8.7},
];

var markers = [];

function colorFor(s){ return s>=8?'#B83222':s>=5?'#C47C1A':'#2D7A47'; }
function labelFor(s){ return s>=8?'Très strict':s>=5?'Modéré':'Souple'; }

function renderMarkers(data){
  markers.forEach(function(m){ map.removeLayer(m); });
  markers = [];
  data.forEach(function(g){
    if(!g.lat && !g.lng) return;
    var mk = L.circleMarker([g.lat, g.lng], {
      radius: 6 + g.s*1.1, fillColor: colorFor(g.s),
      color: '#fff', weight: 1.5, fillOpacity: 0.85
    }).addTo(map);
    mk.bindPopup(
      '<div class="pn">' + g.n + '</div>'
      + '<div class="pr">' + g.r + '</div>'
      + '<div class="ps" style="color:' + colorFor(g.s) + '">' + g.s
      + '<span style="font-size:12px;color:#A8A8A8">/10</span></div>'
      + '<div class="pl">' + labelFor(g.s) + '</div>',
      {maxWidth:250}
    );
    markers.push(mk);
  });
  var badge = document.getElementById('map-count');
  if(badge) badge.textContent = data.length + ' juridictions';
}

/* Rendu initial avec le fallback complet */
renderMarkers(GEO);

/* ── Synchronisation temps reel avec le parent (sentinel.html) ──
   Le parent envoie postMessage({type:'jurs-update', data:[...]}) chaque fois
   que JURS change (chargement initial ou apres une actualisation IA). */
window.addEventListener('message', function(event){
  if(event.data && event.data.type === 'jurs-update' && Array.isArray(event.data.data)){
    renderMarkers(event.data.data);
  }
});

/* Signaler au parent que la carte est prete a recevoir des donnees */
if(window.parent && window.parent !== window){
  window.parent.postMessage({type:'map-ready'}, '*');
}
}

