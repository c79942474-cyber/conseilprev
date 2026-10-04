/* LES FAITS DE L'ÉVÉNEMENT, ET LE FICHIER D'AGENDA — FICHIER ENGENDRÉ.
   ════════════════════════════════════════════════════════════════════════
   Source : evenement.py · Outil : outils/engendrer_invitation.py
   NE PAS MODIFIER À LA MAIN : une correction écrite ici serait perdue au
   prochain passage, et une règle refuse déjà que ce fichier dérive.

   Deux écrans s'en servent : le bandeau de l'accueil et la page
   d'invitation /formation-ia. Un seul fabricant de .ics pour les deux, parce
   que deux fabricants finissent par poser deux séances différentes. */
(function () {
  "use strict";

  var E = {
    titre: "Gouverner et sécuriser l'IA",
    public: "Formation pratique pour RSSI, DSI, CAIO, dirigeants et grands comptes",
    /* 14 h – 18 h à Paris le 9 novembre 2026, en heure d'hiver (UTC+1) :
       écrit en UTC pour que le fuseau du lecteur ne déplace rien. */
    debut: Date.UTC(2026, 10, 9, 13, 0, 0),
    fin: Date.UTC(2026, 10, 9, 17, 0, 0),
    lieu: "Novotel Paris Les Halles",
    adresse: "8 place Marguerite de Navarre",
    ville: "75001 Paris",
    acces: "Métro et RER : Châtelet – Les Halles",
    inscription: "christophe.cerf@outlook.com",
    animateur: "Christophe CERF",
    conditions: ["L'événement peut être reporté ou décalé en cas de participation insuffisante, ou annulé au plus tard 10 jours avant.", "Si besoin, l'événement pourra se dérouler dans un autre Novotel à Paris, à une autre date à définir."],
    page: "/formation-ia",
    fichier: 'formation-ia-conseilprev-2026-11-09.ics'
  };

  function echapper(s) {
    return String(s).replace(/\\/g, '\\\\').replace(/;/g, '\;')
      .replace(/,/g, '\\,').replace(/\n/g, '\\n');
  }

  /* RFC 5545 §3.1 : 75 OCTETS par ligne, pas 75 caractères — « é » en vaut
     deux. La suite repart après CRLF et une espace. */
  function plier(ligne) {
    var morceaux = ligne.match(/[\uD800-\uDBFF][\uDC00-\uDFFF]|[\s\S]/g) || [];
    var out = [], cour = '', n = 0;
    morceaux.forEach(function (c) {
      var o = encodeURIComponent(c).replace(/%[0-9A-F]{2}/gi, 'x').length;
      if (n + o > 75) { out.push(cour); cour = ' ' + c; n = 1 + o; }
      else { cour += c; n += o; }
    });
    out.push(cour);
    return out.join('\r\n');
  }

  function horodatage(t) {
    return new Date(t).toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');
  }

  E.lieuComplet = function () { return E.lieu + ', ' + E.adresse + ', ' + E.ville; };

  E.description = function () {
    return E.public + '.\n'
      + 'Animée par ' + E.animateur + ', CEO de CONSEILPREV.\n'
      + 'Gratuit sur inscription : ' + E.inscription + '\n'
      + E.acces + '\n'
      + 'Conditions : ' + E.conditions.join(' ');
  };

  E.ics = function () {
    return [
      'BEGIN:VCALENDAR', 'VERSION:2.0',
      'PRODID:-//CONSEILPREV//Invitation formation IA//FR',
      'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
      'BEGIN:VEVENT',
      'UID:formation-ia-2026-11-09@conseilprev',
      'DTSTAMP:' + horodatage(Date.now()),
      'DTSTART:' + horodatage(E.debut),
      'DTEND:' + horodatage(E.fin),
      'SUMMARY:' + echapper(E.titre + ' — formation CONSEILPREV'),
      'LOCATION:' + echapper(E.lieuComplet()),
      'DESCRIPTION:' + echapper(E.description()),
      'STATUS:CONFIRMED',
      'BEGIN:VALARM', 'ACTION:DISPLAY', 'TRIGGER:-P1D',
      'DESCRIPTION:' + echapper('Formation IA demain à 14h — ' + E.lieu),
      'END:VALARM',
      'END:VEVENT', 'END:VCALENDAR'
    ].map(plier).join('\r\n') + '\r\n';
  };

  /* Le téléchargement est fabriqué dans la page : aucun aller-retour, donc
     rien à attendre et rien qui puisse répondre 404 le jour J. */
  E.telechargerIcs = function () {
    var url = URL.createObjectURL(
      new Blob([E.ics()], { type: 'text/calendar;charset=utf-8' }));
    var a = document.createElement('a');
    a.href = url;
    a.download = E.fichier;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 10000);
  };

  window.CPEvenement = E;
})();
