# -*- coding: utf-8 -*-
"""LA DERNIÈRE DEMANDE PEINT L'ÉCRAN — PAS LA DERNIÈRE RÉPONSE ARRIVÉE.

CE QUI A ÉTÉ SIGNALÉ. Un contrôle de la recette DORA, « l'articulation nomme
les quatre dispositions écartées », échouait par moments — sur l'ancien code
comme sur le nouveau. On l'avait cru instable.

CE QUE LA MESURE A TROUVÉ : UN DÉFAUT DE L'APPLICATION, PAS DE LA RECETTE.
Choisir « établissement de crédit » puis « identifié NIS 2 » envoie deux
qualifications dans la même milliseconde, la première avec NIS 2 encore
inconnu. Flask répond sur plusieurs fils : l'ordre d'arrivée est aléatoire.
Quand la réponse périmée arrivait la dernière, elle repeignait
l'articulation à vide — 0 disposition écartée au lieu de 4. Deux fois sur
seize au naturel, à chaque fois quand elle est retardée de 400 ms (recette,
section 2). Quatorze calculs de Sentinel avaient le même motif.

CE QUE CES RÈGLES FONT. La première EXÉCUTE la vraie page (le harnais de
tests/test_memoire_ecrans.py), lui rend les VRAIES réponses du moteur DORA
dans le mauvais ordre, et lit l'articulation affichée. La deuxième recense
chaque calcul des écrans de conformité dans le code, et exige qu'il prenne
un numéro de demande ET qu'il le vérifie avant de peindre : un calcul ajouté
demain sans garde tombe ici, sans que personne n'ait à l'inscrire.
"""
import io
import json
import os
import re
import sys

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RACINE)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dora  # noqa: E402
import dora_ponts  # noqa: E402
import test_memoire_ecrans as _tm  # noqa: E402

PAGE_JS = io.open(os.path.join(_RACINE, "sentinel.page.js"), encoding="utf-8").read()


def _reponse(identifiee_nis2):
    """Ce que /api/dora/qualifier rend, calculé par le moteur lui-même
    (app.py : dora.qualifier puis dora_ponts.articulation)."""
    d = {"entite": "etablissement_credit", "identifiee_nis2": identifiee_nis2}
    q = dora.qualifier(d)
    a = dora_ponts.articulation(q, identifiee_nis2)
    return json.loads(json.dumps({"ok": q.get("ok", False), "qualification": q,
                                  "articulation": a}, default=str))


def _executer(scenario):
    ancien = _tm._refs
    reponses = {"null": _reponse(None), "true": _reponse(True)}
    _tm._refs = lambda: dict(ancien(), dora_reponses=reponses)
    try:
        return _tm._executer(scenario)
    finally:
        _tm._refs = ancien


#: Le fetch de la page, remplacé : chaque requête reste EN ROUTE jusqu'à ce
#: que le scénario décide de lui répondre — et dans quel ordre.
_EN_ROUTE = r"""
const enRoute = [];
global.fetch = function (u, o) {
  return new Promise(function (resoudre, rejeter) {
    enRoute.push({ u: String(u), corps: (o && o.body) || '',
      rendre: function (j) { resoudre({ json: function () { return Promise.resolve(j); } }); },
      echouer: function () { rejeter(new Error('coupure')); } });
  });
};
function ecartes() {
  const a = document.getElementById('dora-articulation');
  return a ? (a.textContent.match(/Article 2[013]|Chapitre VII/g) || []).length : -1;
}
"""


def test_le_moteur_ecarte_bien_quatre_dispositions_quand_NIS2_est_connu():
    """LE TÉMOIN. Sans lui, la règle suivante pourrait passer sur un moteur
    qui n'écarte plus rien du tout."""
    assert len(_reponse(True)["articulation"].get("ecarte") or []) == 4
    assert not (_reponse(None)["articulation"].get("ecarte") or [])


def test_la_reponse_PERIMEE_ne_repeint_pas_l_articulation_DORA():
    """LE DÉFAUT, EXÉCUTÉ. Deux champs, deux qualifications en route ; la
    bonne répond d'abord, la périmée ensuite — l'ordre qui échouait."""
    o = _executer(_EN_ROUTE + r"""
      DORA_REF = REFS.dora;
      doraChamp('entite', 'etablissement_credit');
      doraChamp('identifiee_nis2', 'oui');
      const q = enRoute.filter(function (a) { return a.u.indexOf('/api/dora/qualifier') >= 0; });
      out.envoyees = q.length;
      const frais = q.filter(function (a) { return /"identifiee_nis2":true/.test(a.corps); })[0];
      const perime = q.filter(function (a) { return /"identifiee_nis2":null/.test(a.corps); })[0];
      out.deux = !!(frais && perime);
      if (out.deux) {
        frais.rendre(REFS.dora_reponses['true']);
        await attendre(20);
        out.apresFrais = ecartes();
        perime.rendre(REFS.dora_reponses['null']);
        await attendre(20);
        out.apresPerime = ecartes();
        out.regime = DORA_REGIME;
      }
    """)
    assert o["envoyees"] == 2 and o["deux"], (
        "le scénario ne reproduit plus la course : %d qualification(s)" % o["envoyees"])
    assert o["apresFrais"] >= 4, "la bonne réponse n'est pas peinte : %r" % o
    assert o["apresPerime"] >= 4, (
        "LA RÉPONSE PÉRIMÉE A REPEINT L'ARTICULATION : %d disposition(s) après "
        "elle, %d avant" % (o["apresPerime"], o["apresFrais"]))


