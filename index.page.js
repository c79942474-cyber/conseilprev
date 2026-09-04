/* Extrait de index.html — 12 bloc(s) en ligne, dans leur ordre d'origine.
   Le HTML est servi en no-store : ce fichier, lui, obtient un ETag
   et répond 304 dès la deuxième visite. */

;/* ── bloc 1/12 ── */

(function(){
  "use strict";
  var TEND  = new Date("2026-07-04T23:59:59").getTime();
  var TTOT  = TEND - new Date("2026-06-05T00:00:00").getTime();
  var TINT  = null;

  function tfmt(n){ return (n < 10 ? "0" : "") + n; }

  function trun(){
    var tnow  = Date.now();
    var tdiff = Math.max(0, TEND - tnow);
    var tdays = Math.floor(tdiff / 86400000);
    var thrs  = Math.floor((tdiff % 86400000) / 3600000);
    var tmins = Math.floor((tdiff % 3600000)  / 60000);
    var tsecs = Math.floor((tdiff % 60000)    / 1000);

    var eD = document.getElementById("ht-d");
    var eH = document.getElementById("ht-h");
    var eM = document.getElementById("ht-m");
    var eS = document.getElementById("ht-s");
    var eP = document.getElementById("hp-prog");

    if(eD) eD.textContent = tfmt(tdays);
    if(eH) eH.textContent = tfmt(thrs);
    if(eM) eM.textContent = tfmt(tmins);
    if(eS){ eS.textContent = tfmt(tsecs); eS.style.opacity = (tsecs % 2 === 0) ? "0.5" : "1"; }
    if(eP){ eP.style.width = Math.max(0, Math.min(100, tdiff / TTOT * 100)).toFixed(1) + "%"; }
  }

  function tstart(){
    trun();
    if(TINT) clearInterval(TINT);
    TINT = setInterval(trun, 1000);
  }

  if(document.readyState === "loading"){
    document.addEventListener("DOMContentLoaded", tstart);
  } else {
    tstart();
  }
})();


;/* ── bloc 2/12 ── */


