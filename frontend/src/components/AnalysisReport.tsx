import { AnalysisResult, getVideoUrl } from "@/lib/api";

function SkillBar({ score }: { score: number }) {
  const color =
    score >= 80 ? "bg-green-500" : score >= 50 ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="w-full bg-gray-200 rounded-full h-4">
      <div
        className={`${color} h-4 rounded-full transition-all duration-1000`}
        style={{ width: `${score}%` }}
      />
    </div>
  );
}

export default function AnalysisReport({
  analysis,
  onSeek,
}: {
  analysis: AnalysisResult;
  onSeek?: (seconds: number) => void;
}) {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">
          Route Difficulty
        </h3>
        <div className="flex items-baseline gap-3">
          <span className="text-4xl font-bold text-gray-900">
            {analysis.difficulty}
          </span>
        </div>
        <p className="mt-2 text-gray-600">{analysis.difficulty_explanation}</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">
          Your Skill Level
        </h3>
        <div className="flex items-baseline gap-3 mb-3">
          <span className="text-2xl font-bold text-gray-900">
            {analysis.skill_level}
          </span>
          <span className="text-lg text-gray-500">{analysis.skill_score}/100</span>
        </div>
        <SkillBar score={analysis.skill_score} />
      </div>

      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">
          Improvement Tips
        </h3>
        <ul className="space-y-3">
          {analysis.suggestions.map((tip, i) => (
            <li key={i} className="flex gap-3">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm font-medium">
                {i + 1}
              </span>
              <span className="text-gray-700">{tip}</span>
            </li>
          ))}
        </ul>
      </div>

      {analysis.improvement_frames && analysis.improvement_frames.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">
            Needs Improvement
          </h3>
          <div className="space-y-4">
            {analysis.improvement_frames.map((frame, i) => (
              <div key={i} className="flex gap-4 border rounded-lg p-3">
                {frame.image_url && (
                  <img
                    src={getVideoUrl(frame.image_url)}
                    alt={`Frame at ${frame.time_sec}s`}
                    className="w-32 h-24 object-cover rounded flex-shrink-0 cursor-pointer hover:opacity-80 transition-opacity"
                    onClick={() => onSeek?.(frame.time_sec)}
                  />
                )}
                <div className="flex-1 min-w-0 space-y-1.5">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => onSeek?.(frame.time_sec)}
                      className="inline-flex items-center gap-1 text-xs font-mono bg-blue-50 text-blue-600 px-2 py-0.5 rounded hover:bg-blue-100 transition-colors"
                    >
                      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M6.3 2.84A1.5 1.5 0 004 4.11v11.78a1.5 1.5 0 002.3 1.27l9.344-5.891a1.5 1.5 0 000-2.538L6.3 2.841z" />
                      </svg>
                      {frame.time_sec.toFixed(1)}s
                    </button>
                  </div>
                  <p className="text-sm text-red-600 font-medium">{frame.issue}</p>
                  <p className="text-sm text-gray-600">{frame.suggestion}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
