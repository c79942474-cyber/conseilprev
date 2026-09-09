"""La rubrique Investisseurs : ce qu'elle publie, et surtout ce qu'elle ne
publie pas.

LE RISQUE PROPRE À CETTE PAGE. Une rubrique « Informations financières » est la
mise en scène d'une société cotée. Conseilprev est une SARL non cotée : y porter
un chiffre d'affaires, un résultat ou une valorisation donnerait un nombre que
personne ne peut vérifier — ni daté, ni déposé, ni opposable — sur la page même
qui prétend informer un investisseur. C'est le défaut que ces règles empêchent,
et il ne lèverait aucune erreur : une page qui ment est une page qui s'affiche
normalement.

CE QUI TIENT LIEU DE CHIFFRE. L'identité au registre, et le chemin vers les
comptes déposés au greffe. Les deux articles qui règlent ce chemin ont été lus
dans leur version en vigueur, et la page les cite.

LES RÈGLES EXÉCUTENT LES ONGLETS. Chercher `montrer` dans le fichier dirait que
la fonction existe. Ce qui se mesure est quel panneau est LU quand on arrive par
l'ancre du pied de page.
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

PAGE = io.open(os.path.join(ICI, "investisseurs.html"), encoding="utf-8").read()
PIED = io.open(os.path.join(ICI, "footer-shared.html"), encoding="utf-8").read()
MENTIONS = io.open(os.path.join(ICI, "mentions-legales.html"), encoding="utf-8").read()

ONGLETS = ["relations", "financier", "gouvernance"]


def _texte(html_):
    import html as _h
    sans = re.sub(r"<(script|style)\b.*?</\1>", " ", html_, flags=re.S | re.I)
    return re.sub(r"\s+", " ", _h.unescape(re.sub(r"<[^>]+>", " ", sans)))


def _panneau(cle):
    d = PAGE.index('id="p-%s"' % cle)
    f = PAGE.index("</section>", d)
    return PAGE[d:f]


# ═══════════════════════════════════════════════════════════════════════════
#  AUCUN CHIFFRE QUE PERSONNE NE PEUT VÉRIFIER
# ═══════════════════════════════════════════════════════════════════════════

#: Les seuls nombres qu'une page d'investisseurs peut porter sans être adossée à
#: un dépôt : ceux du REGISTRE (capital, numéro RCS, adresse), les références de
#: textes, et les dates. Tout le reste est un chiffre d'exploitation.
_NOMBRES_ADMIS = {
    "8.000",          # capital social — porté au registre
    "494", "530", "157",  # numéro RCS
    "19", "75015",    # siège social
    "232", "22", "25",    # articles du code de commerce
    "2022", "2065", "2025", "2026", "2019", "1", "9", "24",  # dates et références
}


def test_la_page_ne_porte_AUCUN_montant_en_euros_hors_capital_social():
    """UN MONTANT SUR CETTE PAGE SERAIT INVÉRIFIABLE. Le capital social fait
    exception : il est porté au registre du commerce, donc opposable et
    consultable par un tiers. Tout autre montant — chiffre d'affaires,
    résultat, levée, valorisation — n'existerait que sur cette page."""
    lu = _texte(PAGE)
    montants = re.findall(r"([\d][\d  .,]*)\s*(?:€|euros?|EUR\b|k€|M€|M\$)", lu)
    hors = [m.strip() for m in montants if m.strip() not in ("8.000",)]
    assert not hors, (
        "la page porte un montant qui n'est pas le capital social : %r" % hors)


def test_aucun_vocabulaire_de_societe_cotee_n_est_employe_comme_un_fait():
    """DIRE « nos résultats trimestriels » ou « notre conseil d'administration »
    décrirait une société qui n'est pas celle-ci. La page peut NOMMER ces
    objets pour dire qu'ils n'existent pas — c'est même ce qu'elle fait — mais
    jamais les présenter comme siens."""
    lu = _texte(PAGE).lower()
    fautes = []
    for mot, pourquoi in (
        ("nos résultats", "annonce des résultats"),
        ("notre conseil d'administration", "une SARL n'en a pas"),
        ("nos actionnaires", "une SARL a des associés, pas des actionnaires"),
        ("cours de bourse", "aucun titre n'est admis aux négociations"),
        ("notre valorisation", "chiffre invérifiable"),
        ("chiffre d'affaires de", "chiffre non déposé"),
    ):
        if mot in lu:
            fautes.append((mot, pourquoi))
    assert not fautes, fautes


def test_la_page_DIT_qu_elle_n_est_pas_une_offre():
    """UNE RUBRIQUE INVESTISSEURS SANS CETTE RÉSERVE se lit comme une
    sollicitation. Elle doit dire, en toutes lettres, ce qu'elle n'est pas."""
    lu = _texte(PAGE).lower()
    assert "n'est pas une offre" in lu or "ni une offre au public" in lu, lu[:400]
    assert "sollicitation" in lu
    assert "aucun titre" in lu and "négociations" in lu


