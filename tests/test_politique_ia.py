# -*- coding: utf-8 -*-
"""Les deux politiques de gouvernance de l'IA, mesurées sur le PDF produit.

POURQUOI SUR LE PDF, ET PAS SUR LE MARKDOWN. Ce qui est remis au client est un
fichier, pas une chaîne de caractères. Entre les deux il y a une mise en page
qui coupe, translittère et pagine — et c'est elle qui a produit le seul vrai
défaut de ce travail : l'encadré de fin, mesuré coupé entre deux pages, trois
lignes en bas de l'avant-dernière et la suite en haut de la dernière. Une règle
qui aurait lu le Markdown l'aurait déclaré parfait.

CE QUE CES RÈGLES GARDENT, ET QUI NE SE DEVINE PAS :

  · LES DEUX DOCUMENTS RESTENT LE MÊME TEXTE. Les tenir à deux endroits aurait
    garanti la dérive, et c'est le modèle remis au client qui aurait vieilli —
    personne ne le relit.

  · LE MODÈLE VIERGE NE PORTE AUCUNE DONNÉE DE CONSEILPREV. Un modèle remis à
    un client avec le SIREN du cabinet dedans est une fuite, et de celles qu'on
    ne remarque qu'après l'envoi.

  · L'INVENTAIRE DISTINGUE CE QUI EST DE L'IA DE CE QUI N'EN EST PAS. Une
    politique qui rangerait les moteurs de calcul parmi les systèmes d'IA leur
    ferait porter des obligations qui ne les visent pas et diluerait
    l'attention sur ceux qui génèrent vraiment du texte.

  · LE DOCUMENT NE SE MARQUE PAS « PRODUIT PAR IA ». Apposer ce marquage sur la
    politique qui ORGANISE cet usage serait faux, et se remarquerait.
"""
import datetime
import re

import pytest

import livrables_export
import politique_ia as P

pypdf = pytest.importorskip("pypdf")

#: Une date FIXE. Passer `today()` ferait changer le verdict d'une règle à
#: minuit, et une suite qui tombe la nuit ne se diagnostique pas le matin.
JOUR = datetime.date(2026, 9, 12)


def _norm(t):
    """Espaces normalisés et apostrophes unifiées.

    LE PDF INSÈRE SES PROPRES RETOURS À LA LIGNE. Comparer une phrase sans
    normaliser fait échouer une vérification sur un document parfaitement
    correct — c'est arrivé pendant ce travail, et la règle accusait le
    document au lieu de s'accuser elle-même.
    """
    return " ".join((t or "").replace("’", "'").split())


@pytest.fixture(scope="module")
def docs():
    out = {}
    for var in ("conseilprev", "modele"):
        d = P.politique(var, entree=JOUR)
        blob = livrables_export.build_pdf(d["markdown"], d["meta"])
        r = pypdf.PdfReader(__import__("io").BytesIO(blob))
        out[var] = {
            "doc": d, "blob": blob, "pdf": r,
            "pages": [p.extract_text() or "" for p in r.pages],
        }
        out[var]["texte"] = _norm("\n".join(out[var]["pages"]))
    return out


# ═══════════════════════════════════════════════════════════════════════════
#  1. LES DEUX DOCUMENTS EXISTENT ET SONT COMPLETS
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("var", ["conseilprev", "modele"])
def test_les_seize_sections_du_gabarit_sont_toutes_la(docs, var):
    """Le gabarit en compte seize. En perdre une en cours de route se voit mal
    dans un document de sept pages, et se paie à l'audit."""
    t = docs[var]["texte"]
    manquantes = [i for i in range(1, 17) if not re.search(r"\b%d\.\s+\w" % i, t)]
    assert not manquantes, "sections absentes du PDF : %r" % manquantes


