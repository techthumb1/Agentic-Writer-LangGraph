// File: frontend/components/TemplateStyleDrillDown.tsx
// Drill-down filtering system that shows optimal style profiles for selected template
// RELEVANT FILES: components/TemplateSelector.tsx, components/StyleProfilesSelector.tsx, lib/template-style-mapping.ts

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ChevronRight, Filter, RotateCcw } from 'lucide-react';
import { getStyleRecommendations, getQualityScore, getQualityIndicator } from '@/lib/template-style-mapping';

interface Template {
  id: string;
  title: string;
  description: string;
  category: string;
  difficulty?: string;
  estimatedLength?: string;
  icon?: string;
}

interface StyleProfile {
  id: string;
  name: string;
  description: string;
  category: string;
  tone?: string;
  complexity?: string;
  qualityScore?: number;
  qualityIndicator?: {
    color: 'green' | 'yellow' | 'red';
    label: string;
    emoji: string;
  };
}

interface TemplateStyleDrillDownProps {
  templates: Template[];
  styleProfiles: StyleProfile[];
  selectedTemplate?: Template | null;
  selectedStyle?: StyleProfile | null;
  styleProfileSectionId?: string;
  onTemplateSelect: (template: Template) => void;
  onStyleSelect: (style: StyleProfile | null) => void;
  onProceed: () => void;
}

