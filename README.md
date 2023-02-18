Stock Trading API Deployment
============================

This is a stock trading API that consumes messages from a messaging queue to update stock prices and mark them as hit when a target is reached. The API is built using Flask and the system is deployed on a Kubernetes cluster using Helm.

Prerequisites
-------------

Before running this project, you need to have the following installed:

-   Docker
-   Minikube
-   kubectl
-   Helm

How to Run
----------

### Clone the Repository

`git clone https://github.com/marwanakeel/stock-task`

`cd stock-task`

### Start Minikube

`minikube start`

to check the logs

`minikube start --alsologtostderr -v=1` 
### Create a NS for THNDR and change context

`kubectl create ns thndr`

`kubectl config set-context --current --namespace=thndr`

###  Set your local Docker environment to use the Minikube Docker registry.

`eval $(minikube docker-env)`

To return back to local docker env

`eval $(docker-machine env -u)`


### Setup the queues

`kubectl run vernemq --image=erlio/docker-vernemq --env="DOCKER_VERNEMQ_ACCEPT_EULA=yes" --env="DOCKER_VERNEMQ_ALLOW_ANONYMOUS=on" --env="MQTT_TOPIC=thndr-trading"`

`kubectl expose pod vernemq --port=1883 --target-port=1883 --name=vernemq-service --type=ClusterIP`

`kubectl run streamer --image=thndr/streamer:0.2 --env="MQTT_HOST=vernemq-service" --env="MQTT_PORT=1883" --env="MQTT_TOPIC=thndr-trading"`

`kubectl expose pod streamer --type=ClusterIP --name=streamer-service --port=1883 --target-port=1883`

### Build the api image

`docker build -t stock-task:v1 .`

### Install the helm
`helm install thndr-api k8s/thndr-api`

or upgrate in case it was already there

`helm upgrade thndr-api k8s/thndr-api`

### Access the API

To access the API, you can use the IP address of the minikube cluster and the exposed port of the stock trading API service:

`minikube service thndr-api -n thndr`


### Deploy Prometheus

Prometheus will be used to scrape metrics from the stock trading API. The following command will deploy Prometheus using the Helm chart:
`helm repo add prometheus-community https://prometheus-community.github.io/helm-charts`

`helm repo update`

`helm install prometheus prometheus-community/prometheus`

### Deploy Grafana

Grafana can be used to visualize the metrics collected by Prometheus. The following command will deploy Grafana using the Helm chart:
`helm repo add grafana https://grafana.github.io/helm-charts`

`helm repo update`

`helm install grafana grafana/grafana --values k8s/grafana/my-values.yaml`
### Access the Grafana

`minikube service grafana -n thndr`

### Add Prometheus Data Source
http://prometheus-server:80

### Import Dashboard
https://grafana.com/grafana/dashboards/11663-k8s-cluster-metrics/