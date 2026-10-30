# -*- coding: utf-8 -*-
"""QCM SÉCURITÉ DE L'IA — CE QUE LA BANQUE REFUSE DE CHARGER.

POURQUOI UN SECOND FICHIER. `qcm_securite_ia` relit sa banque à l'import et
lève : une question dont la bonne réponse pointe hors des options ne doit pas
se déployer, parce qu'un stagiaire en formation la verrait corrigée de
travers. Mais un module qui lève à l'import empêche de collecter tout fichier
de règles qui l'importe — la faute est attrapée et aucune règle ne la NOMME,
et le banc de mutations prendrait l'erreur de collecte pour une survivante.

CE FICHIER N'IMPORTE DONC PAS LE MODULE : il injecte un défaut précis dans une
copie jetable, l'importe là, et vérifie que le refus nomme CE défaut.

LES PORTES, ET POURQUOI CELLES-LÀ — ce sont les gestes d'une main qui édite
une question :
  · LA BONNE RÉPONSE HORS DES OPTIONS (un `a` resté sur l'ancien indice) ;
  · UNE OPTION DE PLUS, ou UN MOTIF D'ERREUR DE PLUS — l'appariement des
    motifs aux options fausses se décalerait en silence ;
  · UN CODE DE RÉFÉRENTIEL MAL FRAPPÉ — la fiche ne surlignerait rien ;
  · UNE CITATION EXTERNE ET DES CODES à la fois — deux vérités ;
  · DEUX QUESTIONS DE MÊME NUMÉRO — une question citée en comité ne se
    retrouverait plus ;
  · UN NIVEAU SANS QUESTION — il s'afficherait et ne s'ouvrirait pas ;
  · LE SEUIL DE LA MÉDAILLE LA PLUS HAUTE SOUS 1 — une question manquée
    passerait pour un sans-faute ;
  · UN CODE INCONNU DANS LA TABLE DE CORRESPONDANCE ;
  · MOINS DE TROIS GESTES « EN PRATIQUE ».
"""
import io
import os
import subprocess
import sys
import textwrap

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _refus(tmp_path, avant, apres, module="qcm_securite_ia"):
    src = io.open(os.path.join(_RACINE, module + ".py"), encoding="utf-8").read()
    assert src.count(avant) == 1, (
        "l'ancre du défaut injecté n'est plus dans %s.py (%d fois) : %r"
        % (module, src.count(avant), avant[:70]))
    d = tmp_path / "copie"
    d.mkdir()
    (d / (module + ".py")).write_text(src.replace(avant, apres), encoding="utf-8")
    #  LA COPIE S'INSÈRE EN DERNIER POUR ÊTRE TROUVÉE EN PREMIER.
    code = textwrap.dedent("""
        import sys
        sys.path.insert(0, %r)
        sys.path.insert(0, %r)
        try:
            __import__(%r)
        except RuntimeError as e:
            sys.stdout.write(str(e))
        else:
            sys.stdout.write("(charge sans broncher)")
    """) % (_RACINE, str(d), module)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True,
                       text=True, timeout=180, cwd=_RACINE)
    return (r.stdout or "") + (r.stderr or "")


_Q1 = '{"n": 1, "domaine": "llm", "niveau": "debutant",\n     "codes": ("LLM01", "ASI01", "T6"),'


def test_la_banque_se_charge_SANS_defaut_injecte(tmp_path):
    """LE TÉMOIN : sans lui, une copie qui ne se chargerait jamais ferait
    passer toutes les portes ci-dessous pour des refus."""
    assert _refus(tmp_path, "_verifier()\n\n\n# ═", "_verifier()\n\n\n# ═") == "(charge sans broncher)"


_PORTES = [
    ("bonne-reponse-hors-options", '     "a": 0,\n', '     "a": 4,\n',
     "indice de bonne réponse 4 hors des options"),
    ("option-de-trop", '"o": ("Une injection de prompt indirecte",',
     '"o": ("Une option de trop", "Une injection de prompt indirecte",',
     "5 options au lieu de 4"),
    ("motif-de-trop", '"faux": ("L’empoisonnement altère les données d’entraînement ou "',
     '"faux": ("Un motif de trop", "L’empoisonnement altère les données d’entraînement ou "',
     "4 motifs d'erreur au lieu de 3"),
    ("code-mal-frappe", _Q1, _Q1.replace('"LLM01"', '"LLM11"'),
     "code de référentiel inconnu 'LLM11'"),
    ("citation-et-codes", _Q1, _Q1 + '\n     "ref": "MITRE ATLAS · AML.T0000",',
     "une citation externe ET des codes OWASP"),
    ("numero-en-double", '{"n": 2, "domaine": "donnees"', '{"n": 1, "domaine": "donnees"',
     "numéro 1 en double"),
    ("niveau-vide", '("expert", "Le niveau expert",', '("expert2", "Le niveau expert",',
     "NIVEAUX[expert2] : aucune question"),
    ("seuil-du-sans-faute", '("platine", "Médaille de platine", "Sans faute", 1.0),',
     '("platine", "Médaille de platine", "Sans faute", 0.95),',
     "une question manquée passerait pour un sans-faute"),
    ("correspondance-inconnue", '"ASI10": {"llm": ["LLM06"]', '"ASI10": {"llm": ["LLM66"]',
     "OWASP_MAP[ASI10] : LLM inconnu 'LLM66'"),
    ("pratique-trop-courte",
     '"pratique": ("Encadrer tout contenu récupéré par des délimiteurs et "',
     '"pratique": ("Un seul geste",), "pratique_retiree": ("Encadrer tout contenu '
     'récupéré par des délimiteurs et "',
     "moins de trois gestes"),
]


@pytest.mark.parametrize("nom,avant,apres,attendu", _PORTES, ids=[p[0] for p in _PORTES])
def test_la_banque_REFUSE_de_se_charger_et_NOMME_le_defaut(tmp_path, nom, avant, apres, attendu):
    msg = _refus(tmp_path, avant, apres)
    assert msg != "(charge sans broncher)", "le défaut « %s » passe la garde" % nom
    assert attendu in msg, "le refus ne nomme pas « %s » : %s" % (attendu, msg[:400])
