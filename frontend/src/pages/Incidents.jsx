import { useCallback, useEffect, useState } from "react";
import DataTable from "../components/DataTable.jsx";
import ErrorState from "../components/ErrorState.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import PageHeader from "../components/PageHeader.jsx";
import { getErrorMessage, getServiceNowIncidents } from "../services/api.js";
import { formatDate, safeValue } from "../utils/formatters.js";
import { normalizeIncidents } from "../utils/normalizers.js";

const columns = [
  { key: "ticketId", header: "Ticket ID", render: (row) => safeValue(row.ticketId) },
  { key: "category", header: "Category", render: (row) => safeValue(row.category) },
  { key: "subcategory", header: "Subcategory", render: (row) => safeValue(row.subcategory) },
  { key: "resolution", header: "Resolution", render: (row) => <span className="line-clamp-3">{safeValue(row.resolution)}</span> },
  { key: "createdAt", header: "Created At", render: (row) => formatDate(row.createdAt) },
];

export default function Incidents() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadIncidents = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      setRows(normalizeIncidents(await getServiceNowIncidents()));
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadIncidents();
  }, [loadIncidents]);

  return (
    <>
      <PageHeader
        description="ServiceNow incidents created from AI triage decisions."
        title="ServiceNow Incidents"
      />
      {loading ? <LoadingSpinner label="Loading incidents" /> : null}
      {!loading && error ? <ErrorState message={error} onRetry={loadIncidents} /> : null}
      {!loading && !error ? <DataTable columns={columns} rows={rows} /> : null}
    </>
  );
}
