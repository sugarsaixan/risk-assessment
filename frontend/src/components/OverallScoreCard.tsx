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
          gradient: "linear-gradient(135deg, #1f7f72, #49c7ac)",
          shadow: "rgba(31, 127, 114, 0.35)",
          iconBg: "bg-emerald-400/30",
        };
      case "MEDIUM":
        return {
          label: MN.results.mediumRisk,
          gradient: "linear-gradient(135deg, #c8942f, #e5b454)",
          shadow: "rgba(200, 148, 47, 0.35)",
          iconBg: "bg-amber-300/30",
        };
      case "HIGH":
        return {
          label: MN.results.highRisk,
          gradient: "linear-gradient(135deg, #d06138, #f08a43)",
          shadow: "rgba(208, 97, 56, 0.4)",
          iconBg: "bg-orange-300/30",
        };
    }
  };

  const config = getRatingConfig(riskRating);

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
      className={`rounded-2xl p-6 text-white ${className}`}
      style={{
        background: config.gradient,
        boxShadow: `0 24px 50px ${config.shadow}`,
      }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold">{MN.results.overall}</h2>
        <div className={`p-2 rounded-full ${config.iconBg} text-white`}>
          {getIcon(riskRating)}
        </div>
      </div>

      {/* Score display */}
      <div className="text-center mb-6">
        <div className="text-5xl font-bold mb-2">{percentage.toFixed(1)}%</div>
        <div className="text-white/80">
          {rawScore} / {maxScore} {MN.results.score}
        </div>
      </div>

      {/* Progress ring (circular) */}
      <div className="flex justify-center mb-6">
        <div className="relative w-32 h-32">
          {/* Background circle */}
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="64"
              cy="64"
              r="56"
              stroke="currentColor"
              strokeWidth="12"
              fill="none"
              className="text-white/20"
            />
            {/* Progress circle */}
            <circle
              cx="64"
              cy="64"
              r="56"
              stroke="currentColor"
              strokeWidth="12"
              fill="none"
              strokeLinecap="round"
              className="text-white"
              strokeDasharray={`${(percentage / 100) * 351.86} 351.86`}
              style={{
                transition: "stroke-dasharray 1s ease-out",
              }}
            />
          </svg>
          {/* Center percentage */}
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-2xl font-bold">{Math.round(percentage)}%</span>
          </div>
        </div>
      </div>

      {/* Risk rating */}
      <div className="text-center">
        <span className="text-sm text-white/70">{MN.results.riskLevel}</span>
        <div className="mt-1 inline-flex items-center px-4 py-2 rounded-full bg-white/20 backdrop-blur-sm">
          <span className="font-semibold">{config.label}</span>
        </div>
      </div>
    </div>
  );
}

export default OverallScoreCard;
