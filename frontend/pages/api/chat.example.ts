/**
 * Optional API Route Example
 * 
 * This file demonstrates how to add backend routes if needed.
 * Currently, the app uses direct API calls to n8n.
 * 
 * To enable this route:
 * 1. Rename this file to pages/api/chat.ts
 * 2. Update services/chatbotApi.ts to call this endpoint instead
 * 3. This acts as a proxy for n8n
 * 
 * Benefits of API route proxy:
 * - Hide n8n URL from client
 * - Add authentication
 * - Rate limiting
 * - Logging
 * - Error handling
 */

import type { NextApiRequest, NextApiResponse } from 'next'
import axios from 'axios'
import { ChatRequest, ChatResponse } from '@/types/chat'

// Configuration
const N8N_WEBHOOK_URL =
  process.env.N8N_WEBHOOK_URL || 'http://localhost:5678/webhook/chat'
const REQUEST_TIMEOUT = 30000 // 30 seconds

interface ApiErrorResponse {
  error: string
  message: string
  status: number
}

/**
 * POST /api/chat
 * Forward chat messages to n8n
 */
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ChatResponse | ApiErrorResponse>
): Promise<void> {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({
      error: 'Method Not Allowed',
      message: `HTTP ${req.method} is not supported`,
      status: 405,
    })
  }

  try {
    const { userQuery } = req.body as ChatRequest

    // Validate input
    if (!userQuery || typeof userQuery !== 'string') {
      return res.status(400).json({
        error: 'Bad Request',
        message: 'userQuery is required and must be a string',
        status: 400,
      })
    }

    if (userQuery.trim().length === 0) {
      return res.status(400).json({
        error: 'Bad Request',
        message: 'userQuery cannot be empty',
        status: 400,
      })
    }

    // Log request (for debugging)
    console.log(`[API] Chat request: ${userQuery.substring(0, 50)}...`)

    // Forward to n8n
    const response = await axios.post<ChatResponse>(
      N8N_WEBHOOK_URL,
      { userQuery },
      {
        timeout: REQUEST_TIMEOUT,
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )

    // Log response
    console.log(`[API] Chat response received: ${response.data.output.substring(0, 50)}...`)

    // Return response
    return res.status(200).json(response.data)
  } catch (error) {
    console.error('[API] Error:', error)

    if (axios.isAxiosError(error)) {
      const status = error.response?.status || 500
      const message = error.response?.data?.message || error.message

      return res.status(status).json({
        error: 'Service Error',
        message,
        status,
      })
    }

    return res.status(500).json({
      error: 'Internal Server Error',
      message:
        error instanceof Error ? error.message : 'An unexpected error occurred',
      status: 500,
    })
  }
}

/**
 * To use this route:
 * 
 * 1. Update services/chatbotApi.ts:
 * 
 * async sendMessage(userQuery: string): Promise<ChatResponse> {
 *   const response = await this.client.post<ChatResponse>(
 *     '/api/chat',  // ← Change from '/webhook/chat'
 *     { userQuery }
 *   )
 *   return response.data
 * }
 * 
 * 2. Update NEXT_PUBLIC_API_BASE_URL to point to your app:
 * NEXT_PUBLIC_API_BASE_URL=http://localhost:3000
 * 
 * 3. Set N8N_WEBHOOK_URL environment variable:
 * N8N_WEBHOOK_URL=http://localhost:5678/webhook/chat
 */
