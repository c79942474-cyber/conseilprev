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

`HISTORIQUE.bundle` porte **l'historique git complet — vingt-neuf commits**,
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

Il est **composé comme un quotidien**. Une gothique au bandeau — convention de
genre, vieille de deux siècles, dans laquelle est composé LE NOM DE CE SITE et
non l'emblème d'un autre, qui est une marque déposée. Playfair Display aux
titres, Newsreader à la colonne : un journal ne compose pas ses manchettes avec
le caractère de son texte. La règle est bornée — **Playfair ne descend pas sous
dix-huit pixels**, ses déliés y disparaissent, et un contrôle lit la taille
minimale de chaque règle qui l'emploie. La gothique, elle, ne compose qu'un
seul sélecteur : son fichier est sous-ensemblé aux lettres et ne porte pas de
chiffres.

Le bandeau se lit comme une première page : le mot-titre, un filet, le
**bandeau de genre** — les quatre sujets en capitales espacées entre deux
filets, la bande qu'un quotidien pose entre son titre et sa une —, puis le
chapeau dans le caractère de la colonne. Ce n'est pas un découpage
d'agrément : une ÉNUMÉRATION et une PROMESSE ne se composent pas pareil, et
les fondre donnait quatre lignes de texte centré sous un logotype.

**Les angles sont droits**, les filets hiérarchisés — épais sous le bandeau,
fins entre les blocs. Un usage de presse n'est pas repris, et c'est écrit : la
**justification**, essayée puis retirée. Un journal justifie parce qu'il coupe
les mots ; le navigateur ne coupe que dans la langue déclarée de la page, or
les chapeaux portent le texte des sources, anglais neuf fois sur dix.

**La typographie va jusqu'au fichier.** Un PDF embarque ses polices : ses
titres prennent le même caractère qu'à l'écran. Le Word non, délibérément — il
n'embarque rien, il existe pour être repris, et un caractère absent chez le
destinataire fait une mise en page qui se défait à la première frappe.

Le site est imprimé sur un **papier couché brillant** — noirs denses, filets
fins, blanc légèrement froid, et le lustre diffus qui distingue un couché d'un
mat à l'œil nu. Ce n'est pas un crème refroidi : c'est un autre papier, celui
du supplément plutôt que du quotidien. Le changement a servi à corriger deux
**défauts de contraste** qui vivaient là depuis l'origine — « SIGNAL FAIBLE »
et « STRUCTURANT » s'affichaient sous le seuil AA, et personne ne l'avait vu
parce que personne ne l'avait mesuré.

La **barre latérale est un meuble, pas une marge** : un blanc cassé glacé
nettement plus soutenu que la feuille le jour, une **ardoise** quand le lecteur
a réglé son système en mode sombre. Elle a ses propres jetons de couleur, si
bien que la bascule redéfinit dix valeurs et rien d'autre — les teintes des
icônes comprises, sans quoi elles seraient invisibles sur l'ardoise. La feuille,
elle, ne bascule pas : ce site est un journal, et un papier ne devient pas noir
la nuit.

Elle est **rétractable à toute largeur**, dit ce que la page contient et où
l'on en est. Elle emploie les **caractères du journal** —
Newsreader nomme, JetBrains Mono étiquette et mesure, Inter tient les gloses —
et chaque groupe porte sa teinte, dont héritent son icône, son filet et les
icônes de ses entrées. Les teintes sont délibérément désaturées, hors des
familles du code éditorial : un menu peint en rouge et en vert apprendrait un
second vocabulaire de couleurs en face du premier.

Elle ne peut pas mentir sur son contenu : ses entrées sont LUES DANS LA PAGE —
et seulement celles qui sont RENDUES, une rubrique masquée n'étant pas une
destination —, ses comptes recopiés de chaque rubrique, et sa **légende** est
faite des éléments eux-mêmes : la pastille de la légende est celle des cartes,
ses noms viennent du référentiel. Un contrôle exige une silhouette pour chaque
rubrique servie, y compris celles qu'écrit le JavaScript.

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

Chaque fiche porte **où vous en êtes** : contour bleu complet tant qu'elle
reste à lire, contour vert **qui bat** une fois ouverte, et le mot « LUE » à
côté de la date — parce que bleu et vert sont exactement la paire que la
deutéranopie confond. Le battement dure une seconde et demie, soit un
vingtième du seuil de trois éclats par seconde au-delà duquel un clignotement
devient un risque ; il s'arrête d'office si le système du lecteur le demande,
et par un interrupteur posé au-dessus du fil comme dans la barre — qui **dit
quand rien ne bat**, puisque le vert n'apparaît que sur une fiche déjà ouverte
et qu'un bouton dont on ne peut pas constater l'effet apprend à se méfier de
tous les autres. Ce repère
tenait auparavant sur trois pixels d'un seul bord, en deux teintes sombres et
voisines : la mécanique marchait, mais personne ne pouvait le constater.

