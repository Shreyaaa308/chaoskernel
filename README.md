# ChaosKernel v2.0

ChaosKernel is an autonomous microservice resilience and chaos-engineering agent built for chat-driven operations (designed to plug directly into Nonilion rooms). Drop any public GitHub repository URL or service architecture description into chat, and ChaosKernel maps its dependency graph, simulates multi-hop failure cascades, pinpoints Single Points of Failure (SPOFs), and generates ready-to-apply `git diff` hardening patches.

---

## What It Does

* **Autonomous Repo & Code Scanning:** Fetches any target GitHub repository via `httpx`, inspects service boundaries, and flags missing timeouts, unbounded connection pools, and unguarded synchronous downstream calls.
* **Multi-Hop Blast Radius Modeling (`NetworkX`):** Builds a directed dependency graph (`DiGraph`) and traverses reverse edges from a failing node to compute exact upstream cascade impacts (`FAILED`, `DEGRADED`, or `HEALTHY`) by hop distance.
* **Quantitative Resilience Score & SPOF Detection:** Uses `nx.betweenness_centrality()` to identify the bottleneck node most likely to amplify a cascade, calculating a deterministic **0–100 Resilience Score** and **Blast Radius %**.
* **Interactive "What-If" Simulations:** Maintains per-room session context (`room_id`) so you can test mitigations in follow-up messages (e.g., *"What if we add a circuit breaker on OrderService?"*) and watch the Resilience Score and blast radius recalculate live.
* **Auto-Immune Patching & Multi-Modal Reports:** Uses Gemini to generate concrete unified `git diff` patches alongside three downloadable artifacts attached directly to the webhook response:
  * **Blast-Radius Dependency Chart (`.png`)** rendered via Matplotlib
  * **Executive Hardening Spec (`.pdf`)** compiled via ReportLab
  * **Architecture & Patch Manifest (`.md`)**

---

## Tech Stack

* **API & Webhooks:** FastAPI, Uvicorn, Pydantic v2
* **Graph & Resilience Engine:** NetworkX
* **AI Reasoning & Patch Generation:** Google Gemini API
* **Visualization & Export:** Matplotlib, ReportLab, HTTPX
* **Deployment & CI:** Render (`render.yaml`), GitHub Actions (`.github/workflows/ci.yml`), Pytest

---

## Project Structure

```text
ChaosKernel/
├── app/
│   ├── core/
│   │   ├── guardrails.py       # Ambiguity & context validation (blocks vague prompts)
│   │   └── session_store.py    # Multi-turn room state for "What-If" simulations
│   ├── engine/
│   │   ├── analyzer.py         # Orchestrates repo scan, graph traversal, and LLM synthesis
│   │   ├── llm_client.py       # Gemini API integration
│   │   └── prompts.py          # Structured resilience & diff-generation prompts
│   ├── schemas/
│   │   ├── chaos_state.py      # TopologyEdge, NodeImpact, ChaosAnalysisResult models
│   │   └── nonilion.py         # Incoming/outgoing chat webhook contracts
│   ├── services/
│   │   ├── exporter.py         # Generates Markdown & PDF hardening specs
│   │   └── visualizer.py       # Renders multi-hop blast-radius PNG graphs
│   ├── tools/
│   │   ├── graph_engine.py     # NetworkX cascade BFS, Resilience Score, & SPOF centrality
│   │   ├── repo_fetcher.py     # Async/sync GitHub repository fetcher
│   │   └── vuln_scanner.py     # Static pattern scanner for unguarded network/DB calls
│   ├── config.py
│   └── main.py                 # FastAPI entrypoint (/health, /webhook)
├── docs/assets/                # Dashboard & architecture visuals
├── tests/                      # Unit & integration tests
├── render.yaml                 # Render web service blueprint
└── requirements.txt

## System Architecture & Execution Flow

```mermaid
flowchart LR
    User([Chat / Nonilion Webhook]) --> Guard{Rule #5 Guardrail}
    Guard -- Vague Prompt --> Reject[Clarification Prompt]
    Guard -- Valid Repo / Arch --> Fetch[GitHub Repo Fetcher & Static Scanner]
    Fetch --> Graph[NetworkX DiGraph & Blast-Radius BFS]
    Graph --> Metrics[Resilience Score 0-100 & SPOF Centrality]
    Metrics --> LLM[Gemini Reasoning & Auto-Immune Diff]
    LLM --> Session[(Room Session Store)]
    LLM --> Out[Multi-Modal Output]
    Out --> PNG[Blast-Radius Chart .png]
    Out --> PDF[Hardening Spec .pdf]
    Out --> MD[Patch Manifest .md]
```

---

## Sample Outputs Produced

### 1. Multi-Hop Blast Radius Chart (`.png`)
![Sample Blast Radius Chart](docs/assets/sample-blast-radius.png)

### 2. Executive Hardening Report (`.pdf`) & Unified Diff
> Once you save a screenshot of your generated PDF spec to `docs/assets/sample-hardening-report.png`, uncomment the line below:
> `![Executive Hardening Spec](docs/assets/sample-hardening-report.png)`
