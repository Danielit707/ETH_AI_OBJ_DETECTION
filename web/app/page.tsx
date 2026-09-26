import DetectionApp from "@/components/DetectionApp";

export default function Home() {
  return (
    <main className="min-h-screen p-4 md:p-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">
                Adverse Weather Object Detection
              </h1>
              <p className="mt-2 max-w-2xl text-gray-400">
                Detect objects in fog, night, rain, and snow conditions using
                YOLO11 on the ACDC dataset. Upload an image or try the demo scene.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex h-fit items-center rounded-lg border border-gray-600 bg-surface-light px-4 py-2 text-sm text-gray-300 transition-colors hover:border-gray-500 hover:text-white"
              >
                API Docs
              </a>
              <a
                href="https://github.com/Danielit707/ETH_AI_OBJ_DETECTION"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex h-fit items-center rounded-lg border border-gray-600 bg-surface-light px-4 py-2 text-sm text-gray-300 transition-colors hover:border-gray-500 hover:text-white"
              >
                GitHub
              </a>
            </div>
          </div>
        </header>
        <DetectionApp />
      </div>
    </main>
  );
}
