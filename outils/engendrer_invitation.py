# -*- coding: utf-8 -*-
"""ENGENDRE LA PAGE D'INVITATION DEPUIS `evenement.py`.

    python3 outils/engendrer_invitation.py            # écrit formation-ia.html
    python3 outils/engendrer_invitation.py --verifier # dit si elle a dérivé

POURQUOI UN GÉNÉRATEUR, ET PAS UNE PAGE ÉCRITE À LA MAIN. Le programme de
l'après-midi existe déjà dans le bandeau de l'accueil. Une page d'invitation
recopiée à la main en ferait une seconde version, et la seconde version est
toujours celle qu'on oublie de corriger. Ici la page est DÉRIVÉE : changer
une heure dans `evenement.py` et rejouer cette commande suffit.

POURQUOI LA PAGE EST QUAND MÊME ÉCRITE SUR DISQUE, et non peinte par du
JavaScript. C'est l'adresse qu'on partage par courriel et sur LinkedIn : elle
doit s'afficher sans JavaScript, se laisser lire par un moteur de recherche et
rendre un aperçu correct quand quelqu'un colle le lien. Le prix de ce choix
est qu'une page engendrée peut vieillir dans le dépôt pendant que le module
change — c'est exactement ce que `--verifier` et la règle
`test_la_page_engendree_est_a_jour` refusent.
"""
import argparse
import html
import io
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)

import evenement as ev  # noqa: E402

CIBLE = os.path.join(RACINE, 'formation-ia.html')

e = html.escape


def _programme():
    out = []
    for heure, titre, detail, module in ev.PROGRAMME:
        classe = ' class="iv-mod"' if module else (
            ' class="iv-pause"' if 'Pause' in titre else '')
        d = ('<span>%s</span>' % e(detail)) if detail else ''
        out.append(
            '        <li%s><time datetime="%sT%s:00+01:00">%s</time>'
            '<div><strong>%s</strong>%s</div></li>'
            % (classe, ev.JOUR, heure, heure, e(titre), d))
    return '\n'.join(out)


def _pitch():
    """Le pitch, un paragraphe par ligne de `evenement.PITCH`."""
    return '\n'.join('      <p>%s</p>' % e(p)
                     for p in ev.PITCH.split('\n') if p.strip())


def _acquis():
    return '\n'.join(
        '        <li><strong>%s</strong><span>%s</span></li>' % (e(t), e(d))
        for t, d in ev.ACQUIS)


def _conditions():
    lignes = ['        <li><strong>%s</strong></li>' % e(ev.GRATUITE)]
    lignes += ['        <li>%s</li>' % e(c) for c in ev.CONDITIONS]
    return '\n'.join(lignes)


def _donnees_structurees():
    """L'événement en JSON-LD. UN LIEN PARTAGÉ EST D'ABORD UN APERÇU : sans
    ce bloc, un moteur voit une page parmi d'autres ; avec lui, il sait qu'il
    y a une date, un lieu et une inscription."""
    import json
    d = {
        '@context': 'https://schema.org',
        '@type': 'EducationEvent',
        'name': ev.TITRE,
        'description': ev.PUBLIC,
        'startDate': ev.DEBUT_UTC.isoformat().replace('+00:00', 'Z'),
        'endDate': ev.FIN_UTC.isoformat().replace('+00:00', 'Z'),
        'eventStatus': 'https://schema.org/EventScheduled',
        'eventAttendanceMode': 'https://schema.org/OfflineEventAttendanceMode',
        'inLanguage': 'fr',
        'isAccessibleForFree': True,
        'location': {
            '@type': 'Place',
            'name': ev.LIEU,
            'address': {
                '@type': 'PostalAddress',
                'streetAddress': ev.ADRESSE,
                'postalCode': ev.VILLE.split(' ')[0],
                'addressLocality': ev.VILLE.split(' ', 1)[1],
                'addressCountry': 'FR',
            },
        },
        'organizer': {'@type': 'Organization', 'name': 'CONSEILPREV',
                      'url': 'https://conseilprev.onrender.com'},
        'performer': {'@type': 'Person', 'name': ev.ANIMATEUR},
        'offers': {
            '@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR',
            'availability': 'https://schema.org/LimitedAvailability',
            'url': ev.MAILTO,
        },
    }
    return json.dumps(d, ensure_ascii=False, indent=2, sort_keys=True)


