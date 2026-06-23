import axios, { AxiosError } from "axios";
import type {
  AgentResponse,
  AgentRequest,
  ApiErrorResponse,
  DashboardResponse,
  JiraIssuesResponse,
  ProcessAllTicketsResponse,
  ProcessTicketResponse,
  ServiceNowIncidentsResponse,
  UnprocessedTicketsResponse,
} from "../types/api";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 45000,
});

export function getDashboard(): Promise<DashboardResponse> {
  return api.get<DashboardResponse>("/dashboard").then((response) => response.data);
}

export function getJiraIssues(): Promise<JiraIssuesResponse> {
  return api.get<JiraIssuesResponse>("/jira/issues").then((response) => response.data);
}

export function getJiraIssue(issueKey: string): Promise<import("../types/api").JiraIssue> {
  return api
    .get<import("../types/api").JiraIssue>(`/jira/issue/${encodeURIComponent(issueKey)}`)
    .then((response) => response.data);
}

export function getUnprocessedJiraTickets(): Promise<UnprocessedTicketsResponse> {
  return api.get<UnprocessedTicketsResponse>("/jira/unprocessed").then((response) => response.data);
}

export function processJiraTicket(issueKey: string): Promise<ProcessTicketResponse> {
  return api
    .post<ProcessTicketResponse>(
      `/jira/process-ticket/${encodeURIComponent(issueKey)}`
    )
    .then((response) => response.data);
}

export function processAllJiraTickets(): Promise<ProcessAllTicketsResponse> {
  return api.get<ProcessAllTicketsResponse>("/jira/process-all").then((response) => response.data);
}

export function getServiceNowIncidents(): Promise<ServiceNowIncidentsResponse> {
  return api.get<ServiceNowIncidentsResponse>("/servicenow/incidents").then((response) => response.data);
}

export function runAgent(query: string): Promise<AgentResponse> {
  const payload: AgentRequest = {
    query,
    session_id: "frontend-session",
  };

  return api
    .post<AgentResponse>("/agent/query", payload, {
      timeout: 180000,
    })
    .then((response) => {
      console.log("Agent Playground backend response:", response.data);
      return response.data;
    });
}

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiErrorResponse>;

    return (
      axiosError.response?.data?.detail ||
      axiosError.response?.data?.message ||
      axiosError.message ||
      "Something went wrong while contacting the API."
    );
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Something went wrong while contacting the API.";
}
