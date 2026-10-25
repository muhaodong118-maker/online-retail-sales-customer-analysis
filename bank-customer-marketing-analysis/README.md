# 银行客户营销经营分析 | Bank Customer Marketing Analytics

> 数据分析作品集项目｜SQL + Python + SQLite + Streamlit

## 1. 项目简介

本项目基于 UCI Machine Learning Repository 的 Bank Marketing 公开数据，围绕葡萄牙一家银行的定期存款电话营销活动，分析不同客群属性、联络渠道、联系频次和历史营销结果与本次认购之间的关联，形成可复现的数据处理、SQL 指标分析、Python 可视化和交互式 Dashboard 流程。

**核心业务问题**

- 整体营销记录量、认购记录量和转化率如何？
- 不同年龄组、职业和账户余额分层的转化表现有什么差异？
- 不同联络渠道、月份和本次联系频次的转化表现有什么差异？
- 历史营销结果与本次认购之间是否存在关联？
- 如何把观察到的差异转化为下一轮可验证的营销试验建议？

**项目技术栈**：Python、Pandas、Matplotlib、SQL、SQLite、Streamlit、Plotly。

## 2. 数据来源与使用说明

- 数据集：UCI Bank Marketing，旧版 `bank-full.csv`。
- 官方页面：https://archive.ics.uci.edu/dataset/222/bank+marketing
- 官方下载包：https://archive.ics.uci.edu/static/public/222/bank+marketing.zip
- 论文引用：Moro, S., Rita, P., & Cortez, P. (2014). *Bank Marketing*. UCI Machine Learning Repository. https://doi.org/10.24432/C5K306
- 数据许可：UCI 页面列明为 CC BY 4.0；使用时保留来源与引用。
- 数据包含 45,211 条记录、17 个字段（包括目标字段 `y`）。原始 CSV 使用分号分隔符。

**重要边界**：数据来自葡萄牙银行电话营销，不代表中国银行的真实经营情况；数据没有客户唯一 ID，行数是营销记录数而不是独立客户数；数据没有产品购买金额、营销成本或完整交易流水，因此无法直接计算真实 ROI、增量收入或客户终身价值。项目结论只做描述性分析，不把分组差异直接解释为因果关系。

## 3. 项目目录

```text
bank-customer-marketing-analysis/
├── app.py                              # Streamlit 交互式 Dashboard
├── run_pipeline.py                     # 一键运行处理、分析、SQLite 与 SQL 查询
├── requirements.txt                    # Python 依赖
├── .gitignore
├── data/
│   ├── raw/                            # 下载的原始数据，不提交 CSV
│   └── processed/                      # 清洗数据，不提交 CSV
├── docs/
│   ├── analysis_plan.md                # 业务问题与指标口径
│   └── data_dictionary.md              # 字段与派生变量说明
├── scripts/
│   ├── download_data.py                # 下载并提取官方数据
│   ├── 01_data_quality.py              # 数据质量检查
│   ├── 02_preprocess.py                # 清洗与派生字段
│   ├── 03_analysis.py                  # 分组指标、结果表和静态图表
│   ├── 04_load_sqlite.py               # 加载 SQLite
│   └── 05_run_sql_queries.py           # 运行 SQL 并导出结果
├── sql/                                # 可单独阅读、运行的 SQL 分析
├── src/common.py                       # 可复用的数据加载和清洗逻辑
├── tests/test_pipeline.py               # 基础单元测试
└── outputs/                            # 本地运行后产生的图表、表格与数据库
```

## 4. 如何运行

建议 Python 3.10 或更高版本。

### Step 1 — 克隆仓库并安装依赖

```bash
git clone https://github.com/YOUR_USERNAME/bank-customer-marketing-analysis.git
cd bank-customer-marketing-analysis
python -m venv .venv
```

Windows PowerShell：

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS / Linux：

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 2 — 获取公开数据

```bash
python scripts/download_data.py
```

脚本会从 UCI 官方下载包中提取 `bank-full.csv` 到 `data/raw/`。若下载失败，可从官方页面手动下载，解压后把 `bank-full.csv` 放到 `data/raw/bank-full.csv`。不要把原始数据文件放在其他路径，除非同步修改脚本里的路径配置。

