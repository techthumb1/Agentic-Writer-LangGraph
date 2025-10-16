// File: frontend/app/api/user/export/route.ts
import { NextResponse } from 'next/server';
import { auth } from '@/auth';
import { prisma } from '@/lib/prisma.node';

type UsageStat = {
  date: Date;
  contentGenerated: number;
  tokensConsumed: number;
  generationTime: number;
  modelsUsed: string[];
};

type GeneratedContent = {
  id: string;
  title: string | null;
  content: string;
  wordCount: number;
  status: string;
  createdAt: Date;
  templateId: string;
  styleProfileId: string;
};

export const runtime = 'nodejs';

export async function POST() {
  try {
    const session = await auth();
    
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const dbUser = await prisma.user.findUnique({
      where: { email: session.user.email },
      include: {
        generated_content: {
          select: {
            id: true,
            title: true,
            content: true,
            wordCount: true,
            status: true,
            createdAt: true,
            templateId: true,
            styleProfileId: true,
          },
          orderBy: { createdAt: 'desc' },
        },
        content_templates: {
          select: {
            id: true,
            title: true,
            description: true,
            category: true,
            createdAt: true,
          },
        },
        style_profiles: {
          select: {
            id: true,
            name: true,
            description: true,
            category: true,
            createdAt: true,
          },
        },
        usage_stats: {
          select: {
            date: true,
            contentGenerated: true,
            tokensConsumed: true,
            generationTime: true,
            modelsUsed: true,
          },
          orderBy: { date: 'desc' },
          take: 90,
        },
        subscriptions: {
          select: {
            plan: true,
            status: true,
            startDate: true,
            endDate: true,
            monthlyTokenLimit: true,
            monthlyContentLimit: true,
          },
        },
      },
    });

    if (!dbUser) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    const totalContentGenerated = dbUser.usage_stats.reduce(
      (sum: number, stat: UsageStat) => sum + stat.contentGenerated,
      0
    );
    const totalTokensConsumed = dbUser.usage_stats.reduce(
      (sum: number, stat: UsageStat) => sum + stat.tokensConsumed,
      0
    );
    const totalGenerationTime = dbUser.usage_stats.reduce(
      (sum: number, stat: UsageStat) => sum + stat.generationTime,
      0
    );

    const userData = {
      profile: {
        id: dbUser.id,
        name: dbUser.name,
        email: dbUser.email,
        image: dbUser.image,
        bio: dbUser.bio,
        avatar: dbUser.avatar,
        language: dbUser.language,
        timezone: dbUser.timezone,
        emailVerified: dbUser.emailVerified?.toISOString() || null,
        createdAt: dbUser.createdAt.toISOString(),
        updatedAt: dbUser.updatedAt.toISOString(),
      },
      
      preferences: {
        notifications: {
          email: dbUser.emailNotifications,
          push: dbUser.pushNotifications,
          marketing: dbUser.marketingCommunications,
        },
        generation: {
          defaultMaxTokens: dbUser.defaultMaxTokens,
          defaultTemperature: dbUser.defaultTemperature,
          defaultModel: dbUser.defaultModel,
          defaultContentQuality: dbUser.defaultContentQuality,
        },
        system: {
          autoSave: dbUser.autoSave,
          backupFrequency: dbUser.backupFrequency,
        },
      },

      content: {
        generated: dbUser.generated_content.map((content: GeneratedContent) => ({
          id: content.id,
          title: content.title || 'Untitled',
          wordCount: content.wordCount,
          status: content.status,
          templateId: content.templateId,
          styleProfileId: content.styleProfileId,
          createdAt: content.createdAt.toISOString(),
          contentPreview: content.content.substring(0, 500) + '...',
        })),
        templates: dbUser.content_templates,
        styleProfiles: dbUser.style_profiles,
        statistics: {
          totalGenerated: dbUser.generated_content.length,
          totalTemplates: dbUser.content_templates.length,
          totalStyleProfiles: dbUser.style_profiles.length,
        },
      },

      usage: {
        summary: {
          totalContentGenerated,
          totalTokensConsumed,
          totalGenerationTimeMs: totalGenerationTime,
          averageWordsPerContent: 
            dbUser.generated_content.length > 0
              ? Math.round(
                  dbUser.generated_content.reduce(
                    (sum: number, c: GeneratedContent) => sum + c.wordCount,
                    0
                  ) / dbUser.generated_content.length
                )
              : 0,
        },
        dailyStats: dbUser.usage_stats.map((stat: UsageStat) => ({
          date: stat.date.toISOString().split('T')[0],
          contentGenerated: stat.contentGenerated,
          tokensConsumed: stat.tokensConsumed,
          generationTime: stat.generationTime,
          modelsUsed: stat.modelsUsed,
        })),
      },

      subscription: dbUser.subscriptions
        ? {
            plan: dbUser.subscriptions.plan,
            status: dbUser.subscriptions.status,
            startDate: dbUser.subscriptions.startDate.toISOString(),
            endDate: dbUser.subscriptions.endDate?.toISOString() || null,
            limits: {
              monthlyTokens: dbUser.subscriptions.monthlyTokenLimit,
              monthlyContent: dbUser.subscriptions.monthlyContentLimit,
            },
          }
        : null,

      export: {
        requestedAt: new Date().toISOString(),
        requestedBy: session.user.email,
        format: 'JSON',
        version: '1.0',
        gdprCompliant: true,
      },
    };

    const jsonData = JSON.stringify(userData, null, 2);
    const timestamp = new Date().toISOString().split('T')[0];
    const filename = `writerzroom-data-export-${timestamp}.json`;

    return new NextResponse(jsonData, {
      headers: {
        'Content-Type': 'application/json',
        'Content-Disposition': `attachment; filename="${filename}"`,
        'Content-Length': jsonData.length.toString(),
      },
    });
  } catch (error) {
    console.error('Data export error:', error);
    return NextResponse.json(
      { 
        error: 'Failed to export data',
        message: error instanceof Error ? error.message : 'Unknown error'
      }, 
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    const session = await auth();
    
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const dbUser = await prisma.user.findUnique({
      where: { email: session.user.email },
      select: {
        _count: {
          select: {
            generated_content: true,
            content_templates: true,
            style_profiles: true,
            usage_stats: true,
          },
        },
      },
    });

    if (!dbUser) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    return NextResponse.json({
      success: true,
      message: 'Export endpoint available',
      user: session.user.email,
      supportedFormats: ['JSON'],
      dataTypes: [
        'Profile information',
        'User preferences', 
        'Generated content',
        'Usage statistics',
        'Account settings',
        'Subscription details',
      ],
      statistics: {
        generatedContent: dbUser._count.generated_content,
        templates: dbUser._count.content_templates,
        styleProfiles: dbUser._count.style_profiles,
        usageRecords: dbUser._count.usage_stats,
      },
      note: 'Use POST method to download complete data export',
      gdprCompliant: true,
    });
  } catch (error) {
    console.error('Export info error:', error);
    return NextResponse.json(
      { 
        error: 'Failed to get export information',
        message: error instanceof Error ? error.message : 'Unknown error'
      }, 
      { status: 500 }
    );
  }
}