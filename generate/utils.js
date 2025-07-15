import JSZip from 'jszip';
import fs from 'fs';
import path from 'path';

export class PptxUtils {
  static async unzipPptx(pptxPath, outputDir) {
    try {
      const data = fs.readFileSync(pptxPath);
      const zip = new JSZip();
      const content = await zip.loadAsync(data);
      
      // Create output directory if it doesn't exist
      if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
      }
      
      // Extract all files
      const files = {};
      for (const [relativePath, file] of Object.entries(content.files)) {
        if (!file.dir) {
          const filePath = path.join(outputDir, relativePath);
          const dirPath = path.dirname(filePath);
          
          // Create directory if it doesn't exist
          if (!fs.existsSync(dirPath)) {
            fs.mkdirSync(dirPath, { recursive: true });
          }
          
          // Extract file content
          const fileContent = await file.async('string');
          fs.writeFileSync(filePath, fileContent);
          files[relativePath] = fileContent;
        }
      }
      
      return files;
    } catch (error) {
      console.error('Error unzipping PPTX:', error);
      throw error;
    }
  }
  
  static async zipToPptx(sourceDir, outputPath) {
    try {
      const zip = new JSZip();
      
      // Recursively add files to zip
      const addFilesToZip = (dirPath, relativePath = '') => {
        const files = fs.readdirSync(dirPath);
        
        files.forEach(file => {
          const filePath = path.join(dirPath, file);
          const zipPath = relativePath ? `${relativePath}/${file}` : file;
          
          if (fs.statSync(filePath).isDirectory()) {
            addFilesToZip(filePath, zipPath);
          } else {
            const fileContent = fs.readFileSync(filePath);
            zip.file(zipPath, fileContent);
          }
        });
      };
      
      addFilesToZip(sourceDir);
      
      // Generate zip file
      const zipBuffer = await zip.generateAsync({ type: 'nodebuffer' });
      fs.writeFileSync(outputPath, zipBuffer);
      
      return outputPath;
    } catch (error) {
      console.error('Error zipping to PPTX:', error);
      throw error;
    }
  }
  
  static findSlide1Path(files) {
    const slide1Path = 'ppt/slides/slide1.xml';
    return files[slide1Path] ? slide1Path : null;
  }
  
  static generateShapeXml(shapeData) {
    const { id, name, x, y, width, height, text, type = 'textBox' } = shapeData;
    
    // Basic shape template with text
    const shapeXml = `
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="${id}" name="${name}"/>
          <p:cNvSpPr/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="${x}" y="${y}"/>
            <a:ext cx="${width}" cy="${height}"/>
          </a:xfrm>
          <a:prstGeom prst="rect">
            <a:avLst/>
          </a:prstGeom>
          <a:solidFill>
            <a:srgbClr val="E6E6FA"/>
          </a:solidFill>
          <a:ln w="12700">
            <a:solidFill>
              <a:srgbClr val="000000"/>
            </a:solidFill>
          </a:ln>
        </p:spPr>
        <p:txBody>
          <a:bodyPr/>
          <a:lstStyle/>
          <a:p>
            <a:r>
              <a:rPr lang="en-US" sz="1800"/>
              <a:t>${text}</a:t>
            </a:r>
          </a:p>
        </p:txBody>
      </p:sp>`;
    
    return shapeXml;
  }
  
  static injectShapeIntoSlide(slideXml, shapeXml) {
    // Find the spTree closing tag and insert the shape before it
    const spTreeClosingTag = '</p:spTree>';
    const insertIndex = slideXml.indexOf(spTreeClosingTag);
    
    if (insertIndex === -1) {
      throw new Error('Cannot find spTree element in slide XML');
    }
    
    // Insert the shape XML before the closing spTree tag
    const modifiedSlideXml = slideXml.slice(0, insertIndex) + shapeXml + slideXml.slice(insertIndex);
    
    return modifiedSlideXml;
  }
}