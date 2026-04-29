# ✅ Getting Started Checklist

Complete this checklist to get your DSSAT RAG Chatbot UI running!

## Pre-Setup (5 minutes)

- [ ] **Check Prerequisites**
  ```bash
  node --version      # Should be 18.17.0 or higher
  npm --version       # Should be 9.0.0 or higher
  ```

- [ ] **Verify n8n Running**
  ```bash
  curl http://localhost:5678/webhook/chat -X POST \
    -H "Content-Type: application/json" \
    -d '{"userQuery":"test"}'
  ```
  Should return a response from your RAG system

- [ ] **Check Project Location**
  Navigate to: `c:\Users\itswa\Desktop\ABE\DSSAT-RAG\frontend`

## Installation (5 minutes)

- [ ] **Navigate to Project**
  ```bash
  cd c:\Users\itswa\Desktop\ABE\DSSAT-RAG\frontend
  ```

- [ ] **Install Dependencies**
  ```bash
  npm install
  ```
  (Takes 2-5 minutes - goes and grabs ~1000 packages)

- [ ] **Verify Installation**
  ```bash
  npm list next react
  ```
  Should show versions installed

## Configuration (2 minutes)

- [ ] **Check Environment File**
  File exists: `.env.local`
  Contains: `NEXT_PUBLIC_API_BASE_URL=http://localhost:5678`
  
- [ ] **Update if n8n is on Different Server**
  Edit `.env.local` and change URL if needed
  Example: `NEXT_PUBLIC_API_BASE_URL=http://your-server:5678`

## Running (1 minute)

- [ ] **Start Development Server**
  ```bash
  npm run dev
  ```
  
  You should see:
  ```
  ✓ Ready in 2.5s
  ➜ Local:        http://localhost:3000
  ➜ Environments: .env.local
  ```

- [ ] **Open in Browser**
  Click or visit: http://localhost:3000
  
  You should see the DSSAT RAG Chatbot interface

## Testing (5 minutes)

- [ ] **Verify UI Loads**
  - See title: "DSSAT RAG Chatbot"
  - See input field at bottom
  - See 3 suggestion cards in center

- [ ] **Test First Message**
  - Click on "What crop data do you have?" suggestion
  - OR type your own question
  - Click Send button
  
  Expected:
  - Message appears on right in blue
  - Loading indicator shows
  - Response appears on left in gray

- [ ] **Test Markdown Rendering**
  If response contains:
  - **Bold text** - should render bold
  - Tables - should display formatted
  - Code blocks - should show with background
  - Lists - should be properly indented

- [ ] **Test Error Handling**
  Stop n8n temporarily
  Try sending a message
  Should see error message: "Unable to connect to the chatbot service"
  
  Restart n8n
  Message should work again

- [ ] **Test Chat Features**
  - [ ] Type long message
  - [ ] Send multiple messages
  - [ ] Verify auto-scroll to latest
  - [ ] Check responsive design (resize browser)

## Quality Checks (5 minutes)

- [ ] **Check for TypeScript Errors**
  ```bash
  npm run type-check
  ```
  Should complete without errors

- [ ] **Check Code Quality**
  ```bash
  npm run lint
  ```
  Should show no critical errors

- [ ] **Build for Production**
  ```bash
  npm run build
  ```
  Should complete successfully with:
  ```
  ✓ Compiled successfully
  ```

## Customization (Optional)

- [ ] **Change Theme Colors**
  File: `styles/theme.ts`
  Look for: `const colors = { ... }`
  Edit: Primary, secondary, success colors
  Save and see changes instantly

- [ ] **Change Welcome Message**
  File: `components/ChatContainer.tsx`
  Find: "Welcome to DSSAT RAG"
  Edit the text

- [ ] **Update Suggestions**
  File: `components/ChatContainer.tsx`
  Find: suggestion cards array
  Change questions

- [ ] **Update Title**
  File: `pages/index.tsx`
  Find: `<ChatContainer title="..."`
  Change title

## Deployment Preparation

- [ ] **Read DEPLOYMENT.md**
  For production deployment options

