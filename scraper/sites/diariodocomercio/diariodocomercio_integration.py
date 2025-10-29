import time
from datetime import datetime
from ...base_scraper import BaseScraper
from .diariodocomercio_service import DiarioDoComercioService

INDEX_PATH = "/publicidade-legal-impresso/page/{page_num}/"
DATE_FORMAT = "%d/%m/%Y"
MAX_PAGES = 200  # proteção contra loop infinito

def scrape_diariodocomercio(cutoff_date, filter_text=None):
    page_num = 1
    collected_publications = []

    while page_num <= MAX_PAGES:
        index_url = f"{DiarioDoComercioService.BASE_URL}{INDEX_PATH.format(page_num=page_num)}"
        print(f"\nPágina: {index_url}")

        page_html = BaseScraper.get_html_content(index_url)
        if not page_html:
            print("Falha ao carregar página. Encerrando.")
            break

        edital_links = BaseScraper.scrape_edital_links(page_html, DiarioDoComercioService.BASE_URL)
        if not edital_links:
            print("Nenhum edital encontrado. Encerrando scraping.")
            break

        print(f"{len(edital_links)} links de edital encontrados.")
        for edital_url in sorted(edital_links, reverse=True):
            pub_date, pub_date_str = DiarioDoComercioService.parse_publication_date_from_url(edital_url)
            if not pub_date:
                print(f"Data inválida: {edital_url}")
                continue

            if pub_date > cutoff_date:
                # print(f"{pub_date_str} é mais nova que {cutoff_date.strftime('%d/%m/%Y')}, ignorando.")
                continue

            edital_html = BaseScraper.get_html_content(edital_url)
            if not edital_html:
                print(f"Erro ao carregar edital: {edital_url}")
                continue

            title, pdf_url = DiarioDoComercioService.extract_publication_data(edital_html, edital_url)
            if not title or not pdf_url:
                continue

            if DiarioDoComercioService.should_filter_title(title, filter_text):
                print(f"Pulando '{title}' (não contém '{filter_text}').")
                continue

            collected_publications.append({
                "date": pub_date_str,
                "pdf_url": pdf_url,
                "title": title,
                "site": "diariodocomercio.com.br",
                "original_url": edital_url
            })
            print(f"Coletado: {pub_date_str} - {title}")
            time.sleep(0.5)

        page_num += 1
        time.sleep(2)

    return collected_publications
