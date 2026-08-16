You're very welcome — genuinely glad it's all working now. Here's a complete README, ready to drop in as `README.md` at your repo root.

```markdown
# 🔍 AI Software Bug Prediction & Code Quality Platform

**PS-038 | Software Engineering × Artificial Intelligence**

A continuous quality layer around the Git workflow — predicting bug risk, detecting security issues, identifying code smells, and enabling AI-assisted repair, all with the developer in control.

**Team haritadesara1** — Harit Adesara · Fenil Koshti · Kinara Patel

🔗 Live repo: [github.com/Kinara2020/bug-predict-platform](https://github.com/Kinara2020/bug-predict-platform)

---

## The Problem

Bugs are often discovered after deployment — when fixes are slower, costlier, and disruptive. Traditional workflows rely on manual code review, testing, and CI/CD pipelines, but many issues still surface late in the development lifecycle, creating maintenance overhead, security risk, and delayed releases.

## Our Solution

An AI-powered platform that acts as a continuous quality layer around the Git workflow. Every push can trigger automatic analysis — predicting bug risk, scanning for security vulnerabilities, and surfacing code smells — before problems ever reach production.

**Core idea: Predict → Detect → Decide → Repair**

---

## Workflow

```
┌─────────────┐
│  Developer  │
│    Push     │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   GitHub Webhook     │  (signature-verified)
└──────┬───────────────┘
       │
       ▼
┌─────────────────────┐
│   Backend Server     │  FastAPI + LangGraph
└──────┬───────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│         ANALYZE (LangGraph)          │
│                                       │
│  Fetch Modified Files                │
│  (GitHub Contents API — no clone)    │
│              │                       │
│              ▼                       │
│  ┌─────────┬─────────┬────────────┐  │
│  │  Radon  │ Bandit  │  Semgrep   │  │
│  │Complexity│Security │  Patterns  │  │
│  └────┬────┴────┬────┴─────┬──────┘  │
│       │         │          │         │
│       └────┬────┴──────────┘         │
│            ▼                         │
│    ML Risk Scoring                   │
│  (GradientBoostingClassifier)        │
│            │                         │
│            ▼                         │
│    Gemini Contextual Review          │
│  (code smells, qualitative bugs)     │
│            │                         │
│            ▼                         │
│      SCAN_STORE (results)            │
└──────┬────────────────────────────────┘
       │
       ▼
┌─────────────────────┐
│  React Dashboard     │
│  Score · Charts ·    │
│  Security Issues     │
└──────┬───────────────┘
       │
       ▼
┌─────────────────────────────┐
│      Developer Decides       │
│                               │
│  Reject │ Approve │ Suggest  │
│                    Fix &      │
│                    Approve     │
└──────┬────────────────────────┘
       │  (Suggest Fix & Approve)
       ▼
┌─────────────────────────────┐
│      fix_agent.py            │
│                               │
│  1. Generate patch (Gemini)  │
│  2. Self-verify fix (SAFE/   │
│     UNSAFE check)             │
│  3. Create AI_FIX-<hash>     │
│     branch                    │
│  4. Commit only approved,     │
│     verified fixes            │
└──────┬────────────────────────┘
       │
       ▼
