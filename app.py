#!/usr/bin/env python3
"""CONSEILPREV — Sert le site statique. API data.gouv.fr appelée côté client."""
import os
from flask import Flask, send_from_directory, jsonify

app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "version": "3.0",
                    "note": "data.gouv.fr API called client-side (CORS open)"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
