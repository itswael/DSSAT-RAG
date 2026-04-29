/**
 * Home Page
 * Main chat interface
 */

import React from 'react'
import Head from 'next/head'
import { ChatContainer } from '@/components'

export default function Home() {
  return (
    <>
      <Head>
        <title>DSSAT RAG Chatbot - Agricultural Data Assistant</title>
        <meta
          name="description"
          content="Production-grade chatbot for DSSAT agricultural data queries"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#1E40AF" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main>
        <ChatContainer
          title="DSSAT RAG Chatbot"
          subtitle="Ask questions about DSSAT agricultural data and cultivation practices"
        />
      </main>
    </>
  )
}
