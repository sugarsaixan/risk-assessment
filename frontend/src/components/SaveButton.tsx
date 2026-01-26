/**
 * SaveButton component with loading/success/error states.
 * Manual save trigger for assessment drafts.
 */

import type { AutoSaveStatus } from "../hooks/useAutoSave";

interface SaveButtonProps {
  /** Current auto-save status */
  status: AutoSaveStatus;
  /** Click handler to trigger save */
  onSave: () => void;
  /** Whether save is disabled */
  disabled?: boolean;
}

export function SaveButton({ status, onSave, disabled }: SaveButtonProps) {
  const isSaving = status === "saving";
  const isDisabled = disabled || isSaving;

  return (
    <button
      type="button"
      onClick={onSave}
      disabled={isDisabled}
      className={`inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors
        ${
          status === "error"
            ? "bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/30"
            : status === "saved"
              ? "bg-green-500/10 text-green-400 border border-green-500/30"
              : "bg-[var(--surface-elevated)] text-[var(--foreground)] hover:bg-[var(--surface-hover)] border border-[var(--border)]"
        }
        disabled:opacity-50 disabled:cursor-not-allowed`}
    >
      {/* Icon */}
      {isSaving ? (
        <span className="spinner spinner-sm" />
      ) : status === "saved" ? (
        <svg
          className="h-4 w-4"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <polyline points="20 6 9 17 4 12" />
        </svg>
      ) : status === "error" ? (
        <svg
          className="h-4 w-4"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="12" cy="12" r="10" />
          <line x1="15" y1="9" x2="9" y2="15" />
          <line x1="9" y1="9" x2="15" y2="15" />
        </svg>
      ) : (
        <svg
          className="h-4 w-4"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
          <polyline points="17 21 17 13 7 13 7 21" />
          <polyline points="7 3 7 8 15 8" />
        </svg>
      )}

      {/* Label */}
      <span>
        {isSaving
          ? "Хадгалж байна..."
          : status === "saved"
            ? "Хадгалагдсан"
            : status === "error"
              ? "Дахин оролдох"
              : "Хадгалах"}
      </span>
    </button>
  );
}

export default SaveButton;
