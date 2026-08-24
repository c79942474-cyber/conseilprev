"""LES GABARITS BILINGUES — ce qui empêche les deux colonnes de diverger.

CE FICHIER GARDE UNE PROMESSE QUI VIENT DE CHANGER. Le site déclarait ne pas
traduire ses analyses, et disait pourquoi : elles sont dérivées par des règles,
et il n'existait de gabarits qu'en français. Il annonçait aussi le remède —
« des gabarits anglais, un vrai travail, pas un réglage ». Ils sont écrits.

CE QUI N'A PAS CHANGÉ, ET QUI EST GARDÉ ICI : aucune de ces phrases n'est
passée par une machine. Une traduction automatique aurait coûté une heure au
lieu d'une journée, et aurait fait de ce site exactement ce qu'il refuse à
chaque page — un texte dont personne ne répond.

CE QUI EST VÉRIFIÉ EST LA FORME, pas le sens : aucun contrôle ne peut dire si
une traduction est juste. Ce qui se vérifie, c'est qu'elle EXISTE, qu'elle
prend les mêmes arguments, et que la logique qui choisit les phrases ne s'est
pas dédoublée — trois défauts qui, eux, ne se voient pas à la relecture parce
qu'ils ne cassent que la colonne qu'on ne lit pas.
"""
import os
import re
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import gabarits as GB  # noqa: E402
import veille as V     # noqa: E402


def _lire(nom):
    return open(os.path.join(ICI, nom), encoding="utf-8").read()


# ── 1. La table ───────────────────────────────────────────────────────────

def test_chaque_gabarit_porte_ses_deux_colonnes():
    """Une entrée à une seule langue rendrait une chaîne vide au lecteur
    anglophone — un paragraphe blanc au milieu d'une fiche."""
    assert GB.defauts() == [], GB.defauts()
    assert len(GB.G) > 50, len(GB.G)


def test_les_deux_colonnes_prennent_les_MEMES_arguments():
    """Un `%s` oublié côté anglais lève une exception AU MOMENT DE LA COLLECTE
    — donc en production, et pour les seuls lecteurs anglophones. Et un ordre
    différent est pire : il ne lève rien, il intervertit."""
    for cle, (fr, en) in GB.G.items():
        assert GB._place(fr) == GB._place(en), (cle, GB._place(fr), GB._place(en))


def test_une_colonne_anglaise_n_est_jamais_la_copie_de_la_francaise():
    """Recopier le français dans la colonne anglaise ferait passer le contrôle
    précédent tout en ne traduisant rien. Les seules égalités admises sont les
    fragments qui n'ont pas de traduction — un sigle, un nom propre."""
    identiques = [c for c, (fr, en) in GB.G.items()
                  if fr == en and len(fr) > 24]
    assert not identiques, identiques


def test_aucune_bibliotheque_de_traduction_automatique():
    """La promesse tient dans le code, pas seulement dans le bandeau. Elle
    vaut pour ce fichier-ci autant que pour la chaîne de collecte : c'est ici
    qu'il aurait été le plus tentant de gagner une journée."""
    for nom in ("gabarits.py", "ingestion.py", "veille.py", "exporter.py"):
        src = _lire(nom).lower()
        for interdit in ("anthropic", "openai", "mistralai", "googletrans",
                         "deepl", "translate("):
            assert interdit not in src, "%s : %s" % (nom, interdit)


# ── 2. La logique de choix ne s'écrit qu'une fois ─────────────────────────

def test_les_lectures_composees_passent_par_l_accumulateur():
    """DEUX FONCTIONS PARALLÈLES AURAIENT FINI PAR NE PLUS CHOISIR LES MÊMES
    PHRASES DANS LES MÊMES CAS, et personne ne l'aurait vu — le français, lui,
    aurait continué à marcher. `Deux` accumule dans les deux colonnes en même
    temps, donc la condition ne s'écrit qu'une fois."""
    src = _lire("ingestion.py")
    # Chaque lecture composée conditionnellement passe par `GB.Deux()`.
    assert src.count("GB.Deux()") >= 4, src.count("GB.Deux()")
    # Et aucune n'assemble encore une liste de phrases à la main.
    assert "phrases.append(" not in src, "une lecture se compose hors gabarits"


