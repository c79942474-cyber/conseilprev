"""LA SÉCURITÉ ET LA VIE PRIVÉE — vérifiées sur des réponses réelles.

POURQUOI CE FICHIER EXISTE. Les en-têtes de sécurité sont la partie du code
que personne ne regarde jamais : ils ne cassent rien quand ils disparaissent,
et le site continue de se servir en paraissant identique. Un `after_request`
supprimé par mégarde, une directive `unsafe-inline` ajoutée « le temps de
déboguer », un `<link>` vers une police distante recopié d'une autre page — les
trois passent inaperçus au navigateur et se découvrent un an plus tard.

CE QUI EST VÉRIFIÉ ICI EST DONC LE RÉSULTAT, PAS L'INTENTION : des requêtes
réelles au client de test, et le texte des pages servies. Un contrôle qui
lirait `app.py` à la recherche de la chaîne « Content-Security-Policy »
passerait le jour où l'en-tête serait posé mais jamais renvoyé.

ET LA PROMESSE DE CONFIDENTIALITÉ EST TRAITÉE COMME UNE RÈGLE ÉDITORIALE, pas
comme un texte : « aucune requête vers un tiers » n'est pas une phrase de la
page de confidentialité, c'est une propriété des fichiers servis, et elle est
mesurée.
"""
import os
import re
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

import app as A  # noqa: E402


def _lire(nom):
    return open(os.path.join(ICI, nom), encoding="utf-8").read()


PAGES = ("index.html", "fiche.html", "abonnement.html", "confronter.html",
         "confidentialite.html")


def client():
    A.app.config["TESTING"] = True
    return A.app.test_client()


# ── 1. Les en-têtes, sur des réponses réelles ─────────────────────────────

def test_les_entetes_accompagnent_toute_reponse():
    """Une page, une feuille de style, une interface, une erreur : les quatre
    passent par le même `after_request`. Un en-tête posé sur les seules pages
    HTML laisserait les réponses JSON — celles qui portent les données d'un
    compte — sans protection."""
    c = client()
    for chemin in ("/", "/confidentialite", "/veille.css", "/api/sante",
                   "/fiche/inexistante-xyz"):
        r = c.get(chemin)
        for entete in ("Content-Security-Policy", "X-Content-Type-Options",
                       "X-Frame-Options", "Referrer-Policy",
                       "Permissions-Policy", "Cross-Origin-Opener-Policy",
                       "Cross-Origin-Resource-Policy"):
            assert entete in r.headers, "%s manque sur %s" % (entete, chemin)


def test_la_politique_de_contenu_est_fermee():
    """`default-src 'self'` sans exception — et surtout, aucune des deux
    échappatoires qui vident une politique de son sens."""
    csp = client().get("/").headers["Content-Security-Policy"]
    assert "default-src 'self'" in csp
    for interdit in ("unsafe-inline", "unsafe-eval", "*", "data: script",
                     "https://"):
        assert interdit not in csp, "%s dans la politique : %s" % (interdit, csp)
    # Les directives qu'on oublie, et qui sont justement les plus utiles.
    for exige in ("base-uri 'none'", "frame-ancestors 'none'",
                  "object-src 'none'", "form-action 'self'"):
        assert exige in csp, exige


def test_hsts_seulement_sur_connexion_chiffree():
    """Envoyé en clair, il est ignoré ; posé en développement sur `localhost`,
    il verrouillerait le poste du développeur sur du HTTPS que rien n'y sert.
    Render termine le TLS en amont : `X-Forwarded-Proto` fait foi."""
    c = client()
    assert "Strict-Transport-Security" not in c.get("/").headers
    r = c.get("/", headers={"X-Forwarded-Proto": "https"})
    assert "max-age=31536000" in r.headers.get("Strict-Transport-Security", "")


def test_aucun_cookie_n_est_pose():
    """La page de confidentialité affirme « aucun cookie ». Ce contrôle est ce
    qui empêche cette phrase de devenir fausse sans que personne ne s'en
    aperçoive."""
    c = client()
    for chemin in ("/", "/confidentialite", "/api/sante", "/api/veille/referentiel"):
        assert not c.get(chemin).headers.getlist("Set-Cookie"), chemin
    py = _lire("app.py")
    assert "set_cookie" not in py
    for nom in ("abonnes.py", "classeur.py", "confrontation.py"):
        assert "cookie" not in _lire(nom).lower(), nom


# ── 2. Aucun tiers, et c'est mesuré ───────────────────────────────────────

