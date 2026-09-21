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


def executable_present():
    """Le SDK a besoin de l'exécutable Claude Code ; est-il là ?

    Mesuré, pas supposé : sur Render, l'image Python n'en contient pas, et
    une promesse de SDK qui tombe au premier appel vaut moins qu'un repli
    annoncé.
    """
    import shutil
    if shutil.which("claude"):
        return True
    for chemin in (os.path.expanduser("~/.npm-global/bin/claude"),
                   "/usr/local/bin/claude",
                   os.path.expanduser("~/.local/bin/claude")):
        if os.path.exists(chemin):
            return True
    return False


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
    voulu = forcer if forcer in MOTEURS else None

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
    """Ce que l'écran affiche pour dire par quoi il sera servi."""
    sdk = sdk_importable()
    cli = executable_present()
    retenu = "sdk" if (sdk and cli) else "api"
    return {
        "version": VERSION,
        "modele": MODELE,
        "sdk_installe": sdk,
        "executable_claude_code": cli,
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


_verifier()