### Step 3 — 运行完整分析流程

```bash
python run_pipeline.py
```

流程会依次执行：数据质量检查 → 清洗与特征派生 → 指标统计与图表生成 → SQLite 建表 → SQL 查询结果导出。

### Step 4 — 查看 Dashboard

```bash
streamlit run app.py
```

Dashboard 提供职业、婚姻状态、联络渠道、年龄组和月份筛选，以及总体 KPI、年龄组转化率、职业转化率、渠道转化率和本次营销联系频次分析。

### Step 5 — 运行基础测试

```bash
python -m unittest discover -s tests -v
```

## 5. 数据处理规则

- 使用 `sep=';'` 读取原始 CSV。
- 统一文本字段前后空格并规范大小写。
- `unknown` 保留为单独类别，不静默填充为众数。
- 负余额保留，不能仅凭数值为负就判定为脏数据。
- 精确重复行会被报告，不自动删除；是否删除需要进一步核对业务含义。
- `pdays < 0` 被编码为此前没有联系记录；保留原始 `pdays` 字段。
- 新增 `target`、`age_group`、`balance_segment`、`campaign_group`、`previous_contacted` 等可解释字段。
- `duration` 保留用于事后描述，但不用于通话前的客户优先级判断，因为通话时长只有通话结束后才知道。

## 6. 指标口径

| 指标 | 口径 |
|---|---|
| 营销记录数 | 当前数据范围内的记录行数，不是独立客户数 |
| 认购记录数 | `y = yes` 的记录数 |
| 未认购记录数 | `y = no` 的记录数 |
| 转化率 | 认购记录数 / 总营销记录数 × 100% |
| 分组转化率 | 某分组 `y = yes` 的比例，同时展示该组记录数 |

## 7. SQL 分析清单

- `sql/01_overall_kpis.sql`：总体经营指标
- `sql/02_conversion_by_segment.sql`：职业、年龄和余额分层的转化差异
- `sql/03_conversion_by_contact.sql`：联络渠道对比
- `sql/04_conversion_by_month.sql`：月份分布与转化率
- `sql/05_campaign_frequency.sql`：本次营销联系频次
- `sql/06_previous_campaign.sql`：历史营销结果与本次表现
- `sql/07_data_quality_checks.sql`：关键数据质量检查

SQL 结果会导出到 `outputs/sql_results/`，便于用 Excel 检查和制作作品集图表。

## 8. 输出文件

首次下载代码后，仓库中不会包含分析结果或预填的业务结论。请先运行完整流程，再根据生成的 CSV 和图表写出实际发现；不要在运行前照抄假设性的结论。

运行后会生成：

- `outputs/tables/data_quality_summary.json`
- `outputs/tables/data_quality_field_profile.csv`
- `outputs/tables/data_quality_categorical_profile.csv`
- `outputs/tables/overall_kpis.csv`
- `outputs/tables/conversion_by_*.csv`
- `outputs/charts/*.png`
- `outputs/bank_marketing.db`
- `outputs/sql_results/*.csv`

这些输出是运行脚本后生成的，因此默认不会提交到 GitHub。作品集定稿时，可挑选必要的非敏感图表放在 `reports/` 或 README 中；不要上传虚构的分析结论。

## 9. 如何把分析转成经营建议

结论建议采用“数据证据 → 业务解释 → 建议动作 → 验证指标”的结构。例如：某客群转化率看起来较高时，先核查该分组样本量及其他变量的差异，再建议在下一轮营销中做分层 A/B 测试，并用转化率、联系成本和投诉/退订等合适指标验证。不要仅凭横截面转化率就下结论说某渠道一定更有效。

## 10. 后续可迭代方向

1. 在分析报告中补充样本量阈值、置信区间或显著性检验，避免对小样本组过度解读。
2. 如果未来增加分类预测模块，应避免将 `duration` 用作通话前预测特征，并使用合适的时间或分层验证方案。
3. 若要分析真实客户经营价值，需要补充客户 ID、产品持有、交易、营销成本和时间维度数据；当前公开数据不支持这些指标。

## 11. 项目声明

本项目为公开数据的学习与作品集分析。数据仅用于分析与演示，不代表任何银行的实际营销策略或客户数据。
