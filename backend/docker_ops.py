# backend/docker_ops.py
import docker
from docker.errors import DockerException

def get_docker_client():
    try:
        client = docker.from_env()
        # quick ping
        client.ping()
        return client
    except DockerException as e:
        raise RuntimeError("Docker not available or socket not mounted: " + str(e))

def list_images():
    c = get_docker_client()
    images = c.images.list()
    return [", ".join(img.tags) or img.short_id for img in images]

def list_containers(all_containers=True):
    c = get_docker_client()
    conts = c.containers.list(all=all_containers)
    return [f"{ct.name} ({ct.status}) image={ct.image.tags}" for ct in conts]

def run_container(name: str, image: str, detach=True):
    c = get_docker_client()
    try:
        ct = c.containers.run(image, name=name, detach=detach)
        return f"Container {name} started from {image}"
    except Exception as e:
        return f"Error running container: {e}"

def stop_container(name: str):
    c = get_docker_client()
    try:
        ct = c.containers.get(name)
        ct.stop()
        return f"Stopped container {name}"
    except Exception as e:
        return f"Error stopping container: {e}"
