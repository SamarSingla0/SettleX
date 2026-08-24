# 🏦 SettleX

### AI-Powered Payment Reconciliation & Settlement Intelligence

> **SettleX** is an AI-powered finance operations platform that automatically reconciles payment, gateway, and bank ledgers, investigates complex settlement exceptions using a LangGraph agent powered by Google Gemini, and escalates unresolved cases for human review.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/TypeScript-5.x-3178C6?style=for-the-badge&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/LangGraph-Agent-7C3AED?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Gemini-AI-4285F4?style=for-the-badge&logo=google&logoColor=white" />
</p>

<p align="center">
  <strong>Deterministic finance logic + AI-powered exception investigation</strong>
</p>

---

## 🎯 What is SettleX?

Payment reconciliation is a critical but highly manual finance operation.

A single payment can pass through multiple financial systems:

```text
Customer Payment
       ↓
Payment Gateway
       ↓
Expected Settlement
       ↓
Bank Settlement
```

These records don't always match.

There may be:

- Amount discrepancies
- Missing settlements
- Duplicate transactions
- Delayed settlements
- Gateway fees
- Entity/name variations
- Missing ledger records

SettleX automates the reconciliation process and uses AI only where reasoning is actually required.

### The core principle

> **Use deterministic code for financial calculations. Use AI for investigation and reasoning.**

This prevents the LLM from becoming the source of truth for financial arithmetic.

---

# 🚀 Key Features

### ⚡ Deterministic-First Reconciliation

Straightforward transactions are resolved using strict Python logic and exact `Decimal` arithmetic without unnecessary LLM calls.

- Payment ↔ Gateway matching
- Gateway ↔ Bank matching
- Expected settlement calculation
- Fee and charge calculations
- Settlement-date validation
- Duplicate detection
- Difference analysis

---

### 🤖 AI-Powered Exception Investigation

Complex exceptions are routed to a **LangGraph investigation agent powered by Google Gemini**.

The agent can use controlled tools such as:

```text
find_payment()
find_gateway_transaction()
find_fee_explanation()
match_customer_entity()
check_duplicate_transactions()
calculate_expected_amount()
search_similar_transactions()
```

The agent gathers verified evidence before making a decision.

---

### 🛡️ Zero Financial Hallucination Architecture

LLMs are **not trusted with financial arithmetic**.

All financial calculations are performed using deterministic backend logic and exact `Decimal` arithmetic.

The AI receives verified data from database tools and returns structured results through a Pydantic schema.

If sufficient evidence does not exist:

```text
UNRESOLVED
      ↓
Human Review Required
```

The agent is designed to **escalate instead of guessing**.

---

### 📊 Ground-Truth Evaluation

SettleX includes a synthetic benchmark with known expected outcomes.

Current benchmark:

| Metric | Result |
|---|---:|
| Match Rate | **80.0%** |
| System Accuracy | **93.3%** |
| Precision | **94.1%** |
| Recall | **91.8%** |
| Entity Variations Resolved | **20 / 20** |
| Documented Fee Discrepancies | **10 / 10** |

This allows the AI system to be evaluated objectively instead of relying only on demo examples.

---

### 🔍 Full Audit Trail

Every investigation is traceable.

For each transaction, SettleX can record:

```text
Transaction
    ↓
Tool Calls
    ↓
Database Evidence
    ↓
Agent Investigation
    ↓
Decision
    ↓
Confidence
    ↓
Recommended Action
```

This makes the system easier to inspect, debug, and audit.

---

# 🖥️ Product Showcase

## Dashboard

<p align="center">
  <img src="docs/images/dashboard.png" width="900" alt="SettleX Dashboard" />
</p>

The dashboard provides a high-level view of:

- Total transactions
- Matched transactions
- Exceptions
- Unresolved cases
- Match rate
- Accuracy
- Precision
- Recall

---

## Transaction Reconciliation

<p align="center">
  <img src="docs/images/reconciliation.png" width="900" alt="SettleX Reconciliation Dashboard" />
</p>

SettleX compares payment, gateway, and bank records to determine whether a settlement can be automatically reconciled.

---

## AI Exception Investigation

<p align="center">
  <img src="docs/images/investigation.png" width="900" alt="SettleX AI Investigation" />
</p>

For complex exceptions, the LangGraph agent investigates the transaction using controlled tools and verified database evidence.

---

## Exception Audit Trail

<p align="center">
  <img src="docs/images/audit-trail.png" width="900" alt="SettleX Audit Trail" />
</p>

Every investigation step is recorded so users can understand how the final decision was reached.

---

## Evaluation Dashboard

<p align="center">
  <img src="docs/images/evaluation.png" width="900" alt="SettleX Evaluation Dashboard" />
</p>

The evaluation dashboard compares system decisions against the known ground truth.

---

