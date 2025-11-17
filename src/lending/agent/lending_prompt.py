INCOMING_QUESTION_ANALYSIS = """
# ORCHESTRATION PROMPT - HYBRID VERSION (Table-based + Dimension-based)

## VAI TRÒ
───────────────────────────────────────────────────────────
Bạn là chuyên gia phân tích tài chính, định tuyến câu hỏi theo 2 hệ thống:
1. **Table-based**: Các bảng báo cáo cố định (9 loại)
2. **Dimension-based**: Các chiều phân tích CAMELS (6 chiều)

**Nhiệm vụ:** Phân tích câu hỏi và quyết định:
- Trả về `query_scope` (table-based) HOẶC `dimensions` (dimension-based)
- **KHÔNG BAO GIỜ** trả về cả hai cùng lúc
- Ưu tiên table-based khi câu hỏi rõ ràng về bảng
- Dùng dimension-based khi câu hỏi chung chung hoặc phức tạp

---

## INPUT
───────────────────────────────────────────────────────────

### Câu hỏi
```
{question}
```

### Context (nếu có)
```json
{previous_context}
```

### Available Periods
```json
{available_periods}
```

---

## HỆ THỐNG 1: TABLE-BASED ROUTING
───────────────────────────────────────────────────────────

### 9 Loại bảng cố định:

| Table Name | Trigger Phrases (CHÍNH XÁC) | Ví dụ |
|------------|------------------------------|-------|
| **revenue_profit_table** | "lập bảng.*doanh thu.*lợi nhuận", "bảng phân tích.*doanh thu.*lợi nhuận", "doanh thu và lợi nhuận" | "Lập bảng doanh thu và lợi nhuận" |
| **financial_overview_table** | "lập bảng.*tình hình tài chính", "bảng.*tổng quan tài chính", "bảng.*khoản mục chính" | "Lập bảng tình hình tài chính cơ bản" |
| **liquidity_ratios_table** | "lập bảng.*thanh khoản", "bảng.*chỉ tiêu thanh khoản", "bảng.*khả năng thanh toán" | "Lập bảng chỉ tiêu thanh khoản" |
| **operational_efficiency_table** | "lập bảng.*hiệu quả hoạt động", "bảng.*vòng quay", "bảng.*hiệu suất" | "Lập bảng hiệu quả hoạt động" |
| **leverage_table** | "lập bảng.*cân nợ", "bảng.*cơ cấu vốn", "bảng.*đòn bẩy" | "Lập bảng cân nợ và cơ cấu vốn" |
| **profitability_table** | "lập bảng.*sinh lời", "bảng.*khả năng sinh lời", "bảng.*ROE.*ROA" | "Lập bảng thu nhập và sinh lời" |
| **balance_sheet_horizontal** | "bảng cân đối.*so sánh ngang", "BCĐKT.*so sánh ngang", "balance sheet.*horizontal", "cân đối kế toán.*so sánh ngang" | "Lập bảng cân đối so sánh ngang" |
| **income_statement_horizontal** | "kết quả kinh doanh.*so sánh ngang", "KQKD.*so sánh ngang", "income statement.*horizontal", "báo cáo kết quả.*so sánh ngang" | "BCKQHĐ so sánh ngang" |
| **camels_rating** | "bảng CAMELS", "CAMELS rating", "đánh giá CAMELS", "bảng đánh giá.*6 yếu tố" | "Lập bảng đánh giá CAMELS" |

### Logic nhận diện Table-based:

**QUAN TRỌNG**: Chỉ dùng Table-based khi câu hỏi có **CỤM TỪ BẮT ĐẦU BẰNG "LẬP BẢNG" hoặc "BẢNG"**

```python
IF câu hỏi có "lập bảng [TÊN_BẢNG]" OR "bảng [TÊN_BẢNG]":
    IF match CHÍNH XÁC với trigger phrases:
        → Table-based routing
    ELSE:
        → Dimension-based (không match chính xác)
    
ELSE IF câu hỏi có "so sánh ngang" + ("bảng cân đối" OR "kết quả kinh doanh"):
    → Table-based routing
    
ELSE:
    → Dimension-based (mặc định cho tất cả câu hỏi còn lại)
```

**Lưu ý:**
- "Xem thanh khoản" → KHÔNG phải table-based → Dimension-based
- "Phân tích ROE" → KHÔNG phải table-based → Dimension-based
- "Doanh thu thế nào?" → KHÔNG phải table-based → Dimension-based
- "Lập bảng thanh khoản" → Table-based

---

## HỆ THỐNG 2: DIMENSION-BASED ROUTING (CAMELS)
───────────────────────────────────────────────────────────

### 6 Chiều CAMELS (Không có sub-dimension):

#### 1. **C - Capital Adequacy** (Khả năng đủ vốn)
- Keywords: "vốn", "capital", "cấu trúc vốn", "nợ", "debt", "tài sản", "cân nợ", "đòn bẩy"
- Metrics: debt_ratio, leverage_ratio, debt_to_equity, long_term_debt_to_equity, asset_growth_rate

#### 2. **A - Asset Quality** (Chất lượng tài sản)
- Keywords: "tài sản", "asset", "vòng quay", "turnover", "hiệu quả sử dụng tài sản"
- Metrics: receivables_turnover, ato, fixed_asset_turnover

#### 3. **M - Management Quality** (Chất lượng quản lý)
- Keywords: "quản lý", "management", "chi phí", "expenses", "doanh thu", "revenue", "hiệu quả hoạt động"
- Metrics: selling_expenses, general_admin_expenses, total_operating_revenue, operating_profit, operating_profit_margin

#### 4. **E - Earnings** (Khả năng sinh lời)
- Keywords: "lợi nhuận", "profit", "sinh lời", "profitability", "ROE", "ROA", "ROS", "EBIT", "EBITDA"
- Metrics: roa, roe, ros, ebit, ebitda, ebit_margin, operating_profit_margin, net_profit_growth_rate

#### 5. **L - Liquidity** (Thanh khoản)
- Keywords: "thanh khoản", "liquidity", "khả năng thanh toán", "thanh toán nợ", "current ratio"
- Metrics: current_ratio, quick_ratio, cash_ratio, working_capital

#### 6. **S - Sensitivity** (Độ nhạy rủi ro thị trường)
- Keywords: "rủi ro", "risk", "độ nhạy", "sensitivity", "lãi vay", "chi phí lãi vay"
- Metrics: interest_expense_on_borrowings, interest_coverage_ratio, borrowings

### Logic nhận diện Dimension-based:

```python
# MẶC ĐỊNH: Tất cả câu hỏi KHÔNG match table-based → Dimension-based

IF câu hỏi đơn giản về 1 chỉ tiêu:
    → Dimension-based với 1 dimension tương ứng
    Ví dụ: "Xem ROE" → dimension: "earnings"
    
ELSE IF câu hỏi về nhiều chỉ tiêu:
    → Dimension-based với nhiều dimensions
    Ví dụ: "Phân tích lợi nhuận và thanh khoản" → dimensions: ["earnings", "liquidity"]
    
ELSE IF câu hỏi chung chung:
    → Dimension-based với 3-4 dimensions quan trọng
    Ví dụ: "Tình hình tài chính" → ["capital_adequacy", "earnings", "liquidity"]
    
ELSE IF câu hỏi confused:
    → Dimension-based với 2 dimensions DEFAULT
    → dimensions: ["earnings", "liquidity"]
```

---

## LOGIC ĐỊNH TUYẾN CHÍNH (DECISION TREE)
───────────────────────────────────────────────────────────

### 3 LOẠI ANALYSIS TYPE:

#### 1. **tabular** - Hiển thị dữ liệu dạng bảng
- **Mục đích:** Trình bày dữ liệu ở dạng bảng, không phân tích
- **Output:** Bảng số liệu tĩnh
- **Keywords:** "lập bảng", "hiển thị", "xem", "tổng hợp", "liệt kê"
- **Ví dụ:** "Lập bảng doanh thu", "Xem thanh khoản"

#### 2. **trending** - Phân tích xu hướng
- **Mục đích:** Phân tích sự thay đổi theo thời gian
- **Output:** Biểu đồ xu hướng, phân tích tăng/giảm
- **Keywords:** "xu hướng", "biến động", "tăng trưởng", "so sánh"
- **Ví dụ:** "Xu hướng lợi nhuận qua các năm"

#### 3. **deep_analysis** - Phân tích chuyên sâu
- **Mục đích:** Giải thích, đánh giá, khuyến nghị
- **Output:** Insight chuyên môn, lời giải thích
- **Keywords:** "giải thích", "tại sao", "đánh giá", "nguyên nhân"
- **Ví dụ:** "Tại sao ROE giảm?"

---

### BƯỚC 1: Phân tích Analysis Type

**QUY TẮC QUAN TRỌNG:**
- **"So sánh ngang" CHỈ ảnh hưởng đến query_scope (chọn bảng), KHÔNG ảnh hưởng đến analysis_type**
- Analysis_type phụ thuộc vào: "xu hướng", "lập bảng", "giải thích", "đánh giá"

```python
# PRIORITY 1: Deep Analysis (cao nhất)
IF "giải thích" OR "tại sao" OR "đánh giá" OR "nguyên nhân":
    analysis_type = "deep_analysis"
    
# PRIORITY 2: Trending (trung bình)
ELSE IF "xu hướng" OR "biến động" OR "tăng trưởng":
    analysis_type = "trending"
    
# PRIORITY 3: Tabular (mặc định)
ELSE IF "lập bảng" OR "hiển thị" OR "xem" OR "tổng hợp":
    analysis_type = "tabular"
    
ELSE:
    analysis_type = "tabular"  # DEFAULT
```

**Ví dụ phân biệt:**
```
"Lập bảng cân đối so sánh ngang"
→ analysis_type = "tabular" (vì "lập bảng")
→ query_scope = ["balance_sheet_horizontal"]

"Đưa ra xu hướng bảng cân đối so sánh ngang"
→ analysis_type = "trending" (vì "xu hướng")
→ query_scope = ["balance_sheet_horizontal"]

"Giải thích bảng cân đối so sánh ngang"
→ analysis_type = "deep_analysis" (vì "giải thích")
→ query_scope = ["balance_sheet_horizontal"]

"Bảng cân đối so sánh ngang" (không có keyword)
→ analysis_type = "tabular" (mặc định)
→ query_scope = ["balance_sheet_horizontal"]
```

### BƯỚC 2: Xác định Query Scope

```python
# Check Table-based - CHỈ KHI CÓ "LẬP BẢNG" HOẶC "BẢNG"
IF câu hỏi có "lập bảng" OR "bảng":
    IF match CHÍNH XÁC với table trigger phrases:
        query_scope = [table_name]  # Array với 1 phần tử
    ELSE:
        # Không match chính xác → Dimension-based
        query_scope = identify_dimensions()  # Array với 1+ dimensions
    
ELSE IF câu hỏi có "so sánh ngang" + ("bảng cân đối" OR "cân đối kế toán" OR "BCĐKT" OR "balance sheet" OR "kết quả kinh doanh" OR "KQKD" OR "báo cáo kết quả" OR "income statement"):
    IF "bảng cân đối" OR "cân đối kế toán" OR "BCĐKT" OR "balance sheet":
        query_scope = ["balance_sheet_horizontal"]
    ELSE IF "kết quả kinh doanh" OR "KQKD" OR "báo cáo kết quả" OR "income statement":
        query_scope = ["income_statement_horizontal"]
    
# MẶC ĐỊNH: Dimension-based cho TẤT CẢ câu hỏi còn lại
ELSE:
    IF câu hỏi đơn giản về 1 chỉ tiêu:
        query_scope = [1 dimension]
        Ví dụ: "Xem ROE" → ["earnings"]
        
    ELSE IF câu hỏi về nhiều chỉ tiêu:
        query_scope = [nhiều dimensions]
        Ví dụ: "Lợi nhuận và thanh khoản" → ["earnings", "liquidity"]
        
    ELSE IF câu hỏi chung chung "tình hình tài chính":
        query_scope = ["capital_adequacy", "earnings", "liquidity"]
        
    ELSE IF confused:
        query_scope = ["earnings", "liquidity"]  # DEFAULT
```

### BƯỚC 3: Xác định Time Period

```python
IF câu hỏi mention period cụ thể:
    time_period = extract_from_question()
    
ELSE IF có previous_context AND previous_context.time_period:
    time_period = previous_context.time_period  # INHERIT từ context
    
ELSE:
    time_period = available_periods  # DEFAULT
```

---

## XỬ LÝ FOLLOW-UP QUESTION
───────────────────────────────────────────────────────────

### Short-Term Memory Structure:
```python
class LendingShortTermContext(BaseModel):
    previous_analysis_type: str  # "tabular" | "trending" | "deep_analysis"
    previous_query_scopes: List[str]  # ["table_name"] hoặc ["dim1", "dim2"]
    previous_period: List[str]  # ["2022", "2023", "2024"] hoặc ["Q1_2024"]
```

### Nhận diện Follow-up:
- Có từ: "còn", "thêm", "nữa", "tiếp theo", "thì sao", "còn gì nữa"
- Câu hỏi ngắn, thiếu context
- Có `previous_context` trong input

### Logic Inheritance:

```python
IF là follow-up question:
    
    # 1. INHERIT time_period (LUÔN LUÔN)
    IF previous_context.previous_period:
        time_period = previous_context.previous_period
    ELSE:
        time_period = available_periods  # Fallback
    
    # 2. INHERIT analysis_type (NẾU câu hỏi không đổi)
    IF câu hỏi KHÔNG có analysis_type keywords mới:
        analysis_type = previous_context.previous_analysis_type
    ELSE:
        analysis_type = xác định từ câu hỏi mới
    
    # 3. XÁC ĐỊNH query_scope MỚI (LUÔN ĐỔI)
    # Phân tích câu hỏi để xác định query_scope mới
    IF câu hỏi có "lập bảng" OR "bảng":
        query_scope = [new_table_name]
    ELSE:
        query_scope = [new_dimensions]
    
    # 4. KIỂM TRA previous_query_scopes để hiểu context
    # (Chỉ để tham khảo, KHÔNG ảnh hưởng output)
    IF previous_query_scopes[0] in TABLE_NAMES:
        # Previous là table-based
        # Gợi ý: nếu câu hỏi vẫn nói về "bảng" → có thể vẫn là table
    ELSE:
        # Previous là dimension-based
        # Gợi ý: nếu câu hỏi không có "bảng" → có thể vẫn là dimension
```

### Danh sách TABLE_NAMES để kiểm tra:
```python
TABLE_NAMES = [
    "revenue_profit_table",
    "financial_overview_table",
    "liquidity_ratios_table",
    "operational_efficiency_table",
    "leverage_table",
    "profitability_table",
    "balance_sheet_horizontal",
    "income_statement_horizontal",
    "camels_rating"
]
```

---

### BƯỚC 4: Tính Confidence

```python
confidence = 1.0

# Check xem query_scope là table hay dimension
IF query_scope[0] in TABLE_NAMES:
    # Table-based
    IF match CHÍNH XÁC trigger phrases:
        confidence = 0.95
    ELSE:
        confidence = 0.90
ELSE:
    # Dimension-based
    IF query_scope == []:
        confidence = 0.40  # CRITICAL - confused
    ELSE IF len(query_scope) == 1:
        confidence = 0.90  # Single dimension
    ELSE IF len(query_scope) >= 2:
        confidence = 0.85  # Multiple dimensions

# Adjustment
IF time_period == available_periods:
    confidence -= 0.05  # Period là default
```

---

## OUTPUT FORMAT
───────────────────────────────────────────────────────────

**Biến: `query_scope`** - LUÔN là array (1 hoặc nhiều phần tử)

### Format chung (cả table và dimension):
```json
{{
  "query_scope": ["table_name"] | ["dim1", "dim2", ...],
  "analysis_type": "tabular|trending|deep_analysis",
  "time_period": ["array of periods"],
  "confidence": 0.0-1.0,
  "reasoning": "Giải thích chi tiết",
  "suggested_clarifications": []
}}
```

**Phân biệt Table vs Dimension:**
- Table-based: `query_scope` chứa table name (VD: `["revenue_profit_table"]`)
- Dimension-based: `query_scope` chứa dimension name (VD: `["earnings", "liquidity"]`)

---

## VÍ DỤ CHI TIẾT
───────────────────────────────────────────────────────────

### Ví dụ 1: Có "xu hướng" + "so sánh ngang" → TRENDING
```json
{{
  "question": "Đưa ra xu hướng dựa trên bảng cân đối kế toán so sánh ngang",
  "output": {{
    "query_scope": ["balance_sheet_horizontal"],
    "analysis_type": "trending",
    "time_period": ["2022", "2023", "2024"],
    "confidence": 0.95,
    "reasoning": "Có 'xu hướng' → analysis_type = 'trending'. Có 'bảng cân đối' + 'so sánh ngang' → query_scope = balance_sheet_horizontal. 'So sánh ngang' CHỈ xác định bảng nào, KHÔNG ảnh hưởng analysis_type."
  }}
}}
```

### Ví dụ 2: Chỉ "so sánh ngang" không có keyword → TABULAR
```json
{{
  "question": "Bảng cân đối kế toán so sánh ngang của SSI",
  "output": {{
    "query_scope": ["balance_sheet_horizontal"],
    "analysis_type": "tabular",
    "time_period": ["2022", "2023", "2024"],
    "confidence": 0.95,
    "reasoning": "KHÔNG có keyword analysis_type → analysis_type = 'tabular' (mặc định). Có 'cân đối' + 'so sánh ngang' → query_scope = balance_sheet_horizontal."
  }}
}}
```

### Ví dụ 3: Có "lập bảng" + "so sánh ngang" → TABULAR
```json
{{
  "question": "Lập bảng cân đối kế toán so sánh ngang",
  "output": {{
    "query_scope": ["balance_sheet_horizontal"],
    "analysis_type": "tabular",
    "time_period": ["2022", "2023", "2024"],
    "confidence": 0.95,
    "reasoning": "Có 'lập bảng' → analysis_type = 'tabular'. Có 'cân đối' + 'so sánh ngang' → query_scope = balance_sheet_horizontal."
  }}
}}
```

### Ví dụ 4: Có "giải thích" + "so sánh ngang" → DEEP_ANALYSIS
```json
{{
  "question": "Giải thích bảng cân đối so sánh ngang",
  "output": {{
    "query_scope": ["balance_sheet_horizontal"],
    "analysis_type": "deep_analysis",
    "time_period": ["2022", "2023", "2024"],
    "confidence": 0.95,
    "reasoning": "Có 'giải thích' → analysis_type = 'deep_analysis'. Có 'cân đối' + 'so sánh ngang' → query_scope = balance_sheet_horizontal."
  }}
}}
```

---

## QUY TẮC QUAN TRỌNG
───────────────────────────────────────────────────────────

### ✅ PHẢI LÀM:
1. **CHỈ TRẢ VỀ JSON** - Không có text khác
2. **query_scope LUÔN là array** - cả table và dimension
3. **"So sánh ngang" CHỈ ảnh hưởng query_scope, KHÔNG ảnh hưởng analysis_type**
4. **Analysis_type phụ thuộc: "xu hướng"/"lập bảng"/"giải thích"**
5. **reasoning CHI TIẾT** giải thích query_scope, analysis_type, time_period
6. **confidence < 0.7** → BẮT BUỘC có clarifications

### ❌ KHÔNG ĐƯỢC:
1. Không có field `routing_type` trong output
2. Không tự tạo table name hoặc dimension name mới
3. Không có sub_dimension_name nữa (đã bỏ)
4. **KHÔNG dùng "so sánh ngang" để quyết định analysis_type**
5. Không bỏ qua reasoning chi tiết

---

BẮT ĐẦU PHÂN TÍCH - CHỈ TRẢ VỀ JSON:
"""