@pytest.mark.parametrize("var", ["conseilprev", "modele"])
def test_l_attestation_porte_les_trois_lignes_a_signer(docs, var):
    """Une attestation sans place pour le nom, la signature et la date n'est
    pas une attestation."""
    t = docs[var]["texte"]
    for mot in ("Nom", "Signature", "Date"):
        assert re.search(mot + r"\s*:\s*_", t), (
            "la ligne « %s » de l'attestation n'a pas d'espace à remplir" % mot)


# ═══════════════════════════════════════════════════════════════════════════
#  2. L'ENCADRÉ DE FIN — LE DÉFAUT QUI A ÉTÉ MESURÉ
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("var", ["conseilprev", "modele"])
def test_l_encadre_est_entier_sur_la_derniere_page(docs, var):
    """LA RÈGLE DÉCISIVE DE CE FICHIER.

    Sans le marquage insécable, l'encadré se coupait entre l'avant-dernière et
    la dernière page. Un avertissement scindé perd la moitié de sa force, et
    personne ne relit un PDF de sept pages pour s'en apercevoir.
    """
    fin = _norm(docs[var]["pages"][-1])
    assert _norm(P.ENCADRE_UE) in fin, (
        "l'encadré n'est pas entier sur la dernière page — il est probablement "
        "coupé par le saut de page")


@pytest.mark.parametrize("var", ["conseilprev", "modele"])
def test_l_encadre_est_repris_mot_pour_mot(docs, var):
    """IL VIENT DU CABINET, PAS DE CE MODULE.

    Le reformuler, même mieux tourné, ferait dire au document autre chose que
    ce que son auteur a voulu — et il porte des dates réglementaires.
    """
    t = docs[var]["texte"]
    for fragment in ("27 juillet 2026", "2 décembre 2027", "2 août 2026",
                     "literacy", "sans garantir un niveau précis"):
        assert _norm(fragment) in t, "fragment perdu : %r" % fragment


def test_l_encadre_ferme_le_document(docs):
    """Il est le dernier contenu, pas un aparté au milieu.

    Mesuré par la POSITION : après lui il ne reste que le pied de page et la
    note de production, jamais une section de la politique.
    """
    for var in ("conseilprev", "modele"):
        t = docs[var]["texte"]
        i = t.index(_norm(P.ENCADRE_UE)[:60])
        apres = t[i:]
        assert not re.search(r"\b1[0-6]\.\s+[A-ZÉÀ]", apres), (
            "une section de la politique suit l'encadré dans %s" % var)


# ═══════════════════════════════════════════════════════════════════════════
#  3. LE MODÈLE VIERGE NE FUIT RIEN DU CABINET
# ═══════════════════════════════════════════════════════════════════════════

