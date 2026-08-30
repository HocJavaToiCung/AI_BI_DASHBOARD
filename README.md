<div align="center">

<h1>📊 AI BUSINESS INTELLIGENCE DASHBOARD 🤖</h1>

<p>
  <b>Hệ thống AI hỗ trợ phân tích tài chính doanh nghiệp, hỏi đáp dữ liệu bằng ngôn ngữ tự nhiên và cung cấp kết quả có thể truy vết</b>
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js" />
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas" />
  <img src="https://img.shields.io/badge/DuckDB-FFF000?style=for-the-badge&logo=duckdb&logoColor=black" alt="DuckDB" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
</p>

</div>

<hr />

## 📖 Giới thiệu

**AI Business Intelligence Dashboard** là hệ thống hỗ trợ phân tích dữ liệu và tài chính doanh nghiệp bằng **ngôn ngữ tự nhiên**, cho phép người dùng đặt câu hỏi bằng tiếng Việt và nhận lại:

* 📈 Số liệu tài chính.
* 📊 Biểu đồ trực quan.
* 🔎 Phân rã và so sánh chỉ số.
* ⚠️ Phát hiện bất thường.
* 🔮 Dự báo chuỗi thời gian.
* 💡 Nhận định dựa trên dữ liệu.
* 🔗 Nguồn dữ liệu và provenance của các con số.

Ý tưởng cốt lõi của hệ thống là:

> **AI quyết định người dùng đang hỏi gì. Máy tính quyết định con số là bao nhiêu.**

Thay vì cho LLM trực tiếp sinh SQL và tự quyết định kết quả tài chính, hệ thống sử dụng kiến trúc nhiều tầng:

```text
Natural Language
      ↓
LLM Understanding
      ↓
Structured Request
      ↓
Validation
      ↓
Semantic Layer
      ↓
Query Compiler
      ↓
Deterministic Analytics
      ↓
Numeric Verification
      ↓
Provenance
      ↓
LLM Explanation
      ↓
Final Response
```

### ⚠️ Lưu ý quan trọng

Hệ thống **không thay thế kế toán, kiểm toán viên, chuyên gia tài chính hoặc nhà quản trị doanh nghiệp**.

Các kết quả do hệ thống cung cấp nhằm mục đích **hỗ trợ phân tích và ra quyết định**, không phải là kết luận tài chính, kế toán hoặc đầu tư cuối cùng.

Đặc biệt, LLM **không được tự quyết định giá trị cuối cùng của các chỉ số tài chính**. Các con số được tính toán bởi deterministic engine và phải có khả năng truy xuất nguồn gốc.

---

# 🎯 Mục tiêu dự án

## 1. Mục tiêu tổng quát

Xây dựng một hệ thống **AI-powered Business Intelligence** cho phép người dùng tương tác với dữ liệu doanh nghiệp bằng ngôn ngữ tự nhiên, đồng thời đảm bảo:

* tính chính xác của số liệu;
* khả năng truy vết;
* khả năng kiểm chứng;
* khả năng giải thích;
* khả năng tái lập kết quả.

## 2. Mục tiêu cụ thể

1. Xây dựng **Semantic Layer** cho các chỉ số tài chính.
2. Chuyển câu hỏi tiếng Việt thành **Structured Request**.
3. Xây dựng Query Compiler và Deterministic Analytics Engine.
4. Xây dựng cơ chế **Numeric Verification**.
5. Xây dựng hệ thống **Provenance Tracking**.
6. Hỗ trợ visualization và dashboard.
7. Hỗ trợ comparison và drill-down.
8. Hỗ trợ contribution/decomposition.
9. Xây dựng anomaly detection.
10. Đánh giá forecasting trên chuỗi tài chính.
11. Xây dựng benchmark tiếng Việt.
12. Thực hiện ablation study và user study.

---

# 💡 Ý tưởng cốt lõi

Các hệ thống BI truyền thống thường yêu cầu người dùng:

```text
Dashboard
   ↓
Chọn KPI
   ↓
Chọn bộ lọc
   ↓
Chọn khoảng thời gian
   ↓
Xem biểu đồ
```

Điều này gây hạn chế khi người dùng có những câu hỏi chưa được thiết kế sẵn.

Ví dụ:

> "Doanh thu quý II năm 2026 tăng bao nhiêu phần trăm so với cùng kỳ năm trước?"

Hoặc:

> "Khu vực nào đóng góp nhiều nhất vào mức giảm lợi nhuận trong quý này?"

Hoặc:

> "Doanh thu giảm bất thường ở sản phẩm nào?"

Hệ thống hướng đến việc biến các câu hỏi trên thành một pipeline có kiểm soát:

```text
Câu hỏi tự nhiên
      ↓
Hiểu ý định
      ↓
Xác định metric
      ↓
Xác định dimension
      ↓
Xác định filter
      ↓
Structured Request
      ↓
Deterministic computation
      ↓
Verified result
      ↓
Natural-language explanation
```

---

# 🏗️ Kiến trúc tổng thể

```text
┌──────────────────────────────────────────────┐
│                    USER / UI                 │
│  Chat · Dashboard · KPI · Charts · Alerts    │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│                LLM ORCHESTRATOR              │
│ Intent · Metric · Filter · Dimension         │
│ → Structured Request                         │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│                 REQUEST VALIDATOR             │
│ Schema · Metric · Permission · Time · Unit   │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│                  SEMANTIC LAYER              │
│ Metric · Formula · Unit · Alias · Dimension  │
│ Source · Version · Business Definition       │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│                  QUERY COMPILER               │
│ Structured Request → SQL / Computation       │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│              DETERMINISTIC ENGINE             │
│ KPI · Comparison · Drill-down · Decomposition│
│ Chart Data · Forecast · Anomaly               │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│                VERIFICATION LAYER             │
│ Numeric · Calculation · Unit · Period         │
│ Provenance · Logical Support                  │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│                RESPONSE GENERATOR             │
│ Table · Chart · Explanation · Sources         │
└──────────────────────────────────────────────┘
```

---

# 📐 Semantic Layer

Semantic Layer là thành phần trung tâm của hệ thống.

Mỗi metric được định nghĩa một cách có cấu trúc để LLM không tự suy diễn công thức.

Ví dụ:

```yaml
metric_id: gross_margin

name: Biên lợi nhuận gộp

aliases:
  - tỷ suất lợi nhuận gộp
  - GPM
  - gross profit margin

formula:
  type: ratio
  numerator: gross_profit
  denominator: net_revenue

unit: percent

dimensions:
  - time
  - company
  - region
  - product
  - channel

source:
  dataset: SEC

version: 1.0
```

## Nguyên tắc

LLM chỉ được lựa chọn:

* metric đã tồn tại;
* dimension đã tồn tại;
* filter hợp lệ;
* period hợp lệ;
* comparison hợp lệ.

Nếu câu hỏi nằm ngoài semantic layer:

```text
→ Không đoán
→ Không tạo metric mới
→ Không tự sinh SQL tùy ý
→ Trả về trạng thái Unsupported
```

---

# 🧠 Structured Request

LLM **không tạo SQL trực tiếp**.

Ví dụ người dùng hỏi:

> "Biên lợi nhuận gộp quý II/2026 thay đổi thế nào so với cùng kỳ?"

LLM chuyển thành:

```json
{
  "intent": "comparison",
  "metric": "gross_margin",
  "period": {
    "type": "quarter",
    "value": "2026Q2"
  },
  "comparison": "same_period_previous_year",
  "dimensions": [],
  "filters": []
}
```

Pipeline:

```text
Vietnamese Question
        ↓
Intent Detection
        ↓
Metric Resolution
        ↓
Dimension Resolution
        ↓
Filter Resolution
        ↓
Structured Request
        ↓
Validation
        ↓
Query Compiler
        ↓
Deterministic Execution
```

---

# 🔢 Deterministic Analytics

Các phép tính tài chính được thực hiện bằng code/query engine thay vì LLM.

Ví dụ:

```text
Revenue_current  = 108
Revenue_previous = 100

Growth Rate
= (108 - 100) / 100
= 8%
```

LLM chỉ nhận kết quả:

```json
{
  "metric": "revenue_growth",
  "value": 0.08,
  "unit": "percent"
}
```

và có thể diễn đạt thành:

> Doanh thu tăng 8% so với cùng kỳ.

LLM **không được tự tính hoặc sửa đổi con số này**.

---

# 🔗 Numeric Verification & Provenance

## 1. Vấn đề

Việc chỉ kiểm tra xem một con số có xuất hiện trong database hay không là chưa đủ.

Ví dụ:

> "Doanh thu tăng 8%."

Con số `8%` có thể là kết quả của phép tính:

```text
Revenue_current = 108
Revenue_previous = 100

(108 - 100) / 100 = 8%
```

Do đó hệ thống cần lưu **claim provenance**.

## 2. Claim Provenance

```json
{
  "claim": "Doanh thu tăng 8%",
  "value": 0.08,
  "source": {
    "metric": "revenue",
    "current_period": "2026Q2",
    "previous_period": "2025Q2"
  },
  "calculation": "(108 - 100) / 100"
}
```

Pipeline kiểm chứng:

```text
Source Data
     ↓
Calculation
     ↓
Result
     ↓
Claim
```

## 3. Verification layers

Hệ thống kiểm tra:

```text
1. Numeric correctness
2. Calculation correctness
3. Unit consistency
4. Period consistency
5. Source provenance
6. Logical support
```

Mục tiêu nghiên cứu:

> **100% claim định lượng trên benchmark phải có provenance hợp lệ.**

Đây là mục tiêu đánh giá trên benchmark, không phải tuyên bố rằng hệ thống luôn đúng trong mọi tình huống thực tế.

---

# 📊 Business Intelligence Features

## 1. KPI Analysis

Hỗ trợ các chỉ số như:

* Revenue.
* Gross Profit.
* Operating Income.
* Net Income.
* EBITDA.
* Gross Margin.
* Operating Margin.
* Net Profit Margin.
* Revenue Growth.
* Earnings Growth.
* Expense Growth.

---

## 2. Period Comparison

Hỗ trợ:

```text
YoY
QoQ
MoM
Period-over-period
Same-period comparison
```

Ví dụ:

```text
Revenue Q2 2026
        vs
Revenue Q2 2025
```

---

## 3. Drill-down

Người dùng có thể phân tích:

```text
Company
   ↓
Region
   ↓
Product
   ↓
Channel
```

Ví dụ:

> "Khu vực nào tạo ra phần lớn mức giảm doanh thu?"

Hệ thống thực hiện:

```text
Total Revenue Change
        ↓
Contribution by Region
        ↓
Rank
        ↓
Visualization
```

---

# 🧩 Contribution / Decomposition

Hệ thống phân rã biến động thành các thành phần đóng góp.

Ví dụ:

```text
Tổng doanh thu giảm: -12%

Central Region       -9 pp
Product A            -6 pp
Product B            -2 pp
Other                +5 pp
```

Mục đích:

> Xác định **dimension đóng góp bao nhiêu vào biến động**.

### Không thực hiện causal inference

Hệ thống không được tự kết luận:

> "Doanh thu giảm vì đối thủ giảm giá."

nếu dữ liệu không cung cấp bằng chứng nhân quả.

Do đó thuật ngữ sử dụng trong dự án là:

> **Contribution / Decomposition**

thay vì:

> **Causal Analysis**

---

# 🚨 Anomaly Detection

Hệ thống hỗ trợ phát hiện:

1. Point anomaly.
2. Contextual anomaly.
3. Collective anomaly.
4. Trend shift.
5. Seasonal violation.

Synthetic dataset được sử dụng để tạo ground truth.

Ví dụ:

```json
{
  "timestamp": "2026-03-01",
  "dimension": "region",
  "value": 120,
  "is_anomaly": true,
  "anomaly_type": "trend_shift"
}
```

Kết quả có thể được trình bày:

```text
⚠️ Anomaly detected

Metric:
Revenue

Dimension:
North Region

Period:
March 2026

Expected:
95

Actual:
120

Deviation:
+26.3%
```

---

# 🔮 Forecasting

Forecasting được xem là module mở rộng của hệ thống.

Baseline:

```text
Naive
Seasonal Naive
ARIMA
ETS
```

So sánh với:

```text
StatsForecast
TimesFM
Chronos
```

## Evaluation protocol

Không sử dụng random train/test split.

Sử dụng:

> **Rolling-origin evaluation**

Ví dụ:

```text
Train → 2018–2022
Test  → Q1 2023

Train → 2018–Q1 2023
Test  → Q2 2023

Train → 2018–Q2 2023
Test  → Q3 2023
```

Đánh giá riêng theo:

```text
h = 1
h = 2
h = 4
h = 8
```

Metrics:

* MAE.
* MASE.
* RMSE nếu phù hợp.
* Prediction Interval Coverage.

Baseline quan trọng:

> **Seasonal Naive**

Mục tiêu tham khảo:

```text
MASE < 1
```

