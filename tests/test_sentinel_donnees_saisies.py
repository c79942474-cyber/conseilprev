# -*- coding: utf-8 -*-
"""UNE DONNÉE SAISIE N'EST PAS DU FRANÇAIS À TRADUIRE — le marquage dans
sentinel.page.js, la mesure qui la compte à part, et le seuil qui tient.

CE QUE LA MESURE NAVIGATEUR A MONTRÉ, ET QUI A FAIT ÉCRIRE CES RÈGLES. La
recette annonçait « PART FRANÇAISE GLOBALE : 25,1 % » alors que la traduction
était faite. Le relevé brut le dit : sur 70 061 mots français comptés à
l'écran (occurrences comprises), 57 255 — 82 % — étaient des ENTRÉES DU
REGISTRE. « Recette — la décision écrit », « Regression logistique /
XGBoost », « Chatbot service client » : des noms de systèmes, des
fournisseurs, des finalités, que le registre, la matrice, l'empreinte, le
FinOps et la qualification assistée réaffichent des milliers de fois. En
production, ce sont les systèmes d'IA du client, écrits dans SA langue. Les
compter comme « du français qui reste à traduire » est faux par
construction, et rendait tout seuil inatteignable.

LES TROIS CHOSES QUE CES RÈGLES MESURENT :

  1. LE MARQUAGE À LA SOURCE. Chaque valeur saisie affichée passe par
     `sentDonnee()`, qui l'échappe et l'enveloppe dans un élément
     translate="no" ; un attribut entièrement fait d'une donnée est porté par
     un élément marqué (SENT_ATTR_DONNEE). Le VRAI moteur (sentinel.i18n.js)
     est exécuté sur le HTML ainsi produit : la donnée reste intacte, la
     phrase autour est traduite.

  2. LA MESURE QUI SÉPARE. outils/sentinel_langue.js relève les textes
     marqués À PART, les tient HORS du verdict, et dit leur volume — tandis
     que les cadres, qui se traduisent désormais eux-mêmes, ENTRENT dans le
     verdict. Le module réel est exécuté sous node.

  3. LE SEUIL TENU. i18n/sentinel/SEUIL porte la part française promise ;
     i18n/sentinel/MESURE_APRES.json porte la part mesurée. La seconde ne
     doit pas dépasser la première — c'est la promesse, relue à chaque
     passage de la suite, sans navigateur.

CE QUI N'EST PAS MARQUÉ, ET POURQUOI. Les libellés composés portés par un
title ou un aria-label (« Supprimer <nom> du registre ») ne sont PAS exclus :
un attribut ne porte pas de balise, on ne peut pas y marquer la seule partie
variable, et les motifs du dictionnaire traduisent la phrase en recopiant la
donnée. Les exclure laisserait la phrase entière en français. Une règle le
garde explicitement.
"""
import functools
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import pytest

_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE = shutil.which("node")
MODULE_I18N = os.path.join(_RACINE, "sentinel.i18n.js")
MODULE_LANGUE = os.path.join(_RACINE, "outils", "sentinel_langue.js")
HARNAIS = os.path.join(_RACINE, "tests", "_dom_sentinel_corps.js")
DOSSIER_I18N = os.path.join(_RACINE, "i18n", "sentinel")
SEUIL = os.path.join(DOSSIER_I18N, "SEUIL")
MESURE_APRES = os.path.join(DOSSIER_I18N, "MESURE_APRES.json")


def _lire(nom):
    return io.open(os.path.join(_RACINE, nom), encoding="utf-8").read()


PAGE_JS = _lire("sentinel.page.js")
RECETTE = _lire("recette_sentinel_langue.js")


def _ids(cas):
    import unicodedata
    out = []
    for c in cas:
        s = unicodedata.normalize("NFKD", c[0]).encode("ascii", "ignore").decode()
        out.append(re.sub(r"-+", "-", re.sub(r"[^A-Za-z0-9]+", "-", s)).strip("-")[:48])
    return out


# ══════════════════════════════════════════════════════════════════════════
#  LE HARNAIS — le VRAI sentDonnee de sentinel.page.js, sous node
# ══════════════════════════════════════════════════════════════════════════
#
# sentinel.page.js ne se charge pas sous node : il peint un document dès sa
# lecture. Les deux fonctions du marquage en sont donc DÉCOUPÉES À LA SOURCE
# et exécutées telles quelles — pas une copie réécrite ici, qui pourrait
# rester juste pendant que le produit dérive.

