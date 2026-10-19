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
- [x] Final kick-the-tires exploration and feedback completed

## Final Review

- [x] Final review complete — feedback resolved and learner confirms ready to ship

## Code Tour and App Map

- [x] Learning activity complete — guided route, focused alternative, prior practice connected, or brief recap
- [x] Optional edit and transfer reflection addressed — offered/declined/already covered/not applicable as appropriate
- [x] `devpost/app-map.html` generated from finished code, checked, and shown, including a project-grounded practice to reuse

Activity and evidence: Brief evidence-based recap and standalone architecture guide generated. Verified end-to-end user journey: sample data loading, image preview, CSV validation, 4 structured cards, inline error handling, and clean session reset.
Route and stops: Mapped 3 key stops in devpost/app-map.html: (1) static/app.js (client ingestion and header verification), (2) app/analyzer.py (deterministic Pandas calculations), and (3) app/analyzer.py (multimodal Gemini reasoning with Pydantic validation).
Edit outcome: Declined / not applicable — learner confirmed all behavior matches expectations and requested zero additional scope or edits.
Reflection: Offered takeaway connecting deterministic data processing in Pandas with qualitative multimodal synthesis in Gemini; no further questions raised.
Activity mode: recap

## Revisions

- Slice 2: Added resilient model fallback across `gemini-3.1-flash-lite`, `gemini-3.8-flash`, and `gemini-3-flash-preview` to prevent transient 503 capacity spikes. Constrained prompt and schema so all metrics strictly reference available CSV fields unless labeled as requiring external analytics tracking.
- Slice 3: Added client-side header verification in `static/app.js` to disable the Analyze Product button immediately when an invalid CSV is selected, complementing backend HTTP 422 validation.

- Pre-ship (6-ship): Average price now computed as total revenue ÷ total units (was mean of the price column). Added deterministic price-change analysis (`describe_price_changes`) comparing average weekly units around each price change and flagging declines that began before it; fixed closing-period bullet to show actual start/end prices. Tightened hypothesis framing: required "Factor worth investigating:" prefix (enforced in code), banned causal wording, and added a `how_to_test` field rendered in Card 3. Added `README.md` with setup/run steps and cache-busting asset versions in `index.html`.
- Pre-ship (6-ship, round 2): Lowered Gemini temperature to 0.2 for steadier repeat runs; accepted common store-export header variants (e.g. `Qty`, `Total Sales`, `Order Date`) in both backend and client checks, and stripped currency symbols/thousands separators from numbers; added a fixed "What this analysis can't see" note under Card 3; added a limited-data warning (fewer than 4 periods) that also tells Gemini to keep hypotheses tentative.
- Pre-ship (6-ship, round 3): Added optional `views` and `returns` CSV columns (with header aliases). Pandas computes conversion rate and return rate, compares halves, and emits a deterministic funnel signal (steady views + falling conversion points to the listing; falling views points to visibility). Card 1 shows Conversion Rate and Return Rate tiles only when present; the Gemini prompt lists tracked fields dynamically and adds funnel/returns reasoning rules. Sample CSV now includes both columns. Scope updated to record the addition.