**Sans accord, aucune carte ne porte de marque** — et le fil dit pourquoi.
Peindre les quatre-vingt-dix-huit cartes en « à lire » affirmerait que vous
n'avez rien lu, alors que la vérité est que ce site **ne sait pas** : c'est
une autre chose, et c'est celle qui doit s'écrire. La mémoire ne quitte jamais
votre navigateur et **n'est pas tenue sans votre accord**. Une fiche
**s'emporte en PDF ou en Word**, avec son statut, la nature de sa lecture et ce
qu'on ne sait pas. Un compte dispose d'un **classeur** pour ses propres
documents, qui dit avant le dépôt ce qu'il conserve.

Les **menus de filtre décrivent les fiches trouvées**, pas le corpus : ils
suivent les filtres en cours, chaque axe compté hors du sien pour qu'on puisse
toujours changer d'avis. Un menu qui n'a rien à proposer le dit au lieu de se
taire, et les pays portent leur nom plutôt que leur code ISO.

Un menu **« Entreprise nommée »** s'y ajoute. Il ne repose sur aucune
extraction : `organisations.py` porte cinquante entrées écrites à la main,
chacune avec les formes **sous lesquelles les sources l'écrivent**, et le nom
n'est cherché QUE dans les champs où une source désigne une entité — `target`
chez ATLAS, `vendorProject` chez CISA. Jamais dans nos phrases d'analyse : le
filtre annoncerait sinon « les fiches qui concernent Microsoft » en servant
« les fiches où nous avons tapé Microsoft ». Le champ `target` d'ATLAS contient
aussi bien « OpenAI ChatGPT » que « Cloud-Based LLM Services » ou « Multiple
systems » — une extraction automatique en ferait des entreprises.

Le menu **Pays porte deux groupes nommés** : *le fait s'y situe*, et *siège de
l'entreprise nommée*. Le second ne dérive d'aucune source lue — c'est un apport
du cabinet, et sa mention voyage avec lui, du menu jusqu'à la fiche. Les fondre
ferait d'un incident contre un produit Microsoft un « fait américain ». Quand le
siège est disputé — VirusTotal, né à Málaga et filiale américaine ; Johnson
Controls, de droit irlandais et dirigé depuis Milwaukee — il reste **vide**, et
le module refuse de se charger si l'entrée n'écrit pas son motif.

**La revue** découpe le même corpus en deux : la semaine, et le mois **vu hors
de France**. Elle compte les fiches dont LE FAIT est daté de la période, jamais
celles collectées pendant la période — les deux dates ne coïncident pas, et une
revue bâtie sur la collecte titrerait la semaine en cours au-dessus de faits de
2021. Une période vide le dit, sans jamais écrire « il ne s'est rien passé » :
elle ne peut parler que du corpus. Les dates posées faute de mieux en sont
écartées et comptées ; la règle « internationale » est écrite et servie avec la
sélection ; ce qu'elle écarte est compté à part.

**La revue s'emporte en PDF et en Word**, et le document porte ce que porte la
page : ce qu'elle compte — en tête, pas en annexe —, ce qu'elle écarte, le
statut et la source de chaque entrée, et les deux rubriques vides. Un PDF qui
les omettrait serait la version « propre » de la revue, et il aurait perdu la
seule chose qu'elle dit d'elle-même. L'adresse écrite dedans rouvre la MÊME
période : un fichier reçu en comité doit pouvoir y ramener.

**Les reportages et les entretiens ne se dérivent pas, et la revue le dit.**
Les deux rubriques existent, elles sont **vides**, elles écrivent pourquoi et ce
qu'il faudrait. Le registre refuse toute pièce sans auteur nommé — « la
rédaction » n'est pas une signature —, sans méthode, sans source vérifiable, et
pour un entretien sans interlocuteur, sans date et sans accord explicite de
publication. Les fabriquer aurait été la seule chose que ce site s'interdit
absolument : un entretien inventé fait DIRE quelque chose à une personne nommée.

Une **bascule FR/EN** traduit l'interface, et **les analyses existent
désormais en anglais** : les gabarits de dérivation portent leurs deux colonnes
côte à côte dans `gabarits.py`, écrites à la main. Ce site n'emploie aucune
traduction automatique nulle part, et les deux colonnes ne peuvent pas
diverger — la logique qui choisit les phrases ne s'écrit qu'une fois.

**La langue des analyses est un réglage séparé de celle de l'interface** : un
francophone qui travaille en anglais veut souvent l'interface en anglais et les
analyses dans leur version d'origine ; un anglophone qui reçoit un lien veut
l'inverse. Le défaut suit l'interface, un clic explicite le fixe. Ce qui vient
de la SOURCE — titres d'origine, résumés, noms de techniques — garde sa langue.
La couverture est **mesurée, pas déclarée**, et une fiche qui n'a pas pu suivre
le dit sur elle-même. Le document emporté est dans la langue où il a été lu,
intertitres, dates et licence compris, et il dit sa langue en pied.

**Chaque source est relue au rythme auquel elle change** — un quart d'heure
pour le catalogue des vulnérabilités exploitées, vingt-quatre pour les
référentiels MITRE, qui pèsent neuf mégaoctets et bougent quelques fois par an.
Mesuré : un tour complet passe de 9,4 s à 1,4 s, ce qui permet au site de se
rafraîchir toutes les cinq minutes au lieu de trente sans devenir un visiteur
impoli. Le journal dit, source par source, si elle a été **relue** ou si l'on
n'y est pas retourné.

