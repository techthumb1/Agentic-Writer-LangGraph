// frontend/app/api/auth/[...nextauth]/route.ts
import { handlers } from "@/auth";

// `handlers` is the object returned by NextAuth in auth.ts:
// export const { handlers, auth, signIn, signOut } = NextAuth({ ... });
export const { GET, POST } = handlers;
