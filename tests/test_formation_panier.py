# -*- coding: utf-8 -*-
"""Réserver de une à quatre formations d'un geste, et choisir laquelle est offerte.

CE QUI A CHANGÉ, ET POURQUOI CE N'EST PAS UN CONFORT. La gratuité tombait sur la
PREMIÈRE séance réservée, quelle qu'elle soit : un client qui voulait la
gouvernance agentique offerte devait la réserver EN PREMIER — et l'apprendre
après coup. Le panier rend ce choix explicite, et ces règles le mesurent : la
séance à zéro doit être CELLE QU'ON A DÉSIGNÉE, pas la première de la liste.

LE POINT DE SÉCURITÉ, ET IL EST LE PLUS IMPORTANT DE CE FICHIER. Le client
envoie désormais une clé « gratuit ». Elle désigne un SUJET, jamais un prix —
mais la frontière ne tient que si le serveur la garde : une règle poste donc la
demande de gratuité pour un client qui a DÉJÀ consommé la sienne, et exige que
tout soit facturé. Sans ce témoin, la relaxation de la règle « aucune clé de
prix dans le corps posté » serait une porte ouverte plutôt qu'une précision.

LES SEPT JOURS SE MESURENT À LA BORNE, PAS AU MILIEU. « Moins de sept jours
avant » est ce qui est dû : à exactement sept jours l'annulation passe encore,
à six elle est refusée. Une règle qui n'éprouverait que J-30 et J-1 serait verte
sur un délai de trois jours comme sur un délai de trente.

CE QUE L'ANNULATION NE FAIT PAS, ET C'EST DÉLIBÉRÉ. Elle n'est pas atteignable
en GET. Le lien part par courriel : un anti-virus qui inspecte les liens, un
client de messagerie qui précharge, un moteur qui indexe — tous le visitent sans
que personne n'ait cliqué. Une annulation déclenchée par une simple visite est
un piège posé à son propre client.
"""
import datetime
import io
import os
import re

import pytest

import app as A
import formations_ia as F


RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = io.open(os.path.join(RACINE, "formation.html"), encoding="utf-8").read()

SIRET_A = "910000000"
SIRET_B = "910000001"
TOUS = [s["cle"] for s in F.SUJETS]


def _purge():
    conn = A.registre_get_db(); cur = conn.cursor()
    try:
        A._formation_ia_table(cur, conn)
        cur.execute("DELETE FROM formation_ia_resa")
        conn.commit()
    except Exception:
        pass
    try: conn.close()
    except Exception: pass


@pytest.fixture
def client():
    _purge()
    c = A.app.test_client()
    yield c
    _purge()


def _creneaux():
    return [c["date"] for c in F.creneaux(datetime.datetime.utcnow().date())]


def _poster(client, paires, gratuit=None, siret=SIRET_A, **kw):
    corps = {
        "seances": [{"sujet": s, "creneau": d} for s, d in paires],
        "nom": "Durand", "prenom": "Alex", "email": kw.get("email", "a@ex.fr"),
        "entreprise": "ESSAI SAS", "siret": siret,
        "telephone": "+33 6 12 34 56 78", "lieu": "12 rue d'Essai, Paris",
    }
    if gratuit:
        corps["gratuit"] = gratuit
    corps.update({k: v for k, v in kw.items() if k != "email"})
    return client.post("/api/formation/inscription", json=corps)


def _lignes():
    conn = A.registre_get_db(); cur = conn.cursor()
    A._formation_ia_table(cur, conn)
    cur.execute("SELECT * FROM formation_ia_resa ORDER BY id ASC")
    out = [dict(r) for r in cur.fetchall()]
    try: conn.close()
    except Exception: pass
    return out


# ══════════════════════════════════════════════════════════════════════════
#  LE DEVIS — le moteur, hors ligne
# ══════════════════════════════════════════════════════════════════════════
def test_de_une_a_quatre_formations_en_un_seul_devis():
    for n in (1, 2, 3, 4):
        d = F.devis(TOUS[:n])
        assert d["ok"], d
        assert d["nb"] == n and len(d["lignes"]) == n


def test_une_cinquieme_formation_est_refusee_et_le_DIT():
    """Le refus muet ferait chercher une panne. Et le plafond n'est pas un
    nombre rond : c'est le nombre de sujets."""
    d = F.devis(TOUS + ["gouvernance-ia"])
    assert not d["ok"] and d["error"] == "trop_de_seances"
    assert "quatre" in d["message"].lower()
    assert F.MAX_SEANCES == F.NB_SUJETS


