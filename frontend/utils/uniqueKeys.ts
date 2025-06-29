// ───────────────────────────────────────────────
// utils/uniqueKeys.ts - Enterprise Key Management System
// ───────────────────────────────────────────────

// Import only when needed for type enforcement
// import type { ContentTemplate, StyleProfile, GeneratedContent, Section, TemplateParameter } from '@/types/content';

// ═══════════════════════════════════════════════
// Core Type Definitions
// ═══════════════════════════════════════════════

interface KeyableItem {
  id: string;
  [key: string]: unknown;
}

interface TemplateItem extends KeyableItem {
  title?: string;
  name?: string;
}

interface ProfileItem extends KeyableItem {
  name: string;
  title?: string;
}

interface ContentItem extends KeyableItem {
  title?: string;
}

interface SectionItem extends KeyableItem {
  title: string;
  order?: number;
}

interface ParameterItem {
  name: string;
  label?: string;
  type: string;
}

interface TagItem {
  value?: string;
  label?: string;
}

type KeyGenerationOptions = {
  includeTimestamp?: boolean;
  includeRandomSuffix?: boolean;
  maxLength?: number;
  sanitize?: boolean;
};

// ═══════════════════════════════════════════════
// Advanced Key Generation Engine
// ═══════════════════════════════════════════════

export class UniqueKeyGenerator {
  private readonly keyRegistry = new Map<string, number>();
  private readonly timestampCache = new Map<string, number>();
  
  /**
   * Generate a cryptographically unique key with enterprise-grade collision prevention
   */
  public generateUniqueKey(
    baseKey: string, 
    prefix?: string, 
    index?: number,
    options: KeyGenerationOptions = {}
  ): string {
    const {
      includeTimestamp = true,
      includeRandomSuffix = true,
      maxLength = 100,
      sanitize = true,
    } = options;

    let processedKey = sanitize ? this.sanitizeKey(baseKey) : baseKey;
    
    if (prefix) {
      processedKey = `${this.sanitizeKey(prefix)}-${processedKey}`;
    }
    
    if (index !== undefined) {
      processedKey = `${processedKey}-${index}`;
    }
    
    // Add collision prevention
    const collisionCount = this.keyRegistry.get(processedKey) || 0;
    if (collisionCount > 0) {
      processedKey = `${processedKey}-${collisionCount}`;
    }
    this.keyRegistry.set(baseKey, collisionCount + 1);
    
    if (includeTimestamp) {
      const timestamp = this.getOptimizedTimestamp(processedKey);
      processedKey = `${processedKey}-${timestamp}`;
    }
    
    if (includeRandomSuffix) {
      const randomSuffix = this.generateCryptoSafeRandomId(6);
      processedKey = `${processedKey}-${randomSuffix}`;
    }
    
    return this.truncateKey(processedKey, maxLength);
  }

  /**
   * Create enterprise-grade unique keys for collections with deduplication
   */
  public createUniqueKeysForCollection<T extends KeyableItem>(
    items: T[], 
    keyField: keyof T = 'id', 
    prefix?: string,
    options: KeyGenerationOptions = {}
  ): Array<{ item: T; key: string; originalIndex: number }> {
    const seenKeys = new Set<string>();
    const processedItems: Array<{ item: T; key: string; originalIndex: number }> = [];
    
    items.forEach((item, index) => {
      const baseKey = String(item[keyField] || `fallback-${index}`);
      let finalKey = this.generateUniqueKey(baseKey, prefix, index, options);
      
      // Ensure absolute uniqueness within this collection
      let uniqueCounter = 1;
      const originalFinalKey = finalKey;
      
      while (seenKeys.has(finalKey)) {
        finalKey = `${originalFinalKey}-unique-${uniqueCounter}`;
        uniqueCounter++;
      }
      
      seenKeys.add(finalKey);
      processedItems.push({
        item,
        key: finalKey,
        originalIndex: index,
      });
    });
    
    return processedItems;
  }

  /**
   * Advanced sanitization for enterprise key safety
   */
  private sanitizeKey(input: string): string {
    return input
      .toLowerCase()
      .replace(/[^a-z0-9]/g, '_')
      .replace(/_{2,}/g, '_')
      .replace(/^_+|_+$/g, '')
      .substring(0, 50);
  }

