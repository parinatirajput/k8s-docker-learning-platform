# backend/app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import k8s_ops
import docker_ops

app = FastAPI(title="K8s Docker Learning API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # LOCK DOWN in production
    allow_methods=["GET", "POST", "DELETE", "PATCH"],
    allow_headers=["*"],
)

class CreateDeployment(BaseModel):
    name: str
    image: str
    replicas: int = 1

class ExposeService(BaseModel):
    name: str
    port: int
    target_port: int = 80
    type: str = "NodePort"

class ScaleRequest(BaseModel):
    name: str
    replicas: int

class DeleteRequest(BaseModel):
    kind: str
    name: str

@app.get("/health")
def health():
    return {"status": "ok"}

# Docker endpoints
@app.get("/docker/images")
def api_list_images():
    try:
        return {"images": docker_ops.list_images()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/docker/containers")
def api_list_containers():
    try:
        return {"containers": docker_ops.list_containers()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/docker/run")
def api_run_container(name: str, image: str):
    try:
        return {"result": docker_ops.run_container(name, image)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/docker/stop")
def api_stop_container(name: str):
    try:
        return {"result": docker_ops.stop_container(name)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Kubernetes endpoints (restricted helpers)
@app.get("/k8s/list/{kind}")
def k8s_list(kind: str):
    return {"items": k8s_ops.list_resources(kind)}

@app.post("/k8s/deployment")
def k8s_create_deployment(req: CreateDeployment):
    # basic validation
    if not req.name.isalnum() and "-" not in req.name:
        raise HTTPException(status_code=400, detail="Invalid name")
    return {"result": k8s_ops.create_deployment(req.name, req.image, req.replicas)}

@app.post("/k8s/expose")
def k8s_expose(req: ExposeService):
    return {"result": k8s_ops.expose_deployment(req.name, req.port, req.target_port, req.type)}

@app.post("/k8s/scale")
def k8s_scale(req: ScaleRequest):
    return {"result": k8s_ops.scale_deployment(req.name, req.replicas)}

@app.post("/k8s/delete")
def k8s_delete(req: DeleteRequest):
    return {"result": k8s_ops.delete_resource(req.kind, req.name)}

@app.delete("/k8s/delete_all")
def k8s_delete_all():
    return {"result": k8s_ops.delete_all()}
