# -*- coding: utf-8 -*-
"""LA NACE RÉV. 2.1 — ET L'ERREUR QUE LA SOURCE A ÉVITÉE.

CE QUI A DÉCLENCHÉ CE FICHIER. Une demande simple : « ajouter des secteurs
d'activité correspondant au classement NACE international ». Écrire cette table
de mémoire aurait produit vingt et une sections A à U, la finance en K et
l'informatique en J. C'EST LA RÉVISION 2, ET ELLE N'EST PLUS EN VIGUEUR.

La révision 2.1, applicable depuis le 1er janvier 2025, compte VINGT-DEUX
sections A à V et redistribue les lettres à partir de G : l'informatique et les
télécommunications forment K, la finance passe en L, l'immobilier en M,
l'enseignement en Q, la santé en R. Une table écrite de mémoire aurait donc été
fausse à partir de sa septième ligne — et d'autant plus crédible qu'elle aurait
été complète, puisque « K » désigne bien une section dans les deux révisions.
Simplement pas la même.

CE QUE CES RÈGLES GARDENT
  · que les vingt-deux sections soient A à V, dans l'ordre — le contrôle qui
    aurait attrapé l'erreur ;
  · que l'intitulé OFFICIEL reste la reprise verbatim de l'annexe, et que la
    traduction française ne soit jamais présentée comme officielle ;
  · qu'AUCUN profil ne soit inventé pour les treize sections que les huit
    profils relevés de Sentinel ne couvrent pas ;
  · que le sélecteur, EXÉCUTÉ, dise à l'écran ce que le module dit dans sa
    structure — un premier jet peignait un bloc d'explication vide pour ces
    treize sections-là, et rien ne le signalait.

CE QU'ELLES NE PEUVENT PAS FAIRE. Vérifier que la correspondance entre les huit
profils Sentinel et les sections est la bonne : c'est un jugement de périmètre,
pas un fait publié. Ni relire la source — la suite n'ouvre aucune socket ;
`outils/recette_nace.py` le fait, à la main, depuis un réseau qui la joint.
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

import secteurs_nace as N                                          # noqa: E402

PAGE = io.open(os.path.join(ICI, "sentinel.html"), encoding="utf-8").read()
MOTEUR = io.open(os.path.join(ICI, "sentinel.page.js"), encoding="utf-8").read()
SOURCE = io.open(os.path.join(ICI, "app.py"), encoding="utf-8").read()
NODE = shutil.which("node")


# ═══════════════════════════════════════════════════════════════════════════
#  1. LA RÉVISION — LE CONTRÔLE QUI AURAIT ATTRAPÉ L'ERREUR
# ═══════════════════════════════════════════════════════════════════════════

def test_LA_REVISION_les_sections_vont_de_A_a_V_et_non_de_A_a_U():
    """VINGT-DEUX, PAS VINGT ET UNE. La Rév. 2 s'arrêtait à U ; la Rév. 2.1
    crée V pour les organismes extraterritoriaux et décale tout le reste."""
    codes = [s["code"] for s in N.SECTIONS]
    assert codes == [chr(c) for c in range(ord("A"), ord("V") + 1)], codes
    assert len(N.SECTIONS) == 22


@pytest.mark.parametrize("code,attendu", [
    ("K", "élécommunication"),     # Rév. 2 : activités financières
    ("L", "financières"),          # Rév. 2 : activités immobilières
    ("M", "immobilières"),         # Rév. 2 : activités spécialisées
    ("Q", "Enseignement"),         # Rév. 2 : santé humaine
    ("R", "Santé"),                # Rév. 2 : arts et spectacles
    ("V", "extraterritoriaux"),    # Rév. 2 : n'existe pas
])
def test_les_lettres_deplacees_par_la_revision_2_1_sont_les_bonnes(code, attendu):
    """LES SIX LETTRES OÙ UNE TABLE ÉCRITE DE MÉMOIRE SE TROMPE. Une règle qui
    se contenterait de compter vingt-deux sections serait verte sur une table
    dont chaque lettre à partir de G désignerait la mauvaise activité."""
    assert attendu in N.section(code)["intitule"], (
        "la section %s porte « %s » — est-ce la Rév. 2 ?"
        % (code, N.section(code)["intitule"]))


def test_chaque_lettre_deplacee_dit_ce_qu_elle_designait_avant():
    """Un lecteur qui connaît la Rév. 2 croirait à une erreur devant « L —
    activités financières ». Le lui dire coûte une ligne ; ne pas le dire coûte
    sa confiance dans tout le reste du tableau."""
    for code in ("J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V"):
        note = N.DEPLACEMENTS_DEPUIS_REV2.get(code)
        assert note and "Rév. 2" in note, code


# ═══════════════════════════════════════════════════════════════════════════
#  2. LA SOURCE, ET CE QU'ELLE NE COUVRE PAS
# ═══════════════════════════════════════════════════════════════════════════

def test_la_source_est_nommee_datee_et_joignable():
    for cle in ("acte", "celex", "journal", "url", "revision",
                "applicable_depuis", "consulte_le"):
        assert str(N.SOURCE.get(cle) or "").strip(), cle
    assert N.SOURCE["celex"] == "32023R0137"
    assert N.SOURCE["celex"] in N.SOURCE["url"]


def test_LA_TRADUCTION_N_EST_JAMAIS_PRESENTEE_COMME_OFFICIELLE():
    """La version consultée est l'anglaise. Un intitulé traduit ici et présenté
    comme celui du règlement est l'erreur qu'on ne repère plus jamais : elle a
    l'air d'une source. La réserve doit dire les deux choses — quelle version a
    été lue, et que le français est une traduction de travail."""
    reserve = N.SOURCE["reserve"]
    assert "ANGLAISE" in reserve or "anglaise" in reserve
    assert "traduction de travail" in reserve
    assert N.SOURCE["version_consultee"] == "anglaise"
    assert "recette_nace" in reserve, (
        "la réserve ne dit pas comment lever le doute — une réserve sans "
        "remède devient une excuse permanente")


def test_l_intitule_officiel_reste_la_reprise_verbatim_de_l_annexe():
    """L'annexe est en capitales. Un intitulé « rendu plus joli » n'est plus
    une reprise, et la recette qui compare à la source tomberait sans qu'on
    sache si c'est le règlement ou nous qui avons bougé."""
    for s in N.SECTIONS:
        assert s["intitule_officiel"] == s["intitule_officiel"].upper(), s["code"]
        assert s["intitule"] != s["intitule_officiel"], (
            "%s : l'intitulé français n'est pas traduit" % s["code"])


