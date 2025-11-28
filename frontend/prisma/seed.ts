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
  category?: string;
  difficulty?: string;
  estimatedLength?: string;
  targetAudience?: string;
  icon?: string;
  tags?: string[];
  parameters?: Array<{
    name: string;
    type: string;
    description?: string;
    required?: boolean;
    default?: string | number | boolean; // More specific than unknown
  }>;
  [key: string]: unknown; // Index signature for JSON compatibility
}

// Define the expected structure for style profile YAML files
interface StyleProfileDoc {
  id?: string;
  name?: string;
  title?: string;
  description?: string;
  category?: string;
  icon?: string;
  tags?: string[];
  profileData?: Record<string, unknown>;
  [key: string]: unknown; // Index signature for JSON compatibility
}

// Helper function to generate consistent IDs
function generateId(filename: string, doc: TemplateDoc | StyleProfileDoc): string {
  return doc?.id || path.parse(filename).name.toLowerCase().replace(/[^a-z0-9]/g, '_');
}

async function main() {
  try {
    const templatesDir = path.join(__dirname, "../frontend/content-templates");
    const styleDir = path.join(__dirname, "../frontend/style-profiles");

    console.log("🌱 Starting database seeding...");

    // Check if directories exist
    if (!fs.existsSync(templatesDir)) {
      console.warn(`⚠️ Templates directory not found: ${templatesDir}`);
    }
    if (!fs.existsSync(styleDir)) {
      console.warn(`⚠️ Style profiles directory not found: ${styleDir}`);
    }

    // Seed Content Templates (matching your schema exactly)
    if (fs.existsSync(templatesDir)) {
      console.log("📄 Seeding content templates...");
      
      for (const file of fs.readdirSync(templatesDir)) {
        if (!file.endsWith(".yaml") && !file.endsWith(".yml")) continue;

        try {
          const fullPath = path.join(templatesDir, file);
          const doc = yaml.load(fs.readFileSync(fullPath, "utf8")) as TemplateDoc;

          // Generate consistent ID
          const id = generateId(file, doc);
          
          // Extract data matching your schema fields
          const title = doc?.name || doc?.title || path.parse(file).name;
          const description = doc?.summary || doc?.description || null; // Can be null in your schema
          const category = doc?.category || "general";
          const difficulty = doc?.difficulty || null;
          const estimatedLength = doc?.estimatedLength || null;
          const targetAudience = doc?.targetAudience || null;
          const icon = doc?.icon || null;
          const tags = doc?.tags || [];
          
          // Store template data as JSON with proper typing
          const templateData = {
            parameters: doc?.parameters || [],
            metadata: {
              originalFilename: file,
              loadedAt: new Date().toISOString(),
            },
            // Include other properties as needed
            ...(doc && typeof doc === 'object' ? doc : {}),
          };

          // Ensure templateData is valid for Prisma's Json type

          // Use ContentTemplate model with correct unique field (id)
          await prisma.contentTemplate.upsert({
            where: { id }, // Use id as unique field
            update: {
              title,
              description,
              templateData,
              category,
              difficulty,
              estimatedLength,
              targetAudience,
              icon,
              tags,
              isBuiltIn: true, // Mark as built-in template
            },
            create: {
              id,
              title,
              description,
              templateData,
              category,
              difficulty,
              estimatedLength,
              targetAudience,
              icon,
              tags,
              isBuiltIn: true,
              isPublic: true, // Make built-in templates public
            },
          });

          console.log(`✅ Seeded template: ${title} (${id})`);
        } catch (error) {
          console.error(`❌ Failed to seed template from ${file}:`, error);
        }
      }
    }

    // Seed Style Profiles (matching your schema exactly)
    if (fs.existsSync(styleDir)) {
      console.log("🎨 Seeding style profiles...");
      
      for (const file of fs.readdirSync(styleDir)) {
        if (!file.endsWith(".yaml") && !file.endsWith(".yml")) continue;

        try {
          const fullPath = path.join(styleDir, file);
          const doc = yaml.load(fs.readFileSync(fullPath, "utf8")) as StyleProfileDoc;

          // Generate consistent ID
          const id = generateId(file, doc);
          
          // Extract data matching your schema fields
          const name = doc?.name || doc?.title || path.parse(file).name;
          const description = doc?.description || `Style profile: ${name}`; // Required field, never null
          const category = doc?.category || "general";
          const icon = doc?.icon || null;
          const tags = doc?.tags || [];
          
          // Store profile data as JSON with proper typing
          const profileData = {
            metadata: {
              originalFilename: file,
              loadedAt: new Date().toISOString(),
            },
            // Include the full document data
            ...(doc && typeof doc === 'object' ? doc : {}),
          } as Record<string, unknown>;

          // Use StyleProfile model with correct unique field (id)
          await prisma.styleProfile.upsert({
            where: { id }, // Use id as unique field
            update: {
              name,
              description,
              profileData: JSON.parse(JSON.stringify(profileData)),
              category,
              icon,
              tags,
              isBuiltIn: true,
            },
            create: {
              id,
              name,
              description,
              profileData: JSON.parse(JSON.stringify(profileData)),
              category,
              icon,
              tags,
              isBuiltIn: true,
              isPublic: true, // Make built-in profiles public
            },
          });

          console.log(`✅ Seeded style profile: ${name} (${id})`);
        } catch (error) {
          console.error(`❌ Failed to seed style profile from ${file}:`, error);
        }
      }
    }

    // Create default user for development
    try {
      await prisma.user.upsert({
        where: { email: 'admin@example.com' },
        update: {},
        create: {
          email: 'admin@example.com',
          name: 'Default Admin User',
          bio: 'System administrator account',
          defaultModel: 'gpt-4-turbo',
          defaultContentQuality: 'balanced',
          defaultMaxTokens: 4000,
          defaultTemperature: 0.7,
        },
      });
      console.log("✅ Created default admin user");
    } catch (error) {
      console.log("ℹ️ Default user already exists or creation failed:", error);
    }

    // Create some basic system configuration
    try {
      const configs = [
        {
          key: 'ai_models',
          value: {
            available: ['gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo'],
            default: 'gpt-4-turbo'
          } as Record<string, unknown>,
          description: 'Available AI models for content generation',
          category: 'ai_models',
          isPublic: true,
        },
        {
          key: 'generation_limits',
          value: {
            free_tier: { monthly_tokens: 10000, monthly_content: 50 },
            pro_tier: { monthly_tokens: 100000, monthly_content: 500 },
            enterprise_tier: { monthly_tokens: 1000000, monthly_content: 5000 }
          } as Record<string, unknown>,
          description: 'Usage limits by subscription tier',
          category: 'limits',
          isPublic: false,
        }
      ];

      for (const config of configs) {
        await prisma.systemConfig.upsert({
          where: { key: config.key },
          update: {
            value: JSON.parse(JSON.stringify(config.value)),
            description: config.description,
            category: config.category,
            isPublic: config.isPublic,
          },
          create: {
            key: config.key,
            value: JSON.parse(JSON.stringify(config.value)),
            description: config.description,
            category: config.category,
            isPublic: config.isPublic,
          },
        });
      }
      console.log("✅ Created system configuration");
    } catch (error) {
      console.log("ℹ️ System config creation failed:", error);
    }

    console.log("🎉 Database seeding completed successfully!");

  } catch (error) {
    console.error("💥 Seeding failed:", error);
    throw error;
  }
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });