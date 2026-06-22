import { AlertTriangle } from "lucide-react";

export default function ErrorState({ message, onRetry }) {
  return (
    <div className="panel rounded-lg p-5">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-red-500/15 text-red-300">
            <AlertTriangle size={20} />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-red-100">Request failed</h2>
            <p className="mt-1 text-sm text-slate-300">{message}</p>
          </div>
        </div>
        {onRetry ? (
          <button
            className="focus-ring rounded-md border border-white/10 bg-white/10 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/15"
            onClick={onRetry}
            type="button"
          >
            Retry
          </button>
        ) : null}
      </div>
    </div>
  );
}
