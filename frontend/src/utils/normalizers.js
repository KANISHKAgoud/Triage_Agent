export function normalizeJiraIssues(data) {
  const issues = Array.isArray(data) ? data : data?.issues || [];

  return issues.map((issue) => ({
    key: issue?.key || issue?.issue_key || "—",
    summary: issue?.fields?.summary || issue?.summary || "—",
    status:
      issue?.fields?.status?.name ||
      issue?.status?.name ||
      issue?.status ||
      "Unknown",
  }));
}

export function normalizeIncidents(data) {
  const incidents = Array.isArray(data) ? data : data?.incidents || [];

  return incidents.map((incident) => {
    if (Array.isArray(incident)) {
      return {
        ticketId: incident[1],
        category: incident[2],
        subcategory: incident[3],
        resolution: incident[4],
        createdAt: incident[5],
      };
    }

    return {
      ticketId: incident?.ticket_id || incident?.ticketId,
      category: incident?.category,
      subcategory: incident?.subcategory,
      resolution: incident?.resolution,
      createdAt: incident?.created_at || incident?.createdAt,
    };
  });
}

export function normalizeProcessedTickets(data) {
  const results = Array.isArray(data) ? data : data?.results || [];

  return results.map((item) => ({
    issueKey: item?.issue_key || item?.issueKey || item?.key || "—",
    category: item?.category || item?.predicted_category || "—",
    subcategory: item?.subcategory || item?.predicted_subcategory || "—",
  }));
}

export function normalizeRetrievedIncidents(data) {
  const incidents = data?.retrieved_incidents || [];

  return incidents.map((incident) => ({
    ticketId: incident?.ticket_id || "—",
    issueName: incident?.issue_name || "—",
    category: incident?.category || "—",
    subcategory: incident?.subcategory || "—",
    rootCause: incident?.root_cause || "—",
    score: incident?.score,
    resolution: incident?.resolution || "—",
  }));
}