var DS=[{"id":"ia-1","theme":"ia","sector":"Technologie","title":"Catalogue des algorithmes publics de l'État","organization":"Etalab / DINUM","description":"Inventaire des systèmes algorithmiques déployés par les administrations françaises.","tags":["IA","algorithmes","transparence"],"metrics":{"reuses":334,"views":19800},"resources":[{"title":"Accéder au catalogue (data.gouv.fr)","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/datasets/catalogue-des-algorithmes-publics-de-letat/"},{"title":"Rapport Etalab algorithmes publics","format":"PDF","size":"—","url":"https://etalab.github.io/algorithmes-publics/"}],"page":"https://www.data.gouv.fr/fr/datasets/catalogue-des-algorithmes-publics-de-letat/"},{"id":"ia-2","theme":"ia","sector":"Technologie","title":"Guide sécurité IA — ANSSI","organization":"ANSSI","description":"Guide de sécurité pour les systèmes d'intelligence artificielle. Recommandations ANSSI.","tags":["IA Act","sécurité","ANSSI"],"metrics":{"reuses":142,"views":8900},"resources":[{"title":"Guide sécurité IA ANSSI (PDF)","format":"PDF","size":"—","url":"https://www.ssi.gouv.fr/guide/securite-de-lia/"},{"title":"Règlement IA — page ANSSI","format":"HTML","size":"—","url":"https://www.ssi.gouv.fr/entreprise/reglementation/reglement-ia/"}],"page":"https://www.ssi.gouv.fr/guide/securite-de-lia/"},{"id":"ia-3","theme":"ia","sector":"Technologie","title":"Livres blancs IA — INRIA","organization":"INRIA","description":"Publications de recherche INRIA sur l'intelligence artificielle, biais et robustesse des modèles.","tags":["LLM","biais","benchmark","INRIA"],"metrics":{"reuses":89,"views":5600},"resources":[{"title":"Livre blanc IA INRIA","format":"PDF","size":"—","url":"https://www.inria.fr/fr/intelligence-artificielle-enjeux-sociaux-et-technologiques"},{"title":"Publications HAL INRIA IA","format":"HTML","size":"—","url":"https://hal.inria.fr/search/index/?q=intelligence+artificielle&rows=30"}],"page":"https://www.inria.fr/fr/intelligence-artificielle-enjeux-sociaux-et-technologiques"},{"id":"ia-4","theme":"ia","sector":"Technologie","title":"Offres d'emploi — France Travail (données ouvertes)","organization":"France Travail","description":"Offres d'emploi liées à l'IA et au numérique. Données ouvertes France Travail.","tags":["emploi","IA","numérique"],"metrics":{"reuses":211,"views":14500},"resources":[{"title":"Dataset offres emploi (data.gouv.fr)","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/datasets/offres-demploi-de-france-travail/"},{"title":"API offres France Travail","format":"JSON","size":"—","url":"https://francetravail.io/data/api"}],"page":"https://www.data.gouv.fr/fr/datasets/offres-demploi-de-france-travail/"},{"id":"ia-5","theme":"ia","sector":"Technologie","title":"IA et services publics — DINUM","organization":"DINUM","description":"Ressources et publications DINUM sur l'IA dans les services publics français.","tags":["IA","services-publics","DINUM"],"metrics":{"reuses":167,"views":11200},"resources":[{"title":"Guide IA secteur public — DINUM","format":"PDF","size":"—","url":"https://www.numerique.gouv.fr/publications/guide-ia/"},{"title":"Tableau de bord IA État","format":"HTML","size":"—","url":"https://www.data.gouv.fr/fr/datasets/?tag=intelligence-artificielle"}],"page":"https://www.numerique.gouv.fr/publications/guide-ia/"},{"id":"cy-1","theme":"cybersecurite","sector":"Sécurité","title":"Panorama de la cybermenace ANSSI","organization":"ANSSI","description":"Rapport annuel ANSSI sur les cybermenaces. Incidents, tendances, acteurs malveillants.","tags":["cybersécurité","ANSSI","incidents"],"metrics":{"reuses":178,"views":11200},"resources":[{"title":"Panorama cybermenace 2024 (PDF)","format":"PDF","size":"—","url":"https://www.ssi.gouv.fr/actualite/le-panorama-de-la-cybermenace-2024/"},{"title":"Rapports ANSSI","format":"HTML","size":"—","url":"https://www.ssi.gouv.fr/actualite/panorama-de-la-cybermenace/"},{"title":"Avis CERT-FR","format":"HTML","size":"—","url":"https://www.cert.ssi.gouv.fr/avis/"}],"page":"https://www.ssi.gouv.fr/actualite/le-panorama-de-la-cybermenace-2024/"},{"id":"cy-2","theme":"cybersecurite","sector":"Sécurité","title":"Alertes et avis CERT-FR — Vulnérabilités","organization":"ANSSI / CERT-FR","description":"Base de vulnérabilités et alertes de sécurité publiées par le CERT-FR. Mise à jour quotidienne.","tags":["CVE","vulnérabilités","CERT-FR"],"metrics":{"reuses":445,"views":32000},"resources":[{"title":"Alertes CERT-FR en ligne","format":"HTML","size":"—","url":"https://www.cert.ssi.gouv.fr/alerte/"},{"title":"Avis de sécurité CERT-FR","format":"HTML","size":"—","url":"https://www.cert.ssi.gouv.fr/avis/"},{"title":"Flux RSS CERT-FR","format":"RSS","size":"—","url":"https://www.cert.ssi.gouv.fr/feed/"}],"page":"https://www.cert.ssi.gouv.fr/"},{"id":"cy-3","theme":"cybersecurite","sector":"Sécurité","title":"Statistiques Cybermalveillance.gouv.fr","organization":"Cybermalveillance.gouv.fr","description":"Données de signalement phishing, ransomware, arnaques. Rapport d'activité annuel.","tags":["phishing","ransomware","signalement"],"metrics":{"reuses":312,"views":22400},"resources":[{"title":"Rapport activité 2023","format":"PDF","size":"—","url":"https://www.cybermalveillance.gouv.fr/tous-nos-contenus/actualites/rapport-activite-2023"},{"title":"Dataset statistiques (data.gouv.fr)","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/search/?q=cybermalveillance"},{"title":"Aide-mémoire cyberattaques","format":"PDF","size":"—","url":"https://www.cybermalveillance.gouv.fr/tous-nos-contenus/kits-de-sensibilisation"}],"page":"https://www.cybermalveillance.gouv.fr/"},{"id":"cy-4","theme":"cybersecurite","sector":"Sécurité","title":"Guide NIS2 — ANSSI","organization":"ANSSI / SGDSN","description":"Guide NIS2 pour les opérateurs d'importance vitale et entités essentielles françaises.","tags":["NIS2","OIV","ANSSI","infrastructures"],"metrics":{"reuses":67,"views":3100},"resources":[{"title":"Guide NIS2 ANSSI","format":"HTML","size":"—","url":"https://www.ssi.gouv.fr/entreprise/reglementation/directive-nis-2/"},{"title":"FAQ NIS2","format":"PDF","size":"—","url":"https://www.ssi.gouv.fr/uploads/2023/01/anssi-nis2-faq.pdf"},{"title":"OIV — Protection des infrastructures","format":"HTML","size":"—","url":"https://www.ssi.gouv.fr/entreprise/protection-des-oiv/"}],"page":"https://www.ssi.gouv.fr/entreprise/reglementation/directive-nis-2/"},{"id":"cy-5","theme":"cybersecurite","sector":"Sécurité","title":"Prestataires qualifiés ANSSI — SecNumCloud","organization":"ANSSI","description":"Liste officielle des prestataires et solutions qualifiés par l'ANSSI (SecNumCloud, PASSI, PSAN).","tags":["SecNumCloud","certification","ANSSI","cloud"],"metrics":{"reuses":234,"views":18900},"resources":[{"title":"Liste prestataires qualifiés ANSSI","format":"HTML","size":"—","url":"https://www.ssi.gouv.fr/entreprise/qualifications/prestataires-de-services-de-confiance-qualifies/"},{"title":"Référentiel SecNumCloud PDF","format":"PDF","size":"—","url":"https://www.ssi.gouv.fr/administration/qualifications/prestataires-de-services-de-confiance-qualifies/"},{"title":"Catalogue SecNumCloud","format":"HTML","size":"—","url":"https://secnumcloud.fr/"}],"page":"https://www.ssi.gouv.fr/entreprise/qualifications/"},{"id":"rg-1","theme":"rgpd","sector":"Juridique","title":"Délibérations et sanctions CNIL","organization":"CNIL","description":"Toutes les délibérations, sanctions et mises en demeure prononcées par la CNIL depuis 2015.","tags":["CNIL","RGPD","sanctions","délibérations"],"metrics":{"reuses":445,"views":28900},"resources":[{"title":"Décisions CNIL (legifrance.gouv.fr)","format":"HTML","size":"—","url":"https://www.legifrance.gouv.fr/cnil/list?pageSize=10&page=1"},{"title":"Rapport annuel CNIL 2023","format":"PDF","size":"—","url":"https://www.cnil.fr/fr/le-rapport-dactivite-2023-de-la-cnil"},{"title":"Sanctions CNIL en ligne","format":"HTML","size":"—","url":"https://www.cnil.fr/fr/les-sanctions-prononcees-par-la-cnil"}],"page":"https://www.cnil.fr/fr/les-sanctions-prononcees-par-la-cnil"},{"id":"rg-2","theme":"rgpd","sector":"Juridique","title":"Outil PIA CNIL — Analyses d'Impact RGPD","organization":"CNIL","description":"Logiciel open source officiel CNIL pour réaliser les Analyses d'Impact Protection Données (AIPD).","tags":["AIPD","DPIA","RGPD","conformité"],"metrics":{"reuses":189,"views":13200},"resources":[{"title":"Télécharger logiciel PIA (GitHub)","format":"ZIP","size":"—","url":"https://github.com/LINCnil/pia/releases/latest"},{"title":"Guide méthode PIA CNIL","format":"PDF","size":"—","url":"https://www.cnil.fr/fr/outil-pia-telechargez-et-installez-le-logiciel-de-la-cnil"},{"title":"Modèles de traitements AIPD","format":"HTML","size":"—","url":"https://www.cnil.fr/fr/les-modeles-de-registre-de-la-cnil"}],"page":"https://www.cnil.fr/fr/outil-pia-telechargez-et-installez-le-logiciel-de-la-cnil"},{"id":"rg-3","theme":"rgpd","sector":"Juridique","title":"Violations de données personnelles — CNIL","organization":"CNIL","description":"Statistiques des violations de données notifiées à la CNIL par secteur et type.","tags":["violations","données-personnelles","CNIL"],"metrics":{"reuses":223,"views":16700},"resources":[{"title":"Dataset violations (data.gouv.fr)","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/search/?q=violations+données+CNIL"},{"title":"Bilan notifications violations","format":"HTML","size":"—","url":"https://www.cnil.fr/fr/bilan-des-notifications-de-violations-de-donnees-personnelles"},{"title":"Notifier une violation à la CNIL","format":"HTML","size":"—","url":"https://www.cnil.fr/fr/notifier-une-violation-de-donnees-personnelles"}],"page":"https://www.cnil.fr/fr/bilan-des-notifications-de-violations-de-donnees-personnelles"},{"id":"sa-1","theme":"sante","sector":"Santé","title":"SNDS — Système National des Données de Santé","organization":"DREES / CNAM","description":"Données de remboursements Assurance Maladie, hospitalisations PMSI, causes de décès.","tags":["SNDS","santé","remboursements","CNAM"],"metrics":{"reuses":567,"views":45000},"resources":[{"title":"Portail SNDS officiel","format":"HTML","size":"—","url":"https://www.snds.gouv.fr/SNDS/Accueil"},{"title":"Dépenses AM — data.gouv.fr","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/search/?q=assurance+maladie+remboursements"},{"title":"Documentation SNDS","format":"PDF","size":"—","url":"https://www.snds.gouv.fr/SNDS/Ressources-documentaires"}],"page":"https://www.snds.gouv.fr/SNDS/Accueil"},{"id":"sa-2","theme":"sante","sector":"Santé","title":"Données hospitalières COVID-19 — Santé Publique France","organization":"Santé Publique France","description":"Hospitalisations, réanimations, décès COVID-19 par département et âge. Séries depuis 2020.","tags":["COVID","hospitalisations","épidémiologie","SPF"],"metrics":{"reuses":2341,"views":189000},"resources":[{"title":"Données hospitalières COVID (data.gouv.fr)","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/datasets/donnees-hospitalieres-relatives-a-lepidemie-de-covid-19/"},{"title":"Synthèse indicateurs COVID","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/datasets/synthese-des-indicateurs-de-suivi-de-lepidemie-covid-19/"},{"title":"Tableau de bord SPF","format":"HTML","size":"—","url":"https://www.santepubliquefrance.fr/dossiers/coronavirus-covid-19"}],"page":"https://www.data.gouv.fr/fr/datasets/donnees-hospitalieres-relatives-a-lepidemie-de-covid-19/"},{"id":"sa-3","theme":"sante","sector":"Santé","title":"Dispositifs médicaux IA — HAS","organization":"HAS / ANSM","description":"Évaluation et certification des dispositifs médicaux intégrant de l'IA. Guide HAS.","tags":["IA-médicale","HAS","ANSM","CE"],"metrics":{"reuses":145,"views":9800},"resources":[{"title":"Guide IA dispositifs médicaux HAS","format":"HTML","size":"—","url":"https://www.has-sante.fr/jcms/p_3488397/fr/intelligence-artificielle"},{"title":"Base EUDAMED (UE)","format":"HTML","size":"—","url":"https://ec.europa.eu/tools/eudamed/"},{"title":"Base ANSM dispositifs médicaux","format":"HTML","size":"—","url":"https://www.ansm.sante.fr/Activites/Surveillance-du-marche-des-dispositifs-medicaux"}],"page":"https://www.has-sante.fr/jcms/p_3488397/fr/intelligence-artificielle"},{"id":"en-1","theme":"energie","sector":"Énergie","title":"Consommation électrique nationale — RTE Open Data","organization":"RTE","description":"Production et consommation électrique nationale. Données temps réel et historique depuis 2012.","tags":["électricité","RTE","consommation","nucléaire"],"metrics":{"reuses":1892,"views":134000},"resources":[{"title":"Open Data RTE — portail","format":"HTML","size":"—","url":"https://data.rte-france.com/"},{"title":"Consommation par région (data.gouv.fr)","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/datasets/consommation-electrique-par-secteur-dactivite-et-par-region/"},{"title":"Bilan prévisionnel RTE 2050","format":"PDF","size":"—","url":"https://www.rte-france.com/analyses-tendances-et-prospectives/bilan-previsionnel-2050-futurs-energetiques"}],"page":"https://data.rte-france.com/"},{"id":"en-2","theme":"energie","sector":"Énergie","title":"DPE Logements — Diagnostics Performance Énergétique","organization":"ADEME / SGPE","description":"Base nationale DPE : 10 millions de logements diagnostiqués. Étiquette A-G, GES, consommation.","tags":["DPE","performance-énergétique","logement"],"metrics":{"reuses":3241,"views":267000},"resources":[{"title":"DPE logements depuis 2021 (data.gouv.fr)","format":"CSV","size":"890 MB","url":"https://www.data.gouv.fr/fr/datasets/dpe-logements-depuis-juillet-2021/"},{"title":"DPE tertiaire (data.gouv.fr)","format":"CSV","size":"120 MB","url":"https://www.data.gouv.fr/fr/datasets/dpe-tertiaire-depuis-juillet-2021/"},{"title":"Observatoire DPE ADEME","format":"HTML","size":"—","url":"https://observatoire-dpe.ademe.fr/"}],"page":"https://www.data.gouv.fr/fr/datasets/dpe-logements-depuis-juillet-2021/"},{"id":"en-3","theme":"energie","sector":"Énergie","title":"Installations EnR — Registre national ENEDIS","organization":"ENEDIS","description":"Cartographie des installations renouvelables raccordées. Éolien, solaire, hydraulique.","tags":["renouvelables","éolien","solaire","ENEDIS"],"metrics":{"reuses":987,"views":72000},"resources":[{"title":"Registre installations EnR (data.gouv.fr)","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/datasets/registre-national-des-installations-de-production-et-de-stockage-delectricite/"},{"title":"Open Data ENEDIS","format":"HTML","size":"—","url":"https://data.enedis.fr/"},{"title":"Panorama énergies renouvelables","format":"HTML","size":"—","url":"https://www.enedis.fr/les-energies-renouvelables"}],"page":"https://www.data.gouv.fr/fr/datasets/registre-national-des-installations-de-production-et-de-stockage-delectricite/"},{"id":"en-4","theme":"energie","sector":"Énergie","title":"Impact environnemental du numérique — ADEME & ARCEP","organization":"ADEME / ARCEP","description":"Empreinte carbone des datacenters et du numérique en France. Rapport ADEME-ARCEP.","tags":["datacenter","numérique","CO2","ESG"],"metrics":{"reuses":312,"views":24000},"resources":[{"title":"Rapport ADEME-ARCEP numérique environnement","format":"PDF","size":"—","url":"https://www.arcep.fr/la-regulation/grands-dossiers-thematiques-transverses/lempreinte-environnementale-du-numerique.html"},{"title":"Guide face cachée du numérique ADEME","format":"HTML","size":"—","url":"https://www.ademe.fr/expertises/numerique/passer-a-laction/fiche/la-face-cachee-du-numerique/"},{"title":"Données numérique responsable","format":"HTML","size":"—","url":"https://www.data.gouv.fr/fr/search/?q=empreinte+numerique"}],"page":"https://www.arcep.fr/la-regulation/grands-dossiers-thematiques-transverses/lempreinte-environnementale-du-numerique.html"},{"id":"tr-1","theme":"transport","sector":"Transport","title":"GTFS France — Transport.data.gouv.fr","organization":"transport.data.gouv.fr","description":"Données GTFS de tous les réseaux de transport en commun français. Lignes, arrêts, horaires.","tags":["GTFS","transport","SNCF","mobilité"],"metrics":{"reuses":4521,"views":312000},"resources":[{"title":"Portail transport.data.gouv.fr","format":"HTML","size":"—","url":"https://transport.data.gouv.fr/"},{"title":"Jeux de données GTFS nationaux","format":"ZIP","size":"—","url":"https://transport.data.gouv.fr/datasets?type=public-transit"},{"title":"API temps réel SNCF","format":"JSON","size":"—","url":"https://data.sncf.com/explore/"}],"page":"https://transport.data.gouv.fr/"},{"id":"tr-2","theme":"transport","sector":"Transport","title":"Accidents corporels de la route — BAAC","organization":"Ministère Intérieur / ONISR","description":"Accidents de la route avec victimes en France. 30 ans de données géolocalisées.","tags":["accidents","sécurité-routière","BAAC","ONISR"],"metrics":{"reuses":2876,"views":198000},"resources":[{"title":"Base BAAC accidents (data.gouv.fr)","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2022/"},{"title":"Bilan accidentalité 2023 ONISR","format":"PDF","size":"—","url":"https://www.onisr.securite-routiere.gouv.fr/etat-de-linsecurite-routiere/bilans-annuels-de-laccidentalite/bilan-de-lannee-2023"},{"title":"Open data sécurité routière","format":"HTML","size":"—","url":"https://www.data.gouv.fr/fr/search/?q=accidents+route"}],"page":"https://www.data.gouv.fr/fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2022/"},{"id":"tr-3","theme":"transport","sector":"Transport","title":"Bornes de recharge VE — IRVE","organization":"Min. Transition Énergétique","description":"100 000+ points de recharge véhicules électriques géolocalisés. Puissance, opérateur, connecteurs.","tags":["VE","bornes","IRVE","électromobilité"],"metrics":{"reuses":1234,"views":87000},"resources":[{"title":"Fichier IRVE consolidé (data.gouv.fr)","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/datasets/fichier-consolide-des-bornes-de-recharge-pour-vehicules-electriques/"},{"title":"Carte bornes recharge","format":"HTML","size":"—","url":"https://www.data.gouv.fr/fr/datasets/fichier-consolide-des-bornes-de-recharge-pour-vehicules-electriques/"},{"title":"API IRVE temps réel","format":"JSON","size":"—","url":"https://transport.data.gouv.fr/datasets?type=charging-stations"}],"page":"https://www.data.gouv.fr/fr/datasets/fichier-consolide-des-bornes-de-recharge-pour-vehicules-electriques/"},{"id":"fi-1","theme":"finance","sector":"Finance","title":"Budget de l'État — Données ouvertes","organization":"Ministère des Finances / DGFiP","description":"Budget général de l'État. Recettes et dépenses par programme, mission, action. Format LOLF.","tags":["budget","PLF","finances-publiques"],"metrics":{"reuses":1567,"views":112000},"resources":[{"title":"Budget ouvert — budget.gouv.fr","format":"HTML","size":"—","url":"https://www.budget.gouv.fr/documentation/open-data"},{"title":"Dataset budget synthèse (data.gouv.fr)","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/datasets/budget-de-letat-donnees-de-synthese/"},{"title":"Rapport Cour des Comptes 2024","format":"PDF","size":"—","url":"https://www.ccomptes.fr/fr/publications/le-budget-de-letat-en-2023"}],"page":"https://www.data.gouv.fr/fr/datasets/budget-de-letat-donnees-de-synthese/"},{"id":"fi-2","theme":"finance","sector":"Finance","title":"DORA — Résilience opérationnelle numérique","organization":"ACPR / Banque de France","description":"Règlement DORA : résilience opérationnelle numérique pour le secteur financier européen.","tags":["DORA","ACPR","résilience","ICT","banque"],"metrics":{"reuses":234,"views":18900},"resources":[{"title":"Page DORA — ACPR","format":"HTML","size":"—","url":"https://acpr.banque-france.fr/dora"},{"title":"Texte règlement DORA (EUR-Lex)","format":"PDF","size":"—","url":"https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX%3A32022R2554"},{"title":"RTS/ITS DORA — EBA","format":"HTML","size":"—","url":"https://www.eba.europa.eu/regulation-and-policy/digital-operational-resilience-act-dora"}],"page":"https://acpr.banque-france.fr/dora"},{"id":"fi-3","theme":"finance","sector":"Finance","title":"Base SIRENE — Entreprises et établissements","organization":"INSEE","description":"12 millions d'unités légales françaises. SIREN, SIRET, APE, date création, effectifs.","tags":["SIRENE","entreprises","INSEE","SIREN"],"metrics":{"reuses":8934,"views":892000},"resources":[{"title":"Base SIRENE (data.gouv.fr)","format":"CSV","size":"2.4 GB","url":"https://www.data.gouv.fr/fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/"},{"title":"Annuaire entreprises — API Sirene","format":"JSON","size":"—","url":"https://api.insee.fr/catalogue/site/themes/wso2/subthemes/insee/pages/item-info.jag?name=Sirene&version=V3.11&provider=insee"},{"title":"Explorateur entreprises","format":"HTML","size":"—","url":"https://annuaire-entreprises.data.gouv.fr/"}],"page":"https://www.data.gouv.fr/fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/"},{"id":"fi-4","theme":"finance","sector":"Finance","title":"Marchés publics — Données essentielles","organization":"Direction des Affaires Juridiques","description":"Marchés publics notifiés en France. Acheteur, titulaire, montant, objet. Loi Sapin II.","tags":["marchés-publics","transparence","commande-publique"],"metrics":{"reuses":2345,"views":167000},"resources":[{"title":"DECP marchés publics (data.gouv.fr)","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/datasets/donnees-essentielles-de-la-commande-publique-fichiers-consolides/"},{"title":"Explorateur marchés publics","format":"HTML","size":"—","url":"https://www.marches-publics.info/"},{"title":"Guide commande publique PDF","format":"PDF","size":"—","url":"https://www.economie.gouv.fr/files/files/directions_services/daj/marches_publics/guides/guide-acheteurs-2019.pdf"}],"page":"https://www.data.gouv.fr/fr/datasets/donnees-essentielles-de-la-commande-publique-fichiers-consolides/"},{"id":"ind-1","theme":"industrie","sector":"Industrie","title":"Émissions polluantes ICPE — Base GEREP","organization":"Min. Transition Écologique","description":"Déclarations d'émissions polluantes des sites industriels ICPE. Air, eau, déchets.","tags":["industrie","émissions","GEREP","ICPE"],"metrics":{"reuses":456,"views":34000},"resources":[{"title":"Émissions industrielles (data.gouv.fr)","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/datasets/emissions-de-polluants-atmospheriques-et-de-gaz-a-effet-de-serre-declarees-par-les-industriels/"},{"title":"Base installations classées","format":"HTML","size":"—","url":"https://www.georisques.gouv.fr/risques/installations-industrielles"},{"title":"Portail des données industrielles","format":"HTML","size":"—","url":"https://www.data.gouv.fr/fr/search/?q=ICPE+émissions"}],"page":"https://www.data.gouv.fr/fr/datasets/emissions-de-polluants-atmospheriques-et-de-gaz-a-effet-de-serre-declarees-par-les-industriels/"},{"id":"ind-2","theme":"industrie","sector":"Industrie","title":"Accidents technologiques — Base ARIA BARPI","organization":"BARPI / MEFSIN","description":"65 000 accidents technologiques et industriels. Retours d'expérience, Seveso.","tags":["accidents","ARIA","ICPE","Seveso"],"metrics":{"reuses":312,"views":24000},"resources":[{"title":"Base ARIA en ligne","format":"HTML","size":"—","url":"https://www.aria.developpement-durable.gouv.fr/"},{"title":"Dataset ARIA (data.gouv.fr)","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/search/?q=accidents+technologiques+ARIA"},{"title":"Bilan accidents industriels","format":"PDF","size":"—","url":"https://www.aria.developpement-durable.gouv.fr/bilan/"}],"page":"https://www.aria.developpement-durable.gouv.fr/"},{"id":"ind-3","theme":"industrie","sector":"Industrie","title":"Brevets industriels — INPI Open Data","organization":"INPI","description":"Brevets déposés en France. Inventeurs, déposants, domaines technologiques, statut.","tags":["brevets","INPI","propriété-intellectuelle"],"metrics":{"reuses":789,"views":56000},"resources":[{"title":"Open Data brevets INPI","format":"HTML","size":"—","url":"https://data.inpi.fr/brevets"},{"title":"Dataset brevets (data.gouv.fr)","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/search/?q=brevets+INPI"},{"title":"Rapport activité INPI 2023","format":"PDF","size":"—","url":"https://www.inpi.fr/sites/default/files/inpi_bilan_activite_2023.pdf"}],"page":"https://data.inpi.fr/brevets"},{"id":"im-1","theme":"immobilier","sector":"Immobilier","title":"DVF — Demandes de Valeurs Foncières","organization":"DGFiP / IGN","description":"Toutes les transactions immobilières depuis 2014 avec géolocalisation. Prix au m².","tags":["DVF","immobilier","prix","transactions"],"metrics":{"reuses":12456,"views":1234000},"resources":[{"title":"DVF sur data.gouv.fr","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/"},{"title":"DVF géolocalisé","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres-geolocalisees/"},{"title":"Explorateur DVF","format":"HTML","size":"—","url":"https://app.dvf.etalab.gouv.fr/"}],"page":"https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/"},{"id":"im-2","theme":"immobilier","sector":"Immobilier","title":"PLU — Plans Locaux d'Urbanisme","organization":"Géoportail Urbanisme / DGALN","description":"Règlements d'urbanisme de toutes les communes françaises. Zones, servitudes, hauteurs.","tags":["PLU","urbanisme","zonage","DGALN"],"metrics":{"reuses":3456,"views":234000},"resources":[{"title":"Géoportail de l'Urbanisme","format":"HTML","size":"—","url":"https://www.geoportail-urbanisme.gouv.fr/"},{"title":"GPU — Données PLU","format":"GEOJSON","size":"—","url":"https://www.geoportail-urbanisme.gouv.fr/"},{"title":"Dataset PLU (data.gouv.fr)","format":"HTML","size":"—","url":"https://www.data.gouv.fr/fr/search/?q=plan+local+urbanisme"}],"page":"https://www.geoportail-urbanisme.gouv.fr/"},{"id":"ed-1","theme":"education","sector":"Éducation","title":"Résultats Baccalauréat par établissement","organization":"MENJ / DEPP","description":"Taux de réussite bac 2024 par lycée, académie, série, mention.","tags":["baccalauréat","résultats","lycées","DEPP"],"metrics":{"reuses":2341,"views":187000},"resources":[{"title":"Résultats bac par lycée (data.gouv.fr)","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/datasets/le-baccalaureat-par-academie/"},{"title":"Indicateurs lycées MENJ","format":"HTML","size":"—","url":"https://www.education.gouv.fr/les-indicateurs-de-resultats-des-lycees-8025"},{"title":"Note DEPP résultats bac 2024","format":"PDF","size":"—","url":"https://www.education.gouv.fr/les-resultats-definitifs-du-baccalaureat-2024-380951"}],"page":"https://www.data.gouv.fr/fr/datasets/le-baccalaureat-par-academie/"},{"id":"ed-2","theme":"education","sector":"Éducation","title":"IA dans l'éducation — Ressources Canopé","organization":"Réseau Canopé / MENJ","description":"Ressources et rapports sur l'IA dans les établissements scolaires. Formation enseignants.","tags":["IA","éducation","numérique","enseignants"],"metrics":{"reuses":234,"views":18900},"resources":[{"title":"Ressources IA Canopé","format":"HTML","size":"—","url":"https://www.reseau-canope.fr/"},{"title":"Données éducation numérique (data.gouv.fr)","format":"HTML","size":"—","url":"https://www.data.gouv.fr/fr/search/?q=education+numerique"},{"title":"Données enseignement sup numérique","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/datasets/le-numerique-dans-lenseignement-superieur/"}],"page":"https://www.reseau-canope.fr/"},{"id":"env-1","theme":"environnement","sector":"Environnement","title":"Qualité de l'air — Données Atmo France","organization":"Atmo France / AirParif","description":"Mesures horaires PM2.5, PM10, NO2, O3, SO2 sur 800 stations françaises.","tags":["qualité-air","pollution","PM2.5","Atmo"],"metrics":{"reuses":2876,"views":234000},"resources":[{"title":"Données qualité air (data.gouv.fr)","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/datasets/donnees-temps-reel-de-mesure-des-concentrations-de-polluants-atmospheriques-reglementes-1/"},{"title":"Portail Atmo France","format":"HTML","size":"—","url":"https://www.atmo-france.org/"},{"title":"AirParif données Paris","format":"HTML","size":"—","url":"https://www.airparif.fr/surveiller-la-pollution/les-donnees-en-open-data"}],"page":"https://www.data.gouv.fr/fr/datasets/donnees-temps-reel-de-mesure-des-concentrations-de-polluants-atmospheriques-reglementes-1/"},{"id":"env-2","theme":"environnement","sector":"Environnement","title":"Inventaire GES national — CITEPA SECTEN","organization":"CITEPA / ADEME","description":"Émissions GES par secteur depuis 1990. Rapport SECTEN annuel. Format standardisé CCNUCC.","tags":["GES","CO2","inventaire","CITEPA","climat"],"metrics":{"reuses":1567,"views":112000},"resources":[{"title":"Rapport SECTEN 2024 — CITEPA","format":"HTML","size":"—","url":"https://www.citepa.org/fr/secten/"},{"title":"Données GES (data.gouv.fr)","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/search/?q=inventaire+gaz+effet+serre"},{"title":"Bilan GES France — ADEME","format":"HTML","size":"—","url":"https://bilans-ges.ademe.fr/"}],"page":"https://www.citepa.org/fr/secten/"},{"id":"ag-1","theme":"agriculture","sector":"Agriculture","title":"Registre Parcellaire Graphique (RPG) 2023","organization":"ASP / Ministère Agriculture","description":"Cartographie des cultures agricoles pour les aides PAC. Toutes les cultures géolocalisées.","tags":["agriculture","RPG","PAC","cultures"],"metrics":{"reuses":4521,"views":345000},"resources":[{"title":"RPG 2023 (data.gouv.fr)","format":"GEOJSON","size":"2.3 GB","url":"https://www.data.gouv.fr/fr/datasets/registre-parcellaire-graphique-rpg-contours-des-parcelles-et-ilots-culturaux-et-leur-groupe-de-cultures-majoritaire/"},{"title":"RPG — GéoServices IGN","format":"HTML","size":"—","url":"https://geoservices.ign.fr/rpg"},{"title":"Open Data agriculture","format":"HTML","size":"—","url":"https://www.data.gouv.fr/fr/search/?q=agriculture+parcelles"}],"page":"https://www.data.gouv.fr/fr/datasets/registre-parcellaire-graphique-rpg-contours-des-parcelles-et-ilots-culturaux-et-leur-groupe-de-cultures-majoritaire/"},{"id":"ag-2","theme":"agriculture","sector":"Agriculture","title":"Pesticides — Ventes et usage Bnvd ANSES","organization":"ANSES / Ministère Agriculture","description":"Quantités de pesticides vendus par matière active et département. Plan Ecophyto.","tags":["pesticides","ANSES","Bnvd","Ecophyto"],"metrics":{"reuses":1234,"views":89000},"resources":[{"title":"Ventes pesticides (data.gouv.fr)","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/datasets/ventes-de-produits-phytopharmaceutiques-par-departement/"},{"title":"Base Bnvd ANSES","format":"HTML","size":"—","url":"https://bnvd.anses.fr/"},{"title":"Rapport ANSES pesticides","format":"HTML","size":"—","url":"https://www.anses.fr/fr/content/bilan-des-ventes-de-produits-phytopharmaceutiques"}],"page":"https://www.data.gouv.fr/fr/datasets/ventes-de-produits-phytopharmaceutiques-par-departement/"},{"id":"to-1","theme":"tourisme","sector":"Tourisme","title":"Hébergements touristiques — Capacité France","organization":"INSEE / DGE","description":"Capacité et fréquentation des hébergements touristiques français. Données mensuelles.","tags":["tourisme","hôtels","hébergements"],"metrics":{"reuses":876,"views":67000},"resources":[{"title":"Hébergements collectifs (data.gouv.fr)","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/datasets/hebergements-collectifs-de-tourisme/"},{"title":"Chiffres clés tourisme 2023","format":"HTML","size":"—","url":"https://www.entreprises.gouv.fr/fr/tourisme/chiffres-du-tourisme"},{"title":"Open data tourisme","format":"HTML","size":"—","url":"https://www.data.gouv.fr/fr/search/?q=tourisme+hébergements"}],"page":"https://www.data.gouv.fr/fr/datasets/hebergements-collectifs-de-tourisme/"},{"id":"rh-1","theme":"rh","sector":"Ressources Humaines","title":"Offres d'emploi — France Travail Open Data","organization":"France Travail","description":"Offres déposées sur France Travail. Métiers, contrats, salaires, localisations.","tags":["emploi","offres","France-Travail","recrutement"],"metrics":{"reuses":5678,"views":456000},"resources":[{"title":"Dataset offres emploi (data.gouv.fr)","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/datasets/offres-demploi-de-france-travail/"},{"title":"API offres France Travail","format":"JSON","size":"—","url":"https://francetravail.io/data/api/offres-emploi"},{"title":"Statistiques emploi","format":"HTML","size":"—","url":"https://statistiques.pole-emploi.org/"}],"page":"https://www.data.gouv.fr/fr/datasets/offres-demploi-de-france-travail/"},{"id":"rh-2","theme":"rh","sector":"Ressources Humaines","title":"Index égalité femmes-hommes — DARES","organization":"Ministère du Travail / DARES","description":"Index égalité salariale obligatoire pour entreprises 50+ salariés. Note /100.","tags":["égalité","femmes-hommes","salaires","DARES"],"metrics":{"reuses":1234,"views":98000},"resources":[{"title":"Index égalité (data.gouv.fr)","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/datasets/index-egalite-professionnelle/"},{"title":"Simulateur index égalité","format":"HTML","size":"—","url":"https://index-egapro.travail.gouv.fr/"},{"title":"Publication DARES égalité","format":"HTML","size":"—","url":"https://dares.travail-emploi.gouv.fr/publication/index-de-legalite-professionnelle"}],"page":"https://www.data.gouv.fr/fr/datasets/index-egalite-professionnelle/"},{"id":"ju-1","theme":"justice","sector":"Juridique","title":"Jurisprudence open data — Judilibre","organization":"Cour de Cassation / Conseil d'État","description":"Décisions judiciaires anonymisées. Cour de cassation, Conseil d'État, cours d'appel.","tags":["jurisprudence","justice","Judilibre"],"metrics":{"reuses":2345,"views":178000},"resources":[{"title":"Moteur Judilibre — recherche","format":"HTML","size":"—","url":"https://www.courdecassation.fr/recherche-judilibre"},{"title":"Dataset jurisprudence (data.gouv.fr)","format":"JSON","size":"—","url":"https://www.data.gouv.fr/fr/datasets/jurisprudence-de-la-cour-de-cassation/"},{"title":"API PISTE Judilibre","format":"JSON","size":"—","url":"https://piste.gouv.fr/"}],"page":"https://www.courdecassation.fr/recherche-judilibre"},{"id":"co-1","theme":"collectivites","sector":"Collectivités","title":"Comptes des collectivités locales","organization":"DGFiP / DGCL","description":"Comptes financiers de communes, départements et régions. Recettes, dépenses, dette.","tags":["collectivités","communes","budget-local","DGFiP"],"metrics":{"reuses":3456,"views":234000},"resources":[{"title":"Comptes communes (data.gouv.fr)","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/datasets/comptes-individuels-des-communes/"},{"title":"Portail finances locales","format":"HTML","size":"—","url":"https://www.collectivites-locales.gouv.fr/finances-locales/les-finances-des-collectivites-locales"},{"title":"Open data collectivités","format":"HTML","size":"—","url":"https://www.data.gouv.fr/fr/search/?q=collectivités+budget"}],"page":"https://www.data.gouv.fr/fr/datasets/comptes-individuels-des-communes/"},{"id":"co-2","theme":"collectivites","sector":"Collectivités","title":"Base Permanente des Équipements — INSEE","organization":"INSEE","description":"2,5 millions d'équipements et services localisés. Écoles, hôpitaux, commerces, services publics.","tags":["équipements","services-publics","INSEE","BPE"],"metrics":{"reuses":4789,"views":345000},"resources":[{"title":"BPE 2023 (data.gouv.fr)","format":"CSV","size":"—","url":"https://www.data.gouv.fr/fr/datasets/base-permanente-des-equipements/"},{"title":"BPE — INSEE","format":"HTML","size":"—","url":"https://www.insee.fr/fr/statistiques/3568638"},{"title":"Carte équipements France","format":"HTML","size":"—","url":"https://www.data.gouv.fr/fr/search/?q=equipements+locaux"}],"page":"https://www.data.gouv.fr/fr/datasets/base-permanente-des-equipements/"}];
var XS={q:"ia",page:1,total:0,pages:1,org:"",fmt:""};
var LANG="fr";
var T={
  fr:JSON.parse(`{"tarif.title":"Tarifications — Comparer les formules","tarif.sub":"Comparez en détail les trois formules Sentinel et choisissez celle qui correspond à votre démarche de conformité.","tarif.feature":"Fonctionnalité","tarif.r1":"Observatoire IA et veille réglementaire","tarif.r2":"Registre des systèmes IA","tarif.r3":"Classification IA Act","tarif.r4":"Cartographies, FRIA et AIPD","tarif.r5":"Veille qualifiée et exports PDF","tarif.r6":"Indice de conformité global (IA Act · RGPD · ISO 42001)","tarif.r7":"Gestion multi-clients et portefeuille","tarif.r8":"Jalons RaaS sur trois cadres","tarif.r9":"Accompagnement CONSEILPREV","tarif.r10":"Utilisateurs","tarif.disc":"Découverte","tarif.unlim":"Illimité","tarif.several":"Plusieurs","tarif.pricerow":"Tarif","tarif.pr_g":"0 €","tarif.pr_p":"Par résultats","tarif.pr_e":"Sur mesure","tarif.cmp_cta":"Comparer les formules","nav.offres":"Nos Offres","offres.title":"Nos offres <span style=color:var(--pf)>Sentinel</span>","offres.sub":"Choisissez le plan adapté à votre démarche de conformité IA. L'offre gratuite est accessible immédiatement par inscription ; les offres Pro et Entreprise donnent accès à la tarification après création de compte.","offres.g.price":"0 €<span>pour découvrir la plateforme</span>","offres.g.feat":"<li>Observatoire IA et veille réglementaire</li><li>Registre des systèmes IA (accès de découverte)</li><li>Simulateur de classification IA Act</li><li>1 utilisateur</li>","offres.g.cta":"Commencer gratuitement","offres.p.badge":"Le plus choisi","offres.p.price":"Tarification par résultats<span>modèle RaaS — détail après inscription</span>","offres.p.feat":"<li>Tout l'IA Act et le RGPD</li><li>Registre illimité, cartographies, FRIA et AIPD</li><li>Veille qualifiée, exports PDF, plan d'action</li><li>Indice de conformité global IA Act · RGPD · ISO 42001</li><li>Plusieurs utilisateurs</li>","offres.p.cta":"Choisir Pro","offres.e.price":"Sur mesure<span>nous consulter — détail après inscription</span>","offres.e.feat":"<li>Gestion multi-clients et portefeuille</li><li>Jalons RaaS sur trois cadres (IA Act, RGPD, ISO 42001)</li><li>Accompagnement CONSEILPREV et audit approfondi</li><li>Support prioritaire et intégrations sur mesure</li>","offres.e.cta":"Choisir Entreprise","offres.note":"Offres et fonctionnalités présentées à titre indicatif, ajustables selon votre périmètre. Le détail tarifaire des offres Pro et Entreprise est communiqué après création de compte, sur la page de tarification.","nav.news":"Actualités","news.eyebrow":"Actualités","news.title":"Simplification du Règlement européen sur l'IA : le « Digital Omnibus on AI » est adopté","news.date":"Paris, le 7 juillet 2026","news.body":"<p>Le 29 juin 2026, le Conseil de l'Union européenne a donné son feu vert final au « Digital Omnibus on AI », après l'approbation du Parlement européen le 16 juin. Issu du paquet « Omnibus VII » de simplification numérique, ce texte réaménage le calendrier et plusieurs obligations du Règlement (UE) 2024/1689 sur l'intelligence artificielle.</p><h4>Un calendrier réaménagé, des obligations maintenues</h4><p>Les obligations des systèmes à haut risque de l'annexe III sont reportées au 2 décembre 2027, celles des systèmes intégrés à des produits réglementés (annexe I) au 2 août 2028, et celles destinées aux autorités publiques au 2 août 2030. Le marquage des contenus synthétiques de l'article 50(2) est reporté au 2 décembre 2026 pour les systèmes déjà sur le marché. Les autres obligations de transparence restent fixées au 2 août 2026.</p><h4>Nouvelles interdictions et assouplissement ciblé</h4><p>Deux interdictions sont ajoutées à l'article 5, applicables au 2 décembre 2026 : les systèmes de nudification et ceux générant du matériel d'exploitation sexuelle d'enfants. La maîtrise de l'IA de l'article 4 est assouplie, et un nouvel article 4a encadre le traitement de données sensibles aux seules fins de correction des biais. Des allègements sont étendus aux petites entreprises de taille intermédiaire.</p><h4>L'analyse de CONSEILPREV</h4><blockquote>Ce report n'est pas une pause, mais une fenêtre pour structurer sa conformité sereinement. Les organisations qui anticipent aborderont les échéances avec un avantage décisif.</blockquote><p>Pour accompagner cette trajectoire, CONSEILPREV met à disposition sa plateforme Sentinel, qui couvre de manière intégrée l'IA Act, le RGPD et la norme ISO/IEC 42001, du registre des systèmes à l'indice de conformité global.</p><p><strong>Contact presse</strong> — Christophe Cerf · christophe.cerf@outlook.com</p><p><small>Communiqué à vocation informative, ne constituant pas un conseil juridique ; les échéances doivent être vérifiées au regard du texte publié au Journal officiel de l'Union européenne.</small></p>","nav.normes":"Normes","nav.data":"Données","nav.svc":"Services","nav.contact":"Contact","hero.ey":"MCP Connector · data.gouv.fr · Paris 2025","hero.h1":"Conformité <em>IA · Data · Cyber</em><br>pilotée par la donnée","hero.sub":"CONSEILPREV connecte votre entreprise aux données publiques françaises pour une conformité IA Act, NIS2, RGPD ancrée dans la réalité réglementaire.","hero.b1":"Explorer les données →","hero.b2":"Nos services","stats.a":"Années expertise","stats.b":"Risques systémiques","stats.c":"Normes couvertes","stats.d":"Datasets indexés","stats.e":"Organisations","nr.lbl":"Conformité réglementaire","nr.ttl":"6 normes maîtrisées, <em>une approche intégrée</em>","nr.ia":"Règlement IA éthique","nr.42":"Gestion IA","nr.27":"Sécurité info","nr.dora":"Résilience num.","nr.nis":"Cybersécurité EU","nr.rgpd":"Privacy by Design","ds.lbl":"Connecteur MCP · data.gouv.fr","ds.ttl":"Données publiques <em>en temps réel</em>","ds.sub":"44 datasets officiels — 37 organisations — 16 thématiques.","ds.theme":"Thématique","ds.org":"Organisation","ds.fmt":"Format","ds.all":"Toutes","ds.ph":"Recherche libre…","ds.btn":"Rechercher","ds.prev":"← Préc.","ds.next":"Suiv. →","ds.hint":"Cliquez sur un dataset","ds.none":"Aucun dataset trouvé","ds.avail":"disponible","ds.availp":"disponibles","sv.lbl":"Offre de services","sv.ttl":"Conseil, Audit & <em>Intelligence Data</em>","sv.a.t":"Audit IA & Cyber","sv.a.d":"Évaluation maturité IA et cyber, cartographie des risques.","sv.b.t":"8 Risques Systémiques IA","sv.b.d":"Juridictionnel, économique, data, opérationnel, géopolitique, cyber, supply chain, environnemental.","sv.c.t":"Connecteur MCP data.gouv.fr","sv.c.d":"Intégration datasets officiels dans vos workflows. API REST Python.","sv.d.t":"Gouvernance & GRC","sv.d.d":"Cadres gouvernance IA/Cyber : politiques, comités, KPIs, reporting.","ct.lbl":"Contact","ct.ttl":"Construisons l’avenir <em>ensemble</em>","ct.sub":"Investisseur, partenaire ou client ? Explorons comment CONSEILPREV peut créer de la valeur avec vous.","fm.ttl":"Nous contacter","fm.sub":"Réponse sous 24h · contact@i-aes.com","fm.name":"Votre nom *","fm.email":"Email professionnel *","fm.co":"Entreprise","fm.sub2":"Sujet","fm.msg":"Votre message *","fm.send":"Envoyer","fm.s1":"Audit IA / Cyber","fm.s2":"Conformité réglementaire","fm.s3":"Investissement","fm.s4":"Partenariat","fm.s5":"Autre","fm.ok":"✅ Message envoyé ! Réponse sous 24h.","fm.err":"❌ Erreur. Contactez-nous : contact@i-aes.com","fm.rl":"⏳ Trop de tentatives. Patientez.","fm.spam":"❌ Erreur de validation.","fm.req":"Veuillez remplir tous les champs requis.","fm.inv":"Email invalide.","ft.desc":"Business Unit IA · Data · Cyber<br>Connecteur MCP data.gouv.fr · Paris 2025","ft.svc":"Services","ft.nrm":"Normes","ch.ttl":"Expert CONSEILPREV","ch.sub":"Claude + Mistral · Conformité · Cyber","ch.q1":"IA Act ?","ch.q2":"Conformité NIS2 ?","ch.q3":"8 risques IA ?","ch.q4":"ISO 27001 vs DORA ?","ch.ph":"Posez votre question…","ch.hi":"Bonjour ! Expert CONSEILPREV.<br>Questions sur <strong>IA Act</strong>, <strong>NIS2</strong>, <strong>ISO 27001</strong>, <strong>DORA</strong>, <strong>RGPD</strong> ?<br><small>🤖 IA — Art. 50 Règl. (UE) 2024/1689</small>",">🤖 IA — Art. 50 Règl. (UE) 2024/1689</small>":"Télécharger","pg":"Voir sur data.gouv.fr","ru":"Réutil.","vi":"Vues","fi":"Fichiers","rs":"Ressources","nav.risques":"Risques IA","nav.expertise":"Expertise","sec.lbl":"Marchés adressés","sec.ttl":"Secteurs d\\\\\\u0027<em>Intervention</em>","sec.sub":"Une expertise sectorielle éprouvée dans les environnements industriels les plus exigeants.","risk.lbl":"Cartographie des menaces","risk.ttl":"8 Risques Systémiques IA <em>que nous adressons</em>","pole.lbl":"Nos trois pôles","pole.ttl":"Une expertise tripolaire<br><em>au service de vos enjeux</em>","pole.sub":"Intelligence Artificielle, Data &amp; Gouvernance, Cybersécurité — trois disciplines réunies pour vous offrir une vision complète et intégrée.","sv.ttl2":"Conseil, Audit &amp; <em>Conformité IA</em>","diff.lbl":"Pourquoi nous choisir","diff.ttl":"<em>Ce qui nous distingue</em>","av.title":"Construisons l’avenir","av.sub":"ensemble","av.desc":"Investisseur, partenaire ou client ? Explorons comment<br>CONSEILPREV peut créer de la valeur avec vous.","ct.lbl2":"Formulaire de projet","ct.ttl2":"Soumettre votre projet <em>IA &amp; Cyber</em>",">IA &amp; Cyber</em>":"Télécharger notre offre :","nav.secteurs":"Secteurs","nav.donnees":"Données","nav.contact2":"Contact","hero.badge":"Sentinel AI — Gouvernance IA","hero.title1":"Votre Tour de Contrôle","hero.title2":"Gouvernance IA","hero.tagline":"Cartographiez vos systèmes IA, évaluez leur conformité et pilotez votre feuille de route — EU AI Act, NIS2 et RGPD, en un seul outil connecté en temps réel.","hero.btn.aies":"Accéder à Sentinel AI →","hero.btn.demo":"▷ Démo","hero.btn.offres":"⬛ Échanger avec un expert","pillars.label":"VOTRE PARCOURS DE CONFORMITÉ EN 3 ÉTAPES","pillars.c1.t":"Cartographier","pillars.c1.d":"Inventaire et classification de vos systèmes IA selon l\\\\\\u0027Annexe III de l\\\\\\u0027AI Act.","pillars.c2.t":"Évaluer","pillars.c2.d":"Scoring multicritère : droits fondamentaux, sécurité, gouvernance des données.","pillars.c3.t":"Planifier","pillars.c3.d":"Feuille de route priorisée avec délais réglementaires et plan d\\\\\\u0027action CONSEILPREV.","promo.label":"🚀 OFFRE DE LANCEMENT","promo.title":"IA Management","promo.desc":"Gouvernance IA, conformité AI Act &amp; RGPD avec intelligence artificielle intégrée","promo.discount":"sur tous vos projets IA &amp; Cyber","promo.limited":"⏱ Offre limitée – Plus que","promo.cta":"Profiter de l\\\\\\u0027offre →","comp.title":"CONFORMITÉ RÉGLEMENTAIRE","dn.back":"← Retour au site","dn.cta.ttl":"Besoin d\\\\\\u0027un <em style=\\\\\\\\",">accompagnement</em> ?":"Nos experts CONSEILPREV vous guident dans l\\\\\\u0027exploitation des données publiques pour votre conformité.","dn.cta.btn1":"Soumettre un projet →","dn.cta.btn2":"📄 Livre Blanc","fl.prenom":"Prénom","fl.nom":"Nom","fl.email":"Adresse e-mail","fl.tel":"Téléphone","fl.co":"Entreprise","fl.role":"Poste / Fonction","fl.sector":"Secteur d\\\\\\u0027activité","fl.size":"Taille de l\\\\\\u0027entreprise","fl.project":"Type de projet IA / Cyber","fl.budget":"Budget indicatif","fl.delay":"Délai souhaité","fl.country":"Pays / Région","fl.norm":"Normes ciblées","fl.desc":"Description de votre besoin","fl.source":"Comment nous avez-vous connus ?","fp.prenom":"Jean","fp.nom":"Dupont","fp.email":"jean.dupont@entreprise.com","fp.tel":"+33 6 00 00 00 00","fp.co":"Nom de votre société","fp.role":"DSI, RSSI, DPO, CTO…","fp.desc":"Décrivez votre projet, vos enjeux, vos contraintes réglementaires…","fs.sector":"— Sélectionnez un secteur —","fs.size":"— Effectif —","fs.project":"— Sélectionnez un type de projet —","fs.budget":"— Fourchette budgétaire —","fs.delay":"— Horizon de démarrage —","fs.country":"— Pays —","fs.norm":"— Référentiel —","fs.source":"— Source —","og.ia":"🧠 IA & Gouvernance","og.cyber":"🛡️ Cybersécurité","og.rgpd":"🔒 RGPD & Données","og.data":"📊 Data & MCP","og.ot":"🏭 Industrie & OT","og.eur":"€ Euros","og.usd":"$ USD","form.consent":"J\\\\\\u0027accepte que mes données soient traitées par <strong>CONSEILPREV</strong> dans le cadre de ma demande de contact, conformément à la <a href=\\\\\\u0027#\\\\\\u0027 class=\\\\\\u0027pclink\\\\\\u0027>politique de confidentialité</a>. Aucune donnée n\\\\\\u0027est partagée avec des tiers.","form.reply":"Réponse garantie sous 24h ouvrées · <a href=\\\\\\u0027mailto:christophe.cerf@outlook.com\\\\\\u0027 class=\\\\\\u0027pclink\\\\\\u0027>christophe.cerf@outlook.com</a>","form.dl":"Télécharger notre offre :","sc.energie":"⚡ Énergie","sc.oilgas":"🛢️ Oil &amp; Gas","sc.ferro":"🚃 Ferroviaire","sc.auto":"🚗 Automobile","sc.indlourde":"🏗️ Industrie Lourde","sc.manufact":"⚙️ Manufacturing","sc.chimie":"⚗️ Chimie &amp; Raffinage","sc.sante":"❤️ Santé","sc.finance":"💲 Finance","sc.logistique":"🚛 Logistique","sc.aero":"✈️ Aérospatial","sc.public":"🏛️ Secteur Public","rk.juri.t":"Juridictionnel","rk.juri.d":"Cloud Act · lois extraterritoriales · sanctions · souveraineté des données","rk.juri.tag":"Droit &amp; Régulation","rk.eco.t":"Économique","rk.eco.d":"Concentration des dépenses · dépendance modèles propriétaires · élasticité tarifaire","rk.eco.tag":"Finance","rk.data.t":"Data &amp; IA","rk.data.d":"Données captives · lock-in fondation · biais algorithmiques · qualité des données","rk.data.tag":"Technique","rk.ops.t":"Opérationnel","rk.ops.d":"Compétences rares · supply chain GPU · dépendance fournisseurs","rk.ops.tag":"Opérations","rk.geo.t":"Géopolitique","rk.geo.d":"Tensions technologiques · restrictions export · fragmentation internet","rk.geo.tag":"Stratégie","rk.cyber.t":"Cyber","rk.cyber.d":"Surface d\\\\\\u0027attaque élargie · adversarial attacks · hallucinations malveillantes","rk.cyber.tag":"Sécurité","rk.sc.t":"Supply Chain Techno","rk.sc.d":"Lock-in propriétaire · portabilité · obsolescence · interopérabilité limitée","rk.sc.tag":"Infrastructure","rk.env.t":"Environnemental","rk.env.d":"Datacenters énergivores · bilan carbone cloud · empreinte IA générative","rk.env.tag":"ESG","risk.cta.txt":"Ces 8 risques sont déjà cartographiés et scorés pour 46 juridictions dans Sentinel AI.","risk.cta.btn":"Explorer Sentinel AI →","df.ai.t":"Assistants IA sur mesure","df.ai.d":"Des assistants qui comprennent votre langage métier et s\\\\\\u0027intègrent parfaitement à vos flux de travail existants.","df.ind.t":"Agents formés industrie","df.ind.d":"Pré-entraînés pour plus de 20 secteurs industriels, nos agents produisent des résultats concrets et mesurables.","df.eco.t":"Optimisation des coûts opérationnels","df.eco.d":"Optimisation des coûts opérationnels grâce à l\\\\\\u0027automatisation intelligente et aux modèles prédictifs.","df.exp.t":"32 ans d\\\\\\u0027expertise sectorielle","df.exp.d":"Énergie, Oil &amp; Gas, Industrie, Finance, Santé — une connaissance terrain des environnements les plus exigeants.","df.jur.t":"Double expertise Juridique &amp; Tech","df.jur.d":"Conformité réglementaire et implémentation technique réunies dans une approche intégrée et cohérente.","df.intl.t":"Couverture internationale","df.intl.d":"Intervention en France, Europe, Moyen-Orient et Amérique du Nord. Maîtrise des réglementations transversales.","po.ia.t":"Intelligence Artificielle","po.ia.d":"Déploiement responsable de l\\\\\\u0027IA, conformité IA Act, gouvernance algorithmique et évaluation des systèmes à haut risque.","po.data.t":"Data &amp; Gouvernance","po.data.d":"Architecture de données, conformité RGPD, data mesh, qualité et lineage — transformer la donnée en actif stratégique sécurisé.","po.cyber.t":"Cybersécurité","po.cyber.d":"Audit, conformité NIS2 &amp; ISO 27001, résilience opérationnelle et protection des systèmes critiques OT/IT industriels.","sv.audit.t":"Audit IA &amp; Cyber","sv.audit.d":"Évaluation complète de votre maturité IA et cyber, cartographie des risques et analyse d\\\\\\u0027écarts réglementaires.","sv.r8.t":"Évaluation des 8 Risques IA","sv.r8.d":"Analyse systémique des risques liés au déploiement IA : biais, robustesse, sécurité et impacts fondamentaux.","sv.conf.t":"Conseil en Conformité","sv.conf.d":"Accompagnement stratégique pour atteindre et maintenir la conformité réglementaire sur l\\\\\\u0027ensemble du périmètre.","sv.integ.t":"Intégration Solutions IA","sv.integ.d":"Déploiement de solutions IA sur mesure pour automatiser vos processus et améliorer la productivité.","sv.form.t":"Formation &amp; Accompagnement","sv.form.d":"Programmes certifiants pour maîtriser les enjeux IA, data et cyber au sein de vos équipes.","sv.grc.t":"Gouvernance &amp; GRC","sv.grc.d":"Cadres de gouvernance IA/Cyber intégrés : politiques, comités, KPIs et reporting conformité.","sv.audit.l1":"Audit conformité IA Act / ISO 42001","sv.audit.l2":"Audit sécurité ISO 27001 / NIS2","sv.audit.l3":"Revue architecture IA &amp; Data","sv.audit.l4":"Rapport d\\\\\\u0027écarts &amp; recommandations","sv.r8.l1":"Classification systèmes à risque","sv.r8.l2":"Analyse d\\\\\\u0027impact algorithmique","sv.r8.l3":"Matrice des 8 risques systémiques","sv.r8.l4":"Monitoring post-déploiement","sv.conf.l1":"Plan de mise en conformité IA Act","sv.conf.l2":"Déploiement SMSI ISO 27001","sv.conf.l3":"Programme conformité NIS2 / DORA","sv.conf.l4":"RGPD &amp; Privacy by Design","sv.integ.l1":"Développement agents IA industriels","sv.integ.l2":"Automatisation processus métier","sv.integ.l3":"Jumeaux numériques &amp; IoT","sv.integ.l4":"MLOps &amp; monitoring IA","sv.form.l1":"Formations certifiantes IA Act","sv.form.l2":"Ateliers cybersécurité NIS2","sv.form.l3":"Coaching équipes DSI/RSSI","sv.form.l4":"Change management IA","sv.grc.l1":"Charte IA &amp; politique gouvernance","sv.grc.l2":"Comité GRC IA &amp; Cyber","sv.grc.l3":"KPIs et reporting conformité","sv.grc.l4":"Gestion fournisseurs IA tiers","ft.brand":"Business Unit IA · Data · Cyber<br>Connecteur MCP data.gouv.fr · Paris 2025","ft.svc.lbl":"Services","ft.nrm.lbl":"Normes","ft.res.lbl":"Ressources","ft.svc.l1":"Audit IA &amp; Cyber","ft.svc.l2":"8 Risques Systémiques IA","ft.svc.l3":"Connecteur MCP data.gouv.fr","ft.svc.l4":"Formation &amp; Accompagnement","ft.svc.l5":"Gouvernance &amp; GRC","ft.nrm.l1":"IA Act · ISO 42001","ft.nrm.l2":"NIS2 · ISO 27001","ft.nrm.l3":"DORA · RGPD","ft.nrm.l4":"8 Risques Systémiques IA","ft.nrm.l5":"Livre Blanc IA &amp; ROI","ft.res.l1":"📄 Livre Blanc","ft.res.l2":"Datasets data.gouv.fr","ft.res.l3":"Soumettre un projet","ft.res.l4":"christophe.cerf@outlook.com","ft.copy":"© 2025 CONSEILPREV · ERSIA IA MANAGEMENT · i-aes.com","ft.tag":"MCP · DATA.GOUV.FR · PARIS","og.gbp":"£ GBP","clients.title":"50 entreprises de tous secteurs nous font confiance depuis 2014","clients.sectors":"<span>Technologies</span> · <span>Finance</span> · <span>Santé</span> · <span>Assurance</span> · <span>Énergie</span> · <span>Industrie</span> · <span>Retail</span>","ft.prod.lbl":"Produits","ft.prod.l1":"Accéder à Sentinel AI →","ft.prod.l2":"Démonstration interactive","ft.prod.l4":"Aide &amp; accessibilité","ft.support.lbl":"Support","ft.support.l1":"Contact","ft.support.l2":"FAQ","ft.support.l3":"Centre d\\\\\\u0027aide","ft.legal.lbl":"Légal","ft.legal.l1":"Mentions légales","ft.legal.l2":"Protection des données","ft.legal.l3":"Conditions générales","ft.legal.l4":"Politique de confidentialité","ft.legal.l5":"DSA Impact","ft.plans.lbl":"Abonnements","ft.plans.l1":"Sentinel Gratuit","ft.plans.l2":"Sentinel Pro ⭐ Populaire","ft.plans.l3":"Sentinel Entreprise","ft.nl.title":"Restez informé des dernières actualités IA","ft.nl.desc":"Recevez nos conseils d\\\\\\u0027experts, les mises à jour réglementaires et les bonnes pratiques directement dans votre boîte mail.","ft.nl.ph":"Votre email professionnel","ft.nl.btn":"S\\\\\\u0027inscrire →","ft.nl.check":"Recevoir la newsletter hebdomadaire avec les dernières actualités IA &amp; conformité","ft.nl.note":"Email professionnel requis. Désinscription possible à tout moment."}`),
  en:JSON.parse(`{"tarif.title":"Pricing — Compare the plans","tarif.sub":"Compare the three Sentinel plans in detail and choose the one that fits your compliance journey.","tarif.feature":"Feature","tarif.r1":"AI observatory and regulatory watch","tarif.r2":"AI system registry","tarif.r3":"AI Act classification","tarif.r4":"Mappings, FRIA and DPIA","tarif.r5":"Qualified watch and PDF exports","tarif.r6":"Overall compliance index (AI Act · GDPR · ISO 42001)","tarif.r7":"Multi-client management and portfolio","tarif.r8":"RaaS milestones across three frameworks","tarif.r9":"CONSEILPREV guidance","tarif.r10":"Users","tarif.disc":"Discovery","tarif.unlim":"Unlimited","tarif.several":"Several","tarif.pricerow":"Price","tarif.pr_g":"€0","tarif.pr_p":"Results-based","tarif.pr_e":"Tailored","tarif.cmp_cta":"Compare plans","nav.offres":"Our Plans","offres.title":"Our <span style=color:var(--pf)>Sentinel</span> plans","offres.sub":"Choose the plan that fits your AI compliance journey. The free plan is available immediately by signing up; the Pro and Enterprise plans give access to pricing after account creation.","offres.g.price":"€0<span>to explore the platform</span>","offres.g.feat":"<li>AI observatory and regulatory watch</li><li>AI system registry (discovery access)</li><li>AI Act classification simulator</li><li>1 user</li>","offres.g.cta":"Start for free","offres.p.badge":"Most popular","offres.p.price":"Results-based pricing<span>RaaS model — details after sign-up</span>","offres.p.feat":"<li>Full AI Act and GDPR coverage</li><li>Unlimited registry, mappings, FRIA and DPIA</li><li>Qualified watch, PDF exports, action plan</li><li>Overall compliance index: AI Act · GDPR · ISO 42001</li><li>Multiple users</li>","offres.p.cta":"Choose Pro","offres.e.price":"Tailored<span>contact us — details after sign-up</span>","offres.e.feat":"<li>Multi-client management and portfolio</li><li>RaaS milestones across three frameworks (AI Act, GDPR, ISO 42001)</li><li>CONSEILPREV guidance and in-depth audit</li><li>Priority support and tailored integrations</li>","offres.e.cta":"Choose Enterprise","offres.note":"Plans and features shown for guidance, adjustable to your scope. Pricing details for the Pro and Enterprise plans are provided after account creation, on the pricing page.","nav.news":"News","news.eyebrow":"News","news.title":"Simplifying the EU AI Regulation: the Digital Omnibus on AI is adopted","news.date":"Paris, 7 July 2026","news.body":"<p>On 29 June 2026, the Council of the European Union gave its final approval to the Digital Omnibus on AI, following the European Parliament vote on 16 June. Part of the Omnibus VII digital simplification package, the text reshapes the timeline and several obligations of Regulation (EU) 2024/1689 on artificial intelligence.</p><h4>A rescheduled timeline, obligations maintained</h4><p>Obligations for high-risk systems under Annex III are postponed to 2 December 2027, those for systems embedded in regulated products (Annex I) to 2 August 2028, and those intended for public authorities to 2 August 2030. Marking of synthetic content under Article 50(2) is deferred to 2 December 2026 for systems already on the market. Other transparency obligations remain set at 2 August 2026.</p><h4>New prohibitions and targeted relief</h4><p>Two prohibitions are added to Article 5, applicable from 2 December 2026: nudification systems and systems generating child sexual abuse material. The AI literacy duty under Article 4 is softened, and a new Article 4a frames the processing of sensitive data solely for bias correction. Relief measures are extended to small mid-cap companies.</p><h4>CONSEILPREV's view</h4><blockquote>This deferral is not a pause, but a window to structure compliance calmly. Organisations that anticipate will approach the deadlines with a decisive advantage.</blockquote><p>To support this path, CONSEILPREV offers its Sentinel platform, which integrates the AI Act, the GDPR and the ISO/IEC 42001 standard, from the system registry to the overall compliance index.</p><p><strong>Press contact</strong> — Christophe Cerf · christophe.cerf@outlook.com</p><p><small>Informational release, not legal advice; deadlines should be verified against the text published in the Official Journal of the European Union.</small></p>","nav.normes":"Standards","nav.data":"Data","nav.svc":"Services","nav.contact":"Contact","hero.ey":"MCP Connector · data.gouv.fr · Paris 2025","hero.h1":"AI-powered <em>IA · Data · Cyber</em><br>Compliance","hero.sub":"CONSEILPREV connects your company to French public data for AI Act, NIS2, GDPR compliance grounded in regulatory reality.","hero.b1":"Explore datasets →","hero.b2":"Our services","stats.a":"Years expertise","stats.b":"Systemic risks","stats.c":"Standards covered","stats.d":"Indexed datasets","stats.e":"Organisations","nr.lbl":"Regulatory compliance","nr.ttl":"6 standards mastered, <em>one integrated approach</em>","nr.ia":"Ethical AI regulation","nr.42":"AI management","nr.27":"Information security","nr.dora":"Digital resilience","nr.nis":"EU Cybersecurity","nr.rgpd":"Privacy by Design","ds.lbl":"MCP Connector · data.gouv.fr","ds.ttl":"Public data <em>in real time</em>","ds.sub":"44 official datasets — 37 organisations — 16 sector themes.","ds.theme":"Theme","ds.org":"Organisation","ds.fmt":"Format","ds.all":"All","ds.ph":"Free search…","ds.btn":"Search","ds.prev":"← Prev","ds.next":"Next →","ds.hint":"Click on a dataset","ds.none":"No dataset found","ds.avail":"available","ds.availp":"available","sv.lbl":"Service offering","sv.ttl":"Consulting, Audit & <em>Data Intelligence</em>","sv.a.t":"AI & Cyber Audit","sv.a.d":"AI and cyber maturity assessment, risk mapping via official data.","sv.b.t":"8 Systemic AI Risks","sv.b.d":"Jurisdictional, economic, data, operational, geopolitical, cyber, supply chain, environmental.","sv.c.t":"MCP Connector data.gouv.fr","sv.c.d":"Official dataset integration in your workflows. Python REST API.","sv.d.t":"Governance & GRC","sv.d.d":"AI/Cyber governance frameworks: policies, committees, KPIs, reporting.","ct.lbl":"Contact","ct.ttl":"Let us build the future <em>together</em>","ct.sub":"Investor, partner or client? Let us explore how CONSEILPREV can create value with you.","fm.ttl":"Contact us","fm.sub":"Reply within 24h · contact@i-aes.com","fm.name":"Your name *","fm.email":"Professional email *","fm.co":"Company","fm.sub2":"Subject","fm.msg":"Your message *","fm.send":"Send message","fm.s1":"AI / Cyber Audit","fm.s2":"Regulatory compliance","fm.s3":"Investment","fm.s4":"Partnership","fm.s5":"Other","fm.ok":"✅ Message sent! Reply within 24h.","fm.err":"❌ Error. Contact us: contact@i-aes.com","fm.rl":"⏳ Too many attempts. Please wait.","fm.spam":"❌ Validation error.","fm.req":"Please fill all required fields.","fm.inv":"Invalid email.","ft.desc":"AI Data Cyber Business Unit<br>MCP Connector data.gouv.fr Paris 2025","ft.svc":"Services","ft.nrm":"Standards","ch.ttl":"CONSEILPREV Expert","ch.sub":"Claude + Mistral · Compliance · Cyber","ch.q1":"What is the AI Act?","ch.q2":"How to comply with NIS2?","ch.q3":"8 systemic AI risks?","ch.q4":"ISO 27001 vs DORA?","ch.ph":"Ask your question…","ch.hi":"Hello! CONSEILPREV Expert.<br>Questions about <strong>AI Act</strong>, <strong>NIS2</strong>, <strong>ISO 27001</strong>, <strong>DORA</strong>, <strong>GDPR</strong>?<br><small>🤖 AI — Art. 50 Reg. (EU) 2024/1689</small>","dl":"Download","pg":"View on data.gouv.fr","ru":"Reuses","vi":"Views","fi":"Files","rs":"Resources","nav.risques":"AI Risks","nav.expertise":"Expertise","sec.lbl":"Markets served","sec.ttl":"<em>Intervention</em> Sectors","sec.sub":"Proven sector expertise in the most demanding industrial environments.","risk.lbl":"Threat mapping","risk.ttl":"8 Systemic AI Risks <em>we address</em>","pole.lbl":"Our three pillars","pole.ttl":"Tripartite expertise<br><em>serving your challenges</em>","pole.sub":"Artificial Intelligence, Data &amp; Governance, Cybersecurity — three disciplines united for a complete integrated vision.","sv.ttl2":"Consulting, Audit &amp; <em>AI Compliance</em>","diff.lbl":"Why choose us","diff.ttl":"<em>What sets us apart</em>","av.title":"Let us build the future","av.sub":"together","av.desc":"Investor, partner or client? Let us explore how<br>CONSEILPREV can create value with you.","ct.lbl2":"Project form","ct.ttl2":"Submit your <em>AI &amp; Cyber</em> project",">AI &amp; Cyber</em> project":"Download our offer:","nav.secteurs":"Sectors","nav.donnees":"Data","nav.contact2":"Contact","hero.badge":"Sentinel AI — Gouvernance IA","hero.title1":"Your Control Tower","hero.title2":"AI Governance","hero.tagline":"Map your AI systems, assess their compliance, and steer your roadmap — EU AI Act, NIS2 and GDPR, in one connected real-time tool.","hero.btn.aies":"Access Sentinel AI →","hero.btn.demo":"▷ Demo","hero.btn.offres":"⬛ Talk to an expert","pillars.label":"YOUR 3-STEP COMPLIANCE JOURNEY","pillars.c1.t":"Map","pillars.c1.d":"Inventory and classification of your AI systems under Annex III of the AI Act.","pillars.c2.t":"Assess","pillars.c2.d":"Multi-criteria scoring: fundamental rights, security, data governance.","pillars.c3.t":"Plan","pillars.c3.d":"Prioritised roadmap with regulatory deadlines and a CONSEILPREV action plan.","promo.label":"🚀 LAUNCH OFFER","promo.title":"AI Management","promo.desc":"AI Governance, AI Act &amp; GDPR compliance with integrated artificial intelligence","promo.discount":"on all your AI &amp; Cyber projects","promo.limited":"⏱ Limited offer – Only","promo.cta":"Get the offer →","comp.title":"REGULATORY COMPLIANCE","dn.back":"← Back to site","dn.cta.ttl":"Need <em style=\\\\\\\\",">support</em>?":"Our CONSEILPREV experts guide you in leveraging public data for your compliance.","dn.cta.btn1":"Submit a project →","dn.cta.btn2":"📄 White Paper","fl.prenom":"First name","fl.nom":"Last name","fl.email":"Email address","fl.tel":"Phone","fl.co":"Company","fl.role":"Position / Role","fl.sector":"Industry sector","fl.size":"Company size","fl.project":"AI / Cyber project type","fl.budget":"Estimated budget","fl.delay":"Desired timeline","fl.country":"Country / Region","fl.norm":"Target standards","fl.desc":"Description of your need","fl.source":"How did you find us?","fp.prenom":"John","fp.nom":"Smith","fp.email":"john.smith@company.com","fp.tel":"+1 555 000 0000","fp.co":"Your company name","fp.role":"CIO, CISO, DPO, CTO…","fp.desc":"Describe your project, challenges, regulatory constraints…","fs.sector":"— Select a sector —","fs.size":"— Company size —","fs.project":"— Select a project type —","fs.budget":"— Budget range —","fs.delay":"— Start timeline —","fs.country":"— Country —","fs.norm":"— Framework —","fs.source":"— Source —","og.ia":"🧠 AI & Governance","og.cyber":"🛡️ Cybersecurity","og.rgpd":"🔒 GDPR & Data","og.data":"📊 Data & MCP","og.ot":"🏭 Industry & OT","og.eur":"€ Euros","og.usd":"$ USD","form.consent":"I agree that my data is processed by <strong>CONSEILPREV</strong> as part of my contact request, in accordance with the <a href=\\\\\\u0027#\\\\\\u0027 class=\\\\\\u0027pclink\\\\\\u0027>privacy policy</a>. No data is shared with third parties.","form.reply":"Reply guaranteed within 24 business hours · <a href=\\\\\\u0027mailto:christophe.cerf@outlook.com\\\\\\u0027 class=\\\\\\u0027pclink\\\\\\u0027>christophe.cerf@outlook.com</a>","form.dl":"Download our offer:","sc.energie":"⚡ Energy","sc.oilgas":"🛢️ Oil &amp; Gas","sc.ferro":"🚃 Rail","sc.auto":"🚗 Automotive","sc.indlourde":"🏗️ Heavy Industry","sc.manufact":"⚙️ Manufacturing","sc.chimie":"⚗️ Chemistry &amp; Refining","sc.sante":"❤️ Healthcare","sc.finance":"💲 Finance","sc.logistique":"🚛 Logistics","sc.aero":"✈️ Aerospace","sc.public":"🏛️ Public Sector","rk.juri.t":"Jurisdictional","rk.juri.d":"Cloud Act · extraterritorial laws · sanctions · data sovereignty","rk.juri.tag":"Law &amp; Regulation","rk.eco.t":"Economic","rk.eco.d":"Spending concentration · proprietary model dependency · tariff elasticity","rk.eco.tag":"Finance","rk.data.t":"Data &amp; AI","rk.data.d":"Captive data · foundation lock-in · algorithmic bias · data quality","rk.data.tag":"Technical","rk.ops.t":"Operational","rk.ops.d":"Scarce skills · GPU supply chain · vendor dependency","rk.ops.tag":"Operations","rk.geo.t":"Geopolitical","rk.geo.d":"Technological tensions · export restrictions · internet fragmentation","rk.geo.tag":"Strategy","rk.cyber.t":"Cyber","rk.cyber.d":"Expanded attack surface · adversarial attacks · malicious hallucinations","rk.cyber.tag":"Security","rk.sc.t":"Tech Supply Chain","rk.sc.d":"Proprietary lock-in · portability · obsolescence · limited interoperability","rk.sc.tag":"Infrastructure","rk.env.t":"Environmental","rk.env.d":"Energy-intensive datacenters · cloud carbon footprint · generative AI impact","rk.env.tag":"ESG","risk.cta.txt":"These 8 risks are already mapped and scored for 46 jurisdictions in Sentinel AI.","risk.cta.btn":"Explore Sentinel AI →","df.ai.t":"Custom AI Assistants","df.ai.d":"Assistants that understand your business language and integrate seamlessly into your existing workflows.","df.ind.t":"Industry-trained Agents","df.ind.d":"Pre-trained for more than 20 industrial sectors, our agents deliver concrete and measurable results.","df.eco.t":"Operational cost optimisation","df.eco.d":"Operational cost optimisation through intelligent automation and predictive models.","df.exp.t":"32 years of sector expertise","df.exp.d":"Energy, Oil &amp; Gas, Industry, Finance, Healthcare — hands-on knowledge of the most demanding environments.","df.jur.t":"Dual Legal &amp; Tech expertise","df.jur.d":"Regulatory compliance and technical implementation united in an integrated and coherent approach.","df.intl.t":"International coverage","df.intl.d":"Operations in France, Europe, Middle East and North America. Mastery of cross-cutting regulations.","po.ia.t":"Artificial Intelligence","po.ia.d":"Responsible AI deployment, AI Act compliance, algorithmic governance and high-risk system evaluation.","po.data.t":"Data &amp; Governance","po.data.d":"Data architecture, GDPR compliance, data mesh, quality and lineage — transforming data into a secure strategic asset.","po.cyber.t":"Cybersecurity","po.cyber.d":"Audit, NIS2 &amp; ISO 27001 compliance, operational resilience and protection of critical industrial OT/IT systems.","sv.audit.t":"AI &amp; Cyber Audit","sv.audit.d":"Complete assessment of your AI and cyber maturity, risk mapping and regulatory gap analysis.","sv.r8.t":"8 AI Risks Assessment","sv.r8.d":"Systemic analysis of AI deployment risks: bias, robustness, security and fundamental impacts.","sv.conf.t":"Compliance Consulting","sv.conf.d":"Strategic support to achieve and maintain regulatory compliance across the entire scope.","sv.integ.t":"AI Solutions Integration","sv.integ.d":"Deployment of custom AI solutions to automate your processes and improve productivity.","sv.form.t":"Training &amp; Support","sv.form.d":"Certification programmes to master AI, data and cyber challenges within your teams.","sv.grc.t":"Governance &amp; GRC","sv.grc.d":"Integrated AI/Cyber governance frameworks: policies, committees, KPIs and compliance reporting.","sv.audit.l1":"AI Act / ISO 42001 compliance audit","sv.audit.l2":"ISO 27001 / NIS2 security audit","sv.audit.l3":"AI &amp; Data architecture review","sv.audit.l4":"Gap report &amp; recommendations","sv.r8.l1":"Risk system classification","sv.r8.l2":"Algorithmic impact analysis","sv.r8.l3":"8 systemic risks matrix","sv.r8.l4":"Post-deployment monitoring","sv.conf.l1":"AI Act compliance roadmap","sv.conf.l2":"ISO 27001 ISMS deployment","sv.conf.l3":"NIS2 / DORA compliance programme","sv.conf.l4":"GDPR &amp; Privacy by Design","sv.integ.l1":"Industrial AI agent development","sv.integ.l2":"Business process automation","sv.integ.l3":"Digital twins &amp; IoT","sv.integ.l4":"MLOps &amp; AI monitoring","sv.form.l1":"AI Act certification training","sv.form.l2":"NIS2 cybersecurity workshops","sv.form.l3":"CIO/CISO team coaching","sv.form.l4":"AI change management","sv.grc.l1":"AI charter &amp; governance policy","sv.grc.l2":"AI &amp; Cyber GRC committee","sv.grc.l3":"KPIs and compliance reporting","sv.grc.l4":"Third-party AI vendor management","ft.brand":"AI Data Cyber Business Unit<br>MCP Connector data.gouv.fr · Paris 2025","ft.svc.lbl":"Services","ft.nrm.lbl":"Standards","ft.res.lbl":"Resources","ft.svc.l1":"AI &amp; Cyber Audit","ft.svc.l2":"8 Systemic AI Risks","ft.svc.l3":"MCP Connector data.gouv.fr","ft.svc.l4":"Training &amp; Support","ft.svc.l5":"Governance &amp; GRC","ft.nrm.l1":"AI Act · ISO 42001","ft.nrm.l2":"NIS2 · ISO 27001","ft.nrm.l3":"DORA · GDPR","ft.nrm.l4":"8 Systemic AI Risks","ft.nrm.l5":"AI &amp; ROI White Paper","ft.res.l1":"📄 White Paper","ft.res.l2":"Datasets data.gouv.fr","ft.res.l3":"Submit a project","ft.res.l4":"christophe.cerf@outlook.com","ft.copy":"© 2025 CONSEILPREV · ERSIA AI MANAGEMENT · i-aes.com","ft.tag":"MCP · DATA.GOUV.FR · PARIS","og.gbp":"£ GBP","clients.title":"50 companies from all sectors have trusted us since 2014","clients.sectors":"<span>Technology</span> · <span>Finance</span> · <span>Healthcare</span> · <span>Insurance</span> · <span>Energy</span> · <span>Industry</span> · <span>Retail</span>","ft.prod.lbl":"Products","ft.prod.l1":"Sentinel AI Features","ft.prod.l2":"Interactive Demo","ft.prod.l4":"Help &amp; accessibility","ft.support.lbl":"Support","ft.support.l1":"Contact","ft.support.l2":"FAQ","ft.support.l3":"Help center","ft.legal.lbl":"Legal","ft.legal.l1":"Legal notice","ft.legal.l2":"Data protection","ft.legal.l3":"Terms &amp; conditions","ft.legal.l4":"Privacy policy","ft.legal.l5":"DSA Impact","ft.plans.lbl":"Plans","ft.plans.l1":"Sentinel Free","ft.plans.l2":"Sentinel Pro ⭐ Popular","ft.plans.l3":"Sentinel Enterprise","ft.nl.title":"Stay informed about the latest AI news","ft.nl.desc":"Receive our expert advice, regulatory updates and best practices directly in your inbox.","ft.nl.ph":"Your professional email","ft.nl.btn":"Subscribe →","ft.nl.check":"Receive the weekly newsletter with the latest AI &amp; compliance news","ft.nl.note":"Professional email required. Unsubscribe at any time."}`),
  de:JSON.parse(`{"tarif.title":"Preise — Angebote vergleichen","tarif.sub":"Vergleichen Sie die drei Sentinel-Angebote im Detail und wählen Sie das passende für Ihren Compliance-Weg.","tarif.feature":"Funktion","tarif.r1":"KI-Observatorium und regulatorische Beobachtung","tarif.r2":"KI-Systemregister","tarif.r3":"AI-Act-Klassifizierung","tarif.r4":"Kartierungen, FRIA und DSFA","tarif.r5":"Qualifizierte Beobachtung und PDF-Exporte","tarif.r6":"Globaler Compliance-Index (AI Act · DSGVO · ISO 42001)","tarif.r7":"Multi-Client-Verwaltung und Portfolio","tarif.r8":"RaaS-Meilensteine über drei Rahmenwerke","tarif.r9":"CONSEILPREV-Begleitung","tarif.r10":"Nutzer","tarif.disc":"Entdeckung","tarif.unlim":"Unbegrenzt","tarif.several":"Mehrere","tarif.pricerow":"Preis","tarif.pr_g":"0 €","tarif.pr_p":"Ergebnisbasiert","tarif.pr_e":"Maßgeschneidert","tarif.cmp_cta":"Angebote vergleichen","nav.offres":"Unsere Angebote","offres.title":"Unsere <span style=color:var(--pf)>Sentinel</span>-Angebote","offres.sub":"Wählen Sie den Plan, der zu Ihrem KI-Compliance-Weg passt. Der kostenlose Plan ist sofort per Registrierung verfügbar; die Pläne Pro und Enterprise geben nach der Kontoerstellung Zugang zur Preisgestaltung.","offres.g.price":"0 €<span>zum Entdecken der Plattform</span>","offres.g.feat":"<li>KI-Observatorium und regulatorische Beobachtung</li><li>KI-Systemregister (Entdeckungszugang)</li><li>AI-Act-Klassifizierungssimulator</li><li>1 Nutzer</li>","offres.g.cta":"Kostenlos starten","offres.p.badge":"Am beliebtesten","offres.p.price":"Ergebnisbasierte Preise<span>RaaS-Modell — Details nach Registrierung</span>","offres.p.feat":"<li>Vollständige Abdeckung von AI Act und DSGVO</li><li>Unbegrenztes Register, Kartierungen, FRIA und DSFA</li><li>Qualifizierte Beobachtung, PDF-Exporte, Aktionsplan</li><li>Globaler Compliance-Index: AI Act · DSGVO · ISO 42001</li><li>Mehrere Nutzer</li>","offres.p.cta":"Pro wählen","offres.e.price":"Maßgeschneidert<span>kontaktieren Sie uns — Details nach Registrierung</span>","offres.e.feat":"<li>Multi-Client-Verwaltung und Portfolio</li><li>RaaS-Meilensteine über drei Rahmenwerke (AI Act, DSGVO, ISO 42001)</li><li>CONSEILPREV-Begleitung und eingehendes Audit</li><li>Prioritäts-Support und maßgeschneiderte Integrationen</li>","offres.e.cta":"Enterprise wählen","offres.note":"Pläne und Funktionen dienen der Orientierung und sind an Ihren Umfang anpassbar. Die Preisdetails der Pläne Pro und Enterprise werden nach der Kontoerstellung auf der Preisseite mitgeteilt.","nav.news":"Aktuelles","news.eyebrow":"Aktuelles","news.title":"Vereinfachung der EU-KI-Verordnung: der Digital Omnibus on AI ist verabschiedet","news.date":"Paris, 7. Juli 2026","news.body":"<p>Am 29. Juni 2026 erteilte der Rat der Europäischen Union dem Digital Omnibus on AI die endgültige Zustimmung, nach der Abstimmung des Europäischen Parlaments am 16. Juni. Als Teil des Digitalpakets Omnibus VII zur Vereinfachung passt der Text den Zeitplan und mehrere Pflichten der Verordnung (EU) 2024/1689 über künstliche Intelligenz an.</p><h4>Angepasster Zeitplan, Pflichten bleiben bestehen</h4><p>Die Pflichten für Hochrisikosysteme nach Anhang III werden auf den 2. Dezember 2027 verschoben, jene für in regulierte Produkte integrierte Systeme (Anhang I) auf den 2. August 2028 und jene für Behörden auf den 2. August 2030. Die Kennzeichnung synthetischer Inhalte nach Artikel 50(2) wird für bereits auf dem Markt befindliche Systeme auf den 2. Dezember 2026 verschoben. Die übrigen Transparenzpflichten bleiben auf den 2. August 2026 festgelegt.</p><h4>Neue Verbote und gezielte Erleichterungen</h4><p>Artikel 5 wird um zwei Verbote ergänzt, anwendbar ab dem 2. Dezember 2026: Nudification-Systeme und Systeme zur Erzeugung von Material über sexuellen Kindesmissbrauch. Die KI-Kompetenzpflicht nach Artikel 4 wird gelockert, und ein neuer Artikel 4a regelt die Verarbeitung sensibler Daten ausschließlich zur Korrektur von Verzerrungen. Erleichterungen werden auf kleine Mid-Cap-Unternehmen ausgeweitet.</p><h4>Die Einschätzung von CONSEILPREV</h4><blockquote>Diese Verschiebung ist keine Pause, sondern ein Fenster, um die Compliance in Ruhe zu strukturieren. Organisationen, die vorausschauend handeln, gehen die Fristen mit einem entscheidenden Vorteil an.</blockquote><p>Zur Unterstützung dieses Weges stellt CONSEILPREV seine Plattform Sentinel bereit, die den AI Act, die DSGVO und die Norm ISO/IEC 42001 integriert – vom Systemregister bis zum globalen Compliance-Index.</p><p><strong>Pressekontakt</strong> — Christophe Cerf · christophe.cerf@outlook.com</p><p><small>Informativer Beitrag, keine Rechtsberatung; die Fristen sind anhand des im Amtsblatt der Europäischen Union veröffentlichten Textes zu überprüfen.</small></p>","nav.normes":"Normen","nav.data":"Daten","nav.svc":"Services","nav.contact":"Kontakt","hero.ey":"MCP Connector data.gouv.fr Paris 2025","hero.h1":"Compliance <em>KI Data Cyber</em><br>datengesteuert","hero.sub":"CONSEILPREV verbindet Ihr Unternehmen mit oeffentlichen Daten fuer KI-Act, NIS2 und DSGVO.","hero.b1":"Daten erkunden","hero.b2":"Unsere Dienste","stats.a":"Jahre Expertise","stats.b":"Systemische Risiken","stats.c":"Normen","stats.d":"Datensaetze","stats.e":"Organisationen","nr.lbl":"Regulatorische Compliance","nr.ttl":"6 Normen gemeistert, <em>ein integrierter Ansatz</em>","nr.ia":"Ethische KI-Regulierung","nr.42":"KI-Management","nr.27":"Informationssicherheit","nr.dora":"Digitale Resilienz","nr.nis":"EU-Cybersicherheit","nr.rgpd":"Privacy by Design","ds.lbl":"MCP-Connector data.gouv.fr","ds.ttl":"Oeffentliche Daten <em>in Echtzeit</em>","ds.sub":"44 offizielle Datensaetze, 37 Organisationen, 16 Sektoren.","ds.theme":"Thema","ds.org":"Organisation","ds.fmt":"Format","ds.all":"Alle","ds.ph":"Freie Suche","ds.btn":"Suchen","ds.prev":"Zurueck","ds.next":"Weiter","ds.hint":"Datensatz anklicken","ds.none":"Kein Datensatz gefunden","ds.avail":"verfuegbar","ds.availp":"verfuegbar","sv.lbl":"Dienstleistungen","sv.ttl":"Beratung, Audit und <em>Daten-Intelligenz</em>","sv.a.t":"KI und Cyber-Audit","sv.a.d":"KI- und Cyber-Reifegrad.","sv.b.t":"8 systemische KI-Risiken","sv.b.d":"Jurisdiktionell, wirtschaftlich, Daten, operativ, geopolitisch, Cyber, Lieferkette, Umwelt.","sv.c.t":"MCP-Connector data.gouv.fr","sv.c.d":"Integration offizieller Datensaetze.","sv.d.t":"Governance und GRC","sv.d.d":"KI/Cyber-Governance: Richtlinien, KPIs.","ct.lbl":"Kontakt","ct.ttl":"Lassen Sie uns die Zukunft <em>gemeinsam</em> gestalten","ct.sub":"Investor, Partner oder Kunde? Lassen Sie uns zusammenarbeiten.","fm.ttl":"Kontaktieren Sie uns","fm.sub":"Antwort innerhalb 24h","fm.name":"Ihr Name","fm.email":"E-Mail","fm.co":"Unternehmen","fm.sub2":"Betreff","fm.msg":"Ihre Nachricht","fm.send":"Absenden","fm.s1":"KI/Cyber-Audit","fm.s2":"Regulatorische Compliance","fm.s3":"Investition","fm.s4":"Partnerschaft","fm.s5":"Sonstiges","fm.ok":"Nachricht gesendet!","fm.err":"Fehler: contact@i-aes.com","fm.rl":"Zu viele Versuche.","fm.spam":"Validierungsfehler.","fm.req":"Bitte alle Pflichtfelder ausfullen.","fm.inv":"Ungueltige E-Mail.","ft.desc":"KI Daten Cyber Business Unit Paris 2025","ft.svc":"Dienste","ft.nrm":"Normen","ch.ttl":"CONSEILPREV Experte","ch.sub":"Claude + Mistral KI Compliance","ch.q1":"Was ist der KI-Act?","ch.q2":"Wie NIS2 einhalten?","ch.q3":"8 KI-Risiken?","ch.q4":"ISO 27001 vs DORA?","ch.ph":"Ihre Frage","ch.hi":"Hallo! Fragen zu KI-Act, NIS2, DSGVO?<br><small>🤖 KI — Art. 50 VO (EU) 2024/1689</small>","dl":"Herunterladen","pg":"Auf data.gouv.fr","ru":"Nutzung","vi":"Aufrufe","fi":"Dateien","rs":"Ressourcen","nav.risques":"KI-Risiken","nav.expertise":"Expertise","sec.lbl":"Adressierte Maerkte","sec.ttl":"<em>Interventions</em>sektoren","sec.sub":"Bewaehrte Sektorexpertise in anspruchsvollen industriellen Umgebungen.","risk.lbl":"Bedrohungskartierung","risk.ttl":"8 systemische KI-Risiken <em>die wir adressieren</em>","pole.lbl":"Unsere drei Bereiche","pole.ttl":"Dreiteilige Expertise<br><em>fuer Ihre Herausforderungen</em>","pole.sub":"Kuenstliche Intelligenz, Daten &amp; Governance, Cybersicherheit — drei Disziplinen fuer eine vollstaendige integrierte Vision.","sv.ttl2":"Beratung, Audit &amp; <em>KI-Compliance</em>","diff.lbl":"Warum uns waehlen","diff.ttl":"<em>Was uns auszeichnet</em>","av.title":"Lassen Sie uns die Zukunft gestalten","av.sub":"gemeinsam","av.desc":"Investor, Partner oder Kunde? Erkunden wir,<br>wie CONSEILPREV Wert fuer Sie schaffen kann.","ct.lbl2":"Projektformular","ct.ttl2":"Ihr <em>KI &amp; Cyber</em>-Projekt einreichen",">KI &amp; Cyber</em>-Projekt einreichen":"Unser Angebot herunterladen:","nav.secteurs":"Sektoren","nav.donnees":"Daten","nav.contact2":"Kontakt","hero.badge":"Sentinel AI — KI-Governance","hero.title1":"Ihr Kontrollturm","hero.title2":"KI-Governance","hero.tagline":"Kartieren Sie Ihre KI-Systeme, bewerten Sie deren Konformitaet und steuern Sie Ihren Fahrplan — EU KI-Act, NIS2 und DSGVO in einem vernetzten Echtzeit-Tool.","hero.btn.aies":"Sentinel AI aufrufen →","hero.btn.demo":"▷ Demo","hero.btn.offres":"⬛ Mit einem Experten sprechen","pillars.label":"IHR COMPLIANCE-WEG IN 3 SCHRITTEN","pillars.c1.t":"Kartieren","pillars.c1.d":"Inventarisierung und Klassifizierung Ihrer KI-Systeme gemaess Anhang III des KI-Act.","pillars.c2.t":"Bewerten","pillars.c2.d":"Multikriterien-Scoring: Grundrechte, Sicherheit, Daten-Governance.","pillars.c3.t":"Planen","pillars.c3.d":"Priorisierter Fahrplan mit regulatorischen Fristen und einem CONSEILPREV-Aktionsplan.","promo.label":"🚀 EINSFUEHRANGEBOT","promo.title":"KI-Management","promo.desc":"KI-Governance, KI-Act &amp; DSGVO-Konformitaet mit integrierter KI","promo.discount":"auf alle Ihre KI &amp; Cyber-Projekte","promo.limited":"⏱ Begrenztes Angebot – Noch","promo.cta":"Angebot nutzen →","comp.title":"REGULATORISCHE COMPLIANCE","dn.back":"← Zurueck zur Website","dn.cta.ttl":"Benoetigen Sie <em style=\\\\\\\\",">Unterstuetzung</em>?":"Unsere CONSEILPREV-Experten begleiten Sie bei der Nutzung oeffentlicher Daten fuer Ihre Compliance.","dn.cta.btn1":"Projekt einreichen →","dn.cta.btn2":"📄 Whitepaper","fl.prenom":"Vorname","fl.nom":"Nachname","fl.email":"E-Mail-Adresse","fl.tel":"Telefon","fl.co":"Unternehmen","fl.role":"Position / Funktion","fl.sector":"Branche","fl.size":"Unternehmensgrösse","fl.project":"KI / Cyber-Projekttyp","fl.budget":"Geschätztes Budget","fl.delay":"Gewünschter Zeitrahmen","fl.country":"Land / Region","fl.norm":"Angestrebte Normen","fl.desc":"Beschreibung Ihres Bedarfs","fl.source":"Wie haben Sie uns gefunden?","fp.prenom":"Johann","fp.nom":"Mueller","fp.email":"johann.mueller@firma.de","fp.tel":"+49 1 000 000 00","fp.co":"Ihr Unternehmensname","fp.role":"CIO, CISO, DPO, CTO…","fp.desc":"Beschreiben Sie Ihr Projekt, Ihre Herausforderungen, regulatorischen Anforderungen…","fs.sector":"— Sektor auswählen —","fs.size":"— Mitarbeiterzahl —","fs.project":"— Projekttyp auswählen —","fs.budget":"— Budgetrahmen —","fs.delay":"— Startzeitraum —","fs.country":"— Land —","fs.norm":"— Referenzrahmen —","fs.source":"— Quelle —","og.ia":"🧠 KI & Governance","og.cyber":"🛡️ Cybersicherheit","og.rgpd":"🔒 DSGVO & Daten","og.data":"📊 Daten & MCP","og.ot":"🏭 Industrie & OT","og.eur":"€ Euro","og.usd":"$ USD","form.consent":"Ich stimme zu, dass meine Daten von <strong>CONSEILPREV</strong> im Rahmen meiner Kontaktanfrage gemäss der <a href=\\\\\\u0027#\\\\\\u0027 class=\\\\\\u0027pclink\\\\\\u0027>Datenschutzrichtlinie</a> verarbeitet werden. Keine Daten werden mit Dritten geteilt.","form.reply":"Antwort garantiert innerhalb von 24 Wertstunden · <a href=\\\\\\u0027mailto:christophe.cerf@outlook.com\\\\\\u0027 class=\\\\\\u0027pclink\\\\\\u0027>christophe.cerf@outlook.com</a>","form.dl":"Unser Angebot herunterladen:","sc.energie":"⚡ Energie","sc.oilgas":"🛢️ Öl &amp; Gas","sc.ferro":"🚃 Eisenbahn","sc.auto":"🚗 Automobilindustrie","sc.indlourde":"🏗️ Schwerindustrie","sc.manufact":"⚙️ Fertigung","sc.chimie":"⚗️ Chemie &amp; Raffination","sc.sante":"❤️ Gesundheit","sc.finance":"💲 Finanzen","sc.logistique":"🚛 Logistik","sc.aero":"✈️ Luft- und Raumfahrt","sc.public":"🏛️ Öffentlicher Sektor","rk.juri.t":"Jurisdiktionell","rk.juri.d":"Cloud Act · extraterritoriale Gesetze · Sanktionen · Datensouveränität","rk.juri.tag":"Recht &amp; Regulierung","rk.eco.t":"Wirtschaftlich","rk.eco.d":"Ausgabenkonzentration · Abhängigkeit von proprietären Modellen · Tarifelastizität","rk.eco.tag":"Finanzen","rk.data.t":"Daten &amp; KI","rk.data.d":"Gebundene Daten · Foundation-Lock-in · algorithmische Verzerrung · Datenqualität","rk.data.tag":"Technisch","rk.ops.t":"Operationell","rk.ops.d":"Seltene Kompetenzen · GPU-Lieferkette · Anbieterabhängigkeit","rk.ops.tag":"Betrieb","rk.geo.t":"Geopolitisch","rk.geo.d":"Technologische Spannungen · Exportbeschränkungen · Internet-Fragmentierung","rk.geo.tag":"Strategie","rk.cyber.t":"Cyber","rk.cyber.d":"Erweiterte Angriffsfläche · gegnerische Angriffe · böswillige Halluzinationen","rk.cyber.tag":"Sicherheit","rk.sc.t":"Tech-Lieferkette","rk.sc.d":"Proprietärer Lock-in · Portabilität · Obsoleszenz · eingeschränkte Interoperabilität","rk.sc.tag":"Infrastruktur","rk.env.t":"Umweltbezogen","rk.env.d":"Energieintensive Rechenzentren · Cloud-CO2-Bilanz · generativer KI-Fussabdruck","rk.env.tag":"ESG","risk.cta.txt":"Diese 8 Risiken sind in Sentinel AI bereits fuer 46 Rechtsordnungen kartiert und bewertet.","risk.cta.btn":"Sentinel AI entdecken →","df.ai.t":"Massgeschneiderte KI-Assistenten","df.ai.d":"Assistenten, die Ihre Unternehmenssprache verstehen und nahtlos in Ihre bestehenden Arbeitsabläufe integriert werden.","df.ind.t":"Industriell trainierte Agenten","df.ind.d":"Für mehr als 20 Industriesektoren vortrainiert liefern unsere Agenten konkrete und messbare Ergebnisse.","df.eco.t":"Operationelle Kostenoptimierung","df.eco.d":"Optimierung der Betriebskosten durch intelligente Automatisierung und prädiktive Modelle.","df.exp.t":"32 Jahre Branchenexpertise","df.exp.d":"Energie, Öl &amp; Gas, Industrie, Finanzen, Gesundheit — Praxiswissen aus anspruchsvollsten Umgebungen.","df.jur.t":"Doppelte juristische &amp; Tech-Expertise","df.jur.d":"Regulatorische Compliance und technische Umsetzung in einem integrierten und kohärenten Ansatz vereint.","df.intl.t":"Internationale Abdeckung","df.intl.d":"Tätigkeit in Frankreich, Europa, Nahost und Nordamerika. Beherrschung übergreifender Vorschriften.","po.ia.t":"Künstliche Intelligenz","po.ia.d":"Verantwortungsvoller KI-Einsatz, KI-Act-Konformität, algorithmische Governance und Hochrisikosystem-Bewertung.","po.data.t":"Daten &amp; Governance","po.data.d":"Datenarchitektur, DSGVO-Konformität, Data Mesh, Qualität und Lineage — Daten in einen sicheren strategischen Vermögenswert umwandeln.","po.cyber.t":"Cybersicherheit","po.cyber.d":"Audit, NIS2 &amp; ISO 27001-Konformität, operative Resilienz und Schutz kritischer industrieller OT/IT-Systeme.","sv.audit.t":"KI &amp; Cyber-Audit","sv.audit.d":"Vollständige Bewertung Ihrer KI- und Cyber-Reife, Risikoanalyse und regulatorische Lückenanalyse.","sv.r8.t":"Bewertung der 8 KI-Risiken","sv.r8.d":"Systemische Analyse von KI-Einsatzrisiken: Verzerrung, Robustheit, Sicherheit und grundlegende Auswirkungen.","sv.conf.t":"Compliance-Beratung","sv.conf.d":"Strategische Begleitung zur Erreichung und Aufrechterhaltung regulatorischer Compliance im gesamten Umfang.","sv.integ.t":"KI-Lösungsintegration","sv.integ.d":"Einsatz massgeschneiderter KI-Lösungen zur Automatisierung Ihrer Prozesse und Produktivitätssteigerung.","sv.form.t":"Schulung &amp; Begleitung","sv.form.d":"Zertifizierungsprogramme zur Beherrschung von KI-, Daten- und Cyber-Herausforderungen in Ihren Teams.","sv.grc.t":"Governance &amp; GRC","sv.grc.d":"Integrierte KI/Cyber-Governance-Rahmen: Richtlinien, Ausschüsse, KPIs und Compliance-Reporting.","sv.audit.l1":"KI-Act / ISO 42001 Konformitätsprüfung","sv.audit.l2":"ISO 27001 / NIS2 Sicherheitsaudit","sv.audit.l3":"KI &amp; Daten-Architekturüberprüfung","sv.audit.l4":"Lückenbericht &amp; Empfehlungen","sv.r8.l1":"Risikoklassifizierung von Systemen","sv.r8.l2":"Algorithmische Wirkungsanalyse","sv.r8.l3":"Matrix der 8 systemischen Risiken","sv.r8.l4":"Nachbereitungsüberwachung","sv.conf.l1":"KI-Act Compliance-Fahrplan","sv.conf.l2":"ISO 27001 ISMS-Einführung","sv.conf.l3":"NIS2 / DORA Compliance-Programm","sv.conf.l4":"DSGVO &amp; Privacy by Design","sv.integ.l1":"Industrielle KI-Agenten-Entwicklung","sv.integ.l2":"Geschäftsprozessautomatisierung","sv.integ.l3":"Digitale Zwillinge &amp; IoT","sv.integ.l4":"MLOps &amp; KI-Überwachung","sv.form.l1":"KI-Act Zertifizierungsschulung","sv.form.l2":"NIS2 Cybersicherheits-Workshops","sv.form.l3":"CIO/CISO Team-Coaching","sv.form.l4":"KI Change-Management","sv.grc.l1":"KI-Charta &amp; Governance-Politik","sv.grc.l2":"KI &amp; Cyber GRC-Ausschuss","sv.grc.l3":"KPIs und Compliance-Berichterstattung","sv.grc.l4":"Drittanbieter-KI-Verwaltung","ft.brand":"KI Daten Cyber Business Unit<br>MCP-Connector data.gouv.fr · Paris 2025","ft.svc.lbl":"Dienste","ft.nrm.lbl":"Normen","ft.res.lbl":"Ressourcen","ft.svc.l1":"KI &amp; Cyber-Audit","ft.svc.l2":"8 systemische KI-Risiken","ft.svc.l3":"MCP-Connector data.gouv.fr","ft.svc.l4":"Schulung &amp; Begleitung","ft.svc.l5":"Governance &amp; GRC","ft.nrm.l1":"KI-Act · ISO 42001","ft.nrm.l2":"NIS2 · ISO 27001","ft.nrm.l3":"DORA · DSGVO","ft.nrm.l4":"8 systemische KI-Risiken","ft.nrm.l5":"KI &amp; ROI-Whitepaper","ft.res.l1":"📄 Whitepaper","ft.res.l2":"Datensätze data.gouv.fr","ft.res.l3":"Projekt einreichen","ft.res.l4":"christophe.cerf@outlook.com","ft.copy":"© 2025 CONSEILPREV · ERSIA KI-MANAGEMENT · i-aes.com","ft.tag":"MCP · DATA.GOUV.FR · PARIS","og.gbp":"£ GBP","clients.title":"50 Unternehmen aus allen Branchen vertrauen uns seit 2014","clients.sectors":"<span>Technologie</span> · <span>Finanzen</span> · <span>Gesundheit</span> · <span>Versicherung</span> · <span>Energie</span> · <span>Industrie</span> · <span>Einzelhandel</span>","ft.prod.lbl":"Produkte","ft.prod.l1":"Sentinel AI-Funktionen","ft.prod.l2":"Interaktive Demo","ft.prod.l4":"Hilfe &amp; Barrierefreiheit","ft.support.lbl":"Support","ft.support.l1":"Kontakt","ft.support.l2":"FAQ","ft.support.l3":"Hilfecenter","ft.legal.lbl":"Rechtliches","ft.legal.l1":"Impressum","ft.legal.l2":"Datenschutz","ft.legal.l3":"AGB","ft.legal.l4":"Datenschutzrichtlinie","ft.legal.l5":"DSA-Auswirkungen","ft.plans.lbl":"Abonnements","ft.plans.l1":"Sentinel Kostenlos","ft.plans.l2":"Sentinel Pro ⭐ Beliebt","ft.plans.l3":"Sentinel Enterprise","ft.nl.title":"Bleiben Sie über die neuesten KI-Nachrichten informiert","ft.nl.desc":"Erhalten Sie unsere Expertenratschläge, regulatorische Updates und Best Practices direkt in Ihrem Posteingang.","ft.nl.ph":"Ihre geschäftliche E-Mail","ft.nl.btn":"Anmelden →","ft.nl.check":"Wöchentlichen Newsletter mit den neuesten KI- &amp; Compliance-Nachrichten erhalten","ft.nl.note":"Geschäftliche E-Mail erforderlich. Jederzeit abmeldbar."}`)
};
function ii(k){return (T[LANG]||T.fr)[k]||(T.fr)[k]||k;}
// Scroll vers #poles avec offset nav
function scrollToPoles(e){
  if(e) e.preventDefault();
  /* Plusieurs cibles possibles, dans l'ordre de preference : la premiere qui
     existe l'emporte. Chercher un seul identifiant et abandonner en silence
     s'il a disparu, c'est ce qui rendait cette entree de menu inerte. */
  var el=null, cibles=['differenciateurs','services','secteurs'];
  for(var i=0;i<cibles.length && !el;i++) el=document.getElementById(cibles[i]);
  if(!el) return;
  var navH=document.querySelector('nav')?document.querySelector('nav').offsetHeight:70;
  var top=el.getBoundingClientRect().top+window.scrollY-navH-8;
  window.scrollTo({top:top,behavior:'smooth'});
}

