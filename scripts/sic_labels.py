"""Ánh xạ mã SIC -> nhãn ngành đọc được (tiếng Việt).

Không nhập toàn bộ danh mục SIC. Chỉ gồm:
  - ~40 mã 4 chữ số phổ biến nhất trong file 2020Q1
  - fallback theo division (nhóm 2 chữ số đầu) cho phần còn lại
"""

SIC_4 = {
    "0000": "Không phân loại",
    "1000": "Khai khoáng kim loại",
    "1311": "Khai thác dầu khí",
    "1381": "Dịch vụ khoan dầu khí",
    "1531": "Xây dựng nhà ở",
    "2000": "Chế biến thực phẩm",
    "2080": "Đồ uống",
    "2834": "Dược phẩm",
    "2835": "Chẩn đoán y sinh (in-vitro/in-vivo)",
    "2836": "Sản phẩm sinh học",
    "2911": "Lọc hóa dầu",
    "3559": "Thiết bị công nghiệp chuyên dụng",
    "3576": "Thiết bị mạng máy tính",
    "3600": "Thiết bị điện & điện tử",
    "3674": "Bán dẫn",
    "3711": "Sản xuất ô tô",
    "3826": "Thiết bị đo lường & phân tích",
    "3841": "Thiết bị y tế & phẫu thuật",
    "4813": "Viễn thông",
    "4911": "Điện lực",
    "4931": "Điện & khí đốt",
    "5122": "Bán buôn dược phẩm",
    "5812": "Nhà hàng - dịch vụ ăn uống",
    "5912": "Bán lẻ dược phẩm",
    "6021": "Ngân hàng thương mại quốc gia",
    "6022": "Ngân hàng thương mại bang",
    "6035": "Tổ chức tiết kiệm",
    "6141": "Cho vay tiêu dùng",
    "6189": "Chứng khoán hóa tài sản",
    "6199": "Dịch vụ tài chính",
    "6221": "Môi giới hàng hóa",
    "6270": "Công ty đầu tư (holding)",
    "6282": "Tư vấn đầu tư",
    "6311": "Bảo hiểm nhân thọ",
    "6331": "Bảo hiểm tài sản & tai nạn",
    "6500": "Bất động sản",
    "6770": "Công ty séc trắng (SPAC)",
    "6798": "Quỹ tín thác bất động sản (REIT)",
    "7011": "Khách sạn - lưu trú",
    "7370": "Dịch vụ máy tính & xử lý dữ liệu",
    "7372": "Phần mềm đóng gói",
    "7374": "Xử lý dữ liệu & lưu trữ",
    "7389": "Dịch vụ CNTT & lập trình",
    "8000": "Dịch vụ y tế",
    "8731": "Nghiên cứu & phát triển thương mại",
}

# division theo dải mã (chuẩn SIC của Mỹ)
DIVISIONS = [
    (100, 999, "Nông - lâm - ngư nghiệp"),
    (1000, 1499, "Khai khoáng"),
    (1500, 1799, "Xây dựng"),
    (2000, 3999, "Sản xuất - chế tạo"),
    (4000, 4999, "Vận tải & dịch vụ công ích"),
    (5000, 5199, "Bán buôn"),
    (5200, 5999, "Bán lẻ"),
    (6000, 6799, "Tài chính - bảo hiểm - bất động sản"),
    (7000, 8999, "Dịch vụ"),
    (9100, 9999, "Hành chính công"),
]


def sic_label(sic) -> str:
    if sic is None or str(sic).strip() in ("", "nan", "None"):
        return "Không rõ ngành"
    s = str(sic).strip()
    if s.isdigit():
        s = s.zfill(4)
    if s in SIC_4:
        return SIC_4[s]
    try:
        n = int(s)
    except ValueError:
        return "Không rõ ngành"
    for lo, hi, name in DIVISIONS:
        if lo <= n <= hi:
            return name
    return "Không rõ ngành"
