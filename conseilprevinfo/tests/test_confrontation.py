"""LA CONFRONTATION — ce qu'un outil qui ne lit pas ne doit pas prétendre.

C'est le module le plus tentant du site. On y dépose un document, il en sort
une liste — et une liste a l'air d'un audit. Ces contrôles gardent les cinq
règles qui empêchent le rapprochement de vocabulaire de se faire passer pour
une lecture :

  1. LE DOCUMENT NE SORT PAS. Ni sur disque, ni dans la réponse.
  2. LE DÉPÔT DEMANDE UN COMPTE. Ce qu'un document contient renseigne sur
     l'installation de celui qui le dépose.
  3. LA RÉSERVE EST PORTÉE PAR LE RÉSULTAT, pas reléguée sur la page.
  4. LE BRUIT EST ÉCARTÉ, ET LA COUPE EST DITE. Trois filtres, chacun posé
     après une mesure qui a montré que le précédent ne suffisait pas.
  5. UNE SORTIE QUI NE TIENT PAS DEBOUT N'EST PAS SERVIE. Le module mesure
     si ses propres questions valent quelque chose, et se tait sinon.
"""
import io
import os
import sys
import zipfile

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import pytest  # noqa: E402

import abonnes as AB  # noqa: E402
import app as A  # noqa: E402
import confrontation as C  # noqa: E402
import veille as V  # noqa: E402

MDP = "une phrase entiere vaut mieux"

DOC = ("Politique de sécurité des systèmes industriels. La segmentation du "
       "réseau industriel repose sur des zones et des conduits documentés. "
       "Chaque zone porte un niveau de sécurité cible issu d'une analyse de "
       "risque. Une zone démilitarisée sépare le réseau bureautique du réseau "
       "de production. Les accès distants des prestataires transitent par un "
       "bastion avec authentification forte et enregistrement de session. La "
       "supervision des équipements est assurée depuis une console dédiée et "
       "les journaux sont centralisés. Les correctifs suivent une fenêtre de "
       "maintenance validée par la production. Les sauvegardes des "
       "configurations d'automates sont hebdomadaires et testées par "
       "restauration. Le plan de continuité prévoit un redémarrage en mode "
       "dégradé et une conduite manuelle des procédés critiques. Un "
       "inventaire des actifs industriels est tenu à jour avec le "
       "propriétaire, la criticité et la zone de chaque équipement. "
       "L'architecture prévoit des postes d'ingénierie durcis et dédiés. Les "
       "supports amovibles sont interdits sauf dérogation nominative écrite. "
       "La sensibilisation des exploitants et de la maintenance est annuelle. "
       "Les incidents sont déclarés au responsable sécurité sous vingt-quatre "
       "heures et le retour d'expérience est formalisé. Les contrats des "
       "fournisseurs portent une clause de sécurité et de notification des "
       "vulnérabilités affectant les produits livrés. La revue du périmètre "
       "et de cette politique est annuelle.") * 2


@pytest.fixture()
def corpus():
    c = A.corpus()
    if not c:
        pytest.skip("corpus vide : sources injoignables")
    return c


@pytest.fixture()
def client():
    A.app.config["TESTING"] = True
    with A.app.test_client() as c:
        yield c


@pytest.fixture(autouse=True)
def _comptes_propres():
    AB._COMPTES.clear()
    AB._SESSIONS.clear()
    yield
    AB._COMPTES.clear()
    AB._SESSIONS.clear()


# ── 1. Le document ne sort pas ────────────────────────────────────────────

def test_le_resultat_ne_contient_aucun_extrait_du_document(corpus):
    """Renvoyer le texte, fût-ce par commodité d'affichage, le ferait
    transiter une fois de plus et apparaître dans les journaux du
    navigateur."""
    r = C.confronter(DOC, corpus)
    assert r["ok"]
    brut = repr(r)
    for phrase in ("zone démilitarisée", "vingt-quatre heures",
                   "supports amovibles", "bastion avec"):
        assert phrase not in brut, phrase
    assert r["document_conserve"] is False


