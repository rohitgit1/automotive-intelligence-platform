-- 01_setup_database.sql: Initial setup for Automotive Intelligence Platform
CREATE WAREHOUSE IF NOT EXISTS AUTOMOTIVE_WH 
    WITH WAREHOUSE_SIZE = 'XSMALL' 
    AUTO_SUSPEND = 60 
    AUTO_RESUME = TRUE 
    INITIALLY_SUSPENDED = FALSE;

USE WAREHOUSE AUTOMOTIVE_WH;

CREATE DATABASE IF NOT EXISTS AUTOMOTIVE_INTELLIGENCE_DB;
USE DATABASE AUTOMOTIVE_INTELLIGENCE_DB;
USE SCHEMA PUBLIC;

-- Create CSV format for external stage ingestion
CREATE FILE FORMAT IF NOT EXISTS CSVFORMAT 
    SKIP_HEADER = 1 
    TYPE = 'CSV'
    FIELD_OPTIONALLY_ENCLOSED_BY = '"';

-- Create external stage pointing to official Snowflake Quickstart dataset S3 bucket
CREATE STAGE IF NOT EXISTS DATA_STAGE
    DIRECTORY = ( ENABLE = TRUE )
    FILE_FORMAT = CSVFORMAT 
    URL = 's3://sfquickstarts/sfguide_root_cause_analysis_for_vehicle_product_quality_with_snowflake/';

-- Refresh directory to locate staged CSV files
ALTER STAGE DATA_STAGE REFRESH;
