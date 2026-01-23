import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from "axios";

/**
 * API client configuration and instance.
 */

// Base URL from environment or default to localhost
const API_BASE_URL =
  import.meta.env["VITE_API_URL"] || "http://localhost:8000";

/**
 * Create configured axios instance for API requests.
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Error response from the API.
 */
export interface ApiError {
  detail: string;
  code?: string;
}

/**
 * Validation error response from the API.
 */
export interface ValidationError {
  detail: Array<{
    loc: string[];
    msg: string;
    type: string;
  }>;
}

/**
 * Type guard to check if error is an API error.
 */
export function isApiError(error: unknown): error is AxiosError<ApiError> {
  return axios.isAxiosError(error) && error.response?.data?.detail !== undefined;
}

/**
 * Type guard to check if error is a validation error.
 */
export function isValidationError(
  error: unknown
): error is AxiosError<ValidationError> {
  return (
    axios.isAxiosError(error) && Array.isArray(error.response?.data?.detail)
  );
}

/**
 * Extract error message from API error.
 */
export function getErrorMessage(error: unknown): string {
  if (isApiError(error)) {
    return error.response?.data.detail || "An error occurred";
  }
  if (isValidationError(error)) {
    const firstError = error.response?.data.detail[0];
    return firstError?.msg || "Validation error";
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "An unexpected error occurred";
}

/**
 * Make a GET request.
 */
export async function get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const response = await apiClient.get<T>(url, config);
  return response.data;
}

/**
 * Make a POST request.
 */
export async function post<T, D = unknown>(
  url: string,
  data?: D,
  config?: AxiosRequestConfig
): Promise<T> {
  const response = await apiClient.post<T>(url, data, config);
  return response.data;
}

/**
 * Make a PATCH request.
 */
export async function patch<T, D = unknown>(
  url: string,
  data?: D,
  config?: AxiosRequestConfig
): Promise<T> {
  const response = await apiClient.patch<T>(url, data, config);
  return response.data;
}

/**
 * Make a DELETE request.
 */
export async function del<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const response = await apiClient.delete<T>(url, config);
  return response.data;
}

/**
 * Upload a file with progress tracking.
 */
export async function uploadFile<T>(
  url: string,
  file: File,
  onProgress?: (progress: number) => void,
  config?: AxiosRequestConfig
): Promise<T> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await apiClient.post<T>(url, formData, {
    ...config,
    headers: {
      ...config?.headers,
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
  });

  return response.data;
}
