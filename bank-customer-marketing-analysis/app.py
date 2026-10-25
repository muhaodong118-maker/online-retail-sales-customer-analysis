from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from src.common import PROCESSED_PATH, require_processed_data  # noqa: E402

st.set_page_config(page_title="银行营销经营分析", page_icon="📊", layout="wide")
st.title("银行客户营销经营分析")
st.caption("UCI Bank Marketing · 定期存款电话营销 · 描述性分析 Dashboard")

if not PROCESSED_PATH.exists():
    st.warning("尚未发现清洗数据。请先在项目根目录运行：python scripts/download_data.py，然后运行：python run_pipeline.py")
    st.stop()

df = require_processed_data()

st.sidebar.header("分析筛选")
def multiselect_filter(label: str, column: str) -> list[str]:
    options = sorted(df[column].dropna().astype(str).unique().tolist())
    return st.sidebar.multiselect(label, options=options, default=options)

selected_jobs = multiselect_filter("职业", "job")
selected_marital = multiselect_filter("婚姻状态", "marital")
selected_contacts = multiselect_filter("联络渠道", "contact")
selected_age = multiselect_filter("年龄组", "age_group")
selected_months = multiselect_filter("月份", "month")

filtered = df[
    df["job"].astype(str).isin(selected_jobs)
    & df["marital"].astype(str).isin(selected_marital)
    & df["contact"].astype(str).isin(selected_contacts)
    & df["age_group"].astype(str).isin(selected_age)
    & df["month"].astype(str).isin(selected_months)
].copy()

if filtered.empty:
    st.info("当前筛选条件没有记录，请调整左侧筛选器。")
    st.stop()

n_records = len(filtered)
n_yes = int(filtered["target"].sum())
n_no = n_records - n_yes
rate = n_yes / n_records * 100 if n_records else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("营销记录数", f"{n_records:,}")
k2.metric("认购记录数", f"{n_yes:,}")
k3.metric("未认购记录数", f"{n_no:,}")
k4.metric("转化率", f"{rate:.2f}%")
st.caption("口径说明：一行对应一条营销记录；该公开数据没有客户唯一 ID，因此记录数不能解释为独立客户数。")

left, right = st.columns(2)
with left:
    st.subheader("按年龄组的转化率")
    by_age = (filtered.groupby("age_group", dropna=False)
              .agg(marketing_records=("target", "size"), subscribed_records=("target", "sum"))
              .reset_index())
    by_age["conversion_rate_pct"] = by_age["subscribed_records"] / by_age["marketing_records"] * 100
    age_order = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+", "unknown"]
    by_age["_order"] = by_age["age_group"].astype(str).map({v: i for i, v in enumerate(age_order)}).fillna(999)
    by_age = by_age.sort_values("_order")
    fig = px.bar(by_age, x="age_group", y="conversion_rate_pct", hover_data=["marketing_records", "subscribed_records"],
                 labels={"age_group": "年龄组", "conversion_rate_pct": "转化率（%）"}, text=by_age["conversion_rate_pct"].map(lambda x: f"{x:.1f}%"))
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("按职业的转化率")
    by_job = (filtered.groupby("job", dropna=False)
              .agg(marketing_records=("target", "size"), subscribed_records=("target", "sum"))
              .reset_index())
    by_job["conversion_rate_pct"] = by_job["subscribed_records"] / by_job["marketing_records"] * 100
    by_job = by_job.sort_values("conversion_rate_pct", ascending=True)
    fig = px.bar(by_job, x="conversion_rate_pct", y="job", orientation="h",
                 hover_data=["marketing_records", "subscribed_records"],
                 labels={"job": "职业", "conversion_rate_pct": "转化率（%）"})
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("按联络渠道的转化率")
    by_contact = (filtered.groupby("contact", dropna=False)
                  .agg(marketing_records=("target", "size"), subscribed_records=("target", "sum"))
                  .reset_index())
    by_contact["conversion_rate_pct"] = by_contact["subscribed_records"] / by_contact["marketing_records"] * 100
    fig = px.bar(by_contact, x="contact", y="conversion_rate_pct", hover_data=["marketing_records", "subscribed_records"],
                 labels={"contact": "联络渠道", "conversion_rate_pct": "转化率（%）"}, text=by_contact["conversion_rate_pct"].map(lambda x: f"{x:.1f}%"))
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("按本次活动联系频次的转化率")
    by_campaign = (filtered.groupby("campaign_group", dropna=False, observed=False)
                   .agg(marketing_records=("target", "size"), subscribed_records=("target", "sum"))
                   .reset_index())
    by_campaign["conversion_rate_pct"] = by_campaign["subscribed_records"] / by_campaign["marketing_records"] * 100
    campaign_order = ["1 contact", "2 contacts", "3 contacts", "4-5 contacts", "6+ contacts", "unknown"]
    by_campaign["_order"] = by_campaign["campaign_group"].astype(str).map({v: i for i, v in enumerate(campaign_order)}).fillna(999)
    by_campaign = by_campaign.sort_values("_order")
    fig = px.bar(by_campaign, x="campaign_group", y="conversion_rate_pct", hover_data=["marketing_records", "subscribed_records"],
                 labels={"campaign_group": "本次活动联系频次", "conversion_rate_pct": "转化率（%）"}, text=by_campaign["conversion_rate_pct"].map(lambda x: f"{x:.1f}%"))
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), showlegend=False, xaxis_tickangle=-15)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("筛选后的指标明细")
summary = (filtered.groupby("poutcome", dropna=False)
           .agg(marketing_records=("target", "size"), subscribed_records=("target", "sum"))
           .reset_index())
summary["not_subscribed_records"] = summary["marketing_records"] - summary["subscribed_records"]
summary["conversion_rate_pct"] = (summary["subscribed_records"] / summary["marketing_records"] * 100).round(2)
st.dataframe(summary.rename(columns={"poutcome": "历史营销结果", "marketing_records": "营销记录数", "subscribed_records": "认购记录数", "not_subscribed_records": "未认购记录数", "conversion_rate_pct": "转化率（%）"}), use_container_width=True, hide_index=True)

st.info("分析边界：分组转化率用于发现关联，不代表因果关系。duration（通话时长）是通话结束后才知道的信息，不用于通话前的客户优先级决策。")
