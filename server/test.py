import requests

response = requests.get("http://localhost:8795/google?Modellering en simulatie&blah")
print(response.content)
