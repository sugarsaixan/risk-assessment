/**
 * TypeScoreCard component for displaying per-type results with group breakdown.
 */

import { useState } from "react";
import { MN } from "../constants/mn";
import type { GroupResult, RiskRating } from "../types/api";

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
  /** Group results within this type */
  groups?: GroupResult[];
  /** Probability score (МАГАДЛАЛЫН ОНОО) */
  probabilityScore?: number | undefined;
  /** Consequence score (ҮР ДАГАВРЫН ОНОО) */
  consequenceScore?: number | undefined;
  /** Type risk value (ЭРСДЭЛ) */
  riskValue?: number | undefined;
  /** Type risk grade (AAA-D) */
  riskGrade?: string | undefined;
  /** Mongolian risk description */
  riskDescription?: string | undefined;
  /** Optional CSS class names */
  className?: string;
}

function getRatingConfig(rating: RiskRating) {
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
}

function getClassificationColor(label: string | undefined) {
  switch (label) {
    case "Хэвийн":
      return { bg: "bg-green-500/15", text: "text-green-400", border: "border-green-500/30" };
    case "Хянахуйц":
      return { bg: "bg-blue-500/15", text: "text-blue-400", border: "border-blue-500/30" };
    case "Анхаарах":
      return { bg: "bg-yellow-500/15", text: "text-yellow-400", border: "border-yellow-500/30" };
    case "Ноцтой":
      return { bg: "bg-orange-500/15", text: "text-orange-400", border: "border-orange-500/30" };
    case "Аюултай":
      return { bg: "bg-red-500/15", text: "text-red-400", border: "border-red-500/30" };
    default:
      return null;
  }
}