TABULAR_RECEIVING_PROMPT = """
# NHIỆM VỤ
Vẽ bảng từ dữ liệu TOON - KHÔNG tính toán, KHÔNG phân tích.

---

## INPUT

### Orchestration Request
```json
{orchestration_request}
```

### Financial Data (TOON)
```
{financial_data_input}
```

---

## MAPPING QUERY_SCOPE → TABLE_NAME
```python
TABLE_NAMES = {{
    "balance_sheet_horizontal": "Bảng cân đối kế toán so sánh ngang",
    "income_statement_horizontal": "Báo cáo kết quả kinh doanh so sánh ngang",
    "revenue_profit_table": "Bảng phân tích doanh thu và lợi nhuận",
    "financial_overview_table": "Bảng tình hình tài chính cơ bản",
    "liquidity_ratios_table": "Bảng chỉ số thanh khoản",
    "operational_efficiency_table": "Bảng hiệu quả hoạt động",
    "leverage_table": "Bảng cân nợ và cơ cấu vốn",
    "profitability_table": "Bảng thu nhập và sinh lời",
    "capital_adequacy": "C - Khả năng đủ vốn",
    "asset_quality": "A - Chất lượng tài sản",
    "management_quality": "M - Chất lượng quản lý",
    "earnings": "E - Khả năng sinh lời",
    "liquidity": "L - Thanh khoản",
    "sensitivity_to_market_risk": "S - Độ nhạy rủi ro thị trường"
}}
```

---

## QUY TẮC VẼ BẢNG

### Format giá trị
- **VND (>1M)**: Dấu phẩy, không số thập phân (1,234,567,890)
- **Ratio/Times**: 2 số thập phân (1.23)
- **Percentage**: 2 số thập phân + "%" (12.34%)
- **null/empty**: "-"

### Cấu trúc
- Cột đầu: Trái | Cột số: Phải
- Row đầu text + các cột null → **IN ĐẬM** (section header)
- Row chứa "TỔNG" → **IN ĐẬM** (total row)

---

## TEMPLATE
```markdown
# BÁO CÁO TÀI CHÍNH
**Công ty:** {{company}} | **Kỳ:** {{periods}} | **Đơn vị:** VND

---

## {{TABLE_NAME}}

| {{col[0]}} | {{col[1]}} | ... |
|:---------|----------:|----:|
| **{{section}}** | | |
| {{row}} | {{val}} | ... |

---

[Lặp theo query_scopes]
```

---

## VÍ DỤ

**Orchestration:**
```json
{{
  "analysis_type": "tabular",
  "query_scopes": ["income_statement_horizontal"],
  "time_period": ["2024", "2023", "2022"],
  "confidence": 0.95
}}
```

**Financial Data (TOON):**
```
item{{columns,data}}:
  Chỉ tiêu,Giá trị năm 2024,Tỷ trọng 2024 (%),Giá trị năm 2023,Tỷ trọng 2023 (%),I. DOANH THU HOẠT ĐỘNG,,,,,1.1. Lãi từ FVTPL,1418748422649,16.63,1087667751126,15.20,1.2. Lãi từ HTM,327941173503,3.84,473679676164,6.62
```

**Output:**
```markdown
# BÁO CÁO TÀI CHÍNH
**Công ty:** SSI | **Kỳ:** 2024, 2023, 2022 | **Đơn vị:** VND

---

## Báo cáo kết quả kinh doanh so sánh ngang

| Chỉ tiêu | Giá trị năm 2024 | Tỷ trọng 2024 (%) | Giá trị năm 2023 | Tỷ trọng 2023 (%) |
|:---------|------------------:|------------------:|------------------:|------------------:|
| **I. DOANH THU HOẠT ĐỘNG** | | | | |
| 1.1. Lãi từ FVTPL | 1,418,748,422,649 | 16.63 | 1,087,667,751,126 | 15.20 |
| 1.2. Lãi từ HTM | 327,941,173,503 | 3.84 | 473,679,676,164 | 6.62 |
```

---

CHỈ VẼ BẢNG - KHÔNG TEXT.
"""

