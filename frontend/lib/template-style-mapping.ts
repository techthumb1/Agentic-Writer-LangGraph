/* ============================================================
   FRONTEND: template-style-mapping.ts
   COMPLETE ENTERPRISE-GRADE TEMPLATE → STYLE MATCH MATRIX
   Ensures:
   - 2–3 Excellent Matches per template
   - Robust Compatible matches
   - No template with empty result sets
============================================================ */

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

/* ============================================================
   TEMPLATE → STYLE MATCH MATRIX
============================================================ */

const TEMPLATE_STYLE_MATRIX: Record<string, StyleRecommendations> = {

  /* ------------------------------
     RESEARCH & ACADEMIC
  ------------------------------ */
  'research_paper_template': {
    recommended: ['phd_academic', 'methodology_paper', 'literature_review'],
    compatible: [
      'scholarly_commentary',
      'academic_textbook',
      'peer_review_article',
      'conference_abstract',
      'phd_lit_review',
      'academic_book_chapter',
      'phd_dissertation',
      'research_proposal'
    ],
    incompatible: [
      'social_media_voice',
      'brand_storytelling',
      'influencer_collaboration'
    ]
  },

  'technical_documentation': {
    recommended: ['api_documentation', 'technical_specification', 'system_architecture'],
    compatible: [
      'deployment_guide',
      'integration_manual',
      'troubleshooting_manual',
      'implementation_guide',
      'technical_dive'
    ],
    incompatible: ['social_media_voice', 'brand_storytelling']
  },

  'api_documentation_template': {
    recommended: ['api_documentation', 'technical_specification', 'code_review_standards'],
    compatible: [
      'deployment_guide',
      'integration_manual',
      'system_architecture'
    ],
    incompatible: ['social_media_voice', 'email_campaign']
  },

  /* ------------------------------
     BUSINESS & ENTERPRISE
  ------------------------------ */
  'business_proposal': {
    recommended: ['executive_summary', 'strategic_planning', 'business_case_analysis'],
    compatible: [
      'investor_presentation',
      'venture_capital_pitch',
      'board_presentation',
      'market_flash',
      'roi_analysis'
    ],
    incompatible: ['social_media_voice']
  },

  'email_newsletter': {
    recommended: ['email_campaign', 'content_marketing', 'customer_success'],
    compatible: [
      'brand_storytelling',
      'thought_leadership',
      'social_media_voice'
    ],
    incompatible: ['phd_academic', 'technical_specification']
  },

  'press_release': {
    recommended: ['thought_leadership', 'brand_storytelling', 'product_launch'],
    compatible: [
      'email_campaign',
      'content_marketing',
      'social_media_voice'
    ],
    incompatible: ['phd_academic', 'technical_specification']
  },

  'social_media_campaign': {
    recommended: ['social_media_voice', 'influencer_collaboration', 'content_marketing'],
    compatible: [
      'brand_storytelling',
      'email_campaign',
      'customer_success'
    ],
    incompatible: ['phd_academic', 'methodology_paper']
  },

  'market_analysis_template': {
    recommended: ['market_research_report', 'competitive_analysis', 'roi_analysis'],
    compatible: [
      'business_case_analysis',
      'strategic_planning',
      'venture_capital_pitch',
      'performance_analysis',
      'content_marketing'
    ],
    incompatible: ['social_media_voice']
  },

  'strategic_brief_template': {
    recommended: ['strategic_planning', 'business_case_analysis', 'executive_summary'],
    compatible: [
      'brand_storytelling',
      'market_flash',
      'roi_analysis',
      'performance_analysis',
      'venture_capital_pitch'
    ],
    incompatible: ['social_media_voice']
  },

  /* ------------------------------
     EDUCATIONAL / CONTENT
  ------------------------------ */
  'blog_article_generator': {
    recommended: ['content_marketing', 'thought_leadership', 'popular_sci'],
    compatible: [
      'beginner_tutorial',
      'brand_storytelling',
      'online_course',
      'general_blog'
    ],
    incompatible: ['phd_academic']
  },

  'data_driven_template': {
    recommended: [
      'market_research_report',
      'performance_analysis',
      'experimental_lab_log'
    ],
    compatible: [
      'competitive_analysis',
      'business_case_analysis',
      'strategic_planning',
      'roi_analysis',
      'market_flash'
    ],
    incompatible: [
      'social_media_voice',
      'influencer_collaboration'
    ]
  },


  
  /* ------------------------------
     FILM / TV / CREATIVE WRITING
  ------------------------------ */
  'feature_screenplay': {
    recommended: ['cinematic_dialogue', 'action_visual_writing', 'tv_premium_drama'],
    compatible: [
      'tv_premium_sci_fi',
      'tv_premium_horror',
      'tv_comedy_writing',
      'brand_storytelling'
    ],
    incompatible: ['api_documentation']
  },

  'tv_pilot_script': {
    recommended: ['tv_premium_drama', 'cinematic_dialogue', 'action_visual_writing'],
    compatible: [
      'tv_premium_sci_fi',
      'tv_premium_horror',
      'tv_comedy_writing',
      'brand_storytelling'
    ],
    incompatible: ['api_documentation']
  }
};

/* ============================================================
   QUALITY SCORING SYSTEM
============================================================ */

