/**
 * QuestionCard component with YES/NO buttons ("Тийм" / "Үгүй").
 */

import { MN } from "../constants/mn";
import type { OptionType } from "../schemas/assessment";

interface QuestionCardProps {
  /** Question ID */
  questionId: string;
  /** Question text to display */
  text: string;
  /** Display order / question number */
  questionNumber: number;
  /** Currently selected option */
  selectedOption?: OptionType;
  /** Callback when an option is selected */
  onSelect: (option: OptionType) => void;
  /** Whether comment is required for YES option */
  yesRequiresComment?: boolean;
  /** Whether image is required for YES option */
  yesRequiresImage?: boolean;
  /** Whether comment is required for NO option */
  noRequiresComment?: boolean;
  /** Whether image is required for NO option */
  noRequiresImage?: boolean;
  /** Optional CSS class names */
  className?: string;
  /** Child elements (for conditional fields) */
  children?: React.ReactNode;
}

export function QuestionCard({
  questionId,
  text,
  questionNumber,
  selectedOption,
  onSelect,
  yesRequiresComment = false,
  yesRequiresImage = false,
  noRequiresComment = false,
  noRequiresImage = false,
  className = "",
  children,
}: QuestionCardProps) {
  const getRequirementText = (requiresComment: boolean, requiresImage: boolean) => {
    const requirements: string[] = [];
    if (requiresComment) requirements.push(MN.assessment.requiredComment);
    if (requiresImage) requirements.push(MN.assessment.requiredImage);
    return requirements.join(", ");
  };

  const yesRequirements = getRequirementText(yesRequiresComment, yesRequiresImage);
  const noRequirements = getRequirementText(noRequiresComment, noRequiresImage);

  return (
    <div
      className={`question-card surface-card p-6 ${className}`}
      data-question-id={questionId}
    >
      {/* Question number and text */}
      <div className="mb-6">
        <span className="pill mb-3">
          {questionNumber}
        </span>
        <p className="text-lg text-[var(--app-ink)]">{text}</p>
      </div>

      {/* YES/NO buttons */}
      <div className="flex flex-col sm:flex-row gap-3">
        {/* YES button */}
        <button
          type="button"
          onClick={() => onSelect("YES")}
          className={`option-button option-button--yes ${
            selectedOption === "YES" ? "option-button--active" : ""
          }`}
          aria-pressed={selectedOption === "YES"}
        >
          <span className="block">{MN.options.yes}</span>
          {yesRequirements && (
            <span className="block text-xs mt-1 opacity-75">({yesRequirements})</span>
          )}
        </button>

        {/* NO button */}
        <button
          type="button"
          onClick={() => onSelect("NO")}
          className={`option-button option-button--no ${
            selectedOption === "NO" ? "option-button--active" : ""
          }`}
          aria-pressed={selectedOption === "NO"}
        >
          <span className="block">{MN.options.no}</span>
          {noRequirements && (
            <span className="block text-xs mt-1 opacity-75">({noRequirements})</span>
          )}
        </button>
      </div>

      {/* Conditional fields (comment, image upload) */}
      {children && selectedOption && <div className="mt-6">{children}</div>}
    </div>
  );
}

export default QuestionCard;
