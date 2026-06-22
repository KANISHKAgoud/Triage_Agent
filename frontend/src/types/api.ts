export interface DashboardResponse {
  total_tickets: number;
  triaged_tickets: number;
  servicenow_incidents: number;
  vector_documents: number;
  vector_db: string;
  mailbox: string;
}

export interface JiraIssue {
  key?: string;
  issue_key?: string;
  summary?: string;
  status?: string | { name?: string };
  fields?: {
    summary?: string;
    status?: {
      name?: string;
    };
  };
}

export interface JiraIssuesResponse {
  issues?: JiraIssue[];
  count?: number;
}

export interface UnprocessedTicket {
  issue_key: string;
  summary: string;
  status: string;
}

export interface UnprocessedTicketsResponse {
  count: number;
  tickets: UnprocessedTicket[];
}

export interface ProcessTicketResponse {
  issue_key: string;
  category: string;
  subcategory: string;
  resolution: string;
}

export interface ProcessAllTicketsResponse {
  processed: number;
  results: ProcessTicketResponse[];
}

export interface ServiceNowIncident {
  ticket_id?: string;
  ticketId?: string;
  category?: string;
  subcategory?: string;
  resolution?: string;
  created_at?: string;
  createdAt?: string;
}

export interface ServiceNowIncidentsResponse {
  count: number;
  incidents: ServiceNowIncident[] | unknown[][];
}

export interface RetrievedIncident {
  ticket_id: string;
  issue_name: string;
  category: string;
  subcategory: string;
  priority: string;
  department: string;
  status: string;
  score: number;
  symptoms: string;
  root_cause: string;
  resolution: string;
}

export interface AgentResponse {
  status: string;
  query: string;
  session_id: string;
  predicted_category: string;
  predicted_subcategory: string;
  confidence_score: number;
  recommended_resolution: string;
  retrieved_incidents: RetrievedIncident[];
}

export interface ApiErrorResponse {
  detail?: string;
  message?: string;
}
