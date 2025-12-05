// frontend/get_user_id.ts
// Retrieves user ID from the backend API instead of Prisma

export async function getUserId(token: string): Promise<string | null> {
  if (!process.env.NEXT_PUBLIC_API_BASE) {
    console.error("NEXT_PUBLIC_API_BASE not set");
    return null;
  }

  try {
    const res = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE}/api/auth/user-id`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        cache: "no-store",
      }
    );

    if (!res.ok) return null;

    const data = await res.json();
    return data.user_id ?? null;
  } catch (err) {
    console.error("Failed to fetch user ID:", err);
    return null;
  }
}
