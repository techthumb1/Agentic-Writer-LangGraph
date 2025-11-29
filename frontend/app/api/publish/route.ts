// app/api/publish/route.ts - Integrates with your existing enhanced_publisher.py
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

// Validation schema for publishing request
const publishSchema = z.object({
  title: z.string().min(1),
  content: z.string().min(1),
  platform: z.enum(['substack', 'medium', 'linkedin', 'twitter', 'wordpress', 'ghost']),
  options: z.object({
    immediate: z.boolean().optional(),
    scheduled: z.boolean().optional(),
    scheduledTime: z.string().optional(),
    tags: z.string().optional(),
    subtitle: z.string().optional(),
    publication: z.string().optional(),
    contentType: z.string().optional(),
    sendNewsletter: z.boolean().optional(),
  }).optional(),
  templateId: z.string().optional(),
  styleProfile: z.string().optional(),
});

// POST - Publish content to platform
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    console.log('Publishing request received:', { 
      platform: body.platform, 
      title: body.title,
      immediate: body.options?.immediate 
    });
    
    // Validate the request body
    const validatedData = publishSchema.parse(body);
    const { title, content, platform, options, templateId, styleProfile } = validatedData;
    
    // Call your existing Python backend enhanced_publisher
    const publisherResponse = await fetch('http://localhost:8000/publish', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        title,
        content,
        platform,
        template_id: templateId,
        style_profile: styleProfile,
        options: {
          ...options,
          scheduled_time: options?.scheduledTime,
          send_newsletter: options?.sendNewsletter,
          content_type: options?.contentType,
        }
      }),
    });

    if (!publisherResponse.ok) {
      const errorData = await publisherResponse.json();
      throw new Error(errorData.detail || 'Publishing failed');
    }

    const result = await publisherResponse.json();
    
    // Log successful publication
    console.log('Content published successfully:', {
      platform,
      publishedUrl: result.published_url,
      scheduledFor: options?.scheduledTime
    });

    return NextResponse.json({
      success: true,
      data: {
        platform,
        publishedUrl: result.published_url,
        publishedAt: result.published_at,
        scheduledFor: result.scheduled_for,
        status: result.status,
      },
      message: options?.scheduled 
        ? `Content scheduled for ${platform}` 
        : `Content published to ${platform}`
    }, { status: 201 });

  } catch (error) {
    console.error('Publishing error:', error);
    
    if (error instanceof z.ZodError) {
      return NextResponse.json({
        success: false,
        error: 'Invalid publishing request',
        details: error.errors
      }, { status: 400 });
    }

    return NextResponse.json({
      success: false,
      error: 'Publishing failed',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

// GET - Get publishing status and connected platforms
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('userId') || 'anonymous';
    
    // Check platform connections status via your backend
    const statusResponse = await fetch(`http://localhost:8000/publish/status?user_id=${userId}`);
    
    if (!statusResponse.ok) {
      throw new Error('Failed to get publishing status');
    }
    
    const statusData = await statusResponse.json();
    
    return NextResponse.json({
      success: true,
      platforms: statusData.platforms,
      scheduledPosts: statusData.scheduled_posts || [],
      publishingHistory: statusData.publishing_history || [],
    });

  } catch (error) {
    console.error('Status check error:', error);
    
    return NextResponse.json({
      success: false,
      error: 'Failed to get publishing status',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

// PUT - Update scheduled post
export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    const { postId, scheduledTime, options } = body;
    
    if (!postId) {
      return NextResponse.json({
        success: false,
        error: 'Post ID is required'
      }, { status: 400 });
    }
    
    // Update via your backend
    const updateResponse = await fetch(`http://localhost:8000/publish/schedule/${postId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        scheduled_time: scheduledTime,
        options
      }),
    });
    
    if (!updateResponse.ok) {
      const errorData = await updateResponse.json();
      throw new Error(errorData.detail || 'Update failed');
    }
    
    const result = await updateResponse.json();
    
    return NextResponse.json({
      success: true,
      data: result,
      message: 'Scheduled post updated successfully'
    });

  } catch (error) {
    console.error('Update error:', error);
    
    return NextResponse.json({
      success: false,
      error: 'Failed to update scheduled post',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

// DELETE - Cancel scheduled post
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const postId = searchParams.get('postId');
    
    if (!postId) {
      return NextResponse.json({
        success: false,
        error: 'Post ID is required'
      }, { status: 400 });
    }
    
    // Cancel via your backend
    const cancelResponse = await fetch(`http://localhost:8000/publish/schedule/${postId}`, {
      method: 'DELETE',
    });
    
    if (!cancelResponse.ok) {
      const errorData = await cancelResponse.json();
      throw new Error(errorData.detail || 'Cancellation failed');
    }
    
    return NextResponse.json({
      success: true,
      message: 'Scheduled post cancelled successfully'
    });

  } catch (error) {
    console.error('Cancellation error:', error);
    
    return NextResponse.json({
      success: false,
      error: 'Failed to cancel scheduled post',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}