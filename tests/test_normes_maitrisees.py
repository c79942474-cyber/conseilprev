# -*- coding: utf-8 -*-
"""LES SEPT NORMES DE L'ACCUEIL, ET LE CHEMIN JUSQU'AU MODULE.

CE QUI A DÉCLENCHÉ CE FICHIER. Une demande : « dans ce menu, connecter chaque
bloc concerné au module de la mise en conformité correspondant dans Sentinel
(sauf DORA) et aller à la page de la norme concernée ».

CE QUE LA MESURE A TROUVÉ AVANT D'ÉCRIRE UNE LIGNE, et qui rendait la demande
irréalisable telle quelle :

    /sentinel?goto=iso27001-risques  →  302  /login

    La destination demandée était PERDUE à la porte. Le visiteur se
    connectait et atterrissait sur l'accueil de Sentinel, à quatre-vingt-dix
    onglets de ce qu'il avait cliqué. Rien ne signalait la perte : la
    connexion avait réussi, une page s'affichait.

ET C'EST LE CAS NORMAL, PAS LE CAS LIMITE. Un lien posé sur la page d'accueil
PUBLIQUE s'adresse par construction à quelqu'un qui n'est pas connecté : sans
cette correction, les six liens n'auraient servi que les visiteurs déjà entrés
— c'est-à-dire pas ceux qu'ils visent.

LA CHAÎNE QUE CES RÈGLES GARDENT, MAILLON PAR MAILLON
  1. la carte porte un lien vers /sentinel?goto=<panneau> ;
  2. la porte de Sentinel reporte cette destination dans ?suite= ;
  3. la page de connexion n'accepte que des chemins internes — sinon elle
     deviendrait un tremplin d'hameçonnage sous notre nom de domaine ;
  4. `hubGo` retrouve l'onglet par son `onclick`, donc chaque cible doit
     exister comme PANNEAU et comme ONGLET, une fois et une seule.

Un maillon rompu quelque part et le lien mène à une page vide, sans que rien
ne tombe ailleurs : c'est pourquoi les quatre sont mesurés séparément.

CE QUE CES RÈGLES NE PEUVENT PAS FAIRE. Ouvrir un navigateur : /sentinel exige
une authentification, et la peinture du panneau se fait en JavaScript après
chargement. Elles vérifient que chaque maillon tient ; elles ne regardent pas
l'écran final.
"""
import io
import os
import re

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = io.open(os.path.join(_RACINE, "index.html"), encoding="utf-8").read()
SENTINEL = io.open(os.path.join(_RACINE, "sentinel.html"), encoding="utf-8").read()
APP = io.open(os.path.join(_RACINE, "app.py"), encoding="utf-8").read()
LOGIN = io.open(os.path.join(_RACINE, "login.page.js"), encoding="utf-8").read()
INDEXJS = io.open(os.path.join(_RACINE, "index.page.js"), encoding="utf-8").read()

#: LA TABLE DE CE QUE LA DEMANDE A DEMANDÉ. Elle est écrite ici une seule
#: fois ; plusieurs règles la parcourent, et la tenir à deux endroits aurait
#: garanti qu'une norme neuve soit contrôlée par l'une et ignorée par l'autre.
ATTENDUES = (
    ("IA Act", "ia-act-hub"),
    ("CRA", "cra-role"),
    ("ISO 42001", "iso42001"),
    ("ISO 27001", "iso27001-risques"),
    ("NIS2", "nis2-qualifier"),
    ("RGPD", "rgpd-hub"),
)

#: LES IDENTIFIANTS DE PARAMÈTRE NE PORTENT PAS D'ESPACE, et ce n'est pas
#: cosmétique : « ISO 27001 » rend un nom de règle qui se coupe en deux dès
#: qu'on lit une ligne `FAILED` mot à mot — un banc de mutations, un filtre
#: `-k`, un rapport. Le nom devient introuvable, et la règle passe pour
#: absente alors qu'elle a bien levé.
IDS = [n.replace(" ", "-") for n, _p in ATTENDUES]

#: LA SEULE EXCLUE, ET C'EST UNE DÉCISION — aucun module Sentinel ne couvre
#: DORA. Une carte muette au milieu de six cliquables se lirait comme un lien
#: cassé ; elle mène donc au texte officiel, et le dit.
SANS_MODULE = "DORA"


