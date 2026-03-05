import ProcessingStatus from "@/components/ProcessingStatus";

export default async function ProcessingPage({
  params,
}: {
  params: Promise<{ taskId: string }>;
}) {
  const { taskId } = await params;
  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white flex items-center justify-center px-4">
      <ProcessingStatus taskId={taskId} />
    </main>
  );
}
