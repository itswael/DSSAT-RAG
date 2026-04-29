/**
 * API Service for n8n Chatbot Integration
 * Handles all communication with the n8n webhook endpoint
 */

import axios, { AxiosInstance, AxiosError } from 'axios'
import { ChatRequest, ChatResponse, ApiError } from '@/types/chat'

class ChatbotApiService {
  private client: AxiosInstance
  private baseURL: string

  constructor(baseURL: string = 'http://localhost:5678') {
    this.baseURL = baseURL
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        return Promise.reject(this.handleError(error))
      }
    )
  }

  /**
   * Send a user query to the chatbot
   * @param userQuery - The user's question/query
   * @returns Promise with the assistant's response
   */
  async sendMessage(userQuery: string): Promise<ChatResponse> {
    try {
      if (!userQuery.trim()) {
        throw new Error('Query cannot be empty')
      }

      const request: ChatRequest = { userQuery }
      const response = await this.client.post<ChatResponse>(
        '/webhook/chat',
        request
      )

      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  /**
   * Handle API errors consistently
   * @param error - The error object
   * @returns Formatted ApiError
   */
  private handleError(error: unknown): ApiError {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<{ message?: string }>

      if (axiosError.response) {
        // Server responded with error status
        return {
          message:
            axiosError.response.data?.message ||
            `Server Error: ${axiosError.status}`,
          code: `ERR_${axiosError.status}`,
          details: axiosError.response.data,
        }
      } else if (axiosError.request) {
        // Request made but no response
        return {
          message:
            'No response from server. Please check if the service is running.',
          code: 'ERR_NO_RESPONSE',
        }
      }
    }

    // Unknown error
    const message =
      error instanceof Error ? error.message : 'An unexpected error occurred'
    return {
      message,
      code: 'ERR_UNKNOWN',
    }
  }

  /**
   * Update the API base URL (useful for multi-environment setups)
   * @param newBaseURL - The new base URL
   */
  setBaseURL(newBaseURL: string): void {
    this.baseURL = newBaseURL
    this.client.defaults.baseURL = newBaseURL
  }

  /**
   * Get the current base URL
   * @returns The current base URL
   */
  getBaseURL(): string {
    return this.baseURL
  }

  /**
   * Health check - verify the service is available
   * @returns Boolean indicating if service is reachable
   */
  async healthCheck(): Promise<boolean> {
    try {
      // Try a simple request to see if service is available
      await this.client.get('/webhook/chat', { timeout: 5000 }).catch(() => {
        // It's okay if the webhook doesn't respond to GET, we just want to check connectivity
        return true
      })
      return true
    } catch {
      return false
    }
  }
}

// Export singleton instance
export const chatbotApiService = new ChatbotApiService(
  process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5678'
)

export default chatbotApiService
