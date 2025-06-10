'use client'

import { useRef } from 'react'
import {
  ButtonBackgroundShine,
  ButtonAnimatedGradient,
  ButtonHoverRight,
  AnimatedBeam,
  SpotlightCard,
  MouseTrail,
  Marquee,
} from '@/components/ui-layouts'

export default function UILayoutsDemo() {
  const containerRef = useRef<HTMLDivElement>(null)
  const div1Ref = useRef<HTMLDivElement>(null)
  const div2Ref = useRef<HTMLDivElement>(null)

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black p-8">
      <div className="max-w-6xl mx-auto space-y-16">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-white mb-4">
            UI Layouts Components Demo
          </h1>
          <p className="text-gray-300 text-lg">
            A showcase of beautiful, interactive React components from ui-layouts
          </p>
        </div>

        {/* Buttons Section */}
        <section className="space-y-8">
          <h2 className="text-2xl font-semibold text-white mb-6">Animated Buttons</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center space-y-4">
              <h3 className="text-lg text-gray-300">Background Shine</h3>
              <ButtonBackgroundShine>
                Hover Me
              </ButtonBackgroundShine>
            </div>
            <div className="text-center space-y-4">
              <h3 className="text-lg text-gray-300">Animated Gradient</h3>
              <ButtonAnimatedGradient>
                Move Mouse
              </ButtonAnimatedGradient>
            </div>
            <div className="text-center space-y-4">
              <h3 className="text-lg text-gray-300">Hover Right</h3>
              <ButtonHoverRight>
                Expand
              </ButtonHoverRight>
            </div>
          </div>
        </section>

        {/* Animated Beam Section */}
        <section className="space-y-8">
          <h2 className="text-2xl font-semibold text-white mb-6">Animated Beam</h2>
          <div 
            ref={containerRef}
            className="relative flex h-64 w-full items-center justify-between rounded-lg border border-gray-700 bg-gray-900/50 p-8"
          >
            <div 
              ref={div1Ref}
              className="flex h-16 w-16 items-center justify-center rounded-full bg-blue-500"
            >
              <span className="text-white font-semibold">A</span>
            </div>
            <div 
              ref={div2Ref}
              className="flex h-16 w-16 items-center justify-center rounded-full bg-purple-500"
            >
              <span className="text-white font-semibold">B</span>
            </div>
            <AnimatedBeam
              containerRef={containerRef}
              fromRef={div1Ref}
              toRef={div2Ref}
              curvature={50}
              gradientStartColor="#3b82f6"
              gradientStopColor="#8b5cf6"
            />
          </div>
        </section>

        {/* Spotlight Cards Section */}
        <section className="space-y-8">
          <h2 className="text-2xl font-semibold text-white mb-6">Spotlight Cards</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <SpotlightCard>
              <h3 className="text-xl font-semibold text-white mb-2">Card 1</h3>
              <p className="text-gray-300">
                Move your mouse over this card to see the spotlight effect in action.
              </p>
            </SpotlightCard>
            <SpotlightCard spotlightColor="rgba(59, 130, 246, 0.3)">
              <h3 className="text-xl font-semibold text-white mb-2">Card 2</h3>
              <p className="text-gray-300">
                This card has a blue spotlight color. Each card can have different colors.
              </p>
            </SpotlightCard>
            <SpotlightCard spotlightColor="rgba(139, 92, 246, 0.3)">
              <h3 className="text-xl font-semibold text-white mb-2">Card 3</h3>
              <p className="text-gray-300">
                This card has a purple spotlight. The effect follows your cursor precisely.
              </p>
            </SpotlightCard>
          </div>
        </section>

        {/* Mouse Trail Section */}
        <section className="space-y-8">
          <h2 className="text-2xl font-semibold text-white mb-6">Mouse Trail</h2>
          <MouseTrail className="rounded-lg border border-gray-700 bg-gray-900/50 p-12">
            <div className="text-center space-y-4">
              <h3 className="text-xl font-semibold text-white">
                Move your mouse around this area
              </h3>
              <p className="text-gray-300">
                You'll see a trail of dots following your cursor with a smooth fade effect.
              </p>
            </div>
          </MouseTrail>
        </section>

        {/* Marquee Section */}
        <section className="space-y-8">
          <h2 className="text-2xl font-semibold text-white mb-6">Marquee</h2>
          <div className="space-y-6">
            <div>
              <h3 className="text-lg text-gray-300 mb-4">Horizontal Marquee</h3>
              <Marquee className="rounded-lg border border-gray-700 bg-gray-900/50">
                {Array.from({ length: 10 }, (_, i) => (
                  <div
                    key={i}
                    className="flex h-16 w-32 items-center justify-center rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 text-white font-semibold"
                  >
                    Item {i + 1}
                  </div>
                ))}
              </Marquee>
            </div>
            
            <div>
              <h3 className="text-lg text-gray-300 mb-4">Reverse Marquee (Hover to Pause)</h3>
              <Marquee 
                reverse 
                pauseOnHover 
                className="rounded-lg border border-gray-700 bg-gray-900/50"
              >
                {Array.from({ length: 8 }, (_, i) => (
                  <div
                    key={i}
                    className="flex h-16 w-32 items-center justify-center rounded-lg bg-gradient-to-r from-green-500 to-blue-500 text-white font-semibold"
                  >
                    Rev {i + 1}
                  </div>
                ))}
              </Marquee>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="text-center py-8">
          <p className="text-gray-400">
            Components from{' '}
            <a 
              href="https://ui-layouts.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300 transition-colors"
            >
              ui-layouts.com
            </a>
          </p>
        </footer>
      </div>
    </div>
  )
} 