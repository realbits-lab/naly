'use client'

import { useState } from 'react'
import ChatPanel from '@/components/ChatPanel'
import CanvasPanel from '@/components/CanvasPanel'

export default function Home() {
  const [generatedDiagram, setGeneratedDiagram] = useState<any>(null)

  const handleDiagramGenerated = (diagram: any) => {
    setGeneratedDiagram(diagram)
  }

  return (
    <main className="flex flex-col h-screen bg-gray-50">
      <div className="h-1/3 bg-white border-b border-gray-200">
        <ChatPanel onDiagramGenerated={handleDiagramGenerated} />
      </div>
      <div className="h-2/3 bg-gray-50">
        <CanvasPanel diagram={generatedDiagram} />
      </div>
    </main>
  )
}