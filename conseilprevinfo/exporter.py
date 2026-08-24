"""EMPORTER UNE FICHE — en PDF ou en Word, sans rien perdre en route.

CE QU'UN EXPORT NE DOIT PAS FAIRE, ET QUE PRESQUE TOUS FONT. Il ne doit pas
produire un document plus affirmatif que la page dont il vient. Un PDF qui ne
garderait que le titre et le chapeau serait plus « propre » — et il aurait
perdu exactement ce qui distingue ce site d'un agrégateur : le statut de
vérification, la nature de la lecture, ce qu'on ne sait pas, et la source.

Un document emporté circule SANS SA PAGE. Il est transféré, imprimé, joint à
un dossier, relu six mois plus tard par quelqu'un qui n'a jamais vu le site.
Il doit donc porter TOUT ce qui permet d'en juger — y compris ce qui le
relativise. Le fichier généré ici porte donc, dans cet ordre :

    · la portée et le sujet, en toutes lettres ;
    · la date DU FAIT, et sa réserve si c'est une convention ;
    · le titre et le chapeau, tels que la source les porte ;
    · la lecture critique AVEC SA NATURE — dérivée par règles ou signée ;
    · ce que cela change ; ce qu'on ne sait pas ;
    · la source, son éditeur, son statut, sa licence, son adresse ;
    · la date d'export et l'adresse de la fiche, pour y revenir.

AUCUN TEXTE N'EST RÉÉCRIT POUR L'EXPORT. Pas de résumé, pas de reformulation,
pas de titre « amélioré ». Ce qui sort est ce qui est publié — sans quoi il
existerait deux versions d'une même fiche, et rien ne dirait laquelle fait
foi.

DEUX FORMATS, DEUX RAISONS. Le PDF pour joindre à un dossier ou imprimer : il
ne bouge plus. Le Word pour reprendre un passage dans une note interne, ce
qu'un industriel fait constamment — refuser ce format le pousserait à
recopier à la main, donc à introduire des erreurs dans une citation.
"""
import io
import os
import re
import zipfile
from datetime import date, datetime, timezone
from xml.sax.saxutils import escape as _x

import gabarits as GB

VERSION = "2026.08.23"

ICI = os.path.dirname(os.path.abspath(__file__))
POLICES = os.path.join(ICI, "polices")

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]


def _fr(iso):
    try:
        d = date.fromisoformat(str(iso)[:10])
        return "%d %s %d" % (d.day, MOIS[d.month - 1], d.year)
    except (TypeError, ValueError):
        return str(iso or "—")


def _nom_fichier(fiche, ext):
    """Un nom de fichier lisible ET sûr.

    Le titre y entre parce qu'un dossier de vingt « fiche.pdf » est
    inexploitable — mais rien de ce qui vient de la source n'entre tel quel
    dans un nom de fichier : un titre porte des barres obliques, des points et
    des caractères que certains systèmes refusent.
    """
    brut = "%s-%s" % (fiche.get("id") or "fiche",
                      (fiche.get("titre") or "")[:60])
    sur = re.sub(r"[^A-Za-z0-9\-]+", "-", brut).strip("-").lower()
    return (sur or "fiche")[:80] + "." + ext


