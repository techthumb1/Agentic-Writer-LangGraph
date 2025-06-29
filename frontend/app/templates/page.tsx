'use client';

import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
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
  Plus
} from 'lucide-react';

type Template = {
  id: string;
  name: string;
  description: string;
  category: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedTime: string;
  popularity: number;
  icon: string;
};

const mockTemplates: Template[] = [
  {
    id: '1',
    name: 'Blog Article Generator',
    description: 'Create engaging blog posts with SEO optimization and compelling headlines.',
    category: 'Content Marketing',
    difficulty: 'beginner',
    estimatedTime: '5-10 min',
    popularity: 95,
    icon: 'FileText'
  },
  {
    id: '2',
    name: 'Social Media Campaign',
    description: 'Generate cohesive social media content across multiple platforms.',
    category: 'Social Media',
    difficulty: 'intermediate',
    estimatedTime: '10-15 min',
    popularity: 87,
    icon: 'TrendingUp'
  },
  {
    id: '3',
    name: 'Technical Documentation',
    description: 'Create clear, comprehensive technical guides and API documentation.',
    category: 'Technical Writing',
    difficulty: 'advanced',
    estimatedTime: '15-25 min',
    popularity: 78,
    icon: 'BookOpen'
  },
  {
    id: '4',
    name: 'Email Newsletter',
    description: 'Craft engaging newsletters that drive engagement and conversions.',
    category: 'Email Marketing',
    difficulty: 'beginner',
    estimatedTime: '5-8 min',
    popularity: 92,
    icon: 'Mail'
  },
  {
    id: '5',
    name: 'Business Proposal',
    description: 'Generate professional business proposals and executive summaries.',
    category: 'Business',
    difficulty: 'intermediate',
    estimatedTime: '20-30 min',
    popularity: 83,
    icon: 'Briefcase'
  },
  {
    id: '6',
    name: 'Press Release',
    description: 'Create compelling press releases for product launches and company news.',
    category: 'Public Relations',
    difficulty: 'intermediate',
    estimatedTime: '10-15 min',
    popularity: 75,
    icon: 'Newspaper'
  }
];

const categories = [
  'All Categories',
  'Content Marketing', 
  'Social Media', 
  'Technical Writing', 
  'Email Marketing', 
  'Business', 
  'Public Relations'
];

const getIcon = (iconName: string) => {
  const icons = {
    FileText,
    TrendingUp,
    BookOpen,
    Mail,
    Briefcase,
    Newspaper,
    Zap
  };
  return icons[iconName as keyof typeof icons] || FileText;
};

const getDifficultyColor = (difficulty: string) => {
  switch (difficulty) {
    case 'beginner': return 'text-green-400';
    case 'intermediate': return 'text-yellow-400';
    case 'advanced': return 'text-red-400';
    default: return 'text-gray-400';
  }
};

export default function TemplatesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All Categories');
  const [selectedDifficulty, setSelectedDifficulty] = useState('all');

  const { data: templates = mockTemplates, isLoading } = useQuery({
    queryKey: ['templates'],
    queryFn: async () => {
      // Mock API call - replace with real implementation
      await new Promise(resolve => setTimeout(resolve, 1000));
      return mockTemplates;
    },
  });

  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'All Categories' || template.category === selectedCategory;
    const matchesDifficulty = selectedDifficulty === 'all' || template.difficulty === selectedDifficulty;
    
    return matchesSearch && matchesCategory && matchesDifficulty;
  });

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
              <div className="text-2xl font-bold text-white">{templates.length}</div>
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
          {isLoading ? (
            <div className="flex justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400"></div>
            </div>
          ) : (
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
                  const IconComponent = getIcon(template.icon);
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
                              <span className="text-sm text-gray-300">{template.popularity}%</span>
                            </div>
                          </div>
                        </div>
                        <div className={`px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(template.difficulty)} bg-white/10`}>
                          {template.difficulty}
                        </div>
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
                          <span>{template.estimatedTime}</span>
                        </div>
                        <span className="bg-purple-600/20 text-purple-300 px-2 py-1 rounded text-xs">
                          {template.category}
                        </span>
                      </div>

                      <div className="flex space-x-2">
                        <Button 
                          className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white text-sm"
                          size="sm"
                        >
                          <Zap className="h-4 w-4 mr-1" />
                          Use Template
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          className="border-purple-400 text-purple-300 hover:bg-purple-900/20"
                        >
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
          )}

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
                className="w-full sm:w-auto border-purple-400 text-purple-300 hover:bg-purple-900/20 border-2 font-semibold px-8 py-3 rounded-full shadow-md transition-all duration-300 hover:scale-105"
              >
                Contact Support
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}