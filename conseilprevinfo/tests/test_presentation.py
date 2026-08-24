"""LA MISE EN PAGE — ce qu'elle a le droit de dire, et ce qu'elle ajouterait.

UNE MISE EN PAGE PEUT MENTIR AUSSI SÛREMENT QU'UN TEXTE. Donner à une fiche
plus de place, c'est affirmer qu'elle compte davantage ; le faire sur un
critère que le moteur ne porte pas reviendrait à noter l'information — ce que
ce site refuse partout ailleurs.

D'OÙ LA RÈGLE : la présentation REND LISIBLE l'ordre du moteur, elle n'en
invente aucun. La tête de première page est la première fiche du tri déjà
publié — « le plus important d'abord, puis le plus récent ». Le jour où ce tri
change, la tête change avec lui, sans qu'une ligne de mise en page soit
touchée.

ET ELLE NE DOIT PAS DEVENIR UN OBSTACLE. Une barre d'outils qui prend
quarante-quatre pour cent d'un écran de téléphone a cessé d'être un outil.
"""
import os
import re
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)


def _lire(nom):
    return open(os.path.join(ICI, nom), encoding="utf-8").read()


# ── 1. La tête de une n'ajoute aucun jugement ─────────────────────────────

def test_la_tete_est_la_premiere_du_tri_publie():
    """Elle n'est pas choisie : elle est la première de la liste que le moteur
    a déjà classée. Un critère de mise en page — « la plus longue », « celle
    qui a une image » — ferait de la page une seconde autorité en face du
    moteur."""
    js = _lire("veille.js")
    i = js.index('$("une").innerHTML')
    bloc = js[i:i + 400]
    assert 'i === 0 ? "tete"' in bloc, bloc[:200]
    # aucune autre condition ne décide de la tête
    for interdit in ("length >", "sort(", "Math.max", "score"):
        assert interdit not in bloc, interdit


def test_la_une_ne_retient_que_ce_qui_rompt():
    """La composition ne change pas ce qui y entre : la une reste la seule
    portée « rupture », et ne se remplit pas des fiches suivantes."""
    js = _lire("veille.js")
    assert 'f.impact === "rupture"' in js
    i = js.index('var une = toutes.filter')
    assert "slice(" not in js[i:i + 200], "la une est coupée à un nombre arbitraire"


def test_le_tri_du_moteur_est_bien_celui_qu_on_rend_lisible():
    """Le commentaire de `filtrer()` annonce « le plus important d'abord, puis
    le plus récent ». Si ce tri disparaissait, la tête cesserait de vouloir
    dire quelque chose — et rien à l'écran ne le signalerait."""
    py = _lire("veille.py")
    i = py.index("def filtrer(")
    bloc = py[i:i + 2600]
    assert "out.sort(" in bloc
    assert 'IMPACTS.get(f.get("impact"), {}).get("rang"' in bloc


# ── 2. La barre recopie, elle ne recalcule pas ────────────────────────────

def test_l_etat_de_la_barre_vient_du_meme_calcul_que_le_bandeau():
    """Un second calcul, même juste, finirait par afficher un autre nombre que
    celui d'à côté. La barre est remplie DANS `rendreEtat`, à partir des mêmes
    variables — elle ne refait aucune addition."""
    js = _lire("veille.js")
    i = js.index("function rendreEtat")
    fin = js.index("\n  /* LE NUMÉRO DE DEMANDE", i)
    bloc = js[i:fin]
    assert '$("bl-etat")' in bloc, "la barre est remplie ailleurs que dans rendreEtat"
    assert "et.fiches" in bloc and "mauvaises.length" in bloc


def test_la_barre_ne_sait_pas_compter_des_fiches():
    """Elle réserve la place, le moteur écrit dedans.

    LA RÈGLE A ÉTÉ RESSERRÉE, PAS ASSOUPLIE. Elle disait « aucun `/api/` dans
    `barre.js` » — une formulation commode tant que la barre ne servait qu'à
    naviguer. La légende, elle, doit lire le RÉFÉRENTIEL : les noms des portées
    et des statuts appartiennent au moteur, et les recopier ici les ferait
    diverger au premier ajout. Ce que la règle protégeait vraiment, c'est que
    la barre ne devienne pas une seconde autorité sur LE CORPUS — qu'elle ne
    compte pas, ne filtre pas, ne classe pas. C'est cela qui est vérifié
    maintenant, et c'est plus étroit que « pas d'API » : le vocabulaire est
    permis, les fiches ne le sont pas.
    """
    b = _lire("barre.js")
    assert 'id="bl-etat"' in b
    # Le seul point d'appel autorisé, et il est nommé.
    appels = re.findall(r'fetch\("([^"]+)"', b)
    assert appels == ["/api/veille/referentiel"], appels
    # Aucune route de corpus, sous aucune forme.
    for interdit in ("/api/veille?", "/api/veille/fiche", "/api/veille/facettes",
                     "/api/veille/dossiers", "/api/veille/pistes", "/api/sources",
                     "/api/classeur", "/api/abonnes"):
        assert interdit not in b, interdit
    # Et les comptes restent RECOPIÉS de la rubrique, jamais recalculés :
    # `data-de` désigne l'élément source, l'observateur en suit les changements.
    assert "data-de" in b and "MutationObserver" in b
    assert "cible.textContent = v" in b


