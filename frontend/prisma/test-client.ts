import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
  const users = await prisma.user.findMany()
  console.log('✅ Prisma connected successfully. Users count:', users.length)
}

main()
  .catch((e) => {
    console.error('❌ Prisma test failed:', e)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })
