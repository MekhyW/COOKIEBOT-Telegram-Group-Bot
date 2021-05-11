from google_images_download import google_images_download 
import sys
orig_stdout = sys.stdout
f = open('URLS.txt', 'w')
sys.stdout = f
response = google_images_download.googleimagesdownload()
arguments = {"keywords":'stackoverflow', "limit":100, "print_urls":True, "no_download":True}
paths = response.download(arguments)
sys.stdout = orig_stdout
f.close()
with open('URLS.txt') as f:
    content = f.readlines()
f.close()
urls = []
for j in range(len(content)):
    if content[j][:7] == 'Printed':
        urls.append(content[j-1][11:-1])   
print(urls)
print(type(urls))