// schemas/generateContentSchema.ts

import { z } from "zod";

export const generateContentSchema = z.object({
  templateId: z.string().min(1, "Template is required"),
  styleProfileId: z.string().min(1, "Style profile is required"),
  dynamic_parameters: z.record(z.union([z.string(), z.number(), z.boolean()])),
  platform: z.string().default("web"),
  use_mock: z.boolean().optional(),
});


export type GenerateContentFormValues = z.infer<typeof generateContentSchema>;