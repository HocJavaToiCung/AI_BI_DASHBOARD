# BÁO CÁO THU THẬP DỮ LIỆU

> **Đề tài:** AI Business Intelligence Dashboard — Tài chính doanh nghiệp  
> **Người thực hiện:** khang250526  
> **Ngày cập nhật:** 30/08/2026  
> **Nguồn tham khảo:** `dataset-ai-bi-dashboard.md`

---

## 1. TỔNG QUAN

Thư mục `D:\PYTHON\Dataset\Data\` chứa **5 nhóm dữ liệu** phục vụ 3 câu hỏi nghiên cứu (RQ1: NL2SQL, RQ2: đa ngữ, RQ3: dự báo) và 6 chức năng hệ thống (F6–F11).

| # | Nhóm dữ liệu | Vị trí | Tình trạng |
|---|-------------|--------|-----------|
| 1 | Text-to-SQL | `1. TEXT-TO-SQL/` | Đã có BookSQL + Spider 2.0-Lite |
| 2 | Tài chính doanh nghiệp | `2. DỮ LIỆU TÀI CHÍNH DOANH NGHIỆP/` | Đã có SEC EDGAR + Online Retail II |
| 3 | Tổng hợp tự sinh | `3. BỘ SINH DỮ LIỆU TỔNG HỢP/` | Đã có pipeline + output |
| 4 | Dự báo chuỗi thời gian | `4. DỰ BÁO CHUỖI THỜI GIAN/` | Đã có 4 bộ Monash/M4/Tourism |
| 5 | Phát hiện bất thường | `5. PHÁT HIỆN BẤT THƯỜNG/` | Đã có TSB-AD-U (870 chuỗi) |

---

## 2. CHI TIẾT TỪNG NHÓM DỮ LIỆU

### 2.1. TEXT-TO-SQL / HỎI ĐÁP NGÔN NGỮ TỰ NHIÊN (cho RQ1)

#### 2.1.1. BookSQL — *ưu tiên số một*

| Thuộc tính | Chi tiết |
|---|---|
| **Nội dung** | 100.000 cặp (câu hỏi tiếng Anh → SQL), CSDL kế toán ~1 triệu bản ghi |
| **Phạm vi** | 27 doanh nghiệp × ~35.000–40.000 giao dịch, nhiều ngành: xây dựng, y tế, bán lẻ, bảo hiểm |
| **Schema** | Theo chart of accounts thật — hóa đơn, thanh toán, công nợ, bút toán |
| **Giấy phép** | **CC-BY-NC-SA** — phi thương mại |
| **Tải** | https://github.com/Exploration-Lab/BookSQL/tree/main/DATA |
| **Bài báo** | NAACL 2024 · https://aclanthology.org/2024.naacl-long.28/ · arXiv:2406.07860 |

**Dữ liệu có sẵn tại:** `D:\PYTHON\Dataset\Data\1. TEXT-TO-SQL\BookSQL\`

**Cấu trúc thư mục:**

```
BookSQL/
├── accounting tables/
│   ├── chart_of_account_OB.csv
│   ├── customer_table.csv
│   ├── employee_table.csv
│   ├── Master_txn_table_1.csv
│   ├── Master_txn_table_2.csv
│   ├── payment_method.csv
│   ├── product_service_table.csv
│   ├── ReadME.txt
│   └── vendor_table.csv
└── BookSQL/
    ├── README.md
    ├── test.json
    ├── train.json
    └── val.json
```

**Schema dữ liệu (7 bảng):**

| Bảng | Mô tả |
|------|-------|
| `master_txn_table` | Bảng chính chứa toàn bộ giao dịch |
| `chart_of_accounts` | Tên tài khoản và loại tài khoản |
| `products_service` | Sản phẩm/dịch vụ và loại |
| `customers` | Thông tin khách hàng |
| `vendors` | Thông tin nhà cung cấp |
| `payment_method` | Phương thức thanh toán |
| `employees` | Thông tin nhân viên |

**JSON files:**

| File | Số mẫu | Kích thước |
|------|--------|-----------|
| `train.json` | 70.828 | ~26,8 MB |
| `val.json` | 7.605 | ~3,1 MB |
| `test.json` | 21.567 | ~2,9 MB |

**Định dạng mẫu:**
```json
{
    "Query": "What was the first invoice for Matthew James?",
    "SQL": "select transaction_id from master_txn_table where customers = \"Matthew James\" and transaction_type = 'invoice' order by transaction_date limit 1",
    "Levels": "medium",
    "split": "test"
}
```

#### 2.1.2. Spider 2.0-Snow — *đối chứng ngoài miền*

| Thuộc tính | Chi tiết |
|---|---|
| **Nội dung** | Workflow text-to-SQL doanh nghiệp thật, schema hàng nghìn cột, nhiều dialect (BigQuery, Snowflake, DuckDB) |
| **Vì sao dùng** | Có leaderboard công khai → đặt kết quả của bạn vào bối cảnh so sánh được |
| **Tải** | https://huggingface.co/datasets/xlangai/spider2-lite · https://spider2-sql.github.io/ |

**Dữ liệu có sẵn tại:** `D:\PYTHON\Dataset\Data\1. TEXT-TO-SQL\Spider 2.0-Snow\spider2-snow.jsonl` (~245 KB)

**Dùng thế nào:** chỉ chạy **một tập con** (~50–100 câu) để tham chiếu. Đừng dồn công sức vào đây — Spider 2.0 rất khó và không thuộc miền tài chính.

---

### 2.2. DỮ LIỆU TÀI CHÍNH DOANH NGHIỆP (warehouse + chỉ số)

#### 2.2.1. SEC EDGAR Financial Statement Data Sets — *nguồn dữ liệu thật chính*

| Thuộc tính | Chi tiết |
|---|---|
| **Nội dung** | Số liệu từ mặt báo cáo tài chính của **toàn bộ** công ty niêm yết Mỹ, trích từ XBRL, đã làm phẳng |
| **Thời gian** | **Q1/2009 → Q2/2026**, cập nhật hàng quý |
| **Cấu trúc** | Mỗi quý là 1 file zip gồm `sub.txt` (thông tin hồ sơ nộp), `num.txt` (số liệu — nay có thêm trường `segments`), `pre.txt`, `tag.txt` |
| **Giấy phép** | Dữ liệu chính phủ Mỹ, **miễn phí, không hạn chế sử dụng** |
| **Tải** | https://www.sec.gov/data-research/sec-markets-data/financial-statement-data-sets |
| **Tài liệu** | https://www.sec.gov/files/aqfs.pdf |

**Dữ liệu có sẵn tại:** `D:\PYTHON\Dataset\Data\2. DỮ LIỆU TÀI CHÍNH DOANH NGHIỆP\`

**Danh sách file đã tải:**

| Quý | File | Kích thước |
|-----|------|-----------|
| 2020 Q1 | `2020q1.7z` | ~45,7 MB |
| 2020 Q2 | `2020q2.7z` | ~41,0 MB |
| 2020 Q3 | `2020q3.7z` | ~42,1 MB |
| 2020 Q4 | `2020q4.7z` | ~43,3 MB |
| 2021 Q1 | `2021q1.7z` | ~46,6 MB |
| 2021 Q2 | `2021q2.7z` | ~45,8 MB |
| 2021 Q3 | `2021q3.7z` | ~47,0 MB |
| 2021 Q4 | `2021q4.7z` | ~49,9 MB |
| 2022 Q1 | `2022q1.7z` | ~50,2 MB |
| 2022 Q2 | `2022q2.7z` | ~47,4 MB |
| 2022 Q3 | `2022q3.7z` | ~47,7 MB |
| 2022 Q4 | `2022q4.7z` | ~55,4 MB |
| 2023 Q1 | `2023q1.7z` | ~55,9 MB |
| 2023 Q2 | `2023q2.7z` | ~56,3 MB |
| 2023 Q3 | `2023q3.7z` | ~56,7 MB |
| 2023 Q4 | `2023q4.7z` | ~58,3 MB |
| 2024 Q1 | `2024q1.7z` | ~58,1 MB |
| 2024 Q2 | `2024q2.7z` | ~57,0 MB |
| 2024 Q3 | `2024q3.7z` | ~56,5 MB |
| 2024 Q4 | `2024q4.7z` | ~59,1 MB |
| 2025 Q1 | `2025q1.7z` | ~60,6 MB |
| 2025 Q2 | `2025q2.7z` | ~41,8 MB |
| 2025 Q3 | `2025q3.7z` | ~60,5 MB |
| 2025 Q4 | `2025q4.7z` | ~37,2 MB |
| 2026 Q1 | `2026q1.7z` | ~47,3 MB |
| 2026 Q2 | `2026q2.7z` | ~34,9 MB |

Tổng cộng: **26 quý** (2020–2026).

**Kỹ thuật tải:** SEC yêu cầu header `User-Agent` có tên và email, giới hạn tối đa 10 request/giây. Không có header sẽ bị chặn:

```python
import requests, zipfile, io, pathlib

HEADERS = {"User-Agent": "Nguyen Ngoc toitenngoc108@gmail.com"}
OUT = pathlib.Path("data/raw/edgar"); OUT.mkdir(parents=True, exist_ok=True)

for year in range(2020, 2027):
    for q in range(1, 5):
        url = f"https://www.sec.gov/files/dera/data/financial-statement-data-sets/{year}q{q}.zip"
        r = requests.get(url, headers=HEADERS, timeout=60)
        if r.status_code != 200:
            print(f"bỏ qua {year}q{q}: {r.status_code}"); continue
        zipfile.ZipFile(io.BytesIO(r.content)).extractall(OUT / f"{year}q{q}")
        print(f"xong {year}q{q}")
```

#### 2.2.2. Online Retail II (UCI) — *drill-down thật*

| Thuộc tính | Chi tiết |
|---|---|
| **Nội dung** | ~1 triệu giao dịch, 2009–2011, có mã sản phẩm, quốc gia, khách hàng, giá, số lượng |
| **Giấy phép** | UCI, dùng cho nghiên cứu |
| **Tải** | https://archive.ics.uci.edu/dataset/502/online+retail+ii |

**Dữ liệu có sẵn tại:** `D:\PYTHON\Dataset\Data\2. DỮ LIỆU TÀI CHÍNH DOANH NGHIỆP\online+retail+ii\online_retail_II.xlsx` (~45,6 MB)

**Schema:**
- `Invoice`: Mã hóa đơn
- `StockCode`: Mã sản phẩm
- `Description`: Mô tả sản phẩm
- `Quantity`: Số lượng
- `InvoiceDate`: Ngày hóa đơn
- `Price`: Đơn giá
- `Customer ID`: Mã khách hàng
- `Country`: Quốc gia

---

### 2.3. BỘ SINH DỮ LIỆU TỔNG HỢP (tự viết — bắt buộc)

**Đây là hạ tầng nghiên cứu quan trọng nhất mà bạn phải tự làm, và không nguồn công khai nào thay thế được.**

**Lý do:** để đánh giá F8 (phát hiện bất thường) và F9 (phân rã nguyên nhân), bạn cần biết **chắc chắn** đâu là bất thường. Dữ liệu thật không có nhãn đó.

**Dữ liệu có sẵn tại:** `D:\PYTHON\Dataset\Data\3. BỘ SINH DỮ LIỆU TỔNG HỢP\synthetic\`

#### Cấu trúc thư mục

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
├── run.py                        # pipeline tự động
└── README.md                     # hướng dẫn sử dụng
```

#### Output & Schema

##### ledger_base.csv
- **Dùng cho:** training normal, forecasting (F10), baseline.
- **Kích thước:** ~13 MB, 101,631 dòng (1 header + 101,630 data).
- **Thời gian:** 2023-01-01 → 2024-12-31

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `transaction_id` | string | UUID rút gọn 8 ký tự |
| `date` | date | Ngày giao dịch |
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

##### labels.csv
- **Dùng cho:** ground truth đánh giá F8/F9.
- **Kích thước:** ~19 KB, 185 dòng (1 header + 184 scenarios).

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

##### 4 loại bất thường