# ── 3. Le repli des filtres ───────────────────────────────────────────────

def test_le_compte_de_filtres_actifs_vient_de_la_table_unique():
    """Un compte tenu à part finirait par annoncer « 2 actifs » sur une page
    qui n'en applique qu'un. Il se calcule sur `FILTRES`, la même table qui
    sert à interroger le serveur et à écrire l'adresse."""
    js = _lire("veille.js")
    i = js.index("function compterActifs")
    bloc = js[i:i + 400]
    assert "FILTRES.filter(" in bloc, bloc[:200]


def test_le_repli_ne_vaut_que_sur_petit_ecran():
    """Au-dessus de 900 px la barre tient sur deux lignes : la replier serait
    une gêne pour rien, et cacher des filtres qu'on voyait est une perte."""
    css = _lire("veille.css")
    assert ".f-plier{display:none}" in css.replace(" ", "")
    i = css.index("@media (max-width:899px)")
    bloc = css[i:i + 1400]
    assert ".f-plier{" in bloc.replace(" ", "").replace("\n", "")
    assert ".filtres .in{display:none}" in bloc


def test_le_bouton_de_repli_declare_ce_qu_il_commande():
    """`aria-expanded` et `aria-controls` ne sont pas décoratifs : sans eux,
    un lecteur d'écran annonce un bouton sans dire s'il ouvre ou ferme, ni
    quoi."""
    h = _lire("index.html")
    i = h.index('id="f-plier"')
    bloc = h[i - 200:i + 300]
    assert 'aria-expanded="false"' in bloc
    assert 'aria-controls="f-champs"' in bloc
    js = _lire("veille.js")
    assert 'plier.setAttribute("aria-expanded"' in js


def test_la_mesure_qui_a_motive_le_repli_est_ecrite():
    """« 44 % de l'écran » n'est pas une impression : c'est une mesure prise au
    navigateur, et elle est écrite là où quelqu'un serait tenté de défaire le
    repli en le trouvant inutile."""
    css = _lire("veille.css")
    assert "373 px" in css and "QUARANTE-QUATRE POUR" in css


# ── 4. La barre latérale : ce qui la garde complète et honnête ────────────

def _rubriques_declarees():
    """Tous les identifiants de rubrique servis par le site — ceux du HTML et
    ceux qu'écrit le JavaScript. Les lire des deux endroits est le point : une
    rubrique posée par du script est aussi visible qu'une autre, et c'est
    justement celle qu'on oublie.

    LE PÉRIMÈTRE EST ÉNUMÉRÉ PAR LE DOSSIER, pas tenu à la main. Il l'était :
    quatre fichiers nommés ici, et `revue.html` n'en faisait pas partie — sa
    rubrique aurait pu vivre sans silhouette sans qu'aucun contrôle ne bouge,
    tandis que l'icône écrite pour elle passait pour orpheline. Un inventaire
    dont le périmètre est lui-même tenu à la main a exactement le défaut qu'il
    est censé empêcher ; c'est la leçon déjà payée sur `fleches.js` dans
    `test_securite`, et elle vaut ici."""
    ids = set()
    for nom in sorted(f for f in os.listdir(ICI)
                      if f.endswith(".html") or f.endswith(".js")):
        for m in re.finditer(r'h2 class="rubrique" id="([a-z0-9-]+)"', _lire(nom)):
            ids.add(m.group(1))
    return ids


def test_chaque_rubrique_servie_a_sa_silhouette():
    """L'icône est une commodité — une entrée sans icône reste lisible. Mais
    elle ne doit pas manquer PAR OUBLI : une barre où trois entrées sur onze
    portent un pictogramme se lit comme une barre à moitié chargée. Ce contrôle
    tombe le jour où quelqu'un ajoute une rubrique sans sa silhouette."""
    b = _lire("barre.js")
    ids = _rubriques_declarees()
    assert len(ids) >= 11, ids
    manquantes = [i for i in sorted(ids) if ('"%s":' % i) not in b]
    assert not manquantes, "rubriques sans silhouette : %s" % manquantes


