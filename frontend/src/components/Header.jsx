import React from 'react'
import { Menu, Brain, Github, ExternalLink, Save, Check, Plus } from 'lucide-react'
import { motion } from 'framer-motion'

const Header = ({ onMenuToggle, onNewChat, isAutoSaved = true, lastSaved = null, sidebarOpen = false }) => {
  const formatLastSaved = (timestamp) => {
    if (!timestamp) return ''
    const now = new Date()
    const saved = new Date(timestamp)
    const diff = Math.floor((now - saved) / 1000)
    
    if (diff < 60) return 'Saved just now'
    if (diff < 3600) return `Saved ${Math.floor(diff / 60)}m ago`
    if (diff < 86400) return `Saved ${Math.floor(diff / 3600)}h ago`
    return `Saved ${Math.floor(diff / 86400)}d ago`
  }

  return (
    <motion.header 
      initial={{ y: -64 }}
      animate={{ y: 0 }}
      transition={{ type: 'spring', damping: 30, stiffness: 300 }}
      className="fixed top-0 z-30 bg-white/95 backdrop-blur-sm border-b border-gray-200 h-16 transition-all duration-300 ease-in-out"
      style={{
        left: sidebarOpen ? '320px' : '0',
        right: '0',
        width: sidebarOpen ? 'calc(100% - 320px)' : '100%'
      }}
    >
      <div className="flex items-center justify-between px-6 h-full">
        {/* Left section */}
        <div className="flex items-center gap-4">
          <button
            onClick={onMenuToggle}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Menu className="w-5 h-5 text-gray-600" />
          </button>
          
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gray-900 flex items-center justify-center">
              <Brain className="w-4 h-4 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-medium text-gray-900">Drishya Developers SPoC</h1>
              <p className="text-xs text-gray-500 hidden sm:block">Architecture Analysis</p>
            </div>
          </div>
        </div>

        {/* Right section */}
        <div className="flex items-center gap-2">
          {/* New Chat Button */}
          {onNewChat && (
            <button
              onClick={onNewChat}
              className="hidden sm:flex items-center gap-2 px-4 py-2 bg-gray-900 hover:bg-gray-800 text-white rounded-lg transition-colors text-sm"
              title="Start new chat"
            >
              <Plus className="w-4 h-4" />
              <span className="hidden md:inline">New Chat</span>
            </button>
          )}

          {/* Auto-save indicator */}
          <div className="hidden sm:flex items-center gap-2 text-xs text-gray-500 mr-2">
            {isAutoSaved ? (
              <div className="flex items-center gap-1">
                <Check className="w-3 h-3 text-green-600" />
                <span>{formatLastSaved(lastSaved) || 'Auto-saved'}</span>
              </div>
            ) : (
              <div className="flex items-center gap-1">
                <Save className="w-3 h-3 text-orange-500 animate-pulse" />
                <span>Saving...</span>
              </div>
            )}
          </div>

          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors group"
            title="View on GitHub"
          >
            <Github className="w-5 h-5 text-gray-600 group-hover:text-gray-900" />
          </a>
          
          <div className="hidden lg:flex items-center gap-2 px-3 py-1 bg-gray-100 rounded-full">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <span className="text-xs text-gray-600">Online</span>
          </div>
        </div>
      </div>
    </motion.header>
  )
}

export default Header
