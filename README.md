# Captura de Publicações Legais

Projeto em **Python + Flask** para realizar **web scraping** de publicações legais disponíveis nos portais:

- [Diário do Comércio](https://diariodocomercio.com.br/publicidade-legal-impresso/)
- [Diário Comercial](https://diariocomercial.com.br/publicidade-legal/)
- [Agora RN](https://agorarn.com.br/publicacoescertificadas/)

O sistema coleta publicações legais, exporta resultados em **JSON** ou **CSV**, e permite consulta via **API**.

---

## Funcionalidades

- Coleta automática de publicações por site.  
- Filtro obrigatório por **data máxima** (`date=dd/mm/yyyy`).  
- Escolha do formato de saída: **JSON** (padrão) ou **CSV**.  
- API local simples feita em **Flask**.  
- Exportação de resultados diretamente pela requisição.

---

## Estrutura do Projeto

```
captura-publicacoes/
│
├── main.py                      # Script principal
├── api/
│   └── routes.py                # Rotas Flask
├── scraper/
│   ├── base_scraper.py          # Classe base
│   └── sites/
│       ├── diariodocomercio/
│       ├── diariocomercial/
│       └── agorarn/
└── tests/                       # Testes
```

---

## Instalação

Clone o repositório e instale as dependências:

```bash
git clone https://github.com/opedrovazz/captura-publicacoes.git
cd captura-publicacoes
pip install -r requirements.txt
```

---

## Execução da API

```bash
python main.py api
```
Após iniciar, o servidor roda por padrão em:

```
http://127.0.0.1:5000
```

---

## Rotas Disponíveis

### 1. `GET /`
Retorna informações básicas sobre a API e os sites disponíveis.

**Exemplo de resposta:**
```json
{
  "message": "API de Scrapers Online",
  "endpoints": {
    "run": "/<site>?date=dd/mm/yyyy&format={json|csv}",
    "sites_disponiveis": ["diariodocomercio", "diariocomercial", "agorarn"]
  }
}
```

---

### 2. `GET /<site>`
Executa o scraper de um site específico, filtrando por data.

**Parâmetros obrigatórios:**  
- `date`: data limite no formato `dd/mm/yyyy`  
- `format`: (opcional) formato de saída, `json` (padrão) ou `csv`

**Exemplos:**

#### JSON (padrão)
```bash
GET /diariodocomercio?date=31/01/2025
```
**Resposta:**
```json
{
  "site": "diariodocomercio",
  "cutoff_date": "31/01/2025",
  "total": 25,
  "results": [
    {"date": "30/01/2025", "title": "Balanço Patrimonial 2024", "pdf_url": "https://..."}
  ]
}
```

#### CSV
```bash
GET /agorarn?date=29/10/2025&format=csv
```
A resposta é um arquivo `.csv` com cabeçalho e colunas:
```
date,title,pdf_url
29/10/2025,Balanço Patrimonial 2024,https://...
```

---

## Observações Importantes

- Caso o `site` informado não exista, a API retorna erro 400.  
- O parâmetro `date` é obrigatório — se omitido, retorna erro 400.  
- Formatos válidos: `json` ou `csv`.  
- Caso não haja resultados, a resposta em CSV retorna código 204 (sem conteúdo).

---
