from typing import Dict, Optional, Literal
from dataclasses import dataclass
from enum import Enum


class Rating(Enum):
    """Các mức xếp hạng khách hàng"""
    A_PLUS = "A+"
    A = "A"
    A_MINUS = "A-"
    B_PLUS = "B+"
    B = "B"
    B_MINUS = "B-"
    C_PLUS = "C+"
    C = "C"
    C_MINUS = "C-"
    D = "D"


@dataclass
class CustomerProfile:
    """Thông tin khách hàng cho Bước 1"""
    tien_an_tien_su: Literal["khong", "vi_pham_gt", "co_trong_20nam", "co_tren_20nam"]
    tuoi: int
    trinh_do_hoc_van: Literal["tren_dai_hoc", "dai_hoc", "trung_hoc", "duoi_trung_hoc"]
    nghe_nghiep: Literal["chuyen_mon", "thu_ky", "kinh_doanh", "nghi_huu"]
    thoi_gian_cong_tac_nam: float
    thoi_gian_cong_viec_hien_tai_nam: float
    tinh_trang_cu_tru: Literal["chu_so_huu", "thue", "o_voi_gia_dinh_khac", "khac"]
    co_cau_gia_dinh: Literal["gia_dinh_hat_nhan", "song_voi_cha_me", "song_cung_1_gd_khac", "song_cung_nhieu_gd_khac"]
    so_nguoi_an_theo: int
    thu_nhap_nam_ca_nhan: float  # triệu đồng
    thu_nhap_nam_gia_dinh: float  # triệu đồng


@dataclass
class CreditProfile:
    """Thông tin tín dụng cho Bước 2"""
    ty_le_no_tren_thu_nhap: float  # %
    tinh_hinh_tra_no: Literal["khong_ap_dung", "chua_qua_han", "qua_han_duoi_30", "qua_han_tren_30"]
    tinh_hinh_cham_tra_lai: Literal["khong_ap_dung", "chua_cham_tra", "khong_cham_trong_2nam", "co_cham_trong_2nam"]
    tong_no_hien_tai: float  # triệu đồng
    dich_vu_ngan_hang: Literal["tiet_kiem", "the", "tiet_kiem_va_the", "khong_co"]
    loai_tai_san_the_chap: Literal["tai_khoan_tien_gui", "bat_dong_san", "xe_co_phieu", "khac"]
    rui_ro_tstc_percent: float  # %
    gia_tri_tstc_tren_von_vay_percent: float  # %


