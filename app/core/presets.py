from typing import Optional
from app.schemas.chaos_state import ChaosAnalysisResult

PRESET_SCENARIOS = {
    "black-friday": ChaosAnalysisResult(
        target_service="checkout-payment-pipeline",
        threat_type="Distributed Race Condition & Cache Stampede",
        severity="P0 - CRITICAL",
        cascade_path=[
            "Client Checkout API",
            "Payment Gateway Service",
            "Redis Session Cache (DEADLOCK)",
            "PostgreSQL Master DB (CONNECTION_EXHAUSTED)",
            "Order Notification Queue (BLOCKED)"
        ],
        blast_radius_nodes={
            "Client API": "DEGRADED",
            "Payment Gateway": "FAILED",
            "Redis Cache": "FAILED",
            "PostgreSQL": "DEGRADED",
            "Auth Service": "HEALTHY",
            "Notification Worker": "FAILED"
        },
        mitigation_summary=(
            "Simulated 120k req/min traffic surge. Redis pool hit thread starvation, "
            "leaking fallback queries directly to PostgreSQL. Database connection pool "
            "exhausted within 4.2 seconds."
        ),
        code_patch=(
            "// Auto-Immune Patch: Redis Redlock + Circuit Breaker\n"
            "async function processCheckout(orderId, userId) {\n"
            "    const breaker = new CircuitBreaker(paymentGatewayClient, {\n"
            "        timeout: 2500,\n"
            "        errorThresholdPercentage: 50,\n"
            "        resetTimeout: 10000\n"
            "    });\n"
            "    return await breaker.fire(orderId, userId);\n"
            "}"
        )
    ),
    "cache-stampede": ChaosAnalysisResult(
        target_service="catalog-read-cluster",
        threat_type="Hotkey Eviction Cascade",
        severity="P1 - HIGH",
        cascade_path=[
            "Catalog Gateway",
            "Redis L2 Cache (HOTKEY_EVICTION)",
            "Primary Read Replica (CPU_100%)",
            "Elasticsearch Search Index (TIMEOUT)"
        ],
        blast_radius_nodes={
            "Catalog Gateway": "DEGRADED",
            "Redis L2": "FAILED",
            "Read Replica": "FAILED",
            "Search Index": "DEGRADED",
            "User Service": "HEALTHY"
        },
        mitigation_summary=(
            "Key 'hot_deal_electronics' expired during peak flash sale. 45,000 parallel "
            "requests bypassed cache layer, driving Read Replica CPU utilization to 100%."
        ),
        code_patch=(
            "# Auto-Immune Patch: Probabilistic Early Expiration (XFetch)\n"
            "def get_with_xfetch(key, ttl, beta=1.0):\n"
            "    val, delta, expiry = redis.get(key)\n"
            "    if time.time() - (delta * beta * math.log(random.random())) > expiry:\n"
            "        val = recompute_and_cache(key, ttl)\n"
            "    return val"
        )
    )
}

def resolve_preset_scenario(command_text: str) -> Optional[ChaosAnalysisResult]:
    """
    Parses commands like '/chaos scenario=black-friday' and returns mock chaos result.
    """
    cleaned = command_text.strip().lower()
    for key, result in PRESET_SCENARIOS.items():
        if key in cleaned:
            return result
    return None
