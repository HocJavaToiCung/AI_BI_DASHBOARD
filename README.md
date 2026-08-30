<div align="center">

# 🤖 AI Business Intelligence Dashboard

### Hệ thống AI hỗ trợ phân tích tài chính doanh nghiệp bằng ngôn ngữ tự nhiên

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js" />
  <img src="https://img.shields.io/badge/DuckDB-FFF000?style=for-the-badge&logo=duckdb&logoColor=black" alt="DuckDB" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
</p>

</div>

<hr />

## 01. Hero / Project Identity

| Thuộc tính | Chi tiết |
|------------|----------|
| **Tên dự án** | AI Business Intelligence Dashboard |
|**Mục tiêu** | Cho phép người dùng hỏi dữ liệu tài chính bằng tiếng Việt, nhận số liệu chính xác và có thể truy vết nguồn gốc |
| **Nguyên tắc cốt lõi** | AI hiểu câu hỏi; máy tính tính số liệu; LLM không tự quyết định giá trị cuối cùng |
| **Người thực hiện** | phamngocuyenhi| HocJavaToiCung |
| **Cập nhật** | 30/08/2026 |

---

## 02. One-Minute Overview

Hệ thống chuyển câu hỏi tiếng Việt thành phân tích tài chính có kiểm soát:

```text
Câu hỏi tự nhiên
      ↓
LLM hiểu ý định
      ↓
Structured Request
      ↓
Deterministic Engine tính số liệu
      ↓
Kết quả + biểu đồ + provenance
```

Khác với chatbot thông thường, **không giao quyền tính toán cho LLM**. Mọi con số đều được deterministic engine tính toán và có khả năng truy xuất nguồn gốc.

---

## 03. Demo

> **Ví dụ câu hỏi:**

- "Doanh thu quý II/2026 tăng bao nhiêu phần trăm so với cùng kỳ?"
- "Khu vực nào đóng góp nhiều nhất vào mức giảm lợi nhuận?"
- "Doanh thu giảm bất thường ở sản phẩm nào?"

**Kết quả trả về:** bảng số liệu, biểu đồ, phân rã theo dimension, nguồn dữ liệu và phép tính.

---

## 04. Core Idea

Thay vì cho LLM sinh SQL trực tiếp, hệ thống dùng kiến trúc 7 tầng:

```text
LLM Orchestrator → Validator → Semantic Layer → Query Compiler → Deterministic Engine → Verification → Response
```

**Semantic Layer** định nghĩa rõ metric, alias, công thức, dimension để LLM chỉ được chọn, không được tự suy diễn.

**Structured Request** là đầu ra chuẩn của LLM thay vì SQL:

```json
{
  "intent": "comparison",
  "metric": "gross_margin",
  "period": { "type": "quarter", "value": "2026Q2" },
  "comparison": "same_period_previous_year"
}
```

---

## 05. Key Features

| # | Tính năng | Mô tả |
|---|-----------|-------|
| 1 | **KPI Analysis** | Revenue, Gross Profit, Margin, EBITDA... |
| 2 | **Period Comparison** | YoY, QoQ, MoM, same-period |
| 3 | **Drill-down** | Company → Region → Product → Channel |
| 4 | **Decomposition** | Phân rã biến động theo dimension |
| 5 | **Anomaly Detection** | Phát hiện spike, level_shift, trend_break |
| 6 | **Forecasting** | Dự báo chuỗi thời gian (Naive, ARIMA, TimesFM...) |
| 7 | **Numeric Verification** | 100% claim có provenance hợp lệ |
| 8 | **Vietnamese Benchmark** | 250 câu tiếng Việt có difficulty, ground truth |

---

## 06. Architecture

