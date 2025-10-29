import time
from datetime import datetime
from ...base_scraper import BaseScraper
from .diariocomercial_service import DiarioComercialService

INDEX_PATH = "/publicidade-legal/pagina/{page_num}/"
DATE_FORMAT = "%d/%m/%Y"
MAX_PAGES = 200

def scrape_diariocomercial(cutoff_date, filter_text=None):
    page_num = 1
    collected = []

    while page_num <= MAX_PAGES:
        index_url = f"{DiarioComercialService.BASE_URL}{INDEX_PATH.format(page_num=page_num)}"
        print(f"\nPágina: {index_url}")

        page_html = BaseScraper.get_html_content(index_url)
        if not page_html:
            print("Falha ao carregar página. Encerrando.")
            break

        publications = DiarioComercialService.parse_page_for_publications(page_html)
        if not publications:
            print("Nenhuma publicação encontrada nesta página. Encerrando.")
            break

        print(f"{len(publications)} publicações encontradas.")

        for pub in publications:
            try:
                pub_date = datetime.strptime(pub["date"], DATE_FORMAT)
            except ValueError:
                print(f"Data inválida: {pub['date']}")
                continue

            if pub_date > cutoff_date:
                # print(f"{pub['date']} é mais nova que {cutoff_date.strftime('%d/%m/%Y')}, ignorando.")
                continue

            if DiarioComercialService.should_filter_title(pub["title"], filter_text):
                print(f"Pulando '{pub['title']}' (não contém '{filter_text}').")
                continue

            collected.append({
                "date": pub["date"],
                "pdf_url": pub["pdf_url"],
                "title": pub["title"],
                "site": "diariocomercial.com.br",
                "original_url": index_url
            })
            print(f"Coletado: {pub['date']} - {pub['title']}")
            time.sleep(0.5)

        page_num += 1
        time.sleep(2)

    return collected
