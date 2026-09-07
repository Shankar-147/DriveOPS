# DriveOps

DriveOps is an AI agent that manages a single vehicle on behalf of its owner — tracking maintenance, documents, expenses, and appointments, and reasoning over that data through a tool-calling LLM agent. It's a full-stack app: a FastAPI backend that exposes the agent as both a REST API and a chat interface, and a React + TypeScript website that surfaces the same data and actions visually.

## Features

- **Chat agent** — ask natural-language questions ("what's going on with my car?", "I'm driving to Pondicherry tomorrow, what should I do?") and get answers grounded in real tool calls, not guesses.
- **Persistent conversation memory** — chats are stored in the database, not just in server memory, so they survive a restart. A ChatGPT-style sidebar lets you browse, resume, or delete past conversations.
- **Safety-tiered actions** — every tool is tagged GREEN (read-only, runs freely), YELLOW (writes state, requires explicit user confirmation before executing), or RED (never executed by the agent — payments, insurance changes, etc.). A YELLOW action is proposed, confirmed, executed, and then verified by reading it back before the agent reports success.
- **Dashboard** — a "command center" view: prioritized HIGH/MEDIUM/LOW alerts, a vehicle health score, and scheduler-driven notifications.
- **Full CRUD pages** — Vehicle Profile, Service History, Documents (with expiry countdown), Expenses (with anomaly detection highlighted on the chart), and Appointments (search service centers, book, confirm).
- **Advanced modules**:
  - **Health Score** — a weighted composite (maintenance/tyres/battery/documents/recalls) framed as "worth inspecting," never a diagnosis.
  - **Trip Prep** — combines maintenance, tyres, documents, and weather into a readiness % and checklist for a planned drive.
  - **Anomaly Detection** — flags a month/category if it's >1.5x its trailing 3-month average.
  - **Breakdown Recovery** — triggered by "I broke down," gives safety guidance and towing-only options, never DIY repair instructions.
- **Background scheduler** — a daily check writes notifications when maintenance or documents need attention.

## Tech stack

- **Backend**: FastAPI, SQLite, APScheduler, httpx — Python 3.14
- **Agent**: OpenRouter (OpenAI-compatible tool-calling), model configurable via `.env`
- **Frontend**: React 19 + TypeScript + Vite, Tailwind CSS v4, react-router-dom, recharts, lucide-react

## External APIs used

- [NHTSA Recalls](https://api.nhtsa.gov/recalls/recallsByVehicle) — model-level recall lookups (US-market vehicles only)
- [Open-Meteo](https://open-meteo.com/) — geocoding + weather forecast, no API key required
- [OpenRouter](https://openrouter.ai/) — LLM chat completions with tool calling

## Project structure

```
DriveOps/
├── backend/
│   ├── main.py                # FastAPI app, CORS, scheduler startup
│   ├── db_access.py           # the only file that touches SQLite directly
│   ├── scheduler.py           # daily maintenance/document notification check
│   ├── agent/                 # LLM client, system prompt, tool-calling loop, tool registry
│   ├── tools/                 # one file per tool group (GREEN + YELLOW)
│   ├── modules/               # health_score, trip_prep, anomaly_detection, breakdown_recovery
│   └── routers/                # FastAPI routers (vehicle, chat, documents, expenses, appointments)
├── db/
│   ├── schema.sql
│   └── seed.py                 # (re)creates driveops.db with demo data for VH001
├── frontend/
│   └── src/
│       ├── pages/               # Dashboard, VehicleProfile, ServiceHistory, Documents, Expenses,
│       │                        # Appointments, ChatAgent, Settings
│       ├── components/          # Sidebar, TopBar, PriorityCard, ConfirmActionModal, ChatBubble,
│       │                        # HealthScoreGauge, ExpenseChart
│       └── api/client.ts        # single axios wrapper - the only file that knows the backend URL
├── tests/
│   ├── test_db_access.py
│   ├── test_tools.py
│   └── test_loop.py             # live-LLM reasoning test cases (hits OpenRouter)
└── run.bat                       # double-click to start both servers + open the browser
```

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- An [OpenRouter](https://openrouter.ai/) API key (a free-tier model works fine)

### Backend

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

cp .env.example .env           # then fill in OPENROUTER_API_KEY
python db/seed.py              # creates db/driveops.db with demo data

uvicorn backend.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env           # defaults are fine for local dev
npm run dev
```

Then open **http://localhost:5173**.

### One-click (Windows)

Once both are set up once, just double-click **`run.bat`** — it starts the backend, the frontend, and opens your browser automatically.

## Running tests

```bash
python db/seed.py                      # reset to a known state first
python tests/test_db_access.py
python tests/test_tools.py
python tests/test_loop.py              # hits the live LLM - needs OPENROUTER_API_KEY
```

## Safety model

Every tool is tagged one of three tiers, enforced in the agent loop:

| Tier | Meaning | Examples |
|---|---|---|
| 🟢 GREEN | Read-only, runs automatically | `get_vehicle_profile`, `check_maintenance_due`, `get_weather` |
| 🟡 YELLOW | Writes state, requires explicit confirmation first | `create_service_appointment`, `add_expense`, `schedule_reminder` |
| 🔴 RED | Never executed by the agent | payments, insurance changes, ownership transfer |

A YELLOW tool call without `confirmed: true` returns a `needs_confirmation` stub instead of executing; only after the user confirms does it run and get verified by reading the row back.
