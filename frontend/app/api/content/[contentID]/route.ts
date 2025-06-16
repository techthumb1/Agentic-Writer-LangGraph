// frontend/app/api/content/[contentID]/route.ts

import { NextRequest, NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";

export async function GET(
  request: NextRequest,
  context: { params: { contentID: string } }  // ✅ THIS must be named `context` and destructured later
) {
  try {
    const contentID = context.params.contentID;  // ✅ Don't destructure inline — use `context.params.contentID`
    const baseDir = path.join(process.cwd(), "../storage");

    for (const week of await fs.readdir(baseDir)) {
      const filePath = path.join(baseDir, week, `${contentID}.json`);
      try {
        const file = await fs.readFile(filePath, "utf-8");
        return NextResponse.json(JSON.parse(file));
      } catch {
        continue; // keep searching other folders
      }
    }

    return NextResponse.json({ error: "File not found" }, { status: 404 });
  } catch (err) {
    const msg = err instanceof Error ? err.message : "Failed to read content";
    console.error("[api/content] error:", msg);
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