def test_la_gratuite_porte_sur_la_seance_CHOISIE_et_non_sur_la_PREMIERE():
    """LE CŒUR DE CE FICHIER. Avant, la première réservée était offerte : cette
    règle serait verte par accident si l'on désignait la première. On désigne
    donc la TROISIÈME, et l'on exige que ce soit ELLE qui soit à zéro."""
    d = F.devis(TOUS[:3], gratuit=TOUS[2])
    offertes = [l["cle"] for l in d["lignes"] if l["gratuit"]]
    assert offertes == [TOUS[2]], offertes
    assert d["lignes"][0]["ht_cents"] == F.TARIF_HT_CENTS
    assert d["ht_cents"] == 2 * F.TARIF_HT_CENTS


def test_sans_choix_la_PREMIERE_est_offerte_et_jamais_AUCUNE():
    """Laisser la gratuité tomber faute d'avoir coché ferait payer une séance
    annoncée offerte — le contraire de la règle publiée."""
    d = F.devis(TOUS[:3])
    assert d["gratuite"] == TOUS[0]
    assert sum(1 for l in d["lignes"] if l["gratuit"]) == 1
    assert d["message"] and "offerte" in d["message"]


def test_une_gratuite_HORS_panier_est_refusee():
    """Une remise sur une séance qu'on ne réserve pas serait introuvable à
    l'écran — et le total, inexplicable."""
    d = F.devis(["gouvernance-ia"], gratuit="securite-ia")
    assert not d["ok"] and d["error"] == "gratuite_hors_panier"


def test_un_client_qui_a_DEJA_consomme_sa_gratuite_paie_tout():
    d = F.devis(TOUS[:2], gratuit=TOUS[1], gratuite_disponible=False)
    assert d["ok"] and d["gratuite"] is None
    assert all(not l["gratuit"] for l in d["lignes"])
    assert d["ht_cents"] == 2 * F.TARIF_HT_CENTS
    assert "déjà" in (d["message"] or "")


def test_le_meme_sujet_deux_fois_est_refuse():
    d = F.devis(["securite-ia", "securite-ia"])
    assert not d["ok"] and d["error"] == "sujet_en_double"


def test_le_total_est_la_SOMME_des_lignes_et_non_un_calcul_a_part():
    """Deux calculs du même montant divergent le jour où l'un des deux change ;
    c'est celui qui est affiché qui a tort, et on ne le sait qu'à la facture."""
    for gr in (None, TOUS[1], TOUS[3]):
        d = F.devis(TOUS, gratuit=gr)
        assert d["ht_cents"] == sum(l["ht_cents"] for l in d["lignes"]), d
        assert d["nb_payantes"] == sum(1 for l in d["lignes"] if not l["gratuit"])


# ══════════════════════════════════════════════════════════════════════════
#  LES SEPT JOURS — mesurés à la borne
# ══════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("reste,possible", [
    (30, True), (8, True), (7, True), (6, False), (1, False), (0, False),
])
def test_l_annulation_est_libre_a_SEPT_jours_et_due_a_SIX(reste, possible):
    """« Moins de sept jours avant » est ce qui est dû : à SEPT, on passe
    encore. La borne se mesure des deux côtés, sans quoi la règle serait verte
    sur un délai de trois jours comme sur un délai de trente."""
    jour = datetime.date(2026, 10, 20)
    ok, motif = F.annulable(jour, jour - datetime.timedelta(days=reste))
    assert ok is possible, (reste, motif)
    if not possible:
        assert str(F.ANNULATION_JOURS) in motif or "eu lieu" in motif


def test_une_seance_PASSEE_ne_s_annule_pas():
    ok, motif = F.annulable("2026-01-01", "2026-02-01")
    assert not ok and "eu lieu" in motif


def test_la_regle_d_annulation_DIT_son_propre_delai():
    """Sept jours écrits dans le code et « une semaine » dans le texte
    finissent par diverger — et c'est le texte que le client a lu qui engage."""
    r = F.regle_annulation()
    assert r["jours"] == F.ANNULATION_JOURS
    for champ in ("payante", "infobulle"):
        assert str(F.ANNULATION_JOURS) in r[champ], champ
    assert "factur" in r["payante"]


# ══════════════════════════════════════════════════════════════════════════
#  LA ROUTE — ce que la base garde vraiment
# ══════════════════════════════════════════════════════════════════════════
def test_trois_seances_en_un_envoi_font_TROIS_reservations(client):
    cre = _creneaux()[:3]
    r = _poster(client, list(zip(TOUS[:3], cre)), gratuit=TOUS[2])
    assert r.status_code == 200 and r.get_json()["ok"], r.get_json()
    lg = _lignes()
    assert len(lg) == 3
    assert len({x["commande"] for x in lg}) == 1, "les trois lignes ne sont pas groupées"
    assert sorted(x["date_creneau"] for x in lg) == sorted(cre)


