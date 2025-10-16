// File: frontend/lib/email.ts
// Email utility functions for user notifications
// Used by: app/api/auth/register/route.ts

import { randomBytes } from 'crypto';
import nodemailer, { Transporter } from 'nodemailer';
import { prisma } from '@/lib/prisma.node';

// --- SMTP config normalization ------------------------------------------------
const SMTP_HOST = process.env.SMTP_HOST;
const SMTP_PORT = Number(process.env.SMTP_PORT || 587);
const SMTP_USER = process.env.SMTP_USER;
const SMTP_PASSWORD = process.env.SMTP_PASSWORD;
const SMTP_FROM = process.env.SMTP_FROM || 'noreply@writerzroom.com';
const NEXT_BASE_URL =
  process.env.NEXTAUTH_URL || process.env.APP_URL || 'http://localhost:3000';

// Decide secure automatically if not explicitly set: port 465 => secure
const SMTP_SECURE =
  process.env.SMTP_SECURE !== undefined
    ? process.env.SMTP_SECURE === 'true'
    : SMTP_PORT === 465;

// --- Create a singleton transporter (prevents multiple instances in dev) -----
let _transporter: Transporter | null = null;
function getTransporter(): Transporter {
  // Validate env vars at runtime, not module load
  if (!SMTP_HOST || !SMTP_USER || !SMTP_PASSWORD) {
    throw new Error(
      'Missing required SMTP env vars: SMTP_HOST, SMTP_USER, SMTP_PASSWORD'
    );
  }

  if (_transporter) return _transporter;
  _transporter = nodemailer.createTransport({
    host: SMTP_HOST,
    port: SMTP_PORT,
    secure: SMTP_SECURE,
    auth: { user: SMTP_USER, pass: SMTP_PASSWORD },
  });
  return _transporter;
}

// --- Token helpers ------------------------------------------------------------
function generateVerificationToken(): string {
  // 32 bytes -> 64 hex chars; cryptographically strong & URL-safe after hex
  return randomBytes(32).toString('hex');
}

// --- Public API ---------------------------------------------------------------
/**
 * Sends an email verification link and persists token + expiry on the user.
 * Assumes your User model has `verificationToken` and `tokenExpires` fields.
 */
export async function sendConfirmationEmail(email: string, name?: string) {
  const token = generateVerificationToken();
  const verificationUrl = `${NEXT_BASE_URL}/auth/verify?token=${token}`;

  // Persist token (24h)
  await prisma.user.update({
    where: { email },
    data: {
      verificationToken: token,
      tokenExpires: new Date(Date.now() + 24 * 60 * 60 * 1000),
    },
  });

  const html = `
  <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #6366f1;">Welcome to WriterzRoom${name ? `, ${escapeHtml(name)}` : ''}!</h2>
    <p>Please verify your email address by clicking the button below:</p>
    <div style="text-align: center; margin: 30px 0;">
      <a href="${verificationUrl}"
         style="background: linear-gradient(to right, #6366f1, #a855f7);
                color: #fff; padding: 12px 30px; text-decoration: none;
                border-radius: 8px; display: inline-block;">
        Verify Email Address
      </a>
    </div>
    <p>Or copy and paste this link into your browser:</p>
    <p style="color: #6366f1; word-break: break-all;">${verificationUrl}</p>
    <p style="color: #666; font-size: 12px; margin-top: 30px;">
      This link will expire in 24 hours. If you didn't create this account, please ignore this email.
    </p>
  </div>`.trim();

  const text = `Welcome to WriterzRoom${name ? `, ${name}` : ''}!\n\n` +
    `Please verify your email address:\n${verificationUrl}\n\n` +
    `This link expires in 24 hours. If you didn't create this account, ignore this message.`;

  const transporter = getTransporter();
  await transporter.sendMail({
    from: SMTP_FROM,
    to: email,
    subject: 'Verify your WriterzRoom account',
    text,
    html,
  });
}

// --- Minimal HTML escaping for interpolation safety --------------------------
function escapeHtml(s: string) {
  return s.replace(/[&<>"']/g, (ch) => {
    switch (ch) {
      case '&': return '&amp;';
      case '<': return '&lt;';
      case '>': return '&gt;';
      case '"': return '&quot;';
      case "'": return '&#39;';
      default: return ch;
    }
  });
}