import React, { useEffect, useRef, useState } from 'react'
import { Menu, Brain, Github, Save, Check, Plus, Sun, Moon, ChevronDown } from 'lucide-react'
import { motion } from 'framer-motion'
import { useApiHealth } from '../hooks/useApiHealth'

const Header = ({
  onMenuToggle,
  onNewChat,
  isAutoSaved = true,
  lastSaved = null,
  sidebarOpen = false,
  activeRepoName = null,
  repositories = [],
  onSwitchRepo,
  onSetActiveRepo,
  onClearActiveRepo
}) => {
  const online = useApiHealth()
  const [dark, setDark] = useState(() => {
    const stored = localStorage.getItem('theme')
    if (stored === 'dark') return true
    if (stored === 'light') return false
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
  })
  const [repoMenuOpen, setRepoMenuOpen] = useState(false)
  const repoBtnRef = useRef(null)

  useEffect(() => {
    const el = document.documentElement
    if (dark) el.classList.add('dark')
    else el.classList.remove('dark')
  localStorage.setItem('theme', dark ? 'dark' : 'light')
  }, [dark])

  useEffect(() => {
    const onDocClick = (e) => {
      if (!repoBtnRef.current) return
      if (!repoBtnRef.current.contains(e.target)) setRepoMenuOpen(false)
    }
    document.addEventListener('click', onDocClick)
    return () => document.removeEventListener('click', onDocClick)
  }, [])

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
  className="fixed top-0 z-40 bg-white/95 dark:bg-gray-950/90 backdrop-blur-sm border-b border-gray-200 dark:border-gray-800 h-16 transition-all duration-300 ease-in-out"
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
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
          >
            <Menu className="w-5 h-5 text-gray-600 dark:text-gray-300" />
          </button>
          
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gray-900 dark:bg-gray-800 flex items-center justify-center">
              <Brain className="w-4 h-4 text-white dark:text-gray-100" />
            </div>
            <div>
              <h1 className="text-lg font-medium text-gray-900 dark:text-gray-100">Drishya Developers SPoC</h1>
              <p className="text-xs text-gray-500 dark:text-gray-400 hidden sm:block">Architecture Analysis</p>
            </div>
          </div>
        </div>

        {/* Right section */}
        <div className="flex items-center gap-2">
          {/* New Chat Button */}
          {onNewChat && (
            <button
              onClick={onNewChat}
              className="hidden sm:flex items-center gap-2 px-4 py-2 bg-gray-900 hover:bg-gray-800 text-white rounded-lg transition-colors text-sm dark:bg-gray-800 dark:hover:bg-gray-700"
              title="Start new chat"
            >
              <Plus className="w-4 h-4" />
              <span className="hidden md:inline">New Chat</span>
            </button>
          )}

          {/* Auto-save indicator */}
          <div className="hidden sm:flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400 mr-2">
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

          {/* API health indicator */}
          <div className="hidden lg:flex items-center gap-2 px-3 py-1 rounded-full border border-gray-200 dark:border-gray-800">
            <div className={`w-2 h-2 rounded-full ${online ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-xs text-gray-600 dark:text-gray-300">{online ? 'Online' : 'Offline'}</span>
          </div>

          {/* Theme toggle */}
          <button
            onClick={() => setDark(d => !d)}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            title={dark ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {dark ? <Sun className="w-5 h-5 text-gray-600 dark:text-gray-200" /> : <Moon className="w-5 h-5 text-gray-600" />}
          </button>

          {/* Active Repo pill - always visible, even with no repos yet */}
          <div className="relative" ref={repoBtnRef}>
            <button
              onClick={() => setRepoMenuOpen(v => !v)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-gray-200 dark:border-gray-800 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 max-w-[220px]"
              title="Active repository context"
              aria-haspopup="menu"
              aria-expanded={repoMenuOpen}
            >
              <span className="truncate">{activeRepoName ? `Repo: ${activeRepoName}` : 'Select repo'}</span>
              <ChevronDown className="w-4 h-4" />
            </button>
            {repoMenuOpen && (
              <div className="absolute right-0 mt-1 w-64 max-h-72 overflow-auto bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg shadow-lg z-[100]">
                <div className="py-1 text-sm">
                  {repositories.length === 0 && (
                    <div className="px-3 py-2 text-gray-500 dark:text-gray-400">No repositories yet</div>
                  )}
                  {repositories.length > 0 && (
                    <>
                      <button
                        className="w-full text-left px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-800"
                        onClick={() => {
                          setRepoMenuOpen(false)
                          onSetActiveRepo?.(repositories[repositories.length - 1].name)
                        }}
                      >
                        Use last analyzed repo
                      </button>
                      {activeRepoName && (
                        <button
                          className="w-full text-left px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-800"
                          onClick={() => {
                            setRepoMenuOpen(false)
                            onClearActiveRepo?.()
                          }}
                        >
                          Clear active context
                        </button>
                      )}
                      <div className="my-1 border-t border-gray-200 dark:border-gray-800" />
                    </>
                  )}
                  {repositories.map((r) => (
                    <button
                      key={r.id}
                      onClick={() => {
                        setRepoMenuOpen(false)
                        if (onSwitchRepo) onSwitchRepo(r.name)
                      }}
                      className={`w-full text-left px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-800 ${
                        r.name === activeRepoName ? 'bg-gray-50 dark:bg-gray-800/50 font-medium' : ''
                      }`}
                      title={r.name}
                    >
                      <div className="truncate">{r.name}</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">{r.type || 'repo'} • {new Date(r.analyzedAt).toLocaleDateString()}</div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors group"
            title="View on GitHub"
          >
            <Github className="w-5 h-5 text-gray-600 dark:text-gray-300 group-hover:text-gray-900 dark:group-hover:text-white" />
          </a>
        </div>
      </div>
    </motion.header>
  )
}

export default Header
