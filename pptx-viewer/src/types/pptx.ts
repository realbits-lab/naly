export interface ColorInfo {
  type?: string;
  rgb?: {
    hex: string;
    red: number;
    green: number;
    blue: number;
  };
  theme_color?: string;
  brightness?: number;
  tint_and_shade?: number;
  error?: string;
}

export interface FillInfo {
  type?: string;
  solid?: boolean;
  pattern?: boolean;
  gradient?: boolean;
  picture?: boolean;
  background?: boolean;
  fore_color?: ColorInfo;
  back_color?: ColorInfo;
  gradient_stops?: Array<{
    position: number;
    color: ColorInfo;
  }>;
  gradient_angle?: number;
  error?: string;
}

export interface LineInfo {
  width?: number;
  color?: ColorInfo;
  fill?: FillInfo;
  error?: string;
}

export interface TextRun {
  text: string;
  font_name?: string;
  font_size?: number;
  bold?: boolean;
  italic?: boolean;
  underline?: string;
  color?: ColorInfo;
}

export interface TextParagraph {
  text: string;
  alignment?: string;
  level?: number;
  space_before?: number;
  space_after?: number;
  line_spacing?: number;
  runs: TextRun[];
}

export interface TextFrame {
  margin_left?: number;
  margin_right?: number;
  margin_top?: number;
  margin_bottom?: number;
  word_wrap?: boolean;
  auto_size?: string;
  vertical_anchor?: string;
  paragraphs: TextParagraph[];
  error?: string;
}

export interface PathCommand {
  command: string;
  x?: string;
  y?: string;
  points?: Array<{ x: string; y: string }>;
}

export interface CustomGeometryPath {
  width?: string;
  height?: string;
  commands?: PathCommand[];
}

export interface CustomGeometry {
  paths?: CustomGeometryPath[];
}

export interface ShapeElement {
  xml_string?: string;
}

export interface Shape {
  slide_index: number;
  shape_index: number;
  shape_id?: number;
  name?: string;
  shape_type: string;
  left?: number;
  top?: number;
  width?: number;
  height?: number;
  rotation?: number;
  fill?: FillInfo;
  line?: LineInfo;
  text?: string;
  text_frame?: TextFrame;
  has_text_frame?: boolean;
  is_placeholder?: boolean;
  chart_data?: any;
  table_data?: any;
  image_properties?: any;
  shadow?: any;
  placeholder_format?: any;
  custom_geometry?: CustomGeometry;
  element?: ShapeElement;
  auto_shape_type?: string;
  adjustments?: number[];
}

export interface SlideData {
  slide_index: number;
  shapes: Shape[];
}

export interface Layout {
  layout_index: number;
  name: string;
  placeholders: Array<{
    placeholder_format: string;
    name: string;
    left: number;
    top: number;
    width: number;
    height: number;
  }>;
  background?: any;
}

export interface ColorScheme {
  [key: string]: {
    rgb: string;
    type: string;
  };
}

export interface FontScheme {
  major_font: {
    latin?: string;
    ea?: string;
    cs?: string;
  };
  minor_font: {
    latin?: string;
    ea?: string;
    cs?: string;
  };
  error?: string;
}

export interface Theme {
  slide_master: {
    name: string;
    width?: number;
    height?: number;
    background?: any;
    placeholders: Array<{
      placeholder_type?: string;
      name?: string;
      left?: number;
      top?: number;
      width?: number;
      height?: number;
    }>;
  };
  color_scheme: ColorScheme;
  font_scheme: FontScheme;
  theme_name: string;
  effect_scheme?: any;
}

export interface MediaFile {
  filename: string;
  size: number;
  data: string;
}

export interface MediaData {
  images: { [key: string]: MediaFile };
  audio: { [key: string]: MediaFile };
  video: { [key: string]: MediaFile };
  embedded_objects: { [key: string]: MediaFile };
  fonts: { [key: string]: MediaFile };
}

export interface DocumentProperties {
  core_properties?: {
    title?: string;
    author?: string;
    subject?: string;
    keywords?: string;
    comments?: string;
    category?: string;
    created?: string;
    modified?: string;
    last_modified_by?: string;
    revision?: string;
    version?: string;
  };
  slide_size?: {
    width: number;
    height: number;
  };
  error?: string;
}

export interface PowerPointData {
  shapes: SlideData[];
  layouts: Layout[];
  theme: Theme;
  media: MediaData;
  properties: DocumentProperties;
}