# -*- coding: utf-8 -*-
"""CE QU'UN `title` DISAIT, LU PAR TOUS — les compléments dans les pages (lot 3).

LE DÉFAUT MESURÉ (recette_complements.js, colonne « avant », commit 32fb668).
/bulle-titre.js montre un `title` au doigt et au clavier — sur ce qui prend
le focus ou se touche. Il ne peut rien pour ce que la page elle-même cache :
  · 151 éléments INERTES à `title` informatif dans Sentinel (pastilles P1,
    blocs de score, « propre à l'IA », « — »…) : jamais lus au clavier, et
    un `tabindex` aurait fait de leur `title` leur NOM (mesuré : « 72 % »
    disparaissait de ce qu'entend un lecteur d'écran) ;
  · des boutons nommés « × », « ‹ », « ← » — et le « × » d'une fenêtre
    ouvrait une bulle « Fermer cette fenêtre » à chaque tabulation ;
  · neuf champs sans autre nom que leur `title` ;
  · dix éléments de l'accueil à DEUX bulles à la souris (la native et
    data-tooltip) ;
  · des « × » de suppression en <div> : ni focus, ni nom ;
  · « Terminer ✓ » ne disait qu'à la souris posée que rien n'est déclaré
    conforme.

CES RÈGLES EXÉCUTENT LE CODE QUAND ELLES LE PEUVENT : les écrans de
conformité sont peints par leurs vrais moteurs, avec les vrais référentiels
servis par l'application (harnais de tests/test_memoire_ecrans.py) ; le
bandeau des parcours par le vrai moteur d'avancement (harnais de
tests/test_parcours_avancement.py) ; les flèches de navigation, les
indicateurs de gouvernance, le bouton d'aide, les confirmations par leurs
vraies fonctions, sous node. Le reste est lu dans le HTML comme un navigateur
le lirait : balises, attributs, texte visible — jamais dans un commentaire.
"""
import html as _html
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
from html.parser import HTMLParser

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE = shutil.which("node")


def _lire(nom):
    return io.open(os.path.join(_RACINE, nom), encoding="utf-8").read()


SENTINEL = _lire("sentinel.html")
PAGE_JS = _lire("sentinel.page.js")
ACCUEIL = _lire("index.html")
ACCUEIL_JS = _lire("index.page.js")
BULLE = _lire("bulle-titre.js")


def _charger(nom):
    """Un harnais voisin, chargé À PART : ses règles ne sont pas recueillies
    une seconde fois, son cache n'est pas partagé."""
    spec = importlib.util.spec_from_file_location(
        "_harnais_" + nom, os.path.join(_RACINE, "tests", nom + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ══════════════════════════════════════════════════════════════════════════
#  LE HTML LU COMME UN NAVIGATEUR : un arbre, des attributs, du texte
# ══════════════════════════════════════════════════════════════════════════

_VIDES = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
          "meta", "param", "source", "track", "wbr"}


class _Noeud(object):
    def __init__(self, tag, attrs, parent, ligne):
        self.tag, self.attrs, self.parent, self.ligne = tag, attrs, parent, ligne
        self.enfants = []

    def texte(self):
        return "".join(e if isinstance(e, str) else e.texte() for e in self.enfants)

    def cache(self):
        st = (self.attrs.get("style") or "").replace(" ", "").lower()
        return "hidden" in self.attrs or "display:none" in st or "visibility:hidden" in st

    def visible(self):
        """Le texte qu'un navigateur AFFICHE : sans ce qui est `hidden` ou
        masqué par son style — un texte caché n'avertit personne."""
        if self.cache():
            return ""
        return "".join(e if isinstance(e, str) else e.visible() for e in self.enfants)

    def ancetres(self):
        p = self.parent
        while p is not None:
            yield p
            p = p.parent

    def classes(self):
        return (self.attrs.get("class") or "").split()


class _Arbre(HTMLParser):
    def __init__(self, src):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.racine = _Noeud("#", {}, None, 0)
        self.courant = self.racine
        self.tous = []
        self.feed(src)

    def handle_starttag(self, tag, attrs):
        n = _Noeud(tag, dict((k, v if v is not None else "") for k, v in attrs),
                   self.courant, self.getpos()[0])
        self.courant.enfants.append(n)
        self.tous.append(n)
        if tag not in _VIDES:
            self.courant = n

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in _VIDES:
            self.courant = self.courant.parent

    def handle_endtag(self, tag):
        n = self.courant
        while n is not None and n.tag != tag:
            n = n.parent
        if n is not None and n.parent is not None:
            self.courant = n.parent

    def handle_data(self, d):
        self.courant.enfants.append(d)

    def par_id(self, i):
        for n in self.tous:
            if n.attrs.get("id") == i:
                return n
        return None


_ARBRES = {}


def _arbre(nom):
    if nom not in _ARBRES:
        _ARBRES[nom] = _Arbre({"sentinel.html": SENTINEL, "index.html": ACCUEIL}[nom])
    return _ARBRES[nom]


def _norm(s):
    """La normalisation de /bulle-titre.js (§2.2) : un `title` égal au nom, à
    la ponctuation finale et aux guillemets près, n'apprend rien."""
    s = re.sub(r'["«»“”„]', "", str(s or "").lower())
    s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r"[\s.:;!?…]+$", "", s)


def _js_regex(nom):
    """Une expression régulière de /bulle-titre.js, telle qu'il l'exécute."""
    m = re.search(r"var " + nom + r" = /(.+?)/([a-z]*);", BULLE)
    assert m, "%s introuvable dans bulle-titre.js" % nom
    return re.compile(m.group(1), re.I if "i" in m.group(2) else 0)


RACCOURCI = _js_regex("RACCOURCI")


def _apprend_quelque_chose(title, nom):
    """Le critère « title informatif » de /bulle-titre.js (§2.2)."""
    ti, n = _norm(title), _norm(nom)
    if len(ti) < 2 or ti == n:
        return False
    if n and ti.startswith(n) and RACCOURCI.match(ti[len(n):]):
        return False
    return True


def _node(harnais, *args):
    if not NODE:
        pytest.skip("node absent : le code ne peut pas être exécuté")
    with tempfile.TemporaryDirectory() as d:
        h = os.path.join(d, "h.js")
        io.open(h, "w", encoding="utf-8").write(harnais)
        r = subprocess.run([NODE, h] + list(args), capture_output=True, text=True, timeout=90)
    if r.returncode != 0:
        pytest.fail("le scénario n'a pas tourné :\n%s" % (r.stderr or "")[-1800:])
    return json.loads(r.stdout)


def _tranche(debut, fin=None, src=PAGE_JS):
    """Une fonction du VRAI fichier, de sa déclaration à sa fin."""
    i = src.find(debut)
    assert i >= 0, "%r est introuvable" % debut
    j = src.find(fin, i) if fin else src.find("\n};", i) + 3
    assert j > i, "fin de %r introuvable" % debut
    return src[i:j]


# ══════════════════════════════════════════════════════════════════════════
#  1. LES PASTILLES RÉPÉTÉES ONT UNE LÉGENDE VISIBLE DANS LEUR ÉCRAN (§3.1 a)
# ══════════════════════════════════════════════════════════════════════════

_memoire = None


def _ecrans_de_conformite():
    """Les cinq écrans peints par leurs VRAIS moteurs, avec les vrais
    référentiels — et, pour les déclarations d'applicabilité, la vraie
    réponse du serveur à des décisions données."""
    global _memoire
    if _memoire is None:
        _memoire = _charger("test_memoire_ecrans")
    refs = _memoire._refs()
    import app as application
    a = application.app
    lien = a.url_map.bind("localhost")
    for cle, url, corps in (
            # Une mesure RETENUE SANS JUSTIFICATION : la pastille
            # « justification manquante » n'apparaît qu'ainsi.
            ("soa42", "/api/iso42001/applicabilite", {"mesures": {"A.2.2": {"decision": "retenue"}}}),
            ("soa27", "/api/iso27001/applicabilite", {"mesures": {}})):
        if cle in refs:
            continue
        ep, args = lien.match(url, method="POST")
        with a.test_request_context(url, method="POST", json=corps):
            r = a.view_functions[ep](**args)
            r = r[0] if isinstance(r, tuple) else r
            refs[cle] = r.get_json()
    return _executer_memoire("""
      ISO_REF = REFS.iso42001; window.isoPeindreArticles();
      out.isoArticles = document.getElementById('iso-art-body').innerHTML;
      var e1 = document.getElementById('iso-soa-body'); isoRendreSoa(e1, REFS.soa42);
      out.isoSoa = e1.innerHTML;
      ISO27_REF = REFS.iso27001; window.iso27PeindreArticles();
      out.iso27Articles = document.getElementById('iso27-art-body').innerHTML;
      var e2 = document.getElementById('iso27-soa-body'); iso27RendreSoa(e2, REFS.soa27);
      out.iso27Soa = e2.innerHTML;
      NIS2_REF = REFS.nis2; window.nis2PeindreGouvernance();
      out.nis2Gouv = document.getElementById('nis2-gouv-body').innerHTML;
    """)