def test_ce_qui_n_est_PAS_publie_est_nomme_poste_par_poste():
    """« Nous ne publions pas tout » ne dit rien. Nommer les postes absents est
    ce qui permet à un lecteur de savoir qu'il ne les cherchera pas ici."""
    lu = _texte(_panneau("financier")).lower()
    for poste in ("chiffre d'affaires", "résultat", "trésorerie",
                  "prévisionnel", "valorisation"):
        assert poste in lu, "le poste « %s » n'est pas nommé comme absent" % poste


# ═══════════════════════════════════════════════════════════════════════════
#  L'IDENTITÉ NE DIVERGE PAS DE SA SOURCE
# ═══════════════════════════════════════════════════════════════════════════


def test_le_RCS_et_le_capital_sont_CEUX_des_mentions_legales():
    """DEUX PAGES, UN SEUL REGISTRE. Une identité recopiée diverge au premier
    changement fait d'un seul côté — et c'est la page investisseurs, la moins
    relue, qui garderait l'ancienne. La règle lit les deux et les compare."""
    def rcs(src):
        m = re.search(r"RCS[^:<]*:\s*(?:<strong>)?\s*Paris\s*([\d\s]+)", src) or \
            re.search(r"RCS\D{0,12}([\d][\d\s]{8,})", src)
        return re.sub(r"\s+", " ", m.group(1)).strip() if m else None

    def capital(src):
        # LE SÉPARATEUR EST FACULTATIF : les mentions légales écrivent
        # « Capital social : 8.000 euros » dans une liste, la page
        # investisseurs pose le libellé en <dt> et la valeur en <dd> — une fois
        # les balises retirées, il n'y a plus de deux-points. Un extracteur qui
        # l'exigeait rendait None sur une page pourtant juste, et la règle
        # échouait pour une raison sans rapport avec ce qu'elle mesure.
        m = re.search(r"[Cc]apital social\s*:?\s*([\d.,\s]*\d\s*euros)", src)
        return re.sub(r"\s+", " ", m.group(1)).strip() if m else None

    r_page, r_ml = rcs(_texte(PAGE)), rcs(_texte(MENTIONS))
    c_page, c_ml = capital(_texte(PAGE)), capital(_texte(MENTIONS))
    assert r_ml and c_ml, "les mentions légales ne portent plus l'identité (%r, %r)" % (r_ml, c_ml)
    assert r_page == r_ml, "RCS divergent : page %r, mentions légales %r" % (r_page, r_ml)
    assert c_page == c_ml, "capital divergent : page %r, mentions légales %r" % (c_page, c_ml)


def test_la_page_renvoie_aux_mentions_legales_comme_a_SA_SOURCE():
    """Afficher l'identité sans dire d'où elle vient ferait de cette page une
    seconde source, et deux sources se contredisent tôt ou tard."""
    fin = _panneau("financier")
    assert '/mentions-legales' in fin
    assert "font foi" in _texte(fin) or "source" in _texte(fin).lower()


def test_les_deux_articles_LUS_sont_cites_avec_leur_version():
    """UNE RÉFÉRENCE SANS DATE N'EST PAS UNE LECTURE. L'article L. 232-22 est
    en vigueur dans sa rédaction du 1er janvier 2025 ; le L. 232-25 dans celle
    du 24 mai 2019. Citer l'article sans sa version laisserait croire à une
    lecture qui n'a pas eu lieu."""
    lu = _texte(_panneau("financier"))
    assert "L. 232-22" in lu and "L. 232-25" in lu
    assert "2025" in lu and "2019" in lu
    # ET LE FOND, pas seulement le numéro : ce que chaque article établit.
    assert "greffe" in lu and "registre du commerce" in lu
    assert "ne seront pas rendus publics" in lu or "pas rendus publics" in lu
    assert "financent ou investissent" in lu, (
        "la page ne dit pas que l'investisseur accède aux comptes malgré la "
        "confidentialité — c'est pourtant le seul point qui lui soit utile")


def test_la_forme_sociale_commande_ce_qui_est_annonce_absent():
    """UNE SARL N'A NI CONSEIL D'ADMINISTRATION NI DÉPÔT AUPRÈS D'UNE AUTORITÉ
    DE MARCHÉ. Le taire laisserait un lecteur les chercher ; les inventer serait
    pire."""
    lu = _texte(_panneau("gouvernance")).lower()
    assert "sarl" in lu or "responsabilité limitée" in lu
    assert "ni conseil d'administration" in lu
    assert "sec" in lu and "amf" in lu, (
        "la page ne dit pas qu'aucun dépôt n'est fait auprès d'une autorité de "
        "marché")


