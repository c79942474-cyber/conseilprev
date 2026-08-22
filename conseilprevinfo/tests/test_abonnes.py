"""LES ABONNÉS ET LE BULLETIN — ce qu'un site n'a pas le droit de laisser fuir.

Une liste d'abonnés à une veille cyber industrielle est une donnée
d'exposition : savoir qu'un industriel suit un automaticien précis renseigne
sur son parc. Ces contrôles gardent cinq règles :

  1. AUCUN MOT DE PASSE N'EST CONSERVÉ, ni en clair ni de façon réversible.
  2. LE FORMULAIRE N'EST PAS UN ANNUAIRE. Ni l'inscription ni la connexion ne
     doivent laisser deviner qu'une adresse est déjà abonnée.
  3. LE SECRET NE SORT JAMAIS. Aucune route, même réservée à l'intéressé, ne
     rend le sel ni le dérivé.
  4. L'EFFACEMENT EST RÉEL. Un « compte supprimé » qui resterait en mémoire
     serait un mensonge tenu par le code.
  5. LE BULLETIN SAIT SE TAIRE. Une lettre hebdomadaire qui se complète les
     semaines creuses n'apprend plus rien de sa longueur.
"""
import os
import sys
from datetime import date

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import pytest  # noqa: E402

import abonnes as AB  # noqa: E402
import bulletin as BUL  # noqa: E402
import veille as V  # noqa: E402

MDP = "une phrase entiere vaut mieux"


@pytest.fixture(autouse=True)
def _registre_propre():
    """Chaque contrôle part d'un registre vide : un compte laissé par le
    précédent ferait passer un test au vert pour la mauvaise raison."""
    AB._COMPTES.clear()
    AB._SESSIONS.clear()
    yield
    AB._COMPTES.clear()
    AB._SESSIONS.clear()


def _fiche(**kw):
    base = {
        "id": "essai-fiche", "titre": "Titre", "chapeau": "Chapeau.",
        "lecture": "L" * 100, "lecture_nature": "regle",
        "portee": "P" * 80, "incertitude": "I" * 60,
        "sujet": "cyber_industriel", "date_fait": "2026-08-20",
        "source_cle": "cisa_kev", "source_url": "https://www.cisa.gov/x",
        "statut": "verifiee_source_primaire", "impact": "structurant",
        "horizon": "constate",
    }
    base.update(kw)
    n = V.normaliser(base)
    assert n["ok"], n.get("fautes")
    return n["fiche"]


# ── 1. Aucun mot de passe conservé ────────────────────────────────────────

def test_le_mot_de_passe_n_est_nulle_part_dans_le_registre():
    AB.creer("jean@exemple.fr", MDP)
    brut = repr(AB._COMPTES)
    assert MDP not in brut
    assert MDP.encode() not in AB._COMPTES["jean@exemple.fr"]["derive"]


def test_deux_comptes_de_meme_mot_de_passe_ont_des_derives_differents():
    """Sans sel par compte, une seule table pré-calculée ouvrirait les deux."""
    AB.creer("a@exemple.fr", MDP)
    AB.creer("b@exemple.fr", MDP)
    assert (AB._COMPTES["a@exemple.fr"]["derive"]
            != AB._COMPTES["b@exemple.fr"]["derive"])


def test_le_cout_de_derivation_ne_descend_pas_sous_le_seuil():
    assert AB._SCRYPT["n"] >= 2 ** 14


def test_un_mot_de_passe_court_est_refuse():
    """La longueur est la seule contrainte qui fasse un travail réel : les
    règles de composition produisent « Motdepasse1! »."""
    r = AB.creer("jean@exemple.fr", "court1!")
    assert not r["ok"] and r["erreur"] == "motdepasse_court"


# ── 2. Le formulaire n'est pas un annuaire ────────────────────────────────

def test_l_inscription_ne_revele_pas_qu_une_adresse_est_deja_prise():
    AB.creer("jean@exemple.fr", MDP)
    r = AB.creer("jean@exemple.fr", MDP)
    assert r["ok"] is True
    assert r["message"] == AB.creer("neuf@exemple.fr", MDP)["message"]


def test_une_seconde_inscription_n_ecrase_pas_le_compte():
    """Le silence protège l'existant : sinon n'importe qui reprendrait un
    compte en le « recréant »."""
    AB.creer("jean@exemple.fr", MDP)
    derive = AB._COMPTES["jean@exemple.fr"]["derive"]
    AB.creer("jean@exemple.fr", "un tout autre mot de passe")
    assert AB._COMPTES["jean@exemple.fr"]["derive"] == derive
    assert AB.connecter("jean@exemple.fr", MDP)["ok"]


