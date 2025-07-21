import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Upload, FileArchive, CheckCircle, X, AlertCircle } from 'lucide-react'
import { useDropzone } from 'react-dropzone'

const FileUpload = ({ onClose, onFileSelect }) => {
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')

  const onDrop = async (acceptedFiles) => {
    const file = acceptedFiles[0]
    if (!file) return

    setUploading(true)
    setError('')
    try {
      await onFileSelect(file)
      onClose()
    } catch (error) {
      console.error('Upload failed:', error)
      setError('Failed to process file. Please try again.')
    }
    setUploading(false)
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/zip': ['.zip'],
      'application/x-zip-compressed': ['.zip']
    },
    multiple: false,
    disabled: uploading
  })

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
          className="bg-white rounded-xl border border-gray-200 shadow-lg p-6 w-full max-w-md"
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Upload Codebase</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>

          {/* Upload area */}
          <div
            {...getRootProps()}
            className={`
              min-h-48 border-2 border-dashed rounded-lg p-6 cursor-pointer transition-all text-center
              ${isDragActive 
                ? 'border-gray-400 bg-gray-50' 
                : 'border-gray-300 hover:border-gray-400 bg-gray-50 hover:bg-gray-100'
              }
              ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            <input {...getInputProps()} />
            
            <div className="flex flex-col items-center justify-center space-y-4">
              {uploading ? (
                <div className="w-12 h-12 border-4 border-gray-300 border-t-gray-900 rounded-full animate-spin"></div>
              ) : (
                <div className="w-16 h-16 rounded-lg bg-gray-100 flex items-center justify-center">
                  <FileArchive className="w-8 h-8 text-gray-600" />
                </div>
              )}
              
              <div>
                <h3 className="text-gray-900 font-medium mb-1">
                  {uploading ? 'Processing...' : isDragActive ? 'Drop your ZIP file here' : 'Upload ZIP file'}
                </h3>
                <p className="text-sm text-gray-600">
                  {uploading 
                    ? 'Analyzing your codebase...' 
                    : 'Drag and drop a ZIP file containing your source code, or click to browse'
                  }
                </p>
              </div>

              {!uploading && (
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <Upload className="w-4 h-4" />
                  <span>Supports .zip files up to 50MB</span>
                </div>
              )}
            </div>
          </div>

          {/* Error message */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2"
            >
              <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0" />
              <span className="text-red-700 text-sm">{error}</span>
            </motion.div>
          )}

          {/* Instructions */}
          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Supported formats:</h4>
            <ul className="text-xs text-gray-600 space-y-1">
              <li>• ZIP archives containing source code</li>
              <li>• Common programming languages (JS, TS, Python, Java, etc.)</li>
              <li>• Project configuration files (package.json, requirements.txt, etc.)</li>
            </ul>
          </div>
        </motion.div>
      </motion.div>
    </>
  )
}

export default FileUpload
