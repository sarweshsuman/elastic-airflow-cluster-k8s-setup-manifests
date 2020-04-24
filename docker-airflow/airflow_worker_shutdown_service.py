# Flask application to receive worker shutdown request in bunch
from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# configs
CELERY_QUEUE = os.environ.get("CELERY_DEFAULT_QUEUE_NAME","celery")
FLOWER_SHUTDOWN_URL = "http://localhost:5555/api/worker/shutdown/"+CELERY_QUEUE+"@"
SERVER_PORT = int(os.environ.get("SERVER_PORT","5559"))

@app.route('/api/worker/shutdown',methods=["POST"])
def shutdownAirflowWorkers():
    workers = request.get_json()['shutdown_workers']
    print("request received for shutting down airflow worker pods: {}".format(workers))
    for worker in workers:
        URL = FLOWER_SHUTDOWN_URL+worker
        resp = requests.post(URL,headers={"content-length":"0"})
        if resp.status_code != 200:
            return jsonify({"status":"failed"}), resp.status_code
    return jsonify({"status":"success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=SERVER_PORT)
