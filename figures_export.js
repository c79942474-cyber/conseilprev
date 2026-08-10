/* ══ EMPORTER LES FIGURES AVEC LES CHIFFRES ═══════════════════════════════════
 *
 * Les cartes et les graphiques de Sentinel sont dessinés DANS LE NAVIGATEUR, en
 * SVG, à partir des calculs servis par les modules. Le serveur ne les a jamais
 * vus : il connaît les nombres, pas leur image. Un document exporté sans elles
 * ne porterait que des tableaux — et perdrait précisément ce qui fait qu'on
 * regarde une carte plutôt qu'une colonne de chiffres.
 *
 * Ce fichier fait donc le chemin inverse : il rembobine chaque SVG en PNG et le
 * joint à la demande d'export.
 *
 * LE PIÈGE, ET IL EST TOTAL. Un SVG affiché dans une page emprunte le style de
 * cette page : la couleur d'un pays, la graisse d'une étiquette, l'épaisseur
 * d'un trait viennent de feuilles CSS extérieures au SVG. Sérialisé tel quel
 * puis rendu hors de la page, il perd TOUT cela d'un coup — on obtient une
 * silhouette noire sur fond transparent, et personne ne comprend pourquoi. Les
 * styles calculés sont donc recopiés en attributs, élément par élément, avant
 * la sérialisation. C'est laborieux et c'est la seule façon.
 *
 * CE QU'ON REFUSE. Une figure qu'on n'a pas pu produire n'est pas envoyée : le
 * composeur écrit alors « figure non jointe » à sa place. Envoyer une image
 * vide ou tronquée serait pire — le document paraîtrait complet.
 */
(function(){
  "use strict";

  /* Les propriétés qui portent l'apparence d'un dessin. Tout recopier
     produirait un fichier dix fois plus lourd sans rien ajouter à l'image. */
  var PROPS = ["fill", "fill-opacity", "fill-rule", "stroke", "stroke-width",
               "stroke-opacity", "stroke-dasharray", "stroke-linecap",
               "stroke-linejoin", "opacity", "font-family", "font-size",
               "font-weight", "font-style", "text-anchor", "letter-spacing",
               "dominant-baseline", "visibility", "display", "paint-order"];

  function styler(source, copie){
    var a = source.querySelectorAll("*"), b = copie.querySelectorAll("*");
    var n = Math.min(a.length, b.length);
    for(var i = 0; i < n; i++){
      var cs = window.getComputedStyle(a[i]);
      var t = "";
      for(var j = 0; j < PROPS.length; j++){
        var v = cs.getPropertyValue(PROPS[j]);
        if(v) t += PROPS[j] + ":" + v + ";";
      }
      b[i].setAttribute("style", t);
      /* Les classes ne servent plus à rien hors de la page, et elles font
         croire à un style qui ne s'appliquera pas. */
      b[i].removeAttribute("class");
    }
  }

  /* Un SVG en PNG, à l'échelle demandée. Rend une promesse de dataURL, ou de
     null si quoi que ce soit a échoué — jamais d'image partielle. */
  function svgEnPng(svg, largeur, echelle){
    return new Promise(function(resoudre){
      try{
        /* Un sélecteur qui désigne le CONTENEUR et non le dessin est une
           erreur silencieuse : on sérialiserait un <div> comme du SVG, l'image
           ne se chargerait jamais, et la figure manquerait sans qu'on sache
           pourquoi. On refuse donc explicitement — le manque est alors nommé. */
        if(!svg) return resoudre(null);
        if(String(svg.tagName || "").toLowerCase() !== "svg") return resoudre(null);
        var boite = svg.getBoundingClientRect();
        var vb = svg.viewBox && svg.viewBox.baseVal;
        var W = (vb && vb.width) || boite.width || largeur || 900;
        var H = (vb && vb.height) || boite.height || 500;
        var L = largeur || Math.min(1400, Math.max(700, Math.round(boite.width || W)));
        var K = echelle || 2;                    /* rendu net à l'impression */

        var copie = svg.cloneNode(true);
        styler(svg, copie);
        copie.setAttribute("xmlns", "http://www.w3.org/2000/svg");
        copie.setAttribute("width", W);
        copie.setAttribute("height", H);
        if(!copie.getAttribute("viewBox")) copie.setAttribute("viewBox", "0 0 " + W + " " + H);
        /* Un fond BLANC, posé explicitement. Le PNG transparent d'un SVG devient
           noir dans certaines visionneuses Word, et la carte y disparaît. */
        var fond = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        fond.setAttribute("x", "0"); fond.setAttribute("y", "0");
        fond.setAttribute("width", String(W)); fond.setAttribute("height", String(H));
        fond.setAttribute("fill", "#FFFFFF");
        copie.insertBefore(fond, copie.firstChild);

        var texte = new XMLSerializer().serializeToString(copie);
        var url = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(texte);
        var img = new Image();
        var fini = false;
        var rate = function(){ if(!fini){ fini = true; resoudre(null); } };
        img.onerror = rate;
        /* Une image qui ne se charge jamais bloquerait tout l'export. */
        setTimeout(rate, 8000);
        img.onload = function(){
          if(fini) return;
          fini = true;
          try{
            var c = document.createElement("canvas");
            c.width = Math.round(L * K);
            c.height = Math.round(L * K * H / W);
            var ctx = c.getContext("2d");
            ctx.fillStyle = "#FFFFFF";
            ctx.fillRect(0, 0, c.width, c.height);
            ctx.drawImage(img, 0, 0, c.width, c.height);
            resoudre(c.toDataURL("image/png"));
          }catch(e){ resoudre(null); }
        };
        img.src = url;
      }catch(e){ resoudre(null); }
    });
  }

  /* Récolte : `specs` est une liste de {cle, sel} — la clé attendue par le
     module d'export, et le sélecteur du SVG dans la page. Rend l'objet des
     figures effectivement produites, et la liste de celles qui manquent. */
  function collecter(specs){
    var faits = {}, manques = [];
    var suite = Promise.resolve();
    (specs || []).forEach(function(s){
      suite = suite.then(function(){
        var el = typeof s.sel === "string" ? document.querySelector(s.sel) : s.sel;
        if(!el){ manques.push(s.cle); return; }
        return svgEnPng(el, s.largeur, s.echelle).then(function(d){
          if(d && d.length > 200) faits[s.cle] = d;
          else manques.push(s.cle);
        });
      });
    });
    return suite.then(function(){ return { figures: faits, manques: manques }; });
  }

  /* Le téléchargement lui-même. Un serveur qui REFUSE répond en JSON : en
     faire un fichier livrerait un Word contenant un message d'erreur. */
  function telecharger(url, corps, nomDefaut){
    return fetch(url, {
      method: "POST", credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(corps || {})
    }).then(function(rep){
      var type = rep.headers.get("Content-Type") || "";
      if(type.indexOf("application/json") >= 0 || !rep.ok){
        return rep.json().catch(function(){ return {}; }).then(function(j){
          throw new Error((j && j.erreur) || ("erreur " + rep.status));
        });
      }
      var cd = rep.headers.get("Content-Disposition") || "";
      var m = cd.match(/filename="?([^";]+)"?/);
      var nom = m ? m[1] : nomDefaut;
      return rep.blob().then(function(b){ return { blob: b, nom: nom }; });
    }).then(function(r){
      var u = URL.createObjectURL(r.blob);
      var a = document.createElement("a");
      a.href = u; a.download = r.nom;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      /* Révocation différée : Firefox annule un téléchargement dont l'URL
         disparaît avant qu'il ne l'ait ouverte. */
      setTimeout(function(){ URL.revokeObjectURL(u); }, 4000);
      return r;
    });
  }

  window.FIG = { svgEnPng: svgEnPng, collecter: collecter, telecharger: telecharger };
})();
