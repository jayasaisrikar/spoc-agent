import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Upload, Brain, Code2, FileText, Zap, Github, Upload as UploadIcon, Plus, Menu, Wrench } from 'lucide-react'
import ChatMessage from './components/ChatMessage'
import FileUpload from './components/FileUpload'
import RepoInput from './components/RepoInput'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import SimpleMermaidDiagram from './components/SimpleMermaidDiagram'
import ToastContainer from './components/ToastContainer'
import KnowledgeBaseVisualizer from './components/KnowledgeBaseVisualizer'
import { useChat } from './hooks/useChat'
import { useToast } from './hooks/useToast'

function App() {
  const {
    messages,
    input,
    setInput,
    isLoading,
    isSaving,
    lastSaved,
    sendMessage,
    analyzeRepository,
    analyzeFile,
    suggestFeature,
    repositories,
  activeRepoName,
  setActiveRepoName,
    clearChatHistory,
    newChat,
    exportChatData,
    importChatData,
    switchToRepository,
    sessionId
  } = useChat()

  const { toasts, addToast, removeToast } = useToast()

  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [showFileUpload, setShowFileUpload] = useState(false)
  const [showRepoInput, setShowRepoInput] = useState(false)
  const [showKnowledgeBase, setShowKnowledgeBase] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const toolsRef = useRef(null)
  const [toolsOpen, setToolsOpen] = useState(false)
  const [mentionOpen, setMentionOpen] = useState(false)
  const [mentionQuery, setMentionQuery] = useState('')
  const [mentionStart, setMentionStart] = useState(null)
  const mentionRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Close tools menu on outside click
  useEffect(() => {
    const onDocClick = (e) => {
      if (!toolsRef.current) return
      if (!toolsRef.current.contains(e.target)) setToolsOpen(false)
    }
    document.addEventListener('click', onDocClick)
    return () => document.removeEventListener('click', onDocClick)
  }, [])

  // ESC to close menus and sidebar overlay
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape') {
        setToolsOpen(false)
        setMentionOpen(false)
        setSidebarOpen(false)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  const handleSendMessage = async (e) => {
    e?.preventDefault()
    if (!input.trim() || isLoading) return

    // Resolve all repo tags (#/@) from the input; strip them from content for a clean prompt.
    let repoOverride = null
    let contentToSend = input
    const allTags = Array.from(input.matchAll(/(^|\s)([#@])([\w.-]{2,})\b/g))
    const resolvedRepos = []
    if (allTags.length > 0) {
      // Collect repo names from tags
      for (const m of allTags) {
        const candidate = m[3]
        const matchRepo = repositories.find(r => r.name.toLowerCase().includes(candidate.toLowerCase()))
        if (matchRepo && !resolvedRepos.includes(matchRepo.name)) resolvedRepos.push(matchRepo.name)
      }
      // Remove all tag tokens (keep preceding space if any to preserve grammar)
      contentToSend = contentToSend
        .replace(/(^|\s)[#@][\w.-]{2,}\b/g, '$1')
        // remove extra spaces before punctuation
        .replace(/\s+([,.;!?])/g, '$1')
        // collapse repeated commas
        .replace(/,\s*,+/g, ', ')
        // trim leading/trailing commas and spaces
        .replace(/^[\s,]+/, '')
        .replace(/[\s,]+$/, '')
        // collapse multiple spaces
        .replace(/\s{2,}/g, ' ')
        .trim()

      // Use the first tag as a fallback override if multi-tag path fails
      if (resolvedRepos.length > 0) repoOverride = resolvedRepos[0]
    }

  await sendMessage(contentToSend, repoOverride, resolvedRepos, input)
    setInput('')
    inputRef.current?.focus()
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  // Mention detection in input
  const handleInputChange = (e) => {
    const val = e.target.value
    setInput(val)
    const caret = e.target.selectionStart
    // Find the word segment before the caret
    const left = val.slice(0, caret)
    const match = left.match(/(^|\s)([#@])([\w.-]*)$/)
    if (match) {
      const q = match[3]
      setMentionOpen(true)
      setMentionQuery(q)
      setMentionStart(caret - q.length - 1) // position at # or @
    } else {
      setMentionOpen(false)
      setMentionQuery('')
      setMentionStart(null)
    }
  }

  const filteredRepos = repositories.filter(r =>
    mentionQuery ? r.name.toLowerCase().includes(mentionQuery.toLowerCase()) : true
  ).slice(0, 8)

  const applyMention = (repoName) => {
    if (mentionStart == null) return
    const before = input.slice(0, mentionStart)
    // find end of current token
    const rest = input.slice(mentionStart)
    const tokenMatch = rest.match(/^[#@][\w.-]*/)
    let afterIdx = mentionStart
    if (tokenMatch) afterIdx = mentionStart + tokenMatch[0].length
    const after = input.slice(afterIdx)
    const insertion = `#${repoName} `
    const newVal = `${before}${insertion}${after}`
    setInput(newVal)
    setMentionOpen(false)
    setMentionQuery('')
    setMentionStart(null)
    // Move caret to after the inserted mention
    requestAnimationFrame(() => {
      const pos = (before + insertion).length
      if (inputRef.current) {
        inputRef.current.setSelectionRange(pos, pos)
        inputRef.current.focus()
      }
    })
  }

  const handleFileUpload = async (file) => {
    try {
      await analyzeFile(file)
      addToast(`Successfully analyzed ${file.name}`, 'success')
      setShowFileUpload(false)
    } catch (error) {
      addToast(`Failed to analyze ${file.name}: ${error.message}`, 'error')
    }
  }

  const handleRepoSubmit = async (repoUrl) => {
    try {
      await analyzeRepository(repoUrl)
      addToast('Repository analysis completed successfully', 'success')
      setShowRepoInput(false)
    } catch (error) {
      addToast(`Failed to analyze repository: ${error.message}`, 'error')
    }
  }

  const handleImportChat = async (file) => {
    try {
      await importChatData(file)
      addToast('Chat data imported successfully', 'success')
      setSidebarOpen(false)
    } catch (error) {
      addToast(`Failed to import chat data: ${error.message}`, 'error')
      throw error // Re-throw to let Sidebar handle it too
    }
  }

  const handleExportChat = () => {
    try {
      exportChatData()
      addToast('Chat data exported successfully', 'success')
    } catch (error) {
      addToast(`Failed to export chat data: ${error.message}`, 'error')
    }
  }

  const handleClearHistory = () => {
    clearChatHistory()
    addToast('Chat history cleared', 'info')
    setSidebarOpen(false)
  }

  const handleNewChat = () => {
    newChat()
    addToast('Started new chat', 'success')
    setSidebarOpen(false)
  }

  const handleVisualizeKnowledgeBase = () => {
    setShowKnowledgeBase(true)
    setSidebarOpen(false)
  }

  const quickActions = [
    {
      icon: <Code2 className="w-4 h-4" />,
      text: "Analyze project structure",
      action: () => setInput("Analyze my project structure and suggest improvements")
    },
    {
      icon: <Brain className="w-4 h-4" />,
      text: "Add authentication system",
      action: () => setInput("Where should I implement user authentication in my codebase?")
    },
    {
      icon: <FileText className="w-4 h-4" />,
      text: "Review API design",
      action: () => setInput("Review my API architecture and suggest best practices")
    },
    {
      icon: <Zap className="w-4 h-4" />,
      text: "Add real-time features",
      action: () => setInput("How can I add real-time features like WebSocket support?")
    }
  ]

  return (
  <div className="h-screen bg-white text-gray-900 dark:bg-gray-950 dark:text-gray-100 flex overflow-hidden">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 ease-in-out flex-shrink-0`}>
        <Sidebar 
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          repositories={repositories}
          messages={messages}
          sessionId={sessionId}
          onSelectRepository={async (repo) => {
            setSidebarOpen(false)
            const result = await switchToRepository(repo.name)
            if (result.success) {
              addToast(`Switched to ${repo.name} conversation`, 'success')
            } else {
              addToast(`Failed to switch to ${repo.name}: ${result.error}`, 'error')
            }
          }}
          onClearHistory={handleClearHistory}
          onNewChat={handleNewChat}
          onExportChat={handleExportChat}
          onImportChat={handleImportChat}
          onVisualizeKnowledgeBase={handleVisualizeKnowledgeBase}
        />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 h-full transition-all duration-300 ease-in-out">
        {/* Header */}
        <Header 
          onMenuToggle={() => setSidebarOpen(!sidebarOpen)} 
          onNewChat={handleNewChat}
          isAutoSaved={!isSaving}
          lastSaved={lastSaved}
          sidebarOpen={sidebarOpen}
          activeRepoName={activeRepoName}
          repositories={repositories}
          onSwitchRepo={async (name) => {
            const result = await switchToRepository(name)
            if (result.success) {
              addToast(`Switched to ${name} conversation`, 'success')
            } else {
              addToast(`Failed to switch to ${name}: ${result.error}`, 'error')
            }
          }}
          onSetActiveRepo={(name) => setActiveRepoName(name)}
          onClearActiveRepo={() => setActiveRepoName(null)}
        />

        {/* Chat Container */}
  <div className="flex-1 flex flex-col min-h-0">
          {/* Conditional rendering: Knowledge Base Visualizer or Chat */}
          {showKnowledgeBase ? (
            <div className="flex-1 overflow-y-auto">
              <div className="p-4">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-2xl font-bold text-gray-900">Knowledge Base Visualizer</h2>
                  <button
                    onClick={() => setShowKnowledgeBase(false)}
                    className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                  >
                    Back to Chat
                  </button>
                </div>
                <KnowledgeBaseVisualizer />
              </div>
            </div>
          ) : (
            <>
              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto">
            <div className={`mx-auto px-6 pt-24 pb-12 transition-all duration-300 ease-in-out ${
              sidebarOpen ? 'max-w-4xl' : 'max-w-5xl'
            }`}>
              {messages.length === 0 ? (
                // Welcome screen - Ultra minimal
                <motion.div
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-center py-32"
                >
                  <div className="w-16 h-16 mx-auto mb-12 rounded-full bg-black flex items-center justify-center">
                    <Brain className="w-8 h-8 text-white" />
                  </div>
                  <h1 className="text-4xl font-extralight text-gray-900 mb-6 tracking-tight">
                    Code Assistant
                  </h1>
                  <p className="text-lg text-gray-500 mb-16 font-light">
                    Analyze, understand, and improve your code
                  </p>
                  
                  {/* Simple upload options */}
                  <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <button
                      onClick={() => setShowFileUpload(true)}
                      className="px-8 py-4 bg-black hover:bg-gray-800 text-white rounded-full transition-colors font-medium"
                    >
                      Upload Project
                    </button>
                    <button
                      onClick={() => setShowRepoInput(true)}
                      className="px-8 py-4 border-2 border-gray-300 hover:border-gray-400 text-gray-700 rounded-full transition-colors font-medium"
                    >
                      Analyze Repository
                    </button>
                  </div>
                </motion.div>
              ) : (
                // Messages - cleaner layout
                <div className="space-y-12 pb-32">
                  {messages.map((message) => (
                    <ChatMessage
                      key={message.id}
                      message={message}
                      onQuoteMessage={(text) => {
                        setInput(prev => (prev ? `${prev}\n\n> ${text}` : text))
                        inputRef.current?.focus()
                      }}
                    />
                  ))}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>
          </div>

          {/* Input Area - Floating and minimal */}
          <div className="fixed bottom-8 z-40" style={{ 
            left: '50%',
            transform: sidebarOpen ? 'translateX(calc(-50% + 160px))' : 'translateX(-50%)',
            width: sidebarOpen ? 'calc(100% - 320px)' : '100%',
            maxWidth: sidebarOpen ? 'calc(1280px - 320px)' : '80rem',
            paddingLeft: '1.5rem',
            paddingRight: '1.5rem',
            transition: 'all 0.3s ease-in-out'
          }}>
            <form onSubmit={handleSendMessage} className="relative">
              <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-full shadow-lg flex items-center pl-2 pr-2 py-2">
                {/* Tools menu */}
                <div className="relative mr-2" ref={toolsRef}>
                  <button
                    type="button"
                    onClick={() => setToolsOpen(v => !v)}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors"
                    title="Tools"
                    aria-haspopup="menu"
                    aria-expanded={toolsOpen}
                  >
                    <Wrench className="w-5 h-5 text-gray-500 dark:text-gray-300" />
                  </button>
                  {toolsOpen && (
                    <div className="absolute bottom-full mb-2 left-0 w-56 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg shadow-lg z-50">
                      <div className="py-1 text-sm">
                        <button
                          className="w-full text-left px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-800"
                          onClick={() => { setShowFileUpload(true); setToolsOpen(false) }}
                        >
                          Upload Project
                        </button>
                        <button
                          className="w-full text-left px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-800"
                          onClick={() => { setShowRepoInput(true); setToolsOpen(false) }}
                        >
                          Analyze Repository
                        </button>
                        <button
                          className="w-full text-left px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-800"
                          onClick={() => { setShowKnowledgeBase(true); setToolsOpen(false) }}
                        >
                          Knowledge Base
                        </button>
                      </div>
                    </div>
                  )}
                </div>
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={handleInputChange}
                  onKeyDown={handleKeyPress}
                  placeholder="Ask about your code..."
                  className="flex-1 bg-transparent text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 outline-none text-lg py-2"
                  disabled={isLoading}
                />
                {/* Mention suggestions dropdown */}
                {mentionOpen && filteredRepos.length > 0 && (
                  <div ref={mentionRef} className="absolute bottom-full mb-2 left-6 w-72 max-h-64 overflow-auto bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg shadow-lg z-50">
                    <div className="py-1 text-sm">
                      {filteredRepos.map(r => (
                        <button
                          key={r.id}
                          className="w-full text-left px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-800"
                          onClick={() => applyMention(r.name)}
                        >
                          #{r.name}
                          <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">{r.type || 'repo'}</span>
                        </button>
                      ))}
                      {repositories.length > 8 && (
                        <div className="px-3 py-1 text-xs text-gray-500 dark:text-gray-400">Showing first 8… refine your search</div>
                      )}
                    </div>
                  </div>
                )}
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setShowFileUpload(true)}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors"
                    title="Upload file"
                  >
                    <UploadIcon className="w-5 h-5 text-gray-400 dark:text-gray-300" />
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowRepoInput(true)}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors"
                    title="Analyze GitHub repo"
                  >
                    <Github className="w-5 h-5 text-gray-400 dark:text-gray-300" />
                  </button>
                  <button
                    type="submit"
                    disabled={!input.trim() || isLoading}
                    className="p-3 bg-black hover:bg-gray-800 disabled:bg-gray-300 dark:disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-full transition-colors ml-2"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </form>
          </div>
              </>
            )}
        </div>
      </div>

      {/* File Upload Modal */}
      <AnimatePresence>
        {showFileUpload && (
          <FileUpload
            onClose={() => setShowFileUpload(false)}
            onFileSelect={handleFileUpload}
          />
        )}
      </AnimatePresence>

      {/* Repo Input Modal */}
      <AnimatePresence>
        {showRepoInput && (
          <RepoInput
            onClose={() => setShowRepoInput(false)}
            onSubmit={handleRepoSubmit}
          />
        )}
      </AnimatePresence>

      {/* Toast Notifications */}
      <ToastContainer toasts={toasts} onClose={removeToast} />
    </div>
  )
}

export default App
