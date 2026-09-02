# -*- coding: utf-8 -*-
"""Les sources de chaque communiqué — et celles qu'on ne peut pas joindre.

POURQUOI CE MODULE, ET POURQUOI LES SOURCES NE SONT PAS SIMPLEMENT ÉCRITES DANS
LA PAGE. Elles y étaient, en prose : « l'Arcep relève », « un article de
recherche de 2021 ». Un lecteur qui veut vérifier n'a alors rien à ouvrir — il
doit chercher lui-même ce que nous avons déjà trouvé. UNE SOURCE QU'ON NE PEUT
PAS JOINDRE EST UNE INTENTION, PAS UNE SOURCE.

CE QUE CE MODULE DÉCLARE, ET CE QU'IL REFUSE D'INVENTER. Chaque entrée porte son
éditeur, son millésime et, quand nous en tenons un dont nous sommes sûrs, son
adresse. QUAND NOUS N'EN TENONS PAS, LE CHAMP RESTE VIDE ET LA RAISON EST
ÉCRITE. Fabriquer une adresse plausible serait pire que de n'en donner aucune :
un lien qui rend 404 se découvre au moment où quelqu'un cherche à vérifier,
c'est-à-dire au moment où la confiance se joue.

Le registre général des sources du site récolte ce module comme les autres —
c'est pourquoi les variables commencent par SOURCES. Ajouter une source ici la
fait paraître là-bas ; rien à tenir à jour de part et d'autre.

CE QU'IL NE FAIT PAS : ouvrir les adresses pour vérifier qu'elles répondent. Un
lien mort serait annoncé comme vivant, et cette limite est écrite plutôt que
cachée — la même que celle du registre général.
"""
VERSION = "2026-09-a"