GABARIT = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{titre} — invitation du {jour_court} · CONSEILPREV</title>
<meta name="description" content="{description}">
<meta property="og:type" content="website">
<meta property="og:title" content="{titre} — {date_courte}">
<meta property="og:description" content="{description}">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" media="print" onload="this.media='all';this.onload=null" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;0,700;1,400&family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;0,700;1,400&family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap"></noscript>
<!-- ╔══════════════════════════════════════════════════════════════════╗
     ║  PAGE ENGENDRÉE — NE PAS LA MODIFIER À LA MAIN.                  ║
     ║  Source : evenement.py · Outil : outils/engendrer_invitation.py  ║
     ║  Une correction écrite ici serait perdue au prochain passage, et ║
     ║  la règle test_la_page_engendree_est_a_jour la refuse déjà.      ║
     ╚══════════════════════════════════════════════════════════════════╝ -->
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#0a0620; --bg2:#120830;
  --pm:#8b5cf6; --pl:#b48af7; --pp:#d4baff;
  --teal:#5eead4; --gold:#fbbf24;
  --wh:#f8f4ff; --mu:rgba(212,186,255,.62);
  --bdr:rgba(180,138,247,.20);
  --serif:"Cormorant Garamond",Georgia,serif;
  --mono:"Space Mono",ui-monospace,monospace;
  --sans:"DM Sans",system-ui,sans-serif;
}}
html{{scroll-behavior:smooth}}
body{{font-family:var(--sans);background:var(--bg);color:var(--wh);line-height:1.6;
  background-image:radial-gradient(900px 520px at 78% -8%,rgba(139,92,246,.20),transparent 60%),
                   radial-gradient(760px 440px at 8% 4%,rgba(217,70,239,.12),transparent 62%);
  background-repeat:no-repeat}}
a{{color:var(--pp)}}
.iv-haut{{display:flex;align-items:center;justify-content:space-between;gap:16px;
  padding:16px 24px;border-bottom:1px solid var(--bdr)}}
.iv-logo{{font-family:var(--serif);font-size:21px;color:var(--wh);text-decoration:none;letter-spacing:.01em}}
.iv-logo span{{color:var(--pl)}}
.iv-retour{{font-family:var(--mono);font-size:11.5px;color:var(--mu);text-decoration:none;
  border:1px solid var(--bdr);border-radius:7px;padding:6px 12px;white-space:nowrap}}
.iv-retour:hover{{color:var(--wh);border-color:var(--pl)}}
main{{max-width:960px;margin:0 auto;padding:40px 20px 72px}}
.iv-billet{{display:grid;grid-template-columns:132px minmax(0,1fr);gap:0;
  border:1px solid rgba(196,181,232,.30);border-radius:16px;overflow:hidden;
  background:linear-gradient(135deg,rgba(30,17,78,.94),rgba(19,11,54,.95));
  box-shadow:0 18px 44px rgba(4,2,22,.5)}}
