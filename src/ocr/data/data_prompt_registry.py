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
Từ nội dung PDF báo cáo kết quả hoạt động kinh doanh đã gửi lên, hãy trích xuất dữ liệu thành định dạng JSON theo BẢNG ÁNH XẠ và VÍ DỤ CHUẨN bên dưới.

YÊU CẦU CẤU TRÚC JSON:
1. Sử dụng giá trị năm báo cáo (cột có năm lớn nhất)
2. Chuyển đổi số: loại bỏ dấu phân cách, "()" = số âm, "-" = null
3. Mỗi object có 2 attributes theo đúng thứ tự:
   - "name": Tên tiếng Anh (snake_case) - PHẢI KHỚP CHÍNH XÁC với bảng ánh xạ
   - "value": Giá trị số (integer hoặc null)
4. CHỈ TRẢ VỀ JSON ARRAY: [{"name":"...","value":123},...]
5. KHÔNG có "description", KHÔNG có text giải thích

NGUYÊN TẮC QUAN TRỌNG NHẤT:
⚠️ SỬ DỤNG CHÍNH XÁC TÊN THUỘC TÍNH TRONG BẢNG - KHÔNG ĐƯỢC THAY ĐỔI hoặc SÁNG TẠO TÊN MỚI
⚠️ Nếu không chắc chắn về mapping → BỎ QUA thay vì dùng tên sai

BẢNG ÁNH XẠ CHI TIẾT (45 TRƯỜNG - PHẢI TUÂN THỦ NGHIÊM NGẶT):

**I. DOANH THU HOẠT ĐỘNG (13 trường)**

1. Mô tả: "Lãi từ các TSTC ghi nhận thông qua lãi/lỗ" / "Lãi từ các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL)"
   Tên: **interest_and_fee_income_from_financial_assets_recognized_through_p_and_l**
   ❌ KHÔNG dùng: income_from_financial_assets_at_fvtpl

2. Mô tả: "Lãi bán các TSTC ghi nhận thông qua lãi/lỗ" / "Lãi bán các tài sản tài chính FVTPL"
   Tên: **interest_income_from_financial_assets_recognized_through_p_and_l**
   ❌ KHÔNG dùng: gain_on_sale_of_financial_assets_at_fvtpl

3. Mô tả: "Chênh lệch tăng về đánh giá lại các TSTC ghi nhận thông qua lãi/lỗ" / "Chênh lệch tăng về đánh giá lại các tài sản tài chính FVTPL"
   Tên: **increase_decrease_in_fair_value_of_financial_assets_recognized_through_p_and_l**
   ❌ KHÔNG dùng: unrealized_gain_on_remeasurement_of_financial_assets_at_fvtpl

4. Mô tả: "Cổ tức, tiền lãi phát sinh từ TSTC ghi nhận thông qua lãi/lỗ" / "Cổ tức, tiền lãi phát sinh từ tài sản tài chính FVTPL"
   Tên: **dividend_and_interest_income_from_financial_assets_recognized_through_p_and_l**
   ❌ KHÔNG dùng: dividends_and_interest_income_from_financial_assets_at_fvtpl

5. Mô tả: "Lãi từ các khoản đầu tư nắm giữ đến ngày đáo hạn" / "Lãi từ các khoản đầu tư nắm giữ đến ngày đáo hạn (HTM)"
   Tên: **interest_income_from_held_to_maturity_investments**

6. Mô tả: "Lãi từ các khoản cho vay và phải thu"
   Tên: **interest_income_from_loans_and_receivables**

7. Mô tả: "Doanh thu nghiệp vụ môi giới chứng khoán"
   Tên: **brokerage_revenue**
   ❌ KHÔNG dùng: brokerage_service_revenue

8. Mô tả: "Doanh thu bảo lãnh, đại lý phát hành chứng khoán" / "Doanh thu nghiệp vụ bảo lãnh, đại lý phát hành chứng khoán"
   Tên: **underwriting_revenue**
   ❌ KHÔNG dùng: underwriting_and_issuance_agency_revenue