nghĩa là mô hình tốt hơn baseline tương ứng.

---

# 🧪 Benchmark

## Bộ câu hỏi

Xây dựng khoảng **250 câu hỏi tiếng Việt**.

| Nhóm                | Số lượng |
| ------------------- | -------: |
| Easy                |       80 |
| Medium              |       90 |
| Hard                |       60 |
| Out-of-scope / Trap |       20 |
| **Tổng**            |  **250** |

## Difficulty

Difficulty được xác định dựa trên complexity:

```text
Metric                    +1
Comparison                +1
Filter                    +1
Grouping                  +1
Multiple dimensions       +1
Nested calculation        +2
Ambiguity                 +2
```

Không chỉ gán difficulty bằng cảm tính.

---

# 📚 Nguồn Benchmark

Benchmark gồm:

```text
250 Questions
├── Adapted from BookSQL
├── Newly authored Vietnamese questions
└── Vietnamese accounting-specific questions
```

BookSQL được sử dụng như:

* nguồn tham khảo;
* cơ sở để thiết kế benchmark;
* nguồn đối chiếu với bài toán Text-to-SQL.

Các câu hỏi được chuyển ngữ/adapt sẽ được đánh dấu riêng để tránh coi toàn bộ câu dịch là benchmark hoàn toàn độc lập.

---

# 🔬 Research Questions

## RQ1 — Semantic Layer

> Semantic Layer có cải thiện độ chính xác của Natural-Language BI không?

### Hypothesis

```text
H1:
Semantic Layer configuration
có accuracy cao hơn
Raw LLM configuration.
```

Mức cải thiện mục tiêu:

```text
Minimum practical effect: +10 percentage points
Expected effect: +20 percentage points
```

Đây là hypothesis/acceptance target, không phải kết quả được giả định trước.

---

# RQ2 — Numeric Faithfulness

> Deterministic computation kết hợp provenance verification có giảm numerical hallucination không?

Đo:

### Numeric Correctness

```text
Correct numeric claims
----------------------
All numeric claims
```

### Coverage

```text
Answered valid questions
------------------------
All valid questions
```

### Abstention Accuracy

```text
Correctly rejected unsupported questions
----------------------------------------
All unsupported questions
```

Mục tiêu:

> Tối ưu đồng thời **Safety + Coverage**, thay vì giảm hallucination bằng cách từ chối tất cả câu hỏi khó.

---

# RQ3 — Forecasting

> Foundation forecasting models có cải thiện đáng kể độ chính xác trên chuỗi tài chính doanh nghiệp ngắn so với statistical baselines không?

So sánh:

```text
Naive
Seasonal Naive
ARIMA / ETS
StatsForecast
TimesFM
Chronos
```

Đánh giá bằng:

* MAE;
* MASE;
* RMSE;
* prediction interval coverage;
* statistical tests.

---

# 🧪 Ablation Study

So sánh bốn cấu hình:

| Configuration | Semantic Layer | Few-shot | Self-repair |
| ------------- | :------------: | :------: | :---------: |
| A             |        ❌       |     ❌    |      ❌      |
| B             |        ✅       |     ❌    |      ❌      |
| C             |        ✅       |     ✅    |      ❌      |
| D             |        ✅       |     ✅    |      ✅      |

### RQ1 comparison

So sánh chính:

```text
A vs B
```

để đánh giá riêng tác động của Semantic Layer.

### Các yếu tố giữ cố định

* LLM.
* Prompt.
* Temperature.
* Token limit.
* Dataset.
* Benchmark.
* Execution environment.
* Retry policy.

---

# 📏 Evaluation Metrics

## Research Metrics

| Metric                | Ý nghĩa                           |
| --------------------- | --------------------------------- |
| Answer Accuracy       | Tỷ lệ câu trả lời đúng            |
| Semantic Accuracy     | Chọn đúng intent/metric           |
| Numeric Faithfulness  | Claim có provenance hợp lệ        |
| Coverage              | Tỷ lệ câu hỏi hợp lệ được trả lời |
| Abstention Accuracy   | Khả năng từ chối đúng             |
| MASE                  | Đánh giá forecasting              |
| F1                    | Đánh giá anomaly detection        |
| Contribution Accuracy | Độ chính xác decomposition        |

## System Metrics

* P95 latency.
* Query failure rate.
* Token usage.
* Cost/query.
* Logging completeness.

## User Metrics

