from flask import Flask, request, jsonify
import os, yaml, requests
import json
from bs4 import BeautifulSoup

# load cache from files if it exists
cache_file = "ara_cache.json"
if os.path.exists(cache_file):
    with open(cache_file, "r") as f:
        cache = json.load(f)
else:
    cache = {}

import atexit
@atexit.register
def save_cache():
    with open(cache_file, "w") as f:
        json.dump(cache, f, indent=2)

# website scrape function
def scrape_text_from_url(url):
    print(f"Scraping: {url}")
    try:
        response = requests.get(url, timeout=8)
        soup = BeautifulSoup(response.text, "html.parser")

        # Try a set of common main content tags
        selectors = [
            {"name": "main"},
            {"name": "article"},
            {"name": "div", "id": "content"},
            {"name": "div", "class_": "article-content"},
            {"name": "section", "class_": "main-section"},
        ]

        for sel in selectors:
            tag = soup.find(**sel)
            if tag:
                print(f"Found tag: {sel}")
                return tag.get_text(separator="\n", strip=True)

        # Fallback: return all text
        print("Falling back to full-page text")
        return soup.get_text(separator="\n", strip=True)

    except Exception as e:
        return f"[Error scraping {url}: {str(e)}]"

# Load configuration from YAML
with open(os.getenv("CONFIG_PATH", "config.yaml"), "r") as f:
    config = yaml.safe_load(f)

MODEL_NAME = config.get("model", "llama3.2:1b")
OLLAMA_HOST = config.get("ai_host", "http://localhost:11434")
SCRAPE_URLS = config.get("sources", [])

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    print("Received POST payload:", request.json)

    question = request.json.get("question", "")
    print("Understood, indexing data storage...")

    # --- check the cache first ---
    if question in cache:
        print("Ah, I already know the answer to that question.")
        return jsonify({"answer": cache[question]})

    # --- Step 1: Scrape Starfinder website ---
    scraped_text = [scrape_text_from_url(url) for url in SCRAPE_URLS]
    print("scraping done.")

    # --- Step 2: combin all text for the AI and Send to AI model ---
    starfinder_context = "\n\n".join(scraped_text)

    prompt = f"Question: {question}\n\nUse this Starfinder context: {starfinder_context}"
    print(f"Prompt to AI: {prompt}")

    # --- Step 3: call the AI model ---
    print("Sending to AI model...")
    SYSTEM_PROMPT = "Your personality is like EDI from Mass Effect, having a calm analytical tone, " \
                    "but with a hint of sarcasm. you go by ARA when appropriate. ARA stands for Artificial Rulings Assistant."

    print(f"DEBUG: About to call Ollama at {OLLAMA_HOST}")
    print(f"DEBUG: Model: {MODEL_NAME}")
    print(f"DEBUG: Prompt length: {len(prompt)}")

    ai_response = requests.post(f"{OLLAMA_HOST}/api/generate", json={
        "model": MODEL_NAME,
        "system": SYSTEM_PROMPT,
        "prompt": prompt,
        "stream": False
    })

    print(f"DEBUG: Ollama status code: {ai_response.status_code}")
    print(f"DEBUG: Ollama response: {ai_response.text}")

    response_json = ai_response.json()
    ai_text = response_json.get("response", "").strip()
    print ("AI returned:", ai_text)

    cache[question] = ai_text
    return jsonify({"answer": ai_text})

if __name__ == "__main__":
    port = config.get("port", 6969)
    app.run(host="0.0.0.0", port=port, debug=True)
