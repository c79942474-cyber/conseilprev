"""LA REVUE — ce qu'elle compte, et les quatre façons dont elle pourrait mentir.

UNE REVUE DE PRESSE EST UN GENRE DANGEREUX. Elle a l'autorité d'un résumé : le
lecteur lui accorde d'avoir vu ce qu'il n'a pas lu. Quatre glissements
suffisent à la rendre fausse sans qu'aucune ligne ne soit inexacte :

  1. COMPTER SUR LA MAUVAISE DATE. Bâtie sur la date de collecte, elle
     titrerait « la semaine du 17 août » au-dessus de faits de 2021.
  2. LAISSER LES DATES DE CONVENTION GONFLER UNE PÉRIODE. Une quinzaine de
     fiches datées du 1er janvier faute de mieux feraient de janvier le mois
     le plus fourni de l'année.
  3. APPELER « INTERNATIONAL » CE QU'ON N'A PAS DÉFINI. Sans règle écrite, la
     sélection ne se discute pas : elle se croit.
  4. NE MONTRER QUE CE QU'ON A TROUVÉ. Une revue qui n'affiche que ses
     rubriques fécondes enseigne une couverture qu'elle n'a pas.

Et une cinquième, la seule qui porte sur des personnes : FABRIQUER LES
REPORTAGES ET LES ENTRETIENS. Le registre est vide, et il refuse de s'ouvrir
sur une pièce non signée.
"""
import os
import re
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import redaction as RED  # noqa: E402
import revue as R  # noqa: E402
import veille as V  # noqa: E402


def _lire(nom):
    return open(os.path.join(ICI, nom), encoding="utf-8").read()


def _sans_commentaires(texte):
    """LES COMMENTAIRES PARLENT DES MOTS INTERDITS — c'est leur travail : ils
    disent pourquoi « en hausse » a été écarté. Les compter comme du code est
    une faute de contrôle, et elle a été commise au premier essai ici même :
    le contrôle accusait la page d'écrire le mot que le commentaire d'à côté
    expliquait avoir refusé."""
    return re.sub(r"/\*.*?\*/", "", texte, flags=re.S)


def _fiche(**kw):
    base = {
        "id": "essai-revue", "titre": "Titre", "chapeau": "Chapeau.",
        "lecture": "L" * 100, "lecture_nature": "regle",
        "portee": "P" * 80, "incertitude": "I" * 60,
        "sujet": "cyber_industriel", "date_fait": "2026-01-15",
        "source_cle": "cisa_kev", "source_url": "https://www.cisa.gov/x",
        "statut": "verifiee_source_primaire", "impact": "structurant",
        "horizon": "constate",
    }
    base.update(kw)
    r = V.normaliser(base)
    assert r.get("ok"), r
    return r["fiche"]


# ══ 1. LA DATE COMPTÉE EST CELLE DU FAIT ═════════════════════════════════

def test_la_revue_compte_la_date_du_fait_et_non_celle_de_la_collecte():
    """LE GLISSEMENT LE PLUS FACILE, ET LE PLUS TROMPEUR. Les deux dates
    existent et ne coïncident pas : CISA inscrit au catalogue une faille
    exploitée depuis des mois, MITRE publie en août l'étude d'un incident de
    janvier. Une revue bâtie sur la collecte titrerait la semaine en cours
    au-dessus de faits vieux de cinq ans."""
    dedans = _fiche(id="r-1", date_fait="2026-01-15")
    dehors = _fiche(id="r-2", date_fait="2025-11-03")
    d = R.revue([dedans, dehors], "semaine", "2026-01-15")
    ids = [f["id"] for b in d["blocs"] for f in b["fiches"]]
    assert ids == ["r-1"], ids
    # Et le module ne lit AUCUN champ de collecte pour découper.
    src = _lire("revue.py")
    for interdit in ("collecte_le", "date_collecte", "collectes"):
        assert interdit not in src, interdit


