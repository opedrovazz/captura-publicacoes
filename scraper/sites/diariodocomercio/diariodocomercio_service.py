from ...base_scraper import BaseScraper
from datetime import datetime
import re
from bs4 import BeautifulSoup

DATE_FORMAT = "%d/%m/%Y"

class DiarioDoComercioService:
    BASE_URL = "https://diariodocomercio.com.br"

    @staticmethod
    def should_collect(pub_date, cutoff_date):
        """Verifica se a data da publicação é anterior ou igual à data limite."""
        return pub_date <= cutoff_date

    @staticmethod
    def should_filter_title(title, filter_title):
        """Verifica se o título deve ser filtrado com base na flag 'filter_title'."""
        if not filter_title:
            return False

        title_norm = re.sub(r'[ãáàâ]', 'a', title, flags=re.IGNORECASE)
        title_norm = re.sub(r'[éèê]', 'e', title_norm, flags=re.IGNORECASE)
        title_norm = re.sub(r'[íìî]', 'i', title_norm, flags=re.IGNORECASE)
        title_norm = re.sub(r'[õóòô]', 'o', title_norm, flags=re.IGNORECASE)
        title_norm = re.sub(r'[úùû]', 'u', title_norm, flags=re.IGNORECASE)

        return 'balanco' not in title_norm.lower()

    @staticmethod
    def parse_publication_date_from_url(edital_url):
        """Extrai e converte a data da URL do edital."""
        url_parts = edital_url.strip('/').split('/')
        date_segment = url_parts[-1] if len(url_parts) > 1 else None

        if date_segment and re.match(r'\d{2}-\d{2}-\d{4}', date_segment):
            pub_date_str = date_segment.replace('-', '/')
            return datetime.strptime(pub_date_str, DATE_FORMAT), pub_date_str
        return None, None

    @staticmethod
    def extract_publication_data(edital_html, edital_url):
        """Extrai título e URL do PDF do edital (usando lógica da BaseScraper)."""
        return BaseScraper.scrape_pdf_link_and_title(edital_html, edital_url)
