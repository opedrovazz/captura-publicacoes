from datetime import datetime
from bs4 import BeautifulSoup
import re

DATE_FORMAT = "%d/%m/%Y"

class DiarioComercialService:
    BASE_URL = "https://diariocomercial.com.br"

    @staticmethod
    def parse_page_for_publications(page_html):
        """
        Lê o HTML da página de índice e retorna uma lista de publicações:
        [
          {"date": "28/10/2025", "title": "...", "pdf_url": "..."}
        ]
        """
        soup = BeautifulSoup(page_html, "lxml")
        items = []

        boxes = soup.find_all("div", class_="publicidade_box_infos")
        for box in boxes:
            date_tag = box.find("span", class_="publicidade_data")
            title_tag = box.find("h2")
            pdf_link_tag = box.find("a", href=re.compile(r"\.pdf$", re.IGNORECASE))

            if not (date_tag and pdf_link_tag):
                continue

            raw_date = date_tag.get_text(strip=True)
            pdf_url = pdf_link_tag.get("href")
            title = title_tag.get_text(strip=True) if title_tag else "Publicação Legal"

            pub_date_str = DiarioComercialService.normalize_date(raw_date)
            if not pub_date_str:
                continue

            items.append({
                "date": pub_date_str,
                "title": title,
                "pdf_url": pdf_url
            })

        return items

    @staticmethod
    def normalize_date(raw_date):
        """Converte data textual PT-BR ('27 de outubro de 2025') para dd/mm/yyyy."""
        meses = {
            "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04",
            "maio": "05", "junho": "06", "julho": "07", "agosto": "08",
            "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"
        }
        match = re.match(r"(\d{1,2}) de (\w+) de (\d{4})", raw_date.lower())
        if not match:
            return None
        dia, mes_texto, ano = match.groups()
        mes_num = meses.get(mes_texto)
        if not mes_num:
            return None
        return f"{int(dia):02d}/{mes_num}/{ano}"

    @staticmethod
    def should_collect(pub_date, cutoff_date):
        return pub_date <= cutoff_date

    @staticmethod
    def should_filter_title(title, filter_title):
        if not filter_title:
            return False

        title_norm = re.sub(r'[ãáàâ]', 'a', title, flags=re.IGNORECASE)
        title_norm = re.sub(r'[éèê]', 'e', title_norm, flags=re.IGNORECASE)
        title_norm = re.sub(r'[íìî]', 'i', title_norm, flags=re.IGNORECASE)
        title_norm = re.sub(r'[õóòô]', 'o', title_norm, flags=re.IGNORECASE)
        title_norm = re.sub(r'[úùû]', 'u', title_norm, flags=re.IGNORECASE)

        return 'balanco' not in title_norm.lower()
