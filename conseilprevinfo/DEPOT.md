# Ce dossier n'est pas à sa place — mais il est en ligne

**https://conseilprevinfo.onrender.com/** — servi depuis le sous-dossier
`conseilprevinfo` de ce dépôt, par un Web Service Render distinct de celui
de la racine.

`conseilprevinfo` est un **site distinct** des deux autres : sa propre
application Flask, son propre corpus, son propre déploiement. Il n'a rien à
faire dans le dépôt `conseilprev`, et il n'y est que faute de mieux : la
session ne peut pas pousser vers `c79942474-cyber/conseilprevinfo`, ce dépôt
n'étant pas dans son ensemble de sources autorisées, et l'outil qui l'y
ajouterait demande une approbation interactive qu'une session automatique
n'obtient pas. **Ce n'est ni un problème de droits GitHub ni un problème de
dépôt : c'est le périmètre de la session.**

Cela n'empêche pas de le mettre en ligne. La suite dit comment, tout de
suite, sans attendre que le dossier ait rejoint son dépôt.

---

## 1. Le brancher sur Render — depuis CE dépôt

**Render → New → Web Service → `c79942474-cyber/conseilprev`.**

Puis renseigner :

| Champ | Valeur |
|---|---|
| **Root Directory** | `conseilprevinfo` |
| **Branch** | `claude/github-connexion-4j0mbe` *(voir l'avertissement)* |
| **Runtime** | Python |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn --workers 1 --threads 8 --timeout 120 app:app` |
| **Health Check Path** | `/api/sante` |

Variables d'environnement : `PYTHON_VERSION=3.11.9`, `VEILLE_TTL=1800`,
`KEV_MAX=40`.

### Ne PAS passer par « Blueprint » depuis ce dépôt

`conseilprev` porte **déjà un `render.yaml` à sa racine**, celui du site en
service. Un Blueprint réévaluerait ce fichier-là, donc le service vivant.
C'est un risque pris pour rien : un Web Service créé à la main donne
exactement le même résultat. Le fichier `conseilprevinfo/render.yaml` existe
pour porter les réglages **et leur motif** ; il redeviendra un vrai Blueprint
le jour où le dossier aura son propre dépôt.

### La branche, et pourquoi elle mérite un avertissement

Tant que ce travail vit sur `claude/github-connexion-4j0mbe`, c'est **cette
branche** qu'il faut désigner. Désigner `main` ferait déployer une branche où
`conseilprevinfo/` n'existe pas encore : Render échouerait à la construction
sans que la cause soit lisible dans le journal. Après fusion, repasser le
service sur `main`.

### Deux réglages qui ne sont pas des préférences

- **Un seul « worker ».** Le corpus vit **en mémoire de processus**
  (`_CORPUS` dans `app.py`). Deux workers, ce sont deux corpus, donc deux
  collectes complètes contre CISA, MITRE, OWASP et les autres — le double de
  charge sur des sources publiques, pour rien. Les fils d'exécution
  suffisent : ce site attend le réseau, il ne calcule pas.
- **120 secondes de délai.** La première requête après un démarrage **attend
  la collecte** (mesuré : 9 à 10 secondes). Avec les 30 secondes par défaut,
  gunicorn tuerait le worker en pleine collecte, redémarrerait, et
  recommencerait — une boucle où le site ne servirait jamais rien.

Aucune dépendance vers `conseilprev` ni vers `conseilprevcyber` : ce site ne
partage pas leur service, et ne doit pas.

---

## 2. Le faire rejoindre son propre dépôt

Depuis votre poste, aucune session nécessaire :

    git clone HISTORIQUE.bundle conseilprevinfo
    cd conseilprevinfo
    git remote set-url origin \
      https://github.com/c79942474-cyber/conseilprevinfo
    git push -u origin master

`HISTORIQUE.bundle` porte **l'historique git complet — quatorze commits**,
messages compris. Il ne s'agit donc pas de repartir d'une copie à plat : le
détail des corrections, des mesures et des défauts constatés vit dans ces
messages, et c'est souvent là qu'est l'information.

Une fois poussé, le déploiement se simplifie : **Render → New → Blueprint →
choisir le dépôt**, plus aucun champ à remplir — `render.yaml` porte tout.

Et ce dossier peut alors quitter `conseilprev` :

    git rm -r conseilprevinfo && git commit -m "conseilprevinfo rejoint son dépôt"

---

## Ce que le site sert aujourd'hui

**98 fiches**, 7 collecteurs, **6 sources lues sur 10** au registre — les
quatre autres portent chacune le motif écrit de leur sommeil, parce qu'un
registre qui annonce ce qu'il ne lit pas se vide de son sens.

Une **barre latérale** dit ce que la page contient et où l'on en est. Elle ne
peut pas mentir sur son contenu : ses entrées sont LUES DANS LA PAGE, et ses
comptes recopiés de chaque rubrique.

La **première page montre le tri du moteur** au lieu de l'aplatir : la tête est
la première fiche du classement déjà publié, jamais un choix de mise en page.
La barre porte l'état du corpus, recopié du même calcul. Sur téléphone, la
barre de filtres se replie — elle y prenait 44 % de l'écran.

Les **menus de filtre décrivent les fiches trouvées**, pas le corpus : ils
suivent les filtres en cours, chaque axe compté hors du sien pour qu'on puisse
toujours changer d'avis. Un menu qui n'a rien à proposer le dit au lieu de se
taire, et les pays portent leur nom plutôt que leur code ISO.

Une **bascule FR/EN** traduit toute l'interface — écrite à la main, ce site
n'employant aucune traduction automatique nulle part. Elle **déclare ce
qu'elle ne traduit pas** : les lectures critiques, dérivées de gabarits
français, et les titres, qui portent la langue de leur source. Le nombre
affiché avec cette réserve est mesuré, pas écrit.

**207 contrôles** passent. Ils ne vérifient pas que le code « marche » : ils
gardent les règles éditoriales, et chacun est écrit pour tomber le jour où
quelqu'un les assouplira. Chaque règle nouvelle a été confrontée à une
**mutation du code qu'elle garde**.

### Les quatorze commits du bundle

    ee260cd  Les menus décrivaient le corpus, pas les fiches trouvées
    4544401  Barre latérale, et une bascule FR/EN qui dit ce qu'elle ne traduit pas
    f5aee5e  Déploiement : les deux chemins, et pourquoi pas Blueprint
    0c1f527  OWASP, et quatre défauts que le pont a fait sortir
    64aabd7  Trois contrôles de la confrontation ne gardaient rien
    000b815  Confronter un document au corpus — et dire quand ça ne marche pas
    182da88  Le registre annonçait neuf sources, le corpus en lisait quatre
    89f52b3  Abonnement, réglages, et un bulletin qui sait se taire
    cd99020  Des pistes d'instruction dérivées du corpus, jamais d'un pari
    d66802d  ATLAS relie ses incidents à ses techniques, et dit comment
    a5cddca  Des liens que la source affirme, et non que ce site déduit
    3ab5c0e  Croisement sourcé, et les axes qui ne donnent rien le disent
    e2d7ca4  CONSEILPREV INFO — le socle éditorial d'une veille qui refuse
             d'inventer
