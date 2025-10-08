// File: frontend/hooks/useTemplateStyleDrillDown.ts
// Integration hook for drill-down template-style selection
// Handles state management and navigation for the unified selection flow
// RELEVANT FILES: components/TemplateStyleDrillDown.tsx, app/generate/page.tsx, lib/template-style-mapping.ts

import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface Template {
  id: string;
  title: string;
  description: string;
  category: string;
  difficulty?: string;
  estimatedLength?: string;
  icon?: string;
  templateData?: {
    template_type?: string;
    parameters?: Record<string, unknown>;
    sections?: unknown[];
    instructions?: string;
    content_format?: string;
    output_structure?: string;
    section_order?: string[];
    validation_rules?: string[];
    tone?: Record<string, unknown>;
    generation_mode?: string;
  };
}

interface StyleProfile {
  id: string;
  name: string;
  description: string;
  category: string;
  tone?: string;
  complexity?: string;
}

interface UseTemplateStyleDrillDownProps {
  templates: Template[];
  styleProfiles: StyleProfile[];
  onComplete?: (template: Template, style: StyleProfile) => void;
}

export function useTemplateStyleDrillDown({
    onComplete
}: UseTemplateStyleDrillDownProps) {
    const router = useRouter();
    const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
    const [selectedStyle, setSelectedStyle] = useState<StyleProfile | null>(null);
    const [isLoading, setIsLoading] = useState(false);

  const handleTemplateSelect = (template: Template) => {
    setSelectedTemplate(template);
    setSelectedStyle(null);
  };

  const handleStyleSelect = (style: StyleProfile) => {
    setSelectedStyle(style);
  };

  const handleProceed = async () => {
    if (!selectedTemplate || !selectedStyle) {
      return;
    }

    setIsLoading(true);

    try {
      if (onComplete) {
        await onComplete(selectedTemplate, selectedStyle);
      } else {
        const params = new URLSearchParams({
          template: selectedTemplate.id,
          style: selectedStyle.id
        });
        router.push(`/generate/${selectedTemplate.id}?${params.toString()}`);
      }
    } catch (error) {
      console.error('Error proceeding with selections:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const reset = () => {
    setSelectedTemplate(null);
    setSelectedStyle(null);
  };

  const canProceed = Boolean(selectedTemplate && selectedStyle);

  return {
    selectedTemplate,
    selectedStyle,
    isLoading,
    canProceed,
    handleTemplateSelect,
    handleStyleSelect,
    handleProceed,
    reset
  };
}