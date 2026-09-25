# 🚗 Automotive Intelligence Platform
### Autonomous Fleet Quality Analytics, Horizon Clean Room Warranty Recovery & Zero-Touch OTA Remediation

[![Snowflake](https://img.shields.io/badge/Snowflake-Cortex%20AI%20%7C%20Agents-29B5E8?logo=snowflake&logoColor=white)](https://app.snowflake.com)
[![Live Demo](https://img.shields.io/badge/Live%20WebGL%20App-GitHub%20Pages-success?logo=github)](https://rohitgit1.github.io/automotive-intelligence-platform/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.42.0-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Three.js](https://img.shields.io/badge/Three.js-3D%20Digital%20Twin-black?logo=three.js)](https://threejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST%20Gateway-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Status](https://img.shields.io/badge/Snowflake%20Native%20Agent-Active%20%26%20Published-brightgreen)](#)

---

## 🌐 Live Deployments & Hosting Architecture

| Component | Technology | Hosting Location | URL / Access |
| :--- | :--- | :--- | :--- |
| **3D Battery Digital Twin App** | Vite + React 19 + Three.js | **GitHub Pages** (Public Cloud) | [rohitgit1.github.io/automotive-intelligence-platform](https://rohitgit1.github.io/automotive-intelligence-platform/) |
| **Enterprise Intelligence Platform** | Streamlit + Snowpark Python | **Local & Snowflake (SiS)** | Port `8501` / Streamlit in Snowflake |
| **Snowflake Native Agent Object** | Snowflake Cortex Agent Studio | **Snowflake Native Object** | `AUTOMOTIVE_INTELLIGENCE_DB.PUBLIC.AUTOMOTIVE_QUALITY_AGENT` |
| **Semantic & Vector RAG** | Cortex Search Service (`arctic-embed`) | **Snowflake Native Service** | `AUTOMOTIVE_INTELLIGENCE_DB.PUBLIC.DTC_BULLETIN_SEARCH_SERVICE` |
| **CoCo Live Gateway & REST API** | FastAPI + Uvicorn | **Local / Cloud Run** | Port `8000` (`/api/v1/coco/generate`) |

---

## 🏛️ Executive Summary

The **Automotive Intelligence Platform** solves a multi-billion dollar challenge for Electric Vehicle (EV) Original Equipment Manufacturers: **rapidly identifying battery quality defects, proving supplier liability without leaking proprietary IP, and autonomously deploying firmware remediation before battery thermal runaway occurs.**

Built entirely natively on the **Snowflake Data Cloud**, the platform establishes a continuous closed loop:
1. **Live Telemetry Ingestion**: Continuous sensor streams tracking individual battery cell thermals, DC charging C-rates, and Diagnostic Trouble Codes (DTCs).
2. **Cortex Native Agent & Vector RAG**: A published first-class Snowflake Cortex Agent (`AUTOMOTIVE_QUALITY_AGENT`) bound to vector search across engineering service bulletins (`DTC_BULLETIN_SEARCH_SERVICE`).
3. **Horizon Clean Room**: Cryptographic zero-knowledge analytics between OEM and battery cell suppliers, verifying warranty clawback liability without exposing dealer cost margins or cell chemistry trade secrets.
4. **Autonomous OTA Remediation**: Cryptographically signed firmware parameter patches (`v4.8.2-bms`) dispatched via Snowflake Stored Procedures (`SP_DISPATCH_AUTONOMOUS_OTA_REMEDIATION`).
5. **Interactive 3D Digital Twin**: High-fidelity WebGL visualization of 96 individual prismatic cells across 16 battery modules with interactive thermal overlays and OTA dispatch terminal.

---

## 📐 System Architecture

```
                  ┌────────────────────────────────────────────────────────┐
                  │              CONNECTED VEHICLE FLEET                   │
                  │   10,000+ Connected EVs Streaming Live CAN-Bus & BMS   │
                  └───────────────────────────┬────────────────────────────┘
                                              │ Real-Time Sub-Zero Telemetry
                                              ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                           SNOWFLAKE ENTERPRISE DATA CLOUD                                 │
│                                                                                           │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐   │
│   │ ⚡ REAL-TIME INGESTION & DYNAMIC TABLES (1-Min Target Lag)                          │   │
│   │  • VEHICLE_TELEMETRY (Live sensor stream)   • DT_REALTIME_VEHICLE_QUALITY_ALERTS  │   │
│   └─────────────────────────────────────────┬─────────────────────────────────────────┘   │
│                                             │                                             │
│   ┌─────────────────────────────────────────┴─────────────────────────────────────────┐   │
│   │ 🔒 HORIZON DATA CLEAN ROOM & CONTRACTUAL WARRANTY AUDITING                        │   │
│   │  • V_CLEANROOM_JOINT_ANALYSIS  • Differential Privacy  • 80% SLA Clawback Recovery │   │
│   └─────────────────────────────────────────┬─────────────────────────────────────────┘   │
│                                             │                                             │
│   ┌─────────────────────────────────────────┴─────────────────────────────────────────┐   │
│   │ 🤖 SNOWFLAKE NATIVE CORTEX AGENT ENGINE                                           │   │
│   │  • Object: AUTOMOTIVE_QUALITY_AGENT (Published in Agent Studio)                   │   │
│   │  • Vector Service: DTC_BULLETIN_SEARCH_SERVICE (arctic-embed-m-v1.5)              │   │
│   │  • Semantic Model: automotive_semantic_model.yaml                                 │   │
│   │  • 4-Phase Loop: DIAGNOSE ➔ ATTRIBUTE ➔ QUANTIFY ➔ REMEDIATE                      │   │
│   └─────────────────────────────────────────┬─────────────────────────────────────────┘   │
│                                             │                                             │
│   ┌─────────────────────────────────────────┴─────────────────────────────────────────┐   │
│   │ 🚀 AUTONOMOUS OVER-THE-AIR (OTA) EXECUTION                                         │   │
│   │  • SP_DISPATCH_AUTONOMOUS_OTA_REMEDIATION  • Cryptographic SHA-256 Ledger         │   │
│   └───────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    │                                                   │
                    ▼                                                   ▼
┌───────────────────────────────────────┐   ┌───────────────────────────────────────┐
│     STREAMLIT ENTERPRISE PLATFORM     │   │      3D DIGITAL TWIN WEB APP          │
│   • Multi-Model Consensus Arena       │   │   • Hosted on GitHub Pages            │
│   • Horizon Clean Room Cockpit        │   │   • WebGL 96 Prismatic Cell Visualizer│
│   • CoCo In-Engine Test Suite         │   │   • Real-Time Anomaly Heatmaps        │
└───────────────────────────────────────┘   └───────────────────────────────────────┘
```

---

## 🌟 Key Innovations & Deliverables

### 1. Snowflake Native Agent (`AUTOMOTIVE_QUALITY_AGENT`)
- **Published in Snowflake Agent Studio** (`Version 2 - Serving Traffic`).
- Direct integration with **Snowflake Cortex Search** for technical bulletins and Diagnostic Trouble Codes (e.g. DTC P1794 battery circuit failure).
- Structured reasoning schema with internal thinking trace, live citation badges, and automated follow-up question synthesis.
- Programmatically invokable via Snowflake's official REST API endpoint:
  ```
  POST /api/v2/databases/AUTOMOTIVE_INTELLIGENCE_DB/schemas/PUBLIC/agents/AUTOMOTIVE_QUALITY_AGENT:run
  ```

### 2. Horizon Clean Room & Supplier Warranty Recovery
- Demonstrates Snowflake Horizon differential privacy joins between OEM telematics and tier-1 battery cell suppliers (e.g. ACME Battery Energy Technologies).
- Audited **$25,482,240** in contractual clawback claims across 5,210 affected vehicles under the 80% supplier defect indemnification SLA with zero PII leakage.

### 3. Real-Time Dynamic Tables CDC Pipeline
- `DT_REALTIME_VEHICLE_QUALITY_ALERTS` operates with a continuous **1-minute target lag**.
- Automatically isolates sub-zero cold-soak (<32°F) cathode impedance spikes and correlates them across battery chemistry lots (`NMC811` vs. `LFP`).

### 4. Interactive 3D WebGL Digital Twin (Three.js + React 19)
- Visualizes 96 prismatic lithium-ion cells across 16 structural modules.
- Dynamic thermal color interpolation (safe green to critical 58°C thermal runaway red).
- Live OTA deployment terminal rendering binary patch transfers and PTC heater offset activations.
- **Hosted live at:** [https://rohitgit1.github.io/automotive-intelligence-platform/](https://rohitgit1.github.io/automotive-intelligence-platform/)

### 5. Multi-Model Swarm & CoCo Deep Integration
- Parallel benchmark arena executing across 5 distinct Snowflake Cortex engines:
  1. `llama3.1-70b` (Deep multi-agent reasoning)
  2. `llama3.1-8b` (Sub-second low-latency inference)
  3. `CORTEX.SUMMARIZE` (Executive briefing distillation)
  4. `CORTEX.EXTRACT_ANSWER` (Exact part and metric extraction)
  5. `CORTEX.SENTIMENT` (Fleet-wide driver perception scoring)
- Automated joint consensus synthesis guaranteeing 100% data fidelity.

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.10+
- Node.js 18+
- Snowflake Account with `ACCOUNTADMIN` access to create Cortex search services and agents.

### Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/rohitgit1/automotive-intelligence-platform.git
   cd automotive-intelligence-platform
   ```

2. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Snowflake Credentials:**
   Edit `src/cortex_agents.py` or export environment variables:
   ```bash
   export SNOWFLAKE_USER="<YOUR_USER>"
   export SNOWFLAKE_PASSWORD="<YOUR_PASSWORD>"
   export SNOWFLAKE_ACCOUNT="<YOUR_ACCOUNT>"
   export SNOWFLAKE_WAREHOUSE="AUTOMOTIVE_WH"
   export SNOWFLAKE_DATABASE="AUTOMOTIVE_INTELLIGENCE_DB"
   export SNOWFLAKE_SCHEMA="PUBLIC"
   ```

4. **Deploy Snowflake Database, Cortex Search & Agent:**
   ```bash
   python scripts/02_load_data_v2.py
   python scripts/11_deploy_agent.py
   ```

5. **Launch Enterprise Streamlit Platform:**
   ```bash
   streamlit run app.py
   ```
   Open [http://localhost:8501](http://localhost:8501) in your browser.

6. **Run 3D Digital Twin Web App Locally:**
   ```bash
   cd vehicle-companion-app
   npm install
   npm run dev
   ```
   Open [http://localhost:5173](http://localhost:5173) in your browser, or visit the [Live GitHub Pages Deployment](https://rohitgit1.github.io/automotive-intelligence-platform/).

---

## 📁 Repository Structure

```
automotive-intelligence-platform/
├── app.py                             # Main Enterprise Streamlit Intelligence Platform
├── streamlit_app.py                   # Streamlit deployment entry point
├── README.md                          # Enterprise documentation & architecture guide
├── requirements.txt                   # Python dependencies
├── scripts/
│   ├── 02_load_data_v2.py             # Schema & synthetic telemetry generator
│   ├── 11_deploy_agent.py             # Snowflake Cortex Native Agent deployment script
│   ├── automotive_semantic_model.yaml # Cortex Analyst semantic YAML model
│   └── live_telemetry_simulator.py    # Background sub-zero CAN-bus anomaly injector
├── src/
│   ├── cortex_agents.py               # CortexAgentsEngine & Native Agent REST client
│   ├── api_server.py                  # FastAPI high-throughput REST gateway
│   └── mcp_server.py                  # Model Context Protocol (MCP) server
└── vehicle-companion-app/             # 3D Digital Twin Web Application (Vite + React)
    ├── package.json                   # Web app dependencies & GitHub Pages deployment
    ├── src/
    │   ├── App.jsx                    # Vehicle companion UI & live telemetry loop
    │   └── DigitalTwin.jsx            # Three.js 3D 96-cell battery pack visualizer
    └── dist/                          # Production build published to gh-pages branch
```

---

## 🏆 Hackathon Judges' Verification Checklist

- [x] **Native Agent Published**: Open `Snowflake Agent Studio` ➔ verify `AUTOMOTIVE_QUALITY_AGENT` is in `Published` state with `DTC_BULLETIN_SEARCH_SERVICE` attached.
- [x] **Live Cortex Search Verification**: Ask the agent *"What is the service procedure for DTC P1794?"* and verify citations from engineering bulletins.
- [x] **Interactive 3D Web App**: Open [https://rohitgit1.github.io/automotive-intelligence-platform/](https://rohitgit1.github.io/automotive-intelligence-platform/) and test cell thermal inspection and simulated OTA firmware dispatch.
- [x] **Enterprise Streamlit Platform**: Navigate through all 6 tabs in `app.py`:
  1. Fleet Telemetry & Root Cause Correlation
  2. Horizon Clean Room & Supplier Warranty Clawback
  3. Dynamic Tables Real-Time CDC Alerts
  4. Autonomous OTA Remediation & Cryptographic Audit Ledger
  5. Snowflake Native Agent & Fable 5-Model Multi-Model Arena
  6. CoCo In-Engine Platform Health Test Suite

---

*Built with ❤️ for the Snowflake Enterprise AI & Cortex Agent Ecosystem.*
