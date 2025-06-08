// frontend/app/content/page.tsx
import Link from "next/link";
import fs from "fs/promises";
import path from "path";
import { prettyName } from "@/lib/string";

interface FileCard {
  slug: string;          // ← store the filename w/o extension
  week: string;
}

export const metadata = { title: "My Content • AI Content Studio" };

export default async function MyContentPage() {
  const baseDir = path.join(process.cwd(), "../storage");
  const cards: FileCard[] = [];

  try {
    for (const week of await fs.readdir(baseDir)) {
      const weekDir = path.join(baseDir, week);
    
      try {
        const stat = await fs.stat(weekDir);
        if (!stat.isDirectory() || week.startsWith(".")) continue;
      } catch {
        continue;
  }

  const files = await fs.readdir(weekDir);
  for (const file of files) {
    if (file.endsWith(".json")) {
      cards.push({
        slug: file.replace(/\.json$/, ""),
        week
      });
    }
  }
}

  } catch (err) {
    console.error("[content list] read error:", err);   // 👈 use it
    return (
      <p className="p-8 text-red-500">
        Failed to read storage — {err instanceof Error ? err.message : "unknown error"}.
      </p>
    );
  }

  if (cards.length === 0)
    return <p className="p-8 text-muted-foreground">No articles yet.</p>;

  /* ---------- render ---------- */
  return (
    <ul className="space-y-4 p-8">
      {cards.map((c) => (
        <li
          key={`${c.week}-${c.slug}`}               // ✅ unique key
          className="flex justify-between items-center border p-4 rounded-lg"
        >
          <div>
            <p className="font-medium">{prettyName(c.slug)}</p>
            <p className="text-xs text-muted-foreground">{c.week}</p>
          </div>

          {/* ✅ Correct link and href */}
          <Link
            href={`/content/${c.slug}`}
            className="text-blue-600 hover:underline"
          >
            View →
          </Link>
        </li>
      ))}
    </ul>
  );
}
