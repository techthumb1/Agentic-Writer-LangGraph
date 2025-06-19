import { PrismaClient } from "@prisma/client";
import fs from "fs";
import path from "path";
import yaml from "js-yaml";

const prisma = new PrismaClient();

// Define the expected structure for template YAML files
interface TemplateDoc {
  id?: string;
  name?: string;
  title?: string;
  summary?: string;
  description?: string;
  parameters?: Array<{
    name: string;
    type: string;
    description?: string;
    required?: boolean;
    default?: unknown;
  }>;
}

// Define the expected structure for style profile YAML files
interface StyleProfileDoc {
  id?: string;
  name?: string;
  title?: string;
  description?: string;
}

async function main() {
  const templatesDir = path.join(__dirname, "../frontend/content-templates");
  const styleDir = path.join(__dirname, "../frontend/style-profiles");

  // Seed Templates
  for (const file of fs.readdirSync(templatesDir)) {
    if (!file.endsWith(".yaml") && !file.endsWith(".yml")) continue;

    const fullPath = path.join(templatesDir, file);
    const doc = yaml.load(fs.readFileSync(fullPath, "utf8")) as TemplateDoc;

    const slug = doc?.id || path.parse(file).name;
    const name = doc?.name || doc?.title || null;
    const description = doc?.summary || doc?.description || null;
    const parameters = doc?.parameters || [];

    if (!name) {
      console.warn(`Skipping ${file}: missing 'title' or 'name'`);
      continue;
    }

    await prisma.template.upsert({
      where: { slug },
      update: {
        name,
        description,
        parameters: JSON.stringify(parameters),
      },
      create: {
        slug,
        name,
        description,
        parameters: JSON.stringify(parameters),
      },
    });
  }

  // Seed Style Profiles
  for (const file of fs.readdirSync(styleDir)) {
    if (!file.endsWith(".yaml") && !file.endsWith(".yml")) continue;

    const fullPath = path.join(styleDir, file);
    const doc = yaml.load(fs.readFileSync(fullPath, "utf8")) as StyleProfileDoc;

    const slug = doc?.id || path.parse(file).name;
    const name = doc?.name || doc?.title || null;
    const description = doc?.description || null;

    if (!name) {
      console.warn(`Skipping ${file}: missing 'name'`);
      continue;
    }

    await prisma.styleProfile.upsert({
      where: { slug },
      update: {
        name,
        description,
      },
      create: {
        slug,
        name,
        description,
      },
    });
  }

  console.log("Seeded templates and style profiles");
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });