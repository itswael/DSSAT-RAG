# Architecture & Design Document

## Overview

The DSSAT RAG Chatbot Frontend is a modern, production-grade web application built with Next.js and React. It provides a beautiful, professional interface for users to interact with the n8n-based agricultural data chatbot.

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│         Browser / User Device                        │
├─────────────────────────────────────────────────────┤
│  Next.js Application                                │
│  ├─ React Components (Chat UI)                      │
│  ├─ State Management (React Hooks)                  │
│  └─ Styling (Material-UI + Emotion)                 │
├─────────────────────────────────────────────────────┤
│  API Service Layer (Axios)                          │
├─────────────────────────────────────────────────────┤
│  Network (HTTP/REST)                                │
├─────────────────────────────────────────────────────┤
│  n8n Webhook Service                                │
│  └─ POST /webhook/chat                              │
└─────────────────────────────────────────────────────┘
```

## Design Patterns

### 1. Component Composition

Each UI element is a reusable React component:

```
ChatContainer (Main Layout)
  ├─ Header (Title + Menu)
  ├─ MessagesArea
  │  └─ ChatMessage (Repeated)
  └─ ChatInput (Input Field)
```

### 2. Service Layer Pattern

API communication is abstracted through a service:

```typescript
// Usage in components
chatbotApiService.sendMessage(query)
  .then(response => handleResponse(response))
  .catch(error => handleError(error))
```

**Benefits**:
- Easy to mock for testing
- Centralized error handling
- Simple API endpoint changes
- Consistent error format

### 3. Type-Driven Development

All data structures are strictly typed:

```typescript
interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  isLoading?: boolean
  error?: string
}
```

**Benefits**:
- Compile-time error detection
- IDE autocomplete support
- Documentation through types
- Runtime safety

### 4. Separation of Concerns

```
components/          # UI rendering
├─ ChatContainer     # Layout & state
├─ ChatMessage       # Message display
└─ ChatInput         # User input

services/            # Business logic
└─ chatbotApi.ts     # API communication

utils/               # Helpers
└─ chatUtils.ts      # Formatting functions

types/               # Type definitions
└─ chat.ts           # Chat-related types

styles/              # Styling
└─ theme.ts          # Theme configuration
```

## State Management Strategy

### Local Component State

Uses React Hooks for component-level state:

```typescript
const [messages, setMessages] = useState<ChatMessage[]>([])
const [isLoading, setIsLoading] = useState(false)
const [error, setError] = useState<string | null>(null)
```

**Why**:
- Simpler than Redux for this use case
- Sufficient for chat application
- Better performance (no unnecessary re-renders)
- Easier to debug

### State Flow

```
User Input
    ↓
handleSendMessage()
    ↓
Add user message to state
    ↓
Call API via service
    ↓
Update loading state
    ↓
Handle response/error
    ↓
Add assistant message to state
    ↓
UI re-renders automatically
```

## Key Features Implementation

### 1. Markdown Rendering

Uses `react-markdown` with `remark-gfm`:

```typescript
<ReactMarkdown
  remarkPlugins={[remarkGfm]}
  components={{...}}
>
  {message.content}
</ReactMarkdown>
```

Supports:
- Tables
- Strikethrough
- Autolinks
- Task lists
- Code syntax highlighting

### 2. Real-time Updates

Auto-scroll implementation:

```typescript
useEffect(() => {
  scrollToBottom()
}, [messages])
```

Smooth scrolling with `behavior: 'smooth'`

### 3. Error Handling Strategy

Three-tier error handling:

```
Tier 1: API Service (chatbotApi.ts)
  ├─ Network errors
  ├─ Server errors
  └─ Validation errors
  
Tier 2: Component (ChatContainer.tsx)
  ├─ State updates
  ├─ User feedback
  └─ Recovery actions
  
Tier 3: UI (ChatMessage.tsx)
  └─ Error display
```

### 4. Performance Optimizations

**Memoization**:
```typescript
const handleSendMessage = useCallback(
  async (userQuery: string) => {
    // Implementation
  },
  []
)
```

**Lazy Rendering**:
- Messages only rendered when visible
- Auto-cleanup of old messages optional

**Efficient Re-renders**:
- Proper dependency arrays
- Avoid inline object creation
- Component memo for static props

## Material Design Implementation

### Color System

```
Primary: #1E40AF (Deep Blue)
  ├─ Light: #3B82F6
  └─ Dark: #0F2958

