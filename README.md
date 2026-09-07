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

## 01. Project Identity

| Thuộc tính | Chi tiết |
|------------|----------|
| **Tên dự án** | AI Business Intelligence Dashboard |
|**Mục tiêu** | Cho phép người dùng hỏi dữ liệu tài chính bằng tiếng Việt, nhận số liệu chính xác và có thể truy vết nguồn gốc |
| **Nguyên tắc cốt lõi** | AI hiểu câu hỏi; máy tính tính số liệu; LLM không tự quyết định giá trị cuối cùng |
| **Người thực hiện** | uyennhi |
| **Cập nhật** | 30/08/2026 |

---

## 02. Overview

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

## 03. Demo / Screenshot

## 04. Cách chạy 

### Dữ liệu

```bash
# Giải nén SEC EDGAR
7z x "Dataset/Data/2. DỮ LIỆU TÀI CHÍNH DOANH NGHIỆP/*.7z" -oDataset/Data/2. DỮ LIỆU TÀI CHÍNH DOANH NGHIỆP/

# Sinh dữ liệu tổng hợp
python Dataset/Data/3. BỘ SINH DỮ LIỆU TỔNG HỢP/synthetic/run.py
```

## 05. Architecture


---

## 06. End-to-End Example
< 1 quy trình đầu - cuối tháo tác trên giao diện và hệ thông >

---

## 07. Data & Benchmark

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


## 08. Project Status

| Module | Trạng thái |
|--------|-----------|

---

## 09. Repository Structure

```
ai-bi-dashboard/
├── README.md                      ← tài liệu này
├── pyproject.toml
├── docker-compose.yml             # postgres + api + web
│
├── semantic/                      ★ ĐÓNG GÓP CỐT LÕI
│   ├── metrics.yml                # định nghĩa chỉ số
│   ├── entities.yml               # bảng, khóa, quan hệ
│   └── glossary.yml               # từ đồng nghĩa Việt–Anh
│
├── backend/
│   ├── main.py                    # FastAPI
│   ├── semantic_layer.py          # YAML → SQL (tất định)
│   ├── nl2query.py                # AI → phiếu JSON (KHÔNG sinh SQL)
│   ├── decompose.py               # phân rã đóng góp
│   ├── anomaly.py                 # STL + z-score
│   ├── forecast.py                # baseline + mô hình nền tảng
│   ├── narrative.py               # sinh nhận định
│   └── guards.py                  ★ BỘ CHẶN SỐ
│
├── frontend/                      # Next.js (cắt được nếu thiếu thời gian)
│
├── data/
│   ├── raw/                       # SEC EDGAR, Online Retail II
│   ├── synthetic/
│   │   ├── generate.py            ★ BỘ SINH DỮ LIỆU
│   │   └── labels.csv             ★ GROUND TRUTH cho F8
│   └── warehouse.duckdb
│
├── eval/                          ★ PHẦN NGHIÊN CỨU
│   ├── benchmark_fin.jsonl        # 250 câu — ĐÓNG BĂNG ở T6
│   ├── run_nl2sql.py
│   ├── run_forecast.py
│   ├── run_narrative.py
│   ├── ablations.py               # A / B / C / D
│   └── results/
│
└── docs/
    └── error_taxonomy.md          # phân loại lỗi thủ công
```

```

---

## 10. Limitations

1. **Không thay thế chuyên gia tài chính** — hệ thống chỉ hỗ trợ phân tích, không phải kết luận cuối cùng
2. **SEC EDGAR chỉ có báo cáo tổng hợp** — không có sổ cái chi tiết, không drill-down sâu vào từng giao dịch
3. **Online Retail II thời gian 2009–2011** — hơi cũ, cần kiểm tra relevance
4. **Dữ liệu tổng hợp thiếu realism** — seasonality phức tạp và noise thực có thể khác
5. **Không thực hiện causal inference** — chỉ contribution/decomposition, không kết luận nguyên nhân
6. **BookSQL câu hỏi tiếng Anh** — cần dịch và rà lại bởi người bản ngữ
7. **TSB-AD local chỉ có 870 chuỗi** — benchmark gốc có 1.070 chuỗi, cần chọn tập con phù hợp domain tài chính
8. **Không triển khai enterprise infrastructure** — không dùng Kubernetes, Kafka, Airflow trong MVP

---

## 11. Documentation

| Tài liệu | Mô tả |
|----------|-------|
| `README.md` | Tài liệu chính |
| `Dataset/Data/Báo cáo thu thập dữ liệu.md` | Chi tiết 5 nhóm dữ liệu |
| `Program/KẾ_HOẠCH.md` | Tiêu chí đánh giá dataset |
| `docs/architecture.md` | Kiến trúc hệ thống |
| `docs/methodology.md` | Phương pháp nghiên cứu |
| `docs/evaluation.md` | Chi tiết đánh giá |

---

## 12. Citation / License

### License

| Dataset | License |
|---------|---------|
| SEC EDGAR | Public domain (US Government) |
| BookSQL | CC-BY-NC-SA |
| Online Retail II | UCI (nghiên cứu/học tập) |
| Monash TSF | CC-BY 4.0 |
| TSB-AD | Apache 2.0 + per-dataset |
| Synthetic Data | Tự quyết định |

