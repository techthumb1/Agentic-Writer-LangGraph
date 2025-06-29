"use client"

import { Button } from '@/components/ui/button';
import { 
  User, 
  Mail, 
  Calendar,
  FileText,
  TrendingUp,
  Clock,
  Star,
  Edit,
  Save,
  Camera
} from 'lucide-react';
import { useSession } from 'next-auth/react';
import { useState } from 'react';

interface ProfileData {
  name: string;
  email: string;
  company: string;
  role: string;
  bio: string;
  joinDate: string;
}

interface UserStats {
  contentGenerated: number;
  totalTimeSaved: number;
  averageRating: number;
  daysActive: number;
}

interface ContentItem {
  title: string;
  type: string;
  createdAt: string;
  words: number;
  rating: number;
}

export default function ProfilePage() {
  const { data: session } = useSession();
  const [isEditing, setIsEditing] = useState(false);
  
  const [profileData, setProfileData] = useState<ProfileData>({
    name: (session?.user?.name as string) || 'John Doe',
    email: (session?.user?.email as string) || 'john.doe@example.com',
    company: 'TechFlow Solutions',
    role: 'Content Marketing Manager',
    bio: 'Passionate about creating engaging content that drives results. Love leveraging AI to streamline content creation workflows.',
    joinDate: '2025-01-15'
  });

  // Mock user stats - replace with real data from your analytics
  const userStats: UserStats = {
    contentGenerated: 47,
    totalTimeSaved: 12.3, // hours
    averageRating: 4.7,
    daysActive: 45
  };

  const recentContent: ContentItem[] = [
    {
      title: "AI in Modern Marketing: A Complete Guide",
      type: "Article",
      createdAt: "2024-06-20",
      words: 2500,
      rating: 5
    },
    {
      title: "10 Content Creation Tips for 2024",
      type: "Blog Post",
      createdAt: "2024-06-18",
      words: 1800,
      rating: 4.5
    },
    {
      title: "Social Media Content Calendar Template",
      type: "Template",
      createdAt: "2024-06-15",
      words: 800,
      rating: 4.8
    }
  ];

  const handleSave = () => {
    // Here you would save the profile data to your backend
    console.log('Saving profile data:', profileData);
    setIsEditing(false);
  };

  const handleInputChange = (field: keyof ProfileData, value: string) => {
    setProfileData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Generate initials from name
  const getInitials = (name: string): string => {
    return name
      .split(' ')
      .map((n: string) => n[0])
      .join('')
      .toUpperCase();
  };

  if (!session) {
    return (
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-2xl mx-auto text-center text-white">
          <h1 className="text-3xl font-bold mb-4">Access Denied</h1>
          <p className="text-gray-300 mb-6">Please sign in to view your profile.</p>
          <Button className="bg-purple-600 hover:bg-purple-700">
            Sign In
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="max-w-4xl mx-auto text-white">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2">
            Your 
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
              {" "}Profile
            </span>
          </h1>
          <p className="text-gray-300">Manage your account and track your content creation journey</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Profile Card */}
          <div className="lg:col-span-1">
            <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6">
              {/* Profile Picture */}
              <div className="text-center mb-6">
                <div className="relative inline-block">
                  <div className="w-24 h-24 bg-gradient-to-r from-purple-400 to-pink-600 rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">
                    {getInitials(profileData.name)}
                  </div>
                  <button className="absolute bottom-0 right-0 bg-purple-600 hover:bg-purple-700 rounded-full p-2 transition-colors">
                    <Camera className="h-4 w-4 text-white" />
                  </button>
                </div>
              </div>

              {/* Profile Info */}
              <div className="space-y-4">
                {isEditing ? (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-1">Name</label>
                      <input
                        type="text"
                        value={profileData.name}
                        onChange={(e) => handleInputChange('name', e.target.value)}
                        className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-1">Company</label>
                      <input
                        type="text"
                        value={profileData.company}
                        onChange={(e) => handleInputChange('company', e.target.value)}
                        className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-1">Role</label>
                      <input
                        type="text"
                        value={profileData.role}
                        onChange={(e) => handleInputChange('role', e.target.value)}
                        className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-1">Bio</label>
                      <textarea
                        value={profileData.bio}
                        onChange={(e) => handleInputChange('bio', e.target.value)}
                        rows={3}
                        className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                  </>
                ) : (
                  <>
                    <div className="flex items-center text-gray-300">
                      <User className="h-4 w-4 mr-2 text-purple-400" />
                      <span className="font-medium">{profileData.name}</span>
                    </div>
                    <div className="flex items-center text-gray-300">
                      <Mail className="h-4 w-4 mr-2 text-purple-400" />
                      <span className="text-sm">{profileData.email}</span>
                    </div>
                    <div className="flex items-center text-gray-300">
                      <TrendingUp className="h-4 w-4 mr-2 text-purple-400" />
                      <span className="text-sm">{profileData.role}</span>
                    </div>
                    <div className="text-gray-300 text-sm">
                      <strong className="text-purple-400">Company:</strong> {profileData.company}
                    </div>
                    <div className="text-gray-300 text-sm">
                      <strong className="text-purple-400">Bio:</strong>
                      <p className="mt-1">{profileData.bio}</p>
                    </div>
                    <div className="flex items-center text-gray-400 text-sm">
                      <Calendar className="h-4 w-4 mr-2" />
                      <span>Joined {new Date(profileData.joinDate).toLocaleDateString()}</span>
                    </div>
                  </>
                )}

                {/* Edit/Save Button */}
                <div className="pt-4">
                  {isEditing ? (
                    <div className="flex space-x-2">
                      <Button 
                        onClick={handleSave}
                        className="flex-1 bg-green-600 hover:bg-green-700"
                      >
                        <Save className="h-4 w-4 mr-2" />
                        Save
                      </Button>
                      <Button 
                        onClick={() => setIsEditing(false)}
                        variant="outline"
                        className="flex-1 border-gray-600 text-gray-300 hover:bg-gray-700"
                      >
                        Cancel
                      </Button>
                    </div>
                  ) : (
                    <Button 
                      onClick={() => setIsEditing(true)}
                      className="w-full bg-purple-600 hover:bg-purple-700"
                    >
                      <Edit className="h-4 w-4 mr-2" />
                      Edit Profile
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4 text-center">
                <FileText className="h-6 w-6 text-purple-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-white">{userStats.contentGenerated}</div>
                <div className="text-xs text-gray-400">Content Created</div>
              </div>
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4 text-center">
                <Clock className="h-6 w-6 text-blue-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-white">{userStats.totalTimeSaved}h</div>
                <div className="text-xs text-gray-400">Time Saved</div>
              </div>
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4 text-center">
                <Star className="h-6 w-6 text-yellow-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-white">{userStats.averageRating}</div>
                <div className="text-xs text-gray-400">Avg Rating</div>
              </div>
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4 text-center">
                <Calendar className="h-6 w-6 text-green-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-white">{userStats.daysActive}</div>
                <div className="text-xs text-gray-400">Days Active</div>
              </div>
            </div>

            {/* Recent Content */}
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-white mb-6">Recent Content</h3>
              <div className="space-y-4">
                {recentContent.map((content, index) => (
                  <div key={index} className="bg-white/5 border border-white/10 rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-white mb-1">{content.title}</h4>
                        <div className="flex items-center space-x-4 text-sm text-gray-400">
                          <span className="bg-purple-600/20 text-purple-300 px-2 py-1 rounded text-xs">
                            {content.type}
                          </span>
                          <span>{content.words} words</span>
                          <span>{new Date(content.createdAt).toLocaleDateString()}</span>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <Star className="h-4 w-4 text-yellow-400 mr-1" />
                        <span className="text-sm text-gray-300">{content.rating}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Achievement Section */}
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-white mb-6">Achievements</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center p-3 bg-gradient-to-r from-purple-600/20 to-pink-600/20 rounded-lg border border-purple-400/20">
                  <div className="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center mr-3">
                    <FileText className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <div className="font-medium text-white">Content Creator</div>
                    <div className="text-sm text-gray-400">Generated 25+ pieces</div>
                  </div>
                </div>
                <div className="flex items-center p-3 bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-lg border border-blue-400/20">
                  <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mr-3">
                    <Clock className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <div className="font-medium text-white">Time Saver</div>
                    <div className="text-sm text-gray-400">Saved 10+ hours</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}