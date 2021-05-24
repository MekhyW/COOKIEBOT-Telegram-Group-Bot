#https://googleapis.dev/python/vision/latest/index.html

#CROP_HINTS = 9
#DOCUMENT_TEXT_DETECTION = 11
#FACE_DETECTION = 1
#IMAGE_PROPERTIES = 7¶
#LABEL_DETECTION = 4
#LANDMARK_DETECTION = 2
#LOGO_DETECTION = 3
#OBJECT_LOCALIZATION = 19
#PRODUCT_SEARCH = 12
#SAFE_SEARCH_DETECTION = 6
#TEXT_DETECTION = 5
#TYPE_UNSPECIFIED = 0
#WEB_DETECTION = 10
from google.cloud import vision
googlevision_client = vision.ImageAnnotatorClient()
response = googlevision_client.annotate_image({'image': {'source': {'image_uri': 'IMAGE_ADDRESS_HERE'}},'features': [{'type_': vision.Feature.Type.FACE_DETECTION}]})