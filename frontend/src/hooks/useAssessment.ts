/**
 * Hook to fetch assessment form data and handle loading/error states.
 * Supports hierarchical Type → Group → Question structure.
 */

import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getAssessmentForm } from "../services/assessment";
import type { AssessmentForm, SnapshotQuestion } from "../types/api";

export type AssessmentState =
  | { status: "loading" }
  | { status: "success"; data: AssessmentForm }
  | { status: "error"; error: "not_found" | "expired" | "already_completed"; message: string };

interface UseAssessmentReturn {
  state: AssessmentState;
  refetch: () => Promise<void>;
}

/**
 * Hook to fetch and manage assessment form data.
 *
 * @param token - The assessment token from URL
 * @returns Assessment state and refetch function
 */
export function useAssessment(token: string | undefined): UseAssessmentReturn {
  const navigate = useNavigate();
  const [state, setState] = useState<AssessmentState>({ status: "loading" });

  const fetchAssessment = useCallback(async () => {
    if (!token) {
      setState({
        status: "error",
        error: "not_found",
        message: "No token provided",
      });
      return;
    }

    setState({ status: "loading" });

    const result = await getAssessmentForm(token);

    if (result.success) {
      setState({ status: "success", data: result.data });
    } else {
      setState({
        status: "error",
        error: result.error,
        message: result.message,
      });

      // Navigate to appropriate error page
      switch (result.error) {
        case "expired":
          navigate("/expired", { replace: true });
          break;
        case "already_completed":
          navigate("/used", { replace: true });
          break;
        case "not_found":
          navigate("/not-found", { replace: true });
          break;
      }
    }
  }, [token, navigate]);

  useEffect(() => {
    fetchAssessment();
  }, [fetchAssessment]);

  return {
    state,
    refetch: fetchAssessment,
  };
}

/**
 * Extended question type with group and type info.
 */
interface ExtendedQuestion extends SnapshotQuestion {
  typeName: string;
  typeId: string;
  groupName: string;
  groupId: string;
}

/**
 * Helper to get all questions from assessment form.
 * Traverses hierarchical Type → Group → Question structure.
 */
export function getAllQuestions(form: AssessmentForm): ExtendedQuestion[] {
  return form.types.flatMap((type) =>
    type.groups.flatMap((group) =>
      group.questions.map((q) => ({
        ...q,
        typeName: type.name,
        typeId: type.id,
        groupName: group.name,
        groupId: group.id,
      }))
    )
  );
}

/**
 * Helper to count total questions.
 * Traverses hierarchical Type → Group → Question structure.
 */
export function getTotalQuestions(form: AssessmentForm): number {
  return form.types.reduce(
    (sum, type) =>
      sum +
      type.groups.reduce((groupSum, group) => groupSum + group.questions.length, 0),
    0
  );
}

export default useAssessment;
