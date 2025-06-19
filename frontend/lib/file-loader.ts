// frontend/lib/file-loader.ts
import fs from 'fs/promises';
import path from 'path';
import YAML from 'yaml';

export async function readYamlFromDir<T>(dir: string): Promise<T[]> {
  const dirPath = path.resolve(process.cwd(), dir);
  const files = await fs.readdir(dirPath);
  const data: T[] = [];

  for (const file of files) {
    const filePath = path.join(dirPath, file);
    const content = await fs.readFile(filePath, 'utf-8');
    const parsed = YAML.parse(content);

    // Auto-inject id and name if missing
    const filename = file.replace(/\.ya?ml$/, '');
    if (!parsed.id) parsed.id = filename;
    if (!parsed.name) parsed.name = filename;

    data.push(parsed);
  }

  return data;
}
