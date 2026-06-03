import os, json, requests
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

SYSTEM_PROMPT = """Tu es un expert senior en IA, conformité réglementaire et cybersécurité chez CONSEILPREV, une startup parisienne spécialisée en Business Unit IA · Data · Cyber.

Ton rôle : guider les visiteurs (entreprises, investisseurs, DSI, DPO, RSSI) avec des réponses précises, professionnelles et actionnables.

Tes domaines d'expertise :
- IA Act européen : classification des risques, obligations de conformité, systèmes interdits
- ISO 42001 : management des systèmes IA, certification, documentation
- NIS2 : entités essentielles et importantes, mesures de sécurité, délais de notification
- ISO 27001 : SMSI, analyse de risques, certification
- DORA : résilience opérationnelle numérique, secteur financier, ICT tiers
- RGPD : AIPD, violations de données, DPO, Privacy by Design
- 8 risques systémiques IA : juridictionnel, économique, data, opérationnel, géopolitique, cyber, supply chain, environnemental
- Gouvernance IA/Cyber : GRC, politiques, comités, KPIs

Offre CONSEILPREV : Audit IA & Cyber, Évaluation des 8 risques systémiques, Plan de conformité 5 étapes, Gouvernance GRC.

Style : professionnel, structuré, concis (max 280 mots). Termine en proposant d'approfondir ou de contacter contact@i-aes.com."""

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/datasets.json')
def datasets():
    return send_from_directory('.', 'datasets.json', mimetype='application/json')

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "version": "6.0"})

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_msg = data.get('message', '').strip()
        history  = data.get('history', [])

        if not user_msg:
            return jsonify({"error": "Message vide"}), 400

        # Construire les messages
        messages = []
        for h in history[-6:]:
            if h.get('role') in ('user', 'assistant') and h.get('content'):
                messages.append({"role": h['role'], "content": h['content']})
        messages.append({"role": "user", "content": user_msg})

        # Appel Anthropic API
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            return jsonify({"reply": "⚠️ Clé API non configurée. Contactez-nous : contact@i-aes.com"}), 200

        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
                "x-api-key": api_key
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 1024,
                "system": SYSTEM_PROMPT,
                "messages": messages
            },
            timeout=30
        )

        if not resp.ok:
            return jsonify({"error": f"API error {resp.status_code}"}), 500

        result = resp.json()
        reply = result['content'][0]['text']
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
