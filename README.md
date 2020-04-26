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
  minikube start
  eval $(minikube docker-env)
  ```

- Setup dependent repo

  ```
  git clone https://github.com/sarweshsuman/elastic-worker-autoscaler.git
  cd elastic-worker-autoscaler/
  make
  make install
  make docker-build IMG=elastic-worker-controllers:0.1
  make deploy IMG=elastic-worker-controllers:0.1  
  ```
  This compiles the controller code and builds image and deploys into minikube cluster namespace
  > elastic-worker-autoscaler-system

  Validate pod is up and fine.
  ```
  kubectl get pods -n elastic-worker-autoscaler-system
  ```

- Setup custom metric APIserver adapter

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

- Deploy into kubernetes

  Wait 5 seconds before running next command.
  ```
  cd ..
  kubectl create -f airflow-rabbitmq.yaml
  kubectl create -f airflow-postgres.yaml
  kubectl create -f airflow-flower.yaml
  kubectl create -f airflow-scheduler.yaml
  kubectl create -f elasticcluster-worker.yaml
  kubectl create -f elasticcluster-autoscaler.yaml
  ```
