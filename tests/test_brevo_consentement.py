# -*- coding: utf-8 -*-
"""L'inscription à une liste Brevo exige une preuve de consentement.

CE QUE LE REGISTRE PROMETTAIT DÉJÀ, ET QUE LE CODE NE FAISAIT PAS. La ligne
« Courriels transactionnels et lettre d'information » du registre des
traitements — semée par le code lui-même, et servie aux visiteurs — déclare :
base « consentement (art. 6.1.a) », destinataire « Brevo (UE) », durée
« jusqu'au retrait du consentement ».

`add_contact_to_brevo` inscrivait sans jamais chercher un consentement ni
honorer un retrait. Un écart entre ce qu'un site DÉCLARE et ce que son code
FAIT, du genre qui se lit très mal dans un contrôle — et qui ne se voyait
nulle part, la fonction n'étant appelée par personne.

CE QUE CES RÈGLES TIENNENT. Une vérification de consentement se contourne de
quatre façons, et chacune a sa règle :

  · en la faisant porter par un ARGUMENT que l'appelant fournit — l'art. 7.1
    met la charge de la preuve sur le responsable de traitement, et une preuve
    qu'on s'accorde à soi-même n'en est pas une ;
  · en laissant un RETRAIT plus récent perdre contre un consentement ancien ;
  · en se rabattant sur « autoriser » quand la base est injoignable — soit
    précisément le jour où personne ne regarde ;
  · en ressuscitant un consentement EFFACÉ au titre de l'article 17.

S'y ajoute la minimisation (art. 5.1.c) : tracer un refus est utile, recopier
l'adresse dans les journaux d'un traitement auquel la personne n'a pas consenti
ajouterait un manquement au lieu d'en corriger un.
"""
import io
import os
import re
import sys

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ICI)

APP = io.open(os.path.join(ICI, "app.py"), encoding="utf-8").read()


def _fonction(nom):
    i = APP.index("\ndef %s(" % nom)
    j = APP.find("\ndef ", i + 1)
    return APP[i:j if j > 0 else len(APP)]


def _code(nom):
    """Le corps SANS sa docstring : une règle qui lirait la prose serait verte
    devant le code qui la contredit."""
    corps = _fonction(nom)
    if corps.count('"""') >= 2:
        return corps[corps.index('"""', corps.index('"""') + 3) + 3:]
    return corps


# ══════════════════════════════════════════════════════════════════════════
# 1. RIEN N'EST ENVOYÉ À BREVO SANS PREUVE
# ══════════════════════════════════════════════════════════════════════════

def test_l_inscription_exige_une_preuve_avant_tout_appel_a_brevo():
    """La vérification doit précéder l'appel réseau. Vérifier après aurait déjà
    transmis l'adresse à un tiers — le manquement est consommé au moment de la
    transmission, pas au moment où l'on s'en aperçoit."""
    code = _code("add_contact_to_brevo")
    i = code.index("consentement_lettre_information(email)")
    j = code.index("api.brevo.com")
    assert i < j, "l'adresse part chez Brevo avant que le consentement soit vérifié"
    refus = code[i:j]
    assert re.search(r"if not ok:[\s\S]*?return False", refus), refus


def test_la_preuve_se_lit_dans_les_donnees_et_pas_dans_un_argument():
    """ART. 7.1 : LA CHARGE DE LA PREUVE INCOMBE AU RESPONSABLE. Un paramètre
    `consentement=True` que l'appelant fournirait rendrait la vérification
    décorative — c'est le contournement le plus naturel, donc celui qu'il faut
    interdire explicitement."""
    signature = APP[APP.index("\ndef add_contact_to_brevo("):]
    signature = signature[:signature.index("\n", 1)]
    for mot in ("consent", "opt_in", "optin", "autorise"):
        assert mot not in signature.lower(), (
            "la signature accepte « %s » : le consentement redeviendrait "
            "déclaratif\n%s" % (mot, signature))
    code = _code("consentement_lettre_information")
    assert "FROM consent_records" in code, code


# ══════════════════════════════════════════════════════════════════════════
# 2. LES QUATRE FAÇONS DE CONTOURNER, CHACUNE FERMÉE
# ══════════════════════════════════════════════════════════════════════════

def test_un_retrait_plus_recent_l_emporte_sur_un_consentement_ancien():
    """Sans cela, le retrait ne serait qu'un enregistrement décoratif : la
    personne cliquerait « je me désinscris » et resterait inscrite. Les lignes
    sont lues de la plus récente à la plus ancienne, et la première qui tranche
    l'emporte."""
    code = _code("consentement_lettre_information")
    assert "ORDER BY id DESC" in code, code
    boucle = code[code.index("for ligne in lignes:"):]
    i = boucle.index("if ligne['retrait']:")
    j = boucle.index("return True")
    assert i < j, ("le consentement est examiné avant le retrait : un retrait "
                   "postérieur perdrait\n%s" % boucle)


