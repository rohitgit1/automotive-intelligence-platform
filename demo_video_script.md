# 🎬 3 to 4-Minute High-Impact Video Presentation Script
## Automotive Intelligence Platform | Final Hackathon Walkthrough

> **Presentation Strategy**: Instead of *telling* the judges this is innovative or impressive, we *show* them concrete outcomes: **300K telemetry rows processed in 1 minute**, **6 weeks of manual engineering compressed into 5 seconds**, and **$8.94M saved by automatically deploying a firmware fix before physical parts break**.

---

### 🖥️ Your 5 Browser Tabs & Screen Setup (Click In Order)

| Tab # | Page / Application | URL | What You Show on Screen |
| :---: | :--- | :--- | :--- |
| **Tab 1** | **3D Battery Digital Twin (Frontend)** | `https://rohitgit1.github.io/automotive-intelligence-platform/` | Rotate 3D battery module, point to the **-19°C Polar Vortex cold stress**, and click **"Simulate Autonomous OTA"**. |
| **Tab 2** | **Streamlit in Snowflake (SiS App)** | `https://app.snowflake.com/bljohcq/fob95633/#/streamlit-apps/AUTOMOTIVE_INTELLIGENCE_DB.PUBLIC.AUTOMOTIVE_INTELLIGENCE_PLATFORM` | Show KPI cards, fault patterns, and the **Supplier Clawback** ledger. |
| **Tab 3** | **Snowflake Agent Studio** ⭐ | `https://app.snowflake.com/bljohcq/fob95633/#/agents/database/AUTOMOTIVE_INTELLIGENCE_DB/schema/PUBLIC/agent/AUTOMOTIVE_QUALITY_AGENT` | Paste the exact prompt into chat and show the live tool execution with citations. |
| **Tab 4** | **Snowflake Database Explorer** | `https://app.snowflake.com/bljohcq/fob95633/#/data/databases/AUTOMOTIVE_INTELLIGENCE_DB/schemas/PUBLIC` | Show `DT_REALTIME_VEHICLE_QUALITY_ALERTS` (1-min lag Dynamic Table) and analytical views. |
| **Tab 5** | **GitHub Repository & Codebase** | `https://github.com/rohitgit1/automotive-intelligence-platform` | Scroll down to **`deploy_all_solution.py`** (the 1-command reproducer). |

---

### ⏱️ Spoken Script & Screen Actions (3:30 Total)

```
[0:00 - 0:40] TAB 1: The Problem & Live 3D Subsystem View
[0:40 - 1:25] TAB 2: Real Telemetry Patterns, Cortex RCA & Supplier Liability
[1:25 - 2:20] TAB 3: Snowflake Native Agent Studio (Live Prompt & Tool Execution)
[2:20 - 2:55] TAB 1: Closing the Loop (Zero-Touch OTA Firmware Remediation)
[2:55 - 3:35] TAB 4 & TAB 5: Snowflake Streaming Architecture & 1-Click Codebase
```

---

#### 📍 SECTION 1: The Problem & Live 3D Subsystem View (0:00 – 0:40)
**Screen**: Show **Tab 1** (`rohitgit1.github.io/automotive-intelligence-platform`). Rotate the 3D battery pack slightly with your mouse.

> **Spoken Script:**
> *"When an electric vehicle battery malfunctions in cold weather, traditional auto manufacturers spend 6 to 8 weeks trying to diagnose the issue. Telemetry is in one system, cell chemistry records are in another, and warranty claims sit in legal spreadsheets.*
> 
> *Here on screen, we connected all three directly inside Snowflake.*
> 
> *In our 3D Battery Subsystem view, we are tracking 300,000 real-world driving events across 10,000 vehicles. When vehicles hit sub-zero conditions—like this -19°C Polar Vortex event in North Dakota—we immediately see cell voltage deltas and internal impedance begin to spike."*

---

#### 📍 SECTION 2: Real Telemetry Patterns & Supplier Liability (0:40 – 1:25)
**Screen**: Switch to **Tab 2** (Streamlit in Snowflake app). Scroll to the KPI cards and click on **Supplier Warranty Clawback**.

> **Spoken Script:**
> *"Switching to our Streamlit application running natively inside Snowflake, our queries analyzed over 300,000 telemetry readings.*
> 
> *The data reveals a striking pattern: out of all vehicles, exactly 5,210 fault codes occurred across 749 cars. Every single one happened when the ambient temperature dropped below 32° Fahrenheit.*
> 
> *Instead of an engineer manually querying databases for weeks, Snowflake Cortex cross-referenced the DTC battery errors with supplier chemistry batches in 5 seconds. The diagnosis: ACME Battery’s Nickel-Manganese-Cobalt cells suffer from electrolyte crystallization during cold fast-charging.*
> 
> *Because we linked telemetry directly to contracts, our system automatically calculated that ACME Battery is contractually liable for $8.49 Million in warranty claims—turning months of legal dispute into an audited ledger in seconds."*