def _executer_memoire(scenario):
    """Le socle du harnais de la mémoire des écrans (la VRAIE tranche de
    sentinel.page.js, les vrais référentiels), avec une sortie écrite dans un
    FICHIER : les écrans peints pèsent des dizaines de kilo-octets, et un
    `process.exit` qui suit une écriture sur un tube la tronque — mesuré, au
    premier essai de cette règle."""
    if not NODE:
        pytest.skip("node absent : les écrans ne peuvent pas être exécutés")
    with tempfile.TemporaryDirectory() as d:
        h, r_, o_ = (os.path.join(d, x) for x in ("h.js", "refs.json", "out.json"))
        io.open(r_, "w", encoding="utf-8").write(json.dumps(_memoire._refs()))
        io.open(h, "w", encoding="utf-8").write(
            _memoire._SOCLE + "(async function () {\n" + scenario + """
})().then(function () {
  fs.writeFileSync(process.argv[5], JSON.stringify(out));
  process.exit(0);
}).catch(function (e) { process.stderr.write(String(e && e.stack || e)); process.exit(3); });
""")
        r = subprocess.run([NODE, h, _memoire.PAGE_JS, r_, _memoire.PAGE_HTML, o_],
                           capture_output=True, text=True, timeout=90)
        if r.returncode != 0:
            pytest.fail("le scénario n'a pas tourné :\n%s" % (r.stderr or "")[-2500:])
        return json.loads(io.open(o_, encoding="utf-8").read())


_PEINTS = {}


def _peint(ecran):
    if not _PEINTS:
        _PEINTS.update(_ecrans_de_conformite())
    return _PEINTS[ecran]


_INTERACTIFS = {"a", "button", "label", "summary", "select", "option", "input", "textarea"}


def _pastilles_titrees(arbre):
    """Les éléments INERTES à `title` informatif d'un morceau de HTML — ceux
    que seule une légende peut rendre lisibles au clavier."""
    out = []
    for n in arbre.tous:
        t = n.attrs.get("title")
        if not t or n.tag in _INTERACTIFS or "onclick" in n.attrs:
            continue
        if any(p.tag in _INTERACTIFS or "onclick" in p.attrs for p in n.ancetres()):
            continue
        if _apprend_quelque_chose(t, n.texte()):
            out.append(n)
    return out


@pytest.mark.parametrize("ecran", ["isoArticles", "isoSoa", "iso27Articles", "iso27Soa", "nis2Gouv"])
def test_chaque_pastille_titree_d_un_ecran_de_conformite_a_sa_LEGENDE(ecran):
    """LE GARDE-FOU, SUR CE QUE LE MOTEUR PEINT VRAIMENT. Chaque pastille dont
    le `title` apprend quelque chose doit trouver, dans le même écran, une
    légende (`data-legende`) qui nomme l'une de ses classes, et qui dit son
    texte visible ET ce que le `title` disait. Un nouveau `title` sur une
    pastille, sans légende, fait tomber la règle."""
    a = _Arbre(_peint(ecran))
    pastilles = _pastilles_titrees(a)
    assert pastilles, "aucune pastille titrée peinte sur %s : la règle ne mesurerait rien" % ecran
    legendes = [n for n in a.tous if n.attrs.get("data-legende")]
    fautes = []
    for p in pastilles:
        vues = [l for l in legendes if set(l.attrs["data-legende"].split()) & set(p.classes())]
        if not vues:
            fautes.append("%s « %s » : aucune légende pour %s" % (p.tag, p.texte(), p.classes()))
            continue
        lt = _norm(" ".join(l.texte() for l in vues))
        visible = _norm(p.texte())
        # Ce que le `title` apprend, sans le libellé qu'il répète en tête.
        dit = re.sub(r"^" + re.escape(visible) + r"\s*:\s*", "", _norm(p.attrs["title"]))
        if visible not in lt or dit not in lt:
            fautes.append("%s « %s » : la légende ne dit pas « %s »" % (p.tag, p.texte(), dit))
    assert not fautes, "\n".join(sorted(set(fautes)))


def test_la_legende_de_la_pastille_n_apparait_qu_avec_la_pastille():
    """UNE LÉGENDE SANS PASTILLE EST DU BRUIT. Sur ISO 42001, « justification
    manquante » ne s'affiche que si une mesure décidée n'est pas justifiée."""
    global _memoire
    if _memoire is None:
        _memoire = _charger("test_memoire_ecrans")
    _memoire._refs()
    o = _executer_memoire("""
      var e = document.getElementById('iso-soa-body');
      isoRendreSoa(e, { ok: true, retenues: 0, ecartees: 0, recevable: false, dit: '',
                        non_decidees: [], sans_justification: [], bloquants: [], objectifs: [],
                        non_exhaustive: { quoi: '', consequence: '', article: '' } });
      out.h = e.innerHTML;
    """)
    assert "data-legende" not in o["h"], o["h"][:400]
    assert "cnf-justif" in _peint("isoSoa"), "le témoin : avec une mesure non justifiée, la légende est là"


def _page(arbre, ident):
    p = arbre.par_id(ident)
    assert p is not None, "l'écran %s a disparu" % ident
    return p


def _sous(noeud):
    pile = list(noeud.enfants)
    while pile:
        n = pile.pop(0)
        if isinstance(n, str):
            continue
        yield n
        pile[0:0] = n.enfants


def test_la_legende_des_priorites_est_AU_DESSUS_de_la_liste_de_l_audit():
    """TRENTE-QUATRE PASTILLES « P1 », « P2 », « P3 ». Leur sens n'était que
    dans un `title` ; il est écrit une fois, au-dessus de la liste, et dit ce
    que dit la table `prioTips` que les pastilles portent toujours."""
    a = _arbre("sentinel.html")
    ordre = list(_sous(_page(a, "p-audit-ia-act")))
    leg = [n for n in ordre if "audit-item-prio" in (n.attrs.get("data-legende") or "").split()]
    liste = [n for n in ordre if n.attrs.get("id") == "audit-sections"]
    assert leg and liste, "légende des priorités : %d, liste : %d" % (len(leg), len(liste))
    assert ordre.index(leg[0]) < ordre.index(liste[0]), "la légende n'est pas au-dessus de la liste"
    texte = _norm(leg[0].texte())
    tips = re.search(r"var prioTips = \{(.*?)\};", PAGE_JS).group(1)
    for p, dit in re.findall(r"(p[123]):'Priorité \d — ([^,.']+)", tips):
        assert p in texte, "la légende ne nomme pas %s" % p.upper()
        assert _norm(dit) in texte, "la légende ne dit pas « %s »" % dit


@pytest.mark.parametrize("ecran,classe,dit", [
    pytest.param("p-benchmark", "bench-na", "socle non relevé pour ce secteur", id="tiret"),
    pytest.param("p-ia50", "ia50-du", "ce que la ligne porte au-delà est un engagement, pas une obligation", id="du"),
    pytest.param("p-ia50", "ia50-du", "aucun paragraphe ne peut lui être rattaché", id="role-inconnu"),
])
def test_le_tiret_du_benchmark_et_la_colonne_du_de_l_article_50_ont_leur_legende(ecran, classe, dit):
    """LU DANS LE HTML DE L'ÉCRAN ET DANS LE CODE QUI PEINT LA PASTILLE : la
    classe que la légende nomme doit être celle que la pastille porte."""
    a = _arbre("sentinel.html")
    legs = [n for n in _sous(_page(a, ecran)) if classe in (n.attrs.get("data-legende") or "").split()]
    assert legs, "aucune légende de .%s dans #%s" % (classe, ecran)
    assert _norm(dit) in _norm(" ".join(l.visible() for l in legs)), "la légende ne dit pas « %s »" % dit
    assert re.search(r"""<span class="%s"[^>]* title=""" % re.escape(classe), PAGE_JS), (
        "aucune pastille titrée ne porte la classe %s : la légende couvrirait du vide" % classe)


def test_les_preuves_de_l_article_50_sont_ecrites_dans_leur_ecran():
    """LA PREUVE DE CHAQUE « mesuré ✓ » EST ÉCRITE EN TOUTES LETTRES dans le
    bloc de vérification du même écran : c'est lui, la légende des pastilles
    `.ia50-preuve`. Mesuré dans le code qui peint ce bloc : il écrit bien
    `m.preuve` dans le texte, pas dans un attribut."""
    a = _arbre("sentinel.html")
    bloc = [n for n in _sous(_page(a, "p-ia50")) if "ia50-preuve" in (n.attrs.get("data-legende") or "").split()]
    assert bloc and bloc[0].attrs.get("id") == "ia50-mesures", "le bloc des mesures ne se déclare pas légende"
    peint = _tranche("window.ia50Verifier = function(){")
    assert re.search(r"min-width:220px;[^']*>' \+ rgpdEsc\(m\.preuve\) \+ '</div>", peint), (
        "le bloc des mesures n'écrit plus la preuve en texte visible")
    assert PAGE_JS.count('class="ia50-preuve"') == 4, "les quatre états de « Mesuré » portent la classe"


# ══════════════════════════════════════════════════════════════════════════
#  2. LES ÉLÉMENTS ISOLÉS DONT L'EXPLICATION COMPTE : UN BOUTON D'AIDE (§3.1 b)
# ══════════════════════════════════════════════════════════════════════════

_AIDE = _tranche("window.aideTitre = function (id, libelle, texte) {") if \
    "window.aideTitre = function (id, libelle, texte) {" in PAGE_JS else ""


def test_le_bouton_d_aide_est_un_BOUTON_nomme_decrit_et_echappe():
    """EXÉCUTÉ. Le bouton « ? » : type button (jamais d'envoi de formulaire),
    nommé « Aide : … », fermé au départ, décrit par un élément caché qui porte
    le texte — et le texte ÉCHAPPÉ : un guillemet ou un chevron venus des
    données ne cassent rien."""
    assert _AIDE, "window.aideTitre est introuvable"
    o = _node("global.window = global;\n" + _AIDE + """
      process.stdout.write(JSON.stringify({ h: window.aideTitre('aide-x', 'Taux "net"', 'a < b & c > "d"') }));
    """)
    a = _Arbre(o["h"])
    b = [n for n in a.tous if n.tag == "button"]
    s = [n for n in a.tous if n.tag == "span"]
    assert len(b) == 1 and len(s) == 1, o["h"]
    b, s = b[0], s[0]
    assert b.attrs.get("type") == "button" and "aide-titre" in b.classes()
    assert b.attrs.get("aria-label") == 'Aide : Taux "net"'
    assert b.attrs.get("aria-expanded") == "false"
    assert b.attrs.get("aria-describedby") == "aide-x" == s.attrs.get("id")
    assert "hidden" in s.attrs and s.texte() == 'a < b & c > "d"'
    assert "title" not in b.attrs, "un title sur le bouton ferait deux bulles à la souris"


def _aides_de(noeud):
    return [n for n in _sous(noeud) if n.tag == "button" and "aide-titre" in n.classes()]


def _decrit(arbre, bouton):
    d = arbre.par_id(bouton.attrs.get("aria-describedby", ""))
    return d


def test_les_six_compteurs_de_l_audit_ont_un_bouton_d_aide_et_plus_de_title():
    """LE BLOC « 72 % » N'EST PAS FOCALISABLE : son `title` ne se lisait qu'à
    la souris. Six boutons d'aide, un par compteur, nommés par le libellé du
    compteur ; le bloc perd son `title` (deux bulles à la souris, sinon)."""
    a = _arbre("sentinel.html")
    kpis = [n for n in _sous(_page(a, "p-audit-ia-act")) if "audit-kpi" in n.classes()]
    assert len(kpis) == 6, len(kpis)
    for k in kpis:
        assert "title" not in k.attrs, "un compteur garde son title : « %s »" % k.attrs["title"][:40]
        b = _aides_de(k)
        assert len(b) == 1, "compteur sans bouton d'aide"
        lbl = [n for n in _sous(k) if "audit-kpi-lbl" in n.classes()][0]
        libelle = "".join(e for e in lbl.enfants if isinstance(e, str)).strip()
        assert b[0].attrs.get("aria-label") == "Aide : " + libelle
        assert b[0].attrs.get("type") == "button" and b[0].attrs.get("aria-expanded") == "false"
        d = _decrit(a, b[0])
        assert d is not None and "hidden" in d.attrs and len(d.texte()) > 20, "texte d'aide absent"


def test_les_indicateurs_de_gouvernance_ont_leur_lecture_dans_un_bouton_d_aide():
    """EXÉCUTÉ, avec le VRAI tableau de bord du moteur de gouvernance : chaque
    bloc d'indicateur perd son `title`, et son bouton d'aide porte la
    « lecture » de l'indicateur, mot pour mot."""
    import gouvernance
    tb = gouvernance.tableau_bord([])
    code = _tranche("window.gouvRenderKpis = function(){", "\nfunction gouvCouleurInd")
    code += _tranche("function gouvCouleurInd(i){", "\n}\n") + "\n}\n"
    code += _tranche("function rgpdEsc(s){", "\n")
    o = _node("global.window = global;\n" + _AIDE + "\n" + code + """
      const box = { innerHTML: '' };
      global.document = { getElementById: (i) => i === 'gouv-kpis' ? box : null };
      window.GOUV = { tb: JSON.parse(process.argv[2]) };
      window.gouvRenderKpis();
      process.stdout.write(JSON.stringify({ h: box.innerHTML }));
    """, json.dumps(tb))
    a = _Arbre(o["h"])
    kpis = [n for n in a.tous if "kpi" in n.classes()]
    assert len(kpis) == 6, len(kpis)
    lectures = dict((i["nom"], i["lecture"]) for i in tb["indicateurs"])
    for k in kpis:
        assert "title" not in k.attrs, "un indicateur garde son title"
        b = _aides_de(k)
        assert len(b) == 1, "indicateur sans bouton d'aide"
        nom = b[0].attrs["aria-label"][len("Aide : "):]
        assert _decrit(a, b[0]).texte() == lectures[nom], nom
    ids = [b.attrs["aria-describedby"] for b in _aides_de(a.racine)]
    assert len(set(ids)) == 6, "deux boutons décrits par le même élément : %s" % ids


@pytest.mark.parametrize("fonction,prefixe,n", [
    pytest.param("window.cartoRenderRoi = function(){", "aide-carto-roi-", 8, id="roi"),
    pytest.param("window.cartoRenderShortlist = function(){", "aide-carto-prio-", 4, id="priorites")])
def test_les_en_tetes_du_chiffrage_ont_un_bouton_d_aide(fonction, prefixe, n):
    """LU DANS LE CODE QUI PEINT LES DEUX TABLEAUX : plus aucun `th` à
    `title` ; un bouton d'aide par en-tête qui en avait un, avec un
    identifiant propre à son tableau — les deux peuvent être peints ensemble."""
    code = _tranche(fonction)
    assert not re.search(r"<th[^>]*title=", code), "un en-tête garde son title"
    # window.enTeteAide(visible, id, …) depuis les correctifs de la revue.
    ids = re.findall(r"window\.(?:aideTitre\(|enTeteAide\('[^']*', )'(" + re.escape(prefixe) + r"\d+)'", code)
    assert len(ids) == n and len(set(ids)) == n, ids


def test_la_methode_de_l_assistant_de_l_accueil_est_dans_un_bouton_d_aide():
    a = _arbre("index.html")
    sub = [n for n in a.tous if "cpc-sub" in n.classes()]
    assert len(sub) == 1
    assert "title" not in sub[0].attrs, "la méthode des réponses reste dans un title"
    b = _aides_de(sub[0])
    assert len(b) == 1 and b[0].attrs.get("type") == "button"
    d = _decrit(a, b[0])
    assert d is not None and "hidden" in d.attrs and "EUR-Lex" in d.texte()


def test_la_zone_de_depot_dit_en_TEXTE_ce_que_disait_son_title():
    """§3.1 c) : le `title` de la zone répétait son texte, à la souris
    seulement. Le texte visible dit tout ; le `title` est retiré."""
    z = _arbre("sentinel.html").par_id("rag-drop-zone")
    assert z is not None and "title" not in z.attrs, "la zone de dépôt garde son title"
    t = _norm(z.visible())
    assert "glissez-déposez un fichier" in t and "cliquez pour parcourir" in t, t


# ══════════════════════════════════════════════════════════════════════════
#  3. LES BOUTONS À GLYPHE ONT UN NOM (§3.2)
# ══════════════════════════════════════════════════════════════════════════

def _boutons_a_glyphe(src, fichier):
    """Les <button> dont le texte n'est qu'un glyphe (ou deux lettres) — dans
    le HTML, et dans les chaînes du JavaScript qui en écrit."""
    out = []
    for m in re.finditer(r"<button\b([^<>]*)>((?:(?!</button>).){0,80}?)</button>", src, re.S):
        attrs, corps = m.group(1), m.group(2)
        if "'+" in corps or '"+' in corps:
            continue
        t = re.sub(r"<[^>]*>", "", corps)
        if "\\u" in t:
            t = t.encode("latin-1", "backslashreplace").decode("unicode_escape")
        t = re.sub(r"\s+", "", _html.unescape(t))
        if re.search(r"[A-Za-zÀ-ÿ0-9]{3,}", t):
            continue
        out.append((fichier, src.count("\n", 0, m.start()) + 1, t, attrs))
    return out


@pytest.mark.parametrize("fichier", ["sentinel.html", "sentinel.page.js", "index.html"])
def test_aucun_bouton_a_GLYPHE_n_est_nomme_par_son_glyphe(fichier):
    """« × », « ‹ », « ← », « FR » : ce qu'entendait un lecteur d'écran. Chaque
    bouton dont le texte n'est qu'un glyphe porte un `aria-label` qui dit
    l'action — le glyphe, lui, n'est pas un nom."""
    src = {"sentinel.html": SENTINEL, "sentinel.page.js": PAGE_JS, "index.html": ACCUEIL}[fichier]
    b = _boutons_a_glyphe(src, fichier)
    assert len(b) >= 3, "le relevé ne trouve presque rien : %d" % len(b)
    sans = []
    for f, ligne, t, attrs in b:
        m = re.search(r'aria-label="([^"]*)"', attrs)
        if not m or not re.search(r"[A-Za-zÀ-ÿ]{3,}", m.group(1)):
            sans.append("%s:%d « %s »" % (f, ligne, t))
    assert not sans, "boutons nommés par leur glyphe :\n  " + "\n  ".join(sans)


