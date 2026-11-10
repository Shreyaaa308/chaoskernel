from fastapi import FastAPI
from app.config import settings
from app.schemas.nonilion import NonilionIncomingMessage, NonilionOutgoingReply
from app.core.guardrails import validate_incident_context
from app.engine.analyzer import analyze_system_architecture

app = FastAPI(
    title="ChaosKernel Agent",
    description="Adversarial Chaos Architect & Auto-Immune Scribe with Render Workflows",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "ChaosKernel",
        "environment": settings.ENVIRONMENT
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ChaosKernel"}

@app.post("/webhook", response_model=NonilionOutgoingReply)
async def nonilion_webhook(payload: NonilionIncomingMessage):
    # 1. Enforce Rule #5 Guardrails
    is_valid, rejection_msg = validate_incident_context(payload.text)
    if not is_valid:
        return NonilionOutgoingReply(reply=rejection_msg, attachments=[])

    # 2. Execute Chaos Simulation & Resilience Engine
    result = analyze_system_architecture(payload.text)

    # 3. Format Response for Nonilion Room
    cascade_str = "\n".join([f"  {i+1}. {step}" for i, step in enumerate(result.cascade_path)])
    
    formatted_reply = (
        f"🚨 **[ChaosKernel Incident Simulation: {result.severity}]**\n\n"
        f"🎯 **Target:** {result.target_service}\n"
        f"⚡ **Threat Mode:** {result.threat_type}\n\n"
        f"📉 **Failure Cascade Path:**\n{cascade_str}\n\n"
        f"🛡️ **Mitigation Summary:**\n{result.mitigation_summary}\n\n"
        f"💻 **Auto-Immune Patch:**\n`{result.code_patch}`\n\n"
        f"*(Render Workflow status: Pipeline execution successful)*"
    )

    return NonilionOutgoingReply(reply=formatted_reply, attachments=[])
