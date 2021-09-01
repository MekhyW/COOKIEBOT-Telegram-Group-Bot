from os import path
import requests
import json
ModerateContentTOKEN = ''
url = "https://cdn77-pic.xnxx-cdn.com/videos/thumbs169xnxxposter/6c/62/0d/6c620d24042a5269a1ff0e0fab9cb43a/6c620d24042a5269a1ff0e0fab9cb43a.5.jpg"
r = requests.get("https://api.moderatecontent.com/moderate/?key={}&url={}".format(ModerateContentTOKEN, url))
print(float(json.loads(r.text)['predictions']['adult']))