# Design Decisions

- 计算引擎用 DuckDB 而非 PySpark：单机数据量够用、零配置、纯 SQL；规模扩大后再迁移到 Spark。
- Raw 层用 JSONL，按事件日期每天一个文件；Bronze 层存成 Parquet，按日期分区（列式存储，查询更快）。
- Bronze 不做任何清洗，只额外加 filename 和 ingested_at 两列，方便追溯数据来源。
- 允许 session 跨午夜，这是真实情况。
- Session 按 login 切分：每个 login 开始一个新 session（窗口函数累计求和）。
- Session 归属 login 的日期：跨午夜的 session 只算一次，和 DAU 口径一致。