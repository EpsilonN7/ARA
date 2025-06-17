from flask import Flask, request, jsonify
import os, yaml, requests
from bs4 import BeautifulSoup

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

MODEL_NAME = config.get("model_name", "llama3.2:1b")
OLLAMA_HOST = config.get("ai_host", "http://localhost:11434")
SCRAPE_URLS = config.get("sources", [])

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    question = request.json.get("question", "")
    print("Heard loud and clear")

    # --- Step 1: Scrape Starfinder website ---
    scraped_text = [scrape_text_from_url(url) for url in SCRAPE_URLS]
    
    # --- Step 2: combin all text for the AI and Send to AI model ---
    starfinder_context = "\n\n".join=(scraped_text)

    prompt = f"Question: {question}\n\nUse this Starfinder context: {starfinder_context}"
    print(f"Prompt to AI: {prompt}")

    ai_response = f"Allright, here's what I could find commander: '{question}'"

    return jsonify({"answer": ai_response})

if __name__ == "__main__":
    port = config.get("port", 6969)
    app.run(host="0.0.0.0", port=port, debug=True)