def test_les_documents_de_gouvernance_pointent_vers_des_routes_SERVIES():
    """UN LIEN VERS UNE PAGE QUI N'EXISTE PAS ne lève rien : il rend un 404 que
    personne ne regarde. Les adresses sont donc relues dans la table des pages
    réellement servies."""
    import app as application
    liens = set(re.findall(r'href="(/[a-z0-9\-]+)"', _panneau("gouvernance")))
    assert liens, "le panneau gouvernance ne porte plus aucun lien interne"
    manquants = sorted(l for l in liens if l not in application.PAGES)
    assert not manquants, "adresses non servies : %r" % manquants


# ═══════════════════════════════════════════════════════════════════════════
#  LE PIED DE PAGE, ET L'ONGLET QU'IL OUVRE
# ═══════════════════════════════════════════════════════════════════════════


def test_la_colonne_investisseurs_est_SOUS_ressources():
    """Le placement demandé : sous Ressources, donc à droite de la colonne
    Légal. La règle mesure l'ORDRE dans le balisage, pas la présence."""
    assert 'data-i18n="ft.inv.lbl"' in PIED
    assert PIED.index('data-i18n="ft.res.lbl"') < PIED.index('data-i18n="ft.inv.lbl"'), (
        "Investisseurs ne suit pas Ressources")
    # ET DANS LA MÊME COLONNE : entre les deux titres, aucune fermeture de
    # colonne — sinon la rubrique partirait ailleurs dans la grille.
    entre = PIED[PIED.index('data-i18n="ft.res.lbl"'):PIED.index('data-i18n="ft.inv.lbl"')]
    assert entre.count('<div class="ft-col">') == 0, (
        "une colonne s'ouvre entre Ressources et Investisseurs")


def test_les_trois_entrees_portent_TROIS_ancres_distinctes():
    """SANS ANCRE, LES TROIS ENTRÉES OUVRIRAIENT LE MÊME ONGLET et deux
    mentiraient sur leur destination."""
    d = PIED.index('data-i18n="ft.inv.lbl"')
    bloc = PIED[d:PIED.index("</ul>", d)]
    ancres = re.findall(r'href="/investisseurs#(\w+)"', bloc)
    assert ancres == ONGLETS, "ancres du pied de page : %r" % (ancres,)


def test_les_quatre_libelles_existent_dans_LES_TROIS_langues():
    """UNE CLÉ MANQUANTE NE LÈVE RIEN : le libellé retombe sur le français, et
    un lecteur allemand voit une rubrique dans une langue qu'il n'a pas
    choisie."""
    src = io.open(os.path.join(ICI, "index.page.js"), encoding="utf-8").read()
    manque = {}
    for lang in ("fr", "en", "de"):
        tete = "\n  %s:JSON.parse(`" % lang
        d = src.index(tete) + len(tete)
        table = src[d:src.index("`)", d)]
        absents = [k for k in ("ft.inv.lbl", "ft.inv.l1", "ft.inv.l2", "ft.inv.l3")
                   if '"%s"' % k not in table]
        if absents:
            manque[lang] = absents
    assert not manque, manque


# ═══════════════════════════════════════════════════════════════════════════
#  CE QUE LES ONGLETS FONT VRAIMENT
# ═══════════════════════════════════════════════════════════════════════════

_HARNAIS = r"""
const fs = require("fs");
const PAGE = fs.readFileSync(process.argv[2], "utf8");
const ANCRE = process.env.ANCRE || "";

function faire(id){
  return { id: id, hidden: false, dataset: {}, _attrs: {}, _ecoutes: {},
    setAttribute: function(k,v){ this._attrs[k] = v; },
    getAttribute: function(k){ return this._attrs[k] === undefined ? null : this._attrs[k]; },
    addEventListener: function(t,f){ (this._ecoutes[t] = this._ecoutes[t] || []).push(f); },
    focus: function(){ global.__focus = id; },
    cliquer: function(){ (this._ecoutes.click || []).forEach(function(f){ f({}); }); },
    toucher: function(k){ (this._ecoutes.keydown || []).forEach(function(f){
        f({ key: k, preventDefault: function(){} }); }); } };
}

const N = {};
["relations","financier","gouvernance"].forEach(function(o){
  N["tab-"+o] = faire("tab-"+o);
  N["tab-"+o].dataset.onglet = o;
  N["p-"+o] = faire("p-"+o);
});

global.document = {
  getElementById: function(id){ return N[id] || null; },
  querySelectorAll: function(sel){
    if(sel === ".tab") return ["relations","financier","gouvernance"].map(function(o){ return N["tab-"+o]; });
    return [];
  },
  addEventListener: function(){}
};
global.location = { hash: ANCRE ? "#" + ANCRE : "" };
global.history = { replaceState: function(a,b,h){ global.location.hash = h; } };
global.window = { addEventListener: function(){}, location: global.location };

const bloc = PAGE.slice(PAGE.lastIndexOf("<script>") + 8);
eval(bloc.slice(0, bloc.indexOf("</scr" + "ipt>")));

function etat(){
  const r = { visibles: [], selectionnes: [], hash: global.location.hash, focus: global.__focus || null };
  ["relations","financier","gouvernance"].forEach(function(o){
    if(!N["p-"+o].hidden) r.visibles.push(o);
    if(N["tab-"+o].getAttribute("aria-selected") === "true") r.selectionnes.push(o);
  });
  return r;
}

const rapport = { arrivee: etat() };
N["tab-gouvernance"].cliquer();
rapport.apres_clic = etat();
N["tab-gouvernance"].toucher("ArrowRight");
rapport.apres_fleche = etat();
process.stdout.write(JSON.stringify(rapport));
"""


