# Lab Link
https://labs.iximiuz.com/playgrounds/k8s-omni

# Tutorial
Here’s a compact “Hello World” walkthrough in Kubernetes using:

* a **Pod**
* a **Deployment**
* a **Service** (to expose it)

We’ll assume you already have:

* `kubectl` installed and configured to talk to a cluster (kind/minikube/cloud, etc.).
* Docker or some container runtime available (or you can just use a public image).

We’ll use a super simple HTTP server image: `nginxdemos/hello`

---

## 1. Hello World Pod

A **Pod** is the smallest deployable unit in Kubernetes.

### Pod manifest: `hello-pod.yaml`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hello-pod
  labels:
    app: hello
spec:
  containers:
    - name: hello-container
      image: nginxdemos/hello:latest
      ports:
        - containerPort: 80
```

### Apply and test

```bash
kubectl apply -f hello-pod.yaml

# Check status
kubectl get pods

# See pod details
kubectl describe pod hello-pod
```

To quickly test it from **inside** the cluster:

```bash
kubectl exec -it hello-pod -- curl http://localhost
```

Pods are **not** meant to be managed alone in most real apps — they’re ephemeral. That’s where Deployments come in.

---

## 2. Hello World Deployment

A **Deployment** manages **ReplicaSets** and ensures the desired number of Pods are running, handles rolling updates, etc.

### Deployment manifest: `hello-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hello
  template:
    metadata:
      labels:
        app: hello
    spec:
      containers:
        - name: hello-container
          image: nginxdemos/hello:latest
          ports:
            - containerPort: 80
```

### Apply and inspect

```bash
kubectl apply -f hello-deployment.yaml

# See deployment, replicasets, pods
kubectl get deployments
kubectl get rs
kubectl get pods -l app=hello
```

If one pod dies, the Deployment will create a new one.

---

## 3. Expose with a Service

A **Service** gives you a stable virtual IP / DNS name to reach your Pods, even as they get recreated.

We’ll create a **ClusterIP** Service (the default). For local testing on minikube/kind, we can then port-forward to it.

### Service manifest: `hello-service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: hello-service
spec:
  selector:
    app: hello          # must match pod labels
  ports:
    - protocol: TCP
      port: 80          # service port
      targetPort: 80    # containerPort in the pod
  type: ClusterIP
```

### Apply and test

```bash
kubectl apply -f hello-service.yaml

# Check the service
kubectl get service hello-service
```

Now make it reachable from your machine via **port-forward**:

```bash
kubectl port-forward service/hello-service 8080:80
```

Open in browser:

* [http://localhost:8080](http://localhost:8080)

You should see the Hello World page from `nginxdemos/hello`.

---

## 4. Optional: LoadBalancer Service (for cloud clusters)

If your cluster supports external load balancers (AWS, GCP, Azure, etc.), you can change the Service to:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: hello-service
spec:
  selector:
    app: hello
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: LoadBalancer
```

Then:

```bash
kubectl apply -f hello-service.yaml
kubectl get service hello-service
```

You’ll eventually get an **EXTERNAL-IP** to hit directly.

---

## 5. Handy commands cheat sheet

```bash
# See everything
kubectl get pods
kubectl get svc
kubectl get deploy
kubectl get all

# Logs from a pod
kubectl logs <pod-name>

# Edit replicas quickly (without editing yaml)
kubectl scale deployment hello-deployment --replicas=5

# Clean up
kubectl delete -f hello-service.yaml
kubectl delete -f hello-deployment.yaml
kubectl delete -f hello-pod.yaml
```

