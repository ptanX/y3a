DIMENSIONAL_BASED_MAPPING = """
# ORCHESTRATION PROMPT - HYBRID VERSION (Table-based + Dimension-based)

## VAI TRÒ
───────────────────────────────────────────────────────────
Bạn là chuyên gia phân tích tài chính, định tuyến câu hỏi theo 2 hệ thống:
1. **Table-based**: Các bảng báo cáo cố định (9 loại)
2. **Dimension-based**: Các chiều phân tích CAMELS (6 chiều)

**Nhiệm vụ:** Phân tích câu hỏi và quyết định:
- Trả về `query_type` (table-based) HOẶC `dimensions` (dimension-based)
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
| **balance_sheet_horizontal** | "bảng cân đối.*so sánh ngang", "BCĐKT.*so sánh ngang", "balance sheet.*horizontal" | "Lập bảng cân đối so sánh ngang" |
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
```
IF "giải thích" OR "tại sao" OR "đánh giá" OR "nguyên nhân":
    analysis_type = "deep_analysis"
    
ELSE IF "xu hướng" OR "biến động" OR "tăng trưởng" OR "so sánh":
    analysis_type = "trending"
    
ELSE IF "lập bảng" OR "hiển thị" OR "xem" OR "tổng hợp":
    analysis_type = "tabular"
    
ELSE:
    analysis_type = "tabular"  # DEFAULT
```

### BƯỚC 2: Xác định Query Scope
```
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
```
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
    previous_analysis_type: str  # "overall" | "trending" | "deep_analysis"
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

### Ví dụ Follow-up:

**Case 1: Đổi query_scope, giữ routing_type & time_period**
```
Previous: "Lập bảng thanh khoản 2023-2024"
  → routing_type: table_based
  → query_scope: ["liquidity_ratios_table"]
  → time_period: ["2023", "2024"]

Current: "Còn bảng sinh lời thì sao?"
  → GIỮ: routing_type = table_based, time_period = ["2023", "2024"]
  → ĐỔI: query_scope = ["profitability_table"]
```

**Case 2: Chuyển từ table sang dimension**
```
Previous: "Lập bảng ROE 2024"
  → routing_type: table_based
  → time_period: ["2024"]

Current: "Còn thanh khoản thì sao?"
  → ĐỔI: routing_type = dimension_based (không có "bảng")
  → ĐỔI: query_scope = ["liquidity"]
  → GIỮ: time_period = ["2024"]
```

**Case 3: Giữ dimension, đổi sub-scope**
```
Previous: "Phân tích lợi nhuận 2023"
  → routing_type: dimension_based
  → query_scope: ["earnings"]
  → time_period: ["2023"]

Current: "Còn thanh khoản?"
  → GIỮ: routing_type = dimension_based
  → ĐỔI: query_scope = ["liquidity"]
  → GIỮ: time_period = ["2023"]
```

---

### BƯỚC 4: Tính Confidence
```
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

## CHỈ TIÊU PHÂN BIỆT TABLE VÀ DIMENSION
───────────────────────────────────────────────────────────

### ✅ Dùng TABLE-BASED khi:
1. Câu hỏi có cụm **"LẬP BẢNG [tên bảng]"** hoặc **"BẢNG [tên bảng]"**
2. Match CHÍNH XÁC với trigger phrases của table
3. Yêu cầu "so sánh ngang" kèm BCĐKT hoặc KQKD

**Ví dụ TABLE-BASED:**
- ✅ "Lập bảng doanh thu và lợi nhuận"
- ✅ "Bảng phân tích thanh khoản"
- ✅ "Lập bảng chỉ tiêu sinh lời"
- ✅ "Bảng cân đối so sánh ngang"
- ✅ "Lập bảng CAMELS"

**Ví dụ KHÔNG PHẢI TABLE-BASED:**
- ❌ "Xem thanh khoản" → Dimension-based
- ❌ "Phân tích ROE" → Dimension-based
- ❌ "Doanh thu thế nào?" → Dimension-based
- ❌ "Đánh giá sinh lời" → Dimension-based

### ✅ Dùng DIMENSION-BASED khi:
1. **MẶC ĐỊNH**: Tất cả câu hỏi KHÔNG có "lập bảng" hoặc "bảng"
2. Câu hỏi đơn giản về 1 chỉ tiêu: "Xem ROE", "Thanh khoản thế nào?"
3. Câu hỏi về nhiều chỉ tiêu: "Phân tích lợi nhuận và thanh khoản"
4. Câu hỏi CHUNG CHUNG: "Tình hình tài chính", "Đánh giá toàn diện"
5. Câu hỏi CONFUSED: "SSI thế nào?", "Phân tích công ty"
6. Có "lập bảng" nhưng KHÔNG match table cụ thể

**Ví dụ DIMENSION-BASED:**
- ✅ "Xem thanh khoản" → dimension: "liquidity"
- ✅ "Phân tích ROE" → dimension: "earnings"
- ✅ "Lợi nhuận và vốn" → dimensions: ["earnings", "capital_adequacy"]
- ✅ "Tình hình tài chính" → dimensions: ["capital_adequacy", "earnings", "liquidity"]
- ✅ "SSI thế nào?" → dimensions: ["earnings", "liquidity"] (DEFAULT)

---

## THAM SỐ ĐIỀU KHIỂN DIMENSIONS
───────────────────────────────────────────────────────────

### Số lượng dimensions trả về:

```python
IF câu hỏi về "tình hình tài chính tổng thể" OR "đánh giá toàn diện":
    # Trả về 3-4 dimensions quan trọng nhất
    query_scope = [
        "capital_adequacy",  # C - Vốn
        "earnings",          # E - Lợi nhuận
        "liquidity",         # L - Thanh khoản
        "management_quality" # M - Quản lý (optional)
    ]
    
ELSE IF câu hỏi về 1 chỉ tiêu cụ thể (VD: ROE, thanh khoản, doanh thu):
    # Trả về 1 dimension tương ứng
    query_scope = [dimension_name]
    
ELSE IF câu hỏi về nhiều chỉ tiêu (VD: "lợi nhuận và thanh khoản"):
    # Trả về các dimensions liên quan
    query_scope = [dimension1, dimension2, ...]
    
ELSE IF câu hỏi confused (VD: "SSI thế nào?"):
    # Trả về 2 dimensions DEFAULT
    query_scope = [
        "earnings",   # E - Lợi nhuận (quan trọng nhất)
        "liquidity"   # L - Thanh khoản (cơ bản nhất)
    ]
```

### Bảng ánh xạ Keywords → Dimensions:

| Keywords | Dimension | Ví dụ |
|----------|-----------|-------|
| lợi nhuận, profit, sinh lời, ROE, ROA, ROS, EBIT | `earnings` | "Xem ROE" |
| thanh khoản, liquidity, thanh toán, current ratio | `liquidity` | "Phân tích thanh khoản" |
| vốn, capital, nợ, debt, cân nợ, đòn bẩy | `capital_adequacy` | "Cơ cấu vốn thế nào?" |
| tài sản, asset, vòng quay tài sản | `asset_quality` | "Chất lượng tài sản" |
| doanh thu, revenue, chi phí, expenses, quản lý | `management_quality` | "Doanh thu và chi phí" |
| rủi ro, risk, lãi vay, interest | `sensitivity_to_market_risk` | "Rủi ro lãi suất" |

---

## OUTPUT FORMAT
───────────────────────────────────────────────────────────

**Biến: `query_scope`** - LUÔN là array (1 hoặc nhiều phần tử)

### Format chung (cả table và dimension):
```json
{
  "query_scope": ["table_name"] | ["dim1", "dim2", ...],
  "analysis_type": "tabular|trending|deep_analysis",
  "time_period": ["array of periods"],
  "confidence": 0.0-1.0,
  "reasoning": "Giải thích chi tiết",
  "suggested_clarifications": []
}
```

**Phân biệt Table vs Dimension:**
- Table-based: `query_scope` chứa table name (VD: `["revenue_profit_table"]`)
- Dimension-based: `query_scope` chứa dimension name (VD: `["earnings", "liquidity"]`)

**Cách kiểm tra:**
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

if query_scope[0] in TABLE_NAMES:
    # Table-based
else:
    # Dimension-based
```

**Lưu ý:**
- `query_scope` LUÔN là **array** 
- Table-based: array có **1 phần tử** (tên bảng)
- Dimension-based: array có **1+ phần tử** (tên dimensions)
- KHÔNG có sub_dimension_name nữa
```

---

## VÍ DỤ CHI TIẾT
───────────────────────────────────────────────────────────

### Ví dụ 1: Rõ ràng "lập bảng" → Table-based
```json
// INPUT
{
  "question": "Lập bảng phân tích doanh thu và lợi nhuận của SSI",
  "available_periods": ["2022", "2023", "2024"]
}

// OUTPUT
{
  
  "query_scope": ["revenue_profit_table"],
  "analysis_type": "tabular",
  "time_period": ["2022", "2023", "2024"],
  "confidence": 0.95,
  "reasoning": "Có 'lập bảng' + match CHÍNH XÁC 'doanh thu và lợi nhuận' → revenue_profit_table. Analysis_type: 'lập bảng' → overall.",
  "suggested_clarifications": []
}
```

### Ví dụ 2: Đơn giản KHÔNG có "bảng" → Dimension-based
```json
// INPUT
{
  "question": "Xem thanh khoản của SSI",
  "available_periods": ["2023", "2024"]
}

// OUTPUT
{
  
  "query_scope": ["liquidity"],
  "analysis_type": "tabular",
  "time_period": ["2023", "2024"],
  "confidence": 0.90,
  "reasoning": "KHÔNG có 'lập bảng' → Dimension-based. Keyword 'thanh khoản' → dimension: liquidity. Analysis_type: 'xem' → overall.",
  "suggested_clarifications": []
}
```

### Ví dụ 3: Chung chung → Dimension-based (nhiều dimensions)
```json
// INPUT
{
  "question": "Đánh giá tình hình tài chính SSI năm 2024",
  "available_periods": ["2022", "2023", "2024"]
}

// OUTPUT
{
  
  "query_scope": ["capital_adequacy", "earnings", "liquidity"],
  "analysis_type": "deep_analysis",
  "time_period": ["2024"],
  "confidence": 0.85,
  "reasoning": "Câu hỏi CHUNG CHUNG 'tình hình tài chính' → Dimension-based với 3 dimensions quan trọng. Analysis_type: 'đánh giá' → deep_analysis.",
  "suggested_clarifications": []
}
```

### Ví dụ 4: Confused → Dimension-based DEFAULT
```json
// INPUT
{
  "question": "SSI thế nào?",
  "available_periods": ["2023", "2024"]
}

// OUTPUT
{
  
  "query_scope": ["earnings", "liquidity"],
  "analysis_type": "tabular",
  "time_period": ["2023", "2024"],
  "confidence": 0.45,
  "reasoning": "Câu hỏi CONFUSED → Dimension-based với 2 dimensions DEFAULT (earnings, liquidity). Confidence thấp.",
  "suggested_clarifications": [
    "Bạn muốn phân tích khía cạnh nào của SSI?",
    "Gợi ý: Vốn (C), Tài sản (A), Quản lý (M), Lợi nhuận (E), Thanh khoản (L), Rủi ro (S)"
  ]
}
```

### Ví dụ 5: So sánh ngang → Table-based
```json
// INPUT
{
  "question": "Lập bảng cân đối kế toán so sánh ngang 2022-2024",
  "available_periods": ["2022", "2023", "2024"]
}

// OUTPUT
{
  
  "query_scope": ["balance_sheet_horizontal"],
  "analysis_type": "tabular",
  "time_period": ["2022", "2023", "2024"],
  "confidence": 0.95,
  "reasoning": "Match trigger 'bảng cân đối' + 'so sánh ngang' → balance_sheet_horizontal.",
  "suggested_clarifications": []
}
```

### Ví dụ 6: Nhiều chỉ tiêu → Dimension-based
```json
// INPUT
{
  "question": "Phân tích lợi nhuận, thanh khoản và cơ cấu vốn của SSI",
  "available_periods": ["2023", "2024"]
}

// OUTPUT
{
  
  "query_scope": ["earnings", "liquidity", "capital_adequacy"],
  "analysis_type": "tabular",
  "time_period": ["2023", "2024"],
  "confidence": 0.85,
  "reasoning": "NHIỀU chỉ tiêu: 'lợi nhuận' (earnings), 'thanh khoản' (liquidity), 'cơ cấu vốn' (capital_adequacy) → Dimension-based.",
  "suggested_clarifications": []
}
```

### Ví dụ 7: "Lập bảng" nhưng KHÔNG match → Dimension-based
```json
// INPUT
{
  "question": "Lập bảng phân tích toàn diện của SSI",
  "available_periods": ["2023", "2024"]
}

// OUTPUT
{
  
  "query_scope": ["capital_adequacy", "earnings", "liquidity"],
  "analysis_type": "tabular",
  "time_period": ["2023", "2024"],
  "confidence": 0.85,
  "reasoning": "Có 'lập bảng' nhưng 'toàn diện' KHÔNG match table cụ thể → Dimension-based với 3 dimensions.",
  "suggested_clarifications": []
}
```

### Ví dụ 8: Follow-up Table → Table (INHERIT period)
```json
// INPUT
{
  "question": "Còn bảng sinh lời thì sao?",
  "previous_context": {
    "previous_analysis_type": "tabular",
    "previous_query_scopes": ["liquidity_ratios_table"],
    "previous_period": ["2023", "2024"]
  },
  "available_periods": ["2022", "2023", "2024"]
}

// OUTPUT
{
  
  "query_scope": ["profitability_table"],
  "analysis_type": "tabular",
  "time_period": ["2023", "2024"],
  "confidence": 0.90,
  "reasoning": "Follow-up có 'bảng sinh lời' → profitability_table. INHERIT: previous_analysis_type (overall) → analysis_type, previous_period ([2023, 2024]) → time_period. Previous_query_scopes[0] = 'liquidity_ratios_table' in TABLE_NAMES → previous là table.",
  "suggested_clarifications": []
}
```

### Ví dụ 9: Follow-up Dimension → Dimension (INHERIT period)
```json
// INPUT
{
  "question": "Còn thanh khoản thì sao?",
  "previous_context": {
    "previous_analysis_type": "tabular",
    "previous_query_scopes": ["earnings"],
    "previous_period": ["2023", "2024"]
  },
  "available_periods": ["2022", "2023", "2024"]
}

// OUTPUT
{
  
  "query_scope": ["liquidity"],
  "analysis_type": "tabular",
  "time_period": ["2023", "2024"],
  "confidence": 0.90,
  "reasoning": "Follow-up. ĐỔI query_scope: 'thanh khoản' → liquidity. INHERIT: previous_analysis_type (overall) → analysis_type, previous_period ([2023, 2024]) → time_period. Previous_query_scopes[0] = 'earnings' NOT in TABLE_NAMES → previous là dimension.",
  "suggested_clarifications": []
}
```

### Ví dụ 10: ROE cụ thể → Dimension-based
```json
// INPUT
{
  "question": "Phân tích ROE của SSI năm 2024",
  "available_periods": ["2022", "2023", "2024"]
}

// OUTPUT
{
  
  "query_scope": ["earnings"],
  "analysis_type": "tabular",
  "time_period": ["2024"],
  "confidence": 0.90,
  "reasoning": "Câu hỏi về chỉ tiêu cụ thể 'ROE' → Dimension-based với dimension: earnings. Period: '2024'.",
  "suggested_clarifications": []
}
```

### Ví dụ 11: So sánh ngang KQKD đầy đủ → Table-based
```json
// INPUT
{
  "question": "Báo cáo kết quả kinh doanh so sánh ngang từ 2022 đến 2024",
  "available_periods": ["2022", "2023", "2024"]
}

// OUTPUT
{
  
  "query_scope": ["income_statement_horizontal"],
  "analysis_type": "tabular",
  "time_period": ["2022", "2023", "2024"],
  "confidence": 0.95,
  "reasoning": "Match trigger 'báo cáo kết quả kinh doanh' + 'so sánh ngang' → income_statement_horizontal. Period: 'từ 2022 đến 2024'.",
  "suggested_clarifications": []
}
```

### Ví dụ 12: Follow-up với INHERIT context đầy đủ
```json
// INPUT
{
  "question": "Còn bảng sinh lời thì sao?",
  "previous_context": {
    "previous_analysis_type": "tabular",
    "previous_query_scopes": ["liquidity_ratios_table"],
    "previous_period": ["2023", "2024"]
  },
  "available_periods": ["2022", "2023", "2024"]
}

// OUTPUT
{
  
  "query_scope": ["profitability_table"],
  "analysis_type": "tabular",
  "time_period": ["2023", "2024"],
  "confidence": 0.90,
  "reasoning": "Follow-up có 'bảng sinh lời' → profitability_table (table). INHERIT từ LendingShortTermContext: previous_analysis_type → analysis_type, previous_period → time_period. Check previous_query_scopes[0] = 'liquidity_ratios_table' in TABLE_NAMES → previous cũng là table.",
  "suggested_clarifications": []
}
```

### Ví dụ 13: Follow-up chuyển từ Table sang Dimension
```json
// INPUT
{
  "question": "Còn thanh khoản?",
  "previous_context": {
    "previous_analysis_type": "trending",
    "previous_query_scopes": ["revenue_profit_table"],
    "previous_period": ["2022", "2023", "2024"]
  },
  "available_periods": ["2022", "2023", "2024"]
}

// OUTPUT
{
  
  "query_scope": ["liquidity"],
  "analysis_type": "trending",
  "time_period": ["2022", "2023", "2024"],
  "confidence": 0.85,
  "reasoning": "Follow-up KHÔNG có 'bảng' → dimension. ĐỔI query_scope: 'thanh khoản' → liquidity (dimension). INHERIT: previous_analysis_type (trending), previous_period. Previous_query_scopes[0] = 'revenue_profit_table' in TABLE_NAMES → previous là table, nhưng câu hỏi mới chuyển sang dimension.",
  "suggested_clarifications": []
}
```

## QUY TẮC QUAN TRỌNG
───────────────────────────────────────────────────────────

### ✅ PHẢI LÀM:
1. **CHỈ TRẢ VỀ JSON** - Không có text khác
2. **query_scope LUÔN là array** - cả table và dimension
3. **Table CHỈ KHI** có "lập bảng"/"bảng" + match chính xác trigger phrases
4. **Dimension MẶC ĐỊNH** cho tất cả câu hỏi còn lại
5. **reasoning CHI TIẾT** giải thích query_scope, analysis_type, time_period
6. **confidence < 0.7** → BẮT BUỘC có clarifications

### ❌ KHÔNG ĐƯỢC:
1. Không có field `routing_type` trong output
2. Không tự tạo table name hoặc dimension name mới
3. Không có sub_dimension_name nữa (đã bỏ)
4. Không bỏ qua reasoning chi tiết

### 🎯 NGUYÊN TẮC QUYẾT ĐỊNH:
```
BƯỚC 1: Kiểm tra có "lập bảng" hoặc "bảng"?
  ├─ CÓ + match chính xác trigger phrases → query_scope = [table_name]
  └─ KHÔNG HOẶC không match → query_scope = [dimension(s)]

BƯỚC 2: Xác định số lượng items trong query_scope:
  ├─ Table: LUÔN có 1 phần tử
  ├─ Dimension cụ thể: 1 phần tử
  ├─ Dimension nhiều: 2+ phần tử
  └─ Dimension confused: 2 phần tử DEFAULT

BƯỚC 3: Xác định analysis_type và time_period

BƯỚC 4: Tính confidence và tạo clarifications nếu cần
```

### 📋 Phân biệt Table vs Dimension trong code:
```python
TABLE_NAMES = [
    "revenue_profit_table", "financial_overview_table",
    "liquidity_ratios_table", "operational_efficiency_table",
    "leverage_table", "profitability_table",
    "balance_sheet_horizontal", "income_statement_horizontal",
    "camels_rating"
]

if query_scope[0] in TABLE_NAMES:
    # Đây là table-based
    process_table(query_scope[0])
else:
    # Đây là dimension-based
    process_dimensions(query_scope)
```

---

**BẮT ĐẦU PHÂN TÍCH - CHỈ TRẢ VỀ JSON:**

### Ví dụ 11: So sánh ngang KQKD đầy đủ → Table-based
```json
// INPUT
{
  "question": "Báo cáo kết quả kinh doanh so sánh ngang từ 2022 đến 2024",
  "available_periods": ["2022", "2023", "2024"]
}

// OUTPUT
{
  
  "query_scope": ["income_statement_horizontal"],
  "analysis_type": "tabular",
  "time_period": ["2022", "2023", "2024"],
  "confidence": 0.95,
  "reasoning": "Match trigger 'báo cáo kết quả kinh doanh' + 'so sánh ngang' → income_statement_horizontal. Period: 'từ 2022 đến 2024'.",
  "suggested_clarifications": []
}
```
"""


