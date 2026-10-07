---
doc: prd
status: approved
---

# ProductLens AI — Product Requirements Document

A lightweight, professional product-audit web application that enables small e-commerce sellers to analyze a product image alongside historical sales data, surfacing grounded cross-modal hypotheses and testable business experiments.
- **Source:** `scope.md > ProductLens AI (Multimodal Product & Sales Auditor)`

## The Core Journey
1. **Arrival & Initial View:** The user lands on a clean, single-page interface with a top-to-bottom layout. The header introduces the tool. The inputs area displays two upload zones (Product Image and Sales CSV), a prominent "Load Sample Data" action, and an "Analyze Product" button (initially disabled). The results section is hidden.
2. **Input Selection:** The user either uploads their own product image (PNG/JPG) and sales CSV, or clicks "Load Sample Data". Upon selecting an image, a live visual preview displays immediately. Once both inputs are present, the "Analyze Product" button becomes enabled.
3. **Triggering Analysis:** The user clicks "Analyze Product". The interface transitions into a loading state ("Analyzing your product and sales data...").
4. **Reviewing Results:** The results area reveals four distinct, structured cards beneath the inputs. The uploaded product image remains visible alongside or above the cards to provide visual context:
   - **Card 1: Sales Data Trends** (Key metrics & bulleted time trends).
   - **Card 2: Visual Observations** (Objective product and presentation features).
   - **Card 3: Cross-Modal Hypotheses** (Hypotheses linking image traits with sales numbers).
   - **Card 4: Recommended Experiments** (2–3 concrete, testable actions with measurable targets).
5. **Resetting:** The user clicks "Analyze Another Product", which clears the inputs, image preview, and results, returning to the fresh initial state.

## Screens and Layout
- **Single-Page Application (SPA):**
  - **Header:** Title, subtitle explaining the tool's purpose.
  - **Input Panel:**
    - Left/Top box: Product Image dropzone with instant image preview.
    - Right/Top box: Sales CSV dropzone with file name indicator and schema check.
    - Quick Action: "Load Sample Data" button for immediate demonstration.
    - Primary Action: "Analyze Product" button centered below the inputs.
  - **Status / Loading Banner:** Appears during analysis with clear progress text.
  - **Results Section:**
    - Persistent Product Image Preview (anchored near results).
    - 4-Card Responsive Grid/Stack:
      1. *Sales Data Trends Card*
      2. *Visual Observations Card*
      3. *Cross-Modal Hypotheses Card* (highlighted as core kernel)
      4. *Recommended Experiments Card*
  - **Footer / Reset Bar:** "Analyze Another Product" button to clear state.

## Look and Feel
- **Theme:** Crisp, modern light theme.
- **Color Palette:**
  - Background: Clean off-white / light neutral (`#F8FAFC` or `#F1F5F9`).
  - Cards & Panels: Pure white (`#FFFFFF`) with subtle border lines (`#E2E8F0`) and soft, clean shadows.
  - Primary Accent: Deep indigo / royal blue (`#1E3A8A` / `#2563EB`) for primary buttons, headers, and key focal points.
  - Supporting Accent: Subtle emerald green (`#059669` / `#10B981`) for positive trend metrics and action item tags.
- **Typography & Styling:** Clean sans-serif typography (e.g., Inter), high contrast, disciplined visual hierarchy.
- **Aesthetic Boundaries:** Professional analytics tool aesthetic; strictly avoid generic dark AI neon glow, excessive gradients, or generic chatbot layouts.

## Features and Behavior

### 1. File Ingestion & Validation
- **Source:** `scope.md > The Core Loop`, `scope.md > The POC Boundary`
- **Behavior:**
  - Accepts image files (`.png`, `.jpg`, `.jpeg`, `.webp`).
  - Accepts CSV files containing required columns: `date` (or `time`), `product`, `price`, `units_sold`, `revenue`.
  - "Load Sample Data" automatically populates a pre-bundled sample product photo and matching realistic sales CSV.
- **Acceptance Criteria:**
  - [ ] Selecting an image immediately displays an image thumbnail preview.
  - [ ] If an uploaded CSV lacks the required columns (`date`, `product`, `price`, `units_sold`, `revenue`), an inline error specifies the missing columns.
  - [ ] The "Analyze Product" button remains disabled until both valid image and valid CSV data are present.
  - [ ] Clicking "Load Sample Data" loads sample assets and enables "Analyze Product" without file dialog prompts.

