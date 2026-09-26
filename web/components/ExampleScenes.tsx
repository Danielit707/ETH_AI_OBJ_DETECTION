"use client";

import { useCallback, useState } from "react";

interface Props {
  onImageUpload: (file: File, dataUrl: string) => void;
  disabled?: boolean;
}

type SceneType = "fog-highway" | "night-city" | "rain-street";

function drawFogHighway(canvas: HTMLCanvasElement) {
  const ctx = canvas.getContext("2d")!;
  const w = canvas.width;
  const h = canvas.height;

  // Dark sky
  const skyGrad = ctx.createLinearGradient(0, 0, 0, h * 0.4);
  skyGrad.addColorStop(0, "#0a0a12");
  skyGrad.addColorStop(1, "#1a1a2e");
  ctx.fillStyle = skyGrad;
  ctx.fillRect(0, 0, w, h * 0.4);

  // Ground/road
  ctx.fillStyle = "#1a1a1a";
  ctx.fillRect(0, h * 0.4, w, h * 0.6);

  // Road markings
  ctx.strokeStyle = "#ffffff33";
  ctx.lineWidth = 2;
  ctx.setLineDash([25, 20]);
  ctx.beginPath();
  ctx.moveTo(w / 2, h * 0.4);
  ctx.lineTo(w / 2, h);
  ctx.stroke();
  ctx.setLineDash();

  // Cars
  const cars = [
    { x: 150, y: 280, w: 100, h: 45, color: "#45B7D1" },
    { x: 380, y: 320, w: 90, h: 40, color: "#FF6B6B" },
    { x: 280, y: 250, w: 80, h: 35, color: "#96CEB4" },
  ];
  cars.forEach((car) => {
    ctx.fillStyle = car.color;
    ctx.beginPath();
    ctx.roundRect(car.x, car.y, car.w, car.h, 6);
    ctx.fill();
    ctx.fillStyle = "#111";
    ctx.beginPath();
    ctx.arc(car.x + 15, car.y + car.h, 10, 0, Math.PI * 2);
    ctx.arc(car.x + car.w - 15, car.y + car.h, 10, 0, Math.PI * 2);
    ctx.fill();
  });

  // Heavy fog overlay
  const fogGrad = ctx.createLinearGradient(0, h * 0.2, 0, h * 0.7);
  fogGrad.addColorStop(0, "rgba(180, 180, 200, 0)");
  fogGrad.addColorStop(0.5, "rgba(180, 180, 200, 0.35)");
  fogGrad.addColorStop(1, "rgba(180, 180, 200, 0)");
  ctx.fillStyle = fogGrad;
  ctx.fillRect(0, h * 0.2, w, h * 0.5);
}

function drawNightCity(canvas: HTMLCanvasElement) {
  const ctx = canvas.getContext("2d")!;
  const w = canvas.width;
  const h = canvas.height;

  // Night sky
  ctx.fillStyle = "#050510";
  ctx.fillRect(0, 0, w, h);

  // Buildings
  const buildings = [
    { x: 20, y: 80, w: 80, h: 200, color: "#0d0d1a" },
    { x: 120, y: 120, w: 60, h: 160, color: "#111125" },
    { x: 200, y: 60, w: 90, h: 220, color: "#0a0a18" },
    { x: 310, y: 100, w: 70, h: 180, color: "#0f0f20" },
    { x: 400, y: 70, w: 85, h: 210, color: "#0c0c1c" },
    { x: 505, y: 110, w: 65, h: 170, color: "#101022" },
  ];
  buildings.forEach((b) => {
    ctx.fillStyle = b.color;
    ctx.fillRect(b.x, b.y, b.w, b.h);
    // Windows
    ctx.fillStyle = "#ffee8833";
    for (let wy = b.y + 10; wy < b.y + b.h - 10; wy += 18) {
      for (let wx = b.x + 8; wx < b.x + b.w - 8; wx += 14) {
        if (Math.random() > 0.5) ctx.fillRect(wx, wy, 6, 8);
      }
    }
  });

  // Street
  ctx.fillStyle = "#111";
  ctx.fillRect(0, h - 60, w, 60);

  // Car with headlights
  ctx.fillStyle = "#FF6B6B";
  ctx.beginPath();
  ctx.roundRect(250, h - 100, 120, 50, 8);
  ctx.fill();
  ctx.fillStyle = "#ffee88";
  ctx.beginPath();
  ctx.arc(360, h - 80, 8, 0, Math.PI * 2);
  ctx.fill();

  // Street light
  ctx.strokeStyle = "#333";
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(180, h - 60);
  ctx.lineTo(180, h - 180);
  ctx.stroke();
  ctx.fillStyle = "#ffee8855";
  ctx.beginPath();
  ctx.arc(180, h - 185, 15, 0, Math.PI * 2);
  ctx.fill();
}

