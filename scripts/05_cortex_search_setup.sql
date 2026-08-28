-- 05_cortex_search_setup.sql: Snowflake Cortex Vector Search & Semantic RAG Setup
USE WAREHOUSE AUTOMOTIVE_WH;
USE DATABASE AUTOMOTIVE_INTELLIGENCE_DB;
USE SCHEMA PUBLIC;

-- 1. Create Knowledge Base Table for DTC Error Manuals & Technical Specs
CREATE OR REPLACE TABLE DTC_KNOWLEDGE_BASE (
    doc_id VARCHAR,
    title VARCHAR,
    error_code VARCHAR,
    component_type VARCHAR,
    content VARCHAR,
    embedding VECTOR(FLOAT, 768)
);

-- 2. Populate Knowledge Base with Technical DTC & Battery Engineering Manuals
INSERT INTO DTC_KNOWLEDGE_BASE (doc_id, title, error_code, component_type, content, embedding)
SELECT 
    'DOC-' || error_id,
    'Technical Service Bulletin: ' || error_code,
    error_code,
    'Battery Pack & Thermal Management System',
    'Diagnostic Code ' || error_code || ': ' || description || '. Recommended Service Procedure: Inspect cathode voltage thresholds, test thermal management coolant flow, and evaluate overcurrent protection relay in extreme ambient cold (<32F).',
    SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', 'Diagnostic Code ' || error_code || ': ' || description || '. Recommended Service Procedure: Inspect cathode voltage thresholds.')
FROM DTC_BATTERY_ERROR_CODES;

-- 3. Create Vector Search Query Function
CREATE OR REPLACE FUNCTION SEARCH_DTC_KNOWLEDGE_BASE(query_text VARCHAR)
RETURNS TABLE (title VARCHAR, error_code VARCHAR, content VARCHAR, similarity_score FLOAT)
AS $$
    SELECT 
        title,
        error_code,
        content,
        VECTOR_COSINE_SIMILARITY(
            embedding, 
            SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', query_text)
        ) AS similarity_score
    FROM DTC_KNOWLEDGE_BASE
    ORDER BY similarity_score DESC
    LIMIT 5
$$;
