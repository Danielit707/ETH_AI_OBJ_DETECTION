"use client";

import { useCallback, useRef, useState } from "react";
import ImageUploader from "./ImageUploader";
import DetectionCanvas from "./DetectionCanvas";
import ControlPanel from "./ControlPanel";
import ResultsList from "./ResultsList";

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
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const handleImageUpload = useCallback((file: File, dataUrl: string) => {
    setImage(dataUrl);
    setImageFile(file);
    setDetections([]);
    setError(null);
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

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_340px]">
      <div className="space-y-4">
        <ImageUploader onImageUpload={handleImageUpload} loading={loading} />
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
  );
}
