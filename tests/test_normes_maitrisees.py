# -*- coding: utf-8 -*-
"""LES NORMES DE L'ACCUEIL, ET LE CHEMIN JUSQU'AU MODULE.

CE QUI A DÉCLENCHÉ CE FICHIER. Une demande : « dans ce menu, connecter chaque
bloc concerné au module de la mise en conformité correspondant dans Sentinel
(sauf DORA) et aller à la page de la norme concernée ».

L'EXCEPTION EST TOMBÉE, ET C'EST LA DEMANDE SUIVANTE QUI L'A FAIT TOMBER :
« connecter et ajouter DORA à votre mise en conformité réglementaire du menu
latéral ». DORA a désormais ses quatre moteurs et son panneau ; les règles
qui le tenaient à part sont retournées plutôt que supprimées — celle qui
disait « DORA est la seule sans module » dit maintenant « AUCUNE carte n'est
sans module », et elle lève au premier ajout d'une norme sans écran.

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
    ("DORA", "dora-qualifier"),
    ("NIS2", "nis2-qualifier"),
    ("RGPD", "rgpd-hub"),
)

#: LES IDENTIFIANTS DE PARAMÈTRE NE PORTENT PAS D'ESPACE, et ce n'est pas
#: cosmétique : « ISO 27001 » rend un nom de règle qui se coupe en deux dès
#: qu'on lit une ligne `FAILED` mot à mot — un banc de mutations, un filtre
#: `-k`, un rapport. Le nom devient introuvable, et la règle passe pour
#: absente alors qu'elle a bien levé.
IDS = [n.replace(" ", "-") for n, _p in ATTENDUES]

#: PLUS AUCUNE EXCLUE. La table est vide, et elle reste écrite : une norme
#: qu'on ajouterait sans écran devrait y figurer explicitement, ce qui oblige
#: à le décider au lieu de le subir.
SANS_MODULE = ()


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

    # ── LE TITRE EST ÉCRIT DEUX FOIS, ET LA RÈGLE N'EN LISAIT QU'UN ──────
    # `data-i18n` fait que le dictionnaire remplace le titre AU CHARGEMENT ;
    # ce qui est dans le HTML est ce qu'on voit AVANT, ce que montre le code
    # source, et ce que lit un robot d'indexation. Les deux normes ajoutées
    # n'avaient été portées qu'au dictionnaire : la règle dérivait son nombre
    # de LÀ, le comparait aux cartes, et trouvait tout en ordre — pendant que
    # le HTML annonçait sept normes au-dessus d'une grille de neuf.
    repli = re.search(r'data-i18n="nr\.ttl">(\d+) normes', INDEX)
    assert repli, "le titre écrit dans le HTML n'annonce plus aucun nombre"
    assert int(repli.group(1)) == n, (
        "le titre écrit dans le HTML annonce %s normes, le dictionnaire %d — "
        "c'est le HTML qu'on lit avant que la traduction s'applique"
        % (repli.group(1), n))
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


def test_AUCUNE_carte_ne_reste_sans_module():
    """LA RÈGLE RETOURNÉE, ET ELLE MESURE PLUS QU'AVANT.

    Elle disait « DORA est la seule sans module ». DORA en a un ; la règle
    devient donc « aucune carte n'est sans module », et ce qu'elle mesure
    s'élargit : elle lève désormais au premier ajout d'une norme à la grille
    sans écran pour la corriger. C'est le défaut qu'elle existe pour
    attraper, et il n'a pas disparu avec DORA — il s'est déplacé au
    PROCHAIN ajout.
    """
    sans = [re.search(r'<div class="nn">([^<]+)</div>', x).group(1).strip()
            for x in _cartes()
            if 'href="/sentinel' not in x]
    assert sans == list(SANS_MODULE), (
        "ces cartes ne mènent à aucun module : %s. Une carte muette au milieu "
        "de dix cliquables se lit comme un lien cassé." % sans)


def test_la_carte_DORA_mene_bien_au_panneau_et_garde_sa_source():
    """CE QUE LE RECÂBLAGE DE DORA NE DOIT PAS AVOIR PERDU.

    La carte menait à EUR-Lex sur toute sa surface. En la branchant sur
    Sentinel, le risque était de perdre le texte officiel — la seule chose
    vérifiable de la carte. Il redevient la pastille, comme sur les dix
    autres.
    """
    c = _carte("DORA")
    assert c, "la carte DORA a disparu"
    m = re.search(r'class="nc-go" href="([^"]+)"', c)
    assert m and m.group(1) == "/sentinel?goto=dora-qualifier", (
        "la carte DORA ne mène pas à son panneau : %r"
        % (m.group(1) if m else None))
    s = re.search(r'class="nc-src" href="(https://[^"]+)"', c)
    assert s and "32022R2554" in s.group(1), (
        "la carte DORA a perdu le texte officiel en gagnant son module : %r"
        % (s.group(1) if s else None))


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
    # PLUS AUCUNE NE SORT : la flèche ne vit que sur la pastille de source,
    # qui est un autre lien. En laisser une sur un intitulé promettrait une
    # sortie du site qui n'a plus lieu.
    for x in _cartes():
        m = re.search(r'<div class="nn">([^<]+)</div>', x)
        assert "↗" not in m.group(1), (
            "un intitulé de carte porte encore la flèche externe : %r"
            % m.group(1))


def test_le_libelle_ecrit_dans_le_HTML_n_est_pas_ECRASE_par_le_dictionnaire():
    """CE QUE LA CAPTURE A MONTRÉ, ET QUE JE N'AURAIS PAS VU AUTREMENT.

    La mention « — texte seul » de la carte DORA avait été écrite dans le
    HTML seulement. Or `data-i18n` fait que le dictionnaire ÉCRASE le contenu
    au chargement : la mention était MORTE, en français comme en anglais, et
    la page rendue disait simplement « Résilience num. ». Le HTML avait
    raison et l'écran disait autre chose.

    LA MENTION A DISPARU AVEC L'EXCEPTION — mais le défaut qu'elle a révélé,
    lui, reste entier : c'est lui que la règle mesure, sur le même libellé.
    Les trois endroits doivent dire la même chose, et aucun des trois ne doit
    promettre un texte seul alors que le module existe.

    LA RÈGLE MESURE LES TROIS ENDROITS : l'intitulé du HTML, et les deux
    dictionnaires. Un libellé qui porte une information ne la porte vraiment
    que s'il la porte partout."""
    import json
    c = _carte("DORA")
    inline = re.search(r'<div class="nd" data-i18n="nr\.dora">([^<]+)</div>',
                       c).group(1)
    assert "texte seul" not in inline and "module" not in inline.lower(), (
        "l'intitulé DORA du HTML annonce encore une absence de module : %r"
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
    assert "text only" not in dicos["en"]["nr.dora"], (
        "la version anglaise annonce encore une absence de module : %r"
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


# ══════════════════════════════════════════════════════════════════════════
#  LE BANDEAU DE CHIFFRES, ET CE QU'IL DOIT À LA PAGE QUI LE PORTE
# ══════════════════════════════════════════════════════════════════════════
#
# CE QUE PERSONNE NE GARDAIT. Le bandeau « 32 · 8 · 25 · 44 · 37 » n'était
# tenu par aucune règle. Il annonçait SIX normes couvertes à trente-cinq
# lignes d'un titre qui en revendique NEUF maîtrisées — et personne ne
# recompte un bandeau de chiffres. C'est le défaut déjà payé une fois dans
# ce fichier, sous une autre forme : un nombre écrit à la main qui cesse de
# correspondre à ce que la page montre.
#
# CE QUI EST MESURÉ, ET CE QUI NE PEUT PAS L'ÊTRE. « Normes couvertes » est
# une revendication du cabinet : rien dans le produit n'énumère vingt-cinq
# normes, et une règle qui figerait ce nombre interdirait d'en ajouter une
# sans rien prouver. Ce qui SE mesure, c'est la relation : on ne peut pas
# maîtriser plus de normes qu'on n'en couvre. Le bandeau doit donc rester
# supérieur ou égal à ce que le bloc des normes maîtrisées revendique — et
# c'est exactement l'accord qui était rompu.


def _bandeau():
    """{clé de traduction: nombre} du bandeau de chiffres de l'accueil."""
    i = INDEX.index('<div class="sb2">')
    #  ON S'ARRÊTE À LA SECTION SUIVANTE, pas au premier `</div></div>` venu :
    #  celui-ci tombe AVANT la fin du bandeau, et la lecture ne rendait qu'une
    #  seule case — trois règles rouges pour une borne mal posée.
    return {cle: int(n) for n, cle in re.findall(
        r'<div class="sn">(\d+)</div><div class="slb" data-i18n="(stats\.[a-e])"',
        INDEX[i:INDEX.index("<section", i)])}


def test_le_bandeau_de_chiffres_se_lit_encore():
    """LE GARDE-FOU DES DEUX RÈGLES SUIVANTES. Si la forme du bandeau change,
    elles compareraient des cases vides en restant vertes."""
    b = _bandeau()
    assert len(b) == 5, (
        "%d chiffre(s) relevés sur 5 : le bandeau a changé de forme et les "
        "règles qui le lisent ne prouvent plus rien — %s" % (len(b), b))
    assert all(v > 0 for v in b.values()), b


def test_on_ne_MAITRISE_pas_plus_de_normes_qu_on_n_en_COUVRE():
    """LA RELATION QUI ÉTAIT ROMPUE, ET QUI NE SE VOYAIT PAS.

    Le bandeau annonçait « 6 normes couvertes ». Trente-cinq lignes plus
    bas, le même écran titrait « 9 normes maîtrisées » au-dessus d'une
    grille de neuf cartes. Couvrir moins qu'on ne maîtrise n'est pas une
    approximation, c'est une impossibilité — et c'est le genre d'erreur
    qu'un visiteur attentif relève avant nous.

    LA RÈGLE NE FIGE AUCUN DES DEUX NOMBRES. Elle les dérive tous les deux,
    l'un du bandeau, l'autre du titre déjà tenu par la première règle de ce
    fichier, et n'exige que leur ordre."""
    couvertes = _bandeau()["stats.c"]
    annonce = re.search(r'"nr\.ttl":"(\d+) normes', INDEXJS)
    assert annonce, "le titre du bloc n'annonce plus aucun nombre"
    maitrisees = int(annonce.group(1))
    assert couvertes >= maitrisees, (
        "le bandeau annonce %d normes COUVERTES et le bloc %d normes "
        "MAÎTRISÉES : on ne peut pas maîtriser ce qu'on ne couvre pas"
        % (couvertes, maitrisees))


def test_le_bandeau_compte_les_risques_que_la_page_MONTRE():
    """LE SEUL CHIFFRE DU BANDEAU QUI SOIT VÉRIFIABLE SUR LA PAGE MÊME.

    « Risques systémiques » n'est pas une revendication : la section
    #risques en aligne les cartes, et le nombre doit être celui-là. Les
    trois autres — années d'expertise, jeux de données indexés,
    organisations — ne se comptent nulle part dans ce dépôt ; les figer ici
    donnerait l'illusion d'un contrôle qui ne regarde rien."""
    i = INDEX.index('id="risques"')
    cartes = INDEX[i:INDEX.index("</section>", i)].count('<div class="risk-card">')
    assert cartes > 0, "aucune carte de risque relevée : la lecture a changé"
    assert _bandeau()["stats.b"] == cartes, (
        "le bandeau annonce %d risques systémiques, la section en montre %d"
        % (_bandeau()["stats.b"], cartes))


def test_aucun_attribut_de_traduction_n_est_ECRIT_DEUX_FOIS():
    """CINQ BALISES DU BANDEAU PORTAIENT `data-i18n` EN DOUBLE. Un analyseur
    HTML garde le premier et jette le second sans rien dire : inoffensif
    tant que les deux valeurs coïncident, invisible le jour où elles
    divergent — et c'est alors la seconde, celle qu'on vient d'écrire, qui
    est ignorée."""
    doubles = re.findall(r'data-i18n="([^"]*)" data-i18n="\1"', INDEX)
    assert not doubles, (
        "%d balise(s) répètent leur attribut de traduction : %s"
        % (len(doubles), sorted(set(doubles))))
