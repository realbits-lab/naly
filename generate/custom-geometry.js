import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export class CustomGeometryGenerator {
  constructor() {
    this.shapeDefinitions = new Map();
    this.loadShapeDefinitions();
  }
  
  loadShapeDefinitions() {
    // Instead of parsing the complex XML, I'll define key shapes based on the patterns found
    this.createBuiltInShapes();
    console.log(`📐 Loaded ${this.shapeDefinitions.size} custom geometry definitions`);
  }
  
  createBuiltInShapes() {
    // Diamond shape based on the XML definition found
    this.shapeDefinitions.set('diamond', {
      name: 'diamond',
      pathGenerator: this.generateDiamondPath,
      guideList: [
        { name: 'ir', formula: '*/ w 3 4' },
        { name: 'ib', formula: '*/ h 3 4' }
      ]
    });
    
    // Star5 shape based on the XML definition found  
    this.shapeDefinitions.set('star5', {
      name: 'star5',
      pathGenerator: this.generateStar5Path,
      guideList: [
        { name: 'a', formula: 'val 19098' },
        { name: 'swd2', formula: '*/ wd2 105146 100000' },
        { name: 'shd2', formula: '*/ hd2 110557 100000' }
      ]
    });
    
    // Down Arrow shape based on the XML definition found
    this.shapeDefinitions.set('downArrow', {
      name: 'downArrow',
      pathGenerator: this.generateDownArrowPath,
      guideList: [
        { name: 'a1', formula: 'val 50000' },
        { name: 'a2', formula: 'val 50000' }
      ]
    });
    
    // Left Arrow shape
    this.shapeDefinitions.set('leftArrow', {
      name: 'leftArrow',
      pathGenerator: this.generateLeftArrowPath,
      guideList: [
        { name: 'a1', formula: 'val 50000' },
        { name: 'a2', formula: 'val 50000' }
      ]
    });
    
    // Right Arrow shape
    this.shapeDefinitions.set('rightArrow', {
      name: 'rightArrow',
      pathGenerator: this.generateRightArrowPath,
      guideList: [
        { name: 'a1', formula: 'val 50000' },
        { name: 'a2', formula: 'val 50000' }
      ]
    });
    
    // Ellipse shape
    this.shapeDefinitions.set('ellipse', {
      name: 'ellipse',
      pathGenerator: this.generateEllipsePath,
      guideList: []
    });
    
    // Cube shape (3D effect)
    this.shapeDefinitions.set('cube', {
      name: 'cube',
      pathGenerator: this.generateCubePath,
      guideList: []
    });
    
    // Flow chart process (rectangle)
    this.shapeDefinitions.set('flowChartProcess', {
      name: 'flowChartProcess',
      pathGenerator: this.generateRectanglePath,
      guideList: []
    });
    
    // Flow chart decision (diamond)
    this.shapeDefinitions.set('flowChartDecision', {
      name: 'flowChartDecision',
      pathGenerator: this.generateDiamondPath,
      guideList: []
    });
    
    // Callout shapes
    this.shapeDefinitions.set('callout1', {
      name: 'callout1',
      pathGenerator: this.generateCalloutPath,
      guideList: []
    });
    
    // Hexagon
    this.shapeDefinitions.set('hexagon', {
      name: 'hexagon',
      pathGenerator: this.generateHexagonPath,
      guideList: []
    });
  }
  
  generateDiamondPath(coords) {
    return [
      { type: 'moveTo', x: coords.l, y: coords.vc },
      { type: 'lnTo', x: coords.hc, y: coords.t },
      { type: 'lnTo', x: coords.r, y: coords.vc },
      { type: 'lnTo', x: coords.hc, y: coords.b },
      { type: 'close' }
    ];
  }
  
  generateStar5Path(coords) {
    // 5-pointed star with outer and inner points
    const outerRadius = Math.min(coords.wd2, coords.hd2) * 0.9;
    const innerRadius = outerRadius * 0.4;
    const centerX = coords.hc;
    const centerY = coords.vc;
    
    const points = [];
    for (let i = 0; i < 10; i++) {
      const angle = (i * Math.PI) / 5 - Math.PI / 2;
      const radius = i % 2 === 0 ? outerRadius : innerRadius;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      
      if (i === 0) {
        points.push({ type: 'moveTo', x, y });
      } else {
        points.push({ type: 'lnTo', x, y });
      }
    }
    points.push({ type: 'close' });
    
    return points;
  }
  
  generateDownArrowPath(coords) {
    const arrowWidth = coords.w * 0.6;
    const arrowHeight = coords.h * 0.4;
    const stemWidth = coords.w * 0.3;
    
    const x1 = coords.hc - stemWidth / 2;
    const x2 = coords.hc + stemWidth / 2;
    const x3 = coords.hc - arrowWidth / 2;
    const x4 = coords.hc + arrowWidth / 2;
    const y1 = coords.t;
    const y2 = coords.b - arrowHeight;
    const y3 = coords.b;
    
    return [
      { type: 'moveTo', x: x1, y: y1 },
      { type: 'lnTo', x: x2, y: y1 },
      { type: 'lnTo', x: x2, y: y2 },
      { type: 'lnTo', x: x4, y: y2 },
      { type: 'lnTo', x: coords.hc, y: y3 },
      { type: 'lnTo', x: x3, y: y2 },
      { type: 'lnTo', x: x1, y: y2 },
      { type: 'close' }
    ];
  }
  
  generateLeftArrowPath(coords) {
    const arrowWidth = coords.w * 0.4;
    const arrowHeight = coords.h * 0.6;
    const stemHeight = coords.h * 0.3;
    
    const y1 = coords.vc - stemHeight / 2;
    const y2 = coords.vc + stemHeight / 2;
    const y3 = coords.vc - arrowHeight / 2;
    const y4 = coords.vc + arrowHeight / 2;
    const x1 = coords.r;
    const x2 = coords.l + arrowWidth;
    const x3 = coords.l;
    
    return [
      { type: 'moveTo', x: x1, y: y1 },
      { type: 'lnTo', x: x2, y: y1 },
      { type: 'lnTo', x: x2, y: y3 },
      { type: 'lnTo', x: x3, y: coords.vc },
      { type: 'lnTo', x: x2, y: y4 },
      { type: 'lnTo', x: x2, y: y2 },
      { type: 'lnTo', x: x1, y: y2 },
      { type: 'close' }
    ];
  }
  
  generateRightArrowPath(coords) {
    const arrowWidth = coords.w * 0.4;
    const arrowHeight = coords.h * 0.6;
    const stemHeight = coords.h * 0.3;
    
    const y1 = coords.vc - stemHeight / 2;
    const y2 = coords.vc + stemHeight / 2;
    const y3 = coords.vc - arrowHeight / 2;
    const y4 = coords.vc + arrowHeight / 2;
    const x1 = coords.l;
    const x2 = coords.r - arrowWidth;
    const x3 = coords.r;
    
    return [
      { type: 'moveTo', x: x1, y: y1 },
      { type: 'lnTo', x: x2, y: y1 },
      { type: 'lnTo', x: x2, y: y3 },
      { type: 'lnTo', x: x3, y: coords.vc },
      { type: 'lnTo', x: x2, y: y4 },
      { type: 'lnTo', x: x2, y: y2 },
      { type: 'lnTo', x: x1, y: y2 },
      { type: 'close' }
    ];
  }
  
  generateEllipsePath(coords) {
    // Approximate ellipse using cubic bezier curves
    const rx = coords.wd2;
    const ry = coords.hd2;
    const cx = coords.hc;
    const cy = coords.vc;
    
    // Magic number for approximating circle/ellipse with bezier
    const k = 0.552284749831;
    
    return [
      { type: 'moveTo', x: cx + rx, y: cy },
      { type: 'cubicBezTo', x1: cx + rx, y1: cy + ry * k, x2: cx + rx * k, y2: cy + ry, x: cx, y: cy + ry },
      { type: 'cubicBezTo', x1: cx - rx * k, y1: cy + ry, x2: cx - rx, y2: cy + ry * k, x: cx - rx, y: cy },
      { type: 'cubicBezTo', x1: cx - rx, y1: cy - ry * k, x2: cx - rx * k, y2: cy - ry, x: cx, y: cy - ry },
      { type: 'cubicBezTo', x1: cx + rx * k, y1: cy - ry, x2: cx + rx, y2: cy - ry * k, x: cx + rx, y: cy },
      { type: 'close' }
    ];
  }
  
  generateCubePath(coords) {
    // 3D cube with perspective
    const offset = Math.min(coords.w, coords.h) * 0.2;
    
    return [
      // Front face
      { type: 'moveTo', x: coords.l, y: coords.t + offset },
      { type: 'lnTo', x: coords.r - offset, y: coords.t + offset },
      { type: 'lnTo', x: coords.r - offset, y: coords.b },
      { type: 'lnTo', x: coords.l, y: coords.b },
      { type: 'close' },
      
      // Top face
      { type: 'moveTo', x: coords.l, y: coords.t + offset },
      { type: 'lnTo', x: coords.l + offset, y: coords.t },
      { type: 'lnTo', x: coords.r, y: coords.t },
      { type: 'lnTo', x: coords.r - offset, y: coords.t + offset },
      { type: 'close' },
      
      // Right face
      { type: 'moveTo', x: coords.r - offset, y: coords.t + offset },
      { type: 'lnTo', x: coords.r, y: coords.t },
      { type: 'lnTo', x: coords.r, y: coords.b - offset },
      { type: 'lnTo', x: coords.r - offset, y: coords.b },
      { type: 'close' }
    ];
  }
  
  generateRectanglePath(coords) {
    return [
      { type: 'moveTo', x: coords.l, y: coords.t },
      { type: 'lnTo', x: coords.r, y: coords.t },
      { type: 'lnTo', x: coords.r, y: coords.b },
      { type: 'lnTo', x: coords.l, y: coords.b },
      { type: 'close' }
    ];
  }
  
  generateCalloutPath(coords) {
    const calloutWidth = coords.w * 0.8;
    const calloutHeight = coords.h * 0.6;
    const tailWidth = coords.w * 0.2;
    const tailHeight = coords.h * 0.3;
    
    const x1 = coords.l + (coords.w - calloutWidth) / 2;
    const x2 = x1 + calloutWidth;
    const y1 = coords.t;
    const y2 = coords.t + calloutHeight;
    const tailX = coords.hc;
    const tailY = coords.b;
    
    return [
      { type: 'moveTo', x: x1, y: y1 },
      { type: 'lnTo', x: x2, y: y1 },
      { type: 'lnTo', x: x2, y: y2 },
      { type: 'lnTo', x: tailX + tailWidth / 2, y: y2 },
      { type: 'lnTo', x: tailX, y: tailY },
      { type: 'lnTo', x: tailX - tailWidth / 2, y: y2 },
      { type: 'lnTo', x: x1, y: y2 },
      { type: 'close' }
    ];
  }
  
  generateHexagonPath(coords) {
    const cx = coords.hc;
    const cy = coords.vc;
    const rx = coords.wd2;
    const ry = coords.hd2;
    
    const points = [];
    for (let i = 0; i < 6; i++) {
      const angle = (i * Math.PI) / 3;
      const x = cx + rx * Math.cos(angle);
      const y = cy + ry * Math.sin(angle);
      
      if (i === 0) {
        points.push({ type: 'moveTo', x, y });
      } else {
        points.push({ type: 'lnTo', x, y });
      }
    }
    points.push({ type: 'close' });
    
    return points;
  }
  
  generateCustomGeometry(shapeName, width, height, x = 0, y = 0) {
    const shapeDefinition = this.shapeDefinitions.get(shapeName);
    if (!shapeDefinition) {
      console.warn(`Shape ${shapeName} not found in definitions`);
      return this.generateRectangleGeometry(width, height, x, y);
    }
    
    try {
      // Create coordinate system variables
      const coords = this.createCoordinateSystem(width, height, x, y);
      
      // Calculate guides if they exist
      const calculatedGuides = this.calculateGuides(shapeDefinition.guideList, coords);
      const allCoords = { ...coords, ...calculatedGuides };
      
      // Generate paths using the shape's path generator
      const paths = shapeDefinition.pathGenerator(allCoords);
      
      return this.createCustomGeometryXml(paths, width, height);
    } catch (error) {
      console.warn(`Error generating custom geometry for ${shapeName}:`, error.message);
      return this.generateRectangleGeometry(width, height, x, y);
    }
  }
  
  createCoordinateSystem(width, height, x, y) {
    return {
      // Basic coordinates
      l: x,                    // left
      t: y,                    // top
      r: x + width,            // right
      b: y + height,           // bottom
      
      // Center coordinates
      hc: x + width / 2,       // horizontal center
      vc: y + height / 2,      // vertical center
      
      // Dimensions
      w: width,                // width
      h: height,               // height
      wd2: width / 2,          // width divided by 2
      hd2: height / 2,         // height divided by 2
      wd4: width / 4,          // width divided by 4
      hd4: height / 4,         // height divided by 4
      
      // Special calculations
      ss: Math.min(width, height), // smaller of width/height
      ls: Math.max(width, height)  // larger of width/height
    };
  }
  
  calculateGuides(guideList, coords) {
    if (!guideList) return {};
    
    const guides = {};
    
    // Process guides in order (some may depend on others)
    for (const guide of guideList) {
      try {
        const value = this.evaluateFormula(guide.formula, { ...coords, ...guides });
        guides[guide.name] = value;
      } catch (error) {
        console.warn(`Error calculating guide ${guide.name}:`, error.message);
        guides[guide.name] = 0;
      }
    }
    
    return guides;
  }
  
  evaluateFormula(formula, coords) {
    // Simple formula evaluator for common OpenXML formulas
    let expr = formula;
    
    // Handle val formula (direct value)
    if (expr.startsWith('val ')) {
      return parseInt(expr.substring(4));
    }
    
    // Handle multiplication formulas like "*/ w 3 4" (w * 3 / 4)
    const mulDivMatch = expr.match(/^\*\/\s+(\w+)\s+(\d+)\s+(\d+)$/);
    if (mulDivMatch) {
      const [, varName, numerator, denominator] = mulDivMatch;
      const baseValue = coords[varName] || 0;
      return (baseValue * parseInt(numerator)) / parseInt(denominator);
    }
    
    // Handle addition/subtraction formulas like "+- hc 0 dx1"
    const addSubMatch = expr.match(/^\+\-\s+(\w+)\s+(\w+|\d+)\s+(\w+|\d+)$/);
    if (addSubMatch) {
      const [, base, add, sub] = addSubMatch;
      const baseValue = coords[base] || 0;
      const addValue = coords[add] || parseInt(add) || 0;
      const subValue = coords[sub] || parseInt(sub) || 0;
      return baseValue + addValue - subValue;
    }
    
    // Handle cosine: cos swd2 1080000
    const cosMatch = expr.match(/^cos\s+(\w+)\s+(\d+)$/);
    if (cosMatch) {
      const [, radiusVar, angle] = cosMatch;
      const radius = coords[radiusVar] || 0;
      const angleRad = (parseInt(angle) * Math.PI) / 10800000; // Convert to radians
      return radius * Math.cos(angleRad);
    }
    
    // Handle sine: sin shd2 1080000
    const sinMatch = expr.match(/^sin\s+(\w+)\s+(\d+)$/);
    if (sinMatch) {
      const [, radiusVar, angle] = sinMatch;
      const radius = coords[radiusVar] || 0;
      const angleRad = (parseInt(angle) * Math.PI) / 10800000; // Convert to radians
      return radius * Math.sin(angleRad);
    }
    
    // Handle pin (clamp): pin 0 adj1 100000
    const pinMatch = expr.match(/^pin\s+(\w+|\d+)\s+(\w+|\d+)\s+(\w+|\d+)$/);
    if (pinMatch) {
      const [, minVal, value, maxVal] = pinMatch;
      const min = coords[minVal] || parseInt(minVal) || 0;
      const val = coords[value] || parseInt(value) || 0;
      const max = coords[maxVal] || parseInt(maxVal) || 0;
      return Math.max(min, Math.min(val, max));
    }
    
    // Handle max: max 0 q12
    const maxMatch = expr.match(/^max\s+(\w+|\d+)\s+(\w+|\d+)$/);
    if (maxMatch) {
      const [, val1, val2] = maxMatch;
      const v1 = coords[val1] || parseInt(val1) || 0;
      const v2 = coords[val2] || parseInt(val2) || 0;
      return Math.max(v1, v2);
    }
    
    // Fallback: return the value if it's a variable name
    if (coords[expr] !== undefined) {
      return coords[expr];
    }
    
    // Fallback: try to parse as number
    const numValue = parseInt(expr);
    return isNaN(numValue) ? 0 : numValue;
  }
  
  createCustomGeometryXml(paths, width, height) {
    if (!paths || paths.length === 0) {
      return this.generateRectangleGeometry(width, height);
    }
    
    let pathData = '';
    
    // Handle both single path and multiple paths
    const pathArray = Array.isArray(paths[0]) ? paths : [paths];
    
    for (const path of pathArray) {
      for (const command of path) {
        switch (command.type) {
          case 'moveTo':
            pathData += `<a:moveTo><a:pt x="${Math.round(command.x)}" y="${Math.round(command.y)}"/></a:moveTo>`;
            break;
          case 'lnTo':
            pathData += `<a:lnTo><a:pt x="${Math.round(command.x)}" y="${Math.round(command.y)}"/></a:lnTo>`;
            break;
          case 'cubicBezTo':
            pathData += `<a:cubicBezTo><a:pt x="${Math.round(command.x1)}" y="${Math.round(command.y1)}"/><a:pt x="${Math.round(command.x2)}" y="${Math.round(command.y2)}"/><a:pt x="${Math.round(command.x)}" y="${Math.round(command.y)}"/></a:cubicBezTo>`;
            break;
          case 'close':
            pathData += `<a:close/>`;
            break;
        }
      }
    }
    
    return `<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="0" t="0" r="${width}" b="${height}"/><a:pathLst><a:path w="${width}" h="${height}">${pathData}</a:path></a:pathLst></a:custGeom>`;
  }
  
  generateRectangleGeometry(width, height, x = 0, y = 0) {
    const pathData = `<a:moveTo><a:pt x="${x}" y="${y}"/></a:moveTo><a:lnTo><a:pt x="${x + width}" y="${y}"/></a:lnTo><a:lnTo><a:pt x="${x + width}" y="${y + height}"/></a:lnTo><a:lnTo><a:pt x="${x}" y="${y + height}"/></a:lnTo><a:close/>`;
    
    return `<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="0" t="0" r="${width}" b="${height}"/><a:pathLst><a:path w="${width}" h="${height}">${pathData}</a:path></a:pathLst></a:custGeom>`;
  }
  
  getAvailableShapes() {
    return Array.from(this.shapeDefinitions.keys());
  }
  
  getShapeInfo(shapeName) {
    return this.shapeDefinitions.get(shapeName);
  }
}