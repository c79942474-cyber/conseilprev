# -*- coding: utf-8 -*-
"""Les relances J-14 et J-7 des formations réservées — mesurées.

CE QUE CES RÈGLES ÉPROUVENT. Après confirmation (gratuite d'emblée, payante une
fois payée), une relance part à DEUX SEMAINES puis à UNE SEMAINE de la séance,
AU CLIENT ET À CONSEILPREV. Chacune part une seule fois. Un devis, une attente
de paiement, une séance annulée ne reçoivent rien.

COMMENT ON MESURE SANS ATTENDRE. `_formation_ia_relances` prend la date de
référence en ARGUMENT : on pose des séances à J+14, J+7, etc. par rapport à une
date fixe, et l'on regarde ce qui est dû. Pour l'envoi, on remplace l'expéditeur
de courriel par un compteur — deux destinataires par relance.
"""
import datetime

import pytest

import app as A

REF = datetime.date(2026, 10, 1)


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
def base():
    _purge()
    yield
    _purge()


def _ins(sujet, jours, statut, email="client@ex.fr"):
    """Une réservation dont la séance tombe `jours` après la date de référence."""
    d = (REF + datetime.timedelta(days=jours)).isoformat()
    conn = A.registre_get_db(); cur = conn.cursor()
    A._formation_ia_table(cur, conn)
    cur.execute(A.registre_sql(
        "INSERT INTO formation_ia_resa (sujet,date_creneau,nom,prenom,email,entreprise,lieu,statut,created_at) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        "INSERT INTO formation_ia_resa (sujet,date_creneau,nom,prenom,email,entreprise,lieu,statut,created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?)"),
        (sujet, d, "Nom", "Prenom", email, "Entreprise", "12 rue d'Essai", statut, "x"))
    conn.commit()
    try: conn.close()
    except Exception: pass


def _quand(dues):
    return sorted((x["sujet"], x["quand"]) for x in dues)


def test_les_deux_fenetres_declenchent_j14_et_j7(base):
    """À deux semaines : la relance J-14. À une semaine : la J-7."""
    _ins("gouvernance-ia", 14, "confirmee")
    _ins("securite-ia", 7, "payee")
    dues = A._formation_ia_relances(REF, envoyer=False)
    assert _quand(dues) == [("gouvernance-ia", "j14"), ("securite-ia", "j7")]


def test_hors_des_deux_fenetres_rien_ne_part(base):
    """15 jours, c'est encore trop tôt ; le jour même (0) et au-delà des deux
    semaines, rien. Les fenêtres sont (7,14] et (0,7]."""
    _ins("gouvernance-ia", 15, "confirmee")
    _ins("securite-ia", 0, "confirmee")
    _ins("gouvernance-agentique", 30, "confirmee")
    assert A._formation_ia_relances(REF, envoyer=False) == []


def test_les_bornes_basses_des_fenetres_sont_incluses(base):
    """8 jours relève encore de la J-14 (7 exclu, 14 inclus) ; 1 jour de la J-7."""
    _ins("gouvernance-ia", 8, "confirmee")
    _ins("securite-ia", 1, "payee")
    assert _quand(A._formation_ia_relances(REF, envoyer=False)) == [
        ("gouvernance-ia", "j14"), ("securite-ia", "j7")]


def test_seule_une_seance_confirmee_est_relancee(base):
    """Un devis ou une attente de paiement n'est pas une confirmation : pas de
    relance tant que le client n'a pas confirmé (ou payé)."""
    _ins("gouvernance-ia", 10, "devis")
    _ins("securite-ia", 10, "en_attente_paiement")
    _ins("gouvernance-agentique", 10, "annulee")
    assert A._formation_ia_relances(REF, envoyer=False) == []


def test_la_relance_va_au_client_ET_a_conseilprev(base, monkeypatch):
    """« au client et à moi » : chaque relance a exactement deux destinataires."""
    _ins("gouvernance-ia", 14, "confirmee", email="leclient@ex.fr")
    envoyes = []
    monkeypatch.setattr(A, "send_email_smart",
                        lambda to, *a, **k: envoyes.append(to))
    env = A._formation_ia_relances(REF, envoyer=True)
    assert len(env) == 1
    assert "leclient@ex.fr" in envoyes
    assert A.CONSEILPREV_INTERNAL_EMAIL in envoyes
    assert len(envoyes) == 2


def test_une_relance_ne_part_quune_seule_fois(base, monkeypatch):
    """La colonne qui la date fait foi : un second passage n'envoie plus rien.
    C'est ce qui rend la boucle sûre dans chaque worker."""
    _ins("securite-ia", 7, "payee")
    envoyes = []
    monkeypatch.setattr(A, "send_email_smart", lambda *a, **k: envoyes.append(1))
    A._formation_ia_relances(REF, envoyer=True)
    apres_premier = len(envoyes)
    A._formation_ia_relances(REF, envoyer=True)
    assert apres_premier == 2, "la première relance n'a pas ses deux destinataires"
    assert len(envoyes) == 2, "un second passage a renvoyé la même relance"


def test_une_relance_deja_reclamee_ne_se_reclame_pas_deux_fois(base):
    """LA GARDE ENTRE WORKERS, MESURÉE POUR ELLE-MÊME.

    La règle précédente ne pouvait pas l'atteindre : après un premier passage,
    le relevé ne propose déjà plus la relance, si bien qu'un second passage
    séquentiel n'envoie rien même SANS garde. Or la boucle tourne dans CHAQUE
    worker, et deux workers peuvent relever la même relance avant que l'un ait
    écrit. Seule la réclamation les départage — on l'éprouve donc directement :
    deux réclamations de suite, une seule doit prendre."""
    _ins("securite-ia", 7, "payee")
    conn = A.registre_get_db(); cur = conn.cursor()
    cur.execute("SELECT MAX(id) AS id FROM formation_ia_resa")
    rid = int(dict(cur.fetchone())["id"])
    premier = A._formation_ia_reclamer(cur, conn, "relance_7_at", rid, "2026-10-01")
    second = A._formation_ia_reclamer(cur, conn, "relance_7_at", rid, "2026-10-01")
    try: conn.close()
    except Exception: pass
    assert premier is True, "la première réclamation n'a pas pris"
    assert second is False, (
        "une relance déjà réclamée se réclame une seconde fois : deux workers "
        "enverraient le même rappel")


def test_les_deux_relances_partent_a_leurs_dates_respectives(base, monkeypatch):
    """La même séance reçoit la J-14, puis, une semaine plus tard, la J-7 : la
    marque de la première ne bloque pas la seconde."""
    _ins("gouvernance-ia", 14, "confirmee")
    monkeypatch.setattr(A, "send_email_smart", lambda *a, **k: None)
    e1 = A._formation_ia_relances(REF, envoyer=True)
    assert _quand(e1) == [("gouvernance-ia", "j14")]
    plus_tard = REF + datetime.timedelta(days=7)     # la séance est à J-7
    e2 = A._formation_ia_relances(plus_tard, envoyer=True)
    assert _quand(e2) == [("gouvernance-ia", "j7")]


def test_le_point_de_relance_est_reserve_a_conseilprev(base):
    """La route d'aperçu/déclenchement des relances n'est pas publique."""
    c = A.app.test_client()
    assert c.get("/api/formation/relances").status_code == 403
    assert c.post("/api/formation/relances").status_code == 403
