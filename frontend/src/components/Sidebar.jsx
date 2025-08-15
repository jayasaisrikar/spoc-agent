import React, { useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Clock, Github, Upload as UploadIcon, Trash2, ExternalLink, Download, FileUp, MessageSquare, Plus, Database } from 'lucide-react'

const Sidebar = ({ 
  isOpen, 
  onClose, 
  repositories, 
  onSelectRepository, 
  onClearHistory,
  onExportChat,
  onImportChat,
  onNewChat,
  onVisualizeKnowledgeBase,
  messages = [],
  sessionId 
}) => {
  const fileInputRef = useRef(null)

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const handleImportClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0]
    if (file && onImportChat) {
      try {
        await onImportChat(file)
        onClose()
      } catch (error) {
        alert('Failed to import chat data: ' + error.message)
      }
    }
    // Reset file input
    e.target.value = ''
  }

  const chatStats = {
    totalMessages: messages.length,
    userMessages: messages.filter(m => m.type === 'user').length,
    assistantMessages: messages.filter(m => m.type === 'assistant').length,
    repositoriesAnalyzed: repositories.length
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop - only on mobile */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          />
          
          {/* Sidebar */}
          <motion.div
            initial={{ x: -320 }}
            animate={{ x: 0 }}
            exit={{ x: -320 }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="lg:relative lg:z-auto fixed left-0 top-0 bottom-0 w-80 bg-white dark:bg-gray-950 border-r border-gray-200 dark:border-gray-800 z-50 flex flex-col min-h-0"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-800">
              <h2 className="text-lg font-light text-gray-900 dark:text-gray-100">History</h2>
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors"
              >
                <X className="w-5 h-5 text-gray-400 dark:text-gray-300" />
              </button>
            </div>

            {/* Actions */}
            <div className="p-6 border-b border-gray-200 dark:border-gray-800">
              <div className="space-y-3">
                <button
                  onClick={() => {
                    onNewChat?.()
                    onClose()
                  }}
                  className="w-full px-4 py-3 bg-black hover:bg-gray-800 text-white rounded-full transition-colors font-medium flex items-center justify-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  New Chat
                </button>
                
                <button
                  onClick={() => {
                    onVisualizeKnowledgeBase?.()
                    onClose()
                  }}
                  className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-full transition-colors font-medium flex items-center justify-center gap-2"
                >
                  <Database className="w-4 h-4" />
                  Visualize Knowledge Base
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6 min-h-0">
              {repositories.length === 0 ? (
                <div className="text-center py-12">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                    <Clock className="w-8 h-8 text-gray-300 dark:text-gray-500" />
                  </div>
                  <p className="text-gray-500 dark:text-gray-400 text-sm font-light">No repositories yet</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {repositories.map((repo) => (
                    <motion.div
                      key={repo.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="p-4 hover:bg-gray-50 dark:hover:bg-gray-900 rounded-xl transition-colors cursor-pointer group"
                      onClick={() => onSelectRepository?.(repo)}
                    >
                      <div className="flex items-start gap-3">
                        <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                          {repo.type === 'upload' ? (
                            <UploadIcon className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                          ) : (
                            <Github className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                          )}
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <h3 className="font-medium text-gray-900 dark:text-gray-100 text-sm truncate">
                            {repo.name}
                          </h3>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 font-light">
                            {formatDate(repo.analyzedAt)}
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            {repositories.length > 0 && (
              <div className="p-6 border-t border-gray-200 dark:border-gray-800">
                <button
                  onClick={onClearHistory}
                  className="w-full px-4 py-3 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30 rounded-full transition-colors font-medium"
                >
                  Clear History
                </button>
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

export default Sidebar
