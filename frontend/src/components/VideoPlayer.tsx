"use client";

import { getVideoUrl } from "@/lib/api";

export default function VideoPlayer({ videoPath }: { videoPath: string }) {
  return (
    <div className="rounded-xl overflow-hidden bg-black">
      <video
        controls
        className="w-full"
        src={getVideoUrl(videoPath)}
      >
        Your browser does not support video playback.
      </video>
    </div>
  );
}
