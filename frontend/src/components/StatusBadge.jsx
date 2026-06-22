const variants = {
  connected: "border-emerald-400/30 bg-emerald-400/10 text-emerald-200",
  healthy: "border-emerald-400/30 bg-emerald-400/10 text-emerald-200",
  done: "border-emerald-400/30 bg-emerald-400/10 text-emerald-200",
  open: "border-sky-400/30 bg-sky-400/10 text-sky-200",
  progress: "border-amber-400/30 bg-amber-400/10 text-amber-200",
  unknown: "border-slate-400/30 bg-slate-400/10 text-slate-200",
};

export default function StatusBadge({ value }) {
  const text = value || "Unknown";
  const key = String(text).toLowerCase();
  const variant =
    variants[key] ||
    (key.includes("done") || key.includes("closed") || key.includes("healthy")
      ? variants.done
      : key.includes("progress") || key.includes("review")
        ? variants.progress
        : key.includes("open") || key.includes("connected")
          ? variants.open
          : variants.unknown);

  return (
    <span className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-medium ${variant}`}>
      {text}
    </span>
  );
}
