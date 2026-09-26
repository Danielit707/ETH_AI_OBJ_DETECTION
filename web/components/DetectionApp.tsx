"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import ImageUploader from "./ImageUploader";
import DetectionCanvas from "./DetectionCanvas";
import ControlPanel from "./ControlPanel";
import ResultsList from "./ResultsList";
import ApiStatus from "./ApiStatus";
import StatsBar from "./StatsBar";
import DemoButton from "./DemoButton";
import ExampleScenes from "./ExampleScenes";

export interface Detection {
  class_id: number;
  class_name: string;
  confidence: number;
  bbox: { x1: number; y1: number; x2: number; y2: number };
}

export interface PredictionResponse {
  width: number;
  height: number;
  detections: Detection[];
}

const CLASS_COLORS: Record<string, string> = {
  person: "#FF6B6B",
  rider: "#4ECDC4",
  car: "#45B7D1",
  truck: "#96CEB4",
  bus: "#FFEAA7",
  train: "#DDA0DD",
  motorcycle: "#FF8C42",
  bicycle: "#98D8C8",
};

export default function DetectionApp() {
  const [image, setImage] = useState<string | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [imageSize, setImageSize] = useState({ width: 0, height: 0 });
  const [confidence, setConfidence] = useState(0.25);
  const [imgSizeParam, setImgSizeParam] = useState(512);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [enabledClasses, setEnabledClasses] = useState<Set<string>>(new Set());
  const [apiStatus, setApiStatus] = useState<"checking" | "online" | "offline">("checking");
  const [inferenceTime, setInferenceTime] = useState<number | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const checkApi = async () => {
      try {
        const res = await fetch("/api/detect", { method: "OPTIONS" });
        setApiStatus(res.ok || res.status === 405 ? "online" : "offline");
      } catch {
        try {
          await fetch("http://localhost:8000/health", { signal: AbortSignal.timeout(2000) });
          setApiStatus("online");
        } catch {
          setApiStatus("offline");
        }
      }
    };
    checkApi();
    const interval = setInterval(checkApi, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleImageUpload = useCallback((file: File, dataUrl: string) => {
    setImage(dataUrl);
    setImageFile(file);
    setDetections([]);
    setError(null);
    setInferenceTime(null);
    const img = new Image();
    img.onload = () => {
      setImageSize({ width: img.naturalWidth, height: img.naturalHeight });
    };
    img.src = dataUrl;
  }, []);

  const handleDetect = useCallback(async () => {
    if (!imageFile) return;
    setLoading(true);
    setError(null);
    setInferenceTime(null);
    const startTime = performance.now();
    try {
      const formData = new FormData();
      formData.append("image", imageFile);
      formData.append("confidence", confidence.toString());
      formData.append("image_size", imgSizeParam.toString());

      const response = await fetch("/api/detect", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.error || `Request failed with status ${response.status}`);
      }

      const data: PredictionResponse = await response.json();
      const elapsed = performance.now() - startTime;
      setInferenceTime(elapsed);
      setDetections(data.detections);
      const uniqueClasses = new Set(data.detections.map((d) => d.class_name));
      setEnabledClasses(uniqueClasses);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Detection failed");
      setDetections([]);
    } finally {
      setLoading(false);
    }
  }, [imageFile, confidence, imgSizeParam]);

  const filteredDetections = detections.filter(
    (d) => d.confidence >= confidence && enabledClasses.has(d.class_name)
  );

  const toggleClass = (className: string) => {
    setEnabledClasses((prev) => {
      const next = new Set(prev);
      if (next.has(className)) next.delete(className);
      else next.add(className);
      return next;
    });
  };

  const exportResults = () => {
    if (!image || filteredDetections.length === 0) return;
    const dataUrl = canvasRef.current?.toDataURL("image/png");
    if (dataUrl) {
      const link = document.createElement("a");
      link.download = "detection-result.png";
      link.href = dataUrl;
      link.click();
    }
  };

  const exportJson = () => {
    if (filteredDetections.length === 0) return;
    const blob = new Blob([JSON.stringify(filteredDetections, null, 2)], {
      type: "application/json",
    });
    const link = document.createElement("a");
    link.download = "detections.json";
    link.href = URL.createObjectURL(blob);
    link.click();
    URL.revokeObjectURL(link.href);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <ApiStatus status={apiStatus} />
        {inferenceTime !== null && (
          <span className="text-sm text-gray-400">
            Inference: {inferenceTime.toFixed(0)} ms
          </span>
        )}
      </div>

      <StatsBar detections={filteredDetections} />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_340px]">
        <div className="space-y-4">
          <div className="flex flex-col gap-3">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-stretch">
              <div className="flex-1">
                <ImageUploader onImageUpload={handleImageUpload} loading={loading} />
              </div>
              <div className="flex items-center">
                <DemoButton onImageUpload={handleImageUpload} disabled={loading} />
              </div>
            </div>
            <ExampleScenes onImageUpload={handleImageUpload} disabled={loading} />
          </div>
          {image && (
            <DetectionCanvas
              imageUrl={image}
              detections={filteredDetections}
              imageSize={imageSize}
              canvasRef={canvasRef}
            />
          )}
          {error && (
            <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-400">
              {error}
            </div>
          )}
          {filteredDetections.length > 0 && (
            <div className="flex gap-2">
              <button
                onClick={exportResults}
                className="rounded-lg bg-surface-lighter px-4 py-2 text-sm text-gray-300 transition-colors hover:bg-gray-700"
              >
                Download Image
              </button>
              <button
                onClick={exportJson}
                className="rounded-lg bg-surface-lighter px-4 py-2 text-sm text-gray-300 transition-colors hover:bg-gray-700"
              >
                Export JSON
              </button>
            </div>
          )}
        </div>
        <div className="space-y-4">
          <ControlPanel
            confidence={confidence}
            onConfidenceChange={setConfidence}
            imgSize={imgSizeParam}
            onImgSizeChange={setImgSizeParam}
            onDetect={handleDetect}
            loading={loading}
            hasImage={!!imageFile}
            detections={detections}
            enabledClasses={enabledClasses}
            onToggleClass={toggleClass}
          />
          <ResultsList detections={filteredDetections} />
        </div>
      </div>
    </div>
  );
}
