// File: frontend/app/api/generate-content/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma.node';
import { contentGenerationEngine } from '@/lib/content-generation-engine';
import { auth } from '@/auth';
interface Section {
  title: string;
  content: string;
  word_count: number; // Changed from wordCount to word_count
}

// Updated interface to match expected structure
interface GenerationResult {
  id: string;
  content: string;
  status: string;
  errors?: string[];
  metadata: {
    generation_id: string;
    template_used: string;
    style_profile_used: string;
    generated_at: Date;
    word_count: number; // Changed from wordCount to word_count
    completed_agents: string[];
    failed_agents: string[];
    processing_time_ms?: number;
    seo_metadata?: Record<string, unknown>;
    innovation_report?: Record<string, unknown>;
    sections?: Section[]; // Added sections property
  };
}

export async function POST(request: NextRequest) {
  const session = await auth();
  
  if (!session?.user?.id) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const body = await request.json();
    // ✅ FIXED: Accept both old and new field names
    const { 
      template, 
      templateId,
      styleProfile, 
      styleProfileId,
      topic,
      audience,
      dynamic_parameters,
      parameters, 
      userPreferences 
    } = body;

    // ✅ Support both naming conventions
    const finalTemplate = template || templateId;
    const finalStyleProfile = styleProfile || styleProfileId;

    // Validate required fields
    if (!finalTemplate || !finalStyleProfile) {
      return NextResponse.json(
        { error: 'Template and Style Profile are required' },
        { status: 400 }
      );
    }

    // ✅ FIXED: Pass topic and audience to generation engine
    const generationResult: GenerationResult = await contentGenerationEngine.generateContent({
      template: finalTemplate,
      style_profile: finalStyleProfile,
      topic: topic || dynamic_parameters?.topic || "Untitled",
      audience: audience || dynamic_parameters?.target_audience || "General audience",
      dynamic_parameters: dynamic_parameters || parameters || {},
    });

    if (generationResult.status === 'error') {
      return NextResponse.json(
        { 
          error: 'Content generation failed', 
          details: generationResult.errors 
        },
        { status: 500 }
      );
    }

    // Save to database using your exact Prisma schema
    try {
      const savedContent = await prisma.generatedContent.create({
        data: {
          id: generationResult.id,
          // Fixed property access to use sections from metadata
          title: generationResult.metadata.sections?.[0]?.title || 'Generated Content',
          content: generationResult.content,
          wordCount: generationResult.metadata.word_count, // Fixed property name
          sectionCount: generationResult.metadata.sections?.length || 0, // Fixed property access
          status: generationResult.status,
          errors: generationResult.errors || [],
          
          // Generation parameters and preferences as JSON
          parameters: parameters || {},
          preferences: userPreferences || {},
          
          // Model and performance data
          modelUsed: userPreferences?.model || 'gpt-4-turbo',
          tokensConsumed: Math.round(generationResult.metadata.word_count * 1.3), // Fixed property name
          generationTime: generationResult.metadata.processing_time_ms || 0, // Use actual timing
          
          // Agent workflow data as JSON - Fixed property access
          agentSteps: generationResult.metadata.sections?.map((section: Section) => ({
            agent: 'writer',
            action: 'generate_section',
            result: `Generated section: ${section.title}`,
            timestamp: new Date().toISOString(),
            wordCount: section.word_count // Fixed property name
          })) || [],
          
          // Foreign key relationships - Fixed parameter names
          templateId: template,
          styleProfileId: styleProfile,
          userId: session.user.id, // You'll need to get this from auth context
          
          // Versioning
          version: 1,
          
          // Publishing
          isPublished: false,
        }
      });

      // Also create content sections - Fixed property access
      if (generationResult.metadata.sections && generationResult.metadata.sections.length > 0) {
        await prisma.contentSection.createMany({
          data: generationResult.metadata.sections.map((section: Section, index: number) => ({
            title: section.title,
            content: section.content,
            wordCount: section.word_count, // Fixed property name
            order: index + 1,
            sectionType: index === 0 ? 'introduction' : 'body',
            generatedContentId: generationResult.id,
          }))
        });
      }

      // Return success response
      return NextResponse.json({
        id: generationResult.id,
        content: generationResult.content,
        metadata: {
          templateUsed: template, // Fixed parameter name
          styleProfileUsed: styleProfile, // Fixed parameter name
          generatedAt: savedContent.createdAt,
          wordCount: generationResult.metadata.word_count, // Fixed property name
          sections: generationResult.metadata.sections, // Fixed property access
          modelUsed: savedContent.modelUsed,
          tokensConsumed: savedContent.tokensConsumed,
          sectionCount: savedContent.sectionCount,
        },
        status: 'success',
        savedAt: savedContent.createdAt,
      });

    } catch (dbError) {
      console.error('Database save failed:', dbError);
      
      // Still return the generated content even if DB save fails
      return NextResponse.json({
        id: generationResult.id,
        content: generationResult.content,
        metadata: generationResult.metadata,
        status: 'success',
        warning: 'Content generated successfully but failed to save to database',
      });
    }

  } catch (error) {
    console.error('Content generation API error:', error);
    
    return NextResponse.json(
      { 
        error: 'Internal server error', 
        message: error instanceof Error ? error.message : 'Unknown error' 
      },
      { status: 500 }
    );
  }
}

