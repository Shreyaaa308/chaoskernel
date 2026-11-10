from pydantic import BaseModel, Field
from typing import Dict, List, Literal

NodeStatus = Literal["FAILED", "DEGRADED", "HEALTHY"]

class ChaosAnalysisResult(BaseModel):
    target_service: str = Field(description="Name of the service under test")
    threat_type: str = Field(description="Specific adversarial failure mode simulated")
    severity: Literal["P0 - CRITICAL", "P1 - HIGH", "P2 - MEDIUM"] = "P0 - CRITICAL"
    cascade_path: List[str] = Field(description="Ordered list showing failure propagation")
    blast_radius_nodes: Dict[str, NodeStatus] = Field(
        description="Dictionary mapping each component to its health status"
    )
    mitigation_summary: str = Field(description="High-level engineering mitigation strategy")
    code_patch: str = Field(description="Hardened code snippet or config patch")
