/**
 * useAutoSave hook - auto-saves draft every 30s and on answer changes (debounced).
 */

import { useCallback, useEffect, useRef, useState } from "react";

import { saveDraft, getRetryAfterMs } from "../services/draft";
import type { DraftSaveRequest } from "../services/draft";

// ============================================================================
// Types
// ============================================================================

export type AutoSaveStatus = "idle" | "saving" | "saved" | "error";

interface UseAutoSaveOptions {
  /** Assessment token */
  token: string | undefined;
  /** Current draft data to save */
  data: DraftSaveRequest | null;
  /** Auto-save interval in ms (default: 30000) */
  interval?: number;
  /** Debounce delay for change detection in ms (default: 2000) */
  debounceDelay?: number;
  /** Whether auto-save is enabled (default: true) */
  enabled?: boolean;
}

interface UseAutoSaveReturn {
  /** Current save status */
  status: AutoSaveStatus;
  /** Last saved timestamp (ISO string) */
  lastSavedAt: string | null;
  /** Error message if save failed */
  error: string | null;
  /** Manually trigger a save */
  saveNow: () => Promise<void>;
  /** Whether a save is in progress */
  isSaving: boolean;
}

// ============================================================================
// Constants
// ============================================================================

const MAX_RETRIES = 3;
const BASE_RETRY_DELAY_MS = 1000;
const SAVE_FAILURE_MESSAGE = "Хадгалж чадсангүй";

// ============================================================================
// Hook
// ============================================================================

export function useAutoSave({
  token,
  data,
  interval = 30000,
  debounceDelay = 2000,
  enabled = true,
}: UseAutoSaveOptions): UseAutoSaveReturn {
  const [status, setStatus] = useState<AutoSaveStatus>("idle");
  const [lastSavedAt, setLastSavedAt] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Refs to avoid stale closures
  const dataRef = useRef(data);
  const lastSavedDataRef = useRef<string | null>(null);
  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const intervalTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const isSavingRef = useRef(false);
  const retryCountRef = useRef(0);
  const prevDataStrRef = useRef<string | null>(null);
  const rateLimitedRef = useRef(false);

  // Update data ref on every change
  dataRef.current = data;

  /**
   * Perform the actual save operation with retry logic.
   * @param force - Skip change detection (used for manual saves)
   */
  const performSave = useCallback(async (force = false) => {
    if (!token || !dataRef.current) return;
    if (isSavingRef.current) return;

    // Check if data has changed since last save (skip for forced/manual saves)
    const currentDataStr = JSON.stringify(dataRef.current);
    if (!force && currentDataStr === lastSavedDataRef.current) return;

    isSavingRef.current = true;
    setStatus("saving");
    setError(null);

    let lastError: string | null = null;
    let succeeded = false;

    for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
      // Wait before retry (exponential backoff)
      if (attempt > 0) {
        const delay = rateLimitedRef.current
          ? getRetryAfterMs(null) // Use default 5s for rate-limited retries
          : BASE_RETRY_DELAY_MS * Math.pow(2, attempt - 1);
        rateLimitedRef.current = false;
        await new Promise((resolve) => setTimeout(resolve, delay));
      }

      const result = await saveDraft(token, dataRef.current);

      if (result.success) {
        succeeded = true;
        retryCountRef.current = 0;
        setStatus("saved");
        setLastSavedAt(result.data.last_saved_at);
        lastSavedDataRef.current = currentDataStr;

        // Reset to idle after 3 seconds
        setTimeout(() => {
          setStatus((prev) => (prev === "saved" ? "idle" : prev));
        }, 3000);
        break;
      }

      lastError = result.message;

      // Track rate limiting for longer backoff
      if (lastError?.includes("Хэт олон хүсэлт")) {
        rateLimitedRef.current = true;
      }
    }

    isSavingRef.current = false;

    if (!succeeded) {
      setStatus("error");
      setError(lastError || SAVE_FAILURE_MESSAGE);
    }
  }, [token]);

  /**
   * Manual save trigger - forces save even if data hasn't changed.
   */
  const saveNow = useCallback(async () => {
    await performSave(true);
  }, [performSave]);

  // Debounced save on data change (value-based comparison to avoid
  // resetting timer on every render when watch() returns new references)
  const dataStr = data ? JSON.stringify(data) : null;
  useEffect(() => {
    if (!enabled || !token || !dataStr) return;

    // Only trigger debounce when the serialized data actually changed
    if (dataStr === prevDataStrRef.current) return;
    prevDataStrRef.current = dataStr;

    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    debounceTimerRef.current = setTimeout(() => {
      performSave();
    }, debounceDelay);

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [dataStr, enabled, token, debounceDelay, performSave]);

  // Interval-based auto-save (every 30s)
  useEffect(() => {
    if (!enabled || !token) return;

    intervalTimerRef.current = setInterval(() => {
      performSave();
    }, interval);

    return () => {
      if (intervalTimerRef.current) {
        clearInterval(intervalTimerRef.current);
      }
    };
  }, [enabled, token, interval, performSave]);

  return {
    status,
    lastSavedAt,
    error,
    saveNow,
    isSaving: status === "saving",
  };
}

export default useAutoSave;
