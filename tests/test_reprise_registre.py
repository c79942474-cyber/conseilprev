# -*- coding: utf-8 -*-
"""La reprise du registre — les propriétés que la mesure a imposées.

POURQUOI CES RÈGLES EXISTENT, ET CE QU'ELLES MESURENT.

L'outil de reprise a été éprouvé le 5 septembre 2026 contre une réplique
fidèle des deux bases : 1 696 lignes d'un côté, 21 de l'autre. Il a annoncé
« 1 573 lignes reprises, transaction validée » et rendu 0. La mesure disait
autre chose — 112 lignes restées au sol, un constat qui annonçait 0 fragment
là où l'exécution en copiait 1 410, et 1 410 fragments repris sans index
plein texte, sur lesquels la recherche rendait ZÉRO résultat.

CES RÈGLES NE RELISENT PAS LE CODE : ELLES TIENNENT LES PROPRIÉTÉS. Chacune
correspond à un défaut mesuré, et le nomme. Le bout-en-bout, lui, demande deux
bases PostgreSQL : il vit dans `outils/recette_reprise_registre.py`, comme les
autres recettes de ce dépôt qui touchent l'extérieur.
"""
import ast
import io
import os
import re
import sys

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

OUTIL = io.open(os.path.join(ICI, "outils", "reprise_registre.py"),
                encoding="utf-8").read()


def _plan():
    """Le PLAN, relevé dans le fichier — pas recopié ici.

    Une liste recopiée décrirait le plan d'un jour donné et cesserait de
    couvrir au premier ajout.

    IL SE LIT COMME UN LITTÉRAL, pas à l'expression régulière : la première
    version butait sur `md5(contenu_fichier)`, dont la parenthèse fermait le
    motif trop tôt. Elle rendait quinze entrées sur seize et perdait
    silencieusement `rag_documents` — la table la plus délicate du plan.
    """
    i = OUTIL.index("PLAN = [")
    bloc = OUTIL[i + len("PLAN = "):OUTIL.index("\n]\n", i) + 2]
    return [(t, tuple(c), tuple(g)) for t, c, g in ast.literal_eval(bloc)]


# ══════════════════════════════════════════════════════════════════════════
# 1. AUCUNE TABLE SANS IDENTITÉ — le défaut qui a laissé 15 lignes au sol
# ══════════════════════════════════════════════════════════════════════════

def test_le_plan_est_relevable_et_non_vide():
    """Garde-fou : un relevé cassé rendrait toutes les règles suivantes vertes
    en ne mesurant rien — le défaut que ce dépôt a déjà commis ailleurs."""
    plan = _plan()
    assert len(plan) >= 17, plan
    noms = [t for t, _, _ in plan]
    assert "rag_documents" in noms, noms
    assert "rgpd_registre_site" in noms, noms


@pytest.mark.parametrize("table,cle,ignorer", _plan())
def test_chaque_table_porte_une_cle_d_identite(table, cle, ignorer):
    """UNE CLÉ VIDE VALAIT « reprise seulement si la destination est vide ».

    Sept tables en avaient une. Sur une destination qui tournait depuis huit
    jours, la règle a refusé les huit preuves de consentement et sept lignes
    d'empreinte — en imprimant une remarque en fin de ligne, et en rendant 0.
    """
    assert cle, ("%s n'a pas de clé d'identité : sur une destination non "
                 "vide, sa reprise sera refusée en silence." % table)


def test_le_document_est_identifie_par_son_contenu_et_non_par_son_nom():
    """MESURÉ : sur `nom_fichier`, trois dépôts du même PDF sous le même nom
    entraient trois fois, et deux repartaient sans un seul fragment. Le nom
    d'un fichier n'est pas son identité ; son contenu l'est."""
    cle = dict((t, c) for t, c, _ in _plan())["rag_documents"]
    assert cle == ("md5(contenu_fichier)",), cle


def test_les_jalons_reprennent_la_contrainte_que_porte_la_destination():
    """La destination porte UNIQUE (client_id, milestone_id). Une clé vide
    aurait fonctionné tant qu'elle est vide, et échoué le jour où elle ne
    l'est plus — c'est-à-dire au deuxième passage."""
    cle = dict((t, c) for t, c, _ in _plan())["raas_milestones"]
    assert cle == ("client_id", "milestone_id"), cle


# ══════════════════════════════════════════════════════════════════════════
# 2. L'INDEX PLEIN TEXTE — le défaut qui rendait le corpus invisible
# ══════════════════════════════════════════════════════════════════════════

def test_aucune_colonne_n_est_reputee_calculee():
    """`search_vector` EN AVAIT L'AIR — le nom, le type tsvector — et elle
    était écartée comme telle. Vérification faite sur la base vivante : aucune
    colonne générée, aucun déclencheur. Rien ne la remplit.

    Les 1 410 fragments repris sans elle rendaient ZÉRO résultat à la
    recherche plein texte. L'outil rendait à l'assistant un corpus invisible
    et se déclarait satisfait — une réussite pour une raison sans rapport avec
    ce qu'elle prétendait.
    """
    i = OUTIL.index("CALCULEES = ")
    ligne = OUTIL[i:OUTIL.index("\n", i)]
    assert ligne.strip() == "CALCULEES = set()", ligne