def _bloc():
    d = INDEX.index('<div class="ng">')
    return INDEX[d:INDEX.index('</div>\n  </div>', d)]


def _cartes():
    """Les cartes du bloc, découpées sur leur balise ouvrante."""
    bloc = _bloc()
    bornes = [m.start() for m in re.finditer(r'<div class="nc[ "]', bloc)]
    bornes.append(len(bloc))
    return [bloc[bornes[i]:bornes[i + 1]] for i in range(len(bornes) - 1)]


def _carte(nom):
    for c in _cartes():
        m = re.search(r'<div class="nn">([^<]+)</div>', c)
        if m and m.group(1).strip().rstrip(" ↗") == nom:
            return c
    return None


# ═══════════════════════════════════════════════════════════════════════════
#  1. LE BLOC — SEPT CARTES, ET LE TITRE QUI LES COMPTE
# ═══════════════════════════════════════════════════════════════════════════

def test_le_titre_compte_EXACTEMENT_les_cartes_du_bloc():
    """LE TITRE COMPTE, ET LA GRILLE AUSSI. Un titre qui annonce un nombre et
    une grille qui en montre un autre est le genre de mensonge qu'on ne voit
    jamais, parce que personne ne recompte.

    LE NOMBRE N'EST PLUS ÉCRIT ICI, ET C'EST LE POINT. Cette règle figeait
    « 7 » ; elle est tombée le jour où deux normes se sont ajoutées, alors
    que le produit était juste et le titre à jour. Une règle qui fige un
    compte interdit d'en ajouter un — elle ne protège pas l'accord entre le
    titre et la grille, elle protège un chiffre. Elle DÉRIVE désormais le
    nombre du titre et le compare aux cartes réellement présentes.
    """
    cartes = _cartes()
    annonce = re.search(r'"nr\.ttl":"(\d+) normes', INDEXJS)
    assert annonce, "le titre du bloc n'annonce plus aucun nombre"
    n = int(annonce.group(1))
    assert len(cartes) == n, (
        "le titre annonce %d normes, la grille en montre %d" % (n, len(cartes)))
    noms = sorted(re.findall(r'<div class="nn">([^<]+)</div>', _bloc()))
    assert len(noms) == n, "%d noms pour %d cartes : %s" % (len(noms), n, noms)
    # LE GARDE-FOU : un bloc vide ferait passer 0 == 0.
    assert n >= 5, "le bloc n'annonce plus que %d normes" % n


def test_la_lecture_du_bloc_n_est_pas_vide():
    """LE GARDE-FOU DES RÈGLES SUIVANTES. Une lecture qui rendrait zéro carte
    ferait passer toutes les comparaisons pour des comparaisons de vides —
    c'est arrivé une fois dans ce dépôt, et la recette est restée verte."""
    assert len(_bloc()) > 800
    assert len(_cartes()) > 5


# ═══════════════════════════════════════════════════════════════════════════
#  2. MAILLON 1 — LA CARTE MÈNE AU MODULE
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("nom,panneau", ATTENDUES, ids=IDS)
def test_chaque_carte_mene_au_module_sentinel_de_sa_norme(nom, panneau):
    c = _carte(nom)
    assert c, "carte « %s » introuvable dans le bloc" % nom
    m = re.search(r'class="nc-go" href="([^"]+)"', c)
    assert m, "la carte « %s » ne porte aucun lien de corps" % nom
    assert m.group(1) == "/sentinel?goto=%s" % panneau, (
        "la carte « %s » mène à %r au lieu du module %s"
        % (nom, m.group(1), panneau))


@pytest.mark.parametrize("nom,panneau", ATTENDUES, ids=IDS)
def test_c_est_la_CARTE_ENTIERE_qui_est_cliquable_et_pas_l_icone_seule(nom, panneau):
    """CE QUI EXISTAIT, ET QUE CETTE RÈGLE EMPÊCHE DE REVENIR. Le lien ne
    couvrait que l'icône et le nom — une cible de quelques dizaines de pixels
    au milieu d'un bloc qui, lui, réagit au survol tout entier. Le lecteur
    vise la carte et ne clique rien.

    LA RÈGLE MESURE QUE LES TROIS PARTIES sont DANS le lien : l'icône, le
    nom, et la description."""
    c = _carte(nom)
    d = c.index('class="nc-go"')
    f = c.index("</a>", d)
    dedans = c[d:f]
    for classe in ("ni", "nn", "nd"):
        assert 'class="%s"' % classe in dedans, (
            "la carte « %s » laisse « %s » HORS du lien : la zone cliquable "
            "ne couvre pas la carte entière" % (nom, classe))