### 2. Multimodal Analysis & Structured Cards
- **Source:** `scope.md > The Unique Kernel`, `scope.md > What "Working" Looks Like`
- **Behavior:**
  - While processing, displays: "Analyzing your product and sales data...".
  - Generates four distinct cards with consistent structure:
    - **Sales Data Trends:** Displays calculated metrics (Total Revenue, Total Units Sold, Average Price, Overall Trend Direction) followed by 2–3 concise bullet points summarizing trajectory over time.
    - **Visual Observations:** Lists observable attributes (product prominence, packaging clarity, color palette, perceived tier/quality), clearly identified as observations.
    - **Cross-Modal Hypotheses:** Presents 2–3 grounded hypotheses connecting specific image elements to sales data patterns. Framed strictly as hypotheses to investigate, not proven causal statements.
    - **Recommended Experiments:** Presents 2–3 concrete, testable experiments (e.g. testing new packaging photography, testing pricing adjustments). Each experiment states: (a) what to change, and (b) what metric to measure.
- **Acceptance Criteria:**
  - [ ] Clicking "Analyze Product" shows the loading indicator and disables the button during execution.
  - [ ] Results populate all four cards with formatted text, bullets, and badge metrics.
  - [ ] The uploaded image remains visible alongside or above the analysis cards.
  - [ ] Content in the Hypotheses card explicitly references both visual cues and numerical metrics.

### 3. State Reset & Session Management
- **Source:** `scope.md > The Core Loop`
- **Behavior:**
  - Provides a visible "Analyze Another Product" / "Start New Analysis" button when results are displayed.
  - Resets all inputs, previews, errors, and results back to the blank arrival state.
- **Acceptance Criteria:**
  - [ ] Clicking "Analyze Another Product" clears inputs, preview, and results, re-disabling the Analyze button.

## States and Boundaries

- **First Use / Empty State:** Fresh page with empty upload boxes, disabled "Analyze Product" button, visible "Load Sample Data" button, and hidden results section.
- **Loaded State:** Image preview active, CSV loaded badge showing filename and row count, "Analyze Product" button active.
- **Loading State:** Disabled buttons, loading message visible ("Analyzing your product and sales data...").
- **Success State:** Full 4-card results displayed, image preview visible, "Analyze Another Product" action available.
- **Error States:**
  - *Missing file:* Analyze button stays disabled; helpful tooltip/label prompts for the missing item.
  - *Invalid CSV schema:* Red error banner detailing required columns (`date`, `product`, `price`, `units_sold`, `revenue`).
  - *AI service error:* Friendly error banner with a "Retry" button without losing uploaded inputs.
- **Persistence Boundary:** In-memory / browser session only; refreshing or resetting clears data. No databases or user accounts.

## Product Decisions
- **Single-page vertical flow:** Keeps the demonstration intuitive and easy to present in a 1-minute video demo without multi-tab friction.
- **Disabled button until valid inputs:** Prevents invalid submissions before they happen.
- **Hypotheses vs. Causal claims:** Language strictly maintained as exploratory hypotheses to maintain data integrity and avoid false marketing claims.
- **Pre-bundled sample data:** Allows the learner to run instant demo tests without having to prepare custom CSV files on the fly.
- **Light theme with deep indigo and emerald:** Fits a serious, high-trust analytics tool aesthetic rather than a flashy AI toy.

## What We're Building
- Single-page responsive web application.
- Dual-input ingestion (Product Image + Sales CSV) with live preview and "Load Sample Data".
- Client-side CSV validation (checking for required headers).
- Multimodal AI processing pipeline yielding structured outputs.
- 4-card results display (Sales Trends, Visual Observations, Cross-Modal Hypotheses, Recommended Experiments).
- Error handling and one-click reset.

## Deferred From the POC
- Multi-product comparative analysis (deferred to keep build under 2–4 hours).
- Persistent audit history / database storage (not needed to prove core multimodal value).
- Export to PDF / shareable link (nice-to-have, deferred).

## Non-Goals
- Full business intelligence platform or inventory management.
- Live Shopify/Amazon store integration.
- Conversion rate or web traffic attribution analysis (unsupported by basic sales CSVs).
- User authentication, payments, or team workspaces.

## Open Questions
- None blocking spec approval; technical architecture details (framework, multimodal API integration, CSV parsing library) will be defined in `4-spec`.
