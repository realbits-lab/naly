import { NextRequest, NextResponse } from 'next/server'
import { generateObject } from 'ai'
import { google } from '@ai-sdk/google'
import { z } from 'zod'

// Define the diagram schema
const diagramSchema = z.object({
  type: z.enum(['mermaid', 'shapes', 'flowchart']),
  description: z.string(),
  content: z.union([
    z.string(), // for mermaid
    z.array(z.object({
      type: z.enum(['rectangle', 'circle', 'triangle', 'text']),
      x: z.number().optional(),
      y: z.number().optional(),
      width: z.number().optional(),
      height: z.number().optional(),
      radius: z.number().optional(),
      text: z.string().optional(),
      fill: z.string().optional(),
      stroke: z.string().optional(),
      fontSize: z.number().optional()
    })), // for shapes
    z.object({
      nodes: z.array(z.object({
        id: z.string(),
        label: z.string(),
        shape: z.enum(['start', 'end', 'process', 'decision']),
        x: z.number(),
        y: z.number()
      })),
      connections: z.array(z.object({
        from: z.string(),
        to: z.string(),
        label: z.string().optional()
      }))
    }) // for flowchart
  ])
})

export async function POST(request: NextRequest) {
  try {
    const { prompt } = await request.json()

    if (!prompt) {
      return NextResponse.json({ error: 'Prompt is required' }, { status: 400 })
    }

    // Check if Google AI API key is available
    if (!process.env.GOOGLE_API_KEY) {
      return NextResponse.json({ error: 'Google AI API key not configured' }, { status: 500 })
    }

    const model = google('gemini-1.5-flash')

    const result = await generateObject({
      model,
      schema: diagramSchema,
      prompt: `Create a diagram based on this description: "${prompt}". 
      
      Choose the most appropriate diagram type:
      - Use 'mermaid' for complex flowcharts, sequence diagrams, or process flows
      - Use 'shapes' for simple geometric diagrams, org charts, or basic layouts
      - Use 'flowchart' for decision trees or step-by-step processes
      
      For mermaid diagrams, provide valid Mermaid syntax.
      For shapes, provide an array of shape objects with proper positioning.
      For flowchart, provide nodes and connections with proper positioning.
      
      Make sure the diagram is visually appealing and represents the user's request accurately.
      Use appropriate colors and positioning to create a professional-looking diagram.`,
    })

    return NextResponse.json({
      diagram: result.object,
      description: result.object.description
    })

  } catch (error) {
    console.error('Error generating diagram:', error)
    return NextResponse.json(
      { error: 'Failed to generate diagram' },
      { status: 500 }
    )
  }
}