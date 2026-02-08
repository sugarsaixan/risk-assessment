/**
 * Collapsible answers section for the Results page.
 * Displays all submitted answers grouped by questionnaire type.
 */

import { useState } from "react";
import { MN } from "../constants/mn";
import type { AnswerBreakdown } from "../types/api";

interface AnswersSectionProps {
  answers: AnswerBreakdown[];
  className?: string;
}

function AnswerRow({ answer }: { answer: AnswerBreakdown }) {
  const isYes = answer.selected_option === "YES";
  // Color based on score_awarded: 0 = green (good), 1+ = red (issue found)
  const hasIssue = answer.score_awarded > 0;

  return (
    <div className="py-3 border-b border-[var(--border)] last:border-b-0">
      <div className="flex items-start justify-between gap-3">
        <span className="text-sm font-medium text-[var(--foreground)]">
          {answer.question_text}
        </span>
        <div className="flex items-center gap-2 shrink-0">
          <span
            className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
              hasIssue
                ? "bg-red-500/10 text-red-400"
                : "bg-green-500/10 text-green-400"
            }`}
          >
            {isYes ? MN.answers.yes : MN.answers.no}
          </span>
          <span className="text-xs label-muted">
            {answer.score_awarded}/{answer.max_score}
          </span>
        </div>
      </div>
      {answer.comment && (
        <p className="mt-1 text-xs label-muted">{answer.comment}</p>
      )}
      {answer.attachment_count > 0 && (
        <span className="mt-1 inline-flex items-center gap-1 text-xs label-muted">
          📎 {answer.attachment_count}
        </span>
      )}
    </div>
  );
}

export function AnswersSection({ answers, className = "" }: AnswersSectionProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (answers.length === 0) return null;

  // Group answers by type_name
  const grouped: Record<string, AnswerBreakdown[]> = {};
  for (const answer of answers) {
    const typeName = answer.type_name;
    if (!grouped[typeName]) {
      grouped[typeName] = [];
    }
    grouped[typeName]!.push(answer);
  }

  return (
    <div className={`surface-card ${className}`}>
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 text-left"
      >
        <h3 className="text-base font-medium text-[var(--foreground)]">
          {MN.answers.title} ({answers.length})
        </h3>
        <div className="flex items-center gap-2">
          <span className="text-sm label-muted">
            {isExpanded ? MN.answers.hide : MN.answers.show}
          </span>
          <svg
            className={`w-4 h-4 text-[var(--foreground)] transition-transform ${
              isExpanded ? "rotate-180" : ""
            }`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {isExpanded && (
        <div className="border-t border-[var(--border)]">
          {Object.entries(grouped).map(([typeName, typeAnswers]) => (
            <div key={typeName}>
              <div className="px-4 py-2 bg-[var(--muted)]/30">
                <span className="text-sm font-medium text-[var(--foreground)]">
                  {typeName}
                </span>
                <span className="text-xs label-muted ml-2">
                  ({typeAnswers.length})
                </span>
              </div>
              <div className="px-4">
                {typeAnswers.map((answer) => (
                  <AnswerRow key={answer.question_id} answer={answer} />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AnswersSection;