// GET endpoint to retrieve templates and style profiles
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');

    switch (action) {
      case 'templates':
        const availableTemplates = contentGenerationEngine.getAvailableTemplates();
        return NextResponse.json({ templates: availableTemplates });

      case 'style-profiles':
        const availableStyleProfiles = contentGenerationEngine.getAvailableStyleProfiles();
        return NextResponse.json({ styleProfiles: availableStyleProfiles });

      case 'template-parameters':
        // Fixed parameter name
        const template = searchParams.get('template');
        if (!template) {
          return NextResponse.json(
            { error: 'Template required' },
            { status: 400 }
          );
        }
        
        // Get template from the engine
        const allTemplates = contentGenerationEngine.getAvailableTemplates();
        const templateObj = allTemplates.find(t => t.id === template);
        
        if (!templateObj) {
          return NextResponse.json(
            { error: 'Template not found' },
            { status: 404 }
          );
        }
        
        return NextResponse.json({ parameters: {} }); // Return empty for now

      case 'generation-history':
        const history = await prisma.generatedContent.findMany({
          orderBy: { createdAt: 'desc' },
          take: 50,
          select: {
            id: true,
            title: true,
            templateId: true,
            styleProfileId: true,
            status: true,
            createdAt: true,
            modelUsed: true,
            tokensConsumed: true,
          },
        });
        
        return NextResponse.json({ history });

      case 'content-sections':
        const contentId = searchParams.get('contentId');
        if (!contentId) {
          return NextResponse.json(
            { error: 'Content ID required' },
            { status: 400 }
          );
        }

        const sections = await prisma.contentSection.findMany({
          where: { generatedContentId: contentId },
          orderBy: { order: 'asc' },
        });

        return NextResponse.json({ sections });

      case 'usage-stats':
        const timeframe = searchParams.get('timeframe') || '7d';
        const days = timeframe === '30d' ? 30 : 7;
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - days);

        const usageStats = await prisma.generatedContent.groupBy({
          by: ['status'],
          where: {
            createdAt: {
              gte: startDate,
            },
          },
          _count: {
            id: true,
          },
        });

        return NextResponse.json({ 
          stats: usageStats,
          timeframe,
          generated_at: new Date().toISOString()
        });

      default:
        return NextResponse.json(
          { error: 'Invalid action parameter' },
          { status: 400 }
        );
    }

  } catch (error) {
    console.error('API GET error:', error);
    
    return NextResponse.json(
      { 
        error: 'Internal server error', 
        message: error instanceof Error ? error.message : 'Unknown error' 
      },
      { status: 500 }
    );
  }
}