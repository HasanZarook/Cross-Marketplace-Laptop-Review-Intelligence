# Cross-Marketplace Laptop & Review Intelligence  
### WebLife Labs – Technical Assessment  
Author: **A.G. Hasan Zarook**  
Role: **AI Engineer**

---

## 📌 Overview

This project delivers an **end-to-end intelligence engine** for business laptops sold across multiple sources — specifically **Lenovo**, **HP**, and marketplace listings like **MySoft**.  
The system unifies:

- **Canonical technical specifications** extracted from PDFs  
- **Marketplace data** (price, availability, promos, badges)  
- **User reviews & Q/A text** from Lenovo/HP product pages  
- **Historical price tracking**  
- **Interactive analytics & visualizations**  
- **A full chatbot + recommendation engine**

A complete **dataset**, **schema**, **documentation**, and **LLM-powered API** are included.

This repository is structured for production-grade clarity and easy reproducibility.

---

# 🚀 System Features (End-to-End)

### ✔ 1. Canonical Spec Extraction from PDFs  
Using the official PSREF and HP datasheets:

- Lenovo ThinkPad E14 Gen 5 (Intel)  
- Lenovo ThinkPad E14 Gen 5 (AMD)  
- HP ProBook 450 G10  
- HP ProBook 440 G11  

The pipeline performs:

- PDF parsing via `pypdf`  
- Structured extraction using regex & rule-based parsing  
- Cleanup and normalization  
- Conversion to canonical JSON specification files

These JSON specs serve as the **ground truth** for comparison.

---

### ✔ 2. Cross-Marketplace Data Aggregation

From Lenovo & HP **official product pages**, and the MySoft marketplace, we collect:

- Price  
- Currency  
- Availability  
- Promo badges  
- Seller (if marketplace)  
- Shipping ETA  
- SKU variations  
- Review counts & ratings  
- Review text and Q&A excerpts  

The data is stored in unified collections and linked to canonical specs.

---

### ✔ 3. Reviews & Rating Intelligence

Reviews from Lenovo and HP pages are:

- Extracted using BeautifulSoup  
- Cleaned for noise  
- Stored in the Reviews table  
- Sentiment-analyzed using  
  - VADER  
  - TextBlob  
  - A custom lightweight transformer (optional)

Outputs include:

- Sentiment labels  
- Summary of opinions  
- Keyword extraction (aspects such as battery, display, performance)

---

### ✔ 4. Unified Dataset Generation

All data sources are merged into a **single identity** for each product (`product_id`).  
The merging pipeline ensures:

- Canonical specs override marketplace inconsistencies  
- Price and availability override PDF info  
- Reviews linked to the correct SKU  
- Historical price entries logged  
- Final dataset saved as `final_dataset.json`

This dataset powers the analytics and chatbot.

---

### ✔ 5. REST API (Production-Ready)

A versioned API is provided with endpoints for:

