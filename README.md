# elastic-airflow-cluster-k8s-setup-manifests

This repo contains dockerfiles/yaml for airflow cluster components.

## setting up for demo

- Setup dependent repo & build image & deploy in local minikube

  ```
  git clone https://github.com/sarweshsuman/elastic-worker-autoscaler.git
  cd elastic-worker-autoscaler/
  make
  make install
  make docker-build IMG=elastic-worker-controllers:0.1
  make deploy IMG=elastic-worker-controllers:0.1  
  ```
  This compiles the controller code and builds image and deploys into kubernetes cluster namespace
  > elastic-worker-autoscaler-system

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
