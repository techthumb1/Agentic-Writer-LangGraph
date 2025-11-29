
// types/theme.ts
export type BaseTheme = 'light' | 'dark' | 'system'
export type CustomTheme = 'default' | 'agentwrite-pro'

export interface ThemeConfig {
  base: BaseTheme
  custom: CustomTheme
}
