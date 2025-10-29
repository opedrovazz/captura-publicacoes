# 📜 Captura de Publicações Legais

Projeto em **Python + Flask** para realizar **web scraping** de publicações legais disponíveis nos portais:

- [Diário do Comércio](https://diariodocomercio.com.br/publicidade-legal-impresso/)  
- [Diário Comercial](https://diariocomercial.com.br/publicidade-legal/)  
- [Agora RN](https://agorarn.com.br/publicacoescertificadas/)

O sistema coleta publicações legais, aplica filtros opcionais, exporta resultados em **JSON** ou **CSV**, e permite execução **tanto via API Flask quanto via linha de comando (CLI)**.

---

## 🧠 Funcionalidades Principais

- Coleta automática de publicações por site.  
- **Filtro obrigatório de data máxima** (`--date dd/mm/yyyy`).  
- **Filtro opcional de título** (`--filter-text "palavra"`), insensível a acentos e caixa.  
- Exportação de resultados em **JSON** (padrão) ou **CSV**.  
- **API local Flask** para consulta via HTTP.  
- Execução **via linha de comando** ou **modo servidor/scheduler**.  
- Lógica comum centralizada em `BaseScraper`, evitando duplicação de código.

---

## 🧱 Estrutura do Projeto

captura-publicacoes/
│
├── main.py                         # Ponto de entrada principal (CLI, API e scheduler)
├── scraper/
│   ├── base_scraper.py             # Classe base genérica
│   └── sites/
│       ├── diariodocomercio/
│       │   ├── diariodocomercio_integration.py
│       │   └── diariodocomercio_service.py
│       ├── diariocomercial/
│       │   ├── diariocomercial_integration.py
│       │   └── diariocomercial_service.py
│       └── agorarn/
│           ├── agorarn_integration.py
│           └── agorarn_service.py
│
├── api/                            # Rotas e inicialização da API Flask
│   └── routes.py
├── scheduler/                      # Tarefas agendadas de scraping automático
│   └── init.py
└── tests/                          # Testes

---

## ⚙️ Instalação

```bash
git clone https://github.com/opedrovazz/captura-publicacoes.git
cd captura-publicacoes
pip install -r requirements.txt
```

---

## 🚀 Modo de Execução via Linha de Comando (CLI)

Permite rodar os scrapers manualmente com parâmetros de filtro e formato.

### Sintaxe geral
```bash
python main.py <site> --date dd/mm/yyyy [--format json|csv] [--filter-text "palavra"]
```

### Parâmetros

| Parâmetro | Obrigatório | Descrição |
|------------|-------------|------------|
| `<site>` | ✅ | Nome do site (`agorarn`, `diariodocomercio`, `diariocomercial`) |
| `--date` | ✅ | Data limite no formato `dd/mm/yyyy`. Publicações posteriores são ignoradas. |
| `--format` | ❌ | Formato de saída: `json` (padrão) ou `csv`. |
| `--filter-text` | ❌ | Palavra a ser buscada nos títulos (case-insensitive e sem acentos). |

### Exemplos

**1️⃣ Executar o scraper do Diário do Comércio (JSON padrão)**  
```bash
python main.py diariodocomercio --date 31/10/2025
```

**2️⃣ Exportar CSV filtrando títulos que contenham “assembleia”**  
```bash
python main.py diariocomercial --date 30/10/2025 --format csv --filter-text "assembleia"
```

**3️⃣ Rodar para Agora RN filtrando “demonstrativo”**  
```bash
python main.py agorarn --date 29/10/2025 --filter-text "demonstrativo"
```

### Saída gerada

O scraper salva automaticamente o resultado no diretório atual:

```
resultados_<site>_<data>.json
resultados_<site>_<data>.csv
```

Exemplo:
```
resultados_diariodocomercio_31-10-2025.csv
```

Cada registro contém:
```json
{
  "date": "30/10/2025",
  "title": "Balanço Patrimonial 2024",
  "pdf_url": "https://...",
  "site": "diariodocomercio.com.br",
  "original_url": "https://..."
}
```

---

## 🧩 Modo Servidor (API Flask)

Permite rodar o servidor Flask local para consultas via HTTP:

```bash
python main.py api
```

Servidor padrão:
```
http://127.0.0.1:5000
```

### Rotas disponíveis

**GET /**  
Retorna informações sobre a API e os sites suportados.

**GET /<site>?date=dd/mm/yyyy&format=json|csv&filter=palavra**  
Executa o scraper e retorna o resultado direto na resposta.

**Exemplo:**
```
GET /agorarn?date=29/10/2025&format=csv&filter=assembleia
```

**Resposta (CSV):**
```
date,title,pdf_url,site,original_url
29/10/2025,Assembleia Geral Extraordinária,https://...,agorarn.com.br,https://...
```

---

## 🕒 Modo Agendado (Scheduler)

Execução automática diária dos scrapers:
```bash
python main.py scheduler
```

Ou para rodar API + Scheduler simultaneamente:
```bash
python main.py both
```

---

## 🧰 Tecnologias e Bibliotecas Utilizadas

- **Python 3.10+**  
- **Flask** — API HTTP  
- **BeautifulSoup4 + lxml** — parsing HTML  
- **urllib** — requisições HTTP  
- **threading** — execução simultânea da API e agendador  
- **argparse** — interface CLI

---

## 📁 Formatos de Saída

| Formato | Extensão | Descrição |
|----------|-----------|-----------|
| JSON | `.json` | Lista de objetos com `date`, `title`, `pdf_url`, `site`, `original_url`. |
| CSV | `.csv` | Arquivo tabular com cabeçalho `date,title,pdf_url,site,original_url`. |

---

## ✅ Escopo de Coleta

O scraper coleta todas as publicações disponíveis de 2025 em cada site.  
Ele interrompe automaticamente quando atinge uma publicação posterior à data limite (`--date`).

---

## 🧾 Exemplo (CLI)

```bash
python main.py agorarn --date 31/10/2025 --format csv --filter-text "patrimonial"
```

Saída esperada:
```
Iniciando coleta para o site 'agorarn' com data limite 31/10/2025...
Processando página: https://agorarn.com.br/publicacoescertificadas/page/1/
5 publicações encontradas.
Coletado: 29/10/2025 - Balanço Patrimonial 2024
✅ Coleta concluída. Resultado salvo em: resultados_agorarn_31-10-2025.csv
```

