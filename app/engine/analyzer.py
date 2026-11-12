import json
import yaml
from typing import Optional, List, Dict, Any

from app.schemas.chaos_state import ChaosAnalysisResult, TopologyEdge, NodeImpact
from app.core.session_store import save_room_session, get_room_session
from app.tools.repo_fetcher import extract_github_url, fetch_github_repo, extract_topology_from_files
from app.tools.vuln_scanner import scan_codebase
from app.tools.graph_engine import compute_blast_radius
from app.engine.prompts import SYSTEM_PROMPT
from app.engine.llm_client import call_llm_json  # Your existing LLM wrapper

def _extract_mitigated_services(message: str, known_nodes: List[str]) -> List[str]:
    lower = message.lower()
    if any(k in lower for k in ["what if", "add timeout", "circuit breaker", "add cache", "redis", "fix"]):
        return [n for n in known_nodes if n.lower() in lower]
    return []

def run_autonomous_analysis(message: str, room_id: Optional[str] = None) -> ChaosAnalysisResult:
    session = get_room_session(room_id)
    repo_url = extract_github_url(message)

    target_name = "CustomArchitecture"
    edges: List[Dict[str, str]] = []
    findings: List[Dict[str, Any]] = []

    # Case 1: User provided a live GitHub Repository URL
    if repo_url:
        repo_data = fetch_github_repo(repo_url)
        target_name = repo_data["repo"]
        edges = extract_topology_from_files(repo_data["files"])
        findings = scan_codebase(repo_data["files"])

    # Case 2: User pasted docker-compose YAML directly in chat
    elif "services:" in message:
        target_name = "DockerComposeStack"
        edges = extract_topology_from_files({"docker-compose.yml": message})

    # Case 3: Multi-turn follow-up ("What if we add a timeout on OrderService?")
    elif session and not repo_url:
        target_name = session["target_name"]
        edges = session["edges"]
        findings = session["findings"]

    # Fallback topology if plain-text scenario was entered without repo/YAML
    if not edges:
        edges = [
            {"source": "APIGateway", "target": "OrderService", "coupling": "SYNC"},
            {"source": "OrderService", "target": "PostgreSQL", "coupling": "SYNC"},
            {"source": "OrderService", "target": "PaymentService", "coupling": "SYNC"},
            {"source": "OrderService", "target": "NotificationQueue", "coupling": "ASYNC"},
        ]

    # Pick real discovered vulnerability OR top dependency bottleneck as Fault Node
    if findings:
        top_fault = findings[0]
        fault_node = top_fault["service"]
        fault_reason = top_fault["vulnerability"]
        vuln_file = top_fault["file"]
        vuln_line = top_fault["line"]
        vuln_snippet = top_fault["code_snippet"]
    else:
        fault_node = edges[0]["target"]
        fault_reason = f"Simulated resource exhaustion / timeout in {fault_node}"
        vuln_file = None
        vuln_line = None
        vuln_snippet = None

    known_nodes = list({e["source"] for e in edges} | {e["target"] for e in edges})
    mitigated = _extract_mitigated_services(message, known_nodes)

    # Deterministic NetworkX Blast-Radius Calculation
    blast_nodes = compute_blast_radius(edges, fault_node, fault_reason, mitigated_nodes=mitigated)

    # Save state for future multi-turn follow-ups in this Nonilion room
    save_room_session(room_id, {
        "target_name": target_name,
        "edges": edges,
        "findings": findings
    })

    # Grounded LLM synthesis for explanation + git diff patch
    llm_payload = (
        f"Target: {target_name}\n"
        f"User Query: {message}\n"
        f"Root Fault Node: {fault_node} ({fault_reason})\n"
        f"Vulnerable Location: {vuln_file}:{vuln_line}\n"
        f"Code Snippet:\n{vuln_snippet or 'N/A'}\n"
        f"Deterministic Blast Radius:\n{json.dumps(blast_nodes, indent=2)}"
    )
    llm_out = call_llm_json(SYSTEM_PROMPT, llm_payload)

    return ChaosAnalysisResult(
        target_name=target_name,
        root_cause_summary=llm_out.get("root_cause_summary", fault_reason),
        vulnerable_file=vuln_file,
        vulnerable_line=vuln_line,
        vulnerable_snippet=vuln_snippet,
        edges=[TopologyEdge(**e) for e in edges],
        nodes=[NodeImpact(**n) for n in blast_nodes],
        mitigation_summary=llm_out.get("mitigation_summary", "Enforce strict timeouts and circuit breakers."),
        git_diff_patch=llm_out.get("git_diff_patch", "# No code snippet provided for diff generation.")
    )