# scripts/08_deploy_streamlit_in_snowflake.py
# Deploys Streamlit directly inside Snowflake (Streamlit in Snowflake - SiS)
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import snowflake.connector
from src.cortex_agents import SNOWFLAKE_CONFIG

def deploy_sis():
    print("Connecting to Snowflake...")
    conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
    cur = conn.cursor()
    
    workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    app_file = os.path.join(workspace_dir, "streamlit_app.py").replace("\\", "/")
    env_file = os.path.join(workspace_dir, "environment.yml").replace("\\", "/")
    
    print(f"Staging files from: {workspace_dir}")
    print(f"App file: {app_file}")
    print(f"Env file: {env_file}")
    
    # 1. Create Internal Stage
    print("1. Creating STREAMLIT_STAGE...")
    cur.execute("CREATE OR REPLACE STAGE STREAMLIT_STAGE DIRECTORY = (ENABLE = TRUE)")
    
    # 2. Upload files to stage
    print("2. Uploading streamlit_app.py...")
    cur.execute(f"PUT file://{app_file} @STREAMLIT_STAGE OVERWRITE=TRUE AUTO_COMPRESS=FALSE")
    
    print("3. Uploading environment.yml...")
    cur.execute(f"PUT file://{env_file} @STREAMLIT_STAGE OVERWRITE=TRUE AUTO_COMPRESS=FALSE")
    
    # 3. Create Streamlit in Snowflake Object
    print("4. Creating STREAMLIT object in Snowflake...")
    create_sis_sql = """
    CREATE OR REPLACE STREAMLIT AUTOMOTIVE_INTELLIGENCE_PLATFORM
    ROOT_LOCATION = '@AUTOMOTIVE_INTELLIGENCE_DB.PUBLIC.STREAMLIT_STAGE'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = 'AUTOMOTIVE_WH'
    TITLE = 'Automotive Intelligence Platform - Vehicle Quality & Closed-Loop Remediation'
    """
    cur.execute(create_sis_sql)
    
    # 4. Grant Usage
    print("5. Granting usage to PUBLIC role...")
    try:
        cur.execute("GRANT USAGE ON STREAMLIT AUTOMOTIVE_INTELLIGENCE_PLATFORM TO ROLE PUBLIC")
    except Exception as e:
        print("Grant notice:", e)
        
    print("SUCCESS: Streamlit app successfully deployed inside Snowflake!")
    cur.close()
    conn.close()

if __name__ == "__main__":
    deploy_sis()
