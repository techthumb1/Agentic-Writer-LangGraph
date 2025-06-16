import fs from "fs";
import path from "path";

export function safeListDirs(baseDir: string): string[] {
  try {
    return fs
      .readdirSync(baseDir, { withFileTypes: true })
      .filter((entry) => entry.isDirectory() && !entry.name.startsWith("."))
      .map((entry) => path.join(baseDir, entry.name));
  } catch (err) {
    console.error("❌ Failed to read directory:", baseDir, err);
    return [];
  }
}