| Loại | Mô tả | Mục đích |
|------|-------|----------|
| `spike/dip` | Một kỳ lệch k×sigma | Kiểm tra nhạy phát hiện điểm |
| `level_shift` | Dịch mức từ kỳ t trở đi | Kiểm tra nhạy phát hiện chuyển mức |
| `trend_break` | Đổi độ dốc | Kiểm tra nhạy phát hiện đổi xu hướng |
| `dimension_local` | Chỉ 1 khu vực bất thường, tổng thể vẫn bình thường | **Quan trọng nhất** — kiểm tra F9 |

---

### 2.4. DỰ BÁO CHUỖI THỜI GIAN (cho RQ3)

#### 2.4.1. Monash Time Series Forecasting Archive

| Thuộc tính | Chi tiết |
|---|---|
| **Nội dung** | Hơn 30 bộ dữ liệu chuỗi thời gian, nhiều miền, định dạng thống nhất `.tsf` |
| **Vì sao dùng** | Có **kết quả baseline đã công bố** của nhiều mô hình |
| **Link** | https://forecastingdata.org/ · https://zenodo.org/records/3898380 · arXiv:2105.06643 |

**Dữ liệu có sẵn tại:** `D:\PYTHON\Dataset\Data\4. DỰ BÁO CHUỖI THỜI GIAN\`

| Bộ dữ liệu | Định dạng | Tần suất | Mô tả |
|-----------|-----------|----------|-------|
| `hospital_dataset/` | `.tsf` | Tháng | 767 chuỗi đếm bệnh nhân, 2000–2006 (84 tháng) |
| `m4_monthly_dataset/` | `.tsf` | Tháng | Phần của M4 Monthly |
| `m4_quarterly_dataset/` | `.tsf` | Quý | Phần của M4 Quarterly |
| `tourism_quarterly_dataset/` | `.tsf` | Quý | Dữ liệu du lịch theo quý |

**Tham chiếu bộ Hospital:**
- Hyndman, R. J., 2015. *expsmooth: Data Sets from Forecasting with Exponential Smoothing*. R package version 2.3. https://CRAN.R-project.org/package=expsmooth

---

### 2.5. PHÁT HIỆN BẤT THƯỜNG (đối chứng cho F8)

#### 2.5.1. TSB-AD — *dùng cái này, đừng dùng NAB/Yahoo S5*

| Thuộc tính | Chi tiết |
|---|---|
| **Nội dung** | **1.070 chuỗi thời gian từ 40 bộ dữ liệu**, chia TSB-AD-U (đơn biến) và TSB-AD-M (đa biến) |
| **Kèm theo** | 40 thuật toán phát hiện đã cài sẵn (thống kê, mạng nơ-ron, mô hình nền tảng) |
| **Giấy phép** | Apache 2.0 cho phần tiền xử lý; giấy phép gốc theo từng dataset thành phần |
| **Link** | https://github.com/TheDatumOrg/TSB-AD |

**Dữ liệu có sẵn tại:** `D:\PYTHON\Dataset\Data\5. PHÁT HIỆN BẤT THƯỜNG\TSB-AD-U\`

Tổng cộng: **870 file CSV**, bao gồm các bộ:
- NAB (28 file)
- WSD (128 file)
- MSL (8 file)
- Stock (20 file)
- Daphnet (1 file)
- MITDB (8 file)
- SMD (38 file)
- LTDB (9 file)
- MGAB (9 file)
- SED (3 file)
- SVDB (20 file)
- TAO (3 file)
- IOPS (17 file)
- NEK (9 file)
- CATSv2 (1 file)
- TODS (15 file)
- Power (1 file)
- UCR (210 file)
- SMAP (19 file)
- SWaT (1 file)
- YAHOO (200 file)
- Exathlon (32 file)
- OPPORTUNITY (29 file)

---

## 3. THỨ TỰ THỰC HIỆN ĐỀ XUẤT

| Tuần | Việc | Kết quả |
|------|------|---------|
| 1 | Tải BookSQL, khảo sát schema, chạy một truy vấn mẫu | Biết chính xác mình đang làm việc với dữ liệu gì |
| 1 | Tải SEC EDGAR 2020–2026, nạp vào DuckDB | Warehouse chạy được |
| 2 | Viết bộ sinh dữ liệu tổng hợp + chèn 4 loại bất thường | `labels.csv` — ground truth cho F8/F9 |
| 3 | Ánh xạ schema BookSQL sang `metrics.yml` | Điều kiện cần để chạy ablation |
| 5–6 | Dịch ~80 câu BookSQL sang tiếng Việt, người bản ngữ rà lại | Tập đánh giá tiếng Việt |
| 11 | Tải tập con Monash (quarterly/monthly), chạy baseline | Số liệu cho RQ3 |
| 12 | TSB-AD tập con — đối chứng anomaly | Số liệu cho F8 |

---

## 4. TÓM TẮT GIẤY PHÉP

| Dataset | Giấy phép | Thương mại? | Phân phối lại? |
|---------|-----------|:-----------:|:--------------:|
| BookSQL | CC-BY-NC-SA | ❌ | ✓ (cùng giấy phép) |
| SEC EDGAR | Public domain (chính phủ Mỹ) | ✓ | ✓ |
| Online Retail II | UCI, dùng cho nghiên cứu | ✓ | ✓ (ghi nguồn) |
| Monash TSF | CC-BY 4.0 (theo từng bộ) | ✓ | ✓ (ghi nguồn) |
| TSB-AD | Apache 2.0 + giấy phép gốc từng bộ | ⚠️ kiểm tra từng bộ | ⚠️ |
| Dữ liệu tự sinh | Bạn tự quyết định | ✓ | ✓ |

> Nếu định phát hành bộ đánh giá của mình như một đóng góp công khai, **chỉ đưa vào phần dữ liệu tự sinh và phần dựa trên SEC EDGAR**. Hai nguồn này không vướng ràng buộc nào.

---

## 5. LIÊN KẾT NGUỒN THAM KHẢO

| Nguồn | Link |
|--------|------|
| **BookSQL (GitHub)** | https://github.com/Exploration-Lab/BookSQL/tree/main/DATA |
| **BookSQL (NAACL 2024)** | https://aclanthology.org/2024.naacl-long.28/ |
| **BookSQL (arXiv)** | https://arxiv.org/abs/2406.07860 |
| **SEC EDGAR** | https://www.sec.gov/data-research/sec-markets-data/financial-statement-data-sets |
| **SEC EDGAR Docs** | https://www.sec.gov/files/aqfs.pdf |
| **Online Retail II (UCI)** | https://archive.ics.uci.edu/dataset/502/online+retail+ii |
| **Monash TSF Archive** | https://forecastingdata.org/ |
| **Monash TSF (Zenodo)** | https://zenodo.org/records/3898380 |
| **Monash TSF (arXiv)** | https://arxiv.org/abs/2105.06643 |
| **TSB-AD** | https://github.com/TheDatumOrg/TSB-AD |
| **Spider 2.0-lite** | https://huggingface.co/datasets/xlangai/spider2-lite |

---

## 6. LƯU Ý KHI SỬ DỤNG

1. **BookSQL:** Câu hỏi bằng tiếng Anh. Nếu muốn khẳng định hệ thống chạy tiếng Việt, phải dịch một tập con và cho người bản ngữ rà lại.
2. **SEC EDGAR:** Chỉ có báo cáo tổng hợp, không có sổ cái chi tiết. Không có chiều "khu vực", "sản phẩm", "khách hàng" → không drill-down sâu được.
3. **Online Retail II:** Dùng cho drill-down thật với chiều sản phẩm/quốc gia/khách hàng.
4. **TSB-AD:** Không cần chạy hết 1.070 chuỗi. Lấy tập con tần suất thấp, có mùa vụ (giống dữ liệu tài chính).
5. **Synthetic data:** Mỗi lần đổi config, nên tăng version hoặc đổi tên thư mục output để tránh nhầm lẫn.
6. **Spider 2.0-Lite:** Chỉ dùng làm đối chứng bên ngoài miền, không phải trọng tâm nghiên cứu.