def test_le_module_declare_ne_rien_conserver():
    s = C.sante()
    assert s["document_conserve"] is False
    assert s["modeles_de_langage"] == 0


def test_aucune_ecriture_sur_disque_dans_le_module():
    """Un `open(..., "w")` ici serait la seule ligne qui compte : tout le
    reste du discours sur la confidentialité en dépend."""
    src = open(os.path.join(ICI, "confrontation.py"), encoding="utf-8").read()
    for interdit in ("open(", "mkstemp", "NamedTemporary", "shutil",
                     "anthropic", "openai"):
        assert interdit not in src, interdit


# ── 2. Le dépôt demande un compte ─────────────────────────────────────────

def test_un_depot_anonyme_est_refuse(client):
    r = client.post("/api/confrontation", data={
        "document": (io.BytesIO(DOC.encode()), "politique.txt")})
    assert r.status_code == 401
    assert r.get_json()["erreur"] == "non_connecte"


def test_un_abonne_peut_confronter(client, corpus):
    AB.creer("ing@usine.fr", MDP)
    j = AB.connecter("ing@usine.fr", MDP)["jeton"]
    r = client.post("/api/confrontation",
                    headers={"Authorization": "Bearer " + j},
                    data={"document": (io.BytesIO(DOC.encode()), "p.txt")})
    assert r.status_code == 200, r.get_json()
    assert r.get_json()["ok"] is True


# ── 3. La réserve voyage avec le résultat ─────────────────────────────────

def test_le_resultat_porte_ce_qu_il_n_etablit_pas(corpus):
    """Reléguée sur la page, la réserve ne suivrait pas un résultat recopié
    dans un courriel ou une note interne."""
    r = C.confronter(DOC, corpus)
    assert "ne lit pas votre document" in r["n_etablit_pas"]
    assert "questions à poser" in r["n_etablit_pas"]
    assert "conformité" in r["n_etablit_pas"]


def test_la_rubrique_retenue_est_dite_avec_sa_raison(corpus):
    """Un filtrage silencieux laisserait croire que le corpus ne porte que
    cela."""
    r = C.confronter(DOC, corpus)
    assert r["sujet_pourquoi"]
    assert isinstance(r["sujet_scores"], dict) and r["sujet_scores"]
    impose = C.confronter(DOC, corpus, sujet="cyber_industriel")
    assert impose["sujet"] == "cyber_industriel"
    assert "imposée par vous" in impose["sujet_pourquoi"]


# ── 4. Le bruit est écarté, et la coupe est dite ──────────────────────────

def test_un_gabarit_repete_ne_devient_pas_un_theme(corpus):
    """PREMIER DÉFAUT MESURÉ. Les quatorze fiches de mix électrique sont
    quatorze exemplaires d'une même phrase : leurs mots paraissaient portés
    par quatorze fiches alors qu'ils ne le sont que par un gabarit. La
    confrontation demandait sérieusement à une politique de cybersécurité si
    elle traitait du « gco2e »."""
    r = C.confronter(DOC, corpus)
    termes = {q["terme"] for q in r["questions"]} | {e["terme"] for e in r["echos"]}
    for gabarit in ("gco2e", "nucleaire", "filiere", "renouvelables"):
        assert gabarit not in termes, gabarit
    assert C.MINI_SOURCES >= 2


def test_la_comparaison_porte_sur_la_langue_du_lecteur(corpus):
    """DEUXIÈME DÉFAUT MESURÉ. La confrontation puisait dans le titre et le
    chapeau, qui viennent de la source — donc en anglais pour MITRE et CISA.
    Une politique française se voyait demander si elle traitait de
    « targeted », « malware » et « threat »."""
    r = C.confronter(DOC, corpus)
    termes = {q["terme"] for q in r["questions"]} | {e["terme"] for e in r["echos"]}
    for anglais in ("targeted", "malware", "threat", "attacks", "systems"):
        assert anglais not in termes, anglais


