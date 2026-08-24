"""LE CLASSEUR, L'EXPORT ET L'ÉTAT DE LECTURE — trois ajouts, trois promesses.

CHACUN DE CES TROIS TOUCHE À UNE RÈGLE QUE LE SITE S'ÉTAIT DONNÉE, et c'est
pour cela qu'ils ont des contrôles à eux :

  · LE CLASSEUR conserve des documents, alors que la page de confrontation
    écrit « aucune copie n'est écrite sur disque ». La phrase reste vraie de
    la confrontation, et elle a été AMENDÉE pour ne plus valoir promesse
    générale. Le classeur, lui, doit dire ce qu'il garde AVANT le dépôt.
  · L'EXPORT fait circuler une fiche SANS SA PAGE. Un document plus
    affirmatif que la page dont il vient serait la faute la plus coûteuse de
    ce site : il doit porter le statut, la nature de la lecture, ce qu'on ne
    sait pas et la source.
  · L'ÉTAT DE LECTURE mémorise ce qu'un lecteur a ouvert. Cette mémoire ne
    doit jamais atteindre le serveur : un cabinet qui saurait quelles
    vulnérabilités un industriel consulte détiendrait exactement le fichier
    que cet industriel redoute.
"""
import io
import os
import re
import sys
import zipfile

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import abonnes as AB  # noqa: E402
import classeur as CL  # noqa: E402
import exporter as EXP  # noqa: E402
import veille as V  # noqa: E402


def _lire(nom):
    return open(os.path.join(ICI, nom), encoding="utf-8").read()


def _vider():
    CL._RANGES.clear()
    AB._COMPTES.clear()
    AB._SESSIONS.clear()


def _fiche(**kw):
    base = {
        "id": "essai-fiche", "titre": "Un titre — avec un tiret cadratin",
        "chapeau": "Chapeau « avec des guillemets ».",
        "lecture": "L" * 100, "lecture_nature": "regle",
        "portee": "P" * 80, "incertitude": "I" * 60,
        "sujet": "cyber_industriel", "date_fait": "2026-01-15",
        "source_cle": "cisa_kev", "source_url": "https://www.cisa.gov/x",
        "statut": "verifiee_source_primaire", "impact": "structurant",
        "horizon": "constate",
    }
    base.update(kw)
    return V.normaliser(base)["fiche"]


# ══ 1. LE CLASSEUR ═══════════════════════════════════════════════════════

def test_le_classeur_dit_qu_il_n_est_pas_un_coffre():
    """LA RÉSERVE EST SERVIE AVEC LA LISTE, donc lisible AVANT tout dépôt. Un
    espace qui perdrait des documents en silence serait pire que pas d'espace
    du tout — et sur cet hébergement, un redémarrage efface la mémoire."""
    _vider()
    r = CL.lister("qui@usine.fr")
    assert r["durable"] is False
    for phrase in ("MÉMOIRE", "redémarrage", "pas un coffre"):
        assert phrase in r["dit"], r["dit"]
    assert "not a vault" in r["dit_en"]


def test_les_plafonds_sont_annonces_avant_d_etre_heurtes():
    """Un plafond qu'on découvre au refus est une mauvaise surprise ; annoncé,
    c'est une contrainte."""
    r = CL.lister("qui@usine.fr")
    assert r["plafond_documents"] == CL.DOCUMENTS_PAR_COMPTE
    assert r["plafond_octets"] == CL.OCTETS_PAR_COMPTE
    assert r["plafond_par_document"] == CL.OCTETS_PAR_DOCUMENT
    assert set(r["formats"]) == set(CL.FORMATS)


