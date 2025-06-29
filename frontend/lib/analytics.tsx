// lib/analytics.ts
export interface ContentMetrics {
  contentId: string;
  userId: string;
  contentType: string;
  wordsGenerated: number;
  timeToGenerate: number;
  userSatisfactionScore?: number;
  timeSavedVsManual?: number;
}

export interface UserStats {
  userId: string;
  totalContentGenerated: number;
  totalTimeSaved: number;
  averageSatisfactionScore: number;
  lastActiveDate: Date;
  signupDate: Date;
}

export interface PlatformStats {
  totalActiveUsers: number; // Users active in last 30 days
  monthlyContentGenerated: number;
  averageSatisfactionRate: number;
  averageTimeSavedPercentage: number;
  lastUpdated: Date;
}

// Analytics tracking functions
export class AgentWriteAnalytics {
  static trackContentGeneration(metrics: ContentMetrics) {
    // Track each piece of content generated
    // Implementation would connect to your analytics service
    console.log('Content generated:', metrics);
  }

  static trackUserSatisfaction(userId: string, score: number, contentId?: string) {
    // Track satisfaction scores
    console.log('Satisfaction tracked:', { userId, score, contentId });
  }

  static trackTimeSaved(userId: string, contentId: string, timeSaved: number) {
    // Track time savings for each generation
    console.log('Time saved tracked:', { userId, contentId, timeSaved });
  }

  static async getPlatformStats(): Promise<PlatformStats> {
    // Get current platform statistics
    // This would query your database for real stats
    return {
      totalActiveUsers: 156, // Start with current real number
      monthlyContentGenerated: 2847,
      averageSatisfactionRate: 87.3,
      averageTimeSavedPercentage: 34.2,
      lastUpdated: new Date()
    };
  }

  static async getUserStats(userId: string): Promise<UserStats> {
    // Get individual user statistics
    return {
      userId,
      totalContentGenerated: 23,
      totalTimeSaved: 4.2, // hours
      averageSatisfactionScore: 4.6,
      lastActiveDate: new Date(),
      signupDate: new Date('2024-01-15')
    };
  }
}

// Database schema additions you might want to consider
export interface ContentGenerationLog {
  id: string;
  userId: string;
  templateId: string;
  contentType: 'article' | 'summary' | 'social_post' | 'email' | 'other';
  wordsGenerated: number;
  timeToGenerate: number; // milliseconds
  satisfactionRating?: number; // 1-5 scale
  estimatedTimeSaved?: number; // hours
  createdAt: Date;
}

export interface UserSatisfactionSurvey {
  id: string;
  userId: string;
  overallSatisfaction: number; // 1-5 scale
  features: {
    easeOfUse: number;
    contentQuality: number;
    speed: number;
    valueForMoney: number;
  };
  feedback?: string;
  createdAt: Date;
}

export interface UserMetrics {
  id: string;
  userId: string;
  month: string; // YYYY-MM format
  contentGeneratedCount: number;
  totalTimeSaved: number;
  averageSatisfactionScore: number;
  isActiveUser: boolean; // Generated content this month
  updatedAt: Date;
}