import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 45000,
});

export function getDashboard() {
  return api.get("/dashboard").then((response) => response.data);
}

export function getJiraIssues() {
  return api.get("/jira/issues").then((response) => response.data);
}

export function processAllJiraTickets() {
  return api.get("/jira/process-all").then((response) => response.data);
}

export function getServiceNowIncidents() {
  return api.get("/servicenow/incidents").then((response) => response.data);
}

export function runAgent(query) {
  return api
    .post("/agent", {
      search_query: query,
      query,
      session_id: "frontend-session",
    })
    .then((response) => response.data);
}

export function getErrorMessage(error) {
  return (
    error?.response?.data?.detail ||
    error?.response?.data?.message ||
    error?.message ||
    "Something went wrong while contacting the API."
  );
}