def test_aucune_silhouette_orpheline():
    """L'inverse compte autant : une icône pour une rubrique retirée reste dans
    le fichier des années, et personne ne sait plus si elle sert."""
    b = _lire("barre.js")
    i = b.index("var ICONES = {")
    bloc = b[i:b.index("\n  };", i)]
    declares = set(re.findall(r'"(r-[a-z0-9-]+)":', bloc))
    orphelines = sorted(declares - _rubriques_declarees())
    assert not orphelines, "silhouettes sans rubrique : %s" % orphelines


def test_la_silhouette_n_est_jamais_seule_a_porter_l_information():
    """WCAG 1.4.1. L'intitulé est écrit à côté de l'icône, et l'icône est
    retirée de l'arbre d'accessibilité — annoncée, elle ferait dire deux fois
    la même chose à un lecteur d'écran."""
    b = _lire("barre.js")
    i = b.index("function icone(")
    bloc = b[i:i + 600]
    assert 'aria-hidden="true"' in bloc and 'focusable="false"' in bloc
    assert "currentColor" in bloc, "l'icône impose sa couleur au lieu de suivre l'état"


def test_la_legende_reprend_les_classes_des_cartes():
    """Une légende peinte à la main dérive à la première retouche de feuille de
    style : le témoin dirait une couleur, la carte en montrerait une autre. Ici
    le témoin EST l'élément — `.past` avec la clé du référentiel."""
    b = _lire("barre.js")
    i = b.index("function legende(")
    bloc = b[i:b.index("\n  function rendre(", i)]
    serre = re.sub(r"\s+", " ", bloc.replace('"', "'"))
    assert "class='past ' + esc(im.cle)" in serre, serre[:400]
    assert "fsource" in bloc and "class=\"st" in bloc
    # et les noms viennent du serveur, jamais du fichier
    assert "nom(im)" in bloc and "nom(s)" in bloc


def test_la_legende_ne_montre_que_les_statuts_qui_sortent():
    """« À vérifier », « rédigée par IA », « réfutée » ne sont jamais servis.
    Les mettre en légende apprendrait au lecteur qu'il peut les rencontrer."""
    b = _lire("barre.js")
    i = b.index("function legende(")
    bloc = b[i:b.index("\n  function rendre(", i)]
    assert "s.publiable" in bloc, "la légende annonce des statuts non publiables"


def test_une_legende_sans_referentiel_dit_pourquoi():
    """Un axe qui ne donne rien le dit — la règle vaut ici comme ailleurs. Une
    légende écrite en dur survivrait à la panne en affirmant des couleurs que
    le moteur n'emploie peut-être plus."""
    b = _lire("barre.js")
    assert 'if (!_ref) {' in b
    assert 'bl.leg.non' in b
    lg = _lire("langue.js")
    assert '"bl.leg.non"' in lg


def test_la_barre_se_replie_a_toute_largeur_et_s_en_souvient():
    """Elle ne se repliait que sous 1100 px : au-dessus, la colonne était
    imposée, et un lecteur qui veut la pleine largeur pour le registre des
    sources n'avait aucun moyen de l'obtenir."""
    css = _lire("veille.css")
    serre = css.replace(" ", "").replace("\n", "")
    assert "html.bl-repliee.bl{display:none}" in serre, "la barre repliée reste en place"
    assert "html.bl-repliee.page{display:block" in serre
    # Le bouton n'est plus caché sur grand écran.
    assert "@media(min-width:1100px){#bl-bouton{display:none}}" not in serre
    b = _lire("barre.js")
    assert 'CLE_ETAT = "cpinfo.barre"' in b
    assert "localStorage.setItem(CLE_ETAT" in b


def test_une_barre_repliee_sort_du_parcours_clavier():
    """Masquée par la grille ou déplacée par `transform`, elle reste dans
    l'ordre de tabulation : un lecteur au clavier traverse une dizaine de liens
    hors écran avant d'atteindre la page."""
    b = _lire("barre.js")
    i = b.index("function ouvrir(")
    bloc = b[i:i + 900]
    assert 'setAttribute("inert"' in bloc and 'aria-hidden' in bloc
    assert 'removeAttribute("inert")' in bloc


def test_la_barre_suit_une_page_rendue_apres_elle():
    """Les rubriques d'une fiche sont écrites par `fiche.js` une fois la
    réponse revenue, donc APRÈS la construction de la barre. Une convocation
    explicite depuis `fiche.js` marcherait aujourd'hui et tomberait à la
    troisième page à rendu différé ; l'observation ne peut pas être oubliée."""
    b = _lire("barre.js")
    assert "function suivrePage(" in b
    # DÉFAUT DU PREMIER CONTRÔLE, trouvé en mutant le code : il vérifiait que
    # la fonction EXISTE, pas qu'elle est APPELÉE. Retirer l'appel dans
    # `demarrer()` laissait passer — et la barre cessait de suivre la page sans
    # qu'aucun contrôle ne bouge.
    d = b[b.index("function demarrer("):]
    assert "suivrePage();" in d[:d.index("\n  }")], "l'observation n'est pas mise en route"
    i = b.index("function suivrePage(")
    bloc = b[i:i + 1400]
    assert 'querySelector("main")' in bloc
    assert "childList: true, subtree: true" in bloc
    # et elle ne reconstruit QUE si la liste des rubriques a changé
    assert "if (s === _signature) return;" in bloc
    f = _lire("fiche.js")
    assert 'id="r-croisement"' in f and 'id="r-voisinage"' in f


def test_la_glose_coupee_de_la_barre_est_rendue_en_infobulle():
    """La barre coupe « Le fil — tout le corpus filtré » à « Le fil » : la
    glose repousserait le compteur hors du cadre. Couper sans rien offrir en
    échange, c'est retirer la seule phrase qui dit ce que la rubrique
    contient."""
    b = _lire("barre.js")
    assert "glose: i > 0 ? titre : \"\"" in b
    assert 's.glose ? \' title="\'' in b


def test_les_blocs_de_la_barre_ne_sont_poses_que_la_ou_ils_sont_remplis():
    """DÉFAUT CONSTATÉ AU NAVIGATEUR. Sur la page de confidentialité, où aucun
    moteur ne tourne, la barre affichait « LE CORPUS » suivi de deux cadres
    vides : un titre qui promet un état et ne le donne jamais. Deux causes,
    corrigées ensemble — le bloc était posé partout, et `hidden` ne le cachait
    pas puisque `display:flex` écrase la feuille du navigateur."""
    b = _lire("barre.js")
    assert 'hote.hasAttribute("data-barre-etat")' in b
    css = _lire("veille.css").replace(" ", "").replace("\n", "")
    assert ".bl-etat[hidden],.bl-lu[hidden]{display:none}" in css
    # Seule la page qui le remplit le demande.
    assert "data-barre-etat" in _lire("index.html")
    for nom in ("confidentialite.html", "abonnement.html", "confronter.html",
                "fiche.html"):
        assert "data-barre-etat" not in _lire(nom), nom
    # Et c'est bien `veille.js`, servi par cette page-là seule, qui l'écrit.
    assert '$("bl-etat")' in _lire("veille.js")


# ── 5. La manchette, les intertitres, l'article ───────────────────────────

def test_la_manchette_est_remplie_par_le_meme_calcul_que_le_reste():
    """Trois endroits affichent le compte de fiches — la manchette, le bandeau
    et la barre. Ils ne valent que s'ils ne peuvent pas diverger, et la seule
    façon de s'en assurer est qu'UN SEUL calcul les remplisse tous les trois."""
    js = _lire("veille.js")
    i = js.index("function rendreEtat")
    fin = js.index("\n  /* LE NUMÉRO DE DEMANDE", i)
    bloc = js[i:fin]
    for cible in ('$("mn-fiches")', '$("mn-date")', '$("mn-rupt")',
                  '$("mn-src")', '$("bl-etat")', '$("etat")'):
        assert cible in bloc, "%s est rempli hors de rendreEtat" % cible
    # Un seul appel, et il vient APRÈS la séparation une / fil : la manchette
    # porte le nombre de ruptures, qui est la longueur de la une.
    assert js.count("rendreEtat(") == 2, "rendreEtat est appelé plusieurs fois"
    assert "rendreEtat(d, une.length);" in js
    assert js.index("var une = toutes.filter") < js.index("rendreEtat(d, une.length)")


def test_le_bandeau_ne_reste_que_pour_ce_qui_ne_va_pas():
    """Un bandeau d'alerte qui s'affiche aussi quand il n'y a pas d'alerte
    n'alerte plus. Il annonçait « toutes les sources ont répondu » sur soixante
    pixels, à chaque visite."""
    js = _lire("veille.js")
    i = js.index("function rendreEtat")
    bloc = js[i:i + 2600]
    assert "if (!mauvaises.length) {" in bloc
    j = bloc.index("if (!mauvaises.length) {")
    assert "e.hidden = true;" in bloc[j:j + 200], bloc[j:j + 200]
    # Mais il nomme toujours les sources muettes — ce que la manchette ne peut
    # pas faire en une ligne, et c'est ce pour quoi il servait vraiment.
    assert "j.message || j.erreur" in bloc


