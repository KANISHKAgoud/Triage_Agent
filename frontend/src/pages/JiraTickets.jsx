import { RefreshCw } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import DataTable from "../components/DataTable.jsx";
import ErrorState from "../components/ErrorState.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import PageHeader from "../components/PageHeader.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import { getErrorMessage, getJiraIssues } from "../services/api";
import { normalizeJiraIssues } from "../utils/normalizers.js";

const columns = [
  { key: "key", header: "Issue Key" },
  { key: "summary", header: "Summary" },
  { key: "status", header: "Status", render: (row) => <StatusBadge value={row.status} /> },
];

export default function JiraTickets() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadIssues = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      setRows(normalizeJiraIssues(await getJiraIssues()));
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadIssues();
  }, [loadIssues]);

  return (
    <>
      <PageHeader
        action={
          <button
            className="focus-ring inline-flex items-center gap-2 rounded-md bg-accent-500 px-4 py-2 text-sm font-semibold text-ink-950 transition hover:bg-accent-600 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={loading}
            onClick={loadIssues}
            type="button"
          >
            <RefreshCw className={loading ? "animate-spin" : ""} size={17} />
            Refresh
          </button>
        }
        description="Current Jira issues available for AI triage."
        title="Jira Tickets"
      />
      {loading ? <LoadingSpinner label="Loading Jira tickets" /> : null}
      {!loading && error ? <ErrorState message={error} onRetry={loadIssues} /> : null}
      {!loading && !error ? <DataTable columns={columns} rows={rows} /> : null}
    </>
  );
}