def test_le_modele_vierge_ne_porte_aucune_donnee_de_conseilprev(docs):
    """UNE FUITE QU'ON NE REMARQUE QU'APRÈS L'ENVOI.

    Le modèle est remis à des tiers. Y laisser le SIREN, l'adresse ou le
    courriel du cabinet serait au mieux gênant, au pire une divulgation.
    """
    # DEUX MESURES, PARCE QU'IL Y A DEUX ZONES. Le CORPS de la politique ne
    # doit porter aucune donnée du cabinet — c'est le document du client. Le
    # PAPIER À EN-TÊTE, lui, en porte forcément : un modèle fourni par un
    # conseil sort à l'en-tête de ce conseil, et l'y interdire reviendrait à
    # remettre un document anonyme. Le premier essai confondait les deux et
    # accusait le document d'une fuite qui était une signature.
    corps = _norm(docs["modele"]["doc"]["markdown"])

    # ELLE LIT `ORGANISME`, ELLE NE RECOPIE PAS SES CLÉS. La version d'origine
    # énumérait huit champs à la main : le jour où le SIRET a été ajouté au
    # cabinet, la règle est restée verte SANS LE VÉRIFIER — une fuite neuve
    # serait passée en silence, et c'est le pire moment pour qu'une règle
    # cesse de mesurer. Toute clé ajoutée ci-après est couverte d'office.
    #
    # LES TOLÉRANCES SONT NOMMÉES, JAMAIS IMPLICITES. Une valeur générique
    # (« SARL », « Gérant ») pourrait un jour figurer légitimement dans un
    # modèle vierge. Aucune ne le fait aujourd'hui — mesuré, les douze sont
    # absentes — donc la liste est vide. Si l'une venait à apparaître, cette
    # règle tomberait et quelqu'un devrait décider, ce qui est le bon geste.
    TOLEREES = ()
    interdits = {k: v for k, v in P.ORGANISME.items()
                 if k not in TOLEREES and str(v).strip()}
    fuites = {k: v for k, v in interdits.items() if _norm(v) in corps}
    assert not fuites, ("le CORPS du modèle vierge porte des données du "
                        "cabinet : %r" % fuites)
    assert len(interdits) >= 10, (
        "ORGANISME a maigri : la règle ne surveille plus que %d champ(s)"
        % len(interdits))
    # Et dans le PDF, ce qui ne figure sur AUCUN en-tête ne doit pas non plus
    # s'y trouver : un SIREN ou une TVA n'a rien à faire sur un papier à
    # en-tête, donc sa présence ne pourrait venir que du corps.
    t = docs["modele"]["texte"]
    # CE QU'UN PAPIER À EN-TÊTE NE PORTE JAMAIS. Un en-tête donne un nom, une
    # adresse, un contact ; il ne donne ni SIREN, ni SIRET, ni TVA, ni capital.
    # Leur présence dans le PDF ne pourrait donc venir que du corps.
    JAMAIS_SUR_UN_ENTETE = ("siren", "siret", "tva", "capital")
    dures = [P.ORGANISME[k] for k in JAMAIS_SUR_UN_ENTETE if P.ORGANISME.get(k)]
    assert len(dures) == len(JAMAIS_SUR_UN_ENTETE), (
        "un champ surveillé a disparu d'ORGANISME : %r" % (dures,))
    assert not [x for x in dures if _norm(x) in t], (
        "le PDF du modèle porte une donnée qui ne peut venir que du corps")


def test_le_modele_vierge_laisse_des_champs_a_remplir(docs):
    """LE TÉMOIN INVERSE. Un document qui n'aurait aucun crochet passerait la
    règle ci-dessus aussi bien qu'un vrai modèle — y compris s'il était vide."""
    t = docs["modele"]["texte"]
    assert t.count("[") >= 8, "trop peu de champs à remplir : %d" % t.count("[")
    assert "[Nom de l'entreprise]" in t, t[:300]


def test_la_politique_du_cabinet_porte_bien_ses_donnees(docs):
    """LE PENDANT : celle de CONSEILPREV est remplie, pas un modèle déguisé."""
    t = docs["conseilprev"]["texte"]
    for cle in ("nom", "siren", "representant", "adresse"):
        assert _norm(P.ORGANISME[cle]) in t, (
            "la politique du cabinet ne porte pas %s" % cle)
    assert "[Nom de l'entreprise]" not in t, "des crochets subsistent"


# ═══════════════════════════════════════════════════════════════════════════
#  4. LE FOND — CE QUE LA POLITIQUE DOIT DIRE POUR NE PAS ÊTRE FAUSSE
# ═══════════════════════════════════════════════════════════════════════════

