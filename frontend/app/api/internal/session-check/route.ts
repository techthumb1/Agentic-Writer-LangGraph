// app/api/internal/session-check/route.ts
import { NextResponse } from "next/server";
import { auth } from "@/auth";  // <- IMPORTANT: from "@/auth", not from the route

export async function GET() {
  const session = await auth();

  return NextResponse.json({
    authenticated: !!session?.user,
    user: session?.user ?? null,
  });
}
