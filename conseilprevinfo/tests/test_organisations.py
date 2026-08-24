"""LES ENTREPRISES NOMMÉES PAR LES SOURCES — et l'écart, minuscule et fatal,
entre « nommée » et « concernée ».

CE QU'UN FILTRE PAR ENTREPRISE PEUT FAIRE DE PIRE. Il peut rattacher une fiche
à une entreprise que la source ne met pas en cause. Un cabinet qui affiche
« Siemens (4) » affirme que quatre faits du corpus concernent Siemens : si l'un
des quatre n'est là que parce que NOUS avons écrit « Siemens » dans une phrase
d'analyse, l'affirmation est fausse, et elle porte sur un tiers nommé.

Ces contrôles gardent donc quatre règles, dans cet ordre d'importance :

  1. LE NOM EST CHERCHÉ LÀ OÙ LA SOURCE NOMME, jamais dans nos textes.
  2. LA CORRESPONDANCE EST UN MOT ENTIER, et la plus longue gagne.
  3. LE SIÈGE N'EST PAS LE PAYS DU FAIT, et les deux axes ne fusionnent pas.
  4. CE QUI N'EST PAS AU RÉPERTOIRE N'EST PAS RATTACHÉ — un axe qui ne trouve
     rien le dit.
"""
import os
import re
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import ingestion as I  # noqa: E402
import organisations as ORG  # noqa: E402
import veille as V  # noqa: E402


def _lire(nom):
    return open(os.path.join(ICI, nom), encoding="utf-8").read()


def _arguments(src, appel):
    """LES ARGUMENTS D'UN APPEL, PARENTHÈSES COMPTÉES.

    PREMIER ESSAI, ET IL NE GARDAIT RIEN : une expression régulière
    `\\(([^)]*)\\)` s'arrêtait à la PREMIÈRE parenthèse fermante. Sur
    `reconnaitre(c.get("target"), lecture_fr)`, elle ne lisait que
    `c.get("target"` — et le second argument, celui qu'il fallait justement
    interdire, était invisible. La mutation est passée sans faire tomber le
    contrôle, ce qui est le pire résultat possible pour un contrôle.

    On compte donc les parenthèses."""
    out = []
    i = src.find(appel)
    while i >= 0:
        j = i + len(appel)
        prof, debut = 1, j
        while j < len(src) and prof:
            if src[j] == "(":
                prof += 1
            elif src[j] == ")":
                prof -= 1
            j += 1
        out.append(src[debut:j - 1])
        i = src.find(appel, j)
    return out


