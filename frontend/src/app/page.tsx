import VideoUploader from "@/components/VideoUploader";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-3xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Climbing Video Analyzer
          </h1>
          <p className="text-lg text-gray-600">
            Upload your climbing video and get AI-powered analysis of your technique,
            difficulty assessment, and personalized improvement tips.
          </p>
        </div>

        <VideoUploader />

        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="text-3xl mb-3">&#x1f9b4;</div>
            <h3 className="font-semibold text-gray-800 mb-2">Pose Detection</h3>
            <p className="text-sm text-gray-600">
              AI tracks your body movements frame by frame with skeleton overlay
            </p>
          </div>
          <div className="text-center">
            <div className="text-3xl mb-3">&#x1f4ca;</div>
            <h3 className="font-semibold text-gray-800 mb-2">Difficulty Rating</h3>
            <p className="text-sm text-gray-600">
              Get an estimated V-scale difficulty for the route you climbed
            </p>
          </div>
          <div className="text-center">
            <div className="text-3xl mb-3">&#x1f4a1;</div>
            <h3 className="font-semibold text-gray-800 mb-2">Smart Tips</h3>
            <p className="text-sm text-gray-600">
              Receive personalized suggestions to improve your climbing technique
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
