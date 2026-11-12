from pydantic import BaseModel
from typing import List, Optional

class TopologyEdge(BaseModel):
    source: str
    target: str
    coupling: str = "SYNC"  # "SYNC" | "ASYNC"

class NodeImpact(BaseModel):
    name: str
    status: str             # "FAILED" | "DEGRADED" | "HEALTHY"
    hop: int                # 0 = root cause, 1 = direct caller, -1 = unaffected
    reason: str

class ChaosAnalysisResult(BaseModel):
    target_name: str
    root_cause_summary: str
    vulnerable_file: Optional[str] = None
    vulnerable_line: Optional[int] = None
    vulnerable_snippet: Optional[str] = None
    edges: List[TopologyEdge]
    nodes: List[NodeImpact]
    mitigation_summary: str
    git_diff_patch: str