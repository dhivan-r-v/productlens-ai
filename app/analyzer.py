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
HYPOTHESIS_PREFIX = "Factor worth investigating:"
MIN_RELIABLE_PERIODS = 4
# Low temperature keeps hypotheses steady across repeat runs on the same inputs
MODEL_TEMPERATURE = 0.2

# Common header variants from store exports, mapped to the required column names.
# Keep in sync with CSV_HEADER_ALIASES in static/app.js.
COLUMN_ALIASES = {
    "date": ["order_date", "week", "week_start", "period", "day"],
    "product": ["product_name", "item", "item_name", "title", "sku"],
    "price": ["unit_price", "selling_price", "avg_price"],
    "units_sold": ["units", "qty", "quantity", "quantity_sold", "units_ordered"],
    "revenue": ["sales", "total_sales", "net_sales", "gross_sales", "amount", "total"],
    # Optional columns: unlock conversion and return-rate analysis when present
    "views": ["sessions", "page_views", "pageviews", "visits", "listing_views"],
    "returns": ["returned", "units_returned", "returned_units", "return_units"],
}
OPTIONAL_COLUMNS = ["views", "returns"]
# Relative change between halves that counts as a meaningful shift
SHIFT_THRESHOLD_PCT = 15


def normalize_header(name: str) -> str:
    return "_".join(str(name).strip().lower().replace("-", " ").split())


def apply_column_aliases(df: pd.DataFrame) -> pd.DataFrame:
    """Renames the first matching alias to each required column that is missing."""
    renames = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        if canonical in df.columns:
            continue
        match = next((a for a in aliases if a in df.columns and a not in renames), None)
        if match:
            renames[match] = canonical
    return df.rename(columns=renames)


def to_number(series: pd.Series) -> pd.Series:
    """Strips currency symbols and thousands separators (e.g. "$1,234.50") before converting."""
    cleaned = series.astype(str).str.replace(r"[^0-9.\-]", "", regex=True)
    return pd.to_numeric(cleaned, errors="coerce")

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
    df.columns = [normalize_header(c) for c in df.columns]
    df = apply_column_aliases(df)

    # Validate required columns
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required CSV columns: {', '.join(missing)}. Required columns are: {', '.join(REQUIRED_COLUMNS)}")

    if len(df) == 0:
        raise ValueError("The provided CSV file contains no data rows.")

    # Convert numeric fields
    try:
        df["price"] = to_number(df["price"]).fillna(0.0)
        df["units_sold"] = to_number(df["units_sold"]).fillna(0).astype(int)
        df["revenue"] = to_number(df["revenue"]).fillna(0.0)
        for col in OPTIONAL_COLUMNS:
            if col in df.columns:
                df[col] = to_number(df[col]).fillna(0).astype(int)
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
    # Revenue-weighted average: what a unit actually sold for across the period
    avg_price = round(total_rev / total_units, 2) if total_units > 0 else 0.0

    # Determine trend trajectory
    trend_summary = "Stable sales performance"
    trend_bullets: List[str] = []

    if len(df) < MIN_RELIABLE_PERIODS:
        trend_bullets.append(
            f"⚠ Limited data: only {len(df)} period(s) recorded. Treat trends as indicative only; "
            f"{MIN_RELIABLE_PERIODS}+ periods are recommended for reliable patterns."
        )

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
            f"Started at {initial_units} units ({df.iloc[0]['date']}) at ${df.iloc[0]['price']:,.2f} and closed at {recent_units} units ({df.iloc[-1]['date']}) at ${df.iloc[-1]['price']:,.2f}."
        )

        trend_bullets.extend(describe_price_changes(df))
        if "views" in df.columns:
            trend_bullets.extend(describe_funnel(df))
        if "returns" in df.columns:
            trend_bullets.extend(describe_returns(df))
    else:
        trend_bullets.append(f"Recorded single entry of {total_units} units generating ${total_rev:,.2f}.")

    total_views = int(df["views"].sum()) if "views" in df.columns else None
    total_returns = int(df["returns"].sum()) if "returns" in df.columns else None

    sales_trends = SalesTrends(
        total_revenue=total_rev,
        total_units_sold=total_units,
        average_price=avg_price,
        overall_trend=trend_summary,
        trend_bullets=trend_bullets,
        total_views=total_views,
        conversion_rate=pct(total_units, total_views),
        total_returns=total_returns,
        return_rate=pct(total_returns, total_units),
    )

    return product_name, sales_trends, df


def pct(part: Optional[float], whole: Optional[float]) -> Optional[float]:
    if part is None or not whole:
        return None
    return round(part / whole * 100, 2)


def relative_change(before: float, after: float) -> float:
    return (after - before) / before * 100 if before else 0.0