def test_aucune_page_n_appelle_un_tiers():
    """« Aucune requête vers un tiers » n'est pas une promesse : c'est une
    propriété des fichiers servis. Une police distante recopiée d'une autre
    page enverrait à nouveau l'adresse IP du lecteur à Google, sans que rien à
    l'écran ne change."""
    for nom in PAGES:
        h = _lire(nom)
        # On retire les commentaires HTML : ils PARLENT de fonts.googleapis.com,
        # et c'est justement leur travail de dire pourquoi il n'y est plus.
        sans = re.sub(r"<!--.*?-->", "", h, flags=re.S)
        externes = re.findall(r'(?:src|href)="(https?://[^"]+)"', sans)
        assert not externes, "%s appelle %s" % (nom, externes)


def test_aucune_feuille_ni_aucun_script_ne_charge_un_tiers():
    """Le même contrôle sur ce que les pages incluent : une adresse externe
    dans `@import` ou dans un `fetch` contournerait le contrôle précédent."""
    fichiers = sorted(f for f in os.listdir(ICI)
                      if f.endswith(".js") or f.endswith(".css"))
    assert len(fichiers) >= 10, fichiers
    for nom in fichiers:
        s = _lire(nom)
        sans = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
        for m in re.finditer(r"https?://[^\s'\")]+", sans):
            raise AssertionError("%s appelle %s" % (nom, m.group(0)))


def test_les_polices_sont_au_depot_et_servies():
    """Elles ne servent à rien au dépôt si la route qui les rend n'existe pas :
    le navigateur retomberait silencieusement sur Georgia."""
    c = client()
    for f in ("Newsreader-latin", "Inter-latin", "JetBrainsMono-latin"):
        r = c.get("/polices/%s.woff2" % f)
        assert r.status_code == 200, f
        assert r.headers["Content-Type"].startswith("font/") or \
            "woff" in r.headers["Content-Type"], r.headers["Content-Type"]
    css = c.get("/polices.css")
    assert css.status_code == 200
    assert "fonts.gstatic.com" not in css.get_data(as_text=True)
    # La licence que la SIL OFL exige, avec les quatre familles nommées.
    lic = _lire("polices/LICENCE.txt")
    for fam in ("Newsreader", "Inter", "JetBrains Mono", "Liberation Serif"):
        assert fam in lic, fam


# ── 3. L'accord : ce qui est demandé, et ce qui ne l'est pas ──────────────

def test_la_memoire_de_lecture_n_ecrit_rien_sans_accord():
    """C'est la seule chose de ce site qui s'écrive toute seule. Sans accord,
    `marquer()` doit sortir AVANT toute écriture — et « sans accord » inclut
    le cas où le module de consentement n'a pas chargé : une porte absente se
    lit fermée."""
    js = _lire("lecture.js")
    i = js.index("function marquer(")
    bloc = js[i:i + 260]
    assert "!autorise()" in bloc, bloc
    assert bloc.index("!autorise()") < bloc.index("ecrire("), \
        "une écriture précède le contrôle d'accord"
    # Le défaut est le refus, y compris si `window.VP` manque.
    i = js.index("function autorise(")
    assert "window.VP && window.VP.accorde" in js[i:i + 200]


def test_le_defaut_est_le_refus():
    """Une valeur absente n'est pas « pas encore demandé, donc on peut »."""
    vp = _lire("vieprivee.js")
    i = vp.index("function accorde(")
    bloc = vp[i:i + 260]
    assert 'etat()[cle] === "oui"' in bloc, bloc


def test_retirer_son_accord_efface_ce_qui_avait_ete_garde():
    """Un consentement retiré qui ne retire rien n'est pas un consentement
    retiré."""
    vp = _lire("vieprivee.js")
    i = vp.index("function repondre(")
    bloc = vp[i:i + 500]
    assert "window.LU.oublier()" in bloc, bloc


def test_refuser_coute_exactement_un_clic_comme_accepter():
    """Le RGPD exige un consentement « libre ». Un bouton de refus plus petit,
    plus pâle ou caché derrière un second écran rend le consentement invalide —
    et c'est ce que fait la quasi-totalité des bandeaux du web."""
    vp = _lire("vieprivee.js")
    # Les deux réponses sont deux boutons frères, au même niveau.
    assert '<button type="button" class="vp-oui">' in vp
    assert '<button type="button" class="vp-non">' in vp
    css = _lire("veille.css")
    # Aucune règle ne distingue l'un de l'autre : la mise en forme est portée
    # par `.vp-a button`, qui les prend tous les deux.
    assert ".vp-a button{" in css.replace("\n", "")
    for regle in (".vp-non{", ".vp-oui{", ".vp-non:", ".vp-oui:"):
        assert regle not in css, "%s distingue une réponse de l'autre" % regle