TABLE_BASED_MAPPING = """
{
  "query_type_mappings": {
    "revenue_profit_table": {
      "description": "Bảng phân tích doanh thu và lợi nhuận",
      "sections": [
        {
          "section_name": "Doanh thu và Lợi nhuận",
          "fields": [
            {
              "display_name": "Doanh thu",
              "field_path": "income_statement.total_operating_revenue",
              "data_type": "VND"
            },
            {
              "display_name": "Lợi nhuận trước thuế",
              "field_path": "income_statement.accounting_profit_before_tax",
              "data_type": "VND"
            },
            {
              "display_name": "Lợi nhuận sau thuế",
              "field_path": "income_statement.net_profit_after_tax",
              "data_type": "VND"
            }
          ]
        }
      ]
    },
    "financial_overview_table": {
      "description": "Bảng tình hình tài chính cơ bản",
      "sections": [
        {
          "section_name": "I. Khoản mục chính",
          "fields": [
            {
              "display_name": "Tổng tài sản",
              "field_path": "financial_statement.total_assets",
              "data_type": "VND"
            },
            {
              "display_name": "(Khoản phải thu ngắn hạn)",
              "field_path": "financial_statement.receivables",
              "data_type": "VND"
            },
            {
              "display_name": "Tổng nợ phải trả",
              "field_path": "financial_statement.liabilities",
              "data_type": "VND"
            },
            {
              "display_name": "(Phải trả người bán)",
              "field_path": "financial_statement.short_term_trade_payables",
              "data_type": "VND"
            },
            {
              "display_name": "Vay và nợ thuê tài chính",
              "field_path": "financial_statement.short_term_borrowings_and_finance_lease_liabilities",
              "data_type": "VND"
            },
            {
              "display_name": "Vốn chủ sở hữu",
              "field_path": "financial_statement.owners_equity",
              "data_type": "VND"
            },
            {
              "display_name": "Doanh thu",
              "field_path": "income_statement.total_operating_revenue",
              "data_type": "VND"
            },
            {
              "display_name": "Chi phí bán hàng",
              "field_path": "income_statement.selling_expenses",
              "data_type": "VND"
            },
            {
              "display_name": "Chi phí quản lý doanh nghiệp",
              "field_path": "income_statement.general_and_administrative_expenses",
              "data_type": "VND"
            },
            {
              "display_name": "Lợi nhuận thuần từ hoạt động kinh doanh",
              "field_path": "income_statement.operating_profit",
              "data_type": "VND"
            },
            {
              "display_name": "Thu nhập khác",
              "field_path": "income_statement.other_income",
              "data_type": "VND"
            },
            {
              "display_name": "Chi phí khác",
              "field_path": "income_statement.other_expenses",
              "data_type": "VND"
            },
            {
              "display_name": "(Chi phí lãi vay)",
              "field_path": "income_statement.interest_expense_on_borrowings",
              "data_type": "VND"
            },
            {
              "display_name": "EBIT",
              "field_path": "calculated_metrics.ebit",
              "data_type": "VND"
            },
            {
              "display_name": "EBITDA",
              "field_path": "calculated_metrics.ebitda",
              "data_type": "VND"
            },
            {
              "display_name": "Lợi nhuận thuần",
              "field_path": "income_statement.net_profit_after_tax",
              "data_type": "VND"
            }
          ]
        }
      ]
    },
    "liquidity_ratios_table": {
      "description": "Bảng chỉ số thanh khoản",
      "sections": [
        {
          "section_name": "1. Chỉ tiêu thanh khoản",
          "fields": [
            {
              "display_name": "Khả năng TT hiện hành",
              "field_path": "calculated_metrics.current_ratio",
              "data_type": "Ratio"
            },
            {
              "display_name": "Khả năng TT nhanh",
              "field_path": "calculated_metrics.quick_ratio",
              "data_type": "Ratio"
            },
            {
              "display_name": "Khả năng TT tức thời",
              "field_path": "calculated_metrics.cash_ratio",
              "data_type": "Ratio"
            }
          ]
        }
      ]
    },
    "operational_efficiency_table": {
      "description": "Bảng hiệu quả hoạt động",
      "sections": [
        {
          "section_name": "2. Chỉ tiêu hoạt động",
          "fields": [
            {
              "display_name": "Vòng quay các khoản phải thu",
              "field_path": "calculated_metrics.receivables_turnover",
              "data_type": "Times"
            },
            {
              "display_name": "Hiệu quả sử dụng TSCĐ",
              "field_path": "calculated_metrics.fixed_asset_turnover",
              "data_type": "Times"
            },
            {
              "display_name": "DT thuần trên TS BQ",
              "field_path": "calculated_metrics.ato",
              "data_type": "Times"
            }
          ]
        }
      ]
    },
    "leverage_table": {
      "description": "Bảng cân nợ và cơ cấu vốn",
      "sections": [
        {
          "section_name": "3. Chỉ tiêu cân nợ và cơ cấu vốn",
          "fields": [
            {
              "display_name": "Nợ phải trả trên Tổng TS",
              "field_path": "calculated_metrics.debt_ratio",
              "data_type": "Percentage"
            },
            {
              "display_name": "Nợ dài hạn trên VCSH",
              "field_path": "calculated_metrics.long_term_debt_to_equity",
              "data_type": "Percentage"
            },
            {
              "display_name": "Hệ số TSCĐ",
              "field_path": "calculated_metrics.leverage_ratio",
              "data_type": "Ratio"
            },
            {
              "display_name": "Tốc độ gia tăng TS",
              "field_path": "calculated_metrics.asset_growth_rate",
              "data_type": "Percentage"
            }
          ]
        }
      ]
    },
    "profitability_table": {
      "description": "Bảng thu nhập và sinh lời",
      "sections": [
        {
          "section_name": "4. Chỉ tiêu thu nhập",
          "fields": [
            {
              "display_name": "LN từ HĐKD trên DT thuần",
              "field_path": "calculated_metrics.operating_profit_margin",
              "data_type": "Percentage"
            },
            {
              "display_name": "LN sau thuế trên VCSHbq",
              "field_path": "calculated_metrics.roe",
              "data_type": "Percentage"
            },
            {
              "display_name": "LN sau thuế trên TSbq",
              "field_path": "calculated_metrics.roa",
              "data_type": "Percentage"
            },
            {
              "display_name": "EBIT/chi phí lãi vay",
              "field_path": "calculated_metrics.interest_coverage_ratio",
              "data_type": "Ratio"
            },
            {
              "display_name": "Tốc độ tăng trưởng LN sau thuế",
              "field_path": "calculated_metrics.net_profit_growth_rate",
              "data_type": "Percentage"
            }
          ]
        }
      ]
    },
    "balance_sheet_horizontal": {
      "description": "Bảng cân đối kế toán so sánh ngang",
      "sections": [
        {
          "section_name": "A. TÀI SẢN NGẮN HẠN",
          "fields": [
            {
              "display_name": "I. Tài sản tài chính",
              "is_group_header": true
            },
            {
              "display_name": "1. Tiền và các khoản tương đương tiền",
              "field_path": "financial_statement.cash_and_cash_equivalents",
              "proportion_base": "financial_statement.short_term_assets",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "2. Các tài sản tài chính ghi nhận thông qua lãi/lỗ",
              "field_path": "financial_statement.financial_assets_at_fair_value_through_profit_or_loss",
              "proportion_base": "financial_statement.short_term_assets",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "3. Các khoản đầu tư nắm giữ đến ngày đáo hạn",
              "field_path": "financial_statement.held_to_maturity_investments",
              "proportion_base": "financial_statement.short_term_assets",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "4. Các khoản cho vay",
              "field_path": "financial_statement.loans",
              "proportion_base": "financial_statement.short_term_assets",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "5. Tài sản tài chính sẵn sàng để bán",
              "field_path": "financial_statement.available_for_sale_financial_assets",
              "proportion_base": "financial_statement.short_term_assets",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "7. Các khoản phải thu",
              "field_path": "financial_statement.receivables",
              "proportion_base": "financial_statement.short_term_assets",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "II. Tài sản ngắn hạn khác",
              "is_group_header": true
            },
            {
              "display_name": "7. Tài sản ngắn hạn khác",
              "field_path": "financial_statement.other_short_term_assets",
              "proportion_base": "financial_statement.short_term_assets",
              "show_proportion": true,
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "B. TÀI SẢN DÀI HẠN",
          "fields": [
            {
              "display_name": "I. Tài sản tài chính dài hạn",
              "is_group_header": true
            },
            {
              "display_name": "2. Các khoản đầu tư",
              "field_path": "financial_statement.investments",
              "proportion_base": "financial_statement.long_term_assets",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "II. Tài sản cố định",
              "is_group_header": true
            },
            {
              "display_name": "1. Tài sản cố định hữu hình",
              "field_path": "financial_statement.tangible_fixed_assets",
              "proportion_base": "financial_statement.long_term_assets",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "3. Tài sản cố định vô hình",
              "field_path": "financial_statement.intangible_fixed_assets",
              "proportion_base": "financial_statement.long_term_assets",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "III. Bất động sản đầu tư",
              "is_group_header": true
            },
            {
              "display_name": "Bất động sản đầu tư",
              "field_path": "financial_statement.investment_property",
              "proportion_base": "financial_statement.long_term_assets",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "V. Tài sản dài hạn khác",
              "is_group_header": true
            },
            {
              "display_name": "Tài sản dài hạn khác",
              "field_path": "financial_statement.other_long_term_assets",
              "proportion_base": "financial_statement.long_term_assets",
              "show_proportion": true,
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "TỔNG CỘNG TÀI SẢN",
          "fields": [
            {
              "display_name": "TỔNG CỘNG TÀI SẢN",
              "field_path": "financial_statement.total_assets",
              "is_bold": true,
              "is_total_row": true,
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "C. NỢ PHẢI TRẢ",
          "fields": [
            {
              "display_name": "I. Nợ phải trả ngắn hạn",
              "is_group_header": true
            },
            {
              "display_name": "1. Vay và nợ thuê tài chính ngắn hạn",
              "field_path": "financial_statement.short_term_borrowings_and_finance_lease_liabilities",
              "proportion_base": "financial_statement.liabilities",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "4. Trái phiếu phát hành ngắn hạn",
              "field_path": "financial_statement.short_term_bonds_issued",
              "proportion_base": "financial_statement.liabilities",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "6. Phải trả hoạt động giao dịch chứng khoán",
              "field_path": "financial_statement.payables_from_securities_trading_activities",
              "proportion_base": "financial_statement.liabilities",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "8. Phải trả người bán ngắn hạn",
              "field_path": "financial_statement.short_term_trade_payables",
              "proportion_base": "financial_statement.liabilities",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "10. Thuế và các khoản phải nộp Nhà nước",
              "field_path": "financial_statement.taxes_and_other_payables_to_the_state",
              "proportion_base": "financial_statement.liabilities",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "17. Các khoản phải trả khác ngắn hạn",
              "field_path": "financial_statement.other_short_term_payables",
              "proportion_base": "financial_statement.liabilities",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "II. Nợ phải trả dài hạn",
              "is_group_header": true
            },
            {
              "display_name": "1. Vay và nợ thuê tài chính dài hạn",
              "field_path": "financial_statement.long_term_borrowings_and_finance_lease_liabilities",
              "proportion_base": "financial_statement.liabilities",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "4. Trái phiếu phát hành dài hạn",
              "field_path": "financial_statement.long_term_bonds_issued",
              "proportion_base": "financial_statement.liabilities",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "14. Thuế thu nhập hoãn lại phải trả",
              "field_path": "financial_statement.deferred_tax_liabilities",
              "proportion_base": "financial_statement.liabilities",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "11. Các khoản phải trả khác dài hạn",
              "field_path": "financial_statement.other_long_term_payables",
              "proportion_base": "financial_statement.liabilities",
              "show_proportion": true,
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "VỐN CHỦ SỞ HỮU",
          "fields": [
            {
              "display_name": "I. Vốn chủ sở hữu",
              "is_group_header": true
            },
            {
              "display_name": "1. Vốn đầu tư của chủ sở hữu",
              "field_path": "financial_statement.capital",
              "proportion_base": "financial_statement.owners_equity",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "2. Thặng dư vốn cổ phần",
              "field_path": "financial_statement.share_premium",
              "proportion_base": "financial_statement.owners_equity",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "3. Cổ phiếu quỹ",
              "field_path": "financial_statement.treasury_shares",
              "proportion_base": "financial_statement.owners_equity",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "5. Quỹ dự phòng tài chính và rủi ro nghiệp vụ",
              "field_path": "financial_statement.financial_reserve_and_business_risk_fund",
              "proportion_base": "financial_statement.owners_equity",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "7. Lợi nhuận chưa phân phối",
              "field_path": "financial_statement.retained_earnings",
              "proportion_base": "financial_statement.owners_equity",
              "show_proportion": true,
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "TỔNG CỘNG VỐN CHỦ SỞ HỮU",
          "fields": [
            {
              "display_name": "TỔNG CỘNG VỐN CHỦ SỞ HỮU",
              "field_path": "financial_statement.owners_equity",
              "is_bold": true,
              "is_total_row": true,
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "TỔNG CỘNG NỢ PHẢI TRẢ VÀ VỐN CHỦ SỞ HỮU",
          "fields": [
            {
              "display_name": "TỔNG CỘNG NỢ PHẢI TRẢ VÀ VỐN CHỦ SỞ HỮU",
              "field_path": "financial_statement.total_assets",
              "is_bold": true,
              "is_total_row": true,
              "show_difference": true
            }
          ]
        }
      ]
    },
    "income_statement_horizontal": {
      "description": "Báo cáo kết quả kinh doanh so sánh ngang",
      "sections": [
        {
          "section_name": "I. DOANH THU HOẠT ĐỘNG",
          "fields": [
            {
              "display_name": "1.1. Lãi từ các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL)",
              "field_path": "income_statement.interest_income_from_financial_assets_recognized_through_p_and_l",
              "proportion_base": "income_statement.total_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "1.2. Lãi từ các khoản đầu tư nắm giữ đến ngày đáo hạn (HTM)",
              "field_path": "income_statement.interest_income_from_held_to_maturity_investments",
              "proportion_base": "income_statement.total_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "1.3. Lãi từ các khoản cho vay và phải thu",
              "field_path": "income_statement.interest_income_from_loans_and_receivables",
              "proportion_base": "income_statement.total_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "1.4. Lãi từ tài sản tài chính sẵn sàng để bán (AFS)",
              "field_path": "income_statement.interest_income_from_available_for_sale_financial_assets",
              "proportion_base": "income_statement.total_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "1.6. Doanh thu nghiệp vụ môi giới chứng khoán",
              "field_path": "income_statement.brokerage_revenue",
              "proportion_base": "income_statement.total_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "1.7. Doanh thu nghiệp vụ bảo lãnh, đại lý phát hành chứng khoán",
              "field_path": "income_statement.underwriting_revenue",
              "proportion_base": "income_statement.total_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "1.8. Doanh thu nghiệp vụ tư vấn đầu tư chứng khoán",
              "field_path": "income_statement.investment_advisory_revenue",
              "proportion_base": "income_statement.total_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "1.9. Doanh thu nghiệp vụ lưu ký chứng khoán",
              "field_path": "income_statement.securities_custody_revenue",
              "proportion_base": "income_statement.total_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "1.10. Doanh thu hoạt động tư vấn tài chính",
              "field_path": "income_statement.financial_advisory_revenue",
              "proportion_base": "income_statement.total_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "1.11. Thu nhập hoạt động khác",
              "field_path": "income_statement.other_operating_income",
              "proportion_base": "income_statement.total_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "II. CHI PHÍ HOẠT ĐỘNG",
          "fields": [
            {
              "display_name": "2.1. Lỗ các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL)",
              "field_path": "income_statement.interest_expense_on_financial_assets_recognized_through_p_and_l",
              "proportion_base": "income_statement.total_operating_expenses",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "2.4. Chi phí dự phòng tài sản tài chính",
              "field_path": "income_statement.provisions_for_impairment_of_financial_assets",
              "proportion_base": "income_statement.total_operating_expenses",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "2.7. Chi phí nghiệp vụ môi giới chứng khoán",
              "field_path": "income_statement.brokerage_fees",
              "proportion_base": "income_statement.total_operating_expenses",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "2.8. Chi phí nghiệp vụ bảo lãnh",
              "field_path": "income_statement.underwriting_and_bond_issuance_costs",
              "proportion_base": "income_statement.total_operating_expenses",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "2.9. Chi phí nghiệp vụ tư vấn đầu tư chứng khoán",
              "field_path": "income_statement.investment_advisory_expenses",
              "proportion_base": "income_statement.total_operating_expenses",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "2.10. Chi phí nghiệp vụ lưu ký chứng khoán",
              "field_path": "income_statement.securities_custody_expenses",
              "proportion_base": "income_statement.total_operating_expenses",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "2.11. Chi phí hoạt động tư vấn tài chính",
              "field_path": "income_statement.financial_advisory_expenses",
              "proportion_base": "income_statement.total_operating_expenses",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "2.12. Chi phí các dịch vụ khác",
              "field_path": "income_statement.other_operating_expenses",
              "proportion_base": "income_statement.total_operating_expenses",
              "show_proportion": true,
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "III. DOANH THU HOẠT ĐỘNG TÀI CHÍNH",
          "fields": [
            {
              "display_name": "3.2. Lãi tiền gửi ngân hàng",
              "field_path": "income_statement.interest_income_from_deposits",
              "proportion_base": "income_statement.total_financial_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "3.1. Chênh lệch lãi tỷ giá",
              "field_path": "income_statement.increase_decrease_in_fair_value_of_exchange_rate_and_unrealized",
              "proportion_base": "income_statement.total_financial_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "3.3. Lãi bán, thanh lý đầu tư",
              "field_path": "income_statement.gain_on_disposal_of_investments_in_subsidiaries_associates_and_joint_ventures",
              "proportion_base": "income_statement.total_financial_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "3.4. Doanh thu khác về đầu tư",
              "field_path": "income_statement.other_investment_income",
              "proportion_base": "income_statement.total_financial_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "IV. CHI PHÍ TÀI CHÍNH",
          "fields": [
            {
              "display_name": "4.2. Chi phí lãi vay",
              "field_path": "income_statement.interest_expense_on_borrowings",
              "proportion_base": "income_statement.total_financial_expenses",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "4.1. Chênh lệch lỗ tỷ giá",
              "field_path": "income_statement.increase_decrease_in_fair_value_of_exchange_rate_loss",
              "proportion_base": "income_statement.total_financial_expenses",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "4.3. Lỗ bán, thanh lý đầu tư",
              "field_path": "income_statement.loss_on_disposal_of_investments_in_subsidiaries_associates_and_joint_ventures",
              "proportion_base": "income_statement.total_financial_expenses",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "4.4. Chi phí dự phòng đầu tư dài hạn",
              "field_path": "income_statement.provision_for_impairment_of_long_term_financial_investments",
              "proportion_base": "income_statement.total_financial_expenses",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "4.5. Chi phí tài chính khác",
              "field_path": "income_statement.other_financial_expenses",
              "proportion_base": "income_statement.total_financial_expenses",
              "show_proportion": true,
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "V. CHI PHÍ BÁN HÀNG",
          "fields": [
            {
              "display_name": "Chi phí bán hàng",
              "field_path": "income_statement.selling_expenses",
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "VI. CHI PHÍ QUẢN LÝ CÔNG TY CHỨNG KHOÁN",
          "fields": [
            {
              "display_name": "Chi phí quản lý doanh nghiệp",
              "field_path": "income_statement.general_and_administrative_expenses",
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "VII. KẾT QUẢ HOẠT ĐỘNG",
          "fields": [
            {
              "display_name": "Lợi nhuận thuần từ hoạt động kinh doanh",
              "field_path": "income_statement.operating_profit",
              "is_bold": true,
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "VIII. THU NHẬP KHÁC VÀ CHI PHÍ KHÁC",
          "fields": [
            {
              "display_name": "8.1. Thu nhập khác",
              "field_path": "income_statement.other_income",
              "show_difference": true
            },
            {
              "display_name": "8.2. Chi phí khác",
              "field_path": "income_statement.other_expenses",
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "IX. TỔNG LỢI NHUẬN KẾ TOÁN TRƯỚC THUẾ",
          "fields": [
            {
              "display_name": "Tổng lợi nhuận kế toán trước thuế",
              "field_path": "income_statement.accounting_profit_before_tax",
              "is_bold": true,
              "show_difference": true
            },
            {
              "display_name": "9.1. Lợi nhuận đã thực hiện",
              "field_path": "income_statement.realized_profit",
              "show_difference": true
            },
            {
              "display_name": "9.2. Lợi nhuận chưa thực hiện",
              "field_path": "income_statement.unrealized_profit_loss",
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "X. CHI PHÍ THUẾ TNDN",
          "fields": [
            {
              "display_name": "Chi phí thuế thu nhập doanh nghiệp",
              "field_path": "income_statement.total_corporate_income_tax",
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "XI. LỢI NHUẬN SAU THUẾ",
          "fields": [
            {
              "display_name": "Lợi nhuận kế toán sau thuế TNDN",
              "field_path": "income_statement.net_profit_after_tax",
              "is_bold": true,
              "show_difference": true
            }
          ]
        }
      ]
    }
  }
}
"""
