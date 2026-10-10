# OptriX — Evidence-Driven Market Intelligence

Discover market opportunities. Connect the evidence. Make better-informed decisions.

OptriX is a multi-source market intelligence platform that transforms web research into structured market signals, opportunity hypotheses, and traceable evidence. By combining search results across multiple Google search verticals with an explainable analysis pipeline, OptriX helps users investigate emerging markets, assess competitive landscapes, and identify areas that deserve deeper research.

Instead of relying on isolated search results, OptriX brings together information from web search, news, jobs, maps, shopping, and academic research into a unified research workflow.

> **Core idea:** Move from scattered market information to structured, evidence-backed opportunity discovery.

<p align="center">
  <a href="https://optrix-1.onrender.com/"><strong>Live Application</strong></a>
  &nbsp; • &nbsp;
  <a href="https://optrix-2.onrender.com/"><strong>Live Deployment</strong></a>
  &nbsp; • &nbsp;
  <a href="https://github.com/KrutinBhat/OptriX"><strong>Source Code</strong></a>
</p>

---

## Table of Contents

- [Platform Overview](#platform-overview)
- [The Market Research Challenge](#the-market-research-challenge)
- [Our Solution](#our-solution)
- [Platform Capabilities](#platform-capabilities)
- [Research Workflow](#research-workflow)
- [Technical Architecture](#technical-architecture)
- [Market Signals & Opportunity Scoring](#market-signals--opportunity-scoring)
- [Technology & Tools](#technology--tools)
- [Codebase Structure](#codebase-structure)
- [Local Setup & Installation](#local-setup--installation)
- [Environment Setup](#environment-setup)
- [API Endpoints & Usage](#api-endpoints--usage)
- [Live Deployment & Configuration](#live-deployment--configuration)

---

## Platform Overview

Market research frequently involves switching between search engines, news articles, job listings, supplier directories, shopping results, and academic publications. The information is fragmented, difficult to compare, and often disconnected from the conclusions drawn from it.

OptriX addresses this problem through a unified research and analysis workflow.

A user provides a market topic and geographic location. The platform collects information from multiple search sources, organizes the returned records, evaluates market activity through structured signals, and generates opportunity hypotheses with associated scores.

The resulting workspace is designed to support market exploration, evidence inspection, opportunity comparison, and transparent review of the research process.

### Who is OptriX for?

- Entrepreneurs: Explore potential market gaps and business ideas.
- Product teams: Investigate industries, technologies, and commercial activity.
- Market researchers: Consolidate information from multiple research sources.
- Students and analysts: Study market patterns using structured evidence.
- Business strategists: Identify hypotheses that warrant further validation.

OptriX is a research-support platform, not a substitute for primary market research, financial due diligence, or professional business judgment.

---

## The Market Research Challenge

Traditional market research can require manually collecting information from multiple disconnected sources.

This creates several challenges:

1. Fragmented information: Relevant market signals are distributed across different platforms.
2. Limited visibility: A single search source may not reveal the wider market landscape.
3. Difficult comparison: Raw search results are not automatically organized into comparable market dimensions.
4. Weak traceability: Conclusions can become disconnected from the records that informed them.
5. One-sided assessment: Positive indicators can overshadow competition, limitations, or contradictory findings.

OptriX brings these research activities into one structured workflow.

## Our Solution

OptriX combines three core layers:

Layer| Responsibility
Multi-source collection| Retrieve structured search results through SerpApi.
Market intelligence| Derive normalized market signals and generate opportunity hypotheses.
Evidence intelligence| Extract and organize evidence, resolve entities, and identify analytical limitations.

The result is a research environment where users can explore both what an opportunity might be and what evidence supports further investigation.

---

## Platform Capabilities

### 1. Multi-Source Market Research

OptriX uses SerpApi to retrieve structured information from six Google search verticals.

Source| Research perspective
Google Search| General market activity, manufacturers, suppliers, and relevant web pages
Google News| Industry developments and news coverage
Google Jobs| Hiring activity and professional demand indicators
Google Maps| Local businesses and geographic supplier discovery
Google Shopping| Product availability and commercial listings
Google Scholar| Academic publications and research activity

The collected records provide different perspectives on a market rather than relying on one source alone.

### 2. Market Signal Analysis

OptriX evaluates six analytical dimensions:

- Demand
- Supply gap
- Market momentum
- Technology activity
- Competition
- Geographic gap

These signals are normalized into a structured representation that can be used by the opportunity-generation pipeline.

### 3. Opportunity Discovery and Scoring

The opportunity engine evaluates market signals against predefined opportunity patterns.

Examples include:

- High-Demand Supply Gap
- Emerging Technology Opportunity
- Geographic Market Opportunity
- Market Momentum Opportunity

Each candidate receives a score on a 0–100 scale, along with information about its contributing signals.

The score is a heuristic research indicator based on configured signal weights and available data. It is not a statistically validated probability of success.

### 4. Evidence Extraction and Organization

OptriX includes an evidence-intelligence layer designed to turn normalized research results into structured evidence records.

The evidence workflow supports:

- Evidence extraction and normalization
- Duplicate identification
- Source and category grouping
- Evidence summaries and coverage measurements
- Links between evidence records and resolved entities
- Source-level traceability

This provides a foundation for investigating how the platform's research findings relate to the underlying collected records.

### 5. Entity Resolution and Exploration

Entity resolution helps organize information about organizations, products, locations, and other entities surfaced during research.

The frontend provides an Entity Explorer for navigating discovered entities and examining the resulting market landscape.

### 6. Supporting and Counter-Evidence

OptriX is designed to encourage balanced research rather than presenting every opportunity as an established conclusion.

Supporting evidence provides relevant information associated with a hypothesis. Counter-evidence analysis can identify limitations such as weak evidence coverage, concentrated sources, stale or undated information, and conflicting analytical indicators.

Counter-evidence findings are research caveats, not definitive proof that an opportunity will fail.

### 7. Evidence Graph

The evidence graph provides a visual way to explore relationships between the researched market and source categories.

Users can navigate the relationship between a market topic and its associated Search, News, Jobs, Maps, Shopping, and Scholar records.

### 8. Research Run Visibility

The research workspace includes a research summary showing key collection statistics, such as executed queries and returned results.

The purpose is to make the collection process easier to inspect and understand.

### 9. Market Intelligence Workspace

The React frontend brings the research workflow together through a user interface containing:

- Market overview and signal summaries
- Opportunity cards and scoring breakdowns
- Evidence graph and source records
- Entity exploration
- Supporting and counter-evidence views
- Research run and provenance information
- Opportunity detail pages

The presentation layer is designed to make research easier to navigate without requiring users to manually inspect every raw result.

---

## Research Workflow

A typical research run follows this workflow:

### Step 1 — Define the research scope

Enter a market topic and geographic location, such as "Drone Components" and "India".

### Step 2 — Collect information

The backend executes configured queries through SerpApi collectors for Search, News, Jobs, Maps, Shopping, and Scholar.

### Step 3 — Normalize research data

The returned source data is mapped into a common structure for downstream analysis. Collection failures are handled at the individual query/source level so that one failed request does not automatically discard successful results from other sources.

### Step 4 — Extract and organize evidence

The analysis pipeline extracts evidence records, resolves entities, and builds an evidence ledger.

### Step 5 — Derive market signals

The Signal Engine evaluates the collected records across the configured market dimensions.

### Step 6 — Generate opportunity hypotheses

The Opportunity Engine evaluates predefined patterns and applies the configured scoring weights to relevant signals.

### Step 7 — Examine evidence and limitations

The evidence-intelligence components organize source records and generate counter-evidence findings for balanced review.

### Step 8 — Explore the results

The frontend presents the research results, signals, opportunity candidates, source records, and supporting analysis in a unified workspace.

---

## Technical Architecture

OptriX uses a React frontend and a Python FastAPI backend.

flowchart TD
    A[User: Topic and Location] --> B[React + Vite Frontend]
    B --> C[FastAPI Research API]
    C --> D[SerpApi Collection Layer]

    D --> E1[Google Search]
    D --> E2[Google News]
    D --> E3[Google Jobs]
    D --> E4[Google Maps]
    D --> E5[Google Shopping]
    D --> E6[Google Scholar]

    E1 --> F[Normalized Research Data]
    E2 --> F
    E3 --> F
    E4 --> F
    E5 --> F
    E6 --> F

    F --> G[Evidence Extraction]
    G --> H[Entity Resolution]
    H --> I[Evidence Ledger]

    I --> J[Signal Engine]
    J --> K[Opportunity Engine]
    I --> L[Counter-Evidence Analysis]
    K --> M[Opportunity Scoring]

    M --> N[Structured Research Response]
    L --> N
    I --> N
    H --> N

    N --> B

### Architectural responsibilities

Component| Responsibility
React frontend| Research input, navigation, dashboards, and result visualization
Vite| Frontend development server and production bundling
FastAPI| HTTP API, request handling, and research orchestration
SerpApi collectors| Retrieve source-specific search results
Evidence Extractor| Convert collected records into structured evidence
Entity Resolver| Identify and organize entities across research data
Evidence Engine| Build a traceable evidence ledger and evidence summaries
Signal Engine| Calculate normalized market signals
Opportunity Engine| Generate opportunity hypotheses from market patterns
Opportunity Scorer| Apply configured scoring weights
Counter-Evidence Engine| Identify research limitations and potential counter-indicators

The architecture separates data collection, analytical processing, and user-interface presentation, making the system easier to inspect and extend.

---

## Market Signals & Opportunity Scoring

OptriX currently defines six market signal dimensions.

Signal| Intended interpretation
Demand| Activity across sources associated with market interest and professional or commercial demand
Supply gap| A heuristic indicator of potential differences between demand-related activity and supplier availability
Momentum| A heuristic indicator derived from configured market activity signals
Technology| Research and technology-related activity
Competition| Competitive activity and the presence of alternative providers
Geographic gap| Potential regional differences in market activity and supplier discovery

### Opportunity scoring

The Opportunity Scorer uses configurable weights for different opportunity patterns.

For example, the "High-Demand Supply Gap" pattern uses the following configured weights:

Signal| Weight
Demand| 40%
Supply gap| 40%
Competition| 20%

Positive signals contribute to the opportunity score, while competition is treated as a negative factor in the scoring logic.

Different patterns use different weights, allowing the engine to evaluate opportunity hypotheses according to their intended signal combinations.

Interpretation note: These scores are heuristic and depend on the available search results and configured normalization baselines. They should not be interpreted as validated market-demand estimates, proof of unmet demand, or guaranteed commercial outcomes. The quality of a result depends on source coverage, query relevance, data quality, and subsequent human validation.

---

## Technology & Tools

### Frontend

Technology| Purpose
React| Component-based user interface
Vite| Frontend development and build tooling
JavaScript (ES modules)| Frontend application logic
Lucide React| Interface icons
CSS| Layout, styling, and responsive presentation

### Backend

Technology| Purpose
Python| Research orchestration and analysis
FastAPI| REST API
Uvicorn| ASGI application server
Requests| HTTP communication with SerpApi
python-dotenv| Environment variable loading
Pydantic| Request validation through FastAPI schemas

### Data and intelligence

- SerpApi for structured search data retrieval
- Custom source collectors for six Google search verticals
- Custom market signal and opportunity scoring engines
- Evidence extraction and evidence-ledger components
- Entity resolution
- Counter-evidence analysis

## Live Deployment & Configuration

The application has been deployed using Render. Deployment configuration, service availability, and environment variables should be verified against the current deployment settings.

---

## Codebase Structure

The following is a simplified overview of the main application modules.

OptriX/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── routes/
│   │   └── research.py
│   ├── schemas/
│   │   └── models.py
│   ├── serpapi/
│   │   ├── client.py
│   │   ├── search.py
│   │   ├── news.py
│   │   ├── jobs.py
│   │   ├── maps.py
│   │   ├── shopping.py
│   │   └── scholar.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── signal_engine.py
│   │   ├── opportunity_engine.py
│   │   └── scoring.py
│   └── ai/
│       ├── extractor.py
│       ├── entity_resolution.py
│       ├── evidence_engine.py
│       └── counter_evidence.py
│
├── frontend/
│   ├── package.json
│   ├── index.html
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── index.css
│       ├── components/
│       ├── pages/
│       ├── services/
│       └── data/
│
└── README.md

This diagram highlights the principal modules; it is not intended to enumerate every file in the repository.

---

## Local Setup & Installation

Follow these steps to run OptriX locally.

### Prerequisites

Install the following:

- Python 3.10 or newer
- Node.js and npm
- Git
- A SerpApi account and API key

Python 3.10+ is recommended for the current backend code, which uses modern Python typing and dataclass features.

1. Clone the repository

git clone https://github.com/KrutinBhat/OptriX.git
cd OptriX

2. Configure the backend

Create and activate a virtual environment.

Windows — Command Prompt

cd backend
python -m venv .venv
.venv\Scripts\activate

Windows — PowerShell

cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1

macOS / Linux

cd backend
python3 -m venv .venv
source .venv/bin/activate

Install the Python dependencies:

python -m pip install --upgrade pip
pip install -r requirements.txt

3. Configure the SerpApi API key

Create a ".env" file inside the "backend/" directory:

SERPAPI_API_KEY=your_serpapi_api_key

Replace the placeholder with your own API key.

Do not commit the ".env" file to GitHub or expose the API key in frontend code.

4. Start the backend

From the "backend/" directory, with the virtual environment activated:

python -m uvicorn main:app --reload

The API should be available at:

http://127.0.0.1:8000

Health endpoint:

http://127.0.0.1:8000/health

Interactive API documentation:

http://127.0.0.1:8000/docs

5. Configure the frontend

Open a second terminal:

cd OptriX/frontend
npm install

Create a "frontend/.env" file:

VITE_API_BASE_URL=http://127.0.0.1:8000

This variable tells the frontend where to send research requests.

Vite exposes "VITE_*" variables to client-side code, so never put API secrets in frontend environment variables.

6. Start the frontend

From the "frontend/" directory:

npm run dev

Open the local URL printed by Vite, typically:

http://localhost:5173

Enter a market topic and location, then run a research query.

---

## Environment Setup

Variable| Location| Required| Description
"SERPAPI_API_KEY"| "backend/.env"| Yes for live collection| Authenticates requests to SerpApi
"VITE_API_BASE_URL"| "frontend/.env"| Recommended| Base URL for the FastAPI backend

Example local configuration:

"backend/.env"

SERPAPI_API_KEY=your_serpapi_api_key

"frontend/.env"

VITE_API_BASE_URL=http://127.0.0.1:8000

Keep credentials private. If a key is accidentally committed, revoke or rotate it with the provider rather than relying only on deleting it from the latest commit.

---

## API Endpoints & Usage

### Health Check

"GET /health"

Checks whether the backend application is responding.

Example:

curl http://127.0.0.1:8000/health

Expected response:

{
  "status": "ok"
}

### Run Market Research

"POST /research"

Starts a research run using the supplied topic and location.

Request:

{
  "topic": "Drone Components",
  "location": "India"
}

Example:

curl -X POST "http://127.0.0.1:8000/research" \
  -H "Content-Type: application/json" \
  -d "{\"topic\":\"Drone Components\",\"location\":\"India\"}"

The response contains the research topic and location, collected source data, structured market signals, opportunity candidates, and research statistics.

The source-specific data includes the configured Google Search, News, Jobs, Maps, Shopping, and Scholar collectors.

Example response shape:

{
  "topic": "Drone Components",
  "location": "India",
  "google_search": {
    "source": "google_search",
    "queries_executed": 2,
    "results": []
  },
  "google_news": {
    "source": "google_news",
    "queries_executed": 1,
    "results": []
  },
  "signals": {
    "demand": {},
    "supply_gap": {},
    "momentum": {},
    "technology": {},
    "competition": {},
    "geographic_gap": {}
  },
  "opportunities": [],
  "research_stats": {
    "total_queries": 7,
    "total_results": 0
  }
}

The example above illustrates the response structure, not a guaranteed live response. Actual signal objects, source results, and opportunity candidates depend on the research request and the data returned by the collectors. Some source requests may fail independently.

---

## Live Deployment & Configuration

OptriX has been deployed using Render, with separate frontend and backend services in the existing deployment setup.

Live application links:

- "OptriX — Frontend deployment" (https://optrix-1.onrender.com/)
- "OptriX — Additional deployment" (https://optrix-2.onrender.com)

### Deployment checklist

Before deploying a new version:

1. Install frontend dependencies and verify the production build with "npm run build".
2. Install backend dependencies from "backend/requirements.txt".
3. Configure "SERPAPI_API_KEY" as a backend environment variable in Render.
4. Configure "VITE_API_BASE_URL" to point to the deployed backend API.
5. Ensure backend CORS settings allow the actual frontend origin.
6. Test "GET /health".
7. Run a real "POST /research" request.
8. Verify that the frontend renders successful results and handles failed source requests.
9. Check logs for API errors, missing configuration, and failed source requests.
