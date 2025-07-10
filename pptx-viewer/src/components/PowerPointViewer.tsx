"use client";

import { useState, useEffect } from "react";
import { PowerPointData } from "@/types/pptx";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import SlideRenderer from "./SlideRenderer";

export default function PowerPointViewer() {
  const [data, setData] = useState<PowerPointData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [shapesData, layoutsData, themeData, mediaData, propertiesData] = await Promise.all([
          fetch('/sample1_shapes.json').then(res => res.json()),
          fetch('/sample1_layouts.json').then(res => res.json()),
          fetch('/sample1_theme.json').then(res => res.json()),
          fetch('/sample1_media.json').then(res => res.json()),
          fetch('/sample1_properties.json').then(res => res.json()),
        ]);

        const powerPointData: PowerPointData = {
          shapes: shapesData,
          layouts: layoutsData,
          theme: themeData,
          media: mediaData,
          properties: propertiesData,
        };

        setData(powerPointData);
      } catch (err) {
        setError(`Error loading data: ${err instanceof Error ? err.message : String(err)}`);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-2">PowerPoint JSON Viewer</h1>
          <p className="text-muted-foreground">Loading presentation data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-2">PowerPoint JSON Viewer</h1>
          <div className="p-3 mb-4 bg-destructive/10 text-destructive rounded-md text-sm max-w-md mx-auto">
            {error}
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-2">PowerPoint JSON Viewer</h1>
          <p className="text-muted-foreground">No data available</p>
        </div>
      </div>
    );
  }

  const slideWidth = data.properties.slide_size?.width || 9144000;
  const slideHeight = data.properties.slide_size?.height || 6858000;

  return (
    <div className="container mx-auto py-8">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-2">PowerPoint JSON Viewer</h1>
        <div className="flex justify-center gap-2 mb-4">
          <Badge variant="outline">{data.shapes.length} slides</Badge>
          <Badge variant="outline">{data.layouts.length} layouts</Badge>
          <Badge variant="outline">{Object.keys(data.media.images).length} images</Badge>
        </div>
      </div>

      <Tabs defaultValue="slides" className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="slides">Slides</TabsTrigger>
          <TabsTrigger value="layouts">Layouts</TabsTrigger>
          <TabsTrigger value="theme">Theme</TabsTrigger>
          <TabsTrigger value="media">Media</TabsTrigger>
          <TabsTrigger value="properties">Properties</TabsTrigger>
        </TabsList>

        <TabsContent value="slides" className="space-y-6">
          {/* Slide Navigation Controls */}
          <div className="flex items-center justify-between mb-6 p-4 bg-gray-50 rounded-lg">
            <Button 
              variant="outline" 
              onClick={() => setCurrentSlideIndex(Math.max(0, currentSlideIndex - 1))}
              disabled={currentSlideIndex === 0}
            >
              Previous
            </Button>
            
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium">
                Slide {currentSlideIndex + 1} of {data.shapes.length}
              </span>
              
              {/* Slide Number Input */}
              <div className="flex items-center gap-2">
                <label htmlFor="slideNumber" className="text-sm">Go to:</label>
                <input
                  id="slideNumber"
                  type="number"
                  min="1"
                  max={data.shapes.length}
                  value={currentSlideIndex + 1}
                  onChange={(e) => {
                    const slideNum = parseInt(e.target.value) - 1;
                    if (slideNum >= 0 && slideNum < data.shapes.length) {
                      setCurrentSlideIndex(slideNum);
                    }
                  }}
                  className="w-16 px-2 py-1 text-sm border rounded"
                />
              </div>
            </div>
            
            <Button 
              variant="outline"
              onClick={() => setCurrentSlideIndex(Math.min(data.shapes.length - 1, currentSlideIndex + 1))}
              disabled={currentSlideIndex === data.shapes.length - 1}
            >
              Next
            </Button>
          </div>

          {/* Current Slide Display */}
          <div className="flex justify-center">
            {data.shapes[currentSlideIndex] && (
              <SlideRenderer
                key={currentSlideIndex}
                slide={data.shapes[currentSlideIndex]}
                theme={data.theme}
                slideWidth={slideWidth / 9525}
                slideHeight={slideHeight / 9525}
              />
            )}
          </div>
        </TabsContent>

        <TabsContent value="layouts" className="space-y-6">
          <div className="grid gap-4">
            {data.layouts.map((layout) => (
              <Card key={layout.layout_index}>
                <CardHeader>
                  <CardTitle>{layout.name}</CardTitle>
                  <CardDescription>
                    Layout {layout.layout_index + 1} • {layout.placeholders.length} placeholders
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {layout.placeholders.map((placeholder, index) => (
                      <div key={index} className="p-3 border rounded-lg">
                        <div className="font-medium">{placeholder.name}</div>
                        <div className="text-sm text-muted-foreground">
                          {placeholder.placeholder_format}
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">
                          {Math.round(placeholder.width / 9525)}×{Math.round(placeholder.height / 9525)} px
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="theme" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>{data.theme.theme_name}</CardTitle>
              <CardDescription>Theme colors and fonts</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="font-semibold mb-3">Color Scheme</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {Object.entries(data.theme.color_scheme).map(([name, color]) => (
                    <div key={name} className="flex items-center gap-2">
                      <div
                        className="w-6 h-6 rounded border"
                        style={{ backgroundColor: `#${color.rgb}` }}
                      />
                      <div>
                        <div className="font-medium text-sm">{name}</div>
                        <div className="text-xs text-muted-foreground">#{color.rgb}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="font-semibold mb-3">Font Scheme</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-3 border rounded-lg">
                    <div className="font-medium mb-1">Major Font (Headings)</div>
                    <div className="text-sm text-muted-foreground">
                      {data.theme.font_scheme.major_font?.latin || "Default"}
                    </div>
                  </div>
                  <div className="p-3 border rounded-lg">
                    <div className="font-medium mb-1">Minor Font (Body)</div>
                    <div className="text-sm text-muted-foreground">
                      {data.theme.font_scheme.minor_font?.latin || "Default"}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="media" className="space-y-6">
          <div className="grid gap-4">
            {Object.entries(data.media.images).map(([filename, media]) => (
              <Card key={filename}>
                <CardHeader>
                  <CardTitle className="text-lg">{filename}</CardTitle>
                  <CardDescription>
                    Size: {Math.round(media.size / 1024)} KB
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <img
                    src={`data:image/jpeg;base64,${media.data}`}
                    alt={filename}
                    className="max-w-full max-h-64 object-contain border rounded"
                  />
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="properties" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Document Properties</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {data.properties.core_properties && Object.entries(data.properties.core_properties).map(([key, value]) => (
                  value && (
                    <div key={key} className="p-3 border rounded-lg">
                      <div className="font-medium capitalize">{key.replace(/_/g, ' ')}</div>
                      <div className="text-sm text-muted-foreground">{value}</div>
                    </div>
                  )
                ))}
              </div>
              
              {data.properties.slide_size && (
                <div className="mt-6 p-3 border rounded-lg">
                  <div className="font-medium">Slide Size</div>
                  <div className="text-sm text-muted-foreground">
                    {Math.round(data.properties.slide_size.width / 9525)}×{Math.round(data.properties.slide_size.height / 9525)} pixels
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}