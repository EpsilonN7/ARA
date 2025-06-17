from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    question = data.get("question", "")

    print(f"Received question: {question}")

    # --- Step 1: Scrape Starfinder website (placeholder for now) ---
    starfinder_context = "This is mock Starfinder rule context."

    # --- Step 2: Send to AI model (placeholder response) ---
    prompt = f"Question: {question}\n\nUse this Starfinder context: {starfinder_context}"
    print(f"Prompt to AI: {prompt}")

    ai_response = f"This is an AI-generated answer to: '{question}' using Starfinder rules."

    return jsonify({"answer": ai_response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6969)
