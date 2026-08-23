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

`HISTORIQUE.bundle` porte **l'historique git complet — dix-huit commits**,
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

Une **manchette** porte la date de l'édition — qui est celle de la collecte —,
le nombre de fiches et celui des ruptures. Le bandeau, lui, ne reste que pour
ce qui ne va pas : il annonçait « toutes les sources ont répondu » à chaque
visite, et un bandeau d'alerte qui s'affiche aussi quand il n'y a pas d'alerte
n'alerte plus.

Une **barre latérale rétractable à toute largeur** dit ce que la page contient
et où l'on en est. Elle ne peut pas mentir sur son contenu : ses entrées sont
LUES DANS LA PAGE, ses comptes recopiés de chaque rubrique, et sa **légende**
est faite des éléments eux-mêmes — la pastille de la légende est celle des
cartes, ses noms viennent du référentiel. Un contrôle exige une silhouette
pour chaque rubrique servie, y compris celles qu'écrit le JavaScript.

**Quatre flèches** parcourent la page et le fil. Aucune ne fait silencieusement
rien : chacune voit son sens résolu au moment où elle est posée, ce sens
devient son intitulé, et une flèche sans emploi s'éteint en disant pourquoi.
Sur une fiche, gauche et droite sont la fiche précédente et la suivante dans
l'ordre du fil que vous lisiez, filtres compris ; ailleurs, la rubrique
précédente et la suivante.

La **première page montre le tri du moteur** au lieu de l'aplatir : la tête est
la première fiche du classement déjà publié, et des **intertitres de portée**
marquent, dans le fil, l'endroit où le classement change de niveau. Rien n'est
réordonné — si le tri cessait de grouper les portées, ces marques se
répéteraient, ce qu'il faudrait précisément voir.

Une **fiche se lit comme un article** : mesure bornée à 68 signes, texte suivi
plus aéré que les vignettes, bloc de source en signature. Mesuré au
navigateur, un paragraphe faisait auparavant cent quatre-vingts signes par
ligne — près du triple de ce qui se lit.

Chaque fiche porte **où vous en êtes** : contour bleu tant qu'elle reste à
lire, vert une fois ouverte — une mémoire qui ne quitte jamais votre
navigateur, et qui **n'est pas tenue sans votre accord**. Une fiche
**s'emporte en PDF ou en Word**, avec son statut, la nature de sa lecture et ce
qu'on ne sait pas. Un compte dispose d'un **classeur** pour ses propres
documents, qui dit avant le dépôt ce qu'il conserve.

Les **menus de filtre décrivent les fiches trouvées**, pas le corpus : ils
suivent les filtres en cours, chaque axe compté hors du sien pour qu'on puisse
toujours changer d'avis. Un menu qui n'a rien à proposer le dit au lieu de se
taire, et les pays portent leur nom plutôt que leur code ISO.

Une **bascule FR/EN** traduit toute l'interface — écrite à la main, ce site
n'employant aucune traduction automatique nulle part. Elle **déclare ce
qu'elle ne traduit pas** : les lectures critiques, dérivées de gabarits
français, et les titres, qui portent la langue de leur source. Le nombre
affiché avec cette réserve est mesuré, pas écrit.

### Ce que le site garde de vous — et ce qu'il ne garde pas

**Aucun cookie. Aucune requête vers un tiers. Aucune mesure d'audience.** Les
polices venaient de `fonts.googleapis.com` : une requête vers Google à chaque
visite, avant tout consentement, emportant l'adresse IP du lecteur pour de la
typographie — montage jugé contraire au RGPD par le tribunal régional de
Munich en janvier 2022. Elles sont au dépôt, sous licence SIL OFL qui
l'autorise.

**Pas de mur de cookies**, donc : il n'y a rien à accepter. Six entrées de
stockage local, dont cinq sont exemptées par l'article 5(3) ePrivacy parce
qu'elles sont le service demandé — langue, repli de la barre, jeton de session,
ordre de lecture, réponse elle-même. **Une seule s'écrit toute seule** : la
liste des fiches ouvertes. C'est la seule qui vous soit demandée, et rien
n'est écrit avant la réponse. **`/confidentialite` porte l'inventaire
complet**, et deux contrôles le comparent aux clés réellement écrites dans le
code — dans les deux sens.

Les **en-têtes de sécurité sont posés par l'application**, pas par
l'hébergeur : un réglage d'hébergeur disparaît au premier déménagement sans
que rien ne le signale. Politique de contenu fermée sur `default-src 'self'`,
sans `unsafe-inline` — ce qui a demandé de retirer les douze attributs `style`
dispersés dans les pages et le JavaScript.

**277 contrôles** passent. Ils ne vérifient pas que le code « marche » : ils
gardent les règles éditoriales, et chacun est écrit pour tomber le jour où
quelqu'un les assouplira. Chaque règle nouvelle a été confrontée à une
**mutation du code qu'elle garde** — et trois de ces mutations ont révélé des
contrôles trop faibles, qui ont été resserrés.

### Les dix-huit commits du bundle

    65be8bd  Une manchette, des intertitres de portée, et la fiche composée
             comme un article
    8e817a1  Quatre flèches dont aucune ne fait silencieusement rien
    a179c5f  La barre se replie partout, et ce que ce site garde de vous
    93de6bc  Ce que vous avez lu, ce que vous emportez, ce que vous rangez
    e44b55f  Une première page qui montre le tri, et une barre d'outils qui
             cesse d'en être un obstacle
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
