// lib-api.ts

import { API_ENDPOINTS } from './constants';
import { APIResponse, StyleProfile } from '../types';

export async function fetchStyleProfiles(params: URLSearchParams): Promise<APIResponse<StyleProfile[]>> {
  const res = await fetch(`${API_ENDPOINTS.STYLE_PROFILES}?${params.toString()}`);
  if (!res.ok) throw new Error('Error fetching style profiles');
  return res.json();
}

export async function fetchTemplates(): Promise<APIResponse<unknown>> {
  const res = await fetch(API_ENDPOINTS.GET_TEMPLATES);
  if (!res.ok) throw new Error('Error fetching templates');
  return res.json();
}

// lib/api.ts
export const getUsage = () => fetch("/api/usage").then(r=>r.json())
// show “3 / 25 credits left” in nav