def _fiche(**kw):
    base = {
        "id": "essai-orga", "titre": "Titre", "chapeau": "Chapeau.",
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


# ══ 1. LE NOM EST CHERCHÉ LÀ OÙ LA SOURCE NOMME ═══════════════════════════

def test_la_reconnaissance_ne_lit_que_les_champs_de_la_source():
    """LA FAUTE À NE JAMAIS COMMETTRE. Les collecteurs appellent
    `reconnaitre()` sur les champs où la source désigne une entité — `target`
    chez ATLAS, `vendorProject`/`product` chez CISA. L'appeler sur la lecture
    critique, la portée ou le chapeau rattacherait une fiche à Microsoft parce
    que NOUS y avons tapé « Microsoft », et le filtre annoncerait « les fiches
    qui concernent Microsoft » en servant « les fiches où nous l'avons écrit ».
    """
    src = _lire("ingestion.py")
    appels = _arguments(src, "ORG.reconnaitre(")
    assert appels, "aucun collecteur ne reconnaît d'organisation"
    interdits = ("lecture", "portee", "incertitude", "chapeau", "titre")
    for a in appels:
        for mot in interdits:
            assert mot not in a, "reconnaissance sur un texte du cabinet : %s" % a
    # ET LES CHAMPS EMPLOYÉS SONT BIEN CEUX DE LA SOURCE, nommés. Un contrôle
    # qui ne ferait qu'interdire laisserait passer un appel sur un champ neuf
    # dont personne n'aurait vérifié la provenance.
    admis = ("target", "vendorProject", "product")
    for a in appels:
        assert any(x in a for x in admis), a


def test_normaliser_ne_reconnait_rien_de_lui_meme():
    """`normaliser()` ne voit que la fiche COMPOSÉE — analyses comprises. Y
    chercher un nom d'entreprise contournerait la règle ci-dessus par la
    porte de service, et le ferait pour TOUS les collecteurs d'un coup."""
    src = _lire("veille.py")
    i = src.index("def normaliser(")
    corps = src[i:src.index("\ndef publiables", i)]
    assert "reconnaitre" not in corps, corps[-400:]
    # La fiche porte quand même le champ, vide : un axe absent se lit comme
    # un axe cassé.
    assert _fiche().get("organisations") == []


# ══ 2. MOT ENTIER, ET LA PLUS LONGUE GAGNE ════════════════════════════════

def test_la_correspondance_porte_sur_des_mots_entiers():
    """`ingestion.py` porte déjà la cicatrice : « Intel Ethernet DIAGNOSTICS
    Driver » ressortait industriel parce que « diagnostics » contient « ics ».
    Une sous-chaîne nue rattacherait « Delta Electronics » à toute fiche
    portant le mot « delta »."""
    assert ORG.reconnaitre("Deltaplane et abbaye") == []
    assert ORG.reconnaitre("Micro-ondes SICKert") == []
    assert ORG.reconnaitre("Delta Electronics DOPSoft") == ["delta"]


def test_la_plus_longue_appellation_gagne_et_consomme():
    """SANS CETTE RÈGLE, LE FILTRE PAR PAYS MENT. Hitachi Energy a son siège à
    Zurich, Hitachi à Tokyo : une fiche nommant « Hitachi Energy » rattachée
    aux DEUX ferait dire au menu « Japon » d'un fait suisse. Le passage trouvé
    est donc consommé."""
    assert ORG.reconnaitre("Hitachi Energy grid product") == ["hitachi_energy"]
    assert ORG.reconnaitre("Hitachi Ltd") == ["hitachi"]
    assert ORG.reconnaitre("Rockwell Automation FactoryTalk") == ["rockwell"]


def test_l_ordre_du_resultat_est_celui_du_repertoire():
    """Deux fiches nommant les mêmes entreprises doivent porter la même liste.
    Un ordre de rencontre ferait croire à un classement — « la première est la
    principale » — que rien ne fonde."""
    a = ORG.reconnaitre("Google Translate, Bing Translator, Systran Translate")
    b = ORG.reconnaitre("Systran, Bing, Google")
    assert a == b and len(a) == 3


# ══ 3. LE SIÈGE N'EST PAS LE PAYS DU FAIT ═════════════════════════════════

def test_les_deux_axes_ne_fusionnent_pas():
    """C'EST LA CONFUSION À NE PAS FAIRE. Le pays d'une fiche dit où le FAIT se
    situe ; le siège dit d'où vient l'entreprise nommée. Un incident contre un
    produit Microsoft n'est pas un fait américain — et une fiche filtrée par
    pays ne doit jamais sortir sur le seul motif d'un siège."""
    f = _fiche(id="o-1", organisations=["microsoft"], pays=[])
    assert V.filtrer([f], pays="US") == []
    assert len(V.filtrer([f], siege="US")) == 1
    # Et le champ `pays` de la fiche n'a pas été rempli en douce.
    assert f["pays"] == []


def test_le_menu_pays_separe_les_deux_provenances():
    """Un seul menu, deux groupes nommés — et c'est `parametres()` qui traduit,
    EN UN SEUL ENDROIT. Traduire à plusieurs endroits produirait une adresse
    partagée qui ne pose pas la question affichée."""
    js = _lire("veille.js")
    assert "f.pays.fait" in js and "f.pays.siege" in js
    assert '<optgroup label="' in js
    # Un seul point de traduction, et son pendant en lecture d'adresse.
    assert js.count('q.push("siege=" + encodeURIComponent(') == 1
    assert 'v = "siege:" + p.get("siege")' in js


def test_le_siege_porte_sa_provenance_partout_ou_il_sert():
    """Il ne vient d'aucune source lue. Servi sans sa mention, il se lirait
    comme le pays du fait — c'est-à-dire comme un constat."""
    assert "aucune des sources lues ne le porte" in ORG.ORIGINE_DU_SIEGE[0]
    fac = V.facettes([_fiche(id="o-2", organisations=["siemens"])])
    assert fac["siege_origine"] == ORG.ORIGINE_DU_SIEGE[0]
    assert fac["siege_origine_en"] == ORG.ORIGINE_DU_SIEGE[1]
    # ET SUR LA FICHE, là où le lecteur vérifie le rattachement.
    assert "fi-orgs-dit" in _lire("fiche.js")
    assert "origine_du_siege" in _lire("app.py")


def test_un_siege_dispute_ne_pese_dans_aucun_pays():
    """VirusTotal est né à Málaga et appartient à un groupe américain ; Johnson
    Controls est de droit irlandais et dirigé depuis Milwaukee. Trancher serait
    un jugement de plus. L'entrée reste filtrable par son nom — c'est le pays
    qui manque, pas elle."""
    f = _fiche(id="o-3", organisations=["virustotal"])
    assert V.facettes([f])["sieges"] == []
    assert len(V.filtrer([f], organisation="virustotal")) == 1
    assert ORG.siege("virustotal") is None


def test_le_compte_par_siege_compte_des_fiches_pas_des_entreprises():
    """Le menu annonce ce que le filtre servira, et le filtre sert des fiches.
    Trois entreprises américaines dans une même étude de cas donnent « (1) ».
    Un menu qui promet trois résultats et en rend un est le défaut déjà
    corrigé sur les autres axes."""
    f = _fiche(id="o-4", organisations=["microsoft", "google", "openai"])
    sieges = {x["cle"]: x["n"] for x in V.facettes([f])["sieges"]}
    assert sieges == {"US": 1}


# ══ 4. CE QUI N'EST PAS AU RÉPERTOIRE N'EST PAS RATTACHÉ ══════════════════

def test_ce_que_la_source_ne_nomme_pas_ne_donne_rien():
    """Mesuré sur les études de cas d'ATLAS : le champ `target` contient
    « Cloud-Based LLM Services », « Multiple systems », « 10 web-scale
    datasets ». Une extraction automatique en ferait des « entreprises ».
    C'est l'invention que ce site refuse."""
    for rien in ("Cloud-Based LLM Services", "Multiple systems",
                 "10 web-scale datasets", "ML-based Android Apps",
                 "Ukraine's security and defense sector"):
        assert ORG.reconnaitre(rien) == [], rien


def test_le_menu_ne_propose_que_ce_qui_est_trouve():
    """Un répertoire de cinquante entreprises dont quarante-six ne rendent
    rien serait un piège, pas un filtre — c'est la règle des facettes, et elle
    vaut ici comme sur les autres axes."""
    fac = V.facettes([_fiche(id="o-5", organisations=["siemens"])])
    assert [x["cle"] for x in fac["organisations"]] == ["siemens"]
    assert len(ORG.ORGANISATIONS) > 5, "sinon ce contrôle ne garde rien"


def test_chaque_axe_est_compte_hors_de_son_propre_filtre():
    """Sans cela, choisir une entreprise réduirait le menu à cette seule
    entreprise, et l'on ne pourrait plus en changer sans tout remettre à
    zéro."""
    c = [_fiche(id="o-6", organisations=["siemens"]),
         _fiche(id="o-7", organisations=["abb"])]
    fac = V.facettes(c, organisation="siemens")
    assert fac["total_trouve"] == 1
    assert {x["cle"] for x in fac["organisations"]} == {"siemens", "abb"}


# ══ 5. LE RÉPERTOIRE LUI-MÊME ═════════════════════════════════════════════

def test_le_repertoire_refuse_de_se_charger_s_il_est_douteux():
    """Une faute ici ne se voit pas à l'écran : elle se voit dans un filtre qui
    rattache des fiches à la mauvaise entreprise, ce qui est pire qu'un filtre
    absent. Le module refuse donc de se charger — et ce contrôle vérifie que le
    refus fonctionne, plutôt que de faire confiance à sa présence."""
    ORG._verifier()          # le répertoire réel passe

    garde = ORG.ORGANISATIONS
    fautes = [
        # même clé deux fois
        garde + ({"cle": garde[0]["cle"], "nom": "X", "nature": "entreprise",
                  "pays": "FR", "appellations": ("xxxx",)},),
        # nature inventée
        garde + ({"cle": "zz", "nom": "X", "nature": "machin",
                  "pays": "FR", "appellations": ("xxxx",)},),
        # siège absent SANS motif : un trou se lirait comme une réserve
        garde + ({"cle": "zz", "nom": "X", "nature": "entreprise",
                  "pays": None, "appellations": ("xxxx",)},),
        # appellation de deux lettres : « ics » dans « diagnostics »
        garde + ({"cle": "zz", "nom": "X", "nature": "entreprise",
                  "pays": "FR", "appellations": ("zz",)},),
        # appellation partagée par deux entrées : le rattachement devient un
        # tirage au sort
        garde + ({"cle": "zz", "nom": "X", "nature": "entreprise",
                  "pays": "FR", "appellations": ("siemens",)},),
    ]
    try:
        for f in fautes:
            ORG.ORGANISATIONS = f
            try:
                ORG._verifier()
            except ValueError:
                continue
            raise AssertionError("répertoire douteux accepté : %r" % (f[-1],))
    finally:
        ORG.ORGANISATIONS = garde
    ORG._verifier()


def test_les_pays_du_repertoire_sont_nommables():
    """Un siège dont le pays ne serait pas au registre s'afficherait « IL » ou
    « TW » dans le menu, et le lecteur devrait savoir lire l'ISO 3166. C'est
    exactement le défaut corrigé sur l'axe des pays."""
    manquants = sorted({o["pays"] for o in ORG.ORGANISATIONS
                        if o.get("pays") and o["pays"] not in V.PAYS})
    assert not manquants, manquants


def test_les_pays_ajoutes_pour_nommer_ne_sont_pas_collectes():
    """Le registre porte des pays qui n'y sont QUE pour nommer un siège. Les
    suivre reviendrait à annoncer un suivi du mix électrique japonais que ce
    site n'a jamais promis, et à lancer une requête pour une entité que les
    jeux de données ne nomment pas ainsi."""
    for o in ORG.ORGANISATIONS:
        p = o.get("pays")
        if p and not V.PAYS[p].get("owid"):
            assert p not in I.PAYS_SUIVIS, p
    # Le cas existe réellement, sinon ce contrôle ne garde rien.
    assert any(o.get("pays") and not V.PAYS[o["pays"]].get("owid")
               for o in ORG.ORGANISATIONS)


def test_le_repertoire_dit_ce_qu_il_couvre():
    """Un répertoire tenu à la main vieillit. Ce compte est ce qui le dira —
    annoncé, il serait faux le jour d'un ajout ; mesuré, il suit."""
    s = ORG.sante()
    assert s["organisations"] == len(ORG.ORGANISATIONS)
    assert s["appellations"] >= s["organisations"]
    assert s["modeles_de_langage"] == 0
    assert sorted(s["siege_dispute"]) == sorted(
        o["cle"] for o in ORG.ORGANISATIONS if not o.get("pays"))


# ══ 6. LE FILTRE N'OUVRE PAS CE QUE LA PORTE FERME ════════════════════════

def test_le_filtre_par_entreprise_ne_sort_pas_une_fiche_non_publiable():
    """La règle du site vaut sur CHAQUE axe, y compris les neufs : un
    paramètre d'URL ne doit jamais devenir le chemin de contournement d'une
    règle éditoriale."""
    # Les deux portes, chacune de son côté : la nature de lecture et le statut.
    # LA LECTURE DE MODÈLE PORTE SON STATUT : `normaliser()` refuse le couple
    # « modèle de langage » + statut publiable AVANT d'en arriver aux filtres,
    # ce qui est une garantie de plus, pas de moins.
    modele = _fiche(id="o-8", organisations=["siemens"],
                    lecture_nature="modele", statut="redigee_par_ia")
    doute = _fiche(id="o-9", organisations=["siemens"], statut="a_verifier")
    for f in (modele, doute):
        assert V.filtrer([f], organisation="siemens") == [], f["id"]
        assert V.filtrer([f], siege="DE") == [], f["id"]
    # Et elles n'apparaissent pas non plus dans les menus, qui autrement
    # annonceraient « Siemens (2) » pour un fil qui n'en montre aucune.
    fac = V.facettes([modele, doute])
    assert fac["organisations"] == [] and fac["sieges"] == []
