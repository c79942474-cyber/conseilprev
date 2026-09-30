# -*- coding: utf-8 -*-
"""Les huit champs du FinOps se saisissent — le renvoi de la page cesse de mentir.

LE DÉFAUT MESURÉ. Le moteur FinOps réclame huit champs par système, et il sert
lui-même leur mode d'emploi : « Registre IA → fiche du système → "Modèle" ».
Ce renvoi désignait un champ qui N'EXISTAIT PAS. Relevé sur le dépôt avant
correction : les huit noms de champs n'apparaissaient dans AUCUNE balise de
saisie, et `regSave()` n'en envoyait aucun. La base les acceptait, l'API les
acceptait en POST comme en PUT, le moteur savait les chiffrer — seul le
formulaire manquait.

Mesure au navigateur, AVANT : couverture « 0 / 4 », « 0 % du parc déclaré est
chiffrable », et chaque ligne au motif « unité de facturation non déclarée ».
Le module était inutilisable, et il disait pourtant où cliquer.

Mesure au navigateur, APRÈS (même parcours, un système renseigné) :
    couverture « 1 / 5 » · 20 % · coût mensuel 45,00 USD
    formule affichée : (10000000 jetons d'entrée / 1e6 × 3.0)
                     + (1000000 jetons de sortie / 1e6 × 15.0) USD
soit 10 × 3 + 1 × 15 = 45 — l'arithmétique du moteur, rendue atteignable.

CE QUE CES RÈGLES MESURENT : que la fiche porte les huit champs, que son
vocabulaire soit CELUI DU MOTEUR et non une recopie qui dérive, que
`regSave` les envoie, et qu'un champ vide parte à `null` — jamais à zéro, qui
ferait d'un parc jamais instruit un parc qui ne coûte rien.
"""
import io
import json
import os
import re

import pytest

import finops_ia as F

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _lire(nom):
    with io.open(os.path.join(RACINE, nom), encoding="utf-8") as f:
        return f.read()


ECRAN = _lire("sentinel.page.js")
SERVEUR = _lire("app.py")

#: Le champ du moteur, et l'identifiant de la case qui le saisit.
CHAMPS = {
    "modele": "rf-modele",
    "unite_facturation": "rf-unite",
    "volume_entree_mois": "rf-vol-entree",
    "volume_sortie_mois": "rf-vol-sortie",
    "volume_source": "rf-vol-source",
    "centre_cout": "rf-centre-cout",
    "classe_tache": "rf-classe-tache",
    "leviers": "rf-leviers",
}


# ── 1. LES HUIT SE SAISISSENT ────────────────────────────────────────────

def test_le_moteur_reclame_bien_huit_champs_et_pas_un_de_plus():
    """La liste de cette règle est celle du moteur, pas une liste parallèle :
    un neuvième champ ajouté au moteur doit faire tomber ce fichier, et non
    passer inaperçu faute de case pour le saisir."""
    assert set(F.CHAMPS_FINOPS) == set(CHAMPS), (
        "le moteur réclame %s, la saisie couvre %s"
        % (sorted(F.CHAMPS_FINOPS), sorted(CHAMPS)))


@pytest.mark.parametrize("champ,case", sorted(CHAMPS.items()))
def test_chaque_champ_du_finops_a_sa_case_dans_la_fiche(champ, case):
    assert 'id="%s"' % case in ECRAN, (
        "« %s » n'a aucune case de saisie : le FinOps le réclame et personne "
        "ne peut le renseigner" % champ)


@pytest.mark.parametrize("champ,case", sorted(CHAMPS.items()))
def test_chaque_champ_du_finops_part_vers_le_serveur(champ, case):
    """Une case qu'on remplit et qui ne part pas est pire qu'une case absente :
    elle donne le sentiment d'avoir répondu."""
    m = re.search(r"var payload = \{(.*?)\n  \};", ECRAN, re.S)
    assert m, "le corps envoyé par regSave est introuvable"
    assert re.search(r"\b%s\s*:" % re.escape(champ), m.group(1)), (
        "« %s » n'est pas dans ce que regSave envoie" % champ)


