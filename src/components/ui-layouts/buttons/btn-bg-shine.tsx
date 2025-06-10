'use client'

import { cn } from '../lib/utils'

interface ButtonBackgroundShineProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children?: React.ReactNode
}

const ButtonBackgroundShine = ({
  children = 'Click Me',
  className,
  ...props
}: ButtonBackgroundShineProps) => {
  return (
    <button
      className={cn(
        'inline-flex w-fit mx-auto h-12 animate-background-shine items-center justify-center rounded-md border-2 dark:border-[#656fe2] border-[#c0c6fc] dark:bg-[linear-gradient(110deg,#1e2a78,45%,#3749be,55%,#1e2a78)] bg-[linear-gradient(110deg,#3d5af1,45%,#5471ff,55%,#3d5af1)] bg-[length:200%_100%] dark:hover:border-white px-6 font-medium text-white dark:text-white transition-colors focus:outline-none focus:ring-2 dark:focus:ring-gray-400 focus:ring-offset-2 focus:ring-offset-gray-50',
        className
      )}
      {...props}
    >
      {children}
    </button>
  )
}

export default ButtonBackgroundShine 