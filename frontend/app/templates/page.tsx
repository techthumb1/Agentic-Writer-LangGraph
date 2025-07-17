//frontend/app/templates/page.tsx

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  FileText, 
  Search, 
  Star, 
  Clock, 
  Users, 
  Zap,
  TrendingUp,
  BookOpen,
  Briefcase,
  Newspaper,
  Mail,
  Plus,
  Eye,
  AlertCircle,
  Loader2,
  X
} from 'lucide-react';
import { useTemplates } from '@/hooks/useTemplates';
import { Template } from '@/types/template';

const categories = [
  'All Categories',
  'Content Marketing', 
  'Social Media', 
  'Technical Writing', 
  'Email Marketing', 
  'Business', 
  'Public Relations'
];

const getIcon = (category: string) => {
  const icons = {
    'Content Marketing': FileText,
    'Social Media': TrendingUp,
    'Technical Writing': BookOpen,
    'Email Marketing': Mail,
    'Business': Briefcase,
    'Public Relations': Newspaper,
  };
  return icons[category as keyof typeof icons] || FileText;
};

const getDifficultyColor = (difficulty?: string) => {
  switch (difficulty) {
    case 'beginner': return 'text-green-400';
    case 'intermediate': return 'text-yellow-400';
    case 'advanced': return 'text-red-400';
    default: return 'text-gray-400';
  }
};

// Extended Template interface for this page
interface ExtendedTemplate extends Template {
  difficulty?: string;
  estimatedLength?: string;
  instructions?: string;
}

// Template preview modal component
const TemplatePreviewModal = ({ 
  template, 
  isOpen, 
  onClose 
}: { 
  template: ExtendedTemplate | null;
  isOpen: boolean;
  onClose: () => void;
}) => {
  if (!isOpen || !template) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">{template.name}</h2>
            <Button variant="outline" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
        
        <div className="p-6 space-y-6">
          {/* Template Overview */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-2">Description</h3>
            <p className="text-gray-700">{template.description}</p>
          </div>

          {/* Template Details */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <h4 className="font-medium text-blue-900 mb-1">Category</h4>
              <p className="text-blue-700">{template.category}</p>
            </div>
            {template.difficulty && (
              <div className="bg-green-50 rounded-lg p-4">
                <h4 className="font-medium text-green-900 mb-1">Difficulty</h4>
                <p className={`font-medium ${getDifficultyColor(template.difficulty)}`}>
                  {template.difficulty}
                </p>
              </div>
            )}
            {template.estimatedLength && (
              <div className="bg-purple-50 rounded-lg p-4">
                <h4 className="font-medium text-purple-900 mb-1">Time Required</h4>
                <p className="text-purple-700">{template.estimatedLength}</p>
              </div>
            )}
          </div>

          {/* Parameters Preview */}
          {template.parameters && Array.isArray(template.parameters) && template.parameters.length > 0 && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Template Parameters</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {template.parameters.map((param: {
                  label: string;
                  required?: boolean;
                  description?: string;
                  type?: string;
                  default?: string;
                }, index: number) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-gray-900">{param.label}</span>
                      {param.required && (
                        <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded">
                          Required
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{param.description}</p>
                    <div className="text-xs text-gray-500">
                      Type: {param.type}
                      {param.default && ` • Default: ${param.default}`}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Instructions */}
          {template.instructions && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Instructions</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-700 whitespace-pre-line">{template.instructions}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default function TemplatesPage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All Categories');
  const [selectedDifficulty, setSelectedDifficulty] = useState('all');
  const [previewTemplate, setPreviewTemplate] = useState<ExtendedTemplate | null>(null);
  const [showPreview, setShowPreview] = useState(false);

  const { data: templates, isLoading, error } = useTemplates();

  const handleUseTemplate = (templateId: string) => {
    router.push(`/generate?template=${templateId}`);
  };

  const handlePreviewTemplate = (template: ExtendedTemplate) => {
    setPreviewTemplate(template);
    setShowPreview(true);
  };

  // Cast templates to ExtendedTemplate for this page
  const extendedTemplates = (templates as ExtendedTemplate[]) || [];

  const filteredTemplates = extendedTemplates.filter(template => {
    const matchesSearch = template?.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                     template?.description?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'All Categories' || template.category === selectedCategory;
    const matchesDifficulty = selectedDifficulty === 'all' || template.difficulty === selectedDifficulty;
    
    return matchesSearch && matchesCategory && matchesDifficulty;
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center">
        <div className="text-center text-white">
          <Loader2 className="h-12 w-12 animate-spin mx-auto mb-4 text-purple-400" />
          <p className="text-xl">Loading templates...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center">
        <div className="text-center text-white max-w-md">
          <AlertCircle className="h-12 w-12 mx-auto mb-4 text-red-400" />
          <h2 className="text-xl font-semibold mb-2">Failed to Load Templates</h2>
          <p className="text-gray-300 mb-4">Could not connect to the backend API</p>
          <Button onClick={() => window.location.reload()} variant="outline">
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-6xl mx-auto text-white">
          {/* Header */}
          <header className="text-center mb-12">
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold mb-6">
              Content
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
                {" "}Templates
              </span>
            </h1>
            <p className="text-xl text-gray-300 leading-relaxed max-w-3xl mx-auto">
              Choose from our library of professionally crafted templates to accelerate your content creation with AgentWrite Pro.
            </p>
          </header>

          {/* Search and Filters */}
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 mb-8">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="md:col-span-2 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search templates..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-gray-800 border-gray-600 text-white focus:border-purple-500"
                />
              </div>
              
              <div>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-600 rounded-md px-3 py-2 text-white focus:border-purple-500 focus:outline-none"
                >
                  {categories.map(category => (
                    <option key={category} value={category}>{category}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <select
                  value={selectedDifficulty}
                  onChange={(e) => setSelectedDifficulty(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-600 rounded-md px-3 py-2 text-white focus:border-purple-500 focus:outline-none"
                >
                  <option value="all">All Difficulty</option>
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4 text-center">
              <FileText className="h-6 w-6 text-purple-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">{extendedTemplates?.length || 0}</div>
              <div className="text-xs text-gray-400">Templates Available</div>
            </div>
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4 text-center">
              <Users className="h-6 w-6 text-blue-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">15K+</div>
              <div className="text-xs text-gray-400">Monthly Uses</div>
            </div>
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4 text-center">
              <Star className="h-6 w-6 text-yellow-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">4.8</div>
              <div className="text-xs text-gray-400">Avg Rating</div>
            </div>
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4 text-center">
              <Clock className="h-6 w-6 text-green-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">85%</div>
              <div className="text-xs text-gray-400">Time Saved</div>
            </div>
          </div>

          {/* Templates Grid */}
          <>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-semibold text-white">
                {filteredTemplates.length} Templates Found
              </h2>
              <Button className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white">
                <Plus className="h-4 w-4 mr-2" />
                Request Template
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredTemplates.map((template) => {
                const IconComponent = getIcon(template.category);
                return (
                  <div
                    key={template.id}
                    className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 hover:bg-white/15 transition-all duration-300 transform hover:scale-105 cursor-pointer group"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="bg-purple-600 w-12 h-12 rounded-lg flex items-center justify-center group-hover:bg-purple-500 transition-colors">
                          <IconComponent className="h-6 w-6 text-white" />
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="flex items-center">
                            <Star className="h-4 w-4 text-yellow-400 mr-1" />
                            <span className="text-sm text-gray-300">95%</span>
                          </div>
                        </div>
                      </div>
                      {template.difficulty && (
                        <div className={`px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(template.difficulty)} bg-white/10`}>
                          {template.difficulty}
                        </div>
                      )}
                    </div>

                    <h3 className="text-xl font-semibold text-white mb-2 group-hover:text-purple-300 transition-colors">
                      {template.name}
                    </h3>
                    
                    <p className="text-gray-300 text-sm mb-4 leading-relaxed">
                      {template.description}
                    </p>

                    <div className="flex items-center justify-between text-sm text-gray-400 mb-4">
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        <span>{template.estimatedLength || '5-10 min'}</span>
                      </div>
                      <span className="bg-purple-600/20 text-purple-300 px-2 py-1 rounded text-xs">
                        {template.category}
                      </span>
                    </div>

                    <div className="flex space-x-2">
                      <Button 
                        onClick={() => handleUseTemplate(template.id)}
                        className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white text-sm"
                        size="sm"
                      >
                        <Zap className="h-4 w-4 mr-1" />
                        Use Template
                      </Button>
                      <Button 
                        onClick={() => handlePreviewTemplate(template)}
                        variant="outline" 
                        size="sm"
                        className="border-purple-400 text-purple-500 hover:bg-purple-900/20"
                      >
                        <Eye className="h-4 w-4 mr-1" />
                        Preview
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>

            {filteredTemplates.length === 0 && (
              <div className="text-center py-12">
                <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">No templates found</h3>
                <p className="text-gray-400 mb-4">Try adjusting your search or filter criteria</p>
                <Button 
                  onClick={() => {
                    setSearchQuery('');
                    setSelectedCategory('All Categories');
                    setSelectedDifficulty('all');
                  }}
                  variant="outline"
                  className="border-purple-400 text-purple-300 hover:bg-purple-900/20"
                >
                  Clear Filters
                </Button>
              </div>
            )}
          </>

          {/* Popular Categories */}
          <div className="mt-16">
            <h2 className="text-3xl font-bold text-center mb-12">Popular Categories</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {categories.slice(1).map((category, index) => {
                const icons = [FileText, TrendingUp, BookOpen, Mail, Briefcase, Newspaper];
                const IconComponent = icons[index] || FileText;
                return (
                  <div
                    key={category}
                    onClick={() => setSelectedCategory(category)}
                    className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4 text-center hover:bg-white/10 transition-all duration-300 cursor-pointer group"
                  >
                    <IconComponent className="h-8 w-8 text-purple-400 mx-auto mb-2 group-hover:text-purple-300 transition-colors" />
                    <div className="text-sm font-medium text-white group-hover:text-purple-300 transition-colors">
                      {category}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* CTA Section */}
          <div className="mt-16 text-center bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-8">
            <h2 className="text-2xl sm:text-3xl font-bold mb-4">
              Can&apos;t Find What You Need?
            </h2>
            <p className="text-gray-300 mb-6 max-w-2xl mx-auto">
              Request a custom template or contact our team to create specialized content structures for your unique needs.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button
                size="lg"
                className="w-full sm:w-auto bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-8 py-3 rounded-full shadow-lg transition-all duration-300 transform hover:scale-105"
              >
                Request Custom Template
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="w-full sm:w-auto border-purple-400 text-purple-500 hover:bg-purple-900/20 border-2 font-semibold px-8 py-3 rounded-full shadow-md transition-all duration-300 hover:scale-105"
              >
                Contact Support
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Template Preview Modal */}
      <TemplatePreviewModal 
        template={previewTemplate}
        isOpen={showPreview}
        onClose={() => setShowPreview(false)}
      />
    </div>
  );
}