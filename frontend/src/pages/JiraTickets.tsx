import type { ReactNode } from "react";
import { Eye, RefreshCw, X } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import DataTable from "../components/DataTable.jsx";
import ErrorState from "../components/ErrorState.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import PageHeader from "../components/PageHeader.jsx";
import {
  getErrorMessage,
  getJiraIssue,
  getJiraIssues,
  processJiraTicket,
} from "../services/api";

import type { JiraIssue } from "../types/api";
import { formatDate, safeValue } from "../utils/formatters.js";

interface JiraTicketRow {
  key: string;
  summary: string;
  aiStatus: string;
  category: string;
}

function getIssueKey(issue: JiraIssue): string {
  return issue.key || issue.issue_key || "-";
}

function getIssueSummary(issue: JiraIssue): string {
  return issue.summary || issue.fields?.summary || "-";
}

function getIssueCategory(issue: JiraIssue): string {
  return issue.category || "-";
}

function getJiraStatus(issue: JiraIssue): string {
  if (issue.jira_status) {
    return issue.jira_status;
  }

  if (typeof issue.status === "string") {
    return issue.status;
  }

  return issue.status?.name || issue.fields?.status?.name || "-";
}

function getCreatedDate(issue: JiraIssue): string {
  return issue.created_date || issue.fields?.created || "";
}

function getAiStatus(issue: JiraIssue): string {
  if (issue.ai_status) {
    return issue.ai_status;
  }

  return issue.processed ? "Triaged" : "Pending";
}

function normalizeJiraRows(data: { issues?: JiraIssue[] } | JiraIssue[]): JiraTicketRow[] {
  const issues = Array.isArray(data) ? data : data?.issues || [];

  return issues.map((issue) => ({
    key: getIssueKey(issue),
    summary: getIssueSummary(issue),
    aiStatus: getAiStatus(issue),
    category: getIssueCategory(issue),
  }));
}

function AiStatusBadge({ value }: { value: string }) {
  const isTriaged = value.toLowerCase() === "triaged";

  return (
    <span
      className={[
        "inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold",
        isTriaged
          ? "border-emerald-400/30 bg-emerald-400/10 text-emerald-200"
          : "border-amber-400/30 bg-amber-400/10 text-amber-200",
      ].join(" ")}
    >
      {isTriaged ? "Triaged" : "Pending"}
    </span>
  );
}

function TicketDetailsModal({
  issue,
  loading,
  error,
  onClose,
}: {
  issue: JiraIssue | null;
  loading: boolean;
  error: string;
  onClose: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4 py-6">
      <button
        aria-label="Close ticket details"
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
        type="button"
      />
      <section className="panel relative max-h-[88vh] w-full max-w-3xl overflow-hidden rounded-lg">
        <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-accent-500">
              Jira Ticket
            </p>
            <h2 className="mt-1 text-lg font-semibold text-white">
              {issue ? getIssueKey(issue) : "Ticket Details"}
            </h2>
          </div>
          <button
            aria-label="Close"
            className="focus-ring rounded-md p-2 text-slate-300 hover:bg-white/10 hover:text-white"
            onClick={onClose}
            type="button"
          >
            <X size={20} />
          </button>
        </div>

        <div className="max-h-[calc(88vh-73px)] overflow-y-auto p-5">
          {loading ? <LoadingSpinner label="Loading ticket details" /> : null}
          {!loading && error ? <ErrorState message={error} /> : null}
          {!loading && !error && issue ? (
            <div className="space-y-5">
              <div className="grid gap-4 md:grid-cols-2">
                <DetailItem label="Issue Key" value={getIssueKey(issue)} />
                <DetailItem
                  label="Processed Status"
                  value={<AiStatusBadge value={getAiStatus(issue)} />}
                />
                <DetailItem label="Jira Status" value={getJiraStatus(issue)} />
                <DetailItem label="Created Date" value={formatDate(getCreatedDate(issue))} />
                <DetailItem label="Category" value={safeValue(issue.category)} />
                <DetailItem label="Subcategory" value={safeValue(issue.subcategory)} />
              </div>

              <DetailBlock label="Summary" value={getIssueSummary(issue)} />
              <DetailBlock label="Description" value={safeValue(issue.description)} />
              <DetailBlock label="Resolution" value={safeValue(issue.resolution)} />
            </div>
          ) : null}
        </div>
      </section>
    </div>
  );
}