def test_la_semaine_est_celle_de_la_norme_iso():
    """Une « semaine glissante de sept jours » aurait produit des revues qui
    se chevauchent, et deux revues successives auraient compté deux fois les
    mêmes faits."""
    p = R.periode("semaine", "2026-01-15")     # un jeudi
    assert (p["debut"], p["fin"]) == ("2026-01-12", "2026-01-18")
    # Le lundi appartient à SA semaine, pas à la précédente.
    assert R.periode("semaine", "2026-01-12")["debut"] == "2026-01-12"


def test_la_periode_precedente_se_calcule_sur_ses_bornes():
    """L'INVARIANT EST CELUI-CI, ET IL EST LE SEUL QUI TIENNE POUR LES DEUX
    GENRES : la période précédente est celle qui contient LA VEILLE DU DÉBUT.
    Un décalage d'un nombre fixe de jours — « moins trente » pour un mois —
    saute février une année sur deux et rate janvier depuis le 1er mars.

    ÉCRIT D'ABORD AUTREMENT, ET C'ÉTAIT MAL DIT : le contrôle prétendait que
    « moins sept jours » cassait. Il ne casse pas, puisqu'on retranche du
    DÉBUT et non d'une ancre quelconque — la veille du 1er mars et le 22
    février sont tous deux en février. Un contrôle doit garder ce que le code
    promet, pas une version dramatisée de sa promesse."""
    for genre, ancre, bornes, avant in (
            ("mois", "2026-03-10", ("2026-03-01", "2026-03-31"),
             ("2026-02-01", "2026-02-28")),
            ("mois", "2026-01-05", ("2026-01-01", "2026-01-31"),
             ("2025-12-01", "2025-12-31")),
            ("semaine", "2026-01-15", ("2026-01-12", "2026-01-18"),
             ("2026-01-05", "2026-01-11"))):
        p = R.periode(genre, ancre)
        assert (p["debut"], p["fin"]) == bornes, genre
        q = R.precedente(p)
        assert (q["debut"], q["fin"]) == avant, genre
        # L'INVARIANT LUI-MÊME : la précédente finit la veille du début.
        assert R._jour(q["fin"]) == R._jour(p["debut"]) - R.timedelta(days=1)


# ══ 2. LES DATES DE CONVENTION NE GONFLENT AUCUNE PÉRIODE ════════════════

def test_les_dates_posees_sont_ecartees_et_comptees():
    """Une partie du corpus porte une date POSÉE par ce site faute de mieux —
    un mix électrique annuel devient le 1er janvier. Elles tomberaient toutes
    dans la même semaine. Les écarter en silence ferait disparaître des fiches
    réelles ; les garder ferait de janvier le mois le plus fourni de
    l'année."""
    vraie = _fiche(id="r-3", date_fait="2026-01-01")
    posee = _fiche(id="r-4", date_fait="2026-01-01",
                   date_convention="année 2025",
                   date_convention_dit="Le jeu de données est annuel.")
    d = R.revue([vraie, posee], "semaine", "2026-01-01")
    ids = [f["id"] for b in d["blocs"] for f in b["fiches"]]
    assert ids == ["r-3"], ids
    assert d["conventions_ecartees"] == 1
    # ET L'ÉCRAN LE DIT — un compte servi que personne n'affiche ne garde rien.
    assert "rv.conv" in _lire("revue.js")


# ══ 3. « INTERNATIONALE » EST UNE RÈGLE ÉCRITE ═══════════════════════════

def test_la_regle_internationale_est_servie_avec_la_selection():
    """Une sélection dont on ignore le critère ne se discute pas : elle se
    croit. La règle voyage donc avec la revue, dans les deux langues."""
    d = R.revue([_fiche(id="r-5", pays=["DE"])], "mois", "2026-01-15",
                international=True)
    assert d["regle_internationale"] == R.REGLE_INTERNATIONALE[0]
    e = R.revue([_fiche(id="r-5", pays=["DE"])], "mois", "2026-01-15",
                international=True, langue="en")
    assert e["regle_internationale"] == R.REGLE_INTERNATIONALE[1]
    # La revue hebdomadaire ne l'applique pas : elle ne l'annonce donc pas.
    assert R.revue([], "semaine", "2026-01-15")["regle_internationale"] is None
    assert "rv-regle" in _lire("revue.js")


