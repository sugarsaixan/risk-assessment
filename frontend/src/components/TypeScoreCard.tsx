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

function GroupScoreRow({ group }: { group: GroupResult }) {
  const config = getRatingConfig(group.risk_rating);

  return (
    <div className="py-3 border-b border-[var(--border)] last:border-b-0">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-[var(--foreground)]">{group.group_name}</span>
        <span className={`text-sm font-medium ${config.textColor}`}>
          {group.percentage.toFixed(1)}%
        </span>
      </div>
      <div className="progress-track h-1.5">
        <div
          className={`h-full ${config.progressColor} rounded-full transition-all duration-500`}
          style={{ width: `${Math.min(group.percentage, 100)}%` }}
        />
      </div>
      <div className="flex items-center justify-between mt-1">
        <span className="text-xs label-muted">
          {group.raw_score} / {group.max_score}
        </span>
        <span className={`text-xs ${config.textColor}`}>{config.label}</span>
      </div>
    </div>
  );
}

export function TypeScoreCard({
  typeName,
  rawScore,
  maxScore,
  percentage,
  riskRating,
  groups = [],
  className = "",
}: TypeScoreCardProps) {
  const [showGroups, setShowGroups] = useState(false);
  const config = getRatingConfig(riskRating);
  const hasGroups = groups.length > 0;

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
