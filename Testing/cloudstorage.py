from google.cloud import storage
import datetime
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../cookiebot-bucket-key.json'
storage_client = storage.Client()

def test_blob(bucket_name, folder):
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=folder)
    bloblist = list(blobs)
    print(len(bloblist))
    print(bloblist[0].name)
    #get url of the first blob
    blob = bucket.blob(bloblist[0].name)
    print(blob.public_url)
    # signed url
    print(blob.generate_signed_url(datetime.timedelta(minutes=15), method='GET'))

test_blob("cookiebot-bucket", "IdeiaDesenho")