9. Mô tả: "Doanh thu nghiệp vụ tư vấn đầu tư chứng khoán" / "Doanh thu tư vấn, đầu tư chứng khoán"
   Tên: **investment_advisory_revenue**
   ❌ KHÔNG dùng: securities_investment_advisory_revenue

10. Mô tả: "Doanh thu nghiệp vụ lưu ký chứng khoán" / "Doanh thu nghiệp vụ lưu ký"
    Tên: **securities_custody_revenue**

11. Mô tả: "Doanh thu nghiệp vụ tư vấn đầu tư tài chính" / "Doanh thu hoạt động tư vấn tài chính"
    Tên: **financial_advisory_revenue**

12. Mô tả: "Thu nhập hoạt động khác" / "Doanh thu hoạt động khác"
    Tên: **other_operating_income**

13. Mô tả: "Cộng doanh thu hoạt động"
    Tên: **total_operating_revenue**

**II. CHI PHÍ HOẠT ĐỘNG (11 trường)**

14. Mô tả: "Lỗ các TSTC ghi nhận thông qua lãi/lỗ" / "Lỗ từ các tài sản tài chính FVTPL"
    Tên: **interest_expense_on_financial_assets_recognized_through_p_and_l**
    ❌ KHÔNG dùng: loss_from_financial_assets_at_fvtpl

15. Mô tả: "Lỗ bán các TSTC ghi nhận thông qua lãi/lỗ" / "Lỗ bán các tài sản tài chính FVTPL"
    Tên: **interest_expense**
    ❌ KHÔNG dùng: loss_on_sale_of_financial_assets_at_fvtpl

16. Mô tả: "Chênh lệch giảm đánh giá lại các TSTC ghi nhận thông qua lãi/lỗ" / "Chênh lệch giảm đánh giá lại các tài sản tài chính FVTPL"
    Tên: **decrease_in_fair_value_of_financial_assets**
    ❌ KHÔNG dùng: unrealized_loss_on_remeasurement_of_financial_assets_at_fvtpl

17. Mô tả: "Chi phí giao dịch mua các TSTC thông qua lãi/lỗ" / "Chi phí giao dịch mua các tài sản tài chính FVTPL"
    Tên: **transaction_fees_for_financial_assets**
    ❌ KHÔNG dùng: transaction_costs_for_financial_assets_at_fvtpl

18. Mô tả: "Chi phí dự phòng TSTC, xử lý tổn thất..." / "Trích lập/(hoàn nhập) dự phòng tài sản tài chính..."
    Tên: **provisions_for_impairment_of_financial_assets**
    ❌ KHÔNG dùng: provision_for_financial_assets_and_loans

19. Mô tả: "Chi phí hoạt động tư doanh" / "Chi phí hoạt động tự doanh"
    Tên: **operating_expense**
    ❌ KHÔNG dùng: proprietary_trading_expenses

20. Mô tả: "Chi phí môi giới chứng khoán" / "Chi phí nghiệp vụ môi giới chứng khoán"
    Tên: **brokerage_fees**
    ❌ KHÔNG dùng: brokerage_service_expenses

21. Mô tả: "Chi phí hoạt động bảo lãnh, đại lý phát hành chứng khoán" / "Chi phí nghiệp vụ bảo lãnh..."
    Tên: **underwriting_and_bond_issuance_costs**
    ❌ KHÔNG dùng: underwriting_and_issuance_agency_expenses

22. Mô tả: "Chi phí tư vấn, đầu tư chứng khoán" / "Chi phí nghiệp vụ tư vấn đầu tư chứng khoán"
    Tên: **investment_advisory_expenses**
    ❌ KHÔNG dùng: securities_investment_advisory_expenses

23. Mô tả: "Chi phí nghiệp vụ lưu ký chứng khoán"
    Tên: **securities_custody_expenses**

24. Mô tả: "Chi phí hoạt động khác"
    Tên: **other_operating_expenses**

25. Mô tả: "Cộng chi phí hoạt động"
    Tên: **total_operating_expenses**

