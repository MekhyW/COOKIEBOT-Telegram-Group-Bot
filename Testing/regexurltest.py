import re
url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
mystring = 'https://www.youtube.com/@CriacoesBakster https://www.geeksforgeeks.org/python-check-url-string/'
urls = re.findall(url_regex, mystring)
for url in urls:
    name = url[0]
    if name.endswith('/'):
        name = name[:-1]
    name = name.split('/')[-1].replace('www.', '')
    print(name)