function drawRainStreet(canvas: HTMLCanvasElement) {
  const ctx = canvas.getContext("2d")!;
  const w = canvas.width;
  const h = canvas.height;

  // Wet sky
  const skyGrad = ctx.createLinearGradient(0, 0, 0, h * 0.35);
  skyGrad.addColorStop(0, "#1a1a28");
  skyGrad.addColorStop(1, "#252538");
  ctx.fillStyle = skyGrad;
  ctx.fillRect(0, 0, w, h * 0.35);

  // Wet road with reflections
  const roadGrad = ctx.createLinearGradient(0, h * 0.35, 0, h);
  roadGrad.addColorStop(0, "#1c1c24");
  roadGrad.addColorStop(1, "#0e0e14");
  ctx.fillStyle = roadGrad;
  ctx.fillRect(0, h * 0.35, w, h * 0.65);

  // Reflections
  ctx.fillStyle = "#45B7D122";
  ctx.fillRect(180, h * 0.5, 80, 8);
  ctx.fillRect(400, h * 0.55, 60, 6);

  // Pedestrian with umbrella
  ctx.fillStyle = "#4ECDC4";
  ctx.beginPath();
  ctx.arc(200, 200, 12, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillRect(192, 210, 16, 35);
  // Umbrella
  ctx.fillStyle = "#FFEAA7";
  ctx.beginPath();
  ctx.arc(200, 195, 25, Math.PI, 0);
  ctx.fill();

  // Car
  ctx.fillStyle = "#96CEB4";
  ctx.beginPath();
  ctx.roundRect(350, 260, 110, 50, 8);
  ctx.fill();
  ctx.fillStyle = "#111";
  ctx.beginPath();
  ctx.arc(370, 310, 12, 0, Math.PI * 2);
  ctx.arc(440, 310, 12, 0, Math.PI * 2);
  ctx.fill();

  // Rain streaks
  ctx.strokeStyle = "#aabbcc33";
  ctx.lineWidth = 1;
  for (let i = 0; i < 80; i++) {
    const x = Math.random() * w;
    const y = Math.random() * h;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x + 2, y + 12);
    ctx.stroke();
  }
}

const SCENES: { type: SceneType; label: string; draw: (c: HTMLCanvasElement) => void }[] = [
  { type: "fog-highway", label: "Fog Highway", draw: drawFogHighway },
  { type: "night-city", label: "Night City", draw: drawNightCity },
  { type: "rain-street", label: "Rain Street", draw: drawRainStreet },
];

export default function ExampleScenes({ onImageUpload, disabled }: Props) {
  const [generating, setGenerating] = useState<SceneType | null>(null);

  const handleScene = useCallback(
    (scene: (typeof SCENES)[number]) => {
      setGenerating(scene.type);
      setTimeout(() => {
        const canvas = document.createElement("canvas");
        canvas.width = 640;
        canvas.height = 480;
        scene.draw(canvas);
        const dataUrl = canvas.toDataURL("image/png");
        const byteString = atob(dataUrl.split(",")[1]);
        const ab = new ArrayBuffer(byteString.length);
        const ia = new Uint8Array(ab);
        for (let i = 0; i < byteString.length; i++) {
          ia[i] = byteString.charCodeAt(i);
        }
        const blob = new Blob([ab], { type: "image/png" });
        const file = new File([blob], `${scene.type}.png`, { type: "image/png" });
        onImageUpload(file, dataUrl);
        setGenerating(null);
      }, 50);
    },
    [onImageUpload]
  );

  return (
    <div className="flex flex-wrap gap-2">
      {SCENES.map((scene) => (
        <button
          key={scene.type}
          onClick={() => handleScene(scene)}
          disabled={disabled || generating !== null}
          className="rounded-lg border border-gray-600 bg-surface-light px-3 py-2 text-xs text-gray-300 transition-colors hover:border-gray-500 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          {generating === scene.type ? "Generating..." : scene.label}
        </button>
      ))}
    </div>
  );
}