* Task completion time.
* Task correctness.
* SUS.
* User preference.
* Error rate.

---

# 📊 Statistical Evaluation

Không chỉ báo cáo:

```text
A = 70%
B = 84%
```

Mà báo cáo:

```text
A = 70%
B = 84%

Δ = +14 percentage points
95% CI = [...]
p-value = [...]
effect size = [...]
```

Với user study:

* cùng participant thực hiện các điều kiện;
* counterbalance thứ tự;
* sử dụng paired measurements;
* phân tích thời gian hoàn thành và độ chính xác.

---

# 👥 User Study

Mẫu dự kiến:

```text
12–15 participants
```

Tiêu chí:

* có kiến thức tài chính/kế toán;
* sử dụng máy tính;
* không yêu cầu chuyên môn AI.

So sánh:

```text
Traditional BI
      vs
AI Business Intelligence Dashboard
```

Đo:

* completion time;
* correctness;
* SUS;
* preference.

Không suy rộng kết quả của mẫu nhỏ thành toàn bộ cộng đồng kế toán hoặc CFO.

---

# 🗃️ Dữ liệu

## SEC EDGAR / XBRL

Nguồn chính cho dữ liệu tài chính doanh nghiệp.

Pipeline:

```text
SEC / XBRL
     ↓
Raw Data
     ↓
Normalization
     ↓
Concept Mapping
     ↓
Semantic Layer
     ↓
Analytics Database
```

Lưu các metadata:

```text
Company
Concept
Metric
Unit
Period
Filing
Source
Version
Provenance
```

---

## Online Retail II

Được sử dụng bổ sung cho:

* transaction analytics;
* product analysis;
* customer dimension;
* country dimension;
* drill-down.

Không sử dụng làm nguồn bằng chứng chính cho accounting analytics.

---

## BookSQL

Sử dụng cho:

* tham khảo Text-to-SQL;
* benchmark adaptation;
* external comparison.

---

## Synthetic Data

Được sử dụng chủ yếu cho:

* anomaly detection;
* controlled experiments;
* ground-truth evaluation.

---

# 🗂️ Data Model

```text
Company
 ├── company_id
 ├── name
 └── industry

FinancialFact
 ├── company_id
 ├── metric_id
 ├── period
 ├── value
 ├── unit
 └── source_id

Dimension
 ├── dimension_id
 ├── type
 └── value

MetricDefinition
 ├── metric_id
 ├── formula
 ├── unit
 ├── aliases
 ├── dimensions
 └── version

Provenance
 ├── result_id
 ├── source_id
 ├── calculation
 └── timestamp
```

---

# 🛠️ Technology Stack

| Thành phần           | Công nghệ                                       |
| -------------------- | ----------------------------------------------- |
| Backend              | Python                                          |
| Frontend             | Next.js / TypeScript                            |
| Database Development | DuckDB                                          |
| Database Deployment  | PostgreSQL                                      |
| LLM                  | GPT / Claude + local model nếu phù hợp          |
| Data Processing      | Pandas / Polars                                 |
| Forecasting          | statsmodels / StatsForecast / TimesFM / Chronos |
| Visualization        | Vega-Lite                                       |
| Evaluation           | Python                                          |
| Monitoring           | Langfuse / Internal Logging                     |

### Không sử dụng trong MVP

* Kubernetes.
* Kafka.
* Airflow.
* Hạ tầng distributed phức tạp.

Mục tiêu là tập trung vào **research contribution và reproducibility**, thay vì xây dựng enterprise infrastructure.

---

# 🚀 MVP Architecture

## P0 — Bắt buộc

```text
├── SEC ingestion
├── Semantic Layer
├── Structured Request
├── Request Validator
├── Deterministic Query Engine
├── Numeric Verification
├── Provenance
├── Benchmark 250 câu
└── Ablation Evaluation
```

## P1 — Quan trọng

```text
├── Visualization
├── Decomposition
├── Anomaly Detection
└── User Study
```

## P2 — Nếu còn thời gian

```text
├── Forecasting
├── Proactive Assistant
└── Local LLM Comparison
```

### Nếu thiếu thời gian

Cắt theo thứ tự:

```text
1. Proactive Assistant
2. Forecasting
3. Advanced Anomaly Detection
4. Local LLM
```

Không cắt:

```text
Semantic Layer
Deterministic Engine
Verification
Benchmark
Ablation
```

Đây là **core contribution** của dự án.

---

