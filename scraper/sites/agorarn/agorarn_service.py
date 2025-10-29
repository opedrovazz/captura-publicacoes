from datetime import datetime
from bs4 import BeautifulSoup
import re
import unicodedata

DATE_FORMAT = "%d/%m/%Y"

class AgoraRNService:
    BASE_URL = "https://agorarn.com.br"

    @staticmethod
    def parse_page_for_publications(page_html):
        """
        Lê o HTML da página e retorna uma lista de publicações:
        [
          {"date": "11/10/2025", "title": "...", "pdf_url": "..."}
        ]
        """
        soup = BeautifulSoup(page_html, "lxml")
        items = []

        rows = soup.find_all("div", id="certificadas", class_="row")

        for row in rows:
            link_tag = row.find("a", href=re.compile(r"\.pdf$", re.IGNORECASE))
            if not link_tag:
                continue

            pdf_url = link_tag["href"]

            # Nome da empresa
            company_div = link_tag.find("div", class_=re.compile(r"strong"))
            company = company_div.get_text(strip=True) if company_div else "Publicação Legal"

            # Descrição da publicação
            desc_div = link_tag.find_all("div", class_=re.compile(r"col-md-5"))
            description = desc_div[0].get_text(strip=True) if desc_div else ""

            # Data
            date_div = link_tag.find("div", class_=re.compile(r"text-center"))
            raw_date = date_div.get_text(strip=True) if date_div else None
            if not raw_date:
                continue

            pub_date_str = AgoraRNService.normalize_date(raw_date)
            if not pub_date_str:
                continue

            title = f"{company} - {description}" if description else company

            items.append({
                "date": pub_date_str,
                "title": title,
                "pdf_url": pdf_url
            })

        return items

    @staticmethod
    def normalize_date(raw_date):
        """Converte datas como '11/10/25' ou '11-10-2025' em DD/MM/YYYY."""
        raw_date = raw_date.strip()
        match = re.match(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", raw_date)
        if not match:
            return None
        dia, mes, ano = match.groups()
        if len(ano) == 2:
            ano = "20" + ano
        return f"{int(dia):02d}/{int(mes):02d}/{ano}"

    @staticmethod
    def should_collect(pub_date, cutoff_date):
        """Retorna True se a publicação estiver dentro da data limite."""
        return pub_date <= cutoff_date

    @staticmethod
    def should_filter_title(title, filter_text):
        """Retorna True se o título NÃO contém o texto buscado (case-insensitive, ignora acentos)."""
        if not filter_text:
            return False

        def normalize(text):
            nfkd = unicodedata.normalize("NFKD", text)
            return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()

        title_norm = normalize(title)
        filter_norm = normalize(filter_text)

        return filter_norm not in title_norm