import { CheckCircle2, Loader2, PlayCircle, RefreshCw, XCircle } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import DataTable from "../components/DataTable.jsx";
import ErrorState from "../components/ErrorState.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import PageHeader from "../components/PageHeader.jsx";
import {
  getErrorMessage,
  getUnprocessedJiraTickets,
  processJiraTicket,
} from "../services/api";
import type { ProcessTicketResponse, UnprocessedTicket } from "../types/api";

type NotificationType = "success" | "error";

interface Notification {
  type: NotificationType;
  message: string;
}

const processedColumns = [
  { key: "issue_key", header: "Issue Key" },
  { key: "category", header: "Category" },
  { key: "subcategory", header: "Subcategory" },
  {
    key: "resolution",
    header: "Resolution",
    render: (row: ProcessTicketResponse) => <span className="line-clamp-3">{row.resolution}</span>,
  },
];

export default function ProcessTickets() {
  const [tickets, setTickets] = useState<UnprocessedTicket[]>([]);
  const [processedResults, setProcessedResults] = useState<ProcessTicketResponse[]>([]);
  const [loadingTickets, setLoadingTickets] = useState(true);
  const [processingKey, setProcessingKey] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [notification, setNotification] = useState<Notification | null>(null);

  const loadUnprocessedTickets = useCallback(async () => {
    setLoadingTickets(true);
    setError("");

    try {
      const data = await getUnprocessedJiraTickets();
      setTickets(data.tickets || []);
      setNotification({
        type: "success",
        message: `Loaded ${data.count ?? data.tickets?.length ?? 0} unprocessed ticket${
          (data.count ?? data.tickets?.length ?? 0) === 1 ? "" : "s"
        }.`,
      });
    } catch (err) {
      const message = getErrorMessage(err);
      setError(message);
      setNotification({ type: "error", message });
    } finally {
      setLoadingTickets(false);
    }
  }, []);

  useEffect(() => {
    loadUnprocessedTickets();
  }, [loadUnprocessedTickets]);

  async function handleProcessTicket(issueKey: string) {
    setProcessingKey(issueKey);
    setError("");
    setNotification(null);

    try {
      const result = await processJiraTicket(issueKey);
      setTickets((currentTickets) => currentTickets.filter((ticket) => ticket.issue_key !== issueKey));
      setProcessedResults((currentResults) => [result, ...currentResults]);
      setNotification({
        type: "success",
        message: `${issueKey} processed successfully.`,
      });
    } catch (err) {
      const message = getErrorMessage(err);
      setError(message);
      setNotification({
        type: "error",
        message: `Failed to process ${issueKey}: ${message}`,
      });
    } finally {
      setProcessingKey(null);
    }
  }

  const unprocessedColumns = [
    { key: "issue_key", header: "Issue Key" },
    { key: "summary", header: "Summary" },
    { key: "status", header: "Status" },
    {
      key: "action",
      header: "Action",
      render: (row: UnprocessedTicket) => {
        const isProcessing = processingKey === row.issue_key;

        return (
          <button
            className="focus-ring inline-flex items-center gap-2 rounded-md border border-accent-500/40 bg-accent-500/10 px-3 py-2 text-xs font-semibold text-accent-500 transition hover:bg-accent-500/20 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={Boolean(processingKey)}
            onClick={() => handleProcessTicket(row.issue_key)}
            type="button"
          >
            {isProcessing ? <Loader2 className="animate-spin" size={15} /> : <PlayCircle size={15} />}
            {isProcessing ? "Processing" : "Process"}
          </button>
        );
      },
    },
  ];

  return (
    <>
      <PageHeader
        action={
          <button
            className="focus-ring inline-flex items-center gap-2 rounded-md bg-accent-500 px-4 py-2 text-sm font-semibold text-ink-950 transition hover:bg-accent-600 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={loadingTickets || Boolean(processingKey)}
            onClick={loadUnprocessedTickets}
            type="button"
          >
            <RefreshCw className={loadingTickets ? "animate-spin" : ""} size={17} />
            Refresh
          </button>
        }
        description="Review unprocessed Jira tickets and triage them one at a time through the AI agent."
        title="Process Tickets"
      />

      {notification ? (
        <div
          className={[
            "mb-4 flex items-start gap-3 rounded-lg border px-4 py-3 text-sm",
            notification.type === "success"
              ? "border-accent-500/25 bg-accent-500/10 text-accent-500"
              : "border-red-400/30 bg-red-500/10 text-red-200",
          ].join(" ")}
        >
          {notification.type === "success" ? (
            <CheckCircle2 className="mt-0.5 shrink-0" size={17} />
          ) : (
            <XCircle className="mt-0.5 shrink-0" size={17} />
          )}
          <span>{notification.message}</span>
        </div>
      ) : null}

      {loadingTickets ? <LoadingSpinner label="Loading unprocessed tickets" /> : null}
      {!loadingTickets && error ? <ErrorState message={error} onRetry={loadUnprocessedTickets} /> : null}
      {!loadingTickets && !error ? (
        <section className="space-y-8">
          <div>
            <div className="mb-3 flex items-center justify-between gap-3">
              <h2 className="text-base font-semibold text-white">Unprocessed Tickets</h2>
              <span className="rounded-full border border-white/10 bg-white/[0.06] px-3 py-1 text-xs font-medium text-slate-300">
                {tickets.length} pending
              </span>
            </div>
            <DataTable
              columns={unprocessedColumns}
              emptyMessage="No unprocessed Jira tickets found."
              rows={tickets}
            />
          </div>

          <div>
            <div className="mb-3 flex items-center justify-between gap-3">
              <h2 className="text-base font-semibold text-white">Processed Results</h2>
              <span className="rounded-full border border-white/10 bg-white/[0.06] px-3 py-1 text-xs font-medium text-slate-300">
                {processedResults.length} processed
              </span>
            </div>
            <DataTable
              columns={processedColumns}
              emptyMessage="Processed ticket results will appear here."
              rows={processedResults}
            />
          </div>
        </section>
      ) : null}
    </>
  );
}
