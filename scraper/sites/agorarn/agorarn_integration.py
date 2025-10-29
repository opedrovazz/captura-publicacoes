import time
from datetime import datetime
from ...base_scraper import BaseScraper
from .agorarn_service import AgoraRNService

INDEX_PATH = "/publicacoescertificadas/page/{page_num}/"
DATE_FORMAT = "%d/%m/%Y"

def scrape_agorarn(cutoff_date, filter_text=None):
    page_num = 1
    collected = []

    while True:
        index_url = f"{AgoraRNService.BASE_URL}{INDEX_PATH.format(page_num=page_num)}"
        print(f"Processando página: {index_url} - agorarn")

        page_html = BaseScraper.get_html_content(index_url)
        if not page_html:
            print("Falha ao carregar página. Encerrando.")
            break

        publications = AgoraRNService.parse_page_for_publications(page_html)
        if not publications:
            print("Nenhuma publicação encontrada nesta página. Encerrando.")
            break

        print(f"{len(publications)} publicações encontradas.")

        collected_on_page = False
        for pub in publications:
            try:
                pub_date = datetime.strptime(pub["date"], DATE_FORMAT)
            except ValueError:
                print(f"Data inválida: {pub['date']}")
                continue

            if not AgoraRNService.should_collect(pub_date, cutoff_date):
                print(f"Data {pub['date']} excede a data limite. Encerrando scraping.")
                return collected

            if AgoraRNService.should_filter_title(pub["title"], filter_text):
                print(f"Pulando '{pub['title']}' (não contém '{filter_text}').")
                continue

            collected.append({
                "date": pub["date"],
                "pdf_url": pub["pdf_url"],
                "title": pub["title"],
                "site": "agorarn.com.br",
                "original_url": index_url
            })
            print(f"Coletado: {pub['date']} - {pub['title']}")
            collected_on_page = True
            time.sleep(0.5)

        if not collected_on_page:
            print("Nenhuma nova publicação nesta página.")
            break

        page_num += 1
        time.sleep(2)

    return collected
