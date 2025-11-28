// frontend/lib/email.ts
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);
const FROM_EMAIL = process.env.RESEND_FROM_EMAIL || 'onboarding@resend.dev';

export async function sendConfirmationEmail(
  email: string,
  token: string
): Promise<void> {
  if (!process.env.RESEND_API_KEY) {
    throw new Error('Missing RESEND_API_KEY environment variable');
  }

  const verifyUrl = `${process.env.NEXTAUTH_URL}/auth/verify?token=${token}`;

  await resend.emails.send({
    from: FROM_EMAIL,
    to: email,
    subject: 'Verify your WriterzRoom account',
    html: `
      <h2>Welcome to WriterzRoom!</h2>
      <p>Please verify your email address by clicking the link below:</p>
      <a href="${verifyUrl}">Verify Email</a>
      <p>Or copy this link: ${verifyUrl}</p>
      <p>This link expires in 24 hours.</p>
    `,
  });
}