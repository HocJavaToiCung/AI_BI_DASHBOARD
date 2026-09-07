# Bước 1 — Ghi chú kho dữ liệu (DuckDB)

**Nguồn:** `Clean/num_sub_tag_clean_2020q1.csv` — SEC EDGAR Financial Statement Data Set quý 2020Q1,
đã gộp sẵn 3 file gốc `num` + `sub` + `tag`.
**Script dựng lại:** `python scripts/load_duckdb.py` (idempotent — drop + create).
**Đầu ra:** `Data/warehouse.duckdb` (~582 MB).

---

## 1. Bảng trong kho

| Bảng | Số dòng | Vai trò |
|------|--------:|---------|
| `fact_raw` | 2.991.269 | Toàn bộ CSV, chỉ ép kiểu, **không lọc**. Nguồn bất biến để tái lập / debug. |
| `fact_annual` | 841.856 | Số hợp nhất theo năm, US-GAAP, USD, đã khử trùng lặp. **Bảng chính cho demo.** |
| `fact_segment` | 857.412 | Số chia theo `segments` (business/geography/legal-entity). Để dành cho F9 — phân rã. |
| `dim_company` | 4.032 | 1 dòng / công ty (`cik`), kèm `industry` = nhãn ngành tiếng Việt suy từ mã SIC. |

### Cột `fact_annual`
`cik, company_name, sic, state, countryinc, adsh, form, filed, filing_fy, filing_period,`
`tag, tlabel, iord, crdr, ddate, qtrs, fiscal_year, is_primary_year, value`

- `fiscal_year = year(ddate)` — năm kết thúc của kỳ mà con số này thuộc về.
- `is_primary_year` = `TRUE` nếu `ddate` trùng năm với kỳ chính của filing (số của chính năm báo cáo),
  `FALSE` nếu là số so sánh năm trước lấy từ cùng một 10-K.

---

## 2. Quy tắc lọc để ra `fact_annual` (và lý do)

| Điều kiện | Lý do |
|-----------|-------|
| `form IN ('10-K', '10-K/A')` | Chỉ báo cáo **năm**. Bỏ 10-Q (1 quý — không dựng chuỗi từ 1 quý được), bỏ S-1/6-K (hồ sơ đăng ký, không phải BCTC). |
| `uom = 'USD'` | Một đơn vị tiền để số liệu **so sánh được**. Tự động loại phần lớn 20-F/40-F (doanh nghiệp nước ngoài). |
| `custom = '0'` | Chỉ tag chuẩn (taxonomy chung), bỏ tag riêng do công ty tự mở rộng — không ánh xạ được vào semantic layer. |
| `version LIKE 'us-gaap/%'` | Chỉ chuẩn **US-GAAP**. Loại các dòng `ifrs/2019`, `ifrs/2018` (IFRS dùng taxonomy khác, định nghĩa chỉ số lệch). |
| `coreg IS NULL` | Chỉ công ty mẹ, bỏ công ty đồng đăng ký (co-registrant) nộp hồ sơ chung. |
| `segments IS NULL` | Lấy **số hợp nhất tổng**, không lấy dòng chia theo segment (đã tách sang `fact_segment`). |
| `(iord='I' AND qtrs=0) OR (iord='D' AND qtrs=4)` | `iord='I'` = số thời điểm (bảng cân đối) → `qtrs=0`. `iord='D'` = số luồng (KQKD, lưu chuyển tiền) → `qtrs=4` = **cả năm**. Bỏ mọi kỳ dở dang (`qtrs` 1–3) đôi khi xuất hiện trong 10-K. |
| `value IS NOT NULL`, `ddate IS NOT NULL` | Số và ngày phải hợp lệ. |
| `year(ddate) BETWEEN 2016 AND 2021` | Chặn các `ddate` rác nằm quá xa kỳ báo cáo. |

### Khử trùng lặp
Sau khi lọc, mỗi `(cik, tag, fiscal_year)` chỉ giữ **1 dòng**, chọn theo:
`ORDER BY filed DESC, adsh DESC` → lấy số từ **bản nộp gần nhất** (xử lý ca 10-K/A đính chính,
và ca số năm N xuất hiện vừa trong 10-K năm N vừa trong 10-K năm N+1 dưới dạng số so sánh).

**Bất biến đã kiểm:** 0 dòng `value` NULL · 0 cặp `(cik, tag, fiscal_year)` trùng.

---

## 3. Công ty: giữ vs loại