export default function TemplateStyleDrillDown({
  templates,
  styleProfiles,
  selectedTemplate,
  selectedStyle,
  onTemplateSelect,
  onStyleSelect,
  onProceed
}: TemplateStyleDrillDownProps) {
  const [filteredStyles, setFilteredStyles] = useState<StyleProfile[]>([]);
  const [filterLevel, setFilterLevel] = useState<'recommended' | 'compatible' | 'all'>('recommended');
  const [showFilters, setShowFilters] = useState(false);

  // Filter styles when template changes
  useEffect(() => {
    if (selectedTemplate) {
      const recommendations = getStyleRecommendations(selectedTemplate.id);
      
      let filtered: StyleProfile[] = [];
      
      switch (filterLevel) {
        case 'recommended':
          filtered = styleProfiles.filter(style => 
            recommendations.recommended.includes(style.id)
          );
          break;
        case 'compatible':
          filtered = styleProfiles.filter(style => 
            recommendations.recommended.includes(style.id) || 
            recommendations.compatible.includes(style.id)
          );
          break;
        case 'all':
          filtered = styleProfiles;
          break;
      }

      // Add quality scores and indicators
      const enrichedStyles = filtered.map(style => ({
        ...style,
        qualityScore: getQualityScore(selectedTemplate.id, style.id),
        qualityIndicator: getQualityIndicator(getQualityScore(selectedTemplate.id, style.id))
      })).sort((a, b) => (b.qualityScore || 0) - (a.qualityScore || 0));

      setFilteredStyles(enrichedStyles);
    } else {
      setFilteredStyles([]);
    }
  }, [selectedTemplate, styleProfiles, filterLevel]);

  const handleTemplateSelect = (template: Template) => {
    onTemplateSelect(template);
    // Reset style selection when template changes
    if (selectedStyle) {
      onStyleSelect(null);
    }
  };

  const getFilterBadgeCount = () => {
    if (!selectedTemplate) return 0;
    const recommendations = getStyleRecommendations(selectedTemplate.id);
    
    switch (filterLevel) {
      case 'recommended':
        return recommendations.recommended.length;
      case 'compatible':
        return recommendations.recommended.length + recommendations.compatible.length;
      case 'all':
        return styleProfiles.length;
      default:
        return 0;
    }
  };

  return (
    <div className="space-y-6">
      {/* Step 1: Template Selection */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2 bg-gradient-to-r from-purple-500/20 to-pink-500/20 px-4 py-2 rounded-lg border border-purple-500/30">
                <span className="bg-blue-100 text-blue-800 text-sm font-medium px-2.5 py-0.5 rounded-full">
                  1
                </span>
                Select Content Template
              </CardTitle>
              <CardDescription>
                Choose the type of content you want to generate
              </CardDescription>
            </div>
            {selectedTemplate && (
              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                Selected: {selectedTemplate.title}
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {templates.map((template) => (
              <Card
                key={template.id}
                className={`cursor-pointer transition-all duration-200 hover:shadow-md h-40 ${
                  selectedTemplate?.id === template.id
                    ? 'ring-2 ring-purple-500 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                }`}
                onClick={() => handleTemplateSelect(template)}
              >
                <CardContent className="p-3">
                  <div className="flex items-start gap-2">
                    {template.icon && (
                      <span className="text-2xl">{template.icon}</span>
                    )}
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-sm truncate">
                        {template.title}
                      </h3>
                      <p className="text-xs text-gray-800 dark:text-gray-200 mt-1 line-clamp-2 text-ellipsis overflow-hidden">
                        {template.description}
                      </p>
                      <div className="flex gap-2 mt-2">
                        <Badge variant="secondary" className="text-xs bg-gradient-to-r from-purple-100 to-pink-100 text-purple-800 dark:from-purple-900 dark:to-pink-900 dark:text-purple-200 border-purple-200 dark:border-purple-700">
                          {template.category}
                        </Badge>
                        {template.difficulty && (
                          <Badge variant="outline" className="text-xs border-gray-400 bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200 dark:border-gray-600">
                            {template.difficulty}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Step 2: Style Profile Selection (only show when template selected) */}
      {selectedTemplate && (
        <div id="style-profile-section">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2 bg-gradient-to-r from-purple-500/20 to-pink-500/20 px-4 py-2 rounded-lg border border-purple-500/30">
                  <span className="bg-blue-100 text-blue-800 text-sm font-medium px-2.5 py-0.5 rounded-full">
                    2
                  </span>
                  Select Style Profile
                  <ChevronRight className="h-4 w-4 text-gray-400" />
                  <span className="text-blue-600 text-sm font-normal">
                    Optimized for {selectedTemplate.title}
                  </span>
                </CardTitle>
                <CardDescription>
                  Choose from {getFilterBadgeCount()} recommended style profiles for optimal output quality
                </CardDescription>
              </div>
              <div className="flex items-center gap-2">
                {selectedStyle && (
                  <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                    {selectedStyle.qualityIndicator?.emoji} {selectedStyle.name}
                  </Badge>
                )}
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setShowFilters(!showFilters)}
                  className="flex items-center gap-2"
                >
                  <Filter className="h-4 w-4" />
                  Filter ({getFilterBadgeCount()})
                </Button>
              </div>
            </div>
          </CardHeader>

          {/* Filter Controls */}
          {showFilters && (
            <div className="px-6 pb-4 border-b">
              <div className="flex items-center gap-4">
                <span className="text-sm font-medium">Show:</span>
                <div className="flex gap-2">
                  {(['recommended', 'compatible', 'all'] as const).map((level) => (
                    <Button
                      type="button"
                      key={level}
                      variant={filterLevel === level ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setFilterLevel(level)}
                      className="capitalize"
                    >
                      {level}
                      {level === 'recommended' && ' (Best)'}
                    </Button>
                  ))}
                </div>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setFilterLevel('recommended');
                    setShowFilters(false);
                  }}
                  className="ml-auto flex items-center gap-2"
                >
                  <RotateCcw className="h-4 w-4" />
                  Reset
                </Button>
              </div>
            </div>
          )}

          <CardContent className="pt-6">
            {filteredStyles.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>No style profiles available for this template.</p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setFilterLevel('all')}
                  className="mt-2"
                >
                  Show All Styles
                </Button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredStyles.map((style) => (
                  <Card
                    key={style.id}
                    className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
                      selectedStyle?.id === style.id
                        ? 'ring-2 ring-purple-500 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20'
                        : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                    }`}
                    onClick={() => onStyleSelect(style)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-2">
                            <h3 className="font-medium text-sm truncate text-gray-900 dark:text-gray-100">
                              {style.name}
                            </h3>
                            {style.qualityIndicator && (
                              <Badge
                                variant="outline"
                                className={`text-xs ${
                                  style.qualityIndicator.color === 'green'
                                    ? 'bg-green-50 text-green-700 border-green-200'
                                    : style.qualityIndicator.color === 'yellow'
                                    ? 'bg-yellow-50 text-yellow-700 border-yellow-200'
                                    : 'bg-red-50 text-red-700 border-red-200'
                                }`}
                              >
                                {style.qualityIndicator.emoji} {style.qualityIndicator.label}
                              </Badge>
                            )}
                          </div>
                          <p className="text-xs text-gray-800 dark:text-gray-200 line-clamp-2 text-ellipsis overflow-hidden mb-2">
                            {style.description}
                          </p>
                          <div className="flex gap-2">
                            <Badge variant="secondary" className="text-xs bg-gradient-to-r from-purple-100 to-pink-100 text-purple-800 dark:from-purple-900 dark:to-pink-900 dark:text-purple-200 border-purple-200 dark:border-purple-700">
                              {style.category}
                            </Badge>
                            {style.tone && (
                              <Badge variant="outline" className="text-xs">
                                {style.tone}
                              </Badge>
                            )}
                          </div>
                        </div>
                        {style.qualityScore && (
                          <div className="text-right">
                            <div className="text-xs font-medium text-gray-500">
                              Quality
                            </div>
                            <div className="text-sm font-bold">
                              {style.qualityScore}%
                            </div>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
        </div>
      )}

      {/* Proceed Button */}
      {selectedTemplate && selectedStyle && (
        <div className="flex justify-center">
          <Button
            onClick={onProceed}
            size="lg"
            className="px-8 py-3 text-base font-medium"
          >
            Proceed to Content Generation
            <ChevronRight className="ml-2 h-5 w-5" />
          </Button>
        </div>
      )}
    </div>
  );
}