def test_le_x_des_fenetres_n_ouvre_pas_de_bulle_son_title_EGALE_son_nom():
    """T-12. Le × s'appelle « Fermer cette fenêtre » ; son `title`, gardé
    pour la souris, dit la même chose — /bulle-titre.js n'ouvre donc rien à la
    tabulation (critère §2.2, celui du script). Mesuré avant : une bulle
    « Fermer cette fenêtre » sur chaque ×, au-dessus de la fenêtre."""
    croix = re.findall(r"<button\b([^<>]*class=\"mat-modal-close\"[^<>]*)>", PAGE_JS)
    assert len(croix) >= 16, len(croix)
    for attrs in croix:
        nom = re.search(r'aria-label="([^"]*)"', attrs)
        assert nom and nom.group(1) == "Fermer cette fenêtre", attrs[:120]
        t = re.search(r'title="([^"]*)"', attrs)
        assert not t or not _apprend_quelque_chose(t.group(1), nom.group(1)), attrs[:120]


def test_les_fleches_de_navigation_disent_l_action_et_le_VRAI_raccourci():
    """EXÉCUTÉ. navInit crée quatre boutons ; chacun reçoit le nom de son
    action et, dans aria-keyshortcuts, une combinaison que l'écouteur de la
    page reconnaît VRAIMENT — vérifié en la lui envoyant : elle doit produire
    la même action que le clic du bouton. Et le `title` n'apprend rien de
    plus que le nom (nom suivi du raccourci)."""
    code = _tranche("window.navInit = function(){")
    o = _node("""
      const crees = [], ecouteurs = [], actions = [];
      function El(tag) { this.tag = tag; this.attrs = {}; this.style = {}; }
      El.prototype.setAttribute = function (k, v) { this.attrs[k] = String(v); };
      global.window = global;
      global.document = {
        getElementById: () => null,
        createElement: (t) => { const e = new El(t); crees.push(e); return e; },
        body: { appendChild: () => {} },
        addEventListener: (t, f) => { if (t === 'keydown') ecouteurs.push(f); },
      };
      window.navGoRelative = (d) => actions.push('va:' + d);
      window.navScrollTo = (d) => actions.push('defile:' + d);
      window.navRefresh = () => {};
    """ + code + """
      window.navInit();
      const out = [];
      for (const b of crees.filter(e => e.tag === 'button')) {
        actions.length = 0; b.onclick(); const parClic = actions.slice();
        actions.length = 0;
        const m = (b.attrs['aria-keyshortcuts'] || '').match(/^Alt\\+(\\w+)$/);
        if (m) ecouteurs.forEach(f => f({ altKey: true, key: m[1], target: {}, preventDefault() {} }));
        out.push({ id: b.id, title: b.title, nom: b.attrs['aria-label'] || null,
                   touches: b.attrs['aria-keyshortcuts'] || null, clic: parClic, clavier: actions.slice() });
      }
      process.stdout.write(JSON.stringify(out));
    """)
    assert [b["id"] for b in o] == ["nav-prev", "nav-next", "nav-top", "nav-bottom"], o
    for b in o:
        assert b["nom"] and re.search(r"[A-Za-zé]{3,}", b["nom"]), b
        assert b["touches"], "%s sans raccourci déclaré" % b["id"]
        assert b["clavier"] == b["clic"] and b["clic"], (
            "%s : %s déclenche %s, le clic %s" % (b["id"], b["touches"], b["clavier"], b["clic"]))
        assert not _apprend_quelque_chose(b["title"], b["nom"]), b


def _bouton(arbre, cond):
    return [n for n in arbre.tous if n.tag in ("button", "a") and cond(n)]


@pytest.mark.parametrize("fichier,classe,en_tete", [
    pytest.param("sentinel.html", "sb-lbtn", True, id="sb-lbtn"), pytest.param("sentinel.html", "vl-btn", True, id="vl-btn"),
    pytest.param("index.html", "lbtn", True, id="lbtn"), pytest.param("index.html", "ft-social", False, id="ft-social")])
def test_le_texte_VISIBLE_est_dans_le_nom(fichier, classe, en_tete):
    """2.5.3. « FR », « in », « AI » : le nom dit ce que le bouton fait ET
    contient ce qu'on voit — qui dit « cliquer sur FR » à sa commande vocale
    doit tomber dessus. Pour une langue, le code EN TÊTE et comme un mot :
    « Français » contient « fr », il ne contient pas le bouton « FR » (mesuré
    par la mutation qui l'a d'abord laissé passer). Pour « in », la marque :
    « LinkedIn » (§3.2). Le globe d'i-aes.com N'EST PLUS EXCLU : la première
    version l'écartait au motif que bascule.js le renommerait — faux (revue
    du lot 3) : bascule.js ne nomme que les liens SANS texte, et « 🌐 » en a
    un. L'exclusion faisait passer la règle pour une raison sans rapport."""
    a = _arbre(fichier)
    bs = [n for n in _bouton(a, lambda n: classe in n.classes())
          if re.sub(r"\s+", "", n.texte()) != "ALL"]
    assert bs, "aucun .%s" % classe
    for b in bs:
        vu = re.sub(r"\s+", " ", b.texte()).strip()
        vu = re.sub(r"^[^\w]+", "", vu)
        nom = b.attrs.get("aria-label") or ""
        dedans = (re.match(re.escape(vu) + r"(?![A-Za-zÀ-ÿ])", nom) if en_tete
                  else vu.lower() in nom.lower())
        assert len(nom) > len(vu) + 2 and dedans, ".%s « %s » : nom « %s »" % (classe, vu, nom)


def test_le_bouton_d_agrandissement_de_l_accueil_garde_un_nom_JUSTE():
    """EXÉCUTÉ. Le glyphe change (⤢ / ⤡) et le `title` aussi : le nom doit
    suivre, sinon « Agrandir » resterait annoncé sur un panneau agrandi."""
    code = _tranche("window.cpxExpandToggle", "\n};\nwindow.cpxCollapseAll", ACCUEIL_JS) + "\n};\n"
    code += _tranche("window.cpxCollapseAll = function(){", None, ACCUEIL_JS)
    o = _node("""
      function Cl() { const s = new Set(); return { add: (c) => s.add(c), remove: (c) => s.delete(c), contains: (c) => s.has(c) }; }
      const btn = { attrs: {}, setAttribute(k, v) { this.attrs[k] = v; }, textContent: '⤢', title: 'Agrandir pour une meilleure lecture' };
      const panel = { classList: Cl(), querySelector: () => btn };
      const over = { classList: Cl() };
      global.window = global;
      global.document = { getElementById: (i) => (i === 'cpcPanel' ? panel : i === 'cpx-overlay' ? over : null),
                          createElement: () => over, body: { appendChild() {} } };
    """ + code + """
      const out = [];
      window.cpxExpandToggle('cpcPanel'); out.push([btn.title, btn.attrs['aria-label'] || null]);
      window.cpxExpandToggle('cpcPanel'); out.push([btn.title, btn.attrs['aria-label'] || null]);
      process.stdout.write(JSON.stringify(out));
    """)
    assert o[0][0] == "Réduire" and o[1][0].startswith("Agrandir"), o
    for title, nom in o:
        assert nom == title, "le nom ne suit pas : title « %s », nom « %s »" % (title, nom)


# ══════════════════════════════════════════════════════════════════════════
#  4. LES « × » CLIQUABLES SONT DES BOUTONS (§3.2, C-7)
# ══════════════════════════════════════════════════════════════════════════

_CROIX = r"<(div|span)\b[^<>]*\bonclick=[^<>]*>\s*(×|\\u00[dD]7|&times;|✕)"


def test_aucun_div_ni_span_CLIQUABLE_ne_porte_une_croix():
    """Un <div onclick> n'a ni focus ni nom : le « × » ne se supprimait qu'à
    la souris. Mesuré avant : quatre dans le registre, deux dans le
    comparateur, un par évaluation enregistrée."""
    faux = []
    for nom, src in (("sentinel.page.js", PAGE_JS), ("sentinel.html", SENTINEL), ("index.html", ACCUEIL)):
        faux += ["%s:%d : %s" % (nom, src.count("\n", 0, m.start()) + 1, m.group(0)[:90])
                 for m in re.finditer(_CROIX, src)]
    assert not faux, "\n".join(faux)


