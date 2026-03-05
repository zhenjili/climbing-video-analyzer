const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export interface ImprovementFrame {
  time_sec: number;
  image_url: string | null;
  issue: string;
  suggestion: string;
}

export interface AnalysisResult {
  difficulty: string;
  difficulty_explanation: string;
  skill_level: string;
  skill_score: number;
  suggestions: string[];
  improvement_frames: ImprovementFrame[];
}

export interface TaskResponse {
  task_id: string;
  status: "pending" | "processing" | "analyzing" | "complete" | "failed";
  progress: number;
  video_url: string | null;
  analysis: AnalysisResult | null;
  error: string | null;
}

export async function uploadVideo(file: File, language: string = "zh"): Promise<{ task_id: string }> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("language", language);

  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "Upload failed");
  }

  return res.json();
}

export async function getTaskStatus(taskId: string): Promise<TaskResponse> {
  const res = await fetch(`${API_BASE}/tasks/${taskId}`);
  if (!res.ok) throw new Error("Failed to fetch task status");
  return res.json();
}

export function getVideoUrl(path: string): string {
  const base = process.env.NEXT_PUBLIC_API_URL?.replace("/api", "") || "http://localhost:8000";
  return `${base}${path}`;
}
