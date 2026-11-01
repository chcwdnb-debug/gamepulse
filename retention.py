import duckdb

con = duckdb.connect()
BRONZE = "read_parquet('data/bronze/events/*/*.parquet', hive_partitioning = true)"
SILVER = "read_parquet('data/silver/sessions.parquet')"

JOINED_SQL = f"""
WITH cohort AS (
    -- TODO: 从 BRONZE 里取出每个玩家的 player_id 和注册日期（叫 signup_date
    SELECT
        player_id,
        CAST("timestamp" AS DATE) AS signup_date
    FROM {BRONZE}
    WHERE event_type = 'signup'
    --       提示：只要 signup 事件；注册日期 = 把 "timestamp" CAST 成 DATE

),
activity AS (
    SELECT DISTINCT player_id, session_date
    FROM {SILVER}
)
SELECT
    c.player_id,
    c.signup_date,
    a.session_date,
    -- TODO: day_n = 注册后第几天玩的session_date 和 signup_date 相差几天）
    date_diff('day',signup_date,session_date) AS day_n
    --       提示date_diff('day', 早的日期, 晚的日期)
FROM cohort c
LEFT JOIN activity a ON c.player_id = a.player_id
"""
RETENTION_SQL = f"""
    SELECT
        signup_date,
        -- TODO: cohort_size  这天注册了多少人

        COUNT(DISTINCT player_id) AS cohort_size,
         -- TODO: d1_retained   其中第 1 天回来的有多少人
       
        COUNT(DISTINCT player_id) FILTER(WHERE day_n =1) AS d1_retained,
        
             -- TODO: d1_rate       D1 留存率，保留 3 位小数
        CASE WHEN signup_date <= DATE '2026-09-29'
          THEN ROUND(
            COUNT(DISTINCT player_id) FILTER (WHERE day_n = 1) * 1.0
            / COUNT(DISTINCT player_id),3)  
        END AS d1_rate,
        CASE WHEN signup_date <= DATE '2026-09-23'
            THEN ROUND(
        COUNT(DISTINCT player_id) FILTER (WHERE day_n = 7) * 1.0
        / COUNT(DISTINCT player_id),
        3)  
        END AS d7_rate

    FROM ({JOINED_SQL})
    GROUP BY signup_date
"""
con.sql(RETENTION_SQL + " ORDER BY signup_date").show(max_rows=40)
con.execute(f"COPY ({RETENTION_SQL}) TO 'data/gold/retention_by_cohort.parquet' (FORMAT PARQUET)")

con.sql(f"""
    SELECT
        -- TODO: overall_d1
    ROUND(COUNT(DISTINCT player_id) FILTER(WHERE day_n =1 AND signup_date<=DATE '2026-09-29') *1.0 /COUNT(DISTINCT player_id) FILTER (WHERE signup_date<=DATE '2026-09-29'),3) AS  overall_d1,
        -- TODO: overall_d7
    ROUND(COUNT(DISTINCT player_id) FILTER(WHERE day_n =7 AND signup_date<=DATE '2026-09-23') *1.0 /COUNT(DISTINCT player_id) FILTER (WHERE signup_date<=DATE '2026-09-23'),3) AS  overall_d7

    FROM ({JOINED_SQL})
""").show()


con.sql(JOINED_SQL + " ORDER BY c.player_id, a.session_date").show(max_rows=20)