def test_la_connexion_rend_le_meme_message_pour_compte_absent_ou_mauvais_mdp():
    """« Mot de passe incorrect » distinguerait un compte connu d'un compte
    inconnu, et transformerait le formulaire en annuaire."""
    AB.creer("jean@exemple.fr", MDP)
    a = AB.connecter("jean@exemple.fr", "mauvais mot de passe ici")
    b = AB.connecter("personne@exemple.fr", "mauvais mot de passe ici")
    assert a["message"] == b["message"]
    assert a["erreur"] == b["erreur"] == "identifiants"


# ── 3. Le secret ne sort jamais ───────────────────────────────────────────

def test_aucune_vue_publique_ne_porte_le_sel_ni_le_derive():
    AB.creer("jean@exemple.fr", MDP)
    pub = AB._public(AB._COMPTES["jean@exemple.fr"])
    assert "sel" not in pub and "derive" not in pub
    assert set(pub) == {"email", "sujets", "seuil", "seuil_nom",
                        "dernier_bulletin"}


def test_la_connexion_ne_rend_que_la_vue_publique():
    AB.creer("jean@exemple.fr", MDP)
    r = AB.connecter("jean@exemple.fr", MDP)
    assert r["ok"] and "sel" not in r["compte"] and "derive" not in r["compte"]


def test_le_module_ne_declare_aucun_envoi_tant_qu_il_n_en_fait_pas():
    """Écrit comme une DÉCLARATION et non comme un oubli : toute
    l'application lit cette constante avant de parler d'envoi."""
    s = AB.sante()
    assert s["envoi_raccorde"] is False
    assert "prestataire" in s["pourquoi_pas_d_envoi"].lower()


# ── 4. L'effacement est réel ──────────────────────────────────────────────

def test_effacer_un_compte_l_ote_du_registre_et_ferme_ses_sessions():
    AB.creer("jean@exemple.fr", MDP)
    j = AB.connecter("jean@exemple.fr", MDP)["jeton"]
    assert AB.oublier(j)["ok"]
    assert "jean@exemple.fr" not in AB._COMPTES
    assert AB.compte_de(j) is None
    assert not AB.connecter("jean@exemple.fr", MDP)["ok"]


def test_un_jeton_expire_n_ouvre_plus_rien():
    AB.creer("jean@exemple.fr", MDP)
    j = AB.connecter("jean@exemple.fr", MDP)["jeton"]
    AB._SESSIONS[j]["expire"] = 0
    assert AB.compte_de(j) is None
    assert j not in AB._SESSIONS, "la session périmée doit être purgée"


def test_la_deconnexion_revoque_le_jeton():
    AB.creer("jean@exemple.fr", MDP)
    j = AB.connecter("jean@exemple.fr", MDP)["jeton"]
    AB.deconnecter(j)
    assert AB.compte_de(j) is None


def test_un_reglage_sans_jeton_ne_passe_pas():
    assert AB.regler("", sujets=["ia"])["erreur"] == "non_connecte"
    assert AB.oublier("jeton-invente")["erreur"] == "non_connecte"


def test_un_sujet_inconnu_est_refuse_a_l_inscription_et_au_reglage():
    assert AB.creer("j@exemple.fr", MDP, sujets=["politique"])["erreur"] \
        == "sujet_inconnu"
    AB.creer("j@exemple.fr", MDP)
    j = AB.connecter("j@exemple.fr", MDP)["jeton"]
    assert AB.regler(j, sujets=["politique"])["erreur"] == "sujet_inconnu"


def test_l_adresse_est_normalisee_pour_ne_pas_ouvrir_deux_comptes():
    AB.creer("Jean@Exemple.FR ", MDP)
    assert "jean@exemple.fr" in AB._COMPTES
    assert AB.connecter("jean@exemple.fr", MDP)["ok"]


# ── 5. Le bulletin sait se taire ──────────────────────────────────────────

def _compte(sujets=("cyber_industriel",), seuil="structurant"):
    return {"email": "jean@exemple.fr", "sujets": list(sujets),
            "seuil": seuil}


def test_un_bulletin_sans_matiere_reste_vide_et_le_dit():
    """C'est le contrôle central : une lettre qui se complète les semaines
    creuses apprend au lecteur que sa longueur ne signifie rien."""
    b = BUL.composer([], _compte(), fin=date(2026, 8, 22))
    assert b["vide"] is True and b["fiches"] == []
    assert "vide" in b["entree"] and "n'a pas été complété" in b["entree"]
    assert "rien à signaler" in b["objet"].lower()


