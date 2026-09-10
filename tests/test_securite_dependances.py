# -*- coding: utf-8 -*-
"""Le manifeste ne redescend pas sous un plancher de sécurité connu.

CE QUE CETTE RÈGLE MESURE, ET CE QU'ELLE NE PEUT PAS MESURER. Elle lit
`requirements.txt` et compare chaque paquet à la version où TOUTES ses
advisories connues au 10 septembre 2026 (relevé pip-audit) sont corrigées. Elle
attrape un retour en arrière — la ligne qui revient à `pypdf==4.3.1` — et le
nomme. Elle NE prouve PAS que la version épinglée s'installe et fonctionne :
cela demande un build, hors de portée d'un test unitaire.

Ce site partage la pile de son jumeau (Flask + Gunicorn + pypdf) et lui ajoute
flask-cors — dont la version 4.0.0 portait dix advisories. La configuration
CORS, elle, est saine : les origines sont une liste explicite (`SITE_ORIGINES`),
jamais un joker. C'est la BIBLIOTHÈQUE qu'on relève, pas la politique.
"""
import io
import os

from packaging.requirements import Requirement
from packaging.version import Version

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paquet -> (plancher, version vulnérable relevée). Le plancher est la plus
# petite version qui efface toutes les advisories connues du paquet.
PLANCHERS = {
    "flask":       ("3.1.3",  "3.0.0"),
    "flask-cors":  ("6.0.0",  "4.0.0"),
    "requests":    ("2.33.0", "2.31.0"),
    "gunicorn":    ("23.0.0", "21.2.0"),
    "werkzeug":    ("3.1.6",  "3.0.1"),
    "pypdf":       ("6.16.1", "4.3.1"),
}


def _epingles():
    out = {}
    with io.open(os.path.join(ICI, "requirements.txt"), encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.split("#", 1)[0].strip()
            if not ligne:
                continue
            try:
                r = Requirement(ligne)
            except Exception:
                continue
            fige = [s.version for s in r.specifier if s.operator in ("==", "===")]
            if fige:
                out[r.name.lower().replace("_", "-")] = Version(fige[0])
    return out


def test_les_paquets_sensibles_sont_AU_DESSUS_de_leur_plancher():
    epingles = _epingles()
    for paquet, (plancher, vulnerable) in PLANCHERS.items():
        assert paquet in epingles, (
            "%s n'est plus épinglé dans requirements.txt : la règle ne peut "
            "plus garantir qu'il n'est pas sur une version vulnérable" % paquet)
        pose = epingles[paquet]
        assert pose >= Version(plancher), (
            "%s==%s est SOUS le plancher de sécurité %s (la version %s portait "
            "des advisories connues) : le manifeste est redescendu sur une "
            "version vulnérable" % (paquet, pose, plancher, vulnerable))
        assert Version(plancher) > Version(vulnerable), (paquet, plancher, vulnerable)


def test_le_manifeste_ne_reintroduit_pas_une_version_vulnerable_nommee():
    epingles = _epingles()
    for paquet, (_plancher, vulnerable) in PLANCHERS.items():
        if paquet in epingles:
            assert epingles[paquet] != Version(vulnerable), (
                "%s est revenu exactement à %s, la version vulnérable relevée "
                "au pentest" % (paquet, vulnerable))
