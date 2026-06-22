import {
  Bot,
  Gauge,
  GitPullRequestArrow,
  Menu,
  RefreshCw,
  ServerCog,
  Ticket,
  X,
} from "lucide-react";
import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";

const navItems = [
  { label: "Dashboard", to: "/dashboard", icon: Gauge },
  { label: "Jira Tickets", to: "/jira", icon: Ticket },
  { label: "Process Tickets", to: "/process", icon: RefreshCw },
  { label: "Incidents", to: "/incidents", icon: ServerCog },
  { label: "Agent Playground", to: "/agent", icon: Bot },
];

function SidebarContent({ onNavigate }) {
  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-white/10 px-5 py-5">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent-500 text-ink-950">
            <GitPullRequestArrow size={22} />
          </div>
          <div>
            <p className="text-sm font-semibold text-white">Triage Agent</p>
            <p className="text-xs text-slate-400">ITSM Operations Console</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-5">
        {navItems.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              className={({ isActive }) =>
                [
                  "flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition",
                  isActive
                    ? "bg-accent-500/15 text-accent-500"
                    : "text-slate-300 hover:bg-white/[0.06] hover:text-white",
                ].join(" ")
              }
              key={item.to}
              onClick={onNavigate}
              to={item.to}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="border-t border-white/10 px-5 py-4">
        <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Backend</p>
        <p className="mt-1 text-sm text-slate-300">localhost:8000</p>
      </div>
    </div>
  );
}

export default function Layout() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="min-h-screen">
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-72 border-r border-white/10 bg-ink-900/90 backdrop-blur-xl lg:block">
        <SidebarContent />
      </aside>

      {isOpen ? (
        <div className="fixed inset-0 z-50 lg:hidden">
          <button
            aria-label="Close navigation"
            className="absolute inset-0 bg-black/60"
            onClick={() => setIsOpen(false)}
            type="button"
          />
          <aside className="relative h-full w-72 border-r border-white/10 bg-ink-900 shadow-panel">
            <button
              aria-label="Close navigation"
              className="focus-ring absolute right-3 top-3 rounded-md p-2 text-slate-300 hover:bg-white/10 hover:text-white"
              onClick={() => setIsOpen(false)}
              type="button"
            >
              <X size={20} />
            </button>
            <SidebarContent onNavigate={() => setIsOpen(false)} />
          </aside>
        </div>
      ) : null}

      <div className="lg:pl-72">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-white/10 bg-ink-950/75 px-4 backdrop-blur-xl lg:hidden">
          <button
            aria-label="Open navigation"
            className="focus-ring rounded-md p-2 text-slate-300 hover:bg-white/10 hover:text-white"
            onClick={() => setIsOpen(true)}
            type="button"
          >
            <Menu size={22} />
          </button>
          <span className="text-sm font-semibold text-white">Triage Agent</span>
          <span className="h-9 w-9" />
        </header>

        <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
