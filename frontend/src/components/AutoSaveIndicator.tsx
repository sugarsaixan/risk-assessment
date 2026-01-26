/**
 * AutoSaveIndicator component showing save status.
 * Displays: Хадгалагдсан (saved) / Хадгалж байна (saving) / error state.
 */

import type { AutoSaveStatus } from "../hooks/useAutoSave";

interface AutoSaveIndicatorProps {
  /** Current auto-save status */
  status: AutoSaveStatus;
  /** Last saved timestamp (ISO string) */
  lastSavedAt: string | null;
  /** Error message if save failed */
  error: string | null;
}

/**
 * Format a timestamp to relative time in Mongolian.
 */
function formatRelativeTime(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);

  if (diffSec < 10) return "Саяхан";
  if (diffSec < 60) return `${diffSec} секундын өмнө`;
  if (diffMin < 60) return `${diffMin} минутын өмнө`;

  return date.toLocaleTimeString("mn-MN", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function AutoSaveIndicator({
  status,
  lastSavedAt,
  error,
}: AutoSaveIndicatorProps) {
  // Don't show anything if never saved and idle
  if (status === "idle" && !lastSavedAt) return null;

  return (
    <div className="flex items-center gap-2 text-xs">
      {status === "saving" && (
        <>
          <span className="spinner spinner-xs" />
          <span className="label-muted">Хадгалж байна...</span>
        </>
      )}

      {status === "saved" && (
        <>
          <svg
            className="h-3.5 w-3.5 text-green-400"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polyline points="20 6 9 17 4 12" />
          </svg>
          <span className="text-green-400">Хадгалагдсан</span>
        </>
      )}

      {status === "error" && (
        <>
          <svg
            className="h-3.5 w-3.5 text-red-400"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <span className="text-red-400">
            {error || "Хадгалж чадсангүй"}
          </span>
        </>
      )}

      {status === "idle" && lastSavedAt && (
        <span className="label-muted">
          Хадгалагдсан: {formatRelativeTime(lastSavedAt)}
        </span>
      )}
    </div>
  );
}

export default AutoSaveIndicator;