function applyLang(){
  document.documentElement.lang=LANG;
  document.querySelectorAll('[data-i18n]').forEach(function(el){
    var v=ii(el.dataset.i18n);if(v)el.innerHTML=v;
  });
  document.querySelectorAll('[data-i18n-ph]').forEach(function(el){
    var v=ii(el.dataset.i18nPh);if(v)el.placeholder=v;
  });
  var xi=document.getElementById('xinp');
  if(xi)xi.placeholder=ii('ch.ph');
  var qs=['ch.q1','ch.q2','ch.q3','ch.q4'];
  document.querySelectorAll('#xsugg .xsg').forEach(function(b,idx){
    if(qs[idx])b.textContent=ii(qs[idx]);
  });
  if(typeof xRender==='function')xRender();
  if(typeof updateFormSelects==='function')updateFormSelects();
}
function setLang(lang){
  LANG=lang;
  document.querySelectorAll('.lbtn').forEach(function(b){
    b.classList.toggle('on',b.dataset.lang===lang);
  });
  var u=new URL(window.location.href);
  u.searchParams.set('lang',lang);
  history.replaceState({},'',u);
  applyLang();
}
var FORM_OPTS={"sector":{"fr":[["","— Sélectionnez un secteur —"],["energie","⚡ Énergie & Utilities"],["oil-gas","🛢️ Oil & Gas"],["industrie","🏭 Industrie & Manufacturing"],["finance","💰 Banque & Finance"],["assurance","🛡️ Assurance"],["sante","🏥 Santé & Pharma"],["transport","🚆 Transport & Logistique"],["immobilier","🏠 Immobilier & Construction"],["telecom","📡 Télécoms & Médias"],["retail","🛒 Retail & Distribution"],["public","🏛️ Secteur Public & Collectivités"],["defense","🎖️ Défense & Sécurité"],["agroalimentaire","🌾 Agroalimentaire"],["tech","💻 Tech & Startups"],["conseil","🎯 Conseil & Services"],["autre","➕ Autre"]],"en":[["","— Select a sector —"],["energie","⚡ Energy & Utilities"],["oil-gas","🛢️ Oil & Gas"],["industrie","🏭 Industry & Manufacturing"],["finance","💰 Banking & Finance"],["assurance","🛡️ Insurance"],["sante","🏥 Healthcare & Pharma"],["transport","🚆 Transport & Logistics"],["immobilier","🏠 Real Estate & Construction"],["telecom","📡 Telecoms & Media"],["retail","🛒 Retail & Distribution"],["public","🏛️ Public Sector & Local Government"],["defense","🎖️ Defence & Security"],["agroalimentaire","🌾 Agri-food"],["tech","💻 Tech & Startups"],["conseil","🎯 Consulting & Services"],["autre","➕ Other"]],"de":[["","— Sektor auswählen —"],["energie","⚡ Energie & Versorgung"],["oil-gas","🛢️ Öl & Gas"],["industrie","🏭 Industrie & Fertigung"],["finance","💰 Banken & Finanzen"],["assurance","🛡️ Versicherung"],["sante","🏥 Gesundheit & Pharma"],["transport","🚆 Transport & Logistik"],["immobilier","🏠 Immobilien & Bau"],["telecom","📡 Telekommunikation & Medien"],["retail","🛒 Einzelhandel & Vertrieb"],["public","🏛️ Öffentlicher Sektor"],["defense","🎖️ Verteidigung & Sicherheit"],["agroalimentaire","🌾 Lebensmittelindustrie"],["tech","💻 Tech & Startups"],["conseil","🎯 Beratung & Dienstleistungen"],["autre","➕ Sonstiges"]]},"size":{"fr":[["","— Effectif —"],["1-10","1 – 10 salariés"],["11-50","11 – 50 salariés"],["51-250","51 – 250 salariés"],["251-1000","251 – 1 000 salariés"],["1001-5000","1 001 – 5 000 salariés"],["5000+","5 000+ salariés"]],"en":[["","— Company size —"],["1-10","1 – 10 employees"],["11-50","11 – 50 employees"],["51-250","51 – 250 employees"],["251-1000","251 – 1,000 employees"],["1001-5000","1,001 – 5,000 employees"],["5000+","5,000+ employees"]],"de":[["","— Mitarbeiterzahl —"],["1-10","1 – 10 Mitarbeiter"],["11-50","11 – 50 Mitarbeiter"],["51-250","51 – 250 Mitarbeiter"],["251-1000","251 – 1 000 Mitarbeiter"],["1001-5000","1 001 – 5 000 Mitarbeiter"],["5000+","5 000+ Mitarbeiter"]]},"delay":{"fr":[["","— Horizon de démarrage —"],["urgent","🔴 Urgent — sous 2 semaines"],["1mois","🟠 Dans le mois"],["3mois","🟡 Sous 3 mois"],["6mois","🟢 Sous 6 mois"],["annee","📅 Horizon 1 an"],["exploration","💡 Phase d'exploration"]],"en":[["","— Start timeline —"],["urgent","🔴 Urgent — within 2 weeks"],["1mois","🟠 Within the month"],["3mois","🟡 Within 3 months"],["6mois","🟢 Within 6 months"],["annee","📅 Within 1 year"],["exploration","💡 Exploration phase"]],"de":[["","— Startzeitraum —"],["urgent","🔴 Dringend — innerhalb 2 Wochen"],["1mois","🟠 Innerhalb des Monats"],["3mois","🟡 Innerhalb 3 Monate"],["6mois","🟢 Innerhalb 6 Monate"],["annee","📅 Innerhalb 1 Jahr"],["exploration","💡 Explorationsphase"]]},"country":{"fr":[["","— Pays —"],["FR","🇫🇷 France"],["BE","🇧🇪 Belgique"],["CH","🇨🇭 Suisse"],["LU","🇱🇺 Luxembourg"],["MC","🇲🇨 Monaco"],["DE","🇩🇪 Allemagne"],["UK","🇬🇧 Royaume-Uni"],["US","🇺🇸 États-Unis"],["CA","🇨🇦 Canada"],["AE","🇦🇪 EAU / Moyen-Orient"],["OTHER","🌍 Autre"]],"en":[["","— Country —"],["FR","🇫🇷 France"],["BE","🇧🇪 Belgium"],["CH","🇨🇭 Switzerland"],["LU","🇱🇺 Luxembourg"],["MC","🇲🇨 Monaco"],["DE","🇩🇪 Germany"],["UK","🇬🇧 United Kingdom"],["US","🇺🇸 United States"],["CA","🇨🇦 Canada"],["AE","🇦🇪 UAE / Middle East"],["OTHER","🌍 Other"]],"de":[["","— Land —"],["FR","🇫🇷 Frankreich"],["BE","🇧🇪 Belgien"],["CH","🇨🇭 Schweiz"],["LU","🇱🇺 Luxemburg"],["MC","🇲🇨 Monaco"],["DE","🇩🇪 Deutschland"],["UK","🇬🇧 Vereinigtes Königreich"],["US","🇺🇸 Vereinigte Staaten"],["CA","🇨🇦 Kanada"],["AE","🇦🇪 VAE / Nahost"],["OTHER","🌍 Sonstiges"]]},"norm":{"fr":[["","— Référentiel —"],["ia-act","IA Act européen"],["iso42001","ISO 42001"],["nis2","NIS2"],["iso27001","ISO 27001"],["dora","DORA"],["rgpd","RGPD / GDPR"],["soc2","SOC 2"],["hds","HDS (Santé)"],["pci-dss","PCI-DSS"],["nist","NIST CSF"],["multi","Plusieurs normes"]],"en":[["","— Framework —"],["ia-act","EU AI Act"],["iso42001","ISO 42001"],["nis2","NIS2"],["iso27001","ISO 27001"],["dora","DORA"],["rgpd","GDPR"],["soc2","SOC 2"],["hds","HDS (Healthcare)"],["pci-dss","PCI-DSS"],["nist","NIST CSF"],["multi","Multiple standards"]],"de":[["","— Referenzrahmen —"],["ia-act","EU-KI-Act"],["iso42001","ISO 42001"],["nis2","NIS2"],["iso27001","ISO 27001"],["dora","DORA"],["rgpd","DSGVO"],["soc2","SOC 2"],["hds","HDS (Gesundheit)"],["pci-dss","PCI-DSS"],["nist","NIST CSF"],["multi","Mehrere Normen"]]},"source":{"fr":[["","— Source —"],["linkedin","LinkedIn"],["google","Google / Moteur de recherche"],["recommandation","Recommandation"],["evenement","Événement / Conférence"],["presse","Presse / Article"],["data-gouv","Portail data.gouv.fr"],["autre","Autre"]],"en":[["","— Source —"],["linkedin","LinkedIn"],["google","Google / Search engine"],["recommandation","Recommendation"],["evenement","Event / Conference"],["presse","Press / Article"],["data-gouv","data.gouv.fr portal"],["autre","Other"]],"de":[["","— Quelle —"],["linkedin","LinkedIn"],["google","Google / Suchmaschine"],["recommandation","Empfehlung"],["evenement","Veranstaltung / Konferenz"],["presse","Presse / Artikel"],["data-gouv","data.gouv.fr-Portal"],["autre","Sonstiges"]]},"project":{"fr":{"og-ia":["🧠 IA & Gouvernance",[["audit-ia","Audit de conformité IA Act (ISO 42001)"],["gouvernance-ia","Gouvernance IA — Comité & Politiques"],["risques-ia","Évaluation 8 risques systémiques IA"],["aipd","Analyse d'Impact IA (AIPD / DPIA)"],["chatbot-ia","Déploiement IA conversationnelle / LLM"],["ia-industrielle","IA industrielle — Maintenance prédictive, vision"],["ia-ingenierie","IA ingénierie industrielle"],["formation-ia","Formation & sensibilisation IA Act"]]],"og-cyber":["🛡️ Cybersécurité",[["audit-nis2","Audit NIS2 — Entités essentielles / importantes"],["audit-iso27","Audit ISO 27001 / SMSI"],["dora","Conformité DORA — Résilience opérationnelle"],["pen-test","Test d'intrusion / Red Team"],["soc","SOC & détection d'incidents"],["grc","GRC — Gouvernance, Risques, Conformité"]]],"og-rgpd":["🔒 RGPD & Données",[["rgpd","Mise en conformité RGPD"],["dpo","Délégué à la Protection des Données (DPO)"],["violations","Gestion des violations de données"]]],"og-data":["📊 Data & MCP",[["mcp-datagouv","Connecteur MCP data.gouv.fr"],["data-strategy","Stratégie Data & IA"],["dashboard","Dashboard IA — Tableau de bord décisionnel"]]],"og-ot":["🏭 Industrie & OT",[["cybersec-ot","Cybersécurité OT/ICS/SCADA"],["oiv","Protection OIV / Seveso"],["continuity","Plan de continuité d'activité (PCA/PRA)"]]]},"en":{"og-ia":["🧠 AI & Governance",[["audit-ia","AI Act compliance audit (ISO 42001)"],["gouvernance-ia","AI Governance — Committee & Policies"],["risques-ia","8 systemic AI risks assessment"],["aipd","AI Impact Assessment (AIPD / DPIA)"],["chatbot-ia","Conversational AI / LLM deployment"],["ia-industrielle","Industrial AI — Predictive maintenance, vision"],["ia-ingenierie","Industrial engineering AI"],["formation-ia","AI Act training & awareness"]]],"og-cyber":["🛡️ Cybersecurity",[["audit-nis2","NIS2 Audit — Essential / important entities"],["audit-iso27","ISO 27001 / ISMS Audit"],["dora","DORA Compliance — Operational resilience"],["pen-test","Penetration test / Red Team"],["soc","SOC & incident detection"],["grc","GRC — Governance, Risk, Compliance"]]],"og-rgpd":["🔒 GDPR & Data",[["rgpd","GDPR compliance"],["dpo","Data Protection Officer (DPO)"],["violations","Data breach management"]]],"og-data":["📊 Data & MCP",[["mcp-datagouv","MCP Connector data.gouv.fr"],["data-strategy","Data & AI Strategy"],["dashboard","AI Dashboard — Decision support"]]],"og-ot":["🏭 Industry & OT",[["cybersec-ot","OT/ICS/SCADA Cybersecurity"],["oiv","OIV / Seveso Protection"],["continuity","Business continuity plan (BCP/DRP)"]]]},"de":{"og-ia":["🧠 KI & Governance",[["audit-ia","KI-Act Konformitätsprüfung (ISO 42001)"],["gouvernance-ia","KI-Governance — Ausschuss & Richtlinien"],["risques-ia","Bewertung 8 systemischer KI-Risiken"],["aipd","KI-Folgenabschätzung (AIPD / DPIA)"],["chatbot-ia","Konversations-KI / LLM-Einsatz"],["ia-industrielle","Industrielle KI — Prädiktive Wartung, Vision"],["ia-ingenierie","Industrie-Engineering KI"],["formation-ia","KI-Act Schulung & Sensibilisierung"]]],"og-cyber":["🛡️ Cybersicherheit",[["audit-nis2","NIS2-Audit — Wesentliche / wichtige Einrichtungen"],["audit-iso27","ISO 27001 / ISMS-Audit"],["dora","DORA-Compliance — Operative Resilienz"],["pen-test","Penetrationstest / Red Team"],["soc","SOC & Vorfallserkennung"],["grc","GRC — Governance, Risiko, Compliance"]]],"og-rgpd":["🔒 DSGVO & Daten",[["rgpd","DSGVO-Compliance"],["dpo","Datenschutzbeauftragter (DSB)"],["violations","Datenpannenverwaltung"]]],"og-data":["📊 Daten & MCP",[["mcp-datagouv","MCP-Connector data.gouv.fr"],["data-strategy","Daten- & KI-Strategie"],["dashboard","KI-Dashboard — Entscheidungsunterstützung"]]],"og-ot":["🏭 Industrie & OT",[["cybersec-ot","OT/ICS/SCADA Cybersicherheit"],["oiv","OIV / Seveso Schutz"],["continuity","Geschäftskontinuitätsplan (BCP/DRP)"]]]}}};
function updateFormSelects(){
  (function(){
    var sel=document.getElementById('pf-sector');
    if(!sel)return;
    var cur=sel.value;
    var opts=FORM_OPTS['sector'][LANG]||FORM_OPTS['sector']['fr'];
    sel.innerHTML='';
    opts.forEach(function(o){
      var el=document.createElement('option');
      el.value=o[0];el.textContent=o[1];
      if(o[0]===cur)el.selected=true;
      sel.appendChild(el);
    });
  })();
  (function(){
    var sel=document.getElementById('pf-size');
    if(!sel)return;
    var cur=sel.value;
    var opts=FORM_OPTS['size'][LANG]||FORM_OPTS['size']['fr'];
    sel.innerHTML='';
    opts.forEach(function(o){
      var el=document.createElement('option');
      el.value=o[0];el.textContent=o[1];
      if(o[0]===cur)el.selected=true;
      sel.appendChild(el);
    });
  })();
  (function(){
    var sel=document.getElementById('pf-delay');
    if(!sel)return;
    var cur=sel.value;
    var opts=FORM_OPTS['delay'][LANG]||FORM_OPTS['delay']['fr'];
    sel.innerHTML='';
    opts.forEach(function(o){
      var el=document.createElement('option');
      el.value=o[0];el.textContent=o[1];
      if(o[0]===cur)el.selected=true;
      sel.appendChild(el);
    });
  })();
  (function(){
    var sel=document.getElementById('pf-country');
    if(!sel)return;
    var cur=sel.value;
    var opts=FORM_OPTS['country'][LANG]||FORM_OPTS['country']['fr'];
    sel.innerHTML='';
    opts.forEach(function(o){
      var el=document.createElement('option');
      el.value=o[0];el.textContent=o[1];
      if(o[0]===cur)el.selected=true;
      sel.appendChild(el);
    });
  })();
  (function(){
    var sel=document.getElementById('pf-norm');
    if(!sel)return;
    var cur=sel.value;
    var opts=FORM_OPTS['norm'][LANG]||FORM_OPTS['norm']['fr'];
    sel.innerHTML='';
    opts.forEach(function(o){
      var el=document.createElement('option');
      el.value=o[0];el.textContent=o[1];
      if(o[0]===cur)el.selected=true;
      sel.appendChild(el);
    });
  })();
  (function(){
    var sel=document.getElementById('pf-source');
    if(!sel)return;
    var cur=sel.value;
    var opts=FORM_OPTS['source'][LANG]||FORM_OPTS['source']['fr'];
    sel.innerHTML='';
    opts.forEach(function(o){
      var el=document.createElement('option');
      el.value=o[0];el.textContent=o[1];
      if(o[0]===cur)el.selected=true;
      sel.appendChild(el);
    });
  })();
  (function(){
    var sel=document.getElementById('pf-project');
    if(!sel)return;
    var cur=sel.value;
    var groups=FORM_OPTS['project'][LANG]||FORM_OPTS['project']['fr'];
    sel.innerHTML='<option value="">'+ii('fs.project')+'</option>';
    Object.keys(groups).forEach(function(ogId){
      var og=document.createElement('optgroup');
      og.label=groups[ogId][0];
      groups[ogId][1].forEach(function(o){
        var el=document.createElement('option');
        el.value=o[0];el.textContent=o[1];
        if(o[0]===cur)el.selected=true;
        og.appendChild(el);
      });
      sel.appendChild(og);
    });
  })();
}

