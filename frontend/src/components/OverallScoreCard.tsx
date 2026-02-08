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
  /** Total risk value (НИЙТ ЭРСДЭЛ) */
  totalRisk?: number | undefined;
  /** Total grade (НИЙТ ЗЭРЭГЛЭЛ) */
  totalGrade?: string | undefined;
  /** Mongolian risk description */
  riskDescription?: string | undefined;
  /** Insurance decision (ДААТГАХ ЭСЭХ) */
  insuranceDecision?: string | undefined;
  /** Optional CSS class names */
  className?: string;
}

function getGradeColor(grade: string | undefined) {
  if (!grade) return null;
  if (["AAA", "AA", "A"].includes(grade))
    return { bg: "bg-green-500/15", text: "text-green-400", border: "border-green-500/30", color: "rgba(34, 197, 94, 0.8)" };
  if (["BBB", "BB", "B"].includes(grade))
    return { bg: "bg-yellow-500/15", text: "text-yellow-400", border: "border-yellow-500/30", color: "rgba(234, 179, 8, 0.8)" };
  if (["CCC", "CC", "C"].includes(grade))
    return { bg: "bg-orange-500/15", text: "text-orange-400", border: "border-orange-500/30", color: "rgba(249, 115, 22, 0.8)" };
  if (["DDD", "DD", "D"].includes(grade))
    return { bg: "bg-red-500/15", text: "text-red-400", border: "border-red-500/30", color: "rgba(239, 68, 68, 0.8)" };
  return null;
}

export function OverallScoreCard({
  rawScore,
  maxScore,
  percentage,
  riskRating,
  totalRisk,
  totalGrade,
  riskDescription,
  insuranceDecision,
  className = "",
}: OverallScoreCardProps) {
  const getRatingConfig = (rating: RiskRating) => {
    switch (rating) {
      case "LOW":
        return {
          label: MN.results.lowRisk,
          color: "var(--risk-low)",
          tintStrong: "rgba(34, 197, 94, 0.2)",
          tintWeak: "rgba(34, 197, 94, 0.05)",
          badgeClass: "bg-green-500/15 text-green-400 border border-green-500/30",
        };
      case "MEDIUM":
        return {
          label: MN.results.mediumRisk,
          color: "var(--risk-medium)",
          tintStrong: "rgba(245, 158, 11, 0.2)",
          tintWeak: "rgba(245, 158, 11, 0.05)",
          badgeClass: "bg-amber-500/15 text-amber-400 border border-amber-500/30",
        };
      case "HIGH":
        return {
          label: MN.results.highRisk,
          color: "var(--risk-high)",
          tintStrong: "rgba(239, 68, 68, 0.2)",
          tintWeak: "rgba(239, 68, 68, 0.05)",
          badgeClass: "bg-red-500/15 text-red-400 border border-red-500/30",
        };
    }
  };

  const config = getRatingConfig(riskRating);
  const hasNewScoring = totalGrade != null;
  const gradeColors = getGradeColor(totalGrade);

  // Use grade-based tint when available
  const tintStrong = gradeColors ? `${gradeColors.color.replace("0.8", "0.2")}` : config.tintStrong;
  const tintWeak = gradeColors ? `${gradeColors.color.replace("0.8", "0.05")}` : config.tintWeak;

  return (
    <div
      className={`relative overflow-hidden surface-card p-6 sm:p-8 ${className}`}
      style={{
        backgroundImage: `linear-gradient(135deg, ${tintStrong}, ${tintWeak})`,
      }}
    >
      {/* New scoring display */}
      {hasNewScoring && gradeColors ? (
        <>
          {/* Header */}
          <h2 className="text-base font-medium text-[var(--foreground)] mb-6">
            {MN.results.overall}
          </h2>

          {/* Grade and risk value */}
          <div className="flex items-center justify-center gap-4 mb-4">
            <span className={`inline-flex items-center px-4 py-2 rounded-full text-2xl font-bold ${gradeColors.bg} ${gradeColors.text} border ${gradeColors.border}`}>
              {totalGrade}
            </span>
            <span className="text-4xl sm:text-5xl font-bold text-[var(--foreground)]">
              {totalRisk}
            </span>
          </div>

          {/* Risk description */}
          {riskDescription && (
            <p className={`text-center text-sm mb-6 ${gradeColors.text}`}>
              {riskDescription}
            </p>
          )}

          {/* Insurance decision */}
          {insuranceDecision && (
            <div className="flex justify-center mb-6">
              <span
                className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold border ${
                  insuranceDecision === "Даатгана"
                    ? "bg-green-500/15 text-green-400 border-green-500/30"
                    : "bg-red-500/15 text-red-400 border-red-500/30"
                }`}
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  {insuranceDecision === "Даатгана" ? (
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  )}
                </svg>
                Даатгах эсэх: {insuranceDecision}
              </span>
            </div>
          )}

          {/* Legacy score info (smaller) - hidden for new scoring */}
          {!hasNewScoring && (
            <div className="text-center text-sm label-muted">
              <span>{rawScore} / {maxScore} {MN.results.score}</span>
              <span className="mx-2">·</span>
              <span>{percentage.toFixed(1)}%</span>
            </div>
          )}
        </>
      ) : (
        <>
          {/* Legacy display */}
          <h2 className="text-base font-medium text-[var(--foreground)]">
            {MN.results.overall}
          </h2>

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
              <svg className="w-full h-full -rotate-90">
                <circle
                  cx="64"
                  cy="64"
                  r={54}
                  stroke="var(--surface-elevated)"
                  strokeWidth="8"
                  fill="none"
                />
                <circle
                  cx="64"
                  cy="64"
                  r={54}
                  stroke={config.color}
                  strokeWidth="8"
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray={`${(Math.min(percentage, 100) / 100) * 2 * Math.PI * 54} ${2 * Math.PI * 54}`}
                  style={{ transition: "stroke-dasharray 1s ease-out" }}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xl font-semibold" style={{ color: config.color }}>
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
        </>
      )}
    </div>
  );
}

export default OverallScoreCard;
