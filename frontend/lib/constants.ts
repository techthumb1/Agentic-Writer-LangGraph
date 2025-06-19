export const PAGINATION = {
  DEFAULT_LIMIT: parseInt(process.env.NEXT_PUBLIC_DEFAULT_LIMIT || '10'),
  MAX_LIMIT: parseInt(process.env.NEXT_PUBLIC_MAX_LIMIT || '100')
};

export const API_ENDPOINTS = {
  STYLE_PROFILES: '/api/style-profiles',
  GENERATE_CONTENT: '/api/generate-content',
  GET_TEMPLATES: '/api/get-templates'
};