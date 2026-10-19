---
doc: spec
status: approved
---

# ProductLens AI — Technical Specification

## How This Works, In Plain Language
ProductLens AI is built as a single, cohesive local application with two main layers:
1. **The Web Interface (Frontend):** A clean, single-page website built with standard HTML, CSS, and vanilla JavaScript. It runs in the user's browser, lets them drop in a product image and a sales CSV (or click "Load Sample Data"), previews the image, and displays the four structured results cards. It does not use heavy frameworks or build tools.
2. **The Python Server (FastAPI):** A lightweight backend server running locally on the user's computer. It handles two critical tasks:
   - **Deterministic Data Processing with Pandas:** When a CSV arrives, Pandas validates the schema and deterministically calculates all numerical metrics (total revenue, units sold, average price, and trajectory over time). No numerical calculations are delegated to the LLM.
   - **Schema-Constrained Multimodal AI with Gemini:** It takes the product image and the Pandas-calculated summary, passes both to the Google Gemini multimodal model with strict schema constraints and prompt guidelines (instructing the model to form testable hypotheses rather than causal claims), and validates the returned payload using Pydantic on the backend before delivering it to the frontend.
3. **Structured Delivery:** The AI response is parsed and validated into the four cards defined in the PRD, ensuring high reliability and zero conversational fluff.

This shape builds directly on the learner's existing Python and data analysis foundation, eliminates unnecessary frontend build tooling, and exposes the exact mechanics of how data, validation, and multimodal models interact inside a real codebase.

## The Core Journey Through the System
- **Implements:** `prd.md > The Core Journey`

1. **Page Load:** The user visits `http://127.0.0.1:8000`. FastAPI serves `index.html` from the `static/` directory. The browser loads `styles.css` and `app.js`. The input dropzones are empty, the "Analyze Product" button is disabled, and results cards are hidden.
2. **File Selection or Sample Data:**
   - *Option A (User Files):* The user selects an image and a CSV. `app.js` renders an image thumbnail preview via `URL.createObjectURL(file)` and records the files in memory.
   - *Option B (Sample Data):* The user clicks "Load Sample Data". `app.js` fetches `static/sample_data/sample_product.jpg` and `static/sample_data/sample_sales.csv`, displays the preview, and marks both as ready.
   - *Validation:* When both files are present, `app.js` enables the "Analyze Product" button.
3. **Analysis Request:** The user clicks "Analyze Product".
   - `app.js` sets the UI into a loading state ("Analyzing your product and sales data...").
   - `app.js` packages the image and CSV into a `FormData` object and fires a `POST` request to `/api/analyze`.
4. **Backend Processing & Multi-Stage Validation:**
   - FastAPI receives the multipart request at `/api/analyze`.
   - **Input Validation:** The backend validates file types and sizes. `analyzer.py` loads the CSV into **Pandas**, verifies required columns (`date`, `product`, `price`, `units_sold`, `revenue`), and computes deterministic summary statistics.
   - **Multimodal AI Call:** `analyzer.py` passes the image bytes and the computed sales summary into the **Google GenAI SDK** (`gemini-2.5-flash`). The prompt explicitly directs the model to treat cross-modal connections as testable hypotheses rather than definitive causal claims. The request is schema-constrained via `response_schema`.
   - **Backend Response Validation:** The raw AI response is parsed and validated through a backend **Pydantic** schema (`MultimodalAnalysisPayload`) before merging. If validation encounters missing fields, defensive parsing ensures safe defaults without breaking the UI.
   - FastAPI merges the deterministic Pandas calculations with the validated AI reasoning and returns a unified JSON response.
5. **Rendering Results:** `app.js` receives the response, hides the loading state, and populates the four cards:
   - *Card 1: Sales Data Trends* (displays computed metrics & bullet points from Pandas)
   - *Card 2: Visual Observations* (displays product packaging & visual presentation factors)
   - *Card 3: Cross-Modal Hypotheses* (displays hypotheses linking visual traits to sales data)
   - *Card 4: Recommended Experiments* (displays testable action items with target metrics)
6. **Reset:** The user clicks "Analyze Another Product". `app.js` clears all file inputs, thumbnails, and result cards, returning the UI to the fresh initial state.