```text
┌──────────────────────────────────────────────┐
│                    USER / UI                 │
│  Chat · Dashboard · KPI · Charts · Alerts    │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│                LLM ORCHESTRATOR              │
│ Intent · Metric · Filter · Dimension         │
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

## 07. End-to-End Example

**Câu hỏi:** *"Biên lợi nhuận gộp quý II/2026 thay đổi thế nào so với cùng kỳ?"*

**Pipeline:**

```text
Vietnamese Question
      ↓
LLM → Structured Request (intent: comparison, metric: gross_margin, period: 2026Q2)
      ↓
Validator kiểm tra metric/period hợp lệ
      ↓
Semantic Layer trả công thức: gross_profit / net_revenue
      ↓
Query Compiler sinh SQL
      ↓
Deterministic Engine tính: (108 - 100) / 100 = 8%
      ↓
Verification kiểm tra unit, period, provenance
      ↓
Response: "Doanh thu tăng 8% so với cùng kỳ" + biểu đồ
```

**LLM không tự tính 8%. LLM chỉ diễn đạt kết quả.**

---

## 08. Research & Evaluation

### Research Questions

| RQ | Câu hỏi | Đánh giá |
|----|---------|----------|
| RQ1 | Semantic Layer có cải thiện accuracy của NL BI không? | A vs B (Semantic Layer on/off) |
| RQ2 | Deterministic + Provenance có giảm numerical hallucination không? | Numeric Correctness, Coverage, Abstention |
| RQ3 | Foundation forecasting model tốt hơn statistical baseline trên chuỗi tài chính không? | MASE, MAE, Prediction Interval |

### Ablation Study

So sánh 4 cấu hình: Raw LLM / +Semantic Layer / +Few-shot / +Self-repair

### User Study

So sánh Traditional BI vs AI BI Dashboard (12–15 participants, paired measurements)

---

## 09. Results

### Success Criteria

| Tiêu chí | Mục tiêu |
|----------|----------|
cần bổ sung...

---

## 10. Data & Benchmark

### Datasets

| # | Dataset | Mục đích | Kích thước |
|---|---------|----------|------------|
| 1 | **SEC EDGAR** | Dữ liệu tài chính doanh nghiệp thật | 26 quý (2020–2026) |
| 2 | **Online Retail II** | Drill-down sản phẩm/khu vực/khách hàng | ~1 triệu giao dịch |
| 3 | **BookSQL** | Text-to-SQL kế toán, benchmark adaptation | 100.000 cặp câu hỏi–SQL |
| 4 | **Synthetic Data** | Anomaly detection ground truth | 101.631 dòng, 184 scenarios |
| 5 | **Monash TSF** | Dự báo chuỗi thời gian | 4 bộ (Hospital, M4, Tourism) |
| 6 | **TSB-AD-U** | Đối chứng phát hiện bất thường | 870 chuỗi, 23 bộ |

### Benchmark

- **250 câu hỏi tiếng Việt:** Easy 80 / Medium 90 / Hard 60 / Out-of-scope 20
- Mỗi câu có: difficulty, expected answer, intent, metric, dimension, filter, ground truth
- Đánh giá: Answer Accuracy, Semantic Accuracy, Numeric Faithfulness, Coverage, Abstention

---

## 11. Quick Start

### Yêu cầu

- Python 3.9+
- Node.js 18+
- DuckDB / PostgreSQL

### Cài đặt

```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

### Chạy

```bash
# Backend
uvicorn api.main:app --reload

# Frontend
npm run dev
```

### Dữ liệu

```bash
# Giải nén SEC EDGAR
7z x "Dataset/Data/2. DỮ LIỆU TÀI CHÍNH DOANH NGHIỆP/*.7z" -oDataset/Data/2. DỮ LIỆU TÀI CHÍNH DOANH NGHIỆP/

# Sinh dữ liệu tổng hợp
python Dataset/Data/3. BỘ SINH DỮ LIỆU TỔNG HỢP/synthetic/run.py
```

---

## 12. Project Status