Le registre dit aussi **ce que ce site ne lit pas encore**, en distinguant deux
natures d'obstacle : ce qui se branchera au déploiement, et ce qui demande un
contrat commercial. **Les dépêches AFP et Reuters sont dans la seconde
catégorie** — aucune des deux n'a de flux libre, et publier sans licence
reviendrait à écrire une mention fausse à l'endroit précis où ce site promet de
dire vrai.

### Ce que le site garde de vous — et ce qu'il ne garde pas

**Aucun cookie. Aucune requête vers un tiers. Aucune mesure d'audience.** Les
polices venaient de `fonts.googleapis.com` : une requête vers Google à chaque
visite, avant tout consentement, emportant l'adresse IP du lecteur pour de la
typographie — montage jugé contraire au RGPD par le tribunal régional de
Munich en janvier 2022. Elles sont au dépôt, sous licence SIL OFL qui
l'autorise.

**Pas de mur de cookies**, donc : il n'y a rien à accepter. Huit entrées de
stockage local, dont sept sont exemptées par l'article 5(3) ePrivacy parce
qu'elles sont le service demandé — langue de l'interface, langue des analyses,
repli de la barre, jeton de session, ordre de lecture, arrêt du clignotement,
et la réponse elle-même. **Une seule s'écrit toute seule** : la liste des
fiches ouvertes. C'est la seule qui vous soit demandée, et rien n'est écrit avant la
réponse. **`/confidentialite` porte l'inventaire complet**, et deux contrôles
le comparent aux clés réellement écrites dans le code — dans les deux sens.

Les **en-têtes de sécurité sont posés par l'application**, pas par
l'hébergeur : un réglage d'hébergeur disparaît au premier déménagement sans
que rien ne le signale. Politique de contenu fermée sur `default-src 'self'`,
sans `unsafe-inline` — ce qui a demandé de retirer les douze attributs `style`
dispersés dans les pages et le JavaScript.

**Les quinze flux de presse de conseilprev sont au registre** — les mêmes que
ceux de son actualité IA et de sa veille réglementaire. Ils y arrivent à part,
et c'est le point : les dix sources d'origine livrent des **faits**, un flux
livre un **article**, c'est-à-dire le compte rendu qu'un tiers donne d'un fait
que ce site n'a pas vérifié. Toutes les fiches qui en naissent portent
`source_secondaire`, **la CNIL et le CERT-FR compris** : lire un flux, c'est
lire un avis de publication, pas ouvrir le document. Deux étiquettes reprises
de conseilprev sont corrigées — `artificialintelligenceact.eu` et `dig.watch`
y passent pour des autorités alors qu'ils sont édités par des organisations
privées, et le nom de domaine du premier prête à confusion. Deux requêtes
Google News sont refusées : un agrégateur n'est pas une source, et l'admettre
ferait entrer par une porte dérobée tout éditeur que la requête rapporte.
**Aucun des quinze ne porte « vérifiée »** : les vingt adresses ont été
réellement sondées, les vingt sont refusées par la politique réseau de
l'environnement de conception, et une date de vérification qu'on n'a pas faite
serait un mensonge à l'endroit exact où ce site promet de dire vrai.

**426 contrôles** passent. Ils ne vérifient pas que le code « marche » : ils
gardent les règles éditoriales, et chacun est écrit pour tomber le jour où
quelqu'un les assouplira. Chaque règle nouvelle a été confrontée à une
**mutation du code qu'elle garde** — et cinq de ces mutations ont révélé des
contrôles trop faibles, qui ont été resserrés. Un contrôle écrit trop STRICT a
aussi été corrigé plutôt que contourné : il supprimait la distinction qu'il
était censé protéger.

### Les trente commits du bundle

    db4575a  Les quinze flux de conseilprev entrent au registre — et un
             article n'y est pas un fait
    25458c4  Le bandeau de titre était converti à moitié
    3ea43c3  La composition passe à celle d'un quotidien — jusque dans les
             documents emportés
    919ad8d  L'interrupteur du clignotement obéissait sans qu'on puisse le
             constater
    a4afe6d  La revue s'emporte en PDF et en Word — réserves comprises
    b6937a6  Une revue hebdomadaire, une revue mensuelle internationale —
             et deux rubriques vides qui disent pourquoi
    fd06ed7  Un filtre par entreprise nommée, et deux provenances de pays
             qui ne se confondent pas
    ad5d9aa  Rendre visible ce qui est lu, et taire ce qui n'est pas su
    074c9e9  La barre latérale devient un meuble : blanc cassé le jour,
             ardoise glacée la nuit
    0541ce3  Chaque source relue à SA cadence, et le registre dit ce qu'il
             ne lit pas
    f12c4e6  Les analyses existent en anglais, et le lecteur choisit — ou pas
    3642a69  Le papier passe au couché brillant, et le menu prend les
             caractères du journal
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
