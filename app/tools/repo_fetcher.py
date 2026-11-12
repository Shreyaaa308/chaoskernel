import re
import yaml
import requests
from typing import Dict, List, Any

GITHUB_API = "https://api.github.com/repos"

def extract_github_url(text: str) -> str | None:
    match = re.search(r"https?://github\.com/[^/\s]+/[^/\s#?]+", text)
    return match.group(0) if match else None

def parse_github_url(url: str) -> tuple[str, str]:
    match = re.search(r"github\.com/([^/]+)/([^/\s#?]+)", url)
    if not match:
        raise ValueError("Invalid GitHub URL")
    return match.group(1), match.group(2).replace(".git", "")

def fetch_github_repo(repo_url: str, max_files: int = 25) -> Dict[str, Any]:
    owner, repo = parse_github_url(repo_url)
    res = None
    active_branch = "main"

    for branch in ["main", "master"]:
        tree_url = f"{GITHUB_API}/{owner}/{repo}/git/trees/{branch}?recursive=1"
        r = requests.get(tree_url, timeout=10)
        if r.status_code == 200:
            res = r
            active_branch = branch
            break

    if not res:
        raise RuntimeError(f"Could not access repository {owner}/{repo} (ensure it is public).")

    tree = res.json().get("tree", [])
    target_exts = (".py", ".js", ".ts", ".go", ".yml", ".yaml")
    fetched_files: Dict[str, str] = {}

    for item in tree:
        path = item["path"]
        if item["type"] == "blob" and path.endswith(target_exts):
            if any(skip in path.lower() for skip in ["node_modules/", "venv/", ".git/", "__pycache__/", "test"]):
                continue
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{active_branch}/{path}"
            file_res = requests.get(raw_url, timeout=8)
            if file_res.status_code == 200:
                fetched_files[path] = file_res.text[:15000]
            if len(fetched_files) >= max_files:
                break

    return {"repo": f"{owner}/{repo}", "files": fetched_files}

def _infer_service_name(filepath: str) -> str:
    parts = [p for p in filepath.split("/") if p not in ("src", "app", "services", "lib")]
    raw = parts[0] if parts else filepath
    name = re.sub(r"\.(py|js|ts|go)$", "", raw)
    return "".join(word.capitalize() for word in re.split(r"[-_]", name)) or "CoreService"

def extract_topology_from_files(files: Dict[str, str]) -> List[Dict[str, str]]:
    edges: List[Dict[str, str]] = []
    seen = set()

    def add_edge(src: str, tgt: str, coupling: str = "SYNC"):
        if src and tgt and src.lower() != tgt.lower() and (src, tgt) not in seen:
            seen.add((src, tgt))
            edges.append({"source": src, "target": tgt, "coupling": coupling})

    # 1. Primary: Parse docker-compose.yml
    for path, content in files.items():
        if "compose" in path.lower() and path.endswith((".yml", ".yaml")):
            try:
                data = yaml.safe_load(content) or {}
                for svc_name, cfg in (data.get("services") or {}).items():
                    deps = cfg.get("depends_on", [])
                    if isinstance(deps, dict):
                        deps = list(deps.keys())
                    for dep in deps:
                        coupling = "ASYNC" if any(k in dep.lower() for k in ["kafka", "rabbit", "redis", "sqs", "celery", "worker"]) else "SYNC"
                        add_edge(svc_name, dep, coupling)
            except yaml.YAMLError:
                continue

    if edges:
        return edges

    # 2. Fallback: Infer dependencies from HTTP URLs, DB drivers, and message queues in code
    service_url_pattern = re.compile(r"https?://([a-zA-Z0-9_-]+)(?::\d+|/)")
    for path, content in files.items():
        if not path.endswith((".py", ".js", ".ts", ".go")):
            continue
        caller = _infer_service_name(path)

        # Detect internal microservice HTTP calls (e.g., http://payment-service:8000/pay)
        for match in service_url_pattern.finditer(content):
            host = match.group(1)
            if host not in ("localhost", "127.0.0.1", "github.com", "api.openai.com"):
                target = "".join(w.capitalize() for w in re.split(r"[-_]", host))
                add_edge(caller, target, "SYNC")

        # Detect Database & Cache dependencies
        lower_c = content.lower()
        if any(db in lower_c for db in ["psycopg2", "sqlalchemy", "postgresql://", "asyncpg"]):
            add_edge(caller, "PostgreSQL", "SYNC")
        if any(db in lower_c for db in ["pymongo", "mongoose", "mongodb://"]):
            add_edge(caller, "MongoDB", "SYNC")
        if "redis" in lower_c:
            add_edge(caller, "RedisCache", "ASYNC")
        if any(q in lower_c for q in ["kafka", "pika", "celery", "bullmq"]):
            add_edge(caller, "MessageBroker", "ASYNC")

    return edges