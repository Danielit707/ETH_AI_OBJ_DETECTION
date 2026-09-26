"use client";

import { useCallback, useState } from "react";

interface Props {
  onImageUpload: (file: File, dataUrl: string) => void;
  loading: boolean;
}

export default function ImageUploader({ onImageUpload, loading }: Props) {
  const [isDragging, setIsDragging] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);

  const handleFile = useCallback(
    (file: File) => {
      if (!file.type.startsWith("image/")) return;
      const reader = new FileReader();
      reader.onload = (e) => {
        const dataUrl = e.target?.result as string;
        setPreview(dataUrl);
        onImageUpload(file, dataUrl);
      };
      reader.readAsDataURL(file);
    },
    [onImageUpload]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => setIsDragging(false), []);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  return (
    <div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      className={`relative flex min-h-[200px] cursor-pointer items-center justify-center rounded-xl border-2 border-dashed transition-colors ${
        isDragging
          ? "border-accent bg-accent/10"
          : "border-gray-600 bg-surface-light hover:border-gray-500"
      }`}
    >
      <input
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={handleInputChange}
        className="absolute inset-0 cursor-pointer opacity-0"
        disabled={loading}
      />
      {preview ? (
        <img
          src={preview}
          alt="Preview"
          className="max-h-[400px] rounded-lg object-contain"
        />
      ) : (
        <div className="p-8 text-center">
          <div className="mb-3 text-4xl font-light text-gray-500">+</div>
          <p className="text-gray-300">
            Drag & drop an image here, or click to browse
          </p>
          <p className="mt-1 text-sm text-gray-500">JPEG, PNG, WebP (max 10 MB)</p>
          <p className="mt-3 text-xs text-gray-600">
            Or use the &quot;Try Demo Scene&quot; button
          </p>
        </div>
      )}
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center rounded-xl bg-black/50">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-gray-600 border-t-accent" />
        </div>
      )}
    </div>
  );
}
