// frontend/app/api/auth/signout/route.ts
import { auth, signOut } from "@/auth";

export async function POST() {
  try {
    const session = await auth();
    
    if (!session) {
      return Response.json({ error: "Not authenticated" }, { status: 401 });
    }

    // Sign out the user
    await signOut({ redirectTo: "/" });
    
    return Response.json({ success: true });
  } catch (error) {
    console.error("Sign out error:", error);
    return Response.json({ error: "Sign out failed" }, { status: 500 });
  }
}