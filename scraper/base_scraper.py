import urllib.request
import urllib.error
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, parse_qs

REQUEST_TIMEOUT = 15

class BaseScraper:
    """Classe base para requisições HTTP e parsing genérico usando urllib/lxml."""

    @staticmethod
    def get_html_content(url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as response:
                content = response.read()
                charset = response.info().get_content_charset() or 'utf-8'
                return content.decode(charset, errors='replace')

        except urllib.error.HTTPError as e:
            print(f"ERRO HTTP: {e.code} - {e.reason} ({url})")
        except urllib.error.URLError as e:
            print(f"ERRO de Conexão/Timeout: {e.reason} ({url})")
        except Exception as e:
            print(f"ERRO inesperado: {e} ({url})")
            
        return None
    
    @staticmethod
    def scrape_edital_links(page_html, url_base):
        """Extrai todos os links de edital ('/edital-completo/') de uma página de índice."""
        soup = BeautifulSoup(page_html, 'lxml')
        edital_links = []
        
        for a_tag in soup.find_all('a', href=re.compile(r'/edital-completo/', re.IGNORECASE)):
            href = a_tag.get('href')
            if href:
                if href.startswith('/'):
                    href = f"{url_base}{href}"
                edital_links.append(href)

        return list(set(edital_links))

    @staticmethod
    def scrape_pdf_link_and_title(edital_html, edital_url):
        """
        Extrai Título e URL do PDF da página do edital.
        A data é extraída da URL do edital para montar o título legível.
        """
        soup = BeautifulSoup(edital_html, 'lxml')
        url_parts = edital_url.strip('/').split('/')
        date_segment = url_parts[-1] if url_parts else None
        
        date_formatted = "Publicação Legal" 

        if date_segment and re.match(r'\d{2}-\d{2}-\d{4}', date_segment):
            date_formatted = date_segment.replace('-', '/')
        
        if date_formatted != "Publicação Legal":
            title = f"Edição {date_formatted}"
        else:
            title = date_formatted

        pdf_url = None
        pdf_link_tag = soup.find('a', href=re.compile(r'\.pdf$', re.IGNORECASE))
        
        if not pdf_link_tag:
             pdf_link_tag = soup.find('a', text=re.compile(r'download|visualizar|pdf|edital completo', re.IGNORECASE))
        
        if not pdf_link_tag:
            iframe_tag = soup.find('iframe', class_='pdfjs-iframe')
            if iframe_tag and iframe_tag.get('src'):
                iframe_src = iframe_tag['src']
                parsed_url = urlparse(iframe_src)
                query_params = parse_qs(parsed_url.query)
                
                if 'file' in query_params and query_params['file']:
                    pdf_url = query_params['file'][0] # 'file' retorna uma lista
                    
        if pdf_url and not pdf_url.startswith('http'):
            base_site_url = urlparse(edital_url).scheme + '://' + urlparse(edital_url).netloc
            pdf_url = f"{base_site_url}{pdf_url}"
            
        return title, pdf_url