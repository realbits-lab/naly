'use client'

import { cn } from './lib/utils'
import React, { forwardRef, useEffect, useId, useRef, useState } from 'react'

export interface AnimatedBeamProps {
  className?: string
  containerRef: React.RefObject<HTMLElement>
  fromRef: React.RefObject<HTMLElement>
  toRef: React.RefObject<HTMLElement>
  curvature?: number
  reverse?: boolean
  pathColor?: string
  pathWidth?: number
  pathOpacity?: number
  gradientStartColor?: string
  gradientStopColor?: string
  delay?: number
  duration?: number
  startXOffset?: number
  startYOffset?: number
  endXOffset?: number
  endYOffset?: number
}

export const AnimatedBeam = forwardRef<SVGSVGElement, AnimatedBeamProps>(
  (
    {
      className,
      containerRef,
      fromRef,
      toRef,
      curvature = 0,
      reverse = false,
      duration = Math.random() * 3 + 4,
      delay = 0,
      pathColor = 'gray',
      pathWidth = 2,
      pathOpacity = 0.2,
      gradientStartColor = '#ffaa40',
      gradientStopColor = '#9c40ff',
      startXOffset = 0,
      startYOffset = 0,
      endXOffset = 0,
      endYOffset = 0,
    },
    ref
  ) => {
    const id = useId()
    const [pathD, setPathD] = useState('')
    const svgRef = useRef<SVGSVGElement>(null)

    useEffect(() => {
      const updatePath = () => {
        if (containerRef.current && fromRef.current && toRef.current) {
          const containerRect = containerRef.current.getBoundingClientRect()
          const rectA = fromRef.current.getBoundingClientRect()
          const rectB = toRef.current.getBoundingClientRect()

          const svgTop = containerRect.top
          const svgLeft = containerRect.left

          const startX =
            rectA.left - svgLeft + rectA.width / 2 + startXOffset
          const startY =
            rectA.top - svgTop + rectA.height / 2 + startYOffset
          const endX = rectB.left - svgLeft + rectB.width / 2 + endXOffset
          const endY = rectB.top - svgTop + rectB.height / 2 + endYOffset

          const controlPointX = startX + curvature
          const controlPointY = startY + curvature

          const d = `M ${startX},${startY} Q ${controlPointX},${controlPointY} ${endX},${endY}`
          setPathD(d)
        }
      }

      const resizeObserver = new ResizeObserver((entries) => {
        for (let entry of entries) {
          updatePath()
        }
      })

      if (containerRef.current) {
        resizeObserver.observe(containerRef.current)
      }

      updatePath()

      return () => {
        resizeObserver.disconnect()
      }
    }, [
      containerRef,
      fromRef,
      toRef,
      curvature,
      startXOffset,
      startYOffset,
      endXOffset,
      endYOffset,
    ])

    return (
      <svg
        ref={ref || svgRef}
        fill="none"
        width="100%"
        height="100%"
        className={cn(
          'pointer-events-none absolute left-0 top-0 transform-gpu stroke-2',
          className
        )}
        viewBox={`0 0 ${containerRef.current?.offsetWidth || 800} ${
          containerRef.current?.offsetHeight || 600
        }`}
      >
        <defs>
          <linearGradient
            className={cn('transform-gpu')}
            id={id}
            gradientUnits="userSpaceOnUse"
            gradientTransform={
              reverse
                ? 'rotate(180, 400, 300)'
                : undefined
            }
          >
            <stop offset="0%" stopColor={gradientStartColor} stopOpacity="0" />
            <stop offset="50%" stopColor={gradientStartColor} />
            <stop offset="100%" stopColor={gradientStopColor} stopOpacity="0" />
            <animateTransform
              attributeName="gradientTransform"
              attributeType="XML"
              type="translate"
              dur={`${duration}s`}
              values={reverse ? '0,0;-200,0;0,0' : '0,0;200,0;0,0'}
              repeatCount="indefinite"
              begin={`${delay}s`}
            />
          </linearGradient>
        </defs>
        <path
          d={pathD}
          stroke={pathColor}
          strokeWidth={pathWidth}
          strokeOpacity={pathOpacity}
          strokeLinecap="round"
        />
        <path
          d={pathD}
          strokeWidth={pathWidth}
          stroke={`url(#${id})`}
          strokeOpacity="1"
          strokeLinecap="round"
        />
      </svg>
    )
  }
)

AnimatedBeam.displayName = 'AnimatedBeam' 