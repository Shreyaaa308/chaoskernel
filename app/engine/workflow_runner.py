import sys
from app.engine.analyzer import analyze_system_architecture

def run_workflow_pipeline(input_payload: str):
    print("🚀 [Step 1/3] Executing Adversarial Chaos Analysis via LLM...")
    result = analyze_system_architecture(input_payload)
    
    print(f"✅ [Step 2/3] Failure scenario modeled: {result.threat_type} (Severity: {result.severity})")
    print(f"📊 [Step 3/3] Blast radius computed for {len(result.blast_radius_nodes)} nodes.")
    
    return result

if __name__ == '__main__':
    payload = sys.argv[1] if len(sys.argv) > 1 else '/chaos scenario=black-friday'
    run_workflow_pipeline(payload)
