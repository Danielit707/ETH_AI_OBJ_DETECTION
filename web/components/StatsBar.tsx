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

export default function StatsBar({ detections }: Props) {
  if (detections.length === 0) return null;

  const classCounts: Record<string, number> = {};
  let totalConfidence = 0;

  detections.forEach((d) => {
    classCounts[d.class_name] = (classCounts[d.class_name] || 0) + 1;
    totalConfidence += d.confidence;
  });

  const avgConfidence = totalConfidence / detections.length;

  return (
    <div className="flex flex-wrap items-center gap-3 rounded-xl bg-surface-light px-5 py-3">
      <div className="flex items-center gap-2">
        <span className="text-2xl font-bold text-white">{detections.length}</span>
        <span className="text-sm text-gray-400">objects</span>
      </div>
      <div className="h-6 w-px bg-gray-700" />
      <div className="flex items-center gap-2">
        <span className="text-2xl font-bold text-white">
          {(avgConfidence * 100).toFixed(0)}%
        </span>
        <span className="text-sm text-gray-400">avg conf</span>
      </div>
      <div className="h-6 w-px bg-gray-700" />
      <div className="flex flex-wrap gap-2">
        {Object.entries(classCounts)
          .sort((a, b) => b[1] - a[1])
          .map(([cls, count]) => (
            <span
              key={cls}
              className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium"
              style={{
                backgroundColor: `${CLASS_COLORS[cls]}20`,
                color: CLASS_COLORS[cls],
              }}
            >
              <span
                className="h-1.5 w-1.5 rounded-full"
                style={{ backgroundColor: CLASS_COLORS[cls] }}
              />
              {count} {cls}
            </span>
          ))}
      </div>
    </div>
  );
}