  /**
   * Generate cryptographically safe random identifier
   */
  private generateCryptoSafeRandomId(length: number): string {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    
    // Use crypto API if available, fallback to Math.random
    if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
      const array = new Uint8Array(length);
      crypto.getRandomValues(array);
      for (let i = 0; i < length; i++) {
        result += chars[array[i] % chars.length];
      }
    } else {
      for (let i = 0; i < length; i++) {
        result += chars[Math.floor(Math.random() * chars.length)];
      }
    }
    
    return result;
  }

  /**
   * Optimized timestamp generation with caching
   */
  private getOptimizedTimestamp(key: string): number {
    const cached = this.timestampCache.get(key);
    if (cached && (Date.now() - cached) < 1000) {
      return cached;
    }
    
    const timestamp = Date.now();
    this.timestampCache.set(key, timestamp);
    return timestamp;
  }

  /**
   * Intelligent key truncation maintaining readability
   */
  private truncateKey(key: string, maxLength: number): string {
    if (key.length <= maxLength) return key;
    
    const parts = key.split('-');
    if (parts.length <= 1) {
      return key.substring(0, maxLength);
    }
    
    // Keep the most important parts (prefix, base, suffix)
    const prefix = parts[0];
    const suffix = parts[parts.length - 1];
    const remainingLength = maxLength - prefix.length - suffix.length - 2;
    
    if (remainingLength > 0) {
      const middle = parts.slice(1, -1).join('-');
      const truncatedMiddle = middle.substring(0, remainingLength);
      return `${prefix}-${truncatedMiddle}-${suffix}`;
    }
    
    return key.substring(0, maxLength);
  }

  /**
   * Clear internal caches for memory management
   */
  public clearCaches(): void {
    this.keyRegistry.clear();
    this.timestampCache.clear();
  }
}

// ═══════════════════════════════════════════════
// Enhanced Type-Safe Key Generators with Schema Integration
// ═══════════════════════════════════════════════

export class SpecializedKeyGenerators {
  private static keyGenerator = new UniqueKeyGenerator();

  /**
   * Generate keys for ContentTemplate entities with full type safety
   */
  public static template(template: TemplateItem, index: number): string {
    const baseKey = template.id || template.title || template.name || `template-${index}`;
    return this.keyGenerator.generateUniqueKey(baseKey, 'template', index);
  }

  /**
   * Generate keys for StyleProfile entities with validation
   */
  public static styleProfile(profile: ProfileItem, index: number): string {
    const baseKey = profile.id || profile.name || profile.title || `profile-${index}`;
    return this.keyGenerator.generateUniqueKey(baseKey, 'profile', index);
  }

  /**
   * Generate keys for GeneratedContent with metadata preservation
   */
  public static content(content: ContentItem, index: number): string {
    const baseKey = content.id || content.title || `content-${index}`;
    return this.keyGenerator.generateUniqueKey(baseKey, 'content', index);
  }

  /**
   * Generate keys for Section entities with ordering context
   */
  public static section(section: SectionItem, index: number): string {
    const baseKey = section.id || `${section.title}-${section.order || index}`;
    return this.keyGenerator.generateUniqueKey(baseKey, 'section', index);
  }

  /**
   * Generate keys for TemplateParameter with type awareness
   */
  public static parameter(parameter: ParameterItem, index: number): string {
    const baseKey = `${parameter.name}-${parameter.type}`;
    return this.keyGenerator.generateUniqueKey(baseKey, 'param', index);
  }

  public static tag(tag: string | TagItem, index: number): string {
    const baseKey = typeof tag === 'string' ? tag : (tag.value || tag.label || 'tag');
    return this.keyGenerator.generateUniqueKey(baseKey, 'tag', index);
  }

  public static option(option: string | { value: string; label?: string }, index: number): string {
    const baseKey = typeof option === 'string' ? option : option.value;
    return this.keyGenerator.generateUniqueKey(baseKey, 'option', index);
  }

  public static navigation(item: { id?: string; name?: string; path?: string }, index: number): string {
    const baseKey = item.id || item.name || item.path || `nav-${index}`;
    return this.keyGenerator.generateUniqueKey(baseKey, 'nav', index);
  }

  public static form(field: { name: string; type?: string }, index: number): string {
    const baseKey = `${field.name}-${field.type || 'field'}`;
    return this.keyGenerator.generateUniqueKey(baseKey, 'form', index);
  }

  /**
   * Enterprise-level generator for queue items with priority awareness
   */
  public static queueItem(item: { id: string; priority?: number; status?: string }, index: number): string {
    const baseKey = `${item.id}-${item.status || 'pending'}-${item.priority || 0}`;
    return this.keyGenerator.generateUniqueKey(baseKey, 'queue', index);
  }

