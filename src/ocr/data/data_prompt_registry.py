SECURITIES_FINANCIAL_STATEMENT_PROMPT = """
Từ file PDF báo cáo tình hình tài chính đã gửi lên, trong đó các trang là bộ phận hợp thành của một bảng báo cáo tài chính lớn duy nhất, hãy trích xuất dữ liệu của bảng đó thành định dạng JSON.

YÊU CẦU CẤU TRÚC JSON:
1. Sử dụng giá trị tại ngày cuối kỳ (ngày có giá trị lớn nhất, thường là 31/12/YYYY hoặc Số cuối năm/Số đầu năm).
2. Chuyển đổi tất cả các giá trị số sang dạng số nguyên (integer/number), loại bỏ dấu phân cách hàng nghìn. Giá trị của toàn bộ ô trong ngoặc "()" được chuyển thành số âm. Giá trị của toàn bộ ô là "-" được chuyển thành null.
3. Mỗi đối tượng JSON (object) phải có 3 attributes:
   - "description": Tên mục tiếng Việt nguyên bản từ cột CHỈ TIÊU/Danh mục, loại bỏ hoàn toàn phần công thức tính toán (ví dụ: "(100=110+130)", "(200=210+220+250)", "(400=410)", v.v.).
   - "name": Tên tiếng Anh chuẩn hóa theo BẢNG ÁNH XẠ bên dưới (sử dụng snake_case).
   - "value": Giá trị số cuối cùng đã được chuyển đổi tại ngày cuối kỳ (integer hoặc null).
4. Câu trả lời CHỈ TRẢ VỀ JSON HỢP LỆ dưới dạng array of objects, KHÔNG CÓ giải thích, markdown, hoặc text nào khác.

BẢNG ÁNH XẠ TÊN THUỘC TÍNH (name):
Ánh xạ các tên tiếng Việt từ báo cáo (có thể khác nhau giữa các đơn vị kiểm toán) sang tên chuẩn tiếng Anh. Áp dụng nguyên tắc: nếu gặp các biến thể từ ngữ có cùng ngữ nghĩa, hãy sử dụng tên chuẩn tương ứng.

TÀI SẢN NGẮN HẠN:
- "Tài sản ngắn hạn" / "TÀI SẢN NGẮN HẠN" / "A. TÀI SẢN NGẮN HẠN" → short_term_assets
- "Tài sản tài chính" / "Tài sản tài chính ngắn hạn" / "I. Tài sản tài chính" → current_financial_assets
- "Tiền và các khoản tương đương tiền" → cash_and_cash_equivalents
- "Tiền" → cash
- "Các khoản tương đương tiền" → cash_equivalents
- "Các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL)" / "Các tài sản tài chính ('TSTC') ghi nhận thông qua lãi/lỗ" / "Các khoản đầu tư nắm giữ đến ngày đáo hạn (HTM)" khi nằm trong FVTPL → financial_assets_recognized_through_p_and_l_at_fvtpl
- "Các khoản đầu tư nắm giữ đến ngày đáo hạn (HTM)" / "Các khoản đầu tư nắm giữ đến ngày đáo hạn" → held_to_maturity_investment_securities
- "Các khoản cho vay" / "Cho vay" → loans
- "Dự phòng suy giảm giá trị các tài sản tài chính và tài sản thế chấp" / "Dự phòng suy giảm giá trị các TSTC và tài sản thế chấp" → provision_for_impairment_of_financial_assets_and_pledged_assets
- "Các khoản phải thu" / "Phải thu" → receivables
- "Phải thu và dự thu cổ tức, tiền lãi các tài sản tài chính" / "Phải thu lãi và dự thu có ứớc, tiền lãi các tài sản tài chính" → interest_and_fee_receivables
- "Phải thu có ứớc, tiền lãi đến ngày nhận" / "Dự thu có ứớc, lãi chưa đến ngày nhận" (khi đã đến hạn) → interest_and_fee_receivables_due
- "Phải thu có ứớc, tiền lãi chưa đến ngày nhận" / "Dự thu có ứớc, lãi chưa đến ngày nhận" → interest_and_fee_receivables_not_yet_due
- "Trả trước cho người bán" / "Tạm ứng" → advances_to_vendors
- "Phải thu các dịch vụ công ty chứng khoán cung cấp" → service_fee_receivables_from_companies_and_securities_clearing
- "Các khoản phải thu khác" → other_receivables
- "Tài sản ngắn hạn khác" / "II. Tài sản ngắn hạn khác" → other_short_term_assets
- "Chi phí trả trước ngắn hạn" / "Chi phí trả trước" → prepaid_expenses
- "Chi phí trả trước ngắn hạn" (khi tách riêng) → short_term_prepaid_expenses
- "Cầm cố, thế chấp, ký quỹ, ký cược ngắn hạn" / "Vật tư văn phòng, công cụ, dụng cụ" → short_term_deposits_pledges_and_guarantees

TÀI SẢN DÀI HẠN:
- "Tài sản dài hạn" / "TÀI SẢN DÀI HẠN" / "B. TÀI SẢN DÀI HẠN" → long_term_assets
- "Tài sản tài chính dài hạn" / "I. Tài sản tài chính dài hạn" → long_term_financial_assets
- "Các khoản đầu tư" / "Đầu tư vào công ty liên doanh, liên kết" → investments
- "Các khoản đầu tư nắm giữ đến ngày đáo hạn" (trong phần dài hạn) → held_to_maturity_investments
- "Tài sản cố định" / "II. Tài sản cố định" → fixed_assets
- "Tài sản cố định hữu hình" / "Nguyên giá" (TSCĐ hữu hình) → tangible_fixed_assets
- "Nguyên giá" (của TSCĐ hữu hình) → tangible_fixed_assets_cost
- "Giá trị hao mòn lũy kế" (của TSCĐ hữu hình) → tangible_fixed_assets_accumulated_depreciation
- "Tài sản cố định vô hình" / "Nguyên giá" (TSCĐ vô hình) → intangible_fixed_assets
- "Nguyên giá" (của TSCĐ vô hình) → intangible_fixed_assets_cost
- "Giá trị hao mòn lũy kế" (của TSCĐ vô hình) → intangible_fixed_assets_accumulated_amortization
- "Tài sản dài hạn khác" / "V. Tài sản dài hạn khác" → other_long_term_assets
- "Cầm cố, thế chấp, ký quỹ, ký cược dài hạn" → long_term_deposits_pledges_and_guarantees
- "Chi phí trả trước dài hạn" → long_term_prepaid_expenses
- "Thuế thu nhập hoãn lại phải thu" / "Tài sản thuế thu nhập hoãn lại" → deferred_tax_assets
- "Tiền nộp Quỹ Hỗ trợ thanh toán" → support_fund_contribution

TỔNG TÀI SẢN:
- "Tổng cộng tài sản" / "TỔNG TÀI SẢN" / "TỔNG CỘNG TÀI SẢN" → total_assets

NỢ PHẢI TRẢ:
- "Nợ phải trả" / "NỢ PHẢI TRẢ" / "C. NỢ PHẢI TRẢ" → liabilities
- "Nợ phải trả ngắn hạn" / "I. Nợ phải trả ngắn hạn" → short_term_liabilities
- "Vay và nợ thuê tài sản tài chính ngắn hạn" / "Vay ngắn hạn" / "Vay và nợ thuê TSTC ngắn hạn" → short_term_borrowings_and_financial_lease_liabilities
- "Vay ngắn hạn" (riêng) → short_term_borrowings
- "Trái phiếu phát hành ngắn hạn" → bonds_issued
- "Phải trả hoạt động giao dịch chứng khoán" → payables_for_securities_trading_activities
- "Phải trả người bán ngắn hạn" → payables_for_securities_purchases
- "Người mua trả tiền trước ngắn hạn" → advances_from_customers
- "Thuế và các khoản phải nộp Nhà nước" → tax_and_other_payables_to_state_budget
- "Phải trả người lao động" / "Người mua trả tiền trước ngắn hạn" → employee_benefits_payable
- "Chi phí phải trả ngắn hạn" (tổng hợp) → accrued_expenses
- "Chi phí phải trả ngắn hạn" (tiền lãi) → short_term_interest_payable
- "Các khoản phải trả, phải nộp khác ngắn hạn" / "Các khoản trích nộp phúc lợi nhân viên" → other_short_term_payables
- "Quỹ khen thưởng, phúc lợi" → bonus_and_welfare_fund
- "Nợ phải trả dài hạn" / "II. Nợ phải trả dài hạn" → long_term_liabilities
- "Thuế thu nhập hoãn lại phải trả" / "Doanh thu chưa thực hiện dài hạn" → deferred_income_tax_payable

VỐN CHỦ SỞ HỮU:
- "Vốn chủ sở hữu" / "VỐN CHỦ SỞ HỮU" / "D. VỐN CHỦ SỞ HỮU" → owners_equity
- "Vốn chủ sở hữu" (chi tiết) / "Vốn đầu tư của chủ sở hữu" / "I. Vốn chủ sở hữu" → owners_capital
- "Vốn góp của chủ sở hữu" / "Cổ phiếu phổ thông có quyền biểu quyết" → contributed_capital
- "Cổ phiếu phổ thông cổ quyền biểu quyết" / "Cổ phiếu dạng lưu hành (số lượng)" → ordinary_share_capital_authorized_and_issued
- "Thặng dư vốn cổ phần" → share_premium
- "Quỹ dự trữ bổ sung vốn điều lệ" / "Cổ phiếu quỹ (số lượng)" → treasury_stock
- "Quỹ dự phòng tài chính và rủi ro nghiệp vụ" → financial_and_operating_risk_reserve
- "Lợi nhuận chưa phân phối" → undistributed_earnings
- "Lợi nhuận đã thực hiện" → retained_earnings_realized
- "Lợi nhuận chưa thực hiện" → retained_earnings_unrealized

TỔNG NỢ VÀ VỐN:
- "Tổng cộng nợ phải trả và vốn chủ sở hữu" / "TỔNG NỢ VÀ VỐN CHỦ SỞ HỮU" → total_liabilities_and_owners_equity

LƯU Ý QUAN TRỌNG:
- Bỏ qua tất cả các mục trong phần "CÁC CHỈ TIÊU NGOÀI BÁO CÁO TÌNH HÌNH TÀI CHÍNH HỢP NHẤT"
- Nếu gặp tên tiếng Việt không có trong BẢNG ÁNH XẠ nhưng có ngữ nghĩa tương tự, hãy ánh xạ sang tên chuẩn gần nhất
- Chỉ trích xuất các mục có giá trị số cụ thể, không trích xuất các tiêu đề tổng hợp không có giá trị

OUTPUT: Trả về JSON array hợp lệ, không có text nào khác.
"""
SECURITIES_INCOME_STATEMENT_PROMPT = """
Từ nội dung PDF báo cáo kết quả hoạt động kinh doanh của công ty chứng khoán, hãy trích xuất dữ liệu thành định dạng JSON theo BẢNG ÁNH XẠ và VÍ DỤ CHUẨN bên dưới.

YÊU CẦU CẤU TRÚC JSON:
1. Sử dụng giá trị năm báo cáo (cột có năm lớn nhất - thường là cột "Năm nay" hoặc cột năm gần nhất)
2. Chuyển đổi số: loại bỏ dấu phân cách (dấu chấm hoặc dấu phẩy), "()" = số âm, "-" = null
3. Mỗi object có 3 attributes theo ĐÚNG THỨ TỰ NÀY:
   - "description": Tên tiếng Việt CHÍNH XÁC như trong PDF (giữ nguyên chữ hoa/thường, giữ nguyên tất cả từ viết tắt như TSTC, FVTPL, HTM, AFS, TNDN)
   - "name": Tên tiếng Anh (snake_case) - PHẢI KHỚP CHÍNH XÁC với bảng ánh xạ
   - "value": Giá trị số (integer hoặc null)
4. CHỈ TRẢ VỀ JSON ARRAY: [{"description":"...","name":"...","value":123},...]
5. KHÔNG có text giải thích thêm

NGUYÊN TẮC QUAN TRỌNG NHẤT:
⚠️ SỬ DỤNG CHÍNH XÁC TÊN THUỘC TÍNH TRONG BẢNG - KHÔNG ĐƯỢC THAY ĐỔI hoặc SÁNG TẠO TÊN MỚI
⚠️ Description phải lấy CHÍNH XÁC tên tiếng Việt từ PDF - không được diễn giải, rút gọn hoặc thay đổi
⚠️ Chỉ trích xuất các trường có trong bảng ánh xạ bên dưới
⚠️ Nếu không tìm thấy mục trong PDF → BỎ QUA, không tạo giá trị giả
⚠️ Nếu không chắc chắn về mapping → BỎ QUA thay vì dùng tên sai

ĐẶC ĐIỂM NHẬN DẠNG BÁO CÁO CHỨNG KHOÁN:
- Có cột "Mã số", "CHỈ TIÊU" hoặc "Thuyết minh"
- Dùng ký hiệu mã số: 01, 01.1, 01.2, 02, 03... hoặc a., b., c.
- Có thể dùng từ viết tắt (KPMG): TSTC, TNDN
- Hoặc dùng từ đầy đủ (EY): tài sản tài chính, thu nhập doanh nghiệp
- Có thể có FVTPL, HTM, AFS trong tên mục
- Số âm được biểu diễn bằng dấu ngoặc đơn: (6.479.470.056)
- Dấu phân cách nghìn là dấu chấm: 18.718.169.267
- Đơn vị tính: VND hoặc đồng

BẢNG ÁNH XẠ CHI TIẾT - 55 TRƯỜNG CHUẨN:

**I. DOANH THU HOẠT ĐỘNG (15 trường)**

1. Tìm trong PDF các biến thể:
   - "Lãi từ các TSTC ghi nhận thông qua lãi/lỗ" (KPMG)
   - "Lãi từ các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL)" (EY)
   - "Lãi từ các tài sản tài chính ghi nhận thông qua lãi/lỗ"
   Tên chuẩn: **interest_and_fee_income_from_financial_assets_recognized_through_p_and_l**

2. Tìm trong PDF các biến thể:
   - "Lãi bán các TSTC ghi nhận thông qua lãi/lỗ" (KPMG)
   - "Lãi bán các tài sản tài chính FVTPL" (EY)
   - "Lãi bán các tài sản tài chính ghi nhận thông qua lãi/lỗ"
   Tên chuẩn: **interest_income_from_financial_assets_recognized_through_p_and_l**

3. Tìm trong PDF các biến thể:
   - "Chênh lệch tăng về đánh giá lại các TSTC ghi nhận thông qua lãi/lỗ" (KPMG)
   - "Chênh lệch tăng về đánh giá lại các tài sản tài chính FVTPL" (EY)
   - "Chênh lệch tăng về đánh giá lại các TSTC FVTPL"
   Tên chuẩn: **increase_decrease_in_fair_value_of_financial_assets_recognized_through_p_and_l**

4. Tìm trong PDF các biến thể:
   - "Cổ tức, tiền lãi phát sinh từ TSTC ghi nhận thông qua lãi/lỗ" (KPMG)
   - "Cổ tức, tiền lãi phát sinh từ tài sản tài chính FVTPL" (EY)
   Tên chuẩn: **dividend_and_interest_income_from_financial_assets_recognized_through_p_and_l**

5. Tìm trong PDF:
   - "Chênh lệch giảm do đánh giá lại phải trả chứng quyền đang lưu hành" (chỉ EY)
   Tên chuẩn: **decrease_in_fair_value_of_outstanding_warrants**

6. Tìm trong PDF các biến thể:
   - "Lãi từ các khoản đầu tư nắm giữ đến ngày đáo hạn" (KPMG)
   - "Lãi từ các khoản đầu tư nắm giữ đến ngày đáo hạn (HTM)" (EY)
   Tên chuẩn: **interest_income_from_held_to_maturity_investments**

7. Tìm trong PDF:
   - "Lãi từ các khoản cho vay và phải thu"
   Tên chuẩn: **interest_income_from_loans_and_receivables**

8. Tìm trong PDF:
   - "Lãi từ tài sản tài chính sẵn sàng để bán (AFS)" (chỉ EY)
   Tên chuẩn: **interest_income_from_available_for_sale_financial_assets**

9. Tìm trong PDF:
   - "Lãi từ các công cụ phái sinh phòng ngừa rủi ro" (chỉ EY)
   Tên chuẩn: **gain_from_hedging_derivatives**

10. Tìm trong PDF:
    - "Doanh thu nghiệp vụ môi giới chứng khoán"
    Tên chuẩn: **brokerage_revenue**

11. Tìm trong PDF các biến thể:
    - "Doanh thu bảo lãnh, đại lý phát hành chứng khoán" (KPMG)
    - "Doanh thu nghiệp vụ bảo lãnh, đại lý phát hành chứng khoán" (EY)
    Tên chuẩn: **underwriting_revenue**

12. Tìm trong PDF các biến thể:
    - "Doanh thu nghiệp vụ tư vấn đầu tư chứng khoán"
    - "Doanh thu tư vấn, đầu tư chứng khoán"
    Tên chuẩn: **investment_advisory_revenue**

13. Tìm trong PDF các biến thể:
    - "Doanh thu nghiệp vụ lưu ký chứng khoán"
    - "Doanh thu nghiệp vụ lưu ký"
    Tên chuẩn: **securities_custody_revenue**

14. Tìm trong PDF các biến thể:
    - "Doanh thu nghiệp vụ tư vấn đầu tư tài chính" (KPMG)
    - "Doanh thu hoạt động tư vấn tài chính" (EY)
    Tên chuẩn: **financial_advisory_revenue**

15. Tìm trong PDF các biến thể:
    - "Thu nhập hoạt động khác"
    - "Doanh thu hoạt động khác"
    Tên chuẩn: **other_operating_income**

16. Tìm trong PDF:
    - "Cộng doanh thu hoạt động"
    Tên chuẩn: **total_operating_revenue**

**II. CHI PHÍ HOẠT ĐỘNG (15 trường)**

17. Tìm trong PDF các biến thể:
    - "Lỗ các TSTC ghi nhận thông qua lãi/lỗ" (KPMG)
    - "Lỗ từ các tài sản tài chính FVTPL" (EY)
    - "Lỗ các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL)"
    Tên chuẩn: **interest_expense_on_financial_assets_recognized_through_p_and_l**

18. Tìm trong PDF các biến thể:
    - "Lỗ bán các TSTC ghi nhận thông qua lãi/lỗ" (KPMG)
    - "Lỗ bán các tài sản tài chính FVTPL" (EY)
    Tên chuẩn: **interest_expense**

19. Tìm trong PDF các biến thể:
    - "Chênh lệch giảm đánh giá lại các TSTC ghi nhận thông qua lãi/lỗ" (KPMG)
    - "Chênh lệch giảm đánh giá lại các tài sản tài chính FVTPL" (EY)
    - "Chênh lệch giảm đánh giá lại các TSTC FVTPL"
    Tên chuẩn: **decrease_in_fair_value_of_financial_assets**

20. Tìm trong PDF các biến thể:
    - "Chi phí giao dịch mua các TSTC thông qua lãi/lỗ" (KPMG)
    - "Chi phí giao dịch mua các tài sản tài chính FVTPL" (EY)
    Tên chuẩn: **transaction_fees_for_financial_assets**

21. Tìm trong PDF:
    - "Chênh lệch tăng do đánh giá lại phải trả chứng quyền đang lưu hành" (chỉ EY)
    Tên chuẩn: **increase_in_fair_value_of_outstanding_warrants**

22. Tìm trong PDF:
    - "Lỗ các khoản đầu tư nắm giữ đến ngày đáo hạn (HTM)" (chỉ EY)
    Tên chuẩn: **loss_from_held_to_maturity_investments**

23. Tìm trong PDF:
    - "Lỗ và ghi nhận chênh lệch đánh giá theo giá trị hợp lý tài sản tài chính sẵn sàng để bán (AFS) khi phân loại lại" (chỉ EY)
    - "Lỗ và ghi nhận chênh lệch đánh giá theo giá trị hợp lý tài sản tài chính AFS khi phân loại lại"
    Tên chuẩn: **loss_and_recognition_of_fair_value_difference_of_available_for_sale_financial_assets_upon_reclassification**

24. Tìm trong PDF các biến thể:
    - "Chi phí dự phòng TSTC, xử lý tổn thất các khoản phải thu khó đòi và lỗ suy giảm TSTC và chi phí đi vay của các khoản cho vay" (KPMG)
    - "Chi phí dự phòng tài sản tài chính, xử lý tổn thất các khoản phải thu khó đòi và lỗ suy giảm tài sản tài chính và chi phí đi vay của các khoản cho vay" (EY)
    - "Hoàn nhập dự phòng tài sản tài chính, xử lý tổn thất các khoản phải thu khó đòi, lỗ suy giảm tài sản tài chính và chi phí đi vay của các khoản cho vay" (EY)
    - "Trích lập/(hoàn nhập) dự phòng tài sản tài chính..."
    Tên chuẩn: **provisions_for_impairment_of_financial_assets**

25. Tìm trong PDF:
    - "Lỗ từ các tài sản tài chính phái sinh phòng ngừa rủi ro" (chỉ EY)
    Tên chuẩn: **loss_from_hedging_derivatives**

26. Tìm trong PDF các biến thể:
    - "Chi phí hoạt động tự doanh"
    - "Chi phí hoạt động tư doanh"
    Tên chuẩn: **operating_expense**

27. Tìm trong PDF các biến thể:
    - "Chi phí môi giới chứng khoán" (KPMG)
    - "Chi phí nghiệp vụ môi giới chứng khoán" (EY)
    Tên chuẩn: **brokerage_fees**

28. Tìm trong PDF các biến thể:
    - "Chi phí bảo lãnh, đại lý phát hành chứng khoán" (KPMG)
    - "Chi phí nghiệp vụ bảo lãnh, đại lý phát hành chứng khoán" (EY)
    - "Chi phí hoạt động bảo lãnh, đại lý phát hành chứng khoán"
    Tên chuẩn: **underwriting_and_bond_issuance_costs**

29. Tìm trong PDF các biến thể:
    - "Chi phí tư vấn đầu tư chứng khoán" (KPMG)
    - "Chi phí nghiệp vụ tư vấn đầu tư chứng khoán" (EY)
    - "Chi phí tư vấn, đầu tư chứng khoán"
    Tên chuẩn: **investment_advisory_expenses**

30. Tìm trong PDF:
    - "Chi phí nghiệp vụ lưu ký chứng khoán"
    Tên chuẩn: **securities_custody_expenses**

31. Tìm trong PDF:
    - "Chi phí hoạt động tư vấn tài chính" (chỉ EY)
    Tên chuẩn: **financial_advisory_expenses**

32. Tìm trong PDF các biến thể:
    - "Chi phí hoạt động khác"
    - "Chi phí các dịch vụ khác"
    Tên chuẩn: **other_operating_expenses**

33. Tìm trong PDF:
    - "Cộng chi phí hoạt động"
    Tên chuẩn: **total_operating_expenses**

**III. DOANH THU HOẠT ĐỘNG TÀI CHÍNH (5 trường)**

34. Tìm trong PDF:
    - "Chênh lệch lãi tỷ giá hối đoái đã và chưa thực hiện"
    Tên chuẩn: **increase_decrease_in_fair_value_of_exchange_rate_and_unrealized**

35. Tìm trong PDF các biến thể:
    - "Doanh thu, dự thu cổ tức, lãi tiền gửi không cố định" (EY)
    - "Doanh thu, dự thu cổ tức, lãi tiền gửi ngân hàng không cố định"
    - "Doanh thu lãi tiền gửi phát sinh trong năm"
    Tên chuẩn: **interest_income_from_deposits**

36. Tìm trong PDF các biến thể:
    - "Lãi bán, thanh lý các khoản đầu tư vào công ty con, liên kết, liên doanh"
    - "Lãi bán, thanh lý các khoản đầu tư vào công ty con, công ty liên kết"
    Tên chuẩn: **gain_on_disposal_of_investments_in_subsidiaries_associates_and_joint_ventures**

37. Tìm trong PDF:
    - "Doanh thu khác về đầu tư"
    Tên chuẩn: **other_investment_income**

38. Tìm trong PDF:
    - "Cộng doanh thu hoạt động tài chính"
    Tên chuẩn: **total_financial_operating_revenue**

**IV. CHI PHÍ TÀI CHÍNH (5 trường)**

39. Tìm trong PDF:
    - "Chênh lệch lỗ tỷ giá hối đoái đã và chưa thực hiện"
    Tên chuẩn: **increase_decrease_in_fair_value_of_exchange_rate_loss**

40. Tìm trong PDF:
    - "Chi phí lãi vay"
    Tên chuẩn: **interest_expense_on_borrowings**

41. Tìm trong PDF:
    - "Lỗ bán, thanh lý các khoản đầu tư vào công ty con, liên kết, liên doanh"
    Tên chuẩn: **loss_on_disposal_of_investments_in_subsidiaries_associates_and_joint_ventures**

42. Tìm trong PDF:
    - "Chi phí dự phòng suy giảm giá trị các khoản đầu tư tài chính dài hạn"
    Tên chuẩn: **provision_for_impairment_of_long_term_financial_investments**

43. Tìm trong PDF:
    - "Chi phí tài chính khác"
    Tên chuẩn: **other_financial_expenses**

44. Tìm trong PDF:
    - "Cộng chi phí tài chính"
    Tên chuẩn: **total_financial_expenses**

**V. CHI PHÍ KHÁC (2 trường)**

45. Tìm trong PDF:
    - "CHI PHÍ BÁN HÀNG" (chỉ EY)
    Tên chuẩn: **selling_expenses**

46. Tìm trong PDF các biến thể:
    - "CHI PHÍ QUẢN LÝ CÔNG TY CHỨNG KHOÁN"
    - "CHI PHÍ QUẢN LÝ"
    Tên chuẩn: **general_and_administrative_expenses**

**VI. KẾT QUẢ HOẠT ĐỘNG (1 trường)**

47. Tìm trong PDF:
    - "KẾT QUẢ HOẠT ĐỘNG"
    Tên chuẩn: **operating_profit**

**VII. THU NHẬP VÀ CHI PHÍ KHÁC (3 trường)**

48. Tìm trong PDF:
    - "Thu nhập khác"
    Tên chuẩn: **other_income**

49. Tìm trong PDF:
    - "Chi phí khác"
    Tên chuẩn: **other_expenses**

50. Tìm trong PDF:
    - "Cộng kết quả hoạt động khác"
    Tên chuẩn: **net_other_income_and_expenses**

**VIII. LỢI NHUẬN TRƯỚC THUẾ (3 trường)**

51. Tìm trong PDF các biến thể:
    - "TỔNG LỢI NHUẬN KẾ TOÁN TRƯỚC THUẾ"
    - "Tổng lợi nhuận kế toán trước thuế"
    Tên chuẩn: **accounting_profit_before_tax**

52. Tìm trong PDF:
    - "Lợi nhuận đã thực hiện"
    Tên chuẩn: **realized_profit**

53. Tìm trong PDF các biến thể:
    - "(Lỗ)/lợi nhuận chưa thực hiện" (KPMG)
    - "Lợi nhuận chưa thực hiện" (EY)
    Tên chuẩn: **unrealized_profit_loss**

**IX. CHI PHÍ THUẾ (3 trường)**

54. Tìm trong PDF các biến thể:
    - "CHI PHÍ THUẾ TNDN" (KPMG)
    - "CHI PHÍ THUẾ THU NHẬP DOANH NGHIỆP (TNDN)" (EY)
    - "Chi phí thuế thu nhập doanh nghiệp"
    Tên chuẩn: **total_corporate_income_tax**

55. Tìm trong PDF các biến thể:
    - "Chi phí thuế TNDN hiện hành"
    - "Chi phí thuế thu nhập doanh nghiệp hiện hành"
    Tên chuẩn: **current_corporate_income_tax_expense**

56. Tìm trong PDF các biến thể:
    - "(Lợi ích)/Chi phí thuế TNDN hoãn lại" (KPMG)
    - "(Thu nhập)/chi phí thuế TNDN hoãn lại" (EY)
    - "Chi phí/(thu nhập) thuế TNDN hoãn lại"
    - "Chi phí thuế thu nhập doanh nghiệp hoãn lại"
    Tên chuẩn: **benefit_from_deferred_income_tax_expense**

**X. LỢI NHUẬN SAU THUẾ (4 trường)**

57. Tìm trong PDF các biến thể:
    - "LỢI NHUẬN KẾ TOÁN SAU THUẾ TNDN"
    - "Lợi nhuận kế toán sau thuế thu nhập doanh nghiệp"
    Tên chuẩn: **net_profit_after_tax**

58. Tìm trong PDF:
    - "Lợi nhuận sau thuế phân bổ cho chủ sở hữu" (chỉ EY)
    Tên chuẩn: **profit_attributable_to_equity_holders**

59. Tìm trong PDF:
    - "Lợi nhuận sau thuế trích các Quỹ" (chỉ EY)
    Tên chuẩn: **profit_after_tax_allocated_to_funds**

60. Tìm trong PDF:
    - "Lợi nhuận thuần phân bổ cho lợi ích của cổ đông không kiểm soát" (chỉ EY)
    Tên chuẩn: **profit_attributable_to_non_controlling_interests**

VÍ DỤ INPUT-OUTPUT CHUẨN:

**VÍ DỤ 1: Báo cáo KPMG**
INPUT (từ PDF):
```
Mã số 01 | Lãi từ các TSTC ghi nhận thông qua lãi/lỗ | 18.718.169.267
Mã số 01.1 | Lãi bán các TSTC ghi nhận thông qua lãi/lỗ | 15.791.720.906
Mã số 02 | Lãi từ các khoản đầu tư nắm giữ đến ngày đáo hạn | 112.885.074.974
```

OUTPUT ĐÚNG:
```json
[
  {
    "description": "Lãi từ các TSTC ghi nhận thông qua lãi/lỗ",
    "name": "interest_and_fee_income_from_financial_assets_recognized_through_p_and_l",
    "value": 18718169267
  },
  {
    "description": "Lãi bán các TSTC ghi nhận thông qua lãi/lỗ",
    "name": "interest_income_from_financial_assets_recognized_through_p_and_l",
    "value": 15791720906
  },
  {
    "description": "Lãi từ các khoản đầu tư nắm giữ đến ngày đáo hạn",
    "name": "interest_income_from_held_to_maturity_investments",
    "value": 112885074974
  }
]
```

**VÍ DỤ 2: Báo cáo EY**
INPUT (từ PDF):
```
Mã số 01 | Lãi từ các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL) | 2.020.267.370.129
Mã số 01.1 | Lãi bán các tài sản tài chính FVTPL | 987.264.064.050
Mã số 04 | Lãi từ tài sản tài chính sẵn sàng để bán (AFS) | 2.853.002.528
```

OUTPUT ĐÚNG:
```json
[
  {
    "description": "Lãi từ các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL)",
    "name": "interest_and_fee_income_from_financial_assets_recognized_through_p_and_l",
    "value": 2020267370129
  },
  {
    "description": "Lãi bán các tài sản tài chính FVTPL",
    "name": "interest_income_from_financial_assets_recognized_through_p_and_l",
    "value": 987264064050
  },
  {
    "description": "Lãi từ tài sản tài chính sẵn sàng để bán (AFS)",
    "name": "interest_income_from_available_for_sale_financial_assets",
    "value": 2853002528
  }
]
```

**VÍ DỤ 3: Xử lý số âm**
INPUT (từ PDF):
```
Mã số 01.2 | Chênh lệch tăng về đánh giá lại các TSTC ghi nhận thông qua lãi/lỗ | (6.479.470.056)
Mã số 92 | Lợi nhuận chưa thực hiện | (298.919.736.776)
Mã số 100.2 | (Lợi ích)/Chi phí thuế TNDN hoãn lại | (1.295.131.776)
```

OUTPUT ĐÚNG:
```json
[
  {
    "description": "Chênh lệch tăng về đánh giá lại các TSTC ghi nhận thông qua lãi/lỗ",
    "name": "increase_decrease_in_fair_value_of_financial_assets_recognized_through_p_and_l",
    "value": -6479470056
  },
  {
    "description": "Lợi nhuận chưa thực hiện",
    "name": "unrealized_profit_loss",
    "value": -298919736776
  },
  {
    "description": "(Lợi ích)/Chi phí thuế TNDN hoãn lại",
    "name": "benefit_from_deferred_income_tax_expense",
    "value": -1295131776
  }
]
```

LƯU Ý ĐẶC BIỆT:
- Trích xuất TẤT CẢ các trường có trong báo cáo khớp với 60 trường chuẩn
- Description phải giữ NGUYÊN VĂN từ PDF: giữ cả TSTC, FVTPL, HTM, AFS, TNDN, dấu ngoặc đơn ()
- Không được rút gọn, diễn giải hoặc thay đổi description
- Số âm: (số) → -số
- Dấu gạch ngang "-" → null
- Dấu phân cách nghìn: loại bỏ khi convert
- Mỗi đơn vị kiểm toán có thể có một số trường riêng:
  + Chỉ KPMG: không có AFS, chứng quyền, phân bổ lợi nhuận, chi phí bán hàng
  + Chỉ EY: có đầy đủ AFS, chứng quyền, phân bổ lợi nhuận, chi phí bán hàng

HƯỚNG DẪN THỰC HIỆN:
1. Đọc toàn bộ PDF, xác định định dạng (KPMG hoặc EY)
2. Với mỗi mục, tìm kiếm mô tả khớp trong bảng ánh xạ 60 trường
3. Lấy CHÍNH XÁC tên tiếng Việt từ PDF làm "description" (không diễn giải)
4. Sử dụng CHÍNH XÁC tên thuộc tính chuẩn làm "name"
5. Chuyển đổi giá trị: loại bỏ dấu phân cách, (số) → -số, "-" → null
6. Sắp xếp theo thứ tự: description - name - value
7. Trích xuất tất cả các trường có trong báo cáo

OUTPUT: CHỈ JSON array như ví dụ, KHÔNG có text giải thích hay markdown.
"""
KPMG_SECURITIES_INCOME_STATEMENT_PROMPT = """
Từ nội dung PDF báo cáo kết quả hoạt động kinh doanh được kiểm toán bởi KPMG, hãy trích xuất dữ liệu thành định dạng JSON theo BẢNG ÁNH XẠ và VÍ DỤ CHUẨN bên dưới.

YÊU CẦU CẤU TRÚC JSON:
1. Sử dụng giá trị năm báo cáo (cột có năm lớn nhất)
2. Chuyển đổi số: loại bỏ dấu phân cách (dấu chấm), "()" = số âm, "-" = null
3. Mỗi object có 3 attributes theo ĐÚNG THỨ TỰ NÀY:
   - "description": Tên tiếng Việt CHÍNH XÁC như trong PDF (giữ nguyên chữ hoa/thường, giữ nguyên cả TSTC, FVTPL, HTM, TNDN nếu có)
   - "name": Tên tiếng Anh (snake_case) - PHẢI KHỚP CHÍNH XÁC với bảng ánh xạ
   - "value": Giá trị số (integer hoặc null)
4. CHỈ TRẢ VỀ JSON ARRAY: [{"description":"...","name":"...","value":123},...]
5. KHÔNG có text giải thích thêm

NGUYÊN TẮC QUAN TRỌNG NHẤT:
⚠️ SỬ DỤNG CHÍNH XÁC TÊN THUỘC TÍNH TRONG BẢNG - KHÔNG ĐƯỢC THAY ĐỔI hoặc SÁNG TẠO TÊN MỚI
⚠️ Description phải lấy CHÍNH XÁC tên tiếng Việt từ PDF - không được diễn giải, viết tắt hoặc thay đổi
⚠️ Chỉ trích xuất các trường có trong bảng ánh xạ KPMG bên dưới (43 trường)
⚠️ Nếu không tìm thấy mục trong PDF → BỎ QUA, không tạo giá trị giả
⚠️ Nếu không chắc chắn về mapping → BỎ QUA thay vì dùng tên sai

ĐẶC ĐIỂM NHẬN DẠNG BÁO CÁO KPMG:
- Có cột "Mã số" và "Thuyết minh"
- Dùng ký hiệu mã số: 01, 01.1, 01.2, 02, 03... hoặc a., b., c.
- Dùng từ viết tắt: TSTC (Tài sản tài chính), TNDN (Thu nhập doanh nghiệp)
- Số âm được biểu diễn bằng dấu ngoặc đơn: (6.479.470.056)
- Dấu phân cách nghìn là dấu chấm: 18.718.169.267

BẢNG ÁNH XẠ CHI TIẾT - 43 TRƯỜNG CẦN TRÍCH XUẤT:

**I. DOANH THU HOẠT ĐỘNG (13 trường)**

1. Tìm trong PDF: "Lãi từ các TSTC ghi nhận thông qua lãi/lỗ" (Thường có mã số 01)
   Tên chuẩn: **interest_and_fee_income_from_financial_assets_recognized_through_p_and_l**
   
2. Tìm trong PDF: "Lãi bán các TSTC ghi nhận thông qua lãi/lỗ" (Thường có mã số 01.1 hoặc a.)
   Tên chuẩn: **interest_income_from_financial_assets_recognized_through_p_and_l**
   
3. Tìm trong PDF: "Chênh lệch tăng về đánh giá lại các TSTC ghi nhận thông qua lãi/lỗ" (Thường có mã số 01.2 hoặc b.)
   Tên chuẩn: **increase_decrease_in_fair_value_of_financial_assets_recognized_through_p_and_l**
   
4. Tìm trong PDF: "Cổ tức, tiền lãi phát sinh từ TSTC ghi nhận thông qua lãi/lỗ" (Thường có mã số 01.3 hoặc c.)
   Tên chuẩn: **dividend_and_interest_income_from_financial_assets_recognized_through_p_and_l**
   
5. Tìm trong PDF: "Lãi từ các khoản đầu tư nắm giữ đến ngày đáo hạn" (Thường có mã số 02)
   Tên chuẩn: **interest_income_from_held_to_maturity_investments**
   
6. Tìm trong PDF: "Lãi từ các khoản cho vay và phải thu" (Thường có mã số 03)
   Tên chuẩn: **interest_income_from_loans_and_receivables**
   
7. Tìm trong PDF: "Doanh thu nghiệp vụ môi giới chứng khoán" (Thường có mã số 06)
   Tên chuẩn: **brokerage_revenue**
   
8. Tìm trong PDF: "Doanh thu bảo lãnh, đại lý phát hành chứng khoán" (Thường có mã số 06 hoặc 07)
   Tên chuẩn: **underwriting_revenue**
   
9. Tìm trong PDF: "Doanh thu nghiệp vụ tư vấn đầu tư chứng khoán" (Thường có mã số 08)
   Tên chuẩn: **investment_advisory_revenue**
   
10. Tìm trong PDF: "Doanh thu nghiệp vụ lưu ký chứng khoán" (Thường có mã số 09)
    Tên chuẩn: **securities_custody_revenue**
    
11. Tìm trong PDF: "Doanh thu nghiệp vụ tư vấn đầu tư tài chính" (Thường có mã số 10)
    Tên chuẩn: **financial_advisory_revenue**
    
12. Tìm trong PDF: "Thu nhập hoạt động khác" (Thường có mã số 11)
    Tên chuẩn: **other_operating_income**
    
13. Tìm trong PDF: "Cộng doanh thu hoạt động" (Thường có mã số 20)
    Tên chuẩn: **total_operating_revenue**

**II. CHI PHÍ HOẠT ĐỘNG (12 trường)**

14. Tìm trong PDF: "Lỗ các TSTC ghi nhận thông qua lãi/lỗ" (Thường có mã số 21)
    Tên chuẩn: **interest_expense_on_financial_assets_recognized_through_p_and_l**
    
15. Tìm trong PDF: "Lỗ bán các TSTC ghi nhận thông qua lãi/lỗ" (Thường có mã số 21.1 hoặc a.)
    Tên chuẩn: **interest_expense**
    
16. Tìm trong PDF: "Chênh lệch giảm đánh giá lại các TSTC ghi nhận thông qua lãi/lỗ" (Thường có mã số 21.2 hoặc b.)
    Tên chuẩn: **decrease_in_fair_value_of_financial_assets**
    
17. Tìm trong PDF: "Chi phí giao dịch mua các TSTC thông qua lãi/lỗ" (Thường có mã số 21.3 hoặc c.)
    Tên chuẩn: **transaction_fees_for_financial_assets**
    
18. Tìm trong PDF: "Chi phí dự phòng TSTC, xử lý tổn thất các khoản phải thu khó đòi và lỗ suy giảm TSTC và chi phí đi vay của các khoản cho vay" (Thường có mã số 24)
    Tên chuẩn: **provisions_for_impairment_of_financial_assets**
    
19. Tìm trong PDF: "Chi phí hoạt động tự doanh" (Thường có mã số 26)
    Tên chuẩn: **operating_expense**
    
20. Tìm trong PDF: "Chi phí môi giới chứng khoán" (Thường có mã số 27)
    Tên chuẩn: **brokerage_fees**
    
21. Tìm trong PDF: "Chi phí bảo lãnh, đại lý phát hành chứng khoán" HOẶC "Chi phí hoạt động bảo lãnh, đại lý phát hành chứng khoán" (Thường có mã số 28)
    Tên chuẩn: **underwriting_and_bond_issuance_costs**
    
22. Tìm trong PDF: "Chi phí tư vấn đầu tư chứng khoán" HOẶC "Chi phí tư vấn, đầu tư chứng khoán" (Thường có mã số 29)
    Tên chuẩn: **investment_advisory_expenses**
    
23. Tìm trong PDF: "Chi phí nghiệp vụ lưu ký chứng khoán" (Thường có mã số 30)
    Tên chuẩn: **securities_custody_expenses**
    
24. Tìm trong PDF: "Chi phí hoạt động khác" (Thường có mã số 32)
    Tên chuẩn: **other_operating_expenses**
    
25. Tìm trong PDF: "Cộng chi phí hoạt động" (Thường có mã số 40)
    Tên chuẩn: **total_operating_expenses**

**III. DOANH THU HOẠT ĐỘNG TÀI CHÍNH (3 trường)**

26. Tìm trong PDF: "Chênh lệch lãi tỷ giá hối đoái đã và chưa thực hiện" (Thường có mã số 41)
    Tên chuẩn: **increase_decrease_in_fair_value_of_exchange_rate_and_unrealized**
    
27. Tìm trong PDF: "Doanh thu khác về đầu tư" (Thường có mã số 44)
    Tên chuẩn: **other_investment_income**
    
28. Tìm trong PDF: "Cộng doanh thu hoạt động tài chính" (Thường có mã số 50)
    Tên chuẩn: **total_financial_operating_revenue**

**IV. CHI PHÍ TÀI CHÍNH (3 trường)**

29. Tìm trong PDF: "Chi phí lãi vay" (Thường có mã số 52)
    Tên chuẩn: **interest_expense_on_borrowings**
    
30. Tìm trong PDF: "Chi phí tài chính khác" (Thường có mã số 52 hoặc 54)
    Tên chuẩn: **other_financial_expenses**
    
31. Tìm trong PDF: "Cộng chi phí tài chính" (Thường có mã số 60)
    Tên chuẩn: **total_financial_expenses**

**V. CHI PHÍ QUẢN LÝ (1 trường)**

32. Tìm trong PDF: "CHI PHÍ QUẢN LÝ CÔNG TY CHỨNG KHOÁN" (Thường có mã số 62, phần VI)
    Tên chuẩn: **general_and_administrative_expenses**

**VI. KẾT QUẢ HOẠT ĐỘNG (1 trường)**

33. Tìm trong PDF: "KẾT QUẢ HOẠT ĐỘNG" (Thường có mã số 70, phần VII)
    Tên chuẩn: **operating_profit**

**VII. THU NHẬP VÀ CHI PHÍ KHÁC (3 trường)**

34. Tìm trong PDF: "Thu nhập khác" (Thường có mã số 71)
    Tên chuẩn: **other_income**
    
35. Tìm trong PDF: "Chi phí khác" (Thường có mã số 72)
    Tên chuẩn: **other_expenses**
    
36. Tìm trong PDF: "Cộng kết quả hoạt động khác" (Thường có mã số 80)
    Tên chuẩn: **net_other_income_and_expenses**

**VIII. LỢI NHUẬN TRƯỚC THUẾ (3 trường)**

37. Tìm trong PDF: "TỔNG LỢI NHUẬN KẾ TOÁN TRƯỚC THUẾ" (Thường có mã số 90, phần IX)
    Tên chuẩn: **accounting_profit_before_tax**
    
38. Tìm trong PDF: "Lợi nhuận đã thực hiện" (Thường có mã số 91)
    Tên chuẩn: **realized_profit**
    
39. Tìm trong PDF: "(Lỗ)/lợi nhuận chưa thực hiện" HOẶC "Lợi nhuận chưa thực hiện" (Thường có mã số 92)
    Tên chuẩn: **unrealized_profit_loss**

**IX. CHI PHÍ THUẾ (3 trường)**

40. Tìm trong PDF: "CHI PHÍ THUẾ TNDN" (Thường có mã số 100, phần X)
    Tên chuẩn: **total_corporate_income_tax**
    
41. Tìm trong PDF: "Chi phí thuế TNDN hiện hành" (Thường có mã số 100.1)
    Tên chuẩn: **current_corporate_income_tax_expense**
    
42. Tìm trong PDF: "(Lợi ích)/chi phí thuế TNDN hoãn lại" HOẶC "(Lợi ích)/Chi phí thuế TNDN hoãn lại" (Thường có mã số 100.2)
    Tên chuẩn: **benefit_from_deferred_income_tax_expense**

**X. LỢI NHUẬN SAU THUẾ (1 trường)**

43. Tìm trong PDF: "LỢI NHUẬN KẾ TOÁN SAU THUẾ TNDN" (Thường có mã số 200, phần XI)
    Tên chuẩn: **net_profit_after_tax**

VÍ DỤ INPUT-OUTPUT CHUẨN:

**VÍ DỤ 1: Trích xuất từ báo cáo KPMG**
INPUT (từ PDF):
```
Mã số: 01 | Lãi từ các TSTC ghi nhận thông qua lãi/lỗ | 18.718.169.267
Mã số: 01.1 | Lãi bán các TSTC ghi nhận thông qua lãi/lỗ | 15.791.720.906
Mã số: 01.2 | Chênh lệch tăng về đánh giá lại các TSTC ghi nhận thông qua lãi/lỗ | (6.479.470.056)
Mã số: 02 | Lãi từ các khoản đầu tư nắm giữ đến ngày đáo hạn | 112.885.074.974
Mã số: 06 | Doanh thu nghiệp vụ môi giới chứng khoán | 84.848.044.663
Mã số: 20 | Cộng doanh thu hoạt động | 452.087.667.139
```

OUTPUT ĐÚNG:
```json
[
  {
    "description": "Lãi từ các TSTC ghi nhận thông qua lãi/lỗ",
    "name": "interest_and_fee_income_from_financial_assets_recognized_through_p_and_l",
    "value": 18718169267
  },
  {
    "description": "Lãi bán các TSTC ghi nhận thông qua lãi/lỗ",
    "name": "interest_income_from_financial_assets_recognized_through_p_and_l",
    "value": 15791720906
  },
  {
    "description": "Chênh lệch tăng về đánh giá lại các TSTC ghi nhận thông qua lãi/lỗ",
    "name": "increase_decrease_in_fair_value_of_financial_assets_recognized_through_p_and_l",
    "value": -6479470056
  },
  {
    "description": "Lãi từ các khoản đầu tư nắm giữ đến ngày đáo hạn",
    "name": "interest_income_from_held_to_maturity_investments",
    "value": 112885074974
  },
  {
    "description": "Doanh thu nghiệp vụ môi giới chứng khoán",
    "name": "brokerage_revenue",
    "value": 84848044663
  },
  {
    "description": "Cộng doanh thu hoạt động",
    "name": "total_operating_revenue",
    "value": 452087667139
  }
]
```

**VÍ DỤ 2: Xử lý số âm và null**
INPUT (từ PDF):
```
Mã số: 21 | Lỗ các TSTC ghi nhận thông qua lãi/lỗ | 80.013.516.180
Mã số: 21.2 | Chênh lệch giảm đánh giá lại các TSTC ghi nhận thông qua lãi/lỗ | 78.176.522.917
Mã số: 91 | Lợi nhuận đã thực hiện | 179.579.791.496
Mã số: 92 | (Lỗ)/lợi nhuận chưa thực hiện | (84.655.992.973)
Mã số: 100.2 | (Lợi ích)/chi phí thuế TNDN hoãn lại | (1.295.131.776)
```

OUTPUT ĐÚNG:
```json
[
  {
    "description": "Lỗ các TSTC ghi nhận thông qua lãi/lỗ",
    "name": "interest_expense_on_financial_assets_recognized_through_p_and_l",
    "value": 80013516180
  },
  {
    "description": "Chênh lệch giảm đánh giá lại các TSTC ghi nhận thông qua lãi/lỗ",
    "name": "decrease_in_fair_value_of_financial_assets",
    "value": 78176522917
  },
  {
    "description": "Lợi nhuận đã thực hiện",
    "name": "realized_profit",
    "value": 179579791496
  },
  {
    "description": "(Lỗ)/lợi nhuận chưa thực hiện",
    "name": "unrealized_profit_loss",
    "value": -84655992973
  },
  {
    "description": "(Lợi ích)/chi phí thuế TNDN hoãn lại",
    "name": "benefit_from_deferred_income_tax_expense",
    "value": -1295131776
  }
]
```

LƯU Ý ĐẶC BIỆT VỀ BÁO CÁO KPMG:
- Chỉ trích xuất 43 trường có trong bảng ánh xạ KPMG ở trên
- KHÔNG trích xuất: AFS, phòng ngừa rủi ro, chi phí hoạt động tư vấn tài chính (2.11), doanh thu lãi tiền gửi (3.2), lãi bán công ty con (3.3), chênh lệch lỗ tỷ giá (4.1), lỗ bán công ty con (4.3), dự phòng dài hạn (4.4), chi phí bán hàng (V.)
- Description phải giữ NGUYÊN VĂN từ PDF: giữ cả TSTC, FVTPL, HTM, TNDN, dấu ngoặc đơn ()
- Số âm: (6.479.470.056) → -6479470056
- Dấu gạch ngang "-" → null
- Dấu phân cách nghìn dùng dấu chấm "." → loại bỏ khi convert

HƯỚNG DẪN THỰC HIỆN:
1. Đọc toàn bộ PDF, xác định định dạng KPMG (có cột Mã số, Thuyết minh)
2. Với mỗi mục, tìm kiếm mô tả khớp trong bảng ánh xạ 43 trường
3. Lấy CHÍNH XÁC tên tiếng Việt từ PDF làm "description" (không diễn giải)
4. Sử dụng CHÍNH XÁC tên thuộc tính chuẩn làm "name"
5. Chuyển đổi giá trị: loại bỏ dấu chấm, (số) → -số, "-" → null
6. Sắp xếp theo thứ tự: description - name - value
7. Chỉ trích xuất các trường có trong 43 trường KPMG

OUTPUT: CHỈ JSON array như ví dụ, KHÔNG có text giải thích hay markdown.
"""
EY_SECURITIES_INCOME_STATEMENT_PROMPT = """
Từ nội dung PDF báo cáo kết quả hoạt động kinh doanh được kiểm toán bởi EY, hãy trích xuất dữ liệu thành định dạng JSON theo BẢNG ÁNH XẠ và VÍ DỤ CHUẨN bên dưới.

YÊU CẦU CẤU TRÚC JSON:
1. Sử dụng giá trị năm báo cáo (cột "Năm nay" - năm lớn nhất)
2. Chuyển đổi số: loại bỏ dấu phân cách (dấu chấm), "()" = số âm, "-" = null
3. Mỗi object có 3 attributes theo ĐÚNG THỨ TỰ NÀY:
   - "description": Tên tiếng Việt CHÍNH XÁC như trong PDF (giữ nguyên chữ hoa/thường, giữ nguyên cả FVTPL, HTM, AFS, TNDN nếu có)
   - "name": Tên tiếng Anh (snake_case) - PHẢI KHỚP CHÍNH XÁC với bảng ánh xạ
   - "value": Giá trị số (integer hoặc null)
4. CHỈ TRẢ VỀ JSON ARRAY: [{"description":"...","name":"...","value":123},...]
5. KHÔNG có text giải thích thêm

NGUYÊN TẮC QUAN TRỌNG NHẤT:
⚠️ SỬ DỤNG CHÍNH XÁC TÊN THUỘC TÍNH TRONG BẢNG - KHÔNG ĐƯỢC THAY ĐỔI hoặc SÁNG TẠO TÊN MỚI
⚠️ Description phải lấy CHÍNH XÁC tên tiếng Việt từ PDF - không được diễn giải, viết tắt hoặc thay đổi
⚠️ Chỉ trích xuất các trường có trong bảng ánh xạ EY bên dưới (55 trường)
⚠️ Nếu không tìm thấy mục trong PDF → BỎ QUA, không tạo giá trị giả
⚠️ Nếu không chắc chắn về mapping → BỎ QUA thay vì dùng tên sai

ĐẶC ĐIỂM NHẬN DẠNG BÁO CÁO EY:
- Có cột "Mã số", "CHỈ TIÊU", "Thuyết minh"
- Dùng ký hiệu mã số: 01, 01.1, 01.2, 02, 03... với số La Mã I, II, III...
- Dùng từ đầy đủ không viết tắt: "tài sản tài chính", "thu nhập doanh nghiệp"
- Có thể có cả FVTPL, HTM, AFS trong tên mục
- Số âm được biểu diễn bằng dấu ngoặc đơn: (298.919.736.776)
- Dấu phân cách nghìn là dấu chấm: 2.020.267.370.129
- Đơn vị tính: VND

BẢNG ÁNH XẠ CHI TIẾT - 55 TRƯỜNG CẦN TRÍCH XUẤT:

**I. DOANH THU HOẠT ĐỘNG (15 trường)**

1. Tìm trong PDF: "Lãi từ các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL)" (Thường có mã số 01 hoặc 1.)
   Tên chuẩn: **interest_and_fee_income_from_financial_assets_recognized_through_p_and_l**
   
2. Tìm trong PDF: "Lãi bán các tài sản tài chính FVTPL" (Thường có mã số 01.1 hoặc 1.1.)
   Tên chuẩn: **interest_income_from_financial_assets_recognized_through_p_and_l**
   
3. Tìm trong PDF: "Chênh lệch tăng về đánh giá lại các tài sản tài chính FVTPL" (Thường có mã số 01.2 hoặc 1.2.)
   Tên chuẩn: **increase_decrease_in_fair_value_of_financial_assets_recognized_through_p_and_l**
   
4. Tìm trong PDF: "Cổ tức, tiền lãi phát sinh từ tài sản tài chính FVTPL" (Thường có mã số 01.3 hoặc 1.3.)
   Tên chuẩn: **dividend_and_interest_income_from_financial_assets_recognized_through_p_and_l**
   
5. Tìm trong PDF: "Chênh lệch giảm do đánh giá lại phải trả chứng quyền đang lưu hành" (Thường có mã số 01.4 hoặc 1.4.)
   Tên chuẩn: **decrease_in_fair_value_of_outstanding_warrants**
   
6. Tìm trong PDF: "Lãi từ các khoản đầu tư nắm giữ đến ngày đáo hạn (HTM)" (Thường có mã số 02 hoặc 2.)
   Tên chuẩn: **interest_income_from_held_to_maturity_investments**
   
7. Tìm trong PDF: "Lãi từ các khoản cho vay và phải thu" (Thường có mã số 03 hoặc 3.)
   Tên chuẩn: **interest_income_from_loans_and_receivables**
   
8. Tìm trong PDF: "Lãi từ tài sản tài chính sẵn sàng để bán (AFS)" (Thường có mã số 04 hoặc 4.)
   Tên chuẩn: **interest_income_from_available_for_sale_financial_assets**
   
9. Tìm trong PDF: "Doanh thu nghiệp vụ môi giới chứng khoán" (Thường có mã số 06 hoặc 5.)
   Tên chuẩn: **brokerage_revenue**
   
10. Tìm trong PDF: "Doanh thu nghiệp vụ bảo lãnh, đại lý phát hành chứng khoán" (Thường có mã số 07 hoặc 6.)
    Tên chuẩn: **underwriting_revenue**
    
11. Tìm trong PDF: "Doanh thu nghiệp vụ tư vấn đầu tư chứng khoán" (Thường có mã số 08 hoặc 7.)
    Tên chuẩn: **investment_advisory_revenue**
    
12. Tìm trong PDF: "Doanh thu nghiệp vụ lưu ký chứng khoán" (Thường có mã số 09 hoặc 8.)
    Tên chuẩn: **securities_custody_revenue**
    
13. Tìm trong PDF: "Doanh thu hoạt động tư vấn tài chính" (Thường có mã số 10 hoặc 9.)
    Tên chuẩn: **financial_advisory_revenue**
    
14. Tìm trong PDF: "Thu nhập hoạt động khác" (Thường có mã số 11 hoặc 10.)
    Tên chuẩn: **other_operating_income**
    
15. Tìm trong PDF: "Cộng doanh thu hoạt động" (Thường có mã số 20)
    Tên chuẩn: **total_operating_revenue**

**II. CHI PHÍ HOẠT ĐỘNG (15 trường)**

16. Tìm trong PDF: "Lỗ từ các tài sản tài chính FVTPL" (Thường có mã số 21 hoặc 1.)
    Tên chuẩn: **interest_expense_on_financial_assets_recognized_through_p_and_l**
    
17. Tìm trong PDF: "Lỗ bán các tài sản tài chính FVTPL" (Thường có mã số 21.1 hoặc 1.1.)
    Tên chuẩn: **interest_expense**
    
18. Tìm trong PDF: "Chênh lệch giảm đánh giá lại các tài sản tài chính FVTPL" (Thường có mã số 21.2 hoặc 1.2.)
    Tên chuẩn: **decrease_in_fair_value_of_financial_assets**
    
19. Tìm trong PDF: "Chi phí giao dịch mua các tài sản tài chính FVTPL" (Thường có mã số 21.3 hoặc 1.3.)
    Tên chuẩn: **transaction_fees_for_financial_assets**
    
20. Tìm trong PDF: "Chênh lệch tăng do đánh giá lại phải trả chứng quyền đang lưu hành" (Thường có mã số 21.4 hoặc 1.4.)
    Tên chuẩn: **increase_in_fair_value_of_outstanding_warrants**
    
21. Tìm trong PDF: "Lỗ và ghi nhận chênh lệch đánh giá theo giá trị hợp lý tài sản tài chính AFS khi phân loại lại" (Thường có mã số 23 hoặc 2.)
    Tên chuẩn: **loss_and_recognition_of_fair_value_difference_of_available_for_sale_financial_assets_upon_reclassification**
    
22. Tìm trong PDF: "Hoàn nhập dự phòng tài sản tài chính, xử lý tổn thất các khoản phải thu khó đòi, lỗ suy giảm tài sản tài chính và chi phí đi vay của các khoản cho vay" (Thường có mã số 24 hoặc 3.)
    Tên chuẩn: **provisions_for_impairment_of_financial_assets**
    
23. Tìm trong PDF: "Chi phí hoạt động tự doanh" (Thường có mã số 26 hoặc 4.)
    Tên chuẩn: **operating_expense**
    
24. Tìm trong PDF: "Chi phí nghiệp vụ môi giới chứng khoán" (Thường có mã số 27 hoặc 5.)
    Tên chuẩn: **brokerage_fees**
    
25. Tìm trong PDF: "Chi phí nghiệp vụ bảo lãnh, đại lý phát hành chứng khoán" (Thường có mã số 28 hoặc 6.)
    Tên chuẩn: **underwriting_and_bond_issuance_costs**
    
26. Tìm trong PDF: "Chi phí nghiệp vụ tư vấn đầu tư chứng khoán" (Thường có mã số 29 hoặc 7.)
    Tên chuẩn: **investment_advisory_expenses**
    
27. Tìm trong PDF: "Chi phí nghiệp vụ lưu ký chứng khoán" (Thường có mã số 30 hoặc 8.)
    Tên chuẩn: **securities_custody_expenses**
    
28. Tìm trong PDF: "Chi phí hoạt động tư vấn tài chính" (Thường có mã số 31 hoặc 9.)
    Tên chuẩn: **financial_advisory_expenses**
    
29. Tìm trong PDF: "Chi phí hoạt động khác" (Thường có mã số 32 hoặc 10.)
    Tên chuẩn: **other_operating_expenses**
    
30. Tìm trong PDF: "Cộng chi phí hoạt động" (Thường có mã số 40)
    Tên chuẩn: **total_operating_expenses**

**III. DOANH THU HOẠT ĐỘNG TÀI CHÍNH (5 trường)**

31. Tìm trong PDF: "Chênh lệch lãi tỷ giá hối đoái đã và chưa thực hiện" (Thường có mã số 41 hoặc 1.)
    Tên chuẩn: **increase_decrease_in_fair_value_of_exchange_rate_and_unrealized**
    
32. Tìm trong PDF: "Doanh thu, dự thu cổ tức, lãi tiền gửi không cố định" (Thường có mã số 42 hoặc 2.)
    Tên chuẩn: **interest_income_from_deposits**
    
33. Tìm trong PDF: "Lãi bán, thanh lý các khoản đầu tư vào công ty con, công ty liên kết" (Thường có mã số 43 hoặc 3.)
    Tên chuẩn: **gain_on_disposal_of_investments_in_subsidiaries_associates_and_joint_ventures**
    
34. Tìm trong PDF: "Doanh thu khác về đầu tư" (Thường có mã số 44 hoặc 4.)
    Tên chuẩn: **other_investment_income**
    
35. Tìm trong PDF: "Cộng doanh thu hoạt động tài chính" (Thường có mã số 50)
    Tên chuẩn: **total_financial_operating_revenue**

**IV. CHI PHÍ TÀI CHÍNH (5 trường)**

36. Tìm trong PDF: "Chênh lệch lỗ tỷ giá hối đoái đã và chưa thực hiện" (Thường có mã số 51 hoặc 1.)
    Tên chuẩn: **increase_decrease_in_fair_value_of_exchange_rate_loss**
    
37. Tìm trong PDF: "Chi phí lãi vay" (Thường có mã số 52 hoặc 2.)
    Tên chuẩn: **interest_expense_on_borrowings**
    
38. Tìm trong PDF: "Chi phí tài chính khác" (Thường có mã số 55 hoặc 3.)
    Tên chuẩn: **other_financial_expenses**
    
39. Tìm trong PDF: "Cộng chi phí tài chính" (Thường có mã số 60)
    Tên chuẩn: **total_financial_expenses**
    
40. Tìm trong PDF: "CHI PHÍ BÁN HÀNG" (Thường có mã số 61, phần V.)
    Tên chuẩn: **selling_expenses**

**V. CHI PHÍ QUẢN LÝ (1 trường)**

41. Tìm trong PDF: "CHI PHÍ QUẢN LÝ" hoặc "CHI PHÍ QUẢN LÝ CÔNG TY CHỨNG KHOÁN" (Thường có mã số 62 hoặc 38, phần VI.)
    Tên chuẩn: **general_and_administrative_expenses**

**VI. KẾT QUẢ HOẠT ĐỘNG (1 trường)**

42. Tìm trong PDF: "KẾT QUẢ HOẠT ĐỘNG" (Thường có mã số 70, phần VII.)
    Tên chuẩn: **operating_profit**

**VII. THU NHẬP VÀ CHI PHÍ KHÁC (3 trường)**

43. Tìm trong PDF: "Thu nhập khác" (Thường có mã số 71)
    Tên chuẩn: **other_income**
    
44. Tìm trong PDF: "Chi phí khác" (Thường có mã số 72)
    Tên chuẩn: **other_expenses**
    
45. Tìm trong PDF: "Cộng kết quả hoạt động khác" (Thường có mã số 80 hoặc 39)
    Tên chuẩn: **net_other_income_and_expenses**

**VIII. LỢI NHUẬN TRƯỚC THUẾ (3 trường)**

46. Tìm trong PDF: "TỔNG LỢI NHUẬN KẾ TOÁN TRƯỚC THUẾ" (Thường có mã số 90, phần IX.)
    Tên chuẩn: **accounting_profit_before_tax**
    
47. Tìm trong PDF: "Lợi nhuận đã thực hiện" (Thường có mã số 91)
    Tên chuẩn: **realized_profit**
    
48. Tìm trong PDF: "Lợi nhuận chưa thực hiện" (Thường có mã số 92)
    Tên chuẩn: **unrealized_profit_loss**

**IX. CHI PHÍ THUẾ (3 trường)**

49. Tìm trong PDF: "CHI PHÍ THUẾ THU NHẬP DOANH NGHIỆP (TNDN)" (Thường có mã số 100 hoặc 40, phần X.)
    Tên chuẩn: **total_corporate_income_tax**
    
50. Tìm trong PDF: "Chi phí thuế TNDN hiện hành" (Thường có mã số 100.1 hoặc 40.1)
    Tên chuẩn: **current_corporate_income_tax_expense**
    
51. Tìm trong PDF: "(Thu nhập)/chi phí thuế TNDN hoãn lại" (Thường có mã số 100.2 hoặc 40.2)
    Tên chuẩn: **benefit_from_deferred_income_tax_expense**

**X. LỢI NHUẬN SAU THUẾ (4 trường)**

52. Tìm trong PDF: "LỢI NHUẬN KẾ TOÁN SAU THUẾ TNDN" (Thường có mã số 200, phần XI.)
    Tên chuẩn: **net_profit_after_tax**
    
53. Tìm trong PDF: "Lợi nhuận sau thuế phân bổ cho chủ sở hữu" (Thường có mã số 201 hoặc 1.)
    Tên chuẩn: **profit_attributable_to_equity_holders**
    
54. Tìm trong PDF: "Lợi nhuận sau thuế trích các Quỹ" (Thường có mã số 202 hoặc 2.)
    Tên chuẩn: **profit_after_tax_allocated_to_funds**
    
55. Tìm trong PDF: "Lợi nhuận thuần phân bổ cho lợi ích của cổ đông không kiểm soát" (Thường có mã số 203 hoặc 3.)
    Tên chuẩn: **profit_attributable_to_non_controlling_interests**

VÍ DỤ INPUT-OUTPUT CHUẨN:

**VÍ DỤ 1: Trích xuất từ báo cáo EY**
INPUT (từ PDF):
```
Mã số 01 | Lãi từ các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL) | 2.020.267.370.129
Mã số 01.1 | Lãi bán các tài sản tài chính FVTPL | 987.264.064.050
Mã số 01.2 | Chênh lệch tăng về đánh giá lại các tài sản tài chính FVTPL | 117.166.592.762
Mã số 02 | Lãi từ các khoản đầu tư nắm giữ đến ngày đáo hạn (HTM) | 417.213.313.455
Mã số 06 | Doanh thu nghiệp vụ môi giới chứng khoán | 1.706.658.107.064
Mã số 20 | Cộng doanh thu hoạt động | 6.335.823.057.960
```

OUTPUT ĐÚNG:
```json
[
  {
    "description": "Lãi từ các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL)",
    "name": "interest_and_fee_income_from_financial_assets_recognized_through_p_and_l",
    "value": 2020267370129
  },
  {
    "description": "Lãi bán các tài sản tài chính FVTPL",
    "name": "interest_income_from_financial_assets_recognized_through_p_and_l",
    "value": 987264064050
  },
  {
    "description": "Chênh lệch tăng về đánh giá lại các tài sản tài chính FVTPL",
    "name": "increase_decrease_in_fair_value_of_financial_assets_recognized_through_p_and_l",
    "value": 117166592762
  },
  {
    "description": "Lãi từ các khoản đầu tư nắm giữ đến ngày đáo hạn (HTM)",
    "name": "interest_income_from_held_to_maturity_investments",
    "value": 417213313455
  },
  {
    "description": "Doanh thu nghiệp vụ môi giới chứng khoán",
    "name": "brokerage_revenue",
    "value": 1706658107064
  },
  {
    "description": "Cộng doanh thu hoạt động",
    "name": "total_operating_revenue",
    "value": 6335823057960
  }
]
```

**VÍ DỤ 2: Xử lý số âm và trường đặc biệt**
INPUT (từ PDF):
```
Mã số 24 | Hoàn nhập dự phòng tài sản tài chính, xử lý tổn thất... | (1.864.347.240)
Mã số 92 | Lợi nhuận chưa thực hiện | (298.919.736.776)
Mã số 100.2 | (Thu nhập)/chi phí thuế TNDN hoãn lại | (46.909.000.130)
Mã số 203 | Lợi nhuận thuần phân bổ cho lợi ích của cổ đông không kiểm soát | (1.626.727.424)
```

OUTPUT ĐÚNG:
```json
[
  {
    "description": "Hoàn nhập dự phòng tài sản tài chính, xử lý tổn thất các khoản phải thu khó đòi, lỗ suy giảm tài sản tài chính và chi phí đi vay của các khoản cho vay",
    "name": "provisions_for_impairment_of_financial_assets",
    "value": -1864347240
  },
  {
    "description": "Lợi nhuận chưa thực hiện",
    "name": "unrealized_profit_loss",
    "value": -298919736776
  },
  {
    "description": "(Thu nhập)/chi phí thuế TNDN hoãn lại",
    "name": "benefit_from_deferred_income_tax_expense",
    "value": -46909000130
  },
  {
    "description": "Lợi nhuận thuần phân bổ cho lợi ích của cổ đông không kiểm soát",
    "name": "profit_attributable_to_non_controlling_interests",
    "value": -1626727424
  }
]
```

LƯU Ý ĐẶC BIỆT VỀ BÁO CÁO EY:
- Trích xuất đầy đủ 55 trường có trong bảng ánh xạ EY
- Description phải giữ NGUYÊN VĂN từ PDF: giữ cả FVTPL, HTM, AFS, TNDN, dấu ngoặc đơn ()
- Số âm: (298.919.736.776) → -298919736776
- Dấu gạch ngang "-" → null
- Dấu phân cách nghìn dùng dấu chấm "." → loại bỏ khi convert
- Có thể có các mục đặc biệt như: chứng quyền (mã 01.4, 21.4), AFS (mã 04, 23), phân bổ lợi nhuận (mã 201, 202, 203)

HƯỚNG DẪN THỰC HIỆN:
1. Đọc toàn bộ PDF, xác định định dạng EY (có cột Mã số, CHỈ TIÊU, Thuyết minh)
2. Với mỗi mục, tìm kiếm mô tả khớp trong bảng ánh xạ 55 trường
3. Lấy CHÍNH XÁC tên tiếng Việt từ PDF làm "description" (không diễn giải)
4. Sử dụng CHÍNH XÁC tên thuộc tính chuẩn làm "name"
5. Chuyển đổi giá trị: loại bỏ dấu chấm, (số) → -số, "-" → null
6. Sắp xếp theo thứ tự: description - name - value
7. Trích xuất đầy đủ 55 trường EY

OUTPUT: CHỈ JSON array như ví dụ, KHÔNG có text giải thích hay markdown.
"""


def get_data_prompt_by_section(document_type: str, section_type: str, other_info=None) -> str:
    if (
            document_type == "securities_financial_report"
            and section_type == "financial_statement"
    ):
        return SECURITIES_FINANCIAL_STATEMENT_PROMPT
    if (
            document_type == "securities_financial_report"
            and section_type == "income_statement"
    ):
        return get_income_statement_by_section(other_info)
    else:
        raise ValueError(
            f"could not find prompt for {document_type} and {section_type}"
        )


def get_income_statement_by_section(other_info) -> str:
    if other_info is None:
        return SECURITIES_INCOME_STATEMENT_PROMPT
    elif other_info.get("auditing_company", "") == "KPMG":
        return KPMG_SECURITIES_INCOME_STATEMENT_PROMPT
    elif other_info.get("auditing_company", "") == "EY":
        return EY_SECURITIES_INCOME_STATEMENT_PROMPT
    raise ValueError(
        f"could not find prompt for income statement"
    )
