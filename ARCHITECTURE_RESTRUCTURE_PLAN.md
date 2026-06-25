# Triage Agent Business Problem And Architecture Restructure Plan

## 1. Executive Summary

The Triage Agent project is an AI-assisted incident triage platform for IT support teams. Its core business purpose is to reduce manual ticket review effort by reading incoming support requests, finding similar historical incidents, predicting category and subcategory, recommending a resolution, and optionally updating downstream systems such as Jira, FreeScout, ServiceNow, Outlook, and email.

The current project already proves the idea: it has FastAPI routes, LangGraph workflow logic, Azure OpenAI integration, ChromaDB semantic search, Jira/FreeScout/Outlook/ServiceNow connectors, SQLite/PostgreSQL storage, and a React dashboard.

The problem is that the project is currently organized like a prototype that kept growing. Business logic, API routing, external integrations, storage concerns, demo endpoints, and workflow orchestration are mixed together. That makes the product harder to test, harder to scale, harder to secure, and harder to explain to enterprise stakeholders.

This document defines:

- The detailed business problem.
- The target product capabilities.
- The correct modular project structure.
- The target system architecture.
- API, domain, data, workflow, integration, and deployment boundaries.
- A practical migration roadmap from the current codebase to a cleaner architecture.

## 2. Detailed Business Problem

### 2.1 Current Operational Problem

IT support teams receive large volumes of tickets through email, Jira, FreeScout, ServiceNow, and other intake channels. Many tickets are repetitive:

- VPN login failures.
- Password reset issues.
- MFA registration problems.
- Shared mailbox access requests.
- Laptop, printer, monitor, or hardware failures.
- Slow database/reporting jobs.
- Application access problems.

Human agents spend time reading each ticket, understanding symptoms, searching past incidents, deciding the right category, selecting subcategory, and writing a resolution or next action.

This creates several business issues:

- Slow first response time.
- Inconsistent ticket categorization.
- Repeated manual investigation for known issues.
- Poor knowledge reuse from historical incidents.
- Weak operational visibility into common support patterns.
- Higher support cost per ticket.
- Delayed routing to the correct resolver group.

### 2.2 Business Goal

The product should become an intelligent triage assistant that helps support teams convert unstructured support requests into structured, auditable, actionable triage decisions.

The business goal is not simply "use AI." The business goal is:

- Reduce manual triage time.
- Improve categorization consistency.
- Improve first response quality.
- Reuse historical incident knowledge.
- Provide transparent confidence and audit history.
- Support human approval before automation when confidence is low or business risk is high.

### 2.3 Target Users

Primary users:

- IT support agents.
- Service desk supervisors.
- Incident managers.

Secondary users:

- Platform administrators.
- Engineering teams maintaining integrations.
- Business stakeholders monitoring ticket trends.

### 2.4 Core Jobs To Be Done

Support agent:

- "When a new ticket arrives, help me quickly understand what kind of issue it is and what resolution has worked before."

Service desk supervisor:

- "Give me consistent triage quality, measurable automation performance, and visibility into unresolved or low-confidence tickets."

Administrator:

- "Let me connect ticket systems safely, configure confidence thresholds, monitor failures, and audit automated actions."

Business executive:

- "Reduce support handling cost and response time without creating uncontrolled automation risk."

## 3. Product Scope

### 3.1 In Scope

The target product should support:

- Ticket intake from API, email, Jira, FreeScout, and eventually ServiceNow.
- Text normalization from subject, description, email body, and comments.
- Retrieval of similar historical incidents using vector search.
- AI classification into category and subcategory.
- AI recommended resolution.
- Confidence scoring and decision policy.
- Human review queue for low-confidence or sensitive decisions.
- Action publishing to Jira/FreeScout/ServiceNow/email.
- Dashboard and operational reporting.
- Audit logs for all AI decisions and external actions.

### 3.2 Out Of Scope For First Production Version

These should not be core requirements for the first clean production version:

- Fully autonomous closure of tickets.
- Multi-tenant enterprise RBAC.
- Complex SLA prediction.
- Full ITSM replacement.
- Real-time streaming agent chat.
- Custom model training pipeline.

The product should first become reliable at assisted triage before becoming autonomous.

## 4. Current Architecture Problems

### 4.1 Route Layer Is Too Large

`backend/routes.py` currently owns many responsibilities:

- Agent query processing.
- FreeScout webhook processing.
- Email test endpoints.
- Outlook processing.
- History endpoints.
- Ticket listing.
- Dashboard aggregation.
- ServiceNow incidents.
- Jira listing, enrichment, processing, and status.

This makes the route layer difficult to test and risky to change.

### 4.2 Business Logic Is Mixed With HTTP

Several route handlers directly:

- Fetch external tickets.
- Parse Jira descriptions.
- Call LangGraph.
- Add Jira comments.
- Mark tickets processed.
- Set ticket status.
- Build response objects.

HTTP handlers should validate requests and call application services. They should not contain domain workflow logic.

### 4.3 External Integrations Are Thin And Unsafe

The Jira and email integrations need:

- Timeouts.
- Error handling.
- Status code validation.
- Retries where safe.
- Typed responses.
- Clear exception types.
- Structured logging.

Currently, some integration code prints response status and text, then returns raw JSON. That is acceptable for a spike, not for a product.

### 4.4 Data Ownership Is Unclear

The app uses SQLite, PostgreSQL, ChromaDB, and several root-level table creation scripts. The storage strategy is not cleanly separated.

Problems:

- Multiple sources of truth.
- Manual schema creation scripts.
- No migration framework.
- Storage modules tied to raw tuple access.
- Unclear ownership between ticket storage, processed Jira storage, status storage, and triage history.

### 4.5 Workflow Calls The LLM More Than Needed

The current LangGraph flow calls the LLM for classification and again for resolution using the same context. This increases:

- Cost.
- Latency.
- Failure probability.
- Inconsistent outputs.

The triage decision should be produced in one structured AI call unless there is a specific reason to split it.

### 4.6 Automation Safety Is Weak

Some routes perform side effects using `GET`, such as processing tickets and writing comments. Mutation endpoints should use `POST`, `PUT`, or `PATCH`.

The system should distinguish:

- Prediction.
- Draft recommendation.
- Human-approved action.
- Automated action.

### 4.7 Observability Is Prototype-Level

The code uses `print()` for operational visibility. A production system needs:

- Structured logs.
- Request IDs.
- Integration latency tracking.
- LLM usage tracking.
- Error categorization.
- Audit events.

## 5. Target Architecture Principles

The restructured project should follow these principles:

1. Keep HTTP thin.
2. Keep business logic in application services.
3. Keep domain models independent of FastAPI and external APIs.
4. Keep integration clients isolated.
5. Keep persistence behind repositories.
6. Make AI workflow deterministic around inputs, outputs, and audit records.
7. Make external side effects explicit and controlled.
8. Prefer one primary relational database.
9. Treat vector search as a knowledge index, not the source of truth.
10. Make every automated decision auditable.

## 6. Target System Architecture

```text
                    +-----------------------+
                    |       Frontend        |
                    | React Dashboard/Admin |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    |      FastAPI API      |
                    | Routers + Validation  |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    |  Application Services |
                    | Use Cases / Workflows |
                    +-----------+-----------+
                                |
         +----------------------+----------------------+
         |                      |                      |
         v                      v                      v
+----------------+     +----------------+     +----------------+
| Domain Layer   |     | AI/RAG Layer    |     | Integrations   |
| Entities/Rules |     | LangGraph/LLM   |     | Jira/Email/etc |
+-------+--------+     +-------+--------+     +-------+--------+
        |                      |                      |
        v                      v                      v
+----------------+     +----------------+     +----------------+
| PostgreSQL     |     | ChromaDB        |     | External APIs  |
| Source of Truth|     | Vector Index    |     | ITSM Systems   |
+----------------+     +----------------+     +----------------+
```

## 7. Recommended Project Structure

