import snowflake.connector
import json

SNOWFLAKE_CONFIG = {
    "user": "SOUTHPAW21",
    "password": "Vande@20345678",
    "account": "qkxtana-ll44738",
    "warehouse": "AUTOMOTIVE_WH",
    "database": "AUTOMOTIVE_INTELLIGENCE_DB",
    "schema": "PUBLIC"
}

class CortexAgentsEngine:
    def __init__(self):
        self.model = "mistral-large2"

    def _get_connection(self):
        return snowflake.connector.connect(**SNOWFLAKE_CONFIG)

    def _call_cortex_llm(self, prompt: str, system_prompt: str) -> str:
        full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # Escape single quotes in prompt
            escaped_prompt = full_prompt.replace("'", "''")
            query = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{self.model}', '{escaped_prompt}')"
            cursor.execute(query)
            result = cursor.fetchone()[0]
            return result
        except Exception as e:
            # Fallback to llama3.3-70b or arctic if mistral fails
            try:
                query = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.3-70b', '{escaped_prompt}')"
                cursor.execute(query)
                return cursor.fetchone()[0]
            except Exception as e2:
                return f"Cortex Engine Error: {str(e)}"
        finally:
            cursor.close()
            conn.close()

    def run_quality_monitoring_agent(self, time_window_days: int = 7) -> str:
        """
        Agent 1: Quality Monitoring Agent for Anomaly Detection
        Analyzes vehicle telemetry spikes, DTC frequency, and operating temp anomalies.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(f"""
                SELECT 
                    COUNT(*) AS TOTAL_RECORDS,
                    COUNT(CASE WHEN dtc_error_code != 0 THEN 1 END) AS DTC_ERRORS,
                    ROUND(COUNT(CASE WHEN dtc_error_code != 0 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS FAILURE_RATE_PCT,
                    AVG(avg_temp_f) AS AVG_TEMP,
                    MIN(avg_temp_f) AS MIN_TEMP,
                    MAX(avg_temp_f) AS MAX_TEMP
                FROM V_ROOT_CAUSE_CORRELATION
            """)
            stats = cursor.fetchone()
            data_context = {
                "total_telemetry_records": stats[0],
                "dtc_error_events": stats[1],
                "failure_rate_percentage": stats[2],
                "avg_temp_f": stats[3],
                "min_temp_f": stats[4],
                "max_temp_f": stats[5]
            }
        finally:
            cursor.close()
            conn.close()

        system_prompt = (
            "You are the Quality Monitoring AI Agent for an OEM Automotive Intelligence Platform. "
            "Your job is real-time anomaly detection across vehicle telemetry datasets. "
            "Identify sudden DTC error spikes, extreme weather operational strain, and unusual failure concentrations."
        )
        user_prompt = f"Analyze the following fleet quality telemetry metrics and report top anomalies:\n{json.dumps(data_context, indent=2)}"
        return self._call_cortex_llm(user_prompt, system_prompt)

    def run_root_cause_analysis_agent(self, supplier_filter: str = None, error_code_filter: str = None) -> str:
        """
        Agent 2: Root Cause Analysis Agent for Automated Investigation
        Cross-references supplier quality, battery chemistry, weather extremes, and DTC codes.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            query = """
                SELECT 
                    supplier_name,
                    cathode,
                    anode,
                    error_code,
                    error_description,
                    TEMPERATURE_CATEGORY,
                    COUNT(*) AS FAILURE_COUNT
                FROM V_ROOT_CAUSE_CORRELATION
                WHERE dtc_error_code IS NOT NULL AND dtc_error_code != 0
                GROUP BY supplier_name, cathode, anode, error_code, error_description, TEMPERATURE_CATEGORY
                ORDER BY FAILURE_COUNT DESC
                LIMIT 15;
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            findings = [
                {
                    "supplier": r[0], "cathode": r[1], "anode": r[2],
                    "error_code": r[3], "description": r[4],
                    "temp_condition": r[5], "failure_count": r[6]
                }
                for r in rows
            ]
        finally:
            cursor.close()
            conn.close()

        system_prompt = (
            "You are the Root Cause Analysis (RCA) AI Agent for Automotive Engineering. "
            "You conduct multi-variable automated investigation linking telemetry, battery component chemistry (cathode/anode), "
            "supplier manufacturing quality, and ambient weather extremes. "
            "Provide a clear root-cause breakdown specifying exact component flaws, weather triggers, and corrective actions."
        )
        user_prompt = f"Perform automated root-cause analysis on the top failure patterns:\n{json.dumps(findings, indent=2)}"
        return self._call_cortex_llm(user_prompt, system_prompt)

    def run_predictive_maintenance_agent(self, forecast_days: int = 30) -> str:
        """
        Agent 3: Predictive Maintenance Agent for Failure Forecasting & Recall Planning
        Predicts 30-day failure likelihoods and prioritizes vehicles for preventive service.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT PREDICTED_RISK_TIER, COUNT(*) AS VEHICLE_COUNT
                FROM V_VEHICLE_RISK_PROFILE
                GROUP BY PREDICTED_RISK_TIER
            """)
            risk_breakdown = {r[0]: r[1] for r in cursor.fetchall()}

            cursor.execute("""
                SELECT car_id, vin, state, supplier_name, cathode, HISTORICAL_DTC_COUNT
                FROM V_VEHICLE_RISK_PROFILE
                WHERE PREDICTED_RISK_TIER = 'CRITICAL RISK'
                LIMIT 5
            """)
            critical_samples = [
                {"car_id": r[0], "vin": r[1], "state": r[2], "supplier": r[3], "cathode": r[4], "dtc_count": r[5]}
                for r in cursor.fetchall()
            ]
        finally:
            cursor.close()
            conn.close()

        system_prompt = (
            "You are the Predictive Maintenance AI Agent. Your goal is to forecast vehicle failure risks for the next 30 days "
            "and recommend proactive preventive maintenance schedules and targeted recall strategies."
        )
        user_prompt = (
            f"Forecast 30-day failure expectations based on current risk breakdown:\n"
            f"Risk Tier Summary: {json.dumps(risk_breakdown)}\n"
            f"Critical Vehicles Sample: {json.dumps(critical_samples)}\n"
            f"Provide a 30-day failure forecast and proactive maintenance mitigation plan."
        )
        return self._call_cortex_llm(user_prompt, system_prompt)

if __name__ == "__main__":
    agent = CortexAgentsEngine()
    print("Testing Quality Agent...")
    print(agent.run_quality_monitoring_agent())