def test_la_gratuite_CHOISIE_est_celle_qui_vaut_zero_EN_BASE(client):
    """L'écran peut afficher ce qu'il veut : ce qui compte est la ligne écrite."""
    cre = _creneaux()[:3]
    _poster(client, list(zip(TOUS[:3], cre)), gratuit=TOUS[2])
    zero = [x["sujet"] for x in _lignes() if int(x["montant_cents"] or 0) == 0]
    assert zero == [TOUS[2]], zero


def test_un_client_DEJA_VENU_ne_retrouve_pas_sa_gratuite_en_la_DEMANDANT(client):
    """LE TÉMOIN DE SÉCURITÉ. Le client envoie « gratuit » : si le serveur le
    croyait, il suffirait de repasser commande pour ne jamais payer."""
    cre = _creneaux()
    _poster(client, [(TOUS[0], cre[0])], gratuit=TOUS[0])
    r = _poster(client, [(TOUS[1], cre[1])], gratuit=TOUS[1])
    assert r.status_code == 200, r.get_json()
    j = r.get_json()
    assert j["devis"]["nb_payantes"] == 1, j["devis"]
    assert j["devis"]["ht_cents"] == F.TARIF_HT_CENTS
    seconde = [x for x in _lignes() if x["sujet"] == TOUS[1]][0]
    assert int(seconde["montant_cents"]) == F.TARIF_HT_CENTS
    assert int(seconde["gratuit"] or 0) == 0


def test_deux_formations_a_la_MEME_date_sont_refusees(client):
    cre = _creneaux()[0]
    r = _poster(client, [(TOUS[0], cre), (TOUS[1], cre)])
    assert r.status_code == 400
    assert "même date" in r.get_json()["error"] or "meme date" in r.get_json()["error"]
    assert _lignes() == [], "un panier refusé a quand même écrit"


def test_une_date_hors_calendrier_est_refusee(client):
    r = _poster(client, [(TOUS[0], "2019-01-01")])
    assert r.status_code == 400 and not _lignes()


def test_un_panier_dont_UNE_date_est_prise_n_ecrit_RIEN(client):
    """L'ATOMICITÉ. Écrire deux séances puis refuser la troisième laisserait un
    panier à moitié réservé — et le client ne saurait pas laquelle est prise."""
    cre = _creneaux()[:3]
    _poster(client, [(TOUS[0], cre[0])], siret=SIRET_B, email="b@ex.fr")
    avant = len(_lignes())
    r = _poster(client, [(TOUS[1], cre[1]), (TOUS[2], cre[0])])
    assert r.status_code == 409, r.get_json()
    assert len(_lignes()) == avant, "le panier refusé a écrit une ligne quand même"


def test_l_ANCIEN_envoi_un_sujet_un_creneau_marche_encore(client):
    """La route promet d'accepter l'ancien envoi ; lui rendre une réponse
    amputée le casserait quand même."""
    r = client.post("/api/formation/inscription", json={
        "sujet": TOUS[0], "creneau": _creneaux()[0], "nom": "Durand",
        "prenom": "Alex", "email": "a@ex.fr", "entreprise": "ESSAI SAS",
        "siret": SIRET_A, "telephone": "+33 6 12 34 56 78",
        "lieu": "12 rue d'Essai, Paris"})
    assert r.status_code == 200
    j = r.get_json()
    for ancienne in ("gratuit", "montant_cents", "ttc_cents", "sujet", "creneau"):
        assert ancienne in j, "la clé « %s » a disparu de la réponse" % ancienne
    assert j["gratuit"] is True and j["montant_cents"] == 0
    assert len(_lignes()) == 1


def test_chaque_reservation_porte_un_jeton_UNIQUE_et_long(client):
    """Le jeton est la SEULE preuve qu'un client sans compte possède sur sa
    réservation. Court ou prévisible, il se teste en quelques minutes."""
    cre = _creneaux()[:3]
    _poster(client, list(zip(TOUS[:3], cre)))
    jetons = [x["jeton"] for x in _lignes()]
    assert all(j and len(j) >= 24 for j in jetons), jetons
    assert len(set(jetons)) == 3, "deux séances partagent un jeton"


# ══════════════════════════════════════════════════════════════════════════
#  L'ANNULATION
# ══════════════════════════════════════════════════════════════════════════
def _jeton_de(sujet):
    return [x["jeton"] for x in _lignes() if x["sujet"] == sujet][0]