| Module | Trạng thái |
|--------|-----------|
| SEC Ingestion | ✅ Đã có 26 quý (2020–2026) |
| Semantic Layer | ✅ Đã có metric definitions |
| Structured Request | ✅ Đã có pipeline |
| Deterministic Engine | ✅ Đã có KPI computation |
| Numeric Verification | ✅ Đã có provenance tracking |
| Benchmark 250 câu | ✅ Đã có cấu trúc |
| Visualization | ✅ Đã có Vega-Lite |
| Decomposition | ✅ Đã có contribution analysis |
| Anomaly Detection | ⏳ Cần chạy TSB-AD tập con |
| Forecasting | ⏳ Cần chạy Monash baseline |
| User Study | ⏳ Chưa triển khai |
| Statistical Evaluation | ⏳ Chưa triển khai |

---

## 13. Repository Structure

```
AI_Business_Intelligence/
│
│
├── Dataset/
│   └── Data/                   
│     └── 1. TEXT-TO-SQL/
│     └── 2. DỮ LIỆU TÀI CHÍNH DOANH NGHIỆP
│     └── 3. BỘ SINH DỮ LIỆU TỔNG HỢP
│     └── 4. DỰ BÁO CHUỖI THỜI GIAN
│     └── 5. PHÁT HIỆN BẤT THƯỜNG
│   └── Clean
│   └── Clean_Data
│   └── EDA
└── README.md
└── .gitignore
```

---

## 14. Limitations

1. **Không thay thế chuyên gia tài chính** — hệ thống chỉ hỗ trợ phân tích, không phải kết luận cuối cùng
2. **SEC EDGAR chỉ có báo cáo tổng hợp** — không có sổ cái chi tiết, không drill-down sâu vào từng giao dịch
3. **Online Retail II thời gian 2009–2011** — hơi cũ, cần kiểm tra relevance
4. **Dữ liệu tổng hợp thiếu realism** — seasonality phức tạp và noise thực có thể khác
5. **Không thực hiện causal inference** — chỉ contribution/decomposition, không kết luận nguyên nhân
6. **BookSQL câu hỏi tiếng Anh** — cần dịch và rà lại bởi người bản ngữ
7. **TSB-AD local chỉ có 870 chuỗi** — benchmark gốc có 1.070 chuỗi, cần chọn tập con phù hợp domain tài chính
8. **Không triển khai enterprise infrastructure** — không dùng Kubernetes, Kafka, Airflow trong MVP

---

## 15. Documentation

| Tài liệu | Mô tả |
|----------|-------|
| `README.md` | Tài liệu chính |
| `Dataset/Data/Báo cáo thu thập dữ liệu.md` | Chi tiết 5 nhóm dữ liệu |
| `Program/KẾ_HOẠCH.md` | Tiêu chí đánh giá dataset |
| `docs/architecture.md` | Kiến trúc hệ thống |
| `docs/methodology.md` | Phương pháp nghiên cứu |
| `docs/evaluation.md` | Chi tiết đánh giá |
| `Dataset/Rule_kilo.md` | Quy tắc vận hành KILO |

---

## 16. Citation / License

### License

| Dataset | License |
|---------|---------|
| SEC EDGAR | Public domain (US Government) |
| BookSQL | CC-BY-NC-SA |
| Online Retail II | UCI (nghiên cứu/học tập) |
| Monash TSF | CC-BY 4.0 |
| TSB-AD | Apache 2.0 + per-dataset |
| Synthetic Data | Tự quyết định |

### Tuyên bố khoa học

- **Không tuyên bố:** "Hệ thống luôn đúng."
- **Tuyên bố đúng:** "Trên tập kiểm thử, các claim định lượng được kiểm chứng và truy vết về nguồn dữ liệu hoặc phép tính tương ứng."

- **Không tuyên bố:** "AI tìm ra nguyên nhân."
- **Tuyên bố đúng:** "Hệ thống phân rã mức đóng góp của các dimension vào biến động của chỉ số."