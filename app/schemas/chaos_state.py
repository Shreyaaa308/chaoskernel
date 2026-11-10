from pydantic import BaseModel, Field, model_validator
from typing import Dict, List, Literal, Any

NodeStatus = Literal["FAILED", "DEGRADED", "HEALTHY"]

class ChaosAnalysisResult(BaseModel):
    target_service: str = Field(description="Name of the service under test")
    threat_type: str = Field(description="Specific adversarial failure mode simulated")
    severity: Literal["P0 - CRITICAL", "P1 - HIGH", "P2 - MEDIUM"] = "P0 - CRITICAL"
    cascade_path: List[str] = Field(description="Ordered list showing failure propagation")
    blast_radius_nodes: Dict[str, NodeStatus] = Field(
        default_factory=dict,
        description="Dictionary mapping each component to its health status"
    )
    mitigation_summary: str = Field(description="High-level engineering mitigation strategy")
    code_patch: str = Field(description="Hardened code snippet or config patch")

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "blast_radius_node" in data and "blast_radius_nodes" not in data:
                data["blast_radius_nodes"] = data["blast_radius_node"]
            if "threat_mode" in data and "threat_type" not in data:
                data["threat_type"] = data["threat_mode"]
        return data
