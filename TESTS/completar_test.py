import googletrans
translator = googletrans.Translator()
#print(translator.translate('Boa tarde guria', dest='en').text)

import requests
import json
r = requests.post("https://api.deepai.org/api/text-generator",data={'text': translator.translate('Boa tarde guria', dest='en').pronunciation,},headers={'api-key': '8a5dedaf-d5a5-4b37-93a1-fcd6e94c6ba4'})
Answer = translator.translate(r.json()['output'], dest='pt').text
print(Answer)