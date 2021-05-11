import json
import requests
message = "Ahhhh o louco possessivo"
#r = requests.get('https://simsumi.herokuapp.com/api?text={}&lang=pt_BR'.format(message))
#Answer = r.text.replace('{"success":"', '').replace('"}', '').encode().decode('unicode_escape').capitalize()
#print(Answer)

#import json
#import requests
#message = "Manda nuds pra mim"
#headers = {'Content-Type': 'application/json','x-api-key': 'DNwrIXADkwIhTi9VWhOwOFZVhW7y7fVSuc2npRbq'}
#data = '{ "utext": "MESSAGE", "lang": "pt", "atext_bad_prob_max": 0.95 }'.replace("MESSAGE", message)
#r = requests.post('https://wsapi.simsimi.com/190410/talk', headers=headers, data=data)
#Answer = json.loads(r.text).get("atext").capitalize()
#print(Answer)

#import googletrans
#translator = googletrans.Translator()
#r = requests.get('https://api.simsimi.net/v1/?text={}&lang=pt'.format(message))
#try:
#    Answer = json.loads(r.text)['success'].capitalize()
#except:
#    Answer = str(r.text).split("{")[1]
#    Answer = "{" + Answer
#    Answer = json.loads(Answer)['success'].capitalize()
#Answer = translator.translate(Answer, dest='pt').text
#print(Answer)

import googletrans
translator = googletrans.Translator()
r = requests.get('https://test.simsimi.net/v1/?text={}&lang=pt&cf=true'.format(message))
try:
    Answer = json.loads(r.text)['messages'][0]['response'].capitalize()
except:
    Answer = str(r.text).split("{")[1]
    Answer = "{" + Answer
    Answer = json.loads(Answer)['messages'][0]['response'].capitalize()
Answer = translator.translate(Answer, dest='pt').text
print(Answer)