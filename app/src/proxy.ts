import { NextResponse } from "next/server";

export function proxy() {
  if (process.env.POLISCOPE_LIVE_EXTRACTION_ENABLED === "false") {
    return NextResponse.json(
      { error: "Live extraction is unavailable on this deployment. Explore a preloaded candidate." },
      { status: 503 },
    );
  }
  return NextResponse.next();
}

export const config = {
  matcher: "/api/extract",
};
