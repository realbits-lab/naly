"use client";

import Image from "next/image";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Heart, Download } from "lucide-react";

interface Template {
  id: string;
  title: string;
  description: string;
  thumbnail_url: string;
  is_premium: boolean;
  category: string;
  download_count: number;
}

interface TemplateCardProps {
  template: Template;
}

export function TemplateCard({ template }: TemplateCardProps) {
  return (
    <Card className="group overflow-hidden">
      <div className="relative aspect-video overflow-hidden">
        <Image
          src={template.thumbnail_url}
          alt={template.title}
          fill
          className="object-cover transition-transform group-hover:scale-105"
        />
        {template.is_premium && (
          <Badge className="absolute top-2 right-2" variant="secondary">
            Premium
          </Badge>
        )}
        <Button
          size="sm"
          variant="ghost"
          className="absolute top-2 left-2 opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <Heart className="w-4 h-4" />
        </Button>
      </div>
      <CardContent className="p-4">
        <h3 className="font-medium line-clamp-1">{template.title}</h3>
        <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
          {template.description}
        </p>
        <div className="flex items-center justify-between mt-2">
          <Badge variant="outline">{template.category}</Badge>
          <span className="text-xs text-muted-foreground">
            {template.download_count} downloads
          </span>
        </div>
      </CardContent>
      <CardFooter className="p-4 pt-0">
        <Button className="w-full">
          <Download className="w-4 h-4 mr-2" />
          Download
        </Button>
      </CardFooter>
    </Card>
  );
}