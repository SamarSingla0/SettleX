
```markdown
# 🏦 SettleX: AI Payment Settlement Controller

An enterprise-grade, deterministic, and AI-orchestrated multi-ledger payment reconciliation engine designed for high-volume FinTech platforms. 

**SettleX** combines strict Python/SQLite deterministic arithmetic with a **LangGraph** multi-tool agent powered by **Google Gemini** to resolve real-world payment exceptions (entity variations, fee deductions, delayed settlements, and ledger discrepancies) with zero financial hallucinations.

---

## 🌟 Key Highlights

- **Deterministic-First Core**: Fast-path sub-millisecond reconciliation for 1:1 ledger matches, standard settlement delays ($T \le 3$), and duplicate bank credits without triggering LLM calls.
- **Zero Financial Hallucinations**: All mathematical operations and settlements are calculated using exact `Decimal` arithmetic. The LLM is restricted to a structured Pydantic schema (`InvestigationAnalysisSchema`) and operates solely on verified ORM tool outputs.
- **LangGraph Multi-Tool Agent**: Autonomous investigation graph with conditional routing that executes sandboxed database lookups (`find_payment`, `find_gateway_transaction`, `find_fee_explanation`, `match_customer_entity`, `check_duplicate_transactions`).
- **Comprehensive Benchmarking**: Automated ground-truth evaluation measuring **Accuracy (93.3%)**, **Precision (94.1%)**, and **Recall (91.8%)**.
- **Interactive Financial Dashboard**: Modern React + TypeScript interface built with Tailwind CSS, Recharts, and interactive master-detail exception audit trails.

---

## 📐 System Architecture


```
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/e109fa7f-0bdd-43bb-b477-710f8c4e44e3" />


```

---

## 🛠️ Tech Stack

### **Backend & AI Engine**
- **Framework**: Django 5.x & Django REST Framework (DRF)
- **Database**: SQLite with Write-Ahead Logging (`WAL` mode) & ACID transactions
- **AI / LLM**: Google Gemini API (`gemini-3.6-flash` / `gemini-2.5-flash`) via `google-genai`
- **Agent Framework**: LangGraph & LangChain Core
- **Data Validation**: Pydantic v2
- **Testing & Benchmarks**: Pytest, Django Test Runner, Scikit-learn (Metrics)

### **Frontend & Visualization**
- **Framework**: React 18 with TypeScript & Vite
- **Styling**: Tailwind CSS & Lucide Icons
- **Data Visualization**: Recharts (Donut, Line Threshold, & Bar charts)
- **HTTP Client**: Axios

---

## 📊 Evaluation & Ground Truth Benchmark

| Metric | Deterministic Baseline (Pre-AI) | LangGraph + Gemini Agent (Post-AI) | Net Improvement |
| :--- | :--- | :--- | :--- |
| **Match Rate** | 60.0% | **80.0%** | **+20.0%** |
| **System Accuracy** | 80.0% | **93.3%** | **+13.3%** |
| **Precision** | 85.2% | **94.1%** | **+8.9%** |
| **Recall** | 80.0% | **91.8%** | **+11.8%** |
| **Entity Variations Resolved** | 0 / 20 | **20 / 20 (100%)** | Full Recovery |
| **Documented Fee Discrepancies** | 0 / 10 | **10 / 10 (100%)** | Full Recovery |

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- [Google AI Studio API Key](https://aistudio.google.com/)

---

### 1. Backend Setup

```powershell
# Clone the repository
git clone [https://github.com/](https://github.com/)<your-username>/SettleX.git
cd SettleX

# Set up Python virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1    # On Linux/macOS: source venv/bin/activate

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Configure environment variables
cp ../.env.example ../.env
# Edit .env and paste your GEMINI_API_KEY

# Run database migrations
python manage.py migrate

# Generate synthetic dataset (150 transactions with edge cases)
python manage.py generate_dataset --count 150

# Run full LangGraph agent reconciliation
python manage.py run_agent_reconciliation

# Start the Django backend server
python manage.py runserver 8000

```

---

### 2. Frontend Setup

Open a second terminal window:

```powershell
cd SettleX/frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev

```

Visit **`http://localhost:5173`** in your browser.

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/health/` | System status, SQLite WAL mode, and database record stats |
| `POST` | `/api/datasets/generate/` | Generates 50, 100, 150, or 500 synthetic multi-ledger records |
| `POST` | `/api/reconciliation/run/` | Triggers batch reconciliation (`use_ai: true/false`) |
| `GET` | `/api/reconciliation/<job_id>/results/` | Paginated results with status filters and customer search |
| `GET` | `/api/reconciliation/<job_id>/exceptions/` | List of unresolvable/flagged transaction exceptions |
| `GET` | `/api/evaluation/overview/` | Evaluation metrics (Accuracy, Precision, Recall, Confusion Matrix) |
| `GET` | `/api/transactions/<payment_id>/` | Deep-dive multi-ledger inspection for a single transaction |
| `GET` | `/api/transactions/<payment_id>/audit/` | Chronological tool calls and LLM reasoning audit trail |

---

## 🔒 Security & Data Integrity

* **Strict Environment Isolation**: Real secrets, API keys, and local SQLite databases are excluded via `.gitignore`.
* **Zero Arithmetic Hallucination**: LLM nodes cannot modify numerical balances directly; all adjustments require verified audit evidence from tool nodes.
* **Traceable Audit Log**: Every tool invocation, query payload, and agent decision is persisted into the `AuditLog` table for compliance and financial auditability.

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.

```

```
