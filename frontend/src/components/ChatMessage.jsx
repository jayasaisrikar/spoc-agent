import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { User, Brain, CheckCircle, AlertCircle, Code2, Clock, Copy, Check, Sparkles } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'
import SimpleMermaidDiagram from './SimpleMermaidDiagram'

const ChatMessage = ({ message }) => {
  const isUser = message.type === 'user'
  const [copied, setCopied] = useState(false)
  
  const messageVariants = {
    initial: { opacity: 0, y: 20, scale: 0.98 },
    animate: { 
      opacity: 1, 
      y: 0, 
      scale: 1,
      transition: { duration: 0.2, ease: "easeOut" }
    }
  }

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy message:', err)
    }
  }

  const getMessageIcon = () => {
    if (isUser) return <User className="w-4 h-4" />
    if (message.isThinking) return <Clock className="w-4 h-4 text-gray-500 animate-pulse" />
    
    switch (message.type) {
      case 'analysis':
        return <Brain className="w-4 h-4 text-gray-600" />
      case 'suggestion':
        return <Code2 className="w-4 h-4 text-gray-600" />
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-600" />
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-600" />
      default:
        return <Brain className="w-4 h-4 text-gray-600" />
    }
  }

  return (
    <motion.div
      variants={messageVariants}
      initial="initial"
      animate="animate"
      className="group mb-6 w-full"
    >
      <div className={`flex items-start gap-4 w-full ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center mt-1 ${
          isUser 
            ? 'bg-gray-900 text-white' 
            : 'bg-gray-100 text-gray-600'
        }`}>
          {getMessageIcon()}
        </div>

        {/* Message Content */}
        <div className={`flex-1 min-w-0 ${isUser ? 'max-w-[85%]' : 'max-w-[90%]'}`}>
          {/* Copy button for non-user messages */}
          {!isUser && !message.isThinking && (
            <div className="flex justify-end mb-2">
              <button
                onClick={handleCopy}
                className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-gray-100 rounded text-xs text-gray-500 hover:text-gray-700"
                title="Copy message"
              >
                {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>
          )}

          <div className={`rounded-xl ${
            isUser 
              ? 'bg-gray-900 text-white px-4 py-3' 
              : message.isError
              ? 'bg-red-50 text-red-900 px-4 py-3 border border-red-200'
              : 'px-4 py-3'
          }`}>
            {message.isThinking ? (
              <div className="flex items-center gap-2 text-gray-500">
                <Sparkles className="w-4 h-4 animate-pulse" />
                <span className="text-sm">{message.content}</span>
              </div>
            ) : (
              <div className={`prose prose-sm max-w-none w-full ${
                isUser ? 'prose-invert' : 'prose-gray'
              }`}>
                <ReactMarkdown
                  components={{
                    code({node, inline, className, children, ...props}) {
                      const match = /language-(\w+)/.exec(className || '')
                      const language = match ? match[1] : ''
                      
                      // Handle Mermaid diagrams
                      if (language === 'mermaid') {
                        return (
                          <SimpleMermaidDiagram 
                            chart={String(children).replace(/\n$/, '')}
                            id={`mermaid-${message.id}-${Date.now()}`}
                          />
                        )
                      }
                      
                      return !inline && match ? (
                        <div className="my-3">
                          <SyntaxHighlighter
                            style={oneLight}
                            language={language}
                            PreTag="div"
                            customStyle={{
                              margin: 0,
                              borderRadius: '0.75rem',
                              background: isUser ? '#374151' : '#f8fafc',
                              border: isUser ? '1px solid #6b7280' : '1px solid #e2e8f0',
                              fontSize: '0.875rem',
                              lineHeight: '1.5'
                            }}
                            {...props}
                          >
                            {String(children).replace(/\n$/, '')}
                          </SyntaxHighlighter>
                        </div>
                      ) : (
                        <code 
                          className={`px-1.5 py-0.5 rounded text-sm font-mono ${
                            isUser 
                              ? 'bg-gray-700 text-gray-200' 
                              : 'bg-gray-100 text-gray-800'
                          }`}
                          {...props}
                        >
                          {children}
                        </code>
                      )
                    },
                    h1: ({children}) => (
                      <h1 className={`text-xl font-semibold mb-3 mt-4 first:mt-0 ${
                        isUser ? 'text-white' : 'text-gray-900'
                      }`}>
                        {children}
                      </h1>
                    ),
                    h2: ({children}) => (
                      <h2 className={`text-lg font-semibold mb-2 mt-4 first:mt-0 ${
                        isUser ? 'text-gray-100' : 'text-gray-800'
                      }`}>
                        {children}
                      </h2>
                    ),
                    h3: ({children}) => (
                      <h3 className={`text-base font-semibold mb-2 mt-3 first:mt-0 ${
                        isUser ? 'text-gray-200' : 'text-gray-700'
                      }`}>
                        {children}
                      </h3>
                    ),
                    p: ({children}) => (
                      <p className={`mb-3 leading-relaxed first:mt-0 ${
                        isUser ? 'text-gray-100' : 'text-gray-700'
                      }`}>
                        {children}
                      </p>
                    ),
                    ul: ({children}) => (
                      <ul className={`list-disc list-inside mb-3 space-y-1 pl-2 ${
                        isUser ? 'text-gray-100' : 'text-gray-700'
                      }`}>
                        {children}
                      </ul>
                    ),
                    ol: ({children}) => (
                      <ol className={`list-decimal list-inside mb-3 space-y-1 pl-2 ${
                        isUser ? 'text-gray-100' : 'text-gray-700'
                      }`}>
                        {children}
                      </ol>
                    ),
                    li: ({children}) => (
                      <li className={isUser ? 'text-gray-100' : 'text-gray-700'}>
                        {children}
                      </li>
                    ),
                    strong: ({children}) => (
                      <strong className={`font-semibold ${
                        isUser ? 'text-white' : 'text-gray-900'
                      }`}>
                        {children}
                      </strong>
                    ),
                    blockquote: ({children}) => (
                      <blockquote className={`border-l-4 pl-4 py-2 my-3 rounded-r-lg ${
                        isUser 
                          ? 'border-gray-500 bg-gray-800 text-gray-200' 
                          : 'border-gray-300 bg-gray-50 text-gray-700'
                      }`}>
                        {children}
                      </blockquote>
                    ),
                    a: ({children, href}) => (
                      <a 
                        href={href} 
                        className={`underline hover:no-underline transition-colors ${
                          isUser ? 'text-gray-200' : 'text-gray-900'
                        }`}
                        target="_blank" 
                        rel="noopener noreferrer"
                      >
                        {children}
                      </a>
                    ),
                    table: ({children}) => (
                      <div className="overflow-x-auto my-3">
                        <table className={`min-w-full border-collapse border ${
                          isUser ? 'border-gray-600' : 'border-gray-200'
                        }`}>
                          {children}
                        </table>
                      </div>
                    ),
                    th: ({children}) => (
                      <th className={`border px-3 py-2 text-left font-semibold ${
                        isUser 
                          ? 'border-gray-600 bg-gray-700 text-gray-200' 
                          : 'border-gray-200 bg-gray-50 text-gray-700'
                      }`}>
                        {children}
                      </th>
                    ),
                    td: ({children}) => (
                      <td className={`border px-3 py-2 ${
                        isUser 
                          ? 'border-gray-600 text-gray-200' 
                          : 'border-gray-200 text-gray-700'
                      }`}>
                        {children}
                      </td>
                    )
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export default ChatMessage
