import json
import requests
NAMEHERE = "mikkel a".split()[0]
print(json.loads(requests.get("https://api.agify.io?name={}".format(NAMEHERE)).text)['age'])