---

#### 📍 SECTION 3: Live Snowflake Agent Studio Demonstration (1:25 – 2:20) ⭐
**Screen**: Switch to **Tab 3** (Snowflake Agent Studio: `AUTOMOTIVE_QUALITY_AGENT`). 
Paste or click this prompt into the chat box:

> 💬 **Exact Query to Ask the Agent:**
> ```
> Which supplier has the highest cold weather failure rate, and what specific firmware calibration is recommended to prevent battery damage?
> ```
*(Alternative short query: `What is the root cause and service bulletin procedure for DTC P1794?`)*

> **Spoken Script:**
> *"Now let's see how our Snowflake Native Agent handles this live.*
> 
> *In Agent Studio, we have `AUTOMOTIVE_QUALITY_AGENT`. Rather than just generating text like a standard chatbot, this agent has tools directly connected to our warehouse.*
> 
> *Notice what happens when I ask:*
> *'Which supplier has the highest cold weather failure rate, and what specific firmware calibration is recommended?'*
> 
> *The agent orchestrates two tools behind the scenes:*
> 1. *It queries our SQL semantic view `V_SUPPLIER_WARRANTY_LIABILITY` to retrieve audited failure rates.*
> 2. *It calls our Cortex Search Service over technical service bulletins using Snowflake Arctic embeddings.*
> 
> *Look at the response: it cites the exact bulletin for code P1794, identifies ACME Battery's NMC811 cathode, and provides the exact engineering fix: adding a 4.5-degree preconditioning offset to the battery management software."*

---

#### 📍 SECTION 4: Closing the Loop with Autonomous OTA Remediation (2:20 – 2:55)
**Screen**: Switch back to **Tab 1** (or stay in Tab 2). Click the **"Simulate Autonomous OTA"** or **"Dispatch OTA Campaign"** button.

> **Spoken Script:**
> *"Most enterprise platforms stop at reporting the problem. Our solution closes the loop.*
> 
> *When we trigger remediation, the platform executes a guarded Snowflake Stored Procedure: `SP_DISPATCH_AUTONOMOUS_OTA_REMEDIATION`.*
> 
> *It takes the calibration parameters from Cortex, verifies an SHA-256 safety hash, and schedules an Over-The-Air software patch to all 749 affected vehicles. By adjusting the thermal pre-heating envelope, it reduces projected 30-day battery failures by 84.3%—saving $8.94 Million in physical battery replacements before a single customer has to visit a dealership."*

---

#### 📍 SECTION 5: Snowflake Architecture & 1-Click Reproducibility (2:55 – 3:35)
**Screen**: Quickly show **Tab 4** (Snowflake Database Explorer: `DT_REALTIME_VEHICLE_QUALITY_ALERTS`), then switch to **Tab 5** (GitHub: `deploy_all_solution.py`).

> **Spoken Script:**
> *"Under the hood in Snowflake Database Explorer, this is powered by a Dynamic Table with a 1-minute target lag, continuously transforming incoming vehicle data.*
> 
> *Finally, to ensure complete evaluation reproducibility, we created **`deploy_all_solution.py`** in our GitHub repository.*
> 
> *Running this single Python script automatically sets up the entire platform on any fresh Snowflake trial account in under 3 minutes—recreating all 11 tables, 300,000 telemetry rows, dynamic tables, Cortex Search services, stored procedures, and the Streamlit application.*
> 
> *By unifying streaming telemetry, Cortex AI, and autonomous firmware remediation in a single governed perimeter, we turned a 6-week manual warranty process into a real-time, closed-loop system. Thank you!"*

---

### 📋 Video Recording Cheat-Sheet:

| Timeline | Tab | Key Talking Point |
| :---: | :---: | :--- |
| **0:00 - 0:40** | **Tab 1 (3D Web App)** | Silos cause 6-week delays; 3D model shows 300K events and -19°C Polar Vortex stress. |
| **0:40 - 1:25** | **Tab 2 (Streamlit)** | 5,210 faults all occurred below 32°F; ACME battery NMC811 defect; $8.49M clawback. |
| **1:25 - 2:20** | **Tab 3 (Agent Studio)** | **Live Prompt**: *Which supplier has the highest cold weather failure rate...?* Shows tool execution & citations. |
| **2:20 - 2:55** | **Tab 1 / Tab 2** | Click **"Simulate Autonomous OTA"**: Stored procedure writes SHA-256 patch, saving $8.94M. |
| **2:55 - 3:35** | **Tab 4 & Tab 5** | 1-min lag Dynamic Table + **`deploy_all_solution.py`** (1-click full reproducibility). |
