import requests

# URL of your local webhook server
url = "http://localhost:6969/webhook"

# Ask the user a question
question = input("What's your question commander?: ")

# Send it as JSON
payload = {"question": question}
response = requests.post(url, json=payload)

# Print the AI response
if response.status_code == 200:
    print("\nAI Response:")
    print("Full server response:", response.text)
    print("\nStandby\n" + response.json()["answer"])
else:
    print("Error:", response.status_code, response.text)
