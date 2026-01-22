/**
 * AssessmentForm page with react-hook-form, conditional fields, and validation.
 */

import { useCallback, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate, useParams } from "react-router-dom";

import { CommentField } from "../components/CommentField";
import { ImageUpload } from "../components/ImageUpload";
import { ProgressBar } from "../components/ProgressBar";
import { QuestionCard } from "../components/QuestionCard";
import { MN } from "../constants/mn";
import { useAssessment, getAllQuestions, getTotalQuestions } from "../hooks/useAssessment";
import { ThemeToggle } from "../hooks/useTheme";
import { useMultiQuestionUpload } from "../hooks/useUpload";
import { submitAssessment } from "../services/assessment";
import type { OptionType, SnapshotQuestion } from "../types/api";

interface FormAnswer {
  selected_option?: OptionType;
  comment?: string;
}

interface FormData {
  answers: Record<string, FormAnswer>;
}

export function AssessmentForm() {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();
  const { state } = useAssessment(token);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<FormData>({
    defaultValues: {
      answers: {},
    },
  });

  const answers = watch("answers");

  // Upload management
  const {
    uploadForQuestion,
    removeFromQuestion,
    getFilesForQuestion,
    getAttachmentIdsForQuestion,
    isUploadingForQuestion,
  } = useMultiQuestionUpload(token || "");

  // Calculate progress
  const answeredCount = Object.values(answers).filter((a) => a?.selected_option).length;

  const totalQuestions = useMemo(() => {
    if (state.status !== "success") return 0;
    return getTotalQuestions(state.data);
  }, [state]);

  // Get all questions flattened
  const allQuestions = useMemo(() => {
    if (state.status !== "success") return [];
    return getAllQuestions(state.data);
  }, [state]);

  // Handle option selection
  const handleOptionSelect = useCallback(
    (questionId: string, option: OptionType) => {
      setValue(`answers.${questionId}.selected_option`, option, {
        shouldValidate: true,
      });
    },
    [setValue]
  );

  // Handle comment change
  const handleCommentChange = useCallback(
    (questionId: string, comment: string) => {
      setValue(`answers.${questionId}.comment`, comment);
    },
    [setValue]
  );

  // Handle image upload
  const handleImageUpload = useCallback(
    async (questionId: string, files: File[]) => {
      for (const file of files) {
        const question = allQuestions.find((q) => q.id === questionId);
        if (!question) continue;

        const selectedOption = answers[questionId]?.selected_option;
        const optionConfig = selectedOption
          ? question.options[selectedOption]
          : question.options.NO;

        await uploadForQuestion(
          questionId,
          file,
          optionConfig.max_images,
          optionConfig.image_max_mb
        );
      }
    },
    [allQuestions, answers, uploadForQuestion]
  );

  // Handle image remove
  const handleImageRemove = useCallback(
    (questionId: string, imageId: string) => {
      removeFromQuestion(questionId, imageId);
    },
    [removeFromQuestion]
  );

  // Get current option config for a question
  const getOptionConfig = useCallback(
    (question: SnapshotQuestion, selectedOption?: OptionType) => {
      if (!selectedOption) return null;
      return question.options[selectedOption];
    },
    []
  );

  // Validate answer against requirements
  const validateAnswer = useCallback(
    (questionId: string): string | null => {
      const question = allQuestions.find((q) => q.id === questionId);
      if (!question) return null;

      const answer = answers[questionId];
      if (!answer?.selected_option) return MN.validation.answerRequired;

      const optionConfig = question.options[answer.selected_option];

      // Check comment requirement
      if (optionConfig.require_comment) {
        if (!answer.comment || answer.comment.length < optionConfig.comment_min_len) {
          return MN.assessment.minCommentLength(optionConfig.comment_min_len);
        }
      }

      // Check image requirement
      if (optionConfig.require_image) {
        const attachmentIds = getAttachmentIdsForQuestion(questionId);
        if (attachmentIds.length === 0) {
          return MN.assessment.requiredImage;
        }
      }

      return null;
    },
    [allQuestions, answers, getAttachmentIdsForQuestion]
  );

  // Handle form submission
  const onSubmit = async () => {
    if (!token || state.status !== "success") return;

    // Validate all answers
    const validationErrors: string[] = [];
    for (const question of allQuestions) {
      const error = validateAnswer(question.id);
      if (error) {
        validationErrors.push(`${question.text.slice(0, 50)}...: ${error}`);
      }
    }

    if (validationErrors.length > 0) {
      setSubmitError(validationErrors[0]);
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    // Build submission data
    const submitData = {
      answers: allQuestions.map((question) => ({
        question_id: question.id,
        selected_option: answers[question.id]?.selected_option || "NO",
        comment: answers[question.id]?.comment || undefined,
        attachment_ids: getAttachmentIdsForQuestion(question.id),
      })),
    };

    const result = await submitAssessment(token, submitData);

    setIsSubmitting(false);

    if (result.success) {
      // Navigate to results page with data
      navigate(`/a/${token}/results`, {
        state: { results: result.data },
        replace: true,
      });
    } else {
      setSubmitError(result.message);

      // Handle specific errors
      if (result.error === "expired") {
        navigate("/expired", { replace: true });
      } else if (result.error === "already_completed") {
        navigate("/used", { replace: true });
      }
    }
  };

  // Loading state
  if (state.status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="surface-card p-8 text-center">
          <div className="spinner spinner-lg mx-auto mb-4" />
          <p className="label-muted">{MN.loading}</p>
        </div>
      </div>
    );
  }

  // Error state (should redirect, but fallback)
  if (state.status === "error") {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="surface-card p-8 text-center">
          <p className="text-red-600">{state.message}</p>
        </div>
      </div>
    );
  }

  const { data: form } = state;

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="container-app">
        {/* Header */}
        <div className="surface-card p-6 sm:p-8 mb-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="pill mb-4">
                <svg
                  className="h-3.5 w-3.5"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M12 3l8 4v5c0 5-3.5 9-8 9s-8-4-8-9V7l8-4z" />
                </svg>
                {MN.assessment.title}
              </div>
              <h1 className="text-2xl sm:text-3xl font-semibold text-[var(--foreground)]">
                {MN.assessment.title}
              </h1>
              <p className="mt-2 text-sm label-muted">{form.respondent_name}</p>
            </div>
            <ThemeToggle />
          </div>

        </div>

        <div className="surface-card p-4 mb-8">
          <ProgressBar current={answeredCount} total={totalQuestions} />
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Questions grouped by type */}
          {form.types.map((type) => (
            <div key={type.id} className="space-y-6">
              {/* Type header */}
              <div className="surface-panel">
                <h2 className="text-base sm:text-lg font-medium">
                  {type.name}
                </h2>
              </div>

              {/* Questions */}
              {type.questions.map((question, index) => {
                const selectedOption = answers[question.id]?.selected_option;
                const optionConfig = getOptionConfig(question, selectedOption);
                const validationError = validateAnswer(question.id);
                const questionNumber =
                  form.types
                    .slice(0, form.types.indexOf(type))
                    .reduce((sum, t) => sum + t.questions.length, 0) +
                  index +
                  1;

                return (
                  <QuestionCard
                    key={question.id}
                    questionId={question.id}
                    text={question.text}
                    questionNumber={questionNumber}
                    selectedOption={selectedOption}
                    onSelect={(option) => handleOptionSelect(question.id, option)}
                    yesRequiresComment={question.options.YES.require_comment}
                    yesRequiresImage={question.options.YES.require_image}
                    noRequiresComment={question.options.NO.require_comment}
                    noRequiresImage={question.options.NO.require_image}
                  >
                    {/* Conditional fields */}
                    {selectedOption && optionConfig && (
                      <div className="space-y-4">
                        {/* Comment field */}
                        {optionConfig.require_comment && (
                          <CommentField
                            value={answers[question.id]?.comment || ""}
                            onChange={(value) =>
                              handleCommentChange(question.id, value)
                            }
                            required
                            minLength={optionConfig.comment_min_len}
                            maxLength={2000}
                            error={
                              validationError?.includes(MN.assessment.minCommentLength(0).split(" ")[0])
                                ? validationError
                                : undefined
                            }
                          />
                        )}

                        {/* Image upload */}
                        {optionConfig.require_image && (
                          <ImageUpload
                            images={getFilesForQuestion(question.id)}
                            onUpload={(files) =>
                              handleImageUpload(question.id, files)
                            }
                            onRemove={(imageId) =>
                              handleImageRemove(question.id, imageId)
                            }
                            required
                            maxImages={optionConfig.max_images}
                            maxSizeMb={optionConfig.image_max_mb}
                            isUploading={isUploadingForQuestion(question.id)}
                            error={
                              validationError === MN.assessment.requiredImage
                                ? validationError
                                : undefined
                            }
                          />
                        )}
                      </div>
                    )}
                  </QuestionCard>
                );
              })}
            </div>
          ))}

          {/* Submit error */}
          {submitError && (
            <div className="surface-card border border-[var(--risk-high)]/40 p-4">
              <p className="text-red-400">{submitError}</p>
            </div>
          )}

          {/* Submit button */}
          <div className="pt-6">
            <button
              type="submit"
              disabled={isSubmitting || answeredCount < totalQuestions}
              className="btn-cta"
            >
              {isSubmitting ? MN.assessment.submitting : MN.assessment.submitAssessment}
            </button>

            {answeredCount < totalQuestions && (
              <p className="mt-2 text-center text-sm label-muted">
                {MN.validation.answerRequired}
              </p>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}

export default AssessmentForm;
