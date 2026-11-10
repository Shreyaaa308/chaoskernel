from app.services.exporter import (
    generate_markdown_report,
    generate_pdf_report,
)

chaos_payload = {
    "target_service": "payment-settlement-worker",
    "threat_type": "Distributed Race Condition & Cache Stampede",
    "severity": "P0 - CRITICAL",
    "blast_radius_nodes": {
        "Gateway": "HEALTHY",
        "Redis": "FAILED",
        "Postgres": "DEGRADED",
    },
    "mitigation_summary": (
        "Atomic distributed lock applied with "
        "exponential backoff retry."
    ),
    "code_patch": (
        "async with redis_lock(f'lock:tx:{order_id}'):\n"
        "    await process_ledger_update()"
    ),
}


# Test Markdown exporter
print("Generating Markdown report...")

markdown_report = generate_markdown_report(chaos_payload)

with open(
    "Chaos_Hardening_Spec.md",
    "w",
    encoding="utf-8",
) as file:
    file.write(markdown_report)

print("Markdown report generated successfully!")


# Test PDF exporter
print("Generating PDF report...")

pdf_path = generate_pdf_report(chaos_payload)

print("PDF report generated successfully!")
print("PDF saved at:", pdf_path)

print("\nAll exporter tests completed!")