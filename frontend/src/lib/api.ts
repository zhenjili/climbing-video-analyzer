const API_BASE = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api").trim();
const BACKEND_BASE = API_BASE.replace(/\/api\/?$/, "");

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

export async function uploadVideo(
  file: File,
  onProgress?: (percent: number) => void,
): Promise<{ task_id: string }> {
  const formData = new FormData();
  formData.append("file", file);

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${API_BASE}/upload`);

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    };

    xhr.onload = () => {
      try {
        const data = JSON.parse(xhr.responseText);
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(data);
        } else {
          reject(new Error(data.detail || "Upload failed"));
        }
      } catch {
        reject(new Error("Upload failed"));
      }
    };

    xhr.onerror = () => reject(new Error("Network error"));
    xhr.send(formData);
  });
}

export async function getTaskStatus(taskId: string): Promise<TaskResponse> {
  const res = await fetch(`${API_BASE}/tasks/${taskId}`);
  if (!res.ok) throw new Error("Failed to fetch task status");
  return res.json();
}

export function getVideoUrl(path: string): string {
  return `${BACKEND_BASE}${path}`;
}