def test_chaque_refus_nomme_sa_raison_et_son_plafond():
    """« Dépôt impossible » oblige à deviner, et l'on devine toujours mal : on
    réessaie avec le même fichier."""
    _vider()
    r = CL.deposer("qui@usine.fr", "photo.zip", b"PK")
    assert r["erreur"] == "format_refuse" and ".zip" in r["message"]
    r = CL.deposer("qui@usine.fr", "gros.pdf", b"x" * (CL.OCTETS_PAR_DOCUMENT + 1))
    assert r["erreur"] == "trop_gros" and "Mio" in r["message"]
    r = CL.deposer("qui@usine.fr", "vide.txt", b"")
    assert r["erreur"] == "vide"
    r = CL.deposer(None, "note.txt", b"x")
    assert r["erreur"] == "hors_compte"


def test_un_classeur_n_est_lisible_que_par_son_compte():
    """LE COMPTE EST UN ARGUMENT DE CHAQUE FONCTION, jamais un contrôle fait
    ailleurs : il suffirait d'un chemin d'API oublié pour ouvrir le classeur
    d'autrui."""
    _vider()
    d = CL.deposer("a@usine.fr", "secret.txt", b"architecture")["document"]
    assert CL.contenu("a@usine.fr", d["id"])["octets_bruts"] == b"architecture"
    assert CL.contenu("b@usine.fr", d["id"]) is None
    assert CL.contenu(None, d["id"]) is None
    assert CL.lister("b@usine.fr")["documents"] == []
    assert CL.effacer("b@usine.fr", d["id"])["ok"] is False
    # et le document d'origine n'a pas bougé
    assert CL.lister("a@usine.fr")["n"] == 1


def test_les_octets_ne_sortent_pas_par_la_liste():
    """Une liste qui porterait le contenu ferait transiter tous les documents
    à chaque affichage de la page."""
    _vider()
    CL.deposer("a@usine.fr", "note.txt", b"contenu")
    for d in CL.lister("a@usine.fr")["documents"]:
        assert not any(k.startswith("_") for k in d), d
        assert "octets_bruts" not in d


def test_un_nom_de_fichier_est_une_entree_d_utilisateur():
    """Il est réaffiché : sans nettoyage il porterait des chemins, des
    caractères de contrôle, ou du balisage."""
    _vider()
    d = CL.deposer("a@usine.fr", "../../etc/passwd.txt", b"x")["document"]
    assert d["nom"] == "passwd.txt", d["nom"]
    d = CL.deposer("a@usine.fr", "note\r\ninjectee.txt", b"x")["document"]
    assert "\n" not in d["nom"] and "\r" not in d["nom"]


def test_l_empreinte_permet_de_verifier_ce_qu_on_recupere():
    """Cet espace n'étant pas durable, l'empreinte est le seul moyen de
    s'assurer que le fichier récupéré est bien celui qui a été déposé."""
    import hashlib
    _vider()
    octets = b"une politique de securite"
    d = CL.deposer("a@usine.fr", "p.txt", octets)["document"]
    assert d["empreinte"] == hashlib.sha256(octets).hexdigest()[:16]


def test_un_compte_efface_emporte_son_classeur():
    """`abonnes.oublier()` promet que « rien n'en subsiste dans ce
    processus ». Cette phrase serait devenue fausse le jour du classeur si
    personne n'y avait pensé — le crochet la maintient vraie par
    construction, sans liste à tenir à jour dans une fonction qu'on ne relit
    pas."""
    _vider()
    # L'APPLICATION DOIT L'AVOIR INSCRIT, pas ce contrôle. Premier essai :
    # l'inscription était faite ici — le contrôle passait donc même quand
    # `app.py` l'avait oubliée, c'est-à-dire dans le seul cas qui compte.
    src = _lire("app.py")
    assert "AB.a_purger(CL.vider)" in src, \
        "l'application n'inscrit pas le classeur à la purge des comptes"
    import app  # noqa: F401  — l'import exécute l'inscription
    assert CL.vider in AB._PURGES

    AB.creer("parti@usine.fr", "une phrase entiere vaut mieux")
    j = AB.connecter("parti@usine.fr", "une phrase entiere vaut mieux")["jeton"]
    CL.deposer("parti@usine.fr", "note.txt", b"x" * 50)
    assert CL.lister("parti@usine.fr")["n"] == 1
    AB.oublier(j)
    assert CL.lister("parti@usine.fr")["n"] == 0


