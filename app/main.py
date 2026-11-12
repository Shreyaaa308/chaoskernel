import os
import uuid
import base64
import tempfile
from fastapi import FastAPI
from app.config import settings
from app.schemas.nonilion import NonilionIncomingMessage, NonilionOutgoingReply, NonilionAttachment
from app.schemas.chaos_state import ChaosAnalysisResult
from app.core.guardrails import validate_incident_context
from app.engine.analyzer import run_autonomous_analysis
from app.services.visualizer import generate_blast_radius_chart
from app.services.exporter import generate_markdown_report, generate_pdf_report

app = FastAPI(title="ChaosKernel Autonomous Resilience Agent", version="2.0.0")


def _to_teammate2_payload(result: ChaosAnalysisResult) -> dict:
    """Translates Person 1's ChaosAnalysisResult into Teammate 2's exact dict contract."""
    failed_count = sum(1 for n in result.nodes if n.status == "FAILED")
    degraded_count = sum(1 for n in result.nodes if n.status == "DEGRADED")

    if failed_count >= 2:
        severity = "CRITICAL"
    elif failed_count == 1:
        severity = "HIGH"
    elif degraded_count >= 1:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    # Enrich labels with Hop Distance for Teammate 2's chart & PDF table
    blast_dict = {}
    for n in result.nodes:
        hop_tag = f"Hop {n.hop}" if n.hop >= 0 else "Isolated"
        blast_dict[f"{n.name} ({hop_tag})"] = n.status

    location_note = (
        f" [Detected at {result.vulnerable_file}:{result.vulnerable_line}]"
        if result.vulnerable_file else ""
    )

    return {
        "target_service": result.target_name,
        "threat_type": f"{result.root_cause_summary}{location_note}",
        "severity": severity,
        "blast_radius_nodes": blast_dict,
        "mitigation_summary": result.mitigation_summary,
        "code_patch": result.git_diff_patch,
    }


@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "ChaosKernel",
        "mode": "Autonomous Engineering Agent v2.0",
        "environment": getattr(settings, "ENVIRONMENT", "production"),
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ChaosKernel"}


@app.post("/webhook", response_model=NonilionOutgoingReply)
def handle_webhook(payload: NonilionIncomingMessage):
    # 1. Rule #5 Guardrail Check (Session-aware for multi-turn follow-ups)
    is_valid, rejection_msg = validate_incident_context(payload.text, payload.room_id)
    if not is_valid:
        return NonilionOutgoingReply(reply=rejection_msg, attachments=[])

    # 2. Person 1 Autonomous Engine (Repo Fetcher + Static Vuln Scanner + NetworkX + LLM)
    result = run_autonomous_analysis(payload.text, payload.room_id)

    # 3. Adapt to Teammate 2's Visualizer & Exporter
    chaos_payload = _to_teammate2_payload(result)
    chart_b64 = generate_blast_radius_chart(chaos_payload)
    md_report = generate_markdown_report(chaos_payload)
    md_b64 = base64.b64encode(md_report.encode("utf-8")).decode("utf-8")

    # Render PDF safely to a temp file and encode as Base64
    run_id = uuid.uuid4().hex[:10]
    tmp_pdf_path = os.path.join(tempfile.gettempdir(), f"Chaos_Hardening_Spec_{run_id}.pdf")
    generate_pdf_report(chaos_payload, output_path=tmp_pdf_path)
    with open(tmp_pdf_path, "rb") as f:
        pdf_b64 = base64.b64encode(f.read()).decode("utf-8")
    if os.path.exists(tmp_pdf_path):
        os.remove(tmp_pdf_path)

    vuln_banner = (
        f"📍 **Vulnerable Code:** `{result.vulnerable_file}:{result.vulnerable_line}`\n"
        if result.vulnerable_file else ""
    )

    chat_reply = (
        f"🚨 **ChaosKernel Autonomous Audit: `{result.target_name}`** (`{chaos_payload['severity']}`)\n\n"
        f"{vuln_banner}"
        f"⚡ **Root Cause:** {result.root_cause_summary}\n\n"
        f"🛡️ **Auto-Immune Fix:** {result.mitigation_summary}\n\n"
        f"```diff\n{result.git_diff_patch}\n```\n"
        f"📎 *Attached: Multi-Hop Blast Radius Chart (PNG), Executive Audit Spec (PDF), and Markdown Manifest.*"
    )

    attachments = [
        NonilionAttachment(type="image", filename=f"blast_radius_{run_id}.png", data_base64=chart_b64),
        NonilionAttachment(type="file", filename=f"Chaos_Hardening_Spec_{run_id}.pdf", data_base64=pdf_b64),
        NonilionAttachment(type="file", filename=f"Chaos_Hardening_Spec_{run_id}.md", data_base64=md_b64),
    ]

    return NonilionOutgoingReply(reply=chat_reply, attachments=attachments)
