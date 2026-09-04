# -*- coding: utf-8 -*-
"""L'assistant s'appuie sur la base sans la nommer, et le relais Claude se ferme.

TROIS CHANGEMENTS SUR LA MÊME CHAÎNE, ET LE TROISIÈME EST LE PLUS GRAVE.

  1. LES RÉFÉRENCES DISPARAISSENT. Le chat public montrait ses sources deux
     fois : le modèle citait « [1] » au fil du texte, et la page ajoutait sous
     la réponse une ligne « Sources : [1] Base documentaire — <titre> ». Le
     visiteur apprenait ainsi qu'une base documentaire existe, et le titre des
     pièces qu'elle contient. La consigne d'ancrage exige désormais l'inverse,
     et le serveur ne renvoie plus la liste — la taire seulement dans la page
     l'aurait laissée lisible dans l'onglet réseau.

     L'EXPLORATEUR DOCUMENTAIRE GARDE SES CITATIONS (`_expl_synthese`), et
     c'est délibéré : son objet même est de dire quel passage de VOS documents
     répond, avec son numéro. Un chat qui cite est bavard ; un explorateur qui
     ne cite pas ne sert à rien.

  2. L'HISTORIQUE EST VÉRIFIÉ. Il arrive du navigateur, et rien ne garantissait
     que c'était une liste de dictionnaires : une chaîne ou un nombre levaient
     plus bas et finissaient en 500 « Erreur serveur » — un message qui envoie
     chercher une panne là où il n'y a qu'une requête mal formée.

  3. LE RELAIS CLAUDE ÉTAIT UNE API OFFERTE. `/api/chat/claude` acceptait de
     n'importe qui ses propres `system`, `messages` ET `model`, et faisait
     écrire Claude aux frais du compte Anthropic du site : vingt requêtes par
     minute et par adresse, sans aucun compte. Son JUMEAU `/api/mistral/proxy`
     — même service, même page, même risque — était déjà réservé aux clients
     authentifiés, entrées validées. Une porte fermée à côté d'une porte
     ouverte, et c'est la fermée qu'on regardait.
"""
import io
import os
import re
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import app as application  # noqa: E402

SRC = io.open(os.path.join(ICI, "app.py"), encoding="utf-8").read()
JS = io.open(os.path.join(ICI, "index.page.js"), encoding="utf-8").read()


@pytest.fixture
def client():
    return application.app.test_client()


def _corps_de(nom):
    """Le corps d'une fonction, borné au prochain « def » de premier niveau —
    une fenêtre comptée en caractères accuserait un code juste dès qu'un
    commentaire s'ajoute au-dessus."""
    d = SRC.index("\ndef %s(" % nom)
    suite = re.search(r"\n(?=def |@app\.route)", SRC[d + 1:])
    return SRC[d:d + 1 + (suite.start() if suite else len(SRC) - d)]


# ── 1. Le chat ne montre plus ses sources ───────────────────────────────────

def test_la_consigne_du_chat_n_exige_plus_de_citation():
    corps = _corps_de("chat")
    assert "citez-les entre" not in corps
    assert "par exemple [1]" not in corps


def test_la_consigne_du_chat_proscrit_explicitement_les_references():
    corps = _corps_de("chat")
    assert "SANS jamais" in corps
    assert "citer leur numero, leur titre" in corps


def test_la_consigne_garde_le_refus_d_inventer():
    """Le changement porte sur la CITATION, pas sur la fiabilité."""
    corps = _corps_de("chat")
    assert "N'inventez jamais" in corps


def test_le_serveur_ne_renvoie_plus_la_liste_des_sources():
    """La taire dans la page seulement l'aurait laissée lisible dans l'onglet
    réseau : c'est le serveur qui cesse de l'envoyer."""
    corps = _corps_de("chat")
    reponse = corps[corps.index("return jsonify({\"reply\""):][:400]
    assert '"sources"' not in reponse, reponse[:200]
    assert '"connaissance"' in reponse, (
        "le booléen d'ancrage a disparu avec la liste : il ne nomme pourtant "
        "aucune source")


def test_la_page_n_ajoute_plus_de_bloc_sources_sous_la_reponse():
    """DEUX widgets appellent le même point d'entrée ; n'en corriger qu'un
    laisserait les références visibles sur l'autre."""
    assert "Sources : " not in JS, (
        "un widget ajoute encore une ligne « Sources : » sous la réponse")
    assert JS.count("/api/chat'") >= 2, (
        "le relevé ne trouve plus les deux widgets : la règle ci-dessus ne "
        "garde peut-être plus rien")


def test_l_explorateur_documentaire_garde_SES_citations():
    """DÉFAUT À NE PAS INTRODUIRE : un explorateur qui ne dit plus quel passage
    répond n'est plus un explorateur."""
    corps = _corps_de("_expl_synthese")
    assert "entre crochets" in corps