def test_aucune_regle_de_la_suite_n_ouvre_de_socket_vers_la_source():
    """Un contrôle qui dépend du réseau rougit les jours où le réseau bouge, et
    une suite qui rougit pour une raison extérieure finit par ne plus être lue.
    La revérification vit donc dans `outils/`."""
    # L'HÔTE EST DÉDUIT DE LA SOURCE, JAMAIS ÉCRIT ICI. Écrit en clair, il
    # ferait tomber la règle SUR ELLE-MÊME : le fichier qui interdit une
    # adresse la contient. Le déduire lève l'auto-référence sans exemption, et
    # suit la source si elle change d'hôte.
    hote = N.SOURCE["url"].split("/")[2]
    # CE QUI SE MESURE EST L'ADRESSE, PAS LE NOM DE LA FONCTION. Un premier
    # jet interdisait « urlopen » et tombait sur `test_dcwatch_import`, qui
    # l'emploie pour prouver que l'import n'ouvre AUCUNE socket — une règle
    # rouge pour l'exact contraire de ce qu'elle voulait interdire.
    for fichier in os.listdir(os.path.join(ICI, "tests")):
        if not fichier.endswith(".py"):
            continue
        texte = io.open(os.path.join(ICI, "tests", fichier),
                        encoding="utf-8").read()
        assert hote not in texte, (
            "%s va chercher la source : la suite dépendrait du réseau" % fichier)


