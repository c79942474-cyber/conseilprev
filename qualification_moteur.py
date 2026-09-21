# -*- coding: utf-8 -*-
"""
LE MOTEUR QUI RÉPOND — ET LA LAISSE QU'IL PORTE.

`qualification_assistee` ne connaît aucun fournisseur : il reçoit une
fonction `repondre(prompt, systeme) -> (ok, texte)`. Ce module est la seule
chose qui fabrique cette fonction, et c'est donc le seul endroit où il faut
regarder pour savoir ce que le moteur a le droit de faire.

CE QU'IL A LE DROIT DE FAIRE : répondre.

L'ÉCRITURE DE RÉFÉRENCE DU SDK EST CELLE-CI :

    query(prompt=..., options=ClaudeAgentOptions(
        allowed_tools=["Read", "Edit", "Bash"]))

Donner `Read`, `Edit` et `Bash` à un agent chargé de qualifier un registre
de conformité lui ouvre trois chemins vers la base : lire `registre_ia.db`,
le réécrire, lancer n'importe quoi. Une classification pourrait alors
changer sans qu'aucune personne l'ait décidée et sans qu'on sache laquelle.
C'est exactement ce que « en conservant une validation humaine » exclut.

ICI, LA LISTE D'OUTILS EST VIDE, et les outils d'écriture sont EN PLUS
nommés dans `disallowed_tools` — une liste vide se remplit par distraction,
un refus explicite se remarque. Les lignes du registre ne sont pas lues par
l'agent : elles voyagent dans le prompt, en données. L'agent n'a donc rien
à ouvrir, rien à écrire, et un seul tour pour répondre.

LE SDK LANCE UN PROCESSUS, PAS UNE REQUÊTE HTTP.
`claude_agent_sdk` pilote l'exécutable Claude Code. Là où il n'est pas
installé — un conteneur Python nu, par exemple — le SDK ne peut pas
démarrer. Le repli n'est pas un autre fournisseur : c'est le MÊME modèle,
appelé par l'API Messages d'Anthropic. Mistral ne sert pas ce chemin : une
qualification réglementaire qui changerait de moteur en silence changerait
aussi de raisonnement, sans que la trace le dise.
"""

import os

VERSION = "2026-09-a"

# Le modèle, fixé ici et réglable sans redéploiement, jamais choisi par
# l'appelant : laisser le navigateur nommer le modèle revient à lui laisser
# choisir le tarif à la ligne.
MODELE = os.environ.get("QUALIF_MODELE", "claude-sonnet-5")

# UN SEUL TOUR. La tâche est « lis cette déclaration et réponds en JSON » :
# elle n'a pas de deuxième tour légitime, et un agent qui boucle sur une
# tâche sans outils ne fait que dépenser.
TOURS_MAX = 1

# OÙ LE BUILD A POSÉ L'EXÉCUTABLE. `build.sh` installe Claude Code dans le
# dossier du projet et écrit le chemin RETENU — celui qui a répondu à
# `--version` — dans ce fichier. Le script n'a donc pas besoin de connaître
# les conventions de ce module, ni ce module celles de l'installateur.
MARQUEUR_CLI = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            ".cli-claude", "CHEMIN")

# L'INTERRUPTEUR, POUR NE PAS AVOIR À REDÉPLOYER DU CODE POUR CHANGER D'AVIS.
#   auto (défaut) — le SDK si l'exécutable est là, l'API sinon
#   sdk           — le SDK, et rien d'autre : s'il manque, la proposition échoue
#                   au lieu de passer en silence par un autre chemin
#   api           — l'API Messages, même si l'exécutable est installé
MOTEUR_VOULU = (os.environ.get("QUALIF_MOTEUR", "auto") or "auto").strip().lower()

# AUCUN OUTIL. Ce n'est pas une précaution de plus : c'est la précaution.
OUTILS_AUTORISES = []

# Nommés un par un, pour que leur absence soit une décision lisible et non
# l'effet d'une liste vide qu'on remplirait un jour sans y penser.
OUTILS_INTERDITS = [
    "Read", "Write", "Edit", "NotebookEdit", "Bash", "BashOutput",
    "Glob", "Grep", "WebFetch", "WebSearch", "Task", "TodoWrite",
]

