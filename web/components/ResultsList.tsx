"use client";

import type { Detection } from "./DetectionApp";

interface Props {
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

export default function ResultsList({ detections }: Props) {
  if (detections.length === 0) {
    return (
      <div className="rounded-xl bg-surface-light p-5">
        <h2 className="mb-2 text-lg font-semibold text-white">Detections</h2>
        <p className="text-sm text-gray-500">No detections yet</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl bg-surface-light p-5">
      <h2 className="mb-3 text-lg font-semibold text-white">
        Detections ({detections.length})
      </h2>
      <div className="max-h-[400px] space-y-2 overflow-y-auto">
        {detections.map((det, i) => {
          const color = CLASS_COLORS[det.class_name] || "#FFFFFF";
          return (
            <div
              key={i}
              className="flex items-center gap-3 rounded-lg bg-surface-lighter p-3"
            >
              <div
                className="h-3 w-3 shrink-0 rounded-full"
                style={{ backgroundColor: color }}
              />
              <div className="min-w-0 flex-1">
                <div className="flex items-baseline justify-between">
                  <span className="font-medium text-white">{det.class_name}</span>
                  <span className="text-sm text-gray-400">
                    {(det.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="mt-1 text-xs text-gray-500">
                  [{det.bbox.x1.toFixed(0)}, {det.bbox.y1.toFixed(0)}]
                  &mdash;
                  [{det.bbox.x2.toFixed(0)}, {det.bbox.y2.toFixed(0)}]
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
