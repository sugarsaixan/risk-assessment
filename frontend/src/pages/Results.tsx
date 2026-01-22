/**
 * Results page displaying type scores and overall score with risk ratings.
 */

import { useLocation, useNavigate, useParams } from "react-router-dom";

import { OverallScoreCard } from "../components/OverallScoreCard";
import { TypeScoreCard } from "../components/TypeScoreCard";
import { MN } from "../constants/mn";
import { ThemeToggle } from "../hooks/useTheme";
import type { SubmitResponse } from "../types/api";

export function Results() {
  const { token } = useParams<{ token: string }>();
  const location = useLocation();
  const navigate = useNavigate();

  // Get results from navigation state
  const results = location.state?.results as SubmitResponse | undefined;

  // If no results in state, redirect to form
  if (!results) {
    // Could redirect to form, but for now show error
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="surface-card p-8 text-center max-w-md">
          <p className="label-muted mb-4">
            {MN.errors.notFound.message}
          </p>
          <button
            onClick={() => navigate(`/a/${token}`)}
            className="btn-ghost"
          >
            {MN.cancel}
          </button>
        </div>
      </div>
    );
  }

  const { type_results, overall_result } = results;

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="container-app">
        {/* Header */}
        <div className="surface-card p-6 sm:p-8 mb-8">
          <div className="flex justify-between items-start gap-4">
            <div>
              <div className="pill mb-4">
                <svg
                  className="h-3.5 w-3.5"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M12 3l8 4v5c0 5-3.5 9-8 9s-8-4-8-9V7l8-4z" />
                </svg>
                {MN.results.title}
              </div>
              <h1 className="text-2xl sm:text-3xl font-semibold">
                {MN.results.title}
              </h1>
              <p className="mt-2 text-sm label-muted">
                {MN.results.completedAt}: {new Date().toLocaleDateString("mn-MN")}
              </p>
            </div>
            <ThemeToggle />
          </div>
        </div>

        {/* Overall Score Card - Featured */}
        <div className="mb-8">
          <OverallScoreCard
            rawScore={overall_result.raw_score}
            maxScore={overall_result.max_score}
            percentage={overall_result.percentage}
            riskRating={overall_result.risk_rating}
          />
        </div>

        {/* Type Results */}
        {type_results.length > 0 && (
          <div>
            <h2 className="text-lg font-medium mb-4">
              {MN.results.typeResults}
            </h2>

            <div className="grid gap-4 sm:grid-cols-2">
              {type_results.map((result) => (
                <TypeScoreCard
                  key={result.type_id}
                  typeName={result.type_name}
                  rawScore={result.raw_score}
                  maxScore={result.max_score}
                  percentage={result.percentage}
                  riskRating={result.risk_rating}
                />
              ))}
            </div>
          </div>
        )}

        {/* Summary Section */}
        <div className="mt-8 surface-card">
          <div className="border-b border-[var(--border)] p-4">
            <h3 className="text-base font-medium text-[var(--foreground)]">
              {MN.results.overall}
            </h3>
          </div>
          <div className="divide-y divide-[var(--border)] text-sm">
            <div className="flex justify-between p-4">
              <span className="label-muted">{MN.results.score}</span>
              <span className="font-medium text-[var(--foreground)]">
                {overall_result.raw_score} / {overall_result.max_score}
              </span>
            </div>
            <div className="flex justify-between p-4">
              <span className="label-muted">{MN.results.percentage}</span>
              <span className="font-medium text-[var(--foreground)]">
                {overall_result.percentage.toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between p-4">
              <span className="label-muted">{MN.results.riskLevel}</span>
              <span
                className={`font-medium ${
                  overall_result.risk_rating === "LOW"
                    ? "text-green-400"
                    : overall_result.risk_rating === "MEDIUM"
                    ? "text-amber-400"
                    : "text-red-400"
                }`}
              >
                {MN.riskRating[overall_result.risk_rating]}
              </span>
            </div>
          </div>
        </div>

        {/* Print / Close note */}
        <div className="mt-8 text-center text-sm label-muted">
          <p>
            Энэ хуудсыг хэвлэх эсвэл дэлгэцийн зураг авч хадгалаарай.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Results;
