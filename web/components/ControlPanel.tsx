"use client";

import type { Detection } from "./DetectionApp";

interface Props {
  confidence: number;
  onConfidenceChange: (v: number) => void;
  imgSize: number;
  onImgSizeChange: (v: number) => void;
  onDetect: () => void;
  loading: boolean;
  hasImage: boolean;
  detections: Detection[];
  enabledClasses: Set<string>;
  onToggleClass: (cls: string) => void;
}

export default function ControlPanel({
  confidence,
  onConfidenceChange,
  imgSize,
  onImgSizeChange,
  onDetect,
  loading,
  hasImage,
  detections,
  enabledClasses,
  onToggleClass,
}: Props) {
  const uniqueClasses = Array.from(new Set(detections.map((d) => d.class_name))).sort();

  return (
    <div className="rounded-xl bg-surface-light p-5">
      <h2 className="mb-4 text-lg font-semibold text-white">Controls</h2>

      <div className="space-y-4">
        <div>
          <label className="mb-1 block text-sm text-gray-400">
            Confidence threshold: {(confidence * 100).toFixed(0)}%
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={confidence}
            onChange={(e) => onConfidenceChange(parseFloat(e.target.value))}
            className="w-full"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm text-gray-400">
            Image size: {imgSize}px
          </label>
          <select
            value={imgSize}
            onChange={(e) => onImgSizeChange(parseInt(e.target.value))}
            className="w-full rounded-lg border border-gray-600 bg-surface px-3 py-2 text-sm text-gray-200 focus:border-accent focus:outline-none"
          >
            <option value={320}>320 (fastest)</option>
            <option value={512}>512 (balanced)</option>
            <option value={640}>640 (accurate)</option>
            <option value={800}>800 (high accuracy)</option>
          </select>
        </div>

        <button
          onClick={onDetect}
          disabled={!hasImage || loading}
          className="w-full rounded-lg bg-accent px-4 py-2.5 font-medium text-white transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Detecting..." : "Detect Objects"}
        </button>

        {uniqueClasses.length > 0 && (
          <div>
            <label className="mb-2 block text-sm text-gray-400">Filter classes</label>
            <div className="flex flex-wrap gap-2">
              {uniqueClasses.map((cls) => (
                <button
                  key={cls}
                  onClick={() => onToggleClass(cls)}
                  className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                    enabledClasses.has(cls)
                      ? "bg-accent text-white"
                      : "bg-surface-lighter text-gray-400"
                  }`}
                >
                  {cls}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
