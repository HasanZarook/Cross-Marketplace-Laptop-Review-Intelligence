# Cross-Marketplace Laptop & Review Intelligence
**Author:** A.G. Hasan Zarook  
**Scope:** Practical deliverable for WebLife Labs technical assessment.

---

## Project Summary (what this repo actually contains)
This project extracts canonical technical specifications from PDF datasheets and *mutable* marketplace fields (price, availability, promos, ratings/review counts) from official HP and Lenovo product pages for **four** target laptops:

- HP ProBook 440 14 inch G11
- HP ProBook 450 15.6 inch G10 (Wolf Pro Security Edition)
- Lenovo ThinkPad E14 Gen 5 (14″ Intel)
- Lenovo ThinkPad E14 Gen 5 (14″ AMD)

You provided:
- PDF extraction code and cleaned JSON (`pdf_extractor.py`, `laptop_specs_normalized.json`)
- Two web scrapers (`webpage_scraper.py`, `webpage_scraper2.py`) and their outputs (`laptops_output.json`, `laptop_data.json`)
- Schema and validator (`laptop_specs_schema.json`, `json_schema_and_validator.py`)
- Backend (FastAPI) that loads the JSONs and uses Groq/Llama for the chatbot (`backend.py`)
- Simple static frontend (`index.html`) that talks to the FastAPI `/chat` endpoint

This README documents *exactly* those artifacts and how to run them.

---

## Files (exactly what you shared)
```
pdf_extractor.py
laptop_specs_normalized.json
laptop_specs_schema.json
json_schema_and_validator.py

webpage_scraper.py
webpage_scraper2.py
laptop_data.json          # output from webpage_scraper2 (HP product JSON-LD + visible_text + reviews/qa)
laptops_output.json       # output from webpage_scraper (summary per-product)

backend.py                # FastAPI, loads JSONs and calls Groq LLM
index.html                # Frontend chat + recommend UI
README.md                 
Some Artifacts
```

---

## Libraries / Tools actually used

- `pdfplumber` — PDF text extraction (used in `pdf_extractor.py`)
- `re`, `json`, `pathlib` — Python stdlib used by extractor
- `crawl4ai` — asynchronous crawler + optional LLM extraction strategy (used in some scraper versions)
- `BeautifulSoup` (`bs4`) — DOM parsing/selector-based extraction (used in both scrapers)
- `requests` — simple HTTP fetching (used in `webpage_scraper2.py`)
- `asyncio` — for async scraping runner
- `Groq` (Groq SDK) — LLM client in `backend.py`
- `dotenv` — load `.env` with `GROQ_API_KEY`
- `fastapi`, `uvicorn` — API server
- `jsonschema` (`Draft7Validator`) — validating PDF-extracted JSON schema (`json_schema_and_validator.py`)
- `pydantic` — FastAPI request model
- `bs4.Comment` — for visible-text extraction in `webpage_scraper2.py`
- `pdfplumber` (and/or `pypdf` if you later use it) — PDF parsing

---

## High-level methodology (what your code does)

### 1) PDF specs extraction (`pdf_extractor.py`)
- Opens each PDF in `data/pdfs` with `pdfplumber`
- Concatenates page text and runs a large set of regex-based extractors to pull structured fields:
  - `model`, `processor`, `memory`, `storage`, `display`, `graphics`, `battery`, `weight`, `dimensions`, `ports`, `wireless`, `os`, `security`, `multimedia`, `monitor`, `chipset`, `colour`, `case_material`, `network`, `warranty`, `certification`, `input_device`, `power`
- Produces `laptop_specs_complete.json` (and you later cleaned -> `laptop_specs_normalized.json`)

Notes:
- The extractor is tolerant: returns `"Not specified"` when patterns are absent.
- Final normalized file `laptop_specs_normalized.json` is the canonical spec source for the 4 models.

---

### 2) Website scraping
Have two scraper approaches because HP and Lenovo structure product pages differently.

#### `webpage_scraper.py` (async + crawl4ai + BeautifulSoup)
- Uses `AsyncWebCrawler` (crawl4ai) with `browserless_driver=True` to render JS where needed
- Retrieves the rendered DOM, parses with BeautifulSoup, then uses explicit CSS selectors you collected manually to extract:
  - `product_title`, `price_current`, `price_original`, `availability`, `promo_text` (multiple), `reviews_count`, `rating`
- Includes fallback logic:
  - If availability text is missing, treat as "Available" if `price_current` exists else "Unavailable"
  - Extracts multiple promo items and joins with `" | "`
- Output: `laptops_output.json` (a summary array with one object per product)

Important notes from your testing:
- Some prices are rendered by JS; `crawl4ai` with `browserless_driver=True` is used to render the page before parsing.
- Encountered pages where price or details were missing (out of stock / available soon). The scraper falls back to rating / reviews when full details are absent.

