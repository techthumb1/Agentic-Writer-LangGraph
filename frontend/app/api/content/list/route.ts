// frontend/app/api/content/list/route.ts

import { NextResponse } from 'next/server';
import { auth } from '@/auth';
import fs from 'fs/promises';
import path from 'path';

export async function GET() {
  // ✅ SECURITY: Require authentication
  const session = await auth();
  if (!session?.user?.id) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const contentDir = path.join(process.cwd(), '../generated_content');
    
    // Check if directory exists
    try {
      await fs.access(contentDir);
    } catch {
      return NextResponse.json({ 
        success: true, 
        content: [],
        message: 'No generated content found'
      });
    }
    
    // Read all week directories
    const weeks = await fs.readdir(contentDir);
    const allContent: unknown[] = [];
    
    for (const week of weeks) {
      if (!week.startsWith('week_')) continue;
      
      const weekPath = path.join(contentDir, week);
      const files = await fs.readdir(weekPath);
      
      // Read all JSON files in this week
      for (const file of files) {
        if (!file.endsWith('.json')) continue;
        
        const filePath = path.join(weekPath, file);
        const fileContent = await fs.readFile(filePath, 'utf-8');
        const contentData = JSON.parse(fileContent);
        
        // ✅ SECURITY: Filter by user_id
        if (contentData.user_id !== session.user.id) {
          continue; // Skip content belonging to other users
        }
        
        // Generate ID from filename (remove .json extension)
        const id = file.replace('.json', '');
        
        allContent.push({
          ...contentData,
          id,
          week,
          filename: file
        });
      }
    }
    
    // Sort by creation date, newest first
    allContent.sort((a, b) => {
      const dateA = new Date((a as { createdAt?: string }).createdAt || 0).getTime();
      const dateB = new Date((b as { createdAt?: string }).createdAt || 0).getTime();
      return dateB - dateA;
    });
    
    console.log(`✅ [CONTENT_LIST] Returned ${allContent.length} items for user ${session.user.id}`);
    
    return NextResponse.json({
      success: true,
      content: allContent,
      count: allContent.length
    });
    
  } catch (error) {
    console.error('❌ [CONTENT_LIST] Error:', error);
    throw error; // Fail fast
  }
}