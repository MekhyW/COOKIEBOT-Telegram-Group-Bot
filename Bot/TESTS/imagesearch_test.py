import random
import google_images_search
import io
import PIL
googleAPIkey = ''
searchEngineCX = ''

gis = google_images_search.GoogleImagesSearch(googleAPIkey, searchEngineCX, validate_images=False)
my_bytes_io = io.BytesIO()

gis.search({'q': 'e621', 'num': 10, 'safe':'high', 'filetype':'jpg|png'})
try:
    image = gis.results()[random.randint(0, len(gis.results())-1)]
    my_bytes_io.seek(0)
    image.copy_to(my_bytes_io, image.get_raw_data())
    my_bytes_io.seek(0)
    temp_img = PIL.Image.open(my_bytes_io)
    temp_img.show()
except:
    print("Não consegui achar uma imagem (ou era NSFW e eu filtrei)")