def test_les_trois_etats_du_territoire_sont_distincts():
    """`None` N'EST PAS `False`. Une fiche que rien ne rattache à un territoire
    n'est pas française : elle est SANS territoire. Les confondre ferait
    passer la moitié du corpus pour nationale — mesuré : quarante-quatre
    fiches sur quatre-vingt-huit ne portent ni pays ni entreprise."""
    assert R._international(_fiche(id="r-6", pays=["DE"])) is True
    assert R._international(_fiche(id="r-7", pays=["FR"])) is False
    assert R._international(_fiche(id="r-8")) is None
    # Le siège d'une entreprise nommée suffit, et il suffit seul.
    assert R._international(_fiche(id="r-9", organisations=["siemens"])) is True
    assert R._international(_fiche(id="r-a", organisations=["schneider"])) is False


def test_ce_qui_est_ecarte_de_la_revue_internationale_est_compte():
    """Les taire ferait disparaître des fiches réelles du corpus, sans un
    mot — et laisserait croire que la période ne portait que cela."""
    c = [_fiche(id="r-b", pays=["DE"]),
         _fiche(id="r-c", pays=["FR"]),
         _fiche(id="r-d")]
    d = R.revue(c, "mois", "2026-01-15", international=True)
    assert d["n"] == 1
    assert d["ecartees_france"] == 1
    assert d["ecartees_sans_territoire"] == 1
    js = _lire("revue.js")
    assert "rv.fr" in js and "rv.hors" in js


def test_l_ancre_par_defaut_suit_la_regle_de_la_revue_demandee():
    """Mesuré sur le corpus servi : le mois le plus récent ne porte AUCUNE
    fiche hors de France. Ouvrir la revue internationale sur ce mois-là
    servirait une page vide alors que le corpus en documente d'autres, et le
    lecteur conclurait que la rubrique ne marche pas."""
    c = [_fiche(id="r-e", date_fait="2026-07-15"),               # sans territoire
         _fiche(id="r-f", date_fait="2026-03-10", pays=["DE"])]  # international
    assert R.derniere_ancre(c, "mois") == "2026-07-15"
    assert R.derniere_ancre(c, "mois", international=True) == "2026-03-10"


# ══ 4. CE QUE LA PÉRIODE NE DIT PAS ══════════════════════════════════════

def test_les_sujets_muets_sont_nommes():
    """Une revue qui n'affiche que ses rubriques fécondes enseigne au lecteur
    une couverture qu'elle n'a pas."""
    c = [_fiche(id="r-g", sujet="cyber_industriel", date_fait="2026-01-15"),
         _fiche(id="r-h", sujet="ia", date_fait="2025-06-02")]
    d = R.revue(c, "semaine", "2026-01-15")
    assert [m["cle"] for m in d["muets"]] == ["ia"]


def test_un_sujet_absent_du_corpus_n_est_pas_reproche_a_la_periode():
    """Nommer tous les sujets du référentiel reprocherait à la semaine un
    silence qui est celui du corpus entier — et la liste serait la même chaque
    semaine, donc muette."""
    d = R.revue([_fiche(id="r-i", sujet="cyber_industriel")], "semaine",
                "2026-01-15")
    assert d["muets"] == []


def test_une_periode_vide_le_dit_plutot_que_de_se_taire():
    """Et elle ne dit pas « il ne s'est rien passé » : les sept collecteurs ne
    couvrent pas tout, et cette page ne peut parler que de ce qu'ils
    rapportent."""
    d = R.revue([_fiche(id="r-j", date_fait="2025-01-02")], "semaine",
                "2026-01-15")
    assert d["n"] == 0 and d["blocs"] == []
    js, dic = _lire("revue.js"), _lire("langue.js")
    assert "rv.vide" in js
    i = dic.index('"rv.vide2"')
    assert "il ne s'est rien passé" in dic[i:i + 400]


