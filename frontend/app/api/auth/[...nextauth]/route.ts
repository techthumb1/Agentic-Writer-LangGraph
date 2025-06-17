// File: frontend/app/api/auth/[...nextauth]/route.ts
// Create this new file in the app/api/auth/[...nextauth] directory

import { handlers } from '@/auth';

export const { GET, POST } = handlers;