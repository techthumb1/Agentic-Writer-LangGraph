// File: frontend/app/api/user/profile/route.ts
// Create this file after making the directory with: mkdir -p app/api/user/profile

import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/auth';

export async function PUT(request: NextRequest) {
  try {
    const session = await auth();
    
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { name, email } = await request.json();

    // TODO: Update user in your database
    // For now, we'll just simulate success
    // In a real app, you'd update your database here:
    // await prisma.user.update({
    //   where: { id: session.user.id },
    //   data: { name, email }
    // });


    return NextResponse.json({ 
      success: true, 
      message: 'Profile updated successfully',
      user: { name, email }
    });
  } catch (error) {
    console.error('Profile update error:', error);
    return NextResponse.json(
      { error: 'Failed to update profile' }, 
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

    // Return current user profile
    return NextResponse.json({
      success: true,
      user: {
        id: session.user.id,
        name: session.user.name,
        email: session.user.email,
        image: session.user.image,
      }
    });
  } catch (error) {
    console.error('Profile fetch error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch profile' }, 
      { status: 500 }
    );
  }
}