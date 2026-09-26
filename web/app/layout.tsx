import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Adverse Weather Object Detection",
  description: "Detect objects in adverse-weather images using YOLOv8/YOLO11 on the ACDC dataset",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="bg-surface text-gray-100 antialiased">{children}</body>
    </html>
  );
}
