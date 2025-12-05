// frontend/app/profile/page.tsx
"use client"

import Image from 'next/image'
import { useSettings } from '@/lib/settings-context';
import { Button } from '@/components/ui/button';
import { showToast } from '@/lib/toast-utils';
import { 
  User, 
  Mail, 
  Calendar,
  FileText,
  Clock,
  Star,
  Edit,
  Save,
  Camera,
  Upload,
  Sparkles,
  FolderOpen,
  Settings,
  BarChart3,
  Zap,
  BookOpen
} from 'lucide-react';
import { useSession } from 'next-auth/react';
import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';

export default function ProfilePage() {
  const router = useRouter();
  const { data: session } = useSession();
  const { 
    userSettings, 
    userStats, 
    updateUserSettings,
    isLoading: settingsLoading
  } = useSettings();
  
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [editForm, setEditForm] = useState({
    name: '',
    bio: ''
  });

  const [isUploadingAvatar, setIsUploadingAvatar] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);

  useEffect(() => {
    if (session?.user?.image) {
      setAvatarUrl(session.user.image);
    }
  }, [session]);

  const handleAvatarClick = () => {
    fileInputRef.current?.click();
  };

  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      showToast.error('Invalid File', 'Please upload an image file');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      showToast.error('File Too Large', 'Maximum file size is 5MB');
      return;
    }

    try {
      setIsUploadingAvatar(true);
      const formData = new FormData();
      formData.append('avatar', file);

      const response = await fetch('/api/user/profile/avatar', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Upload failed');
      }

      const data = await response.json();
      setAvatarUrl(data.avatarUrl);
      showToast.success('Success', 'Profile picture updated');

    } catch (error) {
      console.error('Avatar upload error:', error);
      showToast.error('Upload Failed', error instanceof Error ? error.message : 'Failed to upload avatar');
    } finally {
      setIsUploadingAvatar(false);
    }
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);

      if (!editForm.name.trim()) {
        showToast.error('Validation Error', 'Name is required');
        return;
      }

      updateUserSettings({
        name: editForm.name.trim(),
        bio: editForm.bio.trim()
      });

      const response = await fetch('/api/user/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: editForm.name.trim(),
          email: userSettings.email,
          bio: editForm.bio.trim()
        })
      });

      if (!response.ok) {
        throw new Error('Failed to save to backend');
      }

      showToast.success('Success', 'Profile updated successfully');
      setIsEditing(false);

    } catch (error) {
      console.error('Failed to save profile:', error);
      showToast.error('Error', 'Failed to save profile');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
  };

  const handleEdit = () => {
    setEditForm({
      name: userSettings.name,
      bio: userSettings.bio
    });
    setIsEditing(true);
  };

  const getInitials = (name: string): string => {
    if (!name) return 'U';
    return name
      .split(' ')
      .map((n: string) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const quickActions = [
    {
      icon: Sparkles,
      label: 'Generate Content',
      description: 'Create new content',
      onClick: () => router.push('/generate'),
      color: 'from-purple-500 to-pink-500'
    },
    {
      icon: FolderOpen,
      label: 'My Content',
      description: 'View all content',
      onClick: () => router.push('/content'),
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: BarChart3,
      label: 'Analytics',
      description: 'View insights',
      onClick: () => router.push('/analytics'),
      color: 'from-green-500 to-emerald-500'
    },
    {
      icon: BookOpen,
      label: 'Templates',
      description: 'Browse templates',
      onClick: () => router.push('/templates'),
      color: 'from-orange-500 to-red-500'
    },
    {
      icon: Settings,
      label: 'Settings',
      description: 'Account settings',
      onClick: () => router.push('/settings'),
      color: 'from-gray-500 to-slate-500'
    },
    {
      icon: Zap,
      label: 'Quick Generate',
      description: 'Skip to generation',
      onClick: () => {
        showToast.info('Quick Generate', 'Opening generation wizard...');
        router.push('/generate');
      },
      color: 'from-yellow-500 to-amber-500'
    }
  ];

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

  if (settingsLoading) {
    return (
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="animate-pulse space-y-8">
            <div className="text-center">
              <div className="h-8 bg-gray-700 rounded w-48 mx-auto mb-2"></div>
              <div className="h-4 bg-gray-700 rounded w-64 mx-auto"></div>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="bg-gray-700 rounded-xl h-96"></div>
              <div className="lg:col-span-2 space-y-4">
                <div className="h-24 bg-gray-700 rounded"></div>
                <div className="h-48 bg-gray-700 rounded"></div>
                <div className="h-32 bg-gray-700 rounded"></div>
              </div>
            </div>
          </div>
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
            <span className="text-transparent bg-clip-text bg-linear-to-r from-purple-400 to-pink-600">
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
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleAvatarUpload}
                    className="hidden"
                  />
                  {avatarUrl ? (
                    <Image
                      src={avatarUrl}
                      alt="Profile"
                      width={96}
                      height={96}
                      className="w-24 h-24 rounded-full object-cover mx-auto mb-4 ring-2 ring-purple-500"
                    />
                  ) : (
                    <div className="w-24 h-24 bg-linear-to-rrom-purple-400 to-pink-600 rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">
                      {getInitials(userSettings.name)}
                    </div>
                  )}
                  <button 
                    className="absolute bottom-0 right-0 bg-purple-600 hover:bg-purple-700 rounded-full p-2 transition-colors disabled:opacity-50"
                    onClick={handleAvatarClick}
                    disabled={isUploadingAvatar}
                  >
                    {isUploadingAvatar ? (
                      <Upload className="h-4 w-4 text-white animate-pulse" />
                    ) : (
                      <Camera className="h-4 w-4 text-white" />
                    )}
                  </button>
                </div>
              </div>

              {/* Profile Info */}
              <div className="space-y-4">
                {isEditing ? (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-1">Name *</label>
                      <input
                        type="text"
                        value={editForm.name}
                        onChange={(e) => setEditForm(prev => ({ ...prev, name: e.target.value }))}
                        className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-1">Bio</label>
                      <textarea
                        value={editForm.bio}
                        onChange={(e) => setEditForm(prev => ({ ...prev, bio: e.target.value }))}
                        placeholder="Tell us about yourself"
                        rows={3}
                        className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                  </>
                ) : (
                  <>
                    <div className="flex items-center text-gray-300">
                      <User className="h-4 w-4 mr-2 text-purple-400" />
                      <span className="font-medium">{userSettings.name || 'No name set'}</span>
                    </div>
                    <div className="flex items-center text-gray-300">
                      <Mail className="h-4 w-4 mr-2 text-purple-400" />
                      <span className="text-sm">{userSettings.email}</span>
                    </div>
                    {userSettings.bio && (
                      <div className="text-gray-300 text-sm">
                        <strong className="text-purple-400">Bio:</strong>
                        <p className="mt-1">{userSettings.bio}</p>
                      </div>
                    )}
                    <div className="flex items-center text-gray-400 text-sm">
                      <Calendar className="h-4 w-4 mr-2" />
                      <span>Joined {userSettings.joinDate ? new Date(userSettings.joinDate).toLocaleDateString() : 'Unknown'}</span>
                    </div>
                  </>
                )}

                {/* Edit/Save Button */}
                <div className="pt-4">
                  {isEditing ? (
                    <div className="flex space-x-2">
                      <Button 
                        onClick={handleSave}
                        disabled={isSaving}
                        className="flex-1 bg-green-600 hover:bg-green-700"
                      >
                        <Save className="h-4 w-4 mr-2" />
                        {isSaving ? 'Saving...' : 'Save'}
                      </Button>
                      <Button 
                        onClick={handleCancel}
                        disabled={isSaving}
                        variant="outline"
                        className="flex-1 border-gray-600 text-gray-300 hover:bg-gray-700"
                      >
                        Cancel
                      </Button>
                    </div>
                  ) : (
                    <Button 
                      onClick={handleEdit}
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

            {/* Quick Actions */}
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-white mb-6">Quick Actions</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {quickActions.map((action, index) => {
                  const Icon = action.icon;
                  return (
                    <button
                      key={index}
                      onClick={action.onClick}
                      className="group relative bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 rounded-lg p-4 transition-all duration-200 text-left"
                    >
                      <div className="flex items-start space-x-4">
                        <div className={`w-12 h-12 rounded-lg bg-linear-to-r ${action.color} flex items-center justify-center shrink-0 group-hover:scale-110 transition-transform`}>
                          <Icon className="h-6 w-6 text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium text-white mb-1 group-hover:text-purple-300 transition-colors">
                            {action.label}
                          </h4>
                          <p className="text-sm text-gray-400">
                            {action.description}
                          </p>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Achievement Section */}
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-white mb-6">Achievements</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className={`flex items-center p-3 rounded-lg border ${
                  userStats.contentGenerated >= 25 
                    ? 'bg-linear-to-r from-purple-600/20 to-pink-600/20 border-purple-400/20' 
                    : 'bg-gray-800/50 border-gray-600/50'
                }`}>
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center mr-3 ${
                    userStats.contentGenerated >= 25 ? 'bg-purple-600' : 'bg-gray-600'
                  }`}>
                    <FileText className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <div className="font-medium text-white">Content Creator</div>
                    <div className="text-sm text-gray-400">
                      {userStats.contentGenerated >= 25 ? 'Generated 25+ pieces' : `${userStats.contentGenerated}/25 pieces`}
                    </div>
                  </div>
                </div>
                <div className={`flex items-center p-3 rounded-lg border ${
                  userStats.totalTimeSaved >= 10 
                    ? 'bg-linear-to-r from-blue-600/20 to-purple-600/20 border-blue-400/20' 
                    : 'bg-gray-800/50 border-gray-600/50'
                }`}>
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center mr-3 ${
                    userStats.totalTimeSaved >= 10 ? 'bg-blue-600' : 'bg-gray-600'
                  }`}>
                    <Clock className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <div className="font-medium text-white">Time Saver</div>
                    <div className="text-sm text-gray-400">
                      {userStats.totalTimeSaved >= 10 ? 'Saved 10+ hours' : `${userStats.totalTimeSaved}/10 hours`}
                    </div>
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