// frontend/app/api/content/[contentID]/route.ts
import { NextRequest, NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";

export async function GET(
  _req: NextRequest,
  context: { params: { contentID: string } }
) {
  try {
    const { contentID } = context.params;                  // ✅ new
    const baseDir = path.join(process.cwd(), "generated_content");

    for (const week of await fs.readdir(baseDir)) {
      const filePath = path.join(baseDir, week, `${contentID}.json`);
      try {
        const file = await fs.readFile(filePath, "utf-8");
        return NextResponse.json(JSON.parse(file));
      } catch { /* keep searching */ }
    }
    return NextResponse.json({ error: "File not found" }, { status: 404 });
  } catch (err) {
    console.error("read-content error", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Server error" },
      { status: 500 }
    );
  }
}
