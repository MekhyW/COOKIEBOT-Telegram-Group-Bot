import requests
DeepaiTOKEN = ''
url = 'https://user-images.githubusercontent.com/3199888/37054504-089d7a00-214d-11e8-8982-ca836f7a4460.jpg'
r = requests.post("https://api.deepai.org/api/torch-srgan", data={'image': '{}'.format(url),},headers={'Api-Key': '{}'.format(DeepaiTOKEN)})
print(r.json()['output_url'])