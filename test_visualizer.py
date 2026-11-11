import base64
from app.services.visualizer import generate_blast_radius_chart

# Sample data simulating ChaosKernel's analysis
chaos_payload = {
    "target_service": "payment-settlement-worker",
    "threat_type": "Cache Stampede",
    "severity": "P0 - CRITICAL",

    "blast_radius_nodes": {
        "Gateway": "HEALTHY",
        "Redis": "FAILED",
        "Postgres": "DEGRADED"
    },

    "mitigation_summary": "Apply distributed locks with exponential backoff.",
    "code_patch": "await process_ledger_update()"
}
# Generate the blast-radius chart
image_base64 = generate_blast_radius_chart(chaos_payload)

# Check whether an image was returned
print("Chart generated successfully!")

# Display the Base64 string length
print("Base64 string length:", len(image_base64))

# Check that the returned data is not empty
print("Image data exists:", bool(image_base64))

# Convert Base64 data back into image bytes
image_bytes = base64.b64decode(image_base64)

# Save the image as a PNG file
with open("chaoskernel_blast_radius.png", "wb") as image_file:
    image_file.write(image_bytes)

print("PNG image saved successfully!")