.iv-souche{{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;
  padding:22px 10px;text-align:center;color:#fff;
  background:linear-gradient(165deg,#5b21b6,#7c3aed 52%,#a21caf);
  border-right:2px dashed rgba(255,255,255,.42)}}
.iv-s1,.iv-s3{{font-family:var(--mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase}}
.iv-s2{{font-family:var(--serif);font-weight:700;font-size:62px;line-height:.86}}
.iv-s4{{margin-top:9px;font-family:var(--mono);font-size:11px;font-weight:700;
  padding:3px 10px;border-radius:999px;background:rgba(10,6,32,.34);white-space:nowrap}}
.iv-corps{{padding:24px 26px 26px;min-width:0}}
.iv-sur{{display:flex;flex-wrap:wrap;align-items:center;gap:7px 10px;margin-bottom:8px;
  font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--teal)}}
.iv-puce{{font-size:10px;letter-spacing:.06em;text-transform:none;padding:2px 9px;border-radius:999px;
  border:1px solid rgba(251,191,36,.55);color:#fcd34d;background:rgba(251,191,36,.08)}}
h1{{font-family:var(--serif);font-weight:700;font-size:clamp(32px,5.2vw,50px);line-height:1.02;
  letter-spacing:-.015em;text-wrap:balance;margin-bottom:8px}}
.iv-public{{font-size:15px;color:rgba(232,224,255,.88);margin-bottom:14px}}
.iv-faits{{display:flex;flex-direction:column;gap:3px;font-size:14px;color:rgba(212,186,255,.84);margin-bottom:20px}}
.iv-ligne{{display:flex;align-items:flex-start;gap:8px}}
.iv-ico{{flex:none;margin-top:4px;opacity:.85}}
.iv-ligne strong{{color:#fff;font-weight:500}}
.iv-actions{{display:flex;flex-wrap:wrap;gap:10px;align-items:center}}
.iv-cta{{display:inline-flex;align-items:center;gap:8px;padding:13px 22px;border-radius:10px;
  font-weight:600;font-size:15px;color:#fff;text-decoration:none;
  background:linear-gradient(135deg,#7c3aed,#a855f7 55%,#db2777);
  box-shadow:0 6px 22px rgba(168,85,247,.42);transition:transform .16s,box-shadow .16s}}
.iv-cta:hover{{transform:translateY(-1px);box-shadow:0 10px 28px rgba(168,85,247,.58)}}
.iv-btn{{display:inline-flex;align-items:center;gap:7px;padding:11px 15px;border-radius:9px;
  border:1px solid var(--bdr);background:rgba(255,255,255,.05);color:#efe9ff;
  font:500 13px/1.2 var(--sans);text-decoration:none;cursor:pointer;transition:background .16s,border-color .16s}}
.iv-btn:hover{{background:rgba(255,255,255,.11);border-color:rgba(216,180,254,.62)}}
.iv-note{{width:100%;margin-top:2px;font-size:12.5px;color:var(--mu)}}
.iv-statut{{margin:12px 0 0;font-size:13px;color:var(--teal);min-height:1px}}
section{{margin-top:38px}}
h2{{font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.15em;
  text-transform:uppercase;color:#c4b5fd;margin-bottom:16px}}
.iv-pitch-corps{{max-width:66ch}}
.iv-pitch-corps p{{font-size:15.5px;line-height:1.72;color:rgba(235,228,255,.90)}}
.iv-pitch-corps p + p{{margin-top:11px}}
.iv-pitch-corps p:first-child{{font-size:17px;color:#fff}}
.iv-acquis{{list-style:none;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));
  gap:14px;margin-top:22px}}
.iv-acquis li{{border:1px solid var(--bdr);border-left:3px solid var(--pm);
  border-radius:10px;padding:14px 16px;background:rgba(14,8,42,.55)}}
.iv-acquis strong{{display:block;font-size:14px;font-weight:500;color:#fff;margin-bottom:4px}}
.iv-acquis span{{display:block;font-size:13px;line-height:1.55;color:rgba(212,186,255,.80)}}
.iv-grille{{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);gap:30px;align-items:start}}
.iv-frise{{list-style:none}}
.iv-frise li{{position:relative;display:grid;grid-template-columns:52px minmax(0,1fr);
  column-gap:26px;padding:7px 0}}
.iv-frise li::before{{content:"";position:absolute;left:64px;top:0;bottom:0;width:1px;background:var(--bdr)}}
.iv-frise li:first-child::before{{top:15px}}
.iv-frise li:last-child::before{{bottom:auto;height:15px}}
.iv-frise li::after{{content:"";position:absolute;left:60.5px;top:12px;width:8px;height:8px;
  border-radius:50%;background:#1c1150;border:1px solid rgba(196,181,232,.65)}}
.iv-frise li.iv-mod::after{{background:#a855f7;border-color:#e9d5ff}}
.iv-frise time{{font-family:var(--mono);font-size:12.5px;line-height:1.6;color:var(--teal);
  font-variant-numeric:tabular-nums}}
.iv-frise strong{{display:block;font-size:15px;font-weight:500;line-height:1.4;color:#fff}}
.iv-frise span{{display:block;margin-top:2px;font-size:13px;line-height:1.5;color:rgba(212,186,255,.78)}}
.iv-frise li.iv-pause strong{{font-weight:400;font-style:italic;color:var(--gold)}}
.iv-carte{{border:1px solid var(--bdr);border-radius:12px;padding:18px 20px;background:rgba(14,8,42,.6)}}
.iv-carte + .iv-carte{{margin-top:14px}}
.iv-anim{{display:flex;gap:13px;align-items:flex-start}}
.iv-ini{{flex:none;display:grid;place-items:center;width:44px;height:44px;border-radius:50%;
  background:linear-gradient(135deg,#7c3aed,#db2777);font-family:var(--serif);font-weight:700;
  font-size:18px;color:#fff}}
.iv-carte p{{font-size:13.5px;line-height:1.6;color:rgba(232,224,255,.88)}}
.iv-carte strong{{color:#fff;font-weight:500}}
address{{font-style:normal;font-size:14px;line-height:1.6;color:#f1ecff}}
.iv-acces{{margin-top:7px;font-size:13px;color:var(--mu)}}
.iv-liens{{margin-top:11px;font-size:13.5px;display:flex;flex-wrap:wrap;gap:4px 12px}}
.iv-liens a,.iv-contact a{{color:#d8b4fe;text-decoration:underline;
  text-decoration-color:rgba(216,180,254,.42);text-underline-offset:3px}}
.iv-liens a:hover,.iv-contact a:hover{{color:#fff;text-decoration-color:#fff}}
.iv-contact{{list-style:none;display:flex;flex-direction:column;gap:5px;font-size:13.5px}}
.iv-cond{{list-style:none;display:flex;flex-direction:column;gap:7px;font-size:14px;
  line-height:1.6;color:rgba(232,224,255,.88)}}
.iv-cond li{{position:relative;padding-left:18px}}
.iv-cond li::before{{content:"";position:absolute;left:3px;top:.62em;width:6px;height:6px;
  border-radius:50%;background:var(--gold)}}
.iv-cond strong{{color:#fcd34d;font-weight:500}}
.iv-pied-inv{{margin-top:34px;padding-top:20px;border-top:1px dashed rgba(196,181,232,.26);
  display:flex;flex-wrap:wrap;gap:10px 22px;align-items:center;font-size:13.5px;color:rgba(232,224,255,.88)}}
.iv-pied-inv a{{color:#d8b4fe;text-decoration:underline;text-decoration-color:rgba(216,180,254,.42);
  text-underline-offset:3px}}
.ft-mini{{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;
  gap:8px 18px;padding:16px 24px;border-top:1px solid var(--bdr);
  background:rgba(5,2,20,.92);font-family:var(--mono);font-size:10.5px;color:var(--mu)}}
.ft-mini a{{color:var(--teal);text-decoration:none}}
.ft-mini a:hover{{text-decoration:underline}}
a:focus-visible,button:focus-visible{{outline:2px solid var(--teal);outline-offset:2px;border-radius:4px}}
@media(max-width:820px){{
  .iv-grille{{grid-template-columns:1fr;gap:26px}}
  .iv-acquis{{grid-template-columns:1fr}}
}}
@media(max-width:560px){{
  main{{padding:26px 16px 56px}}
  .iv-billet{{grid-template-columns:1fr}}
  .iv-souche{{flex-direction:row;flex-wrap:nowrap;gap:10px;height:58px;padding:8px 16px;
    border-right:0;border-bottom:2px dashed rgba(255,255,255,.42)}}
  .iv-s2{{font-size:34px}}
  .iv-s4{{margin-top:0}}
  .iv-corps{{padding:18px 18px 20px}}
  .iv-cta{{width:100%;justify-content:center}}
  .iv-btn{{flex:1 1 calc(50% - 5px);justify-content:center}}
}}
@media(prefers-reduced-motion:reduce){{
  .iv-cta,.iv-btn{{transition:none}} .iv-cta:hover{{transform:none}}
  html{{scroll-behavior:auto}}
}}
</style>
</head>
<body>

<header class="iv-haut">
  <a class="iv-logo" href="/">CONSEIL<span>PREV</span></a>
  <a class="iv-retour" href="/">← Retour au site</a>
</header>

<main>
  <article class="iv-billet">
    <div class="iv-souche" aria-hidden="true">
      <span class="iv-s1">{jour_nom}</span>
      <span class="iv-s2">{jour_num}</span>
      <span class="iv-s3">{mois_an}</span>
      <span class="iv-s4">{plage}</span>
    </div>
    <div class="iv-corps">
      <p class="iv-sur">
        <span>Invitation gratuite · CONSEILPREV</span>
        <span class="iv-puce">Places limitées</span>
      </p>
      <h1>{titre}</h1>
      <p class="iv-public">{public}</p>
      <div class="iv-faits">
        <span class="iv-ligne"><svg class="iv-ico" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true" focusable="false"><rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg><strong>{date_lisible}</strong></span>
        <span class="iv-ligne"><svg class="iv-ico" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true" focusable="false"><path d="M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 0 1 13 0c0 5.4-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/></svg><span>{lieu}, {adresse}, {ville}</span></span>
      </div>
      <div class="iv-actions">
        <a class="iv-cta" id="iv-inscrire" href="{mailto}">S'inscrire gratuitement <span aria-hidden="true">→</span></a>
        <button type="button" class="iv-btn" id="iv-agenda"><svg class="iv-ico" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true" focusable="false"><rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4M12 13v5M9.5 15.5h5"/></svg>Ajouter à mon agenda</button>
        <a class="iv-btn" href="{itineraire}" target="_blank" rel="noopener">Itinéraire <span aria-hidden="true">↗</span></a>
        <p class="iv-note">Gratuit sur inscription par e-mail — <a href="#conditions">voir les conditions</a>.</p>
      </div>
      <p class="iv-statut" id="iv-statut" role="status" aria-live="polite"></p>
    </div>
  </article>

  <section class="iv-pitch">
    <h2>L'invitation en deux minutes</h2>
    <div class="iv-pitch-corps">
{pitch}
    </div>
    <ul class="iv-acquis">
{acquis}
    </ul>
  </section>

  <section>
    <div class="iv-grille">
      <div>
        <h2>Programme de l'après-midi</h2>
        <ol class="iv-frise">
{programme}
        </ol>
      </div>
      <div>
        <h2>Informations pratiques</h2>
        <div class="iv-carte">
          <div class="iv-anim">
            <span class="iv-ini" aria-hidden="true">{initiales}</span>
            <p><strong>{animateur}</strong>, {qualite}</p>
          </div>
        </div>
        <div class="iv-carte">
          <address>{lieu}<br>{adresse}<br>{ville}, {pays}</address>
          <p class="iv-acces">{acces}</p>
          <p class="iv-liens">
            <a href="{itineraire}" target="_blank" rel="noopener">Voir l'itinéraire ↗</a>
            <a href="{gcal}" target="_blank" rel="noopener">Google Agenda ↗</a>
          </p>
        </div>
        <div class="iv-carte">
          <ul class="iv-contact">
            <li><a href="{tel_lien}">{tel}</a></li>
            <li><a href="mailto:{courriel}">{courriel}</a></li>
            <li><a href="{linkedin}" target="_blank" rel="noopener">linkedin.com/in/cerfchristophe</a></li>
            <li><a href="{site1}" target="_blank" rel="noopener">i-aes.eu</a> · <a href="{site2}" target="_blank" rel="noopener">i-aes.com</a></li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <section id="conditions">
    <h2>Conditions</h2>
    <ul class="iv-cond">
{conditions}
    </ul>
  </section>

  <div class="iv-pied-inv">
    <span>Inscription par e-mail : <a href="{mailto}">{inscription}</a></span>
    <a href="{pdf}" download="Conseilprev_Invitation_Formation_IA_9_novembre_2026.pdf">Télécharger l'invitation (PDF)</a>
    <a href="/formations">Voir le catalogue de formations</a>
  </div>
</main>

<script type="application/ld+json">
{jsonld}
</script>

<!-- UNE BARRE, PAS LE PIED DE PAGE MARCHAND. Cette page a UNE action —
     s'inscrire. Les quarante sorties du pied partagé (offres, abonnements,
     lettre d'information) lui feraient concurrence, et c'est le propre d'une
     page d'invitation de n'en offrir qu'une. /footer-loader.js reste chargé :
     c'est lui qui pose le bandeau de consentement, comme partout ailleurs. -->
<div class="ft-mini">
  <span>© 2025 CONSEILPREV · Invitation du 9 novembre 2026 · <a href="/">conseilprev.onrender.com</a></span>
  <a href="/">← Retour au site</a>
</div>

<script src="/evenement.js" defer></script>
<script src="/formation-ia.page.js" defer></script>
<script src="/footer-loader.js"></script>
<!-- Les liens i-aes.com des contacts : si le site institutionnel ne répond
     pas, la bascule les réécrit plutôt que de laisser un lien mort. Chargée
     ici et non par le pied partagé, que cette page n'a pas. -->
<script src="/bascule.js" defer></script>
<script src="/guide.js" defer></script>
</body>
</html>
"""


def engendrer():
    return GABARIT.format(
        titre=e(ev.TITRE),
        public=e(ev.PUBLIC),
        description=e('%s — %s. %s, %s. %s'
                      % (ev.TITRE, ev.DATE_LISIBLE, ev.LIEU, ev.VILLE,
                         ev.GRATUITE)),
        jour_court='9 novembre 2026',
        date_courte=e('lundi 9 novembre 2026, 14h-18h, ' + ev.LIEU),
        jour_nom='Lundi', jour_num='9', mois_an='Novembre 2026',
        plage='14h – 18h',
        date_lisible=e(ev.DATE_LISIBLE),
        lieu=e(ev.LIEU), adresse=e(ev.ADRESSE), ville=e(ev.VILLE),
        pays=e(ev.PAYS), acces=e(ev.ACCES),
        mailto=e(ev.MAILTO), inscription=e(ev.INSCRIPTION),
        itineraire=e(ev.itineraire()), gcal=e(ev.google_agenda()),
        pdf=e(ev.PDF),
        animateur=e(ev.ANIMATEUR), qualite=e(ev.ANIMATEUR_QUALITE),
        initiales=''.join(m[0] for m in ev.ANIMATEUR.split()),
        tel=e(ev.TELEPHONE), tel_lien=e(ev.TELEPHONE_LIEN),
        courriel=e(ev.COURRIEL), linkedin=e(ev.LINKEDIN),
        site1=e(ev.SITES[0]), site2=e(ev.SITES[1]),
        pitch=_pitch(), acquis=_acquis(),
        programme=_programme(), conditions=_conditions(),
        jsonld=_donnees_structurees(),
    )


# ══════════════════════════════════════════════════════════════════════════
#  LE SCRIPT PARTAGÉ : /evenement.js
# ══════════════════════════════════════════════════════════════════════════
#  POURQUOI IL EXISTE. Le bouton « Ajouter à mon agenda » est sur le bandeau
#  de l'accueil ET sur la page d'invitation. Deux fabricants de fichier .ics
#  produiraient un jour deux séances différentes — un horaire corrigé d'un
#  côté, pas de l'autre, et personne pour s'en apercevoir avant que la salle
#  soit à moitié vide. Il n'y en a donc qu'un, et il est ENGENDRÉ depuis
#  `evenement.py`, comme la page.

CIBLE_JS = os.path.join(RACINE, 'evenement.js')

GABARIT_JS = r"""/* LES FAITS DE L'ÉVÉNEMENT, ET LE FICHIER D'AGENDA — FICHIER ENGENDRÉ.
   ════════════════════════════════════════════════════════════════════════
   Source : evenement.py · Outil : outils/engendrer_invitation.py
   NE PAS MODIFIER À LA MAIN : une correction écrite ici serait perdue au
   prochain passage, et une règle refuse déjà que ce fichier dérive.

   Deux écrans s'en servent : le bandeau de l'accueil et la page
   d'invitation /formation-ia. Un seul fabricant de .ics pour les deux, parce
   que deux fabricants finissent par poser deux séances différentes. */
(function () {{
  "use strict";

  var E = {{
    titre: {titre_js},
    public: {public_js},
    /* 14 h – 18 h à Paris le 9 novembre 2026, en heure d'hiver (UTC+1) :
       écrit en UTC pour que le fuseau du lecteur ne déplace rien. */
    debut: Date.UTC({an}, {mois0}, {jour_n}, {h_debut}, 0, 0),
    fin: Date.UTC({an}, {mois0}, {jour_n}, {h_fin}, 0, 0),
    lieu: {lieu_js},
    adresse: {adresse_js},
    ville: {ville_js},
    acces: {acces_js},
    inscription: {inscription_js},
    animateur: {animateur_js},
    conditions: {conditions_js},
    page: {page_js},
    fichier: 'formation-ia-conseilprev-{jour_iso}.ics'
  }};

  function echapper(s) {{
    return String(s).replace(/\\/g, '\\\\').replace(/;/g, '\;')
      .replace(/,/g, '\\,').replace(/\n/g, '\\n');
  }}

  /* RFC 5545 §3.1 : 75 OCTETS par ligne, pas 75 caractères — « é » en vaut
     deux. La suite repart après CRLF et une espace. */
  function plier(ligne) {{
    var morceaux = ligne.match(/[\uD800-\uDBFF][\uDC00-\uDFFF]|[\s\S]/g) || [];
    var out = [], cour = '', n = 0;
    morceaux.forEach(function (c) {{
      var o = encodeURIComponent(c).replace(/%[0-9A-F]{{2}}/gi, 'x').length;
      if (n + o > 75) {{ out.push(cour); cour = ' ' + c; n = 1 + o; }}
      else {{ cour += c; n += o; }}
    }});
    out.push(cour);
    return out.join('\r\n');
  }}

  function horodatage(t) {{
    return new Date(t).toISOString().replace(/[-:]/g, '').replace(/\.\d{{3}}/, '');
  }}

  E.lieuComplet = function () {{ return E.lieu + ', ' + E.adresse + ', ' + E.ville; }};

  E.description = function () {{
    return E.public + '.\n'
      + 'Animée par ' + E.animateur + ', CEO de CONSEILPREV.\n'
      + 'Gratuit sur inscription : ' + E.inscription + '\n'
      + E.acces + '\n'
      + 'Conditions : ' + E.conditions.join(' ');
  }};

  E.ics = function () {{
    return [
      'BEGIN:VCALENDAR', 'VERSION:2.0',
      'PRODID:-//CONSEILPREV//Invitation formation IA//FR',
      'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
      'BEGIN:VEVENT',
      'UID:formation-ia-{jour_iso}@conseilprev',
      'DTSTAMP:' + horodatage(Date.now()),
      'DTSTART:' + horodatage(E.debut),
      'DTEND:' + horodatage(E.fin),
      'SUMMARY:' + echapper(E.titre + ' — formation CONSEILPREV'),
      'LOCATION:' + echapper(E.lieuComplet()),
      'DESCRIPTION:' + echapper(E.description()),
      'STATUS:CONFIRMED',
      'BEGIN:VALARM', 'ACTION:DISPLAY', 'TRIGGER:-P1D',
      'DESCRIPTION:' + echapper('Formation IA demain à 14h — ' + E.lieu),
      'END:VALARM',
      'END:VEVENT', 'END:VCALENDAR'
    ].map(plier).join('\r\n') + '\r\n';
  }};

  /* Le téléchargement est fabriqué dans la page : aucun aller-retour, donc
     rien à attendre et rien qui puisse répondre 404 le jour J. */
  E.telechargerIcs = function () {{
    var url = URL.createObjectURL(
      new Blob([E.ics()], {{ type: 'text/calendar;charset=utf-8' }}));
    var a = document.createElement('a');
    a.href = url;
    a.download = E.fichier;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () {{ URL.revokeObjectURL(url); }}, 10000);
  }};

  window.CPEvenement = E;
}})();
"""


def engendrer_js():
    import json
    j = lambda v: json.dumps(v, ensure_ascii=False)  # noqa: E731
    return GABARIT_JS.format(
        titre_js=j(ev.TITRE), public_js=j(ev.PUBLIC),
        an=ev.DEBUT_UTC.year, mois0=ev.DEBUT_UTC.month - 1,
        jour_n=ev.DEBUT_UTC.day,
        h_debut=ev.DEBUT_UTC.hour, h_fin=ev.FIN_UTC.hour,
        lieu_js=j(ev.LIEU), adresse_js=j(ev.ADRESSE), ville_js=j(ev.VILLE),
        acces_js=j(ev.ACCES), inscription_js=j(ev.INSCRIPTION),
        animateur_js=j(ev.ANIMATEUR),
        conditions_js=j(list(ev.CONDITIONS)),
        page_js=j(ev.PAGE), jour_iso=ev.JOUR,
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--verifier', action='store_true',
                    help="ne rien écrire : dire si la page a dérivé")
    a = ap.parse_args()
    attendus = ((CIBLE, engendrer()), (CIBLE_JS, engendrer_js()))
    if a.verifier:
        derives = [c for c, att in attendus
                   if (io.open(c, encoding='utf-8').read()
                       if os.path.exists(c) else '') != att]
        if not derives:
            print('formation-ia.html et evenement.js : à jour')
            return 0
        print('a DÉRIVÉ de evenement.py : %s — rejouez '
              '« python3 outils/engendrer_invitation.py »'
              % ', '.join(os.path.basename(c) for c in derives))
        return 1
    for cible, att in attendus:
        io.open(cible, 'w', encoding='utf-8').write(att)
        print('écrit : %s (%d octets)'
              % (os.path.basename(cible), len(att.encode('utf-8'))))
    return 0


if __name__ == '__main__':
    sys.exit(main())
