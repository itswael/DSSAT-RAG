# Developer Setup Guide

Complete guide to set up and develop the DSSAT RAG Chatbot Frontend.

## Prerequisites

### Required Software

- **Node.js**: 18.17 LTS or later
  - Download: https://nodejs.org/
  - Verify: `node --version` (should be v18.17.0+)

- **npm**: Comes with Node.js
  - Verify: `npm --version` (should be 9.0.0+)

- **Git**: For version control
  - Download: https://git-scm.com/
  - Verify: `git --version`

### Optional

- **Docker**: For containerized development
  - Download: https://www.docker.com/products/docker-desktop

- **Visual Studio Code**: Recommended editor
  - Download: https://code.visualstudio.com/
  - Extensions: ESLint, Prettier, TypeScript Vue Plugin (optional)

### System Requirements

- **Windows**: 10 or later (8GB RAM recommended)
- **macOS**: 10.15 or later (8GB RAM recommended)
- **Linux**: Ubuntu 18.04+ or equivalent (8GB RAM recommended)
- **Disk Space**: 500MB for project + dependencies

## Step-by-Step Setup

### 1. Clone or Download the Project

```bash
# Option 1: Clone from GitHub (if available)
git clone <repository-url>
cd frontend

# Option 2: If you have a zip file
unzip frontend.zip
cd frontend
```

### 2. Install Dependencies

```bash
# Install all project dependencies
npm install

# This will download ~1000+ packages (~500MB)
# Takes 2-5 minutes depending on internet speed
```

**Troubleshooting Installation**:
```bash
# If you get permission errors on Mac/Linux
sudo npm install

# If you get network errors
npm install --legacy-peer-deps

# If you get corrupted cache
npm cache clean --force
npm install
```

### 3. Set Up Environment Variables

```bash
# Copy the example env file
cp .env.example .env.local

# .env.local contents (edit as needed)
NEXT_PUBLIC_API_BASE_URL=http://localhost:5678
```

**Environment Variables Explained**:

| Variable | Purpose | Default |
|----------|---------|---------|
| `NEXT_PUBLIC_API_BASE_URL` | n8n webhook base URL | `http://localhost:5678` |

**Important**: 
- Variables starting with `NEXT_PUBLIC_` are exposed to the browser
- Never commit `.env.local` to version control
- Keep `.env.example` updated for new developers

### 4. Verify n8n Service

Before starting the development server, ensure n8n is running:

```bash
# Test connectivity
curl http://localhost:5678/webhook/chat -X POST \
  -H "Content-Type: application/json" \
  -d '{"userQuery": "test"}'

# If you get a response, n8n is running ✓
```

**If n8n is not running**:
1. Start your n8n service first
2. Ensure it's configured correctly
3. Update `NEXT_PUBLIC_API_BASE_URL` if needed

### 5. Start Development Server

```bash
# Start the Next.js dev server
npm run dev

# Output should show:
# ✓ Ready in 2.5s
# ➜ Local:        http://localhost:3000
```

**Access the Application**:
- Open browser: http://localhost:3000
- You should see the DSSAT RAG Chatbot interface

## Development Workflow

### Directory Structure

```
frontend/
├── components/           # React components
│   ├── ChatContainer.tsx # Main chat interface
│   ├── ChatMessage.tsx   # Message display
│   ├── ChatInput.tsx     # Input field
│   └── index.ts          # Exports
├── pages/               # Next.js pages (routes)
│   ├── _app.tsx         # App wrapper
│   └── index.tsx        # Home page (/)
├── services/            # API layer
│   └── chatbotApi.ts    # API calls
├── types/               # TypeScript types
│   └── chat.ts          # Chat types
├── styles/              # Styling
│   └── theme.ts         # Material-UI theme
├── utils/               # Utilities
│   └── chatUtils.ts     # Helper functions
└── public/              # Static files
```

### Making Changes

#### Adding a New Component

1. **Create component file**:
```typescript
// components/MyNewComponent.tsx
import React from 'react'
import { Box, Typography } from '@mui/material'

interface MyNewComponentProps {
  title: string
}

export const MyNewComponent: React.FC<MyNewComponentProps> = ({ title }) => {
  return (
    <Box>
      <Typography variant="h6">{title}</Typography>
    </Box>
  )
}

export default MyNewComponent
```

2. **Export from index**:
```typescript
// components/index.ts
export { MyNewComponent } from './MyNewComponent'
```

3. **Use in other components**:
```typescript
import { MyNewComponent } from '@/components'

// In your component
<MyNewComponent title="Hello" />
```

#### Modifying API Service

```typescript
// services/chatbotApi.ts
async sendMessage(userQuery: string): Promise<ChatResponse> {
  // Add new logic here
  const response = await this.client.post<ChatResponse>(
    '/webhook/chat',
    { userQuery }
  )
  return response.data
}
```

#### Adding Type Definitions

```typescript
// types/chat.ts
export interface NewType {
  id: string
  name: string
  // Add properties
}
```

### Hot Reload

The development server has Hot Module Replacement (HMR):
- Save a file → Changes appear instantly
- No need to restart server
- State is preserved when possible

### VS Code Integration

**Recommended Extensions**:
```
ESLint
Prettier
TypeScript Vue Plugin (Volar)
Material-UI
```