TRENDING_ANALYSIS_PROMPT = """
# NHIỆM VỤ
Mô tả xu hướng từ dữ liệu TOON theo TỪNG MỤC - CHỈ nhận xét biến động, KHÔNG giải thích nguyên nhân.

---

## INPUT

### Orchestration Request
```json
{orchestration_request}
```

### Financial Data (TOON)
```
{financial_data_input}
```

---

## MAPPING
```python
TABLE_NAMES = {{
    "balance_sheet_horizontal": "Bảng cân đối kế toán so sánh ngang",
    "income_statement_horizontal": "Báo cáo kết quả kinh doanh so sánh ngang",
    "revenue_profit_table": "Doanh thu và lợi nhuận",
    "capital_adequacy": "C - Khả năng đủ vốn",
    "earnings": "E - Khả năng sinh lời",
    "liquidity": "L - Thanh khoản"
}}
```

---

## QUY TẮC

### Ngôn ngữ
- **>20%**: tăng/giảm mạnh
- **10-20%**: tăng/giảm đáng kể
- **5-10%**: tăng/giảm
- **2-5%**: tăng/giảm nhẹ
- **0-2%**: ổn định

### Format
- VND: Dấu phẩy
- Ratio: 2 số thập phân
- %: Từ cột Δ có sẵn

### Cấu trúc
- Phân tích THEO TỪNG MỤC/SECTION
- Mỗi section → Header riêng
- Nhận xét section sau khi phân tích chỉ tiêu

### Cấm
- ❌ KHÔNG tính Δ% mới
- ❌ KHÔNG giải thích nguyên nhân
- ❌ KHÔNG đánh giá tốt/xấu

---

## TEMPLATE
```markdown
# XU HƯỚNG TÀI CHÍNH
**Công ty:** {{company}} | **Giai đoạn:** {{periods}} | **Đơn vị:** VND

---

## {{TABLE_NAME}}

### {{Section_1}}

**{{Chỉ tiêu 1.1}}:**
- {{Period_old}}: {{Value}}
- {{Period_mid}}: {{Value}} ({{trend}} {{Δ%}} so với {{Period_old}})
- {{Period_new}}: {{Value}} ({{trend}} {{Δ%}} so với {{Period_mid}})

**{{Chỉ tiêu 1.2}}:**
[Tương tự]

**Nhận xét {{Section_1}}:** {{1-2 câu xu hướng chung}}.

---

### {{Section_2}}

[Tương tự Section_1]

---

### 📊 Tóm tắt {{TABLE_NAME}}

**Xu hướng:**
- {{Section_1}}: {{Xu hướng chính}}
- {{Section_2}}: {{Xu hướng chính}}

**Biến động lớn:** {{Chỉ tiêu}} ({{±Δ%}})

**Ổn định:** {{Chỉ tiêu}}

---

[Lặp cho tables khác]
```

---

CHỈ MÔ TẢ XU HƯỚNG THEO MỤC.
"""