def test_un_ECHEC_perime_n_efface_pas_un_verdict_frais():
    """L'AUTRE MOITIÉ. Une requête ancienne qui échoue après coup écrivait
    « Qualification momentanément indisponible » par-dessus un verdict juste :
    la garde vaut pour l'échec comme pour la réussite."""
    o = _executer(_EN_ROUTE + r"""
      DORA_REF = REFS.dora;
      doraChamp('entite', 'etablissement_credit');
      doraChamp('identifiee_nis2', 'oui');
      const q = enRoute.filter(function (a) { return a.u.indexOf('/api/dora/qualifier') >= 0; });
      q[1].rendre(REFS.dora_reponses['true']);
      await attendre(20);
      out.avant = document.getElementById('dora-verdict').textContent;
      q[0].echouer();
      await attendre(20);
      out.apres = document.getElementById('dora-verdict').textContent;
    """)
    assert "Cadre complet" in o["avant"], "le verdict frais n'est pas peint : %r" % o["avant"][:80]
    assert "indisponible" not in o["apres"], (
        "un échec PÉRIMÉ a effacé le verdict : %r" % o["apres"][:80])


def test_une_reponse_en_route_ne_repeint_pas_un_ecran_REMIS_A_ZERO():
    """LE NUMÉRO EST PRIS AVANT LA REMISE À ZÉRO. Vider le type d'entité
    n'envoie aucune requête ; si le numéro n'était pris qu'avant l'envoi,
    une qualification encore en route repeindrait un verdict sur l'écran
    que l'on vient de vider."""
    o = _executer(_EN_ROUTE + r"""
      DORA_REF = REFS.dora;
      doraChamp('entite', 'etablissement_credit');
      doraChamp('entite', '');
      const q = enRoute.filter(function (a) { return a.u.indexOf('/api/dora/qualifier') >= 0; });
      out.envoyees = q.length;
      q[0].rendre(REFS.dora_reponses['true']);
      await attendre(20);
      out.verdict = document.getElementById('dora-verdict').textContent;
      out.regime = DORA_REGIME;
    """)
    assert o["envoyees"] == 1, o
    assert "Renseignez le type" in o["verdict"] and o["regime"] is None, (
        "la réponse en route a repeint l'écran vidé : %r" % o["verdict"][:80])


def test_CHAQUE_calcul_des_ecrans_de_conformite_prend_un_numero_et_le_VERIFIE():
    """LE RECENSEMENT, DÉRIVÉ DU CODE. Chaque POST vers /api/dora, /api/cra,
    /api/recyf, /api/parcours ou /api/conformite est un calcul relancé à la
    saisie. Il doit prendre un numéro de demande AVANT de partir, et le
    vérifier dans sa réponse. Prendre le numéro sans le vérifier ne protège
    de rien — c'est la moitié de la règle qu'une relecture laisse passer."""
    sites, nus = [], []
    for m in re.finditer(r"fetch\(\s*'(/api/(?:dora|cra|recyf|parcours|conformite)/[^']*)'", PAGE_JS):
        if "'POST'" not in PAGE_JS[m.start():m.start() + 240]:
            continue
        debut = max(PAGE_JS.rfind("\nfunction ", 0, m.start()),
                    PAGE_JS.rfind("\nwindow.", 0, m.start()))
        nom = re.match(r"\n(?:function |window\.)(\w+)", PAGE_JS[debut:debut + 80]).group(1)
        fin = PAGE_JS.find("\n}", m.start())
        avant, apres = PAGE_JS[debut:m.start()], PAGE_JS[m.start():fin]
        pris = re.search(r"var (\w+) = derniereDemande\(", avant) \
            or re.search(r"var (\w+) = \+\+\w+_DEMANDE;", avant)
        # LA VÉRIFICATION EST CHERCHÉE LÀ OÙ ELLE SERT : dans le gestionnaire
        # de la RÉPONSE, et dans le `.catch` quand celui-ci peint. Une garde
        # présente dans le seul `.catch` laissait passer la réponse périmée —
        # une mutation l'a montré.
        coupe = apres.find(".catch(")
        reponse = apres[:coupe] if coupe >= 0 else apres
        echec = apres[coupe:apres.find("});", coupe) + 3] if coupe >= 0 else ""
        def _garde(txt):
            return pris and (re.search(r"\b%s\(\)" % pris.group(1), txt)
                             or re.search(r"\b%s [!=]== \w+_DEMANDE" % pris.group(1), txt))
        peint = re.search(r"innerHTML|textContent", echec)
        verifie = _garde(reponse) and (not peint or _garde(echec))
        sites.append(nom)
        if not verifie:
            nus.append("%s (%s)" % (nom, m.group(1)))
    assert len(sites) >= 14, "le recensement ne trouve que %d calculs : %s" % (len(sites), sites)
    assert not nus, "calculs dont la réponse périmée peut encore peindre : %s" % nus


def test_derniereDemande_ne_reconnait_QUE_la_derniere_demande_de_sa_cle():
    """LA GARDE ELLE-MÊME, exécutée : la plus récente d'une clé est à jour,
    la précédente ne l'est plus, et une autre clé ne la dérange pas."""
    import shutil
    import subprocess
    node = shutil.which("node")
    if not node:
        pytest.skip("node absent")
    m = re.search(r"function derniereDemande\(cle\) \{.*?\n\}", PAGE_JS, re.S)
    assert m, "la garde derniereDemande est introuvable"
    code = m.group(0) + r"""
      var a1 = derniereDemande('a'), b1 = derniereDemande('b'), a2 = derniereDemande('a');
      process.stdout.write(JSON.stringify([a1(), a2(), b1()]));"""
    r = subprocess.run([node, "-e", code], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout) == [False, True, True], r.stdout