# Les moteurs possibles, dans l'ordre où ils sont essayés.
MOTEURS = ("sdk", "api")

MOTEUR_TEXTE = {
    "sdk": "claude-agent-sdk (Claude Code en sous-processus, sans aucun outil)",
    "api": "API Messages d'Anthropic (repli quand l'exécutable Claude Code "
           "n'est pas installé)",
    "aucun": "Aucun moteur disponible",
}


def sdk_importable():
    try:
        import claude_agent_sdk  # noqa: F401
        return True
    except Exception:
        return False


def chemin_cli():
    """Où est l'exécutable Claude Code, ou None.

    Mesuré, pas supposé : sur Render, l'image Python n'en contient pas par
    elle-même, et une promesse de SDK qui tombe au premier appel vaut moins
    qu'un repli annoncé.

    L'ORDRE N'EST PAS ARBITRAIRE. Une variable d'environnement passe avant
    tout — c'est la seule façon de désigner un exécutable que ni le build ni
    les conventions n'ont prévu. Vient ensuite ce que `build.sh` a posé DANS
    le projet, parce que c'est le seul emplacement dont on sait qu'il
    survit jusqu'à l'exécution sur Render. Les emplacements standards
    ferment la marche.
    """
    import shutil

    declare = (os.environ.get("QUALIF_CLI_CHEMIN") or "").strip()
    if declare and os.path.exists(declare):
        return declare

    try:
        with open(MARQUEUR_CLI, encoding="utf-8") as f:
            pose = f.read().strip()
        if pose and os.path.exists(pose):
            return pose
    except Exception:
        pass

    trouve = shutil.which("claude")
    if trouve:
        return trouve
    for chemin in (os.path.expanduser("~/.npm-global/bin/claude"),
                   "/usr/local/bin/claude",
                   os.path.expanduser("~/.local/bin/claude")):
        if os.path.exists(chemin):
            return chemin
    return None


def executable_present():
    return chemin_cli() is not None


def options_sdk(systeme_prompt=""):
    """Les options EXACTES passées au SDK, rendues telles quelles.

    Les rendre permet de les mesurer pour de vrai : une règle qui lirait le
    code source pour vérifier que `allowed_tools` est vide passerait encore
    le jour où une autre ligne, plus bas, le remplit.
    """
    from claude_agent_sdk import ClaudeAgentOptions
    return ClaudeAgentOptions(
        allowed_tools=list(OUTILS_AUTORISES),
        disallowed_tools=list(OUTILS_INTERDITS),
        system_prompt=systeme_prompt,
        model=MODELE,
        max_turns=TOURS_MAX,
        # LE CHEMIN EST DONNÉ, PAS CHERCHÉ. Le SDK sait chercher `claude`
        # dans le PATH et dans quatre emplacements conventionnels ; aucun
        # d'eux n'est le dossier du projet, qui est justement le seul où
        # l'exécutable survit sur Render.
        cli_path=chemin_cli(),
        # UN DOSSIER DE CONFIGURATION ÉCRIVABLE. Le CLI écrit sous
        # `~/.claude` ; là où le home ne l'est pas, il refuserait de
        # démarrer pour une raison qui n'a rien à voir avec la tâche.
        env={"CLAUDE_CONFIG_DIR": os.environ.get(
            "CLAUDE_CONFIG_DIR", os.path.join(
                os.path.dirname(MARQUEUR_CLI), "config"))},
        # NI LES RÉGLAGES DU PROJET, NI CEUX DE L'UTILISATEUR. Sans cela le
        # SDK chargerait le CLAUDE.md du dépôt et ses compétences : des
        # consignes qui n'ont rien à voir avec une qualification, et que
        # personne n'a relues pour cet usage.
        setting_sources=[],
    )


def _texte_des_messages(messages):
    morceaux = []
    for m in messages:
        for bloc in getattr(m, "content", None) or []:
            t = getattr(bloc, "text", None)
            if t:
                morceaux.append(t)
    return "".join(morceaux)


