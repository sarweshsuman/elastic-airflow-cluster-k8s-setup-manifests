# Application to pull metrics from flask and push to redis metric db
import redis
import os
import requests
import time
import sys, traceback
import math

# configs
REDIS_HOST=os.environ.get("REDIS_METRIC_HOST","redis-metric-db.elasticworker-custommetrics.svc.cluster.local")
REDIS_PORT=int(os.environ.get("REDIS_METRIC_PORT","6379"))
REDIS_DB=int(os.environ.get("REDIS_METRIC_DB","0"))
FLOWER_WORKER_LIST_URL="http://localhost:5555/api/workers?refresh=True"
FLOWER_WORKER_STATUS_URL="http://localhost:5555/api/workers?refresh=True&status=True"
CELERY_WORKER_CONCURRENCY=int(os.environ.get("CELERY_WORKER_CONCURRENCY","16"))
NAMESPACE=os.environ.get("NAMESPACE","default")
METRIC_NAME_FORMAT=os.environ.get("POD_METRIC_NAME_FORMAT","elasticclustermetric_{}_{}_{}")
CLUSTER_NAME=os.environ.get("CLUSTER_NAME","UNKNOWN_CLUSTER_NAME")

def create_redis_connection():
    redis_conn = redis.Redis(host=REDIS_HOST,port=REDIS_PORT,db=REDIS_DB)
    return redis_conn

def poll_list_of_workers():
    print("polling for list of workers")
    resp = requests.get(FLOWER_WORKER_LIST_URL)
    if resp.status_code != 200:
        print("response status code is not 200: {}, text: {}".format(resp.status_code,resp.text))
        return {}
    return resp.json()

def poll_status_of_workers():
    print("retrieving status of all workers")
    resp = requests.get(FLOWER_WORKER_STATUS_URL)
    if resp.status_code != 200:
        print("response status code is not 200: {}, text: {}".format(resp.status_code,resp.text))
        return {}
    return resp.json()

if __name__ == '__main__':
    print("Connecting to redis {}".format(REDIS_HOST))
    while True:
        try:
            redis_conn = create_redis_connection()
            print("Connected to redis {}".format(redis_conn.ping()))
            break
        except Exception as e:
            print("exception while connecting to redis {}".format(e))
            time.sleep(2)

    print("Starting metrics_logger")
    while True:
        print("starting pass")
        try:
            workers_list = poll_list_of_workers()
            workers_status = poll_status_of_workers()
            print("list of workers found {}".format(workers_list.keys()))
            total_active_tasks = 0
            actual_active_workers = []
            for worker in workers_list.keys():
                if workers_status[worker] == False:
                    continue
                actual_active_workers.append(worker)
                no_of_active_tasks = len(workers_list[worker]['active'])
                load = math.ceil(100 * (no_of_active_tasks/CELERY_WORKER_CONCURRENCY))
                # fixed metric name load
                pod_name = worker.split("@")[1]
                metric_name = METRIC_NAME_FORMAT.format(NAMESPACE,pod_name,"load")
                redis_conn.set(metric_name,load)
                total_active_tasks += no_of_active_tasks
            total_cluster_load = math.ceil(100 * (total_active_tasks / (len(actual_active_workers)*CELERY_WORKER_CONCURRENCY)))
            metric_name = METRIC_NAME_FORMAT.format(NAMESPACE,CLUSTER_NAME,"total_cluster_load")
            redis_conn.set(metric_name,total_cluster_load)
        except Exception as e:
            print("Exception received {}".format(e))
            traceback.print_exc(file=sys.stdout)
        print("pass complete")
        time.sleep(2)