@pytest.mark.parametrize("site,attendu", [
    pytest.param("cjRemove(", r"aria-label=\"Retirer '\+code\+' du comparateur\"", id="comparateur"),
    pytest.param("cpEvalRemove(", r"aria-label=\"Supprimer l\\u2019\\u00e9valuation ' \+ cpEvalAttr\(cpEvalQuoi\(e\)\) \+ '\"", id="evaluation"),
    pytest.param("regDelete(", r"aria-label=\"Supprimer '\+regAttr\(s\.nom\)\+' du registre\"", id="registre"),
])
def test_chaque_croix_de_suppression_est_un_bouton_qui_dit_QUOI(site, attendu):
    """Un <button type="button">, et un nom qui dit ce qui part : trois « ×
    Supprimer » l'un sous l'autre ne se distinguent pas à l'oreille."""
    b = [m.group(0) for m in re.finditer(r"<button\b[^<>]*" + re.escape(site) + r"[^<>]*>\s*(?:×|\\u00[dD]7)", PAGE_JS)]
    assert len(b) == 1, "le « × » de %s n'est pas un bouton : %s" % (site, b)
    assert 'type="button"' in b[0]
    assert re.search(attendu, b[0]), b[0]


def test_le_nom_du_systeme_ne_casse_pas_le_nom_du_bouton():
    """EXÉCUTÉ. Le nom d'un système entre dans un attribut : un guillemet le
    couperait."""
    code = _tranche("  function regAttr(v){", "\n  }\n") + "\n  }\n"
    o = _node(code + "process.stdout.write(JSON.stringify(regAttr('Le « \"robot\" » <b> & co')));")
    assert o == "Le « &quot;robot&quot; » &lt;b&gt; &amp; co", o


# ══════════════════════════════════════════════════════════════════════════
#  5. L'ACCUEIL : PLUS DE DOUBLE BULLE (§3.3)
# ══════════════════════════════════════════════════════════════════════════

_DIX = ["nav-up", "nav-down", "cp-nav-down", "btt", "ck-btn", "acc-reading-btn",
        "acc-dyslexia-btn", "acc-contrast-btn", "vbtn", "cp-ft-top"]


def test_aucun_element_de_l_accueil_ne_porte_title_ET_data_tooltip():
    """DEUX BULLES À LA SOURIS : la native, et celle d'/infobulles.js. Mesuré
    avant : dix éléments."""
    doubles = [n.attrs.get("id") or n.attrs.get("class") for n in _arbre("index.html").tous
               if "title" in n.attrs and "data-tooltip" in n.attrs]
    assert not doubles, doubles


def test_les_dix_gardent_leur_bulle_et_un_NOM():
    """Le `title` parti, rien ne doit manquer : la bulle data-tooltip reste,
    et le nom (aria-label, ou un texte) dit l'action — « ↑ » n'en est pas un.
    Mesuré avant : « ↑ » et « 📰 » n'avaient que leur `title` pour dire ce
    qu'ils font."""
    fautes = []
    for ident in _DIX:
        n = _arbre("index.html").par_id(ident)
        if n is None or not n.attrs.get("data-tooltip"):
            fautes.append("%s a perdu sa bulle data-tooltip" % ident)
            continue
        nom = n.attrs.get("aria-label") or n.texte()
        if not re.search(r"[A-Za-zÀ-ÿ]{3,}", nom):
            fautes.append("%s s'appelle « %s »" % (ident, nom.strip()))
    assert not fautes, fautes


def test_les_fleches_de_section_de_l_accueil_declarent_le_raccourci_que_la_page_ECOUTE():
    """Le raccourci était dans le `title` (retiré, pour une bulle unique) :
    il passe dans aria-keyshortcuts — et c'est celui que l'écouteur de
    index.page.js associe à la même action que le bouton."""
    ecoute = dict((act.replace(" ", ""), cle) for cle, act in
                  re.findall(r"e\.altKey && e\.key === '(\w+)'\)\{\s*e\.preventDefault\(\); (\w+\([-\d]+\));", ACCUEIL_JS))
    assert len(ecoute) == 4, ecoute
    a = _arbre("index.html")
    for ident in ("nav-haut", "nav-up", "nav-down", "nav-bas"):
        n = a.par_id(ident)
        action = n.attrs["onclick"].replace(" ", "")
        assert n.attrs.get("aria-keyshortcuts") == "Alt+" + ecoute[action], (
            "%s (%s) : %r au lieu de Alt+%s" % (ident, action, n.attrs.get("aria-keyshortcuts"), ecoute[action]))


# ══════════════════════════════════════════════════════════════════════════
#  6. LES CHAMPS : UN NOM, ET L'AIDE VISIBLE (§3.4)
# ══════════════════════════════════════════════════════════════════════════

_SANS_NOM = ["qualif-filtre", "qualif-decideur", "histo-filter-select", "rag-filter-select",
             "ent-ent-name", "conn-url", "conn-sec", "form-date", "shadow-risk-filter"]


def test_aucun_champ_de_sentinel_ne_garde_un_title():
    """Sur un champ, un `title` ne se lit jamais au doigt (le clavier virtuel
    ou le sélecteur natif recouvre tout) ni au clavier. Mesuré avant : dix
    champs, dont neuf n'avaient pas d'autre nom."""
    t = ["%s#%s" % (n.tag, n.attrs.get("id")) for n in _arbre("sentinel.html").tous
         if n.tag in ("input", "select", "textarea") and "title" in n.attrs]
    assert not t, t


@pytest.mark.parametrize("ident", _SANS_NOM)
def test_le_champ_a_un_NOM(ident):
    a = _arbre("sentinel.html")
    n = a.par_id(ident)
    assert n is not None, ident
    labels = [l for l in a.tous if l.tag == "label" and l.attrs.get("for") == ident]
    nom = n.attrs.get("aria-label") or " ".join(l.texte() for l in labels) or ""
    assert re.search(r"[A-Za-zÀ-ÿ]{3,}", nom), "%s n'a pas de nom" % ident


@pytest.mark.parametrize("ident,dit", [
    pytest.param("sb-role", "un chemin de lecture par métier", id="sb-role"),
    pytest.param("qualif-decideur", "le nom inscrit au registre", id="qualif-decideur"),
    pytest.param("conn-sec", "transmis mais jamais réaffiché", id="conn-sec")])
def test_l_aide_d_un_champ_est_VISIBLE_et_reliee(ident, dit):
    """Là où le `title` était une aide (et pas un nom) : elle est écrite sous
    le champ, et le champ la porte en description (3.3.2)."""
    a = _arbre("sentinel.html")
    n = a.par_id(ident)
    d = a.par_id(n.attrs.get("aria-describedby", "") or "-")
    assert d is not None, "%s n'est décrit par rien" % ident
    assert not d.cache() and not any(p.cache() for p in d.ancetres()), "l'aide de %s est cachée" % ident
    assert _norm(dit) in _norm(d.visible()), d.texte()


# ══════════════════════════════════════════════════════════════════════════
#  7. LES AVERTISSEMENTS CRITIQUES SE LISENT SANS SURVOL (§3.5)
# ══════════════════════════════════════════════════════════════════════════

_parcours = None


def test_Terminer_ECRIT_que_rien_n_est_declare_conforme():
    """EXÉCUTÉ PAR LE VRAI MOTEUR DU BANDEAU. Mesuré avant : l'avertissement
    n'était que dans le `title` du bouton — dans le texte que le bandeau
    affiche, rien. Il y est, et le bouton le porte en description."""
    global _parcours
    if _parcours is None:
        _parcours = _charger("test_parcours_avancement")
    r = _parcours._executer("""
      guidedStartStep(P.id, P.steps.length - 1);
      out.bandeau = zones['guided-banner'].innerHTML;
    """)
    a = _Arbre(r["bandeau"])
    visible = _norm(a.racine.visible())
    assert "rien n’est déclaré conforme" in visible, visible[-200:]
    fin = [n for n in a.tous if n.tag == "button" and "Terminer" in n.texte()]
    assert len(fin) == 1
    d = a.par_id(fin[0].attrs.get("aria-describedby", "") or "-")
    assert d is not None and "rien n’est déclaré conforme" in _norm(d.visible())
    # CE QUI EST ÉCRIT N'A PAS BESOIN DE BULLE : le `title` redisait
    # l'avertissement dans une autre version, et s'ouvrait à chaque
    # tabulation (revue du lot 3).
    assert "title" not in fin[0].attrs, "« Terminer » garde un title : « %s »" % fin[0].attrs["title"]


@pytest.mark.parametrize("fonction,appel,dit", [
    pytest.param("window.billingRunExecute = function(){", "window.billingRunExecute()", "prélève réellement", id="prelevement"),
    pytest.param("window.rgpdPurge = function(simulation){", "window.rgpdPurge(false)", "anonymis", id="purge"),
    pytest.param("window.histoPurgeAll = function(){", "window.histoPurgeAll()", "irréversible", id="historique"),
    pytest.param("window.regDelete = function(id){", "window.regDelete(7)", "définitivement", id="registre"),
])
def test_une_action_irreversible_DEMANDE_et_DIT_avant_d_agir(fonction, appel, dit):
    """EXÉCUTÉ, EN REFUSANT. Les quatre actions qui ne se défont pas —
    prélèvement Stripe réel, purge, historique, suppression du registre —
    posent la question AVANT, et la question dit l'avertissement que le
    `title` portait. Refusée : aucune requête ne part. (Ces quatre
    confirmations existaient ; la règle les garde.)"""
    code = _tranche(fonction)
    o = _node("""
      const questions = [], requetes = [];
      global.window = global;
      global.confirm = (m) => { questions.push(String(m)); return false; };
      global.fetch = (u) => { requetes.push(String(u)); return new Promise(() => {}); };
      global.document = { getElementById: () => ({ textContent: '', innerHTML: '' }) };
      global.alert = () => {};
    """ + code + "\n" + appel + """;
      process.stdout.write(JSON.stringify({ questions, requetes }));
    """)
    assert len(o["questions"]) == 1 and dit in o["questions"][0].replace("é", "é"), o
    assert o["requetes"] == [], "refusée, l'action est quand même partie : %s" % o["requetes"]