const QUALITY_SCORES: Record<string, Record<string, number>> = {

  /* ============================
     RESEARCH & ACADEMIC
  ============================ */
  'research_paper_template': {
    'phd_academic': 95,
    'methodology_paper': 92,
    'literature_review': 90,
    'scholarly_commentary': 88,
    'academic_textbook': 85,
    'peer_review_article': 83,
    'conference_abstract': 80,
    'phd_lit_review': 82,
    'academic_book_chapter': 84,
    'phd_dissertation': 92,
    'research_proposal': 90,
    'technical_specification': 70,
    'content_marketing': 40,
    'social_media_voice': 25
  },

  'technical_documentation': {
    'api_documentation': 95,
    'technical_specification': 93,
    'system_architecture': 90,
    'deployment_guide': 88,
    'integration_manual': 85,
    'troubleshooting_manual': 83,
    'technical_dive': 82,
    'security_protocol': 88,
    'implementation_guide': 84,
    'business_case_analysis': 60,
    'content_marketing': 40,
    'social_media_voice': 30
  },

  'api_documentation_template': {
    'api_documentation': 95,
    'technical_specification': 92,
    'code_review_standards': 90,
    'system_architecture': 88,
    'integration_manual': 85,
    'deployment_guide': 83,
    'technical_dive': 82,
    'content_marketing': 45,
    'social_media_voice': 25
  },

  /* ============================
     BUSINESS & ENTERPRISE
  ============================ */
  'business_proposal': {
    'executive_summary': 95,
    'strategic_planning': 92,
    'business_case_analysis': 90,
    'investor_presentation': 88,
    'venture_capital_pitch': 85,
    'board_presentation': 83,
    'market_flash': 78,
    'roi_analysis': 86,
    'grant_application': 82,
    'content_marketing': 60,
    'social_media_voice': 35
  },

  'strategic_brief_template': {
    'strategic_planning': 95,
    'business_case_analysis': 92,
    'executive_summary': 90,
    'market_flash': 85,
    'roi_analysis': 84,
    'performance_analysis': 82,
    'venture_capital_pitch': 80,
    'brand_storytelling': 75,
    'content_marketing': 60,
    'social_media_voice': 30
  },

  'market_analysis_template': {
    'market_research_report': 95,
    'competitive_analysis': 92,
    'roi_analysis': 90,
    'business_case_analysis': 88,
    'strategic_planning': 85,
    'performance_analysis': 84,
    'venture_capital_pitch': 82,
    'content_marketing': 65,
    'brand_storytelling': 60,
    'social_media_voice': 30
  },

  'press_release': {
    'thought_leadership': 92,
    'brand_storytelling': 90,
    'product_launch': 88,
    'email_campaign': 85,
    'content_marketing': 82,
    'social_media_voice': 80,
    'founder_storytelling': 78,
    'general_blog': 75,
    'phd_academic': 25,
    'technical_specification': 40
  },

  'email_newsletter': {
    'email_campaign': 95,
    'content_marketing': 92,
    'customer_success': 88,
    'brand_storytelling': 85,
    'thought_leadership': 83,
    'social_media_voice': 78,
    'general_blog': 75,
    'phd_academic': 25,
    'technical_specification': 40
  },

  /* ============================
     EDUCATIONAL / CONTENT
  ============================ */
  'blog_article_generator': {
    'content_marketing': 93,
    'thought_leadership': 90,
    'popular_sci': 88,
    'brand_storytelling': 85,
    'beginner_tutorial': 83,
    'online_course': 80,
    'general_blog': 78,
    'research_proposal': 70,
    'phd_academic': 25
  },

  'data_driven_template': {
    'market_research_report': 95,
    'performance_analysis': 92,
    'experimental_lab_log': 90,
    'competitive_analysis': 88,
    'business_case_analysis': 85,
    'strategic_planning': 82,
    'roi_analysis': 82,
    'market_flash': 80,
    'content_marketing': 60,
    'social_media_voice': 30
  },

  /* ============================
     CREATIVE WRITING
  ============================ */
  'tv_pilot_script': {
    'tv_premium_drama': 95,
    'cinematic_dialogue': 93,
    'action_visual_writing': 92,
    'tv_premium_sci_fi': 85,
    'tv_premium_horror': 82,
    'tv_comedy_writing': 78,
    'brand_storytelling': 70
  },

  'feature_screenplay': {
    'cinematic_dialogue': 95,
    'action_visual_writing': 93,
    'tv_premium_drama': 90,
    'tv_premium_horror': 85,
    'tv_premium_sci_fi': 83,
    'tv_comedy_writing': 78
  }
};


/* ============================================================
   HELPERS
============================================================ */

export function getStyleRecommendations(templateId: string): StyleRecommendations {
  return TEMPLATE_STYLE_MATRIX[templateId] || {
    recommended: [],
    compatible: [],
    incompatible: []
  };
}

export function getQualityScore(templateId: string, styleId: string): number {
  const templateScores = QUALITY_SCORES[templateId];
  if (!templateScores) return 75;
  return templateScores[styleId] ?? null;
}

export function getQualityIndicator(score: number): QualityIndicator {
  if (score >= 85) {
    return { color: 'green', label: 'Excellent Match', emoji: '🎯' };
  } else if (score >= 70) {
    return { color: 'yellow', label: 'Good Match', emoji: '✅' };
  } else {
    return { color: 'red', label: 'Poor Match', emoji: '⚠️' };
  }
}
