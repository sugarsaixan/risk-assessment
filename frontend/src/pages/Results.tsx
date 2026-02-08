/**
 * Results page displaying type scores with group breakdown and overall score with risk ratings.
 */

import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";

import { AnswersSection } from "../components/AnswersSection";
import { OverallScoreCard } from "../components/OverallScoreCard";
import { TypeScoreCard } from "../components/TypeScoreCard";
import { MN } from "../constants/mn";
import { ThemeToggle } from "../hooks/useTheme";
import { getAssessmentResults } from "../services/assessment";
import type { SubmitResponse } from "../types/api";

export function Results() {
  const { token } = useParams<{ token: string }>();
  const location = useLocation();
  const navigate = useNavigate();

  // Get results from navigation state (if coming from submit)
  const stateResults = location.state?.results as SubmitResponse | undefined;

  // State for fetched results
  const [results, setResults] = useState<SubmitResponse | undefined>(stateResults);
  const [isLoading, setIsLoading] = useState(!stateResults);
  const [error, setError] = useState<string | null>(null);

  // Fetch results if not available from state
  useEffect(() => {
    if (stateResults || !token) return;

    async function fetchResults() {
      setIsLoading(true);
      setError(null);

      const result = await getAssessmentResults(token!);

      if (result.success) {
        setResults(result.data);
      } else {
        setError(result.message);
      }

      setIsLoading(false);
    }

    fetchResults();
  }, [token, stateResults]);

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="surface-card p-8 text-center max-w-md">
          <span className="spinner spinner-lg mx-auto mb-4" />
          <p className="label-muted">Уншиж байна...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !results) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="surface-card p-8 text-center max-w-md">
          <p className="label-muted mb-4">
            {error || MN.errors.notFound.message}
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
            totalRisk={overall_result.total_risk}
            totalGrade={overall_result.total_grade}
            riskDescription={overall_result.risk_description}
            insuranceDecision={overall_result.insurance_decision}
          />
        </div>

        {/* Type Results with Group Breakdown */}
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
                  groups={result.groups}
                  probabilityScore={result.probability_score}
                  consequenceScore={result.consequence_score}
                  riskValue={result.risk_value}
                  riskGrade={result.risk_grade}
                  riskDescription={result.risk_description}
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
            {overall_result.total_grade != null ? (
              <>
                {/* New scoring display */}
                <div className="flex justify-between p-4">
                  <span className="label-muted">Нийт зэрэглэл</span>
                  <span className="font-medium text-[var(--foreground)]">
                    {overall_result.total_grade}
                  </span>
                </div>
                <div className="flex justify-between p-4">
                  <span className="label-muted">Нийт эрсдэл</span>
                  <span className="font-medium text-[var(--foreground)]">
                    {overall_result.total_risk}
                  </span>
                </div>
                {overall_result.risk_description && (
                  <div className="flex justify-between p-4">
                    <span className="label-muted">Тайлбар</span>
                    <span className="font-medium text-[var(--foreground)]">
                      {overall_result.risk_description}
                    </span>
                  </div>
                )}
                {overall_result.insurance_decision && (
                  <div className="flex justify-between p-4">
                    <span className="label-muted">Даатгах эсэх</span>
                    <span
                      className={`font-medium ${
                        overall_result.insurance_decision === "Даатгана"
                          ? "text-green-400"
                          : "text-red-400"
                      }`}
                    >
                      {overall_result.insurance_decision}
                    </span>
                  </div>
                )}
              </>
            ) : (
              <>
                {/* Legacy scoring display */}
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
              </>
            )}
          </div>
        </div>

        {/* Answers Section */}
        {results.answer_breakdown && results.answer_breakdown.length > 0 && (
          <div className="mt-8">
            <AnswersSection answers={results.answer_breakdown} />
          </div>
        )}

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
