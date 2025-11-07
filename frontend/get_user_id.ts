import { PrismaClient } from '@prisma/client';

async function main() {
  const prisma = new PrismaClient();
  const user = await prisma.user.findFirst();
  console.log('SERVICE_USER_ID =', user?.id || 'No users found');
  await prisma.$disconnect();
}

main();
