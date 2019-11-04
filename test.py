import requests

response = requests.get("http://localhost:8795/something?Modellering en simulatie&blah")
print(response.content)
