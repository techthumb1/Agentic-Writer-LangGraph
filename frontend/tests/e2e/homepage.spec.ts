import { test, expect } from '@playwright/test'

test('homepage loads correctly', async ({ page }) => {
  await page.goto('/')
  
  // Check if the page title is present
  await expect(page).toHaveTitle(/Agentic Writer/)
  
  // Check if main navigation is present
  await expect(page.locator('nav')).toBeVisible()
})

test('content generation flow', async ({ page }) => {
  await page.goto('/')
  
  // Navigate to generation page
  await page.click('text=Generate')
  
  // Check if template selector is present
  await expect(page.locator('[data-testid="template-selector"]')).toBeVisible()
})
