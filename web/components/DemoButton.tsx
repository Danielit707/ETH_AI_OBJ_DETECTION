"use client";

import { useCallback, useState } from "react";

interface Props {
  onImageUpload: (file: File, dataUrl: string) => void;
  disabled?: boolean;
}

function generateDemoImage(): { file: File; dataUrl: string } {
  const canvas = document.createElement("canvas");
  canvas.width = 640;
  canvas.height = 480;
  const ctx = canvas.getContext("2d")!;

  // Sky gradient
  const skyGrad = ctx.createLinearGradient(0, 0, 0, 200);
  skyGrad.addColorStop(0, "#1a1a2e");
  skyGrad.addColorStop(1, "#16213e");
  ctx.fillStyle = skyGrad;
  ctx.fillRect(0, 0, 640, 200);

  // Road
  const roadGrad = ctx.createLinearGradient(0, 200, 0, 480);
  roadGrad.addColorStop(0, "#2d2d2d");
  roadGrad.addColorStop(1, "#1a1a1a");
  ctx.fillStyle = roadGrad;
  ctx.fillRect(0, 200, 640, 280);

  // Road lines
  ctx.strokeStyle = "#ffffff44";
  ctx.lineWidth = 2;
  ctx.setLineDash([20, 15]);
  ctx.beginPath();
  ctx.moveTo(320, 200);
  ctx.lineTo(320, 480);
  ctx.stroke();
  ctx.setLineDash();

  // Car 1
  ctx.fillStyle = "#45B7D1";
  ctx.beginPath();
  ctx.roundRect(200, 260, 120, 60, 8);
  ctx.fill();
  ctx.fillStyle = "#2a6f7f";
  ctx.beginPath();
  ctx.roundRect(215, 250, 90, 30, 6);
  ctx.fill();
  ctx.fillStyle = "#1a1a2e";
  ctx.beginPath();
  ctx.arc(225, 320, 15, 0, Math.PI * 2);
  ctx.arc(295, 320, 15, 0, Math.PI * 2);
  ctx.fill();

  // Car 2
  ctx.fillStyle = "#FF6B6B";
  ctx.beginPath();
  ctx.roundRect(420, 300, 100, 50, 8);
  ctx.fill();
  ctx.fillStyle = "#cc5555";
  ctx.beginPath();
  ctx.roundRect(435, 290, 70, 25, 6);
  ctx.fill();
  ctx.fillStyle = "#1a1a2e";
  ctx.beginPath();
  ctx.arc(440, 350, 12, 0, Math.PI * 2);
  ctx.arc(500, 350, 12, 0, Math.PI * 2);
  ctx.fill();

  // Person
  ctx.fillStyle = "#4ECDC4";
  ctx.beginPath();
  ctx.arc(100, 280, 12, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillRect(92, 290, 16, 35);

  // Bicycle
  ctx.strokeStyle = "#98D8C8";
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.arc(550, 340, 18, 0, Math.PI * 2);
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(590, 340, 18, 0, Math.PI * 2);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(550, 340);
  ctx.lineTo(570, 310);
  ctx.lineTo(590, 340);
  ctx.stroke();

  // Fog effect
  const fogGrad = ctx.createLinearGradient(0, 150, 0, 350);
  fogGrad.addColorStop(0, "rgba(200, 200, 220, 0)");
  fogGrad.addColorStop(0.5, "rgba(200, 200, 220, 0.15)");
  fogGrad.addColorStop(1, "rgba(200, 200, 220, 0)");
  ctx.fillStyle = fogGrad;
  ctx.fillRect(0, 150, 640, 200);

  const dataUrl = canvas.toDataURL("image/png");
  const byteString = atob(dataUrl.split(",")[1]);
  const mimeString = dataUrl.split(",")[0].split(":")[1].split(";")[0];
  const ab = new ArrayBuffer(byteString.length);
  const ia = new Uint8Array(ab);
  for (let i = 0; i < byteString.length; i++) {
    ia[i] = byteString.charCodeAt(i);
  }
  const blob = new Blob([ab], { type: mimeString });
  const file = new File([blob], "demo-scene.png", { type: "image/png" });
  return { file, dataUrl };
}

export default function DemoButton({ onImageUpload, disabled }: Props) {
  const [loading, setLoading] = useState(false);

  const handleDemo = useCallback(async () => {
    setLoading(true);
    try {
      const { file, dataUrl } = generateDemoImage();
      onImageUpload(file, dataUrl);
    } finally {
      setLoading(false);
    }
  }, [onImageUpload]);

  return (
    <button
      onClick={handleDemo}
      disabled={disabled || loading}
      className="rounded-lg border border-gray-600 bg-surface-light px-4 py-2 text-sm text-gray-300 transition-colors hover:border-gray-500 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
    >
      {loading ? "Generating..." : "Try Demo Scene"}
    </button>
  );
}
