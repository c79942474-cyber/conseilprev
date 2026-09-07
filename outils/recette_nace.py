# -*- coding: utf-8 -*-
"""Revérifier les vingt-deux sections NACE contre la source publiée.

POURQUOI CE FICHIER EST ICI ET NON DANS `tests/`

`secteurs_nace.py` a été écrit depuis un environnement dont le proxy sortant
refuse eur-lex.europa.eu, ec.europa.eu et insee.fr. Les intitulés viennent d'un
relevé de l'annexe du règlement délégué (UE) 2023/137 obtenu par une autre voie,
et la version consultée était l'anglaise. C'est un relevé daté, pas une lecture
en direct — et la différence doit rester visible.

La suite de tests, elle, n'ouvre aucune socket : un contrôle qui dépend du
réseau échoue les jours où le réseau bouge, et une suite qui rougit pour une
raison extérieure finit par ne plus être lue. Ce script est donc à lancer À LA
MAIN, depuis une machine qui joint la source :

    python3 outils/recette_nace.py

CE QU'IL VÉRIFIE
  1. que les vingt-deux sections A à V existent, dans cet ordre ;
  2. que chaque intitulé officiel est celui de l'annexe, mot pour mot ;
  3. que les intitulés FRANÇAIS, aujourd'hui traduction de travail, peuvent
     être remplacés par ceux de la version française du règlement.

CE QU'IL NE PEUT PAS VÉRIFIER : que la correspondance entre les huit profils
Sentinel et les sections est la bonne. C'est un jugement de périmètre, pas un
fait publié ; il se relit, il ne se mesure pas.
"""
import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import secteurs_nace as N                                          # noqa: E402

ADRESSES = {
    "en": "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32023R0137",
    "fr": "https://eur-lex.europa.eu/legal-content/FR/TXT/HTML/?uri=CELEX:32023R0137",
}
# LE MOTIF S'ARRÊTE À LA SECTION SUIVANTE. Sans la sentinelle, « [^<\n|]{3,200} »
# avale la section d'après quand la source les sépare par des espaces plutôt
# que par des sauts de ligne — et la recette signale alors vingt et un écarts
# sur une source pourtant identique au référentiel. Le défaut a été trouvé en
# EXÉCUTANT la recette contre une annexe fabriquée, pas en la relisant.
MOTIF = re.compile(
    r"SECTION\s+([A-Z])\s*[\u2013\u2014-]\s*"
    r"(.{3,200}?)(?=\s*SECTION\s+[A-Z]\s*[\u2013\u2014-]|\s*\d|\s*$)",
    re.S)


def relever(langue):
    with urllib.request.urlopen(ADRESSES[langue], timeout=60) as r:
        page = r.read().decode("utf-8", "replace")
    texte = re.sub(r"<[^>]+>", " ", page)
    releve = {}
    for code, intitule in MOTIF.findall(texte):
        releve.setdefault(code, re.sub(r"\s+", " ", intitule).strip())
    return releve


def main():
    print("Référentiel local : %s, %d sections, relevé le %s (version %s)"
          % (N.SOURCE["revision"], len(N.SECTIONS), N.SOURCE["consulte_le"],
             N.SOURCE["version_consultee"]))
    ecarts = 0
    try:
        en = relever("en")
    except Exception as e:                                   # noqa: BLE001
        print("\nLa source anglaise n'est pas joignable depuis ici : %s" % e)
        print("C'est exactement la situation dans laquelle le module a été "
              "écrit. Relancez depuis un réseau qui joint eur-lex.")
        return 2

    for s in N.SECTIONS:
        publie = en.get(s["code"])
        if publie is None:
            print("  %s : ABSENTE de la source" % s["code"]); ecarts += 1
        elif publie.upper() != s["intitule_officiel"].upper():
            print("  %s : ÉCART\n      local  : %s\n      publié : %s"
                  % (s["code"], s["intitule_officiel"], publie)); ecarts += 1
    for code in sorted(set(en) - {s["code"] for s in N.SECTIONS}):
        print("  %s : présente à la source, absente du référentiel local"
              % code); ecarts += 1

    try:
        fr = relever("fr")
        print("\nVersion française relevée — à reporter dans `intitule` et à "
              "retirer de SOURCE['reserve'] :")
        for s in N.SECTIONS:
            if fr.get(s["code"]):
                print("  %s : %s" % (s["code"], fr[s["code"]]))
    except Exception as e:                                   # noqa: BLE001
        print("\nVersion française non joignable : %s" % e)

    print("\n%d écart(s)." % ecarts)
    return 1 if ecarts else 0


if __name__ == "__main__":
    sys.exit(main())
