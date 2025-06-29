// utils/formUtils.ts - Fixed version
export function getDefaultValues(parameters: Array<{
  name: string;
  default?: string | number | boolean | string[];
}>): Record<string, string | number | boolean> {
  const result: Record<string, string | number | boolean> = {};
  
  parameters.forEach((param) => {
    if (param.default !== undefined) {
      // Handle string array defaults by converting to comma-separated string
      if (Array.isArray(param.default)) {
        result[param.name] = param.default.join(', ');
      } else {
        result[param.name] = param.default;
      }
    }
  });
  
  return result;
}