def test_le_corpus_ne_retire_que_l_identifiant_et_le_lien():
    """Le seul retrait légitime : la clé primaire, que la destination
    réattribue, et `document_id`, qui suit la renumérotation."""
    i = OUTIL.index("def _reprendre_corpus(")
    corps = OUTIL[i:OUTIL.index("\ndef ", i + 10)]
    m = re.search(r'c not in \(([^)]*)\)', corps)
    assert m, corps[:400]
    retires = tuple(x.strip().strip('"') for x in m.group(1).split(",") if x.strip())
    assert retires == ("id", "document_id"), m.group(1)


# ══════════════════════════════════════════════════════════════════════════
# 3. LE CONSTAT PRÉDIT L'EXÉCUTION
# ══════════════════════════════════════════════════════════════════════════

def test_les_tables_manquantes_sont_creees_dans_les_deux_modes():
    """MESURÉ : le constat annonçait 1 524 lignes, l'exécution 1 566. Il ne
    pouvait pas compter celles des tables qu'il n'avait pas créées. Le DDL
    étant transactionnel, le constat les crée puis annule sa transaction."""
    i = OUTIL.index("def _creer_manquantes(")
    signature = OUTIL[i:OUTIL.index(")", i) + 1]
    assert "ecrire" not in signature, (
        "la création est conditionnée au mode : le constat sous-estimera "
        "la reprise de tout ce que porte une table absente. %s" % signature)
    corps = OUTIL[i:OUTIL.index("\ndef ", i + 10)]
    assert "if ecrire" not in corps, corps


def _branches_du_mode():
    """Les deux branches de `if ecrire:` dans main(), isolées.

    LA PREMIÈRE VERSION DE CETTE RÈGLE SE CONTENTAIT DE TROUVER UN
    `dst.rollback()` quelque part après `if ecrire:`. Le `except` en contient
    un : remplacer l'annulation du constat par une validation laissait donc la
    règle verte. Une mutation l'a montré — la règle passait pour une raison
    sans rapport avec ce qu'elle prétendait. Elle lit désormais chaque branche.
    """
    i = OUTIL.index("def main(")
    corps = OUTIL[i:]
    j = corps.index("if ecrire:")
    k = corps.index("\n        else:", j)
    fin = corps.index("except Exception", k)
    return corps[j:k], corps[k:fin]


def test_le_constat_annule_sa_transaction():
    """Un constat qui écrirait ne serait plus un constat."""
    _, blanc = _branches_du_mode()
    assert "dst.rollback()" in blanc, blanc
    assert "dst.commit()" not in blanc, blanc


def test_l_execution_valide_la_sienne():
    """Le témoin négatif de la règle précédente : sans lui, une reprise qui
    annulerait tout passerait pour prudente."""
    ecrit, _ = _branches_du_mode()
    assert "dst.commit()" in ecrit, ecrit
    assert "dst.rollback()" not in ecrit, ecrit


# ══════════════════════════════════════════════════════════════════════════
# 4. LE VERDICT REFUSE DE RENDRE 0 — le défaut le plus coûteux
# ══════════════════════════════════════════════════════════════════════════

def test_ce_qui_reste_au_sol_est_compte_et_nomme():
    """LA PREMIÈRE VERSION IMPRIMAIT « absente de la destination » dans une
    colonne de remarques, poursuivait, et rendait 0 en annonçant une
    transaction validée. Cent douze lignes étaient restées derrière — dont le
    registre RGPD, le registre de l'article 50 et les événements Stripe."""
    i = OUTIL.index("def main(")
    corps = OUTIL[i:]
    assert "au_sol" in corps, corps[:400]
    assert "RESTÉ AU SOL" in corps, corps[-1200:]
    assert "return 1" in corps, corps[-800:]


def test_le_succes_n_est_rendu_que_si_rien_n_est_reste_au_sol():
    """La règle qui distingue « la reprise a tourné » de « la reprise a eu
    lieu ». Le `return 0` doit être gardé par l'absence de perte."""
    i = OUTIL.index("def main(")
    corps = OUTIL[i:]
    j = corps.index("if au_sol:")
    k = corps.index("return 0")
    assert j < k, ("le succès est rendu avant d'avoir regardé ce qui reste "
                   "au sol")
    assert "return 1" in corps[j:k], corps[j:k]


# ══════════════════════════════════════════════════════════════════════════
# 5. LE LOT SE DÉDOUBLONNE LUI-MÊME
# ══════════════════════════════════════════════════════════════════════════