def blocs(fiche, url_fiche=None, langue="fr"):
    """LA STRUCTURE DU DOCUMENT, une seule fois pour les deux formats.

    Deux compositions séparées auraient divergé : le jour où l'on ajoute un
    champ, l'un des deux formats l'aurait porté et l'autre non — et personne
    ne s'en apercevrait, puisque personne n'ouvre les deux.

    LE DOCUMENT EST DANS LA LANGUE OÙ IL A ÉTÉ LU, INTERTITRES COMPRIS. Un PDF
    exporté depuis une interface anglaise avec « Ce qu'on ne sait pas » au
    milieu est pire qu'un document entièrement français : le lecteur qui le
    reçoit ne sait plus dans quelle langue est le texte qu'il n'a pas encore
    lu. Et le document DIT sa langue, en pied : il circule sans sa page.
    """
    f = fiche
    s = f.get("source") or {}
    out = []

    out.append(("entete", "%s · %s" % (f.get("impact_nom") or "",
                                       f.get("sujet_nom") or "")))
    out.append(("titre", f.get("titre") or ""))

    daté = GB.date(f.get("date_fait"), langue)
    if f.get("date_convention"):
        # LA RÉSERVE VOYAGE AVEC LA DATE, dans le document comme à l'écran.
        # Séparées, la date serait lue comme une observation par quiconque
        # n'ouvre pas le paragraphe suivant.
        daté += GB.dire("exp.convention", langue,
                        f.get("date_convention_dit") or "")
    out.append(("date", daté))

    if f.get("chapeau"):
        out.append(("chapeau", f["chapeau"]))

    out.append(("titre2", GB.dire("exp.lecture", langue,
                                  f.get("lecture_nom") or "")))
    out.append(("corps", f.get("lecture") or ""))
    if f.get("lecture_dit"):
        out.append(("note", f["lecture_dit"]))

    out.append(("titre2", GB.dire("exp.change", langue)))
    out.append(("corps", f.get("portee") or ""))

    out.append(("titre2", GB.dire("exp.ignore", langue)))
    out.append(("corps", f.get("incertitude") or ""))

    out.append(("titre2", GB.dire("exp.source", langue)))
    out.append(("corps", "%s — %s" % (s.get("nom") or "", s.get("editeur") or "")))
    out.append(("note", GB.dire("exp.statut", langue,
                                f.get("statut_nom") or "",
                                f.get("statut_dit") or "")))
    if s.get("url"):
        out.append(("note", GB.dire("exp.origine", langue, s["url"])))
    if s.get("licence"):
        out.append(("note", GB.dire("exp.licence", langue,
                                    s.get("licence_en") if langue == "en"
                                    and s.get("licence_en") else s["licence"])))

    # CE QUI PERMET DE REVENIR. Un document emporté circule sans sa page ; sans
    # son adresse, un lecteur qui le reçoit six mois plus tard ne peut pas
    # vérifier s'il a été corrigé depuis.
    pied = GB.dire("exp.pied", langue,
                   GB.date(datetime.now(timezone.utc).date().isoformat(), langue))
    if url_fiche:
        pied += " · %s" % url_fiche
    out.append(("pied", pied))
    out.append(("pied", GB.dire("exp.pied.regle", langue)))
    # LA LANGUE DU DOCUMENT, ÉCRITE DEDANS. Et si la fiche n'avait pas de
    # gabarit anglais, la réserve part avec elle : un document reçu six mois
    # plus tard doit dire lui-même pourquoi son texte est en français.
    out.append(("pied", GB.dire("exp.langue." + langue, langue)))
    if langue == "en" and f.get("analyses_traduites") is False:
        out.append(("pied", GB.dire("exp.langue.repli", langue)))
    return out


def _nom_fichier_revue(revue, ext):
    """« revue-hebdomadaire-2026-07-27.pdf ». Le genre ET la date, parce qu'un
    dossier de comité en accumule douze : « revue.pdf » les rendrait
    indiscernables au moment précis où l'on cherche celle de mars."""
    p = revue.get("periode") or {}
    genre = "mensuelle-internationale" if revue.get("international") else \
        ("hebdomadaire" if p.get("genre") == "semaine" else "mensuelle")
    return "revue-%s-%s.%s" % (genre, p.get("debut") or "sans-date", ext)


