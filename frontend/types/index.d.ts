// frontend/types/index.d.ts

export type ContentTemplate = {
  id: string; // e.g., 'federated_learning_101'
  name: string; // e.g., 'Federated Learning 101 Guide'
  description: string;
  parameters: Array<{
    name: string; // internal key, e.g., 'topic'
    label: string; // UI label, e.g., 'Main Topic'
    type: 'text' | 'textarea' | 'select' | 'number' | 'checkbox';
    default?: string | number | boolean;
    options?: string[]; // For 'select' type
    placeholder?: string;
  }>;
};

export type StyleProfile = {
  id: string; // e.g., 'beginner_friendly'
  name: string; // e.g., 'Beginner Friendly'
  description: string;
};

export type GenerateContentPayload = {
  templateId: string;
  styleProfileId: string;
  parameters: Record<string, string | number | boolean>; // Dynamic parameters from template
};

export type GeneratedContent = {
  id: string;
  title: string;
  contentHtml: string; // HTML string from Tiptap, or markdown converted to HTML
  status: 'pending' | 'generating' | 'completed' | 'failed';
  createdAt: string;
  updatedAt: string;
};
