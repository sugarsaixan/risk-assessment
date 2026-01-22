/**
 * NotFound page for invalid tokens.
 */

import { MN } from "../constants/mn";
import { ThemeToggle } from "../hooks/useTheme";

export function NotFound() {
  return (
    <div className="min-h-screen app-content flex flex-col">
      {/* Header with theme toggle */}
      <div className="absolute top-4 right-4">
        <ThemeToggle />
      </div>

      {/* Content */}
      <div className="flex-1 flex items-center justify-center px-4">
        <div className="surface-card text-center max-w-md p-8">
          {/* Icon */}
          <div className="mx-auto w-20 h-20 rounded-2xl flex items-center justify-center mb-6 bg-[rgba(31,127,114,0.14)]">
            <svg
              className="w-10 h-10 text-[var(--app-accent-2)]"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>

          {/* 404 */}
          <div className="text-6xl font-bold text-[var(--app-border)] mb-4">
            404
          </div>

          {/* Title */}
          <h1 className="text-2xl font-bold font-display mb-3">
            {MN.errors.notFound.title}
          </h1>

          {/* Message */}
          <p className="label-muted text-lg">
            {MN.errors.notFound.message}
          </p>

          {/* Additional info */}
          <p className="mt-6 text-sm label-muted">
            Линк буруу эсвэл хүчингүй байж магадгүй. Линкээ дахин шалгана уу.
          </p>
        </div>
      </div>
    </div>
  );
}

export default NotFound;
