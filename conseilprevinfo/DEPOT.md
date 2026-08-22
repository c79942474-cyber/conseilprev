# Ce dossier n'est pas à sa place — et le dépôt qui l'attend existe

`conseilprevinfo` est un **site distinct** des deux autres : sa propre
application Flask, son propre corpus, son propre déploiement. Il n'a rien à
faire dans le dépôt `conseilprev`, et il n'y est que faute de mieux.

## Où il doit aller

    https://github.com/c79942474-cyber/c79942474-cyber-conseilprevinfo

Ce dépôt a été créé le 22 août 2026. **La session n'a pas pu y pousser** : le
proxy git répond

    access denied by the git proxy: … is not in this session's authorized
    repository set

Le dépôt n'est pas dans l'ensemble des sources autorisées de la session, et
l'outil qui l'y ajouterait (`add_repo`) demande une approbation interactive
que cette session ne peut pas obtenir. Ce n'est donc ni un problème de droits
GitHub ni un problème de dépôt : c'est le périmètre de la session.

## Comment le pousser — trois voies, la première étant la plus simple

**1. Depuis votre poste** (aucune session nécessaire) :

    git clone HISTORIQUE.bundle conseilprevinfo
    cd conseilprevinfo
    git remote set-url origin \
      https://github.com/c79942474-cyber/c79942474-cyber-conseilprevinfo
    git push -u origin master

**2. Depuis une nouvelle session** dont les sources incluent ce dépôt : il
suffira alors de reprendre le dossier et de pousser.

**3. En autorisant le dépôt dans la session en cours**, si l'interface vous
propose d'approuver l'ajout d'une source.

`HISTORIQUE.bundle` contient **l'historique git complet — huit commits**,
messages compris. Il ne s'agit donc pas de repartir d'une copie à plat : le
détail des corrections, des mesures et des défauts constatés vit dans ces
messages.

## Une fois poussé

Supprimer ce dossier du dépôt `conseilprev` :

    git rm -r conseilprevinfo && git commit -m "conseilprevinfo rejoint son dépôt"

## Déploiement

Ce site se déploie **séparément** sur Render : `python app.py`, port lu dans
`PORT`. Dépendances : `flask`, `pyyaml` (ATLAS et Electricity Maps sont
publiés en YAML), et `pypdf` seulement si vous voulez que la confrontation
lise les PDF — sans lui, elle le dit et accepte les autres formats.

Il n'a aucune dépendance vers `conseilprev` ni vers `conseilprevcyber`, et ne
doit pas partager leur service.

## Les huit commits contenus dans le bundle

    000b815  Confronter un document au corpus — et dire quand ça ne marche pas
    182da88  Le registre annonçait neuf sources, le corpus en lisait quatre
    89f52b3  Abonnement, réglages, et un bulletin qui sait se taire
    cd99020  Des pistes d'instruction dérivées du corpus, jamais d'un pari
    d66802d  ATLAS relie ses incidents à ses techniques, et dit comment
    a5cddca  Des liens que la source affirme, et non que ce site déduit
    3ab5c0e  Croisement sourcé, et les axes qui ne donnent rien le disent
    e2d7ca4  CONSEILPREV INFO — le socle éditorial d'une veille qui refuse
             d'inventer
