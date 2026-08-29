"""DEUX CALENDRIERS SUR LA MÊME PAGE, ET ILS SE CONTREDISAIENT DE DIX-HUIT MOIS.

CE QUI A ÉTÉ TROUVÉ, LE 29 AOÛT 2026. Le tableau « Calendrier consolidé EU AI
Act », en tête du simulateur, portait déjà les dates du Digital Omnibus :
annexe III au 2 décembre 2027, annexe I au 2 août 2028. La frise rendue dans
les RÉSULTATS du même simulateur, quelques centaines de pixels plus bas,
portait sa propre liste écrite à la main et annonçait encore le 2 août 2026
pour l'annexe III. Le même écran donnait deux réponses à la question
« quand ? ».

La frise se trompait par ailleurs d'annexe : elle citait « composants de
sécurité (Annexe II) », alors que l'annexe II liste la législation
d'harmonisation — ce sont les produits de l'ANNEXE I qui portent les systèmes à
haut risque intégrés.

Et la même date périmée figurait dans dix-neuf fiches du panorama, dans les
jalons de `juridique.py`, dans la feuille de route, dans le rapport de
direction, dans les guides de page et dans la question d'antériorité du
simulateur.

CE QUE CES RÈGLES GARDENT. Qu'il n'y ait plus qu'UNE source de calendrier et
que la frise en dérive au lieu de la recopier ; qu'aucun fichier n'énonce, à
côté d'« annexe III », une date autre que celle de cette source ; et — c'est
l'autre moitié, celle qu'on oublie — que la correction ne déborde pas :
l'article 50 s'applique depuis le 2 août 2026, le Digital Omnibus ne l'a pas
déplacé, et une correction en masse des dates le casserait.

CE QU'ELLES NE PEUVENT PAS FAIRE. Dire si ces dates sont juridiquement exactes.
Elles proviennent du communiqué que le cabinet a lui-même publié le 13 juillet
2026 sur l'adoption du Digital Omnibus. Ces règles garantissent la COHÉRENCE du
site avec ce qu'il affirme, pas la véracité de ce qu'il affirme.
"""
import io
import json
import os
import re
import shutil
import subprocess

import pytest

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOTEUR = io.open(os.path.join(ICI, 'sentinel.page.js'), encoding='utf-8').read()
NODE = shutil.which('node')

# La source unique, telle qu'elle est déclarée dans le fichier.
ANNEXE_III = '2 décembre 2027'
ANNEXE_I = '2 août 2028'
ARTICLE_50 = '2 août 2026'

FICHIERS = [f for f in os.listdir(ICI)
            if f.endswith(('.js', '.html', '.py')) and os.path.isfile(os.path.join(ICI, f))]