def blocs_revue(revue, url_revue=None, langue="fr"):
    """LA REVUE, COMPOSÉE UNE SEULE FOIS POUR LES DEUX FORMATS.

    ═══════════════════════════════════════════════════════════════════════
    CE QUE CE DOCUMENT DOIT PORTER, ET POURQUOI CE N'EST PAS NÉGOCIABLE
    ═══════════════════════════════════════════════════════════════════════
    UNE REVUE DE PRESSE EST LE DOCUMENT QUI CIRCULE LE PLUS. Elle est
    transférée, jointe à un ordre du jour, lue en comité par des gens qui
    n'ouvriront jamais le site. Et elle a l'autorité d'un résumé : le lecteur
    lui accorde d'avoir vu ce qu'il n'a pas lu lui-même.

    D'où trois règles, toutes appliquées ici et vérifiables ligne à ligne :

      · CE QU'ELLE COMPTE EST ÉCRIT EN TÊTE, pas en annexe. Sans cette
        phrase, « Revue de la semaine du 27 juillet » se lit comme
        « l'actualité de cette semaine-là », alors que c'est « les faits
        DATÉS de cette semaine et entrés au corpus ». Reléguée en pied, elle
        arriverait après la décision.
      · CE QU'ELLE ÉCARTE PART AVEC ELLE. Les dates posées, les fiches sans
        territoire, celles qui ne concernent que la France : trois comptes
        qui, absents, feraient croire que la période ne portait que ce qui
        est imprimé.
      · LES DEUX RUBRIQUES VIDES SONT DANS LE DOCUMENT. Un PDF qui les
        omettrait serait la version « propre » de la revue — et il aurait
        perdu la seule chose qu'elle dise d'elle-même : qu'elle ne contient
        ni reportage ni entretien, et pourquoi.

    AUCUN TEXTE N'EST RÉÉCRIT. Les titres et les chapeaux sont ceux des
    fiches, les comptes ceux du moteur, le classement le sien.
    """
    p = revue.get("periode") or {}
    out = []
    lib = p.get("libelle_en") if langue == "en" else p.get("libelle")

    out.append(("entete", GB.dire("exp.rv.mensuel" if revue.get("international")
                                  else "exp.rv.hebdo", langue)))
    out.append(("titre", lib or ""))

    # LE CORPUS VIDE EN PREMIER, s'il l'était : tout ce qui suit ne dirait
    # alors rien de la période, et le lecteur doit le savoir avant de lire.
    if revue.get("corpus_vide"):
        out.append(("note", GB.dire("exp.rv.corpus.vide", langue)))

    out.append(("note", GB.dire("exp.rv.compte", langue)))
    if revue.get("regle_internationale"):
        out.append(("note", GB.dire("exp.rv.regle", langue,
                                    revue["regle_internationale"])))

    t = revue.get("retard") or {}
    if (t.get("jours_depuis_la_fin") or 0) > 6 and t.get("dernier_fait"):
        out.append(("note", GB.dire("exp.rv.retard", langue,
                                    t["jours_depuis_la_fin"],
                                    GB.date(t["dernier_fait"], langue))))

    prec = revue.get("precedente") or {}
    ecart = prec.get("ecart", 0)
    out.append(("date", GB.dire("exp.rv.compteur", langue, revue.get("n", 0),
                                prec.get("n", 0),
                                ("+%d" % ecart) if ecart > 0 else str(ecart))))
    if revue.get("par_sujet"):
        out.append(("note", GB.dire(
            "exp.rv.sujets", langue,
            " · ".join("%s (%d)" % (x["nom"], x["n"])
                       for x in revue["par_sujet"]))))
    if revue.get("par_source"):
        out.append(("note", GB.dire(
            "exp.rv.sources", langue,
            " · ".join("%s (%d)" % (x["nom"], x["n"])
                       for x in revue["par_source"]))))

    if not revue.get("n"):
        out.append(("corps", GB.dire("exp.rv.vide", langue)))

    for b in revue.get("blocs") or []:
        out.append(("titre2", "%s — %d" % (b["nom"], b["n"])))
        for f in b["fiches"]:
            # LE TITRE ET LA DATE SUR LA MÊME LIGNE : douze entrées à quatre
            # lignes chacune font une revue qu'on ne parcourt plus.
            out.append(("chapeau", "%s — %s"
                        % (GB.date(f.get("date_fait"), langue),
                           f.get("titre") or "")))
            if f.get("chapeau"):
                out.append(("corps", f["chapeau"]))
            terr = list(f.get("organisations") or []) + list(f.get("pays") or [])
            if terr:
                out.append(("note", GB.dire("exp.rv.terr", langue,
                                            " · ".join(terr))))
            # LE STATUT ET LA SOURCE SUR CHAQUE ENTRÉE, comme sur la fiche.
            # Une revue qui aligne douze titres sans dire d'où ils viennent
            # est une revue de presse au sens le plus creux du mot.
            out.append(("note", GB.dire("exp.statut", langue,
                                        f.get("statut_nom") or "",
                                        f.get("source_nom") or "")))

    # ── CE QUE LA PÉRIODE NE DIT PAS ──────────────────────────────────────
    absences = []
    if revue.get("muets"):
        absences.append(GB.dire("exp.rv.muets", langue,
                                " · ".join(m["nom"] for m in revue["muets"])))
    if revue.get("conventions_ecartees"):
        absences.append(GB.dire("exp.rv.conv", langue,
                                revue["conventions_ecartees"]))
    if revue.get("ecartees_sans_territoire"):
        absences.append(GB.dire("exp.rv.hors", langue,
                                revue["ecartees_sans_territoire"]))
    if revue.get("ecartees_france"):
        absences.append(GB.dire("exp.rv.fr", langue, revue["ecartees_france"]))
    if absences:
        out.append(("titre2", GB.dire("exp.rv.absences", langue)))
        for a in absences:
            out.append(("note", a))

    # ── LES DEUX RUBRIQUES QUI NE SE DÉRIVENT PAS ─────────────────────────
    out.append(("titre2", GB.dire("exp.rv.signees", langue)))
    for r in revue.get("rubriques") or []:
        out.append(("chapeau", r["nom"]))
        out.append(("note", r["dit"]))
        if not r["n"]:
            out.append(("corps", r["vide_motif"]))
            out.append(("note", r["ce_qu_il_faudrait"]))
            continue
        for piece in r["pieces"]:
            out.append(("chapeau", piece.get("titre") or ""))
            if piece.get("chapeau"):
                out.append(("corps", piece["chapeau"]))
            if piece.get("texte"):
                out.append(("corps", piece["texte"]))
            if piece.get("interlocuteur"):
                out.append(("note", GB.dire(
                    "exp.rv.entretien", langue, piece["interlocuteur"],
                    piece.get("fonction") or "",
                    GB.date(piece.get("date_entretien"), langue))))
            # LA SIGNATURE N'EST PAS UNE MENTION LÉGALE EN PIED : elle est ce
            # qui distingue ce texte de tout le reste du document, qui est
            # dérivé. Elle voyage donc avec la pièce.
            out.append(("note", GB.dire("exp.rv.signe", langue,
                                        piece.get("auteur") or "",
                                        GB.date(piece.get("date"), langue))))
            if piece.get("methode"):
                out.append(("note", piece["methode"]))

    pied = GB.dire("exp.pied", langue,
                   GB.date(datetime.now(timezone.utc).date().isoformat(), langue))
    if url_revue:
        pied += " · %s" % url_revue
    out.append(("pied", pied))
    out.append(("pied", GB.dire("exp.rv.pied.regle", langue)))
    out.append(("pied", GB.dire("exp.langue." + langue, langue)))
    return out


