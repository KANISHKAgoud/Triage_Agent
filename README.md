# Triage_Agent# AI-Powered Triage Agent

## Overview

The AI-Powered Triage Agent is an intelligent incident management system that automatically processes incoming support requests, retrieves similar historical incidents using Retrieval-Augmented Generation (RAG), classifies tickets using Azure OpenAI and LangGraph, stores results in PostgreSQL, and integrates with Outlook and ServiceNow workflows.

The system is designed to reduce manual triage effort by automatically identifying incident categories, suggesting resolutions, and creating structured ticket records.

---

## Architecture

```text
Outlook Mailbox
       │
       ▼
Email Processor
       │
       ▼
LangGraph Workflow
       │
       ▼
RAG Search (ChromaDB)
       │
       ▼
Azure OpenAI
       │
       ▼
Incident Classification
       │
       ▼
Ticket Creation
       │
       ▼
PostgreSQL Storage
       │
       ├── ServiceNow Integration
       │
       └── Email Notification
```

---

## Features

### Intelligent Ticket Classification

* Automatic incident categorization
* Automatic sub-category prediction
* Confidence score generation
* Resolution recommendation

### RAG-Powered Incident Retrieval

* Semantic search using ChromaDB
* Historical incident matching
* Similar ticket retrieval
* Context-aware recommendations

### LangGraph Agent Workflow

* Retrieval Node
* Classification Node
* Resolution Node
* Response Node

### Ticket Management

* Ticket creation
* Ticket status tracking
* Dashboard monitoring
* Incident history storage

### Outlook Integration

* Mailbox monitoring
* Email processing workflow
* Processed email tracking
* Real Outlook-ready architecture

### ServiceNow Integration

* Incident creation workflow
* Ticket synchronization skeleton
* Enterprise integration architecture

### Storage

* PostgreSQL
* SQLite
* ChromaDB Vector Store

### Containerization

* Docker support
* Docker Compose support

---

## Technology Stack

### Backend

* Python
* FastAPI
* LangGraph

### AI & LLM

* Azure OpenAI
* GPT-4o

### Vector Database

* ChromaDB
* Sentence Transformers

### Databases

* PostgreSQL
* SQLite

### DevOps

* Docker
* Docker Compose

---

## API Endpoints

### Agent APIs

| Method | Endpoint          |
| ------ | ----------------- |
| POST   | /agent            |
| GET    | /history          |
| GET    | /postgres-history |

### Outlook APIs

| Method | Endpoint         |
| ------ | ---------------- |
| GET    | /outlook/test    |
| GET    | /outlook/process |

### Monitoring APIs

| Method | Endpoint       |
| ------ | -------------- |
| GET    | /dashboard     |
| GET    | /vector-health |

### Ticket APIs

| Method | Endpoint |
| ------ | -------- |
| GET    | /tickets |

---

## Sample Workflow

1. User sends an email.
2. Outlook service retrieves the email.
3. LangGraph starts the triage workflow.
4. ChromaDB retrieves similar incidents.
5. Azure OpenAI predicts category and resolution.
6. Ticket is created.
7. Ticket is stored in PostgreSQL.
8. ServiceNow incident workflow is triggered.
9. Resolution email is generated.

---

## Running the Project

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
python -m uvicorn backend.main:app --reload
```

---

## Docker

### Build

```bash
docker build -t triage-agent .
```

### Run

```bash
docker run -p 8000:8000 triage-agent
```

---

## Future Enhancements

* Real Microsoft Graph Integration
* Real Outlook Mailbox Processing
* ServiceNow REST API Integration
* Azure Deployment
* Multi-Agent Workflow
* Human Approval Workflow
* Automated Ticket Assignment
* Monitoring Dashboard

---

## Author

Kanishka Goud

Computer Engineering | Savitribai Phule Pune University

AI-Powered Triage Agent Internship Project