def _jouer(ancre=""):
    node = shutil.which("node")
    if not node:
        pytest.skip("node absent : les onglets ne peuvent pas être exécutés")
    with tempfile.TemporaryDirectory() as d:
        h = os.path.join(d, "h.js")
        io.open(h, "w", encoding="utf-8").write(_HARNAIS)
        env = dict(os.environ, ANCRE=ancre)
        p = subprocess.run([node, h, os.path.join(ICI, "investisseurs.html")],
                           capture_output=True, text=True, timeout=60, env=env)
    if p.returncode != 0:
        pytest.fail("le script des onglets ne tourne pas :\n%s" % (p.stderr or "")[-1200:])
    return json.loads(p.stdout)


@pytest.mark.parametrize("ancre", ONGLETS)
def test_L_ANCRE_DU_PIED_DE_PAGE_ouvre_SON_onglet(ancre):
    """LE POINT QUI FAIT TOUT LE RESTE. Trois entrées distinctes au pied de
    page qui ouvriraient le même onglet : deux d'entre elles annonceraient une
    destination qu'elles ne servent pas, et rien ne le signalerait."""
    r = _jouer(ancre)["arrivee"]
    assert r["visibles"] == [ancre], r
    assert r["selectionnes"] == [ancre], r


def test_UN_SEUL_panneau_est_lisible_a_la_fois():
    """Deux panneaux ouverts feraient lire la réserve d'une rubrique sous le
    titre d'une autre."""
    for ancre in ONGLETS + ["", "inconnu"]:
        r = _jouer(ancre)["arrivee"]
        assert len(r["visibles"]) == 1, (ancre, r)
        assert len(r["selectionnes"]) == 1, (ancre, r)


def test_une_ancre_inconnue_retombe_sur_le_PREMIER_onglet():
    """Un lien vieilli ne doit pas rendre une page vide : trois panneaux
    cachés et aucun titre actif."""
    assert _jouer("inconnu")["arrivee"]["visibles"] == ["relations"]
    assert _jouer("")["arrivee"]["visibles"] == ["relations"]


def test_le_panneau_se_cache_avec_hidden_et_non_par_une_classe():
    """`display:none` posé par une classe laisse l'élément dans l'arbre
    d'accessibilité : un lecteur d'écran annonce trois rubriques là où une
    seule est lisible. `hidden` retire les deux à la fois."""
    r = _jouer("financier")
    assert r["arrivee"]["visibles"] == ["financier"]
    assert "hidden" in PAGE[PAGE.index('id="p-financier"'):PAGE.index('id="p-financier"') + 220]
    assert ".panneau[hidden]{display:none}" in PAGE.replace(" ", "")


def test_le_clic_change_d_onglet_ET_l_adresse():
    """Sans l'adresse, un lien copié depuis la page rouvrirait le premier
    onglet — et le lecteur croirait s'être trompé de lien."""
    r = _jouer("relations")
    assert r["apres_clic"]["visibles"] == ["gouvernance"], r["apres_clic"]
    assert r["apres_clic"]["hash"] == "#gouvernance", r["apres_clic"]


def test_les_fleches_parcourent_la_rangee_et_emportent_le_focus():
    """Motif ARIA des onglets : sans les flèches, il faut tabuler à travers
    chaque bouton. Le focus DOIT suivre, sinon la flèche change l'affichage
    sans déplacer le lecteur — qui ne sait plus où il est."""
    r = _jouer("relations")["apres_fleche"]
    assert r["visibles"] == ["relations"], (
        "ArrowRight depuis le dernier onglet ne revient pas au premier : %r" % r)
    assert r["focus"] == "tab-relations", (
        "le focus n'a pas suivi la flèche : %r" % r["focus"])
