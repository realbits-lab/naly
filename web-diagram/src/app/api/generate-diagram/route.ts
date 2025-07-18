import { NextRequest, NextResponse } from 'next/server'
import { GoogleGenerativeAI } from '@google/generative-ai'

export async function POST(request: NextRequest) {
  try {
    console.log('API route called')
    const { prompt } = await request.json()
    console.log('Prompt received:', prompt)

    if (!prompt) {
      console.log('No prompt provided')
      return NextResponse.json({ error: 'Prompt is required' }, { status: 400 })
    }

    // Check if Google AI API key is available
    if (!process.env.GOOGLE_API_KEY) {
      console.log('Google API key not found')
      return NextResponse.json({ error: 'Google AI API key not configured' }, { status: 500 })
    }

    console.log('Google API key found, initializing model')
    
    try {
      const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY)
      const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' })
      console.log('Model initialized successfully')
      
      console.log('Generating text with AI')
      const result = await model.generateContent(`Create a simple diagram description for: "${prompt}". Return a JSON object with type: "shapes" and content: an array of 2-3 simple shapes like rectangles or circles.`)
      const response = await result.response
      const text = response.text()
      
      console.log('AI generation successful:', text)
      
      // Parse the result as JSON
      try {
        // Extract JSON from the response (it might be wrapped in markdown code blocks)
        const jsonMatch = text.match(/```json\s*([\s\S]*?)\s*```/) || text.match(/\{[\s\S]*\}/)
        const jsonString = jsonMatch ? jsonMatch[1] || jsonMatch[0] : text
        const diagramData = JSON.parse(jsonString)
        
        // Ensure the diagram data has the correct format
        const formattedDiagram = {
          type: diagramData.type || 'shapes',
          content: (diagramData.content || diagramData.shapes || []).map((shape: any) => ({
            ...shape,
            type: shape.type || shape.shape || 'rectangle'
          }))
        }
        
        return NextResponse.json({
          diagram: formattedDiagram,
          description: `Generated diagram for: ${prompt}`
        })
      } catch (parseError) {
        console.log('Failed to parse AI response as JSON, returning fallback response')
        return NextResponse.json({
          diagram: {
            type: 'shapes',
            content: [
              {
                type: 'rectangle',
                x: 50,
                y: 50,
                width: 100,
                height: 60,
                fill: '#3b82f6',
                text: 'Generated'
              }
            ]
          },
          description: text
        })
      }
    } catch (modelError) {
      console.error('Error with Google AI model:', modelError)
      throw modelError
    }

  } catch (error) {
    console.error('Error generating diagram:', error)
    console.error('Error details:', {
      name: error instanceof Error ? error.name : 'Unknown',
      message: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : 'No stack trace'
    })
    return NextResponse.json(
      { error: 'Failed to generate diagram' },
      { status: 500 }
    )
  }
}