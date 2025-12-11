// frontend/app.js
const API_BASE = "/api"; // if you deploy behind ingress, route /api -> backend

function showOutput(text) {
  document.getElementById("output").value = Array.isArray(text) ? text.join("\n") : (text || "");
}

async function listImages(){
  try {
    const res = await fetch("/api/docker/images");
    const data = await res.json();
    showOutput(data.images);
  } catch (e) {
    showOutput("Error: " + e);
  }
}

async function listContainers(){
  try {
    const res = await fetch("/api/docker/containers");
    const data = await res.json();
    showOutput(data.containers);
  } catch (e) {
    showOutput("Error: " + e);
  }
}

async function runDocker(){
  const name = document.getElementById("cmdName").value;
  const image = document.getElementById("cmdImage").value;
  try {
    const res = await fetch(`/api/docker/run?name=${encodeURIComponent(name)}&image=${encodeURIComponent(image)}`, { method: "POST" });
    const data = await res.json();
    showOutput(data.result);
  } catch (e) {
    showOutput("Error: " + e);
  }
}

/* Kubernetes helpers */
async function k8sList(kind) {
  try {
    const res = await fetch(`/api/k8s/list/${kind}`);
    const data = await res.json();
    showOutput(data.items);
  } catch (e) {
    showOutput("Error: " + e);
  }
}

async function createDeployment() {
  const name = document.getElementById("dep_name").value;
  const image = document.getElementById("dep_image").value;
  const replicas = parseInt(document.getElementById("dep_replicas").value || "1");
  try {
    const res = await fetch("/api/k8s/deployment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, image, replicas })
    });
    const data = await res.json();
    showOutput(data.result);
  } catch (e) {
    showOutput("Error: " + e);
  }
}

async function exposeDeployment() {
  const name = document.getElementById("dep_name").value;
  let port = parseInt(prompt("Enter port to expose (eg 30080):", "30080"));
  if (!port) return;
  try {
    const res = await fetch("/api/k8s/expose", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, port, target_port: 80, type: "NodePort" })
    });
    const data = await res.json();
    showOutput(data.result);
  } catch (e) {
    showOutput("Error: " + e);
  }
}

async function scaleDeployment() {
  const name = document.getElementById("scale_name").value;
  const replicas = parseInt(document.getElementById("scale_replicas").value || "1");
  try {
    const res = await fetch("/api/k8s/scale", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, replicas })
    });
    const data = await res.json();
    showOutput(data.result);
  } catch (e) {
    showOutput("Error: " + e);
  }
}

async function deleteAll() {
  if (!confirm("Delete all deployments/pods/services in default namespace?")) return;
  try {
    const res = await fetch("/api/k8s/delete_all", { method: "DELETE" });
    const data = await res.json();
    showOutput(data.result);
  } catch (e) {
    showOutput("Error: " + e);
  }
}
