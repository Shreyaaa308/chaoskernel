import logging
from app.schemas.chaos_state import ChaosAnalysisResult
from app.core.presets import resolve_preset_scenario
from app.engine.prompts import SYSTEM_PROMPT, build_chaos_analysis_prompt
from app.engine.llm_client import chaos_llm_client

logger = logging.getLogger(__name__)

def analyze_system_architecture(payload_text: str) -> ChaosAnalysisResult:
    preset_result = resolve_preset_scenario(payload_text)
    if preset_result:
        return preset_result

    try:
        user_prompt = build_chaos_analysis_prompt(payload_text)
        json_output = chaos_llm_client.generate_json_response(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt
        )
        return ChaosAnalysisResult(**json_output)
    except Exception as e:
        logger.error(f"Error during LLM chaos analysis: {e}")
        return ChaosAnalysisResult(
            target_service="target-service-pipeline",
            threat_type="Cascading Dependency Failure & Thread Pool Exhaustion",
            severity="P0 - CRITICAL",
            cascade_path=[
                "Ingress Gateway",
                "Application Worker (DEADLOCK)",
                "State Store Connection Pool (STARVATION)",
                "Upstream Circuit (TRIPPED)"
            ],
            blast_radius_nodes={
                "Ingress Gateway": "DEGRADED",
                "Application Worker": "FAILED",
                "State Store": "FAILED",
                "Auth Service": "HEALTHY",
                "Notification Broker": "DEGRADED"
            },
            mitigation_summary=(
                f"Adversarial analysis triggered an unexpected exception ({str(e)[:60]}). "
                "Engaged emergency auto-immune fallback."
            ),
            code_patch=(
                "// Emergency Fallback Circuit Breaker\n"
                "const breaker = new CircuitBreaker(targetServiceCall, { timeout: 3000 });"
            )
        )