**VS Code Settings** (`.vscode/settings.json`):
```json
{
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

## Common Development Tasks

### Check for Type Errors

```bash
npm run type-check

# Runs TypeScript compiler without emitting files
# Shows all type errors
```

### Run Linter

```bash
npm run lint

# Checks code style and quality
# ESLint configuration in .eslintrc.json
```

### Build for Production

```bash
npm run build

# Creates optimized build in .next/
# Analyzes bundle size
# Type checks automatically
```

### Start Production Server

```bash
npm start

# Runs the optimized production build
# Faster than development mode
```

## Debugging

### Browser DevTools

1. Open the app in Chrome
2. Press `F12` to open DevTools
3. Use:
   - **Console**: View logs and errors
   - **Network**: Monitor API requests
   - **React DevTools**: Inspect components (install extension)

### VS Code Debugger

Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Next.js",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/node_modules/.bin/next",
      "args": ["dev"],
      "console": "integratedTerminal"
    }
  ]
}
```

Then press `F5` to debug.

### Common Issues

**Issue**: "Cannot find module"
```bash
# Solution: Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Issue**: Port 3000 already in use
```bash
# Option 1: Kill process on port 3000
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :3000
kill -9 <PID>

# Option 2: Use different port
npm run dev -- -p 3001
```

**Issue**: Type errors after dependency update
```bash
# Rebuild types
npm run type-check

# If still failing
rm -rf node_modules
npm install
```

## Testing

### Running Tests (when added)

```bash
# Run all tests
npm test

# Run specific test file
npm test ChatMessage

# Run with coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

### Writing Tests

Example test file (`__tests__/chatUtils.test.ts`):
```typescript
import { formatTime } from '@/utils/chatUtils'

describe('chatUtils', () => {
  test('formatTime formats date correctly', () => {
    const date = new Date('2024-01-15T14:30:00')
    const result = formatTime(date)
    expect(result).toContain(':30')
  })
})
```

## Production Deployment

### Build Optimization

```bash
# Check bundle size
npm run build

# Output shows:
# ✓ API routes compiled
# ✓ Middleware compiled
# ✓ Built in 2.5s
```

### Environment Setup for Production

Create `.env.production`:
```
NEXT_PUBLIC_API_BASE_URL=https://your-production-n8n-server.com
```

### Deploy to Vercel (Recommended)

1. Push code to GitHub
2. Go to vercel.com
3. Import project
4. Add environment variables in dashboard
5. Deploy

### Deploy with Docker

```bash
# Build Docker image
docker build -t dssat-chatbot-ui .

# Run container
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_BASE_URL=http://localhost:5678 \
  dssat-chatbot-ui
```

### Deploy with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Performance Tips

### Development Performance

```bash
# Use development mode (faster rebuild)
npm run dev

# Not production build during development
# npm run build (slow, use only when needed)
```

### Production Performance

- Automatic code splitting
- Image optimization
- CSS minimization
- JavaScript minification

Check performance:
```bash
npm run build

# Check .next/static for generated files
```

## Git Workflow

### Basic Git Commands

```bash
# Check status
git status

# Stage changes
git add .

# Commit changes
git commit -m "feat: add new feature"

# Push to remote
git push origin main

# Pull latest changes
git pull origin main
```

### Commit Message Format

```
feat: add new feature
fix: fix a bug
refactor: refactor code
test: add tests
docs: update documentation
chore: update dependencies
```

### Create Feature Branch

```bash
# Create and switch to feature branch
git checkout -b feature/my-feature

# Make changes...
# Commit...

# Push feature branch
git push origin feature/my-feature

# Create Pull Request on GitHub
```

## Troubleshooting Guide

### Complete Reset

If everything is broken:

```bash
# 1. Remove node_modules and lock file
rm -rf node_modules package-lock.json

# 2. Clear npm cache
npm cache clean --force

# 3. Reinstall
npm install

# 4. Clear Next.js cache
rm -rf .next

# 5. Start fresh
npm run dev
```

### Update Dependencies

```bash
# Check outdated packages
npm outdated

# Update all packages
npm update

# Update specific package
npm install package-name@latest

# Update to next major version
npm install next@latest
```

### Clear Cache

```bash
# Next.js build cache
rm -rf .next

# npm cache
npm cache clean --force

# Browser cache
# DevTools > Application > Clear storage
```

## Learning Resources

### Next.js
- https://nextjs.org/docs
- https://nextjs.org/learn

### React
- https://react.dev
- React documentation and tutorials

### Material-UI
- https://mui.com/material-ui/
- Component library and examples

### TypeScript
- https://www.typescriptlang.org/docs/
- Type system documentation

### Web Development
- MDN Web Docs: https://developer.mozilla.org/
- Can I Use: https://caniuse.com/

## Getting Help

### Check Logs

```bash
# Browser console
F12 → Console tab

# Terminal output
# Check npm run dev terminal for errors

# Next.js logs
# Check server output for 500 errors
```

### Common Solutions

1. **Clear everything** (see Complete Reset above)
2. **Check n8n connection** (see Prerequisites)
3. **Review error message** in browser/terminal
4. **Search Stack Overflow** for the error
5. **Check GitHub Issues** in project

## Contact & Support

For issues specific to this project:
1. Review this guide first
2. Check project README
3. Review ARCHITECTURE.md
4. Contact development team

---

**Happy Coding! 🚀**
