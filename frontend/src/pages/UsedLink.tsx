/**
 * UsedLink page showing "Энэ линк аль хэдийн ашиглагдсан байна."
 */

import { MN } from "../constants/mn";
import { ThemeToggle } from "../hooks/useTheme";

export function UsedLink() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header with theme toggle */}
      <div className="absolute top-4 right-4">
        <ThemeToggle />
      </div>

      {/* Content */}
      <div className="flex-1 flex items-center justify-center px-4">
        <div className="surface-card text-center max-w-md p-8">
          {/* Icon */}
          <div className="mx-auto w-20 h-20 rounded-2xl flex items-center justify-center mb-6 border border-[var(--app-border)] bg-[#111113]">
            <svg
              className="w-10 h-10 text-[var(--app-accent)]"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>

          {/* Title */}
          <h1 className="text-2xl font-semibold mb-3">
            {MN.errors.alreadyCompleted.title}
          </h1>

          {/* Message */}
          <p className="label-muted text-lg">
            {MN.errors.alreadyCompleted.message}
          </p>

          {/* Additional info */}
          <p className="mt-6 text-sm label-muted">
            Та үнэлгээг аль хэдийн бөглөсөн байна. Үр дүнг администратораас авна уу.
          </p>
        </div>
      </div>
    </div>
  );
}

export default UsedLink;
