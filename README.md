# Kubernetes Operator
This is a demo project exploring the creation of a Kubernetes Operator in python.

The file `crd.yaml` creates a custom resource, `main.py` is the control loop, and `my-printer.yaml` is an example custom object. This custom resource, called **Printer**, simply asks the controller to create a `Pod` that will print a given text to the standard output 
> note: no sanitization is done to the input, which presents a risk, but this repo is intended simply as a learning tool

# How to use
You must have a working kubernetes cluster and a config file, then simply:

```sh
kubectl apply -f crd.yaml

# you should use a venv before running the steps bellow
pip install -r requirements.txt # update kubernetes version according to your cluster
```

To run without a framework: 
> Folder **no-framework** shows an example of building an operator with only the kubernetes library.
In most cases it is pretty simple, but guaranteeing that all resources are watched is not as simple as demonstrated on this example, since old resources are not returned by the code showed (in the version of kubernetes and library used for the tests in 2022);
```sh
python no-framework/main.py
```

To run with `kopf` framework
> Folder **framework** demonstrates using kopf to make things a little easier!
```sh
kopf run framework/main.py --verbose
```

The above code will start listening for any resources. **On another shell**:

```sh
kubectl apply -f my-printer.yaml
# Wait a few moments
kubectl get pods # Wait ultil the pod is "completed"
kubectl logs print-wrgtvjcydk # Check for the name your controller created
# You should see "Hello Kube!" logged if you haven't modified my-printer.yaml
kubectl delete -f my-printer.yaml # This will also delete the Pod, since there is an OwnerReference
```

# So, what is this for?
An Operator is simply a pod that listens for a Custom Resource. [This section](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/#should-i-use-a-configmap-or-a-custom-resource) of the official documentation gives a good idea of scenarios where a simple `ConfigMap` would suffice. I've used this pattern to allow the creation of `Jobs` based on some business criteria, this way the resources needed for the containers would only be reserved when necessary, which reduced stress on our auto scaller, made control loops shorter and generated savings :)