- [ ] **Choose Deployment Platform**
  - [ ] Vercel (easiest for Next.js)
  - [ ] Docker (most flexible)
  - [ ] AWS/Azure (enterprise)
  - [ ] Self-hosted (full control)

- [ ] **Prepare Production Environment**
  Update API URL for production n8n server
  Set up SSL/HTTPS

## File Organization

✅ Main App Entry
- `pages/_app.tsx` - Application wrapper
- `pages/index.tsx` - Home page

✅ Chat Components
- `components/ChatContainer.tsx` - Main interface
- `components/ChatMessage.tsx` - Message display
- `components/ChatInput.tsx` - Input field

✅ Backend Integration
- `services/chatbotApi.ts` - API calls to n8n

✅ Types & Utilities
- `types/chat.ts` - TypeScript types
- `utils/chatUtils.ts` - Helper functions
- `styles/theme.ts` - UI theme

✅ Configuration
- `package.json` - Dependencies
- `tsconfig.json` - TypeScript config
- `.env.local` - Environment variables

✅ Documentation
- `README.md` - Full project guide
- `QUICKSTART.md` - Quick setup
- `DEVELOPMENT.md` - Dev workflow
- `ARCHITECTURE.md` - System design
- `DEPLOYMENT.md` - Production setup

## Troubleshooting

If you encounter issues, check:

1. **Installation Issues**
   ```bash
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Port Already in Use**
   ```bash
   npm run dev -- -p 3001
   ```

3. **API Connection Fails**
   - Verify n8n is running
   - Check .env.local has correct URL
   - Look at browser console (F12) for errors

4. **TypeScript Errors**
   ```bash
   npm run type-check
   npm install
   ```

5. **Module Not Found**
   ```bash
   rm -rf .next node_modules
   npm install
   npm run dev
   ```

## Success Indicators ✅

You'll know everything is working when:

✅ Development server starts without errors
✅ Browser shows chatbot UI at http://localhost:3000
✅ Can type and send messages
✅ Receive responses from n8n
✅ Markdown formatting displays correctly
✅ Error handling shows graceful messages
✅ Chat scrolls automatically
✅ No console errors (F12 to check)

## Common Commands for Reference

```bash
# Development
npm run dev              # Start dev server

# Production
npm run build            # Build app
npm start                # Run production app

# Quality
npm run type-check       # Check types
npm run lint             # Check code quality

# Testing
npm test                 # Run tests (when added)
```

## Documentation Quick Links

- **Need setup help?** → Read `QUICKSTART.md`
- **Want to develop?** → Read `DEVELOPMENT.md`
- **Need to deploy?** → Read `DEPLOYMENT.md`
- **Understanding code?** → Read `ARCHITECTURE.md`
- **Full details?** → Read `README.md`

## Next Actions

1. ✅ Complete installation
2. ✅ Start development server
3. ✅ Test chat functionality
4. ✅ Explore the code
5. ✅ Customize as needed
6. ✅ Deploy to production

## Support Resources

- Next.js Docs: https://nextjs.org/docs
- Material-UI: https://mui.com
- TypeScript: https://www.typescriptlang.org
- React: https://react.dev

## Final Notes

- All files are production-ready
- Full TypeScript type safety
- Material Design professional UI
- Error handling included
- Markdown rendering works
- Responsive design
- Docker support included
- Deployment guides provided

---

**You're all set! Start with `npm install && npm run dev`** 🚀

---

## Quick Reference Card

**PROJECT LOCATION**
```
c:\Users\itswa\Desktop\ABE\DSSAT-RAG\frontend
```

**START HERE**
```bash
npm install
npm run dev
# http://localhost:3000
```

**n8n CONNECTION**
```
API URL: http://localhost:5678/webhook/chat
Config: .env.local
```

**DEPLOYMENT**
- Vercel (easiest)
- Docker
- Self-hosted

**DOCS**
- QUICKSTART.md (5 min setup)
- DEVELOPMENT.md (dev guide)
- DEPLOYMENT.md (production)

---

Print this checklist and check off items as you go! ✅