class CustomerRatingSystem:
    """Hệ thống chấm điểm và xếp hạng khách hàng"""

    def __init__(self):
        self.step1_score = 0
        self.step2_score = 0
        self.total_score = 0
        self.rating = None

    def calculate_step1(self, profile: CustomerProfile) -> int:
        """
        Tính điểm Bước 1
        Returns: điểm bước 1 (int)
        """
        score = 0

        # 1. Tiền án, tiền sự
        tien_an_scores = {
            "khong": 25,
            "vi_pham_gt": 20,
            "co_trong_20nam": 0,
            "co_tren_20nam": -15
        }
        score += tien_an_scores[profile.tien_an_tien_su]

        # 2. Tuổi
        if profile.tuoi < 18:
            score += -15
        elif 18 <= profile.tuoi < 25:
            score += 0
        elif 25 <= profile.tuoi <= 55:
            score += 20
        else:  # > 55
            score += 10

        # 3. Trình độ học vấn
        hoc_van_scores = {
            "tren_dai_hoc": 20,
            "dai_hoc": 15,
            "trung_hoc": 5,
            "duoi_trung_hoc": -5
        }
        score += hoc_van_scores[profile.trinh_do_hoc_van]

        # 4. Nghề nghiệp
        nghe_nghiep_scores = {
            "chuyen_mon": 25,
            "thu_ky": 15,
            "kinh_doanh": 5,
            "nghi_huu": 0
        }
        score += nghe_nghiep_scores[profile.nghe_nghiep]

        # 5. Thời gian công tác
        if profile.thoi_gian_cong_tac_nam < 0.5:
            score += 5
        elif 0.5 <= profile.thoi_gian_cong_tac_nam < 1:
            score += 10
        elif 1 <= profile.thoi_gian_cong_tac_nam < 5:
            score += 15
        else:  # >= 5
            score += 20

        # 6. Thời gian làm công việc hiện tại
        if profile.thoi_gian_cong_viec_hien_tai_nam < 0.5:
            score += 5
        elif 0.5 <= profile.thoi_gian_cong_viec_hien_tai_nam < 1:
            score += 10
        elif 1 <= profile.thoi_gian_cong_viec_hien_tai_nam < 5:
            score += 15
        else:  # >= 5
            score += 20

        # 7. Tình trạng cư trú
        cu_tru_scores = {
            "chu_so_huu": 30,
            "thue": 12,
            "o_voi_gia_dinh_khac": 5,
            "khac": 0
        }
        score += cu_tru_scores[profile.tinh_trang_cu_tru]

        # 8. Cơ cấu gia đình
        gia_dinh_scores = {
            "gia_dinh_hat_nhan": 20,
            "song_voi_cha_me": 5,
            "song_cung_1_gd_khac": 0,
            "song_cung_nhieu_gd_khac": -5
        }
        score += gia_dinh_scores[profile.co_cau_gia_dinh]

        # 9. Số người ăn theo
        if profile.so_nguoi_an_theo == 0:
            score += 0
        elif profile.so_nguoi_an_theo < 3:
            score += 10
        elif 3 <= profile.so_nguoi_an_theo <= 5:
            score += 5
        else:  # > 5
            score += -5

        # 10. Thu nhập hàng năm cá nhân
        if profile.thu_nhap_nam_ca_nhan > 120:
            score += 30
        elif 36 <= profile.thu_nhap_nam_ca_nhan <= 120:
            score += 20
        elif 12 <= profile.thu_nhap_nam_ca_nhan < 36:
            score += 5
        else:  # < 12
            score += -5

        # 11. Thu nhập hàng năm gia đình
        if profile.thu_nhap_nam_gia_dinh > 240:
            score += 30
        elif 72 <= profile.thu_nhap_nam_gia_dinh <= 240:
            score += 20
        elif 24 <= profile.thu_nhap_nam_gia_dinh < 72:
            score += 5
        else:  # < 24
            score += -5

        self.step1_score = score
        return score

    def calculate_step2(self, credit: CreditProfile) -> int:
        """
        Tính điểm Bước 2
        Returns: điểm bước 2 (int)
        """
        score = 0

        # 1. Tỷ trọng vay vốn
        if credit.ty_le_no_tren_thu_nhap == 0:
            score += 25
        elif 0 < credit.ty_le_no_tren_thu_nhap <= 20:
            score += 10
        elif 20 < credit.ty_le_no_tren_thu_nhap <= 50:
            score += 5
        else:  # > 50
            score += -5

        # 2. Tình hình trả nợ
        tra_no_scores = {
            "khong_ap_dung": 0,
            "chua_qua_han": 25,
            "qua_han_duoi_30": 0,
            "qua_han_tren_30": -5
        }
        score += tra_no_scores[credit.tinh_hinh_tra_no]

        # 3. Tình hình chậm trả lãi
        cham_tra_scores = {
            "khong_ap_dung": 0,
            "chua_cham_tra": 20,
            "khong_cham_trong_2nam": 5,
            "co_cham_trong_2nam": -5
        }
        score += cham_tra_scores[credit.tinh_hinh_cham_tra_lai]

        # 4. Tổng nợ hiện tại
        if credit.tong_no_hien_tai < 100:
            score += 25
        elif 100 <= credit.tong_no_hien_tai < 500:
            score += 10
        elif 500 <= credit.tong_no_hien_tai < 1000:
            score += 5
        else:  # >= 1000
            score += -5

        # 5. Các dịch vụ sử dụng
        dich_vu_scores = {
            "tiet_kiem": 15,
            "the": 5,
            "tiet_kiem_va_the": 25,
            "khong_co": -5
        }
        score += dich_vu_scores[credit.dich_vu_ngan_hang]

        # 6. Loại tài sản thế chấp
        tstc_scores = {
            "tai_khoan_tien_gui": 25,
            "bat_dong_san": 20,
            "xe_co_phieu": 10,
            "khac": 5
        }
        score += tstc_scores[credit.loai_tai_san_the_chap]

        # 7. Rủi ro TSTC
        if credit.rui_ro_tstc_percent == 0:
            score += 25
        elif 1 <= credit.rui_ro_tstc_percent <= 20:
            score += 5
        elif 21 <= credit.rui_ro_tstc_percent <= 50:
            score += 0
        else:  # > 50
            score += -20

        # 8. Giá trị TSTC so với vốn vay
        if credit.gia_tri_tstc_tren_von_vay_percent > 150:
            score += 20
        elif 120 <= credit.gia_tri_tstc_tren_von_vay_percent <= 150:
            score += 10
        elif 100 <= credit.gia_tri_tstc_tren_von_vay_percent < 120:
            score += 5
        else:  # < 100
            score += -5

        self.step2_score = score
        return score

    def get_rating(self, total_score: int) -> Rating:
        """Xác định xếp hạng dựa trên tổng điểm"""
        if total_score >= 392:
            return Rating.A_PLUS
        elif total_score >= 343:
            return Rating.A
        elif total_score >= 294:
            return Rating.A_MINUS
        elif total_score >= 245:
            return Rating.B_PLUS
        elif total_score >= 196:
            return Rating.B
        elif total_score >= 147:
            return Rating.B_MINUS
        elif total_score >= 98:
            return Rating.C_PLUS
        elif total_score >= 49:
            return Rating.C
        elif total_score >= 0:
            return Rating.C_MINUS
        else:
            return Rating.D

    def evaluate_customer(
            self,
            profile: CustomerProfile,
            credit: Optional[CreditProfile] = None
    ) -> Dict:
        """
        Đánh giá khách hàng qua 2 bước

        Returns:
            Dict chứa kết quả đánh giá
        """
        # Bước 1
        step1_score = self.calculate_step1(profile)

        result = {
            "step1_score": step1_score,
            "step1_passed": step1_score >= 0,
            "step2_score": None,
            "total_score": None,
            "rating": None,
            "approved": False,
            "message": ""
        }

        # Kiểm tra điều kiện Bước 1
        if step1_score < 0:
            result["message"] = f"Từ chối: Điểm Bước 1 ({step1_score}) < 0"
            result["total_score"] = step1_score
            result["rating"] = Rating.D.value
            return result

        # Bước 2
        if credit is None:
            result["message"] = "Cần thông tin tín dụng để tiếp tục Bước 2"
            return result

        step2_score = self.calculate_step2(credit)
        total_score = step1_score + step2_score
        rating = self.get_rating(total_score)

        result.update({
            "step2_score": step2_score,
            "total_score": total_score,
            "rating": rating.value,
            "approved": total_score >= 0,
            "message": f"Xếp hạng: {rating.value} với tổng điểm {total_score}"
        })

        self.total_score = total_score
        self.rating = rating

        return result