def test_ce_qui_est_partout_n_est_pas_un_theme(corpus):
    """TROISIÈME DÉFAUT MESURÉ, et le plus embarrassant : les questions
    portaient sur MA PROPRE PROSE — « votre » sur 80 fiches, « point »,
    « seulement ». Ce site dérive ses lectures par règles : son vocabulaire
    est uniforme par construction."""
    r = C.confronter(DOC, corpus)
    termes = {q["terme"] for q in r["questions"]} | {e["terme"] for e in r["echos"]}
    for tic in ("votre", "point", "seulement", "confronter"):
        assert tic not in termes, tic
    assert 0 < C.PART_MAX_CORPUS <= 0.34


def test_les_termes_ecartes_sont_comptes_et_dits(corpus):
    """Une coupe silencieuse se lit comme une couverture complète."""
    r = C.confronter(DOC, corpus)
    assert r["termes_ecartes_gabarit"] >= 0
    assert r["plafond_fiches"] >= C.MINI_FICHES
    if r["termes_ecartes_gabarit"] or r["termes_ecartes_partout"]:
        assert r["ecartes_dit"]


# ── 5. Une sortie qui ne tient pas debout n'est pas servie ────────────────

def test_les_questions_ne_sont_servies_que_si_elles_valent_quelque_chose(corpus):
    """LE CONTRÔLE CENTRAL. Servir une liste parce qu'elle est non vide, sur
    un corpus dont le vocabulaire est uniforme, reviendrait à présenter des
    mots de liaison comme des points à instruire — et à faire perdre
    confiance dans tout le reste de la page."""
    r = C.confronter(DOC, corpus)
    assert isinstance(r["questions_utiles"], bool)
    assert r["questions_pourquoi"]
    if not r["questions_utiles"]:
        assert r["questions"] == [] and r["n_questions"] == 0
        assert "constat, pas une panne" in r["questions_pourquoi"]
    else:
        assert all(len(q["sources"]) >= 3 for q in r["questions"])


def test_un_document_trop_court_est_refuse_plutot_que_confronte(corpus):
    r = C.confronter("Trois mots seulement ici.", corpus)
    assert r["ok"] is False and r["erreur"] == "trop_court"
    assert str(C.MOTS_MIN) in r["message"]


# ── 6. Lire un document, ou dire pourquoi on ne peut pas ──────────────────

def test_un_format_inconnu_est_refuse_avec_la_liste_des_formats_lus():
    t, faute = C.lire("schema.dwg", b"x" * 500)
    assert t is None and ".txt" in faute and ".docx" in faute


def test_un_fichier_trop_gros_est_refuse_avec_sa_taille():
    t, faute = C.lire("gros.txt", b"x" * (C.OCTETS_MAX + 1))
    assert t is None and "trop volumineux" in faute


def test_un_docx_est_lu_sans_bibliotheque_tierce():
    """Un .docx est un zip d'XML : la bibliothèque standard suffit, et l'on
    évite une dépendance de plus pour lire un format documenté."""
    tampon = io.BytesIO()
    with zipfile.ZipFile(tampon, "w") as z:
        z.writestr("word/document.xml",
                   '<?xml version="1.0"?><w:document xmlns:w="x"><w:body>'
                   '<w:p><w:r><w:t>segmentation des zones</w:t></w:r></w:p>'
                   '<w:p><w:r><w:t>bastion et journalisation</w:t></w:r></w:p>'
                   '</w:body></w:document>')
    t, faute = C.lire("note.docx", tampon.getvalue())
    assert not faute, faute
    assert "segmentation" in t and "bastion" in t


def test_un_docx_illisible_le_dit_au_lieu_de_rendre_un_texte_vide():
    """Un texte vide se lirait comme un document sans vocabulaire — donc
    comme un document qui ne traite de rien."""
    t, faute = C.lire("faux.docx", b"ceci n'est pas un zip")
    assert t is None and "illisible" in faute.lower()


def test_deux_confrontations_du_meme_document_rendent_le_meme_resultat(corpus):
    assert C.confronter(DOC, corpus) == C.confronter(DOC, corpus)