**III. DOANH THU HOẠT ĐỘNG TÀI CHÍNH (4 trường)**

26. Mô tả: "Chênh lệch lãi tỷ giá hối đoái đã và chưa thực hiện"
    Tên: **increase_decrease_in_fair_value_of_exchange_rate_and_unrealized**
    ❌ KHÔNG dùng: realized_and_unrealized_exchange_rate_gain

27. Mô tả: "Doanh thu lãi tiền gửi phát sinh trong năm" / "Doanh thu, dự thu cổ tức, lãi tiền gửi không cố định"
    Tên: **interest_income_from_deposits**
    ❌ KHÔNG dùng: dividends_and_interest_income_from_non_fixed_deposits

28. Mô tả: "Doanh thu khác về đầu tư" (gộp cả "Lãi bán, thanh lý các khoản đầu tư vào công ty con..." nếu có)
    Tên: **other_investment_income**

29. Mô tả: "Cộng doanh thu hoạt động tài chính"
    Tên: **total_financial_operating_revenue**

**IV. CHI PHÍ TÀI CHÍNH (4 trường)**

30. Mô tả: "Chênh lệch lỗ tỷ giá hối đoái đã và chưa thực hiện"
    Tên: **increase_decrease_in_fair_value_of_exchange_rate_loss**
    ❌ KHÔNG dùng: realized_and_unrealized_exchange_rate_loss

