# datadog-hpa
A minimal example showcasing how autoscale Kubernetes workloads with any Datadog metric or custom query. You can refer to [the Datadog documentation](https://docs.datadoghq.com/containers/guide/cluster_agent_autoscaling_metrics/?tab=helm) for more details. Also, having an understanding for how Horizontal Pod Autoscaling in Kubernetes works is recommended. Have a read through [this piece](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/#algorithm-details) of documentation.
## Requirements
1. A Kubernetes cluster. Sandbox-like clusters such as [Rancher Desktop](https://rancherdesktop.io/) or [minikube](https://minikube.sigs.k8s.io/docs/start/) are recommended for trying out this example.
2. A Datadog account. You can get started with a free Datadog trial [here](https://www.datadoghq.com/dg/monitor/free-trial).
3. A Datadog Agent and Cluster Agent running in your cluster. Following [the Helm-based installation steps](https://docs.datadoghq.com/containers/kubernetes/installation/?tab=helm#installation) will greatly simplify the task.
4. Configure your Agent's deployment to [support DogStatsD metrics](https://docs.datadoghq.com/developers/dogstatsd/?tab=helm#setup) as well as an [external metrics server for the Datadog Cluster Agent](https://docs.datadoghq.com/containers/guide/cluster_agent_autoscaling_metrics/?tab=helm#installation).
Once all of the steps above are completed, you should have a values file like so:
```yaml
datadog:
  apiKeyExistingSecret: datadog-secret
  appKeyExistingSecret: datadog-secret
  site: datadoghq.com
  dogstatsd:
    port: 8125
    useHostPort: true
    nonLocalTraffic: true

clusterAgent:
  enabled: true
  metricsProvider:
    enabled: true
    useDatadogMetrics: true
```
This file is provided, and this README will cover the Agent's deployment. That said, it's highly recommended that you review the documentation links above to understand the overall logic behind this example (and to understand how to do it in case you are not using Helm).
## Running the Example
For starters, you'll need to deploy node Datadog Agents as well as a Cluster Agent. Here are the steps for doing so with Helm:
1. Install [Helm](https://v3.helm.sh/docs/intro/install/#through-package-managers).
2. `helm repo add datadog https://helm.datadoghq.com`
3. `helm repo update`
4. `kubectl create secret generic datadog-secret --from-literal api-key=$DD_API_KEY --from-literal app-key=$DD_APP_KEY`
5. Clone this repo (e.g. `git clone git@github.com:nsuarezcanton/datadog-hpa.git`) and `cd` into it.
6. `helm install datadog-agent -f datadog-values.yaml --set targetSystem=linux datadog/datadog`.

Note that this assumes that `$DD_API_KEY` and `$DD_APP_KEY` are environment variables set in your current shell session.
### Custom Metrics
Let's start by deploying a service that will submit custom metrics under the namespace `datadog.examples.kubernetes_hpa.custom`:
```
kubectl apply -f custom-metrics-deployment.yaml
```
### nginx Deployment
Let's then apply our nginx deployment. Though this is used as a "dummy" deployment, it will be scaled up (and down) based on the value of the custom metric that's being submitted by our `custom-metrics-deployment.yaml`. To apply the nginx:
```
kubectl apply -f nginx-deployment.yaml
```
### Datadog Metric Custom Resource
Now, the custom metrics service and the nginx pods have been deployed. The next step is to deploy a Custom Resource `DatadogMetric` where the Cluster Agent will store the value from the metric query. Keep in mind that the Cluster Agent is acting as a metric server. To apply the CRD:
```
kubectl apply -f crd-datadog-metric.yaml
```
### Horizontal Pod Autoscaler

The final step is to wire up a HPA resource to scale the `nginx-deployment` based on the value of the `hpa-metric`. To apply the HPA:
```
kubectl apply -f hpa-datadog-metric.yaml
```