// Attacher au lien nav (résiste aux innerHTML rewrites de applyLang)
document.addEventListener('DOMContentLoaded',function(){
  var link=document.getElementById('nav-expertise');
  if(link) link.addEventListener('click',scrollToPoles);
});
// Re-attacher après chaque applyLang
// scrollToPoles est attaché via onclick dans le HTML — pas besoin de wrapper


/* ftNlSubmit vivait ICI en double, à l'identique — la seconde
   définition écrasait celle-ci en silence. Une seule reste. */



// ════════════════════════════════════════

// Attacher au lien nav (résiste aux innerHTML rewrites de applyLang)
document.addEventListener('DOMContentLoaded',function(){
  var link=document.getElementById('nav-expertise');
  if(link) link.addEventListener('click',scrollToPoles);
});
// Re-attacher après chaque applyLang
// scrollToPoles est attaché via onclick dans le HTML — pas besoin de wrapper


function ftNlSubmit(e){
  e.preventDefault();
  var email=document.getElementById('ft-nl-email').value.trim();
  var st=document.getElementById('ft-nl-status');
  var at=email.indexOf('@');
  if(at<1||email.indexOf('.',at)<at+2){
    st.className='ft-nl-status err';
    st.textContent=LANG==='en'?'Invalid email.':LANG==='de'?'Ungültige E-Mail.':'Email invalide.';
    return;
  }
  var subj=encodeURIComponent('[CONSEILPREV] Newsletter IA');
  var body=encodeURIComponent('Inscription newsletter:\nEmail: '+email);
  window.open('mailto:christophe.cerf@outlook.com?subject='+subj+'&body='+body);
  st.className='ft-nl-status ok';
  /* CE MESSAGE MENTAIT. Rien n'est enregistré : on ouvre le client mail
     du visiteur avec un brouillon. S'il ne l'envoie pas, il n'est
     inscrit nulle part — et il croyait l'être. */
  st.textContent=LANG==='en'?'✉️ Draft ready — send it to confirm.':LANG==='de'?'✉️ Entwurf bereit — zum Bestätigen senden.':'✉️ Votre demande est prête — envoyez l’email pour confirmer.';
  e.target.reset();
}


