"""LE CHARGEMENT DES PAGES — deux défauts que l'extraction du JavaScript a créés.

CE QUE L'EXTRACTION A CHANGÉ SANS QUE PERSONNE LE VOIE. Le JavaScript en ligne
des pages a été sorti vers des fichiers `.page.js` chargés en `defer`. Un
script en ligne s'exécute PENDANT l'analyse du document : `document.readyState`
y vaut « loading ». Un script différé s'exécute APRÈS l'analyse mais AVANT
`DOMContentLoaded` : `readyState` y vaut « interactive ».

PREMIER DÉFAUT — CE QUI TOURNAIT DEUX FOIS. Sept endroits de sentinel
écrivaient deux instructions INDÉPENDANTES là où il fallait une alternative :

    document.addEventListener('DOMContentLoaded', function(){ … });
    if(document.readyState !== 'loading'){ … }

En ligne, le `if` était faux et seul l'écouteur tirait. En différé, le `if` est
vrai — et l'écouteur tire quand même un instant plus tard. Les sept fonctions
s'exécutaient deux fois. Cela se voyait au réseau :
`/api/notifications/summary` demandé deux fois par chargement.

SECOND DÉFAUT — LA MÊME QUESTION POSÉE SEPT FOIS. Six endroits demandaient
« qui est connecté ? » avec leur propre `fetch('/api/sentinel-auth/me')`, ce
qui donnait sept requêtes réelles au chargement. Et cette route ne se contente
pas de lire la session : elle appelle `check_pending_reports()` et
`_essai_relances()`, qui ouvrent chacun la base. Sept appels, c'est sept
connexions et quatorze requêtes SQL pour une réponse identique.

CE QUE CES CONTRÔLES LISENT. Le JavaScript débarrassé de ses commentaires.
Deux fois déjà, une règle écrite pour ce défaut a accusé un COMMENTAIRE qui le
citait — dont celui qui décrit le défaut en tête de `sentinel.page.js`. Une
règle qui confond la prose et le code ne mesure pas ce qu'elle prétend.
"""
import glob
import io
import os
import re
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)


def _sans_commentaires(src):
    """Le code, et rien que le code.

    Un automate minimal : il suit les chaînes (simples, doubles, gabarits)
    pour ne pas prendre un `//` d'URL pour un commentaire, et retire les
    blocs `/* */` et les fins de ligne `//`."""
    out, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if c in "\"'`":
            j = i + 1
            while j < n and src[j] != c:
                j += 2 if src[j] == "\\" else 1
            out.append(src[i:j + 1])
            i = j + 1
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append("\n" * src.count("\n", i, j))   # garde la numérotation
            i = j
        elif src.startswith("//", i):
            j = src.find("\n", i)
            i = n if j < 0 else j
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _fichiers():
    for f in sorted(glob.glob(os.path.join(ICI, "*.page.js"))):
        yield os.path.basename(f), _sans_commentaires(
            io.open(f, encoding="utf-8").read())


def _doubles_declenchements(nom, code):
    """Un écouteur `DOMContentLoaded` suivi, dans les lignes voisines, d'un
    test de `readyState` SANS `else` : les deux chemins s'exécutent."""
    fautes = []
    lignes = code.split("\n")
    for i, l in enumerate(lignes):
        if "addEventListener(" not in l or "DOMContentLoaded" not in l:
            continue
        fenetre = "\n".join(lignes[i:i + 6])
        if "readyState" in fenetre and "else" not in fenetre:
            fautes.append("%s:%d  %s" % (nom, i + 1, l.strip()[:80]))
    return fautes


# ── PREMIER DÉFAUT : CE QUI TOURNAIT DEUX FOIS ────────────────────────────

def test_aucune_fonction_ne_se_declenche_deux_fois_au_chargement():
    """LE CONTRÔLE QUI AURAIT VU LE DÉFAUT. Il ne connaît pas les sept
    endroits : il relit tous les fichiers extraits."""
    fautes = []
    for nom, code in _fichiers():
        fautes += _doubles_declenchements(nom, code)
    assert not fautes, (
        "écouteur DOMContentLoaded ET test readyState sans alternative — "
        "en `defer`, les deux tirent :\n   " + "\n   ".join(fautes))


