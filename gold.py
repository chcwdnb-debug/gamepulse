import os
import duckdb
BRONZE = "read_parquet('data/bronze/events/*/*.parquet', hive_partitioning = true)"
os.makedirs("data/gold", exist_ok=True)
con = duckdb.connect()
SILVER = "read_parquet('data/silver/sessions.parquet')"

GOLD_SQL = f"""
SELECT
    session_date,
    COUNT(DISTINCT player_id) AS dau,              
    COUNT(*) AS n_sessions,        
    ROUND(AVG(session_minutes),1) AS avg_session_minutes,
    SUM(n_matches) AS total_matches,
    SUM(revenue) AS revenue,
    COUNT(DISTINCT player_id) FILter(WHERE n_purchases>0) AS payers,
    ROUND( payers  * 1.0/ dau,3)   AS payer_rate
FROM {SILVER}       
GROUP BY session_date
"""


CRASH_SQL = f"""
SELECT
    game_version,
    platform,
    -- TODO: n_sessions   这一组有多少个 session
    COUNT(*) AS n_sessions,
    -- TODO: n_crashed    其中多少个是崩溃结束的
    COUNT(*) FILTER(WHERE ended_by_crash) AS n_crashed,
    -- TODO: crash_rate   崩溃率 = n_crashed / n_sessions保留 3 位小数
    ROUND(n_crashed *1.0 /n_sessions,3) AS crash_rate
FROM {SILVER}
GROUP BY game_version, platform
"""
crash_rate_pergame = f"""
SELECT
    ROUND(COUNT(*) FILTER (WHERE event_type ='crash')*1.0 / COUNT(*) FILTER (WHERE event_type ='match_start'),3) AS crash_rate_pergame,
    game_version,platform
FROM {BRONZE}
GROUP BY game_version,platform
ORDER BY game_version, platform

"""


con.sql(crash_rate_pergame).show()       

con.sql(CRASH_SQL + " ORDER BY game_version, platform").show()
con.execute(f"COPY ({CRASH_SQL}) TO 'data/gold/crash_by_version.parquet' (FORMAT PARQUET)")
con.sql(GOLD_SQL + " ORDER BY session_date").show(max_rows=40)

# 验证通过后再取消注释：
con.execute(f"COPY ({GOLD_SQL}) TO 'data/gold/daily_metrics.parquet' (FORMAT PARQUET)")
con.sql(f"""
    SELECT SUM(amount) FROM {BRONZE} WHERE event_type = 'purchase'
    
""").show()
con.sql(f"""
    SELECT SUM(revenue) FROM read_parquet('data/gold/daily_metrics.parquet')
""").show()