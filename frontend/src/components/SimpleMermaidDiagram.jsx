import React, { useEffect, useRef, useState } from 'react'
import { Copy, Check, Download, ZoomIn } from 'lucide-react'

// Global flag to track if Mermaid is loaded
let mermaidLoaded = false
let mermaidLoading = false
const mermaidCallbacks = []

const SimpleMermaidDiagram = ({ chart, id }) => {
  const elementRef = useRef(null)
  const [copied, setCopied] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    // Initialize Mermaid once globally
    const initMermaid = () => {
      if (mermaidLoaded) {
        setIsReady(true)
        renderDiagram()
        return
      }

      if (mermaidLoading) {
        // Add to callback queue
        mermaidCallbacks.push(() => {
          setIsReady(true)
          renderDiagram()
        })
        return
      }

      // Load Mermaid from CDN
      mermaidLoading = true
      const script = document.createElement('script')
      script.src = 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js'
      script.onload = () => {
        console.log('Mermaid loaded from CDN')
        window.mermaid.initialize({ 
          startOnLoad: false,
          theme: 'dark',
          themeVariables: {
            primaryColor: '#3b82f6',
            primaryTextColor: '#f3f4f6',
            primaryBorderColor: '#6b7280',
            lineColor: '#9ca3af',
            secondaryColor: '#1f2937',
            tertiaryColor: '#374151',
            background: '#111827',
            darkMode: true
          },
          fontFamily: 'ui-monospace, SFMono-Regular, Monaco, Consolas, monospace'
        })
        
        mermaidLoaded = true
        mermaidLoading = false
        
        // Execute all waiting callbacks
        mermaidCallbacks.forEach(callback => callback())
        mermaidCallbacks.length = 0
        
        setIsReady(true)
        renderDiagram()
      }
      script.onerror = () => {
        console.error('Failed to load Mermaid from CDN')
        mermaidLoading = false
      }
      document.head.appendChild(script)
    }

    initMermaid()
  }, [])

  useEffect(() => {
    if (isReady && chart) {
      renderDiagram()
    }
  }, [chart, isReady])

  const renderDiagram = async () => {
    if (!elementRef.current || !chart || !window.mermaid || !isReady) {
      console.log('Cannot render diagram:', { 
        hasElement: !!elementRef.current, 
        hasChart: !!chart, 
        hasMermaid: !!window.mermaid,
        isReady 
      })
      return
    }

    try {
      console.log('Starting diagram render...', chart)
      
      // Clear the element
      elementRef.current.innerHTML = 'Rendering diagram...'
      
      // Create a unique ID
      const diagramId = id || `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      
      // Clean the chart syntax
      const cleanChart = chart.trim()
      
      // Use mermaid.render to get SVG
      const { svg } = await window.mermaid.render(diagramId, cleanChart)
      elementRef.current.innerHTML = svg

      // Style the SVG
      const svgElement = elementRef.current.querySelector('svg')
      if (svgElement) {
        svgElement.style.maxWidth = '100%'
        svgElement.style.height = 'auto'
        svgElement.style.background = 'transparent'
        svgElement.style.display = 'block'
        svgElement.style.margin = '0 auto'
      }
      
      console.log('Diagram rendered successfully')
    } catch (error) {
      console.error('Mermaid rendering error:', error)
      elementRef.current.innerHTML = `
        <div class="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
          <div class="text-red-400 mb-2 font-medium">Diagram Rendering Error</div>
          <p class="text-red-300 text-sm mb-3">${error.message}</p>
          <details class="text-xs">
            <summary class="cursor-pointer text-red-400 hover:text-red-300">Show raw Mermaid code</summary>
            <pre class="bg-red-950/30 p-2 rounded mt-2 overflow-x-auto text-red-200 whitespace-pre-wrap font-mono">${chart}</pre>
          </details>
        </div>
      `
    }
  }

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(chart)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy diagram code:', err)
    }
  }

  const handleDownload = () => {
    const svgElement = elementRef.current?.querySelector('svg')
    if (!svgElement) return

    const svgData = new XMLSerializer().serializeToString(svgElement)
    const blob = new Blob([svgData], { type: 'image/svg+xml' })
    const url = URL.createObjectURL(blob)
    
    const link = document.createElement('a')
    link.href = url
    link.download = 'architecture-diagram.svg'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen)
  }

  return (
    <>
      <div className="bg-gray-800/50 border border-gray-600/30 rounded-lg my-4 overflow-hidden">
        {/* Header with controls */}
        <div className="flex items-center justify-between px-4 py-2 bg-gray-800/80 border-b border-gray-600/30">
          <span className="text-sm font-medium text-gray-300">Architecture Diagram</span>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="p-1.5 text-gray-400 hover:text-gray-200 hover:bg-gray-700/50 rounded transition-colors"
              title="Copy Mermaid code"
            >
              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            </button>
            <button
              onClick={handleDownload}
              className="p-1.5 text-gray-400 hover:text-gray-200 hover:bg-gray-700/50 rounded transition-colors"
              title="Download as SVG"
            >
              <Download className="w-4 h-4" />
            </button>
            <button
              onClick={toggleFullscreen}
              className="p-1.5 text-gray-400 hover:text-gray-200 hover:bg-gray-700/50 rounded transition-colors"
              title="View fullscreen"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
          </div>
        </div>
        
        {/* Diagram content */}
        <div className="p-4">
          <div 
            ref={elementRef} 
            className="mermaid-container text-center min-h-[100px] flex items-center justify-center"
          />
        </div>
      </div>

      {/* Fullscreen modal */}
      {isFullscreen && (
        <div className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4">
          <div className="bg-gray-900 rounded-lg max-w-7xl max-h-full overflow-auto w-full">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700">
              <h3 className="text-lg font-semibold text-gray-100">Architecture Diagram</h3>
              <button
                onClick={toggleFullscreen}
                className="text-gray-400 hover:text-gray-200 text-xl"
              >
                ×
              </button>
            </div>
            <div className="p-6">
              <div 
                dangerouslySetInnerHTML={{ 
                  __html: elementRef.current?.innerHTML || '' 
                }}
                className="text-center"
              />
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default SimpleMermaidDiagram