def _recette():
    """La recette, chargée comme module — pour l'exécuter, pas pour la lire."""
    import importlib.util
    chemin = os.path.join(ICI, "outils", "recette_nace.py")
    assert os.path.exists(chemin), "la recette de revérification a disparu"
    spec = importlib.util.spec_from_file_location("recette_nace_sous_test", chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fausse_annexe(sections):
    """L'annexe telle que la source la publie — en capitales, avec le tiret."""
    corps = " ".join("<p>SECTION %s – %s</p>" % (s["code"], s["intitule_officiel"])
                     for s in sections)
    return ("<html><body>" + corps + "</body></html>").encode("utf-8")


def test_LA_RECETTE_COMPARE_VRAIMENT_verte_sur_la_source_rouge_sur_un_ecart(monkeypatch):
    """UNE RÈGLE QUI CHERCHAIT DEUX CHAÎNES DANS LE FICHIER A LAISSÉ PASSER UNE
    MUTATION qui renommait la table des adresses : la recette ne relevait plus
    rien et le fichier contenait toujours « urllib » et le numéro CELEX. Elle
    est donc EXÉCUTÉE, contre une fausse annexe servie sur place — la seule
    façon de prouver qu'elle compare, et sans ouvrir de socket."""
    import urllib.request
    recette = _recette()

    class _Reponse(object):
        def __init__(self, corps): self._corps = corps
        def read(self): return self._corps
        def __enter__(self): return self
        def __exit__(self, *a): return False

    # 1. Servie à l'identique, la recette ne relève AUCUN écart.
    monkeypatch.setattr(urllib.request, "urlopen",
                        lambda *a, **k: _Reponse(_fausse_annexe(N.SECTIONS)))
    assert recette.main() == 0, (
        "la recette signale un écart alors que la source servie est identique "
        "au référentiel : elle ne compare pas ce qu'elle prétend")

    # 2. Un seul intitulé changé à la source, et elle le voit.
    abime = [dict(x) for x in N.SECTIONS]
    abime[5]["intitule_officiel"] = "BUILDING WORKS"
    monkeypatch.setattr(urllib.request, "urlopen",
                        lambda *a, **k: _Reponse(_fausse_annexe(abime)))
    assert recette.main() == 1, (
        "la source publie un autre intitulé pour la section F et la recette "
        "ne le signale pas")


# ═══════════════════════════════════════════════════════════════════════════
#  3. AUCUN PROFIL N'EST INVENTÉ
# ═══════════════════════════════════════════════════════════════════════════

def _parcourir(objet, cle=None):
    """Toutes les paires (clé, valeur) d'une structure imbriquée."""
    if isinstance(objet, dict):
        for k, v in objet.items():
            for paire in _parcourir(v, k):
                yield paire
    elif isinstance(objet, (list, tuple)):
        for v in objet:
            for paire in _parcourir(v, cle):
                yield paire
    else:
        yield cle, objet


def test_LE_POINT_QUI_DECIDE_aucune_section_sans_profil_n_en_recoit_un():
    """Fabriquer un socle de piliers, un budget et une durée pour les treize
    sections non couvertes donnerait vingt-deux entrées d'apparence homogène
    dont neuf seraient relevées et treize devinées — et rien, à l'écran, ne
    permettrait de les distinguer. La règle exige que ces treize sortent
    VIDES de profil, et qu'elles disent pourquoi."""
    c = N.couverture()
    assert c["total"] == 22 and c["avec_profil"] == 9 and c["sans_profil"] == 13
    for code in c["codes_sans_profil"]:
        r = N.choisir(code)
        assert r["profils"] == [], code
        assert r["motif"] and "aucun profil" in r["motif"], code
        # LA RÈGLE MESURE LES CLÉS ET LES VALEURS, PAS LES MOTS. Un premier jet
        # cherchait « budget » dans le JSON entier et tombait sur la PROSE qui
        # explique qu'il n'y en a pas — une règle rouge pour une raison sans
        # rapport avec ce qu'elle prétendait mesurer. Ce qui se mesure est
        # qu'aucune clé de profil n'existe, et qu'AUCUN NOMBRE ne traverse :
        # un socle, un budget ou une durée inventés seraient forcément
        # numériques.
        for cle, valeur in _parcourir(r):
            assert cle not in ("pillars", "budget", "duree", "specifics",
                               "systems", "regs"), (code, cle)
            assert not isinstance(valeur, (int, float)) or isinstance(valeur, bool), (
                "%s : la section porte une valeur chiffrée (%s = %r) alors "
                "qu'aucun profil n'est relevé pour elle" % (code, cle, valeur))


def test_une_section_sans_profil_ne_recoit_pas_un_repli_choisi_a_sa_place():
    """« Le moins faux » est un arbitrage qui appartient au client. Le faire
    ici, en silence, donnerait un audit assis sur un secteur qu'il n'a pas
    choisi — et l'export en garderait la trace comme d'une décision."""
    for code in N.couverture()["codes_sans_profil"]:
        assert not N.choisir(code)["profils"], code


def test_ce_qui_manque_pour_etablir_un_profil_est_ecrit_et_non_promis():
    """Écrit dans le module, servi à l'écran : c'est la seule forme qui survit
    à l'oubli. Un « à faire » dans un carnet ne se relit pas."""
    assert set(N.A_RENSEIGNER) >= {"socle_des_piliers", "budget_et_duree",
                                   "specificites_reglementaires"}
    for cle, texte in N.A_RENSEIGNER.items():
        assert len(texte) > 80, cle


def test_les_profils_declares_existent_vraiment_dans_l_audit():
    """Une clé inventée ici ferait promettre au sélecteur un profil que l'audit
    ne connaît pas : le bouton ouvrirait sur rien, sans erreur."""
    bloc = MOTEUR[MOTEUR.index("var MAT_SECTORS = {"):]
    bloc = bloc[:bloc.index("window.MAT_SECTORS")]
    connus = set(re.findall(r'"(\w+)": \{"label"', bloc))
    assert connus, "les profils de l'audit sont introuvables"
    assert set(N.PROFILS_SENTINEL) == connus, (
        "le module déclare %s, l'audit connaît %s"
        % (sorted(N.PROFILS_SENTINEL), sorted(connus)))


def test_chaque_profil_dit_POURQUOI_il_couvre_ces_sections_la():
    """Une correspondance sans motif est une affirmation. « La santé couvre R,
    C et K » ne se comprend que si l'on dit que les fabricants de dispositifs
    relèvent de l'industrie et les éditeurs de logiciels de l'informatique."""
    for cle, p in N.PROFILS_SENTINEL.items():
        assert len(p["note"]) > 40, cle
        assert p["sections"], cle


def test_une_lettre_inconnue_n_est_jamais_devinee():
    r = N.choisir("Z")
    assert r["connu"] is False and r["profils"] == []
    assert "A à V" in r["motif"]


@pytest.mark.parametrize("casse", ["lettre", "section_fantome", "verbatim"])
def test_le_referentiel_refuse_de_se_charger_s_il_se_contredit(monkeypatch, casse):
    """Contrôlé à l'import : c'est le seul moment où l'incohérence est encore
    gratuite. Plus tard elle sort à l'écran, et à l'écran on la croit."""
    if casse == "lettre":
        monkeypatch.setattr(N, "SECTIONS", N.SECTIONS[:-1])
    elif casse == "section_fantome":
        monkeypatch.setattr(N, "PROFILS_SENTINEL",
                            dict(N.PROFILS_SENTINEL,
                                 finance={"sections": ["Z"], "note": "x" * 50}))
    else:
        abime = [dict(s) for s in N.SECTIONS]
        abime[0]["intitule_officiel"] = "Agriculture, forestry and fishing"
        monkeypatch.setattr(N, "SECTIONS", abime)
        monkeypatch.setattr(N, "_PAR_CODE", {s["code"]: s for s in abime})
    with pytest.raises(ValueError):
        N._verifier()


# ═══════════════════════════════════════════════════════════════════════════
#  4. LA ROUTE ET LE SÉLECTEUR — EXÉCUTÉ, PAS LU
# ═══════════════════════════════════════════════════════════════════════════

def test_la_route_sert_le_module_sans_le_recopier():
    bloc = re.search(r"@app\.route\('/api/secteurs-nace'.*?\n@app\.route",
                     SOURCE, re.S)
    assert bloc, "la route /api/secteurs-nace est introuvable"
    corps = bloc.group(0)
    assert "secteurs_nace.etat()" in corps
    assert "@rate_limit" in corps
    # Aucun intitulé recopié dans la route : la nomenclature a UNE source.
    for s in N.SECTIONS[:6]:
        assert s["intitule"] not in corps, s["code"]


def test_aucune_zone_adressee_par_le_selecteur_ne_manque_a_la_page():
    """LE DÉFAUT MIROIR de la zone orpheline. Le sélecteur écrit dans trois
    éléments ; si l'un d'eux est renommé dans la page, `getElementById` rend
    `null`, la fonction sort, et le bloc reste blanc — sans erreur. Un contrôle
    qui exécute avec des identifiants écrits en dur dans le harnais ne le
    verrait pas : il faut confronter le JS à la PAGE."""
    d = MOTEUR.index("window.naceCharger = function()")
    d = MOTEUR.rindex("(function(){", 0, d)
    bloc = MOTEUR[d:MOTEUR.index("\n})();", d)]
    adressees = set(re.findall(r"getElementById\('(mat-nace-[a-z-]+)'\)", bloc))
    assert adressees, "le sélecteur n'adresse aucune zone"
    i = PAGE.index('id="p-maturite"')
    page = PAGE[i:PAGE.index('<div class="page"', i + 10)]
    dans_la_page = set(re.findall(r'id="(mat-nace-[a-z-]+)"', page))
    assert adressees == dans_la_page, (
        "le sélecteur écrit dans %s, la page déclare %s"
        % (sorted(adressees), sorted(dans_la_page)))


def test_le_selecteur_est_dans_le_panneau_et_avant_les_huit_profils():
    """L'ORDRE EST L'ARGUMENT. Le classement international se choisit d'abord,
    et il renvoie ensuite vers le profil relevé — l'inverse ferait du NACE une
    note de bas de page sur un choix déjà fait."""
    i = PAGE.index('id="p-maturite"')
    bloc = PAGE[i:PAGE.index('<div class="page"', i + 10)]
    assert bloc.index('id="mat-nace-select"') < bloc.index('id="mat-sector-bar"')


_HARNAIS = r"""
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const fin = src.indexOf('window.naceCharger = function()');
const deb = src.lastIndexOf('(function(){', fin);
const iife = src.slice(deb, src.indexOf('\n})();', fin) + 6);
const ids = ['mat-nace-select','mat-nace-reponse','mat-nace-source'];
const zones = {};
ids.forEach(function(id){ zones[id] = {id:id, innerHTML:'', dataset:{}}; });
global.window = { MAT_SECTORS: JSON.parse(process.argv[4]) };
global.document = { getElementById: function(id){ return zones[id] || null; } };
const rep = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
global.fetch = function(){
  return Promise.resolve({ok:true, json:function(){ return Promise.resolve(rep); }});
};
eval(iife);
window.naceCharger();
setTimeout(function(){
  const out = {liste: zones['mat-nace-select'].innerHTML,
               source: zones['mat-nace-source'].innerHTML};
  window.naceChoisir('L'); out.avec = zones['mat-nace-reponse'].innerHTML;
  window.naceChoisir('Q'); out.sans = zones['mat-nace-reponse'].innerHTML;
  window.naceChoisir('');  out.vide = zones['mat-nace-reponse'].innerHTML;
  process.stdout.write(JSON.stringify(out));
}, 40);
"""


def _peindre():
    if not NODE:
        pytest.skip("node absent : le sélecteur ne peut pas être exécuté")
    etat = N.etat()
    etat["ok"] = True
    faux_profils = {k: {"icon": "•", "label": k.upper()} for k in N.PROFILS_SENTINEL}
    with tempfile.TemporaryDirectory() as d:
        rep = os.path.join(d, "rep.json")
        harnais = os.path.join(d, "h.js")
        io.open(rep, "w", encoding="utf-8").write(json.dumps(etat, ensure_ascii=False))
        io.open(harnais, "w", encoding="utf-8").write(_HARNAIS)
        r = subprocess.run([NODE, harnais, os.path.join(ICI, "sentinel.page.js"),
                            rep, json.dumps(faux_profils)],
                           capture_output=True, text=True, timeout=90)
    if r.returncode != 0:
        pytest.fail("le sélecteur ne s'exécute pas :\n%s" % (r.stderr or "")[-1500:])
    return json.loads(r.stdout)


def _texte(html_):
    import html as _h
    return re.sub(r"\s+", " ", _h.unescape(re.sub(r"<[^>]+>", " ", html_)))


def test_les_vingt_deux_sections_sont_proposees_a_l_ecran():
    peint = _peindre()
    assert peint["liste"].count("<option") == 23, "22 sections + l'invite"
    lu = _texte(peint["liste"])
    for s in N.SECTIONS:
        assert s["intitule"] in lu, s["code"]


def test_la_liste_dit_DES_LA_LISTE_qu_une_section_n_a_pas_de_profil():
    """Le découvrir après le choix ferait porter au client une déception que la
    liste pouvait lui épargner. La règle compte : treize mentions, ni plus ni
    moins — un « (aucun profil relevé)» sur toutes les lignes passerait un
    contrôle de simple présence."""
    peint = _peindre()
    assert peint["liste"].count("aucun profil relevé") == 13


def test_LE_DEFAUT_VU_EN_EXECUTANT_une_section_sans_profil_dit_pourquoi():
    """Un premier jet construisait la liste servie à part de `choisir()`, sans
    `motif` : l'écran peignait, pour ces treize sections, un bloc d'explication
    VIDE — exactement l'information qui manquait le plus. La structure était
    juste, l'écran muet, et rien ne le signalait."""
    lu = _texte(_peindre()["sans"])
    assert "aucun profil sectoriel n'est relevé" in lu
    assert "ne dépendent pas du secteur" in lu, (
        "l'écran ne dit pas que l'audit reste utilisable — le lecteur croit "
        "être devant une impasse")
    for texte in N.A_RENSEIGNER.values():
        assert texte[:60] in lu


def test_une_section_avec_profil_mene_au_profil_et_dit_pourquoi():
    lu = _texte(_peindre()["avec"])
    assert "FINANCE" in lu.upper()
    assert N.PROFILS_SENTINEL["finance"]["note"][:50] in lu
    assert "matSelect" in _peindre()["avec"], (
        "aucun bouton n'ouvre le profil : la correspondance est décorative")


def test_l_ecran_porte_la_source_la_couverture_et_la_reserve():
    """Les trois ensemble, ou rien : une nomenclature sans source est une
    liste, une liste sans couverture donne vingt-deux entrées d'apparence
    équivalente, et une traduction sans réserve se prend pour un texte
    officiel."""
    lu = _texte(_peindre()["source"])
    assert N.SOURCE["celex"] in lu
    assert N.SOURCE["revision"] in lu
    assert "9 des 22 sections" in lu
    assert "traduction de travail" in lu


def test_un_choix_vide_efface_la_reponse_au_lieu_de_la_laisser():
    """Sans cela, la réponse de la section précédente reste affichée sous une
    liste revenue à l'invite — et se lit comme la réponse du choix courant."""
    assert not _peindre()["vide"].strip()
