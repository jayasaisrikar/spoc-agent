import { useState, useCallback, useEffect } from 'react'
import { API_BASE_URL, apiFetch } from '../utils/api'

// Storage keys
const STORAGE_KEYS = {
  MESSAGES: 'codebase_agent_messages',
  REPOSITORIES: 'codebase_agent_repositories',
  CHAT_SESSIONS: 'codebase_agent_chat_sessions'
}

// Default welcome message
const DEFAULT_WELCOME_MESSAGE = {
  id: '1',
  type: 'assistant',
  content: 'Welcome! I\'m your AI Code Architecture Assistant. I can analyze codebases, suggest feature placements, and help you understand your repository structure. \n\nYou can:\n• Upload a ZIP file of your codebase\n• Provide a GitHub repository URL\n• Ask questions about code architecture\n• Get suggestions for implementing new features',
  timestamp: new Date().toISOString()
}

// Storage utilities
const storage = {
  save: (key, data) => {
    try {
      localStorage.setItem(key, JSON.stringify(data))
    } catch (error) {
      console.error('Failed to save to localStorage:', error)
    }
  },
  load: (key, defaultValue = null) => {
    try {
      const item = localStorage.getItem(key)
      return item ? JSON.parse(item) : defaultValue
    } catch (error) {
      console.error('Failed to load from localStorage:', error)
      return defaultValue
    }
  },
  remove: (key) => {
    try {
      localStorage.removeItem(key)
    } catch (error) {
      console.error('Failed to remove from localStorage:', error)
    }
  }
}