def test_le_plafond_global_protege_la_memoire_partagee():
    """Sans lui, un seul dépôt épuiserait la mémoire d'un serveur partagé et
    ferait tomber le site pour tout le monde."""
    assert CL.OCTETS_AU_TOTAL >= CL.OCTETS_PAR_COMPTE
    src = _lire("classeur.py")
    i = src.index("def deposer")
    assert "_total_global()" in src[i:i + 3200]


# ══ 2. L'EXPORT ══════════════════════════════════════════════════════════

def test_un_document_emporte_porte_de_quoi_en_juger():
    """Il circule SANS SA PAGE : transféré, imprimé, relu six mois plus tard
    par quelqu'un qui n'a jamais vu le site. Un export réduit au titre et au
    chapeau serait plus « propre » et aurait perdu exactement ce qui
    distingue ce site d'un agrégateur."""
    f = _fiche()
    textes = " ".join(t for _, t in EXP.blocs(f, "https://x/fiche/essai-fiche"))
    assert f["titre"] in textes
    assert f["lecture"] in textes and f["portee"] in textes
    assert f["incertitude"] in textes          # ce qu'on ne sait pas
    assert f["statut_nom"] in textes           # le statut de vérification
    assert f["lecture_nom"] in textes          # la nature de la lecture
    assert f["source"]["nom"] in textes and f["source"]["url"] in textes
    assert "https://x/fiche/essai-fiche" in textes   # de quoi y revenir


def test_aucun_texte_n_est_reecrit_pour_l_export():
    """Sans quoi il existerait deux versions d'une même fiche, et rien ne
    dirait laquelle fait foi."""
    f = _fiche()
    par_genre = dict((g, t) for g, t in EXP.blocs(f))
    assert par_genre["titre"] == f["titre"]
    assert par_genre["chapeau"] == f["chapeau"]
    corps = [t for g, t in EXP.blocs(f) if g == "corps"]
    assert f["lecture"] in corps and f["portee"] in corps


def test_la_reserve_d_une_date_de_convention_voyage_avec_elle():
    """Séparées, la date serait lue comme une observation par quiconque
    n'ouvre pas le paragraphe suivant."""
    f = _fiche(date_convention=True,
               date_convention_dit="La source date son édition, pas ses entrées.")
    date_ = dict((g, t) for g, t in EXP.blocs(f))["date"]
    assert "N'EST PAS UNE OBSERVATION" in date_
    assert "édition" in date_


def test_le_docx_est_une_archive_que_word_ouvre():
    d = EXP.docx(_fiche())
    z = zipfile.ZipFile(io.BytesIO(d))
    assert set(z.namelist()) == {"[Content_Types].xml", "_rels/.rels",
                                 "word/document.xml"}
    import xml.dom.minidom
    xml.dom.minidom.parseString(z.read("word/document.xml"))   # lève si mal formé
    assert "Un titre" in z.read("word/document.xml").decode("utf-8")


def test_deux_exports_de_la_meme_fiche_rendent_les_memes_octets():
    """Un horodatage les rendrait différents, et l'on ne pourrait plus
    vérifier qu'un fichier reçu n'a pas été retouché."""
    f = _fiche()
    assert EXP.docx(f) == EXP.docx(f)


def test_le_pdf_porte_les_signes_que_le_latin_1_ne_connait_pas():
    """Les polices intégrées de fpdf2 sont en latin-1 : les tirets cadratins
    et les guillemets français en sortiraient en points d'interrogation — un
    défaut invisible ici, visible par le seul lecteur qui ouvre le fichier.
    D'où la police Unicode versée au dépôt."""
    ok, pourquoi = EXP.pdf_disponible()
    if not ok:
        import pytest
        pytest.skip(pourquoi)
    p = EXP.pdf(_fiche())
    assert p[:5] == b"%PDF-"
    assert len(p) > 5000
    assert os.path.exists(os.path.join(EXP.POLICES, "LiberationSerif-Regular.ttf"))


