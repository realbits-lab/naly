# ECMA-376 Database Viewer

A Next.js web application for browsing and searching ECMA-376 documentation sections stored in a PostgreSQL database. Built with TypeScript, Tailwind CSS, and shadcn/ui components.

## Features

- 📊 **Database Statistics Dashboard** - View comprehensive statistics about the ECMA-376 documentation
- 🔍 **Advanced Search** - Search sections by title and description
- 🏷️ **Level Filtering** - Filter sections by hierarchy depth (Level 1-5)
- 📱 **Responsive Design** - Works on desktop and mobile devices
- ⚡ **Real-time Health Monitoring** - Database connection status monitoring
- 🎨 **Modern UI** - Built with shadcn/ui components and Tailwind CSS

## Prerequisites

Before running this application, ensure you have:

1. **Node.js** (v18 or higher)
2. **PostgreSQL** running on localhost:5432
3. **ECMA-376 Database** (`ecma376_docs`) with the sections table populated

### Database Setup

The application expects a PostgreSQL database with the following configuration:
- Database name: `ecma376_docs`
- User: `thomasjeon`
- Host: `localhost`
- Port: `5432`

The database should contain the `ecma_sections` table with ECMA-376 documentation data.

## Getting Started

1. **Install dependencies:**
```bash
npm install
```

2. **Start the development server:**
```bash
npm run dev
```

3. **Open your browser:**
Navigate to [http://localhost:3000](http://localhost:3000) to view the application.

## Development Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linting
npm run lint

# Type checking
npx tsc --noEmit

# Test API endpoints (requires dev server running)
./test-api.js
```

## API Endpoints

The application provides the following REST API endpoints:

- `GET /api/health` - Database connection health check
- `GET /api/stats` - Database statistics and metrics
- `GET /api/sections` - Fetch sections with optional filtering:
  - `?limit=50` - Limit number of results
  - `?offset=0` - Pagination offset
  - `?search=term` - Search by title/description
  - `?depth=1` - Filter by hierarchy level

## Project Structure

```
src/
├── app/
│   ├── api/              # API routes
│   │   ├── health/       # Health check endpoint
│   │   ├── sections/     # Sections data endpoint
│   │   └── stats/        # Statistics endpoint
│   ├── page.tsx          # Main dashboard page
│   └── layout.tsx        # Root layout
├── components/
│   ├── ui/               # shadcn/ui components
│   └── sections-table.tsx # Main data table component
└── lib/
    └── db.ts             # Database connection and queries
```

## Technologies Used

- **[Next.js 15](https://nextjs.org/)** - React framework with App Router
- **[TypeScript](https://www.typescriptlang.org/)** - Type safety
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first CSS framework
- **[shadcn/ui](https://ui.shadcn.com/)** - Reusable component library
- **[PostgreSQL](https://www.postgresql.org/)** - Database
- **[pg](https://node-postgres.com/)** - PostgreSQL client for Node.js

## Features Overview

### Dashboard
- Real-time database connection status
- Key metrics: total sections, embeddings count, depth levels, section types
- Responsive grid layout for statistics

### Sections Table
- Paginated data display with "Load More" functionality
- Search across titles and descriptions
- Filter by hierarchy depth (1-5 levels)
- Color-coded depth badges
- Responsive table design
- Text truncation with hover tooltips

### Database Integration
- Connection pooling for optimal performance
- Health monitoring and error handling
- Structured queries for hierarchical data
- Search and filtering capabilities

## Troubleshooting

### Database Connection Issues

If you see "Database Connection Error":

1. Ensure PostgreSQL is running: `brew services start postgresql` (macOS)
2. Verify database exists: `psql -l | grep ecma376_docs`
3. Check user permissions: `psql -U thomasjeon -d ecma376_docs -c "SELECT 1;"`
4. Review connection settings in `src/lib/db.ts`

### Build Issues

Note: Due to special characters in the directory path, the production build may fail. This is a known issue with Next.js file tracing. For development and testing, use `npm run dev`.

### Testing

Run the API test script to verify functionality:
```bash
# Start the dev server first
npm run dev

# In another terminal, run tests
./test-api.js
```

## License

This project is part of the ECMA-376 documentation framework.