def test_le_rembourrage_de_la_carte_est_DANS_le_lien():
    """CE QUE LE NAVIGATEUR A MESURÉ, ET QU'AUCUNE LECTURE DU BALISAGE NE
    DONNE. Écrit d'abord sans cette précaution, le lien couvrait 58 % de la
    carte : les 20 px de rembourrage restaient DEHORS, et un clic dans le
    pourtour — c'est-à-dire sur tout le tour de la carte — ne faisait rien.
    Le balisage était pourtant parfait : les trois parties étaient bien dans
    le lien.

    LA CORRECTION EST UN DÉPLACEMENT DE RÈGLE, pas un ajout : le rembourrage
    passe de `.nc` à `.nc-go`, l'œil ne voit aucune différence, et la
    couverture passe à 98 % — les 2 % restants étant la bordure d'un pixel.
    """
    plat = INDEX.replace(" ", "").replace("\n", "")
    assert ".nc-go{display:block;padding:20px14px;" in plat, (
        "le rembourrage n'est pas porté par le lien : le pourtour de la "
        "carte redeviendra mort au clic")
    assert ".nc.nc-lie,.nc.nc-ext{cursor:pointer;padding:0}" in plat, (
        "la carte garde son propre rembourrage EN PLUS de celui du lien : "
        "les deux s'ajoutent et le pourtour reste hors du lien")


def test_les_cartes_liees_annoncent_une_zone_cliquable():
    """UNE CARTE QUI MÈNE QUELQUE PART ET GARDE `cursor:default` ne se
    signale pas : rien ne dit au lecteur qu'il peut cliquer. Et `.nc` porte
    justement `cursor:default` — c'est de lui qu'il faut reprendre la main.

    ═══ CETTE RÈGLE ÉTAIT INFALSIFIABLE ═════════════════════════════════
    Sa première version se terminait par `assert … or ".nc-lie" in INDEX` :
    la seconde branche suffisait à la rendre verte, et la classe `.nc-lie`
    figure partout dans le bloc. Elle ne pouvait donc PAS tomber. Le `or`
    est parti."""
    plat = INDEX.replace(" ", "").replace("\n", "")
    assert "cursor:pointer" in plat[plat.index(".nc.nc-lie"):
                                    plat.index(".nc.nc-lie") + 80], (
        "les cartes-liens n'annoncent pas de zone cliquable")
    assert ".nc-go{display:block" in plat, (
        "le lien de carte n'est pas en bloc : il ne couvrirait pas la carte")
    # ET LE TÉMOIN QUI DONNE SON SENS À LA RÈGLE : sans reprise, `.nc` impose
    # `cursor:default` à tout le monde.
    assert "cursor:default" in plat, (
        "`.nc` ne porte plus `cursor:default` : cette règle ne reprend plus "
        "rien à personne et ne mesure plus rien")


# ═══════════════════════════════════════════════════════════════════════════
#  3. MAILLON 4 — `hubGo` DOIT POUVOIR RETROUVER L'ONGLET
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("nom,panneau", ATTENDUES, ids=IDS)
def test_chaque_cible_existe_comme_panneau_ET_comme_onglet(nom, panneau):
    """CE DONT `hubGo` A BESOIN, ET RIEN D'AUTRE. Il cherche
    `.sb-item[onclick*="go('<id>'"]` et clique dessus. Sans onglet, le lien
    mène à Sentinel et il ne se passe RIEN — la page reste sur l'accueil, et
    aucune erreur ne paraît."""
    assert 'id="p-%s"' % panneau in SENTINEL, (
        "le panneau p-%s n'existe pas : le lien de la carte « %s » mène "
        "nulle part" % (panneau, nom))
    onglets = SENTINEL.count("go('%s'," % panneau)
    assert onglets == 1, (
        "%d onglet(s) portent go('%s') : hubGo en prend UN, et s'il y en a "
        "zéro il ne se passe rien" % (onglets, panneau))