# ══════════════════════════════════════════════════════════════════════════
#  8. LE GARDE-FOU D'INVENTAIRE NE SE PÉRIME PAS EN SILENCE
# ══════════════════════════════════════════════════════════════════════════

def test_la_liste_des_generiques_admis_est_NOMINATIVE_et_justifiee():
    """Chaque entrée nomme un écran qui existe, une classe que le code pose,
    et dit pourquoi ni légende ni bouton d'aide."""
    d = json.loads(_lire(os.path.join("tests", "titres_generiques_admis.json")))
    assert isinstance(d.get("admis"), list)
    ecrans = set(re.findall(r'id="(p-[a-z0-9-]+)"', SENTINEL))
    for a in d["admis"]:
        assert a.get("ecran") in ecrans, a
        assert re.search(r"""class="[^"]*\b%s\b""" % re.escape(a.get("classe", "")), SENTINEL + PAGE_JS), a
        assert len(a.get("justification", "")) >= 40, a


def _chaine_js(src, nom):
    m = re.search(r"var " + nom + r" = ((?:'[^']*'\s*\+?\s*)+);", src)
    assert m, "%s introuvable" % nom
    return "".join(re.findall(r"'([^']*)'", m.group(1)))


def test_la_recette_applique_le_MEME_critere_que_le_script():
    """LE GARDE-FOU COPIE LE CRITÈRE DE /bulle-titre.js (§2.2) : ce qui est
    « interactif », ce qu'est un raccourci. Une copie qui dériverait
    compterait autre chose que ce que le script montre — la recette
    passerait pour une raison sans rapport."""
    rec = _lire("recette_complements.js")
    assert "titres_generiques_admis.json" in rec
    inter = re.search(r"const INTER = '([^']*)';", rec)
    assert inter and inter.group(1) == _chaine_js(BULLE, "INTERACTIF"), "INTERACTIF a dérivé"
    racc = re.search(r"const RACC = /(.+?)/i;", rec)
    assert racc and racc.group(1) == RACCOURCI.pattern, "RACCOURCI a dérivé"


@pytest.mark.parametrize("ancre", ["audit-kpi", "aide-titre", "mat-modal-close", "sb-pager-btn", "nav-prev",
                                   "sb-lbtn", "procOpenDoc", "proc-modal-body", "rag-drop-zone",
                                   "qualif-decideur", "conn-sec", "shadow-risk-filter", "sb-role",
                                   "billingRunExecute", "rgpdPurge(false)", "histoPurgeAll", "rs-del",
                                   "cj-tag-rm", "cpEvaluations", "guidedStartStep",
                                   "GUIDED_PATHS", "cpcToggle", "aide-cpc-methode", "data-legende",
                                   "DECL_VERSION", "page-guide-btn", "cartoGoStep", "__cartoState", "CARTO_UC",
                                   "evals-rows", "suppr-x", "cj-add-btn", "ft-social", "audit-item-prio"])
def test_la_recette_vise_des_ancres_QUI_EXISTENT(ancre):
    rec = _lire("recette_complements.js")
    assert ancre in rec, "la recette ne vise plus %r" % ancre
    assert ancre in SENTINEL + PAGE_JS + ACCUEIL + ACCUEIL_JS, (
        "%r a disparu du code : la recette mesure un identifiant mort" % ancre)


# ══════════════════════════════════════════════════════════════════════════
#  9. LES CORRECTIFS DE LA REVUE DU LOT 3
# ══════════════════════════════════════════════════════════════════════════

def _elements_simules():
    """Un DOM minimal pour exécuter les vraies fonctions : des éléments qui
    savent `closest`, `querySelectorAll` (classes, balises, [attribut]) et
    `focus` — et un document dont le focus RETOMBE SUR <body> quand
    l'élément qui l'avait quitte la page, comme dans un navigateur."""
    return r"""
      function El(tag, attrs, parent) {
        this.tagName = tag.toUpperCase(); this.attrs = attrs || {}; this.enfants = []; this.parentNode = null;
        this.id = this.attrs.id || ''; this.className = this.attrs['class'] || '';
        if (parent) parent.ajouter(this);
      }
      El.prototype.ajouter = function (e) { e.parentNode = this; this.enfants.push(e); if (e.id) IDS[e.id] = e; return e; };
      El.prototype.vider = function () { this.enfants.forEach(function (e) { e.parentNode = null; }); this.enfants = []; };
      El.prototype.getAttribute = function (k) { return k in this.attrs ? this.attrs[k] : null; };
      El.prototype.setAttribute = function (k, v) { this.attrs[k] = String(v); };
      El.prototype.hasAttribute = function (k) { return k in this.attrs; };
      El.prototype.focus = function () { document.activeElement = this; };
      function _un(e, s) {
        s = s.trim();
        var m = s.match(/^([a-z]*)((?:\.[\w-]+)*)((?:\[[\w-]+\])*)(:not\(\[disabled\]\))?$/i);
        if (!m) throw new Error('sélecteur non simulé : ' + s);
        if (m[1] && e.tagName !== m[1].toUpperCase()) return false;
        var cl = (e.className || '').split(/\s+/);
        var ok = (m[2].match(/[\w-]+/g) || []).every(function (c) { return cl.indexOf(c) >= 0; });
        ok = ok && (m[3].match(/[\w-]+/g) || []).every(function (a) { return a in e.attrs; });
        return ok && !(m[4] && 'disabled' in e.attrs);
      }
      function _correspond(e, sel) { return sel.split(',').some(function (s) { return _un(e, s); }); }
      El.prototype.closest = function (sel) { for (var e = this; e; e = e.parentNode) if (e.tagName && _correspond(e, sel)) return e; return null; };
      El.prototype.querySelectorAll = function (sel) {
        var out = []; (function tour(n) { n.enfants.forEach(function (e) { if (_correspond(e, sel)) out.push(e); tour(e); }); })(this); return out; };
      El.prototype.querySelector = function (sel) { return this.querySelectorAll(sel)[0] || null; };
      function _dansLaPage(e) { for (; e; e = e.parentNode) if (e === document.body) return true; return false; }
      var IDS = {};
      global.document = { body: null, activeElement: null,
        getElementById: function (i) { var e = IDS[i]; return e && _dansLaPage(e) ? e : null; } };
      document.body = new El('body'); document.activeElement = document.body;
      /* LE REPEINT : ce que fait `innerHTML` — les anciens enfants quittent la
         page, et le focus qu'ils portaient retombe sur <body>. */
      function repeindre(boite, fabriquer) {
        boite.vider(); fabriquer(boite);
        if (!_dansLaPage(document.activeElement)) document.activeElement = document.body;
      }
      function decrire(e) { return e ? (e.tagName + (e.id ? '#' + e.id : '') + (e.attrs['data-x'] ? '[' + e.attrs['data-x'] + ']' : '')) : null; }
      global.window = global;
    """


def _helpers_focus():
    """Les deux fonctions du focus après un retrait, si le code les a —
    absentes du code d'avant : alors rien ne ramène le focus, et c'est ce
    que la règle doit voir."""
    out = ""
    for debut in ("window.focusRang = function (boite, selecteur) {",
                  "window.focusRendre = function (boite, selecteur, rang) {"):
        if debut in PAGE_JS:
            out += _tranche(debut) + "\n"
    return out


def test_un_clic_sur_un_bouton_d_aide_N_EST_PAS_une_reponse():
    """EXÉCUTÉ : la VRAIE fonction `_railSurReponse`. LE DÉFAUT MESURÉ (revue
    du lot 3, audit IA Act) : chaque clic sur un « ? » passait pour une
    réponse — un POST /api/parcours/ia_act, une version de déclarations de
    plus, le bandeau `role="status"` réécrit. LE TÉMOIN : un autre bouton du
    même écran, lui, compte toujours — sans quoi « rien » passerait aussi sur
    une fonction qui ne compte plus rien."""
    code = PAGE_JS[PAGE_JS.index("function _railSurReponse(ev) {"):]
    code = code[:code.index("\n}\n") + 3]
    o = _node(_elements_simules() + """
      var versions = 0, demandes = [];
      global.declarationsChangees = function () { versions++; };
      global.railNormeDuPanneau = function (e) { return e === 'audit-ia-act' ? 'ia_act' : null; };
      global.railDemander = function (n) { demandes.push(n); };
    """ + code + """
      var page = new El('div', { id: 'p-audit-ia-act', 'class': 'page on' }, document.body);
      var kpi = new El('div', { 'class': 'audit-kpi' }, page);
      var aide = new El('button', { type: 'button', 'class': 'aide-titre' }, kpi);
      var texte = new El('span', { 'class': 'audit-kpi-lbl' }, kpi);
      var guide = new El('button', { 'class': 'page-guide-btn' }, page);
      function cliquer(t) { var v = versions, d = demandes.length;
        _railSurReponse({ type: 'click', target: t }); return [versions - v, demandes.slice(d)]; }
      process.stdout.write(JSON.stringify({ temoin: cliquer(guide), texte: cliquer(texte), aide: cliquer(aide) }));
    """)
    assert o["temoin"] == [1, ["ia_act"]], (
        "le témoin : un bouton de l'écran doit compter comme une réponse — %s" % o)
    assert o["texte"] == [0, []], o
    assert o["aide"] == [0, []], (
        "un clic sur « ? » passe pour une réponse : %d version(s), calcul(s) du rail %s" % tuple(o["aide"]))


