# Web Diagram Generator

A Next.js application that generates diagrams using AI (Gemini) and displays them on a canvas. The application features a chat interface for describing diagrams and a canvas panel for visualizing the results.

## Features

- **Chat Interface**: Located on the left side (200px width) with input at the bottom
- **Canvas Panel**: Located on the right side for displaying generated diagrams
- **AI-Powered Generation**: Uses Google Gemini AI to interpret prompts and generate diagrams
- **Multiple Diagram Types**: Supports Mermaid diagrams, shape-based diagrams, and flowcharts
- **Interactive Canvas**: Built with Fabric.js for interactive diagram manipulation

## Technologies Used

- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: Modern UI components
- **Google Gemini AI**: AI model for diagram generation
- **AI SDK**: Framework for handling LLM operations
- **Fabric.js**: Canvas manipulation library
- **Mermaid**: Diagram generation from text
- **D3.js**: Data visualization library

## Setup Instructions

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Configure Environment Variables**
   Create a `.env.local` file in the root directory:
   ```
   GOOGLE_GENERATIVE_AI_API_KEY=your_google_ai_api_key_here
   ```

3. **Run Development Server**
   ```bash
   npm run dev
   ```

4. **Open in Browser**
   Navigate to `http://localhost:3000` (or the port shown in the terminal)

## Usage

1. **Describe Your Diagram**: Type a description in the chat panel on the left
2. **Generate**: Click send or press Enter to generate the diagram
3. **View Result**: The generated diagram will appear on the canvas panel on the right

## Example Prompts

- "Create a flowchart for a login process"
- "Draw an organizational chart with CEO, managers, and employees"
- "Make a simple diagram showing the software development lifecycle"
- "Create a network diagram with servers and databases"

## Project Structure

```
src/
├── app/
│   ├── api/
│   │   └── generate-diagram/
│   │       └── route.ts          # API endpoint for diagram generation
│   ├── globals.css               # Global styles with Tailwind
│   ├── layout.tsx               # Root layout component
│   └── page.tsx                 # Main page component
├── components/
│   ├── ui/                      # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   └── scroll-area.tsx
│   ├── ChatPanel.tsx            # Chat interface component
│   └── CanvasPanel.tsx          # Canvas display component
└── lib/
    └── utils.ts                 # Utility functions
```

## How It Works

1. **User Input**: User types a diagram description in the chat panel
2. **AI Processing**: The prompt is sent to Google Gemini AI via the API endpoint
3. **Diagram Generation**: AI generates structured diagram data (Mermaid, shapes, or flowchart)
4. **Canvas Rendering**: The structured data is rendered on the canvas using Fabric.js
5. **Interactive Display**: Users can interact with the generated diagram on the canvas

## API Endpoints

- `POST /api/generate-diagram`: Generates diagram data from text prompts

## Diagram Types

- **Mermaid**: Complex flowcharts, sequence diagrams, process flows
- **Shapes**: Simple geometric diagrams, org charts, basic layouts
- **Flowchart**: Decision trees, step-by-step processes

## Development Notes

- The application uses Next.js 15 with the App Router
- TypeScript is configured for type safety
- Tailwind CSS provides responsive styling
- shadcn/ui components ensure consistent design
- The AI SDK handles Gemini AI integration
- Fabric.js manages canvas interactions
- Mermaid provides text-to-diagram conversion