# 📅 Kế hoạch 16 tuần

| Tuần | Công việc                             |
| ---: | ------------------------------------- |
|    1 | Chốt RQ + architecture                |
|    2 | Thiết kế semantic schema              |
|    3 | SEC ingestion                         |
|    4 | Normalization + database              |
|    5 | Semantic Layer v1                     |
|    6 | Benchmark 250 câu                     |
|    7 | Structured Request + Validator        |
|    8 | Deterministic Query Engine            |
|    9 | Chạy A/B/C/D                          |
|   10 | Numeric Verification + Provenance     |
|   11 | Visualization + Decomposition         |
|   12 | Anomaly Detection                     |
|   13 | Forecasting                           |
|   14 | User Study                            |
|   15 | Error Analysis + Statistical Analysis |
|   16 | README + Report + Presentation + Demo |

### Milestone quan trọng

**Cuối tuần 9**, hệ thống tối thiểu phải chạy được:

```text
Question
    ↓
Structured Request
    ↓
Deterministic Result
    ↓
Evaluation
```

Nếu chưa đạt milestone này:

> Ưu tiên hoàn thiện RQ1 + RQ2 và cắt các module forecasting/anomaly nâng cao.

---

# 🔍 Failure Analysis

Mỗi câu trả lời sai được phân loại:

```text
1. Intent error
2. Metric selection error
3. Dimension error
4. Filter error
5. Time-period error
6. Unit error
7. Query compilation error
8. Calculation error
9. Numeric verification error
10. Unsupported question
```

Ví dụ báo cáo:

```text
Total errors = 100%

Metric selection       25%
Time period            20%
Dimension              15%
Filter                  12%
Intent                  10%
Query compilation       8%
Others                  10%
```

Mục tiêu không chỉ là:

> Accuracy = 88%

mà còn phải trả lời được:

> **Hệ thống sai chủ yếu ở đâu và vì sao?**

---

# 🔐 Security & Data Governance

LLM chỉ được nhận dữ liệu cần thiết cho quá trình phân tích.

Pipeline:

```text
Raw Financial Data
        ↓
Aggregation / Masking
        ↓
LLM
```

Không gửi cho LLM nếu không cần:

* customer identifier;
* PII;
* transaction-level sensitive data;
* confidential business information.

Mọi request nên được audit:

```text
User
Timestamp
Dataset
Metric
Filters
Structured Request
Result
Provenance
```

---

# ✅ Success Criteria

## Core Research

| Tiêu chí                   |               Mục tiêu |
| -------------------------- | ---------------------: |
| Easy/Medium Accuracy       |                  ≥ 75% |
| Hard Accuracy              |                  ≥ 45% |
| Semantic Layer Improvement |               ≥ +10 pp |
| Trap Abstention Accuracy   |                  ≥ 70% |
| Numeric Claim Provenance   | **100% trên test set** |
| Forecast MASE              |     < 1 nếu triển khai |
| Anomaly F1                 |  ≥ 0.70 nếu triển khai |

## System

| Tiêu chí             | Mục tiêu |
| -------------------- | -------: |
| P95 Latency          |    < 12s |
| Query Failure        |     < 2% |
| Logging Completeness |    ≥ 99% |

## User

| Tiêu chí                    | Mục tiêu |
| --------------------------- | -------: |
| Task Completion Improvement |    ≥ 25% |
| SUS                         |     ≥ 68 |

Các ngưỡng trên là **acceptance targets của đề tài**, không phải kết quả đã được chứng minh trước.

---

# 🏆 Expected Contributions

## Contribution 1 — Semantic Layer

Đánh giá thực nghiệm tác động của Semantic Layer đối với Natural-Language BI.

## Contribution 2 — Deterministic Numeric Pipeline

Thiết kế kiến trúc tách biệt:

```text
Language Reasoning
        ≠
Numeric Computation
```

## Contribution 3 — Provenance-based Verification

Mỗi claim định lượng có thể truy ngược:

```text
Source
   ↓
Calculation
   ↓
Result
   ↓
Text Claim
```

## Contribution 4 — Vietnamese Financial BI Benchmark

Xây dựng benchmark tiếng Việt có:

* difficulty;
* expected answer;
* intent;
* metric;
* dimension;
* filter;
* trap/out-of-scope;
* ground truth.

## Contribution 5 — Empirical Ablation

Đánh giá:

```text
Raw LLM
   vs
Semantic Layer
   vs
Semantic Layer + Few-shot
   vs
Full System
```

