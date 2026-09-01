# DCWatch — base importée, non modifiée

**Contient des informations de DCWatch, mises à disposition sous
[Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/).**

DCWatch est un projet de recherche collaboratif porté par Hubblo.
Source : https://gitlab.com/hubblo/datacenter-watch — documentation :
https://dcwatch.hubblo.org/

<!-- table:debut -->
| | |
|---|---|
| Version importée | `2026.04.09`, récupérée à l'étiquette du même nom |
| Fichier | `export_summary.csv`, repris **tel quel**, sans modification |
| Empreinte SHA-256 | `3af6bb6765c17aa7b1d6a4f08d77aa93083fae6d087683ef30c819314df0e1fd` |
| Enregistrements | 520 |
| Importé le | 29 août 2026 |
<!-- table:fin -->

## Pourquoi ce répertoire est à part

Cette base n'est **pas** fusionnée avec le référentiel de centres de données de
CONSEILPREV, et ce n'est pas un détail d'organisation : c'est la condition qui
permet de l'employer sans ouvrir notre propre référentiel. La séparation porte
sur les **estimations** — c'est là que se joue la fusion. Cinq points
géographiques ont fait exception, par décision explicite ; voir plus bas.

**Comment cette base est tenue à jour.** Elle est figée sur l'étiquette
`2026.04.09`, et le fichier ci-dessous lui est identique octet pour octet.
`recette_dcwatch_amont.py` compare le dépôt à l'amont et **dit** quand celui-ci
a bougé ; elle ne remplace jamais la base d'elle-même, parce qu'un
rafraîchissement silencieux déplacerait des chiffres déjà publiés. Le tableau
ci-dessous est **calculé depuis le fichier**, entre deux marqueurs : il ne peut
plus décrire autre chose que ce qui est déposé.

L'ODbL impose le **partage à l'identique** (article 4.4) à toute *base dérivée*
dont on fait un usage public. Verser les puissances DCWatch dans le référentiel
servi par `/api/datacentres` créerait une telle base dérivée, et obligerait à
publier le référentiel fusionné sous ODbL.

L'article 4.5 dit exactement où passe la limite :

> **b.** Using this Database, a Derivative Database, or this Database as part of
> a Collective Database **to create a Produced Work does not create a Derivative
> Database** for purposes of Section 4.4;
>
> **c.** Use of a Derivative Database **internally within an organisation is not
> to the public** and therefore does not fall under the requirements of
> Section 4.4.

Et l'article 4.5.a précise qu'une *base collective* — deux bases côte à côte,
non fusionnées — n'a pas à être publiée sous ODbL ; seule la partie DCWatch
reste sous ODbL. C'est le régime de ce répertoire.

## Ce que cela autorise, et ce que cela interdit

**Autorisé** — produire et publier des chiffres agrégés, des cartes, des
graphiques, des ordres de grandeur. Ce sont des *travaux produits* au sens de
l'article 4.3 : ils portent la mention de provenance, rien de plus.

**Interdit ici** — faire sortir une ligne par site vers ce que le service
publie. `dcwatch.py` n'expose aucune fonction qui rende les enregistrements, et
une règle le vérifie sur ce qui SORT, pas sur la forme du code.

**Ce qui est passé, et de combien.** En septembre 2026, cinq communes que la
carte publiée nommait manquaient au référentiel de CONSEILPREV — Val-de-Reuil,
Amilly, Saint-Saturnin, Prévessin-Moëns, Bruges. Elles y sont entrées avec un
**point géographique** repris d'ici, aucun géocodeur n'étant joignable. Cette
page a d'abord continué d'affirmer le contraire ; elle dit maintenant ce qui
est.

Aucune **estimation** n'est entrée : ni puissance, ni surface, ni année, ni
gabarit — `capacite_mw` reste nul sur les 254 lignes servies. Les cinq portent
`point_source='dcwatch'`, la mention de provenance dans leur note, et une règle
borne leur nombre : c'est l'**ampleur** de l'emprunt, non son principe, qui
ferait basculer la lecture de l'article 4.4. Les deux lectures possibles — base
dérivée, ou extraction insubstantielle — sont exposées dans
`datacentres.LIMITES`, et n'y sont pas tranchées.

## Deux réserves qui ne viennent pas de la licence

1. **Article 4.8.** L'ODbL couvre les droits sur la *base*. Les contenus
   individuels peuvent porter leurs propres droits : DCWatch demande
   explicitement de respecter aussi la licence de ses sources.
2. **La méthode.** DCWatch se déclare non exhaustive, et son estimation de
   puissance est obtenue par mesure de bâtiment sur imagerie satellite. C'est
   une mesure de BÂTIMENT, pas de charge informatique — l'employer ne lève pas
   l'avertissement sur les mégawatts, il le déplace vers une autre méthode, à
   documenter comme telle.