def test_hubGo_cherche_bien_l_onglet_par_son_onclick():
    """LE MAILLON MESURÉ DANS LE MOTEUR, et pas supposé. Si `hubGo` changeait
    de stratégie — un `data-` attribut, un identifiant —, les règles
    ci-dessus vérifieraient une convention que plus personne n'emploie."""
    js = io.open(os.path.join(_RACINE, "sentinel.page.js"),
                 encoding="utf-8").read()
    d = js.index("window.hubGo = function(id)")
    corps = js[d:js.index("\n", d)]
    assert "sb-item" in corps and "onclick" in corps, (
        "hubGo ne cherche plus l'onglet par son onclick : %r" % corps[:160])
    assert ".click()" in corps, (
        "hubGo ne clique plus l'onglet : le module ne s'amorcerait pas")


def test_le_lien_profond_lit_bien_le_parametre_goto():
    """LE MAILLON QUI RELIE L'URL AU MOTEUR."""
    js = io.open(os.path.join(_RACINE, "sentinel.page.js"),
                 encoding="utf-8").read()
    d = js.index("window.sentinelGotoDeepLink")
    corps = js[d:js.index("\n", d)]
    assert "'goto'" in corps, "le lien profond ne lit plus ?goto="
    assert "hubGo" in corps
    assert "addEventListener('load', window.sentinelGotoDeepLink)" in js, (
        "le lien profond n'est plus appelé au chargement")


# ═══════════════════════════════════════════════════════════════════════════
#  4. MAILLON 2 — LA PORTE GARDE LA DESTINATION
# ═══════════════════════════════════════════════════════════════════════════
#
#  LES DEUX RÈGLES CI-DESSOUS TRAVERSENT L'APPLICATION RÉELLE.
#  LE CLIENT DE RECETTE N'ENVOIE NI `Accept-Language` NI `Accept-Encoding` :
#  le middleware anti-scanner rend alors 404 sur toute page — un navigateur
#  envoie les deux. Sans ces en-têtes, les règles mesureraient le middleware
#  et non la porte.

_NAVIGATEUR = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/120",
               "Accept-Language": "fr-FR,fr;q=0.9",
               "Accept-Encoding": "gzip, deflate"}


@pytest.fixture(scope="module")
def client():
    os.environ.setdefault("FLASK_ENV", "testing")
    import app as A
    return A.app.test_client()


@pytest.mark.parametrize("nom,panneau", ATTENDUES, ids=IDS)
def test_la_destination_demandee_SURVIT_a_la_porte(client, nom, panneau):
    """LE DÉFAUT MESURÉ AVANT CORRECTION, ET IL ÉTAIT SILENCIEUX.

        /sentinel?goto=iso27001-risques  →  302  /login

    Le visiteur se connectait et se retrouvait sur l'accueil de Sentinel. La
    connexion avait réussi, une page s'affichait, rien n'indiquait la perte —
    il ne restait qu'à chercher parmi quatre-vingt-dix onglets."""
    cible = "/sentinel?goto=%s" % panneau
    r = client.get(cible, headers=_NAVIGATEUR, follow_redirects=False)
    assert r.status_code == 302, (
        "un visiteur anonyme doit être renvoyé vers la connexion : %s"
        % r.status_code)
    loc = r.headers.get("Location") or ""
    assert loc.startswith("/login?suite="), (
        "la porte renvoie vers %r sans reporter la destination : le clic sur "
        "« %s » se perdra" % (loc, nom))
    assert panneau in loc, (
        "le panneau demandé (%s) ne survit pas dans %r" % (panneau, loc))


def test_la_porte_reporte_aussi_une_destination_SANS_parametre(client):
    """LE TÉMOIN QUI INTERDIT DE NE TRAITER QUE LE CAS `?goto=`. Un
    `full_path` nu se termine par « ? » ; le laisser produirait
    /login?suite=/sentinel? — un chemin qui marche par chance."""
    r = client.get("/sentinel", headers=_NAVIGATEUR, follow_redirects=False)
    assert r.headers.get("Location") == "/login?suite=/sentinel", (
        "destination mal reportée : %r" % r.headers.get("Location"))


