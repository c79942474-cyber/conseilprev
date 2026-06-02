#!/usr/bin/env python3
"""
CONSEILPREV — Data.gouv.fr MCP Connector
API Flask + connecteur data.gouv.fr + filtres sectoriels
"""

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ══ CONNECTEUR DATA.GOUV.FR ══

class DataGouvFRConnector:
    def __init__(self, base_url="https://www.data.gouv.fr/api/1"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "CONSEILPREV-MCP-Connector/1.0",
            "Accept": "application/json"
        })

    def search_datasets(self, query="IA gouvernance", page=1, page_size=20, sort="reuse_count"):
        url = f"{self.base_url}/datasets/"
        params = {"q": query, "page": page, "page_size": page_size, "sort": sort}
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e), "data": []}

    def get_dataset(self, dataset_id):
        url = f"{self.base_url}/datasets/{dataset_id}/"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def get_dataset_resources(self, dataset_id):
        data = self.get_dataset(dataset_id)
        return data.get("resources", [])

    def get_dataset_metrics(self, dataset_id):
        url = f"{self.base_url}/datasets/{dataset_id}/metrics/"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def search_organizations(self, query):
        url = f"{self.base_url}/organizations/"
        params = {"q": query, "page_size": 10}
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def get_reuses(self, dataset_id):
        url = f"{self.base_url}/datasets/{dataset_id}/reuses/"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def filter_datasets_by_sector(self, datasets, sector):
        """Filtre les datasets par secteur (titre, description, tags)"""
        results = []
        for ds in datasets:
            title = ds.get("title", "").lower()
            desc = ds.get("description", "").lower()
            tags = " ".join(ds.get("tags", [])).lower()
            if sector.lower() in (title + desc + tags):
                results.append(ds)
        return results

    def get_ia_compliance_datasets(self):
        """Datasets spécifiques IA, cybersécurité, conformité"""
        queries = ["intelligence artificielle", "cybersécurité", "conformité RGPD", "données publiques"]
        all_datasets = []
        for q in queries:
            result = self.search_datasets(q, page_size=5)
            all_datasets.extend(result.get("data", []))
        # Dédupliquer par ID
        seen = set()
        unique = []
        for ds in all_datasets:
            if ds.get("id") not in seen:
                seen.add(ds.get("id"))
                unique.append(ds)
        return unique


connector = DataGouvFRConnector()


# ══ ROUTES API ══

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "CONSEILPREV MCP Connector", "version": "1.0"})

@app.route("/api/datasets")
def get_datasets():
    query = request.args.get("query", "IA gouvernance")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 20))
    sector = request.args.get("sector", None)
    result = connector.search_datasets(query, page, page_size)
    if sector:
        result["data"] = connector.filter_datasets_by_sector(result.get("data", []), sector)
    return jsonify(result)

@app.route("/api/datasets/<dataset_id>")
def get_dataset(dataset_id):
    return jsonify(connector.get_dataset(dataset_id))

@app.route("/api/datasets/<dataset_id>/resources")
def get_resources(dataset_id):
    return jsonify(connector.get_dataset_resources(dataset_id))

@app.route("/api/datasets/<dataset_id>/metrics")
def get_metrics(dataset_id):
    return jsonify(connector.get_dataset_metrics(dataset_id))

@app.route("/api/organizations")
def get_organizations():
    query = request.args.get("query", "")
    return jsonify(connector.search_organizations(query))

@app.route("/api/ia-compliance")
def get_ia_datasets():
    datasets = connector.get_ia_compliance_datasets()
    return jsonify({"data": datasets, "total": len(datasets)})

@app.route("/api/filter")
def filter_datasets():
    query = request.args.get("query", "données")
    sector = request.args.get("sector", "santé")
    result = connector.search_datasets(query, page_size=50)
    filtered = connector.filter_datasets_by_sector(result.get("data", []), sector)
    return jsonify({"data": filtered, "total": len(filtered), "sector": sector})


if __name__ == "__main__":
    print("🚀 CONSEILPREV MCP Connector — data.gouv.fr")
    print("📡 API: http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
