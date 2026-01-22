/**
 * ProgressBar component showing "X / Y асуулт" progress.
 */

import { MN } from "../constants/mn";

interface ProgressBarProps {
  /** Current question number (1-indexed) */
  current: number;
  /** Total number of questions */
  total: number;
  /** Optional CSS class names */
  className?: string;
}

export function ProgressBar({ current, total, className = "" }: ProgressBarProps) {
  const percentage = total > 0 ? Math.round((current / total) * 100) : 0;

  return (
    <div className={`w-full ${className}`}>
      {/* Progress text */}
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-medium text-[var(--app-ink)]">
          {MN.assessment.questionCount(current, total)}
        </span>
        <span className="text-sm label-muted">{percentage}%</span>
      </div>

      {/* Progress bar */}
      <div className="progress-track">
        <div
          className="progress-fill"
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={current}
          aria-valuemin={0}
          aria-valuemax={total}
          aria-label={MN.assessment.questionCount(current, total)}
        />
      </div>
    </div>
  );
}

export default ProgressBar;
