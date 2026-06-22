export default function LoadingSpinner({ label = "Loading" }) {
  return (
    <div className="flex min-h-32 items-center justify-center gap-3 text-sm text-slate-300">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-slate-600 border-t-accent-500" />
      <span>{label}</span>
    </div>
  );
}
