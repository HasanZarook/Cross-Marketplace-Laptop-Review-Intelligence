import requests
import json
from bs4 import BeautifulSoup, Comment

# -----------------------------
# Config
# -----------------------------
PRODUCT_URL = "https://www.hp.com/us-en/shop/pdp/hp-probook-440-14-inch-g11-notebook-pc-p-a3rn0ua-aba-1"
HTML_SAVE_FILE = "laptop.html"
OUTPUT_FILE = "laptop_data.json"


session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "text/html",
})


# -----------------------------
# Extract visible text helper
# -----------------------------
def extract_visible_text(html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "head", "meta", "link", "title"]):
        tag.decompose()

    def is_visible(element):
        return not isinstance(element, Comment)

    visible = filter(is_visible, soup.strings)
    return "\n".join(t.strip() for t in visible if t.strip())


# -----------------------------
# Fetch main page
# -----------------------------
response = session.get(PRODUCT_URL, timeout=20)
html = response.text
soup = BeautifulSoup(html, "html.parser")

# Save raw HTML
with open(HTML_SAVE_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print("Saved:", HTML_SAVE_FILE)


# -----------------------------
# Extract Product JSON-LD
# -----------------------------
product_json = None
json_ld_tag = soup.find("script", type="application/ld+json")

if json_ld_tag:
    try:
        parsed = json.loads(json_ld_tag.string)

        if isinstance(parsed, list):
            for item in parsed:
                if item.get("@type") == "Product":
                    product_json = item
                    break
        elif parsed.get("@type") == "Product":
            product_json = parsed
    except:
        pass


# -----------------------------
# Find Review + Q&A endpoints
# -----------------------------
review_endpoint = None
qa_endpoint = None

for script in soup.find_all("script"):
    if not script.string:
        continue

    text = script.string

    if "review" in text.lower() and "api" in text.lower():
        for piece in text.split('"'):
            if "review" in piece and "api" in piece:
                review_endpoint = piece

    if "question" in text.lower() and "api" in text.lower():
        for piece in text.split('"'):
            if "question" in piece and "api" in piece:
                qa_endpoint = piece


# -----------------------------
# API Review Fetch
# -----------------------------
reviews_api = []
if review_endpoint:
    try:
        r = session.get(review_endpoint, timeout=20)
        js = r.json()

        for item in js.get("results", []):
            reviews_api.append({
                "rating": item.get("rating"),
                "title": item.get("title"),
                "review": item.get("reviewText"),
                "author": item.get("userNickname"),
                "date": item.get("submissionTime"),
            })
    except Exception as e:
        print("Review API failed:", e)


# -----------------------------
# API Q&A Fetch
# -----------------------------
qa_api = []
if qa_endpoint:
    try:
        r = session.get(qa_endpoint, timeout=20)
        js = r.json()

        for item in js.get("results", []):
            answers = [{
                "answer": a.get("answerText"),
                "author": a.get("userNickname"),
                "date": a.get("submissionTime"),
            } for a in item.get("answers", [])]

            qa_api.append({
                "question": item.get("questionText"),
                "answers": answers
            })
    except Exception as e:
        print("Q&A API failed:", e)


# ----------------------------------------------------
# HTML Review Extraction (BazaarVoice DOM)
# ----------------------------------------------------
def extract_reviews_html(soup):
    reviews = []
    blocks = soup.select("section[id^='bv-review-'], div[id^='bv-review-']")

    for r in blocks:
        user = None
        rating = None
        title = None
        body = None
        verified = False
        location = None

        u = r.select_one("span.bv-rnr__sc-1r4hv38-0")
        if u:
            user = u.get_text(strip=True)

        rt = r.select_one("[aria-label*='out of 5 stars']")
        if rt and rt.get("aria-label"):
            rating = rt.get("aria-label").split(" out")[0]

        t = r.select_one("h3, .bv-content-title")
        if t:
            title = t.get_text(strip=True)

        b = r.select_one(".bv-content-summary-body-text, .bv-content-review-text")
        if b:
            body = b.get_text(" ", strip=True)

        verified = bool(r.select_one("[aria-label='Verified Purchaser']"))

        loc = r.select_one(".bv-rnr__emkap-1 span")
        if loc:
            location = loc.get_text(strip=True)

        reviews.append({
            "user": user,
            "rating": rating,
            "title": title,
            "body": body,
            "verified": verified,
            "location": location
        })

    return reviews


# ----------------------------------------------------
# HTML Q&A Extraction (BazaarVoice DOM)
# ----------------------------------------------------
def extract_qna_html(soup):
    qna = []
    blocks = soup.select("section[id^='bv-question-'], div[id^='bv-question-']")

    for q in blocks:
        question = None
        answer = None

        qelem = q.select_one(".bv-content-title, .bv-question-summary, h3")
        if qelem:
            question = qelem.get_text(" ", strip=True)

        aelem = q.select_one(".bv-answer, .bv-answer-text")
        if aelem:
            answer = aelem.get_text(" ", strip=True)

        qna.append({
            "question": question,
            "answer": answer
        })

    return qna


# Run HTML parsers
reviews_html = extract_reviews_html(soup)
qa_html = extract_qna_html(soup)

# -----------------------------
# Build final JSON
# -----------------------------
output = {
    "url": PRODUCT_URL,
    "product": product_json or {},
    "visible_text": extract_visible_text(html),
    "reviews": {
        "api": reviews_api,
        "html": reviews_html,
    },
    "qa": {
        "api": qa_api,
        "html": qa_html,
    }
}

# -----------------------------
# Save JSON
# -----------------------------
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=4, ensure_ascii=False)

print("Saved:", OUTPUT_FILE)
