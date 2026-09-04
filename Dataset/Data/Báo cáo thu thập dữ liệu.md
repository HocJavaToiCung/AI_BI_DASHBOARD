# BÁO CÁO THU THẬP DỮ LIỆU

> **Đề tài:** AI Business Intelligence Dashboard — Tài chính doanh nghiệp  
> **Người thực hiện:** uyennhi 
> **Ngày cập nhật:** 30/08/2026  
> **Nguồn tham khảo:** `dataset-ai-bi-dashboard.md`

---

## 1. TỔNG QUAN

Thư mục `D:\PYTHON\Dataset\Data\` chứa **5 nhóm dữ liệu** phục vụ 3 câu hỏi nghiên cứu (RQ1: NL2SQL, RQ2: đa ngữ, RQ3: dự báo) và 6 chức năng hệ thống (F6–F11).

| # | Nhóm dữ liệu | Vị trí | Tình trạng |
|---|-------------|--------|-----------|
| 1 | Text-to-SQL | `1. TEXT-TO-SQL/` | Đã có BookSQL + Spider 2.0-Snow |
| 2 | Tài chính doanh nghiệp | `2. DỮ LIỆU TÀI CHÍNH DOANH NGHIỆP/` | Đã có SEC EDGAR + Online Retail II |
| 3 | Tổng hợp tự sinh | `3. BỘ SINH DỮ LIỆU TỔNG HỢP/` | Đã có pipeline + output |
| 4 | Dự báo chuỗi thời gian | `4. DỰ BÁO CHUỖI THỜI GIAN/` | Đã có 4 bộ Monash/M4/Tourism |
| 5 | Phát hiện bất thường | `5. PHÁT HIỆN BẤT THƯỜNG/` | Đã có TSB-AD-U (870 chuỗi) |

---

## 2. CHI TIẾT TỪNG NHÓM DỮ LIỆU

### 2.1. TEXT-TO-SQL / HỎI ĐÁP NGÔN NGỮ TỰ NHIÊN (cho RQ1)

#### 2.1.1. BookSQL 

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

**Tại sao cần:** BookSQL là dataset text-to-SQL chính cho RQ1. Nó cung cấp 100.000 cặp câu hỏi–SQL **đúng miền kế toán** (invoice, payment, chart of accounts), đủ để train và đánh giá mô hình NL2SQL mà không cần tự viết hàng nghìn câu bằng tay.

**Lý do lấy:** 
- Schema dựa trên chart of accounts thật → khớp trực tiếp với báo cáo tài chính doanh nghiệp.
- Có sẵn SQL vàng (gold SQL) → có thể đánh giá execution accuracy khách quan.
- 27 doanh nghiệp, nhiều ngành → đa dạng biểu thức kế toán, tránh overfit vào một ngành.

**Review sơ bộ:**
- **Hoàn thiện:** CSV sạch, JSON có cấu trúc rõ ràng, đủ train/val/test.
- **Chất lượng:** Dữ liệu đã được làm sạch, schema nhất quán, không có missing value nghiêm trọng.
- **Vấn đề tiềm ẩn:** 
  - Câu hỏi bằng tiếng Anh, cần dịch sang tiếng Việt cho đánh giá. Một số câu hỏi có độ phức tạp cao (level hard) có thể cần hiểu biết sâu về kế toán.
  - **Phương pháp:** BookSQL chủ yếu có câu hỏi tiếng Anh. Việc đánh giá năng lực tiếng Việt không được suy ra trực tiếp từ kết quả trên BookSQL tiếng Anh; cần xây dựng một tập Vietnamese evaluation subset được dịch và human-reviewed. Không dùng bản dịch tự động chưa kiểm duyệt làm gold evaluation.
- **Độ sẵn sàng:** Sẵn sàng cho train/eval sau khi ánh xạ schema sang `metrics.yml`.

#### 2.1.2. Spider 2.0-Snow

| Thuộc tính | Chi tiết |
|---|---|
| **Nội dung** | Workflow text-to-SQL doanh nghiệp thật, schema phức tạp, tập trung vào Snowflake SQL dialect |
| **Vì sao dùng** | Có leaderboard công khai → đặt kết quả của bạn vào bối cảnh so sánh được |
| **Tải** | https://huggingface.co/datasets/xlangai/spider2-lite · https://spider2-sql.github.io/ |

**Dữ liệu có sẵn tại:** `D:\PYTHON\Dataset\Data\1. TEXT-TO-SQL\Spider 2.0-Snow\spider2-snow.jsonl` (~245 KB)

**Ghi chú:** File local có tên `spider2-snow.jsonl`, có vẻ là tập trung vào dialect Snowflake. Link tải gốc từ HuggingFace là `spider2-lite`, có thể chứa nhiều variant. Cần xác nhận lại variant chính xác của file local trước khi sử dụng.

**Dùng thế nào:** chỉ chạy **một tập con** (~50–100 câu) để tham chiếu. Đừng dồn công sức vào đây — Spider 2.0 rất khó và không thuộc miền tài chính.

**Tại sao cần:** Spider 2.0 cung cấp leaderboard công khai cho text-to-SQL doanh nghiệp thật. Dùng nó để đặt kết quả của hệ thống vào bối cảnh so sánh được với các phương pháp state-of-the-art.

**Lý do lấy:** 
- Schema phức tạp, hàng nghìn cột → kiểm tra khả năng generalize của mô hình ra ngoài miền kế toán.
- Tập trung vào Snowflake SQL dialect → đánh giá độ robust với một dialect cụ thể.
- Chỉ cần tập con ~50–100 câu vì không phải trọng tâm, chỉ cần baseline tham chiếu.

**Review sơ bộ:**
- **Hoàn thiện:** File JSONL ~245 KB, đủ cho tập con tham chiếu.
- **Chất lượng:** Schema phức tạp, đa dialect, leaderboard công khai → đánh giá khách quan được.
- **Vấn đề tiềm ẩn:** Rất khó, không thuộc miền tài chính → chỉ dùng làm baseline tham chiếu, không làm kết quả chính.
- **Độ sẵn sàng:** Sẵn sàng sau khi chọn tập con ~50–100 câu phù hợp.

---

### 2.2. DỮ LIỆU TÀI CHÍNH DOANH NGHIỆP (warehouse + chỉ số)

#### 2.2.1. SEC EDGAR Financial Statement Data Sets 

| Thuộc tính | Chi tiết |
|---|---|
| **Nội dung** | Số liệu được trích xuất từ các báo cáo tài chính doanh nghiệp nộp cho SEC bằng XBRL, bao phủ các registrant có dữ liệu phù hợp trong SEC Financial Statement Data Sets |
| **Thời gian** | Nguồn công khai có từ **Q1/2009 → Q2/2026**. Phạm vi đã tải và xử lý trong đề tài: **2020 Q1 → 2026 Q2**, tổng cộng **26 quý** |
| **Cấu trúc** | Mỗi quý là 1 file zip gồm `sub.txt` (thông tin hồ sơ nộp), `num.txt` (số liệu — phiên bản gần đây có thêm trường `segments`), `pre.txt`, `tag.txt` |
| **Giấy phép** | Dữ liệu công khai từ SEC; khi sử dụng hoặc phân phối lại dữ liệu/phiên bản đã xử lý cần tuân thủ điều kiện sử dụng và attribution hiện hành của SEC |
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

**Ví dụ cấu trúc giải nén:** Sau khi giải nén `2022q1.7z` (~50,2 MB), thu được thư mục `2022q1/` với các file:

| File | Kích thước nén | Kích thước giải nén | Số dòng | Công dụng |
|------|---------------|---------------------|---------|-----------|
| `num.txt` | ~50 MB | ~413 MB | 3.264.633 | **Số liệu tài chính** (financial data) |
| `pre.txt` | ~22 MB | ~98 MB | 832.868 | **Presentation/link** (liên kết giữa báo cáo và số liệu) |
| `tag.txt` | ~22 MB | ~21,5 MB | 105.254 | **Tag dictionary** (định nghĩa các tag XBRL) |
| `sub.txt` | ~2,1 MB | ~2,1 MB | 7.238 | **Submission metadata** (thông tin công ty) |
| `readme.htm` | - | ~151 KB | - | **Documentation** (hướng dẫn định dạng) |

**Chi tiết từng file:**

##### `sub.txt` — Submission Metadata
**Công dụng:** Thông tin về công ty và báo cáo tài chính đã nộp.

| Cột | Ví dụ | Mô tả |
|-----|-------|-------|
| `adsh` | `0000002178-22-000033` | Accession number (ID duy nhất của filing) |
| `cik` | `2178` | CIK của công ty |
| `name` | `ADAMS RESOURCES & ENERGY, INC.` | Tên công ty |
| `sic` | `5172` | Mã SIC (ngành) |
| `countryba` | `US` | Quốc gia trụ sở |
| `stprba` | `TX` | Bang |
| `cityba` | `HOUSTON` | Thành phố |
| `fy` | `2021` | Năm tài chính |
| `fp` | `FY` | Fiscal period |
| `filed` | `20220309` | Ngày nộp |
| `form` | `10-K` | Loại báo cáo |
| `period` | `20211231` | Ngày kết thúc kỳ |

##### `num.txt` — Financial Data (quan trọng nhất)
**Công dụng:** Tất cả số liệu tài chính numeric, đây là file lớn nhất và quan trọng nhất cho warehouse.

| Cột | Ví dụ | Mô tả |
|-----|-------|-------|
| `adsh` | `0001126975-22-000070` | Accession number |
| `tag` | `Revenues` | Tên chỉ số tài chính (XBRL tag) |
| `version` | `us-gaap/2021` | Taxonomy version |
| `ddate` | `20211231` | Ngày số liệu (thường là period end date) |
| `qtrs` | `4` | Số quý dữ liệu (0 = điểm, 4 = cả năm) |
| `uom` | `USD` | Đơn vị |
| `segments` | `BusinessSegments=GlobalServices` | Thông tin segment |
| `coreg` | | Entity nếu consolidated |
| `value` | `248000000.0000` | **Giá trị số** |
| `footnote` | | Chú thích |

##### `pre.txt` — Presentation
**Công dụng:** Liên kết giữa financial statements (BS/IS/CF) và các số liệu trong `num.txt`.

| Cột | Ví dụ | Mô tả |
|-----|-------|-------|
| `adsh` | | Accession number |
| `report` | `3` | Report number |
| `line` | `5` | Line number trong statement |
| `stmt` | `BS` | Statement type: BS/IS/CF/SE/CI |
| `inpth` | `0` | Depth |
| `rfile` | `H` | Report file type |
| `tag` | `AccountsReceivableNetCurrent` | Tag |
| `plabel` | `Accounts receivable, net...` | Label |
| `negating` | `0` | Có phải số âm không |

##### `tag.txt` — Tag Dictionary
**Công dụng:** Định nghĩa các tag XBRL chuẩn.

| Cột | Ví dụ | Mô tả |
|-----|-------|-------|
| `tag` | `NetIncomeLoss` | Tên tag |
| `version` | `us-gaap/2020` | Taxonomy version |
| `custom` | `0` | 0 = standard, 1 = custom |
| `abstract` | `0` | Có phải node trừu tượng không |
| `datatype` | `monetary` | Kiểu dữ liệu |
| `iord` | `D` | D = debit, C = credit |
| `crdr` | `C` | C = credit |
| `tlabel` | `Net Income (Loss)...` | Label chuẩn |
| `doc` | | Mô tả chi tiết |

**Lưu ý về phạm vi:** Nguồn SEC EDGAR có dữ liệu từ Q1/2009, nhưng phạm vi sử dụng trong đề tài này chỉ tải và xử lý **2020 Q1 đến 2026 Q2**.

**Lưu ý về chất lượng:** Dữ liệu được lấy từ hồ sơ XBRL "as filed" với SEC và được cung cấp dưới dạng flat files. Dữ liệu có thể chứa sai sót phát sinh từ thông tin do registrant cung cấp hoặc quá trình trích xuất/tổng hợp; với các số liệu tài chính quan trọng cần đối chiếu với filing gốc.

**Lưu ý về dimension:** SEC Financial Statement Data Sets không cung cấp transaction-level ledger với các chiều sản phẩm/khách hàng/khu vực như một hệ thống ERP. Dữ liệu XBRL vẫn có một số thông tin dimensional/segment và SIC. Vì vậy SEC phù hợp hơn với phân tích financial-statement level và industry-level hơn là drill-down transaction-level.

**Tại sao cần:** SEC EDGAR là nguồn dữ liệu tài chính thật chính cho warehouse. Cung cấp số liệu từ báo cáo tài chính doanh nghiệp nộp cho SEC, đủ để tính các chỉ số doanh nghiệp (doanh thu, biên lợi nhuận, DSO...) và tạo chuỗi thời gian cho dự báo RQ3.

**Lý do lấy:**
- **Dữ liệu thật, chuẩn XBRL** → độ tin cậy cao, có thể kiểm chứng với báo cáo công khai.
- **Miễn phí, không giới hạn** → không lo vấn đề giấy phép khi phân tích hoặc công bố.
- **26 quý (2020–2026)** → cung cấp cửa sổ dữ liệu tương đối phù hợp cho một số baseline forecasting ngắn hạn và phân tích xu hướng, nhưng là hạn chế đáng kể đối với deep learning hoặc các mô hình cần chuỗi dài.
- Có mã SIC → phân tích theo ngành, tạo chiều drill-down tự nhiên.

**Review sơ bộ:**
- **Hoàn thiện:** 26 quý đã tải đầy đủ (2020–2026), file .7z nguyên vẹn.
- **Chất lượng:** Dữ liệu chuẩn XBRL, có kiểm tra của SEC, cập nhật đều quý.
- **Vấn đề tiềm ẩn:** Chỉ có báo cáo tổng hợp, không có sổ cái chi tiết → không drill-down sâu. Cần xử lý ~1,2 GB nén, tốn thời gian extract/transform.
- **Độ sẵn sàng:** Cần giải nén và nạp vào DuckDB trước khi dùng.

**Validation cần thực hiện:**
- Kiểm tra duplicate filing
- Kiểm tra missing values trong các trường chính
- Kiểm tra units và scale
- Kiểm tra fiscal period consistency
- Kiểm tra entity coverage
- Kiểm tra segment fields (nếu có)

#### 2.2.2. Online Retail II (UCI) 

| Thuộc tính | Chi tiết |
|---|---|
| **Nội dung** | ~1 triệu giao dịch, 2009–2011, có mã sản phẩm, quốc gia, khách hàng, giá, số lượng |
| **Giấy phép** | UCI Machine Learning Repository. Được phép sử dụng cho nghiên cứu và học tập; cần kiểm tra điều khoản cụ thể trước khi sử dụng thương mại hoặc phân phối lại |
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

**Tại sao cần:** Online Retail II bù đắp hạn chế của SEC EDGAR — không có chiều sản phẩm/khu vực/khách hàng chi tiết. Dataset này cung cấp giao dịch bán lẻ thật với đầy đủ chiều phân rã để đánh giá F9 (phân rã nguyên nhân) và tạo dashboard có drill-down sâu.

**Lý do lấy:**
- ~1 triệu giao dịch, 2009–2011 → đủ lớn để thật, đủ nhỏ để xử lý local.
- Có mã sản phẩm, quốc gia, khách hàng → đủ chiều để phân tích "doanh thu giảm do đâu?" (sản phẩm? khu vực? khách hàng?).
- Giấy phép UCI rõ ràng, dùng cho nghiên cứu → phù hợp cho đồ án. Cần kiểm tra điều khoản cụ thể trước khi sử dụng thương mại hoặc phân phối lại.

**Review sơ bộ:**
- **Hoàn thiện:** File Excel ~45,6 MB, đầy đủ 8 cột, ~1 triệu giao dịch.
- **Chất lượng:** Dữ liệu thật, có khách hàng/sản phẩm/quốc gia → đủ chiều phân rã. Tuy nhiên có missing values (Customer ID, Description) và outliers (Price âm, Quantity âm).
- **Vấn đề tiềm ẩn:** Thời gian 2009–2011 hơi cũ, cần kiểm tra lại tính relevance. Giao dịch có `Quantity < 0` thường liên quan đến cancellation/returns và không nên đơn giản coi tất cả là lỗi; cần xác định quy tắc business semantics trước khi loại bỏ (ví dụ: tách cancellation/return thành loại giao dịch riêng tùy mục tiêu phân tích).
- **Độ sẵn sàng:** Sẵn sàng sau khi clean: xác định business semantics cho Quantity < 0 (cancellation/return), điền missing, chuyển đổi định dạng ngày tháng.

**Validation cần thực hiện:**
- Kiểm tra missing values (Customer ID, Description)
- Kiểm tra negative/zero price
- Kiểm tra negative quantity và xác định business semantics
- Kiểm tra duplicate invoice line
- Kiểm tra date range consistency

---

### 2.3. BỘ SINH DỮ LIỆU TỔNG HỢP (tự viết)

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
│   ├── ledger_base.csv           # sổ cái sạch (101,631 dòng: 1 header + 101,630 data)
│   ├── ledger_anomaly.csv        # sổ cái có anomaly (184 scenarios)
│   ├── labels.csv                # ground truth (185 dòng: 1 header + 184 scenarios)
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

**Tại sao cần:** Đây là hạ tầng nghiên cứu quan trọng nhất, không nguồn công khai nào thay thế được. Dữ liệu thật không có nhãn "đâu là bất thường" → không thể đánh giá F8 (phát hiện bất thường) và F9 (phân rã nguyên nhân) một cách khách quan. Phải tự sinh dữ liệu và chèn bất thường có kiểm soát.

**Lý do lấy:**
- **Ground truth chắc chắn** → biết chính xác vị trí, loại, độ lớn bất thường, đánh giá F1/F8/F9 có cơ sở.
- **4 loại bất thường** (spike, level_shift, trend_break, dimension_local) → kiểm tra toàn diện khả năng phát hiện của hệ thống.
- **184 scenarios** → tạo cơ sở để phân tích F1 theo loại anomaly và magnitude, với điều kiện mỗi nhóm magnitude có đủ số scenario để ước lượng metric ổn định.
- **Loại dimension_local** quan trọng nhất: tổng doanh thu bình thường nhưng một khu vực sụt 40% → đây là ca kiểm tra F9, không dataset công khai nào trả lời được.

**Phương pháp ghi chú:** Synthetic data được dùng để tạo ground truth có kiểm soát, cho phép đo detection/recovery/attribution một cách khách quan. Nó không được dùng để tuyên bố hệ thống hoạt động tốt trên dữ liệu thực.

**Review sơ bộ:**
- **Hoàn thiện:** Pipeline hoàn chỉnh, output đã sinh xong: `ledger_base.csv` (101,631 dòng), `ledger_anomaly.csv`, `labels.csv` (184 scenarios), `labels_verified.csv` (184/184 passed).
- **Chất lượng:** Dữ liệu sạch, đa dạng chiều (region, product, channel), 4 loại anomaly rõ ràng. Labels đã được verify tự động.
- **Vấn đề tiềm ẩn:** Là dữ liệu tổng hợp, có thể thiếu chiều sâu của dữ liệu thật (như seasonality phức tạp, noise thực). Cần kết hợp với dữ liệu thật để tăng realism.
- **Độ sẵn sàng:** Sẵn sàng cho F8/F9 evaluation. Có thể mở rộng bằng cách thêm config mới, tăng version để tránh nhầm lẫn.

**Validation cần thực hiện:**
- Kiểm tra label consistency
- Kiểm tra scenario overlap
- Kiểm tra affected rows
- Kiểm tra ground-truth correctness
- Kiểm tra không có data leakage giữa train và test

---

### 2.4. DỰ BÁO CHUỖI THỜI GIAN (cho RQ3)

#### 2.4.1. Monash Time Series Forecasting Archive

| Thuộc tính | Chi tiết |
|---|---|
| **Nội dung** | Hơn 30 bộ dữ liệu chuỗi thời gian, nhiều miền, định dạng thống nhất `.tsf` |
| **Vì sao dùng** | Cung cấp benchmark context và các kết quả tham chiếu cho đánh giá RQ3 |
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

**Tại sao cần:** Monash cung cấp chuỗi thời gian công khai có **kết quả baseline đã công bố** của nhiều mô hình (ETS, ARIMA, Prophet, DeepAR...). Dùng nó để đánh giá RQ3 — mô hình dự báo của bạn có tốt hơn các phương pháp cổ điển không.

**Lý do lấy:**
- Archive cung cấp benchmark context và các kết quả tham chiếu. Tuy nhiên, nếu muốn kết luận mô hình đề xuất tốt hơn một baseline cụ thể, baseline cần được chạy lại hoặc tái tạo dưới cùng protocol về split, forecast horizon, preprocessing và metric.
- Định dạng `.tsf` thống nhất → dễ parse, nhiều thư viện hỗ trợ.
- Tần suất quý/tháng giống dữ liệu tài chính → đánh giá trên domain tương đồng.
- Chọn bộ có tính chất giống chuỗi tài chính (tần suất thấp, có mùa vụ, chuỗi ngắn) → Hospital, M4-Quarterly, Tourism-Quarterly.

**Review sơ bộ:**
- **Hoàn thiện:** 4 bộ `.tsf` đã có đầy đủ: Hospital, M4 Monthly, M4 Quarterly, Tourism Quarterly.
- **Chất lượng:** Định dạng thống nhất, có metadata (frequency, series length), baseline công khai sẵn có.
- **Vấn đề tiềm ẩn:** Chuỗi thời gian ngắn (~84 tháng), có thể không đủ cho deep learning. Cần đánh giá nếu dùng TimesFM/Chronos (có thể rò rỉ dữ liệu từ training set).
- **Độ sẵn sàng:** Sẵn sàng cho baseline evaluation sau khi parse `.tsf` và chạy các mô hình tham chiếu.

**Validation cần thực hiện:**
- Kiểm tra TSF parsing
- Kiểm tra frequency metadata
- Kiểm tra missing observations
- Kiểm tra series length
- Kiểm tra train/val/test split theo thời gian

---

### 2.5. PHÁT HIỆN BẤT THƯỜNG (đối chứng cho F8)

#### 2.5.1. TSB-AD 

| Thuộc tính | Chi tiết |
|---|---|
| **Nội dung** | **1.070 chuỗi thời gian từ 40 bộ dữ liệu** (toàn bộ benchmark). Thư mục local đang lưu **TSB-AD-U** (đơn biến) với 870 file CSV thuộc 23 bộ |
| **Kèm theo** | 40 thuật toán phát hiện đã cài sẵn (thống kê, mạng nơ-ron, mô hình nền tảng) |
| **Giấy phép** | Apache 2.0 cho phần tiền xử lý; giấy phép gốc theo từng dataset thành phần |
| **Link** | https://github.com/TheDatumOrg/TSB-AD |

**Dữ liệu có sẵn tại:** `D:\PYTHON\Dataset\Data\5. PHÁT HIỆN BẤT THƯỜNG\TSB-AD-U\`

Đây là phần **TSB-AD-U** (đơn biến) của benchmark, gồm **870 file CSV** thuộc **23 bộ dữ liệu** sau:
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

**Tại sao cần:** TSB-AD cung cấp benchmark chuẩn cho phát hiện bất thường chuỗi thời gian. Dùng nó làm đối chứng cho F8 — so sánh phương pháp STL+z-score của bạn với 40 thuật toán khác nhau (thống kê, mạng nơ-ron, mô hình nền tảng).

**Lý do lấy:**
- **Toàn bộ benchmark TSB-AD gốc có 1.070 chuỗi từ 40 bộ dữ liệu** → đa dạng domain, tần suất, kích thước, kiểm tra độ tổng quát.
- **Chất lượng nhãn tốt** hơn NAB/Yahoo S5 → tránh đánh giá trên dữ liệu có lỗi gán nhãn.
- **40 thuật toán mặc định** → có sẵn baseline so sánh, không cần cài đặt lại.
- Thư mục local chỉ có **TSB-AD-U (đơn biến): 870 chuỗi thuộc 23 bộ**. Chỉ cần **tập con tần suất thấp, có mùa vụ** (giống tài chính) → đánh giá phù hợp domain, không cần chạy hết 870 chuỗi.

**Review sơ bộ:**
- **Hoàn thiện:** 870 file CSV đã có sẵn (TSB-AD-U), đủ 23 bộ dữ liệu, đa dạng domain.
- **Chất lượng:** Chất lượng nhãn tốt hơn NAB/Yahoo S5, đã được tuyển chọn và chuẩn hóa bởi TSB-AD.
- **Vấn đề tiềm ẩn:** Toàn bộ benchmark gốc có 1.070 chuỗi từ 40 bộ (bao gồm TSB-AD-M đa biến), nhưng thư mục local chỉ có TSB-AD-U (870 chuỗi, 23 bộ). Quy tắc chọn tập con phải được công bố trước khi chạy evaluation để tránh selection bias (ví dụ: chỉ chọn các chuỗi có kết quả tốt).
- **Độ sẵn sàng:** Sẵn sàng cho đối chứng F8 sau khi chọn tập con ~50–100 chuỗi phù hợp.

**Validation cần thực hiện:**
- Kiểm tra label format
- Kiểm tra frequency
- Kiểm tra series length
- Kiểm tra anomaly ratio
- Kiểm tra dataset provenance

---

## 3. THỨ TỰ THỰC HIỆN ĐỀ XUẤT

| Giai đoạn | Việc | Output |
|-----------|------|--------|
| 1 | Validate local inventory | Dataset manifest |
| 2 | Validate BookSQL + schema | NL2SQL baseline |
| 3 | Extract SEC → DuckDB | Financial warehouse |
| 4 | Clean Online Retail II | Transaction warehouse |
| 5 | Finalize synthetic generator | Ground truth |
| 6 | Vietnamese BookSQL subset | RQ2 evaluation |
| 7 | Define forecasting protocol | RQ3 protocol |
| 8 | Run Monash baselines | Forecasting benchmark |
| 9 | Select TSB-AD subset | F8 benchmark |
| 10 | Run integrated evaluation | Final metrics |

---

## 4. TÓM TẮT GIẤY PHÉP

| Dataset | License / điều kiện | Thương mại? | Phân phối lại? |
|---------|---------------------|:-----------:|:--------------:|
| BookSQL | CC-BY-NC-SA | ❌ | ✓ (cùng giấy phép) |
| SEC EDGAR | Dữ liệu công khai từ SEC; tuân thủ điều kiện sử dụng/attribution | ✓* | ✓* |
| Online Retail II | CC BY 4.0 | ✓ | ✓, kèm attribution |
| Monash TSF | Theo từng dataset/nguồn gốc | ⚠️ | ⚠️ |
| TSB-AD | Apache 2.0 cho preprocessing/curation; dataset thành phần theo license gốc | ⚠️ | ⚠️ |
| Dữ liệu tự sinh | Do nhóm tự tạo | ✓ | ✓ |

> `*` Cần kiểm tra điều kiện cụ thể khi đóng gói/phân phối lại dữ liệu đã xử lý.

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
| **Spider 2.0-Snow** | https://huggingface.co/datasets/xlangai/spider2-lite |

---

## 6. ÁNH XẠ DATASET → CÂU HỎI NGHIÊN CỨU / CHỨC NĂNG

| Dataset | RQ | Function | Vai trò |
|---------|----|----------|---------|
| BookSQL | RQ1 | NL2SQL | Benchmark chính cho miền kế toán |
| Spider 2.0-Snow | RQ1 | NL2SQL | External reference / out-of-domain baseline |
| SEC EDGAR | RQ1, RQ3 | F6, F7, F10, F11 | Financial warehouse + forecasting |
| Online Retail II | — | F9 | Transaction-level drill-down |
| Synthetic | — | F8, F9, F10 | Ground-truth evaluation |
| Monash | RQ3 | F10 | Forecasting benchmark |
| TSB-AD-U | — | F8 | Anomaly benchmark |

---

## 7. PROTOCOL ĐÁNH GIÁ DỰ BÁO (RQ3)

### 7.1. Dataset

- SEC financial time series
- Synthetic normal time series
- Monash reference datasets

### 7.2. Forecasting unit

Phải xác định rõ dự báo theo:
- company/entity
- financial metric
- hoặc aggregated series

### 7.3. Temporal split

Sử dụng chronological split / rolling-origin evaluation. Không random shuffle.

### 7.4. Metrics

Đề xuất:
- MAE
- RMSE
- MASE hoặc sMAPE

### 7.5. Baselines

Ít nhất xem xét:
- Naive
- Seasonal Naive nếu phù hợp
- ARIMA/ETS
- Model đề xuất

### 7.6. Foundation model contamination

Nếu sử dụng TimesFM/Chronos hoặc các foundation model khác, phải ghi rõ vấn đề potential data contamination / training-data leakage và không coi kết quả là hoàn toàn công bằng nếu benchmark có khả năng xuất hiện trong pretraining corpus.

---

## 8. DATA LEAKAGE / CONTAMINATION

### 8.1. NL2SQL

Không để cùng một question/template/schema xuất hiện giữa train và evaluation nếu pipeline tự xây dựng dữ liệu bổ sung.

### 8.2. Forecasting

Không random shuffle temporal data.

### 8.3. Foundation models

TimesFM/Chronos và các foundation model khác có khả năng đã được pre-trained trên dữ liệu công khai. Nếu dataset benchmark có khả năng nằm trong training corpus, đánh dấu kết quả là potentially contaminated.

### 8.4. Synthetic

Không dùng anomaly-injected test data để train anomaly detector nếu mục tiêu là đánh giá khả năng phát hiện.

---

## 9. HẠN CHẾ (LIMITATIONS)

1. **SEC EDGAR:** Chỉ có báo cáo tổng hợp, không có transaction-level ledger với chiều sản phẩm/khách hàng/khu vực chi tiết. 26 quý là hạn chế đáng kể cho deep learning.
2. **Online Retail II:** Thời gian 2009–2011 hơi cũ; cần kiểm tra lại tính relevance.
3. **BookSQL:** Câu hỏi tiếng Anh; đánh giá tiếng Việt cần tập con riêng được dịch và human-reviewed.
4. **Synthetic data:** Là dữ liệu tổng hợp, có thể thiếu chiều sâu của dữ liệu thật (seasonality phức tạp, noise thực).
5. **Monash:** Chuỗi thời gian ngắn (~84 tháng), có thể không đủ cho deep learning.
6. **TSB-AD:** Thư mục local chỉ có TSB-AD-U (870 chuỗi, 23 bộ), chưa đầy đủ toàn bộ benchmark (1.070 chuỗi, 40 bộ).
7. **Spider 2.0-Snow:** Chỉ là đối chứng ngoài miền, không phải trọng tâm nghiên cứu.

---

## 7. LƯU Ý KHI SỬ DỤNG

1. **BookSQL:** Câu hỏi bằng tiếng Anh. Nếu muốn khẳng định hệ thống chạy tiếng Việt, phải dịch một tập con và cho người bản ngữ rà lại.
2. **SEC EDGAR:** Chỉ có báo cáo tổng hợp, không có sổ cái chi tiết. Không có chiều "khu vực", "sản phẩm", "khách hàng" → không drill-down sâu được.
3. **Online Retail II:** Dùng cho drill-down thật với chiều sản phẩm/quốc gia/khách hàng.
4. **TSB-AD:** Không cần chạy hết 1.070 chuỗi. Lấy tập con tần suất thấp, có mùa vụ (giống dữ liệu tài chính).
5. **Synthetic data:** Mỗi lần đổi config, nên tăng version hoặc đổi tên thư mục output để tránh nhầm lẫn.
6. **Spider 2.0-Snow:** Chỉ dùng làm đối chứng bên ngoài miền, không phải trọng tâm nghiên cứu.