## Stack
- **Backend Language:** Python 3.10+
- **Backend Framework:** [FastAPI](https://fastapi.tiangolo.com) (`fastapi`, `uvicorn`, `python-multipart`)
  - *Rationale:* Fast, lightweight, type-safe API framework with native async support and simple file upload handling.
- **Data Processing:** [Pandas](https://pandas.pydata.org) (`pandas`)
  - *Rationale:* Handles deterministic CSV parsing, column validation, and mathematical aggregations locally.
- **Multimodal AI SDK:** [Google GenAI Python SDK](https://github.com/googleapis/python-genai) (`google-genai`)
  - *Rationale:* Official Google SDK for Gemini 2.5 Flash (`gemini-2.5-flash`). Supports native multimodal input and schema-constrained JSON outputs.
- **Data Validation:** [Pydantic](https://docs.pydantic.dev/) (`pydantic`)
  - *Rationale:* Strictly validates both the incoming requests and the AI responses on the backend before returning data to the frontend.
- **Environment Management:** [python-dotenv](https://saurabh-kumar.com/python-dotenv/)
  - *Rationale:* Loads `GEMINI_API_KEY` securely from `.env` without exposing keys in code or commits.
- **Frontend:** Vanilla HTML5, Vanilla CSS3, Vanilla JavaScript (ES6+)
  - *Rationale:* Zero build tools or npm dependencies; renders instantly with full control over aesthetics.

## Where It Runs and How Someone Tries It
- **Runtime:** Local environment (Windows, macOS, or Linux).
- **Environment Variables:** A `.env` file containing:
  ```bash
  GEMINI_API_KEY="your-gemini-api-key-here"
  ```
  *(A template `.env.example` is provided in the repository.)*
- **Installation:**
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command:**
  ```bash
  uvicorn app.main:app --reload --port 8000
  ```
- **Demo Access:** Open `http://127.0.0.1:8000` in any web browser.
- **Public Repository:** https://github.com/dhivan-r-v/productlens-ai
- **Demo Video:** _(to be added)_
- **Demo Recording Target:** Demonstrable in a 1-to-2 minute screen recording (loading sample data, clicking Analyze, walking through the four result cards, clicking reset). Deployment to cloud is optional and not required.

## Look and Feel
- **Carried forward from:** `prd.md > Look and Feel`
- **Theme:** Crisp, modern light theme.
- **Palette:**
  - Background: Off-white neutral (`#F8FAFC`).
  - Card Surfaces: Crisp pure white (`#FFFFFF`) with subtle slate borders (`#E2E8F0`) and smooth box-shadows.
  - Primary Accent: Deep royal indigo (`#1E3A8A` / `#2563EB`) for headers, primary buttons, and focal elements.
  - Supporting Accent: Subtle emerald green (`#059669` / `#10B981`) for positive trend metrics and experiment badges.
  - Text: High-contrast slate (`#0F172A` for headings, `#334155` for body, `#64748B` for secondary captions).
- **Typography:** Modern clean sans-serif typography (`Inter`, `system-ui`).
- **Density & Tone:** Spacious, structured, data-focused product audit dashboard—strictly avoiding cluttered tables, generic chatbot bubbles, or dark neon glows.

## Components

### 1. Web UI Surface (`static/index.html`, `static/styles.css`, `static/app.js`)
- **Implements:** `prd.md > Screens and Layout`, `prd.md > Features and Behavior > 1. File Ingestion & Validation`, `prd.md > Features and Behavior > 3. State Reset & Session Management`
- **Responsibilities:**
  - Renders input dropzones for Product Image and Sales CSV.
  - Manages image thumbnail generation and display.
  - Provides one-click "Load Sample Data" action.
  - Enforces button state (disabled until both inputs are valid).
  - Handles client-side fetch call with loading spinner/banner.
  - Populates the 4 result cards dynamically from the validated JSON response.
  - Provides "Analyze Another Product" reset functionality.

### 2. FastAPI Application & API Router (`app/main.py`)
- **Implements:** `prd.md > Features and Behavior > 1. File Ingestion & Validation`
- **Responsibilities:**
  - Mounts the `static/` directory to serve the frontend interface.
  - Defines `POST /api/analyze` accepting `image` (UploadFile), `csv` (UploadFile), and optional `use_sample` (boolean).
  - Performs initial file type and size verification.
  - Catches validation errors and returns friendly HTTP 422 JSON errors if required files or CSV headers are missing.
  - Invokes `analyzer.py` and returns structured, validated analysis results.

### 3. Data Crunching & Pandas Processor (`app/analyzer.py > process_sales_csv`)
- **Implements:** `prd.md > Features and Behavior > 2. Multimodal Analysis & Structured Cards (Card 1)`
- **Responsibilities:**
  - Parses uploaded CSV into a Pandas DataFrame.
  - Validates required column headers: `date`, `product`, `price`, `units_sold`, `revenue`.
  - Calculates deterministic summary statistics:
    - Total Revenue (`df['revenue'].sum()`)
    - Total Units Sold (`df['units_sold'].sum()`)
    - Average Selling Price (`df['price'].mean()`)
    - Overall Trend (revenue trajectory over date periods).
  - Generates bullet-point summaries of trend trajectory directly from data.

### 4. Multimodal AI Engine (`app/analyzer.py > run_multimodal_analysis`)
- **Implements:** `prd.md > Features and Behavior > 2. Multimodal Analysis & Structured Cards (Cards 2, 3, 4)`
- **Responsibilities:**
  - Initializes `google-genai` client using `GEMINI_API_KEY`.
  - Formulates system and task prompt incorporating the calculated sales metrics and business context.
  - Explicitly instructs Gemini to present cross-modal relationships as **testable hypotheses or factors worth investigating**, strictly avoiding statements of unproven causality.
  - Configures schema constraint (`response_schema`).
  - Validates the returned JSON payload on the backend using Pydantic before returning to caller.
  - Merges AI reasoning with Pandas metrics into the final validated `AnalysisResponse` object.

### 5. Data Schemas (`app/schemas.py`)
- **Implements:** `prd.md > Features and Behavior > 2. Multimodal Analysis & Structured Cards`
- **Responsibilities:**
  - Pydantic models defining the backend validation contract:
    - `SalesTrends`: Deterministic numerical metrics calculated by Pandas.
    - `MultimodalAnalysisPayload`: Schema for Gemini output (`visual_observations`, `cross_modal_hypotheses`, `recommended_experiments`).
    - `AnalysisResponse`: Unified validated schema returned to the client.

## Data Model
- **Client State (`app.js`):**
  - `selectedImage`: File object or sample URL.
  - `selectedCsv`: File object or sample URL.
  - `analysisResult`: JSON object returned from `/api/analyze`.
  - *Persistence:* In-memory only; resetting or page reload clears state.
- **Analysis Response Schema (`AnalysisResponse`):**
  ```json
  {
    "sales_trends": {
      "total_revenue": 14250.00,
      "total_units_sold": 475,
      "average_price": 30.00,
      "overall_trend": "Declining over the past 6 weeks",
      "trend_bullets": [
        "Initial launch peaked at 120 units/week at $30 price point.",
        "Sales dropped 45% in weeks 4-6 despite price remaining constant."
      ]
    },
    "visual_observations": [
      "Minimalist monochrome packaging with small typography.",
      "Key product benefit callouts are not immediately visible from the primary front-facing view.",
      "Premium aesthetic feel matching higher-tier price brackets."
    ],
    "cross_modal_hypotheses": [
      {
        "hypothesis": "Premium packaging aesthetic may be conflicting with budget search intent, dampening repeat conversions.",
        "supporting_data": "Steady decline in units sold despite $30 price stability.",
        "visual_factor": "High-end luxury bottle design with muted, subtle branding."
      }
    ],
    "recommended_experiments": [
      {
        "action": "A/B Test High-Contrast Hero Photography",
        "what_to_change": "Photograph product against a lifestyle background highlighting the product size and primary benefit.",
        "metric_to_measure": "Units sold over a 14-day test period."
      },
      {
        "action": "Test $34.99 Premium Price Point",
        "what_to_change": "Align the pricing more closely with the luxury aesthetic to test whether higher price increases perceived value.",
        "metric_to_measure": "Gross revenue and unit conversion rate."
      }
    ]
  }
  ```

## File Structure
```
AI-Basics-Hackathon/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI server, static mounts, /api/analyze route
│   ├── analyzer.py              # Pandas data processing & Gemini multimodal client
│   └── schemas.py               # Pydantic schemas for backend validation
├── static/
│   ├── index.html               # Single-page UI markup
│   ├── styles.css               # Clean modern light theme styling
│   ├── app.js                   # Frontend event handlers, file preview & card rendering
│   └── sample_data/             # Pre-bundled demo files
│       ├── sample_product.jpg   # Sample e-commerce product photo
│       └── sample_sales.csv     # Sample sales history matching the product
├── devpost/                     # Devpost curriculum planning docs
│   ├── learner-profile.md
│   ├── scope.md
│   ├── prd.md
│   └── spec.md
├── .env.example                 # Environment variable template
├── .gitignore                   # Ignores .env and devpost/learner-profile.md
├── requirements.txt             # Python dependencies
└── README.md                    # Project overview and run instructions
```

## External Services and Dependencies
- **Google Gemini API (`google-genai`):**
  - **Endpoint / Model:** `gemini-2.5-flash` via `client.models.generate_content`.
  - **Payload:** Multimodal contents (PIL Image/bytes + Text Prompt + Response Schema).
  - **Authentication:** `GEMINI_API_KEY` passed via environment variable.
  - **Documentation:** [Google GenAI SDK Documentation](https://github.com/googleapis/python-genai)
  - **Cost & Limits:** Generous free tier via Google AI Studio; low latency (~2-3s response time).

## Important Failure Modes
1. **Invalid or Missing CSV Columns:**
   - *Failure:* User uploads a CSV lacking `date`, `product`, `price`, `units_sold`, or `revenue`.
   - *Behavior:* Pandas validation immediately catches missing columns; FastAPI returns HTTP 422 with a message listing the missing required columns. The frontend displays an inline red alert banner.
2. **Unsupported or Corrupted Image:**
   - *Failure:* User uploads a non-image file or corrupted file.
   - *Behavior:* FastAPI/PIL checks file integrity; returns HTTP 422 ("Please upload a valid JPG or PNG image"). The frontend displays an error banner without wiping the CSV.
3. **Gemini API Error, Invalid Key, or Schema Mismatch:**
   - *Failure:* Invalid API key, rate limit reached, or AI output fails validation.
   - *Behavior:* `analyzer.py` catches errors and returns HTTP 500 with a clear message ("Unable to complete analysis. Please verify your API key and retry."). The frontend preserves uploaded inputs and displays a retry action.

## What Was Simplified and Why
- **Deterministic calculations in Pandas instead of LLM calculations:**
  - *Why:* LLMs can hallucinate math or round inconsistently; Pandas guarantees 100% deterministic, reproducible numbers for Card 1.
- **Backend Pydantic validation instead of blind LLM trust:**
  - *Why:* Schema-constrained responses from LLMs can occasionally truncate or deviate; backend validation ensures only clean, complete payloads reach the UI.
- **Local in-memory files instead of Cloud Storage (S3/GCS):**
  - *Why:* Storing images in local temporary memory or passing bytes directly to Gemini avoids AWS/GCP bucket configuration, credential overhead, and storage costs for a proof of concept.
- **Client-side session state instead of a Database (PostgreSQL/SQLite):**
  - *Why:* The PRD specifically targets single-product audits without audit history; avoiding databases eliminates migration scripts and schema maintenance.
- **FastAPI static file mounting instead of a separate Node.js / React dev server:**
  - *Why:* Running a single command (`uvicorn app.main:app`) runs the entire stack simultaneously on one port, eliminating CORS setup, npm installs, and dual-terminal management.

## Decisions and Open Issues
- **Decisions Made:**
  - *Architecture:* FastAPI + Vanilla HTML/CSS/JS agreed upon to align with the learner's Python strengths while keeping the frontend simple and transparent.
  - *Mathematical Determinism:* All core sales metrics calculated strictly in Pandas; Gemini focuses purely on qualitative multimodal reasoning.
  - *Hypothesis Framing:* Prompt explicitly requires Gemini to present cross-modal relationships as testable hypotheses rather than causal claims.
  - *Dual Validation:* Strict validation on both user uploads and the AI response before delivering results to the frontend.
  - *Security:* API key kept in local `.env`, ignored in Git, with a sanitized `.env.example` provided for repository sharing.
- **One Useful Unknown & Resolution:**
  - *The Question:* How to guarantee end-to-end data flow and structured output (preventing Gemini from returning an unstructured text wall).
  - *Clarification:* Using `google-genai`'s `response_schema` parameter with Pydantic schemas provides schema constraints. Pandas handles deterministic mathematical aggregation locally, ensuring the numbers in Card 1 are 100% accurate, while Gemini focuses purely on multimodal reasoning for Cards 2, 3, and 4.
- **Open Questions:**
  - None blocking implementation. Everything is ready for `5-build`.
