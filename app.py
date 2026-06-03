import os
from flask import Flask, send_from_directory, jsonify

app = Flask(__name__, static_folder='.', static_url_path='')

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
    return jsonify({"status": "ok", "source": "local", "version": "5.0"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Proxy Mistral AI — la clé API est côté serveur, jamais exposée au client"""
    import requests as req
    data = request.get_json()
    messages = data.get('messages', [])
    mistral_key = os.environ.get('MISTRAL_API_KEY', '')
    if not mistral_key:
        return jsonify({"error": "MISTRAL_API_KEY non configurée"}), 500
    try:
        r = req.post(
            'https://api.mistral.ai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {mistral_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'mistral-small-latest',
                'messages': messages,
                'max_tokens': 600,
                'temperature': 0.7
            },
            timeout=30
        )
        r.raise_for_status()
        return jsonify(r.json())
    except req.HTTPError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
