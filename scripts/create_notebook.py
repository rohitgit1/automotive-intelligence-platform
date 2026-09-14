import json
import os

os.makedirs("notebooks", exist_ok=True)

cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# ⚡ Automotive Intelligence Platform\n",
            "## Real-Time Vehicle Quality Analytics, Snowflake ML & Closed-Loop OTA Remediation\n",
            "**Use Case:** Automotive Manufacturing & Fleet Quality  \n",
            "**Platform:** Snowflake Data Cloud (Cortex AI, Snowflake ML, Dynamic Tables, Streamlit in Snowflake)  \n",
            "**Key Objective:** Move from passive dashboards to closed-loop autonomous remediation and supplier financial clawbacks."
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 1. Unified Telemetry, Ambient Weather & Battery Chemistry Ingestion\n",
            "We correlate over 300,000 CAN-bus sensor records across 10,000 production vehicles with local ambient weather and supplier cathode specifications."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "-- Query the root cause analytical view\n",
            "SELECT \n",
            "    supplier_name,\n",
            "    battery_type_name,\n",
            "    cathode,\n",
            "    temperature_category,\n",
            "    COUNT(*) AS total_telemetry_events,\n",
            "    COUNT(CASE WHEN dtc_error_code != 0 THEN 1 END) AS total_failures,\n",
            "    ROUND(COUNT(CASE WHEN dtc_error_code != 0 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS failure_rate_pct\n",
            "FROM V_ROOT_CAUSE_CORRELATION\n",
            "GROUP BY supplier_name, battery_type_name, cathode, temperature_category\n",
            "ORDER BY total_failures DESC\n",
            "LIMIT 10;"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 2. Snowflake ML Anomaly Detection (`SNOWFLAKE.ML.ANOMALY_DETECTION`)\n",
            "Unsupervised ML model trained inside Snowflake engine to detect anomalous spikes in fleet failure telemetry."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "-- Query anomalies detected by Snowflake ML\n",
            "SELECT \n",
            "    TS AS observation_timestamp,\n",
            "    Y AS actual_fault_count,\n",
            "    FORECAST AS baseline_expected,\n",
            "    LOWER_BOUND,\n",
            "    UPPER_BOUND,\n",
            "    IS_ANOMALY,\n",
            "    PERCENTILE\n",
            "FROM FLEET_TELEMETRY_ANOMALIES\n",
            "WHERE IS_ANOMALY = TRUE\n",
            "ORDER BY TS DESC;"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 3. Snowflake ML 30-Day Ahead Failure Forecast (`SNOWFLAKE.ML.FORECAST`)\n",
            "Time-series forecasting model generating 30-day ahead failure trajectory with 95% confidence intervals."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "-- Query 30-day failure forecast results\n",
            "SELECT \n",
            "    TS AS forecast_date,\n",
            "    ROUND(FORECAST, 1) AS predicted_failures,\n",
            "    ROUND(LOWER_BOUND, 1) AS lower_95_ci,\n",
            "    ROUND(UPPER_BOUND, 1) AS upper_95_ci\n",
            "FROM FLEET_30DAY_FORECAST_RESULTS\n",
            "ORDER BY TS ASC;"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 4. Snowflake Cortex LLM Autonomous Root Cause Investigation\n",
            "Leverages `SNOWFLAKE.CORTEX.COMPLETE` with `mistral-large2` to synthesize multi-variable telemetry and component specifications into root-cause engineering rationales."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "SELECT SNOWFLAKE.CORTEX.COMPLETE(\n",
            "    'mistral-large2',\n",
            "    'Analyze vehicle battery DTC error spikes: ACME Battery Corp with Lithium Cobalt Oxide cathodes shows 18.4% defect rate under sub-zero temperatures (<32F), whereas BETA and GAMMA show <1.5%. Provide technical diagnosis and root cause.'\n",
            ") AS cortex_rca_diagnosis;"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 5. Closed-Loop Autonomous Over-The-Air (OTA) Remediation Dispatch\n",
            "Executes stored procedure `SP_DISPATCH_AUTONOMOUS_OTA_REMEDIATION` to write verified cryptographic firmware calibrations into `FLEET_OTA_CAMPAIGNS`."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "CALL SP_DISPATCH_AUTONOMOUS_OTA_REMEDIATION(\n",
            "    'FW-2026.4.2-PTC',\n",
            "    4820,\n",
            "    'ACME Lithium Cobalt Oxide under <32F',\n",
            "    8940000.0\n",
            ");\n",
            "\n",
            "-- View audit log\n",
            "SELECT * FROM FLEET_OTA_CAMPAIGNS ORDER BY DEPLOYED_AT DESC LIMIT 5;"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 6. Supplier Warranty Liability & Statutory SLA Dispute Ledger\n",
            "Converts engineering telemetry root causes into formal indemnification clawbacks on supplier balance sheets."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "SELECT * FROM V_SUPPLIER_WARRANTY_LIABILITY\n",
            "ORDER BY ALLOCATED_SUPPLIER_CLAWBACK_USD DESC;"
        ]
    }
]

nb = {
    "cells": cells,
    "metadata": {
        "language_info": {"name": "sql"},
        "orig_nbformat": 4
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

with open("notebooks/automotive_notebook.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=2)

print("Created notebooks/automotive_notebook.ipynb successfully!")