def test_annuler_a_plus_de_sept_jours_LIBERE_le_creneau(client):
    cre = _creneaux()[0]
    _poster(client, [(TOUS[0], cre)])
    pris = [c for c in client.get("/api/formation/referentiel").get_json()["creneaux"]
            if c["date"] == cre][0]
    assert not pris["libre"], "le créneau n'a jamais été pris"
    r = client.post("/api/formation/annulation", json={"jeton": _jeton_de(TOUS[0])})
    assert r.status_code == 200 and r.get_json()["ok"], r.get_json()
    apres = [c for c in client.get("/api/formation/referentiel").get_json()["creneaux"]
             if c["date"] == cre][0]
    assert apres["libre"], "le créneau annulé reste bloqué"


def test_annuler_a_MOINS_de_sept_jours_est_REFUSE_et_dit_que_c_est_du(client):
    """On ne peut pas réserver à moins de sept jours — le calendrier ne le
    propose pas. La ligne est donc posée directement en base, comme une
    réservation prise il y a trois semaines pour après-demain."""
    cre = _creneaux()[0]
    _poster(client, [(TOUS[0], cre)])
    proche = (datetime.datetime.utcnow().date()
              + datetime.timedelta(days=3)).isoformat()
    conn = A.registre_get_db(); cur = conn.cursor()
    cur.execute(A.registre_sql("UPDATE formation_ia_resa SET date_creneau=%s, gratuit=0, montant_cents=80000",
                               "UPDATE formation_ia_resa SET date_creneau=?, gratuit=0, montant_cents=80000"),
                (proche,))
    conn.commit()
    try: conn.close()
    except Exception: pass
    r = client.post("/api/formation/annulation", json={"jeton": _jeton_de(TOUS[0])})
    assert r.status_code == 409, r.get_json()
    j = r.get_json()
    assert j.get("delai_depasse") and j.get("jours") == F.ANNULATION_JOURS
    assert "factur" in j["message"]
    assert _lignes()[0]["statut"] != "annulee", "refusée mais annulée quand même"


def test_le_jeton_d_un_AUTRE_n_annule_pas_ma_seance(client):
    cre = _creneaux()[:2]
    _poster(client, [(TOUS[0], cre[0])])
    _poster(client, [(TOUS[1], cre[1])], siret=SIRET_B, email="b@ex.fr")
    r = client.post("/api/formation/annulation", json={"jeton": _jeton_de(TOUS[1])})
    assert r.status_code == 200
    etats = {x["sujet"]: x["statut"] for x in _lignes()}
    assert etats[TOUS[1]] == "annulee"
    assert etats[TOUS[0]] != "annulee", "l'annulation a débordé sur l'autre client"


def test_un_jeton_inconnu_ne_dit_PAS_s_il_a_existe(client):
    """Distinguer « inconnu » de « déjà servi » donnerait à qui essaie des
    jetons au hasard un signal sur ceux qui existent."""
    r = client.post("/api/formation/annulation", json={"jeton": "z" * 40})
    assert r.status_code == 404
    assert "deja" not in r.get_json()["error"].lower()


def test_recliquer_sur_le_lien_ne_ressemble_pas_a_une_panne(client):
    _poster(client, [(TOUS[0], _creneaux()[0])])
    jet = _jeton_de(TOUS[0])
    client.post("/api/formation/annulation", json={"jeton": jet})
    r = client.post("/api/formation/annulation", json={"jeton": jet})
    assert r.status_code == 200 and r.get_json()["ok"] and r.get_json()["deja"]


def test_l_annulation_n_est_PAS_atteignable_en_GET(client):
    """LE PIÈGE DU LIEN DE COURRIEL. Un anti-virus qui inspecte les liens, un
    client de messagerie qui précharge : tous visitent l'adresse sans que
    personne n'ait cliqué. Une annulation déclenchée par une visite est un
    piège posé à son propre client."""
    _poster(client, [(TOUS[0], _creneaux()[0])])
    jet = _jeton_de(TOUS[0])
    # LA MESURE PORTE SUR L'EFFET, PAS SUR LE CODE DE RETOUR. Un 404 et un 405
    # disent tous deux « pas par ici » ; ce qui compte est que la séance soit
    # toujours là après la visite.
    r = client.get("/api/formation/annulation?jeton=" + jet)
    assert r.status_code in (404, 405), r.status_code
    assert _lignes()[0]["statut"] != "annulee", (
        "une simple visite de l'adresse a annulé la séance")
    # Et le lien du courriel mène à la PAGE, pas à l'écriture. La page est
    # servie avec un en-tête de navigateur : le garde anti-robot du site refuse
    # un client sans agent utilisateur, et mesurer SON refus ne dirait rien de
    # ce qu'on veut ici.
    NAVIGATEUR = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                                " (KHTML, like Gecko) Chrome/120 Safari/537.36",
                  "Accept": "text/html,application/xhtml+xml",
                  "Accept-Language": "fr-FR"}
    assert client.get("/formation?annuler=" + jet,
                      headers=NAVIGATEUR).status_code == 200
    assert _lignes()[0]["statut"] != "annulee", (
        "ouvrir la page d'annulation annule sans qu'on ait cliqué")


