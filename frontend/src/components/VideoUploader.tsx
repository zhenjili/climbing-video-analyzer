"use client";

import { useCallback, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { uploadVideo } from "@/lib/api";

export default function VideoUploader() {
  const router = useRouter();
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isPreparing, setIsPreparing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const pendingFileRef = useRef<File | null>(null);

  const startUpload = useCallback(
    async (file: File) => {
      setIsPreparing(false);
      setIsUploading(true);
      setUploadProgress(0);

      try {
        const { task_id } = await uploadVideo(file, setUploadProgress);
        router.push(`/processing/${task_id}`);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Upload failed");
        setIsUploading(false);
      }
    },
    [router]
  );

  const handleFile = useCallback(
    (file: File) => {
      const validTypes = ["video/mp4", "video/quicktime", "video/x-msvideo", "video/x-matroska"];
      if (!validTypes.includes(file.type) && !file.name.match(/\.(mp4|mov|avi|mkv)$/i)) {
        setError("Please upload a video file (MP4, MOV, AVI, or MKV)");
        return;
      }

      setError(null);
      // Show preparing state immediately so the mobile gallery can dismiss
      setIsPreparing(true);
      pendingFileRef.current = file;

      // Defer the actual upload to the next frame, allowing the
      // mobile file picker / photo gallery to close first
      setTimeout(() => {
        const pending = pendingFileRef.current;
        if (pending) {
          pendingFileRef.current = null;
          startUpload(pending);
        }
      }, 100);
    },
    [startUpload]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      className={`border-2 border-dashed rounded-2xl p-12 text-center transition-colors cursor-pointer ${
        isDragging
          ? "border-blue-500 bg-blue-50"
          : "border-gray-300 hover:border-gray-400"
      }`}
    >
      {isPreparing ? (
        <div className="flex flex-col items-center gap-4 w-full max-w-xs mx-auto py-4">
          <div className="w-10 h-10 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin" />
          <p className="text-gray-600 text-sm">Loading video...</p>
        </div>
      ) : isUploading ? (
        <div className="flex flex-col items-center gap-4 w-full max-w-xs mx-auto">
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className="bg-blue-500 h-full rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
          <p className="text-gray-600 text-sm">
            {uploadProgress < 100
              ? `Uploading... ${uploadProgress}%`
              : "Processing, please wait..."}
          </p>
        </div>
      ) : (
        <label className="cursor-pointer flex flex-col items-center gap-4">
          <svg className="w-12 h-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 16l4-4m0 0l4 4m-4-4v12M21 12V4a2 2 0 00-2-2h-6l-2 2H5a2 2 0 00-2 2v4" />
          </svg>
          <div>
            <p className="text-lg font-medium text-gray-700">
              Drop your climbing video here
            </p>
            <p className="text-sm text-gray-500 mt-1">
              or click to browse (MP4, MOV, AVI, MKV up to 100MB)
            </p>
          </div>
          <input
            type="file"
            accept="video/*"
            onChange={handleChange}
            className="hidden"
          />
        </label>
      )}
      {error && <p className="mt-4 text-red-500 text-sm">{error}</p>}
    </div>
  );
}