def test_un_argument_de_texte_voyage_dans_les_deux_langues():
    """DÉFAUT CONSTATÉ AU PREMIER ESSAI : « The vendor falls within the
    industrial perimeter (éditeur au répertoire industriel du cabinet) ». Un
    argument qui est lui-même du texte doit être un couple, sinon la phrase
    anglaise porte du français en son milieu."""
    fr, en = GB.deux("kev.industriel", GB.deux("kev.motif.repertoire"))
    assert "répertoire industriel du cabinet" in fr
    assert "industrial directory" in en
    assert "répertoire" not in en, en


def test_un_argument_simple_reste_le_meme_des_deux_cotes():
    """Un nom propre, un identifiant, un nombre : pas de couple, pas de
    traduction, et surtout pas d'erreur."""
    fr, en = GB.deux("attack.groupe.titre", "APT38", " (G0082)")
    assert "APT38" in fr and "APT38" in en


# ── 3. La couverture, mesurée sur le corpus réel ──────────────────────────

def test_chaque_collecteur_produit_ses_trois_champs_en_anglais():
    """La couverture n'est pas déclarée, elle est constatée. Un collecteur
    ajouté demain sans gabarits anglais fera tomber ce contrôle — ce qui est
    exactement ce qu'on veut, plutôt qu'une fiche à moitié française servie en
    silence."""
    import ingestion as I
    corpus = I.collecter_tout(limite_kev=4)["corpus"]
    assert len(corpus) > 40, len(corpus)
    manquantes = {}
    for f in corpus:
        for c in V.CHAMPS_TRADUITS:
            if not (f.get(c + "_en") or "").strip():
                cle = f.get("source_cle") or "?"
                manquantes.setdefault(cle, set()).add(c)
    assert not manquantes, manquantes


def test_la_mesure_de_couverture_suit_le_corpus():
    import ingestion as I
    lg = V.langues(I.collecter_tout(limite_kev=4)["corpus"])
    assert lg["analyses_total"] == lg["analyses_traduites"]
    assert lg["complet"] is True
    assert lg["manquantes_par_source"] == {}


# ── 4. La vue anglaise ne laisse pas de reste français ────────────────────

def test_la_vue_anglaise_remplace_aussi_les_libelles_du_referentiel():
    """DÉFAUT CONSTATÉ : « Reading — Lecture dérivée par règles » en tête du
    document exporté. Le pire des mélanges, parce qu'il se lit comme une
    citation et qu'il n'en est pas une."""
    import ingestion as I
    f = V.dans(I.collecter_owasp_llm(limite=1)["fiches"][0], "en")
    assert f["lecture_nom"] == V.LECTURES["regle"]["nom_en"]
    assert f["statut_nom"] == V.STATUTS["verifiee_source_primaire"]["nom_en"]
    assert "Lecture" not in f["lecture_nom"]
    # La glose aussi : elle est affichée sous chaque fiche.
    assert "règles écrites" not in (f.get("lecture_dit") or "")


def test_chaque_glose_du_referentiel_a_sa_colonne_anglaise():
    """Elles s'affichent sous les fiches et dans les infobulles de la légende.
    Une seule oubliée met une phrase française sous un texte anglais."""
    manque = []
    for nom, table in (("STATUTS", V.STATUTS), ("LECTURES", V.LECTURES),
                       ("IMPACTS", V.IMPACTS), ("HORIZONS", V.HORIZONS)):
        for cle, e in table.items():
            if e.get("dit") and not e.get("dit_en"):
                manque.append("%s.%s" % (nom, cle))
            if e.get("nom") and not e.get("nom_en"):
                manque.append("%s.%s (nom)" % (nom, cle))
    assert not manque, manque


def test_chaque_source_a_sa_licence_en_anglais():
    """Elle est affichée sous chaque fiche et dans chaque document emporté."""
    import sources as SRC
    manque = [c for c, s in SRC.SOURCES.items() if not s.get("licence_en")]
    assert not manque, manque


def test_le_document_emporte_est_dans_la_langue_ou_il_a_ete_lu():
    """Un PDF exporté depuis une interface anglaise avec « Ce qu'on ne sait
    pas » au milieu est pire qu'un document entièrement français : le lecteur
    qui le reçoit ne sait plus dans quelle langue est le texte qu'il n'a pas
    encore lu."""
    import exporter as EXP
    import ingestion as I
    f = V.dans(I.collecter_owasp_llm(limite=1)["fiches"][0], "en")
    textes = [t for _, t in EXP.blocs(f, "https://exemple/x", "en")]
    entier = " ".join(textes)
    for reste in ("Ce que cela change", "Ce qu'on ne sait pas", "La source",
                  "Statut :", "Exporté de", "Document d'origine",
                  "janvier", "février", "août"):
        assert reste not in entier, reste
    # ET IL DIT SA LANGUE : il circule sans sa page, six mois plus tard.
    assert "English version" in entier