def test_le_nom_de_fichier_ne_reprend_rien_de_dangereux():
    """Un titre porte des barres obliques, des points et des caractères que
    certains systèmes refusent."""
    n = EXP._nom_fichier(_fiche(titre="A/B: « c » — d.e"), "pdf")
    assert re.match(r"^[a-z0-9\-]+\.pdf$", n), n


def test_un_format_absent_le_dit_au_lieu_de_tomber():
    """Un bouton qui rend une erreur cinq secondes après le clic est pire
    qu'un bouton absent."""
    ok, pourquoi = EXP.pdf_disponible()
    assert ok or len(pourquoi) > 40
    s = EXP.sante()
    assert "docx" in s["formats"]
    assert s["pdf_disponible"] is ok


def test_l_export_ne_contourne_pas_la_porte_editoriale():
    """Une fiche non publiable répond 404 à l'export comme à l'écran : un
    format de sortie ne doit jamais devenir le chemin de contournement d'une
    règle éditoriale."""
    src = _lire("app.py")
    i = src.index("def emporter")
    bloc = src[i:i + 900]
    assert "V.publiables(corpus())" in bloc, bloc[:300]


# ══ 3. L'ÉTAT DE LECTURE ═════════════════════════════════════════════════

def test_la_memoire_de_lecture_ne_quitte_pas_le_navigateur():
    """Un cabinet qui saurait quelles vulnérabilités un industriel consulte
    détiendrait exactement le fichier que cet industriel redoute. La mémoire
    vit dans `localStorage` — aucune requête ne la transporte."""
    js = _lire("lecture.js")
    assert "localStorage" in js
    for interdit in ("fetch(", "XMLHttpRequest", "navigator.sendBeacon", "/api/"):
        assert interdit not in js, interdit


def test_le_clignotement_permanent_est_encadre():
    """CE CONTRÔLE GARDAIT L'ENGAGEMENT INVERSE — « le clignotement permanent a
    été écarté » — et il a été RÉÉCRIT, pas retiré. Le clignotement est
    désormais demandé et rendu ; ce qu'il faut garder, ce sont les quatre
    conditions qui le rendent tenable. Les perdre une par une est exactement
    ainsi qu'une animation devient nuisible.

    UNE : le cycle reste loin des trois éclats par seconde de la règle WCAG
    2.3.1, seuil du risque de crise pour les personnes photosensibles.
    DEUX : il s'arrête, ce qu'exige la règle WCAG 2.2.2 au-delà de cinq
    secondes — et de deux façons, dont une qui ne demande aucun geste.
    TROIS : seul le vert bat. Quatre-vingt-dix-huit contours battant ensemble
    rendraient la page inutilisable, et le mouvement ne dirait plus rien
    puisqu'il serait partout.
    QUATRE : l'interrupteur existe VRAIMENT. Une classe `cp-fixe` que rien
    n'écrirait serait une conformité de façade."""
    css = _lire("veille.css")
    assert "@keyframes cp-clignote" in css

    # UN — la durée du cycle, lue dans la règle et non supposée.
    m = re.search(r"\.fiche\.lu\{animation:cp-clignote ([\d.]+)s", css)
    assert m, "aucune règle d'animation sur .fiche.lu"
    assert float(m.group(1)) >= 1.0, \
        "un cycle de %ss s'approche du seuil des trois éclats par seconde" \
        % m.group(1)

    # DEUX — les deux arrêts, et le second est celui du système.
    serre = css.replace(" ", "").replace("\n", "")
    assert "html.cp-fixe.fiche.lu{animation:none}" in serre, \
        "l'interrupteur ne coupe plus l'animation"
    # LA FEUILLE PORTE PLUSIEURS `prefers-reduced-motion` — la première trouvée
    # coupait les transitions des cartes, pas ce clignotement. Un contrôle qui
    # se contente de la première dit « c'est coupé » d'une règle qui ne coupe
    # pas celle-ci : on cherche donc CETTE règle-là, entière.
    assert "@media(prefers-reduced-motion:reduce){.fiche.lu{animation:none}}" \
        in serre, "le réglage du système ne coupe plus CE clignotement"

    # TROIS — le bleu ne bat pas, et la carte nue non plus.
    for jamais in (".fiche.neuf{animation:", ".fiche{animation:"):
        assert jamais.replace(" ", "") not in serre, jamais

    # QUATRE — quelqu'un pose réellement la classe, et quelqu'un l'appelle.
    js = _lire("lecture.js")
    assert 'classList.toggle("cp-fixe"' in js
    assert "clignoter:" in js, "l'interrupteur n'est pas exposé"
    assert "prefers-reduced-motion" in js
    appels = sum("LU.clignoter(" in _lire(f) for f in ("veille.js", "barre.js"))
    assert appels == 2, \
        "l'interrupteur doit être atteignable depuis le fil ET depuis la barre"