def test_une_base_injoignable_refuse_au_lieu_d_enroler():
    """L'INCERTITUDE SE TRANCHE CONTRE LE TRAITEMENT. Un repli permissif
    enrôlerait le jour où la vérification tombe en panne — c'est-à-dire
    exactement quand personne ne regarde."""
    code = _code("consentement_lettre_information")
    i = code.index("except Exception")
    j = code.index("for ligne in lignes:")
    bloc = code[i:j]
    assert re.search(r"return False, '[^']+'", bloc), bloc
    assert "return True" not in bloc, bloc


def test_un_consentement_efface_au_titre_de_l_article_17_ne_ressuscite_pas():
    """L'effacement blanchit l'adresse et pose `efface=1` sans supprimer la
    ligne (la preuve d'avoir effacé est elle-même une preuve). Lire ces lignes
    ferait revivre un consentement que la personne a fait disparaître."""
    code = _code("consentement_lettre_information")
    requete = code[code.index("SELECT finalites"):code.index("ORDER BY id DESC")]
    assert "efface=0" in requete, requete


def test_l_adresse_n_est_pas_journalisee():
    """ART. 5.1.c. Tracer un refus est utile ; recopier l'adresse dans les
    journaux d'un traitement auquel la personne n'a pas consenti ajouterait un
    manquement au lieu d'en corriger un."""
    for nom in ("add_contact_to_brevo", "consentement_lettre_information"):
        for appel in re.findall(r"logger\.\w+\([^\n]*\)", _code(nom)):
            assert "email" not in appel and "{em}" not in appel, (
                "%s journalise l'adresse : %s" % (nom, appel))


# ══════════════════════════════════════════════════════════════════════════
# 3. UNE SEULE FINALITÉ, ET LE CODE FAIT CE QUE LE REGISTRE DÉCLARE
# ══════════════════════════════════════════════════════════════════════════

def test_la_finalite_est_nommee_une_seule_fois():
    """Le point de RECUEIL et le point de VÉRIFICATION doivent nommer la même
    chose. Deux libellés voisins produiraient un consentement recueilli pour une
    finalité et cherché pour une autre — donc jamais trouvé, ou pire, trouvé à
    tort. La règle exige la constante ET l'absence de littéral concurrent."""
    assert "CONSENTEMENT_LETTRE_INFORMATION = 'lettre_information'" in APP, \
        "la finalité n'est pas nommée une seule fois"
    litteraux = re.findall(r"'lettre_information'", APP)
    assert len(litteraux) == 1, (
        "« lettre_information » apparaît %d fois en littéral : la constante ne "
        "sert plus à rien" % len(litteraux))
    assert "finalites.get(CONSENTEMENT_LETTRE_INFORMATION)" in \
        _code("consentement_lettre_information")


def test_le_registre_servi_aux_visiteurs_declare_bien_ce_qu_on_applique():
    """LE REGISTRE EST SERVI AUX VISITEURS, DONC IL ENGAGE. Sa ligne Brevo doit
    déclarer le consentement comme base et le retrait comme terme — c'est
    exactement ce que le code applique désormais. Si elle dérivait vers
    l'intérêt légitime, le code deviendrait plus strict que la déclaration :
    moins grave que l'inverse, mais l'écart doit se voir dans les deux sens.

    La règle lit LA LIGNE DU REGISTRE, pas un commentaire qui la paraphrase.
    Que le code honore le consentement et le retrait est tenu par
    `test_l_inscription_exige_une_preuve_avant_tout_appel_a_brevo` et
    `test_un_retrait_plus_recent_l_emporte_sur_un_consentement_ancien` : le
    redire ici ferait tomber trois règles pour un seul défaut — c'est le
    recouvrement corrigé quatre fois cette semaine.
    """
    i = APP.index("'nom': 'Courriels transactionnels et lettre d\\'information'")
    ligne = APP[i:APP.index("}", i)]
    # CHAQUE AFFIRMATION EST LUE DANS SON PROPRE CHAMP. Chercher le mot
    # « consentement » n'importe où dans la ligne resterait vert devant une base
    # légale changée en intérêt légitime : `duree` contient déjà « retrait du
    # consentement ». C'est la règle qui passe pour une raison sans rapport avec
    # ce qu'elle prétend — corrigée ici avant d'être écrite.
    champs = dict(re.findall(r"'(\w+)': '((?:[^'\\]|\\.)*)'", ligne))
    assert "Brevo" in champs.get("destinataires", ""), champs
    assert "consentement" in champs.get("base", "").lower(), champs
    assert "retrait" in champs.get("duree", "").lower(), champs
