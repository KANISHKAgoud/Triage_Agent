# 🤖 AI Triage Agent

An AI-powered IT Support Triage Agent built using **FastAPI**, **LangGraph**, **Gemini 2.5 Flash**, **RAG (Retrieval-Augmented Generation)**, **ChromaDB**, **PostgreSQL**, **Jira**, **ServiceNow**, and **SMTP Email**.

The system automatically classifies IT support tickets, retrieves similar historical incidents, generates AI-powered resolutions, updates external ticketing systems, stores ticket history, and sends professional HTML email reports.

---

# 🚀 Features

- AI-powered IT ticket classification
- Retrieval-Augmented Generation (RAG)
- Similar incident retrieval using ChromaDB
- LangGraph workflow orchestration
- Gemini 2.5 Flash integration
- Automatic Category Prediction
- Automatic Subcategory Prediction
- AI Resolution Recommendation
- Confidence Score Generation
- Keyword Boost Retrieval
- PostgreSQL Ticket Storage
- Jira Integration
- ServiceNow Integration
- Professional HTML Email Reports
- FastAPI REST APIs
- Interactive Swagger Documentation

---

# 🛠 Tech Stack

## Backend

- Python 3.10+
- FastAPI
- LangGraph
- Uvicorn

## AI

- Google Gemini 2.5 Flash
- Sentence Transformers
- RAG
- ChromaDB

## Database

- PostgreSQL

## Integrations

- Jira Cloud REST API
- ServiceNow API
- SMTP Email

## Frontend

- React
- Vite
- Tailwind CSS

---

# 📁 Project Structure

```
backend/
│
├── src/
│   ├── api/
│   ├── graph/
│   ├── nodes/
│   ├── prompts/
│   ├── services/
│   ├── storage/
│   ├── utils/
│   └── main.py
│
├── database.py
├── models.py
└── ticket_status.py

frontend/

rag/

data/

chroma_db/

tests/
```

---

# ⚙️ AI Workflow

```
User Ticket
      │
      ▼
Retrieve Similar Incidents
      │
      ▼
Keyword Boost
      │
      ▼
Confidence Calculation
      │
      ▼
Gemini AI
      │
      ▼
Category Prediction
      │
      ▼
Subcategory Prediction
      │
      ▼
Resolution Generation
      │
      ▼
Decision Node
      │
      ▼
Save Results
      │
      ▼
Response
      │
      ├────────► PostgreSQL
      │
      ├────────► Jira
      │
      ├────────► ServiceNow
      │
      └────────► HTML Email
```

---

# 🧠 AI Pipeline

- Retrieve Similar Historical Incidents
- Semantic Search
- Keyword Boosting
- Confidence Calculation
- Prompt Engineering
- Gemini Response Generation
- Category Classification
- Subcategory Classification
- Resolution Recommendation
- Database Storage
- External System Integration

---

# 📦 Installation

## 1. Clone Repository

```bash
git clone <repository-url>
cd Triage_Agent
```

---

## 2. Create Virtual Environment

Windows

```bash
python -m venv venv
```

Activate

```bash
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file.

Example:

```env
GEMINI_API_KEY=

GEMINI_MODEL=gemini-2.5-flash

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=
SMTP_PASSWORD=

POSTGRES_HOST=
POSTGRES_PORT=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=

JIRA_URL=
JIRA_EMAIL=
JIRA_API_TOKEN=
JIRA_PROJECT_KEY=

SERVICENOW_URL=
SERVICENOW_USERNAME=
SERVICENOW_PASSWORD=
```

---

# 🗄 Database Setup

Create PostgreSQL tables.

Run:

```bash
python create_postgres_table.py

python create_ticket_table.py

python create_processed_jira_table.py

python create_servicenow_table.py

python create_ticket_status_table.py
```

---

# 📂 Create Vector Database

Generate Chroma embeddings.

```bash
python rag/ingest.py
```

---

# ▶️ Run Backend

```bash
python -m uvicorn backend.src.main:app --reload
```

Backend

```
http://127.0.0.1:8000
```

Swagger

```
http://127.0.0.1:8000/docs
```

---

# 💻 Run Frontend

Move to frontend.

```bash
cd frontend
```

Install packages.

```bash
npm install
```

Run

```bash
npm run dev
```

Frontend

```
http://localhost:5173
```

---

# 📧 Email Workflow

The system automatically sends a professional HTML email after processing a ticket.

The email contains:

- Ticket Summary
- Issue Details
- AI Category
- AI Subcategory
- Recommended Resolution
- Confidence Score
- Similar Historical Incident
- Previous Resolution
- Technology Stack

---

# 🎯 Jira Workflow

Create Jira Ticket

↓

Retrieve Ticket

↓

AI Processing

↓

Add AI Comment

↓

Store Ticket

↓

Update Status

↓

Send Email Report

---

# 🗃 ServiceNow Workflow

Receive Ticket

↓

Generate AI Resolution

↓

Create Incident

↓

Store in PostgreSQL

---

# 📡 API Endpoints

## Agent

```
POST /agent/query
```

---

## Jira

```
GET /jira/issues

GET /jira/issue/{issue_key}

POST /jira/process-ticket/{issue_key}

GET /jira/process-all

GET /jira/unprocessed
```

---

## Outlook

```
GET /outlook/test

GET /outlook/live

GET /outlook/process
```

---

## Dashboard

```
GET /dashboard
```

---

# 📊 Technologies Used

- FastAPI
- LangGraph
- Gemini 2.5 Flash
- ChromaDB
- Sentence Transformers
- PostgreSQL
- Jira Cloud
- ServiceNow
- SMTP
- React
- Tailwind CSS
- Vite

---

# 📌 Future Improvements

- Microsoft Outlook Graph API
- Docker PostgreSQL Container
- Background Scheduler
- User Authentication
- Role-Based Access Control
- Analytics Dashboard
- Ticket Prioritization using LLM
- Multi-LLM Support

---

# 👨‍💻 Developed By

**Kanishka Goud**

AI/ML Intern

Provatosoft Pvt. Ltd.
