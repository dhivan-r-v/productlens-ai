import io
import os
import json
import logging
from typing import Tuple, List, Optional
import pandas as pd
from dotenv import load_dotenv
from PIL import Image

from app.schemas import (
    SalesTrends,
    MultimodalAnalysisPayload,
    CrossModalHypothesis,
    RecommendedExperiment,
    AnalysisResponse,
)

load_dotenv()
logger = logging.getLogger("productlens")

REQUIRED_COLUMNS = ["date", "product", "price", "units_sold", "revenue"]
CANDIDATE_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash",
    "gemini-3-flash-preview",
]

def process_sales_csv(csv_bytes: bytes) -> Tuple[str, SalesTrends, pd.DataFrame]:
    """
    Parses, validates, and computes deterministic metrics from the uploaded sales CSV.
    All mathematical calculations are performed deterministically in Pandas.
    """
    try:
        df = pd.read_csv(io.BytesIO(csv_bytes))
    except Exception as e:
        raise ValueError(f"Failed to parse CSV file: {str(e)}")

    # Standardize column headers
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Validate required columns
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required CSV columns: {', '.join(missing)}. Required columns are: {', '.join(REQUIRED_COLUMNS)}")

    if len(df) == 0:
        raise ValueError("The provided CSV file contains no data rows.")

    # Convert numeric fields
    try:
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0.0)
        df["units_sold"] = pd.to_numeric(df["units_sold"], errors="coerce").fillna(0).astype(int)
        df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0.0)
    except Exception as e:
        raise ValueError(f"Failed to convert numerical columns: {str(e)}")

    # Parse dates for sorting & trend calculation
    try:
        df["parsed_date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.sort_values(by="parsed_date").reset_index(drop=True)
    except Exception:
        pass

    product_name = str(df["product"].iloc[0]) if "product" in df.columns else "Product"

    # Deterministic calculations
    total_rev = round(float(df["revenue"].sum()), 2)
    total_units = int(df["units_sold"].sum())
    avg_price = round(float(df["price"].mean()), 2) if len(df) > 0 else 0.0

    # Determine trend trajectory
    trend_summary = "Stable sales performance"
    trend_bullets: List[str] = []

    if len(df) >= 2:
        half_idx = len(df) // 2
        first_half_rev = df.iloc[:half_idx]["revenue"].sum()
        second_half_rev = df.iloc[half_idx:]["revenue"].sum()

        if first_half_rev > 0:
            growth_pct = round(((second_half_rev - first_half_rev) / first_half_rev) * 100, 1)
            if growth_pct > 15:
                trend_summary = f"Upward trajectory (+{growth_pct}% in second half)"
            elif growth_pct < -15:
                trend_summary = f"Downward trajectory ({growth_pct}% in second half)"
            else:
                trend_summary = f"Steady revenue performance ({growth_pct:+0.1f}% change)"
        else:
            trend_summary = "Increasing from initial zero revenue"

        # Peak period calculation
        peak_row = df.loc[df["units_sold"].idxmax()]
        trend_bullets.append(
            f"Peak volume reached on {peak_row['date']} with {peak_row['units_sold']} units sold generating ${peak_row['revenue']:,.2f}."
        )

        # Recent period vs baseline
        recent_units = df.iloc[-1]["units_sold"]
        initial_units = df.iloc[0]["units_sold"]
        trend_bullets.append(
            f"Started at {initial_units} units ({df.iloc[0]['date']}) and closed at {recent_units} units ({df.iloc[-1]['date']}) at an average price of ${avg_price:,.2f}."
        )
    else:
        trend_bullets.append(f"Recorded single entry of {total_units} units generating ${total_rev:,.2f}.")

    sales_trends = SalesTrends(
        total_revenue=total_rev,
        total_units_sold=total_units,
        average_price=avg_price,
        overall_trend=trend_summary,
        trend_bullets=trend_bullets,
    )

    return product_name, sales_trends, df


def run_multimodal_analysis(
    image_bytes: bytes,
    mime_type: str,
    product_name: str,
    sales_trends: SalesTrends,
    df: pd.DataFrame,
    api_key: Optional[str] = None
) -> MultimodalAnalysisPayload:
    """
    Calls Google Gemini multimodal model to analyze the product image and sales metrics.
    Enforces strict data grounding and hypothesis framing, validating response with Pydantic.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError(
            "GEMINI_API_KEY is not configured. Please add your GEMINI_API_KEY to the .env file in the project root."
        )

    from google import genai
    from google.genai import types

    # Initialize client
    client = genai.Client(api_key=key)

    # Format historical records summary for prompt context
    records_summary = []
    for idx, row in df.iterrows():
        records_summary.append(
            f"- Date: {row['date']}, Price: ${row['price']}, Units Sold: {row['units_sold']}, Revenue: ${row['revenue']}"
        )
    records_text = "\n".join(records_summary)

    prompt = f"""You are ProductLens AI, an expert e-commerce product and merchandising auditor for independent sellers.
You are evaluating the product "{product_name}".

The user has uploaded a product photograph along with historical sales records.

### DETERMINISTIC SALES METRICS (Computed by Pandas):
- Total Revenue: ${sales_trends.total_revenue:,.2f}
- Total Units Sold: {sales_trends.total_units_sold}
- Average Price: ${sales_trends.average_price:,.2f}
- Overall Trajectory: {sales_trends.overall_trend}
- Key Trends:
{chr(10).join('- ' + b for b in sales_trends.trend_bullets)}

### DETAILED HISTORICAL SALES LOG:
{records_text}

### STRICT DATA-GROUNDING & REASONING RULES:
1. Data-Grounding Boundaries:
   - The provided data ONLY tracks: `date`, `product`, `price`, `units_sold`, and `revenue`.
   - Do NOT assume or claim to measure metrics not in the dataset (such as repeat purchase rates, customer retention, click-through rate, or conversion rate).
   - If a recommended experiment suggests measuring an external metric not present in this sales CSV (like CTR or page conversion rate), you MUST explicitly label it as: "(requires external analytics tracking)". Otherwise, ground the outcome metric directly in the available sales fields (e.g., "Weekly units sold", "Gross weekly revenue", or "Realized revenue per unit").

2. Visual Observations:
   - Carefully inspect the product image.
   - Note concrete, observable attributes: packaging materials/finish, color palette, logo/text prominence, design clarity, perceived luxury or budget tier.
   - State these strictly as objective visual observations, NOT assumptions about buyer emotions.

3. Cross-Modal Hypotheses (CORE KERNEL):
   - Synthesize the visual presentation with the sales trends (units sold over time, price shifts, revenue trajectories).
   - For example: examine how packaging minimalism, perceived tier, or visual clarity might relate to price adjustments (e.g. price dropping from $32 to $28) and sales volume drop-offs.
   - CRITICAL REQUIREMENT: Present every connection strictly as a TESTABLE HYPOTHESIS or FACTOR WORTH INVESTIGATING.
   - DO NOT claim that the product image or design definitively caused a sales outcome. Frame as: "Factor worth investigating: [Hypothesis]".
   - Each hypothesis must cite both the supporting sales data (using ONLY available fields: date, price, units sold, revenue) and the specific visual factor.

4. Recommended Experiments:
   - Provide 2 to 3 practical, grounded experiments the business owner can run.
   - Focus on actions directly supported by the inputs (e.g., A/B testing product photography styles, testing pricing tiers, testing clear visual benefit callouts).
   - Each recommendation must specify:
     (a) action title
     (b) what specific change to test
     (c) what concrete outcome metric to measure over a test period (e.g., "Weekly units sold over a 14-day test period" or "Weekly revenue at the new price tier"; if suggesting an external metric like conversion rate, explicitly append "(requires external analytics tracking)").

Return your response strictly according to the provided schema.
"""

    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

    last_error = None
    for model_name in CANDIDATE_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[image_part, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=MultimodalAnalysisPayload.model_json_schema(),
                ),
            )

            response_text = response.text
            if not response_text:
                continue

            # Backend validation: parse with Pydantic
            payload_data = json.loads(response_text)
            validated_payload = MultimodalAnalysisPayload.model_validate(payload_data)
            return validated_payload

        except Exception as e:
            error_str = str(e)
            last_error = error_str
            logger.warning(f"Model {model_name} failed: {error_str}. Trying next candidate...")
            continue

    if last_error:
        if "API_KEY_INVALID" in last_error or "invalid api key" in last_error.lower():
            raise ValueError("The provided GEMINI_API_KEY is invalid. Please check your key in .env.")
        raise ValueError(f"Gemini Multimodal Analysis failed: {last_error}")
    raise ValueError("Gemini Multimodal Analysis failed to produce a valid response.")
