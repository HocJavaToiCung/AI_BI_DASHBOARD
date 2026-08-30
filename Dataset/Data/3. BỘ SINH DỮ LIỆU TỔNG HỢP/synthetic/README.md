# BỘ SINH DỮ LIỆU TỔNG HỢP

Pipeline sinh sổ cái tài chính tổng hợp có chứa 4 loại bất thường có nhãn vàng, phục vụ đánh giá chức năng phát hiện bất thường (F8) và phân rã nguyên nhân (F9) của hệ thống AI BI Dashboard.

---

## 📑 Mục lục

- [1. Tổng quan](#1-tổng-quan)
- [2. Cấu trúc thư mục](#2-cấu-trúc-thư-mục)
- [3. Data Pipeline](#3-data-pipeline)
- [4. Output & Schema](#4-output--schema)
- [5. Configuration](#5-configuration)
- [6. Nguyên tắc thiết kế](#6-nguyên-tắc-thiết-kế)
- [7. Cách chạy](#7-cách-chạy)
- [8. Lưu ý khi sử dụng](#8-lưu-ý-khi-sử-dụng)
- [9. Thuật ngữ & ký hiệu](#9-thuật-ngữ--ký-hiệu)
- [10. Tham khảo](#10-tham-khảo)

---

## 1. Tổng quan

### Synthetic data là gì?

Dữ liệu tài chính được sinh ra bằng công thức toán học (trend × season × noise × factors), **không lấy từ thực tế**. Sau khi sinh, hệ thống chèn bất thường có kiểm soát vào dữ liệu.

### Dùng để làm gì?

| Mục đích | Lý do |
|----------|-------|
| Đánh giá F8 (phát hiện bất thường) | Có ground truth biết chính xác đâu là bất thường |
| Đánh giá F9 (phân rã nguyên nhân) | Tạo ca kiểm tra dimension-local: tổng bình thường nhưng 1 dimension sụt giảm |
| Benchmark F10 (dự báo) | Có chuỗi thời gian nền sạch, dài 2 năm |
| Training F6/F7 | Có schema ổn định, nhiều dimensions để drill-down |

### Liên quan F6–F11

| Chức năng | Vai trò |
|-----------|---------|
| F6 NL2SQL | Dùng schema ledger để tạo câu hỏi SQL |
| F7 Biểu đồ | Dữ liệu có region/product/channel → drill-down trực quan |
| F8 Bất thường | **Chính** — có ground truth tính precision/recall/F1 |
| F9 Phân rã | **Chính** — dimension-local anomaly kiểm tra khả năng phân rã |
| F10 Dự báo | Dùng `ledger_base.csv` làm chuỗi thời gian nền |
| F11 Diễn giải | Có metadata đầy đủ để giải thích anomaly |

---

## 2. Cấu trúc thư mục

```
synthetic/
├── config/
│   ├── base_trend.yaml           # tham số sinh dữ liệu nền
│   └── anomaly_scenarios.yaml    # kịch bản 4 loại bất thường
├── engine/
│   ├── generator.py              # sinh sổ cái sạch
│   ├── injector.py               # chèn anomaly có nhãn
│   └── labeler.py                # verify labels
├── output/
│   ├── ledger_base.csv           # sổ cái sạch (101,630 dòng)
│   ├── ledger_anomaly.csv        # sổ cái có anomaly (184 scenarios)
│   ├── labels.csv                # ground truth
│   └── labels_verified.csv       # labels đã kiểm tra (184/184 passed)
└── run.py                        # pipeline tự động
```

### Vai trò từng thư mục

| Thư mục | Vai trò |
|---------|---------|
| `config/` | Chứa tham số đầu vào. Đây là **source of truth**. Thay đổi config → thay đổi output. |
| `engine/` | Code xử lý: sinh data, inject anomaly, verify labels. |
| `output/` | Sản phẩm đầu ra của pipeline. |

---

## 3. Data Pipeline

### Flow

```
[base_trend.yaml] ──→ [generator.py] ──→ ledger_base.csv
                                              │
[anomaly_scenarios.yaml] ──→ [injector.py] ──→ ledger_anomaly.csv
                                              │
                                         labels.csv
                                              │
                                        [labeler.py]
                                              │
                                        labels_verified.csv
```

### 3 stage

| Stage | Input | Output | Mô tả |
|-------|-------|--------|-------|
| 1. Generate | `base_trend.yaml` | `ledger_base.csv` | Sinh sổ cái sạch theo trend × season × noise × factors |
| 2. Inject | `ledger_base.csv` + `anomaly_scenarios.yaml` | `ledger_anomaly.csv` + `labels.csv` | Chèn 4 loại anomaly có nhãn |
| 3. Verify | `labels.csv` | `labels_verified.csv` | Kiểm tra tính hợp lệ của labels |

---

## 4. Output & Schema

### 4.1 `ledger_base.csv`

**Dùng cho:** training normal, forecasting (F10), baseline.

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `transaction_id` | string | UUID rút gọn 8 ký tự |
| `date` | date | Ngày giao dịch (2023-01-01 → 2024-12-31) |
| `region` | string | North, Central, South, Highlands, Mekong, Urban |
| `product` | string | Software Dev, Cloud Services, Consulting, ... |
| `channel` | string | Online, Agency, Direct, Contract, Partner |
| `transaction_type` | string | Invoice, Payment, Credit Memo, Estimate, Sales Receipt |
| `amount` | float | Số tiền ≥ 100 |
| `cost` | float | Chi phí |
| `margin` | float | Lợi nhuận = amount - cost |
| `customer_id` | string | CUST-XXXX |
| `vendor_id` | string | VEND-XXXX |
| `description` | string | "{txn_type} - {product} - {region}" |

**Kích thước:** ~13 MB, 101,631 dòng (1 header + 101,630 data).

### 4.2 `ledger_anomaly.csv`

**Dùng cho:** đánh giá F8/F9. Có 2,764 dòng chứa tag `[ANOMALY: ...]`.

| Khác biệt | Giá trị |
|-----------|---------|
| Số dòng | 101,631 (giống `ledger_base.csv`) |
| Anomaly tags | Có 2,764 dòng được tag |
| Mục đích | Đánh giá phát hiện bất thường |

### 4.3 `labels.csv`

**Dùng cho:** ground truth đánh giá F8/F9.

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `scenario_id` | string | Định danh duy nhất, ví dụ: `A1_spike_1_1.5sigma_positive` |
| `anomaly_type` | enum | `spike`, `level_shift`, `trend_break`, `dimension_local` |
| `magnitude` | float | Độ lớn: σ cho spike, % cho các loại khác |
| `dimension` | string | Dimension bị ảnh hưởng, ví dụ: `region=North` |
| `date_start` | date | Ngày bắt đầu |
| `date_end` | date | Ngày kết thúc |
| `affected_rows` | int | Số dòng bị ảnh hưởng |
| `ground_truth_value` | float | Tổng amount của các dòng bị ảnh hưởng |
| `expected_detection` | enum | `TRUE` |

**Kích thước:** ~19 KB, 185 dòng (1 header + 184 scenarios).

### 4.4 `labels_verified.csv`

**Dùng cho:** kiểm tra chất lượng labels trước khi đánh giá.

| Cột bổ sung | Giá trị |
|-------------|---------|
| `verified` | `TRUE` nếu scenario hợp lệ (184/184 passed) |

---

## 5. Configuration

### 5.1 `base_trend.yaml`

Định nghĩa mô hình sinh dữ liệu nền.

| Section | Vai trò |
|---------|---------|
| `time` | start/end date, freq (D=ngày) |
| `dimensions` | regions (6), products (10), channels (5) |
| `base_values` | `revenue_base` (50,000), `cost_ratio` (0.65) |
| `trend` | Piecewise linear slopes |
| `season` | Fourier series + holiday effects |
| `noise` | Gaussian N(0, 0.08²) |
| `factors` | Hệ số nhân theo region/product/channel |
| `transactions_per_day` | Số giao dịch/ngày: [80, 200] |

### 5.2 `anomaly_scenarios.yaml`

Định nghĩa 4 loại anomaly.

| Section | Vai trò |
|---------|---------|
| `scenarios.spike_dip` | magnitudes, duration_days, directions |
| `scenarios.level_shift` | magnitudes, start_dates |
| `scenarios.trend_break` | break_dates, new_slopes |
| `scenarios.dimension_local` | magnitudes, compensation |
| `global_settings` | ràng buộc: min/max_affected_rows, ensure_detectable |

---

## 6. Nguyên tắc thiết kế

### Minimal

Chỉ sinh đủ cho R&D: 2 năm, ~100k dòng. 4 loại anomaly cốt lõi, không thêm loại phức tạp chưa cần thiết.

### Reproducible

Cùng config + cùng seed → cùng output.

- Seed cố định (`seed: 42`) trong YAML.
- Mọi tham số đều trong YAML, không hardcode trong Python.
- Có thể tái tạo y hệt kết quả để kiểm chnh, debug, so sánh mô hình công bằng.

### Versioning

Config là source of truth. Khi cần thử nghiệm tham số mới:

1. Copy `config/` → `config_v002/`
2. Sửa file trong `config_v002/`
3. Chạy pipeline với config mới
4. Output lưu vào `output_v002/`

### Raw data isolation

Synthetic data hoàn toàn tách khỏi raw SEC EDGAR, BookSQL. Không import raw, không ghi đè.

### Metadata

- Seed cố định trong config.
- `labels.csv` đủ thông tin để reconstruction anomaly.
- Mỗi file output có thể kèm `generated_at`, `seed`, `params`.

### Validation

- `labels_verified.csv` đảm bảo 100% scenarios hợp lệ.
- Pipeline chỉ tạo label nếu `affected_rows > 0`.
- Có thể thêm visual inspection bằng matplotlib.

---

## 7. Cách chạy

### Yêu cầu

```bash
pip install numpy pyyaml
```

### Full pipeline

```bash
python run.py
```

### Individual stages

```bash
# Stage 1: Generate base ledger
python -c "from engine.generator import generate; generate('config/base_trend.yaml', 'output/ledger_base.csv')"

# Stage 2: Inject anomalies
python -c "from engine.injector import inject; inject('config/anomaly_scenarios.yaml', 'output/ledger_base.csv', 'output/ledger_anomaly.csv', seed=42)"

# Stage 3: Verify labels
python -c "from engine.labeler import verify_labels; verify_labels('output/labels.csv', 'output/labels_verified.csv')"
```

### Tùy chỉnh

- Sửa `config/base_trend.yaml` để đổi số năm, dimensions, trend, season.
- Sửa `config/anomaly_scenarios.yaml` để thêm/bớt loại anomaly, magnitudes, dates.
- Đổi `seed` trong `run.py` để sinh bộ dữ liệu mới.

---

## 8. Lưu ý khi sử dụng

1. **Không dùng `ledger_anomaly.csv` làm input cho mô hình dự báo** — đã bị phá bởi anomaly. Dùng `ledger_base.csv` cho F10.
2. **`labels.csv` chỉ dùng cho đánh giá F8/F9**, không dùng cho training.
3. **Khi chạy lại pipeline**, file output cũ sẽ bị ghi đè. Copy sang thư mục khác nếu cần giữ lại.
4. **Mỗi lần đổi config**, nên tăng version hoặc đổi tên thư mục output để tránh nhầm lẫn.
5. **Kiểm tra `labels_verified.csv`** trước khi dùng. Nếu `verified = FALSE` cho bất kỳ scenario nào, cần kiểm tra lại config.

---

## 9. Thuật ngữ & ký hiệu

| Viết tắt | Nghĩa đầy đủ | Giải thích |
|----------|-------------|------------|
| F8 | Function 8 — Phát hiện bất thường | Chức năng phát hiện điểm/chu kỳ bất thường trong dữ liệu tài chính |
| F9 | Function 9 — Phân rã nguyên nhân | Chức năng xác định dimension nào gây ra bất thường |
| RQ | Research Question — Câu hỏi nghiên cứu | RQ1: NL2SQL, RQ2: đa ngữ, RQ3: dự báo |
| YAML | YAML Ain't Markup Language | Định dạng file cấu hình |
| CSV | Comma-Separated Values | Định dạng bảng dữ liệu phân cách bằng dấu phẩy |
| σ | Sigma — Độ lệch chuẩn | Đơn vị đo biên độ anomaly trong spike/dip |
| U(...) | Uniform distribution | Phân phối đều trong khoảng giá trị |
| N(μ, σ²) | Normal distribution | Phân phối chuẩn với mean μ và variance σ² |
| seed | Hạt giống ngẫu nhiên | Giá trị cố định để tái tạo kết quả ngẫu nhiên |
| dimension | Chiều phân rã | Trong ngữ cảnh này: region, product, channel |
| ground truth | Sự thật cơ sở | Nhãn đúng, dùng để đánh giá mô hình |
| pipeline | Dây chuyền xử lý | Chuỗi các bước: generate → inject → verify |
| trend | Xu hướng | Thay đổi dài hạn của chuỗi thời gian |
| season | Mùa vụ | Chu kỳ lặp lại định kỳ |
| noise | Nhiễu | Biến động ngẫu nhiên quanh giá trị trung bình |
| Fourier series | Chuỗi Fourier | Phương pháp biểu diễn hàm tuần hoàn dạng sin/cos |

---

## 10. Tham khảo

- Tài liệu đề tài: `dataset-ai-bi-dashboard.md` (mục 3)
- Công trình liên quan:
  - Marco Schreyer et al., "Deep Autoencoder for Anomaly Detection in Accounting Data", arXiv:1709.05254
  - https://github.com/GitiHubi/deepPaper — tuyển tập công trình audit analytics
- Benchmark anomaly detection:
  - TSB-AD: https://github.com/TheDatumOrg/TSB-AD
