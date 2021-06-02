import requests
import json
userid = 673062173
response = requests.post('https://burrbot.xyz/noraid.php', data={'id': '{}'.format(userid)})
is_raider = json.loads(response.text)['raider']
print(is_raider)