def test_l_etat_de_lecture_ne_touche_pas_au_code_des_pastilles():
    """Les pastilles portent quatre codes de couleur que le lecteur apprend.
    L'état de lecture passe par le CONTOUR de la carte — un autre canal, pour
    une autre nature d'information : ce que la fiche EST, contre où VOUS en
    êtes.

    LA FORME DU CONTOUR A CHANGÉ, ET C'ÉTAIT LE DÉFAUT : trois pixels du seul
    bord gauche, en deux teintes sombres et voisines, dans une grille à trois
    colonnes. Le lecteur ne distinguait rien. Ce que ce contrôle garde n'est
    donc pas la forme d'hier, c'est la SÉPARATION DES CANAUX — et le fait que
    le contour soit complet, ce qui est ce qui l'a rendu visible."""
    # LES ESPACES SONT RETIRÉS DES DEUX CÔTÉS. Premier essai : retirés de la
    # source seule, ce qui rendait le contrôle impossible à satisfaire — il
    # cherchait un motif espacé dans un texte qui ne l'était plus.
    def serre(x):
        return x.replace(" ", "").replace("\n", "")
    css = serre(_lire("veille.css"))
    assert serre(".fiche.neuf{outline:2px solid var(--bleu)") in css
    assert serre(".fiche.lu{outline:2px solid var(--vert)") in css
    # aucune pastille n'a été repeinte
    assert serre(".past.sujet{color:var(--bleu)") in css


def test_la_couleur_ne_decide_pas_seule_de_l_etat_de_lecture():
    """RÈGLE WCAG 1.4.1, et elle mord ici plus qu'ailleurs : bleu et vert sont
    précisément la paire que la deutéranopie confond, et sur un filet de deux
    pixels aucune nuance ne sauve personne. La carte lue porte donc son MOT.

    SEULE LA CARTE LUE. L'absence est le second canal du cas courant :
    quatre-vingt-dix-huit étiquettes « non lue » n'apprendraient rien à
    personne et encombreraient chaque vignette."""
    for nom in ("veille.js", "fiche.js"):
        js = _lire(nom)
        assert 'class="fmarque"' in js, nom
        assert "lc.marque" in js, nom
        assert '=== "lu"' in js, nom
    css = _lire("veille.css").replace(" ", "").replace("\n", "")
    assert ".fmarque{" in css


def test_sans_accord_la_page_n_affirme_pas_que_rien_n_a_ete_lu():
    """LE DÉFAUT QUI A MOTIVÉ TOUT CECI, et le plus grave des deux. `classe()`
    rendait « neuf » quand la mémoire n'est pas tenue : la page peignait alors
    les quatre-vingt-dix-huit cartes en « à lire », ce qui AFFIRME que le
    lecteur n'a rien lu — alors que la vérité est que le site ne sait pas.

    Il voyait donc un code parfaitement uniforme et en concluait, à juste
    titre, qu'il ne distinguait rien. Sans accord : aucune marque, et le fil
    dit pourquoi en toutes lettres, là où les cartes sont."""
    js = _lire("lecture.js")
    i = js.index("function classe(")
    corps = js[i:js.index("\n  }", i)]
    assert 'if (!autorise()) return ""' in corps, corps

    # ET LE FIL LE DIT — un silence sans phrase serait la même panne muette.
    v = _lire("veille.js")
    assert "function direRepere(" in v
    assert "lc.non" in v
    # La porte s'ouvre depuis le repère, et c'est le module de consentement
    # qui l'ouvre : une seule fonction du site écrit l'accord.
    assert 'VP.repondre("memoire", true)' in v
    assert 'id="repere"' in _lire("index.html")