# ── LES SOURCES, PAR COMMUNIQUÉ ────────────────────────────────────────────
# `lien` vaut None quand nous ne tenons pas d'adresse dont nous soyons sûrs.
# `reserve` dit alors quoi chercher, et pourquoi l'adresse manque.
SOURCES_COMMUNIQUES = {
    "na5": [
        {"titre": "Energy and AI", "editeur": "Agence internationale de l'énergie",
         "annee": "2025", "lien": "https://www.iea.org/reports/energy-and-ai",
         "nature": "rapport",
         "note": "Le scénario de référence de ce rapport porte la trajectoire "
                 "de consommation des centres de données à l'horizon 2030."},
        {"titre": "Carbon Emissions and Large Neural Network Training",
         "editeur": "Patterson et al.", "annee": "2021",
         "lien": "https://arxiv.org/abs/2104.10350", "nature": "article de recherche",
         "note": "La seule des trois empreintes d'entraînement citées par la "
                 "fiche commentée qui soit publiée avec sa méthode."},
        {"titre": "Enquête annuelle sur l'empreinte environnementale du numérique",
         "editeur": "Arcep", "annee": "2023 (parc déclarant)", "lien": None,
         "nature": "enquête",
         "reserve": "Les valeurs d'eau sur site et en amont sont reprises de "
                    "notre module `eau_dc`, qui les tient de cette enquête. "
                    "L'adresse de l'édition exacte reste à joindre."},
        {"titre": "United States Data Center Energy Usage Report",
         "editeur": "Lawrence Berkeley National Laboratory", "annee": "2024",
         "lien": None, "nature": "rapport",
         "reserve": "Millésime de données 2023. L'adresse stable de cette "
                    "édition reste à joindre."},
        {"titre": "Règlement délégué (UE) 2024/1364 — indicateurs de durabilité "
                  "des centres de données", "editeur": "Union européenne",
         "annee": "2024",
         "lien": "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32024R1364",
         "nature": "texte réglementaire",
         "note": "C'est ce texte qui fixe l'eau DU SITE comme indicateur "
                 "déclaré — d'où le fait que l'amont manque partout."},
        {"titre": "L'IA et l'environnement : ce que je retiens (fiche n°1)",
         "editeur": "Jean Ponroy", "annee": "2026", "lien": None,
         "nature": "document commenté",
         "reserve": "Fiche pédagogique diffusée sur LinkedIn, commentée par ce "
                    "communiqué. Adresse de publication à joindre."},
    ],
    "na4": [
        {"titre": "Règlement (UE) 2024/1689 établissant des règles harmonisées "
                  "concernant l'intelligence artificielle", "editeur": "Union européenne",
         "annee": "2024",
         "lien": "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32024R1689",
         "nature": "texte réglementaire",
         "note": "Article 50 : obligations de transparence. Le paragraphe 2 "
                 "porte le marquage lisible par machine, et il pèse sur le "
                 "fournisseur."},
        {"titre": "Coalition for Content Provenance and Authenticity (C2PA)",
         "editeur": "C2PA", "annee": "spécification en vigueur",
         "lien": "https://c2pa.org/", "nature": "standard ouvert",
         "note": "Métadonnées de provenance attachées au fichier, pour l'image "
                 "et la vidéo."},
        {"titre": "SynthID-Text — filigrane statistique pour le texte généré",
         "editeur": "Google DeepMind", "annee": "2024", "lien": None,
         "nature": "publication technique",
         "reserve": "Publication citée par la synthèse commentée. Adresse à "
                    "joindre avant de s'en prévaloir."},
        {"titre": "Synthèse sur le marquage des contenus générés par IA",
         "editeur": "InfoQ", "annee": "2026", "lien": None,
         "nature": "synthèse de presse",
         "reserve": "Document commenté par ce communiqué. L'association d'une "
                    "technique à un fournisseur donné n'a pas été vérifiée à "
                    "la source par nos soins."},
    ],
    "na3": [
        {"titre": "Proposition de Cloud and AI Development Act",
         "editeur": "Commission européenne", "annee": "3 juin 2026", "lien": None,
         "nature": "proposition législative",
         "reserve": "Proposition, non encore adoptée : elle doit être examinée "
                    "par le Parlement et le Conseil. L'adresse du document "
                    "COM reste à joindre."},
        {"titre": "Règlement (UE) 2024/1689 — obligations des fournisseurs de "
                  "modèles à usage général", "editeur": "Union européenne",
         "annee": "2024",
         "lien": "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32024R1689",
         "nature": "texte réglementaire",
         "note": "Ce que le règlement corrige — la documentation des modèles — "
                 "et ce qu'il ne garantit pas : ni continuité, ni portabilité."},
        {"titre": "Part de marché des fournisseurs européens de services en nuage",
         "editeur": "Commission européenne", "annee": "2017-2022", "lien": None,
         "nature": "donnée citée",
         "reserve": "Chiffres repris de l'exposé des motifs de la proposition. "
                    "À vérifier au texte publié."},
    ],
    "na2": [
        {"titre": "Règlement (UE) 2024/1689 — article 50",
         "editeur": "Union européenne", "annee": "2024",
         "lien": "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32024R1689",
         "nature": "texte réglementaire",
         "note": "Les trois échéances citées — 2 août 2026, 2 décembre 2026, "
                 "2 février 2027 — se vérifient dans ce texte et dans celui "
                 "qui l'a modifié."},
        {"titre": "Code de bonnes pratiques sur le marquage et l'étiquetage des "
                  "contenus générés par l'IA", "editeur": "Commission européenne — Bureau de l'IA",
         "annee": "10 juin 2026", "lien": None, "nature": "code volontaire",
         "reserve": "L'adhésion est volontaire ; les obligations de l'article 50 "
                    "s'imposent que le code soit signé ou non. Adresse de la "
                    "version finale à joindre."},
    ],
    "na": [
        {"titre": "Digital Omnibus on AI — modification du règlement (UE) 2024/1689",
         "editeur": "Conseil de l'Union européenne et Parlement européen",
         "annee": "juin 2026", "lien": None, "nature": "texte modificatif",
         "reserve": "Les reports d'échéances cités doivent être vérifiés au "
                    "texte publié au Journal officiel. Adresse à joindre."},
        {"titre": "Règlement (UE) 2024/1689 — texte modifié",
         "editeur": "Union européenne", "annee": "2024",
         "lien": "https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32024R1689",
         "nature": "texte réglementaire",
         "note": "Articles 4, 5 et 50 : c'est ce texte que l'omnibus réaménage."},
    ],
}


def pour(identifiant):
    """Les sources d'un communiqué, dans l'ordre déclaré. Liste vide si aucune."""
    return list(SOURCES_COMMUNIQUES.get(identifiant) or [])


def couverture():
    """Quelle part des sources déclarées le lecteur peut RÉELLEMENT rouvrir.

    C'EST LE CHIFFRE QUI COMPTE, et le publier dérange un peu — c'est voulu. Une
    bibliographie où rien ne s'ouvre a l'apparence du sérieux sans en avoir le
    fond ; le lecteur doit savoir, avant de lire, ce qu'il pourra vérifier.
    """
    toutes = [s for lot in SOURCES_COMMUNIQUES.values() for s in lot]
    joignables = [s for s in toutes if (s.get("lien") or "").startswith("http")]
    return {
        "version": VERSION,
        "total": len(toutes),
        "joignables": len(joignables),
        "sans_lien": len(toutes) - len(joignables),
        "part_joignable": (round(len(joignables) / len(toutes), 3)
                           if toutes else None),
        "limite": "Les adresses ne sont pas ouvertes pour vérifier qu'elles "
                  "répondent : un lien mort serait annoncé comme vivant.",
    }