// ════════════════════════════════════════
// WIDGET VEILLE IA — Flux RSS multi-sources
// ════════════════════════════════════════
(function(){
  "use strict";

  var V_OPEN = false;
  var V_CAT  = "all";
  var V_LANG = "all";
  var V_ITEMS = [];
  var V_INTERVAL = null;
  var V_LOADING = false;

  // Sources RSS via proxy public (rss2json ou allorigins)
  var V_SOURCES = [
    {name:"ActuIA",         url:"https://www.actuia.com/feed/",                      cat:"ai",    ico:"🤖"},
    {name:"ANSSI",          url:"https://cyber.gouv.fr/feed",                         cat:"secu",  ico:"🛡️"},
    {name:"CNIL",           url:"https://www.cnil.fr/fr/rss.xml",                    cat:"regl",  ico:"🔒"},
    {name:"LMI",            url:"https://www.lemondeinformatique.fr/rss/rss-actu.xml",cat:"innov", ico:"💻"},
    {name:"Usine Digitale", url:"https://www.usine-digitale.fr/rss/all",             cat:"innov", ico:"🏭"},
    {name:"AI Act EU",      url:"https://artificialintelligenceact.eu/feed/",         cat:"regl",  ico:"⚖️"},
    {name:"EU Digital",     url:"https://digital-strategy.ec.europa.eu/en/rss.xml",  cat:"intl",  ico:"🇪🇺"},
    {name:"Cybersec-info",  url:"https://cybersecurite-info.fr/feed/",               cat:"secu",  ico:"🔐"},
    {name:"Infosecurity Mag",url:"https://www.infosecurity-magazine.com/rss/news/",      cat:"secu",  ico:"🔏"},
  ];

  // Catégories -> icônes et labels
  var V_CAT_MAP = {
    regl: {label:"Réglementation", cls:"tag-regl", icoCls:"cat-regl"},
    secu: {label:"Sécurité",       cls:"tag-secu", icoCls:"cat-secu"},
    innov:{label:"Innovation",     cls:"tag-innov", icoCls:"cat-innov"},
    intl: {label:"International",  cls:"tag-intl", icoCls:"cat-intl"},
    fr:   {label:"France",         cls:"tag-fr",   icoCls:"cat-fr"},
    ai:   {label:"IA & Mistral",   cls:"tag-ai",   icoCls:"cat-ai"},
  };

  function vOpen(){
    var box = document.getElementById("vbox");
    if(!box){ console.warn("[vOpen] #vbox introuvable"); return; }
    V_OPEN = !V_OPEN;
    if(V_OPEN){
      box.classList.add("open");
      if(!V_ITEMS.length) vFetch();
      else { V_SCROLL_POS = 0; vStartScroll(); }
    } else {
      box.classList.remove("open");
      vStopScroll();
    }
  }
  window.vOpen = vOpen;

  function vFilter(btn, cat){
    document.querySelectorAll(".vf-btn").forEach(function(b){b.classList.remove("on");});
    btn.classList.add("on");
    V_CAT = cat;
    vRender();
  }
  window.vFilter = vFilter;

  function vLang(btn, lang){
    document.querySelectorAll(".vl-btn").forEach(function(b){ b.classList.remove("on"); });
    btn.classList.add("on");
    V_LANG = lang;
    vRender();
  }
  window.vLang = vLang;

  function vRefresh(){
    V_ITEMS = [];
    vFetch();
  }
  window.vRefresh = vRefresh;

  function vDateFmt(d){
    try {
      var dt = new Date(d);
      var now = new Date();
      var diff = Math.floor((now - dt) / 60000);
      if(diff < 1) return "À l\'instant";
      if(diff < 60) return diff + " min";
      if(diff < 1440) return Math.floor(diff/60) + "h";
      return dt.toLocaleDateString("fr-FR",{day:"numeric",month:"short"});
    } catch(e){ return ""; }
  }

  function vCatDetect(title, src){
    var t = (title||"").toLowerCase();
    if(/mistral|gemini|gpt|llm|generat|ia|intelligence artif/i.test(t)) return "ai";
    if(/france|cnil|anssi|dinum|gouvernement|sénat|assemblée/i.test(t)) return "fr";
    if(/rgpd|gdpr|ia act|nist|iso|conformit|règlement|directive|légis/i.test(t)) return "regl";
    if(/cyber|attaque|malware|ransomware|phish|sécurit|vulnerab|breach/i.test(t)) return "secu";
    if(/europe|usa|chine|international|mondial|onu|ocde|g7/i.test(t)) return "intl";
    return src || "innov";
  }

  function vFetch(){
    if(V_LOADING) return;
    V_LOADING = true;
    var loading = document.getElementById("vloading");
    var items   = document.getElementById("vitems");
    if(loading){ loading.style.display = "block"; }
    if(items)  { items.innerHTML = ""; }
    document.getElementById("vstatus-txt").textContent = "Chargement…";

    var attempts = 0;

    function doFetch(){
      attempts++;
      if(loading && attempts > 1){
        loading.innerHTML = "<div class=\"vspinner\"></div>Redémarrage du serveur… "
          + attempts + "/3 (" + (attempts * 8) + "s)";
      }
      fetch("/api/news")
        .then(function(r){
          if(!r.ok) throw new Error("HTTP " + r.status);
          return r.json();
        })
        .then(function(data){
          V_LOADING = false;
          if(loading){ loading.style.display = "none"; loading.innerHTML = "<div class=\"vspinner\"></div>Chargement des actualités…"; }
          if(data && data.items && data.items.length){
            V_ITEMS = data.items;
            vRender();
            document.getElementById("vstatus-txt").textContent =
              data.count + " actualités · " +
              new Date().toLocaleTimeString("fr-FR",{hour:"2-digit",minute:"2-digit"});
          } else {
            vShowError("Aucune actualité disponible. Cliquez ↻ pour réessayer.");
          }
        })
        .catch(function(){
          if(attempts < 3){
            /* Serveur Render peut démarrer à froid — réessayer après 8s */
            setTimeout(doFetch, 8000);
          } else {
            V_LOADING = false;
            if(loading){ loading.style.display = "none"; loading.innerHTML = "<div class=\"vspinner\"></div>Chargement des actualités…"; }
            vShowError("Service temporairement indisponible. Cliquez ↻ pour réessayer.");
          }
        });
    }

    doFetch();
  }

  function vShowError(msg){
    var items = document.getElementById("vitems");
    if(items) items.innerHTML = "<div style=\"padding:24px;text-align:center;color:rgba(196,181,232,.5);font-size:13px;\">"
      +"<div style=\"font-size:32px;margin-bottom:10px;\">📡</div>"
      + msg + "<br><small style=\"opacity:.6;\">Cliquez ↻ pour réessayer</small></div>";
    document.getElementById("vstatus-txt").textContent = "Erreur de chargement";
  }

  var V_SCROLL_RAF = null;
  var V_SCROLL_POS = 0;
  var V_SCROLL_PAUSED = false;
  var V_SCROLL_SPEED = 0.4; // px par frame (~24px/sec)

  function vRender(){
    var container = document.getElementById("vitems");
    if(!container) return;
    var list = V_ITEMS.filter(function(i){
      var catOk  = (V_CAT  === "all") || (i.cat  === V_CAT);
      var langOk = (V_LANG === "all") || (i.lang === V_LANG);
      return catOk && langOk;
    });
    if(!list.length){
      vStopScroll();
      container.innerHTML = "<div style=\"padding:32px;text-align:center;color:rgba(196,181,232,.4);font-size:13px;\">Aucune actualité dans cette catégorie.<br><small>Essayez \"Tout\"</small></div>";
      return;
    }
    var catMap = V_CAT_MAP;
    // Doubler la liste pour le défilement infini (seamless loop)
    var itemsHtml = list.slice(0,30).map(function(item){
      var cm = catMap[item.cat] || catMap.innov;
      return "<a href=\""+item.link+"\" target=\"_blank\" rel=\"noopener\" class=\"vi\" style=\"text-decoration:none;\">"
        +"<div class=\"vi-ico " + cm.icoCls + "\">" + item.ico + "</div>"
        +"<div class=\"vi-body\">"
        +"<div class=\"vi-title\">" + item.title.replace(/</g,"&lt;").replace(/>/g,"&gt;") + "</div>"
        +"<div class=\"vi-meta\">"
        +"<span class=\"vi-tag " + cm.cls + "\">" + cm.label + "</span>"
        +(item.date?"<span class=\"vi-date\">📅 " + vDateFmt(item.date) + "</span>":"")
        +"</div>"
        +"<div class=\"vi-source\">" + item.source + "</div>"
        +"</div>"
        +"</a>";
    }).join("");
    // Créer inner div avec liste doublée pour boucle infinie
    container.innerHTML = "<div id=\"vitems-inner\">" + itemsHtml + itemsHtml + "</div>";
    V_SCROLL_POS = 0;
    vStartScroll();
    // Pause au survol
    container.addEventListener("mouseenter", function(){ V_SCROLL_PAUSED = true; });
    container.addEventListener("mouseleave", function(){ V_SCROLL_PAUSED = false; });
    // Clic ne bloque pas le scroll
  }

  function vStartScroll(){
    vStopScroll();
    V_SCROLL_POS = 0;
    function tick(){
      if(!V_SCROLL_PAUSED){
        var inner = document.getElementById("vitems-inner");
        if(inner){
          V_SCROLL_POS += V_SCROLL_SPEED;
          var half = inner.scrollHeight / 2;
          if(V_SCROLL_POS >= half) V_SCROLL_POS = 0; // reset seamless
          inner.style.transform = "translateY(-" + V_SCROLL_POS.toFixed(2) + "px)";
        }
      }
      V_SCROLL_RAF = requestAnimationFrame(tick);
    }
    V_SCROLL_RAF = requestAnimationFrame(tick);
  }

  function vStopScroll(){
    if(V_SCROLL_RAF){ cancelAnimationFrame(V_SCROLL_RAF); V_SCROLL_RAF = null; }
  }

  // Auto-refresh toutes les 10 minutes
  V_INTERVAL = setInterval(function(){
    if(V_OPEN) vFetch();
  }, 600000);

})();


