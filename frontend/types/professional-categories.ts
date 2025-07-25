// File: frontend/types/professional-categories.ts
// Professional category types for frontend integration
import React from 'react';

export interface StyleProfile {
  id: string;
  name: string;
  description: string;
  category: string;
  subcategory: string;
  complexity: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  audience: string;
  tone: string;
  voice: string;
  targetLength: {
    min: number;
    max: number;
    optimal: number;
  };
  useCases: string[];
  professionalGrade: boolean;
}

export interface ContentTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  complexity: string;
  recommendedStyles: string[];
  sections: Array<{
    title: string;
    required: boolean;
  }>;
  targetLength: {
    min_words: number;
    max_words: number;
    optimal_words: number;
  };
}

export interface StyleCategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  profileCount: number;
  complexityDistribution: {
    beginner: number;
    intermediate: number;
    advanced: number;
    expert: number;
  };
  audienceTypes: string[];
  profiles: StyleProfile[];
}

// Professional category definitions
export const PROFESSIONAL_CATEGORIES: StyleCategory[] = [
  {
    id: 'academic_research',
    name: 'Academic & Research',
    description: 'Scholarly writing for academic institutions, research papers, and peer-reviewed publications',
    icon: '🎓',
    profileCount: 10,
    complexityDistribution: { beginner: 0, intermediate: 2, advanced: 4, expert: 4 },
    audienceTypes: ['Academics', 'Researchers', 'Graduate Students', 'Peer Reviewers'],
    profiles: []
  },
  {
    id: 'technical_documentation',
    name: 'Technical Documentation',
    description: 'Precise technical writing for developers, engineers, and technical professionals',
    icon: '⚙️',
    profileCount: 10,
    complexityDistribution: { beginner: 0, intermediate: 3, advanced: 5, expert: 2 },
    audienceTypes: ['Developers', 'Engineers', 'Technical Teams', 'DevOps'],
    profiles: []
  },
  {
    id: 'business_strategy',
    name: 'Business Strategy',
    description: 'Strategic business communication for executives, stakeholders, and decision-makers',
    icon: '📊',
    profileCount: 10,
    complexityDistribution: { beginner: 0, intermediate: 2, advanced: 6, expert: 2 },
    audienceTypes: ['Executives', 'Investors', 'Board Members', 'Stakeholders'],
    profiles: []
  },
  {
    id: 'educational_content',
    name: 'Educational Content',
    description: 'Instructional content for learning, training, and knowledge transfer',
    icon: '📚',
    profileCount: 10,
    complexityDistribution: { beginner: 3, intermediate: 5, advanced: 2, expert: 0 },
    audienceTypes: ['Students', 'Trainees', 'Workshop Participants', 'Learners'],
    profiles: []
  },
  {
    id: 'marketing_communications',
    name: 'Marketing Communications',
    description: 'Persuasive marketing content for brand building and customer engagement',
    icon: '📢',
    profileCount: 10,
    complexityDistribution: { beginner: 2, intermediate: 6, advanced: 2, expert: 0 },
    audienceTypes: ['Customers', 'Prospects', 'Brand Audiences', 'Social Media'],
    profiles: []
  }
];

// Content template categories
export const CONTENT_TEMPLATE_CATEGORIES = [
  {
    id: 'blog_articles',
    name: 'Blog Articles',
    templates: ['blog_article_generator', 'content_marketing_template', 'tutorial_guide_template'],
    recommendedStyleCategories: ['educational_content', 'marketing_communications', 'technical_documentation']
  },
  {
    id: 'business_documents',
    name: 'Business Documents', 
    templates: ['business_proposal_template', 'strategic_plan_template'],
    recommendedStyleCategories: ['business_strategy']
  },
  {
    id: 'technical_docs',
    name: 'Technical Documentation',
    templates: ['api_documentation_template', 'system_architecture_template'],
    recommendedStyleCategories: ['technical_documentation']
  },
  {
    id: 'research_papers',
    name: 'Research Papers',
    templates: ['research_paper_template', 'academic_article_template'],
    recommendedStyleCategories: ['academic_research']
  },
  {
    id: 'marketing_content',
    name: 'Marketing Content',
    templates: ['email_campaign_template', 'content_marketing_template'],
    recommendedStyleCategories: ['marketing_communications']
  },
  {
    id: 'educational_materials',
    name: 'Educational Materials',
    templates: ['training_module_template', 'tutorial_guide_template'],
    recommendedStyleCategories: ['educational_content']
  }
];

