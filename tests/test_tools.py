from app.tools.repo_fetcher import extract_topology_from_files
from app.tools.vuln_scanner import scan_codebase
from app.tools.graph_engine import compute_blast_radius

def test_autonomous_pipeline():
    mock_repo_files = {
        "order_service/db.py": (
            "from sqlalchemy import create_engine\n"
            "import requests\n"
            "engine = create_engine('postgresql://user:pass@db:5432/orders')\n"
            "def charge():\n"
            "    return requests.post('http://payment-service:8000/charge')\n"
        ),
        "notification_worker/worker.py": (
            "import redis\n"
            "r = redis.Redis(host='redis-cache')\n"
        )
    }

    edges = extract_topology_from_files(mock_repo_files)
    findings = scan_codebase(mock_repo_files)
    assert len(findings) >= 2
    assert findings[0]["rule_id"] == "UNBOUNDED_DB_POOL"

    blast = compute_blast_radius(edges, findings[0]["service"], findings[0]["vulnerability"])
    statuses = {n["name"]: n["status"] for n in blast}
    assert statuses["OrderService"] == "FAILED"
    print("All Person 1 autonomous tools passed!", blast)

if __name__ == "__main__":
    test_autonomous_pipeline()