// ════════════════════════════════════════
// CHAT MISTRAL AI
// ════════════════════════════════════════
var xCO=false, xCB=false, xCH=[];
/* Cle API retiree : le chat passe par le serveur (/api/chat), moteur hybride. */
var xSYS={
  fr:'Tu es un expert senior CONSEILPREV spécialisé en gouvernance IA, conformité et cybersécurité. Réponds en français, de manière professionnelle et concise (max 280 mots). Domaines : IA Act, ISO 42001, NIS2, ISO 27001, DORA, RGPD, 8 risques systémiques IA. Pour toute question de projet, oriente vers contact@i-aes.com ou le formulaire du site.',
  en:'You are a senior CONSEILPREV expert in AI governance, compliance and cybersecurity. Reply in English, professionally and concisely (max 280 words). Domains: AI Act, ISO 42001, NIS2, ISO 27001, DORA, GDPR, 8 systemic AI risks. For project inquiries, direct to contact@i-aes.com.',
  de:'Sie sind ein erfahrener CONSEILPREV-Experte für KI-Governance, Compliance und Cybersicherheit. Antworten Sie auf Deutsch, professionell und präzise (max. 280 Wörter). Bereiche: KI-Act, ISO 42001, NIS2, ISO 27001, DORA, DSGVO. Für Projektanfragen: contact@i-aes.com.'
};

function xOpen(){
  xCO=!xCO;
  var box=document.getElementById('xbox');
  var btn=document.getElementById('xbtn');
  if(box){ box.style.display=xCO?'flex':'none'; }
  if(btn){ btn.textContent=xCO?'✕':'💬'; }
  if(xCO && xCH.length===0){
    /* AI-DISCLOSURE (IA Act, art. 50.1) : information des la premiere interaction. */
    xMsg('b','<div class="ia50-notice"><span class="ia50-badge">IA</span><span>Vous \u00e9changez avec un <strong>assistant fond\u00e9 sur l\u2019intelligence artificielle</strong>, et non avec une personne. Ses r\u00e9ponses peuvent comporter des erreurs et ne constituent pas un conseil juridique.</span></div>');
    xMsg('b',ii('ch.hi')||'Bonjour ! Expert CONSEILPREV.<br>Questions sur <strong>IA Act</strong>, <strong>NIS2</strong>, <strong>ISO 27001</strong>, <strong>DORA</strong>, <strong>RGPD</strong> ?');
  }
  if(xCO){ setTimeout(function(){ var i=document.getElementById('xinp'); if(i)i.focus(); },120); }
}

function xMsg(role,txt){
  var b=document.getElementById('xmsgs');
  if(!b) return;
  var d=document.createElement('div');
  d.className='xm '+(role==='b'?'b':'u');
  d.innerHTML='<div class="xav">'+(role==='b'?'AI':'✦')+'</div><div class="xbl">'+txt+'</div>';
  b.appendChild(d);
  b.scrollTop=b.scrollHeight;
  return d;
}

function xTyp(show){
  if(show){
    var b=document.getElementById('xmsgs');
    if(!b) return;
    var d=document.createElement('div');
    d.className='xm b'; d.id='xtind';
    d.innerHTML='<div class="xav">AI</div><div class="xbl"><div class="xtd"><span></span><span></span><span></span></div></div>';
    b.appendChild(d); b.scrollTop=b.scrollHeight;
  } else {
    var t=document.getElementById('xtind');
    if(t) t.remove();
  }
}

