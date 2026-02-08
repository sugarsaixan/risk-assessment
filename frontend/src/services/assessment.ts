/**
 * Assessment API service for public endpoints.
 */

import { apiClient, getErrorMessage } from "./api";
import type {
  AssessmentForm,
  AttachmentUpload,
  SubmitRequest,
  SubmitResponse,
} from "../types/api";

/** Error response from the API */
interface AssessmentErrorResponse {
  error: "not_found" | "expired" | "already_completed";
  message: string;
}

/** Result type for assessment operations */
export type AssessmentResult<T> =
  | { success: true; data: T }
  | { success: false; error: AssessmentErrorResponse["error"]; message: string };

/**
 * Get assessment form data by token.
 */
export async function getAssessmentForm(
  token: string
): Promise<AssessmentResult<AssessmentForm>> {
  try {
    const response = await apiClient.get<AssessmentForm>(`/a/${token}`);
    return { success: true, data: response.data };
  } catch (error: unknown) {
    // Check for specific error responses
    if (
      error &&
      typeof error === "object" &&
      "response" in error &&
      error.response &&
      typeof error.response === "object" &&
      "status" in error.response &&
      "data" in error.response
    ) {
      const { status, data } = error.response as {
        status: number;
        data: AssessmentErrorResponse;
      };

      if (status === 404) {
        return {
          success: false,
          error: "not_found",
          message: data.message || "Assessment not found",
        };
      }
      if (status === 410) {
        return {
          success: false,
          error: data.error || "expired",
          message: data.message || "Assessment unavailable",
        };
      }
    }

    return {
      success: false,
      error: "not_found",
      message: getErrorMessage(error),
    };
  }
}

/**
 * Upload an image attachment.
 */
export async function uploadImage(
  token: string,
  questionId: string,
  file: File,
  onProgress?: (progress: number) => void
): Promise<AttachmentUpload> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("question_id", questionId);

  const response = await apiClient.post<AttachmentUpload>(
    `/a/${token}/upload`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(progress);
        }
      },
    }
  );

  return response.data;
}

/**
 * Get assessment results by token.
 * Only works for completed assessments.
 */
export async function getAssessmentResults(
  token: string,
  includeBreakdown: boolean = true
): Promise<AssessmentResult<SubmitResponse>> {
  try {
    const params = includeBreakdown ? '?breakdown=true' : '';
    const response = await apiClient.get<SubmitResponse>(`/a/${token}/results${params}`);
    return { success: true, data: response.data };
  } catch (error: unknown) {
    // Check for specific error responses
    if (
      error &&
      typeof error === "object" &&
      "response" in error &&
      error.response &&
      typeof error.response === "object" &&
      "status" in error.response &&
      "data" in error.response
    ) {
      const { status, data } = error.response as {
        status: number;
        data: AssessmentErrorResponse;
      };

      if (status === 404) {
        return {
          success: false,
          error: "not_found",
          message: data.message || "Assessment not found",
        };
      }
      if (status === 400) {
        return {
          success: false,
          error: "not_found",
          message: data.message || "Assessment not completed",
        };
      }
    }

    return {
      success: false,
      error: "not_found",
      message: getErrorMessage(error),
    };
  }
}

/**
 * Submit assessment answers.
 */
export async function submitAssessment(
  token: string,
  data: SubmitRequest
): Promise<AssessmentResult<SubmitResponse>> {
  try {
    const response = await apiClient.post<SubmitResponse>(
      `/a/${token}/submit`,
      data
    );
    return { success: true, data: response.data };
  } catch (error: unknown) {
    // Check for specific error responses
    if (
      error &&
      typeof error === "object" &&
      "response" in error &&
      error.response &&
      typeof error.response === "object" &&
      "status" in error.response &&
      "data" in error.response
    ) {
      const { status, data } = error.response as {
        status: number;
        data: AssessmentErrorResponse | { detail: { errors: string[] } };
      };

      if (status === 404) {
        return {
          success: false,
          error: "not_found",
          message: "Assessment not found",
        };
      }
      if (status === 410) {
        const errorData = data as AssessmentErrorResponse;
        return {
          success: false,
          error: errorData.error || "expired",
          message: errorData.message || "Assessment unavailable",
        };
      }
      if (status === 400) {
        const validationData = data as { detail: { errors: string[] } };
        return {
          success: false,
          error: "not_found", // Using as generic error
          message: validationData.detail?.errors?.join(", ") || "Validation error",
        };
      }
    }

    return {
      success: false,
      error: "not_found",
      message: getErrorMessage(error),
    };
  }
}
