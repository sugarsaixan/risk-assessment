/**
 * Main application component with route configuration.
 */

import { Routes, Route } from "react-router-dom";

import { AssessmentForm } from "./pages/AssessmentForm";
import { ExpiredLink } from "./pages/ExpiredLink";
import { NotFound } from "./pages/NotFound";
import { Results } from "./pages/Results";
import { UsedLink } from "./pages/UsedLink";

function App() {
  return (
    <div className="min-h-screen app-shell">
      <Routes>
        {/* Public assessment routes */}
        <Route path="/a/:token" element={<AssessmentForm />} />
        <Route path="/a/:token/results" element={<Results />} />

        {/* Error pages */}
        <Route path="/expired" element={<ExpiredLink />} />
        <Route path="/used" element={<UsedLink />} />
        <Route path="/not-found" element={<NotFound />} />

        {/* Home - redirect to not found or show info */}
        <Route path="/" element={<Home />} />

        {/* Catch-all for invalid routes */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </div>
  );
}

/**
 * Home page component - simple landing/info page.
 */
function Home() {
  return (
    <div className="app-content flex items-center justify-center min-h-screen px-4 py-10">
      <div className="surface-card max-w-lg w-full p-8 sm:p-10 text-center">
        <div className="mx-auto w-16 h-16 rounded-2xl flex items-center justify-center mb-6 bg-[rgba(208,97,56,0.14)]">
          <svg
            className="w-8 h-8 text-[var(--app-accent)]"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        </div>

        <div className="pill mx-auto mb-4">
          Эрсдэлийн үнэлгээ
        </div>

        <h1 className="text-3xl sm:text-4xl font-bold mb-4 font-display">
          Эрсдэлийн үнэлгээний систем
        </h1>

        <p className="label-muted mb-6 text-sm sm:text-base">
          Risk Assessment Survey System
        </p>

        <div className="divider-line my-6" />

        <p className="text-sm label-muted">
          Үнэлгээ бөглөхийн тулд танд илгээсэн линкийг ашиглана уу.
        </p>
      </div>
    </div>
  );
}

export default App;