def docx_revue(revue, url_revue=None, langue="fr"):
    return _docx(blocs_revue(revue, url_revue, langue))


def pdf_revue(revue, url_revue=None, langue="fr"):
    return _pdf(blocs_revue(revue, url_revue, langue))


# ── WORD ──────────────────────────────────────────────────────────────────
# ÉCRIT AVEC LA BIBLIOTHÈQUE STANDARD, et c'est un choix. Un `.docx` est une
# archive ZIP de trois fichiers XML ; l'écrire à la main évite une dépendance
# de plus sur un site qui en compte quatre, et surtout évite un format
# intermédiaire qui déciderait à notre place de ce qui est un titre.

_STYLES = {
    "entete":  ("18", "808080", False, "240"),
    "titre":   ("32", "14110D", True,  "120"),
    "date":    ("18", "75695A", False, "240"),
    "chapeau": ("22", "3E362B", False, "240"),
    "titre2":  ("24", "9E1F14", True,  "300"),
    "corps":   ("21", "14110D", False, "160"),
    "note":    ("17", "75695A", False, "120"),
    "pied":    ("16", "93866F", False, "100"),
}


def _p(genre, texte):
    taille, couleur, gras, apres = _STYLES.get(genre, _STYLES["corps"])
    return (
        '<w:p><w:pPr><w:spacing w:after="%s"/></w:pPr>'
        '<w:r><w:rPr><w:rFonts w:ascii="Liberation Serif" '
        'w:hAnsi="Liberation Serif"/><w:sz w:val="%s"/><w:color w:val="%s"/>%s'
        '</w:rPr><w:t xml:space="preserve">%s</w:t></w:r></w:p>'
        % (apres, taille, couleur, "<w:b/>" if gras else "", _x(texte))
    )


def docx(fiche, url_fiche=None, langue="fr"):
    """Rend les octets d'un `.docx` que Word, LibreOffice et Pages ouvrent."""
    return _docx(blocs(fiche, url_fiche, langue))


def _docx(lot):
    """LE RENDU WORD, UNE SEULE FOIS POUR TOUS LES DOCUMENTS.

    La fiche et la revue sont deux COMPOSITIONS différentes ; elles n'ont
    aucune raison d'être deux MISES EN PAGE différentes. Deux renderers
    auraient divergé exactement comme deux compositions l'auraient fait —
    c'est l'argument écrit au-dessus de `blocs()`, et il vaut d'un cran
    au-dessus."""
    corps = "".join(_p(g, t) for g, t in lot if t)
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/'
        'wordprocessingml/2006/main"><w:body>%s'
        '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1400" w:right="1400" w:bottom="1400" w:left="1400"/>'
        '</w:sectPr></w:body></w:document>' % corps)

    types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/'
        'content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats'
        '-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.'
        'openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '</Types>')
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/'
        'relationships"><Relationship Id="rId1" Type="http://schemas.'
        'openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="word/document.xml"/></Relationships>')

    tampon = io.BytesIO()
    # LA DATE DES ENTRÉES EST FIGÉE : deux exports de la même fiche doivent
    # rendre des octets identiques. Un horodatage les rendrait différents, et
    # l'on ne pourrait plus vérifier qu'un fichier reçu n'a pas été retouché.
    with zipfile.ZipFile(tampon, "w", zipfile.ZIP_DEFLATED) as z:
        for nom, contenu in (("[Content_Types].xml", types),
                             ("_rels/.rels", rels),
                             ("word/document.xml", document)):
            info = zipfile.ZipInfo(nom, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, contenu.encode("utf-8"))
    return tampon.getvalue()


