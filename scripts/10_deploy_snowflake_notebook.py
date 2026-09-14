import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import snowflake.connector
from src.cortex_agents import SNOWFLAKE_CONFIG

def deploy_notebook():
    conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
    cur = conn.cursor()
    
    workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    nb_file = os.path.join(workspace_dir, "notebooks", "automotive_notebook.ipynb").replace("\\", "/")
    
    print(f"Uploading {nb_file} to @STREAMLIT_STAGE...")
    cur.execute(f"PUT file://{nb_file} @STREAMLIT_STAGE OVERWRITE=TRUE AUTO_COMPRESS=FALSE")
    
    print("Creating NOTEBOOK object in Snowflake...")
    try:
        cur.execute("""
        CREATE OR REPLACE NOTEBOOK AUTOMOTIVE_QUALITY_DATA_SCIENCE_NOTEBOOK
        FROM '@AUTOMOTIVE_INTELLIGENCE_DB.PUBLIC.STREAMLIT_STAGE'
        MAIN_FILE = 'automotive_notebook.ipynb'
        QUERY_WAREHOUSE = 'AUTOMOTIVE_WH'
        """)
        print("Notebook created successfully!")
    except Exception as e:
        print("Notebook creation notice (may require Snowsight UI creation depending on account edition):", e)
        
    cur.close()
    conn.close()

if __name__ == "__main__":
    deploy_notebook()
