/**
 * Draft API service for saving and loading assessment drafts.
 */

import axios from "axios";

import { apiClient, getErrorMessage } from "./api";
import type { OptionType } from "../types/api";

// ============================================================================
// Types
// ============================================================================

export interface DraftAnswer {
  question_id: string;
  selected_option?: OptionType | null;
  comment?: string | null;
  attachment_ids?: string[];
}

export interface DraftSaveRequest {
  answers: DraftAnswer[];
  current_type_index?: number;
  current_group_index?: number;
}

export interface DraftSaveResponse {
  last_saved_at: string;
  message?: string;
}

export interface DraftResponse {
  answers: DraftAnswer[];
  current_type_index?: number;
  current_group_index?: number;
  last_saved_at: string;
}

export type DraftResult<T> =
  | { success: true; data: T }
  | { success: false; message: string };

// ============================================================================
// API Functions
// ============================================================================

/**
 * Save draft answers for an assessment.
 * Uses PUT with upsert semantics (creates or updates).
 */
export async function saveDraft(
  token: string,
  data: DraftSaveRequest
): Promise<DraftResult<DraftSaveResponse>> {
  try {
    const response = await apiClient.put<DraftSaveResponse>(
      `/a/${token}/draft`,
      data
    );
    return { success: true, data: response.data };
  } catch (error: unknown) {
    // Detect network errors and rate limiting
    if (axios.isAxiosError(error)) {
      if (!error.response) {
        return { success: false, message: "Сүлжээний алдаа" };
      }
      if (error.response.status === 429) {
        return { success: false, message: "Хэт олон хүсэлт. Түр хүлээнэ үү." };
      }
    }
    return {
      success: false,
      message: getErrorMessage(error),
    };
  }
}

/**
 * Load saved draft for an assessment.
 * Returns null data if no draft exists (204 response).
 */
/**
 * Extract Retry-After delay in milliseconds from a 429 response.
 * Returns a default of 5000ms if the header is missing.
 */
export function getRetryAfterMs(error: unknown): number {
  if (axios.isAxiosError(error) && error.response?.headers) {
    const retryAfter = error.response.headers["retry-after"];
    if (retryAfter) {
      const seconds = parseInt(retryAfter, 10);
      if (!isNaN(seconds)) return seconds * 1000;
    }
  }
  return 5000;
}

/**
 * Load saved draft for an assessment.
 * Returns null data if no draft exists (204 response).
 */
export async function loadDraft(
  token: string
): Promise<DraftResult<DraftResponse | null>> {
  try {
    const response = await apiClient.get<DraftResponse>(`/a/${token}/draft`);

    // 204 No Content means no draft exists
    if (response.status === 204) {
      return { success: true, data: null };
    }

    return { success: true, data: response.data };
  } catch (error: unknown) {
    // 204 may also come as an error in some axios configurations
    if (
      error &&
      typeof error === "object" &&
      "response" in error &&
      error.response &&
      typeof error.response === "object" &&
      "status" in error.response &&
      error.response.status === 204
    ) {
      return { success: true, data: null };
    }

    // Rate limiting
    if (axios.isAxiosError(error) && error.response?.status === 429) {
      return { success: false, message: "Хэт олон хүсэлт. Түр хүлээнэ үү." };
    }

    // Network error
    if (axios.isAxiosError(error) && !error.response) {
      return { success: false, message: "Сүлжээний алдаа" };
    }

    return {
      success: false,
      message: getErrorMessage(error),
    };
  }
}
