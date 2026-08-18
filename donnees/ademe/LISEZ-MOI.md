# Base Carbone® ADEME — fichiers d'origine, conservés tels quels

Ces fichiers ne sont pas de nous. Ils sont déposés ici **dans leur forme
d'origine**, sans retraitement, pour que les facteurs d'émission employés par
le site soient **lus** et jamais recopiés dans du code — un facteur recopié
cesse d'être vérifiable le jour où sa source change.

| Fichier | Ce qu'il porte | Poids |
|---|---|---|
| `base_carbone_v22.csv` | La Base Carbone® v22.0 complète — 15 264 lignes, dont les mix électriques nationaux | 8,5 Mo |
| `procedes_flux_ges.xlsx` | Procédés — flux de gaz à effet de serre | 1,3 Mo |
| `procedes_flux_interne.xlsx` | Procédés — flux internes | 0,6 Mo |
| `procedes_impacts.xlsx` | Procédés — impacts | 0,5 Mo |

## Provenance et licence

- **Éditeur** : ADEME (Agence de la transition écologique).
- **Portail** : <https://base-empreinte.ademe.fr/>
- **Licence annoncée par l'éditeur** : Licence Ouverte / Open Licence (Etalab),
  qui impose la **mention de la paternité** — « Base Carbone® — ADEME ».
  `Base Carbone` est une marque déposée de l'ADEME : la citer telle quelle
  fait partie des conditions d'emploi.

> **Ce que nous n'avons pas vérifié.** Ces mentions reprennent ce que l'éditeur
> annonce sur son portail. Elles n'ont **pas** été revérifiées en ligne depuis
> l'environnement où ce dépôt est construit, qui n'a pas d'accès sortant. Avant
> toute rediffusion de ces fichiers hors du présent dépôt, rouvrir le portail et
> lire les conditions en vigueur : elles peuvent avoir changé.

## Encodage — le piège

`base_carbone_v22.csv` est publié en **Windows-1252**, séparateur `;`, décimale
française. Le lire en UTF-8 ne lève pas toujours d'erreur : cela abîme
silencieusement les accents, et « Tchéquie » cesse alors de correspondre à
« Tchéquie ». `base_carbone.py` déclare donc l'encodage explicitement.

## Millésime — à lire avant de s'en servir

Les facteurs « Électricité / mix moyen » de cette version portent une période
de validité de **décembre 2017** pour la plupart des pays, **décembre 2019**
pour six d'entre eux. Ce sont les valeurs qui **font foi** pour un bilan
d'émissions de gaz à effet de serre français (BEGES, art. L229-25 du code de
l'environnement) ; ce ne sont **pas** celles qui décrivent le réseau européen
de 2026.

Le site sert donc les deux jeux de valeurs et nomme l'usage de chacun. Il ne
substitue rien : le raisonnement complet est dans l'en-tête de
`base_carbone.py`, et l'écart mesuré est publié par `/api/base-carbone`.
