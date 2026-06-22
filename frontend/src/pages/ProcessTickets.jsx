import { PlayCircle } from "lucide-react";
import { useState } from "react";
import DataTable from "../components/DataTable.jsx";
import ErrorState from "../components/ErrorState.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import PageHeader from "../components/PageHeader.jsx";
import { getErrorMessage, processAllJiraTickets } from "../services/api.js";
import { normalizeProcessedTickets } from "../utils/normalizers.js";

const columns = [
  { key: "issueKey", header: "Issue Key" },
  { key: "category", header: "Category" },
  { key: "subcategory", header: "Subcategory" },
];

export default function ProcessTickets() {
  const [rows, setRows] = useState([]);
  const [processed, setProcessed] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleProcessTickets() {
    setLoading(true);
    setError("");

    try {
      const data = await processAllJiraTickets();
      setRows(normalizeProcessedTickets(data));
      setProcessed(data?.processed ?? normalizeProcessedTickets(data).length);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <PageHeader
        action={
          <button
            className="focus-ring inline-flex items-center gap-2 rounded-md bg-accent-500 px-4 py-2 text-sm font-semibold text-ink-950 transition hover:bg-accent-600 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={loading}
            onClick={handleProcessTickets}
            type="button"
          >
            <PlayCircle size={18} />
            Process New Tickets
          </button>
        }
        description="Run Jira issues through the AI agent and write the classification back to Jira."
        title="Process Tickets"
      />

      {loading ? <LoadingSpinner label="Processing Jira tickets" /> : null}
      {!loading && error ? <ErrorState message={error} onRetry={handleProcessTickets} /> : null}
      {!loading && !error && processed !== null ? (
        <div className="mb-4 rounded-lg border border-accent-500/25 bg-accent-500/10 px-4 py-3 text-sm text-accent-500">
          Processed {processed} ticket{processed === 1 ? "" : "s"}.
        </div>
      ) : null}
      {!loading && !error ? (
        <DataTable columns={columns} emptyMessage="No processed tickets yet." rows={rows} />
      ) : null}
    </>
  );
}
