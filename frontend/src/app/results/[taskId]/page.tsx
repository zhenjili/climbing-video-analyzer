"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { getTaskStatus, TaskResponse } from "@/lib/api";
import VideoPlayer, { VideoPlayerHandle } from "@/components/VideoPlayer";
import AnalysisReport from "@/components/AnalysisReport";

export default function ResultsPage({
  params,
}: {
  params: Promise<{ taskId: string }>;
}) {
  const router = useRouter();
  const videoRef = useRef<VideoPlayerHandle>(null);
  const [task, setTask] = useState<TaskResponse | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);

  useEffect(() => {
    params.then((p) => setTaskId(p.taskId));
  }, [params]);

  useEffect(() => {
    if (!taskId) return;
    getTaskStatus(taskId).then(setTask).catch(() => router.push("/"));
  }, [taskId, router]);

  if (!task || task.status !== "complete") {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full" />
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Analysis Results</h1>
          <button
            onClick={() => router.push("/")}
            className="text-blue-600 hover:underline text-sm"
          >
            &larr; Analyze another video
          </button>
        </div>

        <div className="space-y-8">
          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-4">
              Skeleton Overlay
            </h2>
            {task.video_url && <VideoPlayer ref={videoRef} videoPath={task.video_url} />}
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-4">
              AI Analysis
            </h2>
            {task.analysis && (
              <AnalysisReport
                analysis={task.analysis}
                onSeek={(sec) => videoRef.current?.seekTo(sec)}
              />
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
