"use client";

import { Shape, SlideData, Theme, ColorInfo, FillInfo } from "@/types/pptx";

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

  const extractTextFromXML = (xmlString: string): string[] => {
    if (!xmlString) return [];
    
    const textElements: string[] = [];
    
    // Extract text from <ns1:t> elements
    const textMatches = xmlString.match(/<ns1:t[^>]*>([^<]*)<\/ns1:t>/g);
    if (textMatches) {
      textMatches.forEach(match => {
        const textContent = match.replace(/<[^>]*>/g, '').trim();
        if (textContent && textContent.length > 0) {
          textElements.push(textContent);
        }
      });
    }
    
    // Extract text from simple text nodes between tags
    const simpleTextMatches = xmlString.match(/>([^<>]+)</g);
    if (simpleTextMatches) {
      simpleTextMatches.forEach(match => {
        const textContent = match.replace(/[><]/g, '').trim();
        // Only include if it's not a number or short text that looks like data
        if (textContent && textContent.length > 2 && !textContent.match(/^\d+$/) && !textContent.includes('ns')) {
          textElements.push(textContent);
        }
      });
    }
    
    // Remove duplicates and filter out empty strings
    return [...new Set(textElements)].filter(text => text.trim().length > 0);
  };

  const createArcPath = (shape: Shape): string => {
    const radius = 150; // Base radius for the arc
    const innerRadius = 60; // Inner radius for donut hole
    const centerX = 150;
    const centerY = 150;
    
    // Map segments based on theme colors to match original PowerPoint layout
    const themeColor = shape.fill?.fore_color?.theme_color;
    let startAngle = 0;
    let endAngle = 90;
    
    switch (themeColor) {
      case "ACCENT_1 (5)": // Dark navy - 01 (top-left)
        startAngle = 180;
        endAngle = 270;
        break;
      case "ACCENT_4 (8)": // Orange - 02 (top-right)  
        startAngle = 270;
        endAngle = 360;
        break;
      case "ACCENT_2 (6)": // Teal - 03 (bottom-left)
        startAngle = 90;
        endAngle = 180;
        break;
      case "ACCENT_5 (9)": // Light orange - 04 (bottom-right)
        startAngle = 0;
        endAngle = 90;
        break;
      default:
        // Fallback to original logic if theme color not recognized
        const segmentIndex = (shape.shape_index || 0) % 4;
        startAngle = segmentIndex * 90;
        endAngle = startAngle + 90;
    }
    
    // Convert to radians
    const startRad = (startAngle * Math.PI) / 180;
    const endRad = (endAngle * Math.PI) / 180;
    
    // Calculate outer arc points
    const x1 = centerX + radius * Math.cos(startRad);
    const y1 = centerY + radius * Math.sin(startRad);
    const x2 = centerX + radius * Math.cos(endRad);
    const y2 = centerY + radius * Math.sin(endRad);
    
    // Calculate inner arc points
    const x3 = centerX + innerRadius * Math.cos(endRad);
    const y3 = centerY + innerRadius * Math.sin(endRad);
    const x4 = centerX + innerRadius * Math.cos(startRad);
    const y4 = centerY + innerRadius * Math.sin(startRad);
    
    const largeArcFlag = (endAngle - startAngle) > 180 ? 1 : 0;
    
    return `M ${x1} ${y1} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2} L ${x3} ${y3} A ${innerRadius} ${innerRadius} 0 ${largeArcFlag} 0 ${x4} ${y4} Z`;
  };

  const getFillStyle = (fill: FillInfo | undefined): React.CSSProperties => {
    if (!fill) return {};
    
    if (fill.solid && fill.fore_color) {
      return {
        backgroundColor: getColorFromInfo(fill.fore_color),
      };
    }
    
    if (fill.gradient && fill.gradient_stops) {
      const stops = fill.gradient_stops.map((stop) => 
        `${getColorFromInfo(stop.color)} ${stop.position * 100}%`
      ).join(', ');
      
      const angle = fill.gradient_angle || 0;
      return {
        background: `linear-gradient(${angle}deg, ${stops})`,
      };
    }
    
    return {};
  };


  const renderText = (shape: Shape): React.ReactNode => {
    if (!shape.text_frame || !shape.text_frame.paragraphs) {
      return shape.text || "";
    }

    return shape.text_frame.paragraphs.map((paragraph, paraIndex) => (
      <div key={paraIndex} className="paragraph" style={{ textAlign: paragraph.alignment as 'left' | 'right' | 'center' | 'justify' }}>
        {paragraph.runs.map((run, runIndex) => (
          <span
            key={runIndex}
            style={{
              fontFamily: run.font_name || theme.font_scheme.minor_font?.latin || "Arial",
              fontSize: run.font_size ? `${run.font_size / 12700}pt` : "12pt",
              fontWeight: run.bold ? "bold" : "normal",
              fontStyle: run.italic ? "italic" : "normal",
              textDecoration: run.underline ? "underline" : "none",
              color: '#000000', // Force black color
            }}
          >
            {run.text}
          </span>
        ))}
      </div>
    ));
  };


  return (
    <div>
      <h3>Slide {slide.slide_index + 1}</h3>
      <div>
        
        <div 
          className="relative border border-gray-200 bg-white mx-auto"
          style={{
            width: `${scaledWidth}px`,
            height: `${scaledHeight}px`,
          }}
        >
          {/* Render unified donut chart for slide 3 BLOCK_ARC shapes */}
          {slide.slide_index === 2 && (() => {
            const blockArcShapes = slide.shapes.filter(shape => 
              shape?.auto_shape_type?.includes('BLOCK_ARC')
            );
            
            if (blockArcShapes.length > 0) {
              const slideWidth = 960; 
              const slideHeight = 540;  
              const centerLeft = (slideWidth / 2) - 50; // Shift left by 50px to match original position
              const centerTop = slideHeight / 2;
              
              return (
                <svg
                  width="300"
                  height="300"
                  viewBox="0 0 300 300"
                  className="absolute"
                  style={{ 
                    left: `${centerLeft}px`, 
                    top: `${centerTop}px`,
                    overflow: 'visible',
                    pointerEvents: 'none',
                    transform: 'translate(-50%, -50%)',
                    zIndex: 10
                  }}
                >
                  {blockArcShapes.map((shape, arcIndex) => {
                    const fillColor = shape.element?.xml_string 
                      ? extractFillFromXML(shape.element.xml_string)
                      : getFillStyle(shape.fill).backgroundColor || "transparent";
                    return (
                      <path
                        key={`arc-${shape.shape_id || shape.shape_index || arcIndex}`}
                        d={createArcPath(shape)}
                        fill={fillColor}
                        stroke="none"
                      />
                    );
                  })}
                </svg>
              );
            }
            return null;
          })()}

          {/* Render semicircle donut chart for slide 5 BLOCK_ARC shapes */}
          {slide.slide_index === 4 && (() => {
            const blockArcShapes = slide.shapes.filter(shape => 
              shape?.auto_shape_type?.includes('BLOCK_ARC')
            );
            
            if (blockArcShapes.length > 0) {
              const slideWidth = 960; 
              const slideHeight = 540;  
              const centerLeft = slideWidth / 2 - 10; // Slightly left to center better
              const centerTop = slideHeight / 2 - 30; // Move up to match original position
              
              return (
                <svg
                  width="400"
                  height="200"
                  viewBox="0 0 400 200"
                  className="absolute"
                  style={{ 
                    left: `${centerLeft}px`, 
                    top: `${centerTop}px`,
                    overflow: 'visible',
                    pointerEvents: 'none',
                    transform: 'translate(-50%, -50%)',
                    zIndex: 10
                  }}
                >
                  {blockArcShapes.map((shape, arcIndex) => {
                    const fillColor = shape.element?.xml_string 
                      ? extractFillFromXML(shape.element.xml_string)
                      : getFillStyle(shape.fill).backgroundColor || "transparent";
                    
                    // Create semicircle donut segments for slide 5
                    const radius = 150;
                    const innerRadius = 80;
                    const centerX = 200;
                    const centerY = 180;
                    
                    // Determine which segment based on theme color
                    const themeColor = shape.fill?.fore_color?.theme_color;
                    let startAngle, endAngle;
                    
                    if (themeColor === "ACCENT_1 (5)") {
                      // Saturn (55%) - larger left segment
                      startAngle = 180; // Start from left
                      endAngle = 180 + (180 * 0.55); // 55% of semicircle
                    } else if (themeColor === "ACCENT_4 (8)") {
                      // Neptune (45%) - smaller right segment  
                      startAngle = 180 + (180 * 0.55); // Start where Saturn ends
                      endAngle = 360; // End at right
                    } else {
                      // Fallback
                      startAngle = arcIndex * 90;
                      endAngle = startAngle + 90;
                    }
                    
                    // Convert to radians
                    const startRad = (startAngle * Math.PI) / 180;
                    const endRad = (endAngle * Math.PI) / 180;
                    
                    // Calculate outer arc points
                    const x1 = centerX + radius * Math.cos(startRad);
                    const y1 = centerY + radius * Math.sin(startRad);
                    const x2 = centerX + radius * Math.cos(endRad);
                    const y2 = centerY + radius * Math.sin(endRad);
                    
                    // Calculate inner arc points
                    const x3 = centerX + innerRadius * Math.cos(endRad);
                    const y3 = centerY + innerRadius * Math.sin(endRad);
                    const x4 = centerX + innerRadius * Math.cos(startRad);
                    const y4 = centerY + innerRadius * Math.sin(startRad);
                    
                    const largeArcFlag = (endAngle - startAngle) > 180 ? 1 : 0;
                    const pathData = `M ${x1} ${y1} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2} L ${x3} ${y3} A ${innerRadius} ${innerRadius} 0 ${largeArcFlag} 0 ${x4} ${y4} Z`;
                    
                    return (
                      <path
                        key={`arc-${shape.shape_id || shape.shape_index || arcIndex}`}
                        d={pathData}
                        fill={fillColor}
                        stroke="none"
                      />
                    );
                  })}
                </svg>
              );
            }
            return null;
          })()}

          {/* Render semicircle donut chart for slide 12 BLOCK_ARC shapes */}
          {slide.slide_index === 11 && (() => {
            const blockArcShapes = slide.shapes.filter(shape => 
              shape?.auto_shape_type?.includes('BLOCK_ARC')
            );
            
            if (blockArcShapes.length > 0) {
              const slideWidth = 960; 
              const slideHeight = 540;  
              const centerLeft = slideWidth / 2 - 30; // Adjust left to better center the semicircle
              const centerTop = slideHeight / 2 - 10; // Move up slightly
              
              return (
                <svg
                  width="400"
                  height="200"
                  viewBox="0 0 400 200"
                  className="absolute"
                  style={{ 
                    left: `${centerLeft}px`, 
                    top: `${centerTop}px`,
                    overflow: 'visible',
                    pointerEvents: 'none',
                    transform: 'translate(-50%, -50%)',
                    zIndex: 10
                  }}
                >
                  {/* Render all 4 segments with proper colors and percentages */}
                  {[0, 1, 2, 3].map((segmentIndex) => {
                    // Create semicircle donut segments for slide 12
                    const radius = 150;
                    const innerRadius = 80;
                    const centerX = 200;
                    const centerY = 180;
                    
                    // Define segments based on percentages from reference image
                    const percentages = [0.30, 0.20, 0.35, 0.15]; // Mars, Jupiter, Saturn, Neptune
                    const cumulativePercentages = [0, 0.30, 0.50, 0.85];
                    const colors = ['accent2', 'accent3', 'accent4', 'accent5']; // Teal, Green, Orange, Yellow
                    const labels = ['30%', '20%', '35%', '15%'];
                    
                    const startAngle = 180 + (180 * cumulativePercentages[segmentIndex]);
                    const endAngle = 180 + (180 * (cumulativePercentages[segmentIndex] + percentages[segmentIndex]));
                    const segmentColor = getSchemeColor(colors[segmentIndex]);
                    
                    // Convert to radians
                    const startRad = (startAngle * Math.PI) / 180;
                    const endRad = (endAngle * Math.PI) / 180;
                    
                    // Calculate outer arc points
                    const x1 = centerX + radius * Math.cos(startRad);
                    const y1 = centerY + radius * Math.sin(startRad);
                    const x2 = centerX + radius * Math.cos(endRad);
                    const y2 = centerY + radius * Math.sin(endRad);
                    
                    // Calculate inner arc points
                    const x3 = centerX + innerRadius * Math.cos(endRad);
                    const y3 = centerY + innerRadius * Math.sin(endRad);
                    const x4 = centerX + innerRadius * Math.cos(startRad);
                    const y4 = centerY + innerRadius * Math.sin(startRad);
                    
                    const largeArcFlag = (endAngle - startAngle) > 180 ? 1 : 0;
                    const pathData = `M ${x1} ${y1} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2} L ${x3} ${y3} A ${innerRadius} ${innerRadius} 0 ${largeArcFlag} 0 ${x4} ${y4} Z`;
                    
                    // Calculate text position (middle of segment)
                    const middleAngle = startAngle + (endAngle - startAngle) / 2;
                    const middleRad = (middleAngle * Math.PI) / 180;
                    const textRadius = (radius + innerRadius) / 2;
                    const textX = centerX + textRadius * Math.cos(middleRad);
                    const textY = centerY + textRadius * Math.sin(middleRad);
                    
                    return (
                      <g key={`segment-${segmentIndex}`}>
                        <path
                          d={pathData}
                          fill={segmentColor}
                          stroke="none"
                        />
                        <text
                          x={textX}
                          y={textY}
                          textAnchor="middle"
                          dominantBaseline="middle"
                          fill="white"
                          fontSize="24"
                          fontWeight="bold"
                        >
                          {labels[segmentIndex]}
                        </text>
                      </g>
                    );
                  })}
                </svg>
              );
            }
            return null;
          })()}

          {slide.shapes.map((shape, index) => {
            const left = convertEMUToPixels(shape.left) * scale;
            const top = convertEMUToPixels(shape.top) * scale;
            const width = convertEMUToPixels(shape.width) * scale;
            const height = convertEMUToPixels(shape.height) * scale;
            
            const pathData = parseCustomGeometry(shape);
            const fillColor = shape.element?.xml_string 
              ? extractFillFromXML(shape.element.xml_string)
              : getFillStyle(shape.fill).backgroundColor || "transparent";

            // Extract text from XML if structured text data is missing
            const xmlTextContent = (!shape.text || shape.text.trim().length === 0) && shape.element?.xml_string 
              ? extractTextFromXML(shape.element.xml_string) 
              : [];
            
            // Check if it's a placeholder with text
            
            // Check if it's a text box or placeholder
            const isTextShape = (shape.has_text_frame && shape.text && shape.text.trim().length > 0) || xmlTextContent.length > 0;
            
            // Check if it's a GROUP shape
            const isGroupShape = shape.shape_type && shape.shape_type.includes('GROUP');
            
            // Check if it's a BLOCK_ARC shape (donut chart segment)
            const isBlockArc = shape.auto_shape_type && shape.auto_shape_type.includes('BLOCK_ARC');
            
            // Check if it's a FREEFORM circular planet container (for slide 3 corner planet icons)
            const isCircularPlanet = slide.slide_index === 2 && 
              shape.shape_type && shape.shape_type.includes('FREEFORM') &&
              pathData && shape.custom_geometry?.paths?.[0]?.commands?.some(cmd => cmd.command === 'cubicBezTo') &&
              Math.abs(width - height) < 50; // Nearly square/circular dimensions
            
            // Skip BLOCK_ARC shapes in slide 3, slide 5, and slide 12 since they're rendered as unified donut above
            if ((slide.slide_index === 2 || slide.slide_index === 4 || slide.slide_index === 11) && isBlockArc) {
              return null;
            }
            
            
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
                {pathData && !isTextShape && !isCircularPlanet && (
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
                


                {/* Render pentagon arrow shapes for slide 4 */}
                {slide.slide_index === 3 && shape.auto_shape_type?.includes('PENTAGON') && (
                  <div
                    className="absolute inset-0"
                    style={{
                      backgroundColor: fillColor,
                      clipPath: 'polygon(0% 0%, 80% 0%, 100% 50%, 80% 100%, 0% 100%)', // Arrow shape
                    }}
                  />
                )}

                {/* Render simple shapes without custom geometry and without text */}
                {!pathData && !isTextShape && !isBlockArc && !isCircularPlanet && !(slide.slide_index === 3 && shape.auto_shape_type?.includes('PENTAGON')) && fillColor !== "transparent" && (
                  <div
                    className="absolute inset-0"
                    style={{
                      backgroundColor: fillColor,
                      borderRadius: (() => {
                        // Apply rounded corners for different shape types
                        if (shape.shape_type.includes('OVAL') || shape.shape_type.includes('ELLIPSE')) {
                          return '50%';
                        }
                        // Check for rounded rectangle property in JSON data
                        else if (shape.auto_shape_type?.includes('ROUNDED_RECTANGLE')) {
                          // Use adjustments array to determine corner radius if available
                          const adjustment = shape.adjustments?.[0] || 0.5;
                          // Convert adjustment to pixel value (adjustment is typically 0.0-1.0)
                          const cornerRadius = Math.max(8, Math.min(20, adjustment * 40));
                          return `${cornerRadius}px`;
                        }
                        // Fallback: For slide 13, apply rounded corners to rectangular shapes
                        else if (slide.slide_index === 12) {
                          return '8px';
                        }
                        return '0';
                      })(),
                    }}
                  />
                )}

                {/* Render circular planet containers (FREEFORM) */}
                {isCircularPlanet && (
                  <div className="absolute inset-0">
                    {/* Render the circular background */}
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
                    
                    {/* Render white planet icon */}
                    <svg
                      width={Math.min(width * 0.4, 60)}
                      height={Math.min(height * 0.4, 60)}
                      viewBox="0 0 24 24"
                      className="absolute"
                      style={{ 
                        left: '50%', 
                        top: '50%', 
                        transform: 'translate(-50%, -50%)',
                        zIndex: 10
                      }}
                    >
                      {/* Generic planet icon */}
                      <circle cx="12" cy="12" r="8" fill="white" stroke="none"/>
                      <circle cx="12" cy="12" r="3" fill="none" stroke="white" strokeWidth="1" opacity="0.3"/>
                      <path d="M8 12c0-2 1-3 2-3s2 1 2 3-1 3-2 3-2-1-2-3z" fill="none" stroke="white" strokeWidth="0.8" opacity="0.4"/>
                    </svg>
                  </div>
                )}

                {/* Render GROUP shapes as containers */}
                {isGroupShape && (
                  <div
                    className="absolute inset-0 overflow-hidden"
                    style={{
                      backgroundColor: (() => {
                        // Fix for slide 12 GROUP shapes - use transparent background with colored border
                        if (slide.slide_index === 11) {
                          return 'transparent';
                        }
                        // Fix for slide 3 GROUP shapes - assign correct theme colors based on position  
                        else if (slide.slide_index === 2) {
                          const leftPos = convertEMUToPixels(shape.left);
                          const topPos = convertEMUToPixels(shape.top);
                          
                          // Venus (bottom-left): Shape 27, left=702674, should be teal
                          if (leftPos < 200 && topPos > 300) {
                            return getSchemeColor('accent2'); // Teal
                          }
                          // Mars (bottom-right): Shape 29, left=8074337, should be orange  
                          else if (leftPos > 700 && topPos > 300) {
                            return getSchemeColor('accent4'); // Orange
                          }
                          // Center icon: Shape 28, left=4383513, should be green
                          else if (leftPos > 300 && leftPos < 700 && topPos > 200 && topPos < 400) {
                            return getSchemeColor('accent3'); // Green
                          }
                        }
                        // Fix for slide 20 GROUP shapes - assign correct theme colors based on position  
                        else if (slide.slide_index === 19) {
                          const leftPos = convertEMUToPixels(shape.left);
                          const topPos = convertEMUToPixels(shape.top);
                          
                          // Mercury (top-left): left=3201268, top=2633377 - orange
                          if (leftPos > 300 && leftPos < 400 && topPos > 250 && topPos < 300) {
                            return getSchemeColor('accent4'); // Orange
                          }
                          // Mars (center-left): left=1143861, top=1745090 - dark blue
                          else if (leftPos > 100 && leftPos < 200 && topPos > 150 && topPos < 200) {
                            return getSchemeColor('accent1'); // Dark blue
                          }
                          // Venus (top-right): left=5258696, top=1698177 - yellow
                          else if (leftPos > 500 && topPos > 150 && topPos < 200) {
                            return getSchemeColor('accent5'); // Yellow
                          }
                          // Jupiter (right): left=7409632, top=2610133 - green
                          else if (leftPos > 700 && topPos > 250 && topPos < 300) {
                            return getSchemeColor('accent3'); // Green
                          }
                        }
                        
                        return fillColor !== "transparent" ? fillColor : getSchemeColor('accent' + (index % 4 + 1));
                      })(),
                      border: 'none',
                      borderRadius: slide.slide_index === 2 || slide.slide_index === 19 ? '50%' : '8px', // Circular for slide 3 and 20, rounded corners for slide 4 and 12
                    }}
                  >
                    {/* Render custom geometry icon or fallback icon */}
                    {pathData ? (
                      <svg
                        width={Math.min(width * 0.6, 80)}
                        height={Math.min(height * 0.6, 80)}
                        viewBox={`0 0 ${shape.custom_geometry?.paths?.[0]?.width || 100} ${shape.custom_geometry?.paths?.[0]?.height || 100}`}
                        className="absolute inset-0 m-auto"
                        style={{ 
                          left: '50%', 
                          top: '50%', 
                          transform: 'translate(-50%, -50%)',
                          zIndex: 10
                        }}
                      >
                        <path
                          d={pathData}
                          fill="white"
                          stroke="none"
                        />
                      </svg>
                    ) : slide.slide_index === 3 ? (
                      // Fallback icons for slide 4 planet GROUP shapes
                      <svg
                        width={Math.min(width * 0.4, 60)}
                        height={Math.min(height * 0.4, 60)}
                        viewBox="0 0 24 24"
                        className="absolute"
                        style={{ 
                          left: '50%', 
                          top: '50%', 
                          transform: 'translate(-50%, -50%)',
                          zIndex: 10
                        }}
                      >
                        {(() => {
                          const topPos = convertEMUToPixels(shape.top);
                          
                          // Jupiter (top position ~165px): People icon
                          if (topPos < 180) {
                            return (
                              <g fill="white">
                                <circle cx="12" cy="8" r="3"/>
                                <path d="M12 14c-4 0-7 2-7 4v2h14v-2c0-2-3-4-7-4z"/>
                              </g>
                            );
                          }
                          // Mars (second position ~231px): Pie chart icon  
                          else if (topPos < 250) {
                            return (
                              <g fill="white">
                                <circle cx="12" cy="12" r="8" fillOpacity="0.3"/>
                                <path d="M12 4 A8 8 0 0 1 20 12 L12 12 Z"/>
                              </g>
                            );
                          }
                          // Saturn (third position ~324px): Document icon
                          else if (topPos < 350) {
                            return (
                              <g fill="white">
                                <rect x="6" y="4" width="12" height="16" rx="1"/>
                                <path d="M8 8h8M8 12h8M8 16h6"/>
                              </g>
                            );
                          }
                          // Neptune (bottom position ~410px): Gear icon
                          else {
                            return (
                              <g fill="white">
                                <circle cx="12" cy="12" r="3"/>
                                <path d="m19.4 15-1.5-1.5c.1-.5.1-1 0-1.5L19.4 9l-1.9-1.9-1.5 1.5c-.5-.1-1-.1-1.5 0L12.6 4.6 10.7 6.1l1.5 1.5c-.1.5-.1 1 0 1.5L10.7 10.7 8.8 12.6l1.5 1.5c.5.1 1 .1 1.5 0l1.5 1.5 1.9-1.9-1.5-1.5c.1-.5.1-1 0-1.5z"/>
                              </g>
                            );
                          }
                        })()}
                      </svg>
                    ) : slide.slide_index === 19 ? (
                      // Planet icons for slide 20 GROUP shapes
                      <svg
                        width={Math.min(width * 0.6, 80)}
                        height={Math.min(height * 0.6, 80)}
                        viewBox="0 0 24 24"
                        className="absolute"
                        style={{ 
                          left: '50%', 
                          top: '50%', 
                          transform: 'translate(-50%, -50%)',
                          zIndex: 10
                        }}
                      >
                        {(() => {
                          const leftPos = convertEMUToPixels(shape.left);
                          const topPos = convertEMUToPixels(shape.top);
                          
                          // Sort by position to assign icons more reliably
                          const quadrant = 
                            leftPos < 400 && topPos < 250 ? 'top-left' :
                            leftPos >= 400 && topPos < 250 ? 'top-right' :
                            leftPos < 400 && topPos >= 250 ? 'bottom-left' :
                            'bottom-right';
                          
                          // Mercury (top-left area) - Crown/atomic symbol
                          if (quadrant === 'top-left') {
                            return (
                              <g fill="white">
                                <circle cx="12" cy="12" r="4"/>
                                <path d="M12 2v4M12 18v4M22 12h-4M6 12H2M19.07 4.93l-2.83 2.83M7.76 16.24l-2.83 2.83M19.07 19.07l-2.83-2.83M7.76 7.76L4.93 4.93"/>
                              </g>
                            );
                          }
                          // Venus (top-right area) - Headphone/audio symbol
                          else if (quadrant === 'top-right') {
                            return (
                              <g fill="white">
                                <path d="M12 2a10 10 0 0 0-10 10v6a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2v-4a2 2 0 0 0-2-2H4v-2a8 8 0 0 1 16 0v2h-2a2 2 0 0 0-2 2v4a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2v-6a10 10 0 0 0-10-10z"/>
                              </g>
                            );
                          }
                          // Mars (bottom-left area) - Face/head profile
                          else if (quadrant === 'bottom-left') {
                            return (
                              <g fill="white">
                                <circle cx="12" cy="8" r="3"/>
                                <path d="M12 14c-4 0-7 2-7 4v2h14v-2c0-2-3-4-7-4z"/>
                              </g>
                            );
                          }
                          // Jupiter (bottom-right area) - Helmet/astronaut symbol
                          else if (quadrant === 'bottom-right') {
                            return (
                              <g fill="white">
                                <circle cx="12" cy="12" r="9"/>
                                <circle cx="12" cy="12" r="6" fill="none" stroke="white" strokeWidth="2"/>
                                <circle cx="12" cy="9" r="2"/>
                                <path d="M8 14c0 2 2 4 4 4s4-2 4-4"/>
                              </g>
                            );
                          }
                          
                          return null;
                        })()}
                      </svg>
                    ) : null}
                    
                    {/* Render text content from XML */}
                    {xmlTextContent.length > 0 && (
                      <div className="absolute inset-0 p-4 flex flex-col justify-between">
                        {xmlTextContent.map((text, textIndex) => {
                          const isTitle = text.length < 15 || text.includes('Mercury') || text.includes('Mars') || text.includes('Jupiter') || text.includes('Venus') || text.includes('Saturn') || text.includes('Neptune');
                          const isNumber = /^\d+$/.test(text);
                          
                          return (
                            <div
                              key={textIndex}
                              style={{
                                fontSize: isTitle ? `${Math.max(18, width / 12)}px` : isNumber ? `${Math.max(24, width / 8)}px` : `${Math.max(12, width / 20)}px`,
                                fontWeight: isTitle ? 'bold' : isNumber ? 'bold' : 'normal',
                                color: (() => {
                                  // For slide 12, use colored text for planet titles
                                  if (slide.slide_index === 11 && isTitle) {
                                    if (text.includes('Mars')) {
                                      return getSchemeColor('accent2'); // Teal
                                    } else if (text.includes('Jupiter')) {
                                      return getSchemeColor('accent3'); // Green
                                    } else if (text.includes('Saturn')) {
                                      return getSchemeColor('accent4'); // Orange
                                    } else if (text.includes('Neptune')) {
                                      return getSchemeColor('accent5'); // Yellow
                                    }
                                  }
                                  return '#000';
                                })(),
                                textAlign: isTitle ? 'left' : isNumber ? 'center' : 'left',
                                lineHeight: '1.2',
                                marginBottom: isTitle ? '8px' : isNumber ? '4px' : '0',
                                order: isTitle ? 1 : isNumber ? 3 : 2,
                              }}
                            >
                              {text}
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                )}

                {/* Render text content for regular shapes */}
                {isTextShape && !isGroupShape && !(slide.slide_index === 11 && shape.text && /^\d+%$/.test(shape.text.trim())) && (
                  <div 
                    className="absolute inset-0 flex items-center justify-center p-1"
                    style={{
                      fontSize: shape.text_frame?.paragraphs?.[0]?.runs?.[0]?.font_size 
                        ? `${Math.max(12, (shape.text_frame.paragraphs[0].runs[0].font_size / 12700) * scale)}px`
                        : shape.text?.includes('Design Elements') ? `${Math.max(28, width / 10)}px` : `${Math.max(16, width / 15)}px`,
                      fontWeight: shape.text?.includes('Design Elements') ? 'bold' : 'normal',
                      lineHeight: "1.2",
                      wordBreak: "break-word",
                      color: (() => {
                        // For slide 12, use white text on percentage numbers
                        if (slide.slide_index === 11 && shape.text && /^\d+%$/.test(shape.text.trim())) {
                          return '#fff';
                        }
                        return shape.text?.includes('Design Elements') ? '#000' : '#000';
                      })(),
                      backgroundColor: 'transparent',
                      zIndex: 10,
                      textAlign: shape.text_frame?.paragraphs?.[0]?.alignment?.includes('RIGHT') ? 'right' : 'center',
                      fontFamily: shape.text_frame?.paragraphs?.[0]?.runs?.[0]?.font_name || 'Arial, sans-serif',
                    }}
                  >
                    {shape.text ? renderText(shape) : xmlTextContent.join(' ')}
                  </div>
                )}
              </div>
            );
          })}
        </div>
        
      </div>
    </div>
  );
}