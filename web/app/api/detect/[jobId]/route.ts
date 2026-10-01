import { NextResponse } from "next/server";

const API_URL = process.env.DETECTION_API_URL || "http://localhost:8000";

export const dynamic = "force-dynamic";

export async function GET(
  _request: Request,
  { params }: { params: { jobId: string } }
) {
  try {
    const response = await fetch(
      `${API_URL}/predict/jobs/${encodeURIComponent(params.jobId)}`,
      { cache: "no-store", signal: AbortSignal.timeout(10000) }
    );
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json(
      { error: `Failed to get prediction status: ${message}` },
      { status: 502 }
    );
  }
}
