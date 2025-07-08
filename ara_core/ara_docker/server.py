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

# relevant urls function
def get_relevant_urls(question, all_urls):
    """select relevant URLs based on the question"""
    question_lower = question.lower()

    # url mapping based in content type
    url_categories = {
        'general': ['Default.aspx'],
        'disease': ['Disease'],
        'poison': ['Poison'],
        'curse': ['Curse'],
        'drug': ['Drug'],
        'corruption': ['Corruption'],
        'affliction': ['Affliction'],
        'aliens': ['Aliens.aspx'],
        'starship': ['Starship'],
        'universal monster rules': ['UniversalMonsterRules.aspx']
    }

    # keywords that indicate specific categories
    keywords = {
        'general': ['rules', 'books', 'mechanics', 'gameplay', 'combat', 'actions', 'abilities', 'skills', 'equipment'],
        'disease': ['disease', 'illness', 'sick', 'infection', 'plague', 'fever'],
        'poison': ['poison', 'poisons', 'venom', 'toxin', 'antidote'],
        'curse': ['curse', 'curses', 'cursed', 'hex'],
        'drug': ['drug', 'drugs', 'addiction', 'narcotic', 'stimulant'],
        'corruption': ['corruption', 'corrupted'],
        'affliction': ['affliction', 'afflictions', 'condition', 'status'],
        'aliens': ['alien', 'aliens', 'extraterrestrial', 'xenobiology', 'xeno', 'swarm', 'creature'],
        'starship': ['starship', 'starships', 'ship', 'vehicle', 'craft', 'starship combat', 'starship rules', 'the drift'],
        'universal monster rules': ['universal monster rules', 'monster rules', 'creature rules', 'monster manual']
    }

    selected_urls = []

    # always the main page for context
    for url in all_urls:
        if "Default.aspx" in url:
              selected_urls.append(url)
    
    # check for specific keywords in the question
    for category, keyword_list in keywords.items():
        print(f"DEBUG: Checking category '{category}' with keywords: {keyword_list}")
        if any(keyword in question_lower for keyword in keyword_list):
            print(f"DEBUG: MATCHED category '{category}'")
            for url in all_urls:
              if any(cat_marker in url for cat_marker in url_categories[category]):
                  print(f"DEBUG: Adding URL: {url}")
                  selected_urls.append(url) 
        else:
            print(f"DEBUG: No match for category '{category}'")

    # If no specific category found, use general URL
    if len(selected_urls) == 1:  # Only has Default.aspx
        for url in all_urls:
            if 'Default.aspx' in url and 'Category=' not in url:
                selected_urls.append(url)
    
    print(f"DEBUG: Final selected URLs: {selected_urls}")
    return selected_urls

# website scrape function
def scrape_text_from_url(url):
    print(f"Scraping: {url}")
    try:
        response = requests.get(url, timeout=8)
        soup = BeautifulSoup(response.text, "html.parser")

        # Try a set of common main content tags
        selectors = [
            {"name": "div", "id": "main"},
            {"name": "div", "id": "main-wrapper"},
            {"name": "div", "class_": "main"},
            {"name": "div", "class_": "main-wrapper"},
            {"name": "div", "id": "page"},
            {"name": "div", "class_": "page"},
            {"name": "span", "id": "ct100_MainContent_MainNewsFeed"},
            {"name": "span", "id": "ct100_MainContent_Body"},
            {"name": "span", "id": "ct100_MainContent_Links:"},
            {"name": "table", "id": "ct100_MainContent_DataListAfflictions"},
            {"name": "table", "id": "ct100_MainContent_DataListCorruptions"},
            # Generic
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

MODEL_NAME = config.get("model", "llama3.2:3b")
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

    # --- Step 1: Check for relevant urls and Scrape Starfinder website ---
    relevant_urls = get_relevant_urls(question, SCRAPE_URLS)

    scraped_text = [scrape_text_from_url(url) for url in relevant_urls]
    print("scraping done.")

    # --- Step 2: combine all text for the AI and Send to AI model ---
    starfinder_context = "\n\n".join(scraped_text)

    try:
        with open("glossary.txt", "r") as f:
            glossary = f.read()
    except:
        glossary = ""

    prompt = f"{glossary} Question: {question}\n\nUse this Starfinder context to answer the question. \
    focus on general rules and definitions rather than specific examples: {starfinder_context}"
    print(f"Prompt to AI: {prompt}")

    # --- Step 3: call the AI model ---
    print("Sending to AI model...")
    SYSTEM_PROMPT = """You are a Starfinder RPG rules expert. Answer questions about specific Starfinder game mechanics, items, spells, creatures, and rules.

IMPORTANT INSTRUCTIONS:
1. If the user asks about something that EXISTS in Starfinder, provide the specific Starfinder details
2. If the user asks about something that does NOT exist in Starfinder, clearly state: "This does not exist in Starfinder" 
3. Do NOT provide generic lists unless specifically asked
4. Focus on answering the EXACT question asked
5. Use only the provided Starfinder reference material

Answer the user's specific question directly and accurately."""

    print(f"DEBUG: About to call Ollama at {OLLAMA_HOST}")
    print(f"DEBUG: Model: {MODEL_NAME}")
    print(f"DEBUG: Prompt length: {len(prompt)}")

    ai_response = requests.post(f"{OLLAMA_HOST}/api/generate", json={
        "model": MODEL_NAME,
        "system": SYSTEM_PROMPT,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.7
        }
    })

    print(f"DEBUG: Ollama status code: {ai_response.status_code}")
    print(f"DEBUG: Ollama response: {ai_response.text}")

    response_json = ai_response.json()
    ai_text = response_json.get("response", "").strip()
    print ("AI returned:", ai_text)

    cache[question] = ai_text
    return jsonify({"answer": ai_text})

if __name__ == "__main__":
    port = config.get("port", 6749)
    app.run(host="0.0.0.0", port=port, debug=True)
