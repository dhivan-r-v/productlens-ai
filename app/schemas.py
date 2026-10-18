from typing import List, Optional
from pydantic import BaseModel, Field

class SalesTrends(BaseModel):
    total_revenue: float = Field(..., description="Total cumulative revenue formatted as a float")
    total_units_sold: int = Field(..., description="Total cumulative units sold")
    average_price: float = Field(..., description="Average price per unit (total revenue / total units sold)")
    overall_trend: str = Field(..., description="Short summary of overall trend direction (e.g. Upward, Downward, Stable)")
    trend_bullets: List[str] = Field(default_factory=list, description="2-3 key observations about changes over time")

class CrossModalHypothesis(BaseModel):
    hypothesis: str = Field(..., description="Hedged, testable hypothesis starting with 'Factor worth investigating:'; never a causal claim")
    supporting_data: str = Field(..., description="Specific numerical sales evidence supporting the hypothesis")
    visual_factor: str = Field(..., description="Specific visual attribute or packaging element observed in the image")
    how_to_test: str = Field(..., description="One concrete way the seller could confirm or rule out this hypothesis")

class RecommendedExperiment(BaseModel):
    action: str = Field(..., description="Clear title of the testable experiment")
    what_to_change: str = Field(..., description="Specific change to test (e.g., photo lighting, pricing tier, hero angle)")
    metric_to_measure: str = Field(..., description="Measurable metric to track during the test period")

class MultimodalAnalysisPayload(BaseModel):
    visual_observations: List[str] = Field(default_factory=list, description="Objective visual traits observed in the product photo")
    cross_modal_hypotheses: List[CrossModalHypothesis] = Field(default_factory=list, description="Hypotheses connecting visual factors with sales numbers")
    recommended_experiments: List[RecommendedExperiment] = Field(default_factory=list, description="2-3 actionable, testable experiments")

class AnalysisResponse(BaseModel):
    success: bool = True
    product_name: str
    sales_trends: SalesTrends
    visual_observations: List[str]
    cross_modal_hypotheses: List[CrossModalHypothesis]
    recommended_experiments: List[RecommendedExperiment]