def test_l_inventaire_distingue_ce_qui_est_de_l_IA_de_ce_qui_ne_l_est_pas(docs):
    """SUR-DÉCLARER EST UNE FAUTE AU MÊME TITRE QUE SOUS-DÉCLARER.

    On mesure les DEUX colonnes sur le document rendu : au moins un système
    déclaré génératif, au moins un déclaré non génératif. Une politique qui
    dirait « oui » partout ne distinguerait plus rien.
    """
    t = docs["conseilprev"]["texte"]
    generatifs = [s for s in P.SYSTEMES if s["ia"]]
    autres = [s for s in P.SYSTEMES if not s["ia"]]
    assert generatifs and autres, "l'inventaire a perdu sa distinction"
    # LA COLONNE SE MESURE LIGNE PAR LIGNE, PAS EN COMPTANT DES MOTS. Compter
    # « Oui » dans tout le document ne dit pas QUEL système est déclaré
    # génératif — et « Non » apparaît de toute façon dans le texte courant. On
    # vérifie donc que la mention suit immédiatement l'usage de CHAQUE système,
    # ce qui est exactement ce que porte la cellule.
    #
    # (Le premier essai cherchait « Oui » entouré d'espaces ; l'extraction du
    # PDF colle les cellules — « …du cabinet.Oui moyen » — et la règle tombait
    # sur un tableau parfaitement correct.)
    for sys_ in P.SYSTEMES:
        assert _norm(sys_["nom"]) in t, "système absent : %r" % sys_["nom"]
        u = _norm(sys_["usage"])
        assert u in t, "usage absent : %r" % sys_["nom"]
        suite = t[t.index(u) + len(u):].lstrip()
        attendu = "Oui" if sys_["ia"] else "Non"
        assert suite.startswith(attendu), (
            "« %s » devrait être déclaré « %s » ; le tableau dit : %r"
            % (sys_["nom"], attendu, suite[:20]))


def test_la_politique_du_cabinet_declare_le_cumul_des_roles(docs):
    """UNE POLITIQUE QUI DÉCRIT UNE ORGANISATION IMAGINAIRE NE PROTÈGE PERSONNE.

    Le gabarit répartit cinq rôles sur cinq personnes. Chez un cabinet à
    effectif très réduit ils se cumulent. L'écrire, avec ce que ce cumul coûte,
    est un acte de gouvernance ; inscrire cinq noms différents serait un faux.
    """
    t = docs["conseilprev"]["texte"]
    assert "cumul est assumé" in t, "le cumul des rôles n'est pas déclaré"
    for attendu in ("séparation des fonctions", "contre-pouvoir"):
        assert attendu in t, "le coût du cumul n'est pas nommé : %r" % attendu


def test_le_cadre_juridique_suit_le_pays(docs):
    """CONSEILPREV EST DE DROIT FRANÇAIS.

    Le gabarit d'origine était québécois : le laisser tel quel aurait fait se
    réclamer la politique d'un texte qui ne la régit pas — exactement la faute
    qu'une politique de conformité est censée empêcher.
    """
    t = docs["conseilprev"]["texte"]
    assert "RGPD" in t and "CNIL" in t, "le cadre européen n'est pas cité"
    for hors_sujet in ("Loi 25", "Commission d'accès à l'information"):
        assert hors_sujet not in t, (
            "la politique de CONSEILPREV se réclame de %r" % hors_sujet)
    # ET LE MODÈLE, LUI, DONNE LES DEUX — il ne sait pas où son lecteur est
    # établi, et trancher à sa place serait le piège inverse.
    m = docs["modele"]["texte"]
    assert "RGPD" in m and "Loi 25" in m, (
        "le modèle ne donne pas la correspondance entre les deux droits")


def test_la_verification_avant_livrable_est_exigee_en_source_primaire(docs):
    """C'EST LA SECTION QUI PORTE TOUT LE RESTE. Sans elle, la politique
    autorise l'usage sans exiger la relecture — et une référence inventée part
    chez un client."""
    for var in ("conseilprev", "modele"):
        t = docs[var]["texte"]
        assert "source primaire" in t, var
        assert "brouillon" in t.lower(), var


# ═══════════════════════════════════════════════════════════════════════════
#  5. LE DOCUMENT DIT CE QU'IL EST
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("var", ["conseilprev", "modele"])
def test_le_document_ne_se_marque_pas_produit_par_IA(docs, var):
    """Apposer « produit avec l'assistance d'une IA » sur la politique qui
    ORGANISE cet usage serait faux — et un marquage apposé partout ne signale
    plus rien. Mesuré dans les propriétés du fichier, pas dans le texte."""
    meta = docs[var]["pdf"].metadata
    sujet = str(meta.get("/Subject") or "")
    assert "deterministe" in sujet.lower(), sujet
    assert docs[var]["doc"]["meta"]["ia"] is False


