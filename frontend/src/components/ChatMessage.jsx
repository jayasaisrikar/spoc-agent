import React, { useEffect, useMemo, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { User, Brain, CheckCircle, AlertCircle, Code2, Clock, Copy, Check, Sparkles, CornerDownLeft } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneLight, oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import SimpleMermaidDiagram from './SimpleMermaidDiagram'

const ChatMessage = ({ message, onQuoteMessage }) => {
  const isUser = message.type === 'user'
  const [copied, setCopied] = useState(false)
  const [isDark, setIsDark] = useState(() => document.documentElement.classList.contains('dark'))
  const codeBlockCounter = useRef(0)
  codeBlockCounter.current = 0
  
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

  // Observe theme changes toggled on <html class="dark"> by Header
  useEffect(() => {
    const el = document.documentElement
    const observer = new MutationObserver(() => {
      setIsDark(el.classList.contains('dark'))
    })
    observer.observe(el, { attributes: true, attributeFilter: ['class'] })
    return () => observer.disconnect()
  }, [])

  // Simple stable hash for IDs
  const hashString = (s) => {
    let h = 0
    for (let i = 0; i < s.length; i++) {
      h = (h << 5) - h + s.charCodeAt(i)
      h |= 0
    }
    return Math.abs(h).toString(36)
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
          {/* Message-level actions for assistant messages */}
          {!isUser && !message.isThinking && (
            <div className="flex justify-end gap-1.5 mb-2">
              {onQuoteMessage && (
                <button
                  onClick={() => onQuoteMessage(message.content)}
                  className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-gray-100 dark:hover:bg-gray-800 rounded text-xs text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-gray-100"
                  title="Insert into input"
                >
                  <CornerDownLeft className="w-4 h-4" />
                </button>
              )}
              <button
                onClick={handleCopy}
                className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-gray-100 dark:hover:bg-gray-800 rounded text-xs text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-gray-100"
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
              ? 'bg-red-50 text-red-900 px-4 py-3 border border-red-200 dark:bg-red-900/20 dark:text-red-200 dark:border-red-900'
              : 'px-4 py-3'
          }`}>
            {message.isThinking ? (
              <div className="flex items-center gap-2 text-gray-500">
                <Sparkles className="w-4 h-4 animate-pulse" />
                <span className="text-sm">{message.content}</span>
              </div>
            ) : (
              <div className={`prose prose-sm max-w-none w-full ${
                isUser ? 'prose-invert' : 'prose-gray dark:prose-invert-0'
              }`}>
                <ReactMarkdown
                  components={{
                    code({node, inline, className, children, ...props}) {
                      const match = /language-(\w+)/.exec(className || '')
                      const language = match ? match[1] : ''
                      const raw = String(children)
                      // track index for stable ids when multiple code blocks exist
                      const blockIndex = (codeBlockCounter.current += 1)
                      
                      // Handle Mermaid diagrams
                      if (language === 'mermaid') {
                        const chart = raw.replace(/\n$/, '')
                        const mermaidId = `mermaid-${message.id}-${hashString(chart)}-${blockIndex}`
                        return <SimpleMermaidDiagram chart={chart} id={mermaidId} />
                      }
                      // Collapsible code blocks with header and copy
                      if (!inline && match) {
                        const [expanded, setExpanded] = [
                          // heuristic: collapse long blocks by default
                          raw.split('\n').length <= 18,
                          null,
                        ]
                        // We can't use hooks here; use a small component wrapper
                        const CodeBlock = ({ content }) => {
                          const [open, setOpen] = useState(expanded)
                          const [copiedBlock, setCopiedBlock] = useState(false)
                          const lines = content.split('\n').length
                          const handleCopyBlock = async () => {
                            try {
                              await navigator.clipboard.writeText(content)
                              setCopiedBlock(true)
                              setTimeout(() => setCopiedBlock(false), 1500)
                            } catch {}
                          }
                          return (
                            <div className="my-3 border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden">
                              <div className="flex items-center justify-between px-3 py-1.5 bg-gray-50 dark:bg-gray-900 text-xs text-gray-600 dark:text-gray-300">
                                <span className="font-mono truncate">{language || 'code'}</span>
                                <div className="flex items-center gap-2">
                                  {lines > 18 && (
                                    <button
                                      type="button"
                                      onClick={() => setOpen(!open)}
                                      className="px-2 py-0.5 rounded hover:bg-gray-100 dark:hover:bg-gray-800"
                                    >
                                      {open ? 'Collapse' : `Expand (${lines} lines)`}
                                    </button>
                                  )}
                                  <button
                                    type="button"
                                    onClick={handleCopyBlock}
                                    className="px-2 py-0.5 rounded hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center gap-1"
                                    title="Copy code"
                                  >
                                    {copiedBlock ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                                    <span>Copy</span>
                                  </button>
                                </div>
                              </div>
                              <div style={{ maxHeight: open ? 'none' : '20rem', overflow: open ? 'visible' : 'auto' }}>
                                <SyntaxHighlighter
                                  style={isDark ? oneDark : oneLight}
                                  language={language}
                                  PreTag="div"
                                  customStyle={{
                                    margin: 0,
                                    borderRadius: 0,
                                    fontSize: '0.875rem',
                                    lineHeight: '1.5'
                                  }}
                                  {...props}
                                >
                                  {content.replace(/\n$/, '')}
                                </SyntaxHighlighter>
                              </div>
                            </div>
                          )
                        }
                        return <CodeBlock content={raw} />
                      }
                      return (
                        <code 
                          className={`px-1.5 py-0.5 rounded text-sm font-mono ${
                            isUser 
          ? 'bg-gray-700 text-gray-200' 
          : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100'
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
