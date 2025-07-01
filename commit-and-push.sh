#!/bin/bash

# Stage all changes
git add .

# Commit with detailed message
git commit -m "feat: Implement new digital asset marketplace architecture

- Add feature-based directory structure for auth, templates, and dashboard
- Create template marketplace with browsing, filtering, and detail pages
- Implement authentication system with Supabase integration
- Add user dashboard with stats, navigation, and subscription management
- Create reusable components following shadcn/ui patterns
- Add comprehensive database schema for templates, users, and subscriptions
- Update navigation to include marketplace link
- Add TypeScript types and service layer for scalability

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to remote
git push origin feature/migration

echo "Commit and push completed!"