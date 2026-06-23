import { Bot, Send } from "lucide-react";
import { useState } from "react";
import DataTable from "../components/DataTable.jsx";
import ErrorState from "../components/ErrorState.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import PageHeader from "../components/PageHeader.jsx";
import { getErrorMessage, runAgent } from "../services/api";
import { formatPercent, safeValue } from "../utils/formatters.js";
import { normalizeRetrievedIncidents } from "../utils/normalizers.js";

const incidentColumns = [
  { key: "ticketId", header: "Ticket ID" },
  { key: "issueName", header: "Issue" },
  { key: "category", header: "Category" },
  { key: "subcategory", header: "Subcategory" },

  {
    key: "rootCause",
    header: "Root Cause",
    render: (row) => (
      <span className="line-clamp-3">
        {row.rootCause}
      </span>
    ),
  },

  {
    key: "score",
    header: "Score",
    render: (row) => formatPercent(row.score),
  },

  {
    key: "resolution",
    header: "Resolution",
    render: (row) => (
      <span className="line-clamp-3">
        {row.resolution}
      </span>
    ),
  },
];

export default function AgentPlayground() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    if (!query.trim()) {
      setError("Enter a query before running the agent.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      setResult(await runAgent(query.trim()));
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  const retrievedIncidents = result ? normalizeRetrievedIncidents(result) : [];

  return (
    <>
      <PageHeader
        description="Test categorization, subcategorization, confidence, and retrieval output from the AI agent."
        title="AI Agent Playground"
      />

      <section className="grid gap-6 xl:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)]">
        <form className="panel rounded-lg p-5" onSubmit={handleSubmit}>
          <div className="mb-4 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent-500/15 text-accent-500">
              <Bot size={20} />
            </div>
            <div>
              <h2 className="text-base font-semibold text-white">Query Input</h2>
              <p className="text-sm text-slate-400">Session: frontend-session</p>
            </div>
          </div>

          <textarea
            className="focus-ring min-h-48 w-full resize-y rounded-lg border border-white/10 bg-ink-950/80 px-4 py-3 text-sm text-white placeholder:text-slate-500"
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Describe the ticket symptoms, affected service, error messages, and user impact."
            value={query}
          />

          <button
            className="focus-ring mt-4 inline-flex w-full items-center justify-center gap-2 rounded-md bg-accent-500 px-4 py-2.5 text-sm font-semibold text-ink-950 transition hover:bg-accent-600 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={loading}
            type="submit"
          >
            <Send size={17} />
            Run Agent
          </button>
        </form>

        <div className="space-y-4">
          {loading ? <LoadingSpinner label="Running agent" /> : null}
          {!loading && error ? <ErrorState message={error} /> : null}
          {!loading && !error && result ? (
            <>
              <div className="panel rounded-lg p-5">
                <div className="grid gap-4 md:grid-cols-3">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Category</p>
                    <p className="mt-2 text-lg font-semibold text-white">{safeValue(result.predicted_category)}</p>
                  </div>
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Subcategory</p>
                    <p className="mt-2 text-lg font-semibold text-white">{safeValue(result.predicted_subcategory)}</p>
                  </div>

                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                      Confidence Score
                    </p>

                    <p
                      className={`mt-2 text-lg font-semibold ${
                        result.confidence_score >= 0.8
                          ? "text-green-400"
                          : result.confidence_score >= 0.6
                          ? "text-yellow-400"
                          : "text-red-400"
                      }`}
                    >
                      {formatPercent(result.confidence_score)}
                    </p>
                  </div>

                </div>
                <div className="mt-5 border-t border-white/10 pt-5">
                  <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Resolution</p>
                  <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-200">
                    {safeValue(result.recommended_resolution)}
                  </p>
                </div>
              </div>

              <div>
                <h2 className="mb-3 text-base font-semibold text-white">Retrieved Incidents</h2>
                <DataTable columns={incidentColumns} rows={retrievedIncidents} />
              </div>
            </>
          ) : null}
          {!loading && !error && !result ? (
            <div className="panel rounded-lg p-8 text-center text-sm text-slate-400">
              Agent output will appear here after a query runs.
            </div>
          ) : null}
        </div>
      </section>
    </>
  );
}
