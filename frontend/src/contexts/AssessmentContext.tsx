/**
 * AssessmentContext - Shared state between AssessmentForm and ContactPage.
 * Preserves form answers and uploaded attachments across page navigation.
 */

import {
  createContext,
  useContext,
  useCallback,
  useState,
  useMemo,
  type ReactNode,
} from "react";

import type { OptionType, SubmissionContactInput } from "../types/api";

// ============================================================================
// Types
// ============================================================================

export interface FormAnswer {
  selected_option?: OptionType;
  comment?: string;
}

export interface UploadedFile {
  id: string;
  file: File;
  preview?: string;
}

interface AssessmentContextValue {
  // Form answers (question_id -> answer)
  answers: Record<string, FormAnswer>;
  setAnswer: (questionId: string, answer: FormAnswer) => void;
  setAnswers: (answers: Record<string, FormAnswer>) => void;

  // Uploaded attachments (question_id -> files)
  attachments: Record<string, UploadedFile[]>;
  setAttachmentsForQuestion: (questionId: string, files: UploadedFile[]) => void;
  getAttachmentIdsForQuestion: (questionId: string) => string[];

  // Contact info (filled on ContactPage)
  contact: Partial<SubmissionContactInput>;
  setContact: (contact: Partial<SubmissionContactInput>) => void;
  updateContactField: (field: keyof SubmissionContactInput, value: string) => void;

  // Reset all state
  resetState: () => void;
}

// ============================================================================
// Context
// ============================================================================

const AssessmentContext = createContext<AssessmentContextValue | null>(null);

// ============================================================================
// Provider
// ============================================================================

interface AssessmentProviderProps {
  children: ReactNode;
}

export function AssessmentProvider({ children }: AssessmentProviderProps) {
  const [answers, setAnswersState] = useState<Record<string, FormAnswer>>({});
  const [attachments, setAttachments] = useState<Record<string, UploadedFile[]>>({});
  const [contact, setContactState] = useState<Partial<SubmissionContactInput>>({});

  // Set a single answer
  const setAnswer = useCallback((questionId: string, answer: FormAnswer) => {
    setAnswersState((prev) => ({
      ...prev,
      [questionId]: answer,
    }));
  }, []);

  // Set all answers at once
  const setAnswers = useCallback((newAnswers: Record<string, FormAnswer>) => {
    setAnswersState(newAnswers);
  }, []);

  // Set attachments for a question
  const setAttachmentsForQuestion = useCallback(
    (questionId: string, files: UploadedFile[]) => {
      setAttachments((prev) => ({
        ...prev,
        [questionId]: files,
      }));
    },
    []
  );

  // Get attachment IDs for a question
  const getAttachmentIdsForQuestion = useCallback(
    (questionId: string): string[] => {
      return (attachments[questionId] || []).map((f) => f.id);
    },
    [attachments]
  );

  // Set entire contact object
  const setContact = useCallback((newContact: Partial<SubmissionContactInput>) => {
    setContactState(newContact);
  }, []);

  // Update a single contact field
  const updateContactField = useCallback(
    (field: keyof SubmissionContactInput, value: string) => {
      setContactState((prev) => ({
        ...prev,
        [field]: value,
      }));
    },
    []
  );

  // Reset all state
  const resetState = useCallback(() => {
    setAnswersState({});
    setAttachments({});
    setContactState({});
  }, []);

  const value = useMemo<AssessmentContextValue>(
    () => ({
      answers,
      setAnswer,
      setAnswers,
      attachments,
      setAttachmentsForQuestion,
      getAttachmentIdsForQuestion,
      contact,
      setContact,
      updateContactField,
      resetState,
    }),
    [
      answers,
      setAnswer,
      setAnswers,
      attachments,
      setAttachmentsForQuestion,
      getAttachmentIdsForQuestion,
      contact,
      setContact,
      updateContactField,
      resetState,
    ]
  );

  return (
    <AssessmentContext.Provider value={value}>
      {children}
    </AssessmentContext.Provider>
  );
}

// ============================================================================
// Hook
// ============================================================================

/**
 * Hook to access assessment form state shared between pages.
 * Must be used within AssessmentProvider.
 */
export function useAssessmentContext(): AssessmentContextValue {
  const context = useContext(AssessmentContext);
  if (!context) {
    throw new Error("useAssessmentContext must be used within AssessmentProvider");
  }
  return context;
}

export default AssessmentContext;
