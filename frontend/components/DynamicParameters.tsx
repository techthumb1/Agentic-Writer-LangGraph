// frontend/components/DynamicParameters.tsx
// Fixed: Remove conflicting register() from Select component
"use client";
import React from "react";
import { useFormContext } from "react-hook-form";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Info, Star, Zap, Target, Palette } from "lucide-react";

type EnhancedParam = {
  name: string;
  label?: string;
  type: "text" | "textarea" | "select" | "number" | "checkbox" | "multiselect" | "range" | "date";
  options?: Record<string, string> | string[];
  default?: string | number | boolean;
  required?: boolean;
  placeholder?: string;
  description?: string;
  commonly_used?: boolean;
  affects_approach?: boolean;
  affects_scope?: boolean;
  affects_tone?: boolean;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
    message?: string;
  };
};

type Props = {
  parameters: EnhancedParam[];
};

function formatParameterOptions(options: Record<string, string> | string[] | undefined): string[] {
  if (!options) return [];
  if (Array.isArray(options)) return options;
  return Object.keys(options);
}

function getOptionDisplayText(option: string, options: Record<string, string> | string[] | undefined): string {
  if (!options) return option;
  if (Array.isArray(options)) {
    return option.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  }
  return options[option] || option.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function getParameterBadge(param: EnhancedParam) {
  if (param.commonly_used) {
    return (
      <Badge variant="default" className="text-xs bg-blue-100 text-blue-800">
        <Star className="h-3 w-3 mr-1" />
        Popular
      </Badge>
    );
  }
  if (param.affects_approach) {
    return (
      <Badge variant="secondary" className="text-xs bg-purple-100 text-purple-800">
        <Zap className="h-3 w-3 mr-1" />
        Key
      </Badge>
    );
  }
  if (param.affects_scope) {
    return (
      <Badge variant="outline" className="text-xs bg-green-100 text-green-800">
        <Target className="h-3 w-3 mr-1" />
        Scope
      </Badge>
    );
  }
  if (param.affects_tone) {
    return (
      <Badge variant="outline" className="text-xs bg-orange-100 text-orange-800">
        <Palette className="h-3 w-3 mr-1" />
        Tone
      </Badge>
    );
  }
  return null;
}

export default function DynamicParameters({ parameters }: Props) {
  const { register, setValue, watch } = useFormContext();

  React.useEffect(() => {
    parameters.forEach(param => {
      const fieldValue = watch(`dynamic_parameters.${param.name}`);
      if (fieldValue === undefined && param.default !== undefined) {
        setValue(`dynamic_parameters.${param.name}`, param.default, { shouldValidate: false });
      }
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [parameters]); // Only re-run when parameters change

  if (!parameters || parameters.length === 0) {
    return (
      <div className="text-sm text-muted-foreground bg-gray-50 p-4 rounded-lg border-2 border-dashed border-gray-200">
        <div className="flex items-center gap-2">
          <Info className="h-4 w-4 text-gray-400" />
          <span>No additional parameters required for this template.</span>
        </div>
      </div>
    );
  }

  const importantParams = parameters.filter(p => p.commonly_used || p.affects_approach);
  const otherParams = parameters.filter(p => !p.commonly_used && !p.affects_approach);

  const renderParameter = (param: EnhancedParam) => {
    const fieldValue = watch(`dynamic_parameters.${param.name}`);
    const badge = getParameterBadge(param);

    const labelElement = (
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Label htmlFor={param.name} className="text-sm font-medium">
            {param.label || param.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            {param.required && <span className="text-red-500 ml-1">*</span>}
          </Label>
          {badge}
        </div>
      </div>
    );

    const descriptionElement = param.description && (
      <p className="text-xs text-muted-foreground mb-2">{param.description}</p>
    );

    if (param.type === "textarea") {
      return (
        <div key={param.name} className="space-y-2">
          {labelElement}
          {descriptionElement}
          <Textarea
            id={param.name}
            {...register(`dynamic_parameters.${param.name}`, { required: param.required })}
            placeholder={param.placeholder || `Enter ${param.label || param.name}...`}
            className="w-full"
            rows={3}
          />
        </div>
      );
    }

    if (param.type === "select") {
      const optionsList = formatParameterOptions(param.options);
      return (
        <div key={param.name} className="space-y-2">
          {labelElement}
          {descriptionElement}
          <Select
            value={fieldValue?.toString() || param.default?.toString() || ""}
            onValueChange={(value) => {
              const actualValue = value === "__none__" ? "" : value;
              setValue(`dynamic_parameters.${param.name}`, actualValue);
            }}
          >
            <SelectTrigger>
              <SelectValue placeholder={`Select ${param.label || param.name}...`} />
            </SelectTrigger>
            <SelectContent>
              {!param.required && (
                <SelectItem value="__none__">
                  <span className="text-muted-foreground">None selected</span>
                </SelectItem>
              )}
              {optionsList.map((option) => (
                <SelectItem key={option} value={option || `option-${option}`}>
                  {getOptionDisplayText(option, param.options)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      );
    }

    if (param.type === "number" || param.type === "range") {
      return (
        <div key={param.name} className="space-y-2">
          {labelElement}
          {descriptionElement}
          <Input
            id={param.name}
            type="number"
            {...register(`dynamic_parameters.${param.name}`, { 
              required: param.required, 
              valueAsNumber: true 
            })}
            placeholder={param.placeholder || `Enter ${param.label || param.name}...`}
            className="w-full"
            min={param.validation?.min}
            max={param.validation?.max}
          />
          {param.validation && (param.validation.min || param.validation.max) && (
            <div className="text-xs text-muted-foreground">
              Range: {param.validation.min || 'any'} - {param.validation.max || 'any'}
            </div>
          )}
        </div>
      );
    }

    if (param.type === "checkbox") {
      return (
        <div key={param.name} className="space-y-2">
          <div className="flex items-center space-x-3">
            <Checkbox
              id={param.name}
              checked={fieldValue !== undefined ? fieldValue : (param.default as boolean || false)}
              onCheckedChange={(checked) => setValue(`dynamic_parameters.${param.name}`, checked)}
            />
            <div className="flex items-center gap-2">
              <Label htmlFor={param.name} className="text-sm font-medium">
                {param.label || param.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                {param.required && <span className="text-red-500 ml-1">*</span>}
              </Label>
              {badge}
            </div>
          </div>
          {param.description && (
            <p className="text-xs text-muted-foreground ml-6">{param.description}</p>
          )}
        </div>
      );
    }

    if (param.type === "date") {
      return (
        <div key={param.name} className="space-y-2">
          {labelElement}
          {descriptionElement}
          <Input
            id={param.name}
            type="date"
            {...register(`dynamic_parameters.${param.name}`, { required: param.required })}
            className="w-full"
          />
        </div>
      );
    }

    // Default: text input - NO value prop, NO onChange prop
    return (
      <div key={param.name} className="space-y-2">
        {labelElement}
        {descriptionElement}
        <Input
          id={param.name}
          type="text"
          {...register(`dynamic_parameters.${param.name}`, { required: param.required })}
          placeholder={param.placeholder || `Enter ${param.label || param.name}...`}
          className="w-full"
        />
        {param.validation?.message && (
          <div className="text-xs text-muted-foreground">
            {param.validation.message}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {importantParams.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-gray-200">
            <Star className="h-4 w-4 text-blue-500" />
            <h4 className="text-sm font-semibold text-gray-700">Key Parameters</h4>
            <Badge variant="outline" className="text-xs">{importantParams.length}</Badge>
          </div>
          <div className="grid grid-cols-1 gap-4">
            {importantParams.map(renderParameter)}
          </div>
        </div>
      )}

      {otherParams.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-gray-200">
            <Info className="h-4 w-4 text-gray-400" />
            <h4 className="text-sm font-semibold text-gray-700">Additional Parameters</h4>
            <Badge variant="outline" className="text-xs">{otherParams.length}</Badge>
          </div>
          <div className="grid grid-cols-1 gap-4">
            {otherParams.map(renderParameter)}
          </div>
        </div>
      )}

      <div className="mt-6 p-3 bg-gray-50 rounded-lg border">
        <div className="text-xs text-gray-600">
          <strong>Parameter Summary:</strong> {parameters.length} total parameters 
          ({importantParams.length} key, {otherParams.length} additional)
        </div>
      </div>
    </div>
  );
}