def test_la_date_de_revision_est_deduite_pas_recopiee():
    """Douze mois après l'entrée en vigueur, calculés.

    Une date saisie à la main finit par annoncer douze mois quand il s'en est
    écoulé dix-huit : c'est le premier écart qu'un auditeur relève.
    """
    assert P._prochaine_revision(datetime.date(2026, 9, 12)) == \
        datetime.date(2027, 9, 12)
    # Le 29 février n'existe pas tous les ans : la déduction ne doit pas lever.
    assert P._prochaine_revision(datetime.date(2024, 2, 29)) == \
        datetime.date(2025, 2, 28)
    assert P._prochaine_revision(datetime.date(2026, 1, 31)) == \
        datetime.date(2027, 1, 31)


def test_deux_appels_le_meme_jour_rendent_le_meme_document():
    """Le module est PUR : la date lui est passée, il ne lit pas l'horloge.

    Sans cela, deux exports du même document à quelques heures d'écart
    différeraient, et l'empreinte d'un document signé ne voudrait plus rien
    dire.
    """
    a = P.politique("conseilprev", entree=JOUR)["markdown"]
    b = P.politique("conseilprev", entree=JOUR)["markdown"]
    assert a == b
    autre = P.politique("conseilprev", entree=datetime.date(2027, 1, 1))
    assert autre["markdown"] != a, "la date d'entrée ne change rien au document"


def test_une_variante_inconnue_est_refusee():
    """Refuser nommément vaut mieux que rendre un document au hasard."""
    with pytest.raises(ValueError):
        P.politique("autre")


# ═══════════════════════════════════════════════════════════════════════════
#  6. DEUX RÈGLES AJOUTÉES PARCE QUE DES MUTATIONS ONT SURVÉCU
# ═══════════════════════════════════════════════════════════════════════════

def test_le_drapeau_genératif_s_accorde_avec_le_motif_ecrit():
    """CE QUE LA RÈGLE PRÉCÉDENTE NE POUVAIT PAS VOIR.

    `test_l_inventaire_distingue…` mesure que le tableau dit la même chose que
    la table : une COHÉRENCE INTERNE. Basculer un moteur déterministe en
    « génératif » garde cette cohérence — le tableau suit — et la mutation
    survivait. Ce qui la démasque est le MOTIF, écrit à côté : un système dont
    la justification dit « formules déterministes » ou « aucun modèle
    n'intervient » ne peut pas être déclaré génératif, et réciproquement.

    C'est la seule chose qu'une règle puisse vérifier ici sans aller lire le
    code de chaque moteur : que les deux affirmations du document ne se
    contredisent pas.
    """
    mots_sans_ia = ("déterministe", "aucun modèle", "expression régulière",
                    "collecte et filtrage", "motifs d'expression")
    mots_avec_ia = ("génère", "modèle", "vecteur", "brouillon")
    for s in P.SYSTEMES:
        motif = s["motif"].lower()
        dit_sans = any(m in motif for m in mots_sans_ia)
        if s["ia"]:
            assert not dit_sans, (
                "« %s » est déclaré génératif mais son motif dit le contraire : "
                "%r" % (s["nom"], s["motif"]))
            assert any(m in motif for m in mots_avec_ia), (
                "« %s » est déclaré génératif sans que le motif dise en quoi"
                % s["nom"])
        else:
            assert dit_sans, (
                "« %s » est déclaré non génératif sans motif qui le justifie : "
                "%r" % (s["nom"], s["motif"]))


