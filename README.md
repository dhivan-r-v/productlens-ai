# ProductLens AI

A local web app that analyzes a product photo together with a sales CSV. Pandas computes the sales metrics, and Google Gemini looks at the image and the trends together to suggest testable hypotheses and experiments.

Built for the Devpost "Build With AI: Basics" learning hackathon.

## Requirements

- Python 3.10+
- A Google Gemini API key ([Google AI Studio](https://aistudio.google.com/))

## Setup

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your key:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

`.env` is git-ignored. Never commit a real key.

## Run

```bash
uvicorn app.main:app --port 8000
```

Open http://127.0.0.1:8000, click **Load Sample Data**, then **Analyze Product**.

## Using your own data

Upload a JPG/PNG/WEBP product image and a CSV with these columns:

| column | example |
| --- | --- |
| `date` | `2026-08-01` |
| `product` | `Aura Minimalist Ceramic Tumbler` |
| `price` | `32.00` |
| `units_sold` | `110` |
| `revenue` | `3520.00` |

Two **optional** columns unlock more analysis:

| column | example | adds |
| --- | --- | --- |
| `views` (or `sessions`, `page_views`, `visits`) | `2200` | Conversion rate, plus a funnel signal: did fewer people see the listing, or did fewer viewers buy? |
| `returns` (or `units_returned`, `returned`) | `4` | Return rate (units returned ÷ units sold) and its trend |

The bundled sample data includes both.

Common export headers are also accepted (for example `Order Date`, `Product Name`, `Unit Price`, `Qty`, `Total Sales`), and values like `$1,234.50` are parsed. Fewer than 4 rows triggers a limited-data warning.

See `static/sample_data/sample_sales.csv`.

## How it works

1. **Sales Data Trends** (`app/analyzer.py > process_sales_csv`): Pandas computes totals, the average price (revenue ÷ units), the trajectory, and how unit volume shifted around each price change.
2. **Visual Observations, Cross-Modal Hypotheses, Recommended Experiments** (`app/analyzer.py > run_multimodal_analysis`): The image and the computed metrics are sent to Gemini with a response schema. The output is validated with Pydantic (`app/schemas.py`) before it reaches the UI. Hypotheses are framed as factors worth investigating, not causal claims.

The frontend is plain HTML/CSS/JS in `static/`, served by FastAPI (`app/main.py`).

## Project docs

Planning documents (scope, PRD, spec, build checklist) and an architecture map (`app-map.html`) are in `devpost/`.

## License

MIT. See [LICENSE](LICENSE).
