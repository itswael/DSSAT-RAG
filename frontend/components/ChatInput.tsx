/**
 * ChatInput Component
 * Handles user input and message submission
 */

import React, { useState, useCallback, useRef, useEffect } from 'react'
import {
  Box,
  TextField,
  IconButton,
  CircularProgress,
  Tooltip,
  InputAdornment,
  Paper,
  Typography,
} from '@mui/material'
import SendIcon from '@mui/icons-material/Send'
import AttachFileIcon from '@mui/icons-material/AttachFile'
import MicIcon from '@mui/icons-material/Mic'

interface ChatInputProps {
  onSendMessage: (message: string) => Promise<void>
  isLoading?: boolean
  disabled?: boolean
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isLoading = false,
  disabled = false,
}) => {
  const [input, setInput] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)
  const [isFocused, setIsFocused] = useState(false)

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const handleSendMessage = useCallback(async () => {
    if (input.trim() && !isLoading && !disabled) {
      const message = input.trim()
      setInput('')
      await onSendMessage(message)
      // Re-focus after sending
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }, [input, isLoading, disabled, onSendMessage])

  const handleKeyPress = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSendMessage()
    }
  }

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInput(event.target.value)
  }

  const handleFocus = () => setIsFocused(true)
  const handleBlur = () => setIsFocused(false)

  const isButtonDisabled = !input.trim() || isLoading || disabled

  return (
    <Paper
      elevation={0}
      sx={{
        borderTop: '1px solid #E5E7EB',
        p: 2,
        backgroundColor: '#FFFFFF',
      }}
    >
      <Box
        sx={{
          display: 'flex',
          gap: 1,
          alignItems: 'flex-end',
        }}
      >
        {/* Attachment Button */}
        <Tooltip title="Attach file (coming soon)">
          <span>
            <IconButton
              size="small"
              disabled
              sx={{
                color: '#9CA3AF',
                '&:hover': { backgroundColor: '#F3F4F6' },
              }}
            >
              <AttachFileIcon sx={{ fontSize: 20 }} />
            </IconButton>
          </span>
        </Tooltip>

        {/* Input Field */}
        <TextField
          inputRef={inputRef}
          multiline
          maxRows={4}
          minRows={1}
          fullWidth
          placeholder="Ask me anything about DSSAT data..."
          value={input}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          onFocus={handleFocus}
          onBlur={handleBlur}
          disabled={isLoading || disabled}
          variant="outlined"
          size="small"
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                {isLoading && <CircularProgress size={20} />}
              </InputAdornment>
            ),
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 2,
              backgroundColor: isFocused ? '#FFFFFF' : '#F9FAFB',
              transition:
                'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              '&:hover fieldset': {
                borderColor: '#3B82F6',
              },
              '&.Mui-focused fieldset': {
                borderColor: '#1E40AF',
                boxShadow: '0 0 0 3px rgba(30, 64, 175, 0.1)',
              },
              '&.Mui-disabled': {
                backgroundColor: '#F3F4F6',
              },
            },
            '& .MuiOutlinedInput-input': {
              fontSize: '0.95rem',
              '&::placeholder': {
                color: '#9CA3AF',
                opacity: 0.8,
              },
            },
          }}
        />

        {/* Microphone Button */}
        <Tooltip title="Voice input (coming soon)">
          <span>
            <IconButton
              size="small"
              disabled
              sx={{
                color: '#9CA3AF',
                '&:hover': { backgroundColor: '#F3F4F6' },
              }}
            >
              <MicIcon sx={{ fontSize: 20 }} />
            </IconButton>
          </span>
        </Tooltip>

        {/* Send Button */}
        <Tooltip title={isButtonDisabled ? 'Type a message to send' : 'Send message (Enter)'}>
          <span>
            <IconButton
              onClick={handleSendMessage}
              disabled={isButtonDisabled}
              sx={{
                backgroundColor: isButtonDisabled ? '#E5E7EB' : '#1E40AF',
                color: 'white',
                borderRadius: 1.5,
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  backgroundColor: isButtonDisabled ? '#E5E7EB' : '#0F2958',
                  transform: 'scale(1.05)',
                },
                '&:active': {
                  transform: 'scale(0.95)',
                },
              }}
            >
              {isLoading ? (
                <CircularProgress size={20} sx={{ color: 'white' }} />
              ) : (
                <SendIcon sx={{ fontSize: 20 }} />
              )}
            </IconButton>
          </span>
        </Tooltip>
      </Box>

      {/* Character count hint */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mt: 1,
          px: 1,
          minHeight: '20px',
        }}
      >
        <Typography
          variant="caption"
          sx={{
            color: '#9CA3AF',
            fontSize: '0.7rem',
          }}
        >
          Shift + Enter for new line
        </Typography>
        {input.length > 0 && (
          <Typography
            variant="caption"
            sx={{
              color: input.length > 1000 ? '#EF4444' : '#9CA3AF',
              fontSize: '0.7rem',
            }}
          >
            {input.length} characters
          </Typography>
        )}
      </Box>
    </Paper>
  )
}

export default ChatInput
