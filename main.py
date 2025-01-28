import requests
import json

# Define the API endpoint and payload
url = "http://74.102.26.111:11434/api/generate"
data = {
    "model": "deepseek-r1",
    "prompt": "Hello, how are you?"
}

# Send the POST request
response = requests.post(url, json=data, stream=True)

print("Streaming Response (Word by Word):")
for line in response.iter_lines():
    if line:
        # Parse each JSON line
        json_line = json.loads(line)
        # Extract the response fragment and split it into words
        response_fragment = json_line.get("response", "")
        for word in response_fragment.split():
            print(word, end=" ", flush=True)  # Print word by word
