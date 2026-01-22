/**
 * CommentField component with character counter (max 2000).
 */

import { useId } from "react";
import { MN } from "../constants/mn";

interface CommentFieldProps {
  /** Current comment value */
  value: string;
  /** Callback when value changes */
  onChange: (value: string) => void;
  /** Whether the field is required */
  required?: boolean;
  /** Minimum character length (only validated if required) */
  minLength?: number;
  /** Maximum character length */
  maxLength?: number;
  /** Error message to display */
  error?: string;
  /** Placeholder text */
  placeholder?: string;
  /** Whether the field is disabled */
  disabled?: boolean;
  /** Optional CSS class names */
  className?: string;
}

export function CommentField({
  value,
  onChange,
  required = false,
  minLength = 0,
  maxLength = 2000,
  error,
  placeholder,
  disabled = false,
  className = "",
}: CommentFieldProps) {
  const id = useId();
  const currentLength = value?.length || 0;
  const isOverLimit = currentLength > maxLength;
  const isBelowMinimum = required && minLength > 0 && currentLength < minLength;

  // Determine counter color
  const getCounterColor = () => {
    if (isOverLimit) return "text-red-600 dark:text-red-400";
    if (currentLength > maxLength * 0.9) return "text-yellow-600 dark:text-yellow-400";
    return "text-gray-500 dark:text-gray-400";
  };

  return (
    <div className={`w-full ${className}`}>
      {/* Label */}
      <label
        htmlFor={id}
        className="block form-label"
      >
        {MN.assessment.requiredComment}
        {required && <span className="text-red-500 ml-1">*</span>}
        {minLength > 0 && (
          <span className="font-normal label-muted ml-2">
            ({MN.assessment.minCommentLength(minLength)})
          </span>
        )}
      </label>

      {/* Textarea */}
      <div className="relative">
        <textarea
          id={id}
          value={value || ""}
          onChange={(e) => onChange(e.target.value)}
          maxLength={maxLength + 100} // Allow slight overflow for UX, but show error
          placeholder={placeholder}
          disabled={disabled}
          rows={4}
          className={`textarea-field disabled:cursor-not-allowed ${
            error || isOverLimit ? "field-error" : isBelowMinimum ? "field-warning" : ""
          }`}
          aria-invalid={!!error || isOverLimit}
          aria-describedby={error ? `${id}-error` : undefined}
        />

        {/* Character counter */}
        <div
          className={`absolute bottom-2 right-3 text-xs ${getCounterColor()}`}
          aria-live="polite"
        >
          {MN.assessment.characterCount(currentLength, maxLength)}
        </div>
      </div>

      {/* Error message */}
      {error && (
        <p id={`${id}-error`} className="mt-2 text-sm text-red-600">
          {error}
        </p>
      )}

      {/* Minimum length hint (when below minimum but no error yet) */}
      {!error && isBelowMinimum && (
        <p className="mt-2 text-sm text-yellow-600">
          {MN.assessment.minCommentLength(minLength)}
        </p>
      )}
    </div>
  );
}

export default CommentField;
