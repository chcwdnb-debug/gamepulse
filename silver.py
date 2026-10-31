import os
import duckdb
import numpy

os.makedirs("data/silver", exist_ok=True)
con = duckdb.connect()
BRONZE = "read_parquet('data/bronze/events/*/*.parquet', hive_partitioning = true)"

SESSIONS_SQL = f"""
WITH numbered AS (
    SELECT
        *,
        SUM(CASE WHEN event_type = 'login' THEN 1 ELSE 0 END) OVER (PARTITION BY player_id ORDER BY "timestamp") AS session_num
    FROM {BRONZE}
)
SELECT
    player_id,
    session_num,
    platform,
    region,
    game_version,
    MIN("timestamp") AS login_time,
    MAX("timestamp") AS session_end_time,
    CAST(login_time AS DATE) AS session_date,
    date_diff('minutes',login_time,session_end_time) AS session_minutes,
    COUNT(*) FILTER(WHERE event_type = 'match_start') AS n_matches,
    COUNT(*) FILTER(WHERE event_type = 'purchase') AS n_purchases,
    COALESCE(SUM(amount),0) AS revenue,
    COUNT(*) FILTER(WHERE event_type = 'crash')>0 AS ended_by_crash
FROM numbered
WHERE session_num >= 1
GROUP BY player_id, session_num, platform, region, game_version
"""
con.sql(f"""
    SELECT  COUNT(session_num), AVG(n_matches),MIN(session_minutes),MAX(session_minutes)
    FROM ({SESSIONS_SQL})
""").show()



con.sql(SESSIONS_SQL + " ORDER BY player_id, session_num").show(max_rows=20)
con.execute(f"COPY ({SESSIONS_SQL}) TO 'data/silver/sessions.parquet' (FORMAT PARQUET)")

con.sql("""
    SELECT SUM(n_purchases) FROM read_parquet('data/silver/sessions.parquet')
""").show()
con.sql("""
    SELECT COUNT(*), COUNT(*) FILTER(WHERE ended_by_crash) FROM read_parquet('data/silver/sessions.parquet')
""").show()
