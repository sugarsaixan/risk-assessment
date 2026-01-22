/**
 * ImageUpload component with drag-drop, preview, and progress.
 */

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { MN } from "../constants/mn";

interface UploadedImage {
  id: string;
  name: string;
  size: number;
  preview?: string;
  progress: number;
  error?: string;
}

interface ImageUploadProps {
  /** List of uploaded images */
  images: UploadedImage[];
  /** Callback when files are selected for upload */
  onUpload: (files: File[]) => void;
  /** Callback when an image is removed */
  onRemove: (imageId: string) => void;
  /** Whether images are required */
  required?: boolean;
  /** Maximum number of images allowed */
  maxImages?: number;
  /** Maximum file size in MB */
  maxSizeMb?: number;
  /** Whether uploading is in progress */
  isUploading?: boolean;
  /** Error message to display */
  error?: string;
  /** Whether the component is disabled */
  disabled?: boolean;
  /** Optional CSS class names */
  className?: string;
}

const ACCEPTED_TYPES = {
  "image/jpeg": [".jpg", ".jpeg"],
  "image/png": [".png"],
  "image/gif": [".gif"],
  "image/webp": [".webp"],
};

export function ImageUpload({
  images,
  onUpload,
  onRemove,
  required = false,
  maxImages = 3,
  maxSizeMb = 5,
  isUploading = false,
  error,
  disabled = false,
  className = "",
}: ImageUploadProps) {
  const [dragError, setDragError] = useState<string | null>(null);
  const canAddMore = images.length < maxImages;

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: { file: File; errors: { message: string }[] }[]) => {
      setDragError(null);

      // Handle rejected files
      if (rejectedFiles.length > 0) {
        const firstError = rejectedFiles[0].errors[0];
        if (firstError.message.includes("larger than")) {
          setDragError(MN.upload.fileTooLarge);
        } else {
          setDragError(MN.upload.invalidType);
        }
        return;
      }

      // Check if adding these would exceed max
      const slotsAvailable = maxImages - images.length;
      const filesToUpload = acceptedFiles.slice(0, slotsAvailable);

      if (filesToUpload.length > 0) {
        onUpload(filesToUpload);
      }
    },
    [images.length, maxImages, onUpload]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxSize: maxSizeMb * 1024 * 1024,
    disabled: disabled || !canAddMore,
    multiple: true,
  });

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className={`w-full ${className}`}>
      {/* Label */}
      <label className="block form-label">
        {MN.assessment.requiredImage}
        {required && <span className="text-red-500 ml-1">*</span>}
        <span className="font-normal label-muted ml-2">
          ({MN.upload.maxImages(maxImages)})
        </span>
      </label>

      {/* Dropzone */}
      {canAddMore && (
        <div
          {...getRootProps()}
          className={`upload-dropzone ${
            disabled
              ? "upload-dropzone-disabled cursor-not-allowed"
              : "cursor-pointer"
          } ${
            isDragActive && !isDragReject
              ? "upload-dropzone-active"
              : isDragReject
              ? "upload-dropzone-reject"
              : ""
          }`}
        >
          <input {...getInputProps()} />

          <div className="space-y-2">
            {/* Upload icon */}
            <svg
              className={`mx-auto h-12 w-12 ${
                isDragActive ? "text-[var(--app-accent-2)]" : "text-[var(--app-muted)]"
              }`}
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
              aria-hidden="true"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>

            <p className="text-sm label-muted">
              {isDragActive ? (
                <span className="text-[var(--app-accent-2)] font-medium">{MN.upload.dragDrop}</span>
              ) : (
                <>
                  {MN.upload.dragDrop} {MN.upload.or}{" "}
                  <span className="text-[var(--app-accent)] font-medium">{MN.upload.browse}</span>
                </>
              )}
            </p>

            <p className="text-xs label-muted">
              {MN.upload.allowedTypes} • {MN.upload.maxSize(maxSizeMb)}
            </p>
          </div>
        </div>
      )}

      {/* Drag error */}
      {dragError && <p className="mt-2 text-sm text-red-600">{dragError}</p>}

      {/* Error message */}
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}

      {/* Image previews */}
      {images.length > 0 && (
        <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 gap-4">
          {images.map((image) => (
            <div
              key={image.id}
              className="relative group rounded-xl overflow-hidden border border-[var(--app-border)] bg-[var(--app-surface)]"
            >
              {/* Preview image */}
              {image.preview ? (
                <img
                  src={image.preview}
                  alt={image.name}
                  className="w-full h-24 object-cover"
                />
              ) : (
                <div className="w-full h-24 flex items-center justify-center text-[var(--app-muted)]">
                  <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                </div>
              )}

              {/* Progress overlay */}
              {image.progress < 100 && !image.error && (
                <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                  <div className="text-white text-sm font-medium">{image.progress}%</div>
                </div>
              )}

              {/* Error overlay */}
              {image.error && (
                <div className="absolute inset-0 bg-red-500/50 flex items-center justify-center">
                  <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
              )}

              {/* File info */}
              <div className="p-2 text-xs truncate">
                <p className="font-medium truncate">{image.name}</p>
                <p className="label-muted">{formatFileSize(image.size)}</p>
              </div>

              {/* Remove button */}
              <button
                type="button"
                onClick={() => onRemove(image.id)}
                disabled={disabled}
                className="absolute top-1 right-1 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity
                  disabled:cursor-not-allowed hover:bg-red-600"
                aria-label={MN.upload.remove}
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Upload status */}
      {isUploading && (
        <p className="mt-2 text-sm text-[var(--app-accent)] flex items-center">
          <svg className="animate-spin h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          {MN.upload.uploading}
        </p>
      )}
    </div>
  );
}

export default ImageUpload;
