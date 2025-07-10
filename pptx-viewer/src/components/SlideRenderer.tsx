"use client";

import { Shape, SlideData, Theme, ColorInfo, FillInfo } from "@/types/pptx";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface SlideRendererProps {
  slide: SlideData;
  theme: Theme;
  slideWidth?: number;
  slideHeight?: number;
}

export default function SlideRenderer({ slide, theme, slideWidth = 960, slideHeight = 540 }: SlideRendererProps) {
  const scale = Math.min(800 / slideWidth, 600 / slideHeight);
  const scaledWidth = slideWidth * scale;
  const scaledHeight = slideHeight * scale;

  const convertEMUToPixels = (emu: number | null | undefined): number => {
    if (emu === null || emu === undefined) return 0;
    return emu / 9525; // 1 inch = 914400 EMU, 1 inch = 96 pixels
  };

  const getColorFromInfo = (colorInfo: ColorInfo | undefined): string => {
    if (!colorInfo) return "transparent";
    
    if (colorInfo.rgb?.hex) {
      return `#${colorInfo.rgb.hex}`;
    }
    
    if (colorInfo.theme_color && theme.color_scheme) {
      const themeColorKey = colorInfo.theme_color.toLowerCase().replace(/[^a-z0-9]/g, '');
      const themeColor = theme.color_scheme[themeColorKey];
      if (themeColor?.rgb) {
        return `#${themeColor.rgb}`;
      }
    }
    
    return "transparent";
  };

  const getSchemeColor = (schemeClr: string): string => {
    if (!theme.color_scheme) return "transparent";
    
    const colorKey = schemeClr.toLowerCase();
    const themeColor = theme.color_scheme[colorKey];
    if (themeColor?.rgb) {
      return `#${themeColor.rgb}`;
    }
    
    return "transparent";
  };

  const parseCustomGeometry = (shape: Shape): string => {
    if (!shape.custom_geometry || !shape.custom_geometry.paths) return "";
    
    const paths = shape.custom_geometry.paths;
    if (paths.length === 0) return "";
    
    const path = paths[0];
    if (!path.commands) return "";
    
    let pathData = "";
    
    for (const cmd of path.commands) {
      switch (cmd.command) {
        case 'moveTo':
          pathData += `M ${cmd.x} ${cmd.y} `;
          break;
        case 'lnTo':
          pathData += `L ${cmd.x} ${cmd.y} `;
          break;
        case 'cubicBezTo':
          if (cmd.points && cmd.points.length === 3) {
            pathData += `C ${cmd.points[0].x} ${cmd.points[0].y} ${cmd.points[1].x} ${cmd.points[1].y} ${cmd.points[2].x} ${cmd.points[2].y} `;
          }
          break;
        case 'close':
          pathData += "Z ";
          break;
      }
    }
    
    return pathData.trim();
  };

  const extractFillFromXML = (xmlString: string): string => {
    if (!xmlString) return "transparent";
    
    // Extract srgbClr color
    const srgbMatch = xmlString.match(/<ns1:srgbClr val="([^"]+)"/);
    if (srgbMatch) {
      return `#${srgbMatch[1]}`;
    }
    
    // Extract schemeClr color
    const schemeMatch = xmlString.match(/<ns1:schemeClr val="([^"]+)"/);
    if (schemeMatch) {
      return getSchemeColor(schemeMatch[1]);
    }
    
    return "transparent";
  };

  const getFillStyle = (fill: FillInfo | undefined): React.CSSProperties => {
    if (!fill) return {};
    
    if (fill.solid && fill.fore_color) {
      return {
        backgroundColor: getColorFromInfo(fill.fore_color),
      };
    }
    
    if (fill.gradient && fill.gradient_stops) {
      const stops = fill.gradient_stops.map((stop, index) => 
        `${getColorFromInfo(stop.color)} ${stop.position * 100}%`
      ).join(', ');
      
      const angle = fill.gradient_angle || 0;
      return {
        background: `linear-gradient(${angle}deg, ${stops})`,
      };
    }
    
    return {};
  };

  const getShapeStyle = (shape: Shape): React.CSSProperties => {
    const left = convertEMUToPixels(shape.left) * scale;
    const top = convertEMUToPixels(shape.top) * scale;
    const width = convertEMUToPixels(shape.width) * scale;
    const height = convertEMUToPixels(shape.height) * scale;
    
    const style: React.CSSProperties = {
      position: "absolute",
      left: `${left}px`,
      top: `${top}px`,
      width: `${width}px`,
      height: `${height}px`,
      transform: shape.rotation ? `rotate(${shape.rotation}deg)` : undefined,
      ...getFillStyle(shape.fill),
    };

    if (shape.line && shape.line.width) {
      style.border = `${convertEMUToPixels(shape.line.width) * scale}px solid ${getColorFromInfo(shape.line.color)}`;
    }

    return style;
  };

  const renderText = (shape: Shape): React.ReactNode => {
    if (!shape.text_frame || !shape.text_frame.paragraphs) {
      return shape.text || "";
    }

    return shape.text_frame.paragraphs.map((paragraph, paraIndex) => (
      <div key={paraIndex} className="paragraph" style={{ textAlign: paragraph.alignment as any }}>
        {paragraph.runs.map((run, runIndex) => (
          <span
            key={runIndex}
            style={{
              fontFamily: run.font_name || theme.font_scheme.minor_font?.latin || "Arial",
              fontSize: run.font_size ? `${run.font_size / 100}pt` : "12pt",
              fontWeight: run.bold ? "bold" : "normal",
              fontStyle: run.italic ? "italic" : "normal",
              textDecoration: run.underline ? "underline" : "none",
              color: getColorFromInfo(run.color),
            }}
          >
            {run.text}
          </span>
        ))}
      </div>
    ));
  };

  const getShapeTypeColor = (shapeType: string): string => {
    const colors = {
      "AUTO_SHAPE": "#3b82f6",
      "TEXT_BOX": "#10b981",
      "PICTURE": "#f59e0b",
      "CHART": "#ef4444",
      "TABLE": "#8b5cf6",
      "GROUP": "#6b7280",
    };
    
    for (const [type, color] of Object.entries(colors)) {
      if (shapeType.includes(type)) {
        return color;
      }
    }
    
    return "#6b7280";
  };

  return (
    <Card className="w-full">
      <CardContent className="p-4">
        <div className="mb-4 flex items-center gap-2">
          <h3 className="font-semibold">Slide {slide.slide_index + 1}</h3>
          <Badge variant="outline">{slide.shapes.length} shapes</Badge>
        </div>
        
        <div 
          className="relative border border-gray-200 bg-white mx-auto"
          style={{
            width: `${scaledWidth}px`,
            height: `${scaledHeight}px`,
          }}
        >
          {slide.shapes.map((shape, index) => {
            const left = convertEMUToPixels(shape.left) * scale;
            const top = convertEMUToPixels(shape.top) * scale;
            const width = convertEMUToPixels(shape.width) * scale;
            const height = convertEMUToPixels(shape.height) * scale;
            
            const pathData = parseCustomGeometry(shape);
            const fillColor = shape.element?.xml_string 
              ? extractFillFromXML(shape.element.xml_string)
              : getFillStyle(shape.fill).backgroundColor || "transparent";

            // Check if it's a placeholder with text
            const isTextPlaceholder = shape.is_placeholder && shape.has_text_frame && shape.text;
            
            return (
              <div
                key={index}
                className="absolute"
                style={{
                  left: `${left}px`,
                  top: `${top}px`,
                  width: `${width}px`,
                  height: `${height}px`,
                  transform: shape.rotation ? `rotate(${shape.rotation}deg)` : undefined,
                }}
                title={`${shape.name || `Shape ${index + 1}`} (${shape.shape_type})`}
              >
                {/* Render custom geometry shapes with SVG */}
                {pathData && !isTextPlaceholder && (
                  <svg
                    width="100%"
                    height="100%"
                    viewBox={`0 0 ${shape.custom_geometry?.paths?.[0]?.width || width} ${shape.custom_geometry?.paths?.[0]?.height || height}`}
                    className="absolute inset-0"
                  >
                    <path
                      d={pathData}
                      fill={fillColor}
                      stroke="none"
                    />
                  </svg>
                )}
                
                {/* Render simple shapes without custom geometry */}
                {!pathData && !isTextPlaceholder && (
                  <div
                    className="absolute inset-0"
                    style={{
                      backgroundColor: fillColor,
                      borderRadius: shape.shape_type.includes('OVAL') || shape.shape_type.includes('ELLIPSE') ? '50%' : '0',
                    }}
                  />
                )}

                {/* Render text content */}
                {shape.has_text_frame && shape.text && (
                  <div 
                    className="absolute inset-0 flex items-center justify-center text-center p-1"
                    style={{
                      fontSize: isTextPlaceholder ? 
                        (shape.text.includes('Design Elements') ? `${Math.max(24, width / 12)}px` : `${Math.max(14, width / 20)}px`) :
                        `${Math.max(8, width / 20)}px`,
                      fontWeight: isTextPlaceholder && shape.text.includes('Design Elements') ? 'bold' : 'normal',
                      lineHeight: "1.2",
                      wordBreak: "break-word",
                      color: isTextPlaceholder ? '#000' : 'inherit',
                      zIndex: 10,
                    }}
                  >
                    {renderText(shape)}
                  </div>
                )}
              </div>
            );
          })}
        </div>
        
        <div className="mt-4 text-sm text-gray-600">
          <p>Scale: {Math.round(scale * 100)}% | Original: {slideWidth}×{slideHeight}</p>
        </div>
      </CardContent>
    </Card>
  );
}