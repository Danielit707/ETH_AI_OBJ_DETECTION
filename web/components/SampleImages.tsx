"use client";

import { useCallback, useState } from "react";

interface Props {
  onImageUpload: (file: File, dataUrl: string) => void;
  disabled?: boolean;
}

const SAMPLES = [
  { src: "/samples/fog.jpg", label: "Fog" },
  { src: "/samples/night.jpg", label: "Night" },
];

export default function SampleImages({ onImageUpload, disabled }: Props) {
  const [loading, setLoading] = useState<string | null>(null);

  const handleSample = useCallback(
    async (src: string, label: string) => {
      setLoading(src);
      try {
        const response = await fetch(src);
        const blob = await response.blob();
        const file = new File([blob], `${label.toLowerCase()}.jpg`, {
          type: "image/jpeg",
        });
        const dataUrl = URL.createObjectURL(blob);
        onImageUpload(file, dataUrl);
      } catch (err) {
        console.error(`Failed to load sample ${src}:`, err);
      }
      setLoading(null);
    },
    [onImageUpload]
  );

  return (
    <div className="flex gap-3">
      {SAMPLES.map((sample) => (
        <button
          key={sample.src}
          onClick={() => handleSample(sample.src, sample.label)}
          disabled={disabled || loading !== null}
          className="group relative overflow-hidden rounded-lg border border-gray-600 transition-colors hover:border-gray-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={sample.src}
            alt={sample.label}
            className="h-20 w-32 object-cover transition-transform group-hover:scale-105"
          />
          <div className="absolute inset-0 flex items-end bg-gradient-to-t from-black/60 to-transparent">
            <span className="p-1.5 text-xs font-medium text-white">
              {loading === sample.src ? "Loading..." : sample.label}
            </span>
          </div>
        </button>
      ))}
    </div>
  );
}