def test_le_renvoi_servi_par_le_moteur_designe_une_case_qui_existe():
    """C'EST LE DÉFAUT D'ORIGINE. Le moteur dit à l'utilisateur où saisir
    chaque champ. Tant que la case n'existait pas, ce renvoi envoyait dans le
    mur — et l'utilisateur concluait qu'il n'avait pas compris."""
    for champ, d in F.CHAMPS_FINOPS.items():
        assert d["panneau"] == "registre", (champ, d["panneau"])
        assert "Registre IA" in d["ou"], (champ, d["ou"])
        assert CHAMPS[champ] and 'id="%s"' % CHAMPS[champ] in ECRAN, (
            "« %s » renvoie vers « %s », et cette case n'existe pas"
            % (champ, d["ou"]))


# ── 2. LE VOCABULAIRE EST CELUI DU MOTEUR, PAS UNE RECOPIE ───────────────

def _options(champ):
    m = re.search(r'sel\("%s",\[(.*?)\]\)' % re.escape(champ), ECRAN, re.S)
    assert m, "les options de « %s » sont introuvables au formulaire" % champ
    return {v for v in re.findall(r'v:"([\w-]*)"', m.group(1)) if v}


def test_les_unites_de_facturation_sont_celles_du_moteur():
    assert _options("unite_facturation") == set(F.UNITES), (
        "le moteur connaît %s, le formulaire propose %s"
        % (sorted(F.UNITES), sorted(_options("unite_facturation"))))


def test_les_classes_de_tache_sont_celles_du_moteur():
    assert _options("classe_tache") == set(F.CLASSES_TACHE), (
        "le moteur connaît %s, le formulaire propose %s"
        % (sorted(F.CLASSES_TACHE), sorted(_options("classe_tache"))))


def test_les_leviers_proposes_sont_ceux_du_moteur():
    i = ECRAN.index('id="rf-leviers"')
    bloc = ECRAN[i:i + 700]
    proposes = set(re.findall(r"\['(\w+)',", bloc))
    assert proposes == set(F.LEVIERS), (
        "le moteur connaît %s, le formulaire propose %s"
        % (sorted(F.LEVIERS), sorted(proposes)))


def test_la_liste_des_modeles_est_servie_et_jamais_recopiee_a_l_ecran():
    """La table de prix bouge — elle porte sa date de relevé et sa péremption.
    Une liste recopiée dans le formulaire proposerait un jour un modèle que le
    chiffrage ne sait plus chiffrer, ou tairait un modèle qu'il sait. La règle
    regarde la CASE elle-même : ses options viennent d'un appel, pas d'un
    tableau littéral. (Les noms de modèles employés ailleurs dans l'écran pour
    appeler une API ne sont pas concernés : ce n'est pas une liste de choix.)"""
    i = ECRAN.index('id="rf-modele"')
    case = ECRAN[i:i + 200]
    assert "regModelesAvec(sys)" in case, (
        "les options du modèle ne sont pas servies : %s" % case[:160])
    for modele in F.TARIFS:
        assert modele not in case, (
            "« %s » est écrit en dur dans la case : la liste doit venir du "
            "serveur, qui seul tient la table de prix" % modele)
    #  LA ROUTE DU REGISTRE, ET PAS UNE AUTRE. « modeles_tarifes » existe
    #  aussi dans la réponse du FinOps : chercher le mot dans tout le fichier
    #  laissait passer la suppression mesurée ici.
    d = SERVEUR.index("def registre_list()")
    route = SERVEUR[d:d + 2500]
    assert "modeles_tarifes" in route, (
        "la route du registre ne sert plus la liste des modèles : la fiche "
        "d'un système n'aurait plus aucun modèle à proposer")
    assert "regModelesTarifesConnus" in ECRAN


@pytest.mark.parametrize("case", ["rf-vol-entree", "rf-vol-sortie"])
def test_l_unite_des_volumes_est_ecrite_a_cote_de_la_case(case):
    """LES VOLUMES SONT DES JETONS, JAMAIS DES REQUÊTES — et le même champ est
    lu en requêtes par l'empreinte quand l'unité de facturation le dit. Un
    nombre sans unité écrite à côté de la case se saisit faux.

    La règle lit LE LIBELLÉ DE SA PROPRE CASE, pas les quatre cents caractères
    qui la précèdent : la première version regardait autour, et le « jetons »
    de la case voisine la faisait passer alors que le libellé mesuré, lui,
    avait perdu le sien."""
    i = ECRAN.index('id="%s"' % case)
    debut = ECRAN.rindex("regField(", 0, i)
    libelle = ECRAN[debut:i]
    assert "jetons" in libelle, (
        "« %s » ne dit pas son unité : le chiffre saisi sera lu en jetons "
        "quoi qu'il arrive — libellé mesuré : %s" % (case, libelle[:200]))


# ── 3. UN CHAMP VIDE N'EST PAS UN ZÉRO ───────────────────────────────────

def test_un_volume_non_saisi_part_a_rien_et_pas_a_zero():
    """« Un parc jamais instruit afficherait un coût mensuel de zéro, crédible
    et faux. » `Number('')` vaut 0 : la conversion naïve aurait transformé
    « rien saisi » en « zéro jeton consommé »."""
    m = re.search(r"function regNombre\(id\) \{(.*?)\n\}", ECRAN, re.S)
    assert m, "regNombre est introuvable"
    corps = m.group(1)
    assert "return null" in corps, corps
    assert "'' " in corps or "=== ''" in corps, (
        "regNombre ne distingue pas la case vide : %s" % corps)


def test_un_volume_nul_declare_se_chiffre_quand_meme():
    """Zéro jeton EST une déclaration, et le moteur la chiffre. La règle tient
    les deux bouts : le vide ne vaut pas zéro, et zéro n'est pas du vide."""
    ligne = F.cout_ligne({
        "id": 1, "nom": "Essai", "modele": "claude-sonnet-5",
        "unite_facturation": "jetons", "volume_entree_mois": 0,
        "volume_sortie_mois": 0, "volume_source": "relevé du mois",
    })
    assert ligne["instruit"] is True, ligne
    assert ligne["montant"] == 0, ligne


@pytest.mark.parametrize("colonne", ["volume_entree_mois", "volume_sortie_mois"])
def test_les_colonnes_de_volume_n_ont_toujours_aucune_valeur_par_defaut(colonne):
    """La saisie change ; la garde de la base, non."""
    m = re.search(
        r"registre_ajouter_colonne\(cur, 'systemes_ia', '%s', ([^)]*)\)"
        % colonne, SERVEUR)
    assert m, colonne
    assert "DEFAULT" not in m.group(1).upper(), (
        "« %s » porte une valeur par défaut : un parc jamais instruit "
        "coûterait zéro" % colonne)


# ── 4. LE SERVEUR REND CE QU'IL A REÇU ───────────────────────────────────

@pytest.mark.parametrize("champ", sorted(CHAMPS))
def test_le_serveur_accepte_et_rend_chaque_champ(champ):
    assert "'%s': d.get('%s')" % (champ, champ) in SERVEUR or \
           "'%s'" % champ in SERVEUR, champ


def test_un_systeme_renseigne_devient_chiffrable_et_le_montant_est_celui_du_tarif():
    """Le bout de la chaîne : ce qui se saisit désormais donne bien le montant
    mesuré à l'écran — 10 millions de jetons d'entrée et 1 million de sortie
    sur claude-sonnet-5, soit 10 × 3 + 1 × 15 = 45 USD."""
    systeme = {
        "id": 1, "nom": "Assistant de tri des candidatures",
        "modele": "claude-sonnet-5", "unite_facturation": "jetons",
        "volume_entree_mois": 10_000_000, "volume_sortie_mois": 1_000_000,
        "volume_source": "console de facturation, relevé du 31/08",
        "centre_cout": "CC-410", "classe_tache": "extraction",
        "leviers": ["cache"],
    }
    c = F.couverture([systeme])
    assert c["instruites"] == 1, c
    assert c["part_instruite"] == 1.0, c
    ligne = c["lignes"][0]
    assert ligne["instruit"] is True, ligne
    assert ligne["montant"] == pytest.approx(45.0), ligne
    assert ligne["devise"] == "USD", ligne
