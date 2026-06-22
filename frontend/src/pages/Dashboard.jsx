import { Database, Inbox, ServerCog, ShieldCheck, Ticket, Workflow } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import ErrorState from "../components/ErrorState.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import PageHeader from "../components/PageHeader.jsx";
import StatCard from "../components/StatCard.jsx";
import { getDashboard, getErrorMessage } from "../services/api";
import { formatNumber } from "../utils/formatters.js";

export default function Dashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      setDashboard(await getDashboard());
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  const cards = [
    { title: "Total Tickets", value: formatNumber(dashboard?.total_tickets), icon: Ticket },
    { title: "Triaged Tickets", value: formatNumber(dashboard?.triaged_tickets), icon: ShieldCheck },
    { title: "ServiceNow Incidents", value: formatNumber(dashboard?.servicenow_incidents), icon: ServerCog },
    { title: "Vector Documents", value: formatNumber(dashboard?.vector_documents), icon: Database },
    { title: "Mailbox Status", value: dashboard?.mailbox || "Unknown", icon: Inbox, status: true },
    { title: "Vector DB Status", value: dashboard?.vector_db || "Unknown", icon: Workflow, status: true },
  ];

  return (
    <>
      <PageHeader
        description="Live health and throughput signals for ticket ingestion, triage, ServiceNow incident creation, and retrieval infrastructure."
        title="Dashboard"
      />
      {loading ? <LoadingSpinner label="Loading dashboard" /> : null}
      {!loading && error ? <ErrorState message={error} onRetry={loadDashboard} /> : null}
      {!loading && !error ? (
        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {cards.map((card) => (
            <StatCard key={card.title} {...card} />
          ))}
        </section>
      ) : null}
    </>
  );
}