---

# 📚 Nguyên tắc khoa học

### ❌ Không tuyên bố

> "Hệ thống luôn đúng."

### ✅ Tuyên bố

> "Trên tập kiểm thử, các claim định lượng được kiểm chứng và truy vết về nguồn dữ liệu hoặc phép tính tương ứng."

---

### ❌ Không tuyên bố

> "AI tìm ra nguyên nhân."

### ✅ Tuyên bố

> "Hệ thống phân rã mức đóng góp của các dimension vào biến động của chỉ số."

---

### ❌ Không tuyên bố

> "Foundation model tốt nhất."

### ✅ Tuyên bố

> "Trong tập dữ liệu, horizon và protocol được xác định, foundation model đạt sai số X so với baseline Y."

---

### ❌ Không tuyên bố

> "Semantic Layer chắc chắn tăng 20% accuracy."

### ✅ Tuyên bố

> "Nghiên cứu kiểm định liệu Semantic Layer có tạo ra mức cải thiện có ý nghĩa về accuracy hay không."

---

# 📦 Deliverables

```text
AI_Business_Intelligence/
│
├── backend/
│   ├── api/
│   ├── semantic/
│   ├── compiler/
│   ├── validator/
│   ├── analytics/
│   └── provenance/
│
├── frontend/
│   ├── dashboard/
│   ├── chat/
│   └── charts/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── synthetic/
│
├── benchmark/
│   ├── questions.json
│   ├── ground_truth.json
│   └── evaluation/
│
├── experiments/
│   ├── ablation/
│   ├── forecasting/
│   ├── anomaly/
│   └── user_study/
│
├── semantic_layer/
│   └── metrics.yaml
│
├── docs/
│   ├── architecture.md
│   ├── methodology.md
│   └── evaluation.md
│
├── README.md
└── requirements.txt
```

---

# 🎯 Definition of Done

Dự án được coi là hoàn thành khi:

* [x] SEC data được ingest và normalize.
* [x] Semantic Layer có metric definitions rõ ràng.
* [x] LLM tạo Structured Request thay vì SQL trực tiếp.
* [x] Query Compiler hoạt động.
* [x] Deterministic Engine tính được KPI.
* [x] Numeric claims có provenance.
* [x] Có benchmark khoảng 250 câu.
* [x] Có cấu hình A/B/C/D.
* [x] Có kết quả ablation.
* [x] Có Accuracy + Coverage + Abstention.
* [x] Có Failure Analysis.
* [x] Có Visualization.
* [x] Có Decomposition.
* [ ] Có Anomaly Benchmark nếu triển khai.
* [ ] Có Forecasting Benchmark nếu triển khai.
* [ ] Có User Study.
* [ ] Có Statistical Evaluation.
* [ ] Có Demo.
* [ ] Có tài liệu reproduce.

---

# 🔄 Core Research Pipeline

Toàn bộ dự án có thể tóm tắt bằng pipeline:

```text
                    USER QUESTION
                          │
                          ▼
                  ┌─────────────┐
                  │     LLM     │
                  │ Understand  │
                  │   Intent    │
                  └──────┬──────┘
                         │
                         ▼
                STRUCTURED REQUEST
                         │
                         ▼
                  ┌─────────────┐
                  │  VALIDATOR  │
                  └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │  SEMANTIC   │
                  │    LAYER    │
                  └──────┬──────┘
                         │
                         ▼
                   QUERY COMPILER
                         │
                         ▼
                 DETERMINISTIC ENGINE
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
             KPI    Decomposition Forecast
              │          │          │
              └──────────┼──────────┘
                         ▼
                    RESULT TABLE
                         │
                         ▼
                  PROVENANCE CHECK
                         │
                         ▼
                  ┌─────────────┐
                  │     LLM     │
                  │ Explanation │
                  └──────┬──────┘
                         │
                         ▼
                  FINAL RESPONSE
             Table + Chart + Explanation
```

---

# 🧠 Research Principle

> **LLM có thể hiểu sai. Vì vậy không giao cho LLM quyền quyết định con số.**

> **Máy tính có thể tính đúng. Vì vậy mọi con số cuối cùng phải quay về deterministic computation và provenance.**

Đây là nguyên tắc trung tâm giúp thống nhất **kiến trúc hệ thống, benchmark, thực nghiệm và đánh giá** của toàn bộ đề tài.