def _calendrier():
    if not NODE:
        pytest.skip('node absent : le calendrier ne peut pas être évalué')
    d = MOTEUR.index('var AI_ACT_TIMELINE = [')
    src = MOTEUR[d:MOTEUR.index('\n];', d) + 3]
    r = subprocess.run([NODE, '-e', src + '\nconsole.log(JSON.stringify(AI_ACT_TIMELINE));'],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        pytest.fail("AI_ACT_TIMELINE ne s'évalue pas :\n%s" % (r.stderr or '')[-1000:])
    return json.loads(r.stdout)


CALENDRIER = _calendrier()


# ── LA SOURCE UNIQUE ─────────────────────────────────────────────────────

def test_le_calendrier_porte_les_dates_du_digital_omnibus():
    lignes = {r['date']: r['quoi'] for r in CALENDRIER}
    assert ANNEXE_III in lignes, (
        "le calendrier ne porte pas d'échéance au %s : les dates du Digital "
        "Omnibus ont-elles été retirées ?" % ANNEXE_III)
    assert 'Annexe III' in lignes[ANNEXE_III], (
        "l'échéance du %s ne concerne plus l'annexe III mais « %s »"
        % (ANNEXE_III, lignes[ANNEXE_III]))
    assert ANNEXE_I in lignes and 'Annexe I' in lignes[ANNEXE_I], (
        "l'échéance annexe I du %s a disparu du calendrier" % ANNEXE_I)


def test_le_calendrier_ne_confond_pas_l_annexe_I_et_l_annexe_II():
    """L'ancienne frise citait « composants de sécurité (Annexe II) ».
    L'annexe II liste la législation d'harmonisation ; ce sont les produits de
    l'annexe I qui portent les systèmes à haut risque intégrés."""
    # ET « Annexe II » EST UN PRÉFIXE D'« Annexe III ». Une première version de
    # ce contrôle accusait la ligne de l'annexe III d'être une ligne de
    # l'annexe II. C'est la troisième fois dans ce travail qu'un numéro
    # d'article ou d'annexe se fait avaler par son voisin plus long.
    for r in CALENDRIER:
        assert not re.search(r'Annexe II(?!I)', r['quoi'] or ''), (
            "l'échéance du %s parle de l'annexe II là où l'annexe I est visée : "
            "« %s »" % (r['date'], r['quoi']))


def test_l_article_50_n_a_pas_ete_deplace():
    """LA MOITIÉ QU'ON OUBLIE. Le Digital Omnibus n'a pas touché aux
    obligations de transparence : elles s'appliquent depuis le 2 août 2026. Une
    correction en masse des dates les emporterait avec le reste."""
    lignes = {r['date']: r['quoi'] for r in CALENDRIER}
    assert ARTICLE_50 in lignes, (
        "l'échéance du %s a disparu du calendrier : les obligations de "
        "transparence de l'article 50 n'ont pourtant pas été déplacées" % ARTICLE_50)
    assert 'Art. 50' in lignes[ARTICLE_50] or 'transparence' in lignes[ARTICLE_50].lower(), (
        "l'échéance du %s ne concerne plus la transparence" % ARTICLE_50)


# ── LA FRISE DÉRIVE, ELLE NE RECOPIE PLUS ────────────────────────────────

def test_la_source_est_exposee_pour_etre_lue_ailleurs():
    assert 'window.AI_ACT_TIMELINE = AI_ACT_TIMELINE;' in MOTEUR, (
        "le calendrier n'est plus expose : la frise des résultats ne peut plus "
        "le lire et devra de nouveau porter sa propre liste")


def test_la_frise_du_simulateur_derive_du_calendrier():
    """LA RÈGLE QUI EMPÊCHE LA CONTRADICTION DE REVENIR. Tant que la frise lit
    la source, les deux ne peuvent plus diverger. Si elle réécrit sa liste,
    elle divergera — c'est ce qui vient d'arriver."""
    d = MOTEUR.index('function simTimeline(classif){')
    corps = MOTEUR[d:MOTEUR.index('\n}', d)]
    assert 'AI_ACT_TIMELINE' in corps, (
        "simTimeline ne lit plus le calendrier consolidé")
    dates = re.findall(r"date:\s*'([^']*20\d\d[^']*)'", corps)
    assert not dates, (
        "simTimeline réécrit des dates en dur : %s. Deux calendriers sur une "
        "même page finissent toujours par se contredire." % ', '.join(dates))


def test_sans_calendrier_la_frise_le_dit_au_lieu_d_inventer():
    """Une liste de secours écrite dans la fonction recommencerait à diverger.
    Mieux vaut une frise qui s'annonce indisponible qu'une frise qui affiche
    des dates dont plus personne ne répond."""
    if not NODE:
        pytest.skip('node absent')
    d = MOTEUR.index('function simTimeline(classif){')
    corps = MOTEUR[d:MOTEUR.index('\n}', d) + 2]
    prog = ('var window = {};\n%s\n'
            'console.log(JSON.stringify(simTimeline({level:"haut", art5:false})));' % corps)
    r = subprocess.run([NODE, '-e', prog], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-800:]
    frise = json.loads(r.stdout)
    assert len(frise) == 1 and '20' not in frise[0]['date'], (
        "sans calendrier, la frise affiche tout de même des dates : %s" % frise)


def test_avec_le_calendrier_la_frise_rend_les_bonnes_dates():
    """Le contrôle décisif : ce que le client lit sous son résultat."""
    if not NODE:
        pytest.skip('node absent')
    d = MOTEUR.index('function simTimeline(classif){')
    corps = MOTEUR[d:MOTEUR.index('\n}', d) + 2]
    dcal = MOTEUR.index('var AI_ACT_TIMELINE = [')
    cal = MOTEUR[dcal:MOTEUR.index('\n];', dcal) + 3]
    prog = ('%s\nvar window = {AI_ACT_TIMELINE: AI_ACT_TIMELINE};\n%s\n'
            'console.log(JSON.stringify(simTimeline({level:"haut", art5:false})));' % (cal, corps))
    r = subprocess.run([NODE, '-e', prog], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-800:]
    frise = json.loads(r.stdout)
    dates = [x['date'] for x in frise]
    assert ANNEXE_III in dates, (
        "la frise des résultats n'annonce pas le %s pour l'annexe III : %s"
        % (ANNEXE_III, ', '.join(dates)))
    soulignees = [x['date'] for x in frise if x.get('urgent')]
    assert soulignees == [ANNEXE_III], (
        "pour un système à haut risque, la ligne soulignée devrait être celle "
        "de l'annexe III ; ce sont : %s" % (soulignees or 'aucune'))


def test_la_ligne_soulignee_suit_le_systeme_analyse():
    """Un système relevant d'une pratique interdite doit voir l'article 5
    souligné, pas l'annexe III."""
    if not NODE:
        pytest.skip('node absent')
    d = MOTEUR.index('function simTimeline(classif){')
    corps = MOTEUR[d:MOTEUR.index('\n}', d) + 2]
    dcal = MOTEUR.index('var AI_ACT_TIMELINE = [')
    cal = MOTEUR[dcal:MOTEUR.index('\n];', dcal) + 3]
    prog = ('%s\nvar window = {AI_ACT_TIMELINE: AI_ACT_TIMELINE};\n%s\n'
            'console.log(JSON.stringify(simTimeline({level:"interdit", art5:true})));' % (cal, corps))
    r = subprocess.run([NODE, '-e', prog], capture_output=True, text=True, timeout=60)
    frise = json.loads(r.stdout)
    soulignees = [x['quoi'] if 'quoi' in x else x['text'] for x in frise if x.get('urgent')]
    assert len(soulignees) == 1 and ('Interdictions' in soulignees[0] or 'Art. 5' in soulignees[0]), (
        "une pratique interdite ne souligne pas la ligne de l'article 5 : %s" % soulignees)


# ── AUCUN FICHIER N'ÉNONCE UNE DATE PÉRIMÉE POUR L'ANNEXE III ────────────

# Ce qui, à côté d'une date, désigne le régime de l'annexe III — et ce qui
# désigne au contraire les obligations de transparence, restées au 2 août 2026.
QUALIFIANT = re.compile(r'annexe\s*III|Annexe\s*III|art\.?\s*6\(1\)|Art\.?\s*6\(2\)', re.I)
TRANSPARENCE = re.compile(r'art\.?\s*50|article\s*50|transparence', re.I)
DATE = re.compile(r'2\s*ao[uû]t\s*2026|2\s*ao[uû]t\s*2027|2026-08-02|2027-08-02')


# L'énoncé qui PORTE la date : ni plus, ni moins.
# 
#     DEUX CORRECTIONS SUCCESSIVES, ET CHACUNE APPRENAIT QUELQUE CHOSE.
# 
#     La première version prenait quatre-vingt-dix caractères de part et d'autre
#     et signalait toute mention d'annexe III trouvée dedans. Elle a accusé
#     quatre phrases JUSTES — celles qui opposent les deux calendriers :
#     « transparence art. 50 depuis le 2 août 2026 ; haut risque annexe III au
#     2 décembre 2027 ». Interdire de nommer les deux régimes dans une même
#     phrase, c'est interdire d'être clair.
# 
#     La deuxième retenait le qualifiant le plus PROCHE. Elle a laissé passer la
#     régression des jalons de `juridique.py` : l'entrée voisine de la liste se
#     terminait par « (transparence) » à vingt caractères de la date, plus près
#     que l'« annexe III » de sa propre phrase. Une fenêtre de caractères ignore
#     les frontières du texte ; une liste de chaînes en a.
# 
#     On borne donc d'abord à l'énoncé — guillemet, retour à la ligne,
#     point-virgule ou fin de phrase —, et la proximité ne joue qu'à l'intérieur.
#     Les balises HTML sont retirées : `<b>` ne sépare pas deux idées.


def _qualifiant_le_plus_proche(unite, pos):
    proches = []
    for rx, etiquette in ((QUALIFIANT, 'annexe III'), (TRANSPARENCE, 'transparence')):
        for m in rx.finditer(unite):
            proches.append((min(abs(m.start() - pos), abs(m.end() - pos)), etiquette))
    if not proches:
        return None
    return min(proches)[1]


def test_aucun_fichier_n_annonce_une_date_perimee_pour_l_annexe_III():
    """LA RÈGLE QUI AURAIT ÉVITÉ TOUT CE TRAVAIL. Les dates étaient recopiées
    dans treize fichiers ; le jour où le calendrier a bougé, un seul a suivi."""
    fautes = []
    for nom in sorted(FICHIERS):
        brut = io.open(os.path.join(ICI, nom), encoding='utf-8', errors='replace').read()
        # Les balises ne séparent pas deux idées : on les retire avant de
        # découper, sans quoi « annexe III au <b>2 août 2026</b> » se casse en
        # deux énoncés dont aucun ne porte les deux termes.
        #
        # DANS LES FICHIERS HTML SEULEMENT, et cette restriction m'a coûté une
        # mutation survivante. Appliqué à un `.js`, `<[^>]*>` ne retire pas des
        # balises : il dévore tout ce qui se trouve entre un `<` et un `>` de
        # COMPARAISON — `if(a < b){…}` et cent lignes derrière. La règle
        # travaillait alors sur un fichier mutilé, où l'énoncé fautif avait
        # simplement disparu.
        s = re.sub(r'<[^>]*>', '', brut) if nom.endswith('.html') else brut
        for m in DATE.finditer(s):
            # L'énoncé qui porte la date, borné aux frontières du texte.
            g = max((s.rfind(x, max(0, m.start() - 400), m.start())
                     for x in ('"', '\n', ';')), default=-1)
            pt = s.rfind('. ', max(0, m.start() - 400), m.start())
            g = max(g, pt + 1 if pt >= 0 else -1)
            fin = min((p for p in (s.find(x, m.end(), m.end() + 400)
                                   for x in ('"', '\n', ';', '. ')) if p >= 0),
                      default=len(s))
            unite = s[g + 1:fin]
            if _qualifiant_le_plus_proche(unite, m.start() - (g + 1)) != 'annexe III':
                continue
            plat = re.sub(r'\s+', ' ', unite)
            # Le commentaire qui RACONTE l'ancienne date pour expliquer la
            # correction n'est pas une affirmation de calendrier.
            if 'annonçait encore' in plat:
                continue
            fautes.append('%s : « %s »' % (nom, plat.strip()[:140]))
    assert not fautes, (
        "date périmée rattachée au régime de l'annexe III :\n  - %s"
        % '\n  - '.join(fautes))


def test_la_date_de_l_annexe_III_est_bien_celle_du_calendrier_partout():
    """L'inverse du contrôle précédent : il refuse les mauvaises dates, celui-ci
    exige que la bonne soit effectivement écrite là où le sujet l'appelle."""
    porteurs = [nom for nom in FICHIERS
                if ANNEXE_III in io.open(os.path.join(ICI, nom), encoding='utf-8',
                                         errors='replace').read()]
    assert len(porteurs) >= 4, (
        "seuls %d fichiers annoncent le %s : %s. Les vues qui parlaient de "
        "l'annexe III ont-elles perdu leur échéance ?"
        % (len(porteurs), ANNEXE_III, ', '.join(porteurs)))


def test_l_article_50_reste_au_2_aout_2026_dans_les_pages():
    """LA GARDE CONTRE LA SUR-CORRECTION. Une reprise en masse des dates
    emporterait l'article 50, que le Digital Omnibus n'a pas déplacé."""
    page = io.open(os.path.join(ICI, 'actualites.html'), encoding='utf-8').read()
    # LA DATE DOIT ÊTRE ATTACHÉE À L'OBLIGATION, PAS SEULEMENT PRÉSENTE DANS LA
    # PAGE. Une première version demandait « 2 août 2026 » quelque part dans le
    # fichier : la date figure aussi dans le titre du communiqué, dans la liste
    # des termes surlignés et dans les versions anglaise et allemande. Déplacer
    # la phrase qui compte laissait donc la règle satisfaite.
    phrase = "Le %s, les obligations de transparence de l'article 50" % ARTICLE_50
    assert phrase in page, (
        "le communiqué n'attache plus l'entrée en application des obligations "
        "de transparence au %s : le Digital Omnibus ne les a pourtant pas "
        "déplacées, et une reprise en masse des dates les emporterait" % ARTICLE_50)


def test_le_bandeau_d_accueil_dit_que_c_est_applicable_et_non_que_cela_approche():
    """Le bandeau annonçait « L'échéance du 2 août 2026 approche » — une date
    passée. Une échéance dépassée qu'on annonce comme prochaine décrédibilise
    tout ce qui l'entoure : le lecteur qui connaît le calendrier en déduit que
    le site n'est pas tenu.

    LE TEXTE EST DOUBLÉ, et le contrôle l'exige : le ruban défile en boucle par
    duplication du texte. N'en corriger qu'un ferait alterner les deux
    formulations sous les yeux du visiteur."""
    accueil = io.open(os.path.join(ICI, 'index.html'), encoding='utf-8').read()
    assert 'approche' not in accueil or ARTICLE_50 not in accueil.split('approche')[0][-200:], (
        "le bandeau annonce encore une échéance passée comme prochaine")
    attendu = ("Depuis le <strong>%s</strong>, les obligations de transparence "
               "de l'IA Act s'appliquent." % ARTICLE_50)
    n = accueil.count(attendu)
    assert n == 2, (
        "le bandeau doit porter deux fois la même phrase — le ruban défile en "
        "la dupliquant — et on en compte %d. Une seule moitié corrigée ferait "
        "alterner deux formulations." % n)
