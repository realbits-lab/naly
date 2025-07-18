'use client'

import { useEffect, useRef, useState } from 'react'
import * as fabric from 'fabric'
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

    console.log('Initializing Fabric.js canvas')
    // Initialize Fabric.js canvas
    const canvas = new fabric.Canvas(canvasRef.current, {
      width: 800,
      height: 600,
      backgroundColor: '#ffffff'
    })

    fabricCanvasRef.current = canvas
    setIsReady(true)
    console.log('Canvas initialized successfully')

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

    console.log('CanvasPanel received diagram:', diagram)
    const canvas = fabricCanvasRef.current
    canvas.clear()

    // Handle different diagram types
    if (diagram.type === 'mermaid') {
      renderMermaidDiagram(diagram.content)
    } else if (diagram.type === 'shapes') {
      console.log('Rendering shapes diagram with content:', diagram.content)
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
          // Ensure objects is always an array
          const groupObjects = Array.isArray(objects) ? objects : [objects]
          const group = new fabric.Group(groupObjects as any[], options)
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
    console.log('renderShapeDiagram called with shapes:', shapes)
    if (!fabricCanvasRef.current) {
      console.log('No fabric canvas reference')
      return
    }

    const canvas = fabricCanvasRef.current
    console.log('Canvas reference found, adding shapes')
    
    shapes.forEach((shape, index) => {
      console.log('Processing shape:', shape)
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
        console.log('Adding fabric object to canvas:', fabricObject)
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

    console.log('Rendering canvas')
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
      <div className="p-4 border-b bg-white">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg flex items-center justify-center">
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-semibold">Canvas</h2>
            <p className="text-sm text-muted-foreground">
              Your generated diagram will appear here
            </p>
          </div>
        </div>
      </div>
      
      <div className="flex-1 p-4 overflow-auto">
        <div className="w-full h-full flex items-center justify-center">
          <canvas
            ref={canvasRef}
            className="border border-gray-300 rounded-lg shadow-sm"
            width={800}
            height={600}
          />
        </div>
      </div>
    </div>
  )
}