Secondary: #06B6D4 (Cyan)

Neutrals: Complete gray scale
  ├─ 50-100: Light backgrounds
  ├─ 200-400: Borders & dividers
  ├─ 500-700: Secondary text
  └─ 800-900: Primary text
```

### Typography

- **Display**: H1-H3 for main headings
- **Body**: Body1-Body2 for content
- **Caption**: Labels and timestamps
- **Button**: Styled action elements

### Component Styling

Using MUI's `sx` prop for consistent styling:

```typescript
sx={{
  backgroundColor: '#F3F4F6',
  borderRadius: 2,
  transition: 'all 0.3s',
  '&:hover': {
    boxShadow: '0 8px 16px rgba(...)',
  },
}}
```

## API Integration Details

### Request Flow

```
User Query
  ↓
Validate (non-empty)
  ↓
Create ChatRequest { userQuery: string }
  ↓
POST to /webhook/chat
  ↓
Wait for ChatResponse { output: string }
  ↓
Parse markdown
  ↓
Display with formatting
```

### Error Recovery

```
Error Occurs
  ↓
Identify Error Type
  ├─ Network → Show connection error
  ├─ Server → Show server error + message
  └─ Unknown → Show generic error
  ↓
User can retry
  ↓
Connection restored
```

## Scalability Considerations

### Current (Single Chat Session)

- Single ChatContainer
- Messages stored in local state
- Suitable for single user

### Future (Multi-session / Team)

1. **User Authentication**
   - Add auth service
   - Persist user identity

2. **Database Integration**
   - Save chat history
   - User preferences

3. **Real-time Sync**
   - WebSocket for live updates
   - Collaborative chat

4. **Analytics**
   - Track user queries
   - Measure response quality

## Testing Strategy

### Unit Tests
```typescript
// Test chat formatting utilities
describe('chatUtils', () => {
  test('generateMessageId creates unique IDs', () => {
    // ...
  })
})
```

### Integration Tests
```typescript
// Test API service
describe('chatbotApiService', () => {
  test('sendMessage returns response', async () => {
    // ...
  })
})
```

### Component Tests
```typescript
// Test React components
describe('<ChatMessage />', () => {
  test('renders user message correctly', () => {
    // ...
  })
})
```

## Security Considerations

### Input Validation
- Trim user input
- Check for empty messages
- Limit message length

### Output Sanitization
- react-markdown handles XSS
- No dangerous HTML execution
- Safe markdown parsing

### Data Protection
- No sensitive data in logs
- HTTPS for production
- Secure API communication

### CORS
- Configure CORS with n8n
- Validate origin
- Restrict methods to POST

## Performance Metrics

### Target Metrics
- **First Contentful Paint**: < 1.5s
- **Time to Interactive**: < 2.5s
- **Largest Contentful Paint**: < 2.5s
- **Message latency**: < 30s (user perception)

### Optimization Techniques
- Next.js automatic code splitting
- Image optimization
- CSS-in-JS efficiency
- Minimal bundle size

## Deployment Architecture

### Local Development
```
npm run dev
→ http://localhost:3000
```

### Production Build
```
npm run build
npm start
→ http://localhost:3000
```

### Cloud Deployment
```
Environment Variables → NEXT_PUBLIC_API_BASE_URL
→ Deployed on Vercel/Docker/AWS
→ HTTPS
→ CDN for static assets
```

## Monitoring & Logging

### Error Logging
- Browser console (dev)
- Service integration (production)

### Performance Monitoring
- Web Vitals
- API response times
- User interaction metrics

## Future Enhancements

1. **Voice Interface**
   - Speech-to-text input
   - Text-to-speech output

2. **File Handling**
   - Upload documents
   - Process CSV/Excel

3. **Advanced Features**
   - Conversation search
   - Export to PDF
   - Report generation

4. **AI Features**
   - Query suggestions
   - Follow-up recommendations
   - Context preservation

---

**This architecture ensures maintainability, scalability, and user satisfaction.**
