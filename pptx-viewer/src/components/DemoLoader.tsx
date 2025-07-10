"use client";

import { useState, useEffect } from "react";
import { PowerPointData } from "@/types/pptx";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface DemoLoaderProps {
  onDataLoad: (data: PowerPointData) => void;
}

export default function DemoLoader({ onDataLoad }: DemoLoaderProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSampleData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [shapesData, layoutsData, themeData, mediaData, propertiesData] = await Promise.all([
        fetch('/sample1-1_shapes.json').then(res => res.json()),
        fetch('/sample1-1_layouts.json').then(res => res.json()),
        fetch('/sample1-1_theme.json').then(res => res.json()),
        fetch('/sample1-1_media.json').then(res => res.json()),
        fetch('/sample1-1_properties.json').then(res => res.json()),
      ]);

      const powerPointData: PowerPointData = {
        shapes: shapesData,
        layouts: layoutsData,
        theme: themeData,
        media: mediaData,
        properties: propertiesData,
      };

      onDataLoad(powerPointData);
    } catch (err) {
      setError(`Error loading sample data: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Load Sample Data</CardTitle>
        <CardDescription>
          Load sample PowerPoint data to test the viewer
        </CardDescription>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="p-3 mb-4 bg-destructive/10 text-destructive rounded-md text-sm">
            {error}
          </div>
        )}
        
        <Button
          onClick={loadSampleData}
          disabled={loading}
          className="w-full"
        >
          {loading ? "Loading..." : "Load Sample PowerPoint"}
        </Button>
      </CardContent>
    </Card>
  );
}