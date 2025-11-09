SECURITIES_FINANCIAL_STATEMENT_PROMPT = """
Từ nội dung PDF báo cáo tình hình tài chính hợp nhất của công ty chứng khoán, hãy trích xuất dữ liệu thành định dạng JSON theo BẢNG ÁNH XẠ và VÍ DỤ CHUẨN bên dưới.

YÊU CẦU CẤU TRÚC JSON:
1. Sử dụng giá trị tại ngày cuối kỳ báo cáo (cột có năm lớn nhất - thường là "Số cuối năm" hoặc cột năm gần nhất như 31/12/2024)
2. Chuyển đổi số: loại bỏ dấu phân cách (dấu chấm hoặc dấu phẩy), "()" = số âm, "-" = null
3. Mỗi object có 3 attributes theo ĐÚNG THỨ TỰ NÀY:
   - "description": Tên tiếng Việt CHÍNH XÁC như trong PDF (giữ nguyên chữ hoa/thường, loại bỏ phần công thức tính như "(100=110+130)")
   - "name": Tên tiếng Anh (snake_case) - PHẢI KHỚP CHÍNH XÁC với bảng ánh xạ
   - "value": Giá trị số (integer hoặc null)
4. CHỈ TRẢ VỀ JSON ARRAY: [{"description":"...","name":"...","value":123},...]
5. KHÔNG có text giải thích thêm

NGUYÊN TẮC QUAN TRỌNG NHẤT:
⚠️ SỬ DỤNG CHÍNH XÁC TÊN THUỘC TÍNH TRONG BẢNG - KHÔNG ĐƯỢC THAY ĐỔI hoặc SÁNG TẠO TÊN MỚI
⚠️ Description phải lấy CHÍNH XÁC tên tiếng Việt từ PDF - không được diễn giải, rút gọn hoặc thay đổi
⚠️ Loại bỏ hoàn toàn phần công thức tính toán trong ngoặc đơn ví dụ: "(100=110+130)", "(200=210+220+250)", "(270=100+200)"
⚠️ Chỉ trích xuất các trường có giá trị số cụ thể
⚠️ BỎ QUA hoàn toàn phần "CÁC CHỈ TIÊU NGOÀI BÁO CÁO TÌNH HÌNH TÀI CHÍNH HỢP NHẤT"
⚠️ Nếu không tìm thấy mục trong PDF → BỎ QUA, không tạo giá trị giả
⚠️ Nếu không chắc chắn về mapping → BỎ QUA thay vì dùng tên sai

ĐẶC ĐIỂM NHẬN DẠNG BÁO CÁO TÌNH HÌNH TÀI CHÍNH HỢP NHẤT:
- Có cột "Mã số", "CHỈ TIÊU" hoặc "Thuyết minh"
- Cấu trúc: A. TÀI SẢN NGẮN HẠN, B. TÀI SẢN DÀI HẠN, C. NỢ PHẢI TRẢ, D. VỐN CHỦ SỞ HỮU
- Dùng ký hiệu mã số: 100, 110, 111, 111.1, 111.2... hoặc A., I., 1., 1.1., 1.2...
- Có thể dùng từ viết tắt: TSTC (Tài sản tài chính), FVTPL, HTM, AFS, TSCĐ (Tài sản cố định)
- Số âm được biểu diễn bằng dấu ngoặc đơn: (39.586.100.297)
- Dấu phân cách nghìn là dấu chấm: 70.932.391.912.367
- Đơn vị tính: VND hoặc đồng

BẢNG ÁNH XẠ CHI TIẾT - 130 TRƯỜNG CHUẨN:

**I. TÀI SẢN NGẮN HẠN (36 trường)**

1. Tìm trong PDF các biến thể:
   - "TÀI SẢN NGẮN HẠN" / "A. TÀI SẢN NGẮN HẠN" / "Tài sản ngắn hạn"
   Tên chuẩn: **short_term_assets**

2. Tìm trong PDF:
   - "Tài sản tài chính" / "I. Tài sản tài chính"
   Tên chuẩn: **financial_assets**

3. Tìm trong PDF:
   - "Tiền và các khoản tương đương tiền"
   Tên chuẩn: **cash_and_cash_equivalents**

4. Tìm trong PDF:
   - "Tiền"
   Tên chuẩn: **cash**

5. Tìm trong PDF:
   - "Các khoản tương đương tiền"
   Tên chuẩn: **cash_equivalents**

6. Tìm trong PDF các biến thể:
   - "Các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL)"
   - "Các tài sản tài chính (TSTC) ghi nhận thông qua lãi/lỗ"
   - "Các TSTC ghi nhận thông qua lãi/lỗ (FVTPL)"
   Tên chuẩn: **financial_assets_at_fair_value_through_profit_or_loss**

7. Tìm trong PDF các biến thể:
   - "Các khoản đầu tư nắm giữ đến ngày đáo hạn (HTM)"
   - "Các khoản đầu tư nắm giữ đến ngày đáo hạn"
   Tên chuẩn: **held_to_maturity_investments**

8. Tìm trong PDF:
   - "Các khoản cho vay" / "Cho vay"
   Tên chuẩn: **loans**

9. Tìm trong PDF:
   - "Tài sản tài chính sẵn sàng để bán (AFS)"
   Tên chuẩn: **available_for_sale_financial_assets**

10. Tìm trong PDF các biến thể:
    - "Dự phòng suy giảm giá trị các tài sản tài chính và tài sản thế chấp"
    - "Dự phòng suy giảm giá trị các TSTC và tài sản thế chấp"
    Tên chuẩn: **provision_for_impairment_of_financial_assets_and_collateral**

11. Tìm trong PDF:
    - "Các khoản phải thu" / "Phải thu"
    Tên chuẩn: **receivables**

12. Tìm trong PDF:
    - "Phải thu bán các tài sản tài chính"
    Tên chuẩn: **receivables_from_sale_of_financial_assets**

13. Tìm trong PDF các biến thể:
    - "Phải thu và dự thu cổ tức, tiền lãi các tài sản tài chính"
    - "Phải thu và dự thu cổ tức, tiền lãi các TSTC"
    Tên chuẩn: **dividends_and_interest_receivable**

14. Tìm trong PDF:
    - "Phải thu cổ tức, tiền lãi đến ngày nhận"
    Tên chuẩn: **dividends_and_interest_receivable_due**

15. Tìm trong PDF:
    - "Dự thu cổ tức, tiền lãi chưa đến ngày nhận"
    Tên chuẩn: **accrued_dividends_and_interest_receivable**

16. Tìm trong PDF:
    - "Trả trước cho người bán"
    Tên chuẩn: **prepayments_to_suppliers**

17. Tìm trong PDF các biến thể:
    - "Phải thu các dịch vụ CTCK cung cấp"
    - "Phải thu các dịch vụ công ty chứng khoán cung cấp"
    Tên chuẩn: **receivables_from_securities_services**

18. Tìm trong PDF:
    - "Phải thu nội bộ"
    Tên chuẩn: **internal_receivables**

19. Tìm trong PDF:
    - "Phải thu về lỗi giao dịch chứng khoán"
    Tên chuẩn: **receivables_from_securities_trading_errors**

20. Tìm trong PDF:
    - "Các khoản phải thu khác"
    Tên chuẩn: **other_receivables**

21. Tìm trong PDF:
    - "Dự phòng suy giảm giá trị các khoản phải thu"
    Tên chuẩn: **provision_for_doubtful_debts**

22. Tìm trong PDF:
    - "Tài sản ngắn hạn khác" / "II. Tài sản ngắn hạn khác"
    Tên chuẩn: **other_short_term_assets**

23. Tìm trong PDF:
    - "Tạm ứng"
    Tên chuẩn: **advances**

24. Tìm trong PDF:
    - "Vật tư văn phòng, công cụ, dụng cụ"
    Tên chuẩn: **office_supplies_and_tools**

25. Tìm trong PDF:
    - "Chi phí trả trước ngắn hạn"
    Tên chuẩn: **short_term_prepaid_expenses**

26. Tìm trong PDF:
    - "Cầm cố, thế chấp, ký quỹ, ký cược ngắn hạn"
    Tên chuẩn: **short_term_collateral_and_deposits**

27. Tìm trong PDF:
    - "Thuế giá trị gia tăng được khấu trừ"
    Tên chuẩn: **deductible_value_added_tax**

28. Tìm trong PDF:
    - "Thuế và các khoản khác phải thu Nhà nước"
    Tên chuẩn: **taxes_and_other_receivables_from_the_state**

29. Tìm trong PDF:
    - "Tài sản ngắn hạn khác" (mục chi tiết, khác với mục tổng II.)
    Tên chuẩn: **other_current_assets**

30. Tìm trong PDF:
    - "Giao dịch mua bán lại trái phiếu Chính phủ" (trong TÀI SẢN)
    Tên chuẩn: **repurchase_agreements_for_government_bonds**

31. Tìm trong PDF:
    - "Dự phòng suy giảm giá trị tài sản ngắn hạn khác"
    Tên chuẩn: **provision_for_impairment_of_other_short_term_assets**

**II. TÀI SẢN DÀI HẠN (30 trường)**

32. Tìm trong PDF:
    - "TÀI SẢN DÀI HẠN" / "B. TÀI SẢN DÀI HẠN" / "Tài sản dài hạn"
    Tên chuẩn: **long_term_assets**

33. Tìm trong PDF:
    - "Tài sản tài chính dài hạn" / "I. Tài sản tài chính dài hạn"
    Tên chuẩn: **long_term_financial_assets**

34. Tìm trong PDF:
    - "Các khoản phải thu dài hạn"
    Tên chuẩn: **long_term_receivables**

35. Tìm trong PDF:
    - "Các khoản đầu tư" (trong phần dài hạn)
    Tên chuẩn: **investments**

36. Tìm trong PDF:
    - "Các khoản đầu tư nắm giữ đến ngày đáo hạn" (trong phần dài hạn, mục 2.1)
    Tên chuẩn: **long_term_held_to_maturity_investments**

37. Tìm trong PDF:
    - "Đầu tư vào công ty con"
    Tên chuẩn: **investments_in_subsidiaries**

38. Tìm trong PDF:
    - "Đầu tư vào công ty liên doanh, liên kết"
    Tên chuẩn: **investments_in_joint_ventures_and_associates**

39. Tìm trong PDF:
    - "Đầu tư dài hạn khác"
    Tên chuẩn: **other_long_term_investments**

40. Tìm trong PDF:
    - "Dự phòng suy giảm tài sản tài chính dài hạn"
    Tên chuẩn: **provision_for_impairment_of_long_term_financial_assets**

41. Tìm trong PDF:
    - "Tài sản cố định" / "II. Tài sản cố định"
    Tên chuẩn: **fixed_assets**

42. Tìm trong PDF:
    - "Tài sản cố định hữu hình" (giá trị ròng)
    Tên chuẩn: **tangible_fixed_assets**

43. Tìm trong PDF:
    - "Nguyên giá" (của TSCĐ hữu hình)
    Tên chuẩn: **tangible_fixed_assets_cost**

44. Tìm trong PDF:
    - "Giá trị hao mòn lũy kế" (của TSCĐ hữu hình)
    Tên chuẩn: **accumulated_depreciation_of_tangible_fixed_assets**

45. Tìm trong PDF:
    - "Đánh giá TSCĐHH theo giá trị hợp lý"
    Tên chuẩn: **fair_value_adjustment_of_tangible_fixed_assets**

46. Tìm trong PDF:
    - "Tài sản cố định thuê tài chính" (giá trị ròng)
    Tên chuẩn: **finance_lease_fixed_assets**

47. Tìm trong PDF:
    - "Nguyên giá" (của TSCĐ thuê tài chính)
    Tên chuẩn: **finance_lease_fixed_assets_cost**

48. Tìm trong PDF:
    - "Giá trị hao mòn lũy kế" (của TSCĐ thuê tài chính)
    Tên chuẩn: **accumulated_depreciation_of_finance_lease_fixed_assets**

49. Tìm trong PDF:
    - "Đánh giá TSCĐTTC theo giá trị hợp lý"
    Tên chuẩn: **fair_value_adjustment_of_finance_lease_fixed_assets**

50. Tìm trong PDF:
    - "Tài sản cố định vô hình" (giá trị ròng)
    Tên chuẩn: **intangible_fixed_assets**

51. Tìm trong PDF:
    - "Nguyên giá" (của TSCĐ vô hình)
    Tên chuẩn: **intangible_fixed_assets_cost**

52. Tìm trong PDF:
    - "Giá trị hao mòn lũy kế" (của TSCĐ vô hình)
    Tên chuẩn: **accumulated_amortization_of_intangible_fixed_assets**

53. Tìm trong PDF:
    - "Đánh giá TSCĐVH theo giá trị hợp lý"
    Tên chuẩn: **fair_value_adjustment_of_intangible_fixed_assets**

54. Tìm trong PDF:
    - "Bất động sản đầu tư" / "III. Bất động sản đầu tư" (giá trị ròng)
    Tên chuẩn: **investment_property**

55. Tìm trong PDF:
    - "Nguyên giá" (của BĐS đầu tư)
    Tên chuẩn: **investment_property_cost**

56. Tìm trong PDF:
    - "Giá trị hao mòn lũy kế" (của BĐS đầu tư)
    Tên chuẩn: **accumulated_depreciation_of_investment_property**

57. Tìm trong PDF:
    - "Đánh giá BĐSĐT theo giá trị hợp lý"
    Tên chuẩn: **fair_value_adjustment_of_investment_property**

58. Tìm trong PDF:
    - "Chi phí xây dựng cơ bản dở dang" / "IV. Chi phí xây dựng cơ bản dở dang"
    Tên chuẩn: **construction_in_progress**

59. Tìm trong PDF:
    - "Tài sản dài hạn khác" / "V. Tài sản dài hạn khác"
    Tên chuẩn: **other_long_term_assets**

60. Tìm trong PDF:
    - "Cầm cố, thế chấp, ký quỹ, ký cược dài hạn"
    Tên chuẩn: **long_term_collateral_and_deposits**

61. Tìm trong PDF:
    - "Chi phí trả trước dài hạn"
    Tên chuẩn: **long_term_prepaid_expenses**

62. Tìm trong PDF:
    - "Tài sản thuế thu nhập hoãn lại"
    Tên chuẩn: **deferred_tax_assets**

63. Tìm trong PDF:
    - "Tiền nộp Quỹ Hỗ trợ thanh toán"
    Tên chuẩn: **deposits_to_clearing_support_fund**

64. Tìm trong PDF:
    - "Tài sản dài hạn khác" (mục chi tiết, khác với mục tổng V.)
    Tên chuẩn: **other_non_current_assets**

65. Tìm trong PDF:
    - "Dự phòng suy giảm giá trị tài sản dài hạn" / "VI. Dự phòng suy giảm giá trị tài sản dài hạn"
    Tên chuẩn: **provision_for_impairment_of_long_term_assets**

**III. TỔNG TÀI SẢN (1 trường)**

66. Tìm trong PDF:
    - "TỔNG CỘNG TÀI SẢN" / "TỔNG TÀI SẢN" / "Tổng cộng tài sản"
    Tên chuẩn: **total_assets**

**IV. NỢ PHẢI TRẢ NGẮN HẠN (20 trường)**

67. Tìm trong PDF:
    - "NỢ PHẢI TRẢ" / "C. NỢ PHẢI TRẢ" / "Nợ phải trả"
    Tên chuẩn: **liabilities**

68. Tìm trong PDF:
    - "Nợ phải trả ngắn hạn" / "I. Nợ phải trả ngắn hạn"
    Tên chuẩn: **short_term_liabilities**

69. Tìm trong PDF các biến thể:
    - "Vay và nợ thuê tài chính ngắn hạn"
    - "Vay và nợ thuê tài sản tài chính ngắn hạn"
    - "Vay và nợ thuê TSTC ngắn hạn"
    Tên chuẩn: **short_term_borrowings_and_finance_lease_liabilities**

70. Tìm trong PDF:
    - "Vay ngắn hạn" (mục chi tiết)
    Tên chuẩn: **short_term_borrowings**

71. Tìm trong PDF:
    - "Nợ thuê tài chính ngắn hạn"
    Tên chuẩn: **short_term_finance_lease_liabilities**

72. Tìm trong PDF:
    - "Vay tài sản tài chính ngắn hạn"
    Tên chuẩn: **short_term_borrowings_of_financial_assets**

73. Tìm trong PDF:
    - "Trái phiếu chuyển đổi ngắn hạn - Cấu phần nợ"
    Tên chuẩn: **short_term_convertible_bonds_debt_component**

74. Tìm trong PDF:
    - "Trái phiếu phát hành ngắn hạn"
    Tên chuẩn: **short_term_bonds_issued**

75. Tìm trong PDF:
    - "Vay Quỹ Hỗ trợ thanh toán"
    Tên chuẩn: **borrowings_from_clearing_support_fund**

76. Tìm trong PDF:
    - "Phải trả hoạt động giao dịch chứng khoán"
    Tên chuẩn: **payables_from_securities_trading_activities**

77. Tìm trong PDF:
    - "Phải trả về lỗi giao dịch các tài sản tài chính"
    Tên chuẩn: **payables_for_securities_trading_errors**

78. Tìm trong PDF:
    - "Phải trả người bán ngắn hạn"
    Tên chuẩn: **short_term_trade_payables**

79. Tìm trong PDF:
    - "Người mua trả tiền trước ngắn hạn"
    Tên chuẩn: **short_term_advances_from_customers**

80. Tìm trong PDF:
    - "Thuế và các khoản phải nộp Nhà nước"
    Tên chuẩn: **taxes_and_other_payables_to_the_state**

81. Tìm trong PDF:
    - "Phải trả người lao động"
    Tên chuẩn: **payables_to_employees**

82. Tìm trong PDF:
    - "Các khoản trích nộp phúc lợi nhân viên"
    Tên chuẩn: **accrued_employee_benefits**

83. Tìm trong PDF:
    - "Chi phí phải trả ngắn hạn"
    Tên chuẩn: **short_term_accrued_expenses**

84. Tìm trong PDF:
    - "Phải trả nội bộ ngắn hạn"
    Tên chuẩn: **short_term_internal_payables**

85. Tìm trong PDF:
    - "Doanh thu chưa thực hiện ngắn hạn"
    Tên chuẩn: **short_term_unearned_revenue**

86. Tìm trong PDF:
    - "Nhận ký quỹ, ký cược ngắn hạn"
    Tên chuẩn: **short_term_deposits_received**

87. Tìm trong PDF:
    - "Các khoản phải trả, phải nộp khác ngắn hạn"
    Tên chuẩn: **other_short_term_payables**

88. Tìm trong PDF:
    - "Dự phòng phải trả ngắn hạn"
    Tên chuẩn: **short_term_provisions**

89. Tìm trong PDF:
    - "Quỹ khen thưởng, phúc lợi"
    Tên chuẩn: **bonus_and_welfare_fund**

90. Tìm trong PDF:
    - "Giao dịch mua bán lại trái phiếu Chính phủ" (trong NỢ PHẢI TRẢ)
    Tên chuẩn: **repurchase_agreements_for_government_bonds_liabilities**

**V. NỢ PHẢI TRẢ DÀI HẠN (15 trường)**

91. Tìm trong PDF:
    - "Nợ phải trả dài hạn" / "II. Nợ phải trả dài hạn"
    Tên chuẩn: **long_term_liabilities**

92. Tìm trong PDF:
    - "Vay và nợ thuê tài chính dài hạn"
    Tên chuẩn: **long_term_borrowings_and_finance_lease_liabilities**

93. Tìm trong PDF:
    - "Vay dài hạn" (mục chi tiết)
    Tên chuẩn: **long_term_borrowings**

94. Tìm trong PDF:
    - "Nợ thuê tài chính dài hạn"
    Tên chuẩn: **long_term_finance_lease_liabilities**

95. Tìm trong PDF:
    - "Vay tài sản tài chính dài hạn"
    Tên chuẩn: **long_term_borrowings_of_financial_assets**

96. Tìm trong PDF:
    - "Trái phiếu chuyển đổi dài hạn - Cấu phần nợ"
    Tên chuẩn: **long_term_convertible_bonds_debt_component**

97. Tìm trong PDF:
    - "Trái phiếu phát hành dài hạn"
    Tên chuẩn: **long_term_bonds_issued**

98. Tìm trong PDF:
    - "Phải trả người bán dài hạn"
    Tên chuẩn: **long_term_trade_payables**

99. Tìm trong PDF:
    - "Người mua trả tiền trước dài hạn"
    Tên chuẩn: **long_term_advances_from_customers**

100. Tìm trong PDF:
     - "Chi phí phải trả dài hạn"
     Tên chuẩn: **long_term_accrued_expenses**

101. Tìm trong PDF:
     - "Phải trả nội bộ dài hạn"
     Tên chuẩn: **long_term_internal_payables**

102. Tìm trong PDF:
     - "Doanh thu chưa thực hiện dài hạn"
     Tên chuẩn: **long_term_unearned_revenue**

103. Tìm trong PDF:
     - "Nhận ký quỹ, ký cược dài hạn"
     Tên chuẩn: **long_term_deposits_received**

104. Tìm trong PDF:
     - "Các khoản phải trả, phải nộp khác dài hạn"
     Tên chuẩn: **other_long_term_payables**

105. Tìm trong PDF:
     - "Dự phòng phải trả dài hạn"
     Tên chuẩn: **long_term_provisions**

106. Tìm trong PDF:
     - "Quỹ bảo vệ Nhà đầu tư"
     Tên chuẩn: **investor_protection_fund**

107. Tìm trong PDF:
     - "Thuế thu nhập hoãn lại phải trả"
     Tên chuẩn: **deferred_tax_liabilities**

108. Tìm trong PDF:
     - "Quỹ phát triển khoa học và công nghệ"
     Tên chuẩn: **science_and_technology_development_fund**

**VI. VỐN CHỦ SỞ HỮU (18 trường)**

109. Tìm trong PDF:
     - "VỐN CHỦ SỞ HỮU" / "D. VỐN CHỦ SỞ HỮU" / "Vốn chủ sở hữu" (tổng)
     Tên chuẩn: **owners_equity**

110. Tìm trong PDF:
     - "Vốn chủ sở hữu" / "I. Vốn chủ sở hữu" (chi tiết)
     Tên chuẩn: **equity**

111. Tìm trong PDF:
     - "Vốn đầu tư của chủ sở hữu"
     Tên chuẩn: **capital**

112. Tìm trong PDF:
     - "Vốn góp của chủ sở hữu" (tổng)
     Tên chuẩn: **share_capital**

113. Tìm trong PDF:
     - "Cổ phiếu phổ thông có quyền biểu quyết"
     Tên chuẩn: **ordinary_shares_with_voting_rights**

114. Tìm trong PDF:
     - "Cổ phiếu ưu đãi"
     Tên chuẩn: **preferred_shares**

115. Tìm trong PDF:
     - "Thặng dư vốn cổ phần"
     Tên chuẩn: **share_premium**

116. Tìm trong PDF:
     - "Quyền chọn chuyển đổi trái phiếu - Cấu phần vốn"
     Tên chuẩn: **convertible_bonds_equity_component**

117. Tìm trong PDF:
     - "Vốn khác của chủ sở hữu"
     Tên chuẩn: **other_capital**

118. Tìm trong PDF:
     - "Cổ phiếu quỹ"
     Tên chuẩn: **treasury_shares**

119. Tìm trong PDF:
     - "Chênh lệch đánh giá tài sản theo giá trị hợp lý"
     Tên chuẩn: **fair_value_adjustment_of_assets**

120. Tìm trong PDF:
     - "Chênh lệch tỷ giá hối đoái"
     Tên chuẩn: **foreign_exchange_differences**

121. Tìm trong PDF:
     - "Quỹ dự trữ bổ sung vốn điều lệ"
     Tên chuẩn: **supplementary_charter_capital_reserve**

122. Tìm trong PDF:
     - "Quỹ dự phòng tài chính và rủi ro nghiệp vụ"
     Tên chuẩn: **financial_reserve_and_business_risk_fund**

123. Tìm trong PDF:
     - "Các Quỹ khác thuộc vốn chủ sở hữu"
     Tên chuẩn: **other_funds_under_owners_equity**

124. Tìm trong PDF:
     - "Lợi nhuận chưa phân phối" (tổng)
     Tên chuẩn: **retained_earnings**

125. Tìm trong PDF:
     - "Lợi nhuận sau thuế đã thực hiện"
     Tên chuẩn: **realized_retained_earnings**

126. Tìm trong PDF:
     - "Lợi nhuận chưa thực hiện" (mục chi tiết trong Lợi nhuận chưa phân phối)
     Tên chuẩn: **unrealized_retained_earnings**

127. Tìm trong PDF:
     - "Nguồn kinh phí và quỹ khác" / "II. Nguồn kinh phí và quỹ khác"
     Tên chuẩn: **funding_and_other_funds**

**VII. TỔNG NỢ VÀ VỐN (1 trường)**

128. Tìm trong PDF:
     - "TỔNG CỘNG NỢ VÀ VỐN CHỦ SỞ HỮU" / "TỔNG CỘNG NỢ PHẢI TRẢ VÀ VỐN CHỦ SỞ HỮU"
     Tên chuẩn: **total_liabilities_and_owners_equity**

VÍ DỤ INPUT-OUTPUT CHUẨN:

**VÍ DỤ 1: Báo cáo EY - SSI 2024**
INPUT (từ PDF):
```
Mã số 100 | A. TÀI SẢN NGẮN HẠN | 70.932.391.912.367
Mã số 111 | Tiền và các khoản tương đương tiền | 239.000.238.200
Mã số 111.1 | Tiền | 208.969.991.625
Mã số 111.2 | Các khoản tương đương tiền | 30.030.246.575
Mã số 112 | Các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL) | 42.438.121.481.401
```

OUTPUT ĐÚNG:
```json
[
  {
    "description": "A. TÀI SẢN NGẮN HẠN",
    "name": "short_term_assets",
    "value": 70932391912367
  },
  {
    "description": "Tiền và các khoản tương đương tiền",
    "name": "cash_and_cash_equivalents",
    "value": 239000238200
  },
  {
    "description": "Tiền",
    "name": "cash",
    "value": 208969991625
  },
  {
    "description": "Các khoản tương đương tiền",
    "name": "cash_equivalents",
    "value": 30030246575
  },
  {
    "description": "Các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL)",
    "name": "financial_assets_at_fair_value_through_profit_or_loss",
    "value": 42438121481401
  }
]
```

**VÍ DỤ 2: Báo cáo KPMG - DNSE 2022**
INPUT (từ PDF):
```
Mã số 100 | TÀI SẢN NGẮN HẠN | 5.429.789.416.430
Mã số 111 | Tiền và các khoản tương đương tiền | 431.936.111.485
Mã số 111.1 | Tiền | 431.936.111.485
Mã số 112 | Các tài sản tài chính ("TSTC") ghi nhận thông qua lãi/lỗ | 575.600.703.154
Mã số 116 | Dự phòng suy giảm giá trị các TSTC và tài sản thế chấp | (39.586.100.297)
```

OUTPUT ĐÚNG:
```json
[
  {
    "description": "TÀI SẢN NGẮN HẠN",
    "name": "short_term_assets",
    "value": 5429789416430
  },
  {
    "description": "Tiền và các khoản tương đương tiền",
    "name": "cash_and_cash_equivalents",
    "value": 431936111485
  },
  {
    "description": "Tiền",
    "name": "cash",
    "value": 431936111485
  },
  {
    "description": "Các tài sản tài chính (\"TSTC\") ghi nhận thông qua lãi/lỗ",
    "name": "financial_assets_at_fair_value_through_profit_or_loss",
    "value": 575600703154
  },
  {
    "description": "Dự phòng suy giảm giá trị các TSTC và tài sản thế chấp",
    "name": "provision_for_impairment_of_financial_assets_and_collateral",
    "value": -39586100297
  }
]
```

**VÍ DỤ 3: Xử lý công thức**
INPUT (từ PDF):
```
Mã số 100 | A. TÀI SẢN NGẮN HẠN (100 = 110 + 130) | 70.932.391.912.367
Mã số 200 | B. TÀI SẢN DÀI HẠN (200 = 210 + 220 + 250) | 2.574.910.647.355
Mã số 270 | TỔNG CỘNG TÀI SẢN (270 = 100 + 200) | 73.507.302.559.722
```

OUTPUT ĐÚNG:
```json
[
  {
    "description": "A. TÀI SẢN NGẮN HẠN",
    "name": "short_term_assets",
    "value": 70932391912367
  },
  {
    "description": "B. TÀI SẢN DÀI HẠN",
    "name": "long_term_assets",
    "value": 2574910647355
  },
  {
    "description": "TỔNG CỘNG TÀI SẢN",
    "name": "total_assets",
    "value": 73507302559722
  }
]
```

LƯU Ý ĐẶC BIỆT:
- Trích xuất TẤT CẢ các trường có trong báo cáo khớp với 128 trường chuẩn
- Description phải giữ NGUYÊN VĂN từ PDF: giữ cả từ viết tắt TSTC, FVTPL, HTM, AFS, TSCĐ
- Loại bỏ hoàn toàn phần công thức trong ngoặc: "(100=110+130)" → chỉ giữ "A. TÀI SẢN NGẮN HẠN"
- Số âm: (39.586.100.297) → -39586100297
- Dấu gạch ngang "-" → null
- Dấu phân cách nghìn: loại bỏ khi convert
- BỎ QUA phần "CÁC CHỈ TIÊU NGOÀI BÁO CÁO TÌNH HÌNH TÀI CHÍNH HỢP NHẤT"

HƯỚNG DẪN THỰC HIỆN:
1. Đọc toàn bộ PDF, xác định các trang là phần chính của báo cáo (bỏ qua phần ngoài báo cáo)
2. Với mỗi mục, tìm kiếm mô tả khớp trong bảng ánh xạ 128 trường
3. Lấy CHÍNH XÁC tên tiếng Việt từ PDF làm "description", loại bỏ phần công thức
4. Sử dụng CHÍNH XÁC tên thuộc tính chuẩn làm "name"
5. Chuyển đổi giá trị: loại bỏ dấu phân cách, (số) → -số, "-" → null
6. Sắp xếp theo thứ tự: description - name - value
7. Trích xuất tất cả các trường có trong báo cáo

OUTPUT: CHỈ JSON array như ví dụ, KHÔNG có text giải thích hay markdown.
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