# 🏗️ System Architecture

<p align="center">
  <img src="docs/images/architecture.png" width="1000" alt="SettleX System Architecture" />
</p>

### Architecture Flow

```text
                         ┌─────────────────────┐
                         │     React Frontend  │
                         │ TypeScript + Tailwind│
                         └──────────┬──────────┘
                                    │
                                    │ REST API
                                    ↓
                         ┌─────────────────────┐
                         │   Django Backend    │
                         │      + DRF          │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┴────────────────┐
                    ↓                                ↓
          ┌────────────────────┐          ┌──────────────────┐
          │ Reconciliation     │          │ LangGraph Agent  │
          │ Engine             │          │                  │
          └─────────┬──────────┘          └────────┬─────────┘
                    │                              │
                    │                              ↓
                    │                       ┌─────────────┐
                    │                       │   Gemini    │
                    │                       └──────┬──────┘
                    │                              │
                    └──────────────┬───────────────┘
                                   ↓
                         ┌─────────────────────┐
                         │   SQLite / Database │
                         └─────────────────────┘
```

---

# 🧠 AI Agent Workflow

The AI investigation workflow is orchestrated using LangGraph.

```text
START
  │
  ↓
Load Exception
  │
  ↓
Analyze Transaction
  │
  ↓
Call Investigation Tools
  │
  ├── Find Payment
  ├── Find Gateway Transaction
  ├── Check Fees
  ├── Check Duplicates
  ├── Match Customer Entity
  └── Search Similar Transactions
  │
  ↓
Analyze Evidence
  │
  ├───────────────┐
  ↓               ↓
RESOLVED       UNRESOLVED
  │               │
  ↓               ↓
Explain         Escalate
Reason          to Human
  │               │
  └───────┬───────┘
          ↓
       Audit Log
```

---

# 🔐 Financial Safety Architecture

SettleX follows a **deterministic-first AI architecture**.

### The LLM does NOT:

- Calculate financial balances
- Modify transaction amounts
- Invent fees
- Directly modify ledger records
- Decide financial values without evidence

### The backend handles:

- Monetary calculations
- Ledger matching
- Settlement calculations
- Fee calculations
- Database transactions
- Ground-truth evaluation

### The AI handles:

- Exception investigation
- Entity reasoning
- Evidence interpretation
- Explanation generation
- Resolution recommendations

This separation makes the system safer and easier to audit.

---

# 📈 Benchmark

SettleX was evaluated against a synthetic dataset containing **150 transactions with known ground truth**.

| Metric | Deterministic Baseline | LangGraph + Gemini | Improvement |
|---|---:|---:|---:|
| Match Rate | 60.0% | **80.0%** | **+20.0%** |
| Accuracy | 80.0% | **93.3%** | **+13.3%** |
| Precision | 85.2% | **94.1%** | **+8.9%** |
| Recall | 80.0% | **91.8%** | **+11.8%** |
| Entity Variations | 0 / 20 | **20 / 20** | **100% Recovery** |
| Fee Discrepancies | 0 / 10 | **10 / 10** | **100% Recovery** |

> The benchmark uses synthetic data and is intended to demonstrate system behavior and evaluation methodology rather than production financial performance.

---

# 🛠️ Tech Stack

## Backend

| Technology | Purpose |
|---|---|
| **Python 3.11+** | Core backend |
| **Django 5.x** | Backend framework |
| **Django REST Framework** | REST APIs |
| **SQLite** | Development database |
| **Pydantic v2** | Structured AI outputs |
| **Pytest / Django Test Runner** | Testing |
| **scikit-learn** | Evaluation metrics |

## AI & Agent

| Technology | Purpose |
|---|---|
| **LangGraph** | Agent orchestration |
| **LangChain Core** | Agent tooling |
| **Google Gemini** | AI reasoning |
| **google-genai** | Gemini API integration |

## Frontend

| Technology | Purpose |
|---|---|
| **React 18** | UI |
| **TypeScript** | Type safety |
| **Vite** | Development/build tooling |
| **Tailwind CSS** | Styling |
| **Axios** | API communication |
| **Recharts** | Data visualization |
| **Lucide Icons** | UI icons |

---

# 📡 REST API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health/` | System health and database statistics |
| `POST` | `/api/datasets/generate/` | Generate synthetic reconciliation data |
| `POST` | `/api/reconciliation/run/` | Start reconciliation |
| `GET` | `/api/reconciliation/<job_id>/results/` | View reconciliation results |
| `GET` | `/api/reconciliation/<job_id>/exceptions/` | View exceptions |
| `GET` | `/api/evaluation/overview/` | View evaluation metrics |
| `GET` | `/api/transactions/<payment_id>/` | Inspect transaction |
| `GET` | `/api/transactions/<payment_id>/audit/` | View investigation audit trail |

---

# 🚀 Quick Start