export const useChat = () => {
  // Initialize state from localStorage or defaults
  const [messages, setMessages] = useState(() => {
    const savedMessages = storage.load(STORAGE_KEYS.MESSAGES, [])
    return savedMessages.length > 0 ? savedMessages : [DEFAULT_WELCOME_MESSAGE]
  })
  
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [lastSaved, setLastSaved] = useState(() => {
    return storage.load('last_saved_timestamp', null)
  })
  const [repositories, setRepositories] = useState(() => {
    return storage.load(STORAGE_KEYS.REPOSITORIES, [])
  })

  // Track which repository is the current active context
  const [activeRepoName, setActiveRepoName] = useState(() => {
    return storage.load('active_repo_name', null)
  })

  // Generate unique session ID for better organization
  const [sessionId] = useState(() => {
    return storage.load('current_session_id', `session_${Date.now()}`)
  })

  // Save current session ID
  useEffect(() => {
    storage.save('current_session_id', sessionId)
  }, [sessionId])

  // Persist active repository selection
  useEffect(() => {
  // Persist even if null to avoid stale values
  storage.save('active_repo_name', activeRepoName)
  }, [activeRepoName])

  // Enhanced message saving with session metadata
  useEffect(() => {
    const saveData = async () => {
      setIsSaving(true)
      await new Promise(resolve => setTimeout(resolve, 100)) // Small delay to show saving state
      
      const timestamp = new Date().toISOString()
      const chatData = {
        sessionId,
        messages,
        lastUpdated: timestamp,
        messageCount: messages.length
      }
      
      storage.save(STORAGE_KEYS.MESSAGES, chatData.messages)
      storage.save('last_saved_timestamp', timestamp)
      
      // Also save session metadata for future features
      const sessionData = storage.load(STORAGE_KEYS.CHAT_SESSIONS, {})
      sessionData[sessionId] = {
        lastUpdated: chatData.lastUpdated,
        messageCount: chatData.messageCount,
        title: messages.length > 1 ? 
          messages.find(m => m.type === 'user')?.content?.substring(0, 50) + '...' || 'New Chat' : 
          'New Chat'
      }
      storage.save(STORAGE_KEYS.CHAT_SESSIONS, sessionData)
      
      setLastSaved(timestamp)
      setIsSaving(false)
    }
    
    saveData()
  }, [messages, sessionId])

  // Save repositories to localStorage whenever repositories change
  useEffect(() => {
    const saveRepositories = async () => {
      setIsSaving(true)
      await new Promise(resolve => setTimeout(resolve, 50))
      storage.save(STORAGE_KEYS.REPOSITORIES, repositories)
      const timestamp = new Date().toISOString()
      storage.save('last_saved_timestamp', timestamp)
      setLastSaved(timestamp)
      setIsSaving(false)
    }
    
  // Always persist, even when empty (to clear prior state)
  saveRepositories()
  }, [repositories])

  // Clear all chat data
  const clearChatHistory = useCallback(() => {
    setMessages([DEFAULT_WELCOME_MESSAGE])
    setRepositories([])
    storage.remove(STORAGE_KEYS.MESSAGES)
    storage.remove(STORAGE_KEYS.REPOSITORIES)
    storage.remove(STORAGE_KEYS.CHAT_SESSIONS)
    storage.remove('current_session_id')
  storage.remove('active_repo_name')
  }, [])

  // Start a new chat while preserving repositories
  const newChat = useCallback(() => {
    setMessages([DEFAULT_WELCOME_MESSAGE])
    setInput('')
    // Don't clear repositories - keep them for reference
    // Generate new session ID for the new chat
    const newSessionId = `session_${Date.now()}`
    storage.save('current_session_id', newSessionId)
    
    // Save the current messages before clearing (for history purposes)
    storage.save(STORAGE_KEYS.MESSAGES, [DEFAULT_WELCOME_MESSAGE])
  }, [])

  // Export chat data for backup
  const exportChatData = useCallback(() => {
    const exportData = {
      messages,
      repositories,
      sessionId,
      exportedAt: new Date().toISOString(),
      version: '1.0'
    }
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `codebase-agent-chat-${sessionId}-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }, [messages, repositories, sessionId])

  // Import chat data from backup
  const importChatData = useCallback((file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const importData = JSON.parse(e.target.result)
          if (importData.messages && importData.repositories) {
            setMessages(importData.messages)
            setRepositories(importData.repositories)
            resolve(true)
          } else {
            reject(new Error('Invalid chat data format'))
          }
        } catch (error) {
          reject(error)
        }
      }
      reader.onerror = () => reject(new Error('Failed to read file'))
      reader.readAsText(file)
    })
  }, [])

  const addMessage = useCallback((message) => {
    setMessages(prev => [...prev, {
      ...message,
      id: Date.now().toString(),
      timestamp: new Date().toISOString()
    }])
  }, [])

  const sendMessage = useCallback(async (content = input, repoOverride = null, repoOverrides = null, originalContent = null) => {
    if (!content.trim() || isLoading) return

    const startTime = Date.now()
    const userMessage = {
      type: 'user',
      // Show exactly what the user typed (with tags) in the UI, but send cleaned content to backend
      content: (originalContent ?? content).trim()
    }

    addMessage(userMessage)
    setInput('')
    setIsLoading(true)

    try {
      // Add thinking message with timer
      const thinkingMessage = {
        type: 'assistant',
        content: 'Let me analyze your request...',
        isThinking: true,
        startTime: startTime
      }
      addMessage(thinkingMessage)

      // Use active repository (or fallback to most recent) to provide context-aware responses
      // Prefer explicit repoOverrides (array) if provided; fallback to detection from content
      let matchedRepos = Array.isArray(repoOverrides) ? [...repoOverrides] : []
      if (matchedRepos.length === 0) {
        const tagMatches = Array.from((content.match(/(^|\s)([#@])([\w.-]{2,})\b/g) || []).values())
        for (const token of tagMatches) {
          const m = token.match(/[#@]([\w.-]{2,})/)
          if (m) {
            const candidate = m[1]
            const found = repositories.find(r => r.name.toLowerCase().includes(candidate.toLowerCase()))
            if (found && !matchedRepos.includes(found.name)) matchedRepos.push(found.name)
          }
        }
      }

      const repoNameForQuestion = repoOverride || activeRepoName || (repositories.length > 0 ? repositories[repositories.length - 1].name : null)
      if (repoNameForQuestion) {
        const formData = new FormData()
        formData.append('question', content.trim())
        if (matchedRepos.length > 1) {
          formData.append('repo_contexts', JSON.stringify(matchedRepos))
        } else {
          formData.append('repo_context', matchedRepos[0] || repoNameForQuestion)
        }
        formData.append('session_id', sessionId)

        const data = await apiFetch(`/ask-question`, {
          method: 'POST',
          body: formData
        })
        const endTime = Date.now()
        const thinkingTime = ((endTime - startTime) / 1000).toFixed(1)

    setMessages(prev => {
          const filtered = prev.filter(m => !m.isThinking)
          return [...filtered, {
            id: Date.now().toString(),
            type: 'assistant',
            content: formatAnalysisResults(data),
            timestamp: new Date().toISOString(),
      thinkingTime: `${thinkingTime}s`,
      repoContext: data?.repo_context || undefined,
      repoContexts: data?.repo_contexts || undefined
          }]
        })
      } else {
        // No repository context - provide general guidance
        setTimeout(() => {
          setMessages(prev => {
            const filtered = prev.filter(m => !m.isThinking)
            return [...filtered, {
              id: Date.now().toString(),
              type: 'assistant',
              content: `I understand you're asking about: "${content}"\n\nTo provide the best analysis, please:\n1. Upload your codebase as a ZIP file, or\n2. Provide a GitHub repository URL\n\nOnce I have access to your code, I can give you detailed insights about architecture, suggest improvements, and help with feature placement.`,
              timestamp: new Date().toISOString()
            }]
          })
          setIsLoading(false)
        }, 1500)
      }

    } catch (error) {
      console.error('Error sending message:', error)
      setMessages(prev => {
        const filtered = prev.filter(m => !m.isThinking)
        return [...filtered, {
          id: Date.now().toString(),
          type: 'assistant',
          content: 'Sorry, I encountered an error while processing your request. Please try again.',
          timestamp: new Date().toISOString(),
          isError: true
        }]
      })
    } finally {
      setIsLoading(false)
    }
  }, [input, isLoading, addMessage, repositories, activeRepoName, sessionId])

  const analyzeRepository = useCallback(async (repoUrl) => {
    const startTime = Date.now()
    setIsLoading(true)
    
    addMessage({
      type: 'user',
      content: `Analyze repository: ${repoUrl}`
    })

    addMessage({
      type: 'assistant',
      content: 'Starting repository analysis...',
      isThinking: true,
      startTime: startTime
    })

    try {
      const formData = new FormData()
      formData.append('repo_url', repoUrl)
      
      // Extract repo name from URL in owner-repo format
      const urlParts = repoUrl.replace(/https?:\/\/github\.com\//, '').split('/')
      const repoName = urlParts.length >= 2 ? `${urlParts[0]}-${urlParts[1]}` : (repoUrl.split('/').pop() || 'unknown-repo')
      formData.append('repo_name', repoName)

      const data = await apiFetch(`/analyze-repo`, {
        method: 'POST',
        body: formData
      })
      const endTime = Date.now()
      const thinkingTime = ((endTime - startTime) / 1000).toFixed(1)
      
      // Remove thinking message and add results
      setMessages(prev => {
        const filtered = prev.filter(m => !m.isThinking)
        return [...filtered, {
          id: Date.now().toString(),
          type: 'assistant',
          content: formatAnalysisResults(data),
          timestamp: new Date().toISOString(),
          thinkingTime: `${thinkingTime}s`,
          analysisData: data
        }]
      })

      // Update repositories list
  if (data.success) {
        setRepositories(prev => {
          const exists = prev.find(repo => repo.url === repoUrl)
          if (!exists) {
            const urlParts = repoUrl.replace(/https?:\/\/github\.com\//, '').split('/')
            const repoName = urlParts.length >= 2 ? `${urlParts[0]}-${urlParts[1]}` : (repoUrl.split('/').pop() || 'unknown-repo')
    const updated = [...prev, {
              id: Date.now().toString(),
              url: repoUrl,
              name: repoName,
              analyzedAt: new Date().toISOString(),
              type: 'github',
              description: data.message || 'Repository analyzed successfully'
    }]
    setActiveRepoName(repoName)
    return updated
          }
          return prev
        })
      } else if (data.repository_info) {
        // Legacy format support
        setRepositories(prev => {
          const exists = prev.find(repo => repo.url === repoUrl)
          if (!exists) {
    const updated = [...prev, {
              id: Date.now().toString(),
              url: repoUrl,
              name: data.repository_info.name || repoUrl.split('/').pop(),
              analyzedAt: new Date().toISOString(),
              ...data.repository_info
    }]
    setActiveRepoName(data.repository_info.name || repoUrl.split('/').pop())
    return updated
          }
          return prev
        })
      }

    } catch (error) {
      console.error('Error analyzing repository:', error)
      
      let errorMessage = `Sorry, I couldn't analyze the repository "${repoUrl}".`
      
      if (error.message.includes('422')) {
        errorMessage += `\n\n**HTTP 422 Error:** This usually means the repository URL format is incorrect or the repository is not accessible. Please check:
        
• Make sure the URL is a valid GitHub repository URL
• Ensure the repository is public or you have access to it
• Try the format: https://github.com/username/repository-name

**Example:** https://github.com/facebook/react`
      } else if (error.message.includes('404')) {
        errorMessage += `\n\n**Repository Not Found:** The repository at this URL doesn't exist or is private.`
      } else if (error.message.includes('500')) {
        errorMessage += `\n\n**Server Error:** There was an internal server error while processing your request. Please try again later.`
      } else {
        errorMessage += `\n\nError details: ${error.message}`
      }
      
      setMessages(prev => {
        const filtered = prev.filter(m => !m.isThinking)
        return [...filtered, {
          id: Date.now().toString(),
          type: 'assistant',
          content: errorMessage,
          timestamp: new Date().toISOString(),
          isError: true
        }]
      })
    } finally {
      setIsLoading(false)
    }
  }, [addMessage])

  const analyzeFile = useCallback(async (file) => {
    setIsLoading(true)
    
    addMessage({
      type: 'user',
      content: `Analyze uploaded file: ${file.name}`
    })

    addMessage({
      type: 'assistant',
      content: 'Processing uploaded file...',
      isThinking: true
    })

    try {
      const formData = new FormData()
      formData.append('file', file)
      
      // Extract filename without extension for repo name
      const repoName = file.name.replace(/\.[^/.]+$/, "") || 'uploaded-repo'
      formData.append('repo_name', repoName)

      const data = await apiFetch(`/analyze-repo`, {
        method: 'POST',
        body: formData
      })
      
      // Remove thinking message and add results
      setMessages(prev => {
        const filtered = prev.filter(m => !m.isThinking)
        return [...filtered, {
          id: Date.now().toString(),
          type: 'assistant',
          content: formatAnalysisResults(data),
          timestamp: new Date().toISOString(),
          analysisData: data
        }]
      })

  // Update repositories list
      if (data.repository_info) {
        setRepositories(prev => {
          const exists = prev.find(repo => repo.name === file.name)
          if (!exists) {
    const updated = [...prev, {
              id: Date.now().toString(),
              name: file.name,
              type: 'upload',
              analyzedAt: new Date().toISOString(),
              ...data.repository_info
    }]
    setActiveRepoName(file.name)
    return updated
          }
          return prev
        })
      }

    } catch (error) {
      console.error('Error analyzing file:', error)
      setMessages(prev => {
        const filtered = prev.filter(m => !m.isThinking)
        return [...filtered, {
          id: Date.now().toString(),
          type: 'assistant',
          content: `Sorry, I couldn't analyze the uploaded file "${file.name}". Please make sure it's a valid ZIP file containing source code.\n\nError: ${error.message}`,
          timestamp: new Date().toISOString(),
          isError: true
        }]
      })
    } finally {
      setIsLoading(false)
    }
  }, [addMessage])

  const suggestFeature = useCallback(async (featureDescription, repositoryContext = null) => {
    setIsLoading(true)
    
    addMessage({
      type: 'user',
      content: `Suggest implementation for: ${featureDescription}`
    })

    addMessage({
      type: 'assistant',
      content: 'Analyzing codebase and generating feature suggestions...',
      isThinking: true
    })

    try {
  // Use the active repository if available
  const repoName = activeRepoName || (repositories.length > 0 ? repositories[repositories.length - 1].name : 'unknown-repo')
      
      const formData = new FormData()
      formData.append('feature_description', featureDescription)
      formData.append('repo_name', repoName)

      const data = await apiFetch(`/suggest-feature`, {
        method: 'POST',
        body: formData
      })
      
      // Remove thinking message and add results
      setMessages(prev => {
        const filtered = prev.filter(m => !m.isThinking)
        return [...filtered, {
          id: Date.now().toString(),
          type: 'assistant',
          content: formatFeatureSuggestions(data),
          timestamp: new Date().toISOString(),
          suggestionData: data
        }]
      })

    } catch (error) {
      console.error('Error getting feature suggestions:', error)
      setMessages(prev => {
        const filtered = prev.filter(m => !m.isThinking)
        return [...filtered, {
          id: Date.now().toString(),
          type: 'assistant',
          content: `Sorry, I couldn't generate feature suggestions. Please make sure you have analyzed a repository first.\n\nError: ${error.message}`,
          timestamp: new Date().toISOString(),
          isError: true
        }]
      })
    } finally {
      setIsLoading(false)
    }
  }, [addMessage])

  // Switch to a specific repository conversation
  const switchToRepository = useCallback(async (repoName) => {
    try {
      setIsLoading(true)
      
      const data = await apiFetch(`/api/conversations/${encodeURIComponent(repoName)}/switch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      
      if (data.success) {
        // Transform backend messages to frontend format
        const transformedMessages = data.messages.map((msg, index) => ({
          id: `${repoName}_${index}`,
          type: msg.role,
          content: msg.content,
          timestamp: msg.timestamp,
          metadata: msg.metadata || {}
        }))
        
        // If no messages exist, add a welcome message for this repository
        if (transformedMessages.length === 0) {
          transformedMessages.push({
            id: `${repoName}_welcome`,
            type: 'assistant',
            content: `Welcome to the ${repoName} repository chat! I have analyzed this repository and can help you understand its structure, suggest improvements, or help you implement new features. What would you like to know?`,
            timestamp: new Date().toISOString(),
            metadata: { repo_name: repoName }
          })
        }
        
  // Update the current conversation
        setMessages(transformedMessages)
        setInput('') // Clear any existing input
  setActiveRepoName(repoName)
        
        // Save the updated conversation to localStorage
        storage.save(STORAGE_KEYS.MESSAGES, transformedMessages)
        
        // Add a lightweight system message at the end
        setMessages(prev => ([
          ...prev,
          {
            id: `${repoName}_${Date.now()}`,
            type: 'assistant',
            content: `Switched to ${repoName} conversation`,
            timestamp: new Date().toISOString(),
            metadata: { repo_name: repoName, system: true }
          }
        ]))
        
        return { success: true, repo_name: repoName }
      } else {
        throw new Error(data.error || 'Failed to switch conversation')
      }
    } catch (error) {
      console.error('Error switching conversation:', error)
      setMessages(prev => ([
        ...prev,
        {
          id: `${repoName}_error_${Date.now()}`,
          type: 'assistant',
          content: `Failed to switch to ${repoName}: ${error.message}`,
          timestamp: new Date().toISOString(),
          isError: true
        }
      ]))
      return { success: false, error: error.message }
    } finally {
      setIsLoading(false)
    }
  }, [addMessage])

  return {
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
  }
}

const formatAnalysisResults = (data) => {
  if (!data) return 'Analysis completed, but no data was returned.'

  // Handle the actual response format from the backend
  if (data.success === false) {
    return `# ❌ Analysis Failed\n\n${data.message || 'Unknown error occurred'}`
  }

  let result = '# 📊 Repository Analysis Complete\n\n'

  // Show success message
  if (data.message) {
    result += `✅ **Status:** ${data.message}\n\n`
  }

  // Show the main analysis summary
  if (data.analysis_summary) {
    result += data.analysis_summary
    result += '\n\n'
  }

  // Show Mermaid diagram if available
  if (data.mermaid_diagram) {
    result += `## 📊 Architecture Diagram\n\n`
    result += '```mermaid\n'
    result += data.mermaid_diagram
    result += '\n```\n\n'
  }

  // Legacy format support (in case the backend changes back)
  if (data.repository_info) {
    result += `## Repository Information\n`
    result += `**Name:** ${data.repository_info.name || 'Unknown'}\n`
    if (data.repository_info.description) {
      result += `**Description:** ${data.repository_info.description}\n`
    }
    if (data.repository_info.language) {
      result += `**Primary Language:** ${data.repository_info.language}\n`
    }
    if (data.repository_info.file_count) {
      result += `**Files Analyzed:** ${data.repository_info.file_count}\n`
    }
    result += '\n'
  }

  if (data.analysis && data.analysis.overview) {
    result += `## 🔍 Architecture Overview\n${data.analysis.overview}\n\n`
  }

  if (data.analysis && data.analysis.suggestions) {
    result += `## 💡 Suggestions\n`
    if (Array.isArray(data.analysis.suggestions)) {
      data.analysis.suggestions.forEach((suggestion, index) => {
        result += `${index + 1}. ${suggestion}\n`
      })
    } else {
      result += `${data.analysis.suggestions}\n`
    }
    result += '\n'
  }

  if (data.file_structure && Array.isArray(data.file_structure)) {
    result += `## 📁 Key Files Found\n`
    const importantFiles = data.file_structure.slice(0, 10) // Show first 10 files
    importantFiles.forEach(file => {
      result += `• ${file}\n`
    })
    if (data.file_structure.length > 10) {
      result += `• ... and ${data.file_structure.length - 10} more files\n`
    }
    result += '\n'
  }

  if (data.technologies && Array.isArray(data.technologies)) {
    result += `## 🛠️ Technologies Detected\n`
    data.technologies.forEach(tech => {
      result += `• ${tech}\n`
    })
    result += '\n'
  }

  return result
}

const formatFeatureSuggestions = (data) => {
  if (!data) return 'Feature analysis completed, but no suggestions were returned.'

  let result = '# 🚀 Feature Implementation Suggestions\n\n'

  if (data.suggestions && Array.isArray(data.suggestions)) {
    data.suggestions.forEach((suggestion, index) => {
      result += `## ${index + 1}. ${suggestion.title || `Suggestion ${index + 1}`}\n`
      if (suggestion.description) {
        result += `${suggestion.description}\n\n`
      }
      if (suggestion.files) {
        result += `**Files to modify:**\n`
        suggestion.files.forEach(file => {
          result += `• ${file}\n`
        })
        result += '\n'
      }
      if (suggestion.implementation) {
        result += `**Implementation notes:**\n${suggestion.implementation}\n\n`
      }
    })
  } else if (data.suggestions) {
    result += data.suggestions
  }

  if (data.architectural_notes) {
    result += `## 🏗️ Architectural Considerations\n${data.architectural_notes}\n\n`
  }

  return result
}
