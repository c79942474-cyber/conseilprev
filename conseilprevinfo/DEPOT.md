# Ce dossier n'est pas à sa place, et voici pourquoi

`conseilprevinfo` est un **site distinct** des deux autres : sa propre
application Flask, son propre corpus, son propre déploiement. Il n'a rien à
faire dans le dépôt `conseilprev`, et il n'y est que faute de mieux.

## Ce qui s'est passé

Le dépôt `c79942474-cyber/conseilprevinfo` n'a pas pu être créé depuis la
session : l'intégration GitHub répond `403 Resource not accessible by
integration` — elle n'a pas le droit de créer des dépôts. Le travail
existait alors uniquement dans un conteneur éphémère, qui est recyclé après
un temps d'inactivité. Le déposer ici était le seul moyen de ne pas le
perdre.

## Comment le remettre à sa place

`HISTORIQUE.bundle` contient **l'historique git complet** des six commits,
messages compris. Il ne s'agit donc pas de repartir d'une copie à plat.

1. Créer le dépôt `c79942474-cyber/conseilprevinfo` (vide, sans README).
2. Restaurer l'historique et le pousser :

       git clone HISTORIQUE.bundle conseilprevinfo
       cd conseilprevinfo
       git remote set-url origin https://github.com/c79942474-cyber/conseilprevinfo
       git push -u origin master

3. Supprimer ce dossier du dépôt `conseilprev` :

       git rm -r conseilprevinfo && git commit -m "conseilprevinfo rejoint son dépôt"

Pour que la session puisse le faire elle-même la prochaine fois, il faut
soit créer le dépôt à la main d'abord, soit accorder à l'application GitHub
le droit de création de dépôts (claude.ai → Paramètres → Connecteurs →
GitHub).

## Déploiement

Ce site se déploie **séparément** sur Render : `python app.py`, port lu dans
`PORT`. Il n'a aucune dépendance vers `conseilprev` ni vers
`conseilprevcyber`, et ne doit pas partager leur service.

## Les six commits contenus dans le bundle

    89f52b3  Abonnement, réglages, et un bulletin qui sait se taire
    cd99020  Des pistes d'instruction dérivées du corpus, jamais d'un pari
    d66802d  ATLAS relie ses incidents à ses techniques, et dit comment
    a5cddca  Des liens que la source affirme, et non que ce site déduit
    3ab5c0e  Croisement sourcé, et les axes qui ne donnent rien le disent
    e2d7ca4  CONSEILPREV INFO — le socle éditorial d'une veille qui refuse
             d'inventer
