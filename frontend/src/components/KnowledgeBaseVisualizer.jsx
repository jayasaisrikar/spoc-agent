import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Database, 
  Table, 
  FileText, 
  Code, 
  BarChart3, 
  Search, 
  ChevronRight,
  ChevronDown,
  Eye,
  Layers,
  Activity,
  Clock,
  Hash,
  RefreshCw,
  Plus,
  Edit,
  Trash2,
  Save,
  X,
  Play,
  Download,
  Upload
} from 'lucide-react'

const KnowledgeBaseVisualizer = () => {
  const [tables, setTables] = useState({})
  const [selectedTable, setSelectedTable] = useState(null)
  const [tableData, setTableData] = useState(null)
  const [selectedRepo, setSelectedRepo] = useState(null)
  const [repoDetails, setRepoDetails] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [expandedRows, setExpandedRows] = useState(new Set())
  const [editingRow, setEditingRow] = useState(null)
  const [editingData, setEditingData] = useState({})
  const [showAddForm, setShowAddForm] = useState(false)
  const [newRowData, setNewRowData] = useState({})
  const [showSqlQuery, setShowSqlQuery] = useState(false)
  const [sqlQuery, setSqlQuery] = useState('')
  const [sqlResults, setSqlResults] = useState(null)
  const [viewMode, setViewMode] = useState('paginated') // 'paginated' or 'all'

  useEffect(() => {
    fetchTables()
  }, [])

  const fetchTables = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/knowledge-base/tables')
      const data = await response.json()
      
      if (data.success) {
        setTables(data.tables)
      } else {
        setError(data.error || 'Failed to fetch tables')
      }
    } catch (err) {
      setError('Failed to connect to API')
    } finally {
      setLoading(false)
    }
  }

  const fetchTableData = async (tableName, showAll = false) => {
    try {
      setLoading(true)
      const endpoint = showAll ? 
        `/api/knowledge-base/table/${tableName}/all` : 
        `/api/knowledge-base/table/${tableName}?limit=50&offset=0`
      
      const response = await fetch(endpoint)
      const data = await response.json()
      
      if (data.success) {
        setTableData(data)
        setViewMode(showAll ? 'all' : 'paginated')
      } else {
        setError(data.error || 'Failed to fetch table data')
      }
    } catch (err) {
      setError('Failed to fetch table data')
    } finally {
      setLoading(false)
    }
  }

  const executeSQL = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/knowledge-base/execute-sql', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: sqlQuery })
      })
      const data = await response.json()
      
      if (data.success) {
        setSqlResults(data)
      } else {
        setError(data.error || 'Failed to execute SQL query')
      }
    } catch (err) {
      setError('Failed to execute SQL query')
    } finally {
      setLoading(false)
    }
  }

  const addRow = async () => {
    try {
      setLoading(true)
      const response = await fetch(`/api/knowledge-base/table/${selectedTable}/row`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newRowData)
      })
      const data = await response.json()
      
      if (data.success) {
        setShowAddForm(false)
        setNewRowData({})
        await fetchTableData(selectedTable, viewMode === 'all')
      } else {
        setError(data.error || 'Failed to add row')
      }
    } catch (err) {
      setError('Failed to add row')
    } finally {
      setLoading(false)
    }
  }

  const updateRow = async (rowId) => {
    try {
      setLoading(true)
      const response = await fetch(`/api/knowledge-base/table/${selectedTable}/row/${rowId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(editingData)
      })
      const data = await response.json()
      
      if (data.success) {
        setEditingRow(null)
        setEditingData({})
        await fetchTableData(selectedTable, viewMode === 'all')
      } else {
        setError(data.error || 'Failed to update row')
      }
    } catch (err) {
      setError('Failed to update row')
    } finally {
      setLoading(false)
    }
  }

  const deleteRow = async (rowId) => {
    if (!confirm('Are you sure you want to delete this row?')) return
    
    try {
      setLoading(true)
      const response = await fetch(`/api/knowledge-base/table/${selectedTable}/row/${rowId}`, {
        method: 'DELETE'
      })
      const data = await response.json()
      
      if (data.success) {
        await fetchTableData(selectedTable, viewMode === 'all')
      } else {
        setError(data.error || 'Failed to delete row')
      }
    } catch (err) {
      setError('Failed to delete row')
    } finally {
      setLoading(false)
    }
  }

  const fetchRepoDetails = async (repoName) => {
    try {
      setLoading(true)
      // Try the repository details endpoint first
      let response = await fetch(`/api/knowledge-base/repository/${encodeURIComponent(repoName)}/details`)
      let data = await response.json()
      
      // If that fails, fallback to getting data from the repositories table
      if (!response.ok || !data.success) {
        console.log('Repository details endpoint not available, using table data...')
        response = await fetch(`/api/knowledge-base/table/repositories/all`)
        data = await response.json()
        
        if (data.success) {
          const repoData = data.data.find(repo => repo.repo_name === repoName)
          if (repoData) {
            // Transform the table data to match the expected format
            const transformedData = {
              success: true,
              repository: {
                id: repoData.id,
                name: repoData.repo_name,
                hash: repoData.repo_hash,
                file_structure: (() => {
                  try {
                    return repoData.file_structure ? JSON.parse(repoData.file_structure) : []
                  } catch (e) {
                    console.error('Error parsing file_structure:', e)
                    return []
                  }
                })(),
                file_contents_count: (() => {
                  try {
                    return repoData.file_contents ? Object.keys(JSON.parse(repoData.file_contents)).length : 0
                  } catch (e) {
                    console.error('Error parsing file_contents:', e)
                    return 0
                  }
                })(),
                file_contents_sample: (() => {
                  try {
                    if (!repoData.file_contents) return {}
                    const parsed = JSON.parse(repoData.file_contents)
                    return Object.fromEntries(
                      Object.entries(parsed).slice(0, 5).map(([k, v]) => [
                        k, 
                        typeof v === 'string' && v.length > 200 ? v.substring(0, 200) + '...' : v
                      ])
                    )
                  } catch (e) {
                    console.error('Error parsing file_contents for sample:', e)
                    return {}
                  }
                })(),
                analysis: (() => {
                  try {
                    return repoData.analysis ? JSON.parse(repoData.analysis) : {}
                  } catch (e) {
                    console.error('Error parsing analysis:', e)
                    return {}
                  }
                })(),
                mermaid_diagram: repoData.mermaid_diagram || '',
                created_at: repoData.created_at,
                features: [] // We'll need to get these separately if needed
              }
            }
            setRepoDetails(transformedData.repository)
          } else {
            setError(`Repository ${repoName} not found`)
          }
        } else {
          setError(data.error || 'Failed to fetch repository details')
        }
      } else {
        setRepoDetails(data.repository)
      }
    } catch (err) {
      console.error('Error fetching repository details:', err)
      setError('Failed to fetch repository details')
    } finally {
      setLoading(false)
    }
  }

  const handleTableSelect = (tableName) => {
    setSelectedTable(tableName)
    setSelectedRepo(null)
    setRepoDetails(null)
    setTableData(null)
    setShowSqlQuery(false)
    setSqlResults(null)
    setEditingRow(null)
    setShowAddForm(false)
    fetchTableData(tableName, false)
  }

  const startEditingRow = (row, index) => {
    setEditingRow(index)
    setEditingData({ ...row })
  }

  const cancelEditing = () => {
    setEditingRow(null)
    setEditingData({})
  }

  const startAddingRow = () => {
    const initialData = {}
    if (tableData && tableData.columns) {
      tableData.columns.forEach(col => {
        if (col !== 'id') {
          initialData[col] = ''
        }
      })
    }
    setNewRowData(initialData)
    setShowAddForm(true)
  }

  const handleRepoSelect = (repoName) => {
    setSelectedRepo(repoName)
    setSelectedTable(null)
    setTableData(null)
    fetchRepoDetails(repoName)
  }

  const toggleRowExpansion = (index) => {
    const newExpanded = new Set(expandedRows)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedRows(newExpanded)
  }

  const renderEditableCell = (value, column, rowIndex) => {
    if (editingRow === rowIndex) {
      if (column === 'id') {
        return <span className="text-gray-400">{value}</span>
      }
      
      const isJson = typeof value === 'string' && (value.startsWith('{') || value.startsWith('['))
      
      if (isJson) {
        return (
          <textarea
            value={editingData[column] || ''}
            onChange={(e) => setEditingData({...editingData, [column]: e.target.value})}
            className="w-full p-2 border border-gray-300 rounded text-xs font-mono"
            rows={3}
          />
        )
      }
      
      return (
        <input
          type="text"
          value={editingData[column] || ''}
          onChange={(e) => setEditingData({...editingData, [column]: e.target.value})}
          className="w-full p-2 border border-gray-300 rounded text-sm"
        />
      )
    }
    
    return renderValue(value, expandedRows.has(rowIndex))
  }

  const renderValue = (value, isExpanded = false) => {
    if (value === null || value === undefined) {
      return <span className="text-gray-400 italic">null</span>
    }
    
    if (typeof value === 'string' && value.length > 100 && !isExpanded) {
      return (
        <span className="text-gray-700">
          {value.substring(0, 100)}...
        </span>
      )
    }
    
    if (typeof value === 'object') {
      return (
        <pre className="text-xs bg-gray-50 p-2 rounded overflow-x-auto max-w-md">
          {JSON.stringify(value, null, 2)}
        </pre>
      )
    }
    
    return <span className="text-gray-700">{String(value)}</span>
  }

  const getTableIcon = (tableName) => {
    switch (tableName) {
      case 'repositories':
        return <Database className="w-4 h-4 text-blue-500" />
      case 'features':
        return <Layers className="w-4 h-4 text-green-500" />
      default:
        return <Table className="w-4 h-4 text-gray-500" />
    }
  }

  const filteredTables = Object.entries(tables).filter(([name]) =>
    name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading && !tables.length) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 text-gray-400 animate-spin mx-auto mb-2" />
          <p className="text-gray-600">Loading knowledge base...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Database className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={fetchTables}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <Database className="w-8 h-8 text-blue-500" />
          <h1 className="text-3xl font-bold text-gray-900">Knowledge Base Admin</h1>
        </div>
        <p className="text-gray-600">
          Explore, edit, and manage your codebase analysis knowledge base
        </p>
        
        {/* Quick Actions */}
        <div className="flex items-center gap-2 mt-4">
          <button
            onClick={() => setShowSqlQuery(!showSqlQuery)}
            className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors flex items-center gap-2"
          >
            <Play className="w-4 h-4" />
            SQL Query
          </button>
          <button
            onClick={() => window.location.href = '/api/knowledge-base/export'}
            className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Export DB
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Tables</h2>
              <button
                onClick={fetchTables}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                title="Refresh"
              >
                <RefreshCw className="w-4 h-4 text-gray-500" />
              </button>
            </div>
            
            <div className="mb-4">
              <div className="relative">
                <Search className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
                <input
                  type="text"
                  placeholder="Search tables..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="space-y-2">
              {filteredTables.map(([tableName, tableInfo]) => (
                <button
                  key={tableName}
                  onClick={() => handleTableSelect(tableName)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    selectedTable === tableName
                      ? 'bg-blue-50 border-2 border-blue-200'
                      : 'hover:bg-gray-50 border-2 border-transparent'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {getTableIcon(tableName)}
                      <span className="font-medium text-gray-900">{tableName}</span>
                    </div>
                    <span className="text-sm text-gray-500">{tableInfo.row_count}</span>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {tableInfo.columns.length} columns
                  </div>
                </button>
              ))}
            </div>

            {/* Repository Quick Access */}
            {tables.repositories && (
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h3 className="text-sm font-semibold text-gray-900 mb-3">Quick Repository Access</h3>
                <div className="space-y-1">
                  {tableData?.data?.slice(0, 5).map((repo) => (
                    <button
                      key={repo.id}
                      onClick={() => handleRepoSelect(repo.repo_name)}
                      className={`w-full text-left p-2 rounded text-sm transition-colors ${
                        selectedRepo === repo.repo_name
                          ? 'bg-green-50 text-green-800'
                          : 'hover:bg-gray-50 text-gray-700'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <FileText className="w-3 h-3" />
                        <span className="truncate">{repo.repo_name}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3">
          {/* SQL Query Interface */}
          {showSqlQuery && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
              <div className="p-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">SQL Query</h3>
              </div>
              <div className="p-4">
                <div className="space-y-4">
                  <div>
                    <textarea
                      value={sqlQuery}
                      onChange={(e) => setSqlQuery(e.target.value)}
                      placeholder="SELECT * FROM repositories LIMIT 10;"
                      className="w-full p-3 border border-gray-300 rounded-lg font-mono text-sm"
                      rows={3}
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={executeSQL}
                      disabled={!sqlQuery.trim()}
                      className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                    >
                      <Play className="w-4 h-4" />
                      Execute Query
                    </button>
                    <button
                      onClick={() => {
                        setSqlQuery('')
                        setSqlResults(null)
                      }}
                      className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                    >
                      Clear
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* SQL Results */}
          {sqlResults && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
              <div className="p-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Query Results ({sqlResults.row_count} rows)</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      {sqlResults.columns.map((column) => (
                        <th
                          key={column}
                          className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                          {column}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {sqlResults.data.map((row, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        {sqlResults.columns.map((column) => (
                          <td key={column} className="px-4 py-4 whitespace-nowrap text-sm">
                            {renderValue(row[column])}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <AnimatePresence mode="wait">
            {selectedTable && tableData && (
              <motion.div
                key={selectedTable}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="bg-white rounded-lg shadow-sm border border-gray-200"
              >
                <div className="p-6 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {getTableIcon(selectedTable)}
                      <h2 className="text-2xl font-bold text-gray-900">{selectedTable}</h2>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => fetchTableData(selectedTable, false)}
                          className={`px-3 py-1 text-sm rounded ${
                            viewMode === 'paginated' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
                          }`}
                        >
                          Paginated
                        </button>
                        <button
                          onClick={() => fetchTableData(selectedTable, true)}
                          className={`px-3 py-1 text-sm rounded ${
                            viewMode === 'all' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
                          }`}
                        >
                          Show All
                        </button>
                      </div>
                      <button
                        onClick={startAddingRow}
                        className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center gap-2"
                      >
                        <Plus className="w-4 h-4" />
                        Add Row
                      </button>
                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        <span className="flex items-center gap-1">
                          <BarChart3 className="w-4 h-4" />
                          {tableData.total_count} rows
                        </span>
                        <span className="flex items-center gap-1">
                          <Table className="w-4 h-4" />
                          {tableData.columns.length} columns
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Add Row Form */}
                {showAddForm && (
                  <div className="p-6 border-b border-gray-200 bg-green-50">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Add New Row</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {tableData.columns.filter(col => col !== 'id').map((column) => (
                        <div key={column}>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            {column}
                          </label>
                          {column.includes('_at') ? (
                            <input
                              type="datetime-local"
                              value={newRowData[column] || ''}
                              onChange={(e) => setNewRowData({...newRowData, [column]: e.target.value})}
                              className="w-full p-2 border border-gray-300 rounded"
                            />
                          ) : (
                            <input
                              type="text"
                              value={newRowData[column] || ''}
                              onChange={(e) => setNewRowData({...newRowData, [column]: e.target.value})}
                              className="w-full p-2 border border-gray-300 rounded"
                              placeholder={`Enter ${column}...`}
                            />
                          )}
                        </div>
                      ))}
                    </div>
                    <div className="flex items-center gap-2 mt-4">
                      <button
                        onClick={addRow}
                        className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center gap-2"
                      >
                        <Save className="w-4 h-4" />
                        Save Row
                      </button>
                      <button
                        onClick={() => setShowAddForm(false)}
                        className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}

                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        {tableData.columns.map((column) => (
                          <th
                            key={column}
                            className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                          >
                            {column}
                          </th>
                        ))}
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {tableData.data.map((row, index) => (
                        <React.Fragment key={index}>
                          <tr className="hover:bg-gray-50">
                            {tableData.columns.map((column) => (
                              <td key={column} className="px-4 py-4 text-sm max-w-xs">
                                {renderEditableCell(row[column], column, index)}
                              </td>
                            ))}
                            <td className="px-4 py-4 whitespace-nowrap text-sm">
                              <div className="flex items-center gap-1">
                                {editingRow === index ? (
                                  <>
                                    <button
                                      onClick={() => updateRow(row.id)}
                                      className="p-1 text-green-600 hover:bg-green-100 rounded transition-colors"
                                      title="Save"
                                    >
                                      <Save className="w-4 h-4" />
                                    </button>
                                    <button
                                      onClick={cancelEditing}
                                      className="p-1 text-gray-600 hover:bg-gray-100 rounded transition-colors"
                                      title="Cancel"
                                    >
                                      <X className="w-4 h-4" />
                                    </button>
                                  </>
                                ) : (
                                  <>
                                    <button
                                      onClick={() => toggleRowExpansion(index)}
                                      className="p-1 hover:bg-gray-100 rounded transition-colors"
                                      title="Expand/Collapse"
                                    >
                                      {expandedRows.has(index) ? (
                                        <ChevronDown className="w-4 h-4 text-gray-400" />
                                      ) : (
                                        <ChevronRight className="w-4 h-4 text-gray-400" />
                                      )}
                                    </button>
                                    <button
                                      onClick={() => startEditingRow(row, index)}
                                      className="p-1 text-blue-600 hover:bg-blue-100 rounded transition-colors"
                                      title="Edit"
                                    >
                                      <Edit className="w-4 h-4" />
                                    </button>
                                    <button
                                      onClick={() => deleteRow(row.id)}
                                      className="p-1 text-red-600 hover:bg-red-100 rounded transition-colors"
                                      title="Delete"
                                    >
                                      <Trash2 className="w-4 h-4" />
                                    </button>
                                    {selectedTable === 'repositories' && (
                                      <button
                                        onClick={() => handleRepoSelect(row.repo_name)}
                                        className="p-1 hover:bg-gray-100 rounded transition-colors"
                                        title="View Details"
                                      >
                                        <Eye className="w-4 h-4 text-blue-500" />
                                      </button>
                                    )}
                                  </>
                                )}
                              </div>
                            </td>
                          </tr>
                          {expandedRows.has(index) && (
                            <tr>
                              <td colSpan={tableData.columns.length + 1} className="px-4 py-4 bg-gray-50">
                                <div className="space-y-2">
                                  {Object.entries(row).map(([key, value]) => (
                                    <div key={key} className="flex">
                                      <span className="w-32 text-sm font-medium text-gray-500 flex-shrink-0">
                                        {key}:
                                      </span>
                                      <div className="flex-1 text-sm">
                                        {renderValue(value, true)}
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      ))}
                    </tbody>
                  </table>
                </div>
              </motion.div>
            )}

            {selectedRepo && repoDetails && (
              <motion.div
                key={selectedRepo}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="bg-white rounded-lg shadow-sm border border-gray-200"
              >
                <div className="p-6 border-b border-gray-200">
                  <div className="flex items-center gap-3">
                    <FileText className="w-8 h-8 text-green-500" />
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900">{repoDetails.name}</h2>
                      <p className="text-gray-600">Repository Details</p>
                    </div>
                  </div>
                </div>

                <div className="p-6 space-y-6">
                  {/* Repository Stats */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Hash className="w-5 h-5 text-blue-500" />
                        <span className="text-sm font-medium text-blue-700">ID</span>
                      </div>
                      <p className="text-2xl font-bold text-blue-900">{repoDetails.id}</p>
                    </div>
                    <div className="bg-green-50 p-4 rounded-lg">
                      <div className="flex items-center gap-2">
                        <FileText className="w-5 h-5 text-green-500" />
                        <span className="text-sm font-medium text-green-700">Files</span>
                      </div>
                      <p className="text-2xl font-bold text-green-900">{repoDetails.file_structure.length}</p>
                    </div>
                    <div className="bg-purple-50 p-4 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Code className="w-5 h-5 text-purple-500" />
                        <span className="text-sm font-medium text-purple-700">Contents</span>
                      </div>
                      <p className="text-2xl font-bold text-purple-900">{repoDetails.file_contents_count}</p>
                    </div>
                    <div className="bg-orange-50 p-4 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Activity className="w-5 h-5 text-orange-500" />
                        <span className="text-sm font-medium text-orange-700">Features</span>
                      </div>
                      <p className="text-2xl font-bold text-orange-900">{repoDetails.features.length}</p>
                    </div>
                  </div>

                  {/* Repository Hash */}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Repository Hash</h3>
                    <code className="bg-gray-100 px-3 py-2 rounded text-sm text-gray-800 break-all">
                      {repoDetails.hash}
                    </code>
                  </div>

                  {/* File Structure */}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">File Structure</h3>
                    <div className="bg-gray-50 p-4 rounded-lg max-h-64 overflow-y-auto">
                      <ul className="space-y-1 text-sm">
                        {repoDetails.file_structure.map((file, index) => (
                          <li key={index} className="flex items-center gap-2">
                            <FileText className="w-4 h-4 text-gray-400" />
                            <span className="text-gray-700">{file}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Sample File Contents */}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Sample File Contents</h3>
                    <div className="space-y-3">
                      {Object.entries(repoDetails.file_contents_sample).map(([filename, content]) => (
                        <div key={filename} className="border border-gray-200 rounded-lg">
                          <div className="px-4 py-2 bg-gray-50 border-b border-gray-200">
                            <span className="text-sm font-medium text-gray-700">{filename}</span>
                          </div>
                          <div className="p-4">
                            <pre className="text-xs text-gray-600 overflow-x-auto">{content}</pre>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Features */}
                  {repoDetails.features.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">Features</h3>
                      <div className="space-y-3">
                        {repoDetails.features.map((feature, index) => (
                          <div key={index} className="border border-gray-200 rounded-lg p-4">
                            <div className="flex items-start justify-between mb-2">
                              <h4 className="font-medium text-gray-900">{feature.description}</h4>
                              <div className="flex items-center gap-1 text-xs text-gray-500">
                                <Clock className="w-3 h-3" />
                                {new Date(feature.created_at).toLocaleDateString()}
                              </div>
                            </div>
                            <p className="text-sm text-gray-600">{feature.suggestions}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            )}

            {!selectedTable && !selectedRepo && (
              <div className="flex items-center justify-center h-96">
                <div className="text-center">
                  <Database className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-700 mb-2">Select a table to explore</h3>
                  <p className="text-gray-500">Choose a table from the sidebar to view its structure and data</p>
                </div>
              </div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}

export default KnowledgeBaseVisualizer
