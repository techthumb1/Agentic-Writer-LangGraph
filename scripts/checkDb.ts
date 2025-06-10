import { PrismaClient } from "@prisma/client";
const db = new PrismaClient();
async function main() {
  console.log(await db.template.findMany({ take: 3 }));
  console.log(await db.styleProfile.findMany({ take: 3 }));
  await db.$disconnect();
}
main();