# ══════════════════════════════════════════════════════════════════════════
#  LA PAGE
# ══════════════════════════════════════════════════════════════════════════
def test_la_page_envoie_les_SEANCES_avec_leur_date():
    i = PAGE.index("/api/formation/inscription")
    corps = PAGE[i:i + 1400]
    assert "seances:" in corps
    assert "sujet:k" in corps.replace(" ", "") or "sujet: k" in corps
    assert "creneau:" in corps


def test_la_page_ne_CALCULE_pas_le_total_elle_meme():
    """Elle ne sait pas si ce client a déjà consommé sa séance offerte — cela
    se lit en base. Un total calculé ici afficherait 1 600 € à qui en doit
    2 400, et l'écart se découvrirait à la caisse."""
    i = PAGE.index("function majRecap(")
    corps = PAGE[i:PAGE.index("\n  }", i)]
    assert "state.devis" in corps, "le récapitulatif n'affiche pas le devis du serveur"
    for ecrit in ("80000", "* 800", "TARIF_HT"):
        assert ecrit not in corps, "le total est recomposé dans la page (« %s »)" % ecrit
    assert "/api/formation/devis" in PAGE, "la page ne demande aucun devis au serveur"


def test_l_infobulle_des_sept_jours_est_LUE_et_non_recopiee():
    """Sept jours écrits dans la page et sept dans le module finissent par
    diverger — et c'est le texte affiché qui engage."""
    i = PAGE.index("function rendreAnnulation(")
    corps = PAGE[i:PAGE.index("\n  }", i)]
    assert "a.infobulle" in corps, "l'infobulle n'est pas lue du référentiel"
    assert "data-tip" in corps
    # Le délai n'est écrit NULLE PART en dur dans la page.
    assert not re.search(r"moins de (sept|7) jours", PAGE), (
        "le délai d'annulation est recopié dans la page au lieu d'être lu")


def test_le_lien_d_annulation_ne_declenche_RIEN_en_s_ouvrant():
    i = PAGE.index("function annulation(")
    corps = PAGE[i:PAGE.index("\n  })();", i)]
    assert "annul-go" in corps and "addEventListener('click'" in corps, (
        "l'annulation ne passe pas par un bouton")
    # L'appel réseau est DANS le gestionnaire de clic, jamais au chargement.
    av = corps[:corps.index("addEventListener('click'")]
    assert "/api/formation/annulation" not in av, (
        "la page appelle l'annulation avant tout clic : le premier anti-virus "
        "qui ouvre le lien annulerait la séance")


def test_sans_limite_de_participants_est_DIT():
    """Le code n'a jamais posé de plafond ; ne pas le dire laissait le client
    supposer le contraire — et n'inviter que trois personnes."""
    assert "limite de participants" in F.SUPPORT["participants"].lower()
    assert 'id="sup-part"' in PAGE


def test_le_support_dit_ce_qui_est_PERSONNALISE_et_ce_qui_ne_l_est_pas():
    """« Support personnalisé » sans dire ce qui l'est est la promesse la plus
    facile à démentir le jour de la séance."""
    natures = {e["nature"] for e in F.SUPPORT["elements"]}
    assert natures == {"standard", "personnalise"}, natures
    i = PAGE.index("function rendreSupport(")
    corps = PAGE[i:PAGE.index("\n  }", i)]
    assert "personnalise" in corps and "standard" in corps
    assert "e.nature" in corps, "la page décide seule de ce qui est personnalisé"


def test_les_etudes_de_cas_suivent_le_TYPE_de_client():
    a = F.etudes_de_cas("exploitant")
    b = F.etudes_de_cas("editeur")
    assert a["choisi"] and b["choisi"] and a["cas"] != b["cas"]
    inconnu = F.etudes_de_cas("zzz")
    assert not inconnu["choisi"] and inconnu["cas"], (
        "un profil inconnu rend une liste vide : on croirait qu'aucun cas "
        "n'est présenté")
    assert 'id="fo-profil"' in PAGE