def test_un_bulletin_vide_ne_va_pas_chercher_la_semaine_d_avant():
    vieille = _fiche(id="essai-vieille", date_fait="2026-01-01")
    b = BUL.composer([vieille], _compte(), fin=date(2026, 8, 22))
    assert b["vide"] is True, b["fiches"]


def test_le_seuil_de_l_abonne_est_respecte_sans_elargissement():
    """Quelqu'un qui n'a demandé que les ruptures ne reçoit pas « aussi deux
    ou trois choses intéressantes »."""
    r = _fiche(id="essai-rup", impact="rupture")
    s = _fiche(id="essai-str", impact="structurant")
    b = BUL.composer([r, s], _compte(seuil="rupture"), fin=date(2026, 8, 22))
    assert [f["id"] for f in b["fiches"]] == ["essai-rup"]


def test_les_sujets_non_suivis_n_entrent_pas():
    a = _fiche(id="essai-cyb", sujet="cyber_industriel")
    d = _fiche(id="essai-dc", sujet="datacenter")
    b = BUL.composer([a, d], _compte(sujets=["cyber_industriel"]),
                     fin=date(2026, 8, 22))
    assert [f["id"] for f in b["fiches"]] == ["essai-cyb"]


def test_une_fiche_en_reserve_n_arrive_jamais_par_courriel():
    """La porte éditoriale ne se contourne pas davantage par le bulletin que
    par les filtres — et ici la fuite sortirait du site."""
    cachee = dict(_fiche(id="essai-cac"), statut="redigee_par_ia",
                  lecture_nature="modele")
    b = BUL.composer([cachee], _compte(), fin=date(2026, 8, 22))
    assert b["vide"] is True


def test_la_coupe_du_bulletin_est_annoncee():
    fs = [_fiche(id="essai-%02d" % i) for i in range(BUL.MAXI_FICHES + 5)]
    b = BUL.composer(fs, _compte(), fin=date(2026, 8, 22))
    assert b["n_servies"] == BUL.MAXI_FICHES and b["coupe"] == 5
    assert "5 fiche(s) de plus" in b["coupe_dit"]
    assert b["coupe_dit"] in BUL.texte(b)


def test_le_bulletin_ne_redige_aucune_phrase_d_analyse():
    """Il reprend les textes du site : un texte rédigé pour l'envoi
    divergerait de la fiche, et c'est la version reçue qui ferait foi."""
    f = _fiche(id="essai-a")
    b = BUL.composer([f], _compte(), fin=date(2026, 8, 22))
    assert b["fiches"][0]["chapeau"] == f["chapeau"]
    assert f["lecture"].startswith(b["fiches"][0]["lecture"][:80])
    assert BUL.sante()["phrases_redigees_pour_l_envoi"] == 0
    assert BUL.sante()["modeles_de_langage"] == 0


def test_une_piste_sans_ses_fiches_n_est_pas_jointe():
    """Une piste déclenchée par des fiches que l'abonné ne reçoit pas lui
    arriverait sans ce qui la fonde — c'est-à-dire comme un avis."""
    dc = [_fiche(id="essai-d%02d" % i, sujet="datacenter", editeur="Siemens")
          for i in range(4)]
    b = BUL.composer(dc, _compte(sujets=["cyber_industriel"]),
                     fin=date(2026, 8, 22))
    assert b["pistes"] == []


def test_deux_compositions_identiques_rendent_le_meme_texte():
    fs = [_fiche(id="essai-%02d" % i) for i in range(3)]
    a = BUL.composer(fs, _compte(), fin=date(2026, 8, 22))
    c = BUL.composer(fs, _compte(), fin=date(2026, 8, 22))
    assert BUL.texte(a) == BUL.texte(c)


def test_le_bulletin_n_est_jamais_marque_comme_envoye():
    b = BUL.composer([_fiche()], _compte(), fin=date(2026, 8, 22))
    assert b["envoye"] is False


def test_l_objet_annonce_un_compte_verifiable_et_non_un_superlatif():
    """« L'essentiel de la semaine » ne se vérifie pas ; « 3 faits, dont 1
    rupture » se vérifie en ouvrant."""
    fs = [_fiche(id="essai-r", impact="rupture"),
          _fiche(id="essai-s", impact="structurant")]
    o = BUL.composer(fs, _compte(), fin=date(2026, 8, 22))["objet"]
    assert "2 fait(s)" in o and "1 rupture(s)" in o
    for creux in ("essentiel", "incontournable", "à ne pas manquer"):
        assert creux not in o.lower()
