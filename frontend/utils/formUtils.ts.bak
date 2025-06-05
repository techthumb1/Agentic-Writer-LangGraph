// utils/formUtils.ts
import { TemplateParameter } from '@/types/content';

export function getDefaultParameterValues(params: TemplateParameter[]): Record<string, string | number | boolean> {
  const result: Record<string, string | number | boolean> = {};
  params.forEach(param => {
    if (param.default !== undefined) {
      result[param.name] = param.default;
    } else if (param.type === 'number') {
      result[param.name] = 0;
    } else if (param.type === 'checkbox') {
      result[param.name] = false;
    } else {
      result[param.name] = '';
    }
  });
  return result;
}
