import os, requests
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY', 'f5NFzuhlT1830mek1QYix3ofyBS3Y8gf')
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"

SYSTEM_PROMPT = """Tu es un expert senior en IA, conformité réglementaire et cybersécurité chez CONSEILPREV, startup parisienne spécialisée en Business Unit IA · Data · Cyber.

Ton rôle : guider les visiteurs (entreprises, investisseurs, DSI, DPO, RSSI) avec des réponses précises, professionnelles et actionnables en français.

Tes domaines d'expertise :
- IA Act européen : classification des risques, obligations, systèmes interdits
- ISO 42001 : management IA, certification, documentation
- NIS2 : entités essentielles, mesures de sécurité, délais de notification
- ISO 27001 : SMSI, analyse de risques, certification
- DORA : résilience opérationnelle numérique, secteur financier
- RGPD : AIPD, violations, DPO, Privacy by Design
- 8 risques systémiques IA : juridictionnel, économique, data, opérationnel, géopolitique, cyber, supply chain, environnemental
- Gouvernance IA/Cyber : GRC, politiques, comités, KPIs

Offre CONSEILPREV : Audit IA & Cyber, 8 risques systémiques, Plan conformité 5 étapes, Gouvernance GRC.

Style : professionnel, structuré avec des listes courtes, concis (max 280 mots). Réponds toujours en français. Termine en proposant d'approfondir ou contacter contact@i-aes.com."""


import feedparser, time

RSS_SOURCES = [
    {"name": "ActuIA",          "url": "https://www.actuia.com/feed/",                         "cat": "ai",    "ico": "🤖"},
    {"name": "ANSSI",           "url": "https://cyber.gouv.fr/feed",                            "cat": "secu",  "ico": "🛡️"},
    {"name": "CNIL",            "url": "https://www.cnil.fr/fr/rss.xml",                        "cat": "regl",  "ico": "🔒"},
    {"name": "LMI",             "url": "https://www.lemondeinformatique.fr/rss/rss-actu.xml",   "cat": "innov", "ico": "💻"},
    {"name": "Usine Digitale",  "url": "https://www.usine-digitale.fr/rss/all",                "cat": "innov", "ico": "🏭"},
    {"name": "AI Act EU",       "url": "https://artificialintelligenceact.eu/feed/",            "cat": "regl",  "ico": "⚖️"},
    {"name": "EU Digital",      "url": "https://digital-strategy.ec.europa.eu/en/rss.xml",     "cat": "intl",  "ico": "🇪🇺"},
    {"name": "Cybersec-info",   "url": "https://cybersecurite-info.fr/feed/",                  "cat": "secu",  "ico": "🔐"},
    {"name": "Infosecurity Mag", "url": "https://www.infosecurity-magazine.com/rss/news/",        "cat": "secu",  "ico": "🔏"},
]

_news_cache = {"data": [], "ts": 0}
CACHE_TTL = 600  # 10 min

import re as _re
def _detect_cat(title, default_cat):
    t = (title or "").lower()
    if _re.search(r"mistral|gemini|gpt|llm|ia g.n.r|generat|intelligence artif", t): return "ai"
    if _re.search(r"france|cnil|anssi|gouvernement|s.nat|assemblée|dinum", t): return "fr"
    if _re.search(r"rgpd|gdpr|ia act|nist|iso|conformit|r.glement|directive", t): return "regl"
    if _re.search(r"cyber|attaque|malware|ransomware|phish|s.curit|vulnerab|breach|faille", t): return "secu"
    if _re.search(r"europe|usa|chine|international|mondial|onu|ocde|g7", t): return "intl"
    return default_cat

@app.route('/api/news')
def news():
    global _news_cache
    now = time.time()
    if now - _news_cache["ts"] < CACHE_TTL and _news_cache["data"]:
        return jsonify({"items": _news_cache["data"], "cached": True, "count": len(_news_cache["data"])})

    all_items = []
    for src in RSS_SOURCES:
        try:
            feed = feedparser.parse(src["url"])
            for entry in (feed.entries or [])[:8]:
                title = entry.get("title", "").strip()
                if not title: continue
                link  = entry.get("link") or entry.get("id") or "#"
                pub   = entry.get("published") or entry.get("updated") or ""
                cat   = _detect_cat(title, src["cat"])
                all_items.append({
                    "title":  title,
                    "link":   link,
                    "date":   pub,
                    "source": src["name"],
                    "ico":    src["ico"],
                    "cat":    cat,
                })
        except Exception:
            pass

    # Trier par date desc, dédupliquer
    seen = set()
    unique = []
    for item in sorted(all_items, key=lambda x: x.get("date",""), reverse=True):
        key = item["title"][:60]
        if key not in seen:
            seen.add(key)
            unique.append(item)

    _news_cache = {"data": unique[:60], "ts": now}
    return jsonify({"items": unique[:60], "cached": False, "count": len(unique)})


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/datasets.json')
def datasets():
    return send_from_directory('.', 'datasets.json', mimetype='application/json')

@app.route('/demo')
def demo():
    return send_from_directory('.', 'demo.html')

@app.route('/accessibility')
def accessibility():
    return send_from_directory('.', 'accessibility.html')

@app.route('/aies')
def aies():
    return send_from_directory('.', 'aies.html')

@app.route('/donnees')
def donnees():
    return send_from_directory('.', 'donnees.html')

@app.route('/demo.mp4')
def demo_video():
    return send_from_directory('.', 'demo.mp4', mimetype='video/mp4')

@app.route('/hero-bg.jpg')
def hero_bg():
    return send_from_directory('.', 'hero-bg.jpg', mimetype='image/jpeg')

@app.route('/livre-blanc')
def livre_blanc():
    return send_from_directory('.', 'livre-blanc.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "version": "7.0", "model": "mistral"})

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_msg = data.get('message', '').strip()
        history  = data.get('history', [])

        if not user_msg:
            return jsonify({"error": "Message vide"}), 400

        # Construire les messages
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for h in history[-8:]:
            if h.get('role') in ('user', 'assistant') and h.get('content'):
                messages.append({"role": h['role'], "content": h['content']})
        messages.append({"role": "user", "content": user_msg})

        # Appel Mistral AI
        resp = requests.post(
            MISTRAL_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {MISTRAL_API_KEY}"
            },
            json={
                "model": "mistral-large-latest",
                "messages": messages,
                "max_tokens": 1024,
                "temperature": 0.7
            },
            timeout=30
        )

        if not resp.ok:
            err = resp.text[:200]
            return jsonify({"error": f"Mistral API {resp.status_code}: {err}"}), 500

        result = resp.json()
        reply = result['choices'][0]['message']['content']
        return jsonify({"reply": reply, "model": "mistral-large-latest"})

    except requests.Timeout:
        return jsonify({"error": "Délai d'attente dépassé, réessayez"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