```text
Triage_Agent/
  backend/
    app/
      __init__.py
      main.py
      config.py
      logging.py
      dependencies.py

      api/
        __init__.py
        router.py
        routes/
          __init__.py
          health.py
          agent.py
          tickets.py
          jira.py
          freescout.py
          servicenow.py
          email.py
          dashboard.py

      domain/
        __init__.py
        models/
          __init__.py
          ticket.py
          triage.py
          incident.py
          integration.py
        policies/
          __init__.py
          triage_policy.py
          automation_policy.py
        exceptions.py

      application/
        __init__.py
        services/
          __init__.py
          triage_service.py
          ticket_service.py
          dashboard_service.py
          approval_service.py
          audit_service.py
        workflows/
          __init__.py
          triage_workflow.py
        commands/
          __init__.py
          process_ticket.py
          process_jira_ticket.py
          process_email.py
        queries/
          __init__.py
          get_dashboard.py
          list_tickets.py
          list_jira_issues.py

      infrastructure/
        __init__.py
        database/
          __init__.py
          session.py
          migrations/
          repositories/
            __init__.py
            ticket_repository.py
            triage_repository.py
            incident_repository.py
            audit_repository.py
        vector/
          __init__.py
          chroma_client.py
          incident_index.py
          ingestion.py
        llm/
          __init__.py
          azure_openai_client.py
          prompts.py
          schemas.py
        integrations/
          __init__.py
          jira/
            __init__.py
            client.py
            mapper.py
          freescout/
            __init__.py
            client.py
            mapper.py
          outlook/
            __init__.py
            client.py
            mapper.py
          servicenow/
            __init__.py
            client.py
            mapper.py
          smtp/
            __init__.py
            client.py

      schemas/
        __init__.py
        requests.py
        responses.py
        jira.py
        dashboard.py

    tests/
      unit/
      integration/
      contract/

  frontend/
    src/
      app/
      components/
      pages/
      services/
      types/
      utils/

  docs/
    architecture.md
    api.md
    operations.md
    deployment.md

  scripts/
    ingest_incidents.py
    seed_demo_data.py

  docker/
    Dockerfile
    docker-compose.yml

  README.md
  ARCHITECTURE_RESTRUCTURE_PLAN.md
```

## 8. Module Responsibilities

### 8.1 `backend/app/main.py`

Responsibility:

- Create the FastAPI app.
- Register routers.
- Configure middleware.
- Configure startup and shutdown lifecycle.

It should not:

- Create tables directly.
- Contain business logic.
- Import integration clients directly.

### 8.2 `backend/app/config.py`

Responsibility:

- Centralized settings using environment variables.
- Validate required configuration at startup.
- Separate development defaults from production requirements.

Recommended settings:

- App environment.
- API host/port.
- Database URL.
- Chroma persistence path.
- Azure OpenAI endpoint/key/model/api version.
- Jira URL/email/token/project.
- FreeScout URL/key.
- SMTP configuration.
- Outlook/Microsoft Graph credentials.
- Automation thresholds.

### 8.3 `api/routes`

Responsibility:

- Validate incoming HTTP requests.
- Call application services.
- Return response schemas.
- Translate domain/application exceptions to HTTP errors.

Example route groups:

- `health.py`: readiness/liveness.
- `agent.py`: direct triage prediction.
- `tickets.py`: internal ticket listing and status.
- `jira.py`: Jira import/process/comment actions.
- `freescout.py`: webhook endpoint and ticket updates.
- `email.py`: email intake and notification.
- `dashboard.py`: dashboard metrics.

### 8.4 `domain`

Responsibility:

- Core business concepts.
- Business rules.
- Decision policies.

Domain models should describe:

- Ticket.
- Incident.
- TriageDecision.
- RetrievedIncident.
- AutomationDecision.
- ExternalAction.
- AuditEvent.

The domain layer should not know about:

- FastAPI.
- SQL.
- Chroma.
- Jira REST API.
- Azure OpenAI SDK.

### 8.5 `application/services`

Responsibility:

- Coordinate use cases.
- Call repositories.
- Call workflows.
- Call integrations through interfaces/clients.
- Enforce business rules.

Important services:

- `TriageService`: creates triage decisions.
- `TicketService`: owns ticket lifecycle and status changes.
- `DashboardService`: aggregates metrics.
- `AuditService`: records decisions and side effects.
- `ApprovalService`: handles human review queue.

### 8.6 `application/workflows`

Responsibility:

- Encapsulate LangGraph or workflow orchestration.
- Accept clean input objects.
- Return clean output objects.

The workflow should produce one structured result:

```json
{
  "category": "Access Management",
  "subcategory": "MFA Reset",
  "confidence_score": 0.86,
  "recommended_resolution": "Reset MFA registration and ask the user to re-enroll.",
  "reasoning_summary": "Similar historical incidents involved phone change and MFA device mismatch.",
  "retrieved_incidents": []
}
```

### 8.7 `infrastructure/database/repositories`

Responsibility:

- Persist and retrieve data.
- Hide SQL/ORM details from application services.
- Return domain objects or typed data transfer objects.

Recommended repositories:

- `TicketRepository`.
- `TriageRepository`.
- `IncidentRepository`.
- `AuditRepository`.
- `IntegrationSyncRepository`.

### 8.8 `infrastructure/vector`

Responsibility:

- ChromaDB client setup.
- Historical incident indexing.
- Semantic search.
- Vector health checks.

Vector search should return retrieved incident candidates. It should not decide final ticket category.

### 8.9 `infrastructure/llm`

Responsibility:

- Azure OpenAI client creation.
- Prompt templates.
- Structured output schemas.
- LLM error mapping.
- Token/cost metadata capture.

The LLM layer should not write to databases or external ticket systems.

### 8.10 `infrastructure/integrations`

Responsibility:

- External API clients.
- Authentication.
- Request timeouts.
- Response validation.
- Integration-specific mappers.

Each integration should expose business-level methods:

- `list_issues()`.
- `get_issue(issue_key)`.
- `add_comment(issue_key, comment)`.
- `update_fields(issue_key, fields)`.
- `create_incident(payload)`.
- `send_email(payload)`.

No route should build raw Jira or ServiceNow payloads directly.

## 9. Target Business Workflow

### 9.1 Assisted Triage Flow

```text
Ticket Intake
  -> Normalize ticket text
  -> Retrieve similar incidents
  -> Generate triage decision
  -> Apply confidence policy
  -> Save decision and audit event
  -> Return recommendation to UI
```

### 9.2 Human Approval Flow

```text
Triage Decision
  -> Confidence below threshold or sensitive category
  -> Put into Review Queue
  -> Human approves/edits/rejects
  -> Publish action to external system
  -> Save audit event
```

### 9.3 Automated Publishing Flow

```text
Triage Decision
  -> Confidence above threshold
  -> Automation enabled for source system
  -> Create external action request
  -> Publish Jira/FreeScout/ServiceNow update
  -> Save external action result
  -> Save audit event
```

## 10. API Design

### 10.1 Health

```text
GET /health/live
GET /health/ready
```

### 10.2 Agent/Triage

```text
POST /triage/predict
POST /triage/tickets/{ticket_id}/process
GET  /triage/decisions/{decision_id}
GET  /triage/history
```

### 10.3 Tickets

```text
GET   /tickets
GET   /tickets/{ticket_id}
PATCH /tickets/{ticket_id}/status
```

### 10.4 Jira

```text
GET  /integrations/jira/issues
GET  /integrations/jira/issues/{issue_key}
POST /integrations/jira/issues/{issue_key}/triage
POST /integrations/jira/issues/{issue_key}/comments
POST /integrations/jira/sync
```

Important: processing and commenting must be `POST`, not `GET`.

### 10.5 FreeScout

```text
POST /webhooks/freescout/ticket-created
POST /integrations/freescout/tickets/{ticket_id}/triage
```

### 10.6 Email

```text
POST /integrations/email/process
POST /integrations/email/send-resolution
```

### 10.7 Dashboard

```text
GET /dashboard/summary
GET /dashboard/triage-quality
GET /dashboard/integration-health
```

## 11. Data Architecture

### 11.1 Recommended Source Of Truth

Use PostgreSQL as the primary source of truth.

Use ChromaDB only as a vector index for historical incidents and knowledge retrieval.

Use SQLite only for local demo mode if needed, behind the same repository interfaces.

### 11.2 Core Tables

#### `tickets`

Stores normalized internal ticket records.

Fields:

- `id`
- `external_source`
- `external_id`
- `subject`
- `description`
- `status`
- `created_at`
- `updated_at`

#### `triage_decisions`

Stores AI decision output.

Fields:

- `id`
- `ticket_id`
- `category`
- `subcategory`
- `confidence_score`
- `recommended_resolution`
- `reasoning_summary`
- `model_name`
- `prompt_version`
- `created_at`

#### `retrieved_incidents`

Stores incidents retrieved for each decision.

Fields:

- `id`
- `triage_decision_id`
- `incident_id`
- `score`
- `rank`
- `matched_text`

#### `external_actions`

Stores side effects published to external systems.

Fields:

- `id`
- `ticket_id`
- `triage_decision_id`
- `system`
- `action_type`
- `status`
- `request_payload`
- `response_payload`
- `error_message`
- `created_at`

#### `audit_events`

Stores business audit trail.

Fields:

- `id`
- `entity_type`
- `entity_id`
- `event_type`
- `actor_type`
- `actor_id`
- `metadata`
- `created_at`