def test_le_retard_est_dit_en_deux_nombres():
    """Le premier situe la période par rapport à aujourd'hui ; le second dit
    jusqu'où le CORPUS va. Sans le second, un lecteur qui ouvre une revue de
    juillet en août croit la page en retard, alors que c'est le corpus qui
    s'arrête là — et c'est une information sur les sources."""
    d = R.revue([_fiche(id="r-k", date_fait="2026-01-15")], "semaine",
                "2026-01-15")
    t = d["retard"]
    assert t["dernier_fait"] == "2026-01-15"
    assert t["jours_depuis_la_fin"] is not None
    assert t["jours_depuis_le_dernier_fait"] is not None
    assert "rv.retard" in _lire("revue.js")


def test_l_ecart_avec_la_periode_precedente_est_un_nombre_pas_une_tendance():
    """« En hausse » sur deux points serait une affirmation que rien ne
    fonde."""
    c = [_fiche(id="r-l", date_fait="2026-01-15"),
         _fiche(id="r-m", date_fait="2026-01-06"),
         _fiche(id="r-n", date_fait="2026-01-07")]
    d = R.revue(c, "semaine", "2026-01-15")
    assert d["precedente"]["n"] == 2 and d["precedente"]["ecart"] == -1
    js = _sans_commentaires(_lire("revue.js")).lower()
    for mot in ("hausse", "baisse", "tendance", "forte", "record"):
        assert mot not in js, mot


# ══ 5. LA REVUE NE COMMENTE PAS, ET NE PUBLIE RIEN DE NON SIGNÉ ══════════

def test_la_revue_n_ajoute_aucune_phrase_d_appreciation():
    """Une revue de presse qui commente cesse d'en être une. Le classement par
    portée est celui du moteur, déjà publié sur chaque fiche."""
    src = _lire("revue.py")
    assert "modeles_de_langage" in src
    for interdit in ("openai", "anthropic.com", "gpt", "llm(", "prompt"):
        assert interdit not in src.lower(), interdit
    # L'ORDRE EST CELUI DU MOTEUR, repris et non recalculé.
    assert "V.IMPACTS" in src and "V.ORDRE_IMPACTS" in src


def test_le_registre_des_pieces_signees_est_vide_et_le_dit():
    """Servir une revue sans ces rubriques laisserait croire qu'elles n'ont
    pas été demandées, ou qu'un mensuel de veille n'en porte pas. Elles
    existent, elles sont vides, elles disent pourquoi et ce qu'il faudrait."""
    assert RED.PIECES == ()
    d = R.revue([], "mois", "2026-01-15")
    natures = [r["nature"] for r in d["rubriques"]]
    assert natures == list(RED.ORDRE_NATURES)
    for r in d["rubriques"]:
        assert r["n"] == 0
        assert r["vide_motif"] and r["ce_qu_il_faudrait"]
    assert "rv-rub-v" in _lire("revue.js")


