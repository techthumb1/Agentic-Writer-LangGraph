// components/DynamicParameters.tsx
"use client";

import { useFormContext } from "react-hook-form";


type Param = {
  name: string;
  label?: string;
  type: "text" | "textarea" | "select" | "number" | "checkbox";
  options?: string[];
};

type Props = {
  parameters: Param[];
};

export default function DynamicParameters({ parameters }: Props) {
  const { register } = useFormContext();

  return (
    <div className="space-y-4">
      {parameters.map((param) => {
        if (param.type === "textarea") {
          return (
            <div key={param.name}>
              <label className="block text-sm font-medium mb-1" htmlFor={param.name}>
                {param.label ?? param.name}
              </label>
              <textarea
                id={param.name}
                {...register(param.name)}
                className="w-full border rounded-lg px-3 py-2 text-sm"
              />
            </div>
          );
        }

        if (param.type === "select" && param.options) {
          return (
            <div key={param.name}>
              <label className="block text-sm font-medium mb-1" htmlFor={param.name}>
                {param.label ?? param.name}
              </label>
              <select
                id={param.name}
                {...register(param.name)}
                className="w-full border rounded-lg px-3 py-2 text-sm"
              >
                <option value="">Select</option>
                {param.options.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            </div>
          );
        }

        return (
          <div key={param.name}>
            <label className="block text-sm font-medium mb-1" htmlFor={param.name}>
              {param.label ?? param.name}
            </label>
            <input
              id={param.name}
              {...register(param.name)}
              className="w-full border rounded-lg px-3 py-2 text-sm"
              type="text"
            />
          </div>
        );
      })}
    </div>
  );
}
