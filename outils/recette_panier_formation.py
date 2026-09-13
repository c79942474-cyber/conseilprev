# -*- coding: utf-8 -*-
"""RECETTE — une commande, de une à quatre formations : la première est offerte.

CE QUE CETTE RECETTE ÉTABLIT, ET QU'AUCUNE RÈGLE NE PEUT ÉTABLIR SEULE. Les
règles de `tests/` mesurent les routes ; elles ne voient pas ce que le CLIENT
VOIT. Le total affiché vient du serveur — la page ne peut pas le calculer, elle
ignore si ce client a déjà reçu sa séance offerte — et un écart entre l'écran et
la caisse ne tomberait sous aucune règle de route.

Le banc coche 1, puis 2, 3, 4 formations dans un VRAI navigateur sur la VRAIE
application, pose une date sur chacune, désigne l'offerte, lit l'écran, puis va
jusqu'à l'envoi et relève ce qui part à la caisse.

CE QUI EST ATTENDU : n formations cochées ⇒ une offerte et (n − 1) payantes à
800 € HT, et exactement (n − 1) lignes chez Stripe — jamais la séance offerte.

ELLE DÉSIGNE LA DERNIÈRE COMME OFFERTE, PAS LA PREMIÈRE. Si la gratuité tombait
sur la première quoi qu'on choisisse — le défaut corrigé en septembre — un banc
qui désignerait toujours la première serait vert sans rien prouver.

    python3 outils/recette_panier_formation.py
"""
import re, sys, threading, time, types, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CREES = []



def faux_stripe():
    st = types.ModuleType("stripe")
    st.api_key = None
    st.max_network_retries = 0

    class _Sess:
        @staticmethod
        def create(**kw):
            CREES.append(kw)
            return {"id": "cs_test_banc", "url": "https://checkout.stripe.test/cs_test_banc"}

    class _Checkout:
        Session = _Sess

    class _TaxRate:
        @staticmethod
        def create(**kw):
            return {"id": "txr_banc"}

    st.checkout = _Checkout
    st.TaxRate = _TaxRate
    return st


sys.modules["stripe"] = faux_stripe()
os.environ["STRIPE_SECRET_KEY"] = "sk_test_banc"

import app as A

# ══════════════════════════════════════════════════════════════════════════
#  CE BANC EFFACE LA TABLE DES RÉSERVATIONS. IL REFUSE DONC DE TOURNER AILLEURS
#  QUE SUR UNE BASE DE TRAVAIL.
# ══════════════════════════════════════════════════════════════════════════
# Un DELETE sans WHERE sur un registre de production effacerait les
# réservations de vrais clients — et la recette, étant une recette, serait
# lancée sans y penser. Le refus est explicite et nomme la raison.
if A.REGISTRE_USE_PG:
    sys.exit("REFUS : le registre pointe sur PostgreSQL. Cette recette EFFACE "
             "la table des réservations et ne doit tourner que sur la base de "
             "travail SQLite locale.")

conn = A.registre_get_db(); cur = conn.cursor()
A._formation_ia_table(cur, conn)
cur.execute("DELETE FROM formation_ia_resa")
conn.commit(); conn.close()

PORT = 5099
threading.Thread(target=lambda: A.app.run(host="127.0.0.1", port=PORT,
                                          debug=False, use_reloader=False),
                 daemon=True).start()
time.sleep(3)