function GroupScoreRow({ group }: { group: GroupResult }) {
  const config = getRatingConfig(group.risk_rating);
  const classColors = getClassificationColor(group.classification_label);
  const hasNewScoring = group.classification_label != null;

  return (
    <div className="py-3 border-b border-[var(--border)] last:border-b-0">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-sm text-[var(--foreground)]">{group.group_name}</span>
          {group.classification_label && classColors && (
            <span
              className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${classColors.bg} ${classColors.text} border ${classColors.border}`}
            >
              {group.classification_label}
            </span>
          )}
        </div>
        {group.sum_score != null && (
          <span className="text-sm font-medium text-[var(--foreground)]">
            {group.sum_score}
          </span>
        )}
      </div>
      {/* Progress bar - use classification colors if available, otherwise legacy colors */}
      {hasNewScoring && classColors ? (
        <div className="progress-track h-1.5">
          <div
            className={`h-full rounded-full transition-all duration-500 ${classColors.text.replace("text-", "bg-").replace("-400", "-500")}/80`}
            style={{ width: `${Math.min(group.percentage, 100)}%` }}
          />
        </div>
      ) : (
        <div className="progress-track h-1.5">
          <div
            className={`h-full ${config.progressColor} rounded-full transition-all duration-500`}
            style={{ width: `${Math.min(group.percentage, 100)}%` }}
          />
        </div>
      )}
      <div className="flex items-center justify-between mt-1">
        <span className="text-xs label-muted">
          {group.raw_score} / {group.max_score}
        </span>
        {/* Only show legacy risk rating label if no new classification */}
        {!hasNewScoring && (
          <span className={`text-xs ${config.textColor}`}>{config.label}</span>
        )}
      </div>
    </div>
  );
}

function getGradeColor(grade: string | undefined) {
  if (!grade) return null;
  if (["AAA", "AA", "A"].includes(grade))
    return { bg: "bg-green-500/15", text: "text-green-400", border: "border-green-500/30" };
  if (["BBB", "BB", "B"].includes(grade))
    return { bg: "bg-yellow-500/15", text: "text-yellow-400", border: "border-yellow-500/30" };
  if (["CCC", "CC", "C"].includes(grade))
    return { bg: "bg-orange-500/15", text: "text-orange-400", border: "border-orange-500/30" };
  if (["DDD", "DD", "D"].includes(grade))
    return { bg: "bg-red-500/15", text: "text-red-400", border: "border-red-500/30" };
  return null;
}

export function TypeScoreCard({
  typeName,
  rawScore,
  maxScore,
  percentage,
  riskRating,
  groups = [],
  probabilityScore,
  consequenceScore,
  riskValue,
  riskGrade,
  riskDescription,
  className = "",
}: TypeScoreCardProps) {
  const [showGroups, setShowGroups] = useState(false);
  const config = getRatingConfig(riskRating);
  const hasGroups = groups.length > 0;
  const hasNewScoring = riskGrade != null;
  const gradeColors = getGradeColor(riskGrade);

  return (
    <div
      className={`surface-card p-4 border border-[var(--border)] border-l-4 ${className}`}
      style={{
        borderLeftColor: hasNewScoring && gradeColors
          ? gradeColors.text === "text-green-400"
            ? "rgba(34, 197, 94, 0.4)"
            : gradeColors.text === "text-yellow-400"
            ? "rgba(234, 179, 8, 0.4)"
            : gradeColors.text === "text-orange-400"
            ? "rgba(249, 115, 22, 0.4)"
            : "rgba(239, 68, 68, 0.4)"
          : config.borderColor
      }}
    >
      {/* Type name */}
      <h3 className="text-sm font-medium mb-3 text-[var(--foreground)]">{typeName}</h3>

      {/* New risk grade display */}
      {hasNewScoring && gradeColors ? (
        <>
          {/* Risk grade badge and value */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-lg font-bold ${gradeColors.bg} ${gradeColors.text} border ${gradeColors.border}`}>
                {riskGrade}
              </span>
              <span className="text-2xl font-bold text-[var(--foreground)]">
                {riskValue}
              </span>
            </div>
          </div>

          {/* Risk description */}
          {riskDescription && (
            <p className={`text-sm mb-3 ${gradeColors.text}`}>{riskDescription}</p>
          )}

          {/* Probability and Consequence scores */}
          <div className="grid grid-cols-2 gap-3 mb-3 p-3 rounded-lg bg-[var(--surface-elevated)]">
            {probabilityScore != null && (
              <div>
                <div className="text-xs label-muted mb-1">Магадлалын оноо</div>
                <div className="text-sm font-semibold text-[var(--foreground)]">
                  {probabilityScore.toFixed(2)}
                </div>
              </div>
            )}
            {consequenceScore != null && (
              <div>
                <div className="text-xs label-muted mb-1">Үр дагаврын оноо</div>
                <div className="text-sm font-semibold text-[var(--foreground)]">
                  {consequenceScore.toFixed(2)}
                </div>
              </div>
            )}
          </div>

          {/* Legacy score info (smaller) */}
          <div className="flex items-center justify-between text-xs label-muted mb-1">
            <span>{rawScore} / {maxScore}</span>
            <span>{percentage.toFixed(1)}%</span>
          </div>
        </>
      ) : (
        <>
          {/* Legacy score display */}
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
        </>
      )}

      {/* Group breakdown toggle */}
      {hasGroups && (
        <div className="mt-4">
          <button
            type="button"
            onClick={() => setShowGroups(!showGroups)}
            className="flex items-center gap-2 text-sm text-[var(--primary)] hover:underline"
          >
            <svg
              className={`w-4 h-4 transition-transform ${showGroups ? "rotate-180" : ""}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
            </svg>
            {showGroups ? "Бүлгүүдийг нуух" : `Бүлгүүдийг харах (${groups.length})`}
          </button>

          {/* Group scores */}
          {showGroups && (
            <div className="mt-3 pt-3 border-t border-[var(--border)]">
              {groups.map((group) => (
                <GroupScoreRow key={group.group_id} group={group} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default TypeScoreCard;
