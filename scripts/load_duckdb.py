"""Bước 1 — Nạp file SEC EDGAR 2020Q1 đã clean vào DuckDB + dựng view sạch.

Chạy:  python scripts/load_duckdb.py
       python scripts/load_duckdb.py --csv <path> --db <path>

Tạo (idempotent, drop + create lại):
  fact_raw      -- toàn bộ CSV, chỉ ép kiểu, KHÔNG lọc. Nguồn bất biến để tái lập.
  fact_annual   -- số hợp nhất năm, US-GAAP, USD, đã khử trùng lặp. Bảng chính cho demo.
  fact_segment  -- số chia theo segment (giữ cho F9 - phân rã, dùng sau).
  dim_company   -- 1 dòng / công ty, kèm nhãn ngành tiếng Việt từ mã SIC.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import duckdb

for _s in (sys.stdout, sys.stderr):  # console Windows mặc định cp1252 -> ép UTF-8
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sic_labels import sic_label  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "Clean" / "num_sub_tag_clean_2020q1.csv"
DEFAULT_DB = ROOT / "Data" / "warehouse.duckdb"

# Danh sách tag ưu tiên cho vài chỉ số - CHỈ dùng để kiểm tra tỉnh táo ở bước này.
# Bộ đầy đủ sẽ nằm trong semantic/metrics.yml ở Bước 2.
CHECK_METRICS = {
    "revenue": [
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
    ],
    "net_income": ["NetIncomeLoss", "ProfitLoss"],
    "total_assets": ["Assets"],
    "equity": [
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    ],
}

# cik -> (tên, có nên xuất hiện trong fact_annual?, ghi chú đối chiếu 10-K công khai)
# Chỉ công ty có năm tài chính kết thúc ~31/12 và nộp 10-K trong quý I dương lịch
# mới có mặt trong bộ 2020Q1. Apple/Microsoft chỉ nộp 10-Q trong quý này -> vắng là ĐÚNG.
KNOWN = {
    "1018724": ("AMAZON COM INC", True, "FY2019: doanh thu ~280,52 tỷ; LNST ~11,59 tỷ; tổng TS ~225,25 tỷ"),
    "1652044": ("ALPHABET INC", True, "FY2019: doanh thu ~161,86 tỷ; LNST ~34,34 tỷ; tổng TS ~275,91 tỷ"),
    "34088": ("EXXON MOBIL CORP", True, "FY2019: doanh thu ~264,94 tỷ; LNST ~14,34 tỷ; tổng TS ~362,60 tỷ"),
    "21344": ("COCA-COLA CO", True, "FY2019: doanh thu ~37,27 tỷ; LNST ~8,92 tỷ; tổng TS ~86,38 tỷ"),
    "19617": ("JPMORGAN CHASE & CO", True, "FY2019: LNST ~36,43 tỷ; tổng TS ~2.687 tỷ"),
    "320193": ("APPLE INC", False, "FYE 28/09 - trong 2020Q1 chỉ có 10-Q, không có 10-K"),
    "789019": ("MICROSOFT CORP", False, "FYE 30/06 - trong 2020Q1 chỉ có 10-Q, không có 10-K"),
}


def build(con: duckdb.DuckDBPyConnection, csv_path: Path) -> None:
    csv_sql = str(csv_path).replace("\\", "/")

    print(f"[1/5] Nạp CSV -> fact_raw  ({csv_path.name}, ~831 MB, ~3M dòng)…")
    con.execute("DROP TABLE IF EXISTS fact_raw")
    con.execute(
        f"""
        CREATE TABLE fact_raw AS
        SELECT
            adsh, cik, name, sic,
            countryba, stprba, countryinc,
            form,
            TRY_CAST(fy AS INTEGER)                    AS fy,
            fp,
            TRY_CAST(strptime(period, '%Y%m%d') AS DATE) AS period,
            fye, afs, wksi,
            TRY_CAST(strptime(filed, '%Y%m%d') AS DATE)  AS filed,
            prevrpt, detail,
            tag, tlabel, version, custom, datatype, iord, crdr,
            TRY_CAST(strptime(ddate, '%Y%m%d') AS DATE)  AS ddate,
            TRY_CAST(qtrs AS INTEGER)                  AS qtrs,
            uom,
            NULLIF(segments, '')                       AS segments,
            NULLIF(coreg, '')                          AS coreg,
            TRY_CAST(value AS DOUBLE)                  AS value,
            footnote,
            TRY_CAST(is_consolidated AS INTEGER)       AS is_consolidated
        FROM read_csv('{csv_sql}', all_varchar = true, header = true)
        """
    )

    print("[2/5] Dựng fact_annual (10-K, US-GAAP, USD, hợp nhất, đã khử trùng lặp)…")
    con.execute("DROP TABLE IF EXISTS fact_annual")
    con.execute(
        """
        CREATE TABLE fact_annual AS
        WITH base AS (
            SELECT
                r.cik,
                r.name                                  AS company_name,
                r.sic,
                r.stprba                                AS state,
                r.countryinc,
                r.adsh,
                r.form,
                r.filed,
                r.fy                                    AS filing_fy,
                r.period                                AS filing_period,
                r.tag,
                r.tlabel,
                r.iord,
                r.crdr,
                r.ddate,
                r.qtrs,
                CAST(year(r.ddate) AS INTEGER)          AS fiscal_year,
                (year(r.ddate) = year(r.period))        AS is_primary_year,
                r.value
            FROM fact_raw r
            WHERE r.form IN ('10-K', '10-K/A')
              AND r.uom = 'USD'
              AND r.custom = '0'
              AND r.version LIKE 'us-gaap/%'
              AND r.coreg IS NULL
              AND r.segments IS NULL
              AND r.value IS NOT NULL
              AND r.ddate IS NOT NULL
              AND ( (r.iord = 'I' AND r.qtrs = 0)
                 OR (r.iord = 'D' AND r.qtrs = 4) )
              AND year(r.ddate) BETWEEN 2016 AND 2021
        )
        SELECT *
        FROM base
        QUALIFY row_number() OVER (
            PARTITION BY cik, tag, fiscal_year
            ORDER BY filed DESC, adsh DESC
        ) = 1
        """
    )

    print("[3/5] Dựng fact_segment (số chia theo segment - để dành cho F9)…")
    con.execute("DROP TABLE IF EXISTS fact_segment")
    con.execute(
        """
        CREATE TABLE fact_segment AS
        SELECT
            r.cik,
            r.name                          AS company_name,
            r.sic,
            r.stprba                        AS state,
            r.adsh,
            r.filed,
            r.tag,
            r.tlabel,
            r.iord,
            r.ddate,
            CAST(year(r.ddate) AS INTEGER)  AS fiscal_year,
            r.qtrs,
            r.segments,
            r.value
        FROM fact_raw r
        WHERE r.form IN ('10-K', '10-K/A')
          AND r.uom = 'USD'
          AND r.custom = '0'
          AND r.version LIKE 'us-gaap/%'
          AND r.coreg IS NULL
          AND r.segments IS NOT NULL
          AND r.value IS NOT NULL
          AND r.ddate IS NOT NULL
          AND ( (r.iord = 'I' AND r.qtrs = 0)
             OR (r.iord = 'D' AND r.qtrs = 4) )
          AND year(r.ddate) BETWEEN 2016 AND 2021
        """
    )

    print("[4/5] Dựng dim_company (+ nhãn ngành tiếng Việt từ SIC)…")
    con.execute("DROP TABLE IF EXISTS dim_company")
    con.execute(
        """
        CREATE TABLE dim_company AS
        SELECT
            r.cik,
            mode(r.name)       AS company_name,
            mode(r.sic)        AS sic,
            mode(r.stprba)     AS state,
            mode(r.countryinc) AS country_inc
        FROM fact_raw r
        WHERE r.cik IN (SELECT DISTINCT cik FROM fact_annual)
        GROUP BY r.cik
        """
    )
    df = con.execute("SELECT * FROM dim_company").fetchdf()
    df["industry"] = df["sic"].map(sic_label)
    con.execute("DROP TABLE IF EXISTS dim_company")
    con.register("dim_company_df", df)
    con.execute("CREATE TABLE dim_company AS SELECT * FROM dim_company_df")
    con.unregister("dim_company_df")

    print("[5/5] Xong dựng bảng.\n")


def validate(con: duckdb.DuckDBPyConnection) -> bool:
    ok = True
    q = con.execute

    n_raw = q("SELECT count(*) FROM fact_raw").fetchone()[0]
    n_ann = q("SELECT count(*) FROM fact_annual").fetchone()[0]
    n_seg = q("SELECT count(*) FROM fact_segment").fetchone()[0]
    n_co = q("SELECT count(*) FROM dim_company").fetchone()[0]
    print("=== ĐẾM DÒNG ===")
    print(f"  fact_raw     : {n_raw:>10,}")
    print(f"  fact_annual  : {n_ann:>10,}")
    print(f"  fact_segment : {n_seg:>10,}")
    print(f"  dim_company  : {n_co:>10,} công ty")

    print("\n=== CÔNG TY: GIỮ vs LOẠI ===")
    raw_co = q("SELECT count(DISTINCT cik) FROM fact_raw").fetchone()[0]
    co_10k = q(
        "SELECT count(DISTINCT cik) FROM fact_raw WHERE form IN ('10-K','10-K/A')"
    ).fetchone()[0]
    co_foreign_only = q(
        """SELECT count(DISTINCT cik) FROM fact_raw
           WHERE cik NOT IN (SELECT cik FROM fact_raw WHERE form IN ('10-K','10-K/A'))"""
    ).fetchone()[0]
    co_ifrs = q(
        "SELECT count(DISTINCT cik) FROM fact_raw WHERE version LIKE 'ifrs/%'"
    ).fetchone()[0]
    print(f"  Tổng công ty trong fact_raw                 : {raw_co:>6,}")
    print(f"  Có nộp 10-K / 10-K/A                        : {co_10k:>6,}")
    print(f"  Giữ lại trong fact_annual                   : {n_co:>6,}")
    print(f"  10-K bị loại (không có dòng US-GAAP/USD/năm): {co_10k - n_co:>6,}")
    print(f"  Chỉ nộp form nước ngoài, không có 10-K      : {co_foreign_only:>6,}")
    print(f"  (thông tin) công ty có tag IFRS             : {co_ifrs:>6,}")

    print("\n=== BẤT BIẾN (phải đạt) ===")
    n_null = q("SELECT count(*) FROM fact_annual WHERE value IS NULL").fetchone()[0]
    n_dup = q(
        """SELECT count(*) FROM (
               SELECT cik, tag, fiscal_year, count(*) c
               FROM fact_annual GROUP BY 1,2,3 HAVING count(*) > 1)"""
    ).fetchone()[0]
    print(f"  value NULL trong fact_annual         : {n_null}  ({'OK' if n_null == 0 else 'LỖI'})")
    print(f"  Trùng (cik, tag, fiscal_year)        : {n_dup}  ({'OK' if n_dup == 0 else 'LỖI'})")
    ok = ok and n_null == 0 and n_dup == 0

    print("\n=== PHÂN BỐ fiscal_year (fact_annual) ===")
    for yr, c, nco in q(
        """SELECT fiscal_year, count(*) AS n_rows, count(DISTINCT cik) AS n_co
           FROM fact_annual GROUP BY 1 ORDER BY 1"""
    ).fetchall():
        print(f"  {yr}: {c:>9,} dòng   {nco:>6,} công ty")

    print("\n=== ĐỐI CHIẾU CÔNG TY LỚN (fact_annual, tag ưu tiên) ===")
    case_parts = []
    for m, tags in CHECK_METRICS.items():
        tlist = ", ".join(f"'{t}'" for t in tags)
        prio = "\n        ".join(
            f"WHEN tag = '{t}' THEN {i}" for i, t in enumerate(tags)
        )
        case_parts.append((m, tlist, prio))

    for cik, (nm, expect, note) in KNOWN.items():
        rows = q(f"SELECT count(*) FROM fact_annual WHERE cik = '{cik}'").fetchone()[0]
        if rows == 0:
            mark = "OK (đúng như dự kiến)" if not expect else "❌ BẤT NGỜ - cần xem lại"
            print(f"  [{cik}] {nm}: vắng mặt — {mark}")
            print(f"        {note}")
            if expect:
                ok = False
            continue
        if not expect:
            print(f"  [{cik}] {nm}: ❌ CÓ MẶT nhưng lẽ ra phải vắng — {note}")
            ok = False
            continue
        print(f"  [{cik}] {nm}")
        print(f"        đối chiếu: {note}")
        for m, tlist, prio in case_parts:
            res = q(
                f"""
                SELECT fiscal_year, value FROM (
                    SELECT fiscal_year, value,
                           row_number() OVER (PARTITION BY fiscal_year
                               ORDER BY CASE {prio} ELSE 99 END) rn
                    FROM fact_annual
                    WHERE cik = '{cik}' AND tag IN ({tlist})
                ) WHERE rn = 1 ORDER BY fiscal_year
                """
            ).fetchall()
            cells = "   ".join(f"{yr}={val/1e9:,.2f} tỷ" for yr, val in res) or "(không có)"
            print(f"        {m:<13}: {cells}")
        print()

    print("=== KẾT LUẬN ===")
    print("  " + ("✅ Bước 1 đạt mọi bất biến." if ok else "❌ Có bất biến KHÔNG đạt - xem log trên."))
    return ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    ap.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = ap.parse_args()

    if not args.csv.exists():
        print(f"Không thấy CSV: {args.csv}", file=sys.stderr)
        return 2

    args.db.parent.mkdir(parents=True, exist_ok=True)
    print(f"CSV : {args.csv}")
    print(f"DB  : {args.db}\n")

    con = duckdb.connect(str(args.db))
    try:
        build(con, args.csv)
        ok = validate(con)
    finally:
        con.close()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
