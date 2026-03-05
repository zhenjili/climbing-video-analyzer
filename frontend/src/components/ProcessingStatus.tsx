"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getTaskStatus, TaskResponse } from "@/lib/api";

const STATUS_LABELS: Record<string, string> = {
  pending: "Waiting in queue...",
  processing: "Analyzing pose & generating skeleton overlay...",
  analyzing: "AI is evaluating your climbing technique...",
  complete: "Analysis complete!",
  failed: "Processing failed",
};

export default function ProcessingStatus({ taskId }: { taskId: string }) {
  const router = useRouter();
  const [task, setTask] = useState<TaskResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const poll = async () => {
      try {
        const data = await getTaskStatus(taskId);
        if (cancelled) return;
        setTask(data);

        if (data.status === "complete") {
          router.push(`/results/${taskId}`);
          return;
        }

        if (data.status === "failed") {
          setError(data.error || "An unknown error occurred");
          return;
        }

        setTimeout(poll, 2000);
      } catch {
        if (!cancelled) setError("Lost connection to server");
      }
    };

    poll();
    return () => { cancelled = true; };
  }, [taskId, router]);

  return (
    <div className="max-w-lg mx-auto text-center">
      <div className="mb-8">
        <div className="animate-pulse text-6xl mb-6">&#x1f9d7;</div>
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          Processing Your Video
        </h2>
        <p className="text-gray-600">
          {task ? STATUS_LABELS[task.status] || task.status : "Connecting..."}
        </p>
      </div>

      <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
        <div
          className="bg-blue-500 h-3 rounded-full transition-all duration-500"
          style={{ width: `${task?.progress ?? 0}%` }}
        />
      </div>
      <p className="text-sm text-gray-500">{task?.progress ?? 0}%</p>

      {error && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600">{error}</p>
          <button
            onClick={() => router.push("/")}
            className="mt-3 text-sm text-blue-600 hover:underline"
          >
            &larr; Try another video
          </button>
        </div>
      )}
    </div>
  );
}