  /**
   * Generator for export operations with format context
   */
  public static exportItem(item: { id: string; exportType?: string; format?: string }, index: number): string {
    const baseKey = `${item.id}-${item.exportType || 'unknown'}-${item.format || 'json'}`;
    return this.keyGenerator.generateUniqueKey(baseKey, 'export', index);
  }

  /**
   * Generator for analytics and usage tracking entities
   */
  public static analyticsItem(item: { id: string; date?: Date | string; type?: string }, index: number): string {
    const dateStr = item.date ? new Date(item.date).toISOString().split('T')[0] : 'no-date';
    const baseKey = `${item.id}-${item.type || 'metric'}-${dateStr}`;
    return this.keyGenerator.generateUniqueKey(baseKey, 'analytics', index);
  }
}

// ═══════════════════════════════════════════════
// React Hook Integration
// ═══════════════════════════════════════════════

import { useMemo, useCallback } from 'react';

export function useUniqueKeys<T extends KeyableItem>(
  items: T[], 
  prefix: string,
  keyField: keyof T = 'id'
): Array<{ item: T; key: string; index: number }> {
  const keyGenerator = useMemo(() => new UniqueKeyGenerator(), []);
  
  return useMemo(() => {
    return keyGenerator.createUniqueKeysForCollection(items, keyField, prefix)
      .map(({ item, key, originalIndex }) => ({
        item,
        key,
        index: originalIndex,
      }));
  }, [items, prefix, keyField, keyGenerator]);
}

export function useKeyGenerator(): {
  generateKey: (baseKey: string, prefix?: string, index?: number) => string;
  generateCollectionKeys: <T extends KeyableItem>(
    items: T[], 
    prefix: string, 
    keyField?: keyof T
  ) => Array<{ item: T; key: string; originalIndex: number }>;
  clearCaches: () => void;
} {
  const keyGenerator = useMemo(() => new UniqueKeyGenerator(), []);
  
  const generateKey = useCallback((
    baseKey: string, 
    prefix?: string, 
    index?: number
  ) => {
    return keyGenerator.generateUniqueKey(baseKey, prefix, index);
  }, [keyGenerator]);

  const generateCollectionKeys = useCallback(<T extends KeyableItem>(
    items: T[], 
    prefix: string, 
    keyField: keyof T = 'id'
  ) => {
    return keyGenerator.createUniqueKeysForCollection(items, keyField, prefix);
  }, [keyGenerator]);

  const clearCaches = useCallback(() => {
    keyGenerator.clearCaches();
  }, [keyGenerator]);

  return {
    generateKey,
    generateCollectionKeys,
    clearCaches,
  };
}

// ═══════════════════════════════════════════════
// Singleton Instance Export
// ═══════════════════════════════════════════════

export const KeyGenerators = {
  template: SpecializedKeyGenerators.template,
  styleProfile: SpecializedKeyGenerators.styleProfile,
  content: SpecializedKeyGenerators.content,
  section: SpecializedKeyGenerators.section,
  parameter: SpecializedKeyGenerators.parameter,
  tag: SpecializedKeyGenerators.tag,
  option: SpecializedKeyGenerators.option,
  navigation: SpecializedKeyGenerators.navigation,
  form: SpecializedKeyGenerators.form,
  queue: SpecializedKeyGenerators.queueItem,
  export: SpecializedKeyGenerators.exportItem,
  analytics: SpecializedKeyGenerators.analyticsItem,
} as const;

export const globalKeyGenerator = new UniqueKeyGenerator();

// ═══════════════════════════════════════════════
// Utility Functions
// ═══════════════════════════════════════════════

export function deduplicateByKey<T extends KeyableItem>(
  items: T[], 
  keyField: keyof T = 'id'
): T[] {
  const seen = new Set<string>();
  return items.filter(item => {
    const key = String(item[keyField]);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

export function validateUniqueKeys(keys: string[]): {
  isValid: boolean;
  duplicates: string[];
  totalKeys: number;
  uniqueKeys: number;
} {
  const seen = new Set<string>();
  const duplicates: string[] = [];
  
  keys.forEach(key => {
    if (seen.has(key)) {
      duplicates.push(key);
    } else {
      seen.add(key);
    }
  });
  
  return {
    isValid: duplicates.length === 0,
    duplicates,
    totalKeys: keys.length,
    uniqueKeys: seen.size,
  };
}