def test_la_legende_ressemble_a_ce_qu_elle_designe():
    """Un témoin qui ne reproduit pas le contour de la carte n'apprend pas à le
    reconnaître — et c'était le cas : filet de 3 px à gauche dans la barre,
    contour complet de 2 px sur les cartes. Les deux légendes du site montrent
    donc exactement ce qu'on verra."""
    css = _lire("veille.css").replace(" ", "").replace("\n", "")
    for etat, ton in (("neuf", "bleu"), ("lu", "vert")):
        assert ".bl-lg-c.%s{outline:2pxsolidvar(--%s)" % (etat, ton) in css, etat
        assert ".repere.rp-c.%s{outline:2pxsolidvar(--%s)" % (etat, ton) in css, etat


def test_la_memoire_de_lecture_peut_s_effacer():
    """Une mémoire qu'on ne peut pas effacer n'est pas une commodité, c'est un
    fichier — même tenu dans le navigateur du lecteur."""
    js = _lire("lecture.js")
    assert "function oublier" in js and "removeItem" in js
    b = _lire("barre.js")
    assert 'id="bl-lu"' in b
    v = _lire("veille.js")
    assert 'id="bl-oubli"' in v and "bl.oublier.sur" in v


def test_la_promesse_de_la_confrontation_a_ete_amendee():
    """Elle disait « ce que devient votre document : rien ». Cela reste vrai
    de la CONFRONTATION — mais laissé tel quel, un lecteur y aurait lu que ce
    site ne garde jamais rien, ce que le classeur dément. Une promesse qu'un
    ajout légitime rend fausse doit être réécrite le jour de l'ajout."""
    d = _lire("langue.js")
    i = d.index('"cf.dev.t"')
    bloc = d[i:i + 1800]
    assert "classeur" in bloc, "la confrontation promet encore sans réserve"
    assert "folder" in bloc, "la version anglaise n'a pas été amendée"


