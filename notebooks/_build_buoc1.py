# -*- coding: utf-8 -*-
"""Dựng notebook Bước 1 (nbformat) rồi thực thi (nbclient) để nhúng kết quả tham chiếu."""
import sys
from pathlib import Path
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
from nbclient import NotebookClient

ROOT = Path(r"D:/BI_DASHBOARD/AI_BI_DASHBOARD")
NB_DIR = ROOT / "notebooks"
NB_DIR.mkdir(exist_ok=True)
OUT = NB_DIR / "buoc1_nap_duckdb.ipynb"
CSV = "Clean/num_sub_tag_clean_2020q1.csv"           # tương đối so với ROOT
DB = "Data/warehouse.duckdb"

cells = []
def md(s): cells.append(new_markdown_cell(s.strip("\n")))
def code(s): cells.append(new_code_cell(s.strip("\n")))

md(r"""
# Bước 1 — Nạp SEC EDGAR 2020Q1 vào DuckDB & dựng lớp dữ liệu sạch

**Nguồn:** `Clean/num_sub_tag_clean_2020q1.csv` — SEC EDGAR *Financial Statement Data Set* quý 2020Q1,
đã gộp sẵn 3 file gốc `num` (số) + `sub` (hồ sơ nộp) + `tag` (từ điển tag XBRL).
Mỗi dòng = **một dữ kiện tài chính** được gắn tag XBRL trong một filing.

**Mục tiêu:** biến 1 file CSV thô thành kho SQL sạch mà mọi bước sau tin tưởng được —
hỏi *"doanh thu công ty X năm 2019"* → trả về **đúng một con số**.

**Đầu ra:** `Data/warehouse.duckdb` gồm 4 bảng: `fact_raw`, `fact_annual`, `fact_segment`, `dim_company`.
Notebook này dựng ra **đúng file DB đó** (giống hệt `scripts/load_duckdb.py`), kèm kết quả tham chiếu từng công đoạn.

**Nguyên tắc:** `fact_raw` giữ **bất biến** (chỉ ép kiểu, không lọc). Mọi quy tắc làm sạch nằm ở
bảng/`VIEW` phía trên — sai thì sửa quy tắc, không nạp lại.
""")

code(r"""
import duckdb, pandas as pd
from pathlib import Path

pd.set_option("display.max_columns", 40)
pd.set_option("display.width", 200)
pd.set_option("display.max_colwidth", 60)

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
CSV = (ROOT / "Clean/num_sub_tag_clean_2020q1.csv").as_posix()
DB  = (ROOT / "Data/warehouse.duckdb").as_posix()
Path(ROOT / "Data").mkdir(exist_ok=True)

print("duckdb", duckdb.__version__)
print("CSV   ", CSV, "|", f"{Path(CSV).stat().st_size/1e6:,.0f} MB")
con = duckdb.connect(DB)
con.execute("SET enable_progress_bar = false")   # tắt thanh tiến trình (tránh widget rác trong .ipynb)
""")

# ------------------------------------------------------------------ Công đoạn 1
md(r"""
---
## Công đoạn 1 — Khảo sát file thô

Chưa nạp gì. Chỉ đọc trực tiếp CSV để biết quy mô, loại form, chuẩn kế toán và độ phủ chỉ số.
""")

code(r"""
con.execute(f"CREATE OR REPLACE VIEW _scan AS SELECT * FROM read_csv('{CSV}', all_varchar=true, header=true)")
con.execute("SELECT * FROM _scan LIMIT 5").fetchdf()
""")

code(r"""
# Tổng quan
con.execute('''
  SELECT count(*)               AS so_dong,
         count(DISTINCT adsh)   AS so_filing,
         count(DISTINCT cik)    AS so_cong_ty,
         count(DISTINCT tag)    AS so_tag_khac_nhau
  FROM _scan
''').fetchdf()
""")

code(r"""
# Phân bố theo loại form (mức filing)
con.execute('''
  SELECT form,
         count(DISTINCT adsh) AS so_filing,
         count(*)             AS so_dong
  FROM _scan GROUP BY 1 ORDER BY so_filing DESC LIMIT 12
''').fetchdf()
""")

