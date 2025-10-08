// File: frontend/lib/template-style-mapping.ts
// Template-style compatibility mapping and quality scoring system
// RELEVANT FILES: components/TemplateStyleDrillDown.tsx, hooks/useTemplateStyleDrillDown.ts

interface StyleRecommendations {
  recommended: string[];
  compatible: string[];
  incompatible: string[];
}

interface QualityIndicator {
  color: 'green' | 'yellow' | 'red';
  label: string;
  emoji: string;
}

// Template-style compatibility matrix
const TEMPLATE_STYLE_MATRIX: Record<string, StyleRecommendations> = {
  // Research & Academic Templates
  'research_paper_template': {
    recommended: ['phd_academic', 'methodology_paper', 'literature_review', 'scholarly_commentary'],
    compatible: ['academic_textbook', 'peer_review_article', 'conference_abstract'],
    incompatible: ['social_media_voice', 'brand_storytelling', 'influencer_collaboration']
  },
  'technical_documentation': {
    recommended: ['api_documentation', 'technical_specification', 'deployment_guide', 'system_architecture'],
    compatible: ['implementation_guide', 'troubleshooting_manual', 'integration_manual'],
    incompatible: ['social_media_voice', 'founder_storytelling', 'content_marketing']
  },
  'api_documentation_template': {
    recommended: ['api_documentation', 'technical_specification', 'code_review_standards'],
    compatible: ['deployment_guide', 'implementation_guide', 'system_architecture'],
    incompatible: ['social_media_voice', 'brand_storytelling', 'email_campaign']
  },

  // Business Templates
  'business_proposal': {
    recommended: ['executive_summary', 'strategic_planning', 'business_case_analysis'],
    compatible: ['investor_presentation', 'venture_capital_pitch', 'board_presentation'],
    incompatible: ['social_media_voice', 'influencer_collaboration', 'beginner_tutorial']
  },
  'email_newsletter': {
    recommended: ['email_campaign', 'content_marketing', 'customer_success'],
    compatible: ['brand_storytelling', 'thought_leadership', 'social_media_voice'],
    incompatible: ['phd_academic', 'technical_specification', 'methodology_paper']
  },
  'press_release': {
    recommended: ['thought_leadership', 'brand_storytelling', 'content_marketing'],
    compatible: ['email_campaign', 'social_media_voice', 'founder_storytelling'],
    incompatible: ['phd_academic', 'technical_specification', 'code_review_standards']
  },
  'social_media_campaign': {
    recommended: ['social_media_voice', 'influencer_collaboration', 'content_marketing'],
    compatible: ['brand_storytelling', 'email_campaign', 'customer_success'],
    incompatible: ['phd_academic', 'methodology_paper', 'technical_specification']
  },

  // Educational Templates
  'blog_article_generator': {
    recommended: ['content_marketing', 'thought_leadership', 'popular_sci'],
    compatible: ['beginner_tutorial', 'online_course', 'brand_storytelling'],
    incompatible: ['phd_academic', 'technical_specification', 'methodology_paper']
  }
};

// Quality scoring based on template-style compatibility
const QUALITY_SCORES: Record<string, Record<string, number>> = {
  // Research templates with academic styles = highest quality
  'research_paper_template': {
    'phd_academic': 95,
    'methodology_paper': 92,
    'literature_review': 90,
    'scholarly_commentary': 88,
    'academic_textbook': 85,
    'peer_review_article': 83,
    'conference_abstract': 80,
    'technical_specification': 70,
    'content_marketing': 40,
    'social_media_voice': 25
  },
  'technical_documentation': {
    'api_documentation': 95,
    'technical_specification': 93,
    'deployment_guide': 90,
    'system_architecture': 88,
    'implementation_guide': 85,
    'troubleshooting_manual': 83,
    'integration_manual': 80,
    'business_case_analysis': 60,
    'content_marketing': 45,
    'social_media_voice': 30
  },
  'business_proposal': {
    'executive_summary': 95,
    'strategic_planning': 92,
    'business_case_analysis': 90,
    'investor_presentation': 88,
    'venture_capital_pitch': 85,
    'board_presentation': 83,
    'thought_leadership': 75,
    'content_marketing': 65,
    'social_media_voice': 40
  },
  'social_media_campaign': {
    'social_media_voice': 95,
    'influencer_collaboration': 92,
    'content_marketing': 88,
    'brand_storytelling': 85,
    'email_campaign': 80,
    'customer_success': 75,
    'thought_leadership': 70,
    'technical_specification': 35,
    'phd_academic': 25
  }
};

export function getStyleRecommendations(templateId: string): StyleRecommendations {
  return TEMPLATE_STYLE_MATRIX[templateId] || {
    recommended: [],
    compatible: [],
    incompatible: []
  };
}

export function getQualityScore(templateId: string, styleId: string): number {
  const templateScores = QUALITY_SCORES[templateId];
  if (!templateScores) return 75; // Default score
  
  return templateScores[styleId] || 75;
}

export function getQualityIndicator(score: number): QualityIndicator {
  if (score >= 85) {
    return {
      color: 'green',
      label: 'Excellent Match',
      emoji: '🎯'
    };
  } else if (score >= 70) {
    return {
      color: 'yellow',
      label: 'Good Match',
      emoji: '✅'
    };
  } else {
    return {
      color: 'red',
      label: 'Poor Match',
      emoji: '⚠️'
    };
  }
}