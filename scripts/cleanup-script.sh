# Create the TypeScript cleanup script
cat > scripts/cleanup-console.ts << 'EOF'
#!/usr/bin/env node

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join } from 'path';

interface CleanupResult {
  filesProcessed: number;
  totalRemoved: number;
  errors: string[];
}

// Files from your ESLint output
const FILES_TO_CLEAN = [
  'app/api/content/[contentID]/route.ts',
  'app/api/generate-content.ts', 
  'app/api/generate/route.ts',
  'app/api/get-templates.ts',
  'app/api/style-profiles/route.ts',
  'app/api/user/export/route.ts',
  'app/api/user/notifications/route.ts',
  'app/api/user/preferences/route.ts',
  'app/api/user/privacy/route.ts',
  'app/api/user/profile/route.ts',
  'app/auth/signin/page.tsx',
  'app/auth/signout/route.ts',
  'app/content/[contentID]/page.tsx',
  'app/generate/page.tsx',
  'app/settings/page.tsx',
  'components/GeneratedContentDisplay.tsx',
  'components/NavigationClient.tsx',
  'components/error-boundary.tsx',
  'hooks/use-performance.ts',
  'lib/react-query-provider.tsx',
  'prisma/seed.ts',
  'utils/safeListDirs.ts'
];

function removeConsoleStatements(content: string): { cleaned: string; removed: number } {
  let removed = 0;
  
  // Split into lines for processing
  const lines = content.split('\n');
  const cleanedLines: string[] = [];
  
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    const trimmedLine = line.trim();
    
    // Skip empty lines and comments
    if (!trimmedLine || trimmedLine.startsWith('//') || trimmedLine.startsWith('*')) {
      cleanedLines.push(line);
      i++;
      continue;
    }
    
    // Check for console statements we want to remove
    if (shouldRemoveConsoleLine(trimmedLine)) {
      // Handle multi-line console statements
      const lineCount = skipConsoleStatement(lines, i);
      removed += lineCount;
      i += lineCount;
    } else {
      cleanedLines.push(line);
      i++;
    }
  }
  
  return {
    cleaned: cleanedLines.join('\n'),
    removed
  };
}

function shouldRemoveConsoleLine(line: string): boolean {
  // Remove these console types
  const removePatterns = [
    /console\.log\s*\(/,
    /console\.warn\s*\(/,
    /console\.info\s*\(/,
    /console\.debug\s*\(/,
    /console\.table\s*\(/,
    /console\.trace\s*\(/,
    /console\.time\s*\(/,
    /console\.timeEnd\s*\(/
  ];
  
  // Keep these console types
  const keepPatterns = [
    /console\.error\s*\(/,
    /console\.assert\s*\(/
  ];
  
  // First check if we should keep it
  if (keepPatterns.some(pattern => pattern.test(line))) {
    return false;
  }
  
  // Then check if we should remove it
  return removePatterns.some(pattern => pattern.test(line));
}

function skipConsoleStatement(lines: string[], startIndex: number): number {
  let lineCount = 1;
  let openParens = 0;
  let inString = false;
  let stringChar = '';
  
  // Count parentheses to handle multi-line console statements
  for (let j = startIndex; j < lines.length; j++) {
    const line = lines[j];
    
    for (let k = 0; k < line.length; k++) {
      const char = line[k];
      const prevChar = k > 0 ? line[k - 1] : '';
      
      // Handle string boundaries
      if ((char === '"' || char === "'" || char === '`') && prevChar !== '\\') {
        if (!inString) {
          inString = true;
          stringChar = char;
        } else if (char === stringChar) {
          inString = false;
          stringChar = '';
        }
      }
      
      // Count parentheses only outside strings
      if (!inString) {
        if (char === '(') openParens++;
        if (char === ')') openParens--;
      }
    }
    
    // If we've closed all parentheses and we're not in the first line, we're done
    if (j > startIndex && openParens <= 0) {
      break;
    }
    
    // If this isn't the first line, increment line count
    if (j > startIndex) {
      lineCount++;
    }
    
    // Safety check - don't go beyond 10 lines for a single console statement
    if (lineCount > 10) {
      break;
    }
  }
  
  return lineCount;
}

function cleanFile(filePath: string): { removed: number; error?: string } {
  try {
    if (!existsSync(filePath)) {
      return { removed: 0, error: `File not found: ${filePath}` };
    }
    
    const content = readFileSync(filePath, 'utf8');
    const { cleaned, removed } = removeConsoleStatements(content);
    
    // Only write if content changed
    if (cleaned !== content) {
      // Create backup
      writeFileSync(`${filePath}.backup`, content, 'utf8');
      writeFileSync(filePath, cleaned, 'utf8');
    }
    
    return { removed };
  } catch (error) {
    return { 
      removed: 0, 
      error: error instanceof Error ? error.message : 'Unknown error' 
    };
  }
}

function main(): void {
  const frontendPath = './frontend';
  
  console.log('🧹 Starting robust console cleanup...\n');
  
  if (!existsSync(frontendPath)) {
    console.error(`❌ Frontend directory not found: ${frontendPath}`);
    process.exit(1);
  }
  
  const result: CleanupResult = {
    filesProcessed: 0,
    totalRemoved: 0,
    errors: []
  };
  
  FILES_TO_CLEAN.forEach(relativePath => {
    const fullPath = join(frontendPath, relativePath);
    console.log(`Processing: ${relativePath}`);
    
    const { removed, error } = cleanFile(fullPath);
    
    if (error) {
      result.errors.push(`${relativePath}: ${error}`);
      console.log(`  ❌ Error: ${error}`);
    } else {
      result.filesProcessed++;
      result.totalRemoved += removed;
      
      if (removed > 0) {
        console.log(`  ✅ Removed ${removed} console statements`);
      } else {
        console.log(`  ✨ No console statements to remove`);
      }
    }
    
    console.log('');
  });
  
  // Summary
  console.log('📊 Cleanup Summary:');
  console.log(`  Files processed: ${result.filesProcessed}`);
  console.log(`  Console statements removed: ${result.totalRemoved}`);
  
  if (result.errors.length > 0) {
    console.log(`  Errors: ${result.errors.length}`);
    result.errors.forEach(error => console.log(`    - ${error}`));
  }
  
  console.log('\n🎉 Console cleanup complete!');
  console.log('\n💡 Next steps:');
  console.log('  1. Run: cd frontend && npm run lint');
  console.log('  2. Test your application');
  console.log('  3. Commit changes if everything works');
}

main();
EOF

# Run the TypeScript cleanup script
npx tsx scripts/cleanup-console.ts