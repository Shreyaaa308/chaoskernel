from pydantic import BaseModel, Field, model_validator
from typing import Dict, List, Any

class ChaosAnalysisResult(BaseModel):
    target_service: str = Field(default="Target Service", description="Name of the service under test")
    threat_type: str = Field(default="Cascading Failure", description="Specific adversarial failure mode simulated")
    severity: str = Field(default="P0 - CRITICAL", description="Incident severity level")
    cascade_path: List[str] = Field(default_factory=lambda: ["Ingress Gateway", "App Worker", "Database Pool"], description="Ordered list showing failure propagation")
    blast_radius_nodes: Dict[str, str] = Field(
        default_factory=dict,
        description="Dictionary mapping each component to its health status"
    )
    mitigation_summary: str = Field(default="Implement circuit breakers and pool isolation.", description="Mitigation summary")
    code_patch: str = Field(default="// Apply circuit breaker pattern\nbreaker.trip();", description="Hardened code snippet or config patch")

    @model_validator(mode="before")
    @classmethod
    def sanitize_llm_payload(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        # Normalize blast radius key variations
        for key in ["blast_radius_nodes", "blast_radius_node", "blast_radius", "nodes"]:
            if key in data:
                nodes_val = data.pop(key)
                if isinstance(nodes_val, dict):
                    data["blast_radius_nodes"] = {str(k): str(v).upper() for k, v in nodes_val.items()}
                elif isinstance(nodes_val, list):
                    data["blast_radius_nodes"] = {str(item): "FAILED" for item in nodes_val}
                break

        # Normalize threat_type / threat_mode
        if "threat_mode" in data and "threat_type" not in data:
            data["threat_type"] = data["threat_mode"]

        # Ensure cascade_path is a list of strings
        if "cascade_path" in data and not isinstance(data["cascade_path"], list):
            data["cascade_path"] = [str(data["cascade_path"])]

        return data
