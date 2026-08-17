"""LE RECOUPEMENT DU REGISTRE DE VÉRIFICATION — mesuré, jamais déclaré.

CE QUI MANQUAIT. Le registre portait un champ `source` au SINGULIER : un
contrôle ne pouvait donc pas enregistrer qu'il avait été recoupé. Quand le
recoupement était fait, il finissait dans la prose du `constat` — invisible à
tout comptage, donc invérifiable. Mesuré à l'audit d'août 2026 : 27 des 40
contrôles reposaient sur le même éditeur, et 20 des 27 corrections aussi.

Vérifier une valeur avec une seule maison n'est pas un recoupement. Ces
contrôles ne l'interdisent pas — un ordre de grandeur peut légitimement
n'avoir qu'une source — mais ils exigent que le registre le DISE, et que le
compte soit calculé sur les sources plutôt qu'annoncé.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import factcheck as F


def test_chaque_controle_porte_une_source_editee():
    muets = [c["sujet"] for c in F.CONTROLES
             if not (c.get("source") or {}).get("editeur")]
    assert muets == [], "contrôles sans éditeur : %s" % muets


def test_le_compte_de_maisons_est_CALCULE_sur_les_sources():
    """Un compte écrit à la main cesse d'être vrai au premier ajout."""
    c = dict(F.CONTROLES[0])
    avant = F.recoupement(c)["nombre"]
    c["corroborations"] = [{"editeur": "Une Autre Maison", "titre": "x", "url": "y"}]
    assert F.recoupement(c)["nombre"] == avant + 1


def test_deux_noms_de_la_meme_maison_ne_font_pas_deux_maisons():
    """« Ember » et « Ember / SEAI » ne sont pas deux sources indépendantes ;
    les compter deux fois fabriquerait un recoupement qui n'existe pas."""
    c = {"source": {"editeur": "Ember"},
         "corroborations": [{"editeur": "Ember / SEAI"}]}
    assert F.recoupement(c)["nombre"] == 1
    assert F.recoupement(c)["recoupe"] is False


def test_un_controle_non_recoupe_LE_DIT():
    c = {"source": {"editeur": "Ember"}}
    r = F.recoupement(c)
    assert r["recoupe"] is False
    assert "une seule maison" in r["dit"]


def test_la_concentration_nomme_l_editeur_dominant():
    """C'est le chiffre qu'un lecteur exigeant demande avant de citer le
    référentiel : sur qui repose-t-il réellement ?"""
    k = F.concentration()
    assert k["total"] == len(F.CONTROLES)
    assert k["editeur_dominant"]
    assert 0.0 <= k["part_dominant"] <= 1.0
    assert k["editeur_dominant"] in k["dit"]


def test_les_corroborations_sont_publiees_avec_les_sources():
    """Les omettre publierait un registre plus pauvre que le travail fait."""
    editeurs = {(s.get("editeur") or "") for s in F.sources()}
    corrobores = {(s.get("editeur") or "")
                  for c in F.CONTROLES for s in (c.get("corroborations") or [])}
    assert corrobores, "aucune corroboration enregistrée dans le registre"
    assert corrobores <= editeurs


def test_l_ETAT_PUBLIE_porte_le_recoupement_de_chaque_controle():
    e = F.etat()
    assert "concentration" in e
    assert all("recoupement" in c for c in e["controles"])


def test_l_ECART_ENTRE_LES_DEUX_SITES_EST_AU_REGISTRE():
    """L'audit a mesuré que 28 des 29 pays communs divergent entre Sentinel et
    conseilprevcyber. Un client qui compare deux livrables du cabinet doit
    trouver la raison au registre, et non la découvrir en réunion."""
    c = F.par_cle("intensite_deux_sites")
    assert c is not None
    assert c["verdict"] == "corrige"
    assert "45" in c["constat"] and "56" in c["constat"]
    assert "millésime" in c["constat"]
    assert F.recoupement(c)["recoupe"] is True
