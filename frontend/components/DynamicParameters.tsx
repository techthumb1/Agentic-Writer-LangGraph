// components/DynamicParameters.tsx
"use client";

import { useFormContext } from "react-hook-form";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";

type Param = {
  name: string;
  label?: string;
  type: "text" | "textarea" | "select" | "number" | "checkbox";
  options?: string[];
  default?: string | number | boolean;
  required?: boolean;
  placeholder?: string;
  description?: string;
};

type Props = {
  parameters: Param[];
};

export default function DynamicParameters({ parameters }: Props) {
  const { register, setValue, watch } = useFormContext();

  console.log('🔧 DynamicParameters received:', parameters);

  if (!parameters || parameters.length === 0) {
    return (
      <div className="text-sm text-muted-foreground">
        No additional parameters required for this template.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {parameters.map((param) => {
        const fieldValue = watch(`dynamic_parameters.${param.name}`);
        
        console.log(`📝 Rendering parameter: ${param.name} (${param.type})`, {
          label: param.label,
          options: param.options,
          default: param.default,
          value: fieldValue
        });

        if (param.type === "textarea") {
          return (
            <div key={param.name} className="space-y-2">
              <Label htmlFor={param.name} className="text-sm font-medium">
                {param.label || param.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                {param.required && <span className="text-red-500 ml-1">*</span>}
              </Label>
              
              {param.description && (
                <p className="text-xs text-muted-foreground">{param.description}</p>
              )}
              
              <Textarea
                id={param.name}
                {...register(`dynamic_parameters.${param.name}`, { 
                  required: param.required,
                  value: param.default || ''
                })}
                placeholder={param.placeholder || `Enter ${param.label || param.name}...`}
                className="w-full"
                rows={3}
              />
            </div>
          );
        }

        if (param.type === "select" && param.options) {
          return (
            <div key={param.name} className="space-y-2">
              <Label htmlFor={param.name} className="text-sm font-medium">
                {param.label || param.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                {param.required && <span className="text-red-500 ml-1">*</span>}
              </Label>
              
              {param.description && (
                <p className="text-xs text-muted-foreground">{param.description}</p>
              )}
              
              <Select
                value={fieldValue || param.default?.toString() || undefined}
                onValueChange={(value) => {
                  // Handle the special "none" case
                  const actualValue = value === "__none__" ? "" : value;
                  setValue(`dynamic_parameters.${param.name}`, actualValue);
                }}
              >
                <SelectTrigger>
                  <SelectValue 
                    placeholder={`Select ${param.label || param.name}...`}
                  />
                </SelectTrigger>
                <SelectContent>
                  {!param.required && (
                    <SelectItem value="__none__">
                      <span className="text-muted-foreground">None selected</span>
                    </SelectItem>
                  )}
                  {param.options.map((option) => (
                    <SelectItem key={option} value={option || `option-${option}`}>
                      {option.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          );
        }

        if (param.type === "number") {
          return (
            <div key={param.name} className="space-y-2">
              <Label htmlFor={param.name} className="text-sm font-medium">
                {param.label || param.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                {param.required && <span className="text-red-500 ml-1">*</span>}
              </Label>
              
              {param.description && (
                <p className="text-xs text-muted-foreground">{param.description}</p>
              )}
              
              <Input
                id={param.name}
                type="number"
                {...register(`dynamic_parameters.${param.name}`, { 
                  required: param.required,
                  valueAsNumber: true,
                  value: param.default || 0
                })}
                placeholder={param.placeholder || `Enter ${param.label || param.name}...`}
                className="w-full"
              />
            </div>
          );
        }

        if (param.type === "checkbox") {
          return (
            <div key={param.name} className="space-y-2">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id={param.name}
                  {...register(`dynamic_parameters.${param.name}`)}
                  defaultChecked={param.default as boolean || false}
                  onCheckedChange={(checked) => setValue(`dynamic_parameters.${param.name}`, checked)}
                />
                <Label htmlFor={param.name} className="text-sm font-medium">
                  {param.label || param.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  {param.required && <span className="text-red-500 ml-1">*</span>}
                </Label>
              </div>
              
              {param.description && (
                <p className="text-xs text-muted-foreground ml-6">{param.description}</p>
              )}
            </div>
          );
        }

        // Default to text input
        return (
          <div key={param.name} className="space-y-2">
            <Label htmlFor={param.name} className="text-sm font-medium">
              {param.label || param.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              {param.required && <span className="text-red-500 ml-1">*</span>}
            </Label>
            
            {param.description && (
              <p className="text-xs text-muted-foreground">{param.description}</p>
            )}
            
            <Input
              id={param.name}
              type="text"
              {...register(`dynamic_parameters.${param.name}`, { 
                required: param.required,
                value: param.default?.toString() || ''
              })}
              placeholder={param.placeholder || `Enter ${param.label || param.name}...`}
              className="w-full"
            />
          </div>
        );
      })}
    </div>
  );
}