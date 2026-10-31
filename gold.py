import os
import duckdb

os.makedirs("data/gold", exist_ok=True)
con = duckdb.connect()
SILVER = "read_parquet('data/silver/sessions.parquet')"

GOLD_SQL = f"""
SELECT
    session_date,
    COUNT(DISTINCT player_id) AS DAU,              
    COUNT(*) AS n_sessions,        
    ROUND(AVG(session_minutes),1) AS avg_session_minutes,
    SUM(n_matches) AS total_matches
FROM {SILVER}       
GROUP BY session_date
"""

con.sql(GOLD_SQL + " ORDER BY session_date").show(max_rows=40)

# 验证通过后再取消注释：
con.execute(f"COPY ({GOLD_SQL}) TO 'data/gold/daily_metrics.parquet' (FORMAT PARQUET)")