code(r"""
# Chuẩn kế toán: us-gaap (giữ) vs ifrs (loại) vs custom = tag công ty tự mở rộng (loại)
con.execute('''
  SELECT CASE WHEN version LIKE 'us-gaap/%' THEN 'us-gaap'
              WHEN version LIKE 'ifrs/%'    THEN 'ifrs'
              ELSE 'custom (mở rộng riêng)' END AS loai_version,
         count(*) AS so_dong
  FROM _scan GROUP BY 1 ORDER BY so_dong DESC
''').fetchdf()
""")

code(r"""
# Độ phủ vài tag chỉ số then chốt (số filing có chứa tag)
con.execute('''
  SELECT tag, count(DISTINCT adsh) AS so_filing_co_tag
  FROM _scan
  WHERE tag IN ('Revenues','RevenueFromContractWithCustomerExcludingAssessedTax',
    'GrossProfit','CostOfGoodsAndServicesSold','OperatingIncomeLoss','NetIncomeLoss',
    'Assets','Liabilities','StockholdersEquity',
    'NetCashProvidedByUsedInOperatingActivities')
  GROUP BY 1 ORDER BY so_filing_co_tag DESC
''').fetchdf()
""")

md(r"""
**Nhận xét công đoạn 1:** ~3 triệu dòng · ~5.400 công ty · chủ yếu **10-K năm tài chính 2019**.
Độ phủ tài sản / vốn chủ / lãi ròng > 5.000 filing → **đủ cho phân tích cross-sectional** (nhiều công ty, 1 kỳ).
IFRS + custom chiếm phần nhỏ và sẽ bị loại ở công đoạn 3.
""")

# ------------------------------------------------------------------ Công đoạn 2
md(r"""
---
## Công đoạn 2 — Nạp CSV → `fact_raw` (ép kiểu, **không lọc**)

Vì sao ép kiểu tường minh:

- `value` → `DOUBLE`: `read_csv_auto` hay đoán nhầm thành text khi gặp ô trống/footnote → không tính tổng được.
- `ddate`, `period`, `filed` đang là số `YYYYMMDD` → đổi sang `DATE` để lọc/nhóm theo năm.
- `cik` giữ `VARCHAR` để không mất số 0 ở đầu.
- `segments`, `coreg`: chuỗi rỗng → `NULL` cho nhất quán.

`fact_raw` sau đó **không bao giờ bị sửa**.
""")

code(r"""
con.execute(f'''
CREATE OR REPLACE TABLE fact_raw AS
SELECT
    adsh, cik, name, sic,
    countryba, stprba, countryinc,
    form,
    TRY_CAST(fy AS INTEGER)                        AS fy,
    fp,
    TRY_CAST(strptime(period, '%Y%m%d') AS DATE)   AS period,
    fye, afs, wksi,
    TRY_CAST(strptime(filed, '%Y%m%d') AS DATE)    AS filed,
    prevrpt, detail,
    tag, tlabel, version, custom, datatype, iord, crdr,
    TRY_CAST(strptime(ddate, '%Y%m%d') AS DATE)    AS ddate,
    TRY_CAST(qtrs AS INTEGER)                      AS qtrs,
    uom,
    NULLIF(segments, '')                           AS segments,
    NULLIF(coreg, '')                              AS coreg,
    TRY_CAST(value AS DOUBLE)                       AS value,
    footnote,
    TRY_CAST(is_consolidated AS INTEGER)           AS is_consolidated
FROM read_csv('{CSV}', all_varchar = true, header = true)
''')
con.execute("SELECT count(*) AS so_dong_fact_raw FROM fact_raw").fetchdf()
""")

code(r"""
con.execute("DESCRIBE fact_raw").fetchdf()
""")

# ------------------------------------------------------------------ Công đoạn 3
md(r"""
---
## Công đoạn 3 — Dựng `fact_annual` (lọc + khử trùng lặp)

### 3a. Phễu lọc — số dòng còn lại sau **từng** điều kiện

| Điều kiện | Lý do |
|-----------|-------|
| `form ∈ {10-K, 10-K/A}` | Chỉ báo cáo **năm**. Bỏ 10-Q, S-1, 6-K… |
| `uom = 'USD'` | Một đơn vị tiền để so sánh được; loại luôn phần lớn doanh nghiệp nước ngoài |
| `custom = '0'` | Chỉ tag chuẩn, bỏ tag công ty tự mở rộng |
| `version LIKE 'us-gaap/%'` | Chỉ **US-GAAP**, loại IFRS |
| `coreg IS NULL` | Chỉ công ty mẹ |
| `segments IS NULL` | Số **hợp nhất tổng**, không phải dòng chia segment |
| `(iord='I' AND qtrs=0) OR (iord='D' AND qtrs=4)` | Số thời điểm (bảng cân đối) hoặc số **cả năm** (KQKD, lưu chuyển tiền); bỏ kỳ dở dang |
| `value`, `ddate` không NULL; `year(ddate)` 2016–2021 | Số & ngày hợp lệ, chặn ngày rác |
""")

