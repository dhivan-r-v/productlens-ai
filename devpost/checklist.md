---
doc: checklist
status: approved
---

# Build Checklist

Build mode: learn

## Slices

- [x] **1. Bootstrap app, UI scaffold, and deterministic sales trends**
  Becomes usable: A running local web app at `http://127.0.0.1:8000` with the crisp light-theme interface. The user can load sample data or upload a sales CSV, see the image preview, and view deterministic Sales Data Trends (revenue, units, average price, trajectory) calculated by Pandas in Card 1.
  Why now: Bootstraps the project scaffold, dependencies, sample data, and static UI, delivering immediate working evidence of the deterministic data pipeline before adding AI complexity.
  PRD ref: `prd.md > The Core Journey` (steps 1–2), `prd.md > Features and Behavior > 1. File Ingestion & Validation`, `prd.md > Features and Behavior > 2. Multimodal Analysis & Structured Cards (Card 1)`
  Spec ref: `spec.md > Stack`, `spec.md > Components > 1. Web UI Surface`, `spec.md > Components > 2. FastAPI Application`, `spec.md > Components > 3. Data Crunching & Pandas Processor`
  Build: Create `requirements.txt`, `.env.example`, `app/__init__.py`, `app/main.py`, `app/schemas.py`, `app/analyzer.py` (Pandas CSV processor), `static/index.html`, `static/styles.css`, `static/app.js`, and `static/sample_data/` (sample product image and sales CSV). Implement `/api/analyze` to calculate and return deterministic sales metrics.
  Verify (mechanical): Start FastAPI server with uvicorn, execute an automated request to `/api/analyze` with sample CSV, and verify HTTP 200 with accurate mathematical totals.
  Learner check: Open `http://127.0.0.1:8000`, click "Load Sample Data", and confirm the product preview displays and the Sales Trends card renders total revenue, units sold, and average price.
  Commit: `Bootstrap app and implement deterministic sales trends`

- [x] **2. Multimodal Gemini reasoning and 4-card results delivery**
  Becomes usable: The core multimodal kernel runs end-to-end. When the user clicks "Analyze Product", the backend passes the image and sales metrics to Gemini with strict hypothesis prompting and response schemas, validates the payload with Pydantic, and renders all 4 cards (Sales Trends, Visual Observations, Cross-Modal Hypotheses, Recommended Experiments).
  Why now: Proves the core kernel and highest technical unknown (multimodal AI integration + structured output) early in the build.
  PRD ref: `prd.md > The Core Journey` (steps 3–4), `prd.md > Features and Behavior > 2. Multimodal Analysis & Structured Cards (Cards 2, 3, 4)`
  Spec ref: `spec.md > Components > 4. Multimodal AI Engine`, `spec.md > External Services and Dependencies > Google Gemini API`, `spec.md > Decisions and Open Issues`
  Build: Implement `run_multimodal_analysis` in `app/analyzer.py` using `google-genai` and Gemini 2.5 Flash. Formulate prompt enforcing testable hypotheses rather than causal claims. Enforce response schema and validate output via Pydantic in `app/schemas.py`. Update `static/app.js` and `static/styles.css` to render all four cards.
  Verify (mechanical): Run an automated test script calling `/api/analyze` with sample image and CSV, validating HTTP 200 and confirming non-empty values across visual observations, hypotheses, and experiments.
  Learner check: Open the app, click "Load Sample Data", click "Analyze Product", and confirm that all four cards populate with grounded observations and testable hypotheses.
  Commit: `Add multimodal Gemini reasoning for visual observations and hypotheses`

- [x] **3. Input validation, error boundaries, and session reset**
  Becomes usable: The application handles invalid inputs gracefully (e.g. CSV missing required columns or invalid images trigger clear inline error banners), enforces disabled button states when inputs are missing, and provides a working "Analyze Another Product" button that resets all state.
  Why now: Closes the entire user journey and hardens edge cases so the application is completely robust and ready for recording the demo video.
  PRD ref: `prd.md > The Core Journey` (step 5), `prd.md > Features and Behavior > 3. State Reset & Session Management`, `prd.md > States and Boundaries`
  Spec ref: `spec.md > Important Failure Modes`, `spec.md > Components > 1. Web UI Surface`
  Build: Add column validation in `app/analyzer.py` returning HTTP 422 with a list of missing columns; add image validation; implement inline alert banners in `static/app.js` and `styles.css`; implement "Analyze Another Product" reset logic to restore the clean initial state.
  Verify (mechanical): Send request with missing CSV columns and verify HTTP 422 with informative error message; send invalid file type and verify HTTP 422; test reset state in frontend.
  Learner check: Try uploading a CSV with missing headers to observe the friendly error message, then load sample data, run analysis, and click "Analyze Another Product" to confirm clean reset.
  Commit: `Add input validation error handling and session reset`

## Hands-on Checkpoints

- [x] Early usable behavior explored — Slice 1 (Bootstrap & Sales Trends)
- [ ] Final kick-the-tires exploration and feedback completed

## Final Review

- [ ] Final review complete — feedback resolved and learner confirms ready to ship

## Code Tour and App Map

- [ ] Learning activity complete — guided route, focused alternative, prior practice connected, or brief recap
- [ ] Optional edit and transfer reflection addressed — offered/declined/already covered/not applicable as appropriate
- [ ] `devpost/app-map.html` generated from finished code, checked, and shown, including a project-grounded practice to reuse

Activity and evidence: [to be recorded upon completion]
Route and stops: [to be recorded upon completion]
Edit outcome: [to be recorded upon completion]
Reflection: [to be recorded upon completion]
Activity mode: [to be recorded upon completion]

## Revisions

