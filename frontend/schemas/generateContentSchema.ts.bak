// schemas/generateContentSchema.ts
import * as z from "zod";

export const generateContentFormSchema = z.object({
  templateId: z.string().min(1, "Please select a content template."),
  styleProfileId: z.string().min(1, "Please select a style profile."),
  dynamic_parameters: z.record(z.string(), z.union([z.string(), z.number(), z.boolean()])),
});

export type GenerateContentFormValues = z.infer<typeof generateContentFormSchema>; 