def test_le_controle_sait_reperer_le_motif_fautif():
    """DISCRIMINATION. Une règle qui déclare « rien à signaler » sans savoir
    reconnaître le défaut ne protège de rien. On lui soumet le code tel qu'il
    était écrit."""
    fautif = ("document.addEventListener('DOMContentLoaded', function(){ f(); });\n"
              "if(document.readyState !== 'loading'){ f(); }\n")
    assert _doubles_declenchements("essai.js", fautif)
    correct = ("if(document.readyState === 'loading'){\n"
               "  document.addEventListener('DOMContentLoaded', f);\n"
               "} else { f(); }\n")
    assert not _doubles_declenchements("essai.js", correct)


def test_le_controle_ne_confond_pas_un_commentaire_avec_du_code():
    """Deux versions de cette règle ont accusé un commentaire qui CITAIT le
    défaut — dont celui qui l'explique en tête de `sentinel.page.js`."""
    prose = ("/* On écrivait autrefois :\n"
             "   document.addEventListener('DOMContentLoaded', function(){ f(); });\n"
             "   if(document.readyState !== 'loading'){ f(); } */\n"
             "_auDomPret(f);\n")
    assert not _doubles_declenchements("essai.js", _sans_commentaires(prose))
    # …et il ne doit pas non plus prendre le `//` d'une URL pour un commentaire.
    assert "fonts.googleapis.com" in _sans_commentaires(
        "var u = 'https://fonts.googleapis.com/css2';\n")


def test_lassistant_de_chargement_est_une_alternative():
    """`_auDomPret` doit être un `if/else` : deux instructions indépendantes
    reproduiraient exactement le défaut qu'il corrige."""
    code = _sans_commentaires(
        io.open(os.path.join(ICI, "sentinel.page.js"), encoding="utf-8").read())
    i = code.index("function _auDomPret(")
    corps = code[i:i + 420]
    assert "else" in corps, "_auDomPret n'a pas d'alternative"
    assert "{once:true}" in corps or "{ once: true }" in corps, (
        "l'écouteur n'est pas posé en `once` : une seconde émission le "
        "rejouerait")


# ── SECOND DÉFAUT : LA MÊME QUESTION POSÉE SEPT FOIS ──────────────────────

def test_la_session_nest_demandee_quen_un_seul_endroit():
    """Sept requêtes pour une réponse identique, et sept fois le travail de
    fond greffé sur cette route côté serveur."""
    code = _sans_commentaires(
        io.open(os.path.join(ICI, "sentinel.page.js"), encoding="utf-8").read())
    directs = re.findall(r"fetch\(\s*['\"]/api/sentinel-auth/me['\"]", code)
    assert len(directs) == 1, (
        "%d appels directs à /api/sentinel-auth/me : ils doivent passer par "
        "`sentAuthMoi()`" % len(directs))
    assert code.count("sentAuthMoi()") >= 6, (
        "les appelants ne passent plus par l'accesseur partagé")


def test_lechec_reseau_ne_condamne_pas_la_page():
    """La promesse est gardée en mémoire. Si elle est gardée EN ÉCHEC, une
    coupure d'une seconde condamne tous les appels ultérieurs de la page."""
    code = _sans_commentaires(
        io.open(os.path.join(ICI, "sentinel.page.js"), encoding="utf-8").read())
    i = code.index("window.sentAuthMoi = function()")
    corps = code[i:i + 520]
    assert "_sentAuthPromesse = null" in corps, (
        "la mémoire n'est pas vidée en cas d'échec : aucun appel ultérieur ne "
        "pourra retenter")
    assert "throw" in corps, (
        "l'échec est avalé : les appelants qui ont un `.catch` ne le verraient "
        "plus, et croiraient à une session absente")


# ── CE QUE LA ROUTE COÛTE, ET POURQUOI LA DÉDUPLICATION COMPTE ────────────

def test_la_route_de_session_fait_bien_du_travail_de_fond():
    """Si cette route devenait une simple lecture de session, la déduplication
    perdrait l'essentiel de son intérêt — et le motif de ces contrôles serait
    à réécrire plutôt qu'à garder tel quel."""
    src = io.open(os.path.join(ICI, "app.py"), encoding="utf-8").read()
    i = src.index("def sentauth_me():")
    corps = src[i:src.index("\n@app.route", i)]
    assert "check_pending_reports()" in corps
    assert "_essai_relances()" in corps