def test_une_piece_non_signee_ne_peut_pas_entrer_au_registre():
    """Une pièce mal formée ne se voit pas à l'écran : elle s'y voit comme un
    article normal, avec l'autorité d'un article normal. C'est précisément le
    cas où l'erreur doit être bruyante — et ce contrôle vérifie que le refus
    FONCTIONNE, plutôt que de faire confiance à sa présence."""
    bonne = {
        "cle": "p1", "nature": "reportage", "titre": "T", "chapeau": "C",
        "texte": "X", "auteur": "Une Personne", "date": "2026-01-15",
        "methode": "Sur place.", "sources": ["https://x"],
    }
    entretien = dict(bonne, cle="p2", nature="entretien",
                     interlocuteur="Quelqu'un", fonction="Directeur",
                     date_entretien="2026-01-14", accord=True)

    garde = RED.PIECES
    fautes = [
        # sans auteur nommé : « la rédaction » n'est pas une signature
        (dict(bonne, auteur="La rédaction"),),
        # sans source vérifiable : un reportage sans source est un récit
        (dict(bonne, sources=[]),),
        # UNE SOURCE QUI N'EST PAS UNE LISTE. « https://x » est une chaîne
        # non vide : elle passe le contrôle des champs obligatoires, et
        # l'écran en tirerait une liste de vingt-trois lettres.
        (dict(bonne, sources="https://x"),),
        # sans méthode : le lecteur ne peut pas peser ce qu'il lit
        (dict(bonne, methode=""),),
        # une date qui n'en est pas une
        (dict(bonne, date="l'an dernier"),),
        # un entretien sans accord de publication : condition de droit
        (dict(entretien, accord=False),),
        # UN ACCORD QUI N'EN EST PAS UN. « En attente » est vrai au sens de
        # Python et faux au sens du droit : dans le doute, on ne publie pas.
        # Sans cette ligne, la mutation qui remplace le contrôle d'accord par
        # `if False:` survivait — le champ obligatoire suffisait à attraper le
        # `False`, mais pas la chaîne.
        (dict(entretien, accord="en attente"),),
        # un entretien sans interlocuteur nommé
        (dict(entretien, interlocuteur=""),),
        # deux fois la même clé
        (bonne, dict(bonne)),
    ]
    try:
        # La pièce bien formée, elle, passe — sinon ce contrôle ne prouverait
        # que l'existence d'un refus indistinct.
        RED.PIECES = (bonne, entretien)
        RED._verifier()
        for f in fautes:
            RED.PIECES = f
            try:
                RED._verifier()
            except ValueError:
                continue
            raise AssertionError("pièce non signée acceptée : %r" % (f[-1],))
    finally:
        RED.PIECES = garde
    RED._verifier()


def test_la_rubrique_cesse_d_annoncer_son_vide_des_qu_elle_a_une_piece():
    """Sans quoi la page continuerait d'annoncer une absence démentie par le
    texte juste au-dessus."""
    garde = RED.PIECES
    try:
        RED.PIECES = ({
            "cle": "p9", "nature": "reportage", "titre": "T", "chapeau": "C",
            "texte": "X", "auteur": "Une Personne", "date": "2026-01-15",
            "methode": "Sur place.", "sources": ["https://x"],
        },)
        r = RED.rubrique("reportage", "fr", "2026-01-01", "2026-01-31")
        assert r["n"] == 1
        assert r["vide_motif"] is None and r["ce_qu_il_faudrait"] is None
        assert r["pieces"][0]["signe"] is True
        # HORS FENÊTRE, elle redit son vide : la rubrique parle de LA PÉRIODE.
        vide = RED.rubrique("reportage", "fr", "2026-02-01", "2026-02-28")
        assert vide["n"] == 0 and vide["vide_motif"]
    finally:
        RED.PIECES = garde


def test_un_corpus_vide_ne_se_lit_pas_comme_une_periode_vide():
    """CONSTATÉ AU NAVIGATEUR, SUR UN SERVEUR QUI VENAIT DE DÉMARRER. La
    première visite tombait avant la fin de la collecte : `ancre` valait donc
    `None`, la revue s'ouvrait sur la semaine EN COURS, et la page annonçait
    « aucun fait daté de cette période n'est entré au corpus ». La phrase était
    exacte et la page ne l'était pas — le lecteur en tirait un jugement sur le
    silence des sources, alors que rien n'avait encore été lu.

    C'est le pire des deux vides : celui qui ressemble à une information."""
    assert R.revue([], "semaine", "2026-01-15")["corpus_vide"] is True
    assert R.revue([_fiche(id="r-o")], "semaine", "2026-01-15")["corpus_vide"] is False
    js = _lire("revue.js")
    assert "corpus_vide" in js and "rv.nocorpus" in js


def test_la_plus_recente_ne_se_dit_que_si_elle_l_est():
    """CONSTATÉ AU NAVIGATEUR AUSSI : la phrase « c'est la plus récente que le
    corpus documente » restait affichée après un clic sur « période
    précédente », au-dessus d'une semaine vide qui n'était évidemment pas la
    plus récente. Une réserve qui suit le lecteur sans se vérifier cesse d'être
    une réserve : elle devient une affirmation fausse."""
    c = [_fiche(id="r-p", date_fait="2026-01-15")]
    assert R.revue(c, "semaine", "2026-01-15")["retard"]["est_la_plus_recente"]
    assert not R.revue(c, "semaine", "2026-01-08")["retard"]["est_la_plus_recente"]
    js = _lire("revue.js")
    assert "est_la_plus_recente" in js
    assert "rv.retard.ancienne" in js


