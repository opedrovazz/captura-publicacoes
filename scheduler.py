import asyncio
import schedule
import time
import json
from datetime import datetime
from scraper.sites.diariodocomercio.diariodocomercio_integration import scrape_diariodocomercio
from scraper.sites.diariocomercial.diariocomercial_integration import scrape_diariocomercial
from scraper.sites.agorarn.agorarn_integration import scrape_agorarn

DATE_FORMAT = "%d/%m/%Y"
MAX_RETRIES = 3

def save_to_json(site_name, data):
    """Salva o resultado do scraper em um arquivo JSON com timestamp."""
    if not data:
        print(f"Nenhum dado coletado para {site_name}.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"publicacoes_{site_name}_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Arquivo salvo: {filename} ({len(data)} registros)")

async def run_scraper_with_retry(site_name, scraper_func, cutoff_date):
    """Executa um scraper com até 3 tentativas em caso de falha."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Iniciando {site_name} (tentativa {attempt}/{MAX_RETRIES})...")
            data = await asyncio.to_thread(scraper_func, cutoff_date)
            print(f"{len(data)} publicações coletadas de {site_name}.")
            save_to_json(site_name, data)
            return
        except Exception as e:
            print(f"Erro ao executar {site_name} (tentativa {attempt}): {e}")
            if attempt < MAX_RETRIES:
                print("Tentando novamente em 5 segundos...")
                await asyncio.sleep(5)
            else:
                print(f"Falha definitiva ao coletar {site_name} após {MAX_RETRIES} tentativas.")

async def run_all_scrapers_async():
    """Executa todos os scrapers em paralelo."""
    today_str = datetime.now().strftime(DATE_FORMAT)
    today = datetime.strptime(today_str, DATE_FORMAT)

    print(f"Iniciando execução paralela ({today_str})")

    scrapers = [
        ("diariodocomercio", scrape_diariodocomercio),
        ("diariocomercial", scrape_diariocomercial),
        ("agorarn", scrape_agorarn)
    ]

    tasks = [
        run_scraper_with_retry(site_name, scraper_func, today)
        for site_name, scraper_func in scrapers
    ]

    await asyncio.gather(*tasks)

    print("\nExecução paralela concluída.")

def run_all_scrapers():
    """Wrapper síncrono para rodar a versão assíncrona."""
    asyncio.run(run_all_scrapers_async())

def start_scheduler():
    """Agendamento diário às 06:00."""
    schedule.every().day.at("06:00").do(run_all_scrapers)
    print("Scheduler iniciado. Aguardando próxima execução (06:00).")

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_all_scrapers()
    start_scheduler()