function DetailItem({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/[0.04] p-4">
      <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">{label}</p>
      <div className="mt-2 text-sm font-medium text-white">{value}</div>
    </div>
  );
}

function DetailBlock({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">{label}</p>
      <div className="mt-2 rounded-lg border border-white/10 bg-ink-950/70 p-4 text-sm leading-6 text-slate-200">
        {value}
      </div>
    </div>
  );
}

export default function JiraTickets() {
  const [rows, setRows] = useState<JiraTicketRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [selectedIssue, setSelectedIssue] = useState<JiraIssue | null>(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [detailsError, setDetailsError] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);

  const loadIssues = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      setRows(normalizeJiraRows(await getJiraIssues()));
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadIssues();
  }, [loadIssues]);

  async function handleProcessTicket(issueKey: string) {
  try {
    setProcessing(issueKey);

    await processJiraTicket(issueKey);

    await loadIssues();

    alert(`Ticket ${issueKey} processed successfully`);
  } catch (err) {
    alert(getErrorMessage(err));
  } finally {
    setProcessing(null);
  }
}

  async function handleOpenIssue(issueKey: string) {
    setIsModalOpen(true);
    setSelectedIssue(null);
    setDetailsLoading(true);
    setDetailsError("");

    try {
      setSelectedIssue(await getJiraIssue(issueKey));
    } catch (err) {
      setDetailsError(getErrorMessage(err));
    } finally {
      setDetailsLoading(false);
    }
  }

  const columns = [
    {
      key: "key",
      header: "Issue Key",
      render: (row: JiraTicketRow) => (
        <button
          className="focus-ring rounded text-sm font-semibold text-accent-500 underline-offset-4 hover:text-accent-600 hover:underline"
          onClick={() => handleOpenIssue(row.key)}
          type="button"
        >
          {row.key}
        </button>
      ),
    },
    { key: "summary", header: "Summary" },
    { key: "aiStatus", header: "AI Status", render: (row: JiraTicketRow) => <AiStatusBadge value={row.aiStatus} /> },
    { key: "category", header: "Category" },
    {
  key: "action",
  header: "Action",
  render: (row: JiraTicketRow) => (
    <div className="flex gap-2">

      <button
        className="focus-ring inline-flex items-center gap-2 rounded-md border border-white/10 bg-white/[0.06] px-3 py-2 text-xs font-semibold text-slate-200 hover:bg-white/10"
        onClick={() => handleOpenIssue(row.key)}
        type="button"
      >
        <Eye size={15} />
        View
      </button>

      {row.aiStatus !== "Triaged" && (
        <button
          className="focus-ring rounded-md bg-accent-500 px-3 py-2 text-xs font-semibold text-black hover:bg-accent-600"
          disabled={processing === row.key}
          onClick={() => handleProcessTicket(row.key)}
          type="button"
        >
          {processing === row.key ? "Processing..." : "Process"}
        </button>
      )}

    </div>
  ),
}
  ];

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
        description="Current Jira issues with AI triage status and detected category."
        title="Jira Tickets"
      />
      {loading ? <LoadingSpinner label="Loading Jira tickets" /> : null}
      {!loading && error ? <ErrorState message={error} onRetry={loadIssues} /> : null}
      {!loading && !error ? <DataTable columns={columns} rows={rows} /> : null}

      {isModalOpen ? (
        <TicketDetailsModal
          error={detailsError}
          issue={selectedIssue}
          loading={detailsLoading}
          onClose={() => setIsModalOpen(false)}
        />
      ) : null}
    </>
  );
}
