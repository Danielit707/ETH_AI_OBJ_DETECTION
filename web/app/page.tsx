import DetectionApp from "@/components/DetectionApp";

export default function Home() {
  return (
    <main className="min-h-screen p-4 md:p-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-white">
            Adverse Weather Object Detection
          </h1>
          <p className="mt-2 text-gray-400">
            Upload an image to detect objects in fog, night, rain, and snow conditions
          </p>
        </header>
        <DetectionApp />
      </div>
    </main>
  );
}