┌─────────────────────┐
│   GitHub Branch      │
│   AI_FIX-xxxxxxxx     │
│   (never touches      │
│    main directly)     │
└──────────────────────┘
```

---

## How It Works — Step by Step

**1. Ingest**
A developer pushes code to GitHub. A webhook (HMAC signature-verified) notifies the backend instantly. For manual testing, the dashboard also supports triggering a scan directly by entering an owner/repo/branch.

**2. Fetch**
Only the modified files are pulled via the GitHub Contents API — no full repository clone, keeping the workflow lightweight and fast.

**3. Analyze — Multi-Signal Detection**
- **Radon** computes code complexity and maintainability metrics per file
- **Bandit** (Python) and **Semgrep** (multi-language) scan for security vulnerabilities and known bad patterns
- A **trained ML classifier** (GradientBoostingClassifier) converts complexity metrics into a bug-risk probability score per file
- **Gemini** performs contextual review on the highest-risk files — catching code smells and issues that pattern-matching alone would miss

**4. Score**
All signals combine into a single 0–100 Overall Quality Score, plus a per-file risk label (low/medium/high).

**5. Decide — Human in the Loop**
The developer reviews findings on the dashboard and chooses:
- **Reject** — dismiss the finding
- **Approve** — accept as-is
- **Suggest Fix & Approve** — select specific flagged files for AI repair (unselected files are never touched)

**6. Repair**
For approved fixes, `fix_agent.py`:
1. Generates a precise patch via Gemini, scoped only to the described issue
2. Runs a self-verification pass — the agent checks its own fix for safety before committing anything
3. Creates an isolated `AI_FIX-<hash>` branch (never touches `main` directly)
4. Commits only fixes that pass verification; unsafe fixes are skipped and reported back

**7. Review**
The dashboard displays the new branch name and the actual before/after code diff, so the team has a clear, traceable place to review AI-generated changes before merging.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph (StateGraph) |
| Backend | FastAPI, PyGithub |
| Bug Prediction | Radon (metrics) + GradientBoostingClassifier (scikit-learn) |
| Security Analysis | Bandit + Semgrep |
| AI Review & Repair | Google Gemini |
| Frontend | React, Recharts |
| Integration | GitHub Webhooks, GitHub Contents API |

---

## Model Notes

The bug-risk classifier is trained on a modeled dataset reflecting documented complexity–defect correlations from software engineering research (loc, cyclomatic complexity, maintainability index, comment ratio → defect probability). Current evaluation: Accuracy ~0.83, F1 ~0.81, AUC-ROC ~0.64. The full training pipeline (`backend/models/train_model.py`) is designed to be re-pointed at a larger real-world labeled defect dataset (e.g. NASA PROMISE) for future accuracy improvements — this is on our roadmap, not a limitation of the architecture.

---

## Why This, Not Just SonarQube or CodeQL

Existing tools are strong at individual stages of detection. This platform unifies them into one workflow:

- Combines complexity, security, pattern, and contextual AI signals into a single risk-oriented finding
- Lets developers Reject / Approve / Suggest Fix — decision stays human-controlled
- Generates an isolated, traceable branch for any approved AI remediation
- Lightweight — API-based file retrieval, no full repository clone

Not another static analyzer — a continuous decision-and-remediation layer around the Git workflow.

---

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- A GitHub Personal Access Token (classic, `repo` scope)
- A Google Gemini API key

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt

# Create .env from .env.example and fill in real values:
# GITHUB_TOKEN=your_token
# GOOGLE_API_KEY=your_key
# GITHUB_WEBHOOK_SECRET=your_secret

python models/train_model.py    # trains and saves the ML model
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173`

### Webhook (optional, for live push-triggered scans)
```bash
ngrok http 8000
```
Add the forwarding URL + `/webhook` as a GitHub webhook (Settings → Webhooks), content type `application/json`, matching secret.

---

## Roadmap

- **Multi-language analysis** — expand Semgrep rule packs and language-specific analyzers
- **PR feedback loops** — automated inline pull-request comments
- **Historical intelligence** — use bug trends to refine ML risk scoring on a larger real-world dataset
- **Team authentication** — GitHub OAuth login, per-user decision history and audit trail

---

## Project Structure
```
backend/
├── main.py                  # FastAPI app, webhook + decision endpoints
├── graph.py                 # LangGraph pipeline definition
├── state.py                 # Shared state schema
├── fix_agent.py             # AI repair agent (generate → verify → commit)
├── github_utils.py          # GitHub Contents API integration
├── analysis/
│   ├── static_analysis.py   # Bandit
│   ├── semgrep_scan.py      # Semgrep
│   ├── ml_bug_predictor.py  # Radon + ML risk scoring
│   └── llm_review.py        # Gemini contextual review
└── models/
    ├── train_model.py       # Model training script
    └── bug_risk_model.pkl   # Trained classifier

frontend/
└── src/
    └── App.jsx               # Dashboard UI


