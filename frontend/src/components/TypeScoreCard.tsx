/**
 * TypeScoreCard component for displaying per-type results.
 */

import { MN } from "../constants/mn";
import type { RiskRating } from "../types/api";

interface TypeScoreCardProps {
  /** Questionnaire type name */
  typeName: string;
  /** Raw score achieved */
  rawScore: number;
  /** Maximum possible score */
  maxScore: number;
  /** Score percentage */
  percentage: number;
  /** Risk rating */
  riskRating: RiskRating;
  /** Optional CSS class names */
  className?: string;
}

export function TypeScoreCard({
  typeName,
  rawScore,
  maxScore,
  percentage,
  riskRating,
  className = "",
}: TypeScoreCardProps) {
  const getRatingConfig = (rating: RiskRating) => {
    switch (rating) {
      case "LOW":
        return {
          label: MN.results.lowRisk,
          textColor: "text-green-400",
          borderColor: "rgba(34, 197, 94, 0.4)",
          progressColor: "bg-green-500",
        };
      case "MEDIUM":
        return {
          label: MN.results.mediumRisk,
          textColor: "text-amber-400",
          borderColor: "rgba(245, 158, 11, 0.4)",
          progressColor: "bg-amber-500",
        };
      case "HIGH":
        return {
          label: MN.results.highRisk,
          textColor: "text-red-400",
          borderColor: "rgba(239, 68, 68, 0.4)",
          progressColor: "bg-red-500",
        };
    }
  };

  const config = getRatingConfig(riskRating);

  return (
    <div
      className={`surface-card p-4 border border-[var(--border)] border-l-4 ${className}`}
      style={{ borderLeftColor: config.borderColor }}
    >
      {/* Type name */}
      <h3 className="text-sm font-medium mb-3 text-[var(--foreground)]">{typeName}</h3>

      {/* Score display */}
      <div className="flex items-end justify-between mb-3">
        <div>
          <span className="text-2xl font-bold text-[var(--foreground)]">
            {rawScore}
          </span>
          <span className="label-muted ml-1">/ {maxScore}</span>
        </div>
        <span className="text-lg font-semibold text-[var(--foreground)]">
          {percentage.toFixed(1)}%
        </span>
      </div>

      {/* Progress bar */}
      <div className="progress-track mb-3">
        <div
          className={`h-full ${config.progressColor} rounded-full transition-all duration-500`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>

      {/* Risk rating badge */}
      <div className="flex justify-between items-center">
        <span className="text-sm label-muted">
          {MN.results.riskLevel}:
        </span>
        <span
          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-sm font-medium border ${config.textColor}`}
          style={{ borderColor: config.borderColor }}
        >
          {config.label}
        </span>
      </div>
    </div>
  );
}

export default TypeScoreCard;
