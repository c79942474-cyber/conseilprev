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


def test_LE_CHIFFRE_PUBLIE_SE_REMESURE_quand_les_deux_depots_sont_la():
    """UN CONSTAT ÉCRIT À LA MAIN SE DÉMODE EN SILENCE — celui-ci l'avait fait.

    La version publiée annonçait « 12,1 % en moyenne ». Re-mesuré, aucun
    dénominateur défendable ne redonne ce chiffre : c'est 12,8 % en rapportant
    l'écart à la valeur Sentinel sur les 29 pays communs (médiane 9,0 %,
    maximum 50 % au Luxembourg). Le chiffre était faux et il était publié.

    Ce contrôle recalcule l'écart sur les DEUX TABLES RÉELLES et exige que le
    constat porte le résultat. Il ne peut le faire que si le dépôt cyber est
    présent à côté ; quand il ne l'est pas, il le DIT au lieu de passer en
    silence — un contrôle qui s'ignore lui-même ne vaut pas mieux qu'un chiffre
    figé."""
    import os
    import statistics
    import importlib.util
    import empreinte_sites

    ailleurs = os.path.join(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))), "conseilprevcyber",
        "datacenter.py")
    if not os.path.exists(ailleurs):
        import pytest
        pytest.skip("dépôt conseilprevcyber absent : écart non re-mesurable "
                    "ici — le constat reste sous la seule foi de son auteur")

    spec = importlib.util.spec_from_file_location("_dc_cyber", ailleurs)
    dc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dc)

    S, C = empreinte_sites.INTENSITE, dc.INTENSITE_RESEAU
    communs = sorted(set(S) & set(C))
    ecarts = [abs(C[p] - S[p]) / S[p] * 100.0 for p in communs if S[p]]
    moyenne = sum(ecarts) / len(ecarts)
    mediane = statistics.median(ecarts)

    c = F.par_cle("intensite_deux_sites")
    # ON ANCRE SUR LA PHRASE, PAS SUR LE CHIFFRE NU — et c'est mesuré : la
    # première rédaction de ce contrôle cherchait « 12.8 » n'importe où dans le
    # constat. Elle passait donc alors même que le chiffre de tête était resté
    # faux à 12,1 %, parce que le bon chiffre figurait plus bas, dans la réserve
    # qui raconte la correction. Un contrôle qui se satisfait d'une occurrence
    # ailleurs ne contrôle rien.
    # LES DEUX ÉCRITURES D'UN ENTIER SONT ACCEPTÉES — « 50 % » et « 50,0 % ».
    # Exiger la seconde obligerait à écrire « maximum 50,0 % » dans une phrase
    # française, ce qui est laid sans rien prouver de plus. On tolère la forme,
    # jamais la valeur.
    def formes(x):
        s = ("%.1f" % x).replace(".", ",")
        return [s] + ([s[:-2]] if s.endswith(",0") else [])

    maximum = max(ecarts)
    for etiquette, valeur in (("MÉDIAN", mediane), ("moyen", moyenne),
                              ("maximum", maximum)):
        attendus = ["%s %s %%" % (etiquette, f) for f in formes(valeur)]
        assert any(a in c["constat"] for a in attendus), (
            "le constat n'annonce pas « %s » — mesuré sur les deux tables"
            % attendus[0])
    # LE COMPTE DE PAYS DIVERGENTS EST LUI AUSSI MESURÉ, pas recopié.
    divergents = sum(1 for p in communs if C[p] != S[p])
    assert "%d des %d" % (divergents, len(communs)) in c["constat"], (
        "le constat annonce un autre compte que les %d / %d mesurés"
        % (divergents, len(communs)))
