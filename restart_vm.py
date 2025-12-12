# Cloud function for restarting the VM, triggered by a Pub/Sub message from Google Cloud Monitoring

import os
import googleapiclient.discovery
from flask import Flask, request

app = Flask(__name__)
project = "PROJECT ID"
zone = "ZONE"
instance = "INSTANCE ID"

@app.post("/")
def restart_vm():
    envelope = request.get_json()
    if not envelope or "message" not in envelope: # Pub/Sub format validation
        return ("", 400)
    compute = googleapiclient.discovery.build("compute", "v1")
    compute.instances.reset(project=project, zone=zone, instance=instance).execute()
    return ("", 204)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