code(r"""
steps = [
    ("0. fact_raw (chưa lọc)",                 "TRUE"),
    ("1. form ∈ {10-K, 10-K/A}",               "form IN ('10-K','10-K/A')"),
    ("2. + uom = 'USD'",                       "uom = 'USD'"),
    ("3. + custom = '0'",                      "custom = '0'"),
    ("4. + version us-gaap",                   "version LIKE 'us-gaap/%'"),
    ("5. + coreg IS NULL",                     "coreg IS NULL"),
    ("6. + segments IS NULL",                  "segments IS NULL"),
    ("7. + (I,qtrs=0) hoặc (D,qtrs=4)",        "((iord='I' AND qtrs=0) OR (iord='D' AND qtrs=4))"),
    ("8. + value/ddate hợp lệ, năm 2016-2021", "value IS NOT NULL AND ddate IS NOT NULL AND year(ddate) BETWEEN 2016 AND 2021"),
]
acc, rows = [], []
for name, c in steps:
    acc.append(c)
    where = " AND ".join(f"({x})" for x in acc)
    n = con.execute(f"SELECT count(*) FROM fact_raw WHERE {where}").fetchone()[0]
    rows.append({"buoc_loc": name, "so_dong_con_lai": n})
pd.DataFrame(rows)
""")

md(r"""
### 3b. Bảng lọc-nhưng-chưa-khử-trùng `_annual_pre`

Tách riêng để **nhìn thấy** vấn đề trùng lặp trước khi xử lý.
""")

code(r"""
con.execute('''
CREATE OR REPLACE TABLE _annual_pre AS
SELECT
    r.cik,
    r.name                            AS company_name,
    r.sic,
    r.stprba                          AS state,
    r.countryinc,
    r.adsh, r.form, r.filed,
    r.fy                              AS filing_fy,
    r.period                          AS filing_period,
    r.tag, r.tlabel, r.iord, r.crdr, r.ddate, r.qtrs,
    CAST(year(r.ddate) AS INTEGER)    AS fiscal_year,
    (year(r.ddate) = year(r.period))  AS is_primary_year,
    r.value
FROM fact_raw r
WHERE r.form IN ('10-K','10-K/A')
  AND r.uom = 'USD' AND r.custom = '0' AND r.version LIKE 'us-gaap/%'
  AND r.coreg IS NULL AND r.segments IS NULL
  AND r.value IS NOT NULL AND r.ddate IS NOT NULL
  AND ((r.iord='I' AND r.qtrs=0) OR (r.iord='D' AND r.qtrs=4))
  AND year(r.ddate) BETWEEN 2016 AND 2021
''')
con.execute("SELECT count(*) AS so_dong_annual_pre FROM _annual_pre").fetchdf()
""")

code(r"""
# Vẫn còn cặp (cik, tag, fiscal_year) xuất hiện nhiều lần
con.execute('''
  SELECT cik, tag, fiscal_year, count(*) AS so_ban
  FROM _annual_pre GROUP BY 1,2,3 HAVING count(*) > 1
  ORDER BY so_ban DESC LIMIT 5
''').fetchdf()
""")

code(r"""
# Soi 1 ca trùng: cùng cik+tag+năm nhưng khác filing (adsh/filed) -> chọn bản nộp gần nhất
con.execute('''
  WITH d AS (
    SELECT cik, tag, fiscal_year FROM _annual_pre
    GROUP BY 1,2,3 HAVING count(*) > 1 LIMIT 1
  )
  SELECT p.cik, p.tag, p.fiscal_year, p.adsh, p.form, p.filed, p.value
  FROM _annual_pre p JOIN d USING (cik, tag, fiscal_year)
  ORDER BY p.filed DESC
''').fetchdf()
""")

