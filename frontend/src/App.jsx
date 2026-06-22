import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import AgentPlayground from "./pages/AgentPlayground.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Incidents from "./pages/Incidents.jsx";
import JiraTickets from "./pages/JiraTickets.jsx";
import ProcessTickets from "./pages/ProcessTickets.jsx";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/jira" element={<JiraTickets />} />
        <Route path="/process" element={<ProcessTickets />} />
        <Route path="/incidents" element={<Incidents />} />
        <Route path="/agent" element={<AgentPlayground />} />
      </Route>
    </Routes>
  );
}
