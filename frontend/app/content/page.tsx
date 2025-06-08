// frontend/app/content/page.tsx

import fs from "fs/promises";
import path from "path";
import Link from "next/link";
import { prettyName } from "@/lib/string";

interface FileCard {
  id: string;        // slug without .json
  week: string;      // week_2
  title: string;
}

export const metadata = { title: "My Content • AI Content Studio" };

export default async function MyContentPage() {
  const baseDir = path.join(process.cwd(), "../storage");
  const cards: FileCard[] = [];

  try {
    const weeks = await fs.readdir(baseDir, { withFileTypes: true });
    for (const wk of weeks) {
      if (!wk.isDirectory() || wk.name.startsWith(".")) continue;
      const weekDir = path.join(baseDir, wk.name);
      const files = await fs.readdir(weekDir);
      for (const file of files) {
        if (!file.endsWith(".json")) continue;
        const filePath = path.join(weekDir, file);
        const json = JSON.parse(await fs.readFile(filePath, "utf8"));
        cards.push({
          id: file.replace(/\.json$/, ""),
          week: wk.name,
          title: json.title ?? prettyName(file.replace(/\.json$/, "")),
        });
      }
    }
  } catch (err) {
    // fail silently – empty list
    console.error("read generated_content error:", err);
  }

  return (
    <main className="max-w-3xl mx-auto py-10">
      <h1 className="text-3xl font-bold mb-6">My Content</h1>

      <ul>
        {cards.map(c => (
          <li
            key={`${c.week}-${c.id}`} 
            className="border rounded p-4 hover:bg-gray-50"
          >
            <Link href={`/content/${c.id}`} className="font-medium text-lg">
              {c.title}
            </Link>
            <p className="text-sm text-muted-foreground">folder: {c.week}</p>
          </li>
        ))}
      </ul>
    </main>
  );
}
