from flask import Blueprint, request, jsonify, make_response
from datetime import datetime
import csv
from io import StringIO
from scraper.sites.diariodocomercio.diariodocomercio_integration import scrape_diariodocomercio
from scraper.sites.diariocomercial.diariocomercial_integration import scrape_diariocomercial
from scraper.sites.agorarn.agorarn_integration import scrape_agorarn

api_blueprint = Blueprint("api", __name__)

DATE_FORMAT = "%d/%m/%Y"
DEFAULT_OUTPUT_FORMAT = "json"

SCRAPER_MAP = {
    "diariodocomercio": scrape_diariodocomercio,
    "diariocomercial": scrape_diariocomercial,
    "agorarn": scrape_agorarn,
}

@api_blueprint.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "API de Scrapers Online",
        "endpoints": {
            "run": "/<site>?date=dd/mm/yyyy&format={json|csv}",
            "sites_disponiveis": list(SCRAPER_MAP.keys())
        }
    })

@api_blueprint.route("/<site>", methods=["GET"])
def run_scraper(site):
    site = site.lower()

    if site not in SCRAPER_MAP:
        return jsonify({"error": f"Site '{site}' não reconhecido"}), 400

    cutoff_str = request.args.get("date")
    if not cutoff_str:
        return jsonify({"error": "Parâmetro 'date' (dd/mm/yyyy) é obrigatório"}), 400

    output_format = request.args.get("format", DEFAULT_OUTPUT_FORMAT).lower()
    if output_format not in ["json", "csv"]:
        return jsonify({"error": f"Formato de saída '{output_format}' inválido. Use 'json' ou 'csv'"}), 400

    try:
        cutoff_date = datetime.strptime(cutoff_str, DATE_FORMAT)
    except ValueError:
        return jsonify({"error": f"Formato inválido da data: {cutoff_str}. Use dd/mm/yyyy"}), 400

    try:
        scraper_func = SCRAPER_MAP[site]
        results = scraper_func(cutoff_date)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if output_format == "csv":
        if not results:
            return make_response("", 204)
            
        output = StringIO()
        keys = results[0].keys()
        writer = csv.DictWriter(output, fieldnames=keys)
        
        writer.writeheader()
        writer.writerows(results)
        csv_data = output.getvalue()
        
        response = make_response(csv_data)
        response.headers["Content-Disposition"] = f"attachment; filename={site}_data.csv"
        response.headers["Content-type"] = "text/csv; charset=utf-8"
        return response
    
    return jsonify({
        "site": site,
        "cutoff_date": cutoff_str,
        "total": len(results),
        "results": results
    })