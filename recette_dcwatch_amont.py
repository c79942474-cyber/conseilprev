# -*- coding: utf-8 -*-
"""LA BASE DCWATCH, CONFRONTEE A SON AMONT. Le seul endroit qui ouvre une socket.

CE QUE CETTE RECETTE ETABLIT, ET DANS CET ORDRE :

  1. LE DEPOT EST-IL CELUI QUI A ETE INSTRUIT ? Avant toute question sur
     l'amont : si le fichier local a change, tous les chiffres publies depuis
     reposent sur autre chose que ce qui a ete documente. Cela se voit sans
     reseau, et cela se voit en premier.

  2. L'ETIQUETTE A-T-ELLE BOUGE ? Le depot est fige sur 2026.04.09. Le fichier
     telecharge A CETTE ETIQUETTE doit lui etre identique, octet pour octet. Une
     difference ici ne veut pas dire « nouvelle version » : elle veut dire
     qu'une reference que l'on croyait figee ne l'etait pas. C'est plus grave
     qu'une derive, et cela se dit autrement.

  3. DE COMBIEN L'AMONT A-T-IL DERIVE ? Le HEAD de `main`, compare au depot, en
     CONSEQUENCES et non en octets. « Les fichiers different » n'aide personne a
     decider ; « trois enregistrements de plus, un site en exploitation de
     moins » se discute — d'autant que ce nombre est publie et qu'une regle de
     lecture s'appuie dessus.

CE QU'ELLE NE FAIT PAS, ET C'EST DELIBERE.

ELLE NE DEPOSE RIEN. Rafraichir la base deplacerait des chiffres deja publies :
« environ trois cent cinquante centres » se lit aujourd'hui sur 342 lignes en
exploitation, et l'amont en porte 341. Le rafraichissement est une action
explicite — `--deposer <etiquette>` — qui reecrit le CSV, regenere le tableau
d'attribution, et imprime ce qui bouge. Jamais un effet de bord d'un controle.

ELLE NE SE TAIT PAS. Reseau injoignable, refuse par la politique de sortie,
etiquette introuvable : elle le dit et sort en echec. Une recette muette se lit
comme un controle vert, et c'est la pire des reponses — celle qui laisse croire
qu'on a verifie.

  POUR L'EXECUTER :  python3 recette_dcwatch_amont.py
  POUR DEPOSER    :  python3 recette_dcwatch_amont.py --deposer 2026.04.09
"""
import datetime
import io
import os
import sys
import urllib.error
import urllib.request

import dcwatch
import dcwatch_import as I

ICI = os.path.dirname(os.path.abspath(__file__))
# Le dossier du depot. Surchargeable, pour qu'une regle puisse eprouver le
# cas « base absente » pour de vrai — une regle qui se contente de lire le
# code ne verifie pas que la recette sort bien en echec.
DOSSIER = os.environ.get('DCWATCH_DOSSIER') or os.path.join(ICI, 'dcwatch')
DELAI = 30

ko = 0


def ok(nom, cond, detail=""):
    global ko
    print("  " + ("OK " if cond else "KO ") + "  " + nom + (" — " + str(detail) if detail else ""))
    if not cond:
        ko += 1


def titre(t):
    print("\n== " + t + " ==\n")


def telecharger(url):
    """Le SEUL appel reseau de tout le depot pour cette source.

    Rend (octets, None) ou (None, raison). Une raison lisible, pas une trace :
    « la politique de sortie refuse gitlab.com » se comprend, « HTTPError 403 »
    se cherche."""
    try:
        with urllib.request.urlopen(url, timeout=DELAI) as r:
            return r.read(), None
    except urllib.error.HTTPError as e:
        if e.code in (403, 405, 407):
            return None, ("refuse par la politique de sortie du poste (HTTP %d). "
                          "Ce n'est pas une panne : c'est un refus, et il se "
                          "leve dans la configuration reseau, pas ici." % e.code)
        if e.code == 404:
            return None, "introuvable en amont (HTTP 404) : etiquette ou fichier inconnu"
        return None, "amont en erreur (HTTP %d)" % e.code
    except Exception as e:
        return None, "amont injoignable : %s" % str(e)[:120]


def lire_depot():
    chemin = os.path.join(DOSSIER, I.FICHIER)
    if not os.path.exists(chemin):
        return None
    with open(chemin, 'rb') as f:
        return f.read()


def deposer(octets, tag):
    """Reecrit la base ET son tableau d'attribution. Les deux, ou aucun : un
    fichier rafraichi sous une attribution perimee est pire qu'un fichier
    ancien, parce qu'il ment sur lui-meme."""
    chemin = os.path.join(DOSSIER, I.FICHIER)
    attribution = os.path.join(DOSSIER, 'ATTRIBUTION.md')
    texte = io.open(attribution, encoding='utf-8').read()
    neuf = I.remplacer_table(texte, I.table_attribution(
        octets, tag=tag,
        le=datetime.date.today().strftime('%d/%m/%Y')))
    if neuf is None:
        print("  KO    ATTRIBUTION.md n'a plus ses marqueurs de tableau : rien n'est depose")
        return False
    with open(chemin, 'wb') as f:
        f.write(octets)
    io.open(attribution, 'w', encoding='utf-8').write(neuf)
    print("  base et attribution reecrites. IL RESTE A FAIRE, A LA MAIN :")
    print("    - porter la nouvelle empreinte dans dcwatch.EMPREINTE ;")
    print("    - relire les chiffres publies qui bougent (voir l'ecart ci-dessus) ;")
    print("    - relancer recette_carte_dcwatch.py et la suite complete.")
    return True


