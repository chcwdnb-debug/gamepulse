import duckdb
import streamlit as st

st.set_page_config(page_title="GamePulse", layout="wide")
con = duckdb.connect()

def q(sql):
    """执行 SQL返回一张表pandas DataFrameStreamlit 可以直接画它"""
    return con.sql(sql).df()

DAILY = "read_parquet('data/gold/daily_metrics.parquet')"
CRASH = "read_parquet('data/gold/crash_by_version.parquet')"
RET   = "read_parquet('data/gold/retention_by_cohort.parquet')"

# ---------- 标题 ----------
st.title("GamePulse — Game Analytics Dashboard")
st.caption("Synthetic game events → Bronze → Silver → Gold → this dashboard")

# ---------- 第一排：4 个核心数字 ----------
kpi = q(f"""
    SELECT
        (SELECT ROUND(AVG(dau), 1)      FROM {DAILY}) AS avg_dau,
        (SELECT ROUND(SUM(revenue), 2)  FROM {DAILY}) AS total_revenue,
        (SELECT SUM(d1_retained) * 1.0 / SUM(cohort_size)
           FROM {RET} WHERE d1_rate IS NOT NULL)      AS d1,
        (SELECT SUM(d7_rate * cohort_size) / SUM(cohort_size)
           FROM {RET} WHERE d7_rate IS NOT NULL)      AS d7
""")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Avg DAU", kpi["avg_dau"][0])
c2.metric("Total revenue", f"${kpi['total_revenue'][0]:,.2f}")
c3.metric("D1 retention", f"{kpi['d1'][0]:.1%}")
c4.metric("D7 retention", f"{kpi['d7'][0]:.1%}")

# ---------- 每日趋势 ----------
daily = q(f"""
    SELECT session_date, dau, revenue, avg_session_minutes, payer_rate
    FROM {DAILY}
    ORDER BY session_date
""")

st.subheader("Daily active users")
st.line_chart(daily, x="session_date", y="dau")

st.subheader("Daily revenue")
st.line_chart(daily, x="session_date", y="revenue")

st.subheader("Average session minutes")
st.line_chart(daily, x="session_date", y="avg_session_minutes")

# ---------- 坏版本 ----------
crash = q(f"""
    SELECT game_version || ' / ' || platform AS segment, crash_rate
    FROM {CRASH}
    ORDER BY game_version, platform
""")
st.subheader("Session crash rate by version x platform")
st.bar_chart(crash, x="segment", y="crash_rate")
st.caption("v1.1 released on 2026-09-15. PS5 on v1.1 crashes ~3x more often than every other segment.")

# ---------- 留存 ----------
ret = q(f"""
    SELECT signup_date, cohort_size, d1_rate, d7_rate
    FROM {RET}
    ORDER BY signup_date
""")
st.subheader("Retention by signup cohort")
st.dataframe(ret, hide_index=True)
st.caption("Empty cells = cohort not mature yet (day N is beyond the data window).")