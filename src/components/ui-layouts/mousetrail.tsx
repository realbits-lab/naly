'use client'

import React, { useCallback, useEffect, useRef, useState } from 'react'
import { cn } from './lib/utils'

interface MouseTrailProps {
  children: React.ReactNode
  className?: string
  size?: number
  delay?: number
  duration?: number
  ease?: string
  color?: string
}

interface MousePosition {
  x: number
  y: number
}

export default function MouseTrail({
  children,
  className,
  size = 6,
  delay = 0.1,
  duration = 0.2,
  ease = 'ease-out',
  color = 'rgba(255, 255, 255, 0.4)',
}: MouseTrailProps) {
  const [trails, setTrails] = useState<MousePosition[]>([])
  const containerRef = useRef<HTMLDivElement>(null)

  const addTrail = useCallback(
    (x: number, y: number) => {
      const newTrail = { x, y }
      setTrails((prevTrails) => {
        const updatedTrails = [...prevTrails, newTrail]
        if (updatedTrails.length > 20) {
          updatedTrails.shift()
        }
        return updatedTrails
      })

      setTimeout(() => {
        setTrails((prevTrails) => prevTrails.filter((trail) => trail !== newTrail))
      }, duration * 1000)
    },
    [duration]
  )

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect()
        const x = e.clientX - rect.left
        const y = e.clientY - rect.top
        
        setTimeout(() => {
          addTrail(x, y)
        }, delay * 1000)
      }
    },
    [addTrail, delay]
  )

  useEffect(() => {
    const container = containerRef.current
    if (container) {
      container.addEventListener('mousemove', handleMouseMove)
      return () => {
        container.removeEventListener('mousemove', handleMouseMove)
      }
    }
  }, [handleMouseMove])

  return (
    <div
      ref={containerRef}
      className={cn('relative overflow-hidden', className)}
    >
      {children}
      {trails.map((trail, index) => (
        <div
          key={`${trail.x}-${trail.y}-${index}`}
          className="pointer-events-none absolute rounded-full"
          style={{
            left: trail.x - size / 2,
            top: trail.y - size / 2,
            width: size,
            height: size,
            backgroundColor: color,
            opacity: 1 - index / trails.length,
            transition: `opacity ${duration}s ${ease}`,
            zIndex: 10,
          }}
        />
      ))}
    </div>
  )
} 