# ── 0. Le depot, avant toute question sur l'amont ──────────────────────────
titre("0. Le depot local est-il celui qui a ete instruit ?")

local = lire_depot()
ok("la base est deposee", local is not None, os.path.join('dcwatch', I.FICHIER))
if local is None:
    print("\nSans base locale, il n'y a rien a comparer. Aucun controle n'est "
          "presente comme vert.\n")
    sys.exit(1)

e = dcwatch.etat()
ok("son empreinte est celle qui a ete documentee", e['empreinte_conforme'], e['dit'])
r = I.resume(local)
print("  %d enregistrements, %d France, %d en exploitation, %d en projet, %d doublon(s)"
      % (r['enregistrements'], r['france'], r['exploitation'], r['projets'],
         r['doublons_france']))
print("  " + dcwatch.MENTION)


# ── 1. L'etiquette figee ───────────────────────────────────────────────────
titre("1. L'etiquette %s, telle qu'elle est en amont" % I.TAG)

tag_octets, raison = telecharger(I.url(I.TAG))
ok("l'etiquette est joignable", tag_octets is not None, raison or I.url(I.TAG))
if tag_octets is not None:
    c = I.comparer(local, tag_octets)
    # LE DETAIL DOIT DIRE CE QUI EST, PAS RECITER L'AVERTISSEMENT. Une ligne
    # verte suivie d'une phrase alarmante se lit de travers : c'est le meme
    # defaut qu'une mention qui decrit autre chose que la realite.
    ok("le depot lui est identique, octet pour octet", c['identiques'],
       ("%d octets, meme empreinte" % r['octets']) if c['identiques'] else
       ("UNE REFERENCE FIGEE A BOUGE — ce n'est pas une nouvelle version, c'est "
        "l'etiquette elle-meme qui a ete deplacee : %s"
        % (c['ecarts'] or 'contenu different a nombre egal')))


# ── 2. La derive de l'amont ────────────────────────────────────────────────
titre("2. Ce que porte le HEAD de main, et ce que cela deplacerait")

main_octets, raison = telecharger(I.url('main'))
ok("le HEAD de main est joignable", main_octets is not None, raison or '')
derive = None
if main_octets is not None:
    derive = I.comparer(local, main_octets)
    a, b = derive['depot'], derive['amont']
    print("  %-18s %8s %8s %9s" % ('', 'depot', 'amont', 'ecart'))
    for cle in ('enregistrements', 'france', 'exploitation', 'projets', 'doublons_france'):
        d = b[cle] - a[cle]
        print("  %-18s %8d %8d %9s" % (cle, a[cle], b[cle], ('%+d' % d) if d else '—'))
    if derive['identiques']:
        print("\n  L'amont n'a pas bouge depuis le depot.")
    else:
        print("\n  L'AMONT A BOUGE. Ce n'est pas un defaut : c'est une decision a "
              "prendre.\n  Le depot reste sur %s tant qu'elle n'est pas prise, et "
              "les chiffres\n  publies restent coherents entre eux." % I.TAG)
        if derive['ecarts'].get('exploitation'):
            print("  A SURVEILLER : « environ trois cent cinquante » se lit "
                  "aujourd'hui sur\n  %d lignes en exploitation ; l'amont en porte %d."
                  % (a['exploitation'], b['exploitation']))
    # LA DERIVE N'EST PAS UN ECHEC. Une base amont qui avance est normale ; ce
    # qui serait fautif, c'est de ne pas le savoir.
    ok("la derive est mesuree et nommee", True,
       "%d ecart(s) de comptage" % len(derive['ecarts']))


# ── 3. Le depot, sur demande explicite ─────────────────────────────────────
if '--deposer' in sys.argv:
    i = sys.argv.index('--deposer')
    tag = sys.argv[i + 1] if len(sys.argv) > i + 1 else I.TAG
    titre("3. Depot demande explicitement : etiquette %s" % tag)
    octets, raison = telecharger(I.url(tag))
    if octets is None:
        ok("l'etiquette demandee est joignable", False, raison)
    else:
        deposer(octets, tag)
else:
    titre("3. Aucun depot")
    print("  Cette recette ne remplace jamais la base d'elle-meme : un "
          "rafraichissement\n  silencieux deplacerait des chiffres deja publies. "
          "Pour le faire :\n\n    python3 recette_dcwatch_amont.py --deposer %s\n"
          % I.TAG)

print((str(ko) + " controle(s) en echec" if ko else "tout est vert") + "\n")
sys.exit(1 if ko else 0)