#### `integration_sync_state`

Tracks cursor and sync state for external systems.

Fields:

- `id`
- `integration_name`
- `cursor`
- `last_success_at`
- `last_error`

## 12. AI/RAG Architecture

### 12.1 Retrieval

Input:

- Normalized ticket text.

Output:

- Top historical incidents.
- Similarity scores.
- Key matched text.

Rules:

- Validate non-empty query.
- Limit top results.
- Include source incident IDs.
- Capture retrieval scores.

### 12.2 Triage Decision

The LLM should produce a single structured decision:

- Category.
- Subcategory.
- Resolution.
- Reasoning summary.
- Confidence estimate if supported.
- Escalation recommendation.

The system should combine:

- Vector similarity score.
- LLM output validity.
- Category agreement among top incidents.
- Keyword/rule boosts.
- Business risk policy.

### 12.3 Prompt Versioning

Prompts should be versioned.

Example:

```text
prompt_name: triage_decision
prompt_version: 2026-06-24.v1
```

Every triage decision should save:

- Model name.
- Prompt version.
- Retrieval set.
- Output schema version.

## 13. Decision Policy

The product should not blindly automate every decision.

### 13.1 Confidence Bands

High confidence:

- Auto-suggest resolution.
- Optionally auto-comment if automation is enabled.

Medium confidence:

- Show recommendation to human.
- Require approval before external update.

Low confidence:

- Mark as manual review.
- Do not publish externally.

Example:

```text
>= 0.80: High confidence
0.50 - 0.79: Needs human approval
< 0.50: Manual review required
```

### 13.2 Sensitive Categories

Always require human approval for:

- Security incidents.
- Data loss.
- Privileged access.
- Compliance/regulatory issues.
- Production outage.

## 14. Integration Architecture

### 14.1 Jira

Jira integration should support:

- List issues.
- Get issue details.
- Convert Jira document format to plain text.
- Add AI triage comment.
- Update category/subcategory custom fields if configured.
- Store action result.

It should handle:

- Timeout.
- Non-2xx status.
- Rate limiting.
- Invalid auth.
- Missing fields.

### 14.2 FreeScout

FreeScout integration should support:

- Receive ticket webhook.
- Normalize webhook payload.
- Add ticket note.
- Update ticket fields.
- Save action result.

### 14.3 Outlook/Email

Email integration should support:

- Fetch unread support emails.
- Convert email to internal ticket.
- Track processed message IDs.
- Send resolution email only after approved action.

### 14.4 ServiceNow

ServiceNow integration should support:

- Create incident.
- Sync incident status.
- Link internal ticket to ServiceNow incident ID.

## 15. Frontend Architecture

The frontend should present an operational product, not only a demo dashboard.

Recommended pages:

- Dashboard summary.
- Ticket inbox.
- Triage decision detail.
- Human review queue.
- Jira issues.
- Integration health.
- Agent playground for testing.
- Settings for thresholds and automation mode.

Frontend service modules should match backend API domains:

```text
frontend/src/services/
  apiClient.ts
  triageApi.ts
  ticketApi.ts
  jiraApi.ts
  dashboardApi.ts
  integrationApi.ts
```

## 16. Security And Governance

Required controls:

- No hardcoded credentials.
- Centralized settings validation.
- Secrets via environment variables or secret manager.
- No sensitive payloads in normal logs.
- Auth for production API routes.
- Webhook signature validation where supported.
- Audit logs for AI decisions and side effects.
- Separate demo endpoints from production routes.

## 17. Observability

Add structured logging with fields:

- `request_id`
- `ticket_id`
- `external_source`
- `external_id`
- `triage_decision_id`
- `integration`
- `latency_ms`
- `status`
- `error_type`

Track metrics:

- Tickets processed.
- Average triage latency.
- LLM call latency.
- LLM failure rate.
- Retrieval failure rate.
- Integration failure rate.
- Auto-triage rate.
- Human override rate.
- Low-confidence rate.

## 18. Testing Strategy

### 18.1 Unit Tests

Cover:

- Ticket text normalization.
- Jira document parsing.
- Triage policy thresholds.
- Prompt output parsing.
- Retrieval result ranking.
- Repository methods with test database.

### 18.2 Integration Tests

Cover:

- API route to service flow.
- Database persistence.
- Chroma search with test collection.
- Mocked Jira/FreeScout/Outlook clients.