DEEP_ANALYSIS_PROMPT = """
# NHIỆM VỤ
Phân tích chuyên sâu theo TỪNG MỤC - Giải thích NGUYÊN NHÂN, đánh giá RỦI RO, xếp hạng TÍN DỤNG.

---

## INPUT

### Orchestration Request
```json
{orchestration_request}
```

### Financial Data (TOON)
```
{financial_data_input}
```

---

## MAPPING
```python
TABLE_NAMES = {{
    "balance_sheet_horizontal": "Bảng cân đối kế toán",
    "income_statement_horizontal": "Báo cáo kết quả kinh doanh",
    "capital_adequacy": "C - Khả năng đủ vốn",
    "earnings": "E - Khả năng sinh lời",
    "liquidity": "L - Thanh khoản"
}}
```

---

## TIÊU CHUẨN (NGÀNH CHỨNG KHOÁN)

| Chỉ tiêu | ✅ Tốt | ⚠️ Chấp nhận | 🚩 Rủi ro |
|:---------|-------:|-------------:|----------:|
| Current Ratio | ≥1.5 | 1.2-1.5 | <1.2 |
| D/E Ratio | ≤1.0 | 1.0-2.0 | >2.0 |
| ROE (%) | ≥15 | 8-15 | <8 |
| ROA (%) | ≥5 | 2-5 | <2 |

### RED FLAGS
- ❌ Lợi nhuận âm 2+ kỳ
- ❌ Current Ratio < 1.0
- ❌ D/E > 3.0
- ❌ Vốn chủ giảm >20%/năm

### CREDIT RATING
- **AAA**: ≥90% Tốt, 0 Red Flag
- **AA**: ≥80% Tốt, 0 Red Flag
- **A**: ≥70% OK, 0 Red Flag
- **BBB**: ≥60% OK, ≤1 Red Flag
- **BB**: 40-60% OK, 1-2 Red Flags
- **B**: <40% OK, 2-3 Red Flags
- **CCC**: ≥60% Rủi ro, ≥3 Red Flags

---

## QUY TẮC

### ✅ Bắt buộc
- CHỈ dùng data có sẵn
- Giải thích NHÂN-QUẢ
- So sánh tiêu chuẩn: ✅/⚠️/🚩
- Phân tích THEO TỪNG MỤC/SECTION

### ❌ Cấm
- KHÔNG tính chỉ số mới
- KHÔNG quyết định cho vay

---

## TEMPLATE
```markdown
# PHÂN TÍCH CHUYÊN SÂU TÀI CHÍNH

**Công ty:** {{company}} | **Kỳ:** {{periods}} | **Đơn vị:** VND

---

## 📋 TÓM TẮT ĐIỀU HÀNH

### CREDIT RATING
> 🏆 **Rating:** {{AAA/.../CCC}}  
> 📈 **Outlook:** {{Positive/Stable/Negative}}

### QUY MÔ

| Chỉ tiêu | {{P1}} | {{P2}} | Δ% |
|:---------|-----:|-----:|---:|
| Tổng TS | {{V}} tỷ | {{V}} tỷ | {{±X%}} |
| Vốn chủ | {{V}} tỷ | {{V}} tỷ | {{±X%}} |
| Doanh thu | {{V}} tỷ | {{V}} tỷ | {{±X%}} |
| LN | {{V}} tỷ | {{V}} tỷ | {{±X%}} |

### ✅ ĐIỂM MẠNH (Top 3)
1. **{{Chỉ tiêu}}:** {{V}} - ✅ Tốt
2. {{...}}

### 🚩 ĐIỂM YẾU (Top 3)
1. **{{Chỉ tiêu}}:** {{V}} - 🚩 Rủi ro
2. {{...}}

### 🔴 RỦI RO (Top 3)
**1. {{Rủi ro}}** - 🔴 Cao: {{Mô tả}}

---

## {{TABLE_NAME}}

### {{Section_1}}

#### 📊 Hiện trạng

| Chỉ tiêu | {{P1}} | {{P2}} | Δ% | Chuẩn | Đánh giá |
|:---------|-----:|-----:|---:|------:|---------:|
| {{CT 1.1}} | {{V}} | {{V}} | {{±X%}} | {{Std}} | {{✅/⚠️/🚩}} |
| {{CT 1.2}} | {{V}} | {{V}} | {{±X%}} | {{Std}} | {{✅/⚠️/🚩}} |

#### 📉 Nguyên nhân

**Hiện tượng:** {{Chỉ số}} {{V1}} → {{V2}} ({{±X%}}).

**Nguyên nhân:**

**Thứ nhất**, {{yếu tố 1}}:
- {{Chi tiết 1}}: {{V_cũ}} → {{V_mới}} ({{±X%}})
- {{Chi tiết 2}}: {{V_cũ}} → {{V_mới}} ({{±X%}})
- Đóng góp: {{Tác động}}

**Thứ hai**, {{yếu tố 2}}:
- {{Chi tiết}}
- Đóng góp: {{Tác động}}

**Kết quả:**
- Ngắn hạn: {{Tác động}}
- Rủi ro: {{Rủi ro}}

#### 💡 Đánh giá {{Section_1}}

**✅ Tích cực:**
- {{Điểm mạnh}}

**🚩 Rủi ro:**
1. **{{R1}}:** {{Mô tả}}
   - Mức độ: {{🔴/🟡/🟢}}
   - Bằng chứng: {{Số liệu}}
   - Tác động: {{Hậu quả}}

**Mức độ rủi ro {{Section_1}}:** {{🔴/🟡/🟢}}

---

### {{Section_2}}

[Tương tự Section_1]

---

### 📊 Tổng hợp {{TABLE_NAME}}

**Điểm mạnh:**
- {{Section_1}}: {{Điểm mạnh}}
- {{Section_2}}: {{Điểm mạnh}}

**Điểm yếu:**
- {{Section_1}}: {{Điểm yếu}}
- {{Section_2}}: {{Điểm yếu}}

**Rủi ro:** {{🔴/🟡/🟢}}

---

[Lặp cho tables khác]

---

## TỔNG HỢP

### A. ĐIỂM MẠNH (Top 5)
1. **{{CT}}:** {{V}} - {{Mô tả}}

### B. ĐIỂM YẾU (Top 5)
1. **{{CT}}:** {{V}} - {{Mô tả}}

### C. RỦI RO CHI TIẾT

**🔴 1. {{Rủi ro}}**

{{2-3 đoạn}}

Bằng chứng:
- {{SL 1}}
- {{SL 2}}

Tác động:
- Ngắn hạn: {{...}}
- Dài hạn: {{...}}

---

## XU HƯỚNG

### Tài sản & Vốn
{{2-3 đoạn}}

### Kinh doanh
{{2-3 đoạn}}

### Dự báo
- Thanh khoản: {{...}}
- Sinh lời: {{...}}
- Rủi ro: {{...}}

---

## KẾT LUẬN

### TỔNG QUAN
{{3-4 đoạn}}

### CREDIT RATING: {{AAA/.../CCC}}

**Cơ sở:**
- ✅ Tốt: {{X}} ({{Y%}})
- ⚠️ CB: {{X}} ({{Y%}})
- 🚩 RR: {{X}} ({{Y%}})
- Red Flags: {{X}}/9

{{2-3 đoạn giải thích}}

### KHẢ NĂNG TRẢ NỢ

**Ngắn hạn:** {{Tốt/TB/Yếu}}
{{2-3 câu}}

**Dài hạn:** {{Tốt/TB/Yếu}}
{{2-3 câu}}

**Rủi ro vỡ nợ:** {{Thấp/TB/Cao}}
{{Chi tiết}}

---

## KHUYẾN NGHỊ

### Thông tin cần bổ sung
- Chiến lược kinh doanh
- Lịch sử tín dụng
- TSĐB

### Vấn đề cần làm rõ
1. {{Vấn đề 1}}
2. {{Vấn đề 2}}

### Biện pháp giảm thiểu

**Ngắn hạn:**
- {{...}}

**Trung hạn:**
- {{...}}

**Dài hạn:**
- {{...}}

---

## LƯU Ý

⚠️ Báo cáo KHÔNG PHẢI quyết định tín dụng.

Cần:
- Phân tích định tính (5C)
- Xem xét chính sách nội bộ
- Đánh giá TSĐB
- Xác minh độc lập

Cập nhật định kỳ.
```

---

PHÂN TÍCH THEO MỤC - CÓ NGUYÊN NHÂN - CÓ BẰNG CHỨNG.
"""
