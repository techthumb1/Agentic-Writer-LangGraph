// File: frontend/app/api/user/preferences/route.ts
// Create this file after making the directory with: mkdir -p app/api/user/preferences

import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/auth';

export async function PUT(request: NextRequest) {
  try {
    const session = await auth();
    
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const preferences = await request.json();

    // Validate the preferences structure
    const allowedPreferences = [
      'theme', 
      'compactMode', 
      'highContrast', 
      'language', 
      'timezone', 
      'dateFormat'
    ];
    
    const validPreferences: Record<string, string | boolean> = {};
    
    for (const [key, value] of Object.entries(preferences)) {
      if (allowedPreferences.includes(key)) {
        if (key === 'compactMode' || key === 'highContrast') {
          if (typeof value === 'boolean') {
            validPreferences[key] = value;
          }
        } else if (typeof value === 'string') {
          validPreferences[key] = value;
        }
      }
    }

    // Validate specific preference values
    const validThemes = ['light', 'dark', 'system'];
    const validLanguages = ['en-US', 'en-GB', 'es', 'fr', 'de'];
    const validTimezones = ['America/Los_Angeles', 'America/New_York', 'Europe/Berlin', 'UTC'];
    const validDateFormats = ['MM/DD/YYYY', 'DD/MM/YYYY', 'YYYY-MM-DD'];

    if (validPreferences.theme && !validThemes.includes(validPreferences.theme as string)) {
      delete validPreferences.theme;
    }
    if (validPreferences.language && !validLanguages.includes(validPreferences.language as string)) {
      delete validPreferences.language;
    }
    if (validPreferences.timezone && !validTimezones.includes(validPreferences.timezone as string)) {
      delete validPreferences.timezone;
    }
    if (validPreferences.dateFormat && !validDateFormats.includes(validPreferences.dateFormat as string)) {
      delete validPreferences.dateFormat;
    }

    // TODO: Save user preferences to your database
    // Example with Prisma:
    // await prisma.userPreferences.upsert({
    //   where: { userId: session.user.id },
    //   update: { preferences: validPreferences },
    //   create: { 
    //     userId: session.user.id, 
    //     preferences: validPreferences 
    //   }
    // });

    console.log('User preferences update:', { 
      userId: session.user.id, 
      preferences: validPreferences 
    });

    return NextResponse.json({ 
      success: true, 
      message: 'Preferences updated successfully',
      preferences: validPreferences
    });
  } catch (error) {
    console.error('Preferences error:', error);
    return NextResponse.json(
      { error: 'Failed to update preferences' }, 
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

    // TODO: Fetch user preferences from your database
    // For now, return default preferences
    const defaultPreferences = {
      theme: 'system',
      compactMode: false,
      highContrast: false,
      language: 'en-US',
      timezone: 'America/Los_Angeles',
      dateFormat: 'MM/DD/YYYY'
    };

    return NextResponse.json({
      success: true,
      preferences: defaultPreferences
    });
  } catch (error) {
    console.error('Preferences fetch error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch preferences' }, 
      { status: 500 }
    );
  }
}