def split_halves(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    half_idx = len(df) // 2
    return df.iloc[:half_idx], df.iloc[half_idx:]


def describe_funnel(df: pd.DataFrame) -> List[str]:
    """
    Separates "fewer people saw it" from "fewer viewers bought it" by comparing
    views per period and conversion (units / views) between the two halves.
    """
    first, second = split_halves(df)
    conv_1 = pct(first["units_sold"].sum(), first["views"].sum())
    conv_2 = pct(second["units_sold"].sum(), second["views"].sum())
    if conv_1 is None or conv_2 is None:
        return []

    views_1, views_2 = first["views"].mean(), second["views"].mean()
    views_change = relative_change(views_1, views_2)
    conv_change = relative_change(conv_1, conv_2)

    bullets = [
        f"Conversion rate moved from {conv_1:.1f}% to {conv_2:.1f}% (first vs second half), while average views "
        f"per period went from {views_1:,.0f} to {views_2:,.0f} ({views_change:+.0f}%)."
    ]

    views_fell = views_change <= -SHIFT_THRESHOLD_PCT
    conv_fell = conv_change <= -SHIFT_THRESHOLD_PCT
    if conv_fell and not views_fell:
        bullets.append(
            "Funnel signal: views held roughly steady but fewer viewers bought, which points to the listing itself "
            "(photo, price or description) rather than visibility."
        )
    elif views_fell and not conv_fell:
        bullets.append(
            "Funnel signal: fewer people viewed the listing while conversion held up, which points to visibility or "
            "traffic rather than the listing itself."
        )
    elif views_fell and conv_fell:
        bullets.append("Funnel signal: both views and conversion fell, so visibility and the listing both shifted.")
    return bullets


def describe_returns(df: pd.DataFrame) -> List[str]:
    """Reports how the share of sold units coming back changed between the two halves."""
    first, second = split_halves(df)
    rate_1 = pct(first["returns"].sum(), first["units_sold"].sum())
    rate_2 = pct(second["returns"].sum(), second["units_sold"].sum())
    if rate_1 is None or rate_2 is None:
        return []

    bullets = [f"Return rate moved from {rate_1:.1f}% to {rate_2:.1f}% of units sold (first vs second half)."]
    if relative_change(rate_1, rate_2) >= SHIFT_THRESHOLD_PCT:
        bullets.append("Returns are rising as a share of units sold.")
    return bullets


def describe_price_changes(df: pd.DataFrame) -> List[str]:
    """
    Splits the sorted sales log into runs of consecutive rows at the same price and
    compares unit volume across each price change. Also flags when units were already
    falling before a change, so a decline is not wrongly blamed on the new price.
    """
    bullets: List[str] = []
    segment_ids = (df["price"] != df["price"].shift()).cumsum()
    segments = [seg for _, seg in df.groupby(segment_ids, sort=False)]

    for before, after in zip(segments, segments[1:]):
        old_price = before["price"].iloc[0]
        new_price = after["price"].iloc[0]
        direction = "cut" if new_price < old_price else "increase"
        bullets.append(
            f"Price {direction} from ${old_price:,.2f} to ${new_price:,.2f} on {after['date'].iloc[0]}: "
            f"average weekly units {before['units_sold'].mean():,.1f} at ${old_price:,.2f} vs "
            f"{after['units_sold'].mean():,.1f} at ${new_price:,.2f}."
        )

        # Was volume already falling at the old price? Compare its peak to its last period.
        if len(before) >= 2:
            peak_units = int(before["units_sold"].max())
            last_units = int(before["units_sold"].iloc[-1])
            if last_units < peak_units:
                bullets.append(
                    f"Units were already declining before the price {direction} "
                    f"({peak_units} → {last_units} while still at ${old_price:,.2f})."
                )

    return bullets


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
    has_views = "views" in df.columns
    has_returns = "returns" in df.columns

    records_summary = []
    for idx, row in df.iterrows():
        line = f"- Date: {row['date']}, Price: ${row['price']}, Units Sold: {row['units_sold']}, Revenue: ${row['revenue']}"
        if has_views:
            line += f", Views: {row['views']}"
        if has_returns:
            line += f", Returns: {row['returns']}"
        records_summary.append(line)
    records_text = "\n".join(records_summary)

    tracked_fields = ["date", "product", "price", "units_sold", "revenue"] + [
        col for col in OPTIONAL_COLUMNS if col in df.columns
    ]
    untracked_examples = ["repeat purchase rates", "customer retention", "click-through rate", "ad spend"]
    if not has_views:
        untracked_examples.append("conversion rate")
    if not has_returns:
        untracked_examples.append("return rate")

    optional_metrics = []
    if has_views:
        optional_metrics.append(f"- Total Views: {sales_trends.total_views:,}")
        optional_metrics.append(f"- Overall Conversion Rate (units / views): {sales_trends.conversion_rate}%")
    if has_returns:
        optional_metrics.append(f"- Total Units Returned: {sales_trends.total_returns:,}")
        optional_metrics.append(f"- Overall Return Rate (returns / units sold): {sales_trends.return_rate}%")
    optional_metrics_text = ("\n" + "\n".join(optional_metrics)) if optional_metrics else ""

    funnel_rules = []
    if has_views:
        funnel_rules.append(
            "   - Views are available. Use the funnel signal in Key Trends to weigh visual hypotheses: they are most relevant "
            "when views held steady but conversion fell. If views fell, name visibility/traffic as the larger factor and keep "
            "visual hypotheses secondary. Conversion rate is an in-dataset metric you may cite and measure."
        )
    if has_returns:
        funnel_rules.append(
            "   - Returns are available. Consider whether the photo may set expectations (finish, size, color, scale) that "
            "differ from the delivered product, citing the return-rate trend. Return rate is an in-dataset metric you may cite and measure."
        )
    if not funnel_rules:
        funnel_rules.append(
            "   - No views or returns data was provided, so you cannot tell whether a decline comes from visibility or from the "
            "listing itself. Acknowledge this where relevant."
        )
    funnel_rules_text = "\n".join(funnel_rules)

    prompt = f"""You are ProductLens AI, an expert e-commerce product and merchandising auditor for independent sellers.
You are evaluating the product "{product_name}".

The user has uploaded a product photograph along with historical sales records.

### DETERMINISTIC SALES METRICS (Computed by Pandas):
- Total Revenue: ${sales_trends.total_revenue:,.2f}
- Total Units Sold: {sales_trends.total_units_sold}
- Average Price: ${sales_trends.average_price:,.2f}
- Overall Trajectory: {sales_trends.overall_trend}{optional_metrics_text}
- Key Trends:
{chr(10).join('- ' + b for b in sales_trends.trend_bullets)}

### DETAILED HISTORICAL SALES LOG:
{records_text}

### STRICT DATA-GROUNDING & REASONING RULES:
1. Data-Grounding Boundaries:
   - The provided data ONLY tracks: {', '.join(f'`{f}`' for f in tracked_fields)}.
   - Do NOT assume or claim to measure metrics not in the dataset (such as {', '.join(untracked_examples)}).
   - If a recommended experiment suggests measuring an external metric not present in this sales CSV, you MUST explicitly label it as: "(requires external analytics tracking)". Otherwise, ground the outcome metric directly in the available fields (e.g., "Weekly units sold", "Gross weekly revenue", or "Realized revenue per unit").
{funnel_rules_text}

2. Visual Observations:
   - Carefully inspect the product image.
   - Note concrete, observable attributes: packaging materials/finish, color palette, logo/text prominence, design clarity, perceived luxury or budget tier.
   - State these strictly as objective visual observations, NOT assumptions about buyer emotions.

3. Cross-Modal Hypotheses (CORE KERNEL):
   - Synthesize the visual presentation with the sales trends (units sold over time, price shifts, revenue trajectories).
   - For example: examine how packaging minimalism, perceived tier, or visual clarity might relate to price adjustments (e.g. price dropping from $32 to $28) and sales volume drop-offs.
   - CRITICAL REQUIREMENT: Present every connection strictly as a TESTABLE HYPOTHESIS or FACTOR WORTH INVESTIGATING.
   - Every `hypothesis` MUST begin with exactly "Factor worth investigating:" and use hedged language ("may", "could", "might").
   - NEVER use causal wording such as "caused", "led to", "leading to", "resulted in", "contributing to", "driving", "due to", "because of", "fails to", "failing to", or "is hindering". Describe co-occurrence instead (e.g., "may be related to", "coincides with"). You have correlational data from one product; you cannot know causes.
   - If the Key Trends above flag limited data, state that uncertainty in each hypothesis and keep claims especially tentative.
   - Respect timing in the Key Trends above: if units were already declining before a price change, do not attribute the decline to that price change.
   - Each hypothesis must cite both the supporting sales data (using ONLY available fields: date, price, units sold, revenue) and the specific visual factor.
   - Each hypothesis must include `how_to_test`: one concrete way the seller could confirm or rule it out.

4. Recommended Experiments:
   - Provide 2 to 3 practical, grounded experiments the business owner can run.
   - Focus on actions directly supported by the inputs (e.g., A/B testing product photography styles, testing pricing tiers, testing clear visual benefit callouts).
   - Each recommendation must specify:
     (a) action title
     (b) what specific change to test
     (c) what concrete outcome metric to measure over a test period (e.g., "Weekly units sold over a 14-day test period" or "Weekly revenue at the new price tier"; if suggesting a metric outside the tracked fields listed in rule 1, explicitly append "(requires external analytics tracking)"; never add that label to a metric computable from the tracked fields).

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
                    temperature=MODEL_TEMPERATURE,
                    response_schema=MultimodalAnalysisPayload.model_json_schema(),
                ),
            )

            response_text = response.text
            if not response_text:
                continue

            # Backend validation: parse with Pydantic
            payload_data = json.loads(response_text)
            validated_payload = MultimodalAnalysisPayload.model_validate(payload_data)

            # Guarantee hypothesis framing even if the model skips the required prefix
            for h in validated_payload.cross_modal_hypotheses:
                if not h.hypothesis.lower().startswith(HYPOTHESIS_PREFIX.lower()):
                    h.hypothesis = f"{HYPOTHESIS_PREFIX} {h.hypothesis}"
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