## Prerequisites

Make sure you have:

- Python 3.11+
- Node.js 18+
- npm
- Google AI Studio API key

---

## 1. Clone the repository

```bash
git clone https://github.com/<your-username>/SettleX.git
cd SettleX
```

---

## 2. Backend Setup

### Windows

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Configure environment variables:

```bash
cp ../.env.example ../.env
```

Add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

Run migrations:

```bash
python manage.py migrate
```

Generate the synthetic dataset:

```bash
python manage.py generate_dataset --count 150
```

Run reconciliation:

```bash
python manage.py run_agent_reconciliation
```

Start Django:

```bash
python manage.py runserver 8000
```

Backend:

```text
http://localhost:8000
```

---

## 3. Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

# 🔄 Example Workflow

```text
Generate Dataset
       ↓
150 Synthetic Transactions
       ↓
Run Reconciliation
       ↓
Deterministic Matching
       ↓
┌───────────────────────────┐
│ Straightforward Cases     │
│ → Automatically Resolved  │
└───────────────────────────┘
       ↓
┌───────────────────────────┐
│ Complex Exceptions        │
│ → LangGraph Agent         │
└───────────────────────────┘
       ↓
Gemini Investigation
       ↓
Evidence Collection
       ↓
RESOLVED / UNRESOLVED
       ↓
Audit Trail
       ↓
Evaluation Dashboard
```

---

# 📂 Project Structure

```text
SettleX/
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   │
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── ...
│   │
│   ├── reconciliation/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── services/
│   │   ├── agent/
│   │   └── management/
│   │
│   └── ...
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── ...
│   │
│   ├── package.json
│   └── vite.config.ts
│
├── docs/
│   └── images/
│       ├── architecture.png
│       ├── dashboard.png
│       ├── reconciliation.png
│       ├── investigation.png
│       ├── audit-trail.png
│       └── evaluation.png
│
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

# 🔒 Security & Data Integrity

SettleX follows several safeguards for financial data processing.

### Environment Isolation

API keys and secrets are stored in environment variables and excluded from version control.

`.env` is never committed.

### Deterministic Financial Arithmetic

Monetary values are calculated using Python `Decimal` rather than floating-point arithmetic.

### Controlled AI Access

The agent interacts with the system through controlled tools rather than unrestricted database access.

### Auditability

Agent tool calls and investigation results are persisted for traceability.

### Human Escalation

When the system cannot establish a reliable explanation, the case is marked:

```text
UNRESOLVED
```

and sent for human review.

---

# 🧪 Testing

Run backend tests:

```bash
pytest
```

or:

```bash
python manage.py test
```

The test suite covers:

- Reconciliation rules
- Settlement calculations
- Duplicate detection
- Exception handling
- Agent tool behavior
- API endpoints
- Evaluation metrics

---

# 🗺️ Future Improvements

SettleX is designed so the architecture can be extended beyond the current prototype.

### Planned possibilities

- PostgreSQL for production workloads
- Redis + Celery for distributed reconciliation jobs
- CSV / Excel ledger uploads
- Real payment gateway integrations
- Real banking integrations
- Role-based access control
- Human approval workflows
- Multi-currency reconciliation
- Automated Slack / email alerts
- Cash-flow forecasting
- Tax-line reconciliation
- Invoice matching
- Multi-agent finance workflows

---

# 💡 Why SettleX?

Traditional reconciliation systems are good at deterministic matching.

LLMs are good at reasoning over ambiguous information.

SettleX combines both:

```text
             FINANCIAL DATA
                    │
                    ↓
        ┌─────────────────────┐
        │ Deterministic Core  │
        │                     │
        │ Exact arithmetic    │
        │ Rule-based matching │
        │ Exception detection │
        └──────────┬──────────┘
                   │
             Complex Cases
                   │
                   ↓
        ┌─────────────────────┐
        │   AI Investigation  │
        │                     │
        │ LangGraph + Gemini  │
        │ Tool-based Evidence │
        │ Structured Output   │
        └──────────┬──────────┘
                   │
                   ↓
           ┌───────────────┐
           │ Final Decision│
           └───────┬───────┘
                   │
          ┌────────┴────────┐
          ↓                 ↓
      RESOLVED          UNRESOLVED
          │                 │
          ↓                 ↓
      Auto Close       Human Review
```

> **SettleX doesn't replace financial controls with AI. It puts AI behind them.**

---

# 📜 License

This project is distributed under the MIT License.

See [`LICENSE`](LICENSE) for more information.

---

# 👨‍💻 Built With

**Django · React · TypeScript · LangGraph · Google Gemini · SQLite · Tailwind CSS**

---

<p align="center">
  <strong>SettleX</strong>
  <br />
  <em>Reconcile faster. Investigate smarter. Escalate responsibly.</em>
</p>
