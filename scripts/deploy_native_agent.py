import json
import snowflake.connector

conn = snowflake.connector.connect(
    user='rohitishere',
    password='Vande@20345678',
    account='bljohcq-fob95633',
    warehouse='AUTOMOTIVE_WH',
    database='AUTOMOTIVE_INTELLIGENCE_DB',
    schema='PUBLIC'
)
cur = conn.cursor()

with open('scripts/native_agent_spec_v4.json', 'r') as f:
    spec = json.load(f)

# Ensure semantic model points to the correct stage location
spec["tool_resources"]["automotive_analyst"] = {
    "semantic_model_file": "@AUTOMOTIVE_INTELLIGENCE_DB.PUBLIC.SEMANTIC_MODELS_STAGE/semantic_models_stage/automotive_semantic_model.yaml",
    "execution_environment": {
        "type": "warehouse",
        "warehouse": "AUTOMOTIVE_WH"
    }
}

spec_json_str = json.dumps(spec)

print("Deploying AUTOMOTIVE_QUALITY_AGENT with full tools specification...")
sql = f"CREATE OR REPLACE AGENT AUTOMOTIVE_QUALITY_AGENT FROM SPECIFICATION $${spec_json_str}$$"
cur.execute(sql)
print("SUCCESS creating AUTOMOTIVE_QUALITY_AGENT!")

# Clean up TEST_AGENT
cur.execute("DROP AGENT IF EXISTS TEST_AGENT")

cur.execute("DESCRIBE AGENT AUTOMOTIVE_QUALITY_AGENT")
cols = [c[0] for c in cur.description]
row = cur.fetchone()
d = dict(zip(cols, row))
print("Agent Spec in Snowflake length:", len(d.get('agent_spec') or ''))
print("Agent Spec in Snowflake preview:", str(d.get('agent_spec'))[:300])

conn.close()
