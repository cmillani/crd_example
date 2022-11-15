from kubernetes import client, config, watch
import random
import string

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

NAMESPACE = "jupyterhub"
CRD_NAME_PLURAL = "printers"
CRD_KIND = "Printer"
CRD_GROUP = "cadumillani.com.br"
CRD_VERSION = "v1"

v1 = client.CoreV1Api()
crd = client.CustomObjectsApi()

def printInPod(message: str, printer_name: str, printer_uid: str):
    if status != 'pending':
        print(f'Resource already handled')
        return
    letters = string.ascii_lowercase
    random_suffix = ''.join(random.choice(letters) for _ in range(10))
    name = f'print-{random_suffix}'
    
    owner_reference = client.V1OwnerReference(api_version=f'{CRD_GROUP}/{CRD_VERSION}', kind=CRD_KIND, name=printer_name, uid=printer_uid)
    metadata = client.V1ObjectMeta(name=name, owner_references=[owner_reference])
    container = client.V1Container(name=name, image='busybox', args=["/bin/sh", "-c", f"echo \"{message}\""])
    pod_spec = client.V1PodSpec(containers=[container], restart_policy="Never")
    pod_body = client.V1Pod(metadata=metadata, spec=pod_spec, kind='Pod', api_version='v1')
    
    v1.create_namespaced_pod(namespace=NAMESPACE, body=pod_body)
    crd.patch_namespaced_custom_object_status(group=CRD_GROUP, namespace=NAMESPACE, plural=CRD_NAME_PLURAL, version=CRD_VERSION, name=printer_name, body={'status': 'created'})


mywatch = watch.Watch()
for event in mywatch.stream(func=crd.list_namespaced_custom_object,
                          group=CRD_GROUP, namespace=NAMESPACE, plural=CRD_NAME_PLURAL, version=CRD_VERSION):
    event_type = event['type']
    printer_obj = event['object']
    printer_name = printer_obj['metadata']['name']
    printer_uid = printer_obj['metadata']['uid']
    text_to_print = printer_obj['spec']['textToPrint']
    status = printer_obj['status']
    print(f"{event_type} - {text_to_print}")
    if event_type == 'ADDED':
        printInPod(text_to_print, printer_name, printer_uid)
        print("Pod Created!\n")
    elif event_type == 'MODIFIED':
        print('Nothing to do!\n')
    elif event_type == 'DELETED':
        print('OwnerResources will terminate created Pod!\n')



    
    