def test_le_document_annonce_une_revision_douze_mois_apres_son_entree(docs):
    """LA DÉDUCTION EST MESURÉE SUR LE DOCUMENT, PAS SUR LA FONCTION.

    `test_la_date_de_revision_est_deduite_pas_recopiee` éprouve
    `_prochaine_revision` en isolation. Remplacer son APPEL par la date
    d'entrée laissait cette règle verte — la fonction restait juste, elle
    n'était simplement plus utilisée. C'est le document qui doit porter la
    preuve : les deux dates y figurent, et leur écart se calcule.
    """
    for var in ("conseilprev", "modele"):
        t = docs[var]["texte"]
        dates = re.findall(r"\b(\d{2}/\d{2}/\d{4})\b", t)
        if var == "modele":
            # Le modèle porte des crochets, pas des dates : on vérifie qu'il
            # RAPPELLE la borne plutôt qu'il ne la calcule.
            assert "12 mois" in t, "le modèle ne rappelle pas la borne de révision"
            continue
        assert len(dates) >= 2, "le document ne porte pas ses deux dates : %r" % dates
        jour = lambda d: datetime.datetime.strptime(d, "%d/%m/%Y").date()
        entree, revision = jour(dates[0]), jour(dates[1])
        assert entree == JOUR, entree
        ecart = (revision.year - entree.year) * 12 + revision.month - entree.month
        assert ecart == P.REVISION_MOIS, (
            "le document annonce une révision à %d mois, la politique en "
            "promet %d" % (ecart, P.REVISION_MOIS))


# ═══════════════════════════════════════════════════════════════════════════
#  LE SIRET — TRANCHÉ PAR DÉCLARATION, VÉRIFIÉ PAR LE CALCUL
# ═══════════════════════════════════════════════════════════════════════════

def test_le_siret_porte_le_siren_et_passe_sa_cle():
    """Une faute de frappe sur quatorze chiffres part dans un document signé.

    CE QUE CETTE RÈGLE NE DIT PAS : que le numéro existe. Les DEUX valeurs qui
    circulaient pour ce cabinet passaient la clé — c'est bien un garde-fou de
    frappe, pas une vérification d'identité, et c'est pourquoi la question a
    été posée au gérant plutôt que tranchée par le calcul.
    """
    siren = re.sub(r"\D", "", P.ORGANISME["siren"])
    siret = re.sub(r"\D", "", P.ORGANISME["siret"])
    assert len(siret) == 14, siret
    assert siret.startswith(siren), (siret, siren)
    total, double = 0, False
    for c in reversed(siret):
        n = int(c)
        if double:
            n = n * 2 - (9 if n * 2 > 9 else 0)
        total += n
        double = not double
    assert total % 10 == 0, "clé de contrôle fausse : %s" % siret


def test_un_siret_incoherent_empeche_le_module_de_servir():
    """LE TÉMOIN NÉGATIF. Sans lui, la garde pourrait ne rien vérifier et la
    règle ci-dessus resterait verte — elle ne mesure que la valeur, pas le
    contrôle."""
    vrai = P.ORGANISME["siret"]
    for faux in ("494 530 157 00037",     # clé fausse
                 "123 456 789 00014",     # autre SIREN
                 "494 530 157 0003"):     # treize chiffres
        P.ORGANISME["siret"] = faux
        try:
            # `RuntimeError` et non `AssertionError` : c'est ce que la garde
            # lève réellement — mesuré, pas supposé. Écrire l'autre aurait
            # fait passer la règle pour verte le jour où la garde disparaît.
            with pytest.raises(RuntimeError) as leve:
                P._verifier()
            assert "SIRET" in str(leve.value), (
                "la garde lève, mais pas à cause du SIRET : %s" % leve.value)
        finally:
            P.ORGANISME["siret"] = vrai
    P._verifier()


def test_le_document_du_cabinet_s_identifie_par_son_ETABLISSEMENT(docs):
    """Le SIRET désigne un lieu où des gens travaillent ; le SIREN, une
    personne morale. Une politique s'applique au premier."""
    t = docs["conseilprev"]["texte"]
    assert _norm(P.ORGANISME["siret"]) in t, (
        "le SIRET ne figure pas dans le document du cabinet")
