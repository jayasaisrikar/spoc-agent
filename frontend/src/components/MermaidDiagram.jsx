import React, { useEffect, useRef, useState } from 'react'
import mermaid from 'mermaid'
import { Copy, Check, Download, ZoomIn } from 'lucide-react'

const MermaidDiagram = ({ chart, id }) => {
  const elementRef = useRef(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const [copied, setCopied] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)

  useEffect(() => {
    // Initialize mermaid with configuration
    mermaid.initialize({
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
      fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
      flowchart: {
        useMaxWidth: true,
        htmlLabels: true,
        curve: 'cardinal'
      },
      sequence: {
        useMaxWidth: true,
        wrap: true
      },
      gantt: {
        useMaxWidth: true
      },
      journey: {
        useMaxWidth: true
      },
      class: {
        useMaxWidth: true
      },
      state: {
        useMaxWidth: true
      },
      er: {
        useMaxWidth: true
      },
      pie: {
        useMaxWidth: true
      },
      requirement: {
        useMaxWidth: true
      },
      gitgraph: {
        useMaxWidth: true
      }
    })
  }, [])

  useEffect(() => {
    const renderDiagram = async () => {
      if (!elementRef.current || !chart) return

      setIsLoading(true)
      setError(null)

      try {
        // Clear the element
        elementRef.current.innerHTML = ''
        
        // Generate unique ID for this diagram
        const diagramId = id || `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
        
        // Render the diagram directly without validation
        const { svg } = await mermaid.render(diagramId, chart)
        elementRef.current.innerHTML = svg

        // Add some styling to the SVG
        const svgElement = elementRef.current.querySelector('svg')
        if (svgElement) {
          svgElement.style.maxWidth = '100%'
          svgElement.style.height = 'auto'
          svgElement.style.background = 'transparent'
        }

        setIsLoading(false)
      } catch (err) {
        console.error('Mermaid rendering error:', err)
        setError(err.message)
        setIsLoading(false)
      }
    }

    renderDiagram()
  }, [chart, id])

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

    // Create a blob with the SVG content
    const svgData = new XMLSerializer().serializeToString(svgElement)
    const blob = new Blob([svgData], { type: 'image/svg+xml' })
    const url = URL.createObjectURL(blob)
    
    // Create download link
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

  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4 my-4">
        <div className="flex items-center gap-2 text-red-400 mb-2">
          <span className="text-sm font-medium">Diagram Rendering Error</span>
        </div>
        <p className="text-red-300 text-sm mb-3">{error}</p>
        <details className="text-xs">
          <summary className="cursor-pointer text-red-400 hover:text-red-300">
            Show raw Mermaid code
          </summary>
          <pre className="bg-red-950/30 p-2 rounded mt-2 overflow-x-auto text-red-200">
            {chart}
          </pre>
        </details>
      </div>
    )
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
          {isLoading && (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
              <span className="ml-3 text-gray-400">Rendering diagram...</span>
            </div>
          )}
          
          <div 
            ref={elementRef} 
            className="mermaid-container text-center"
            style={{ 
              minHeight: isLoading ? '100px' : 'auto',
              display: isLoading ? 'none' : 'block'
            }}
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

export default MermaidDiagram
