# CONSEILPREV INFO — veille sourcée

Cybersécurité industrielle · Intelligence artificielle · Systèmes d'IA ·
Centres de données.

## Le parti pris

Chaque fiche porte **sa source, sa date, son statut de vérification et une
lecture critique dont la provenance est déclarée**. Une fiche qui ne remplit
pas ces conditions n'est pas affichée avec une réserve : elle est **refusée**
par `veille.publiables()`, qui est la seule porte du site.

La lecture critique vient de l'un de trois endroits, jamais confondus :

- **dérivée par règles** — composée à partir des seules données de la source,
  par des règles publiées dans `ingestion.py`. Reproductible : deux collectes
  rendent le même texte, mot pour mot. Aucun modèle de langage n'intervient.
- **rédigée et signée** — un avis d'analyste, daté, qui engage son signataire.
- **brouillon de modèle** — ne sort jamais. Deux verrous indépendants
  l'en empêchent (le statut ET la nature de lecture).

## Démarrer

    pip install flask
    python app.py            # http://127.0.0.1:5000

## Les sources

Neuf sources admises, toutes **atteintes et lues** depuis l'environnement de
conception le 22 août 2026 — voir `sources.py`, champ `verifie_le`. Le bouton
« Sonder » de la page va réellement rechercher l'adresse et rend ce qu'elle
répond, à l'instant.

Six autres sont déclarées `A_BRANCHER` : elles sont refusées (403) ou
injoignables depuis l'environnement de conception. Elles se brancheront en
production, où l'accès sortant est libre.

## Le croisement (`croisement.py`)

Le site rapproche des fiches, et **dit pourquoi** chaque rapprochement
existe. Cinq types de lien, rangés par force :

1. **Déclaré par la source** — le référentiel d'origine affirme lui-même la
   relation (`relationship` d'ATT&CK, étapes de `procedure` d'ATLAS). Le seul
   lien qui n'engage pas le cabinet : ce n'est pas inférer, c'est citer. Les
   références du référentiel voyagent avec le lien.
2. Même éditeur · 3. Même pays · 4. Même technologie — des règles écrites
   dans le module, donc défendables mais nôtres.
5. **Même période** — présentée à part, sous le nom de *voisinage*, parce
   qu'une proximité de calendrier n'est pas une relation.

`mesure_liens()` et `mesure_entites()` comptent ce que chaque axe forme
réellement, **y compris quand il ne forme rien** : un site qui n'afficherait
que ses axes féconds enseignerait une couverture qu'il n'a pas.

## Les pistes (`decision.py`)

Quatre déclencheurs publiés dérivent des **pistes d'instruction** depuis le
corpus. Chacune porte ce qui la déclenche (fiches nommées), ce qu'elle
suppose, ce qui la disqualifierait, et — avant tout le reste — **ce qu'elle
n'établit pas**, à commencer par l'existence d'un acheteur.

Le module s'interdit tout chiffre de marché, toute prédiction, toute piste
qui ne pointe aucune fiche. Le classement suit la **solidité du
déclencheur**, jamais un attrait commercial supposé, que ce site n'a aucun
moyen d'évaluer.

## L'abonnement (`abonnes.py`, `bulletin.py`) — `/abonnement`

Comptes, connexion, sujets suivis et seuil de signalement.

- **Aucun mot de passe n'est conservé**, ni en clair ni sous forme
  réversible : seul un dérivé `scrypt` (n = 2¹⁵, sel par compte) est gardé,
  et la comparaison est à temps constant.
- **Le formulaire n'est pas un annuaire** : ni l'inscription ni la connexion
  ne laissent deviner qu'une adresse est déjà abonnée — même message, même
  temps de calcul.
- **L'effacement est réel** : le compte sort du registre, ses sessions avec.
- **Le bulletin sait se taire.** Quand rien ne franchit le seuil de l'abonné,
  il est vide et le dit. Une lettre qui se complète les semaines creuses
  apprend au lecteur que sa longueur ne signifie rien.
- Le bulletin ne rédige aucune phrase d'analyse : il reprend les textes du
  site, sans quoi la version reçue par courriel ferait foi.

**Aucun courriel n'est envoyé.** `PRESTATAIRE_COURRIEL` vaut `None`, et
l'application l'écrit à l'écran plutôt que de laisser croire à un envoi :
l'expédition demande un domaine authentifié (SPF, DKIM, DMARC), un
prestataire et l'accord du responsable de traitement. Le bulletin est
**composé et montré** — c'est ce qui permet de le relire en entier.

Les comptes vivent en mémoire du processus, ce qui est assumé à cette étape :
le choix du support (chiffrement au repos, sauvegarde, effacement sur demande)
engage le responsable de traitement.

## Les contrôles

    python -m pytest tests/ -q

113 contrôles. Ils ne vérifient pas que le code « marche » : ils gardent les
règles éditoriales, et chacun a été confronté à une **mutation du code qu'il
garde** pour établir qu'il tomberait si la règle sautait.

## Ce qui reste à construire

Envoi réel des bulletins (prestataire et domaine authentifié) · persistance
des comptes · dépôt de documents client et comparaison au corpus · chaîne
multimédia.
