#!/usr/bin/env python3
"""
CONSEILPREV — Data.gouv.fr MCP Connector
"""
import os
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

DATAGOUV = "https://www.data.gouv.fr/api/1"
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "CONSEILPREV-MCP/1.0",
    "Accept": "application/json"
})

# ── SITE ──────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204

# ── HEALTH ────────────────────────────────────────
@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "version": "2.0"})

# ── DATASETS ──────────────────────────────────────
@app.route('/api/datasets')
def get_datasets():
    query     = request.args.get('query', 'intelligence artificielle')
    page      = request.args.get('page', '1')
    page_size = request.args.get('page_size', '15')

    try:
        r = SESSION.get(f"{DATAGOUV}/datasets/", params={
            "q": query,
            "page": page,
            "page_size": page_size,
            "sort": "reuse_count"
        }, timeout=15)
        r.raise_for_status()
        data = r.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e), "data": [], "total": 0}), 500

# ── DATASET DETAIL ─────────────────────────────────
@app.route('/api/datasets/<dataset_id>')
def get_dataset(dataset_id):
    try:
        r = SESSION.get(f"{DATAGOUV}/datasets/{dataset_id}/", timeout=15)
        r.raise_for_status()
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── ORGANISATIONS ─────────────────────────────────
@app.route('/api/organizations')
def get_organizations():
    query = request.args.get('query', '')
    try:
        r = SESSION.get(f"{DATAGOUV}/organizations/", params={
            "q": query,
            "page_size": 20,
            "sort": "datasets"
        }, timeout=15)
        r.raise_for_status()
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e), "data": []}), 500

# ── THEMES AVEC VRAIS TOTAUX ───────────────────────
@app.route('/api/themes')
def get_themes():
    """Retourne les thématiques avec le nombre réel de datasets sur data.gouv.fr"""
    themes = [
        {"value": "intelligence artificielle", "label": "Intelligence Artificielle"},
        {"value": "cybersecurite",              "label": "Cybersécurité"},
        {"value": "RGPD donnees personnelles",  "label": "RGPD & Données personnelles"},
        {"value": "sante",                      "label": "Santé"},
        {"value": "energie",                    "label": "Énergie & Transition"},
        {"value": "transport",                  "label": "Transport & Mobilité"},
        {"value": "finance economie",           "label": "Finance & Économie"},
        {"value": "education",                  "label": "Éducation & Formation"},
        {"value": "environnement",              "label": "Environnement"},
        {"value": "logement immobilier",        "label": "Logement & Immobilier"},
    ]
    results = []
    for t in themes:
        try:
            r = SESSION.get(f"{DATAGOUV}/datasets/", params={
                "q": t["value"], "page_size": 1
            }, timeout=8)
            total = r.json().get("total", 0) if r.ok else 0
        except:
            total = 0
        results.append({**t, "total": total})
    return jsonify(results)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
