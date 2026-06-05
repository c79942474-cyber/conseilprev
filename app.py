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

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/datasets.json')
def datasets():
    return send_from_directory('.', 'datasets.json', mimetype='application/json')

@app.route('/donnees')
def donnees():
    return send_from_directory('.', 'donnees.html')

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