function xFmtT(txt){
  // Nettoyage defensif du formatage Markdown residuel, en complement de la
  // consigne donnee au modele (qui peut occasionnellement l ignorer) :
  // titres (#), listes a puces (- ou *), italique (*texte*), asterisques isoles.
  txt = txt.replace(/^#{1,6}\s*/gm, '');           // titres Markdown (#, ##, ###...)
  txt = txt.replace(/^[\*\-]\s+/gm, '');           // puces de liste (* ou - en debut de ligne)
  var bold = txt.split('**').map(function(s,idx){return idx%2===1?'<strong>'+s+'</strong>':s;}).join('');
  bold = bold.replace(/\*([^*<>]+)\*/g, '$1');     // *italique* -> texte simple
  bold = bold.replace(/\*/g, '');                  // tout asterisque isole restant
  return bold.replace(/\n\n/g,'<br><br>').replace(/\n/g,'<br>');
}


/* Minimisation (RGPD art. 5.1.c) — le serveur refuse un premier envoi qui
   contient des donnees personnelles et dit ce qu il a trouve. Trois issues,
   toutes tenues par l utilisateur : corriger, caviarder, ou maintenir. On
   n interdit jamais : un avertissement qui empeche de travailler finit par
   etre contourne. Le controle vit cote serveur ; ceci n en est que la
   presentation. */
function cpMinEsc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;')
  .replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function cpMinHtml(j){
  var m=(j&&j.minimisation)||{}, det=m.detections||[];
  var d=det.map(function(x){
    return cpMinEsc(x.libelle)+' \u00d7 '+x.occurrences
      +(x.exemples&&x.exemples.length?' <span style="opacity:.7">('+cpMinEsc(x.exemples.join(', '))+')</span>':'');
  }).join(' \u00b7 ');
  return '<div class="cpmin"><b>'+cpMinEsc(j.message||'Ce texte contient des donnees personnelles.')+'</b>'
    +'<div class="cpmin-d">'+d+'</div>'
    +'<div class="cpmin-b">'
    +'<button type="button" class="pri" data-mz="corriger">Corriger ma question</button>'
    +'<button type="button" data-mz="masquer">Retirer et envoyer</button>'
    +'<button type="button" data-mz="accepter">Envoyer quand meme</button>'
    +'</div></div>';
}

var xDerniere='', xBulle=null;

async function xSend(mode){
  if(xCB) return;
  var inp=document.getElementById('xinp');
  if(!inp) return;
  var m=mode?xDerniere:inp.value.trim();
  if(!m) return;
  if(!mode){
    inp.value=''; inp.style.height='auto';
    var sugg=document.getElementById('xsugg');
    if(sugg) sugg.style.display='none';
    xBulle=xMsg('u',m.replace(/</g,'&lt;').replace(/>/g,'&gt;'));
    xDerniere=m;
    xCH.push({role:'user',content:m});
  }
  xCB=true;
  var btn=document.getElementById('xsnd');
  if(btn) btn.disabled=true;
  xTyp(true);
  try{
    var lang=typeof LANG!=='undefined'?LANG:'fr';
    var sys=xSYS[lang]||xSYS.fr;
    var msgs=[{role:'system',content:sys}];
    xCH.slice(-8).forEach(function(h){msgs.push(h);});
    var r=await fetch('/api/chat',{
      method:'POST', credentials:'same-origin',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({message:m, history:xCH.slice(-8), minimisation:mode||''})
    });
    var data=await r.json();
    if(data && data.code==='donnees_personnelles'){
      xTyp(false);
      var av=xMsg('b',cpMinHtml(data));
      av.addEventListener('click',function(e){
        var t=e.target.getAttribute&&e.target.getAttribute('data-mz'); if(!t) return;
        av.remove();
        if(t==='corriger'){
          for(var k=xCH.length-1;k>=0;k--){ if(xCH[k].role==='user'){ xCH.splice(k,1); break; } }
          if(xBulle){ xBulle.remove(); xBulle=null; }
          inp.value=xDerniere; inp.focus();
          return;
        }
        xSend(t);
      });
      xCB=false;
      if(btn) btn.disabled=false;
      return;
    }
    if(!r.ok || !data.reply) throw new Error(data.error || ('HTTP '+r.status));
    xTyp(false);
    if(data.envoye){        // caviarde : la conversation repart du texte transmis
      for(var q=xCH.length-1;q>=0;q--){ if(xCH[q].role==='user'){ xCH[q].content=data.envoye; break; } }
      if(xBulle){ var bl=xBulle.querySelector('.xbl'); if(bl) bl.textContent=data.envoye; }
    }
    // Aucun bloc \u00ab Sources \u00bb : la reponse s'appuie sur la base documentaire
    // sans jamais la nommer (le serveur ne les envoie plus).
    var rep=data.reply;
    xMsg('b',xFmtT(rep));
    xCH.push({role:'assistant',content:rep});
  }catch(err){
    xTyp(false);
    xMsg('b','⚠ Erreur: '+err.message+'. Contactez <a href="mailto:contact@i-aes.com" style="color:var(--teal)">contact@i-aes.com</a>');
  }
  xCB=false;
  if(btn) btn.disabled=false;
}

function xSug(btn){
  var inp=document.getElementById('xinp');
  if(inp){ inp.value=btn.textContent; xSend(); }
}

// Entrée clavier dans le chat
(function(){
  var inp=document.getElementById('xinp');
  if(inp){
    inp.addEventListener('keydown',function(e){
      if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();xSend();}
      this.style.height='auto';
      this.style.height=Math.min(this.scrollHeight,90)+'px';
    });
  }
})();




// ══════════════════════════════════════════════════
// HERO TITLE ROTATOR
// Séquence : Gouvernance IA → Risk Management →
// Compliance → Conformité IA → IA Industrielle
// ══════════════════════════════════════════════════
(function(){
  "use strict";

  var WORDS = [
    "Gouvernance IA",
    "Risk Management",
    "Compliance",
    "Conformité IA",
    "IA Industrielle"
  ];

  var COLORS = [
    "linear-gradient(135deg,#a78bfa,#e879f9)",   // violet → fuchsia
    "linear-gradient(135deg,#818cf8,#c084fc)",   // bleu → violet
    "linear-gradient(135deg,#c084fc,#f0abfc)",   // violet → lilas
    "linear-gradient(135deg,#e879f9,#a78bfa)",   // fuchsia → violet
    "linear-gradient(135deg,#93c5fd,#a78bfa)",   // bleu ciel → violet
  ];

  var INTERVAL = 3000;  // ms entre chaque mot
  var ANIM_OUT = 450;   // durée animation sortie

  var container = document.getElementById('hero-rotating');
  var spacer    = document.getElementById('rot-spacer');
  if(!container) return;

  var currentIndex = 0;
  var currentEl    = null;

  function makeWord(text, color){
    var el = document.createElement('span');
    el.className   = 'rot-word';
    el.textContent = text;
    el.style.background = color;
    el.style.webkitBackgroundClip = 'text';
    el.style.backgroundClip = 'text';
    el.style.webkitTextFillColor = 'transparent';
    // Aligner la largeur du spacer sur le mot le plus long
    return el;
  }

  function updateSpacerWidth(){
    // Trouver le mot le plus large et réserver cet espace
    var maxWord = WORDS.reduce(function(a,b){ return b.length > a.length ? b : a; });
    spacer.textContent = maxWord;
  }

  function showWord(index){
    var text  = WORDS[index];
    var color = COLORS[index % COLORS.length];
    var newEl = makeWord(text, color);

    // Animer la sortie du mot actuel
    if(currentEl){
      var old = currentEl;
      old.classList.remove('visible');
      old.classList.add('leaving');
      setTimeout(function(){ if(old.parentNode) old.parentNode.removeChild(old); }, ANIM_OUT);
    }

    // Insérer et animer l'entrée du nouveau mot
    container.appendChild(newEl);
    // Forcer reflow
    newEl.getBoundingClientRect();
    newEl.classList.add('entering');

    // Passer à "visible" après la fin de l'animation d'entrée
    setTimeout(function(){
      newEl.classList.remove('entering');
      newEl.classList.add('visible');
    }, 550);

    currentEl    = newEl;
    currentIndex = index;
  }

  // Init
  updateSpacerWidth();
  showWord(0);

  // Boucle
  setInterval(function(){
    var next = (currentIndex + 1) % WORDS.length;
    showWord(next);
  }, INTERVAL);

})();

// ════════════════════════════════════════
// BOUTONS ACCESSIBILITÉ FLOTTANTS
// ════════════════════════════════════════
(function(){
  "use strict";

  var ACC_STATE = {reading:false, dyslexia:false, contrast:false};
  var ACC_STORE_KEY = "conseilprev_acc_float";

  // Charger les préférences sauvegardées
  function loadAccState(){
    try{
      var s = JSON.parse(localStorage.getItem(ACC_STORE_KEY)||'{}');
      Object.keys(ACC_STATE).forEach(function(k){ if(s[k]!==undefined) ACC_STATE[k]=s[k]; });
    }catch(e){}
  }

  function saveAccState(){
    try{ localStorage.setItem(ACC_STORE_KEY, JSON.stringify(ACC_STATE)); }catch(e){}
  }

  // Appliquer les classes sur body
  function applyAccState(){
    var body = document.body;
    // Mode lecture
    body.classList.toggle('acc-reading', ACC_STATE.reading);
    // Mode dyslexie
    body.classList.toggle('acc-dyslexia', ACC_STATE.dyslexia);
    // Contraste élevé
    body.classList.toggle('acc-contrast', ACC_STATE.contrast);

    // Mettre à jour les boutons
    ['reading','dyslexia','contrast'].forEach(function(mode){
      var btn = document.getElementById('acc-'+mode+'-btn');
      if(btn){
        btn.classList.toggle('active', ACC_STATE[mode]);
        btn.setAttribute('aria-pressed', ACC_STATE[mode] ? 'true' : 'false');
      }
    });

    // Jouer le son si disponible
    playSoundAcc(null);
  }

  function playSoundAcc(type){
    try{
      var ctx = new(window.AudioContext||window.webkitAudioContext)();
      var osc = ctx.createOscillator(); var gain = ctx.createGain();
      osc.connect(gain); gain.connect(ctx.destination);
      osc.frequency.setValueAtTime(type==='off'?500:600, ctx.currentTime);
      osc.frequency.linearRampToValueAtTime(type==='off'?350:750, ctx.currentTime+0.12);
      gain.gain.setValueAtTime(0.06, ctx.currentTime);
      gain.gain.linearRampToValueAtTime(0, ctx.currentTime+0.18);
      osc.start(ctx.currentTime); osc.stop(ctx.currentTime+0.18);
    }catch(e){}
  }

  // Toggle public
  window.accToggle = function(mode){
    ACC_STATE[mode] = !ACC_STATE[mode];
    playSoundAcc(ACC_STATE[mode] ? 'on' : 'off');
    applyAccState();
    saveAccState();

    // Toast
    var labels = {reading:'Mode lecture', dyslexia:'Mode dyslexie', contrast:'Contraste élevé'};
    var msg = labels[mode] + (ACC_STATE[mode] ? ' activé' : ' désactivé');
    showAccToast(msg, ACC_STATE[mode]);
  };

  function showAccToast(msg, active){
    var old = document.getElementById('acc-toast');
    if(old) old.remove();
    var t = document.createElement('div');
    t.id = 'acc-toast';
    var bg = active ? 'rgba(124,92,191,.97)' : 'rgba(22,11,48,.97)';
    t.style.cssText = 'position:fixed;bottom:80px;left:50%;transform:translateX(-50%) translateY(10px);'
      +'background:'+bg+';border:1px solid rgba(196,181,232,.35);color:#fff;'
      +'font-size:12px;font-family:"Space Mono",monospace;padding:8px 18px;border-radius:100px;'
      +'z-index:10002;backdrop-filter:blur(12px);box-shadow:0 4px 18px rgba(0,0,0,.4);'
      +'pointer-events:none;opacity:0;transition:opacity .18s,transform .18s;letter-spacing:.03em';
    t.textContent = (active ? '✓ ' : '○ ') + msg;
    document.body.appendChild(t);
    requestAnimationFrame(function(){
      t.style.opacity = '1';
      t.style.transform = 'translateX(-50%) translateY(0)';
    });
    setTimeout(function(){ t.style.opacity='0'; t.style.transform='translateX(-50%) translateY(6px)'; }, 2000);
    setTimeout(function(){ if(t.parentNode) t.remove(); }, 2400);
  }

  // CSS dynamique pour les modes
  var ACC_STYLE = document.createElement('style');
  ACC_STYLE.textContent = [
    // Mode lecture
    'body.acc-reading{--acc-bg:#f7f4ff;--acc-txt:#1a1230;--acc-mu:#555;background:#f7f4ff!important;color:#1a1230!important}',
    'body.acc-reading *{transition:background .18s,color .18s}',
    'body.acc-reading::before{display:none!important}',
    'body.acc-reading .nav{background:rgba(247,244,255,.97)!important;border-bottom:1px solid rgba(124,92,191,.25)!important}',
    'body.acc-reading p,body.acc-reading li{max-width:72ch;line-height:1.85!important;font-size:1.05em!important}',
    'body.acc-reading h1,body.acc-reading h2,body.acc-reading h3{color:#2d1b6b!important}',
    'body.acc-reading .sec{background:rgba(247,244,255,.6)!important}',
    'body.acc-reading .card,body.acc-reading .feat-card,body.acc-reading .ck-cat{background:#fff!important;border-color:rgba(124,92,191,.2)!important;color:#1a1230!important}',
    // Mode dyslexie
    'body.acc-dyslexia{font-family:Arial,Helvetica,sans-serif!important;letter-spacing:.07em!important;word-spacing:.2em!important;line-height:2!important}',
    'body.acc-dyslexia p,body.acc-dyslexia li,body.acc-dyslexia span{font-size:1.05em!important}',
    'body.acc-dyslexia a{text-decoration:underline!important;text-underline-offset:3px!important}',
    'body.acc-dyslexia h1,body.acc-dyslexia h2,body.acc-dyslexia h3{letter-spacing:.04em!important;line-height:1.4!important}',
    // Contraste élevé
    'body.acc-contrast{background:#000!important;color:#fff!important}',
    'body.acc-contrast::before{opacity:.03!important}',
    'body.acc-contrast .nav{background:#000!important;border-bottom:2px solid #ff0!important}',
    'body.acc-contrast .card,body.acc-contrast .feat-card,body.acc-contrast .ck-cat{background:#111!important;border:2px solid #fff!important;color:#fff!important}',
    'body.acc-contrast a{color:#ff0!important;text-decoration:underline!important}',
    'body.acc-contrast .hero{background:#000!important}',
    'body.acc-contrast h1,body.acc-contrast h2,body.acc-contrast h3{color:#ff0!important}',
    'body.acc-contrast .acc-float-btn{border:3px solid #fff!important}',
    'body.acc-contrast button{border:2px solid #fff!important}',
  ].join('');
  document.head.appendChild(ACC_STYLE);

  // Init
  document.addEventListener('DOMContentLoaded', function(){
    loadAccState();
    applyAccState();
  });

})();


// ════════════════════════════════════════
// NAVIGATION FLÈCHES — SECTIONS
// ════════════════════════════════════════
(function(){
  "use strict";

  // Sections à naviguer (dans l'ordre de la page)
  var SECTION_IDS = ['hero','secteurs','normes','risques','poles','services','differenciateurs','avenir','contact','clients'];
  var SECTION_LABELS = {
    'hero':        '🏠 Accueil',
    'secteurs':    '🏭 Secteurs',
    'normes':      '📋 Normes',
    'risques':     '⚠️ Risques IA',
    'poles':       '💡 Expertise',
    'services':    '🛠 Services',
    'differenciateurs': '✨ Différenciateurs',
    'avenir':      '🚀 Construisons',
    'contact':     '📩 Contact',
    'clients':     '🏆 Clients',
  };

  var currentSection = 0;
  var isScrolling = false;

  // Initialiser les points de navigation
  function initDots(){
    var container = document.getElementById('nav-section-dots');
    if(!container) return;
    SECTION_IDS.forEach(function(id, i){
      var dot = document.createElement('div');
      dot.className = 'nav-dot' + (i===0?' active':'');
      dot.setAttribute('role','tab');
      dot.setAttribute('aria-label', SECTION_LABELS[id]||id);
      dot.setAttribute('title', SECTION_LABELS[id]||id);
      dot.addEventListener('click', function(){ goToSection(i); });
      container.appendChild(dot);
    });
  }

  // Aller à une section
  function goToSection(idx){
    if(idx < 0) idx = 0;
    if(idx >= SECTION_IDS.length) idx = SECTION_IDS.length-1;
    var id = SECTION_IDS[idx];
    var el = document.getElementById(id);
    if(!el) return;
    isScrolling = true;
    var navH = document.querySelector('nav')?document.querySelector('nav').offsetHeight:70;
    var top = el.getBoundingClientRect().top + window.scrollY - navH - 8;
    window.scrollTo({top: top, behavior:'smooth'});
    currentSection = idx;
    updateArrows();
    showSectionLabel(id);
    setTimeout(function(){ isScrolling=false; }, 800);
  }
  window.goToSection = goToSection;

  // Navigation +1/-1
  window.navSection = function(dir){
    goToSection(currentSection + dir);
  };

  /* Les deux bornes. Elles ne passent PAS par goToSection : la premiere section
     ne commence pas a zero (l'en-tete la precede) et la derniere ne finit pas
     au pied de page. « Haut » et « bas » veulent dire le haut et le bas du
     document, pas la premiere et la derniere section. */
  window.navBorne = function(bas){
    var doux = window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
    window.scrollTo({ top: bas ? document.body.scrollHeight : 0, behavior: doux });
  };

  // Mettre à jour les boutons et points
  function updateArrows(){
    var up   = document.getElementById('nav-up');
    var down = document.getElementById('nav-down');
    if(up)   up.disabled   = (currentSection === 0);
    if(down) down.disabled = (currentSection === SECTION_IDS.length-1);
    document.querySelectorAll('.nav-dot').forEach(function(d,i){
      d.classList.toggle('active', i===currentSection);
    });
  }

  // Afficher le label section
  var labelTimer = null;
  function showSectionLabel(id){
    var lbl = document.getElementById('nav-section-label');
    if(!lbl) return;
    lbl.textContent = SECTION_LABELS[id]||id;
    lbl.classList.add('show');
    clearTimeout(labelTimer);
    labelTimer = setTimeout(function(){ lbl.classList.remove('show'); }, 2000);
    // Positionner verticalement au niveau de la flèche active
    var arrows = document.getElementById('nav-arrows');
    if(arrows) lbl.style.top = (arrows.getBoundingClientRect().top + window.scrollY + 40) + 'px';
  }

  // Détecter la section active au scroll
  function onScroll(){
    // Barre de progression
    var prog = document.getElementById('read-progress');
    if(prog){
      var scrolled = window.scrollY;
      var total = document.body.scrollHeight - window.innerHeight;
      prog.style.width = (total > 0 ? Math.round(scrolled/total*100) : 0) + '%';
    }

    // Section active
    var navH = document.querySelector('nav')?document.querySelector('nav').offsetHeight:70;
    var midScreen = window.scrollY + navH + (window.innerHeight-navH)/3;
    var found = 0;
    SECTION_IDS.forEach(function(id, i){
      var el = document.getElementById(id);
      if(el){
        var top = el.getBoundingClientRect().top + window.scrollY;
        if(top <= midScreen) found = i;
      }
    });
    if(found !== currentSection && !isScrolling){
      currentSection = found;
      updateArrows();
    }

    // Afficher/masquer la colonne
    var arrows = document.getElementById('nav-arrows');
    if(arrows) arrows.classList.toggle('visible', window.scrollY > 200);
  }

  // Raccourcis clavier
  document.addEventListener('keydown', function(e){
    if(e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if(e.altKey && e.key === 'ArrowUp'){   e.preventDefault(); navSection(-1); }
    if(e.altKey && e.key === 'ArrowDown'){ e.preventDefault(); navSection(1);  }
    /* Alt+Origine visait la premiere SECTION, pas le haut du document : on
       n'arrivait jamais tout en haut. Meme raisonnement en bas. */
    if(e.altKey && e.key === 'Home'){      e.preventDefault(); navBorne(0); }
    if(e.altKey && e.key === 'End'){       e.preventDefault(); navBorne(1); }
  });

  // Init
  document.addEventListener('DOMContentLoaded', function(){
    initDots();
    updateArrows();
    window.addEventListener('scroll', onScroll, {passive:true});
    onScroll();
  });

})();


// ── Dropdown menus ──
function toggleDrop(id, e){
  if(e){ e.preventDefault(); e.stopPropagation(); }
  var li = document.getElementById(id);
  if(!li) return;
  var wasOpen = li.classList.contains('open');
  // Fermer tous
  document.querySelectorAll('.has-dropdown.open').forEach(function(el){ el.classList.remove('open'); });
  if(!wasOpen) li.classList.add('open');
}
// Fermer au clic extérieur
document.addEventListener('click', function(e){
  if(!e.target.closest('.has-dropdown')){
    document.querySelectorAll('.has-dropdown.open').forEach(function(el){ el.classList.remove('open'); });
  }
});
// Fermer au Echap
document.addEventListener('keydown', function(e){
  if(e.key==='Escape'){
    document.querySelectorAll('.has-dropdown.open').forEach(function(el){ el.classList.remove('open'); });
  }
});

// ════════════════════════════════════════
// SYSTÈME COOKIES RGPD — CONSEILPREV
// Conforme RGPD Art.7, CNIL, Directive ePrivacy
// ════════════════════════════════════════
(function(){
  "use strict";

  var CK_KEY  = "conseilprev_cookies";
  var CK_TTL  = 13 * 30 * 24 * 60 * 60 * 1000; // 13 mois en ms

  // ── Lire les préférences ──
  function ckLoad(){
    try{
      var raw = localStorage.getItem(CK_KEY);
      if(!raw) return null;
      var data = JSON.parse(raw);
      // Vérifier expiration
      if(Date.now() - data.ts > CK_TTL){
        localStorage.removeItem(CK_KEY);
        return null;
      }
      return data;
    }catch(e){ return null; }
  }

  // ── Sauvegarder les préférences ──
  function ckSave(prefs){
    var data = {
      necessary:  true,
      functional: !!prefs.functional,
      analytics:  !!prefs.analytics,
      marketing:  !!prefs.marketing,
      ts:         Date.now(),
      date:       new Date().toLocaleString('fr-FR'),
      ua:         navigator.userAgent.slice(0,80),
      version:    '1.0'
    };
    localStorage.setItem(CK_KEY, JSON.stringify(data));
    /* Preuve de consentement serveur (RGPD art. 7) : acceptation, personnalisation
       ou refus sont horodates et conserves comme preuve, sans donnee superflue. */
    try {
      fetch('/api/rgpd/consentement', { method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ methode: 'banniere-cookies',
          finalites: { necessary: true, functional: data.functional, analytics: data.analytics, marketing: data.marketing },
          retrait: !(data.functional || data.analytics || data.marketing) }) }).catch(function(){});
    } catch(e){}
    return data;
  }

  // ── Mettre à jour le bouton flottant ──
  function ckUpdateBtn(prefs){
    var dot = document.getElementById('ck-btn-dot');
    if(!dot) return;
    var allOn  = prefs && prefs.functional && prefs.analytics && prefs.marketing;
    var allOff = prefs && !prefs.functional && !prefs.analytics && !prefs.marketing;
    if(!prefs){ dot.className='refused'; return; }
    if(allOn)  dot.className='accepted';
    else if(allOff) dot.className='refused';
    else dot.className='partial';
  }

  // ── Mettre à jour les toggles dans la modal ──
  function ckUpdateToggles(prefs){
    ['functional','analytics','marketing'].forEach(function(k){
      var el = document.getElementById('ck-'+k);
      if(el) el.checked = prefs ? !!prefs[k] : false;
    });
    var ts = document.getElementById('ck-proof-ts');
    if(ts && prefs && prefs.date){
      ts.textContent = 'Consentement enregistré le ' + prefs.date;
    }
  }

  // ── Ouvrir la modal ──
  window.ckOpenModal = function(){
    var modal = document.getElementById('ck-modal');
    var banner= document.getElementById('ck-banner');
    if(modal) modal.classList.add('open');
    if(banner) banner.classList.remove('show');
    var prefs = ckLoad();
    ckUpdateToggles(prefs);
    // Focus trap
    setTimeout(function(){
      var close = document.querySelector('#ck-modal .ck-modal-close');
      if(close) close.focus();
    }, 100);
  };

  // ── Fermer la modal ──
  window.ckCloseModal = function(){
    var modal = document.getElementById('ck-modal');
    if(modal) modal.classList.remove('open');
  };

  // ── Clic en dehors ──
  window.ckModalBg = function(e){
    if(e.target.id === 'ck-modal') ckCloseModal();
  };

  // ── Enregistrer les préférences ──
  window.ckSavePrefs = function(){
    var prefs = {
      functional: !!(document.getElementById('ck-functional')||{}).checked,
      analytics:  !!(document.getElementById('ck-analytics')||{}).checked,
      marketing:  !!(document.getElementById('ck-marketing')||{}).checked,
    };
    var saved = ckSave(prefs);
    ckUpdateBtn(saved);
    ckUpdateToggles(saved);
    ckCloseModal();
    // Toast confirmation
    ckToast('✓ Préférences enregistrées');
    // Appliquer les cookies
    ckApply(saved);
  };

  // ── Tout accepter ──
  window.ckAcceptAll = function(){
    var prefs = {functional:true, analytics:true, marketing:true};
    var saved = ckSave(prefs);
    ckUpdateBtn(saved);
    ckUpdateToggles(saved);
    var banner = document.getElementById('ck-banner');
    if(banner) banner.classList.remove('show');
    ckCloseModal();
    ckToast('✓ Tous les cookies acceptés');
    ckApply(saved);
  };

  // ── Tout refuser ──
  window.ckRefuseAll = function(){
    var prefs = {functional:false, analytics:false, marketing:false};
    var saved = ckSave(prefs);
    ckUpdateBtn(saved);
    ckUpdateToggles(saved);
    var banner = document.getElementById('ck-banner');
    if(banner) banner.classList.remove('show');
    ckCloseModal();
    ckToast('Cookies non essentiels refusés');
    ckApply(saved);
  };

  // ── Appliquer les cookies (hooks pour futurs scripts) ──
  function ckApply(prefs){
    // Analytics — activer/désactiver GA si présent
    if(typeof window.gtag === 'function'){
      if(prefs.analytics){
        window['ga-disable-UA-XXXXX-X'] = false;
      } else {
        window['ga-disable-UA-XXXXX-X'] = true;
      }
    }
    // Custom event pour intégrations tierces
    document.dispatchEvent(new CustomEvent('conseilprev:cookies', {detail: prefs}));
  }

  // ── Toast notification ──
  function ckToast(msg){
    var old = document.getElementById('ck-toast');
    if(old) old.remove();
    var t = document.createElement('div');
    t.id = 'ck-toast';
    t.textContent = msg;
    t.style.cssText = 'position:fixed;bottom:80px;left:50%;transform:translateX(-50%);background:rgba(22,11,48,.97);border:1px solid rgba(124,92,191,.4);color:var(--pp, #c4b5e8);font-size:13px;padding:10px 20px;border-radius:100px;z-index:10002;font-family:"DM Sans",sans-serif;backdrop-filter:blur(12px);box-shadow:0 4px 20px rgba(0,0,0,.4);pointer-events:none;transition:opacity .18s';
    document.body.appendChild(t);
    setTimeout(function(){ t.style.opacity='0'; }, 2200);
    setTimeout(function(){ if(t.parentNode) t.remove(); }, 2600);
  }

  // ── Raccourci clavier Échap ──
  document.addEventListener('keydown', function(e){
    if(e.key === 'Escape'){
      var modal = document.getElementById('ck-modal');
      if(modal && modal.classList.contains('open')) ckCloseModal();
    }
  });

  // ── Init au chargement ──
  document.addEventListener('DOMContentLoaded', function(){
    var prefs = ckLoad();
    if(!prefs){
      // Premier visite — afficher le bandeau après 1 seconde
      setTimeout(function(){
        var banner = document.getElementById('ck-banner');
        if(banner) banner.classList.add('show');
      }, 1000);
    } else {
      ckUpdateBtn(prefs);
      ckApply(prefs);
    }
  });

})();

