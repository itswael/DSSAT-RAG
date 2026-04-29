/**
 * ChatMessage Component
 * Displays individual chat messages with markdown support
 */

import React from 'react'
import {
  Box,
  Paper,
  Typography,
  Avatar,
  CircularProgress,
} from '@mui/material'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { ChatMessage as ChatMessageType } from '@/types/chat'
import { formatTime } from '@/utils/chatUtils'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import PersonIcon from '@mui/icons-material/Person'
import ErrorIcon from '@mui/icons-material/Error'

interface ChatMessageProps {
  message: ChatMessageType
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user'
  const isError = !!message.error

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2,
        animation: 'slideIn 0.3s ease-out',
        '@keyframes slideIn': {
          from: {
            opacity: 0,
            transform: isUser ? 'translateX(20px)' : 'translateX(-20px)',
          },
          to: {
            opacity: 1,
            transform: 'translateX(0)',
          },
        },
      }}
    >
      <Box
        sx={{
          display: 'flex',
          gap: 1.5,
          maxWidth: '85%',
          flexDirection: isUser ? 'row-reverse' : 'row',
        }}
      >
        {/* Avatar */}
        <Avatar
          sx={{
            width: 36,
            height: 36,
            backgroundColor: isUser ? '#1E40AF' : '#10B981',
            color: 'white',
            flexShrink: 0,
            mt: 0.5,
          }}
        >
          {isUser ? (
            <PersonIcon sx={{ fontSize: 20 }} />
          ) : (
            <SmartToyIcon sx={{ fontSize: 20 }} />
          )}
        </Avatar>

        {/* Message Content */}
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            gap: 0.5,
          }}
        >
          {/* Message Bubble */}
          <Paper
            elevation={isUser ? 1 : 0}
            sx={{
              p: 2,
              backgroundColor: isError
                ? '#FEF2F2'
                : isUser
                  ? '#1E40AF'
                  : '#F3F4F6',
              color: isError ? '#DC2626' : isUser ? 'white' : '#111827',
              borderRadius: 2,
              borderTopLeftRadius: isUser ? 16 : 4,
              borderTopRightRadius: isUser ? 4 : 16,
              maxWidth: '100%',
              wordWrap: 'break-word',
              overflowWrap: 'break-word',
              border: isError ? '1px solid #EF4444' : 'none',
            }}
          >
            {message.isLoading ? (
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                <CircularProgress size={20} />
                <Typography variant="body2">Thinking...</Typography>
              </Box>
            ) : isError ? (
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-start' }}>
                <ErrorIcon sx={{ fontSize: 20, flexShrink: 0, mt: 0.25 }} />
                <Box>
                  <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                    Error
                  </Typography>
                  <Typography variant="body2">{message.error}</Typography>
                </Box>
              </Box>
            ) : (
              <Box
                className="markdown-content"
                sx={{
                  '& p': { m: 0, mb: 1, '&:last-child': { mb: 0 } },
                  '& h1, & h2, & h3, & h4, & h5, & h6': {
                    m: 0,
                    mb: 1,
                    mt: 1.5,
                    fontWeight: 700,
                    '&:first-of-type': { mt: 0 },
                  },
                  '& strong': { fontWeight: 700 },
                  '& em': { fontStyle: 'italic' },
                  '& code': {
                    backgroundColor: isUser ? 'rgba(0,0,0,0.2)' : '#E5E7EB',
                    color: isUser ? '#FFF' : '#111827',
                    padding: '2px 6px',
                    borderRadius: '3px',
                    fontFamily: 'Monaco, Courier, monospace',
                    fontSize: '0.85em',
                  },
                  '& pre': {
                    backgroundColor: isUser ? 'rgba(0,0,0,0.2)' : '#1F2937',
                    color: isUser ? '#FFF' : '#F9FAFB',
                    padding: '12px',
                    borderRadius: '6px',
                    overflow: 'auto',
                    fontSize: '0.85em',
                    margin: '8px 0',
                  },
                  '& table': {
                    borderCollapse: 'collapse',
                    margin: '8px 0',
                    width: '100%',
                    fontSize: '0.9em',
                  },
                  '& th, & td': {
                    border: `1px solid ${isUser ? 'rgba(0,0,0,0.3)' : '#D1D5DB'}`,
                    padding: '8px 12px',
                    textAlign: 'left',
                  },
                  '& th': {
                    backgroundColor: isUser ? 'rgba(0,0,0,0.2)' : '#D1D5DB',
                    fontWeight: 700,
                  },
                  '& ul, & ol': {
                    pl: 2,
                    mb: 1,
                    '&:last-child': { mb: 0 },
                  },
                  '& li': {
                    mb: 0.5,
                    '&:last-child': { mb: 0 },
                  },
                  '& blockquote': {
                    borderLeftWidth: '4px',
                    borderLeftStyle: 'solid',
                    borderLeftColor: isUser ? 'rgba(0,0,0,0.3)' : '#D1D5DB',
                    pl: 1.5,
                    py: 0.5,
                    my: 1,
                    fontStyle: 'italic',
                    color: isUser ? 'rgba(255,255,255,0.8)' : '#4B5563',
                  },
                  '& a': {
                    color: isUser ? '#ADE4FF' : '#0284C7',
                    textDecoration: 'underline',
                    '&:hover': {
                      textDecoration: 'none',
                    },
                  },
                }}
              >
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    table: ({ node, ...props }) => (
                      <table
                        {...props}
                        style={{
                          borderCollapse: 'collapse',
                          width: '100%',
                          margin: '8px 0',
                        }}
                      />
                    ),
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </Box>
            )}
          </Paper>

          {/* Timestamp and Status */}
          <Box
            sx={{
              display: 'flex',
              gap: 1,
              alignItems: 'center',
              px: 1,
              justifyContent: isUser ? 'flex-end' : 'flex-start',
            }}
          >
            <Typography
              variant="caption"
              sx={{
                color: '#9CA3AF',
                fontSize: '0.75rem',
              }}
            >
              {formatTime(message.timestamp)}
            </Typography>
          </Box>
        </Box>
      </Box>
    </Box>
  )
}

export default ChatMessage
