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
          color: "var(--risk-low)",
          tint: "rgba(34, 197, 94, 0.2)",
          badgeClass: "bg-green-500/15 text-green-400 border border-green-500/30",
        };
      case "MEDIUM":
        return {
          label: MN.results.mediumRisk,
          color: "var(--risk-medium)",
          tint: "rgba(245, 158, 11, 0.2)",
          badgeClass: "bg-amber-500/15 text-amber-400 border border-amber-500/30",
        };
      case "HIGH":
        return {
          label: MN.results.highRisk,
          color: "var(--risk-high)",
          tint: "rgba(239, 68, 68, 0.2)",
          badgeClass: "bg-red-500/15 text-red-400 border border-red-500/30",
        };
    }
  };

  const config = getRatingConfig(riskRating);
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const progress = Math.min(percentage, 100);

  return (
    <div
      className={`surface-card p-6 sm:p-8 ${className}`}
      style={{
        background: `linear-gradient(135deg, ${config.tint}, transparent 60%)`,
      }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-base font-medium text-[var(--foreground)]">
          {MN.results.overall}
        </h2>
      </div>

      {/* Score display */}
      <div className="text-center mb-6">
        <div className="text-5xl sm:text-6xl font-bold mb-2" style={{ color: config.color }}>
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
          <svg className="w-full h-full -rotate-90">
            <circle
              cx="64"
              cy="64"
              r={radius}
              stroke="var(--surface-elevated)"
              strokeWidth="8"
              fill="none"
            />
            {/* Progress circle */}
            <circle
              cx="64"
              cy="64"
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
            <span className="text-2xl font-semibold text-[var(--foreground)]">
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
