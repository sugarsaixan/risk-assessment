/**
 * AssessmentForm page with hierarchical Type → Group → Question structure.
 * Contact info is collected on a separate page after questionnaire completion.
 */

import { useCallback, useEffect, useMemo, useState } from "react";
import { useForm, useWatch } from "react-hook-form";
import { useNavigate, useParams } from "react-router-dom";

import { AutoSaveIndicator } from "../components/AutoSaveIndicator";
import { CommentField } from "../components/CommentField";
import { ImageUpload } from "../components/ImageUpload";
import { ProgressBar } from "../components/ProgressBar";
import { QuestionCard } from "../components/QuestionCard";
import { SaveButton } from "../components/SaveButton";
import { MN } from "../constants/mn";
import { useAssessmentContext } from "../contexts/AssessmentContext";
import { useAssessment, getAllQuestions, getTotalQuestions } from "../hooks/useAssessment";
import { useAutoSave } from "../hooks/useAutoSave";
import { ThemeToggle } from "../hooks/useTheme";
import { useMultiQuestionUpload, type UploadedFile } from "../hooks/useUpload";
import type { OptionType, SnapshotQuestion, AssessmentFormDraft } from "../types/api";
import { loadDraft } from "../services/draft";
import type { DraftAnswer, DraftResponse } from "../services/draft";

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
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [draftLoaded, setDraftLoaded] = useState(false);
  const [loadedDraft, setLoadedDraft] = useState<AssessmentFormDraft | DraftResponse | null>(null);

  // Get context to store answers for ContactPage
  const { setAnswers: setContextAnswers, answers: contextAnswers } = useAssessmentContext();

  const {
    handleSubmit,
    control,
    setValue,
    reset,
  } = useForm<FormData>({
    defaultValues: {
      answers: contextAnswers,
    },
  });

  const answers = useWatch({ control, name: "answers" }) || {};

  // Restore draft answers on initial load
  const [draftRestored, setDraftRestored] = useState(false);
  useEffect(() => {
    if (draftRestored) return;
    if (!draftLoaded) return;

    const draft = loadedDraft;
    if (!draft || draft.answers.length === 0) {
      setDraftRestored(true);
      return;
    }

    // Only restore if context answers are empty (i.e., not returning from ContactPage)
    const hasContextAnswers = Object.keys(contextAnswers).length > 0;
    if (hasContextAnswers) {
      setDraftRestored(true);
      return;
    }

    // Convert draft answers array to Record<string, FormAnswer>
    const restoredAnswers: Record<string, FormAnswer> = {};
    for (const da of draft.answers) {
      const answer: FormAnswer = {};
      if (da.selected_option) {
        answer.selected_option = da.selected_option;
      }
      if (da.comment) {
        answer.comment = da.comment;
      }
      restoredAnswers[da.question_id] = answer;
    }

    // Set restored answers into the form and context
    reset({ answers: restoredAnswers });
    setContextAnswers(restoredAnswers);

    setDraftRestored(true);
  }, [draftRestored, draftLoaded, loadedDraft, contextAnswers, reset, setContextAnswers]);

  // Upload management
  const {
    uploadForQuestion,
    removeFromQuestion,
    setFilesForQuestion,
    getFilesForQuestion,
    getAttachmentIdsForQuestion,
    isUploadingForQuestion,
  } = useMultiQuestionUpload(token || "");

  // Load draft from assessment response or draft endpoint
  useEffect(() => {
    if (draftLoaded) return;
    if (state.status !== "success") return;

    const inlineDraft = state.data.draft ?? null;
    if (inlineDraft) {
      setLoadedDraft(inlineDraft);
      setDraftLoaded(true);
      return;
    }

    let cancelled = false;
    (async () => {
      if (!token) {
        setDraftLoaded(true);
        return;
      }
      const result = await loadDraft(token);
      if (cancelled) return;
      if (result.success) {
        setLoadedDraft(result.data);
      } else {
        setLoadedDraft(null);
      }
      setDraftLoaded(true);
    })();

    return () => {
      cancelled = true;
    };
  }, [draftLoaded, state, token]);

  // Seed attachment IDs from draft so validation + autosave include them
  useEffect(() => {
    if (!draftRestored || !loadedDraft) return;

    for (const da of loadedDraft.answers) {
      if (!da.attachment_ids || da.attachment_ids.length === 0) continue;
      const files: UploadedFile[] = da.attachment_ids.map((id) => ({
        id,
        name: "Saved attachment",
        size: 0,
        progress: 100,
      }));
      setFilesForQuestion(da.question_id, files);
    }
  }, [draftRestored, loadedDraft, setFilesForQuestion]);

  // Build draft data for auto-save
  const draftData = useMemo(() => {
    const draftAnswers: DraftAnswer[] = Object.entries(answers)
      .filter(([, a]) => {
        if (!a) return false;
        if (a.selected_option) return true;
        if (a.comment && a.comment.trim().length > 0) return true;
        return false;
      })
      .map(([questionId, a]) => ({
        question_id: questionId,
        selected_option: a.selected_option ?? null,
        comment: a.comment ?? null,
        attachment_ids: getAttachmentIdsForQuestion(questionId),
      }));

    return { answers: draftAnswers };
  }, [answers, getAttachmentIdsForQuestion]);

  // Auto-save hook
  const {
    status: autoSaveStatus,
    lastSavedAt,
    error: autoSaveError,
    saveNow,
  } = useAutoSave({
    token,
    data: draftData,
    enabled: state.status === "success",
  });

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
        shouldDirty: true,
        shouldTouch: true,
      });
    },
    [setValue]
  );

  // Handle comment change
  const handleCommentChange = useCallback(
    (questionId: string, comment: string) => {
      setValue(`answers.${questionId}.comment`, comment, {
        shouldDirty: true,
        shouldTouch: true,
      });
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

  // Handle form submission - navigate to contact page
  const onSubmit = () => {
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
      setSubmitError(validationErrors[0] || null);
      return;
    }

    setSubmitError(null);

    // Store answers in context for ContactPage to access
    setContextAnswers(answers);

    // Navigate to contact page to collect contact info
    navigate(`/a/${token}/contact`);
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

  // Calculate question number accounting for hierarchical structure
  let questionCounter = 0;
  const getQuestionNumber = () => {
    questionCounter++;
    return questionCounter;
  };

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
            <div className="flex flex-col items-end gap-2">
              <ThemeToggle />
              <SaveButton
                status={autoSaveStatus}
                onSave={saveNow}
              />
              <AutoSaveIndicator
                status={autoSaveStatus}
                lastSavedAt={lastSavedAt}
                error={autoSaveError}
              />
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="surface-card p-4 mb-8">
          <ProgressBar current={answeredCount} total={totalQuestions} />
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Questions grouped by type → group → question */}
          {form.types.map((type) => (
            <div key={type.id} className="space-y-6">
              {/* Type header */}
              <div className="surface-panel">
                <h2 className="text-base sm:text-lg font-medium">
                  {type.name}
                </h2>
              </div>

              {/* Groups within type */}
              {type.groups.map((group) => (
                <div key={group.id} className="space-y-4">
                  {/* Group header */}
                  <div className="px-4 py-2 bg-[var(--surface-elevated)] border-l-2 border-[var(--primary)]">
                    <h3 className="text-sm font-medium text-[var(--foreground)]">
                      {group.name}
                    </h3>
                  </div>

                  {/* Questions within group */}
                  {group.questions.map((question) => {
                    const questionNumber = getQuestionNumber();
                    const selectedOption = answers[question.id]?.selected_option;
                    const optionConfig = getOptionConfig(question, selectedOption);
                    const validationError = validateAnswer(question.id);
                    const minCommentToken =
                      MN.assessment.minCommentLength(0).split(" ")[0] || "";

                    return (
                      <QuestionCard
                        key={question.id}
                        questionId={question.id}
                        text={question.text}
                        questionNumber={questionNumber}
                        {...(selectedOption ? { selectedOption } : {})}
                        onSelect={(option) => handleOptionSelect(question.id, option)}
                        yesRequiresComment={question.options.YES.require_comment}
                        yesRequiresImage={question.options.YES.require_image}
                        noRequiresComment={question.options.NO.require_comment}
                        noRequiresImage={question.options.NO.require_image}
                        isCritical={question.is_critical}
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
                                {...(validationError?.includes(minCommentToken)
                                  ? { error: validationError }
                                  : {})}
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
                                {...(validationError === MN.assessment.requiredImage
                                  ? { error: validationError }
                                  : {})}
                              />
                            )}
                          </div>
                        )}
                      </QuestionCard>
                    );
                  })}
                </div>
              ))}
            </div>
          ))}

          {/* Submit error */}
          {submitError && (
            <div className="surface-card border border-[var(--risk-high)]/40 p-4">
              <p className="text-red-400">{submitError}</p>
            </div>
          )}

          {/* Submit button - navigates to contact page */}
          <div className="pt-6">
            <button
              type="submit"
              disabled={answeredCount < totalQuestions}
              className="btn-cta"
            >
              {MN.assessment.submitAssessment}
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
