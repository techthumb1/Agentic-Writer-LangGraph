import { NextRequest, NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";

export async function GET(
  request: NextRequest,
  { params }: { params: { contentID: string } }
) {
  try {
    const contentID = params.contentID;
    const baseDir = path.join(process.cwd(), "generated_content");
    let content = "";
    
    // Search subfolders like week_1/, week_2/
    const weeks = await fs.readdir(baseDir);
    for (const week of weeks) {
      const tryPath = path.join(baseDir, week, `${contentID}.md`);
      try {
        content = await fs.readFile(tryPath, "utf-8");
        break; // found it
      } catch {
        continue;
      }
    }
    
    if (!content) {
      return NextResponse.json({ error: "File not found" }, { status: 404 });
    }
    return NextResponse.json({ content });
  } catch (error: unknown) {
    console.error("Error reading content:", error);
    return NextResponse.json({ error: error instanceof Error ? error.message : "Failed to read content" }, { status: 500 });
  }
}
