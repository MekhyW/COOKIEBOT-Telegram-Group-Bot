import random
import requests
import json

def get_reddit_img(sub):
  resposta = json.loads(requests.get("https://reddit.com/r/{0}/random.json".format(sub), headers={'User-agent': 'your bot 0.1'}).text)
  try:
    nunes = resposta[0]['data']['children'][0]['data']['url']
    x = str(nunes)
    return x
  except KeyError:
    try:
      nunes = resposta[0]['data']['children'][0]['data']['url_overriden_by_dest']
      x = str(nunes)
      return x
    except:
      pass

def get_reddit_video(sub):
  resposta = requests.get("https://reddit.com/r/{0}/random.json".format(sub), headers={'User-agent': 'your bot 0.1'})
  vai = resposta.text
  dados = json.loads(vai)
  batata = dados[0]['data']['children'][0]['data']['media_embed']['content']
  x = "&lt;iframe src=\""
  batata = str(batata).replace(x,'')
  return batata

def get_reddit_img1(sub):
  resposta = requests.get("https://reddit.com/r/{0}/random.json".format(sub), headers={'User-agent': 'your bot 0.1'})
  vai = resposta.text
  dados = json.loads(vai)
  nunes = dados[0]['data']['children'][0]['data']['url']
  x = str(nunes)
  return (x)

def get_reddit_img2(sub):
  resposta = requests.get("https://reddit.com/r/{0}/random.json".format(sub), headers={'User-agent': 'your bot 0.1'})
  vai = resposta.text
  dados = json.loads(vai)
  nunes = dados[0]['data']['children'][0]['data']['url_overriden_by_dest']
  x = str(nunes)
  return (x)


print(get_reddit_img('essamerdanaoexiste'))