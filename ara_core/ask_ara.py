import requests

# URL of your local webhook server
url = "http://localhost:6969/webhook"

# Ask the user a question
question = input("Hello commander, what is your question?: ")

# Send it as JSON
response = requests.post(url, json={"question": question})

# Print the AI response
if response.status_code == 200:
    data = response.json()
    ai_answer = data.get("answer", "[No answer found]")
    print("\nAI Response:\n" + ai_answer)
else:
    print("Error:", response.status_code, response.text)