def test_une_API_reste_en_401_et_ne_redirige_PAS(client):
    """LE TÉMOIN INVERSE, et il compte. Renvoyer une requête d'API vers une
    page de connexion rendrait du HTML là où du JSON est attendu : l'écran
    afficherait une erreur d'analyse au lieu de « connectez-vous ».

    ═══ CE QUE LA BATTERIE DE MUTATIONS A MONTRÉ ════════════════════════
    La première version interrogeait /api/registre — qui rend bien 401, mais
    DEPUIS SON CORPS, pas depuis `@sentinel_login_required`. Supprimer la
    branche d'API du décorateur ne la faisait donc pas tomber : la règle
    passait pour une raison sans rapport avec ce qu'elle prétend garder.
    Elle interroge désormais une route RÉELLEMENT décorée."""
    r = client.get("/api/notifications/summary", headers=_NAVIGATEUR,
                   follow_redirects=False)
    assert r.status_code == 401, (
        "une requête d'API doit recevoir 401, pas une redirection : %s %s"
        % (r.status_code, r.headers.get("Location")))
    assert "Authentification" in (r.get_json() or {}).get("error", "")
    # ET LA ROUTE INTERROGÉE PASSE BIEN PAR LA GARDE — sinon la règle
    # mesurerait à nouveau autre chose qu'elle-même.
    d = APP.index("@app.route('/api/notifications/summary'")
    assert "@sentinel_login_required" in APP[d:d + 200], (
        "/api/notifications/summary n'est plus derrière la garde : la règle "
        "ne mesure plus le décorateur")


# ═══════════════════════════════════════════════════════════════════════════
#  5. MAILLON 3 — LA PAGE DE CONNEXION N'EST PAS UN TREMPLIN
# ═══════════════════════════════════════════════════════════════════════════

def test_la_destination_reportee_ne_peut_etre_qu_un_chemin_interne():
    """CE QUE CETTE RÈGLE EMPÊCHE, ET QUI SERAIT GRAVE. Un `?suite=` acceptant
    une URL absolue ferait de la page de connexion un REDIRECT OUVERT :
    /login?suite=https://ailleurs.exemple emmènerait un visiteur hors du site
    en lui laissant croire qu'il y est resté — un tremplin d'hameçonnage sous
    notre propre nom de domaine.

    LA GARDE EXISTE DES DEUX CÔTÉS, et les deux sont vérifiés : le serveur
    (`_suite_sure`) et la page (`__suiteSure`)."""
    import app as A
    for mauvais in ("https://ailleurs.exemple/piege", "//ailleurs.exemple",
                    "\\\\ailleurs", "javascript:alert(1)", ""):
        assert A._suite_sure(mauvais) == "/sentinel", (
            "le serveur accepte une destination externe : %r" % mauvais)
    assert A._suite_sure("/sentinel?goto=nis2-qualifier") \
        == "/sentinel?goto=nis2-qualifier"
    # ET LA MÊME GARDE CÔTÉ PAGE : c'est elle qui décide vraiment où le
    # navigateur part après la connexion.
    d = LOGIN.index("function __suiteSure()")
    corps = LOGIN[d:LOGIN.index("function __authDest", d)]
    assert "charAt(0) !== '/'" in corps, (
        "la page de connexion n'exige plus un chemin absolu interne")
    assert "'//'" in corps, "la page n'écarte plus les URL protocol-relative"
    assert "'\\\\'" in corps, "la page n'écarte plus l'antislash"


def test_la_page_de_connexion_emploie_bien_la_destination_reportee():
    """UNE GARDE QUI NETTOIE UNE VALEUR QUE PERSONNE N'EMPLOIE ne protège
    rien."""
    d = LOGIN.index("function __authDest()")
    corps = LOGIN[d:LOGIN.index("\n}", d)]
    assert "__suiteSure()" in corps, (
        "la destination reportée n'est pas employée après connexion")


