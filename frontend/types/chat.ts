/**
 * Chat message types for the application
 */

export type ChatRole = 'user' | 'assistant' | 'system'

export interface ChatMessage {
  id: string
  role: ChatRole
  content: string
  timestamp: Date
  isLoading?: boolean
  error?: string
}

export interface ChatRequest {
  userQuery: string
}

export interface ChatResponse {
  output: string
}

export interface ApiError {
  message: string
  code?: string
  details?: unknown
}

export interface ChatContextState {
  messages: ChatMessage[]
  isLoading: boolean
  error: string | null
}