(function(){
  var u=new URL(window.location.href);
  var lp=u.searchParams.get('lang');
  var nav=(navigator.language||'fr').toLowerCase();
  LANG=lp==='en'?'en':lp==='fr'?'fr':lp==='de'?'de':
       nav.startsWith('en')?'en':nav.startsWith('de')?'de':'fr';
  document.querySelectorAll('.lbtn').forEach(function(b){
    b.classList.toggle('on',b.dataset.lang===LANG);
  });
  applyLang();
  if(typeof xInitOrgs==='function'){
    xInitOrgs('ia');
    var xt=document.getElementById('xtheme');
    if(xt)xt.value='ia';
  }
})();


// ── Validation consentement formulaire contact ──



;/* ── bloc 3/12 ── */

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


;/* ── bloc 4/12 ── */

/* ════ FORMULAIRE CONTACT PROJET IA — CONSEILPREV ════ */
(function(){
  'use strict';

  /* 1. Feedback visuel */
  function pfStatus(type, content){
    var el = document.getElementById('pfst');
    if(!el) return;
    var bg = {
      success: 'rgba(6,95,70,.2)',
      warn:    'rgba(120,53,15,.25)',
      error:   'rgba(127,29,29,.2)'
    };
    var bd = {
      success: 'rgba(94,234,212,.5)',
      warn:    'rgba(251,191,36,.5)',
      error:   'rgba(248,113,113,.5)'
    };
    var col = {
      success: '#5eead4',
      warn:    '#fde68a',
      error:   '#fca5a5'
    };
    el.style.cssText = [
      'display:block',
      'margin-top:18px',
      'padding:16px 20px',
      'border-radius:11px',
      'font-size:13px',
      'line-height:1.7',
      'font-family:"DM Sans",sans-serif',
      'background:' + (bg[type]||bg.error),
      'border:1px solid ' + (bd[type]||bd.error),
      'color:' + (col[type]||col.error),
    ].join(';');
    el.innerHTML = content;
    el.scrollIntoView({behavior:'smooth', block:'nearest'});
  }

  /* 2. Mailto fallback */
  function openMailto(){
    var v = function(id){
      var e = document.getElementById(id);
      return e && e.value ? e.value.trim() : '';
    };
    var lines = [
      '=== DEMANDE DE PROJET IA / CYBER — CONSEILPREV ===', '',
      'Prénom      : ' + (v('pf-prenom')||'—'),
      'Nom         : ' + (v('pf-nom')||'—'),
      'Email       : ' + (v('pf-email')||'—'),
      'Téléphone   : ' + (v('pf-tel')||'—'),
      'Entreprise  : ' + (v('pf-co')||'—'),
      'Fonction    : ' + (v('pf-role')||'—'),
      'Secteur     : ' + (v('pf-sector')||'—'),
      'Pays        : ' + (v('pf-country')||'—'),
      'Taille      : ' + (v('pf-size')||'—'), '',
      'Projet      : ' + (v('pf-project')||'—'),
      'Norme       : ' + (v('pf-norm')||'—'),
      'Budget      : ' + (v('pf-budget')||'—'),
      'Délai       : ' + (v('pf-delay')||'—'),
      'Source      : ' + (v('pf-source')||'—'), '',
      'Description :',
      v('pf-msg')||'—', '',
      '---',
      'conseilprev.onrender.com · ' + new Date().toLocaleString('fr-FR'),
    ];
    var subj = '[PROJET IA] ' + (v('pf-prenom')||'') + ' ' + (v('pf-nom')||'')
               + ' — ' + (v('pf-co')||'') + ' (' + (v('pf-project')||'demande') + ')';
    window.open(
      'mailto:christophe.cerf@outlook.com'
      + '?subject=' + encodeURIComponent(subj)
      + '&body='    + encodeURIComponent(lines.join('\n')),
      '_blank'
    );
  }
  // Exposer pour le bouton mailto secours
  window.openMailtoContact = openMailto;

  /* 3. Submit */
  var form = document.getElementById('cform');
  if(!form){ return; }

  form.addEventListener('submit', function(e){
    e.preventDefault();

    // Aucune case de consentement à cocher : traiter une demande de contact
    // relève des mesures précontractuelles (art. 6.1.b), et un consentement
    // exigé pour envoyer ne serait pas libre (art. 7.4). Le formulaire porte
    // une mention d'information (art. 13), pas une condition d'envoi.

    // Champs
    var v = function(id){ var e=document.getElementById(id); return e&&e.value?e.value.trim():''; };
    var prenom=v('pf-prenom'), nom=v('pf-nom'), email=v('pf-email');
    var co=v('pf-co'), sector=v('pf-sector'), project=v('pf-project'), msg=v('pf-msg');

    if(!prenom||!nom||!email||!co||!sector||!project||!msg){
      pfStatus('error','⚠ Veuillez remplir tous les champs obligatoires (*).');
      return;
    }

    // Honeypot
    if(v('hp')){ return; }

    // Envoi
    var sbtn = form.querySelector('[type="submit"]');
    var btxt = document.getElementById('pbtn-txt');
    if(sbtn) sbtn.disabled = true;
    if(btxt) btxt.textContent = '⏳ Envoi en cours…';
    pfStatus('warn','⏳ Envoi de votre demande en cours…');

    var fd = new FormData();
    fd.append('form_type',  'contact_projet');
    fd.append('prenom',     prenom);
    fd.append('nom',        nom);
    fd.append('email',      email);
    fd.append('telephone',  v('pf-tel'));
    fd.append('entreprise', co);
    fd.append('fonction',   v('pf-role'));
    fd.append('secteur',    sector);
    fd.append('type_projet',project);
    fd.append('budget',     v('pf-budget'));
    fd.append('message',
      'PROJET : '+project+'\nSECTEUR : '+sector+
      '\nPAYS : '+v('pf-country')+'\nTAILLE : '+v('pf-size')+
      '\nNORME : '+v('pf-norm')+'\nDÉLAI : '+v('pf-delay')+
      '\nBUDGET : '+v('pf-budget')+'\nSOURCE : '+v('pf-source')+
      '\n\nDESCRIPTION :\n'+msg
    );
    fd.append('consent',    'true');
    fd.append('source_url', window.location.pathname);

    fetch('/api/apply', {method:'POST', body:fd})
      .then(function(r){ return r.json(); })
      .then(function(res){
        if(sbtn) sbtn.disabled = false;
        if(res.ok){
          if(res.email_sent){
            // ✅ Vert — email SMTP envoyé
            pfStatus('success',
              '✓ Votre demande a bien été envoyée à CONSEILPREV !<br>'+
              '<span style="font-size:11px;opacity:.85">Réponse garantie sous 24h ouvrées · christophe.cerf@outlook.com</span>'
            );
            if(btxt) btxt.textContent = '✓ Demande envoyée';
            form.reset();
          } else {
            // 🟡 Orange — SMTP absent, mailto auto
            pfStatus('warn',
              '✓ Demande sauvegardée — ouverture de votre messagerie dans 1 seconde…<br>'+
              '<button onclick="openMailtoContact()" style="margin-top:10px;background:linear-gradient(135deg,#1d4ed8,#2563eb);color:#fff;border:none;padding:10px 22px;border-radius:8px;font-size:12px;font-weight:700;cursor:pointer;font-family:DM Sans,sans-serif">'+
              '📧 Ouvrir ma messagerie maintenant</button>'
            );
            if(btxt) btxt.textContent = '📨 Relancer →';
            setTimeout(openMailto, 1000);
          }
        } else {
          // 🔴 Rouge — erreur
          pfStatus('error',
            '⚠ '+(res.error||'Erreur serveur — réessayez.')+'<br>'+
            '<button onclick="openMailtoContact()" style="margin-top:10px;background:linear-gradient(135deg,#7c3aed,#d946ef);color:#fff;border:none;padding:10px 20px;border-radius:8px;font-size:12px;font-weight:700;cursor:pointer;font-family:DM Sans,sans-serif">'+
            '📧 Envoyer directement par messagerie</button>'
          );
          if(btxt) btxt.textContent = '📨 Envoyer ma demande';
          setTimeout(openMailto, 1500);
        }
      })
      .catch(function(){
        if(sbtn) sbtn.disabled = false;
        if(btxt) btxt.textContent = '📨 Envoyer ma demande';
        // 🔴 Erreur réseau
        pfStatus('error',
          '⚠ Erreur réseau — votre messagerie s\'ouvre maintenant.<br>'+
          '<button onclick="openMailtoContact()" style="margin-top:8px;background:linear-gradient(135deg,#1d4ed8,#2563eb);color:#fff;border:none;padding:9px 18px;border-radius:7px;font-size:12px;font-weight:700;cursor:pointer;font-family:DM Sans,sans-serif">'+
          '📧 Renvoyer</button>'
        );
        setTimeout(openMailto, 700);
      });
  });
})();


;/* ── bloc 5/12 ── */

/* CHATBOT CONSEILPREV */
(function(){
/* Cle API retiree : le chat passe par le serveur (/api/chat), moteur hybride. */
var OPEN=false,HIST=[],BUSY=false,READY=false;
var SYS='Tu es Sentinel, expert reglementaire CONSEILPREV (Paris). Tu reponds en francais, avec precision et concision (max 280 mots). Domaines : EU AI Act (Regl. 2024/1689), NIS2, RGPD, DORA, ISO 42001, ISO 27001, gouvernance IA, cybersecurite industrielle. Tu aides aussi a naviguer sur le site CONSEILPREV et Sentinel AI. Pour tout projet ou audit, oriente vers christophe.cerf@outlook.com. Pas d avis juridique - orientations expertes.';
var TAGS=['Art. 6 AI Act','Obligations NIS2','Classification IA','Sanctions AI Act','Comment utiliser Sentinel AI ?','Audit de conformite'];
var WELCOME='Bonjour, je suis <strong>Sentinel</strong>, votre assistant reglementaire propulse par CONSEILPREV.<br><br>Je peux vous aider sur l\'<strong>EU AI Act</strong>, <strong>NIS2</strong>, <strong>RGPD</strong> et la gouvernance IA, ainsi que sur la navigation dans Sentinel AI.';

window.cpcToggle=function(){
  OPEN=!OPEN;
  var p=document.getElementById('cpcPanel');
  var b=document.getElementById('cpcBtn');
  if(!p) return;
  if(OPEN){
    p.classList.add('open');
    if(b) b.classList.remove('has-notif');
    if(!READY){cpcInit();READY=true;}
    setTimeout(function(){var i=document.getElementById('cpcInput');if(i)i.focus();},100);
  } else {
    p.classList.remove('open');
  }
};

function cpcInit(){
  var t=document.getElementById('cpcTags');
  if(t) t.innerHTML=TAGS.map(function(tg){
    return '<button class="cpc-tag" onclick="cpcSend(\''+tg.replace(/'/g,'\\\'')+'\')" title="'+tg.replace(/"/g,'&quot;')+'">'+(tg.length>22?tg.substring(0,22)+'…':tg)+'</button>';
  }).join('');
  /* AI-DISCLOSURE (IA Act, art. 50.1) : information des la premiere interaction. */
  cpcAdd('bot','<div class="ia50-notice"><span class="ia50-badge">IA</span><span>Vous \u00e9changez avec un <strong>assistant fond\u00e9 sur l\u2019intelligence artificielle</strong>, et non avec une personne. Ses r\u00e9ponses peuvent comporter des erreurs et ne constituent pas un conseil juridique.</span></div>');
  cpcAdd('bot',WELCOME);
}

function cpcAdd(role,html){
  var m=document.getElementById('cpcMsgs');
  if(!m) return;
  var d=document.createElement('div');
  d.className='cpc-msg '+role;
  d.innerHTML='<div class="cpc-av '+role+'">'+(role==='bot'?'S':'V')+'</div>'
    +'<div class="cpc-bubble">'+html+'</div>';
  m.appendChild(d);
  m.scrollTop=m.scrollHeight;
  return d;
}

function cpcTyping(){
  var m=document.getElementById('cpcMsgs');
  if(!m) return null;
  var d=document.createElement('div');
  d.className='cpc-msg bot';d.id='cpcTyping';
  d.innerHTML='<div class="cpc-av bot">S</div>'
    +'<div class="cpc-bubble"><div class="cpc-typing"><span></span><span></span><span></span></div></div>';
  m.appendChild(d);
  m.scrollTop=m.scrollHeight;
  return d;
}

var cpcDerniere='', cpcBulle=null;

window.cpcSend=function(preset,mode){
  if(BUSY) return;
  var inp=document.getElementById('cpcInput');
  var txt=mode?cpcDerniere:(preset||(inp?inp.value.trim():''));
  if(!txt) return;
  if(!mode){
    if(inp){inp.value='';inp.style.height='auto';}
    cpcBulle=cpcAdd('user',txt.replace(/</g,'&lt;').replace(/>/g,'&gt;'));
    cpcDerniere=txt;
    HIST.push({role:'user',content:txt});
  }
  BUSY=true;
  var ty=cpcTyping();
  fetch('/api/chat',{
    method:'POST', credentials:'same-origin',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({message:txt, history:HIST.slice(-8), minimisation:mode||''})
  })
  .then(function(r){return r.json();})
  .then(function(d){
    if(ty)ty.remove();
    if(d && d.code==='donnees_personnelles'){
      var av=cpcAdd('bot',cpMinHtml(d));
      av.addEventListener('click',function(e){
        var t=e.target.getAttribute&&e.target.getAttribute('data-mz'); if(!t) return;
        av.remove();
        if(t==='corriger'){
          for(var k=HIST.length-1;k>=0;k--){ if(HIST[k].role==='user'){ HIST.splice(k,1); break; } }
          if(cpcBulle){ cpcBulle.remove(); cpcBulle=null; }
          if(inp){ inp.value=cpcDerniere; inp.focus(); }
          return;
        }
        BUSY=false; window.cpcSend(null,t);
      });
      BUSY=false;
      return;
    }
    if(d.envoye){        // caviarde : la conversation repart du texte transmis
      for(var q=HIST.length-1;q>=0;q--){ if(HIST[q].role==='user'){ HIST[q].content=d.envoye; break; } }
      if(cpcBulle){ var bl=cpcBulle.querySelector('.cpc-bubble'); if(bl) bl.textContent=d.envoye; }
    }
    // Aucun bloc « Sources » : voir le widget jumeau plus haut.
    var rep=d.reply || (d.error ? ('Erreur : '+d.error) : 'Reponse indisponible.');
    HIST.push({role:'assistant',content:rep});
    cpcAdd('bot',rep.replace(/\n/g,'<br>').replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>'));
    BUSY=false;
  })
  .catch(function(){
    if(ty)ty.remove();
    cpcAdd('bot','Connexion indisponible. Contactez-nous : <a href="mailto:christophe.cerf@outlook.com">christophe.cerf@outlook.com</a>');
    BUSY=false;
  });
};

setTimeout(function(){
  if(!OPEN){var b=document.getElementById('cpcBtn');if(b)b.classList.add('has-notif');}
},10000);
})();


;/* ── bloc 6/12 ── */


(function () {
  var overlay = document.getElementById("cpExitModal");
  if (!overlay) return;
  window.cpOpenEssai = function (e) {
    if (e && e.preventDefault) e.preventDefault();
    overlay.classList.add("is-visible");
    document.body.style.overflow = "hidden";
    var input = document.getElementById("cpEmail");
    if (input) input.focus();
  };
  function closeModal() {
    overlay.classList.remove("is-visible");
    document.body.style.overflow = "";
  }
  overlay.querySelectorAll("[data-cp-close]").forEach(function (btn) { btn.addEventListener("click", closeModal); });
  overlay.addEventListener("click", function (e) { if (e.target === overlay) closeModal(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeModal(); });
  var sub = document.getElementById("cpSubmit");
  if (sub) sub.addEventListener("click", function () {
    var input = document.getElementById("cpEmail");
    if (!input.checkValidity() || input.value.trim() === "") { input.reportValidity(); return; }
    window.location.href = "/login?plan=gratuit&essai=1&email=" + encodeURIComponent(input.value.trim());
  });
})();



;/* ── bloc 7/12 ── */

/* Fleches de defilement rapide : bas (en-tete) et haut (pied de page). */
window.cpScrollBottom = function(){
  var y = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);
  try { window.scrollTo({ top: y, behavior: "smooth" }); } catch(e){ window.scrollTo(0, y); }
};
window.cpScrollTop = function(){
  try { window.scrollTo({ top: 0, behavior: "smooth" }); } catch(e){ window.scrollTo(0, 0); }
};


;/* ── bloc 8/12 ── */

(function(){
  var d=document.getElementById('cpd-drawer'), s=document.getElementById('cpd-scrim'),
      btn=document.querySelector('.cpd-btn'), last=null;
  if(!d||!s) return;
  window.cpdOpen=function(){
    last=document.activeElement;
    s.classList.add('open'); d.classList.add('open'); d.setAttribute('aria-hidden','false');
    if(btn) btn.setAttribute('aria-expanded','true');
    document.documentElement.style.overflow='hidden';
    var c=d.querySelector('.cpd-close'); if(c) c.focus();
  };
  window.cpdClose=function(){
    s.classList.remove('open'); d.classList.remove('open'); d.setAttribute('aria-hidden','true');
    if(btn) btn.setAttribute('aria-expanded','false');
    document.documentElement.style.overflow='';
    if(last&&last.focus) last.focus();
  };
  document.addEventListener('keydown',function(e){ if(e.key==='Escape'&&d.classList.contains('open')) window.cpdClose(); });
  d.addEventListener('click',function(e){ if(e.target.closest('a')) window.cpdClose(); });
  var p=(location.pathname||'/').replace(/\/+$/,'')||'/';
  d.querySelectorAll('a.cpd-lnk').forEach(function(a){
    var h=(a.getAttribute('href')||'').split('#')[0].replace(/\/+$/,'');
    if(h&&h===p){ a.classList.add('active'); a.setAttribute('aria-current','page'); }
  });
})();


;/* ── bloc 9/12 ── */

document.addEventListener('DOMContentLoaded', function(){
  var selectors = '.sector-card, .norm-card, .risk-card';
  document.querySelectorAll(selectors).forEach(function(card){
    card.style.cursor = 'pointer';
    card.setAttribute('role', 'link');
    card.setAttribute('tabindex', '0');
    card.addEventListener('click', function(){
      window.open('/sentinel', '_blank', 'noopener');
    });
    card.addEventListener('keydown', function(e){
      if(e.key === 'Enter' || e.key === ' '){
        e.preventDefault();
        window.open('/sentinel', '_blank', 'noopener');
      }
    });
  });
});



;/* ── bloc 10/12 ── */

/* ══ ANTI-SCRAPING — Detection de navigateurs headless (signal silencieux) ══ */
(function(){
'use strict';
try {
  var signals = {
    webdriver: navigator.webdriver === true,
    no_plugins: navigator.plugins && navigator.plugins.length === 0,
    no_languages: !navigator.languages || navigator.languages.length === 0
  };
  if(signals.webdriver || signals.no_plugins || signals.no_languages){
    fetch('/api/client-signal', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify(signals)
    }).catch(function(){});
  }
} catch(e){}
})();



;/* ── bloc 11/12 ── */

(function(){
  var banner = document.getElementById('ai-act-banner');
  if(!banner) return;
  window.aiActBannerClose = function(){
    banner.style.display = 'none';
    document.body.classList.remove('has-ai-act-banner');
    localStorage.setItem('aiActBannerClosed', '1');
  };
  if(localStorage.getItem('aiActBannerClosed') === '1'){
    banner.style.display = 'none';
    return;
  }
  document.body.classList.add('has-ai-act-banner');
})();



;/* ── bloc 12/12 ── */

window.cpxExpandToggle = function(panelId){
  var panel = document.getElementById(panelId);
  if(!panel) return;
  var overlay = document.getElementById('cpx-overlay');
  if(!overlay){
    overlay = document.createElement('div');
    overlay.id = 'cpx-overlay';
    overlay.className = 'cpx-overlay';
    overlay.onclick = function(){ window.cpxCollapseAll(); };
    document.body.appendChild(overlay);
  }
  var isExpanded = panel.classList.contains('cpx-expanded');
  window.cpxCollapseAll();
  if(!isExpanded){
    panel.classList.add('cpx-expanded');
    overlay.classList.add('on');
    var btn = panel.querySelector('.cpx-expand-btn');
    if(btn) btn.textContent = '⤡';
    if(btn) btn.title = 'Réduire';
  }
};
window.cpxCollapseAll = function(){
  ['cpcPanel','vbox'].forEach(function(id){
    var p = document.getElementById(id);
    if(p){
      p.classList.remove('cpx-expanded');
      var btn = p.querySelector('.cpx-expand-btn');
      if(btn){ btn.textContent = '⤢'; btn.title = 'Agrandir pour une meilleure lecture'; }
    }
  });
  var overlay = document.getElementById('cpx-overlay');
  if(overlay) overlay.classList.remove('on');
};
document.addEventListener('keydown', function(e){
  if(e.key === 'Escape') window.cpxCollapseAll();
});


