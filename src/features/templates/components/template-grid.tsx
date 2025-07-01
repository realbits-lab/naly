"use client";

import { TemplateCard } from "./template-card";

interface Template {
  id: string;
  title: string;
  description: string;
  thumbnail_url: string;
  is_premium: boolean;
  category: string;
  download_count: number;
}

interface TemplateGridProps {
  templates: Template[];
}

export function TemplateGrid({ templates }: TemplateGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {templates.map((template) => (
        <TemplateCard key={template.id} template={template} />
      ))}
    </div>
  );
}