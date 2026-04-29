# Quick Start Guide

Get the DSSAT RAG Chatbot UI running in 5 minutes! ⚡

## Prerequisites Check

```bash
# Check Node.js version (should be 18+)
node --version

# Check npm version
npm --version

# Ensure n8n is running
curl http://localhost:5678/webhook/chat -X POST \
  -H "Content-Type: application/json" \
  -d '{"userQuery":"test"}'
```

## Installation (2 minutes)

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Setup environment
cp .env.example .env.local
# (No changes needed if n8n is on localhost:5678)
```

## Run Development Server (1 minute)

```bash
npm run dev
```

Open browser: **http://localhost:3000**

You should see the chatbot interface! 🎉

## First Message

1. Type: "What crop data do you have?"
2. Click Send (or press Enter)
3. Wait for response (should appear in chat)

## Next Steps

### Understand the Code
- See components: `components/` folder
- API calls: `services/chatbotApi.ts`
- Types: `types/chat.ts`

### Make Changes
- Edit components and see changes instantly (hot reload)
- No server restart needed

### Deploy
- See `DEPLOYMENT.md` for production setup
- Options: Vercel, Docker, AWS, or self-hosted

### Learn More
- `README.md` - Project overview
- `DEVELOPMENT.md` - Development guide
- `ARCHITECTURE.md` - System design
- `DEPLOYMENT.md` - Deployment guide

## Common Commands

```bash
# Start development
npm run dev

# Check for errors
npm run type-check
npm run lint

# Build for production
npm run build
npm start

# Run tests (when added)
npm test
```

## Troubleshooting

### "Cannot find module" error
```bash
rm -rf node_modules package-lock.json
npm install
```

### Port 3000 already in use
```bash
npm run dev -- -p 3001
```

### API connection error
Check:
1. n8n is running on localhost:5678
2. Browser console (F12) for error details
3. Network tab to see failed requests

### TypeScript errors
```bash
npm run type-check
# Then fix any reported issues
```

## File Structure Quick Reference

```
frontend/
├── components/     → React components (UI)
├── pages/          → Next.js pages (routes)
├── services/       → API calls
├── types/          → TypeScript types
├── styles/         → Theme and styling
└── utils/          → Helper functions
```

## What's Included

✅ Beautiful Material-UI design
✅ Markdown support for responses
✅ Error handling
✅ TypeScript throughout
✅ Responsive design
✅ Production-ready code

## Next Actions

1. **Customize Theme**
   - Edit `styles/theme.ts`
   - Change colors, fonts, spacing

2. **Add Features**
   - Create new components in `components/`
   - Add types in `types/`

3. **Connect to Backend**
   - Already connected to n8n!
   - See `services/chatbotApi.ts` for API

4. **Deploy to Production**
   - Follow `DEPLOYMENT.md`
   - Choose: Vercel, Docker, or self-hosted

## Support Resources

- Next.js docs: https://nextjs.org/docs
- Material-UI: https://mui.com
- TypeScript: https://www.typescriptlang.org/docs
- React: https://react.dev

---

**Need more details? Check README.md and DEVELOPMENT.md**