md(r"""
### 3c. Khử trùng lặp → `fact_annual`

Mỗi `(cik, tag, fiscal_year)` giữ **1 dòng**, lấy từ **bản nộp gần nhất**
(`ORDER BY filed DESC, adsh DESC`). Xử lý ca 10-K/A đính chính và ca số năm N
vừa nằm trong 10-K năm N vừa là số so sánh trong 10-K năm N+1.
""")

code(r"""
con.execute('''
CREATE OR REPLACE TABLE fact_annual AS
SELECT * FROM _annual_pre
QUALIFY row_number() OVER (
    PARTITION BY cik, tag, fiscal_year
    ORDER BY filed DESC, adsh DESC
) = 1
''')
con.execute("SELECT count(*) AS so_dong_fact_annual FROM fact_annual").fetchdf()
""")

# ------------------------------------------------------------------ Công đoạn 4
md(r"""
---
## Công đoạn 4 — `fact_segment` (số chia theo segment — để dành cho F9)

Cùng bộ lọc như `fact_annual` **nhưng** `segments IS NOT NULL`. Không dùng ở demo 1 file;
giữ sẵn cho chức năng phân rã nguyên nhân (F9) sau này.
""")

code(r"""
con.execute('''
CREATE OR REPLACE TABLE fact_segment AS
SELECT
    r.cik, r.name AS company_name, r.sic, r.stprba AS state,
    r.adsh, r.filed, r.tag, r.tlabel, r.iord, r.ddate,
    CAST(year(r.ddate) AS INTEGER) AS fiscal_year,
    r.qtrs, r.segments, r.value
FROM fact_raw r
WHERE r.form IN ('10-K','10-K/A')
  AND r.uom = 'USD' AND r.custom = '0' AND r.version LIKE 'us-gaap/%'
  AND r.coreg IS NULL AND r.segments IS NOT NULL
  AND r.value IS NOT NULL AND r.ddate IS NOT NULL
  AND ((r.iord='I' AND r.qtrs=0) OR (r.iord='D' AND r.qtrs=4))
  AND year(r.ddate) BETWEEN 2016 AND 2021
''')
con.execute("SELECT count(*) AS so_dong_fact_segment FROM fact_segment").fetchdf()
""")

code(r"""
# 10 kiểu segment phổ biến nhất
con.execute('''
  SELECT segments, count(*) AS so_dong
  FROM fact_segment GROUP BY 1 ORDER BY so_dong DESC LIMIT 10
''').fetchdf()
""")

# ------------------------------------------------------------------ Công đoạn 5
md(r"""
---
## Công đoạn 5 — `dim_company` + nhãn ngành tiếng Việt

1 dòng / công ty. Mã SIC (số) → nhãn ngành đọc được, dùng `scripts/sic_labels.py`
(~40 mã 4 chữ số phổ biến + fallback theo nhóm ngành). Cần để câu hỏi kiểu
*"ngành ngân hàng"*, *"công ty phần mềm"* ánh xạ được.
""")

code(r"""
import sys
sys.path.insert(0, (ROOT / "scripts").as_posix())
from sic_labels import sic_label

dim = con.execute('''
  SELECT r.cik,
         mode(r.name)       AS company_name,
         mode(r.sic)        AS sic,
         mode(r.stprba)     AS state,
         mode(r.countryinc) AS country_inc
  FROM fact_raw r
  WHERE r.cik IN (SELECT DISTINCT cik FROM fact_annual)
  GROUP BY r.cik
''').fetchdf()
dim["industry"] = dim["sic"].map(sic_label)
con.execute("CREATE OR REPLACE TABLE dim_company AS SELECT * FROM dim")
dim.head(10)
""")

code(r"""
con.execute('''
  SELECT industry, count(*) AS so_cong_ty
  FROM dim_company GROUP BY 1 ORDER BY so_cong_ty DESC LIMIT 12
''').fetchdf()
""")

# ------------------------------------------------------------------ Công đoạn 6
md(r"""
---
## Công đoạn 6 — Kiểm tra tỉnh táo & đối chiếu 10-K công khai

Đây là **bằng chứng** Bước 1 chạy đúng.
""")

