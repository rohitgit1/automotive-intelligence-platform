"""
11_deploy_agent.py (v2)
Deploys the AUTOMOTIVE_QUALITY_AGENT via Snowflake REST API with proper
Cortex Search + Cortex Analyst tools configured.
"""
import snowflake.connector
import os
import json
import sys
import requests

sys.stdout.reconfigure(encoding='utf-8')

SNOWFLAKE_CONFIG = {
    "user": "rohitishere",
    "password": "Vande@20345678",
    "account": "bljohcq-fob95633",
    "warehouse": "AUTOMOTIVE_WH",
    "database": "AUTOMOTIVE_INTELLIGENCE_DB",
    "schema": "PUBLIC"
}

ACCOUNT_URL = "https://bljohcq-fob95633.snowflakecomputing.com"

def deploy_agent():
    conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
    cur = conn.cursor()
    
    try:
        # =====================================================================
        # STEP 1: Upload Semantic Model YAML to Stage
        # =====================================================================
        print("[1/5] Uploading semantic model YAML to @SEMANTIC_MODELS_STAGE...")
        
        yaml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "automotive_semantic_model.yaml")
        yaml_path_fwd = yaml_path.replace("\\", "/")
        
        cur.execute(f"PUT 'file://{yaml_path_fwd}' @SEMANTIC_MODELS_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE")
        result = cur.fetchone()
        print(f"  Upload result: {result[0]} -> {result[-2]}")
        
        cur.execute("LIST @SEMANTIC_MODELS_STAGE")
        files = cur.fetchall()
        print(f"  Files in stage: {[f[0] for f in files]}")
        
        # =====================================================================
        # STEP 2: Get a session token from the connection for REST API
        # =====================================================================
        print("\n[2/5] Getting session token for REST API...")
        
        # Get the session token from the existing connection
        cur.execute("SELECT SYSTEM$GET_SNOWFLAKE_PLATFORM_INFO()")
        platform_info = cur.fetchone()[0]
        print(f"  Platform: {platform_info[:100]}...")
        
        # Get the master token from the connection internals
        session_token = conn.rest.token
        master_token = conn.rest.master_token
        print(f"  Session token obtained (length: {len(session_token)})")
        
        # =====================================================================
        # STEP 3: Drop existing agent
        # =====================================================================
        print("\n[3/5] Dropping existing AUTOMOTIVE_QUALITY_AGENT...")
        try:
            cur.execute("DROP AGENT IF EXISTS AUTOMOTIVE_QUALITY_AGENT")
            print("  Dropped successfully.")
        except Exception as e:
            print(f"  Drop note: {e}")
        
        # =====================================================================
        # STEP 4: Create Agent via REST API with tools
        # =====================================================================
        print("\n[4/5] Creating AUTOMOTIVE_QUALITY_AGENT via REST API...")
        
        agent_payload = {
            "name": "AUTOMOTIVE_QUALITY_AGENT",
            "comment": "Enterprise Automotive Quality Intelligence Agent for fleet analytics, warranty analysis, and OTA remediation",
            "agent_config": {
                "instructions": (
                    "You are the Automotive Quality Intelligence Agent for an EV OEM's fleet quality platform. "
                    "You have access to two tools:\n\n"
                    "1. **dtc_bulletin_search** (Cortex Search): Search technical service bulletins and DTC error "
                    "knowledge base documents. Use this when users ask about specific error codes (like P1794), "
                    "battery failure mechanisms, repair procedures, or technical specifications.\n\n"
                    "2. **automotive_quality_analyst** (Cortex Analyst): Query structured fleet data including "
                    "supplier warranty liability, quality metrics, vehicle risk profiles, and OTA campaign history. "
                    "Use this when users ask about supplier failure rates, warranty clawback amounts, vehicle counts, "
                    "risk tiers, or financial exposure data.\n\n"
                    "Always use the appropriate tool to answer questions. Provide specific numbers, supplier names, "
                    "and dollar amounts when available. Be concise and authoritative."
                ),
                "tools": [
                    {
                        "tool_spec": {
                            "type": "cortex_search",
                            "name": "dtc_bulletin_search"
                        },
                        "tool_resources": {
                            "cortex_search": {
                                "name": "dtc_bulletin_search",
                                "service_name": "AUTOMOTIVE_INTELLIGENCE_DB.PUBLIC.DTC_BULLETIN_SEARCH_SERVICE",
                                "max_results": 3,
                                "title_column": "TITLE",
                                "id_column": "DOC_ID"
                            }
                        }
                    },
                    {
                        "tool_spec": {
                            "type": "cortex_analyst",
                            "name": "automotive_quality_analyst"
                        },
                        "tool_resources": {
                            "cortex_analyst": {
                                "name": "automotive_quality_analyst",
                                "semantic_model_file": "@AUTOMOTIVE_INTELLIGENCE_DB.PUBLIC.SEMANTIC_MODELS_STAGE/automotive_semantic_model.yaml"
                            }
                        }
                    }
                ]
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f'Snowflake Token="{session_token}"',
            "X-Snowflake-Authorization-Token-Type": "SNOWFLAKE"
        }
        
        # Try the REST API endpoint
        api_url = f"{ACCOUNT_URL}/api/v2/databases/AUTOMOTIVE_INTELLIGENCE_DB/schemas/PUBLIC/agents?createMode=orReplace"
        
        print(f"  POST {api_url}")
        print(f"  Payload preview: {json.dumps(agent_payload)[:300]}...")
        
        try:
            resp = requests.post(api_url, headers=headers, json=agent_payload, timeout=30)
            print(f"  Response status: {resp.status_code}")
            print(f"  Response body: {resp.text[:500]}")
            
            if resp.status_code in [200, 201]:
                print("  Agent created successfully via REST API!")
            else:
                print(f"  REST API response: {resp.status_code}")
                # Try alternative payload structure
                alt_payload = {
                    "name": "AUTOMOTIVE_QUALITY_AGENT",
                    "comment": "Enterprise Automotive Quality Intelligence Agent",
                    "tools": [
                        {
                            "type": "cortex_search_service",
                            "cortex_search_service": {
                                "service_name": "AUTOMOTIVE_INTELLIGENCE_DB.PUBLIC.DTC_BULLETIN_SEARCH_SERVICE",
                                "max_results": 3,
                                "title_column": "TITLE",
                                "id_column": "DOC_ID"
                            }
                        },
                        {
                            "type": "cortex_analyst_tool",
                            "cortex_analyst_tool": {
                                "semantic_model_file": "@AUTOMOTIVE_INTELLIGENCE_DB.PUBLIC.SEMANTIC_MODELS_STAGE/automotive_semantic_model.yaml"
                            }
                        }
                    ],
                    "instructions": agent_payload["agent_config"]["instructions"]
                }
                
                resp2 = requests.post(api_url, headers=headers, json=alt_payload, timeout=30)
                print(f"\n  Alt payload response: {resp2.status_code}")
                print(f"  Alt response body: {resp2.text[:500]}")
        except Exception as e:
            print(f"  REST API error: {e}")
        
        # =====================================================================
        # STEP 4b: Fallback - Create agent via SQL and configure via Snowsight
        # =====================================================================
        print("\n[4b] Fallback: Creating base agent via SQL...")
        try:
            cur.execute("""
                CREATE OR REPLACE AGENT AUTOMOTIVE_QUALITY_AGENT
                COMMENT = 'Enterprise Automotive Quality Intelligence Agent for fleet analytics, warranty analysis, and OTA remediation'
            """)
            print("  Base agent created via SQL.")
        except Exception as e:
            print(f"  SQL create note: {e}")
        
        # =====================================================================
        # STEP 5: Verify Agent Definition
        # =====================================================================
        print("\n[5/5] Verifying agent definition...")
        try:
            cur.execute("DESCRIBE AGENT AUTOMOTIVE_QUALITY_AGENT")
            desc = cur.fetchall()
            cols = [d[0] for d in cur.description]
            for r in desc:
                row_dict = dict(zip(cols, r))
                print(f"  Name: {row_dict.get('name', 'N/A')}")
                print(f"  Profile: {row_dict.get('profile', 'N/A')}")
                spec = row_dict.get('agent_spec', 'N/A')
                print(f"  Agent Spec: {str(spec)[:400]}")
                print(f"  Comment: {row_dict.get('comment', 'N/A')}")
        except Exception as e:
            print(f"  DESCRIBE error: {e}")
        
        conn.commit()
        print("\n=== DEPLOYMENT COMPLETE ===")
        print("NOTE: If REST API didn't attach tools, configure them via Snowsight Agent Studio UI.")
        print("Agent Studio URL: https://app.snowflake.com/qkxtana/ll44738/#/agent-studio")
        
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    deploy_agent()