| | Số công ty |
|---|--:|
| Tổng trong `fact_raw` | 5.404 |
| Có nộp 10-K / 10-K/A | 4.038 |
| **Giữ trong `fact_annual`** | **4.032** |
| 10-K bị loại (không còn dòng US-GAAP/USD/năm nào qua bộ lọc) | 6 |
| Chỉ nộp form nước ngoài, không có 10-K | 1.366 |
| (thông tin) có ít nhất 1 tag IFRS | 246 |

Phân bố `fiscal_year` trong `fact_annual`: 2016: 6.582 dòng · 2017: 168.018 · 2018: 326.869 ·
2019: 332.963 · 2020: 7.424 (99 công ty có năm tài chính kết thúc tháng 1–2/2020, ví dụ Walmart).

---

## 4. Đối chiếu với 10-K công khai (đã khớp)

Kiểm bằng danh sách tag ưu tiên tạm thời trong script (`CHECK_METRICS`); bộ đầy đủ ở Bước 2.

| Công ty | FY2019 doanh thu | FY2019 LNST | FY2019 tổng tài sản |
|---------|--:|--:|--:|
| Amazon (1018724) | 280,52 tỷ | 11,59 tỷ | 225,25 tỷ |
| Alphabet (1652044) | 161,86 tỷ | 34,34 tỷ | 275,91 tỷ |
| ExxonMobil (34088) | 264,94 tỷ | 14,34 tỷ | 362,60 tỷ |
| Coca-Cola (21344) | 37,27 tỷ | 8,92 tỷ | 86,38 tỷ |
| JPMorgan (19617) | — (xem ghi chú) | 36,43 tỷ | 2.687,38 tỷ |

Tất cả khớp số trong 10-K công bố.

---

## 5. Hạn chế / lưu ý cho các bước sau

1. **1 quý dữ liệu ⇒ chỉ cross-sectional.** Có tối đa 2–4 năm số liệu / công ty (chính + số so sánh
   trong cùng 10-K), đủ cho so sánh **YoY năm**, **không** đủ cho MoM/QoQ, phát hiện bất thường theo
   thời gian (F8) hay dự báo (F10, RQ3).
2. **Apple / Microsoft vắng mặt là đúng.** Năm tài chính kết thúc tháng 9 / tháng 6 → 10-K của họ nằm
   ở quý EDGAR khác; trong 2020Q1 họ chỉ nộp 10-Q. Chỉ công ty có FYE ~31/12 và nộp 10-K trong quý I
   dương lịch mới xuất hiện.
3. **Ngân hàng không có `Revenues`.** JPMorgan và các ngân hàng khác báo cáo thu nhập lãi thuần +
   thu nhập ngoài lãi, không có một dòng "doanh thu" duy nhất. Semantic layer (Bước 2) cần định nghĩa
   chỉ số riêng cho nhóm tài chính (SIC 60xx–61xx).
4. **`fiscal_year` = `year(ddate)`, không phải nhãn công ty tự đặt.** Công ty FYE tháng 1–2 (Walmart)
   có `fiscal_year=2019` ứng với kỳ họ gọi là "FY2019" nhưng `ddate` là 2019-01-31.
5. **Tag doanh thu phân mảnh.** Phải `COALESCE` theo thứ tự: `Revenues` →
   `RevenueFromContractWithCustomerExcludingAssessedTax` → `RevenueFromContractWithCustomerIncludingAssessedTax`.
6. **`fiscal_year=2016`** hầu hết là số dư đầu kỳ trong bảng biến động vốn chủ sở hữu của báo cáo
   3 năm — không phải bộ chỉ số đầy đủ. Lọc `is_primary_year` hoặc `fiscal_year >= 2017` khi cần.
7. **Doanh nghiệp nước ngoài / IFRS bị loại có chủ đích** (≈5% filing). Đảo ngược được: các dòng vẫn
   nằm trong `fact_raw`; muốn thêm thì bổ sung alias tag `ifrs-full:*` + bảng quy đổi tỷ giá theo
   `(currency, period_end)`.

---

## 6. Bàn giao cho Bước 2 (Semantic layer)

- `fact_annual` là bảng để compiler ngữ nghĩa sinh SQL. Truy vấn mẫu:
  ```sql
  SELECT value FROM fact_annual
  WHERE cik = ? AND tag = ? AND fiscal_year = ? AND is_primary_year;
  ```
- `dim_company` cung cấp dimension `industry` (từ SIC) và `state`.
- Cần xử lý: danh sách tag ưu tiên cho từng chỉ số, chỉ số phái sinh (margin, ROA, D/E),
  nhóm chỉ số riêng cho ngân hàng/bảo hiểm, so sánh YoY qua self-join `fiscal_year` 2019 vs 2018.
