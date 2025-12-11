# backend/k8s_ops.py
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from typing import Optional

# Attempt in-cluster config, fall back to kubeconfig
def get_client():
    try:
        config.load_incluster_config()
    except Exception:
        config.load_kube_config()
    return client.CoreV1Api(), client.AppsV1Api(), client.RbacAuthorizationV1Api()

core_v1, apps_v1, rbac_v1 = get_client()

def list_resources(kind: str):
    try:
        kind = kind.lower()
        if kind == "pods":
            pods = core_v1.list_namespaced_pod(namespace="default")
            return [f"{p.metadata.name} {p.status.phase}" for p in pods.items]
        if kind == "deployments":
            deps = apps_v1.list_namespaced_deployment(namespace="default")
            return [f"{d.metadata.name} replicas={d.spec.replicas}" for d in deps.items]
        if kind == "services":
            svcs = core_v1.list_namespaced_service(namespace="default")
            return [f"{s.metadata.name} type={s.spec.type} ports={s.spec.ports}" for s in svcs.items]
        if kind == "nodes":
            nodes = core_v1.list_node()
            return [n.metadata.name for n in nodes.items]
        return [f"Unknown resource kind: {kind}"]
    except ApiException as e:
        return [f"API error: {e}"]

def create_deployment(name: str, image: str, replicas: int = 1):
    container = client.V1Container(
        name=name,
        image=image,
        ports=[client.V1ContainerPort(container_port=80)]
    )
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": name}),
        spec=client.V1PodSpec(containers=[container])
    )
    spec = client.V1DeploymentSpec(replicas=replicas, template=template, selector={'matchLabels': {'app': name}})
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=name),
        spec=spec
    )
    try:
        resp = apps_v1.create_namespaced_deployment(namespace="default", body=deployment)
        return f"Deployment {name} created"
    except ApiException as e:
        if e.status == 409:
            return f"Deployment {name} already exists"
        return f"Error: {e}"

def expose_deployment(name: str, port: int, target_port: Optional[int] = 80, svc_type: str = "NodePort"):
    svc = client.V1Service(
        metadata=client.V1ObjectMeta(name=name),
        spec=client.V1ServiceSpec(
            selector={"app": name},
            ports=[client.V1ServicePort(port=port, target_port=target_port)],
            type=svc_type
        )
    )
    try:
        core_v1.create_namespaced_service(namespace="default", body=svc)
        return f"Service {name} created type={svc_type} port={port}"
    except ApiException as e:
        if e.status == 409:
            return f"Service {name} already exists"
        return f"Error: {e}"

def scale_deployment(name: str, replicas: int):
    try:
        body = {'spec': {'replicas': replicas}}
        apps_v1.patch_namespaced_deployment_scale(name=name, namespace="default", body=body)
        return f"Deployment {name} scaled to {replicas}"
    except ApiException as e:
        return f"Error: {e}"

def delete_resource(kind: str, name: str):
    kind = kind.lower()
    try:
        if kind == "deployment":
            apps_v1.delete_namespaced_deployment(name=name, namespace="default")
            return f"Deleted deployment {name}"
        if kind == "service":
            core_v1.delete_namespaced_service(name=name, namespace="default")
            return f"Deleted service {name}"
        if kind == "pod":
            core_v1.delete_namespaced_pod(name=name, namespace="default")
            return f"Deleted pod {name}"
        return f"Unsupported kind {kind}"
    except ApiException as e:
        return f"Error: {e}"

def delete_all():
    try:
        apps_v1.delete_collection_namespaced_deployment(namespace="default")
        core_v1.delete_collection_namespaced_pod(namespace="default")
        core_v1.delete_collection_namespaced_service(namespace="default")
        return "Deleted all deployments, pods, and services in default namespace (async)"
    except ApiException as e:
        return f"Error: {e}"