def test_la_pastille_de_la_revue_ne_ment_pas_sur_le_code_de_couleur():
    """VU À L'ÉCRAN : la carte affichait le nom du SUJET dans la couleur de la
    PORTÉE — « Cybersécurité industrielle » peint en ambre parce que la fiche
    est structurante. Le code que la légende enseigne (rouge la rupture, bleu
    le sujet) était démenti sur chaque carte de cette page.

    La portée est déjà donnée par l'intertitre qui coiffe le bloc ; la
    répéter sur chaque carte n'apprendrait rien."""
    js = _sans_commentaires(_lire("revue.js"))
    assert '<span class="past sujet">' in js
    assert 'class="past ' + "' + esc(f.impact)" not in js


# ══ 7. LA REVUE EMPORTÉE ══════════════════════════════════════════════════

import exporter as E  # noqa: E402


def _revue(**kw):
    c = kw.pop("corpus", [_fiche(id="r-x1", date_fait="2026-01-15"),
                          _fiche(id="r-x2", date_fait="2026-01-16",
                                 impact="rupture", pays=["DE"])])
    return R.revue(c, kw.pop("genre", "semaine"), kw.pop("ancre", "2026-01-15"),
                   **kw)


def test_le_document_porte_ce_que_la_revue_compte():
    """LA RÈGLE LA PLUS IMPORTANTE DE CE MODULE, ET ELLE MORD DEUX FOIS PLUS
    ICI QU'À L'ÉCRAN. Une revue de presse est le document qui circule le
    plus : transférée, jointe à un ordre du jour, lue en comité par des gens
    qui n'ouvriront jamais le site. Elle a l'autorité d'un résumé — le lecteur
    lui accorde d'avoir vu ce qu'il n'a pas lu.

    Sans cette phrase EN TÊTE, « Revue de la semaine du 12 janvier » se lit
    comme « l'actualité de cette semaine-là », alors que c'est « les faits
    DATÉS de cette semaine et entrés au corpus »."""
    lot = E.blocs_revue(_revue())
    genres = [g for g, _ in lot]
    textes = [t for _, t in lot]
    assert genres[0] == "entete" and genres[1] == "titre"
    compte = next(i for i, t in enumerate(textes) if "CE QUE CETTE REVUE COMPTE" in t)
    # EN TÊTE, PAS EN ANNEXE : reléguée en pied, elle arriverait après la
    # décision. On exige qu'elle précède la première entrée.
    premiere = next(i for i, g in enumerate(genres) if g == "titre2")
    assert compte < premiere, (compte, premiere)


def test_le_document_emporte_ce_que_la_revue_ecarte():
    """Trois comptes qui, absents, feraient croire que la période ne portait
    que ce qui est imprimé. Un PDF « propre » est exactement le PDF qui les
    perd."""
    c = [_fiche(id="r-y1", date_fait="2026-01-15", pays=["DE"]),
         _fiche(id="r-y2", date_fait="2026-01-15", pays=["FR"]),
         _fiche(id="r-y3", date_fait="2026-01-15"),
         _fiche(id="r-y4", date_fait="2026-01-15", date_convention="année 2025",
                date_convention_dit="Le jeu de données est annuel.")]
    rv = R.revue(c, "mois", "2026-01-15", international=True)
    texte = " ".join(t for _, t in E.blocs_revue(rv))
    assert "Dates posées, écartées : 1" in texte
    assert "Sans territoire, écartées : 1" in texte
    assert "France seulement, écartées : 1" in texte
    # ET LA RÈGLE QUI A PRÉSIDÉ À LA SÉLECTION.
    assert "LA RÈGLE DE SÉLECTION" in texte


