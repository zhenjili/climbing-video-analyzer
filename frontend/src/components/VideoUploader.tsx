"use client";

import { useCallback, useState } from "react";
import { useRouter } from "next/navigation";
import { uploadVideo } from "@/lib/api";

export default function VideoUploader() {
  const router = useRouter();
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [language, setLanguage] = useState("zh");

  const handleFile = useCallback(
    async (file: File) => {
      const validTypes = ["video/mp4", "video/quicktime", "video/x-msvideo", "video/x-matroska"];
      if (!validTypes.includes(file.type) && !file.name.match(/\.(mp4|mov|avi|mkv)$/i)) {
        setError("Please upload a video file (MP4, MOV, AVI, or MKV)");
        return;
      }

      setError(null);
      setIsUploading(true);

      try {
        const { task_id } = await uploadVideo(file, language);
        router.push(`/processing/${task_id}`);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Upload failed");
        setIsUploading(false);
      }
    },
    [router, language]
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
    <div className="space-y-4">
      <div className="flex justify-end">
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm text-gray-700 bg-white"
        >
          <option value="zh">中文</option>
          <option value="en">English</option>
          <option value="ja">日本語</option>
        </select>
      </div>
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
      {isUploading ? (
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full" />
          <p className="text-gray-600">Uploading video...</p>
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
    </div>
  );
}