# ═══════════════════════════════════════════════════════════════════════════
#  6. LA SOURCE OFFICIELLE SURVIT, ET DORA DIT POURQUOI IL EST À PART
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("nom,_p", ATTENDUES, ids=IDS)
def test_la_source_officielle_reste_atteignable(nom, _p):
    """CE QUE LE CÂBLAGE NE DOIT PAS DÉTRUIRE. Les liens vers EUR-Lex et
    ISO.org existaient et valaient quelque chose : le module dit ce que le
    texte impose, le texte fait foi. Les remplacer purement et simplement
    aurait perdu la seule chose vérifiable de la carte."""
    c = _carte(nom)
    m = re.search(r'class="nc-src" href="(https://[^"]+)"', c)
    assert m, "la carte « %s » ne cite plus sa source officielle" % nom
    assert 'target="_blank"' in c and 'rel="noopener"' in c, (
        "la source de « %s » s'ouvre sans précaution d'onglet" % nom)


def test_la_source_n_est_PAS_imbriquee_dans_le_lien_de_carte():
    """UN <a> DANS UN <a> EST INVALIDE, et les navigateurs le réparent en
    cassant les deux : la carte cesserait de mener au module ET la source
    deviendrait inatteignable. La pastille est donc un FRÈRE, posé sur la
    carte par la feuille de style."""
    for c in _cartes():
        if 'class="nc-src"' not in c:
            continue
        d = c.index('class="nc-go"')
        f = c.index("</a>", d)
        assert 'class="nc-src"' not in c[d:f], (
            "une source est imbriquée dans le lien de carte : les deux liens "
            "seront cassés")
    assert ".nc-src{position:absolute" in INDEX, (
        "la pastille de source n'est plus positionnée sur la carte")


def test_DORA_est_la_SEULE_sans_module_et_le_dit():
    """UNE CARTE MUETTE AU MILIEU DE SIX CLIQUABLES SE LIT COMME UN LIEN
    CASSÉ. Celle-ci mène au texte officiel — sur toute sa surface, ce qui est
    déjà mieux qu'avant — et son intitulé annonce qu'aucun module ne la
    couvre, au lieu de laisser le lecteur le découvrir en cliquant."""
    c = _carte(SANS_MODULE)
    assert c, "la carte DORA a disparu"
    m = re.search(r'class="nc-go" href="([^"]+)"', c)
    assert m and m.group(1).startswith("https://"), (
        "DORA doit mener au texte officiel : %r" % (m.group(1) if m else None))
    assert "/sentinel" not in c, (
        "DORA a reçu un module Sentinel — la demande l'excluait explicitement")
    assert "Aucun module Sentinel" in c, (
        "la carte DORA ne dit pas pourquoi elle est à part")
    # ET C'EST BIEN LA SEULE : toutes les autres mènent à Sentinel.
    sans = [re.search(r'<div class="nn">([^<]+)</div>', x).group(1).strip()
            for x in _cartes()
            if 'href="/sentinel' not in x]
    assert sans == ["DORA ↗"], (
        "ces cartes ne mènent à aucun module : %s" % sans)


def test_aucune_carte_liee_au_module_ne_porte_la_fleche_d_ouverture_externe():
    """LA FLÈCHE ↗ DIT « CE LIEN SORT DU SITE ». La laisser sur une carte qui
    mène désormais à Sentinel ferait promettre le contraire de ce qui se
    passe — et c'est exactement le genre de détail qu'on ne relit jamais."""
    for nom, _p in ATTENDUES:
        c = _carte(nom)
        m = re.search(r'<div class="nn">([^<]+)</div>', c)
        assert "↗" not in m.group(1), (
            "la carte « %s » mène à Sentinel et garde la flèche d'ouverture "
            "externe : %r" % (nom, m.group(1)))
    # ET LA SEULE QUI SORT VRAIMENT LA GARDE.
    assert "↗" in re.search(r'<div class="nn">([^<]+)</div>',
                            _carte(SANS_MODULE)).group(1)


