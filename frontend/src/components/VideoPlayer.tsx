"use client";

import { forwardRef, useImperativeHandle, useRef } from "react";
import { getVideoUrl } from "@/lib/api";

export interface VideoPlayerHandle {
  seekTo: (seconds: number) => void;
}

const VideoPlayer = forwardRef<VideoPlayerHandle, { videoPath: string }>(
  function VideoPlayer({ videoPath }, ref) {
    const videoRef = useRef<HTMLVideoElement>(null);

    useImperativeHandle(ref, () => ({
      seekTo(seconds: number) {
        if (videoRef.current) {
          videoRef.current.currentTime = seconds;
          videoRef.current.play();
          videoRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      },
    }));

    return (
      <div className="rounded-xl overflow-hidden bg-black">
        <video
          ref={videoRef}
          controls
          className="w-full"
          src={getVideoUrl(videoPath)}
        >
          Your browser does not support video playback.
        </video>
      </div>
    );
  }
);

export default VideoPlayer;