31. Mô tả: "Chi phí lãi vay"
    Tên: **interest_expense_on_borrowings**
    ❌ KHÔNG dùng: interest_expense (tên này đã dùng cho trường #15)

32. Mô tả: "Chi phí tài chính khác"
    Tên: **other_financial_expenses**

33. Mô tả: "Cộng chi phí tài chính"
    Tên: **total_financial_expenses**

**V. CHI PHÍ QUẢN LÝ (1 trường)**

34. Mô tả: "Chi phí quản lý công ty chứng khoán" / "Chi phí quản lý"
    Tên: **general_and_administrative_expenses**
    ❌ KHÔNG dùng: administrative_expenses

**VI. KẾT QUẢ HOẠT ĐỘNG (1 trường)**

35. Mô tả: "Kết quả hoạt động"
    Tên: **operating_profit**
    ❌ KHÔNG dùng: operating_result

**VII. THU NHẬP VÀ CHI PHÍ KHÁC (3 trường)**

36. Mô tả: "Thu nhập khác"
    Tên: **other_income**

37. Mô tả: "Chi phí khác"
    Tên: **other_expenses**

38. Mô tả: "Cộng kết quả hoạt động khác"
    Tên: **net_other_income_and_expenses**
    ❌ KHÔNG dùng: total_other_activities_result

**VIII. LỢI NHUẬN TRƯỚC THUẾ (3 trường)**

39. Mô tả: "Tổng lợi nhuận kế toán trước thuế"
    Tên: **accounting_profit_before_tax**
    ❌ KHÔNG dùng: profit_before_tax

40. Mô tả: "Lợi nhuận đã thực hiện"
    Tên: **realized_profit**
    ❌ KHÔNG dùng: retained_earnings_realized

41. Mô tả: "(Lỗ)/lợi nhuận chưa thực hiện" / "Lợi nhuận chưa thực hiện"
    Tên: **unrealized_profit_loss**
    ❌ KHÔNG dùng: retained_earnings_unrealized

**IX. CHI PHÍ THUẾ (3 trường)**

42. Mô tả: "Chi phí thuế TNDN hiện hành"
    Tên: **current_corporate_income_tax_expense**

43. Mô tả: "(Lợi ích)/chi phí thuế TNDN hoãn lại" / "Chi phí/(thu nhập) thuế TNDN hoãn lại"
    Tên: **benefit_from_deferred_income_tax_expense**
    ❌ KHÔNG dùng: deferred_income_tax_expense

44. Mô tả: "Chi phí thuế thu nhập doanh nghiệp (TNDN)" / "Chi phí thuế TNDN"
    Tên: **total_corporate_income_tax**
    ❌ KHÔNG dùng: corporate_income_tax_expense

**X. LỢI NHUẬN SAU THUẾ (1 trường)**

45. Mô tả: "Lợi nhuận kế toán sau thuế TNDN"
    Tên: **net_profit_after_tax**
    ❌ KHÔNG dùng: profit_after_tax

VÍ DỤ INPUT-OUTPUT CHUẨN:

**VÍ DỤ 1: Báo cáo đơn giản**
INPUT (từ PDF):
```
Mã số: 01
Lãi từ các TSTC ghi nhận thông qua lãi/lỗ: 18.718.169.267
Mã số: 02
Lãi từ các khoản đầu tư nắm giữ đến ngày đáo hạn: 112.885.074.974
```

OUTPUT ĐÚNG:
```json
[
  {"name":"interest_and_fee_income_from_financial_assets_recognized_through_p_and_l","value":18718169267},
  {"name":"interest_income_from_held_to_maturity_investments","value":112885074974}
]
```

OUTPUT SAI (KHÔNG được phép):
```json
[
  {"name":"income_from_financial_assets_at_fvtpl","value":18718169267},
  {"name":"interest_income_from_htm","value":112885074974}
]
```

**VÍ DỤ 2: Báo cáo phức tạp**
INPUT (từ PDF):
```
01. Lãi từ các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL): 3.166.865.050.788
    01.1 Lãi bán các tài sản tài chính FVTPL: 1.087.667.751.126
    01.2 Chênh lệch tăng về đánh giá lại các tài sản tài chính FVTPL: 177.162.004.311
06. Doanh thu nghiệp vụ môi giới chứng khoán: 1.502.190.490.196
```

OUTPUT ĐÚNG:
```json
[
  {"name":"interest_and_fee_income_from_financial_assets_recognized_through_p_and_l","value":3166865050788},
  {"name":"interest_income_from_financial_assets_recognized_through_p_and_l","value":1087667751126},
  {"name":"increase_decrease_in_fair_value_of_financial_assets_recognized_through_p_and_l","value":177162004311},
  {"name":"brokerage_revenue","value":1502190490196}
]
```

OUTPUT SAI (KHÔNG được phép):
```json
[
  {"name":"income_from_financial_assets_at_fvtpl","value":3166865050788},
  {"name":"gain_on_sale_of_financial_assets_at_fvtpl","value":1087667751126},
  {"name":"unrealized_gain_on_remeasurement_of_financial_assets_at_fvtpl","value":177162004311},
  {"name":"brokerage_service_revenue","value":1502190490196}
]
```

LƯU Ý ĐẶC BIỆT:
- BỎ QUA hoàn toàn các mục về: chứng quyền, AFS, phân bổ lợi nhuận, thu nhập toàn diện, EPS
- Với mục "Doanh thu khác về đầu tư": nếu có cả "Lãi bán, thanh lý các khoản đầu tư vào công ty con..." và "Doanh thu khác về đầu tư" → CỘNG cả 2 giá trị lại
- Luôn sử dụng TÊN DÀI trong bảng ánh xạ, không rút gọn

HƯỚNG DẪN THỰC HIỆN:
1. Đọc toàn bộ PDF
2. Với mỗi dòng, tìm mô tả khớp trong bảng ánh xạ
3. Sử dụng CHÍNH XÁC tên thuộc tính đã cho (không thay đổi, không rút gọn)
4. Nếu không chắc chắn → BỎ QUA
5. Xuất JSON theo thứ tự 1-45

OUTPUT: CHỈ JSON array như ví dụ, KHÔNG có text khác.
"""


def get_data_prompt_by_section(document_type: str, section_type: str) -> str:
    if (
        document_type == "securities_financial_report"
        and section_type == "financial_statement"
    ):
        return SECURITIES_FINANCIAL_STATEMENT_PROMPT
    if (
        document_type == "securities_financial_report"
        and section_type == "income_statement"
    ):
        return SECURITIES_FINANCIAL_STATEMENT_PROMPT
    else:
        raise ValueError(
            f"could not find prompt for {document_type} and {section_type}"
        )
