# elastic-airflow-cluster-k8s-setup-manifests

This repo contains dockerfiles/yaml for airflow cluster components.

## setting up for demo on mac

- setup minikube

  Install minikube
  ```
  https://kubernetes.io/docs/tasks/tools/install-minikube/
  ```

  Make sure minikube vm has enough cpu and memory to run several pods.
  ```
  minikube start --cpus 4 --memory 10240
  eval $(minikube docker-env)
  ```

  **Important:**
  *Create below directories within minikube vm, by logging into the vm.
  These directories are for dags/logs folder and we will be mounting these into pods for sharing & persistence.*
  ```
  minikube ssh
  sudo mkdir dags
  sudo mkdir logs
  sudo chmod -R 777 dags
  sudo chmod -R 777 logs
  logout
  ```
  This has to be done every time you restart minikube.
  You can avoid this by creating a mount from your local mac to above path in minikube vm.
  For demo, i am sticking with this manual step.

- Setup dependent repo

  This repo has **ElasticWorker/ElasticWorkerAutoscaler** CRD and controllers code.

  ```
  git clone https://github.com/sarweshsuman/elastic-worker-autoscaler.git
  cd elastic-worker-autoscaler/
  make
  make install
  make docker-build IMG=elastic-worker-controllers:0.1
  make deploy IMG=elastic-worker-controllers:0.1  
  ```
  This compiles the controller code and builds image and deploys into minikube cluster namespace *elastic-worker-autoscaler-system*.

  Validate pod is up and fine.
  ```
  kubectl get pods -n elastic-worker-autoscaler-system
  ```

- Setup custom metric APIserver adapter

  This repo has custom metric adapter code which works closely with ElasticWorkerAutoscaler controller.

  *This setup can be replaced with Prometheus setup if moving into production.*

  ```
  git clone https://github.com/sarweshsuman/elastic-worker-custommetrics-adapter.git
  cd elastic-worker-custommetrics-adapter/
  GOOS=linux go build -o docker/
  cd docker/
  docker build -t elasticworker-custommetric-adapter:0.1 .
  ```

  This builds custom metric adapter and creates a docker image.
  Now we will deploy it into minikube.

  ```
  cd ../manifest
  kubectl create -f redis-metric-db.yaml
  kubectl create -f elasticworker-adapter.yaml
  ```

  Validate all pods are up and fine.
  ```
  kubectl get pods -n elasticworker-custommetrics
  ```

  Goto https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/#support-for-metrics-apis for more info on how to setup custom metrics.


- Clone this repo.

  ```
  git clone https://github.com/sarweshsuman/elastic-airflow-cluster-k8s-setup-manifests.git
  cd elastic-airflow-cluster-k8s-setup-manifest/
  ```

- Build rest of the components images

  Build airflow image, will be common for scheduler, worker, flower.
  ```
  cd docker-airflow/
  docker build -t airflow-slim:0.1 .
  ```

  Build postgres image
  ```
  cd ../docker-postgres/
  docker build -t airflow-postgres:0.1 .
  ```

  Build rabbitmq image
  ```
  cd ../docker-rabbitmq/
  docker build -t airflow-rabbitmq:0.1 .
  ```

  All needed images are now built.

  Validate all images are created.
  ```
  docker image ls
  ```

- Deploy into minikube

  Wait 5 seconds before running subsequent command, to avoid putting all load at once on your mac.
  ```
  cd ..
  kubectl create -f airflow-rabbitmq.yaml
  kubectl create -f airflow-postgres.yaml
  kubectl create -f airflow-scheduler.yaml
  kubectl create -f airflow-flower.yaml
  kubectl create -f elasticcluster-worker.yaml
  kubectl create -f elasticcluster-autoscaler.yaml
  ```

  Validate all pods are up and running fine.
  ```
  kubectl get pods
  ```

- Test the cluster with a DAG.

  To test we will have to first login into minikube vm and create a DAG file.

  Sample dag is at - https://github.com/sarweshsuman/elastic-airflow-cluster-k8s-setup-manifests/tree/master/sample-dags

  ```
  minikube ssh
  cd dags
  cat>dag_1.py
  ....PASTE CONTENT FROM SAMPLE DAG....
  ctrl-d
  logout
  ```

  Trigger the DAG from within scheduler pod.

  ```
  kubectl get pods
  kubectl exec -it airflow-scheduler-76d5df7b9b-948k2 bash
  >cd dags/
  >airflow unpause dag_1
  >airflow trigger_dag dag_1
  >logout
  ```
  This will trigger the DAG. If everything is fine, worker will execute it.
  Note, you might see error in unpausing the dag, it is because scheduler has not yet picked the dag yet. If you retry this     issue will go away. Alternatively, you could use -sd mention the subdirectory manully.
  You can open the flower UI for checking the status of the cluster.
  ```
  kubectl cluster-info
  ```

  - COPY ip, for example:- 192.168.64.8
  - Open browser and paste,
    http://192.168.64.8:31000/dashboard
