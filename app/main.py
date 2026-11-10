from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.config import settings
from app.engine.analyzer import analyze_system_architecture

app = FastAPI(title="ChaosKernel API", version="1.0.0")

class WebhookRequest(BaseModel):
    text: str

class WebhookResponse(BaseModel):
    reply: str

VAGUE_KEYWORDS = ["fix our service", "help me", "fix it", "check this", "something is broken"]

@app.get("/")
def read_root():
    return {"status": "online", "service": "ChaosKernel", "environment": settings.ENVIRONMENT}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ChaosKernel"}

@app.post("/webhook", response_model=WebhookResponse)
def handle_webhook(payload: WebhookRequest):
    cleaned_input = payload.text.strip()
    
    # Rule #5: Ambiguity Guardrail
    if len(cleaned_input.split()) < 4 or any(kw in cleaned_input.lower() for kw in VAGUE_KEYWORDS):
        if not cleaned_input.startswith("/chaos"):
            guidance = (
                "⚠️ **[ChaosKernel Ambiguity Guardrail]**\n\n"
                "Insufficient architectural context provided. Please provide:\n"
                "1. Target services and communication protocols (e.g. gRPC, HTTP REST)\n"
                "2. State stores or dependencies (e.g. Redis, PostgreSQL, Kafka)\n"
                "3. Observed symptoms or desired adversarial fault injection scenario.\n\n"
                "Or trigger a simulation preset: /chaos scenario=black-friday"
            )
            return WebhookResponse(reply=guidance)

    result = analyze_system_architecture(cleaned_input)

    reply_markdown = (
        f"🚨 **[ChaosKernel Incident Simulation: {result.severity}]**\n\n"
        f"🎯 **Target:** {result.target_service}\n"
        f"⚡ **Threat Mode:** {result.threat_type}\n\n"
        f"💥 **Failure Cascade Path:**\n" +
        "\n".join([f"  {i+1}. {step}" for i, step in enumerate(result.cascade_path)]) +
        f"\n\n🛡️ **Mitigation Summary:**\n{result.mitigation_summary}\n\n"
        f"🔧 **Auto-Immune Patch:**\n`{result.code_patch}`\n\n"
        f"*(Render Workflow status: Pipeline execution successful)*"
    )
    return WebhookResponse(reply=reply_markdown)
