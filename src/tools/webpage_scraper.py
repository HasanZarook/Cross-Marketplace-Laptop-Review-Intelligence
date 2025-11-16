import re
import json
import asyncio
from crawl4ai import AsyncWebCrawler, CacheMode
from bs4 import BeautifulSoup

# --------------------------
# Utility Functions
# --------------------------
def extract_price(text):
    if not text:
        return None
    m = re.search(r"\$[\d,]+(?:\.\d{2})?", text)
    if not m:
        return None
    return float(m.group(0).replace("$", "").replace(",", ""))

def pick_first(soup, selectors):
    for sel in selectors:
        for el in soup.select(sel):
            text = el.get_text(strip=True)
            if text:
                return text
    return None

def pick_all_texts(soup, selectors):
    results = []
    for sel in selectors:
        for el in soup.select(sel):
            text = el.get_text(strip=True)
            if text and text not in results:
                results.append(text)
    return results

# --------------------------
# CSS selectors for HP + Lenovo
# --------------------------
SELECTORS = {
    "title": [
        "h1.pdp-title",'h1[data-test-hook="@hpstellar/core/typography"]',"h1", 
        "h1[itemprop='name']",'h1.product-name', ".product-title", ".product-name", "h2.Vp-v_gf"
    ],
    "price_current": [
        'span.sale-subscription-price', "span[data-test='product-price']",
        "span[itemprop='price']", 'div.price_container',
        ".product-price .price", ".pdp-price .price", ".price__value"
    ],
    "price_original": [
        ".compare-at-price",'div.starting-at-price span[data-test-hook="@hpstellar/core/typography"]',
        ".price--was", 'div.price_container',".original-price", ".was-price",
        ".price--strike"
    ],
    "availability": [
        'button[data-test-hook="@hpstellar/core/button"] span[data-test-hook="@hpstellar/core/typography"]',
        "span[data-test-hook='@hpstellar/core/product-tile__stock__stock']",
        'span[data-test-hook="@hpstellar/core/stock-indicator__stock"]',
        'span.special-status_text', ".stock-status", ".availability", 
        ".out-of-stock", ".pdp-unavailable", ".stock"
    ],
    "promo_text": [
        'div[data-test-hook="@hpstellar/core/banner/highlight-banner__description"]',
        'div[data-test-hook="@hpstellar/core/banner/highlight-banner__title"]',
        'div.merchandizingItem[data-tkey="merchandizingBanner.item"] p',
        "ul.V2-I_gf div[data-test-hook='@hpstellar/core/typography'] span.cust-html",
        'div.product-offers-content p',
        'div.product-offers div.offer-type-contingent p[data-test-hook="@hpstellar/core/typography"]',
        ".promo", ".offer", ".savings", ".price-savings", ".promo-text"
    ],
    "reviews_count": [
        "div[data-test-hook='@hpstellar/core/typography'].Nm-Nu_gf",
        'div.bv_numReviews_component_container meta[itemprop="reviewCount"]',
        'div.bv_numReviews_component_container div.bv_text',
        ".reviews-count", ".review-count", "#reviews .count",'div.bv_numReviews_text'
    ],
    "rating": [
        "div.bv_averageRating_component_container div.bv_text",
        "nuber_box",
        "bv_text"
        "div.bv_averageRating_component_container div.bv_text",
        "div.bv_text",
        "div[data-test-hook='@hpstellar/core/typography'].Nm-Nt_gf",
        'div.bv_avgRating_component_container[itemprop="ratingValue"]',
        'div.bv_averageRating_component_container div.bv_text'
    ]
}

# --------------------------
# Main scraping function
# --------------------------
async def scrape_laptop(url):
    async with AsyncWebCrawler(cache_mode=CacheMode.BYPASS, browserless_driver=True) as crawler:
        result = await crawler.arun(url=url, css_selector="body")  # fully rendered page
        soup = BeautifulSoup(result.html, "html.parser")

    # -------------------------
    # Title
    # -------------------------
    title = pick_first(soup, SELECTORS["title"])

    # -------------------------
    # Prices
    # -------------------------
    price_current_txt = pick_first(soup, SELECTORS["price_current"])
    price_current = price_current_txt.strip("()") if price_current_txt else None
    

    price_original_txt = pick_first(soup, SELECTORS["price_original"])
    price_original = price_original_txt.strip("()") if price_original_txt else None
    

    # -------------------------
    # Availability
    # -------------------------
    availability_txt = pick_first(soup, SELECTORS["availability"])
    if availability_txt:
        availability = availability_txt.strip()
    else:
        availability = "Available" if price_current else "Unavailable"

    # -------------------------
    # Promo text (multiple)
    # -------------------------
    promos = pick_all_texts(soup, SELECTORS["promo_text"])
    promo_text = " | ".join(promos) if promos else None

    # -------------------------
    # Reviews & Rating
    # -------------------------
    reviews_txt = pick_first(soup, SELECTORS["reviews_count"])
    reviews = reviews_txt.strip("()") if reviews_txt else None

    rating_txt = pick_first(soup, SELECTORS["rating"])
    rating = rating_txt.strip("()") if rating_txt else None

    # -------------------------
    # Discount
    # -------------------------
    discount = price_original - price_current if price_current and price_original and price_original > price_current else None

    # -------------------------
    # Return structured JSON
    # -------------------------
    return {
        "product_title": title,
        "brand": "HP" if "hp.com" in url else "Lenovo",
        "price_current": price_current,
        "price_original": price_original,
        "discount": discount,
        "availability": availability,
        "promo_text": promo_text,
        "reviews_count": reviews,
        "rating": rating,
        "source_url": url
    }

# --------------------------
# Run all URLs
# --------------------------
async def run_all():
    urls = [
       # "https://www.hp.com/us-en/shop/pdp/hp-probook-440-14-inch-g11-notebook-pc-p-a3rn0ua-aba-1",
        "https://www.hp.com/us-en/shop/mdp/pro-352502--1/probook-450#buy",
        "https://www.lenovo.com/us/en/p/laptops/thinkpad/thinkpade/thinkpad-e14-gen-5-14-inch-intel/len101t0064",
        "https://www.lenovo.com/us/en/p/laptops/thinkpad/thinkpade/thinkpad-e14-gen-5-14-inch-amd/len101t0068"
    ]

    final_output = []

    for url in urls:
        print(f"Scraping → {url}")
        try:
            data = await scrape_laptop(url)
            final_output.append(data)
        except Exception as e:
            final_output.append({"error": str(e), "source_url": url})

    with open("laptops_output.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=4, ensure_ascii=False)

    print("\nDONE! Saved → laptops_output.json")

if __name__ == "__main__":
    asyncio.run(run_all())