def _nom_calcule(n):
    """Le nom d'un en-tête tel que le calcule un navigateur (accname, en
    bref) : son `aria-label`, sinon son contenu — où un bouton compte pour
    SON nom, et où ce qui est `hidden` ne compte pas."""
    al = (n.attrs.get("aria-label") or "").strip()
    if al:
        return al
    morceaux = []
    for e in n.enfants:
        if isinstance(e, str):
            morceaux.append(e)
        elif not e.cache():
            morceaux.append(_nom_calcule(e) if e.tag == "button" and e.attrs.get("aria-label") else
                            (e.attrs.get("aria-label") or _nom_calcule(e)))
    return re.sub(r"\s+", " ", " ".join(morceaux)).strip()


_CARTO_STUBS = """
  global.window = global;
  const box = { innerHTML: '' };
  global.document = { getElementById: (i) => (i === 'carto-roi' || i === 'carto-shortlist') ? box : null };
  global.cartoSelectedList = () => [{ n: 'Cas A', p: 'Achats', f: 'ML' }, { n: 'Cas B', p: 'Finance', f: 'LLM' }];
  global.cartoKey = (u) => u.n;
  global.cartoScoreOf = () => ({ impact: 3, faisabilite: 3, donnees: 3, risque: 3 });
  global.cartoGlobal = () => 3;
  global.cartoPriority = () => 'P2';
  global.cartoQuadrant = () => ({ col: 'x', label: 'y' });
  global.cartoRoiOf = () => ({ assiette: 1000, gain: 0.1, setup: 100, run: 10 });
  global.cartoRoiCompute = () => ({ gainAnnuel: 100, netAn1: -10, roiPct: -0.1, paybackMois: 12 });
  global.cartoRoiTotals = () => {}; global.cartoUpdateSynthese = () => {};
"""


@pytest.mark.parametrize("fonction,n", [
    pytest.param("window.cartoRenderRoi = function(){", 8, id="roi"),
    pytest.param("window.cartoRenderShortlist = function(){", 4, id="priorites")])
def test_les_colonnes_du_chiffrage_s_appellent_par_leur_LIBELLE(fonction, n):
    """EXÉCUTÉ : les deux tableaux peints par leurs vraies fonctions. LE
    DÉFAUT MESURÉ (revue du lot 3, arbre de Chromium) : la colonne
    s'appelait « ASSIETTE ANNUELLE Aide : Assiette annuelle » — le bouton
    d'aide entrait dans le nom de l'en-tête, et un lecteur d'écran le
    répétait à chaque cellule. Chaque en-tête à bouton d'aide s'appelle par
    son libellé ; le bouton garde « Aide : … »."""
    aides = ""
    for debut in ("window.aideTitre = function (id, libelle, texte) {",
                  "window.enTeteAide = function (visible, id, libelle, texte) {"):
        if debut in PAGE_JS:
            aides += _tranche(debut) + "\n"
    o = _node(_CARTO_STUBS + aides + _tranche(fonction) + """
      window.%s();
      process.stdout.write(JSON.stringify({ h: box.innerHTML }));
    """ % fonction.split(" = ")[0].replace("window.", ""))
    a = _Arbre(o["h"])
    ths = [t for t in a.tous if t.tag == "th" and _aides_de(t)]
    assert len(ths) == n, "%d en-têtes à bouton d'aide, %d attendus" % (len(ths), n)
    fautes = []
    for t in ths:
        libelle = _aides_de(t)[0].attrs["aria-label"][len("Aide : "):]
        nom = _nom_calcule(t)
        if nom != libelle or "Aide" in nom:
            fautes.append("« %s » au lieu de « %s »" % (nom, libelle))
    assert not fautes, "le nom de colonne embarque le bouton :\n  " + "\n  ".join(fautes)


def test_l_en_tete_a_aide_echappe_son_libelle():
    """EXÉCUTÉ. Le libellé entre dans un attribut : un guillemet le couperait."""
    assert "window.enTeteAide = function (visible, id, libelle, texte) {" in PAGE_JS, "window.enTeteAide absent"
    o = _node("global.window = global;\n" + _AIDE + "\n"
              + _tranche("window.enTeteAide = function (visible, id, libelle, texte) {") + """
      process.stdout.write(JSON.stringify({ h: window.enTeteAide('Taux', 'aide-t', 'Taux "net" <b>', 'x') }));
    """)
    th = [n for n in _Arbre(o["h"]).tous if n.tag == "th"]
    assert len(th) == 1 and th[0].attrs.get("aria-label") == 'Taux "net" <b>', o["h"]


@pytest.mark.parametrize("site", ["comparateur", "evaluations", "registre"])
def test_apres_un_retrait_le_focus_RESTE_dans_la_liste(site):
    """EXÉCUTÉ : les VRAIES fonctions de retrait, avec un DOM où le repeint
    fait retomber le focus sur <body> — ce qu'il fait dans un navigateur.
    LE DÉFAUT MESURÉ (revue du lot 3) : Entrée sur « Retirer DE du
    comparateur », puis focus sur BODY ; de même pour une évaluation. Ce lot
    rendait ces « × » atteignables au clavier : c'est lui qui exposait le
    défaut (WCAG 2.4.3).
    On retire le 2e « × » de trois → le focus va au nouveau 2e ; le dernier →
    au nouveau dernier ; le seul → au contrôle que garde la liste vide
    (« + Ajouter un pays », un lien) ; et sans focus sur un « × » au
    départ (un clic de souris sous Safari), rien ne bouge — LE TÉMOIN que la
    règle ne fait pas que « poser le focus quelque part »."""
    commun = _elements_simules() + _helpers_focus()
    if site == "comparateur":
        code = _tranche("function cjRemove(code){", "\n}\n") + "\n}\n"
        scen = """
          var boite = new El('div', { id: 'cj-tags' }, document.body);
          global.cjSelected = ['FR', 'DE', 'IT'];
          global.cjRender = function () { repeindre(boite, function (b) {
            cjSelected.forEach(function (c) { new El('button', { 'class': 'cj-tag-rm', 'data-x': c }, b); });
            new El('button', { id: 'cj-add-btn', 'class': 'cj-add' }, b); }); };
          cjRender();
          function retirer(i) { var bs = boite.querySelectorAll('.cj-tag-rm'); if (i >= 0) bs[i].focus();
            else document.activeElement = document.body; cjRemove(bs[Math.max(i, 0)].attrs['data-x']); return decrire(document.activeElement); }
          var out = { temoin: null };
          out.milieu = retirer(1); out.dernier = retirer(1); out.seul = retirer(0);
          cjSelected = ['FR', 'DE']; cjRender(); out.temoin = retirer(-1);
          out.attendu = ['BUTTON[IT]', 'BUTTON[FR]', 'BUTTON#cj-add-btn', 'BODY'];
        """
    elif site == "evaluations":
        code = _tranche("function cpEvalQuoi(e){", "\n}\n") + "\n}\n" \
            + _tranche("function cpEvalAttr(v){", "\n}\n") + "\n}\n" \
            + _tranche("function cpEvalFmtDate(iso){", "\n}\n") + "\n}\n" \
            if "function cpEvalQuoi(e){" in PAGE_JS else ""
        code += _tranche("window.cpEvalRemove = function(id){")
        scen = """
          var boite = new El('div', { id: 'evals-rows' }, document.body);
          var LISTE = [1, 2, 3].map(function (i) { return { id: i, title: 'Éval ' + i, date: '2026-09-0' + i + 'T10:00:00Z' }; });
          global.confirm = function () { return true; };
          global.cpEvalGetAll = function () { return LISTE.slice(); };
          global.cpEvalSetAll = function (l) { LISTE = l; };
          global.cpEvalUpdateBadge = function () {};
          global.cpEvalRenderList = function () { repeindre(boite, function (b) {
            if (!LISTE.length) { new El('a', { href: '#', 'data-x': 'vide' }, b); return; }
            LISTE.forEach(function (e) { new El('button', { 'class': 'suppr-x', 'data-x': String(e.id) }, b); }); }); };
          cpEvalRenderList();
          function retirer(i) { var bs = boite.querySelectorAll('.suppr-x'); if (i >= 0) bs[i].focus();
            else document.activeElement = document.body; cpEvalRemove(+bs[Math.max(i, 0)].attrs['data-x']); return decrire(document.activeElement); }
          var out = {};
          out.milieu = retirer(1); out.dernier = retirer(1); out.seul = retirer(0);
          LISTE = [{ id: 8, title: 'x', date: '2026-09-01T10:00:00Z' }, { id: 9, title: 'y', date: '2026-09-01T10:00:00Z' }];
          cpEvalRenderList(); out.temoin = retirer(-1);
          out.attendu = ['BUTTON[3]', 'BUTTON[1]', 'A[vide]', 'BODY'];
        """
    else:
        code = _tranche("window.regDelete = function(id){")
        scen = """
          var boite = new El('div', { id: 'reg-sys-body' }, document.body);
          global.REG_DATA = [{ id: 1 }, { id: 2 }, { id: 3 }];
          global.confirm = function () { return true; };
          global.alert = function (m) { throw new Error('alerte : ' + m); };
          global.regCloseModal = function () {}; window.sentRegistreOublier = function () {};
          global.fetch = function () { return Promise.resolve({ status: 200, json: function () { return Promise.resolve({}); } }); };
          global.regRender = function () { repeindre(boite, function (b) {
            if (!REG_DATA.length) { new El('a', { href: '#', 'data-x': 'vide' }, b); return; }
            REG_DATA.forEach(function (s) { new El('button', { 'class': 'rs-del', 'data-x': String(s.id) }, b); }); }); };
          regRender();
          var attendre = function () { return new Promise(function (r) { setTimeout(r, 20); }); };
          async function retirer(i) { var bs = boite.querySelectorAll('.rs-del'); if (i >= 0) bs[i].focus();
            else document.activeElement = document.body; regDelete(+bs[Math.max(i, 0)].attrs['data-x']); await attendre(); return decrire(document.activeElement); }
          var out = {};
        """
        code += "\n"
        scen_fin = """
          (async function () {
            out.milieu = await retirer(1); out.dernier = await retirer(1); out.seul = await retirer(0);
            REG_DATA = [{ id: 8 }, { id: 9 }]; regRender(); out.temoin = await retirer(-1);
            out.attendu = ['BUTTON[3]', 'BUTTON[1]', 'A[vide]', 'BODY'];
            process.stdout.write(JSON.stringify(out));
          })().catch(function (e) { process.stderr.write(String(e.stack)); process.exit(3); });
        """
        o = _node(commun + code + scen + scen_fin)
        assert [o["milieu"], o["dernier"], o["seul"], o["temoin"]] == o["attendu"], o
        return
    o = _node(commun + code + scen + "process.stdout.write(JSON.stringify(out));")
    assert [o["milieu"], o["dernier"], o["seul"], o["temoin"]] == o["attendu"], (
        "focus après retrait (milieu, dernier, seul, témoin sans focus) : %s" % o)


def test_le_x_d_une_evaluation_DEMANDE_et_dit_LAQUELLE():
    """EXÉCUTÉ, EN REFUSANT. § 3.5, « suppression × » : c'était la seule des
    suppressions « × » qui effaçait d'une touche (mesuré, revue du lot 3).
    Refusée, rien ne part ; la question dit le titre et la date de
    l'évaluation — pas « celle-ci »."""
    code = ""
    for debut in ("function cpEvalQuoi(e){", "function cpEvalFmtDate(iso){"):
        if debut in PAGE_JS:
            code += _tranche(debut, "\n}\n") + "\n}\n"
    code += _tranche("window.cpEvalRemove = function(id){")
    o = _node("""
      global.window = global;
      var LISTE = [{ id: 7, title: 'Audit de conformité IA Act', date: '2026-09-01T10:00:00Z' }], ecrit = 0, questions = [];
      global.confirm = function (m) { questions.push(String(m)); return false; };
      global.cpEvalGetAll = function () { return LISTE.slice(); };
      global.cpEvalSetAll = function (l) { ecrit++; LISTE = l; };
      global.cpEvalUpdateBadge = function () {}; global.cpEvalRenderList = function () {};
    """ + code + """
      window.cpEvalRemove(7);
      process.stdout.write(JSON.stringify({ questions: questions, ecrit: ecrit, reste: LISTE.length }));
    """)
    assert len(o["questions"]) == 1, "aucune question avant d'effacer : %s" % o
    q = o["questions"][0]
    assert "définitivement" in q and "Audit de conformité IA Act" in q and "01/09/2026" in q, q
    assert o["ecrit"] == 0 and o["reste"] == 1, "refusée, l'évaluation est quand même effacée : %s" % o


def test_le_nom_du_x_d_une_evaluation_dit_LAQUELLE_pas_son_rang():
    """EXÉCUTÉ : la vraie liste peinte. Mesuré (revue du lot 3) : « Supprimer
    l'évaluation 01 » — un RANG, qui passait à la suivante après une
    suppression. Deux évaluations du même titre se distinguent par leur date
    et leur heure ; un guillemet dans un titre ne casse pas l'attribut."""
    code = ""
    for debut in ("function cpEvalQuoi(e){", "function cpEvalAttr(v){", "function cpEvalFmtDate(iso){",
                  "function cpEvalBadgeColor(level){"):
        if debut in PAGE_JS:
            code += _tranche(debut, "\n}\n") + "\n}\n"
    code += _tranche("function cpEvalRenderList(){", "\n}\n") + "\n}\n"
    o = _node("""
      global.window = global;
      const box = { innerHTML: '' };
      global.document = { getElementById: (i) => i === 'evals-rows' ? box : null };
      const E = (id, t, d) => ({ id, title: t, date: d, type: 'audit', score: 50, scoreMax: 100, level: 'haut', badge: 'X', icon: '', subtitle: '' });
      global.cpEvalGetAll = () => [E(1, 'Audit "IA"', '2026-09-01T10:00:00Z'), E(2, 'Audit "IA"', '2026-09-01T15:30:00Z')];
    """ + code + """
      cpEvalRenderList();
      process.stdout.write(JSON.stringify({ h: box.innerHTML }));
    """)
    noms = [n.attrs.get("aria-label", "") for n in _Arbre(o["h"]).tous if n.tag == "button" and "suppr-x" in n.classes()]
    assert len(noms) == 2, o["h"][:300]
    for nom in noms:
        assert 'Audit "IA"' in nom and "01/09/2026" in nom, nom
        assert not re.search(r"évaluation 0\d\b", nom), "le nom dit un rang : « %s »" % nom
    assert noms[0] != noms[1], "deux évaluations, un seul nom : %s" % noms


def _liens_a_glyphe(src):
    out = []
    for m in re.finditer(r"<a\b([^<>]*)>((?:(?!</a>).){0,80}?)</a>", src, re.S):
        t = re.sub(r"\s+", "", _html.unescape(re.sub(r"<[^>]*>", "", m.group(2))))
        if not re.search(r"[A-Za-zÀ-ÿ0-9]{3,}", t):
            out.append((src.count("\n", 0, m.start()) + 1, t, m.group(1)))
    return out


def test_aucun_LIEN_a_glyphe_de_l_accueil_n_est_nomme_par_son_glyphe():
    """« 🌐 » : le lien d'i-aes.com s'appelait ainsi (mesuré au balayage de
    l'arbre d'accessibilité, revue du lot 3) — seul glyphe restant, oublié
    parmi les liens sociaux. La règle des boutons à glyphe ne lisait que les
    <button>."""
    liens = _liens_a_glyphe(ACCUEIL)
    assert len(liens) >= 3, "le relevé ne trouve presque rien : %d" % len(liens)
    sans = ["index.html:%d « %s »" % (l, t) for l, t, attrs in liens
            if not re.search(r'aria-label="[^"]*[A-Za-zÀ-ÿ]{3,}', attrs)]
    assert not sans, "liens nommés par leur glyphe :\n  " + "\n  ".join(sans)


@pytest.mark.parametrize("fichier,quoi", [
    pytest.param("sentinel.html", lambda n: "sb-lbtn" in n.classes(), id="sb-lbtn"),
    pytest.param("sentinel.html", lambda n: "vl-btn" in n.classes() and n.texte().strip() != "ALL", id="vl-btn"),
    pytest.param("index.html", lambda n: n.attrs.get("aria-label") == "Fermer la veille", id="fermer-veille")])
def test_un_title_qui_REDIT_le_nom_autrement_n_ouvre_pas_de_bulle(fichier, quoi):
    """LE CRITÈRE DE /bulle-titre.js (§2.2) : un `title` qui n'égale pas le
    nom est « informatif », et s'ouvre à chaque tabulation. Mesuré (revue du
    lot 3) : « Afficher Sentinel en français » pour un bouton « FR —
    français », « Fermer » pour « Fermer la veille » — une bulle pour redire,
    autrement ou en moins, ce que le nom dit déjà."""
    bs = [n for n in _arbre(fichier).tous if n.tag == "button" and quoi(n)]
    assert bs, "aucun bouton visé"
    fautes = ["« %s » / nom « %s »" % (b.attrs.get("title"), b.attrs.get("aria-label")) for b in bs
              if b.attrs.get("title") and _apprend_quelque_chose(b.attrs["title"], b.attrs.get("aria-label") or b.texte())]
    assert not fautes, "\n".join(fautes)
