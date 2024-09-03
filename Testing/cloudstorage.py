import datetime
import random
import os
from google.cloud import storage
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'cookiebot-bucket-key.json'
storage_client = storage.Client()

def test_blob(bucket_name, folder):
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=folder)
    bloblist = list(blobs)
    print(len(bloblist))
    #get url of the first blob
    blob = bloblist[random.randint(0, len(bloblist)-1)]
    print(blob.public_url)
    # signed url
    print(blob.generate_signed_url(datetime.timedelta(minutes=15), method='GET'))

test_blob("cookiebot-bucket", "IdeiaDesenho")
