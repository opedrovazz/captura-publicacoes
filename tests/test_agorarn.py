import json
import csv
import time
from datetime import datetime
import sys

try:
    from scraper.sites.agorarn.agorarn_integration import scrape_agorarn
except ImportError as e:
    print(f"Erro ao importar o módulo do scraper: {e}")
    print("Verifique se a estrutura de pastas está correta (scraper/sites/agorarn/...)")
    sys.exit(1)

DATE_FORMAT = "%d/%m/%Y"
OUTPUT_FILENAME = "publicacoes_coletadas_agorarn"
DEFAULT_CUTOFF_DATE = "31/12/2025"
FILTER_TITLE = False
OUTPUT_FORMAT = "json"

def write_output(data, filename, fmt):
    """Salva os resultados em JSON ou CSV."""
    if not data:
        print("Nenhum dado coletado.")
        return

    if fmt == "json":
        with open(f"{filename}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        keys = data[0].keys()
        with open(f"{filename}.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
    print(f"Arquivo salvo: {filename}.{fmt}")

def main():
    print("Iniciando scraping: Agora RN")
    print(f"Data limite: {DEFAULT_CUTOFF_DATE}")
    if FILTER_TITLE:
        print("Filtro 'balanço' ativado")

    try:
        cutoff_date = datetime.strptime(DEFAULT_CUTOFF_DATE, DATE_FORMAT)
    except ValueError:
        print(f"Data limite inválida: {DEFAULT_CUTOFF_DATE}")
        sys.exit(1)

    start = time.time()
    data = scrape_agorarn(cutoff_date, FILTER_TITLE)
    end = time.time()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{OUTPUT_FILENAME}_{timestamp}"
    write_output(data, filename, OUTPUT_FORMAT)

    print("")
    print(f"Tempo total: {end - start:.2f} segundos")
    print(f"Total coletado: {len(data)}")

if __name__ == "__main__":
    main()