// API response types
export interface CategoryAPIResponse {
  categories: StyleCategory[];
  templates: ContentTemplate[];
  mappings: {
    [templateId: string]: string[];
  };
}

export interface StyleSelectionState {
  selectedTemplate: string | null;
  selectedCategory: string | null;
  selectedStyle: string | null;
  availableStyles: StyleProfile[];
  recommendations: StyleProfile[];
}

// Utility functions
export const getStylesForTemplate = (templateId: string, categories: StyleCategory[]): StyleProfile[] => {
  const templateCategory = CONTENT_TEMPLATE_CATEGORIES.find(cat => 
    cat.templates.includes(templateId)
  );
  
  if (!templateCategory) return [];
  
  const relevantCategories = categories.filter(cat => 
    templateCategory.recommendedStyleCategories.includes(cat.id)
  );
  
  return relevantCategories.flatMap(cat => cat.profiles);
};

export const getRecommendedStyles = (
  templateId: string, 
  userLevel: 'beginner' | 'intermediate' | 'advanced' | 'expert',
  categories: StyleCategory[]
): StyleProfile[] => {
  const availableStyles = getStylesForTemplate(templateId, categories);
  
  // Filter by complexity level (user level ± 1)
  const complexityOrder = ['beginner', 'intermediate', 'advanced', 'expert'];
  const userIndex = complexityOrder.indexOf(userLevel);
  const allowedComplexities = complexityOrder.slice(
    Math.max(0, userIndex - 1),
    Math.min(complexityOrder.length, userIndex + 2)
  );
  
  return availableStyles
    .filter(style => allowedComplexities.includes(style.complexity))
    .sort((a, b) => {
      // Prioritize exact match, then closer matches
      const aDistance = Math.abs(complexityOrder.indexOf(a.complexity) - userIndex);
      const bDistance = Math.abs(complexityOrder.indexOf(b.complexity) - userIndex);
      return aDistance - bDistance;
    })
    .slice(0, 5); // Top 5 recommendations
};

export const getCategoryIcon = (categoryId: string): string => {
  const category = PROFESSIONAL_CATEGORIES.find(cat => cat.id === categoryId);
  return category?.icon || '📝';
};

export const getComplexityColor = (complexity: string): string => {
  const colors = {
    beginner: 'bg-green-100 text-green-800',
    intermediate: 'bg-blue-100 text-blue-800',
    advanced: 'bg-purple-100 text-purple-800',
    expert: 'bg-red-100 text-red-800'
  };
  return colors[complexity as keyof typeof colors] || 'bg-gray-100 text-gray-800';
};

export const formatAudience = (audience: string): string => {
  return audience.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

// React hook for style selection
export const useStyleSelection = () => {
  const [state, setState] = React.useState<StyleSelectionState>({
    selectedTemplate: null,
    selectedCategory: null,
    selectedStyle: null,
    availableStyles: [],
    recommendations: []
  });
  
  const selectTemplate = (templateId: string) => {
    setState(prev => ({
      ...prev,
      selectedTemplate: templateId,
      selectedCategory: null,
      selectedStyle: null,
      availableStyles: getStylesForTemplate(templateId, PROFESSIONAL_CATEGORIES),
      recommendations: getRecommendedStyles(templateId, 'intermediate', PROFESSIONAL_CATEGORIES)
    }));
  };
  
  const selectCategory = (categoryId: string) => {
    const category = PROFESSIONAL_CATEGORIES.find(cat => cat.id === categoryId);
    setState(prev => ({
      ...prev,
      selectedCategory: categoryId,
      selectedStyle: null,
      availableStyles: category?.profiles || []
    }));
  };
  
  const selectStyle = (styleId: string) => {
    setState(prev => ({
      ...prev,
      selectedStyle: styleId
    }));
  };
  
  return {
    ...state,
    selectTemplate,
    selectCategory,
    selectStyle
  };
};