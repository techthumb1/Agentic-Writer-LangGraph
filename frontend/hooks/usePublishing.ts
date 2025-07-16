// hooks/usePublishing.ts - Integration with your existing enhanced_publisher.py
import { useState, useCallback } from 'react';

interface PublishingOptions {
  immediate?: boolean;
  scheduled?: boolean;
  scheduledTime?: string;
  tags?: string;
  subtitle?: string;
  publication?: string;
  contentType?: string;
  sendNewsletter?: boolean;
}

interface ContentToPublish {
  title: string;
  content: string;
  templateId: string;
  styleProfile: string;
}

export function usePublishing() {
  const [isPublishing, setIsPublishing] = useState(false);
  const [publishingStatus, setPublishingStatus] = useState<Record<string, string>>({});
  
  // const { toast } = useToast();

  // Publish content to a platform
  const publishContent = useCallback(async (
    content: ContentToPublish,
    platform: string,
    options: PublishingOptions = {}
  ) => {
    setIsPublishing(true);
    setPublishingStatus(prev => ({ ...prev, [platform]: 'publishing' }));

    try {
      const response = await fetch('/api/publish', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: content.title,
          content: content.content,
          platform,
          options: {
            ...options,
            immediate: !options.scheduled,
          },
          templateId: content.templateId,
          styleProfile: content.styleProfile,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Publishing failed');
      }

      const result = await response.json();
      
      setPublishingStatus(prev => ({ ...prev, [platform]: 'published' }));
      
      return result.data;

    } catch (error) {
      setPublishingStatus(prev => ({ ...prev, [platform]: 'error' }));
      throw error;
    } finally {
      setIsPublishing(false);
    }
  }, []);

  // Schedule content for future publishing
  const scheduleContent = useCallback(async (
    content: ContentToPublish,
    platform: string,
    scheduledTime: Date,
    options: PublishingOptions = {}
  ) => {
    setIsPublishing(true);
    setPublishingStatus(prev => ({ ...prev, [platform]: 'scheduling' }));

    try {
      const response = await fetch('/api/publish', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: content.title,
          content: content.content,
          platform,
          options: {
            ...options,
            scheduled: true,
            scheduledTime: scheduledTime.toISOString(),
          },
          templateId: content.templateId,
          styleProfile: content.styleProfile,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Scheduling failed');
      }

      const result = await response.json();
      
      setPublishingStatus(prev => ({ ...prev, [platform]: 'scheduled' }));
      
      return result.data;

    } catch (error) {
      setPublishingStatus(prev => ({ ...prev, [platform]: 'error' }));
      throw error;
    } finally {
      setIsPublishing(false);
    }
  }, []);

  // Get publishing platforms status
  const getPublishingStatus = useCallback(async (userId?: string) => {
    try {
      const params = userId ? `?userId=${userId}` : '';
      const response = await fetch(`/api/publish${params}`);
      
      if (!response.ok) {
        throw new Error('Failed to get publishing status');
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting publishing status:', error);
      return { platforms: [], scheduledPosts: [], publishingHistory: [] };
    }
  }, []);

  // Reset publishing status
  const resetStatus = useCallback(() => {
    setPublishingStatus({});
  }, []);

  return {
    isPublishing,
    publishingStatus,
    publishContent,
    scheduleContent,
    getPublishingStatus,
    resetStatus,
  };
}