def test_l_interrupteur_ne_propose_pas_d_arreter_ce_qui_ne_bat_pas():
    """DÉFAUT SIGNALÉ PAR LE LECTEUR : « Arrêter le clignotement — ne
    fonctionne pas ». IL FONCTIONNAIT, et c'est ce qui rend le défaut
    intéressant : il écrivait son réglage, posait `cp-fixe`, changeait son
    propre intitulé. Mais à l'écran, RIEN NE BOUGEAIT.

    LA CAUSE. Seul le contour vert bat, et le vert n'apparaît que sur une
    fiche DÉJÀ OUVERTE. Un lecteur qui vient d'accorder la mémoire n'en a
    aucune : soixante cartes bleues, immobiles. Le bouton proposait donc
    d'arrêter ce qui n'avait pas commencé, et rien ne permettait de constater
    qu'il avait obéi.

    C'est exactement la faute déjà écrite pour `prefers-reduced-motion` —
    « proposer d'arrêter ce qui ne bouge pas apprend au lecteur à se méfier de
    tous les autres boutons du site » — et elle n'avait été traitée que pour
    ce cas-là, qui est le plus RARE. Le cas courant, la première visite,
    restait ouvert.

    LE BOUTON N'EST PAS CACHÉ POUR AUTANT : il faudrait alors lire une fiche
    pour pouvoir refuser une animation. Il reste, et la page dit que rien ne
    bat."""
    v, b = _lire("veille.js"), _lire("barre.js")

    # LES DEUX RÉGIONS EXACTES, et non les deux fichiers entiers. PREMIER
    # ESSAI, ET IL NE GARDAIT RIEN : le contrôle cherchait `lc.rien` et le
    # comptage n'importe où dans le fichier. Remplacer `if (!bat)` par
    # `if (false)` laissait les deux en place — la phrase n'était plus jamais
    # écrite, et le contrôle restait vert. Un contrôle qui vérifie qu'un
    # ingrédient EXISTE ne vérifie pas qu'on s'en sert.
    fil = v[v.index("var actif = !window.LU.clignote"):v.index("e.innerHTML = h;")]
    bar = b[b.index("var actif = window.LU.clignote();"):b.index("return h;")]

    # LE COMPTE EST FAIT SUR LA PAGE, pas déduit du réglage : c'est ce que le
    # lecteur a sous les yeux qui décide de la phrase — ET IL DÉCIDE.
    assert 'document.querySelectorAll(".fiche.lu").length > 0' in fil
    assert 'if (!bat) h += ' in fil and 'tr("lc.rien")' in fil
    assert 'if (!document.querySelector(".fiche.lu"))' in bar
    assert 't("lc.rien")' in bar

    # LE BOUTON RESTE, ET SANS CONDITION — sinon il faudrait lire une fiche
    # pour pouvoir refuser une animation. Le cacher serait la correction
    # facile, et elle enfermerait le lecteur que le mouvement dérange.
    # ANCRÉ EN DÉBUT DE LIGNE, et c'est le point. Chercher la sous-chaîne
    # `h += '<button…` laissait passer `if (false) h += '<button…` : le
    # fragment restait dans le fichier, le bouton n'était plus écrit, et le
    # contrôle restait vert. La condition, si elle revenait, se glisserait
    # exactement là.
    assert re.search(r"""(?m)^\s*h \+= '<button type="button" id="rp-cli\"""", fil)
    assert re.search(
        r"""(?m)^\s*h \+= '<button type="button" class="bl-lg-cli" id="bl-cli\"""", bar)
    for region, nom in ((fil, "veille.js"), (bar, "barre.js")):
        assert "lc.stop" in region and "lc.repart" in region, nom

    # LA PHRASE NE SURVIT PAS À LA LECTURE QUI LA DÉMENT. Une seule annonce,
    # au seul endroit où une fiche devient lue, et les deux repères l'écoutent.
    l = _lire("lecture.js")
    i = l.index("function marquer(")
    assert "lecture-changee" in l[i:l.index("\n  }", i)], "l'annonce manque"
    assert 'addEventListener("lecture-changee"' in b, "la barre ne l'écoute pas"
    j = v.index("function suivreLecture(")
    assert "direRepere();" in v[j:v.index("\n  }", j)], "le fil ne se refait pas"

    # ET LA BARRE NE DEVINE PAS UN ÉTAT DE PAGE QUI N'EXISTE PAS ENCORE.
    # DÉFAUT TROUVÉ EN VÉRIFIANT LA CORRECTION PRÉCÉDENTE, et plus profond
    # qu'elle : la barre se compose au chargement du document, les cartes
    # arrivent après un aller-retour réseau. Sa question « y a-t-il une carte
    # verte ? » recevait TOUJOURS non — non parce qu'aucune fiche n'était lue,
    # mais parce qu'aucune n'existait. C'est la faute qui avait déjà motivé
    # `suivreCompteurs()`, et elle appelle la même réponse : être prévenue.
    assert "function annoncerFil(" in v and 'CustomEvent("fil-rendu")' in v
    assert 'addEventListener("fil-rendu", rendre)' in b, \
        "la barre décide encore sur une page qui n'est pas rendue"
    # L'ANNONCE EST FAITE AUX DEUX ENDROITS QUI POSENT LES CARTES : le rendu
    # du fil, et le rafraîchissement au retour depuis le cache.
    assert v.count("annoncerFil();") == 2, v.count("annoncerFil();")
