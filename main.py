import sys
import threading
import argparse
import json
import csv
from datetime import datetime
from api import create_app
from scheduler import start_scheduler, run_all_scrapers

# Scrapers
from scraper.sites.agorarn.agorarn_integration import scrape_agorarn
from scraper.sites.diariodocomercio.diariodocomercio_integration import scrape_diariodocomercio
from scraper.sites.diariocomercial.diariocomercial_integration import scrape_diariocomercial


def start_api():
    """Inicializa o servidor Flask."""
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)


def start_scheduler_thread():
    """Inicia o scheduler em uma thread separada."""
    try:
        run_all_scrapers()
        start_scheduler()
    except KeyboardInterrupt:
        print("Encerrando scheduler...")


def run_scraper_cli(args):
    """Executa o scraper via linha de comando."""
    site = args.site.lower()
    date_str = args.date
    fmt = args.format.lower()
    filter_text = args.filter_text

    try:
        cutoff_date = datetime.strptime(date_str, "%d/%m/%Y")
    except ValueError:
        print("Formato de data inválido. Use dd/mm/yyyy.")
        sys.exit(1)

    print(f"Iniciando coleta para o site '{site}' com data limite {date_str}...")

    if site == "agorarn":
        results = scrape_agorarn(cutoff_date, filter_text=filter_text)
    elif site == "diariodocomercio":
        results = scrape_diariodocomercio(cutoff_date, filter_text=filter_text)
    elif site == "diariocomercial":
        results = scrape_diariocomercial(cutoff_date, filter_text=filter_text)
    else:
        print(f"Site '{site}' não reconhecido.")
        sys.exit(1)

    if not results:
        print("Nenhuma publicação coletada.")
        return

    output_name = f"resultados_{site}_{date_str.replace('/', '-')}.{fmt}"
    if fmt == "json":
        with open(output_name, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    elif fmt == "csv":
        with open(output_name, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    else:
        print("Formato inválido. Use 'json' ou 'csv'.")
        sys.exit(1)

    print(f"Coleta concluída. Resultado salvo em: {output_name}")


def main():
    """
    Ponto de entrada principal.

    Exemplos:
      python main.py api
      python main.py scheduler
      python main.py both
      python main.py agorarn --date 31/10/2025 --filter-text "balanço" --format csv
    """
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python main.py api")
        print("  python main.py scheduler")
        print("  python main.py both")
        print("  python main.py <site> --date dd/mm/yyyy [--format json|csv] [--filter-text 'palavra']")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command in ("api", "scheduler", "both"):
        if command == "api":
            start_api()
        elif command == "scheduler":
            start_scheduler_thread()
        elif command == "both":
            api_thread = threading.Thread(target=start_api, daemon=True)
            api_thread.start()
            start_scheduler_thread()
    else:
        parser = argparse.ArgumentParser(description="Executa o scraper de publicações legais.")
        parser.add_argument("site", help="Nome do site (agorarn, diariodocomercio, diariocomercial)")
        parser.add_argument("--date", required=True, help="Data limite (dd/mm/yyyy)")
        parser.add_argument("--format", default="json", choices=["json", "csv"], help="Formato de saída")
        parser.add_argument("--filter-text", help="Filtra publicações cujo título contenha a palavra informada (case-insensitive).")
        args = parser.parse_args()
        run_scraper_cli(args)


if __name__ == "__main__":
    main()
