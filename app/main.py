import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from PIL import Image
import io

from app.schemas import AnalysisResponse
from app.analyzer import process_sales_csv, run_multimodal_analysis

app = FastAPI(title="ProductLens AI", description="Multimodal Product & Sales Auditor")

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
SAMPLE_DIR = STATIC_DIR / "sample_data"

# Mount static directory for assets
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(str(index_file))

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_product(
    image: UploadFile = File(None),
    csv_file: UploadFile = File(None, alias="csv"),
    use_sample: bool = Form(False)
):
    """
    Analyzes product image and sales CSV.
    Computes deterministic sales metrics via Pandas and generates multimodal insights via Gemini.
    """
    image_bytes = None
    csv_bytes = None
    mime_type = "image/jpeg"

    if use_sample:
        sample_img_path = SAMPLE_DIR / "sample_product.jpg"
        sample_csv_path = SAMPLE_DIR / "sample_sales.csv"
        if not sample_img_path.exists() or not sample_csv_path.exists():
            raise HTTPException(status_code=500, detail="Bundled sample data files are missing.")
        image_bytes = sample_img_path.read_bytes()
        csv_bytes = sample_csv_path.read_bytes()
        mime_type = "image/jpeg"
    else:
        if not image or not csv_file:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Both a product image and a sales CSV file are required."
            )
        image_bytes = await image.read()
        csv_bytes = await csv_file.read()
        mime_type = image.content_type or "image/jpeg"

    # Validate image integrity
    try:
        pil_img = Image.open(io.BytesIO(image_bytes))
        pil_img.verify()
        if pil_img.format:
            mime_type = f"image/{pil_img.format.lower()}"
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid image file. Please upload a readable JPG or PNG image."
        )

    # 1. Deterministic Sales Analysis with Pandas
    try:
        product_name, sales_trends, df = process_sales_csv(csv_bytes)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing sales data: {str(e)}"
        )

    # 2. Multimodal Reasoning with Gemini
    try:
        multimodal_payload = run_multimodal_analysis(
            image_bytes=image_bytes,
            mime_type=mime_type,
            product_name=product_name,
            sales_trends=sales_trends,
            df=df
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multimodal AI reasoning error: {str(e)}"
        )

    # 3. Deliver Unified Validated Response
    return AnalysisResponse(
        success=True,
        product_name=product_name,
        sales_trends=sales_trends,
        visual_observations=multimodal_payload.visual_observations,
        cross_modal_hypotheses=multimodal_payload.cross_modal_hypotheses,
        recommended_experiments=multimodal_payload.recommended_experiments,
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
