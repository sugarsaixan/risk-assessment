/**
 * OverallScoreCard component for displaying overall assessment result.
 */

import { MN } from "../constants/mn";
import type { RiskRating } from "../types/api";

interface OverallScoreCardProps {
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

export function OverallScoreCard({
  rawScore,
  maxScore,
  percentage,
  riskRating,
  className = "",
}: OverallScoreCardProps) {
  const getRatingConfig = (rating: RiskRating) => {
    switch (rating) {
      case "LOW":
        return {
          label: MN.results.lowRisk,
          color: "#22c55e",
          badgeClass: "bg-green-500/15 text-green-400 border border-green-500/30",
        };
      case "MEDIUM":
        return {
          label: MN.results.mediumRisk,
          color: "#f59e0b",
          badgeClass: "bg-amber-500/15 text-amber-400 border border-amber-500/30",
        };
      case "HIGH":
        return {
          label: MN.results.highRisk,
          color: "#ef4444",
          badgeClass: "bg-red-500/15 text-red-400 border border-red-500/30",
        };
    }
  };

  const config = getRatingConfig(riskRating);
  const radius = 62;
  const circumference = 2 * Math.PI * radius;
  const progress = Math.min(percentage, 100);

  // Get icon based on rating
  const getIcon = (rating: RiskRating) => {
    switch (rating) {
      case "LOW":
        return (
          <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case "MEDIUM":
        return (
          <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        );
      case "HIGH":
        return (
          <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  return (
    <div
      className={`surface-card p-6 ${className}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-medium text-[var(--app-ink)]">{MN.results.overall}</h2>
        <div className="p-2 rounded-full border border-[var(--app-border)] bg-[#111113] text-[var(--app-ink)]">
          {getIcon(riskRating)}
        </div>
      </div>

      {/* Score display */}
      <div className="text-center mb-6">
        <div className="text-5xl sm:text-6xl font-bold text-[var(--app-ink)] mb-2">
          {percentage.toFixed(1)}%
        </div>
        <div className="text-sm label-muted">
          {rawScore} / {maxScore} {MN.results.score}
        </div>
      </div>

      {/* Progress ring (circular) */}
      <div className="flex justify-center mb-6">
        <div className="relative w-[140px] h-[140px]">
          {/* Background circle */}
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="70"
              cy="70"
              r={radius}
              stroke="#27272a"
              strokeWidth="8"
              fill="none"
            />
            {/* Progress circle */}
            <circle
              cx="70"
              cy="70"
              r={radius}
              stroke={config.color}
              strokeWidth="8"
              fill="none"
              strokeLinecap="round"
              strokeDasharray={`${(progress / 100) * circumference} ${circumference}`}
              style={{
                transition: "stroke-dasharray 1s ease-out",
              }}
            />
          </svg>
          {/* Center percentage */}
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-2xl font-bold text-[var(--app-ink)]">
              {Math.round(percentage)}%
            </span>
          </div>
        </div>
      </div>

      {/* Risk rating */}
      <div className="text-center space-y-2">
        <span className="text-sm label-muted">{MN.results.riskLevel}</span>
        <div className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium ${config.badgeClass}`}>
          {config.label}
        </div>
      </div>
    </div>
  );
}

export default OverallScoreCard;