_DECOUPE = re.compile(
    r"(function sentDonneeEch\(v\) \{.*?\n\}\n).*?(function sentDonnee\(v\) \{.*?\n\}\n)",
    re.S)


def source_du_marquage():
    m = _DECOUPE.search(PAGE_JS)
    assert m, ("sentinel.page.js ne définit plus sentDonneeEch / sentDonnee : "
               "les valeurs saisies ne sont plus marquées à la source")
    return m.group(1) + m.group(2)


def _node(programme, *fichiers):
    if not NODE:
        pytest.skip("node absent : le code ne peut pas être exécuté")
    r = subprocess.run([NODE, "-e", programme] + list(fichiers),
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, "node n'a pas tourné :\n%s" % (r.stderr or "")[-2000:]
    return json.loads(r.stdout)


def marquer(*valeurs):
    """Le VRAI sentDonnee, appliqué à chaque valeur."""
    prog = (source_du_marquage()
            + "const vs = JSON.parse(process.argv[1]);\n"
            + "process.stdout.write(JSON.stringify(vs.map(sentDonnee)));\n")
    return _node(prog, json.dumps(list(valeurs), ensure_ascii=False))


@functools.lru_cache(maxsize=None)
def _jouer_json(programme):
    if not NODE:
        pytest.skip("node absent")
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "prog.json")
        io.open(p, "w", encoding="utf-8").write(programme)
        r = subprocess.run([NODE, HARNAIS, MODULE_I18N, p],
                           capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, "le module n'a pas tourné :\n%s" % (r.stderr or "")[-2000:]
    return r.stdout


def jouer(html, ops, dico=None):
    out = json.loads(_jouer_json(json.dumps(
        {"html": html, "dico": dico or {"texte": {}, "bloc": {}}, "ops": ops},
        ensure_ascii=False, sort_keys=True)))
    for i, r in enumerate(out):
        assert not (isinstance(r, dict) and "erreur" in r), (
            "l'opération %d (%s) a levé : %s" % (i, ops[i]["op"], r["erreur"][:600]))
    return out


def langue(*appels):
    prog = ("const M = require(process.argv[1]);\n"
            "const p = JSON.parse(process.argv[2]);\n"
            "process.stdout.write(JSON.stringify(p.map(([f, a]) => M[f].apply(null, a))));\n")
    return _node(prog, MODULE_LANGUE, json.dumps(list(appels), ensure_ascii=False))


# ══════════════════════════════════════════════════════════════════════════
#  1. LE MARQUAGE — sentDonnee pose translate="no" et échappe
# ══════════════════════════════════════════════════════════════════════════

CAS_MARQUAGE = [
    ("nom de système ordinaire", u"Chatbot service client",
     u'<span translate="no">Chatbot service client</span>'),
    ("chevrons et esperluette", u'Scoring <IA> & "crédit"',
     u'<span translate="no">Scoring &lt;IA&gt; &amp; &quot;crédit&quot;</span>'),
    ("apostrophe", u"L'octroi de crédit",
     u'<span translate="no">L&#39;octroi de crédit</span>'),
    ("valeur absente", None, u'<span translate="no"></span>'),
]


@pytest.mark.parametrize("nom,valeur,attendu", CAS_MARQUAGE, ids=_ids(CAS_MARQUAGE))
def test_une_valeur_saisie_est_echappee_ET_declaree_donnee(nom, valeur, attendu):
    """L'échappement et la déclaration vont ensemble : marquer sans échapper
    ouvrirait une injection là où le code écrivait `ech(...)` avant."""
    assert marquer(valeur) == [attendu]


def test_le_moteur_laisse_la_donnee_INTACTE_et_traduit_la_phrase_autour():
    """LA RÈGLE QUI DIT TOUT LE SUJET, jouée sur le VRAI moteur : la cellule
    garde le nom du système tel qu'il a été saisi, et la phrase qui l'encadre
    passe en anglais."""
    nom = marquer(u"Détection de fraude")[0]
    html = (u'<div id="c"><span>Système : </span>' + nom
            + u'<span> — non instruit</span></div>')
    dico = {"texte": {u"Système :": u"System:", u"— non instruit": u"— not costed"},
            "bloc": {}}
    r = jouer(html, [{"op": "traduire", "sel": "#c", "langue": "en"},
                     {"op": "texte", "sel": "#c"}], dico)
    assert r[1] == u"System: Détection de fraude — not costed".replace(u" ", u" "), r[1]


def test_un_attribut_entierement_fait_d_une_donnee_est_porte_par_un_element_marque():
    """« <nom> — <secteur> » en title : rien à traduire dedans. Un attribut ne
    porte pas de balise, c'est donc l'élément qui se déclare donnée — et le
    moteur ne le touche pas plus que son contenu."""
    assert u"var SENT_ATTR_DONNEE = ' translate=\"no\"';" in PAGE_JS, (
        u"SENT_ATTR_DONNEE a disparu de sentinel.page.js")
    html = (u'<div id="c"><div class="matrix-dot" translate="no" '
            u'title="Détection de fraude — Finance">x</div></div>')
    dico = {"texte": {u"Détection de fraude — Finance": u"Fraud detection — Finance"}, "bloc": {}}
    r = jouer(html, [{"op": "traduire", "sel": "#c", "langue": "en"},
                     {"op": "attr", "sel": ".matrix-dot", "nom": "title"}], dico)
    assert r[0] == 0, u"le moteur a écrit %d fois dans une donnée" % r[0]
    assert r[1] == u"Détection de fraude — Finance", r[1]


# ══════════════════════════════════════════════════════════════════════════
#  2. CHAQUE VALEUR SAISIE AFFICHÉE EST MARQUÉE — sentinel.page.js
# ══════════════════════════════════════════════════════════════════════════
#
# Un extrait par écran, pris tel qu'il s'écrit dans le fichier : la valeur y
# est marquée, et le libellé d'interface autour ne l'est pas. Une ligne
# remise en clair fait tomber la règle de son écran.

CAS_SOURCE = [
    ("registre — nom du système",
     u"""'<div><div class="rs-name">'+sentDonnee(s.nom)+pctBadge+'</div>"""),
    ("registre — type et secteur",
     u"""'<div><span class="chip chip-b">'+(s.secteur?sentDonnee(s.secteur):"—")+'</span></div>'"""),
    ("registre — titre de la modale",
     u"""'<div class="mat-modal-title">'+(sys?sentDonnee(sys.nom):"Ajouter au registre")+'</div>"""),
    ("matrice — le title d'une pastille",
     u"""'<div class="matrix-dot"' + SENT_ATTR_DONNEE + ' title="'+sentDonneeEch(s.nom)+' — '+sentDonneeEch(s.secteur||'')+'"""),
    ("matrice — la liste critique",
     u"""'<div class="eval-body"><div class="eval-n">'+sentDonnee(s.nom)+'</div>"""),
    ("empreinte IA — les systèmes sans volume",
     u"""c.volume_manquant.map(sentDonnee).join(', ')"""),
    ("empreinte IA — le tableau ligne à ligne",
     u"""'<td style="padding:6px 8px"><strong>' + sentDonnee(l.nom) + '</strong></td>'"""),
    ("finops — fournisseur nommé, modèle non déclaré",
     u"""sentDonnee(x.nom) + '</b> — fournisseur « '\n                   + sentDonnee(x.fournisseur)"""),
    ("finops — le détail ligne à ligne",
     u"""'<tr><td>' + sentDonnee(l.nom) + '</td><td>'\n                   + (l.modele ? sentDonnee(l.modele)"""),
    ("finops — l'attribution par centre de coût",
     u"""'<tr><td>' + sentDonnee(x.cle) + '</td><td>' + x.systemes"""),
    ("fria — la carte d'un système",
     u"""<div class="fria-sys-name">'+sentDonnee(systeme.nom)+'</div>"""),
    ("clients — raison sociale et courriel",
     u"""<div class="rs-name">' + sentDonnee(c.nom_entreprise) + '</div><div class="rs-type">' + sentDonnee(c.email)"""),
    ("qualification assistée — le nom du système",
     u"""(p.systeme_nom ? sentDonnee(p.systeme_nom) : qualifEsc('système #' + p.systeme_id))"""),
    ("qualification assistée — les citations de la déclaration",
     u"""p.indices.map(function (i) { return '<li>« ' + sentDonnee(i) + ' »</li>'; })"""),
]


@pytest.mark.parametrize("nom,extrait", CAS_SOURCE, ids=_ids(CAS_SOURCE))
def test_chaque_valeur_saisie_affichee_est_marquee_donnee(nom, extrait):
    assert extrait in PAGE_JS, (
        u"l'écran « %s » n'écrit plus sa valeur saisie par sentDonnee : "
        u"elle repartira dans la part française et le seuil ne tiendra plus.\n"
        u"attendu :\n%s" % (nom, extrait))


def test_les_libelles_composes_en_attribut_restent_traduits_par_les_motifs():
    """« Supprimer <nom> du registre » NE DOIT PAS être exclu : un attribut ne
    porte pas de balise, l'exclure laisserait la phrase entière en français.
    C'est le motif du dictionnaire qui la traduit en recopiant la donnée."""
    assert u"""aria-label="Supprimer '+regAttr(s.nom)+' du registre" title="Supprimer '+regAttr(s.nom)+' du registre\"""" in PAGE_JS
    assert u"""class="rs-del"' + SENT_ATTR_DONNEE""" not in PAGE_JS
    html = (u'<div id="c"><button class="rs-del" aria-label="Supprimer Détection de fraude du registre">'
            u'×</button></div>')
    dico = {"texte": {}, "bloc": {},
            "motif": {u"Supprimer {} du registre": u"Delete {} from the register"}}
    r = jouer(html, [{"op": "traduire", "sel": "#c", "langue": "en"},
                     {"op": "attr", "sel": ".rs-del", "nom": "aria-label"}], dico)
    assert r[1] == u"Delete Détection de fraude from the register", r[1]


# ══════════════════════════════════════════════════════════════════════════
#  3. LA MESURE — données à part et hors verdict, cadres dans le verdict
# ══════════════════════════════════════════════════════════════════════════

RELEVES = {
    "pages": {
        "registre": [
            {"t": u"Aucun système trouvé.", "ou": "texte"},                    # fr, 3 mots
            {"t": u"Chatbot service client français", "ou": "donnee:texte"},   # donnée, 4 mots
            {"t": u"Regression logistique", "ou": "donnee:texte"},             # donnée, 2 mots
            {"t": u"Fraud detection on transactions", "ou": "texte"},          # en, 4 mots
        ],
        "pan-sia": [
            {"t": u"Le panorama complet des cas", "ou": "cadre:texte"},        # cadre, fr, 5 mots
            {"t": u"Loading the map", "ou": "cadre:texte"},                    # cadre, en, 3 mots
            {"t": u"Détection de fraude", "ou": "cadre:donnee:texte"},         # donnée DANS un cadre
        ],
    },
    "coquille": [{"t": u"Steering", "ou": "texte"}],
}


def _agreger():
    return langue(["agreger", [RELEVES, {"base": "http://x", "date": "2026-09-25T00:00:00Z"}]])[0]


def test_les_donnees_saisies_sont_relevees_A_PART_et_hors_verdict():
    """LA RÈGLE QUI PORTE TOUTE LA MESURE : un nom de système ne compte pas
    comme « du français qui reste à traduire »."""
    m = _agreger()
    assert "donnees" in m, sorted(m)
    p = m["pages"]["registre"]
    assert (p["mots_fr"], p["mots_en"]) == (3, 4), p
    assert p["donnees"]["mots_fr"] == 6, p["donnees"]
    assert m["donnees"]["mots_fr"] == 9, m["donnees"]     # 6 au registre + 3 dans le cadre
    assert m["donnees"]["pages"] == 2, m["donnees"]


def test_le_volume_des_donnees_ecartees_est_DIT_dans_le_resume():
    """Une part qui tombe parce qu'on a cessé de compter doit pouvoir se
    relire : sans cette ligne, on croirait ces mots disparus."""
    r = langue(["resumer", [_agreger(), 0.05]])[0]
    assert u"données (saisies, hors verdict) : 9 mots fr" in r, r


def test_les_cadres_ENTRENT_desormais_dans_le_verdict_et_restent_dits_a_part():
    """Depuis qu'ils chargent sentinel.i18n.js, les cadres se traduisent par
    la même mécanique que Sentinel : les tenir hors du verdict reviendrait à
    ne pas regarder un cinquième de ce qu'un lecteur voit."""
    m = _agreger()
    p = m["pages"]["pan-sia"]
    assert (p["mots_fr"], p["mots_en"]) == (5, 3), p
    assert p["cadres"]["mots_fr"] == 5, p["cadres"]
    assert m["cadres"]["pages"] == 1 and m["cadres"]["mots_fr"] == 5, m["cadres"]
    # global = registre (3 fr / 4 en) + pan-sia (5 fr / 3 en) + coquille (0 / 1)
    assert (m["global"]["mots_fr"], m["global"]["mots_en"]) == (8, 8), m["global"]
    assert u"cadres (iframes, COMPRIS dans le verdict)" in langue(["resumer", [m, 0.05]])[0]


def test_une_donnee_dans_un_cadre_est_une_donnee_d_abord():
    """Elle ne se traduit pas plus là qu'ailleurs : la ranger dans les cadres
    la ferait rentrer dans le verdict par la bande."""
    t = langue(["trier", [RELEVES["pages"]["pan-sia"]]])[0]
    assert len(t["donnees"]) == 1 and len(t["cadres"]) == 2 and len(t["verdict"]) == 2, t


def test_le_releve_navigateur_marque_ce_qui_est_sous_translate_no():
    """C'est le relevé qui pose le marqueur ; sans lui, l'agrégation n'a rien
    à séparer. La règle lit le code de la recette, que seul un navigateur
    peut exécuter."""
    assert u"el.getAttribute('translate') === 'no'" in RECETTE, RECETTE[:0]
    assert u"prefixe = prefixe + 'donnee:';" in RECETTE


# ══════════════════════════════════════════════════════════════════════════
#  4. LE SEUIL — la promesse écrite, et la mesure qui la tient
# ══════════════════════════════════════════════════════════════════════════


def _seuil():
    valeurs = []
    for ligne in io.open(SEUIL, encoding="utf-8"):
        ligne = ligne.split("#")[0].strip().replace(",", ".")
        if ligne:
            valeurs.append(ligne)
    assert len(valeurs) == 1, u"i18n/sentinel/SEUIL doit porter UNE valeur, lu : %r" % valeurs
    v = float(valeurs[0])
    assert 0.0 <= v <= 1.0, v
    return v


def test_le_SEUIL_porte_la_part_francaise_promise_et_rien_d_autre():
    assert os.path.isfile(SEUIL), "i18n/sentinel/SEUIL manque"
    assert _seuil() <= 0.20, (
        u"un seuil aussi haut ne promet plus rien : la part française mesurée "
        u"était de 25,1 %% avant ce lot")


def test_la_part_francaise_MESUREE_ne_depasse_pas_le_SEUIL():
    """LA PROMESSE, RELUE SANS NAVIGATEUR. La recette écrit ce qu'elle a vu
    dans MESURE_APRES.json ; cette règle vérifie que ce qu'elle a vu tient
    dans ce que le dépôt promet. Le jour où une page revient en français, la
    mesure remonte et cette règle tombe."""
    assert os.path.isfile(MESURE_APRES), "i18n/sentinel/MESURE_APRES.json manque"
    m = json.load(io.open(MESURE_APRES, encoding="utf-8"))
    part = m["global"]["part_fr"]
    assert part is not None, m["global"]
    assert part <= _seuil(), (
        u"part française mesurée %.2f %% > seuil promis %.2f %% — "
        u"les pages les plus françaises : %s"
        % (part * 100, _seuil() * 100,
           ", ".join("%s (%.0f %%)" % (k, (v["part_fr"] or 0) * 100)
                     for k, v in sorted(m["pages"].items(),
                                        key=lambda kv: -(kv[1]["part_fr"] or 0))[:5])))


def test_la_mesure_commitee_separe_bien_les_donnees_du_texte_de_site():
    """Une mesure d'avant le partage ferait tenir le seuil pour une raison
    qui n'est pas la bonne : elle n'aurait simplement rien écarté."""
    m = json.load(io.open(MESURE_APRES, encoding="utf-8"))
    assert "donnees" in m, sorted(m)
    assert m["donnees"]["mots_fr"] > 10000, (
        u"les données saisies pèsent %s mots français : le marquage n'a pas "
        u"pris" % m["donnees"]["mots_fr"])
    assert m["dictionnaire"]["charge"] is True, m["dictionnaire"]
    assert m.get("pages_429") == [], m.get("pages_429")
    assert len(m["pages"]) == 118, len(m["pages"])
