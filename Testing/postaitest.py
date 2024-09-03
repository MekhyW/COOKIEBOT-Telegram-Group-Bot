import requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"

r = requests.post('https://api.simsimi.vn/v2/simtalk', data={'text': 'Qual o seu problema?', 'lc': 'pt'}, headers={"User-Agent": USER_AGENT}, timeout=10)
print(r.json()['message'])
