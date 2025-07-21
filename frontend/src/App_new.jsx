import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Upload, Brain, Code2, FileText, Zap, Github, Upload as UploadIcon, Plus, Menu } from 'lucide-react'
import ChatMessage from './components/ChatMessage'
import FileUpload from './components/FileUpload'
import RepoInput from './components/RepoInput'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import { useChat } from './hooks/useChat'

function App() {
  const {
    messages,
    input,
    setInput,
    isLoading,
    sendMessage,
    analyzeRepository,
    analyzeFile,
    suggestFeature,
    repositories
  } = useChat()

  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [showFileUpload, setShowFileUpload] = useState(false)
  const [showRepoInput, setShowRepoInput] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (e) => {
    e?.preventDefault()
    if (!input.trim() || isLoading) return
    
    await sendMessage(input)
    setInput('')
    inputRef.current?.focus()
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleFileUpload = async (file) => {
    await analyzeFile(file)
    setShowFileUpload(false)
  }

  const handleRepoSubmit = async (repoUrl) => {
    await analyzeRepository(repoUrl)
    setShowRepoInput(false)
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
    <div className="min-h-screen bg-gray-950 text-gray-100 flex">
      {/* Sidebar */}
      <Sidebar 
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        repositories={repositories}
        onSelectRepository={(repo) => {
          setInput(`Let's analyze the ${repo.name} repository`)
          setSidebarOpen(false)
        }}
        onClearHistory={() => {
          console.log('Clear history')
        }}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <Header onMenuToggle={() => setSidebarOpen(!sidebarOpen)} />

        {/* Chat Container */}
        <div className="flex-1 flex flex-col pt-16">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto">
            <div className="max-w-4xl mx-auto px-4 py-6">
              {messages.length === 0 ? (
                // Welcome screen
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-center py-12"
                >
                  <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                    <Brain className="w-8 h-8 text-white" />
                  </div>
                  <h1 className="text-2xl font-bold text-gray-100 mb-3">
                    AI Code Architecture Assistant
                  </h1>
                  <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
                    I can help you analyze codebases, suggest feature implementations, and provide architectural guidance. 
                    Upload a ZIP file, provide a GitHub URL, or just ask me questions about your code.
                  </p>
                  
                  {/* Quick action buttons */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto mb-8">
                    {quickActions.map((action, index) => (
                      <motion.button
                        key={index}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        onClick={action.action}
                        className="flex items-center gap-3 p-4 bg-gray-800/50 hover:bg-gray-800 border border-gray-700/50 rounded-lg transition-colors text-left"
                      >
                        <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center text-blue-400">
                          {action.icon}
                        </div>
                        <span className="text-gray-300">{action.text}</span>
                      </motion.button>
                    ))}
                  </div>

                  {/* Upload options */}
                  <div className="flex flex-col sm:flex-row gap-3 justify-center">
                    <button
                      onClick={() => setShowFileUpload(true)}
                      className="flex items-center gap-2 px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
                    >
                      <UploadIcon className="w-4 h-4" />
                      Upload ZIP File
                    </button>
                    <button
                      onClick={() => setShowRepoInput(true)}
                      className="flex items-center gap-2 px-6 py-3 bg-gray-800 hover:bg-gray-700 border border-gray-600 text-gray-100 rounded-lg transition-colors"
                    >
                      <Github className="w-4 h-4" />
                      Analyze GitHub Repo
                    </button>
                  </div>
                </motion.div>
              ) : (
                // Messages
                <div className="space-y-6">
                  {messages.map((message) => (
                    <ChatMessage key={message.id} message={message} />
                  ))}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-800 bg-gray-950/95 backdrop-blur-sm">
            <div className="max-w-4xl mx-auto p-4">
              <form onSubmit={handleSendMessage} className="relative">
                <div className="flex items-end gap-2">
                  {/* Action buttons */}
                  <div className="flex gap-1 mb-3">
                    <button
                      type="button"
                      onClick={() => setShowFileUpload(true)}
                      className="p-2 hover:bg-gray-800 rounded-lg transition-colors group"
                      title="Upload file"
                    >
                      <UploadIcon className="w-5 h-5 text-gray-400 group-hover:text-gray-300" />
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowRepoInput(true)}
                      className="p-2 hover:bg-gray-800 rounded-lg transition-colors group"
                      title="Analyze GitHub repo"
                    >
                      <Github className="w-5 h-5 text-gray-400 group-hover:text-gray-300" />
                    </button>
                  </div>

                  {/* Input field */}
                  <div className="flex-1 relative">
                    <textarea
                      ref={inputRef}
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={handleKeyPress}
                      placeholder="Ask me about your codebase, request analysis, or describe a feature you'd like to implement..."
                      className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 pr-12 text-gray-100 placeholder-gray-500 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent max-h-32"
                      rows={1}
                      style={{ minHeight: '44px' }}
                      disabled={isLoading}
                    />
                    <button
                      type="submit"
                      disabled={!input.trim() || isLoading}
                      className="absolute right-2 bottom-2 p-2 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </form>
            </div>
          </div>
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
    </div>
  )
}

export default App