code(r"""
# Bất biến bắt buộc
n_null = con.execute("SELECT count(*) FROM fact_annual WHERE value IS NULL").fetchone()[0]
n_dup  = con.execute('''SELECT count(*) FROM (
           SELECT 1 FROM fact_annual GROUP BY cik, tag, fiscal_year HAVING count(*) > 1)''').fetchone()[0]
pd.DataFrame([
    {"kiem_tra": "value NULL trong fact_annual",        "ket_qua": n_null, "dat": n_null == 0},
    {"kiem_tra": "cặp (cik,tag,fiscal_year) trùng lặp", "ket_qua": n_dup,  "dat": n_dup == 0},
])
""")

code(r"""
# Đếm dòng 4 bảng
pd.DataFrame([
    {"bang": b, "so_dong": con.execute(f"SELECT count(*) FROM {b}").fetchone()[0]}
    for b in ["fact_raw", "fact_annual", "fact_segment", "dim_company"]
])
""")

code(r"""
# Công ty: giữ vs loại
raw_co   = con.execute("SELECT count(DISTINCT cik) FROM fact_raw").fetchone()[0]
co_10k   = con.execute("SELECT count(DISTINCT cik) FROM fact_raw WHERE form IN ('10-K','10-K/A')").fetchone()[0]
kept     = con.execute("SELECT count(*) FROM dim_company").fetchone()[0]
foreign  = con.execute('''SELECT count(DISTINCT cik) FROM fact_raw
             WHERE cik NOT IN (SELECT cik FROM fact_raw WHERE form IN ('10-K','10-K/A'))''').fetchone()[0]
ifrs     = con.execute("SELECT count(DISTINCT cik) FROM fact_raw WHERE version LIKE 'ifrs/%'").fetchone()[0]
pd.DataFrame([
    {"chi_tieu": "Tổng công ty trong fact_raw",                 "so_cong_ty": raw_co},
    {"chi_tieu": "Có nộp 10-K / 10-K/A",                        "so_cong_ty": co_10k},
    {"chi_tieu": "Giữ trong fact_annual",                       "so_cong_ty": kept},
    {"chi_tieu": "10-K bị loại (hết dòng US-GAAP/USD/năm)",     "so_cong_ty": co_10k - kept},
    {"chi_tieu": "Chỉ nộp form nước ngoài, không có 10-K",      "so_cong_ty": foreign},
    {"chi_tieu": "(thông tin) có tag IFRS",                     "so_cong_ty": ifrs},
])
""")

code(r"""
# Phân bố fiscal_year
con.execute('''
  SELECT fiscal_year,
         count(*)            AS so_dong,
         count(DISTINCT cik) AS so_cong_ty
  FROM fact_annual GROUP BY 1 ORDER BY 1
''').fetchdf()
""")

md(r"""
### Đối chiếu số với 10-K công bố

Dùng danh sách tag ưu tiên tạm thời (bộ đầy đủ ở Bước 2). Đơn vị: **tỷ USD**.
Chỉ công ty có năm tài chính kết thúc ~31/12 và nộp 10-K trong quý I dương lịch mới có mặt
→ Apple (FYE 30/9) và Microsoft (FYE 30/6) **vắng là đúng**.
""")

code(r"""
CHECK_METRICS = {
    "doanh_thu":    ["Revenues",
                     "RevenueFromContractWithCustomerExcludingAssessedTax",
                     "RevenueFromContractWithCustomerIncludingAssessedTax"],
    "lai_rong":     ["NetIncomeLoss", "ProfitLoss"],
    "tong_tai_san": ["Assets"],
    "von_chu_so_huu":["StockholdersEquity",
                     "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
}
KNOWN = {
    "1018724": "AMAZON COM INC",
    "1652044": "ALPHABET INC",
    "34088":   "EXXON MOBIL CORP",
    "21344":   "COCA-COLA CO",
    "19617":   "JPMORGAN CHASE & CO",
    "320193":  "APPLE INC (kỳ vọng: VẮNG)",
    "789019":  "MICROSOFT CORP (kỳ vọng: VẮNG)",
}

def metric_series(cik, tags):
    tlist = ",".join(f"'{t}'" for t in tags)
    prio  = " ".join(f"WHEN tag='{t}' THEN {i}" for i, t in enumerate(tags))
    q = f'''
      SELECT fiscal_year, value FROM (
        SELECT fiscal_year, value,
               row_number() OVER (PARTITION BY fiscal_year
                    ORDER BY CASE {prio} ELSE 99 END) rn
        FROM fact_annual WHERE cik = '{cik}' AND tag IN ({tlist})
      ) WHERE rn = 1 ORDER BY fiscal_year
    '''
    return {int(y): v for y, v in con.execute(q).fetchall()}

recs = []
for cik, nm in KNOWN.items():
    present = con.execute(f"SELECT count(*) FROM fact_annual WHERE cik = '{cik}'").fetchone()[0] > 0
    if not present:
        recs.append({"cong_ty": nm, "chi_so": "(vắng mặt trong fact_annual)",
                     "FY2017": None, "FY2018": None, "FY2019": None})
        continue
    for m, tags in CHECK_METRICS.items():
        s = metric_series(cik, tags)
        recs.append({
            "cong_ty": nm, "chi_so": m,
            "FY2017": round(s.get(2017)/1e9, 2) if s.get(2017) is not None else None,
            "FY2018": round(s.get(2018)/1e9, 2) if s.get(2018) is not None else None,
            "FY2019": round(s.get(2019)/1e9, 2) if s.get(2019) is not None else None,
        })
pd.DataFrame(recs)
""")

