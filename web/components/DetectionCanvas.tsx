"use client";

import { useEffect, useRef } from "react";
import type { Detection } from "./DetectionApp";

interface Props {
  imageUrl: string;
  detections: Detection[];
  imageSize: { width: number; height: number };
  canvasRef: React.RefObject<HTMLCanvasElement>;
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

export default function DetectionCanvas({
  imageUrl,
  detections,
  imageSize,
  canvasRef,
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !imageSize.width) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const img = new Image();
    img.onload = () => {
      const containerWidth = containerRef.current?.clientWidth || 800;
      const scale = containerWidth / imageSize.width;
      const displayWidth = containerWidth;
      const displayHeight = imageSize.height * scale;

      canvas.width = displayWidth;
      canvas.height = displayHeight;

      ctx.drawImage(img, 0, 0, displayWidth, displayHeight);

      detections.forEach((det) => {
        const color = CLASS_COLORS[det.class_name] || "#FFFFFF";
        const x = det.bbox.x1 * scale;
        const y = det.bbox.y1 * scale;
        const w = (det.bbox.x2 - det.bbox.x1) * scale;
        const h = (det.bbox.y2 - det.bbox.y1) * scale;

        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, w, h);

        const label = `${det.class_name} ${(det.confidence * 100).toFixed(0)}%`;
        ctx.font = "bold 12px system-ui, sans-serif";
        const metrics = ctx.measureText(label);
        const labelHeight = 18;
        const labelWidth = metrics.width + 8;

        ctx.fillStyle = color;
        ctx.fillRect(x, y - labelHeight, labelWidth, labelHeight);
        ctx.fillStyle = "#000";
        ctx.fillText(label, x + 4, y - 5);
      });
    };
    img.src = imageUrl;
  }, [imageUrl, detections, imageSize, canvasRef]);

  return (
    <div ref={containerRef} className="overflow-hidden rounded-xl bg-surface-light">
      <canvas
        ref={canvasRef}
        className="w-full"
        style={{ display: "block" }}
      />
    </div>
  );
}
