import os
import duckdb

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
    MAX("timestamp") AS logout_time,
    CAST(login_time AS DATE) AS session_date,
    date_diff('minutes',login_time,logout_time) AS session_minutes,
    COUNT(*) FILTER(WHERE event_type = 'match_start') AS n_matches
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