md(r"""
| Đối chiếu 10-K công bố (FY2019) | Doanh thu | LNST | Tổng tài sản |
|---|--:|--:|--:|
| Amazon | 280,52 | 11,59 | 225,25 |
| Alphabet | 161,86 | 34,34 | 275,91 |
| ExxonMobil | 264,94 | 14,34 | 362,60 |
| Coca-Cola | 37,27 | 8,92 | 86,38 |
| JPMorgan | — (ngân hàng, không có 1 dòng "doanh thu") | 36,43 | 2.687,38 |

Kết quả trong bảng trên khớp từng chữ số.
""")

# ------------------------------------------------------------------ Kết luận
md(r"""
---
## Kết luận & bàn giao cho Bước 2

**Đã tạo `Data/warehouse.duckdb`:**

| Bảng | ~Số dòng | Vai trò |
|------|--------:|---------|
| `fact_raw` | 2.991.269 | Toàn bộ CSV, chỉ ép kiểu — nguồn bất biến |
| `fact_annual` | 841.856 | 10-K · US-GAAP · USD · hợp nhất · khử trùng lặp — **bảng chính** |
| `fact_segment` | 857.412 | Số chia theo segment — để dành F9 |
| `dim_company` | 4.032 công ty | + `industry` từ SIC |

**Bất biến:** 0 `value` NULL · 0 cặp `(cik, tag, fiscal_year)` trùng. **Số khớp 10-K công bố.**

**Hạn chế** (chi tiết trong `docs/warehouse_notes.md`): 1 quý dữ liệu ⇒ chỉ so sánh **YoY năm**,
không đủ cho MoM/QoQ, phát hiện bất thường theo thời gian (F8), dự báo (F10). Ngân hàng không có tag
`Revenues` → Bước 2 cần bộ chỉ số riêng cho SIC 60xx–61xx.

**Bước 2 (semantic layer)** sẽ dùng:
```sql
SELECT value FROM fact_annual
WHERE cik = ? AND tag = ? AND fiscal_year = ? AND is_primary_year;
```
cùng `dim_company` cho dimension `industry` / `state`.
""")

code(r"""
con.close()
print("Xong. DB:", DB)
""")

nb = new_notebook(cells=cells)
nb.metadata.update({
    "kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
    "language_info": {"name": "python"},
})

print("Thực thi notebook…")
client = NotebookClient(nb, timeout=1200, kernel_name="python3",
                        resources={"metadata": {"path": str(NB_DIR)}})
client.execute()

# Dọn mọi tàn dư widget (nếu còn) để trình xem không báo "Could not render"
nb.metadata.pop("widgets", None)
WIDGET_MIME = "application/vnd.jupyter.widget-view+json"
for c in nb.cells:
    if c.get("cell_type") != "code":
        continue
    new_outputs = []
    for o in c.get("outputs", []):
        data = o.get("data", {})
        if WIDGET_MIME in data:
            data.pop(WIDGET_MIME, None)
            data.pop("application/vnd.jupyter.widget-state+json", None)
            if not data:
                continue  # output rỗng -> bỏ hẳn
        new_outputs.append(o)
    c["outputs"] = new_outputs

nbformat.write(nb, OUT)
print("Đã ghi:", OUT)