def _par_sdk(prompt, systeme_prompt):
    import asyncio
    from claude_agent_sdk import query

    async def _aller():
        recus = []
        async for message in query(prompt=prompt,
                                   options=options_sdk(systeme_prompt)):
            recus.append(message)
        return recus

    try:
        messages = asyncio.run(_aller())
    except Exception as e:
        return False, "sdk_indisponible: %s" % str(e)[:200]
    texte = _texte_des_messages(messages)
    return (True, texte) if texte.strip() else (False, "reponse_vide")


def repondeur(secours=None, forcer=None):
    """La fonction de réponse, et le NOM du moteur qui la sert.

    Le nom est rendu avec elle parce qu'il sera écrit à côté de la
    proposition : six mois plus tard, savoir par quoi une proposition a été
    produite fait partie de la proposition.

    `secours` est l'appel à l'API Messages d'Anthropic, injecté par
    l'application (qui détient la clé). `forcer` sert à la recette.
    """
    # L'APPELANT PASSE AVANT L'ENVIRONNEMENT, l'environnement avant le défaut.
    # `forcer` sert la recette ; `QUALIF_MOTEUR` sert l'exploitant, qui peut
    # ainsi basculer sans redéployer une ligne de code.
    voulu = forcer if forcer in MOTEURS else (
        MOTEUR_VOULU if MOTEUR_VOULU in MOTEURS else None)

    if voulu in (None, "sdk") and sdk_importable() and executable_present():
        def _repondre(prompt, systeme_prompt):
            ok, texte = _par_sdk(prompt, systeme_prompt)
            if ok or secours is None or voulu == "sdk":
                return ok, texte
            # LE SDK A ÉCHOUÉ EN COURS DE ROUTE. Le repli est le même
            # modèle par un autre chemin, jamais un autre fournisseur.
            return secours(prompt, systeme_prompt)
        return _repondre, "sdk"

    if voulu in (None, "api") and secours is not None:
        return secours, "api"

    def _rien(prompt, systeme_prompt):
        return False, "aucun_moteur"
    return _rien, "aucun"


def etat():
    """Ce que l'écran affiche pour dire par quoi il sera servi.

    LE MOTEUR RETENU EST CALCULÉ COMME `repondeur()` LE CALCULE, et non
    décrit à côté. Un écran qui annoncerait « SDK » pendant que l'API sert
    serait pire qu'un écran muet : il ferait chercher un défaut là où il
    n'y en a pas.
    """
    sdk = sdk_importable()
    chemin = chemin_cli()
    possible = bool(sdk and chemin)

    if MOTEUR_VOULU == "sdk":
        retenu = "sdk" if possible else "aucun"
    elif MOTEUR_VOULU == "api":
        retenu = "api"
    else:
        retenu = "sdk" if possible else "api"

    return {
        "version": VERSION,
        "modele": MODELE,
        "sdk_installe": sdk,
        "executable_claude_code": bool(chemin),
        "chemin_cli": chemin,
        "moteur_voulu": MOTEUR_VOULU,
        "moteur_retenu": retenu,
        "moteur_texte": MOTEUR_TEXTE[retenu],
        "tours_max": TOURS_MAX,
        "outils_autorises": list(OUTILS_AUTORISES),
        "outils_interdits": list(OUTILS_INTERDITS),
        "sans_outils": not OUTILS_AUTORISES,
    }


def _verifier():
    assert OUTILS_AUTORISES == [], \
        "le moteur de qualification ne prend AUCUN outil"
    for interdit in ("Read", "Write", "Edit", "Bash"):
        assert interdit in OUTILS_INTERDITS, \
            "%s doit être refusé nommément" % interdit
        assert interdit not in OUTILS_AUTORISES
    assert TOURS_MAX == 1, "un seul tour"
    assert set(MOTEUR_TEXTE) == set(MOTEURS) | {"aucun"}
    assert MODELE.strip(), "aucun modèle"
    assert MOTEUR_VOULU in ("auto",) + MOTEURS, (
        "QUALIF_MOTEUR vaut « %s » : les seules valeurs sont auto, sdk, api"
        % MOTEUR_VOULU)


_verifier()
