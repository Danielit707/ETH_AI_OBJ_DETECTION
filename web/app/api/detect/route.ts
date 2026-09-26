import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.DETECTION_API_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const image = formData.get("image");
    const confidence = formData.get("confidence") || "0.25";
    const imageSize = formData.get("image_size") || "512";

    if (!image || !(image instanceof File)) {
      return NextResponse.json(
        { error: "No image file provided" },
        { status: 400 }
      );
    }

    const backendForm = new FormData();
    backendForm.append("image", image);
    backendForm.append("confidence", confidence);
    backendForm.append("image_size", imageSize);

    const response = await fetch(`${API_URL}/predict`, {
      method: "POST",
      body: backendForm,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { error: errorData.detail || `Backend returned ${response.status}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json(
      { error: `Failed to connect to inference API: ${message}` },
      { status: 502 }
    );
  }
}
