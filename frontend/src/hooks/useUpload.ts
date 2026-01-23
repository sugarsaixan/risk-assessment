/**
 * Hook to handle image upload with progress tracking.
 */

import { useCallback, useState } from "react";
import { uploadImage } from "../services/assessment";
import type { AttachmentUpload } from "../types/api";

export interface UploadedFile {
  id: string;
  name: string;
  size: number;
  preview?: string;
  progress: number;
  error?: string;
}

interface UseUploadOptions {
  token: string;
  questionId: string;
  maxFiles?: number;
  maxSizeMb?: number;
}

interface UseUploadReturn {
  files: UploadedFile[];
  isUploading: boolean;
  upload: (file: File) => Promise<AttachmentUpload | null>;
  remove: (fileId: string) => void;
  clear: () => void;
  getAttachmentIds: () => string[];
}

/**
 * Hook to manage file uploads with progress tracking.
 *
 * @param options - Upload configuration
 * @returns Upload state and functions
 */
export function useUpload({
  token,
  questionId,
  maxFiles = 3,
  maxSizeMb = 5,
}: UseUploadOptions): UseUploadReturn {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const upload = useCallback(
    async (file: File): Promise<AttachmentUpload | null> => {
      // Check if we can add more files
      if (files.length >= maxFiles) {
        return null;
      }

      // Validate file size
      const maxBytes = maxSizeMb * 1024 * 1024;
      if (file.size > maxBytes) {
        return null;
      }

      // Create preview URL for images
      const preview = file.type.startsWith("image/")
        ? URL.createObjectURL(file)
        : undefined;

      // Create temporary file entry
      const tempId = `temp-${Date.now()}-${Math.random().toString(36).slice(2)}`;
      const newFile: UploadedFile = {
        id: tempId,
        name: file.name,
        size: file.size,
        ...(preview ? { preview } : {}),
        progress: 0,
      };

      setFiles((prev) => [...prev, newFile]);
      setIsUploading(true);

      try {
        // Upload with progress tracking
        const result = await uploadImage(token, questionId, file, (progress) => {
          setFiles((prev) =>
            prev.map((f) => (f.id === tempId ? { ...f, progress } : f))
          );
        });

        // Update file with server ID
        setFiles((prev) =>
          prev.map((f) =>
            f.id === tempId
              ? { ...f, id: result.id, progress: 100 }
              : f
          )
        );

        setIsUploading(false);
        return result;
      } catch (error) {
        // Mark file as failed
        setFiles((prev) =>
          prev.map((f) =>
            f.id === tempId
              ? { ...f, error: "Upload failed", progress: 0 }
              : f
          )
        );
        setIsUploading(false);
        return null;
      }
    },
    [token, questionId, files.length, maxFiles, maxSizeMb]
  );

  const remove = useCallback((fileId: string) => {
    setFiles((prev) => {
      const file = prev.find((f) => f.id === fileId);
      // Revoke preview URL if exists
      if (file?.preview) {
        URL.revokeObjectURL(file.preview);
      }
      return prev.filter((f) => f.id !== fileId);
    });
  }, []);

  const clear = useCallback(() => {
    // Revoke all preview URLs
    files.forEach((file) => {
      if (file.preview) {
        URL.revokeObjectURL(file.preview);
      }
    });
    setFiles([]);
  }, [files]);

  const getAttachmentIds = useCallback(() => {
    return files
      .filter((f) => !f.error && !f.id.startsWith("temp-"))
      .map((f) => f.id);
  }, [files]);

  return {
    files,
    isUploading,
    upload,
    remove,
    clear,
    getAttachmentIds,
  };
}

/**
 * Hook to manage uploads for multiple questions.
 */
export function useMultiQuestionUpload(token: string) {
  const [uploads, setUploads] = useState<Map<string, UploadedFile[]>>(new Map());
  const [uploadingQuestions, setUploadingQuestions] = useState<Set<string>>(
    new Set()
  );

  const uploadForQuestion = useCallback(
    async (
      questionId: string,
      file: File,
      maxFiles: number = 3,
      maxSizeMb: number = 5
    ): Promise<AttachmentUpload | null> => {
      const currentFiles = uploads.get(questionId) || [];

      // Check limits
      if (currentFiles.length >= maxFiles) return null;
      if (file.size > maxSizeMb * 1024 * 1024) return null;

      const preview = file.type.startsWith("image/")
        ? URL.createObjectURL(file)
        : undefined;

      const tempId = `temp-${Date.now()}-${Math.random().toString(36).slice(2)}`;
      const newFile: UploadedFile = {
        id: tempId,
        name: file.name,
        size: file.size,
        ...(preview ? { preview } : {}),
        progress: 0,
      };

      setUploads((prev) => {
        const updated = new Map(prev);
        updated.set(questionId, [...(prev.get(questionId) || []), newFile]);
        return updated;
      });

      setUploadingQuestions((prev) => new Set(prev).add(questionId));

      try {
        const result = await uploadImage(token, questionId, file, (progress) => {
          setUploads((prev) => {
            const updated = new Map(prev);
            const files = prev.get(questionId) || [];
            updated.set(
              questionId,
              files.map((f) => (f.id === tempId ? { ...f, progress } : f))
            );
            return updated;
          });
        });

        setUploads((prev) => {
          const updated = new Map(prev);
          const files = prev.get(questionId) || [];
          updated.set(
            questionId,
            files.map((f) =>
              f.id === tempId ? { ...f, id: result.id, progress: 100 } : f
            )
          );
          return updated;
        });

        setUploadingQuestions((prev) => {
          const updated = new Set(prev);
          updated.delete(questionId);
          return updated;
        });

        return result;
      } catch (error) {
        setUploads((prev) => {
          const updated = new Map(prev);
          const files = prev.get(questionId) || [];
          updated.set(
            questionId,
            files.map((f) =>
              f.id === tempId ? { ...f, error: "Upload failed", progress: 0 } : f
            )
          );
          return updated;
        });

        setUploadingQuestions((prev) => {
          const updated = new Set(prev);
          updated.delete(questionId);
          return updated;
        });

        return null;
      }
    },
    [token, uploads]
  );

  const removeFromQuestion = useCallback((questionId: string, fileId: string) => {
    setUploads((prev) => {
      const updated = new Map(prev);
      const files = prev.get(questionId) || [];
      const file = files.find((f) => f.id === fileId);
      if (file?.preview) {
        URL.revokeObjectURL(file.preview);
      }
      updated.set(
        questionId,
        files.filter((f) => f.id !== fileId)
      );
      return updated;
    });
  }, []);

  const getFilesForQuestion = useCallback(
    (questionId: string): UploadedFile[] => {
      return uploads.get(questionId) || [];
    },
    [uploads]
  );

  const getAttachmentIdsForQuestion = useCallback(
    (questionId: string): string[] => {
      const files = uploads.get(questionId) || [];
      return files
        .filter((f) => !f.error && !f.id.startsWith("temp-"))
        .map((f) => f.id);
    },
    [uploads]
  );

  const isUploadingForQuestion = useCallback(
    (questionId: string): boolean => {
      return uploadingQuestions.has(questionId);
    },
    [uploadingQuestions]
  );

  return {
    uploadForQuestion,
    removeFromQuestion,
    getFilesForQuestion,
    getAttachmentIdsForQuestion,
    isUploadingForQuestion,
  };
}

export default useUpload;