def test_le_document_francais_reste_francais():
    """La bascule ne doit pas emporter le français avec elle."""
    import exporter as EXP
    import ingestion as I
    f = I.collecter_owasp_llm(limite=1)["fiches"][0]
    entier = " ".join(t for _, t in EXP.blocs(f, None, "fr"))
    assert "Ce qu'on ne sait pas" in entier
    assert "What is not known" not in entier
    assert "Version française" in entier


# ── 5. Le réglage du lecteur ──────────────────────────────────────────────

def test_la_langue_des_analyses_est_distincte_de_celle_de_l_interface():
    """Un francophone qui travaille en anglais veut souvent l'interface en
    anglais ET les analyses dans leur version d'origine. Une seule bascule
    déciderait à sa place — et « ou pas » n'existerait plus."""
    lg = _lire("langue.js")
    assert 'CLE_ANALYSES = "cpinfo.analyses"' in lg
    assert "function analyses()" in lg
    # Le défaut SUIT l'interface : un réglage jamais touché se comporte comme
    # on l'attend, sans rien régler.
    i = lg.index("function analyses()")
    assert "return courante();" in lg[i:i + 400], lg[i:i + 400]
    # Et un choix explicite prime.
    assert "function choisirAnalyses(" in lg


def test_le_serveur_ne_traduit_que_sur_demande_explicite():
    """Un paramètre absent ne doit jamais faire servir une traduction que
    personne n'a demandée : le français est la langue d'écriture de ce site."""
    src = _lire("app.py")
    i = src.index("def _langue_analyses()")
    bloc = src[i:i + 900]
    assert '"en" if (request.args.get("analyses") or "").lower() == "en" else "fr"' \
        in bloc, bloc[-300:]


def test_la_langue_ne_part_pas_dans_l_adresse_partagee():
    """Collée dans l'adresse, elle voyagerait avec chaque lien partagé et
    imposerait au destinataire la langue de l'expéditeur."""
    js = _lire("veille.js")
    assert "parametres(true)" in js
    # LA FENÊTRE EST LA FONCTION, PAS NEUF CENTS CARACTÈRES. Le compte était
    # arbitraire : un commentaire ajouté dans `parametres()` a suffi à pousser
    # la ligne cherchée hors de la fenêtre, et le contrôle est tombé sur un
    # code qui tenait toujours sa promesse. Un contrôle qui se déclenche sur
    # la longueur d'un commentaire n'apprend rien à personne.
    i = js.index("function parametres(")
    corps = js[i:js.index("\n  }", i)]
    assert "if (!pourAdresse && langueAnalyses() === \"en\")" in corps, corps


def test_une_fiche_non_traduite_le_dit_sur_elle_meme():
    """Le bandeau de tête annonce la réserve pour tout le corpus ; il ne dit
    pas LAQUELLE des soixante cartes à l'écran est concernée. Sans repère, un
    lecteur anglophone tombe sur un paragraphe français au milieu de la page
    et en conclut que le site est cassé."""
    for nom in ("veille.js", "fiche.js"):
        js = _lire(nom)
        assert "analyses_traduites === false" in js, nom
        assert 'tr("an.repli")' in js, nom
    assert '"an.repli"' in _lire("langue.js")
    # Et le repère porte `lang="fr"` : un lecteur d'écran anglophone doit
    # changer de voix, pas prononcer du français à l'anglaise.
    assert 'class="an-r" lang="fr"' in _lire("veille.js")


def test_le_serveur_dit_par_fiche_si_elle_a_pu_suivre():
    """Le client ne le déduit pas de la présence d'un champ : c'est le serveur
    qui détient les deux colonnes, et lui seul sait laquelle existe."""
    f = V.dans({"lecture": "a", "portee": "b", "incertitude": "c"}, "en")
    assert f["analyses_traduites"] is False and f["langue_analyses"] == "fr"
    g = V.dans({"lecture": "a", "portee": "b", "incertitude": "c",
                "lecture_en": "A", "portee_en": "B", "incertitude_en": "C"}, "en")
    assert g["analyses_traduites"] is True and g["langue_analyses"] == "en"
    assert g["lecture"] == "A"
