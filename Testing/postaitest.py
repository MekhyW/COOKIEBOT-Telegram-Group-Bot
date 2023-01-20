import requests

r = requests.post('https://api.simsimi.vn/v2/simtalk', data={'text': 'No!', 'lc': 'pt'})
print(r.json()['message'])