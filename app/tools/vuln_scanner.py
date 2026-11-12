import re
from typing import Dict, List, Any
from app.tools.repo_fetcher import _infer_service_name

VULN_RULES = [
    {
        "id": "UNBOUNDED_DB_POOL",
        "pattern": r"create_engine\((?![^)]*pool_timeout)[^)]*\)",
        "severity": "CRITICAL",
        "description": "SQLAlchemy engine created without pool_timeout or pool_pre_ping; causes connection pool exhaustion under spike."
    },
    {
        "id": "MISSING_HTTP_TIMEOUT",
        "pattern": r"requests\.(get|post|put|delete)\((?![^)]*timeout\s*=)[^)]*\)",
        "severity": "HIGH",
        "description": "Synchronous Python requests call lacks timeout parameter; upstream latency will exhaust worker threads."
    },
    {
        "id": "AXIOS_NO_TIMEOUT",
        "pattern": r"axios\.(get|post|put|delete)\((?![^)]*timeout)[^)]*\)",
        "severity": "HIGH",
        "description": "Axios HTTP request has no timeout or circuit breaker; susceptible to cascading hang."
    },
    {
        "id": "HTTPX_NO_TIMEOUT",
        "pattern": r"httpx\.(get|post|AsyncClient)\((?![^)]*timeout)[^)]*\)",
        "severity": "HIGH",
        "description": "HTTPX client missing explicit timeout bounds."
    },
    {
        "id": "SILENT_EXCEPTION_SWALLOW",
        "pattern": r"except\s*(Exception)?\s*:\s*\n\s*pass",
        "severity": "MEDIUM",
        "description": "Silent exception suppression masks downstream service failures and delays circuit breaking."
    }
]

def scan_codebase(files: Dict[str, str]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []

    for filepath, content in files.items():
        if not filepath.endswith((".py", ".js", ".ts")):
            continue
        lines = content.splitlines()
        service_name = _infer_service_name(filepath)

        for rule in VULN_RULES:
            for match in re.finditer(rule["pattern"], content):
                line_no = content[:match.start()].count("\n") + 1
                start_idx = max(0, line_no - 3)
                end_idx = min(len(lines), line_no + 3)
                snippet = "\n".join(f"{i+1}: {lines[i]}" for i in range(start_idx, end_idx))

                findings.append({
                    "service": service_name,
                    "file": filepath,
                    "line": line_no,
                    "rule_id": rule["id"],
                    "severity": rule["severity"],
                    "vulnerability": rule["description"],
                    "code_snippet": snippet
                })

    rank = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2}
    findings.sort(key=lambda x: rank.get(x["severity"], 3))
    return findings