def test_les_intertitres_lisent_l_ordre_et_ne_le_refont_pas():
    """La mise en page rend lisible l'ordre du moteur, elle n'en invente aucun.
    Un intertitre est posé LÀ OÙ LA PORTÉE CHANGE, en lisant la liste dans
    l'ordre où elle arrive — et si le tri cessait de grouper les portées, ils
    se répéteraient, ce qui est exactement ce qu'il faudrait voir."""
    js = _lire("veille.js")
    i = js.index("function composerFil(")
    bloc = js[i:js.index("\n  function charger()", i)]
    assert "f.impact !== prec" in bloc, bloc[:300]
    for interdit in ("sort(", "reverse(", "IMPACTS", "rang"):
        assert interdit not in bloc, "la composition du fil réordonne : %s" % interdit
    # Le libellé vient du référentiel servi avec la fiche, jamais d'ici.
    assert 'nommer("impact", f.impact, f.impact_nom)' in bloc


def test_l_intertitre_traverse_la_grille():
    """Posé dans une case, il occuperait la largeur d'une carte et se lirait
    comme une carte vide."""
    css = _lire("veille.css").replace(" ", "").replace("\n", "")
    i = css.index(".intertitre{")
    assert "grid-column:1/-1" in css[i:i + 260], css[i:i + 260]


def test_la_fiche_est_bornee_a_une_mesure_lisible():
    """Mesuré au navigateur : sur la colonne de 1 240 px, un paragraphe de
    lecture critique faisait cent quatre-vingts signes par ligne — près du
    triple de ce qui se lit sans perdre la ligne suivante."""
    f = _lire("fiche.js")
    assert '<article class="art">' in f
    assert "h += '</article>';" in f
    # Le croisement et le voisinage restent HORS de l'article : ce sont des
    # grilles de vignettes, pas du texte suivi.
    i = f.index("h += '</article>';")
    assert f.index('id="r-croisement"') > i
    assert f.index('id="r-voisinage"') > i
    css = _lire("veille.css").replace(" ", "").replace("\n", "")
    assert ".art{max-width:68ch" in css
    assert "CENTQUATRE-VINGTS" in _lire("veille.css").replace(" ", "")


def test_la_barre_n_annonce_pas_une_rubrique_masquee():
    """DÉFAUT CONSTATÉ AU NAVIGATEUR, sur la page d'abonnement. Elle porte deux
    panneaux exclusifs — « hors compte » et « dans le compte » — dont un seul
    est affiché, l'autre étant `hidden`. La barre lisait les rubriques des DEUX
    et en annonçait quatre quand une seule était à l'écran : trois entrées qui
    menaient à du vide.

    C'est le défaut même que la lecture dans la page devait rendre impossible.
    Lire un élément masqué le reproduit par un autre chemin : il ne suffit pas
    qu'une rubrique EXISTE, il faut qu'elle SOIT RENDUE."""
    b = _lire("barre.js")
    assert "function rendue(h)" in b
    assert "h.getClientRects().length > 0" in b
    i = b.index("function sections()")
    assert ".filter(rendue)" in b[i:i + 260], b[i:i + 260]
    # Les flèches lisent la même chose, et doivent l'ignorer de même : un
    # titre masqué a un rectangle de hauteur nulle en haut de page, donc
    # « déjà dépassé », donc la flèche « rubrique suivante » se croit arrivée.
    f = _lire("fleches.js")
    i = f.index("function rubriques()")
    assert "getClientRects().length > 0" in f[i:i + 500]
    # Et la page d'abonnement porte bien les deux panneaux exclusifs qui ont
    # révélé le défaut : si elle cessait, ce contrôle garderait une règle sans
    # objet, et il faudrait le savoir.
    h = _lire("abonnement.html")
    assert '<section id="hors" hidden>' in h and '<section id="dedans" hidden>' in h


def test_la_barre_suit_un_panneau_qu_on_revele():
    """Retirer `hidden` ne change aucun nœud : sans surveillance des attributs,
    la barre resterait sur les rubriques d'avant la connexion, et resterait
    fausse jusqu'au prochain rechargement."""
    for nom in ("barre.js", "fleches.js"):
        s = _lire(nom)
        assert 'attributeFilter: ["hidden", "class"]' in s, nom
