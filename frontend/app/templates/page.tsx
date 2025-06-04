import fs from "fs/promises";
import path from "path";
import { prettyName } from "@/lib/string";

export const metadata = { title: "Templates • AI Content Studio" };

export default async function TemplatesPage() {
  const tplDir = path.join(process.cwd(), "content_templates");
  let names: string[] = [];

  try {
    names = (await fs.readdir(tplDir))
      .filter(f => f.endsWith(".yaml"))
      .map(f => f.replace(/\.yaml$/, ""));
  } catch (err) {
    console.error("read content_templates error:", err);
  }

  return (
    <main className="max-w-2xl mx-auto py-10">
      <h1 className="text-3xl font-bold mb-6">Available Templates</h1>

      {names.length === 0 ? (
        <p className="text-muted-foreground">No templates found.</p>
      ) : (
        <ul className="grid gap-3">
          {names.map(n => (
            <li key={n} className="border rounded p-3">
              {prettyName(n)}
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
