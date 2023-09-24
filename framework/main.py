from kubernetes import client
import kopf
import logging

@kopf.on.create('printers')
def create_fn(body, **kwargs):
    logging.info(f"A handler is called with body: {body}")
    printer_name = body['metadata']['name']
    namespace = body['metadata']['namespace']
    message = body['spec']['textToPrint']
    v1 = client.CoreV1Api()
    
    metadata = client.V1ObjectMeta(name=printer_name)
    container = client.V1Container(name=printer_name, image='busybox', args=["/bin/sh", "-c", f"echo \"{message}\""])
    pod_spec = client.V1PodSpec(containers=[container], restart_policy="Never")
    pod_body = client.V1Pod(metadata=metadata, spec=pod_spec, kind='Pod', api_version='v1')

    kopf.adopt(pod_body)
    
    v1.create_namespaced_pod(namespace=namespace, body=pod_body)
