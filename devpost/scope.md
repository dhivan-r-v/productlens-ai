---
doc: scope
status: approved
---

# ProductLens AI (Multimodal Product & Sales Auditor)

A lightweight AI application that analyzes a product image alongside historical sales data to surface cross-modal hypotheses, factors worth investigating, and actionable next steps for e-commerce sellers.

## The Unique Kernel
The AI doesn't just analyze numbers and images separately; it reasons across both. It identifies relevant visual characteristics of the product (e.g., packaging clarity, design aesthetics, perceived product tier) and connects them with sales trends (units sold, revenue trajectories, price points over time) to formulate grounded hypotheses and factors worth investigating—carefully avoiding unverified causal claims.

## Who It's For
A small e-commerce or retail business owner who manages their own inventory and sales.
- **Goal:** Understand what factors might be influencing product performance and what specific, testable changes (in pricing, presentation, or product photography) are worth trying.
- **Current alternative:** Staring at isolated spreadsheets and guessing, or paying for expensive agency audits.

## The Core Loop
1. Open the web app.
2. Upload a product photo and a small sales CSV (product, price, units sold, revenue over time), or click "Load Sample Data".
3. Click **Analyze Product**.
4. Review the structured output:
   - **Sales Data Trends:** Numerical summaries and trajectory (units, revenue, price trends over time).
   - **Visual Observations:** Key visual features, packaging, and presentation factors observed in the image.
   - **Cross-Modal Hypotheses:** Potential factors and relationships worth investigating that connect visual traits with sales patterns (stated clearly as testable hypotheses, not causal certainties).
   - **Actionable Next Steps:** 2–3 concrete experiments the owner could run (e.g., A/B testing product photography, testing pricing tiers).

## Inspiration & Identity
- **Tone:** Pragmatic, analytical, transparent about hypotheses vs. facts.
- **Mood:** Professional analytics tool designed for small merchants—clean, digestible visual breakdown without clutter.

## Why This Matters to the Learner
Combines past professional experience as a Data Analyst providing business insights with a new curiosity about deep learning, CNNs, and multimodal models. It represents a hands-on milestone: moving from isolated ML theory to building an end-to-end, working multimodal AI application.

## What "Working" Looks Like
In a 1-minute demo video:
The user opens the app, uploads a product image and a sales CSV (or selects sample data), and clicks **Analyze Product**. Within seconds, the screen presents a clean card-by-card breakdown that clearly separates:
1. What the numerical data shows (sales trends over time),
2. What the image suggests (visual characteristics),
3. Cross-modal hypotheses connecting visual cues with sales numbers for further investigation,
4. Concrete, realistic next experiments grounded in the inputs (e.g., photography or pricing experiments).

## The POC Boundary
- **In Scope:**
  - Single-product analysis flow.
  - Image upload (JPG/PNG) + small sales CSV upload (product, price, units sold, revenue over time) with pre-bundled sample dataset for instant testing.
  - Multimodal LLM integration that produces structured, separated outputs (Data Trends, Visual Features, Cross-Modal Hypotheses, Actionable Recommendations).
  - Clean, responsive single-page web interface.

## Later
- Multi-product comparison (comparing top-seller vs. underperforming product side-by-side).
- Direct e-commerce store integration (Shopify, Amazon, WooCommerce API).
- Longitudinal tracking and automated email alerts.

## Explicitly Cut
- Full ERP or business intelligence platform (too broad for a 2–4 hour PoC).
- Conversion rate or traffic attribution modeling (out of scope unless click/traffic data is explicitly tracked).
- Copywriting or listing text optimization (focus remains squarely on visual presentation and sales metrics).
- User authentication and accounts (adds friction without testing the core multimodal kernel).
- Live payment gateways or billing tiers.
- Real database setup (local session state is sufficient).
