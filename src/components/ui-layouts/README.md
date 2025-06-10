# UI Layouts Components

This directory contains a collection of beautiful, interactive React components inspired by [ui-layouts.com](https://ui-layouts.com). These components are designed to work seamlessly with Tailwind CSS and Framer Motion.

## 🚀 Quick Start

```tsx
import { 
  ButtonBackgroundShine, 
  SpotlightCard, 
  AnimatedBeam 
} from '@/components/ui-layouts'

// Use in your components
<ButtonBackgroundShine>Click Me</ButtonBackgroundShine>
```

## 📦 Components

### Buttons

#### ButtonBackgroundShine
A button with an animated background shine effect.

```tsx
<ButtonBackgroundShine className="w-32">
  Shine Button
</ButtonBackgroundShine>
```

#### ButtonAnimatedGradient
Interactive button with gradient that follows mouse movement.

```tsx
<ButtonAnimatedGradient>
  Gradient Button
</ButtonAnimatedGradient>
```

#### ButtonHoverRight
Expandable button that reveals text on hover.

```tsx
<ButtonHoverRight>
  Visit
</ButtonHoverRight>
```

### Interactive Components

#### SpotlightCard
Card component with a spotlight effect that follows the cursor.

```tsx
<SpotlightCard 
  spotlightColor="rgba(59, 130, 246, 0.3)"
  className="p-6"
>
  <h3>Card Title</h3>
  <p>Card content here...</p>
</SpotlightCard>
```

**Props:**
- `spotlightColor?: string` - Color of the spotlight effect
- `className?: string` - Additional CSS classes
- `children: React.ReactNode` - Card content

#### AnimatedBeam
Creates animated connecting lines between elements.

```tsx
const containerRef = useRef<HTMLDivElement>(null)
const fromRef = useRef<HTMLDivElement>(null)
const toRef = useRef<HTMLDivElement>(null)

<div ref={containerRef} className="relative">
  <div ref={fromRef}>Start Point</div>
  <div ref={toRef}>End Point</div>
  <AnimatedBeam
    containerRef={containerRef}
    fromRef={fromRef}
    toRef={toRef}
    curvature={50}
    gradientStartColor="#3b82f6"
    gradientStopColor="#8b5cf6"
  />
</div>
```

**Props:**
- `containerRef: React.RefObject<HTMLElement>` - Container element reference
- `fromRef: React.RefObject<HTMLElement>` - Start element reference
- `toRef: React.RefObject<HTMLElement>` - End element reference
- `curvature?: number` - Curve amount (default: 0)
- `duration?: number` - Animation duration
- `gradientStartColor?: string` - Start color of the beam
- `gradientStopColor?: string` - End color of the beam

#### MouseTrail
Wrapper component that creates a trail effect following the mouse cursor.

```tsx
<MouseTrail 
  size={8} 
  color="rgba(255, 255, 255, 0.4)"
  duration={0.3}
>
  <div>Content with mouse trail effect</div>
</MouseTrail>
```

**Props:**
- `size?: number` - Size of trail dots (default: 6)
- `color?: string` - Color of trail dots
- `duration?: number` - Fade duration (default: 0.2)
- `delay?: number` - Trail delay (default: 0.1)

#### Marquee
Infinitely scrolling content component.

```tsx
<Marquee 
  reverse={false}
  pauseOnHover={true}
  duration="40s"
>
  {items.map(item => (
    <div key={item.id}>{item.content}</div>
  ))}
</Marquee>
```

**Props:**
- `reverse?: boolean` - Reverse scroll direction
- `pauseOnHover?: boolean` - Pause animation on hover
- `vertical?: boolean` - Vertical scrolling
- `duration?: string` - Animation duration (default: "40s")
- `repeat?: number` - Number of repetitions (default: 4)

## 🛠 Utilities & Hooks

### Hooks

#### useMediaQuery
```tsx
const isMobile = useMediaQuery('(max-width: 768px)')
```

#### useClickOutside
```tsx
const ref = useClickOutside<HTMLDivElement>(() => {
  console.log('Clicked outside!')
})

<div ref={ref}>Content</div>
```

#### useMounted
```tsx
const mounted = useMounted()
if (!mounted) return null
```

### Utilities

#### cn
Utility function for combining class names with Tailwind merge.

```tsx
import { cn } from '@/components/ui-layouts'

<div className={cn('base-classes', conditionalClass && 'conditional', className)} />
```

## 🎨 Styling

These components are designed to work with Tailwind CSS. Make sure your `tailwind.config.ts` includes the necessary animations:

```ts
// tailwind.config.ts
export default {
  theme: {
    extend: {
      keyframes: {
        "background-shine": {
          from: { backgroundPosition: "0 0" },
          to: { backgroundPosition: "-200% 0" },
        },
        marquee: {
          from: { transform: "translateX(0)" },
          to: { transform: "translateX(calc(-100% - var(--gap)))" },
        },
        // ... other keyframes
      },
      animation: {
        "background-shine": "background-shine 2s linear infinite",
        marquee: "marquee var(--duration) infinite linear",
        // ... other animations
      },
    },
  },
}
```

## 🎯 Demo

Visit `/ui-layouts-demo` to see all components in action with interactive examples.

## 📝 License

These components are inspired by [ui-layouts.com](https://ui-layouts.com) and adapted for this project. Please check the original repository for license details.

## 🤝 Contributing

Feel free to contribute by adding more components from ui-layouts or creating your own variations! 