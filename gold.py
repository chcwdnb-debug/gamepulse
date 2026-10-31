import os
import duckdb
BRONZE = "read_parquet('data/bronze/events/*/*.parquet', hive_partitioning = true)"
os.makedirs("data/gold", exist_ok=True)
con = duckdb.connect()
SILVER = "read_parquet('data/silver/sessions.parquet')"

GOLD_SQL = f"""
SELECT
    session_date,
    COUNT(DISTINCT player_id) AS DAU,              
    COUNT(*) AS n_sessions,        
    ROUND(AVG(session_minutes),1) AS avg_session_minutes,
    SUM(n_matches) AS total_matches,
    SUM(revenue) AS revenue,
    COUNT(DISTINCT player_id) FILter(WHERE n_purchases>0) AS payers,
    ROUND( payers  * 1.0/ DAU,3)   AS payer_rate
FROM {SILVER}       
GROUP BY session_date
"""

con.sql(GOLD_SQL + " ORDER BY session_date").show(max_rows=40)

# 验证通过后再取消注释：
con.execute(f"COPY ({GOLD_SQL}) TO 'data/gold/daily_metrics.parquet' (FORMAT PARQUET)")
con.sql(f"""
    SELECT SUM(amount) FROM {BRONZE} WHERE event_type = 'purchase'
    
""").show()
con.sql(f"""
    SELECT SUM(revenue) FROM read_parquet('data/gold/daily_metrics.parquet')
""").show()