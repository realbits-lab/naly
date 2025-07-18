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
    <main className="flex h-screen bg-gray-100">
      <div className="w-[200px] bg-white border-r border-gray-200">
        <ChatPanel onDiagramGenerated={handleDiagramGenerated} />
      </div>
      <div className="flex-1 bg-gray-50">
        <CanvasPanel diagram={generatedDiagram} />
      </div>
    </main>
  )
}