def test_le_libelle_ecrit_dans_le_HTML_n_est_pas_ECRASE_par_le_dictionnaire():
    """CE QUE LA CAPTURE A MONTRÉ, ET QUE JE N'AURAIS PAS VU AUTREMENT.

    La mention « — texte seul » de la carte DORA avait été écrite dans le
    HTML seulement. Or `data-i18n` fait que le dictionnaire ÉCRASE le contenu
    au chargement : la mention était MORTE, en français comme en anglais, et
    la page rendue disait simplement « Résilience num. ». Le HTML avait
    raison et l'écran disait autre chose.

    LA RÈGLE MESURE LES TROIS ENDROITS : l'intitulé du HTML, et les deux
    dictionnaires. Un libellé qui porte une information ne la porte vraiment
    que s'il la porte partout."""
    import json
    c = _carte(SANS_MODULE)
    inline = re.search(r'<div class="nd" data-i18n="nr\.dora">([^<]+)</div>',
                       c).group(1)
    assert "texte seul" in inline, (
        "l'intitulé DORA du HTML ne signale plus l'absence de module : %r"
        % inline)
    dicos = {}
    for lg in ("fr", "en"):
        m = re.search(r"\n\s*%s:JSON\.parse\(`(.*?)`\)" % lg, INDEXJS, re.S)
        assert m, "dictionnaire %s introuvable" % lg
        dicos[lg] = json.loads(m.group(1).replace("\\`", "`"))
    assert dicos["fr"]["nr.dora"] == inline, (
        "le dictionnaire français écrase l'intitulé du HTML par %r : la "
        "mention écrite dans le HTML ne s'affichera jamais"
        % dicos["fr"]["nr.dora"])
    assert "text only" in dicos["en"]["nr.dora"], (
        "la version anglaise ne signale pas l'absence de module : %r"
        % dicos["en"]["nr.dora"])


def test_chaque_cle_du_bloc_existe_dans_LES_DEUX_dictionnaires():
    """UNE CLÉ PRÉSENTE D'UN CÔTÉ SEULEMENT laisse la description en français
    sur la version anglaise — et rien ne le signale à qui relit le français."""
    import json
    cles = set(re.findall(r'data-i18n="(nr\.[a-z0-9]+)"', _bloc()))
    # AUTANT DE CLÉS QUE DE CARTES, dérivé — pas un nombre écrit ici.
    assert len(cles) == len(_cartes()), (
        "%d clés de traduction pour %d cartes" % (len(cles), len(_cartes())))
    for lg in ("fr", "en"):
        m = re.search(r"\n\s*%s:JSON\.parse\(`(.*?)`\)" % lg, INDEXJS, re.S)
        d = json.loads(m.group(1).replace("\\`", "`"))
        manquantes = sorted(k for k in cles if k not in d)
        assert not manquantes, (
            "clés absentes du dictionnaire %s : %s" % (lg, manquantes))


def test_les_libelles_traduits_survivent_au_cablage():
    """LES SEPT CLÉS `data-i18n` PILOTENT LA VERSION ANGLAISE. Les perdre en
    réécrivant le bloc aurait laissé sept descriptions figées en français,
    sans que rien ne le signale côté français."""
    cles = sorted(re.findall(r'data-i18n="(nr\.[a-z0-9]+)"', _bloc()))
    # ON N'ÉNUMÈRE PLUS LES CLÉS ATTENDUES : cette liste interdisait d'ajouter
    # une norme sans la modifier, et c'est le produit qui décide combien il y
    # en a. Ce qui se mesure ici est qu'AUCUNE carte ne perd la sienne —
    # une carte sans clé garde sa description française sur la version
    # anglaise, et rien ne le signale à qui relit le français.
    assert len(cles) == len(set(cles)), (
        "deux cartes partagent la même clé : %s" % cles)
    assert len(cles) == len(_cartes()), (
        "%d clés pour %d cartes : une carte a perdu la sienne" 
        % (len(cles), len(_cartes())))
    for socle in ("nr.ia", "nr.rgpd", "nr.nis"):
        assert socle in cles, "la clé de socle %s a disparu du bloc" % socle


@pytest.mark.parametrize("nom,_p", ATTENDUES, ids=IDS)
def test_chaque_carte_dit_ou_elle_mene_avant_qu_on_clique(nom, _p):
    """UNE CARTE QUI MÈNE DANS UN ESPACE AUTHENTIFIÉ doit le dire : le
    visiteur anonyme passera par une page de connexion, et l'apprendre après
    le clic est une mauvaise surprise."""
    c = _carte(nom)
    d = c.index('class="nc-go"')
    balise = c[d:c.index(">", d)]
    assert 'title="' in balise, "la carte « %s » ne dit pas où elle mène" % nom
    assert "Sentinel" in balise, (
        "l'infobulle de « %s » ne nomme pas Sentinel : %r" % (nom, balise))