# ==================== DEMO USAGE ====================
# if __name__ == "__main__":
#     # Ví dụ 1: Khách hàng tốt
#     print("=" * 60)
#     print("VÍ DỤ 1: KHÁCH HÀNG TỐT")
#     print("=" * 60)
#
#     customer1 = CustomerProfile(
#         tien_an_tien_su="khong",
#         tuoi=35,
#         trinh_do_hoc_van="dai_hoc",
#         nghe_nghiep="chuyen_mon",
#         thoi_gian_cong_tac_nam=8,
#         thoi_gian_cong_viec_hien_tai_nam=6,
#         tinh_trang_cu_tru="chu_so_huu",
#         co_cau_gia_dinh="gia_dinh_hat_nhan",
#         so_nguoi_an_theo=2,
#         thu_nhap_nam_ca_nhan=150,
#         thu_nhap_nam_gia_dinh=300
#     )
#
#     credit1 = CreditProfile(
#         ty_le_no_tren_thu_nhap=15,
#         tinh_hinh_tra_no="chua_qua_han",
#         tinh_hinh_cham_tra_lai="chua_cham_tra",
#         tong_no_hien_tai=80,
#         dich_vu_ngan_hang="tiet_kiem_va_the",
#         loai_tai_san_the_chap="bat_dong_san",
#         rui_ro_tstc_percent=5,
#         gia_tri_tstc_tren_von_vay_percent=160
#     )
#
#     system = CustomerRatingSystem()
#     result1 = system.evaluate_customer(customer1, credit1)
#
#     print(f"Điểm Bước 1: {result1['step1_score']}")
#     print(f"Điểm Bước 2: {result1['step2_score']}")
#     print(f"Tổng điểm: {result1['total_score']}")
#     print(f"Xếp hạng: {result1['rating']}")
#     print(f"Kết quả: {result1['message']}")
#
#     # Ví dụ 2: Khách hàng bị từ chối
#     print("\n" + "=" * 60)
#     print("VÍ DỤ 2: KHÁCH HÀNG BỊ TỪ CHỐI (Bước 1)")
#     print("=" * 60)
#
#     customer2 = CustomerProfile(
#         tien_an_tien_su="co_trong_20nam",
#         tuoi=22,
#         trinh_do_hoc_van="duoi_trung_hoc",
#         nghe_nghiep="kinh_doanh",
#         thoi_gian_cong_tac_nam=0.3,
#         thoi_gian_cong_viec_hien_tai_nam=0.2,
#         tinh_trang_cu_tru="thue",
#         co_cau_gia_dinh="song_cung_nhieu_gd_khac",
#         so_nguoi_an_theo=6,
#         thu_nhap_nam_ca_nhan=10,
#         thu_nhap_nam_gia_dinh=20
#     )
#
#     system2 = CustomerRatingSystem()
#     result2 = system2.evaluate_customer(customer2)
#
#     print(f"Điểm Bước 1: {result2['step1_score']}")
#     print(f"Kết quả: {result2['message']}")
#
#     # Ví dụ 3: Khách hàng trung bình
#     print("\n" + "=" * 60)
#     print("VÍ DỤ 3: KHÁCH HÀNG TRUNG BÌNH")
#     print("=" * 60)
#
#     customer3 = CustomerProfile(
#         tien_an_tien_su="vi_pham_gt",
#         tuoi=28,
#         trinh_do_hoc_van="trung_hoc",
#         nghe_nghiep="thu_ky",
#         thoi_gian_cong_tac_nam=3,
#         thoi_gian_cong_viec_hien_tai_nam=2,
#         tinh_trang_cu_tru="thue",
#         co_cau_gia_dinh="song_voi_cha_me",
#         so_nguoi_an_theo=1,
#         thu_nhap_nam_ca_nhan=40,
#         thu_nhap_nam_gia_dinh=100
#     )
#
#     credit3 = CreditProfile(
#         ty_le_no_tren_thu_nhap=35,
#         tinh_hinh_tra_no="qua_han_duoi_30",
#         tinh_hinh_cham_tra_lai="khong_cham_trong_2nam",
#         tong_no_hien_tai=200,
#         dich_vu_ngan_hang="the",
#         loai_tai_san_the_chap="xe_co_phieu",
#         rui_ro_tstc_percent=25,
#         gia_tri_tstc_tren_von_vay_percent=115
#     )
#
#     system3 = CustomerRatingSystem()
#     result3 = system3.evaluate_customer(customer3, credit3)
#
#     print(f"Điểm Bước 1: {result3['step1_score']}")
#     print(f"Điểm Bước 2: {result3['step2_score']}")
#     print(f"Tổng điểm: {result3['total_score']}")
#     print(f"Xếp hạng: {result3['rating']}")
#     print(f"Kết quả: {result3['message']}")