// components/PublishingManager.tsx - Enhanced Publishing for WriterzRoom
'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { useToast } from '@/hooks/use-toast';
import { 
  Send, 
  Settings, 
  Globe, 
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

interface PublishingPlatform {
  id: string;
  name: string;
  icon: string;
  color: string;
  connected: boolean;
  capabilities: string[];
}

interface PublishingOptions {
  tags?: string;
  publication?: string;
  subtitle?: string;
  sendNewsletter?: boolean;
  contentType?: string;
  immediate?: boolean;
  scheduled?: boolean;
}

interface PublishingManagerProps {
  content: {
    title: string;
    content: string;
    templateId: string;
    styleProfile: string;
  };
  onPublish: (platform: string, options: PublishingOptions) => Promise<void>;
  onSchedule: (platform: string, scheduledTime: Date, options: PublishingOptions) => Promise<void>;
}

export default function PublishingManager({ content, onPublish, onSchedule }: PublishingManagerProps) {
  const [isPublishing, setIsPublishing] = useState(false);
  const [publishingOptions, setPublishingOptions] = useState<PublishingOptions>({});
  const [scheduledTime, setScheduledTime] = useState<string>('');
  const [showScheduler, setShowScheduler] = useState(false);
  
  const { toast } = useToast();

  // Available publishing platforms (based on your existing enhanced_publisher.py)
  const platforms: PublishingPlatform[] = [
    {
      id: 'substack',
      name: 'Substack',
      icon: '📰',
      color: 'bg-orange-500',
      connected: true,
      capabilities: ['draft', 'publish', 'schedule', 'newsletter']
    },
    {
      id: 'medium',
      name: 'Medium',
      icon: '✍️',
      color: 'bg-green-500',
      connected: true,
      capabilities: ['draft', 'publish', 'tags', 'publications']
    },
    {
      id: 'linkedin',
      name: 'LinkedIn',
      icon: '💼',
      color: 'bg-blue-600',
      connected: true,
      capabilities: ['post', 'article', 'schedule']
    },
    {
      id: 'twitter',
      name: 'Twitter/X',
      icon: '🐦',
      color: 'bg-black',
      connected: false,
      capabilities: ['thread', 'single', 'schedule']
    },
    {
      id: 'wordpress',
      name: 'WordPress',
      icon: '📝',
      color: 'bg-blue-500',
      connected: true,
      capabilities: ['draft', 'publish', 'schedule', 'categories']
    },
    {
      id: 'ghost',
      name: 'Ghost',
      icon: '👻',
      color: 'bg-gray-800',
      connected: false,
      capabilities: ['draft', 'publish', 'schedule', 'members']
    }
  ];

  const handlePublishNow = async (platformId: string) => {
    setIsPublishing(true);
    try {
      await onPublish(platformId, {
        ...publishingOptions,
        immediate: true
      });
      
      toast({
        title: "Content Published!",
        description: `Successfully published to ${platforms.find(p => p.id === platformId)?.name}`,
        variant: "default",
      });
    } catch (error) {
      toast({
        title: "Publishing Failed",
        description: error instanceof Error ? error.message : "Failed to publish content",
        variant: "destructive",
      });
    } finally {
      setIsPublishing(false);
    }
  };

  const handleSchedulePublish = async (platformId: string) => {
    if (!scheduledTime) {
      toast({
        title: "Schedule Required",
        description: "Please select a date and time for scheduling",
        variant: "destructive",
      });
      return;
    }

    setIsPublishing(true);
    try {
      await onSchedule(platformId, new Date(scheduledTime), {
        ...publishingOptions,
        scheduled: true
      });
      
      toast({
        title: "Content Scheduled!",
        description: `Scheduled for ${new Date(scheduledTime).toLocaleString()}`,
        variant: "default",
      });
      
      setShowScheduler(false);
      setScheduledTime('');
    } catch (error) {
      toast({
        title: "Scheduling Failed",
        description: error instanceof Error ? error.message : "Failed to schedule content",
        variant: "destructive",
      });
    } finally {
      setIsPublishing(false);
    }
  };

  const renderPlatformOptions = (platform: PublishingPlatform) => {
    switch (platform.id) {
      case 'medium':
        return (
          <div className="space-y-3">
            <div>
              <Label htmlFor="medium-tags">Tags (comma-separated)</Label>
              <Input
                id="medium-tags"
                placeholder="ai, writing, technology"
                value={publishingOptions.tags || ''}
                onChange={(e) => setPublishingOptions((prev: PublishingOptions) => ({ ...prev, tags: e.target.value }))}
              />
            </div>
            <div>
              <Label htmlFor="medium-publication">Publication</Label>
              <Select onValueChange={(value) => setPublishingOptions((prev: PublishingOptions) => ({ ...prev, publication: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="Select publication (optional)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Publish to your profile</SelectItem>
                  <SelectItem value="towards-data-science">Towards Data Science</SelectItem>
                  <SelectItem value="better-programming">Better Programming</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        );
      
      case 'substack':
        return (
          <div className="space-y-3">
            <div>
              <Label htmlFor="substack-subtitle">Subtitle</Label>
              <Input
                id="substack-subtitle"
                placeholder="Brief description for newsletter"
                value={publishingOptions.subtitle || ''}
                onChange={(e) => setPublishingOptions((prev: PublishingOptions) => ({ ...prev, subtitle: e.target.value }))}
              />
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="substack-newsletter"
                checked={publishingOptions.sendNewsletter || false}
                onChange={(e) => setPublishingOptions((prev: PublishingOptions) => ({ ...prev, sendNewsletter: e.target.checked }))}
              />
              <Label htmlFor="substack-newsletter">Send as newsletter to subscribers</Label>
            </div>
          </div>
        );
      
      case 'linkedin':
        return (
          <div className="space-y-3">
            <div>
              <Label htmlFor="linkedin-type">Content Type</Label>
              <Select onValueChange={(value) => setPublishingOptions((prev: PublishingOptions) => ({ ...prev, contentType: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="Select content type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="article">Article</SelectItem>
                  <SelectItem value="post">Post</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Globe className="h-5 w-5" />
          Publish Content
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {platforms.map((platform) => (
            <Card key={platform.id} className={`relative ${!platform.connected ? 'opacity-60' : ''}`}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{platform.icon}</span>
                    <span className="font-medium">{platform.name}</span>
                  </div>
                  {platform.connected ? (
                    <Badge variant="default" className="bg-green-500">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Connected
                    </Badge>
                  ) : (
                    <Badge variant="secondary">
                      <AlertCircle className="h-3 w-3 mr-1" />
                      Not Connected
                    </Badge>
                  )}
                </div>
                
                <div className="flex flex-wrap gap-1 mb-3">
                  {platform.capabilities.map((cap) => (
                    <Badge key={cap} variant="outline" className="text-xs">
                      {cap}
                    </Badge>
                  ))}
                </div>

                {platform.connected ? (
                  <div className="space-y-2">
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button 
                          className="w-full" 
                          size="sm"
                        >
                          <Send className="h-3 w-3 mr-1" />
                          Publish Now
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-md">
                        <DialogHeader>
                          <DialogTitle>Publish to {platform.name}</DialogTitle>
                        </DialogHeader>
                        <div className="space-y-4">
                          {renderPlatformOptions(platform)}
                          <div className="flex gap-2">
                            <Button 
                              onClick={() => handlePublishNow(platform.id)}
                              disabled={isPublishing}
                              className="flex-1"
                            >
                              {isPublishing ? 'Publishing...' : 'Publish Now'}
                            </Button>
                            <Dialog open={showScheduler} onOpenChange={setShowScheduler}>
                              <DialogTrigger asChild>
                                <Button variant="outline" size="sm">
                                  <Clock className="h-3 w-3" />
                                </Button>
                              </DialogTrigger>
                              <DialogContent>
                                <DialogHeader>
                                  <DialogTitle>Schedule Publication</DialogTitle>
                                </DialogHeader>
                                <div className="space-y-4">
                                  <div>
                                    <Label htmlFor="schedule-time">Schedule Date & Time</Label>
                                    <Input
                                      id="schedule-time"
                                      type="datetime-local"
                                      value={scheduledTime}
                                      onChange={(e) => setScheduledTime(e.target.value)}
                                      min={new Date().toISOString().slice(0, 16)}
                                    />
                                  </div>
                                  <Button 
                                    onClick={() => handleSchedulePublish(platform.id)}
                                    disabled={isPublishing || !scheduledTime}
                                    className="w-full"
                                  >
                                    {isPublishing ? 'Scheduling...' : 'Schedule'}
                                  </Button>
                                </div>
                              </DialogContent>
                            </Dialog>
                          </div>
                        </div>
                      </DialogContent>
                    </Dialog>
                  </div>
                ) : (
                  <Button variant="outline" size="sm" className="w-full">
                    <Settings className="h-3 w-3 mr-1" />
                    Connect Account
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Content Preview */}
        <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
          <h4 className="font-medium mb-2">Content Preview</h4>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            <p><strong>Title:</strong> {content.title}</p>
            <p><strong>Template:</strong> {content.templateId}</p>
            <p><strong>Style:</strong> {content.styleProfile}</p>
            <p><strong>Length:</strong> {content.content.split(' ').length} words</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}