from playwright.sync_api import sync_playwright

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
    pg = nav.new_page(viewport={"width": 1280, "height": 1000})
    erreurs = []
    pg.on("pageerror", lambda e: erreurs.append(str(e)))
    pg.goto("http://127.0.0.1:%d/formation" % PORT, wait_until="networkidle")
    pg.wait_for_selector(".subj", timeout=15000)

    cartes = pg.query_selector_all(".subj")
    print("formations au catalogue : %d\n" % len(cartes))

    for n in (1, 2, 3, 4):
        # On repart d'une page neuve : l'etat du panier vit dans la page.
        pg.goto("http://127.0.0.1:%d/formation" % PORT, wait_until="networkidle")
        pg.wait_for_selector(".subj", timeout=15000)
        cartes = pg.query_selector_all(".subj")
        for i in range(n):
            cartes[i].click()
            pg.wait_for_timeout(120)

        # Une date par seance, toutes differentes.
        #
        # ON REQUESTIONNE LE DOM A CHAQUE TOUR. `rendrePanier()` remplace tout
        # l innerHTML du panier des qu une date change : une poignee gardee
        # d un tour sur l autre pointe un element detache, et le banc tombe sur
        # une panne qui n est pas celle de l application.
        assert len(pg.query_selector_all("select.pan-date")) == n
        for k in range(n):
            sel = pg.query_selector_all("select.pan-date")
            vals = sel[k].eval_on_selector_all(
                "option", "os => os.map(o => o.value).filter(Boolean)")
            sel[k].select_option(vals[k])
            pg.wait_for_timeout(200)

        # On designe la DERNIERE comme offerte : si la gratuite tombait sur la
        # premiere quoi qu'on fasse, c'est ici que cela se verrait.
        radios = pg.query_selector_all('input[name="pan-gratuit"]')
        radios[-1].click()
        pg.wait_for_timeout(600)

        total = (pg.text_content("#rc-total") or "").strip()
        lignes = pg.eval_on_selector_all(
            ".pan-ligne",
            "ls => ls.map(l => ({titre: l.querySelector('.pan-titre').textContent.trim(),"
            " offerte: l.classList.contains('offerte')}))")
        attendu = (n - 1) * 800
        # LIRE ZERO N EST PAS LIRE RIEN. L ecran n ecrit pas « 0 € HT » quand
        # tout est offert : il ecrit « Aucun montant — seance offerte ». Mon
        # analyseur comptait cette phrase comme un ecart — un faux positif de
        # l appareil de mesure, pas de la page.
        if "ucun montant" in total:
            vu = 0
        else:
            chiffres = re.sub(r"[^0-9]", "", total.split("€")[0])
            vu = int(chiffres) if chiffres else -1

        print("── %d formation(s) cochee(s) ──────────────────────────" % n)
        for l in lignes:
            print("   %-26s %s" % (l["titre"][:26], "OFFERTE" if l["offerte"] else "payante"))
        print("   ecran #rc-total : %s" % total)
        print("   attendu         : %d € HT  (%d payante(s) x 800)" % (attendu, n - 1))
        print("   verdict         : %s\n" % ("OK" if vu == attendu else "ECART ←←←"))

    # ══════════════════════════════════════════════════════════════════
    #  ET ON ENVOIE — quatre formations, la TROISIEME designee offerte
    # ══════════════════════════════════════════════════════════════════
    # Ce que rien d autre ne montre : ce qui part REELLEMENT a la caisse quand
    # le geste vient d un vrai navigateur, sur un vrai formulaire.
    del CREES[:]
    conn = A.registre_get_db(); cur = conn.cursor()
    cur.execute("DELETE FROM formation_ia_resa"); conn.commit(); conn.close()

    pg.goto("http://127.0.0.1:%d/formation" % PORT, wait_until="networkidle")
    pg.wait_for_selector(".subj", timeout=15000)
    for i in range(4):
        pg.query_selector_all(".subj")[i].click()
        pg.wait_for_timeout(120)
    for k in range(4):
        sel = pg.query_selector_all("select.pan-date")
        vals = sel[k].eval_on_selector_all(
            "option", "os => os.map(o => o.value).filter(Boolean)")
        sel[k].select_option(vals[k])
        pg.wait_for_timeout(200)
    pg.query_selector_all('input[name="pan-gratuit"]')[2].click()
    pg.wait_for_timeout(600)

    pg.fill('[name="prenom"]', "Alex")
    pg.fill('[name="nom"]', "Durand")
    pg.fill('[name="email"]', "banc@ex.fr")
    pg.fill('[name="telephone"]', "+33 6 12 34 56 78")
    pg.fill('[name="entreprise"]', "BANC SAS")
    pg.fill('[name="siret"]', "910000888")
    pg.fill('[name="lieu"]', "12 rue d Essai, 75002 Paris")
    pg.wait_for_timeout(200)
    print("── ENVOI : 4 formations, la TROISIEME designee offerte ──────")
    print("   ecran avant envoi : %s" % (pg.text_content("#rc-total") or "").strip())

    pg.click("#fo-submit")
    pg.wait_for_timeout(3000)

    conn = A.registre_get_db(); cur = conn.cursor()
    cur.execute("SELECT sujet, gratuit, montant_cents, statut FROM formation_ia_resa ORDER BY id")
    base = [dict(x) for x in cur.fetchall()]
    conn.close()
    for b in base:
        print("   en base         : %-24s %s %4d €  [%s]"
              % (b["sujet"], "OFFERTE" if b["gratuit"] else "payante",
                 (b["montant_cents"] or 0) // 100, b["statut"]))

    li = (CREES[0].get("line_items") if CREES else []) or []
    tot = 0
    print("   lignes a la caisse : %d" % len(li))
    for x in li:
        pd = x.get("price_data") or {}
        nom = ((pd.get("product_data") or {}).get("name") or "?")
        ua = int(pd.get("unit_amount") or 0)
        tot += ua * int(x.get("quantity") or 1)
        print("      · %-46s %4d €" % (nom[:46], ua // 100))
    print("   total caisse       : %d € HT" % (tot // 100))
    print("   offerte facturee ? : %s"
          % ("NON — correct" if len(li) == 3 and tot == 240000 else "A VERIFIER"))

    print("\nerreurs JavaScript pendant le banc :", erreurs or "aucune")
    nav.close()
