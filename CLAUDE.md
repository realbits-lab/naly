# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Setup

### Prerequisites
- Node.js 18+ (React 19 requires Node.js 18 or higher)
- pnpm package manager (this project uses pnpm-lock.yaml)

### Initial Setup
```bash
# Install dependencies
pnpm install

# Start development server with Turbopack
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start
```

### Available Scripts
- `pnpm dev` - Start development server on http://localhost:3000 with Turbopack
- `pnpm build` - Create production build
- `pnpm start` - Start production server
- `pnpm lint` - Run ESLint
- `pnpm generate-screenshots` - Generate component screenshots using Puppeteer

### Environment Variables
The project uses a `.env` file for configuration. Create one if it doesn't exist. No `.env.example` is provided in the repository.

## Architecture Overview

### Technology Stack
- **Next.js 15.1.7** with App Router and Turbopack
- **React 19.0.0** with TypeScript
- **Tailwind CSS** with custom animations and shadcn/ui design system
- **Component Libraries**: Radix UI primitives, Framer Motion
- **Form Handling**: React Hook Form + Zod validation
- **Analytics**: PostHog integration

### Project Structure
```
src/
├── app/                # Next.js app router
│   ├── (components)/  # Component documentation routes
│   ├── blocks/        # Block preview pages
│   ├── templates/     # Template pages
│   └── api/          # API routes
├── blocks/            # Full-page UI blocks
├── components/        
│   ├── ui/           # Base shadcn/ui components
│   ├── ui-layouts/   # Custom layout components
│   ├── customized/   # Component variations
│   └── layout/       # App layout components
├── lib/              # Utilities and helpers
├── hooks/            # Custom React hooks
├── providers/        # React context providers
└── types/            # TypeScript definitions
```

### Key Patterns
- **Component Registry**: JSON-based system for component discovery
- **File-based Routing**: Using Next.js App Router
- **CSS Variables**: For theming (defined in globals.css)
- **TypeScript Path Aliases**: Use `@/*` for imports from src
- **Screenshot Generation**: Automated with Puppeteer for component previews

### Important Notes
- This is a component library/showcase project (Naly, formerly Shadcn UI Blocks)
- No testing framework is currently set up
- Uses pnpm as the package manager (not npm or yarn)
- Strict TypeScript configuration is enabled
- Component code follows shadcn/ui patterns and conventions