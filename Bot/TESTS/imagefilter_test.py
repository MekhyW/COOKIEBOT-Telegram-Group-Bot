from os import path
import requests
import json
ModerateContentTOKEN = ''
url = "https://pbs.twimg.com/media/Dkro4WLXsAAp9Lr.jpg"
r = requests.get("https://api.moderatecontent.com/moderate/?key={}&url={}".format(ModerateContentTOKEN, url))
print(float(json.loads(r.text)['predictions']['adult']))