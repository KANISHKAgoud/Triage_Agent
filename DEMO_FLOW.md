# Triage Agent Demo Flow

## 1. Start Application

```bash
python -m uvicorn backend.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

---

## 2. Check System Health

Run:

GET /dashboard

Expected:

* Total Tickets
* Triaged Tickets
* Mailbox Connected
* Vector DB Healthy

---

## 3. Check Vector Database

Run:

GET /vector-health

Expected:

* ChromaDB Healthy
* 100 Documents Loaded

---

## 4. Test AI Triage

POST /agent

Input:

```json
{
  "search_query": "VPN login failing after changing phone",
  "session_id": "ctx-001"
}
```

Show:

* Predicted Category
* Predicted Subcategory
* Confidence Score
* Recommended Resolution

---

## 5. Show RAG Results

Explain:

* Similar incidents retrieved
* Historical tickets used as context
* ChromaDB semantic search

---

## 6. Show Outlook Processing

GET /outlook/test

GET /outlook/process

Explain:

* Mailbox monitoring
* Email ingestion
* Ticket generation

---

## 7. Show PostgreSQL Storage

GET /tickets

Explain:

* Ticket stored
* Status tracking
* Resolution tracking

---

## 8. Show Architecture

Explain:

Outlook → LangGraph → RAG → Azure OpenAI → PostgreSQL → ServiceNow → Email

---

## 9. Docker

Show:

```bash
docker ps
```

Explain:

* PostgreSQL container
* FreeScout container
* Triage Agent container
