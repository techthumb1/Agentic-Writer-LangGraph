// File: frontend/app/api/user/privacy/route.ts
// Create this file after making the directory with: mkdir -p app/api/user/privacy

import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/auth';

export async function PUT(request: NextRequest) {
  try {
    const session = await auth();
    
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const privacySettings = await request.json();

    // Validate the privacy settings structure
    const allowedSettings = ['analytics', 'profileVisible', 'dataSharing'];
    const validSettings: Record<string, boolean> = {};
    
    for (const [key, value] of Object.entries(privacySettings)) {
      if (allowedSettings.includes(key) && typeof value === 'boolean') {
        validSettings[key] = value;
      }
    }

    // TODO: Save privacy preferences to your database
    // Example with Prisma:
    // await prisma.userPreferences.upsert({
    //   where: { userId: session.user.id },
    //   update: { privacy: validSettings },
    //   create: { 
    //     userId: session.user.id, 
    //     privacy: validSettings 
    //   }
    // });

    console.log('Privacy settings update:', { 
      userId: session.user.id, 
      settings: validSettings 
    });

    return NextResponse.json({ 
      success: true, 
      message: 'Privacy settings updated successfully',
      settings: validSettings
    });
  } catch (error) {
    console.error('Privacy settings error:', error);
    return NextResponse.json(
      { error: 'Failed to update privacy settings' }, 
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

    // TODO: Fetch privacy preferences from your database
    // For now, return default settings
    const defaultSettings = {
      analytics: true,
      profileVisible: false,
      dataSharing: false
    };

    return NextResponse.json({
      success: true,
      settings: defaultSettings
    });
  } catch (error) {
    console.error('Privacy settings fetch error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch privacy settings' }, 
      { status: 500 }
    );
  }
}