# ── PDF ───────────────────────────────────────────────────────────────────

_PDF_TAILLES = {"entete": 9, "titre": 19, "date": 9, "chapeau": 12,
                "titre2": 12, "corps": 10.5, "note": 8.5, "pied": 8}
_PDF_COULEURS = {"entete": (128, 128, 128), "titre": (20, 17, 13),
                 "date": (117, 105, 90), "chapeau": (62, 54, 43),
                 "titre2": (158, 31, 20), "corps": (20, 17, 13),
                 "note": (117, 105, 90), "pied": (147, 134, 111)}


def pdf_disponible():
    """Dit si l'export PDF peut réellement se faire, et pourquoi non le cas
    échéant. Un bouton qui rend une erreur cinq secondes après le clic est
    pire qu'un bouton absent."""
    try:
        import fpdf  # noqa: F401
    except ImportError:
        return False, ("La bibliothèque de composition PDF n'est pas "
                       "installée sur ce serveur.")
    if not os.path.exists(os.path.join(POLICES, "LiberationSerif-Regular.ttf")):
        return False, ("La police Unicode n'est pas au dépôt : sans elle, les "
                       "tirets cadratins et les guillemets français "
                       "deviendraient des points d'interrogation.")
    return True, ""


def pdf(fiche, url_fiche=None, langue="fr"):
    """Rend les octets d'un PDF A4.

    LA POLICE EST CELLE DU DÉPÔT, jamais celle du système. Les polices
    intégrées de fpdf2 sont en latin-1 : le corpus est plein de tirets
    cadratins et de guillemets français qu'il ne porte pas, et ils
    sortiraient en points d'interrogation — un défaut invisible ici, visible
    par le seul lecteur qui ouvre le fichier.
    """
    return _pdf(blocs(fiche, url_fiche, langue))


def _pdf(lot):
    """LE RENDU PDF, UNE SEULE FOIS POUR TOUS LES DOCUMENTS — même argument
    que `_docx`."""
    ok, pourquoi = pdf_disponible()
    if not ok:
        raise RuntimeError(pourquoi)
    from fpdf import FPDF

    d = FPDF(format="A4")
    d.set_auto_page_break(True, margin=20)
    d.add_font("lib", "", os.path.join(POLICES, "LiberationSerif-Regular.ttf"))
    d.add_font("lib", "B", os.path.join(POLICES, "LiberationSerif-Bold.ttf"))
    d.set_margins(20, 20, 20)
    d.add_page()

    for genre, texte in lot:
        if not texte:
            continue
        gras = genre in ("titre", "titre2")
        d.set_font("lib", "B" if gras else "", _PDF_TAILLES.get(genre, 10.5))
        d.set_text_color(*_PDF_COULEURS.get(genre, (20, 17, 13)))
        if genre == "titre2":
            d.ln(3)
        d.multi_cell(0, _PDF_TAILLES.get(genre, 10.5) * 0.52, texte)
        d.ln(1.4 if genre in ("entete", "note", "pied") else 2.6)
    return bytes(d.output())


def sante():
    ok, pourquoi = pdf_disponible()
    return {
        "module": "exporter", "version": VERSION,
        "formats": ["docx"] + (["pdf"] if ok else []),
        "pdf_disponible": ok,
        "pdf_pourquoi_pas": pourquoi,
        "documents": ["fiche", "revue"],
        "portee": "Reprend une fiche PUBLIÉE telle quelle, avec son statut, "
                  "la nature de sa lecture, ce qu'on ne sait pas et sa "
                  "source — ou une REVUE de période, avec ce qu'elle compte, "
                  "ce qu'elle écarte et ses deux rubriques vides. Aucun texte "
                  "n'est réécrit, résumé ni raccourci : un document emporté "
                  "circule sans sa page, il doit porter de quoi en juger.",
    }
