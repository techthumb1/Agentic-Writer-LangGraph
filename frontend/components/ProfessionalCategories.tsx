// File: frontend/components/ProfessionalCategorySelector.tsx
// Professional category and style selection component

import React, { useState, useEffect } from 'react';
import { 
  StyleProfile, 
  StyleCategory,
  PROFESSIONAL_CATEGORIES,
  getStylesForTemplate,
  getRecommendedStyles,
  getComplexityColor,
  formatAudience 
} from '../types/professional-categories';

interface ProfessionalCategorySelectorProps {
  selectedTemplate?: string;
  onStyleSelect: (styleId: string, styleName: string) => void;
  userLevel?: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  className?: string;
}

export const ProfessionalCategorySelector: React.FC<ProfessionalCategorySelectorProps> = ({
  selectedTemplate,
  onStyleSelect,
  userLevel = 'intermediate',
  className = ''
}) => {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedStyle, setSelectedStyle] = useState<string | null>(null);
  const [availableStyles, setAvailableStyles] = useState<StyleProfile[]>([]);
  const [recommendations, setRecommendations] = useState<StyleProfile[]>([]);
  const [viewMode, setViewMode] = useState<'categories' | 'recommendations'>('recommendations');

  // Load styles when template changes
  useEffect(() => {
    if (selectedTemplate) {
      const styles = getStylesForTemplate(selectedTemplate, PROFESSIONAL_CATEGORIES);
      const recs = getRecommendedStyles(selectedTemplate, userLevel, PROFESSIONAL_CATEGORIES);
      setAvailableStyles(styles);
      setRecommendations(recs);
      setSelectedCategory(null);
      setSelectedStyle(null);
    }
  }, [selectedTemplate, userLevel]);

  const handleCategorySelect = (categoryId: string) => {
    setSelectedCategory(categoryId);
    const category = PROFESSIONAL_CATEGORIES.find(cat => cat.id === categoryId);
    if (category) {
      setAvailableStyles(category.profiles);
    }
  };

  const handleStyleSelect = (style: StyleProfile) => {
    setSelectedStyle(style.id);
    onStyleSelect(style.id, style.name);
  };

  if (!selectedTemplate) {
    return (
      <div className={`p-6 bg-gray-50 rounded-lg ${className}`}>
        <div className="text-center text-gray-500">
          <div className="text-2xl mb-2">📝</div>
          <p>Select a content template to see available style profiles</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header with View Toggle */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Professional Style Profiles</h3>
          <p className="text-sm text-gray-600">
            Choose from {availableStyles.length} professional styles for your content
          </p>
        </div>
        
        <div className="flex bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setViewMode('recommendations')}
            className={`px-3 py-1 text-sm rounded-md transition-colors ${
              viewMode === 'recommendations'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Recommended
          </button>
          <button
            onClick={() => setViewMode('categories')}
            className={`px-3 py-1 text-sm rounded-md transition-colors ${
              viewMode === 'categories'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            All Categories
          </button>
        </div>
      </div>

      {/* Recommendations View */}
      {viewMode === 'recommendations' && (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-700">Recommended for you:</span>
            <span className={`px-2 py-1 text-xs rounded-full ${getComplexityColor(userLevel)}`}>
              {userLevel} level
            </span>
          </div>
          
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {recommendations.map((style) => (
              <StyleCard
                key={style.id}
                style={style}
                isSelected={selectedStyle === style.id}
                onSelect={() => handleStyleSelect(style)}
                isRecommended={true}
              />
            ))}
          </div>

          {recommendations.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <p>No recommendations available for this template</p>
            </div>
          )}
        </div>
      )}

      {/* Categories View */}
      {viewMode === 'categories' && (
        <div className="space-y-6">
          {/* Category Selection */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {PROFESSIONAL_CATEGORIES.map((category) => (
              <CategoryCard
                key={category.id}
                category={category}
                isSelected={selectedCategory === category.id}
                onSelect={() => handleCategorySelect(category.id)}
                hasRelevantStyles={availableStyles.some(style => style.category === category.id)}
              />
            ))}
          </div>

          {/* Style Selection for Selected Category */}
          {selectedCategory && (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700">
                  {PROFESSIONAL_CATEGORIES.find(cat => cat.id === selectedCategory)?.name} Styles:
                </span>
              </div>
              
              <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                {availableStyles
                  .filter(style => style.category === selectedCategory)
                  .map((style) => (
                    <StyleCard
                      key={style.id}
                      style={style}
                      isSelected={selectedStyle === style.id}
                      onSelect={() => handleStyleSelect(style)}
                    />
                  ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Category Card Component
interface CategoryCardProps {
  category: StyleCategory;
  isSelected: boolean;
  onSelect: () => void;
  hasRelevantStyles: boolean;
}

const CategoryCard: React.FC<CategoryCardProps> = ({
  category,
  isSelected,
  onSelect,
  hasRelevantStyles
}) => {
  return (
    <button
      onClick={onSelect}
      disabled={!hasRelevantStyles}
      className={`p-4 rounded-lg border-2 text-left transition-all ${
        isSelected
          ? 'border-blue-500 bg-blue-50'
          : hasRelevantStyles
          ? 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
          : 'border-gray-100 bg-gray-50 opacity-50 cursor-not-allowed'
      }`}
    >
      <div className="flex items-start gap-3">
        <span className="text-2xl">{category.icon}</span>
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-gray-900 truncate">{category.name}</h4>
          <p className="text-sm text-gray-600 mt-1 line-clamp-2">{category.description}</p>
          
          <div className="flex items-center gap-2 mt-2">
            <span className="text-xs text-gray-500">{category.profileCount} profiles</span>
            {!hasRelevantStyles && (
              <span className="text-xs text-orange-600">Not available for this template</span>
            )}
          </div>
        </div>
      </div>
    </button>
  );
};

// Style Card Component
interface StyleCardProps {
  style: StyleProfile;
  isSelected: boolean;
  onSelect: () => void;
  isRecommended?: boolean;
}

const StyleCard: React.FC<StyleCardProps> = ({
  style,
  isSelected,
  onSelect,
  isRecommended = false
}) => {
  return (
    <button
      onClick={onSelect}
      className={`p-4 rounded-lg border-2 text-left transition-all ${
        isSelected
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
      }`}
    >
      <div className="space-y-3">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <h4 className="font-medium text-gray-900 truncate">{style.name}</h4>
            <p className="text-sm text-gray-600 mt-1">{formatAudience(style.audience)}</p>
          </div>
          
          {isRecommended && (
            <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
              Recommended
            </span>
          )}
        </div>

        {/* Description */}
        <p className="text-sm text-gray-600 line-clamp-2">{style.description}</p>

        {/* Metadata */}
        <div className="flex items-center gap-2 text-xs">
          <span className={`px-2 py-1 rounded-full ${getComplexityColor(style.complexity)}`}>
            {style.complexity}
          </span>
          <span className="text-gray-500">•</span>
          <span className="text-gray-500">{style.voice} voice</span>
        </div>

        {/* Length indicator */}
        <div className="text-xs text-gray-500">
          Target: {style.targetLength.min.toLocaleString()}-{style.targetLength.max.toLocaleString()} words
        </div>
      </div>
    </button>
  );
};

// Quick Style Recommendations Component
export const QuickStyleRecommendations: React.FC<{
  templateId: string;
  userLevel?: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  onStyleSelect: (styleId: string, styleName: string) => void;
  maxRecommendations?: number;
}> = ({ 
  templateId, 
  userLevel = 'intermediate', 
  onStyleSelect,
  maxRecommendations = 3 
}) => {
  const recommendations = getRecommendedStyles(templateId, userLevel, PROFESSIONAL_CATEGORIES)
    .slice(0, maxRecommendations);

  if (recommendations.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      <h4 className="text-sm font-medium text-gray-700">Quick Style Picks</h4>
      <div className="space-y-2">
        {recommendations.map((style) => (
          <button
            key={style.id}
            onClick={() => onStyleSelect(style.id, style.name)}
            className="w-full p-3 text-left border border-gray-200 rounded-lg hover:border-gray-300 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-gray-900">{style.name}</span>
                  <span className={`px-2 py-1 text-xs rounded-full ${getComplexityColor(style.complexity)}`}>
                    {style.complexity}
                  </span>
                </div>
                <p className="text-sm text-gray-600 truncate">{style.description}</p>
              </div>
              <span className="ml-2 text-gray-400">→</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

// Style Profile Preview Component
export const StyleProfilePreview: React.FC<{
  styleId: string;
  onClose: () => void;
}> = ({ styleId, onClose }) => {
  const [style, setStyle] = useState<StyleProfile | null>(null);

  useEffect(() => {
    // Find style across all categories
    const foundStyle = PROFESSIONAL_CATEGORIES
      .flatMap(cat => cat.profiles)
      .find(profile => profile.id === styleId);
    
    setStyle(foundStyle || null);
  }, [styleId]);

  if (!style) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{style.name}</h3>
              <div className="flex items-center gap-2 mt-1">
                <span className={`px-2 py-1 text-xs rounded-full ${getComplexityColor(style.complexity)}`}>
                  {style.complexity}
                </span>
                <span className="text-sm text-gray-600">for {formatAudience(style.audience)}</span>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>

          {/* Description */}
          <div className="mb-6">
            <h4 className="font-medium text-gray-900 mb-2">Description</h4>
            <p className="text-gray-600">{style.description}</p>
          </div>

          {/* Style Characteristics */}
          <div className="grid md:grid-cols-2 gap-6 mb-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Style Characteristics</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Tone:</span>
                  <span className="font-medium capitalize">{style.tone}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Voice:</span>
                  <span className="font-medium capitalize">{style.voice}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Complexity:</span>
                  <span className="font-medium capitalize">{style.complexity}</span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 mb-2">Content Specifications</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Target Length:</span>
                  <span className="font-medium">
                    {style.targetLength.min.toLocaleString()}-{style.targetLength.max.toLocaleString()} words
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Professional Grade:</span>
                  <span className={`font-medium ${style.professionalGrade ? 'text-green-600' : 'text-gray-600'}`}>
                    {style.professionalGrade ? 'Yes' : 'No'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Use Cases */}
          <div className="mb-6">
            <h4 className="font-medium text-gray-900 mb-2">Use Cases</h4>
            <div className="flex flex-wrap gap-2">
              {style.useCases.map((useCase, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full"
                >
                  {useCase}
                </span>
              ))}
            </div>
          </div>

          {/* Example Output Preview */}
          <div className="mb-6">
            <h4 className="font-medium text-gray-900 mb-2">Expected Output Style</h4>
            <div className="p-4 bg-gray-50 rounded-lg border">
              <div className="text-sm text-gray-600 mb-2">Example opening for &quot;{style.name}&quot; style:</div>
              <div className="text-gray-900 italic">
                {getExampleOpening(style)}
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={() => {
                onClose();
                // You can add onSelect callback here if needed
              }}
              className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Select This Style
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper function to generate example openings
const getExampleOpening = (style: StyleProfile): string => {
  const examples = {
    'phd_dissertation': 'This dissertation examines the theoretical frameworks underlying contemporary approaches to...',
    'api_documentation': 'The following API documentation provides comprehensive technical specifications for...',
    'executive_summary': 'This strategic analysis presents key findings and recommendations for executive leadership regarding...',
    'beginner_tutorial': 'This tutorial introduces the fundamental concepts of... in an accessible, step-by-step format...',
    'content_marketing': 'Discover how innovative approaches to... can transform your understanding and drive measurable results...',
    'business_case_analysis': 'The business case for this initiative demonstrates significant strategic value through...',
    'technical_specification': 'Technical specifications outlined in this document define the architectural requirements for...',
    'peer_review_article': 'This study investigates the relationship between... using a rigorous methodological approach...',
    'email_campaign': 'Transform your approach to... with these proven strategies that deliver immediate impact...',
    'workshop_facilitator': 'Welcome to this comprehensive workshop where participants will develop practical skills in...'
  };

  return examples[style.id as keyof typeof examples] || 
    `This ${style.complexity}-level content examines... using a ${style.tone} approach suitable for ${formatAudience(style.audience).toLowerCase()}...`;
};

export default ProfessionalCategorySelector;