def test_le_lot_source_se_dedoublonne_et_pas_seulement_contre_la_destination():
    """La garde ne comparait qu'à la destination : elle protégeait de
    l'existant, pas du lot en cours. Trois exemplaires du même document sont
    entrés ensemble."""
    i = OUTIL.index("def _reprendre_table(")
    corps = OUTIL[i:OUTIL.index("\ndef ", i + 10)]
    assert "vues" in corps, corps
    assert "k in vues" in corps, corps
    assert "doublons" in corps, corps


def test_les_doublons_ecartes_sont_comptes_a_part_des_pertes():
    """Un doublon écarté est un ARBITRAGE ; une ligne perdue est un DÉFAUT.
    Les confondre dans un même total les rendrait tous deux illisibles."""
    i = OUTIL.index("def main(")
    corps = OUTIL[i:]
    assert "doublons" in corps, corps[:900]
    assert "%9s" % "doublons" in corps or '"doublons"' in corps, corps[:900]


# ══════════════════════════════════════════════════════════════════════════
# 6. CE QUE L'OUTIL NE FAIT PAS, ET LE DIT
# ══════════════════════════════════════════════════════════════════════════

def test_l_outil_n_ecrase_jamais_et_ne_supprime_rien():
    """La ligne VIVANTE gagne toujours : huit jours d'exploitation valent
    mieux qu'une reprise qui les efface."""
    assert "UPDATE " not in OUTIL.upper().replace("UPDATE_", "")
    assert "DELETE FROM" not in OUTIL.upper()
    assert "DROP " not in OUTIL.upper()


# ══════════════════════════════════════════════════════════════════════════
# 7. LE SCRIPT DE NETTOYAGE — gardé, parce qu'un TRUNCATE ne se rejoue pas
# ══════════════════════════════════════════════════════════════════════════

NETTOYAGE = io.open(os.path.join(ICI, "outils", "reprise_nettoyer_rag.py"),
                    encoding="utf-8").read()


def test_le_nettoyage_est_a_sec_par_defaut():
    """Sans `--vider`, il compte et n'écrit rien. Le TRUNCATE doit être gardé
    par le drapeau — un nettoyage qui agit par défaut est un accident qui
    attend son heure."""
    i = NETTOYAGE.index("def main(")
    corps = NETTOYAGE[i:]
    assert 'vider = "--vider" in sys.argv' in corps, corps[:200]
    j = corps.index("TRUNCATE")
    # Entre le début de main et le TRUNCATE, il y a le garde `if not vider`.
    assert "if not vider:" in corps[:j], "le TRUNCATE n'est pas gardé par --vider"


def test_le_nettoyage_refuse_de_vider_la_source():
    """La source de la reprise ne doit JAMAIS être vidée — ce serait effacer le
    corpus qu'on s'apprête à recopier. Le garde compare au nom de l'ancienne
    base."""
    assert 'SOURCE_INTERDITE = "conseilprev_registre_db"' in NETTOYAGE, NETTOYAGE[:400]
    i = NETTOYAGE.index("def main(")
    corps = NETTOYAGE[i:]
    assert "== SOURCE_INTERDITE" in corps, corps
    # Le refus doit précéder tout TRUNCATE.
    assert corps.index("SOURCE_INTERDITE") < corps.index("TRUNCATE"), corps


def test_le_nettoyage_ne_touche_que_les_deux_tables_du_rag():
    """Il ne doit nommer aucune autre table. Un nettoyage qui déborde de son
    périmètre est le contraire d'un nettoyage."""
    assert 'TABLES_RAG = ("rag_chunks", "rag_documents")' in NETTOYAGE, NETTOYAGE[:600]
    import re as _re
    # Uniquement le SQL RÉELLEMENT exécuté (cur.execute("TRUNCATE ...")), pas
    # les mentions du mot dans les commentaires.
    cibles = _re.findall(r'cur\.execute\("TRUNCATE ([^"]+)"', NETTOYAGE)
    assert cibles, "aucun TRUNCATE exécuté trouvé"
    for c in cibles:
        for mot in c.replace(",", " ").split():
            if mot in ("RESTART", "IDENTITY", "CASCADE"):
                continue
            assert mot in ("rag_chunks", "rag_documents"), (
                "le TRUNCATE vise autre chose que le RAG : %r" % mot)


def test_le_nettoyage_dit_a_quelle_base_il_parle():
    """Le nom de la base est imprimé avant tout : une erreur d'adresse doit se
    voir, pas se subir."""
    i = NETTOYAGE.index("def main(")
    corps = NETTOYAGE[i:]
    assert "current_database" in corps, corps[:400]
    assert corps.index("current_database") < corps.index('cur.execute("TRUNCATE'), corps


def test_la_source_n_est_jamais_ecrite():
    """Elle est lue, et c'est tout — la reprise ne doit pas abîmer ce qu'elle
    copie, ni empêcher un second essai."""
    assert "src.commit()" not in OUTIL
    i = OUTIL.index("def main(")
    assert "src.close()" in OUTIL[i:]
