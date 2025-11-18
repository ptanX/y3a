from typing import List, Dict

from pydantic import BaseModel, Field

from src.state.type import DefaultState


class DimensionRequest(BaseModel):
    """Schema cho từng dimension được request"""

    dimension_name: str = Field(
        description="Tên dimension từ danh sách hợp lệ: capital_adequacy, asset_quality, management_quality, earnings,"
                    " liquidity, sensitivity_to_market_risk"
    )
    sub_dimension_name: List[str] = Field(
        description="Danh sách các sub-dimension names thuộc dimension này"
    )


class OrchestrationInformation(BaseModel):
    """Schema cho orchestration output"""

    analysis_type: str = Field(
        description="Loại phân tích: overall, trending, hoặc deep_analysis"
    )
    query_scopes: List[str] = Field(
        description="Danh sách các dimensions và sub-dimensions cần phân tích"
    )
    time_period: List[str] = Field(
        description="Các khoảng thời gian cần phân tích: 2021, 2022, 2023, Q1_2024"
    )
    confidence: float = Field(description="mức độ tự tin")
    reasoning: str = Field(description="lý do đưa ra quyết định")
    suggested_clarifications: List[str] = Field(
        description="clarification nếu như confidence < 0.7"
    )


class LendingShortTermContext(BaseModel):
    previous_analysis_type: str = Field(
        description="Loại phân tích: overall, trending, hoặc deep_analysis"
    )

    previous_query_scopes: List[str] = Field(
        description="Danh sách các query scope cũ"
    )

    previous_period: List[str] = Field(
        description="Các khoảng thời gian cần phân tích: 2021, 2022, 2023, Q1_2024"
    )


class BusinessLoanValidationState(DefaultState):
    question: str
    orchestration_information: OrchestrationInformation
    financial_outputs: List[Dict]
    company: str