def test_le_document_porte_les_deux_rubriques_vides():
    """Un PDF qui les omettrait serait la version « propre » de la revue — et
    il aurait perdu la seule chose qu'elle dise d'elle-même : qu'elle ne
    contient ni reportage ni entretien, et pourquoi."""
    texte = " ".join(t for _, t in E.blocs_revue(_revue()))
    assert "Aucun reportage n'a été mené" in texte
    assert "Aucun entretien n'a été conduit" in texte
    # ET CE QU'IL FAUDRAIT — un manque sans remède se lit comme un renoncement.
    assert "doit aller constater un fait et le signer" in texte


def test_chaque_entree_du_document_porte_sa_source_et_son_statut():
    """Une revue qui aligne douze titres sans dire d'où ils viennent est une
    revue de presse au sens le plus creux du mot — et c'est celle-là qui
    circule en comité."""
    lot = E.blocs_revue(_revue())
    textes = [t for _, t in lot]
    assert sum(1 for t in textes if t.startswith("Statut :")) == 2


def test_le_document_ne_reecrit_aucun_texte():
    """Ce qui sort est ce qui est publié — sans quoi il existerait deux
    versions d'une même revue, et rien ne dirait laquelle fait foi."""
    f = _fiche(id="r-z1", date_fait="2026-01-15", titre="Un titre précis",
               chapeau="Un chapeau qui dit exactement ceci.")
    rv = R.revue([f], "semaine", "2026-01-15")
    textes = [t for _, t in E.blocs_revue(rv)]
    assert any("Un titre précis" in t for t in textes)
    assert "Un chapeau qui dit exactement ceci." in textes


def test_le_document_est_dans_la_langue_ou_il_a_ete_lu():
    """Un PDF anglais avec « Ce que cette revue compte » au milieu est pire
    qu'un document entièrement français : celui qui le reçoit ne sait plus
    dans quelle langue est le texte qu'il n'a pas encore lu."""
    rv = R.revue([_fiche(id="r-z2", date_fait="2026-01-15")], "semaine",
                 "2026-01-15", langue="en")
    textes = " ".join(t for _, t in E.blocs_revue(rv, None, "en"))
    assert "WHAT THIS REVIEW COUNTS" in textes
    assert "CE QUE CETTE REVUE COMPTE" not in textes
    assert "English version" in textes


def test_les_deux_formats_composent_le_meme_document():
    """Deux compositions séparées auraient divergé : le jour où l'on ajoute un
    champ, l'un des deux formats l'aurait porté et l'autre non — et personne
    ne s'en apercevrait, puisque personne n'ouvre les deux."""
    src = _lire("exporter.py")
    assert "def _docx(" in src and "def _pdf(" in src
    assert "_docx(blocs_revue(" in src and "_pdf(blocs_revue(" in src
    assert "_docx(blocs(" in src and "_pdf(blocs(" in src
    rv = _revue()
    assert len(E.docx_revue(rv)) > 1000
    ok, _ = E.pdf_disponible()
    if ok:
        assert len(E.pdf_revue(rv)) > 1000


def test_le_nom_du_fichier_distingue_les_revues_entre_elles():
    """Un dossier de comité en accumule douze : « revue.pdf » les rendrait
    indiscernables au moment précis où l'on cherche celle de mars."""
    assert E._nom_fichier_revue(_revue(), "pdf") == "revue-hebdomadaire-2026-01-12.pdf"
    m = _revue(genre="mois", international=True)
    assert E._nom_fichier_revue(m, "docx") == \
        "revue-mensuelle-internationale-2026-01-01.docx"


def test_l_adresse_du_document_rouvre_la_meme_periode():
    """Un fichier reçu en comité doit pouvoir rouvrir la MÊME période. Une
    adresse vers `/revue` nu rendrait la période par défaut, c'est-à-dire une
    autre — et le lecteur ne s'en apercevrait qu'en comparant deux comptes."""
    src = _lire("app.py")
    i = src.index("def emporter_revue")
    corps = src[i:src.index("\n@app.route", i)]
    assert 'rv["periode"]["debut"]' in corps, corps
    assert "genre=%s&ancre=%s" in corps
    # ET LES BOUTONS DE LA PAGE PORTENT LA PÉRIODE AFFICHÉE, pas la défaut.
    js = _lire("revue.js")
    assert 'a.setAttribute("href", "/revue." + x[1] + q)' in js
    assert "emporter();" in js


