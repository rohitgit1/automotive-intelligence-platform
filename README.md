# Automotive Intelligence Platform

This project is a closed-loop automotive engineering platform built on the Snowflake Data Cloud. It ingests vehicle telemetry, correlates it with manufacturing data, and uses LLM-backed agents to diagnose hardware faults, calculate supplier liability, and autonomously dispatch Over-The-Air (OTA) firmware patches.

## Core Features

1. **Battery Digital Twin**: A WebGL-based visualization of 96 battery cells across 16 modules, tied to real-time thermal and voltage telemetry. 
2. **Autonomous OTA Remediation**: Cortex-powered agents generate dynamic BMS firmware patches (e.g., PTC heater offsets, C-rate caps) based on anomaly data. Patches are cryptographically signed (SHA-256) and written back to Snowflake's `FLEET_OTA_CAMPAIGNS` ledger.
3. **Automated Supplier Clawbacks**: Cross-references failure rates with supplier SLAs to automatically calculate warranty liability and generate legal claim payloads in Snowflake (`SUPPLIER_WARRANTY_CLAIMS`).
4. **Natural Language SQL Interface**: A text-to-SQL interface powered by Cortex Analyst and a strict semantic YAML model (`automotive_semantic_model.yaml`), ensuring deterministic read-only queries against production views.
5. **Multi-Agent Orchestrator**: A custom Python agent engine that routes user intents to vector search (`CORTEX.SEARCH_PREVIEW`), semantic models, or stored procedures before synthesizing responses with `llama3.3-70b`.

## Architecture Overview

The system operates across three tiers:
*   **Data Layer (Snowflake)**: Houses raw telemetry (`VEHICLES`, `WEATHER_DATA`), analytical views (`V_ROOT_CAUSE_CORRELATION`), and write-back audit ledgers.
*   **AI/Execution Layer (Python/Snowpark)**: Orchestrates Cortex LLM calls, ML forecasting models (`SNOWFLAKE.ML.FORECAST`), and stored procedure dispatches.
*   **Presentation Layer (React/Streamlit)**: A split front-end featuring a Streamlit dashboard for data pipeline management and a React/Three.js Web App for 3D vehicle state visualization.

## Setup & Deployment

### 1. Database Initialization
Ensure you have a Snowflake account. Run the database seed scripts to create the schema, load the synthetic telemetry, and configure the Cortex search services.

```bash
python scripts/02_load_data_v2.py
# Execute the SQL files in scripts/ (03, 05, 06) to build views and stored procedures.
```

### 2. Streamlit Dashboard
The dashboard handles the data pipeline, scenario planning, and Cortex agent interactions.
```bash
streamlit run app.py
```

### 3. WebGL Vehicle Companion App
The React application serves the 3D Digital Twin and OTA terminal simulation.
```bash
cd vehicle-companion-app
npm install
npm run dev
```

## Performance & Testing

The multi-agent orchestrator has been benchmarked against a matrix of in-domain, multi-step, and adversarial prompts. It utilizes a deterministic intent router combined with semantic models to guarantee zero SQL-injection vulnerability and prevents LLM hallucination on financial or telemetry metrics. See `scripts/cortex_agent_benchmark.py` for the testing harness.

---
*Built for the Snowflake x Capgemini Hackathon.*
