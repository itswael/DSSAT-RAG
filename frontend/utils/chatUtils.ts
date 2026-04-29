/**
 * Utility functions for chat message formatting and display
 */

/**
 * Generate a unique ID for messages
 * @returns UUID string
 */
export const generateMessageId = (): string => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

/**
 * Format timestamp for display
 * @param date - Date object to format
 * @returns Formatted time string (e.g., "2:30 PM")
 */
export const formatTime = (date: Date): string => {
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  })
}

/**
 * Truncate text to a maximum length with ellipsis
 * @param text - Text to truncate
 * @param maxLength - Maximum length
 * @returns Truncated text
 */
export const truncateText = (text: string, maxLength: number = 100): string => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

/**
 * Check if content contains markdown formatting
 * @param content - Content to check
 * @returns Boolean indicating if markdown is present
 */
export const hasMarkdown = (content: string): boolean => {
  const markdownPatterns = [
    /#{1,6}\s/, // Headers
    /\*\*.*?\*\*/, // Bold
    /\*.*?\*/, // Italic
    /`.*?`/, // Inline code
    /```[\s\S]*?```/, // Code blocks
    /\[.*?\]\(.*?\)/, // Links
    /^[-*+]\s/, // Lists
    /^\d+\.\s/, // Numbered lists
    /\|.*\|/, // Tables
  ]

  return markdownPatterns.some((pattern) => pattern.test(content))
}

/**
 * Sanitize content to prevent XSS (markdown-react handles this, but good practice)
 * @param content - Content to sanitize
 * @returns Sanitized content
 */
export const sanitizeContent = (content: string): string => {
  // Remove dangerous scripts but preserve markdown
  return content
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/on\w+\s*=\s*["'][^"']*["']/gi, '')
}

/**
 * Extract plain text from markdown content
 * @param markdown - Markdown content
 * @returns Plain text preview
 */
export const getMarkdownPreview = (markdown: string, length: number = 150): string => {
  const plainText = markdown
    .replace(/#{1,6}\s/g, '') // Remove headers
    .replace(/\*\*|__/g, '') // Remove bold
    .replace(/\*|_/g, '') // Remove italic
    .replace(/`/g, '') // Remove code markers
    .replace(/\[([^\]]*)\]\([^\)]*\)/g, '$1') // Extract link text
    .replace(/\n+/g, ' ') // Replace newlines with spaces
    .trim()

  return plainText.length > length
    ? plainText.substring(0, length) + '...'
    : plainText
}

/**
 * Count the number of words in content
 * @param content - Content to count
 * @returns Word count
 */
export const countWords = (content: string): number => {
  return content.trim().split(/\s+/).length
}

/**
 * Estimate read time in seconds
 * Average reading speed: 200 words per minute
 * @param content - Content to estimate
 * @returns Estimated read time in seconds
 */
export const estimateReadTime = (content: string): number => {
  const words = countWords(content)
  const wordsPerMinute = 200
  const minutes = Math.ceil(words / wordsPerMinute)
  return minutes * 60
}

/**
 * Detect if content is likely a table
 * @param content - Content to check
 * @returns Boolean indicating if content appears to be a table
 */
export const isTableContent = (content: string): boolean => {
  const tablePattern = /^\|[\s\S]*\|$/m
  return tablePattern.test(content)
}
