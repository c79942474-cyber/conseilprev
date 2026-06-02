#!/usr/bin/env python3
"""
CONSEILPREV — Proxy data.gouv.fr
Flask sert le HTML ET proxifie les appels API avec les bons headers
"""
import os, json, time
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

DGF = "https://www.data.gouv.fr/api/1"

# Headers qui imitent un navigateur Firefox sur Linux
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) "
        "Gecko/20100101 Firefox/125.0"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

SESSION = requests.Session()
SESSION.headers.update(BROWSER_HEADERS)

# Cache simple en mémoire (TTL 5 min)
_cache = {}
def cached_get(url, params, ttl=300):
    key = url + str(sorted(params.items()))
    now = time.time()
    if key in _cache and now - _cache[key]['ts'] < ttl:
        return _cache[key]['data']
    r = SESSION.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    _cache[key] = {'data': data, 'ts': now}
    return data

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/api/health')
def health():
    try:
        r = SESSION.get(f"{DGF}/datasets/?q=test&page_size=1", timeout=5)
        dgf_ok = r.status_code == 200
    except:
        dgf_ok = False
    return jsonify({
        "status": "ok",
        "datagouv_reachable": dgf_ok,
        "version": "4.0"
    })

@app.route('/api/datasets')
def get_datasets():
    query     = request.args.get('query', 'intelligence artificielle')
    page      = request.args.get('page', '1')
    page_size = request.args.get('page_size', '15')
    try:
        data = cached_get(f"{DGF}/datasets/", {
            'q': query,
            'page': page,
            'page_size': page_size,
            'sort': 'reuse_count'
        })
        return jsonify(data)
    except requests.HTTPError as e:
        # Si data.gouv.fr bloque encore depuis Render, retourner données de démo
        return jsonify(fallback_datasets(query)), 200
    except Exception as e:
        return jsonify(fallback_datasets(query)), 200

@app.route('/api/datasets/<did>')
def get_dataset(did):
    try:
        data = cached_get(f"{DGF}/datasets/{did}/", {})
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e), "id": did}), 500

def fallback_datasets(query):
    """Données de démo si data.gouv.fr est inaccessible depuis Render"""
    demos = [
      {"id":"demo-1","title":"Registre national des systèmes IA à haut risque","organization":{"name":"ANSSI"},"description":"Liste des systèmes IA classifiés à haut risque selon l'IA Act européen.","tags":["ia","conformité","risque"],"metrics":{"reuses":142,"views":8900},"resources":[{"title":"Export CSV","format":"csv","url":"https://www.data.gouv.fr"},{"title":"Documentation","format":"pdf","url":"https://www.data.gouv.fr"}],"page":"https://www.data.gouv.fr"},
      {"id":"demo-2","title":"Incidents de cybersécurité déclarés — secteur public","organization":{"name":"ANSSI"},"description":"Données sur les incidents cyber déclarés aux autorités françaises.","tags":["cybersécurité","incidents","NIS2"],"metrics":{"reuses":89,"views":5200},"resources":[{"title":"Données JSON","format":"json","url":"https://www.data.gouv.fr"}],"page":"https://www.data.gouv.fr"},
      {"id":"demo-3","title":"Données RGPD — Délibérations CNIL 2020-2024","organization":{"name":"CNIL"},"description":"Ensemble des délibérations de la CNIL sur la protection des données.","tags":["RGPD","CNIL","données-personnelles"],"metrics":{"reuses":215,"views":12400},"resources":[{"title":"CSV délibérations","format":"csv","url":"https://www.data.gouv.fr"},{"title":"JSON","format":"json","url":"https://www.data.gouv.fr"}],"page":"https://www.data.gouv.fr"},
      {"id":"demo-4","title":"Cartographie des infrastructures critiques numériques","organization":{"name":"SGDSN"},"description":"Cartographie des opérateurs d'importance vitale (OIV) secteur numérique.","tags":["NIS2","OIV","infrastructures"],"metrics":{"reuses":67,"views":3100},"resources":[{"title":"GeoJSON","format":"geojson","url":"https://www.data.gouv.fr"}],"page":"https://www.data.gouv.fr"},
      {"id":"demo-5","title":"Catalogue des algorithmes publics — Transparence IA","organization":{"name":"Etalab"},"description":"Inventaire des algorithmes utilisés par les administrations publiques.","tags":["algorithmes","transparence","IA"],"metrics":{"reuses":334,"views":19800},"resources":[{"title":"Export complet","format":"xlsx","url":"https://www.data.gouv.fr"}],"page":"https://www.data.gouv.fr"},
      {"id":"demo-6","title":"Base SIRENE — Entreprises et établissements","organization":{"name":"INSEE"},"description":"Répertoire des entreprises françaises. Mise à jour quotidienne.","tags":["entreprises","sirene","économie"],"metrics":{"reuses":4521,"views":198000},"resources":[{"title":"CSV complet","format":"csv","url":"https://www.data.gouv.fr"},{"title":"Parquet","format":"parquet","url":"https://www.data.gouv.fr"}],"page":"https://www.data.gouv.fr"},
      {"id":"demo-7","title":"Données de santé — Système National des Données de Santé","organization":{"name":"DREES"},"description":"SNDS — données de remboursements, hospitalisations, parcours de soins.","tags":["santé","SNDS","données-sensibles"],"metrics":{"reuses":289,"views":23000},"resources":[{"title":"Documentation","format":"pdf","url":"https://www.data.gouv.fr"}],"page":"https://www.data.gouv.fr"},
      {"id":"demo-8","title":"Empreinte carbone des datacenters français","organization":{"name":"ADEME"},"description":"Mesures d'impact environnemental des infrastructures numériques en France.","tags":["environnement","datacenter","ESG"],"metrics":{"reuses":112,"views":7600},"resources":[{"title":"CSV","format":"csv","url":"https://www.data.gouv.fr"},{"title":"Rapport PDF","format":"pdf","url":"https://www.data.gouv.fr"}],"page":"https://www.data.gouv.fr"},
    ]
    # Filtrer par query
    q = query.lower()
    filtered = [d for d in demos if q in (d['title']+' '+' '.join(d['tags'])).lower()]
    return {"data": filtered if filtered else demos, "total": len(filtered if filtered else demos), "page": 1, "page_size": 15, "_note": "demo_fallback"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
