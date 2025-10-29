from ...base_scraper import BaseScraper
from datetime import datetime
import re
import unicodedata

DATE_FORMAT = "%d/%m/%Y"

class DiarioDoComercioService:
    BASE_URL = "https://diariodocomercio.com.br"

    @staticmethod
    def should_collect(pub_date, cutoff_date):
        return pub_date <= cutoff_date

    @staticmethod
    def should_filter_title(title, filter_text):
        if not filter_text:
            return False

        def normalize(text):
            nfkd = unicodedata.normalize("NFKD", text)
            return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()

        title_norm = normalize(title)
        filter_norm = normalize(filter_text)
        return filter_norm not in title_norm

    @staticmethod
    def parse_publication_date_from_url(edital_url):
        url_parts = edital_url.strip('/').split('/')
        date_segment = url_parts[-1] if len(url_parts) > 1 else None

        if date_segment and re.match(r'\d{2}-\d{2}-\d{4}', date_segment):
            pub_date_str = date_segment.replace('-', '/')
            return datetime.strptime(pub_date_str, DATE_FORMAT), pub_date_str
        return None, None

    @staticmethod
    def extract_publication_data(edital_html, edital_url):
        return BaseScraper.scrape_pdf_link_and_title(edital_html, edital_url)
