import StatusBadge from "./StatusBadge.jsx";

export default function StatCard({ title, value, icon: Icon, status }) {
  return (
    <div className="panel rounded-lg p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-slate-400">{title}</p>
          <div className="mt-3 text-3xl font-semibold text-white">{status ? <StatusBadge value={value} /> : value}</div>
        </div>
        {Icon ? (
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-white/10 text-accent-500">
            <Icon size={22} />
          </div>
        ) : null}
      </div>
    </div>
  );
}
