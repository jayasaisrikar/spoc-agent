import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Github, X, ExternalLink, AlertCircle, Globe } from 'lucide-react'

const RepoInput = ({ onClose, onSubmit }) => {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!url.trim()) return

    setLoading(true)
    setError('')
    
    try {
      await onSubmit(url.trim())
      onClose()
    } catch (error) {
      console.error('Analysis failed:', error)
      setError('Failed to analyze repository. Please check the URL and try again.')
    }
    setLoading(false)
  }

  const validateUrl = (url) => {
    const githubPattern = /^https?:\/\/(www\.)?github\.com\/[\w\-\.]+\/[\w\-\.]+\/?.*$/
    return githubPattern.test(url)
  }

  const isValidUrl = url ? validateUrl(url) : true

  const exampleRepos = [
    'https://github.com/facebook/react',
    'https://github.com/microsoft/vscode',
    'https://github.com/nodejs/node'
  ]

  return (
    <>
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
      >
        {/* Modal */}
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
          className="bg-gray-900 rounded-xl border border-gray-700 p-6 w-full max-w-md"
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Github className="w-5 h-5 text-gray-400" />
              <h2 className="text-lg font-semibold text-gray-100">Analyze GitHub Repository</h2>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-400" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="repo-url" className="block text-sm font-medium text-gray-300 mb-2">
                Repository URL
              </label>
              <div className="relative">
                <input
                  id="repo-url"
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://github.com/username/repository"
                  className={`w-full bg-gray-800 border rounded-lg px-4 py-3 text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    !isValidUrl ? 'border-red-500' : 'border-gray-600'
                  }`}
                  disabled={loading}
                />
                <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                  <Globe className="w-5 h-5 text-gray-400" />
                </div>
              </div>
              {!isValidUrl && (
                <p className="mt-1 text-sm text-red-400">Please enter a valid GitHub repository URL</p>
              )}
            </div>

            {/* Error message */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center gap-2"
              >
                <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
                <span className="text-red-300 text-sm">{error}</span>
              </motion.div>
            )}

            {/* Examples */}
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-400">Example repositories:</p>
              <div className="space-y-1">
                {exampleRepos.map((repo, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => setUrl(repo)}
                    className="block w-full text-left text-sm text-blue-400 hover:text-blue-300 hover:bg-gray-800/50 rounded px-2 py-1 transition-colors"
                  >
                    {repo.replace('https://github.com/', '')}
                  </button>
                ))}
              </div>
            </div>

            {/* Submit button */}
            <button
              type="submit"
              disabled={!url.trim() || !isValidUrl || loading}
              className="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Analyzing...
                </>
              ) : (
                <>
                  <Github className="w-4 h-4" />
                  Analyze Repository
                </>
              )}
            </button>
          </form>

          {/* Info */}
          <div className="mt-4 p-3 bg-gray-800/50 rounded-lg">
            <h4 className="text-sm font-medium text-gray-300 mb-2">What we analyze:</h4>
            <ul className="text-xs text-gray-400 space-y-1">
              <li>• Project structure and architecture</li>
              <li>• Technology stack and dependencies</li>
              <li>• Code organization and patterns</li>
              <li>• Configuration files and documentation</li>
            </ul>
          </div>
        </motion.div>
      </motion.div>
    </>
  )
}

export default RepoInput
