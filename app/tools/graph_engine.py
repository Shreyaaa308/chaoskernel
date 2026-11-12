import networkx as nx
from typing import List, Dict, Any

def compute_blast_radius(
    edges: List[Dict[str, str]],
    fault_node: str,
    fault_reason: str,
    mitigated_nodes: List[str] | None = None
) -> List[Dict[str, Any]]:
    """
    edges: [{"source": "OrderService", "target": "PostgreSQL", "coupling": "SYNC"}]
    When target fails, upstream callers (source) suffer cascading impact.
    """
    mitigated = {m.lower() for m in (mitigated_nodes or [])}
    G = nx.DiGraph()

    for e in edges:
        G.add_edge(e["source"], e["target"], coupling=e.get("coupling", "SYNC"))

    if fault_node not in G:
        G.add_node(fault_node)

    rev_G = G.reverse(copy=True)
    visited: Dict[str, tuple[str, int, str]] = {
        fault_node: ("FAILED", 0, fault_reason)
    }

    queue = [(fault_node, 0)]
    while queue:
        curr, hop = queue.pop(0)
        curr_status, _, _ = visited[curr]

        for caller in rev_G.neighbors(curr):
            coupling = rev_G[curr][caller].get("coupling", "SYNC")
            next_hop = hop + 1

            # Check if user applied a "what-if" mitigation (timeout / circuit breaker / cache)
            if caller.lower() in mitigated or curr.lower() in mitigated:
                status = "DEGRADED" if curr_status == "FAILED" else "HEALTHY"
                reason = f"Circuit breaker / timeout isolated {caller} from {curr} cascade"
            elif curr_status == "FAILED" and coupling == "SYNC":
                status = "FAILED" if next_hop == 1 else "DEGRADED"
                reason = f"Synchronous dependency on {curr} caused thread/connection starvation"
            elif curr_status in ("FAILED", "DEGRADED") and coupling == "ASYNC":
                status = "DEGRADED"
                reason = f"Async queue backlog building due to {curr} slowdown"
            else:
                status = "HEALTHY"
                reason = f"Isolated from {curr} failure path"

            if caller not in visited:
                visited[caller] = (status, next_hop, reason)
                queue.append((caller, next_hop))

    for node in G.nodes():
        if node not in visited:
            visited[node] = ("HEALTHY", -1, "Decoupled execution path; unaffected")

    results = [
        {"name": node, "status": status, "hop": hop, "reason": reason}
        for node, (status, hop, reason) in visited.items()
    ]

    order = {"FAILED": 0, "DEGRADED": 1, "HEALTHY": 2}
    results.sort(key=lambda x: (order[x["status"]], x["hop"]))
    return results