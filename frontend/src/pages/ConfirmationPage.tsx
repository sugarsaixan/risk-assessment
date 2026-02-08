/**
 * ConfirmationPage - displays acknowledgment message after survey submission.
 * Shows "Таны хүсэлтийг хүлээж авлаа" (Your request has been received).
 * No navigation elements, reference numbers, or follow-up information per spec.
 */

import { ThemeToggle } from "../hooks/useTheme";

export function ConfirmationPage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header with theme toggle */}
      <div className="absolute top-4 right-4">
        <ThemeToggle />
      </div>

      {/* Content */}
      <div className="flex-1 flex items-center justify-center px-4">
        <div className="surface-card text-center max-w-md p-8">
          {/* Icon - checkmark to indicate success */}
          <div className="mx-auto w-20 h-20 rounded-2xl flex items-center justify-center mb-6 border border-[var(--border)] bg-[var(--surface-elevated)]">
            <svg
              className="w-10 h-10 text-[var(--primary)]"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>

          {/* Message */}
          <h1 className="text-2xl font-semibold">
            Таны хүсэлтийг хүлээж авлаа
          </h1>
        </div>
      </div>
    </div>
  );
}

export default ConfirmationPage;
