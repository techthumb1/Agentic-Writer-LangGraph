/** Turn "future_of_llms" → "Future Of Llms" */
export const prettyName = (slug: string) =>
  slug
    .replace(/_/g, " ")
    .replace(/\b\w/g, c => c.toUpperCase());
