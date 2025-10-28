import argparse
import sys
import json
import csv
import time
from datetime import datetime

try:
    from scraper.sites.diariodocomercio.diariodocomercio_integration import scrape_diariodocomercio
except ImportError as e:
    print(f"ERRO de Importação: {e}")
    sys.exit(1)

DATE_FORMAT = "%d/%m/%Y"
OUTPUT_FILENAME = "publicacoes_coletadas"
DEFAULT_CUTOFF_DATE = "31/12/2025"

def write_output(data, filename, fmt):
    if not data:
        print("Nenhum dado coletado.")
        return

    if fmt == 'json':
        with open(f"{filename}.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        keys = data[0].keys()
        with open(f"{filename}.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
    print(f"Dados salvos em {filename}.{fmt}")

def main():
    parser = argparse.ArgumentParser(description="Executa o scraper do Diário do Comércio")
    parser.add_argument('cutoff_date', nargs='?', default=DEFAULT_CUTOFF_DATE)
    parser.add_argument('-t', '--filter-title', action='store_true')
    parser.add_argument('-f', '--format', choices=['json', 'csv'], default='json')

    args = parser.parse_args()

    try:
        cutoff_date = datetime.strptime(args.cutoff_date, DATE_FORMAT)
    except ValueError:
        print(f"Data inválida: {args.cutoff_date}. Formato correto: {DATE_FORMAT}")
        sys.exit(1)

    print(f"Iniciando scraping com data limite: {args.cutoff_date}")
    if args.filter_title:
        print("Filtro 'balanço' ativado")

    start = time.time()
    data = scrape_diariodocomercio(cutoff_date, args.filter_title)
    end = time.time()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{OUTPUT_FILENAME}_diariodocomercio_{timestamp}"
    write_output(data, filename, args.format)

    print(f"\nTempo total: {end - start:.2f}s")
    print(f"Total coletado: {len(data)}")

if __name__ == "__main__":
    main()
