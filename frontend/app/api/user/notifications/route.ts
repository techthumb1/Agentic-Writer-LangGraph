// File: frontend/app/api/user/notifications/route.ts
// Create this file after making the directory with: mkdir -p app/api/user/notifications

import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/auth';

export async function PUT(request: NextRequest) {
  try {
    const session = await auth();
    
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const notificationSettings = await request.json();

    // Validate the notification settings structure
    const allowedSettings = ['email', 'push', 'marketing', 'security'];
    const validSettings: Record<string, boolean> = {};
    
    for (const [key, value] of Object.entries(notificationSettings)) {
      if (allowedSettings.includes(key) && typeof value === 'boolean') {
        validSettings[key] = value;
      }
    }

    // TODO: Save notification preferences to your database
    // Example with Prisma:
    // await prisma.userPreferences.upsert({
    //   where: { userId: session.user.id },
    //   update: { notifications: validSettings },
    //   create: { 
    //     userId: session.user.id, 
    //     notifications: validSettings 
    //   }
    // });

    return NextResponse.json({ 
      success: true, 
      message: 'Notification settings updated successfully',
      settings: validSettings
    });
  } catch (error) {
    console.error('Notification settings error:', error);
    return NextResponse.json(
      { error: 'Failed to update notification settings' }, 
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

    // TODO: Fetch notification preferences from your database
    // For now, return default settings
    const defaultSettings = {
      email: true,
      push: false,
      marketing: false,
      security: true
    };

    return NextResponse.json({
      success: true,
      settings: defaultSettings
    });
  } catch (error) {
    console.error('Notification settings fetch error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch notification settings' }, 
      { status: 500 }
    );
  }
}