'use client'

import { useEffect, useRef, useState } from 'react'
import { fabric } from 'fabric'
import mermaid from 'mermaid'

interface CanvasPanelProps {
  diagram: any
}

export default function CanvasPanel({ diagram }: CanvasPanelProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const fabricCanvasRef = useRef<fabric.Canvas | null>(null)
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    if (!canvasRef.current) return

    // Initialize Fabric.js canvas
    const canvas = new fabric.Canvas(canvasRef.current, {
      width: 800,
      height: 600,
      backgroundColor: '#ffffff'
    })

    fabricCanvasRef.current = canvas
    setIsReady(true)

    // Initialize Mermaid
    mermaid.initialize({ 
      startOnLoad: true,
      theme: 'default',
      securityLevel: 'loose',
    })

    return () => {
      canvas.dispose()
    }
  }, [])

  useEffect(() => {
    if (!diagram || !fabricCanvasRef.current || !isReady) return

    const canvas = fabricCanvasRef.current
    canvas.clear()

    // Handle different diagram types
    if (diagram.type === 'mermaid') {
      renderMermaidDiagram(diagram.content)
    } else if (diagram.type === 'shapes') {
      renderShapeDiagram(diagram.content)
    } else if (diagram.type === 'flowchart') {
      renderFlowchartDiagram(diagram.content)
    }
  }, [diagram, isReady])

  const renderMermaidDiagram = async (content: string) => {
    try {
      const { svg } = await mermaid.render('mermaid-diagram', content)
      
      // Convert SVG to Fabric.js object
      fabric.loadSVGFromString(svg, (objects, options) => {
        if (fabricCanvasRef.current) {
          const group = new fabric.Group(objects, options)
          group.set({
            left: 100,
            top: 100,
            scaleX: 0.8,
            scaleY: 0.8
          })
          fabricCanvasRef.current.add(group)
          fabricCanvasRef.current.renderAll()
        }
      })
    } catch (error) {
      console.error('Error rendering Mermaid diagram:', error)
    }
  }

  const renderShapeDiagram = (shapes: any[]) => {
    if (!fabricCanvasRef.current) return

    const canvas = fabricCanvasRef.current
    
    shapes.forEach((shape, index) => {
      let fabricObject: fabric.Object | null = null

      switch (shape.type) {
        case 'rectangle':
          fabricObject = new fabric.Rect({
            left: shape.x || 50 + index * 120,
            top: shape.y || 50 + index * 80,
            width: shape.width || 100,
            height: shape.height || 60,
            fill: shape.fill || '#3b82f6',
            stroke: shape.stroke || '#1e40af',
            strokeWidth: 2
          })
          break
        case 'circle':
          fabricObject = new fabric.Circle({
            left: shape.x || 50 + index * 120,
            top: shape.y || 50 + index * 80,
            radius: shape.radius || 40,
            fill: shape.fill || '#10b981',
            stroke: shape.stroke || '#059669',
            strokeWidth: 2
          })
          break
        case 'triangle':
          fabricObject = new fabric.Triangle({
            left: shape.x || 50 + index * 120,
            top: shape.y || 50 + index * 80,
            width: shape.width || 80,
            height: shape.height || 70,
            fill: shape.fill || '#f59e0b',
            stroke: shape.stroke || '#d97706',
            strokeWidth: 2
          })
          break
        case 'text':
          fabricObject = new fabric.Text(shape.text || 'Text', {
            left: shape.x || 50 + index * 120,
            top: shape.y || 50 + index * 80,
            fontSize: shape.fontSize || 16,
            fill: shape.fill || '#1f2937',
            fontFamily: 'Arial'
          })
          break
      }

      if (fabricObject) {
        canvas.add(fabricObject)
        
        // Add text label if specified
        if (shape.text && shape.type !== 'text') {
          const text = new fabric.Text(shape.text, {
            left: (fabricObject.left || 0) + (fabricObject.width || 0) / 2,
            top: (fabricObject.top || 0) + (fabricObject.height || 0) / 2,
            fontSize: 12,
            fill: '#ffffff',
            fontFamily: 'Arial',
            textAlign: 'center',
            originX: 'center',
            originY: 'center'
          })
          canvas.add(text)
        }
      }
    })

    canvas.renderAll()
  }

  const renderFlowchartDiagram = (flowchart: any) => {
    if (!fabricCanvasRef.current) return

    const canvas = fabricCanvasRef.current
    const { nodes, connections } = flowchart

    // Draw nodes
    nodes.forEach((node: any) => {
      let shape: fabric.Object | null = null

      switch (node.shape) {
        case 'start':
        case 'end':
          shape = new fabric.Ellipse({
            left: node.x,
            top: node.y,
            rx: 60,
            ry: 30,
            fill: node.shape === 'start' ? '#10b981' : '#ef4444',
            stroke: '#000',
            strokeWidth: 2
          })
          break
        case 'process':
          shape = new fabric.Rect({
            left: node.x,
            top: node.y,
            width: 120,
            height: 60,
            fill: '#3b82f6',
            stroke: '#000',
            strokeWidth: 2
          })
          break
        case 'decision':
          const points = [
            { x: node.x + 60, y: node.y },
            { x: node.x + 120, y: node.y + 30 },
            { x: node.x + 60, y: node.y + 60 },
            { x: node.x, y: node.y + 30 }
          ]
          shape = new fabric.Polygon(points, {
            fill: '#f59e0b',
            stroke: '#000',
            strokeWidth: 2
          })
          break
      }

      if (shape) {
        canvas.add(shape)
        
        // Add text label
        const text = new fabric.Text(node.label, {
          left: node.x + 60,
          top: node.y + 30,
          fontSize: 12,
          fill: '#ffffff',
          fontFamily: 'Arial',
          textAlign: 'center',
          originX: 'center',
          originY: 'center'
        })
        canvas.add(text)
      }
    })

    // Draw connections
    connections.forEach((conn: any) => {
      const fromNode = nodes.find((n: any) => n.id === conn.from)
      const toNode = nodes.find((n: any) => n.id === conn.to)
      
      if (fromNode && toNode) {
        const line = new fabric.Line([
          fromNode.x + 60, fromNode.y + 60,
          toNode.x + 60, toNode.y
        ], {
          stroke: '#000',
          strokeWidth: 2
        })
        canvas.add(line)
        
        // Add arrow head
        const angle = Math.atan2(toNode.y - fromNode.y, toNode.x - fromNode.x)
        const arrowHead = new fabric.Triangle({
          left: toNode.x + 60,
          top: toNode.y,
          width: 10,
          height: 10,
          fill: '#000',
          angle: (angle * 180) / Math.PI + 90,
          originX: 'center',
          originY: 'center'
        })
        canvas.add(arrowHead)
      }
    })

    canvas.renderAll()
  }

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold">Canvas</h2>
        <p className="text-sm text-muted-foreground">
          Your generated diagram will appear here
        </p>
      </div>
      
      <div className="flex-1 p-4 overflow-auto">
        <div className="w-full h-full flex items-center justify-center">
          {!diagram ? (
            <div className="text-center text-muted-foreground">
              <p>No diagram generated yet</p>
              <p className="text-sm mt-2">
                Start by describing your diagram in the chat panel
              </p>
            </div>
          ) : (
            <canvas
              ref={canvasRef}
              className="border border-gray-300 rounded-lg shadow-sm"
            />
          )}
        </div>
      </div>
    </div>
  )
}