// File: frontend/app/api/auth/register/route.ts
// Handles user registration with email verification
// WHY: Provides credential-based signup flow with email confirmation
// RELEVANT FILES: lib/email.ts, lib/prisma.ts, auth.ts

import { NextRequest, NextResponse } from 'next/server';
import { hash } from 'bcryptjs';
import { prisma } from '@/lib/prisma';
import { sendConfirmationEmail } from '@/lib/email';

export async function POST(req: NextRequest) {
  try {
    const { name, email, password } = await req.json();

    // Validate input
    if (!name || !email || !password) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Validate password strength
    if (password.length < 8) {
      return NextResponse.json(
        { error: 'Password must be at least 8 characters' },
        { status: 400 }
      );
    }

    // Check if user exists
    const existingUser = await prisma.user.findUnique({
      where: { email }
    });

    if (existingUser) {
      return NextResponse.json(
        { error: 'Email already registered' },
        { status: 409 }
      );
    }

    // Hash password
    const hashedPassword = await hash(password, 10);

    // Create user
    const user = await prisma.user.create({
      data: {
        name,
        email,
        password: hashedPassword,
        emailVerified: null
      }
    });

    console.log('✅ User created:', user.email);

    // Send confirmation email with detailed error catching
    try {
      console.log('📧 Attempting to send verification email to:', user.email);
      await sendConfirmationEmail(user.email, user.name || 'User');
      console.log('✅ Verification email sent successfully');
    } catch (emailError) {
      console.error('❌ Email sending failed:', emailError);
      // Still return success since user was created
      // You can manually verify them or retry email later
      return NextResponse.json(
        { 
          success: true, 
          message: 'Account created but email verification failed. Please contact support.',
          emailError: emailError instanceof Error ? emailError.message : 'Unknown error'
        },
        { status: 201 }
      );
    }

    return NextResponse.json(
      { 
        success: true, 
        message: 'Registration successful. Please check your email to verify your account.' 
      },
      { status: 201 }
    );

  } catch (error) {
    console.error('❌ Registration error:', error);
    return NextResponse.json(
      { error: 'Registration failed. Please try again.' },
      { status: 500 }
    );
  }
}