def test_le_bandeau_ne_bloque_pas_la_lecture():
    """Un bandeau qui empêche de lire tant qu'on n'a pas cliqué obtient des
    clics, pas des consentements."""
    vp = _lire("vieprivee.js")
    for interdit in ("aria-modal", 'role="dialog"', "overflow = 'hidden'",
                     'overflow = "hidden"', "showModal"):
        assert interdit not in vp, interdit
    css = _lire("veille.css")
    i = css.index(".vp-b{")
    bloc = css[i:i + 300]
    assert "position:fixed" in bloc and "bottom:0" in bloc
    assert "inset:0" not in bloc, "le bandeau couvre l'écran"


def test_la_memoire_de_lecture_ne_sort_toujours_pas_du_navigateur():
    """La règle d'origine tient : rien de cette mémoire n'est envoyé nulle
    part. L'accord ne change pas cela — il décide si elle est TENUE, pas si
    elle est transmise."""
    for nom in ("lecture.js", "vieprivee.js"):
        s = _lire(nom)
        for interdit in ("fetch(", "XMLHttpRequest", "sendBeacon", "/api/"):
            assert interdit not in s, "%s dans %s" % (interdit, nom)


# ── 4. L'inventaire dit tout ce qui est écrit, et rien de plus ────────────

def _cles_de_stockage():
    """Toutes les clés que le site écrit, lues DANS LE CODE. L'inventaire de
    la page de confidentialité est comparé à celles-ci : une clé ajoutée sans
    y être inscrite fait tomber ce contrôle, ce qui est le seul moyen qu'une
    page de confidentialité reste vraie."""
    cles = set()
    # TOUS LES SCRIPTS SERVIS, ÉNUMÉRÉS PAR LE DOSSIER et non par une liste
    # tenue à la main. DÉFAUT TROUVÉ EN AJOUTANT `fleches.js` : la liste écrite
    # ici ne le contenait pas, et sa clé de stockage aurait pu vivre hors de
    # l'inventaire sans qu'aucun contrôle ne bouge. Un inventaire dont le
    # périmètre est lui-même tenu à la main a le défaut qu'il est censé
    # empêcher.
    for nom in sorted(f for f in os.listdir(ICI) if f.endswith(".js")):
        s = _lire(nom)
        for m in re.finditer(r'"(cpinfo\.[a-z]+)"', s):
            cles.add(m.group(1))
    # `cpinfo.essai` n'est pas une donnée : c'est l'écriture d'essai qui vérifie
    # que le stockage fonctionne, retirée dans la ligne qui suit.
    cles.discard("cpinfo.essai")
    return cles


def test_l_inventaire_est_complet():
    """Une politique de confidentialité qui oublie une entrée est fausse, et
    elle l'est en silence."""
    page = _lire("confidentialite.html")
    manquantes = sorted(c for c in _cles_de_stockage()
                        if "<code>%s</code>" % c not in page)
    assert not manquantes, "absentes de l'inventaire : %s" % manquantes


def test_l_inventaire_n_annonce_rien_qui_n_existe_pas():
    """L'inverse compte autant : annoncer une entrée retirée depuis des mois
    donne au lecteur une idée fausse de ce que le site fait — dans l'autre
    sens, mais fausse."""
    page = _lire("confidentialite.html")
    annoncees = set(re.findall(r"<code>(cpinfo\.[a-z]+)</code>", page))
    fantomes = sorted(annoncees - _cles_de_stockage())
    assert not fantomes, "annoncées mais jamais écrites : %s" % fantomes


def test_une_seule_entree_est_soumise_a_accord():
    """Si un jour une deuxième l'était, la page dirait encore « une seule
    chose vous est demandée » — et ce serait un mensonge de plus dans le seul
    texte du site qui n'a pas le droit d'en porter."""
    vp = _lire("vieprivee.js")
    i = vp.index("var SOUMIS = {")
    bloc = vp[i:vp.index("}", i)]
    assert bloc.count(":") == 1, bloc
    assert "memoire" in bloc


def test_la_page_de_confidentialite_est_servie_et_traduite():
    """Une politique française servie sous une interface anglaise est le seul
    texte de ce site qu'un lecteur DOIT pouvoir lire dans sa langue : c'est
    celui par lequel il exerce ses droits."""
    r = client().get("/confidentialite")
    assert r.status_code == 200
    page = r.get_data(as_text=True)
    lg = _lire("langue.js")
    cles = set(re.findall(r'data-i18n="([^"]+)"', page))
    assert len(cles) > 40, len(cles)
    manquantes = sorted(c for c in cles if '"%s":' % c not in lg)
    assert not manquantes, "sans traduction : %s" % manquantes


def test_toute_page_du_site_mene_a_l_inventaire():
    """Une politique de confidentialité qu'on ne trouve qu'au pied de
    l'accueil n'est pas consultée. Elle est dans la barre latérale, donc sur
    les cinq pages."""
    b = _lire("barre.js")
    assert '<a href="/confidentialite">' in b
    for nom in PAGES:
        assert "data-barre" in _lire(nom), nom