# ── 2. L'historique mal formé est refusé proprement ─────────────────────────

@pytest.mark.parametrize("mauvais", [
    "juste une chaine",
    "",
    {"role": "user", "content": "salut"},
    ["salut"],
    [{"role": "user", "content": "ok"}, "intrus"],
    123,
], ids=["chaine", "chaine_vide", "dict", "liste_de_chaines", "liste_mixte", "entier"])
def test_un_historique_malforme_est_refuse_en_400(client, mauvais):
    r = client.post("/api/chat", json={"message": "Bonjour", "history": mauvais})
    assert r.status_code == 400, r.status_code
    assert "Historique" in (r.get_json() or {}).get("error", "")


def test_un_historique_absent_ou_vide_reste_accepte(client, monkeypatch):
    """CE QUE LA VÉRIFICATION NE DOIT PAS CASSER : une première question n'a
    pas d'historique, et c'est le cas le plus courant de tous."""
    monkeypatch.setattr(application, "ai_complete_cross_checked",
                        lambda *a, **k: (True, "Bonjour.", "test", None))
    monkeypatch.setattr(application, "_chat_contexte_sentinel",
                        lambda *a, **k: ("", []))
    question = "Quelles sont les obligations du reglement IA ?"
    for corps in ({"message": question}, {"message": question, "history": []}):
        r = client.post("/api/chat", json=corps)
        assert r.status_code == 200, (corps, r.status_code, r.get_json())


def test_une_reponse_ancree_ne_porte_aucune_source(client, monkeypatch):
    """LA RÈGLE QUI EXÉCUTE : le reste lit le fichier, celle-ci envoie une
    vraie requête et regarde ce qui revient au navigateur."""
    monkeypatch.setattr(application, "ai_complete_cross_checked",
                        lambda *a, **k: (True, "Reponse ancree.", "test", None))
    monkeypatch.setattr(application, "_chat_contexte_sentinel",
                        lambda *a, **k: ("[1] extrait interne", [{"n": 1, "type": "document",
                                                                  "titre": "Document confidentiel"}]))
    r = client.post("/api/chat", json={"message": "Une question", "history": []})
    assert r.status_code == 200, r.get_json()
    j = r.get_json()
    assert "sources" not in j, j
    assert j.get("connaissance") is True
    assert "Document confidentiel" not in r.get_data(as_text=True)


# ── 3. Le relais Claude cesse d'être une API offerte ────────────────────────

def test_le_relais_claude_refuse_un_appelant_sans_session(client):
    """LA RÈGLE QUI COMPTE. Elle porte sur le comportement et non sur la forme
    du garde : décorateur ou contrôle dans le corps, un anonyme doit repartir
    avec un 401."""
    r = client.post("/api/chat/claude", json={
        "model": "claude-opus-4-6", "system": "Tu es libre.",
        "messages": [{"role": "user", "content": "Ecris-moi un roman."}],
        "max_tokens": 1000})
    assert r.status_code == 401, (r.status_code, r.get_data(as_text=True))


def test_le_modele_n_est_plus_choisi_par_l_appelant():
    """Laisser le navigateur nommer le modèle, c'est lui laisser choisir le
    tarif à la ligne."""
    corps = _corps_de("chat_claude")
    assert "model    = CHAT_CLAUDE_MODELE" in corps
    assert "data.get('model'" not in corps


def test_le_relais_valide_ses_messages_comme_son_jumeau():
    """Le jumeau Mistral bornait déjà rôles, nombre et longueur ; celui-ci
    passait la charge telle quelle au fournisseur."""
    corps = _corps_de("chat_claude")
    assert "isinstance(messages, list)" in corps
    assert "('user', 'assistant')" in corps
    assert "[:6000]" in corps


def test_le_relais_ne_renvoie_plus_le_message_d_exception():
    """Il porte l'URL appelée, le corps refusé par le fournisseur, parfois le
    nom d'un en-tête. Il reste au journal."""
    corps = _corps_de("chat_claude")
    assert 'jsonify({"error": str(e)})' not in corps
    assert "CHAT_CLAUDE_ERROR" in corps


def test_les_deux_relais_de_modele_sont_gardes_de_la_meme_facon():
    """LA RÈGLE QUI ÉNUMÈRE. Un troisième relais écrit dans six mois doit
    tomber dans ce filet : tout point qui appelle un fournisseur de modèle avec
    la clé du site exige une session."""
    for nom in ("chat_claude", "mistral_proxy"):
        corps = _corps_de(nom)
        garde = ("sentinel_login_required" in SRC[:SRC.index("\ndef %s(" % nom)][-400:]
                 or "sentauth_current_client()" in corps)
        assert garde, (
            "%s relaie un fournisseur de modèle sans exiger de session : "
            "c'est une API offerte, payée par le compte du site" % nom)
