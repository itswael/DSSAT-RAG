# DSSAT RAG Chatbot - Frontend UI

A production-grade chatbot user interface for the DSSAT RAG (Retrieval-Augmented Generation) system. Built with Next.js, React, TypeScript, and Material-UI.

## Features

✨ **Beautiful UI**
- Modern Material Design with professional color scheme
- Responsive design that works on desktop and mobile
- Smooth animations and transitions
- Dark and light theme support ready

📱 **Chat Interface**
- Real-time message exchange with the n8n chatbot
- Auto-scrolling chat history
- Typing indicators and loading states
- Error handling and connection status

📝 **Rich Content Support**
- Full Markdown rendering (headings, bold, italic, code)
- Syntax-highlighted code blocks
- Table rendering
- List support (ordered and unordered)
- Link and blockquote support

🔧 **Production Ready**
- Full TypeScript support with strict typing
- Comprehensive error handling
- API service abstraction layer
- Environment-based configuration
- Export chat history as text
- Clear chat history functionality

## Tech Stack

- **Framework**: Next.js 14
- **UI Library**: Material-UI (MUI) 5
- **Language**: TypeScript
- **Markdown**: React Markdown with GitHub Flavored Markdown (GFM)
- **HTTP Client**: Axios
- **Styling**: Emotion (MUI's styling engine)

## Project Structure

```
frontend/
├── components/           # React components
│   ├── ChatContainer.tsx # Main chat interface
│   ├── ChatMessage.tsx   # Individual message component
│   ├── ChatInput.tsx     # Input field component
│   └── index.ts          # Component exports
├── pages/               # Next.js pages
│   ├── _app.tsx         # App wrapper with theme
│   └── index.tsx        # Home page
├── services/            # API service layer
│   └── chatbotApi.ts    # n8n webhook integration
├── types/               # TypeScript type definitions
│   └── chat.ts          # Chat-related types
├── styles/              # Styling and theme
│   └── theme.ts         # Material-UI theme config
├── utils/               # Utility functions
│   └── chatUtils.ts     # Chat-specific utilities
├── public/              # Static files
├── package.json         # Dependencies
├── tsconfig.json        # TypeScript config
├── next.config.ts       # Next.js config
├── .env.example         # Environment variables template
└── README.md            # This file
```

## Getting Started

### Prerequisites

- Node.js 18+ (18.17 or later)
- npm or yarn
- n8n service running and accessible

### Installation

1. **Copy environment variables**
   ```bash
   cp .env.example .env.local
   ```

2. **Update API endpoint** (if needed)
   ```bash
   # .env.local
   NEXT_PUBLIC_API_BASE_URL=http://localhost:5678
   ```

3. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

### Development

Start the development server:

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Building for Production

Build the application:

```bash
npm run build
npm start
# or
yarn build
yarn start
```

### Type Checking

Run TypeScript type checker:

```bash
npm run type-check
```

## API Integration

The chatbot communicates with your n8n webhook endpoint:

**Endpoint**: `POST /webhook/chat`

**Request Format**:
```json
{
  "userQuery": "what crop data you have"
}
```

**Response Format**:
```json
{
  "output": "The response from the AI/RAG system..."
}
```

The application handles:
- Connection errors with user-friendly messages
- Network timeouts
- Validation of user input
- Response markdown formatting

## Component API

### ChatContainer

Main chat interface component.

```typescript
<ChatContainer
  title="DSSAT RAG Chatbot"
  subtitle="Ask questions about DSSAT agricultural data"
/>
```

**Props**:
- `title` (optional): Header title
- `subtitle` (optional): Header subtitle

### ChatMessage

Displays individual chat messages.

```typescript
<ChatMessage message={chatMessage} />
```

**Props**:
- `message`: ChatMessage object with role, content, timestamp

### ChatInput

Input field for user messages.

```typescript
<ChatInput
  onSendMessage={handleSendMessage}
  isLoading={isLoading}
  disabled={false}
/>
```

**Props**:
- `onSendMessage`: Callback function for sending messages
- `isLoading` (optional): Loading state
- `disabled` (optional): Disable input

## Service API

### chatbotApiService

API service for n8n integration.

```typescript
import { chatbotApiService } from '@/services/chatbotApi'

// Send message
const response = await chatbotApiService.sendMessage('what crop data you have')

// Check service health
const isAvailable = await chatbotApiService.healthCheck()

// Update base URL
chatbotApiService.setBaseURL('http://new-server:5678')
```

## Styling & Theme

The application uses a professional Material Design theme with:

- **Primary Colors**: Deep blue (#1E40AF) with gradients
- **Secondary**: Cyan (#06B6D4)
- **Neutral Palette**: Tailored gray scale for readability
- **Spacing**: 8px base unit
- **Typography**: Modern system font stack
- **Shadows**: Subtle elevation system

### Customizing Theme

Edit `styles/theme.ts` to modify:
- Color palette
- Typography
- Component overrides
- Breakpoints

## Features in Detail

### Markdown Support

The chat fully supports markdown formatting:
- Headers (H1-H6)
- Bold and italic text
- Code blocks and inline code
- Tables
- Lists (ordered and unordered)
- Blockquotes
- Links

### Chat History Management

Users can:
- Export chat as text file
- Clear chat history
- Auto-scroll to latest message
- See typing indicators during loading

### Error Handling

The app handles:
- Connection failures
- API errors with detailed messages
- Invalid input validation
- Timeout handling
- Network disconnections with user feedback

## Best Practices Implemented

✅ **Code Quality**
- Strict TypeScript configuration
- Comprehensive error handling
- Component composition
- Proper separation of concerns

✅ **Performance**
- React hooks optimization
- Callback memoization
- Lazy rendering of messages
- Efficient re-renders

✅ **Accessibility**
- ARIA labels
- Keyboard navigation
- Semantic HTML
- Color contrast compliance

✅ **UX/UI**
- Smooth animations
- Loading states
- Error messages
- Empty state guidance
- Responsive design

## Troubleshooting

### API Connection Error

**Problem**: "Unable to connect to the chatbot service"

**Solution**:
1. Verify n8n is running on the correct port
2. Check `NEXT_PUBLIC_API_BASE_URL` in `.env.local`
3. Ensure firewall allows communication

### Markdown Not Rendering

**Problem**: Markdown formatting appears as text

**Solution**:
- This is expected for plain text responses
- Rich formatting only displays for actual markdown content

### Slow Performance

**Problem**: Chat is slow or laggy

**Solution**:
1. Check network connection
2. Verify n8n API response time
3. Clear browser cache
4. Check for browser extensions interference

## Deployment

### Vercel (Recommended for Next.js)

1. Push to GitHub
2. Import project in Vercel
3. Set environment variables in dashboard
4. Deploy

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Other Platforms

The app can be deployed to any platform supporting Node.js:
- AWS Amplify
- Netlify
- Railway
- Heroku
- Self-hosted servers

## Development Roadmap

Future enhancements:
- [ ] Voice input/output
- [ ] File attachment support
- [ ] Conversation search
- [ ] User authentication
- [ ] Chat persistence to database
- [ ] Mobile app version
- [ ] Dark mode toggle
- [ ] Response feedback (helpful/not helpful)

## Contributing

Contributions are welcome! Please follow:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is private and part of the ABE DSSAT RAG system.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review existing error logs
3. Contact the development team

## Environment Configuration

### Development

```bash
# .env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:5678
```

### Production

Update `NEXT_PUBLIC_API_BASE_URL` to your production n8n server address.

---

**Built with ❤️ for agricultural data enthusiasts**