### 18.3 Contract Tests

Cover:

- Jira client expected payloads.
- FreeScout webhook payloads.
- Triage API request/response schemas.

### 18.4 End-To-End Demo Tests

Cover:

- Create sample ticket.
- Run triage.
- Save decision.
- Display in frontend.
- Mock external comment publication.

## 19. Migration Roadmap

### Phase 1: Repository Hygiene

Goals:

- Stop tracking generated/vendor files.
- Add clean docs.
- Stabilize local development.

Tasks:

- Remove tracked `frontend/node_modules`.
- Remove tracked `frontend/dist` unless static deployment requires it.
- Keep `.env`, DB files, Chroma files ignored.
- Add `.env.example`.
- Move root test scripts into `scripts/` or real `tests/`.

### Phase 2: Split Routes

Goals:

- Make HTTP layer understandable.

Tasks:

- Replace monolithic `backend/routes.py` with route modules.
- Keep backward-compatible endpoint aliases temporarily.
- Convert mutating `GET` endpoints to `POST`.
- Move Jira enrichment and parsing into application/integration modules.

### Phase 3: Centralize Configuration

Goals:

- Remove hardcoded infrastructure values.

Tasks:

- Add `config.py`.
- Replace direct `os.getenv()` calls in business code.
- Move PostgreSQL config to `DATABASE_URL`.
- Validate required settings at startup.

### Phase 4: Create Application Services

Goals:

- Move business workflows out of routes.

Tasks:

- Add `TriageService`.
- Add `JiraTriageService`.
- Add `EmailIntakeService`.
- Add `DashboardService`.
- Make routes call services only.

### Phase 5: Clean AI Workflow

Goals:

- Reduce cost and improve decision consistency.

Tasks:

- Make one LLM call per triage decision.
- Return one structured triage output.
- Persist prompt version, model, and retrieved incidents.
- Add confidence policy.

### Phase 6: Persistence Redesign

Goals:

- Establish source of truth.

Tasks:

- Choose PostgreSQL as primary storage.
- Add migration tool such as Alembic.
- Convert table scripts into migrations.
- Implement repositories.
- Use SQLite only as optional local profile.

### Phase 7: Integration Hardening

Goals:

- Make external systems reliable.

Tasks:

- Add timeouts.
- Add `raise_for_status()`.
- Add typed integration errors.
- Store external action attempts.
- Add retry policy where safe.

### Phase 8: Governance And UI

Goals:

- Make the product enterprise-safe.

Tasks:

- Add human review queue.
- Add automation settings.
- Add audit event viewer.
- Add integration health page.
- Add metrics and structured logs.

## 20. Immediate Refactor Targets In Current Code

### High Priority

- Split `backend/routes.py`.
- Convert `/jira/process-all` from `GET` to `POST`.
- Convert `/jira/process/{issue_key}` from `GET` to `POST`.
- Remove duplicate imports in routes.
- Move Jira description parsing to a utility/mapper.
- Make LangGraph call Azure OpenAI once.
- Replace hardcoded PostgreSQL credentials.
- Add structured logging.

### Medium Priority

- Add service classes.
- Add repository interfaces.
- Add `.env.example`.
- Add integration errors and timeouts.
- Add real tests with assertions.

### Lower Priority

- Improve dashboard metrics.
- Add prompt versioning.
- Add frontend settings page.
- Add incident ingestion admin action.

## 21. Target Definition Of Done

The architecture restructure is complete when:

- Route modules are separated by domain.
- Business logic is in application services.
- Domain rules are testable without FastAPI.
- Integrations are isolated behind clients.
- PostgreSQL is the primary relational store.
- ChromaDB is only the vector index.
- Mutating routes use proper HTTP verbs.
- LLM is called once per triage decision.
- Decisions and external actions are audited.
- Tests validate core workflows.
- Frontend consumes stable domain APIs.

## 22. Final Product Positioning

The strongest business positioning is:

> "An AI-assisted IT support triage platform that converts unstructured support requests into consistent, auditable triage decisions using historical incident retrieval, configurable automation policies, and human approval controls."

This positioning is stronger than simply saying "AI ticket classifier" because it emphasizes:

- Operational reliability.
- Governance.
- Auditability.
- Human control.
- Enterprise workflow integration.

The project should evolve from a demo that proves AI can classify tickets into a product that proves an organization can safely trust AI-assisted triage.
