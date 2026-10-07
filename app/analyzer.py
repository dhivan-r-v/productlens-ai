import io
import os
from typing import Tuple, List
import pandas as pd
from dotenv import load_dotenv

from app.schemas import SalesTrends, MultimodalAnalysisPayload, AnalysisResponse, CrossModalHypothesis, RecommendedExperiment

load_dotenv()

REQUIRED_COLUMNS = ["date", "product", "price", "units_sold", "revenue"]

def process_sales_csv(csv_bytes: bytes) -> Tuple[str, SalesTrends, pd.DataFrame]:
    """
    Parses, validates, and computes deterministic metrics from the uploaded sales CSV.
    """
    try:
        # Read CSV with pandas
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
