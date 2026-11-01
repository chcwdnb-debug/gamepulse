# Design Decisions

- 计算引擎用 DuckDB 而非 PySpark：单机数据量够用、零配置、纯 SQL；规模扩大后再迁移到 Spark。
- Raw 层用 JSONL，按事件日期每天一个文件；Bronze 层存成 Parquet，按日期分区（列式存储，查询更快）。
- Bronze 不做任何清洗，只额外加 filename 和 ingested_at 两列，方便追溯数据来源。
- 允许 session 跨午夜，这是真实情况。
- Session 按 login 切分：每个 login 开始一个新 session（窗口函数累计求和）。
- Session 归属 login 的日期：跨午夜的 session 只算一次，和 DAU 口径一致。
- Gold 层预先算好日指标表（DAU、session 数、平均时长、比赛数），看板直接读取，避免每次从原始事件重算，也保证所有地方用的是同一个指标定义。
- 金额目前用 float 存，加总后有浮点误差（如 1089.4900000000002）；生产环境应改用 DECIMAL 或以"分"为单位的整数。
- 留存按注册日 cohort 计算：day_n = 活跃日期 − 该玩家自己的注册日期；D1/D7 = cohort 中 day_n = 1/7 的玩家比例。
- 不成熟的 cohort（第 N 天还在数据范围之外）留存记为 NULL 而不是 0，避免误读为"留存暴跌"；整体留存只用成熟 cohort 加权计算。