def test_l_export_de_la_revue_passe_par_le_meme_calcul_que_la_page():
    """Refaire ici une sélection « pour l'export » produirait tôt ou tard un
    PDF qui ne dit pas ce que l'écran disait — et c'est le PDF qui circule."""
    src = _lire("app.py")
    i = src.index("def emporter_revue")
    corps = src[i:src.index("\n@app.route", i)]
    assert "RV.revue(fiches, genre, ancre" in corps
    assert "RV.derniere_ancre(c, genre, international=inter)" in corps
    # LA PORTE ÉDITORIALE RESTE LA MÊME : un format de sortie ne doit jamais
    # devenir le chemin de contournement d'une règle.
    assert "V.dans(x, langue)" in corps


def test_la_route_d_export_ne_masque_pas_le_script_de_la_page():
    """DÉFAUT CONSTATÉ AU NAVIGATEUR, ET DU PIRE GENRE : LA PAGE RENDAIT QUAND
    MÊME. Écrite `/revue.<format_>`, la route d'export capturait aussi
    `/revue.js` — Werkzeug la préfère à `/<path:nom>.js`, qui est plus
    générique. Le script de la page répondait donc 404 « format inconnu ». Les
    onglets ne réagissaient plus, les boutons gardaient leur adresse par
    défaut, et RIEN ne le signalait : le HTML s'affichait entier, seule la
    mécanique manquait.

    Le contrôle vérifie les DEUX côtés — que le script est servi, et que
    l'export l'est aussi. Ne garder que l'un des deux laisserait revenir la
    faute par l'autre bout."""
    import app as A
    c = A.app.test_client()
    r = c.get("/revue.js")
    assert r.status_code == 200 and len(r.data) > 2000
    assert b"function emporter" in r.data
    for f in ("pdf", "docx"):
        assert c.get("/revue." + f).status_code == 200, f
    # ET TOUTE PAGE SERVIE GARDE SON SCRIPT. La faute n'a pas de raison de se
    # limiter à celle-ci le jour où une autre route d'export sera écrite.
    for nom in ("veille", "fiche", "barre", "langue", "lecture"):
        assert c.get("/%s.js" % nom).status_code == 200, nom


def test_le_pdf_rendu_porte_reellement_ce_qu_on_y_met():
    """LE SEUL CONTRÔLE QUI OUVRE LE FICHIER. Tous les autres lisent la
    composition — la liste de blocs — et concluent que le document la porte.
    Entre les deux, il y a un rendu, une police et un encodage : c'est
    exactement là qu'un tiret cadratin devient un point d'interrogation, et
    ce défaut-là n'est visible que par le lecteur qui ouvre le fichier.

    Il est PASSÉ si `pypdf` manque, qui est déclarée facultative : un contrôle
    qui échoue faute de bibliothèque de lecture n'apprend rien sur le site."""
    ok, _ = E.pdf_disponible()
    if not ok:
        return
    try:
        import pypdf
    except ImportError:
        return
    import io as _io
    rv = _revue()
    lu = pypdf.PdfReader(_io.BytesIO(E.pdf_revue(rv, "https://exemple/revue")))
    texte = "\n".join(p.extract_text() or "" for p in lu.pages)
    for att in ("Revue de presse hebdomadaire", "CE QUE CETTE REVUE COMPTE",
                "Reportages et entretiens", "Aucun reportage",
                "Exporté de CONSEILPREV INFO", "https://exemple/revue"):
        assert att in texte, att
    # LES SIGNES FRANÇAIS SURVIVENT AU RENDU. C'est le motif écrit dans
    # `requirements.txt` pour lequel la police est au dépôt plutôt qu'au
    # système ; ce contrôle est ce qui le vérifie sur un fichier réel.
    assert "—" in texte, "le tiret cadratin n'a pas survécu au rendu"
    assert "é" in texte and "è" in texte
