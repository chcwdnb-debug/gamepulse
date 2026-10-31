import duckdb
import os
os.makedirs("data/bronze", exist_ok=True)   # 新加：先把上级文件夹建好

con = duckdb.connect()

con.execute("""
    COPY (
        SELECT
            *,                                       -- 原始字段全部保留
            CAST("timestamp" AS DATE) AS dt,         -- 分区键：事件日期
            now()                     AS ingested_at -- 什么时候进的 Bronze
        FROM read_json_auto('data/raw/*.jsonl', filename = true)  -- filename 列记录来源文件
    )
    TO 'data/bronze/events'
    (FORMAT PARQUET, PARTITION_BY (dt), OVERWRITE)
""")

BRONZE = "read_parquet('data/bronze/events/*/*.parquet', hive_partitioning = true)"

# 示范查询：每天多少条事件
print(con.sql(f"""
    SELECT dt, COUNT(*) AS n_events
    FROM {BRONZE}
    GROUP BY dt
    ORDER BY dt
"""))
print(con.sql(f"""

    SELECT event_type,COUNT(*) AS n_type
    FROM {BRONZE}
    GROUP BY event_type
    ORDER BY n_type
"""))

print(con.sql(f"""
    SELECT dt, COUNT(DISTINCT player_id)AS dau
    FROM {BRONZE}
    WHERE event_type = 'login'
    GROUP BY dt
    ORDER BY dt
"""))
print(con.sql(f"""
    SELECT dt,COUNT(*)
    FROM {BRONZE}
    WHERE event_type = 'match_end'
    GROUP BY dt
    ORDER BY dt
"""))
print(con.sql(f"""
    SELECT platform,COUNT(DISTINCT player_id)
    FROM {BRONZE}
    GROUP BY platform   
    ORDER BY platform
"""))
print(con.sql(f"""
    SELECT dt,region,COUNT(DISTINCT player_id)
    FROM {BRONZE}
    WHERE event_type = 'login'
    GROUP BY dt,region
    ORDER by dt,region

"""))
print(con.sql(f"""
    SELECT dt,COUNT(DISTINCT player_id)
    FROM {BRONZE}
    WHERE platform ='PS5' AND event_type = 'login'
    GROUP BY dt
    ORDER by dt

"""))
print(con.sql(f"""
    SELECT player_id,COUNT(*) AS n_logins
    FROM {BRONZE}
    WHERE event_type = 'login' 
    GROUP BY player_id
    ORDER BY n_logins DESC
    LIMIT 10  

"""))
print(con.sql(f"""
    SELECT  COUNT(*)FILTER(WHERE event_type='match_start') *1.0 / COUNT(*) FILTER(WHERE event_type='login') 
    FROM {BRONZE}

"""))