#### `webpage_scraper2.py` (requests + BeautifulSoup)
- A defensive scraper: downloads raw HTML (non-rendered), saves to `laptop.html`, extracts:
  - `application/ld+json` Product block (JSON-LD)
  - visible text (stripping scripts/styles/comments)
  - attempts to discover review / Q&A API endpoints embedded in inline scripts and call them
  - HTML parsers for BazaarVoice-like review/Q&A DOM fragments
- Output: `laptop_data.json` containing:
  - `product` (JSON-LD if present)
  - `visible_text`
  - `reviews` (`api` + `html`)
  - `qa` (`api` + `html`)

used both scrapers because HP stores some data in JSON-LD and external review APIs, while Lenovo's layout required a different approach.

---

### 3) Schema & validation (`json_schema_and_validator.py`)
- JSON Schema (Draft-07) is provided as `laptop_specs_schema.json`
- `validate_laptop_specs` uses `Draft7Validator` to list all errors
- `normalize_data` canonicalizes certain fields (booleans, arrays, weights -> `weights.variant_1`)
- Outputs `laptop_specs_normalized.json` and report text

---

### 4) Backend (FastAPI) — `backend.py`
- Loads `laptop_specs_normalized.json` and website JSONs (`laptops_output.json` / `laptop_data.json`)
- Endpoint `POST /chat`:
  - Builds a system prompt listing the 4 laptops and including the JSON dumps of PDF specs and website scrap data
  - Sends the prompt + history to Groq `llama-3.3-70b-versatile`
  - Returns the assistant's answer
- Endpoint `GET /` healthcheck and `POST /clear` to clear chat history
- How you run it:
  - Put `GROQ_API_KEY` in `.env`
  - `uvicorn backend:app --reload --host 0.0.0.0 --port 8000`

Caveats already discovered:
- Passing large raw HTML/JSON into the LLM is expensive (tokens). You intentionally limit what goes to LLM (summaries, cleaned JSON).
- Local LLMs (ollama / large models) were considered but resource constraints and hallucination risk led to the current approach.

---

## How to run everything (exact commands, minimal assumptions)

1. **Create a Python virtual environment**
```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
```

2. **Install dependencies (suggested list based on your code)**
Create `requirements.txt` with:
```
pdfplumber
crawl4ai
beautifulsoup4
requests
fastapi
uvicorn[standard]
groq
python-dotenv
jsonschema
pydantic
```
Then:
```bash
pip install -r requirements.txt
```

3. **Run scrapers (optional)**
- `webpage_scraper.py` (async crawl4ai version)
```bash
python -m asyncio -c "import asyncio, webpage_scraper; asyncio.run(webpage_scraper.run_all())"
```
*(Or just run the script if it's set to call run_all() under `if __name__ == '__main__'`.)*

- `webpage_scraper2.py`:
```bash
python webpage_scraper2.py
```
This will create `laptop.html` and `laptop_data.json`.

4. **Validate PDF schema**
```bash
python json_schema_and_validator.py
# produces laptop_specs_normalized.json and laptop_specs_report.txt
```

5. **Run backend**
- Create `.env` with `GROQ_API_KEY=your_key_here`
- Start:
```bash
uvicorn backend:app --reload --host 0.0.0.0 --port 8000
```

6. **Open frontend**
- Open `index.html` in a browser (it's a static file that posts to `http://localhost:8000/chat` by default).

---

## Known limitations & recommendations (you already discussed these)
- **JS-rendered price fields**: some pages load price via client JS or third-party review widgets — using `crawl4ai` with `browserless_driver=True` helps but may still miss fields if the site blocks headless browsers.
- **LLM token limits**: avoid sending entire HTML to the LLM. Use cleaned JSON and short summaries instead.
- **Out of stock / removed products**: website JSONs may lack price/offer for discontinued models — rely on PDF canonical specs as fallback for technical fields.
- **Review text scarcity**: some pages expose rating & count but not full text (or require API keys). You handled this by collecting rating / review count when text isn't available.

---

## Suggested next steps (practical, minimal)
1. Persist merged dataset to a small DB (SQLite/Postgres) for history and price-trend storage.  
2. Implement per-SKU price-history ingestion and a scheduled scraper (cron) to track offers.  
3. Create a small summarizer that reduces `visible_text` to a short paragraph before sending to LLM to reduce token usage.  
4. Add unit tests around your regex extractors to stabilize PDF parsing.

---

## 🧪 Testing & Validation

    PDF extraction validation
    JSON schema compliance
    Scraper output validation
    API response signature verification
    Chat grounding tests
    No-hallucination safeguards


## 📘 License
  
  This project is for WebLife Labs – AI Engineer Technical Assessment.


## Contact
  AG Hasan Zarook
  BSc Computer Engineer R.Eng(PEC)
  hasanzarook46@gmail.com
