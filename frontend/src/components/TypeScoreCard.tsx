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
          tint: "rgba(31, 127, 114, 0.12)",
          textColor: "text-emerald-700",
          borderColor: "rgba(31, 127, 114, 0.35)",
          progressColor: "bg-emerald-500",
        };
      case "MEDIUM":
        return {
          label: MN.results.mediumRisk,
          tint: "rgba(200, 148, 47, 0.12)",
          textColor: "text-amber-700",
          borderColor: "rgba(200, 148, 47, 0.35)",
          progressColor: "bg-amber-500",
        };
      case "HIGH":
        return {
          label: MN.results.highRisk,
          tint: "rgba(208, 97, 56, 0.12)",
          textColor: "text-orange-700",
          borderColor: "rgba(208, 97, 56, 0.35)",
          progressColor: "bg-orange-500",
        };
    }
  };

  const config = getRatingConfig(riskRating);

  return (
    <div
      className={`surface-card p-4 border-l-4 ${className}`}
      style={{
        borderColor: config.borderColor,
        borderLeftColor: config.borderColor,
      }}
    >
      {/* Type name */}
      <h3 className="font-medium mb-3">{typeName}</h3>

      {/* Score display */}
      <div className="flex items-end justify-between mb-3">
        <div>
          <span className="text-2xl font-bold">
            {rawScore}
          </span>
          <span className="label-muted ml-1">/ {maxScore}</span>
        </div>
        <span className="text-xl font-semibold">
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
          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-sm font-medium ${config.textColor}`}
          style={{ background: config.tint }}
        >
          {config.label}
        </span>
      </div>
    </div>
  );
}

export default TypeScoreCard;
