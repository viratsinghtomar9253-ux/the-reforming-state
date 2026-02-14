import requests
import time

url = "http://localhost:5000/whatsapp"
data = {
    "Body": "You never listen to me and you're always late! I hate how you treat me.",
    "From": "whatsapp:+1234567890"
}

print(f"Sending mock message to {url}...")
try:
    response = requests.post(url, data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except requests.exceptions.ConnectionError:
    print("Error: Could not connect to Flask server. Is it running?")
